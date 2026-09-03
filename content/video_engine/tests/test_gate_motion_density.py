"""Motion-density gate (ruling E21 / doc 29 s9.25): red on Steel and Paper as
shipped, green on a dense synthetic build. P35 T4: the timeline's own docks
are the dock clock (evidence-dock.json only as fallback), a LEDGER PAGE's
build beats count as visual events and its start as an evidence entry
(s9.28 C5 / D1 / D2), and `build_scene_timeline_f.world_for_plate` turns a
`ledger:` shot-table id into the page world."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BUILD = EP / "build-f"
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
    # the rebuilt ep1 declares cap_mode (P34 T5): M08 is enforced and FAILs on the dock-held stills;
    # a build predating the declaration gets the INFO list instead
    assert g["M08"].level in ("FAIL", "INFO"), g["M08"]


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


# ---- P35 T4: the timeline is the dock clock; ledger pages count ------------

def _caption_pages(runtime: float) -> list[dict]:
    pages, t = [], 0.0
    while t < runtime:
        pages.append({"s": t, "e": t + 1.5, "t": [{"w": "x"}] * 5}); t += 1.5
    return pages


def _page_window(with_page: bool):
    """A 90s build whose docks ride the TIMELINE's scenes (enter 3s and 54s) and
    whose 12-42s window is dock-free. Its first scene, 12-31s, is the ledger
    page when `with_page`: the page's beats (12, 12.6, 15.4, 16.2, 19.2) break
    the 19s still stretch and its start is the evidence entry that keeps the
    3s -> 54s wait under 45s. The page scene is 19s, not the whole window,
    because the hold after the build is STILL (s9.28 C5) - a page alone
    cannot carry 30s; only its build phase moves."""
    spans = [(0, 6), (6, 12), (12, 31), (31, 40), (40, 49), (49, 58), (58, 67), (67, 76), (76, 85), (85, 90)]
    docks_at = {0: [{"slide": "ev-a", "slot": 0, "enter": 3.0, "exit": 11.0, "badge_at": [5.05]}],
                49: [{"slide": "ev-b", "slot": 0, "enter": 54.0, "exit": 62.0, "badge_at": [56.05]}]}
    scenes = []
    for i, (a, b) in enumerate(spans):
        page = with_page and a == 12
        world = {"kind": "ledger", "page": {"schema_version": "ledger_page.v1", "builder": "story"},
                 "ken_burns": {"scale": 0.03, "x": 0, "y": 0}} if page else {"asset_id": f"world-{i}"}
        scenes.append({"scene_id": f"s{i:02d}", "world": world, "span": [float(a), float(b)], "docks": docks_at.get(a, [])})
    tl = {"runtime_s": 90.0, "scenes": scenes, "caption_pages": _caption_pages(90.0), "rows": [], "species": ["ledger"] if with_page else []}
    return tl, [], {"cues": []}


def test_page_build_counts_as_events_and_its_start_as_evidence():
    tl, docks, mp = _page_window(with_page=True)
    gates, stats = G.run(tl, docks, mp)
    g = _by_id(gates)
    assert g["M01"].level == "PASS", g["M01"]
    assert g["M03"].level == "PASS", g["M03"]
    assert g["M05"].level == "PASS", g["M05"]          # a 19s page holds like a plate, under the 20s ceiling
    assert stats["ledger_pages"] == 1 and stats["dock_source"] == "timeline"
    ev = G.analyse(tl, docks, mp)["events"]
    assert all(t in ev for t in (12.0, 12.6, 15.4, 16.2, 19.2)), ev   # roll-out, field, outline, build start, build complete


def test_same_window_without_the_page_fails_m01_and_m03():
    tl, docks, mp = _page_window(with_page=False)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "FAIL" and "19.0s at 0:12" in g["M01"].message, g["M01"]
    assert g["M03"].level == "FAIL" and "51s from 0:03" in g["M03"].message, g["M03"]


def test_page_beat_offsets_follow_the_template_lp_constants():
    # template `const LP = { ROLL: 0.6, BLEED: 2.8, OUTLINE: 0.8, ..., BUILD: 3.0 }`
    assert G.PAGE_BEAT_OFFSETS == (0.0, 0.6, 3.4, 4.2, 7.2)


def test_timeline_docks_are_the_clock_when_present():
    """scenes[].docks (enter/exit/badge_at) win over evidence-dock.json, whose
    clock drifted from the timeline's (P35 T0: divergence 26.4 vs 50.4)."""
    tl, _docks, mp = _dense_build()
    tl["scenes"][2]["docks"] = [{"slide": "ev-x", "slot": 0, "enter": 50.4, "exit": 70.9, "badge_at": [52.45, 53.75]}]
    stale_file = [{"asset": "ev-x", "at": 26.4, "end": 42.0}]
    A = G.analyse(tl, stale_file, mp)
    assert A["dock_source"] == "timeline"
    assert A["spans"] == [(50.4, 70.9)] and 26.4 not in A["events"]
    assert 52.45 in A["events"] and 53.75 in A["events"]           # badge reveals are visual events
    assert G.run(tl, stale_file, mp)[1]["dock_source"] == "timeline"


