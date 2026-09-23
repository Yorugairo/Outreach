"""Narrow, read-only Rigify planted-foot probe for the pinned v1.1 scene.

This file runs inside Blender. The three poses and camera exist only in memory;
the source .blend is never saved. Evaluated vertex positions are copied before
the temporary mesh is released so each pose has a valid, stable witness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[5]
SOURCE_RELATIVE = "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"
SOURCE_SHA256 = "5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade"
REVIEW_RELATIVE = "content/video_engine/review/model-engines/benchmark-v1/3d/foot-contact-probe"
SLIP_BUDGET_M = 0.005
CLEARANCE_BUDGET_M = 0.005
UNCOMPENSATED_MIN_SLIP_M = 0.020
ROOT_SHIFT_M = 0.050
SCHEMA = "model_foot_contact_probe.v1"


class ContactProbeError(RuntimeError):
    """The pinned diagnostic could not produce a trustworthy measurement."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _world_matrix(rig, pose_bone):
    return rig.matrix_world @ pose_bone.matrix


def _vector(vector):
    return [round(float(component), 8) for component in vector]


def _bone_state(rig, name):
    bone = rig.pose.bones[name]
    world = _world_matrix(rig, bone)
    return {
        "name": name,
        "parent": bone.parent.name if bone.parent else None,
        "location_local": _vector(bone.location),
        "translation_world_m": _vector(world.translation),
        "rotation_world_quaternion_xyzw": _vector(
            (world.to_quaternion().x, world.to_quaternion().y,
             world.to_quaternion().z, world.to_quaternion().w)
        ),
    }


def _foot_group_indices(body):
    names = ("DEF-foot.L", "DEF-toe.L", "DEF-foot.R", "DEF-toe.R")
    missing = [name for name in names if body.vertex_groups.get(name) is None]
    if missing:
        raise ContactProbeError(f"Human lacks anatomical foot skin groups: {missing}")
    return ({body.vertex_groups[name].index for name in names[:2]},
            {body.vertex_groups[name].index for name in names[2:]})


def _evaluated_points(body, depsgraph):
    left_groups, right_groups = _foot_group_indices(body)
    evaluated = body.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise ContactProbeError("Human evaluated mesh is unavailable")
    try:
        world = evaluated.matrix_world.copy()
        points = [tuple(float(component) for component in (world @ vertex.co))
                  for vertex in mesh.vertices]
        weights = [
            (sum(float(group.weight) for group in vertex.groups if group.group in left_groups),
             sum(float(group.weight) for group in vertex.groups if group.group in right_groups))
            for vertex in mesh.vertices
        ]
        return points, weights
    finally:
        evaluated.to_mesh_clear()


def _witness_indices(points, weights, foot_world, floor_z):
    fx, fy, _ = foot_world
    candidates = [
        index for index, (x, y, z) in enumerate(points)
        if abs(x - fx) <= 0.16 and abs(y - fy) <= 0.30
        and floor_z - 0.005 <= z <= floor_z + 0.010
        and weights[index][0] >= 0.20 and weights[index][1] <= 0.05
    ]
    if len(candidates) < 16:
        raise ContactProbeError(f"left-foot sole witness has only {len(candidates)} evaluated vertices")
    return candidates


