"""Source-clock 30 fps Blender exchange to a review-only 24 fps layer sequence.

The Blender scene and its fixture remain immutable inputs.  This bridge renders
the two generic fighters together onto a transparent motion plane and composes
that frame through the existing :class:`LayeredScene` implementation.  The
per-seek adapter keeps one raster state loaded at a time, within LayeredScene's
existing state and memory budgets.
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
LayeredScene: Any = None
LayeredSceneError: type[Exception] = ValueError


def _ensure_host_dependencies() -> None:
    """Load Pillow and LayeredScene only in the host Python, not Blender's worker."""
    global Image, ImageDraw, ImageFont, LayeredScene, LayeredSceneError
    if Image is not None:
        return
    from PIL import Image as pillow_image, ImageDraw as pillow_draw, ImageFont as pillow_font

    from content.video_engine.src.modeling.layered import (
        LayeredScene as layered_scene,
        LayeredSceneError as layered_scene_error,
    )

    Image = pillow_image
    ImageDraw = pillow_draw
    ImageFont = pillow_font
    LayeredScene = layered_scene
    LayeredSceneError = layered_scene_error


SCHEMA = "model_exchange_layers.v1"
SOURCE_SCENE_SHA256 = "942ba684be00e87988330e6709c14a46fd54c34f64714c2253727b863a3d772f"
SOURCE_BUNDLE_RELATIVE = Path(
    "content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange/t7a3-parent-source"
)
REVIEW_RELATIVE = Path(
    "content/video_engine/review/model-engines/benchmark-v1/2_5d/source-exchange"
)
FIXTURE_RELATIVE = fight_motion.FIXTURE_RELATIVE
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
FPS = 24
FRAME_COUNT = 29
FRAME_END = FRAME_COUNT - 1
WIDTH, HEIGHT = 540, 960
MAX_OUTPUT_BYTES = 16_777_216
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
    "Generic two-rig source exchange only. Not approved fighter art. The source ends before the fall or ground "
    "continuation; no fall, extra impact, extra head response, or audio change is authored."
)
PREVIEW_LABEL = "GENERIC DIAGNOSTIC | NO FALL / NO ART APPROVAL"


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


def validate_output_target(
    root: Path,
    output: Path,
    *,
    review_root: Path | None = None,
) -> Path:
    """Require a new direct child of the T7a.3 review quarantine."""
    root = Path(root).resolve(strict=True)
    approved_root = _review_root(root, review_root)
    candidate = Path(output)
    if ".." in candidate.parts:
        raise ExchangeLayersError("unsafe output path")
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.absolute()
    _reject_redirected_path_chain(approved_root)
    _reject_redirected_path_chain(candidate)
    approved = approved_root.resolve(strict=False)
    target = candidate.resolve(strict=False)
    if target == approved or target.parent != approved:
        raise ExchangeLayersError("output must be a direct child of the T7a.3 review quarantine")
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


