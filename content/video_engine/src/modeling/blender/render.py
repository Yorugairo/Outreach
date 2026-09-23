"""Reopen and render the T6a Blender scene with beauty, metric depth and IDs."""

from __future__ import annotations

from array import array
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


try:
    from . import scene as compiler
except ImportError:  # Blender executes this file directly with --python.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import scene as compiler  # type: ignore[no-redef]


ROOT = compiler.ROOT
DEFAULT_FIXTURE = compiler.DEFAULT_FIXTURE
BLENDER_VERSION = compiler.BLENDER_VERSION


class BlenderRenderError(ValueError):
    """The saved scene or one of its declared review passes could not render."""


def _json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BlenderRenderError(f"{label} is unreadable JSON: {path}") from exc
    if not isinstance(data, dict):
        raise BlenderRenderError(f"{label} must be a JSON object: {path}")
    return data


def _artifact(directory: Path, suffix: str) -> Path:
    matches = [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() == suffix.lower()]
    if len(matches) != 1 or matches[0].stat().st_size <= 32:
        raise BlenderRenderError(f"expected one non-empty {suffix} artifact in {directory}; found {len(matches)}")
    return matches[0]


def _pixel_buffer(bpy: Any, path: Path) -> tuple[Any, int, int, int, str]:
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        width, height = int(image.size[0]), int(image.size[1])
        if width <= 0 or height <= 0:
            raise BlenderRenderError(f"render pass has invalid image dimensions: {path}")
        pixel_count = width * height
        raw = array("f", [0.0]) * len(image.pixels)
        image.pixels.foreach_get(raw)
        if len(raw) % pixel_count:
            raise BlenderRenderError(f"render pass pixel buffer has an invalid channel count: {path}")
        channels = len(raw) // pixel_count
        if channels < 1 or channels > 4:
            raise BlenderRenderError(f"render pass pixel buffer has an unsupported channel count: {channels}")
        return raw, width, height, channels, hashlib.sha256(raw.tobytes()).hexdigest()
    finally:
        bpy.data.images.remove(image)


def _validate_render_pixels(bpy: Any, outputs: Mapping[str, Any], binding_ids: Sequence[str],
                            clip_end_m: float) -> dict[str, Any]:
    depth_path = Path(outputs["depth"])
    depth, width, height, depth_channels, depth_pixel_hash = _pixel_buffer(bpy, depth_path)
    binding_masks: dict[str, tuple[Any, int, int, int, str]] = {}
    for binding_id in binding_ids:
        binding_masks[binding_id] = _pixel_buffer(bpy, Path(outputs["masks"][binding_id]))
    if any((item[1], item[2]) != (width, height) for item in binding_masks.values()):
        raise BlenderRenderError("metric depth and binding masks do not share one pixel grid")

    pixel_count = width * height
    valid_depth: list[bool] = []
    depth_values: list[float] = []
    for index in range(pixel_count):
        value = float(depth[index * depth_channels])
        hit = math.isfinite(value) and 0.000001 < value < clip_end_m
        valid_depth.append(hit)
        if hit:
            depth_values.append(value)
    if not depth_values:
        raise BlenderRenderError("metric camera-depth pass contains no finite visible geometry")

    mask_bits: dict[str, list[bool]] = {}
    mask_pixel_counts: dict[str, int] = {}
    mask_hashes: dict[str, str] = {}
    for binding_id, (pixels, _width, _height, channels, pixel_hash) in binding_masks.items():
        bits = [float(pixels[index * channels]) > 0.5 for index in range(pixel_count)]
        count = sum(bits)
        if count == 0:
            raise BlenderRenderError(f"binding-ID mask is empty: {binding_id}")
        mask_bits[binding_id] = bits
        mask_pixel_counts[binding_id] = count
        mask_hashes[binding_id] = pixel_hash
    union = [any(mask_bits[binding_id][index] for binding_id in binding_ids)
             for index in range(pixel_count)]
    mismatch = sum(1 for index in range(pixel_count) if union[index] != valid_depth[index])
    if mismatch:
        raise BlenderRenderError(f"camera-depth and binding-ID geometry disagree at {mismatch} pixels")

    beauty, beauty_width, beauty_height, beauty_channels, beauty_pixel_hash = _pixel_buffer(bpy, Path(outputs["beauty"]))
    if (beauty_width, beauty_height) != (width, height) or beauty_channels < 4:
        raise BlenderRenderError("beauty output is missing the alpha channel or differs from data-pass dimensions")
    opaque_alpha = sum(1 for index in range(pixel_count) if float(beauty[index * beauty_channels + 3]) > 0.01)
    alpha_mask_mismatch = sum(1 for index in range(pixel_count)
                              if (float(beauty[index * beauty_channels + 3]) > 0.01) != union[index])
    return {
        "resolution_px": [width, height],
        "depth_unit": "m",
        "depth_metric": "Blender Cycles Depth pass distance to nearest visible surface",
        "depth_format": "OpenEXR 32-bit float",
        "depth_pixel_sha256": depth_pixel_hash,
        "depth_valid_pixels": len(depth_values),
        "depth_min_m": round(min(depth_values), 8),
        "depth_max_m": round(max(depth_values), 8),
        "depth_channels": depth_channels,
        "mask_method": "Cycles Object Index pass isolated by Blender ID Mask compositor nodes",
        "mask_pixel_sha256": mask_hashes,
        "mask_pixel_counts": mask_pixel_counts,
        "depth_mask_mismatch_pixels": mismatch,
        "alpha_pixel_sha256": beauty_pixel_hash,
        "alpha_nonzero_pixels": opaque_alpha,
        "alpha_mask_edge_mismatch_pixels": alpha_mask_mismatch,
    }


