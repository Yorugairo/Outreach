"""Hash-bound adapter for the Martial Matters editorial handoff.

The handoff package is intentionally not a renderer manifest.  This adapter
copies the already-authored candidate files into a named revision, preserves
the cue-sheet clock, and emits the existing editorial-motion contract.  No
provider is contacted and no source-package flag is changed.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import shutil
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.editorial_motion import (
    EditorialMotionError,
    _normalized_tokens,
    build_default_pacing_recipe,
    compile_timestamped_editorial_motion_plan,
    derive_editorial_motion_sample,
    validate_editorial_pacing_recipe,
)
from content.video_engine.src.services.generated_block_images import (
    GeneratedBlockImageError,
    validate_timestamped_plate_plan,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


MARTIAL_ADAPTER_MANIFEST_VERSION = "martial_editorial_adapter_manifest.v1"
EDITORIAL_REVIEW_AUTHORIZATION_VERSION = "editorial_review_authorization.v1"
_HASH_RE = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_REMOTE_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_REPO_ROOT = Path(__file__).resolve().parents[4]
_ENGINE_ROOT = _REPO_ROOT / "content" / "video_engine"
_CANONICAL_DURATION_S = 567.804
_CANONICAL_CUE_COUNT = 192
_CANONICAL_WORD_COUNT = 1528
_EPSILON = 1e-4
_CAPTION_EPSILON = 1e-2


class MartialEditorialAdapterError(ValueError):
    """Raised when a Martial handoff cannot be compiled safely."""

    def __init__(self, errors: Sequence[str] | str) -> None:
        self.errors = [str(errors)] if isinstance(errors, str) else list(errors)
        super().__init__("; ".join(self.errors))


def _load(value: Mapping[str, Any] | str | Path | None, label: str) -> dict[str, Any]:
    if value is None:
        raise MartialEditorialAdapterError(f"{label} is required")
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MartialEditorialAdapterError(f"{label} could not be read: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise MartialEditorialAdapterError(f"{label} must be an object")
    return copy.deepcopy(dict(payload))


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _without_hash(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in payload.items() if key != "artifact_hash"}


def _artifact_hash(payload: Mapping[str, Any], label: str) -> str:
    declared = str(payload.get("artifact_hash") or "").casefold()
    actual = canonical_sha256(_without_hash(payload))
    if not _HASH_RE.fullmatch(declared):
        raise MartialEditorialAdapterError(f"{label} is missing a valid artifact_hash")
    if declared != actual:
        raise MartialEditorialAdapterError(f"{label} artifact_hash is stale")
    return declared


def _schema_errors(payload: Mapping[str, Any], schema_name: str) -> list[str]:
    try:
        schema = json.loads(( _ENGINE_ROOT / "configs" / schema_name).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"unable to load {schema_name}: {exc}"]
    return [
        f"{'.'.join(str(item) for item in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(
            Draft7Validator(schema).iter_errors(payload),
            key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
        )
    ]


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _relative_path(raw: Any, root: Path, label: str) -> Path:
    text = str(raw or "").strip().replace("\\", "/")
    if not text:
        raise MartialEditorialAdapterError(f"{label} is empty")
    if "\x00" in text or _REMOTE_RE.match(text) or text.startswith("//"):
        raise MartialEditorialAdapterError(f"{label} must be a local relative path")
    candidate = Path(text)
    if candidate.is_absolute() or re.match(r"^[A-Za-z]:", text):
        raise MartialEditorialAdapterError(f"{label} must be a local relative path")
    resolved = (root / candidate).resolve()
    if not _inside(resolved, root):
        raise MartialEditorialAdapterError(f"{label} escapes its approved root")
    if any(part in {".", ".."} for part in candidate.parts):
        raise MartialEditorialAdapterError(f"{label} may not contain dot segments")
    if ":" in candidate.name:
        raise MartialEditorialAdapterError(f"{label} may not use an alternate data stream")
    return resolved


def _input_path(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise MartialEditorialAdapterError(f"{label} does not exist: {path}")
    return path


def _episode_root(edit_package: str | Path | None, project_root: Path) -> Path:
    if edit_package is not None and not isinstance(edit_package, Mapping):
        path = Path(edit_package).expanduser().resolve()
        for ancestor in (path.parent, *path.parents):
            if (ancestor / "audio").is_dir() and (ancestor / "continuity").is_dir():
                return ancestor
    return project_root


def _default_inputs(
    edit_package: Mapping[str, Any] | str | Path,
    *,
    project_root: Path,
) -> dict[str, Path]:
    if isinstance(edit_package, Mapping):
        raise MartialEditorialAdapterError(
            "cue_sheet, audio_manifest, word_timings, and caption paths are required when edit_package is a mapping"
        )
    package_path = Path(edit_package).expanduser().resolve()
    episode = _episode_root(package_path, project_root)
    revision_name = package_path.parent.name
    return {
        "cue_sheet": episode / "continuity" / "revisions" / revision_name / "word-timed-visual-cues-r1.v1.json",
        "audio_manifest": episode / "audio" / "revisions" / revision_name / "marshall-monday-001-canonical-audio-r1.v1.json",
        "word_timings": episode / "audio" / "revisions" / revision_name / "marshall-monday-001-master-r1.words.json",
        "caption_plan": episode / "edit" / "revisions" / revision_name / "captions" / "marshall-monday-001-dynamic-captions.v1.json",
        "caption_output": episode / "edit" / "revisions" / revision_name / "captions" / "marshall-monday-001-anchor.en-US.srt",
    }


def _resolve_source_path(
    raw: Any,
    *,
    project_root: Path,
    episode_root: Path,
    label: str,
) -> Path:
    text = str(raw or "").strip().replace("\\", "/")
    if not text:
        raise MartialEditorialAdapterError(f"{label} is empty")
    candidates: list[Path] = []
    if not Path(text).is_absolute() and not re.match(r"^[A-Za-z]:", text):
        for root in (project_root, episode_root):
            try:
                candidate = _relative_path(text, root, label)
            except MartialEditorialAdapterError:
                continue
            if candidate not in candidates:
                candidates.append(candidate)
    else:
        raise MartialEditorialAdapterError(f"{label} must be project-relative")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise MartialEditorialAdapterError(f"{label} does not resolve to a file")


def _same_number(first: Any, second: Any, *, label: str) -> None:
    try:
        if not math.isclose(float(first), float(second), abs_tol=_EPSILON):
            raise MartialEditorialAdapterError(f"{label} does not match")
    except (TypeError, ValueError) as exc:
        raise MartialEditorialAdapterError(f"{label} is not numeric") from exc


def _safe_revision_id(value: str) -> str:
    revision_id = str(value or "").strip().casefold()
    if _SAFE_ID_RE.fullmatch(revision_id) is None:
        raise MartialEditorialAdapterError("revision_id must be a safe lowercase ID")
    return revision_id


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise MartialEditorialAdapterError(f"existing artifact is unreadable: {path}") from exc
        if existing != payload:
            raise MartialEditorialAdapterError(f"immutable artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded, encoding="utf-8", newline="\n")


def _copy_immutable(source: Path, destination: Path, *, expected_sha: str, label: str) -> None:
    if _hash_file(source) != expected_sha:
        raise MartialEditorialAdapterError(f"{label} source hash is stale")
    if destination.exists():
        if not destination.is_file() or _hash_file(destination) != expected_sha:
            raise MartialEditorialAdapterError(f"immutable staged file differs: {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if _hash_file(destination) != expected_sha:
        raise MartialEditorialAdapterError(f"{label} staged hash is stale")


def _caption_overlay_map(caption_payload: Mapping[str, Any], *, duration_s: float) -> dict[str, dict[str, Any]]:
    captions = caption_payload.get("captions")
    if not isinstance(captions, Sequence) or isinstance(captions, (str, bytes, bytearray)):
        raise MartialEditorialAdapterError("caption plan requires a captions array")
    overlays: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(captions):
        if not isinstance(raw, Mapping):
            raise MartialEditorialAdapterError(f"caption plan captions[{index}] must be an object")
        caption_id = str(raw.get("id") or "")
        if _SAFE_ID_RE.fullmatch(caption_id) is None or caption_id in overlays:
            raise MartialEditorialAdapterError(f"caption plan captions[{index}] has an invalid or duplicate id")
        try:
            start_s = float(raw["start_s"])
            end_s = float(raw["end_s"])
        except (KeyError, TypeError, ValueError) as exc:
            raise MartialEditorialAdapterError(f"caption plan captions[{index}] has invalid timing") from exc
        if start_s < -_EPSILON or end_s <= start_s or end_s > duration_s + _CAPTION_EPSILON:
            raise MartialEditorialAdapterError(f"caption plan captions[{index}] escapes the audio duration")
        end_s = min(end_s, duration_s)
        overlays[caption_id] = {
            "kind": "caption",
            "text": str(raw.get("text") or ""),
            "emphasis": str(raw.get("emphasis") or ""),
            "from_s": round(max(0.0, start_s), 6),
            "start_s": round(max(0.0, start_s), 6),
            "duration_s": round(end_s - start_s, 6),
            "end_s": round(end_s, 6),
            "position": "bottom",
        }
    return overlays


def _function_for_cue(primary_class: str) -> str:
    return {
        "evidence": "document_quote_closeup",
        "journey": "migration_map_timeline",
        "academic": "lineage_graph",
        "martial": "concept_mechanics_cutaway",
        "scenic": "artifact_cold_open",
        "transition": "concept_mechanics_cutaway",
        "narrative": "artifact_cold_open",
    }.get(primary_class.casefold(), "concept_mechanics_cutaway")


def _validate_source_contracts(
    *,
    package: Mapping[str, Any],
    cues_payload: Mapping[str, Any],
    audio: Mapping[str, Any],
    words_payload: Mapping[str, Any],
    authorization: Mapping[str, Any],
    package_hash: str,
    cue_hash: str,
    audio_manifest_hash: str,
    word_sha: str,
    episode_root: Path,
    project_root: Path,
) -> tuple[list[dict[str, Any]], list[Path]]:
    errors: list[str] = []
    if package.get("schema_version") != "marshall_monday_edit_package.v1":
        errors.append("edit package schema_version is not marshall_monday_edit_package.v1")
    if cues_payload.get("schema_version") != "word_timed_visual_cues.v1":
        errors.append("cue sheet schema_version is not word_timed_visual_cues.v1")
    if audio.get("schema_version") != "elevenlabs_canonical_audio.v1":
        errors.append("audio manifest schema_version is not elevenlabs_canonical_audio.v1")
    if audio.get("status") != "ready":
        errors.append("canonical audio is not ready")
    if authorization.get("schema_version") != EDITORIAL_REVIEW_AUTHORIZATION_VERSION:
        errors.append("authorization schema_version is not editorial_review_authorization.v1")
    if authorization.get("scope") != "internal_revision_render_only":
        errors.append("authorization scope must be internal_revision_render_only")
    if authorization.get("publication_authorized") is not False:
        errors.append("publication_authorized must remain false")
    if authorization.get("catalog_promotion_authorized") is not False:
        errors.append("catalog_promotion_authorized must remain false")
    if package.get("episode_id") != cues_payload.get("episode_id"):
        errors.append("edit package and cue sheet episode IDs differ")
    if package.get("episode_id") != authorization.get("episode_id"):
        errors.append("authorization episode_id does not match the edit package")
    expected_hashes = {
        "base_edit_package_hash": package_hash,
        "cue_sheet_hash": cue_hash,
        "canonical_audio_manifest_hash": audio_manifest_hash,
        "canonical_audio_hash": str(audio.get("audio_sha256") or ""),
        "word_timing_sha256": word_sha,
    }
    for key, expected in expected_hashes.items():
        if str(authorization.get(key) or "") != expected:
            errors.append(f"authorization {key} does not match the immutable handoff")
    if str(package.get("cue_sheet_hash") or "") != cue_hash:
        errors.append("edit package cue_sheet_hash is stale or mismatched")
    if str(package.get("canonical_audio_hash") or "") != str(audio.get("audio_sha256") or ""):
        errors.append("edit package canonical_audio_hash is mismatched")
    if str(package.get("word_timing_sha256") or "") != word_sha:
        errors.append("edit package word_timing_sha256 is mismatched")
    if str(cues_payload.get("canonical_audio_hash") or "") != str(audio.get("audio_sha256") or ""):
        errors.append("cue sheet canonical_audio_hash is mismatched")
    if str(cues_payload.get("canonical_audio_manifest_hash") or "") != audio_manifest_hash:
        errors.append("cue sheet canonical_audio_manifest_hash is mismatched")
    if str(cues_payload.get("word_timing_sha256") or "") != word_sha:
        errors.append("cue sheet word_timing_sha256 is mismatched")
    try:
        duration_s = float(audio.get("duration_s") or 0)
    except (TypeError, ValueError):
        duration_s = 0.0
    if not math.isclose(duration_s, _CANONICAL_DURATION_S, abs_tol=_EPSILON):
        errors.append("canonical audio duration must be 567.804 seconds")
    if len(words_payload.get("words") or []) != _CANONICAL_WORD_COUNT:
        errors.append("canonical word timing must contain exactly 1528 words")
    words = list(words_payload.get("words") or [])
    package_timeline = package.get("timeline")
    cue_records = cues_payload.get("cues")
    if not isinstance(package_timeline, list) or len(package_timeline) != _CANONICAL_CUE_COUNT:
        errors.append("edit package must contain exactly 192 timeline entries")
        package_timeline = []
    if not isinstance(cue_records, list) or len(cue_records) != _CANONICAL_CUE_COUNT:
        errors.append("cue sheet must contain exactly 192 cues")
        cue_records = []
    selected_assets = authorization.get("selected_assets")
    if not isinstance(selected_assets, list) or len(selected_assets) != _CANONICAL_CUE_COUNT:
        errors.append("authorization must list exactly 192 selected assets")
        selected_assets = []
    selected_by_id: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(selected_assets):
        if not isinstance(item, Mapping):
            errors.append(f"authorization selected_assets[{index}] must be an object")
            continue
        cue_id = str(item.get("cue_id") or "")
        if cue_id in selected_by_id:
            errors.append(f"authorization duplicates selected asset {cue_id}")
        selected_by_id[cue_id] = item
    sources: list[Path] = []
    normalized: list[dict[str, Any]] = []
    previous_word_end = -1
    previous_timeline_end = 0.0
    for index in range(max(len(package_timeline), len(cue_records))):
        if index >= len(package_timeline) or index >= len(cue_records):
            break
        timeline = package_timeline[index]
        cue = cue_records[index]
        if not isinstance(timeline, Mapping) or not isinstance(cue, Mapping):
            errors.append(f"cue/timeline pair {index + 1} must be objects")
            continue
        cue_id = str(cue.get("cue_id") or "")
        if cue_id != str(timeline.get("cue_id") or ""):
            errors.append(f"cue {index + 1} ID does not match edit package timeline")
        if int(cue.get("order") or 0) != index + 1:
            errors.append(f"cue {cue_id} order is not contiguous")
        try:
            start_index = int(cue["start_word_index"])
            end_index = int(cue["end_word_index"])
            timeline_start = float(cue["timeline_start_s"])
            timeline_end = float(cue["timeline_end_s"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"cue {cue_id} has invalid word or timeline bounds: {exc}")
            continue
        package_range = timeline.get("word_range")
        if not isinstance(package_range, list) or len(package_range) != 2:
            errors.append(f"edit package cue {cue_id} has invalid word_range")
            package_range = [-1, -1]
        if [start_index, end_index] != [int(package_range[0]), int(package_range[1])]:
            errors.append(f"cue {cue_id} word range does not match edit package")
        if start_index != previous_word_end + 1 or end_index < start_index or end_index >= len(words):
            errors.append(f"cue {cue_id} word range is not contiguous")
        excerpt = " ".join(str(cue.get("narration_excerpt") or "").split())
        package_excerpt = " ".join(str(timeline.get("narration_excerpt") or "").split())
        canonical_excerpt = " ".join(str(word.get("w") or "") for word in words[start_index : end_index + 1])
        if _normalized_tokens(excerpt) != _normalized_tokens(package_excerpt) or _normalized_tokens(excerpt) != _normalized_tokens(canonical_excerpt):
            errors.append(f"cue {cue_id} narration excerpt does not match its word range")
        _same_number(timeline_start, timeline.get("start_s"), label=f"cue {cue_id} start")
        _same_number(timeline_end, timeline.get("end_s"), label=f"cue {cue_id} end")
        _same_number(timeline_end - timeline_start, cue.get("duration_s"), label=f"cue {cue_id} duration")
        if index == 0:
            if not math.isclose(timeline_start, 0.0, abs_tol=_EPSILON):
                errors.append("cue timeline must start at 0.000 seconds")
        elif not math.isclose(timeline_start, previous_timeline_end, abs_tol=_EPSILON):
            errors.append(f"cue {cue_id} timeline has a gap or overlap")
        if index:
            midpoint = (float(words[previous_word_end]["end_s"]) + float(words[start_index]["start_s"])) / 2
            if not math.isclose(timeline_start, midpoint, abs_tol=_EPSILON):
                errors.append(f"cue {cue_id} boundary is not the deterministic word midpoint")
        candidate = timeline.get("candidate")
        if not isinstance(candidate, Mapping):
            errors.append(f"cue {cue_id} is missing its candidate record")
            candidate = {}
        candidate_path = str(candidate.get("candidate_path") or "")
        candidate_sha = str(candidate.get("sha256") or "").casefold()
        auth_asset = selected_by_id.get(cue_id)
        if auth_asset is None:
            errors.append(f"authorization is missing selected asset for {cue_id}")
        else:
            if str(auth_asset.get("candidate_path") or "") != candidate_path:
                errors.append(f"authorization candidate path differs for {cue_id}")
            if str(auth_asset.get("sha256") or "").casefold() != candidate_sha:
                errors.append(f"authorization candidate hash differs for {cue_id}")
        try:
            source = _resolve_source_path(
                candidate_path,
                project_root=project_root,
                episode_root=episode_root,
                label=f"candidate {cue_id}",
            )
            if _hash_file(source) != candidate_sha:
                errors.append(f"candidate {cue_id} content hash is stale")
            sources.append(source)
        except MartialEditorialAdapterError as exc:
            errors.extend(exc.errors)
            source = Path()
        micro_events = copy.deepcopy(list(cue.get("micro_events") or []))
        if timeline_end - timeline_start > 3.35 + _EPSILON:
            material_events = [
                event for event in micro_events
                if isinstance(event, Mapping) and str(event.get("action") or "").strip()
            ]
            if not material_events:
                errors.append(f"cue {cue_id} longer than 3.35 seconds lacks a timed material event")
        normalized.append(
            {
                "block_id": cue_id,
                "order": index + 1,
                "coverage_slot_ids": [cue_id],
                "start_s": round(timeline_start, 6),
                "end_s": round(timeline_end, 6),
                "duration_s": round(timeline_end - timeline_start, 6),
                "narration_excerpt": excerpt,
                "chapter_id": str(cue.get("chapter_id") or ""),
                "function": _function_for_cue(str(cue.get("primary_class") or "")),
                "visual_archetype": "martial_matters_woodblock_editorial_plate",
                "visual_source": "authorized_local_candidate",
                "visual_direction": str(cue.get("story_signal") or cue.get("entry_action") or f"Authorized primary plate for {cue_id}"),
                "prompt": f"Martial Matters editorial plate {cue_id}: {excerpt}",
                "planned_path": f"assets/{cue_id}.png",
                "status": "authorized_local_candidate",
                "render_eligible": False,
                "evidence_eligible": False,
                "contains_factual_text": False,
                "disclosure_label": "Authorized internal-review editorial plate",
                "source_cue_id": cue_id,
                "start_word_index": start_index,
                "end_word_index": end_index,
                "timeline_start_s": round(timeline_start, 6),
                "timeline_end_s": round(timeline_end, 6),
                "explicit_word_range": {"start_index": start_index, "end_index": end_index},
                "explicit_timeline_range": {"start_s": round(timeline_start, 6), "end_s": round(timeline_end, 6)},
                "claim_refs": copy.deepcopy(list(cue.get("claim_refs") or [])),
                "source_locators": copy.deepcopy(list(cue.get("source_locators") or [])),
                "local_overlay": copy.deepcopy(cue.get("local_overlay") or {}),
                "entry_action": str(cue.get("entry_action") or ""),
                "micro_events": micro_events,
                "exit_transition": str(cue.get("exit_transition") or ""),
                "selected_asset_sha256": candidate_sha,
                "candidate_path": candidate_path,
            }
        )
        previous_word_end = end_index
        previous_timeline_end = timeline_end
    if previous_word_end != len(words) - 1:
        errors.append("cue word ranges must cover canonical words 0 through 1527")
    if not math.isclose(previous_timeline_end, duration_s, abs_tol=_EPSILON):
        errors.append("cue timeline must end at the canonical audio duration")
    if len(set(str(item.get("cue_id") or "") for item in selected_assets if isinstance(item, Mapping))) != _CANONICAL_CUE_COUNT:
        errors.append("authorization selected assets must contain each cue exactly once")
    if errors:
        raise MartialEditorialAdapterError(errors)
    return normalized, sources


def compile_martial_editorial(
    *,
    edit_package: Mapping[str, Any] | str | Path,
    authorization: Mapping[str, Any] | str | Path,
    job_root: str | Path,
    revision_id: str,
    cue_sheet: Mapping[str, Any] | str | Path | None = None,
    audio_manifest: Mapping[str, Any] | str | Path | None = None,
    word_timings: Mapping[str, Any] | str | Path | None = None,
    caption_plan: Mapping[str, Any] | str | Path | None = None,
    caption_output: Mapping[str, Any] | str | Path | None = None,
    pacing_recipe: Mapping[str, Any] | str | Path | None = None,
    project_root: str | Path | None = None,
    allow_external_job_root: bool = False,
    sample_max_seconds: float | None = None,
    sample_max_cues: int | None = None,
) -> dict[str, Any]:
    """Compile the authorized handoff into a contained revision directory."""

    project = Path(project_root).expanduser().resolve() if project_root else _REPO_ROOT
    revision = _safe_revision_id(revision_id)
    job = Path(job_root).expanduser().resolve()
    canonical_jobs = (_ENGINE_ROOT / "runtime" / "jobs").resolve()
    if not allow_external_job_root and not _inside(job, canonical_jobs):
        raise MartialEditorialAdapterError(
            "job_root must remain under content/video_engine/runtime/jobs"
        )
    if job == canonical_jobs:
        raise MartialEditorialAdapterError("job_root must identify a named job directory")
    revision_dir = (job / "animatic" / "revisions" / revision).resolve()
    if not _inside(revision_dir, job / "animatic" / "revisions"):
        raise MartialEditorialAdapterError("revision output escapes job_root")
    defaults = _default_inputs(edit_package, project_root=project) if not isinstance(edit_package, Mapping) else {}
    cue_source = cue_sheet or defaults.get("cue_sheet")
    audio_source = audio_manifest or defaults.get("audio_manifest")
    words_source = word_timings or defaults.get("word_timings")
    package = _load(edit_package, "edit package")
    cues_payload = _load(cue_source, "cue sheet")
    audio = _load(audio_source, "canonical audio manifest")
    words_payload = _load(words_source, "canonical word timings")
    auth = _load(authorization, "editorial review authorization")
    if caption_plan is None:
        caption_plan = defaults.get("caption_plan") or package.get("caption_outputs", {}).get("dynamic_caption_track")
    if caption_output is None:
        caption_output = defaults.get("caption_output") or package.get("caption_outputs", {}).get("anchor_srt")
    if isinstance(caption_plan, Mapping) or isinstance(caption_output, Mapping):
        raise MartialEditorialAdapterError(
            "caption_plan and caption_output must be explicit contained files"
        )
    caption_plan_path = _input_path(caption_plan, "caption plan")
    caption_output_path = _input_path(caption_output, "caption output")
    caption_payload = _load(caption_plan_path, "caption plan")
    pacing = validate_editorial_pacing_recipe(pacing_recipe or build_default_pacing_recipe())
    package_hash = _artifact_hash(package, "edit package")
    cue_hash = _artifact_hash(cues_payload, "cue sheet")
    audio_manifest_hash = _artifact_hash(audio, "canonical audio manifest")
    auth_errors = _schema_errors(auth, "editorial_review_authorization.schema.json")
    if auth_errors:
        raise MartialEditorialAdapterError(auth_errors)
    auth_hash = _artifact_hash(auth, "editorial review authorization")
    if not auth_hash:
        raise MartialEditorialAdapterError("authorization is not hash-bound")
    word_path = Path(words_source).expanduser().resolve() if words_source is not None and not isinstance(words_source, Mapping) else None
    if word_path is not None and not word_path.is_file():
        raise MartialEditorialAdapterError(f"canonical word timings do not exist: {word_path}")
    word_sha = _hash_file(word_path) if word_path is not None else canonical_sha256(words_payload)
    episode = _episode_root(edit_package if not isinstance(edit_package, Mapping) else None, project)
    normalized, sources = _validate_source_contracts(
        package=package,
        cues_payload=cues_payload,
        audio=audio,
        words_payload=words_payload,
        authorization=auth,
        package_hash=package_hash,
        cue_hash=cue_hash,
        audio_manifest_hash=audio_manifest_hash,
        word_sha=word_sha,
        episode_root=episode,
        project_root=project,
    )
    audio_source_path = _resolve_source_path(
        audio.get("audio_path"),
        project_root=project,
        episode_root=episode,
        label="canonical audio",
    )
    audio_sha = str(audio.get("audio_sha256") or "").casefold()
    if _hash_file(audio_source_path) != audio_sha:
        raise MartialEditorialAdapterError("canonical audio content hash is stale")
    package_caption_outputs = package.get("caption_outputs")
    if not isinstance(package_caption_outputs, Mapping):
        raise MartialEditorialAdapterError("edit package is missing caption_outputs")
    expected_caption_plan = _resolve_source_path(
        package_caption_outputs.get("dynamic_caption_track"),
        project_root=project,
        episode_root=episode,
        label="edit package dynamic caption track",
    )
    expected_caption_output = _resolve_source_path(
        package_caption_outputs.get("anchor_srt"),
        project_root=project,
        episode_root=episode,
        label="edit package anchor caption output",
    )
    if caption_plan_path != expected_caption_plan:
        raise MartialEditorialAdapterError("caption plan differs from the edit package locator")
    if caption_output_path != expected_caption_output:
        raise MartialEditorialAdapterError("caption output differs from the edit package locator")
    caption_plan_sha = _hash_file(caption_plan_path)
    caption_output_sha = _hash_file(caption_output_path)
    if str(caption_payload.get("schema_version") or "") != "dynamic_caption_track.v1":
        raise MartialEditorialAdapterError("caption plan must use dynamic_caption_track.v1")
    if str(caption_payload.get("word_timing_sha256") or "") != word_sha:
        raise MartialEditorialAdapterError("caption plan word_timing_sha256 is stale")
    overlay_map = _caption_overlay_map(caption_payload, duration_s=float(audio["duration_s"]))
    overlay_ids_by_cue: dict[str, list[str]] = {}
    for block in normalized:
        start_s = float(block["timeline_start_s"])
        end_s = float(block["timeline_end_s"])
        overlay_ids_by_cue[str(block["source_cue_id"])] = [
            overlay_id
            for overlay_id, overlay in overlay_map.items()
            if float(overlay["start_s"]) < end_s - _EPSILON and float(overlay["end_s"]) > start_s + _EPSILON
        ]
        block["overlay_ids"] = overlay_ids_by_cue[str(block["source_cue_id"])]
    plate_core = {
        "schema_version": "timestamped_plate_plan.v1",
        "provider": "authorized-local-editorial-adapter",
        "coverage_plan_hash": cue_hash,
        "plate_count": len(normalized),
        "duration_s": _CANONICAL_DURATION_S,
        "one_primary_plate_per_timestamp_slot": True,
        "blocks": normalized,
        "policy": {
            "generated_pixels_are_not_evidence": True,
            "factual_overlay_owner": "remotion",
            "provider_output_render_eligible": False,
            "internal_review_authorization_only": True,
        },
    }
    plate_plan = {**plate_core, "artifact_hash": canonical_sha256(plate_core)}
    try:
        plate_plan = validate_timestamped_plate_plan(plate_plan)
    except GeneratedBlockImageError as exc:
        raise MartialEditorialAdapterError(exc.errors) from exc
    assets: list[dict[str, Any]] = []
    for block, source in zip(normalized, sources, strict=True):
        cue_id = str(block["source_cue_id"])
        sha = str(block["selected_asset_sha256"])
        assets.append(
            {
                "id": cue_id,
                "path": f"assets/{cue_id}.png",
                "local_path": f"assets/{cue_id}.png",
                "source_path": str(block["candidate_path"]),
                "sha256": sha,
                "content_hash": sha,
                "render_eligible": True,
                "human_promoted": True,
                "provider_output": False,
                "evidence_eligible": False,
                "metadata": {
                    "coverage_slot_id": cue_id,
                    "timestamped_plate_plan_hash": plate_plan["artifact_hash"],
                    "source_cue_id": cue_id,
                    "authorization_id": str(auth["authorization_id"]),
                },
            }
        )
    asset_core = {
        "schema_version": "martial_editorial_asset_map.v1",
        "episode_id": str(package.get("episode_id") or ""),
        "revision_id": revision,
        "authorization_id": str(auth.get("authorization_id") or ""),
        "assets": assets,
        "source_edit_package_hash": package_hash,
        "source_cue_sheet_hash": cue_hash,
    }
    asset_map = {**asset_core, "artifact_hash": canonical_sha256(asset_core)}
    _copy_immutable(audio_source_path, job / str(audio["audio_path"]), expected_sha=audio_sha, label="canonical audio")
    public = revision_dir / "public"
    for item, source in zip(assets, sources, strict=True):
        _copy_immutable(source, public / str(item["path"]), expected_sha=str(item["sha256"]), label=f"asset {item['id']}")
    audio_destination = public / "audio" / "canonical.mp3"
    _copy_immutable(audio_source_path, audio_destination, expected_sha=audio_sha, label="revision canonical audio")
    explicit_assets = {str(item["id"]): str(item["path"]) for item in assets}
    motion_plan = compile_timestamped_editorial_motion_plan(
        timestamped_plate_plan=plate_plan,
        asset_map=asset_map,
        audio_manifest=audio,
        word_timings=words_payload,
        pacing_recipe=pacing,
        explicit_timing=True,
    )
    selected_motion_plan = motion_plan
    selected_count = len(motion_plan["shots"])
    if sample_max_cues is not None:
        if int(sample_max_cues) <= 0:
            raise MartialEditorialAdapterError("sample_max_cues must be positive")
        selected_count = min(selected_count, int(sample_max_cues))
    if sample_max_seconds is not None:
        if float(sample_max_seconds) <= 0:
            raise MartialEditorialAdapterError("sample_max_seconds must be positive")
        eligible = [
            shot for shot in motion_plan["shots"]
            if float(shot["start_s"]) + float(shot["duration_s"]) <= float(sample_max_seconds) + _EPSILON
        ]
        if not eligible:
            raise MartialEditorialAdapterError("sample_max_seconds does not include a complete cue")
        selected_count = min(selected_count, len(eligible))
    if selected_count < len(motion_plan["shots"]):
        sample_end = float(motion_plan["shots"][selected_count - 1]["start_s"]) + float(motion_plan["shots"][selected_count - 1]["duration_s"])
        selected_motion_plan = derive_editorial_motion_sample(
            motion_plan,
            end_s=sample_end,
            known_asset_ids={str(item["id"]) for item in assets},
        )
    props_core = {
        "plan": selected_motion_plan,
        "asset_map": explicit_assets,
        "canonical_audio": {"path": "audio/canonical.mp3", "start_s": 0.0, "volume": 1},
        "overlay_map": overlay_map,
        "caption_policy": "platform",
        "citation_policy": "credits_only",
        "diagnostic": False,
        "render_profile": {"width": 854, "height": 480, "fps": 15, "label": "martial-editorial-adapter"},
    }
    props = {**props_core, "artifact_hash": canonical_sha256(props_core)}
    contained_files = [
        {"path": f"public/{item['path']}", "sha256": str(item["sha256"])}
        for item in assets
    ] + [{"path": "public/audio/canonical.mp3", "sha256": audio_sha}]
    manifest_core = {
        "schema_version": MARTIAL_ADAPTER_MANIFEST_VERSION,
        "episode_id": str(package.get("episode_id") or ""),
        "revision_id": revision,
        "authorization_id": str(auth.get("authorization_id") or ""),
        "base_edit_package_hash": package_hash,
        "cue_sheet_hash": cue_hash,
        "canonical_audio_manifest_hash": audio_manifest_hash,
        "canonical_audio_hash": audio_sha,
        "word_timing_sha256": word_sha,
        "caption_plan_sha256": caption_plan_sha,
        "caption_output_sha256": caption_output_sha,
        "pacing_recipe_hash": str(pacing["artifact_hash"]),
        "normalized_plate_plan_hash": plate_plan["artifact_hash"],
        "asset_map_hash": asset_map["artifact_hash"],
        "overlay_map_hash": canonical_sha256(overlay_map),
        "props_hash": props["artifact_hash"],
        "motion_plan_hash": selected_motion_plan["artifact_hash"],
        "duration_s": float(selected_motion_plan["duration_s"]),
        "coverage_start_s": 0.0,
        "coverage_end_s": float(selected_motion_plan["duration_s"]),
        "cue_count": _CANONICAL_CUE_COUNT,
        "staged_asset_count": len(assets),
        "contained_file_hashes": contained_files,
    }
    manifest = {**manifest_core, "artifact_hash": canonical_sha256(manifest_core)}
    manifest_errors = _schema_errors(manifest, "martial_editorial_adapter_manifest.schema.json")
    if manifest_errors:
        raise MartialEditorialAdapterError(manifest_errors)
    for name, payload in {
        "timestamped-plate-plan.json": plate_plan,
        "asset-map.json": asset_map,
        "overlay-map.json": overlay_map,
        "editorial-motion-plan.json": selected_motion_plan,
        "canonical-audio-manifest.json": audio,
        "adapter-remotion-props.json": props,
        "pacing-recipe.json": pacing,
        "martial-editorial-adapter-manifest.json": manifest,
    }.items():
        _write_json(revision_dir / name, payload)
    return {
        "episode_id": package.get("episode_id"),
        "revision_id": revision,
        "authorization_id": auth.get("authorization_id"),
        "output_dir": str(revision_dir),
        "revision_dir": str(revision_dir),
        "timestamped_plate_plan": plate_plan,
        "normalized_plate_plan": plate_plan,
        "asset_map": asset_map,
        "overlay_map": overlay_map,
        "motion_plan": selected_motion_plan,
        "plan": selected_motion_plan,
        "props": props,
        "adapter_manifest": manifest,
        "artifact_paths": {
            name: str(revision_dir / name)
            for name in (
                "timestamped-plate-plan.json",
                "asset-map.json",
                "overlay-map.json",
                "editorial-motion-plan.json",
                "canonical-audio-manifest.json",
                "adapter-remotion-props.json",
                "pacing-recipe.json",
                "martial-editorial-adapter-manifest.json",
            )
        },
    }


compile_martial_editorial_adapter = compile_martial_editorial


__all__ = [
    "EDITORIAL_REVIEW_AUTHORIZATION_VERSION",
    "MARTIAL_ADAPTER_MANIFEST_VERSION",
    "MartialEditorialAdapterError",
    "compile_martial_editorial",
    "compile_martial_editorial_adapter",
]