def _worker_render(
    root: Path,
    source_dir: Path,
    output: Path,
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
    actor_meshes = [obj for obj in actor_objects if obj.type == "MESH"]
    if not actor_meshes or any(not obj.data.vertices for obj in actor_meshes):
        raise ExchangeLayersError("one or both privately bound fighter meshes are missing or empty")
    visible_meshes = sorted(
        obj.name for obj in actor_meshes if not obj.hide_render and obj.visible_get()
    )
    expected_bindings = {str(obj.get("model_binding_id")) for obj in actor_meshes}
    if expected_bindings != {"attacker", "receiver"} or len(visible_meshes) < 2:
        raise ExchangeLayersError("source exchange render does not contain both bound fighters")

    target = Path(output).resolve(strict=True)
    motion_root = target / "motion"
    if not motion_root.is_dir() or motion_root.is_symlink():
        raise ExchangeLayersError("preflighted motion output directory is missing or redirected")
    floor.hide_render = True  # In-memory render state only; the source blend is never saved.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = True
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = 100

    frame_rows: dict[str, Any] = {}
    for output_frame, source_frame in enumerate(source_frame_map()):
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
        destination = motion_root / f"frame-{output_frame:03d}.png"
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
        frame_rows[str(output_frame)] = {
            "output_frame": output_frame,
            "source_frame": source_frame,
            "path": destination.relative_to(target).as_posix(),
            "sha256": sha256(destination),
            "bytes": destination.stat().st_size,
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
        "frame_count": len(frame_rows),
        "frames": frame_rows,
    }


def _blender_entry() -> None:
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 6 or args[0] != "--worker":
        raise ExchangeLayersError("expected Blender worker arguments: --worker ROOT SOURCE_BUNDLE OUTPUT REPORT")
    _, root_raw, source_raw, output_raw, report_raw, mode = args
    if mode != "render":
        raise ExchangeLayersError("unsupported Blender worker mode")
    report = _worker_render(Path(root_raw), Path(source_raw), Path(output_raw))
    report_path = Path(report_raw)
    _reject_redirected_path_chain(report_path)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("MODEL_EXCHANGE_LAYERS_WORKER=" + json.dumps({
        "status": "rendered",
        "frame_count": report["frame_count"],
        "source_scene_sha256": report["source_scene_sha256_after"],
        "report": str(report_path),
    }, sort_keys=True))


def _run_blender_worker(
    root: Path,
    source_dir: Path,
    output: Path,
    *,
    blender: Path = BLENDER,
) -> dict[str, Any]:
    if not Path(blender).is_file():
        raise ExchangeLayersError(f"pinned Blender executable is missing: {blender}")
    report_path = output / "blender-state.json"
    command = [
        str(blender), "--background", "--offline-mode", "--disable-autoexec",
        str(source_dir / "source-exchange.blend"), "--python", str(Path(__file__).resolve()), "--",
        "--worker", str(root.resolve()), str(source_dir.resolve()), str(output.resolve()), str(report_path.resolve()), "render",
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
    if report.get("frame_count") != FRAME_COUNT or len(report.get("frames", {})) != FRAME_COUNT:
        raise ExchangeLayersError("Blender worker did not render all 29 output frames")
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


def _scene_document(first_motion_asset: Mapping[str, Any]) -> dict[str, Any]:
    bg = _background_plane(WIDTH, HEIGHT)
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
            "motion_channels": [
                {"channel_id": "source-frame-pose", "binding_id": "generic_exchange",
                 "target_kind": "articulation", "semantic_target": "mapped_source_frame",
                 "value_unit": "normalized", "interpolation": "step",
                 "keyframes": [{"frame": 0, "value": 0}]},
                {"channel_id": "source-frame-expression", "binding_id": "generic_exchange",
                 "target_kind": "face_control", "semantic_target": "source_expression",
                 "value_unit": "normalized", "interpolation": "step",
                 "keyframes": [{"frame": 0, "value": 0}]},
            ],
        },
        "layers": [
            bg,
            {
                "layer_id": "combined-generic-fighter-motion",
                "kind": "character",
                "binding_id": "generic_exchange",
                "role": "subject",
                "depth": 1.0,
                "anchor_px": [WIDTH / 2, HEIGHT / 2],
                "source_bounds_px": [0, 0, WIDTH, HEIGHT],
                "silhouette_bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
                "disocclusion_budget_px": MAX_DISOCCLUSION_PX,
                "pose_channel": "source-frame-pose",
                "expression_channel": "source-frame-expression",
                "shapes": [],
                "pose_states": [{
                    "state_id": "source-frame-00",
                    "index": 0,
                    "shapes": [],
                    "raster_asset": dict(first_motion_asset),
                }],
                "expression_states": [{"state_id": "fixed-source-expression", "index": 0, "shapes": []}],
            },
        ],
    }