def _configure_compositor(bpy: Any, scene: Any, output_root: Path,
                          binding_pass_indices: Mapping[str, int]) -> dict[str, Any]:
    view_layer = scene.view_layers[0]
    view_layer.use_pass_z = True
    view_layer.use_pass_object_index = True
    view_layer.update_render_passes()
    group = bpy.data.node_groups.new("T6aReviewPassGraph", "CompositorNodeTree")
    scene.compositing_node_group = group
    nodes = group.nodes
    nodes.clear()
    render_layers = nodes.new("CompositorNodeRLayers")
    render_layers.scene = scene
    render_layers.layer = view_layer.name
    required_outputs = {"Image", "Depth", "Object Index"}
    missing = required_outputs - {socket.name for socket in render_layers.outputs}
    if missing:
        raise BlenderRenderError(f"Blender did not expose required render pass sockets: {sorted(missing)}")

    group.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    composite = nodes.new("NodeGroupOutput")
    group.links.new(render_layers.outputs["Image"], composite.inputs["Image"])

    depth_node = nodes.new("CompositorNodeOutputFile")
    depth_node.name = "T6a_Metric_Camera_Depth"
    depth_node.format.media_type = "IMAGE"
    depth_node.format.file_format = "OPEN_EXR"
    depth_node.format.color_mode = "BW"
    depth_node.format.color_depth = "32"
    depth_node.format.exr_codec = "ZIP"
    depth_node.file_name = "depth_"
    depth_node.file_output_items.new("FLOAT", "Depth")
    group.links.new(render_layers.outputs["Depth"], depth_node.inputs["Depth"])

    masks: dict[str, Any] = {}
    for binding_id, pass_index in binding_pass_indices.items():
        id_mask = nodes.new("CompositorNodeIDMask")
        id_mask.name = f"T6a_Binding_Mask_{binding_id}"
        id_mask.inputs["Index"].default_value = int(pass_index)
        id_mask.inputs["Anti-Alias"].default_value = False
        group.links.new(render_layers.outputs["Object Index"], id_mask.inputs["ID value"])
        output = nodes.new("CompositorNodeOutputFile")
        output.name = f"T6a_Binding_Mask_Output_{binding_id}"
        output.format.media_type = "IMAGE"
        output.format.file_format = "PNG"
        output.format.color_mode = "BW"
        output.format.color_depth = "8"
        output.file_name = "mask_"
        output.file_output_items.new("FLOAT", "Mask")
        group.links.new(id_mask.outputs["Alpha"], output.inputs["Mask"])
        masks[binding_id] = output

    scene.render.use_compositing = True
    return {"depth": depth_node, "masks": masks}


