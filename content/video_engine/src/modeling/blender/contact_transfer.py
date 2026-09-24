"""Opt-in, source-timed contact and recoil successor for the synthetic exchange."""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any

from . import fight_motion as fight


SCHEMA = "model_fight_motion_contact_transfer.v1"
RENDER_FRAMES = (8, 10, 12, 15, 21, 24, 26, 32)
PALM_PLANE_GAP_TARGET_M = 0.003
MAX_PALM_PLANE_PENETRATION_M = 0.03
MAX_LATERAL_PROXIMITY_ADJUSTMENT_RESIDUAL_M = 0.05
MIN_RESPONSE_ROOT_M = 0.02
MIN_RESPONSE_HEAD_M = 0.02
MIN_RESPONSE_TORSO_M = 0.015
MIN_POST_CONTACT_PLANE_SEPARATION_M = 0.015
MIN_POST_CONTACT_PROXIMITY_GROWTH_M = 0.01
MIN_HOOK_HEAD_RECOIL_ADVANTAGE_M = 0.01
CONTACT_FRAMES = {"right": (10, 11), "left": (24,)}
STRIKING_DIGIT_CONTROL_MULTIPLIER = 1.25
FINGER_SEGMENTS = ("01", "02", "03")
FINGER_NAMES = ("f_index", "f_middle", "f_ring", "f_pinky")


def _vec(values) -> list[float]:
    return [round(float(value), 7) for value in values]


def _home_feet(bpy, instances) -> dict[str, dict[str, Any]]:
    scene = bpy.context.scene
    scene.frame_set(0)
    bpy.context.view_layer.update()
    result = {}
    for binding, objects in instances.items():
        rig = objects["Human.rigify"]
        result[binding] = {
            side: fight._world(rig, f"foot_ik.{side}").copy()
            for side in ("L", "R")
        }
    return result


def _hand_finger_surface_indices(bpy, body, side: str) -> tuple[int, ...]:
    groups = [f"DEF-hand.{side}"]
    groups.extend(
        f"DEF-{finger}.{segment}.{side}"
        for finger in FINGER_NAMES for segment in FINGER_SEGMENTS
    )
    groups.extend(f"DEF-thumb.{segment}.{side}" for segment in FINGER_SEGMENTS)
    group_ids = {
        body.vertex_groups[name].index
        for name in groups if body.vertex_groups.get(name) is not None
    }
    if len(group_ids) != len(groups):
        raise fight.FightMotionError(f"incomplete Rigify hand/finger deform groups for {side}")
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise fight.FightMotionError(f"evaluated hand/finger surface unavailable for {side}")
    try:
        found = {
            vertex.index for vertex in mesh.vertices
            if any(item.group in group_ids and item.weight >= 0.55 for item in vertex.groups)
        }
    finally:
        evaluated.to_mesh_clear()
    if len(found) < 32:
        raise fight.FightMotionError(f"too few hand/finger surface samples for {side}: {len(found)}")
    return tuple(sorted(found))


def _indices(bpy, instances) -> tuple[dict[str, dict[str, tuple[int, ...]]], dict[str, dict[str, int]]]:
    found = {}
    for binding, objects in instances.items():
        body = objects["Human"]
        rig = objects["Human.rigify"]
        found[binding] = {}
        for side in ("R", "L"):
            found[binding][f"hand_{side}"] = fight._skin_indices(
                bpy, body, f"DEF-hand.{side}",
            )
            found[binding][f"hand_fingers_{side}"] = _hand_finger_surface_indices(bpy, body, side)
        found[binding]["head"] = fight._head_indices(bpy, rig, body)
        for side in ("L", "R"):
            found[binding][f"foot_{side}"] = fight._sole_indices(bpy, rig, body, side)
    counts = {binding: {
        name: len(found[binding][name])
        for name in ("hand_R", "hand_L", "hand_fingers_R", "hand_fingers_L")
    } for binding in instances}
    return found, counts


def _measure_palm_plane_and_hand_finger_proximity(bpy, instances, indices,
                                                 hand_side: str, frame: int):
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    palm = fight._evaluated_points(
        instances["attacker"]["Human"],
        indices["attacker"][f"hand_{hand_side}"], depsgraph,
    )
    hand_fingers = fight._evaluated_points(
        instances["attacker"]["Human"],
        indices["attacker"][f"hand_fingers_{hand_side}"], depsgraph,
    )
    head = fight._evaluated_points(
        instances["receiver"]["Human"], indices["receiver"]["head"], depsgraph,
    )
    tree = KDTree(len(head))
    for index, point in enumerate(head):
        tree.insert(Vector(point), index)
    tree.balance()
    closest_hand = None
    closest_head = None
    closest_distance = math.inf
    for point in hand_fingers:
        nearest, _, distance = tree.find(Vector(point))
        if distance < closest_distance:
            closest_hand = tuple(point)
            closest_head = tuple(nearest)
            closest_distance = float(distance)
    axial_gap = min(point[0] for point in palm) - max(point[0] for point in head)
    return round(axial_gap, 7), closest_distance, closest_hand, closest_head


