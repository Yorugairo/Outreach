"""Offline MPFB/Rigify authoring for one diagnostic native character family.

This module is imported inside the pinned Blender interpreter. It keeps the
authoring source editable and emits structured inspection state beside renders.
All generated art remains diagnostic and review-only.
"""

from __future__ import annotations

import addon_utils
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

from .presets import (
    BODY_BOUNDS,
    CLOTHING_PALETTES,
    FACE_TARGETS,
    FAMILY_ID,
    SKIN_PALETTES,
    family_manifest,
    resolve_controls,
)


REPO_ROOT = Path(__file__).resolve().parents[5]
T1_ROOT = REPO_ROOT / "content/video_engine/tests/fixtures/modeling/baseline"
T1_MANIFEST_PATH = T1_ROOT / "benchmark-inputs.json"
BLENDER_EXPECTED_PATH = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
PACKAGE_PATH = T1_ROOT / "tools/packages/mpfb-2.0.17.zip"
TARGET_CACHE_ROOT = T1_ROOT / "profile/extensions/user_default/mpfb/data/targets"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _save_mainfile_without_backup(path: Path) -> None:
    """Avoid a stale .blend1 without changing the operator's Blender preference."""
    filepaths = bpy.context.preferences.filepaths
    previous_version_count = filepaths.save_version
    try:
        filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
    finally:
        filepaths.save_version = previous_version_count


def _path_is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def validate_local_runtime() -> dict[str, Any]:
    """Fail closed unless this is the exact isolated T1 Blender/MPFB setup."""
    if not T1_MANIFEST_PATH.is_file():
        raise RuntimeError(f"T1 benchmark manifest is missing: {T1_MANIFEST_PATH}")
    baseline = json.loads(T1_MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = baseline["tools"]["blender"]
    candidate = baseline["candidate"]
    profile = (T1_ROOT / "profile").resolve()
    resource_path = Path(bpy.utils.resource_path("USER")).resolve()
    env_profile = Path(os.environ.get("BLENDER_USER_RESOURCES", "")).resolve()
    executable = Path(bpy.app.binary_path).resolve()
    build_hash = bpy.app.build_hash.decode("utf-8") if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash)

    if executable != Path(expected["path"]).resolve() or executable != BLENDER_EXPECTED_PATH.resolve():
        raise RuntimeError(f"pinned Blender executable mismatch: got {executable}, expected {expected['path']}")
    if bpy.app.version_string != expected["version"] or build_hash != expected["build_hash"]:
        raise RuntimeError(
            f"pinned Blender build mismatch: got {bpy.app.version_string}/{build_hash}, "
            f"expected {expected['version']}/{expected['build_hash']}"
        )
    if not profile.is_dir() or env_profile != profile or resource_path != profile:
        raise RuntimeError(
            "MPFB must run with BLENDER_USER_RESOURCES and Blender USER resource path "
            f"inside the isolated T1 profile; env={env_profile}, USER={resource_path}, expected={profile}"
        )
    if not PACKAGE_PATH.is_file() or _sha256(PACKAGE_PATH) != candidate["package_sha256"]:
        raise RuntimeError(f"pinned MPFB 2.0.17 package missing or hash mismatch: {PACKAGE_PATH}")
    if not _path_is_inside(TARGET_CACHE_ROOT, profile) or not TARGET_CACHE_ROOT.is_dir():
        raise RuntimeError(f"MPFB bundled targets are absent from the isolated T1 profile: {TARGET_CACHE_ROOT}")
    return {
        "blender_executable": str(executable),
        "blender_version": bpy.app.version_string,
        "blender_build_hash": build_hash,
        "mpfb_version": "2.0.17",
        "mpfb_source_commit": candidate["source_commit"],
        "mpfb_package_path": str(PACKAGE_PATH),
        "mpfb_package_sha256": candidate["package_sha256"],
        "isolated_profile": str(profile),
        "offline_mode_requested": True,
        "provider_calls": 0,
    }


def _mpfb_symbol(module_suffix: str, symbol: str) -> Any:
    for module_name in tuple(sys.modules):
        if module_name.endswith(module_suffix):
            module = importlib.import_module(module_name)
            if hasattr(module, symbol):
                return getattr(module, symbol)
    raise RuntimeError(f"MPFB module ending in {module_suffix!r} did not expose {symbol!r}")


def _enable_local_addons() -> dict[str, Any]:
    addon_utils.modules_refresh()
    addon_utils.enable("rigify", default_set=True, persistent=False)
    addon_utils.modules_refresh()
    addon_utils.enable("bl_ext.user_default.mpfb", default_set=True, persistent=False)
    rigify_state = list(addon_utils.check("rigify"))
    mpfb_state = list(addon_utils.check("bl_ext.user_default.mpfb"))
    if not all(rigify_state) or not all(mpfb_state):
        raise RuntimeError(f"local addons failed to enable: rigify={rigify_state}, mpfb={mpfb_state}")
    if not hasattr(bpy.ops.mpfb, "create_human") or not hasattr(bpy.ops.mpfb, "add_rigify_rig"):
        raise RuntimeError("MPFB create_human/add_rigify_rig operators were not registered")
    return {"rigify": rigify_state, "mpfb": mpfb_state}


def _clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for camera in tuple(bpy.data.cameras):
        if camera.users == 0:
            bpy.data.cameras.remove(camera)
    for light in tuple(bpy.data.lights):
        if light.users == 0:
            bpy.data.lights.remove(light)


def _material(name: str, color: tuple[float, float, float, float], *, roughness: float = 0.56,
              metallic: float = 0.0, emission: float = 0.0) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = roughness
        principled.inputs["Metallic"].default_value = metallic
        if "Emission Color" in principled.inputs:
            principled.inputs["Emission Color"].default_value = color
        if "Emission Strength" in principled.inputs:
            principled.inputs["Emission Strength"].default_value = emission
        if "Subsurface Weight" in principled.inputs:
            principled.inputs["Subsurface Weight"].default_value = 0.025 if name.startswith("MM_Skin") else 0.0
    return material


def _face_basis(rig: bpy.types.Object) -> dict[str, Vector]:
    head = rig.data.bones.get("head")
    if head is None:
        raise RuntimeError("generated Rigify armature has no head control")
    basis = rig.matrix_world.to_3x3() @ head.matrix_local.to_3x3()
    vectors = {
        "right": (basis @ Vector((1.0, 0.0, 0.0))).normalized(),
        "up": (basis @ Vector((0.0, 1.0, 0.0))).normalized(),
        "forward": (basis @ Vector((0.0, 0.0, 1.0))).normalized(),
        "origin": rig.matrix_world @ head.head_local,
    }
    if vectors["up"].z < 0.7 or vectors["forward"].y > -0.5:
        raise RuntimeError(f"unexpected head orientation; extracted basis={vectors}")
    return vectors


def _find_deform_bone(rig: bpy.types.Object, *names: str) -> str:
    for name in names:
        bone = rig.data.bones.get(name)
        if bone is not None and bone.use_deform:
            return name
    raise RuntimeError(f"none of the required deform bones exist: {names}")


def _head_surface_point(body: bpy.types.Object, point: Vector, forward: Vector,
                        clearance: float) -> Vector:
    """Anchor a facial detail to the actual shaped head instead of a fixed bone offset."""
    inverse = body.matrix_world.inverted()
    start = point + forward * 0.15
    hit, location, _normal, _face = body.ray_cast(
        inverse @ start, (inverse.to_3x3() @ (-forward)).normalized(), distance=0.35,
    )
    if not hit:
        raise RuntimeError(f"facial detail has no shaped-head surface at {tuple(point)}")
    return body.matrix_world @ location + forward * clearance


