"""Source-clock, review-only first exchange on two native generic Rigify rigs.

This module runs inside pinned Blender. It authors a separate editable scene,
measures evaluated mesh surfaces, and never opens or saves the source blend.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import stat
import struct
from pathlib import Path
import sys
from typing import Any


SCHEMA = "model_fight_motion.v1"
SOURCE_SHA256 = "5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade"
FIXTURE_SHA256 = "d7d37878a692e3359cbeb4d3409620c840150c9152d5c344c90815aacf1db971"
CODE_ROOT = Path(__file__).resolve().parents[5]
REVIEW_RELATIVE = Path("content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange")
FIXTURE_RELATIVE = Path("content/video_engine/tests/fixtures/modeling/blender/characters/source-exchange/exchange.v1.json")
FRAMES = tuple(range(36))
RENDER_SIZE = (540, 960)
RENDER_FRAMES = (0, 8, 10, 12, 23, 24, 25, 26, 32)
OBJECT_NAMES = (
    "Human.rigify", "Human", "Garment_FightShorts", "Face_Brow_L",
    "Face_Brow_R", "Face_Iris_L", "Face_Iris_R", "Face_Pupil_L",
    "Face_Pupil_R", "Hair_CropCap", "Hair_SweptQuiff",
)


class FightMotionError(RuntimeError):
    """The bounded proof cannot be authored or measured faithfully."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_fixture(root: Path, fixture_path: Path) -> dict[str, Any]:
    """Check the complete fixed input set before a Blender scene is touched."""
    root = root.resolve()
    if fixture_path.is_symlink():
        raise FightMotionError("exchange fixture must not be redirected")
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    if (fixture.get("schema") != "model_source_exchange.v1"
            or fixture.get("status") != "review_only"
            or fixture.get("fps") != 30 or fixture.get("frame_end") != 35
            or tuple(fixture.get("render_frames", ())) != RENDER_FRAMES):
        raise FightMotionError("source exchange fixture/clock/render contract changed")
    for name in ("source_video", "source_clock", "source_blend"):
        entry = fixture[name]
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise FightMotionError(f"unsafe {name} path")
        unresolved = root / relative
        path = unresolved.resolve()
        if (unresolved.is_symlink() or not path.is_relative_to(root)
                or not path.is_file()):
            raise FightMotionError(f"missing or redirected {name}")
        if sha256(path) != entry["sha256"]:
            raise FightMotionError(f"stale {name} hash")
    if fixture["source_blend"]["sha256"] != SOURCE_SHA256:
        raise FightMotionError("generic source blend is not the pinned v1.1 scene")
    clock = json.loads((root / fixture["source_clock"]["path"]).read_text(encoding="utf-8"))
    if (clock["provenance"]["sha256"] != fixture["source_video"]["sha256"]
            or clock["scene"]["fps"] != {"numerator": 30, "denominator": 1}
            or [(item["event_id"], item["frame"]) for item in clock["scene"]["events"]]
            != [("left-hook-contact", 24), ("head-snap", 25)]):
        raise FightMotionError("source clock no longer matches observed contact/snap")
    keys = fixture["keyframes"]
    if [item["frame"] for item in keys] != sorted({item["frame"] for item in keys}):
        raise FightMotionError("exchange keys must be unique and ordered")
    if keys[0]["frame"] != 0 or keys[-1]["frame"] != 35:
        raise FightMotionError("exchange keys do not cover the diagnostic")
    if sha256(fixture_path) != FIXTURE_SHA256:
        raise FightMotionError("source exchange fixture SHA-256 differs from the pinned document")
    return fixture


def _reject_redirected_output_chain(path: Path) -> None:
    """Reject symlinks and Windows reparse-point redirects in the whole path."""
    current = path
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    while True:
        try:
            info = current.lstat()
        except FileNotFoundError:
            info = None
        except OSError as exc:
            raise FightMotionError(f"cannot inspect exchange output path: {current}") from exc
        if info is not None:
            attributes = getattr(info, "st_file_attributes", 0)
            if stat.S_ISLNK(info.st_mode) or attributes & reparse_point:
                raise FightMotionError("exchange output path contains symlink/junction redirection")
        parent = current.parent
        if parent == current:
            break
        current = parent


def validate_output_target(root: Path, output: Path) -> Path:
    """Resolve a new direct child of the approved quarantine without creating it."""
    root = Path(root).resolve()
    output = Path(output)
    if ".." in output.parts:
        raise FightMotionError("unsafe exchange output path")
    candidate = output if output.is_absolute() else root / output
    candidate = candidate.absolute()

    approved_root = root / REVIEW_RELATIVE
    _reject_redirected_output_chain(approved_root)
    if not approved_root.is_dir():
        raise FightMotionError("approved exchange review quarantine is missing")
    approved_root = approved_root.resolve(strict=True)

    _reject_redirected_output_chain(candidate)
    target = candidate.resolve(strict=False)
    if target == approved_root or target.parent != approved_root:
        raise FightMotionError("exchange output must be a direct child of the approved review quarantine")
    if target.exists():
        if not target.is_dir() or any(target.iterdir()):
            raise FightMotionError("exchange output target must be a new or empty directory")
    return target


