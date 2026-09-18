"""R26-232: THE PULSE ROWS READ A LIVING FULL-STAGE PAGE AS DEAD - the two terms they were missing.

(1) A CAPTION PAGE IS AN EVENT WHEREVER IT SITS. `gate_motion_density` counted a page in the STAGE
    register and counted a page in the ANCHORED strip as nothing at all, which R26-205 turned into a
    defect the day it landed: at 16:9 a full-stage ledger page is stamped `caption: "anchor"` and every
    caption page over it is stamped `cap_mode: "anchor"`, so the H bed's 24 anchored pages - one every
    ~1.75 s - read as 42 s of stillness (49 events, M05 / M10 / M16 FAIL on 6.2 / 7.0 / 8.3 s gaps).

(2) A LIVE PAGE'S OWN LIFE IS A SUSTAINED EVENT. R26-228 built the interior life of `idle=live` (the
    lead point's spark at 0.40 @ 0.62 Hz, the glow pulsing with it, every word walking 5.0 stage px at
    its own phase); the gate had no term for it, so the PULSE ROWS (M05, M10, M16) read a frame that
    never goes still as dead. They now credit one event every PAGE_LIFE_STEP_S = 1.613 s (the period of
    that measured 0.62 Hz spark - the slowest named cycle of the life) inside a live page's span, and
    name the term in the row's own text. It is a PULSE term only: M01 / M02 / M03 / M07 count the
    frame's own events exactly as before.

(3) The summary states both terms separately, so a reader sees what was counted.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402


def _by_id(gates: list) -> dict:
    return {x.id: x for x in gates}


# ---- (1) a caption page is an event wherever the PAGE puts it ------------------------------------

def _caption_tl(mode: str, runtime: float = 30.0, arrive: str | None = None, pinned: bool = True) -> dict:
    """ONE full-stage 16:9 ledger page row (R26-205: `full_stage` + `caption: "anchor"`) under caption
    pages every 1.5 s, five words each on its own spoken time. `pinned=False` is the ep1 shape instead:
    the same pages over picture plates, where an anchored page is the lower-third strip E21 read as
    stillness."""
    if pinned:
        scenes = [{"scene_id": "s01", "span": [0.0, runtime], "docks": [], "species": [],
                   "world": {"kind": "ledger", "asset_id": "ledger-page-1",
                             "page": {"enter": "roll", "exit": "retract", "full_stage": True, "caption": "anchor"}}}]
    else:
        scenes, t, i = [], 0.0, 0
        while t < runtime:
            scenes.append({"scene_id": f"s{i:02d}", "world": {"asset_id": f"world-{i}"},
                           "span": [t, min(t + 15.0, runtime)]})
            t += 15.0
            i += 1
    pages, t = [], 0.0
    while t < runtime:
        pg = {"s": t, "e": t + 1.4, "cap_mode": mode,
              "t": [{"w": "x", "s": t + 0.25 * k, "e": t + 0.25 * k + 0.25} for k in range(5)]}
        if arrive:
            pg["cap_arrive"] = arrive
        pages.append(pg)
        t += 1.5
    return {"runtime_s": runtime, "aspect": "16:9", "caption_modes": ["stage", "anchor"],
            "caption_pages": pages, "scenes": scenes}


def test_an_anchored_page_on_a_full_stage_row_counts_exactly_as_many_events_as_a_stage_page() -> None:
    """R26-232 (1): on the row R26-205 pins, the register does not decide whether the page happened."""
    anchored = G.analyse(_caption_tl("anchor"), [], {})
    staged = G.analyse(_caption_tl("stage"), [], {})
    assert anchored["events"] == staged["events"], (len(anchored["events"]), len(staged["events"]))
    assert anchored["cap_counts"]["instants"] == staged["cap_counts"]["instants"] > 20
    assert anchored["cap_counts"]["modes"] == {"anchor": 20} and staged["cap_counts"]["modes"] == {"stage": 20}
    assert anchored["cap_counts"]["unpinned_anchor"] == 0


def test_the_pinned_stretch_now_passes_m01_and_m08_as_the_staged_one_does() -> None:
    """The H bed's defect in miniature: the same rows, the same verdicts, either register."""
    for mode in ("anchor", "stage"):
        g = _by_id(G.run(_caption_tl(mode), [], {})[0])
        assert g["M01"].level == "PASS", (mode, g["M01"])
        assert g["M08"].level == "PASS", (mode, g["M08"])
    anchored = _by_id(G.run(_caption_tl("anchor"), [], {})[0])
    assert "counted: 20 anchor page(s), 100 word arrival(s)" in anchored["M08"].message, anchored["M08"].message


