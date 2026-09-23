"""Offline, review-only compiler for hash-bound ``model_scene.v1`` assets.

The parent process validates contracts and output paths. Blender appends only
the editable object trees from the pinned source files into a fresh scene, then
saves a derived ``.blend``.  No source scene is ever opened as the active file
or saved back to its original path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_FIXTURE = ROOT / "content/video_engine/tests/fixtures/modeling/blender/generalization-scene.model_scene.v1.json"
BLENDER_INPUTS = ROOT / "content/video_engine/tests/fixtures/modeling/baseline/benchmark-inputs.json"
BLENDER_VERSION = "5.2.2 LTS"
SUPPORTED_PASSES = frozenset({"beauty", "depth", "object_mask"})
REQUIRED_PASSES = SUPPORTED_PASSES
REVIEW_FRAMES = (1, 13, 25)
COMPILED_SCENE_NAME = "compiled-scene.blend"


class SceneCompileError(ValueError):
    """A source, scene contract, Blender worker, or output path was refused."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_bytes(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        payload = path.read_bytes()
        parsed = json.loads(payload)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SceneCompileError(f"{label} is unreadable JSON: {path}") from exc
    if not isinstance(parsed, dict):
        raise SceneCompileError(f"{label} must be a JSON object: {path}")
    return parsed, payload


