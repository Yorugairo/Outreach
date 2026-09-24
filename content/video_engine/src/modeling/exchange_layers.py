"""Source-clock 30 fps Blender exchange to review-only 24 fps fighter planes.

The immutable Blender scene renders a combined visible contribution, EEVEE
Cryptomatte actor mattes, and actor-masked depth. Host-side alpha normalization
turns the disjoint visible coverage into two ordered transparent fighter planes
that recompose at the fixed source view. The planes are not hidden-surface RGB
reconstruction and do not support arbitrary independent parallax.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat
import subprocess
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_FIGHT_MOTION_PATH = ROOT / "content/video_engine/src/modeling/blender/fight_motion.py"
_FIGHT_MOTION_SPEC = importlib.util.spec_from_file_location("t7a3_pinned_fight_motion", _FIGHT_MOTION_PATH)
if _FIGHT_MOTION_SPEC is None or _FIGHT_MOTION_SPEC.loader is None:
    raise RuntimeError(f"cannot load pinned fight-motion implementation: {_FIGHT_MOTION_PATH}")
fight_motion = importlib.util.module_from_spec(_FIGHT_MOTION_SPEC)
sys.modules[_FIGHT_MOTION_SPEC.name] = fight_motion
_FIGHT_MOTION_SPEC.loader.exec_module(fight_motion)


Image: Any = None
ImageDraw: Any = None
ImageFont: Any = None
ImageFilter: Any = None
LayeredScene: Any = None
LayeredSceneError: type[Exception] = ValueError
np: Any = None


def _ensure_host_dependencies() -> None:
    """Load Pillow and LayeredScene only in the host Python, not Blender's worker."""
    global Image, ImageDraw, ImageFont, ImageFilter, LayeredScene, LayeredSceneError, np
    if Image is not None:
        return
    from PIL import Image as pillow_image, ImageDraw as pillow_draw, ImageFilter as pillow_filter, ImageFont as pillow_font
    import numpy as numpy

    from content.video_engine.src.modeling.layered import (
        LayeredScene as layered_scene,
        LayeredSceneError as layered_scene_error,
    )

    Image = pillow_image
    ImageDraw = pillow_draw
    ImageFont = pillow_font
    ImageFilter = pillow_filter
    LayeredScene = layered_scene
    LayeredSceneError = layered_scene_error
    np = numpy


SCHEMA_V1 = "model_exchange_layers.v1"
SCHEMA = "model_exchange_layers.v2"
SOURCE_SCENE_SHA256 = "942ba684be00e87988330e6709c14a46fd54c34f64714c2253727b863a3d772f"
SOURCE_BUNDLE_RELATIVE = Path(
    "content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange/t7a3-parent-source"
)
REVIEW_RELATIVE = Path(
    "content/video_engine/review/model-engines/benchmark-v1/2_5d/source-exchange"
)
T7A4_REVIEW_RELATIVE = Path(
    "content/video_engine/review/model-engines/benchmark-v1/2_5d/fighter-planes-t7a4"
)
FIXTURE_RELATIVE = fight_motion.FIXTURE_RELATIVE
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FPS = 24
FRAME_COUNT = 29
FRAME_END = FRAME_COUNT - 1
WIDTH, HEIGHT = 540, 960
MAX_OUTPUT_BYTES = 16_777_216
SMOKE_OUTPUT_FRAMES = (8, 19)  # Source frames 10 and 24: first right contact and left-hook contact.
CAMERA_ZOOM_LIMITS = (1.0, 1.005)
CAMERA_KEYFRAMES = (
    {"frame": 0, "zoom": 1.0, "look_px": [270, 480], "at_px": [270, 480], "yaw_deg": 0, "pitch_deg": 0},
    {"frame": 14, "zoom": 1.005, "look_px": [270, 480], "at_px": [272, 479], "yaw_deg": 0, "pitch_deg": 0},
    {"frame": 28, "zoom": 1.0, "look_px": [270, 480], "at_px": [270, 480], "yaw_deg": 0, "pitch_deg": 0},
)
BACKGROUND_BLEED_PX = 32
MAX_DISOCCLUSION_PX = 6.0
EVENT_MAP = {
    10: ("right_hand_contact_window_start",),
    11: ("right_hand_contact_window_end",),
    12: ("right_hand_follow_through",),
    24: ("left_hook_contact",),
    25: ("receiving_head_response",),
    26: ("left_hand_follow_through",),
}
EXPECTED_EVENTS = [
    {"event_id": "first_right_contact_window", "source_frames": [10, 11], "output_frames": [8, 9]},
    {"event_id": "right_hand_follow_through", "source_frames": [12], "output_frames": [10]},
    {"event_id": "left_hook_contact", "source_frames": [24], "output_frames": [19]},
    {"event_id": "receiving_head_response", "source_frames": [25], "output_frames": [20]},
    {"event_id": "left_hand_follow_through", "source_frames": [26], "output_frames": [21]},
]
DIAGNOSTIC_NOTE = (
    "Generic two-rig source exchange only. Fighter planes are visible contributions from one combined source view, "
    "not hidden-surface RGB reconstruction or arbitrary independent parallax. Not approved fighter art. The source "
    "ends before the fall or ground continuation; no fall, extra impact, extra head response, or audio change is authored."
)
PREVIEW_LABEL = (
    "FIGHTER-PLANES DIAGNOSTIC | FIXED SOURCE VIEW / VISIBLE CONTRIBUTIONS / "
    "NO INDEPENDENT PARALLAX / NO FALL / NO ART APPROVAL"
)
FIGHTER_LAYERS = {
    "fighter_a": {
        "label": "A",
        "binding_id": "attacker",
        "layer_id": "generic-fighter-a-visible-contribution",
        "pose_channel": "fighter-a-source-frame-pose",
        "expression_channel": "fighter-a-source-frame-expression",
        "depth": 1.0,
    },
    "fighter_b": {
        "label": "B",
        "binding_id": "receiver",
        "layer_id": "generic-fighter-b-visible-contribution",
        "pose_channel": "fighter-b-source-frame-pose",
        "expression_channel": "fighter-b-source-frame-expression",
        "depth": 1.0,
    },
}
OCCLUSION_CONTRACT = {
    "method": "per_pixel_visible_contribution_mattes_with_ordered_alpha_normalization",
    "source_over_order_back_to_front": ["fighter_b", "fighter_a"],
    "projection_group": {
        "mode": "source_over_before_projection",
        "layer_keys_back_to_front": ["fighter_b", "fighter_a"],
    },
    "coverage_rule": "scale A/B Cryptomatte weights proportionally to source combined alpha",
    "byte_alpha_rule": (
        "A_alpha8=round(source_alpha8*A_weight/(A_weight+B_weight)); "
        "B_alpha8=round((source_alpha8-A_alpha8)*255/(255-A_alpha8)); clamp to 0..255"
    ),
    "source_rgb_rule": "use each actor Cryptomatte-masked source-view RGB where its normalized matte owns coverage",
    "hidden_surface_rgb_reconstructed": False,
    "arbitrary_independent_parallax_supported": False,
    "equal_camera_depth": True,
    "layer_order_is_authored_back_to_front": True,
    "recomposition_claim": "measured per frame from hash-pinned planes and recomputed by the validator",
}
RECOMPOSITION_LIMITS = {
    "transparent_alpha_max_error_8bit": 0,
    "transparent_visible_rgb_max_channel_error_8bit": 1,
    "layered_scene_max_channel_error_8bit": 24,
    "layered_scene_mean_channel_error_max": 0.003,
    "layered_scene_actor_alpha_max_error_8bit": 24,
    "coverage_assignment_error_threshold": "2/255",
}