def _instance_function(root: Path):
    path = root / "content/video_engine/src/modeling/blender/character_instance.py"
    spec = importlib.util.spec_from_file_location("model_character_instance", path)
    if spec is None or spec.loader is None:
        raise FightMotionError("cannot load self-contained native instancer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.append_character_instance


def _world(rig, bone_name: str):
    return rig.matrix_world @ rig.pose.bones[bone_name].matrix


def _vec(vector):
    return [round(float(value), 7) for value in vector]


def _set_world_bone(rig, name: str, world_matrix, frame: int):
    bone = rig.pose.bones[name]
    bone.matrix = rig.matrix_world.inverted() @ world_matrix
    bone.keyframe_insert(data_path="location", frame=frame, group=name)
    if bone.rotation_mode == "QUATERNION":
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame, group=name)
    else:
        bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=name)


def _material(bpy, name: str, rgba):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = 0.82
    return mat


def _stage(bpy, instances):
    from mathutils import Vector

    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end = 35
    scene.render.fps = 30
    scene.render.fps_base = 1.0
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = RENDER_SIZE
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.render.image_settings.color_depth = "8"
    scene.world = bpy.data.worlds.new("ExchangeWorld")
    scene.world.color = (0.12, 0.13, 0.16)

    # Only diagnostic geography and neutral presentation: no injury effects.
    for binding, rgba in (("attacker", (0.84, 0.81, 0.69, 1)),
                          ("receiver", (0.12, 0.16, 0.22, 1))):
        shorts = instances[binding]["Garment_FightShorts"]
        shorts.data.materials.clear()
        shorts.data.materials.append(_material(bpy, binding + "_shorts", rgba))
        instances[binding]["Hair_SweptQuiff"].hide_render = True
        if binding == "attacker":
            instances[binding]["Hair_CropCap"].hide_render = True

    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.003))
    floor = bpy.context.object
    floor.name = "Exchange_Floor"
    floor.data.materials.append(_material(bpy, "matte_floor", (0.23, 0.25, 0.28, 1)))
    cam_data = bpy.data.cameras.new("PhoneCameraData")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 3.0
    camera = bpy.data.objects.new("PhoneCamera", cam_data)
    scene.collection.objects.link(camera)
    target = Vector((0, 0, 0.98))
    camera.location = Vector((0.35, -5.5, 2.20))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    for name, location, power, size in (
        ("Key", (1.0, -2.4, 4.2), 780, 4.0),
        ("Fill", (-2.0, -0.8, 3.2), 420, 3.0),
    ):
        light_data = bpy.data.lights.new(name, type="AREA")
        light_data.energy = power
        light_data.shape = "DISK"
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        scene.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    return camera


def _hand_target(label: str, rig, receiver, side: str):
    from mathutils import Vector

    if label == "guard":
        # A held guard stays near the actor's own cheek, not the source rest pose.
        own = _world(rig, "head").translation
        facing = -1 if rig.rotation_euler.z < 0 else 1
        return own + Vector((facing * 0.18,
                             0.14 if side == "R" else -0.14, -0.15))
    head = _world(receiver, "head").translation
    offsets = {
        "right_approach": (0.43, 0.17, -0.04),
        "right_touch": (0.13, 0.08, -0.02),
        "right_follow": (0.04, 0.06, -0.02),
        "left_windup": (0.54, -0.36, -0.10),
        "left_approach": (0.34, -0.28, -0.03),
        "left_near": (0.24, -0.20, 0.00),
        "left_touch": (0.13, -0.04, 0.02),
        "left_follow": (0.06, 0.02, 0.04),
        "left_follow_far": (-0.02, 0.16, 0.05),
    }
    if label not in offsets:
        raise FightMotionError(f"unknown hand pose: {label}")
    return head + Vector(offsets[label])