def _mesh_object(name: str, vertices: list[tuple[float, float, float]], faces: list[tuple[int, ...]],
                 material: bpy.types.Material, rig: bpy.types.Object, bone_name: str,
                 *, layer: str) -> bpy.types.Object:
    if not vertices or not faces:
        raise ValueError(f"{name} must have nonempty vertices and faces")
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    group = obj.vertex_groups.new(name=bone_name)
    group.add(list(range(len(vertices))), 1.0, "REPLACE")
    modifier = obj.modifiers.new("Rigify_Attachment", "ARMATURE")
    modifier.object = rig
    obj.parent = rig
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj["diagnostic_layer"] = layer
    obj["attachment_bone"] = bone_name
    obj["asset_family_id"] = FAMILY_ID
    return obj


def _ellipsoid_mesh(center: Vector, basis: dict[str, Vector], radii: tuple[float, float, float],
                    segments: int = 20, rings: int = 12) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    right, up, forward = basis["right"], basis["up"], basis["forward"]
    for i in range(rings + 1):
        theta = math.pi * i / rings
        for j in range(segments):
            phi = 2.0 * math.pi * j / segments
            point = (center + right * (radii[0] * math.sin(theta) * math.cos(phi))
                     + up * (radii[1] * math.cos(theta))
                     + forward * (radii[2] * math.sin(theta) * math.sin(phi)))
            vertices.append(tuple(point))
    for i in range(rings):
        for j in range(segments):
            jn = (j + 1) % segments
            a = i * segments + j
            b = (i + 1) * segments + j
            c = (i + 1) * segments + jn
            d = i * segments + jn
            faces.append((a, b, c, d))
    return vertices, faces


def _add_ellipsoid(name: str, center: Vector, basis: dict[str, Vector], radii: tuple[float, float, float],
                   material: bpy.types.Material, rig: bpy.types.Object, bone_name: str,
                   *, layer: str, segments: int = 24, rings: int = 14) -> bpy.types.Object:
    vertices, faces = _ellipsoid_mesh(center, basis, radii, segments, rings)
    return _mesh_object(name, vertices, faces, material, rig, bone_name, layer=layer)


def _ribbon_mesh(points: list[Vector], half_width: float, right: Vector) -> tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]:
    vertices: list[tuple[float, float, float]] = []
    for point in points:
        vertices.extend((tuple(point - right * half_width), tuple(point + right * half_width)))
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(points) - 1)]
    return vertices, faces


def _hair_geometry(basis: dict[str, Vector], style: str, material: bpy.types.Material,
                   rig: bpy.types.Object, head_bone: str) -> list[str]:
    origin = basis["origin"]
    center = origin + basis["up"] * 0.088 + basis["forward"] * 0.004
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    segments = 32
    ring_steps = 8
    rx, ry, rz = 0.092, 0.080, 0.073
    for i in range(ring_steps + 1):
        theta = 0.08 + (1.66 - 0.08) * i / ring_steps
        for j in range(segments):
            phi = 2.0 * math.pi * j / segments
            p = (center + basis["right"] * (rx * math.sin(theta) * math.cos(phi))
                 + basis["forward"] * (ry * math.sin(theta) * math.sin(phi))
                 + basis["up"] * (rz * math.cos(theta)))
            vertices.append(tuple(p))
    for i in range(ring_steps):
        for j in range(segments):
            jn = (j + 1) % segments
            a, b = i * segments + j, (i + 1) * segments + j
            c, d = (i + 1) * segments + jn, i * segments + jn
            faces.append((a, b, c, d))
    cap_faces = list(faces)
    cap_vertices = list(vertices)
    _mesh_object("Hair_CropCap", cap_vertices, cap_faces, material, rig, head_bone, layer="hair")
    names = ["Hair_CropCap"]

    if style == "quiff":
        # Rounded swept tuft. A single five-vertex pyramid reads as a spike at
        # portrait scale and hides whether the hairstyle control is useful.
        quiff_vertices: list[tuple[float, float, float]] = []
        quiff_faces: list[tuple[int, ...]] = []
        sections = (
            (0.108, 0.040, 0.048, 0.021, -0.025),
            (0.130, 0.060, 0.048, 0.022, -0.010),
            (0.151, 0.070, 0.036, 0.018, 0.012),
            (0.170, 0.061, 0.022, 0.012, 0.030),
            (0.180, 0.050, 0.008, 0.006, 0.040),
        )
        ring_size = 12
        for height, forward_offset, width, depth, side_offset in sections:
            center = (origin + basis["up"] * height + basis["forward"] * forward_offset
                      + basis["right"] * side_offset)
            for j in range(ring_size):
                angle = 2.0 * math.pi * j / ring_size
                point = center + basis["right"] * (width * math.cos(angle)) + basis["forward"] * (depth * math.sin(angle))
                quiff_vertices.append(tuple(point))
        for i in range(len(sections) - 1):
            for j in range(ring_size):
                jn = (j + 1) % ring_size
                quiff_faces.append((i * ring_size + j, i * ring_size + jn,
                                    (i + 1) * ring_size + jn, (i + 1) * ring_size + j))
        quiff_faces.append(tuple(range(ring_size - 1, -1, -1)))
        quiff_faces.append(tuple((len(sections) - 1) * ring_size + j for j in range(ring_size)))
        _mesh_object("Hair_SweptQuiff", quiff_vertices, quiff_faces, material, rig, head_bone, layer="hair")
        names.append("Hair_SweptQuiff")
    return names


