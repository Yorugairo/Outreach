"""Build the optional S13 Blender mechanism proof.

This is an isolated, source-free schematic.  It deliberately does not import
episode claims, generate labels, run a simulation, or touch the scene-evidence
engine.  Run inside Blender 5.2 with one explicit mode::

    blender --background --factory-startup --python build_mechanism.py -- --samples
    blender --background --factory-startup --python build_mechanism.py -- --render

``--samples`` writes four stills and a reverse-seek determinism receipt.
``--render`` repeats that receipt and writes the five-second review movie.
Every generated artifact remains review-only; the operator owns promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Iterable

import bpy  # type: ignore
from mathutils import Vector  # type: ignore


ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "frames"
REVERSE_FRAMES = FRAMES / "reverse"
SAMPLES = (1, 36, 60, 120)
FPS = 24
FRAME_END = 120
DURATION_S = FRAME_END / FPS
W = 2560
H = 1440
CAMERA_DISTANCE = 17.0
CAMERA_TARGET = Vector((0.0, 0.0, 1.9))
AZ_START = 27.0
AZ_FINAL = 35.0
ELEVATION = 25.0
REVEAL_END = 36
LOW_STOP_Z = 0.55
SLIDER_START_Z = 3.65
SLIDER_FINAL_Z = 0.95

COLORS = {
    "cream": (0.86, 0.77, 0.58, 1.0),
    "paper": (0.97, 0.88, 0.67, 1.0),
    "charcoal": (0.025, 0.035, 0.055, 1.0),
    "cobalt": (0.018, 0.105, 0.34, 1.0),
    "teal": (0.008, 0.30, 0.31, 1.0),
    "amber": (0.82, 0.34, 0.035, 1.0),
}


def script_args() -> list[str]:
    """Return only arguments after Blender's ``--`` separator."""
    argv = sys.argv
    if "--" not in argv:
        return []
    return argv[argv.index("--") + 1 :]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--samples", action="store_true", help="render still samples and reverse-seek proof")
    modes.add_argument("--render", action="store_true", help="render still samples, then proof.mp4")
    return parser.parse_args(script_args())


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def make_material(name: str, rgba: tuple[float, float, float, float], texture: bool = True):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        raise RuntimeError(f"no Principled BSDF in {name}")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = 0.96
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.16
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.0
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    if texture:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 7.0
        noise.inputs["Detail"].default_value = 1.0
        noise.inputs["Roughness"].default_value = 0.35
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.022
        bump.inputs["Distance"].default_value = 0.018
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def add_cube(name: str, dimensions: tuple[float, float, float], location: tuple[float, float, float], material,
             bevel: float = 0.04):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("soft_printed_edges", "BEVEL")
        modifier.width = bevel * 0.45
        modifier.segments = 1
    obj.data.materials.append(material)
    return obj


def add_bar_between(name: str, start: tuple[float, float, float], end: tuple[float, float, float], width: float,
                    depth: float, material):
    a = Vector(start)
    b = Vector(end)
    delta = b - a
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(a + b) / 2)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (delta.length / 2.0, width / 2.0, depth / 2.0)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("X", "Z")
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("soft_printed_edges", "BEVEL")
    modifier.width = min(width, depth) * 0.32
    modifier.segments = 2
    obj.data.materials.append(material)
    return obj


def add_open_endpoint(name: str, center: tuple[float, float, float], width: float = 1.15, height: float = 0.92,
                      material=None) -> list:
    x, y, z = center
    # Three sides only: an intentionally open, unassigned route terminus.
    return [
        add_cube(f"{name}_top", (width, 0.18, 0.13), (x, y, z + height / 2), material),
        add_cube(f"{name}_bottom", (width, 0.18, 0.13), (x, y, z - height / 2), material),
        add_cube(f"{name}_left", (0.13, 0.18, height), (x - width / 2, y, z), material),
    ]


def look_at(obj, target: Vector) -> None:
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (target - obj.location).to_track_quat("-Z", "Y")


