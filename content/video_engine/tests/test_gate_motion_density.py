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


FIRST_CHART_S = 12.0   # E24 M11: the first chart enters inside 0:08-0:20
DOCK_HOLD_S = 5.0      # E25 M12: a chart dock holds <= 6s in the opening minute and never spans a scene boundary
SPOTLIGHT = {"kind": "spotlight", "at": FIRST_CHART_S + 0.2, "dur": 2.0,
             "target": {"kind": "region", "x0": 0, "y0": 0, "x1": 0.4, "y1": 0.4}}   # E24 M11: annotated within 1.5s


def _dense_build(runtime=180.0, scene_len=6.0, dock_every=18.0, stage=False):
    """The conforming synthetic build: 6s scenes, 5s docks that start on a scene start
    (every 18s from 12s, so none spans a boundary - E25 M12), the first chart at 12s
    with a spotlight at 12.2s (E24 M11), no still stretch > 6s in the opening minute (M10)."""
    scenes = []
    t = 0.0
    i = 0
    while t < runtime:
        scenes.append({"scene_id": f"s{i:02d}", "world": {"asset_id": f"world-{i}"}, "span": [t, min(t + scene_len, runtime)]})
        t += scene_len; i += 1
    docks = [{"asset": f"ev-{k}", "at": a, "end": min(a + DOCK_HOLD_S, runtime)}
             for k, a in enumerate([x * dock_every + FIRST_CHART_S for x in range(int(runtime // dock_every))])]
    next(s for s in scenes if s["span"][0] <= FIRST_CHART_S < s["span"][1])["species"] = [dict(SPOTLIGHT)]
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
    tl, docks, mp = _dense_build(scene_len=15.0, dock_every=15.0, stage=True)
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
    page when `with_page`: the page's beats (12, 12.7, 13.5, 15.9, 16.7, 17.2, 20.2) break
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
    assert all(t in ev for t in (12.0, 12.7, 13.5, 15.9, 16.4, 19.4)), ev   # roll-out, savor, field, punch, build start, build end + focus (no outline, E22 addendum 7)


def test_page_badges_are_events_after_the_build():
    tl, docks, mp = _page_window(with_page=True)
    tl["scenes"][2]["world"]["page"]["badges"] = [{"label": "A", "value": "1", "tag": "t", "accent": "teal"}] * 3
    ev = G.analyse(tl, docks, mp)["events"]
    assert all(round(12.0 + 7.4 + 0.4 + 0.9 * k, 2) in ev for k in range(3)), ev


def test_a_short_page_credits_only_the_beats_it_had_time_to_play():
    # reviewer 2026-09-03: a 1.5s ledger row bought 7.4s of motion inside the bare plate after it
    tl, docks, mp = _page_window(with_page=True)
    page = tl["scenes"][2]
    assert page["world"]["kind"] == "ledger" and page["span"] == [12.0, 31.0]
    page["span"] = [12.0, 13.5]
    tl["scenes"].insert(3, {"scene_id": "s02b", "world": {"asset_id": "world-bare"}, "span": [13.5, 31.0], "docks": []})
    ev = G.analyse(tl, docks, mp)["events"]
    assert 12.0 in ev and 12.7 in ev
    assert 13.5 in ev   # the scene boundary itself, not a page beat
    assert not any(t in ev for t in (15.9, 16.4, 19.4)), ev
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "FAIL", g["M01"]   # the 17.5s bare plate is still again


def test_species_events_stop_at_the_scene_end():
    tl, docks, mp = _bare_plate(runtime=30.0, species=[{"kind": "plate_life", "at": 28.0, "dur": 5.0, "target": {"kind": "point", "x": 0.5, "y": 0.5}}])
    ev = G.analyse(tl, docks, mp)["events"]
    z = float(tl["scenes"][-1]["span"][1])
    assert all(t <= z for t in ev), [t for t in ev if t > z]


def test_m06_and_m07_report_info_rows_instead_of_vanishing():
    tl, docks, mp = _page_window(with_page=True)
    del tl["caption_pages"]
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M06"].level == "INFO" and "not run" in g["M06"].message
    short, d2, m2 = _bare_plate(runtime=10.0)
    g2 = _by_id(G.run(short, d2, m2)[0])
    assert "M07" in g2 and g2["M07"].level in ("INFO", "PASS", "FAIL")


def test_report_carries_the_hash_of_the_timeline_it_measured(tmp_path):
    import hashlib, json
    tl, docks, mp = _page_window(with_page=True)
    (tmp_path / "x.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    (tmp_path / "evidence-dock.json").write_text(json.dumps(docks), encoding="utf-8")
    (tmp_path / "motion-plan.json").write_text(json.dumps(mp), encoding="utf-8")
    report, _ = G.write_report(tmp_path, "x.timeline.json")
    digest = hashlib.sha256((tmp_path / "x.timeline.json").read_bytes()).hexdigest()
    assert f"TIMELINE: x.timeline.json sha256:{digest}" in report.read_text(encoding="utf-8")


def test_same_window_without_the_page_fails_m01_and_m03():
    tl, docks, mp = _page_window(with_page=False)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "FAIL" and "19.0s at 0:12" in g["M01"].message, g["M01"]
    assert g["M03"].level == "FAIL" and "51s from 0:03" in g["M03"].message, g["M03"]


def test_page_beat_offsets_follow_the_template_lp_constants():
    # template `const LP = { ROLL: 0.7, SAVOR: 0.8, FIELD: 2.4, PUNCH: 0.5, INK: 2.0, BUILD: 3.0 }`
    # (doc 29 s9.26, E22 addenda 6-7): roll-out, savor start, field start, punch, build start, build end + focus;
    # the outline beat is retired (addendum 7) - the deckle is the edge
    assert G.PAGE_BEAT_OFFSETS == (0.0, 0.7, 1.5, 3.9, 4.4, 7.4)


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
    assert B.parse_ledger_id("ledger:ev-x:line") == ("ev-x", "line", None, "right", None, None)
    assert B.parse_ledger_id("ledger:ev-x:bars:3") == ("ev-x", "bars", 3, "right", None, None)
    assert B.parse_ledger_id("ledger:ev-x:bars::left") == ("ev-x", "bars", None, "left", None, None)


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



# ---- P35 T7: targeted species fire as events (s9.27 gate column); M09 one camera move per window -----

def _bare_plate(runtime=30.0, species=None, ken_scale=0.0):
    scene = {"scene_id": "s00", "world": {"asset_id": "world-bare", "ken_burns": {"scale": ken_scale, "x": 0, "y": 0}},
             "span": [0.0, runtime], "docks": [], "species": species or []}
    tl = {"runtime_s": runtime, "scenes": [scene], "caption_pages": _caption_pages(runtime), "rows": [],
          "species": sorted({sp["kind"] for sp in (species or [])})}
    return tl, [], {"cues": []}


def test_plate_life_steps_fill_a_bare_plate_and_pass_m01():
    tl, docks, mp = _bare_plate()
    assert _by_id(G.run(tl, docks, mp)[0])["M01"].level == "FAIL"          # 30s with nothing moving
    tl, docks, mp = _bare_plate(species=[{"kind": "plate_life", "at": 12.0, "dur": 18.0}])
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "PASS", g["M01"]                               # stepping at 10 fps from 12s to 30s
    ev = G.analyse(tl, docks, mp)["events"]
    assert 12.0 in ev and 12.1 in ev and 29.9 in ev and 30.0 in ev
    assert 11.9 not in ev                                                   # nothing before the species fires
    assert g["M09"].level == "PASS"


def test_species_edges_are_events_per_the_gate_column():
    species = [{"kind": "punch", "at": 3.0, "dur": 0.8, "target": {"kind": "point", "x": 0.5, "y": 0.5}},
               {"kind": "spotlight", "at": 10.0, "dur": 2.5, "target": {"kind": "region", "x0": 0, "y0": 0, "x1": 0.4, "y1": 0.4}},
               {"kind": "squiggle", "at": 20.0, "dur": 1.0, "target": {"kind": "span", "from_word": 1, "to_word": 2}}]
    tl, docks, mp = _bare_plate(species=species)
    ev = G.analyse(tl, docks, mp)["events"]
    assert 3.0 in ev and 3.8 not in ev                                      # punch: one event at the punch
    assert 10.0 in ev and 12.5 in ev                                        # spotlight: departure and arrival of the glide
    assert 20.0 not in ev and 21.0 not in ev                                # squiggle: a caption event in stage mode only - none of its own
    assert G.SPECIES_EVENTS["focus_zoom"] == ("at", "end") and G.SPECIES_EVENTS["plate_life"] == "stepping"


def test_two_camera_moves_on_one_scene_fail_m09():
    species = [{"kind": "punch", "at": 3.0, "dur": 0.8, "target": {"kind": "point", "x": 0.5, "y": 0.5}},
               {"kind": "pull_back", "at": 12.0, "dur": 2.0, "target": {"kind": "datum", "index": 4}}]
    tl, docks, mp = _bare_plate(species=species)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M09"].level == "FAIL" and "s00 (punch + pull_back)" in g["M09"].message, g["M09"]


def test_camera_move_over_ken_burns_fails_m09_on_a_hand_edited_timeline():
    species = [{"kind": "focus_zoom", "at": 3.0, "dur": 2.0, "target": {"kind": "datum", "index": 4}}]
    tl, docks, mp = _bare_plate(species=species, ken_scale=0.04)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M09"].level == "FAIL" and "s00 (focus_zoom over Ken Burns scale 0.04)" in g["M09"].message, g["M09"]
    tl, docks, mp = _bare_plate(species=species, ken_scale=0.0)
    assert _by_id(G.run(tl, docks, mp)[0])["M09"].level == "PASS"


def test_m09_passes_on_a_build_without_species():
    tl, docks, mp = _dense_build()
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M09"].level == "PASS" and "no scene stacks two camera moves" in g["M09"].message


# ---- E24 / E25: the opening minute (M10, M11) and the chart as proof, not homework (M12) -----

@needs_ep1
def test_red_steel_and_paper_opening_minute_and_chart_holds():
    tl, docks, mp = G._load(BUILD, "steel-and-paper.timeline.json")
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M10"].level == "FAIL" and "0:57+14s" in g["M10"].message, g["M10"]          # 14s still at 0:57
    assert g["M11"].level == "FAIL" and "unannotated" in g["M11"].message, g["M11"]      # 9.5s full chart, no species
    assert "no sound cue" in g["M11"].message and "9.5s" in g["M11"].message, g["M11"]
    assert g["M12"].level == "FAIL", g["M12"]
    for offender in ("ev-bravos-original-v1 0:09-0:50 crosses 2 scene boundaries",
                     "ev-divergence-v1 0:50-1:10 crosses 1 scene boundaries",
                     "ev-capital-formation-v1 2:02-2:52 crosses 2 scene boundaries"):
        assert offender in g["M12"].message, (offender, g["M12"].message)
    assert "E24" in g["M10"].src and "E24" in g["M11"].src and "E25" in g["M12"].src


def test_green_first_chart_at_12s_spotlit_with_short_docks_inside_one_scene():
    tl, docks, mp = _dense_build()
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M10"].level == "PASS", g["M10"]
    assert g["M11"].level == "PASS" and "enters at 12.0s with spotlight at 12.2s" in g["M11"].message, g["M11"]
    assert "every dock treated as a chart candidate" in g["M11"].message      # the synthetic build has no evidence map
    assert g["M12"].level == "PASS", g["M12"]


def test_opening_still_over_6s_fails_m10_even_under_the_12s_ceiling():
    tl, docks, mp = _dense_build(scene_len=10.0, dock_every=30.0)            # 10s scenes: fine for M01, not for M10
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "PASS", g["M01"]
    assert g["M10"].level == "FAIL" and "0:00+10s" in g["M10"].message, g["M10"]


def test_first_chart_unannotated_or_outside_the_window_fails_m11_and_no_cue_warns():
    tl, docks, mp = _dense_build()
    tl["scenes"][2]["species"] = []                                          # the spotlight gone
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "unannotated" in g["M11"].message, g["M11"]
    tl, docks, mp = _dense_build()
    late = [{**docks[0], "at": 24.0, "end": 29.0}] + docks[1:]              # first chart after 0:20
    g = _by_id(G.run(tl, late, mp)[0])
    assert g["M11"].level == "FAIL" and "enters at 24.0s - outside 8-20s" in g["M11"].message, g["M11"]
    tl, docks, mp = _dense_build()
    g = _by_id(G.run(tl, docks, {"cues": []})[0])                           # no cues, no `sound` on the timeline
    assert g["M11"].level == "WARN" and "no sound structure to check" in g["M11"].message, g["M11"]


def test_chart_dock_across_a_boundary_or_held_as_homework_fails_m12_but_a_re_enter_passes():
    tl, docks, mp = _dense_build()
    straddle = [{**docks[0], "at": 12.0, "end": 20.0}] + docks[1:]         # 8s hold crossing the 18s scene start
    g = _by_id(G.run(tl, straddle, mp)[0])
    assert g["M12"].level == "FAIL", g["M12"]
    assert "ev-0 0:12-0:20 crosses 1 scene boundaries (world-2 -> world-3), hold 8.0s > 6s (opening minute)" in g["M12"].message, g["M12"]
    tl, _, mp = _dense_build(scene_len=30.0, dock_every=30.0)
    g = _by_id(G.run(tl, [{"asset": "ev-x", "at": 90.0, "end": 101.0}], mp)[0])
    assert g["M12"].level == "FAIL" and "ev-x 1:30-1:41 hold 11.0s > 10s" in g["M12"].message, g["M12"]
    reenter = [{"asset": "ev-x", "at": 12.0, "end": 17.0}, {"asset": "ev-x", "at": 30.0, "end": 35.0}]
    assert _by_id(G.run(tl, reenter, mp)[0])["M12"].level == "PASS"          # re-entering the same chart is the pattern
    assert (G.OPENING_STILL_MAX_S, G.PARADOX_S, G.FIRST_CHART_MAX_S) == (6.0, 8.0, 20.0)
    assert (G.CHART_HOLD_MAX_S, G.OPENING_CHART_HOLD_MAX_S) == (10.0, 6.0)


# ---- P41 (2026-09-05): the short-mode reads - a page's annotation clock is its landing; a short has no minutes to rank ----

def _page_scene(sid, a, z, species=None, badges=None):
    return {"scene_id": sid, "span": [a, z], "species": species or [],
            "world": {"kind": "ledger", "page": {"schema_version": "ledger_page.v1", "builder": "story", "badges": badges or []}}}


def _short_build(page_at=17.0, spot_at=None, runtime=82.0):
    """A short's shape: clip worlds, one ledger page as the first proof, a spotlight declared on it."""
    scenes = [{"scene_id": "s01", "world": {"kind": "clip"}, "span": [0.0, 5.0]},
              {"scene_id": "s02", "world": {"kind": "clip"}, "span": [5.0, 9.0]},
              {"scene_id": "s03", "world": {"kind": "clip"}, "span": [9.0, page_at]},
              _page_scene("s04", page_at, page_at + 16.0, species=[{"kind": "spotlight", "at": spot_at if spot_at is not None else page_at + 8.4, "dur": 2.0, "target": {"kind": "datum", "index": 12}}]),
              {"scene_id": "s05", "world": {"kind": "clip"}, "span": [page_at + 16.0, runtime]}]
    pages, tt = [], 0.0
    while tt < runtime:
        pages.append({"s": tt, "e": tt + 1.5, "t": [{"w": "x"}] * 5, "cap_mode": "stage"}); tt += 1.5
    tl = {"runtime_s": runtime, "scenes": scenes, "caption_pages": pages, "rows": []}
    mp = {"cues": [{"kind": "evidence", "in": page_at + 0.5, "out": page_at + 1.0}]}   # the page-roll foley at the entry (M11 sound cue)
    return tl, [], mp


def test_page_build_end_is_the_template_landing():
    assert G.PAGE_BUILD_END_S == 7.4 == G.PAGE_BEAT_OFFSETS[-1]


def test_m11_on_a_page_clocks_the_annotation_from_the_build_landing():
    tl, docks, mp = _short_build(page_at=17.0, spot_at=17.0 + 8.4)       # 1.0s after the build lands at 24.4
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level in ("PASS", "WARN"), g["M11"]
    assert "build lands at 24.4s" in g["M11"].message and "spotlight at 25.4s" in g["M11"].message, g["M11"]


def test_m11_on_a_page_refuses_a_highlight_over_the_build():
    tl, docks, mp = _short_build(page_at=17.0, spot_at=17.2)             # with the roll-out: over the charcoal build
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "AFTER the page's build lands at 24.4s" in g["M11"].message, g["M11"]
    tl, docks, mp = _short_build(page_at=17.0, spot_at=17.0 + 7.4 + 1.6)  # too late as well
    assert _by_id(G.run(tl, docks, mp)[0])["M11"].level == "FAIL"


def test_m11_page_window_is_still_the_page_entry():
    tl, docks, mp = _short_build(page_at=22.0, spot_at=22.0 + 8.0)       # the page itself enters after 0:20
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "outside 8-20s" in g["M11"].message, g["M11"]


def test_m07_on_a_short_is_an_info_row_with_both_rates():
    tl, docks, mp = _short_build()
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M07"].level == "INFO", g["M07"]
    assert "short: 1 full minute(s) in 82s" in g["M07"].message and "tail from 1:00" in g["M07"].message and "whole runtime" in g["M07"].message, g["M07"]


def test_a_spiral_entry_credits_one_beat_and_every_page_credits_its_retract():
    tl, docks, mp = _short_build(page_at=17.0)
    tl["scenes"][3]["world"]["page"]["enter"] = "spiral"
    ev = G.analyse(tl, docks, mp)["events"]
    assert 17.0 in ev and 18.6 in ev and 17.7 not in ev, ev           # the unwind, not the roll-out
    assert 31.0 in ev and 32.0 in ev, ev                              # the retract on a page ending at 33.0
    ev2 = G.analyse(_short_build(page_at=17.0)[0], docks, mp)["events"]
    assert 17.7 in ev2 and 31.0 in ev2, ev2                           # a full entry keeps its beats and still retracts
    tl3 = _short_build(page_at=17.0)[0]; tl3["scenes"][3]["world"]["page"]["exit"] = "cut"
    assert 31.0 not in G.analyse(tl3, docks, mp)["events"]            # exit=cut: no retract beats


def test_m15_refuses_a_species_over_the_retract_unless_the_page_exits_on_the_cut():
    tl, docks, mp = _short_build(page_at=17.0)
    assert _by_id(G.run(tl, docks, mp)[0])["M15"].level == "PASS"
    tl["scenes"][3]["species"].append({"kind": "punch", "at": 32.5, "dur": 0.9, "target": {"kind": "datum", "index": 3}})
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M15"].level == "FAIL" and "punch 32.5-33.4s over the retract from 31.0s" in g["M15"].message, g["M15"]
    tl["scenes"][3]["world"]["page"]["exit"] = "cut"
    assert _by_id(G.run(tl, docks, mp)[0])["M15"].level == "PASS"


def test_ledger_id_enter_token_is_validated():
    import build_scene_timeline_f as B
    assert B.parse_ledger_id("ledger:x:line:12:right:spiral")[4] == "spiral"
    assert B.parse_ledger_id("ledger:x:line")[4] is None
    assert B.parse_ledger_id("ledger:x:bars:3:right::cut")[4:] == (None, "cut")
    with pytest.raises(ValueError):
        B.parse_ledger_id("ledger:x:bars:3:right::fade")
    with pytest.raises(ValueError):
        B.parse_ledger_id("ledger:x:line:12:right:wobble")


def test_m07_still_ranks_a_long_form_build():
    tl, docks, mp = _dense_build(runtime=180.0)
    assert _by_id(G.run(tl, docks, mp)[0])["M07"].level in ("PASS", "FAIL")


def test_m16_the_gate_is_the_pulse_on_a_short():
    tl, docks, mp = _short_build(page_at=17.0)
    tl["aspect"] = "9:16"
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M16"].level in ("PASS", "FAIL"), g["M16"]           # a short is judged
    # a 4 s hole with no events: the pulse FAILs, and the message asks for MORE motion, never less
    tl["caption_pages"] = [p for p in tl["caption_pages"] if not (60.0 <= p["s"] < 64.5)]
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M16"].level == "FAIL" and "add motion" in g["M16"].message, g["M16"]


def test_m16_is_info_on_long_form():
    tl, docks, mp = _dense_build(runtime=240.0)
    assert _by_id(G.run(tl, docks, mp)[0])["M16"].level == "INFO"
