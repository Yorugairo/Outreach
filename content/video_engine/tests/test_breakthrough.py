"""The BREAKTHROUGH bars (2026-09-10; the operator: "show the average bond market return over the last 10 yrs with the average
return of SOXX as the breakthrough" / "either the breakthrough shows at the bond level (the comparator) then stacks each frame
that same amount til it builds to its real number, OR it builds to 1.52% right next to the bonds, then immediately counts/shoots
up to breakthrough up to 36.59%").

A bars page STATES its scale (`domain`) that one value cannot fit. That bar builds to the COMPARATOR's level (the tallest honest
bar) with the others, holds, then runs by one of two mechanics:
  burst (Bravos, measured at 8:02 of the SPR chart): it shoots to its true height WHILE the scale rewrites to the nice ceiling
        above it; the honest bar shrinks to a sliver; old ticks slide and fade, new ones fade in; an overshoot settles; it glows.
  stack (the operator's A): the scale holds; the bar grows one comparator per step until its number - off the page.
The scale and the value are printed at every instant (E28/E53). A page that declares neither is byte-identical (the goldens).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LP  # noqa: E402
import render_baseline as RB  # noqa: E402

EP = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
OBJ = EP / "evidence/objects/ev-bonds-vs-chips-10y-v1.series.json"
PLATE = "ledger:ev-bonds-vs-chips-10y-v1:bars:1:right"
BUILD_AT = 0.7 + 0.8 + 2.4 + 0.5   # LP.ROLL + SAVOR + FIELD + PUNCH: the bars build from here, for the page's build_s (LP.BUILD 3.0 by default)
HOLD, RUN, SETTLE, STEP = 0.5, 0.6, 0.3, 0.06   # LPX.BT_* mirrored
BUILD_S = float(json.loads(OBJ.read_text(encoding="utf-8")).get("build_s", 3.0)) if OBJ.exists() else 3.0   # the object's own build (Tokyo: 1.2 s)
T_HOLD = BUILD_AT + BUILD_S + HOLD / 2      # built, standing at the comparator's level
T_RUN0 = BUILD_AT + BUILD_S + HOLD          # the run begins

needs_object = pytest.mark.skipif(not OBJ.exists(), reason="the bonds-vs-chips object is not on disk")


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the grammar ------------------------------------------------------------------------------------


def test_overflow_is_an_axes_key_the_story_block_carries():
    assert "overflow" in LP.AXES_KEYS and "domain" in LP.AXES_KEYS
    axes = LP._story_block({"bars": [{"label": "a", "value": 1.5}, {"label": "b", "value": 36.6}],
                            "domain": [0, 8], "overflow": "burst"}).get("axes")
    assert axes == {"overflow": "burst", "domain": [0, 8]}, "the scale and the mechanic ride the page's axes"


def test_a_bars_page_without_a_domain_carries_no_axes():
    assert "axes" not in LP._story_block({"bars": [{"label": "a", "value": 1.5}]}), "a page that declares nothing is unchanged"


GOOD = {"title": "t", "src": "s", "bars": [{"label": "Bonds", "value": 1.52}, {"label": "Chips", "value": 36.59}], "domain": [0, 8], "overflow": "burst"}


@pytest.mark.parametrize("over, needle", [
    ({"overflow": "wobble"}, "not one of burst|stack|break"),
    ({"domain": None}, "needs a stated scale"),
    ({"domain": [8, 0]}, "needs a stated scale"),
    ({"bars": [{"label": "Bonds", "value": 1.52}, {"label": "Chips", "value": 6.0}]}, "no bar makes"),
    ({"bars": [{"label": "Bonds", "value": 12.0}, {"label": "Chips", "value": 36.59}]}, "lie of the other kind"),
])
def test_an_overflow_is_checked_not_trusted(over, needle):
    """E60: the mechanic is one we have, the scale is stated, one bar breaks it, one bar reads on it."""
    errs = LP.validate({**GOOD, **over}, "bars")
    assert any(needle in e for e in errs), (needle, errs)


def test_a_sound_overflow_page_validates_and_a_line_page_may_not_carry_one():
    assert LP.validate(GOOD, "bars") == []
    assert LP.validate({**GOOD, "overflow": "stack"}, "bars") == [] and LP.validate({**GOOD, "overflow": "break"}, "bars") == []
    line = {"title": "t", "src": "s", "series": [{"name": "a", "pts": [[0, 1], [1, 2]]}], "domain": [0, 8], "overflow": "burst"}
    assert any("BARS page's device" in e for e in LP.validate(line, "line"))


@needs_object
def test_the_object_states_its_scale_and_its_figures_are_the_sourced_ones():
    obj = json.loads(OBJ.read_text(encoding="utf-8"))
    assert obj["domain"] == [0, 8] and obj["overflow"] == "burst", "Bravos's mechanic is the default"
    vals = {b["label"]: b["value"] for b in obj["bars"]}
    assert vals == {"Bonds": 1.52, "Chips": 36.59}, "iShares AGG / SOXX ten-year average annual total return (NAV)"
    assert "ishares-soxx-agg-returns-2026-09-10" in obj["src_full"], "the source on disk is named on the page"


# ---- the page ----------------------------------------------------------------------------------------


PROBE = """() => {
  const st = window.wA?.__lp || window.wB?.__lp || document.querySelector('.world')?.__lp;
  const bars = st.bars.map(b => ({ i: b.i, over: !!b.over, h: b.h, end: b.end, y: Number(b.bar.getAttribute('y')), bx: b.bx, bw: b.bw,
                                   snap: b.snap ? Number(b.snap[0].getAttribute('opacity')) : null, filter: b.bar.style.filter || "" }));
  const B = st.bt || null;
  const pill = st.cpill || (st.callout ? st.callout.querySelector('.cpill') : null);
  const track = st.chart.querySelector('rect.btrack'), stamp = st.chart.querySelector('text.bstamp'), lead = st.chart.querySelector('line.blead');
  const num = (el, a) => el ? Number(el.getAttribute(a)) : null;
  const e = st.bars.find(b => b.over);
  return { bars, base: st.bt ? st.bt.base : null, top: st.bt ? st.bt.top : null, plot: st.bt ? st.bt.plot : null,
           track: track ? { op: num(track, 'opacity'), y: num(track, 'y'), h: num(track, 'height') } : null,
           stamp: stamp ? { op: num(stamp, 'opacity'), y: num(stamp, 'y'), txt: stamp.textContent } : null,
           lead: lead ? { y1: num(lead, 'y1'), y2: num(lead, 'y2'), x: num(lead, 'x1'), op: num(lead, 'opacity'), dash: lead.getAttribute('stroke-dasharray') } : null,
           calloutOp: st.callout ? Number(st.callout.getAttribute('opacity')) : null,
           cad: st.bt && st.bt.cad ? { hold: st.bt.cad.hold, fps: st.bt.cad.fps, why: st.bt.cad.why } : null,
           labY: e ? Number(e.lab.getAttribute('y')) : null, end: e ? e.end : null,
           y1: st.scale.y1, y0: st.scale.y0, mode: B && B.mode, comp: B && B.comp, hi1: B && B.hi1,
           old: B ? B.ticks0.filter((e, j) => (j & 1) === 1 && B.vals0[j >> 1] !== 0).map(e => Number(e.getAttribute('opacity') ?? 1)) : [],
           neu: B ? B.ticks1.map(e => Number(e.getAttribute('opacity'))) : [],
           text: st.cval ? st.cval.textContent : null, pillY: pill ? Number(pill.getAttribute('y')) : null,
           pillW: pill ? Number(pill.getAttribute('width')) : null, textW: st.cval ? st.cval.getComputedTextLength() : null };
}"""


def _player(mode: str, opts: dict | None = None):
    """The breakthrough page, with whatever OPTIONS the slice is about laid on its axes (P50 T10/T13).
    `opts` None is the page exactly as E60 shipped it."""
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    world = json.loads(json.dumps(world)); world["page"]["axes"]["overflow"] = mode
    world["page"]["axes"].update(opts or {})
    scene = dict(tl["scenes"][0], species=[], span=[0.0, 16.0], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=16.0, scenes=[scene], caption_pages=[], captions=[])
    timeline["kinetics"] = dict(timeline.get("kinetics") or {}, min_jerk=True)
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "breakthrough.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["9:16"]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return page, errs, close


def _at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(PROBE)


@needs_object
@needs_browser
def test_the_breaking_bar_first_stands_at_the_comparator_s_level_in_both_mechanics():
    for mode in ("burst", "stack"):
        page, errs, close = _player(mode)
        try:
            p = _at(page, T_HOLD)
            assert not errs, errs
            assert p["mode"] == mode and p["comp"] == 1.52 and p["y1"] == 8
            bonds, chips = p["bars"]
            assert chips["over"] and not bonds["over"]
            assert abs(chips["h"] - bonds["h"]) < 0.6, ("a bar like the others, at the bonds' level", mode, chips["h"], bonds["h"])
            assert abs(bonds["h"] - p["plot"] * 1.52 / 8) < 0.6, "the honest bar is honest on the stated scale"
            assert p["text"] == "1.52%", "the pill counts to the comparator, not past it"
        finally:
            close()


@needs_object
@needs_browser
def test_the_burst_shoots_while_the_scale_rewrites_and_lands_on_the_number():
    page, errs, close = _player("burst")
    try:
        mid = _at(page, T_RUN0 + RUN * 0.45)
        assert 8 < mid["y1"] < 40, ("the scale is mid-rewrite", mid["y1"])
        assert 0 < mid["old"][0] < 1 and 0 < mid["neu"][0] < 1, "old ticks leaving, new ticks arriving"
        chips = mid["bars"][1]
        assert 1.52 < float(mid["text"].rstrip("%")) < 36.59 and "drop-shadow" in chips["filter"]
        end = _at(page, 10.0)
        assert not errs, errs
        assert end["y1"] == 40 and end["hi1"] == 40, "the nice ceiling above 36.59 (Bravos: 1,405 on 0-1500)"
        bonds, chips = end["bars"]
        assert abs(chips["h"] - end["plot"] * 36.59 / 40) < 0.6, "the true height on the rewritten scale"
        assert abs(bonds["h"] - max(3, end["plot"] * 1.52 / 40)) < 0.6, "the honest bar is a sliver now"
        assert chips["end"] > end["top"], "inside the frame: Bravos does not break it, it rescales it"
        assert all(o == 0 for o in end["old"]) and all(n == 1 for n in end["neu"])
        assert end["text"] == "36.59%" and end["pillW"] >= end["textW"] + 20
        assert "drop-shadow" in chips["filter"], "the glow holds"
    finally:
        close()


@needs_object
@needs_browser
def test_the_stack_grows_one_comparator_per_step_off_the_page_at_the_stated_scale():
    page, errs, close = _player("stack")
    try:
        mid = _at(page, T_RUN0 + STEP * 6.5)   # the comparator brick + seven steps: 1.52 x 8 = 12.16
        assert mid["y1"] == 8, "the scale holds"
        chips = mid["bars"][1]
        assert mid["text"] == "12.2%" and abs(chips["h"] - mid["plot"] * 12.16 / 8) < 0.6, (mid["text"], chips["h"])
        assert chips["snap"] == 1, "the top gridline has snapped"
        end = _at(page, 10.0)
        assert not errs, errs
        chips = end["bars"][1]
        assert end["y1"] == 8 and abs(chips["h"] - end["plot"] * 36.59 / 8) < 0.6, "the true height on the STATED scale"
        assert chips["y"] < end["top"] - end["plot"], "far above the plot - the page's edge is what clips it"
        assert end["text"] == "36.59%" and end["pillY"] == 24, "the pill sits inside its own bar once the tip has left"
        assert chips["filter"] == "", "no glow on the stack"
    finally:
        close()


T_MID = BUILD_AT + BUILD_S * 0.5   # mid-build: the bars law is running, the breakthrough's clock (bts) is still negative


# ---- P50 T10: the burst's furniture ---------------------------------------------------------------------


FURNITURE = {"overflow_placeholder": "?", "overflow_capsule": "axis"}
PH_OUT_S = 0.18   # BREAK.PH_OUT_S mirrored: the mark leaves over this much of the hold


def test_the_furniture_keys_ride_the_axes_and_are_checked_beside_the_overflow():
    """E60's furniture is grammar on the OBJECT, validated with the mechanic it belongs to - a dial nothing
    reads is worse than an error, so it is one."""
    for k in ("overflow_placeholder", "overflow_capsule", "break_cadence"):
        assert k in LP.AXES_KEYS
    assert LP.validate({**GOOD, **FURNITURE, "break_cadence": "stop"}, "bars") == []
    axes = LP._story_block({"bars": GOOD["bars"], "domain": [0, 8], "overflow": "burst", **FURNITURE}).get("axes")
    assert axes["overflow_placeholder"] == "?" and axes["overflow_capsule"] == "axis"
    assert any("declares no 'overflow'" in e for e in LP.validate({**{k: v for k, v in GOOD.items() if k != "overflow"}, "overflow_placeholder": "?"}, "bars"))
    # `placeholder` is NOT this key: since the intake it has marked figures still under SOURCES-TO-VERIFY,
    # and a page never renders those (AGENTS.md). Taking it would have weakened that refusal.
    assert any("SOURCES-TO-VERIFY" in e for e in LP.validate({**GOOD, "status": "SOURCES-TO-VERIFY", "placeholder": True}, "bars"))
    assert any("not one of axis" in e for e in LP.validate({**GOOD, "overflow_capsule": "tip"}, "bars"))
    assert any("not a caption" in e for e in LP.validate({**GOOD, "overflow_placeholder": "unknown"}, "bars"))
    assert any("already steps" in e for e in LP.validate({**GOOD, "overflow": "stack", "break_cadence": "stop"}, "bars"))


@needs_object
@needs_browser
def test_the_placeholder_holds_the_number_s_place_until_it_is_spoken():
    """T10: Bravos 8:01.8 - the row is a grey "?" track until the number is said. Ours: the mark stands where
    the number will be, the track stands behind the bar at the comparator's height, and the COUNT that would
    otherwise sit there is held back. "Spoken" is the start of the hold."""
    page, errs, close = _player("burst", FURNITURE)
    try:
        for t in (BUILD_AT + BUILD_S * 0.25, T_MID, BUILD_AT + BUILD_S - 0.01):
            p = _at(page, t)
            assert p["stamp"]["txt"] == "?" and p["stamp"]["op"] == 1, ("the mark stands through the build", t, p["stamp"])
            assert p["track"]["op"] > 0, "and the track stands behind the bar"
            assert p["calloutOp"] == 0, "... while the count is held back: one mark on the page, never two"
        p = _at(page, T_MID)
        comp_h = p["plot"] * 1.52 / 8
        assert abs(p["track"]["h"] - comp_h) < 0.6, ("the track is the COMPARATOR's height - furniture, not data (E28)", p["track"])
        assert abs(p["track"]["y"] - (p["base"] - comp_h)) < 0.6
        assert p["stamp"]["y"] < p["track"]["y"], "the mark is written above the track's top edge, where the number will be"
        q = _at(page, T_HOLD)   # 0.25 s into the hold, past PH_OUT_S
        assert not errs, errs
        assert q["stamp"]["op"] == 0 and q["track"]["op"] == 0, "the mark leaves as the number is spoken"
        assert q["calloutOp"] == 1 and q["text"] == "1.52%", "and the count stands in its place, at the comparator"
        assert _at(page, 10.0)["text"] == "36.59%", "the burst lands on its number as it always did"
    finally:
        close()


@needs_object
@needs_browser
def test_the_capsule_mounts_on_the_axis_with_a_dotted_leader_to_the_bar_s_end():
    """T10: Bravos 8:02.6 - a value capsule counts up ON THE AXIS under the bar's end with a dotted leader.
    Ours mounts at the zero line, fits the band the chart's box leaves (the page's citation is below it, E52),
    takes the x-label's row - the name goes above the zero line - and routes the leader CLEAR of the bar, which
    a vertical bar's geometry demands (a line from its top to the axis would cross it)."""
    page, errs, close = _player("burst", FURNITURE)
    try:
        mid = _at(page, T_RUN0 + RUN * 0.45)
        assert not errs, errs
        assert mid["pillY"] > mid["base"], ("the capsule is ON THE AXIS, under it", mid["pillY"], mid["base"])
        assert mid["pillY"] - mid["base"] < 20, "and close to it - the pad, not a drift"
        assert 1.52 < float(mid["text"].rstrip("%")) < 36.59, "counting up during the shoot"
        lead = mid["lead"]
        assert lead["dash"] and " " in lead["dash"], "DOTTED: a solid rule across a chart is a comparator (E53 s6)"
        assert lead["op"] == 1
        assert lead["y1"] > mid["end"] and lead["y2"] < mid["pillY"], ("from the bar's end down to the capsule", lead, mid["end"])
        chips = mid["bars"][1]
        assert lead["x"] < chips["bx"] or lead["x"] > chips["bx"] + chips["bw"],             ("routed clear of the bar, not through it", lead["x"], chips["bx"], chips["bw"])
        assert mid["labY"] < mid["base"], "the capsule took the label's row: the bar's name is written above the zero line"
        end = _at(page, 10.0)
        assert end["text"] == "36.59%" and end["pillY"] == mid["pillY"], "the capsule does not move: the bar does"
        assert end["lead"]["y1"] > end["end"] and end["lead"]["y2"] == mid["lead"]["y2"]
    finally:
        close()


