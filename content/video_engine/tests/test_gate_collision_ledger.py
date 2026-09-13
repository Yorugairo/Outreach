"""M34 - the collision ledger (K9: C05-R023 + C09-R003; the casebook's ring-on-the-tip-label and
name-on-the-neighbour-line). Every text box a page shows - ticks, values, series names, pills, a ring's or a
callout's own label and flag - is checked against every MARK (a ring's or a callout's stroke) and every SERIES
polyline, from probe.py's own DOM read; a mark's own text stays married to its ellipse.

The fixtures are stage px at 9:16. The two casebook "before" geometries are read off the frames in each case
(half-scale PNGs, doubled) and the probe's own box for "10-year" on review-v1 at 19.16 s."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import gate_motion_density as G  # noqa: E402
import probe as P  # noqa: E402


def _inst(t=57.0, labels=(), lines=(), marks=(), scene="s06"):
    return {"t": t, "why": "fixture", "docks": [], "page": {}, "texts": [], "overlaps": [],
            "labels": [dict(role=r, text=x, box=list(b), **({"own": o} if o else {})) for r, x, b, o in labels],
            "ledger": {"lines": [{"own": o, "hw": hw, "pts": [list(p) for p in pts]} for o, hw, pts in lines],
                       "marks": [{"own": m[0], "kind": m[1], "e": list(m[2]), "hw": m[3], **({"tg": list(m[4])} if len(m) > 4 else {})}
                                 for m in marks]},
            "clearances": {"safe_pct": {}}, "camera": {"scene": scene, "zoom": 1.0, "look": [540, 960]},
            "marks": {"n": 1, "drawn": 1.0, "up": 1.0, "parked": False}}


def _doc(*instants, aspect="9:16"):
    return {"player_sha256": "x", "aspect": aspect, "instants": list(instants)}


# ---- the casebook, before and after -----------------------------------------------------------------------------
# ring-on-the-tip-label, 0:57 (before.png, doubled): the debt line's tip at (820, 656); "x3.9 Federal debt" ends
# 8 px left of it (the builder's old gap), 30 px above; the dashed 123% ring hugs the tip at rx 54 / ry 40
# (RING.MIN_RX / MIN_RY).
DEBT_TIP = (820, 656)
DEBT_LINE = ("s0", 2, [(380, 1000), (560, 880), (700, 760), (745, 700), (752, 610), (770, 690), DEBT_TIP])   # the 2020 spike left of "123%"
RING_123 = ("m1", "ring", (820, 656, 54, 40), 3)
RING_LABEL = ("mark", "123%", (752, 572, 70, 34), "m1")


def _debt_name(right: int):
    return ("sname", "x3.9 Federal debt", (right - 360, 578, 360, 56), "s0")


def test_the_ring_painted_over_its_own_line_s_name_fails():
    before = _inst(labels=[_debt_name(DEBT_TIP[0] - 8), RING_LABEL], lines=[DEBT_LINE], marks=[RING_123])
    g = G._collision_gate(_doc(before))
    assert g is not None and g.level == "FAIL", g and g.message
    assert "ring m1 over sname:x3.9 Federal debt" in g.message and "0:57" in g.message, g.message
    assert "over mark:123%" not in g.message, "a mark's own label is not a fault"


def test_the_name_moved_past_the_ring_s_reach_passes():
    after = _inst(labels=[_debt_name(DEBT_TIP[0] - 8 - 110), RING_LABEL], lines=[DEBT_LINE], marks=[RING_123])
    g = G._collision_gate(_doc(after))
    assert g.level == "PASS", g.message


# name-on-the-neighbour-line, 0:19.5: "10-year" at the probe's own box (review-v1 layout-probe.json, 19.16 s),
# the grey 30-year line through it, the orange 10-year line below with its 4.83% datum at (812, 796) ringed by
# the callout at pad 24 (calloutPath: rx = 22 + pad, ry = 18 + pad).
TEN_NAME = ("sname", "10-year", (647, 724, 157, 50), "s0")
THIRTY_NAME = ("sname", "30-year", (647, 556, 157, 50), "s1")
TEN_LINE = ("s0", 2, [(220, 1030), (500, 930), (700, 850), (812, 796)])
THIRTY_LINE = ("s1", 2, [(220, 780), (500, 760), (600, 790), (660, 760), (740, 660), (812, 632)])
CALLOUT_483 = ("m0", "callout", (812, 796, 46, 42), 3)


def test_a_name_across_the_neighbour_s_line_fails_and_under_its_own_line_passes():
    before = _inst(19.5, labels=[TEN_NAME, THIRTY_NAME], lines=[TEN_LINE, THIRTY_LINE], scene="s02")
    g = G._collision_gate(_doc(before))
    assert g.level == "FAIL", g.message
    assert "sname:10-year on line s1" in g.message and "0:19" in g.message, g.message
    under = ("sname", "10-year", (600, 870, 157, 50), "s0")   # under its own line, the 41bf55c placement
    after = _inst(20.8, labels=[under, THIRTY_NAME], lines=[TEN_LINE, THIRTY_LINE], scene="s02")
    assert G._collision_gate(_doc(after)).level == "PASS", G._collision_gate(_doc(after)).message


def test_the_callout_arc_clipping_the_neighbour_name_fails_as_a_mark_over_text():
    before = _inst(19.5, labels=[TEN_NAME], lines=[TEN_LINE], marks=[CALLOUT_483], scene="s02")
    g = G._collision_gate(_doc(before))
    assert g.level == "FAIL" and "callout m0 over sname:10-year" in g.message, g.message


# ---- the rules, one at a time -----------------------------------------------------------------------------------

def test_a_mark_s_own_label_and_flag_may_touch_its_stroke():
    own = [("mark", "123%", (860, 600, 70, 34), "m1"), ("flag", "today", (800, 680, 60, 60), "m1")]
    g = G._collision_gate(_doc(_inst(labels=own, marks=[RING_123])))
    assert g.level == "PASS", g.message


def test_text_wholly_inside_a_ring_is_what_a_ring_circles():
    circled = ("val", "123%", (800, 640, 40, 30), None)
    assert G._collision_gate(_doc(_inst(labels=[circled], marks=[RING_123]))).level == "PASS"


def test_a_hairline_of_antialiasing_is_not_a_crossing():
    box = ("tick", "5", (100, 100, 40, 40), None)
    grazing = ("s3", 2, [(90, 141), (200, 141)])   # centre 1 px below the box, ink (hw 2) 1 px inside it: under LINE_TOUCH_PX
    assert G._collision_gate(_doc(_inst(labels=[box], lines=[grazing]))).level == "PASS"
    through = ("s3", 2, [(90, 120), (200, 120)])
    assert G._collision_gate(_doc(_inst(labels=[box], lines=[through]))).level == "FAIL"


def test_a_name_on_its_own_line_away_from_the_end_warns():
    far = ("sname", "x3.9 Federal debt", (200, 850, 360, 56), "s0")   # across its own line's middle, 260 px from the tip
    g = G._collision_gate(_doc(_inst(labels=[far], lines=[DEBT_LINE])))
    assert g.level == "WARN" and "its own line" in g.message, g.message
    # at the end - inside the builder's 8 px + the 110 px tip clearance - it is where a direct label belongs
    at_end = ("sname", "x3.9 Federal debt", (342, 720, 360, 56), "s0")   # touches its line at (700, 760), 118 px from the tip
    assert G._collision_gate(_doc(_inst(labels=[at_end], lines=[DEBT_LINE]))).level == "PASS"
    # a muted history is the same series: its live name across it away from the end is the same WARN, never a FAIL
    muted = ("s0:h", 2, [(100, 900), (500, 900)])
    g = G._collision_gate(_doc(_inst(labels=[far], lines=[DEBT_LINE, muted])))
    assert g.level == "WARN" and "FAIL" not in g.level, g.message


def test_a_name_near_its_end_may_cross_its_own_history_and_never_a_neighbour_s():
    """Parent decision 2026-09-13: `s0:h` is s0. Within the reach of the LIVE line's end (118 px portrait) the name
    may cross its own history; a DIFFERENT series' history is still a line it does not name."""
    near = _debt_name(DEBT_TIP[0] - 118)                       # right edge 118 px from the live tip: inside the reach
    own_history = ("s0:h", 2, [(100, 600), (500, 600)])
    assert G._collision_gate(_doc(_inst(labels=[near], lines=[DEBT_LINE, own_history]))).level == "PASS"
    neighbour_history = ("s1:h", 2, [(100, 600), (500, 600)])
    g = G._collision_gate(_doc(_inst(labels=[near], lines=[DEBT_LINE, neighbour_history])))
    assert g.level == "FAIL" and "sname:x3.9 Federal debt on line s1" in g.message, g.message


