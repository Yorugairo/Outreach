"""A dock that reads at one box and parks at another (2026-09-10): `read` names the box a centred card pops at, `read_s` /
`park_s` its own clock; a centred card may sit on either slot. The template's choreography (PHASE A read, PHASE B the
minimum-jerk park) is the one the clips have had since E44 - a centred card only stopped short-circuiting it."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402

PLACE = {"x": 600, "y": 420, "w": 430, "h": 430}
READ = {"x": 227, "y": 880, "w": 626, "h": 294}


def test_read_and_the_clock_are_dock_options_a_centred_card_may_carry():
    o = B.dock_opts({"centre": True, "card_aspect": 1.0, "centre_w": 0.4, "centre_x": 0.77, "centre_y": 0.335,
                     "read": {"centre_w": 0.58, "centre_x": 0.5, "centre_y": 0.535, "card_aspect": 0.47}, "read_s": 1.54, "park_s": 0.7})
    assert o["read"]["centre_w"] == 0.58 and o["read_s"] == 1.54 and o["park_s"] == 0.7


@pytest.mark.parametrize("raw, needle", [
    ({"read": {"centre_w": 0.5}}, "CENTRED card's option"),
    ({"centre": True, "read": {"wobble": 1}}, "read must be a dict of"),
    ({"centre": True, "read": {"centre_w": 1.4}}, "positive share of the stage"),
    ({"centre": True, "read": {"centre_w": 0.5}, "read_s": 0}, "seconds > 0"),
    ({"centre": True, "read": {"centre_w": 0.5}, "park_s": -1}, "seconds > 0"),
])
def test_a_reading_box_is_checked(raw, needle):
    with pytest.raises(ValueError) as e:
        B.dock_opts(raw)
    assert needle in str(e.value)


def test_a_dock_entry_carries_its_reading_box_and_its_own_clock():
    d = B.dock_entry("dock-x", 1, 10.0, 16.0, 0, B.DOCK_KIND_IMAGE, PLACE, None, None, True, read_place=READ, read_s=1.54, park_s=0.7)
    assert d["slot"] == 1 and d["place"] == PLACE and d["read_place"] == READ and d["centre"] is True
    assert d["read_s"] == 1.54 and d["park_s"] == 0.7 and d["park"] is True, "6 s holds a 1.54 s read and a 0.7 s park"
    plain = B.dock_entry("dock-x", 0, 10.0, 16.0, 0, B.DOCK_KIND_IMAGE, PLACE, None, None, True)
    assert "read_place" not in plain and plain["read_s"] == B.DOCK_READ_S and plain["park_s"] == B.DOCK_PARK_S, "without a read box: exactly as it was"
    short = B.dock_entry("dock-x", 0, 10.0, 11.0, 0, B.DOCK_KIND_IMAGE, PLACE, None, None, True, read_place=READ, read_s=1.54, park_s=0.7)
    assert short["park"] is False, "too short to hold both phases: the card stays at reading size"
