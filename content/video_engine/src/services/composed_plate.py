"""Composed plates — figures drawn as real type, never generated as pixels.

The strongest references reviewed on 2026-08-22 put *typography* in the content
zone, not illustration: a board reading ``YR 1: $55,000``, an arithmetic stack
``$50K + $36K`` over a rule giving ``$86K TOTAL IN.``, a labelled ``3% BOND``
against ``5% BOND``. All of that lettering is crisp because it is composited, not
generated.

So this module renders SVG from structured values. SVG is text, which makes the
output byte-identical across runs, free of garbling, free of drift, and seek-safe
in HyperFrames. Composed slots never enter the prompt pack, so they cost nothing.

Arithmetic is verified before it is drawn: a stack whose declared total does not
match its operands is refused rather than rendered. A plate that shows a wrong
number is worse than no plate.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft7Validator

from content.video_engine.src.services.artifact_io import (
    load_json,
    stamp_artifact_hash,
    write_artifact,
)
from content.video_engine.src.services.style_packs import get_pack

COMPOSED_PLATE_VERSION = "composed_plate.v1"
PLATE_KIND_COMPOSED = "composed_plate"
PLATE_KIND_GENERATED = "generated_plate"

_VIDEO_ENGINE_ROOT = Path(__file__).resolve().parents[2]
_CONFIG_DIR = _VIDEO_ENGINE_ROOT / "configs"

_WIDTH = 1920
_HEIGHT = 1080
#: The evidence zone every lane reserves. Composed content never overlaps the
#: character, which is what protects legibility at any rendition level.
_ZONE = {"x": 96, "y": 140, "w": 1100, "h": 800}
_ARITHMETIC_TOLERANCE = 0.005

_REQUIRED_CONTENT = {
    "figure_board": ("rows",),
    "arithmetic_stack": ("operands", "total"),
    "comparison_pair": ("pair",),
    "stat_row": ("stats",),
}


class ComposedPlateError(ValueError):
    """The plate could not be composed, or its figures do not reconcile."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "invalid composed plate")


def _schema_errors(payload: Mapping[str, Any]) -> list[str]:
    schema = load_json(_CONFIG_DIR / "composed_plate.schema.json", "composed plate schema")
    validator = Draft7Validator(schema)
    return [
        "plate" + "".join(f"[{part!r}]" for part in error.absolute_path) + f": {error.message}"
        for error in sorted(validator.iter_errors(dict(payload)), key=lambda e: list(e.absolute_path))
    ]


def _layout_errors(payload: Mapping[str, Any]) -> list[str]:
    layout = str(payload.get("layout") or "")
    content = payload.get("content") or {}
    required = _REQUIRED_CONTENT.get(layout, ())
    return [
        f"layout {layout!r} requires content.{field}"
        for field in required
        if not content.get(field)
    ]


def _arithmetic_errors(payload: Mapping[str, Any]) -> list[str]:
    """A stack that does not add up is refused, not drawn."""

    if payload.get("layout") != "arithmetic_stack":
        return []
    content = payload.get("content") or {}
    operands = content.get("operands") or []
    total = content.get("total") or {}
    if not operands or "amount" not in total:
        return []
    computed = sum(float(item.get("amount") or 0.0) for item in operands)
    declared = float(total.get("amount") or 0.0)
    if abs(computed - declared) <= _ARITHMETIC_TOLERANCE:
        return []
    return [
        f"arithmetic does not reconcile: operands sum to {computed:g} but total "
        f"declares {declared:g}; a plate showing a wrong number is worse than no plate"
    ]


def _tone_colours(lane: str) -> dict[str, str]:
    pack = get_pack(lane)
    semantics = pack.get("colour_semantics") or {}
    palette = (pack.get("background") or {}).get("palette") or ["#FFFFFF"]
    return {
        "positive": semantics.get("positive", "#2E7D32"),
        "negative": semantics.get("negative", "#C62828"),
        "neutral": "#25313C",
        "accent": semantics.get("accent", "#1769C2"),
        "ground": palette[0],
    }


def validate_composed_plate(
    value: Mapping[str, Any] | str | Path,
) -> dict[str, Any]:
    """Validate a plate and stamp its artifact hash."""

    payload = dict(load_json(value, "composed plate"))
    payload["schema_version"] = COMPOSED_PLATE_VERSION
    payload.pop("artifact_hash", None)
    stamp_artifact_hash(payload)

    errors = _schema_errors(payload)
    if errors:
        raise ComposedPlateError(errors)

    errors.extend(_layout_errors(payload))
    errors.extend(_arithmetic_errors(payload))
    if errors:
        raise ComposedPlateError(errors)
    return payload


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _text(x: int, y: int, value: Any, *, size: int, fill: str, weight: int = 700,
          anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Inter, system-ui, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{_esc(value)}</text>'
    )


_ARROWS = {"up": "↑", "down": "↓", "flat": "→"}


def _figure_board(content: Mapping[str, Any], tones: Mapping[str, str]) -> list[str]:
    parts: list[str] = []
    y = _ZONE["y"] + 120
    for row in content.get("rows") or []:
        colour = tones[str(row.get("tone") or "neutral")]
        arrow = _ARROWS.get(str(row.get("direction") or ""), "")
        parts.append(_text(_ZONE["x"], y, f"{row['label']}:", size=64, fill=tones["neutral"]))
        parts.append(
            _text(
                _ZONE["x"] + _ZONE["w"],
                y,
                f"{row['value']} {arrow}".strip(),
                size=64,
                fill=colour,
                anchor="end",
            )
        )
        y += 110
    return parts


