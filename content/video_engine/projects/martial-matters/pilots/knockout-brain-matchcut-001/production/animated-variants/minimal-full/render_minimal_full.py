"""Render the private-review full-cut minimalist animation variant.

This is a standalone, code-native flat-graphic renderer.  It reuses the
already-reviewed minimal-2d proof only for the opening/replay silhouette, then
authors the interview and Henderson/Bisping match as new SVG geometry.  SVG is
rasterised to a numbered PNG sequence only as the final render step; no source
footage, provider, or image filter is involved.
"""

from __future__ import annotations

import argparse
import importlib.util
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
NOMINAL_DURATION_S = 20.933333
FRAME_COUNT = math.ceil(NOMINAL_DURATION_S * FPS)
REACTION_START = 8.766667
REACTION_DURATION = 2.3
REACTION_END = REACTION_START + REACTION_DURATION

ROOT = Path(__file__).resolve().parent
PRODUCTION = ROOT.parents[1]
PROOF_PATH = ROOT.parent / "minimal-2d" / "render_minimal_2d.py"
FRAMES_DIR = ROOT / "frames"
VIDEO_PATH = ROOT / "minimal-full-review-roughcut.mp4"
CONTACT_SHEET = ROOT / "contact-sheet.png"
STYLE_SVG = ROOT / "style-preview.svg"
STYLE_PNG = ROOT / "style-preview.png"
TIMELINE_PATH = ROOT / "timeline.json"
VALIDATION_PATH = ROOT / "validation.json"
AUDIO_PATH = ROOT / "audio" / "minimal-full-review-audio.wav"
AUDIO_MANIFEST = ROOT / "audio" / "audio-manifest.json"

MASTER_AUDIO = PRODUCTION / "audio" / "master-v11.wav"
REACTION_AUDIO = PRODUCTION / "animated-variants" / "audio" / "reaction-duo.wav"
CONTINUOUS_BED = PRODUCTION / "edit-v9" / "continuous-bed.wav"

BG_TOP = "#0d1422"
BG_BOTTOM = "#172238"
CAGE = "#2d405e"
CAGE_LIGHT = "#415776"
MAT = "#243451"
MAT_LINE = "#3c5373"
INK = "#111722"
GLOVE = "#080c14"
GLOVE_HIGHLIGHT = "#252f3d"
WHITE = "#f7fbff"
GOLD = "#ffd166"
GOLD_DEEP = "#e9a936"
RED_WRAP = "#e04f55"
BLUE_WRAP = "#47b9df"