def test_an_anchored_page_the_page_did_not_pin_is_still_nothing() -> None:
    """E21, ep1's verdict ("ep1 died of VISUAL stillness"): a lower-third strip punching over a picture
    plate is what a viewer reads as stillness, and M01 / M08 are calibrated on that cut. R26-232 opened
    the pinned row, not the register - and the report says how many pages it passed over."""
    tl = _caption_tl("anchor", runtime=60.0, pinned=False)
    A = G.analyse(tl, [], {})
    g = _by_id(G.run(tl, [], {})[0])
    assert A["cap_counts"]["instants"] == 0 and A["cap_counts"]["unpinned_anchor"] == 40
    assert g["M01"].level == "FAIL" and g["M08"].level == "FAIL", (g["M01"], g["M08"])
    assert "40 unpinned anchored page(s) passed over (R26-232)" in g["M08"].message
    staged = G.analyse(_caption_tl("stage", runtime=60.0, pinned=False), [], {})
    assert staged["cap_counts"]["instants"] > 40          # the stage register over the same plates counts


def test_a_still_stretch_with_no_caption_page_at_all_still_fails_m08() -> None:
    """The row still bites: R26-232 widened which pages count, it did not retire the law."""
    tl = _caption_tl("anchor", runtime=60.0)
    tl["caption_pages"] = [dict(tl["caption_pages"][0])]          # one page at 0:00, then nothing for a minute
    g = _by_id(G.run(tl, [], {})[0])
    assert g["M08"].level == "FAIL" and "no stage-mode caption and no pinned anchored page" in g["M08"].message, g["M08"]
    assert g["M01"].level == "FAIL", g["M01"]


def test_the_envelope_is_a_stage_register_device_so_an_anchored_page_reads_its_raw_onsets() -> None:
    """`fuArrive = stage && ((pg.cap_arrive || TL.caption_arrive) === "fade_up")` (engine :16133): under
    the anchor the player never runs the stagger, so the gate must not credit its offsets."""
    onsets = [0.0, 0.02, 0.04, 0.06]      # three words crowding the first: the envelope would spread them
    page = {"s": 0.0, "e": 1.4, "cap_mode": "anchor", "cap_arrive": G.CAP_ARRIVE_FADE,
            "t": [{"w": "x", "s": o, "e": o + 0.2} for o in onsets]}
    pinned = {"scenes": [{"scene_id": "s01", "span": [0.0, 10.0],
                          "world": {"kind": "ledger", "page": {"caption": "anchor", "full_stage": True}}}],
              "caption_arrive": G.CAP_ARRIVE_FADE}
    rows, counts = G._caption_page_rows(pinned, [page])
    assert sorted(r["t"] for r in rows) == [0.0, 0.0, 0.02, 0.04, 0.06]      # the page's start + the raw onsets
    staged, _ = G._caption_page_rows(pinned, [dict(page, cap_mode="stage")])
    assert sorted(r["t"] for r in staged) == [0.0, 0.0, G.CAP_STAGGER_S, 2 * G.CAP_STAGGER_S, 3 * G.CAP_STAGGER_S]
    assert counts["words"] == 4


# ---- (2) a live page's own life is a sustained event for the pulse rows ---------------------------

def _live_page_tl(idle: str | None = "live", runtime: float = 30.0, kin_idle: bool = True) -> dict:
    """ONE ledger page holding a short's whole runtime with no captions and no docks: its authored beats
    land in the first 7.4 s (PAGE_BEAT_OFFSETS) and its retract in the last 2, so the middle is the
    20-second hole the pulse rows FAILed the H bed on."""
    world = {"kind": "ledger", "asset_id": "ledger-page-1",
             "page": {"enter": "roll", "exit": "retract", "full_stage": True, "caption": "anchor"}}
    if idle:
        world["idle"] = idle
    return {"runtime_s": runtime, "aspect": "9:16", "kinetics": {"idle": bool(kin_idle)},
            "scenes": [{"scene_id": "s01", "world": world, "span": [0.0, runtime], "docks": [], "species": []}],
            "caption_pages": []}