def _key_exchange(bpy, fixture, instances):
    from mathutils import Matrix

    scene = bpy.context.scene
    scene.frame_set(0)
    bpy.context.view_layer.update()
    # The starter action contains synthetic f27/f50 arm/leg motion and a
    # frame-1 FK switch. Those keys must not leak into the observed source run.
    for binding, objects in instances.items():
        rig = objects["Human.rigify"]
        old_action = rig.animation_data.action
        rig.animation_data.action = bpy.data.actions.new(
            f"{binding}__source_exchange_action")
        if old_action.users == 0:
            bpy.data.actions.remove(old_action)
        rig.pose.bones["upper_arm_fk.R"].rotation_euler = (0, 0, 0)
        rig.pose.bones["thigh_fk.L"].rotation_euler = (0, 0, 0)
    home_feet = {}
    wrist_rot = {}
    for binding, objects in instances.items():
        rig = objects["Human.rigify"]
        home_feet[binding] = {}
        for side in ("L", "R"):
            planted = _world(rig, f"foot_ik.{side}").copy()
            stagger = (-0.38 if side == "L" else 0.18) * (1 if binding == "attacker" else -1)
            planted.translation.x += stagger
            home_feet[binding][side] = planted
        wrist_rot[binding] = {side: _world(rig, f"hand_ik.{side}").to_quaternion().to_matrix().to_4x4()
                              for side in ("L", "R")}

    # These are authored pose angles, not inferred force or anatomy constants.
    yaw = {0: 0, 6: 0.03, 9: 0.10, 10: 0.15, 11: 0.18, 12: 0.17,
           15: 0.02, 18: -0.16, 21: -0.30, 23: -0.41, 24: -0.48,
           25: -0.50, 26: -0.52, 28: -0.44, 32: -0.08, 35: 0}
    hip_twist = {0: 0, 6: 0.02, 9: 0.06, 10: 0.10, 11: 0.12, 12: 0.10,
                 15: 0.01, 18: -0.08, 21: -0.16, 23: -0.22, 24: -0.27,
                 25: -0.29, 26: -0.30, 28: -0.26, 32: -0.03, 35: 0}

    for key in fixture["keyframes"]:
        frame = key["frame"]
        scene.frame_set(frame)
        for binding in ("attacker", "receiver"):
            rig = instances[binding]["Human.rigify"]
            rig.location.x = key["attacker_x" if binding == "attacker" else "receiver_x"]
            rig.keyframe_insert(data_path="location", frame=frame)
            if binding == "attacker":
                rig.rotation_euler.z = -math.pi / 2 + yaw[frame]
                rig.keyframe_insert(data_path="rotation_euler", frame=frame)
            for side in ("L", "R"):
                leg = rig.pose.bones[f"thigh_parent.{side}"]
                leg["IK_FK"] = 0.0
                leg.keyframe_insert(data_path='["IK_FK"]', frame=frame)
                arm = rig.pose.bones[f"upper_arm_parent.{side}"]
                arm["IK_FK"] = 0.0
                arm.keyframe_insert(data_path='["IK_FK"]', frame=frame)
        bpy.context.view_layer.update()
        for binding in ("attacker", "receiver"):
            rig = instances[binding]["Human.rigify"]
            for side in ("L", "R"):
                _set_world_bone(rig, f"foot_ik.{side}", home_feet[binding][side], frame)
        bpy.context.view_layer.update()
        attacker = instances["attacker"]["Human.rigify"]
        receiver = instances["receiver"]["Human.rigify"]
        hips = attacker.pose.bones["hips"]
        hips.rotation_mode = "XYZ"
        hips.rotation_euler.z = hip_twist[frame]
        hips.keyframe_insert(data_path="rotation_euler", frame=frame)
        chest = attacker.pose.bones["chest"]
        chest.rotation_mode = "XYZ"
        chest.rotation_euler.z = hip_twist[frame] * 0.55
        chest.keyframe_insert(data_path="rotation_euler", frame=frame)
        torso = attacker.pose.bones["torso"]
        torso.rotation_mode = "XYZ"
        torso.rotation_euler.y = key["attacker_torso_y"]
        torso.keyframe_insert(data_path="rotation_euler", frame=frame)
        head = receiver.pose.bones["head"]
        head.rotation_mode = "XYZ"
        head.rotation_euler.x = -key["receiver_head_y"] * 0.8
        head.rotation_euler.y = key["receiver_head_y"] * 0.3
        head.keyframe_insert(data_path="rotation_euler", frame=frame)
        neck = receiver.pose.bones["neck"]
        neck.rotation_mode = "XYZ"
        neck.rotation_euler.x = -key["receiver_head_y"] * 1.1
        neck.rotation_euler.y = key["receiver_head_y"] * 0.25
        neck.keyframe_insert(data_path="rotation_euler", frame=frame)
        bpy.context.view_layer.update()
        for side, label in (("R", key["right"]), ("L", key["left"])):
            target = _hand_target(label, attacker, receiver, side)
            rotation = Matrix.Rotation(0.8, 4, "Y") if label == "guard" else Matrix.Identity(4)
            world_matrix = Matrix.Translation(target) @ rotation @ wrist_rot["attacker"][side]
            _set_world_bone(attacker, f"hand_ik.{side}", world_matrix, frame)
        # Receiver keeps its guard; the incoming contact drives its head later.
        for side in ("R", "L"):
            target = _hand_target("guard", receiver, attacker, side)
            _set_world_bone(receiver, f"hand_ik.{side}",
                            Matrix.Translation(target) @ Matrix.Rotation(0.8, 4, "Y")
                            @ wrist_rot["receiver"][side], frame)
        bpy.context.view_layer.update()

    for binding in ("attacker", "receiver"):
        rig = instances[binding]["Human.rigify"]
        action = rig.animation_data.action if rig.animation_data else None
        if action is None or action is instances["receiver" if binding == "attacker" else "attacker"]["Human.rigify"].animation_data.action:
            raise FightMotionError("fighter actions are missing or shared")
        action.name = f"{binding}__source_exchange_action"
    scene.frame_set(0)
    _key_fists(bpy, instances)


