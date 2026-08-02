"""Audio-driven Higgsfield explainer contracts.

This module is deliberately a provider boundary, not a renderer.  It compiles
the reviewed History coverage and generated plates into fixed ten-second
requests, resolves only an episode-local ElevenLabs manifest, and records
Higgsfield tasks without making an implicit network or billing call.

The provider receives local, content-addressed references and an abstract
style/action prompt.  Research claims, citations, URLs, and unresolved source
provenance stay in the local editorial layer.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlparse

from content.video_engine.src.services.generated_block_images import (
    GeneratedBlockImageError,
    validate_generated_block_batch,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


HIGGSFIELD_BLOCK_PLAN_VERSION = "higgsfield_audio_blocks.v1"
ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION = "elevenlabs_block_audio.v1"
HIGGSFIELD_JOB_MANIFEST_VERSION = "higgsfield_audio_job.v1"
HIGGSFIELD_LOCAL_ASSEMBLY_MANIFEST_VERSION = "higgsfield_local_assembly.v1"

_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_REMOTE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_PROHIBITED = (
    "in the style of",
    "style of",
    "youtube.com",
    "youtu.be",
    "source frame",
    "creator name",
    "reference video",
)


class HiggsfieldExplainerError(ValueError):
    """Raised when the audio-driven handoff is unsafe or incomplete."""

    def __init__(self, errors: Iterable[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors) or "invalid Higgsfield explainer artifact")


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HiggsfieldExplainerError([f"{label} is not valid JSON: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise HiggsfieldExplainerError([f"{label} must contain an object"])
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_remote(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc) or bool(_REMOTE.match(value))


def _resolve_local(value: str, root: Path) -> Path | None:
    if not value or Path(value).is_absolute() or _is_remote(value):
        return None
    try:
        path = (root / value).resolve(strict=True)
        path.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    return path if path.is_file() else None


def _normalise_text(value: Any) -> str:
    return " ".join(str(value or "").split())


def _narration_hash(value: Any) -> str:
    return hashlib.sha256(_normalise_text(value).encode("utf-8")).hexdigest()


def _safe_id(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return (cleaned[:56] or fallback).strip("-")


def _ordered_unique(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "")
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _character_refs(value: Mapping[str, Any] | str | Path | None) -> tuple[list[dict[str, Any]], str]:
    if value is None:
        return [], ""
    payload = _load(value, "character pack")
    characters = payload.get("characters")
    if not isinstance(characters, list):
        raise HiggsfieldExplainerError(["character pack characters must be an array"])
    refs: list[dict[str, Any]] = []
    for index, raw in enumerate(characters):
        if not isinstance(raw, Mapping):
            raise HiggsfieldExplainerError([f"character pack characters[{index}] must be an object"])
        character_id = str(raw.get("character_id") or raw.get("id") or "")
        if not _SAFE_ID.fullmatch(character_id):
            raise HiggsfieldExplainerError([f"character pack characters[{index}] has an unsafe id"])
        asset = raw.get("asset") if isinstance(raw.get("asset"), Mapping) else raw
        path = str((asset or {}).get("path") or (asset or {}).get("local_path") or "")
        digest = str((asset or {}).get("sha256") or "").casefold()
        approved_asset_ids = raw.get("reference_asset_ids")
        approved_asset_id = (
            str(approved_asset_ids[0])
            if isinstance(approved_asset_ids, list) and approved_asset_ids and approved_asset_ids[0]
            else character_id
        )
        refs.append(
            {
                "character_id": character_id,
                "asset_id": str((asset or {}).get("asset_id") or approved_asset_id),
                "path": path,
                "sha256": digest,
            }
        )
    return refs, str(payload.get("artifact_hash") or canonical_sha256(payload))


def _partition_slots(slots: list[Mapping[str, Any]], count: int) -> list[list[Mapping[str, Any]]]:
    """Partition contiguous slots near equal-duration targets.

    The source coverage is 607.999 seconds while the provider request is a
    ten-second clip.  We retain the exact source duration on each block and
    use a deterministic video-only fit during local assembly; narration is
    never trimmed to make a provider boundary look exact.
    """

    if count < 1:
        raise HiggsfieldExplainerError(["block_count must be positive"])
    if len(slots) < count:
        raise HiggsfieldExplainerError(
            [f"coverage has {len(slots)} slots; cannot compile {count} non-empty blocks"]
        )
    durations = [float(slot.get("duration_s") or 0.0) for slot in slots]
    if any(duration <= 0 for duration in durations):
        raise HiggsfieldExplainerError(["every coverage slot duration_s must be positive"])
    cumulative: list[float] = [0.0]
    for duration in durations:
        cumulative.append(cumulative[-1] + duration)
    total = cumulative[-1]
    groups: list[list[Mapping[str, Any]]] = []
    start = 0
    for group_index in range(count):
        remaining_groups = count - group_index - 1
        if group_index == count - 1:
            end = len(slots)
        else:
            minimum_end = start + 1
            maximum_end = len(slots) - remaining_groups
            target = total * (group_index + 1) / count
            end = min(
                range(minimum_end, maximum_end + 1),
                key=lambda candidate: (abs(cumulative[candidate] - target), candidate),
            )
        groups.append(slots[start:end])
        start = end
    return groups


def _plate_for_group(
    group: list[Mapping[str, Any]],
    plate_by_slot: Mapping[str, list[Mapping[str, Any]]],
) -> Mapping[str, Any]:
    group_ids = {str(slot.get("slot_id") or "") for slot in group}
    candidates: list[tuple[int, int, Mapping[str, Any]]] = []
    for slot_id in group_ids:
        for plate in plate_by_slot.get(slot_id, []):
            covered = set(str(item) for item in plate.get("coverage_slot_ids", []))
            overlap = len(group_ids & covered)
            order = int(plate.get("order") or 10**9)
            candidates.append((overlap, -order, plate))
    if not candidates:
        raise HiggsfieldExplainerError(
            [f"no generated plate covers block slots {sorted(group_ids)!r}"]
        )
    return max(candidates, key=lambda item: (item[0], item[1]))[2]


def _block_prompt(excerpt: str, function: str) -> str:
    return (
        "Animate the supplied original illustrated plate as a clean, silent, "
        "audio-timed editorial shot. Preserve the plate, cast ownership, woodblock-comic "
        "palette, paper texture, and composition. Use exactly one clear action only; "
        f"the editorial function is {function!r} and the narration beat is {excerpt!r}. "
        "Use smooth restrained motion, no camera shake, no scene replacement, and end on "
        "a readable held pose for local captions and citations. Do not render words, dates, "
        "maps, logos, citations, or new historical facts."
    )


def _negative_prompt() -> str:
    return (
        "camera shake, handheld drift, shuttering, background wobble, scene replacement, "
        "new characters, costume change, face change, extra limbs, generated text, logos, "
        "watermarks, lip sync, dialogue, photorealism, grappling choreography, new facts"
    )


def compile_higgsfield_blocks(
    coverage: Mapping[str, Any] | str | Path,
    generated_batch: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    block_count: int = 60,
    provider_duration_s: float = 10.0,
    character_pack: Mapping[str, Any] | str | Path | None = None,
    art_bible_hash: str = "",
    storyboard_hash: str = "",
) -> dict[str, Any]:
    """Compile 138 editorial beats into deterministic audio-driven blocks."""

    coverage_payload = _load(coverage, "editorial coverage")
    if coverage_payload.get("schema_version") != "editorial_coverage.v1":
        raise HiggsfieldExplainerError(["coverage must use editorial_coverage.v1"])
    slots_raw = coverage_payload.get("slots")
    if not isinstance(slots_raw, list) or not slots_raw:
        raise HiggsfieldExplainerError(["coverage slots must be a non-empty array"])
    slots: list[Mapping[str, Any]] = []
    seen_slots: set[str] = set()
    for index, raw in enumerate(slots_raw):
        if not isinstance(raw, Mapping):
            raise HiggsfieldExplainerError([f"coverage slots[{index}] must be an object"])
        slot_id = str(raw.get("slot_id") or "")
        if not _SAFE_ID.fullmatch(slot_id) or slot_id in seen_slots:
            raise HiggsfieldExplainerError([f"coverage slots[{index}] has a duplicate or unsafe slot_id"])
        if not _normalise_text(raw.get("narration_excerpt")):
            raise HiggsfieldExplainerError([f"coverage slots[{index}] narration_excerpt is required"])
        seen_slots.add(slot_id)
        slots.append(raw)

    root = Path(job_root).resolve()
    try:
        batch = validate_generated_block_batch(
            generated_batch,
            job_root=root,
            check_files=True,
        )
    except GeneratedBlockImageError as exc:
        raise HiggsfieldExplainerError(exc.errors) from exc

    plate_by_slot: dict[str, list[Mapping[str, Any]]] = {}
    for plate in batch.get("blocks", []):
        for slot_id in plate.get("coverage_slot_ids", []):
            plate_by_slot.setdefault(str(slot_id), []).append(plate)
    missing_plates = sorted(seen_slots - set(plate_by_slot))
    if missing_plates:
        raise HiggsfieldExplainerError(
            [f"generated plate batch does not cover slots: {', '.join(missing_plates[:8])}"]
        )
    character_refs, character_pack_hash = _character_refs(character_pack)

    groups = _partition_slots(slots, block_count)
    blocks: list[dict[str, Any]] = []
    timeline_cursor = 0.0
    for index, group in enumerate(groups, start=1):
        first = group[0]
        slot_ids = [str(slot["slot_id"]) for slot in group]
        excerpt = " ".join(
            _ordered_unique(slot.get("narration_excerpt") for slot in group)
        )
        duration_s = round(sum(float(slot.get("duration_s") or 0) for slot in group), 6)
        function = str(first.get("function") or "illustrated_reconstruction")
        plate = _plate_for_group(group, plate_by_slot)
        events: list[dict[str, Any]] = []
        local_offset = 0.0
        for slot in group:
            for event in slot.get("micro_events") or []:
                if not isinstance(event, Mapping):
                    continue
                event_copy = dict(event)
                event_copy["at_s"] = round(
                    local_offset + float(event.get("at_s") or 0),
                    6,
                )
                event_copy["source_slot_id"] = str(slot["slot_id"])
                events.append(event_copy)
            local_offset += float(slot.get("duration_s") or 0)
        if not events:
            events = [{"at_s": 0.0, "action": "hold", "recipe": "restrained_breath"}]
        block_id = f"higgsfield-block-{index:03d}-{_safe_id(slot_ids[0], f'block-{index:03d}')[:48]}"
        blocks.append(
            {
                "block_id": block_id,
                "order": index,
                "source_beat_ids": slot_ids,
                "coverage_slot_ids": slot_ids,
                "narration_excerpt": excerpt,
                "narration_hash": _narration_hash(excerpt),
                "claim_refs": _ordered_unique(
                    claim for slot in group for claim in (slot.get("claim_refs") or [])
                ),
                "citation_refs": _ordered_unique(
                    citation for slot in group for citation in (slot.get("citation_refs") or [])
                ),
                "asset_ids": _ordered_unique(
                    asset for slot in group for asset in (slot.get("asset_ids") or [])
                ),
                "function": function,
                "semantic_purposes": _ordered_unique(
                    slot.get("semantic_purpose") for slot in group
                ),
                "duration_s": duration_s,
                "provider_duration_s": float(provider_duration_s),
                "timeline_start_s": round(timeline_cursor, 6),
                "timeline_end_s": round(timeline_cursor + duration_s, 6),
                "micro_events": events,
                "motion_recipe": str(first.get("motion_recipe") or "detail_punch"),
                "plate": {
                    "source_block_id": str(plate.get("block_id") or ""),
                    "path": str(plate.get("path") or plate.get("planned_path") or ""),
                    "sha256": str(plate.get("sha256") or "").casefold(),
                },
                "character_refs": copy.deepcopy(character_refs),
                "prompt": _block_prompt(excerpt, function),
                "negative_prompt": _negative_prompt(),
                "audio": {
                    "required": True,
                    "source": "elevenlabs",
                    "block_plan_narration_hash": _narration_hash(excerpt),
                    "generate_audio": False,
                },
                "fit_policy": {
                    "source_duration_s": duration_s,
                    "provider_duration_s": float(provider_duration_s),
                    "video_only_time_stretch": True,
                    "narration_trim_allowed": False,
                },
                "status": "planned",
                "render_eligible": False,
            }
        )
        timeline_cursor += duration_s

    core = {
        "schema_version": HIGGSFIELD_BLOCK_PLAN_VERSION,
        "coverage_plan_hash": str(
            coverage_payload.get("artifact_hash") or canonical_sha256(coverage_payload)
        ),
        "generated_plate_batch_hash": str(batch.get("artifact_hash") or ""),
        "art_bible_hash": art_bible_hash,
        "storyboard_hash": storyboard_hash,
        "character_pack_hash": character_pack_hash,
        "coverage_slot_count": len(slots),
        "block_count": len(blocks),
        "timeline_duration_s": round(timeline_cursor, 6),
        "provider_duration_s": float(provider_duration_s),
        "character_count": len(character_refs),
        "blocks": blocks,
        "policy": {
            "fixed_provider_blocks": True,
            "provider_duration_s": float(provider_duration_s),
            "canonical_narration_owner": "elevenlabs",
            "provider_audio_disabled": True,
            "provider_output_render_eligible": False,
            "one_clear_action_per_block": True,
            "narration_trim_allowed": False,
            "local_remotion_assembly_authoritative": True,
        },
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def compile_audio_aligned_higgsfield_blocks(
    coverage: Mapping[str, Any] | str | Path,
    generated_batch: Mapping[str, Any] | str | Path,
    narration: Mapping[str, Any] | str | Path,
    canonical_audio: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    character_pack: Mapping[str, Any] | str | Path | None = None,
    art_bible_hash: str = "",
    storyboard_hash: str = "",
) -> dict[str, Any]:
    """Compile visual coverage against real narration windows.

    The legacy compiler partitions the visual cadence into sixty groups and
    uses each group's visual excerpts as speech.  V2 keeps the visual plates,
    but the audio manifest owns block count, timing, and spoken text.  Coverage
    is scaled once from its editorial timeline onto the measured voice take;
    no coverage excerpt is sent to TTS.
    """

    from content.video_engine.src.services.history_narration import (
        validate_canonical_audio,
        validate_history_narration,
    )

    coverage_payload = _load(coverage, "editorial coverage")
    if coverage_payload.get("schema_version") != "editorial_coverage.v1":
        raise HiggsfieldExplainerError(["coverage must use editorial_coverage.v1"])
    raw_slots = coverage_payload.get("slots")
    if not isinstance(raw_slots, list) or not raw_slots:
        raise HiggsfieldExplainerError(["coverage slots must be a non-empty array"])
    slots: list[Mapping[str, Any]] = []
    seen_slots: set[str] = set()
    for index, raw in enumerate(raw_slots):
        if not isinstance(raw, Mapping):
            raise HiggsfieldExplainerError([f"coverage slots[{index}] must be an object"])
        slot_id = str(raw.get("slot_id") or "")
        if not _SAFE_ID.fullmatch(slot_id) or slot_id in seen_slots:
            raise HiggsfieldExplainerError([f"coverage slots[{index}] has a duplicate or unsafe slot_id"])
        duration = float(raw.get("duration_s") or 0)
        if duration <= 0:
            raise HiggsfieldExplainerError([f"coverage slots[{index}] duration_s must be positive"])
        seen_slots.add(slot_id)
        slots.append(raw)
    try:
        batch = validate_generated_block_batch(generated_batch, job_root=Path(job_root).resolve(), check_files=True)
    except GeneratedBlockImageError as exc:
        raise HiggsfieldExplainerError(exc.errors) from exc
    narration_payload = validate_history_narration(narration)
    audio_payload = validate_canonical_audio(canonical_audio, job_root=job_root)
    if audio_payload.get("status") != "ready":
        raise HiggsfieldExplainerError(["audio-aligned block compilation requires ready canonical audio"])
    audio_blocks = audio_payload.get("blocks")
    if not isinstance(audio_blocks, list) or not audio_blocks:
        raise HiggsfieldExplainerError(["canonical audio must contain block slices"])

    plate_by_slot: dict[str, list[Mapping[str, Any]]] = {}
    for plate in batch.get("blocks", []):
        for slot_id in plate.get("coverage_slot_ids", []):
            plate_by_slot.setdefault(str(slot_id), []).append(plate)
    missing_plates = sorted(seen_slots - set(plate_by_slot))
    if missing_plates:
        raise HiggsfieldExplainerError(
            [f"generated plate batch does not cover slots: {', '.join(missing_plates[:8])}"]
        )
    character_refs, character_pack_hash = _character_refs(character_pack)

    coverage_durations = [float(slot.get("duration_s") or 0) for slot in slots]
    coverage_total = sum(coverage_durations)
    audio_duration = float(audio_payload.get("duration_s") or 0)
    if coverage_total <= 0 or audio_duration <= 0:
        raise HiggsfieldExplainerError(["coverage and canonical audio durations must be positive"])
    scale = audio_duration / coverage_total
    slot_windows: list[tuple[Mapping[str, Any], float, float]] = []
    cursor = 0.0
    for slot, duration in zip(slots, coverage_durations):
        start = cursor * scale
        end = (cursor + duration) * scale
        slot_windows.append((slot, start, end))
        cursor += duration

    groups: list[list[Mapping[str, Any]]] = []
    group_windows: list[tuple[float, float]] = []
    assigned: set[str] = set()
    for index, raw_audio_block in enumerate(audio_blocks):
        block_start = float(raw_audio_block.get("start_s") or 0)
        block_end = float(raw_audio_block.get("end_s") or 0)
        group: list[Mapping[str, Any]] = []
        for slot, slot_start, slot_end in slot_windows:
            slot_id = str(slot["slot_id"])
            midpoint = (slot_start + slot_end) / 2.0
            if slot_id not in assigned and (
                block_start <= midpoint < block_end
                or (index == len(audio_blocks) - 1 and midpoint <= block_end)
            ):
                group.append(slot)
                assigned.add(slot_id)
        if not group:
            nearest = min(
                (entry for entry in slot_windows if str(entry[0]["slot_id"]) not in assigned),
                key=lambda entry: abs(((entry[1] + entry[2]) / 2.0) - ((block_start + block_end) / 2.0)),
                default=None,
            )
            if nearest is not None:
                group = [nearest[0]]
                assigned.add(str(nearest[0]["slot_id"]))
        groups.append(group)
        group_windows.append((block_start, block_end))
    if assigned != seen_slots:
        missing = sorted(seen_slots - assigned)
        raise HiggsfieldExplainerError(
            [f"audio timeline does not cover all visual slots: {', '.join(missing[:8])}"]
        )

    blocks: list[dict[str, Any]] = []
    for index, (group, (audio_start, audio_end), raw_audio_block) in enumerate(
        zip(groups, group_windows, audio_blocks), start=1
    ):
        if not group:
            raise HiggsfieldExplainerError([f"audio block {index} has no visual coverage"])
        first = group[0]
        slot_ids = [str(slot["slot_id"]) for slot in group]
        excerpt = " ".join(
            str(item.get("w") or "") for item in (raw_audio_block.get("word_timings") or [])
        ).strip()
        if not excerpt:
            excerpt = "Hold the approved illustration while the narration resolves."
        function = str(first.get("function") or "illustrated_reconstruction")
        plate = _plate_for_group(group, plate_by_slot)
        events: list[dict[str, Any]] = []
        for slot, slot_start, slot_end in slot_windows:
            if str(slot.get("slot_id")) not in slot_ids:
                continue
            for event in slot.get("micro_events") or []:
                if not isinstance(event, Mapping):
                    continue
                event_copy = dict(event)
                event_copy["at_s"] = round(
                    max(0.0, min(audio_end - audio_start, slot_start - audio_start + float(event.get("at_s") or 0) * scale)),
                    6,
                )
                event_copy["source_slot_id"] = str(slot["slot_id"])
                events.append(event_copy)
        if not events:
            events = [{"at_s": 0.0, "action": "hold", "recipe": "restrained_breath"}]
        block_id = f"higgsfield-block-{index:03d}-{_safe_id(slot_ids[0], f'block-{index:03d}')[:48]}"
        blocks.append(
            {
                "block_id": block_id,
                "order": index,
                "source_beat_ids": slot_ids,
                "coverage_slot_ids": slot_ids,
                "narration_excerpt": excerpt,
                "narration_hash": _narration_hash(excerpt),
                "canonical_narration_hash": narration_payload["narration_hash"],
                "claim_refs": _ordered_unique(claim for slot in group for claim in (slot.get("claim_refs") or [])),
                "citation_refs": _ordered_unique(citation for slot in group for citation in (slot.get("citation_refs") or [])),
                "asset_ids": _ordered_unique(asset for slot in group for asset in (slot.get("asset_ids") or [])),
                "function": function,
                "semantic_purposes": _ordered_unique(slot.get("semantic_purpose") for slot in group),
                "duration_s": round(audio_end - audio_start, 6),
                "provider_duration_s": 10.0,
                "timeline_start_s": round(audio_start, 6),
                "timeline_end_s": round(audio_end, 6),
                "audio_start_s": round(audio_start, 6),
                "audio_end_s": round(audio_end, 6),
                "micro_events": sorted(events, key=lambda event: float(event.get("at_s") or 0)),
                "motion_recipe": str(first.get("motion_recipe") or "detail_punch"),
                "plate": {
                    "source_block_id": str(plate.get("block_id") or ""),
                    "path": str(plate.get("path") or plate.get("planned_path") or ""),
                    "sha256": str(plate.get("sha256") or "").casefold(),
                },
                "character_refs": copy.deepcopy(character_refs),
                "prompt": _block_prompt(excerpt, function),
                "negative_prompt": _negative_prompt(),
                "audio": {
                    "required": True,
                    "source": "elevenlabs_canonical_take",
                    "audio_block_id": str(raw_audio_block.get("audio_block_id") or f"audio-block-{index:03d}"),
                    "audio_path": str(raw_audio_block.get("audio_path") or ""),
                    "sha256": str(raw_audio_block.get("sha256") or "").casefold(),
                    "duration_s": float(raw_audio_block.get("duration_s") or 0),
                    "generate_audio": False,
                },
                "fit_policy": {
                    "source_duration_s": round(audio_end - audio_start, 6),
                    "provider_duration_s": 10.0,
                    "video_only_time_stretch": True,
                    "narration_trim_allowed": False,
                    "final_partial_block_allowed": index == len(audio_blocks) and (audio_end - audio_start) < 10.0,
                },
                "status": "planned",
                "render_eligible": False,
            }
        )
    core = {
        "schema_version": HIGGSFIELD_BLOCK_PLAN_VERSION,
        "coverage_plan_hash": str(coverage_payload.get("artifact_hash") or canonical_sha256(coverage_payload)),
        "generated_plate_batch_hash": str(batch.get("artifact_hash") or ""),
        "art_bible_hash": art_bible_hash,
        "storyboard_hash": storyboard_hash,
        "character_pack_hash": character_pack_hash,
        "coverage_slot_count": len(slots),
        "block_count": len(blocks),
        "timeline_duration_s": round(audio_duration, 6),
        "provider_duration_s": 10.0,
        "character_count": len(character_refs),
        "canonical_narration_hash": narration_payload["narration_hash"],
        "canonical_audio_hash": str(audio_payload.get("artifact_hash") or ""),
        "blocks": blocks,
        "policy": {
            "fixed_provider_blocks": True,
            "provider_duration_s": 10.0,
            "canonical_narration_owner": "storyboard_scene_narration",
            "narration_source": "canonical_elevenlabs_word_timings",
            "visual_coverage_scaled_to_audio": True,
            "provider_audio_disabled": True,
            "provider_output_render_eligible": False,
            "one_clear_action_per_block": True,
            "narration_trim_allowed": False,
            "local_remotion_assembly_authoritative": True,
        },
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def bind_canonical_audio_to_higgsfield_blocks(
    block_plan: Mapping[str, Any] | str | Path,
    canonical_audio: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    storyboard_hash: str = "",
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Create the existing block-audio manifest from canonical audio slices."""

    plan_raw = _load(block_plan, "Higgsfield block plan")
    plan = validate_higgsfield_blocks(
        plan_raw,
        job_root=job_root,
        expected_block_count=int(plan_raw.get("block_count") or 0),
        check_files=True,
    )
    from content.video_engine.src.services.history_narration import validate_canonical_audio

    audio = validate_canonical_audio(canonical_audio, job_root=job_root)
    audio_blocks = audio.get("blocks") or []
    if len(audio_blocks) != len(plan["blocks"]):
        raise HiggsfieldExplainerError(["canonical audio block count does not match Higgsfield blocks"])
    items: list[dict[str, Any]] = []
    root = Path(job_root).resolve()
    for block, audio_block in zip(plan["blocks"], audio_blocks):
        if int(audio_block.get("order") or 0) != int(block.get("order") or 0):
            raise HiggsfieldExplainerError([f"audio order does not match {block['block_id']}"])
        path = _resolve_local(str(audio_block.get("audio_path") or ""), root)
        if path is None:
            raise HiggsfieldExplainerError([f"audio path is outside the job for {block['block_id']}"])
        items.append(
            {
                "block_id": str(block["block_id"]),
                "audio_path": str(audio_block["audio_path"]),
                "words_path": str(audio.get("words_path") or ""),
                "sha256": str(audio_block["sha256"]),
                "duration_s": float(audio_block["duration_s"]),
                "narration_hash": str(block["narration_hash"]),
                "voice_id": str(audio.get("voice_id") or ""),
                "storyboard_hash": storyboard_hash or str(audio.get("storyboard_hash") or ""),
                "word_timings": list(audio_block.get("word_timings") or []),
                "canonical_narration_hash": str(audio.get("narration_hash") or ""),
                "cache_hit": bool(audio.get("cache_hit")),
                "cost_usd": 0.0,
            }
        )
    core = {
        "schema_version": ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION,
        "status": "ready",
        "provider": "elevenlabs",
        "episode_scope": "history-episode-1",
        "block_plan_hash": str(plan["artifact_hash"]),
        "storyboard_hash": storyboard_hash or str(audio.get("storyboard_hash") or ""),
        "voice_id": str(audio.get("voice_id") or ""),
        "narration_hashes": [str(block["narration_hash"]) for block in plan["blocks"]],
        "canonical_narration_hash": str(audio.get("narration_hash") or ""),
        "canonical_audio_manifest_hash": str(audio.get("artifact_hash") or ""),
        "missing_block_ids": [],
        "items": items,
        "cache_hits": int(bool(audio.get("cache_hit"))) * len(items),
        "cache_misses": 0 if audio.get("cache_hit") else len(items),
        "cost_usd": float(audio.get("cost_usd") or 0),
        "policy": {
            "matching_manifest_required": True,
            "older_job_audio_rejected": True,
            "canonical_audio_owner": "elevenlabs",
            "single_continuous_take_sliced_locally": True,
            "with_timestamps_required": True,
            "provider_video_audio_must_be_discarded": True,
        },
    }
    payload = {**core, "artifact_hash": canonical_sha256(core)}
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def validate_higgsfield_blocks(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_coverage_hash: str | None = None,
    expected_plate_batch_hash: str | None = None,
    expected_block_count: int | None = 60,
    check_files: bool = True,
) -> dict[str, Any]:
    payload = _load(value, "Higgsfield block plan")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != HIGGSFIELD_BLOCK_PLAN_VERSION:
        errors.append(f"schema_version must be {HIGGSFIELD_BLOCK_PLAN_VERSION}")
    if expected_coverage_hash and payload.get("coverage_plan_hash") != expected_coverage_hash:
        errors.append("coverage_plan_hash is stale")
    if expected_plate_batch_hash and payload.get("generated_plate_batch_hash") != expected_plate_batch_hash:
        errors.append("generated_plate_batch_hash is stale")
    blocks = payload.get("blocks")
    if not isinstance(blocks, list):
        errors.append("blocks must be an array")
        blocks = []
    if expected_block_count is not None and len(blocks) != expected_block_count:
        errors.append(f"blocks must contain exactly {expected_block_count} entries")
    seen_blocks: set[str] = set()
    seen_slots: set[str] = set()
    previous_end = 0.0
    for index, raw in enumerate(blocks):
        label = f"blocks[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        block = dict(raw)
        block_id = str(block.get("block_id") or "")
        if not _SAFE_ID.fullmatch(block_id) or block_id in seen_blocks:
            errors.append(f"{label}.block_id must be unique and safe")
        seen_blocks.add(block_id)
        if int(block.get("order") or 0) != index + 1:
            errors.append(f"{label}.order must be {index + 1}")
        slot_ids = block.get("coverage_slot_ids")
        if not isinstance(slot_ids, list) or not slot_ids or not all(isinstance(slot, str) for slot in slot_ids):
            errors.append(f"{label}.coverage_slot_ids must be a non-empty string array")
            slot_ids = []
        for slot_id in slot_ids:
            if slot_id in seen_slots:
                errors.append(f"{label} reuses coverage slot {slot_id!r}")
            seen_slots.add(slot_id)
        if float(block.get("provider_duration_s") or 0) != 10.0:
            errors.append(f"{label}.provider_duration_s must be exactly 10")
        if float(block.get("duration_s") or 0) <= 0:
            errors.append(f"{label}.duration_s must be positive")
        start = float(block.get("timeline_start_s") or 0)
        end = float(block.get("timeline_end_s") or 0)
        if start < previous_end - 0.00001 or end <= start:
            errors.append(f"{label} timeline is not contiguous and increasing")
        previous_end = end
        if block.get("render_eligible") is not False:
            errors.append(f"{label}.render_eligible must remain false")
        audio = block.get("audio")
        if not isinstance(audio, Mapping) or audio.get("generate_audio") is not False:
            errors.append(f"{label}.audio.generate_audio must be false")
        for field in ("prompt", "negative_prompt"):
            text = str(block.get(field) or "").casefold()
            if not text:
                errors.append(f"{label}.{field} is required")
            for term in _PROHIBITED:
                if term in text:
                    errors.append(f"{label}.{field} contains prohibited input {term!r}")
        plate = block.get("plate")
        if not isinstance(plate, Mapping):
            errors.append(f"{label}.plate is required")
            continue
        plate_path = str(plate.get("path") or "")
        resolved = _resolve_local(plate_path, root)
        if check_files and resolved is None:
            errors.append(f"{label}.plate.path must resolve inside the job")
        digest = str(plate.get("sha256") or "").casefold()
        if not _HEX64.fullmatch(digest):
            errors.append(f"{label}.plate.sha256 must be a SHA-256 digest")
        if resolved is not None and _HEX64.fullmatch(digest) and _sha256(resolved) != digest:
            errors.append(f"{label}.plate.sha256 is stale")
    if len(seen_slots) != int(payload.get("coverage_slot_count") or 0):
        errors.append("coverage_slot_count does not match block coverage")
    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256({key: val for key, val in payload.items() if key != "artifact_hash"})
    if declared_hash != actual_hash:
        errors.append("artifact_hash is stale")
    if errors:
        raise HiggsfieldExplainerError(errors)
    return {**payload, "blocks": blocks, "artifact_hash": actual_hash}