def test_a_page_with_no_idle_fails_the_three_pulse_rows() -> None:
    """The control: the same page without `idle=live` paints nothing in that hole, and the rows say so."""
    g = _by_id(G.run(_live_page_tl(idle=None), [], {})[0])
    for row in ("M05", "M10", "M16"):
        assert g[row].level == "FAIL", (row, g[row])
    assert "no visual event" in g["M05"].message
    assert "TERM page_life" not in g["M16"].message


def test_a_live_pages_span_does_not_fail_the_pulse_rows_and_the_row_names_the_term() -> None:
    """R26-232 (2): inside a live page's span the pulse rows read the page's own life."""
    A = G.analyse(_live_page_tl(), [], {})
    g = _by_id(G.run(_live_page_tl(), [], {})[0])
    for row in ("M05", "M10", "M16"):
        assert g[row].level == "PASS", (row, g[row])
        assert "TERM page_life (R26-232 (2))" in g[row].message, (row, g[row].message)
        assert "1.613s" in g[row].message and "s01" in g[row].message
    # the term is the page's own span, one event per measured cycle
    assert A["live_spans"] == [(0.0, 30.0, "s01")]
    assert A["page_life"][:3] == [0.0, 1.61, 3.23]
    # the instants are rounded to 2 dp, as every event list in this gate is (`_page_events`' own rounding)
    assert max(b - a for a, b in zip(A["page_life"], A["page_life"][1:])) <= G.PAGE_LIFE_STEP_S + 0.01
    assert G.PAGE_LIFE_STEP_S < G.SHORT_PULSE_MAX_S      # a live page clears the pulse floor by design


def test_the_step_is_the_measured_period_of_the_lead_points_spark() -> None:
    """The number is R26-228's own measurement (tests/R26-228-NOTE.md:194 - "0.40 @ 0.62 Hz ... period
    1.613 s"), never a number chosen to make a row pass."""
    assert G.PAGE_LIFE_STEP_S == 1.613
    assert abs(1.0 / 0.62 - G.PAGE_LIFE_STEP_S) < 0.005
    assert G.PAGE_LIFE_STEP_S > G.LIFE_CONTINUOUS_S      # the conservative read: slower than a steam / video-dock life


def test_the_life_term_is_the_pulse_rows_only() -> None:
    """M01 / M02 / M03 / M07 count the frame's own events: R26-232 changed the pulse rows and no other."""
    A = G.analyse(_live_page_tl(), [], {})
    g = _by_id(G.run(_live_page_tl(), [], {})[0])
    assert A["events"] == G.analyse(_live_page_tl(idle=None), [], {})["events"]
    assert A["still"][0][1] > G.STILL_FAIL_S and A["pulse_still"][0][1] <= G.PAGE_LIFE_STEP_S + 0.01
    assert g["M01"].level == "FAIL" and "TERM page_life" not in g["M01"].message
    assert "the PULSE rows' term, not this one" in g["M01"].message


def test_the_page_must_actually_render_the_life_the_row_asked_for() -> None:
    """`idleOf` returns "none" unless the timeline's kinetics carry `idle: true` (engine :7584), so a
    build with the idle switched off gets no term - the gate credits what the player paints."""
    g = _by_id(G.run(_live_page_tl(kin_idle=False), [], {})[0])
    for row in ("M05", "M10", "M16"):
        assert g[row].level == "FAIL", (row, g[row])
    assert G.analyse(_live_page_tl(kin_idle=False), [], {})["page_life"] == []


def test_the_pages_own_idle_outranks_the_rows() -> None:
    """`pgIdleKind = (pg && pg.idle) || scene.world.idle` (engine :7594): the PAGE's word first."""
    tl = _live_page_tl(idle="drift")
    tl["scenes"][0]["world"]["page"]["idle"] = "live"
    assert G.analyse(tl, [], {})["live_spans"] == [(0.0, 30.0, "s01")]
    tl["scenes"][0]["world"]["page"]["idle"] = "breath"
    tl["scenes"][0]["world"]["idle"] = "live"
    assert G.analyse(tl, [], {})["live_spans"] == []