def _unique_frame_outputs(bpy: Any, scene: Any, output_root: Path, frame: int,
                          phase: str, file_nodes: Mapping[str, Any], binding_ids: Sequence[str],
                          clip_end_m: float) -> dict[str, Any]:
    root = output_root / phase
    beauty_dir = root / "beauty" / f"frame_{frame:03d}"
    depth_dir = root / "depth" / f"frame_{frame:03d}"
    mask_dirs = {binding_id: root / "binding_masks" / binding_id / f"frame_{frame:03d}"
                 for binding_id in binding_ids}
    all_dirs = [beauty_dir, depth_dir, *mask_dirs.values()]
    for directory in all_dirs:
        if directory.exists():
            raise BlenderRenderError(f"refusing to overwrite render evidence: {directory}")
        directory.mkdir(parents=True, exist_ok=False)

    file_nodes["depth"].directory = str(depth_dir)
    for binding_id, node in file_nodes["masks"].items():
        node.directory = str(mask_dirs[binding_id])
    scene.render.filepath = str(beauty_dir / "beauty_")
    scene.frame_set(int(frame))
    bpy.ops.render.render(write_still=True)

    beauty = _artifact(beauty_dir, ".png")
    depth = _artifact(depth_dir, ".exr")
    masks = {binding_id: _artifact(directory, ".png") for binding_id, directory in mask_dirs.items()}
    outputs = {"beauty": str(beauty), "depth": str(depth),
               "masks": {binding_id: str(path) for binding_id, path in masks.items()}}
    metrics = _validate_render_pixels(bpy, outputs, binding_ids, clip_end_m)
    output_hashes = {
        "beauty": compiler.sha256_file(beauty),
        "depth": compiler.sha256_file(depth),
        "masks": {binding_id: compiler.sha256_file(path) for binding_id, path in masks.items()},
    }
    return {"frame": int(frame), "outputs": outputs, "output_sha256": output_hashes, "metrics": metrics}


def render_scene(
    scene_document: str | Path = DEFAULT_FIXTURE,
    output_root: str | Path = "",
    *, project_root: str | Path = ROOT,
    blender: str | Path | None = None,
    frames: Sequence[int] = compiler.REVIEW_FRAMES,
    verify_seek_parity: bool = True,
) -> dict[str, Any]:
    """Reopen a compiled scene and render the authored passes at selected frames."""

    project = Path(project_root).resolve(strict=True)
    fixture = Path(scene_document).resolve(strict=True)
    scene, sources = compiler._validate_scene_document(fixture, project)
    selected = tuple(int(frame) for frame in frames)
    if not selected or len(selected) != len(set(selected)) or not set(selected) <= set(compiler.REVIEW_FRAMES):
        raise BlenderRenderError("T6a render frames must be a unique subset of 1, 13 and 25")
    if verify_seek_parity and set(selected) != set(compiler.REVIEW_FRAMES):
        raise BlenderRenderError("seek parity requires all T6a frames 1, 13 and 25")
    output = compiler._checked_output_root(output_root, must_be_new=False)
    compile_report = _json(output / "compile-state.json", "compiled scene state")
    scene_file = output / compiler.COMPILED_SCENE_NAME
    if not scene_file.is_file() or compiler.sha256_file(scene_file) != compile_report.get("compiled_scene_sha256"):
        raise BlenderRenderError("compiled .blend is missing or differs from its hash-bound compile report")
    fixture_hash = compiler.sha256_file(fixture)
    if fixture_hash != compile_report.get("fixture_sha256"):
        raise BlenderRenderError("scene fixture changed after compilation")
    for binding_id, row in sources.items():
        if compile_report.get("source_hashes", {}).get(binding_id) != row["source_sha256"]:
            raise BlenderRenderError(f"compiled report source hash differs for {binding_id}")
        if compiler.sha256_file(Path(row["source_path"])) != row["source_sha256"]:
            raise BlenderRenderError(f"source hash became stale before rendering: {binding_id}")
    for relative in ("first", "seek-parity"):
        if (output / relative).exists():
            raise BlenderRenderError(f"refusing to overwrite prior render evidence: {output / relative}")

    indices = compile_report.get("binding_pass_indices")
    if not isinstance(indices, Mapping) or set(indices) != set(sources):
        raise BlenderRenderError("compiled report has no complete binding-ID pass map")
    executable = Path(blender) if blender else compiler._default_blender()
    args = ["--worker", "render", "--project-root", str(project), "--scene-document", str(fixture),
            "--output-root", str(output), "--fixture-sha256", fixture_hash,
            "--compiled-scene-sha256", str(compile_report["compiled_scene_sha256"]),
            "--frames", ",".join(str(frame) for frame in selected),
            "--seek-parity", "true" if verify_seek_parity else "false"]
    report = compiler._run_blender_worker(
        blender=executable, script=Path(__file__).resolve(), output_root=output,
        stage="render", arguments=args, input_blend=scene_file,
    )
    if report.get("blender_version") != BLENDER_VERSION:
        raise BlenderRenderError(f"Blender {BLENDER_VERSION} required; worker reported {report.get('blender_version')!r}")
    unchanged = {}
    for binding_id, row in sources.items():
        current_hash = compiler.sha256_file(Path(row["source_path"]))
        unchanged[binding_id] = current_hash == row["source_sha256"]
    if not all(unchanged.values()):
        raise BlenderRenderError("one or more source hashes changed during rendering")
    report["reopened_scene_sha256"] = compiler.sha256_file(scene_file)
    report["source_hashes_unchanged"] = unchanged
    report["fixture_sha256"] = fixture_hash
    report["render_state_path"] = str(output / "render-state.json")
    return report


