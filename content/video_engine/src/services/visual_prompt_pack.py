"""Prompt fan-out and slot-bound candidate validation.

Two rules from the 2026-08-22 art-style review are enforced here rather than
left to review:

1. **No generated text in a plate.** Every prompt carries a negative clause
   forbidding lettering, numerals, logos and watermarks, and a candidate
   flagged ``contains_factual_text`` is refused. On-screen typography is
   composited by the renderer as real type.
2. **Identity in silhouette and costume colour.** Every prompt repeats the
   pack's ``identity_anchor`` so face drift cannot break continuity.

The engine emits the pack and validates what comes back. It never calls a
provider.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
    write_artifact,
)
from content.video_engine.src.services.composed_plate import is_composed
from content.video_engine.src.services.generated_visuals import (
    GeneratedVisualValidationError,
    validate_generated_visual_candidates,
)
from content.video_engine.src.services.style_packs import StylePackError, get_pack

VISUAL_PROMPT_PACK_VERSION = "visual_prompt_pack.v1"
DEFAULT_VARIANTS_PER_SLOT = 3
MIN_VARIANTS_PER_SLOT = 2

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"

#: Forbidden in every generated plate. Text is the renderer's job.
NEGATIVE_PROMPT = (
    "no lettering, no words, no numerals, no captions, no signage text, no logos, "
    "no watermarks, no signatures, no UI chrome, no extra fingers, no photorealism"
)

_ARCHETYPE_ROLES = {
    "lofi_stick_figure_comic": "lofi_comedy",
    "period_comic_block": "illustration",
    "typography_explainer": "illustration",
    "chapter_card": "illustration",
}
_DEFAULT_ROLE = "illustration"


class VisualPromptPackError(ValueError):
    """Prompt pack or candidate batch failed validation."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid visual prompt pack")


