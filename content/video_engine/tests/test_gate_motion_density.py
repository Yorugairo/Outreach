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


def test_a_press_stack_step_is_already_an_event_and_the_underline_counts_at_its_word():
    """P50 T3: a stack step needs NOTHING added to the gate. Each press card in a pile is its own dock, and a
    dock's enter and exit have been events since P35 (_dock_clock -> _collect_events); the underline is a
    `callout`, which SPECIES_EVENTS already counts at `at`. This test is the confirmation, in the gate's own
    terms - if either ever stops being true, a stack of three claims would read as one event and M16 would
    credit a still frame."""
    docks = [{"slide": f"ev-press-{i}", "slot": 0, "enter": e, "exit": 26.0, "badge_at": [],
              "kind": "press", "source": "The Herald", "phrase": {"x0": 0.1, "y0": 0.2, "x1": 0.6, "y1": 0.4},
              "stack_index": i, "stack_n": 3} for i, e in enumerate((5.0, 7.4, 9.8))]
    species = [{"kind": "callout", "form": "underline", "at": 10.6, "dur": 2.0,
                "target": {"kind": "phrase", "dock": "ev-press-2"}}]
    tl, d0, mp = _bare_plate(runtime=30.0, species=species)
    tl["scenes"][0]["docks"] = docks
    ev = G.analyse(tl, d0, mp)["events"]
    for step in (5.0, 7.4, 9.8):
        assert step in ev, f"the stack step at {step}s is not an event: {sorted(ev)}"
    assert 10.6 in ev, "the underline counts at its word"
    assert 26.0 in ev, "the pile leaving is an event too"
    # and a press card is NOT a video dock: it is a still card, and it credits no continuous motion
    assert G._video_dock_events(tl["scenes"], d0) == []


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
    # runtime 240s = long form: M11 keeps E24's 8-20s window there (E44's 0-10s is under 3:00)
    tl, docks, mp = _short_build(page_at=17.0, spot_at=17.0 + 8.4, runtime=240.0)   # 1.0s after the build lands at 24.4
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level in ("PASS", "WARN"), g["M11"]
    assert "build lands at 24.4s" in g["M11"].message and "spotlight at 25.4s" in g["M11"].message, g["M11"]


def test_m11_on_a_page_refuses_a_highlight_over_the_build():
    tl, docks, mp = _short_build(page_at=17.0, spot_at=17.2, runtime=240.0)   # with the roll-out: over the charcoal build
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "AFTER the page's build lands at 24.4s" in g["M11"].message, g["M11"]
    tl, docks, mp = _short_build(page_at=17.0, spot_at=17.0 + 7.4 + 1.6, runtime=240.0)  # too late as well
    assert _by_id(G.run(tl, docks, mp)[0])["M11"].level == "FAIL"


def test_m11_page_window_is_still_the_page_entry():
    tl, docks, mp = _short_build(page_at=22.0, spot_at=22.0 + 8.0, runtime=240.0)   # the page itself enters after 0:20
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "outside 8-20s" in g["M11"].message, g["M11"]
    assert "E24 long form" in g["M11"].message, g["M11"]


# ---- E44 (2026-09-06): on a SHORT the first ledger page rolls out ON THE HOOK - window 0:00-0:10 ----

def _short_e44_build(page_at=3.3, spot_at=None, runtime=88.0):
    """A short whose first proof is a ledger page rolling out on the hook line (E44): the lead
    is only the hook, the page holds, a clip closes it out. Mirrors _short_build's page shape."""
    land = page_at + G.PAGE_BUILD_END_S
    scenes = [{"scene_id": "s01", "world": {"kind": "clip"}, "span": [0.0, page_at]},
              _page_scene("s02", page_at, page_at + 20.0,
                          species=[{"kind": "spotlight", "at": spot_at if spot_at is not None else land + 1.0,
                                    "dur": 2.0, "target": {"kind": "datum", "index": 12}}]),
              {"scene_id": "s03", "world": {"kind": "clip"}, "span": [page_at + 20.0, runtime]}]
    pages, tt = [], 0.0
    while tt < runtime:
        pages.append({"s": tt, "e": tt + 1.5, "t": [{"w": "x"}] * 5, "cap_mode": "stage"}); tt += 1.5
    tl = {"runtime_s": runtime, "aspect": "9:16", "scenes": scenes, "caption_pages": pages, "rows": []}
    mp = {"cues": [{"kind": "evidence", "in": page_at + 0.5, "out": page_at + 1.0}]}   # the page-roll foley
    return tl, [], mp


def test_m11_on_a_short_takes_the_e44_window_and_passes_a_page_on_the_hook():
    tl, docks, mp = _short_e44_build(page_at=3.3)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "PASS", g["M11"]
    assert "enters at 3.3s" in g["M11"].message, g["M11"]
    assert "window 0-10s (E44 short" in g["M11"].message, g["M11"]


def test_m11_on_a_short_fails_a_first_chart_that_waits_past_0_10():
    tl, docks, mp = _short_e44_build(page_at=12.0)
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "enters at 12.0s - outside 0-10s" in g["M11"].message, g["M11"]
    assert "E44 short" in g["M11"].message, g["M11"]


def test_m11_on_a_short_still_wants_the_annotation_after_the_build_and_a_sound_cue():
    tl, docks, mp = _short_e44_build(page_at=3.3, spot_at=3.5)               # over the charcoal build
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "FAIL" and "AFTER the page's build lands at 10.7s" in g["M11"].message, g["M11"]
    tl, docks, _ = _short_e44_build(page_at=3.3)
    g = _by_id(G.run(tl, docks, {"cues": []})[0])                            # no cue structure at all
    assert g["M11"].level == "WARN" and "no sound structure to check" in g["M11"].message, g["M11"]