def _align_palm_plane_for_contact_window(bpy, instances, indices, side: str, frame: int):
    """Align the palm plane; closest hand/finger samples are proximity diagnostics only."""
    rig = instances["attacker"]["Human.rigify"]
    total_x_correction = 0.0
    total_yz_correction = 0.0
    for _ in range(6):
        gap, distance, hand_point, head_point = _measure_palm_plane_and_hand_finger_proximity(
            bpy, instances, indices, side, frame,
        )
        if (abs(PALM_PLANE_GAP_TARGET_M - gap) < 0.0002
                and distance <= MAX_LATERAL_PROXIMITY_ADJUSTMENT_RESIDUAL_M):
            break
        correction_x = PALM_PLANE_GAP_TARGET_M - gap
        total_x_correction += correction_x
        if abs(total_x_correction) > 0.12:
            raise fight.FightMotionError(
                f"palm-plane alignment needs an excessive strike-axis shift at frame {frame}: "
                f"{total_x_correction:.4f} m"
            )
        correction_y = 0.0
        correction_z = 0.0
        if distance > MAX_LATERAL_PROXIMITY_ADJUSTMENT_RESIDUAL_M:
            correction_y = head_point[1] - hand_point[1]
            correction_z = head_point[2] - hand_point[2]
            total_yz_correction += math.hypot(correction_y, correction_z)
            if total_yz_correction > 0.08:
                raise fight.FightMotionError(
                    f"palm-plane alignment needs an excessive hand/finger lateral shift at frame {frame}: "
                    f"{total_yz_correction:.4f} m"
                )
        matrix = fight._world(rig, f"hand_ik.{side}").copy()
        matrix.translation.x += correction_x
        matrix.translation.y += correction_y
        matrix.translation.z += correction_z
        fight._set_world_bone(rig, f"hand_ik.{side}", matrix, frame)
        bpy.context.view_layer.update()
    gap, _, _, _ = _measure_palm_plane_and_hand_finger_proximity(
        bpy, instances, indices, side, frame,
    )
    if abs(PALM_PLANE_GAP_TARGET_M - gap) > 0.005:
        raise fight.FightMotionError(
            f"palm-plane alignment missed frame {frame}: axial={gap:.5f} m"
        )
    if gap < -MAX_PALM_PLANE_PENETRATION_M - 0.001:
        raise fight.FightMotionError(
            f"palm-plane alignment could not cap {side} frame {frame} penetration: {gap:.5f} m"
        )
    return fight._world(rig, f"hand_ik.{side}").copy()


def _key_receiver_recoil(bpy, instances, home_feet) -> None:
    """Add small, source-timed body recoil while keeping both soles planted."""
    scene = bpy.context.scene
    rig = instances["receiver"]["Human.rigify"]
    root_offsets = {
        9: 0.0, 10: 0.0, 11: 0.0,
        12: -0.030, 15: -0.010, 18: 0.0,
        23: 0.0, 24: 0.0, 25: -0.040, 26: -0.050,
        28: -0.015, 32: 0.0,
    }
    response = {
        9: 0.0, 10: 0.0, 11: 0.0, 12: 1.0, 15: 0.25, 18: 0.0,
        23: 0.0, 24: 0.0, 25: 0.85, 26: 1.0, 28: 0.45, 32: 0.0,
    }
    baseline = {}
    for frame in root_offsets:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        baseline[frame] = {
            "location": rig.location.copy(),
            "rotations": {
                name: rig.pose.bones[name].rotation_euler.copy()
                for name in ("hips", "chest", "torso")
            },
        }

    for frame, offset in root_offsets.items():
        scene.frame_set(frame)
        amount = response[frame]
        rig.location = baseline[frame]["location"]
        rig.location.x += offset
        rig.keyframe_insert(data_path="location", frame=frame)
        rotations = baseline[frame]["rotations"]
        hips = rig.pose.bones["hips"]
        hips.rotation_mode = "XYZ"
        hips.rotation_euler = rotations["hips"]
        hips.rotation_euler.z -= 0.035 * amount
        hips.keyframe_insert(data_path="rotation_euler", frame=frame)
        chest = rig.pose.bones["chest"]
        chest.rotation_mode = "XYZ"
        chest.rotation_euler = rotations["chest"]
        chest.rotation_euler.z -= 0.055 * amount
        chest.keyframe_insert(data_path="rotation_euler", frame=frame)
        torso = rig.pose.bones["torso"]
        torso.rotation_mode = "XYZ"
        torso.rotation_euler = rotations["torso"]
        torso.rotation_euler.y -= 0.12 * amount
        torso.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()
        for side in ("L", "R"):
            fight._set_world_bone(
                rig, f"foot_ik.{side}", home_feet["receiver"][side], frame,
            )
            bpy.context.view_layer.update()