def _create_skinned_garment(body: bpy.types.Object, rig: bpy.types.Object, style: str,
                            material: bpy.types.Material) -> dict[str, Any]:
    """Duplicate a shaped body surface patch into a separate weighted cloth shell."""
    regions = {"fight_kit": (0.64, 1.03), "warmup": (0.08, 1.03)}
    if style not in regions:
        raise ValueError(f"unsupported diagnostic garment style: {style}")
    lower, upper = regions[style]
    group_name_by_index = {group.index: group.name for group in body.vertex_groups}
    visible_group = body.vertex_groups.get("body")
    if visible_group is None:
        raise RuntimeError("MPFB body lacks the visible-skin body vertex group")
    visible_skin = {vertex.index for vertex in body.data.vertices
                    if any(assignment.group == visible_group.index and assignment.weight > 0.5
                           for assignment in vertex.groups)}
    lower_body_groups = {group.index for group in body.vertex_groups
                         if group.name.startswith(("DEF-pelvis", "DEF-spine", "DEF-thigh", "DEF-shin", "DEF-foot", "DEF-toe"))}
    if not lower_body_groups:
        raise RuntimeError("MPFB body lacks lower-body deformation groups")

    armature_modifiers = [modifier for modifier in body.modifiers if modifier.type == "ARMATURE"]
    # MPFB also masks helper topology. Disable that mask while sampling the
    # shaped source so its vertex indices still match the stored skin weights.
    modifier_visibility = [(modifier, modifier.show_viewport, modifier.show_render)
                           for modifier in body.modifiers]
    shape_mesh = None
    try:
        for modifier, _viewport, _render in modifier_visibility:
            modifier.show_viewport = False
            modifier.show_render = False
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        shaped_body = body.evaluated_get(depsgraph)
        shape_mesh = shaped_body.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        shape_mesh.update()
        if len(shape_mesh.vertices) != len(body.data.vertices):
            raise RuntimeError(
                f"shaped body topology differs from the source skin-weight mesh: "
                f"evaluated={len(shape_mesh.vertices)}, stored={len(body.data.vertices)}, "
                f"modifiers={[(item.name, item.type, item.show_viewport) for item in body.modifiers]}"
            )

        selected_faces: list[tuple[tuple[int, ...], int]] = []
        selected_vertex_ids: set[int] = set()
        for polygon in shape_mesh.polygons:
            face_vertices = tuple(polygon.vertices)
            center = sum((shape_mesh.vertices[index].co for index in face_vertices), Vector()) / len(face_vertices)
            if not lower <= center.z <= upper:
                continue
            if not all(vertex_index in visible_skin for vertex_index in face_vertices):
                continue
            region_weight = sum(
                assignment.weight
                for vertex_index in face_vertices
                for assignment in body.data.vertices[vertex_index].groups
                if assignment.group in lower_body_groups
            ) / len(face_vertices)
            if region_weight < 0.24:
                continue
            selected_faces.append((face_vertices, polygon.index))
            selected_vertex_ids.update(face_vertices)
    finally:
        if shape_mesh is not None:
            shaped_body.to_mesh_clear()
        for modifier, viewport, render in modifier_visibility:
            modifier.show_viewport = viewport
            modifier.show_render = render
        bpy.context.view_layer.update()

    if len(selected_faces) < 250 or len(selected_vertex_ids) < 500:
        raise RuntimeError(
            f"diagnostic {style} garment patch is undersized: "
            f"{len(selected_faces)} faces / {len(selected_vertex_ids)} vertices"
        )

    # Re-evaluate the shaped body without its armature to copy the actual control
    # result and its surface normals into editable cloth vertices.
    modifier_visibility = [(modifier, modifier.show_viewport, modifier.show_render)
                           for modifier in body.modifiers]
    shape_mesh = None
    try:
        for modifier, _viewport, _render in modifier_visibility:
            modifier.show_viewport = False
            modifier.show_render = False
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        shaped_body = body.evaluated_get(depsgraph)
        shape_mesh = shaped_body.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        shape_mesh.update()
        source_ids = sorted(selected_vertex_ids)
        destination_index = {source: destination for destination, source in enumerate(source_ids)}
        vertices = []
        for source_index in source_ids:
            normal = shape_mesh.vertices[source_index].normal.copy()
            if normal.length < 1e-8:
                raise RuntimeError(f"garment source vertex {source_index} has no stable surface normal")
            point = shape_mesh.vertices[source_index].co + normal.normalized() * 0.009
            vertices.append(tuple(float(value) for value in point))
        faces = [tuple(destination_index[source] for source in face) for face, _poly in selected_faces]
        source_polygon_indices = [poly for _face, poly in selected_faces]
    finally:
        if shape_mesh is not None:
            shaped_body.to_mesh_clear()
        for modifier, viewport, render in modifier_visibility:
            modifier.show_viewport = viewport
            modifier.show_render = render
        bpy.context.view_layer.update()

    garment_name = "Garment_FightShorts" if style == "fight_kit" else "Garment_WarmupPants"
    garment_mesh = bpy.data.meshes.new(f"{garment_name}_Mesh")
    garment_mesh.from_pydata(vertices, [], faces)
    garment_mesh.update(calc_edges=True)
    garment_mesh.materials.append(material)
    color = tuple(float(value) for value in material.diffuse_color)
    trim_color = tuple(min(1.0, component * 0.64 + 0.11) for component in color[:3]) + (1.0,)
    trim_material = _material("MM_Garment_Seam", trim_color, roughness=0.78)
    garment_mesh.materials.append(trim_material)
    for polygon, source_polygon_index in zip(garment_mesh.polygons, source_polygon_indices):
        polygon.use_smooth = True
        source_polygon = body.data.polygons[source_polygon_index]
        center_z = sum(body.data.vertices[index].co.z for index in source_polygon.vertices) / len(source_polygon.vertices)
        polygon.material_index = 1 if center_z >= upper - 0.045 else 0

    source_index_attribute = garment_mesh.attributes.new(
        name="body_source_vertex_index", type="INT", domain="POINT",
    )
    for destination, source in enumerate(source_ids):
        source_index_attribute.data[destination].value = source

    garment = bpy.data.objects.new(garment_name, garment_mesh)
    bpy.context.scene.collection.objects.link(garment)
    garment.matrix_world = body.matrix_world.copy()
    garment["diagnostic_layer"] = "clothing"
    garment["asset_family_id"] = FAMILY_ID
    garment["garment_style"] = style
    garment["garment_representation"] = "separate_editable_skinned_shell"
    garment["surface_ease_m"] = 0.009
    garment["weight_transfer"] = "copied_from_shaped_body_by_source_vertex_index"
    garment["art_status"] = "diagnostic_only"

    used_group_indices = {assignment.group for source in source_ids
                          for assignment in body.data.vertices[source].groups}
    # Retain empty armature mask groups too. Blender clears a modifier's named
    # vertex_group if that group does not exist on the new garment; its second
    # Armature modifier would then deform the entire garment a second time.
    used_group_indices.update(
        body.vertex_groups[modifier.vertex_group].index
        for modifier in armature_modifiers if modifier.vertex_group
    )
    garment_groups = {
        group_index: garment.vertex_groups.new(name=group_name_by_index[group_index])
        for group_index in sorted(used_group_indices)
    }
    for destination, source in enumerate(source_ids):
        for assignment in body.data.vertices[source].groups:
            target_group = garment_groups.get(assignment.group)
            if target_group is not None and assignment.weight > 0.0:
                target_group.add([destination], float(assignment.weight), "REPLACE")

    for body_modifier in armature_modifiers:
        modifier = garment.modifiers.new(body_modifier.name, "ARMATURE")
        modifier.object = body_modifier.object
        modifier.vertex_group = body_modifier.vertex_group
        modifier.use_vertex_groups = body_modifier.use_vertex_groups
        modifier.use_bone_envelopes = body_modifier.use_bone_envelopes
        modifier.use_deform_preserve_volume = body_modifier.use_deform_preserve_volume
        modifier.show_viewport = body_modifier.show_viewport
        modifier.show_render = body_modifier.show_render

    solidify = garment.modifiers.new("Garment_Seam_Thickness", "SOLIDIFY")
    solidify.thickness = 0.003
    solidify.offset = -1.0
    solidify.use_even_offset = True
    solidify.use_rim = True
    solidify.material_offset = 0
    solidify.material_offset_rim = 1

    return {
        "object_name": garment.name,
        "style": style,
        "body_polygons_copied": len(selected_faces),
        "garment_vertices": len(vertices),
        "garment_polygons": len(faces),
        "weighted_vertices": len(source_ids),
        "weight_group_count": len(garment_groups),
        "source_vertex_attribute": "body_source_vertex_index",
        "surface_ease_m": 0.009,
        "shell_thickness_m": 0.003,
        "lower_z_m": lower,
        "upper_z_m": upper,
    }


def _add_face_details(body: bpy.types.Object, basis: dict[str, Vector], materials: dict[str, bpy.types.Material],
                      rig: bpy.types.Object, head_bone: str) -> list[str]:
    origin, right, up, front = basis["origin"], basis["right"], basis["up"], basis["forward"]
    names: list[str] = []
    for side, sign in (("L", 1.0), ("R", -1.0)):
        # MPFB already supplies the shaped eye region. Add only color details
        # at that region; a second sclera above it produces a duplicate eye.
        eye_hint = origin + up * 0.040 + front * 0.085 + right * (0.032 * sign)
        surface = _head_surface_point(body, eye_hint, front, 0.0)
        iris_center = surface + front * 0.002
        iris = _add_ellipsoid(f"Face_Iris_{side}", iris_center, basis, (0.0052, 0.0052, 0.0018),
                              materials["iris"], rig, head_bone, layer="face", segments=18, rings=10)
        pupil = _add_ellipsoid(f"Face_Pupil_{side}", surface + front * 0.004,
                               basis, (0.0028, 0.0035, 0.0012), materials["pupil"],
                               rig, head_bone, layer="face", segments=14, rings=8)
        brow_hints = [
            origin + up * 0.078 + front * 0.081 + right * (sign * 0.014),
            origin + up * 0.089 + front * 0.092 + right * (sign * 0.033),
            origin + up * 0.080 + front * 0.085 + right * (sign * 0.052),
        ]
        brow_points = [_head_surface_point(body, point, front, 0.003) for point in brow_hints]
        verts, faces = _ribbon_mesh(brow_points, 0.004, right)
        brow = _mesh_object(f"Face_Brow_{side}", verts, faces, materials["brow"], rig, head_bone, layer="face")
        names.extend((iris.name, pupil.name, brow.name))

    return names


