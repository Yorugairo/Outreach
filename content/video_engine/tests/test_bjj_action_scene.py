from __future__ import annotations

import pytest

from content.video_engine.src.scenes.bjj_action import (
    ACTION_PHASES,
    ARM_BAR_ACTION_CHAIN,
    BJJActionScene,
    PHASE_NAMES,
    STATE_POSES,
    build_bjj_cast,
)
from content.video_engine.src.scenes.base import MANIM_AVAILABLE


def test_cast_exposes_persistent_members_joints_ownership_and_layers() -> None:
    cast = build_bjj_cast()

    assert cast.cast_ids == ("attacker", "defender")
    assert cast.attacker.variant_id == "white_gi_blue_belt"
    assert cast.defender.variant_id == "black_gi_purple_belt"
    assert {"attacker:head", "defender:head"} <= set(cast.joints)
    assert cast.body_ownership["attacker:forearm_right"] == "attacker"
    assert cast.body_ownership["defender:forearm_right"] == "defender"
    assert cast.z_order["attacker:forearm_right"] > cast.z_order["defender:forearm_right"]
    assert cast.contact_anchors["wrist_control"].source == "attacker:wrist_right"
    assert cast.contact_anchors["wrist_control"].target == "defender:wrist_left"


def test_armbar_recipe_has_all_causal_phases_and_nonzero_state_changes() -> None:
    assert ACTION_PHASES == PHASE_NAMES
    assert tuple(phase.name for phase in ARM_BAR_ACTION_CHAIN) == PHASE_NAMES
    assert {phase.motion_path for phase in ARM_BAR_ACTION_CHAIN} >= {
        "linear",
        "arc",
        "pivot",
        "compression",
    }
    assert all(phase.duration_s > 0 for phase in ARM_BAR_ACTION_CHAIN)
    assert all(phase.state_from != phase.state_to for phase in ARM_BAR_ACTION_CHAIN)
    assert all(phase.contact_anchors for phase in ARM_BAR_ACTION_CHAIN)

    for phase in ARM_BAR_ACTION_CHAIN:
        assert phase.state_from in STATE_POSES
        assert phase.state_to in STATE_POSES
        assert phase.action


def test_scene_constructs_without_manim_and_keeps_one_cast_group() -> None:
    scene = BJJActionScene({}, layout="landscape", audio_duration=4.0)
    scene.construct()

    assert scene.phase_names == PHASE_NAMES
    assert [item["phase"] for item in scene.phase_history] == list(PHASE_NAMES)
    assert scene.current_state == "armbar_extension_held"
    assert scene.cast_group is not None
    assert scene._play_timeline == pytest.approx(4.0, abs=0.001)
    assert scene._first_animation_start is not None
    assert scene._first_animation_start <= 0.5
    # The vector cast remains a single persistent group; only phase contact
    # markers are added as the action progresses.
    assert scene.mobjects.count(scene.cast_group) == 1
    assert set(scene.contact_anchors) >= {
        "wrist_control",
        "hip_fulcrum",
        "knee_over_head",
        "elbow_line",
    }


def test_scene_contract_contains_body_and_contact_evidence() -> None:
    contract = BJJActionScene({}, audio_duration=3.0).action_contract()

    assert contract["recipe_version"] == "shot_recipe.v1"
    assert contract["cast"] == {
        "attacker": "white_gi_blue_belt",
        "defender": "black_gi_purple_belt",
    }
    assert contract["state_from"] == "closed_guard_posture_broken"
    assert contract["state_to"] == "armbar_extension_held"
    assert contract["motion"]["phases"] == list(PHASE_NAMES)
    assert contract["body_ownership"]["attacker:thigh_left"] == "attacker"
    assert contract["contact_anchors"]["hip_fulcrum"]["kind"] == "fulcrum"


def test_v3_cast_uses_filled_masses_and_keeps_joints_as_metadata() -> None:
    scene = BJJActionScene({}, audio_duration=1.0)
    assert scene.filled_layers
    assert all(part.fill_opacity == pytest.approx(1.0) for part in scene.filled_layers)
    assert all(part.shape.startswith("filled_") for part in scene.filled_layers)
    assert scene.joint_metadata["attacker:hip_right"]["owner"] == "attacker"
    assert scene.joint_metadata["defender:elbow_right"]["role"] == "elbow"


def test_filled_mass_mobjects_are_opaque_and_owner_tagged_after_entrance() -> None:
    scene = BJJActionScene({}, audio_duration=1.0)
    scene.entrance()
    masses = [
        member.part_mobjects[name]
        for member in scene.cast.members.values()
        for name, part in member.body_parts.items()
        if part.kind in {"mass", "panel"}
    ]
    assert masses
    assert all(getattr(mass, "fill_opacity", 0.0) == pytest.approx(1.0) for mass in masses)
    assert all(getattr(mass, "body_owner", "") in {"attacker", "defender"} for mass in masses)


def test_scene_rejects_incomplete_or_unknown_custom_phase_contract() -> None:
    incomplete = {"parameters": {"phases": [{"phase": "action"}]}}
    with pytest.raises(ValueError, match="must define state_from/action/state_to"):
        BJJActionScene(incomplete).phases

    unknown = {
        "parameters": {
            "phases": [
                {
                    "phase": phase,
                    "state_from": ARM_BAR_ACTION_CHAIN[index].state_from,
                    "action": ARM_BAR_ACTION_CHAIN[index].action,
                    "state_to": "not_a_reviewed_state" if index == 0 else ARM_BAR_ACTION_CHAIN[index].state_to,
                }
                for index, phase in enumerate(PHASE_NAMES)
            ]
        }
    }
    with pytest.raises(KeyError, match="unknown BJJ action state"):
        BJJActionScene(unknown).phases


@pytest.mark.render_smoke
def test_optional_manim_dependency_is_explicit() -> None:
    if not MANIM_AVAILABLE:
        pytest.skip("missing local dependency: manim")
    assert MANIM_AVAILABLE
