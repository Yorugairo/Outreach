"""The BREAKTHROUGH bars (Bravos, 2026-09-10; the operator: "show the average bond market return over the last 10 yrs with the
average return of SOXX as the breakthrough").

A bars page may STATE its scale (`domain`) and let a value past it break through the top (`overflow: "break"`): the bar runs
BREAK (0.12 of the plot) past the top gridline, a break glyph cuts it there, its value stands above. The scale is printed and
the value is printed, so the height is not a lie (E28); the drama is the frame that could not hold the number. A page that
declares neither is byte-identical to what it was (the goldens hold that).
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
BREAK_SHARE = 0.12   # of the plot's height [DERIVED: Bravos 50-55, the bar that runs out]

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
                            "domain": [0, 8], "overflow": "break"}).get("axes")
    assert axes == {"overflow": "break", "domain": [0, 8]}, "the scale and the break ride the page's axes"


def test_a_bars_page_without_a_domain_carries_no_axes():
    assert "axes" not in LP._story_block({"bars": [{"label": "a", "value": 1.5}]}), "a page that declares nothing is unchanged"


@needs_object
def test_the_object_states_its_scale_and_its_figures_are_the_sourced_ones():
    obj = json.loads(OBJ.read_text(encoding="utf-8"))
    assert obj["domain"] == [0, 8] and obj["overflow"] == "break"
    vals = {b["label"]: b["value"] for b in obj["bars"]}
    assert vals == {"Bonds": 1.52, "Chips": 36.59}, "iShares AGG / SOXX ten-year average annual total return (NAV)"
    assert "ishares-soxx-agg-returns-2026-09-10" in obj["src_full"], "the source on disk is named on the page"


# ---- the page ----------------------------------------------------------------------------------------


PROBE = """() => {
  const st = document.querySelector('.world')?.__lp || window.wA?.__lp || window.wB?.__lp;
  const rect = (el) => { const r = el.getBBox(); return {x: r.x, y: r.y, w: r.width, h: r.height}; };
  const bars = st.bars.map(b => ({ i: b.i, over: !!b.over, h: b.h, end: b.end, brk: !!b.brk,
                                   brkOn: b.brk ? Number(b.brk.getAttribute('opacity')) : null }));
  const pill = st.callout ? st.callout.querySelector('.cpill') : null;
  const cval = st.cval;
  return { bars, base: st.scale.my(0), top: st.scale.my(st.scale.y1), y1: st.scale.y1, y0: st.scale.y0,
           pillW: pill ? Number(pill.getAttribute('width')) : null,
           textW: cval ? cval.getComputedTextLength() : null, final: st.cfinal };
}"""


def _player():
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(PLATE, (0, 0, 0), EP)
    scene = dict(tl["scenes"][0], species=[], span=[0.0, 16.0], world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=16.0, scenes=[scene], caption_pages=[], captions=[])
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
def test_the_chips_bar_breaks_through_the_stated_scale_and_the_bonds_bar_reads_on_it():
    page, errs, close = _player()
    try:
        p = _at(page, 12.0)
        assert not errs, errs
        assert p["y0"] == 0 and p["y1"] == 8, "the page's scale is the stated one, 0-8 %, not the data's"
        plot = p["base"] - p["top"]
        bonds, chips = p["bars"]
        assert not bonds["over"] and chips["over"]
        assert bonds["h"] == pytest.approx(plot * 1.52 / 8, abs=0.6), "the bonds bar is honest on the stated scale"
        assert chips["h"] == pytest.approx(plot + BREAK_SHARE * plot, abs=0.6), "the chips bar runs BREAK past the top gridline"
        assert chips["end"] < p["top"] - 1, "its end stands above the plot"
        assert chips["brk"] and chips["brkOn"] == 1, "the break glyph cuts the built bar"
        assert not bonds["brk"]
        # the value stands above the break and its pill fits the whole number
        assert p["final"] == "36.59%"
        assert p["pillW"] >= p["textW"] + 20, (p["pillW"], p["textW"])
    finally:
        close()


@needs_object
@needs_browser
def test_the_break_glyph_waits_until_the_bar_has_run_past_the_top():
    page, errs, close = _player()
    try:
        early = _at(page, 4.6)   # the bars have begun to grow but the chips bar has not run out yet
        chips = early["bars"][1]
        assert chips["brk"] and chips["brkOn"] == 0, "the glyph is on the page but not yet shown"
        assert not errs, errs
    finally:
        close()