@needs_object
@needs_browser
def test_with_the_options_off_the_burst_is_exactly_what_e60_shipped():
    """The acceptance both slices stand on: a page that names no option renders the frame it always did.
    The same assertions the two E60 tests make, re-run on a player built through the new code path."""
    page, errs, close = _player("burst")
    try:
        p = _at(page, T_HOLD)
        assert p["track"] is None and p["stamp"] is None and p["lead"] is None and p["cad"] is None, "no furniture is built"
        assert p["mode"] == "burst" and p["comp"] == 1.52 and p["y1"] == 8
        bonds, chips = p["bars"]
        assert abs(chips["h"] - bonds["h"]) < 0.6 and p["text"] == "1.52%"
        assert p["pillY"] < p["base"], "the pill rides the tip, above the bar - the default is untouched"
        end = _at(page, 10.0)
        assert not errs, errs
        assert end["y1"] == 40 and end["hi1"] == 40 and end["text"] == "36.59%"
        assert abs(end["bars"][1]["h"] - end["plot"] * 36.59 / 40) < 0.6
        assert "drop-shadow" in end["bars"][1]["filter"]
    finally:
        close()


# ---- P50 T13: the stop-motion burst (R26-30, E60's blend) -----------------------------------------------


@needs_object
@needs_browser
def test_the_stepped_shoot_is_piecewise_constant_between_frames_and_monotone_across_them():
    """T13: the shoot, the counter, the rescale and the ticks' crossing read off ONE stepped clock, so they
    step together. The cadence is the one the burst's own speed asks for through stopaction's rule."""
    page, errs, close = _player("burst", {"break_cadence": "stop"})
    try:
        p0 = _at(page, T_RUN0)
        assert p0["cad"] == {"hold": 1, "fps": 24, "why": "359 px/s > 250: on 1s"}, p0["cad"]
        fps = 24
        poses, prev = [], None
        for f in range(0, 15):
            a = _at(page, T_RUN0 + f / fps)
            b = _at(page, T_RUN0 + (f + 0.25) / fps)
            assert (a["bars"][1]["h"], a["y1"], a["text"]) == (b["bars"][1]["h"], b["y1"], b["text"]), \
                f"frame {f} must HOLD: the bar, the scale and the counter step together"
            poses.append((a["bars"][1]["h"], a["y1"], a["text"]))
            if prev:
                assert a["bars"][1]["h"] >= prev[0] - 1e-9 and a["y1"] >= prev[1] - 1e-9, f"frame {f} went backwards"
            prev = poses[-1]
        assert not errs, errs
        assert len(set(poses)) >= 8, ("a shoot, not a cut", len(set(poses)))
        assert len(set(poses)) <= 15, "and a stepped one, not a continuum"
        land = _at(page, T_RUN0 + 15 / fps)
        assert "drop-shadow" in land["bars"][1]["filter"] and land["text"] == "36.59%", "the glow HITS on the landing step"
        assert "drop-shadow" not in _at(page, T_RUN0 + 14 / fps)["bars"][1]["filter"], "and on no step before it"
    finally:
        close()


