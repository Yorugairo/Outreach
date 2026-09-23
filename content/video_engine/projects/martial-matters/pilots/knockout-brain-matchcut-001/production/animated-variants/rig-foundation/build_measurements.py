"""Emit the deterministic pose/contact receipt for the rig-foundation proof."""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rig_pose as rig


ROOT = Path(__file__).resolve().parent


def _frame_receipts(poses: list[rig.FramePose]) -> list[dict]:
    return [rig.frame_measurement(pose, poses[index - 1] if index else None) for index, pose in enumerate(poses)]


def _max_link_error(frames: list[dict]) -> float:
    return max(
        max(abs(item[key]) for item in frame["limb_lengths"] for key in ("upper_error_px", "lower_error_px"))
        for frame in frames
    )


def build_receipt() -> tuple[dict, dict]:
    poses = rig.evaluate_all_frames()
    frames = _frame_receipts(poses)
    ground = frames[round(rig.GROUND_T * rig.FPS)]
    final = frames[-1]
    max_floor_penetration = max(
        max(0.0, -frame["floor"][owner]["clearance_px"])
        for frame in frames
        for owner in ("victim", "attacker")
    )
    min_floor_clearance = min(
        frame["floor"][owner]["clearance_px"]
        for frame in frames
        for owner in ("victim", "attacker")
    )
    planted_frames = [frame for frame in frames if frame["time_s"] < rig.ATTACKER_STEP_RELEASE_T]
    pre_contact = frames[round(rig.RIGHT_CONTACT_T * rig.FPS) - 1]
    contact = frames[round(rig.RIGHT_CONTACT_T * rig.FPS)]
    recoil = frames[round(rig.HEAD_SNAP_T * rig.FPS)]
    hook = frames[round(rig.HOOK_CONTACT_T * rig.FPS)]
    seek_equivalent = all(poses[index] == rig.evaluate_frame(index / rig.FPS) for index in reversed(range(rig.FRAME_COUNT)))
    reachable_count = sum(1 for frame in frames for value in frame["reachability"] if value)
    total_targets = sum(len(frame["reachability"]) for frame in frames)
    summary = {
        "schema": "rig-foundation.receipt.v1",
        "canvas": {"width": 540, "height": 960, "fps": rig.FPS, "duration_s": rig.DURATION_S, "frame_count": rig.FRAME_COUNT},
        "representation": {
            "pose": "analytic planar FK arcs + fixed-length two-bone IK",
            "rendered_mesh": "parent planar unit dual-quaternion skinning when available",
            "fallback": "normalized per-point rigid-transform blend (not DQS or BBW)",
            "global_volume_claim": False,
        },
        "events": {
            "right_straight_contact": {"frame": round(rig.RIGHT_CONTACT_T * rig.FPS), "time_s": rig.RIGHT_CONTACT_T, "surface_gap_px": contact["contact"]["right_straight_surface_gap_px"]},
            "head_recoil": {"frame": round(rig.HEAD_SNAP_T * rig.FPS), "time_s": rig.HEAD_SNAP_T, "surface_gap_px": recoil["contact"]["right_straight_surface_gap_px"], "brain_first_visible": recoil["brain_visible"]},
            "left_hook_contact": {"frame": round(rig.HOOK_CONTACT_T * rig.FPS), "time_s": rig.HOOK_CONTACT_T, "surface_gap_px": hook["contact"]["left_hook_surface_gap_px"]},
            "victim_fall_release": {"frame": round(rig.FALL_RELEASE_T * rig.FPS), "time_s": rig.FALL_RELEASE_T},
            "victim_ground": {"frame": round(rig.GROUND_T * rig.FPS), "time_s": rig.GROUND_T, "floor": ground["floor"]["victim"]},
        },
        "checks": {
            "pre_contact_gap_positive_px": pre_contact["contact"]["right_straight_surface_gap_px"] > 0.0,
            "right_contact_zero_surface_gap": abs(contact["contact"]["right_straight_surface_gap_px"]) <= 1.0,
            "hook_contact_zero_surface_gap": abs(hook["contact"]["left_hook_surface_gap_px"]) <= 1.0,
            "contact_velocity_nonzero_px_s": {"right": contact["contact"]["right_velocity_px_s"] > 0.0, "left": hook["contact"]["left_velocity_px_s"] > 0.0},
            "brain_only_after_head_recoil": all((not frame["brain_visible"]) for frame in frames[: round(rig.HEAD_SNAP_T * rig.FPS)]) and recoil["brain_visible"],
            "fixed_lengths_max_error_px": _max_link_error(frames),
            "all_targets_reachable": reachable_count == total_targets,
            "target_count": total_targets,
            "unreachable_target_count": total_targets - reachable_count,
            "planted_foot_max_slip_px_before_release": max(frame["foot_slip_px"] for frame in planted_frames),
            "step_release_time_s": rig.ATTACKER_STEP_RELEASE_T,
            "min_rendered_surface_clearance_px": min_floor_clearance,
            "max_rendered_surface_penetration_px": max_floor_penetration,
            "floor_clearance_pass": max_floor_penetration <= 0.5,
            "seek_order_equivalent": seek_equivalent,
            "skinning_triangle_orientation_all_frames": all(frame["skinning"]["triangle_orientation_preserved"] for frame in frames),
        },
        "final": {
            "victim_head_center_px": final["head_center_px"],
            "victim_floor": final["floor"]["victim"],
            "attacker_floor": final["floor"]["attacker"],
            "victim_scale": poses[-1].victim.scale,
        },
        "frames": frames,
    }
    timing = {
        "schema": "rig-foundation.timing.v1",
        "fps": rig.FPS,
        "duration_s": rig.DURATION_S,
        "events": [
            {"name": "right_straight_contact", "frame": round(rig.RIGHT_CONTACT_T * rig.FPS), "time_s": rig.RIGHT_CONTACT_T, "surface_gap_px": contact["contact"]["right_straight_surface_gap_px"]},
            {"name": "head_recoil_and_brain_release", "frame": round(rig.HEAD_SNAP_T * rig.FPS), "time_s": rig.HEAD_SNAP_T, "surface_gap_px": recoil["contact"]["right_straight_surface_gap_px"]},
            {"name": "attacker_step_release", "frame": round(rig.ATTACKER_STEP_RELEASE_T * rig.FPS), "time_s": rig.ATTACKER_STEP_RELEASE_T},
            {"name": "left_hook_contact", "frame": round(rig.HOOK_CONTACT_T * rig.FPS), "time_s": rig.HOOK_CONTACT_T, "surface_gap_px": hook["contact"]["left_hook_surface_gap_px"]},
            {"name": "victim_fall_release", "frame": round(rig.FALL_RELEASE_T * rig.FPS), "time_s": rig.FALL_RELEASE_T},
            {"name": "victim_grounded", "frame": round(rig.GROUND_T * rig.FPS), "time_s": rig.GROUND_T, "floor_clearance_px": ground["floor"]["victim"]["clearance_px"]},
        ],
        "note": "World-space timing receipt; parent renderer applies a constant camera fit for the 540x960 proof.",
    }
    return summary, timing


def main() -> None:
    summary, timing = build_receipt()
    (ROOT / "measurements.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ROOT / "timing.json").write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"measurements": str(ROOT / "measurements.json"), "timing": str(ROOT / "timing.json"), "frames": summary["canvas"]["frame_count"], "floor_clearance_pass": summary["checks"]["floor_clearance_pass"], "seek_order_equivalent": summary["checks"]["seek_order_equivalent"]}))


if __name__ == "__main__":
    main()
