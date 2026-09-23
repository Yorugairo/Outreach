"""Offline, review-only Blender to LayeredScene raster diagnostic.

Run ``python -m content.video_engine.src.modeling.bake_layers inspect|bake`` from
the repository root. Blender reopens the immutable source with auto-execution
disabled; all scene changes occur in memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import struct
import subprocess
import sys
from typing import Any
import zlib


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"
MANIFEST = SOURCE.with_suffix(".manifest.json")
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FRAMES = {"neutral": 1, "arm_stress": 27, "leg_stress": 52}
WIDTH, HEIGHT = 512, 768
CAMERA = "ReviewCamera_front"
VISIBLE_MESHES = ("Human", "Garment_FightShorts")
# The binary centre-ray mask and antialiased beauty may differ at silhouette edges.
MAX_ALPHA_MASK_INTERIOR_MISMATCH_FRACTION = 0.005
MAX_ALPHA_MASK_INTERIOR_MISMATCH_PIXELS = 64
MAX_OUTPUT_FILE_BYTES = 16_777_216


class BakeError(ValueError):
    """An input or rendered pass violates the fixed diagnostic contract."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pinned_source(source: Path = SOURCE, manifest: Path = MANIFEST) -> str:
    if not source.is_file() or not manifest.is_file():
        raise BakeError("pinned Blender source or manifest missing")
    expected = json.loads(manifest.read_text(encoding="utf-8"))["editable_source_sha256"]
    if sha256(source) != expected:
        raise BakeError("saved Blender source SHA-256 differs from manifest")
    return expected


def _check_new_output_dir(path: Path) -> Path:
    """Reject existing destinations and symlinked ancestors before any output write."""
    absolute = path.absolute()
    if any(part.is_symlink() or (part.exists() and part.resolve() != part)
           for part in (absolute, *absolute.parents)):
        raise BakeError(f"output path contains a symlink or junction: {absolute}")
    if absolute.exists():
        raise BakeError(f"output directory must be new: {absolute}")
    return absolute


def _new_output_dir(path: Path) -> Path:
    output = _check_new_output_dir(path)
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise BakeError(f"output directory must be new: {output}") from exc
    return output


def run_blender(mode: str, output: Path, *, source: Path = SOURCE, blender: Path = BLENDER,
                hide_character: bool = False) -> dict[str, Any]:
    pinned_source(source)
    if mode not in {"inspect", "bake"}:
        raise BakeError("unsupported Blender worker mode")
    if not blender.is_file():
        raise BakeError(f"pinned Blender executable missing: {blender}")
    output = _new_output_dir(output)
    report = output / "blender-state.json"
    command = [str(blender), "--background", "--offline-mode", "--disable-autoexec",
               str(source), "--python", str(Path(__file__).resolve()), "--",
               "--worker", mode, "--output", str(output), "--report", str(report)]
    if hide_character:
        command.append("--hide-character")
    done = subprocess.run(command, capture_output=True, text=True, timeout=1200, check=False,
                          env={**os.environ, "BLENDER_USER_CONFIG": str(output / "blender-config"),
                               "BLENDER_USER_SCRIPTS": str(output / "blender-scripts")})
    (output / "blender-stdout.txt").write_text(done.stdout, encoding="utf-8")
    (output / "blender-stderr.txt").write_text(done.stderr, encoding="utf-8")
    if done.returncode or not report.is_file() or "Traceback (most recent call last)" in done.stderr:
        raise BakeError(f"Blender {mode} failed ({done.returncode}); inspect {output / 'blender-stderr.txt'}")
    return json.loads(report.read_text(encoding="utf-8"))


