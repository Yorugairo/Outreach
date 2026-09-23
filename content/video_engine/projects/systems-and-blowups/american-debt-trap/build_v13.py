"""Build the American Debt Trap V13 measured-prefix pilot.

This module owns only the episode hand-off.  The frozen narration and scratch
take are read, never regenerated; the episode shot table is authored by the
parent and is loaded only at compile time.  The output stays in a private
build directory and its receipt explicitly remains quarantined for review.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCRIPTS = REPO / "content/video_engine/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from align_take import script_tokens  # noqa: E402
from authoring import Project  # noqa: E402
from authoring import audio as A, docks as D, table as T, words as W  # noqa: E402
from run_script_gates import script_hash  # noqa: E402


EPISODE_ID = "american-debt-trap-v13"
BUILD_VERSION = "V13"
VIDEO_FORM = "short"
SCRIPT_PATH = HERE.parents[4] / "docs/research/runs/american-debt-trap-20260920/script-review/REVISED-V13-VO.txt"
SCRIPT_NAME = SCRIPT_PATH.name
TAKE_STEM = "scratch-kokoro"
SHOT_TABLE_NAME = "SHOT-TABLE-V13.py"
DEFAULT_BUILD_ROOT = HERE / "build-private/v13"
GATE_SCRIPT = SCRIPTS / "gate_opening_structure.py"
OPENING_COUNTERPARTY = "refinancing"
OPENING_RING = "renewal letter"
OPENING_TITLE = "Inside the Great American Debt Trap: How It Becomes Your Problem"
SEGMENT_TARGETS = {"bed": 30.0, "unit": 90.0, "pilot": 180.0}
TIMELINE_NAMES = {
    segment: f"{EPISODE_ID}-{segment}.timeline.json"
    for segment in SEGMENT_TARGETS
}
# A later operator-selected manifest wins automatically; the verified candidate
# inventory remains a safe fallback until that selection exists.
ASSET_MANIFEST_NAMES = ("SELECTED-ASSETS.json", "ASSET-CANDIDATES.json")
_RESULT_RE = re.compile(
    r"RESULT:\s*(\d+) FAIL / (\d+) WARN / (\d+) PASS / (\d+) JUDGE",
    re.I,
)
_HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class BuildInputError(ValueError):
    """A missing or contradictory input that must stop the build."""


@dataclass(frozen=True)
class SegmentBoundary:
    segment: str
    target_s: float
    end_s: float
    end_word_index: int
    closing_sentence: str


@dataclass(frozen=True)
class GateResult:
    exit_code: int
    report_path: Path
    fail_count: int | None
    warn_count: int | None
    pass_count: int | None
    judge_count: int | None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool):
        raise BuildInputError(f"{label} must be numeric")
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise BuildInputError(f"{label} must be numeric") from exc
    if not math.isfinite(value):
        raise BuildInputError(f"{label} must be finite")
    return value


def load_words(take_dir: Path, take_stem: str = TAKE_STEM) -> list[dict[str, Any]]:
    """Read and validate the measured take's word clock without rewriting it."""
    path = Path(take_dir) / f"{take_stem}.words.json"
    if not path.is_file():
        raise BuildInputError(f"take words missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildInputError(f"take words unreadable: {path}: {exc}") from exc
    words = payload.get("words") if isinstance(payload, dict) else payload
    if not isinstance(words, list) or not words:
        raise BuildInputError(f"take words must be a non-empty array: {path}")

    previous_end = -math.inf
    checked: list[dict[str, Any]] = []
    for index, word in enumerate(words):
        if not isinstance(word, dict) or not isinstance(word.get("w"), str) or not word["w"].strip():
            raise BuildInputError(f"take word {index} is missing spoken text")
        start = _finite(word.get("start_s"), f"take word {index} start_s")
        end = _finite(word.get("end_s"), f"take word {index} end_s")
        if start < 0 or end <= start:
            raise BuildInputError(f"take word {index} has invalid span {start:.3f}-{end:.3f}")
        if start < previous_end - 1e-6:
            raise BuildInputError(f"take word {index} overlaps the preceding word")
        previous_end = end
        checked.append({**word, "start_s": start, "end_s": end})
    return checked


def verify_canonical_alignment(words: list[dict[str, Any]], script_path: Path | None = None) -> str:
    """Require the scratch word sequence to equal the frozen V13 spoken tokens."""
    script_path = SCRIPT_PATH if script_path is None else Path(script_path)
    if not script_path.is_file():
        raise BuildInputError(f"frozen narration missing: {script_path}")
    text = script_path.read_text(encoding="utf-8")
    expected = script_tokens(text)
    actual = [str(word["w"]) for word in words]
    if actual != expected:
        limit = min(len(actual), len(expected))
        first = next((i for i in range(limit) if actual[i] != expected[i]), limit)
        got = actual[first] if first < len(actual) else "<missing>"
        want = expected[first] if first < len(expected) else "<missing>"
        raise BuildInputError(
            f"canonical narration token alignment failed at word {first}: got {got!r}, expected {want!r}; "
            f"take has {len(actual)} tokens, frozen V13 has {len(expected)}"
        )
    return script_hash(text)


def complete_sentence_boundary(words: list[dict[str, Any]], segment: str) -> SegmentBoundary:
    """Choose the latest complete spoken sentence whose measured end fits the cap."""
    if segment not in SEGMENT_TARGETS:
        raise BuildInputError(f"unknown segment {segment!r}; choose bed, unit, or pilot")
    target = SEGMENT_TARGETS[segment]
    sentence_start = 0
    candidates: list[tuple[float, int, str]] = []
    for index, word in enumerate(words):
        token = str(word["w"]).rstrip(W.QUOTE_TAIL)
        if token.endswith(tuple(W.HARD_STOPS)):
            end = float(word["end_s"])
            if end <= target + 1e-6:
                phrase = " ".join(str(item["w"]) for item in words[sentence_start:index + 1])
                candidates.append((end, index, phrase))
            sentence_start = index + 1
    if not candidates:
        raise BuildInputError(f"{segment}: no complete sentence ends by {target:.2f}s")
    end, index, phrase = max(candidates, key=lambda item: item[0])
    return SegmentBoundary(segment, target, round(end, 3), index, phrase)


def _project(build: Path, take_dir: Path) -> Project:
    return Project(
        here=HERE,
        build=Path(build),
        take=Path(take_dir),
        take_stem=TAKE_STEM,
        script_name=SCRIPT_NAME,
        episode_id=EPISODE_ID,
        take_name=Path(take_dir).name,
    )


def _resolve_build_dir(segment: str, explicit: Path | None) -> Path:
    if explicit is not None:
        path = Path(explicit)
        return path if path.is_absolute() else (HERE / path)
    return DEFAULT_BUILD_ROOT / segment


def _resolve_repo_path(raw: Any, label: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise BuildInputError(f"{label}: path is required")
    candidate = Path(raw)
    options = [candidate] if candidate.is_absolute() else [REPO / candidate, HERE / candidate]
    path = next((item.resolve() for item in options if item.is_file()), None)
    if path is None:
        raise BuildInputError(f"{label}: file not found: {raw}")
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise BuildInputError(f"{label}: path must remain inside the repository: {raw}") from exc
    return path


def _field_value(payload: Any, field: str) -> Any:
    value = payload
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def load_asset_manifest(path: Path | None = None) -> list[dict[str, Any]]:
    """Load the episode candidate/selection manifest and verify every binding."""
    manifest = Path(path) if path is not None else next(
        (HERE / name for name in ASSET_MANIFEST_NAMES if (HERE / name).is_file()), None
    )
    if manifest is None:
        raise BuildInputError(
            "asset manifest missing; provide ASSET-CANDIDATES.json or SELECTED-ASSETS.json "
            "with ID/path/hash/approval bindings"
        )
    try:
        document = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildInputError(f"asset manifest unreadable: {manifest}: {exc}") from exc
    entries = None
    if isinstance(document, dict):
        # The inventory worker calls this field ``items``; the older selected
        # manifest contract calls it ``assets``.  Both carry the same
        # id/path/hash/approval binding and neither implies visual approval.
        entries = document.get("assets", document.get("items"))
    else:
        entries = document
    if not isinstance(entries, list):
        raise BuildInputError(f"asset manifest must contain an assets array: {manifest}")
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise BuildInputError(f"asset manifest item {index} must be an object")
        asset_id = raw.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id or asset_id in seen:
            raise BuildInputError(f"asset manifest item {index} has a missing or duplicate asset_id")
        seen.add(asset_id)
        asset = _resolve_repo_path(raw.get("path"), f"asset {asset_id}")
        approval = _resolve_repo_path(raw.get("approval_path"), f"approval {asset_id}")
        recorded_asset = raw.get("sha256")
        recorded_approval = raw.get("approval_sha256")
        if not _HEX64.fullmatch(str(recorded_asset or "")) or not _HEX64.fullmatch(str(recorded_approval or "")):
            raise BuildInputError(f"asset {asset_id}: sha256 and approval_sha256 must be 64 hex characters")
        actual_asset = _sha256(asset)
        actual_approval = _sha256(approval)
        if actual_asset.lower() != str(recorded_asset).lower():
            raise BuildInputError(f"asset {asset_id}: sha256 mismatch")
        if actual_approval.lower() != str(recorded_approval).lower():
            raise BuildInputError(f"asset {asset_id}: approval_sha256 mismatch")
        approval_field = raw.get("approval_field")
        if not isinstance(approval_field, str) or not approval_field:
            raise BuildInputError(f"asset {asset_id}: approval_field is required")
        try:
            approval_payload = json.loads(approval.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BuildInputError(f"approval {asset_id}: unreadable JSON: {exc}") from exc
        expected_approval = raw.get("approval_value")
        actual_approval_value = _field_value(approval_payload, approval_field)
        approval_matches = actual_approval_value == expected_approval
        if isinstance(actual_approval_value, list) and not isinstance(expected_approval, list):
            approval_matches = expected_approval in actual_approval_value
        if not approval_matches:
            raise BuildInputError(
                f"asset {asset_id}: approval {approval_field!r} is not {expected_approval!r}"
            )
        out.append({
            "asset_id": asset_id,
            "path": asset,
            "sha256": actual_asset,
            "approval_path": approval,
            "approval_sha256": actual_approval,
            "approval_field": approval_field,
            "approval_value": expected_approval,
        })
    return out


def register_assets(entries: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Register only manifest-verified assets with the native render resolver."""
    items = list(entries)
    for entry in items:
        D.register(str(entry["asset_id"]), Path(entry["path"]))
    return items


def _load_shot_table() -> ModuleType:
    path = HERE / SHOT_TABLE_NAME
    if not path.is_file():
        raise BuildInputError(f"episode shot table missing: {path}")
    spec = importlib.util.spec_from_file_location("american_debt_trap_v13_shot_table", path)
    if spec is None or spec.loader is None:
        raise BuildInputError(f"episode shot table cannot be loaded: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "build_rows", None)):
        raise BuildInputError(f"episode shot table must expose build_rows: {path}")
    return module


def _validate_rows(rows: list[tuple], runtime_s: float) -> None:
    if not rows:
        raise BuildInputError("shot table returned no rows")
    previous_end = 0.0
    for index, row in enumerate(rows):
        if not isinstance(row, tuple) or len(row) < 6:
            raise BuildInputError(f"shot row {index} must be a tuple with at least six fields")
        start = _finite(row[0], f"shot row {index} start")
        end = _finite(row[1], f"shot row {index} end")
        if start < -1e-6 or end <= start:
            raise BuildInputError(f"shot row {index} has invalid span {start:.3f}-{end:.3f}")
        if abs(start - previous_end) > 0.05:
            raise BuildInputError(f"shot rows are not contiguous before row {index}: {previous_end:.3f} -> {start:.3f}")
        previous_end = end
    if abs(previous_end - runtime_s) > 0.05:
        raise BuildInputError(f"shot table ends at {previous_end:.3f}s, measured runtime is {runtime_s:.3f}s")


def _write_measured_timeline(project: Project, words: list[dict[str, Any]], runtime_s: float) -> Path:
    project.build.mkdir(parents=True, exist_ok=True)
    project.mkdirs()
    W.write_timeline(project, words, runtime_s)
    return project.build / "timeline.json"


def _run_opening_gate(script: Path, timeline: Path, report_path: Path) -> GateResult:
    """Run the real opening gate against full canonical start/end word timings."""
    command = [
        sys.executable,
        str(GATE_SCRIPT),
        str(script),
        "--timeline",
        str(timeline),
        "--counterparty",
        OPENING_COUNTERPARTY,
        "--ring",
        OPENING_RING,
        "--title",
        OPENING_TITLE,
        "--long",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    output = completed.stdout
    if completed.stderr:
        output += ("\n" if output else "") + completed.stderr
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        "$ " + " ".join(command) + "\n\n" + output,
        encoding="utf-8",
    )
    match = _RESULT_RE.search(output)
    counts = tuple(int(value) for value in match.groups()) if match else (None, None, None, None)
    return GateResult(completed.returncode, report_path, *counts)


def _trim_audio(source: Path, build: Path, runtime_s: float) -> Path:
    destination = build / "audio/episode.mp3"
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(source), "-t", f"{runtime_s:.3f}",
         "-c:a", "libmp3lame", "-q:a", "2", str(destination)],
        check=True,
    )
    return destination


def _hash_if_file(path: Path) -> str | None:
    return _sha256(path) if path.is_file() else None


def _write_receipt(
    *,
    build: Path,
    take_dir: Path,
    boundary: SegmentBoundary,
    script_hash_value: str,
    words_path: Path,
    source_audio: Path,
    gate: GateResult,
    full_timeline: Path,
    segment_timeline: Path,
    shot_table: Path,
    authored_shot_table: Path,
    assets: list[dict[str, Any]],
) -> Path:
    receipt = {
        "schema": f"american-debt-trap.{BUILD_VERSION.lower()}.build-receipt.v1",
        "episode_id": EPISODE_ID,
        "segment": boundary.segment,
        "quarantine": True,
        "visual_approval": {"state": "pending", "claim": "not visually approved"},
        "release": {"published": False, "final_voice": False, "git_action": False},
        "script": {"path": _repo_relative(SCRIPT_PATH), "spoken_sha256": script_hash_value, "token_aligned": True},
        "take": {
            "words_path": _repo_relative(words_path),
            "words_sha256": _sha256(words_path),
            "audio_path": _repo_relative(source_audio),
            "audio_sha256": _sha256(source_audio),
            "take_stem": TAKE_STEM,
        },
        "boundary": {
            "target_s": boundary.target_s,
            "end_s": boundary.end_s,
            "end_word_index": boundary.end_word_index,
            "closing_sentence": boundary.closing_sentence,
        },
        "opening_gate": {
            "report_path": _repo_relative(gate.report_path),
            "report_sha256": _sha256(gate.report_path),
            "exit_code": gate.exit_code,
            "fail": gate.fail_count,
            "warn": gate.warn_count,
            "pass": gate.pass_count,
            "judge": gate.judge_count,
            "force_used": False,
        },
        "timelines": {
            "full_measured_path": _repo_relative(full_timeline),
            "full_measured_sha256": _sha256(full_timeline),
            "segment_path": _repo_relative(segment_timeline),
            "segment_sha256": _sha256(segment_timeline),
        },
        "shot_table": {
            "path": _repo_relative(shot_table),
            "sha256": _sha256(shot_table),
            "authored_path": _repo_relative(authored_shot_table),
            "authored_sha256": _sha256(authored_shot_table),
        },
        "assets": [
            {
                "asset_id": item["asset_id"],
                "path": _repo_relative(item["path"]),
                "sha256": item["sha256"],
                "approval_path": _repo_relative(item["approval_path"]),
                "approval_sha256": item["approval_sha256"],
                "approval_field": item["approval_field"],
                "approval_value": item["approval_value"],
            }
            for item in assets
        ],
        "compiled": {
            "player_manifest": _hash_if_file(build / "player.json"),
            "scene_timeline": _hash_if_file(build / TIMELINE_NAMES[boundary.segment]),
            "review_only": True,
        },
    }
    path = build / f"BUILD-{BUILD_VERSION}-RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def check_inputs(*, take_dir: Path | None, script_path: Path | None = None, asset_manifest: Path | None = None) -> list[str]:
    """Return blockers without creating a build or touching the scratch take."""
    script_path = SCRIPT_PATH if script_path is None else Path(script_path)
    blockers: list[str] = []
    if take_dir is None:
        return ["--take-dir is required; scratch generation is not part of this builder"]
    take_dir = Path(take_dir)
    if not take_dir.is_dir():
        blockers.append(f"take directory missing: {take_dir}")
        return blockers
    try:
        words = load_words(take_dir)
        verify_canonical_alignment(words, script_path)
    except BuildInputError as exc:
        blockers.append(str(exc))
    audio = take_dir / f"{TAKE_STEM}.mp3"
    if not audio.is_file():
        blockers.append(f"take audio missing: {audio}")
    try:
        load_asset_manifest(asset_manifest)
    except BuildInputError as exc:
        blockers.append(str(exc))
    return blockers


def _write_effective_shot_table(build: Path, rows: list[tuple]) -> Path:
    """Persist the resolved rows for native T without rewriting the authored table."""
    path = build / f"SHOT-TABLE-{BUILD_VERSION}-EFFECTIVE.py"
    header = (
        f'"""Generated, quarantined {BUILD_VERSION} row hand-off; source table remains authored elsewhere.\n'
        'This file is not visual approval or release evidence.\n'
        '"""\n'
    )
    return T.write_shot_table(path, rows, header)


def build(*, segment: str, take_dir: Path, build_dir: Path | None = None, asset_manifest: Path | None = None) -> int:
    """Build one measured segment and return the native compiler status."""
    if segment not in SEGMENT_TARGETS:
        raise BuildInputError(f"unknown segment {segment!r}; choose bed, unit, or pilot")
    blockers = check_inputs(take_dir=take_dir, asset_manifest=asset_manifest)
    if blockers:
        raise BuildInputError("; ".join(blockers))

    take_dir = Path(take_dir).resolve()
    build = _resolve_build_dir(segment, build_dir).resolve()
    words_path = take_dir / f"{TAKE_STEM}.words.json"
    source_audio = take_dir / f"{TAKE_STEM}.mp3"
    words = load_words(take_dir)
    spoken_hash = verify_canonical_alignment(words)
    boundary = complete_sentence_boundary(words, segment)
    full_runtime = round(float(words[-1]["end_s"]), 3)
    full_project = _project(build / "gate-full-v13", take_dir)
    full_timeline = _write_measured_timeline(full_project, words, full_runtime)
    gate = _run_opening_gate(SCRIPT_PATH, full_timeline, build / f"GATES-OPENING-{BUILD_VERSION}.md")
    if gate.exit_code != 0 or (gate.fail_count or 0) > 0:
        raise BuildInputError(
            f"opening gate failed ({gate.fail_count} FAIL, {gate.warn_count} WARN); report: {gate.report_path}"
        )

    project = _project(build, take_dir)
    project.mkdirs()
    selected_words = words[: boundary.end_word_index + 1]
    _trim_audio(source_audio, build, boundary.end_s)
    segment_timeline = _write_measured_timeline(project, selected_words, boundary.end_s)

    table_module = _load_shot_table()
    assets = register_assets(load_asset_manifest(asset_manifest))
    register_table_assets = getattr(table_module, "register_assets", None)
    if register_table_assets is not None:
        if not callable(register_table_assets):
            raise BuildInputError("episode shot table register_assets must be callable")
        register_table_assets(D)
    dock_meta = getattr(table_module, "DOCK_META", None)
    if dock_meta is not None:
        if not isinstance(dock_meta, list) or not all(isinstance(item, dict) for item in dock_meta):
            raise BuildInputError("episode shot table DOCK_META must be a list of objects")
        (build / "evidence-dock.json").write_text(
            json.dumps(dock_meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    # The table resolves all phrase anchors against the complete measured take,
    # then owns clipping its authored rows to this segment's sentence boundary.
    try:
        # Resolve all anchors against the full measured take; the episode table
        # decides whether its authored evidence reaches this segment.
        rows = list(table_module.build_rows(words, boundary.end_s, segment))
    except (TypeError, ValueError, KeyError) as exc:
        raise BuildInputError(f"episode shot table refused {segment}: {exc}") from exc
    _validate_rows(rows, boundary.end_s)
    authored_shot_table = HERE / SHOT_TABLE_NAME
    effective_shot_table = _write_effective_shot_table(build, rows)
    effective_shot_table_arg = os.path.relpath(effective_shot_table, HERE).replace("\\", "/")
    T.caption_pages(build, char_budget=34, max_words=6)
    rc = T.compile_timeline(
        HERE,
        build,
        timeline_name=TIMELINE_NAMES[segment],
        shot_table_file=effective_shot_table_arg,
        title="America's Debt Trap",
        subtitle="Money Physics · measured opening pilot",
        episode_id=f"{EPISODE_ID}-{segment}",
        aspect="16:9",
        caption_style="phrase",
        kinetics={
            "analytic_spring": True,
            "min_jerk": True,
            "area_squash": True,
            "curvature_stroke": True,
            "plate_idle_paints": False,
            **({
                "first_chart_policy": "opening_ledger_action",
                "first_quant_claim_at": 98.362,
            } if BUILD_VERSION == "V15" else {}),
        },
        render=True,
        form=VIDEO_FORM,
    )
    if rc != 0:
        return int(rc)
    receipt = _write_receipt(
        build=build,
        take_dir=take_dir,
        boundary=boundary,
        script_hash_value=spoken_hash,
        words_path=words_path,
        source_audio=source_audio,
        gate=gate,
        full_timeline=full_timeline,
        segment_timeline=segment_timeline,
        shot_table=effective_shot_table,
        authored_shot_table=authored_shot_table,
        assets=assets,
    )
    print(f"segment={segment} runtime={boundary.end_s:.3f}s closing={boundary.closing_sentence}")
    print(f"opening gate={gate.fail_count} FAIL / {gate.warn_count} WARN; report={gate.report_path}")
    print(f"quarantine receipt={receipt}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the quarantined American Debt Trap V13 measured pilot")
    parser.add_argument("--segment", choices=tuple(SEGMENT_TARGETS), required=True)
    parser.add_argument("--take-dir", type=Path, required=True, help="existing scratch take directory; never generated here")
    parser.add_argument("--build-dir", type=Path, help="exact private output directory; defaults to build-private/v13/<segment>")
    parser.add_argument("--asset-manifest", type=Path, help="episode ASSET-CANDIDATES/SELECTED-ASSETS manifest")
    parser.add_argument("--check-inputs", action="store_true", help="validate inputs without creating a build")
    args = parser.parse_args(argv)
    try:
        if args.check_inputs:
            blockers = check_inputs(take_dir=args.take_dir, asset_manifest=args.asset_manifest)
            for blocker in blockers:
                print(f"[FAIL] {blocker}")
            if not blockers:
                print(f"[PASS] frozen {BUILD_VERSION} narration and measured scratch inputs are aligned")
            return 1 if blockers else 0
        return build(
            segment=args.segment,
            take_dir=args.take_dir,
            build_dir=args.build_dir,
            asset_manifest=args.asset_manifest,
        )
    except (BuildInputError, OSError, subprocess.CalledProcessError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
