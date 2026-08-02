from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.living_scenes import (
    LivingSceneValidationError,
    build_default_communication_grammar,
    validate_asset_foundation_review,
    validate_creative_asset_map,
    validate_scene_bundle,
    validate_scene_flow_graph,
    validate_style_pack_library,
    validate_world_pack_library,
)


def _rehash(payload: dict) -> dict:
    payload["artifact_hash"] = canonical_sha256(payload)
    return payload


def _asset(
    asset_id: str,
    asset_class: str,
    *,
    role: str | None = None,
    episode: str = "episode-1",
    state: str = "approved",
    readiness: str = "demanded",
) -> dict:
    result = {
        "id": asset_id,
        "label": asset_id.replace("-", " "),
        "asset_class": asset_class,
        "readiness": readiness,
        "episodes": [episode],
        "uses": [
            {
                "episode_id": episode,
                "role": "test demand",
                "research_state": state,
            }
        ],
        "recurrence_count": 1,
        "reuse_priority": 3,
        "dependencies": [],
        "manifest_asset_ids": [],
        "source_strategy": "local_deterministic",
        "generation_needed": False,
        "motion_needed": asset_class != "style_key",
        "animation_ready": asset_class in {"fact_surface", "transition_motif"},
        "evidence_eligible": asset_class == "fact_surface",
        "render_eligible": False,
    }
    if role is not None:
        result["character_role"] = role
    return result


def _asset_map() -> dict:
    grammar_hash = build_default_communication_grammar()["artifact_hash"]
    assets = [
        _asset("style-key", "style_key", state="none"),
        _asset("narrator", "character", role="narrator", state="none"),
        _asset("world-one", "world"),
        _asset("prop-one", "prop", state="none"),
        _asset("ambient-one", "ambient_loop", state="none"),
        _asset("fact-one", "fact_surface"),
        _asset("transition-one", "transition_motif", state="none"),
    ]
    core = {
        "schema_version": "creative_asset_map.v1",
        "id": "test-assets",
        "series_id": "test-series",
        "communication_grammar_hash": grammar_hash,
        "policy": {
            "no_undemanded_generation": True,
            "actual_assets_resolve_through_manifest": True,
            "asset_ceilings": {
                "style_key": 1,
                "narrator": 1,
                "historical_character": 0,
                "world": 1,
                "prop": 1,
                "ambient_loop": 1,
                "fact_surface": 1,
                "transition_motif": 1,
            },
            "fallbacks": {
                "style_key": "use local grammar",
                "character": "omit character",
                "world": "use clean background",
                "prop": "omit prop",
                "archive": "use citation card",
                "ambient_loop": "hold still",
                "fact_surface": "use fact folio",
                "transition_motif": "use hard cut",
                "scene_plate": "use reusable world",
            },
        },
        "assets": assets,
        "summary": {
            "total_assets": len(assets),
            "by_class": {
                "ambient_loop": 1,
                "character": 1,
                "fact_surface": 1,
                "prop": 1,
                "style_key": 1,
                "transition_motif": 1,
                "world": 1,
            },
            "by_readiness": {"demanded": 7},
        },
        "render_eligible": False,
    }
    return _rehash(core)


def _world_library(asset_map: dict) -> dict:
    core = {
        "schema_version": "world_pack_library.v1",
        "id": "test-worlds",
        "communication_grammar_hash": asset_map["communication_grammar_hash"],
        "asset_map_id": asset_map["id"],
        "packs": [
            {
                "id": "world-one",
                "label": "World one",
                "episodes": ["episode-1"],
                "research_state": "approved",
                "reuse_priority": 3,
                "narrative_functions": ["test scene"],
                "style_key_id": "style-key",
                "style_pack_id": "woodblock-historical-editorial-v1",
                "plates": [
                    {
                        "view": "master_establishing",
                        "composition": "wide layered world",
                        "character_staging": ["narrator at left"],
                        "fact_anchors": ["fact at right"],
                    },
                    {
                        "view": "clean_background",
                        "composition": "same world without characters",
                        "character_staging": [],
                        "fact_anchors": ["fact at right"],
                    },
                ],
                "ambient_candidates": ["ambient-one"],
                "entry_motif_ids": ["transition-one"],
                "exit_motif_ids": ["transition-one"],
                "prompt_core": "Original flat-color layered environment with thick outlines and a stable locked camera for character staging.",
                "negative_constraints": [
                    "no generated text",
                    "no generated dates",
                    "no generated labels",
                ],
                "generation_status": "planned",
                "render_eligible": False,
            }
        ],
        "render_eligible": False,
    }
    return _rehash(core)


