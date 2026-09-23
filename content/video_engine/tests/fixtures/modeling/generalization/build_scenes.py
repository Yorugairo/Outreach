"""Build offline, editable T4c diagnostic Blender scenes and portrait views."""

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args_after_separator():
    return sys.argv[sys.argv.index("--") + 1:]


def material(name, color, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = 0.55
    return mat


def box(name, location, scale, mat, bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted_Normals", "WEIGHTED_NORMAL")
    return obj


def empty(name, location, parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_type = "ARROWS"
    obj.empty_display_size = 0.15
    obj.parent = parent
    obj.location = location
    return obj


def aim(camera, target):
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def camera_at(location, target):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = "Diagnostic_Camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 3.25
    aim(camera, target)
    bpy.context.scene.camera = camera
    return camera


def light(name, location, energy, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 0.6))


def common_scene(kind):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene["fixture_kind"] = kind
    scene["status"] = "diagnostic_only"
    scene["art_approval"] = "not_approved"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 540
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.16, 0.20, 0.27)
    scene.frame_start = 1
    scene.frame_end = 25
    light("Key_Softbox", (1.8, -2.5, 4.0), 750, 4.0)
    light("Rim_Softbox", (-2.5, 1.5, 3.5), 450, 3.0)


def make_prop():
    common_scene("hinged_prop")
    teal = material("Enamel_Teal", (0.06, 0.38, 0.42), 0.2)
    cream = material("Ceramic_Cream", (0.83, 0.76, 0.58))
    bronze = material("Hinge_Bronze", (0.55, 0.34, 0.12), 0.65)
    floor = material("Backdrop_Indigo", (0.08, 0.12, 0.20))
    base = box("Prop_Base", (0, 0, 0.22), (1.5, 0.82, 0.34), teal)
    base["semantic_role"] = "prop_body"
    hinge = empty("Hinge_Pivot", (0, 0.39, 0.40))
    hinge["semantic_role"] = "articulation"
    hinge["articulation_id"] = "lid_hinge"
    lid = box("Prop_Lid", (0, -0.39, 0.05), (1.5, 0.82, 0.10), cream)
    lid.parent = hinge
    lid.location = (0, -0.39, 0.05)
    lid["semantic_role"] = "hinged_panel"
    # Axis is parallel to X, crossing the rear edge of the box.
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.055, depth=1.55,
                                        location=(0, 0.39, 0.40), rotation=(0, math.pi / 2, 0))
    pin = bpy.context.object
    pin.name = "Hinge_Pin"
    pin.data.materials.append(bronze)
    socket = empty("Socket_Grip", (0, -0.43, 0.08), parent=base)
    socket["semantic_role"] = "attachment_socket"
    socket["socket_id"] = "grip_socket"
    box("Latch", (0, -0.47, 0.31), (0.28, 0.08, 0.10), bronze)
    box("Display_Platform", (0, 0, -0.06), (2.05, 1.38, 0.10), floor)
    camera_at((2.4, -3.4, 2.25), (0, 0, 0.46))
    for frame, angle in ((1, 0.0), (25, -1.30)):
        hinge.rotation_euler.x = angle
        hinge.keyframe_insert(data_path="rotation_euler", frame=frame)
    bpy.context.scene.frame_set(1)


def make_environment():
    common_scene("layered_environment")
    stone = material("Floor_Stone", (0.24, 0.31, 0.34))
    blue = material("Midground_Blue", (0.10, 0.32, 0.52))
    amber = material("Background_Amber", (0.65, 0.39, 0.16))
    dark = material("Foreground_Ink", (0.055, 0.08, 0.14))
    floor = box("Floor_Collision", (0, 0, -0.05), (3.4, 3.6, 0.10), stone, 0)
    floor["semantic_role"] = "collision_surface"
    floor["surface_id"] = "floor"
    floor["collision_role"] = "solid"
    floor.modifiers.new("Floor_Collision", "COLLISION")
    back = box("Background_Wall", (0, 1.55, 1.15), (3.4, 0.12, 2.3), amber)
    back["layer_role"] = "background"
    back["depth_y_m"] = 1.55
    mid = box("Midground_Dais", (0.25, 0.48, 0.24), (1.72, 0.84, 0.48), blue)
    mid["layer_role"] = "midground"
    mid["depth_y_m"] = 0.48
    for index, x in enumerate((-1.12, 1.12)):
        obj = box(f"Midground_Column_{index+1}", (x, 0.84, 0.86), (0.22, 0.20, 1.72), blue)
        obj["layer_role"] = "midground"
    occluder = box("Foreground_Occluder", (-0.83, -1.12, 0.94),
                   (0.34, 0.24, 1.88), dark)
    occluder["layer_role"] = "foreground_occluder"
    occluder["depth_y_m"] = -1.12
    box("Foreground_Crossbeam", (0, -1.12, 1.94), (2.60, 0.24, 0.22), dark)["layer_role"] = "foreground_occluder"
    camera = camera_at((1.0, -4.3, 2.1), (0, 0.1, 0.9))
    camera.data.ortho_scale = 6.25
    bpy.context.scene.frame_end = 1


def render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("prop", "environment"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--renders", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args(args_after_separator())
    for path in (args.output, args.renders, args.result):
        if not path.is_absolute():
            raise ValueError(f"absolute output path required: {path}")
    if bpy.app.version_string != "5.2.2 LTS":
        raise RuntimeError(f"expected pinned Blender 5.2.2 LTS, got {bpy.app.version_string}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.renders.mkdir(parents=True, exist_ok=True)
    args.result.parent.mkdir(parents=True, exist_ok=True)
    if args.kind == "prop":
        make_prop()
    else:
        make_environment()
    scene = bpy.context.scene
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))
    if args.kind == "prop":
        for frame, name in ((1, "closed"), (25, "open")):
            scene.frame_set(frame)
            render(scene, args.renders / f"hinged-prop-{name}.png")
        scene.frame_set(1)
    else:
        render(scene, args.renders / "environment-three-quarter.png")
        camera = scene.camera
        camera.location = (0, -4.3, 1.8)
        aim(camera, (0, 0.1, 0.9))
        render(scene, args.renders / "environment-front.png")
    args.result.write_text(json.dumps({"kind": args.kind, "blender_version": bpy.app.version_string,
                                      "source": str(args.output), "renders": str(args.renders)}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