def _key_striking_digit_controls(bpy, instances) -> None:
    """Increase striking-side digit-control rotations relative to the generic preset."""
    rig = instances["attacker"]["Human.rigify"]
    for side in ("R", "L"):
        for bone in rig.pose.bones:
            if not (bone.name.endswith(f".{side}")
                    and bone.name.startswith((*FINGER_NAMES, "thumb."))):
                continue
            if bone.rotation_mode != "XYZ":
                continue
            for axis in range(3):
                bone.rotation_euler[axis] *= STRIKING_DIGIT_CONTROL_MULTIPLIER
            bone.keyframe_insert(
                data_path="rotation_euler", frame=0, group="contact_transfer_digit_controls",
            )
    bpy.context.view_layer.update()


def _guard_matrix(bpy, instances, side: str, guard_rotation):
    from mathutils import Matrix

    attacker = instances["attacker"]["Human.rigify"]
    receiver = instances["receiver"]["Human.rigify"]
    target = fight._hand_target("guard", attacker, receiver, side)
    return Matrix.Translation(target) @ guard_rotation.to_matrix().to_4x4()


def _blend_matrix(contact_matrix, guard_matrix, weight: float):
    rotation = contact_matrix.to_quaternion().slerp(guard_matrix.to_quaternion(), weight)
    matrix = rotation.to_matrix().to_4x4()
    matrix.translation = contact_matrix.translation.lerp(guard_matrix.translation, weight)
    return matrix


def _retract_to_guard(bpy, instances, contact_poses) -> None:
    """Retract after the impulse; never track the receiver through follow-through."""
    scene = bpy.context.scene
    attacker = instances["attacker"]["Human.rigify"]
    guard_rotations = {}
    scene.frame_set(15)
    bpy.context.view_layer.update()
    guard_rotations["R"] = fight._world(attacker, "hand_ik.R").to_quaternion().copy()
    guard_rotations["L"] = fight._world(attacker, "hand_ik.L").to_quaternion().copy()

    for side, schedule in (
        ("R", ((12, 0.55), (13, 0.82), (14, 0.96), (15, 1.0))),
        ("L", ((25, 0.35), (26, 0.68), (27, 0.90), (28, 1.0), (32, 1.0))),
    ):
        contact_matrix = contact_poses[side]
        for frame, weight in schedule:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            guard = _guard_matrix(bpy, instances, side, guard_rotations[side])
            pose = _blend_matrix(contact_matrix, guard, weight)
            fight._set_world_bone(attacker, f"hand_ik.{side}", pose, frame)
            bpy.context.view_layer.update()


def _arm_state(bpy, instances, side: str) -> dict[str, Any]:
    rig = instances["attacker"]["Human.rigify"]
    elbow = fight._world(rig, f"DEF-forearm.{side}").translation
    wrist = fight._world(rig, f"DEF-hand.{side}").translation
    target = fight._world(rig, f"hand_ik.{side}")
    forearm = wrist - elbow
    digit_euler_activity = sum(
        abs(float(value))
        for bone in rig.pose.bones
        if bone.name.endswith(f".{side}")
        and bone.name.startswith((*FINGER_NAMES, "thumb."))
        and bone.rotation_mode == "XYZ"
        for value in bone.rotation_euler
    )
    return {
        "elbow_world_m": _vec(elbow),
        "wrist_world_m": _vec(wrist),
        "forearm_vector_world": _vec(forearm),
        "forearm_length_m": round(float(forearm.length), 7),
        "digit_control_euler_activity_abs_sum_rad": round(digit_euler_activity, 7),
        "hand_ik_target_quaternion_wxyz": _vec((target.to_quaternion().w,
                                                target.to_quaternion().x,
                                                target.to_quaternion().y,
                                                target.to_quaternion().z)),
    }