Point = tuple[float, float]


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def smooth(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def fast_out(value: float) -> float:
    value = clamp(value)
    return 1.0 - (1.0 - value) ** 3


def fall_in(value: float) -> float:
    value = clamp(value)
    return value * value


def lerp(a: float, b: float, value: float) -> float:
    return a + (b - a) * value


def lerp_point(a: Point, b: Point, value: float) -> Point:
    return (lerp(a[0], b[0], value), lerp(a[1], b[1], value))


def fmt(value: float) -> str:
    return f"{value:.2f}"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def svg_text(x: float, y: float, text: str, size: float, fill: str = WHITE, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<text x="{fmt(x)}" y="{fmt(y)}" fill="{fill}" font-family="Arial, sans-serif" font-size="{fmt(size)}" {extra}>{esc(text)}</text>'


def svg_rect(x: float, y: float, width: float, height: float, fill: str, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="{fmt(height)}" fill="{fill}" {extra}/>'


def svg_circle(cx: float, cy: float, radius: float, fill: str, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(radius)}" fill="{fill}" {extra}/>'


def svg_ellipse(cx: float, cy: float, rx: float, ry: float, fill: str, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy)}" rx="{fmt(rx)}" ry="{fmt(ry)}" fill="{fill}" {extra}/>'


def svg_line(points: list[Point], stroke: str, width: float, **attrs: Any) -> str:
    points_text = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<polyline points="{points_text}" fill="none" stroke="{stroke}" stroke-width="{fmt(width)}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def svg_polygon(points: list[Point], fill: str, **attrs: Any) -> str:
    points_text = " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points)
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    return f'<polygon points="{points_text}" fill="{fill}" {extra}/>'


def svg_path(path: str, fill: str = "none", stroke: str | None = None, stroke_width: float = 0.0, **attrs: Any) -> str:
    extra = " ".join(f'{key.replace("_", "-")}="{esc(str(value))}"' for key, value in attrs.items())
    stroke_attr = f' stroke="{stroke}" stroke-width="{fmt(stroke_width)}"' if stroke else ""
    return f'<path d="{path}" fill="{fill}"{stroke_attr} {extra}/>'


def proof_module() -> Any:
    spec = importlib.util.spec_from_file_location("minimal_2d_proof_for_full", PROOF_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load proof renderer: {PROOF_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PROOF = proof_module()


def arena_background(parts: list[str], *, warm: bool = False) -> None:
    top = "#251d24" if warm else BG_TOP
    bottom = "#15111c" if warm else BG_BOTTOM
    parts.append(
        '<defs><linearGradient id="arena-bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{top}"/><stop offset="100%" stop-color="{bottom}"/>'
        '</linearGradient></defs>'
    )
    parts.append(svg_rect(0, 0, WIDTH, HEIGHT, "url(#arena-bg)"))
    parts.append(svg_rect(24, 174, 492, 678, "none", rx="18", stroke=CAGE, stroke_width="7", opacity="0.84"))
    for x in (72, 168, 270, 372, 468):
        parts.append(svg_line([(x, 174), (x, 852)], CAGE, 3, opacity="0.62"))
    for y in (270, 392, 520, 650, 770):
        parts.append(svg_line([(25, y), (515, y)], CAGE, 2, opacity="0.42"))
    parts.append(svg_line([(24, 174), (516, 174)], CAGE_LIGHT, 9, opacity="0.7"))
    parts.append(svg_line([(24, 852), (516, 852)], CAGE_LIGHT, 10, opacity="0.9"))
    parts.append(svg_ellipse(270, 838, 244, 56, MAT, opacity="0.98"))
    parts.append(svg_ellipse(270, 838, 187, 39, "none", stroke=MAT_LINE, stroke_width="3", opacity="0.9"))
    parts.append(svg_line([(42, 838), (498, 838)], MAT_LINE, 3, opacity="0.85"))
    parts.append(svg_line([(270, 805), (270, 871)], MAT_LINE, 3, opacity="0.7"))


def badge(parts: list[str], text: str = "ANIMATED PARODY") -> None:
    parts.append(svg_rect(28, 32, 194, 34, GOLD, rx="17", opacity="0.96"))
    parts.append(svg_text(125, 55, text, 14, INK, text_anchor="middle", font_weight="700", letter_spacing="1.2"))


def lower_label(parts: list[str], line1: str, line2: str = "", *, y: float = 876.0, color: str = WHITE) -> None:
    parts.append(svg_rect(28, y - 38, 484, 72, "#0a0f19", rx="12", opacity="0.91"))
    parts.append(svg_text(48, y - 11, line1, 18, color, font_weight="700", letter_spacing="0.8"))
    if line2:
        parts.append(svg_text(48, y + 15, line2, 13, "#b8c7dc", letter_spacing="0.5"))


def title_overlay(parts: list[str], title: str, subtitle: str = "", *, y: float = 112.0) -> None:
    parts.append(svg_text(270, y, title, 27, WHITE, text_anchor="middle", font_weight="700", letter_spacing="1.0"))
    if subtitle:
        parts.append(svg_text(270, y + 29, subtitle, 14, "#a7b7ce", text_anchor="middle", letter_spacing="0.8"))


def wrap_svg(svg: str, additions: list[str]) -> str:
    return svg.replace("</svg>", "".join(additions) + "</svg>")


def opening_local_time(global_t: float) -> float:
    """Map v11 opening time to the proof without freezing before the filed beat."""
    if global_t < 1.197:
        return lerp(0.0, 0.4, global_t / 1.197)
    if global_t < 2.35:
        return 0.4
    if global_t < 4.1:
        return lerp(0.4, 1.125, (global_t - 2.35) / (4.1 - 2.35))
    return clamp(1.125 + (global_t - 4.1), 0.0, 4.0)


def opening_caption(global_t: float) -> str:
    if 0.0 <= global_t < 1.197:
        return "NO CHARGES FILED."
    if 1.197 <= global_t < 2.199:
        return "THEN SHARAF DELIVERED A"
    if 2.199 <= global_t < 3.5:
        return "ONE-PUNCH VERDICT."
    return ""


def opening_frame(global_t: float) -> str:
    # Preserve v11's freeze, power flash, effect lead, contact and complete
    # follow-through while using the reviewed proof's analytic poses.
    local_t = opening_local_time(global_t)
    svg = PROOF.render_svg(local_t)
    additions: list[str] = []
    badge(additions)
    caption = opening_caption(global_t)
    if caption:
        additions.append(svg_text(270, 130, caption, 25 if global_t < 1.197 else 22, GOLD, text_anchor="middle", font_weight="700", letter_spacing="1.2"))
    if global_t < 1.197:
        additions.append(svg_rect(0, 0, WIDTH, HEIGHT, "#050912", opacity="0.15"))
    elif global_t < 2.35:
        flash = 0.78 * (1.0 - clamp((global_t - 2.199) / 0.151))
        additions.append(svg_rect(0, 0, WIDTH, HEIGHT, "#fff4cc", opacity=f"{flash:.3f}"))
    return wrap_svg(svg, additions)


def draw_avatar(parts: list[str], cx: float, cy: float, *, skin: str, hair: str, shirt: str, mouth_open: bool, label: str = "") -> None:
    parts.append(svg_ellipse(cx, cy + 126, 88, 20, "#080d17", opacity="0.45"))
    parts.append(svg_rect(cx - 72, cy + 28, 144, 132, shirt, rx="30"))
    parts.append(svg_circle(cx, cy, 64, skin))
    if hair == "dark_short":
        parts.append(svg_path(f"M {fmt(cx-60)},{fmt(cy-16)} Q {fmt(cx-45)},{fmt(cy-76)} {fmt(cx)},{fmt(cy-69)} Q {fmt(cx+51)},{fmt(cy-79)} {fmt(cx+62)},{fmt(cy-16)} L {fmt(cx+42)},{fmt(cy-27)} Q {fmt(cx)},{fmt(cy-7)} {fmt(cx-42)},{fmt(cy-28)} Z", INK))
    elif hair == "buzz":
        parts.append(svg_path(f"M {fmt(cx-54)},{fmt(cy-28)} Q {fmt(cx)},{fmt(cy-72)} {fmt(cx+54)},{fmt(cy-28)} L {fmt(cx+43)},{fmt(cy-8)} Q {fmt(cx)},{fmt(cy-30)} {fmt(cx-43)},{fmt(cy-9)} Z", "#6f7783"))
    parts.append(svg_circle(cx - 21, cy - 2, 7, WHITE))
    parts.append(svg_circle(cx + 21, cy - 2, 7, WHITE))
    parts.append(svg_circle(cx - 20, cy - 2, 3, INK))
    parts.append(svg_circle(cx + 20, cy - 2, 3, INK))
    parts.append(svg_path(f"M {fmt(cx-33)},{fmt(cy+28)} Q {fmt(cx)},{fmt(cy+50)} {fmt(cx+33)},{fmt(cy+28)} Q {fmt(cx+28)},{fmt(cy+66)} {fmt(cx)},{fmt(cy+69)} Q {fmt(cx-28)},{fmt(cy+66)} {fmt(cx-33)},{fmt(cy+28)} Z", INK))
    if mouth_open:
        parts.append(svg_ellipse(cx, cy + 39, 23, 18, "#05070b"))
        parts.append(svg_rect(cx - 17, cy + 27, 34, 7, WHITE, rx="3"))
    else:
        parts.append(svg_line([(cx - 17, cy + 40), (cx + 17, cy + 40)], INK, 5))
    if label:
        parts.append(svg_text(cx, cy + 199, label, 13, "#d3dfef", text_anchor="middle", font_weight="700", letter_spacing="0.9"))


def interview_background(parts: list[str], *, reaction: bool = False) -> None:
    parts.append('<defs><linearGradient id="interview-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#182536"/><stop offset="100%" stop-color="#2b1e2e"/></linearGradient></defs>')
    parts.append(svg_rect(0, 0, WIDTH, HEIGHT, "url(#interview-bg)"))
    parts.append(svg_rect(31, 172, 478, 596, "#d9c49d", rx="22", opacity="0.94"))
    parts.append(svg_rect(52, 193, 436, 554, "#f4e7c5", rx="18"))
    parts.append(svg_line([(52, 645), (488, 645)], "#c8ae82", 5))


def quote_frame(local_t: float) -> str:
    parts: list[str] = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">']
    interview_background(parts)
    badge(parts)
    parts.append(svg_text(270, 116, "SEAN SHARAF", 20, "#5c4631", text_anchor="middle", font_weight="700", letter_spacing="1.2"))
    mouth_open = math.sin(local_t * math.pi * 7.0) > 0.0
    draw_avatar(parts, 270, 410, skin="#c98966", hair="bald", shirt="#5f7d92", mouth_open=mouth_open)
    parts.append(svg_rect(88, 554, 364, 87, WHITE, rx="18", opacity="0.94"))
    parts.append(svg_polygon([(240, 641), (268, 641), (250, 670)], WHITE))
    parts.append(svg_text(270, 590, "2019 ALLEGATION", 22, INK, text_anchor="middle", font_weight="700", letter_spacing="1.4"))
    parts.append(svg_text(270, 617, "NO CHARGES FILED.", 15, "#a13f45", text_anchor="middle", font_weight="700", letter_spacing="1.2"))
    parts.append("</svg>")
    return "".join(parts)


def reaction_frame(local_t: float) -> str:
    parts: list[str] = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">']
    interview_background(parts, reaction=True)
    badge(parts)
    # Side cutouts keep their arm-up silhouettes and mouth shapes throughout the
    # full 2.3s inserted beat, while the central avatar stays neutral.
    for cx, skin, shirt, side in ((132, "#bf805f", "#875f91", -1), (408, "#e2ad84", "#3b8090", 1)):
        bob = math.sin(local_t * math.pi * 4.0 + (0.4 if side > 0 else 0.0)) * 3.0
        cy = 486 + bob
        parts.append(svg_ellipse(cx, 706, 84, 18, "#080d17", opacity="0.4"))
        parts.append(svg_rect(cx - 64, 572, 128, 134, shirt, rx="26"))
        parts.append(svg_circle(cx, cy, 54, skin))
        parts.append(svg_path(f"M {fmt(cx-54)},{fmt(cy-16)} Q {fmt(cx)},{fmt(cy-64)} {fmt(cx+54)},{fmt(cy-15)} L {fmt(cx+43)},{fmt(cy-4)} Q {fmt(cx)},{fmt(cy-22)} {fmt(cx)},{fmt(cy-22)} Q {fmt(cx-39)},{fmt(cy-20)} {fmt(cx-45)},{fmt(cy-3)} Z", INK if side < 0 else "#737b87"))
        parts.append(svg_ellipse(cx - 18, cy + 27, 20, 16, "#05070b"))
        parts.append(svg_rect(cx - 17, cy + 16, 34, 6, WHITE, rx="3"))
        if side < 0:
            parts.append(svg_line([(cx - 40, 596), (cx - 104, 404)], shirt, 31))
            parts.append(svg_line([(cx + 38, 596), (cx + 104, 428)], shirt, 31))
            parts.append(svg_circle(cx - 104, 404, 22, GLOVE))
            parts.append(svg_circle(cx + 104, 428, 22, GLOVE))
        else:
            parts.append(svg_line([(cx + 40, 596), (cx + 104, 404)], shirt, 31))
            parts.append(svg_line([(cx - 38, 596), (cx - 104, 428)], shirt, 31))
            parts.append(svg_circle(cx + 104, 404, 22, GLOVE))
            parts.append(svg_circle(cx - 104, 428, 22, GLOVE))
        parts.append(svg_text(cx, 743, "INTERVIEWER", 12, "#5d4d3d", text_anchor="middle", font_weight="700", letter_spacing="1.0"))
    draw_avatar(parts, 270, 410, skin="#c98966", hair="bald", shirt="#5f7d92", mouth_open=False)
    parts.append("</svg>")
    return "".join(parts)


def rotate_local(point: Point, angle_deg: float) -> Point:
    radians = math.radians(angle_deg)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return (point[0] * cosine - point[1] * sine, point[0] * sine + point[1] * cosine)


def world_point(pose: dict[str, Any], point: Point) -> Point:
    rotated = rotate_local(point, float(pose["angle"]))
    scale = float(pose.get("scale", 1.0))
    return (pose["root"][0] + rotated[0] * scale, pose["root"][1] + rotated[1] * scale)


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
            u = fast_out(raw) if easing == "fast" else fall_in(raw) if easing == "fall" else smooth(raw)
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


HENDO_KEYS: list[dict[str, Any]] = [
    {"t": 0.0, "root": (172.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (90.0, -136.0), "front_fist": (72.0, -214.0), "back_elbow": (-72.0, -132.0), "back_fist": (-62.0, -208.0)},
    {"t": 0.92, "root": (172.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (108.0, -114.0), "front_fist": (88.0, -184.0), "back_elbow": (-72.0, -132.0), "back_fist": (-62.0, -208.0)},
    {"t": 1.30, "root": (174.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (130.0, -188.0), "front_fist": (208.0, -285.0), "back_elbow": (-72.0, -132.0), "back_fist": (-62.0, -208.0), "ease_from": "fast"},
    {"t": 1.58, "root": (180.0, 604.0), "angle": -5.0, "scale": 1.0, "front_elbow": (122.0, -182.0), "front_fist": (198.0, -274.0), "back_elbow": (-72.0, -130.0), "back_fist": (-58.0, -202.0), "ease_from": "fast"},
    {"t": 2.35, "root": (180.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (88.0, -136.0), "front_fist": (72.0, -214.0), "back_elbow": (-72.0, -132.0), "back_fist": (-62.0, -208.0)},
    {"t": 4.2, "root": (180.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (88.0, -136.0), "front_fist": (72.0, -214.0), "back_elbow": (-72.0, -132.0), "back_fist": (-62.0, -208.0)},
]

BISPING_KEYS: list[dict[str, Any]] = [
    {"t": 0.0, "root": (382.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (-90.0, -136.0), "front_fist": (-72.0, -214.0), "back_elbow": (72.0, -132.0), "back_fist": (62.0, -208.0)},
    {"t": 1.30, "root": (382.0, 600.0), "angle": 0.0, "scale": 1.0, "front_elbow": (-90.0, -136.0), "front_fist": (-72.0, -214.0), "back_elbow": (72.0, -132.0), "back_fist": (62.0, -208.0)},
    {"t": 1.74, "root": (414.0, 640.0), "angle": 13.0, "scale": 0.98, "front_elbow": (-90.0, -130.0), "front_fist": (-72.0, -204.0), "back_elbow": (72.0, -126.0), "back_fist": (60.0, -198.0), "ease_from": "fast"},
    {"t": 2.34, "root": (390.0, 722.0), "angle": 38.0, "scale": 0.90, "front_elbow": (-84.0, -126.0), "front_fist": (-66.0, -198.0), "back_elbow": (65.0, -116.0), "back_fist": (56.0, -190.0), "ease_from": "fall"},
    {"t": 2.96, "root": (322.0, 790.0), "angle": 66.0, "scale": 0.80, "front_elbow": (-80.0, -118.0), "front_fist": (-60.0, -184.0), "back_elbow": (62.0, -108.0), "back_fist": (50.0, -178.0), "ease_from": "fall"},
    {"t": 3.52, "root": (260.0, 824.0), "angle": 82.0, "scale": 0.74, "front_elbow": (-78.0, -114.0), "front_fist": (-58.0, -178.0), "back_elbow": (60.0, -105.0), "back_fist": (48.0, -172.0), "ease_from": "fall"},
    {"t": 4.2, "root": (260.0, 824.0), "angle": 82.0, "scale": 0.74, "front_elbow": (-78.0, -114.0), "front_fist": (-58.0, -178.0), "back_elbow": (60.0, -105.0), "back_fist": (48.0, -172.0)},
]


def fighter_anchors(pose: dict[str, Any]) -> dict[str, Point]:
    return {"head": world_point(pose, (0.0, -285.0)), "front_fist": world_point(pose, pose["front_fist"]), "back_fist": world_point(pose, pose["back_fist"]), "root": pose["root"]}


def draw_limb(parts: list[str], points: list[Point], skin: str, shadow: str, width: float) -> None:
    parts.append(svg_line(points, shadow, width + 10.0))
    parts.append(svg_line(points, skin, width))


def draw_generic_fighter(parts: list[str], pose: dict[str, Any], *, facing: int, skin: str, shadow: str, highlight: str, shorts: str, wrap: str, hair: str, beard: str | None) -> dict[str, Point]:
    root_x, root_y = pose["root"]
    scale = float(pose.get("scale", 1.0))
    angle = float(pose.get("angle", 0.0))
    parts.append(f'<g transform="translate({fmt(root_x)},{fmt(root_y)}) rotate({fmt(angle)}) scale({fmt(scale)})">')
    draw_limb(parts, [(-23.0, -2.0), (-48.0, 112.0), (-64.0, 230.0)], skin, shadow, 58.0)
    draw_limb(parts, [(23.0, -2.0), (48.0, 110.0), (64.0, 230.0)], skin, shadow, 64.0)
    parts.append(svg_circle(-64.0, 230.0, 31.0, INK, opacity="0.95"))
    parts.append(svg_circle(64.0, 230.0, 33.0, INK, opacity="0.95"))
    parts.append(svg_polygon([(-45.0, -183.0), (45.0, -183.0), (57.0, -9.0), (22.0, 30.0), (-22.0, 30.0), (-57.0, -9.0)], shadow))
    parts.append(svg_polygon([(-41.0, -180.0), (41.0, -180.0), (47.0, -25.0), (-47.0, -25.0)], skin))
    shorts_fill = "#f2efe7" if shorts == "white_black" else shorts
    parts.append(svg_polygon([(-47.0, -29.0), (47.0, -29.0), (43.0, 55.0), (8.0, 72.0), (-8.0, 72.0), (-43.0, 55.0)], shorts_fill))
    if shorts == "#f2efe7":
        parts.append(svg_polygon([(4.0, -29.0), (47.0, -29.0), (43.0, 55.0), (8.0, 72.0)], "#dce6ef", opacity="0.86"))
    elif shorts == "white_black":
        parts.append(svg_polygon([(-6.0, -29.0), (47.0, -29.0), (43.0, 55.0), (8.0, 72.0)], "#131722"))
    parts.append(svg_line([(-35.0, -30.0), (35.0, -30.0)], INK, 5, opacity="0.7"))
    rear_shoulder = (-42.0, -164.0)
    front_shoulder = (42.0, -164.0)
    if facing < 0:
        rear_shoulder, front_shoulder = front_shoulder, rear_shoulder
    draw_limb(parts, [rear_shoulder, pose["back_elbow"], pose["back_fist"]], skin, shadow, 49.0)
    draw_limb(parts, [front_shoulder, pose["front_elbow"], pose["front_fist"]], skin, shadow, 55.0)
    for elbow, fist in ((pose["back_elbow"], pose["back_fist"]), (pose["front_elbow"], pose["front_fist"])):
        dx = fist[0] - elbow[0]
        dy = fist[1] - elbow[1]
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        parts.append(svg_line([(fist[0] - ux * 36.0, fist[1] - uy * 36.0), (fist[0] - ux * 15.0, fist[1] - uy * 15.0)], wrap, 23.0))
    parts.append(svg_circle(pose["back_fist"][0], pose["back_fist"][1], 31.0, INK))
    parts.append(svg_circle(pose["back_fist"][0], pose["back_fist"][1] - 3.0, 26.0, GLOVE))
    parts.append(svg_circle(pose["front_fist"][0], pose["front_fist"][1], 34.0, INK))
    parts.append(svg_circle(pose["front_fist"][0], pose["front_fist"][1] - 3.0, 29.0, GLOVE))
    parts.append(svg_ellipse(pose["front_fist"][0] - 8.0, pose["front_fist"][1] - 12.0, 10.0, 5.0, GLOVE_HIGHLIGHT, opacity="0.7"))
    parts.append(svg_ellipse(0.0, -225.0, 25.0, 39.0, shadow))
    parts.append(svg_ellipse(0.0, -229.0, 21.0, 35.0, skin))
    parts.append(svg_circle(0.0, -285.0, 50.0, shadow))
    parts.append(svg_circle(0.0, -288.0, 47.0, skin))
    if hair == "short_dark":
        parts.append(svg_path("M -45,-300 Q -34,-347 0,-337 Q 39,-345 46,-300 L 35,-286 Q 4,-305 -31,-286 Z", INK))
    elif hair == "buzz":
        parts.append(svg_path("M -44,-300 Q -33,-337 0,-337 Q 35,-337 44,-300 L 32,-286 Q 4,-304 -30,-286 Z", "#7e8995"))
    if beard is not None:
        parts.append(svg_path("M -33,-260 Q 0,-232 34,-261 Q 28,-220 0,-215 Q -28,-220 -33,-260 Z", beard))
    eye_x = facing * 17.0
    parts.append(svg_ellipse(eye_x, -295.0, 6.0, 8.0, WHITE))
    parts.append(svg_circle(eye_x + facing * 2.0, -295.0, 3.0, INK))
    parts.append(svg_line([(eye_x - facing * 13.0, -309.0), (eye_x + facing * 8.0, -306.0)], INK, 6))
    parts.append(svg_line([(facing * 16.0, -282.0), (facing * 27.0, -274.0)], INK, 4))
    parts.append('</g>')
    return fighter_anchors(pose)


def impact_ring(parts: list[str], center: Point, progress: float, color: str = GOLD) -> None:
    progress = clamp(progress)
    if progress <= 0.0:
        return
    intensity = math.sin(math.pi * progress)
    radius = 24.0 + 45.0 * progress
    cx, cy = center
    parts.append(svg_circle(cx, cy, radius, "none", stroke=color, stroke_width=7.0, opacity=f"{0.8 * intensity:.3f}"))
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        inner, outer = radius + 8.0, radius + 8.0 + 18.0 * intensity
        parts.append(svg_line([(cx + math.cos(radians) * inner, cy + math.sin(radians) * inner), (cx + math.cos(radians) * outer, cy + math.sin(radians) * outer)], color, 5.0, opacity=f"{0.9 * intensity:.3f}"))


def hendo_frame(local_t: float, *, replay: bool = False) -> str:
    parts: list[str] = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">']
    arena_background(parts, warm=True)
    badge(parts)
    bisping_pose = pose_at(BISPING_KEYS, local_t)
    bisping = draw_generic_fighter(parts, bisping_pose, facing=-1, skin="#f0c9ad", shadow="#ad7c69", highlight="#ffe0c6", shorts="white_black", wrap=BLUE_WRAP, hair="buzz", beard=None)
    # Paint the attacking left/Henderson silhouette second so the right glove
    # remains visibly on the receiving face at the contact witness frame.
    hendo = draw_generic_fighter(parts, pose_at(HENDO_KEYS, local_t), facing=1, skin="#e0ad89", shadow="#9d6b55", highlight="#f1c2a0", shorts="#f2efe7", wrap=RED_WRAP, hair="short_dark", beard=None)
    if 1.06 <= local_t <= 1.60:
        ring_progress = clamp((local_t - 1.06) / 0.18) if local_t < 1.24 else clamp((1.60 - local_t) / 0.36)
        impact_ring(parts, bisping["head"], ring_progress, color="#ffb15c")
    parts.append(svg_text(110, 784, "HENDERSON", 15, "#f3d49c", text_anchor="middle", font_weight="700", letter_spacing="1.2"))
    parts.append(svg_text(428, 784, "BISPING", 15, "#8bdcff", text_anchor="middle", font_weight="700", letter_spacing="1.2"))
    parts.append("</svg>")
    return "".join(parts)


def followup_frame(local_t: float) -> str:
    mapped = clamp(0.18 + local_t * (3.64 / 3.066667), 0.0, 4.0)
    svg = PROOF.render_svg(mapped)
    return wrap_svg(svg, [svg_rect(28, 32, 194, 34, GOLD, rx="17", opacity="0.96"), svg_text(125, 55, "ANIMATED PARODY", 14, INK, text_anchor="middle", font_weight="700", letter_spacing="1.2")])


def render_frame(global_t: float) -> str:
    if global_t < 7.333333:
        return opening_frame(global_t)
    if global_t < REACTION_START:
        return quote_frame(global_t - 7.333333)
    if global_t < REACTION_END:
        return reaction_frame(global_t - REACTION_START)
    followup_start = REACTION_END
    followup_end = followup_start + 3.066667
    if global_t < followup_end:
        return followup_frame(global_t - followup_start)
    hendo_start = followup_end
    hendo_end = hendo_start + 4.2
    if global_t < hendo_end:
        return hendo_frame(global_t - hendo_start)
    replay_start = hendo_end
    replay_local = clamp((global_t - replay_start) * (4.2 / 2.6), 0.0, 4.2)
    return hendo_frame(replay_local, replay=True)


def write_style_preview() -> None:
    svg = hendo_frame(1.30)
    STYLE_SVG.write_text(svg, encoding="utf-8")
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(STYLE_PNG), output_width=WIDTH, output_height=HEIGHT)


def render_animation() -> None:
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    for frame_index in range(FRAME_COUNT):
        time_s = frame_index / FPS
        svg = render_frame(time_s)
        output_path = FRAMES_DIR / f"frame-{frame_index:05d}.png"
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(output_path), output_width=WIDTH, output_height=HEIGHT)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to encode the review rough cut")
    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(FPS), "-i", str(FRAMES_DIR / "frame-%05d.png"),
        "-frames:v", str(FRAME_COUNT), "-c:v", "libx264", "-crf", "18",
        "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(ROOT / "video-only.mp4"),
    ]
    subprocess.run(command, check=True)
    build_audio()
    mux = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(ROOT / "video-only.mp4"),
        "-i", str(AUDIO_PATH), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(VIDEO_PATH),
    ]
    subprocess.run(mux, check=True)


def build_audio() -> None:
    if not MASTER_AUDIO.exists() or not REACTION_AUDIO.exists() or not CONTINUOUS_BED.exists():
        raise FileNotFoundError("required v11 master, reaction-duo, or continuous-bed source is missing")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to build the inserted reaction audio")
    AUDIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    filter_complex = (
        "[0:a]atrim=start=0:end=8.766667,asetpts=PTS-STARTPTS,"
        "afade=t=out:curve=hsin:st=8.726667:d=0.04[pre];"
        "[0:a]atrim=start=8.766667:end=18.633333,asetpts=PTS-STARTPTS,"
        "afade=t=in:curve=hsin:st=0:d=0.04[tail];"
        "[1:a]atrim=start=0:end=2.3,asetpts=PTS-STARTPTS[reaction];"
        "[2:a]atrim=start=8.766667:end=11.066667,asetpts=PTS-STARTPTS[bedseg];"
        "[reaction][bedseg]amix=inputs=2:duration=first:dropout_transition=0:weights='1 1':normalize=0,"
        "afade=t=in:curve=hsin:st=0:d=0.04,afade=t=out:curve=hsin:st=2.26:d=0.04,alimiter=limit=0.95[insert];"
        "[pre][insert][tail]concat=n=3:v=0:a=1,atrim=duration=20.933333,asetpts=PTS-STARTPTS[out]"
    )
    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(MASTER_AUDIO), "-i", str(REACTION_AUDIO), "-i", str(CONTINUOUS_BED),
        "-filter_complex", filter_complex, "-map", "[out]", "-ar", "48000", "-ac", "2",
        "-c:a", "pcm_s16le", str(AUDIO_PATH),
    ]
    subprocess.run(command, check=True)
    AUDIO_MANIFEST.write_text(json.dumps({
        "status": "PASS",
        "source_master": str(MASTER_AUDIO),
        "source_reaction": str(REACTION_AUDIO),
        "source_continuous_bed": str(CONTINUOUS_BED),
        "original_duration_s": 18.633333,
        "insert_at_s": REACTION_START,
        "reaction_duration_s": REACTION_DURATION,
        "new_duration_s": NOMINAL_DURATION_S,
        "mix_rule": "master before + reaction-duo mixed over continuous v9 bed at unity + master tail; 40ms equal-power fades at boundaries; no ducking",
    }, indent=2) + "\n", encoding="utf-8")


def make_contact_sheet() -> None:
    sample_times = [0.0, 1.18, 2.20, 4.10, 5.50, 7.30, 7.95, 8.78, 9.75, 11.0, 11.85, 13.4, 14.20, 15.43, 17.60, 18.38, 19.45, 20.88]
    labels = [
        "filed freeze", "anticipation", "flash", "contact", "brain/recoil", "full fall", "quote", "reaction",
        "reaction / center dry", "reaction end", "follow-up contact", "follow-up fall", "Hendo guard", "Hendo contact",
        "Bisping fall", "replay start", "replay fall", "grounded hold",
    ]
    cols = 6
    rows = math.ceil(len(sample_times) / cols)
    cell_w, cell_h, label_h = 150, 267, 26
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), "#0b1120")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
    for index, (time_s, label) in enumerate(zip(sample_times, labels)):
        frame_index = min(FRAME_COUNT - 1, max(0, round(time_s * FPS)))
        frame_path = FRAMES_DIR / f"frame-{frame_index:05d}.png"
        with Image.open(frame_path) as frame:
            frame = frame.convert("RGB")
            frame.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + (cell_w - frame.width) // 2
            y = (index // cols) * (cell_h + label_h) + label_h
            sheet.paste(frame, (x, y))
        draw.text(((index % cols) * cell_w + 4, (index // cols) * (cell_h + label_h) + 6), f"{time_s:0.2f}s {label}", fill=WHITE, font=font)
    sheet.save(CONTACT_SHEET, format="PNG", optimize=True)


def geometry_receipt() -> dict[str, Any]:
    opening_contact_s = 4.1
    proof_local_contact = opening_contact_s - 2.975
    left_contact = PROOF.anchors_for(PROOF.pose_at(PROOF.LEFT_KEYS, proof_local_contact))
    right_contact = PROOF.anchors_for(PROOF.pose_at(PROOF.RIGHT_KEYS, proof_local_contact))
    contact_distance = math.hypot(right_contact["front_fist"][0] - left_contact["head"][0], right_contact["front_fist"][1] - left_contact["head"][1])
    hendo_contact_s = (REACTION_END + 3.066667) + 1.30
    hendo_pose = pose_at(HENDO_KEYS, 1.30)
    bisping_pose = pose_at(BISPING_KEYS, 1.30)
    hendo = fighter_anchors(hendo_pose)
    bisping = fighter_anchors(bisping_pose)
    hendo_distance = math.hypot(hendo["front_fist"][0] - bisping["head"][0], hendo["front_fist"][1] - bisping["head"][1])
    fall_pose = pose_at(BISPING_KEYS, 3.52)
    fall = fighter_anchors(fall_pose)
    fall_head_radius = 50.0 * float(fall_pose.get("scale", 1.0))
    return {
        "opening": {
            "animation_map": {"guard_motion_s": [0.0, 1.197], "filed_freeze_s": [1.197, 2.35], "proof_local_at_0_s": 0.0, "proof_local_at_1.197_s": 0.4, "proof_local_at_2.35_s": 0.4, "proof_local_at_4.1_s": 1.125},
            "contact": {"time_s": opening_contact_s, "attacker": "right_fighter_right_glove", "receiver": "left_head", "glove_center_px": [round(right_contact["front_fist"][0], 2), round(right_contact["front_fist"][1], 2)], "receiver_head_center_px": [round(left_contact["head"][0], 2), round(left_contact["head"][1], 2)], "center_distance_px": round(contact_distance, 2), "passes": contact_distance <= 20.0},
            "brain_launch": {"planned_time_s": 4.2, "visible_from_s": 4.2, "rule": "proof brain appears only after proof contact/recoil; no skull or gore"},
            "fall": {"start_s": 5.455, "floor_s": 6.625, "attacker_stays_standing": True},
        },
        "hendo_bisping": {
            "contact": {"time_s": round(hendo_contact_s, 6), "attacker": "left_henderson_right_glove", "receiver": "right_bisping_head", "glove_center_px": [round(hendo["front_fist"][0], 2), round(hendo["front_fist"][1], 2)], "receiver_head_center_px": [round(bisping["head"][0], 2), round(bisping["head"][1], 2)], "center_distance_px": round(hendo_distance, 2), "passes": hendo_distance <= 20.0},
            "fall": {"sample_s": round(hendo_contact_s - 1.30 + 3.52, 6), "fighter": "right_bisping", "head_center_px": [round(fall["head"][0], 2), round(fall["head"][1], 2)], "torso_root_px": [round(fall["root"][0], 2), round(fall["root"][1], 2)], "mat_y_px": 838.0, "head_radius_px": round(fall_head_radius, 2), "body_angle_deg": round(float(fall_pose["angle"]), 2), "near_horizontal": abs(abs(float(fall_pose["angle"])) - 90.0) <= 12.0, "floor_contact_passes": abs(838.0 - fall["head"][1]) <= fall_head_radius * 1.25, "torso_floor_contact_passes": abs(838.0 - fall["root"][1]) <= 20.0},
        },
    }


def write_timeline() -> None:
    timeline = {
        "schema_version": "minimal_full_private_review.v1",
        "project": "knockout-brain-matchcut-001",
        "variant": "minimal-full",
        "status": "private-review-rough-cut",
        "renderer": "render_minimal_full.py",
        "deviation": "standalone native SVG frame sequence with full audio; not migrated into shared scene-evidence engine",
        "canvas": {"width": WIDTH, "height": HEIGHT, "fps": FPS, "nominal_duration_s": NOMINAL_DURATION_S, "frame_count": FRAME_COUNT},
        "source_edit": "production/edit-v11.json",
        "audio": {"original_master": "production/audio/master-v11.wav", "reaction_insert": "production/animated-variants/audio/reaction-duo.wav", "continuous_bed": "production/edit-v9/continuous-bed.wav", "insert_at_s": REACTION_START, "reaction_end_s": REACTION_END, "new_duration_s": NOMINAL_DURATION_S},
        "segments": [
            {"id": "hook", "start_s": 0.0, "end_s": 7.333333, "source_duration_s": 7.333333, "visual": "proof art opening; filed freeze, transformation flash, right-hand contact, brain recoil, full fall"},
            {"id": "news", "start_s": 7.333333, "end_s": REACTION_START, "source_duration_s": 1.433333, "visual": "native cutout-comedy attributed interview; speaker mouth animates"},
            {"id": "reaction", "start_s": REACTION_START, "end_s": REACTION_END, "source_duration_s": REACTION_DURATION, "visual": "two interviewer mouths scream/arms-up while center remains dry"},
            {"id": "follow-up", "start_s": REACTION_END, "end_s": 14.133334, "source_duration_s": 3.066667, "source_start_s": 8.766667, "visual": "proof-art follow-up replay with actual contact, recoil, continuing fall"},
            {"id": "hendo", "start_s": 14.133334, "end_s": 18.333334, "source_duration_s": 4.2, "source_start_s": 11.833333, "visual": "separate Henderson/Bisping flat silhouettes; left red right-hand contact, right blue fighter falls"},
            {"id": "hendo-replay", "start_s": 18.333334, "end_s": 20.933333, "source_duration_s": 2.6, "source_start_s": 16.033333, "visual": "Henderson/Bisping replay; right blue fighter remains down"},
        ],
        "captions": [{"start_s": 0.0, "end_s": 1.197, "text": "NO CHARGES FILED."}, {"start_s": 1.197, "end_s": 2.199, "text": "THEN SHARAF DELIVERED A"}, {"start_s": 2.199, "end_s": 3.5, "text": "ONE-PUNCH VERDICT."}],
        "required_disclosures": ["ANIMATED PARODY", "SEAN SHARAF", "2019 ALLEGATION", "NO CHARGES FILED"],
        "characters": {"opening_left": "dark skin, short black hair, beard, black shorts, red wraps; falls", "opening_right": "light skin, bald, beard, white shorts, blue wraps; lands right hand then left hook", "hendo_left": "Henderson parody silhouette, light tan skin, short dark hair, white shorts, red wraps; lands right hand", "bisping_right": "Bisping parody silhouette, pale skin, buzzcut, black/white shorts, blue wraps; falls"},
        "geometry": geometry_receipt(),
        "review_artifacts": {"video": VIDEO_PATH.name, "contact_sheet": CONTACT_SHEET.name, "style_preview": STYLE_PNG.name, "audio": str(AUDIO_PATH.relative_to(ROOT))},
    }
    TIMELINE_PATH.write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")


def run_validation() -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    ffmpeg = shutil.which("ffmpeg")
    if not ffprobe or not ffmpeg:
        raise RuntimeError("ffprobe and ffmpeg are required for validation")
    probe = subprocess.run([ffprobe, "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate,nb_frames,duration,pix_fmt,codec_name", "-of", "json", str(VIDEO_PATH)], check=True, capture_output=True, text=True)
    decoded = subprocess.run([ffmpeg, "-v", "error", "-i", str(VIDEO_PATH), "-f", "null", "-"], capture_output=True, text=True)
    if decoded.returncode != 0:
        raise RuntimeError(f"ffmpeg decode failed: {decoded.stderr.strip()}")
    metadata = json.loads(probe.stdout)
    video_stream = next(stream for stream in metadata["streams"] if stream.get("codec_type", "video") == "video")
    audio_stream = next((stream for stream in metadata["streams"] if stream.get("codec_type") == "audio"), None)
    result = {"status": "PASS", "video": VIDEO_PATH.name, "probe": {"video": video_stream, "audio": audio_stream}, "decode": "PASS", "checks": {"dimensions": [video_stream.get("width"), video_stream.get("height")] == [WIDTH, HEIGHT], "frame_rate": video_stream.get("r_frame_rate") == f"{FPS}/1", "frame_count": int(video_stream.get("nb_frames", 0)) == FRAME_COUNT, "duration_s_within_one_frame": abs(float(video_stream.get("duration", 0.0)) - NOMINAL_DURATION_S) <= 1.0 / FPS, "audio_present": audio_stream is not None}}
    if not all(result["checks"].values()):
        result["status"] = "FAIL"
        raise RuntimeError(json.dumps(result, indent=2))
    VALIDATION_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--audio", action="store_true")
    parser.add_argument("--contact-sheet", action="store_true")
    parser.add_argument("--timeline", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.error("choose --style, --render, --audio, --contact-sheet, --timeline, --validate, or --all")
    if args.style or args.all:
        write_style_preview()
    if args.audio or args.all:
        build_audio()
    if args.render or args.all:
        render_animation()
    if args.timeline or args.all:
        write_timeline()
    if args.contact_sheet or args.all:
        make_contact_sheet()
    if args.validate or args.all:
        print(json.dumps(run_validation(), indent=2))


if __name__ == "__main__":
    main()
