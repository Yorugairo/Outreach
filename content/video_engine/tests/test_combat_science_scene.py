from __future__ import annotations

import pytest

from content.video_engine.src.scenes.combat_science import (
    COMPOSITION_FUNCTION_NAMES,
    CONTACT_MACRO_IDS,
    LIVING_DIAGRAM_IDS,
    CombatScienceScene,
    build_contact_macro,
    build_living_diagram,
    build_matched_comparison,
)


def test_all_composition_functions_have_deterministic_mechanic_contracts() -> None:
    first = CombatScienceScene({"parameters": {"function": "wide_setup"}}, audio_duration=2.0)
    second = CombatScienceScene({"parameters": {"function": "wide_setup"}}, audio_duration=2.0)
    assert first.composition_names == COMPOSITION_FUNCTION_NAMES
    assert first.composition_contract() == second.composition_contract()
    for function in COMPOSITION_FUNCTION_NAMES:
        contract = first.composition_contract(function)
        assert contract["function"] == function
        assert contract["reviewed_anchors"]
        assert contract["state_from"] in first.state_ids
        assert contract["state_to"] in first.state_ids
        assert contract["reference_refs"] == []


@pytest.mark.parametrize("macro_id", CONTACT_MACRO_IDS)
def test_contact_macros_preserve_context_and_ownership(macro_id: str) -> None:
    scene = CombatScienceScene({}, audio_duration=1.0)
    macro = build_contact_macro(scene, macro_id)
    assert macro.context_preserved is True
    assert macro.ownership_preserved is True
    assert macro.anchor_id in scene.contact_anchors
    assert macro.context_joints


def test_wrong_right_comparison_is_matched_but_changes_one_reviewed_variable() -> None:
    scene = CombatScienceScene({}, audio_duration=1.0)
    comparison = build_matched_comparison(scene)
    assert comparison.matched_start_state is True
    assert comparison.matched_framing is True
    assert comparison.decisive_variable == "elbow_alignment"
    assert [panel["state"] for panel in comparison.panels] == [
        "wrist_control_hip_frame",
        "wrist_control_hip_frame",
    ]


@pytest.mark.parametrize("diagram_id", LIVING_DIAGRAM_IDS)
def test_living_diagrams_are_derived_from_reviewed_anchor_positions(diagram_id: str) -> None:
    scene = CombatScienceScene({}, audio_duration=1.0)
    diagram = build_living_diagram(scene, diagram_id)
    assert diagram.derived_from_reviewed_anchors is True
    assert tuple(diagram.anchor_ids)
    assert set(diagram.anchor_positions) == set(diagram.anchor_ids)
    assert all(len(point) == 3 for point in diagram.anchor_positions.values())


def test_combat_science_scene_constructs_with_the_persistent_filled_cast() -> None:
    scene = CombatScienceScene({"parameters": {"function": "force_diagram"}}, audio_duration=3.0)
    scene.construct()
    assert scene.cast_group is not None
    assert scene.current_state == "armbar_extension_held"
    assert scene._play_timeline == pytest.approx(3.0, abs=0.001)
    assert scene.mobjects.count(scene.cast_group) == 1
    assert all(part.kind in {"mass", "panel", "circle"} for part in scene.filled_layers)
    assert scene.joint_metadata["attacker:hip_right"]["owner"] == "attacker"