def _measure_contact_transfer(bpy, instances):
    indices, counts = _indices(bpy, instances)
    rows = []
    scene = bpy.context.scene
    for frame in fight.FRAMES:
        row = fight.measure_frame(bpy, instances, indices, frame)
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        head_points = fight._evaluated_points(
            instances["receiver"]["Human"], indices["receiver"]["head"], depsgraph,
        )
        for side in ("R", "L"):
            hand_finger_points = fight._evaluated_points(
                instances["attacker"]["Human"],
                indices["attacker"][f"hand_fingers_{side}"], depsgraph,
            )
            row[f"{side.lower()}_hand_finger_head_nearest_sample_distance_m"] = round(
                fight._nearest(hand_finger_points, head_points), 7,
            )
        row["attacker_arm"] = {}
        attacker = instances["attacker"]["Human.rigify"]
        receiver = instances["receiver"]["Human.rigify"]
        row["attacker_pivot"] = {
            name: round(float(attacker.pose.bones[name].rotation_euler.z), 7)
            for name in ("hips", "chest")
        }
        for side in ("L", "R"):
            arm = _arm_state(bpy, instances, side)
            guard = fight._hand_target("guard", attacker, receiver, side)
            arm["guard_target_world_m"] = _vec(guard)
            arm["guard_distance_m"] = round(
                math.dist(row["fighters"]["attacker"][f"hand_ik_{side}_world_m"], guard), 7,
            )
            row["attacker_arm"][side] = arm
        rows.append(row)
    return rows, counts


def _xyz_distance(a: list[float], b: list[float]) -> float:
    return math.dist(a, b)


def _rotation_delta_deg(a: list[float], b: list[float]) -> float:
    dot = abs(sum(x * y for x, y in zip(a, b)))
    return math.degrees(2.0 * math.acos(min(1.0, dot)))


def _contact_pair_checks(
    *, palm_plane_min_gap: float, palm_plane_end_gap: float, follow_palm_plane_gap: float,
    contact_hand_proximity: float, follow_hand_proximity: float,
    root_dx: float, head_dx: float, torso_dx: float,
    guard_contact: float, guard_follow: float, guard_recovery: float,
) -> dict[str, bool]:
    """Apply stylized budgets to one source-timed contact/recoil/retraction beat."""
    return {
        "palm_plane_penetration_capped": palm_plane_min_gap >= -MAX_PALM_PLANE_PENETRATION_M,
        "palm_plane_does_not_deepen": (
            follow_palm_plane_gap >= palm_plane_end_gap + MIN_POST_CONTACT_PLANE_SEPARATION_M
        ),
        "hand_finger_proximity_increases_after_contact": (
            follow_hand_proximity >= contact_hand_proximity + MIN_POST_CONTACT_PROXIMITY_GROWTH_M
        ),
        "receiver_root_recoil": root_dx >= MIN_RESPONSE_ROOT_M,
        "receiver_head_recoil": head_dx >= MIN_RESPONSE_HEAD_M,
        "receiver_torso_recoil": torso_dx >= MIN_RESPONSE_TORSO_M,
        "strike_hand_retracts": guard_follow < guard_contact,
        "strike_hand_returns_to_guard": guard_recovery <= 0.06,
    }