def test_m11_long_form_keeps_the_e24_window_and_the_short_window_is_declared():
    tl, docks, mp = _dense_build()                                           # runtime 180s: long form
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M11"].level == "PASS" and "window 8-20s (E24 long form" in g["M11"].message, g["M11"]
    early = [{**docks[0], "at": 3.3, "end": 8.3}] + docks[1:]                # E44's short window, on long form
    g = _by_id(G.run(tl, early, mp)[0])
    assert g["M11"].level == "FAIL" and "enters at 3.3s - outside 8-20s" in g["M11"].message, g["M11"]
    assert G.FIRST_CHART_SHORT == (0.0, 10.0)                                # E44


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


def test_m16_credits_a_declared_life_over_a_caption_hole():
    """The Remotion outro: a clip world that animates on its own carries a `life` species (a declared claim, verified by eye);
    the gate credits it as continuous, so the tail of a short with no captions is not a hole."""
    tl, docks, mp = _short_build(page_at=17.0)
    tl["aspect"] = "9:16"
    tl["caption_pages"] = [p for p in tl["caption_pages"] if not (60.0 <= p["s"] < 66.0)]
    assert _by_id(G.run(tl, docks, mp)[0])["M16"].level == "FAIL"
    tl["scenes"][-1]["species"] = [{"kind": "life", "at": 60.0, "dur": 6.0}]
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M16"].level == "PASS", g["M16"]


def test_m16_credits_each_word_pop_on_a_stage_page():
    """Sentence-sized pages (2026-09-05): a stage page's words pop on their own spoken times, so a 3 s page whose words land
    every 0.5 s is not a 3 s hole."""
    tl, docks, mp = _short_build(page_at=17.0)
    tl["aspect"] = "9:16"
    tl["caption_pages"] = [p for p in tl["caption_pages"] if not (60.0 <= p["s"] < 66.0)]
    assert _by_id(G.run(tl, docks, mp)[0])["M16"].level == "FAIL"
    tl["caption_pages"].append({"s": 60.0, "e": 66.0, "cap_mode": "stage", "t": [{"w": "x", "s": 60.0 + 0.5 * i, "e": 60.4 + 0.5 * i} for i in range(12)]})
    assert _by_id(G.run(tl, docks, mp)[0])["M16"].level == "PASS"


def test_m16_is_info_on_long_form():
    tl, docks, mp = _dense_build(runtime=240.0)
    assert _by_id(G.run(tl, docks, mp)[0])["M16"].level == "INFO"


# ---- E44 / R26-7: a VIDEO dock is moving pictures, an IMAGE dock is a still card ------------


def _one_dock_build(kind: str | None = None, runtime: float = 30.0, enter: float = 2.0):
    """One 30s scene under one dock that holds from `enter` to the end. As an IMAGE card that is a
    28s hold with nothing moving; as a VIDEO card (E44) the frame moves the whole time."""
    d = {"slide": "clip-a", "slot": 0, "enter": enter, "exit": runtime, "badge_at": []}
    if kind:
        d["kind"] = kind
    scenes = [{"scene_id": "s01", "world": {"asset_id": "plate"}, "span": [0.0, runtime], "docks": [d]}]
    return {"runtime_s": runtime, "scenes": scenes, "caption_pages": [], "rows": []}, [], {"cues": []}


def test_a_video_dock_counts_as_continuous_motion_and_an_image_dock_does_not():
    still_tl, docks, mp = _one_dock_build()                       # today's behaviour: a still card
    g = _by_id(G.run(still_tl, docks, mp)[0])
    assert g["M01"].level == "FAIL", g["M01"]
    assert g["M10"].level == "FAIL" and "0:02+28s" in g["M10"].message, g["M10"]
    assert g["M16"].level == "FAIL" and "0:02+28.0s" in g["M16"].message, g["M16"]

    video_tl, docks, mp = _one_dock_build(kind="video")           # E44: the card carries a clip
    A = G.analyse(video_tl, docks, mp)
    assert A["still"][0][1] <= 2.0, A["still"][:3]                # only the bare 0-2s before the card lands
    g = _by_id(G.run(video_tl, docks, mp)[0])
    assert g["M01"].level == "PASS", g["M01"]
    assert g["M10"].level == "PASS", g["M10"]
    assert g["M16"].level == "PASS", g["M16"]


def test_a_video_dock_credits_one_event_a_second_it_is_on_screen():
    tl, docks, mp = _one_dock_build(kind="video")
    ev = G.analyse(tl, docks, mp)["events"]
    assert G.VIDEO_DOCK_STEP_S == G.LIFE_CONTINUOUS_S             # credited exactly like a continuous species
    for t in (2.0, 3.0, 12.0, 29.0):
        assert t in ev, (t, ev[:12])
    assert G._video_dock_events(tl["scenes"], []) == [round(2.0 + k, 2) for k in range(29)]


def test_the_video_credit_stops_with_the_dock_and_never_runs_past_it():
    tl, docks, mp = _one_dock_build(kind="video", runtime=30.0)
    tl["scenes"][0]["docks"][0]["exit"] = 10.0
    ev = G.analyse(tl, docks, mp)["events"]
    assert max(t for t in ev if t < 30.0) == 10.0, ev             # 10s dock, 30s scene: no credit after the card leaves
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M01"].level == "FAIL" and "0:10" in g["M01"].message, g["M01"]


def test_the_evidence_dock_file_is_the_video_fallback_when_the_timeline_carries_no_docks():
    tl, _, mp = _one_dock_build(kind="video")
    tl["scenes"][0].pop("docks")
    file_docks = [{"asset": "clip-a", "at": 2.0, "end": 30.0, "kind": "video"}]
    assert G._video_dock_events(tl["scenes"], file_docks)[:3] == [2.0, 3.0, 4.0]
    assert _by_id(G.run(tl, file_docks, mp)[0])["M10"].level == "PASS"


# ---- R26-50 (2026-09-11): the mount is the soak on the page's own clock - a MOUNTED page lands its chart mount_s + 3.5 s after enter (E45 s2's roll-out was mount_s + 6.7) ----
def test_a_mounted_pages_landing_skips_only_the_roll():
    import gate_motion_density as G
    rolled = {"world": {"kind": "ledger", "page": {"enter": "roll"}}}
    mounted = {"world": {"kind": "ledger", "page": {"enter": "mount", "mount_s": 1.51}}}
    defaulted = {"world": {"kind": "ledger", "page": {"enter": "mount"}}}
    assert G._page_land_offset(rolled) == G.PAGE_BUILD_END_S
    assert abs(G._page_land_offset(mounted) - (1.51 + G.PAGE_BUILD_END_S - G.LP_ROLL_S - G.LP_SAVOR_S - G.LP_FIELD_S)) < 1e-9
    assert abs(G._page_land_offset(defaulted) - (G.LP_FIELD_S + G.PAGE_BUILD_END_S - G.LP_ROLL_S - G.LP_SAVOR_S - G.LP_FIELD_S)) < 1e-9


# ---- E47 #4: a dip / blur-zoom is the boundary EVENT, never stillness (operator 2026-09-06) ----
def _tail_build(exit_id: str, first_scene_s: float, runtime: float = 60.0) -> tuple[dict, list, dict]:
    """One long opening scene whose tail is still, then 5s scenes to the end. The first boundary
    carries `exit_id`; nothing else in the build moves, so M10's verdict is that boundary's alone."""
    edges, t = [0.0, first_scene_s], first_scene_s
    while t + 5.0 < runtime:
        t = round(t + 5.0, 2); edges.append(t)
    edges.append(runtime)
    scenes = [{"scene_id": f"s{i:02d}", "world": {"asset_id": f"world-{i}"}, "span": [a, z], "exit": "cut"}
              for i, (a, z) in enumerate(zip(edges, edges[1:]))]
    scenes[1]["exit"] = exit_id
    return {"runtime_s": runtime, "scenes": scenes, "caption_pages": []}, [], {}


def test_a_dip_splits_the_still_tail_it_ends_so_m10_passes():
    """A 6.2s still tail FAILs M10 on a cut and PASSes on a dip: the dip's 14 frames are the event."""
    on_cut = _by_id(G.run(*_tail_build("cut", 6.2))[0])
    assert on_cut["M10"].level == "FAIL", on_cut["M10"]
    on_dip = _by_id(G.run(*_tail_build("dip", 6.2))[0])
    assert on_dip["M10"].level == "PASS", on_dip["M10"]
    tl = _tail_build("dip", 6.2)[0]
    assert G._transition_events(tl["scenes"]) == [round(6.2 - G.DIP_S / 2, 3), 6.2, round(6.2 + G.DIP_S / 2, 3)]


def test_a_blurzoom_splits_the_still_tail_it_ends_so_m10_passes():
    on_cut = _by_id(G.run(*_tail_build("cut", 6.1))[0])
    assert on_cut["M10"].level == "FAIL", on_cut["M10"]
    on_bz = _by_id(G.run(*_tail_build("blurzoom", 6.1))[0])
    assert on_bz["M10"].level == "PASS", on_bz["M10"]
    tl = _tail_build("blurzoom", 6.1)[0]
    assert G._transition_events(tl["scenes"]) == [round(6.1 - G.BLURZOOM_S / 2, 3), 6.1, round(6.1 + G.BLURZOOM_S / 2, 3)]


def test_a_timed_exit_credits_the_length_it_declares_and_the_first_scene_credits_nothing():
    tl = _tail_build("dip:1.0", 6.2)[0]
    tl["scenes"][1]["exit_s"] = 1.0
    assert G._transition_events(tl["scenes"]) == [5.7, 6.2, 6.7]
    tl["scenes"][0]["exit"] = "dip"          # no boundary before the first scene
    assert G._transition_events(tl["scenes"])[0] == 5.7


def test_a_wipe_or_a_cut_credits_no_transition_window():
    for name in ("cut", "wipe_right", "dissolve", "suck:0.5,0.5"):
        assert G._transition_events(_tail_build(name, 6.2)[0]["scenes"]) == [], name


# ---- P48 T6 (2026-09-10): M23 - a chart changes state, never over a build, never at the edge; a transition is a landing and a data mark ----

def _xf(to, at, dur=1.2, **kw):
    return {"kind": "chart_to", "to": to, "at": at, "dur": dur, **({"state": 1} if to in ("recast", "morph") else {}), **kw}


def _page_with_states(sid, a, z, species, n_states=2):
    s = _page_scene(sid, a, z, species=species)
    s["world"]["page_states"] = [{"schema_version": "ledger_page.v1", "builder": "story"}] * (n_states - 1)
    return s


def _run_page(scene, runtime=60.0):
    scenes = [{"scene_id": "s01", "world": {"kind": "clip"}, "span": [0.0, scene["span"][0]]}, scene,
              {"scene_id": "s99", "world": {"kind": "clip"}, "span": [scene["span"][1], runtime]}]
    pages, tt = [], 0.0
    while tt < runtime:
        pages.append({"s": tt, "e": tt + 1.5, "t": [{"w": "x"}] * 5, "cap_mode": "stage"}); tt += 1.5
    return _by_id(G.run({"runtime_s": runtime, "scenes": scenes, "caption_pages": pages, "rows": []}, [], {"cues": []})[0])


def test_m23_lists_every_transition_and_passes_when_each_is_on_a_built_chart_clear_of_the_edge():
    land = 10.0 + G.PAGE_BUILD_END_S
    g = _run_page(_page_with_states("s02", 10.0, 40.0, [_xf("rescale", land + 2.0, window=[1, 2]), _xf("extend", land + 8.0, to_index=9)]))
    assert g["M23"].level == "PASS" and "2 transition(s)" in g["M23"].message and "s02 rescale" in g["M23"].message and "extend" in g["M23"].message, g["M23"]


def test_m23_warns_on_a_transition_inside_the_build_beat_or_at_the_page_s_edge():
    land = 10.0 + G.PAGE_BUILD_END_S
    early = _run_page(_page_with_states("s02", 10.0, 40.0, [_xf("rescale", land - 2.0, window=[1, 2])]))
    assert early["M23"].level == "WARN" and "inside the page's build beat" in early["M23"].message, early["M23"]
    late = _run_page(_page_with_states("s02", 10.0, 40.0, [_xf("rescale", 39.0, dur=0.8, window=[1, 2])]))
    assert late["M23"].level == "WARN" and "last 0.5 s" in late["M23"].message, late["M23"]


def test_m23_fails_a_page_built_with_two_states_and_no_transition_between_them():
    g = _run_page(_page_with_states("s02", 10.0, 40.0, [_xf("park", 20.0)]))
    assert g["M23"].level == "FAIL" and "2 chart states and no transition" in g["M23"].message, g["M23"]
    assert "M23" not in _run_page(_page_scene("s02", 10.0, 40.0)), "a page with one chart and no chart_to has no M23 row"


def test_m23_counts_a_morph_to_and_m17_is_measured_per_morph():
    """P48 T5: a morph_to is a data transition (M23 lists it, its end is a landing and a data mark), and M17 reads the
    invariants PER MORPH - the page-enter morph keyed by its scene, every morph_to keyed scene@at."""
    land = 10.0 + G.PAGE_BUILD_END_S
    g = _run_page(_page_with_states("s02", 10.0, 40.0, [_xf("morph", land + 3.0, dur=2.0)]))
    assert g["M23"].level == "PASS" and "s02 morph" in g["M23"].message, g["M23"]
    lives = G._deployed_lives([_page_with_states("s02", 10.0, 40.0, [_xf("morph", land + 3.0, dur=2.0)])])
    assert lives and lives[0][1] == round(land + 5.0, 2), "E50's clock restarts at the morph's end"
    sc = _page_with_states("s02", 10.0, 40.0, [_xf("morph", land + 3.0, dur=2.0)])
    sc["world"]["page"]["enter"] = "morph"
    keys = [k for k, _l in G._morphs([sc])]
    assert keys == ["s02", f"s02@{land + 3.0:.2f}"], keys
    assert G._morph_events(sc)[0]["from"] == 0 and G._morph_events(sc)[0]["to"] == 1
    good = {"centroid_ok": True, "axis_ok": True, "area_ok": True, "centroid_shift": 0.01, "axis_deg": 2.0, "area_ratio": 0.9, "min_det": 0.4}
    assert G._morph_gate([sc], None).level == "INFO" and "2 morph(s)" in G._morph_gate([sc], None).message
    assert G._morph_gate([sc], {"scenes": {"s02": good, f"s02@{land + 3.0:.2f}": good}}).level == "PASS"
    w = G._morph_gate([sc], {"scenes": {"s02": good}})
    assert w.level == "WARN" and "morph_to at" in w.message and "not in the measurement" in w.message, w


def test_a_transition_s_end_is_a_landing_for_the_push_tie_and_a_data_mark_for_the_deployed_clock():
    land = 10.0 + G.PAGE_BUILD_END_S
    xf = _xf("extend", land + 4.0, dur=2.0, to_index=9)
    tied = _run_page(_page_with_states("s02", 10.0, 40.0, [xf, {"kind": "punch", "at": land + 6.2, "dur": 1.0, "target": {"kind": "datum", "index": 3}}]))
    assert tied["M22"].level == "PASS", tied["M22"]
    lives = G._deployed_lives([_page_with_states("s02", 10.0, 40.0, [xf])])
    assert lives and lives[0][1] == round(land + 6.0, 2), "E50's clock restarts at the transition's end"
    parked = G._deployed_lives([_page_scene("s02", 10.0, 40.0, species=[_xf("park", land + 4.0, dur=1.0)])])
    assert parked[0][1] == round(land, 2), "a park moves the chart and changes no data: the clock does not restart"
    assert not any("park" in n for _t, n in G._landings(_page_scene("s02", 10.0, 40.0, species=[_xf("park", land + 4.0)])))


# ---- P49 T6: the gate reads the camera track - M09/M14 count key segments, M24 in-frame ---------------------------

def _keyed(scene, keys):
    scene["camera"] = {"keys": keys, "attention": "locked"}
    return scene


def test_m09_counts_an_authored_key_segment_as_a_camera_move():
    tl, docks, mp = _bare_plate(species=[{"kind": "punch", "at": 10.0, "dur": 1.2, "target": {"kind": "point", "x": 0.5, "y": 0.5}}])
    _keyed(tl["scenes"][0], [{"t": 2.0, "zoom": 1.0}, {"t": 4.0, "zoom": 1.3, "look": [0.6, 0.4]}])
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M09"].level == "FAIL" and "camera keys + punch" in g["M09"].message, g["M09"]
    tl, docks, mp = _bare_plate(ken_scale=0.04)
    _keyed(tl["scenes"][0], [{"t": 2.0, "zoom": 1.0}, {"t": 4.0, "zoom": 1.3}])
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M09"].level == "FAIL" and "camera keys over Ken Burns" in g["M09"].message, g["M09"]
    tl, docks, mp = _bare_plate()
    _keyed(tl["scenes"][0], [{"t": 2.0, "zoom": 1.3}, {"t": 4.0, "zoom": 1.3}])   # two keys, nothing moves: not a move
    assert G._camera_key_segments(tl["scenes"][0]) == []
    assert G._camera_key_segments(_keyed({"scene_id": "x"}, [{"t": 1.0, "zoom": 1}, {"t": 3.0, "zoom": 2, "ease": "hold"}])) == [(3.0, 3.0 + G.CAMERA_MOVE_S, "camera key step at 3.0s")]


def test_m14_catches_a_key_segment_over_an_evidence_build():
    tl, docks, mp = _bare_plate()
    tl["scenes"][0]["docks"] = [{"asset": "dock-x", "slot": 0, "enter": 5.0, "exit": 12.0, "badge_at": []}]
    _keyed(tl["scenes"][0], [{"t": 4.0, "zoom": 1.0}, {"t": 7.0, "zoom": 1.4, "look": [0.5, 0.5]}])
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M14"].level == "FAIL" and "camera keys 4.0-7.0s over dock-x build" in g["M14"].message, g["M14"]


def test_m24_reads_the_track_and_names_a_target_out_of_frame():
    point_in = {"kind": "point", "x": 0.6, "y": 0.4}
    point_out = {"kind": "point", "x": 0.05, "y": 0.05}
    tl, docks, mp = _bare_plate(species=[{"kind": "callout", "at": 10.0, "dur": 1.0, "target": point_in},
                                         {"kind": "spotlight", "at": 12.0, "dur": 1.0, "target": point_out}])
    assert "M24" not in _by_id(G.run(tl, docks, mp)[0]), "no keys, no row: the identity camera frames everything"
    _keyed(tl["scenes"][0], [{"t": 6.0, "zoom": 1.0, "look": [0.6, 0.4]}, {"t": 8.0, "zoom": 2.0, "look": [0.6, 0.4]}])
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M24"].level == "FAIL" and "s00 spotlight at" in g["M24"].message and "0% in frame (zoom 2.00)" in g["M24"].message, g["M24"]
    assert "callout" not in g["M24"].message, "the callout's target sits at the look point - in frame"
    tl["scenes"][0]["species"] = [{"kind": "callout", "at": 10.0, "dur": 1.0, "target": point_in}]
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M24"].level == "PASS" and "1 pointing species" in g["M24"].message, g["M24"]
    # the state the gate evaluates is the player's: identity before the first key, the lerp, the hold
    sc = tl["scenes"][0]
    assert G.camera_state_at(sc, 5.0, 1920.0, 1080.0, None)["s"] == 1.0
    assert abs(G.camera_state_at(sc, 7.0, 1920.0, 1080.0, None)["s"] - (1 + (1 - (1 - 0.5) ** 3))) < 1e-9
    assert G.camera_state_at(sc, 30.0, 1920.0, 1080.0, None)["s"] == 2.0
    fr = G.camera_frustum(G.camera_state_at(sc, 30.0, 1920.0, 1080.0, None), 1920.0, 1080.0)
    assert abs((fr["x1"] - fr["x0"]) - 960) < 1e-9 and abs(fr["x0"] - 576) < 1e-9 and abs(fr["x1"] - 1536) < 1e-9, "a zoom in place keeps the look point where it was on screen: the frame is not centred on it"


def test_the_attention_pull_is_tied_to_its_own_dock_and_clashes_with_any_other_build():
    """P49 T4: the attention pull toward a landing overlaps that dock's build by definition (E51: the push IS the landing)
    - M14 exempts it against its own dock and names it against another's; M09 clashes it with a camera species."""
    dock = {"asset": "dock-x", "slot": 0, "enter": 5.0, "exit": 12.0, "arrive": "throw", "place": {"x": 140, "y": 600, "w": 800, "h": 450}, "badge_at": []}
    tl, docks, mp = _bare_plate()
    tl["scenes"][0]["docks"] = [dict(dock)]
    tl["scenes"][0]["camera"] = {"keys": [], "attention": "landings"}
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M14"].level == "PASS", g["M14"]
    assert G._attention_moves(tl["scenes"][0]) == [(5.45, 5.95, "dock-x")]
    tl["scenes"][0]["docks"].append({"asset": "dock-y", "slot": 1, "enter": 5.2, "exit": 12.0, "badge_at": []})   # a second build under the pull
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M14"].level == "FAIL" and "attention pull 5.5-6.0s (toward dock-x) over dock-y build" in g["M14"].message, g["M14"]
    tl, docks, mp = _bare_plate(species=[{"kind": "punch", "at": 8.0, "dur": 1.2, "target": {"kind": "point", "x": 0.5, "y": 0.5}}])
    tl["scenes"][0]["docks"] = [dict(dock)]
    tl["scenes"][0]["camera"] = {"keys": [], "attention": "landings"}
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M09"].level == "FAIL" and "attention landings + punch" in g["M09"].message, g["M09"]
    # M24 evaluates the pull: a point at the far corner leaves the 1.06 frame about the card
    tl, docks, mp = _bare_plate(species=[{"kind": "callout", "at": 8.0, "dur": 1.0, "target": {"kind": "point", "x": 0.01, "y": 0.01}}])
    tl["scenes"][0]["docks"] = [dict(dock)]
    tl["scenes"][0]["camera"] = {"keys": [], "attention": "landings"}
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M24"].level == "FAIL" and "zoom 1.06" in g["M24"].message, g["M24"]


def test_a_breakthrough_state_s_run_is_its_last_data_mark_and_its_landing():
    """E60: a recast into a chart state whose axes carry `overflow` lands when the bar's run ends - the state's own build
    (build_s), the hold at the comparator's level, the burst and its settle - not at the transition's end. M21's clock and
    E51's landings both read that instant; a state with no overflow lands at the transition's end as before."""
    bt = {"axes": {"overflow": "burst", "domain": [0, 8]}, "values": [1.52, 36.59], "build_s": 1.2}
    plain = {"values": [1, 2]}
    s = _page_scene("s04", 40.0, 60.0, species=[{"kind": "chart_to", "at": 50.0, "dur": 0.5, "to": "recast", "state": 2}])
    s["world"]["page_states"] = [plain, bt]
    assert G._breakthrough_run_s(bt) == pytest.approx(G.BT_HOLD_S + G.BT_RUN_S + G.BT_SETTLE_S)
    assert G._breakthrough_run_s(plain) == 0.0
    land = 50.5 + 1.2 + G.BT_HOLD_S + G.BT_RUN_S + G.BT_SETTLE_S
    assert G._transition_land(s, s["species"][0]) == pytest.approx(land)
    assert any(abs(t - land) < 1e-6 and "recast" in n for t, n in G._landings(s)), "the landing is the run's end"
    lives = {sid: (last, end) for sid, last, end, _d in G._deployed_lives([s])}
    assert lives["s04"][0] == pytest.approx(land, abs=0.01), "M21 counts the deployed life from the run's end"
    s["species"][0]["state"] = 1   # the plain state: the transition's end, as before
    assert G._transition_land(s, s["species"][0]) == 50.5
    stack = {"axes": {"overflow": "stack", "domain": [0, 8]}, "values": [1.52, 36.59]}
    assert G._breakthrough_run_s(stack) == pytest.approx(G.BT_HOLD_S + G.BT_STEP_S * 26), "25 bricks of 1.52 reach 36.59: the comparator's plus 25 steps"


# ---- P51 T2: M25, the layout gate - the three defects of 2026-09-10, rebuilt as fixtures ---------------------------
# Each fixture takes the COMPILED Tokyo short timeline, edits one row, instantiates it through
# render_baseline onto the reviewed template with the build's own assets, probes the instants that
# matter with probe.py and runs M25 on what the page's DOM says. The untouched timeline is the control.

import json as _json  # noqa: E402
import re as _re  # noqa: E402
import tempfile as _tempfile  # noqa: E402

import probe as PROBE  # noqa: E402
import render_baseline as RB25  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short"
TOKYO_TL = "tokyo-short.timeline.json"
# the record reads, the fab card reads, the burst, the fab card parked beside the record (E60)
M25_INSTANTS = [(56.3, "the record at reading size"), (57.92, "the fab card at reading size"),
                (58.6, "the burst"), (58.72, "the fab card parked")]


def _browser_ok25() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser25 = pytest.mark.skipif(not _browser_ok25(), reason="playwright chromium not installed")
needs_tokyo25 = pytest.mark.skipif(not (TOKYO / "player.html").exists(), reason="the Tokyo short build is not on disk")


@pytest.fixture(scope="module")
def tokyo_parts():
    """The compiled timeline and the build's own asset map, lifted out of the built player once."""
    html = (TOKYO / "player.html").read_text(encoding="utf-8")
    # P51 T1: a build's page may be the split form (the slot is empty and assets.json sits beside it)
    # or the single-file one committed before the split. Both give the same asset map TEXT.
    slot = _re.search(r'<script id="asset-data"[^>]*>(.*?)</script>', html, _re.S)
    uris = (slot.group(1).strip() if slot else "") or (TOKYO / "assets.json").read_text(encoding="utf-8")
    tpl = RB25.single_file_shell()   # the shell with the engine inlined, data slots still open
    return _json.loads((TOKYO / TOKYO_TL).read_text(encoding="utf-8")), uris, tpl


def _probe_doc(tl: dict, parts, instants=M25_INSTANTS) -> dict:
    """Build a player from this timeline and probe those instants. ONE run feeds every gate that reads
    layout-probe.json - M25 the boxes, M26 the values."""
    _base, uris, tpl = parts
    with _tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / TOKYO_TL).write_text(_json.dumps(tl), encoding="utf-8")
        # RB.instantiate's own substitution, with the asset map left as the text it already is
        (d / "player.html").write_text(tpl.replace("{{TIMELINE}}", _json.dumps(tl, separators=(",", ":"))).replace("{{URIS}}", uris), encoding="utf-8")
        with PROBE.Probe(d, TOKYO_TL) as p:
            return PROBE.probe_doc(d, probe=p, instants=instants)


