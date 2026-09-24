from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
WIDTH = 720
HEIGHT = 1280
FPS = 30
FRAME_COUNT = 105
SOURCE_CLIP_SHA256 = "d16bc20d1f953ad149b6dd30c545a0146b7b04f0df5ada9a8cd7f2f1ebba8daf"
RAW_SOURCE_SHA256 = "c162dcb7e7a11336c5b0bd3b29d51ecbf2f8cd5a49f90a3b851775165da64758"
SOURCE_CLIP_RELATIVE = (
    "content/video_engine/projects/martial-matters/pilots/"
    "knockout-brain-matchcut-001/production/edit-media/knockout.mp4"
)
RAW_SOURCE_RELATIVE = (
    "content/video_engine/projects/martial-matters/pilots/"
    "knockout-brain-matchcut-001/assets/raw/source-short/"
    "ufc-sharaf-steveson-high.mkv"
)
TIMING_FIXTURE_RELATIVE = (
    "content/video_engine/tests/fixtures/modeling/motion/"
    "source-exchange-clock.v1.json"
)
TIMING_FIXTURE_SHA256 = "74305d4eb84efdcc9875d3abaaf0e86f2618913cf32335341f4d5ff027d2d823"
FRAME_CONTACTS = [8, 9, 10, 11, 12, 22, 23, 24, 25, 26, 27]
JAB_ANCHOR = (427, 528)
HOOK_ANCHOR = (332, 478)
INK = (25, 35, 56, 230)
GOLD = (242, 205, 104, 224)
CREAM = (255, 246, 221, 236)
SUPERSAMPLE = 3


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, capture: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def ffprobe(path: Path) -> dict[str, Any]:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-count_frames",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ]
    )
    return json.loads(result.stdout)


def video_stream(probe: dict[str, Any]) -> dict[str, Any]:
    streams = [stream for stream in probe["streams"] if stream.get("codec_type") == "video"]
    if len(streams) != 1:
        raise ValueError(f"Expected one video stream, found {len(streams)}")
    return streams[0]


def assert_source_probe(probe: dict[str, Any]) -> None:
    stream = video_stream(probe)
    actual = (
        stream.get("width"),
        stream.get("height"),
        stream.get("r_frame_rate"),
        int(stream.get("nb_read_frames") or stream.get("nb_frames") or 0),
    )
    expected = (WIDTH, HEIGHT, "30/1", FRAME_COUNT)
    if actual != expected:
        raise ValueError(f"Source video probe mismatch: expected {expected}, got {actual}")
    if any(stream.get("codec_type") == "audio" for stream in probe["streams"]):
        raise ValueError("Pinned knockout.mp4 is expected to be silent; refusing an audio-bearing input")
    duration = float(probe["format"]["duration"])
    if not math.isclose(duration, FRAME_COUNT / FPS, abs_tol=0.001):
        raise ValueError(f"Source duration mismatch: {duration}")


def assert_fixture(fixture_path: Path, raw_source_sha: str) -> dict[str, Any]:
    if sha256(fixture_path) != TIMING_FIXTURE_SHA256:
        raise ValueError("Timing fixture hash does not match the base-checkout value recorded for this work order")
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    provenance = fixture["provenance"]
    scene = fixture["scene"]
    if provenance["sha256"] != raw_source_sha:
        raise ValueError("Timing fixture points at a different raw source")
    if scene["duration_frames"] != FRAME_COUNT or scene["fps"] != {"numerator": FPS, "denominator": 1}:
        raise ValueError("Timing fixture frame clock does not match the pinned knockout clip")
    events = {event["event_id"]: event["frame"] for event in scene["events"]}
    if events.get("left-hook-contact") != 24 or events.get("head-snap") != 25:
        raise ValueError(f"Unexpected hook/head-snap timing in fixture: {events}")
    return fixture


def rgba_canvas() -> Image.Image:
    return Image.new("RGBA", (WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE), (0, 0, 0, 0))


