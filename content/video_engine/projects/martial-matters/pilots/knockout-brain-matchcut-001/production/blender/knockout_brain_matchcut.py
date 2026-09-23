"""Build a review-only stylized 3D head/brain knockout insert.

Run with Blender 5.2 (the script imports ``bpy`` and is not a normal Python
program)::

    blender.exe --background --factory-startup --python knockout_brain_matchcut.py -- --render

The scene is deliberately self-contained and source-free.  It produces a
three-second 720x1280/30fps H.264 insert, representative PNGs, the source
blend, a structured motion-state receipt, and a quarantine manifest.  The
asset is a diagnostic editorial insert, not a medical visualization or a
publication-ready claim.
"""
from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore


ROOT = Path(__file__).resolve().parent
FPS = 30
FRAME_START = 1
FRAME_END = 90
WIDTH = 720
HEIGHT = 1280
SAMPLES = (1, 12, 24, 36, 48, 60, 75, 90)
HEAD_CENTER = Vector((0.0, 0.0, 3.35))

COLORS = {
    "void": (0.006, 0.011, 0.024, 1.0),
    "void_blue": (0.012, 0.035, 0.075, 1.0),
    "shell": (0.12, 0.52, 0.72, 1.0),
    "shell_edge": (0.18, 0.76, 1.0, 1.0),
    "brain_left": (0.95, 0.20, 0.34, 1.0),
    "brain_right": (1.0, 0.34, 0.36, 1.0),
    "brain_ridge": (1.0, 0.30, 0.22, 1.0),
    "brain_shadow": (0.30, 0.025, 0.065, 1.0),
    "white": (0.82, 0.93, 1.0, 1.0),
    "cyan": (0.10, 0.82, 1.0, 1.0),
    "magenta": (1.0, 0.15, 0.42, 1.0),
}


def script_args() -> list[str]:
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1 :]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--samples", action="store_true", help="build the blend and render representative stills")
    modes.add_argument("--render", action="store_true", help="build, sample, and render the three-second movie")
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
        bpy.data.fonts,
    ):
        for block in list(collection):
            if block.users == 0:
                collection.remove(block)


def set_surface_render_method(material, method: str = "BLENDED") -> None:
    # Blender 4.2+ renamed Eevee's transparency control.  Keep the fallback
    # for older local builds so the work order remains reproducible.
    if hasattr(material, "surface_render_method"):
        try:
            material.surface_render_method = method
            return
        except Exception:
            pass
    if hasattr(material, "blend_method"):
        try:
            material.blend_method = "BLEND"
            material.use_screen_refraction = True
        except Exception:
            pass


