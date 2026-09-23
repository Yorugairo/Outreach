"""Offline Blender proof: native MPFB face targets on the existing v1.1 Rigify body.

This fixture writes diagnostic review assets only. It is not a likeness builder.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import types

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[6]
FIXTURE = Path(__file__).with_name("face-targets.v1.json")
BASELINE = ROOT / "content/video_engine/tests/fixtures/modeling/baseline"
TARGET_ROOT = BASELINE / "profile/extensions/user_default/mpfb/data/targets"
MPFB_PACKAGE = BASELINE / "tools/packages/mpfb-2.0.17.zip"
EXPECTED_PACKAGE_SHA = "923b0a0950b2b1d75440200b5457e9af9951e477b37a8e1537956f5f28b15c31"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def config() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def import_authoring():
    """Mirror the existing Blender fixture import without host-only jsonschema."""
    package_path = ROOT / "content/video_engine/src/modeling/blender"
    package = types.ModuleType("_face_proof_blender")
    package.__path__ = [str(package_path)]
    sys.modules[package.__name__] = package
    return importlib.import_module("_face_proof_blender.authoring")


def verify_runtime(document: dict) -> Path:
    benchmark = json.loads((BASELINE / "benchmark-inputs.json").read_text(encoding="utf-8"))
    expected = benchmark["tools"]["blender"]
    build_hash = bpy.app.build_hash.decode() if isinstance(bpy.app.build_hash, bytes) else str(bpy.app.build_hash)
    assert Path(bpy.app.binary_path).resolve() == Path(expected["path"]).resolve()
    assert bpy.app.version_string == expected["version"] and build_hash == expected["build_hash"]
    assert Path(os.environ["BLENDER_USER_RESOURCES"]).resolve() == (BASELINE / "profile").resolve()
    assert Path(bpy.utils.resource_path("USER")).resolve() == (BASELINE / "profile").resolve()
    assert MPFB_PACKAGE.is_file() and sha256(MPFB_PACKAGE) == EXPECTED_PACKAGE_SHA
    assert TARGET_ROOT.is_dir()
    source = ROOT / document["source_asset"]
    assert source.is_file() and sha256(source) == document["source_sha256"]
    return source


def parse_target(path: Path, vertex_count: int) -> dict[int, Vector]:
    """MPFB target order is X,Z,-Y; reject topology mistakes before loading."""
    deltas: dict[int, Vector] = {}
    with gzip.open(path, "rt", encoding="utf-8") as source:
        for line in source:
            raw = line.strip()
            if not raw or raw.startswith(("#", '"')):
                continue
            parts = raw.split()
            assert len(parts) == 4, (path, raw)
            index = int(parts[0])
            assert 0 <= index < vertex_count and index not in deltas, (path, index)
            deltas[index] = Vector((float(parts[1]), -float(parts[3]), float(parts[2])))
    assert deltas, path
    return deltas


def bounds(points: list[Vector]) -> dict:
    return {"min": [round(min(point[i] for point in points), 7) for i in range(3)],
            "max": [round(max(point[i] for point in points), 7) for i in range(3)]}


def scene_objects(document: dict):
    body = bpy.data.objects.get(document["human_object"])
    rig = bpy.data.objects.get(document["rig_object"])
    garment = bpy.data.objects.get("Garment_FightShorts")
    assert body and body.type == "MESH" and len(body.data.vertices) == document["expected_body_vertices"]
    assert rig and rig.type == "ARMATURE" and len(rig.data.bones) == 930
    assert garment and garment.type == "MESH"
    assert any(mod.type == "ARMATURE" and mod.object == rig for mod in garment.modifiers)
    assert any(mod.type == "ARMATURE" and mod.object == rig for mod in body.modifiers)
    return body, rig, garment


def target_metrics(body, key, deltas: dict[int, Vector], scale: float, head_floor_z: float) -> dict:
    basis = key.relative_key
    changed = []
    non_face_max = 0.0
    max_error = 0.0
    max_displacement = 0.0
    for index, (base, shaped) in enumerate(zip(basis.data, key.data)):
        actual = shaped.co - base.co
        expected = deltas.get(index, Vector()) * scale
        max_error = max(max_error, (actual - expected).length)
        distance = actual.length
        if distance > 1e-6:
            changed.append(base.co.copy())
            max_displacement = max(max_displacement, distance)
            if base.co.z < head_floor_z:
                non_face_max = max(non_face_max, distance)
    assert changed and max_error < 2e-6, (key.name, max_error)
    return {
        "target_entries": len(deltas),
        "max_target_index": max(deltas),
        "changed_vertices_gt_1e-6_m": len(changed),
        "changed_basis_bounds_local_m": bounds(changed),
        "max_full_weight_displacement_m": round(max_displacement, 7),
        "max_target_to_shape_key_error_m": round(max_error, 9),
        "non_face_max_displacement_below_head_floor_m": round(non_face_max, 9),
        "head_floor_z_local_m": round(head_floor_z, 7),
    }


def camera(name: str, target: Vector, direction: Vector, scale: float, resolution: tuple[int, int]):
    data = bpy.data.cameras.new(name)
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    data.type = "ORTHO"
    data.ortho_scale = scale
    obj.location = target + direction.normalized() * 3.0
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = obj
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    return obj


def render_views(body, rig, garment, rows: list[dict], render_dir: Path) -> dict:
    """Same camera/lighting for neutral and target-on clay comparisons."""
    authoring = import_authoring()

    render_dir.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.69, 0.72, 0.75)
    scene.display.shading.show_cavity = True
    scene.display.shading.show_shadows = True
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    original_hidden = {obj.name: obj.hide_render for obj in bpy.data.objects if obj.type == "MESH"}
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj is not body:
            obj.hide_render = True
    basis = authoring._face_basis(rig)
    shoulder_r = rig.matrix_world @ rig.data.bones["shoulder.R"].head_local
    shoulder_l = rig.matrix_world @ rig.data.bones["shoulder.L"].head_local
    side = (shoulder_l - shoulder_r).normalized()
    forward = basis["forward"].normalized()
    face_target = basis["origin"] + basis["up"] * 0.055 + forward * 0.020
    views = {
        "front": camera("Proof_FaceFront", face_target, forward, 0.43, (640, 640)),
        "profile": camera("Proof_FaceProfile", face_target, side, 0.43, (640, 640)),
    }
    outputs = {}
    for treatment in ("neutral", "morph"):
        for row in rows:
            body.data.shape_keys.key_blocks[row["shape_key"]].value = (0.0 if treatment == "neutral" else row["weight"])
        scene.frame_set(1)
        bpy.context.view_layer.update()
        for name, view in views.items():
            scene.camera = view
            scene.render.filepath = str(render_dir / f"face-{treatment}-{name}.png")
            bpy.ops.render.render(write_still=True)
            outputs[f"{treatment}_{name}"] = str(Path(scene.render.filepath).resolve())
    for obj in bpy.data.objects:
        if obj.type == "MESH" and obj.name in original_hidden:
            obj.hide_render = original_hidden[obj.name]
    body.hide_render = False
    garment.hide_render = False
    scene.frame_set(52)
    bpy.context.view_layer.update()
    camera("Proof_StressFront", Vector((0.0, 0.0, 0.84)), forward, 2.02, (512, 768))
    scene.render.filepath = str(render_dir / "face-morph-rig-stress-frame-52.png")
    bpy.ops.render.render(write_still=True)
    outputs["rig_stress_frame_52"] = str(Path(scene.render.filepath).resolve())
    scene.frame_set(1)
    bpy.context.view_layer.update()
    scene.camera = views["front"]
    return outputs


def build(document: dict, output: Path, render_dir: Path, report: Path) -> None:
    source = verify_runtime(document)
    assert Path(bpy.data.filepath).resolve() == source.resolve()
    body, rig, garment = scene_objects(document)
    authoring = import_authoring()

    authoring._enable_local_addons()
    TargetService = authoring._mpfb_symbol("mpfb.services.targetservice", "TargetService")
    GeneralObjectProperties = authoring._mpfb_symbol("mpfb.entities.objectproperties", "GeneralObjectProperties")
    scale = GeneralObjectProperties.get_value("scale_factor", entity_reference=body) or 1.0
    assert 0.0001 <= scale <= 100.0
    face_basis = authoring._face_basis(rig)
    head_floor_z = face_basis["origin"].z - 0.25
    metrics = []
    existing_keys = {key.name for key in body.data.shape_keys.key_blocks}
    for row in document["targets"]:
        assert row["shape_key"] not in existing_keys
        path = (TARGET_ROOT / row["relative_path"]).resolve()
        assert path.is_file() and path.is_relative_to(TARGET_ROOT.resolve())
        assert sha256(path) == row["sha256"]
        deltas = parse_target(path, len(body.data.vertices))
        key = TargetService.load_target(body, str(path), weight=row["weight"], name=row["shape_key"])
        assert key.name == row["shape_key"] and len(key.data) == len(body.data.vertices)
        item = {"path": row["relative_path"], "sha256": row["sha256"],
                "shape_key": key.name, "weight": row["weight"]}
        item.update(target_metrics(body, key, deltas, scale, head_floor_z))
        metrics.append(item)
    assert len(metrics) == 4
    assert all(item["non_face_max_displacement_below_head_floor_m"] < 1e-6 for item in metrics)
    outputs = render_views(body, rig, garment, document["targets"], render_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    previous = bpy.context.preferences.filepaths.save_version
    try:
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(output))
    finally:
        bpy.context.preferences.filepaths.save_version = previous
    result = {"schema": document["schema"], "status": document["status"], "source_asset": str(source),
              "source_sha256": document["source_sha256"], "blender_version": bpy.app.version_string,
              "mpfb_package_sha256": sha256(MPFB_PACKAGE), "target_scale_factor": scale,
              "stored_body_vertices": len(body.data.vertices), "rig_bones": len(rig.data.bones),
              "garment_vertices": len(garment.data.vertices), "targets": metrics,
              "renders": {name: {"path": path, "sha256": sha256(Path(path))} for name, path in outputs.items()},
              "saved_blend": str(output.resolve()), "saved_blend_sha256": sha256(output)}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def reopen(document: dict, report: Path) -> None:
    verify_runtime(document)
    body, rig, garment = scene_objects(document)
    keys = body.data.shape_keys.key_blocks
    actual = {row["shape_key"]: round(keys[row["shape_key"]].value, 6) for row in document["targets"]}
    expected = {row["shape_key"]: row["weight"] for row in document["targets"]}
    assert actual == expected
    assert all(len(keys[name].data) == len(body.data.vertices) for name in expected)
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    neutral = [vertex.co.copy() for vertex in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    scene.frame_set(52)
    bpy.context.view_layer.update()
    stress = [vertex.co.copy() for vertex in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    assert len(neutral) == len(stress)
    changed = sum((a - b).length > 1e-5 for a, b in zip(neutral, stress))
    assert changed > 1000
    result = {"status": "reopened", "blend": str(Path(bpy.data.filepath).resolve()),
              "blend_sha256": sha256(Path(bpy.data.filepath)), "body_vertices": len(body.data.vertices),
              "rig_bones": len(rig.data.bones), "garment_vertices": len(garment.data.vertices),
              "proof_shape_key_weights": actual, "stress_frame": 52,
              "evaluated_vertices_changed_gt_1e-5_m": changed}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("build", "reopen"), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--renders", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    supplied_paths = {"report": args.report, "output": args.output, "renders": args.renders}
    for label, path in supplied_paths.items():
        if path is not None and not path.is_absolute():
            parser.error(f"--{label} must be an absolute path; Blender may resolve relative render paths outside the worktree")
    document = config()
    if args.mode == "build":
        assert args.output is not None and args.renders is not None
        build(document, args.output, args.renders, args.report)
    else:
        reopen(document, args.report)


if __name__ == "__main__":
    main()