def camera_pose(azimuth_deg: float) -> tuple[Vector, tuple[float, float, float, float]]:
    az = math.radians(azimuth_deg)
    el = math.radians(ELEVATION)
    horizontal = CAMERA_DISTANCE * math.cos(el)
    loc = CAMERA_TARGET + Vector((horizontal * math.cos(az), horizontal * math.sin(az), CAMERA_DISTANCE * math.sin(el)))
    quat = (CAMERA_TARGET - loc).to_track_quat("-Z", "Y")
    return loc, tuple(quat)


def expected_state(frame: int) -> dict:
    phase = min(1.0, max(0.0, (frame - 1) / float(REVEAL_END - 1)))
    azimuth = AZ_START + (AZ_FINAL - AZ_START) * phase
    slider_z = SLIDER_START_Z + (SLIDER_FINAL_Z - SLIDER_START_Z) * phase
    return {
        "frame": frame,
        "time_s": round((frame - 1) / FPS, 6),
        "camera_azimuth_deg": round(azimuth, 6),
        "camera_elevation_deg": ELEVATION,
        "slider_z": round(slider_z, 6),
        "low_stop_z": LOW_STOP_Z,
        "available_downward_span": round(max(0.0, slider_z - LOW_STOP_Z), 6),
    }


def keyframe_linear(obj) -> None:
    if not obj.animation_data or not obj.animation_data.action:
        return
    # Blender 5.2's slotted Action API no longer exposes the legacy fcurves
    # collection on every action.  Walk channel bags when present, retaining
    # the legacy path for older Blender builds.
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
            point.interpolation = "LINEAR"


def animate_scene(camera, slider, capacity_span) -> None:
    for frame in (1, REVEAL_END, REVEAL_END + 1, FRAME_END):
        state = expected_state(frame)
        loc, quat = camera_pose(state["camera_azimuth_deg"])
        camera.location = loc
        camera.rotation_mode = "QUATERNION"
        camera.rotation_quaternion = quat
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        slider.location.z = state["slider_z"]
        slider.keyframe_insert(data_path="location", index=2, frame=frame)

        span = max(0.08, state["available_downward_span"])
        capacity_span.location.z = (state["slider_z"] + LOW_STOP_Z) / 2.0
        capacity_span.scale.z = span
        capacity_span.keyframe_insert(data_path="location", index=2, frame=frame)
        capacity_span.keyframe_insert(data_path="scale", index=2, frame=frame)

    keyframe_linear(camera)
    keyframe_linear(slider)
    keyframe_linear(capacity_span)


def configure_render(scene) -> None:
    # Blender 5.2 exposes the Eevee engine under this stable identifier.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = W
    scene.render.resolution_y = H
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.fps_base = 1.0
    scene.frame_start = 1
    scene.frame_end = FRAME_END
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.world.color = COLORS["cream"][:3]
    if scene.world.use_nodes:
        background = scene.world.node_tree.nodes.get("Background")
        if background:
            background.inputs["Color"].default_value = COLORS["cream"]
            background.inputs["Strength"].default_value = 0.32
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def add_area_light(name: str, location: tuple[float, float, float], energy: float, size: float, color: tuple[float, float, float]):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    look_at(obj, CAMERA_TARGET)
    return obj


