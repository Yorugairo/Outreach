"""Bounded offline MPFB + Rigify import/pose/deformation smoke benchmark.

Run only through Blender with BLENDER_USER_RESOURCES set to this fixture's
profile. The script refuses to import either add-on if Blender's USER path is
outside that profile. It writes only the candidate report, .blend, and PNGs in
the T1 benchmark review directory.
"""

import addon_utils
import bpy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import traceback
from mathutils import Vector


SCRIPT = Path(__file__).resolve()
FIXTURE = SCRIPT.parent
REPO = SCRIPT.parents[6]
PROFILE = (FIXTURE / "profile").resolve()
POSE_FIXTURE = FIXTURE / "impact-pose-fixture.v1.json"
OUTPUT = (REPO / "content/video_engine/review/model-engines/benchmark-v1/baseline/candidates/mpfb-2.0.17").resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUTPUT / "inspection.json"
BLEND_PATH = OUTPUT / "mpfb-rigify-probe.blend"


def vec(v):
    return [round(float(x), 7) for x in v]


def mat(m):
    return [[round(float(x), 7) for x in row] for row in m]


def inside(path, parent):
    try:
        return os.path.commonpath([str(Path(path).resolve()), str(Path(parent).resolve())]).casefold() == str(Path(parent).resolve()).casefold()
    except (OSError, ValueError):
        return False