def _key_fists(bpy, instances):
    """Curl actual finger controls so contact uses a compact glove-free fist."""
    assignments = {
        "f_index": (("01", 2, 0.55), ("02", 2, 0.85), ("03", 2, 0.55)),
        "f_middle": (("01", 0, 0.50), ("02", 0, 0.90), ("03", 0, 0.55)),
        "f_ring": (("01", 2, -0.55), ("02", 2, -0.85), ("03", 2, -0.55)),
        "f_pinky": (("01", 2, -0.55), ("02", 2, -0.85), ("03", 2, -0.55)),
        "thumb": (("01_master", 0, 0.55), ("02", 0, 0.65)),
    }
    for objects in instances.values():
        rig = objects["Human.rigify"]
        for side in ("L", "R"):
            sign = 1 if side == "R" else -1
            for finger, controls in assignments.items():
                for segment, axis, angle in controls:
                    bone = rig.pose.bones[f"{finger}.{segment}.{side}"]
                    bone.rotation_mode = "XYZ"
                    bone.rotation_euler[axis] = angle * (sign if axis == 2 else 1)
                    bone.keyframe_insert(data_path="rotation_euler", frame=0)
    bpy.context.view_layer.update()


def _skin_indices(bpy, body, group: str, minimum=0.55):
    vertex_group = body.vertex_groups.get(group)
    if vertex_group is None:
        raise FightMotionError(f"missing anatomical skin group {group}")
    group_index = vertex_group.index
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise FightMotionError("evaluated skin mesh unavailable")
    try:
        found = [vertex.index for vertex in mesh.vertices
                 if any(item.group == group_index and item.weight >= minimum
                        for item in vertex.groups)]
    finally:
        evaluated.to_mesh_clear()
    if len(found) < 12:
        raise FightMotionError(f"too few skin vertices for {group}: {len(found)}")
    return tuple(found)


def _head_indices(bpy, rig, body):
    # This MPFB/Rigify body has no DEF-head skin group. Select a stable
    # anatomical surface region from its neutral evaluated geometry instead.
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise FightMotionError("neutral evaluated head surface unavailable")
    try:
        head = _world(rig, "head").translation
        world = evaluated.matrix_world.copy()
        found = tuple(vertex.index for vertex in mesh.vertices
                      if (world @ vertex.co - head).length <= 0.28
                      and (world @ vertex.co).z >= head.z - 0.13)
    finally:
        evaluated.to_mesh_clear()
    if len(found) < 50:
        raise FightMotionError(f"neutral head surface has only {len(found)} vertices")
    return found


def _sole_indices(bpy, rig, body, side: str):
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    own = {body.vertex_groups[name].index
           for name in (f"DEF-foot.{side}", f"DEF-toe.{side}")}
    other = "R" if side == "L" else "L"
    opposite = {body.vertex_groups[name].index
                for name in (f"DEF-foot.{other}", f"DEF-toe.{other}")}
    foot = _world(rig, f"foot_ik.{side}").translation
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise FightMotionError("neutral evaluated sole unavailable")
    try:
        world = evaluated.matrix_world.copy()
        found = []
        for vertex in mesh.vertices:
            point = world @ vertex.co
            left_weight = sum(group.weight for group in vertex.groups if group.group in own)
            other_weight = sum(group.weight for group in vertex.groups if group.group in opposite)
            if (left_weight >= 0.20 and other_weight <= 0.05
                    and abs(point.x - foot.x) <= 0.16
                    and abs(point.y - foot.y) <= 0.30
                    and -0.005 <= point.z <= 0.010):
                found.append(vertex.index)
    finally:
        evaluated.to_mesh_clear()
    if len(found) < 16:
        raise FightMotionError(f"{side} sole band has only {len(found)} vertices")
    return tuple(found)


def _evaluated_points(body, indices, depsgraph):
    evaluated = body.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None or max(indices) >= len(mesh.vertices):
        raise FightMotionError(
            f"evaluated body mesh/topology is unavailable: "
            f"vertices={len(mesh.vertices) if mesh is not None else None}, "
            f"max_index={max(indices)}"
        )
    try:
        world = evaluated.matrix_world.copy()
        return [tuple(float(v) for v in world @ mesh.vertices[index].co)
                for index in indices]
    finally:
        evaluated.to_mesh_clear()