def make_material(
    name: str,
    rgba: tuple[float, float, float, float],
    *,
    alpha: float = 1.0,
    metallic: float = 0.0,
    roughness: float = 0.38,
    emission_strength: float = 0.0,
    transmission: float = 0.0,
    transparent_mix: bool = False,
) :
    material = bpy.data.materials.new(name)
    material.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    if transparent_mix:
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        emission = nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
        emission.inputs["Strength"].default_value = max(0.1, emission_strength)
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = alpha
        links.new(transparent.outputs["BSDF"], mix.inputs[1])
        links.new(emission.outputs["Emission"], mix.inputs[2])
        links.new(mix.outputs["Shader"], output.inputs["Surface"])
    else:
        shader = nodes.new("ShaderNodeBsdfPrincipled")
        shader.inputs["Base Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic
        if "Alpha" in shader.inputs:
            shader.inputs["Alpha"].default_value = alpha
        if "Transmission Weight" in shader.inputs:
            shader.inputs["Transmission Weight"].default_value = transmission
        elif "Transmission" in shader.inputs:
            shader.inputs["Transmission"].default_value = transmission
        if "IOR" in shader.inputs:
            shader.inputs["IOR"].default_value = 1.45
        if "Emission Color" in shader.inputs:
            shader.inputs["Emission Color"].default_value = (rgba[0], rgba[1], rgba[2], 1.0)
        if "Emission Strength" in shader.inputs:
            shader.inputs["Emission Strength"].default_value = emission_strength
        links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    if alpha < 0.999:
        set_surface_render_method(material)
        if hasattr(material, "use_transparency_overlap"):
            material.use_transparency_overlap = False
    return material


def smooth_mesh(obj) -> None:
    if obj.type != "MESH":
        return
    for polygon in obj.data.polygons:
        polygon.use_smooth = True


def add_uv_sphere(name: str, location: tuple[float, float, float], scale: tuple[float, float, float], material,
                  segments: int = 48, rings: int = 32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    obj.data.materials.append(material)
    return obj


def add_ico_sphere(name: str, location: tuple[float, float, float], scale: tuple[float, float, float], material,
                   subdivisions: int = 3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    obj.data.materials.append(material)
    return obj


def add_cylinder(name: str, location: tuple[float, float, float], radius: float, depth: float, material,
                 vertices: int = 32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    smooth_mesh(obj)
    obj.data.materials.append(material)
    return obj


def add_cone(name: str, location: tuple[float, float, float], radius1: float, radius2: float, depth: float,
             rotation: tuple[float, float, float], material, vertices: int = 32):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    smooth_mesh(obj)
    obj.data.materials.append(material)
    return obj


def add_torus(name: str, location: tuple[float, float, float], major_radius: float, minor_radius: float,
              material, rotation: tuple[float, float, float] = (0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=64,
        minor_segments=12,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth_mesh(obj)
    obj.data.materials.append(material)
    return obj


def add_curve(name: str, points: list[tuple[float, float, float]], material, bevel_depth: float = 0.035,
              parent=None):
    curve_data = bpy.data.curves.new(name, type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 16
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 3
    curve_data.fill_mode = "FULL"
    spline = curve_data.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    if parent is not None:
        parent_keep_world(obj, parent)
    return obj


def add_wireframe(source, name: str, material, thickness: float = 0.018):
    wire = source.copy()
    wire.data = source.data.copy()
    wire.name = name
    bpy.context.collection.objects.link(wire)
    wire.modifiers.new("silhouette_wire", "WIREFRAME").thickness = thickness
    wire.data.materials.clear()
    wire.data.materials.append(material)
    return wire


def parent_keep_world(obj, parent) -> None:
    """Parent an already placed object without changing its world pose."""
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def look_at(obj, target: Vector) -> None:
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (target - obj.location).to_track_quat("-Z", "Y")


def add_area_light(name: str, location: tuple[float, float, float], energy: float, size: float,
                   color: tuple[float, float, float], target=HEAD_CENTER):
    light_data = bpy.data.lights.new(name, type="AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light_data.color = color
    obj = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def add_point_light(name: str, location: tuple[float, float, float], energy: float,
                    color: tuple[float, float, float]):
    light_data = bpy.data.lights.new(name, type="POINT")
    light_data.energy = energy
    light_data.color = color
    light_data.shadow_soft_size = 1.5
    obj = bpy.data.objects.new(name, light_data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return obj


def keyframe_linear(obj) -> None:
    if not obj.animation_data or not obj.animation_data.action:
        return
    curves = getattr(obj.animation_data.action, "fcurves", None)
    if curves is None:
        curves = []
        action = obj.animation_data.action
        for layer in getattr(action, "layers", []):
            for strip in getattr(layer, "strips", []):
                for bag in getattr(strip, "channelbags", []):
                    curves.extend(getattr(bag, "fcurves", []))
    for curve in curves:
        for point in curve.keyframe_points:
            point.interpolation = "BEZIER"
            point.handle_left_type = "AUTO"
            point.handle_right_type = "AUTO"


def key_transform(obj, frame: int, location: tuple[float, float, float], rotation: tuple[float, float, float]):
    obj.rotation_mode = "XYZ"
    obj.location = location
    obj.rotation_euler = rotation
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def configure_render(scene) -> None:
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
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.use_file_extension = True
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background is not None:
        background.inputs["Color"].default_value = COLORS["void"]
        background.inputs["Strength"].default_value = 0.035
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    eevee = getattr(scene, "eevee", None)
    if eevee is not None:
        if hasattr(eevee, "taa_render_samples"):
            eevee.taa_render_samples = 16
        if hasattr(eevee, "use_gtao"):
            eevee.use_gtao = True
        if hasattr(eevee, "gtao_distance"):
            eevee.gtao_distance = 3.0
        if hasattr(eevee, "gtao_factor"):
            eevee.gtao_factor = 1.25

    # A restrained bloom/glow pass keeps the electric rim legible at phone size.
    scene.use_nodes = True
    compositor_tree = getattr(scene, "node_tree", None)
    # Blender 5.2 moved the compositor tree behind ``compositing_node_group``;
    # the direct Eevee emission materials remain the reliable glow path when
    # that new tree is unavailable in background mode.
    if compositor_tree is None:
        return
    nodes = compositor_tree.nodes
    links = compositor_tree.links
    nodes.clear()
    render_layers = nodes.new("CompositorNodeRLayers")
    glare = nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.quality = "LOW"
    glare.threshold = 1.0
    glare.size = 6
    glare.mix = -0.86
    composite = nodes.new("CompositorNodeComposite")
    links.new(render_layers.outputs["Image"], glare.inputs["Image"])
    links.new(glare.outputs["Image"], composite.inputs["Image"])


def brain_front_y(x: float, z: float) -> float:
    nx = (x / 1.70) ** 2
    nz = ((z - 3.42) / 1.53) ** 2
    inside = max(0.07, 1.0 - nx - nz)
    return -0.30 - 1.06 * math.sqrt(inside)


def add_brain_ridges(brain_root, mats: dict) -> None:
    bright = mats["brain_ridge"]
    shadow = mats["brain_shadow"]
    # Horizontal folds read as convolutions at portrait resolution.  Their
    # y-coordinate follows the front ellipsoid so they sit on the visible lobe.
    for row in range(8):
        z0 = 2.52 + row * 0.245
        points = []
        for i in range(13):
            x = -1.52 + i * 0.253
            z = z0 + 0.075 * math.sin(i * 1.48 + row * 0.63)
            y = brain_front_y(x, z) - 0.026
            points.append((x, y, z))
        add_curve(f"brain_fold_h_{row:02d}", points, bright, bevel_depth=0.037, parent=brain_root)

    for col in range(5):
        x0 = -1.30 + col * 0.65
        points = []
        for i in range(9):
            z = 2.67 + i * 0.19
            x = x0 + 0.095 * math.sin(i * 1.6 + col * 0.77)
            y = brain_front_y(x, z) - 0.043
            points.append((x, y, z))
        add_curve(f"brain_fold_v_{col:02d}", points, shadow, bevel_depth=0.023, parent=brain_root)

    # Short serpentine folds keep the two lobes organic without the concentric
    # ring pattern that reads like cartoon eyes at phone scale.
    for lobe, cx in (("left", -0.78), ("right", 0.78)):
        for ridge in range(4):
            points = []
            z0 = 2.77 + ridge * 0.39
            for i in range(9):
                t = -1.0 + i / 4.0
                x = cx + 0.58 * t
                z = z0 + 0.10 * math.sin(i * 1.55 + ridge * 0.70)
                y = brain_front_y(x, z) - 0.055
                points.append((x, y, z))
            add_curve(f"brain_serpentine_{lobe}_{ridge}", points, bright, bevel_depth=0.029, parent=brain_root)

    add_curve(
        "brain_midline",
        [(0.0, -1.37, 2.25), (0.03, -1.39, 2.90), (-0.02, -1.39, 3.50), (0.04, -1.36, 4.14), (0.0, -1.30, 4.78)],
        shadow,
        bevel_depth=0.030,
        parent=brain_root,
    )


def add_face_details(head_root, mats: dict):
    # The face points left.  These restrained cyan contours make the rotation
    # readable without introducing gore or a realistic injury depiction.
    outline = add_curve(
        "face_jaw_contour",
        [(-1.90, -1.12, 3.15), (-2.13, -1.02, 2.85), (-1.67, -1.13, 2.13), (-0.60, -1.20, 1.72), (0.45, -1.10, 1.78)],
        mats["shell_edge"],
        bevel_depth=0.024,
        parent=head_root,
    )
    outline["semantic_role"] = "stylized_face_contour"

    # Eye socket: dark center plus a thin rim, intentionally non-graphic.
    socket = add_torus("eye_socket", (-1.13, -1.58, 3.85), 0.25, 0.026, mats["shell_edge"], rotation=(math.pi / 2.0, 0.0, 0.0), scale=(1.0, 0.72, 1.0))
    parent_keep_world(socket, head_root)
    eye = add_uv_sphere("eye_socket_dark", (-1.13, -1.61, 3.85), (0.11, 0.055, 0.11), mats["void"], segments=24, rings=16)
    parent_keep_world(eye, head_root)
    eye.hide_render = True

    # Ear ring and nose bridge support the silhouette from the 3/4 camera.
    ear = add_torus("ear_contour", (1.52, -0.18, 3.18), 0.38, 0.032, mats["shell_edge"], rotation=(math.pi / 2.0, 0.0, 0.0), scale=(1.0, 0.70, 1.0))
    parent_keep_world(ear, head_root)
    bridge = add_curve(
        "nose_bridge_contour",
        [(-1.10, -1.48, 4.08), (-1.46, -1.49, 3.72), (-1.78, -1.38, 3.30), (-2.12, -1.18, 3.07)],
        mats["shell_edge"],
        bevel_depth=0.023,
        parent=head_root,
    )
    bridge["semantic_role"] = "stylized_nose_contour"


def build_scene() -> dict:
    clear_scene()
    scene = bpy.context.scene
    configure_render(scene)
    mats = {
        "void": make_material("mat_void", COLORS["void"], roughness=0.92),
        "backdrop": make_material("mat_backdrop", COLORS["void_blue"], roughness=0.85),
        "shell": make_material("mat_head_shell", COLORS["shell"], alpha=0.11, roughness=0.22, emission_strength=0.32, transmission=0.04, transparent_mix=True),
        "shell_edge": make_material("mat_shell_edge", COLORS["shell_edge"], alpha=0.62, roughness=0.26, emission_strength=0.82),
        "shell_grid": make_material("mat_shell_grid", COLORS["shell"], alpha=0.24, roughness=0.46, emission_strength=0.08),
        "brain_left": make_material("mat_brain_left", COLORS["brain_left"], roughness=0.30, emission_strength=0.34),
        "brain_right": make_material("mat_brain_right", COLORS["brain_right"], roughness=0.30, emission_strength=0.34),
        "brain_ridge": make_material("mat_brain_ridge", COLORS["brain_ridge"], roughness=0.28, emission_strength=0.16),
        "brain_shadow": make_material("mat_brain_shadow", COLORS["brain_shadow"], roughness=0.30, emission_strength=0.10),
        "cyan": make_material("mat_cyan", COLORS["cyan"], roughness=0.20, emission_strength=2.4),
        "magenta": make_material("mat_magenta", COLORS["magenta"], roughness=0.22, emission_strength=2.2),
        "white": make_material("mat_white", COLORS["white"], roughness=0.35, emission_strength=1.2),
    }

    # A deep blue wall and two low-contrast orbit rings establish scale without
    # competing with the anatomical insert.
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(0.0, 3.0, 3.4), rotation=(math.pi / 2.0, 0.0, 0.0))
    backdrop = bpy.context.object
    backdrop.name = "dark_backdrop"
    backdrop.data.materials.append(mats["backdrop"])
    # The anatomy owns the frame; broad orbit rings were intentionally omitted
    # after the representative review because they competed with the profile.

    head_root = bpy.data.objects.new("HEAD_ROOT__punch_rotation", None)
    bpy.context.collection.objects.link(head_root)
    brain_root = bpy.data.objects.new("BRAIN_ROOT__delayed_lag_recoil", None)
    bpy.context.collection.objects.link(brain_root)
    # Both roots pivot at the anatomical centre.  Keeping this explicit avoids
    # a world-origin rotation making the brain appear to eject from the skull.
    head_root.location = HEAD_CENTER
    brain_root.location = HEAD_CENTER
    parent_keep_world(brain_root, head_root)
    head_root["semantic_role"] = "outer_head_skull_silhouette"
    brain_root["semantic_role"] = "inner_brain_delayed_recoil"

    # Head silhouette: shell + jaw/neck + face profile.  The shell remains
    # translucent so the coral brain and bright folds read through it.
    cranium = add_uv_sphere("head_shell_translucent_cranium", (0.0, 0.0, 3.55), (2.20, 1.62, 2.27), mats["shell"])
    parent_keep_world(cranium, head_root)
    cranium["semantic_role"] = "semi_transparent_skull_shell"
    cranium_wire = add_wireframe(cranium, "head_shell_edge_grid", mats["shell_grid"], thickness=0.006)
    parent_keep_world(cranium_wire, head_root)
    cranium_wire.hide_render = True
    jaw = add_uv_sphere("head_shell_translucent_jaw", (-0.24, 0.0, 2.10), (1.48, 1.42, 1.24), mats["shell"])
    parent_keep_world(jaw, head_root)
    jaw_wire = add_wireframe(jaw, "jaw_shell_edge_grid", mats["shell_grid"], thickness=0.005)
    parent_keep_world(jaw_wire, head_root)
    jaw_wire.hide_render = True
    neck = add_cylinder("neck_shell_translucent", (0.24, 0.08, 0.82), 0.72, 1.65, mats["shell"], vertices=32)
    parent_keep_world(neck, head_root)
    neck_wire = add_wireframe(neck, "neck_shell_edge_grid", mats["shell_grid"], thickness=0.004)
    parent_keep_world(neck_wire, head_root)
    neck_wire.hide_render = True
    nose = add_cone("nose_shell_profile", (-2.00, -0.02, 3.18), 0.46, 0.075, 0.78, (0.0, math.pi / 2.0, 0.0), mats["shell_edge"])
    parent_keep_world(nose, head_root)
    add_face_details(head_root, mats)
    outline_points = []
    for i in range(25):
        theta = (math.tau * i) / 24.0
        x = 2.16 * math.cos(theta)
        z = 3.55 + 2.22 * math.sin(theta)
        outline_points.append((x, -1.64, z))
    add_curve("skull_silhouette_contour", outline_points, mats["shell_edge"], bevel_depth=0.030, parent=head_root)

    # Brain lobes are deliberately stylized rather than medical.  The clear
    # hemispheric color split makes the lag relative to the shell easy to read.
    lobe_left = add_uv_sphere("brain_left_coral_lobe", (-0.76, -0.25, 3.43), (0.78, 0.86, 1.25), mats["brain_left"])
    parent_keep_world(lobe_left, brain_root)
    lobe_right = add_uv_sphere("brain_right_coral_lobe", (0.76, -0.25, 3.43), (0.78, 0.86, 1.25), mats["brain_right"])
    parent_keep_world(lobe_right, brain_root)
    brain_glow = add_ico_sphere("brain_soft_coral_glow", (0.0, -0.23, 3.43), (1.78, 1.14, 1.62), mats["brain_ridge"], subdivisions=3)
    # The glow object is intentionally low-alpha through a dedicated material;
    # keeping it behind the ridges gives the folds a clean bright edge.
    brain_glow.data.materials.clear()
    brain_glow.data.materials.append(make_material("mat_brain_glow", COLORS["brain_ridge"], alpha=0.09, roughness=0.25, emission_strength=0.8))
    parent_keep_world(brain_glow, brain_root)
    brain_glow.hide_render = True
    add_brain_ridges(brain_root, mats)

    # Punch direction and recoil accents: small non-gore arcs stay behind the
    # head and only appear briefly around the first directional change.
    impact_arc = add_curve(
        "impact_direction_arc",
        [(-3.20, 1.85, 5.65), (-2.72, 1.78, 5.96), (-2.06, 1.72, 6.05), (-1.53, 1.66, 5.92)],
        mats["magenta"],
        bevel_depth=0.038,
    )
    impact_arc["semantic_role"] = "non_gore_punch_direction_marker"
    impact_arc.hide_render = True
    recoil_arc = add_curve(
        "delayed_recoil_arc",
        [(1.56, 1.74, 5.94), (2.10, 1.70, 6.05), (2.78, 1.65, 5.88), (3.26, 1.60, 5.56)],
        mats["cyan"],
        bevel_depth=0.030,
    )
    recoil_arc["semantic_role"] = "brain_recoil_direction_marker"
    recoil_arc.hide_render = True

    # Static camera-facing labels are not attached to the moving head, so they
    # remain legible during the push.  STYLIZED REPLAY stays small per brief;
    # BRAIN RECOIL gives the insert an immediate editorial identity.
    bpy.ops.object.text_add(location=(0.0, -2.22, 7.15))
    label = bpy.context.object
    label.name = "label_stylized_replay"
    label.data.body = "STYLIZED REPLAY"
    label.data.align_x = "CENTER"
    label.data.align_y = "CENTER"
    label.data.size = 0.19
    label.data.extrude = 0.003
    label.data.bevel_depth = 0.002
    label.data.materials.append(mats["white"])
    label.scale.x = -1.0
    label["semantic_role"] = "review_label"
    bpy.ops.object.text_add(location=(0.0, -2.22, 6.78))
    title = bpy.context.object
    title.name = "title_brain_recoil"
    title.data.body = "BRAIN RECOIL"
    title.data.align_x = "CENTER"
    title.data.align_y = "CENTER"
    title.data.size = 0.40
    title.data.extrude = 0.004
    title.data.bevel_depth = 0.003
    title.data.materials.append(mats["brain_ridge"])
    title.scale.x = -1.0
    title["semantic_role"] = "insert_title"

    # Camera push: one target and one move, with no motion overlapping an
    # evidence build because this is a standalone insert.
    camera_data = bpy.data.cameras.new("camera_knockout_brain_matchcut")
    camera = bpy.data.objects.new("camera_knockout_brain_matchcut", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 9.10
    scene.camera = camera
    camera_start = Vector((0.65, -19.2, 4.72))
    camera_end = Vector((0.95, -16.3, 4.36))
    for frame, position, scale in ((1, camera_start, 9.10), (28, camera_start, 8.88), (90, camera_end, 8.18)):
        camera.location = position
        camera.data.ortho_scale = scale
        look_at(camera, Vector((0.0, 0.0, 3.25)))
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        camera.data.keyframe_insert(data_path="ortho_scale", frame=frame)
    keyframe_linear(camera)
    keyframe_linear(camera.data)
    # Blender text's readable face is its local -Z side; using the same
    # forward axis as the camera keeps STYLIZED REPLAY from rendering mirrored.
    label.rotation_mode = "QUATERNION"
    label.rotation_quaternion = (camera_end - label.location).to_track_quat("-Z", "Y")
    title.rotation_mode = "QUATERNION"
    title.rotation_quaternion = (camera_end - title.location).to_track_quat("-Z", "Y")

    # The key is warm coral, with cyan and magenta rims separating shell and
    # brain against the blue-black wall.
    add_area_light("key_coral", (-5.5, -7.0, 9.0), 780.0, 5.0, (1.0, 0.16, 0.24))
    add_area_light("rim_cyan", (6.5, 3.2, 8.5), 1250.0, 4.0, (0.08, 0.58, 1.0))
    add_area_light("fill_white", (1.0, -6.5, 4.0), 440.0, 6.0, (0.72, 0.88, 1.0))
    add_point_light("magenta_edge_point", (-4.0, 1.0, 4.6), 180.0, (1.0, 0.05, 0.28))

    # Head rotates left first; the brain begins later, overshoots once, then
    # repeats a smaller recoil before settling.  The location offsets make the
    # inertial lag visible even when the shell is translucent.
    head_keys = {
        1: ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        9: ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        18: ((-0.16, 0.0, 0.0), (0.0, math.radians(-8.0), math.radians(-4.0))),
        27: ((-0.46, 0.0, 0.0), (0.0, math.radians(-20.0), math.radians(-11.0))),
        38: ((-0.25, 0.0, 0.0), (0.0, math.radians(-12.0), math.radians(-6.0))),
        52: ((-0.37, 0.0, 0.0), (0.0, math.radians(-16.0), math.radians(-8.0))),
        68: ((-0.22, 0.0, 0.0), (0.0, math.radians(-10.0), math.radians(-5.0))),
        90: ((-0.20, 0.0, 0.0), (0.0, math.radians(-9.0), math.radians(-4.0))),
    }
    brain_keys = {
        1: ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        15: ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        27: ((0.21, 0.0, 0.0), (0.0, math.radians(-5.0), math.radians(-2.0))),
        38: ((-0.13, 0.0, 0.0), (0.0, math.radians(-17.0), math.radians(-8.0))),
        50: ((0.16, 0.0, 0.0), (0.0, math.radians(-24.0), math.radians(-12.0))),
        63: ((-0.06, 0.0, 0.0), (0.0, math.radians(-13.0), math.radians(-6.0))),
        77: ((0.03, 0.0, 0.0), (0.0, math.radians(-10.0), math.radians(-4.5))),
        90: ((0.0, 0.0, 0.0), (0.0, math.radians(-9.0), math.radians(-4.0))),
    }
    for frame, (location, rotation) in head_keys.items():
        key_transform(head_root, frame, tuple(HEAD_CENTER + Vector(location)), rotation)
    for frame, (location, rotation) in brain_keys.items():
        # brain_root is a child of head_root; these are intentionally small
        # local offsets layered on top of the head's rigid motion.
        key_transform(brain_root, frame, location, rotation)
    keyframe_linear(head_root)
    keyframe_linear(brain_root)

    # The marker arcs are part of the insert's visual language; pulse the
    # first punch and then the second recoil without hiding the anatomy.
    for obj in (impact_arc, recoil_arc):
        obj.scale = (0.35, 0.35, 0.35)
        obj.keyframe_insert(data_path="scale", frame=1)
        obj.scale = (1.0, 1.0, 1.0)
        obj.keyframe_insert(data_path="scale", frame=18 if obj is impact_arc else 36)
        obj.scale = (0.78, 0.78, 0.78)
        obj.keyframe_insert(data_path="scale", frame=32 if obj is impact_arc else 60)
        obj.scale = (0.60, 0.60, 0.60)
        obj.keyframe_insert(data_path="scale", frame=90)
        keyframe_linear(obj)

    scene["proof_schema"] = "martial_matters_knockout_brain_matchcut.v1"
    scene["review_state"] = "review_only"
    scene["render_eligible"] = False
    scene["source_data"] = False
    scene["notes"] = "Stylized anatomy insert: head rotation precedes delayed brain lag and two recoil beats. No gore, ejection, or medical claim."
    scene.frame_set(1)
    return {"scene": scene, "camera": camera, "head_root": head_root, "brain_root": brain_root}


def state_document(scene_info: dict) -> dict:
    scene = scene_info["scene"]
    head_root = scene_info["head_root"]
    brain_root = scene_info["brain_root"]
    samples = []
    for frame in SAMPLES:
        scene.frame_set(frame)
        head_rot = tuple(math.degrees(float(v)) for v in head_root.rotation_euler)
        brain_rot = tuple(math.degrees(float(v)) for v in brain_root.rotation_euler)
        samples.append(
            {
                "frame": frame,
                "time_s": round((frame - FRAME_START) / FPS, 6),
                "head_location": [round(float(v), 5) for v in head_root.location],
                "head_rotation_deg_xyz": [round(v, 3) for v in head_rot],
                "brain_location": [round(float(v), 5) for v in brain_root.location],
                "brain_rotation_deg_xyz": [round(v, 3) for v in brain_rot],
                "brain_vs_head_y_rotation_deg": round(brain_rot[1] - head_rot[1], 3),
            }
        )
    scene.frame_set(1)
    return {
        "schema": "martial_matters_knockout_brain_matchcut.v1",
        "review_state": "review_only",
        "render_eligible": False,
        "source_data": False,
        "scene": {
            "resolution": [WIDTH, HEIGHT],
            "fps": FPS,
            "frames": [FRAME_START, FRAME_END],
            "duration_s": FRAME_END / FPS,
            "engine": scene.render.engine,
        },
        "motion_contract": {
            "head": "leftward rotation begins at frame 9 and peaks at frame 27",
            "brain": "delayed lag starts after frame 15; overshoot/recoil peaks at frames 38 and 50",
            "recoil_beats": ["first recoil / catch-up", "second smaller recoil / settle"],
            "gore": False,
            "brain_ejection": False,
        },
        "sampled_motion_state": samples,
        "objects": {
            "head_root": head_root.name,
            "brain_root": brain_root.name,
            "camera": scene_info["camera"].name,
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pixel_sha256(path: Path) -> str:
    """Hash decoded pixels, not Blender's non-semantic PNG metadata."""
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        buf = array("f", [0.0]) * (image.size[0] * image.size[1] * 4)
        image.pixels.foreach_get(buf)
        return hashlib.sha256(buf.tobytes()).hexdigest()
    finally:
        bpy.data.images.remove(image)


def render_stills(scene) -> dict:
    frames_dir = ROOT / "frames"
    reverse_dir = frames_dir / "reverse"
    frames_dir.mkdir(parents=True, exist_ok=True)
    reverse_dir.mkdir(parents=True, exist_ok=True)
    forward = {}
    reverse = {}
    forward_pixels = {}
    reverse_pixels = {}
    for frame in SAMPLES:
        scene.frame_set(frame)
        path = frames_dir / f"frame-{frame:04d}.png"
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Blender did not write {path}")
        forward[frame] = sha256(path)
        forward_pixels[frame] = pixel_sha256(path)
    for frame in reversed(SAMPLES):
        scene.frame_set(frame)
        path = reverse_dir / f"frame-{frame:04d}.png"
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Blender did not write {path}")
        reverse[frame] = sha256(path)
        reverse_pixels[frame] = pixel_sha256(path)
    comparisons = {str(frame): forward_pixels[frame] == reverse_pixels[frame] for frame in SAMPLES}
    receipt = {
        "schema": "martial_matters_knockout_brain_determinism.v1",
        "sample_frames": list(SAMPLES),
        "forward_hashes": {str(k): v for k, v in forward.items()},
        "reverse_hashes": {str(k): v for k, v in reverse.items()},
        "forward_pixel_hashes": {str(k): v for k, v in forward_pixels.items()},
        "reverse_pixel_hashes": {str(k): v for k, v in reverse_pixels.items()},
        "reverse_seek_equal": all(comparisons.values()),
        "comparisons": comparisons,
        "comparison_note": "PNG byte hashes can differ in metadata; verdict compares decoded Blender pixel buffers.",
    }
    (ROOT / "determinism.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def render_movie(scene) -> dict:
    movie = ROOT / "brain-recoil.mp4"
    movie_frames = ROOT / "movie-frames"
    movie_frames.mkdir(parents=True, exist_ok=True)
    scene.frame_set(FRAME_START)
    # Blender 5.2 removed FFMPEG from ImageSettings.file_format.  Render the
    # movie frames in Eevee, then encode that exact sequence with ffmpeg; this
    # keeps the geometry/render reproducible while remaining compatible with
    # the installed Blender 5.2 API.
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(movie_frames / "frame-")
    bpy.ops.render.render(animation=True)
    result = {
        "path": str(movie.relative_to(ROOT)).replace("\\", "/"),
        "exists": False,
        "bytes": 0,
    }
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        command = [
            ffmpeg,
            "-y",
            "-framerate",
            str(FPS),
            "-start_number",
            str(FRAME_START),
            "-i",
            str(movie_frames / "frame-%04d.png"),
            "-frames:v",
            str(FRAME_END - FRAME_START + 1),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(movie),
        ]
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        result["ffmpeg_command"] = " ".join(command)
        result["ffmpeg_exit"] = proc.returncode
        result["ffmpeg_stderr_tail"] = proc.stderr[-2000:]
    else:
        result["ffmpeg"] = "not available on PATH"
    result["exists"] = movie.is_file()
    result["bytes"] = movie.stat().st_size if movie.is_file() else 0
    ffprobe = shutil.which("ffprobe")
    if ffprobe and movie.is_file():
        command = [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration",
            "-of",
            "json",
            str(movie),
        ]
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        result["ffprobe_command"] = " ".join(command)
        result["ffprobe_exit"] = proc.returncode
        result["ffprobe"] = json.loads(proc.stdout) if proc.returncode == 0 and proc.stdout.strip() else {"stderr": proc.stderr[-2000:]}
        (ROOT / "ffprobe.json").write_text(json.dumps(result["ffprobe"], indent=2) + "\n", encoding="utf-8")
    else:
        result["ffprobe"] = "not available on PATH" if not ffprobe else "movie missing"
    if movie.is_file() and movie_frames.is_dir():
        shutil.rmtree(movie_frames, ignore_errors=True)
    return result


def write_proof(mode: str, determinism: dict, movie: dict | None) -> None:
    lines = [
        "# Knockout brain match-cut — Blender insert",
        "",
        "Status: **review-only diagnostic**; `review_state=review_only`; `render_eligible=false`; no publication approval claimed.",
        "",
        "## Acceptance",
        "",
        "Three seconds at 720x1280 / 30 fps. The camera makes a restrained push while a translucent head/skull silhouette rotates left first; the coral brain visibly lags, overshoots, and performs a second smaller recoil. The insert is non-graphic: no gore, ejection, or medical claim.",
        "",
        "Representative frames: `frames/frame-0001.png`, `frames/frame-0024.png`, `frames/frame-0038.png`, `frames/frame-0050.png`, `frames/frame-0090.png`. Structured motion facts are in `state.json`; forward/reverse sample hashes are in `determinism.json`.",
        "",
        "## Reproduction",
        "",
        "```text",
        "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python knockout_brain_matchcut.py -- --samples",
        "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python knockout_brain_matchcut.py -- --render",
        "ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration -of json brain-recoil.mp4",
        "```",
        "",
        f"Build mode: `{mode}`. Reverse-seek sample equality: **{determinism['reverse_seek_equal']}**.",
        "",
        "## Custody",
        "",
        "The scene is code-authored and source-free. It remains quarantined for operator frame review; the presence of a render is not an approval or a publication claim.",
        "",
    ]
    if movie is not None:
        lines.extend(["## Movie probe receipt", "", "```json", json.dumps(movie, indent=2), "```", ""])
    (ROOT / "PROOF.md").write_text("\n".join(lines), encoding="utf-8")


def output_files() -> list[Path]:
    paths = [
        ROOT / "knockout_brain_matchcut.py",
        ROOT / "brain-recoil.blend",
        ROOT / "state.json",
        ROOT / "determinism.json",
        ROOT / "ffprobe.json",
        ROOT / "PROOF.md",
    ]
    paths.extend((ROOT / "frames").glob("frame-*.png"))
    paths.extend((ROOT / "frames" / "reverse").glob("frame-*.png"))
    movie = ROOT / "brain-recoil.mp4"
    if movie.is_file():
        paths.append(movie)
    return [path for path in paths if path.is_file()]


def write_manifest() -> None:
    entries = []
    for path in sorted(output_files(), key=lambda p: p.relative_to(ROOT).as_posix()):
        entries.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    manifest = {
        "schema": "asset-quarantine.v1",
        "asset_id": "martial-matters-knockout-brain-matchcut-001-blender",
        "review_state": "review_only",
        "render_eligible": False,
        "source_data": False,
        "operator_approval": None,
        "files": entries,
    }
    (ROOT / "quarantine-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    scene_info = build_scene()
    state = state_document(scene_info)
    (ROOT / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    scene = scene_info["scene"]
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "brain-recoil.blend"))
    determinism = render_stills(scene)
    movie = render_movie(scene) if args.render else None

    # Leave the blend in a predictable frame-1/PNG state, not a transient movie
    # output mode or whichever representative frame was rendered last.
    scene.render.image_settings.file_format = "PNG"
    scene.frame_set(FRAME_START)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "brain-recoil.blend"))
    write_proof("render" if args.render else "samples", determinism, movie)
    write_manifest()
    print(
        json.dumps(
            {
                "mode": "render" if args.render else "samples",
                "reverse_seek_equal": determinism["reverse_seek_equal"],
                "movie": movie,
                "output_dir": str(ROOT),
            },
            indent=2,
        )
    )
    return 0 if determinism["reverse_seek_equal"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
