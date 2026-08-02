"""Asset inventory and communication contracts for the living-scene lane.

This module is deliberately provider-free.  It inventories local R&D media and
validates the communication rules that later scene compilers must obey.  An
inventory or grammar is evidence and planning input, never a render manifest.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft7Validator

from content.video_engine.src.services.history_contracts import canonical_sha256


CREATIVE_INVENTORY_VERSION = "creative_inventory.v1"
COMMUNICATION_GRAMMAR_VERSION = "communication_grammar.v1"
CREATIVE_ASSET_MAP_VERSION = "creative_asset_map.v1"
WORLD_PACK_LIBRARY_VERSION = "world_pack_library.v1"
SCENE_BUNDLE_VERSION = "scene_bundle.v1"
SCENE_FLOW_GRAPH_VERSION = "scene_flow_graph.v1"
STYLE_PACK_LIBRARY_VERSION = "style_pack_library.v1"
ASSET_FOUNDATION_REVIEW_VERSION = "asset_foundation_review.v1"
CLASSIFICATIONS = {
    "approved_reusable",
    "reference_only",
    "rejected",
    "superseded",
    "unknown",
}
MEDIA_KINDS = {
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".webp": "image",
    ".gif": "image",
    ".svg": "vector",
    ".mp4": "video",
    ".mov": "video",
    ".webm": "video",
    ".mkv": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
    ".aac": "audio",
}


class LivingSceneValidationError(ValueError):
    """Raised when a living-scene planning artifact fails closed."""

    def __init__(self, errors: Iterable[str], *, contract: str):
        self.errors = list(errors)
        self.contract = contract
        super().__init__(f"invalid {contract}: {'; '.join(self.errors)}")


def _engine_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load(value: Mapping[str, Any] | str | Path, label: str) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    try:
        payload = json.loads(Path(value).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LivingSceneValidationError(
            [f"{label} is not valid JSON: {exc}"], contract=label
        ) from exc
    if not isinstance(payload, Mapping):
        raise LivingSceneValidationError(
            [f"{label} root must be an object"], contract=label
        )
    return copy.deepcopy(dict(payload))


def _schema_errors(payload: Mapping[str, Any], schema_name: str) -> list[str]:
    try:
        schema = json.loads(
            (_engine_root() / "configs" / schema_name).read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"schema could not be loaded: {exc}"]
    errors = sorted(
        Draft7Validator(schema).iter_errors(payload),
        key=lambda error: (
            tuple(str(part) for part in error.absolute_path),
            error.message,
        ),
    )
    return [
        "schema "
        + (".".join(str(part) for part in error.absolute_path) or "root")
        + f": {error.message}"
        for error in errors
    ]


def _artifact_hash_error(payload: Mapping[str, Any]) -> str | None:
    declared = payload.get("artifact_hash")
    expected = canonical_sha256(payload)
    if declared != expected:
        return "artifact_hash does not match canonical content"
    return None


def build_default_communication_grammar() -> dict[str, Any]:
    """Return the first Combat History living-scene communication grammar."""

    core: dict[str, Any] = {
        "schema_version": COMMUNICATION_GRAMMAR_VERSION,
        "id": "combat-history-living-scenes-v1",
        "surfaces": [
            {
                "id": "world",
                "audience_function": "Establish place, period, mood, and scale.",
                "owns": ["architecture", "terrain", "weather", "atmosphere", "background activity"],
                "prohibits": ["factual text", "exact routes", "dates", "citations"],
            },
            {
                "id": "character",
                "audience_function": "Create attention, empathy, humor, and human action.",
                "owns": ["gesture", "reaction", "travel", "object handling", "point of view"],
                "prohibits": ["unsourced claims", "provider dialogue", "provider lip-sync"],
            },
            {
                "id": "evidence",
                "audience_function": "State exactly what the historical record supports.",
                "owns": ["dates", "claims", "quotations", "archive excerpts", "citations", "uncertainty"],
                "prohibits": ["invented documents", "uncited quotations", "generated facts"],
            },
            {
                "id": "explanation",
                "audience_function": "Make sequence, relationships, and causality legible.",
                "owns": ["reviewed routes", "timelines", "entity-verb graphs", "comparisons"],
                "prohibits": ["keyword graphs", "generated geography", "unsourced edges"],
            },
            {
                "id": "transition",
                "audience_function": "Carry meaning and visual continuity into the next scene.",
                "owns": ["shared motion", "shape", "object", "material", "color"],
                "prohibits": ["unmotivated effects", "random wipes", "continuity-breaking movement"],
            },
        ],
        "documentary_beat_grammar": [
            {"order": 1, "id": "picture_it", "purpose": "Establish the human situation through world or character."},
            {"order": 2, "id": "name_it", "purpose": "Introduce the exact person, place, date, or proposition."},
            {"order": 3, "id": "show_relationship", "purpose": "Make the consequence legible through action or explanation."},
            {"order": 4, "id": "qualify_it", "purpose": "Show what the evidence can and cannot prove."},
            {"order": 5, "id": "carry_forward", "purpose": "Transform the exit motif into the next scene's entry motif."},
        ],
        "fact_surfaces": [
            {"id": "date_seal", "owner": "evidence", "content_rule": "One date and one short event label.", "citation_required": True},
            {"id": "fact_folio", "owner": "evidence", "content_rule": "One concise claim and a compact citation rail.", "citation_required": True},
            {"id": "archive_proof", "owner": "evidence", "content_rule": "A rights-reviewed image or excerpt with source identity.", "citation_required": True},
            {"id": "journey_ribbon", "owner": "explanation", "content_rule": "Reviewed places, direction, and dates over an interpretive world.", "citation_required": True},
            {"id": "relationship_scroll", "owner": "explanation", "content_rule": "Named entities joined only by sourced verbs.", "citation_required": True},
            {"id": "uncertainty_card", "owner": "evidence", "content_rule": "Display the approved claim state and qualification.", "citation_required": True},
        ],
        "motion_hierarchy": [
            {"rank": 1, "id": "character_prop", "examples": ["enter", "turn", "point", "carry", "open", "stamp", "react", "walk"]},
            {"rank": 2, "id": "localized_environment", "examples": ["water", "leaves", "fabric", "steam", "smoke", "rain", "firelight", "mill wheel"]},
            {"rank": 3, "id": "information_reveal", "examples": ["date seal", "evidence highlight", "route trace", "relationship branch", "correction stamp"]},
            {"rank": 4, "id": "camera", "examples": ["locked frame", "restrained push-in"]},
        ],
        "scene_policy": {
            "target_duration_s": 25,
            "minimum_duration_s": 20,
            "maximum_duration_s": 30,
            "narration_beats_min": 2,
            "narration_beats_max": 4,
            "camera_only_motion_satisfies_beat": False,
            "whole_background_motion_default": False,
            "required_meaningful_motion_layers": [
                "character_prop",
                "localized_environment",
                "information_reveal",
            ],
        },
        "humor_policy": {
            "primary_owner": "character",
            "may_authenticate_claims": False,
            "may_settle_contested_claims": False,
        },
        "generated_content_policy": {
            "factual_text_in_generated_pixels": False,
            "generated_maps_are_evidence": False,
            "generated_documents_are_evidence": False,
            "facts_rendered_locally": True,
        },
        "visual_system_policy": {
            "stable_outline_color_camera": True,
            "concept_controls_motion": True,
            "comparison_template_reused": True,
            "flat_colors": True,
            "thick_outlines": True,
        },
        "transition_policy": {
            "catalog_layout_reused": True,
            "subject_motivated": True,
            "structural_resets": [
                "section_title_card",
                "color_coded_icon_change",
                "photo_to_diagram_swap",
                "direct_hard_cut",
            ],
            "action_cut_points": [
                "anticipation",
                "contact",
                "recoil",
                "result",
            ],
            "motifs_per_chapter_min": 1,
            "motifs_per_chapter_max": 2,
            "match_dimensions": ["shape", "direction"],
        },
        "sound_policy": {
            "mix": "narration_led",
            "music": "restrained",
            "ui_card_sounds": "subtle",
            "impact_accents": "demonstration_only",
        },
        "cost_policy": {
            "higgsfield_observed_credits": 600,
            "higgsfield_observed_duration_s": 180,
            "baseline_credits_per_second": 3.333333,
            "full_runtime_provider_default": False,
            "proof_max_paid_motion_s": 30,
        },
        "render_eligible": False,
    }
    return {**core, "artifact_hash": canonical_sha256(core)}


def validate_communication_grammar(
    value: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    payload = _load(value, "communication grammar")
    errors = _schema_errors(payload, "communication_grammar.schema.json")

    surfaces = [str(item.get("id")) for item in payload.get("surfaces", []) if isinstance(item, Mapping)]
    expected_surfaces = ["world", "character", "evidence", "explanation", "transition"]
    if surfaces != expected_surfaces:
        errors.append(f"surfaces must appear once in canonical order: {expected_surfaces}")

    beats = [str(item.get("id")) for item in payload.get("documentary_beat_grammar", []) if isinstance(item, Mapping)]
    expected_beats = ["picture_it", "name_it", "show_relationship", "qualify_it", "carry_forward"]
    if beats != expected_beats:
        errors.append(f"documentary beat grammar must use canonical order: {expected_beats}")

    motion = [str(item.get("id")) for item in payload.get("motion_hierarchy", []) if isinstance(item, Mapping)]
    expected_motion = ["character_prop", "localized_environment", "information_reveal", "camera"]
    if motion != expected_motion:
        errors.append(f"motion hierarchy must use canonical order: {expected_motion}")

    policy = payload.get("scene_policy") or {}
    if isinstance(policy, Mapping):
        minimum = float(policy.get("minimum_duration_s") or 0)
        target = float(policy.get("target_duration_s") or 0)
        maximum = float(policy.get("maximum_duration_s") or 0)
        if not minimum <= target <= maximum:
            errors.append("scene duration must satisfy minimum <= target <= maximum")
        beats_min = int(policy.get("narration_beats_min") or 0)
        beats_max = int(policy.get("narration_beats_max") or 0)
        if beats_min > beats_max:
            errors.append("narration beat minimum cannot exceed maximum")

    cost = payload.get("cost_policy") or {}
    if isinstance(cost, Mapping):
        credits = float(cost.get("higgsfield_observed_credits") or 0)
        duration = float(cost.get("higgsfield_observed_duration_s") or 0)
        baseline = float(cost.get("baseline_credits_per_second") or 0)
        if duration > 0 and abs((credits / duration) - baseline) > 0.00001:
            errors.append("baseline credits per second does not match observed cost")

    transitions = payload.get("transition_policy") or {}
    if isinstance(transitions, Mapping):
        expected_cut_points = ["anticipation", "contact", "recoil", "result"]
        if transitions.get("action_cut_points") != expected_cut_points:
            errors.append(
                f"action cut points must use canonical order: {expected_cut_points}"
            )

    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="communication grammar")
    return payload


def _asset_index(
    value: Mapping[str, Any] | str | Path | None,
) -> tuple[dict[str, Any] | None, dict[str, Mapping[str, Any]]]:
    if value is None:
        return None, {}
    payload = validate_creative_asset_map(value)
    return payload, {
        str(asset["id"]): asset
        for asset in payload.get("assets", [])
        if isinstance(asset, Mapping)
    }


def _style_pack_index(
    value: Mapping[str, Any] | str | Path | None,
) -> tuple[dict[str, Any] | None, dict[str, Mapping[str, Any]]]:
    if value is None:
        return None, {}
    payload = validate_style_pack_library(value)
    return payload, {
        str(pack["id"]): pack
        for pack in payload.get("packs", [])
        if isinstance(pack, Mapping)
    }


def _resolve_style_pack(
    pack_id: str,
    packs: Mapping[str, Mapping[str, Any]],
    errors: list[str],
    label: str,
) -> None:
    if pack_id not in packs:
        errors.append(f"{label} references unknown style pack {pack_id!r}")


def validate_style_pack_library(
    value: Mapping[str, Any] | str | Path,
    *,
    calibration_inventory: Mapping[str, Any] | str | Path | None = None,
    asset_map: Mapping[str, Any] | str | Path | None = None,
    check_files: bool = True,
) -> dict[str, Any]:
    """Validate the three pack variants under one woodblock parent identity."""

    payload = _load(value, "style pack library")
    errors = _schema_errors(payload, "style_pack_library.schema.json")
    expected_ids = [
        "woodblock-anime-action-v1",
        "woodblock-historical-editorial-v1",
        "woodblock-comic-whitespace-v1",
    ]
    pack_ids = [
        str(pack.get("id") or "")
        for pack in payload.get("packs") or []
        if isinstance(pack, Mapping)
    ]
    if pack_ids != expected_ids:
        errors.append(f"style packs must use canonical order: {expected_ids}")

    if calibration_inventory is not None:
        try:
            inventory = validate_creative_inventory(
                calibration_inventory,
                check_files=check_files,
            )
        except LivingSceneValidationError as exc:
            errors.extend(f"calibration inventory: {error}" for error in exc.errors)
        else:
            if payload.get("calibration_inventory_hash") != inventory.get("artifact_hash"):
                errors.append("calibration_inventory_hash does not match supplied inventory")
            non_reference = [
                item.get("relative_path")
                for item in inventory.get("items") or []
                if isinstance(item, Mapping)
                and item.get("classification") != "reference_only"
            ]
            if non_reference:
                errors.append("calibration inventory must remain reference_only")

    if asset_map is not None:
        try:
            _, assets = _asset_index(asset_map)
        except LivingSceneValidationError as exc:
            errors.extend(f"asset map: {error}" for error in exc.errors)
        else:
            _resolve_asset(
                str(payload.get("parent_style_key_id") or ""),
                "style_key",
                assets,
                errors,
                "parent_style_key_id",
            )

    canonical_cuts = ["anticipation", "contact", "recoil", "result"]
    for index, pack in enumerate(payload.get("packs") or []):
        if not isinstance(pack, Mapping):
            continue
        composition = pack.get("composition") or {}
        if isinstance(composition, Mapping):
            if int(composition.get("panel_count_min") or 0) > int(
                composition.get("panel_count_max") or 0
            ):
                errors.append(f"packs[{index}] panel range is inverted")
            if float(composition.get("negative_space_min") or 0) > float(
                composition.get("negative_space_max") or 0
            ):
                errors.append(f"packs[{index}] negative-space range is inverted")
        motion = pack.get("motion") or {}
        if isinstance(motion, Mapping):
            drivers = motion.get("primary_drivers") or []
            if not drivers or drivers == ["camera"]:
                errors.append(f"packs[{index}] camera cannot be the only motion driver")
        prompt = str(pack.get("prompt_core") or "").casefold()
        if "in the style of" in prompt:
            errors.append(f"packs[{index}] uses prohibited imitation language")
        negative_text = " ".join(
            str(item).casefold() for item in pack.get("negative_constraints") or []
        )
        for token in ("text", "date", "label", "logo"):
            if token not in negative_text:
                errors.append(f"packs[{index}] negative constraints must prohibit {token}")

        pack_id = pack.get("id")
        lanes = pack.get("primary_lanes") or []
        production = pack.get("production") or {}
        characters = pack.get("character_policy") or {}
        if pack_id == "woodblock-anime-action-v1":
            if not {"technique_analysis", "fight_analysis"}.issubset(set(lanes)):
                errors.append("action pack must cover technique and fight analysis")
            if isinstance(motion, Mapping) and motion.get("action_cut_points") != canonical_cuts:
                errors.append("action pack must use canonical action cut points")
            if isinstance(characters, Mapping) and characters.get("fighter_color_ownership") is not True:
                errors.append("action pack requires fighter color ownership")
        elif pack_id == "woodblock-historical-editorial-v1":
            if "history" not in lanes:
                errors.append("historical pack must cover the history lane")
        elif pack_id == "woodblock-comic-whitespace-v1":
            if "trending_response" not in lanes:
                errors.append("whitespace pack must cover trending response")
            if isinstance(composition, Mapping) and float(
                composition.get("negative_space_min") or 0
            ) < 0.35:
                errors.append("whitespace pack requires at least 35% negative space")
            if isinstance(production, Mapping) and production.get("turnaround_class") != "rapid":
                errors.append("whitespace pack must use rapid turnaround")

    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="style pack library")
    return payload


def _resolve_asset(
    asset_id: str,
    expected_class: str,
    assets: Mapping[str, Mapping[str, Any]],
    errors: list[str],
    label: str,
) -> None:
    asset = assets.get(asset_id)
    if asset is None:
        errors.append(f"{label} references unknown asset {asset_id!r}")
    elif asset.get("asset_class") != expected_class:
        errors.append(
            f"{label} requires {expected_class}, but {asset_id!r} is "
            f"{asset.get('asset_class')!r}"
        )


def validate_creative_asset_map(
    value: Mapping[str, Any] | str | Path,
    *,
    expected_grammar_hash: str | None = None,
) -> dict[str, Any]:
    """Validate the finite asset demand contract before any generation."""

    payload = _load(value, "creative asset map")
    errors = _schema_errors(payload, "creative_asset_map.schema.json")
    if expected_grammar_hash and payload.get("communication_grammar_hash") != expected_grammar_hash:
        errors.append("communication_grammar_hash does not match approved grammar")

    assets = payload.get("assets") or []
    ids: set[str] = set()
    by_class: Counter[str] = Counter()
    by_readiness: Counter[str] = Counter()
    ceiling_counts: Counter[str] = Counter()
    dependency_records: list[tuple[int, str]] = []
    terminal_readiness = {
        "manifest_approved",
        "visual_approved",
        "animation_tested",
        "production_ready",
    }
    for index, asset in enumerate(assets):
        if not isinstance(asset, Mapping):
            continue
        asset_id = str(asset.get("id") or "")
        asset_class = str(asset.get("asset_class") or "")
        readiness = str(asset.get("readiness") or "")
        if asset_id in ids:
            errors.append(f"assets[{index}] duplicates id {asset_id!r}")
        ids.add(asset_id)
        by_class[asset_class] += 1
        by_readiness[readiness] += 1
        uses = [item for item in asset.get("uses", []) if isinstance(item, Mapping)]
        episodes = sorted({str(item.get("episode_id") or "") for item in uses})
        if sorted(asset.get("episodes") or []) != episodes:
            errors.append(f"assets[{index}] episodes do not match uses")
        if asset.get("recurrence_count") != len(uses):
            errors.append(f"assets[{index}] recurrence_count does not match uses")
        for dependency in asset.get("dependencies") or []:
            dependency_records.append((index, str(dependency)))

        only_questions = bool(uses) and all(
            item.get("research_state") == "question_only" for item in uses
        )
        if only_questions:
            if readiness != "blocked_research":
                errors.append(
                    f"assets[{index}] question-only demand must be blocked_research"
                )
            if asset.get("generation_needed") is True:
                errors.append(
                    f"assets[{index}] question-only demand cannot authorize generation"
                )
        if readiness == "blocked_research" and asset.get("generation_needed") is True:
            errors.append(f"assets[{index}] blocked research cannot authorize generation")
        if (
            readiness in terminal_readiness
            and asset_class in {"character", "archive", "scene_plate"}
            and not asset.get("manifest_asset_ids")
        ):
            errors.append(
                f"assets[{index}] {readiness} {asset_class} requires a manifest asset ID"
            )

        if readiness not in {"blocked_research", "rejected", "superseded"}:
            if asset_class == "character":
                role = str(asset.get("character_role") or "")
                ceiling_counts[
                    "narrator" if role == "narrator" else "historical_character"
                ] += 1
            elif asset_class in {
                "style_key",
                "world",
                "prop",
                "ambient_loop",
                "fact_surface",
                "transition_motif",
            }:
                ceiling_counts[asset_class] += 1

    for index, dependency in dependency_records:
        if dependency not in ids:
            errors.append(f"assets[{index}] dependency {dependency!r} does not resolve")

    policy = payload.get("policy") or {}
    ceilings: Mapping[str, Any] = {}
    if isinstance(policy, Mapping):
        candidate_ceilings = policy.get("asset_ceilings") or {}
        if isinstance(candidate_ceilings, Mapping):
            ceilings = candidate_ceilings
    if isinstance(ceilings, Mapping):
        for asset_class, count in sorted(ceiling_counts.items()):
            ceiling = ceilings.get(asset_class)
            if isinstance(ceiling, int) and count > ceiling:
                errors.append(
                    f"asset ceiling exceeded for {asset_class}: {count} > {ceiling}"
                )

    summary = payload.get("summary") or {}
    if isinstance(summary, Mapping):
        if summary.get("total_assets") != len(assets):
            errors.append("summary total_assets does not match assets")
        if summary.get("by_class") != dict(sorted(by_class.items())):
            errors.append("summary by_class does not match assets")
        if summary.get("by_readiness") != dict(sorted(by_readiness.items())):
            errors.append("summary by_readiness does not match assets")
    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="creative asset map")
    return payload


def validate_asset_foundation_review(
    value: Mapping[str, Any] | str | Path,
    *,
    asset_map: Mapping[str, Any] | str | Path,
    world_packs: Mapping[str, Any] | str | Path,
    style_packs: Mapping[str, Any] | str | Path,
    calibration_inventory: Mapping[str, Any] | str | Path,
    asset_manifest: Mapping[str, Any] | str | Path,
    project_root: str | Path,
    check_files: bool = True,
) -> dict[str, Any]:
    """Validate quarantined foundation candidates without promoting them."""

    payload = _load(value, "asset foundation review")
    errors = _schema_errors(payload, "asset_foundation_review.schema.json")

    try:
        asset_payload, assets = _asset_index(asset_map)
    except LivingSceneValidationError as exc:
        errors.extend(f"asset map: {error}" for error in exc.errors)
        asset_payload, assets = None, {}
    try:
        style_payload = validate_style_pack_library(style_packs)
    except LivingSceneValidationError as exc:
        errors.extend(f"style packs: {error}" for error in exc.errors)
        style_payload = None
    try:
        world_payload = validate_world_pack_library(
            world_packs,
            asset_map=asset_map,
            style_pack_library=style_packs,
        )
    except LivingSceneValidationError as exc:
        errors.extend(f"world packs: {error}" for error in exc.errors)
        world_payload = None
    try:
        inventory_payload = validate_creative_inventory(
            calibration_inventory,
            check_files=check_files,
        )
    except LivingSceneValidationError as exc:
        errors.extend(f"calibration inventory: {error}" for error in exc.errors)
        inventory_payload = None
    try:
        manifest_payload = _load(asset_manifest, "asset manifest")
    except LivingSceneValidationError as exc:
        errors.extend(f"asset manifest: {error}" for error in exc.errors)
        manifest_payload = {}

    immutable = payload.get("immutable_inputs") or {}
    expected_hashes = {
        "asset_map_hash": asset_payload.get("artifact_hash") if asset_payload else None,
        "world_pack_hash": world_payload.get("artifact_hash") if world_payload else None,
        "style_pack_hash": style_payload.get("artifact_hash") if style_payload else None,
        "calibration_inventory_hash": (
            inventory_payload.get("artifact_hash") if inventory_payload else None
        ),
        "asset_manifest_hash": canonical_sha256(manifest_payload),
    }
    if isinstance(immutable, Mapping):
        for field, expected in expected_hashes.items():
            if expected and immutable.get(field) != expected:
                errors.append(f"immutable_inputs.{field} does not match supplied artifact")

    root = Path(project_root).resolve()
    manifest_assets = {
        str(item.get("id") or ""): item
        for item in manifest_payload.get("assets") or []
        if isinstance(item, Mapping)
    }
    style_ids = {
        str(item.get("id") or "")
        for item in (style_payload or {}).get("packs") or []
        if isinstance(item, Mapping)
    }
    class_counts: Counter[str] = Counter()
    seen_candidates: set[str] = set()
    class_to_demand = {
        "world_master": "world",
        "character_motion_sheet": "character",
        "prop_sprite": "prop",
        "archive_evidence": "archive",
        "scene_plate": "scene_plate",
    }
    for index, candidate in enumerate(payload.get("candidates") or []):
        if not isinstance(candidate, Mapping):
            continue
        candidate_id = str(candidate.get("id") or "")
        demand_id = str(candidate.get("demand_asset_id") or "")
        candidate_class = str(candidate.get("candidate_class") or "")
        if candidate_id in seen_candidates:
            errors.append(f"candidates[{index}] duplicates id {candidate_id!r}")
        seen_candidates.add(candidate_id)
        class_counts[candidate_class] += 1
        demand = assets.get(demand_id)
        if demand is None:
            errors.append(f"candidates[{index}] references unknown demand {demand_id!r}")
        else:
            if demand.get("asset_class") != class_to_demand.get(candidate_class):
                errors.append(f"candidates[{index}] class does not match demand {demand_id!r}")
            if demand.get("readiness") == "blocked_research":
                errors.append(f"candidates[{index}] cannot satisfy blocked research demand")
        if candidate.get("style_pack_id") not in style_ids:
            errors.append(f"candidates[{index}] references unknown style pack")

        source_kind = candidate.get("source_kind")
        manifest_ids = [str(item) for item in candidate.get("manifest_asset_ids") or []]
        if source_kind == "generated_quarantine":
            provider = candidate.get("provider")
            if not isinstance(provider, Mapping) or provider.get("access_path") != "codex_builtin":
                errors.append(f"candidates[{index}] generated media requires provider provenance")
            if candidate.get("rights_status") != "provider_original_pending_operator":
                errors.append(f"candidates[{index}] generated media requires operator rights review")
            if manifest_ids:
                errors.append(f"candidates[{index}] quarantined media cannot claim manifest assets")
            if candidate.get("evidence_eligible") is True:
                errors.append(f"candidates[{index}] generated art cannot be evidence eligible")
        elif source_kind == "approved_manifest":
            if not manifest_ids:
                errors.append(f"candidates[{index}] approved manifest source requires an asset ID")
            for manifest_id in manifest_ids:
                item = manifest_assets.get(manifest_id)
                if item is None or item.get("render_eligible") is not True:
                    errors.append(
                        f"candidates[{index}] manifest asset {manifest_id!r} is not approved"
                    )

        if candidate.get("factual_pixel_risks") and candidate.get("evidence_eligible"):
            errors.append(f"candidates[{index}] pixel risks prohibit evidence use")
        alpha_found = False
        for file_index, record in enumerate(candidate.get("files") or []):
            if not isinstance(record, Mapping):
                continue
            relative = str(record.get("path") or "")
            resolved = (root / relative).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"candidates[{index}].files[{file_index}] escapes project root")
                continue
            if source_kind == "generated_quarantine" and "assets/quarantine/" not in relative.replace("\\", "/"):
                errors.append(f"candidates[{index}] generated file is outside quarantine")
            if not check_files:
                continue
            if not resolved.is_file():
                errors.append(f"candidates[{index}].files[{file_index}] is missing")
                continue
            if _file_sha256(resolved) != record.get("sha256"):
                errors.append(f"candidates[{index}].files[{file_index}] SHA-256 mismatch")
            if resolved.suffix.casefold() in {".png", ".jpg", ".jpeg", ".webp"}:
                try:
                    from PIL import Image

                    with Image.open(resolved) as opened:
                        if opened.width != record.get("width") or opened.height != record.get("height"):
                            errors.append(
                                f"candidates[{index}].files[{file_index}] dimensions mismatch"
                            )
                        if record.get("alpha_required"):
                            alpha_found = alpha_found or "A" in opened.getbands()
                            if "A" not in opened.getbands() or opened.getchannel("A").getextrema()[0] != 0:
                                errors.append(
                                    f"candidates[{index}].files[{file_index}] lacks usable alpha"
                                )
                except OSError as exc:
                    errors.append(f"candidates[{index}].files[{file_index}] is unreadable: {exc}")
        if candidate_class == "character_motion_sheet" and not alpha_found:
            errors.append(f"candidates[{index}] character sheet requires transparent pixels")

    seen_gaps: set[str] = set()
    blocking_gap_count = 0
    for index, gap in enumerate(payload.get("gaps") or []):
        if not isinstance(gap, Mapping):
            continue
        demand_id = str(gap.get("demand_asset_id") or "")
        if demand_id in seen_gaps:
            errors.append(f"gaps[{index}] duplicates demand {demand_id!r}")
        seen_gaps.add(demand_id)
        demand = assets.get(demand_id)
        if demand is None:
            errors.append(f"gaps[{index}] references unknown demand {demand_id!r}")
            continue
        status = gap.get("status")
        if status == "blocked_research" and demand.get("readiness") != "blocked_research":
            errors.append(f"gaps[{index}] falsely marks an approved demand as research blocked")
        if demand.get("readiness") == "blocked_research" and status != "blocked_research":
            errors.append(f"gaps[{index}] must preserve blocked research status")
        if status == "ready_local_recipe" and demand.get("asset_class") not in {
            "fact_surface",
            "transition_motif",
        }:
            errors.append(f"gaps[{index}] local recipe is invalid for this asset class")
        if gap.get("blocks_foundation"):
            blocking_gap_count += 1

    summary = payload.get("summary") or {}
    if isinstance(summary, Mapping):
        if summary.get("candidate_count") != len(payload.get("candidates") or []):
            errors.append("summary candidate_count does not match candidates")
        if summary.get("by_candidate_class") != dict(sorted(class_counts.items())):
            errors.append("summary by_candidate_class does not match candidates")
        if summary.get("gap_count") != len(payload.get("gaps") or []):
            errors.append("summary gap_count does not match gaps")
        if summary.get("blocking_gap_count") != blocking_gap_count:
            errors.append("summary blocking_gap_count does not match gaps")

    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="asset foundation review")
    return payload


def validate_world_pack_library(
    value: Mapping[str, Any] | str | Path,
    *,
    asset_map: Mapping[str, Any] | str | Path | None = None,
    style_pack_library: Mapping[str, Any] | str | Path | None = None,
    expected_grammar_hash: str | None = None,
) -> dict[str, Any]:
    """Validate reusable world planning without promoting images to assets."""

    payload = _load(value, "world pack library")
    errors = _schema_errors(payload, "world_pack.schema.json")
    asset_payload, assets = _asset_index(asset_map)
    _, style_packs = _style_pack_index(style_pack_library)
    if expected_grammar_hash and payload.get("communication_grammar_hash") != expected_grammar_hash:
        errors.append("communication_grammar_hash does not match approved grammar")
    if asset_payload is not None and payload.get("asset_map_id") != asset_payload.get("id"):
        errors.append("asset_map_id does not match the supplied creative asset map")

    seen: set[str] = set()
    for index, pack in enumerate(payload.get("packs") or []):
        if not isinstance(pack, Mapping):
            continue
        pack_id = str(pack.get("id") or "")
        if pack_id in seen:
            errors.append(f"packs[{index}] duplicates id {pack_id!r}")
        seen.add(pack_id)
        if assets:
            _resolve_asset(pack_id, "world", assets, errors, f"packs[{index}]")
            _resolve_asset(
                str(pack.get("style_key_id") or ""),
                "style_key",
                assets,
                errors,
                f"packs[{index}].style_key_id",
            )
            for item in pack.get("ambient_candidates") or []:
                _resolve_asset(str(item), "ambient_loop", assets, errors, f"packs[{index}]")
            for field in ("entry_motif_ids", "exit_motif_ids"):
                for item in pack.get(field) or []:
                    _resolve_asset(
                        str(item), "transition_motif", assets, errors, f"packs[{index}].{field}"
                    )
        if style_packs:
            _resolve_style_pack(
                str(pack.get("style_pack_id") or ""),
                style_packs,
                errors,
                f"packs[{index}].style_pack_id",
            )
        views = [
            str(item.get("view") or "")
            for item in pack.get("plates") or []
            if isinstance(item, Mapping)
        ]
        if len(views) != len(set(views)):
            errors.append(f"packs[{index}] repeats a plate view")
        prompt = str(pack.get("prompt_core") or "").casefold()
        if "in the style of" in prompt:
            errors.append(f"packs[{index}] uses prohibited imitation language")
        negative_text = " ".join(str(item).casefold() for item in pack.get("negative_constraints") or [])
        for token in ("text", "date", "label"):
            if token not in negative_text:
                errors.append(f"packs[{index}] negative constraints must prohibit {token}")
        if (
            pack.get("research_state") == "question_only"
            and pack.get("generation_status") != "blocked_research"
        ):
            errors.append(f"packs[{index}] question-only world must be blocked_research")

    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="world pack library")
    return payload


def validate_scene_bundle(
    value: Mapping[str, Any] | str | Path,
    *,
    asset_map: Mapping[str, Any] | str | Path | None = None,
    style_pack_library: Mapping[str, Any] | str | Path | None = None,
) -> dict[str, Any]:
    """Validate a 20–30 second scene as a meaningful motion bundle."""

    payload = _load(value, "scene bundle")
    errors = _schema_errors(payload, "scene_bundle.schema.json")
    asset_payload, assets = _asset_index(asset_map)
    _, style_packs = _style_pack_index(style_pack_library)
    if asset_payload is not None and payload.get("asset_map_hash") != asset_payload.get("artifact_hash"):
        errors.append("asset_map_hash does not match the supplied creative asset map")
    if style_packs:
        _resolve_style_pack(
            str(payload.get("style_pack_id") or ""),
            style_packs,
            errors,
            "style_pack_id",
        )
    duration = float(payload.get("duration_s") or 0)
    meaningful_motion = False
    for index, event in enumerate(payload.get("micro_events") or []):
        if not isinstance(event, Mapping):
            continue
        if float(event.get("at_s") or 0) >= duration:
            errors.append(f"micro_events[{index}] occurs outside scene duration")
        if event.get("motion_layer") != "camera":
            meaningful_motion = True
    if not meaningful_motion:
        errors.append("scene requires meaningful motion beyond camera movement")

    for index, beat in enumerate(payload.get("narration_beats") or []):
        if not isinstance(beat, Mapping):
            continue
        if beat.get("surface") in {"evidence", "explanation"}:
            if not beat.get("claim_refs") or not beat.get("citation_refs"):
                errors.append(
                    f"narration_beats[{index}] evidence/explanation requires claim and citation refs"
                )
    camera = payload.get("camera") or {}
    if isinstance(camera, Mapping) and camera.get("mode") == "directed_motion" and not str(camera.get("reason") or "").strip():
        errors.append("directed camera motion requires a reason")

    if assets:
        _resolve_asset(str(payload.get("world_asset_id") or ""), "world", assets, errors, "world_asset_id")
        for field, expected in (("character_slots", "character"), ("prop_slots", "prop")):
            for index, slot in enumerate(payload.get(field) or []):
                if isinstance(slot, Mapping):
                    _resolve_asset(str(slot.get("asset_id") or ""), expected, assets, errors, f"{field}[{index}]")
        for index, loop in enumerate(payload.get("ambient_loops") or []):
            if isinstance(loop, Mapping):
                _resolve_asset(str(loop.get("asset_id") or ""), "ambient_loop", assets, errors, f"ambient_loops[{index}]")
        for index, anchor in enumerate(payload.get("fact_anchors") or []):
            if isinstance(anchor, Mapping):
                _resolve_asset(str(anchor.get("fact_surface_id") or ""), "fact_surface", assets, errors, f"fact_anchors[{index}]")
        for state_name in ("entry_state", "exit_state"):
            state = payload.get(state_name) or {}
            if isinstance(state, Mapping):
                _resolve_asset(str(state.get("motif_id") or ""), "transition_motif", assets, errors, state_name)

    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="scene bundle")
    return payload


def validate_scene_flow_graph(
    value: Mapping[str, Any] | str | Path,
    *,
    asset_map: Mapping[str, Any] | str | Path | None = None,
    style_pack_library: Mapping[str, Any] | str | Path | None = None,
    expected_grammar_hash: str | None = None,
) -> dict[str, Any]:
    """Validate foundation scene families and explicit transition continuity."""

    payload = _load(value, "scene flow graph")
    errors = _schema_errors(payload, "scene_flow_graph.schema.json")
    asset_payload, assets = _asset_index(asset_map)
    _, style_packs = _style_pack_index(style_pack_library)
    if expected_grammar_hash and payload.get("communication_grammar_hash") != expected_grammar_hash:
        errors.append("communication_grammar_hash does not match approved grammar")
    if asset_payload is not None and payload.get("asset_map_hash") != asset_payload.get("artifact_hash"):
        errors.append("asset_map_hash does not match the supplied creative asset map")

    scenes_by_id: dict[str, Mapping[str, Any]] = {}
    episode_scenes: dict[str, list[Mapping[str, Any]]] = {}
    for index, scene in enumerate(payload.get("scenes") or []):
        if not isinstance(scene, Mapping):
            continue
        scene_id = str(scene.get("id") or "")
        if scene_id in scenes_by_id:
            errors.append(f"scenes[{index}] duplicates id {scene_id!r}")
        scenes_by_id[scene_id] = scene
        episode = str(scene.get("episode_id") or "")
        episode_scenes.setdefault(episode, []).append(scene)
        if episode in {"episode-2", "episode-3"} and scene.get("research_state") != "question_only":
            errors.append(f"scenes[{index}] {episode} must remain question_only")
        if style_packs:
            _resolve_style_pack(
                str(scene.get("style_pack_id") or ""),
                style_packs,
                errors,
                f"scenes[{index}].style_pack_id",
            )
        if assets:
            _resolve_asset(str(scene.get("world_asset_id") or ""), "world", assets, errors, f"scenes[{index}].world_asset_id")
            for field, expected in (
                ("character_asset_ids", "character"),
                ("prop_asset_ids", "prop"),
                ("fact_surface_ids", "fact_surface"),
                ("ambient_loop_ids", "ambient_loop"),
            ):
                for asset_id in scene.get(field) or []:
                    _resolve_asset(str(asset_id), expected, assets, errors, f"scenes[{index}].{field}")
            for field in ("entry_motif_id", "exit_motif_id"):
                _resolve_asset(str(scene.get(field) or ""), "transition_motif", assets, errors, f"scenes[{index}].{field}")

    expected_pairs: set[tuple[str, str]] = set()
    episode_counts: dict[str, int] = {}
    for episode, scenes in sorted(episode_scenes.items()):
        ordered = sorted(scenes, key=lambda item: int(item.get("order") or 0))
        orders = [int(item.get("order") or 0) for item in ordered]
        if orders != list(range(1, len(ordered) + 1)):
            errors.append(f"{episode} scene order must be consecutive from 1")
        expected_pairs.update(
            (str(left.get("id") or ""), str(right.get("id") or ""))
            for left, right in zip(ordered, ordered[1:])
        )
        episode_counts[episode] = len(ordered)

    edge_pairs: Counter[tuple[str, str]] = Counter()
    for index, edge in enumerate(payload.get("edges") or []):
        if not isinstance(edge, Mapping):
            continue
        pair = (str(edge.get("from") or ""), str(edge.get("to") or ""))
        edge_pairs[pair] += 1
        source = scenes_by_id.get(pair[0])
        target = scenes_by_id.get(pair[1])
        if source is None or target is None:
            errors.append(f"edges[{index}] references an unknown scene")
            continue
        motif = edge.get("motif_id")
        if motif != source.get("exit_motif_id") or motif != target.get("entry_motif_id"):
            errors.append(f"edges[{index}] motif does not join source exit to target entry")
        if assets:
            _resolve_asset(str(motif or ""), "transition_motif", assets, errors, f"edges[{index}].motif_id")
    for pair in sorted(expected_pairs):
        if edge_pairs[pair] != 1:
            errors.append(f"scene transition {pair[0]} -> {pair[1]} requires exactly one edge")
    for pair in sorted(edge_pairs):
        if pair not in expected_pairs:
            errors.append(f"edge {pair[0]} -> {pair[1]} is not an adjacent scene transition")

    summary = payload.get("summary") or {}
    if isinstance(summary, Mapping):
        if summary.get("scene_count") != len(payload.get("scenes") or []):
            errors.append("summary scene_count does not match scenes")
        if summary.get("edge_count") != len(payload.get("edges") or []):
            errors.append("summary edge_count does not match edges")
        if summary.get("episode_counts") != episode_counts:
            errors.append("summary episode_counts does not match scenes")
    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="scene flow graph")
    return payload


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _image_dimensions(path: Path) -> tuple[int, int] | None:
    if path.suffix.casefold() not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return None
    try:
        from PIL import Image

        with Image.open(path) as image:
            return int(image.width), int(image.height)
    except (OSError, ValueError):
        return None


def _media_duration(path: Path) -> float | None:
    if MEDIA_KINDS.get(path.suffix.casefold()) not in {"video", "audio"}:
        return None
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            check=True,
            text=True,
            timeout=20,
        )
        duration = float(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return None
    return round(duration, 6) if duration > 0 else None


def _classification(path: Path, default: str, approved_ids: list[str]) -> str:
    lowered = path.as_posix().casefold()
    if approved_ids:
        return "approved_reusable"
    if "rejected" in lowered:
        return "rejected"
    if "superseded" in lowered:
        return "superseded"
    if "/quarantine/" in lowered or "/provider/" in lowered:
        return "reference_only"
    return default


def _manifest_memberships(
    manifests: Iterable[str | Path], project_root: Path
) -> dict[Path, list[str]]:
    memberships: dict[Path, list[str]] = {}
    for manifest_path in manifests:
        payload = _load(manifest_path, "asset manifest")
        for asset in payload.get("assets") or []:
            if not isinstance(asset, Mapping) or asset.get("render_eligible") is not True:
                continue
            raw_path = str(asset.get("path") or asset.get("local_path") or asset.get("asset_path") or "")
            if not raw_path:
                continue
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = project_root / candidate
            resolved = candidate.resolve()
            memberships.setdefault(resolved, []).append(str(asset.get("id") or resolved.name))
    return memberships


def build_creative_inventory(
    *,
    roots: Mapping[str, str | Path],
    project_root: str | Path,
    asset_manifests: Iterable[str | Path] = (),
    default_classification: str = "reference_only",
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Inventory local media without promoting or modifying any source file."""

    if default_classification not in CLASSIFICATIONS:
        raise ValueError(f"unknown default classification {default_classification!r}")
    project = Path(project_root).resolve()
    memberships = _manifest_memberships(asset_manifests, project)
    root_records: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    seen_roots: set[str] = set()

    for root_id, root_value in roots.items():
        if root_id in seen_roots:
            raise ValueError(f"duplicate root id {root_id!r}")
        seen_roots.add(root_id)
        root = Path(root_value).resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"inventory root is not a directory: {root}")
        root_records.append(
            {
                "id": root_id,
                "path": str(root),
                "default_classification": default_classification,
            }
        )
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().casefold()):
            if not path.is_file():
                continue
            extension = path.suffix.casefold()
            media_kind = MEDIA_KINDS.get(extension)
            if media_kind is None:
                continue
            resolved = path.resolve()
            approved_ids = sorted(set(memberships.get(resolved, [])))
            item: dict[str, Any] = {
                "root_id": root_id,
                "relative_path": path.relative_to(root).as_posix(),
                "sha256": _file_sha256(path),
                "size_bytes": path.stat().st_size,
                "extension": extension,
                "media_kind": media_kind,
                "classification": _classification(path, default_classification, approved_ids),
                "manifest_asset_ids": approved_ids,
            }
            dimensions = _image_dimensions(path)
            if dimensions:
                item["width"], item["height"] = dimensions
            duration = _media_duration(path)
            if duration is not None:
                item["duration_s"] = duration
            items.append(item)

    classification_counts = Counter(item["classification"] for item in items)
    media_counts = Counter(item["media_kind"] for item in items)
    core = {
        "schema_version": CREATIVE_INVENTORY_VERSION,
        "roots": root_records,
        "items": items,
        "summary": {
            "total_items": len(items),
            "by_classification": dict(sorted(classification_counts.items())),
            "by_media_kind": dict(sorted(media_counts.items())),
        },
        "render_eligible": False,
    }
    payload = {**core, "artifact_hash": canonical_sha256(core)}
    if output_path is not None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def validate_creative_inventory(
    value: Mapping[str, Any] | str | Path,
    *,
    check_files: bool = True,
) -> dict[str, Any]:
    payload = _load(value, "creative inventory")
    errors = _schema_errors(payload, "creative_inventory.schema.json")
    roots: dict[str, Path] = {}
    for index, root in enumerate(payload.get("roots") or []):
        if not isinstance(root, Mapping):
            continue
        root_id = str(root.get("id") or "")
        try:
            resolved = Path(str(root.get("path") or "")).resolve(strict=check_files)
        except OSError as exc:
            errors.append(f"roots[{index}] does not exist: {exc}")
            continue
        if root_id in roots:
            errors.append(f"duplicate root id {root_id!r}")
        roots[root_id] = resolved

    seen: set[tuple[str, str]] = set()
    classifications: Counter[str] = Counter()
    media_kinds: Counter[str] = Counter()
    for index, item in enumerate(payload.get("items") or []):
        if not isinstance(item, Mapping):
            continue
        root_id = str(item.get("root_id") or "")
        relative = str(item.get("relative_path") or "")
        key = (root_id, relative.casefold())
        if key in seen:
            errors.append(f"items[{index}] duplicates {root_id}:{relative}")
        seen.add(key)
        classifications[str(item.get("classification") or "")] += 1
        media_kinds[str(item.get("media_kind") or "")] += 1
        root = roots.get(root_id)
        if root is None:
            errors.append(f"items[{index}] references unknown root {root_id!r}")
            continue
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"items[{index}] escapes inventory root")
            continue
        if check_files:
            if not candidate.is_file():
                errors.append(f"items[{index}] file is missing: {candidate}")
            elif _file_sha256(candidate) != item.get("sha256"):
                errors.append(f"items[{index}] SHA-256 does not match {candidate}")

    summary = payload.get("summary") or {}
    if isinstance(summary, Mapping):
        if summary.get("total_items") != len(payload.get("items") or []):
            errors.append("summary total_items does not match items")
        if summary.get("by_classification") != dict(sorted(classifications.items())):
            errors.append("summary by_classification does not match items")
        if summary.get("by_media_kind") != dict(sorted(media_kinds.items())):
            errors.append("summary by_media_kind does not match items")
    hash_error = _artifact_hash_error(payload)
    if hash_error:
        errors.append(hash_error)
    if errors:
        raise LivingSceneValidationError(errors, contract="creative inventory")
    return payload


__all__ = [
    "ASSET_FOUNDATION_REVIEW_VERSION",
    "COMMUNICATION_GRAMMAR_VERSION",
    "CREATIVE_ASSET_MAP_VERSION",
    "CREATIVE_INVENTORY_VERSION",
    "LivingSceneValidationError",
    "SCENE_BUNDLE_VERSION",
    "SCENE_FLOW_GRAPH_VERSION",
    "STYLE_PACK_LIBRARY_VERSION",
    "WORLD_PACK_LIBRARY_VERSION",
    "build_creative_inventory",
    "build_default_communication_grammar",
    "validate_communication_grammar",
    "validate_asset_foundation_review",
    "validate_creative_asset_map",
    "validate_creative_inventory",
    "validate_scene_bundle",
    "validate_scene_flow_graph",
    "validate_style_pack_library",
    "validate_world_pack_library",
]