def _pair_metrics(by_frame, side: str, contact_frames: tuple[int, ...], follow: int,
                  recovery: int) -> dict[str, Any]:
    hand = "r" if side == "R" else "l"
    end_contact = contact_frames[-1]
    start_row = by_frame[contact_frames[0]]
    end_row = by_frame[end_contact]
    follow_row = by_frame[follow]
    recovery_row = by_frame[recovery]
    start_receiver = start_row["fighters"]["receiver"]
    end_receiver = end_row["fighters"]["receiver"]
    follow_receiver = follow_row["fighters"]["receiver"]
    start_arm = start_row["attacker_arm"][side]
    end_arm = end_row["attacker_arm"][side]
    follow_arm = follow_row["attacker_arm"][side]
    recovery_arm = recovery_row["attacker_arm"][side]
    gaps = [by_frame[frame][f"{hand}_hand_head_axial_gap_m"] for frame in contact_frames]
    hand_proximities = [
        by_frame[frame][f"{hand}_hand_finger_head_nearest_sample_distance_m"]
        for frame in contact_frames
    ]
    root_dx = abs(follow_receiver["root_world_m"][0] - end_receiver["root_world_m"][0])
    head_dx = _xyz_distance(
        follow_receiver["head_surface_centroid_world_m"],
        end_receiver["head_surface_centroid_world_m"],
    )
    torso_dx = _xyz_distance(follow_receiver["torso_world_m"], end_receiver["torso_world_m"])
    hand_ik_rotation_delta = max(
        _rotation_delta_deg(
            by_frame[frame]["attacker_arm"][side]["hand_ik_target_quaternion_wxyz"],
            end_arm["hand_ik_target_quaternion_wxyz"],
        )
        for frame in contact_frames
    )
    forearm_before = by_frame[contact_frames[0] - 1]["attacker_arm"][side]["forearm_vector_world"]
    forearm_contact = end_arm["forearm_vector_world"]
    forearm_dot = sum(a * b for a, b in zip(forearm_before, forearm_contact))
    forearm_len = math.sqrt(sum(value * value for value in forearm_before)) * math.sqrt(
        sum(value * value for value in forearm_contact)
    )
    forearm_delta = math.degrees(math.acos(max(-1.0, min(1.0, forearm_dot / forearm_len))))
    checks = _contact_pair_checks(
        palm_plane_min_gap=min(gaps),
        palm_plane_end_gap=by_frame[end_contact][f"{hand}_hand_head_axial_gap_m"],
        follow_palm_plane_gap=follow_row[f"{hand}_hand_head_axial_gap_m"],
        root_dx=root_dx,
        head_dx=head_dx,
        torso_dx=torso_dx,
        guard_contact=end_arm["guard_distance_m"],
        guard_follow=follow_arm["guard_distance_m"],
        guard_recovery=recovery_arm["guard_distance_m"],
        contact_hand_proximity=hand_proximities[-1],
        follow_hand_proximity=follow_row[
            f"{hand}_hand_finger_head_nearest_sample_distance_m"
        ],
    )
    return {
        "contact_frames": list(contact_frames),
        "follow_frame": follow,
        "recovery_frame": recovery,
        "palm_plane_axial_gaps_m": gaps,
        "follow_palm_plane_axial_gap_m": follow_row[f"{hand}_hand_head_axial_gap_m"],
        "post_contact_palm_plane_separation_m": round(
            follow_row[f"{hand}_hand_head_axial_gap_m"]
            - by_frame[end_contact][f"{hand}_hand_head_axial_gap_m"], 7,
        ),
        "hand_finger_nearest_sample_distance_m": {
            "contact_frames": hand_proximities,
            "follow": follow_row[f"{hand}_hand_finger_head_nearest_sample_distance_m"],
        },
        "hand_finger_nearest_sample_proximity_growth_m": round(
            follow_row[f"{hand}_hand_finger_head_nearest_sample_distance_m"]
            - hand_proximities[-1], 7,
        ),
        "receiver_root_recoil_m": round(root_dx, 7),
        "receiver_head_recoil_m": round(head_dx, 7),
        "receiver_torso_recoil_m": round(torso_dx, 7),
        "attacker_hip_pivot_rad_at_contact": round(
            sum(by_frame[frame]["attacker_pivot"]["hips"] for frame in contact_frames)
            / len(contact_frames), 7,
        ),
        "attacker_chest_pivot_rad_at_contact": round(
            sum(by_frame[frame]["attacker_pivot"]["chest"] for frame in contact_frames)
            / len(contact_frames), 7,
        ),
        "digit_control_euler_activity_abs_sum_rad_at_contact": (
            end_arm["digit_control_euler_activity_abs_sum_rad"]
        ),
        "guard_distance_m": {
            "contact": end_arm["guard_distance_m"],
            "follow": follow_arm["guard_distance_m"],
            "recovery": recovery_arm["guard_distance_m"],
        },
        "hand_ik_target_rotation_change_deg_across_contact_frames": round(
            hand_ik_rotation_delta, 5,
        ),
        "wrist_alignment_status": "unverified_MM-HAND-01",
        "forearm_direction_change_deg_from_approach": round(forearm_delta, 5),
        "forearm_length_m_at_contact": end_arm["forearm_length_m"],
        "checks": checks,
    }