def _audio_item_path(item: Mapping[str, Any], key: str) -> str:
    return str(item.get(key) or "")


def validate_elevenlabs_block_audio_manifest(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    block_plan: Mapping[str, Any] | str | Path | None = None,
    expected_voice_id: str | None = None,
    expected_storyboard_hash: str | None = None,
    check_files: bool = True,
) -> dict[str, Any]:
    payload = _load(value, "ElevenLabs block audio manifest")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION:
        errors.append(f"schema_version must be {ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION}")
    if payload.get("provider") != "elevenlabs":
        errors.append("provider must be elevenlabs")
    if payload.get("episode_scope") != "history-episode-1":
        errors.append("episode_scope must be history-episode-1")
    plan_payload = _load(block_plan, "Higgsfield block plan") if block_plan is not None else None
    if plan_payload is not None and payload.get("block_plan_hash") != plan_payload.get("artifact_hash"):
        errors.append("block_plan_hash is stale")
    if plan_payload is not None:
        expected_narration_hashes = [
            str(block.get("narration_hash") or "")
            for block in plan_payload.get("blocks", [])
            if isinstance(block, Mapping)
        ]
        if payload.get("narration_hashes") != expected_narration_hashes:
            errors.append("narration_hashes do not match the block plan")
    if expected_voice_id and payload.get("voice_id") != expected_voice_id:
        errors.append("voice_id is stale or does not match the episode")
    if expected_storyboard_hash and payload.get("storyboard_hash") != expected_storyboard_hash:
        errors.append("storyboard_hash is stale")
    status = str(payload.get("status") or "")
    if status not in {"awaiting_audio", "ready"}:
        errors.append("status must be awaiting_audio or ready")
    items = payload.get("items")
    if not isinstance(items, list):
        errors.append("items must be an array")
        items = []
    expected_blocks = {
        str(block.get("block_id")): block
        for block in (plan_payload or {}).get("blocks", [])
        if isinstance(block, Mapping)
    }
    seen: set[str] = set()
    for index, raw in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = dict(raw)
        block_id = str(item.get("block_id") or "")
        if block_id in seen or not _SAFE_ID.fullmatch(block_id):
            errors.append(f"{label}.block_id must be unique and safe")
        seen.add(block_id)
        expected = expected_blocks.get(block_id)
        if expected is not None and item.get("narration_hash") != expected.get("narration_hash"):
            errors.append(f"{label}.narration_hash does not match the block")
        digest = str(item.get("sha256") or "").casefold()
        if not _HEX64.fullmatch(digest):
            errors.append(f"{label}.sha256 must be a SHA-256 digest")
        audio_path = _audio_item_path(item, "audio_path")
        resolved = _resolve_local(audio_path, root)
        if check_files and resolved is None:
            errors.append(f"{label}.audio_path must resolve inside the job")
        if resolved is not None and _HEX64.fullmatch(digest) and _sha256(resolved) != digest:
            errors.append(f"{label}.sha256 is stale")
        words_path = _audio_item_path(item, "words_path")
        if words_path:
            words_resolved = _resolve_local(words_path, root)
            if check_files and words_resolved is None:
                errors.append(f"{label}.words_path must resolve inside the job")
        if float(item.get("duration_s") or 0) <= 0:
            errors.append(f"{label}.duration_s must be positive")
        if expected_storyboard_hash and item.get("storyboard_hash") != expected_storyboard_hash:
            errors.append(f"{label}.storyboard_hash is stale")
        if payload.get("voice_id") and item.get("voice_id") != payload.get("voice_id"):
            errors.append(f"{label}.voice_id does not match the manifest")
    if status == "ready" and expected_blocks and set(expected_blocks) != seen:
        errors.append("ready audio manifest does not cover every Higgsfield block")
    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256({key: val for key, val in payload.items() if key != "artifact_hash"})
    if declared_hash != actual_hash:
        errors.append("artifact_hash is stale")
    if errors:
        raise HiggsfieldExplainerError(errors)
    return {**payload, "items": items, "artifact_hash": actual_hash}