def _schema_errors(payload: Mapping[str, Any], name: str) -> list[str]:
    schema = load_json(_CONFIG_DIR / f"{name}.schema.json", f"{name} schema")
    validator = Draft7Validator(schema)
    return [
        name + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def role_for_archetype(archetype: str) -> str:
    return _ARCHETYPE_ROLES.get(archetype, _DEFAULT_ROLE)


def identity_anchor_for_lane(lane: str) -> str:
    """Read the anchor from the style-pack registry — one source of truth.

    Duplicating anchors here would let a lane's prompt drift from its pack.
    """

    try:
        return str(get_pack(lane)["character"]["identity_anchor"])
    except StylePackError as exc:
        raise VisualPromptPackError(exc.errors) from exc


def _compose_prompt(slot: Mapping[str, Any], *, lane: str, identity_anchor: str) -> str:
    intent = str(slot.get("visual_intent") or slot.get("narration_excerpt") or "").strip()
    archetype = str(slot.get("visual_archetype") or "")
    return (
        f"{lane} style plate. {intent} "
        f"Composition archetype: {archetype.replace('_', ' ')}. "
        f"Character identity: {identity_anchor}. "
        "Leave clear negative space for typography that is added later. "
        f"Negative: {NEGATIVE_PROMPT}."
    )


def compile_visual_prompt_pack(
    coverage: Mapping[str, Any] | str | Path,
    *,
    lane: str,
    variants_per_slot: int = DEFAULT_VARIANTS_PER_SLOT,
    identity_anchor: str | None = None,
    style_note: str | None = None,
) -> dict[str, Any]:
    """One prompt group per coverage slot, each requesting N variants."""

    if variants_per_slot < MIN_VARIANTS_PER_SLOT:
        raise VisualPromptPackError(
            [f"variants_per_slot must be at least {MIN_VARIANTS_PER_SLOT}"]
        )
    coverage_payload = load_json(coverage, "coverage")
    all_slots = list(coverage_payload.get("slots") or [])
    if not all_slots:
        raise VisualPromptPackError(["coverage contains no slots"])

    # Composed slots are drawn by the renderer from structured values, so they
    # never reach an image provider and never enter the generation budget.
    slots = [slot for slot in all_slots if not is_composed(slot)]
    if not slots:
        raise VisualPromptPackError(
            ["every coverage slot is composed; no prompt pack is required"]
        )

    anchor = identity_anchor or identity_anchor_for_lane(lane)
    groups = [
        {
            "slot_id": str(slot.get("slot_id")),
            "variant_count": variants_per_slot,
            "prompt": _compose_prompt(slot, lane=lane, identity_anchor=anchor),
            "narration_excerpt": str(slot.get("narration_excerpt") or ""),
            "visual_intent": str(slot.get("visual_intent") or ""),
            "visual_archetype": str(slot.get("visual_archetype") or "typography_explainer"),
            "motion_recipe": str(slot.get("motion_recipe") or "detail_punch"),
            "duration_s": float(slot.get("duration_s") or 0.0),
            "on_screen_text": slot.get("on_screen_text"),
            "copy_deferred": slot.get("copy_deferred") is True,
        }
        for slot in slots
    ]

    payload = {
        "schema_version": VISUAL_PROMPT_PACK_VERSION,
        "coverage_hash": str(coverage_payload.get("artifact_hash") or ""),
        "timing_basis": coverage_payload.get("timing_basis", "canonical"),
        "lane": lane,
        "variants_per_slot": variants_per_slot,
        "negative_prompt": NEGATIVE_PROMPT,
        "identity_anchor": anchor,
        "style_note": style_note,
        "composed_slot_count": len(all_slots) - len(slots),
        "groups": groups,
    }
    if style_note is None:
        payload.pop("style_note")
    stamp_artifact_hash(payload)

    errors = _schema_errors(payload, "visual_prompt_pack")
    if errors:
        raise VisualPromptPackError(errors)
    return payload


def _slot_binding_errors(
    items: Sequence[Mapping[str, Any]],
    *,
    known_slots: set[str],
    variants_per_slot: int,
) -> list[str]:
    errors: list[str] = []
    by_slot: dict[str, list[int]] = defaultdict(list)

    for index, item in enumerate(items):
        label = f"items[{index}]"
        slot_id = str(item.get("slot_id") or "").strip()
        if not slot_id:
            errors.append(f"{label}.slot_id is required")
            continue
        if slot_id not in known_slots:
            errors.append(f"{label}.slot_id {slot_id!r} is not a coverage slot")
            continue
        variant = item.get("variant_index")
        if not isinstance(variant, int) or isinstance(variant, bool) or variant < 0:
            errors.append(f"{label}.variant_index must be a non-negative integer")
            continue
        if variant in by_slot[slot_id]:
            errors.append(
                f"{label}.variant_index {variant} duplicates another candidate for "
                f"slot {slot_id!r}"
            )
        by_slot[slot_id].append(variant)

    for slot_id in sorted(known_slots):
        found = len(by_slot.get(slot_id, []))
        if found < variants_per_slot:
            errors.append(
                f"slot {slot_id!r} has {found} candidates; the pack requested "
                f"{variants_per_slot}"
            )
    return errors


def _generated_text_errors(items: Sequence[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, item in enumerate(items):
        if item.get("contains_factual_text") is True:
            errors.append(
                f"items[{index}] is flagged contains_factual_text; generated text in "
                "a plate is never render-eligible — typography is composited by the "
                "renderer"
            )
    return errors


def validate_candidate_batch(
    batch: Mapping[str, Any] | str | Path,
    *,
    pack: Mapping[str, Any] | str | Path,
    job_root: str | Path,
    check_files: bool = True,
) -> dict[str, Any]:
    """Layer slot binding and the no-generated-text rule over the base contract."""

    pack_payload = load_json(pack, "visual prompt pack")
    batch_payload = load_json(batch, "candidate batch")
    items = list(batch_payload.get("items") or [])

    errors = _generated_text_errors(items)
    errors.extend(
        _slot_binding_errors(
            items,
            known_slots={str(group["slot_id"]) for group in pack_payload.get("groups") or []},
            variants_per_slot=int(pack_payload.get("variants_per_slot") or MIN_VARIANTS_PER_SLOT),
        )
    )
    if errors:
        raise VisualPromptPackError(errors)

    try:
        normalized = validate_generated_visual_candidates(
            batch_payload, job_root=job_root, check_files=check_files
        )
    except GeneratedVisualValidationError as exc:
        raise VisualPromptPackError(getattr(exc, "errors", None) or [str(exc)]) from exc
    return normalized


def compile_and_write(
    coverage: Mapping[str, Any] | str | Path,
    *,
    lane: str,
    output_dir: str | Path,
    variants_per_slot: int = DEFAULT_VARIANTS_PER_SLOT,
    style_note: str | None = None,
) -> dict[str, Any]:
    pack = compile_visual_prompt_pack(
        coverage,
        lane=lane,
        variants_per_slot=variants_per_slot,
        style_note=style_note,
    )
    path = write_artifact(Path(output_dir) / "visual_prompt_pack.json", pack)
    return {
        "pack_path": str(path),
        "pack_hash": pack["artifact_hash"],
        "group_count": len(pack["groups"]),
        "composed_slot_count": pack.get("composed_slot_count", 0),
        "variants_per_slot": pack["variants_per_slot"],
        "requested_generations": len(pack["groups"]) * pack["variants_per_slot"],
    }
