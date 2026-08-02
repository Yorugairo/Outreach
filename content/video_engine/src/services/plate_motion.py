"""Image-to-video handoff for generated documentary plates.

The plan is provider-neutral at the editorial boundary but intentionally
matches the existing Magnific/Kling adapter contract.  It turns each reviewed
generated block into one short, silent motion request.  Captions, citations,
credits, and narration remain local editor concerns.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from content.video_engine.src.services.generated_block_images import (
    GeneratedBlockImageError,
    validate_generated_block_batch,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


PLATE_MOTION_PLAN_VERSION = "plate_motion_plan.v1"
PLATE_MOTION_MANIFEST_VERSION = "magnific_video_manifest.v1"
MAGNIFIC_VIDEO_PLAN_VERSION = "magnific_video_plan.v1"
_HEX64 = re.compile(r"^[a-f0-9]{64}$")
_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_PROHIBITED = (
    "in the style of",
    "style of",
    "youtube.com",
    "youtu.be",
    "source frame",
    "creator name",
)


class PlateMotionError(ValueError):
    """Raised when a plate-to-motion handoff is unsafe or incomplete."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PlateMotionError([f"{label} is not valid JSON: {exc}"]) from exc
    if not isinstance(payload, dict):
        raise PlateMotionError([f"{label} must contain an object"])
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_remote(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc)


def _resolve(path_text: str, root: Path) -> Path | None:
    raw = Path(path_text)
    if raw.is_absolute() or _is_remote(path_text):
        return None
    try:
        resolved = (root / raw).resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _motion_recipe(function: str) -> str:
    return {
        "artifact_cold_open": "locked_push_and_reveal",
        "archival_portrait": "portrait_breath",
        "illustrated_reconstruction": "single_action_parallax",
        "document_quote_closeup": "page_turn_or_highlight",
        "migration_map_timeline": "route_trace",
        "lineage_graph": "branch_reveal",
        "concept_mechanics_cutaway": "single_metaphor_motion",
        "chapter_cta": "title_card_breath",
    }.get(function, "restrained_editorial_breath")


def _prompt(block: Mapping[str, Any]) -> str:
    function = str(block.get("function") or "editorial_scene")
    excerpt = " ".join(str(block.get("narration_excerpt") or "").split())
    recipe = _motion_recipe(function)
    return (
        "Animate this supplied original illustrated plate as a clean, silent, "
        "narration-matched editorial shot. Preserve the exact woodblock-informed "
        "palette, character ownership, silhouettes, framing, and paper texture. "
        f"Use one restrained action only: {recipe}. "
        f"The narration beat is {excerpt!r}; use it only to choose emphasis and "
        "timing, never to render words, dates, maps, citations, logos, or new "
        "historical facts. Keep the horizon and plate geometry stable, use a "
        "smooth 24fps motion path, and end in a readable held pose for editorial "
        "captions."
    )