def _blender_render_worker(project_root: Path, scene_document: Path, output_root: Path,
                           expected_fixture_hash: str, expected_scene_hash: str,
                           frames: Sequence[int], verify_seek_parity: bool, report_path: Path) -> None:
    import bpy  # type: ignore[import-not-found]
    from mathutils import Vector  # type: ignore[import-not-found]

    if bpy.app.version_string != BLENDER_VERSION:
        raise BlenderRenderError(f"Blender {BLENDER_VERSION} required; got {bpy.app.version_string}")
    compiled_path = Path(bpy.data.filepath).resolve(strict=True)
    if compiler.sha256_file(compiled_path) != expected_scene_hash:
        raise BlenderRenderError("reopened .blend SHA-256 differs from compile report")
    if compiler.sha256_file(scene_document) != expected_fixture_hash:
        raise BlenderRenderError("fixture hash changed before scene reopen")
    scene, sources = compiler._read_scene_and_source_records(project_root, scene_document)
    compiled_report = _json(output_root / "compile-state.json", "compiled scene state")
    active_scene = bpy.context.scene
    if active_scene.get("t6a_review_state") != "review_only" or active_scene.get("t6a_render_eligible") is not False:
        raise BlenderRenderError("reopened scene does not preserve the review-only boundary")
    if active_scene.get("t6a_fixture_sha256") != expected_fixture_hash:
        raise BlenderRenderError("reopened scene fixture hash does not match")
    if active_scene.render.engine != "CYCLES" or active_scene.camera is None:
        raise BlenderRenderError("reopened scene is missing its authored Cycles engine or camera")
    camera = active_scene.camera
    if camera.type != "CAMERA" or not camera.get("authored_by_model_scene"):
        raise BlenderRenderError("reopened scene camera is not the authored scene camera")
    asset_objects: dict[str, list[Any]] = {binding_id: [] for binding_id in sources}
    for obj in active_scene.objects:
        binding_id = obj.get("model_binding_id")
        if binding_id in asset_objects:
            asset_objects[binding_id].append(obj)
    geometry_rows = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for binding_id, objects in asset_objects.items():
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
    compiler.validate_geometry_rows(geometry_rows, set(asset_objects))

    channels = scene["motion_channels"]
    if len(channels) != 1:
        raise BlenderRenderError("reopened fixture must retain exactly one authored hinge channel")
    channel = channels[0]
    hinge = compiler.resolve_control(asset_objects[channel["binding_id"]], channel["semantic_target"], "articulation_id")
    prop_binding = next(binding_id for binding_id, row in
                        ((item["binding_id"], sources[item["binding_id"]]) for item in scene["bindings"])
                        if row["asset_kind"] == "prop")
    env_binding = next(binding_id for binding_id, row in
                       ((item["binding_id"], sources[item["binding_id"]]) for item in scene["bindings"])
                       if row["asset_kind"] == "environment")
    socket = compiler.resolve_control(asset_objects[prop_binding], "grip_socket", "socket_id")
    floor = compiler.resolve_control(asset_objects[env_binding], "floor", "surface_id")
    if not hinge.animation_data or not hinge.animation_data.action:
        raise BlenderRenderError("reopened scene lost the authored hinge action")
    if socket.parent is None or socket.parent.get("model_binding_id") != prop_binding:
        raise BlenderRenderError("reopened scene lost the grip socket parent hierarchy")
    if not any(modifier.type == "COLLISION" for modifier in floor.modifiers):
        raise BlenderRenderError("reopened scene lost the environment floor collision modifier")
    floor_top = max((floor.matrix_world @ Vector(corner)).z for corner in floor.bound_box)
    if abs(float(floor_top)) > 0.001:
        raise BlenderRenderError("reopened environment floor no longer has z=0 m top")
    source_cameras_lights = [obj.name for obj in active_scene.objects
                             if obj.type in {"CAMERA", "LIGHT"} and not obj.get("authored_by_model_scene")]
    if source_cameras_lights:
        raise BlenderRenderError(f"source cameras/lights leaked into derived scene: {source_cameras_lights}")
    authored_lights = [obj for obj in active_scene.objects if obj.type == "LIGHT" and obj.get("authored_by_model_scene")]
    if not authored_lights or any(obj.hide_render for obj in authored_lights):
        raise BlenderRenderError("reopened scene lost its authored visible lights")

    hinge_angles = {}
    for frame in compiler.REVIEW_FRAMES:
        active_scene.frame_set(frame)
        hinge_angles[str(frame)] = round(math.degrees(float(hinge.rotation_euler.x)), 6)
    active_scene.frame_set(1)
    if hinge_angles != compiled_report.get("hinge", {}).get("angles_deg"):
        raise BlenderRenderError("reopened hinge channel differs from compile-time state")
    indices = compiled_report.get("binding_pass_indices")
    if not isinstance(indices, Mapping) or set(indices) != set(sources):
        raise BlenderRenderError("binding pass indices are incomplete")
    for binding_id, pass_index in indices.items():
        for obj in asset_objects[binding_id]:
            if obj.type == "MESH" and int(obj.pass_index) != int(pass_index):
                raise BlenderRenderError(f"object index is not bound to {binding_id}: {obj.name}")

    clip_end = float(active_scene.camera.data.clip_end)
    file_nodes = _configure_compositor(bpy, active_scene, output_root, indices)
    active_scene.cycles.seed = 0
    active_scene.cycles.use_animated_seed = False
    active_scene.cycles.use_denoising = False
    active_scene.render.resolution_percentage = 100
    active_scene.render.image_settings.file_format = "PNG"
    active_scene.render.image_settings.color_mode = "RGBA"
    active_scene.render.image_settings.color_depth = "8"
    active_scene.render.film_transparent = True
    active_scene.render.use_compositing = True
    active_scene.view_layers[0].pass_alpha_threshold = 0.5

    ordered = list(frames)
    if verify_seek_parity:
        ordered = [13, 1, 25]
    first_results = {}
    for frame in ordered:
        first_results[str(frame)] = _unique_frame_outputs(
            bpy, active_scene, output_root, frame, "first", file_nodes, tuple(sources), clip_end)
    parity_rows = []
    if verify_seek_parity:
        for frame in (25, 1, 13):
            repeat = _unique_frame_outputs(
                bpy, active_scene, output_root, frame, "seek-parity", file_nodes, tuple(sources), clip_end)
            original = first_results[str(frame)]
            same = (
                original["metrics"]["depth_pixel_sha256"] == repeat["metrics"]["depth_pixel_sha256"]
                and original["metrics"]["alpha_pixel_sha256"] == repeat["metrics"]["alpha_pixel_sha256"]
                and original["metrics"]["mask_pixel_sha256"] == repeat["metrics"]["mask_pixel_sha256"]
            )
            if not same:
                raise BlenderRenderError(f"arbitrary-seek pixel parity failed at frame {frame}")
            parity_rows.append({"frame": frame, "same_decoded_pixels": same,
                                "first_output_sha256": original["output_sha256"],
                                "seek_output_sha256": repeat["output_sha256"]})

    after_hashes = {binding_id: compiler.sha256_file(Path(row["source_path"]))
                    for binding_id, row in sources.items()}
    source_hashes = {binding_id: row["source_sha256"] for binding_id, row in sources.items()}
    if after_hashes != source_hashes:
        raise BlenderRenderError("source bytes changed while reopening/rendering")
    reopened_state = {
        "scene_id": active_scene.get("model_scene_id"),
        "review_state": active_scene.get("t6a_review_state"),
        "render_eligible": active_scene.get("t6a_render_eligible"),
        "scene_frame": active_scene.frame_current,
        "frame_range": [active_scene.frame_start, active_scene.frame_end],
        "camera": camera.name,
        "authored_light_objects": sorted(obj.name for obj in authored_lights),
        "source_camera_light_objects": source_cameras_lights,
        "collections": sorted(collection.name for collection in active_scene.collection.children),
        "object_names": sorted(obj.name for obj in active_scene.objects),
        "namespaced_tree_counts": {binding_id: len(objects) for binding_id, objects in asset_objects.items()},
        "hinge_angles_deg": hinge_angles,
        "hinge_action_present": True,
        "socket": {"object": socket.name, "parent": socket.parent.name, "socket_id": socket.get("socket_id")},
        "environment_floor": {"object": floor.name, "surface_id": floor.get("surface_id"),
                              "top_z_m": round(float(floor_top), 8), "collision_modifier": True},
        "geometry_meshes": geometry_rows,
    }
    report = {
        "schema_version": "model_scene_blender_render_state.v1",
        "scene_id": active_scene.get("model_scene_id"),
        "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode("ascii"),
        "review_state": "review_only",
        "render_eligible": False,
        "fixture_sha256": expected_fixture_hash,
        "compiled_scene_path": str(compiled_path),
        "reopened_scene_sha256": compiler.sha256_file(compiled_path),
        "source_hashes": source_hashes,
        "source_hashes_unchanged": {binding_id: after_hashes[binding_id] == source_hashes[binding_id]
                                    for binding_id in sources},
        "reopened_state": reopened_state,
        "frames": [first_results[str(frame)] for frame in sorted(first_results, key=int)],
        "seek_parity": {"verified": verify_seek_parity, "order": ordered,
                        "repeat_order": [25, 1, 13] if verify_seek_parity else [], "frames": parity_rows},
    }
    compiler._write_json_exclusive(report_path, report)


def _worker_arguments() -> list[str]:
    try:
        return sys.argv[sys.argv.index("--") + 1:]
    except ValueError:
        return []


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=["render"])
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--scene-document", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--fixture-sha256")
    parser.add_argument("--compiled-scene-sha256")
    parser.add_argument("--frames", default="1,13,25")
    parser.add_argument("--seek-parity", choices=["true", "false"], default="true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(_worker_arguments())
    if args.worker == "render":
        if not all((args.project_root, args.scene_document, args.output_root, args.fixture_sha256,
                    args.compiled_scene_sha256, args.report)):
            raise BlenderRenderError("render worker arguments are incomplete")
        frames = tuple(int(item) for item in args.frames.split(",") if item)
        _blender_render_worker(args.project_root, args.scene_document, args.output_root,
                               args.fixture_sha256, args.compiled_scene_sha256, frames,
                               args.seek_parity == "true", args.report)


if __name__ == "__main__":
    _main()