def _arithmetic_stack(content: Mapping[str, Any], tones: Mapping[str, str]) -> list[str]:
    parts: list[str] = []
    operands = list(content.get("operands") or [])
    total = content.get("total") or {}
    y = _ZONE["y"] + 120
    right = _ZONE["x"] + _ZONE["w"]
    for index, item in enumerate(operands):
        colour = tones[str(item.get("tone") or "neutral")]
        sign = "" if index == 0 else "+"
        parts.append(_text(_ZONE["x"], y, sign, size=72, fill=tones["neutral"]))
        parts.append(_text(right, y, item["label"], size=72, fill=colour, anchor="end"))
        y += 110
    parts.append(
        f'<line x1="{_ZONE["x"]}" y1="{y - 60}" x2="{right}" y2="{y - 60}" '
        f'stroke="{tones["neutral"]}" stroke-width="6"/>'
    )
    parts.append(_text(right, y + 50, total["label"], size=84, fill=tones["accent"], anchor="end"))
    return parts


def _comparison_pair(content: Mapping[str, Any], tones: Mapping[str, str]) -> list[str]:
    parts: list[str] = []
    half = _ZONE["w"] // 2
    for index, item in enumerate(content.get("pair") or []):
        cx = _ZONE["x"] + half * index + half // 2
        colour = tones[str(item.get("tone") or "neutral")]
        parts.append(
            f'<rect x="{_ZONE["x"] + half * index + 24}" y="{_ZONE["y"] + 60}" '
            f'width="{half - 48}" height="420" rx="24" fill="none" '
            f'stroke="{tones["neutral"]}" stroke-width="5"/>'
        )
        parts.append(_text(cx, _ZONE["y"] + 260, item["value"], size=110, fill=colour, anchor="middle"))
        parts.append(
            _text(cx, _ZONE["y"] + 370, item["label"], size=54, fill=tones["neutral"],
                  weight=500, anchor="middle")
        )
    return parts


def _stat_row(content: Mapping[str, Any], tones: Mapping[str, str]) -> list[str]:
    stats = list(content.get("stats") or [])
    parts: list[str] = []
    width = _ZONE["w"] // max(1, len(stats))
    for index, stat in enumerate(stats):
        cx = _ZONE["x"] + width * index + width // 2
        colour = tones[str(stat.get("tone") or "neutral")]
        parts.append(_text(cx, _ZONE["y"] + 220, stat["value"], size=96, fill=colour, anchor="middle"))
        parts.append(
            _text(cx, _ZONE["y"] + 300, stat["caption"], size=42, fill=tones["neutral"],
                  weight=500, anchor="middle")
        )
    return parts


_RENDERERS = {
    "figure_board": _figure_board,
    "arithmetic_stack": _arithmetic_stack,
    "comparison_pair": _comparison_pair,
    "stat_row": _stat_row,
}


def render_plate_svg(plate: Mapping[str, Any]) -> str:
    """Deterministic SVG. Same values in, byte-identical markup out."""

    tones = _tone_colours(str(plate.get("lane")))
    body: list[str] = [
        f'<rect width="{_WIDTH}" height="{_HEIGHT}" fill="{tones["ground"]}"/>'
    ]
    title = plate.get("title")
    if title:
        body.append(_text(_ZONE["x"], _ZONE["y"], title, size=56, fill=tones["neutral"]))
    body.extend(_RENDERERS[str(plate["layout"])](plate.get("content") or {}, tones))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{_WIDTH}" height="{_HEIGHT}" '
        f'viewBox="0 0 {_WIDTH} {_HEIGHT}" role="img">'
        + "".join(body)
        + "</svg>"
    )


def compose_and_write(
    plate: Mapping[str, Any] | str | Path,
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Validate, render and persist a composed plate as SVG plus its artifact."""

    validated = validate_composed_plate(plate)
    out = Path(output_dir) / "composed_plates"
    json_path = write_artifact(out / f"{validated['plate_id']}.json", validated)
    svg_path = out / f"{validated['plate_id']}.svg"
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(render_plate_svg(validated), encoding="utf-8")
    return {
        "plate_id": validated["plate_id"],
        "layout": validated["layout"],
        "plate_hash": validated["artifact_hash"],
        "svg_path": str(svg_path),
        "artifact_path": str(json_path),
        "generation_cost_usd": 0.0,
    }


def plate_kind(slot: Mapping[str, Any]) -> str:
    """Default to generated so existing coverage keeps its behaviour."""

    kind = str(slot.get("plate_kind") or PLATE_KIND_GENERATED)
    if kind not in {PLATE_KIND_GENERATED, PLATE_KIND_COMPOSED}:
        raise ComposedPlateError(
            [f"slot {slot.get('slot_id')!r} declares unknown plate_kind {kind!r}"]
        )
    return kind


def is_composed(slot: Mapping[str, Any]) -> bool:
    return plate_kind(slot) == PLATE_KIND_COMPOSED