class ExchangeLayerSequence:
    """Per-seek adapter that feeds one source frame to the existing LayeredScene."""

    def __init__(
        self,
        document: Mapping[str, Any],
        frame_rows: Sequence[Mapping[str, Any]],
        *,
        asset_root: Path,
    ):
        if len(frame_rows) != FRAME_COUNT:
            raise ExchangeLayersError("LayeredScene adapter requires all 29 source frame rows")
        self.document = copy.deepcopy(dict(document))
        self.frame_rows = tuple(frame_rows)
        self.asset_root = Path(asset_root).resolve(strict=True)
        self._fighter = next(
            (layer for layer in self.document.get("layers", [])
             if layer.get("layer_id") == "combined-generic-fighter-motion"),
            None,
        )
        if not isinstance(self._fighter, dict) or len(self._fighter.get("pose_states", [])) != 1:
            raise ExchangeLayersError("per-seek adapter requires one bounded authored raster state")

    def render(self, output_frame: int, *, supersample: int = 1):
        _ensure_host_dependencies()
        source_frame = source_frame_for_output(output_frame)
        row = self.frame_rows[output_frame]
        if row.get("output_frame") != output_frame or row.get("source_frame") != source_frame:
            raise ExchangeLayersError("per-seek source mapping differs from the exact 24 fps rule")
        motion = row.get("motion_layer")
        if not isinstance(motion, Mapping):
            raise ExchangeLayersError(f"output frame {output_frame} lacks its transparent motion asset")
        document = copy.deepcopy(self.document)
        fighter = next(layer for layer in document["layers"]
                       if layer["layer_id"] == "combined-generic-fighter-motion")
        pose = fighter["pose_states"][0]
        pose["state_id"] = f"source-frame-{source_frame:02d}"
        pose["raster_asset"] = {
            "path": motion["path"],
            "sha256": motion["sha256"],
            "bounds_local_px": [-WIDTH / 2, -HEIGHT / 2, WIDTH / 2, HEIGHT / 2],
        }
        try:
            scene = LayeredScene(document, asset_root=self.asset_root)
            state = scene.evaluate(output_frame)
            expected_state = f"source-frame-{source_frame:02d}"
            if (state.selected_states.get("combined-generic-fighter-motion", {}).get("pose") != expected_state
                    or state.events or state.contacts):
                raise ExchangeLayersError("LayeredScene selected a wrong source frame or declared a new event/contact")
            return scene.render(output_frame, supersample=supersample)
        except LayeredSceneError as exc:
            raise ExchangeLayersError(f"LayeredScene rejected output frame {output_frame}: {exc}") from exc


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