def _m25(tl: dict, parts, instants=M25_INSTANTS) -> "G.Gate":
    """Build a player from this timeline, probe those instants, return the M25 row."""
    return G._layout_gate(_probe_doc(tl, parts, instants))


def _m26(tl: dict, parts, instants=M25_INSTANTS) -> "G.Gate":
    """... and the M26 row, off the same file."""
    return G._values_gate(_probe_doc(tl, parts, instants))


def _s04(tl: dict) -> dict:
    return next(s for s in tl["scenes"] if s["scene_id"] == "s04")


def test_m25_is_info_until_the_probe_has_run():
    """M18's pattern exactly: measured or named, never a silent skip."""
    assert G._layout_gate(None).level == "INFO" and "probe.py" in G._layout_gate(None).message
    assert G._layout_gate("stale").level == "INFO" and "another player.html" in G._layout_gate("stale").message
    assert G._layout_gate({"instants": []}).level == "INFO"
    assert G.load_layout(Path("no/such/build")) is None


@needs_browser25
@needs_tokyo25
def test_m25_passes_the_tokyo_short_as_built(tokyo_parts):
    """The cut the operator watched and approved (2026-09-09): two cards parked beside a chart parked to
    0.52, the citation riding it down. M25 must not have an opinion about it."""
    g = _m25(_json.loads(_json.dumps(tokyo_parts[0])), tokyo_parts)
    assert g.level == "PASS", g.message
    assert "no settled card on the chart's data" in g.message