def _scene_bundle(asset_map: dict) -> dict:
    core = {
        "schema_version": "scene_bundle.v1",
        "id": "test-scene",
        "episode_id": "episode-1",
        "communication_grammar_hash": asset_map["communication_grammar_hash"],
        "asset_map_hash": asset_map["artifact_hash"],
        "style_pack_id": "woodblock-historical-editorial-v1",
        "duration_s": 25,
        "narration_beats": [
            {
                "id": "beat-one",
                "text": "Picture the world.",
                "surface": "world",
                "claim_refs": [],
                "citation_refs": [],
            },
            {
                "id": "beat-two",
                "text": "The record supports this claim.",
                "surface": "evidence",
                "claim_refs": ["claim-one"],
                "citation_refs": ["citation-one"],
            },
        ],
        "world_asset_id": "world-one",
        "depth_layers": ["foreground", "midground", "background"],
        "character_slots": [
            {
                "id": "guide",
                "asset_id": "narrator",
                "staging": "left third",
                "actions": ["open prop"],
            }
        ],
        "prop_slots": [
            {
                "id": "object",
                "asset_id": "prop-one",
                "staging": "center",
                "actions": ["open"],
            }
        ],
        "ambient_loops": [
            {
                "asset_id": "ambient-one",
                "mask_id": "water-mask",
                "region": "lower background",
                "camera_locked": True,
            }
        ],
        "fact_anchors": [
            {
                "id": "fact-anchor",
                "fact_surface_id": "fact-one",
                "safe_zone": "right third",
            }
        ],
        "micro_events": [
            {"at_s": 2, "motion_layer": "character_prop", "action": "guide opens prop"},
            {"at_s": 8, "motion_layer": "information_reveal", "action": "fact card appears"},
        ],
        "entry_state": {
            "motif_id": "transition-one",
            "connector_type": "object",
            "description": "prop enters frame",
        },
        "exit_state": {
            "motif_id": "transition-one",
            "connector_type": "object",
            "description": "prop carries into next scene",
        },
        "camera": {"mode": "locked", "reason": "character and overlay motion own the beat"},
        "fallback": "Use the clean world plate with local character and fact layers.",
        "render_eligible": False,
    }
    return _rehash(core)


def _scene_flow(asset_map: dict) -> dict:
    def scene(scene_id: str, order: int) -> dict:
        return {
            "id": scene_id,
            "episode_id": "episode-1",
            "order": order,
            "title": scene_id,
            "purpose": "Test a meaningful scene family.",
            "research_state": "approved",
            "style_pack_id": "woodblock-historical-editorial-v1",
            "target_duration_s": 25,
            "narration_beats_target": 3,
            "world_asset_id": "world-one",
            "character_asset_ids": ["narrator"],
            "prop_asset_ids": ["prop-one"],
            "fact_surface_ids": ["fact-one"],
            "ambient_loop_ids": ["ambient-one"],
            "entry_motif_id": "transition-one",
            "exit_motif_id": "transition-one",
        }

    core = {
        "schema_version": "scene_flow_graph.v1",
        "id": "test-flow",
        "series_id": "test-series",
        "planning_scope": "foundation_scene_families",
        "communication_grammar_hash": asset_map["communication_grammar_hash"],
        "asset_map_hash": asset_map["artifact_hash"],
        "policy": {
            "catalog_layout_reused": True,
            "one_or_two_motifs_per_chapter": True,
            "question_briefs_are_not_claims": True,
        },
        "scenes": [scene("scene-one", 1), scene("scene-two", 2)],
        "edges": [
            {
                "from": "scene-one",
                "to": "scene-two",
                "connector_type": "object",
                "motif_id": "transition-one",
                "cut_point": "result",
                "rationale": "The same prop carries through the cut.",
            }
        ],
        "summary": {
            "scene_count": 2,
            "edge_count": 1,
            "episode_counts": {"episode-1": 2},
        },
        "render_eligible": False,
    }
    return _rehash(core)