def _contained_file(project_root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise SceneCompileError(f"{label} path must be a non-empty project-relative string")
    posix = PurePosixPath(relative)
    windows = PureWindowsPath(relative)
    if posix.is_absolute() or windows.is_absolute() or windows.drive or "\\" in relative:
        raise SceneCompileError(f"{label} path must be project-relative: {relative!r}")
    if any(part in {"", ".", ".."} for part in posix.parts):
        raise SceneCompileError(f"{label} path contains traversal: {relative!r}")
    root = project_root.resolve(strict=True)
    candidate = (root / Path(*posix.parts)).resolve(strict=True)
    if not candidate.is_relative_to(root) or not candidate.is_file():
        raise SceneCompileError(f"{label} is not a regular file under the project root: {relative!r}")
    return candidate


def _binding_sources(scene: Mapping[str, Any], project_root: Path) -> dict[str, dict[str, str]]:
    bindings = scene.get("bindings")
    if not isinstance(bindings, list):
        raise SceneCompileError("scene bindings must be an array")
    result: dict[str, dict[str, str]] = {}
    kinds: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise SceneCompileError("scene binding must be an object")
        binding_id = str(binding.get("binding_id", ""))
        descriptor_rel = str(binding.get("descriptor_path", ""))
        descriptor_path = _contained_file(project_root, descriptor_rel, f"{binding_id} descriptor")
        descriptor_hash = sha256_file(descriptor_path)
        if descriptor_hash != binding.get("descriptor_sha256"):
            raise SceneCompileError(f"stale descriptor hash for binding {binding_id!r}")
        descriptor, _ = _json_bytes(descriptor_path, f"{binding_id} descriptor")
        asset_id = binding.get("asset_id")
        revision_id = binding.get("revision_id")
        if descriptor.get("asset_id") != asset_id:
            raise SceneCompileError(f"descriptor asset_id differs for binding {binding_id!r}")
        revision = descriptor.get("revision")
        if not isinstance(revision, Mapping) or revision.get("revision_id") != revision_id:
            raise SceneCompileError(f"descriptor revision differs for binding {binding_id!r}")
        asset_kind = descriptor.get("asset_kind")
        if asset_kind not in {"prop", "environment"}:
            raise SceneCompileError(f"T6a accepts only prop and environment assets; got {asset_kind!r}")
        if asset_kind in kinds:
            raise SceneCompileError(f"T6a requires one asset of each kind; duplicate {asset_kind!r}")
        kinds.add(str(asset_kind))
        resources = descriptor.get("resources")
        if not isinstance(resources, list):
            raise SceneCompileError(f"descriptor resources are missing for binding {binding_id!r}")
        editable = [row for row in resources
                    if isinstance(row, Mapping) and row.get("resource_kind") == "editable_source"]
        if len(editable) != 1:
            raise SceneCompileError(f"binding {binding_id!r} needs exactly one editable source")
        resource = editable[0]
        source_path = _contained_file(project_root, str(resource.get("path", "")), f"{binding_id} editable source")
        source_hash = sha256_file(source_path)
        if source_hash != resource.get("sha256"):
            raise SceneCompileError(f"stale editable source hash for binding {binding_id!r}")
        if source_path.suffix.lower() != ".blend" or source_path.stat().st_size <= 50_000:
            raise SceneCompileError(f"binding {binding_id!r} editable source is not a substantial .blend file")
        if binding_id in result:
            raise SceneCompileError(f"duplicate binding_id {binding_id!r}")
        result[binding_id] = {
            "asset_id": str(asset_id),
            "asset_kind": str(asset_kind),
            "revision_id": str(revision_id),
            "descriptor_path": descriptor_rel,
            "descriptor_sha256": descriptor_hash,
            "source_path": str(source_path),
            "source_relative_path": str(resource["path"]),
            "source_sha256": source_hash,
        }
    if kinds != {"prop", "environment"}:
        raise SceneCompileError("T6a requires exactly one hash-pinned prop and one environment")
    return result


def _validate_scene_document(scene_path: Path, project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        from content.video_engine.src.modeling.contracts import validate_model_scene
        from content.video_engine.src.modeling.motion import MotionTimeline

        # Deliberately validation-only: this compiler never requests trusted
        # production render eligibility or operator approval.
        scene = validate_model_scene(scene_path, project_root=project_root, for_render=False)
        timeline = MotionTimeline.from_scene(scene)
    except Exception as exc:
        raise SceneCompileError(f"model_scene.v1 validation failed: {exc}") from exc

    profile = scene.get("render_profile")
    if not isinstance(profile, Mapping):
        raise SceneCompileError("scene must author a render_profile")
    requested = profile.get("passes")
    if not isinstance(requested, list):
        raise SceneCompileError("render_profile.passes must be an array")
    unsupported = sorted(set(requested) - SUPPORTED_PASSES)
    if unsupported:
        raise SceneCompileError(f"unsupported render passes: {', '.join(unsupported)}")
    missing = sorted(REQUIRED_PASSES - set(requested))
    if missing:
        raise SceneCompileError(f"required review passes were not requested: {', '.join(missing)}")
    if profile.get("engine_id") != "blender_cycles":
        raise SceneCompileError("T6a metric Depth and Object Index passes require blender_cycles")
    camera = scene.get("camera")
    lights = scene.get("lights")
    if not isinstance(camera, Mapping) or not isinstance(lights, list) or not lights:
        raise SceneCompileError("scene must author one camera and at least one light")
    if scene.get("duration_frames") != 26 or not set(REVIEW_FRAMES) <= set(range(scene.get("duration_frames", 0))):
        raise SceneCompileError("T6a review frames 1, 13 and 25 must lie in the authored scene range")
    channels = scene.get("motion_channels")
    if not isinstance(channels, list) or not channels:
        raise SceneCompileError("scene must author an articulation channel")
    for channel in channels:
        if (channel.get("target_kind") != "articulation" or channel.get("value_unit") != "degrees"
                or channel.get("interpolation") not in {"linear", "step"}):
            raise SceneCompileError("T6a supports authored degree articulation channels with linear or step interpolation")
        if channel.get("binding_id") not in {row.get("binding_id") for row in scene["bindings"]}:
            raise SceneCompileError("articulation channel refers to an unknown binding")
    return scene, _binding_sources(scene, project_root)


def _path_redirected(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    if callable(junction) and junction():
        return True
    try:
        attributes = os.lstat(path).st_file_attributes
        if attributes & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT (Windows links and junctions)
            return True
    except (AttributeError, FileNotFoundError, OSError):
        pass
    return False


def _checked_output_root(path: str | Path, *, must_be_new: bool) -> Path:
    output = Path(path).expanduser().absolute()
    for candidate in (output, *output.parents):
        if (candidate.exists() or candidate.is_symlink()) and _path_redirected(candidate):
            raise SceneCompileError(f"output path contains a symlink or junction: {candidate}")
    if must_be_new and output.exists():
        raise SceneCompileError(f"output root must be new and exclusive: {output}")
    if not must_be_new and (not output.exists() or not output.is_dir()):
        raise SceneCompileError(f"output root is not an existing directory: {output}")
    if not output.parent.exists() or not output.parent.is_dir():
        raise SceneCompileError(f"output parent must already exist: {output.parent}")
    return output


def _default_blender() -> Path:
    try:
        settings, _ = _json_bytes(BLENDER_INPUTS, "Blender benchmark inputs")
        executable = settings["tools"]["blender"]["path"]
    except (KeyError, TypeError) as exc:
        raise SceneCompileError("pinned Blender executable is not configured") from exc
    return Path(executable)


def _write_json_exclusive(path: Path, payload: Mapping[str, Any]) -> None:
    try:
        with path.open("x", encoding="utf-8", newline="\n") as target:
            json.dump(payload, target, indent=2, sort_keys=True)
            target.write("\n")
    except FileExistsError as exc:
        raise SceneCompileError(f"refusing to overwrite evidence: {path}") from exc


def _run_blender_worker(
    *, blender: Path, script: Path, output_root: Path, stage: str,
    arguments: Sequence[str], input_blend: Path | None = None, timeout: int = 900,
) -> dict[str, Any]:
    if not blender.is_file():
        raise SceneCompileError(f"pinned Blender executable missing: {blender}")
    output_root = _checked_output_root(output_root, must_be_new=False)
    logs = output_root / "logs"
    if logs.exists() or logs.is_symlink():
        _checked_output_root(logs, must_be_new=False)
    else:
        logs.mkdir(exist_ok=False)
    _checked_output_root(logs, must_be_new=False)
    stdout_path = logs / f"{stage}-stdout.txt"
    stderr_path = logs / f"{stage}-stderr.txt"
    report_path = output_root / f"{stage}-state.json"
    if any(path.exists() or path.is_symlink() for path in (stdout_path, stderr_path, report_path)):
        raise SceneCompileError(f"refusing to reuse Blender {stage} evidence in {output_root}")
    command = [str(blender), "--background", "--factory-startup", "--offline-mode",
               "--disable-autoexec", "--python-exit-code", "17", "--threads", "2"]
    if input_blend is not None:
        command.append(str(input_blend))
    command.extend(["--python", str(script), "--", *arguments, "--report", str(report_path)])
    env = {**os.environ, "PYTHONNOUSERSITE": "1",
           "BLENDER_USER_CONFIG": str(output_root / "_blender-user" / "config"),
           "BLENDER_USER_SCRIPTS": str(output_root / "_blender-user" / "scripts")}
    # Reserve both log files before launching Blender. Held handles keep a
    # failed stage's evidence intact even if the output directory is moved.
    with stdout_path.open("x", encoding="utf-8") as stdout_log, stderr_path.open("x", encoding="utf-8") as stderr_log:
        try:
            done = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                  timeout=timeout, check=False, env=env)
        except subprocess.TimeoutExpired as exc:
            stdout_log.write(str(exc.stdout or ""))
            stderr_log.write(str(exc.stderr or ""))
            raise SceneCompileError(f"Blender {stage} worker timed out; partial output is preserved in {output_root}") from exc
        stdout_log.write(done.stdout or "")
        stderr_log.write(done.stderr or "")
    if done.returncode != 0 or not report_path.is_file():
        raise SceneCompileError(f"Blender {stage} worker failed ({done.returncode}); logs are preserved in {logs}")
    report, _ = _json_bytes(report_path, f"Blender {stage} report")
    return report


def compile_scene(
    scene_document: str | Path = DEFAULT_FIXTURE,
    output_root: str | Path = "",
    *, project_root: str | Path = ROOT,
    blender: str | Path | None = None,
) -> dict[str, Any]:
    """Compile the review-only scene into a new editable ``.blend`` file."""

    project = Path(project_root).resolve(strict=True)
    fixture = Path(scene_document).resolve(strict=True)
    scene, sources = _validate_scene_document(fixture, project)
    output = _checked_output_root(output_root, must_be_new=True)
    output.mkdir(exist_ok=False)
    fixture_hash = sha256_file(fixture)
    # Keep the exact authored input beside the derived scene for independent review.
    (output / "source-scene.model_scene.v1.json").write_bytes(fixture.read_bytes())
    executable = Path(blender) if blender else _default_blender()
    args = ["--worker", "compile", "--project-root", str(project),
            "--scene-document", str(fixture), "--output-root", str(output),
            "--fixture-sha256", fixture_hash]
    report = _run_blender_worker(blender=executable, script=Path(__file__).resolve(),
                                 output_root=output, stage="compile", arguments=args)
    if report.get("blender_version") != BLENDER_VERSION:
        raise SceneCompileError(f"Blender {BLENDER_VERSION} required; worker reported {report.get('blender_version')!r}")
    if report.get("review_state") != "review_only" or report.get("render_eligible") is not False:
        raise SceneCompileError("compiled scene attempted to alter its review-only status")
    scene_file = output / COMPILED_SCENE_NAME
    if not scene_file.is_file():
        raise SceneCompileError("Blender did not save the compiled .blend")
    report["compiled_scene_path"] = str(scene_file)
    report["compiled_scene_sha256"] = sha256_file(scene_file)
    report["fixture_path"] = str(fixture)
    report["fixture_sha256"] = fixture_hash
    report["descriptor_hashes"] = {binding_id: row["descriptor_sha256"] for binding_id, row in sources.items()}
    report["source_hashes"] = {binding_id: row["source_sha256"] for binding_id, row in sources.items()}
    report["source_paths"] = {binding_id: row["source_relative_path"] for binding_id, row in sources.items()}
    for binding_id, row in sources.items():
        if sha256_file(Path(row["source_path"])) != row["source_sha256"]:
            raise SceneCompileError(f"source bytes changed during Blender compilation: {binding_id}")
    report["review_state"] = "review_only"
    report["render_eligible"] = False
    return report


def compile_and_render(
    scene_document: str | Path = DEFAULT_FIXTURE,
    output_root: str | Path = "",
    *, project_root: str | Path = ROOT,
    blender: str | Path | None = None,
) -> dict[str, Any]:
    """Compile, reopen, render requested review passes, and write one receipt."""

    compiled = compile_scene(scene_document, output_root, project_root=project_root, blender=blender)
    from content.video_engine.src.modeling.blender.render import render_scene

    rendered = render_scene(scene_document, output_root, project_root=project_root, blender=blender)
    output = Path(output_root).absolute()
    receipt = {
        "schema_version": "model_scene_blender_review_receipt.v1",
        "scene_id": compiled["scene_id"],
        "review_state": "review_only",
        "render_eligible": False,
        "for_render_requested": False,
        "blender_version": compiled["blender_version"],
        "blender_build_hash": compiled["blender_build_hash"],
        "fixture_path": compiled["fixture_path"],
        "fixture_sha256": compiled["fixture_sha256"],
        "descriptor_hashes": compiled["descriptor_hashes"],
        "source_paths": compiled["source_paths"],
        "source_hashes": compiled["source_hashes"],
        "source_hashes_unchanged": rendered["source_hashes_unchanged"],
        "compiled_scene_path": compiled["compiled_scene_path"],
        "compiled_scene_sha256": compiled["compiled_scene_sha256"],
        "reopened_scene_sha256": rendered["reopened_scene_sha256"],
        "render_profile": compiled["render_profile"],
        "binding_pass_indices": compiled["binding_pass_indices"],
        "reopened_state": rendered["reopened_state"],
        "frames": rendered["frames"],
        "seek_parity": rendered["seek_parity"],
        "scope": "T4c prop/environment compilation only; diagnostic blockouts; no fighter art, T5b, T6, HG2 or HG3 claim",
    }
    if receipt["reopened_scene_sha256"] != receipt["compiled_scene_sha256"]:
        raise SceneCompileError("reopened scene hash differs from the compiled scene")
    _write_json_exclusive(output / "receipt.json", receipt)
    return receipt


def _read_scene_and_source_records(project_root: Path, scene_document: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    scene, _ = _json_bytes(scene_document, "model scene")
    sources = _binding_sources(scene, project_root)
    return scene, sources


def _blender_compile_worker(project_root: Path, scene_document: Path, output_root: Path,
                            expected_fixture_hash: str, report_path: Path) -> None:
    import bpy  # type: ignore[import-not-found]
    from mathutils import Vector  # type: ignore[import-not-found]

    if bpy.app.version_string != BLENDER_VERSION:
        raise SceneCompileError(f"Blender {BLENDER_VERSION} required; got {bpy.app.version_string}")
    if sha256_file(scene_document) != expected_fixture_hash:
        raise SceneCompileError("fixture changed after parent validation")
    scene, sources = _read_scene_and_source_records(project_root, scene_document)
    if scene.get("schema_version") != "model_scene.v1":
        raise SceneCompileError("unsupported scene schema")

    active_scene = bpy.context.scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(active_scene.collection.children):
        active_scene.collection.children.unlink(collection)
        if collection.users == 0:
            bpy.data.collections.remove(collection)
    for datablocks in (bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

    active_scene.name = f"{scene['scene_id']}__review_only"
    active_scene.frame_start = 1
    active_scene.frame_end = 25
    active_scene.render.fps = int(scene["fps"]["numerator"])
    active_scene.render.fps_base = float(scene["fps"]["denominator"])
    active_scene.unit_settings.system = "METRIC"
    active_scene.unit_settings.scale_length = 1.0
    active_scene["model_scene_id"] = scene["scene_id"]
    active_scene["t6a_review_state"] = "review_only"
    active_scene["t6a_render_eligible"] = False
    active_scene["t6a_fixture_sha256"] = expected_fixture_hash

    binding_rows = {row["binding_id"]: row for row in scene["bindings"]}
    binding_codes = {binding_id: index for index, binding_id in enumerate(sorted(binding_rows), start=1)}
    binding_objects: dict[str, list[Any]] = {}
    for binding_id, binding in binding_rows.items():
        source = Path(sources[binding_id]["source_path"])
        expected_source_hash = sources[binding_id]["source_sha256"]
        if sha256_file(source) != expected_source_hash:
            raise SceneCompileError(f"source bytes changed before append: {binding_id}")
        with bpy.data.libraries.load(str(source), link=False) as (from_file, to_file):
            object_names = list(from_file.objects)
            if not object_names:
                raise SceneCompileError(f"editable source has no objects: {binding_id}")
            to_file.objects = object_names
        imported = [obj for obj in to_file.objects if obj is not None]
        if not imported:
            raise SceneCompileError(f"Blender appended no objects: {binding_id}")
        collection = bpy.data.collections.new(f"binding__{binding_id}")
        active_scene.collection.children.link(collection)
        visible_objects = []
        names = [obj.name for obj in imported]
        if len(names) != len(set(names)):
            raise SceneCompileError(f"duplicate object names in source tree: {binding_id}")
        for obj in imported:
            if obj.type in {"CAMERA", "LIGHT"}:
                bpy.data.objects.remove(obj, do_unlink=True)
                continue
            source_name = obj.name
            final_name = f"{binding_id}__{source_name}"
            if bpy.data.objects.get(final_name) is not None:
                raise SceneCompileError(f"namespaced object collision: {final_name}")
            obj.name = final_name
            obj["model_binding_id"] = binding_id
            obj["source_object_name"] = source_name
            obj["t6a_review_only"] = True
            obj.pass_index = binding_codes[binding_id]
            for old_collection in list(obj.users_collection):
                if old_collection != collection:
                    old_collection.objects.unlink(obj)
            if collection not in obj.users_collection:
                collection.objects.link(obj)
            visible_objects.append(obj)
        binding_objects[binding_id] = visible_objects
        if sha256_file(source) != expected_source_hash:
            raise SceneCompileError(f"source bytes changed while appending: {binding_id}")
    for datablocks in (bpy.data.cameras, bpy.data.lights):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

    geometry_rows = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for binding_id, objects in binding_objects.items():
        for obj in objects:
            if obj.type != "MESH":
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                geometry_rows.append({
                    "binding_id": binding_id,
                    "object_type": obj.type,
                    "object_name": obj.name,
                    "source_object_name": obj.get("source_object_name"),
                    "vertices": len(obj.data.vertices),
                    "polygons": len(obj.data.polygons),
                    "evaluated_vertices": len(mesh.vertices),
                    "evaluated_polygons": len(mesh.polygons),
                    "hide_render": bool(obj.hide_render),
                    "hide_viewport": bool(obj.hide_viewport),
                    "visible": bool(obj.visible_get()),
                })
            finally:
                evaluated.to_mesh_clear()
    validate_geometry_rows(geometry_rows, set(binding_objects))

    hinge_channels = [row for row in scene["motion_channels"]
                      if row["target_kind"] == "articulation"]
    if len(hinge_channels) != 1:
        raise SceneCompileError("T6a fixture requires exactly one authored articulation channel")
    channel = hinge_channels[0]
    hinge = resolve_control(binding_objects[channel["binding_id"]], channel["semantic_target"], "articulation_id")
    if hinge.type != "EMPTY":
        raise SceneCompileError("authored hinge semantic control must be an Empty pivot")
    hinge.animation_data_clear()
    for keyframe in channel["keyframes"]:
        hinge.rotation_mode = "XYZ"
        hinge.rotation_euler.x = math.radians(float(keyframe["value"]))
        hinge.keyframe_insert(data_path="rotation_euler", index=0, frame=int(keyframe["frame"]), group="T6a authored hinge")
    action = hinge.animation_data.action if hinge.animation_data else None
    if action is None:
        raise SceneCompileError("authored hinge animation was not created")
    slot = hinge.animation_data.action_slot
    if slot is None or len(action.layers) != 1 or len(action.layers[0].strips) != 1:
        raise SceneCompileError("authored hinge action has no unique Blender 5.2 keyframe strip")
    channelbag = action.layers[0].strips[0].channelbag(slot)
    if channelbag is None:
        raise SceneCompileError("authored hinge action has no channelbag for its control")
    for curve in channelbag.fcurves:
        if curve.data_path == "rotation_euler" and curve.array_index == 0:
            for point in curve.keyframe_points:
                point.interpolation = "LINEAR" if channel["interpolation"] == "linear" else "CONSTANT"
    if not any(curve.data_path == "rotation_euler" and curve.array_index == 0 for curve in channelbag.fcurves):
        raise SceneCompileError("authored hinge channel did not bind to a rotation curve")

    prop_binding = next(key for key, row in sources.items() if row["asset_kind"] == "prop")
    env_binding = next(key for key, row in sources.items() if row["asset_kind"] == "environment")
    socket = resolve_control(binding_objects[prop_binding], "grip_socket", "socket_id")
    floor = resolve_control(binding_objects[env_binding], "floor", "surface_id")
    if socket.parent is None or socket.parent.get("model_binding_id") != prop_binding:
        raise SceneCompileError("prop grip socket lost its in-tree parent")
    if not any(modifier.type == "COLLISION" for modifier in floor.modifiers):
        raise SceneCompileError("environment floor collision modifier was not preserved")
    floor_top = max((floor.matrix_world @ Vector(corner)).z for corner in floor.bound_box)
    if abs(float(floor_top)) > 0.001:
        raise SceneCompileError(f"environment floor top moved from z=0 m: {floor_top}")

    camera_data = scene["camera"]
    camera_data_block = bpy.data.cameras.new("compiler_camera_data")
    camera_obj = bpy.data.objects.new("compiler_camera", camera_data_block)
    active_scene.collection.objects.link(camera_obj)
    camera_obj.location = camera_data["position_m"]
    camera_obj.rotation_euler = (Vector(camera_data["target_m"]) - camera_obj.location).to_track_quat("-Z", "Y").to_euler()
    near, far = camera_data["clip_planes_m"]
    camera_data_block.clip_start = float(near)
    camera_data_block.clip_end = float(far)
    if camera_data["projection"] == "orthographic":
        camera_data_block.type = "ORTHO"
        camera_data_block.ortho_scale = float(camera_data["orthographic_scale_m"])
    elif camera_data["projection"] == "perspective":
        camera_data_block.type = "PERSP"
        camera_data_block.lens = float(camera_data["focal_length_mm"])
    else:
        raise SceneCompileError("unsupported authored camera projection")
    camera_obj["authored_by_model_scene"] = True
    active_scene.camera = camera_obj

    created_lights = []
    for light_spec in scene["lights"]:
        light_type = str(light_spec["light_type"]).upper()
        if light_type not in {"POINT", "SPOT", "AREA", "SUN"}:
            raise SceneCompileError(f"unsupported authored light type: {light_type}")
        light_data = bpy.data.lights.new(f"compiler_light_data__{light_spec['light_id']}", light_type)
        light_obj = bpy.data.objects.new(f"compiler_light__{light_spec['light_id']}", light_data)
        active_scene.collection.objects.link(light_obj)
        light_data.energy = float(light_spec["energy_w"])
        light_data.color = light_spec["color_rgb"]
        if light_type != "SUN" and "position_m" in light_spec:
            light_obj.location = light_spec["position_m"]
        if light_type in {"AREA", "SPOT", "SUN"} and "direction_xyz" in light_spec:
            direction = Vector(light_spec["direction_xyz"])
            if direction.length == 0:
                raise SceneCompileError(f"light direction must be non-zero: {light_spec['light_id']}")
            light_obj.rotation_euler = direction.normalized().to_track_quat("-Z", "Y").to_euler()
        if light_type == "AREA":
            light_data.shape = "DISK"
            light_data.size = float(light_spec.get("size_m", 1.0))
        if light_type == "SPOT":
            light_data.spot_size = math.radians(45.0)
        light_obj["authored_by_model_scene"] = True
        created_lights.append(light_obj)

    profile = scene["render_profile"]
    active_scene.render.engine = "CYCLES"
    active_scene.cycles.samples = int(profile["samples"])
    active_scene.cycles.seed = 0
    active_scene.cycles.use_animated_seed = False
    active_scene.cycles.use_denoising = False
    active_scene.render.resolution_x = int(profile["resolution_px"][0])
    active_scene.render.resolution_y = int(profile["resolution_px"][1])
    active_scene.render.resolution_percentage = 100
    active_scene.render.image_settings.file_format = "PNG"
    active_scene.render.image_settings.color_mode = "RGBA"
    active_scene.render.image_settings.color_depth = "8"
    active_scene.render.film_transparent = True
    active_scene.view_settings.view_transform = str(profile.get("color_space", "AgX"))
    active_scene.view_layers[0].use_pass_z = True
    active_scene.view_layers[0].use_pass_object_index = True
    active_scene.view_layers[0].update_render_passes()
    active_scene.render.use_compositing = True

    hinge_angles = {}
    for frame in REVIEW_FRAMES:
        active_scene.frame_set(frame)
        hinge_angles[str(frame)] = round(math.degrees(float(hinge.rotation_euler.x)), 6)
    active_scene.frame_set(1)
    active_scene["t6a_hinge_binding_id"] = channel["binding_id"]
    active_scene["t6a_hinge_semantic_target"] = channel["semantic_target"]
    active_scene["t6a_binding_codes_json"] = json.dumps(binding_codes, sort_keys=True)

    scene_path = output_root / COMPILED_SCENE_NAME
    if scene_path.exists():
        raise SceneCompileError(f"refusing to overwrite derived scene: {scene_path}")
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_path), check_existing=False)
    source_hashes = {binding_id: row["source_sha256"] for binding_id, row in sources.items()}
    after_hashes = {binding_id: sha256_file(Path(row["source_path"])) for binding_id, row in sources.items()}
    if source_hashes != after_hashes:
        raise SceneCompileError("one or more source hashes changed during scene compilation")
    materials = {}
    for binding_id, objects in binding_objects.items():
        materials[binding_id] = sorted({slot.material.name for obj in objects if obj.type == "MESH"
                                        for slot in obj.material_slots if slot.material})
    report = {
        "schema_version": "model_scene_blender_compile_state.v1",
        "scene_id": scene["scene_id"],
        "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode("ascii"),
        "review_state": "review_only",
        "render_eligible": False,
        "fixture_sha256": expected_fixture_hash,
        "source_hashes": source_hashes,
        "descriptor_hashes": {binding_id: row["descriptor_sha256"] for binding_id, row in sources.items()},
        "source_paths": {binding_id: row["source_relative_path"] for binding_id, row in sources.items()},
        "binding_collections": {binding_id: f"binding__{binding_id}" for binding_id in sorted(binding_rows)},
        "binding_pass_indices": binding_codes,
        "object_names": sorted(obj.name for obj in active_scene.objects),
        "namespaced_object_trees": {
            binding_id: sorted(obj.name for obj in objects) for binding_id, objects in binding_objects.items()
        },
        "source_camera_light_objects_removed": True,
        "camera": {
            "name": camera_obj.name,
            "projection": camera_data_block.type,
            "position_m": [round(float(value), 8) for value in camera_obj.matrix_world.translation],
            "clip_planes_m": [float(camera_data_block.clip_start), float(camera_data_block.clip_end)],
            "orthographic_scale_m": float(camera_data_block.ortho_scale) if camera_data_block.type == "ORTHO" else None,
            "focal_length_mm": float(camera_data_block.lens) if camera_data_block.type == "PERSP" else None,
        },
        "lights": [{"name": obj.name, "type": obj.data.type, "energy_w": float(obj.data.energy),
                    "color_rgb": [float(value) for value in obj.data.color],
                    "position_m": [round(float(value), 8) for value in obj.matrix_world.translation]}
                   for obj in created_lights],
        "render_profile": {
            "engine_id": profile["engine_id"],
            "engine": active_scene.render.engine,
            "resolution_px": [active_scene.render.resolution_x, active_scene.render.resolution_y],
            "samples": active_scene.cycles.samples,
            "passes": list(profile["passes"]),
            "camera_depth_units": "m",
        },
        "hinge": {
            "binding_id": channel["binding_id"],
            "semantic_target": channel["semantic_target"],
            "control_object": hinge.name,
            "action_present": bool(hinge.animation_data and hinge.animation_data.action),
            "angles_deg": hinge_angles,
        },
        "socket": {"object": socket.name, "socket_id": socket.get("socket_id"),
                   "parent": socket.parent.name if socket.parent else None},
        "environment_floor": {"object": floor.name, "surface_id": floor.get("surface_id"),
                              "collision_role": floor.get("collision_role"),
                              "collision_modifier": True, "top_z_m": round(float(floor_top), 8)},
        "source_materials": materials,
        "geometry": geometry_rows,
        "frame_range": [active_scene.frame_start, active_scene.frame_end],
        "fps": {"numerator": active_scene.render.fps, "denominator": int(active_scene.render.fps_base)},
        "compiled_scene_path": str(scene_path),
        "compiled_scene_sha256": sha256_file(scene_path),
    }
    _write_json_exclusive(report_path, report)


def _custom_value(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    getter = getattr(value, "get", None)
    return getter(name, default) if callable(getter) else default


def resolve_control(objects: Sequence[Any], semantic_value: str, property_name: str) -> Any:
    matches = [obj for obj in objects if _custom_value(obj, property_name) == semantic_value]
    if len(matches) != 1:
        raise SceneCompileError(
            f"semantic control {property_name}={semantic_value!r} must resolve exactly once; found {len(matches)}"
        )
    return matches[0]


def validate_geometry_rows(rows: Sequence[Mapping[str, Any]], binding_ids: set[str]) -> None:
    """Fail closed on any empty/hidden mesh in either imported object tree."""
    for binding_id in sorted(binding_ids):
        meshes = [row for row in rows if row.get("binding_id") == binding_id and row.get("object_type") == "MESH"]
        if not meshes:
            raise SceneCompileError(f"binding {binding_id!r} has no mesh geometry")
        for row in meshes:
            if row.get("hide_render") or row.get("hide_viewport") or row.get("visible") is False:
                raise SceneCompileError(f"binding {binding_id!r} contains hidden mesh geometry: {row.get('object_name')}")
            counts = (row.get("vertices", 0), row.get("polygons", 0),
                      row.get("evaluated_vertices", row.get("vertices", 0)),
                      row.get("evaluated_polygons", row.get("polygons", 0)))
            if any(not isinstance(value, int) or value <= 0 for value in counts):
                raise SceneCompileError(f"binding {binding_id!r} contains empty mesh geometry: {row.get('object_name')}")


def _worker_arguments() -> list[str]:
    try:
        return sys.argv[sys.argv.index("--") + 1:]
    except ValueError:
        return []


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=["compile"])
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--scene-document", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--fixture-sha256")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(_worker_arguments())
    if args.worker == "compile":
        if not all((args.project_root, args.scene_document, args.output_root, args.fixture_sha256, args.report)):
            raise SceneCompileError("compile worker arguments are incomplete")
        _blender_compile_worker(args.project_root, args.scene_document, args.output_root,
                                args.fixture_sha256, args.report)


if __name__ == "__main__":
    _main()