def compile_plate_motion_plan(
    batch: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_plan: Mapping[str, Any] | str | Path | None = None,
    provider: str = "magnific",
    model: str = "kling-v2-5-pro",
) -> dict[str, Any]:
    """Create one image-to-video request per generated image block."""

    root = Path(job_root).resolve()
    try:
        validated = validate_generated_block_batch(
            batch,
            job_root=root,
            expected_plan=expected_plan,
        )
    except GeneratedBlockImageError as exc:
        raise PlateMotionError(exc.errors) from exc

    items: list[dict[str, Any]] = []
    for block in validated["blocks"]:
        source = str(block["path"])
        item = {
            "id": str(block["block_id"]),
            "source_path": source,
            "source_sha256": str(block["sha256"]),
            "prompt": _prompt(block),
            "negative_prompt": (
                "camera shake, handheld drift, background wobble, scene replacement, "
                "new characters, costume change, face change, extra limbs, unreadable "
                "text, logos, watermarks, photorealism, grappling choreography"
            ),
            "duration": "10",
            "cfg_scale": 0.7,
            "coverage_slot_ids": list(block["coverage_slot_ids"]),
            "narration_excerpt": str(block["narration_excerpt"]),
            "function": str(block.get("function") or "editorial_scene"),
            "motion_recipe": _motion_recipe(str(block.get("function") or "")),
            "target_duration_s": float(block.get("duration_s") or 0),
            "render_eligible": False,
            "status": "planned",
        }
        items.append(item)

    core = {
        "schema_version": PLATE_MOTION_PLAN_VERSION,
        "provider": provider,
        "model": model,
        "source_batch_hash": str(validated.get("artifact_hash") or ""),
        "block_count": len(items),
        "items": items,
        "policy": {
            "one_clip_per_generated_block": True,
            "provider_output_is_silent": True,
            "provider_output_render_eligible": False,
            "narration_caption_citation_owner": "remotion",
            "motion_is_optional_until_provider_approval": True,
        },
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_plate_motion_plan(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_batch_hash: str | None = None,
) -> dict[str, Any]:
    """Validate the local image-to-video plan before any paid provider call."""

    payload = _load(value, "plate motion plan")
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != PLATE_MOTION_PLAN_VERSION:
        errors.append(f"schema_version must be {PLATE_MOTION_PLAN_VERSION}")
    if not str(payload.get("provider") or "").strip():
        errors.append("provider is required")
    if not str(payload.get("model") or "").strip():
        errors.append("model is required")
    if expected_batch_hash and payload.get("source_batch_hash") != expected_batch_hash:
        errors.append("source_batch_hash is stale")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must contain at least one plate")
        items = []
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = dict(raw)
        item_id = str(item.get("id") or "")
        if not _SAFE_ID.fullmatch(item_id):
            errors.append(f"{label}.id must be a safe lowercase ID")
        if item_id in seen:
            errors.append(f"{label}.id duplicates {item_id!r}")
        seen.add(item_id)
        path_text = str(item.get("source_path") or "")
        resolved = _resolve(path_text, root)
        if not path_text or resolved is None:
            errors.append(f"{label}.source_path must resolve inside the job")
        declared = str(item.get("source_sha256") or "").casefold()
        if not _HEX64.fullmatch(declared):
            errors.append(f"{label}.source_sha256 must be a SHA-256 digest")
        if resolved is not None and _HEX64.fullmatch(declared) and _sha256(resolved) != declared:
            errors.append(f"{label}.source_sha256 is stale")
        prompt = str(item.get("prompt") or "")
        negative = str(item.get("negative_prompt") or "")
        if not prompt:
            errors.append(f"{label}.prompt is required")
        for prompt_label, text in (("prompt", prompt), ("negative_prompt", negative)):
            lowered = text.casefold()
            for term in _PROHIBITED:
                if term in lowered:
                    errors.append(f"{label}.{prompt_label} contains prohibited input {term!r}")
        if item.get("render_eligible") is not False:
            errors.append(f"{label}.render_eligible must remain false")
        if str(item.get("duration") or "") not in {"5", "10"}:
            errors.append(f"{label}.duration must be 5 or 10")
        normalized.append({**item, "source_path": path_text, "source_sha256": declared})

    declared_hash = str(payload.get("artifact_hash") or "").casefold()
    actual_hash = canonical_sha256({key: value for key, value in payload.items() if key != "artifact_hash"})
    if declared_hash != actual_hash:
        errors.append("artifact_hash is stale")
    if errors:
        raise PlateMotionError(errors)
    return {**payload, "items": normalized, "artifact_hash": actual_hash}


def to_magnific_video_plan(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
    expected_batch_hash: str | None = None,
) -> dict[str, Any]:
    """Adapt the validated editorial plan to the existing Magnific adapter."""

    plan = validate_plate_motion_plan(
        value,
        job_root=job_root,
        expected_batch_hash=expected_batch_hash,
    )
    core = {
        "schema_version": MAGNIFIC_VIDEO_PLAN_VERSION,
        "provider": "magnific",
        "model": str(plan["model"]),
        "source_batch_hash": str(plan["source_batch_hash"]),
        "items": [
            {
                "id": item["id"],
                "source_path": item["source_path"],
                "source_sha256": item["source_sha256"],
                "prompt": item["prompt"],
                "negative_prompt": item["negative_prompt"],
                "duration": item["duration"],
                "cfg_scale": item["cfg_scale"],
            }
            for item in plan["items"]
        ],
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_plate_motion_manifest(
    value: Mapping[str, Any] | str | Path,
    *,
    job_root: str | Path,
) -> dict[str, Any]:
    """Validate a completed Magnific manifest and resolve quarantined clips."""

    payload = _load(value, "plate motion manifest")
    manifest_path = Path(value).resolve() if not isinstance(value, Mapping) else None
    base = manifest_path.parent if manifest_path is not None else Path(job_root).resolve()
    root = Path(job_root).resolve()
    errors: list[str] = []
    if payload.get("schema_version") != PLATE_MOTION_MANIFEST_VERSION:
        errors.append(f"schema_version must be {PLATE_MOTION_MANIFEST_VERSION}")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        errors.append("motion manifest requires items")
        items = []
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(raw, Mapping):
            errors.append(f"{label} must be an object")
            continue
        item = dict(raw)
        item_id = str(item.get("id") or "")
        if not _SAFE_ID.fullmatch(item_id) or item_id in seen:
            errors.append(f"{label}.id must be unique and safe")
        seen.add(item_id)
        path_text = str(item.get("output_path") or "")
        resolved: Path | None = None
        if path_text and not Path(path_text).is_absolute() and not _is_remote(path_text):
            try:
                candidate = (base / path_text).resolve(strict=True)
                candidate.relative_to(root)
            except (OSError, RuntimeError, ValueError):
                candidate = None
            if candidate is not None and candidate.is_file():
                resolved = candidate
        if resolved is None:
            errors.append(f"{label}.output_path must resolve inside the job")
        if item.get("render_eligible") is not False:
            errors.append(f"{label}.render_eligible must remain false")
        normalized.append({**item, "_resolved_path": resolved})
    if errors:
        raise PlateMotionError(errors)
    return {**payload, "items": normalized}


__all__ = [
    "PLATE_MOTION_MANIFEST_VERSION",
    "PLATE_MOTION_PLAN_VERSION",
    "PlateMotionError",
    "compile_plate_motion_plan",
    "to_magnific_video_plan",
    "validate_plate_motion_manifest",
    "validate_plate_motion_plan",
]