class ExchangeLayersError(ValueError):
    """The pinned exchange cannot be rasterized or validated safely."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_tracked_python_sha256(path: Path, expected_sha256: Any, label: str) -> str:
    """Accept exact Python bytes or the same source with LF/CRLF-only changes.

    Receipts keep the raw digest written by their producing checkout. The
    validator permits only the two common newline encodings of identical text;
    it does not normalize code, whitespace, or any binary evidence.
    """
    if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(char not in "0123456789abcdefABCDEF" for char in expected_sha256)):
        raise ExchangeLayersError(f"{label} SHA-256 pin is malformed")
    try:
        payload = Path(path).read_bytes()
    except OSError as exc:
        raise ExchangeLayersError(f"cannot read tracked Python implementation for {label}: {path}") from exc

    raw_digest = hashlib.sha256(payload).hexdigest()
    lf = bytes((10,))
    cr = bytes((13,))
    crlf = cr + lf
    # Refuse to synthesize candidates for lone-CR files; only LF and CRLF are
    # checkout line endings covered by this compatibility check.
    without_crlf = payload.replace(crlf, b"")
    digests = {raw_digest}
    if cr not in without_crlf:
        lf_payload = payload.replace(crlf, lf)
        digests.add(hashlib.sha256(lf_payload).hexdigest())
        digests.add(hashlib.sha256(lf_payload.replace(lf, crlf)).hexdigest())
    normalized_expected = expected_sha256.lower()
    if normalized_expected not in digests:
        raise ExchangeLayersError(
            f"{label} SHA-256 differs; only exact bytes or LF/CRLF-only line-ending changes are accepted"
        )
    return "exact" if normalized_expected == raw_digest else "lf_crlf_equivalent"


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def source_frame_for_output(output_frame: int) -> int:
    """Nearest 30 fps source frame for a 24 fps frame; exact ties round down."""
    if isinstance(output_frame, bool) or not isinstance(output_frame, int) or not 0 <= output_frame < FRAME_COUNT:
        raise ExchangeLayersError(f"output frame must be an integer in 0..{FRAME_END}")
    return (5 * output_frame + 1) // 4


def source_frame_map() -> tuple[int, ...]:
    mapping = tuple(source_frame_for_output(frame) for frame in range(FRAME_COUNT))
    if mapping[0] != 0 or mapping[-1] != 35 or tuple(sorted(set(mapping))) != mapping:
        raise ExchangeLayersError("24 fps source mapping no longer covers the pinned 0..35 exchange in order")
    return mapping


def output_frames_for_source(source_frame: int) -> list[int]:
    return [output for output, sample in enumerate(source_frame_map()) if sample == source_frame]


def _reject_redirected_path_chain(path: Path) -> None:
    """Reject symlinks and Windows reparse-point redirects in every ancestor."""
    current = Path(path).absolute()
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    while True:
        try:
            info = current.lstat()
        except FileNotFoundError:
            info = None
        except OSError as exc:
            raise ExchangeLayersError(f"cannot inspect path component: {current}") from exc
        if info is not None:
            attributes = getattr(info, "st_file_attributes", 0)
            if stat.S_ISLNK(info.st_mode) or attributes & reparse_point:
                raise ExchangeLayersError(f"path contains symlink or junction redirection: {current}")
        parent = current.parent
        if parent == current:
            break
        current = parent


def _inside(root: Path, relative: str, label: str, *, require_file: bool = True) -> Path:
    if not isinstance(relative, str) or not relative or "\x00" in relative:
        raise ExchangeLayersError(f"{label} path is missing or malformed")
    posix = PurePosixPath(relative.replace("\\", "/"))
    windows = PureWindowsPath(relative)
    if (posix.is_absolute() or windows.is_absolute() or windows.drive
            or any(part in {"", ".", ".."} for part in posix.parts)):
        raise ExchangeLayersError(f"unsafe {label} path")
    candidate = root / Path(*posix.parts)
    _reject_redirected_path_chain(candidate)
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise ExchangeLayersError(f"{label} path is missing or escapes its root") from exc
    if require_file and not resolved.is_file():
        raise ExchangeLayersError(f"{label} is not a file")
    return resolved


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExchangeLayersError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ExchangeLayersError(f"{label} root must be an object")
    return value


def validate_source_bundle(
    root: Path = ROOT,
    source_dir: Path | None = None,
) -> dict[str, Any]:
    """Validate the parent-rebuilt, hash-pinned T5a.3 scene and its receipt."""
    root = Path(root).resolve(strict=True)
    expected_dir = root / SOURCE_BUNDLE_RELATIVE
    supplied_dir = expected_dir if source_dir is None else Path(source_dir)
    _reject_redirected_path_chain(supplied_dir)
    try:
        resolved_dir = supplied_dir.resolve(strict=True)
        if resolved_dir != expected_dir.resolve(strict=True) or not resolved_dir.is_dir():
            raise ExchangeLayersError("source exchange bundle must be the parent-provided pinned review directory")
    except OSError as exc:
        raise ExchangeLayersError("parent-provided source exchange bundle is missing") from exc

    fixture_path = root / FIXTURE_RELATIVE
    try:
        fixture = fight_motion.validate_fixture(root, fixture_path)
    except (OSError, ValueError, KeyError) as exc:
        raise ExchangeLayersError(f"pinned source exchange fixture failed validation: {exc}") from exc

    receipt_path = resolved_dir / "receipt.json"
    scene_path = resolved_dir / "source-exchange.blend"
    _reject_redirected_path_chain(receipt_path)
    _reject_redirected_path_chain(scene_path)
    receipt = _read_json(receipt_path, "parent source exchange receipt")
    scene_digest = sha256(scene_path)
    if (receipt.get("schema") != fight_motion.SCHEMA
            or receipt.get("status") != "review_only_diagnostic"
            or receipt.get("fps") != 30 or receipt.get("frame_range") != [0, 35]
            or receipt.get("embedded_scripts") != "disabled"
            or receipt.get("blender") != "5.2.2 LTS"):
        raise ExchangeLayersError("parent source exchange receipt contract differs")
    scene_record = receipt.get("scene")
    if (not isinstance(scene_record, dict) or scene_record.get("path") != scene_path.name
            or scene_record.get("sha256") != SOURCE_SCENE_SHA256
            or scene_record.get("sha256") != scene_digest
            or scene_record.get("bytes") != scene_path.stat().st_size):
        raise ExchangeLayersError("parent saved scene hash or byte count is stale")
    expected_source = {name: fixture[name] for name in ("source_video", "source_clock", "source_blend")}
    if (receipt.get("source") != expected_source
            or receipt.get("source_blend_sha256_after") != fixture["source_blend"]["sha256"]
            or receipt.get("fixture_sha256") != fight_motion.FIXTURE_SHA256):
        raise ExchangeLayersError("parent source or fixture pin differs")
    _verify_tracked_python_sha256(
        Path(fight_motion.__file__), receipt.get("implementation_sha256"), "fight_motion.py implementation",
    )
    frames = receipt.get("frames")
    metrics = receipt.get("metrics")
    if (not isinstance(frames, list) or len(frames) != 36
            or [row.get("frame") for row in frames] != list(range(36))
            or not isinstance(metrics, dict)
            or not isinstance(metrics.get("checks"), dict)
            or not metrics["checks"] or not all(metrics["checks"].values())):
        raise ExchangeLayersError("parent source scene is missing complete measured 30 fps frame evidence")
    try:
        render_verification = fight_motion._verify_receipt_renders(receipt, receipt_path)
    except fight_motion.FightMotionError as exc:
        raise ExchangeLayersError(f"parent source scene review renders failed validation: {exc}") from exc
    if render_verification != "verified":
        raise ExchangeLayersError("parent source scene must have its nine receipt-pinned review renders")

    root_relative = lambda path: Path(path).resolve().relative_to(root).as_posix()
    return {
        "fixture": fixture,
        "receipt": receipt,
        "scene_path": scene_path,
        "receipt_path": receipt_path,
        "scene_sha256": scene_digest,
        "receipt_sha256": sha256(receipt_path),
        "fixture_path": fixture_path,
        "fixture_sha256": fight_motion.FIXTURE_SHA256,
        "source": {
            name: {"path": fixture[name]["path"], "sha256": fixture[name]["sha256"]}
            for name in ("source_video", "source_clock", "source_blend")
        },
        "source_bundle_path": root_relative(resolved_dir),
        "source_scene_path": root_relative(scene_path),
        "source_receipt_path": root_relative(receipt_path),
        "source_fixture_path": root_relative(fixture_path),
        "render_verification": render_verification,
    }


def _review_root(root: Path = ROOT, review_root: Path | None = None) -> Path:
    root = Path(root).resolve(strict=True)
    candidate = root / REVIEW_RELATIVE if review_root is None else Path(review_root)
    _reject_redirected_path_chain(candidate)
    return candidate.absolute()


def _approved_review_roots(root: Path, review_root: Path | None) -> tuple[Path, ...]:
    root = Path(root).resolve(strict=True)
    candidates = ((Path(review_root),) if review_root is not None else
                  (root / REVIEW_RELATIVE, root / T7A4_REVIEW_RELATIVE))
    approved: list[Path] = []
    for candidate in candidates:
        _reject_redirected_path_chain(candidate)
        approved.append(candidate.absolute().resolve(strict=False))
    return tuple(approved)


def validate_output_target(
    root: Path,
    output: Path,
    *,
    review_root: Path | None = None,
) -> Path:
    """Require a new direct child of the T7a.3 review quarantine."""
    root = Path(root).resolve(strict=True)
    candidate = Path(output)
    if ".." in candidate.parts:
        raise ExchangeLayersError("unsafe output path")
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.absolute()
    _reject_redirected_path_chain(candidate)
    approved_roots = _approved_review_roots(root, review_root)
    target = candidate.resolve(strict=False)
    if target.parent not in approved_roots:
        raise ExchangeLayersError("output must be a direct child of an approved exchange-layer review quarantine")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ExchangeLayersError("output target must be new or an empty directory")
    return target


def _new_output_dir(path: Path) -> Path:
    path = Path(path)
    _reject_redirected_path_chain(path)
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExchangeLayersError(f"cannot create review output directory: {path}") from exc
    _reject_redirected_path_chain(path)
    if not path.is_dir():
        raise ExchangeLayersError("review output target is not a directory")
    return path.resolve(strict=True)


def _matrix_rows(matrix: Any) -> list[list[float]]:
    return [[float(value) for value in row] for row in matrix]


def _matrix_matches(actual: Sequence[Sequence[float]], expected: Sequence[Sequence[float]], tol: float = 1e-6) -> bool:
    if len(actual) != 4 or len(expected) != 4:
        return False
    return all(
        len(actual_row) == len(expected_row) == 4
        and all(math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol
                for a, b in zip(actual_row, expected_row))
        for actual_row, expected_row in zip(actual, expected)
    )


def _output_file_node(
    bpy: Any,
    tree: Any,
    directory: Path,
    *,
    item_type: str,
    item_name: str,
    file_format: str,
    color_mode: str,
    color_depth: str,
) -> Any:
    node = tree.nodes.new("CompositorNodeOutputFile")
    node.format.media_type = "IMAGE"
    node.format.file_format = file_format
    node.format.color_mode = color_mode
    node.format.color_depth = color_depth
    node.file_output_items.new(item_type, item_name)
    node.directory = str(directory)
    return node


def _setup_actor_pass_graph(
    bpy: Any,
    scene: Any,
    actor_meshes: Mapping[str, Sequence[Any]],
    output_root: Path,
) -> tuple[Any, dict[str, dict[str, Any]], dict[str, Any]]:
    view_layer = scene.view_layers[0]
    view_layer.use_pass_z = True
    view_layer.use_pass_cryptomatte_object = True
    view_layer.pass_cryptomatte_depth = 6
    view_layer.use_pass_cryptomatte_accurate = True
    view_layer.update_render_passes()

    tree = bpy.data.node_groups.new("T7a4 Visible Contribution Passes", "CompositorNodeTree")
    scene.compositing_node_group = tree
    scene.render.use_compositing = True
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    render_layers = tree.nodes.new("CompositorNodeRLayers")
    render_layers.scene = scene
    render_layers.layer = view_layer.name
    group_output = tree.nodes.new("NodeGroupOutput")
    tree.links.new(render_layers.outputs["Image"], group_output.inputs["Image"])
    required_outputs = {"Image", "Depth", "CryptoObject00"}
    output_names = {socket.name for socket in render_layers.outputs}
    if not required_outputs.issubset(output_names):
        raise ExchangeLayersError(
            f"Blender did not expose required EEVEE Cryptomatte/depth passes: {sorted(required_outputs - output_names)}"
        )
    crypto_layer = f"{view_layer.name}.CryptoObject"
    nodes: dict[str, dict[str, Any]] = {}
    for layer_key, config in FIGHTER_LAYERS.items():
        label = config["label"]
        binding = config["binding_id"]
        meshes = sorted(actor_meshes[binding], key=lambda obj: obj.name)
        matte_id = ",".join(obj.name for obj in meshes)
        rgba_dir = output_root / "passes" / layer_key / "rgba"
        matte_dir = output_root / "passes" / layer_key / "matte"
        depth_dir = output_root / "passes" / layer_key / "depth"
        for directory in (rgba_dir, matte_dir, depth_dir):
            directory.mkdir(parents=True, exist_ok=False)

        color_crypto = tree.nodes.new("CompositorNodeCryptomatteV2")
        color_crypto.scene = scene
        color_crypto.layer_name = crypto_layer
        color_crypto.matte_id = matte_id
        tree.links.new(render_layers.outputs["Image"], color_crypto.inputs["Image"])

        depth_crypto = tree.nodes.new("CompositorNodeCryptomatteV2")
        depth_crypto.scene = scene
        depth_crypto.layer_name = crypto_layer
        depth_crypto.matte_id = matte_id
        tree.links.new(render_layers.outputs["Depth"], depth_crypto.inputs["Image"])

        rgba_output = _output_file_node(
            bpy, tree, rgba_dir, item_type="RGBA", item_name="Image", file_format="PNG",
            color_mode="RGBA", color_depth="8",
        )
        tree.links.new(color_crypto.outputs["Image"], rgba_output.inputs["Image"])
        matte_output = _output_file_node(
            bpy, tree, matte_dir, item_type="FLOAT", item_name="Matte", file_format="PNG",
            color_mode="BW", color_depth="16",
        )
        tree.links.new(color_crypto.outputs["Matte"], matte_output.inputs["Matte"])
        depth_output = _output_file_node(
            bpy, tree, depth_dir, item_type="RGBA", item_name="Depth", file_format="OPEN_EXR",
            color_mode="RGBA", color_depth="32",
        )
        tree.links.new(depth_crypto.outputs["Image"], depth_output.inputs["Depth"])
        nodes[layer_key] = {
            "rgba": rgba_output,
            "matte": matte_output,
            "depth": depth_output,
            "matte_id": matte_id,
            "object_names": [obj.name for obj in meshes],
            "binding_id": binding,
            "label": label,
        }
    return tree, nodes, {
        "crypto_layer": crypto_layer,
        "cryptomatte_depth": int(view_layer.pass_cryptomatte_depth),
        "render_layer_outputs": sorted(output_names),
        "actor_mesh_counts": {key: len(actor_meshes[config["binding_id"]])
                               for key, config in FIGHTER_LAYERS.items()},
        "pass_types_per_actor": ["masked_rgba", "cryptomatte_matte", "cryptomatte_masked_depth"],
        "pass_count_per_actor": 3,
        "total_actor_pass_count": len(FIGHTER_LAYERS) * 3,
    }


def _validate_output_frames(output_frames: Sequence[int] | None) -> tuple[int, ...]:
    frames = tuple(range(FRAME_COUNT)) if output_frames is None else tuple(output_frames)
    if (not frames or any(isinstance(frame, bool) or not isinstance(frame, int) for frame in frames)
            or len(set(frames)) != len(frames) or any(frame < 0 or frame >= FRAME_COUNT for frame in frames)):
        raise ExchangeLayersError("output frame selection must be unique integer indices in 0..28")
    return frames


def _worker_render(
    root: Path,
    source_dir: Path,
    output: Path,
    output_frames: Sequence[int] | None = None,
) -> dict[str, Any]:
    import bpy  # type: ignore[import-not-found]

    root = Path(root).resolve(strict=True)
    source = validate_source_bundle(root, source_dir)
    scene_path: Path = source["scene_path"]
    receipt_path: Path = source["receipt_path"]
    if bpy.app.version_string != "5.2.2 LTS" or "--disable-autoexec" not in sys.argv:
        raise ExchangeLayersError("offline Blender 5.2.2 LTS with scripts disabled is required")
    try:
        reopened = fight_motion.reopen_exchange(bpy, scene_path, receipt_path)
    except fight_motion.FightMotionError as exc:
        raise ExchangeLayersError(f"saved source exchange scene failed Blender reopen: {exc}") from exc
    if (reopened.get("status") != "reopened_and_measured"
            or reopened.get("checked_frames") != list(range(36))
            or reopened.get("exposure_verified") is not True
            or reopened.get("render_verification") != "verified"):
        raise ExchangeLayersError("saved source exchange receipt did not reopen with verified 36-frame evidence")

    scene = bpy.context.scene
    camera = scene.camera
    source_camera = source["receipt"].get("camera", {})
    expected_camera_matrix = source_camera.get("matrix_world")
    if (camera is None or camera.name != "PhoneCamera" or camera.type != "CAMERA"
            or camera.data.type != "ORTHO" or abs(float(camera.data.ortho_scale) - 3.0) > 1e-8
            or not isinstance(expected_camera_matrix, list)
            or not _matrix_matches(_matrix_rows(camera.matrix_world), expected_camera_matrix)):
        raise ExchangeLayersError("source exchange camera differs from its fixed orthographic receipt")
    if (scene.render.fps != 30 or float(scene.render.fps_base) != 1.0
            or (scene.frame_start, scene.frame_end) != (0, 35)
            or scene.render.resolution_percentage != 100
            or (scene.render.resolution_x, scene.render.resolution_y) != (WIDTH, HEIGHT)):
        raise ExchangeLayersError("source exchange render clock or phone resolution differs")
    floor = bpy.data.objects.get("Exchange_Floor")
    if floor is None or floor.type != "MESH" or floor.hide_render:
        raise ExchangeLayersError("expected visible Exchange_Floor is missing")
    actor_objects = [obj for obj in scene.objects
                     if obj.get("model_binding_id") in {"attacker", "receiver"}]
    actor_meshes_by_binding = {
        binding: sorted(
            (obj for obj in actor_objects
             if obj.type == "MESH" and obj.get("model_binding_id") == binding),
            key=lambda obj: obj.name,
        )
        for binding in ("attacker", "receiver")
    }
    actor_meshes = [obj for values in actor_meshes_by_binding.values() for obj in values]
    if (not actor_meshes or any(not obj.data.vertices for obj in actor_meshes)
            or any(len(values) != 10 for values in actor_meshes_by_binding.values())):
        raise ExchangeLayersError("one or both privately bound fighter meshes are missing or empty")
    visible_meshes = sorted(
        obj.name for obj in actor_meshes if not obj.hide_render and obj.visible_get()
    )
    expected_bindings = {str(obj.get("model_binding_id")) for obj in actor_meshes}
    if expected_bindings != {"attacker", "receiver"} or len(visible_meshes) < 2:
        raise ExchangeLayersError("source exchange render does not contain both bound fighters")

    target = Path(output).resolve(strict=True)
    source_root = target / "source"
    if not source_root.is_dir() or source_root.is_symlink():
        raise ExchangeLayersError("preflighted combined-source output directory is missing or redirected")
    selected_output_frames = _validate_output_frames(output_frames)
    floor.hide_render = True  # In-memory render state only; the source blend is never saved.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100
    _, pass_nodes, pass_contract = _setup_actor_pass_graph(bpy, scene, actor_meshes_by_binding, target)

    frame_rows: dict[str, Any] = {}
    for output_frame in selected_output_frames:
        source_frame = source_frame_for_output(output_frame)
        scene.frame_set(source_frame)
        if scene.frame_current != source_frame:
            raise ExchangeLayersError(f"Blender did not evaluate source frame {source_frame}")
        if not _matrix_matches(_matrix_rows(scene.camera.matrix_world), expected_camera_matrix):
            raise ExchangeLayersError(f"source camera moved at source frame {source_frame}")
        current_visible = sorted(
            obj.name for obj in actor_meshes if not obj.hide_render and obj.visible_get()
        )
        if current_visible != visible_meshes:
            raise ExchangeLayersError(f"visible fighter mesh set changed at source frame {source_frame}")
        for nodes in pass_nodes.values():
            for kind, node in nodes.items():
                if kind in {"rgba", "matte", "depth"}:
                    node.file_name = f"frame-{output_frame:03d}-"
        destination = source_root / f"frame-{output_frame:03d}.png"
        scene.render.filepath = str(destination)
        bpy.ops.render.render(write_still=True)
        if not destination.is_file() or destination.stat().st_size > MAX_OUTPUT_BYTES:
            raise ExchangeLayersError(f"Blender did not produce a bounded motion PNG for output frame {output_frame}")
        header = destination.read_bytes()[:24]
        if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n"
                or header[12:16] != b"IHDR"
                or int.from_bytes(header[16:20], "big") != WIDTH
                or int.from_bytes(header[20:24], "big") != HEIGHT):
            raise ExchangeLayersError(f"Blender produced an invalid phone-sized PNG at output frame {output_frame}")
        actor_passes: dict[str, dict[str, dict[str, Any]]] = {}
        for layer_key in FIGHTER_LAYERS:
            actor_passes[layer_key] = {}
            for kind, suffix in (("rgba", "Image.png"), ("matte", "Matte.png"), ("depth", "Depth.exr")):
                pass_path = target / "passes" / layer_key / kind / f"frame-{output_frame:03d}-{suffix}"
                if (not pass_path.is_file() or pass_path.is_symlink()
                        or pass_path.stat().st_size > MAX_OUTPUT_BYTES):
                    raise ExchangeLayersError(
                        f"Blender did not produce a bounded {layer_key} {kind} pass at output frame {output_frame}"
                    )
                pass_header = pass_path.read_bytes()[:32]
                if kind in {"rgba", "matte"}:
                    if (len(pass_header) < 24 or pass_header[:8] != b"\x89PNG\r\n\x1a\n"
                            or int.from_bytes(pass_header[16:20], "big") != WIDTH
                            or int.from_bytes(pass_header[20:24], "big") != HEIGHT):
                        raise ExchangeLayersError(
                            f"Blender produced an invalid {layer_key} PNG pass at output frame {output_frame}"
                        )
                elif not pass_header.startswith(b"v/1\x01"):
                    raise ExchangeLayersError(
                        f"Blender produced an invalid {layer_key} EXR depth pass at output frame {output_frame}"
                    )
                pass_kind = {"rgba": "rgba_pass", "matte": "matte_pass", "depth": "depth_pass"}[kind]
                actor_passes[layer_key][pass_kind] = {
                    "path": pass_path.relative_to(target).as_posix(),
                    "sha256": sha256(pass_path),
                    "bytes": pass_path.stat().st_size,
                }
        frame_rows[str(output_frame)] = {
            "output_frame": output_frame,
            "source_frame": source_frame,
            "path": destination.relative_to(target).as_posix(),
            "sha256": sha256(destination),
            "bytes": destination.stat().st_size,
            "actor_passes": actor_passes,
            "render_state": {
                "blender_version": bpy.app.version_string,
                "blender_build_hash": bpy.app.build_hash.decode("ascii"),
                "embedded_scripts": "disabled",
                "online_mode": "offline",
                "scene_frame_current": scene.frame_current,
                "render_engine": scene.render.engine,
                "camera": camera.name,
                "camera_projection": camera.data.type,
                "camera_ortho_scale": float(camera.data.ortho_scale),
                "camera_matrix_world": _matrix_rows(camera.matrix_world),
                "resolution_px": [scene.render.resolution_x, scene.render.resolution_y],
                "film_transparent": bool(scene.render.film_transparent),
                "color_mode": scene.render.image_settings.color_mode,
                "floor_hidden_in_working_process": bool(floor.hide_render),
                "visible_fighter_meshes": current_visible,
                "cryptomatte_object_pass": True,
                "cryptomatte_depth": pass_contract["cryptomatte_depth"],
                "actor_mesh_counts": pass_contract["actor_mesh_counts"],
                "source_over_order_back_to_front": OCCLUSION_CONTRACT["source_over_order_back_to_front"],
            },
        }

    if sha256(scene_path) != source["scene_sha256"]:
        raise ExchangeLayersError("source exchange blend changed during the read-only raster pass")
    return {
        "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode("ascii"),
        "embedded_scripts": "disabled",
        "online_mode": "offline",
        "saved_scene_reopen": reopened,
        "source_scene_sha256_before": source["scene_sha256"],
        "source_scene_sha256_after": sha256(scene_path),
        "source_receipt_sha256": source["receipt_sha256"],
        "camera": {
            "name": camera.name,
            "projection": camera.data.type,
            "orthographic_scale_m": float(camera.data.ortho_scale),
            "resolution_px": [WIDTH, HEIGHT],
            "matrix_world": _matrix_rows(camera.matrix_world),
        },
        "render_engine": scene.render.engine,
        "floor_hidden_in_working_process": bool(floor.hide_render),
        "visible_fighter_meshes": visible_meshes,
        "actor_pass_contract": pass_contract,
        "output_frame_indices": list(selected_output_frames),
        "frame_count": len(frame_rows),
        "frames": frame_rows,
    }


def _blender_entry() -> None:
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 7 or args[0] != "--worker":
        raise ExchangeLayersError(
            "expected Blender worker arguments: --worker ROOT SOURCE_BUNDLE OUTPUT REPORT MODE FRAME_INDICES"
        )
    _, root_raw, source_raw, output_raw, report_raw, mode, frames_raw = args
    if mode != "render":
        raise ExchangeLayersError("unsupported Blender worker mode")
    try:
        output_frames = tuple(int(value) for value in frames_raw.split(","))
    except ValueError as exc:
        raise ExchangeLayersError("Blender worker frame selection is malformed") from exc
    report = _worker_render(Path(root_raw), Path(source_raw), Path(output_raw), output_frames)
    report_path = Path(report_raw)
    _reject_redirected_path_chain(report_path)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("MODEL_EXCHANGE_LAYERS_WORKER=" + json.dumps({
        "status": "rendered",
        "frame_count": report["frame_count"],
        "output_frame_indices": report["output_frame_indices"],
        "source_scene_sha256": report["source_scene_sha256_after"],
        "report": str(report_path),
    }, sort_keys=True))


def _run_blender_worker(
    root: Path,
    source_dir: Path,
    output: Path,
    *,
    blender: Path = BLENDER,
    output_frames: Sequence[int] | None = None,
) -> dict[str, Any]:
    selected_output_frames = _validate_output_frames(output_frames)
    if not Path(blender).is_file():
        raise ExchangeLayersError(f"pinned Blender executable is missing: {blender}")
    report_path = output / "blender-state.json"
    command = [
        str(blender), "--background", "--offline-mode", "--disable-autoexec",
        str(source_dir / "source-exchange.blend"), "--python", str(Path(__file__).resolve()), "--",
        "--worker", str(root.resolve()), str(source_dir.resolve()), str(output.resolve()), str(report_path.resolve()),
        "render", ",".join(str(frame) for frame in selected_output_frames),
    ]
    done = subprocess.run(
        command,
        cwd=root,
        env={**os.environ,
             "BLENDER_USER_CONFIG": str(output / "blender-config"),
             "BLENDER_USER_SCRIPTS": str(output / "blender-scripts")},
        capture_output=True,
        text=True,
        timeout=1800,
        check=False,
    )
    (output / "blender-stdout.txt").write_text(done.stdout, encoding="utf-8")
    (output / "blender-stderr.txt").write_text(done.stderr, encoding="utf-8")
    if (done.returncode != 0 or not report_path.is_file()
            or "Traceback (most recent call last)" in done.stdout + done.stderr):
        raise ExchangeLayersError(
            f"offline Blender sequence render failed ({done.returncode}); preserve and inspect "
            f"{output / 'blender-stderr.txt'}"
        )
    report = _read_json(report_path, "Blender sequence state report")
    if (report.get("output_frame_indices") != list(selected_output_frames)
            or report.get("frame_count") != len(selected_output_frames)
            or set(report.get("frames", {})) != {str(frame) for frame in selected_output_frames}):
        raise ExchangeLayersError("Blender worker output frame set differs from the requested sequence")
    return report


def _alpha_bounds(image: Image.Image) -> tuple[int, int, list[int] | None]:
    _ensure_host_dependencies()
    alpha = image.convert("RGBA").getchannel("A")
    low, high = alpha.getextrema()
    bounds = alpha.getbbox()
    return low, high, list(bounds) if bounds else None


def _verify_png(
    path: Path,
    *,
    expected_mode: str,
    expected_size: tuple[int, int] = (WIDTH, HEIGHT),
    max_bytes: int = MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    _ensure_host_dependencies()
    if path.is_symlink() or not path.is_file():
        raise ExchangeLayersError(f"required PNG is missing or redirected: {path.name}")
    size = path.stat().st_size
    if size <= 0 or size > max_bytes:
        raise ExchangeLayersError(f"PNG byte size is outside its bound: {path.name}")
    try:
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != expected_size or image.mode != expected_mode:
                raise ExchangeLayersError(
                    f"PNG {path.name} must be {expected_mode} {expected_size[0]}x{expected_size[1]}"
                )
            image.load()
            result: dict[str, Any] = {
                "width_px": image.width,
                "height_px": image.height,
                "mode": image.mode,
                "bytes": size,
                "sha256": sha256(path),
            }
            if expected_mode == "RGBA":
                alpha_min, alpha_max, bounds = _alpha_bounds(image)
                if alpha_min == 255 or alpha_max == 0 or bounds is None:
                    raise ExchangeLayersError(f"transparent fighter PNG has invalid alpha coverage: {path.name}")
                result.update({"alpha_min": alpha_min, "alpha_max": alpha_max, "alpha_bounds_px": bounds})
            return result
    except ExchangeLayersError:
        raise
    except (Image.DecompressionBombError, OSError, ValueError) as exc:
        raise ExchangeLayersError(f"PNG cannot be decoded safely: {path.name}: {exc}") from exc


def _read_cryptomatte_mask(path: Path) -> tuple[Any, dict[str, Any]]:
    _ensure_host_dependencies()
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_OUTPUT_BYTES:
        raise ExchangeLayersError(f"Cryptomatte mask is missing, redirected, or oversized: {path.name}")
    try:
        with Image.open(path) as image:
            if image.format != "PNG" or image.size != (WIDTH, HEIGHT):
                raise ExchangeLayersError(f"Cryptomatte mask must be a {WIDTH}x{HEIGHT} PNG: {path.name}")
            if image.mode not in {"L", "I", "I;16", "I;16L", "I;16B"}:
                raise ExchangeLayersError(f"Cryptomatte mask has unsupported precision: {image.mode}")
            image.load()
            values = np.asarray(image)
            if np.any(values < 0):
                raise ExchangeLayersError(f"Cryptomatte mask contains negative values: {path.name}")
            scale = 65535.0 if image.mode.startswith("I;16") or values.dtype == np.uint16 else 255.0
            if image.mode == "I":
                scale = 65535.0 if int(values.max(initial=0)) > 255 else 255.0
            if float(values.max(initial=0)) > scale:
                raise ExchangeLayersError(f"Cryptomatte mask exceeds its encoded range: {path.name}")
            info = {
                "path": path.as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "width_px": image.width,
                "height_px": image.height,
                "mode": image.mode,
                "precision_bits": 16 if scale == 65535.0 else 8,
            }
            return values.astype(np.float64) / scale, info
    except ExchangeLayersError:
        raise
    except (Image.DecompressionBombError, OSError, TypeError, ValueError) as exc:
        raise ExchangeLayersError(f"Cryptomatte mask cannot be decoded safely: {path.name}: {exc}") from exc


def _verify_depth_exr(path: Path) -> dict[str, Any]:
    """Check bounded OpenEXR structure and its camera-sized RGBA depth channels."""
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ExchangeLayersError(f"actor depth plane is missing or redirected: {path.name}")
    size = path.stat().st_size
    if size <= 0 or size > MAX_OUTPUT_BYTES:
        raise ExchangeLayersError(f"actor depth plane byte size is outside its bound: {path.name}")

    def cstring(stream) -> bytes:
        value = bytearray()
        while len(value) <= 128:
            char = stream.read(1)
            if not char:
                raise ExchangeLayersError(f"OpenEXR header is truncated: {path.name}")
            if char == b"\x00":
                return bytes(value)
            value.extend(char)
        raise ExchangeLayersError(f"OpenEXR header string exceeds its bound: {path.name}")

    attributes: dict[bytes, tuple[bytes, bytes]] = {}
    try:
        with path.open("rb") as stream:
            if stream.read(4) != b"v/1\x01":
                raise ExchangeLayersError(f"actor depth plane is not OpenEXR: {path.name}")
            version = stream.read(4)
            if len(version) != 4:
                raise ExchangeLayersError(f"OpenEXR version header is truncated: {path.name}")
            while True:
                name = cstring(stream)
                if not name:
                    break
                kind = cstring(stream)
                size_bytes = stream.read(4)
                if len(size_bytes) != 4:
                    raise ExchangeLayersError(f"OpenEXR attribute size is truncated: {path.name}")
                payload_size = int.from_bytes(size_bytes, "little")
                if payload_size > 1_048_576:
                    raise ExchangeLayersError(f"OpenEXR attribute exceeds its bound: {path.name}")
                payload = stream.read(payload_size)
                if len(payload) != payload_size:
                    raise ExchangeLayersError(f"OpenEXR attribute is truncated: {path.name}")
                attributes[name] = (kind, payload)
    except OSError as exc:
        raise ExchangeLayersError(f"actor depth plane cannot be read: {path.name}: {exc}") from exc

    for name in (b"dataWindow", b"displayWindow"):
        kind, payload = attributes.get(name, (b"", b""))
        if kind != b"box2i" or len(payload) != 16:
            raise ExchangeLayersError(f"OpenEXR {name.decode()} is missing or malformed: {path.name}")
        coords = [int.from_bytes(payload[index:index + 4], "little", signed=True) for index in range(0, 16, 4)]
        if coords != [0, 0, WIDTH - 1, HEIGHT - 1]:
            raise ExchangeLayersError(f"OpenEXR depth window is not {WIDTH}x{HEIGHT}: {path.name}")
    channel_kind, channel_payload = attributes.get(b"channels", (b"", b""))
    if channel_kind != b"chlist":
        raise ExchangeLayersError(f"OpenEXR channel list is missing: {path.name}")
    channels: list[str] = []
    offset = 0
    while offset < len(channel_payload):
        end = channel_payload.find(b"\x00", offset)
        if end < 0:
            raise ExchangeLayersError(f"OpenEXR channel name is malformed: {path.name}")
        name = channel_payload[offset:end]
        offset = end + 1
        if not name:
            break
        if offset + 16 > len(channel_payload):
            raise ExchangeLayersError(f"OpenEXR channel definition is truncated: {path.name}")
        channels.append(name.decode("ascii", errors="strict"))
        offset += 16
    if not {"R", "G", "B", "A"}.issubset(channels):
        raise ExchangeLayersError(f"OpenEXR masked depth needs RGBA channels: {path.name}")
    return {
        "path": path.as_posix(),
        "sha256": sha256(path),
        "bytes": size,
        "format": "OpenEXR",
        "width_px": WIDTH,
        "height_px": HEIGHT,
        "channels": sorted(channels),
        "semantics": "EEVEE camera-space depth masked by the actor Cryptomatte matte",
    }


def _normalize_visible_coverage(source_alpha8: Any, matte_a: Any, matte_b: Any) -> tuple[Any, Any, dict[str, Any]]:
    """Convert Cryptomatte sample ownership into byte-exact ordered over-alpha."""
    _ensure_host_dependencies()
    source_alpha = np.asarray(source_alpha8, dtype=np.uint8)
    alpha_float = source_alpha.astype(np.float64) / 255.0
    actor_a = np.asarray(matte_a, dtype=np.float64)
    actor_b = np.asarray(matte_b, dtype=np.float64)
    if source_alpha.shape != actor_a.shape or source_alpha.shape != actor_b.shape:
        raise ExchangeLayersError("source alpha and Cryptomatte mattes have different dimensions")
    if (not np.isfinite(actor_a).all() or not np.isfinite(actor_b).all()
            or np.any(actor_a < 0) or np.any(actor_b < 0)
            or np.any(actor_a > 1) or np.any(actor_b > 1)):
        raise ExchangeLayersError("Cryptomatte mattes contain non-finite or out-of-range coverage")
    matte_sum = actor_a + actor_b
    support = matte_sum > 1e-12
    coverage_a = np.divide(alpha_float * actor_a, matte_sum, out=np.zeros_like(alpha_float), where=support)
    coverage_b = np.divide(alpha_float * actor_b, matte_sum, out=np.zeros_like(alpha_float), where=support)
    coverage_error = coverage_a + coverage_b - alpha_float
    tolerance = 2.0 / 255.0
    unassigned = (coverage_error > tolerance).sum()
    duplicate = (coverage_error < -tolerance).sum()
    if unassigned or duplicate:
        raise ExchangeLayersError(
            f"Cryptomatte split leaves unassigned/duplicate visible pixels ({unassigned}/{duplicate})"
        )

    alpha_a8 = np.rint(coverage_a * 255.0).clip(0, 255).astype(np.uint8)
    denominator = 255 - alpha_a8.astype(np.int32)
    numerator = (source_alpha.astype(np.int32) - alpha_a8.astype(np.int32)).clip(0) * 255
    alpha_b_float = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(alpha_float),
        where=denominator > 0,
    )
    alpha_b8 = np.rint(alpha_b_float).clip(0, 255).astype(np.uint8)
    return alpha_a8, alpha_b8, {
        "normalized_coverage_sum_max_error_8bit": round(float(np.abs(coverage_error).max(initial=0)) * 255, 6),
        "normalized_coverage_sum_mean_error_8bit": round(float(np.abs(coverage_error).mean()) * 255, 6),
        "unassigned_coverage_pixel_count_over_2_255": int(unassigned),
        "duplicate_coverage_pixel_count_over_2_255": int(duplicate),
        "raw_fractional_matte_overlap_pixel_count": int(
            ((np.minimum(actor_a, actor_b) > (1.0 / 255.0)) & (source_alpha > 0)).sum()
        ),
        "raw_matte_sum_minus_source_alpha_max_8bit": round(
            float(np.abs(matte_sum - alpha_float).max(initial=0)) * 255, 6
        ),
        "raw_matte_sum_minus_source_alpha_mean_8bit": round(
            float(np.abs(matte_sum - alpha_float).mean()) * 255, 6
        ),
        "source_coverage_pixel_count": int((source_alpha > 1).sum()),
    }


def _recomposition_metrics(rebuilt_rgba: Any, source_rgba: Any, normalization: Mapping[str, Any]) -> dict[str, Any]:
    _ensure_host_dependencies()
    rebuilt = np.asarray(rebuilt_rgba, dtype=np.uint8)
    source = np.asarray(source_rgba, dtype=np.uint8)
    if rebuilt.shape != source.shape or rebuilt.ndim != 3 or rebuilt.shape[2] != 4:
        raise ExchangeLayersError("recomposition images have incompatible dimensions")
    rgb_error = np.abs(rebuilt[..., :3].astype(np.int16) - source[..., :3].astype(np.int16))
    alpha_error = np.abs(rebuilt[..., 3].astype(np.int16) - source[..., 3].astype(np.int16))
    visible = source[..., 3] > 1
    edge = (source[..., 3] > 0) & (source[..., 3] < 255)
    visible_rgb = rgb_error[visible]
    metrics = {
        **dict(normalization),
        "status": "measured",
        "alpha_max_error_8bit": int(alpha_error.max(initial=0)),
        "alpha_mean_error_8bit": round(float(alpha_error.mean()), 6),
        "visible_rgb_max_channel_error_8bit": int(visible_rgb.max(initial=0)) if visible_rgb.size else 0,
        "visible_rgb_mean_channel_error_8bit": round(float(visible_rgb.mean()), 6) if visible_rgb.size else 0.0,
        "edge_pixel_count": int(edge.sum()),
        "visible_source_pixel_count": int(visible.sum()),
    }
    if (metrics["alpha_max_error_8bit"] > RECOMPOSITION_LIMITS["transparent_alpha_max_error_8bit"]
            or metrics["visible_rgb_max_channel_error_8bit"] >
            RECOMPOSITION_LIMITS["transparent_visible_rgb_max_channel_error_8bit"]):
        raise ExchangeLayersError(
            "fighter planes do not meet source-view alpha/RGB tolerances "
            f"(alpha={metrics['alpha_max_error_8bit']}, rgb={metrics['visible_rgb_max_channel_error_8bit']})"
        )
    return metrics


def _render_layered_actor_rgba(document: Mapping[str, Any], frame: int, asset_root: Path) -> Any:
    """Reuse LayeredScene's own raster/project path while retaining the actor-only alpha result."""
    _ensure_host_dependencies()

    actor_document = copy.deepcopy(dict(document))
    actor_document["clear_color"] = "#00000000"
    actor_document["layers"] = [layer for layer in actor_document["layers"] if layer["kind"] == "character"]
    scene = LayeredScene(actor_document, asset_root=asset_root)
    output, _ = scene._render_rgba_frame(frame, supersample=1)
    return np.asarray(output, dtype=np.uint8).copy()