def _nearest(a, b):
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    tree = KDTree(len(b))
    for index, point in enumerate(b):
        tree.insert(Vector(point), index)
    tree.balance()
    return min(float(tree.find(Vector(point))[2]) for point in a)


def measure_frame(bpy, instances, indices, frame: int):
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result = {"frame": frame, "fighters": {}}
    points = {}
    for binding in ("attacker", "receiver"):
        objects = instances[binding]
        rig = objects["Human.rigify"]
        body = objects["Human"]
        points[binding] = {name: _evaluated_points(body, group_indices, depsgraph)
                           for name, group_indices in indices[binding].items()}
        left = points[binding]["foot_L"]
        right = points[binding]["foot_R"]
        result["fighters"][binding] = {
            "root_world_m": _vec(rig.matrix_world.translation),
            "head_world_m": _vec(_world(rig, "head").translation),
            "head_surface_centroid_world_m": _vec(tuple(
                sum(point[axis] for point in points[binding]["head"])
                / len(points[binding]["head"]) for axis in range(3))),
            "torso_world_m": _vec(_world(rig, "torso").translation),
            "hand_ik_R_world_m": _vec(_world(rig, "hand_ik.R").translation),
            "hand_ik_L_world_m": _vec(_world(rig, "hand_ik.L").translation),
            "hand_def_R_world_m": _vec(_world(rig, "DEF-hand.R").translation),
            "hand_def_L_world_m": _vec(_world(rig, "DEF-hand.L").translation),
            "foot_ik_L_world_m": _vec(_world(rig, "foot_ik.L").translation),
            "foot_ik_R_world_m": _vec(_world(rig, "foot_ik.R").translation),
            "sole_L_centroid_xy_m": _vec((sum(v[0] for v in left) / len(left),
                                            sum(v[1] for v in left) / len(left))),
            "sole_R_centroid_xy_m": _vec((sum(v[0] for v in right) / len(right),
                                            sum(v[1] for v in right) / len(right))),
            "sole_L_min_z_m": round(min(v[2] for v in left), 7),
            "sole_R_min_z_m": round(min(v[2] for v in right), 7),
            "arm_ik_fk_R": float(rig.pose.bones["upper_arm_parent.R"]["IK_FK"]),
            "arm_ik_fk_L": float(rig.pose.bones["upper_arm_parent.L"]["IK_FK"]),
            "leg_ik_fk_L": float(rig.pose.bones["thigh_parent.L"]["IK_FK"]),
            "leg_ik_fk_R": float(rig.pose.bones["thigh_parent.R"]["IK_FK"]),
        }
    head_points = points["receiver"]["head"]
    for side in ("R", "L"):
        hand = points["attacker"][f"hand_{side}"]
        result[f"{side.lower()}_hand_head_min_distance_m"] = round(_nearest(hand, head_points), 7)
        result[f"{side.lower()}_hand_head_axial_gap_m"] = round(
            min(v[0] for v in hand) - max(v[0] for v in head_points), 7)
    return result


def _measure(bpy, instances):
    groups = {"hand_R": "DEF-hand.R", "hand_L": "DEF-hand.L"}
    indices = {binding: {name: _skin_indices(bpy, objects["Human"], group)
                         for name, group in groups.items()}
               for binding, objects in instances.items()}
    for binding, objects in instances.items():
        indices[binding]["head"] = _head_indices(
            bpy, objects["Human.rigify"], objects["Human"])
        for side in ("L", "R"):
            indices[binding][f"foot_{side}"] = _sole_indices(
                bpy, objects["Human.rigify"], objects["Human"], side)
    rows = [measure_frame(bpy, instances, indices, frame) for frame in FRAMES]
    return rows, {binding: {key: len(value) for key, value in groupset.items()}
                  for binding, groupset in indices.items()}