def _summary(rows, budgets) -> dict[str, Any]:
    by_frame = {row["frame"]: row for row in rows}
    legacy = fight._summary(rows, budgets)
    checks = dict(legacy["checks"])
    palm_nearest_samples = legacy.pop("contact_min_surface_distance_m")
    palm_plane_gaps = legacy.pop("contact_axial_gap_m")
    legacy["palm_plane_nearest_sample_distance_m"] = palm_nearest_samples
    legacy["palm_plane_axial_gap_m"] = palm_plane_gaps
    checks.pop("contact_surface_gap", None)
    checks["palm_plane_penetration_capped"] = checks.pop("contact_axial_penetration")
    # The legacy metric treats a deeper axial gap as better follow-through.
    checks.pop("right_follow_through", None)
    checks.pop("left_follow_through", None)
    jab = _pair_metrics(by_frame, "R", CONTACT_FRAMES["right"], 12, 15)
    hook = _pair_metrics(by_frame, "L", CONTACT_FRAMES["left"], 25, 28)
    checks.update({f"right_{name}": passed for name, passed in jab["checks"].items()})
    checks.update({f"left_{name}": passed for name, passed in hook["checks"].items()})
    hook_head_advantage = hook["receiver_head_recoil_m"] - jab["receiver_head_recoil_m"]
    hook_pivot_stronger = (
        abs(hook["attacker_hip_pivot_rad_at_contact"])
        > abs(jab["attacker_hip_pivot_rad_at_contact"])
    )
    checks["lead_hook_hip_pivot_exceeds_jab"] = hook_pivot_stronger
    checks["lead_hook_head_recoil_exceeds_jab"] = (
        hook_head_advantage >= MIN_HOOK_HEAD_RECOIL_ADVANTAGE_M
    )
    return {
        **legacy,
        "checks": checks,
        "contact_transfer": {
            "contact_geometry_status": "palm_plane_alignment_and_nearest_sample_proximity_only",
            "contact_surface_acceptance": "not_established",
            "hand_finger_sample_note": (
                "Nearest evaluated DEF-hand and finger/thumb mesh samples; not a knuckle-contact test."
            ),
            "wrist_alignment_status": "unverified_MM-HAND-01",
            "digit_shape_status": "unverified_MM-HAND-01",
            "stylized_budgets_m": {
                "max_palm_plane_penetration": MAX_PALM_PLANE_PENETRATION_M,
                "min_root_response": MIN_RESPONSE_ROOT_M,
                "min_head_response": MIN_RESPONSE_HEAD_M,
                "min_torso_response": MIN_RESPONSE_TORSO_M,
                "min_post_contact_plane_separation": MIN_POST_CONTACT_PLANE_SEPARATION_M,
                "min_post_contact_hand_proximity_growth": MIN_POST_CONTACT_PROXIMITY_GROWTH_M,
                "min_hook_head_recoil_advantage": MIN_HOOK_HEAD_RECOIL_ADVANTAGE_M,
                "max_lateral_alignment_adjustment_residual": (
                    MAX_LATERAL_PROXIMITY_ADJUSTMENT_RESIDUAL_M
                ),
                "striking_digit_control_rotation_multiplier": (
                    STRIKING_DIGIT_CONTROL_MULTIPLIER
                ),
            },
            "style_comparison": {
                "interpretation": "measured_scripted_response_not_visual_or_physics_approval",
                "jab_hip_pivot_abs_rad": round(
                    abs(jab["attacker_hip_pivot_rad_at_contact"]), 7,
                ),
                "lead_hook_hip_pivot_abs_rad": round(
                    abs(hook["attacker_hip_pivot_rad_at_contact"]), 7,
                ),
                "lead_hook_head_recoil_advantage_m": round(hook_head_advantage, 7),
            },
            "right_jab": jab,
            "left_hook": hook,
        },
    }


def _verify_renders(receipt: dict[str, Any], receipt_path: Path) -> str:
    renders = receipt.get("renders")
    if not isinstance(renders, dict) or not renders:
        return "not_listed"
    for frame in RENDER_FRAMES:
        record = renders.get(str(frame))
        name = f"frame-{frame:02d}.png"
        path = receipt_path.parent / name
        if (not isinstance(record, dict) or record.get("path") != name
                or not path.is_file() or path.is_symlink()
                or fight.sha256(path) != record.get("sha256")
                or path.stat().st_size != record.get("bytes")):
            raise fight.FightMotionError(f"contact-transfer render missing or changed: frame {frame}")
    if len(renders) != len(RENDER_FRAMES):
        raise fight.FightMotionError("contact-transfer render manifest has unexpected entries")
    return "verified"


def _validate_reopened(rows, counts, receipt, fixture) -> None:
    if receipt.get("schema") != SCHEMA:
        raise fight.FightMotionError("reopened contact-transfer receipt schema differs")
    if receipt.get("fixture_sha256") != fight.FIXTURE_SHA256:
        raise fight.FightMotionError("contact-transfer receipt fixture hash differs")
    if receipt.get("roles") != fixture["roles"]:
        raise fight.FightMotionError("contact-transfer receipt roles differ")
    if receipt.get("source_clock_windows") != fixture["observed_windows"]:
        raise fight.FightMotionError("contact-transfer source clock windows differ")
    if receipt.get("mesh_witness_vertex_counts") != counts:
        raise fight.FightMotionError("contact-transfer mesh witness counts differ")
    declared = receipt.get("frames")
    if not isinstance(declared, list) or len(declared) != len(fight.FRAMES):
        raise fight.FightMotionError("contact-transfer receipt lacks all integer frame measurements")
    for frame, observed in zip(fight.FRAMES, rows):
        if declared[frame] != observed:
            raise fight.FightMotionError(f"saved contact-transfer scene differs at frame {frame}")
    summary = _summary(rows, fixture["budgets_m"])
    if receipt.get("metrics") != summary:
        raise fight.FightMotionError("contact-transfer receipt metrics differ from reopened scene")
    if not all(summary["checks"].values()):
        failed = [name for name, value in summary["checks"].items() if not value]
        raise fight.FightMotionError("contact-transfer checks failed: " + ", ".join(failed))


