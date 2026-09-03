"""Motion-density gate (ruling E21 / doc 29 s9.25): red on Steel and Paper as
shipped, green on a dense synthetic build."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402

BUILD = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f"
needs_ep1 = pytest.mark.skipif(not (BUILD / "steel-and-paper.timeline.json").exists(), reason="episode one build not on disk")


def _by_id(gates):
    return {g.id: g for g in gates}


@needs_ep1
def test_red_steel_and_paper_as_shipped():
    tl, docks, mp = G._load(BUILD, "steel-and-paper.timeline.json")
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "FAIL" and "> 12s" in g["M01"].message, g["M01"]   # 23% of runtime still
    assert g["M03"].level == "FAIL", g["M03"]                                    # P6 has no docks
    assert g["M07"].level == "FAIL", g["M07"]                                    # opening minute is the thinnest
    assert g["M08"].level == "INFO"                                              # no cap_mode yet -> required list


def _dense_build(runtime=180.0, scene_len=6.0, dock_every=20.0, stage=False):
    scenes = []
    t = 0.0
    i = 0
    while t < runtime:
        scenes.append({"scene_id": f"s{i:02d}", "world": {"asset_id": f"world-{i}"}, "span": [t, min(t + scene_len, runtime)]})
        t += scene_len; i += 1
    docks = [{"asset": f"ev-{k}", "at": a, "end": min(a + 8.0, runtime)} for k, a in enumerate([x * dock_every + 3.0 for x in range(int(runtime // dock_every))])]
    pages = []
    t = 0.0
    while t < runtime:
        pages.append({"s": t, "e": t + 1.5, "t": [{"w": "x"}] * 5}); t += 1.5
    rows = [{"t": s["span"][0], "cap_mode": "stage"} for s in scenes] if stage else []
    tl = {"runtime_s": runtime, "scenes": scenes, "caption_pages": pages, "rows": rows}
    mp = {"cues": [{"kind": "evidence", "in": d["at"] + 1.0, "out": d["at"] + 1.5} for d in docks]}
    return tl, docks, mp


def test_green_dense_build_passes():
    tl, docks, mp = _dense_build()
    gates, _ = G.run(tl, docks, mp)
    fails = [g for g in gates if g.level == "FAIL"]
    assert not fails, "\n".join(f"{g.id} {g.message}" for g in fails)


def test_still_stretch_over_12s_fails():
    tl, docks, mp = _dense_build(scene_len=15.0, dock_every=60.0)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "FAIL" and g["M03"].level == "FAIL"


def test_stage_captions_count_as_events():
    tl, docks, mp = _dense_build(scene_len=15.0, dock_every=20.0, stage=True)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M08"].level == "PASS"


def test_plate_hold_ceiling_needs_two_docks():
    tl, docks, mp = _dense_build(scene_len=25.0, dock_every=20.0)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M05"].level == "FAIL"
