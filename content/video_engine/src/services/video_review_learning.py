"""Durable video review packets and evidence-backed learning candidates.

The service has no provider or render side effects. It copies only evidence
files explicitly named in a review draft, validates the resulting packet, and
keeps learning promotion behind an operator gate.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft7Validator, FormatChecker


CONFIG_ROOT = Path(__file__).resolve().parents[2] / "configs"
SCHEMAS = {
    "video_watch_review.v1": "video_watch_review_v1.schema.json",
    "video_review_learning.v1": "video_review_learning_v1.schema.json",
}
ZERO_HASH = "0" * 64
SCOPE_RANK = {"episode": 0, "lane": 1, "engine": 2, "global": 3}
PROMOTION_RANK = {"observation": 0, "candidate_rule": 1, "approved_rule": 2, "implemented": 3}


class VideoReviewValidationError(ValueError):
    """Raised when a review or learning artifact violates its contract."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_json(payload: Mapping[str, Any]) -> str:
    core = dict(payload)
    core.pop("artifact_hash", None)
    return json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def with_artifact_hash(payload: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(payload)
    result["artifact_hash"] = canonical_sha256(result)
    return result


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    version = str(payload.get("schema_version") or "")
    schema_name = SCHEMAS.get(version)
    if schema_name is None:
        return [f"unsupported schema_version: {version!r}"]
    schema = load_json(CONFIG_ROOT / schema_name)
    errors = sorted(
        Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(dict(payload)),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _review_semantic_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    duration = float(payload.get("source", {}).get("duration_s", 0))
    finding_ids: set[str] = set()
    for index, finding in enumerate(payload.get("findings", [])):
        finding_id = str(finding.get("finding_id") or "")
        prefix = f"findings.{index}"
        if finding_id in finding_ids:
            errors.append(f"{prefix}.finding_id is duplicated: {finding_id}")
        finding_ids.add(finding_id)
        start = float(finding.get("start_s", 0))
        end = float(finding.get("end_s", 0))
        if end <= start:
            errors.append(f"{prefix} end_s must be greater than start_s")
        if duration and end > duration + 0.05:
            errors.append(f"{prefix} end_s exceeds source duration")
        for frame_index, frame in enumerate(finding.get("evidence_frames", [])):
            timestamp = float(frame.get("timestamp_s", -1))
            if timestamp < start - 0.05 or timestamp > end + 0.05:
                errors.append(
                    f"{prefix}.evidence_frames.{frame_index}.timestamp_s must fall inside the finding range"
                )
    decision = payload.get("operator_decision", {})
    if decision.get("state") == "approved" and not decision.get("approved_at"):
        errors.append("approved operator_decision requires approved_at")
    if decision.get("state") != "approved" and decision.get("approved_at"):
        errors.append("approved_at must be null until operator_decision is approved")
    return errors


def _learning_semantic_errors(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    review_hashes = set(payload.get("source_review_hashes", []))
    candidate_ids: set[str] = set()
    for index, candidate in enumerate(payload.get("candidates", [])):
        candidate_id = str(candidate.get("candidate_id") or "")
        prefix = f"candidates.{index}"
        if candidate_id in candidate_ids:
            errors.append(f"{prefix}.candidate_id is duplicated: {candidate_id}")
        candidate_ids.add(candidate_id)
        observations = candidate.get("observations", [])
        episodes = {item.get("episode_id") for item in observations}
        lanes = {item.get("lane_id") for item in observations}
        if candidate.get("distinct_episode_count") != len(episodes):
            errors.append(f"{prefix}.distinct_episode_count is stale")
        if candidate.get("distinct_lane_count") != len(lanes):
            errors.append(f"{prefix}.distinct_lane_count is stale")
        if any(item.get("review_hash") not in review_hashes for item in observations):
            errors.append(f"{prefix} contains an observation outside source_review_hashes")
        if candidate.get("operator_gate") == "satisfied" and candidate.get("promotion_state") not in {
            "approved_rule",
            "implemented",
        }:
            errors.append(f"{prefix} operator_gate cannot be satisfied before approval")
    return errors


def validate_artifact(payload: Mapping[str, Any]) -> dict[str, Any]:
    errors = _schema_errors(payload)
    if payload.get("artifact_hash") != canonical_sha256(payload):
        errors.append(f"artifact_hash is stale: expected {canonical_sha256(payload)}")
    if payload.get("schema_version") == "video_watch_review.v1":
        errors.extend(_review_semantic_errors(payload))
    elif payload.get("schema_version") == "video_review_learning.v1":
        errors.extend(_learning_semantic_errors(payload))
    if errors:
        raise VideoReviewValidationError(errors)
    return dict(payload)


def _resolve_input_path(value: str, draft_dir: Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = draft_dir / candidate
    candidate = candidate.resolve()
    if not candidate.is_file():
        raise VideoReviewValidationError([f"evidence file does not exist: {candidate}"])
    return candidate


def _verified_file_hash(path: Path, declared: str | None, label: str) -> str:
    actual = file_sha256(path)
    if declared and declared != ZERO_HASH and declared != actual:
        raise VideoReviewValidationError([f"{label} sha256 mismatch: expected {actual}"])
    return actual


def _evidence_name(finding_id: str, frame_index: int, source: Path) -> str:
    suffix = source.suffix.lower() or ".bin"
    return f"{finding_id}-frame-{frame_index + 1:02d}{suffix}"


def _require_within(path: Path, root: Path, label: str) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise VideoReviewValidationError([f"{label} must stay inside repository root: {root}"]) from exc


def _copy_evidence(payload: dict[str, Any], draft_dir: Path, output_dir: Path) -> dict[str, Any]:
    result = json.loads(json.dumps(payload))
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    source = result["source"]
    if source["kind"] == "local":
        source_path = _resolve_input_path(source["uri"], draft_dir)
        source["sha256"] = _verified_file_hash(source_path, source.get("sha256"), "source")
        source["uri"] = str(source_path)
    elif not source.get("sha256") or source.get("sha256") == ZERO_HASH:
        raise VideoReviewValidationError(["URL source requires the SHA-256 of the downloaded review file"])

    transcript = result.get("transcript")
    if transcript:
        transcript_path = _resolve_input_path(transcript["path"], draft_dir)
        transcript["sha256"] = _verified_file_hash(
            transcript_path, transcript.get("sha256"), "transcript"
        )
        transcript_target = evidence_dir / f"transcript{transcript_path.suffix.lower() or '.txt'}"
        if transcript_path != transcript_target:
            shutil.copy2(transcript_path, transcript_target)
        transcript["path"] = transcript_target.relative_to(output_dir).as_posix()

    for finding in result["findings"]:
        for frame_index, frame in enumerate(finding["evidence_frames"]):
            frame_path = _resolve_input_path(frame["path"], draft_dir)
            frame["sha256"] = _verified_file_hash(
                frame_path, frame.get("sha256"), f"{finding['finding_id']} evidence frame"
            )
            target = evidence_dir / _evidence_name(finding["finding_id"], frame_index, frame_path)
            if frame_path != target:
                shutil.copy2(frame_path, target)
            frame["path"] = target.relative_to(output_dir).as_posix()
    return result


def review_requires_prp(review: Mapping[str, Any]) -> bool:
    """Systemic scopes require grounded planning; episode-only fixes do not."""

    return any(finding.get("scope") in {"lane", "engine", "global"} for finding in review.get("findings", []))


def render_review_markdown(review: Mapping[str, Any]) -> str:
    summary = review["summary"]
    lines = [
        f"# Video Review — {review['episode_id']}",
        "",
        f"- Review: `{review['review_id']}`",
        f"- Source SHA-256: `{review['source']['sha256']}`",
        f"- State: `{summary['overall_state']}`",
        f"- PRP recommended: `{'yes' if review_requires_prp(review) else 'no'}`",
        "",
        summary["assessment"],
        "",
        "## Findings",
        "",
        "| Time | Severity | Scope | Kind | Observable problem | Acceptance |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for finding in review["findings"]:
        time = f"{finding['start_s']:.3f}–{finding['end_s']:.3f}s"
        symptom = str(finding["symptom"]).replace("|", "\\|")
        acceptance = str(finding["acceptance"]).replace("|", "\\|")
        lines.append(
            f"| {time} | {finding['severity']} | {finding['scope']} | {finding['kind']} | {symptom} | {acceptance} |"
        )
    for finding in review["findings"]:
        evidence = ", ".join(f"`{item['path']}`" for item in finding["evidence_frames"])
        lines.extend(
            [
                "",
                f"### {finding['finding_id']}",
                "",
                f"- Root cause: {finding['root_cause']}",
                f"- Viewer/production impact: {finding['impact']}",
                f"- Proposed fix: {finding['proposed_fix']}",
                f"- Confidence: `{finding['confidence']}`",
                f"- Recurrence key: `{finding['recurrence_key']}`",
                f"- Evidence: {evidence}",
            ]
        )
    return "\n".join(lines) + "\n"


def render_edit_delta(review: Mapping[str, Any]) -> str:
    local = [item for item in review["findings"] if item["scope"] == "episode"]
    systemic = [item for item in review["findings"] if item["scope"] != "episode"]
    lines = [
        f"# Edit Delta — {review['episode_id']}",
        "",
        f"Bound to review `{review['review_id']}` and hash `{review['artifact_hash']}`.",
        "",
        "## Episode Corrections",
        "",
    ]
    if local:
        for finding in local:
            lines.append(
                f"- [ ] `{finding['finding_id']}` ({finding['start_s']:.3f}–{finding['end_s']:.3f}s): "
                f"{finding['proposed_fix']} Acceptance: {finding['acceptance']}"
            )
    else:
        lines.append("- None.")
    lines.extend(["", "## PRP Intake", ""])
    if systemic:
        lines.append("Run `prp-plan` with this review packet as mandatory evidence for:")
        lines.append("")
        for finding in systemic:
            lines.append(
                f"- `{finding['finding_id']}` [{finding['scope']}]: {finding['proposed_fix']} "
                f"Acceptance: {finding['acceptance']}"
            )
    else:
        lines.append("No systemic finding requires a PRP. Keep the correction episode-local.")
    lines.extend(
        [
            "",
            "## Rewatch Gate",
            "",
            "After implementation, run `/watch` focused on each finding range and mark a finding `verified` only when its acceptance statement is observable.",
        ]
    )
    return "\n".join(lines) + "\n"


def _candidate_confidence(observations: list[dict[str, Any]], recurrence_total: int) -> float:
    episode_count = len({item["episode_id"] for item in observations})
    lane_count = len({item["lane_id"] for item in observations})
    if lane_count >= 2:
        confidence = 0.8
    elif episode_count >= 2:
        confidence = 0.7
    elif recurrence_total >= 2:
        confidence = 0.5
    else:
        confidence = 0.3
    if observations and all(item["status"] == "verified" for item in observations):
        confidence = min(0.9, confidence + 0.1)
    return round(confidence, 1)


def _recommended_destination(scope: str, episode_count: int, lane_count: int) -> str:
    if scope == "global" and lane_count >= 2:
        return "global_instinct"
    if scope == "engine":
        return "process_runbook"
    if episode_count >= 2 and lane_count == 1:
        return "lane_skill"
    if scope == "episode":
        return "episode_edit_delta"
    return "project_instinct"


def aggregate_review_learnings(reviews: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    validated: list[dict[str, Any]] = []
    seen_review_hashes: set[str] = set()
    for review in reviews:
        item = validate_artifact(review)
        if item["artifact_hash"] not in seen_review_hashes:
            validated.append(item)
            seen_review_hashes.add(item["artifact_hash"])
    if not validated:
        raise VideoReviewValidationError(["at least one review is required"])
    project_ids = {review["project_id"] for review in validated}
    if len(project_ids) != 1:
        raise VideoReviewValidationError(["learning aggregation cannot mix project_id values"])

    grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for review in validated:
        for finding in review["findings"]:
            if finding["status"] == "wont_fix":
                continue
            grouped[finding["recurrence_key"]].append((review, finding))

    candidates: list[dict[str, Any]] = []
    for recurrence_key in sorted(grouped):
        pairs = grouped[recurrence_key]
        triggers = {finding["learning_trigger"] for _, finding in pairs}
        actions = {finding["learning_action"] for _, finding in pairs}
        kinds = {finding["kind"] for _, finding in pairs}
        if len(triggers) != 1 or len(actions) != 1 or len(kinds) != 1:
            raise VideoReviewValidationError(
                [f"recurrence_key {recurrence_key!r} has conflicting trigger, action, or kind"]
            )
        observations = [
            {
                "review_id": review["review_id"],
                "review_hash": review["artifact_hash"],
                "finding_id": finding["finding_id"],
                "episode_id": review["episode_id"],
                "lane_id": review["lane_id"],
                "scope": finding["scope"],
                "status": finding["status"],
            }
            for review, finding in pairs
        ]
        episode_count = len({item["episode_id"] for item in observations})
        lane_count = len({item["lane_id"] for item in observations})
        recurrence_total = sum(int(finding["recurrence_count"]) for _, finding in pairs)
        scope = max((finding["scope"] for _, finding in pairs), key=SCOPE_RANK.__getitem__)
        promotion_state = max(
            (finding["promotion_state"] for _, finding in pairs), key=PROMOTION_RANK.__getitem__
        )
        if promotion_state == "observation" and (episode_count >= 2 or recurrence_total >= 2):
            promotion_state = "candidate_rule"
        approved = promotion_state in {"approved_rule", "implemented"}
        candidates.append(
            {
                "candidate_id": f"learning-{recurrence_key}",
                "recurrence_key": recurrence_key,
                "kind": next(iter(kinds)),
                "trigger": next(iter(triggers)),
                "action": next(iter(actions)),
                "scope": scope,
                "confidence": _candidate_confidence(observations, recurrence_total),
                "observations": observations,
                "distinct_episode_count": episode_count,
                "distinct_lane_count": lane_count,
                "recommended_destination": _recommended_destination(scope, episode_count, lane_count),
                "promotion_state": promotion_state,
                "operator_gate": "satisfied" if approved else "required",
            }
        )

    artifact = with_artifact_hash(
        {
            "schema_version": "video_review_learning.v1",
            "project_id": next(iter(project_ids)),
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_review_hashes": sorted(seen_review_hashes),
            "candidates": candidates,
        }
    )
    return validate_artifact(artifact)


def render_learning_markdown(learning: Mapping[str, Any]) -> str:
    lines = [
        f"# Video Review Learning Candidates — {learning['project_id']}",
        "",
        "Candidates are evidence-backed suggestions. `operator_gate: required` forbids automatic skill, runbook, or global-memory changes.",
        "",
        "| Candidate | Confidence | Episodes | Lanes | Destination | Promotion |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for candidate in learning["candidates"]:
        lines.append(
            f"| `{candidate['candidate_id']}` | {candidate['confidence']:.1f} | "
            f"{candidate['distinct_episode_count']} | {candidate['distinct_lane_count']} | "
            f"{candidate['recommended_destination']} | {candidate['promotion_state']} |"
        )
        lines.extend(
            [
                "",
                f"- Trigger: {candidate['trigger']}",
                f"- Action: {candidate['action']}",
                f"- Operator gate: `{candidate['operator_gate']}`",
            ]
        )
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def compile_review_packet(
    draft_path: str | Path, output_dir: str | Path, *, repo_root: str | Path | None = None
) -> dict[str, Path]:
    draft_path = Path(draft_path).resolve()
    output_dir = Path(output_dir).resolve()
    if repo_root is not None:
        _require_within(output_dir, Path(repo_root).resolve(), "output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)
    draft = load_json(draft_path)
    draft.pop("artifact_hash", None)
    prepared = _copy_evidence(draft, draft_path.parent, output_dir)
    review = with_artifact_hash(prepared)
    validate_artifact(review)
    learning = aggregate_review_learnings([review])

    review_json = output_dir / "watch-review.v1.json"
    review_md = output_dir / "watch-review.md"
    edit_delta = output_dir / "edit-delta.md"
    learning_json = output_dir / "learning-candidates.v1.json"
    learning_md = output_dir / "learning-candidates.md"
    _write_json(review_json, review)
    review_md.write_text(render_review_markdown(review), encoding="utf-8")
    edit_delta.write_text(render_edit_delta(review), encoding="utf-8")
    _write_json(learning_json, learning)
    learning_md.write_text(render_learning_markdown(learning), encoding="utf-8")
    return {
        "review_json": review_json,
        "review_markdown": review_md,
        "edit_delta": edit_delta,
        "learning_json": learning_json,
        "learning_markdown": learning_md,
    }


def write_aggregated_learning(
    review_paths: Iterable[str | Path],
    output_json: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Path]:
    reviews = [load_json(path) for path in review_paths]
    learning = aggregate_review_learnings(reviews)
    output_json = Path(output_json).resolve()
    if repo_root is not None:
        _require_within(output_json, Path(repo_root).resolve(), "output")
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md = output_json.with_suffix(".md")
    _write_json(output_json, learning)
    output_md.write_text(render_learning_markdown(learning), encoding="utf-8")
    return {"learning_json": output_json, "learning_markdown": output_md}
