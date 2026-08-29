"""Deterministic P30 production-editor contracts and snapshot compiler.

The editor snapshot is a derived read model.  Canonical v1 artifacts remain the
source of truth; this module only projects them into frame-addressable tracks,
typed component metadata, and hash-bound evidence for the browser editor.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator

from content.video_engine.src.services.production_console_snapshot import (
    ProductionConsoleSnapshotError,
    compile_production_console_snapshot,
)
from content.video_engine.src.services.semantic_evidence_binding import (
    canonical_sha256 as _semantic_hash,
    compile_semantic_evidence_binding,
    load_plate_layout_profiles,
    validate_plate_layout_profile,
)


SNAPSHOT_V2_VERSION = "production_console_snapshot.v2"
TIMELINE_REVISION_VERSION = "editorial_timeline_revision.v1"
COMPONENT_CATALOG_VERSION = "editor_component_catalog.v1"
COMPONENT_PRESET_VERSION = "editor_component_preset.v1"
REMOTION_VERSION = "4.0.502"
REMOTION_BITS_VERSION = "0.2.0"
DEFAULT_FPS = 30
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_WAVEFORM_POINTS = 256
EDITOR_PLATE_KINDS = frozenset({"hero_plate", "generated_hero", "world_board", "mechanism"})
SENTENCE_NATIVE_PLATE_KIND = "sentence_native_plate"

TRACK_DEFINITIONS: tuple[tuple[str, str, str, bool], ...] = (
    ("track-scenes", "scenes", "Scenes", True),
    ("track-cues", "cues", "Cues", True),
    ("track-captions", "captions", "Captions", True),
    ("track-overlays", "overlays", "Overlays / annotations", True),
    ("track-teacher_stamp", "teacher_stamp", "Teacher stamp", True),
    ("track-evidence", "evidence", "Evidence", True),
    ("track-world_plates", "world_plates", "World plates", True),
    ("track-narration", "narration", "Narration", False),
)

_BIT_PROP_KEYS: dict[str, list[str]] = {
    "fade-in": ["text", "durationInFrames", "style", "color", "fontSize"],
    "blur-in": ["text", "durationInFrames", "style", "color", "fontSize", "blurAmount"],
    "word-by-word": ["text", "durationInFrames", "style", "color", "fontSize", "staggerFrames"],
    "slide-from-left": ["text", "durationInFrames", "style", "color", "fontSize", "distance"],
    "basic-typewriter": ["text", "style", "color", "fontSize", "typeSpeedFrames", "showCursor"],
    "basic-counter": [
        "from",
        "to",
        "prefix",
        "postfix",
        "decimals",
        "durationInFrames",
        "style",
        "color",
        "fontSize",
    ],
    "list-reveal": ["items", "staggerFrames", "durationInFrames", "style", "color", "fontSize", "backgroundColor"],
    "grid-stagger": ["items", "columns", "staggerFrames", "durationInFrames", "style", "color", "fontSize", "backgroundColor"],
    "mosaic-reframe": ["images", "assetMap", "tileCount", "style", "backgroundColor"],
    "3d-card-stack": ["cards", "staggerFrames", "durationInFrames", "style", "color", "fontSize", "backgroundColor"],
    "ken-burns-effect": ["images", "assetMap", "scaleFrom", "scaleTo", "direction", "durationInFrames", "style", "backgroundColor"],
}

_BIT_NAMES: dict[str, str] = {
    "fade-in": "Fade In",
    "blur-in": "Blur In",
    "word-by-word": "Word by Word",
    "slide-from-left": "Slide from Left",
    "basic-typewriter": "Basic Typewriter",
    "basic-counter": "Basic Counter",
    "list-reveal": "List Reveal",
    "grid-stagger": "Grid Stagger",
    "mosaic-reframe": "Mosaic Reframe",
    "3d-card-stack": "3D Card Stack",
    "ken-burns-effect": "Ken Burns Effect",
}

_BUILTIN_COMPONENTS: tuple[tuple[str, str, str, list[str]], ...] = (
    ("caption", "Captions", "caption", ["style_id", "font_size", "line_height", "color"]),
    ("text-overlay", "Text overlay", "text", ["style_id", "font_size", "line_height", "color", "background_color"]),
    ("annotation", "Annotation", "annotation", ["variant", "color", "stroke_color", "opacity"]),
    ("teacher-stamp", "Teacher stamp", "teacher_stamp", ["variant", "opacity", "x", "y", "scale", "rotation", "z"]),
    ("world-plate", "World plate", "world_plate", ["asset_role", "motion_recipe", "opacity", "x", "y", "scale", "rotation", "z"]),
    ("evidence-plate", "Evidence plate", "evidence_plate", ["asset_role", "motion_recipe", "opacity", "x", "y", "scale", "rotation", "z"]),
    ("shape", "Shape", "shape", ["variant", "background_color", "opacity", "x", "y", "scale", "rotation", "z"]),
    ("chart", "Chart", "chart", ["variant", "color", "background_color", "opacity", "x", "y", "scale", "rotation", "z"]),
)

_BUILTIN_COMPONENT_IDS = {item[0] for item in _BUILTIN_COMPONENTS}
_KNOWN_COMPONENT_IDS = _BUILTIN_COMPONENT_IDS | set(_BIT_PROP_KEYS)
_KNOWN_PROP_KEYS = {
    key
    for _, _, _, prop_keys in _BUILTIN_COMPONENTS
    for key in prop_keys
} | {key for prop_keys in _BIT_PROP_KEYS.values() for key in prop_keys}


class ProductionEditorError(ProductionConsoleSnapshotError):
    """Raised when an editor contract or canonical projection is unsafe."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductionEditorError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductionEditorError(f"JSON artifact must be an object: {path}")
    return value


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise ProductionEditorError(f"cannot hash artifact {path}: {exc}") from exc
    return digest.hexdigest()


def _canonical_hash(value: Mapping[str, Any], excluded: Iterable[str]) -> str:
    excluded_keys = set(excluded)
    core = {key: item for key, item in value.items() if key not in excluded_keys}
    encoded = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _schema_path(name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "configs" / name


def _validate_schema(payload: Mapping[str, Any], schema_name: str, label: str) -> dict[str, Any]:
    value = dict(payload)
    try:
        schema = _read_json(_schema_path(schema_name))
    except ProductionEditorError:
        raise
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        detail = "; ".join(
            f"{'/'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors[:8]
        )
        raise ProductionEditorError(f"{label} schema validation failed: {detail}")
    return value


def _write_json(payload: Mapping[str, Any], output_path: str | Path) -> None:
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)


def _safe_relative(path: Path, root: Path) -> str:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise ProductionEditorError(f"path escapes configured root: {path}") from exc
    return relative.as_posix()


def _path_from_declared(raw: str, *, project_root: Path, repository_root: Path) -> tuple[Path, str]:
    if not raw:
        raise ProductionEditorError("canonical audio path is missing")
    declared = Path(raw)
    if declared.is_absolute():
        absolute = declared.resolve()
        try:
            return absolute, _safe_relative(absolute, project_root)
        except ProductionEditorError:
            return absolute, _safe_relative(absolute, repository_root)
    if any(part in {"", ".", ".."} for part in declared.parts):
        raise ProductionEditorError(f"unsafe declared path: {raw}")
    absolute = (project_root / declared).resolve()
    return absolute, _safe_relative(absolute, project_root)


def _resolve_editor_media_path(
    raw: str,
    *,
    project_root: Path,
    repository_root: Path,
) -> tuple[Path, str, str] | None:
    """Resolve legacy episode- or project-relative media inside allowed roots."""

    if not raw:
        return None
    declared = Path(raw)
    if declared.is_absolute() or any(part in {"", ".", ".."} for part in declared.parts):
        return None
    project_family_root = project_root.parents[1]
    candidates = (project_root, project_family_root, repository_root)
    for base in candidates:
        candidate = (base / declared).resolve()
        try:
            relative = _safe_relative(candidate, project_root)
            path_root = "project"
        except ProductionEditorError:
            try:
                relative = _safe_relative(candidate, repository_root)
                path_root = "repository"
            except ProductionEditorError:
                continue
        if candidate.is_file():
            return candidate, path_root, relative
    return None


