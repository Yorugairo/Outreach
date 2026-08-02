"""Provider-neutral explainer blocks and producer request planning.

The planner translates reviewed editorial coverage into requests for image,
video, archive, and deterministic producers. Providers never receive research
URLs, creator names, or unresolved local paths; Remotion/Manim remain the
assembly and evidence layers.
"""

from __future__ import annotations

import json
from typing import Any, Mapping

from content.video_engine.src.services.history_contracts import canonical_sha256


PRODUCER_PLAN_VERSION = "producer_plan.v1"
PRODUCER_KINDS = {"image", "video", "asset", "deterministic"}
PRODUCER_IDS = {
    "gpt_image",
    "magnific_nano_banana_2",
    "magnific_kling_2_5",
    "google_flow_character",
    "google_flow_ingredients_to_video",
    "higgsfield_nano_banana_2",
    "higgsfield_gemini_omni",
    "magnific_stock",
    "asset_manifest",
    "remotion",
    "manim",
}
PROHIBITED_PROVIDER_INPUTS = (
    "in the style of",
    "youtube reference pack",
    "consultant outline",
    "creator name",
    "creator_name",
    "source_frame",
)


class ProducerPlanError(ValueError):
    """Raised when producer orchestration cannot be safely compiled."""


def _producer_route(source: str) -> tuple[str, list[str], list[str]]:
    if source == "original_illustration":
        return (
            "image",
            ["gpt_image", "magnific_nano_banana_2"],
            ["magnific_kling_2_5", "higgsfield_gemini_omni"],
        )
    if source in {"archive", "stock_photo", "stock_vector"}:
        return ("asset", ["asset_manifest", "magnific_stock"], ["remotion"])
    if source in {"map", "graph", "document", "concept", "concept_mechanics"}:
        return (
            "image",
            ["gpt_image", "magnific_nano_banana_2"],
            ["remotion"],
        )
    return ("deterministic", ["remotion", "manim"], ["remotion"])


def _overlay_policy(source: str) -> dict[str, Any]:
    policies = {
        "map": {
            "plate_role": "migration_world",
            "overlay_owner": "remotion",
            "overlay_fields": ["reviewed_places", "reviewed_route", "reviewed_dates", "citation_rail"],
            "generated_geometry_is_evidence": False,
        },
        "graph": {
            "plate_role": "lineage_scroll",
            "overlay_owner": "remotion",
            "overlay_fields": ["reviewed_entities", "reviewed_relationship_verbs", "uncertainty_labels", "citation_rail"],
            "generated_geometry_is_evidence": False,
        },
        "document": {
            "plate_role": "archive_world",
            "overlay_owner": "remotion",
            "overlay_fields": ["approved_excerpt", "locator", "qualification", "citation_rail"],
            "generated_geometry_is_evidence": False,
        },
        "concept": {
            "plate_role": "concept_cutaway",
            "overlay_owner": "remotion",
            "overlay_fields": ["reviewed_concept_labels", "caption", "citation_rail"],
            "generated_geometry_is_evidence": False,
        },
        "concept_mechanics": {
            "plate_role": "concept_cutaway",
            "overlay_owner": "remotion",
            "overlay_fields": ["reviewed_concept_labels", "caption", "citation_rail"],
            "generated_geometry_is_evidence": False,
        },
    }
    return dict(policies.get(source, {
        "plate_role": "none",
        "overlay_owner": "manim_or_remotion",
        "overlay_fields": [],
        "generated_geometry_is_evidence": False,
    }))


def _producer_source(slot: Mapping[str, Any]) -> str:
    """Resolve source by documentary function before honoring a weak fallback."""

    function = str(slot.get("function") or slot.get("visual_function") or "")
    function_sources = {
        "migration_map_timeline": "map",
        "lineage_graph": "graph",
        "concept_mechanics_cutaway": "concept_mechanics",
        "document_quote_closeup": "document",
    }
    if function in function_sources:
        return function_sources[function]
    return str(
        slot.get("selected_visual_source")
        or slot.get("preferred_visual_source")
        or ""
    )


