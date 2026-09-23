"""Bounded math, contact, skinning, and seek tests for the rig proof."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import rig_math as m  # noqa: E402
import rig_pose as rig  # noqa: E402


def _load_parent_dqs():
    path = ROOT.parent / "rig-skinning" / "dqs.py"
    spec = importlib.util.spec_from_file_location("test_parent_dqs", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_symmetric_two_bone_ik_and_reach_reporting():
    plus = m.two_bone_ik((0.0, 0.0), (1.0, 0.0), 1.0, 1.0, bend=1)
    minus = m.two_bone_ik((0.0, 0.0), (1.0, 0.0), 1.0, 1.0, bend=-1)
    assert plus.end == pytest.approx((1.0, 0.0), abs=1e-7)
    assert minus.end == pytest.approx((1.0, 0.0), abs=1e-7)
    assert plus.elbow[1] == pytest.approx(-minus.elbow[1], abs=1e-7)
    assert math.dist(plus.root, plus.elbow) == pytest.approx(1.0)
    assert math.dist(plus.elbow, plus.end) == pytest.approx(1.0)
    unreachable = m.two_bone_ik((0.0, 0.0), (3.0, 0.0), 1.0, 1.0)
    assert not unreachable.reachable
    assert unreachable.target_error == pytest.approx(1.0, abs=1e-6)
    assert unreachable.upper_error == pytest.approx(0.0, abs=1e-7)
    assert unreachable.lower_error == pytest.approx(0.0, abs=1e-7)


def test_rigid_fallback_identity_and_stable_weight_order():
    identity = {"root": m.RigidTransform2D()}
    assert m.blend_rigid_point((3.0, -2.0), identity, {"root": 4.0}) == pytest.approx((3.0, -2.0))
    transforms_a = {"z": m.RigidTransform2D(2.0, 0.0, math.pi), "a": m.RigidTransform2D(-2.0, 0.0, -math.pi)}
    transforms_b = {"a": transforms_a["a"], "z": transforms_a["z"]}
    point_a = m.blend_rigid_point((1.0, 0.0), transforms_a, {"z": 0.5, "a": 0.5})
    point_b = m.blend_rigid_point((1.0, 0.0), transforms_b, {"a": 0.5, "z": 0.5})
    assert point_a == pytest.approx(point_b)
    with pytest.raises(ValueError):
        m.blend_rigid_point((0.0, 0.0), identity, {"root": -1.0})
    with pytest.raises(ValueError):
        m.blend_rigid_point((0.0, 0.0), identity, {"root": float("nan")})
    with pytest.raises(ValueError):
        m.blend_rigid_point((0.0, 0.0), identity, {"root": 0.0})


def test_parent_dqs_identity_rigid_and_deforming_triangle_receipt():
    dqs = _load_parent_dqs()
    assert dqs.apply(dqs.encode(0.0, 0.0, 0.0), (3.0, 4.0)) == pytest.approx((3.0, 4.0))
    assert dqs.apply(dqs.encode(2.0, 3.0, math.pi / 2.0), (1.0, 0.0)) == pytest.approx((2.0, 4.0))
    points = dqs.skin_mesh(
        [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)],
        {"a": dqs.encode(0.0, 0.0, 0.0), "b": dqs.encode(1.0, 0.0, 0.0)},
        [{"a": 1.0}, {"b": 1.0}, {"a": 1.0}],
    )
    signed_area = m.triangle_area(*points)
    assert signed_area > 0.0
    receipt = rig.skinning_receipt(rig.evaluate_frame(50 / rig.FPS).victim)
    assert receipt["representation"] == "planar_unit_dual_quaternion_blend"
    assert receipt["triangle_orientation_preserved"]
    assert receipt["global_volume_claim"] is False
    assert receipt["area_is_measured_not_guaranteed"] is True


def test_contacts_recoil_brain_and_nonzero_followthrough():
    poses = rig.evaluate_all_frames()
    right = poses[round(rig.RIGHT_CONTACT_T * rig.FPS)]
    hook = poses[round(rig.HOOK_CONTACT_T * rig.FPS)]
    right_gap = math.dist(right.attacker.arm("right").end, right.victim.head) - rig.GLOVE_RADIUS - right.victim.head_radius
    hook_gap = math.dist(hook.attacker.arm("left").end, hook.victim.head) - rig.GLOVE_RADIUS - hook.victim.head_radius
    assert right_gap == pytest.approx(0.0, abs=1.0)
    assert hook_gap == pytest.approx(0.0, abs=1.0)
    assert poses[round(rig.RIGHT_CONTACT_T * rig.FPS) - 1].right_impact == 0.0
    assert poses[round(rig.HOOK_CONTACT_T * rig.FPS) - 1].hook_impact == 0.0
    assert poses[round(rig.HEAD_SNAP_T * rig.FPS)].brain is not None
    assert all(p.brain is None for p in poses[: round(rig.HEAD_SNAP_T * rig.FPS)])
    measurements = [rig.frame_measurement(p, poses[i - 1] if i else None) for i, p in enumerate(poses)]
    assert measurements[round(rig.RIGHT_CONTACT_T * rig.FPS)]["contact"]["right_velocity_px_s"] > 0.0
    assert measurements[round(rig.HOOK_CONTACT_T * rig.FPS)]["contact"]["left_velocity_px_s"] > 0.0


def test_hook_fk_arc_matches_followthrough_tangent():
    epsilon = 1.0e-6
    t = rig.HOOK_CONTACT_T
    before = rig.left_hook_target(t - epsilon)
    at_contact = rig.left_hook_target(t)
    after = rig.left_hook_target(t + epsilon)
    incoming = ((at_contact[0] - before[0]) / epsilon, (at_contact[1] - before[1]) / epsilon)
    outgoing = ((after[0] - at_contact[0]) / epsilon, (after[1] - at_contact[1]) / epsilon)
    assert incoming == pytest.approx((-130.0, 46.0), abs=0.1)
    assert outgoing == pytest.approx((-130.0, 46.0), abs=0.1)


def test_fixed_lengths_floor_capsules_scale_and_step_release():
    poses = rig.evaluate_all_frames()
    planted = []
    for pose in poses:
        assert pose.victim.scale == pytest.approx(1.0)
        assert pose.attacker.scale == pytest.approx(1.0)
        for fighter in (pose.victim, pose.attacker):
            for chain in (*fighter.feet, fighter.arm("right"), fighter.arm("left")):
                assert abs(chain.upper_error) < 1e-5
                assert abs(chain.lower_error) < 1e-5
                assert chain.reachable
            assert rig.floor_receipt(fighter)["clearance_px"] >= -0.5
        if pose.time_s < rig.ATTACKER_STEP_RELEASE_T:
            planted.extend(math.dist(foot.end, target) for foot, target in zip(pose.attacker.feet, rig.ATTACKER_FEET))
        if pose.time_s < rig.FALL_RELEASE_T:
            planted.extend(math.dist(foot.end, target) for foot, target in zip(pose.victim.feet, rig.VICTIM_FEET))
    assert max(planted) < 0.1
    assert poses[-1].victim.head[1] + poses[-1].victim.head_radius <= rig.FLOOR_Y + 0.5
    assert poses[-1].victim.root[0] > 0.0


def test_head_precedes_torso_and_evaluation_is_seek_safe():
    poses = rig.evaluate_all_frames()
    first_head = next(p.frame for p in poses if rig.distance(rig.victim_head_offset(p.time_s), (0.0, 0.0)) > 1e-6)
    first_torso = next(p.frame for p in poses if p.time_s >= 1.30 and abs(p.victim.root[0] - 170.0) > 1e-6)
    assert first_head == round(rig.HEAD_SNAP_T * rig.FPS)
    assert first_head < first_torso
    sequential = poses
    for frame in reversed(range(rig.FRAME_COUNT)):
        assert sequential[frame] == rig.evaluate_frame(frame / rig.FPS)