def test_the_tip_reach_is_the_engine_s_own_per_aspect():
    assert G.TIP_REACH_PX == {"9:16": 8 + 110, "16:9": 12 + 56}


def test_a_mark_s_label_that_has_left_its_ellipse_warns():
    wandered = ("mark", "123%", (400, 300, 70, 34), "m1")
    g = G._collision_gate(_doc(_inst(labels=[wandered], marks=[RING_123])))
    assert g.level == "WARN" and "married" in g.message and "mark:123%" in g.message, g.message
    near = ("mark", "123%", (820 + 54 + 12, 580, 70, 34), "m1")    # the ring's own place: 12 px off the ellipse
    assert G._collision_gate(_doc(_inst(labels=[near], marks=[RING_123]))).level == "PASS"
    assert G.MARRY_PX == 34 + 18


def test_m34_says_nothing_until_the_probe_has_run_and_info_when_the_probe_predates_the_ledger():
    assert G._collision_gate(None) is None and G._collision_gate("stale") is None   # M28 already names the missing probe
    old = _inst(labels=[TEN_NAME])
    del old["ledger"]
    g = G._collision_gate(_doc(old))
    assert g.level == "INFO" and "probe.py" in g.message, g.message
    empty = G._collision_gate(_doc(_inst()))
    assert empty.level == "INFO" and "nothing to check" in empty.message, empty.message