@needs_object
@needs_browser
def test_the_stepped_burst_rests_on_the_continuous_one_s_frame():
    """T13's acceptance: the blend lands where the ruled default lands. Asserted on the DOM and on the
    RENDERED PNG - the two pages' frames at and after the settle hash the same."""
    import hashlib
    T_SETTLED = T_RUN0 + RUN + SETTLE
    states = {}
    for mode, opts in (("cont", None), ("stop", {"break_cadence": "stop"})):
        page, errs, close = _player("burst", opts)
        try:
            states[mode] = [_at(page, T_SETTLED + d) for d in (0.0, 0.2, 1.0)]
            states[mode + "_png"] = [hashlib.sha256(RB.frame_png(page, T_SETTLED + d, RB.STAGE["9:16"])).hexdigest()
                                     for d in (0.0, 0.2)]
            assert not errs, errs
        finally:
            close()
    for a, b in zip(states["cont"], states["stop"]):
        for k in ("bars", "y1", "hi1", "text", "pillY", "old", "neu"):
            assert a[k] == b[k], (k, a[k], b[k])
    assert states["cont_png"] == states["stop_png"], "the rendered frame at rest is the same frame, byte for byte"

ONSCREEN = """() => {
  const R = (el) => el.getBoundingClientRect().height;
  const emph = document.querySelector('.lp-chart rect.bar.emph'), plain = document.querySelector('.lp-chart rect.bar:not(.emph)');
  return { emph: emph ? R(emph) : null, plain: plain ? R(plain) : null };
}"""