def _layered_rgb_metrics(
    rebuilt_rgb: Any,
    source_rgb: Any,
    rebuilt_actor_rgba: Any,
    source_actor_rgba: Any,
) -> dict[str, Any]:
    _ensure_host_dependencies()
    rebuilt = np.asarray(rebuilt_rgb.convert("RGB"), dtype=np.uint8)
    source = np.asarray(source_rgb.convert("RGB"), dtype=np.uint8)
    if rebuilt.shape != source.shape:
        raise ExchangeLayersError("LayeredScene and source-reference renders have different dimensions")
    error = np.abs(rebuilt.astype(np.int16) - source.astype(np.int16))
    pixel_error = error.max(axis=2)
    rebuilt_rgba = np.asarray(rebuilt_actor_rgba, dtype=np.uint8)
    source_rgba = np.asarray(source_actor_rgba, dtype=np.uint8)
    if rebuilt_rgba.shape != source_rgba.shape or rebuilt_rgba.shape[:2] != error.shape[:2]:
        raise ExchangeLayersError("LayeredScene actor-only alpha rasters have incompatible dimensions")
    alpha_error = np.abs(rebuilt_rgba[..., 3].astype(np.int16) - source_rgba[..., 3].astype(np.int16))
    edge = (source_rgba[..., 3] > 0) & (source_rgba[..., 3] < 255)
    edge_image = Image.fromarray(edge.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(5))
    edge_region = np.asarray(edge_image) > 0
    metrics = {
        "status": "measured",
        "max_channel_error_8bit": int(error.max(initial=0)),
        "mean_channel_error_8bit": round(float(error.mean()), 8),
        "affected_pixel_count_over_1": int((pixel_error > 1).sum()),
        "edge_region_pixel_count": int(edge_region.sum()),
        "edge_region_affected_pixel_count_over_1": int(((pixel_error > 1) & edge_region).sum()),
        "actor_alpha_max_error_8bit": int(alpha_error.max(initial=0)),
        "actor_alpha_mean_error_8bit": round(float(alpha_error.mean()), 8),
        "actor_alpha_affected_pixel_count": int((alpha_error > 0).sum()),
        "pixel_count": int(error.shape[0] * error.shape[1]),
    }
    if (metrics["max_channel_error_8bit"] > RECOMPOSITION_LIMITS["layered_scene_max_channel_error_8bit"]
            or metrics["mean_channel_error_8bit"] > RECOMPOSITION_LIMITS["layered_scene_mean_channel_error_max"]
            or metrics["actor_alpha_max_error_8bit"] > RECOMPOSITION_LIMITS["layered_scene_actor_alpha_max_error_8bit"]):
        raise ExchangeLayersError(
            "equal-depth fighter planes exceed the declared LayeredScene resampling envelope "
            f"(RGB max/mean={metrics['max_channel_error_8bit']}/{metrics['mean_channel_error_8bit']}, "
            f"actor alpha max={metrics['actor_alpha_max_error_8bit']}/255)"
        )
    return metrics