def test_one_fault_at_four_instants_is_one_row():
    rows = [_inst(t, labels=[TEN_NAME], lines=[TEN_LINE, THIRTY_LINE], scene="s02") for t in (19.2, 19.4, 19.6, 19.8)]
    g = G._collision_gate(_doc(*rows))
    assert g.message.startswith("1 collision(s)"), g.message
    # a bracket label across a series' muted history AND its live line is one collision with that series
    history = ("s1:h", 2, [(600, 750), (820, 750)])
    g = G._collision_gate(_doc(_inst(labels=[TEN_NAME], lines=[THIRTY_LINE, history])))
    assert g.message.startswith("1 collision(s)") and "on line s1 " in g.message, g.message


def test_m34_is_wired_and_cites_both_cases():
    assert "ring-on-the-tip-label" in G.SRC_M34 and "name-on-the-neighbour-line" in G.SRC_M34
    assert "C05-R023" in G.SRC_M34 and "C09-R003" in G.SRC_M34
    tl = {"runtime_s": 60.0, "aspect": "9:16", "scenes": []}
    gates, _ = G.run(tl, [], {}, layout=_doc(_inst(labels=[TEN_NAME], lines=[THIRTY_LINE])))
    assert [x.level for x in gates if x.id == "M34"] == ["FAIL"]
    gates, _ = G.run(tl, [], {}, layout=None)
    assert not [x for x in gates if x.id == "M34"]


def test_the_segment_box_arithmetic():
    assert G._seg_hits_box((0, 5), (10, 5), [2, 0, 4, 10], 0)
    assert not G._seg_hits_box((0, 20), (10, 20), [2, 0, 4, 10], 0)
    assert G._seg_hits_box((0, 13), (10, 13), [2, 0, 4, 10], 4)          # inflated by 4
    assert G._seg_hits_box((3, 3), (4, 4), [2, 0, 4, 10], 0)             # wholly inside
    assert not G._seg_hits_box((0, -5), (1, -1), [2, 0, 4, 10], 0)


# ---- the probe's side: the ledger it writes --------------------------------------------------------------------

def _dom(labels=(), lines=(), marks=()):
    return {"docks": [], "items": [], "plots": [], "data": [], "chart": None, "caption": None, "marks": None,
            "labels": list(labels), "lines": list(lines), "smarks": list(marks)}


def test_the_probe_derives_the_ledger_rounded_simplified_and_owned():
    straight = [[100 + i * 10.3, 500.2] for i in range(49)]
    far_away = [[100, 1500], [600, 1500]]
    dom = _dom(labels=[{"role": "sname", "text": "10-year", "box": [647.4, 724, 157, 50], "own": "s0"},
                       {"role": "tick", "text": "4", "box": [194, 480, 23, 45]}],
               lines=[{"own": "s0", "hw": 2.0, "pts": straight}, {"own": "s1", "hw": 2.0, "pts": far_away}],
               marks=[{"own": "m0", "kind": "ring", "box": [766, 616, 108, 80], "hw": 3.0}])   # an SVG box is the geometry, stroke excluded
    out = P.derive(dom, 19.5, "fixture", {}, "9:16", {})
    assert out["labels"][0] == {"role": "sname", "text": "10-year", "box": [647, 724, 157, 50], "own": "s0"}
    assert "own" not in out["labels"][1]
    assert out["ledger"]["lines"] == [{"own": "s0", "hw": 2, "tip": [594, 500], "p": [100, 500, 594, 500]}]   # collinear points dropped, written flat
    # ... and a line that comes near no text box is not written at all: the gate would read nothing off it
    assert out["ledger"]["marks"] == [{"own": "m0", "kind": "ring", "e": [820, 656, 54, 40], "hw": 3}]


