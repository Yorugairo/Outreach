"""Read-only landmark probe for the pinned hand/contact baseline scene.

Run in Blender with --disable-autoexec. This measures a skeletal centerline,
not physiological carpal joint angles or evaluated skin/glove contact.
"""

import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def xyz(point):
    return [round(float(value), 6) for value in point]


def landmarks(rig, bones, side, *, rest):
    def point(name, end):
        bone = bones[name]
        position = getattr(bone, f"{end}_local") if rest else getattr(bone, end)
        return rig.matrix_world @ position

    hand_name = f"DEF-hand.{side}"
    forearm_name = bones[hand_name].parent.name
    elbow = point(forearm_name, "head")
    wrist = point(hand_name, "head")
    mcps = [point(f"DEF-f_{finger}.01.{side}", "head")
            for finger in ("index", "middle", "ring", "pinky")]
    mean_mcp = sum(mcps, Vector()) / len(mcps)
    forearm = wrist - elbow
    hand = mean_mcp - wrist
    return {
        "forearm_bone": forearm_name,
        "elbow_world_m": xyz(elbow),
        "wrist_world_m": xyz(wrist),
        "mean_mcp_world_m": xyz(mean_mcp),
        "centerline_angle_deg": round(math.degrees(forearm.angle(hand)), 4),
        "forearm_length_m": round(float(forearm.length), 6),
        "wrist_to_mcp_length_m": round(float(hand.length), 6),
    }


args = sys.argv[sys.argv.index("--") + 1:]
if len(args) != 1 or "--disable-autoexec" not in sys.argv:
    raise ValueError("run with --disable-autoexec -- <saved-scene.blend>")
source = Path(args[0]).resolve(strict=True)
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
scene = bpy.context.scene
rig = bpy.data.objects["attacker__Human.rigify"]
result = {
    "schema": "hand_wrist_skeletal_baseline.v1",
    "source_scene": str(source),
    "source_scene_sha256": source_hash,
    "blender_version": bpy.app.version_string,
    "units": {"length": "m", "angle": "deg"},
    "meaning": "elbow-to-wrist versus wrist-to-mean-MCP centerline, not carpal flexion",
    "rest": {side: landmarks(rig, rig.data.bones, side, rest=True)
             for side in ("R", "L")},
    "frames": {},
}
for frame in (0, 8, 10, 11, 12, 21, 23, 24, 25, 26, 32):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    result["frames"][str(frame)] = {
        side: landmarks(rig, rig.pose.bones, side, rest=False)
        for side in ("R", "L")
    }
print("HAND_WRIST_BASELINE_JSON=" + json.dumps(result, sort_keys=True))