@needs_object
@needs_browser
def test_mid_build_the_breaking_bar_rises_to_the_comparator_s_level():
    """R26-39 (the self-watch's first read, Tokyo 57.5 s): the breaking bar is laid out at its VALUE on the stated scale
    (36.59 on 0-8, taller than the plot) and the breakthrough paint rewrote it to the comparator's level only from the
    hold, so the build phase scaled the oversized rect - a tall bar that then snapped down. E60: it builds to the
    comparator's level WITH the others, holds, then shoots."""
    for mode in ("burst", "stack"):
        page, errs, close = _player(mode)
        try:
            p = _at(page, T_MID)
            assert not errs, errs
            bonds, chips = p["bars"]
            comp_h = p["plot"] * 1.52 / 8
            assert abs(chips["h"] - comp_h) < 0.6, ("the breaking bar's rest is the comparator's level during the build", mode, chips["h"], comp_h)
            on = page.evaluate(ONSCREEN)
            assert on["emph"] <= comp_h + 1.0, ("on screen it never rises past the comparator's level while building", mode, on)
            assert all(o == 1 for o in p["old"]) and all(o == 0 for o in p["neu"]), ("the stated scale is the visible one", mode, p["old"], p["neu"])
            assert p["text"] is not None and p["text"] != "36.59%", ("the pill counts toward the comparator, it does not print the number", mode, p["text"])
            q = _at(page, T_HOLD)
            assert abs(q["bars"][1]["h"] - q["bars"][0]["h"]) < 0.6, "and at the hold it stands level with the bonds, as before"
        finally:
            close()
