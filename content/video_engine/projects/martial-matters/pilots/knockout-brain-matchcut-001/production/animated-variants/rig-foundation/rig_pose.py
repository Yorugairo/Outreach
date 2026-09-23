"""Pure frame evaluator for the research-backed 2D rig/contact proof.

The scene is deliberately a bounded schematic: the pose layer owns timing,
FK-authored hand arcs, analytical IK, body weight transfer, lagged head/torso
channels and measurements.  The renderer is a separate consumer of these
poses, so a later character-art pass can keep the same contact contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import math
from pathlib import Path
from typing import Any

from rig_math import (
    IKResult,
    RigidTransform2D,
    Vec2,
    add,
    bounds,
    clamp,
    cubic_bezier,
    distance,
    fall_in,
    fast_out,
    hermite,
    lerp,
    lerp_point,
    minimum_jerk,
    polygon_area,
    scale,
    skin_mesh as weighted_rigid_skin_mesh,
    sub,
    two_bone_ik,
)


def _load_dqs_module() -> Any:
    """Load the parent-owned planar DQS implementation without copying it."""
    dqs_path = Path(__file__).resolve().parent.parent / "rig-skinning" / "dqs.py"
    if not dqs_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("parent_planar_dqs", dqs_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DQS = _load_dqs_module()


FPS = 24
DURATION_S = 4.0
FRAME_COUNT = int(FPS * DURATION_S)
FLOOR_Y = 838.0
HEAD_RADIUS = 48.0
GLOVE_RADIUS = 31.0
FOOT_RADIUS = 28.0
ARM_UPPER = 120.0
ARM_LOWER = 145.0
LEG_UPPER = 115.0
LEG_LOWER = 120.0
RIGHT_CONTACT_T = 27.0 / FPS
HEAD_SNAP_T = 28.0 / FPS
HOOK_CONTACT_T = 50.0 / FPS
FALL_RELEASE_T = 2.25
GROUND_T = 3.55
ATTACKER_STEP_RELEASE_T = 1.72

ATTACKER_FEET: tuple[Vec2, Vec2] = ((324.0, 810.0), (432.0, 810.0))
VICTIM_FEET: tuple[Vec2, Vec2] = ((114.0, 810.0), (222.0, 810.0))
REST_TORSO: tuple[Vec2, ...] = ((-58.0, -182.0), (58.0, -182.0), (64.0, -18.0), (32.0, 72.0), (-32.0, 72.0), (-64.0, -18.0))
TORSO_WEIGHTS: tuple[dict[str, float], ...] = (
    {"chest": 0.90, "pelvis": 0.10},
    {"chest": 0.90, "pelvis": 0.10},
    {"chest": 0.55, "pelvis": 0.45},
    {"chest": 0.10, "pelvis": 0.90},
    {"chest": 0.10, "pelvis": 0.90},
    {"chest": 0.55, "pelvis": 0.45},
)


def rotate(point: Vec2, angle: float) -> Vec2:
    c = math.cos(angle)
    s = math.sin(angle)
    return (c * point[0] - s * point[1], s * point[0] + c * point[1])


def local_to_world(root: Vec2, angle: float, local: Vec2) -> Vec2:
    return add(root, rotate(local, angle))


def pulse(t: float, start: float, end: float, *, ease_in: str = "fast", ease_out: str = "minimum") -> float:
    """One explicitly scoped transfer envelope; not a global easing default."""
    if t <= start or t >= end:
        return 0.0
    mid = (start + end) * 0.5
    if t <= mid:
        raw = (t - start) / max(mid - start, 1.0e-9)
        return fast_out(raw) if ease_in == "fast" else minimum_jerk(raw)
    raw = (t - mid) / max(end - mid, 1.0e-9)
    return 1.0 - (minimum_jerk(raw) if ease_out == "minimum" else fast_out(raw))


def breathing(t: float) -> float:
    """A non-sinusoidal breath pulse for the standing guard."""
    cycle = t % 3.2
    if cycle < 1.25:
        return 2.0 * minimum_jerk(cycle / 1.25)
    if cycle < 2.25:
        return 2.0 * (1.0 - minimum_jerk((cycle - 1.25) / 1.0))
    return 0.0


def victim_root_state(t: float) -> tuple[Vec2, float, float]:
    """Return pelvis root, body angle and scale; torso response lags head snap."""
    breath = breathing(t) if t < RIGHT_CONTACT_T else 0.0
    if t < 1.30:
        return ((170.0, 605.0 + breath), 0.0, 1.0)
    if t < 1.55:
        u = minimum_jerk((t - 1.30) / 0.25)
        return (lerp_point((170.0, 605.0), (151.0, 620.0), u), math.radians(-10.0) * u, 1.0)
    if t < HOOK_CONTACT_T:
        return ((151.0, 620.0), math.radians(-10.0), 1.0)
    if t < 2.30:
        u = fast_out((t - HOOK_CONTACT_T) / (2.30 - HOOK_CONTACT_T))
        return (lerp_point((151.0, 620.0), (200.0, 660.0), u), lerp(math.radians(-10.0), math.radians(-25.0), u), 1.0)
    if t < GROUND_T:
        u = fall_in((t - 2.30) / (GROUND_T - 2.30))
        # Pull the root down to the mat while keeping the authored body at
        # full scale. The folded foot targets then provide the floor contact.
        return (lerp_point((200.0, 660.0), (340.0, 742.0), u), lerp(math.radians(-25.0), math.radians(-90.0), u), 1.0)
    return ((340.0, 742.0), math.radians(-90.0), 1.0)


def victim_head_offset(t: float) -> Vec2:
    """Head snaps on contact; torso root begins moving 175 ms later."""
    if t < RIGHT_CONTACT_T:
        return (0.0, 0.0)
    if t < 1.40:
        return hermite((0.0, 0.0), (-45.0, -8.0), (0.0, 0.0), (-120.0, -8.0), (t - RIGHT_CONTACT_T) / (1.40 - RIGHT_CONTACT_T), 1.40 - RIGHT_CONTACT_T)
    if t < HOOK_CONTACT_T:
        return (-45.0, -8.0)
    if t < 2.30:
        return hermite((-45.0, -8.0), (-70.0, 10.0), (-110.0, 0.0), (-40.0, 25.0), (t - HOOK_CONTACT_T) / (2.30 - HOOK_CONTACT_T), 2.30 - HOOK_CONTACT_T)
    if t < 2.55:
        return lerp_point((-70.0, 10.0), (0.0, 0.0), minimum_jerk((t - 2.30) / 0.25))
    # Explicit secondary head settling after the torso reaches the mat.
    return (0.0, 40.0)


def victim_head_position(t: float) -> Vec2:
    root, angle, _ = victim_root_state(t)
    return add(local_to_world(root, angle, (0.0, -230.0)), victim_head_offset(t))


def victim_scale(t: float) -> float:
    return victim_root_state(t)[2]


def attacker_weight_transfer(t: float) -> float:
    return 8.0 * pulse(t, 0.65, 1.48) + 10.0 * pulse(t, 1.58, 2.34)


def attacker_state(t: float) -> tuple[Vec2, float, float, float]:
    transfer = attacker_weight_transfer(t)
    right_drive = pulse(t, 0.65, 1.48)
    hook_drive = pulse(t, 1.58, 2.34)
    # The second strike includes a compact step-in; this keeps the left glove
    # physically reachable without changing either authored bone length.
    root = (380.0 + transfer - 110.0 * hook_drive, 605.0 + 1.5 * right_drive + 2.0 * hook_drive)
    torso_angle = math.radians(-3.0 * right_drive - 4.0 * hook_drive)
    # Head and shoulders carry a small lagged response rather than a rigid
    # slot swap. The delay is a pure time translation and remains seek-safe.
    head_angle = math.radians(-1.0 * pulse(max(0.0, t - 0.08), 0.65, 1.48) - 1.5 * pulse(max(0.0, t - 0.08), 1.58, 2.34))
    return root, torso_angle, head_angle, 1.0


def right_hand_target(t: float) -> Vec2:
    contact_head = victim_head_position(RIGHT_CONTACT_T)
    contact = add(contact_head, (HEAD_RADIUS + GLOVE_RADIUS, 0.0))
    guard = (324.0, 318.0)
    follow = (contact[0] - 52.0, contact[1] + 2.0)
    load = (300.0, 330.0)
    if t < 0.72:
        return guard
    if t < 0.95:
        return hermite(guard, load, (0.0, -10.0), (15.0, 0.0), (t - 0.72) / 0.23, 0.23)
    if t < RIGHT_CONTACT_T:
        # A short four-frame extension carries nonzero velocity through the
        # surface contact; the earlier interval is a visible load, not a
        # slow float into the face.
        return hermite(load, contact, (15.0, 0.0), (-220.0, -5.0), (t - 0.95) / (RIGHT_CONTACT_T - 0.95), RIGHT_CONTACT_T - 0.95)
    if t < 1.35:
        return hermite(contact, follow, (-220.0, -5.0), (-5.0, 0.0), (t - RIGHT_CONTACT_T) / (1.35 - RIGHT_CONTACT_T), 1.35 - RIGHT_CONTACT_T)
    if t < 1.55:
        return lerp_point(follow, guard, minimum_jerk((t - 1.35) / 0.20))
    return guard


def left_hook_target(t: float) -> Vec2:
    contact_head = victim_head_position(HOOK_CONTACT_T)
    contact = add(contact_head, (HEAD_RADIUS + GLOVE_RADIUS, 0.0))
    guard = (426.0, 318.0)
    # A compact post-contact recovery point stays within the fixed bone reach
    # envelope while still carrying the glove away from the face.
    follow = (contact[0] + 20.0, contact[1] + 38.0)
    load = (468.0, 360.0)
    contact_velocity = (-130.0, 46.0)
    arc_start = 1.80
    if t < arc_start:
        if t < 1.72:
            return guard
        return lerp_point(guard, load, minimum_jerk((t - 1.72) / (arc_start - 1.72)))
    if t < HOOK_CONTACT_T:
        u = (t - arc_start) / (HOOK_CONTACT_T - arc_start)
        # Match the outgoing Hermite tangent at contact so the hook does not
        # kink when it crosses from authored FK arc to follow-through.
        c2 = sub(contact, scale(contact_velocity, (HOOK_CONTACT_T - arc_start) / 3.0))
        return cubic_bezier(load, (500.0, 420.0), c2, contact, u)
    if t < 2.30:
        return hermite(contact, follow, contact_velocity, (-5.0, 0.0), (t - HOOK_CONTACT_T) / (2.30 - HOOK_CONTACT_T), 2.30 - HOOK_CONTACT_T)
    if t < 2.48:
        return lerp_point(follow, guard, minimum_jerk((t - 2.30) / 0.18))
    return guard


def victim_arm_target(t: float, side: str) -> Vec2:
    root, angle, _ = victim_root_state(t)
    if t >= FALL_RELEASE_T:
        return local_to_world(root, angle, (-54.0, -120.0) if side == "right" else (54.0, -120.0))
    return local_to_world(root, angle, (-118.0, -270.0) if side == "right" else (118.0, -270.0))


def foot_targets(root: Vec2, angle: float, t: float, *, victim: bool) -> tuple[Vec2, Vec2]:
    if not victim:
        if t < ATTACKER_STEP_RELEASE_T:
            return ATTACKER_FEET
        # The attacker explicitly releases the planted-foot constraint for a
        # compact step-in before the hook; the new anchors remain fixed after
        # the step rather than silently sliding under the pelvis.
        u = minimum_jerk(min(1.0, (t - ATTACKER_STEP_RELEASE_T) / 0.24))
        offset = -55.0 * u
        return ((ATTACKER_FEET[0][0] + offset, ATTACKER_FEET[0][1]), (ATTACKER_FEET[1][0] + offset, ATTACKER_FEET[1][1]))
    if t < FALL_RELEASE_T:
        return VICTIM_FEET
    raw = (local_to_world(root, angle, (-64.0, 230.0)), local_to_world(root, angle, (64.0, -220.0)))
    # Once the planted constraint is released, the feet fold sideways but the
    # rendered foot capsules remain on/above the mat rather than penetrating.
    return tuple((point[0], min(point[1], FLOOR_Y - FOOT_RADIUS)) for point in raw)  # type: ignore[return-value]


def chest_transform(root: Vec2, body_angle: float, torso_lag: float) -> RigidTransform2D:
    anchor_local = (0.0, -80.0)
    anchor_world = local_to_world(root, body_angle, anchor_local)
    chest_angle = body_angle + torso_lag
    rotated_anchor = rotate(anchor_local, chest_angle)
    translation = sub(anchor_world, rotated_anchor)
    return RigidTransform2D(translation[0], translation[1], chest_angle)


def torso_mesh(root: Vec2, body_angle: float, torso_lag: float) -> list[Vec2]:
    transforms = {
        "pelvis": RigidTransform2D(root[0], root[1], body_angle),
        "chest": chest_transform(root, body_angle, torso_lag),
    }
    if DQS is not None:
        encoded = {name: DQS.encode(transform.tx, transform.ty, transform.angle) for name, transform in transforms.items()}
        return DQS.skin_mesh(list(REST_TORSO), encoded, list(TORSO_WEIGHTS))
    # Local fallback remains a measured comparison path, never called DQS.
    return weighted_rigid_skin_mesh(REST_TORSO, transforms, TORSO_WEIGHTS)


@dataclass(frozen=True)
class FighterPose:
    name: str
    root: Vec2
    body_angle: float
    torso_lag: float
    head_angle: float
    scale: float
    head: Vec2
    head_radius: float
    feet_targets: tuple[Vec2, Vec2]
    feet: tuple[IKResult, IKResult]
    arms: tuple[tuple[str, IKResult], tuple[str, IKResult]]
    torso: tuple[Vec2, ...]

    def arm(self, name: str) -> IKResult:
        for arm_name, result in self.arms:
            if arm_name == name:
                return result
        raise KeyError(name)


@dataclass(frozen=True)
class FramePose:
    frame: int
    time_s: float
    victim: FighterPose
    attacker: FighterPose
    brain: Vec2 | None
    right_impact: float
    hook_impact: float


def build_fighter(name: str, t: float, *, victim: bool) -> FighterPose:
    if victim:
        root, body_angle, scale_value = victim_root_state(t)
        torso_lag = math.radians(2.0) * pulse(t, 1.30, 1.75) + math.radians(4.0) * pulse(t, HOOK_CONTACT_T, 2.55)
        head_angle = body_angle + torso_lag * 0.35
        head = add(local_to_world(root, body_angle, (0.0, -230.0)), victim_head_offset(t))
        right_target = victim_arm_target(t, "right")
        left_target = victim_arm_target(t, "left")
        feet_target = foot_targets(root, body_angle, t, victim=True)
        right_shoulder = local_to_world(root, body_angle, (-32.0, -164.0))
        left_shoulder = local_to_world(root, body_angle, (32.0, -164.0))
        fall_arm_bend = -1 if t >= FALL_RELEASE_T else 1
        right_arm = two_bone_ik(right_shoulder, right_target, ARM_UPPER, ARM_LOWER, bend=fall_arm_bend)
        left_arm = two_bone_ik(left_shoulder, left_target, ARM_UPPER, ARM_LOWER, bend=fall_arm_bend)
    else:
        root, body_angle, head_angle, scale_value = attacker_state(t)
        torso_lag = body_angle * 0.65
        head = local_to_world(root, head_angle, (0.0, -230.0))
        right_target = right_hand_target(t)
        left_target = left_hook_target(t)
        feet_target = foot_targets(root, body_angle, t, victim=False)
        right_shoulder = local_to_world(root, body_angle, (-32.0, -164.0))
        left_shoulder = local_to_world(root, body_angle, (32.0, -164.0))
        right_arm = two_bone_ik(right_shoulder, right_target, ARM_UPPER, ARM_LOWER, bend=1)
        left_arm = two_bone_ik(left_shoulder, left_target, ARM_UPPER, ARM_LOWER, bend=1)
    right_leg_root = local_to_world(root, body_angle, (-25.0, 4.0))
    left_leg_root = local_to_world(root, body_angle, (25.0, 4.0))
    right_leg_bend = (-1 if t >= FALL_RELEASE_T else 1) if victim else -1
    right_leg = two_bone_ik(right_leg_root, feet_target[0], LEG_UPPER, LEG_LOWER, bend=right_leg_bend)
    left_leg = two_bone_ik(left_leg_root, feet_target[1], LEG_UPPER, LEG_LOWER, bend=-1)
    return FighterPose(
        name=name,
        root=root,
        body_angle=body_angle,
        torso_lag=torso_lag,
        head_angle=head_angle,
        scale=scale_value,
        head=head,
        head_radius=HEAD_RADIUS * scale_value,
        feet_targets=feet_target,
        feet=(right_leg, left_leg),
        arms=(("right", right_arm), ("left", left_arm)),
        torso=tuple(torso_mesh(root, body_angle, torso_lag)),
    )


def brain_position(t: float) -> Vec2 | None:
    if t < HEAD_SNAP_T or t > 1.78:
        return None
    start_head = victim_head_position(HEAD_SNAP_T)
    end_head = victim_head_position(1.78)
    u = (t - HEAD_SNAP_T) / (1.78 - HEAD_SNAP_T)
    return cubic_bezier(add(start_head, (-2.0, -48.0)), add(start_head, (-26.0, -82.0)), add(end_head, (-50.0, -110.0)), add(end_head, (-78.0, -88.0)), fast_out(u))


def evaluate_frame(time_s: float) -> FramePose:
    time_s = clamp(time_s, 0.0, DURATION_S - 1.0 / FPS)
    frame = int(round(time_s * FPS))
    time_s = frame / FPS
    victim = build_fighter("left_victim", time_s, victim=True)
    attacker = build_fighter("right_attacker", time_s, victim=False)
    # Impacts are post-contact response envelopes. They must not flash during
    # the anticipation/swing-in interval before a glove reaches the head.
    right_impact = max(0.0, 1.0 - (time_s - RIGHT_CONTACT_T) / 0.13) if time_s >= RIGHT_CONTACT_T else 0.0
    hook_impact = max(0.0, 1.0 - (time_s - HOOK_CONTACT_T) / 0.15) if time_s >= HOOK_CONTACT_T else 0.0
    return FramePose(frame, time_s, victim, attacker, brain_position(time_s), right_impact, hook_impact)


def evaluate_all_frames() -> list[FramePose]:
    return [evaluate_frame(frame / FPS) for frame in range(FRAME_COUNT)]


def surface_points(fighter: FighterPose) -> list[Vec2]:
    points = list(fighter.torso)
    # Include capsule extrema, not only joints, so floor clearance accounts for
    # rendered limb radii rather than allowing a segment to penetrate unseen.
    for ik, radius in (
        (fighter.feet[0], 22.0),
        (fighter.feet[1], 22.0),
        (fighter.arm("right"), 19.0),
        (fighter.arm("left"), 19.0),
    ):
        for start, end in ((ik.root, ik.elbow), (ik.elbow, ik.end)):
            delta = sub(end, start)
            length = max(distance(start, end), 1.0e-9)
            normal = (-delta[1] / length * radius, delta[0] / length * radius)
            points.extend((add(start, normal), sub(start, normal), add(end, normal), sub(end, normal)))
    points.extend((
        (fighter.head[0] - fighter.head_radius, fighter.head[1]),
        (fighter.head[0] + fighter.head_radius, fighter.head[1]),
        (fighter.head[0], fighter.head[1] - fighter.head_radius),
        (fighter.head[0], fighter.head[1] + fighter.head_radius),
    ))
    for foot in fighter.feet:
        points.extend(((foot.end[0] - FOOT_RADIUS, foot.end[1]), (foot.end[0] + FOOT_RADIUS, foot.end[1]), (foot.end[0], foot.end[1] + FOOT_RADIUS)))
    for arm_name in ("right", "left"):
        hand = fighter.arm(arm_name).end
        points.extend(((hand[0] - GLOVE_RADIUS, hand[1]), (hand[0] + GLOVE_RADIUS, hand[1]), (hand[0], hand[1] + GLOVE_RADIUS)))
    return points


def floor_receipt(fighter: FighterPose) -> dict[str, Any]:
    box = bounds(surface_points(fighter))
    max_surface_y = box[3]
    return {"bounds_px": [round(value, 3) for value in box], "max_surface_y_px": round(max_surface_y, 3), "floor_y_px": FLOOR_Y, "clearance_px": round(FLOOR_Y - max_surface_y, 3), "no_penetration": max_surface_y <= FLOOR_Y + 0.5, "near_floor": 0.0 <= FLOOR_Y - max_surface_y <= 16.0}


def skinning_receipt(fighter: FighterPose) -> dict[str, Any]:
    rest_signed = polygon_area(REST_TORSO)
    deformed_signed = polygon_area(fighter.torso)
    rest_triangle_signed = polygon_area(REST_TORSO[:3])
    deformed_triangle_signed = polygon_area(fighter.torso[:3])
    return {"representation": "planar_unit_dual_quaternion_blend" if DQS is not None else "normalized_per_point_rigid_transform_blend_fallback", "rest_polygon_area": round(abs(rest_signed), 4), "deformed_polygon_area": round(abs(deformed_signed), 4), "rest_triangle_area": round(abs(rest_triangle_signed), 4), "deformed_triangle_area": round(abs(deformed_triangle_signed), 4), "triangle_orientation_preserved": (rest_triangle_signed * deformed_triangle_signed > 0.0), "global_volume_claim": False, "area_is_measured_not_guaranteed": True}


def frame_measurement(pose: FramePose, previous: FramePose | None = None) -> dict[str, Any]:
    victim = pose.victim
    attacker = pose.attacker
    right_hand = attacker.arm("right").end
    left_hand = attacker.arm("left").end
    right_gap = distance(right_hand, victim.head) - (GLOVE_RADIUS + victim.head_radius)
    left_gap = distance(left_hand, victim.head) - (GLOVE_RADIUS + victim.head_radius)
    if previous is None:
        right_velocity = 0.0
        left_velocity = 0.0
    else:
        right_velocity = distance(right_hand, previous.attacker.arm("right").end) * FPS
        left_velocity = distance(left_hand, previous.attacker.arm("left").end) * FPS
    standing_slips = [distance(current.end, fixed) for current, fixed in zip(attacker.feet, ATTACKER_FEET)]
    if pose.time_s < FALL_RELEASE_T:
        standing_slips.extend(distance(current.end, fixed) for current, fixed in zip(victim.feet, VICTIM_FEET))
    link_measurements: list[dict[str, Any]] = []
    for owner, limbs in (("attacker", (attacker.arm("right"), attacker.arm("left"), *attacker.feet)), ("victim", (victim.arm("right"), victim.arm("left"), *victim.feet))):
        for index, limb in enumerate(limbs):
            link_measurements.append({"owner": owner, "index": index, "upper_rest_px": limb.upper_length, "lower_rest_px": limb.lower_length, "upper_actual_px": round(distance(limb.root, limb.elbow), 6), "lower_actual_px": round(distance(limb.elbow, limb.end), 6), "upper_error_px": round(limb.upper_error, 8), "lower_error_px": round(limb.lower_error, 8), "target_reachable": limb.reachable, "target_error_px": round(limb.target_error, 6)})
    return {"frame": pose.frame, "time_s": round(pose.time_s, 6), "contact": {"right_straight_surface_gap_px": round(right_gap, 6), "left_hook_surface_gap_px": round(left_gap, 6), "right_velocity_px_s": round(right_velocity, 6), "left_velocity_px_s": round(left_velocity, 6)}, "foot_slip_px": round(max(standing_slips or [0.0]), 6), "limb_lengths": link_measurements, "reachability": [item["target_reachable"] for item in link_measurements], "head_center_px": [round(victim.head[0], 4), round(victim.head[1], 4)], "torso_root_px": [round(victim.root[0], 4), round(victim.root[1], 4)], "head_response_offset_px": [round(value, 4) for value in victim_head_offset(pose.time_s)], "floor": {"victim": floor_receipt(victim), "attacker": floor_receipt(attacker)}, "skinning": skinning_receipt(victim), "brain_visible": pose.brain is not None}
