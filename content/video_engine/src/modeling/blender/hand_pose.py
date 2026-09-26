"""Opt-in palmward finger flexion on the existing Rigify fighter.

The source exchange curls three fingers around local Z, sweeping them sideways.
This helper keys all four finger chains around their tested local X flexion axis.
It does not correct wrist orientation or prove a closed striking-fist silhouette,
and never changes the default exchange unless explicitly invoked on a rig.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


FINGERS = ("f_index", "f_middle", "f_ring", "f_pinky")
SEGMENTS = ("01", "02", "03")
FLEXION_RAD = (0.8, 1.15, 0.65)
MIN_PALMWARD_M = 0.025
MIN_RETRACTION_M = 0.010
MAX_LATERAL_SWEEP_M = 0.025
MIN_THUMB_SKELETAL_CLEARANCE_M = 0.006
REVIEW_FRAMES = ((10, "R"), (24, "L"))
RENDER_SIZE = (540, 960)
BLENDER_VERSION = "5.2.2 LTS"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def key_palmward_finger_flexion(bpy, rig, side: str, *, frame: int = 0) -> None:
    """Key the existing finger controls; leave thumb, wrist, IK and body intact."""
    if side not in ("R", "L"):
        raise ValueError("side must be R or L")
    for finger in FINGERS:
        for segment, flexion in zip(SEGMENTS, FLEXION_RAD):
            control = rig.pose.bones[f"{finger}.{segment}.{side}"]
            control.rotation_mode = "XYZ"
            control.rotation_euler = (flexion, 0.0, 0.0)
            control.keyframe_insert(data_path="rotation_euler", frame=frame,
                                    group="mm_finger_flexion")
    bpy.context.view_layer.update()


def _point_segment_distance(point, start, end) -> float:
    span = end - start
    fraction = max(0.0, min(1.0, (point - start).dot(span) / max(span.length_squared, 1e-12)))
    return float((point - (start + span * fraction)).length)


def measure_finger_flexion(bpy, rig, side: str, frame: int) -> dict:
    """Measure evaluated deform endpoints in hand-local space, not Euler totals.

    Thumb clearance is to distal finger *bone segments*, not a skin collision
    witness. The skin and pose still require visual review.
    """
    if side not in ("R", "L"):
        raise ValueError("side must be R or L")
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    hand_inverse = rig.pose.bones[f"DEF-hand.{side}"].matrix.inverted()
    palm_sign = 1 if side == "R" else -1
    thumb = rig.pose.bones[f"DEF-thumb.03.{side}"]
    thumb_tip = hand_inverse @ thumb.tail
    rows = {}
    distances = []
    for finger in FINGERS:
        proximal = rig.pose.bones[f"DEF-{finger}.01.{side}"]
        middle = rig.pose.bones[f"DEF-{finger}.02.{side}"]
        distal = rig.pose.bones[f"DEF-{finger}.03.{side}"]
        mcp = hand_inverse @ proximal.head
        tip = hand_inverse @ distal.tail
        middle_head = hand_inverse @ middle.head
        distal_head = hand_inverse @ distal.head
        rows[finger] = {
            "mcp_hand_local_m": [round(float(value), 6) for value in mcp],
            "tip_hand_local_m": [round(float(value), 6) for value in tip],
            "palmward_m": round(float(palm_sign * (mcp.x - tip.x)), 6),
            "retraction_m": round(float(mcp.y - tip.y), 6),
            "lateral_sweep_m": round(float(abs(tip.z - mcp.z)), 6),
        }
        distances.append(_point_segment_distance(thumb_tip, middle_head, distal_head))
        distances.append(_point_segment_distance(thumb_tip, distal_head, tip))
    return {
        "frame": frame, "side": side, "fingers": rows,
        "thumb_tip_hand_local_m": [round(float(value), 6) for value in thumb_tip],
        "thumb_tip_to_distal_finger_bones_min_m": round(min(distances), 6),
        "thumb_clearance_kind": "skeletal_proxy_not_skin_collision",
    }


def pose_checks(measurement: dict) -> dict[str, bool]:
    rows = measurement["fingers"]
    return {
        "four_finger_tips_palmward": all(
            rows[name]["palmward_m"] >= MIN_PALMWARD_M for name in FINGERS),
        "four_finger_tips_retracted": all(
            rows[name]["retraction_m"] >= MIN_RETRACTION_M for name in FINGERS),
        "lateral_sweep_bounded": all(
            rows[name]["lateral_sweep_m"] <= MAX_LATERAL_SWEEP_M for name in FINGERS),
        "thumb_bone_clearance_proxy":
            measurement["thumb_tip_to_distal_finger_bones_min_m"] >=
            MIN_THUMB_SKELETAL_CLEARANCE_M,
    }


def _require_blender(bpy) -> None:
    if bpy.app.version_string != BLENDER_VERSION or "--disable-autoexec" not in sys.argv:
        raise RuntimeError("pinned Blender 5.2.2 LTS with scripts disabled is required")


def _render(bpy, path: Path, camera, frame: int) -> dict:
    scene = bpy.context.scene
    scene.frame_set(frame)
    scene.camera = camera
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"missing PNG review frame {frame}: {path}")
    return {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}


def build_review(bpy, source_scene: Path, output: Path) -> dict:
    """Build a fresh, isolated ungloved pose scene from a saved exchange."""
    from mathutils import Vector

    _require_blender(bpy)
    source_scene = Path(source_scene).resolve(strict=True)
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("review output must be a new empty directory")
    output.mkdir(parents=True, exist_ok=True)
    source_hash = sha256(source_scene)
    bpy.ops.wm.open_mainfile(filepath=str(source_scene), load_ui=False)
    scene = bpy.context.scene
    if (scene.render.resolution_x, scene.render.resolution_y) != RENDER_SIZE:
        raise RuntimeError("saved exchange is not the pinned 540x960 phone scene")
    attacker = bpy.data.objects["attacker__Human.rigify"]
    original_camera = scene.camera
    if original_camera is None:
        raise RuntimeError("saved exchange has no camera")
    before = {f"{frame}_{side}": measure_finger_flexion(bpy, attacker, side, frame)
              for frame, side in REVIEW_FRAMES}
    scene.frame_set(0)
    bpy.context.view_layer.update()
    for side in ("R", "L"):
        key_palmward_finger_flexion(bpy, attacker, side, frame=0)
    after = {f"{frame}_{side}": measure_finger_flexion(bpy, attacker, side, frame)
             for frame, side in REVIEW_FRAMES}
    checks = {key: pose_checks(value) for key, value in after.items()}
    if not all(all(row.values()) for row in checks.values()):
        raise RuntimeError(f"finger-flexion evaluated geometry failed: {checks}")
    if all(all(pose_checks(row).values()) for row in before.values()):
        raise RuntimeError("source pose already passes; opt-in proof has no contrast")

    # The review camera keeps the original projection direction and follows
    # the strike hand for a close diagnostic. The saved phone camera remains.
    close_camera = original_camera.copy()
    close_camera.data = original_camera.data.copy()
    close_camera.name = "HandPoseCloseReviewCamera"
    close_camera.data.ortho_scale = 0.80
    scene.collection.objects.link(close_camera)
    original_focus = Vector((0.0, 0.0, 0.98))
    for frame, side in REVIEW_FRAMES:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        hand_world = attacker.matrix_world @ attacker.pose.bones[f"DEF-hand.{side}"].matrix
        close_camera.location = original_camera.location + (hand_world.translation - original_focus)
        close_camera.keyframe_insert(data_path="location", frame=frame)
    scene.frame_set(0)
    scene.camera = original_camera
    saved = output / "finger-flexion-pose.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(saved), check_existing=False, compress=True)
    renders = {}
    for frame, _side in REVIEW_FRAMES:
        renders[str(frame)] = {
            "phone": _render(bpy, output / f"phone-{frame:02d}.png", original_camera, frame),
            "close": _render(bpy, output / f"close-{frame:02d}.png", close_camera, frame),
        }
    scene.camera = original_camera
    result = {
        "schema": "mm_finger_flexion_optin.v1", "status": "review_only_finger_flexion",
        "source_scene": {"path": str(source_scene), "sha256": source_hash},
        "source_scene_sha256_after": sha256(source_scene),
        "implementation_sha256": sha256(Path(__file__)),
        "blender": bpy.app.version_string, "embedded_scripts": "disabled",
        "resolution_px": list(RENDER_SIZE), "review_frames": [10, 24],
        "before": before, "after": after, "checks": checks,
        "scene": {"path": saved.name, "sha256": sha256(saved), "bytes": saved.stat().st_size},
        "renders": renders,
        "claim_limits": ["palmward_finger_flexion_only", "no_closed_fist_silhouette",
                         "no_wrist_alignment", "no_contact_gate", "no_glove_art",
                         "no_fight_physics"],
    }
    (output / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                          encoding="utf-8")
    return result


def reopen_review(bpy, source_scene: Path, saved: Path, receipt_path: Path) -> dict:
    _require_blender(bpy)
    source_scene = Path(source_scene).resolve(strict=True)
    saved = Path(saved).resolve(strict=True)
    receipt_path = Path(receipt_path).resolve(strict=True)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["schema"] != "mm_finger_flexion_optin.v1":
        raise RuntimeError("review receipt schema differs")
    if receipt["source_scene"]["sha256"] != sha256(source_scene):
        raise RuntimeError("source scene digest differs")
    if receipt["implementation_sha256"] != sha256(Path(__file__)):
        raise RuntimeError("hand-pose implementation digest differs")
    if receipt["scene"]["sha256"] != sha256(saved):
        raise RuntimeError("saved review scene digest differs")
    for frame, views in receipt["renders"].items():
        for view in ("phone", "close"):
            image = saved.parent / views[view]["path"]
            if image.stat().st_size != views[view]["bytes"] or sha256(image) != views[view]["sha256"]:
                raise RuntimeError(f"render digest differs: {frame} {view}")
    bpy.ops.wm.open_mainfile(filepath=str(saved), load_ui=False)
    if (bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y) != RENDER_SIZE:
        raise RuntimeError("reopened review camera resolution differs")
    attacker = bpy.data.objects["attacker__Human.rigify"]
    observed = {f"{frame}_{side}": measure_finger_flexion(bpy, attacker, side, frame)
                for frame, side in REVIEW_FRAMES}
    if observed != receipt["after"]:
        raise RuntimeError("reopened evaluated hand pose differs")
    if not all(all(pose_checks(row).values()) for row in observed.values()):
        raise RuntimeError("reopened hand pose fails its measurements")
    return {"status": "reopened_and_measured", "checked_frames": [10, 24],
            "scene_and_renders_verified": True, "source_unchanged":
            sha256(source_scene) == receipt["source_scene"]["sha256"]}


if __name__ == "__main__":
    import bpy

    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) == 3 and args[0] == "build":
        record = build_review(bpy, Path(args[1]), Path(args[2]))
        print("HAND_POSE_BUILD=" + json.dumps({
            "status": record["status"], "checks": record["checks"],
            "receipt": str(Path(args[2]).resolve() / "receipt.json")}, sort_keys=True))
    elif len(args) == 4 and args[0] == "reopen":
        result = reopen_review(bpy, Path(args[1]), Path(args[2]), Path(args[3]))
        print("HAND_POSE_REOPEN=" + json.dumps(result, sort_keys=True))
    else:
        raise ValueError("expected build <source-scene> <new-output> or "
                         "reopen <source-scene> <saved-scene> <receipt>")