def _frame_rows_from_worker(output: Path, worker: Mapping[str, Any], source: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_map = source_frame_map()
    worker_frames = worker.get("frames")
    if not isinstance(worker_frames, Mapping) or set(worker_frames) != {str(i) for i in range(FRAME_COUNT)}:
        raise ExchangeLayersError("Blender state report does not contain the exact 29 output frames")
    rows: list[dict[str, Any]] = []
    for output_frame, source_frame in enumerate(source_map):
        report = worker_frames[str(output_frame)]
        expected_path = f"motion/frame-{output_frame:03d}.png"
        if (report.get("output_frame") != output_frame or report.get("source_frame") != source_frame
                or report.get("path") != expected_path):
            raise ExchangeLayersError(f"Blender state report source mapping/path differs at output frame {output_frame}")
        path = _inside(output, expected_path, f"motion frame {output_frame}")
        info = _verify_png(path, expected_mode="RGBA")
        if report.get("sha256") != info["sha256"] or report.get("bytes") != info["bytes"]:
            raise ExchangeLayersError(f"Blender report hash or byte count differs at output frame {output_frame}")
        rows.append({
            "output_frame": output_frame,
            "output_time_seconds": f"{output_frame}/{FPS}",
            "source_frame": source_frame,
            "source_time_seconds": f"{source_frame}/30",
            "source_scene_sha256": source["scene_sha256"],
            "source_fixture_sha256": source["fixture_sha256"],
            "event_ids": _event_ids(source_frame),
            "motion_layer": {"path": expected_path, **info},
            "render_state": dict(report["render_state"]),
        })
    return rows


def _write_layered_scene(output: Path, first_motion_asset: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    scene_path = output / "layered-scene.v1.json"
    document = _scene_document(first_motion_asset)
    scene_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if _read_json(scene_path, "authored layered scene") != document:
        raise ExchangeLayersError("saved LayeredScene document differs from its in-memory contract")
    return scene_path, document


def _compose_sequence(output: Path, document: Mapping[str, Any], rows: list[dict[str, Any]]) -> list[Path]:
    sequence = ExchangeLayerSequence(document, rows, asset_root=output)
    composite_root = output / "composite"
    composite_root.mkdir(exist_ok=False)
    destinations: dict[int, Path] = {}
    for output_frame in _seek_order():
        rendered = sequence.render(output_frame, supersample=1)
        destination = composite_root / f"frame-{output_frame:03d}.png"
        rendered.image.save(destination, format="PNG", optimize=False, compress_level=6)
        destinations[output_frame] = destination
    paths = [destinations[index] for index in range(FRAME_COUNT)]
    return paths


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
    (output_root / "motion").mkdir()

    worker = _run_blender_worker(root, Path(source_dir), output_root, blender=blender)
    if (worker.get("source_scene_sha256_before") != source["scene_sha256"]
            or worker.get("source_scene_sha256_after") != source["scene_sha256"]
            or worker.get("source_receipt_sha256") != source["receipt_sha256"]
            or worker.get("embedded_scripts") != "disabled"
            or worker.get("online_mode") != "offline"
            or worker.get("saved_scene_reopen", {}).get("render_verification") != "verified"):
        raise ExchangeLayersError("offline Blender reopen/render report failed source integrity checks")

    rows = _frame_rows_from_worker(output_root, worker, source)
    first_asset = rows[0]["motion_layer"]
    layered_path, layered_document = _write_layered_scene(output_root, first_asset)
    composite_paths = _compose_sequence(output_root, layered_document, rows)
    for row, path in zip(rows, composite_paths):
        info = _verify_png(path, expected_mode="RGB")
        row["layered_scene_output"] = {"path": path.relative_to(output_root).as_posix(), **info}
    preview_info = _save_preview(composite_paths, output_root / "phone-sequence-preview.gif")

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
            "module_path": Path(__file__).resolve().relative_to(root).as_posix(),
            "module_sha256": sha256(Path(__file__)),
            "script_path": (root / "content/video_engine/scripts/model_exchange_layers.py").relative_to(root).as_posix(),
            "script_sha256": sha256(root / "content/video_engine/scripts/model_exchange_layers.py"),
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
            "fighter_motion": {
                "layer_id": "combined-generic-fighter-motion",
                "kind": "character",
                "role": "subject",
                "depth": 1.0,
                "representation": "transparent combined two-rig PNG, one hash-pinned asset per output frame",
                "per_seek_adapter": "ExchangeLayerSequence; one pose asset loaded at a time",
            },
        },
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
        "frames": rows,
    }
    receipt_path = output_root / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_bundle(receipt_path, root=root, source_dir=source_dir, review_root=review_root)
    return receipt_path


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
    approved_root = _review_root(root, review_root).resolve(strict=False)
    if output_root.parent != approved_root or receipt_path.name != "receipt.json":
        raise ExchangeLayersError("receipt must live in a direct child of the T7a.3 review quarantine")
    receipt = _read_json(receipt_path, "exchange layers receipt")
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

    parser = argparse.ArgumentParser(description="Build or validate the T7a.3 review-only source exchange layer sequence.")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="render the pinned source exchange to a new 24 fps review directory")
    build.add_argument("--output", type=Path, default=ROOT / REVIEW_RELATIVE / "exchange-sequence")
    build.add_argument("--source-dir", type=Path, default=ROOT / SOURCE_BUNDLE_RELATIVE)
    build.add_argument("--blender", type=Path, default=BLENDER)
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
    else:
        result = validate_bundle(args.receipt, root=ROOT, source_dir=args.source_dir)
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__" and "--worker" in sys.argv:
    _blender_entry()