def _summary(rows, budgets):
    by_frame = {row["frame"]: row for row in rows}
    head = lambda f: by_frame[f]["fighters"]["receiver"]["head_surface_centroid_world_m"]
    base = head(0)
    before_first = max(math.dist(head(f), base) for f in range(10))
    before_hook = max(math.dist(head(f), head(18)) for f in range(18, 25))
    after_first = math.dist(head(12), head(11))
    after_hook = math.dist(head(25), head(24))
    foot_slip = {}
    support_margin = {}
    floor_min = 1.0
    for binding in ("attacker", "receiver"):
        for side in ("L", "R"):
            label = f"{binding}_{side}"
            positions = [row["fighters"][binding][f"sole_{side}_centroid_xy_m"]
                         for row in rows]
            foot_slip[label] = round(max(math.dist(point, positions[0]) for point in positions), 7)
            floor_min = min(floor_min, *(row["fighters"][binding][f"sole_{side}_min_z_m"]
                                          for row in rows))
        margins = []
        for row in rows:
            fighter = row["fighters"][binding]
            low, high = sorted((fighter["sole_L_centroid_xy_m"][0],
                                fighter["sole_R_centroid_xy_m"][0]))
            root_x = fighter["root_world_m"][0]
            margins.append(min(root_x - low, high - root_x))
        support_margin[binding] = round(min(margins), 7)
    contact = {
        "right_f10": by_frame[10]["r_hand_head_min_distance_m"],
        "right_f11": by_frame[11]["r_hand_head_min_distance_m"],
        "left_f24": by_frame[24]["l_hand_head_min_distance_m"],
    }
    axial = {
        "right_f10": by_frame[10]["r_hand_head_axial_gap_m"],
        "right_f11": by_frame[11]["r_hand_head_axial_gap_m"],
        "left_f24": by_frame[24]["l_hand_head_axial_gap_m"],
    }
    checks = {
        "no_first_precontact_head_snap": before_first <= budgets["precontact_head_motion"],
        "no_pre_hook_head_snap": before_hook <= budgets["precontact_head_motion"],
        "first_head_response_after_contact": after_first > budgets["precontact_head_motion"],
        "left_head_response_at_f25": after_hook > budgets["precontact_head_motion"],
        "visible_left_head_response": after_hook >= budgets["post_hook_head_response_min"],
        "contact_surface_gap": all(value <= budgets["contact_surface_gap"] for value in contact.values()),
        "contact_axial_penetration": all(value >= -budgets["contact_penetration"] for value in axial.values()),
        "sole_xy_slip": all(value <= budgets["planted_sole_slip_xy"] for value in foot_slip.values()),
        "floor_clearance": floor_min >= -budgets["floor_penetration"],
        "root_projection_in_support_x": all(value >= -budgets["root_support_margin"]
                                            for value in support_margin.values()),
        "right_follow_through": by_frame[12]["r_hand_head_axial_gap_m"] < by_frame[11]["r_hand_head_axial_gap_m"],
        "left_follow_through": by_frame[26]["l_hand_head_axial_gap_m"] < by_frame[24]["l_hand_head_axial_gap_m"],
    }
    return {
        "head_motion_m": {"before_first_max": round(before_first, 7),
                          "before_hook_max": round(before_hook, 7),
                          "f11_to_f12": round(after_first, 7),
                          "f24_to_f25": round(after_hook, 7)},
        "contact_min_surface_distance_m": contact,
        "contact_axial_gap_m": axial,
        "foot_max_centroid_slip_xy_m": foot_slip,
        "root_projection_support_x_min_margin_m": support_margin,
        "lowest_sole_z_m": round(floor_min, 7),
        "checks": checks,
    }


def _exposure_map():
    # Half-open output intervals [n*30/24, (n+1)*30/24).
    from fractions import Fraction

    return {
        name: {"source_frame": frame,
               "output_frame_24fps": int(Fraction(frame * 24, 30)),
               "source_exposure_start": str(Fraction(int(Fraction(frame * 24, 30)) * 30, 24)),
               "source_exposure_end": str(Fraction((int(Fraction(frame * 24, 30)) + 1) * 30, 24))}
        for name, frame in (("right_contact_observed_window_start", 10),
                            ("right_contact_observed_window_end", 11),
                            ("left_hook_contact", 24), ("head_snap", 25))
    }


def _pinned_fixture() -> dict[str, Any]:
    """Load only the already-pinned fixture fields needed to verify a receipt."""
    root = Path(__file__).resolve().parents[5]
    path = root / FIXTURE_RELATIVE
    if path.is_symlink() or not path.is_file() or sha256(path) != FIXTURE_SHA256:
        raise FightMotionError("pinned source exchange fixture is missing or changed")
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_receipt_renders(receipt: dict[str, Any], receipt_path: Path) -> str:
    """Verify listed review PNGs in-place; an empty list means no render claim."""
    renders = receipt.get("renders")
    if not isinstance(renders, dict):
        raise FightMotionError("receipt renders mapping is missing or malformed")
    if not renders:
        return "not_listed"
    expected_frames = tuple(str(frame) for frame in RENDER_FRAMES)
    if set(renders) != set(expected_frames):
        raise FightMotionError("receipt render frame mapping differs from the pinned render set")

    directory = Path(receipt_path).parent.resolve(strict=True)
    for frame in RENDER_FRAMES:
        basename = f"frame-{frame:02d}.png"
        entry = renders[str(frame)]
        if not isinstance(entry, dict) or entry.get("path") != basename:
            raise FightMotionError(f"receipt render {frame} has an unsafe or unexpected path")
        path = directory / basename
        if path.is_symlink() or not path.is_file():
            raise FightMotionError(f"receipt render {frame} is missing or redirected")
        resolved = path.resolve(strict=True)
        if resolved.parent != directory:
            raise FightMotionError(f"receipt render {frame} escapes its receipt directory")
        size = path.stat().st_size
        if isinstance(entry.get("bytes"), bool) or entry.get("bytes") != size:
            raise FightMotionError(f"receipt render {frame} byte count differs")
        if entry.get("sha256") != sha256(path):
            raise FightMotionError(f"receipt render {frame} SHA-256 differs")
        with path.open("rb") as stream:
            header = stream.read(24)
        if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n"
                or header[12:16] != b"IHDR"
                or struct.unpack(">II", header[16:24]) != RENDER_SIZE):
            raise FightMotionError(f"receipt render {frame} is not a 540x960 PNG")
    return "verified"


