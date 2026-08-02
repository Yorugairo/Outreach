"""Deterministic six-still visual direction style board.

The style board is deliberately a local, renderer-owned artifact.  It is a
small visual contract between art direction and the human Visual Direction
Gate; it is not an approval and it never reads pixels from the study corpus.
The service only uses persisted art-bible/treatment values and Pillow's
deterministic drawing primitives, so tests and local pipeline runs need no
provider credentials.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from PIL import Image, ImageDraw, ImageFont

from content.video_engine.src.models import StageContext, StageOutput, VideoRun


STYLE_BOARD_VERSION = "style_board.v1"
STYLE_BOARD_REVIEW_PACKET_VERSION = "style_board_review.v1"

# These are the six human-facing still roles.  ``result_preview`` is accepted
# as a synonym for ``hook`` by the guard, while all other aliases are kept in
# one place so callers can use the vocabulary from either V2 or V3.
STYLE_BOARD_STILL_ROLES: tuple[str, ...] = (
    "hook",
    "wide_setup",
    "contact_closeup",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
)
REQUIRED_STILL_ROLES = STYLE_BOARD_STILL_ROLES
STYLE_BOARD_ROLES = STYLE_BOARD_STILL_ROLES
REQUIRED_STILLS = STYLE_BOARD_STILL_ROLES
STYLE_BOARD_STILLS = STYLE_BOARD_STILL_ROLES

COMPOSITION_FUNCTIONS: tuple[str, ...] = (
    "result_preview",
    "wide_setup",
    "contact_closeup",
    "mechanic_transition",
    "wrong_right_compare",
    "force_diagram",
    "result_hold",
    "story_or_persona_cutaway",
)
REQUIRED_COMPOSITION_FUNCTIONS = frozenset(COMPOSITION_FUNCTIONS)

_ROLE_ALIASES: dict[str, frozenset[str]] = {
    "hook": frozenset({"hook", "hero", "hero_frame", "result_preview", "opening"}),
    "wide_setup": frozenset({"wide_setup", "wide", "context"}),
    "contact_closeup": frozenset(
        {"contact_closeup", "contact_detail", "detail", "closeup", "close_up"}
    ),
    "wrong_right_compare": frozenset(
        {"wrong_right_compare", "wrong_right", "comparison", "compare"}
    ),
    "force_diagram": frozenset(
        {"force_diagram", "diagram", "leverage_diagram", "force"}
    ),
    "result_hold": frozenset({"result_hold", "held_result", "result"}),
}

_DEFAULT_CAST: dict[str, dict[str, Any]] = {
    "attacker": {
        "id": "attacker",
        "color": "#3B82F6",
        "fill": "#F4F7FA",
        "gi": "white_gi",
        "belt": "blue_belt",
        "depth": 1,
    },
    "defender": {
        "id": "defender",
        "color": "#8B5CF6",
        "fill": "#151C24",
        "gi": "black_gi",
        "belt": "purple_belt",
        "depth": 0,
    },
}
_DEFAULT_PALETTE = {
    "background": "#0B0F14",
    "surface": "#151C24",
    "ink": "#F4F7FA",
    "muted": "#9DAABB",
    "accent": "#20D69B",
    "active": "#FF8A3D",
    "warning": "#FF8A3D",
    "wrong": "#EF5B5B",
    "attacker": "#3B82F6",
    "attacker_fill": "#F4F7FA",
    "defender": "#8B5CF6",
    "defender_fill": "#151C24",
}
_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


class StyleBoardError(ValueError):
    """Raised when a deterministic style board cannot be built."""


def canonical_json(value: Any) -> bytes:
    """Return the canonical bytes used by all V3 artifact hashes."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _load_json(value: Any, label: str) -> Any:
    if isinstance(value, Mapping):
        return copy.deepcopy(dict(value))
    if isinstance(value, (str, Path)):
        path = Path(value)
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise StyleBoardError(f"{label} is not valid JSON: {path}") from exc
        # A JSON string is useful for small integration tests; regular strings
        # are intentionally treated as paths first to avoid accepting a path
        # as a JSON object by accident.
        if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise StyleBoardError(f"{label} is not valid JSON") from exc
    raise StyleBoardError(f"{label} must be a mapping or JSON path")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _deep_copy(value: Any) -> Any:
    return copy.deepcopy(value)