def _style_packs(asset_map: dict) -> dict:
    def pack(
        pack_id: str,
        lanes: list[str],
        *,
        negative_space: tuple[float, float],
        turnaround: str,
        fighter_color: bool,
        cuts: list[str],
    ) -> dict:
        return {
            "id": pack_id,
            "label": pack_id.replace("-", " "),
            "primary_lanes": lanes,
            "audience_job": "Communicate one clear visual job through the shared woodblock identity.",
            "composition": {
                "panel_count_min": 1,
                "panel_count_max": 3,
                "negative_space_min": negative_space[0],
                "negative_space_max": negative_space[1],
                "depth_layers_min": 2,
                "camera_default": "locked",
                "layout_rules": ["preserve silhouette", "reserve local overlay space"],
            },
            "motion": {
                "primary_drivers": ["character_prop", "information_reveal"],
                "background_motion": "localized_only",
                "action_cut_points": cuts,
                "transition_motifs": ["paper transition"],
            },
            "character_policy": {
                "silhouette_priority": "high",
                "identity_reference_required": True,
                "fighter_color_ownership": fighter_color,
            },
            "information_policy": {
                "facts_rendered_locally": True,
                "evidence_surfaces_local": True,
                "preferred_surfaces": ["fact folio"],
            },
            "production": {
                "turnaround_class": turnaround,
                "required_asset_slots": ["subject", "background"],
                "stress_tests": ["silhouette", "safe zone", "vertical crop"],
                "fallback": "Use a static reviewed subject with a local fact folio.",
            },
            "prompt_core": "Original woodblock print composition with warm paper, carved indigo lines, flat registered color, stable staging, and clean local overlay space.",
            "negative_constraints": [
                "no generated text",
                "no generated dates",
                "no generated labels",
                "no generated logos",
            ],
            "status": "demanded",
            "render_eligible": False,
        }

    core = {
        "schema_version": "style_pack_library.v1",
        "id": "test-style-packs",
        "parent_style_key_id": "style-key",
        "calibration_inventory_hash": "a" * 64,
        "calibration_policy": {
            "use": "human_directed_style_calibration",
            "overlap_allowed": True,
            "promotion_requires_asset_manifest": True,
            "render_eligible": False,
        },
        "shared_identity": {
            "name": "Test Woodblock",
            "medium": "woodblock_print",
            "palette": ["#E7D3A1", "#17324D", "#1B1A17", "#B64F36"],
            "linework": "thick carved outlines",
            "texture": "warm paper grain",
            "visual_motifs": ["sun disc", "ink wave", "paper panel"],
            "factual_text_in_generated_pixels": False,
            "creator_imitation": False,
        },
        "packs": [
            pack(
                "woodblock-anime-action-v1",
                ["technique_analysis", "fight_analysis"],
                negative_space=(0.1, 0.3),
                turnaround="standard",
                fighter_color=True,
                cuts=["anticipation", "contact", "recoil", "result"],
            ),
            pack(
                "woodblock-historical-editorial-v1",
                ["history"],
                negative_space=(0.2, 0.4),
                turnaround="premium",
                fighter_color=False,
                cuts=["anticipation", "result"],
            ),
            pack(
                "woodblock-comic-whitespace-v1",
                ["trending_response"],
                negative_space=(0.4, 0.65),
                turnaround="rapid",
                fighter_color=False,
                cuts=["result"],
            ),
        ],
        "render_eligible": False,
    }
    return _rehash(core)