def test_evidence_dock_file_is_the_fallback_when_the_timeline_carries_no_docks():
    tl, docks, mp = _dense_build()
    assert not any(s.get("docks") for s in tl["scenes"])
    A = G.analyse(tl, docks, mp)
    assert A["dock_source"] == "evidence-dock.json" and len(A["spans"]) == len(docks)
    assert G.run(tl, docks, mp)[1]["dock_source"] == "evidence-dock.json"


@needs_ep1
def test_ep1_reads_its_own_timeline_clock_and_stays_red():
    tl, docks, mp = G._load(BUILD, "steel-and-paper.timeline.json")
    gates, stats = G.run(tl, docks, mp)
    g = _by_id(gates)
    assert stats["dock_source"] == "timeline"
    assert stats["docks"] == sum(len(s.get("docks", [])) for s in tl["scenes"])   # 43 on the shipped build, not the file's 27
    assert g["M01"].level == "FAIL" and g["M03"].level == "FAIL"                  # the baseline stays red on its own clock
    print("\nep1 on the timeline clock:", g["M01"].message, "|", g["M03"].message, "|", stats)


# ---- P35 T4: build_scene_timeline_f.world_for_plate ---------------------------

def _builder():
    import build_scene_timeline_f as B  # noqa: E402  (imports build_render_f, which reads the episode's indexes)
    return B


@needs_ep1
def test_world_for_plate_ledger_row_builds_the_page_spec():
    B = _builder()
    w = B.world_for_plate("ledger:ev-trim-proof-v1:bars:7:right", (0.04, 0, 0), EP)
    assert w["kind"] == "ledger" and "asset_id" not in w and "sha256" not in w
    page = w["page"]
    assert page["schema_version"] == "ledger_page.v1" and page["surface"] == "page"
    assert page["builder"] == "story" and page["variant"] == "bars"
    assert page["emphasize"] == 7 and page["quiet_zone"] == "right"
    assert page["source"] and page["title"] and len(page["labels"]) == len(page["value_strings"])
    assert w["ken_burns"] == {"scale": 0.04, "x": 0, "y": 0}
    assert G._is_page({"world": w}) and G._plate_id({"world": w, "scene_id": "s13"}) == "ledger:s13"


@needs_ep1
def test_world_for_plate_bogus_ledger_ids_are_hard_errors():
    B = _builder()
    with pytest.raises(ValueError, match="series file missing"):
        B.world_for_plate("ledger:ev-nope-v9:bars", (0, 0, 0), EP)
    with pytest.raises(ValueError, match="variant 'donut'"):
        B.world_for_plate("ledger:ev-trim-proof-v1:donut", (0, 0, 0), EP)
    with pytest.raises(ValueError, match="quiet_zone 'middle'"):
        B.world_for_plate("ledger:ev-trim-proof-v1:bars:1:middle", (0, 0, 0), EP)
    with pytest.raises(ValueError, match="expected ledger:"):
        B.world_for_plate("ledger:", (0, 0, 0), EP)


@needs_ep1
def test_parse_ledger_id_defaults_emphasize_and_quiet_zone():
    B = _builder()
    assert B.parse_ledger_id("ledger:ev-x:line") == ("ev-x", "line", None, "right")
    assert B.parse_ledger_id("ledger:ev-x:bars:3") == ("ev-x", "bars", 3, "right")
    assert B.parse_ledger_id("ledger:ev-x:bars::left") == ("ev-x", "bars", None, "left")


# ---- P34 T5: caption STAGE mode declared per page; M08 enforced -----------------------------

def _stage_pages(tl, mode="stage", every=1.5):
    """caption_pages as the build emits them: cap_mode at each page's first word."""
    pages, t = [], 0.0
    while t < tl["runtime_s"]:
        pages.append({"s": t, "e": t + 1.4, "t": [{"w": "x"}] * 5, "cap_mode": mode}); t += every
    return {**tl, "caption_pages": pages, "caption_modes": ["stage", "anchor"]}


def test_stage_pages_are_events_and_m08_passes():
    tl, docks, mp = _dense_build(scene_len=15.0, dock_every=60.0)      # still > 12s without captions
    g = _by_id(G.run(_stage_pages(tl), docks, mp)[0])
    assert g["M01"].level == "PASS", g["M01"]
    assert g["M08"].level == "PASS", g["M08"]


def test_declaring_build_with_anchor_pages_on_a_still_stretch_fails_m08():
    tl, docks, mp = _dense_build(scene_len=15.0, dock_every=60.0)
    g = _by_id(G.run(_stage_pages(tl, mode="anchor"), docks, mp)[0])
    assert g["M08"].level == "FAIL" and "no stage-mode caption" in g["M08"].message, g["M08"]
    assert g["M01"].level == "FAIL"

