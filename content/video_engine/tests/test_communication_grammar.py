from __future__ import annotations

import copy
from pathlib import Path

import pytest

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.living_scenes import (
    LivingSceneValidationError,
    build_default_communication_grammar,
    validate_communication_grammar,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT_GRAMMAR = (
    ROOT
    / "projects"
    / "history-of-bjj"
    / "communication-grammar.v1.json"
)


def _rehash(payload: dict) -> dict:
    payload["artifact_hash"] = canonical_sha256(payload)
    return payload


def test_default_grammar_has_five_owned_surfaces_and_cost_baseline() -> None:
    grammar = validate_communication_grammar(
        build_default_communication_grammar()
    )

    assert [surface["id"] for surface in grammar["surfaces"]] == [
        "world",
        "character",
        "evidence",
        "explanation",
        "transition",
    ]
    assert grammar["motion_hierarchy"][0]["id"] == "character_prop"
    assert grammar["motion_hierarchy"][-1]["id"] == "camera"
    assert grammar["scene_policy"]["camera_only_motion_satisfies_beat"] is False
    assert grammar["generated_content_policy"]["facts_rendered_locally"] is True
    assert grammar["visual_system_policy"]["comparison_template_reused"] is True
    assert grammar["transition_policy"]["action_cut_points"] == [
        "anticipation",
        "contact",
        "recoil",
        "result",
    ]
    assert grammar["sound_policy"]["mix"] == "narration_led"
    assert grammar["sound_policy"]["impact_accents"] == "demonstration_only"
    assert grammar["cost_policy"]["baseline_credits_per_second"] == pytest.approx(
        600 / 180, abs=1e-6
    )


def test_grammar_rejects_camera_first_and_generated_factual_text() -> None:
    camera_first = copy.deepcopy(build_default_communication_grammar())
    camera_first["motion_hierarchy"][0], camera_first["motion_hierarchy"][3] = (
        camera_first["motion_hierarchy"][3],
        camera_first["motion_hierarchy"][0],
    )
    for rank, item in enumerate(camera_first["motion_hierarchy"], start=1):
        item["rank"] = rank
    _rehash(camera_first)
    with pytest.raises(LivingSceneValidationError, match="motion hierarchy"):
        validate_communication_grammar(camera_first)

    factual_pixels = copy.deepcopy(build_default_communication_grammar())
    factual_pixels["generated_content_policy"][
        "factual_text_in_generated_pixels"
    ] = True
    _rehash(factual_pixels)
    with pytest.raises(LivingSceneValidationError, match="factual_text"):
        validate_communication_grammar(factual_pixels)


def test_grammar_rejects_cost_baseline_drift_and_stale_hash() -> None:
    cost_drift = copy.deepcopy(build_default_communication_grammar())
    cost_drift["cost_policy"]["baseline_credits_per_second"] = 0.5
    _rehash(cost_drift)
    with pytest.raises(LivingSceneValidationError, match="credits per second"):
        validate_communication_grammar(cost_drift)

    stale = copy.deepcopy(build_default_communication_grammar())
    stale["surfaces"][0]["audience_function"] = "changed"
    with pytest.raises(LivingSceneValidationError, match="artifact_hash"):
        validate_communication_grammar(stale)


def test_project_grammar_validates() -> None:
    grammar = validate_communication_grammar(PROJECT_GRAMMAR)
    assert grammar["id"] == "combat-history-living-scenes-v1"
