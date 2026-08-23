from __future__ import annotations

import copy

import pytest

from content.video_engine.src.services.editorial_motion import (
    EditorialMotionError,
    _contextual_visual_intent_and_actions,
    _visual_intent_and_actions,
    analyze_timestamped_semantic_coverage,
    build_default_pacing_recipe,
    compile_canonical_visual_coverage,
    compile_editorial_motion_plan,
    compile_timestamped_editorial_motion_plan,
    derive_editorial_motion_sample,
    validate_editorial_motion_plan,
)
from content.video_engine.src.services.history_contracts import canonical_sha256


def _hashed(core: dict) -> dict:
    return {**core, "artifact_hash": canonical_sha256(core)}


def _inputs() -> dict:
    story = {"schema_version": "2.3.0", "source": {"kind": "history_episode"}, "scenes": []}
    story_hash = canonical_sha256(story)
    narration = _hashed(
        {
            "schema_version": "history_narration.v1",
            "source_storyboard_hash": story_hash,
            "narration_hash": "1" * 64,
            "segments": [
                {
                    "segment_id": "opening",
                    "claim_refs": ["claim-one"],
                    "citation_refs": ["citation-one"],
                    "text": "One two three. Four five six.",
                }
            ],
        }
    )
    audio = _hashed(
        {
            "schema_version": "elevenlabs_canonical_audio.v1",
            "status": "ready",
            "narration_hash": "1" * 64,
            "duration_s": 3.0,
        }
    )
    beats = _hashed(
        {
            "schema_version": "editorial_beat_plan.v1",
            "source_storyboard_hash": story_hash,
            "duration_s": 9.0,
            "beat_count": 3,
            "beats": [
                {"beat_id": "beat-one", "narration_excerpt": "One two three."},
                {"beat_id": "beat-one-visual-b", "narration_excerpt": "One two three."},
                {"beat_id": "beat-two", "narration_excerpt": "Four five six."},
            ],
        }
    )
    words = {
        "words": [
            {"w": "One", "start_s": 0.0, "end_s": 0.35},
            {"w": "two", "start_s": 0.4, "end_s": 0.7},
            {"w": "three.", "start_s": 0.75, "end_s": 1.0},
            {"w": "Four", "start_s": 1.4, "end_s": 1.7},
            {"w": "five", "start_s": 1.75, "end_s": 2.1},
            {"w": "six.", "start_s": 2.2, "end_s": 2.55},
        ]
    }
    bundle = _hashed({"schema_version": "scene_bundle.v1", "id": "bundle-one"})
    flow = _hashed({"schema_version": "scene_flow_graph.v1", "id": "flow-one"})
    asset_map = _hashed({"assets": {"world-one": {}, "prop-one": {}}})
    shots = [
        {
            "shot_id": "shot-one",
            "word_range": {"start_index": 0, "end_index": 2},
            "parent_beat_ids": ["beat-one", "beat-one-visual-b"],
            "parent_scene_bundle_id": "bundle-one",
            "purpose": "establish",
            "shot_scale": "wide",
            "focal_point": {"x": 0.5, "y": 0.45},
            "layers": [{"asset_id": "world-one", "role": "world"}],
            "subject_action": "none",
            "ambient_actions": ["lamp_flicker"],
            "information_reveal": "none",
            "camera": {"kind": "locked"},
            "transition_in": {"kind": "hard_cut", "reason": "opening"},
            "transition_out": {
                "kind": "match_cut",
                "reason": "shared circle",
                "motif_id": "motif-circle",
            },
            "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
            "overlay_ids": [],
            "uniqueness_signature": "wide-world-locked-ambient",
        },
        {
            "shot_id": "shot-two",
            "word_range": {"start_index": 3, "end_index": 5},
            "parent_beat_ids": ["beat-two"],
            "parent_scene_bundle_id": "bundle-one",
            "purpose": "detail",
            "shot_scale": "insert",
            "focal_point": {"x": 0.7, "y": 0.5},
            "layers": [{"asset_id": "prop-one", "role": "prop"}],
            "subject_action": "none",
            "ambient_actions": [],
            "information_reveal": "citation-one",
            "camera": {"kind": "push_settle", "amount": 0.018},
            "transition_in": {"kind": "hard_cut", "reason": "word boundary"},
            "transition_out": {"kind": "hard_cut", "reason": "proof end"},
            "provider_motion": {"requirement": "none", "fallback": "local_layer_motion"},
            "overlay_ids": ["citation-one"],
            "uniqueness_signature": "insert-prop-push-evidence",
        },
    ]
    return {
        "storyboard": story,
        "beat_plan": beats,
        "narration_plan": narration,
        "audio_manifest": audio,
        "word_timings": words,
        "pacing_recipe": build_default_pacing_recipe(),
        "shot_specs": shots,
        "scene_bundles": [bundle],
        "scene_flow_graph": flow,
        "asset_map": asset_map,
        "source_end_s": 3.0,
    }