def _validate_reopened_measurements(
    rows: list[dict[str, Any]], counts: dict[str, Any],
    receipt: dict[str, Any], fixture: dict[str, Any],
) -> None:
    """Require the full scene measurements and declared summary to match."""
    if receipt.get("fixture_sha256") != FIXTURE_SHA256:
        raise FightMotionError("reopened receipt does not reference the pinned fixture")
    if receipt.get("roles") != fixture["roles"]:
        raise FightMotionError("reopened receipt roles differ from the pinned fixture")
    budgets = fixture["budgets_m"]
    if receipt.get("budgets_predeclared_m") != budgets:
        raise FightMotionError("reopened receipt budgets differ from the pinned fixture")
    if receipt.get("exposure_24fps") != _exposure_map():
        raise FightMotionError("reopened receipt exposure mapping differs")
    if receipt.get("mesh_witness_vertex_counts") != counts:
        raise FightMotionError("reopened mesh witness counts differ")

    declared_rows = receipt.get("frames")
    if not isinstance(declared_rows, list) or len(declared_rows) != len(FRAMES):
        raise FightMotionError("reopened receipt does not contain all 36 frame rows")
    for frame, observed in zip(FRAMES, rows):
        if observed.get("frame") != frame or declared_rows[frame] != observed:
            raise FightMotionError(f"saved/reopened scene differs at frame {frame}")

    summary = _summary(rows, budgets)
    if receipt.get("metrics") != summary:
        raise FightMotionError("reopened receipt summary metrics differ")
    checks = summary.get("checks")
    if not isinstance(checks, dict) or not checks or not all(checks.values()):
        raise FightMotionError("reopened scene fails one or more declared motion checks")