def test_living_scene_contracts_validate_together() -> None:
    asset_map = validate_creative_asset_map(_asset_map())
    style_packs = validate_style_pack_library(
        _style_packs(asset_map), asset_map=asset_map
    )
    assert validate_world_pack_library(
        _world_library(asset_map),
        asset_map=asset_map,
        style_pack_library=style_packs,
    )["packs"][0]["id"] == "world-one"
    assert validate_scene_bundle(
        _scene_bundle(asset_map),
        asset_map=asset_map,
        style_pack_library=style_packs,
    )["id"] == "test-scene"
    assert validate_scene_flow_graph(
        _scene_flow(asset_map),
        asset_map=asset_map,
        style_pack_library=style_packs,
    )["summary"]["edge_count"] == 1


def test_style_packs_reject_imitation_and_weak_whitespace() -> None:
    asset_map = _asset_map()
    payload = _style_packs(asset_map)
    payload["packs"][0]["prompt_core"] = (
        "Create this visual in the style of a named creator while retaining enough words for schema validation."
    )
    payload["packs"][2]["composition"]["negative_space_min"] = 0.2
    _rehash(payload)
    with pytest.raises(LivingSceneValidationError, match="imitation|35%"):
        validate_style_pack_library(payload, asset_map=asset_map)


def test_asset_map_blocks_question_only_generation_and_ceiling_drift() -> None:
    payload = _asset_map()
    payload["assets"][2]["uses"][0]["research_state"] = "question_only"
    payload["assets"][2]["generation_needed"] = True
    _rehash(payload)
    with pytest.raises(LivingSceneValidationError, match="question-only"):
        validate_creative_asset_map(payload)

    ceiling = _asset_map()
    ceiling["policy"]["asset_ceilings"]["world"] = 0
    _rehash(ceiling)
    with pytest.raises(LivingSceneValidationError, match="asset ceiling"):
        validate_creative_asset_map(ceiling)

    malformed = _asset_map()
    malformed["policy"] = []
    _rehash(malformed)
    with pytest.raises(LivingSceneValidationError, match="schema policy"):
        validate_creative_asset_map(malformed)


def test_world_pack_rejects_imitation_language_and_generated_labels() -> None:
    asset_map = _asset_map()
    payload = _world_library(asset_map)
    payload["packs"][0]["prompt_core"] = (
        "Create this environment in the style of a named creator with enough words to pass length."
    )
    payload["packs"][0]["negative_constraints"] = [
        "no text",
        "no dates",
        "no logos",
    ]
    _rehash(payload)
    with pytest.raises(LivingSceneValidationError, match="imitation|labels"):
        validate_world_pack_library(payload, asset_map=asset_map)


def test_scene_bundle_rejects_camera_only_motion_and_uncited_evidence() -> None:
    asset_map = _asset_map()
    payload = _scene_bundle(asset_map)
    for event in payload["micro_events"]:
        event["motion_layer"] = "camera"
    payload["narration_beats"][1]["citation_refs"] = []
    _rehash(payload)
    with pytest.raises(
        LivingSceneValidationError,
        match="meaningful motion|claim and citation",
    ):
        validate_scene_bundle(payload, asset_map=asset_map)


def test_scene_flow_rejects_research_leakage_and_broken_transition() -> None:
    asset_map = _asset_map()
    payload = _scene_flow(asset_map)
    payload["scenes"][1]["episode_id"] = "episode-2"
    payload["scenes"][1]["order"] = 1
    payload["scenes"][1]["research_state"] = "approved"
    payload["summary"]["episode_counts"] = {"episode-1": 1, "episode-2": 1}
    _rehash(payload)
    with pytest.raises(LivingSceneValidationError, match="question_only|adjacent"):
        validate_scene_flow_graph(payload, asset_map=asset_map)

    broken = _scene_flow(asset_map)
    broken["scenes"][1]["entry_motif_id"] = "different-transition"
    _rehash(broken)
    with pytest.raises(LivingSceneValidationError, match="motif"):
        validate_scene_flow_graph(broken, asset_map=asset_map)


