"""P37 T1 - M14 (47 s2 G-a): a camera move may not overlap an evidence build. The eye is
blind during a saccade (doc 07 Pillar 4), so a punch that lands while a card is wiping in or
a badge is revealing throws the build away."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402


def _tl(punch_at: float, dock_enter: float = 10.0, badges=(11.75, 13.05)) -> tuple[dict, list]:
    scene = {"scene_id": "s01", "world": {"asset_id": "w1", "ken_burns": {"scale": 0}}, "span": [0.0, 30.0],
             "docks": [{"slide": "ev-1", "slot": 0, "enter": dock_enter, "exit": 25.0, "badge_at": list(badges)}],
             "species": [{"kind": "punch", "at": punch_at, "dur": 1.2, "target": {"kind": "point", "x": 0.5, "y": 0.5}}]}
    return {"runtime_s": 30.0, "scenes": [scene], "caption_pages": []}, []


def _m14(tl, docks) -> G.Gate:
    return next(g for g in G.run(tl, docks, {"cues": []})[0] if g.id == "M14")


def test_build_window_spans_the_entrance_and_the_last_badge_settle():
    tl, docks = _tl(punch_at=20.0)
    (slide, a, z), = G._build_windows(tl["scenes"], docks)
    assert (slide, a, z) == ("ev-1", 10.0, 13.05 + G.BADGE_SETTLE_S)


def test_punch_during_the_card_entrance_fails():
    g = _m14(*_tl(punch_at=10.4))
    assert g.level == "FAIL" and "punch 10.4-11.6s over ev-1 build 10.0-13.7s" in g.message and g.src == G.SRC_M14


def test_punch_during_a_badge_reveal_fails():
    assert _m14(*_tl(punch_at=12.5)).level == "FAIL"


def test_punch_after_the_build_settles_passes():
    g = _m14(*_tl(punch_at=14.0))
    assert g.level == "PASS", g.message


def test_fallback_dock_shape_is_read_too():
    tl = {"runtime_s": 30.0, "caption_pages": [],
          "scenes": [{"scene_id": "s01", "world": {"asset_id": "w1"}, "span": [0.0, 30.0],
                      "species": [{"kind": "focus_zoom", "at": 10.5, "dur": 1.0, "target": {"kind": "point", "x": 0.5, "y": 0.5}}]}]}
    docks = [{"asset": "ev-9", "at": 10.0, "end": 20.0}]
    assert _m14(tl, docks).level == "FAIL"
    docks = [{"asset": "ev-9", "at": 5.0, "end": 8.0}]
    assert _m14(tl, docks).level == "PASS"