def build_scene() -> dict:
    clear_scene()
    scene = bpy.context.scene
    configure_render(scene)

    mats = {name: make_material(name, color) for name, color in COLORS.items()}

    # Flat printed world: a large cream board and a quiet cobalt backing slab.
    add_cube("base_board", (15.5, 9.2, 0.28), (0.0, 0.0, -0.28), mats["paper"], bevel=0.08)
    add_cube("backing_slab", (15.5, 0.26, 6.6), (0.0, -2.9, 2.6), mats["cobalt"], bevel=0.08)
    add_cube("backing_inset", (14.8, 0.08, 5.9), (0.0, -2.74, 2.6), mats["teal"], bevel=0.04)
    # Restrained carved-ink hatching: deterministic, low-contrast marks on the
    # backing plate rather than a glossy procedural texture.
    for index, x in enumerate((-6.4, -5.0, -3.6, 3.6, 5.0, 6.4)):
        add_bar_between(
            f"backing_hatch_{index}",
            (x - 0.65, -2.61, 0.25),
            (x + 0.65, -2.61, 5.4),
            0.045,
            0.035,
            mats["charcoal"],
        )

    # RRP chamber, deliberately an abstract rigid cutaway rather than a tank.
    chamber_y = 0.05
    add_cube("chamber_left_wall", (0.34, 0.86, 4.7), (-1.75, chamber_y, 2.55), mats["cobalt"], bevel=0.06)
    add_cube("chamber_right_wall", (0.34, 0.86, 4.7), (1.75, chamber_y, 2.55), mats["cobalt"], bevel=0.06)
    add_cube("chamber_top_wall", (3.84, 0.86, 0.34), (0.0, chamber_y, 4.73), mats["cobalt"], bevel=0.06)
    add_cube("chamber_back", (3.38, 0.12, 4.22), (0.0, -0.32, 2.55), mats["cream"], bevel=0.03)
    add_cube("chamber_track", (0.16, 0.24, 3.62), (0.0, 0.48, 2.55), mats["teal"], bevel=0.025)
    add_cube("chamber_left_contour", (0.075, 0.09, 4.15), (-1.53, 0.53, 2.55), mats["charcoal"], bevel=0.01)
    add_cube("chamber_right_contour", (0.075, 0.09, 4.15), (1.53, 0.53, 2.55), mats["charcoal"], bevel=0.01)
    add_cube("chamber_top_contour", (3.15, 0.09, 0.075), (0.0, 0.53, 4.50), mats["charcoal"], bevel=0.01)
    add_cube("low_stop", (2.95, 0.5, 0.22), (0.0, 0.51, LOW_STOP_Z), mats["amber"], bevel=0.05)
    add_cube("low_stop_contour", (2.72, 0.08, 0.075), (0.0, 0.79, LOW_STOP_Z + 0.16), mats["charcoal"], bevel=0.01)
    add_cube("low_stop_shadow", (2.50, 0.16, 0.10), (0.0, 0.80, LOW_STOP_Z - 0.18), mats["charcoal"], bevel=0.02)

    slider = add_cube("adjustment_slider", (2.45, 0.72, 0.34), (0.0, 0.64, SLIDER_START_Z), mats["amber"], bevel=0.07)
    add_cube("slider_face", (1.62, 0.08, 0.11), (0.0, 1.02, SLIDER_START_Z), mats["paper"], bevel=0.02)
    capacity_span = add_cube("available_downward_span", (0.22, 0.24, 1.0), (0.0, 0.64, 2.0), mats["amber"], bevel=0.03)
    capacity_span["semantic_role"] = "illustrative_remaining_adjustment_span"
    slider["semantic_role"] = "illustrative_rigid_adjustment_slider"
    slider["source_data"] = False
    capacity_span["source_data"] = False

    # Two open, unassigned alternatives.  Their empty ends are intentional.
    left_start = (-1.62, 0.35, 0.72)
    left_end = (-4.55, 1.20, 0.72)
    right_start = (1.62, 0.35, 0.72)
    right_end = (4.55, 1.20, 0.72)
    add_bar_between("route_left_rail", left_start, left_end, 0.24, 0.15, mats["teal"])
    add_bar_between("route_right_rail", right_start, right_end, 0.24, 0.15, mats["cobalt"])
    add_cube("route_left_join", (0.18, 0.18, 0.18), (-1.62, 0.36, 0.72), mats["amber"], bevel=0.04)
    add_cube("route_right_join", (0.18, 0.18, 0.18), (1.62, 0.36, 0.72), mats["amber"], bevel=0.04)
    add_open_endpoint("route_left_open", left_end, material=mats["teal"])
    add_open_endpoint("route_right_open", right_end, material=mats["cobalt"])

    # Blank bays reserve later code labels without putting text in the proof.
    add_cube("label_zone_left", (2.5, 0.11, 0.75), (-5.1, 1.56, 4.45), mats["paper"], bevel=0.03)
    add_cube("label_zone_right", (2.5, 0.11, 0.75), (5.1, 1.56, 4.45), mats["paper"], bevel=0.03)

    # Small printed registration marks make the flat composition read as a plate,
    # not as a glossy product render.  They carry no data or text.
    for x in (-6.3, 6.3):
        add_cube("registration_mark", (0.12, 0.10, 0.72), (x, 1.58, 0.55), mats["charcoal"], bevel=0.01)

    camera_data = bpy.data.cameras.new("s13_orthographic_camera")
    camera = bpy.data.objects.new("s13_orthographic_camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 18.5
    scene.camera = camera

    add_area_light("key_print_light", (5.0, 6.0, 9.0), 500.0, 8.0, (1.0, 0.83, 0.62))
    add_area_light("fill_cobalt_light", (-5.0, 0.0, 6.0), 260.0, 7.0, (0.35, 0.55, 1.0))
    add_area_light("edge_teal_light", (0.0, -4.0, 5.0), 180.0, 6.0, (0.28, 0.92, 0.83))

    animate_scene(camera, slider, capacity_span)
    scene.frame_set(1)
    scene["proof_schema"] = "fed_s13_blender_mechanism.v1"
    scene["source_data"] = False
    scene["render_eligible"] = False
    scene["review_state"] = "review_only"

    return {
        "camera": camera,
        "slider": slider,
        "capacity_span": capacity_span,
        "route_positions": {
            "left": {"start": list(left_start), "open_end": list(left_end)},
            "right": {"start": list(right_start), "open_end": list(right_end)},
        },
        "label_zones": {
            "left": {"center": [-5.1, 1.56, 4.45], "size": [2.5, 0.11, 0.75]},
            "right": {"center": [5.1, 1.56, 4.45], "size": [2.5, 0.11, 0.75]},
        },
    }


def state_document(scene_info: dict) -> dict:
    camera_transforms = {}
    for frame in SAMPLES:
        state = expected_state(frame)
        location, quaternion = camera_pose(state["camera_azimuth_deg"])
        camera_transforms[str(frame)] = {
            "location": [round(float(value), 6) for value in location],
            "rotation_quaternion": [round(float(value), 6) for value in quaternion],
        }
    return {
        "schema": "fed_s13_blender_mechanism.v1",
        "review_state": "review_only",
        "render_eligible": False,
        "source_data": False,
        "illustrative_geometry_units": True,
        "scene": {"resolution": [W, H], "fps": FPS, "frames": [1, FRAME_END], "duration_s": DURATION_S},
        "camera": {
            "type": "orthographic",
            "azimuth_deg": {"frame_1": AZ_START, "frame_36": AZ_FINAL, "frame_120": AZ_FINAL},
            "elevation_deg": ELEVATION,
            "reveal_degrees": AZ_FINAL - AZ_START,
            "reveal_frames": [1, REVEAL_END],
            "locked_from_frame": REVEAL_END + 1,
            "target": list(CAMERA_TARGET),
            "ortho_scale": 18.5,
            "sample_transforms": camera_transforms,
        },
        "chamber": {
            "frame_geometry": {
                "left_wall_center": [-1.75, 0.05, 2.55],
                "right_wall_center": [1.75, 0.05, 2.55],
                "top_wall_center": [0.0, 0.05, 4.73],
                "inner_back_center": [0.0, -0.32, 2.55],
                "outer_width": 3.84,
                "inner_height": 4.22,
            },
            "slider_dimensions": [2.45, 0.72, 0.34],
            "low_stop_z": LOW_STOP_Z,
            "slider_z": {str(frame): expected_state(frame)["slider_z"] for frame in SAMPLES},
            "available_downward_span": {
                str(frame): expected_state(frame)["available_downward_span"] for frame in SAMPLES
            },
            "semantic_note": "Rigid schematic chamber; no financial scale or source observation.",
        },
        "routes": scene_info["route_positions"],
        "label_zones": scene_info["label_zones"],
        "samples": [expected_state(frame) for frame in SAMPLES],
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def canonicalize_png(path: Path) -> None:
    """Rewrite Blender's pixels with stable PNG chunks/compression.

    Blender's rendered RGBA pixels were identical on forward/reverse seeks,
    but its IDAT compressor can emit different byte streams.  The proof hashes
    this fixed, pixel-preserving encoding rather than treating compressor
    bookkeeping as visual nondeterminism.
    """
    source = path.read_bytes()
    if not source.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError(f"not a PNG: {path}")
    i = 8
    ihdr = None
    image_data = bytearray()
    while i < len(source):
        if i + 12 > len(source):
            raise RuntimeError(f"truncated PNG: {path}")
        length = struct.unpack(">I", source[i : i + 4])[0]
        kind = source[i + 4 : i + 8]
        payload = source[i + 8 : i + 8 + length]
        i += 12 + length
        if kind == b"IHDR":
            ihdr = payload
        elif kind == b"IDAT":
            image_data.extend(payload)
        elif kind == b"IEND":
            break
    if ihdr is None or not image_data:
        raise RuntimeError(f"PNG has no image data: {path}")
    raw = zlib.decompress(bytes(image_data))
    stable = b"\x89PNG\r\n\x1a\n"
    stable += _png_chunk(b"IHDR", ihdr)
    stable += _png_chunk(b"sRGB", b"\x00")
    stable += _png_chunk(b"IDAT", zlib.compress(raw, level=9))
    stable += _png_chunk(b"IEND", b"")
    path.write_bytes(stable)


def render_png(scene, frame: int, path: Path) -> None:
    scene.frame_set(frame)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Blender did not write {path}")
    canonicalize_png(path)


def render_samples(scene) -> dict:
    FRAMES.mkdir(parents=True, exist_ok=True)
    REVERSE_FRAMES.mkdir(parents=True, exist_ok=True)
    forward = {}
    reverse = {}
    for frame in SAMPLES:
        path = FRAMES / f"frame-{frame:04d}.png"
        render_png(scene, frame, path)
        forward[frame] = sha256(path)
    for frame in reversed(SAMPLES):
        path = REVERSE_FRAMES / f"frame-{frame:04d}.png"
        render_png(scene, frame, path)
        reverse[frame] = sha256(path)
    comparisons = {str(frame): forward[frame] == reverse[frame] for frame in SAMPLES}
    doc = {
        "schema": "fed_s13_blender_determinism.v1",
        "sample_frames": list(SAMPLES),
        "forward_hashes": {str(k): v for k, v in forward.items()},
        "reverse_hashes": {str(k): v for k, v in reverse.items()},
        "reverse_seek_equal": all(comparisons.values()),
        "comparisons": comparisons,
        "note": "The same rigid/keyframed scene was sampled forward and in reverse order; stable pixel-preserving PNG encoding removes compressor bookkeeping; no simulation is used.",
    }
    (ROOT / "determinism.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    lines = ["# SHA-256 of canonical forward sample frames", "# reverse samples are compared in determinism.json"]
    lines.extend(f"{forward[frame]}  frames/frame-{frame:04d}.png" for frame in SAMPLES)
    (ROOT / "frame-hashes.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return doc


def render_movie(scene) -> dict:
    movie = ROOT / "proof.mp4"
    scene.frame_set(1)
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.audio_codec = "NONE"
    scene.render.filepath = str(movie)
    bpy.ops.render.render(animation=True)
    result = {"path": str(movie.relative_to(ROOT)), "exists": movie.is_file(), "bytes": movie.stat().st_size if movie.is_file() else 0}
    ffprobe = shutil.which("ffprobe")
    if ffprobe and movie.is_file():
        command = [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate:format=duration",
            "-of",
            "json",
            str(movie),
        ]
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        result["ffprobe_command"] = " ".join(command)
        result["ffprobe_exit"] = proc.returncode
        try:
            result["ffprobe"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            result["ffprobe_stdout"] = proc.stdout[-2000:]
            result["ffprobe_stderr"] = proc.stderr[-2000:]
    else:
        result["ffprobe"] = "not available on PATH" if not ffprobe else "movie missing"
    return result


def output_files() -> list[Path]:
    paths = [
        ROOT / "build_mechanism.py",
        ROOT / "mechanism.blend",
        ROOT / "state.json",
        ROOT / "determinism.json",
        ROOT / "determinism-initial-failed.json",
        ROOT / "frame-hashes.sha256",
        ROOT / "PROOF.md",
    ]
    paths.extend(FRAMES / f"frame-{frame:04d}.png" for frame in SAMPLES)
    paths.extend(REVERSE_FRAMES / f"frame-{frame:04d}.png" for frame in SAMPLES)
    paths.extend(FRAMES.glob("candidate-*.png"))
    movie = ROOT / "proof.mp4"
    if movie.is_file():
        paths.append(movie)
    return [path for path in paths if path.is_file()]


def write_proof(mode: str, state: dict, determinism: dict, movie: dict | None) -> None:
    lines = [
        "# S13 Blender mechanism proof",
        "",
        "Status: **review-only diagnostic**; `render_eligible=false`; no operator or HG2 approval claimed.",
        "",
        "## Scope",
        "",
        "This is a five-second, 24 fps, 2560x1440 schematic cutaway for S13. It uses rigid, code-authored geometry: an abstract RRP adjustment chamber approaches a marked low stop while two alternative route rails remain visibly open and unassigned. The amber span is an illustrative geometric cue, not a financial quantity, source observation, chart, or prediction. There is no fluid simulation, generated text, label, or source-data import. Labels are intentionally reserved for the later code composition.",
        "",
        "Camera: orthographic, 35° azimuth / 25° elevation after one 8° reveal over frames 1–36; locked from frame 37. All animated poses use direct keyframes with linear interpolation and no physics/simulation.",
        "",
        "## Files and validation",
        "",
        f"Builder mode: `{mode}`. Samples: frames 1, 36, 60, 120. Reverse-seek equality: **{determinism['reverse_seek_equal']}** (see `determinism.json`).",
        "",
        "The full movie, when present, must be checked independently with the exact ffprobe command recorded below. A CLI probe is not a render test or asset approval.",
        "",
        "```text",
        "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python build_mechanism.py -- --samples",
        "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe --background --factory-startup --python build_mechanism.py -- --render",
        "ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration -of json proof.mp4",
        "```",
        "",
        "## Custody",
        "",
        "All files are code-authored review outputs. `quarantine-manifest.json` is the custody record; the operator must inspect representative frames and compare the 2D fallback before any promotion. This proof does not alter the episode builder or shared renderer.",
        "",
    ]
    if movie:
        lines.extend(["## Movie probe receipt", "", "```json", json.dumps(movie, indent=2), "```", ""])
    (ROOT / "PROOF.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest() -> None:
    entries = []
    for path in sorted(output_files(), key=lambda p: p.relative_to(ROOT).as_posix()):
        rel = path.relative_to(ROOT).as_posix()
        entries.append({"path": rel, "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "schema": "asset-quarantine.v1",
        "asset_id": "fed-s13-blender-mechanism-proof",
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

    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "mechanism.blend"))
    determinism = render_samples(scene)
    movie = render_movie(scene) if args.render else None
    # Keep the saved .blend in a predictable still/sample state, not in a
    # transient movie-output mode or an arbitrary reverse-seek frame.
    scene.render.image_settings.file_format = "PNG"
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "mechanism.blend"))
    write_proof("render" if args.render else "samples", state, determinism, movie)
    write_manifest()
    print(json.dumps({"mode": "render" if args.render else "samples", "reverse_seek_equal": determinism["reverse_seek_equal"], "movie": movie}, indent=2))
    return 0 if determinism["reverse_seek_equal"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
