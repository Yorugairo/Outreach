"""The chip readability profile is optional, but closed when declared."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402


PLATE = "world-spike-desk-v1"
STILL = (0, 0, 0)


def _chip(**overrides):
    entry = {
        "kind": "chip",
        "at": 10.0,
        "dur": 6.0,
        "icon": "factory",
        "label": "STEEL",
        "target": {"kind": "point", "x": 0.3, "y": 0.5},
    }
    entry.update(overrides)
    return entry


def test_chip_without_readability_keeps_legacy_contract():
    assert B.validate_species([_chip()], STILL, PLATE) == []


def test_chip_accepts_the_only_supported_readability_profile():
    assert B.validate_species([_chip(readability="landscape-phone")], STILL, PLATE) == []


def test_chip_rejects_unknown_readability_profile_instead_of_falling_back():
    errors = B.validate_species([_chip(readability="landscape-phon")], STILL, PLATE)
    assert errors == ["chip: readability must be 'landscape-phone'"], errors


def test_chip_rejects_non_string_readability_profile():
    errors = B.validate_species([_chip(readability=None)], STILL, PLATE)
    assert errors == ["chip: readability must be 'landscape-phone'"], errors