def _compile_editor_media_assets(
    asset_map: Mapping[str, Any],
    referenced_asset_ids: set[str],
    *,
    project_root: Path,
    repository_root: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    records = asset_map.get("assets", {})
    if not isinstance(records, Mapping):
        return [], ["editor_media: asset map has no asset records"]
    assets: list[dict[str, Any]] = []
    degraded: list[str] = []
    for asset_id in sorted(referenced_asset_ids):
        raw_record = records.get(asset_id)
        if not isinstance(raw_record, Mapping):
            degraded.append(f"editor_media: unknown plate asset {asset_id}")
            continue
        resolved = _resolve_editor_media_path(
            str(raw_record.get("path") or ""),
            project_root=project_root,
            repository_root=repository_root,
        )
        if resolved is None:
            degraded.append(f"editor_media: missing plate asset {asset_id}")
            continue
        absolute, path_root, relative = resolved
        expected_hash = str(raw_record.get("sha256") or "")
        actual_hash = _file_sha256(absolute)
        if expected_hash != actual_hash:
            degraded.append(f"editor_media: hash mismatch for plate asset {asset_id}")
            continue
        assets.append(
            {
                "asset_id": asset_id,
                "label": str(raw_record.get("label") or asset_id.replace("-", " ").title()),
                "path_root": path_root,
                "path": relative,
                "sha256": actual_hash,
                "source_kind": "project_asset",
                "approval_scope": "none",
                "evidence_eligible": bool(raw_record.get("evidence_eligible", False)),
                "rights_state": "review_only",
                "context_status": "operator_verified" if raw_record.get("human_promoted") else "review_only",
                "deck_id": None,
                "slide_number": None,
                "width": None,
                "height": None,
                "what_it_is": str(raw_record.get("kind") or "editorial world asset"),
                "claim_refs": [],
                "cue_refs": [],
            }
        )
    return assets, degraded


def _compile_sentence_native_plate_assets(
    *,
    project_root: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Expose composition-approved sentence-native plates without promoting evidence.

    The earlier waves live under ``assets/quarantine`` because they were
    produced and reviewed in batches, not because every accepted candidate was
    rejected. Only manifests explicitly approved for composition contribute a
    final composite plate. Their layered intermediates and rejected candidates
    remain unavailable to the editor.
    """

    root = project_root / "assets" / "quarantine"
    assets: list[dict[str, Any]] = []
    degraded: list[str] = []
    for manifest_path in sorted(root.glob("sentence-native-wave-*/wave-*-review-manifest.v1.json")):
        payload = _read_json(manifest_path)
        if payload.get("review_state") != "operator_approved_for_composition":
            continue
        candidates = payload.get("accepted_candidates", [])
        if not isinstance(candidates, list):
            degraded.append(f"sentence_native: malformed accepted candidates in {manifest_path.name}")
            continue
        for candidate in candidates:
            if not isinstance(candidate, Mapping):
                degraded.append(f"sentence_native: malformed candidate in {manifest_path.name}")
                continue
            filename = str(candidate.get("filename") or "")
            if not filename or Path(filename).name != filename or Path(filename).suffix.casefold() not in {".png", ".jpg", ".jpeg", ".webp"}:
                degraded.append(f"sentence_native: unsafe candidate filename in {manifest_path.name}")
                continue
            image_path = manifest_path.parent / filename
            if not image_path.is_file():
                degraded.append(f"sentence_native: missing approved plate {filename}")
                continue
            expected_hash = str(candidate.get("sha256") or "")
            actual_hash = _file_sha256(image_path)
            if expected_hash != actual_hash:
                degraded.append(f"sentence_native: hash mismatch for {filename}")
                continue
            asset_id = f"sentence-native-{image_path.stem}"
            label = image_path.stem.removeprefix("beat-").replace("-", " ").title()
            semantic_job = str(candidate.get("semantic_job") or "Sentence-native composition-approved world plate").strip()
            assets.append(
                {
                    "asset_id": asset_id,
                    "label": label,
                    "path_root": "project",
                    "path": _safe_relative(image_path, project_root),
                    "sha256": actual_hash,
                    "source_kind": "project_asset",
                    "approval_scope": "review_only",
                    "evidence_eligible": False,
                    "rights_state": "operator_authorized",
                    "context_status": "operator_verified",
                    "deck_id": None,
                    "slide_number": None,
                    "width": int(candidate["width"]) if candidate.get("width") else None,
                    "height": int(candidate["height"]) if candidate.get("height") else None,
                    "what_it_is": f"{SENTENCE_NATIVE_PLATE_KIND} · {semantic_job}",
                    "claim_refs": [],
                    "cue_refs": [],
                }
            )
    return assets, degraded


def _png_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        header = path.read_bytes()[:24]
    except OSError:
        return None, None
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def _compile_semantic_evidence_assets(
    approved_assets: Sequence[Mapping[str, Any]],
    *,
    project_root: Path,
    repository_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Promote context-preserving deck crops only when their parent slide is approved.

    The semantic crop stays hash-bound to its deck context manifest and inherits
    the operator's factual/rights approval from the corresponding full slide.
    """

    approved_slides = {
        (str(asset.get("deck_id") or ""), int(asset.get("slide_number") or 0)): asset
        for asset in approved_assets
        if asset.get("evidence_eligible") and asset.get("deck_id") and asset.get("slide_number")
    }
    project_family_root = project_root.parents[1]
    decks_root = project_family_root / "sources" / "decks"
    assets: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    degraded: list[str] = []
    for context_path in sorted(decks_root.glob("*/semantic-assets/asset-context.json")):
        payload = _read_json(context_path)
        deck_id = str(payload.get("deck_id") or "")
        artifacts.append(
            _artifact_record(
                context_path,
                artifact_id=f"semantic_asset_context_{deck_id}",
                kind="deck_semantic_asset_context",
                path_root="project_family",
                root=project_family_root,
            )
        )
        raw_assets = payload.get("assets", [])
        if not isinstance(raw_assets, list):
            degraded.append(f"semantic_evidence: malformed asset context for {deck_id}")
            continue
        for raw in raw_assets:
            if not isinstance(raw, Mapping):
                continue
            slide_number = int(raw.get("slide_number") or 0)
            parent = approved_slides.get((deck_id, slide_number))
            if parent is None:
                continue
            raw_path = str(raw.get("path") or "")
            declared = Path(raw_path)
            if not raw_path or declared.is_absolute() or any(part in {"", ".", ".."} for part in declared.parts):
                degraded.append(f"semantic_evidence: unsafe path for {raw.get('asset_id')}")
                continue
            absolute = (decks_root / declared).resolve()
            try:
                relative = _safe_relative(absolute, project_family_root)
            except ProductionEditorError:
                degraded.append(f"semantic_evidence: path escaped repository for {raw.get('asset_id')}")
                continue
            if not absolute.is_file():
                degraded.append(f"semantic_evidence: missing crop {raw.get('asset_id')}")
                continue
            actual_hash = _file_sha256(absolute)
            if actual_hash != str(raw.get("sha256") or ""):
                degraded.append(f"semantic_evidence: hash mismatch for {raw.get('asset_id')}")
                continue
            context = raw.get("context") if isinstance(raw.get("context"), Mapping) else {}
            width, height = _png_dimensions(absolute)
            asset_id = str(raw.get("asset_id") or "")
            if not asset_id:
                degraded.append(f"semantic_evidence: unnamed crop in {deck_id}")
                continue
            semantic_tail = asset_id.removeprefix(f"{deck_id}-s{slide_number:02d}-").removesuffix("-v1").replace("-", " ").title()
            assets.append(
                {
                    "asset_id": asset_id,
                    "label": f"{parent.get('label') or deck_id} · {semantic_tail}",
                    "path_root": "project_family",
                    "path": relative,
                    "sha256": actual_hash,
                    "source_kind": "evidence_surface",
                    "approval_scope": str(parent.get("approval_scope") or "production_visuals"),
                    "evidence_eligible": True,
                    "rights_state": str(parent.get("rights_state") or "operator_authorized"),
                    "context_status": "operator_verified",
                    "deck_id": deck_id,
                    "slide_number": slide_number,
                    "width": width,
                    "height": height,
                    "what_it_is": str(context.get("what_it_is") or "Approved semantic crop from a source deck"),
                    "claim_refs": _ordered_unique(context.get("claim_refs", [])),
                    "cue_refs": _ordered_unique(context.get("cue_refs", [])),
                }
            )
    return assets, artifacts, degraded


def _compile_semantic_recommendations(
    *,
    project_root: Path,
    repository_root: Path,
    snapshot_id: str,
    fps: int,
    cues: Sequence[Mapping[str, Any]],
    semantic_assets: Sequence[Mapping[str, Any]],
    beat_plan: Mapping[str, Any],
    claim_ledger: Mapping[str, Any],
    motion_plan: Mapping[str, Any],
    asset_map: Mapping[str, Any],
    base_artifact_hashes: Mapping[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Compile transparent recommendations only for reviewed active plates.

    The editor receives recommendations, never automatic insertions.  Candidate
    paths are rewritten to repository-relative paths before the semantic
    compiler performs containment and byte-hash checks.
    """

    profiles_path = _schema_path("plate_layout_profiles.v1.json")
    profile_collection = _read_json(profiles_path)
    profile_index = load_plate_layout_profiles(profiles_path)
    reviewed_world_ids = {
        str(profile.get("world_asset_id"))
        for profile in profile_index.values()
        if profile.get("status") == "reviewed" and profile.get("world_asset_id")
    }

    context_by_id: dict[str, Mapping[str, Any]] = {}
    decks_root = project_root.parents[1] / "sources" / "decks"
    for context_path in sorted(decks_root.glob("*/semantic-assets/asset-context.json")):
        payload = _read_json(context_path)
        for raw in payload.get("assets", []):
            if isinstance(raw, Mapping) and raw.get("asset_id"):
                context_by_id[str(raw["asset_id"])] = raw

    candidates: list[dict[str, Any]] = []
    approvals: list[dict[str, Any]] = []
    for asset in semantic_assets:
        asset_id = str(asset.get("asset_id") or "")
        raw = context_by_id.get(asset_id)
        if not asset_id or raw is None:
            continue
        root_by_kind = {
            "project": project_root,
            "project_family": project_root.parents[1],
            "repository": repository_root,
        }
        absolute = (root_by_kind[str(asset["path_root"])] / str(asset["path"])).resolve()
        try:
            repository_path = absolute.relative_to(repository_root).as_posix()
        except ValueError as exc:
            raise ProductionEditorError(f"semantic evidence path escaped repository: {asset_id}") from exc
        context = dict(raw.get("context") or {})
        context["context_status"] = "operator_verified"
        context.setdefault("visual_role", "evidence")
        context.setdefault("representation_mode", "literal_evidence")
        context.setdefault("factual_text", True)
        context.setdefault(
            "reuse_policy",
            {"scope": "scene", "max_total_uses": 1, "allowed_reasons": ["evidence_hold"], "claim_bound": True},
        )
        candidate = {
            **dict(raw),
            "asset_id": asset_id,
            "kind": "semantic_crop",
            "path": repository_path,
            "sha256": str(asset["sha256"]),
            "context": context,
            "rights_state": "approved",
            "review_state": "approved_reusable",
            "render_eligible": True,
        }
        candidates.append(candidate)
        approvals.append({"asset_id": asset_id, "status": "approved", "sha256": str(asset["sha256"])})

    beats = {
        str(beat.get("beat_id")): beat
        for beat in beat_plan.get("beats", [])
        if isinstance(beat, Mapping) and beat.get("beat_id")
    }
    shot_by_beat: dict[str, Mapping[str, Any]] = {}
    for shot in motion_plan.get("shots", []):
        if not isinstance(shot, Mapping):
            continue
        for beat_id in shot.get("parent_beat_ids", []):
            shot_by_beat[str(beat_id)] = shot
    raw_world_assets = asset_map.get("assets", {}) if isinstance(asset_map.get("assets"), Mapping) else {}
    snapshot_anchor_core = {
        "schema_version": SNAPSHOT_V2_VERSION,
        "snapshot_id": snapshot_id,
        "project_profile": {"fps": fps},
        "base_artifact_hashes": dict(sorted(base_artifact_hashes.items())),
    }
    snapshot_anchor = {**snapshot_anchor_core, "artifact_hash": _semantic_hash(snapshot_anchor_core)}
    occupied_by_profile: dict[str, list[str]] = {}
    bindings: list[dict[str, Any]] = []
    for cue in cues:
        cue_id = str(cue.get("cue_id") or "")
        beat_id = cue_id.replace("-cue-", "-beat-")
        shot = shot_by_beat.get(beat_id, {})
        world_id = next(
            (
                str(layer.get("asset_id"))
                for layer in shot.get("layers", [])
                if isinstance(layer, Mapping) and layer.get("asset_id") in reviewed_world_ids
            ),
            "",
        )
        if not world_id:
            continue
        world_record = raw_world_assets.get(world_id)
        if not isinstance(world_record, Mapping):
            continue
        world = {
            "asset_id": world_id,
            "sha256": str(world_record.get("sha256") or ""),
            "path": str(world_record.get("path") or ""),
            "what_it_is": str(world_record.get("kind") or "reviewed finance world plate"),
        }
        profile = profile_index[world_id]
        binding = compile_semantic_evidence_binding(
            cue,
            beats.get(beat_id, {}),
            claim_ledger,
            world,
            candidates,
            project_id=project_root.name,
            snapshot=snapshot_anchor,
            motion_plan=motion_plan,
            profiles=profile_index,
            asset_root=repository_root,
            world_root=project_root.parents[1],
            approval_ledger=approvals,
            occupied_slot_ids=occupied_by_profile.get(str(profile["profile_id"]), []),
            thresholds={"min_score": 24.0, "min_lead_margin": 1.5},
        )
        bindings.append(binding)
        proposed = binding.get("proposed_binding")
        if isinstance(proposed, Mapping) and proposed.get("slot_id"):
            occupied_by_profile.setdefault(str(profile["profile_id"]), []).append(str(proposed["slot_id"]))
    return profile_collection, bindings


def _apply_semantic_caption_layouts(
    tracks: Sequence[dict[str, Any]],
    bindings: Sequence[Mapping[str, Any]],
) -> None:
    """Place protected captions in the reviewed region selected with evidence."""

    layout_by_cue: dict[str, dict[str, float]] = {}
    for binding in bindings:
        proposed = binding.get("proposed_binding")
        if not isinstance(proposed, Mapping):
            continue
        caption_zone = proposed.get("caption_zone")
        rect = caption_zone.get("rect") if isinstance(caption_zone, Mapping) else None
        cue_id = binding.get("cue_id")
        if not isinstance(cue_id, str) or not isinstance(rect, Mapping):
            continue
        x = float(rect["x"])
        y = float(rect["y"])
        width = float(rect["width"])
        height = float(rect["height"])
        layout_by_cue[cue_id] = {
            "x": round(x + width / 2 - 0.5, 6),
            "y": round(y + height / 2 - 0.5, 6),
            "width": width,
            "height": height,
        }
    for track in tracks:
        if track.get("kind") != "captions":
            continue
        for item in track.get("items", []):
            cue_id = str(item.get("cue_id") or "")
            if cue_id in layout_by_cue:
                item["layout"] = dict(layout_by_cue[cue_id])


def _compile_teacher_stamp_asset(project_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    family_root = project_root.parents[1]
    relative = Path("assets/generated/host/teacher-stamp-watermark-fit-character-v4-center-gaze.png")
    absolute = (family_root / relative).resolve()
    if not absolute.is_file():
        return None, "editor_media: approved teacher stamp is not staged"
    return {
        "asset_id": "teacher-stamp-center-gaze-v4",
        "label": "Teacher stamp — center gaze",
        "path_root": "project_family",
        "path": relative.as_posix(),
        "sha256": _file_sha256(absolute),
        "source_kind": "project_asset",
        "approval_scope": "review_only",
        "evidence_eligible": False,
        "rights_state": "operator_authorized",
        "context_status": "operator_verified",
        "deck_id": None,
        "slide_number": None,
        "width": 128,
        "height": 96,
        "what_it_is": "Approved compact presenter stamp with center-facing gaze",
        "claim_refs": [],
        "cue_refs": [],
    }, None


def _compile_draw_hand_asset(project_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    relative = Path("finance-whiteboard-deck-asset-proof-v1/assets/draw-hand-a-v1.png")
    absolute = (project_root / relative).resolve()
    if not absolute.is_file():
        return None, "editor_media: whiteboard draw hand is not staged"
    return {
        "asset_id": "whiteboard-draw-hand-a-v1",
        "label": "Whiteboard marker hand — down stroke",
        "path_root": "project",
        "path": relative.as_posix(),
        "sha256": _file_sha256(absolute),
        "source_kind": "project_asset",
        "approval_scope": "review_only",
        "evidence_eligible": False,
        "rights_state": "operator_authorized",
        "context_status": "operator_verified",
        "deck_id": None,
        "slide_number": None,
        "width": 1024,
        "height": 1536,
        "what_it_is": "Photographed marker hand used only while an evidence card is being revealed",
        "claim_refs": [],
        "cue_refs": [],
    }, None


def _frame_value(seconds: float, fps: int) -> int:
    if not math.isfinite(seconds) or seconds < 0:
        raise ProductionEditorError(f"invalid source time: {seconds!r}")
    return int(math.floor(seconds * fps + 0.5))


def _duration_frames(duration_s: float, fps: int) -> int:
    value = math.ceil(duration_s * fps - 1e-9)
    return max(1, int(value))


def _frame_range(
    start_s: float,
    end_s: float,
    *,
    duration_s: float,
    duration_frames: int,
    fps: int,
) -> tuple[int, int]:
    if end_s < start_s:
        raise ProductionEditorError(f"source time range is reversed: {start_s}..{end_s}")
    start_frame = min(duration_frames, max(0, _frame_value(start_s, fps)))
    end_frame = min(duration_frames, max(0, _frame_value(end_s, fps)))
    if math.isclose(end_s, duration_s, rel_tol=0, abs_tol=1e-6):
        end_frame = duration_frames
    if end_s > start_s and end_frame <= start_frame:
        end_frame = min(duration_frames, start_frame + 1)
    return start_frame, end_frame


def _ordered_unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value))


def _component_catalog_core() -> dict[str, Any]:
    components: list[dict[str, Any]] = []
    presets: list[dict[str, Any]] = []
    for component_id, label, kind, prop_keys in _BUILTIN_COMPONENTS:
        preset_id = f"{component_id}-default"
        components.append(
            {
                "component_id": component_id,
                "label": label,
                "kind": kind,
                "adapter_id": f"builtin-{component_id}",
                "source": "builtin",
                "version": "1.0.0",
                "deterministic": True,
                "allowed_prop_keys": list(prop_keys),
                "preset_ids": [preset_id],
            }
        )
        presets.append(
            {
                "preset_id": preset_id,
                "component_id": component_id,
                "label": f"{label} default",
                "props": {"style_id": "default"},
            }
        )

    for component_id in _BIT_PROP_KEYS:
        preset_id = f"{component_id}-default"
        components.append(
            {
                "component_id": component_id,
                "label": _BIT_NAMES[component_id],
                "kind": "remotion_bit",
                "adapter_id": f"remotion-bits-{component_id}",
                "source": "remotion_bits",
                "version": REMOTION_BITS_VERSION,
                "package_name": "remotion-bits",
                "package_version": REMOTION_BITS_VERSION,
                "deterministic": True,
                "allowed_prop_keys": list(_BIT_PROP_KEYS[component_id]),
                "preset_ids": [preset_id],
            }
        )
        presets.append(
            {
                "preset_id": preset_id,
                "component_id": component_id,
                "label": f"{_BIT_NAMES[component_id]} default",
                "props": {"style_id": "remotion-bit-default"},
            }
        )

    return {
        "schema_version": COMPONENT_CATALOG_VERSION,
        "catalog_id": "production-editor-curated-v1",
        "catalog_version": "1.0.0",
        "remotion_version": REMOTION_VERSION,
        "components": sorted(components, key=lambda item: item["component_id"]),
        "presets": sorted(presets, key=lambda item: item["preset_id"]),
    }


def validate_editor_component_catalog(payload: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_schema(payload, "editor_component_catalog.schema.json", "component catalog")
    expected = _canonical_hash(value, {"catalog_hash", "artifact_hash"})
    if value.get("catalog_hash") != expected or value.get("artifact_hash") != expected:
        raise ProductionEditorError("component catalog hashes do not match canonical content")
    component_ids = [str(item["component_id"]) for item in value["components"]]
    if len(component_ids) != len(set(component_ids)):
        raise ProductionEditorError("component catalog contains duplicate component IDs")
    unknown_components = set(component_ids) - _KNOWN_COMPONENT_IDS
    if unknown_components:
        raise ProductionEditorError(
            f"component catalog contains unknown components: {sorted(unknown_components)}"
        )
    for component in value["components"]:
        component_id = str(component["component_id"])
        allowed_props = set(component["allowed_prop_keys"])
        if not allowed_props <= _KNOWN_PROP_KEYS:
            raise ProductionEditorError(f"component exposes unsupported props: {component_id}")
        if component_id in _BIT_PROP_KEYS:
            if component["kind"] != "remotion_bit" or component["source"] != "remotion_bits":
                raise ProductionEditorError(f"Remotion Bit component has invalid source metadata: {component_id}")
            if component.get("package_name") != "remotion-bits" or component.get("package_version") != REMOTION_BITS_VERSION:
                raise ProductionEditorError(f"Remotion Bit component is not pinned: {component_id}")
        elif component["source"] != "builtin":
            raise ProductionEditorError(f"builtin component has invalid source metadata: {component_id}")
    preset_ids = [str(item["preset_id"]) for item in value["presets"]]
    if len(preset_ids) != len(set(preset_ids)):
        raise ProductionEditorError("component catalog contains duplicate preset IDs")
    known_components = set(component_ids)
    for preset in value["presets"]:
        if preset["component_id"] not in known_components:
            raise ProductionEditorError(f"preset references unknown component: {preset['preset_id']}")
    return value


def validate_editor_component_preset(payload: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_schema(payload, "editor_component_preset.schema.json", "component preset")
    expected = _canonical_hash(value, {"artifact_hash"})
    if value.get("artifact_hash") != expected:
        raise ProductionEditorError("component preset artifact_hash does not match canonical content")
    if value["component_id"] not in _KNOWN_COMPONENT_IDS:
        raise ProductionEditorError(f"component preset references unknown component: {value['component_id']}")
    return value


def compile_editor_component_catalog(*, output_path: str | Path | None = None) -> dict[str, Any]:
    """Compile the closed, pinned component/preset catalog used by the editor."""

    core = _component_catalog_core()
    digest = _canonical_hash(core, {"catalog_hash", "artifact_hash"})
    catalog = {**core, "catalog_hash": digest, "artifact_hash": digest}
    validated = validate_editor_component_catalog(catalog)
    if output_path is not None:
        _write_json(validated, output_path)
    return validated


def _catalog_from_input(
    component_catalog: Mapping[str, Any] | str | Path | None,
    component_catalog_path: str | Path | None,
) -> dict[str, Any]:
    source: Mapping[str, Any] | None = None
    if component_catalog_path is not None:
        source = _read_json(Path(component_catalog_path).resolve())
    elif isinstance(component_catalog, (str, Path)):
        source = _read_json(Path(component_catalog).resolve())
    elif isinstance(component_catalog, Mapping):
        source = component_catalog
    if source is None:
        return compile_editor_component_catalog()
    return validate_editor_component_catalog(source)


def _default_visual_catalog(repository_root: Path) -> Path:
    return (
        repository_root
        / "content"
        / "video_engine"
        / "projects"
        / "systems-and-blowups"
        / "sources"
        / "decks"
        / "teacher-stamped-production-visuals"
        / "teacher-stamped-production-visuals-manifest.v1.json"
    )


def _artifact_record(path: Path, *, artifact_id: str, kind: str, path_root: str, root: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ProductionEditorError(f"required editor artifact is missing: {path}")
    return {
        "artifact_id": artifact_id,
        "kind": kind,
        "path_root": path_root,
        "path": _safe_relative(path, root),
        "sha256": _file_sha256(path),
        "status": "available",
        "degraded_reason": None,
    }


def _compile_words(
    words: Sequence[Mapping[str, Any]], *, duration_s: float, duration_frames: int, fps: int
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(words):
        start_s = float(raw.get("start_s", 0))
        end_s = float(raw.get("end_s", start_s))
        start_frame, end_frame = _frame_range(
            start_s,
            end_s,
            duration_s=duration_s,
            duration_frames=duration_frames,
            fps=fps,
        )
        result.append(
            {
                "word_id": f"word-{index:05d}",
                "text": str(raw.get("w", raw.get("text", ""))),
                "start_s": round(start_s, 6),
                "end_s": round(end_s, 6),
                "start_frame": start_frame,
                "end_frame": end_frame,
            }
        )
    return result


def _compile_cues(
    cues: Sequence[Mapping[str, Any]], *, duration_s: float, duration_frames: int, fps: int
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for raw in cues:
        cue_id = str(raw.get("cue_id") or "")
        if not cue_id:
            raise ProductionEditorError("cue is missing cue_id")
        start_s = float(raw.get("start_s", 0))
        end_s = float(raw.get("end_s", start_s))
        start_frame, end_frame = _frame_range(
            start_s,
            end_s,
            duration_s=duration_s,
            duration_frames=duration_frames,
            fps=fps,
        )
        micro_events: list[dict[str, Any]] = []
        for event in raw.get("micro_events", []):
            if not isinstance(event, Mapping):
                continue
            at_s = float(event.get("at_s", start_s))
            micro_events.append(
                {
                    "at_s": round(at_s, 6),
                    "frame": _frame_range(
                        at_s,
                        at_s,
                        duration_s=duration_s,
                        duration_frames=duration_frames,
                        fps=fps,
                    )[0],
                    "action": str(event.get("action") or ""),
                }
            )
        result.append(
            {
                "cue_id": cue_id,
                "start_word": int(raw.get("start_word", 0)),
                "end_word": int(raw.get("end_word", raw.get("start_word", 0))),
                "start_s": round(start_s, 6),
                "end_s": round(end_s, 6),
                "start_frame": start_frame,
                "end_frame": end_frame,
                "excerpt": str(raw.get("excerpt") or ""),
                "claim_refs": _ordered_unique(raw.get("claim_refs", [])),
                "state_type": str(raw.get("state_type") or "unknown"),
                "visual_world": str(raw.get("visual_world") or "unknown"),
                "entry_action": str(raw.get("entry_action") or "unspecified"),
                "exit_transition": str(raw.get("exit_transition") or "unspecified"),
                "fact_surface": raw.get("fact_surface") if isinstance(raw.get("fact_surface"), str) else None,
                "micro_events": micro_events,
                "short_membership": _ordered_unique(raw.get("short_membership", [])),
            }
        )
    return result


def _compile_scenes(
    scenes: Sequence[Mapping[str, Any]], *, duration_s: float, duration_frames: int, fps: int
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for raw in scenes:
        start_s = float(raw.get("start_s", 0))
        end_s = float(raw.get("end_s", start_s))
        start_frame, end_frame = _frame_range(
            start_s,
            end_s,
            duration_s=duration_s,
            duration_frames=duration_frames,
            fps=fps,
        )
        result.append(
            {
                **dict(raw),
                "start_s": round(start_s, 6),
                "end_s": round(end_s, 6),
                "start_frame": start_frame,
                "end_frame": end_frame,
            }
        )
    return result


def _overlay_track_items(
    overlay_map: Mapping[str, Any],
    *,
    cue_by_number: Mapping[str, Mapping[str, Any]],
    duration_s: float,
    duration_frames: int,
    fps: int,
) -> list[dict[str, Any]]:
    def percent(value: Any, fallback: float) -> float:
        if isinstance(value, str) and value.strip().endswith("%"):
            try:
                return float(value.strip()[:-1]) / 100
            except ValueError:
                return fallback
        return fallback

    items: list[dict[str, Any]] = []
    for overlay_id, raw in sorted(overlay_map.items(), key=lambda item: (str(item[1].get("from_s", 0)) if isinstance(item[1], Mapping) else "", str(item[0]))):
        if not isinstance(raw, Mapping):
            continue
        local_start_s = float(raw.get("from_s", 0))
        local_duration_s = float(raw.get("duration_s", 0))
        suffix = "".join(character for character in str(overlay_id) if character.isdigit())
        cue = cue_by_number.get(suffix[:3]) if suffix else None
        cue_id = str(cue["cue_id"]) if cue else None
        start_s = local_start_s + (float(cue["start_s"]) if cue else 0)
        end_s = start_s + local_duration_s
        if cue:
            end_s = min(end_s, float(cue["end_s"]))
        start_frame, end_frame = _frame_range(
            start_s,
            end_s,
            duration_s=duration_s,
            duration_frames=duration_frames,
            fps=fps,
        )
        style = raw.get("style")
        style_id = str(style.get("id")) if isinstance(style, Mapping) and style.get("id") else "overlay-default"
        if isinstance(style, Mapping):
            screen_width = min(0.72, max(0.08, percent(style.get("width"), 0.44)))
            screen_height = 0.14
            left = percent(style.get("left"), 0.5 - screen_width / 2)
            if style.get("left") in {None, "auto"} and isinstance(style.get("right"), str):
                left = 1 - percent(style.get("right"), 0.08) - screen_width
            top = percent(style.get("top"), 0.08)
            layout = {
                "x": round(left + screen_width / 2 - 0.5, 6),
                "y": round(top + screen_height / 2 - 0.5, 6),
                "width": round(screen_width / 0.72, 6),
                "height": round(screen_height / 0.66, 6),
            }
        elif raw.get("position") == "rail" or raw.get("kind") == "citation":
            layout = {"x": 0.0, "y": 0.44, "width": 0.9, "height": 0.1}
        else:
            layout = {"x": 0.0, "y": -0.34, "width": 0.72, "height": 0.18}
        is_citation = raw.get("kind") == "citation"
        item: dict[str, Any] = {
            "item_id": str(overlay_id),
            "item_type": "overlay",
            "overlay_kind": str(raw.get("kind")) if raw.get("kind") in {"text", "annotation", "shape", "arrow"} else ("annotation" if is_citation else "text"),
            "start_frame": start_frame,
            "end_frame": end_frame,
            "locked": False,
            "locked_fields": [],
            "source_ref": str(overlay_id),
            "style_id": style_id,
            "layout": layout,
        }
        if is_citation:
            citation_id = str(raw.get("citation_id") or "").strip()
            if not citation_id:
                raise ProductionEditorError(f"citation overlay {overlay_id} is missing citation_id")
            item.update(
                {
                    "citation_id": citation_id,
                    "diagnostic_label": str(raw.get("text") or citation_id),
                    "locked": True,
                    "locked_fields": ["text", "source_ref"],
                }
            )
        else:
            display_text = str(raw.get("display_text") or raw.get("text") or "").strip()
            if display_text:
                item["display_text"] = display_text
        if cue_id:
            item["cue_id"] = cue_id
        items.append(item)
    return items


def _compile_tracks(
    scenes: Sequence[Mapping[str, Any]],
    cues: Sequence[Mapping[str, Any]],
    words: Sequence[Mapping[str, Any]],
    motion_plan: Mapping[str, Any],
    overlay_map: Mapping[str, Any],
    asset_records: Sequence[Mapping[str, Any]],
    asset_map: Mapping[str, Any],
    *,
    duration_frames: int,
    duration_s: float,
    fps: int,
    approval_path: str | None,
    evidence_approval: bool,
    audio_id: str,
    audio_sha256: str,
    audio_path: str,
) -> list[dict[str, Any]]:
    scene_by_id = {str(scene["scene_id"]): scene for scene in scenes}
    cue_by_id = {str(cue["cue_id"]): cue for cue in cues}
    cue_by_number = {
        str(cue["cue_id"]).split("-")[-1]: cue
        for cue in cues
    }
    approved_ids = {
        str(asset["asset_id"])
        for asset in asset_records
        if asset.get("approval_scope") == "production_visuals"
        and asset.get("rights_state") in {"approved", "operator_authorized"}
    }
    raw_asset_records = asset_map.get("assets", {})
    asset_hashes = {
        str(asset_id): str(record.get("sha256"))
        for asset_id, record in raw_asset_records.items()
        if isinstance(record, Mapping) and record.get("sha256")
    }

    scene_items = [
        {
            "item_id": f"scene-item-{scene['scene_id']}",
            "item_type": "scene",
            "start_frame": scene["start_frame"],
            "end_frame": scene["end_frame"],
            "locked": False,
            "locked_fields": ["word_timing", "source_ref"],
            "source_ref": str(scene["scene_id"]),
            "scene_id": str(scene["scene_id"]),
        }
        for scene in scenes
    ]
    cue_items = [
        {
            "item_id": f"cue-item-{cue['cue_id']}",
            "item_type": "cue",
            "start_frame": cue["start_frame"],
            "end_frame": cue["end_frame"],
            "locked": False,
            "locked_fields": ["word_timing", "source_ref"],
            "source_ref": str(cue["cue_id"]),
            "cue_id": str(cue["cue_id"]),
            "start_word": cue["start_word"],
            "end_word": cue["end_word"],
            "excerpt": cue["excerpt"],
        }
        for cue in cues
    ]
    caption_items = [
        {
            "item_id": f"caption-item-{cue['cue_id']}",
            "item_type": "caption",
            "start_frame": cue["start_frame"],
            "end_frame": cue["end_frame"],
            "locked": False,
            "locked_fields": ["text", "word_timing"],
            "source_ref": str(cue["cue_id"]),
            "cue_id": str(cue["cue_id"]),
            "start_word": cue["start_word"],
            "end_word": cue["end_word"],
            "text": cue["excerpt"],
            "style_id": "default",
            "caption_preset": "compact",
        }
        for cue in cues
    ]
    overlay_items = _overlay_track_items(
        overlay_map,
        cue_by_number=cue_by_number,
        duration_s=duration_s,
        duration_frames=duration_frames,
        fps=fps,
    )

    world_items: list[dict[str, Any]] = []
    for shot in motion_plan.get("shots", []):
        if not isinstance(shot, Mapping):
            continue
        shot_id = str(shot.get("shot_id") or "")
        if not shot_id:
            continue
        shot_start = float(shot.get("start_s", 0))
        shot_end = shot_start + float(shot.get("duration_s", 0))
        start_frame, end_frame = _frame_range(
            shot_start,
            shot_end,
            duration_s=duration_s,
            duration_frames=duration_frames,
            fps=fps,
        )
        scene_id = str(shot.get("parent_scene_bundle_id") or "")
        cue_id = None
        for beat_id in shot.get("parent_beat_ids", []):
            candidate = str(beat_id).replace("-beat-", "-cue-")
            if candidate in cue_by_id:
                cue_id = candidate
                break
        for layer_index, layer in enumerate(shot.get("layers", [])):
            if not isinstance(layer, Mapping) or not layer.get("asset_id"):
                continue
            asset_id = str(layer["asset_id"])
            item: dict[str, Any] = {
                "item_id": f"world-item-{shot_id}-{layer_index + 1:02d}",
                "item_type": "world_plate",
                "start_frame": start_frame,
                "end_frame": end_frame,
                "locked": False,
                "locked_fields": ["asset_id", "asset_hash", "source_ref"],
                "source_ref": shot_id,
                "asset_id": asset_id,
                "component_id": "world-plate",
                "preset_id": "world-plate-default",
            }
            if scene_id in scene_by_id:
                item["scene_id"] = scene_id
            if cue_id:
                item["cue_id"] = cue_id
            if asset_id in asset_hashes:
                item["sha256"] = asset_hashes[asset_id]
            world_items.append(item)

    approval_item = {
        "item_id": "teacher-stamp-approval",
        "item_type": "teacher_stamp",
        "start_frame": 0,
        "end_frame": duration_frames,
        "locked": True,
        "locked_fields": ["approval", "source_ref"],
        "source_ref": approval_path or "approval-not-present",
    }
    evidence_item = {
        "item_id": "evidence-approval-rail",
        "item_type": "evidence",
        "start_frame": 0,
        "end_frame": duration_frames,
        "locked": True,
        "locked_fields": ["approval", "evidence_eligibility"],
        "source_ref": approval_path or "approval-not-present",
        "evidence_eligible": bool(evidence_approval and approved_ids),
    }
    narration_item = {
        "item_id": "narration-canonical",
        "item_type": "narration",
        "start_frame": 0,
        "end_frame": duration_frames,
        "locked": True,
        "locked_fields": ["audio_source", "word_timing"],
        "source_ref": audio_path,
        "asset_id": audio_id,
        "sha256": audio_sha256,
    }

    items_by_kind: dict[str, list[dict[str, Any]]] = {
        "scenes": scene_items,
        "cues": cue_items,
        "captions": caption_items,
        "overlays": overlay_items,
        "teacher_stamp": [approval_item],
        "evidence": [evidence_item],
        "world_plates": world_items,
        "narration": [narration_item],
    }
    return [
        {
            "track_id": track_id,
            "kind": kind,
            "label": label,
            "order": order,
            "editable": editable,
            "items": items_by_kind[kind],
        }
        for order, (track_id, kind, label, editable) in enumerate(TRACK_DEFINITIONS)
    ]


def _build_waveform(
    words: Sequence[Mapping[str, Any]],
    *,
    audio_sha256: str,
    duration_s: float,
    waveform_points: int,
    waveform_cache: Mapping[str, Any] | None = None,
    waveform_cache_path: str | Path | None = None,
) -> dict[str, Any]:
    cache = waveform_cache
    if cache is None and waveform_cache_path is not None:
        cache = _read_json(Path(waveform_cache_path).resolve())
    if cache is not None:
        cache_audio_hash = str(cache.get("audio_sha256") or cache.get("source_audio_sha256") or "")
        if cache_audio_hash != audio_sha256:
            raise ProductionEditorError("waveform cache is stale for canonical audio")
        raw_peaks = cache.get("peaks")
        if not isinstance(raw_peaks, list) or not raw_peaks:
            raise ProductionEditorError("waveform cache must contain non-empty peaks")
        peaks = [round(float(value), 6) for value in raw_peaks]
        if any(not math.isfinite(value) or value < 0 or value > 1 for value in peaks):
            raise ProductionEditorError("waveform cache peaks must be finite values in [0, 1]")
        sample_count = len(peaks)
        algorithm = "cached_peaks"
        status = "cached"
    else:
        sample_count = waveform_points
        bin_duration = duration_s / sample_count
        energy = [0.0] * sample_count
        for word in words:
            start_s = max(0.0, float(word.get("start_s", 0)))
            end_s = min(duration_s, max(start_s, float(word.get("end_s", start_s))))
            if end_s <= start_s:
                continue
            first = max(0, min(sample_count - 1, int(start_s / bin_duration)))
            last = max(0, min(sample_count - 1, int((end_s - 1e-9) / bin_duration)))
            for index in range(first, last + 1):
                left = index * bin_duration
                right = left + bin_duration
                energy[index] += max(0.0, min(end_s, right) - max(start_s, left))
        peaks = [round(min(1.0, value / bin_duration), 6) for value in energy]
        algorithm = "word_timing_envelope"
        status = "derived"
    cache_key = hashlib.sha256(f"waveform:{audio_sha256}:{sample_count}".encode("ascii")).hexdigest()
    return {
        "audio_sha256": audio_sha256,
        "source_audio_sha256": audio_sha256,
        "cache_key": cache_key,
        "sample_count": sample_count,
        "peaks": peaks,
        "algorithm": algorithm,
        "status": status,
    }


def validate_production_editor_snapshot(payload: Mapping[str, Any]) -> dict[str, Any]:
    value = _validate_schema(payload, "production_console_snapshot.v2.schema.json", "snapshot v2")
    expected = _canonical_hash(value, {"artifact_hash"})
    if value.get("artifact_hash") != expected:
        raise ProductionEditorError("snapshot v2 artifact_hash does not match canonical content")
    catalog = validate_editor_component_catalog(value["component_catalog"])
    if value.get("component_catalog_hash") != catalog["catalog_hash"]:
        raise ProductionEditorError("snapshot v2 component catalog hash does not match embedded catalog")
    profile_collection = _validate_schema(
        value["plate_layout_profiles"],
        "plate_layout_profiles.v1.schema.json",
        "plate layout profiles",
    )
    for profile in profile_collection["profiles"]:
        try:
            validate_plate_layout_profile(profile)
        except Exception as exc:
            raise ProductionEditorError(f"embedded plate layout profile is invalid: {exc}") from exc
    cue_ids = {str(cue["cue_id"]) for cue in value["cues"]}
    for binding in value["semantic_evidence_bindings"]:
        _validate_schema(binding, "semantic_evidence_binding.v1.schema.json", "semantic evidence binding")
        if binding["artifact_hash"] != _semantic_hash(binding):
            raise ProductionEditorError("semantic evidence binding artifact hash does not match canonical content")
        if str(binding["cue_id"]) not in cue_ids:
            raise ProductionEditorError("semantic evidence binding references an unknown cue")
    expected_tracks = [kind for _, kind, _, _ in TRACK_DEFINITIONS]
    actual_tracks = [str(track["kind"]) for track in value["tracks"]]
    if actual_tracks != expected_tracks:
        raise ProductionEditorError("snapshot v2 tracks do not match the fixed semantic track order")
    duration_frames = int(value["project_profile"]["duration_frames"])
    for collection_name in ("scenes", "cues", "words"):
        for item in value[collection_name]:
            if item["start_frame"] > item["end_frame"] or item["end_frame"] > duration_frames:
                raise ProductionEditorError(f"{collection_name} contains an out-of-bounds frame range")
    item_ids: set[str] = set()
    for track in value["tracks"]:
        for item in track["items"]:
            if item["item_id"] in item_ids:
                raise ProductionEditorError(f"duplicate timeline item ID: {item['item_id']}")
            item_ids.add(item["item_id"])
            if not 0 <= item["start_frame"] < item["end_frame"] <= duration_frames:
                raise ProductionEditorError(f"timeline item is outside the project frame range: {item['item_id']}")
            if item.get("citation_id"):
                if item.get("item_type") != "overlay" or item.get("overlay_kind") != "annotation":
                    raise ProductionEditorError("citation metadata is only valid on annotation overlays")
                if item.get("display_text") or item.get("text"):
                    raise ProductionEditorError("citation metadata cannot enter normal display text")
                if not item.get("diagnostic_label"):
                    raise ProductionEditorError("citation metadata requires an explicit diagnostic label")
            display_text = item.get("display_text")
            if display_text and display_text in {
                item.get("item_id"),
                item.get("source_ref"),
                item.get("citation_id"),
                item.get("asset_id"),
            }:
                raise ProductionEditorError("protected identifier cannot be used as generated display text")
    waveform = value["waveform"]
    if waveform["sample_count"] != len(waveform["peaks"]):
        raise ProductionEditorError("waveform sample_count does not match peaks")
    if waveform["audio_sha256"] != value["project_profile"]["audio"]["sha256"]:
        raise ProductionEditorError("waveform is not bound to the canonical audio hash")
    return value


def compile_production_editor_snapshot(
    project_root: str | Path,
    *,
    repository_root: str | Path | None = None,
    production_visual_catalog: str | Path | None = None,
    component_catalog: Mapping[str, Any] | str | Path | None = None,
    component_catalog_path: str | Path | None = None,
    fps: int = DEFAULT_FPS,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    profile_id: str = "landscape-final-v1",
    audio_trim: Mapping[str, Any] | None = None,
    waveform_cache: Mapping[str, Any] | None = None,
    waveform_cache_path: str | Path | None = None,
    waveform_points: int = DEFAULT_WAVEFORM_POINTS,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compile the P30 snapshot without changing any canonical or v1 artifact."""

    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ProductionEditorError(f"project root does not exist: {root}")
    repository = Path(repository_root).resolve() if repository_root else Path(__file__).resolve().parents[4]
    if not repository.is_dir():
        raise ProductionEditorError(f"repository root does not exist: {repository}")
    if not isinstance(fps, int) or not 1 <= fps <= 240:
        raise ProductionEditorError("fps must be an integer in [1, 240]")
    if not isinstance(width, int) or not 1 <= width <= 16384:
        raise ProductionEditorError("width must be an integer in [1, 16384]")
    if not isinstance(height, int) or not 1 <= height <= 16384:
        raise ProductionEditorError("height must be an integer in [1, 16384]")
    if not isinstance(waveform_points, int) or not 1 <= waveform_points <= 8192:
        raise ProductionEditorError("waveform_points must be an integer in [1, 8192]")

    visual_catalog = Path(production_visual_catalog).resolve() if production_visual_catalog else _default_visual_catalog(repository)
    visual_catalog_arg: str | Path | None = visual_catalog if visual_catalog.is_file() else None
    v1_snapshot = compile_production_console_snapshot(
        root,
        repository_root=repository,
        production_visual_catalog=visual_catalog_arg,
    )

    relative_paths = {
        "cue_sheet": "edit/word-timed-v1/finance-visual-cue-sheet.v1.json",
        "motion_plan": "edit/word-timed-v1/editorial-motion-plan.v1.json",
        "beat_plan": "edit/word-timed-v1/editorial-beat-plan.v1.json",
        "overlay_map": "edit/word-timed-v1/overlay-map.v1.json",
        "audio_manifest": "audio/canonical-audio.v1.json",
        "asset_map": "edit/word-timed-v1/asset-map.v1.json",
        "claim_ledger": "claim-ledger.v1.json",
    }
    payloads = {key: _read_json(root / relative) for key, relative in relative_paths.items()}
    audio_manifest = payloads["audio_manifest"]
    duration_s = float(audio_manifest.get("duration_s") or payloads["motion_plan"].get("duration_s") or 0)
    if duration_s <= 0:
        raise ProductionEditorError("canonical audio duration must be positive")
    duration_frames = _duration_frames(duration_s, fps)

    trim = audio_trim or {}
    if not isinstance(trim, Mapping):
        raise ProductionEditorError("audio_trim must be an object")
    trim_start_s = float(trim["start_s"]) if "start_s" in trim else float(trim.get("start_frame", 0)) / fps
    trim_end_s = float(trim["end_s"]) if "end_s" in trim else (
        float(trim["end_frame"]) / fps if "end_frame" in trim else duration_s
    )
    if trim_start_s < 0 or trim_end_s <= trim_start_s or trim_end_s > duration_s + 1e-6:
        raise ProductionEditorError("audio trim must be contained by canonical narration")
    trim_start_frame, trim_end_frame = _frame_range(
        trim_start_s,
        trim_end_s,
        duration_s=duration_s,
        duration_frames=duration_frames,
        fps=fps,
    )
    if trim_end_frame <= trim_start_frame:
        raise ProductionEditorError("audio trim must span at least one frame")

    audio_path_absolute, audio_path = _path_from_declared(
        str(audio_manifest.get("audio_path") or ""),
        project_root=root,
        repository_root=repository,
    )
    audio_sha256 = str(audio_manifest.get("audio_sha256") or "")
    if len(audio_sha256) != 64:
        raise ProductionEditorError("canonical audio manifest is missing a sha256")
    degraded = list(v1_snapshot.get("degraded_inputs", []))
    if not audio_path_absolute.is_file():
        degraded.append(f"audio_media: missing {audio_path}")

    artifacts: list[dict[str, Any]] = []
    for artifact in v1_snapshot["artifacts"]:
        artifacts.append({**dict(artifact), "path_root": "project"})
    base_hashes = dict(v1_snapshot["base_artifact_hashes"])

    approval_relative = "review/teacher-stamped-sheets/teacher-stamped-decks-approval.v1.json"
    approval_path = root / approval_relative
    approval_record: dict[str, Any] | None = None
    evidence_approval = False
    approval_payload: dict[str, Any] | None = None
    if approval_path.is_file():
        approval_payload = _read_json(approval_path)
        approval_record = _artifact_record(
            approval_path,
            artifact_id="teacher_stamped_approval",
            kind="teacher_stamped_approval",
            path_root="project",
            root=root,
        )
        evidence = approval_payload.get("evidence_approval")
        evidence_approval = isinstance(evidence, Mapping) and evidence.get("status") == "approved"
        base_hashes["teacher_stamped_approval"] = approval_record["sha256"]
    else:
        degraded.append(f"review: missing {approval_relative}")

    catalog_record: dict[str, Any] | None = None
    if visual_catalog.is_file():
        catalog_record = _artifact_record(
            visual_catalog,
            artifact_id="production_visual_catalog",
            kind="teacher_stamped_visual_catalog",
            path_root="repository",
            root=repository,
        )
        base_hashes["production_visual_catalog"] = catalog_record["sha256"]
    elif production_visual_catalog is not None:
        degraded.append(f"production_visuals: missing {visual_catalog.as_posix()}")
    if approval_record:
        artifacts.append(approval_record)
    if catalog_record:
        artifacts.append(catalog_record)
    artifacts.sort(key=lambda item: item["artifact_id"])

    words_path_absolute, _ = _path_from_declared(
        str(audio_manifest.get("words_path") or ""),
        project_root=root,
        repository_root=repository,
    )
    word_payload = _read_json(words_path_absolute)
    words = _compile_words(
        [item for item in word_payload.get("words", []) if isinstance(item, Mapping)],
        duration_s=duration_s,
        duration_frames=duration_frames,
        fps=fps,
    )
    scenes = _compile_scenes(
        [item for item in v1_snapshot["scenes"] if isinstance(item, Mapping)],
        duration_s=duration_s,
        duration_frames=duration_frames,
        fps=fps,
    )
    cues = _compile_cues(
        [item for item in payloads["cue_sheet"].get("cues", []) if isinstance(item, Mapping)],
        duration_s=duration_s,
        duration_frames=duration_frames,
        fps=fps,
    )
    assets = [dict(asset) for asset in v1_snapshot["assets"]]
    approved_assets = [
        dict(asset)
        for asset in assets
        if asset.get("approval_scope") == "production_visuals"
        and asset.get("rights_state") in {"operator_authorized", "approved"}
        and asset.get("context_status") == "operator_verified"
    ]
    semantic_assets, semantic_artifacts, semantic_degraded = _compile_semantic_evidence_assets(
        approved_assets,
        project_root=root,
        repository_root=repository,
    )
    known_asset_ids = {str(asset["asset_id"]) for asset in assets}
    assets.extend(asset for asset in semantic_assets if asset["asset_id"] not in known_asset_ids)
    approved_assets.extend(
        asset for asset in semantic_assets if asset["asset_id"] not in {str(item["asset_id"]) for item in approved_assets}
    )
    artifacts.extend(semantic_artifacts)
    degraded.extend(semantic_degraded)
    for artifact in semantic_artifacts:
        base_hashes[str(artifact["artifact_id"])] = str(artifact["sha256"])
    artifacts.sort(key=lambda item: item["artifact_id"])
    catalog = _catalog_from_input(component_catalog, component_catalog_path)
    tracks = _compile_tracks(
        scenes,
        cues,
        words,
        payloads["motion_plan"],
        payloads["overlay_map"],
        assets,
        payloads["asset_map"],
        duration_frames=duration_frames,
        duration_s=duration_s,
        fps=fps,
        approval_path=approval_relative if approval_record else None,
        evidence_approval=evidence_approval,
        audio_id="canonical-narration",
        audio_sha256=audio_sha256,
        audio_path=audio_path,
    )
    referenced_world_asset_ids = {
        str(item["asset_id"])
        for track in tracks
        if track.get("kind") == "world_plates"
        for item in track.get("items", [])
        if isinstance(item, Mapping) and item.get("asset_id")
    }
    referenced_world_asset_ids.update(
        str(profile["world_asset_id"])
        for profile in load_plate_layout_profiles().values()
        if profile.get("status") == "reviewed" and profile.get("world_asset_id")
    )
    raw_asset_records = payloads["asset_map"].get("assets", {})
    if not isinstance(raw_asset_records, Mapping):
        raise ProductionEditorError("asset map assets must be an object")
    # The editor needs the complete reviewed plate library, not only the
    # handful of plates currently selected by the motion plan or a slot
    # profile. These remain visual-only project assets; this does not promote
    # them into approved factual evidence.
    referenced_world_asset_ids.update(
        str(asset_id)
        for asset_id, record in raw_asset_records.items()
        if isinstance(record, Mapping)
        and record.get("render_eligible") is True
        and str(record.get("kind") or "") in EDITOR_PLATE_KINDS
    )
    editor_media_assets, editor_media_degraded = _compile_editor_media_assets(
        payloads["asset_map"],
        referenced_world_asset_ids,
        project_root=root,
        repository_root=repository,
    )
    known_asset_ids = {str(asset["asset_id"]) for asset in assets}
    assets.extend(asset for asset in editor_media_assets if asset["asset_id"] not in known_asset_ids)
    degraded.extend(editor_media_degraded)
    known_asset_ids = {str(asset["asset_id"]) for asset in assets}
    sentence_native_assets, sentence_native_degraded = _compile_sentence_native_plate_assets(project_root=root)
    assets.extend(asset for asset in sentence_native_assets if asset["asset_id"] not in known_asset_ids)
    degraded.extend(sentence_native_degraded)
    teacher_stamp_asset, teacher_stamp_degraded = _compile_teacher_stamp_asset(root)
    if teacher_stamp_asset and teacher_stamp_asset["asset_id"] not in known_asset_ids:
        assets.append(teacher_stamp_asset)
    if teacher_stamp_degraded:
        degraded.append(teacher_stamp_degraded)
    draw_hand_asset, draw_hand_degraded = _compile_draw_hand_asset(root)
    if draw_hand_asset and draw_hand_asset["asset_id"] not in {str(asset["asset_id"]) for asset in assets}:
        assets.append(draw_hand_asset)
    if draw_hand_degraded:
        degraded.append(draw_hand_degraded)
    waveform = _build_waveform(
        words,
        audio_sha256=audio_sha256,
        duration_s=duration_s,
        waveform_points=waveform_points,
        waveform_cache=waveform_cache,
        waveform_cache_path=waveform_cache_path,
    )
    profile_collection, semantic_bindings = _compile_semantic_recommendations(
        project_root=root,
        repository_root=repository,
        snapshot_id=f"{root.name}-v2",
        fps=fps,
        cues=cues,
        semantic_assets=semantic_assets,
        beat_plan=payloads["beat_plan"],
        claim_ledger=payloads["claim_ledger"],
        motion_plan=payloads["motion_plan"],
        asset_map=payloads["asset_map"],
        base_artifact_hashes=base_hashes,
    )
    _apply_semantic_caption_layouts(tracks, semantic_bindings)

    snapshot_core: dict[str, Any] = {
        "schema_version": SNAPSHOT_V2_VERSION,
        "snapshot_id": f"{root.name}-v2",
        "project_id": str(v1_snapshot["project_id"]),
        "composition_id": str(v1_snapshot["composition_id"]),
        "project_profile": {
            "profile_id": profile_id,
            "fps": fps,
            "width": width,
            "height": height,
            "duration_s": round(duration_s, 6),
            "duration_frames": duration_frames,
            "audio": {
                "audio_id": "canonical-narration",
                "path": audio_path,
                "sha256": audio_sha256,
                "duration_s": round(duration_s, 6),
                "status": "available" if audio_path_absolute.is_file() else "missing",
            },
            "audio_trim": {
                "start_s": round(trim_start_s, 6),
                "end_s": round(trim_end_s, 6),
                "start_frame": trim_start_frame,
                "end_frame": trim_end_frame,
            },
        },
        "base_artifact_hashes": dict(sorted(base_hashes.items())),
        "artifacts": artifacts,
        "scenes": scenes,
        "cues": cues,
        "words": words,
        "tracks": tracks,
        "assets": sorted(assets, key=lambda item: item["asset_id"]),
        "approved_assets": sorted(approved_assets, key=lambda item: item["asset_id"]),
        "reviews": [dict(review) for review in v1_snapshot["reviews"]],
        "locks": {
            "narration": True,
            "transcript": True,
            "word_timing": True,
            "canonical_audio": True,
            "source_artifacts": True,
            "approved_assets": True,
            "evidence_eligibility": True,
        },
        "waveform": waveform,
        "component_catalog": catalog,
        "component_catalog_hash": catalog["catalog_hash"],
        "plate_layout_profiles": profile_collection,
        "semantic_evidence_bindings": semantic_bindings,
        "degraded_inputs": sorted(set(degraded)),
    }
    snapshot = {**snapshot_core, "artifact_hash": _canonical_hash(snapshot_core, {"artifact_hash"})}
    validated = validate_production_editor_snapshot(snapshot)
    if output_path is not None:
        _write_json(validated, output_path)
    return validated


# Explicit aliases make the versioned boundary easy for callers while keeping
# the descriptive compiler name used by the P30 service layer.
compile_production_console_snapshot_v2 = compile_production_editor_snapshot
validate_production_console_snapshot_v2 = validate_production_editor_snapshot
compile_production_editor_catalog = compile_editor_component_catalog


__all__ = [
    "COMPONENT_CATALOG_VERSION",
    "ProductionEditorError",
    "compile_editor_component_catalog",
    "compile_production_editor_catalog",
    "compile_production_console_snapshot_v2",
    "compile_production_editor_snapshot",
    "validate_editor_component_catalog",
    "validate_editor_component_preset",
    "validate_production_console_snapshot_v2",
    "validate_production_editor_snapshot",
]