def _blender_worker(mode: str, output: Path, report: Path, *, hide_character: bool = False) -> None:
    import bpy  # type: ignore[import-not-found]
    from mathutils import Vector  # type: ignore[import-not-found]

    scene = bpy.context.scene
    scene.frame_set(1)
    if hide_character:
        bpy.data.objects["Human"].hide_render = True
    inventory = []
    for obj in scene.objects:
        bounds = []
        if obj.type == "MESH" and not obj.hide_render:
            bounds = [list(map(float, obj.matrix_world @ Vector(corner))) for corner in obj.bound_box]
        if obj.hide_render and obj.name.startswith("WGT-"):
            continue
        row = {"name": obj.name, "type": obj.type,
                          "hide_render": bool(obj.hide_render),
                          "visible_render": bool(obj.visible_get()),
                          "vertices": len(obj.data.vertices) if obj.type == "MESH" else 0,
                          "bounds_world_m": bounds}
        if obj.type == "CAMERA":
            row.update({"projection": obj.data.type, "ortho_scale": obj.data.ortho_scale,
                        "matrix_world": [list(map(float, row)) for row in obj.matrix_world]})
        inventory.append(row)
    state: dict[str, Any] = {
        "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode("ascii"),
        "scene_unit_system": scene.unit_settings.system,
        "scene_unit_scale_length": scene.unit_settings.scale_length,
        "frame_range": [scene.frame_start, scene.frame_end],
        "inventory": inventory,
        "source_frame_map": FRAMES,
    }
    if mode == "bake":
        state.update(_render_passes(bpy, scene, output))
    report.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _render_passes(bpy: Any, scene: Any, output: Path) -> dict[str, Any]:
    from array import array
    from mathutils.bvhtree import BVHTree  # type: ignore[import-not-found]
    from mathutils import Vector  # type: ignore[import-not-found]

    camera = bpy.data.objects.get(CAMERA)
    floor = bpy.data.objects.get("Diagnostic_Floor")
    if camera is None or camera.type != "CAMERA" or camera.data.type != "ORTHO":
        raise BakeError("fixed front orthographic camera missing")
    if floor is None or floor.type != "MESH":
        raise BakeError("diagnostic floor missing")
    for name in VISIBLE_MESHES:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH" or obj.hide_render or not obj.visible_get() or not obj.data.vertices:
            raise BakeError(f"required visible character geometry missing or hidden: {name}")
    floor.hide_render = True  # In-memory only; the saved source is never written.
    scene.camera = camera
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.filepath = str(output / "unused.png")
    scene.view_settings.view_transform = "Standard"
    visible_meshes = sorted(obj.name for obj in scene.objects if obj.type == "MESH" and not obj.hide_render and obj.visible_get())
    if not visible_meshes or any(name.startswith("WGT-") or name == floor.name for name in visible_meshes):
        raise BakeError("unexpected visible geometry in character-only bake")
    camera_matrix = [list(map(float, row)) for row in camera.matrix_world]
    camera_ortho_scale = float(camera.data.ortho_scale)
    frame_corners = camera.data.view_frame(scene=scene)
    left = min(corner.x for corner in frame_corners)
    right = max(corner.x for corner in frame_corners)
    bottom = min(corner.y for corner in frame_corners)
    top = max(corner.y for corner in frame_corners)
    direction = (camera.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
    per_frame: dict[str, Any] = {}
    for state_id, frame in FRAMES.items():
        scene.frame_set(frame)
        current_matrix = [list(map(float, row)) for row in camera.matrix_world]
        if (any(abs(current_matrix[row][col] - camera_matrix[row][col]) > 1e-6
                for row in range(4) for col in range(4))
                or abs(camera.data.ortho_scale - camera_ortho_scale) > 1e-6):
            raise BakeError("source camera changed across frames; fixed-view bake unsupported")
        current_visible = sorted(obj.name for obj in scene.objects if obj.type == "MESH" and not obj.hide_render and obj.visible_get())
        if current_visible != visible_meshes:
            raise BakeError("render-visible mesh set changed across source frames")
        beauty = output / f"{state_id}-beauty.png"
        scene.render.filepath = str(beauty)
        bpy.ops.render.render(write_still=True)
        if not beauty.is_file():
            raise BakeError(f"Blender did not write {beauty}")
        depsgraph = bpy.context.evaluated_depsgraph_get()
        vertices = []
        triangles = []
        for name in visible_meshes:
            evaluated = scene.objects[name].evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                mesh.calc_loop_triangles()
                offset = len(vertices)
                vertices.extend(evaluated.matrix_world @ vert.co for vert in mesh.vertices)
                triangles.extend(tuple(offset + index for index in triangle.vertices) for triangle in mesh.loop_triangles)
            finally:
                evaluated.to_mesh_clear()
        if not triangles:
            raise BakeError("evaluated character geometry is empty")
        bvh = BVHTree.FromPolygons(vertices, triangles, all_triangles=True)
        mask = bytearray(WIDTH * HEIGHT)
        depths = array("f", [0.0]) * (WIDTH * HEIGHT)
        for y in range(HEIGHT):
            local_y = top - (y + 0.5) / HEIGHT * (top - bottom)
            for x in range(WIDTH):
                local_x = left + (x + 0.5) / WIDTH * (right - left)
                origin = camera.matrix_world @ Vector((local_x, local_y, 0.0))
                _, _, _, distance = bvh.ray_cast(origin, direction)
                if distance is not None and math.isfinite(distance) and distance > 0:
                    index = y * WIDTH + x
                    mask[index] = 255
                    depths[index] = distance * scene.unit_settings.scale_length
        mask_path = output / f"{state_id}-mask.png"
        _write_gray_png(mask_path, WIDTH, HEIGHT, mask)
        f32 = output / f"{state_id}-depth.f32"
        with f32.open("wb") as handle:
            depths.tofile(handle)
        files = {"beauty": beauty.name, "mask": mask_path.name, "depth_f32": f32.name}
        human = scene.objects["Human"]
        evaluated = human.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            bounds = [[min(point[axis] for point in points), max(point[axis] for point in points)] for axis in range(3)]
        finally:
            evaluated.to_mesh_clear()
        per_frame[state_id] = {"source_frame": frame, "files": files,
                               "human_evaluated_bounds_world_m": bounds,
                               "geometry_pixels": sum(value > 0 for value in mask),
                               "depth_f32_positive_pixels": sum(value > 0 for value in depths),
                               "depth_f32_min_m": min((value for value in depths if value > 0), default=0),
                               "depth_f32_max_m": max(depths)}
    return {"camera": {"object": CAMERA, "projection": camera.data.type,
                       "ortho_scale_m": camera.data.ortho_scale,
                       "matrix_world": camera_matrix, "resolution_px": [WIDTH, HEIGHT],
                       "camera_space_depth_unit": "metre"},
            "floor_hidden_in_working_process": floor.hide_render,
            "visible_meshes": visible_meshes,
            "mask_method": "Blender evaluated mesh BVH ray cast at each orthographic pixel centre",
            "frames": per_frame}


def _write_gray_png(path: Path, width: int, height: int, pixels: bytes | bytearray) -> None:
    """Write the Blender ray-hit buffer as a plain 8-bit grayscale PNG."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)

    rows = b"".join(b"\x00" + bytes(pixels[y * width:(y + 1) * width]) for y in range(height))
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(rows, level=9)) + chunk(b"IEND", b""))


def _inside(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\x00" in relative:
        raise BakeError("output path must be a non-empty relative path")
    posix = PurePosixPath(relative.replace("\\", "/"))
    windows = PureWindowsPath(relative)
    if posix.is_absolute() or windows.is_absolute() or windows.drive or any(part == ".." for part in posix.parts):
        raise BakeError("output path escapes its declared root")
    path = (root.resolve() / Path(*posix.parts)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise BakeError("output path escapes its declared root") from exc
    if not path.is_file():
        raise BakeError(f"required output missing: {relative}")
    if path.stat().st_size > MAX_OUTPUT_FILE_BYTES:
        raise BakeError(f"required output exceeds {MAX_OUTPUT_FILE_BYTES} bytes: {relative}")
    return path


def _scene_document(beauty_digests: dict[str, str]) -> dict[str, Any]:
    states = []
    for index, state_id in enumerate(FRAMES):
        states.append({"state_id": state_id, "index": index, "shapes": [],
                       "raster_asset": {"path": f"{state_id}-beauty.png",
                                        "sha256": beauty_digests[state_id],
                                        "bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2]}})
    return {
        "schema_version": "authored_layer_scene.v1",
        "scene_id": "native-fighter-bridge-diagnostic",
        "review_state": "review_only", "render_eligible": False, "diagnostic_only": True,
        "art_note": "Generic saved Blender starter. Deformation probes only; no fighter identity, combat or contact claim.",
        "canvas_px": [WIDTH, HEIGHT], "clear_color": "#161c26",
        "view_envelope_deg": {"yaw_deg": [0, 0], "pitch_deg": [0, 0]},
        "occlusion_policy": "declared_depth_back_to_front",
        "camera": {"zoom_limits": [1.0, 1.04], "keyframes": [
            {"frame": 0, "zoom": 1.0, "look_px": [WIDTH / 2, HEIGHT / 2], "at_px": [WIDTH / 2, HEIGHT / 2], "yaw_deg": 0, "pitch_deg": 0},
            {"frame": 27, "zoom": 1.025, "look_px": [WIDTH / 2, HEIGHT / 2], "at_px": [WIDTH / 2 + 3, HEIGHT / 2 - 2], "yaw_deg": 0, "pitch_deg": 0},
            {"frame": 52, "zoom": 1.0, "look_px": [WIDTH / 2, HEIGHT / 2], "at_px": [WIDTH / 2, HEIGHT / 2], "yaw_deg": 0, "pitch_deg": 0},
        ]},
        "scene": {"scene_id": "native-fighter-bridge-diagnostic", "duration_frames": 72,
                  "fps": {"numerator": 24, "denominator": 1},
                  "time_origin": {"scene_time_seconds": {"numerator": 0, "denominator": 1}},
                  "events": [], "contacts": [], "motion_channels": [
                      {"channel_id": "probe-pose", "binding_id": "generic_fighter", "target_kind": "articulation",
                       "semantic_target": "saved_source_frame", "value_unit": "normalized", "interpolation": "step",
                       "keyframes": [{"frame": 0, "value": 0}, {"frame": 27, "value": 1}, {"frame": 52, "value": 2}]},
                      {"channel_id": "probe-expression", "binding_id": "generic_fighter", "target_kind": "face_control",
                       "semantic_target": "fixed_expression", "value_unit": "normalized", "interpolation": "step",
                       "keyframes": [{"frame": 0, "value": 0}]},
                  ]},
        "layers": [
            {"layer_id": "diagnostic-background", "kind": "environment", "role": "background", "depth": 0.75,
             "source_bounds_px": [-64, -64, WIDTH + 64, HEIGHT + 64],
             "painted_bounds_px": [-64, -64, WIDTH + 64, HEIGHT + 64],
             "shapes": [{"kind": "rect", "bounds_px": [-64, -64, WIDTH + 64, HEIGHT + 64], "fill": "#202937"}]},
            {"layer_id": "generic-fighter", "kind": "character", "binding_id": "generic_fighter",
             "role": "subject", "depth": 1.0, "anchor_px": [WIDTH / 2, HEIGHT / 2],
             "source_bounds_px": [0, 0, WIDTH, HEIGHT],
             "silhouette_bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
             "disocclusion_budget_px": 0, "pose_channel": "probe-pose", "expression_channel": "probe-expression",
             "shapes": [], "pose_states": states,
             "expression_states": [{"state_id": "source_expression", "index": 0, "shapes": []}]},
        ],
    }


def _alignment(beauty: Path, mask: Path, depth: Path) -> dict[str, Any]:
    from array import array
    from PIL import Image

    with Image.open(beauty) as picture, Image.open(mask) as geometry:
        if picture.format != "PNG" or picture.mode != "RGBA" or picture.size != (WIDTH, HEIGHT):
            raise BakeError("beauty must be full-resolution RGBA PNG")
        if geometry.format != "PNG" or geometry.size != (WIDTH, HEIGHT):
            raise BakeError("geometry mask dimensions or format mismatch")
        alpha = picture.getchannel("A")
        mask_l = geometry.convert("L")
        alpha_bytes = alpha.tobytes()
        mask_bytes = mask_l.tobytes()
        alpha_bounds = alpha.getbbox()
        geometry_bounds = mask_l.getbbox()
    if alpha_bounds is None or geometry_bounds is None:
        raise BakeError("empty or hidden character geometry")
    if any(abs(a - b) > 2 for a, b in zip(alpha_bounds, geometry_bounds)):
        raise BakeError("beauty alpha and native geometry mask bounds are misaligned")
    if len(depth.read_bytes()) != WIDTH * HEIGHT * 4:
        raise BakeError("float depth dimensions do not match raster passes")
    depths = array("f")
    depths.frombytes(depth.read_bytes())
    if sys.byteorder != "little":
        depths.byteswap()
    geometry_count = 0
    alpha_count = 0
    interior_mismatch = 0
    positive = []
    for a, m, d in zip(alpha_bytes, mask_bytes, depths):
        if m:
            geometry_count += 1
            if not math.isfinite(d) or not 0.1 < d < 1000:
                raise BakeError("native geometry pixel lacks finite camera-space depth")
            positive.append(d)
        elif d != 0:
            raise BakeError("float depth has values outside geometry mask")
        if a > 127:
            alpha_count += 1
            if not m:
                interior_mismatch += 1
    if geometry_count < 1000 or alpha_count < 1000:
        raise BakeError("empty or hidden character geometry")
    if interior_mismatch > max(MAX_ALPHA_MASK_INTERIOR_MISMATCH_PIXELS,
                               int(alpha_count * MAX_ALPHA_MASK_INTERIOR_MISMATCH_FRACTION)):
        raise BakeError("beauty alpha and native geometry mask interior are misaligned")
    return {"alpha_bounds_px": list(alpha_bounds), "geometry_bounds_px": list(geometry_bounds),
            "alpha_visible_pixels": alpha_count, "geometry_pixels": geometry_count,
            "interior_mismatch_pixels": interior_mismatch,
            "depth_min_m": min(positive), "depth_max_m": max(positive)}


def validate_bundle(receipt_path: Path, fixture_root: Path, evidence_root: Path) -> dict[str, Any]:
    """Recheck pinning, fixed view, geometry/depth alignment, and raster loading."""
    from content.video_engine.src.modeling.layered import LayeredScene, LayeredSceneError

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != "native_layer_bridge_diagnostic.v1":
        raise BakeError("bridge receipt schema mismatch")
    if receipt.get("review_state") != "review_only" or receipt.get("render_eligible") is not False:
        raise BakeError("bridge must stay review-only")
    if receipt.get("source", {}).get("sha256") != pinned_source():
        raise BakeError("receipt source SHA-256 differs from immutable manifest")
    if receipt["source"].get("sha256_after") != pinned_source():
        raise BakeError("source blend changed during or after diagnostic bake")
    if receipt["source"].get("manifest_sha256") != sha256(MANIFEST):
        raise BakeError("source manifest SHA-256 mismatch")
    if receipt.get("implementation_sha256") != sha256(Path(__file__)):
        raise BakeError("bridge implementation SHA-256 mismatch")
    if "matched_sheet" in receipt:
        sheet = _inside(evidence_root, receipt["matched_sheet"]["path"])
        if sha256(sheet) != receipt["matched_sheet"]["sha256"]:
            raise BakeError("matched review sheet SHA-256 mismatch")
    report_entry = receipt["blender_state"]
    report_path = _inside(evidence_root, report_entry["path"])
    if sha256(report_path) != report_entry["sha256"]:
        raise BakeError("Blender state report SHA-256 mismatch")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    camera = report.get("camera", {})
    if (receipt.get("camera") != camera or receipt.get("visible_meshes") != report.get("visible_meshes")
            or receipt.get("blender_build") != {"version": report.get("blender_version"),
                                                "hash": report.get("blender_build_hash")}):
        raise BakeError("Blender camera, visibility or build receipt differs from structured state")
    if (camera.get("object") != CAMERA or camera.get("projection") != "ORTHO"
            or camera.get("resolution_px") != [WIDTH, HEIGHT]
            or camera.get("camera_space_depth_unit") != "metre"):
        raise BakeError("fixed orthographic front view or metric camera depth unsupported")
    if report.get("scene_unit_system") != "METRIC" or report.get("scene_unit_scale_length") != 1:
        raise BakeError("saved source unit is not one metre per Blender unit")
    if not report.get("floor_hidden_in_working_process"):
        raise BakeError("diagnostic floor leaked into character bake")
    if not set(VISIBLE_MESHES).issubset(report.get("visible_meshes", [])) or any(
        name == "Diagnostic_Floor" or name.startswith("WGT-") for name in report.get("visible_meshes", [])
    ):
        raise BakeError("required character geometry missing or hidden")
    if report.get("mask_method") != "Blender evaluated mesh BVH ray cast at each orthographic pixel centre":
        raise BakeError("native geometry mask method missing")
    if receipt.get("mask_method") != report["mask_method"]:
        raise BakeError("native geometry mask receipt changed")
    if receipt.get("alpha_mask_alignment_tolerance") != {
        "bounds_px": 2,
        "interior_fraction": MAX_ALPHA_MASK_INTERIOR_MISMATCH_FRACTION,
        "interior_pixels_floor": MAX_ALPHA_MASK_INTERIOR_MISMATCH_PIXELS,
    }:
        raise BakeError("alpha and native geometry mask tolerance changed")
    if receipt.get("source_frame_to_diagnostic_frame") != {"1": 0, "27": 27, "52": 52}:
        raise BakeError("source to diagnostic frame mapping changed")
    scene_entry = receipt["scene"]
    scene_path = _inside(fixture_root, scene_entry["path"])
    if sha256(scene_path) != scene_entry["sha256"]:
        raise BakeError("authored scene SHA-256 mismatch")
    scene_document = json.loads(scene_path.read_text(encoding="utf-8"))
    if scene_document.get("view_envelope_deg") != {"yaw_deg": [0, 0], "pitch_deg": [0, 0]}:
        raise BakeError("unsupported authored view envelope")
    if scene_document.get("scene", {}).get("events") != [] or scene_document.get("scene", {}).get("contacts") != []:
        raise BakeError("diagnostic must make no combat or contact claim")
    results = {}
    for state_id, frame in FRAMES.items():
        entry = receipt["states"][state_id]
        if entry.get("source_frame") != frame or entry.get("diagnostic_frame") != (0 if frame == 1 else frame):
            raise BakeError("pose state frame mapping changed")
        paths = {}
        for label, root in (("beauty", fixture_root), ("mask", evidence_root), ("depth_f32", evidence_root)):
            item = entry[label]
            paths[label] = _inside(root, item["path"])
            if sha256(paths[label]) != item["sha256"]:
                raise BakeError(f"{state_id} {label} SHA-256 mismatch")
        render_output = _inside(evidence_root, entry["blender_beauty"]["path"])
        if sha256(render_output) != entry["blender_beauty"]["sha256"] or sha256(render_output) != sha256(paths["beauty"]):
            raise BakeError(f"{state_id} original Blender beauty SHA-256 mismatch")
        results[state_id] = _alignment(paths["beauty"], paths["mask"], paths["depth_f32"])
        if results[state_id] != entry["alignment"]:
            raise BakeError(f"{state_id} alpha/mask/depth measurements changed")
        if report["frames"][state_id]["source_frame"] != frame or report["frames"][state_id]["geometry_pixels"] < 1000:
            raise BakeError("Blender source frame has missing or hidden geometry")
    try:
        layered = LayeredScene(scene_document, asset_root=fixture_root)
        if layered.timeline.clock.fps.numerator != 24 or layered.timeline.clock.fps.denominator != 1:
            raise BakeError("diagnostic scene must run at exact 24 fps")
        for frame, state_id in ((0, "neutral"), (27, "arm_stress"), (52, "leg_stress")):
            state = layered.evaluate(frame)
            if state.selected_states["generic-fighter"]["pose"] != state_id or state.contacts or state.events:
                raise BakeError("layered diagnostic pose or contact state mismatch")
    except LayeredSceneError as exc:
        raise BakeError(f"LayeredScene rejected bridge: {exc}") from exc
    return results


def _matched_sheet(fixture_root: Path, evidence_root: Path) -> Path:
    from array import array
    from PIL import Image, ImageDraw
    from content.video_engine.src.modeling.layered import LayeredScene

    scene = LayeredScene.load(fixture_root / "bridge-scene.v1.json", asset_root=fixture_root)
    tile_w, tile_h, header = 256, 384, 34
    sheet = Image.new("RGB", (tile_w * 4, (tile_h + header) * 3), "#10151f")
    draw = ImageDraw.Draw(sheet)
    for row, (state_id, frame) in enumerate((("neutral", 0), ("arm_stress", 27), ("leg_stress", 52))):
        beauty = Image.open(fixture_root / f"{state_id}-beauty.png").convert("RGBA")
        beauty_back = Image.new("RGBA", beauty.size, "#303944")
        beauty_back.alpha_composite(beauty)
        mask = Image.open(evidence_root / f"{state_id}-mask.png").convert("RGB")
        depths = array("f")
        depths.frombytes((evidence_root / f"{state_id}-depth.f32").read_bytes())
        positive = [v for v in depths if v > 0]
        low, high = min(positive), max(positive)
        depth_gray = Image.frombytes("L", (WIDTH, HEIGHT), bytes(
            0 if value <= 0 else round(64 + 191 * (high - value) / max(high - low, 1e-6)) for value in depths
        )).convert("RGB")
        composite = scene.render(frame, supersample=1).image
        for col, (title, picture) in enumerate((("beauty RGBA", beauty_back.convert("RGB")),
                                                 ("geometry mask", mask),
                                                 (f"depth {low:.2f}-{high:.2f} m", depth_gray),
                                                 ("LayeredScene", composite))):
            x, y = col * tile_w, row * (tile_h + header)
            draw.text((x + 5, y + 6), f"{state_id} | {title}", fill="white")
            sheet.paste(picture.resize((tile_w, tile_h), Image.Resampling.LANCZOS), (x, y + header))
    destination = evidence_root / "matched-sheet.png"
    sheet.save(destination, format="PNG")
    return destination


def bake_bridge(fixture_root: Path, evidence_root: Path) -> Path:
    fixture_root = _check_new_output_dir(fixture_root)
    evidence_root = _check_new_output_dir(evidence_root)
    if fixture_root == evidence_root or fixture_root in evidence_root.parents or evidence_root in fixture_root.parents:
        raise BakeError("fixture and evidence output roots must be separate and non-nested")
    source_sha = pinned_source()
    report = run_blender("bake", evidence_root)
    fixture_root = _new_output_dir(fixture_root)
    beauty_digests = {}
    for state_id in FRAMES:
        source_beauty = evidence_root / report["frames"][state_id]["files"]["beauty"]
        target = fixture_root / f"{state_id}-beauty.png"
        shutil.copyfile(source_beauty, target)
        beauty_digests[state_id] = sha256(target)
    scene_path = fixture_root / "bridge-scene.v1.json"
    scene_path.write_text(json.dumps(_scene_document(beauty_digests), indent=2) + "\n", encoding="utf-8")
    receipt: dict[str, Any] = {
        "schema_version": "native_layer_bridge_diagnostic.v1",
        "review_state": "review_only", "render_eligible": False,
        "scope": "generic saved Blender deformation probes; no combat, contact, finished art, T7b or HG2 claim",
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": source_sha,
                   "manifest_sha256": sha256(MANIFEST), "sha256_after": sha256(SOURCE)},
        "implementation_sha256": sha256(Path(__file__)),
        "blender_state": {"path": "blender-state.json", "sha256": sha256(evidence_root / "blender-state.json")},
        "blender_build": {"version": report["blender_version"], "hash": report["blender_build_hash"]},
        "camera": report["camera"], "visible_meshes": report["visible_meshes"],
        "mask_method": report["mask_method"],
        "alpha_mask_alignment_tolerance": {
            "bounds_px": 2,
            "interior_fraction": MAX_ALPHA_MASK_INTERIOR_MISMATCH_FRACTION,
            "interior_pixels_floor": MAX_ALPHA_MASK_INTERIOR_MISMATCH_PIXELS,
        },
        "depth_units": "camera-space metres (float32 little-endian; zero where no geometry)",
        "layer_depth_units": "dimensionless plane ordering; not interchangeable with camera-space metres",
        "source_frame_to_diagnostic_frame": {"1": 0, "27": 27, "52": 52},
        "scene": {"path": scene_path.name, "sha256": sha256(scene_path)},
        "states": {},
    }
    for state_id, frame in FRAMES.items():
        beauty = fixture_root / f"{state_id}-beauty.png"
        mask = evidence_root / report["frames"][state_id]["files"]["mask"]
        depth = evidence_root / report["frames"][state_id]["files"]["depth_f32"]
        receipt["states"][state_id] = {
            "source_frame": frame, "diagnostic_frame": 0 if frame == 1 else frame,
            "blender_beauty": {"path": report["frames"][state_id]["files"]["beauty"],
                               "sha256": sha256(evidence_root / report["frames"][state_id]["files"]["beauty"])},
            "beauty": {"path": beauty.name, "sha256": sha256(beauty)},
            "mask": {"path": mask.name, "sha256": sha256(mask)},
            "depth_f32": {"path": depth.name, "sha256": sha256(depth)},
            "alignment": _alignment(beauty, mask, depth),
        }
    receipt_path = evidence_root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_bundle(receipt_path, fixture_root, evidence_root)
    sheet = _matched_sheet(fixture_root, evidence_root)
    receipt["matched_sheet"] = {"path": sheet.name, "sha256": sha256(sheet)}
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if sha256(SOURCE) != source_sha:
        raise BakeError("source blend changed during diagnostic bake")
    return receipt_path


def main() -> None:
    if "--" in sys.argv and "--worker" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        parser = argparse.ArgumentParser()
        parser.add_argument("--worker", choices=("inspect", "bake"), required=True)
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--report", type=Path, required=True)
        parser.add_argument("--hide-character", action="store_true")
        parsed = parser.parse_args(args)
        _blender_worker(parsed.worker, parsed.output, parsed.report, hide_character=parsed.hide_character)
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inspect", "bake", "validate"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args()
    if args.mode == "inspect":
        result = run_blender("inspect", args.output)
        print(json.dumps({key: result[key] for key in ("blender_version", "blender_build_hash", "scene_unit_system", "scene_unit_scale_length", "frame_range")}, indent=2))
    else:
        if args.fixture is None:
            parser.error("--fixture is required for bake and validate")
        if args.mode == "bake":
            receipt = bake_bridge(args.fixture, args.output)
            print(f"baked and validated {receipt}")
        else:
            result = validate_bundle(args.output / "receipt.json", args.fixture, args.output)
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