def _foundation_review(tmp_path: Path) -> tuple[dict, dict, dict, dict, dict, dict]:
    asset_map = _asset_map()
    style_packs = _style_packs(asset_map)
    world_packs = _world_library(asset_map)
    reference_root = tmp_path / "references"
    reference_root.mkdir()
    inventory = _rehash(
        {
            "schema_version": "creative_inventory.v1",
            "roots": [
                {
                    "id": "references",
                    "path": str(reference_root),
                    "default_classification": "reference_only",
                }
            ],
            "items": [],
            "summary": {
                "total_items": 0,
                "by_classification": {},
                "by_media_kind": {},
            },
            "render_eligible": False,
        }
    )
    manifest = {"schema_version": "asset_manifest.v1", "assets": []}
    relative = Path("content/assets/quarantine/world.png")
    image_path = tmp_path / relative
    image_path.parent.mkdir(parents=True)
    Image.new("RGB", (32, 18), "#ead7ae").save(image_path)
    review = {
        "schema_version": "asset_foundation_review.v1",
        "id": "test-foundation",
        "series_id": "test-series",
        "episode_id": "test-episode",
        "immutable_inputs": {
            "asset_map_hash": asset_map["artifact_hash"],
            "world_pack_hash": world_packs["artifact_hash"],
            "style_pack_hash": style_packs["artifact_hash"],
            "calibration_inventory_hash": inventory["artifact_hash"],
            "asset_manifest_hash": canonical_sha256(manifest),
        },
        "policy": {
            "image_generation_authorized": True,
            "animation_generation_authorized": False,
            "voice_generation_authorized": False,
            "automatic_promotion": False,
            "facts_rendered_locally": True,
            "generated_art_is_evidence": False,
        },
        "candidates": [
            {
                "id": "candidate-world",
                "demand_asset_id": "world-one",
                "candidate_class": "world_master",
                "source_kind": "generated_quarantine",
                "provider": {
                    "name": "test generator",
                    "model": "fixture",
                    "access_path": "codex_builtin",
                },
                "style_pack_id": "woodblock-historical-editorial-v1",
                "files": [
                    {
                        "role": "master",
                        "path": relative.as_posix(),
                        "sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
                        "width": 32,
                        "height": 18,
                        "alpha_required": False,
                    }
                ],
                "manifest_asset_ids": [],
                "rights_status": "provider_original_pending_operator",
                "identity_status": "not_applicable",
                "composition_status": "strong_master",
                "motion_status": "localized_regions_unmasked",
                "evidence_eligible": False,
                "factual_pixel_risks": [],
                "required_followups": ["operator composition approval"],
                "render_eligible": False,
            }
        ],
        "gaps": [],
        "summary": {
            "candidate_count": 1,
            "by_candidate_class": {"world_master": 1},
            "gap_count": 0,
            "blocking_gap_count": 0,
        },
        "review": {
            "status": "awaiting_asset_foundation_gate",
            "gate": "asset_foundation",
            "required_decisions": ["approve world"],
        },
        "render_eligible": False,
    }
    return _rehash(review), asset_map, world_packs, style_packs, inventory, manifest


def test_foundation_review_validates_quarantine_hashes_and_rejects_drift(
    tmp_path: Path,
) -> None:
    review, asset_map, world_packs, style_packs, inventory, manifest = (
        _foundation_review(tmp_path)
    )
    assert validate_asset_foundation_review(
        review,
        asset_map=asset_map,
        world_packs=world_packs,
        style_packs=style_packs,
        calibration_inventory=inventory,
        asset_manifest=manifest,
        project_root=tmp_path,
    )["id"] == "test-foundation"

    stale = copy.deepcopy(review)
    stale["candidates"][0]["files"][0]["sha256"] = "f" * 64
    _rehash(stale)
    with pytest.raises(LivingSceneValidationError, match="SHA-256 mismatch"):
        validate_asset_foundation_review(
            stale,
            asset_map=asset_map,
            world_packs=world_packs,
            style_packs=style_packs,
            calibration_inventory=inventory,
            asset_manifest=manifest,
            project_root=tmp_path,
        )
