"""Deterministic read model for the local Remotion Production Console."""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator


SNAPSHOT_VERSION = "production_console_snapshot.v1"
DEFAULT_COMPOSITION_ID = "EditorialMotion"


class ProductionConsoleSnapshotError(ValueError):
    """Raised when canonical console inputs cannot produce a safe snapshot."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductionConsoleSnapshotError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductionConsoleSnapshotError(f"JSON artifact must be an object: {path}")
    return value


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    core = {key: item for key, item in value.items() if key != "artifact_hash"}
    encoded = json.dumps(
        core,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_relative(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ProductionConsoleSnapshotError(f"artifact escapes project root: {path}") from exc
    return relative.as_posix()


def _ordered_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _title_from_chapter(chapter: str, fallback: str) -> str:
    parts = str(chapter or "").split("-")
    words = parts[6:] if len(parts) > 6 else parts
    title = " ".join(words).replace("_", " ").strip().title()
    return title or fallback


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / "production_console_snapshot.schema.json"


def validate_production_console_snapshot(payload: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(payload)
    errors = sorted(
        Draft202012Validator(_read_json(_schema_path())).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors[:8]
        )
        raise ProductionConsoleSnapshotError(f"snapshot schema validation failed: {detail}")
    expected = _canonical_sha256(value)
    if value.get("artifact_hash") != expected:
        raise ProductionConsoleSnapshotError("snapshot artifact_hash does not match canonical content")
    return value


def _artifact_record(
    project_root: Path,
    artifact_id: str,
    kind: str,
    relative_path: str,
    *,
    required: bool,
    degraded: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    path = (project_root / relative_path).resolve()
    try:
        path.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ProductionConsoleSnapshotError(f"configured artifact escapes project root: {relative_path}") from exc
    if not path.is_file():
        reason = f"{artifact_id}: missing {relative_path}"
        degraded.append(reason)
        if required:
            raise ProductionConsoleSnapshotError(reason)
        return None, None
    payload = _read_json(path)
    sha256 = _file_sha256(path)
    return (
        {
            "artifact_id": artifact_id,
            "kind": kind,
            "path": _safe_relative(path, project_root),
            "sha256": sha256,
            "status": "available",
            "degraded_reason": None,
        },
        payload,
    )


def _compile_scenes(
    flow: Mapping[str, Any],
    bundles: Mapping[str, Any],
    motion: Mapping[str, Any],
    cue_sheet: Mapping[str, Any],
) -> list[dict[str, Any]]:
    bundle_map = {
        str(bundle.get("id")): bundle
        for bundle in bundles.get("bundles", [])
        if isinstance(bundle, Mapping) and bundle.get("id")
    }
    cues = [cue for cue in cue_sheet.get("cues", []) if isinstance(cue, Mapping)]
    cue_by_id = {str(cue.get("cue_id")): cue for cue in cues if cue.get("cue_id")}
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for shot in motion.get("shots", []):
        if isinstance(shot, Mapping) and shot.get("parent_scene_bundle_id"):
            grouped[str(shot["parent_scene_bundle_id"])].append(shot)

    scenes: list[dict[str, Any]] = []
    for scene_id in flow.get("nodes", []):
        scene_id = str(scene_id)
        shots = sorted(grouped.get(scene_id, []), key=lambda shot: float(shot.get("start_s", 0)))
        if not shots:
            continue
        start_s = min(float(shot.get("start_s", 0)) for shot in shots)
        end_s = max(
            float(shot.get("start_s", 0)) + float(shot.get("duration_s", 0))
            for shot in shots
        )
        cue_refs: list[str] = []
        claim_refs: list[str] = []
        asset_ids: list[str] = []
        for shot in shots:
            for beat_id in shot.get("parent_beat_ids", []):
                cue_id = str(beat_id).replace("-beat-", "-cue-")
                cue = cue_by_id.get(cue_id)
                if cue:
                    cue_refs.append(cue_id)
                    claim_refs.extend(str(item) for item in cue.get("claim_refs", []))
            asset_ids.extend(
                str(layer.get("asset_id"))
                for layer in shot.get("layers", [])
                if isinstance(layer, Mapping) and layer.get("asset_id")
            )
        bundle = bundle_map.get(scene_id, {})
        scenes.append(
            {
                "scene_id": scene_id,
                "title": _title_from_chapter(str(bundle.get("chapter", "")), scene_id),
                "start_s": round(start_s, 6),
                "end_s": round(end_s, 6),
                "cue_refs": _ordered_unique(cue_refs),
                "claim_refs": _ordered_unique(claim_refs),
                "asset_ids": _ordered_unique(asset_ids),
                "review_state": "unreviewed",
            }
        )
    if not scenes:
        raise ProductionConsoleSnapshotError("canonical motion plan produced no scenes")
    return scenes


def _compile_words(words_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, word in enumerate(words_payload.get("words", [])):
        if not isinstance(word, Mapping):
            continue
        result.append(
            {
                "word_id": f"word-{index:05d}",
                "text": str(word.get("w", word.get("text", ""))),
                "start_s": round(float(word.get("start_s", 0)), 6),
                "end_s": round(float(word.get("end_s", word.get("start_s", 0))), 6),
            }
        )
    return result


def _compile_project_assets(asset_map: Mapping[str, Any], project_root: Path, degraded: list[str]) -> list[dict[str, Any]]:
    assets: list[dict[str, Any]] = []
    missing_count = 0
    raw_assets = asset_map.get("assets", {})
    if not isinstance(raw_assets, Mapping):
        raise ProductionConsoleSnapshotError("asset map assets must be an object")
    for asset_id in sorted(raw_assets):
        record = raw_assets[asset_id]
        if not isinstance(record, Mapping) or not record.get("path") or not record.get("sha256"):
            continue
        path = project_root / str(record["path"])
        if not path.is_file():
            missing_count += 1
            continue
        evidence_eligible = record.get("evidence_eligible") is True
        assets.append(
            {
                "asset_id": str(asset_id),
                "label": str(record.get("label") or asset_id).replace("-", " ").title(),
                "path_root": "project",
                "path": _safe_relative(path, project_root),
                "sha256": str(record["sha256"]),
                "source_kind": "evidence_surface" if evidence_eligible else "project_asset",
                "approval_scope": "evidence" if evidence_eligible else "review_only",
                "evidence_eligible": evidence_eligible,
                "rights_state": "review_only",
                "context_status": "review_only",
                "deck_id": None,
                "slide_number": None,
                "width": None,
                "height": None,
                "what_it_is": str(record.get("kind") or "project asset"),
                "claim_refs": [],
                "cue_refs": [],
            }
        )
    if missing_count:
        degraded.append(f"project_assets: {missing_count} manifest entries are not staged in this metadata baseline")
    return assets


def _compile_production_visuals(
    catalog_path: Path | None,
    repository_root: Path,
    degraded: list[str],
) -> list[dict[str, Any]]:
    if catalog_path is None or not catalog_path.is_file():
        degraded.append("production_visuals: approved teacher-stamped catalog has not been generated")
        return []
    catalog = _read_json(catalog_path)
    assets: list[dict[str, Any]] = []
    records = catalog.get("visuals", catalog.get("assets", []))
    if not isinstance(records, list):
        raise ProductionConsoleSnapshotError("production visual catalog must contain a visuals array")
    for record in records:
        if not isinstance(record, Mapping):
            continue
        asset_id = str(record.get("image_id") or record.get("asset_id") or "")
        asset_path = str(record.get("extracted_path") or record.get("path") or "")
        if not asset_id or not asset_path:
            raise ProductionConsoleSnapshotError("production visual is missing image_id/asset_id or extracted_path/path")
        absolute = (catalog_path.parent / asset_path).resolve()
        _safe_relative(absolute, repository_root)
        if not absolute.is_file():
            degraded.append(f"production_visuals: missing {asset_id}")
            continue
        sha256 = _file_sha256(absolute)
        if sha256 != record.get("sha256"):
            raise ProductionConsoleSnapshotError(
                f"production visual hash mismatch: {asset_id}"
            )
        context = record.get("context", {})
        if not isinstance(context, Mapping):
            context = {}
        evidence_eligible = record.get("evidence_render_eligible") is True
        assets.append(
            {
                "asset_id": asset_id,
                "label": str(context.get("label") or record.get("label") or asset_id),
                "path_root": "repository",
                "path": _safe_relative(absolute, repository_root),
                "sha256": sha256,
                "source_kind": "production_visual",
                "approval_scope": "production_visuals",
                "evidence_eligible": evidence_eligible,
                "rights_state": "operator_authorized" if record.get("render_eligible") is True else str(record.get("rights_state") or "review_only"),
                "context_status": str(context.get("context_status") or record.get("context_status") or "review_only"),
                "deck_id": str(record.get("deck_id")) if record.get("deck_id") else None,
                "slide_number": int(record["slide_number"]) if record.get("slide_number") else None,
                "width": int(record["width"]) if record.get("width") else None,
                "height": int(record["height"]) if record.get("height") else None,
                "what_it_is": str(context.get("summary") or record.get("what_it_is") or "approved stamped slide"),
                "claim_refs": [str(value) for value in context.get("claim_refs", record.get("claim_refs", []))],
                "cue_refs": [str(value) for value in context.get("cue_refs", record.get("cue_refs", []))],
            }
        )
    return assets


def compile_production_console_snapshot(
    project_root: str | Path,
    *,
    repository_root: str | Path | None = None,
    production_visual_catalog: str | Path | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compile existing canonical artifacts into one read-only console snapshot."""

    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ProductionConsoleSnapshotError(f"project root does not exist: {root}")
    repository = Path(repository_root).resolve() if repository_root else Path(__file__).resolve().parents[3]
    if not repository.is_dir():
        raise ProductionConsoleSnapshotError(f"repository root does not exist: {repository}")
    # The episode and reusable production-visual catalog may live in separate
    # explicitly configured workspace roots.  Every resolved artifact is still
    # constrained to its declared root below; requiring one root to contain the
    # other would make multi-worktree editing impossible without copying media.

    degraded: list[str] = []
    specs = [
        ("scene_flow", "scene_flow_graph", "edit/word-timed-v1/scene-flow-graph.v1.json", True),
        ("scene_bundles", "scene_bundles", "edit/word-timed-v1/scene-bundles.v1.json", True),
        ("pacing_recipe", "pacing_recipe", "edit/word-timed-v1/pacing-recipe.v1.json", False),
        ("overlay_map", "overlay_map", "edit/word-timed-v1/overlay-map.v1.json", False),
        ("cue_sheet", "finance_visual_cue_sheet", "edit/word-timed-v1/finance-visual-cue-sheet.v1.json", True),
        ("edit_manifest", "finance_edit_manifest", "edit/word-timed-v1/finance-edit-manifest.v1.json", False),
        ("claim_ledger", "finance_claim_ledger", "claim-ledger.v1.json", True),
        ("asset_map", "asset_map", "edit/word-timed-v1/asset-map.v1.json", True),
        ("motion_plan", "editorial_motion_plan", "edit/word-timed-v1/editorial-motion-plan.v1.json", True),
        ("audio_manifest", "canonical_audio", "audio/canonical-audio.v1.json", True),
    ]
    artifacts: list[dict[str, Any]] = []
    payloads: dict[str, dict[str, Any]] = {}
    hashes: dict[str, str] = {}
    for artifact_id, kind, relative, required in specs:
        record, payload = _artifact_record(
            root,
            artifact_id,
            kind,
            relative,
            required=required,
            degraded=degraded,
        )
        if record and payload is not None:
            artifacts.append(record)
            payloads[artifact_id] = payload
            hashes[artifact_id] = record["sha256"]

    words_relative = str(payloads["audio_manifest"].get("words_path") or "")
    words_record, words_payload = _artifact_record(
        root,
        "words",
        "word_timing",
        words_relative,
        required=True,
        degraded=degraded,
    )
    assert words_record is not None and words_payload is not None
    artifacts.append(words_record)
    hashes["words"] = words_record["sha256"]

    catalog = Path(production_visual_catalog).resolve() if production_visual_catalog else None
    assets = _compile_project_assets(payloads["asset_map"], root, degraded)
    assets.extend(_compile_production_visuals(catalog, repository, degraded))

    approval_relative = "review/teacher-stamped-sheets/teacher-stamped-decks-approval.v1.json"
    approval_path = root / approval_relative
    reviews: list[dict[str, Any]] = []
    if approval_path.is_file():
        approval = _read_json(approval_path)
        reviews.append(
            {
                "review_id": "teacher-stamped-decks",
                "scope": str(approval.get("approval_scope") or "production_visuals"),
                "state": "approved" if approval.get("status") == "approved" else "unreviewed",
                "artifact_path": approval_relative,
                "sha256": _file_sha256(approval_path),
            }
        )
        evidence_approval = approval.get("evidence_approval", {})
        if isinstance(evidence_approval, Mapping):
            reviews.append(
                {
                    "review_id": "teacher-stamped-decks-factual-content",
                    "scope": "evidence",
                    "state": (
                        "approved"
                        if evidence_approval.get("status") == "approved"
                        else "unreviewed"
                    ),
                    "artifact_path": approval_relative,
                    "sha256": _file_sha256(approval_path),
                }
            )
    else:
        degraded.append(f"review: missing {approval_relative}")

    snapshot_core: dict[str, Any] = {
        "schema_version": SNAPSHOT_VERSION,
        "snapshot_id": f"{root.name}-v1",
        "project_id": str(payloads["scene_flow"].get("episode_id") or root.name),
        "composition_id": DEFAULT_COMPOSITION_ID,
        "base_artifact_hashes": dict(sorted(hashes.items())),
        "artifacts": sorted(artifacts, key=lambda item: item["artifact_id"]),
        "scenes": _compile_scenes(
            payloads["scene_flow"],
            payloads["scene_bundles"],
            payloads["motion_plan"],
            payloads["cue_sheet"],
        ),
        "words": _compile_words(words_payload),
        "assets": sorted(assets, key=lambda item: item["asset_id"]),
        "reviews": reviews,
        "degraded_inputs": sorted(set(degraded)),
    }
    snapshot = {**snapshot_core, "artifact_hash": _canonical_sha256(snapshot_core)}
    validated = validate_production_console_snapshot(snapshot)

    if output_path is not None:
        output = Path(output_path).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(validated, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, output)
    return validated


__all__ = [
    "ProductionConsoleSnapshotError",
    "compile_production_console_snapshot",
    "validate_production_console_snapshot",
]