def _extract_art_bible(art_direction: Mapping[str, Any]) -> Any:
    for key in ("art_bible", "artBible", "art_direction", "art_direction_snapshot"):
        candidate = art_direction.get(key)
        if isinstance(candidate, Mapping):
            nested = candidate.get("art_bible")
            return _as_mapping(nested) if isinstance(nested, Mapping) else candidate
        if isinstance(candidate, (str, Path)):
            return candidate
    return art_direction


def _explicit_hash(value: Mapping[str, Any]) -> str | None:
    for key in (
        "art_bible_hash",
        "artBibleHash",
        "artifact_hash",
        "content_hash",
        "hash",
    ):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip().lower()
    return None


def resolve_art_bible_hash(
    art_direction: Mapping[str, Any],
    art_bible: Mapping[str, Any] | None = None,
) -> str:
    """Resolve the current art-bible hash without leaking study provenance."""

    direction_hash = _explicit_hash(art_direction)
    if direction_hash:
        return direction_hash
    bible = art_bible if art_bible is not None else _extract_art_bible(art_direction)
    if not isinstance(bible, Mapping):
        return sha256_json(bible)
    bible_hash = _explicit_hash(bible)
    if bible_hash:
        return bible_hash
    return sha256_json(bible)


def _font(size: int, *, mono: bool = False) -> ImageFont.ImageFont:
    font_root = Path(__file__).resolve().parents[1] / "assets" / "fonts"
    names = (
        (font_root / "RobotoMono-Variable.ttf", "DejaVuSansMono.ttf")
        if mono
        else (font_root / "Inter-Variable.ttf", "DejaVuSans.ttf", "arial.ttf")
    )
    for name in names:
        try:
            return ImageFont.truetype(str(name), size)
        except OSError:
            continue
    return ImageFont.load_default()


def _color(value: Any, default: str) -> str:
    candidate = str(value or "").strip()
    return candidate if _HEX_COLOR.fullmatch(candidate) else default


