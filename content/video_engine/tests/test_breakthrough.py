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
  const bars = st.bars.map(b => ({ i: b.i, over: !!b.over, h: b.h, end: b.end, y: Number(b.bar.getAttribute('y')),
                                   snap: b.snap ? Number(b.snap[0].getAttribute('opacity')) : null, filter: b.bar.style.filter || "" }));
  const B = st.bt || null;
  const pill = st.cpill || (st.callout ? st.callout.querySelector('.cpill') : null);
  return { bars, base: st.bt ? st.bt.base : null, top: st.bt ? st.bt.top : null, plot: st.bt ? st.bt.plot : null,
           y1: st.scale.y1, y0: st.scale.y0, mode: B && B.mode, comp: B && B.comp, hi1: B && B.hi1,
           old: B ? B.ticks0.filter((e, j) => (j & 1) === 1 && B.vals0[j >> 1] !== 0).map(e => Number(e.getAttribute('opacity') ?? 1)) : [],
           neu: B ? B.ticks1.map(e => Number(e.getAttribute('opacity'))) : [],
           text: st.cval ? st.cval.textContent : null, pillY: pill ? Number(pill.getAttribute('y')) : null,
           pillW: pill ? Number(pill.getAttribute('width')) : null, textW: st.cval ? st.cval.getComputedTextLength() : null };
}"""


def _player(mode: str):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    world = json.loads(json.dumps(world)); world["page"]["axes"]["overflow"] = mode
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