def test_the_ledger_writes_only_the_runs_near_text_and_the_gate_still_reads_the_tip():
    bent = [[100, 100], [300, 100], [300, 400], [500, 400], [500, 900], [900, 900]]
    name = {"role": "sname", "text": "x3.9 Federal debt", "box": [330, 360, 150, 60], "own": "s0"}
    out = P.derive(_dom(labels=[name], lines=[{"own": "s0", "hw": 2.0, "pts": bent}]), 1.0, "fixture", {}, "9:16", {})
    assert out["ledger"]["lines"] == [{"own": "s0", "hw": 2, "tip": [900, 900], "p": [300, 400, 500, 400]}]
    doc = _doc(dict(_inst(1.0), labels=out["labels"], ledger=out["ledger"]))
    g = G._collision_gate(doc)
    assert g.level == "WARN" and "420 px from the line's end" in g.message, g.message   # measured to the TIP, not the run's end


def test_simplify_keeps_a_bend():
    pts = [[0, 0], [50, 1], [100, 0], [150, 80], [200, 160]]
    assert P.simplify(pts, 3.0) == [[0, 0], [100, 0], [200, 160]]


def test_the_gate_s_instants_include_each_mark_once_it_has_closed():
    tl = {"runtime_s": 60.0, "scenes": [{"scene_id": "s06", "span": [10.0, 59.0], "species": [
        {"kind": "ring", "at": 54.86, "dur": 2.4, "target": {"kind": "datum", "index": 240}},
        {"kind": "callout", "at": 19.16, "dur": 2.2, "target": {"kind": "datum", "index": 172}}]}]}
    got = {w: t for t, w in P.gate_instants(tl)}
    assert abs(got["s06 ring closed"] - (54.86 + P.MARK_CLOSED_S)) < 0.02, got
    assert abs(got["s06 callout closed"] - (19.16 + P.MARK_CLOSED_S)) < 0.02, got


def test_read_dom_exports_the_series_the_marks_and_their_owners():
    js = P.READ_DOM
    for needle in ("out.lines", "out.smarks", "species-under", "rngdash", "path.co", "chipcard", "own:",
                   "bracketOf", "targetsOf", "tg: targetsOf", "pf.figures", "pf.brackets"):
        assert needle in js, needle


# ---- the operator's corrections, 2026-09-13 ---------------------------------------------------------------------
# "bracket should probably be able to bypass that rule" / "a ring or callout drawn over a label doesn't automatically
# fail, if the point is to draw a ring or highlight around that label - but we have spotlight tools"
FIGURE_31 = ("bracket", "31% of GDP", (393, 952, 219, 65), "s0")   # the bridge's figure at datum 63, as re-probed
EARLY_DEBT = ("s0", 2, [(380, 1020), (396, 997), (407, 993), (560, 880), (820, 656)])   # tip 208 px right of the figure: past the reach


def test_a_bracket_on_the_series_it_measures_passes_anywhere_on_it():
    g = G._collision_gate(_doc(_inst(27.7, labels=[FIGURE_31], lines=[EARLY_DEBT, ("s0:h", 2, [(300, 1040), (396, 998)])], scene="s04")))
    assert g.level == "PASS", g.message


def test_a_bracket_across_a_different_series_line_still_fails():
    other = ("bracket", "31% of GDP", (393, 952, 219, 65), "s1")
    g = G._collision_gate(_doc(_inst(27.7, labels=[other], lines=[EARLY_DEBT], scene="s04")))
    assert g.level == "FAIL" and "bracket:31% of GDP on line s0" in g.message, g.message


def test_a_ring_over_its_own_target_label_warns_and_names_the_spotlight():
    value = ("val", "123%", (760, 600, 90, 50), None)                        # the stroke runs through it
    ring = ("m1", "ring", (820, 656, 54, 40), 3, ["val:123%"])
    g = G._collision_gate(_doc(_inst(labels=[value], marks=[ring])))
    assert g.level == "WARN" and "spotlight" in g.message and "its own target val:123%" in g.message, g.message


def test_a_ring_over_an_unrelated_label_still_fails_when_it_has_a_target():
    tick = ("tick", "100", (760, 600, 90, 50), None)
    ring = ("m1", "ring", (820, 656, 54, 40), 3, ["val:123%"])
    g = G._collision_gate(_doc(_inst(labels=[tick], marks=[ring])))
    assert g.level == "FAIL" and "ring m1 over tick:100" in g.message, g.message


def test_the_probe_carries_a_mark_s_targets_cut_as_the_label_text_is():
    dom = _dom(marks=[{"own": "m0", "kind": "ring", "box": [766, 616, 108, 80], "hw": 3,
                       "tg": ["bracket:31% of GDP and more", "val:123%", "val:123%"]}])
    assert P.derive(dom, 1.0, "fixture", {}, "9:16", {})["ledger"]["marks"][0]["tg"] == ["bracket:31% of GDP and", "val:123%"]