def evaluated_mesh(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    return points


def bounds(points):
    if not points:
        return None
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return {"min": vec(mins), "max": vec(maxs), "dimensions": vec([maxs[i] - mins[i] for i in range(3)])}


def object_bounds(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    return bounds(points)


def object_inventory(obj):
    data = {
        "name": obj.name,
        "type": obj.type,
        "hidden_viewport": bool(obj.hide_viewport),
        "hidden_render": bool(obj.hide_render),
        "parent": obj.parent.name if obj.parent else None,
        "location_world": vec(obj.matrix_world.translation),
        "rotation_euler": vec(obj.rotation_euler),
        "scale": vec(obj.scale),
        "bounds_world": object_bounds(obj),
        "modifiers": [{"name": m.name, "type": m.type, "object": getattr(m, "object", None).name if getattr(m, "object", None) else None} for m in obj.modifiers],
        "materials": [m.name if m else None for m in getattr(obj.data, "materials", [])],
    }
    if obj.type == "MESH":
        data.update({
            "vertices": len(obj.data.vertices),
            "polygons": len(obj.data.polygons),
            "shape_keys": [key.name for key in obj.data.shape_keys.key_blocks] if obj.data.shape_keys else [],
            "vertex_group_count": len(obj.vertex_groups),
        })
    return data


def armature_inventory(obj):
    bones = []
    for bone in obj.data.bones:
        world_head = obj.matrix_world @ bone.head_local
        world_tail = obj.matrix_world @ bone.tail_local
        pose_bone = obj.pose.bones.get(bone.name)
        bones.append({
            "name": bone.name,
            "parent": bone.parent.name if bone.parent else None,
            "use_deform": bool(bone.use_deform),
            "head_local": vec(bone.head_local),
            "tail_local": vec(bone.tail_local),
            "head_world_rest": vec(world_head),
            "tail_world_rest": vec(world_tail),
            "roll": round(float(bone.roll), 7) if hasattr(bone, "roll") else None,
            "roll_property_available": hasattr(bone, "roll"),
            "matrix_local": mat(bone.matrix_local),
            "constraints": [{"type": c.type, "target": c.target.name if getattr(c, "target", None) else None, "subtarget": getattr(c, "subtarget", None)} for c in pose_bone.constraints] if pose_bone else [],
        })
    return {
        "name": obj.name,
        "bone_count": len(obj.data.bones),
        "location_world": vec(obj.matrix_world.translation),
        "rotation_euler": vec(obj.rotation_euler),
        "scale": vec(obj.scale),
        "bones": bones,
    }


def pose_snapshot(rig, frame, selected_controls, character_meshes):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    pose = {}
    for name in selected_controls:
        pb = rig.pose.bones.get(name)
        if pb is None:
            continue
        pose[name] = {
            "location": vec(pb.location),
            "rotation_mode": pb.rotation_mode,
            "rotation_euler": vec(pb.rotation_euler),
            "rotation_quaternion": vec(pb.rotation_quaternion),
            "scale": vec(pb.scale),
            "matrix": mat(pb.matrix),
            "head_world": vec(rig.matrix_world @ pb.head),
            "tail_world": vec(rig.matrix_world @ pb.tail),
        }
    mesh_bounds = {obj.name: object_bounds(obj) for obj in character_meshes}
    foot_candidates = ("foot_fk.L", "foot_fk.R", "foot_ik.L", "foot_ik.R", "foot.L", "foot.R")
    feet = {}
    for name in foot_candidates:
        pb = rig.pose.bones.get(name)
        if pb is not None:
            feet[name] = {"head_world": vec(rig.matrix_world @ pb.head), "tail_world": vec(rig.matrix_world @ pb.tail)}
    min_mesh_z = min((item["min"][2] for item in mesh_bounds.values() if item), default=None)
    return {
        "frame": frame,
        "time_s": round((frame - 1) / bpy.context.scene.render.fps, 7),
        "root_location_world": vec(rig.matrix_world.translation),
        "root_heading_euler": vec(rig.rotation_euler),
        "controls": pose,
        "mesh_bounds_world": mesh_bounds,
        "ground_clearance_min_character_mesh_z_m": min_mesh_z,
        "semantic_foot_bones_world": feet,
    }


def setup_camera(target, front, side, scale):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("T1-neutral-world") if not scene.world else scene.world
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.16, 0.17, 0.19, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    try:
        scene.view_settings.look = "Medium High Contrast"
    except (TypeError, ValueError):
        # A color-management look is cosmetic; Blender builds expose different look enums.
        pass

    camera_data = bpy.data.cameras.new("T1-review-camera")
    camera = bpy.data.objects.new("T1-review-camera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(2.0, scale * 1.25)
    scene.camera = camera

    key_data = bpy.data.lights.new("T1-key", type="AREA")
    key = bpy.data.objects.new("T1-key", key_data)
    scene.collection.objects.link(key)
    key.location = target + front * (scale * 2.0) + side * (scale * 0.7) + Vector((0, 0, scale * 1.4))
    key_data.energy = 1150
    key_data.size = max(1.0, scale * 0.65)
    key.rotation_euler = (target - key.location).to_track_quat("-Z", "Y").to_euler()

    fill_data = bpy.data.lights.new("T1-fill", type="AREA")
    fill = bpy.data.objects.new("T1-fill", fill_data)
    scene.collection.objects.link(fill)
    fill.location = target - front * scale + side * scale + Vector((0, 0, scale * 0.7))
    fill_data.energy = 600
    fill_data.size = max(1.0, scale * 0.8)
    fill.rotation_euler = (target - fill.location).to_track_quat("-Z", "Y").to_euler()
    return camera


def render_view(camera, target, direction, scale, filepath):
    scene = bpy.context.scene
    camera.location = target + direction * (scale * 3.5)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(filepath)
    bpy.ops.render.render(write_still=True)


def main():
    user_path = Path(bpy.utils.resource_path("USER")).resolve()
    report = {
        "schema": "blender-motion-state-inspection.v1",
        "candidate": "MPFB 2.0.17 + Rigify",
        "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode("utf-8") if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),
        "user_resource_path": str(user_path),
        "profile_path": str(PROFILE),
        "profile_isolated": inside(user_path, PROFILE),
        "network_policy": "Blender was launched with --offline-mode; no provider/service calls are performed by this script.",
        "pose_fixture": json.loads(POSE_FIXTURE.read_text(encoding="utf-8")),
        "verdict": {"technical_import": "pending", "rig_generation": "pending", "rig_control_propagation": "pending", "skinning_deformation": "pending", "art_status": "not reviewed / not approved"},
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not inside(user_path, PROFILE):
        raise RuntimeError(f"Refusing add-on import: Blender USER resource path {user_path} is outside isolated profile {PROFILE}")

    addon_utils.modules_refresh()
    addon_utils.enable("rigify", default_set=True, persistent=False)
    addon_utils.modules_refresh()
    addon_utils.enable("bl_ext.user_default.mpfb", default_set=True, persistent=False)
    report["enabled_addons"] = [{"module": "rigify", "state": list(addon_utils.check("rigify"))}, {"module": "bl_ext.user_default.mpfb", "state": list(addon_utils.check("bl_ext.user_default.mpfb"))}]
    report["operators_present"] = {"create_human": hasattr(bpy.ops.mpfb, "create_human"), "add_rigify_rig": hasattr(bpy.ops.mpfb, "add_rigify_rig")}
    if not report["operators_present"]["create_human"] or not report["operators_present"]["add_rigify_rig"]:
        raise RuntimeError("MPFB operators did not register after extension import")

    scene = bpy.context.scene
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 96
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    default_cube = bpy.data.objects.get("Cube")
    if default_cube is not None:
        default_cube.hide_render = True
        default_cube.hide_viewport = True
    report["default_cube_hidden"] = bool(default_cube and default_cube.hide_render and default_cube.hide_viewport)
    bpy.ops.mpfb.create_human()
    base_mesh = bpy.context.view_layer.objects.active
    if base_mesh is None or base_mesh.type != "MESH":
        raise RuntimeError("MPFB create_human completed without an active mesh")
    report["created_base_mesh"] = base_mesh.name
    report["pre_rig_scene_objects"] = [object_inventory(obj) for obj in bpy.data.objects]

    bpy.ops.mpfb.add_rigify_rig()
    armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError("MPFB did not create any armature object")
    rig = max(armatures, key=lambda obj: len(obj.data.bones))
    report["rig_objects"] = [armature_inventory(obj) for obj in armatures]
    report["selected_rig"] = rig.name
    report["selected_rig_bone_count"] = len(rig.data.bones)
    report["scene_objects_after_rig"] = [object_inventory(obj) for obj in bpy.data.objects]

    candidate_controls = report["pose_fixture"]["pose_probe"]["control_candidates"]
    selected_controls = [name for name in candidate_controls if rig.pose.bones.get(name)]
    report["controls_found"] = selected_controls
    if not selected_controls:
        upper_arm_names = [pb.name for pb in rig.pose.bones if "upper_arm" in pb.name.lower()]
        report["upper_arm_bone_names"] = upper_arm_names
        raise RuntimeError("No expected Rigify FK arm controls found")

    right_control = "upper_arm_fk.R" if "upper_arm_fk.R" in selected_controls else selected_controls[0]
    left_control = "upper_arm_fk.L" if "upper_arm_fk.L" in selected_controls else None
    arm_switches = {}
    for side in ("R", "L"):
        parent = rig.pose.bones.get(f"upper_arm_parent.{side}")
        if parent is None or "IK_FK" not in parent:
            raise RuntimeError(f"Missing Rigify upper_arm_parent.{side} IK_FK switch")
        parent["IK_FK"] = 1.0
        parent.keyframe_insert(data_path='["IK_FK"]', frame=1, group="T1 diagnostic controls")
        arm_switches[parent.name] = float(parent["IK_FK"])
    report["arm_ik_fk_switches_for_fk_pose"] = arm_switches
    angle = float(report["pose_fixture"]["pose_probe"]["local_rotation_probe_rad"])
    for name in set(filter(None, [right_control, left_control])):
        pb = rig.pose.bones[name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0.0, 0.0, 0.0)
        pb.keyframe_insert(data_path="rotation_euler", frame=1, group="T1 diagnostic controls")
    rig.pose.bones[right_control].rotation_euler.z = angle
    rig.pose.bones[right_control].keyframe_insert(data_path="rotation_euler", frame=27, group="T1 diagnostic controls")
    rig.pose.bones[right_control].rotation_euler.z = angle * 1.1
    rig.pose.bones[right_control].keyframe_insert(data_path="rotation_euler", frame=28, group="T1 diagnostic controls")
    if left_control:
        rig.pose.bones[left_control].rotation_euler.z = angle
        rig.pose.bones[left_control].keyframe_insert(data_path="rotation_euler", frame=50, group="T1 diagnostic controls")
        rig.pose.bones[left_control].rotation_euler.z = angle * 0.7
        rig.pose.bones[left_control].keyframe_insert(data_path="rotation_euler", frame=54, group="T1 diagnostic controls")
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    weighted_meshes = [obj for obj in meshes if any(mod.type == "ARMATURE" and mod.object == rig for mod in obj.modifiers)]
    report["weighted_meshes_for_selected_rig"] = [obj.name for obj in weighted_meshes]
    if not weighted_meshes:
        raise RuntimeError("No body mesh has an Armature modifier pointing to the generated Rigify rig")
    if base_mesh not in weighted_meshes:
        raise RuntimeError("Created Human mesh is not weighted to the generated Rigify rig")
    deform_bone = rig.pose.bones.get("DEF-upper_arm.R")
    if deform_bone is None:
        raise RuntimeError("Generated Rigify rig has no DEF-upper_arm.R bone")

    sampled_frames = [1, 27, 28, 41, 50, 54, 85]
    neutral = {}
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    deform_tail_neutral = rig.matrix_world @ deform_bone.tail
    for obj in weighted_meshes:
        neutral[obj.name] = evaluated_mesh(obj)
    report["sampled_motion_states"] = [pose_snapshot(rig, frame, selected_controls, weighted_meshes) for frame in sampled_frames]
    bpy.context.scene.frame_set(27)
    bpy.context.view_layer.update()
    deform_tail_posed = rig.matrix_world @ deform_bone.tail
    deform_tail_displacement = (deform_tail_posed - deform_tail_neutral).length
    report["deform_bone_motion_frame_1_to_27"] = {
        "bone": deform_bone.name,
        "neutral_tail_world": vec(deform_tail_neutral),
        "posed_tail_world": vec(deform_tail_posed),
        "tail_displacement_world_m": round(deform_tail_displacement, 7),
    }
    deformation = {}
    for obj in weighted_meshes:
        before = neutral[obj.name]
        after = evaluated_mesh(obj)
        pairs = zip(before, after)
        displacements = [(b - a).length for a, b in pairs]
        changed = [d for d in displacements if d > 1e-5]
        deformation[obj.name] = {
            "vertex_count": len(after),
            "changed_vertex_count_gt_1e-5": len(changed),
            "changed_vertex_ratio": round(len(changed) / max(1, len(after)), 7),
            "max_displacement_world_m": round(max(displacements, default=0.0), 7),
            "mean_displacement_world_m": round(sum(displacements) / max(1, len(displacements)), 7),
            "neutral_bounds_world": bounds(before),
            "posed_bounds_world": bounds(after),
        }
    report["deformation_measurements_frame_1_to_27"] = deformation
    report["verdict"]["technical_import"] = "pass" if meshes else "fail"
    report["verdict"]["rig_generation"] = "pass" if len(rig.data.bones) > 20 else "fail"
    report["verdict"]["rig_control_propagation"] = "pass" if deform_tail_displacement > 1e-5 else "fail"
    report["verdict"]["skinning_deformation"] = "pass" if deformation[base_mesh.name]["changed_vertex_count_gt_1e-5"] > 0 else "fail"

    all_points = [point for obj in weighted_meshes for point in evaluated_mesh(obj)]
    all_bounds = bounds(all_points)
    report["character_bounds_world"] = all_bounds
    if all_bounds:
        lo, hi = Vector(all_bounds["min"]), Vector(all_bounds["max"])
        target = (lo + hi) * 0.5
        height = max(hi.z - lo.z, 0.1)
    else:
        target, height = Vector((0, 0, 1)), 2.0

    bones = rig.data.bones
    left_name = next((name for name in ("shoulder.L", "upper_arm.L", "upper_arm_fk.L") if bones.get(name)), None)
    right_name = next((name for name in ("shoulder.R", "upper_arm.R", "upper_arm_fk.R") if bones.get(name)), None)
    if left_name and right_name:
        side = (rig.matrix_world @ bones[right_name].head_local) - (rig.matrix_world @ bones[left_name].head_local)
    else:
        side = rig.matrix_world.to_3x3() @ Vector((1, 0, 0))
    if side.length < 1e-6:
        side = Vector((1, 0, 0))
    side.normalize()
    up = Vector((0, 0, 1))
    front = side.cross(up)
    if front.length < 1e-6:
        front = Vector((0, -1, 0))
    front.normalize()
    report["orientation"] = {
        "world_up": [0, 0, 1],
        "side_vector_from_bilateral_bone_heads": vec(side),
        "front_estimate_cross_side_x_world_up": vec(front),
        "source_bone_pair": [left_name, right_name],
        "front_direction_visual_confirmation": "pending two-sided render review",
        "ground_clearance_neutral_m": deformation[base_mesh.name]["neutral_bounds_world"]["min"][2],
        "ground_clearance_posed_m": deformation[base_mesh.name]["posed_bounds_world"]["min"][2],
        "ground_contact_scope": "body bounding-box floor clearance only; no foot-lock, fall, or fight-contact claim",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    camera = setup_camera(target, front, side, height)
    report["render_settings"] = {"engine": bpy.context.scene.render.engine, "look": bpy.context.scene.view_settings.look}
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    bpy.context.scene.frame_set(27)
    bpy.context.view_layer.update()
    render_view(camera, target, front, height, OUTPUT / "posed-from-forward-estimate.png")
    render_view(camera, target, -front, height, OUTPUT / "posed-from-opposite-estimate.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    report["artifacts"] = {
        "blend": str(BLEND_PATH),
        "blend_sha256": hashlib.sha256(BLEND_PATH.read_bytes()).hexdigest(),
        "renders": [str(OUTPUT / "posed-from-forward-estimate.png"), str(OUTPUT / "posed-from-opposite-estimate.png")],
        "inspection": str(REPORT_PATH),
    }
    report["verdict"]["technical_candidate"] = "pass" if all(report["verdict"][key] == "pass" for key in ("technical_import", "rig_generation", "rig_control_propagation", "skinning_deformation")) else "fail"
    report["verdict"]["art_status"] = "technical prototype only; not reviewed, not approved, no character likeness claim"
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")


try:
    main()
except Exception as exc:
    previous = json.loads(REPORT_PATH.read_text(encoding="utf-8")) if REPORT_PATH.exists() else {}
    previous["fatal_error"] = {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}
    previous.setdefault("verdict", {})["technical_candidate"] = "fail"
    previous.setdefault("verdict", {})["art_status"] = "not reviewed / not approved"
    REPORT_PATH.write_text(json.dumps(previous, indent=2), encoding="utf-8")
    raise