def scaled_points(points: list[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(round(x * SUPERSAMPLE), round(y * SUPERSAMPLE)) for x, y in points]


def add_rounded_stroke(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    width: float,
    outer: tuple[int, int, int, int],
    inner: tuple[int, int, int, int],
) -> None:
    pts = scaled_points(points)
    outer_width = max(1, round((width + 3.2) * SUPERSAMPLE))
    inner_width = max(1, round(width * SUPERSAMPLE))
    draw.line(pts, fill=outer, width=outer_width, joint="curve")
    draw.line(pts, fill=inner, width=inner_width, joint="curve")
    radius = inner_width // 2
    for x, y in (pts[0], pts[-1]):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=inner)


def bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    progress: float = 1.0,
    steps: int = 48,
) -> list[tuple[float, float]]:
    end = max(2, round(steps * progress))
    points = []
    for index in range(end + 1):
        t = index / steps
        u = 1.0 - t
        points.append(
            (
                u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
            )
        )
    return points


def ray_polygon(
    center: tuple[float, float],
    angle_deg: float,
    inner_radius: float,
    outer_radius: float,
    base_width: float,
) -> list[tuple[float, float]]:
    angle = math.radians(angle_deg)
    dx, dy = math.cos(angle), math.sin(angle)
    nx, ny = -dy, dx
    mid_radius = inner_radius + (outer_radius - inner_radius) * 0.62
    widths = (base_width, base_width * 0.7, 0.8)
    radii = (inner_radius, mid_radius, outer_radius)
    left = []
    right = []
    for radius, width in zip(radii, widths):
        x = center[0] + dx * radius
        y = center[1] + dy * radius
        left.append((x + nx * width / 2, y + ny * width / 2))
        right.append((x - nx * width / 2, y - ny * width / 2))
    return left + list(reversed(right))


def draw_ink_burst(canvas: Image.Image, center: tuple[int, int], flavor: str) -> None:
    draw = ImageDraw.Draw(canvas)
    angles = (
        [-164, -128, -83, -37, 9, 54, 119, 163]
        if flavor == "jab"
        else [-153, -110, -62, -16, 33, 78, 132, 174]
    )
    for index, angle in enumerate(angles):
        inner = 21 + (index % 3) * 2
        outer = 39 + ((index * 7) % 9)
        width = 10 + (index % 2) * 2
        dark = scaled_points(ray_polygon(center, angle, inner - 1, outer + 2, width + 3))
        warm = scaled_points(ray_polygon(center, angle, inner, outer, width))
        draw.polygon(dark, fill=INK)
        draw.polygon(warm, fill=GOLD)
    # Small ink flecks sit outside the empty center; the contact remains visible.
    flecks = [(-43, -15, -33, -18), (26, -35, 31, -42), (39, 21, 47, 27)]
    for x1, y1, x2, y2 in flecks:
        add_rounded_stroke(
            draw,
            [(center[0] + x1, center[1] + y1), (center[0] + x2, center[1] + y2)],
            2.2,
            INK,
            CREAM,
        )


def draw_broken_ring(canvas: Image.Image, center: tuple[int, int], flavor: str) -> None:
    draw = ImageDraw.Draw(canvas)
    cx, cy = (round(x * SUPERSAMPLE) for x in center)
    radius = 42
    box = (
        cx - radius * SUPERSAMPLE,
        cy - radius * SUPERSAMPLE,
        cx + radius * SUPERSAMPLE,
        cy + radius * SUPERSAMPLE,
    )
    # Keep the target-head side open: the jab's marks sit behind the red glove,
    # and the hook's marks sit behind the incoming hand on the opposite side.
    arcs = (
        [(108, 148), (160, 205), (218, 260), (270, 285)]
        if flavor == "jab"
        else [(285, 333), (342, 360), (0, 62), (72, 108)]
    )
    ring_core = (255, 236, 184, 244)
    for start, end in arcs:
        draw.arc(box, start=start, end=end, fill=(25, 35, 56, 242), width=11 * SUPERSAMPLE)
        draw.arc(box, start=start + 1, end=end - 1, fill=ring_core, width=4 * SUPERSAMPLE)
    tick_angles = [110, 193, 257] if flavor == "jab" else [291, 4, 76]
    for angle in tick_angles:
        radians = math.radians(angle)
        x1 = center[0] + math.cos(radians) * 48
        y1 = center[1] + math.sin(radians) * 48
        x2 = center[0] + math.cos(radians) * 57
        y2 = center[1] + math.sin(radians) * 57
        add_rounded_stroke(draw, [(x1, y1), (x2, y2)], 3.1, INK, CREAM)