@needs_browser25
@needs_tokyo25
def test_m25_refuses_the_card_on_the_chart_s_data_and_the_citation_left_under_it(tokyo_parts):
    """Defects (i) and (ii), 2026-09-10, from one edit: delete row 4's park and the fab card lands on the
    bars the park made room beside, with the page's source line left full-size underneath it (E52)."""
    tl = _json.loads(_json.dumps(tokyo_parts[0]))
    sc = _s04(tl)
    n = len(sc["species"])
    sc["species"] = [x for x in sc["species"]
                     if not (x.get("kind") == "chart_to" and x.get("to") == "park" and float(x["at"]) < 55.0)]
    assert len(sc["species"]) == n - 1, "row 4's park is the row this fixture deletes"
    g = _m25(tl, tokyo_parts)
    assert g.level == "FAIL", g.message
    assert "dock-i-fab-wafer over the chart's data" in g.message, g.message          # (i)
    assert "the page's source line under dock-i-fab-wafer" in g.message, g.message   # (ii)
    assert "%" in g.message and "px" in g.message, "the boxes are named with their area"


# ---- R26-40: M26, the VALUE gate - the printed number and the drawn height agree -----------------------------------
# R26-39's own numbers are the fixture: on the Tokyo side build at 57.5 s the chips bar stood 303 px on the
# rewritten 0-40 % scale while its pill read "0.00 %". The bug is fixed (commit cde3304); the GATE that would
# have named it is this one, so the fixture keeps the defect alive as arithmetic.
R26_39_BASE, R26_39_TICK = 822, [40, 525]          # the zero line and the topmost visible tick, in stage px
R26_39_DEFECT = 303                                 # the height the bar was drawn at while printing 0.00 %