def _event_ids(source_frame: int) -> list[str]:
    return list(EVENT_MAP.get(source_frame, ()))


def _background_plane(width: int, height: int) -> dict[str, Any]:
    bleed = BACKGROUND_BLEED_PX
    bounds = [-bleed, -bleed, width + bleed, height + bleed]
    horizon = round(height * 0.66)
    return {
        "layer_id": "static-source-exchange-background",
        "kind": "environment",
        "role": "background",
        "depth": 0.0,
        "anchor_px": [0, 0],
        "source_bounds_px": bounds,
        "painted_bounds_px": bounds,
        "shapes": [
            {"kind": "rect", "bounds_px": bounds, "fill": "#1b222c"},
            {"kind": "polygon", "points_px": [
                [-bleed, horizon], [width + bleed, horizon],
                [width + bleed, height + bleed], [-bleed, height + bleed],
            ], "fill": "#3b4149"},
        ],
    }


def _character_layer(config: Mapping[str, Any], raster_asset: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "layer_id": config["layer_id"],
        "kind": "character",
        "binding_id": config["binding_id"],
        "role": "subject",
        "depth": config["depth"],
        "anchor_px": [WIDTH / 2, HEIGHT / 2],
        "source_bounds_px": [0, 0, WIDTH, HEIGHT],
        "silhouette_bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
        "disocclusion_budget_px": MAX_DISOCCLUSION_PX,
        "pose_channel": config["pose_channel"],
        "expression_channel": config["expression_channel"],
        "shapes": [],
        "pose_states": [{
            "state_id": "source-frame-00",
            "index": 0,
            "shapes": [],
            "raster_asset": {
                "path": raster_asset["path"],
                "sha256": raster_asset["sha256"],
                "bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
            },
        }],
        "expression_states": [{"state_id": "fixed-source-expression", "index": 0, "shapes": []}],
    }