def _configure_rig_pose(rig: bpy.types.Object) -> dict[str, Any]:
    candidate_controls = ["upper_arm_fk.R", "upper_arm_fk.L"]
    found = [name for name in candidate_controls if rig.pose.bones.get(name)]
    if not found:
        raise RuntimeError("Rigify did not produce the T1 FK upper-arm controls")
    parent_switches: dict[str, float] = {}
    for side in ("R", "L"):
        parent = rig.pose.bones.get(f"upper_arm_parent.{side}")
        if parent is None or "IK_FK" not in parent:
            raise RuntimeError(f"Rigify upper_arm_parent.{side} has no IK_FK switch")
        parent["IK_FK"] = 1.0
        parent.keyframe_insert(data_path='["IK_FK"]', frame=1, group="Diagnostic pose controls")
        parent.keyframe_insert(data_path='["IK_FK"]', frame=27, group="Diagnostic pose controls")
        parent_switches[parent.name] = float(parent["IK_FK"])

    right = rig.pose.bones["upper_arm_fk.R"] if "upper_arm_fk.R" in found else rig.pose.bones[found[0]]
    right.rotation_mode = "XYZ"
    right.rotation_euler = (0.0, 0.0, 0.0)
    right.keyframe_insert(data_path="rotation_euler", frame=1, group="Diagnostic pose controls")
    right.rotation_euler.z = 0.60
    right.keyframe_insert(data_path="rotation_euler", frame=27, group="Diagnostic pose controls")
    right.rotation_euler.z = 0.66
    right.keyframe_insert(data_path="rotation_euler", frame=28, group="Diagnostic pose controls")
    right.rotation_euler.z = 0.0
    right.keyframe_insert(data_path="rotation_euler", frame=48, group="Diagnostic pose controls")
    left_thigh = rig.pose.bones.get("thigh_fk.L")
    if left_thigh is None:
        raise RuntimeError("Rigify did not produce the T4b left thigh FK stress control")
    left_thigh_parent = rig.pose.bones.get("thigh_parent.L")
    if left_thigh_parent is None or "IK_FK" not in left_thigh_parent:
        raise RuntimeError("Rigify thigh_parent.L has no IK_FK switch")
    left_thigh_parent["IK_FK"] = 1.0
    left_thigh_parent.keyframe_insert(data_path='["IK_FK"]', frame=1, group="Diagnostic pose controls")
    left_thigh_parent.keyframe_insert(data_path='["IK_FK"]', frame=52, group="Diagnostic pose controls")
    left_thigh.rotation_mode = "XYZ"
    left_thigh.rotation_euler = (0.0, 0.0, 0.0)
    left_thigh.keyframe_insert(data_path="rotation_euler", frame=1, group="Diagnostic pose controls")
    left_thigh.keyframe_insert(data_path="rotation_euler", frame=50, group="Diagnostic pose controls")
    left_thigh.rotation_euler.x = 0.72
    left_thigh.keyframe_insert(data_path="rotation_euler", frame=51, group="Diagnostic pose controls")
    left_thigh.keyframe_insert(data_path="rotation_euler", frame=52, group="Diagnostic pose controls")
    left_thigh.rotation_euler.x = 0.0
    left_thigh.keyframe_insert(data_path="rotation_euler", frame=53, group="Diagnostic pose controls")
    return {
        "fk_controls": found,
        "ik_fk_switches": parent_switches,
        "pose_keyframes": [1, 27, 28, 48, 50, 51, 52, 53],
        "probe_rotation_radians": 0.60,
        "leg_stress_control": "thigh_fk.L",
        "leg_ik_fk_switch": "thigh_parent.L",
        "leg_stress_rotation_radians": 0.72,
        "leg_stress_frame": 52,
        "scope": "isolated arm and hip/leg deformation probes; not combat choreography",
    }


def _add_floor_and_lighting() -> None:
    floor_material = _material("MM_Stage_Floor", (0.055, 0.065, 0.080, 1.0), roughness=0.74)
    floor_mesh = bpy.data.meshes.new("Diagnostic_Floor_Mesh")
    floor_mesh.from_pydata([(-6, -6, 0), (6, -6, 0), (6, 6, 0), (-6, 6, 0)], [], [(0, 1, 2, 3)])
    floor_mesh.update()
    floor = bpy.data.objects.new("Diagnostic_Floor", floor_mesh)
    bpy.context.scene.collection.objects.link(floor)
    floor.data.materials.append(floor_material)
    floor["diagnostic_only"] = True

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    try:
        scene.view_settings.look = "Medium High Contrast"
    except (TypeError, ValueError):
        pass
    scene.render.image_settings.compression = 20
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 53
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.world = scene.world or bpy.data.worlds.new("MM_Diagnostic_World")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.075, 0.09, 0.12, 1.0)
    scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.65

    def area(name: str, position: Vector, power: float, size: float, color: tuple[float, float, float]) -> None:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = position
        target = Vector((0.0, 0.0, 0.95))
        obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()

    area("MM_Key", Vector((3.6, -4.6, 4.3)), 850, 3.4, (1.0, 0.78, 0.63))
    area("MM_Fill", Vector((-3.2, -2.7, 2.3)), 480, 4.0, (0.55, 0.72, 1.0))
    area("MM_Rim", Vector((-0.4, 3.5, 3.4)), 1050, 2.6, (0.42, 0.72, 1.0))


def _make_camera(name: str, target: Vector, direction: Vector, scale: float,
                 resolution: tuple[int, int], output_path: Path) -> bpy.types.Object:
    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    distance = max(3.0, scale * 3.5)
    direction = direction.normalized()
    camera.location = target + direction * distance
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(output_path)
    return camera