def _bars_instant(t: float, rows: list[dict], base: int = R26_39_BASE, tick: list | None = None) -> dict:
    return {"t": t, "why": "fixture", "page": {"bars": {"base": base, "tick": list(tick or R26_39_TICK), "b": rows}}}


def test_m26_is_info_until_the_probe_has_run():
    """M18's and M25's pattern: measured or named, never a silent skip."""
    assert G._values_gate(None).level == "INFO" and "probe.py" in G._values_gate(None).message
    assert G._values_gate("stale").level == "INFO" and "another player.html" in G._values_gate("stale").message
    assert G._values_gate({"instants": []}).level == "INFO"
    # ... and INFO, not PASS, when the page printed nothing to check
    quiet = G._values_gate({"instants": [_bars_instant(1.0, [{"l": "Mar", "h": 100, "y": 722}])]})
    assert quiet.level == "INFO" and "printed a value" in quiet.message


def test_m26_names_the_bar_whose_height_and_printed_value_disagree():
    """R26-39 as the gate would have caught it: 303 px of bar at "0.00 %" is 40.8 on the scale the page was
    printing beside it. The honest bar in the same fixture must not be named."""
    doc = {"instants": [_bars_instant(57.5, [{"l": "Bonds", "h": 11, "y": 811, "v": "1.52%"},
                                             {"l": "Chips", "h": R26_39_DEFECT, "y": 519, "v": "0.00%"}])]}
    g = G._values_gate(doc)
    assert g.level == "FAIL", g.message
    assert "Chips prints 0.00% and draws 40.8" in g.message, g.message
    assert "0:57" in g.message and "303 px" in g.message, "the bar, the instant, the printed value and the drawn one"
    assert "Bonds" not in g.message, "the bar that agrees is not named"
    # the same page drawn honestly - the bar at its number on the rewritten scale - passes
    ok = {"instants": [_bars_instant(59.6, [{"l": "Bonds", "h": 11, "y": 811, "v": "1.52%"},
                                            {"l": "Chips", "h": 272, "y": 550, "v": "36.59%"}])]}
    assert G._values_gate(ok).level == "PASS", G._values_gate(ok).message