def build_contact_transfer_exchange(bpy, root: Path, fixture_path: Path,
                                    output: Path, *, render: bool,
                                    review_root: Path | None = None):
    """Build an opt-in contact impulse/recoil/retraction proof on the pinned clock."""
    fixture = fight.validate_fixture(root, fixture_path)
    if bpy.app.version_string != "5.2.2 LTS":
        raise fight.FightMotionError(
            f"pinned Blender 5.2.2 LTS required, got {bpy.app.version_string}"
        )
    if "--disable-autoexec" not in sys.argv:
        raise fight.FightMotionError("embedded scripts must be disabled")
    source = root / fixture["source_blend"]["path"]
    source_root = Path(root).resolve()
    fixture_path = Path(fixture_path)
    code_review_root = Path(review_root) if review_root is not None else source_root / fight.REVIEW_RELATIVE
    append = fight._instance_function(fight.CODE_ROOT)
    canonical_review_root = (fight.CODE_ROOT / fight.REVIEW_RELATIVE).resolve(strict=True)
    if code_review_root.resolve(strict=True) != canonical_review_root:
        raise fight.FightMotionError("contact-transfer quarantine differs from this code checkout")
    output = fight.validate_output_target(fight.CODE_ROOT, output)
    output.mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    instances = {}
    for binding, x, heading in (("attacker", 0.58, -math.pi / 2),
                                ("receiver", -0.45, math.pi / 2)):
        instances[binding] = append(
            bpy, source=source, source_sha256=fight.SOURCE_SHA256,
            binding_id=binding, rig_name="Human.rigify",
            object_names=fight.OBJECT_NAMES, position_m=(x, 0.0, 0.0),
            heading_rad=heading,
        )
    camera = fight._stage(bpy, instances)
    fight._key_exchange(bpy, fixture, instances)
    _key_striking_digit_controls(bpy, instances)
    home_feet = _home_feet(bpy, instances)
    indices, _ = _indices(bpy, instances)
    _key_receiver_recoil(bpy, instances, home_feet)

    contact_poses = {}
    for side, frames in (("R", CONTACT_FRAMES["right"]),
                         ("L", CONTACT_FRAMES["left"])):
        for frame in frames:
            contact_poses[side] = _align_palm_plane_for_contact_window(
                bpy, instances, indices, side, frame,
            )
    _retract_to_guard(bpy, instances, contact_poses)

    rows, counts = _measure_contact_transfer(bpy, instances)
    summary = _summary(rows, fixture["budgets_m"])
    if not all(summary["checks"].values()):
        failed = [name for name, value in summary["checks"].items() if not value]
        raise fight.FightMotionError("contact-transfer checks failed: " + ", ".join(failed))
    scene = bpy.context.scene
    scene.frame_set(0)
    blend = output / "contact-transfer.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=False, compress=True)
    if not blend.is_file():
        raise fight.FightMotionError("Blender did not save the contact-transfer scene")
    renders = {}
    if render:
        for frame in RENDER_FRAMES:
            scene.frame_set(frame)
            path = output / f"frame-{frame:02d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
                raise fight.FightMotionError(f"missing or invalid contact-transfer frame {frame}")
            renders[str(frame)] = {
                "path": path.name,
                "sha256": fight.sha256(path),
                "bytes": path.stat().st_size,
            }
    result = {
        "schema": SCHEMA,
        "status": "review_only_diagnostic",
        "mode": "contact_transfer_opt_in",
        "source": {name: fixture[name] for name in
                   ("source_video", "source_clock", "source_blend")},
        "source_blend_sha256_after": fight.sha256(source),
        "fixture_sha256": fight.sha256(fixture_path),
        "provenance_roots": {
            "implementation_checkout": str(fight.CODE_ROOT.resolve()),
            "source_input_checkout": str(source_root),
            "review_quarantine": str(code_review_root.resolve()),
            "review_output": str(output.resolve()),
        },
        "implementation_sha256": fight.sha256(Path(__file__)),
        "fight_motion_sha256": fight.sha256(Path(fight.__file__)),
        "blender": bpy.app.version_string,
        "embedded_scripts": "disabled",
        "fps": scene.render.fps,
        "frame_range": [scene.frame_start, scene.frame_end],
        "camera": {
            "name": camera.name,
            "resolution_px": [scene.render.resolution_x, scene.render.resolution_y],
            "orthographic_scale_m": camera.data.ortho_scale,
        },
        "roles": fixture["roles"],
        "source_clock_windows": fixture["observed_windows"],
        "actions": {binding: instances[binding]["Human.rigify"].animation_data.action.name
                    for binding in instances},
        "mesh_witness_vertex_counts": counts,
        "stylized_budgets_m": summary["contact_transfer"]["stylized_budgets_m"],
        "metrics": summary,
        "render_frames": list(RENDER_FRAMES),
        "renders": renders,
        "scene": {
            "path": blend.name,
            "sha256": fight.sha256(blend),
            "bytes": blend.stat().st_size,
        },
        "frames": rows,
    }
    receipt_path = output / "receipt.json"
    receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    return result