# ---- (3) the summary states what was counted -----------------------------------------------------

def test_the_summary_states_the_caption_pages_and_the_live_page_term_separately() -> None:
    tl = _live_page_tl()
    tl["caption_pages"] = [{"s": 0.3, "e": 1.7, "cap_mode": "anchor",
                            "t": [{"w": "x", "s": 0.3 + 0.2 * k, "e": 0.5 + 0.2 * k} for k in range(5)]}]
    stats = G.run(tl, [], {})[1]
    assert "1 anchor" in stats["caption_page_events"] and "5 word arrival(s)" in stats["caption_page_events"]
    assert stats["caption_page_events"].startswith("6 from 1 page(s)")
    assert "every 1.613s inside s01 0:00-0:30" in stats["live_page_life"]
    assert "PULSE rows M05/M10/M16 only" in stats["live_page_life"]
    text = G.report_text(*G.run(tl, [], {}), Path("build-x"))
    assert "caption_page_events:" in text and "live_page_life:" in text


def test_a_build_with_no_live_page_says_so_in_the_summary() -> None:
    stats = G.run(_caption_tl("stage", pinned=False), [], {})[1]
    assert stats["live_page_life"].startswith("no page with idle=live")

# ---- R26-233's clause on the same row: a FOLLOWED rescale's clock IS the build -------------------

def _rescale_tl(follow: object | None, at: float = 3.0, runtime: float = 30.0) -> dict:
    """One dense-line page whose chart lands at PAGE_BUILD_END_S (7.4 s) with a `chart_to rescale` at 3.0 s -
    inside the build, which is where a FOLLOWED rescale belongs and a plain one does not."""
    sp = {"kind": "chart_to", "to": "rescale", "at": at, "dur": 1.0, "domain": [0.0, 640.0]}
    if follow is not None:
        sp["follow"] = follow
    return {"runtime_s": runtime, "aspect": "9:16", "kinetics": {"idle": True},
            "scenes": [{"scene_id": "s01", "span": [0.0, runtime], "docks": [], "species": [sp],
                        "world": {"kind": "ledger", "asset_id": "ledger-page-1",
                                  "page": {"enter": "roll", "exit": "retract", "builder": "dense-line",
                                           "full_stage": True, "caption": "anchor"}}}]}


def test_a_followed_rescale_over_its_build_is_not_a_transition_over_a_build() -> None:
    """R26-233: `follow` puts the domain on the followed LINE's clock (the top is that series' drawn extremum,
    `build_scene_timeline_f.py:3796`), so the line's `build_to` IS the rescale's clock - over the build is the
    shape the verb exists for. The compiler resolves the key to the series' INDEX, and 0 is a legal answer."""
    for follow in (True, 0, 2):
        g = _by_id(G.run(_rescale_tl(follow), [], {})[0])
        assert g["M23"].level == "PASS", (follow, g["M23"])
        assert "FOLLOWS its line" in g["M23"].message and "R26-233" in g["M23"].message, g["M23"].message
    assert "R26-233" in G.SRC_M23 and "EXEMPT from the over-a-build check" in G.SRC_M23


def test_a_plain_rescale_over_a_build_still_warns() -> None:
    """The row still bites: a rescale that names no `follow` is exactly the rescale it was (E45/E50)."""
    for follow in (None, False):
        g = _by_id(G.run(_rescale_tl(follow), [], {})[0])
        assert g["M23"].level == "WARN", (follow, g["M23"])
        assert "fires inside the page's build beat" in g["M23"].message, g["M23"].message
        assert "FOLLOWS its line" not in g["M23"].message
    # and a followed rescale keeps every OTHER fault: the edge check is untouched
    late = _by_id(G.run(_rescale_tl(True, at=29.4), [], {})[0])
    assert late["M23"].level == "WARN" and "ends inside the last 0.5 s of its page" in late["M23"].message, late["M23"]