def test_m26_reads_a_negative_bar_by_its_geometry_and_allows_the_burst_its_overshoot():
    """E28: sign IS geometry - a bar hanging below the zero line prints a negative number, and the gate reads
    it there rather than from the string. E60: during the shoot a breaking bar is drawn up to BT_OVER past its
    own number on purpose, so the band carries that share of the printed value."""
    neg = {"instants": [_bars_instant(56.0, [{"l": "May", "h": 390, "y": 697, "v": "-$66.8"}], base=697, tick=[20, 580])]}
    assert G._values_gate(neg).level == "PASS", G._values_gate(neg).message
    flipped = {"instants": [_bars_instant(56.0, [{"l": "May", "h": 390, "y": 307, "v": "-$66.8"}], base=697, tick=[20, 580])]}
    assert G._values_gate(flipped).level == "FAIL", "a bar drawn ABOVE the line cannot print a fall"
    shot = lambda h: _bars_instant(59.3, [{"l": "Chips", "h": round(h), "y": R26_39_BASE - round(h), "v": "36.59%"}])
    over = 272 * (1 + G.VALUE_OVERSHOOT * 0.95)      # mid-overshoot, just inside the band
    assert G._values_gate({"instants": [shot(over)]}).level == "PASS", G._values_gate({"instants": [shot(over)]}).message
    far = 272 * (1 + G.VALUE_OVERSHOOT + 3 * G.VALUE_TOL)
    assert G._values_gate({"instants": [shot(far)]}).level == "FAIL", "past the overshoot the page is lying about its data"


@needs_browser25
@needs_tokyo25
def test_m26_passes_the_tokyo_short_as_built(tokyo_parts):
    """The cut the operator watched and approved, including the burst at 58.6: every number the page prints is
    drawn at that number on the scale printed beside it."""
    g = _m26(_json.loads(_json.dumps(tokyo_parts[0])), tokyo_parts)
    assert g.level == "PASS", g.message
    assert "agree with the height drawn" in g.message


@needs_browser25
@needs_tokyo25
def test_m25_refuses_paper_in_the_caption_strip(tokyo_parts):
    """Defect (iii): the record's READING box grown to the row's `read: {centre_w: 0.95, centre_y: 0.80}`
    - which the compiler writes as this read_place (build_scene_timeline_f.centred_place) - so the paper
    rests over the caption while a caption is showing."""
    tl = _json.loads(_json.dumps(tokyo_parts[0]))
    rec = next(d for d in _s04(tl)["docks"] if d["slide"] == "dock-k-pledge-record")
    card_aspect = rec["read_place"]["h"] / rec["read_place"]["w"]
    w = round(0.95 * 1080)
    h = round(w * card_aspect)
    rec["read_place"] = {"x": round((1080 - w) / 2), "y": round(0.80 * 1920 - h / 2), "w": w, "h": h}
    g = _m25(tl, tokyo_parts, [(56.0, "the record reads"), (56.3, "the record reads"), (56.6, "the record reads")])
    assert g.level == "FAIL", g.message
    assert "dock-k-pledge-record in the caption strip" in g.message, g.message


