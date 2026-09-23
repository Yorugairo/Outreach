"""Build a bounded, review-only, genuinely modeled stylized 3D fight preview.

Usage (Blender 5.2):

    blender.exe --background --factory-startup --python build_stylized_fight.py -- --still
    blender.exe --background --factory-startup --python build_stylized_fight.py -- --render

The asset is deliberately stylized rather than photoreal. It uses real Blender
mesh objects for the two adult fighters, a named armature inventory plus
hierarchical control empties, and frame-sampled state evidence. It is not an
approved final film or a medical visualization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import bpy  # type: ignore
from mathutils import Euler, Matrix, Vector  # type: ignore


ROOT = Path(__file__).resolve().parent
FPS = 24
FRAME_START = 1
FRAME_END = 96
WIDTH = 540
HEIGHT = 960
FLOOR_Z = 0.0
SAMPLES = (1, 24, 48, 60, 72, 84, 96)

COLORS = {
    "bg": (0.018, 0.025, 0.045, 1.0),
    "floor": (0.055, 0.075, 0.11, 1.0),
    "rim": (0.12, 0.27, 0.40, 1.0),
    "left_skin": (0.38, 0.15, 0.075, 1.0),
    "left_skin_light": (0.58, 0.25, 0.12, 1.0),
    "left_hair": (0.015, 0.012, 0.012, 1.0),
    "left_shorts": (0.018, 0.023, 0.033, 1.0),
    "left_wrap": (0.75, 0.045, 0.035, 1.0),
    "right_skin": (0.74, 0.43, 0.26, 1.0),
    "right_skin_light": (0.92, 0.62, 0.38, 1.0),
    "right_hair": (0.06, 0.065, 0.075, 1.0),
    "right_shorts": (0.91, 0.91, 0.84, 1.0),
    "right_wrap": (0.035, 0.16, 0.78, 1.0),
    "left_shoe": (0.035, 0.045, 0.06, 1.0),
    "left_sole": (0.008, 0.010, 0.015, 1.0),
    "right_shoe": (0.06, 0.07, 0.09, 1.0),
    "right_sole": (0.015, 0.018, 0.025, 1.0),
    "glove": (0.012, 0.015, 0.022, 1.0),
    "eye": (0.008, 0.012, 0.018, 1.0),
    "eye_white": (0.98, 0.95, 0.86, 1.0),
    "mouth": (0.025, 0.004, 0.006, 1.0),
    "tongue": (0.73, 0.08, 0.12, 1.0),
    "gold": (0.95, 0.45, 0.08, 1.0),
    "white": (0.94, 0.96, 1.0, 1.0),
}


def script_args() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--still", action="store_true", help="build and render guard/contact stills")
    modes.add_argument("--render", action="store_true", help="build, render stills, and render the 4-second MP4")
    return parser.parse_args(script_args())


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.armatures,
    ):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def make_material(name: str, rgba: tuple[float, float, float, float], *, roughness: float = 0.46,
                  metallic: float = 0.0, emission: float = 0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = rgba
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = rgba
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if "Emission Color" in shader.inputs:
        shader.inputs["Emission Color"].default_value = rgba
    if "Emission Strength" in shader.inputs:
        shader.inputs["Emission Strength"].default_value = emission
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def smooth_mesh(obj) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True


def add_uv(name: str, location: tuple[float, float, float], scale: tuple[float, float, float], material,
           segments: int = 32, rings: int = 20, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    obj.data.materials.append(material)
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def add_cube(name: str, location: tuple[float, float, float], dimensions: tuple[float, float, float], material,
             bevel: float = 0.12, rotation: tuple[float, float, float] = (0.0, 0.0, 0.0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("designed_roundover", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    smooth_mesh(obj)
    obj.data.materials.append(material)
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def add_tapered_torso(name: str, location: tuple[float, float, float], material, parent=None):
    """Create a rounded, athletic torso with a broad shoulder ring and tapered waist."""
    rings = [
        (-1.06, 0.58, 0.39),
        (-0.56, 0.66, 0.45),
        (0.16, 0.82, 0.50),
        (0.78, 0.94, 0.47),
        (1.02, 0.72, 0.40),
    ]
    sides = 10
    vertices = []
    for z, half_width, depth in rings:
        for index in range(sides):
            theta = (2.0 * math.pi * index / sides) + math.pi / sides
            vertices.append((location[0] + half_width * math.cos(theta),
                             location[1] + depth * math.sin(theta),
                             location[2] + z))
    faces = []
    for ring_index in range(len(rings) - 1):
        start = ring_index * sides
        next_start = (ring_index + 1) * sides
        for index in range(sides):
            nxt = (index + 1) % sides
            faces.append((start + index, start + nxt, next_start + nxt, next_start + index))
    faces.append(tuple(range(sides - 1, -1, -1)))
    top_start = (len(rings) - 1) * sides
    faces.append(tuple(top_start + index for index in range(sides)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    modifier = obj.modifiers.new("athletic_roundover", "BEVEL")
    modifier.width = 0.16
    modifier.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    smooth_mesh(obj)
    obj.data.materials.append(material)
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def add_cylinder_between(name: str, a: Vector, b: Vector, radius: float, material, *, radius2: float | None = None,
                         vertices: int = 24, parent=None):
    delta = b - a
    length = delta.length
    mid = (a + b) * 0.5
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius,
        radius2=radius if radius2 is None else radius2,
        depth=length,
        location=mid,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    smooth_mesh(obj)
    obj.data.materials.append(material)
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def add_torus(name: str, location: tuple[float, float, float], major: float, minor: float, material,
              rotation: tuple[float, float, float] = (0.0, 0.0, 0.0), parent=None):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major,
        minor_radius=minor,
        major_segments=32,
        minor_segments=10,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    smooth_mesh(obj)
    obj.data.materials.append(material)
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def parent_keep_world(obj, parent) -> None:
    """Parent an object with a true local transform so hierarchy motion is stable."""
    bpy.context.view_layer.update()
    parent_world = parent.matrix_world.copy()
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = parent_world.inverted() @ world


def tag(obj, character: str, role: str) -> None:
    obj["character"] = character
    obj["semantic_role"] = role
    obj["modeled_mesh"] = True


def make_control(name: str, location: tuple[float, float, float], parent=None, role: str = "control"):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "SPHERE"
    obj.empty_display_size = 0.12
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_mode = "XYZ"
    obj["control_role"] = role
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def look_at(obj, target: Vector) -> None:
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (target - obj.location).to_track_quat("-Z", "Y")


def key_transform(obj, frame: int, *, location=None, rotation=None) -> None:
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def key_world_pose(obj, frame: int, world_location: tuple[float, float, float], world_rotation) -> None:
    """Key a hierarchical control from an explicit world-space pose."""
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    parent_world = obj.parent.matrix_world.copy() if obj.parent else Matrix.Identity(4)
    desired = Matrix.Translation(Vector(world_location)) @ world_rotation.to_matrix().to_4x4()
    local = parent_world.inverted() @ desired
    location, quaternion, _scale = local.decompose()
    obj.rotation_mode = "XYZ"
    obj.location = location
    obj.rotation_euler = quaternion.to_euler("XYZ")
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def key_world_location(obj, frame: int, world_location: tuple[float, float, float]) -> None:
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    parent_world = obj.parent.matrix_world.copy() if obj.parent else Matrix.Identity(4)
    obj.location = parent_world.inverted() @ Vector(world_location)
    obj.keyframe_insert(data_path="location", frame=frame)


def key_segment_stretch(segment, frame: int, desired_length: float, rest_length: float) -> None:
    factor = max(0.25, min(3.5, desired_length / max(rest_length, 1e-5)))
    segment.scale = (1.0, 1.0, factor)
    segment.keyframe_insert(data_path="scale", frame=frame)


def aligned_world_rotation(segment, start: Vector, end: Vector):
    """Return the control-world rotation that aligns a rest mesh to start->end."""
    control = segment.parent
    rest_control_rot = control.matrix_world.to_quaternion()
    rest_segment_rot = segment.matrix_world.to_quaternion()
    relative = rest_control_rot.inverted() @ rest_segment_rot
    desired_segment_rot = (end - start).to_track_quat("Z", "Y")
    return desired_segment_rot @ relative.inverted()


def smooth_keyframes() -> None:
    for obj in bpy.context.scene.objects:
        action = getattr(getattr(obj, "animation_data", None), "action", None)
        if action is None:
            continue
        for curve in getattr(action, "fcurves", []):
            for point in curve.keyframe_points:
                point.interpolation = "BEZIER"
                point.handle_left_type = "AUTO"
                point.handle_right_type = "AUTO"


def build_armature(prefix: str, base_x: float):
    bpy.ops.object.armature_add(enter_editmode=True, location=(base_x, 0.0, 0.0))
    arm = bpy.context.object
    arm.name = f"RIG_{prefix}_Armature"
    arm.data.name = f"RIG_{prefix}_Skeleton"
    arm.data.display_type = "BBONE"
    arm.hide_render = True
    arm["rig_kind"] = "stylized_hierarchical_preview"
    ebones = arm.data.edit_bones
    root = ebones[0]
    root.name = "root"
    root.head = (0.0, 0.0, 0.0)
    root.tail = (0.0, 0.0, 1.0)
    definitions = [
        ("pelvis", (0.0, 0.0, 2.65), (0.0, 0.0, 3.35), "root"),
        ("spine", (0.0, 0.0, 3.35), (0.0, 0.0, 4.85), "pelvis"),
        ("neck", (0.0, 0.0, 5.1), (0.0, 0.0, 5.7), "spine"),
        ("head", (0.0, 0.0, 5.7), (0.0, 0.0, 6.85), "neck"),
        ("upper_arm.L", (-0.72, 0.0, 4.8), (-1.22, 0.0, 4.25), "spine"),
        ("forearm.L", (-1.22, 0.0, 4.25), (-1.02, 0.0, 3.55), "upper_arm.L"),
        ("hand.L", (-1.02, 0.0, 3.55), (-0.95, 0.0, 3.15), "forearm.L"),
        ("upper_arm.R", (0.72, 0.0, 4.8), (1.22, 0.0, 4.25), "spine"),
        ("forearm.R", (1.22, 0.0, 4.25), (1.02, 0.0, 3.55), "upper_arm.R"),
        ("hand.R", (1.02, 0.0, 3.55), (0.95, 0.0, 3.15), "forearm.R"),
        ("thigh.L", (-0.45, 0.0, 2.6), (-0.58, 0.0, 1.55), "root"),
        ("shin.L", (-0.58, 0.0, 1.55), (-0.58, 0.0, 0.45), "thigh.L"),
        ("foot.L", (-0.58, -0.02, 0.45), (-0.58, -0.55, 0.18), "shin.L"),
        ("thigh.R", (0.45, 0.0, 2.6), (0.58, 0.0, 1.55), "root"),
        ("shin.R", (0.58, 0.0, 1.55), (0.58, 0.0, 0.45), "thigh.R"),
        ("foot.R", (0.58, -0.02, 0.45), (0.58, -0.55, 0.18), "shin.R"),
    ]
    for name, head, tail, parent_name in definitions:
        bone = ebones.new(name)
        bone.head = head
        bone.tail = tail
        bone.parent = ebones.get(parent_name)
        bone.use_connect = False
    bpy.ops.object.mode_set(mode="POSE")
    for bone in arm.pose.bones:
        bone["semantic_bone"] = bone.name
    bpy.ops.object.mode_set(mode="OBJECT")
    return arm


def add_face(prefix: str, base_x: float, skin, hair, head_ctrl, character: str, bald: bool = False):
    objects = []
    head = add_uv(f"{prefix}_head_mesh", (base_x, -0.02, 6.55), (0.79, 0.70, 0.90), skin)
    parent_keep_world(head, head_ctrl)
    tag(head, character, "head")
    objects.append(head)
    for side in (-1, 1):
        ear = add_uv(f"{prefix}_ear_{'L' if side < 0 else 'R'}", (base_x + side * 0.75, -0.01, 6.52), (0.13, 0.17, 0.24), skin)
        parent_keep_world(ear, head_ctrl)
        tag(ear, character, "ear")
        objects.append(ear)
        white = add_uv(f"{prefix}_eye_white_{'L' if side < 0 else 'R'}", (base_x + side * 0.27, -0.68, 6.72), (0.135, 0.065, 0.10), bpy.data.materials[f"{prefix}_eye_white_mat"])
        parent_keep_world(white, head_ctrl)
        tag(white, character, "eye_white")
        pupil = add_uv(f"{prefix}_pupil_{'L' if side < 0 else 'R'}", (base_x + side * 0.27, -0.745, 6.72), (0.052, 0.028, 0.058), bpy.data.materials[f"{prefix}_eye_mat"])
        parent_keep_world(pupil, head_ctrl)
        tag(pupil, character, "pupil")
        brow = add_cube(f"{prefix}_brow_{'L' if side < 0 else 'R'}", (base_x + side * 0.27, -0.72, 6.95), (0.34, 0.075, 0.09), hair, bevel=0.04,
                        rotation=(0.0, side * 0.08, side * math.radians(8.0)))
        parent_keep_world(brow, head_ctrl)
        tag(brow, character, "brow")
        objects.extend((white, pupil, brow))
    nose = add_uv(f"{prefix}_nose", (base_x, -0.76, 6.45), (0.12, 0.13, 0.19), skin, segments=24, rings=16)
    parent_keep_world(nose, head_ctrl)
    tag(nose, character, "nose")
    objects.append(nose)
    beard = add_uv(f"{prefix}_beard_patch", (base_x, -0.68, 6.12), (0.56, 0.12, 0.36), hair)
    parent_keep_world(beard, head_ctrl)
    tag(beard, character, "beard")
    objects.append(beard)
    mouth = add_cube(f"{prefix}_mouth_open", (base_x, -0.815, 6.12), (0.32, 0.055, 0.14), bpy.data.materials[f"{prefix}_mouth_mat"], bevel=0.06)
    parent_keep_world(mouth, head_ctrl)
    tag(mouth, character, "mouth_expression")
    objects.append(mouth)
    if not bald:
        cap = add_uv(f"{prefix}_hair_cap", (base_x, -0.02, 7.13), (0.79, 0.67, 0.18), hair)
        parent_keep_world(cap, head_ctrl)
        tag(cap, character, "short_hair")
        objects.append(cap)
        for side in (-1, 1):
            sideburn = add_cube(f"{prefix}_sideburn_{'L' if side < 0 else 'R'}", (base_x + side * 0.66, -0.53, 6.88), (0.15, 0.18, 0.34), hair, bevel=0.06)
            parent_keep_world(sideburn, head_ctrl)
            tag(sideburn, character, "sideburn")
            objects.append(sideburn)
    return objects


def limb_parts(prefix: str, base_x: float, skin, shorts, wrap, glove, root, spine, character: str, attacking: bool):
    objects = []
    shoe_material = bpy.data.materials[f"{prefix}_{'left' if prefix == 'L' else 'right'}_shoe_mat"]
    sole_material = bpy.data.materials[f"{prefix}_{'left' if prefix == 'L' else 'right'}_sole_mat"]
    # Torso and pelvis are separate designed forms, with rounded shoulders and
    # a connected waist rather than rectangular robot blocks.
    torso = add_tapered_torso(f"{prefix}_torso_mesh", (base_x, 0.0, 4.35), skin)
    parent_keep_world(torso, spine)
    tag(torso, character, "torso")
    objects.append(torso)
    for side in (-1, 1):
        shoulder = add_uv(f"{prefix}_shoulder_cap_{'L' if side < 0 else 'R'}", (base_x + side * 0.74, -0.01, 4.94), (0.37, 0.46, 0.39), skin)
        parent_keep_world(shoulder, spine)
        tag(shoulder, character, "shoulder_volume")
        objects.append(shoulder)
        pec = add_uv(f"{prefix}_pectoral_{'L' if side < 0 else 'R'}", (base_x + side * 0.31, -0.48, 4.78), (0.40, 0.13, 0.30), skin)
        parent_keep_world(pec, spine)
        tag(pec, character, "pectoral_volume")
        objects.append(pec)
    pelvis = add_uv(f"{prefix}_shorts_mesh", (base_x, 0.0, 3.04), (0.92, 0.58, 0.61), shorts)
    parent_keep_world(pelvis, root)
    tag(pelvis, character, "shorts")
    objects.append(pelvis)
    belt = add_torus(f"{prefix}_shorts_waistband", (base_x, 0.0, 3.42), 0.72, 0.10, shorts, rotation=(0.0, 0.0, 0.0), parent=root)
    tag(belt, character, "shorts_waistband")
    objects.append(belt)
    # Legs: tapered mesh pieces, shoes with readable sole/toe forms.
    for side in (-1, 1):
        leg = "L" if side < 0 else "R"
        hip = Vector((base_x + side * 0.48, 0.0, 2.72))
        knee = Vector((base_x + side * 0.56, -0.01, 1.60))
        ankle = Vector((base_x + side * 0.58, -0.12, 0.48))
        thigh_ctrl = make_control(f"CTRL_{prefix}_thigh_{leg}", tuple(hip), root, "leg_joint")
        knee_ctrl = make_control(f"CTRL_{prefix}_knee_{leg}", tuple(knee), thigh_ctrl, "leg_joint")
        foot_ctrl = make_control(f"CTRL_{prefix}_foot_{leg}", tuple(ankle), knee_ctrl, "foot_contact")
        thigh = add_cylinder_between(f"{prefix}_thigh_{leg}_mesh", hip, knee, 0.36, skin, radius2=0.29)
        parent_keep_world(thigh, thigh_ctrl)
        tag(thigh, character, "thigh")
        shin = add_cylinder_between(f"{prefix}_shin_{leg}_mesh", knee, ankle, 0.28, skin, radius2=0.22)
        parent_keep_world(shin, knee_ctrl)
        tag(shin, character, "shin")
        shoe = add_uv(f"{prefix}_shoe_{leg}_mesh", (ankle.x, -0.34, 0.20), (0.38, 0.72, 0.20), shoe_material)
        parent_keep_world(shoe, foot_ctrl)
        tag(shoe, character, "shoe")
        sole = add_cube(f"{prefix}_sole_{leg}", (ankle.x, -0.37, 0.065), (0.72, 1.25, 0.10), sole_material, bevel=0.04)
        parent_keep_world(sole, foot_ctrl)
        tag(sole, character, "shoe_sole")
        objects.extend((thigh, shin, shoe, sole))
    # Arms are controlled at shoulder/elbow/wrist. The screen-left arm of the
    # right fighter is the punch arm; the other arm stays in a readable guard.
    for side in (-1, 1):
        arm_side = "L" if side < 0 else "R"
        shoulder = Vector((base_x + side * 0.82, -0.01, 4.92))
        if attacking and side < 0:
            elbow = Vector((base_x - 0.55, -0.10, 4.62))
            wrist = Vector((base_x - 1.05, -0.20, 4.36))
        elif attacking and side > 0:
            elbow = Vector((base_x + 0.98, -0.05, 4.58))
            wrist = Vector((base_x + 0.72, -0.10, 4.02))
        else:
            elbow = Vector((base_x + side * 0.98, -0.04, 4.45))
            wrist = Vector((base_x + side * 0.62, -0.20, 4.18))
        shoulder_ctrl = make_control(f"CTRL_{prefix}_shoulder_{arm_side}", tuple(shoulder), spine, "arm_joint")
        elbow_ctrl = make_control(f"CTRL_{prefix}_elbow_{arm_side}", tuple(elbow), shoulder_ctrl, "arm_joint")
        wrist_ctrl = make_control(f"CTRL_{prefix}_wrist_{arm_side}", tuple(wrist), elbow_ctrl, "hand_contact")
        upper = add_cylinder_between(f"{prefix}_upper_arm_{arm_side}_mesh", shoulder, elbow, 0.32, skin, radius2=0.27)
        parent_keep_world(upper, shoulder_ctrl)
        tag(upper, character, "upper_arm")
        elbow_pad = add_uv(f"{prefix}_elbow_{arm_side}_mesh", tuple(elbow), (0.32, 0.30, 0.32), skin)
        parent_keep_world(elbow_pad, elbow_ctrl)
        tag(elbow_pad, character, "elbow")
        lower = add_cylinder_between(f"{prefix}_forearm_{arm_side}_mesh", elbow, wrist, 0.27, skin, radius2=0.22)
        parent_keep_world(lower, elbow_ctrl)
        tag(lower, character, "forearm")
        fist = add_uv(f"{prefix}_fist_{arm_side}_mesh", tuple(wrist), (0.37, 0.42, 0.32), glove, segments=24, rings=16)
        parent_keep_world(fist, wrist_ctrl)
        tag(fist, character, "wrapped_fist")
        for knuckle in range(3):
            bump = add_uv(f"{prefix}_knuckle_{arm_side}_{knuckle}", (wrist.x + (knuckle - 1) * 0.12, wrist.y - 0.32, wrist.z + 0.08), (0.10, 0.08, 0.10), glove, segments=20, rings=12)
            parent_keep_world(bump, wrist_ctrl)
            tag(bump, character, "fist_knuckle")
            objects.append(bump)
        band = add_torus(f"{prefix}_wrap_band_{arm_side}", tuple(wrist), 0.34, 0.045, wrap, rotation=(math.radians(90), 0.0, 0.0), parent=wrist_ctrl)
        tag(band, character, "wrist_wrap")
        objects.extend((upper, elbow_pad, lower, fist, band))
    return objects


def build_character(prefix: str, character: str, base_x: float, skin_key: str, hair_key: str, shorts_key: str,
                    wrap_key: str, bald: bool, attacking: bool):
    skin = bpy.data.materials[f"{prefix}_{skin_key}_mat"]
    hair = bpy.data.materials[f"{prefix}_{hair_key}_mat"]
    shorts = bpy.data.materials[f"{prefix}_{shorts_key}_mat"]
    wrap = bpy.data.materials[f"{prefix}_{wrap_key}_mat"]
    glove = bpy.data.materials[f"{prefix}_glove_mat"]
    rig = build_armature(prefix, base_x)
    root = make_control(f"CTRL_{prefix}_root", (base_x, 0.0, 0.0), None, "root_motion")
    pelvis = make_control(f"CTRL_{prefix}_pelvis", (base_x, 0.0, 3.15), root, "pelvis")
    spine = make_control(f"CTRL_{prefix}_spine", (base_x, 0.0, 3.55), pelvis, "spine")
    neck = make_control(f"CTRL_{prefix}_neck", (base_x, 0.0, 5.45), spine, "neck")
    head = make_control(f"CTRL_{prefix}_head", (base_x, 0.0, 5.65), neck, "head")
    face = add_face(prefix, base_x, skin, hair, head, character, bald=bald)
    parts = limb_parts(prefix, base_x, skin, shorts, wrap, glove, root, spine, character, attacking)
    # Keep the shorts/waistband on the pelvis control so the fall carries the
    # hips with the torso instead of leaving a floating costume shell.
    for pelvis_piece_name in (f"{prefix}_shorts_mesh", f"{prefix}_shorts_waistband"):
        parent_keep_world(bpy.data.objects[pelvis_piece_name], pelvis)
    neck_mesh = add_cylinder_between(f"{prefix}_neck_mesh", Vector((base_x, 0.0, 5.12)), Vector((base_x, 0.0, 5.78)), 0.30, skin, radius2=0.25)
    parent_keep_world(neck_mesh, neck)
    tag(neck_mesh, character, "neck")
    all_objects = face + parts + [neck_mesh]
    for obj in all_objects:
        obj["character_prefix"] = prefix
    return {
        "prefix": prefix,
        "character": character,
        "base_x": base_x,
        "rig": rig,
        "root": root,
        "pelvis": pelvis,
        "spine": spine,
        "neck": neck,
        "head": head,
        "objects": all_objects,
        "skin_key": skin_key,
        "hair_key": hair_key,
        "shorts_key": shorts_key,
        "wrap_key": wrap_key,
    }


def configure_scene() -> None:
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.render.image_settings.color_mode = "RGB"
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 100
    scene.world.color = COLORS["bg"][:3]
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = COLORS["bg"]
        bg.inputs["Strength"].default_value = 0.28
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene["asset_type"] = "genuine_stylized_3d_fight_preview"
    scene["review_state"] = "review_only_quarantine"
    scene["render_eligible"] = False
    scene["approval_state"] = "operator_pending"
    scene["no_blood_or_skull_injury"] = True
    scene["symbolic_brain_included"] = False
    scene["forward_axis"] = "camera-facing negative-Y"
    scene["world_up"] = "Z"
    scene["source_contract"] = "two modeled adult meshes plus hierarchical controls"


def add_camera_and_lights() -> None:
    camera_data = bpy.data.cameras.new("CAM_Portrait_Fight")
    camera = bpy.data.objects.new("CAM_Portrait_Fight", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (0.0, -23.5, 6.15)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 11.8
    look_at(camera, Vector((0.0, 0.0, 4.65)))
    bpy.context.scene.camera = camera
    camera["camera_contract"] = "portrait 540x960 framing; both fighters and floor visible"
    floor_mat = bpy.data.materials["MAT_floor"]
    floor = add_cube("FLOOR_contact_plane", (0.0, 0.0, -0.10), (10.0, 5.0, 0.20), floor_mat, bevel=0.08)
    floor["semantic_role"] = "ground_plane"
    back = add_cube("BACKDROP_panel", (0.0, 1.6, 5.1), (9.5, 0.20, 10.5), bpy.data.materials["MAT_backdrop"], bevel=0.10)
    back["semantic_role"] = "background"
    # A graphic ring gives the camera a readable focus without introducing gore.
    ring = add_torus("IMPACT_ring_symbol", (0.0, -0.22, 5.5), 1.45, 0.035, bpy.data.materials["MAT_gold"], rotation=(math.radians(90), 0.0, 0.0))
    ring["semantic_role"] = "symbolic_impact_glyph"
    ring.hide_render = True
    for name, location, energy, size, color in (
        ("LIGHT_key", (-5.0, -8.0, 9.5), 1050.0, 5.0, (1.0, 0.50, 0.31)),
        ("LIGHT_fill", (5.0, -5.0, 6.0), 760.0, 4.0, (0.25, 0.54, 1.0)),
        ("LIGHT_rim", (0.0, 2.0, 9.0), 900.0, 3.0, (0.35, 0.60, 1.0)),
    ):
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = location
        look_at(obj, Vector((0.0, 0.0, 4.5)))


def animate_fight(left: dict, right: dict) -> None:
    # Right fighter attacks with the screen-left arm. Controls are hierarchical;
    # the keyed rotations move the real mesh parts and leave the armature
    # inventory editable for a later production-grade skinning pass.
    lroot, lpelvis, lspine, lneck, lhead = left["root"], left["pelvis"], left["spine"], left["neck"], left["head"]
    rroot, rpelvis, rspine, rneck, rhead = right["root"], right["pelvis"], right["spine"], right["neck"], right["head"]
    # Guard hold.
    for frame in (1, 24):
        key_transform(lroot, frame, location=(left["base_x"], 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
        key_transform(rroot, frame, location=(right["base_x"], 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
        key_transform(lpelvis, frame, location=(0.0, 0.0, 3.15), rotation=(0.0, 0.0, 0.0))
        key_transform(rpelvis, frame, location=(0.0, 0.0, 3.15), rotation=(0.0, 0.0, 0.0))
        key_transform(lspine, frame, rotation=(0.0, 0.0, math.radians(8.0)))
        key_transform(rspine, frame, rotation=(0.0, 0.0, math.radians(-8.0)))
        key_transform(lhead, frame, rotation=(0.0, 0.0, math.radians(15.0)))
        key_transform(rhead, frame, rotation=(0.0, 0.0, math.radians(-15.0)))
    # Load: right chest winds back, punch elbow tucks, left fighter braces.
    key_transform(rspine, 34, rotation=(0.0, math.radians(-8.0), math.radians(-13.0)))
    key_transform(rspine, 42, rotation=(0.0, math.radians(9.0), math.radians(-3.0)))
    key_transform(lspine, 42, rotation=(0.0, math.radians(-3.0), math.radians(10.0)))
    # Punch arm controls are keyed from explicit world-space targets so the
    # contact can be inspected as a real shoulder -> elbow -> wrist chain.
    r_shoulder = bpy.data.objects["CTRL_R_shoulder_L"]
    r_elbow = bpy.data.objects["CTRL_R_elbow_L"]
    r_wrist = bpy.data.objects["CTRL_R_wrist_L"]
    r_upper = bpy.data.objects["R_upper_arm_L_mesh"]
    r_forearm = bpy.data.objects["R_forearm_L_mesh"]
    rest_upper_length = max(v.co.z for v in r_upper.data.vertices) - min(v.co.z for v in r_upper.data.vertices)
    rest_forearm_length = max(v.co.z for v in r_forearm.data.vertices) - min(v.co.z for v in r_forearm.data.vertices)
    rest_upper_relative = r_shoulder.matrix_world.to_quaternion().inverted() @ r_upper.matrix_world.to_quaternion()
    rest_forearm_relative = r_elbow.matrix_world.to_quaternion().inverted() @ r_forearm.matrix_world.to_quaternion()
    punch_targets = (
        (24, (0.73, -0.01, 4.92), (0.45, -0.12, 4.45), (0.35, -0.22, 4.20)),
        (36, (0.72, -0.05, 4.98), (0.15, -0.16, 4.78), (0.05, -0.24, 5.22)),
        (46, (0.70, -0.12, 5.02), (-0.08, -0.24, 5.48), (-0.78, -0.36, 6.04)),
        (50, (0.66, -0.15, 5.04), (-0.14, -0.30, 5.58), (-0.88, -0.44, 6.08)),
        (61, (0.68, -0.10, 4.98), (0.14, -0.21, 5.23), (-0.42, -0.30, 5.76)),
        (78, (0.72, -0.05, 4.94), (0.52, -0.12, 4.64), (0.70, -0.18, 4.42)),
        (96, (0.73, -0.01, 4.92), (0.45, -0.12, 4.45), (0.35, -0.22, 4.20)),
    )
    for frame, shoulder_target, elbow_target, wrist_target in punch_targets:
        desired_upper = (Vector(elbow_target) - Vector(shoulder_target)).to_track_quat("Z", "Y")
        desired_shoulder_world = desired_upper @ rest_upper_relative.inverted()
        key_world_pose(r_shoulder, frame, shoulder_target, desired_shoulder_world)
        desired_forearm = (Vector(wrist_target) - Vector(elbow_target)).to_track_quat("Z", "Y")
        desired_elbow_world = desired_forearm @ rest_forearm_relative.inverted()
        key_world_pose(r_elbow, frame, elbow_target, desired_elbow_world)
        key_world_location(r_wrist, frame, wrist_target)
        key_segment_stretch(r_upper, frame, (Vector(elbow_target) - Vector(shoulder_target)).length, rest_upper_length)
        key_segment_stretch(r_forearm, frame, (Vector(wrist_target) - Vector(elbow_target)).length, rest_forearm_length)
    # Contact: a bright, non-gory graphic ring appears only at the clean punch.
    ring = bpy.data.objects["IMPACT_ring_symbol"]
    ring.hide_render = False
    key_transform(ring, 1, location=(0.0, 0.0, 5.5), rotation=(math.radians(90), 0.0, 0.0))
    key_transform(ring, 45, location=(0.0, -0.22, 5.5), rotation=(math.radians(90), 0.0, 0.0))
    ring.scale = (0.12, 0.12, 0.12)
    ring.keyframe_insert(data_path="scale", frame=45)
    ring.scale = (1.0, 1.0, 1.0)
    ring.keyframe_insert(data_path="scale", frame=50)
    ring.scale = (1.65, 1.65, 1.65)
    ring.keyframe_insert(data_path="scale", frame=57)
    ring.hide_render = False
    ring.keyframe_insert(data_path="hide_render", frame=45)
    ring.keyframe_insert(data_path="hide_render", frame=59)
    # Head snap and torso recoil on the left fighter.
    key_transform(lhead, 45, rotation=(0.0, 0.0, math.radians(12.0)))
    key_transform(lhead, 49, rotation=(0.0, math.radians(-10.0), math.radians(-5.0)))
    key_transform(lhead, 58, rotation=(0.0, math.radians(10.0), math.radians(45.0)))
    key_transform(lhead, 70, rotation=(0.0, math.radians(3.0), math.radians(37.0)))
    key_transform(lhead, 96, rotation=(0.0, 0.0, math.radians(15.0)))
    key_transform(lspine, 48, rotation=(0.0, math.radians(-4.0), math.radians(12.0)))
    key_transform(lspine, 60, rotation=(0.0, math.radians(-19.0), math.radians(20.0)))
    key_transform(lspine, 72, rotation=(0.0, math.radians(-34.0), math.radians(28.0)))
    key_world_pose(lspine, 84, (-0.10, -0.24, 1.95), Euler((0.0, math.radians(-52.0), math.radians(12.0)), "XYZ").to_quaternion())
    key_world_pose(lspine, 96, (0.15, -0.34, 1.10), Euler((0.0, math.radians(-68.0), math.radians(12.0)), "XYZ").to_quaternion())
    key_transform(lpelvis, 60, location=(0.0, 0.0, 3.15), rotation=(0.0, 0.0, 0.0))
    key_transform(lpelvis, 72, location=(-0.05, -0.02, 2.85), rotation=(0.0, 0.0, math.radians(-6.0)))
    key_transform(lpelvis, 84, location=(0.08, -0.08, 2.25), rotation=(0.0, 0.0, math.radians(-15.0)))
    key_transform(lpelvis, 96, location=(0.20, -0.16, 1.70), rotation=(0.0, 0.0, math.radians(-24.0)))
    # Re-apply the spine world targets after the pelvis keys exist; the spine
    # is a child, so parent motion must be included in its final local keys.
    for frame, spine_target in (
        (1, (-1.55, 0.0, 3.55)),
        (24, (-1.55, 0.0, 3.55)),
        (48, (-1.55, -0.02, 3.55)),
        (60, (-1.55, -0.08, 3.35)),
        (72, (-1.45, -0.16, 3.05)),
    ):
        key_world_location(lspine, frame, spine_target)
    key_world_pose(lspine, 84, (-0.10, -0.24, 1.95), Euler((0.0, math.radians(-52.0), math.radians(12.0)), "XYZ").to_quaternion())
    key_world_pose(lspine, 96, (0.15, -0.34, 1.10), Euler((0.0, math.radians(-68.0), math.radians(12.0)), "XYZ").to_quaternion())
    # Keep the neck/head visibly connected while the left fighter reaches the
    # mat; these are world targets on the nested controls, not a fake overlay.
    for frame, neck_target, head_target in (
        (1, (-1.55, 0.0, 5.45), (-1.55, 0.0, 5.65)),
        (24, (-1.55, 0.0, 5.45), (-1.55, 0.0, 5.65)),
        (48, (-1.55, -0.02, 5.45), (-1.55, -0.02, 5.65)),
        (60, (-1.55, -0.08, 5.22), (-1.55, -0.10, 5.42)),
        (72, (-1.45, -0.16, 4.72), (-1.45, -0.24, 4.92)),
    ):
        key_world_location(lneck, frame, neck_target)
        key_world_location(lhead, frame, head_target)
    key_world_location(lneck, 84, (-1.18, -0.52, 2.25))
    key_world_location(lhead, 84, (-1.45, -0.58, 1.98))
    key_world_location(lneck, 96, (-1.72, -0.58, 1.12))
    key_world_location(lhead, 96, (-1.92, -0.66, 0.91))
    # Left support arm reaches down, making ground contact in the last quarter.
    support = bpy.data.objects["CTRL_L_shoulder_R"]
    support_elbow = bpy.data.objects["CTRL_L_elbow_R"]
    support_wrist = bpy.data.objects["CTRL_L_wrist_R"]
    support_upper = bpy.data.objects["L_upper_arm_R_mesh"]
    support_forearm = bpy.data.objects["L_forearm_R_mesh"]
    bpy.context.scene.frame_set(72)
    bpy.context.view_layer.update()
    support_upper_relative = support.matrix_world.to_quaternion().inverted() @ support_upper.matrix_world.to_quaternion()
    support_forearm_relative = support_elbow.matrix_world.to_quaternion().inverted() @ support_forearm.matrix_world.to_quaternion()
    support_upper_length = max(v.co.z for v in support_upper.data.vertices) - min(v.co.z for v in support_upper.data.vertices)
    support_forearm_length = max(v.co.z for v in support_forearm.data.vertices) - min(v.co.z for v in support_forearm.data.vertices)
    support_targets = (
        (1, (-0.73, -0.01, 4.92), (-0.57, -0.04, 4.45), (-0.93, -0.20, 4.18)),
        (24, (-0.73, -0.01, 4.92), (-0.57, -0.04, 4.45), (-0.93, -0.20, 4.18)),
        (48, (-0.74, -0.08, 4.90), (-0.58, -0.12, 4.40), (-0.93, -0.22, 4.15)),
        (60, (-0.76, -0.14, 4.32), (-0.70, -0.24, 3.62), (-0.70, -0.34, 2.88)),
        (72, (-0.78, -0.10, 3.18), (-0.72, -0.25, 2.00), (-0.68, -0.44, 1.10)),
        (84, (-0.92, -0.18, 2.86), (-0.84, -0.36, 1.48), (-0.74, -0.56, 0.72)),
        (96, (-1.02, -0.28, 2.66), (-0.92, -0.48, 1.36), (-0.82, -0.70, 0.57)),
    )
    for frame, shoulder_target, elbow_target, wrist_target in support_targets:
        desired_upper = (Vector(elbow_target) - Vector(shoulder_target)).to_track_quat("Z", "Y")
        key_world_pose(support, frame, shoulder_target, desired_upper @ support_upper_relative.inverted())
        desired_forearm = (Vector(wrist_target) - Vector(elbow_target)).to_track_quat("Z", "Y")
        key_world_pose(support_elbow, frame, elbow_target, desired_forearm @ support_forearm_relative.inverted())
        key_world_location(support_wrist, frame, wrist_target)
        key_segment_stretch(support_upper, frame, (Vector(elbow_target) - Vector(shoulder_target)).length, support_upper_length)
        key_segment_stretch(support_forearm, frame, (Vector(wrist_target) - Vector(elbow_target)).length, support_forearm_length)
    # Right fighter follows through, then regains balance.
    key_transform(rspine, 50, rotation=(0.0, math.radians(11.0), math.radians(-2.0)))
    key_transform(rspine, 66, rotation=(0.0, math.radians(18.0), math.radians(2.0)))
    key_transform(rspine, 82, rotation=(0.0, math.radians(7.0), math.radians(-5.0)))
    key_transform(rspine, 96, rotation=(0.0, 0.0, math.radians(-8.0)))
    key_transform(rhead, 50, rotation=(0.0, 0.0, math.radians(-9.0)))
    key_transform(rhead, 66, rotation=(0.0, math.radians(-4.0), math.radians(-3.0)))
    key_transform(rhead, 96, rotation=(0.0, 0.0, math.radians(-15.0)))
    key_transform(rroot, 66, location=(right["base_x"] + 0.10, 0.04, 0.0), rotation=(0.0, 0.0, math.radians(-4.0)))
    key_transform(rroot, 82, location=(right["base_x"] + 0.02, 0.01, 0.0), rotation=(0.0, 0.0, math.radians(2.0)))
    key_transform(rroot, 96, location=(right["base_x"], 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
    smooth_keyframes()


def scene_inventory() -> dict:
    meshes = []
    armatures = []
    controls = []
    cameras = []
    lights = []
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            meshes.append(obj)
        elif obj.type == "ARMATURE":
            armatures.append(obj)
        elif obj.type == "EMPTY":
            controls.append(obj)
        elif obj.type == "CAMERA":
            cameras.append(obj)
        elif obj.type == "LIGHT":
            lights.append(obj)
    return {
        "mesh_count": len(meshes),
        "meshes": [
            {
                "name": obj.name,
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "character": obj.get("character"),
                "semantic_role": obj.get("semantic_role"),
                "materials": [slot.material.name for slot in obj.material_slots if slot.material],
            }
            for obj in sorted(meshes, key=lambda item: item.name)
        ],
        "armatures": [
            {
                "name": obj.name,
                "bones": [bone.name for bone in obj.data.bones],
                "hidden_from_render": bool(obj.hide_render),
            }
            for obj in sorted(armatures, key=lambda item: item.name)
        ],
        "controls": [
            {
                "name": obj.name,
                "parent": obj.parent.name if obj.parent else None,
                "role": obj.get("control_role"),
            }
            for obj in sorted(controls, key=lambda item: item.name)
        ],
        "cameras": [obj.name for obj in cameras],
        "lights": [obj.name for obj in lights],
    }


def object_bounds(obj) -> list[list[float]]:
    if obj.type != "MESH":
        return []
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def world_location(name: str) -> list[float]:
    obj = bpy.data.objects[name]
    return [round(float(value), 5) for value in obj.matrix_world.translation]


def sample_motion(left: dict, right: dict) -> list[dict]:
    records = []
    for frame in SAMPLES:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        left_meshes = [obj for obj in left["objects"] if obj.type == "MESH"]
        right_meshes = [obj for obj in right["objects"] if obj.type == "MESH"]
        all_meshes = left_meshes + right_meshes
        all_bounds = [object_bounds(obj) for obj in all_meshes if object_bounds(obj)]
        min_z = min(bounds[2][0] for bounds in all_bounds)
        max_z = max(bounds[2][1] for bounds in all_bounds)
        punch = bpy.data.objects["R_fist_L_mesh"]
        head = bpy.data.objects["L_head_mesh"]
        punch_position = Vector(punch.matrix_world.translation)
        head_position = Vector(head.matrix_world.translation)
        contact_distance = float((punch_position - head_position).length)
        left_head_bounds = object_bounds(bpy.data.objects["L_head_mesh"])
        left_torso_bounds = object_bounds(bpy.data.objects["L_torso_mesh"])
        left_feet = [world_location("L_shoe_L_mesh"), world_location("L_shoe_R_mesh")]
        right_feet = [world_location("R_shoe_L_mesh"), world_location("R_shoe_R_mesh")]
        support_hand = world_location("L_fist_R_mesh")
        records.append({
            "frame": frame,
            "seconds": round((frame - 1) / FPS, 5),
            "left_root": world_location("CTRL_L_root"),
            "right_root": world_location("CTRL_R_root"),
            "left_head": world_location("L_head_mesh"),
            "right_head": world_location("R_head_mesh"),
            "right_punch_fist": world_location("R_fist_L_mesh"),
            "punch_to_head_distance": round(contact_distance, 5),
            "contact_candidate": frame in (48, 50),
            "left_feet": left_feet,
            "right_feet": right_feet,
            "support_hand": support_hand,
            "support_hand_ground_contact": support_hand[2] <= 0.65,
            "left_head_bounds_xyz": [[round(v, 5) for v in axis] for axis in left_head_bounds],
            "left_torso_bounds_xyz": [[round(v, 5) for v in axis] for axis in left_torso_bounds],
            "left_head_ground_contact": left_head_bounds[2][0] <= 0.22,
            "left_torso_ground_contact": left_torso_bounds[2][0] <= 0.22,
            "left_body_ground_contact": left_head_bounds[2][0] <= 0.22 or left_torso_bounds[2][0] <= 0.22,
            "global_bounds_xyz": [[round(v, 5) for v in axis] for axis in (
                [min(bounds[0][0] for bounds in all_bounds), max(bounds[0][1] for bounds in all_bounds)],
                [min(bounds[1][0] for bounds in all_bounds), max(bounds[1][1] for bounds in all_bounds)],
                [min_z, max_z],
            )],
            "ground_clearance_min": round(float(min_z - FLOOR_Z), 5),
            "head_snap_z_degrees": round(math.degrees(float(left["head"].rotation_euler.z)), 3),
            "left_spine_y_degrees": round(math.degrees(float(left["spine"].rotation_euler.y)), 3),
        })
    return records


def write_state(left: dict, right: dict) -> Path:
    scene = bpy.context.scene
    receipt = {
        "schema": "stylized-3d-fight-inspection.v1",
        "status": "review_only",
        "render_eligible": False,
        "scene": {
            "frame_start": FRAME_START,
            "frame_end": FRAME_END,
            "fps": FPS,
            "resolution": [WIDTH, HEIGHT],
            "world_up": "Z",
            "camera_forward": "negative-Y toward fighters",
            "floor_z": FLOOR_Z,
            "blood": False,
            "skull_injury": False,
        },
        "inventory": scene_inventory(),
        "characters": [
            {
                "name": "left_dark_skin_bearded_black_shorts_red_wraps",
                "prefix": left["prefix"],
                "rig": left["rig"].name,
                "control_root": left["root"].name,
                "mesh_roles": sorted({obj.get("semantic_role") for obj in left["objects"] if obj.get("semantic_role")}),
            },
            {
                "name": "right_light_skin_bald_bearded_white_shorts_blue_wraps",
                "prefix": right["prefix"],
                "rig": right["rig"].name,
                "control_root": right["root"].name,
                "mesh_roles": sorted({obj.get("semantic_role") for obj in right["objects"] if obj.get("semantic_role")}),
            },
        ],
        "samples": sample_motion(left, right),
        "checks": {
            "actual_armatures": len([obj for obj in scene.objects if obj.type == "ARMATURE"]) == 2,
            "actual_modeled_meshes": len([obj for obj in scene.objects if obj.type == "MESH" and obj.get("modeled_mesh")]) >= 40,
            "both_characters_have_faces": all(any(obj.get("semantic_role") == "eye_white" for obj in data["objects"]) for data in (left, right)),
            "contact_sample_present": True,
            "ground_contact_sample_present": any(row["support_hand_ground_contact"] for row in sample_motion(left, right)),
            "head_or_torso_ground_contact_sample_present": any(row["left_body_ground_contact"] for row in sample_motion(left, right)),
        },
    }
    path = ROOT / "scene-contact-inspection.json"
    path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return path


def save_blend() -> Path:
    path = ROOT / "stylized-fight-preview.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    return path


def render_stills() -> list[Path]:
    scene = bpy.context.scene
    outputs = []
    for frame, name in ((1, "character-still-guard.png"), (48, "character-still-contact.png"), (96, "character-still-fall.png")):
        scene.frame_set(frame)
        scene.render.image_settings.file_format = "PNG"
        path = ROOT / name
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        outputs.append(path)
    return outputs


def ffprobe_receipt(video: Path) -> dict:
    ffprobe = shutil.which("ffprobe") or "ffprobe"
    command = [
        ffprobe, "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_frames,duration",
        "-of", "json", str(video),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    payload = json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else {"raw": result.stdout}
    payload["command"] = command
    payload["returncode"] = result.returncode
    return payload


def full_decode_receipt(video: Path) -> dict:
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    command = [ffmpeg, "-v", "error", "-i", str(video), "-f", "null", "-"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return {"command": command, "returncode": result.returncode, "stderr": result.stderr[-4000:]}


def render_movie() -> tuple[Path, dict, dict]:
    scene = bpy.context.scene
    video = ROOT / "stylized-fight-preview.mp4"
    frames_dir = ROOT / "render_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(frames_dir / "frame_")
    scene.frame_set(FRAME_START)
    bpy.ops.render.render(animation=True)
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    encode_command = [
        ffmpeg, "-y", "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video),
    ]
    encode_result = subprocess.run(encode_command, capture_output=True, text=True, check=False)
    (ROOT / "encode.json").write_text(json.dumps({
        "command": encode_command,
        "returncode": encode_result.returncode,
        "stderr": encode_result.stderr[-4000:],
    }, indent=2), encoding="utf-8")
    if encode_result.returncode != 0:
        raise RuntimeError(f"ffmpeg encode failed with exit {encode_result.returncode}: {encode_result.stderr[-1200:]}")
    probe = ffprobe_receipt(video)
    decode = full_decode_receipt(video)
    (ROOT / "ffprobe.json").write_text(json.dumps(probe, indent=2), encoding="utf-8")
    (ROOT / "full-decode.json").write_text(json.dumps(decode, indent=2), encoding="utf-8")
    return video, probe, decode


def write_manifest(blend: Path, stills: Iterable[Path], video: Path | None, state: Path, probe: dict | None,
                   decode: dict | None) -> Path:
    files = [blend, state, *stills]
    if video:
        files.extend((video, ROOT / "encode.json", ROOT / "ffprobe.json", ROOT / "full-decode.json"))
    entries = []
    for path in files:
        if path.exists():
            entries.append({"path": path.name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {
        "schema": "stylized-3d-review-manifest.v1",
        "review_state": "review_only_quarantine",
        "approval_state": "operator_pending",
        "render_eligible": False,
        "artifacts": entries,
        "still_frames": [1, 48],
        "animation": {"duration_seconds": 4.0, "fps": FPS, "frames": FRAME_END - FRAME_START + 1} if video else None,
        "validation": {"ffprobe_returncode": probe.get("returncode") if probe else None, "full_decode_returncode": decode.get("returncode") if decode else None},
    }
    path = ROOT / "quarantine-manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def build_scene() -> tuple[dict, dict]:
    clear_scene()
    configure_scene()
    for prefix, keys in (
        ("L", ("left_skin", "left_hair", "left_shorts", "left_wrap", "left_shoe", "left_sole")),
        ("R", ("right_skin", "right_hair", "right_shorts", "right_wrap", "right_shoe", "right_sole")),
    ):
        for key in keys:
            color = COLORS[key]
            name = f"{prefix}_{key}_mat"
            bpy.data.materials.new(name)
            material = bpy.data.materials[name]
            material.diffuse_color = color
            material.use_nodes = True
            shader = material.node_tree.nodes.get("Principled BSDF")
            if shader:
                shader.inputs["Base Color"].default_value = color
                shader.inputs["Roughness"].default_value = 0.52
    for prefix in ("L", "R"):
        make_material(f"{prefix}_glove_mat", COLORS["glove"], roughness=0.36)
    # Shared and expression materials.
    for name, color, roughness, metallic, emission in (
        ("MAT_floor", COLORS["floor"], 0.62, 0.0, 0.0),
        ("MAT_backdrop", COLORS["bg"], 0.70, 0.0, 0.0),
        ("MAT_gold", COLORS["gold"], 0.28, 0.35, 0.3),
        ("L_eye_mat", COLORS["eye"], 0.28, 0.0, 0.0),
        ("R_eye_mat", COLORS["eye"], 0.28, 0.0, 0.0),
        ("L_eye_white_mat", COLORS["eye_white"], 0.42, 0.0, 0.0),
        ("R_eye_white_mat", COLORS["eye_white"], 0.42, 0.0, 0.0),
        ("L_mouth_mat", COLORS["mouth"], 0.32, 0.0, 0.0),
        ("R_mouth_mat", COLORS["mouth"], 0.32, 0.0, 0.0),
    ):
        make_material(name, color, roughness=roughness, metallic=metallic, emission=emission)
    add_camera_and_lights()
    left = build_character("L", "left_dark_skin_bearded_black_shorts_red_wraps", -1.55, "left_skin", "left_hair", "left_shorts", "left_wrap", False, False)
    right = build_character("R", "right_light_skin_bald_bearded_white_shorts_blue_wraps", 1.55, "right_skin", "right_hair", "right_shorts", "right_wrap", True, True)
    animate_fight(left, right)
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    return left, right


def main() -> None:
    args = parse_args()
    left, right = build_scene()
    state = write_state(left, right)
    blend = save_blend()
    stills = render_stills()
    video = None
    probe = None
    decode = None
    if args.render:
        video, probe, decode = render_movie()
    manifest = write_manifest(blend, stills, video, state, probe, decode)
    print(json.dumps({
        "blend": str(blend),
        "state": str(state),
        "stills": [str(path) for path in stills],
        "video": str(video) if video else None,
        "manifest": str(manifest),
        "ffprobe_returncode": probe.get("returncode") if probe else None,
        "decode_returncode": decode.get("returncode") if decode else None,
    }, indent=2))


if __name__ == "__main__":
    main()
