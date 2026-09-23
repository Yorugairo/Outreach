"""Render a small, editable, code-native 2D fight proof.

The renderer is intentionally standalone. It authors SVG geometry for every
frame, rasterizes that geometry with CairoSVG, and lets FFmpeg perform only
the final deterministic image-sequence encode. No source art or providers are
needed, so the pose math remains inspectable and repeatable.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any

import cairosvg
from PIL import Image, ImageDraw, ImageFont


WIDTH = 540
HEIGHT = 960
FPS = 24
DURATION_S = 4.0
FRAME_COUNT = int(FPS * DURATION_S)

ROOT = Path(__file__).resolve().parent
FRAMES_DIR = ROOT / "frames"
STYLE_SVG = ROOT / "style-preview.svg"
STYLE_PNG = ROOT / "style-preview.png"
VIDEO_PATH = ROOT / "minimal-2d-fight-proof.mp4"
CONTACT_SHEET = ROOT / "contact-sheet.png"
TIMING_PATH = ROOT / "timing.json"
VALIDATION_PATH = ROOT / "validation.json"

BG_TOP = "#0d1422"
BG_BOTTOM = "#172238"
CAGE = "#2d405e"
CAGE_LIGHT = "#415776"
MAT = "#243451"
MAT_LINE = "#3c5373"
LEFT_SKIN = "#6c3e32"
LEFT_SHADOW = "#432722"
LEFT_HIGHLIGHT = "#955945"
RIGHT_SKIN = "#d59a75"
RIGHT_SHADOW = "#9b604a"
RIGHT_HIGHLIGHT = "#edb18b"
INK = "#111722"
BLACK_SHORTS = "#101318"
WHITE_SHORTS = "#f2efe7"
RED_WRAP = "#e04f55"
BLUE_WRAP = "#47b9df"
GLOVE = "#080c14"
GLOVE_HIGHLIGHT = "#252f3d"
GOLD = "#ffd166"
GOLD_DEEP = "#e9a936"
GOLD_GLOW = "#ffed9b"
WHITE = "#f7fbff"


Point = tuple[float, float]


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def ease_in_out(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def ease_out_cubic(value: float) -> float:
    value = clamp(value)
    return 1.0 - (1.0 - value) ** 3


def ease_in_quad(value: float) -> float:
    value = clamp(value)
    return value * value


def lerp(a: float, b: float, value: float) -> float:
    return a + (b - a) * value


def lerp_point(a: Point, b: Point, value: float) -> Point:
    return (lerp(a[0], b[0], value), lerp(a[1], b[1], value))


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt(value: float) -> str:
    return f"{value:.2f}"


def svg_circle(cx: float, cy: float, radius: float, fill: str, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(radius)}" fill="{fill}" {extra}/>'


def svg_ellipse(cx: float, cy: float, rx: float, ry: float, fill: str, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return (
        f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" '
        f'fill="{fill}" {extra}/>'
    )


def svg_line(points: list[Point], stroke: str, width: float, **attrs: Any) -> str:
    points_text = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return (
        f'<polyline points="{points_text}" fill="none" stroke="{stroke}" '
        f'stroke-width="{fmt(width)}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'
    )


def svg_polygon(points: list[Point], fill: str, **attrs: Any) -> str:
    points_text = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<polygon points="{points_text}" fill="{fill}" {extra}/>'


def svg_path(path: str, fill: str = "none", stroke: str | None = None, stroke_width: float = 0.0, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    stroke_attr = f' stroke="{stroke}" stroke-width="{fmt(stroke_width)}"' if stroke else ""
    return f'<path d="{path}" fill="{fill}"{stroke_attr} {extra}/>'


def pose_at(keys: list[dict[str, Any]], time_s: float) -> dict[str, Any]:
    if time_s <= keys[0]["t"]:
        return dict(keys[0])
    if time_s >= keys[-1]["t"]:
        return dict(keys[-1])
    for first, second in zip(keys, keys[1:]):
        if first["t"] <= time_s <= second["t"]:
            span = second["t"] - first["t"]
            raw = 0.0 if span <= 0 else (time_s - first["t"]) / span
            easing = second.get("ease_from", "smooth")
            if easing == "fast":
                u = ease_out_cubic(raw)
            elif easing == "fall":
                u = ease_in_quad(raw)
            else:
                u = ease_in_out(raw)
            result: dict[str, Any] = {"t": time_s}
            for key, value in first.items():
                if key in {"t", "ease_from"}:
                    continue
                other = second.get(key, value)
                if isinstance(value, tuple):
                    result[key] = lerp_point(value, other, u)
                elif isinstance(value, (int, float)):
                    result[key] = lerp(float(value), float(other), u)
                else:
                    result[key] = value
            return result
    return dict(keys[-1])


LEFT_KEYS: list[dict[str, Any]] = [
    {
        "t": 0.0,
        "root": (185.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (78.0, -130.0),
        "front_fist": (58.0, -208.0),
        "back_elbow": (-74.0, -130.0),
        "back_fist": (-62.0, -210.0),
    },
    {
        "t": 1.15,
        "root": (185.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (78.0, -130.0),
        "front_fist": (58.0, -208.0),
        "back_elbow": (-74.0, -130.0),
        "back_fist": (-62.0, -210.0),
    },
    {
        "t": 1.4,
        "root": (174.0, 601.0),
        "angle": -6.0,
        "scale": 1.0,
        "front_elbow": (62.0, -142.0),
        "front_fist": (42.0, -216.0),
        "back_elbow": (-64.0, -134.0),
        "back_fist": (-50.0, -210.0),
    },
    {
        "t": 1.78,
        "root": (185.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (78.0, -130.0),
        "front_fist": (58.0, -208.0),
        "back_elbow": (-74.0, -130.0),
        "back_fist": (-62.0, -210.0),
        "ease_from": "fast",
    },
    {
        "t": 2.08,
        "root": (180.0, 610.0),
        "angle": -2.0,
        "scale": 1.0,
        "front_elbow": (78.0, -130.0),
        "front_fist": (58.0, -208.0),
        "back_elbow": (-74.0, -130.0),
        "back_fist": (-62.0, -210.0),
        "ease_from": "fast",
    },
    {
        "t": 2.42,
        "root": (245.0, 690.0),
        "angle": -28.0,
        "scale": 0.95,
        "front_elbow": (80.0, -125.0),
        "front_fist": (53.0, -190.0),
        "back_elbow": (-72.0, -120.0),
        "back_fist": (-54.0, -198.0),
        "ease_from": "fall",
    },
    {
        "t": 2.82,
        "root": (285.0, 755.0),
        "angle": -55.0,
        "scale": 0.88,
        "front_elbow": (82.0, -118.0),
        "front_fist": (45.0, -180.0),
        "back_elbow": (-70.0, -115.0),
        "back_fist": (-52.0, -190.0),
        "ease_from": "fall",
    },
    {
        "t": 3.3,
        "root": (315.0, 810.0),
        "angle": -72.0,
        "scale": 0.78,
        "front_elbow": (85.0, -112.0),
        "front_fist": (44.0, -176.0),
        "back_elbow": (-72.0, -112.0),
        "back_fist": (-50.0, -188.0),
        "ease_from": "fall",
    },
    {
        "t": 3.65,
        "root": (320.0, 830.0),
        "angle": -84.0,
        "scale": 0.70,
        "front_elbow": (85.0, -112.0),
        "front_fist": (44.0, -176.0),
        "back_elbow": (-72.0, -112.0),
        "back_fist": (-50.0, -188.0),
        "ease_from": "fall",
    },
    {
        "t": 4.0,
        "root": (320.0, 830.0),
        "angle": -84.0,
        "scale": 0.70,
        "front_elbow": (85.0, -112.0),
        "front_fist": (44.0, -176.0),
        "back_elbow": (-72.0, -112.0),
        "back_fist": (-50.0, -188.0),
        "ease_from": "smooth",
    },
]


# Facing left, the right fighter's front arm is his right-hand straight;
# his back arm is authored as the left-hand follow-up hook.
RIGHT_KEYS: list[dict[str, Any]] = [
    {
        "t": 0.0,
        "root": (380.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (74.0, -130.0),
        "back_fist": (62.0, -210.0),
    },
    {
        "t": 0.74,
        "root": (380.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-75.0, -92.0),
        "front_fist": (-82.0, -150.0),
        "back_elbow": (74.0, -130.0),
        "back_fist": (62.0, -210.0),
        "ease_from": "smooth",
    },
    {
        "t": 1.12,
        "root": (380.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-100.0, -160.0),
        "front_fist": (-195.0, -280.0),
        "back_elbow": (72.0, -132.0),
        "back_fist": (60.0, -210.0),
        "ease_from": "fast",
    },
    {
        "t": 1.42,
        "root": (380.0, 604.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (74.0, -130.0),
        "back_fist": (62.0, -210.0),
        "ease_from": "fast",
    },
    {
        "t": 1.78,
        "root": (380.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (92.0, -72.0),
        "back_fist": (38.0, -22.0),
        "ease_from": "smooth",
    },
    {
        "t": 2.12,
        "root": (380.0, 600.0),
        "angle": 2.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (-82.0, -120.0),
        "back_fist": (-215.0, -275.0),
        "ease_from": "fast",
    },
    {
        "t": 2.48,
        "root": (380.0, 604.0),
        "angle": 5.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (-90.0, -106.0),
        "back_fist": (-192.0, -222.0),
        "ease_from": "fast",
    },
    {
        "t": 2.78,
        "root": (380.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (74.0, -130.0),
        "back_fist": (62.0, -210.0),
        "ease_from": "smooth",
    },
    {
        "t": 4.0,
        "root": (380.0, 600.0),
        "angle": 0.0,
        "scale": 1.0,
        "front_elbow": (-74.0, -130.0),
        "front_fist": (-58.0, -208.0),
        "back_elbow": (74.0, -130.0),
        "back_fist": (62.0, -210.0),
    },
]


def rotate_local(point: Point, angle_deg: float) -> Point:
    radians = math.radians(angle_deg)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return (point[0] * cosine - point[1] * sine, point[0] * sine + point[1] * cosine)


def world_point(pose: dict[str, Any], point: Point) -> Point:
    rotated = rotate_local(point, float(pose["angle"]))
    scale = float(pose.get("scale", 1.0))
    return (pose["root"][0] + rotated[0] * scale, pose["root"][1] + rotated[1] * scale)


def anchors_for(pose: dict[str, Any]) -> dict[str, Point]:
    return {
        "head": world_point(pose, (0.0, -285.0)),
        "front_fist": world_point(pose, pose["front_fist"]),
        "back_fist": world_point(pose, pose["back_fist"]),
        "root": pose["root"],
    }


def draw_background(parts: list[str]) -> None:
    parts.append(
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{BG_TOP}"/><stop offset="100%" stop-color="{BG_BOTTOM}"/>'
        '</linearGradient><radialGradient id="spot" cx="50%" cy="38%" r="63%">'
        '<stop offset="0%" stop-color="#31486d" stop-opacity="0.45"/>'
        '<stop offset="100%" stop-color="#0d1422" stop-opacity="0"/></radialGradient></defs>'
    )
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bg)"/>')
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#spot)"/>')
    parts.append('<g opacity="0.84">')
    parts.append(f'<rect x="24" y="174" width="492" height="678" rx="18" fill="none" stroke="{CAGE}" stroke-width="7"/>')
    for x in (72, 168, 270, 372, 468):
        parts.append(svg_line([(x, 174), (x, 852)], CAGE, 3, opacity="0.65"))
    for y in (270, 392, 520, 650, 770):
        parts.append(svg_line([(25, y), (515, y)], CAGE, 2, opacity="0.42"))
    parts.append(svg_line([(24, 174), (516, 174)], CAGE_LIGHT, 9, opacity="0.7"))
    parts.append(svg_line([(24, 852), (516, 852)], CAGE_LIGHT, 10, opacity="0.9"))
    parts.append('</g>')
    parts.append(svg_ellipse(270, 838, 244, 56, MAT, opacity="0.98"))
    parts.append(svg_ellipse(270, 838, 187, 39, "none", stroke=MAT_LINE, stroke_width="3", opacity="0.9"))
    parts.append(svg_line([(42, 838), (498, 838)], MAT_LINE, 3, opacity="0.85"))
    parts.append(svg_line([(270, 805), (270, 871)], MAT_LINE, 3, opacity="0.7"))
    parts.append(svg_ellipse(190, 831, 77, 18, "#08101d", opacity="0.65"))
    parts.append(svg_ellipse(366, 831, 77, 18, "#08101d", opacity="0.65"))


def draw_limb(parts: list[str], points: list[Point], skin: str, shadow: str, width: float) -> None:
    parts.append(svg_line(points, shadow, width + 10))
    parts.append(svg_line(points, skin, width))


def draw_wrap(parts: list[str], elbow: Point, fist: Point, color: str) -> None:
    dx = fist[0] - elbow[0]
    dy = fist[1] - elbow[1]
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    start = (fist[0] - ux * 35.0, fist[1] - uy * 35.0)
    end = (fist[0] - ux * 16.0, fist[1] - uy * 16.0)
    parts.append(svg_line([start, end], color, 23))
    parts.append(svg_line([start, end], WHITE, 5, opacity="0.25"))


def draw_fighter(parts: list[str], pose: dict[str, Any], *, facing: int, skin: str, shadow: str, highlight: str, shorts: str, wrap: str, left: bool) -> dict[str, Point]:
    root_x, root_y = pose["root"]
    angle = pose["angle"]
    scale = float(pose.get("scale", 1.0))
    parts.append(f'<g transform="translate({fmt(root_x)},{fmt(root_y)}) rotate({fmt(angle)}) scale({fmt(scale)})">')
    # Legs are deliberately broad filled strokes, so the graphic reads as a body silhouette.
    rear_hip = (-23.0, -2.0)
    rear_knee = (-48.0, 112.0)
    rear_foot = (-64.0, 230.0)
    front_hip = (23.0, -2.0)
    front_knee = (48.0, 110.0)
    front_foot = (64.0, 230.0)
    draw_limb(parts, [rear_hip, rear_knee, rear_foot], skin, shadow, 58.0)
    draw_limb(parts, [front_hip, front_knee, front_foot], skin, shadow, 64.0)
    parts.append(svg_circle(rear_foot[0], rear_foot[1], 31.0, INK, opacity="0.95"))
    parts.append(svg_circle(front_foot[0], front_foot[1], 33.0, INK, opacity="0.95"))

    # Torso and shorts.
    torso = [(-45.0, -183.0), (45.0, -183.0), (57.0, -9.0), (22.0, 30.0), (-22.0, 30.0), (-57.0, -9.0)]
    parts.append(svg_polygon(torso, shadow))
    parts.append(svg_polygon([(-41.0, -180.0), (41.0, -180.0), (47.0, -25.0), (-47.0, -25.0)], skin))
    parts.append(svg_polygon([(-47.0, -29.0), (47.0, -29.0), (43.0, 55.0), (8.0, 72.0), (-8.0, 72.0), (-43.0, 55.0)], shorts))
    parts.append(svg_line([(-35.0, -30.0), (35.0, -30.0)], INK if shorts == WHITE_SHORTS else "#2b2f36", 5, opacity="0.7"))
    parts.append(svg_polygon([(-4.0, -172.0), (15.0, -172.0), (28.0, -42.0), (12.0, -34.0)], highlight, opacity="0.25"))

    # Rear arm, then the near/front arm.
    rear_shoulder = (-42.0, -164.0)
    front_shoulder = (42.0, -164.0)
    if facing < 0:
        rear_shoulder, front_shoulder = front_shoulder, rear_shoulder
    draw_limb(parts, [rear_shoulder, pose["back_elbow"], pose["back_fist"]], skin, shadow, 49.0)
    draw_limb(parts, [front_shoulder, pose["front_elbow"], pose["front_fist"]], skin, shadow, 55.0)
    draw_wrap(parts, pose["back_elbow"], pose["back_fist"], wrap)
    draw_wrap(parts, pose["front_elbow"], pose["front_fist"], wrap)
    parts.append(svg_circle(pose["back_fist"][0], pose["back_fist"][1], 31.0, INK))
    parts.append(svg_circle(pose["back_fist"][0], pose["back_fist"][1] - 3.0, 26.0, GLOVE))
    parts.append(svg_circle(pose["front_fist"][0], pose["front_fist"][1], 34.0, INK))
    parts.append(svg_circle(pose["front_fist"][0], pose["front_fist"][1] - 3.0, 29.0, GLOVE))
    parts.append(svg_ellipse(pose["front_fist"][0] - 8.0, pose["front_fist"][1] - 12.0, 10.0, 5.0, GLOVE_HIGHLIGHT, opacity="0.7"))

    # Oversized head, simple hair/beard and face markers.
    head_y = -285.0
    parts.append(svg_ellipse(0.0, -225.0, 25.0, 39.0, shadow))
    parts.append(svg_ellipse(0.0, -229.0, 21.0, 35.0, skin))
    parts.append(svg_circle(0.0, head_y, 50.0, shadow))
    parts.append(svg_circle(0.0, head_y - 3.0, 47.0, skin))
    if left:
        parts.append(svg_path("M -45,-300 Q -34,-347 0,-337 Q 39,-345 46,-300 L 35,-286 Q 4,-305 -31,-286 Z", INK))
    # Both fighters carry a short beard marker; the right fighter is bald.
    parts.append(svg_path("M -33,-260 Q 0,-232 34,-261 Q 28,-220 0,-215 Q -28,-220 -33,-260 Z", INK))
    eye_x = facing * 17.0
    parts.append(svg_ellipse(eye_x, -295.0, 6.0, 8.0, WHITE))
    parts.append(svg_circle(eye_x + facing * 2.0, -295.0, 3.0, INK))
    parts.append(svg_line([(eye_x - facing * 13.0, -309.0), (eye_x + facing * 8.0, -306.0)], INK, 6))
    parts.append(svg_path(f"M {fmt(facing * 16.0)},-282 Q {fmt(facing * 29.0)},-275 {fmt(facing * 17.0)},-268", fill="none", stroke=INK, stroke_width=4))
    parts.append(svg_circle(-facing * 44.0, -283.0, 10.0, skin, opacity="0.85"))
    parts.append('</g>')
    return anchors_for(pose)


def draw_impact(parts: list[str], center: Point, progress: float, color: str = GOLD) -> None:
    progress = clamp(progress)
    if progress <= 0.0:
        return
    intensity = math.sin(math.pi * progress)
    cx, cy = center
    radius = 26.0 + 42.0 * progress
    parts.append(svg_circle(cx, cy, radius, "none", stroke=color, stroke_width=7.0, opacity=f"{0.76 * intensity:.3f}"))
    parts.append(svg_circle(cx, cy, radius * 0.55, "none", stroke=WHITE, stroke_width=3.0, opacity=f"{0.62 * intensity:.3f}"))
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        inner = radius + 9.0
        outer = inner + 16.0 * intensity
        parts.append(
            svg_line(
                [(cx + math.cos(radians) * inner, cy + math.sin(radians) * inner),
                 (cx + math.cos(radians) * outer, cy + math.sin(radians) * outer)],
                color,
                5.0,
                opacity=f"{0.86 * intensity:.3f}",
            )
        )


def draw_brain(parts: list[str], time_s: float) -> None:
    # The brain starts after the verified glove-to-face contact at 1.12 s.
    start = 1.24
    end = 1.82
    if not start <= time_s <= end:
        return
    raw = (time_s - start) / (end - start)
    travel = ease_out_cubic(raw)
    fade = min(1.0, raw * 6.0, (1.0 - raw) * 5.0)
    x = lerp(157.0, 88.0, travel) + math.sin(raw * math.pi) * 10.0
    y = lerp(326.0, 236.0, travel) - math.sin(raw * math.pi) * 15.0
    scale = 0.76 + 0.12 * math.sin(raw * math.pi)
    parts.append(f'<g transform="translate({fmt(x)},{fmt(y)}) scale({fmt(scale)})" opacity="{fade:.3f}">')
    parts.append(svg_circle(0.0, 0.0, 35.0, GOLD_GLOW, opacity="0.16"))
    parts.append(svg_path("M -27,13 C -39,1 -35,-20 -17,-25 C -13,-42 10,-40 16,-26 C 34,-27 42,-8 31,5 C 39,23 17,35 2,27 C -11,39 -31,31 -27,13 Z", GOLD, GOLD_DEEP, 5.0))
    parts.append(svg_path("M -15,-22 C -25,-10 -7,-9 -15,4 C -22,17 -5,11 -5,27 M 7,-27 C -2,-14 17,-13 8,0 C 1,11 17,10 12,25 M 25,-16 C 14,-6 28,-1 18,10", fill="none", stroke=GOLD_DEEP, stroke_width=5.0, opacity="0.95"))
    parts.append(svg_line([(-51.0, -3.0), (-66.0, -12.0)], GOLD_GLOW, 5.0))
    parts.append(svg_line([(47.0, 10.0), (61.0, 18.0)], GOLD_GLOW, 5.0))
    parts.append(svg_line([(-2.0, -50.0), (-2.0, -66.0)], GOLD_GLOW, 5.0))
    parts.append('</g>')


def draw_ground_dust(parts: list[str], time_s: float, fall_anchor: Point) -> None:
    if time_s < 3.0:
        return
    progress = clamp((time_s - 3.0) / 0.8)
    alpha = 0.62 * (1.0 - 0.4 * progress)
    x, _ = fall_anchor
    y = 826.0
    parts.append(svg_ellipse(x + 30.0, y, 52.0 + progress * 22.0, 10.0, GOLD_GLOW, opacity=f"{alpha * 0.18:.3f}"))
    parts.append(svg_line([(x - 5.0, y), (x - 33.0 - 20.0 * progress, y - 25.0)], GOLD_GLOW, 4.0, opacity=f"{alpha:.3f}"))
    parts.append(svg_line([(x + 42.0, y - 2.0), (x + 78.0 + 18.0 * progress, y - 18.0)], GOLD_GLOW, 4.0, opacity=f"{alpha * 0.82:.3f}"))


def render_svg(time_s: float) -> str:
    left_pose = pose_at(LEFT_KEYS, time_s)
    right_pose = pose_at(RIGHT_KEYS, time_s)
    parts: list[str] = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">']
    draw_background(parts)
    # The dark/red fighter is always painted first so the blue fighter's right
    # straight and left hook remain visibly on top at their two contacts.
    left_anchor = draw_fighter(parts, left_pose, facing=1, skin=LEFT_SKIN, shadow=LEFT_SHADOW, highlight=LEFT_HIGHLIGHT, shorts=BLACK_SHORTS, wrap=RED_WRAP, left=True)
    right_anchor = draw_fighter(parts, right_pose, facing=-1, skin=RIGHT_SKIN, shadow=RIGHT_SHADOW, highlight=RIGHT_HIGHLIGHT, shorts=WHITE_SHORTS, wrap=BLUE_WRAP, left=False)

    if 0.98 <= time_s <= 1.38:
        impact_progress = clamp((time_s - 0.98) / 0.20) if time_s < 1.18 else clamp((1.38 - time_s) / 0.32)
        draw_impact(parts, left_anchor["head"], impact_progress)
    if 1.96 <= time_s <= 2.48:
        hook_progress = clamp((time_s - 1.96) / 0.16) if time_s < 2.12 else clamp((2.48 - time_s) / 0.36)
        draw_impact(parts, left_anchor["head"], hook_progress, color="#ff9b54")
    draw_brain(parts, time_s)
    draw_ground_dust(parts, time_s, left_anchor["root"])
    parts.append('</svg>')
    return "".join(parts)


def write_style_preview() -> None:
    # A recoil beat keeps the character silhouettes and the brain gag readable
    # in the first style gate; the contact ring remains authored in the final
    # motion and is represented in the contact-sheet review frames.
    svg = render_svg(1.46)
    STYLE_SVG.write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(STYLE_PNG), output_width=WIDTH, output_height=HEIGHT)


def render_animation() -> None:
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for frame_index in range(FRAME_COUNT):
        time_s = frame_index / FPS
        svg = render_svg(time_s)
        output_path = FRAMES_DIR / f"frame-{frame_index:04d}.png"
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(output_path), output_width=WIDTH, output_height=HEIGHT)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to encode the proof")
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAMES_DIR / "frame-%04d.png"),
        "-frames:v",
        str(FRAME_COUNT),
        "-c:v",
        "libx264",
        "-crf",
        "18",
        "-preset",
        "medium",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(VIDEO_PATH),
    ]
    subprocess.run(command, check=True)


def make_contact_sheet() -> None:
    sample_times = [0.0, 0.5, 0.96, 1.20, 1.50, 1.78, 2.08, 2.38, 2.80, 3.20, 3.62, 3.96]
    cols = 4
    rows = 3
    cell_w, cell_h = 180, 320
    label_h = 28
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), "#0b1120")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    labels = {
        0.0: "guard",
        0.5: "anticipation",
        0.96: "punch launch",
        1.20: "CONTACT / brain",
        1.50: "recoil",
        1.78: "hook load",
        2.08: "RIGHT LEFT-HOOK",
        2.38: "follow-through",
        2.80: "fall begins",
        3.20: "fall",
        3.62: "near-horizontal",
        3.96: "grounded hold",
    }
    for index, time_s in enumerate(sample_times):
        frame_index = min(FRAME_COUNT - 1, round(time_s * FPS))
        frame_path = FRAMES_DIR / f"frame-{frame_index:04d}.png"
        with Image.open(frame_path) as frame:
            frame = frame.convert("RGB")
            frame.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + (cell_w - frame.width) // 2
            y = (index // cols) * (cell_h + label_h) + label_h
            sheet.paste(frame, (x, y))
        label = f"{time_s:0.2f}s  {labels[time_s]}"
        draw.text(((index % cols) * cell_w + 6, (index // cols) * (cell_h + label_h) + 6), label, fill=WHITE, font=font)
    sheet.save(CONTACT_SHEET, format="PNG", optimize=True)


def write_timing() -> None:
    contact_t = 27.0 / FPS
    left_contact = anchors_for(pose_at(LEFT_KEYS, contact_t))
    right_contact = anchors_for(pose_at(RIGHT_KEYS, contact_t))
    glove_center = right_contact["front_fist"]
    receiver_head = left_contact["head"]
    contact_distance = math.hypot(glove_center[0] - receiver_head[0], glove_center[1] - receiver_head[1])
    hook_t = 51.0 / FPS
    left_hook = anchors_for(pose_at(LEFT_KEYS, hook_t))
    right_hook = anchors_for(pose_at(RIGHT_KEYS, hook_t))
    hook_glove_center = right_hook["back_fist"]
    hook_receiver_head = left_hook["head"]
    hook_distance = math.hypot(hook_glove_center[0] - hook_receiver_head[0], hook_glove_center[1] - hook_receiver_head[1])
    fall_t = 3.65
    fall_pose = pose_at(LEFT_KEYS, fall_t)
    fall_anchor = anchors_for(fall_pose)
    fall_head_radius = 50.0 * float(fall_pose.get("scale", 1.0))
    mat_y = 838.0
    fall_head_to_mat = abs(mat_y - fall_anchor["head"][1])
    timing = {
        "schema_version": "minimal_2d_fight_timing.v1",
        "project": "knockout-brain-matchcut-001",
        "variant": "minimal-2d",
        "renderer": "render_minimal_2d.py",
        "style": "code-native-flat-graphic",
        "canvas": {"width": WIDTH, "height": HEIGHT, "fps": FPS, "duration_s": DURATION_S, "frame_count": FRAME_COUNT},
        "characters": {
            "left": "dark skin, short black hair, beard, black shorts, red wraps",
            "right": "light skin, bald, beard, white shorts, blue wraps",
        },
        "beats": [
            {"id": "guard_anticipation", "start_s": 0.0, "end_s": 0.74, "keyframe": 0, "description": "Both fighters hold broad readable guards; right shoulder coils."},
            {"id": "contact", "start_s": 0.98, "end_s": 1.20, "keyframe": 27, "description": "The right bald/blue fighter's right-hand straight reaches the left face; impact ring marks the clean contact."},
            {"id": "recoil", "start_s": 1.20, "end_s": 1.82, "keyframe": 36, "description": "The left dark/red fighter's head and torso recoil while feet stay planted; one symbolic golden cartoon brain exits on the visible recoil only."},
            {"id": "followup_right_left_hook", "start_s": 1.78, "end_s": 2.48, "keyframe": 51, "description": "The same right fighter's left hook crosses into the left jaw with a warm impact accent."},
            {"id": "fall", "start_s": 2.48, "end_s": 4.0, "keyframe": 78, "description": "The left dark/red fighter continues rotating and descending until the body reaches the floor plane; the right fighter stays standing."},
        ],
        "brain_visibility": {"start_s": 1.24, "end_s": 1.82, "rule": "visible only after glove-face contact and during head recoil; no skull or gore"},
        "contact_geometry": {
            "sample_s": contact_t,
            "frame": 27,
            "attacker": "right_fighter_right_glove",
            "receiver": "left_head",
            "glove_center_px": [round(glove_center[0], 2), round(glove_center[1], 2)],
            "receiver_head_center_px": [round(receiver_head[0], 2), round(receiver_head[1], 2)],
            "center_distance_px": round(contact_distance, 2),
            "receiver_head_radius_px": 50,
            "passes": contact_distance <= 20.0,
        },
        "followup_geometry": {
            "sample_s": hook_t,
            "frame": 51,
            "attacker": "right_fighter_left_glove",
            "receiver": "left_head",
            "glove_center_px": [round(hook_glove_center[0], 2), round(hook_glove_center[1], 2)],
            "receiver_head_center_px": [round(hook_receiver_head[0], 2), round(hook_receiver_head[1], 2)],
            "center_distance_px": round(hook_distance, 2),
            "receiver_head_radius_px": 50,
            "passes": hook_distance <= 20.0,
        },
        "fall_geometry": {
            "sample_s": fall_t,
            "frame": round(fall_t * FPS),
            "fighter": "left_dark_red",
            "head_center_px": [round(fall_anchor["head"][0], 2), round(fall_anchor["head"][1], 2)],
            "mat_y_px": mat_y,
            "head_radius_px": round(fall_head_radius, 2),
            "head_to_mat_px": round(fall_head_to_mat, 2),
            "body_angle_deg": round(float(fall_pose["angle"]), 2),
            "scale": round(float(fall_pose.get("scale", 1.0)), 3),
            "near_horizontal": abs(abs(float(fall_pose["angle"])) - 90.0) <= 12.0,
            "floor_contact_passes": fall_head_to_mat <= fall_head_radius * 1.1,
        },
        "review_artifacts": {"style_preview": STYLE_PNG.name, "contact_sheet": CONTACT_SHEET.name, "video": VIDEO_PATH.name},
    }
    TIMING_PATH.write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")


def run_validation() -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("ffprobe and ffmpeg are required for validation")
    probe_command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,nb_frames,duration,pix_fmt,codec_name",
        "-of",
        "json",
        str(VIDEO_PATH),
    ]
    probe = subprocess.run(probe_command, check=True, capture_output=True, text=True)
    decoded = subprocess.run([ffmpeg, "-v", "error", "-i", str(VIDEO_PATH), "-f", "null", "-"], capture_output=True, text=True)
    if decoded.returncode != 0:
        raise RuntimeError(f"ffmpeg decode failed: {decoded.stderr.strip()}")
    metadata = json.loads(probe.stdout)
    stream = metadata["streams"][0]
    result = {
        "status": "PASS",
        "video": VIDEO_PATH.name,
        "probe": stream,
        "decode": "PASS",
        "checks": {
            "dimensions": [stream.get("width"), stream.get("height")] == [WIDTH, HEIGHT],
            "frame_rate": stream.get("r_frame_rate") == f"{FPS}/1",
            "frame_count": int(stream.get("nb_frames", 0)) == FRAME_COUNT,
            "duration_s": abs(float(stream.get("duration", 0.0)) - DURATION_S) <= 1.0 / FPS,
        },
    }
    if not all(result["checks"].values()):
        result["status"] = "FAIL"
        raise RuntimeError(json.dumps(result, indent=2))
    VALIDATION_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", action="store_true", help="write the first editable style still")
    parser.add_argument("--render", action="store_true", help="render the 96-frame MP4 proof")
    parser.add_argument("--contact-sheet", action="store_true", help="write the labeled contact sheet")
    parser.add_argument("--timing", action="store_true", help="write timing.json")
    parser.add_argument("--validate", action="store_true", help="ffprobe and fully decode the MP4")
    parser.add_argument("--all", action="store_true", help="run style, render, timing, contact sheet, validation")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error("choose --style, --render, --contact-sheet, --timing, --validate, or --all")
    if args.style or args.all:
        write_style_preview()
    if args.render or args.all:
        render_animation()
    if args.timing or args.all:
        write_timing()
    if args.contact_sheet or args.all:
        make_contact_sheet()
    if args.validate or args.all:
        result = run_validation()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
