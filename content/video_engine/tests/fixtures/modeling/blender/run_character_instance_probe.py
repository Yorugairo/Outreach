"""Blender-backed two-instance rig/skin integrity check; no saved output."""

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[6]
MODULE_PATH = ROOT / "content/video_engine/src/modeling/blender/character_instance.py"
spec = importlib.util.spec_from_file_location("model_character_instance", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
append_character_instance = module.append_character_instance


source = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
expected = "5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade"
assert bpy.app.version_string == "5.2.2 LTS"
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30


def orphaned_character_data():
    return {
        (kind, datablock.name)
        for kind, collection in (
            ("mesh", bpy.data.meshes),
            ("armature", bpy.data.armatures),
            ("action", bpy.data.actions),
        )
        for datablock in collection if datablock.users == 0
    }


baseline_orphans = orphaned_character_data()
render_objects = (
    "Human.rigify", "Human", "Garment_FightShorts",
    "Face_Brow_L", "Face_Brow_R", "Face_Iris_L", "Face_Iris_R",
    "Face_Pupil_L", "Face_Pupil_R", "Hair_CropCap", "Hair_SweptQuiff",
)
instances = {}
for binding_id, x, heading in (("attacker", 0.85, -math.pi / 2),
                               ("receiver", -0.85, math.pi / 2)):
    instances[binding_id] = append_character_instance(
        bpy,
        source=source,
        source_sha256=expected,
        binding_id=binding_id,
        rig_name="Human.rigify",
        object_names=render_objects,
        position_m=(x, 0.0, 0.0),
        heading_rad=heading,
    )
assert not (orphaned_character_data() - baseline_orphans), orphaned_character_data()
scene.frame_set(1)

def evaluated_bounds(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    assert mesh is not None
    try:
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        return [[round(min(point[axis] for point in points), 7),
                 round(max(point[axis] for point in points), 7)] for axis in range(3)]
    finally:
        evaluated.to_mesh_clear()


def bone_tail(rig, name):
    return tuple(float(v) for v in rig.matrix_world @ rig.pose.bones[name].tail)


rows = {}
for binding_id, objects in instances.items():
    rig = objects["Human.rigify"]
    body = objects["Human"]
    shorts = objects["Garment_FightShorts"]
    pupil = objects["Face_Pupil_L"]
    assert body.parent is shorts.parent is rig
    assert len(rig.pose.bones) == 930
    assert rig.animation_data and rig.animation_data.action
    assert all(mod.object is rig for obj in (body, shorts)
               for mod in obj.modifiers if mod.type == "ARMATURE")
    body_bounds = evaluated_bounds(body)
    shorts_bounds = evaluated_bounds(shorts)
    assert abs(sum(body_bounds[0]) / 2 - sum(shorts_bounds[0]) / 2) < 0.2
    pupil_world = sum((pupil.matrix_world @ vertex.co for vertex in pupil.data.vertices),
                      Vector()) / len(pupil.data.vertices)
    head_world = rig.matrix_world @ rig.pose.bones["head"].head
    face_axis_world = pupil_world - head_world
    rows[binding_id] = {
        "rig": rig.name,
        "action": rig.animation_data.action.name,
        "objects": sorted(obj.name for obj in objects.values()),
        "root_x_m": round(float(rig.matrix_world.translation.x), 7),
        "face_axis_world_m": [round(float(v), 7) for v in face_axis_world],
        "body_bounds_m": body_bounds,
        "shorts_bounds_m": shorts_bounds,
        "head_world_m": [round(float(v), 7) for v in head_world],
        "right_arm_tail_world_m": [round(v, 7) for v in bone_tail(rig, "DEF-upper_arm.R")],
    }
assert rows["receiver"]["body_bounds_m"][0][1] < rows["attacker"]["body_bounds_m"][0][0]
assert rows["attacker"]["root_x_m"] == 0.85
assert rows["receiver"]["root_x_m"] == -0.85
assert rows["attacker"]["face_axis_world_m"][0] < -0.08
assert rows["receiver"]["face_axis_world_m"][0] > 0.08
for name in render_objects:
    assert instances["attacker"][name].data is not instances["receiver"][name].data
assert instances["attacker"]["Human.rigify"].animation_data.action is not instances["receiver"]["Human.rigify"].animation_data.action

attacker = instances["attacker"]["Human.rigify"]
receiver = instances["receiver"]["Human.rigify"]
attacker_before = bone_tail(attacker, "DEF-upper_arm.R")
receiver_before = bone_tail(receiver, "DEF-upper_arm.R")
arm = attacker.pose.bones["upper_arm_fk.R"]
assert float(attacker.pose.bones["upper_arm_parent.R"]["IK_FK"]) == 1.0
arm.rotation_mode = "XYZ"
arm.rotation_euler.z += 0.25
bpy.context.view_layer.update()
attacker_movement = math.dist(attacker_before, bone_tail(attacker, "DEF-upper_arm.R"))
receiver_movement = math.dist(receiver_before, bone_tail(receiver, "DEF-upper_arm.R"))
assert attacker_movement > 0.015, attacker_movement
assert receiver_movement < 0.000001, receiver_movement
assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
print("INSTANCE_JSON=" + json.dumps({
    "schema": "model_character_instance_probe.v1",
    "status": "diagnostic_only",
    "blender": bpy.app.version_string,
    "source_sha256_before_after": expected,
    "scene_fps": scene.render.fps,
    "attacker_arm_movement_m": round(attacker_movement, 7),
    "receiver_arm_movement_m": round(receiver_movement, 7),
    "instances": rows,
}, sort_keys=True))
