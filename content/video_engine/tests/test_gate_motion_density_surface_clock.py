"""The motion gate must read the player's registered surface-arrival clock."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402

BED_TIMELINE = (ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/build-bed"
                / "fed-liquidity-bed.timeline.json")


def _surface_scene() -> dict:
    return {
        "scene_id": "s02",
        "span": [9.15, 21.35],
        "world": {
            "kind": "ledger",
            "page": {
                "enter": "surface",
                "surface_from": {"grow_s": 0.45},
            },
            "page_states": [{"schema_version": "ledger_page.v1"}],
        },
        "species": [
            {"kind": "spotlight", "at": 9.60, "dur": 1.2,
             "target": {"kind": "datum", "index": 2}},
            {"kind": "chart_to", "to": "recast", "at": 11.85, "dur": 1.2, "state": 1},
        ],
    }


def test_registered_surface_uses_native_grow_clock_not_ledger_rollout():
    scene = _surface_scene()
    assert G._page_land_offset(scene) == pytest.approx(0.45)
    assert G._page_land_offset(scene) != G.PAGE_BUILD_END_S


def test_surface_prebind_uses_native_clock_until_binder_stamps_grow_s():
    scene = _surface_scene()
    del scene["world"]["page"]["surface_from"]["grow_s"]
    scene["world"]["page"]["surface_from"].update({"surface": "center-paper", "lead_s": 1.2})
    assert G._page_land_offset(scene) == pytest.approx(G.SURFACE_GROW_S)
    assert G._page_land_offset(scene) != 0.0
    assert B.CAMERA_ARRIVAL_S == pytest.approx(G.SURFACE_GROW_S)
    assert B.page_build_windows(scene["world"], scene["species"], scene["span"][0]) == [(9.15, 9.6)]


@pytest.mark.skipif(not BED_TIMELINE.exists(), reason="bed timeline not on disk")
def test_bed_surface_metadata_is_the_gate_clock():
    timeline = json.loads(BED_TIMELINE.read_text(encoding="utf-8"))
    scene = next(s for s in timeline["scenes"] if s["scene_id"] == "s02")
    page = scene["world"]["page"]
    assert page["enter"] == "surface"
    assert page["surface_from"]["grow_s"] == pytest.approx(0.45)
    assert G._page_land_offset(scene) == pytest.approx(page["surface_from"]["grow_s"])


def test_m11_and_m23_share_surface_landing():
    scene = _surface_scene()
    timeline = {"runtime_s": 30.0, "scenes": [scene], "caption_pages": []}
    first = G._first_chart_gate(timeline, [], {"cues": [{"kind": "evidence", "in": 9.15}]})
    assert first.level == "PASS"
    assert "build lands at 9.6s" in first.message
    transition = G._transitions([scene])
    assert transition == [{"scene": "s02", "to": "recast", "at": 11.85, "dur": 1.2,
                          "end": 13.05, "follows": False, "in_build": False,
                          "at_edge": False}]


def _mode_timeline(*, form=None, aspect="16:9", runtime=178.0) -> dict:
    timeline = {
        "runtime_s": runtime,
        "aspect": aspect,
        "scenes": [{"scene_id": "s01", "span": [0.0, runtime],
                    "world": {"kind": "plate", "asset": "test"}, "species": []}],
        "caption_pages": [],
    }
    if form is not None:
        timeline["form"] = form
    return timeline


def test_explicit_long_form_wins_at_authentic_pilot_runtime_and_m16_is_not_binding():
    timeline = _mode_timeline(form="long")
    assert G._is_short(timeline, 178.0) is False
    assert G._first_chart_window(timeline)[:2] == (G.PARADOX_S, G.FIRST_CHART_MAX_S)
    gates, _ = G.run(timeline, [], {})
    assert next(g for g in gates if g.id == "M16").level == "INFO"


def test_explicit_short_form_overrides_long_runtime_without_relaxing_pulse():
    timeline = _mode_timeline(form="short")
    assert G._is_short(timeline, 178.0) is True
    gates, _ = G.run(timeline, [], {})
    assert next(g for g in gates if g.id == "M16").level == "FAIL"


def test_absent_form_preserves_legacy_aspect_and_runtime_read():
    assert G._is_short(_mode_timeline(runtime=179.0), 179.0) is True
    assert G._is_short(_mode_timeline(runtime=180.0), 180.0) is False
    assert G._is_short(_mode_timeline(aspect="9:16", runtime=240.0), 240.0) is True


@pytest.mark.parametrize("form", [None, "medium", 1, {"short": True}])
def test_invalid_or_inconsistent_form_fails_closed(form):
    timeline = _mode_timeline(form=form)
    if form is None:
        # An explicit null is distinct from an omitted legacy field.
        timeline["form"] = None
    gates, _ = G.run(timeline, [], {})
    form_gate = next(g for g in gates if g.id == "M00")
    assert form_gate.level == "FAIL"
    assert G._is_short(timeline, 178.0) is True


def test_long_form_portrait_is_rejected_and_fails_closed():
    timeline = _mode_timeline(form="long", aspect="9:16")
    gates, _ = G.run(timeline, [], {})
    form_gate = next(g for g in gates if g.id == "M00")
    assert form_gate.level == "FAIL"
    assert "portrait" in form_gate.message
    assert G._is_short(timeline, 178.0) is True


def test_readable_species_reserve_is_the_actual_caption_pin_and_keeps_word_events():
    pages = [{"s": 1.0, "e": 2.0, "cap_mode": "anchor", "cap_reserve": "readable-species",
              "t": [{"s": 1.25}, {"s": 1.75}]}]
    rows, counts = G._caption_page_rows({"scenes": []}, pages)
    assert [row["t"] for row in rows] == [1.0, 1.25, 1.75]
    assert counts["modes"] == {"anchor": 1}


def test_readable_species_reserve_can_pin_without_cap_mode_but_unknown_reserve_cannot():
    valid = [{"s": 1.0, "e": 2.0, "cap_reserve": "readable-species", "t": []}]
    invalid = [{"s": 1.0, "e": 2.0, "cap_mode": "anchor", "cap_reserve": "stage", "t": [{"s": 1.25}]}]
    rows, counts = G._caption_page_rows({"scenes": []}, valid)
    assert [row["t"] for row in rows] == [1.0]
    assert counts["modes"] == {"anchor": 1}
    rows, counts = G._caption_page_rows({"scenes": []}, invalid)
    assert rows == []
    assert counts["unpinned_anchor"] == 1