def draw_slash_ticks(canvas: Image.Image, center: tuple[int, int], flavor: str) -> None:
    directions = (
        [(-47, -27, -33, -32), (35, -36, 48, -30), (43, 19, 55, 25)]
        if flavor == "jab"
        else [(-42, -34, -29, -41), (40, -27, 51, -19), (31, 35, 43, 40)]
    )
    draw = ImageDraw.Draw(canvas)
    for x1, y1, x2, y2 in directions:
        add_rounded_stroke(
            draw,
            [(center[0] + x1, center[1] + y1), (center[0] + x2, center[1] + y2)],
            4.8,
            INK,
            CREAM,
        )


def contact_layer(kind: str, center: tuple[int, int], flavor: str) -> Image.Image:
    canvas = rgba_canvas()
    if kind == "ink-burst":
        draw_ink_burst(canvas, center, flavor)
    elif kind == "broken-ring":
        draw_broken_ring(canvas, center, flavor)
    elif kind == "slash-ticks":
        draw_slash_ticks(canvas, center, flavor)
    else:
        raise ValueError(f"Unknown contact treatment: {kind}")
    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def draw_linear_streaks(frame: int) -> Image.Image:
    canvas = rgba_canvas()
    draw = ImageDraw.Draw(canvas)
    progress = 0.7 if frame == 8 else 1.0
    all_lines = [
        [(311, 496), (338, 493), (371, 490), (404, 488)],
        [(318, 518), (353, 516), (390, 515), (441, 513)],
        [(321, 548), (350, 547), (384, 545), (428, 541)],
        [(341, 570), (369, 568), (397, 565)],
    ]
    for line in all_lines:
        start, end = line[0], line[-1]
        shortened = (start[0] + (end[0] - start[0]) * progress, start[1] + (end[1] - start[1]) * progress)
        points = [start, *line[1:-1], shortened]
        add_rounded_stroke(draw, points, 3.3, INK, GOLD)
    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def draw_hook_arc_streaks(frame: int) -> Image.Image:
    canvas = rgba_canvas()
    draw = ImageDraw.Draw(canvas)
    progress = 0.62 if frame == 22 else 1.0
    paths = [
        ((477, 572), (466, 502), (405, 470), (365, 466)),
        ((489, 589), (466, 514), (420, 483), (379, 478)),
        ((455, 601), (439, 545), (405, 512), (389, 505)),
    ]
    for index, path in enumerate(paths):
        points = bezier(*path, progress=progress)
        add_rounded_stroke(draw, points, 3.1 if index < 2 else 2.6, INK, GOLD if index == 0 else CREAM)
    return canvas.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def make_layer(frame: int, event_id: str, selected_style: str) -> Image.Image:
    if event_id == "jab-linear":
        return draw_linear_streaks(frame)
    if event_id == "hook-arc":
        return draw_hook_arc_streaks(frame)
    if event_id == "jab-contact":
        return contact_layer(selected_style, JAB_ANCHOR, "jab")
    if event_id == "hook-contact":
        return contact_layer(selected_style, HOOK_ANCHOR, "hook")
    raise ValueError(f"Unknown event id: {event_id}")


def ffmpeg_extract_frame(video: Path, frame: int, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video),
            "-vf",
            f"select='eq(n,{frame})'",
            "-fps_mode",
            "passthrough",
            "-frames:v",
            "1",
            str(output),
        ]
    )


def font(size: int) -> ImageFont.ImageFont:
    windows_font = Path("C:/Windows/Fonts/arialbd.ttf")
    if windows_font.exists():
        return ImageFont.truetype(str(windows_font), size=size)
    return ImageFont.load_default()