def build_exchange(bpy, root: Path, fixture_path: Path, output: Path, *, render: bool):
    fixture = validate_fixture(root, fixture_path)
    if bpy.app.version_string != "5.2.2 LTS":
        raise FightMotionError(f"pinned Blender 5.2.2 LTS required, got {bpy.app.version_string}")
    if "--disable-autoexec" not in sys.argv:
        raise FightMotionError("embedded scripts must be disabled")
    source = root / fixture["source_blend"]["path"]
    append = _instance_function(root)
    output = validate_output_target(root, output)
    output.mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    instances = {}
    for binding, x, heading in (("attacker", 0.58, -math.pi / 2),
                                ("receiver", -0.45, math.pi / 2)):
        instances[binding] = append(
            bpy, source=source, source_sha256=SOURCE_SHA256,
            binding_id=binding, rig_name="Human.rigify", object_names=OBJECT_NAMES,
            position_m=(x, 0.0, 0.0), heading_rad=heading,
        )
    camera = _stage(bpy, instances)
    _key_exchange(bpy, fixture, instances)
    rows, counts = _measure(bpy, instances)
    summary = _summary(rows, fixture["budgets_m"])
    scene = bpy.context.scene
    scene.frame_set(0)
    blend = output / "source-exchange.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=False, compress=True)
    if not blend.is_file():
        raise FightMotionError("Blender did not save the editable exchange scene")
    renders = {}
    if render:
        for frame in RENDER_FRAMES:
            scene.frame_set(frame)
            path = output / f"frame-{frame:02d}.png"
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True)
            if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
                raise FightMotionError(f"missing or invalid frame {frame} render")
            renders[str(frame)] = {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
    result = {
        "schema": SCHEMA,
        "status": "review_only_diagnostic",
        "source": {name: fixture[name] for name in ("source_video", "source_clock", "source_blend")},
        "source_blend_sha256_after": sha256(source),
        "fixture_sha256": sha256(fixture_path),
        "implementation_sha256": sha256(Path(__file__)),
        "blender": bpy.app.version_string,
        "embedded_scripts": "disabled",
        "fps": scene.render.fps,
        "frame_range": [scene.frame_start, scene.frame_end],
        "camera": {"name": camera.name, "orthographic_scale_m": camera.data.ortho_scale,
                   "resolution_px": list(RENDER_SIZE), "matrix_world": [list(map(float, row)) for row in camera.matrix_world]},
        "roles": fixture["roles"],
        "actions": {binding: instances[binding]["Human.rigify"].animation_data.action.name
                    for binding in instances},
        "mesh_witness_vertex_counts": counts,
        "budgets_predeclared_m": fixture["budgets_m"],
        "metrics": summary,
        "exposure_24fps": _exposure_map(),
        "scene": {"path": blend.name, "sha256": sha256(blend), "bytes": blend.stat().st_size},
        "renders": renders,
        "frames": rows,
    }
    (output / "receipt.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def reopen_exchange(bpy, scene_path: Path, receipt_path: Path):
    if bpy.app.version_string != "5.2.2 LTS" or "--disable-autoexec" not in sys.argv:
        raise FightMotionError("pinned scripts-disabled Blender is required to reopen")
    scene_path = Path(scene_path)
    receipt_path = Path(receipt_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    scene_record = receipt.get("scene")
    if (not isinstance(scene_record, dict) or receipt.get("schema") != SCHEMA
            or scene_record.get("path") != scene_path.name
            or scene_path.parent.resolve() != receipt_path.parent.resolve()
            or not scene_path.is_file()
            or sha256(scene_path) != scene_record.get("sha256")
            or scene_path.stat().st_size != scene_record.get("bytes")):
        raise FightMotionError("saved scene hash/receipt mismatch")
    if "FINISHED" not in bpy.ops.wm.open_mainfile(filepath=str(scene_path), load_ui=False, use_scripts=False):
        raise FightMotionError("Blender could not reopen the derived scene")
    scene = bpy.context.scene
    if (scene.render.fps != 30 or scene.render.fps_base != 1.0
            or (scene.frame_start, scene.frame_end) != (0, 35)
            or scene.render.resolution_percentage != 100
            or (scene.render.resolution_x, scene.render.resolution_y) != RENDER_SIZE):
        raise FightMotionError("reopened scene clock differs")
    instances = {
        binding: {name: bpy.data.objects[f"{binding}__{name}"] for name in OBJECT_NAMES}
        for binding in ("attacker", "receiver")
    }
    rigs = []
    actions = []
    for binding, objects in instances.items():
        rig = objects["Human.rigify"]
        if rig.type != "ARMATURE" or rig.get("model_binding_id") != binding:
            raise FightMotionError("reopened fighter rig is not privately bound")
        if not rig.animation_data or not rig.animation_data.action:
            raise FightMotionError("reopened private action is missing")
        action = rig.animation_data.action
        if action.name != receipt["actions"][binding]:
            raise FightMotionError("reopened private action differs")
        rigs.append(rig)
        actions.append(action)
        for name in OBJECT_NAMES:
            if name == "Human.rigify":
                continue
            mesh = objects[name]
            if mesh.type != "MESH" or mesh.get("model_binding_id") != binding:
                raise FightMotionError("reopened render mesh is not privately bound")
            armature_modifiers = [mod for mod in mesh.modifiers if mod.type == "ARMATURE"]
            if not armature_modifiers or any(mod.object is not rig for mod in armature_modifiers):
                raise FightMotionError("reopened skin rig binding differs")
    if rigs[0] is rigs[1] or rigs[0].data is rigs[1].data or actions[0] is actions[1]:
        raise FightMotionError("attacker and receiver rigs/actions are not private")

    fixture = _pinned_fixture()
    if (receipt.get("blender") != bpy.app.version_string
            or receipt.get("embedded_scripts") != "disabled"
            or receipt.get("fps") != 30 or receipt.get("frame_range") != [0, 35]
            or receipt.get("camera", {}).get("resolution_px") != list(RENDER_SIZE)):
        raise FightMotionError("reopened receipt scene contract differs")
    render_verification = _verify_receipt_renders(receipt, receipt_path)
    rows, counts = _measure(bpy, instances)
    _validate_reopened_measurements(rows, counts, receipt, fixture)
    return {"status": "reopened_and_measured", "scene_sha256": sha256(scene_path),
            "checked_frames": list(FRAMES), "checked_frame_count": len(FRAMES),
            "summary_verified": True, "exposure_verified": True,
            "render_verification": render_verification,
            "actions": receipt["actions"]}


def build_contact_transfer_exchange(
    bpy, root: Path, fixture_path: Path, output: Path, *, render: bool,
    review_root: Path | None = None,
):
    """Opt-in successor; the pinned `build_exchange` path above stays unchanged."""
    from .contact_transfer import build_contact_transfer_exchange as build

    return build(bpy, root, fixture_path, output, render=render, review_root=review_root)


def reopen_contact_transfer(
    bpy, scene_path: Path, receipt_path: Path, *, root: Path | None = None,
    fixture_path: Path | None = None, review_root: Path | None = None,
):
    """Reopen and independently remeasure an opt-in contact-transfer proof."""
    from .contact_transfer import reopen_contact_transfer as reopen

    return reopen(bpy, scene_path, receipt_path, root=root,
                  fixture_path=fixture_path, review_root=review_root)