# ---- M27 (E63, 2026-09-11): the READ over a build -----------------------------------------------
def test_m27_refuses_a_card_docking_over_a_plot_drawing_or_finished():
    """The Tokyo defect at 0:09.5-0:10.5, as the probe measured it: the panel card at its solo reading
    box over the plot (277,066 px, 72 % of the smaller box) while `marks.drawn` says 0.50 - the line is
    still being drawn under it. E63 widened the same evening: the same card on the same plot with the
    chart FINISHED is the same defect, and the row says which. A PARKED card is not this row's business
    (M25 scores the parked composition). The fuller set is in tests/test_dock_over_build.py; this is the
    row's own smoke."""
    def inst(drawn, state, share, area=277066, t=10.29, data=True):
        ov = [{"a": "dock-c-blue-ties-panel", "b": "page.plot", "area_px": area, "share_of_smaller": share}]
        if data:   # E65: the plot's empty ROOM is a place the placer may choose; its INK is the fault
            ov.append({"a": "dock-c-blue-ties-panel", "b": "page.data", "area_px": area, "share_of_smaller": share})
        return {"t": t, "why": "s02 dock dock-c-blue-ties-panel reading size",
                "docks": [{"id": "dock-c-blue-ties-panel", "state": state, "box": [79, 552, 801, 474], "rest": 1}],
                "page": {"plot": [230, 464, 580, 681], "data": [246, 500, 540, 600]}, "texts": [],
                "overlaps": ov,
                "clearances": {"safe_pct": {}}, "camera": {"scene": "s02", "zoom": 1.0, "look": [540, 960]},
                "marks": {"n": 2, "drawn": drawn, "up": 1.0, "parked": False}}

    # the compiler's own clock (E63: `build_windows` on the scene) now chooses the row's WORDS, never the verdict;
    # marks.drawn is reported, never scored
    M27_SCENES = [{"scene_id": "s02", "span": [1.99, 38.96], "build_windows": [[1.99, 10.69]], "docks": []}]
    bad = G._over_build_gate({"aspect": "9:16", "instants": [inst(0.5, "reading", 72)]}, M27_SCENES)
    assert bad.level == "FAIL", bad.message
    assert "dock-c-blue-ties-panel" in bad.message and "72 %" in bad.message and "marks 50% drawn" in bad.message, bad.message
    assert "while the chart draws" in bad.message, bad.message
    done = G._over_build_gate({"aspect": "9:16", "instants": [inst(1.0, "reading", 72, t=12.0)]}, M27_SCENES)
    assert done.level == "FAIL" and "on the finished chart" in done.message, done.message
    assert G._over_build_gate({"aspect": "9:16", "instants": [inst(1.0, "reading", 72)]}, []).level == "FAIL", "no windows is not an exemption"
    assert G._over_build_gate({"aspect": "9:16", "instants": [inst(0.5, "parked", 72)]}, M27_SCENES).level == "PASS"
    room = G._over_build_gate({"aspect": "9:16", "instants": [inst(0.5, "reading", 72, data=False)]}, M27_SCENES)
    assert room.level == "WARN" and "clear of the ink" in room.message, room.message   # E65's own placement
    assert G._over_build_gate({"aspect": "9:16", "instants": [inst(0.5, "reading", 4, area=2147, data=False)]}, M27_SCENES).level == "WARN"
    assert G._over_build_gate(None, []).level == "INFO", "no probe file: said so, never silently green"


# ---- M28 (R26-53, 2026-09-11): text on text among a page's own labels ----------------------------
# The Tokyo Meta page's own boxes at 9:16 are the fixture, from both builds: the approved cut (no
# lpFitValues - values 133 px wide, the callout's pill 7 px off "$604") and the side build that carries
# the fit (values 122 px, the pill risen to its band). Neither TOUCHES; the defect the operator saw is
# the air, so the row's FAIL tier is the intersection and its WARN tier is half a figure.
META_APPROVED = [("val", "$665", [239, 567, 133, 67]), ("val", "$633", [395, 583, 133, 67]),
                 ("val", "$604", [552, 598, 133, 67]), ("pill", "$577", [692, 559, 167, 85])]
META_FITTED = [("val", "$665", [246, 575, 122, 61]), ("val", "$633", [401, 591, 122, 61]),
               ("val", "$604", [557, 606, 122, 61]), ("pill", "$577", [690, 473, 166, 84])]
# the same page with the pill shoved back over bar 3's number - R26-53 as a collision, which is what a
# REGRESSION of lpPillBand would draw: 25 px x 67 px of shared box, 19 % of the smaller label
META_CRASHED = META_APPROVED[:3] + [("pill", "$577", [660, 590, 167, 85])]
META_CRASH_PAIR = ("val:$604", "pill:$577", 1675, 19)


def _labels_instant(t: float, labels, pairs=(), vpx: int = 60) -> dict:
    return {"t": t, "why": "s05 the Meta page", "docks": [], "page": {},
            "texts": [{"k": "chart.val", "n": 3, "px": vpx, "css": round(vpx * 390 / 1080, 1)}],
            "labels": [{"role": r, "text": x, "box": list(b)} for r, x, b in labels],
            "overlaps": [{"a": a, "b": b, "area_px": ar, "share_of_smaller": sh} for a, b, ar, sh in pairs],
            "clearances": {"safe_pct": {}}, "camera": {"scene": "s05", "zoom": 1.0, "look": [540, 960]},
            "marks": {"n": 4, "drawn": 1.0, "up": 1.0, "parked": False}}


def test_m28_is_info_until_the_probe_has_run():
    """M18's, M25's and M26's pattern: measured or named, never a silent skip."""
    assert G._labels_gate(None).level == "INFO" and "probe.py" in G._labels_gate(None).message
    assert G._labels_gate("stale").level == "INFO" and "another player.html" in G._labels_gate("stale").message
    assert G._labels_gate({"instants": []}).level == "INFO"
    # ... and INFO, not PASS, when no page put two labels on screen at once - a plate has none
    quiet = G._labels_gate({"instants": [_labels_instant(1.0, META_FITTED[:1])]})
    assert quiet.level == "INFO" and "nothing to check" in quiet.message, quiet.message


def test_m28_names_the_two_labels_that_sit_on_each_other():
    """A regression of lpPillBand: the callout's pill back over bar 3's number. The row names the page's
    scene, the instant, both labels, the px and the share - and says nothing about the three that are fine."""
    g = G._labels_gate({"instants": [_labels_instant(71.0, META_CRASHED, [META_CRASH_PAIR])]})
    assert g.level == "FAIL", g.message
    assert "val:$604 on pill:$577" in g.message, g.message
    assert "1:11" in g.message and "(s05)" in g.message and "1,675 px" in g.message and "19 %" in g.message, g.message
    assert "$665" not in g.message and "$633" not in g.message, "the labels that clear each other are not named"
    # the same pair at four instants is ONE row, not four
    doc = {"instants": [_labels_instant(t, META_CRASHED, [META_CRASH_PAIR]) for t in (71.0, 71.5, 72.0, 73.0)]}
    assert G._labels_gate(doc).message.startswith("1 pair(s)"), G._labels_gate(doc).message