def _prompt_contract(
    slot: Mapping[str, Any],
    style_key: Mapping[str, Any],
) -> dict[str, Any]:
    archetype = str(slot.get("visual_archetype") or "editorial visual")
    recipe = str(slot.get("motion_recipe") or "hard_cut")
    source = _producer_source(slot)
    overlay_policy = _overlay_policy(source)
    world_plate_instruction = (
        "Create a clean unlabeled world plate. Do not draw names, dates, routes, relationship verbs, "
        "citations, maps-as-evidence, or factual document text; those are deterministic post overlays."
        if overlay_policy["plate_role"] != "none"
        else "Keep the composition abstract and free of factual labels."
    )
    return {
        "scene": (
            f"Original non-photorealistic {archetype} supporting the reviewed "
            "narration beat; interpret the idea without adding historical evidence. "
            f"Apply the internal style key consistently. {world_plate_instruction}"
        ),
        "style_key": dict(style_key),
        "motion": f"Use the approved {recipe} motion recipe; one clear action only.",
        "audio": "Silent provider output; narration, captions, citations, and credits are added in post.",
        "negative": [
            "photorealism",
            "live action",
            "generated text",
            "logos",
            "watermarks",
            "lip sync",
            "dialogue",
            "new factual claims",
            "creator imitation",
        ],
        "world_plate_policy": overlay_policy,
    }