def label_tile(image: Image.Image, label: str, size: tuple[int, int]) -> Image.Image:
    tile = image.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(tile, "RGBA")
    use_font = font(max(17, round(size[0] * 0.061)))
    box = draw.textbbox((0, 0), label, font=use_font)
    pad_x, pad_y = 8, 5
    draw.rounded_rectangle(
        (7, 7, box[2] + pad_x * 2 + 7, box[3] + pad_y * 2 + 7),
        radius=6,
        fill=(15, 23, 38, 212),
        outline=(242, 205, 104, 220),
        width=1,
    )
    draw.text((7 + pad_x, 7 + pad_y), label, font=use_font, fill=(255, 246, 221, 255))
    return tile


def candidate_sheet(source_frames: dict[int, Image.Image], output: Path) -> str:
    styles = [("SOURCE", None), ("A  INK BURST", "ink-burst"), ("B  BROKEN RING", "broken-ring"), ("C  SLASH TICKS", "slash-ticks")]
    cell = (360, 640)
    sheet = Image.new("RGB", (cell[0] * 4, cell[1] * 2), (12, 18, 30))
    for row, (frame, center, flavor) in enumerate(
        [(10, JAB_ANCHOR, "jab"), (24, HOOK_ANCHOR, "hook")]
    ):
        source = source_frames[frame].convert("RGBA")
        for col, (label, style) in enumerate(styles):
            preview = source.copy()
            if style:
                preview = Image.alpha_composite(preview, contact_layer(style, center, flavor))
            tile = label_tile(preview, f"f{frame:02d}  {label}", cell)
            sheet.paste(tile, (col * cell[0], row * cell[1]))
    sheet.save(output, optimize=True)
    return sha256(output)


def build_contact_sheet(video: Path, output: Path, temp_dir: Path) -> str:
    cell = (360, 640)
    sheet = Image.new("RGB", (cell[0] * 4, cell[1] * 4), (15, 22, 35))
    for index, frame in enumerate(FRAME_CONTACTS):
        image_path = temp_dir / f"final-f{frame:03d}.png"
        ffmpeg_extract_frame(video, frame, image_path)
        image = Image.open(image_path)
        tile = label_tile(image, f"f{frame:02d}", cell)
        x = (index % 4) * cell[0]
        y = (index // 4) * cell[1]
        sheet.paste(tile, (x, y))
    sheet.save(output, optimize=True)
    if sheet.size != (1440, 2560):
        raise ValueError(f"Contact sheet size is not 9:16: {sheet.size}")
    return sha256(output)


def build_detail_crop_sheet(video: Path, output: Path, temp_dir: Path) -> str:
    frames = [10, 24, 25]
    crop_box = (0, 350, WIDTH, 894)
    crop_width = crop_box[2] - crop_box[0]
    crop_height = crop_box[3] - crop_box[1]
    label_height = 42
    sheet = Image.new("RGB", (crop_width, len(frames) * (crop_height + label_height)), (15, 22, 35))
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        image_path = temp_dir / f"detail-f{frame:03d}.png"
        ffmpeg_extract_frame(video, frame, image_path)
        image = Image.open(image_path).convert("RGB").crop(crop_box)
        top = index * (crop_height + label_height)
        draw.rectangle((0, top, crop_width, top + label_height), fill=(15, 22, 35))
        draw.text((12, top + 7), f"f{frame:02d}" + ("  clean head-snap reference" if frame == 25 else "  contact beat"),
                  font=font(24), fill=(255, 246, 221))
        sheet.paste(image, (0, top + label_height))
    sheet.save(output, optimize=True)
    return sha256(output)


def overlay_video(source: Path, layer_records: list[dict[str, Any]], output: Path) -> list[str]:
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source)]
    for record in layer_records:
        command.extend(["-loop", "1", "-framerate", str(FPS), "-i", str(ROOT / record["path"])])

    filters = ["[0:v]setpts=PTS-STARTPTS,format=rgba[base]"]
    last = "base"
    for index, record in enumerate(layer_records):
        overlay = f"layer{index}"
        result = f"v{index}"
        filters.append(f"[{index + 1}:v]setpts=PTS-STARTPTS,format=rgba[{overlay}]")
        filters.append(
            f"[{last}][{overlay}]overlay=0:0:format=auto:eof_action=pass:shortest=0:"
            f"enable='eq(n,{record['frame']})'[{result}]"
        )
        last = result
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{last}]",
            "-an",
            "-frames:v",
            str(FRAME_COUNT),
            "-r",
            str(FPS),
            "-fps_mode",
            "cfr",
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
            "-metadata",
            "title=Private review - source-timed anime accent exchange",
            str(output),
        ]
    )
    run(command)
    return command