def _hamming(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def _dct_phash(image: Image.Image) -> str:
    """Compute a dependency-free 64-bit perceptual DCT hash.

    Pillow is already a required video-engine dependency.  Keeping the hash
    implementation local avoids adding imagehash/numpy just for QC and makes
    the output stable on the supported Python versions.
    """

    sample = image.convert("L").resize((32, 32), Image.Resampling.LANCZOS)
    flattened = getattr(sample, "get_flattened_data", None)
    pixels = list(flattened() if callable(flattened) else sample.getdata())
    coefficients: list[float] = []
    for u in range(8):
        for v in range(8):
            total = 0.0
            for x in range(32):
                for y in range(32):
                    total += pixels[x * 32 + y] * math.cos(
                        math.pi * (2 * x + 1) * u / 64
                    ) * math.cos(math.pi * (2 * y + 1) * v / 64)
            coefficients.append(total)
    low = coefficients[1:]
    median = sorted(low)[len(low) // 2]
    bits = 0
    for coefficient in low:
        bits = (bits << 1) | int(coefficient > median)
    return f"{bits:016x}"


def _safe_zones() -> dict[str, dict[str, str]]:
    return {
        "landscape": {"action_zone": "center", "caption_zone": "top"},
        "vertical": {"action_zone": "middle", "caption_zone": "top"},
    }


def _normalize_treatments(
    art_direction: Mapping[str, Any],
    treatments: Mapping[str, Any] | Sequence[Any] | None,
) -> list[dict[str, Any]]:
    value: Any = treatments
    if value is None:
        for key in (
            "treatments",
            "visual_treatments",
            "visual_treatment",
            "treatment_library",
            "shots",
        ):
            value = art_direction.get(key)
            if value is not None:
                break
    if isinstance(value, Mapping):
        value = value.get("treatments") or value.get("shots") or [value]
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        value = []
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            continue
        normalized = _deep_copy(dict(item))
        normalized.setdefault(
            "id",
            normalized.get("treatment_id")
            or normalized.get("shot_id")
            or f"treatment_{index + 1:02d}",
        )
        normalized.setdefault(
            "function",
            normalized.get("visual_function") or normalized.get("composition") or "",
        )
        result.append(normalized)
    return result


def _treatment_for_role(
    role: str,
    index: int,
    treatments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    aliases = _ROLE_ALIASES.get(role, frozenset({role}))
    for treatment in treatments:
        function = str(
            treatment.get("function")
            or treatment.get("visual_function")
            or treatment.get("composition")
            or ""
        ).casefold()
        if function in aliases:
            return dict(treatment)
    if treatments:
        return dict(treatments[index % len(treatments)])
    defaults = {
        "hook": ("result_preview", "preview_hero"),
        "wide_setup": ("wide_setup", "wide_context"),
        "contact_closeup": ("contact_closeup", "contact_macro"),
        "wrong_right_compare": ("wrong_right_compare", "matched_comparison"),
        "force_diagram": ("force_diagram", "living_leverage"),
        "result_hold": ("result_hold", "held_result"),
    }
    function, treatment_id = defaults[role]
    return {"id": treatment_id, "function": function}


def _role_function(role: str, treatment: Mapping[str, Any]) -> str:
    function = str(
        treatment.get("function")
        or treatment.get("visual_function")
        or treatment.get("composition")
        or ""
    ).casefold()
    return function or {"hook": "result_preview"}.get(role, role)


def _role_overlay(role: str) -> list[dict[str, Any]]:
    if role == "contact_closeup":
        return [{"id": "contact_anchor", "anchor": "wrist_control", "reviewed": True}]
    if role == "wrong_right_compare":
        return [{"id": "comparison_divider", "anchor": "hip_angle", "reviewed": True}]
    if role == "force_diagram":
        return [
            {"id": "fulcrum_marker", "anchor": "hip_fulcrum", "reviewed": True},
            {"id": "force_vector", "anchor": "line_of_force", "reviewed": True},
        ]
    return []


def _draw_capsule(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    width: int,
    fill: str,
    outline: str,
) -> None:
    """Draw one opaque tapered-limb mass with a readable ownership edge."""

    outline_width = max(width + 6, 8)
    draw.line((*start, *end), fill=outline, width=outline_width)
    radius = outline_width // 2
    for x, y in (start, end):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=outline)
    draw.line((*start, *end), fill=fill, width=max(width, 4))
    radius = max(width // 2, 2)
    for x, y in (start, end):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)


def _draw_cutout_fighter(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    *,
    scale: float,
    angle_deg: float,
    facing: int,
    fill: str,
    accent: str,
    outline: str,
    pose: str = "guard",
) -> dict[str, tuple[float, float]]:
    """Draw a compact filled gi cutout and return its mechanical anchors."""

    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    def point(x: float, y: float) -> tuple[float, float]:
        x *= float(facing)
        return (
            center[0] + (x * cos_a - y * sin_a) * scale,
            center[1] + (x * sin_a + y * cos_a) * scale,
        )

    if pose == "extension":
        local = {
            "hip": (0, 6),
            "shoulder": (0, -42),
            "head": (0, -68),
            "elbow_l": (-32, -35),
            "hand_l": (-62, -12),
            "elbow_r": (28, -28),
            "hand_r": (55, -48),
            "knee_l": (-36, 38),
            "foot_l": (-68, 50),
            "knee_r": (38, 34),
            "foot_r": (70, 18),
        }
    else:
        local = {
            "hip": (0, 6),
            "shoulder": (0, -42),
            "head": (0, -68),
            "elbow_l": (-30, -28),
            "hand_l": (-48, 2),
            "elbow_r": (30, -28),
            "hand_r": (48, 2),
            "knee_l": (-36, 34),
            "foot_l": (-18, 62),
            "knee_r": (36, 34),
            "foot_r": (18, 62),
        }
    joints = {name: point(*value) for name, value in local.items()}

    limb_width = max(8, round(13 * scale))
    for start, end in (
        ("hip", "knee_l"),
        ("knee_l", "foot_l"),
        ("hip", "knee_r"),
        ("knee_r", "foot_r"),
    ):
        _draw_capsule(
            draw,
            joints[start],
            joints[end],
            width=limb_width + 2,
            fill=fill,
            outline=outline,
        )

    shoulder, hip = joints["shoulder"], joints["hip"]
    dx, dy = shoulder[0] - hip[0], shoulder[1] - hip[1]
    length = max(math.hypot(dx, dy), 1)
    nx, ny = -dy / length * 20 * scale, dx / length * 20 * scale
    torso = (
        (shoulder[0] + nx, shoulder[1] + ny),
        (shoulder[0] - nx, shoulder[1] - ny),
        (hip[0] - nx * 0.78, hip[1] - ny * 0.78),
        (hip[0] + nx * 0.78, hip[1] + ny * 0.78),
    )
    draw.polygon(torso, fill=outline)
    inset = tuple(
        (
            center[0] + (x - center[0]) * 0.88,
            center[1] + (y - center[1]) * 0.88,
        )
        for x, y in torso
    )
    draw.polygon(inset, fill=fill)

    for start, end in (
        ("shoulder", "elbow_l"),
        ("elbow_l", "hand_l"),
        ("shoulder", "elbow_r"),
        ("elbow_r", "hand_r"),
    ):
        _draw_capsule(
            draw,
            joints[start],
            joints[end],
            width=limb_width,
            fill=fill,
            outline=outline,
        )

    head_radius = max(10, round(17 * scale))
    hx, hy = joints["head"]
    draw.ellipse(
        (hx - head_radius - 3, hy - head_radius - 3, hx + head_radius + 3, hy + head_radius + 3),
        fill=outline,
    )
    draw.ellipse(
        (hx - head_radius, hy - head_radius, hx + head_radius, hy + head_radius),
        fill=fill,
    )
    belt_a, belt_b = point(-19, 4), point(19, 4)
    draw.line((*belt_a, *belt_b), fill=accent, width=max(5, round(8 * scale)))
    lapel_a, lapel_b = point(-8, -38), point(6, 0)
    draw.line((*lapel_a, *lapel_b), fill=accent, width=max(3, round(5 * scale)))
    for name in ("hand_l", "hand_r", "foot_l", "foot_r"):
        x, y = joints[name]
        radius = max(4, round(6 * scale))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=accent)
    return joints


def _draw_still(
    role: str,
    index: int,
    *,
    width: int,
    height: int,
    palette: Mapping[str, str],
    cast: Mapping[str, Any],
    treatment: Mapping[str, Any],
) -> Image.Image:
    bg = _color(palette.get("background"), _DEFAULT_PALETTE["background"])
    surface = _color(palette.get("surface"), _DEFAULT_PALETTE["surface"])
    ink = _color(palette.get("ink"), _DEFAULT_PALETTE["ink"])
    muted = _color(palette.get("muted"), _DEFAULT_PALETTE["muted"])
    accent = _color(palette.get("accent"), _DEFAULT_PALETTE["accent"])
    warning = _color(palette.get("warning"), _DEFAULT_PALETTE["warning"])
    wrong = _color(palette.get("wrong"), _DEFAULT_PALETTE["wrong"])
    image = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(image)
    title = _font(max(18, width // 30))
    body = _font(max(13, width // 48))
    small = _font(max(11, width // 60), mono=True)
    draw.rectangle((0, 0, width, max(48, height // 8)), fill=surface)
    draw.text((24, 14), f"COMBAT SCIENCE  /  {role.replace('_', ' ').upper()}", fill=ink, font=title)
    draw.text(
        (24, height - 34),
        str(treatment.get("id") or f"treatment_{index + 1:02d}"),
        fill=muted,
        font=small,
    )

    # Every role has a distinct large primitive and line-of-action.  This is
    # intentionally diagrammatic rather than an attempt at photoreal anatomy.
    left = width // 8
    right = width - left
    top = height // 3
    bottom = height - height // 6
    attacker_color = _color(
        _as_mapping(cast.get("attacker")).get("color")
        or palette.get("attacker")
        or palette.get("attacker_blue"),
        "#3B82F6",
    )
    defender_color = _color(
        _as_mapping(cast.get("defender")).get("color")
        or palette.get("defender")
        or palette.get("defender_purple"),
        "#8B5CF6",
    )
    attacker_fill = _color(
        _as_mapping(cast.get("attacker")).get("fill")
        or palette.get("attacker_fill")
        or palette.get("attacker_ivory"),
        "#F4F7FA",
    )
    defender_fill = _color(
        _as_mapping(cast.get("defender")).get("fill")
        or palette.get("defender_fill")
        or palette.get("defender_charcoal"),
        "#151C24",
    )

    def fighter(
        center: tuple[float, float],
        *,
        scale: float,
        angle: float,
        attacker: bool,
        pose: str = "guard",
    ) -> dict[str, tuple[float, float]]:
        return _draw_cutout_fighter(
            draw,
            center,
            scale=scale,
            angle_deg=angle,
            facing=1 if attacker else -1,
            fill=attacker_fill if attacker else defender_fill,
            accent=attacker_color if attacker else defender_color,
            outline=ink,
            pose=pose,
        )

    if role == "hook":
        draw.rounded_rectangle(
            (left, top - 12, right, bottom + 5),
            radius=20,
            fill=surface,
            outline=accent,
            width=5,
        )
        fighter((width * 0.43, height * 0.60), scale=0.86, angle=-68, attacker=True, pose="extension")
        fighter((width * 0.57, height * 0.59), scale=0.82, angle=104, attacker=False, pose="extension")
        draw.arc((width * 0.31, top - 10, width * 0.69, bottom + 20), 195, 348, fill=warning, width=7)
        draw.text((left + 18, top - 1), "RESULT  →  REWIND", fill=warning, font=body)
    elif role == "wide_setup":
        draw.rounded_rectangle((left, top - 18, right, bottom + 4), radius=18, fill=surface)
        for y in (bottom - 38, bottom - 10):
            draw.line((left + 12, y, right - 12, y), fill=muted, width=2)
        fighter((width * 0.36, height * 0.63), scale=0.9, angle=-18, attacker=True)
        fighter((width * 0.64, height * 0.62), scale=0.9, angle=18, attacker=False)
        draw.text((left + 16, top - 2), "SCREEN DIRECTION  →", fill=accent, font=small)
    elif role == "contact_closeup":
        draw.rounded_rectangle((left, top - 10, right, bottom + 8), radius=28, fill=surface, outline=accent, width=7)
        _draw_capsule(
            draw,
            (left + 48, height * 0.58),
            (width * 0.49, height * 0.52),
            width=28,
            fill=attacker_fill,
            outline=attacker_color,
        )
        _draw_capsule(
            draw,
            (right - 52, height * 0.66),
            (width * 0.51, height * 0.52),
            width=30,
            fill=defender_fill,
            outline=defender_color,
        )
        draw.ellipse((width // 2 - 30, height // 2 - 30, width // 2 + 30, height // 2 + 30), outline=accent, width=8)
        draw.ellipse((width // 2 - 9, height // 2 - 9, width // 2 + 9, height // 2 + 9), fill=warning)
        draw.rounded_rectangle((right - 142, top, right - 20, top + 84), radius=10, fill=bg, outline=muted, width=2)
        fighter((right - 90, top + 50), scale=0.32, angle=-66, attacker=True, pose="extension")
        fighter((right - 66, top + 49), scale=0.3, angle=104, attacker=False, pose="extension")
        draw.text((left + 18, bottom - 34), "WRIST OWNERSHIP", fill=accent, font=small)
    elif role == "wrong_right_compare":
        middle = width // 2
        draw.rectangle((left, top, middle - 12, bottom), fill=surface, outline=wrong, width=6)
        draw.rectangle((middle + 12, top, right, bottom), fill=surface, outline=accent, width=6)
        draw.text((left + 20, top + 18), "WRONG", fill=wrong, font=body)
        draw.text((middle + 32, top + 18), "RIGHT", fill=accent, font=body)
        for cx in (width * 0.28, width * 0.72):
            fighter((cx - 13, height * 0.68), scale=0.46, angle=-70, attacker=True, pose="extension")
            fighter((cx + 13, height * 0.67), scale=0.44, angle=105, attacker=False, pose="extension")
        draw.line((left + 40, bottom - 39, middle - 40, bottom - 62), fill=wrong, width=6)
        draw.line((middle + 40, bottom - 50, right - 40, bottom - 50), fill=accent, width=6)
        draw.text((left + 20, bottom - 32), "ELBOW LEAKS", fill=wrong, font=small)
        draw.text((middle + 32, bottom - 32), "ELBOW STACKS", fill=accent, font=small)
    elif role == "force_diagram":
        fighter((width * 0.44, height * 0.62), scale=0.75, angle=-68, attacker=True, pose="extension")
        fighter((width * 0.57, height * 0.61), scale=0.72, angle=104, attacker=False, pose="extension")
        draw.ellipse((width // 2 - 30, height // 2 - 30, width // 2 + 30, height // 2 + 30), outline=warning, width=7)
        draw.line((width // 2 - 120, bottom - 28, width // 2 + 115, top + 14), fill=accent, width=7)
        draw.polygon((width // 2 + 115, top + 14, width // 2 + 78, top + 18, width // 2 + 103, top + 44), fill=accent)
        draw.line((width // 2, top - 8, width // 2, bottom + 5), fill=warning, width=4)
        draw.text((left, top - 34), "FULCRUM  /  LINE OF FORCE", fill=muted, font=small)
    else:  # result_hold
        draw.rounded_rectangle((left, top - 10, right, bottom + 6), radius=22, fill=surface, outline=accent, width=6)
        fighter((width * 0.42, height * 0.62), scale=0.8, angle=-68, attacker=True, pose="extension")
        fighter((width * 0.55, height * 0.61), scale=0.77, angle=103, attacker=False, pose="extension")
        checklist = (
            "✓ KNEES CONNECT",
            "✓ HIPS UNDER ELBOW",
            "✓ CONTROL, THEN EXTEND",
        )
        for line_index, text_value in enumerate(checklist):
            draw.text((right - 196, top + 15 + line_index * 24), text_value, fill=accent, font=small)
        draw.text((left + 18, bottom - 38), "HOLD  /  RECOGNIZE", fill=ink, font=body)
    return image


def _still_record(
    role: str,
    index: int,
    image: Image.Image,
    path: Path,
    root: Path,
    *,
    art_bible_hash: str,
    cast: Mapping[str, Any],
    treatment: Mapping[str, Any],
) -> dict[str, Any]:
    image.save(path, format="PNG", optimize=False, compress_level=9)
    function = _role_function(role, treatment)
    overlay_anchors = _role_overlay(role)
    signature = "|".join(
        (
            role,
            function,
            str(treatment.get("id") or f"treatment_{index + 1:02d}"),
            "filled_cast",
            "stable_screen_direction",
        )
    )
    return {
        "still_id": f"still_{index + 1:02d}",
        "role": role,
        "role_aliases": sorted(_ROLE_ALIASES.get(role, frozenset({role}))),
        "composition": function,
        "visual_function": function,
        "treatment_id": str(treatment.get("id") or f"treatment_{index + 1:02d}"),
        "path": path.relative_to(root).as_posix(),
        "width": image.width,
        "height": image.height,
        "image_hash": hashlib.sha256(path.read_bytes()).hexdigest(),
        "phash": _dct_phash(image),
        "signature": signature,
        "art_bible_hash": art_bible_hash,
        "cast": _deep_copy(dict(cast)),
        "safe_zones": _safe_zones(),
        "overlay_anchors": overlay_anchors,
        "reviewed_overlay_anchors": overlay_anchors,
        "source": "deterministic_style_board",
    }


class StyleBoardService:
    """Build and persist an immutable, reviewable six-still style board."""

    def __init__(self, *, width: int = 640, height: int = 360) -> None:
        self.width = int(width)
        self.height = int(height)
        if self.width < 64 or self.height < 64:
            raise ValueError("style-board dimensions must be at least 64px")

    def build(
        self,
        art_direction: Mapping[str, Any] | str | Path | None = None,
        output_dir: str | Path | None = None,
        *,
        art_bible: Mapping[str, Any] | str | Path | None = None,
        treatments: Mapping[str, Any] | Sequence[Any] | str | Path | None = None,
        current_art_bible_hash: str | None = None,
    ) -> dict[str, Any]:
        """Build six deterministic PNG stills and two machine-readable artifacts.

        ``art_direction`` may be the T1 resolver snapshot or the art-bible
        mapping itself.  Explicit ``art_bible``/``treatments`` values are
        accepted for direct unit tests and future pipeline adapters.
        """

        direction = (
            _load_json(art_direction, "art direction")
            if art_direction is not None
            else {}
        )
        if not isinstance(direction, Mapping):
            raise StyleBoardError("art direction must be an object")
        direction = dict(direction)
        bible = (
            _load_json(art_bible, "art bible")
            if art_bible is not None
            else _extract_art_bible(direction)
        )
        if isinstance(bible, str):
            bible = _load_json(bible, "art bible")
        if not isinstance(bible, Mapping):
            for key in ("art_bible_path", "artBiblePath", "art_direction_path"):
                candidate = direction.get(key)
                if isinstance(candidate, (str, Path)) and Path(candidate).is_file():
                    bible = _load_json(candidate, "art bible")
                    break
        if not isinstance(bible, Mapping):
            raise StyleBoardError("art bible must be an object")
        bible = dict(bible)
        resolved_hash = str(current_art_bible_hash or resolve_art_bible_hash(direction, bible)).strip().lower()
        if not resolved_hash:
            raise StyleBoardError("art bible hash cannot be empty")
        output = Path(output_dir or "style_board")
        output.mkdir(parents=True, exist_ok=True)
        still_root = output / "stills"
        still_root.mkdir(parents=True, exist_ok=True)

        palette_source = bible.get("palette") or bible.get("colors") or direction.get("palette")
        palette = dict(_DEFAULT_PALETTE)
        if isinstance(palette_source, Mapping):
            palette.update({str(key): str(value) for key, value in palette_source.items()})
        cast_source = bible.get("cast") or bible.get("characters") or direction.get("cast")
        cast = dict(_DEFAULT_CAST)
        if isinstance(cast_source, Mapping):
            for key, value in cast_source.items():
                if isinstance(value, Mapping):
                    cast[str(key)] = dict(value)
        treatment_input: Any = treatments
        if isinstance(treatment_input, (str, Path)):
            treatment_input = _load_json(treatment_input, "treatments")
        treatment_list = _normalize_treatments(direction, treatment_input)
        stills: list[dict[str, Any]] = []
        for index, role in enumerate(STYLE_BOARD_STILL_ROLES):
            treatment = _treatment_for_role(role, index, treatment_list)
            image = _draw_still(
                role,
                index,
                width=self.width,
                height=self.height,
                palette=palette,
                cast=cast,
                treatment=treatment,
            )
            stills.append(
                _still_record(
                    role,
                    index,
                    image,
                    still_root / f"{index + 1:02d}_{role}.png",
                    output,
                    art_bible_hash=resolved_hash,
                    cast=cast,
                    treatment=treatment,
                )
            )

        # A deterministic contact sheet is the operator-facing review surface;
        # the six individual stills remain the machine-facing evidence.
        sheet = Image.new("RGB", (self.width * 2, self.height * 3), _color(palette.get("background"), _DEFAULT_PALETTE["background"]))
        for index, still in enumerate(stills):
            still_image = Image.open(output / still["path"]).convert("RGB")
            sheet.paste(still_image, ((index % 2) * self.width, (index // 2) * self.height))
        contact_sheet_path = output / "style_board.png"
        sheet.save(contact_sheet_path, format="PNG", optimize=False, compress_level=9)
        contact_sheet_hash = hashlib.sha256(contact_sheet_path.read_bytes()).hexdigest()

        treatment_records = [
            {
                "id": str(item.get("id") or f"treatment_{index + 1:02d}"),
                "function": _role_function(
                    str(item.get("function") or item.get("visual_function") or ""),
                    item,
                ),
            }
            for index, item in enumerate(treatment_list)
            if isinstance(item, Mapping)
        ]
        if not treatment_records:
            treatment_records = [
                {"id": still["treatment_id"], "function": still["composition"]}
                for still in stills
            ]

        # Renderer-facing artifacts deliberately copy only internal style
        # atoms.  Study paths, creator names, source frames, and imitation
        # prompts are never copied from the input snapshot.
        board_core: dict[str, Any] = {
            "schema_version": STYLE_BOARD_VERSION,
            "art_bible_id": str(
                bible.get("id")
                or direction.get("art_bible_id")
                or "art-bible"
            ),
            "art_bible_hash": resolved_hash,
            "still_count": len(stills),
            "contact_sheet_path": "style_board.png",
            "contact_sheet_hash": contact_sheet_hash,
            "required_roles": list(STYLE_BOARD_STILL_ROLES),
            "roles": list(STYLE_BOARD_STILL_ROLES),
            "composition_functions": list(COMPOSITION_FUNCTIONS),
            "treatments": treatment_records,
            "stills": stills,
            "cast": _deep_copy(cast),
            "palette": _deep_copy(palette),
            "provider_calls": 0,
            "approval_granted": False,
            "source": "deterministic_style_board",
        }
        board = dict(board_core)
        board["artifact_hash"] = sha256_json(board_core)
        artifact_path = output / "style_board.json"
        artifact_path.write_bytes(canonical_json(board) + b"\n")
        review_core = {
            "schema_version": STYLE_BOARD_REVIEW_PACKET_VERSION,
            "style_board_artifact": "style_board.json",
            "contact_sheet_path": "style_board.png",
            "contact_sheet_hash": contact_sheet_hash,
            "style_board_hash": board["artifact_hash"],
            "art_bible_id": board["art_bible_id"],
            "art_bible_hash": resolved_hash,
            "still_count": len(stills),
            "stills": _deep_copy(stills),
            "required_roles": list(STYLE_BOARD_STILL_ROLES),
            "approval_granted": False,
            "provider_calls": 0,
        }
        review_packet = dict(review_core)
        review_packet["artifact_hash"] = sha256_json(review_core)
        review_path = output / "review-packet.json"
        review_path.write_bytes(canonical_json(review_packet) + b"\n")
        return {
            **board,
            "artifact_path": artifact_path.as_posix(),
            "review_packet_path": review_path.as_posix(),
            "contact_sheet_path": contact_sheet_path.as_posix(),
        }

    render = build
    create = build
    persist = build
    render_style_board = build

    def run_stage(self, job: VideoRun, ctx: StageContext) -> StageOutput:
        """Pipeline adapter used by the parent T4 integration slice."""

        payload = job.input_payload if isinstance(job.input_payload, Mapping) else {}
        configs = ctx.configs if isinstance(ctx.configs, Mapping) else {}
        direction: Any = payload.get("art_direction") or payload.get("art_direction_snapshot")
        if direction is None:
            direction = payload.get("art_bible")
        if direction is None:
            direction = configs.get("art_direction") or configs.get("art_bible")
        for candidate in (
            ctx.job_dir / "art_direction.json",
            ctx.job_dir / "art_bible.json",
            ctx.job_dir / "art_bible.v1.json",
        ):
            if direction is None and candidate.is_file():
                direction = candidate
                break
        if direction is None:
            raise FileNotFoundError(
                "art_direction.json or art_bible.json is required before style-board rendering"
            )
        treatments: Any = (
            payload.get("treatments")
            or payload.get("visual_treatments")
            or payload.get("visual_treatment")
        )
        if treatments is None:
            treatments = (
                configs.get("visual_treatments")
                or configs.get("visual_treatment")
                or configs.get("treatments")
            )
        if treatments is None:
            for candidate in (
                ctx.job_dir / "visual_treatments.json",
                ctx.job_dir / "visual_treatment.json",
                ctx.job_dir / "treatments.json",
            ):
                if candidate.is_file():
                    treatments = candidate
                    break
        result = self.build(
            direction,
            ctx.job_dir / "style_board",
            treatments=treatments,
            current_art_bible_hash=(
                payload.get("art_bible_hash")
                or configs.get("art_bible_hash")
                or None
            ),
        )
        return StageOutput(
            {
                "artifact_path": "style_board/style_board.json",
                "review_packet_path": "style_board/review-packet.json",
                "still_count": len(result["stills"]),
                "art_bible_hash": result["art_bible_hash"],
                "approval_granted": False,
                "provider_calls": 0,
            }
        )


def run_style_board_stage(job: VideoRun, ctx: StageContext) -> StageOutput:
    return StyleBoardService().run_stage(job, ctx)


run_stage = run_style_board_stage


__all__ = [
    "COMPOSITION_FUNCTIONS",
    "REQUIRED_COMPOSITION_FUNCTIONS",
    "REQUIRED_STILL_ROLES",
    "REQUIRED_STILLS",
    "STYLE_BOARD_ROLES",
    "STYLE_BOARD_STILLS",
    "STYLE_BOARD_REVIEW_PACKET_VERSION",
    "STYLE_BOARD_STILL_ROLES",
    "STYLE_BOARD_VERSION",
    "StyleBoardError",
    "StyleBoardService",
    "canonical_json",
    "resolve_art_bible_hash",
    "sha256_json",
    "run_style_board_stage",
    "run_stage",
]