def test_m28_fails_the_value_row_the_eye_reads_as_one_string_and_warns_the_row_short_of_air():
    """R26-53 as the frame actually is on the approved build: the pill's box clears "$604" by 7 px - under a
    QUARTER of a figure at the page's own value size (60 px -> 8) - and the eye reads one string: the operator's
    "crashing text" is a FAIL even though no box meets. Between a quarter and half a figure (17) the row has
    lost the fit's air without crashing: a WARN."""
    g = G._labels_gate({"instants": [_labels_instant(71.0, META_APPROVED)]})
    assert g.level == "FAIL", g.message
    assert "val:$604 and pill:$577" in g.message and "7 px of air" in g.message and "quarter of a figure" in g.message, g.message
    assert "1:11" in g.message, g.message
    nudged = [(r, x, [b[0] + 6, b[1], b[2], b[3]] if r == "pill" else list(b)) for r, x, b in META_APPROVED]   # 13 px of air
    w = G._labels_gate({"instants": [_labels_instant(71.0, nudged)]})
    assert w.level == "WARN", w.message
    assert "val:$604 and pill:$577" in w.message and "13 px of air" in w.message and "17" in w.message, w.message


def test_m28_passes_the_row_the_fit_has_fitted():
    """build-short-vals' own boxes: one size for the row, a figure between neighbours, the pill in its band."""
    g = G._labels_gate({"instants": [_labels_instant(70.0, META_FITTED, vpx=55)]})
    assert g.level == "PASS", g.message
    assert "6 label pair(s) checked" in g.message, g.message
    # a tick under a negative bar's value keeps its own layer's gutter - the air law binds the VALUE row
    tight = META_FITTED + [("tick", "5.5%", [727, 998, 91, 44]), ("tick", "5%", [589, 998, 58, 44])]
    assert G._labels_gate({"instants": [_labels_instant(70.0, tight, vpx=55)]}).level == "PASS"


# ---- E44 s2a / R26-5 (M29): the cut's sound inside the drop window 0:05-0:12 ----

def _drop_window_build(cue_at=9.0, slot="press 3", gain=0.16, fade_in=0.0, page_at=3.3, runtime=88.0):
    """_short_e44_build (a page on the hook, chart landing at page_at + 7.4s) plus ONE sound cue in the
    timeline's own `sound` list - the structure build_short.py flattens the SOUND-PLAN onto."""
    tl, docks, mp = _short_e44_build(page_at=page_at, runtime=runtime)
    tl["sound"] = [{"slot": slot, "at": cue_at, "gain": gain, "fade_in": fade_in, "env": []}]
    return tl, docks, mp


def test_m29_fails_a_transient_in_the_drop_window_with_no_page_landing_on_it():
    tl, docks, mp = _drop_window_build(cue_at=9.0)        # the chart lands at 10.7s: 1.7s away, over CUE_TOL_S
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M29"].level == "FAIL", g["M29"]
    assert "press 3 at 9.00s gain 0.16" in g["M29"].message, g["M29"]
    assert "nearest page landing s02 chart lands at 10.70s" in g["M29"].message, g["M29"]
    assert "window 0:05-0:12" in g["M29"].message, g["M29"]


def test_m29_passes_the_same_transient_when_a_page_lands_with_it():
    tl, docks, mp = _drop_window_build(cue_at=10.0, gain=0.08)   # 0.7s from the chart landing at 10.7s
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M29"].level == "PASS", g["M29"]
    assert "with s02 chart lands at 10.70s" in g["M29"].message, g["M29"]


def test_m29_exempts_a_bed_and_carries_no_row_when_the_window_is_quiet():
    tl, docks, mp = _drop_window_build(cue_at=9.0, slot="hook bed", gain=0.0569, fade_in=1.5)
    assert "M29" not in _by_id(G.run(tl, docks, mp)[0])          # a bed marks no instant
    tl, docks, mp = _drop_window_build(cue_at=20.0)               # a transient outside the window
    assert "M29" not in _by_id(G.run(tl, docks, mp)[0])


# ---- E44 s2b / R26-6 (M30): a returning character mounts, it never cuts on ----

def _cast_build(back_exit="dissolve", asset_back="clip-host-desk", page_at=6.0, runtime=44.0, declare=True):
    """The host enters s01, the page holds s02, and s03 brings him BACK. `back_exit` is the transition INTO
    s03 - a scene's own `exit` names its entry (the player's law, _transition_events)."""
    land = page_at + G.PAGE_BUILD_END_S
    host = {"kind": "clip", "asset_id": "clip-host-counter"}
    back = {"kind": "clip", "asset_id": asset_back}
    if declare:
        host["character"] = back["character"] = "mike"
    scenes = [{"scene_id": "s01", "exit": "cut", "span": [0.0, page_at], "world": host},
              _page_scene("s02", page_at, page_at + 20.0,
                          species=[{"kind": "spotlight", "at": land + 1.0, "dur": 2.0,
                                    "target": {"kind": "datum", "index": 3}}]),
              {"scene_id": "s03", "exit": back_exit, "span": [page_at + 20.0, runtime], "world": back}]
    scenes[1]["exit"] = "mount"
    pages, tt = [], 0.0
    while tt < runtime:
        pages.append({"s": tt, "e": tt + 1.5, "t": [{"w": "x"}] * 5, "cap_mode": "stage"}); tt += 1.5
    tl = {"runtime_s": runtime, "aspect": "9:16", "scenes": scenes, "caption_pages": pages, "rows": []}
    return tl, [], {"cues": [{"kind": "evidence", "in": page_at + 0.5, "out": page_at + 1.0}]}


def test_m30_fails_a_cut_onto_a_character_already_seen():
    tl, docks, mp = _cast_build(back_exit="cut")
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M30"].level == "FAIL", g["M30"]
    assert "s03 cuts onto mike at 0:26 - he entered first at 0:00" in g["M30"].message, g["M30"]
    assert "a re-entry MOUNTS" in g["M30"].message, g["M30"]


def test_m30_passes_when_the_returning_character_arrives_on_a_transition():
    tl, docks, mp = _cast_build(back_exit="dissolve")
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M30"].level == "PASS", g["M30"]
    assert "mike enters at 0:00 (s01)" in g["M30"].message, g["M30"]
    # the FIRST entry may be a cut - it is the cold open, and nothing has been seen yet
    tl, docks, mp = _cast_build(back_exit="dissolve", asset_back="clip-second-host", declare=True)
    assert _by_id(G.run(tl, docks, mp)[0])["M30"].level == "PASS"


def test_m30_reads_a_character_declared_by_its_evidence_species_and_is_absent_without_a_cast():
    tl, docks, mp = _cast_build(back_exit="cut", asset_back="clip-host-counter", declare=False)
    tl["evidence"] = {"clip-host-counter": {"species": "character"}}
    g = _by_id(G.run(tl, docks, mp)[0])
    assert g["M30"].level == "FAIL" and "clip-host-counter" in g["M30"].message, g["M30"]
    tl, docks, mp = _cast_build(back_exit="cut", declare=False)   # no world, species or evidence declares a cast
    assert "M30" not in _by_id(G.run(tl, docks, mp)[0])