def validate_output(output: Path, expected_source_hash: str, source: Path, raw_source: Path) -> dict[str, Any]:
    probe = ffprobe(output)
    stream = video_stream(probe)
    actual = (
        stream.get("width"),
        stream.get("height"),
        stream.get("r_frame_rate"),
        int(stream.get("nb_read_frames") or stream.get("nb_frames") or 0),
    )
    expected = (WIDTH, HEIGHT, "30/1", FRAME_COUNT)
    if actual != expected:
        raise ValueError(f"Output probe mismatch: expected {expected}, got {actual}")
    if any(stream.get("codec_type") == "audio" for stream in probe["streams"]):
        raise ValueError("Output unexpectedly contains an audio stream")
    duration = float(probe["format"]["duration"])
    if not math.isclose(duration, FRAME_COUNT / FPS, abs_tol=0.001):
        raise ValueError(f"Output duration mismatch: {duration}")
    decode_command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-xerror",
        "-i",
        str(output),
        "-map",
        "0:v:0",
        "-f",
        "null",
        "-",
    ]
    decode = run(decode_command)
    source_hash_after = sha256(source)
    raw_hash_after = sha256(raw_source)
    if source_hash_after != expected_source_hash or raw_hash_after != RAW_SOURCE_SHA256:
        raise ValueError("A pinned source hash changed during the build")
    return {
        "ffprobe": probe,
        "full_decode": {
            "command": decode_command,
            "returncode": decode.returncode,
            "stdout": decode.stdout,
            "stderr": decode.stderr,
        },
        "source_sha256_after": source_hash_after,
        "raw_source_sha256_after": raw_hash_after,
    }


