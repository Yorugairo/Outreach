from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from content.video_engine.src.guards.storyboard_guard import (
    guard,
    guard_with_warnings,
)


FIXTURE = Path(__file__).parent / "fixtures" / "armbar_storyboard.json"


def _storyboard() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _violation(storyboard: dict, needle: str) -> list[str]:
    passed, violations = guard(storyboard)
    assert not passed
    assert any(needle in violation for violation in violations), violations
    return violations


def test_canonical_armbar_storyboard_passes_and_is_deterministic() -> None:
    storyboard = _storyboard()
    first = guard(storyboard)
    second = guard(copy.deepcopy(storyboard))
    assert first == (True, [])
    assert second == first


def test_schema_validation_collects_all_errors() -> None:
    storyboard = _storyboard()
    storyboard.pop("source")
    storyboard.pop("channel")
    passed, violations = guard(storyboard)
    assert not passed
    assert len(violations) >= 2
    assert all(item.startswith("schema ") for item in violations)


@pytest.mark.parametrize(
    "narration,reason",
    [
        ("This takes 12 seconds.", "unledgered number"),
        ("This medical treatment is safe.", "unledgered medical language"),
        ("The investment returns profit.", "unledgered financial language"),
        ("This is the best option.", "unledgered superlative language"),
    ],
)
def test_claim_bearing_sentences_require_verified_claim_refs(
    narration: str, reason: str
) -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["narration_text"] = narration
    storyboard["scenes"][0]["claim_refs"] = []
    _violation(storyboard, reason)


def test_years_are_allowlisted_but_unverified_refs_still_fail() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["narration_text"] = "The method dates to 1988."
    assert guard(storyboard) == (True, [])
    storyboard["scenes"][0]["claim_refs"] = ["c2"]
    storyboard["claims"].append(
        {
            "id": "c2",
            "text": "unverified",
            "kind": "historical",
            "source": "unknown",
            "verified": False,
        }
    )
    _violation(storyboard, "unverified claim")


def test_unreferenced_claims_are_warnings_not_violations() -> None:
    storyboard = _storyboard()
    storyboard["claims"].append(
        {
            "id": "c2",
            "text": "A verified but unused detail.",
            "kind": "other",
            "source": "corpus",
            "verified": True,
        }
    )
    result = guard_with_warnings(storyboard)
    assert result.ok
    assert result.violations == []
    assert any("c2" in warning for warning in result.warnings)


def test_arc_order_and_required_acts_are_enforced() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["act"] = "develop"
    storyboard["scenes"][-1]["act"] = "payoff"
    _violation(storyboard, "hook scene must be first")
    _violation(storyboard, "cta scene must be last")


def test_long_run_requires_first_third_conflict_and_comeback() -> None:
    storyboard = _storyboard()
    for scene in storyboard["scenes"]:
        scene["timing"]["target_s"] = 20
    for scene in storyboard["scenes"]:
        scene["act"] = "develop"
    storyboard["scenes"][0]["act"] = "hook"
    storyboard["scenes"][-1]["act"] = "cta"
    violations = _violation(storyboard, "conflict in the first third")
    assert any("comeback" in violation for violation in violations)


def test_credential_framing_requires_named_expert() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["narration_text"] = "A doctor explains the armbar."
    _violation(storyboard, "credential framing")
    storyboard["expert"] = {"name": "Dr. Example", "credential": "sports medicine"}
    assert guard(storyboard) == (True, [])


def test_unknown_scene_class_pose_and_action_are_rejected() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["manim_class"] = "UnknownScene"
    storyboard["scenes"][0]["parameters"]["poses"] = ["not_a_pose"]
    storyboard["scenes"][0]["beats"][0]["action"] = "spin:unknown"
    violations = _violation(storyboard, "unknown manim_class")
    assert any("missing pose" in violation for violation in violations)
    assert any("beat action" in violation for violation in violations)


def test_hard_cut_budget_and_pacing_budget_are_enforced() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][0]["act"] = "develop"
    storyboard["scenes"][1]["act"] = "develop"
    storyboard["scenes"][0]["transition"] = {"in": "hard_cut", "motif": None}
    storyboard["scenes"][1]["transition"] = {"in": "hard_cut", "motif": None}
    storyboard["scenes"][1]["beats"] = []
    storyboard["scenes"][1]["timing"]["target_s"] = 20
    violations = _violation(storyboard, "hard cuts")
    assert any("visual-change budget" in violation for violation in violations)


def test_realistic_recreation_forces_synthetic_disclosure() -> None:
    storyboard = _storyboard()
    storyboard["scenes"][2]["realistic_recreation"] = True
    _violation(storyboard, "synthetic_content_disclosure")
    storyboard["packaging"]["synthetic_content_disclosure"]["required"] = True
    assert guard(storyboard) == (True, [])


def test_shorts_scene_ids_and_custom_voice_policy_are_checked() -> None:
    storyboard = _storyboard()
    storyboard["shorts"][0]["scene_ids"] = [999]
    storyboard["global_settings"]["voice"]["is_custom_voice"] = False
    violations = _violation(storyboard, "missing scene ids")
    assert any("custom_voice" in violation for violation in violations)