def _motion_channels(configs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    channels = []
    for config in configs:
        channels.extend((
            {"channel_id": config["pose_channel"], "binding_id": config["binding_id"],
             "target_kind": "articulation", "semantic_target": "mapped_source_frame",
             "value_unit": "normalized", "interpolation": "step",
             "keyframes": [{"frame": 0, "value": 0}]},
            {"channel_id": config["expression_channel"], "binding_id": config["binding_id"],
             "target_kind": "face_control", "semantic_target": "source_expression",
             "value_unit": "normalized", "interpolation": "step",
             "keyframes": [{"frame": 0, "value": 0}]},
        ))
    return channels


def _scene_document(first_plane_assets: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    layers = [_background_plane(WIDTH, HEIGHT)]
    order = OCCLUSION_CONTRACT["source_over_order_back_to_front"]
    for layer_key in order:
        if layer_key not in FIGHTER_LAYERS or layer_key not in first_plane_assets:
            raise ExchangeLayersError("first frame is missing one of the two fighter plane assets")
        layers.append(_character_layer(FIGHTER_LAYERS[layer_key], first_plane_assets[layer_key]))
    return {
        "schema_version": "authored_layer_scene.v1",
        "scene_id": "generic-source-exchange-24fps-diagnostic",
        "review_state": "review_only",
        "render_eligible": False,
        "diagnostic_only": True,
        "art_note": DIAGNOSTIC_NOTE,
        "canvas_px": [WIDTH, HEIGHT],
        "clear_color": "#1b222c",
        "view_envelope_deg": {"yaw_deg": [0, 0], "pitch_deg": [0, 0]},
        "occlusion_policy": "declared_depth_back_to_front",
        "camera": {"zoom_limits": list(CAMERA_ZOOM_LIMITS), "keyframes": [
            {**key, "ease": "smoothstep"} for key in CAMERA_KEYFRAMES
        ]},
        "scene": {
            "scene_id": "generic-source-exchange-24fps-diagnostic",
            "duration_frames": FRAME_COUNT,
            "fps": {"numerator": FPS, "denominator": 1},
            "time_origin": {"scene_time_seconds": {"numerator": 0, "denominator": 1}},
            "events": [],
            "contacts": [],
            "motion_channels": _motion_channels([FIGHTER_LAYERS[key] for key in FIGHTER_LAYERS]),
        },
        "layers": layers,
        "projection_groups": [{
            "layer_ids": [FIGHTER_LAYERS[key]["layer_id"]
                          for key in OCCLUSION_CONTRACT["projection_group"]["layer_keys_back_to_front"]],
            "mode": OCCLUSION_CONTRACT["projection_group"]["mode"],
        }],
    }


def _source_reference_document(
    document: Mapping[str, Any], source_asset: Mapping[str, Any],
) -> dict[str, Any]:
    reference = copy.deepcopy(dict(document))
    reference.pop("projection_groups", None)
    template = next(layer for layer in reference["layers"] if layer["kind"] == "character")
    config = {
        "layer_id": "combined-source-reference",
        "binding_id": "source_reference",
        "pose_channel": "source-reference-pose",
        "expression_channel": "source-reference-expression",
        "depth": 1.0,
    }
    reference["layers"] = [reference["layers"][0], _character_layer(config, source_asset)]
    reference["scene"]["motion_channels"] = _motion_channels([config])
    return reference


class ExchangeLayerSequence:
    """Per-seek adapter that independently selects both fighter planes in LayeredScene."""

    def __init__(
        self,
        document: Mapping[str, Any],
        frame_rows: Sequence[Mapping[str, Any]],
        *,
        asset_root: Path,
    ):
        indexed_rows = {int(row["output_frame"]): dict(row) for row in frame_rows}
        if (not indexed_rows or len(indexed_rows) != len(frame_rows)
                or any(frame not in range(FRAME_COUNT) for frame in indexed_rows)):
            raise ExchangeLayersError("LayeredScene adapter needs unique source frame rows in 0..28")
        self.document = copy.deepcopy(dict(document))
        self.frame_rows = indexed_rows
        self.asset_root = Path(asset_root).resolve(strict=True)
        self._layers = {
            layer_key: next((layer for layer in self.document.get("layers", [])
                             if layer.get("layer_id") == config["layer_id"]), None)
            for layer_key, config in FIGHTER_LAYERS.items()
        }
        if any(not isinstance(layer, dict) or len(layer.get("pose_states", [])) != 1
               for layer in self._layers.values()):
            raise ExchangeLayersError("per-seek adapter requires one bounded raster state per fighter")

    def render(self, output_frame: int, *, supersample: int = 1):
        _ensure_host_dependencies()
        source_frame = source_frame_for_output(output_frame)
        row = self.frame_rows.get(output_frame)
        if row is None:
            raise ExchangeLayersError(f"per-seek sequence has no output frame {output_frame}")
        if row.get("output_frame") != output_frame or row.get("source_frame") != source_frame:
            raise ExchangeLayersError("per-seek source mapping differs from the exact 24 fps rule")
        document = copy.deepcopy(self.document)
        expected_state = f"source-frame-{source_frame:02d}"
        for layer_key, config in FIGHTER_LAYERS.items():
            plane = row.get("fighter_planes", {}).get(layer_key, {}).get("image")
            if not isinstance(plane, Mapping):
                raise ExchangeLayersError(f"output frame {output_frame} lacks the {layer_key} plane asset")
            layer = next(item for item in document["layers"] if item["layer_id"] == config["layer_id"])
            pose = layer["pose_states"][0]
            pose["state_id"] = expected_state
            pose["raster_asset"] = {
                "path": plane["path"],
                "sha256": plane["sha256"],
                "bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
            }
        try:
            scene = LayeredScene(document, asset_root=self.asset_root)
            state = scene.evaluate(output_frame)
            if (any(state.selected_states.get(config["layer_id"], {}).get("pose") != expected_state
                    for config in FIGHTER_LAYERS.values()) or state.events or state.contacts):
                raise ExchangeLayersError("LayeredScene selected a wrong source frame or declared a new event/contact")
            return scene.render(output_frame, supersample=supersample)
        except LayeredSceneError as exc:
            raise ExchangeLayersError(f"LayeredScene rejected output frame {output_frame}: {exc}") from exc

    def render_source_reference(self, output_frame: int, *, supersample: int = 1):
        _ensure_host_dependencies()
        source_frame = source_frame_for_output(output_frame)
        row = self.frame_rows.get(output_frame)
        if row is None or row.get("source_frame") != source_frame:
            raise ExchangeLayersError("source-reference adapter has an invalid output/source frame mapping")
        source_asset = row.get("source_render")
        if not isinstance(source_asset, Mapping):
            raise ExchangeLayersError(f"output frame {output_frame} lacks its combined source reference")
        document = _source_reference_document(self.document, source_asset)
        layer = next(item for item in document["layers"] if item["layer_id"] == "combined-source-reference")
        layer["pose_states"][0]["state_id"] = f"source-frame-{source_frame:02d}"
        try:
            scene = LayeredScene(document, asset_root=self.asset_root)
            state = scene.evaluate(output_frame)
            if (state.selected_states.get("combined-source-reference", {}).get("pose")
                    != f"source-frame-{source_frame:02d}" or state.events or state.contacts):
                raise ExchangeLayersError("LayeredScene selected a wrong combined-source reference frame")
            return scene.render(output_frame, supersample=supersample)
        except LayeredSceneError as exc:
            raise ExchangeLayersError(f"LayeredScene rejected source-reference frame {output_frame}: {exc}") from exc


def _seek_order() -> list[int]:
    # 17 and 29 are coprime, so this visits every frame exactly once out of order.
    return [(index * 17) % FRAME_COUNT for index in range(FRAME_COUNT)]


def _save_preview(composite_paths: Sequence[Path], destination: Path) -> dict[str, Any]:
    _ensure_host_dependencies()
    frames: list[Image.Image] = []
    for path in composite_paths:
        with Image.open(path) as source:
            image = source.convert("RGB")
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.rectangle((0, 0, WIDTH, 36), fill=(12, 17, 24, 215))
        draw.text((9, 10), PREVIEW_LABEL, font=ImageFont.load_default(), fill=(255, 255, 255, 255))
        frames.append(Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB"))
    if len(frames) != FRAME_COUNT:
        raise ExchangeLayersError("phone sequence preview needs all 29 composite frames")
    frames[0].save(
        destination,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=42,
        loop=0,
        disposal=2,
        optimize=False,
    )
    del frames
    try:
        with Image.open(destination) as preview:
            count = int(getattr(preview, "n_frames", 1))
            size = preview.size
            if preview.format != "GIF" or size != (WIDTH, HEIGHT) or count != FRAME_COUNT:
                raise ExchangeLayersError("phone-sized diagnostic preview dimensions or frame count differ")
    except (Image.DecompressionBombError, OSError, ValueError) as exc:
        raise ExchangeLayersError(f"phone-sized preview cannot be decoded: {exc}") from exc
    return {
        "path": destination.name,
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
        "width_px": WIDTH,
        "height_px": HEIGHT,
        "format": "GIF",
        "frame_count": FRAME_COUNT,
        "frame_delay_ms": 42,
        "label": PREVIEW_LABEL,
        "preview_timing_note": "Visual review preview only; authoritative timing is the receipt's exact 24 fps frame map.",
    }


def _save_contact_sheet(
    output: Path,
    composite_paths: Mapping[int, Path],
    frame_rows: Sequence[Mapping[str, Any]],
    destination: Path,
) -> dict[str, Any]:
    _ensure_host_dependencies()
    by_frame = {int(row["output_frame"]): row for row in frame_rows}
    frame_ids = sorted(composite_paths)
    if not frame_ids or set(frame_ids) != set(by_frame):
        raise ExchangeLayersError("contact sheet inputs need one composite for every selected frame")
    columns = 4
    cell_width, cell_height, header = 270, 480, 28
    rows = math.ceil(len(frame_ids) / columns)
    title_height = 48
    sheet = Image.new("RGB", (columns * cell_width, title_height + rows * (cell_height + header)), "#10151f")
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 5), "FIGHTER PLANES — REVIEW-ONLY FIXED-SOURCE-VIEW CONTRIBUTIONS", fill="white")
    draw.text((8, 23), "Actor planes share one source/world grid and camera projection; hidden surfaces and independent parallax are not reconstructed.", fill="#d7dce4")
    for index, output_frame in enumerate(frame_ids):
        row = by_frame[output_frame]
        source_frame = row["source_frame"]
        with Image.open(composite_paths[output_frame]) as opened:
            tile = opened.convert("RGB").resize((cell_width, cell_height), Image.Resampling.LANCZOS)
        x = (index % columns) * cell_width
        y = title_height + (index // columns) * (cell_height + header)
        draw.text((x + 6, y + 7), f"out {output_frame:02d} / src {source_frame:02d}", fill="white")
        sheet.paste(tile, (x, y + header))
    sheet.save(destination, format="PNG", optimize=False, compress_level=6)
    return {
        "path": destination.relative_to(output).as_posix(),
        "sha256": sha256(destination),
        "bytes": destination.stat().st_size,
        "width_px": sheet.width,
        "height_px": sheet.height,
        "frame_count": len(frame_ids),
        "frames": frame_ids,
    }


def _render_layered_frame(
    document: Mapping[str, Any],
    row: Mapping[str, Any],
    asset_root: Path,
) -> tuple[Any, dict[str, Any]]:
    output_frame = int(row["output_frame"])
    sequence = ExchangeLayerSequence(document, [row], asset_root=asset_root)
    rendered = sequence.render(output_frame, supersample=1)
    source_reference = sequence.render_source_reference(output_frame, supersample=1)
    expected_state = f"source-frame-{row['source_frame']:02d}"
    actor_document = copy.deepcopy(dict(document))
    for layer_key, config in FIGHTER_LAYERS.items():
        layer = next(item for item in actor_document["layers"] if item["layer_id"] == config["layer_id"])
        layer["pose_states"][0]["state_id"] = expected_state
        asset = row["fighter_planes"][layer_key]["image"]
        layer["pose_states"][0]["raster_asset"] = {
            "path": asset["path"], "sha256": asset["sha256"],
            "bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
        }
    source_actor_document = _source_reference_document(document, row["source_render"])
    source_actor_document["clear_color"] = "#00000000"
    source_actor_document["layers"] = [
        layer for layer in source_actor_document["layers"] if layer["kind"] == "character"
    ]
    source_actor_document["layers"][0]["pose_states"][0]["state_id"] = expected_state
    actor_rgba = _render_layered_actor_rgba(actor_document, output_frame, asset_root)
    source_actor_rgba = _render_layered_actor_rgba(source_actor_document, output_frame, asset_root)
    metrics = _layered_rgb_metrics(rendered.image, source_reference.image, actor_rgba, source_actor_rgba)
    return rendered.image, metrics


def _read_rgba(path: Path, label: str) -> Any:
    _ensure_host_dependencies()
    _verify_png(path, expected_mode="RGBA")
    with Image.open(path) as opened:
        return np.asarray(opened, dtype=np.uint8).copy()


def _normalize_actor_plane_assets(
    output: Path,
    output_frame: int,
    source_path: Path,
    actor_pass_paths: Mapping[str, Mapping[str, Path]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    _ensure_host_dependencies()
    source_rgba = _read_rgba(source_path, "combined source view")
    actor_rgba: dict[str, Any] = {}
    raw_mattes: dict[str, Any] = {}
    raw_matte_info: dict[str, dict[str, Any]] = {}
    for layer_key in FIGHTER_LAYERS:
        actor_rgba[layer_key] = _read_rgba(actor_pass_paths[layer_key]["rgba_pass"], f"{layer_key} Cryptomatte color")
        raw_mattes[layer_key], raw_matte_info[layer_key] = _read_cryptomatte_mask(
            actor_pass_paths[layer_key]["matte_pass"]
        )
    alpha_a8, alpha_b8, normalization = _normalize_visible_coverage(
        source_rgba[..., 3], raw_mattes["fighter_a"], raw_mattes["fighter_b"],
    )
    normalized_alpha = {"fighter_a": alpha_a8, "fighter_b": alpha_b8}
    plane_info: dict[str, dict[str, Any]] = {}
    plane_rgba: dict[str, Any] = {}
    for layer_key in FIGHTER_LAYERS:
        image = actor_rgba[layer_key].copy()
        image[..., 3] = normalized_alpha[layer_key]
        mask = normalized_alpha[layer_key].copy()
        plane_root = output / "planes" / layer_key
        image_path = plane_root / "image" / f"frame-{output_frame:03d}.png"
        mask_path = plane_root / "mask" / f"frame-{output_frame:03d}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        mask_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(image, "RGBA").save(image_path, format="PNG", optimize=False, compress_level=6)
        Image.fromarray(mask, "L").save(mask_path, format="PNG", optimize=False, compress_level=6)
        plane_rgba[layer_key] = image
        plane_info[layer_key] = {
            "image": {"path": image_path.relative_to(output).as_posix(),
                      **_verify_png(image_path, expected_mode="RGBA")},
            "mask": {"path": mask_path.relative_to(output).as_posix(),
                     **_verify_png(mask_path, expected_mode="L")},
        }

    rebuilt = Image.alpha_composite(
        Image.fromarray(plane_rgba["fighter_b"], "RGBA"),
        Image.fromarray(plane_rgba["fighter_a"], "RGBA"),
    )
    recomposed_path = output / "recomposed" / f"frame-{output_frame:03d}.png"
    recomposed_path.parent.mkdir(parents=True, exist_ok=True)
    rebuilt.save(recomposed_path, format="PNG", optimize=False, compress_level=6)
    rebuilt_rgba = np.asarray(rebuilt, dtype=np.uint8)

    visible_rgb_errors = {}
    for layer_key in FIGHTER_LAYERS:
        owned = raw_mattes[layer_key] > (1.0 / 255.0)
        color_error = np.abs(actor_rgba[layer_key][..., :3].astype(np.int16)
                             - source_rgba[..., :3].astype(np.int16))[owned]
        if not color_error.size:
            raise ExchangeLayersError(f"{layer_key} Cryptomatte pass has no owned source pixels")
        visible_rgb_errors[layer_key] = {
            "max_channel_error_8bit": int(color_error.max(initial=0)),
            "mean_channel_error_8bit": round(float(color_error.mean()), 6),
        }
    metrics = _recomposition_metrics(rebuilt_rgba, source_rgba, normalization)
    metrics["actor_rgb_pass_error_8bit"] = visible_rgb_errors
    metrics["recomposed_rgba"] = {
        "path": recomposed_path.relative_to(output).as_posix(),
        **_verify_png(recomposed_path, expected_mode="RGBA"),
    }
    return plane_info, metrics, {"source_rgba": source_rgba, "planes": plane_rgba, "rebuilt": rebuilt_rgba}


def _frame_rows_from_worker(
    output: Path,
    worker: Mapping[str, Any],
    source: Mapping[str, Any],
    output_frames: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    selected_output_frames = _validate_output_frames(output_frames)
    worker_frames = worker.get("frames")
    if (not isinstance(worker_frames, Mapping)
            or set(worker_frames) != {str(i) for i in selected_output_frames}
            or worker.get("output_frame_indices") != list(selected_output_frames)):
        raise ExchangeLayersError("Blender state report output frame set differs from the requested sequence")
    rows: list[dict[str, Any]] = []
    for output_frame in selected_output_frames:
        source_frame = source_frame_for_output(output_frame)
        report = worker_frames[str(output_frame)]
        expected_path = f"source/frame-{output_frame:03d}.png"
        if (report.get("output_frame") != output_frame or report.get("source_frame") != source_frame
                or report.get("path") != expected_path):
            raise ExchangeLayersError(f"Blender state report source mapping/path differs at output frame {output_frame}")
        source_path = _inside(output, expected_path, f"combined source frame {output_frame}")
        source_info = _verify_png(source_path, expected_mode="RGBA")
        if report.get("sha256") != source_info["sha256"] or report.get("bytes") != source_info["bytes"]:
            raise ExchangeLayersError(f"Blender report hash or byte count differs at output frame {output_frame}")
        raw_passes: dict[str, dict[str, Path]] = {}
        pass_metadata: dict[str, dict[str, dict[str, Any]]] = {}
        report_passes = report.get("actor_passes")
        if not isinstance(report_passes, Mapping) or set(report_passes) != set(FIGHTER_LAYERS):
            raise ExchangeLayersError(f"Blender actor-pass report differs at output frame {output_frame}")
        for layer_key in FIGHTER_LAYERS:
            expected_paths = {
                "rgba_pass": f"passes/{layer_key}/rgba/frame-{output_frame:03d}-Image.png",
                "matte_pass": f"passes/{layer_key}/matte/frame-{output_frame:03d}-Matte.png",
                "depth_pass": f"passes/{layer_key}/depth/frame-{output_frame:03d}-Depth.exr",
            }
            entries = report_passes[layer_key]
            if not isinstance(entries, Mapping) or set(entries) != set(expected_paths):
                raise ExchangeLayersError(f"{layer_key} Blender pass set is incomplete at frame {output_frame}")
            raw_passes[layer_key] = {}
            pass_metadata[layer_key] = {}
            for pass_kind, relative_path in expected_paths.items():
                entry = entries[pass_kind]
                if entry.get("path") != relative_path:
                    raise ExchangeLayersError(f"{layer_key} Blender pass path differs at frame {output_frame}")
                pass_path = _inside(output, relative_path, f"{layer_key} {pass_kind} frame {output_frame}")
                if pass_kind == "rgba_pass":
                    pass_info = _verify_png(pass_path, expected_mode="RGBA")
                elif pass_kind == "matte_pass":
                    _, pass_info = _read_cryptomatte_mask(pass_path)
                    pass_info["path"] = relative_path
                else:
                    pass_info = _verify_depth_exr(pass_path)
                    pass_info["path"] = relative_path
                if entry.get("sha256") != pass_info["sha256"] or entry.get("bytes") != pass_info["bytes"]:
                    raise ExchangeLayersError(f"{layer_key} Blender pass hash/size differs at frame {output_frame}")
                raw_passes[layer_key][pass_kind] = pass_path
                pass_metadata[layer_key][pass_kind] = {"path": relative_path, **{
                    key: value for key, value in pass_info.items() if key != "path"
                }}
        plane_info, metrics, _ = _normalize_actor_plane_assets(
            output, output_frame, source_path, raw_passes,
        )
        fighter_planes = {}
        for layer_key, config in FIGHTER_LAYERS.items():
            fighter_planes[layer_key] = {
                "layer_id": config["layer_id"],
                "binding_id": config["binding_id"],
                "depth_order": config["depth"],
                **plane_info[layer_key],
                "depth_plane": pass_metadata[layer_key]["depth_pass"],
                "cryptomatte_passes": {
                    "rgba_pass": pass_metadata[layer_key]["rgba_pass"],
                    "matte_pass": pass_metadata[layer_key]["matte_pass"],
                },
            }
        metrics["source_over_order_back_to_front"] = list(OCCLUSION_CONTRACT["source_over_order_back_to_front"])
        rows.append({
            "output_frame": output_frame,
            "output_time_seconds": f"{output_frame}/{FPS}",
            "source_frame": source_frame,
            "source_time_seconds": f"{source_frame}/30",
            "source_scene_sha256": source["scene_sha256"],
            "source_fixture_sha256": source["fixture_sha256"],
            "event_ids": _event_ids(source_frame),
            "source_render": {"path": expected_path, **source_info},
            "fighter_planes": fighter_planes,
            "fixed_view_recomposition": metrics,
            "render_state": dict(report["render_state"]),
        })
    return rows


def _write_layered_scene(
    output: Path,
    first_plane_assets: Mapping[str, Mapping[str, Any]],
) -> tuple[Path, dict[str, Any]]:
    scene_path = output / "layered-scene.v1.json"
    document = _scene_document(first_plane_assets)
    scene_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if _read_json(scene_path, "authored layered scene") != document:
        raise ExchangeLayersError("saved LayeredScene document differs from its in-memory contract")
    return scene_path, document


def _compose_sequence(
    output: Path,
    document: Mapping[str, Any],
    rows: list[dict[str, Any]],
    output_frames: Sequence[int] | None = None,
) -> dict[int, Path]:
    selected_output_frames = _validate_output_frames(output_frames)
    sequence = ExchangeLayerSequence(document, rows, asset_root=output)
    composite_root = output / "composite"
    composite_root.mkdir(parents=True, exist_ok=True)
    destinations: dict[int, Path] = {}
    row_by_frame = {int(row["output_frame"]): row for row in rows}
    if set(row_by_frame) != set(selected_output_frames):
        raise ExchangeLayersError("LayeredScene frame rows differ from the selected output frames")
    order = [frame for frame in _seek_order() if frame in row_by_frame]
    if len(order) != len(selected_output_frames):
        raise ExchangeLayersError("shuffled LayeredScene order omitted a requested frame")
    for output_frame in order:
        row = row_by_frame[output_frame]
        rendered_image, layered_metrics = _render_layered_frame(document, row, output)
        row_by_frame[output_frame]["layered_scene_recomposition"] = layered_metrics
        destination = composite_root / f"frame-{output_frame:03d}.png"
        rendered_image.save(destination, format="PNG", optimize=False, compress_level=6)
        destinations[output_frame] = destination
    return destinations


def _render_layered_exchange(
    output_root: Path,
    source: Mapping[str, Any],
    *,
    root: Path,
    source_dir: Path,
    blender: Path,
    output_frames: Sequence[int],
) -> tuple[dict[str, Any], list[dict[str, Any]], Path, dict[str, Any], dict[int, Path]]:
    """Render selected source samples and run them through the existing LayeredScene backend."""
    (output_root / "source").mkdir()
    worker = _run_blender_worker(
        root, source_dir, output_root, blender=blender, output_frames=output_frames,
    )
    if (worker.get("source_scene_sha256_before") != source["scene_sha256"]
            or worker.get("source_scene_sha256_after") != source["scene_sha256"]
            or worker.get("source_receipt_sha256") != source["receipt_sha256"]
            or worker.get("embedded_scripts") != "disabled"
            or worker.get("online_mode") != "offline"
            or worker.get("saved_scene_reopen", {}).get("render_verification") != "verified"):
        raise ExchangeLayersError("offline Blender reopen/render report failed source integrity checks")

    rows = _frame_rows_from_worker(output_root, worker, source, output_frames)
    first_assets = {key: rows[0]["fighter_planes"][key]["image"] for key in FIGHTER_LAYERS}
    layered_path, layered_document = _write_layered_scene(output_root, first_assets)
    composite_paths = _compose_sequence(output_root, layered_document, rows, output_frames)
    rows_by_frame = {int(row["output_frame"]): row for row in rows}
    for output_frame, path in composite_paths.items():
        info = _verify_png(path, expected_mode="RGB")
        rows_by_frame[output_frame]["layered_scene_output"] = {
            "path": path.relative_to(output_root).as_posix(), **info,
        }
    return worker, rows, layered_path, layered_document, composite_paths


def _implementation_pins(root: Path) -> dict[str, str]:
    module_path = Path(__file__).resolve()
    script_path = root / "content/video_engine/scripts/model_exchange_layers.py"
    layered_module_path = root / "content/video_engine/src/modeling/layered.py"
    return {
        "module_path": module_path.relative_to(root).as_posix(),
        "module_sha256": sha256(module_path),
        "script_path": script_path.relative_to(root).as_posix(),
        "script_sha256": sha256(script_path),
        "layered_module_path": layered_module_path.relative_to(root).as_posix(),
        "layered_module_sha256": sha256(layered_module_path),
    }


def _fixed_view_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    alpha_errors = [row["fixed_view_recomposition"]["alpha_max_error_8bit"] for row in rows]
    rgb_errors = [row["fixed_view_recomposition"]["visible_rgb_max_channel_error_8bit"] for row in rows]
    layered_errors = [row["layered_scene_recomposition"]["max_channel_error_8bit"] for row in rows]
    if not rows or any(row["fixed_view_recomposition"].get("status") != "measured" for row in rows):
        raise ExchangeLayersError("fixed-view recomposition summary needs measured frame rows")
    if any(row["layered_scene_recomposition"].get("status") != "measured" for row in rows):
        raise ExchangeLayersError("post-camera resampling summary needs measured frame rows")
    return {
        "status": "measured_within_declared_limits",
        "output_frames": [int(row["output_frame"]) for row in rows],
        "max_alpha_error_8bit": max(alpha_errors),
        "max_visible_rgb_channel_error_8bit": max(rgb_errors),
        "max_layered_scene_rgb_channel_error_8bit": max(layered_errors),
        "max_layered_scene_actor_alpha_error_8bit": max(
            row["layered_scene_recomposition"]["actor_alpha_max_error_8bit"] for row in rows
        ),
        "max_layered_scene_mean_rgb_channel_error": max(
            row["layered_scene_recomposition"]["mean_channel_error_8bit"] for row in rows
        ),
        "post_camera_per_frame": [
            {
                "output_frame": int(row["output_frame"]),
                "max_rgb_channel_error_8bit": row["layered_scene_recomposition"]["max_channel_error_8bit"],
                "mean_rgb_channel_error": row["layered_scene_recomposition"]["mean_channel_error_8bit"],
                "rgb_affected_pixels_over_1": row["layered_scene_recomposition"]["affected_pixel_count_over_1"],
                "edge_region_affected_pixels_over_1": row["layered_scene_recomposition"]["edge_region_affected_pixel_count_over_1"],
                "actor_alpha_max_error_8bit": row["layered_scene_recomposition"]["actor_alpha_max_error_8bit"],
                "actor_alpha_affected_pixels": row["layered_scene_recomposition"]["actor_alpha_affected_pixel_count"],
            }
            for row in rows
        ],
        "limits": dict(RECOMPOSITION_LIMITS),
    }


def build_exchange_probe(
    output: Path,
    *,
    root: Path = ROOT,
    source_dir: Path | None = None,
    blender: Path = BLENDER,
    review_root: Path | None = None,
    output_frames: Sequence[int] = SMOKE_OUTPUT_FRAMES,
) -> Path:
    """Run a small measured bridge smoke before spending on all 29 output frames."""
    root = Path(root).resolve(strict=True)
    source_dir = (root / SOURCE_BUNDLE_RELATIVE) if source_dir is None else Path(source_dir)
    source = validate_source_bundle(root, source_dir)
    selected_frames = _validate_output_frames(output_frames)
    target = validate_output_target(root, output, review_root=review_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    _reject_redirected_path_chain(target.parent)
    output_root = _new_output_dir(target)
    worker, rows, layered_path, _, composite_paths = _render_layered_exchange(
        output_root, source, root=root, source_dir=Path(source_dir), blender=blender,
        output_frames=selected_frames,
    )
    contact_sheet = _save_contact_sheet(
        output_root, composite_paths, rows, output_root / "contact-sheet.png",
    )
    probe = {
        "schema": "model_exchange_layers.bridge_probe.v2",
        "status": "measured_review_only",
        "diagnostic_only": True,
        "limits": dict(RECOMPOSITION_LIMITS),
        "scope": "fixed source-view visible fighter contribution; no hidden-surface reconstruction or arbitrary parallax",
        "selected_output_frames": list(selected_frames),
        "selected_source_frames": [source_frame_for_output(frame) for frame in selected_frames],
        "source_scene_sha256": source["scene_sha256"],
        "source_fixture_sha256": source["fixture_sha256"],
        "source_receipt_sha256": source["receipt_sha256"],
        "implementation": _implementation_pins(root),
        "source_scene_reopen": worker["saved_scene_reopen"],
        "layered_scene": {"path": layered_path.name, "sha256": sha256(layered_path)},
        "camera": {
            "fighter_depths": {key: FIGHTER_LAYERS[key]["depth"] for key in FIGHTER_LAYERS},
            "source_over_order_back_to_front": list(OCCLUSION_CONTRACT["source_over_order_back_to_front"]),
            "keyframes": [dict(key) for key in CAMERA_KEYFRAMES],
        },
        "fixed_view_recomposition": _fixed_view_summary(rows),
        "contact_sheet": contact_sheet,
        "frames": rows,
    }
    probe_path = output_root / "probe-receipt.json"
    probe_path.write_text(json.dumps(probe, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return probe_path


def build_exchange_layers(
    output: Path,
    *,
    root: Path = ROOT,
    source_dir: Path | None = None,
    blender: Path = BLENDER,
    review_root: Path | None = None,
) -> Path:
    """Render, layer, receipt, and validate a new unique review sequence."""
    root = Path(root).resolve(strict=True)
    source_dir = (root / SOURCE_BUNDLE_RELATIVE) if source_dir is None else Path(source_dir)
    source = validate_source_bundle(root, source_dir)
    target = validate_output_target(root, output, review_root=review_root)
    # Ensure the quarantine exists only after all requested destinations passed preflight.
    target.parent.mkdir(parents=True, exist_ok=True)
    _reject_redirected_path_chain(target.parent)
    output_root = _new_output_dir(target)
    worker, rows, layered_path, layered_document, composite_paths = _render_layered_exchange(
        output_root, source, root=root, source_dir=Path(source_dir), blender=blender,
        output_frames=tuple(range(FRAME_COUNT)),
    )
    preview_info = _save_preview(
        [composite_paths[frame] for frame in range(FRAME_COUNT)],
        output_root / "phone-sequence-preview.gif",
    )
    contact_sheet = _save_contact_sheet(
        output_root, composite_paths, rows, output_root / "contact-sheet.png",
    )

    worker_path = output_root / "blender-state.json"
    stdout_path = output_root / "blender-stdout.txt"
    stderr_path = output_root / "blender-stderr.txt"
    scene_digest = sha256(layered_path)
    receipt = {
        "schema": SCHEMA,
        "status": "review_only_diagnostic",
        "review_state": "review_only",
        "render_eligible": False,
        "diagnostic_only": True,
        "art_note": DIAGNOSTIC_NOTE,
        "claims": {
            "technical_continuous_motion_bridge": True,
            "fighter_art_approved": False,
            "fall_or_ground_continuation": False,
            "audio_changed_or_stretched": False,
            "new_player_introduced": False,
        },
        "source_fps": {"numerator": 30, "denominator": 1},
        "output_fps": {"numerator": FPS, "denominator": 1},
        "output_frame_range_inclusive": [0, FRAME_END],
        "output_frame_count": FRAME_COUNT,
        "source_mapping": {
            "rule": "floor((5*n+1)/4)",
            "interpretation": "nearest 30 fps source frame to each 24 fps sample; exact ties round down",
            "source_frames": list(source_frame_map()),
        },
        "source_events": EXPECTED_EVENTS,
        "inputs": {
            "source_video": source["source"]["source_video"],
            "source_clock": source["source"]["source_clock"],
            "source_blend": source["source"]["source_blend"],
            "source_fixture": {"path": source["source_fixture_path"], "sha256": source["fixture_sha256"]},
            "saved_exchange_scene": {
                "path": source["source_scene_path"], "sha256": source["scene_sha256"],
            },
            "saved_exchange_receipt": {
                "path": source["source_receipt_path"], "sha256": source["receipt_sha256"],
            },
        },
        "source_scene_reopen": worker["saved_scene_reopen"],
        "implementation": {
            **_implementation_pins(root),
        },
        "layered_scene": {"path": layered_path.name, "sha256": scene_digest},
        "blender_state": {"path": worker_path.name, "sha256": sha256(worker_path)},
        "blender_logs": {
            "stdout": {"path": stdout_path.name, "sha256": sha256(stdout_path)},
            "stderr": {"path": stderr_path.name, "sha256": sha256(stderr_path)},
        },
        "render_state": {
            "blender_version": worker["blender_version"],
            "blender_build_hash": worker["blender_build_hash"],
            "embedded_scripts": worker["embedded_scripts"],
            "online_mode": worker["online_mode"],
            "render_engine": worker["render_engine"],
            "camera": worker["camera"],
            "floor_hidden_in_working_process": worker["floor_hidden_in_working_process"],
            "visible_fighter_meshes": worker["visible_fighter_meshes"],
        },
        "layer_planes": {
            "background": {
                "layer_id": "static-source-exchange-background",
                "kind": "environment",
                "role": "background",
                "depth": 0.0,
                "representation": "static LayeredScene shapes",
            },
            "fighter_planes": [
                {
                    "layer_id": FIGHTER_LAYERS[key]["layer_id"],
                    "binding_id": FIGHTER_LAYERS[key]["binding_id"],
                    "depth": FIGHTER_LAYERS[key]["depth"],
                    "representation": "Cryptomatte visible-contribution RGBA/mask/depth, one hash-pinned asset per output frame",
                }
                for key in OCCLUSION_CONTRACT["source_over_order_back_to_front"]
            ],
        },
        "occlusion_contract": dict(OCCLUSION_CONTRACT),
        "fixed_source_view_recomposition": _fixed_view_summary(rows),
        "camera_contract": {
            "view_envelope_deg": {"yaw_deg": [0, 0], "pitch_deg": [0, 0]},
            "zoom_limits": list(CAMERA_ZOOM_LIMITS),
            "keyframes": [dict(key) for key in CAMERA_KEYFRAMES],
            "maximum_disocclusion_px": MAX_DISOCCLUSION_PX,
            "background_bleed_px": BACKGROUND_BLEED_PX,
        },
        "seek_validation": {
            "order": _seek_order(),
            "frame_count": FRAME_COUNT,
            "repeated_seek_frames": [21, 8, 20, 9, 19, 10, 0, 28, 21],
            "expected": "each shuffled LayeredScene render is byte-identical to its hash-pinned composite",
        },
        "preview": preview_info,
        "contact_sheet": contact_sheet,
        "frames": rows,
    }
    receipt_path = output_root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)
    return receipt_path


def _validate_v2_bundle(
    receipt_path: Path,
    output_root: Path,
    receipt: Mapping[str, Any],
    source: Mapping[str, Any],
    *,
    root: Path,
    verify_layered_seeks: bool,
) -> dict[str, Any]:
    if (receipt.get("schema") != SCHEMA or receipt.get("status") != "review_only_diagnostic"
            or receipt.get("review_state") != "review_only" or receipt.get("render_eligible") is not False
            or receipt.get("diagnostic_only") is not True or receipt.get("art_note") != DIAGNOSTIC_NOTE):
        raise ExchangeLayersError("exchange layer receipt is not the pinned v2 review-only diagnostic contract")
    claims = {
        "technical_continuous_motion_bridge": True,
        "fighter_art_approved": False,
        "fall_or_ground_continuation": False,
        "audio_changed_or_stretched": False,
        "new_player_introduced": False,
    }
    if receipt.get("claims") != claims:
        raise ExchangeLayersError("receipt claims exceed the generic diagnostic scope")
    expected_inputs = {
        "source_video": source["source"]["source_video"],
        "source_clock": source["source"]["source_clock"],
        "source_blend": source["source"]["source_blend"],
        "source_fixture": {"path": source["source_fixture_path"], "sha256": source["fixture_sha256"]},
        "saved_exchange_scene": {"path": source["source_scene_path"], "sha256": source["scene_sha256"]},
        "saved_exchange_receipt": {"path": source["source_receipt_path"], "sha256": source["receipt_sha256"]},
    }
    if receipt.get("inputs") != expected_inputs:
        raise ExchangeLayersError("receipt source, fixture, saved-scene, or source-receipt pins differ")
    implementation = receipt.get("implementation")
    module_path = Path(__file__).resolve()
    script_path = root / "content/video_engine/scripts/model_exchange_layers.py"
    layered_module_path = root / "content/video_engine/src/modeling/layered.py"
    if (not isinstance(implementation, Mapping)
            or implementation.get("module_path") != module_path.relative_to(root).as_posix()
            or implementation.get("script_path") != script_path.relative_to(root).as_posix()
            or implementation.get("layered_module_path") != layered_module_path.relative_to(root).as_posix()):
        raise ExchangeLayersError("exchange layer implementation path differs")
    _verify_tracked_python_sha256(module_path, implementation.get("module_sha256"), "exchange_layers.py implementation")
    _verify_tracked_python_sha256(script_path, implementation.get("script_sha256"), "model_exchange_layers.py CLI")
    _verify_tracked_python_sha256(
        layered_module_path, implementation.get("layered_module_sha256"), "layered.py implementation",
    )
    if (receipt.get("source_mapping") != {
            "rule": "floor((5*n+1)/4)",
            "interpretation": "nearest 30 fps source frame to each 24 fps sample; exact ties round down",
            "source_frames": list(source_frame_map()),
        } or receipt.get("source_events") != EXPECTED_EVENTS
            or receipt.get("source_fps") != {"numerator": 30, "denominator": 1}
            or receipt.get("output_fps") != {"numerator": FPS, "denominator": 1}
            or receipt.get("output_frame_range_inclusive") != [0, FRAME_END]
            or receipt.get("output_frame_count") != FRAME_COUNT):
        raise ExchangeLayersError("source/output clock, events, or frame map differs from the pinned contract")

    frames = receipt.get("frames")
    if not isinstance(frames, list) or len(frames) != FRAME_COUNT:
        raise ExchangeLayersError("v2 receipt must list exactly 29 output frames")
    report_entry = receipt.get("blender_state", {})
    report_path = _inside(output_root, report_entry.get("path"), "Blender state report")
    if sha256(report_path) != report_entry.get("sha256"):
        raise ExchangeLayersError("Blender state report SHA-256 differs")
    worker = _read_json(report_path, "Blender sequence state report")
    if (worker.get("blender_version") != "5.2.2 LTS" or worker.get("embedded_scripts") != "disabled"
            or worker.get("online_mode") != "offline"
            or worker.get("source_scene_sha256_before") != source["scene_sha256"]
            or worker.get("source_scene_sha256_after") != source["scene_sha256"]
            or worker.get("source_receipt_sha256") != source["receipt_sha256"]
            or worker.get("frame_count") != FRAME_COUNT
            or worker.get("output_frame_indices") != list(range(FRAME_COUNT))):
        raise ExchangeLayersError("offline Blender state report failed source or render-state validation")
    saved_reopen = worker.get("saved_scene_reopen", {})
    if (saved_reopen.get("status") != "reopened_and_measured"
            or saved_reopen.get("checked_frames") != list(range(36))
            or saved_reopen.get("summary_verified") is not True
            or saved_reopen.get("exposure_verified") is not True
            or saved_reopen.get("render_verification") != "verified"
            or receipt.get("source_scene_reopen") != saved_reopen):
        raise ExchangeLayersError("saved source scene was not reopened and recomputed under scripts-disabled Blender")

    layered_entry = receipt.get("layered_scene", {})
    layered_path = _inside(output_root, layered_entry.get("path"), "LayeredScene document")
    if layered_path.name != "layered-scene.v1.json" or sha256(layered_path) != layered_entry.get("sha256"):
        raise ExchangeLayersError("LayeredScene document path or SHA-256 differs")
    document = _read_json(layered_path, "authored LayeredScene document")
    first_planes = frames[0].get("fighter_planes", {})
    if set(first_planes) != set(FIGHTER_LAYERS):
        raise ExchangeLayersError("first frame must pin independent A and B fighter planes")
    first_assets = {key: first_planes[key]["image"] for key in FIGHTER_LAYERS}
    if document != _scene_document(first_assets):
        raise ExchangeLayersError("LayeredScene differs from the equal-depth two-plane source contract")
    if (document.get("layers", [])[0].get("layer_id") != "static-source-exchange-background"
            or [layer.get("layer_id") for layer in document.get("layers", [])[1:]] != [
                FIGHTER_LAYERS[key]["layer_id"] for key in OCCLUSION_CONTRACT["source_over_order_back_to_front"]
            ]
            or [layer.get("depth") for layer in document.get("layers", [])[1:]] != [1.0, 1.0]
            or document.get("camera", {}).get("keyframes") != [
                {**key, "ease": "smoothstep"} for key in CAMERA_KEYFRAMES
            ]):
        raise ExchangeLayersError("LayeredScene actor order, equal depth, or source camera transform differs")

    expected_layer_planes = {
        "background": {
            "layer_id": "static-source-exchange-background", "kind": "environment", "role": "background",
            "depth": 0.0, "representation": "static LayeredScene shapes",
        },
        "fighter_planes": [
            {
                "layer_id": FIGHTER_LAYERS[key]["layer_id"],
                "binding_id": FIGHTER_LAYERS[key]["binding_id"],
                "depth": 1.0,
                "representation": "Cryptomatte visible-contribution RGBA/mask/depth, one hash-pinned asset per output frame",
            }
            for key in OCCLUSION_CONTRACT["source_over_order_back_to_front"]
        ],
    }
    expected_camera = {
        "view_envelope_deg": {"yaw_deg": [0, 0], "pitch_deg": [0, 0]},
        "zoom_limits": list(CAMERA_ZOOM_LIMITS), "keyframes": [dict(key) for key in CAMERA_KEYFRAMES],
        "maximum_disocclusion_px": MAX_DISOCCLUSION_PX, "background_bleed_px": BACKGROUND_BLEED_PX,
    }
    seek_contract = {
        "order": _seek_order(), "frame_count": FRAME_COUNT,
        "repeated_seek_frames": [21, 8, 20, 9, 19, 10, 0, 28, 21],
        "expected": "each shuffled LayeredScene render is byte-identical to its hash-pinned composite",
    }
    if (receipt.get("layer_planes") != expected_layer_planes
            or receipt.get("occlusion_contract") != OCCLUSION_CONTRACT
            or receipt.get("camera_contract") != expected_camera
            or receipt.get("seek_validation") != seek_contract):
        raise ExchangeLayersError("receipt layer order, camera, occlusion, or random-seek contract differs")

    worker_frames = worker.get("frames", {})
    if set(worker_frames) != {str(frame) for frame in range(FRAME_COUNT)}:
        raise ExchangeLayersError("Blender report frame set differs")
    expected_render_state = {
        key: worker[key] for key in (
            "blender_version", "blender_build_hash", "embedded_scripts", "online_mode", "render_engine", "camera",
            "floor_hidden_in_working_process", "visible_fighter_meshes",
        )
    }
    if receipt.get("render_state") != expected_render_state:
        raise ExchangeLayersError("receipt render state differs from the verified Blender worker")

    composite_paths: dict[int, Path] = {}
    try:
        for output_frame, row in enumerate(frames):
            source_frame = source_frame_for_output(output_frame)
            if (row.get("output_frame") != output_frame or row.get("source_frame") != source_frame
                    or row.get("output_time_seconds") != f"{output_frame}/{FPS}"
                    or row.get("source_time_seconds") != f"{source_frame}/30"
                    or row.get("event_ids") != _event_ids(source_frame)
                    or row.get("source_scene_sha256") != source["scene_sha256"]
                    or row.get("source_fixture_sha256") != source["fixture_sha256"]):
                raise ExchangeLayersError(f"receipt source mapping or event order differs at output frame {output_frame}")
            report = worker_frames[str(output_frame)]
            expected_source = f"source/frame-{output_frame:03d}.png"
            source_record = row.get("source_render", {})
            if report.get("source_frame") != source_frame or source_record.get("path") != expected_source:
                raise ExchangeLayersError(f"source frame report differs at output frame {output_frame}")
            source_path = _inside(output_root, expected_source, f"source render {output_frame}")
            source_info = _verify_png(source_path, expected_mode="RGBA")
            if {key: source_record.get(key) for key in source_info} != source_info:
                raise ExchangeLayersError(f"source render hash/metadata differs at output frame {output_frame}")
            if report.get("sha256") != source_info["sha256"] or report.get("bytes") != source_info["bytes"]:
                raise ExchangeLayersError(f"Blender source render pin differs at output frame {output_frame}")

            fighter_planes = row.get("fighter_planes", {})
            actor_passes = report.get("actor_passes", {})
            if set(fighter_planes) != set(FIGHTER_LAYERS) or set(actor_passes) != set(FIGHTER_LAYERS):
                raise ExchangeLayersError(f"both fighter planes and pass reports are required at frame {output_frame}")
            source_rgba = _read_rgba(source_path, "combined source view")
            actor_rgba: dict[str, Any] = {}
            mattes: dict[str, Any] = {}
            normalized_assets: dict[str, Any] = {}
            for layer_key in FIGHTER_LAYERS:
                expected_pass_paths = {
                    "rgba_pass": f"passes/{layer_key}/rgba/frame-{output_frame:03d}-Image.png",
                    "matte_pass": f"passes/{layer_key}/matte/frame-{output_frame:03d}-Matte.png",
                    "depth_pass": f"passes/{layer_key}/depth/frame-{output_frame:03d}-Depth.exr",
                }
                pass_record = fighter_planes[layer_key]
                report_set = actor_passes[layer_key]
                if (pass_record.get("layer_id") != FIGHTER_LAYERS[layer_key]["layer_id"]
                        or pass_record.get("binding_id") != FIGHTER_LAYERS[layer_key]["binding_id"]
                        or pass_record.get("depth_order") != 1.0):
                    raise ExchangeLayersError(f"{layer_key} plane binding/depth differs at frame {output_frame}")
                pass_meta: dict[str, Any] = {}
                for kind, relative in expected_pass_paths.items():
                    record = (pass_record.get("depth_plane") if kind == "depth_pass" else
                              pass_record.get("cryptomatte_passes", {}).get(kind))
                    worker_record = report_set.get(kind)
                    if (not isinstance(record, Mapping) or record.get("path") != relative
                            or not isinstance(worker_record, Mapping) or worker_record.get("path") != relative):
                        raise ExchangeLayersError(f"{layer_key} {kind} path differs at frame {output_frame}")
                    path = _inside(output_root, relative, f"{layer_key} {kind} {output_frame}")
                    if kind == "rgba_pass":
                        actual = _verify_png(path, expected_mode="RGBA")
                    elif kind == "matte_pass":
                        _, matte_info = _read_cryptomatte_mask(path)
                        actual = {key: value for key, value in matte_info.items() if key != "path"}
                    else:
                        depth_info = _verify_depth_exr(path)
                        actual = {key: value for key, value in depth_info.items() if key != "path"}
                    if ({key: record.get(key) for key in actual} != actual
                            or worker_record.get("sha256") != actual["sha256"]
                            or worker_record.get("bytes") != actual["bytes"]):
                        raise ExchangeLayersError(f"{layer_key} {kind} hash/metadata differs at frame {output_frame}")
                    pass_meta[kind] = path
                actor_rgba[layer_key] = _read_rgba(pass_meta["rgba_pass"], f"{layer_key} actor render")
                mattes[layer_key], _ = _read_cryptomatte_mask(pass_meta["matte_pass"])
                expected_image_path = f"planes/{layer_key}/image/frame-{output_frame:03d}.png"
                expected_mask_path = f"planes/{layer_key}/mask/frame-{output_frame:03d}.png"
                image_record, mask_record = pass_record.get("image", {}), pass_record.get("mask", {})
                if image_record.get("path") != expected_image_path or mask_record.get("path") != expected_mask_path:
                    raise ExchangeLayersError(f"{layer_key} normalized image/mask paths differ at frame {output_frame}")
                image_path = _inside(output_root, expected_image_path, f"{layer_key} normalized image")
                mask_path = _inside(output_root, expected_mask_path, f"{layer_key} normalized mask")
                image_info = _verify_png(image_path, expected_mode="RGBA")
                mask_info = _verify_png(mask_path, expected_mode="L")
                if ({key: image_record.get(key) for key in image_info} != image_info
                        or {key: mask_record.get(key) for key in mask_info} != mask_info):
                    raise ExchangeLayersError(f"{layer_key} normalized image/mask digest differs at frame {output_frame}")
                with Image.open(mask_path) as opened_mask:
                    normalized_mask = np.asarray(opened_mask, dtype=np.uint8).copy()
                with Image.open(image_path) as opened_image:
                    normalized_image = np.asarray(opened_image, dtype=np.uint8).copy()
                if not np.array_equal(normalized_image[..., 3], normalized_mask):
                    raise ExchangeLayersError(f"{layer_key} image alpha differs from its stored mask at frame {output_frame}")
                normalized_assets[layer_key] = normalized_image

            alpha_a, alpha_b, normalization = _normalize_visible_coverage(
                source_rgba[..., 3], mattes["fighter_a"], mattes["fighter_b"],
            )
            for layer_key, expected_alpha in (("fighter_a", alpha_a), ("fighter_b", alpha_b)):
                if (not np.array_equal(normalized_assets[layer_key][..., 3], expected_alpha)
                        or not np.array_equal(normalized_assets[layer_key][..., :3], actor_rgba[layer_key][..., :3])):
                    raise ExchangeLayersError(f"{layer_key} visible RGB/alpha normalization differs at frame {output_frame}")
            recomposed = Image.alpha_composite(
                Image.fromarray(normalized_assets["fighter_b"], "RGBA"),
                Image.fromarray(normalized_assets["fighter_a"], "RGBA"),
            )
            recomposed_path = _inside(output_root, f"recomposed/frame-{output_frame:03d}.png", "recomposed source frame")
            recomposed_info = _verify_png(recomposed_path, expected_mode="RGBA")
            recomposed_rgba = np.asarray(recomposed, dtype=np.uint8)
            with Image.open(recomposed_path) as opened_recomposed:
                if not np.array_equal(recomposed_rgba, np.asarray(opened_recomposed, dtype=np.uint8)):
                    raise ExchangeLayersError(f"stored normalized recomposition differs at frame {output_frame}")
            fixed_metrics = _recomposition_metrics(recomposed_rgba, source_rgba, normalization)
            fixed_metrics["source_over_order_back_to_front"] = list(OCCLUSION_CONTRACT["source_over_order_back_to_front"])
            fixed_metrics["recomposed_rgba"] = {"path": f"recomposed/frame-{output_frame:03d}.png", **recomposed_info}
            rgb_errors: dict[str, Any] = {}
            for layer_key in FIGHTER_LAYERS:
                owned = mattes[layer_key] > (1.0 / 255.0)
                channel_error = np.abs(actor_rgba[layer_key][..., :3].astype(np.int16)
                                       - source_rgba[..., :3].astype(np.int16))[owned]
                rgb_errors[layer_key] = {
                    "max_channel_error_8bit": int(channel_error.max(initial=0)),
                    "mean_channel_error_8bit": round(float(channel_error.mean()), 6),
                }
            fixed_metrics["actor_rgb_pass_error_8bit"] = rgb_errors
            if row.get("fixed_view_recomposition") != fixed_metrics:
                raise ExchangeLayersError(f"fixed-view recomposition metrics differ at frame {output_frame}")
            render_state = report.get("render_state", {})
            if (row.get("render_state") != render_state
                    or render_state.get("scene_frame_current") != source_frame
                    or render_state.get("film_transparent") is not True
                    or render_state.get("camera_projection") != "ORTHO"
                    or render_state.get("resolution_px") != [WIDTH, HEIGHT]
                    or render_state.get("visible_fighter_meshes") != worker.get("visible_fighter_meshes")):
                raise ExchangeLayersError(f"Blender render state differs at output frame {output_frame}")
            composite_rel = f"composite/frame-{output_frame:03d}.png"
            composite_record = row.get("layered_scene_output", {})
            if composite_record.get("path") != composite_rel:
                raise ExchangeLayersError(f"LayeredScene composite path differs at output frame {output_frame}")
            composite_path = _inside(output_root, composite_rel, f"LayeredScene composite {output_frame}")
            composite_info = _verify_png(composite_path, expected_mode="RGB")
            if {key: composite_record.get(key) for key in composite_info} != composite_info:
                raise ExchangeLayersError(f"LayeredScene composite hash/metadata differs at output frame {output_frame}")
            rendered, layered_metrics = _render_layered_frame(document, row, output_root)
            if row.get("layered_scene_recomposition") != layered_metrics:
                raise ExchangeLayersError(f"post-camera resampling metrics differ at output frame {output_frame}")
            if rendered.tobytes() != np.asarray(Image.open(composite_path).convert("RGB"), dtype=np.uint8).tobytes():
                raise ExchangeLayersError(f"LayeredScene rendered bytes differ from composite at frame {output_frame}")
            composite_paths[output_frame] = composite_path

    except (KeyError, TypeError, AttributeError, OSError, ValueError) as exc:
        if isinstance(exc, ExchangeLayersError):
            raise
        raise ExchangeLayersError(f"v2 receipt or LayeredScene validation failed: {exc}") from exc

    if receipt.get("fixed_source_view_recomposition") != _fixed_view_summary(frames):
        raise ExchangeLayersError("receipt fixed-view/post-camera measured summary differs from per-frame evidence")
    if ({path.name for path in (output_root / "source").glob("*.png")} !=
            {f"frame-{frame:03d}.png" for frame in range(FRAME_COUNT)}
            or {path.name for path in (output_root / "composite").glob("*.png")} !=
            {f"frame-{frame:03d}.png" for frame in range(FRAME_COUNT)}):
        raise ExchangeLayersError("source/composite sequence contains a missing or unexpected frame")

    for record_name, root_name in (("stdout", "blender-stdout.txt"), ("stderr", "blender-stderr.txt")):
        record = receipt.get("blender_logs", {}).get(record_name, {})
        log_path = _inside(output_root, record.get("path"), f"Blender {record_name} log")
        if log_path.name != root_name or sha256(log_path) != record.get("sha256"):
            raise ExchangeLayersError(f"Blender {record_name} log pin differs")
    preview = receipt.get("preview", {})
    preview_path = _inside(output_root, preview.get("path"), "phone-sized sequence preview")
    if (preview_path.name != "phone-sequence-preview.gif" or sha256(preview_path) != preview.get("sha256")
            or preview.get("label") != PREVIEW_LABEL or preview.get("frame_delay_ms") != 42
            or preview.get("width_px") != WIDTH or preview.get("height_px") != HEIGHT
            or preview.get("format") != "GIF" or preview.get("frame_count") != FRAME_COUNT):
        raise ExchangeLayersError("phone-sized diagnostic preview pin differs")
    with Image.open(preview_path) as gif:
        if gif.format != "GIF" or gif.size != (WIDTH, HEIGHT) or int(getattr(gif, "n_frames", 1)) != FRAME_COUNT:
            raise ExchangeLayersError("phone-sized preview dimensions/frame count differ")
    sheet = receipt.get("contact_sheet", {})
    sheet_path = _inside(output_root, sheet.get("path"), "diagnostic contact sheet")
    if sha256(sheet_path) != sheet.get("sha256") or sheet.get("frames") != list(range(FRAME_COUNT)):
        raise ExchangeLayersError("contact sheet pin or coverage differs")
    with Image.open(sheet_path) as image:
        if image.format != "PNG" or image.size != (sheet.get("width_px"), sheet.get("height_px")):
            raise ExchangeLayersError("contact sheet dimensions/format differ")

    if verify_layered_seeks:
        adapter = ExchangeLayerSequence(document, frames, asset_root=output_root)
        seek_order = receipt["seek_validation"]["order"]
        for output_frame in seek_order:
            rendered = adapter.render(output_frame, supersample=1)
            with Image.open(composite_paths[output_frame]) as expected:
                if rendered.image.tobytes() != expected.convert("RGB").tobytes():
                    raise ExchangeLayersError(f"LayeredScene shuffled seek differs at frame {output_frame}")
        for output_frame in seek_contract["repeated_seek_frames"]:
            rendered = adapter.render(output_frame, supersample=1)
            with Image.open(composite_paths[output_frame]) as expected:
                if rendered.image.tobytes() != expected.convert("RGB").tobytes():
                    raise ExchangeLayersError(f"LayeredScene repeat seek differs at frame {output_frame}")
    return {
        "status": "verified_review_only",
        "receipt_sha256": sha256(receipt_path),
        "source_scene_sha256": source["scene_sha256"],
        "fixture_sha256": source["fixture_sha256"],
        "output_frame_count": FRAME_COUNT,
        "shuffled_seek_count": FRAME_COUNT if verify_layered_seeks else 0,
        "source_mapping_verified": True,
        "render_verification": "verified",
        "source_scene_reopen": "verified",
        "pre_camera_alpha_max_error_8bit": receipt["fixed_source_view_recomposition"]["max_alpha_error_8bit"],
        "post_camera_rgb_max_error_8bit": receipt["fixed_source_view_recomposition"]["max_layered_scene_rgb_channel_error_8bit"],
        "post_camera_alpha_max_error_8bit": receipt["fixed_source_view_recomposition"]["max_layered_scene_actor_alpha_error_8bit"],
        "review_eligible": False,
    }


def validate_bundle(
    receipt_path: Path,
    *,
    root: Path = ROOT,
    source_dir: Path | None = None,
    review_root: Path | None = None,
    verify_layered_seeks: bool = True,
) -> dict[str, Any]:
    """Recompute source/output hashes, image bounds, views, and shuffled LayeredScene seeks."""
    _ensure_host_dependencies()
    root = Path(root).resolve(strict=True)
    source_dir = (root / SOURCE_BUNDLE_RELATIVE) if source_dir is None else Path(source_dir)
    source = validate_source_bundle(root, source_dir)
    receipt_path = Path(receipt_path)
    _reject_redirected_path_chain(receipt_path)
    try:
        output_root = receipt_path.parent.resolve(strict=True)
    except OSError as exc:
        raise ExchangeLayersError("review receipt directory is missing") from exc
    approved_roots = _approved_review_roots(root, review_root)
    if output_root.parent not in approved_roots or receipt_path.name != "receipt.json":
        raise ExchangeLayersError("receipt must live in a direct child of an approved exchange-layer review quarantine")
    receipt = _read_json(receipt_path, "exchange layers receipt")
    if receipt.get("schema") == SCHEMA_V1:
        legacy_implementation = receipt.get("implementation")
        legacy_module = Path(__file__).resolve()
        legacy_script = root / "content/video_engine/scripts/model_exchange_layers.py"
        if (not isinstance(legacy_implementation, Mapping)
                or legacy_implementation.get("module_path") != legacy_module.relative_to(root).as_posix()
                or legacy_implementation.get("script_path") != legacy_script.relative_to(root).as_posix()):
            raise ExchangeLayersError("legacy v1 exchange receipt implementation paths differ")
        # A v1 receipt is understood as the historical combined-plane format,
        # but its whole-file implementation pins must still be current. This
        # branch intentionally rejects the old run after any code change.
        _verify_tracked_python_sha256(
            legacy_module, legacy_implementation.get("module_sha256"), "exchange_layers.py implementation",
        )
        _verify_tracked_python_sha256(
            legacy_script, legacy_implementation.get("script_sha256"), "model_exchange_layers.py CLI",
        )
        raise ExchangeLayersError("legacy v1 combined-plane receipt requires its producing implementation")
    if receipt.get("schema") == SCHEMA:
        return _validate_v2_bundle(
            receipt_path, output_root, receipt, source, root=root, verify_layered_seeks=verify_layered_seeks,
        )
    if (receipt.get("schema") != SCHEMA or receipt.get("status") != "review_only_diagnostic"
            or receipt.get("review_state") != "review_only"
            or receipt.get("render_eligible") is not False or receipt.get("diagnostic_only") is not True
            or receipt.get("art_note") != DIAGNOSTIC_NOTE):
        raise ExchangeLayersError("exchange layer receipt is not the pinned review-only diagnostic contract")
    if receipt.get("claims") != {
        "technical_continuous_motion_bridge": True,
        "fighter_art_approved": False,
        "fall_or_ground_continuation": False,
        "audio_changed_or_stretched": False,
        "new_player_introduced": False,
    }:
        raise ExchangeLayersError("receipt claims exceed the generic diagnostic scope")
    if receipt.get("inputs", {}).get("saved_exchange_scene", {}).get("sha256") != source["scene_sha256"]:
        raise ExchangeLayersError("source scene SHA-256 differs from the parent-pinned bundle")
    expected_input_pins = {
        "source_video": source["source"]["source_video"],
        "source_clock": source["source"]["source_clock"],
        "source_blend": source["source"]["source_blend"],
        "source_fixture": {"path": source["source_fixture_path"], "sha256": source["fixture_sha256"]},
        "saved_exchange_scene": {"path": source["source_scene_path"], "sha256": source["scene_sha256"]},
        "saved_exchange_receipt": {"path": source["source_receipt_path"], "sha256": source["receipt_sha256"]},
    }
    if receipt.get("inputs") != expected_input_pins:
        raise ExchangeLayersError("receipt source, fixture, saved-scene, or source-receipt pins differ")
    implementation = receipt.get("implementation")
    module_path = Path(__file__).resolve()
    script_path = root / "content/video_engine/scripts/model_exchange_layers.py"
    if (not isinstance(implementation, Mapping)
            or implementation.get("module_path") != module_path.relative_to(root).as_posix()
            or implementation.get("script_path") != script_path.relative_to(root).as_posix()):
        raise ExchangeLayersError("exchange layer implementation path differs")
    _verify_tracked_python_sha256(
        module_path, implementation.get("module_sha256"), "exchange_layers.py implementation",
    )
    _verify_tracked_python_sha256(
        script_path, implementation.get("script_sha256"), "model_exchange_layers.py CLI",
    )
    if receipt.get("source_mapping") != {
        "rule": "floor((5*n+1)/4)",
        "interpretation": "nearest 30 fps source frame to each 24 fps sample; exact ties round down",
        "source_frames": list(source_frame_map()),
    }:
        raise ExchangeLayersError("24 fps source frame map is stale or altered")
    if receipt.get("source_events") != EXPECTED_EVENTS:
        raise ExchangeLayersError("contact and follow-through event order differs from the pinned source fixture")
    if (receipt.get("source_fps") != {"numerator": 30, "denominator": 1}
            or receipt.get("output_fps") != {"numerator": 24, "denominator": 1}
            or receipt.get("output_frame_range_inclusive") != [0, 28]
            or receipt.get("output_frame_count") != FRAME_COUNT):
        raise ExchangeLayersError("output sequence duration or frame-rate contract differs")

    try:
        frames = receipt.get("frames")
        if not isinstance(frames, list) or len(frames) != FRAME_COUNT:
            raise ExchangeLayersError("receipt must list exactly 29 output frames")
        report_entry = receipt.get("blender_state")
        report_path = _inside(output_root, report_entry.get("path"), "Blender state report")
        if sha256(report_path) != report_entry.get("sha256"):
            raise ExchangeLayersError("Blender state report SHA-256 differs")
        worker = _read_json(report_path, "Blender sequence state report")
        if (worker.get("blender_version") != "5.2.2 LTS"
                or worker.get("embedded_scripts") != "disabled"
                or worker.get("online_mode") != "offline"
                or worker.get("source_scene_sha256_before") != source["scene_sha256"]
                or worker.get("source_scene_sha256_after") != source["scene_sha256"]
                or worker.get("source_receipt_sha256") != source["receipt_sha256"]
                or worker.get("frame_count") != FRAME_COUNT):
            raise ExchangeLayersError("offline Blender state report failed source or render-state validation")
        saved_reopen = worker.get("saved_scene_reopen", {})
        if (saved_reopen.get("status") != "reopened_and_measured"
                or saved_reopen.get("checked_frames") != list(range(36))
                or saved_reopen.get("summary_verified") is not True
                or saved_reopen.get("exposure_verified") is not True
                or saved_reopen.get("render_verification") != "verified"):
            raise ExchangeLayersError("saved-scene receipt was not reopened and recomputed in Blender")
        if receipt.get("source_scene_reopen") != saved_reopen:
            raise ExchangeLayersError("receipt saved-scene reopen summary differs from Blender state report")

        layered_entry = receipt.get("layered_scene", {})
        layered_path = _inside(output_root, layered_entry.get("path"), "LayeredScene document")
        if layered_path.name != "layered-scene.v1.json" or sha256(layered_path) != layered_entry.get("sha256"):
            raise ExchangeLayersError("authored LayeredScene document path or SHA-256 differs")
        document = _read_json(layered_path, "authored LayeredScene document")
        if (document.get("scene_id") != "generic-source-exchange-24fps-diagnostic"
                or document.get("review_state") != "review_only"
                or document.get("render_eligible") is not False
                or document.get("diagnostic_only") is not True
                or document.get("art_note") != DIAGNOSTIC_NOTE
                or document.get("view_envelope_deg") != {"yaw_deg": [0, 0], "pitch_deg": [0, 0]}
                or document.get("camera", {}).get("zoom_limits") != list(CAMERA_ZOOM_LIMITS)
                or document.get("camera", {}).get("keyframes") != [
                    {**key, "ease": "smoothstep"} for key in CAMERA_KEYFRAMES
                ]):
            raise ExchangeLayersError("unsupported or unapproved authored camera view")
        first_motion = frames[0].get("motion_layer")
        if not isinstance(first_motion, Mapping) or document != _scene_document(first_motion):
            raise ExchangeLayersError("authored LayeredScene differs from the pinned static-background/two-rig contract")
        timeline = document.get("scene", {})
        if (timeline.get("duration_frames") != FRAME_COUNT
                or timeline.get("fps") != {"numerator": FPS, "denominator": 1}
                or timeline.get("events") != [] or timeline.get("contacts") != []):
            raise ExchangeLayersError("LayeredScene clock must remain 24 fps with no invented contacts/events")
        if len(document.get("layers", [])) != 2:
            raise ExchangeLayersError("LayeredScene must contain the static background and one combined fighter plane")
        background = document["layers"][0]
        fighter = document["layers"][1]
        if (background.get("layer_id") != "static-source-exchange-background"
                or background.get("kind") != "environment" or background.get("role") != "background"
                or background.get("depth") != 0.0
                or fighter.get("layer_id") != "combined-generic-fighter-motion"
                or fighter.get("kind") != "character" or fighter.get("binding_id") != "generic_exchange"
                or fighter.get("depth") != 1.0 or len(fighter.get("pose_states", [])) != 1
                or len(fighter.get("expression_states", [])) != 1):
            raise ExchangeLayersError("static background or bounded combined-fighter layer contract differs")

        expected_camera_contract = {
            "view_envelope_deg": {"yaw_deg": [0, 0], "pitch_deg": [0, 0]},
            "zoom_limits": list(CAMERA_ZOOM_LIMITS),
            "keyframes": [dict(key) for key in CAMERA_KEYFRAMES],
            "maximum_disocclusion_px": MAX_DISOCCLUSION_PX,
            "background_bleed_px": BACKGROUND_BLEED_PX,
        }
        if receipt.get("camera_contract") != expected_camera_contract:
            raise ExchangeLayersError("receipt camera view or bounded parallax contract differs")
        if receipt.get("layer_planes") != {
            "background": {
                "layer_id": "static-source-exchange-background",
                "kind": "environment",
                "role": "background",
                "depth": 0.0,
                "representation": "static LayeredScene shapes",
            },
            "fighter_motion": {
                "layer_id": "combined-generic-fighter-motion",
                "kind": "character",
                "role": "subject",
                "depth": 1.0,
                "representation": "transparent combined two-rig PNG, one hash-pinned asset per output frame",
                "per_seek_adapter": "ExchangeLayerSequence; one pose asset loaded at a time",
            },
        }:
            raise ExchangeLayersError("receipt static background or combined fighter plane contract differs")
        if receipt.get("seek_validation") != {
            "order": _seek_order(),
            "frame_count": FRAME_COUNT,
            "repeated_seek_frames": [21, 8, 20, 9, 19, 10, 0, 28, 21],
            "expected": "each shuffled LayeredScene render is byte-identical to its hash-pinned composite",
        }:
            raise ExchangeLayersError("receipt out-of-order seek validation contract differs")

        report_frames = worker.get("frames", {})
        if set(report_frames) != {str(i) for i in range(FRAME_COUNT)}:
            raise ExchangeLayersError("Blender report frame set differs")
        if (receipt.get("render_state", {}).get("blender_version") != worker.get("blender_version")
                or receipt.get("render_state", {}).get("blender_build_hash") != worker.get("blender_build_hash")
                or receipt.get("render_state", {}).get("render_engine") != worker.get("render_engine")
                or receipt.get("render_state", {}).get("floor_hidden_in_working_process") is not True):
            raise ExchangeLayersError("receipt render state differs from the verified Blender state")

        composite_paths: dict[int, Path] = {}
        for output_frame, row in enumerate(frames):
            source_frame = source_frame_for_output(output_frame)
            expected_events = _event_ids(source_frame)
            if (row.get("output_frame") != output_frame or row.get("source_frame") != source_frame
                    or row.get("output_time_seconds") != f"{output_frame}/24"
                    or row.get("source_time_seconds") != f"{source_frame}/30"
                    or row.get("event_ids") != expected_events
                    or row.get("source_scene_sha256") != source["scene_sha256"]
                    or row.get("source_fixture_sha256") != source["fixture_sha256"]):
                raise ExchangeLayersError(f"receipt source mapping or event order differs at output frame {output_frame}")
            report_frame = report_frames[str(output_frame)]
            motion = row.get("motion_layer", {})
            expected_motion_path = f"motion/frame-{output_frame:03d}.png"
            if report_frame.get("source_frame") != source_frame or motion.get("path") != expected_motion_path:
                raise ExchangeLayersError(f"motion sequence reference differs at output frame {output_frame}")
            motion_path = _inside(output_root, expected_motion_path, f"motion frame {output_frame}")
            motion_info = _verify_png(motion_path, expected_mode="RGBA")
            if {key: motion.get(key) for key in motion_info} != motion_info:
                raise ExchangeLayersError(f"motion PNG hash, dimensions, alpha bounds or bytes differ at output frame {output_frame}")
            report_render_state = report_frame.get("render_state")
            if row.get("render_state") != report_render_state:
                raise ExchangeLayersError(f"render state differs at output frame {output_frame}")
            if (report_render_state.get("source_frame_current") != source_frame
                    and report_render_state.get("scene_frame_current") != source_frame):
                raise ExchangeLayersError(f"Blender evaluated the wrong source frame at output frame {output_frame}")
            if (report_render_state.get("film_transparent") is not True
                    or report_render_state.get("camera_projection") != "ORTHO"
                    or report_render_state.get("resolution_px") != [WIDTH, HEIGHT]
                    or report_render_state.get("visible_fighter_meshes") != worker.get("visible_fighter_meshes")):
                raise ExchangeLayersError(f"Blender render state is unsupported at output frame {output_frame}")
            composite = row.get("layered_scene_output", {})
            expected_composite_path = f"composite/frame-{output_frame:03d}.png"
            if composite.get("path") != expected_composite_path:
                raise ExchangeLayersError(f"LayeredScene composite path differs at output frame {output_frame}")
            composite_path = _inside(output_root, expected_composite_path, f"composite frame {output_frame}")
            composite_info = _verify_png(composite_path, expected_mode="RGB")
            if {key: composite.get(key) for key in composite_info} != composite_info:
                raise ExchangeLayersError(f"LayeredScene composite hash or dimensions differ at output frame {output_frame}")
            composite_paths[output_frame] = composite_path

        expected_pngs = {f"frame-{frame:03d}.png" for frame in range(FRAME_COUNT)}
        if ({path.name for path in (output_root / "motion").glob("*.png")} != expected_pngs
                or {path.name for path in (output_root / "composite").glob("*.png")} != expected_pngs):
            raise ExchangeLayersError("a sequence frame is missing or an unexpected PNG was added")

        preview = receipt.get("preview", {})
        preview_path = _inside(output_root, preview.get("path"), "phone-sized sequence preview")
        if preview_path.name != "phone-sequence-preview.gif" or sha256(preview_path) != preview.get("sha256"):
            raise ExchangeLayersError("phone-sized sequence preview SHA-256 differs")
        if (preview.get("label") != PREVIEW_LABEL or preview.get("frame_delay_ms") != 42
                or preview.get("width_px") != WIDTH or preview.get("height_px") != HEIGHT
                or preview.get("format") != "GIF"):
            raise ExchangeLayersError("phone-sized sequence preview lacks its generic diagnostic label or dimensions")
        with Image.open(preview_path) as encoded_preview:
            if (encoded_preview.format != "GIF" or encoded_preview.size != (WIDTH, HEIGHT)
                    or int(getattr(encoded_preview, "n_frames", 1)) != FRAME_COUNT
                    or preview.get("frame_count") != FRAME_COUNT):
                raise ExchangeLayersError("phone-sized preview dimensions or frame count differs")

        if verify_layered_seeks:
            adapter = ExchangeLayerSequence(document, frames, asset_root=output_root)
            seek_order = receipt.get("seek_validation", {}).get("order")
            if seek_order != _seek_order():
                raise ExchangeLayersError("receipt shuffled seek order differs")
            for output_frame in seek_order:
                rendered = adapter.render(output_frame, supersample=1)
                with Image.open(composite_paths[output_frame]) as expected_image:
                    expected_bytes = expected_image.convert("RGB").tobytes()
                if rendered.image.tobytes() != expected_bytes:
                    raise ExchangeLayersError(f"LayeredScene shuffled seek differs at output frame {output_frame}")
            repeat_frames = receipt["seek_validation"].get("repeated_seek_frames")
            if repeat_frames != [21, 8, 20, 9, 19, 10, 0, 28, 21]:
                raise ExchangeLayersError("receipt repeated seek sequence differs")
            for output_frame in repeat_frames:
                rendered = adapter.render(output_frame, supersample=1)
                with Image.open(composite_paths[output_frame]) as expected_image:
                    if rendered.image.tobytes() != expected_image.convert("RGB").tobytes():
                        raise ExchangeLayersError(f"LayeredScene repeat seek differs at frame {output_frame}")
    except (KeyError, TypeError, AttributeError, OSError, ValueError) as exc:
        if isinstance(exc, ExchangeLayersError):
            raise
        raise ExchangeLayersError(f"receipt or LayeredScene validation failed: {exc}") from exc

    return {
        "status": "verified_review_only",
        "receipt_sha256": sha256(receipt_path),
        "source_scene_sha256": source["scene_sha256"],
        "fixture_sha256": source["fixture_sha256"],
        "output_frame_count": FRAME_COUNT,
        "shuffled_seek_count": FRAME_COUNT if verify_layered_seeks else 0,
        "source_mapping_verified": True,
        "render_verification": "verified",
        "source_scene_reopen": "verified",
        "review_eligible": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build or validate the T7a.4 review-only fighter-plane exchange.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="render all 29 pinned source samples to a new 24 fps review directory")
    build.add_argument("--output", type=Path, default=ROOT / T7A4_REVIEW_RELATIVE / "fighter-planes-sequence-v2")
    build.add_argument("--source-dir", type=Path, default=ROOT / SOURCE_BUNDLE_RELATIVE)
    build.add_argument("--blender", type=Path, default=BLENDER)
    probe = sub.add_parser("probe", help="measure a bounded f10/f24 bridge smoke through LayeredScene")
    probe.add_argument("--output", type=Path, default=ROOT / T7A4_REVIEW_RELATIVE / "bridge-smoke-f10-f24-v3")
    probe.add_argument("--source-dir", type=Path, default=ROOT / SOURCE_BUNDLE_RELATIVE)
    probe.add_argument("--blender", type=Path, default=BLENDER)
    validate = sub.add_parser("validate", help="recompute hashes and all shuffled LayeredScene seeks")
    validate.add_argument("--receipt", type=Path, required=True)
    validate.add_argument("--source-dir", type=Path, default=ROOT / SOURCE_BUNDLE_RELATIVE)
    args = parser.parse_args(argv)
    if args.command == "build":
        receipt_path = build_exchange_layers(
            args.output, root=ROOT, source_dir=args.source_dir, blender=args.blender,
        )
        result = validate_bundle(receipt_path, root=ROOT, source_dir=args.source_dir)
        print(json.dumps({"receipt": str(receipt_path), **result}, sort_keys=True))
    elif args.command == "probe":
        probe_path = build_exchange_probe(
            args.output, root=ROOT, source_dir=args.source_dir, blender=args.blender,
        )
        print(json.dumps({"probe_receipt": str(probe_path), "status": "measured_review_only"}, sort_keys=True))
    else:
        result = validate_bundle(args.receipt, root=ROOT, source_dir=args.source_dir)
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__" and "--worker" in sys.argv:
    _blender_entry()