def test_compile_binds_explicit_shots_to_words_without_repeating_audio() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    assert plan["duration_s"] == 3.0
    assert len(plan["shots"]) == 2
    assert plan["shots"][0]["parent_beat_ids"] == ["beat-one", "beat-one-visual-b"]
    assert plan["shots"][0]["narration_excerpt"] == "One two three."
    assert plan["shots"][1]["start_s"] == 1.4
    assert plan["shots"][1]["word_range"] == {"start_index": 3, "end_index": 5}
    assert plan["provider_calls"] == 0


def test_compile_explicit_shot_timing_preserves_authored_midpoint_pause() -> None:
    inputs = _inputs()
    legacy = compile_editorial_motion_plan(**inputs)
    explicit = compile_editorial_motion_plan(
        **inputs,
        explicit_shot_timing=[
            {"start_s": 0.0, "end_s": 1.2},
            {"start_s": 1.2, "end_s": 3.0},
        ],
    )

    assert legacy["shots"][1]["start_s"] == 1.4
    assert explicit["shots"][0]["duration_s"] == 1.2
    assert explicit["shots"][1]["start_s"] == 1.2
    assert explicit["duration_s"] == 3.0


def test_explicit_timing_allows_subframe_final_word_rounding_only() -> None:
    inputs = _inputs()
    inputs["word_timings"]["words"][-1]["end_s"] = 3.001
    explicit = compile_editorial_motion_plan(
        **inputs,
        explicit_shot_timing=[
            {"start_s": 0.0, "end_s": 1.2},
            {"start_s": 1.2, "end_s": 3.0},
        ],
    )
    assert explicit["duration_s"] == 3.0

    inputs["word_timings"]["words"][-1]["end_s"] = 3.02
    with pytest.raises(EditorialMotionError, match="cuts off"):
        compile_editorial_motion_plan(
            **inputs,
            explicit_shot_timing=[
                {"start_s": 0.0, "end_s": 1.2},
                {"start_s": 1.2, "end_s": 3.0},
            ],
        )


def test_compile_is_deterministic() -> None:
    first = compile_editorial_motion_plan(**_inputs())
    second = compile_editorial_motion_plan(**_inputs())
    assert first == second
    assert first["artifact_hash"] == second["artifact_hash"]


def test_editorial_motion_sample_requires_an_authored_cut_boundary() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    sample = derive_editorial_motion_sample(
        plan,
        end_s=1.4,
        known_asset_ids={"world-one", "prop-one"},
    )
    assert sample["duration_s"] == 1.4
    assert len(sample["shots"]) == 1
    with pytest.raises(EditorialMotionError, match="authored shot boundary"):
        derive_editorial_motion_sample(
            plan,
            end_s=1.2,
            known_asset_ids={"world-one", "prop-one"},
        )


