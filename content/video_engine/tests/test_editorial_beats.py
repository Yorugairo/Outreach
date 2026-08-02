from __future__ import annotations

import pytest

from content.video_engine.src.services.editorial_beats import (
    EditorialBeatPlanError,
    compile_editorial_beat_plan,
)


def _storyboard() -> dict:
    return {
        "schema_version": "2.2.0",
        "source": {"kind": "history_episode"},
        "scenes": [
            {
                "scene_id": 1,
                "chapter_id": "kano",
                "narration_text": (
                    "The useful starting point is not a battlefield legend "
                    "but an institution. In 1882, Jigoro Kano established "
                    "the Kodokan."
                ),
                "visual_function": "artifact_cold_open",
                "claim_refs": ["claim-kano"],
                "citation_refs": ["citation-kano"],
                "asset_ids": ["archive-jigoro-kano"],
                "timing": {"target_s": 12.0},
                "transition": {"in": "hard_cut", "motif": "artifact"},
            }
        ],
    }


def test_editorial_beats_split_sentences_and_semantic_contrast() -> None:
    plan = compile_editorial_beat_plan(_storyboard())

    assert plan["schema_version"] == "editorial_beat_plan.v1"
    assert plan["parent_scene_count"] == 1
    assert plan["beat_count"] == 3
    assert [beat["visual_intent"] for beat in plan["beats"]] == [
        "battlefield_legend",
        "tranquil_institution",
        "kodokan_origin",
    ]
    assert [beat["function"] for beat in plan["beats"]] == [
        "illustrated_reconstruction",
        "archival_portrait",
        "archival_portrait",
    ]
    assert all(
        beat["citation_refs"] == ["citation-kano"]
        for beat in plan["beats"]
    )
    assert sum(beat["duration_s"] for beat in plan["beats"]) == pytest.approx(
        12.0,
        abs=1e-6,
    )


def test_editorial_beats_are_deterministic_and_hash_bound() -> None:
    assert compile_editorial_beat_plan(
        _storyboard()
    ) == compile_editorial_beat_plan(_storyboard())


def test_editorial_beats_split_long_compound_ideas() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["narration_text"] = (
        "Kano drew from multiple jujutsu schools, selected and reorganized "
        "techniques, and connected practice to a broader educational program."
    )
    storyboard["scenes"][0]["timing"]["target_s"] = 18.0

    plan = compile_editorial_beat_plan(storyboard)

    assert plan["beat_count"] >= 2
    assert max(
        len(beat["narration_excerpt"].split()) for beat in plan["beats"]
    ) <= 20
    assert sum(beat["duration_s"] for beat in plan["beats"]) == pytest.approx(
        18.0,
        abs=1e-6,
    )


def test_editorial_beats_reject_non_history_storyboard() -> None:
    with pytest.raises(EditorialBeatPlanError, match="History V4"):
        compile_editorial_beat_plan({"scenes": []})


def test_editorial_beats_do_not_turn_generic_lineage_language_into_graphs() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["narration_text"] = (
        "That date does not mean every older practice became one lineage."
    )
    storyboard["scenes"][0]["visual_function"] = "lineage_graph"
    storyboard["scenes"][0]["timing"]["target_s"] = 5.0

    beat = compile_editorial_beat_plan(storyboard)["beats"][0]

    assert beat["visual_intent"] == "lofi_editorial_aside"
    assert beat["function"] == "concept_mechanics_cutaway"
    assert beat["literature_mode"] == "lofi_comedy"


def test_storyboard_2_3_uses_reviewed_visual_beats_without_resplitting() -> None:
    storyboard = _storyboard()
    storyboard["schema_version"] = "2.3.0"
    storyboard["coverage_plan_hash"] = "1" * 64
    storyboard["asset_selection_hash"] = "2" * 64
    storyboard["scenes"][0]["visual_beats"] = [
        {
            "coverage_slot_id": "shot-001-unit-01-part-01",
            "narration_excerpt": "The useful starting point is not a battlefield legend.",
            "parent_offset_s": 0.0,
            "duration_s": 5.0,
            "semantic_purpose": "correction",
            "visual_source": "stock_photo",
            "asset_ids": ["stock-battlefield"],
            "motion_recipe": "detail_punch",
            "micro_events": [
                {"at_s": 0.0, "action": "establish", "recipe": "detail_punch"},
                {"at_s": 2.25, "action": "reveal", "recipe": "detail_punch"},
            ],
            "transition": "hard_cut",
        },
        {
            "coverage_slot_id": "shot-001-unit-02-part-01",
            "narration_excerpt": "In 1882, Jigoro Kano established the Kodokan.",
            "parent_offset_s": 5.0,
            "duration_s": 7.0,
            "semantic_purpose": "person",
            "visual_source": "archive",
            "asset_ids": ["archive-jigoro-kano"],
            "motion_recipe": "parallax_push",
            "micro_events": [
                {"at_s": 0.0, "action": "establish", "recipe": "parallax_push"},
                {"at_s": 2.25, "action": "reframe", "recipe": "parallax_push"},
                {"at_s": 4.5, "action": "emphasize", "recipe": "parallax_push"},
            ],
            "transition": "match_cut",
        },
    ]

    plan = compile_editorial_beat_plan(storyboard)

    assert plan["beat_count"] == 2
    assert plan["coverage_plan_hash"] == "1" * 64
    assert [beat["motion_recipe"] for beat in plan["beats"]] == [
        "detail_punch",
        "parallax_push",
    ]
    assert plan["beats"][0]["asset_ids"] == ["stock-battlefield"]