def compile_producer_plan(
    coverage: Mapping[str, Any],
    *,
    art_bible_id: str = "",
    art_bible_hash: str = "",
    character_pack_id: str = "",
    style_descriptor: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile one typed producer block per semantic coverage slot."""

    if coverage.get("schema_version") != "editorial_coverage.v1":
        raise ProducerPlanError("producer planning requires editorial_coverage.v1")
    slots = coverage.get("slots")
    if not isinstance(slots, list) or not slots:
        raise ProducerPlanError("producer planning requires coverage slots")

    blocks: list[dict[str, Any]] = []
    for order, slot in enumerate(slots, start=1):
        if not isinstance(slot, Mapping):
            raise ProducerPlanError(f"coverage slot {order} must be an object")
        slot_id = str(slot.get("slot_id") or "").strip()
        if not slot_id:
            raise ProducerPlanError(f"coverage slot {order} requires slot_id")
        requested_source = str(
            slot.get("selected_visual_source")
            or slot.get("preferred_visual_source")
            or ""
        )
        source = _producer_source(slot)
        kind, still_producers, motion_producers = _producer_route(source)
        if character_pack_id and source == "original_illustration":
            still_producers = [*still_producers, "google_flow_character"]
            motion_producers = ["google_flow_ingredients_to_video", *motion_producers]
        duration_s = float(slot.get("duration_s") or 0)
        if duration_s <= 0:
            raise ProducerPlanError(f"{slot_id} requires a positive duration")
        block_id = f"block-{order:04d}-{slot_id}"
        style_key = {
            "art_bible_id": art_bible_id,
            "art_bible_hash": art_bible_hash,
            "style_key_asset_id": "",
            **dict(style_descriptor or {}),
            "character_pack_id": character_pack_id,
        }
        block = {
            "block_id": block_id,
            "order": order,
            "coverage_slot_id": slot_id,
            "narration_excerpt": str(slot.get("narration_excerpt") or ""),
            "duration_s": round(duration_s, 6),
            "provider_duration_s": 10 if motion_producers != ["remotion"] else None,
            "semantic_purpose": str(slot.get("semantic_purpose") or ""),
            "visual_archetype": str(slot.get("visual_archetype") or ""),
            "visual_source": source,
            "requested_visual_source": requested_source,
            "producer_kind": kind,
            "still_producers": [
                {"id": producer, "kind": "image" if producer not in {"asset_manifest", "magnific_stock", "remotion", "manim"} else "asset"}
                for producer in still_producers
            ],
            "motion_producers": [
                {"id": producer, "kind": "video" if producer not in {"remotion", "manim"} else "deterministic"}
                for producer in motion_producers
            ],
            "style_key": style_key,
            "prompt": _prompt_contract(slot, style_key),
            "world_plate_policy": _overlay_policy(source),
            "claim_refs": list(slot.get("claim_refs") or []),
            "citation_refs": list(slot.get("citation_refs") or []),
            "asset_ids": list(slot.get("asset_ids") or []),
            "motion_recipe": str(slot.get("motion_recipe") or ""),
            "micro_events": list(slot.get("micro_events") or []),
            "uniqueness_signature": str(slot.get("uniqueness_signature") or ""),
            "status": "planned",
            "render_eligible": False,
            "assembly": {
                "narration_owner": "elevenlabs_or_human_recorded",
                "caption_owner": "remotion",
                "citation_owner": "remotion",
                "diagram_owner": "manim_or_remotion",
                "world_plate_owner": "gpt_image_or_nano_banana_2" if kind == "image" else "none",
                "fact_overlay_owner": "remotion",
            },
        }
        blocks.append(block)

    core = {
        "schema_version": PRODUCER_PLAN_VERSION,
        "coverage_plan_hash": str(
            coverage.get("artifact_hash") or canonical_sha256(coverage)
        ),
        "art_bible_id": art_bible_id,
        "art_bible_hash": art_bible_hash,
        "character_pack_id": character_pack_id,
        "block_count": len(blocks),
        "policy": {
            "style_key_required": True,
            "audio_generated_separately": True,
            "provider_output_render_eligible": False,
            "research_and_rights_stay_outside_provider_prompts": True,
            "character_builder_outputs_require_operator_promotion": True,
        },
        "blocks": blocks,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_producer_plan(
    payload: Mapping[str, Any],
    *,
    expected_art_bible_hash: str | None = None,
    expected_coverage_hash: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != PRODUCER_PLAN_VERSION:
        errors.append(f"producer plan must use {PRODUCER_PLAN_VERSION}")
    blocks = payload.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        return [*errors, "producer plan requires blocks"]
    if expected_art_bible_hash and payload.get("art_bible_hash") != expected_art_bible_hash:
        errors.append("producer plan art_bible_hash is stale")
    if expected_coverage_hash and payload.get("coverage_plan_hash") != expected_coverage_hash:
        errors.append("producer plan coverage_plan_hash is stale")
    seen: set[str] = set()
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True).casefold()
    for term in PROHIBITED_PROVIDER_INPUTS:
        if term in serialized:
            errors.append(f"producer plan contains prohibited provider input {term!r}")
    for index, block in enumerate(blocks):
        if not isinstance(block, Mapping):
            errors.append(f"blocks[{index}] must be an object")
            continue
        block_id = str(block.get("block_id") or "")
        if not block_id or block_id in seen:
            errors.append(f"blocks[{index}].block_id must be unique")
        seen.add(block_id)
        if not str(block.get("narration_excerpt") or "").strip():
            errors.append(f"{block_id or index} narration_excerpt is required")
        if float(block.get("duration_s") or 0) <= 0:
            errors.append(f"{block_id or index} duration_s must be positive")
        if block.get("render_eligible") is not False:
            errors.append(f"{block_id or index} provider output must not be render eligible")
        for key in ("still_producers", "motion_producers"):
            producers = block.get(key)
            if not isinstance(producers, list) or not producers:
                errors.append(f"{block_id or index} requires {key}")
                continue
            for producer in producers:
                if not isinstance(producer, Mapping) or producer.get("id") not in PRODUCER_IDS:
                    errors.append(f"{block_id or index} has an invalid producer in {key}")
        style_key = block.get("style_key")
        if not isinstance(style_key, Mapping):
            errors.append(f"{block_id or index} requires style_key")
    expected = canonical_sha256(
        {key: value for key, value in payload.items() if key != "artifact_hash"}
    )
    if payload.get("artifact_hash") != expected:
        errors.append("producer plan artifact_hash does not match content")
    return errors


__all__ = [
    "PRODUCER_KINDS",
    "PRODUCER_PLAN_VERSION",
    "ProducerPlanError",
    "compile_producer_plan",
    "validate_producer_plan",
]