def reopen_contact_transfer(
    bpy, scene_path: Path, receipt_path: Path, *, root: Path | None = None,
    fixture_path: Path | None = None, review_root: Path | None = None,
) -> dict[str, Any]:
    if bpy.app.version_string != "5.2.2 LTS" or "--disable-autoexec" not in sys.argv:
        raise fight.FightMotionError("pinned scripts-disabled Blender is required to reopen")
    scene_path = Path(scene_path)
    receipt_path = Path(receipt_path)
    source_root = Path(root).resolve() if root is not None else fight.CODE_ROOT.resolve()
    fixture_path = Path(fixture_path) if fixture_path is not None else source_root / fight.FIXTURE_RELATIVE
    code_review_root = Path(review_root) if review_root is not None else source_root / fight.REVIEW_RELATIVE
    canonical_review_root = (fight.CODE_ROOT / fight.REVIEW_RELATIVE).resolve(strict=True)
    if code_review_root.resolve(strict=True) != canonical_review_root:
        raise fight.FightMotionError("reopen review quarantine differs from this code checkout")
    fight._reject_redirected_output_chain(code_review_root)
    fight._reject_redirected_output_chain(receipt_path.parent)
    if (receipt_path.is_symlink() or not receipt_path.is_file()
            or receipt_path.parent.parent.resolve(strict=True) != canonical_review_root):
        raise fight.FightMotionError("contact-transfer receipt escapes this review quarantine")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    scene_record = receipt.get("scene")
    if (receipt.get("schema") != SCHEMA or not isinstance(scene_record, dict)
            or scene_record.get("path") != scene_path.name
            or scene_path.parent.resolve() != receipt_path.parent.resolve()
            or not scene_path.is_file() or scene_path.is_symlink()
            or scene_path.parent.resolve(strict=True) != receipt_path.parent.resolve(strict=True)
            or fight.sha256(scene_path) != scene_record.get("sha256")
            or scene_path.stat().st_size != scene_record.get("bytes")):
        raise fight.FightMotionError("contact-transfer scene hash/receipt mismatch")
    if "FINISHED" not in bpy.ops.wm.open_mainfile(
        filepath=str(scene_path), load_ui=False, use_scripts=False,
    ):
        raise fight.FightMotionError("Blender could not reopen the contact-transfer scene")
    scene = bpy.context.scene
    if (scene.render.fps != 30 or scene.render.fps_base != 1.0
            or (scene.frame_start, scene.frame_end) != (0, 35)
            or scene.render.resolution_percentage != 100
            or (scene.render.resolution_x, scene.render.resolution_y) != fight.RENDER_SIZE):
        raise fight.FightMotionError("reopened contact-transfer scene clock differs")
    instances = {
        binding: {name: bpy.data.objects[f"{binding}__{name}"]
                  for name in fight.OBJECT_NAMES}
        for binding in ("attacker", "receiver")
    }
    fixture = fight.validate_fixture(source_root, fixture_path)
    source_blend_path = source_root / fixture["source_blend"]["path"]
    if (receipt.get("implementation_sha256") != fight.sha256(Path(__file__))
            or receipt.get("fight_motion_sha256") != fight.sha256(Path(fight.__file__))):
        raise fight.FightMotionError("contact-transfer implementation hashes differ from reopened code")
    if (receipt.get("fixture_sha256") != fight.sha256(fixture_path)
            or receipt.get("source_blend_sha256_after") != fight.sha256(source_blend_path)):
        raise fight.FightMotionError("contact-transfer fixture/source hashes differ from read-only inputs")
    roots = receipt.get("provenance_roots")
    if (not isinstance(roots, dict)
            or roots.get("implementation_checkout") != str(fight.CODE_ROOT.resolve())
            or roots.get("source_input_checkout") != str(source_root)
            or roots.get("review_quarantine") != str(canonical_review_root)
            or roots.get("review_output") != str(receipt_path.parent.resolve(strict=True))):
        raise fight.FightMotionError("contact-transfer provenance roots differ from requested inputs/output")
    rows, counts = _measure_contact_transfer(bpy, instances)
    _validate_reopened(rows, counts, receipt, fixture)
    render_status = _verify_renders(receipt, receipt_path)
    return {
        "status": "reopened_and_measured",
        "scene_sha256": scene_record["sha256"],
        "checked_frames": list(fight.FRAMES),
        "summary_verified": True,
        "checks": receipt["metrics"]["checks"],
        "render_verification": render_status,
    }