def _sample(bpy, rig, body, label, floor_z, witness_indices=None):
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points, weights = _evaluated_points(body, depsgraph)
    foot_world = _vector(_world_matrix(rig, rig.pose.bones["foot_ik.L"]).translation)
    if witness_indices is None:
        witness_indices = _witness_indices(points, weights, foot_world, floor_z)
    if max(witness_indices) >= len(points):
        raise ContactProbeError("evaluated Human topology changed between contact poses")
    if any(weights[index][0] < 0.20 or weights[index][1] > 0.05 for index in witness_indices):
        raise ContactProbeError("anatomical foot weights changed between contact poses")
    patch = [points[index] for index in witness_indices]
    skin_weights = [[round(weights[index][0], 8), round(weights[index][1], 8)]
                    for index in witness_indices]
    if any(not math.isfinite(value) for point in patch for value in point):
        raise ContactProbeError("evaluated witness contains a non-finite coordinate")
    names = ("root", "foot_ik.L", "toe_ik.L", "thigh_parent.L",
             "thigh_ik_target.L", "VIS_thigh_ik_pole.L", "DEF-foot.L")
    missing = [name for name in names if name not in rig.pose.bones]
    if missing:
        raise ContactProbeError(f"required Rigify controls missing: {missing}")
    return {
        "label": label,
        "frame": bpy.context.scene.frame_current,
        "evaluated_human_vertex_count": len(points),
        "witness_vertex_count": len(patch),
        "witness_indices": witness_indices,
        "witness_world_m": [_vector(point) for point in patch],
        "witness_combined_skin_weights": skin_weights,
        "witness_min_z_m": round(min(point[2] for point in patch), 8),
        "witness_centroid_world_m": _vector(tuple(sum(point[axis] for point in patch) / len(patch)
                                                 for axis in range(3))),
        "controls": {name: _bone_state(rig, name) for name in names},
        "left_leg_ik_fk": float(rig.pose.bones["thigh_parent.L"]["IK_FK"]),
        "left_leg_pole_vector_enabled": bool(rig.pose.bones["thigh_parent.L"]["pole_vector"]),
    }


def _distance(a, b):
    return math.dist(a, b)


def _compare(neutral, moved):
    first = neutral["witness_world_m"]
    second = moved["witness_world_m"]
    if len(first) != len(second) or neutral["witness_indices"] != moved["witness_indices"]:
        raise ContactProbeError("witness correspondence changed between contact poses")
    slip = [math.dist(a[:2], b[:2]) for a, b in zip(first, second)]
    full = [_distance(a, b) for a, b in zip(first, second)]
    return {
        "max_witness_slip_xy_m": round(max(slip), 8),
        "mean_witness_slip_xy_m": round(sum(slip) / len(slip), 8),
        "max_witness_displacement_xyz_m": round(max(full), 8),
        "foot_ik_control_slip_xy_m": round(math.dist(
            neutral["controls"]["foot_ik.L"]["translation_world_m"][:2],
            moved["controls"]["foot_ik.L"]["translation_world_m"][:2]), 8),
        "clearance_change_m": round(moved["witness_min_z_m"] - neutral["witness_min_z_m"], 8),
        "root_shift_xyz_m": _vector(tuple(
            moved["controls"]["root"]["translation_world_m"][axis]
            - neutral["controls"]["root"]["translation_world_m"][axis]
            for axis in range(3))),
    }


def _render_camera(bpy, rig):
    from mathutils import Vector

    scene = bpy.context.scene
    camera_data = bpy.data.cameras.new("FootContactProbeCameraData")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 0.80
    camera = bpy.data.objects.new("FootContactProbeCamera", camera_data)
    scene.collection.objects.link(camera)
    target = _world_matrix(rig, rig.pose.bones["foot_ik.L"]).translation + Vector((0.0, -0.04, 0.20))
    camera.location = target + Vector((1.20, -1.80, 0.75))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    return {
        "name": camera.name,
        "location_world_m": _vector(camera.location),
        "rotation_euler_rad": _vector(camera.rotation_euler),
        "ortho_scale_m": camera_data.ortho_scale,
        "resolution_px": [640, 640],
    }


def _render(bpy, output: Path, label: str):
    path = output / f"{label}.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise ContactProbeError(f"Blender did not produce a valid {label} PNG")
    return {"path": path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size}