def resolve_elevenlabs_audio(
    block_plan: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    manifest_path: str | Path | None = None,
    storyboard_hash: str = "",
    voice_id: str = "",
    allow_synthesis: bool = False,
    synthesizer: Any | None = None,
    synthesis_config: Any | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Resolve a matching local manifest, or return a fail-closed pending manifest.

    Synthesis is opt-in.  The caller must explicitly set ``allow_synthesis``;
    automated tests and dry runs never cross the ElevenLabs boundary.
    """

    plan = _load(block_plan, "Higgsfield block plan")
    plan = validate_higgsfield_blocks(plan, job_root=job_root, check_files=True)
    root = Path(job_root).resolve()
    voice_id = voice_id or (os.environ.get("ELEVENLABS_VOICE_ID") or "").strip()
    if manifest_path is not None and Path(manifest_path).is_file():
        existing_raw = _load(manifest_path, "ElevenLabs block audio manifest")
        existing_manifest = validate_elevenlabs_block_audio_manifest(
            manifest_path,
            job_root=root,
            block_plan=plan,
            expected_voice_id=(
                None
                if allow_synthesis and existing_raw.get("status") == "awaiting_audio"
                else voice_id or None
            ),
            expected_storyboard_hash=storyboard_hash or None,
            check_files=True,
        )
        if existing_manifest.get("status") == "ready" or not allow_synthesis:
            return existing_manifest
    if allow_synthesis:
        if not storyboard_hash:
            raise HiggsfieldExplainerError(["storyboard_hash is required before synthesis"])
        from content.video_engine.src.services.audio_synth import (
            AudioSynthService,
            ElevenLabsConfig,
        )

        service = synthesizer or AudioSynthService()
        config = synthesis_config or getattr(service, "config", None) or ElevenLabsConfig.from_env()
        resolved_voice_id = voice_id or str(getattr(config, "voice_id", "") or "")
        if not resolved_voice_id:
            raise HiggsfieldExplainerError(
                ["an ElevenLabs voice ID is required before block synthesis"]
            )
        audio_dir = root / "audio" / "higgsfield"
        cache_dir = root / "audio" / ".cache"
        audio_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        items: list[dict[str, Any]] = []
        total_cost = 0.0
        cache_hits = 0
        for index, block in enumerate(plan["blocks"], start=1):
            try:
                result = service.synthesize_scene(
                    index,
                    str(block["narration_excerpt"]),
                    voice_id=resolved_voice_id,
                    settings={},
                    audio_dir=audio_dir,
                    cache_dir=cache_dir,
                    config=config,
                )
            except Exception as exc:  # noqa: BLE001 - provider adapter boundary
                raise HiggsfieldExplainerError(
                    [f"ElevenLabs synthesis failed for {block['block_id']}: {exc}"]
                ) from exc
            target_audio = audio_dir / f"block_{index:03d}.mp3"
            target_words = audio_dir / f"block_{index:03d}.words.json"
            target_audio.write_bytes(Path(result.audio_path).read_bytes())
            words_payload: dict[str, Any] = {}
            if Path(result.words_path).is_file():
                try:
                    words_payload = json.loads(Path(result.words_path).read_text(encoding="utf-8"))
                except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                    raise HiggsfieldExplainerError(
                        [f"ElevenLabs words artifact is invalid for {block['block_id']}: {exc}"]
                    ) from exc
            target_words.write_text(
                json.dumps(
                    {
                        "block_id": block["block_id"],
                        "duration_s": float(result.duration_s),
                        "words": list(words_payload.get("words") or []),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            # AudioSynthService writes scene_* names by contract.  The block
            # manifest is the canonical handoff, so remove those temporary
            # aliases after copying rather than leaving ambiguous duplicates
            # beside the episode's block artifacts.
            for temporary in (Path(result.audio_path), Path(result.words_path)):
                if temporary.resolve() not in {target_audio.resolve(), target_words.resolve()}:
                    try:
                        temporary.unlink()
                    except FileNotFoundError:
                        pass
            relative_audio = target_audio.relative_to(root).as_posix()
            relative_words = target_words.relative_to(root).as_posix()
            item = {
                "block_id": block["block_id"],
                "audio_path": relative_audio,
                "words_path": relative_words,
                "sha256": _sha256(target_audio),
                "duration_s": float(result.duration_s),
                "narration_hash": str(block["narration_hash"]),
                "voice_id": resolved_voice_id,
                "storyboard_hash": storyboard_hash,
                "word_timings": list(words_payload.get("words") or []),
                "cache_hit": bool(result.cache_hit),
                "cost_usd": float(result.cost_usd),
            }
            items.append(item)
            total_cost += float(result.cost_usd)
            cache_hits += int(bool(result.cache_hit))
        core = {
            "schema_version": ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION,
            "status": "ready",
            "provider": "elevenlabs",
            "episode_scope": "history-episode-1",
            "block_plan_hash": str(plan["artifact_hash"]),
            "storyboard_hash": storyboard_hash,
            "voice_id": resolved_voice_id,
            "narration_hashes": [str(block["narration_hash"]) for block in plan["blocks"]],
            "missing_block_ids": [],
            "items": items,
            "cache_hits": cache_hits,
            "cache_misses": len(items) - cache_hits,
            "cost_usd": round(total_cost, 8),
            "policy": {
                "matching_manifest_required": True,
                "older_job_audio_rejected": True,
                "canonical_audio_owner": "elevenlabs",
                "with_timestamps_required": True,
                "provider_video_audio_must_be_discarded": True,
            },
        }
        payload = {**core, "artifact_hash": canonical_sha256(core)}
        if output_path is not None:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload
    missing = [str(block["block_id"]) for block in plan["blocks"]]
    core = {
        "schema_version": ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION,
        "status": "awaiting_audio",
        "provider": "elevenlabs",
        "episode_scope": "history-episode-1",
        "block_plan_hash": str(plan["artifact_hash"]),
        "storyboard_hash": storyboard_hash,
        "voice_id": voice_id,
        "narration_hashes": [str(block["narration_hash"]) for block in plan["blocks"]],
        "missing_block_ids": missing,
        "items": [],
        "policy": {
            "matching_manifest_required": True,
            "older_job_audio_rejected": True,
            "canonical_audio_owner": "elevenlabs",
            "with_timestamps_required": True,
            "provider_video_audio_must_be_discarded": True,
        },
    }
    payload = {**core, "artifact_hash": canonical_sha256(core)}
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


DEFAULT_MODEL_CAPABILITIES: dict[str, dict[str, Any]] = {
    "seedance_2_0": {
        "supports_audio_references": True,
        "audio_reference_limit": 3,
        "requires_visual_reference": True,
        "durations_s": [5, 10],
        "live_contract_confirmed": False,
    },
    "wan2_6": {
        "supports_audio_references": True,
        "audio_reference_limit": 3,
        "requires_visual_reference": True,
        "durations_s": [5, 10, 15],
        "live_contract_confirmed": False,
    },
}


def preflight_higgsfield_models(
    capabilities: Mapping[str, Any] | None = None,
    *,
    preferred_model: str = "seedance_2_0",
    duration_s: float = 10.0,
    audio_reference_count: int = 1,
    has_visual_reference: bool = True,
) -> dict[str, Any]:
    """Select Seedance or Wan without submitting a task.

    With no live capability snapshot the result is intentionally marked as
    requiring operator confirmation.  This prevents a stale catalog from
    silently turning into a paid submission.
    """

    source = capabilities or DEFAULT_MODEL_CAPABILITIES
    order = [preferred_model] + [model for model in ("wan2_6", "seedance_2_0") if model != preferred_model]
    errors: list[str] = []
    fallback_reason = ""
    selected: str | None = None
    for model in order:
        raw = source.get(model) if isinstance(source, Mapping) else None
        if not isinstance(raw, Mapping):
            errors.append(f"{model}: capability snapshot is missing")
            continue
        if raw.get("live_contract_confirmed") is False and capabilities is not None:
            errors.append(f"{model}: live contract is not confirmed")
            continue
        if raw.get("supports_audio_references") is not True:
            errors.append(f"{model}: audio references are unsupported")
            continue
        if audio_reference_count > int(raw.get("audio_reference_limit") or 0):
            errors.append(f"{model}: audio reference limit is too low")
            continue
        if raw.get("requires_visual_reference") is True and not has_visual_reference:
            errors.append(f"{model}: a visual reference is required")
            continue
        durations = {float(value) for value in (raw.get("durations_s") or [])}
        if float(duration_s) not in durations:
            errors.append(f"{model}: {duration_s:g}s is not a supported duration")
            continue
        selected = model
        if model != preferred_model:
            fallback_reason = "; ".join(errors)
        break
    if selected is None:
        raise HiggsfieldExplainerError(errors or ["no audio-capable Higgsfield model is available"])
    return {
        "valid": True,
        "selected_model": selected,
        "preferred_model": preferred_model,
        "fallback_reason": fallback_reason,
        "duration_s": float(duration_s),
        "audio_reference_count": audio_reference_count,
        "generate_audio": False,
        "live_contract_confirmed": bool(
            isinstance(source.get(selected), Mapping)
            and source[selected].get("live_contract_confirmed") is True
        ),
        "requires_operator_live_preflight": not bool(
            isinstance(source.get(selected), Mapping)
            and source[selected].get("live_contract_confirmed") is True
        ),
        "errors": errors,
    }


def compile_higgsfield_job_manifest(
    block_plan: Mapping[str, Any] | str | Path,
    audio_manifest: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    project_root: str | Path | None = None,
    character_pack: Mapping[str, Any] | str | Path | None = None,
    model_capabilities: Mapping[str, Any] | None = None,
    preferred_model: str = "seedance_2_0",
    storyboard_hash: str = "",
    art_bible_hash: str = "",
) -> dict[str, Any]:
    """Create a quarantined provider manifest; never submits a task."""

    plan_raw = _load(block_plan, "Higgsfield block plan")
    plan = validate_higgsfield_blocks(
        plan_raw,
        job_root=job_root,
        expected_block_count=int(plan_raw.get("block_count") or 0),
        check_files=True,
    )
    audio = validate_elevenlabs_block_audio_manifest(
        audio_manifest,
        job_root=job_root,
        block_plan=plan,
        expected_storyboard_hash=storyboard_hash or None,
        check_files=audio_manifest.get("status") == "ready" if isinstance(audio_manifest, Mapping) else True,
    )
    preflight = preflight_higgsfield_models(
        model_capabilities,
        preferred_model=preferred_model,
        duration_s=10.0,
        audio_reference_count=1,
        has_visual_reference=True,
    )
    character_refs, character_pack_hash = _character_refs(character_pack)
    root = Path(job_root).resolve()
    asset_root = Path(project_root or job_root).resolve()
    for ref in character_refs:
        path_text = str(ref.get("path") or "")
        if path_text:
            resolved = _resolve_local(path_text, asset_root)
            if resolved is None:
                raise HiggsfieldExplainerError(
                    [f"character {ref['character_id']} path must resolve inside the approved asset root"]
                )
            digest = str(ref.get("sha256") or "").casefold()
            if not _HEX64.fullmatch(digest) or _sha256(resolved) != digest:
                raise HiggsfieldExplainerError(
                    [f"character {ref['character_id']} sha256 is missing or stale"]
                )
    audio_by_block = {
        str(item.get("block_id")): item
        for item in audio.get("items", [])
        if isinstance(item, Mapping)
    }
    items: list[dict[str, Any]] = []
    for block in plan["blocks"]:
        block_id = str(block["block_id"])
        audio_item = audio_by_block.get(block_id)
        if audio_item is not None:
            audio_path = _resolve_local(str(audio_item.get("audio_path") or ""), root)
            if audio_path is None:
                raise HiggsfieldExplainerError([f"{block_id} audio path is outside the job"])
        item = {
            "block_id": block_id,
            "order": int(block["order"]),
            "duration_s": 10.0,
            "plate_reference": dict(block["plate"]),
            "character_references": copy.deepcopy(character_refs),
            "audio_reference": {
                "audio_path": str(audio_item.get("audio_path")) if audio_item else "",
                "sha256": str(audio_item.get("sha256")) if audio_item else "",
                "duration_s": float(audio_item.get("duration_s") or 0) if audio_item else 0.0,
                "narration_hash": str(audio_item.get("narration_hash") or "") if audio_item else "",
                "voice_id": str(audio_item.get("voice_id") or "") if audio_item else "",
            },
            "narration_excerpt": str(block["narration_excerpt"]),
            "claim_refs": list(block.get("claim_refs") or []),
            "citation_refs": list(block.get("citation_refs") or []),
            "prompt": str(block["prompt"]),
            "negative_prompt": str(block["negative_prompt"]),
            "settings": {
                "generate_audio": False,
                "audio_reference_count": 1,
                "visual_reference_required": True,
                "model": preflight["selected_model"],
            },
            "task_id": None,
            "retry_count": 0,
            "status": "awaiting_audio" if audio.get("status") != "ready" else "planned",
            "provider_output_path": "",
            "render_eligible": False,
        }
        items.append(item)
    core = {
        "schema_version": HIGGSFIELD_JOB_MANIFEST_VERSION,
        "status": "awaiting_audio" if audio.get("status") != "ready" else "planned",
        "episode_id": "history-of-bjj-episode-1",
        "model": preflight["selected_model"],
        "model_preflight": preflight,
        "block_plan_hash": str(plan["artifact_hash"]),
        "audio_manifest_hash": str(audio.get("artifact_hash") or ""),
        "storyboard_hash": storyboard_hash,
        "art_bible_hash": art_bible_hash,
        "character_pack_hash": character_pack_hash,
        "block_count": len(items),
        "items": items,
        "policy": {
            "preferred_model": preferred_model,
            "fallback_model": "wan2_6",
            "provider_audio_disabled": True,
            "canonical_audio_owner": "elevenlabs",
            "provider_output_render_eligible": False,
            "no_duplicate_running_tasks": True,
            "submit_requires_bounded_authorization": True,
            "local_remotion_assembly_authoritative": True,
        },
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_higgsfield_job_manifest(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_block_plan_hash: str | None = None,
    expected_audio_manifest_hash: str | None = None,
    expected_model: str | None = None,
) -> dict[str, Any]:
    payload = _load(value, "Higgsfield job manifest")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != HIGGSFIELD_JOB_MANIFEST_VERSION:
        errors.append(f"schema_version must be {HIGGSFIELD_JOB_MANIFEST_VERSION}")
    if expected_block_plan_hash and payload.get("block_plan_hash") != expected_block_plan_hash:
        errors.append("block_plan_hash is stale")
    if expected_audio_manifest_hash and payload.get("audio_manifest_hash") != expected_audio_manifest_hash:
        errors.append("audio_manifest_hash is stale")
    if expected_model and payload.get("model") != expected_model:
        errors.append("model does not match preflight")
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != int(payload.get("block_count") or 0):
        errors.append("items must match block_count")
        items = items if isinstance(items, list) else []
    seen_blocks: set[str] = set()
    seen_tasks: set[str] = set()
    for index, raw in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        block_id = str(raw.get("block_id") or "")
        if not _SAFE_ID.fullmatch(block_id) or block_id in seen_blocks:
            errors.append(f"{label}.block_id must be unique and safe")
        seen_blocks.add(block_id)
        if int(raw.get("order") or 0) != index + 1:
            errors.append(f"{label}.order must be {index + 1}")
        if float(raw.get("duration_s") or 0) != 10.0:
            errors.append(f"{label}.duration_s must be exactly 10")
        settings = raw.get("settings")
        if not isinstance(settings, Mapping) or settings.get("generate_audio") is not False:
            errors.append(f"{label}.settings.generate_audio must be false")
        plate = raw.get("plate_reference")
        if not isinstance(plate, Mapping):
            errors.append(f"{label}.plate_reference is required")
        else:
            plate_path = _resolve_local(str(plate.get("path") or ""), root)
            if plate_path is None:
                errors.append(f"{label}.plate_reference.path must resolve inside the job")
            digest = str(plate.get("sha256") or "").casefold()
            if plate_path is not None and _HEX64.fullmatch(digest) and _sha256(plate_path) != digest:
                errors.append(f"{label}.plate_reference.sha256 is stale")
        audio_ref = raw.get("audio_reference")
        if not isinstance(audio_ref, Mapping):
            errors.append(f"{label}.audio_reference is required")
        elif str(audio_ref.get("audio_path") or ""):
            audio_path = _resolve_local(str(audio_ref.get("audio_path")), root)
            if audio_path is None:
                errors.append(f"{label}.audio_reference.audio_path must resolve inside the job")
        for field in ("prompt", "negative_prompt"):
            text = str(raw.get(field) or "").casefold()
            for term in _PROHIBITED:
                if term in text:
                    errors.append(f"{label}.{field} contains prohibited input {term!r}")
        task_id = str(raw.get("task_id") or "")
        if task_id:
            if task_id in seen_tasks:
                errors.append(f"{label}.task_id is assigned to more than one block")
            seen_tasks.add(task_id)
        if raw.get("render_eligible") is not False:
            errors.append(f"{label}.render_eligible must remain false")
    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256({key: val for key, val in payload.items() if key != "artifact_hash"})
    if declared_hash != actual_hash:
        errors.append("artifact_hash is stale")
    if errors:
        raise HiggsfieldExplainerError(errors)
    return {**payload, "items": items, "artifact_hash": actual_hash}


def record_higgsfield_task(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    block_id: str,
    task_id: str,
    status: str = "submitted",
) -> dict[str, Any]:
    """Bind one provider task ID, rejecting duplicate running submissions."""

    payload = validate_higgsfield_job_manifest(value, job_root=job_root)
    if not task_id.strip():
        raise HiggsfieldExplainerError(["task_id is required"])
    target = next((item for item in payload["items"] if item.get("block_id") == block_id), None)
    if target is None:
        raise HiggsfieldExplainerError([f"unknown block_id {block_id!r}"])
    for item in payload["items"]:
        existing = str(item.get("task_id") or "")
        if existing == task_id and item.get("block_id") != block_id:
            raise HiggsfieldExplainerError([f"task_id {task_id!r} is already bound to another block"])
    existing = str(target.get("task_id") or "")
    if existing and existing != task_id and str(target.get("status")) in {"submitted", "running"}:
        raise HiggsfieldExplainerError([f"{block_id} already has a running task {existing!r}"])
    target["task_id"] = task_id
    target["status"] = status
    core = {key: val for key, val in payload.items() if key != "artifact_hash"}
    return {**core, "artifact_hash": canonical_sha256(core)}


def record_higgsfield_output(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    block_id: str,
    output_path: str | Path,
    status: str = "complete",
) -> dict[str, Any]:
    """Bind a downloaded provider clip while keeping it quarantined."""

    payload = validate_higgsfield_job_manifest(value, job_root=job_root)
    root = Path(job_root).resolve()
    target = next((item for item in payload["items"] if item.get("block_id") == block_id), None)
    if target is None:
        raise HiggsfieldExplainerError([f"unknown block_id {block_id!r}"])
    try:
        resolved = Path(output_path).resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise HiggsfieldExplainerError(["provider output must be a local file inside the job root"]) from exc
    if resolved.suffix.casefold() not in {".mp4", ".webm", ".mov"}:
        raise HiggsfieldExplainerError(["provider output must be a video file"])
    target["provider_output_path"] = resolved.relative_to(root).as_posix()
    target["provider_output_sha256"] = _sha256(resolved)
    target["status"] = status
    target["render_eligible"] = False
    core = {key: val for key, val in payload.items() if key != "artifact_hash"}
    return {**core, "artifact_hash": canonical_sha256(core)}


def compile_higgsfield_local_assembly(
    job_manifest: Mapping[str, Any] | str | Path,
    audio_manifest: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Bind completed silent clips to canonical ElevenLabs audio for Remotion.

    This is intentionally unavailable until every provider item has a local,
    human-promotable output.  It prevents a provider's generated audio track
    from entering the final mix and keeps the local editor authoritative.
    """

    job = validate_higgsfield_job_manifest(job_manifest, job_root=job_root)
    audio = validate_elevenlabs_block_audio_manifest(
        audio_manifest,
        job_root=job_root,
        check_files=True,
    )
    if audio.get("status") != "ready":
        raise HiggsfieldExplainerError(["local assembly requires a ready ElevenLabs audio manifest"])
    root = Path(job_root).resolve()
    audio_by_block = {
        str(item.get("block_id")): item
        for item in audio.get("items", [])
        if isinstance(item, Mapping)
    }
    clips: list[dict[str, Any]] = []
    for item in job["items"]:
        block_id = str(item["block_id"])
        if str(item.get("status") or "") not in {"complete", "promoted"}:
            raise HiggsfieldExplainerError([f"{block_id} has no completed Higgsfield clip"])
        video_path = _resolve_local(str(item.get("provider_output_path") or ""), root)
        if video_path is None:
            raise HiggsfieldExplainerError([f"{block_id} provider output is not a local file"])
        video_digest = str(item.get("provider_output_sha256") or "").casefold()
        if not _HEX64.fullmatch(video_digest) or _sha256(video_path) != video_digest:
            raise HiggsfieldExplainerError([f"{block_id} provider output hash is missing or stale"])
        audio_item = audio_by_block.get(block_id)
        if audio_item is None:
            raise HiggsfieldExplainerError([f"{block_id} has no canonical ElevenLabs audio"])
        audio_path = _resolve_local(str(audio_item.get("audio_path") or ""), root)
        if audio_path is None:
            raise HiggsfieldExplainerError([f"{block_id} audio is not a local file"])
        clips.append(
            {
                "block_id": block_id,
                "order": int(item["order"]),
                "video_path": str(item["provider_output_path"]),
                "video_sha256": video_digest,
                "provider_duration_s": 10.0,
                "audio_path": str(audio_item["audio_path"]),
                "audio_sha256": str(audio_item["sha256"]),
                "audio_duration_s": float(audio_item["duration_s"]),
                "provider_audio_discarded": True,
            }
        )
    core = {
        "schema_version": HIGGSFIELD_LOCAL_ASSEMBLY_MANIFEST_VERSION,
        "status": "ready_for_local_edit",
        "job_manifest_hash": str(job["artifact_hash"]),
        "audio_manifest_hash": str(audio["artifact_hash"]),
        "clip_count": len(clips),
        "clips": sorted(clips, key=lambda clip: int(clip["order"])),
        "assembly": {
            "editor": "remotion",
            "narration_owner": "elevenlabs",
            "captions_owner": "remotion",
            "citations_owner": "remotion",
            "credits_owner": "remotion",
            "provider_audio_discarded": True,
            "vertical_reframes_local": True,
        },
        "render_eligible": False,
    }
    payload = {**core, "artifact_hash": canonical_sha256(core)}
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


class HiggsfieldCli:
    """Read-only CLI adapter used for capability preflight.

    Generation submission intentionally is not exposed here.  The caller
    must build the manifest, obtain bounded authorization, and then use an
    explicitly reviewed provider adapter.
    """

    def __init__(self, executable: str | None = None, runner: Callable[..., Any] | None = None):
        self.executable = executable or os.environ.get("HIGGSFIELD_CLI") or shutil.which("higgsfield")
        self._runner = runner or subprocess.run

    @property
    def installed(self) -> bool:
        return bool(self.executable)

    def _run(self, args: list[str]) -> dict[str, Any]:
        if not self.executable:
            raise HiggsfieldExplainerError(["higgsfield CLI is not installed"])
        result = self._runner(
            [self.executable, *args, "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if int(getattr(result, "returncode", 1)) != 0:
            raise HiggsfieldExplainerError([
                f"higgsfield CLI failed ({getattr(result, 'returncode', 1)}): "
                f"{str(getattr(result, 'stderr', '') or '').strip()[:300]}"
            ])
        try:
            payload = json.loads(str(getattr(result, "stdout", "") or "{}"))
        except json.JSONDecodeError as exc:
            raise HiggsfieldExplainerError(["higgsfield CLI returned non-JSON output"] ) from exc
        if not isinstance(payload, dict):
            raise HiggsfieldExplainerError(["higgsfield CLI JSON output must be an object"])
        return payload

    def auth_status(self) -> dict[str, Any]:
        if not self.executable:
            raise HiggsfieldExplainerError(["higgsfield CLI is not installed"])
        result = self._runner(
            [self.executable, "auth", "token"],
            capture_output=True,
            text=True,
            check=False,
        )
        # The token command returns a secret on success.  Never return or log
        # it; the adapter only exposes the boolean needed for preflight.
        return {
            "authenticated": int(getattr(result, "returncode", 1)) == 0
            and bool(str(getattr(result, "stdout", "") or "").strip())
        }

    def account_status(self) -> dict[str, Any]:
        return self._run(["account", "status"])

    def model_get(self, model: str) -> dict[str, Any]:
        return self._run(["model", "get", model])


__all__ = [
    "DEFAULT_MODEL_CAPABILITIES",
    "ELEVENLABS_BLOCK_AUDIO_MANIFEST_VERSION",
    "HIGGSFIELD_BLOCK_PLAN_VERSION",
    "HIGGSFIELD_JOB_MANIFEST_VERSION",
    "HIGGSFIELD_LOCAL_ASSEMBLY_MANIFEST_VERSION",
    "HiggsfieldCli",
    "HiggsfieldExplainerError",
    "bind_canonical_audio_to_higgsfield_blocks",
    "compile_audio_aligned_higgsfield_blocks",
    "compile_higgsfield_blocks",
    "compile_higgsfield_job_manifest",
    "compile_higgsfield_local_assembly",
    "preflight_higgsfield_models",
    "record_higgsfield_task",
    "record_higgsfield_output",
    "resolve_elevenlabs_audio",
    "validate_elevenlabs_block_audio_manifest",
    "validate_higgsfield_blocks",
    "validate_higgsfield_job_manifest",
]