def _render_review_views(rig: bpy.types.Object, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    head = rig.data.bones["head"]
    basis = _face_basis(rig)
    shoulder_r = rig.matrix_world @ rig.data.bones["shoulder.R"].head_local
    shoulder_l = rig.matrix_world @ rig.data.bones["shoulder.L"].head_local
    side = (shoulder_l - shoulder_r).normalized()
    front = basis["forward"].normalized()
    body_target = Vector((0.0, 0.0, 0.84))
    directions = {
        "front": front,
        "three-quarter": (front + side * 0.72).normalized(),
        "side": side,
        "back": -front,
    }
    paths: dict[str, str] = {}
    for name, direction in directions.items():
        path = output_dir / f"fighter-family-{name}.png"
        _make_camera(f"ReviewCamera_{name}", body_target, direction, 2.02, (512, 768), path)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
        paths[name] = str(path)

    garment_center = Vector((0.0, -0.12, 0.76))
    for name, direction in (
        ("garment-front", front),
        ("garment-three-quarter", (front + side * 0.72).normalized()),
    ):
        path = output_dir / f"fighter-family-{name}.png"
        _make_camera(f"ReviewCamera_{name}", garment_center, direction, 0.70, (512, 512), path)
        scene.frame_set(1)
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
        paths[name] = str(path)

    face_target = basis["origin"] + basis["up"] * 0.055 + front * 0.020
    face_path = output_dir / "fighter-family-face.png"
    _make_camera("ReviewCamera_face", face_target, front, 0.42, (512, 512), face_path)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    paths["face"] = str(face_path)

    hand_bone = rig.data.bones.get("hand_fk.R") or rig.data.bones.get("DEF-hand.R")
    if hand_bone is None:
        raise RuntimeError("Rigify has no right hand bone for the hand close-up")
    hand_target = rig.matrix_world @ ((hand_bone.head_local + hand_bone.tail_local) * 0.5)
    hand_path = output_dir / "fighter-family-hand.png"
    hand_dir = (front + side * 0.45).normalized()
    _make_camera("ReviewCamera_hand", hand_target, hand_dir, 0.48, (512, 512), hand_path)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    paths["hand"] = str(hand_path)

    stress_path = output_dir / "fighter-family-stress-arm.png"
    _make_camera("ReviewCamera_stress", body_target, front, 2.02, (512, 768), stress_path)
    scene.frame_set(27)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    paths["stress_arm_frame_27"] = str(stress_path)
    for frame, suffix in ((28, "frame-28"), (52, "hip-leg-frame-52")):
        path = output_dir / f"fighter-family-stress-{suffix}.png"
        scene.camera = bpy.data.objects.get("ReviewCamera_front")
        scene.render.filepath = str(path)
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
        paths[f"stress_{suffix.replace('-', '_')}"] = str(path)
    garment_stress_path = output_dir / "fighter-family-garment-stress-hip-leg-frame-52.png"
    _make_camera("ReviewCamera_garment_stress", garment_center, front, 0.70, (512, 512), garment_stress_path)
    scene.frame_set(52)
    bpy.context.view_layer.update()
    bpy.ops.render.render(write_still=True)
    paths["garment_stress_hip_leg_frame_52"] = str(garment_stress_path)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    scene.camera = bpy.data.objects.get("ReviewCamera_front")
    return paths


def _mesh_world_points(obj: bpy.types.Object) -> list[Vector]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    evaluated.to_mesh_clear()
    return points


def _garment_clearance_metrics(body: bpy.types.Object, garment: bpy.types.Object) -> dict[str, Any]:
    """Measure matched skin-to-shell offsets and nearest surface separation in the live pose."""
    solidify = next((modifier for modifier in garment.modifiers if modifier.type == "SOLIDIFY"), None)
    if solidify is None:
        return {"status": "missing_shell_thickness_modifier"}
    was_visible = solidify.show_viewport
    solidify.show_viewport = False
    topology_modifiers = [(modifier, modifier.show_viewport) for modifier in body.modifiers
                          if modifier.type == "MASK"]
    for modifier, _visible in topology_modifiers:
        modifier.show_viewport = False
    body_mesh = garment_mesh = None
    try:
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated_body = body.evaluated_get(depsgraph)
        evaluated_garment = garment.evaluated_get(depsgraph)
        body_mesh = evaluated_body.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        garment_mesh = evaluated_garment.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        attribute = garment_mesh.attributes.get("body_source_vertex_index")
        if attribute is None or attribute.domain != "POINT" or attribute.data_type != "INT":
            return {"status": "source_vertex_map_missing"}
        if len(attribute.data) != len(garment_mesh.vertices):
            return {"status": "source_vertex_map_size_mismatch"}

        body_points = [evaluated_body.matrix_world @ vertex.co for vertex in body_mesh.vertices]
        garment_points = [evaluated_garment.matrix_world @ vertex.co for vertex in garment_mesh.vertices]
        normals_xform = evaluated_body.matrix_world.to_3x3().inverted().transposed()
        garment_normals_xform = evaluated_garment.matrix_world.to_3x3().inverted().transposed()
        signed_offsets: list[float] = []
        matched_samples: list[tuple[float, int, int, Vector, Vector]] = []
        nearest_distances: list[float] = []
        for garment_index, point in enumerate(garment_points):
            source_index = int(attribute.data[garment_index].value)
            if not 0 <= source_index < len(body_mesh.vertices):
                return {"status": "source_vertex_index_out_of_range"}
            normal = normals_xform @ body_mesh.vertices[source_index].normal
            if normal.length < 1e-8:
                continue
            normal.normalize()
            offset = float((point - body_points[source_index]).dot(normal))
            signed_offsets.append(offset)
            matched_samples.append((offset, garment_index, source_index, point, body_points[source_index]))

        visible_group = body.vertex_groups.get("body")
        visible_skin = {vertex.index for vertex in body.data.vertices
                        if any(assignment.group == visible_group.index and assignment.weight > 0.5
                               for assignment in vertex.groups)} if visible_group is not None else set()
        body_tree = BVHTree.FromPolygons(
            body_points,
            [tuple(polygon.vertices) for polygon in body_mesh.polygons
             if all(index in visible_skin for index in polygon.vertices)],
            all_triangles=False,
        )
        for point in garment_points:
            nearest = body_tree.find_nearest(point)
            if nearest is not None and nearest[3] is not None:
                nearest_distances.append(float(nearest[3]))
        if not signed_offsets or not nearest_distances:
            return {"status": "no_clearance_samples"}
        source_faces = {tuple(sorted(polygon.vertices)): polygon
                        for polygon in body_mesh.polygons}
        face_normal_dots: list[float] = []
        face_centroid_offsets: list[float] = []
        for polygon in garment_mesh.polygons:
            source_ids = tuple(sorted(int(attribute.data[index].value) for index in polygon.vertices))
            source_polygon = source_faces.get(source_ids)
            if source_polygon is None:
                continue
            body_normal = (normals_xform @ source_polygon.normal).normalized()
            garment_normal = (garment_normals_xform @ polygon.normal).normalized()
            body_center = sum((body_points[index] for index in source_polygon.vertices), Vector()) / len(source_polygon.vertices)
            garment_center = sum((garment_points[index] for index in polygon.vertices), Vector()) / len(polygon.vertices)
            face_normal_dots.append(float(body_normal.dot(garment_normal)))
            face_centroid_offsets.append(float((garment_center - body_center).dot(body_normal)))
        return {
            "status": "measured",
            "sampled_vertices": len(signed_offsets),
            "matched_signed_offset_min_m": round(min(signed_offsets), 7),
            "matched_signed_offset_median_m": round(sorted(signed_offsets)[len(signed_offsets) // 2], 7),
            "matched_signed_offset_max_m": round(max(signed_offsets), 7),
            "matched_vertices_at_or_below_1mm": sum(value <= 0.001 for value in signed_offsets),
            "worst_matched_samples": [
                {"offset_m": round(offset, 7), "garment_vertex": garment_index,
                 "body_vertex": source_index,
                 "garment_world_m": [round(float(v), 5) for v in point],
                 "body_world_m": [round(float(v), 5) for v in body_point]}
                for offset, garment_index, source_index, point, body_point
                in sorted(matched_samples, key=lambda sample: sample[0])[:5]
            ],
            "nearest_body_surface_min_m": round(min(nearest_distances), 7),
            "nearest_vertices_at_or_below_1mm": sum(value <= 0.001 for value in nearest_distances),
            "matched_faces": len(face_centroid_offsets),
            "face_normal_dot_min": round(min(face_normal_dots), 7) if face_normal_dots else None,
            "face_normal_opposed_count": sum(value < 0.0 for value in face_normal_dots),
            "face_centroid_offset_min_m": round(min(face_centroid_offsets), 7) if face_centroid_offsets else None,
            "face_centroids_at_or_below_1mm": sum(value <= 0.001 for value in face_centroid_offsets),
            "interpretation": "Sampled corresponding-vertex offsets and unsigned nearest-surface distances; not cloth simulation or a whole-mesh collision proof.",
        }
    finally:
        if body_mesh is not None:
            evaluated_body.to_mesh_clear()
        if garment_mesh is not None:
            evaluated_garment.to_mesh_clear()
        solidify.show_viewport = was_visible
        for modifier, visible in topology_modifiers:
            modifier.show_viewport = visible
        bpy.context.view_layer.update()


def _bounds(points: list[Vector]) -> dict[str, list[float]] | None:
    if not points:
        return None
    minimum = [min(float(point[axis]) for point in points) for axis in range(3)]
    maximum = [max(float(point[axis]) for point in points) for axis in range(3)]
    return {
        "min": [round(value, 7) for value in minimum],
        "max": [round(value, 7) for value in maximum],
        "dimensions": [round(maximum[i] - minimum[i], 7) for i in range(3)],
    }


def _weighted_group_measure(body: bpy.types.Object, name: str) -> dict[str, Any]:
    """Measure the stored base mesh vertices with meaningful rig weights."""
    group = body.vertex_groups.get(name)
    if group is None:
        return {"vertex_count": 0, "bounds_stored_base_world_m": None}
    points = [body.matrix_world @ vertex.co for vertex in body.data.vertices
              if any(item.group == group.index and item.weight > 0.05 for item in vertex.groups)]
    return {"vertex_count": len(points), "bounds_stored_base_world_m": _bounds(points)}


def collect_scene_state() -> dict[str, Any]:
    """Structured inspection for the persisted scene; call after reopening it."""
    body = bpy.data.objects.get("Human")
    rig = bpy.data.objects.get("Human.rigify")
    if body is None or body.type != "MESH" or rig is None or rig.type != "ARMATURE":
        raise RuntimeError("reopened preset is missing its Human body mesh or Rigify armature")
    garment = next((obj for obj in bpy.data.objects
                    if obj.type == "MESH" and obj.get("diagnostic_layer") == "clothing"), None)

    scene = bpy.context.scene
    body_points = _mesh_world_points(body)
    body_bounds = _bounds(body_points)
    shape_keys = body.data.shape_keys.key_blocks if body.data.shape_keys else []
    body_materials = [material.name for material in body.data.materials if material]
    body_material_polygon_counts = {
        material.name: sum(polygon.material_index == index for polygon in body.data.polygons)
        for index, material in enumerate(body.data.materials) if material
    }
    armature_modifiers = [modifier for modifier in body.modifiers if modifier.type == "ARMATURE"]
    deform_bones = {bone.name for bone in rig.data.bones if bone.use_deform}
    armature_bind = [modifier.object.name if modifier.object else None for modifier in armature_modifiers]
    armature_stack = [{
        "name": modifier.name,
        "target": modifier.object.name if modifier.object else None,
        "vertex_group": modifier.vertex_group,
        "preserve_volume": bool(modifier.use_deform_preserve_volume),
        "use_vertex_groups": bool(modifier.use_vertex_groups),
        "use_bone_envelopes": bool(modifier.use_bone_envelopes),
        "show_viewport": bool(modifier.show_viewport),
        "show_render": bool(modifier.show_render),
    } for modifier in armature_modifiers]
    expected_stack = [
        {"name": "Armature", "target": rig.name, "vertex_group": "", "preserve_volume": False,
         "use_vertex_groups": True, "use_bone_envelopes": False, "show_viewport": True, "show_render": True},
        {"name": "Armature PV", "target": rig.name, "vertex_group": "mhmask-preserve-volume",
         "preserve_volume": True, "use_vertex_groups": True, "use_bone_envelopes": False,
         "show_viewport": True, "show_render": True},
    ]

    scene.frame_set(1)
    bpy.context.view_layer.update()
    baseline_points = _mesh_world_points(body)
    baseline_bounds = _bounds(baseline_points)
    sampled = []
    for frame in (1, 27, 28, 52):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        points = _mesh_world_points(body)
        displacements = [(points[i] - baseline_points[i]).length for i in range(min(len(points), len(baseline_points)))]
        bounds = _bounds(points)
        sampled.append({
            "frame": frame,
            "time_s": round((frame - 1) / max(1, scene.render.fps), 7),
            "body_bounds_world_m": bounds,
            "ground_clearance_min_z_m": bounds["min"][2] if bounds else None,
            "vertices_changed_gt_1e-5_from_frame_1": sum(value > 1e-5 for value in displacements),
            "max_vertex_displacement_from_frame_1_m": round(max(displacements, default=0.0), 7),
            "rig_control_rotation": [round(float(value), 7) for value in rig.pose.bones["upper_arm_fk.R"].rotation_euler],
            "leg_control_rotation": [round(float(value), 7) for value in rig.pose.bones["thigh_fk.L"].rotation_euler],
            "garment_clearance": _garment_clearance_metrics(body, garment) if garment is not None else None,
        })

    modifier_probe: dict[str, Any] = {"frame": 27, "status": "not_measured"}
    if len(armature_modifiers) == 2:
        scene.frame_set(27)
        bpy.context.view_layer.update()
        both_points = _mesh_world_points(body)
        primary, preserve_volume = armature_modifiers
        try:
            preserve_volume.show_viewport = False
            primary_points = _mesh_world_points(body)
            preserve_volume.show_viewport = True
            primary.show_viewport = False
            pv_points = _mesh_world_points(body)
        finally:
            primary.show_viewport = True
            preserve_volume.show_viewport = True
            bpy.context.view_layer.update()
        if len(both_points) == len(primary_points) == len(pv_points):
            primary_deltas = [(a - b).length for a, b in zip(both_points, primary_points)]
            pv_deltas = [(a - b).length for a, b in zip(both_points, pv_points)]
            modifier_probe = {
                "frame": 27,
                "status": "measured",
                "both_vs_main_only_max_m": round(max(primary_deltas, default=0.0), 8),
                "both_vs_main_only_vertices_gt_1e-5_m": sum(value > 1e-5 for value in primary_deltas),
                "both_vs_pv_only_max_m": round(max(pv_deltas, default=0.0), 7),
                "both_vs_pv_only_vertices_gt_1e-5_m": sum(value > 1e-5 for value in pv_deltas),
            }

    scene.frame_set(1)
    bpy.context.view_layer.update()
    orientation = _face_basis(rig)
    shoulder_r = rig.matrix_world @ rig.data.bones["shoulder.R"].head_local
    shoulder_l = rig.matrix_world @ rig.data.bones["shoulder.L"].head_local
    side_vector = (shoulder_l - shoulder_r).normalized()
    head_world = rig.matrix_world @ rig.data.bones["head"].head_local
    iris_centers = []
    for name in ("Face_Iris_L", "Face_Iris_R"):
        iris_obj = bpy.data.objects.get(name)
        points = _mesh_world_points(iris_obj) if iris_obj is not None else []
        if points:
            iris_centers.append(sum(points, Vector()) / len(points))
    face_hand_metrics = {
        "head_weighted_group": _weighted_group_measure(body, "DEF-spine.006"),
        "left_hand_weighted_group": _weighted_group_measure(body, "DEF-hand.L"),
        "right_hand_weighted_group": _weighted_group_measure(body, "DEF-hand.R"),
        "iris_center_distance_m": round((iris_centers[0] - iris_centers[1]).length, 7)
        if len(iris_centers) == 2 else None,
    }
    relevant_bones = {}
    for name in ("root", "DEF-spine", "DEF-spine.003", "DEF-spine.006", "head", "shoulder.L", "shoulder.R",
                 "upper_arm_fk.L", "upper_arm_fk.R", "hand_fk.L", "hand_fk.R", "thigh_fk.L", "thigh_fk.R"):
        bone = rig.data.bones.get(name)
        if bone:
            relevant_bones[name] = {
                "deform": bool(bone.use_deform),
                "head_world_m": [round(float(value), 7) for value in rig.matrix_world @ bone.head_local],
                "tail_world_m": [round(float(value), 7) for value in rig.matrix_world @ bone.tail_local],
                "parent": bone.parent.name if bone.parent else None,
            }

    objects = []
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        evaluated_points = _mesh_world_points(obj)
        objects.append({
            "name": obj.name,
            "vertices_stored": len(obj.data.vertices),
            "polygons_stored": len(obj.data.polygons),
            "triangles_stored": sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons),
            "world_bounds_m": _bounds(evaluated_points),
            "materials": [material.name for material in obj.data.materials if material],
            "vertex_groups": [group.name for group in obj.vertex_groups],
            "armature_targets": [modifier.object.name if modifier.object else None for modifier in obj.modifiers if modifier.type == "ARMATURE"],
            "modifier_stack": [{
                "name": modifier.name,
                "type": modifier.type,
                "target": modifier.object.name if modifier.type == "ARMATURE" and modifier.object else None,
                "vertex_group": modifier.vertex_group if modifier.type == "ARMATURE" else None,
                "thickness_m": round(float(modifier.thickness), 7) if modifier.type == "SOLIDIFY" else None,
                "show_viewport": bool(modifier.show_viewport),
                "show_render": bool(modifier.show_render),
            } for modifier in obj.modifiers],
            "diagnostic_layer": obj.get("diagnostic_layer"),
            "attachment_bone": obj.get("attachment_bone"),
            "garment_style": obj.get("garment_style"),
            "garment_representation": obj.get("garment_representation"),
        })

    return {
        "schema_version": "blender_model_preset_inspection.v1",
        "family_id": body.get("asset_family_id"),
        "asset_status": body.get("art_status", "diagnostic_only"),
        "blender": {
            "version": bpy.app.version_string,
            "build_hash": bpy.app.build_hash.decode("utf-8") if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash),
            "filepath": bpy.data.filepath,
            "render_engine": scene.render.engine,
            "fps": scene.render.fps,
            "world_up": "Z",
        },
        "character": {
            "body_name": body.name,
            "body_vertices_stored": len(body.data.vertices),
            "body_polygons_stored": len(body.data.polygons),
            "body_triangles_stored": sum(max(0, len(poly.vertices) - 2) for poly in body.data.polygons),
            "body_bounds_frame_1_world_m": baseline_bounds,
            "body_materials": body_materials,
            "body_material_polygon_counts": body_material_polygon_counts,
            "clothing_representation": body.get("clothing_representation"),
            "shape_keys": [{"name": key.name, "value": round(float(key.value), 6),
                            "slider_min": round(float(key.slider_min), 6), "slider_max": round(float(key.slider_max), 6)}
                           for key in shape_keys],
            "vertex_group_count": len(body.vertex_groups),
            "armature_modifier_targets": armature_bind,
            "armature_modifier_stack": armature_stack,
            "body_custom_controls_json": body.get("preset_controls_json"),
            "head_origin_world_m": [round(float(value), 7) for value in head_world],
            "head_forward_world": [round(float(value), 7) for value in orientation["forward"]],
            "head_up_world": [round(float(value), 7) for value in orientation["up"]],
            "bilateral_shoulder_side_world": [round(float(value), 7) for value in side_vector],
        },
        "rig": {
            "name": rig.name,
            "bone_count": len(rig.data.bones),
            "deform_bone_count": len(deform_bones),
            "required_deform_bones_present": all(name in deform_bones for name in ("DEF-spine.003", "DEF-spine.006", "DEF-thigh.L", "DEF-thigh.R")),
            "fk_controls_present": all(rig.pose.bones.get(name) for name in ("upper_arm_fk.L", "upper_arm_fk.R")),
            "pose_action_present": bool(rig.animation_data and rig.animation_data.action),
            "pose_action_name": rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None,
            "style_controls": {key: rig.get(key) for key in ("hair_style", "clothing_style", "skin_palette", "clothing_palette")},
            "leg_stress_control": "thigh_fk.L",
            "key_bones": relevant_bones,
        },
        "garment": {
            "present": garment is not None,
            "object_name": garment.name if garment is not None else None,
            "style": garment.get("garment_style") if garment is not None else None,
            "representation": garment.get("garment_representation") if garment is not None else None,
            "surface_ease_m": garment.get("surface_ease_m") if garment is not None else None,
            "source_vertex_attribute": "body_source_vertex_index" if garment is not None and garment.data.attributes.get("body_source_vertex_index") else None,
            "material_names": [material.name for material in garment.data.materials if material] if garment is not None else [],
            "stored_vertex_count": len(garment.data.vertices) if garment is not None else 0,
            "stored_polygon_count": len(garment.data.polygons) if garment is not None else 0,
            "weighted_vertex_count": sum(bool(vertex.groups) for vertex in garment.data.vertices) if garment is not None else 0,
            "vertex_group_count": len(garment.vertex_groups) if garment is not None else 0,
            "armature_modifier_targets": [modifier.object.name if modifier.object else None
                                           for modifier in garment.modifiers if modifier.type == "ARMATURE"] if garment is not None else [],
            "solidify_modifier": next(({
                "name": modifier.name,
                "thickness_m": round(float(modifier.thickness), 7),
                "offset": round(float(modifier.offset), 4),
                "use_even_offset": bool(modifier.use_even_offset),
                "use_rim": bool(modifier.use_rim),
            } for modifier in garment.modifiers if modifier.type == "SOLIDIFY"), None) if garment is not None else None,
        },
        "objects": objects,
        "stress_samples": sampled,
        "modifier_probe": modifier_probe,
        "face_hand_metrics": face_hand_metrics,
        "floor": {
            "object_present": bpy.data.objects.get("Diagnostic_Floor") is not None,
            "z_m": 0.0,
            "baseline_body_clearance_m": baseline_bounds["min"][2] if baseline_bounds else None,
        },
        "verdict": {
            "saved_scene_integrity": "pass" if body_bounds and body_materials and armature_stack == expected_stack else "fail",
            "rig_deformation_probe": "pass" if len(sampled) >= 3 and sampled[1]["vertices_changed_gt_1e-5_from_frame_1"] > 0 else "fail",
            "garment_geometry": "pass" if garment is not None and len(garment.data.vertices) >= 500 and len(garment.data.polygons) >= 250 else "missing_or_undersized",
            "face_hand_hair_clothing_presence": "pending visual review",
            "art_status": "diagnostic only; not reviewed or approved; no fighter likeness claim",
        },
    }


def build_native_preset(output_path: str | Path, *, controls: dict[str, Any] | None = None,
                        render_dir: str | Path | None = None) -> dict[str, Any]:
    """Build one editable MPFB/Rigify family member and return recorded state."""
    resolved = resolve_controls(controls)
    runtime = validate_local_runtime()
    addon_states = _enable_local_addons()
    _clear_scene()

    HumanObjectProperties = _mpfb_symbol("mpfb.entities.objectproperties", "HumanObjectProperties")
    TargetService = _mpfb_symbol("mpfb.services.targetservice", "TargetService")
    LocationService = _mpfb_symbol("mpfb.services.locationservice", "LocationService")
    targets_root = Path(LocationService.get_mpfb_data("targets")).resolve()
    if targets_root != TARGET_CACHE_ROOT.resolve():
        raise RuntimeError(f"MPFB target root differs from the pinned local package: {targets_root}")

    bpy.context.scene.render.fps = 24
    bpy.ops.mpfb.create_human()
    human = bpy.context.view_layer.objects.active
    if human is None or human.type != "MESH" or human.name != "Human":
        raise RuntimeError("MPFB did not create the expected Human base mesh")

    macro_keys = ("height", "muscle", "weight", "proportions")
    for key in macro_keys:
        HumanObjectProperties.set_value(key, resolved["body"][key], entity_reference=human)
    # Masculine-coded generic sports base. This is a family parameter, not a fighter likeness.
    # MPFB's phenotype scale is 0=female, 1=male. This is a generic athletic
    # starter, not a likeness; keep the chosen value explicit in the manifest.
    HumanObjectProperties.set_value("gender", 0.86, entity_reference=human)
    TargetService.reapply_macro_details(human)

    applied_face_targets: dict[str, list[dict[str, Any]]] = {}
    for control, target_spec in FACE_TARGETS.items():
        raw_targets = target_spec["asset"]
        targets = raw_targets if isinstance(raw_targets, list) else [raw_targets]
        applied_face_targets[control] = []
        for relative in targets:
            target_path = (targets_root / relative).resolve()
            if not _path_is_inside(target_path, targets_root) or not target_path.is_file():
                raise RuntimeError(f"required MPFB CC0 target is missing/outside the pinned target root: {target_path}")
            before = set(key.name for key in human.data.shape_keys.key_blocks) if human.data.shape_keys else set()
            weight = float(resolved["face"][control])
            TargetService.load_target(human, str(target_path), weight=weight)
            after = set(key.name for key in human.data.shape_keys.key_blocks) if human.data.shape_keys else set()
            new_names = sorted(after - before)
            if not new_names:
                raise RuntimeError(f"MPFB target {relative} failed to create a face/hand shape key")
            key = human.data.shape_keys.key_blocks[new_names[-1]]
            key.slider_min = 0.0
            key.slider_max = float(target_spec["maximum"])
            applied_face_targets[control].append({"target": relative, "shape_key": key.name, "value": weight})

    bpy.ops.mpfb.add_rigify_rig()
    armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError("MPFB generated no Rigify armature")
    rig = max(armatures, key=lambda obj: len(obj.data.bones))
    if rig.name != "Human.rigify":
        raise RuntimeError(f"unexpected generated Rigify object name: {rig.name}")
    body_modifiers = [modifier for modifier in human.modifiers if modifier.type == "ARMATURE"]
    if (len(body_modifiers) != 2 or
            [modifier.name for modifier in body_modifiers] != ["Armature", "Armature PV"] or
            any(modifier.object != rig for modifier in body_modifiers) or
            body_modifiers[0].vertex_group or body_modifiers[0].use_deform_preserve_volume or
            body_modifiers[1].vertex_group != "mhmask-preserve-volume" or
            not body_modifiers[1].use_deform_preserve_volume):
        raise RuntimeError("MPFB body has an unexpected Rigify/preserve-volume modifier stack")

    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj is not human:
            obj.hide_render = True
            # Rigify widget meshes can live in its hidden/non-view-layer collection;
            # hide_set() raises for those objects, while object-level flags are safe.
            obj.hide_viewport = True
    human.hide_render = False
    human.hide_viewport = False

    skin = _material("MM_Skin_" + resolved["skin_palette"], SKIN_PALETTES[resolved["skin_palette"]], roughness=0.61)
    costume = _material("MM_Costume_" + resolved["clothing_palette"], CLOTHING_PALETTES[resolved["clothing_palette"]], roughness=0.76)
    hair_material = _material("MM_Hair_Ink", (0.017, 0.020, 0.028, 1.0), roughness=0.42)
    iris = _material("MM_Eye_Iris", (0.18, 0.065, 0.025, 1.0), roughness=0.31)
    pupil = _material("MM_Eye_Pupil", (0.008, 0.006, 0.009, 1.0), roughness=0.24)
    brow = _material("MM_Face_Detail", (0.028, 0.016, 0.018, 1.0), roughness=0.64)
    human.data.materials.append(skin)
    for polygon in human.data.polygons:
        polygon.use_smooth = True

    face_basis = _face_basis(rig)
    head_deform = _find_deform_bone(rig, "DEF-spine.006", "DEF-head")
    facial_objects = _add_face_details(human, face_basis,
                                      {"iris": iris, "pupil": pupil, "brow": brow},
                                      rig, head_deform)
    hair_objects = _hair_geometry(face_basis, resolved["hair_style"], hair_material, rig, head_deform)
    clothing_geometry = _create_skinned_garment(human, rig, resolved["clothing_style"], costume)
    _add_floor_and_lighting()
    pose_metadata = _configure_rig_pose(rig)

    controls_json = json.dumps(resolved, sort_keys=True, separators=(",", ":"))
    human["asset_family_id"] = FAMILY_ID
    human["art_status"] = "diagnostic_only"
    human["clothing_representation"] = "separate_editable_skinned_garment_shell"
    human["preset_controls_json"] = controls_json
    human["applied_mpfb_targets_json"] = json.dumps(applied_face_targets, sort_keys=True, separators=(",", ":"))
    rig["asset_family_id"] = FAMILY_ID
    rig["hair_style"] = resolved["hair_style"]
    rig["clothing_style"] = resolved["clothing_style"]
    rig["skin_palette"] = resolved["skin_palette"]
    rig["clothing_palette"] = resolved["clothing_palette"]
    for prop_name, prop_value, low, high in (
        ("body_height", resolved["body"]["height"], *BODY_BOUNDS["height"]),
        ("body_muscle", resolved["body"]["muscle"], *BODY_BOUNDS["muscle"]),
        ("body_weight", resolved["body"]["weight"], *BODY_BOUNDS["weight"]),
        ("body_proportions", resolved["body"]["proportions"], *BODY_BOUNDS["proportions"]),
    ):
        rig[prop_name] = float(prop_value)
        rig.id_properties_ui(prop_name).update(min=low, max=high, soft_min=low, soft_max=high, description="Bounded MPFB family control; rebuild to apply")

    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.camera = None
    manifest = family_manifest()
    manifest.update({
        "asset_id": "native-fighter-family-diagnostic-v1.1",
        "revision": "r2",
        "created_with": runtime,
        "enabled_addons": addon_states,
        "controls_applied": resolved,
        "base_phenotype_gender": 0.86,
        "mpfb_targets_applied": applied_face_targets,
        "attached_diagnostic_objects": {"face": facial_objects, "hair": hair_objects,
                                        "clothing": [clothing_geometry["object_name"]]},
        "diagnostic_clothing": clothing_geometry,
        "rig_pose_probe": pose_metadata,
        "artifact": {"path": str(output.relative_to(REPO_ROOT).as_posix()) if _path_is_inside(output, REPO_ROOT) else output.name},
    })
    bpy.context.scene["model_preset_manifest_json"] = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    _save_mainfile_without_backup(output)

    render_paths: dict[str, str] = {}
    if render_dir is not None:
        render_paths = _render_review_views(rig, Path(render_dir).resolve())
        # Restore the neutral pose and camera before saving the deliverable scene.
        scene.frame_set(1)
        bpy.context.view_layer.update()
        _save_mainfile_without_backup(output)
    return {
        "manifest": manifest,
        "runtime": runtime,
        "enabled_addons": addon_states,
        "controls_applied": resolved,
        "applied_mpfb_targets": applied_face_targets,
        "pose_probe": pose_metadata,
        "render_paths": render_paths,
        "asset_path": str(output),
        "asset_sha256": _sha256(output),
        "inspection": collect_scene_state(),
    }
