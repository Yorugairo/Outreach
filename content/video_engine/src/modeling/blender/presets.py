"""Bounded, Blender-independent controls for the diagnostic native model family.

The family is an editable starting point. Its controls do not imply a finished
character, likeness, or deformation approval.
"""

from __future__ import annotations

import copy
import math
from collections.abc import Mapping
from typing import Any


FAMILY_ID = "martial-matters-fighter-family-v1"

BODY_BOUNDS = {
    "height": (0.40, 0.62),
    "muscle": (0.35, 0.78),
    "weight": (0.28, 0.68),
    "proportions": (0.38, 0.64),
}

FACE_TARGETS = {
    "head_width": {
        "asset": "head/head-scale-horiz-incr.target.gz",
        "minimum": 0.0,
        "maximum": 0.25,
    },
    "nose_depth": {
        "asset": "nose/nose-scale-depth-incr.target.gz",
        "minimum": 0.0,
        "maximum": 0.25,
    },
    "jaw_drop": {
        "asset": "chin/chin-jaw-drop-incr.target.gz",
        "minimum": 0.0,
        "maximum": 0.20,
    },
    "hand_scale": {
        "asset": ["hands/l-hand-scale-incr.target.gz", "hands/r-hand-scale-incr.target.gz"],
        "minimum": 0.0,
        "maximum": 0.25,
    },
}

HAIR_STYLES = ("crop", "quiff")
CLOTHING_STYLES = ("fight_kit", "warmup")
SKIN_PALETTES = {
    "sand": (0.57, 0.31, 0.20, 1.0),
    "rose": (0.48, 0.22, 0.18, 1.0),
    "deep": (0.25, 0.095, 0.055, 1.0),
}
CLOTHING_PALETTES = {
    "cobalt": (0.025, 0.14, 0.42, 1.0),
    "brick": (0.42, 0.055, 0.035, 1.0),
    "teal": (0.015, 0.26, 0.22, 1.0),
}

DEFAULT_CONTROLS: dict[str, Any] = {
    "body": {"height": 0.56, "muscle": 0.70, "weight": 0.42, "proportions": 0.55},
    "face": {"head_width": 0.16, "nose_depth": 0.12, "jaw_drop": 0.08, "hand_scale": 0.12},
    "hair_style": "quiff",
    "clothing_style": "fight_kit",
    "skin_palette": "sand",
    "clothing_palette": "cobalt",
}


def resolve_controls(overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return a complete controls object and reject unknown or out-of-range values."""
    result = copy.deepcopy(DEFAULT_CONTROLS)
    if overrides is None:
        return result
    if not isinstance(overrides, Mapping):
        raise TypeError("preset controls must be a mapping")

    allowed_top = set(result)
    unknown_top = set(overrides) - allowed_top
    if unknown_top:
        raise ValueError(f"unknown preset control(s): {', '.join(sorted(map(str, unknown_top)))}")

    for group in ("body", "face"):
        if group not in overrides:
            continue
        values = overrides[group]
        if not isinstance(values, Mapping):
            raise TypeError(f"{group} controls must be a mapping")
        allowed = BODY_BOUNDS if group == "body" else FACE_TARGETS
        unknown = set(values) - set(allowed)
        if unknown:
            raise ValueError(f"unknown {group} control(s): {', '.join(sorted(map(str, unknown)))}")
        for key, raw in values.items():
            low, high = (BODY_BOUNDS[key] if group == "body" else
                         (FACE_TARGETS[key]["minimum"], FACE_TARGETS[key]["maximum"]))
            if isinstance(raw, bool) or not isinstance(raw, (int, float)) or not math.isfinite(float(raw)):
                raise ValueError(f"{group}.{key} must be a finite number")
            value = float(raw)
            if not low <= value <= high:
                raise ValueError(f"{group}.{key} must be between {low} and {high}")
            result[group][key] = value

    for key, allowed in (
        ("hair_style", HAIR_STYLES),
        ("clothing_style", CLOTHING_STYLES),
        ("skin_palette", tuple(SKIN_PALETTES)),
        ("clothing_palette", tuple(CLOTHING_PALETTES)),
    ):
        if key in overrides:
            value = overrides[key]
            if not isinstance(value, str) or value not in allowed:
                raise ValueError(f"{key} must be one of: {', '.join(allowed)}")
            result[key] = value

    return result


def family_manifest() -> dict[str, Any]:
    """Portable manifest for controls; no Blender import is required."""
    return {
        "schema_version": "native_character_preset.v1",
        "family_id": FAMILY_ID,
        "status": "diagnostic_only",
        "art_approval": "not_approved",
        "base": {
            "generator": "MPFB 2.0.17",
            "rig": "Blender Rigify",
            "editable_source": "native/fighter-family-v1.blend",
        },
        "controls": {
            "body": {key: {"minimum": low, "maximum": high} for key, (low, high) in BODY_BOUNDS.items()},
            "face": {key: {"minimum": value["minimum"], "maximum": value["maximum"],
                           "target": value["asset"]} for key, value in FACE_TARGETS.items()},
            "hair_style": list(HAIR_STYLES),
            "clothing_style": list(CLOTHING_STYLES),
            "skin_palette": list(SKIN_PALETTES),
            "clothing_palette": list(CLOTHING_PALETTES),
        },
        "default_parameters": copy.deepcopy(DEFAULT_CONTROLS),
        "license_basis": {
            "mpfb_code": "GPL-3.0-or-later",
            "bundled_mesh_and_target_assets": "CC0-1.0",
            "generated_output": "MPFB upstream LICENSE.md section D states that generated output is user data; this family adds original Blender-authored geometry and materials.",
            "recorded_source": "content/video_engine/tests/fixtures/modeling/baseline/tools/mpfb2/LICENSE.md (local T1 tool cache; MPFB commit 80919fa4682335c41847f761a4d79dcad4124732)",
        },
        "scope_note": "Diagnostic body/rig family and authoring controls only. No fighter identity, likeness, motion-quality or operator-art approval is claimed.",
    }