def alpha_receipt(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256(path),
        "size": list(image.size),
        "nontransparent_pixels": sum(1 for value in alpha.getdata() if value > 0),
        "alpha_bounds": list(alpha.getbbox() or (0, 0, 0, 0)),
    }


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the private-review 105-frame anime accent exchange.")
    parser.add_argument("--source-video", required=True, type=Path)
    parser.add_argument("--raw-source", required=True, type=Path)
    parser.add_argument("--timing-fixture", required=True, type=Path)
    parser.add_argument("--previews-only", action="store_true")
    parser.add_argument(
        "--style",
        choices=["ink-burst", "broken-ring", "slash-ticks"],
        help="Contact treatment selected after inspecting the 2-3 option preview.",
    )
    args = parser.parse_args()

    source = args.source_video.resolve()
    raw_source = args.raw_source.resolve()
    fixture_path = args.timing_fixture.resolve()
    expected_hashes = [
        (source, SOURCE_CLIP_SHA256, "prepared 105-frame source clip"),
        (raw_source, RAW_SOURCE_SHA256, "raw official FIGHT source"),
        (fixture_path, TIMING_FIXTURE_SHA256, "base-checkout source timing fixture"),
    ]
    for path, expected, label in expected_hashes:
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"{label} hash mismatch: expected {expected}, got {actual}")

    source_probe = ffprobe(source)
    assert_source_probe(source_probe)
    fixture = assert_fixture(fixture_path, sha256(raw_source))

    layers_dir = ROOT / "layers"
    review_dir = ROOT / "review"
    layers_dir.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    output = ROOT / "anime-exchange-overlay.mp4"
    manifest_path = ROOT / "manifest.json"
    verification_path = review_dir / "verification.json"
    contact_sheet_path = review_dir / "contact-sheet-9x16.png"
    candidate_sheet_path = review_dir / "candidate-treatments.png"
    detail_crops_path = review_dir / "detail-crops-f10-f24-f25.png"

    if args.previews_only:
        with tempfile.TemporaryDirectory(prefix="anime-overlay-candidates-", dir=ROOT) as temp_name:
            source_frames: dict[int, Image.Image] = {}
            for frame in (10, 24):
                image_path = Path(temp_name) / f"source-f{frame:03d}.png"
                ffmpeg_extract_frame(source, frame, image_path)
                source_frames[frame] = Image.open(image_path).convert("RGBA")
            candidate_sha = candidate_sheet(source_frames, candidate_sheet_path)
        print(
            json.dumps(
                {
                    "candidate_sheet": str(candidate_sheet_path),
                    "candidate_sha256": candidate_sha,
                    "options": ["ink-burst", "broken-ring", "slash-ticks"],
                    "frames": [10, 24],
                    "source_frame_origin": 0,
                },
                indent=2,
            )
        )
        return
    if args.style is None:
        raise SystemExit("Render the option preview first, inspect it, then pass --style <selected option>.")

    event_layers = [
        (8, "jab-linear", "f008-jab-linear.png"),
        (9, "jab-linear", "f009-jab-linear.png"),
        (10, "jab-contact", "f010-jab-contact.png"),
        (22, "hook-arc", "f022-hook-arc.png"),
        (23, "hook-arc", "f023-hook-arc.png"),
        (24, "hook-contact", "f024-hook-contact.png"),
    ]
    layer_records = []
    for frame, event_id, name in event_layers:
        path = layers_dir / name
        make_layer(frame, event_id, args.style).save(path, optimize=True)
        layer_records.append(
            {
                "frame": frame,
                "time_seconds": str(Fraction(frame, FPS)),
                "event_id": event_id,
                "path": path.relative_to(ROOT).as_posix(),
                "effect_family": "hand-authored low-opacity anime motion-ink accent",
                "sha256": sha256(path),
            }
        )

    encode_command = overlay_video(source, layer_records, output)

    with tempfile.TemporaryDirectory(prefix="anime-overlay-review-", dir=ROOT) as temp_name:
        temp_dir = Path(temp_name)
        source_frames: dict[int, Image.Image] = {}
        for frame in (10, 24):
            image_path = temp_dir / f"source-f{frame:03d}.png"
            ffmpeg_extract_frame(source, frame, image_path)
            source_frames[frame] = Image.open(image_path).convert("RGBA")
        candidate_sha = candidate_sheet(source_frames, candidate_sheet_path)
        contact_sha = build_contact_sheet(output, contact_sheet_path, temp_dir)
        detail_crops_sha = build_detail_crop_sheet(output, detail_crops_path, temp_dir)

    verification = validate_output(output, SOURCE_CLIP_SHA256, source, raw_source)
    write_json(verification_path, verification)

    source_path_hash = sha256(source)
    raw_path_hash = sha256(raw_source)
    fixture_hash = sha256(fixture_path)
    manifest = {
        "schema": "anime_exchange_overlay.v1",
        "status": "private-review / experimental local recipe",
        "approval": "not approved; parent owns visual approval and native assembly",
        "source_clock": {
            "source_clip_input": SOURCE_CLIP_RELATIVE,
            "source_clip_sha256": source_path_hash,
            "raw_source_input": RAW_SOURCE_RELATIVE,
            "raw_source_sha256": raw_path_hash,
            "raw_source_start_seconds": 0,
            "frame_origin": 0,
            "frame_mapping": "output frame n == knockout.mp4 frame n == raw FIGHT frame n",
            "fps": FPS,
            "frame_count": FRAME_COUNT,
            "duration_seconds": "3.5",
            "dimensions": [WIDTH, HEIGHT],
            "input_audio": "none",
            "output_audio": "none; silent review proof",
        },
        "timing_reference": {
            "path": TIMING_FIXTURE_RELATIVE,
            "sha256": fixture_hash,
            "scene_id": fixture["scene"]["scene_id"],
            "reference_events": [
                {
                    "id": "first-right-contact",
                    "observed_frames": [10, 11],
                    "used_contact_frame": 10,
                    "time_seconds": str(Fraction(10, FPS)),
                    "basis": "current work order plus visual inspection of source f8-f12",
                },
                {
                    "id": "left-hook-contact",
                    "observed_frame": 24,
                    "used_contact_frame": 24,
                    "time_seconds": str(Fraction(24, FPS)),
                    "basis": "source-exchange-clock.v1.json and visual inspection",
                },
                {
                    "id": "receiving-head-snap",
                    "observed_frame": 25,
                    "time_seconds": str(Fraction(25, FPS)),
                    "overlay_policy": "left fully unobscured; no recoil accent",
                },
            ],
        },
        "recipe": {
            "generator": Path(__file__).name,
            "generator_sha256": sha256(Path(__file__).resolve()),
            "selected_contact_treatment": args.style,
            "parameters": {
                "supersample": SUPERSAMPLE,
                "contact_anchors_px": {
                    "jab": list(JAB_ANCHOR),
                    "hook": list(HOOK_ANCHOR),
                },
                "broken_ring": {
                    "radius_px": 42,
                    "outer_stroke_px": 11,
                    "core_stroke_px": 4,
                    "jab_arc_degrees": [[108, 148], [160, 205], [218, 260], [270, 285]],
                    "hook_arc_degrees": [[285, 333], [342, 360], [0, 62], [72, 108]],
                    "jab_tick_angles_degrees": [110, 193, 257],
                    "hook_tick_angles_degrees": [291, 4, 76],
                },
                "visual_policy": "keep head-facing sides open; no effect on f25",
            },
            "candidate_contact_treatments": ["ink-burst", "broken-ring", "slash-ticks"],
            "candidate_preview": {
                "path": candidate_sheet_path.relative_to(ROOT).as_posix(),
                "sha256": candidate_sha,
                "layout": "unmodified, A, B, C across each f10 and f24 row; 360x640 per cell",
            },
            "event_layers": layer_records,
            "visual_limits": [
                "No posterization or source-wide color filter",
                "No source-frame hold, speed change, retime, or audio warp",
                "No transformation prelude because the existing stills are not pose-matched to this 105-frame origin",
                "No effect on f25 head snap or on unlisted frames",
                "No injury depiction or force claim",
            ],
        },
        "render": {
            "path": output.name,
            "sha256": sha256(output),
            "video_codec": "libx264",
            "pixel_format": "yuv420p",
            "preset": "medium",
            "crf": 18,
            "ffmpeg_version": run(["ffmpeg", "-version"]).stdout.splitlines()[0],
            "encode_command": encode_command,
        },
        "review": {
            "contact_sheet": {
                "path": contact_sheet_path.relative_to(ROOT).as_posix(),
                "sha256": contact_sha,
                "dimensions": [1440, 2560],
                "aspect_ratio": "9:16",
                "frames": FRAME_CONTACTS,
                "cell_dimensions": [360, 640],
            },
            "detail_crops": {
                "path": detail_crops_path.relative_to(ROOT).as_posix(),
                "sha256": detail_crops_sha,
                "dimensions": [WIDTH, 3 * (544 + 42)],
                "frames": [10, 24, 25],
                "crop_box_source_pixels": [0, 350, WIDTH, 894],
                "purpose": "native-size fight viewport crops; f25 remains the unaccented snap reference",
            },
            "verification_path": verification_path.relative_to(ROOT).as_posix(),
        },
    }
    manifest["recipe"]["layer_alpha_receipts"] = [
        alpha_receipt(ROOT / item["path"]) for item in layer_records
    ]
    write_json(manifest_path, manifest)
    print(
        json.dumps(
            {
                "output": str(output),
                "output_sha256": manifest["render"]["sha256"],
                "manifest": str(manifest_path),
                "contact_sheet": str(contact_sheet_path),
                "detail_crops": str(detail_crops_path),
                "candidate_sheet": str(candidate_sheet_path),
                "frames": FRAME_COUNT,
                "source_frame_origin": 0,
                "source_sha256_after": verification["source_sha256_after"],
                "raw_source_sha256_after": verification["raw_source_sha256_after"],
                "full_decode_returncode": verification["full_decode"]["returncode"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