def run_probe(bpy, source: Path, output: Path):
    if bpy.app.version_string != "5.2.2 LTS":
        raise ContactProbeError(f"Blender 5.2.2 LTS required, got {bpy.app.version_string}")
    if sha256_file(source) != SOURCE_SHA256:
        raise ContactProbeError("source hash differs from pinned v1.1 scene")
    result = bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    if "FINISHED" not in result:
        raise ContactProbeError("Blender could not open the pinned scene")
    if sha256_file(source) != SOURCE_SHA256:
        raise ContactProbeError("source hash changed while opening scene")
    scene = bpy.context.scene
    scene.frame_set(1)
    if scene.unit_settings.scale_length != 1.0:
        raise ContactProbeError("scene is not in 1-meter Blender units")
    rig = bpy.data.objects.get("Human.rigify")
    body = bpy.data.objects.get("Human")
    floor = bpy.data.objects.get("Diagnostic_Floor")
    if not rig or rig.type != "ARMATURE" or not body or body.type != "MESH" or not floor:
        raise ContactProbeError("pinned scene lacks Rigify, Human, or diagnostic floor")
    floor_z = min(float((floor.matrix_world @ vertex.co).z) for vertex in floor.data.vertices)
    root = rig.pose.bones.get("root")
    foot = rig.pose.bones.get("foot_ik.L")
    leg = rig.pose.bones.get("thigh_parent.L")
    if root is None or foot is None or leg is None:
        raise ContactProbeError("required root/left foot/leg controls missing")
    # The saved action keys IK_FK=1 at frame 1. Blender's render evaluation
    # reapplies that key. Override this single frame-1 key in memory so the
    # rest of the saved pose/action remains active for both samples and PNGs.
    saved_action = rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None
    if saved_action is None:
        raise ContactProbeError("pinned Rigify action is missing")
    leg["IK_FK"] = 0.0
    if not leg.keyframe_insert(data_path='["IK_FK"]', frame=1):
        raise ContactProbeError("could not override left-leg IK switch in memory")
    scene.frame_set(1)
    bpy.context.view_layer.update()
    if float(leg["IK_FK"]) != 0.0:
        raise ContactProbeError("left leg IK switch did not activate")
    original_root_basis = root.matrix_basis.copy()
    original_foot_basis = foot.matrix_basis.copy()
    neutral_foot_world = _world_matrix(rig, foot).copy()
    camera = _render_camera(bpy, rig)

    neutral = _sample(bpy, rig, body, "neutral", floor_z)
    indices = neutral["witness_indices"]
    renders = {"neutral": _render(bpy, output, "neutral")}

    root.location.x += ROOT_SHIFT_M
    bpy.context.view_layer.update()
    uncompensated = _sample(bpy, rig, body, "uncompensated", floor_z, indices)
    renders["uncompensated"] = _render(bpy, output, "uncompensated")

    root.matrix_basis = original_root_basis.copy()
    foot.matrix_basis = original_foot_basis.copy()
    bpy.context.view_layer.update()
    root.location.x += ROOT_SHIFT_M
    bpy.context.view_layer.update()
    foot.matrix = rig.matrix_world.inverted() @ neutral_foot_world
    bpy.context.view_layer.update()
    compensated = _sample(bpy, rig, body, "compensated", floor_z, indices)
    renders["compensated"] = _render(bpy, output, "compensated")

    uncompensated_delta = _compare(neutral, uncompensated)
    compensated_delta = _compare(neutral, compensated)
    checks = {
        "ik_mode_all_poses": all(pose["left_leg_ik_fk"] == 0.0
                                 for pose in (neutral, uncompensated, compensated)),
        "uncompensated_witness_slip_measurable": uncompensated_delta["mean_witness_slip_xy_m"] >= UNCOMPENSATED_MIN_SLIP_M,
        "uncompensated_root_shift_m": abs(uncompensated_delta["root_shift_xyz_m"][0] - ROOT_SHIFT_M) <= 0.001,
        "compensated_root_shift_m": abs(compensated_delta["root_shift_xyz_m"][0] - ROOT_SHIFT_M) <= 0.001,
        "compensated_control_held": compensated_delta["foot_ik_control_slip_xy_m"] <= SLIP_BUDGET_M,
        "compensated_witness_slip": compensated_delta["max_witness_slip_xy_m"] <= SLIP_BUDGET_M,
        "compensated_clearance_change": abs(compensated_delta["clearance_change_m"]) <= CLEARANCE_BUDGET_M,
        "compensated_floor_penetration": compensated["witness_min_z_m"] >= floor_z - CLEARANCE_BUDGET_M,
    }
    if sha256_file(source) != SOURCE_SHA256:
        raise ContactProbeError("source hash changed during probe")
    witness_raw = {
        "schema": "model_foot_contact_witness.v1",
        "evaluated_human_vertex_count": neutral["evaluated_human_vertex_count"],
        "vertex_indices": indices,
        "neutral_combined_skin_weights": neutral["witness_combined_skin_weights"],
        "world_coordinates_m": {
            label: pose["witness_world_m"] for label, pose in
            (("neutral", neutral), ("uncompensated", uncompensated),
             ("compensated", compensated))
        },
    }
    witness_path = output / "witness-patches.json"
    witness_path.write_text(json.dumps(witness_raw, sort_keys=True, separators=(",", ":"),
                                       allow_nan=False) + "\n", encoding="utf-8")
    compact_poses = {
        label: {key: value for key, value in pose.items()
                if key not in {"witness_indices", "witness_world_m",
                               "witness_combined_skin_weights"}}
        for label, pose in (("neutral", neutral), ("uncompensated", uncompensated),
                            ("compensated", compensated))
    }
    build_hash = bpy.app.build_hash
    if isinstance(build_hash, bytes):
        build_hash = build_hash.decode("ascii", errors="replace")
    return {
        "schema": SCHEMA,
        "status": "diagnostic_only",
        "verdict": "pass" if all(checks.values()) else "fail",
        "scope": "left-foot IK contact feasibility only; no full action, likeness, T5b, or HG2 approval",
        "source": {"path": SOURCE_RELATIVE, "sha256_before": SOURCE_SHA256,
                   "sha256_after": sha256_file(source), "mutated": False},
        "tool": {"name": "Blender", "version": bpy.app.version_string,
                 "build_hash": str(build_hash), "offline": True, "embedded_scripts": "disabled"},
        "binding_private": {"semantic_effector": "left_foot", "rig_object": rig.name,
                            "control": foot.name, "ik_switch": "thigh_parent.L.IK_FK=0"},
        "saved_action_retained": saved_action,
        "in_memory_frame_1_override": "thigh_parent.L.IK_FK: 1 -> 0; source action and scene not saved",
        "budgets_predeclared_m": {"root_shift": ROOT_SHIFT_M,
                                  "compensated_max_witness_slip_xy": SLIP_BUDGET_M,
                                  "compensated_clearance_change": CLEARANCE_BUDGET_M,
                                  "uncompensated_mean_witness_slip_min": UNCOMPENSATED_MIN_SLIP_M},
        "floor_world_z_m": round(floor_z, 8),
        "witness_selection": {
            "mesh": "evaluated Human",
            "anatomical_skin_groups_left": ["DEF-foot.L", "DEF-toe.L"],
            "anatomical_skin_groups_right_exclusion": ["DEF-foot.R", "DEF-toe.R"],
            "minimum_combined_left_weight": 0.20,
            "maximum_combined_right_weight": 0.05,
            "observed_minimum_left_weight": min(item[0] for item in neutral["witness_combined_skin_weights"]),
            "observed_maximum_right_weight": max(item[1] for item in neutral["witness_combined_skin_weights"]),
            "neutral_xy_radius_m": [0.16, 0.30],
            "neutral_floor_band_relative_m": [-0.005, 0.010],
            "stable_index_policy": "select once at neutral; copy same evaluated indices at all poses",
        },
        "witness_raw": {"path": witness_path.name, "sha256": sha256_file(witness_path),
                        "vertex_count": len(indices)},
        "camera": camera,
        "poses": compact_poses,
        "deltas_from_neutral": {"uncompensated": uncompensated_delta,
                                "compensated": compensated_delta},
        "checks": checks,
        "renders": renders,
    }


def _arguments():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args(argv)


def main():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    args = _arguments()
    source = Path(args.source).resolve(strict=True)
    output = Path(args.output).resolve(strict=True)
    if source != (ROOT / SOURCE_RELATIVE).resolve(strict=True):
        raise ContactProbeError("source must be the pinned v1.1 scene")
    if not output.is_relative_to((ROOT / REVIEW_RELATIVE).resolve(strict=True)):
        raise ContactProbeError("output must be inside foot-contact review quarantine")
    import bpy

    receipt = run_probe(bpy, source, output)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True,
                                                    allow_nan=False) + "\n", encoding="utf-8")
    print(f"CONTACT_PROBE_VERDICT={receipt['verdict']}")


if __name__ == "__main__":
    main()