def test_compile_rejects_audio_narration_mismatch() -> None:
    values = _inputs()
    values["audio_manifest"] = _hashed(
        {**{key: value for key, value in values["audio_manifest"].items() if key != "artifact_hash"}, "narration_hash": "9" * 64}
    )
    with pytest.raises(EditorialMotionError, match="narration hash"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_stale_source_artifact_hashes() -> None:
    values = _inputs()
    values["beat_plan"]["duration_s"] = 99.0
    with pytest.raises(EditorialMotionError, match="editorial beat plan artifact_hash is stale"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_stale_asset_map_hash() -> None:
    values = _inputs()
    values["asset_map"]["assets"]["world-two"] = {}
    with pytest.raises(EditorialMotionError, match="asset map artifact_hash is stale"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_excerpt_past_audio_duration() -> None:
    values = _inputs()
    values["audio_manifest"] = _hashed(
        {
            **{
                key: value
                for key, value in values["audio_manifest"].items()
                if key != "artifact_hash"
            },
            "duration_s": 2.75,
        }
    )
    with pytest.raises(EditorialMotionError, match="exceeds the canonical audio duration"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_word_gap_or_overlap() -> None:
    values = _inputs()
    values["shot_specs"][1]["word_range"] = {"start_index": 4, "end_index": 5}
    with pytest.raises(EditorialMotionError, match="not contiguous"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_missing_next_shot_word_start_as_contract_error() -> None:
    values = _inputs()
    values["shot_specs"][1]["word_range"].pop("start_index")
    with pytest.raises(
        EditorialMotionError,
        match=r"shot_specs\[1\]\.word_range\.start_index must be an integer",
    ):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_unknown_asset_id() -> None:
    values = _inputs()
    values["shot_specs"][0]["layers"][0]["asset_id"] = "unknown-world"
    with pytest.raises(EditorialMotionError, match="unknown asset"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_moving_camera_without_matching_phases() -> None:
    values = _inputs()
    values["shot_specs"][1]["camera"] = {
        "kind": "push_settle",
        "amount": 0.02,
        "hold_in_s": 0.1,
        "move_s": 0.1,
        "hold_out_s": 0.1,
    }
    with pytest.raises(EditorialMotionError, match="phases must equal"):
        compile_editorial_motion_plan(**values)


def test_compile_rejects_unmotivated_crossfade() -> None:
    values = _inputs()
    values["shot_specs"][0]["transition_out"] = {
        "kind": "crossfade",
        "duration_s": 0.5,
        "reason": "decorative",
    }
    with pytest.raises(EditorialMotionError, match="time_or_place_change"):
        compile_editorial_motion_plan(**values)


def test_validate_rejects_locked_camera_motion_and_camera_only_event() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    invalid = copy.deepcopy(plan)
    invalid["shots"][0]["camera"]["amount"] = 0.02
    invalid["shots"][1]["layers"] = [{"asset_id": "world-one", "role": "world"}]
    invalid["shots"][1]["subject_action"] = "none"
    invalid["shots"][1]["ambient_actions"] = []
    invalid["shots"][1]["information_reveal"] = "none"
    invalid["artifact_hash"] = canonical_sha256({key: value for key, value in invalid.items() if key != "artifact_hash"})
    with pytest.raises(EditorialMotionError) as exc:
        validate_editorial_motion_plan(invalid, known_asset_ids={"world-one", "prop-one"})
    assert "locked camera" in str(exc.value)
    assert "no positive visual event" in str(exc.value)


def test_validate_accepts_a_new_relevant_asset_as_the_visual_event() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    revised = copy.deepcopy(plan)
    revised["shots"][0]["ambient_actions"] = []
    revised["shots"][1]["subject_action"] = "none"
    revised["shots"][1]["ambient_actions"] = []
    revised["shots"][1]["information_reveal"] = "none"
    revised["shots"][1]["camera"] = {
        "kind": "locked",
        "amount": 0.0,
        "easing": "smoothstep",
        "direction": "toward_focal_point",
        "hold_in_s": revised["shots"][1]["duration_s"],
        "move_s": 0.0,
        "hold_out_s": 0.0,
    }
    revised["artifact_hash"] = canonical_sha256(
        {key: value for key, value in revised.items() if key != "artifact_hash"}
    )
    assert validate_editorial_motion_plan(
        revised,
        known_asset_ids={"world-one", "prop-one"},
    )["shots"][1]["layers"][0]["asset_id"] == "prop-one"


def test_validate_rejects_deletion_as_the_only_visual_event() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    invalid = copy.deepcopy(plan)
    invalid["shots"][0]["layers"].append({"asset_id": "prop-one", "role": "prop"})
    invalid["shots"][1]["layers"] = [{"asset_id": "world-one", "role": "world"}]
    invalid["shots"][1]["subject_action"] = "none"
    invalid["shots"][1]["ambient_actions"] = []
    invalid["shots"][1]["information_reveal"] = "none"
    invalid["shots"][1]["camera"] = {
        "kind": "locked",
        "amount": 0.0,
        "easing": "smoothstep",
        "direction": "toward_focal_point",
        "hold_in_s": invalid["shots"][1]["duration_s"],
        "move_s": 0.0,
        "hold_out_s": 0.0,
    }
    invalid["artifact_hash"] = canonical_sha256(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )
    with pytest.raises(EditorialMotionError, match="removing assets alone is not a visual event"):
        validate_editorial_motion_plan(invalid, known_asset_ids={"world-one", "prop-one"})


def test_validate_rejects_stale_artifact_hash() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    plan["shots"][0]["purpose"] = "hook"
    with pytest.raises(EditorialMotionError, match="artifact_hash is stale"):
        validate_editorial_motion_plan(plan)


def test_schema_rejects_invalid_focal_point() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    plan["shots"][0]["focal_point"]["x"] = 1.2
    plan["artifact_hash"] = canonical_sha256({key: value for key, value in plan.items() if key != "artifact_hash"})
    with pytest.raises(EditorialMotionError, match="greater than the maximum"):
        validate_editorial_motion_plan(plan)


def test_schema_accepts_bounded_character_layer_layout() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    plan["shots"][1]["layers"][0]["layout"] = {
        "x": 0.62,
        "y": 0.18,
        "width": 0.3,
        "height": 0.74,
        "fit": "contain",
    }
    plan["artifact_hash"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "artifact_hash"}
    )
    assert validate_editorial_motion_plan(plan)["shots"][1]["layers"][0]["layout"]["x"] == 0.62


def test_compile_requires_a_contained_layout_for_archival_portraits() -> None:
    values = _inputs()
    values["asset_map"] = _hashed(
        {
            "assets": [
                {"id": "world-one", "kind": "archival_portrait"},
                {"id": "prop-one", "kind": "generated_prop"},
            ]
        }
    )

    with pytest.raises(EditorialMotionError, match="must declare a contained layout"):
        compile_editorial_motion_plan(**values)

    values["shot_specs"][0]["layers"][0]["layout"] = {
        "x": 0.0,
        "y": 0.0,
        "width": 1.0,
        "height": 1.0,
        "fit": "contain",
    }
    assert compile_editorial_motion_plan(**values)["shots"][0]["layers"][0]["layout"]["fit"] == "contain"


def test_compile_preserves_integrated_information_surface() -> None:
    values = _inputs()
    values["shot_specs"][1]["information_surface"] = {
        "mode": "surface_ink",
        "x": 0.55,
        "y": 0.45,
        "width": 0.3,
        "height": 0.15,
        "text_align": "center",
        "surface_asset_id": "prop-one",
    }
    plan = compile_editorial_motion_plan(**values)
    assert plan["shots"][1]["information_surface"]["mode"] == "surface_ink"


def test_compile_rejects_information_surface_asset_outside_shot() -> None:
    values = _inputs()
    values["shot_specs"][1]["information_surface"] = {
        "mode": "surface_ink",
        "x": 0.55,
        "y": 0.45,
        "width": 0.3,
        "height": 0.15,
        "surface_asset_id": "world-one",
    }
    with pytest.raises(EditorialMotionError, match="outside the shot"):
        compile_editorial_motion_plan(**values)


def test_compile_preserves_grounded_timed_exit_and_hash_bound_sound_effect() -> None:
    values = _inputs()
    values["shot_specs"][0]["layers"].append(
        {
            "asset_id": "prop-one",
            "role": "character",
            "action": "gesture",
            "layout": {"x": 0.55, "y": 0.2, "width": 0.2, "height": 0.6},
            "placement": {
                "support_plane": {
                    "id": "deck",
                    "x": 0.5,
                    "y": 0.75,
                    "width": 0.3,
                    "height": 0.2,
                },
                "foot_anchor": {"x": 0.5, "y": 1.0},
                "exclusion_zones": [
                    {"id": "cargo", "x": 0.0, "y": 0.4, "width": 0.4, "height": 0.5}
                ],
            },
            "timing": {
                "exit_at_s": 0.7,
                "exit_duration_s": 0.2,
                "exit_effect": "smoke_puff",
            },
        }
    )
    values["shot_specs"][0]["sound_effects"] = [
        {
            "id": "vanish-smoke-woosh",
            "at_s": 0.7,
            "duration_s": 0.2,
            "volume": 0.2,
            "sha256": "a" * 64,
        }
    ]

    plan = compile_editorial_motion_plan(**values)

    assert plan["shots"][0]["layers"][1]["timing"]["exit_effect"] == "smoke_puff"
    assert plan["shots"][0]["sound_effects"][0]["id"] == "vanish-smoke-woosh"


def test_validate_rejects_character_placement_over_an_exclusion_zone() -> None:
    plan = compile_editorial_motion_plan(**_inputs())
    plan["shots"][0]["layers"].append(
        {
            "asset_id": "prop-one",
            "role": "character",
            "layout": {"x": 0.25, "y": 0.2, "width": 0.25, "height": 0.6},
            "placement": {
                "support_plane": {
                    "id": "deck",
                    "x": 0.2,
                    "y": 0.75,
                    "width": 0.4,
                    "height": 0.2,
                },
                "foot_anchor": {"x": 0.5, "y": 1.0},
                "exclusion_zones": [
                    {"id": "cargo", "x": 0.2, "y": 0.4, "width": 0.3, "height": 0.4}
                ],
            },
        }
    )
    plan["artifact_hash"] = canonical_sha256(
        {key: value for key, value in plan.items() if key != "artifact_hash"}
    )

    with pytest.raises(EditorialMotionError, match="overlaps exclusion zone"):
        validate_editorial_motion_plan(plan, known_asset_ids={"world-one", "prop-one"})


def _timestamped_motion_inputs() -> dict:
    raw_blocks = [
        {
            "block_id": "plate-one",
            "order": 1,
            "coverage_slot_ids": ["slot-one"],
            "start_s": 0.0,
            "end_s": 2.0,
            "duration_s": 2.0,
            "narration_excerpt": "One two three four.",
            "function": "artifact_cold_open",
            "visual_direction": "Open sky over a quiet gate.",
            "prompt": "original plate one",
        },
        {
            "block_id": "plate-two",
            "order": 2,
            "coverage_slot_ids": ["slot-two"],
            "start_s": 2.0,
            "end_s": 4.0,
            "duration_s": 2.0,
            "narration_excerpt": "One two three four.",
            "function": "artifact_cold_open",
            "visual_direction": "A threshold on the right.",
            "prompt": "original plate two",
        },
        {
            "block_id": "plate-three",
            "order": 3,
            "coverage_slot_ids": ["slot-three"],
            "start_s": 4.0,
            "end_s": 6.0,
            "duration_s": 2.0,
            "narration_excerpt": "Five six seven eight.",
            "function": "illustrated_reconstruction",
            "visual_direction": "A calm interior room.",
            "prompt": "original plate three",
        },
        {
            "block_id": "plate-four",
            "order": 4,
            "coverage_slot_ids": ["slot-four"],
            "start_s": 6.0,
            "end_s": 8.0,
            "duration_s": 2.0,
            "narration_excerpt": "Five six seven eight.",
            "function": "document_quote_closeup",
            "visual_direction": "A document detail on the left.",
            "prompt": "original plate four",
        },
    ]
    plan_core = {
        "schema_version": "timestamped_plate_plan.v1",
        "coverage_plan_hash": "a" * 64,
        "prompt_spine_hash": "b" * 64,
        "plate_count": len(raw_blocks),
        "duration_s": 8.0,
        "one_primary_plate_per_timestamp_slot": True,
        "blocks": raw_blocks,
    }
    plates = _hashed(plan_core)
    assets = []
    for index, block in enumerate(raw_blocks, start=1):
        assets.append(
            {
                "id": f"timestamped-plate-{index:03d}",
                "render_eligible": True,
                "metadata": {
                    "coverage_slot_id": block["coverage_slot_ids"][0],
                    "timestamped_plate_plan_hash": plates["artifact_hash"],
                },
            }
        )
    asset_map = _hashed({"assets": assets})
    audio = _hashed(
        {
            "schema_version": "elevenlabs_canonical_audio.v1",
            "status": "ready",
            "narration_hash": "c" * 64,
            "duration_s": 4.0,
        }
    )
    words = {
        "words": [
            {"w": "One", "start_s": 0.0, "end_s": 0.35},
            {"w": "two", "start_s": 0.4, "end_s": 0.7},
            {"w": "three", "start_s": 0.75, "end_s": 1.0},
            {"w": "four.", "start_s": 1.05, "end_s": 1.3},
            {"w": "Five", "start_s": 2.0, "end_s": 2.25},
            {"w": "six", "start_s": 2.3, "end_s": 2.5},
            {"w": "seven", "start_s": 2.55, "end_s": 2.8},
            {"w": "eight.", "start_s": 2.85, "end_s": 3.2},
        ]
    }
    return {
        "timestamped_plate_plan": plates,
        "asset_map": asset_map,
        "audio_manifest": audio,
        "word_timings": words,
        "pacing_recipe": build_default_pacing_recipe(),
    }


def test_timestamped_motion_compiler_binds_every_original_plate_to_audio() -> None:
    plan = compile_timestamped_editorial_motion_plan(**_timestamped_motion_inputs())

    assert plan["duration_s"] == 4.0
    assert [shot["layers"][0]["asset_id"] for shot in plan["shots"]] == [
        "timestamped-plate-001",
        "timestamped-plate-002",
        "timestamped-plate-003",
        "timestamped-plate-004",
    ]
    # The source schedule, not a repeated prose excerpt, controls cuts.  The
    # spoken intervals remain contiguous and every primary image has a bounded
    # visual hold.
    assert plan["shots"][0]["word_range"]["start_index"] == 0
    assert plan["shots"][-1]["word_range"]["end_index"] == 7
    assert all(
        previous["word_range"]["end_index"] + 1
        == following["word_range"]["start_index"]
        for previous, following in zip(plan["shots"], plan["shots"][1:])
    )
    assert all(shot["duration_s"] <= 6.0 for shot in plan["shots"])
    assert all(not shot["overlay_ids"] for shot in plan["shots"])
    assert all(shot["information_reveal"] == "none" for shot in plan["shots"])


def test_timestamped_motion_compiler_rejects_unmatched_narration() -> None:
    values = _timestamped_motion_inputs()
    invalid = copy.deepcopy(values["timestamped_plate_plan"])
    invalid["blocks"][2]["narration_excerpt"] = "This was never narrated."
    invalid["blocks"][3]["narration_excerpt"] = "This was never narrated."
    invalid["artifact_hash"] = canonical_sha256(
        {key: value for key, value in invalid.items() if key != "artifact_hash"}
    )
    values["timestamped_plate_plan"] = invalid
    for asset in values["asset_map"]["assets"]:
        asset["metadata"]["timestamped_plate_plan_hash"] = invalid["artifact_hash"]
    values["asset_map"]["artifact_hash"] = canonical_sha256(
        {key: value for key, value in values["asset_map"].items() if key != "artifact_hash"}
    )

    with pytest.raises(EditorialMotionError, match="cannot be resolved"):
        compile_timestamped_editorial_motion_plan(**values)


def test_timestamped_coverage_reports_and_blocks_uncovered_canonical_prose() -> None:
    values = _timestamped_motion_inputs()
    values["word_timings"] = {
        "words": [
            *values["word_timings"]["words"][:4],
            {"w": "Interlude", "start_s": 1.35, "end_s": 1.55},
            {"w": "words.", "start_s": 1.6, "end_s": 1.85},
            *values["word_timings"]["words"][4:],
        ]
    }

    coverage = analyze_timestamped_semantic_coverage(
        timestamped_plate_plan=values["timestamped_plate_plan"],
        word_timings=values["word_timings"],
    )

    assert coverage["render_ready"] is False
    assert coverage["uncovered_slots"] == [
        {
            "slot_id": "semantic-gap-01-01",
            "word_range": {"start_index": 4, "end_index": 5},
            "start_s": 1.35,
            "end_s": 1.85,
            "narration_excerpt": "Interlude words.",
            "visual_intent": "explanation",
            "required_visual_actions": [],
            "asset_status": "generation_required",
        }
    ]
    with pytest.raises(EditorialMotionError, match="leaves canonical narration uncovered"):
        compile_timestamped_editorial_motion_plan(**values)


def test_canonical_visual_coverage_uses_final_audio_words_as_the_image_schedule() -> None:
    values = _timestamped_motion_inputs()

    coverage = compile_canonical_visual_coverage(
        audio_manifest=values["audio_manifest"],
        word_timings=values["word_timings"],
        target_duration_s=2.0,
        minimum_duration_s=1.0,
        maximum_duration_s=3.0,
    )

    assert coverage["schema_version"] == "canonical_visual_coverage.v11"
    assert coverage["render_ready"] is False
    assert coverage["slots"][0]["word_range"]["start_index"] == 0
    assert coverage["slots"][-1]["word_range"]["end_index"] == 7
    assert all(
        previous["word_range"]["end_index"] + 1
        == following["word_range"]["start_index"]
        for previous, following in zip(coverage["slots"], coverage["slots"][1:])
    )
    assert all(slot["duration_s"] <= 3.0 for slot in coverage["slots"])


def test_visual_intent_requires_one_action_per_explicit_list_item() -> None:
    _, actions = _visual_intent_and_actions(
        "We can follow a system as it acquires schools, teachers, rules, and public meaning."
    )

    assert actions == [
        {"kind": "list_item_popout", "subject": "schools"},
        {"kind": "list_item_popout", "subject": "teachers"},
        {"kind": "list_item_popout", "subject": "rules"},
        {"kind": "list_item_popout", "subject": "public meaning"},
    ]


def test_visual_intent_requires_actions_for_enumerated_contexts_without_a_list_verb() -> None:
    intent, actions = _visual_intent_and_actions(
        "The practice could look different when it entered a school, a theater, a challenge match, or a community of immigrants."
    )

    assert intent == "academic"
    assert actions == [
        {"kind": "list_item_popout", "subject": "a school"},
        {"kind": "list_item_popout", "subject": "a theater"},
        {"kind": "list_item_popout", "subject": "a challenge match"},
        {"kind": "list_item_popout", "subject": "a community of immigrants"},
    ]


def test_visual_intent_requires_actions_for_enumerated_uses() -> None:
    intent, actions = _visual_intent_and_actions(
        "A word can be used to sell an exhibition, identify a teacher, describe a lineage, or summarize a ruleset."
    )

    assert intent == "academic"
    assert actions == [
        {"kind": "list_item_popout", "subject": "sell an exhibition"},
        {"kind": "list_item_popout", "subject": "identify a teacher"},
        {"kind": "list_item_popout", "subject": "describe a lineage"},
        {"kind": "list_item_popout", "subject": "summarize a ruleset"},
    ]


def test_contextual_actions_do_not_lose_a_list_when_a_slot_crosses_sentences() -> None:
    words = [
        {"w": word}
        for word in (
            "Public names travel through advertisements, demonstrations, newspapers, translations, "
            "and later memories. A word can be used to sell an exhibition."
        ).split()
    ]

    _, first_actions = _contextual_visual_intent_and_actions(words, 4, 5)
    _, later_actions = _contextual_visual_intent_and_actions(words, 6, 10)

    assert first_actions == [
        {"kind": "list_item_popout", "subject": "advertisements"},
        {"kind": "list_item_popout", "subject": "demonstrations"},
    ]
    assert later_actions == [
        {"kind": "list_item_popout", "subject": "newspapers"},
        {"kind": "list_item_popout", "subject": "translations"},
        {"kind": "list_item_popout", "subject": "later memories"},
    ]


def test_subject_led_enumeration_schedules_each_meaningful_list_item() -> None:
    _, actions = _visual_intent_and_actions(
        "Theaters, demonstrations, challenges, and advertised lessons put Japanese "
        "grappling in front of audiences."
    )

    assert actions == [
        {"kind": "list_item_popout", "subject": "Theaters"},
        {"kind": "list_item_popout", "subject": "demonstrations"},
        {"kind": "list_item_popout", "subject": "challenges"},
        {"kind": "list_item_popout", "subject": "advertised lessons"},
    ]


def test_subject_led_helped_enumeration_schedules_each_meaningful_list_item() -> None:
    _, actions = _visual_intent_and_actions(
        "Scholarship locates a phase of reinvention when public performances, "
        "institutions, promotion, and nationalism helped distinguish a Brazilian "
        "combat sport from other practices."
    )

    assert actions == [
        {"kind": "list_item_popout", "subject": "public performances"},
        {"kind": "list_item_popout", "subject": "institutions"},
        {"kind": "list_item_popout", "subject": "promotion"},
        {"kind": "list_item_popout", "subject": "nationalism"},
    ]


def test_explanatory_enumeration_excludes_the_sentence_frame() -> None:
    _, actions = _visual_intent_and_actions(
        "It shows why techniques, labels, and teaching methods could shift as they moved."
    )

    assert actions == [
        {"kind": "list_item_popout", "subject": "techniques"},
        {"kind": "list_item_popout", "subject": "labels"},
        {"kind": "list_item_popout", "subject": "teaching methods"},
    ]


def test_parallel_modal_clauses_schedule_one_action_per_clause() -> None:
    _, actions = _visual_intent_and_actions(
        "A student can become an instructor, a local teacher can carry practice into another "
        "community, and later memory can compress several stages into one famous connection."
    )

    assert actions == [
        {"kind": "list_item_popout", "subject": "A student can become an instructor"},
        {
            "kind": "list_item_popout",
            "subject": "a local teacher can carry practice into another community",
        },
        {
            "kind": "list_item_popout",
            "subject": "later memory can compress several stages into one famous connection",
        },
    ]


def test_identifying_inventory_schedules_each_meaningful_list_item() -> None:
    _, actions = _visual_intent_and_actions(
        "Studies of Brazilian judo identify immigrant teachers, professional fighters, "
        "and community networks that spread related practices through different regions."
    )

    assert actions == [
        {"kind": "list_item_popout", "subject": "immigrant teachers"},
        {"kind": "list_item_popout", "subject": "professional fighters"},
        {"kind": "list_item_popout", "subject": "community networks"},
    ]


def test_visual_intent_requires_a_map_cut_in_for_named_travel() -> None:
    intent, actions = _visual_intent_and_actions(
        "The practice travelled from Japan to Brazil through the Americas."
    )

    assert intent == "journey"
    assert actions == [
        {"kind": "map_cut_in", "subject": "Japan"},
        {"kind": "map_cut_in", "subject": "Brazil"},
        {"kind": "map_cut_in", "subject": "the Americas"},
    ]
