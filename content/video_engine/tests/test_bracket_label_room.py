"""P72 T43 (R26-219's bracket half, R26-338) - THE BRACKET'S LABEL ROOM, measured at 16:9.

  * R26-219: the Steel and Paper H unit's railway page (`ledger:ev-railway-index-v1:line:139:right`, full stage, 16:9)
    drew its peak-to-trough `bracket` at the plot's right edge, in the gutter that belongs to the terminal tags. The
    compiler now estimates the span and its label against the page's boxes (`ledger_page.page_boxes`) and WARNs by
    name with the numbers - the label's box, the room beside the span, the end tag the span stands on;
  * R26-338: a brace on a bar with neighbours (a three-bar stacked page, bar 0 or bar 1) found no clean side for its
    label and took the least-crowded one - over the neighbouring bar. The engine now sets the label ABOVE the bar when
    neither side is clean (its box clears every bar: overlap 0), and the compiler WARNs by name;
  * E99 s106: every finding is a WARN - the compiler never refuses a bracket for its room, and an authored `side`
    stands as written; a bracket or brace with a clean side renders byte-identically (the goldens pin it).

The browser rows need playwright + chromium and are skipped without them.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402
import build_golden_sources as G  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

RAIL_BRACKET = {"kind": "bracket", "at": 12.0, "dur": 1.6, "from": 53, "to": 139,   # the peak -> the trough (H row 9)
                "label": "−64%", "sub": "peak to trough"}
RAIL_BUILD = [dict(G.LIT_SPECIES[0]), dict(G.LIT_SPECIES[1])]   # the build to the peak, then the fall on "crashed"
BRACE_T = 16.33   # the brace golden's own judging instant: both part names written


def _rail_page() -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(G.LIT_PLATE, (0, 0, 0), G.LIT_PROJECT)
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    return world["page"]


def _bars3_page() -> dict:
    """The funding object's three stacked bars (Q1 2024 .. Q1 2026), the combo's line dropped - P70 T5's probe page."""
    s = G.stacked_funding_series()
    for k in ("series", "line_unit", "line_label"):
        s.pop(k, None)
    assert LPG.validate(s, "bars") == [], LPG.validate(s, "bars")
    return B.stamp_full_stage(LPG.build_spec(s, "bars", None, "right"))


def _brace(bar: int, **kw) -> dict:
    return dict(G.BRACE_SPECIES[0], bar=bar, **kw)


# ---- the compiler: the room estimate, a WARN by name (s106) -------------------------------------------------------------

def test_the_railway_span_is_measured_against_the_pages_boxes_and_warned_by_name():
    notes = B.check_brace(_rail_page(), RAIL_BUILD + [dict(RAIL_BRACKET)], "16:9")
    assert len(notes) == 1, notes
    (w,) = notes
    for part in ("R26-219", "bracket at 12.0", "'\\u221264%'", "end-tag column", "ABOVE the span", "REPORTED (E99 s106)"):
        assert part in w, (part, w)
    assert "series 0's end tag" in w and "741 RAILWAY SHARE PRICES" in w, ("the tag the span's foot stands on, named", w)
    assert w.isascii(), ("the words ascii-escaped: a build's log is cp1252 on Windows", w)
    assert "room beside" in w and " px" in w, ("the numbers: the label's box and the room", w)


def test_the_long_forms_railway_span_is_measured_on_its_own_wider_chart():
    page = _rail_page()
    LPG.apply_longform(page, "middle")   # the row's `;readability=longform`
    (w,) = B.check_brace(page, [dict(RAIL_BRACKET)], "16:9")
    assert "R26-219" in w and "end-tag column" in w and "ABOVE the span" in w, w


def test_a_span_with_room_beside_it_is_silent():
    inner = dict(RAIL_BRACKET, **{"from": 10, "to": 40})   # an inner stretch: the span stands in the plot, the label beside it
    assert B.check_brace(_rail_page(), [inner], "16:9") == []


def test_the_estimate_is_the_16x9_pages_and_a_portrait_page_is_not_estimated():
    assert B.check_brace(_rail_page(), [dict(RAIL_BRACKET)], "9:16") == []


@pytest.mark.parametrize("bar", [0, 1, 2])
def test_a_brace_with_no_clean_side_warns_with_the_room_and_names_the_above_fallback(bar):
    notes = B.check_brace(_bars3_page(), [_brace(bar)], "16:9")
    assert len(notes) == 1, notes
    (w,) = notes
    for part in ("R26-338", f"on bar {bar}", "'Cash from operations'", "no clean side", "ABOVE the bar",
                 "left", "right", "REPORTED (E99 s106)"):
        assert part in w, (part, w)


def test_the_last_bars_leader_figure_takes_its_right_side():
    (w,) = B.check_brace(_bars3_page(), [_brace(2)], "16:9")
    assert "leader" in w and "$9.5" in w, ("the thin top part's figure stands on a leader on the bar's right", w)


def test_a_brace_with_a_clean_side_is_silent():
    tl, _uris = G.brace_funding()
    page, species = tl["scenes"][0]["world"]["page"], tl["scenes"][0]["species"]
    assert B.check_brace(page, species, "16:9") == []


def test_an_authored_side_with_no_room_stands_and_is_reported():
    (w,) = B.check_brace(_bars3_page(), [_brace(1, side="left")], "16:9")
    assert "side 'left' is the author's" in w and "stands" in w and "ABOVE" not in w, w


def test_the_room_is_advice_never_a_refusal():
    page = _bars3_page()
    world = {"kind": "ledger", "page": page}
    B.derive_rescale_states(world, [_brace(0)], "ledger:fx-bars:bars", ROOT)   # no raise (s106)


def test_the_compiler_path_prints_the_warn(capsys):
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        B.derive_rescale_states({"kind": "ledger", "page": _bars3_page()}, [_brace(1)], "ledger:fx-bars:bars", ROOT)
    finally:
        B.ASPECT = saved
    out = capsys.readouterr().out
    assert "[WARN] P72 T43 (R26-338)" in out, out


# ---- the browser: the label above the bar, the clean page untouched ------------------------------------------------------

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { brackets: [] };
  const B = (el) => { if (!el) return null; const r = el.getBBox(); return [r.x, r.y, r.width, r.height]; };
  const S = (el) => { if (!el) return null; const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; };
  const bks = (PF.brackets || []).map(b => ({ brace: !!b.brace, side: b.side || null, above: !!b.above, fits: b.fits,
    path: B(b.main.line), label: B(b.main.label), sub: B(b.main.sub), labelScreen: S(b.main.label),
    anchor: b.main.label.getAttribute('text-anchor'), glow: B(b.glow.label),
    glyphs: b.main.lg.map(ts => +(ts.getAttribute('opacity') || 0)),
    names: (b.names || []).map(n => ({ j: n.j, box: B(n.el) })) }));
  const bars = (st.marks || []).filter(m => m.role === 'bar').map(m => m.geom);
  const vals = (st.bars || []).map(b => b.val ? B(b.val) : null);
  const figs = (st.segFigs || []).map(f => B(f.el));
  const title = st.titleEl ? S(st.titleEl) : null;
  return { bks, bars, vals, figs, title };
}"""


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _serve(page: dict, species: list, t: float) -> tuple[dict, list]:
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    tl = G._timeline("P72 T43: the bracket's label room", scenes, {}, "16:9")
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "room.html"
        html.write_text(RB.instantiate(tl, G._base_uris()), encoding="utf-8")
        w, h = RB.STAGE["16:9"]
        pg, errs, close = SP.open_served(html, w, h)
        try:
            pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
            return pg.evaluate(PROBE), errs
        finally:
            close()


def _meet(a, b) -> float:
    return max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


def _rect(g: dict) -> list[float]:
    return [g["x"], g["y"], g["w"], g["h"]]


@needs_browser
@pytest.mark.parametrize("bar", [0, 1])
def test_a_brace_on_bar_0_or_1_sets_its_label_above_the_bar_clear_of_every_bar(bar):
    s, errs = _serve(_bars3_page(), [_brace(bar)], BRACE_T)
    assert not errs, errs
    (bk,) = s["bks"]
    assert bk["brace"] and bk["above"], ("neither side is clean: the label goes above", bk)
    for other in s["bars"]:
        assert _meet(bk["label"], _rect(other)) == 0, ("overlap 0 with every bar", bk["label"], other)
    for box in [v for v in s["vals"] if v] + [f for f in s["figs"] if f]:
        assert _meet(bk["label"], box) == 0, ("the label meets no value or part figure", bk["label"], box)
    own = s["bars"][bar]
    assert bk["label"][1] + bk["label"][3] <= s["vals"][bar][1] + 0.5, ("above the bar's own value", bk["label"], s["vals"][bar])
    cx = bk["label"][0] + bk["label"][2] / 2
    assert abs(cx - (own["x"] + own["w"] / 2)) < 1.0 and bk["anchor"] == "middle", ("centred over its bar", cx, own)
    assert bk["label"][1] >= 0, ("inside the chart's top: never into the title band", bk["label"])
    assert bk["glow"] == bk["label"], "the relight's twin stands where the label stands"
    assert all(g == 1 for g in bk["glyphs"]), "written on the bracket's clock, as before"
    for n in bk["names"]:
        for other in s["bars"]:
            assert _meet(n["box"], _rect(other)) == 0, ("a part's name stays beside its bar", n, other)
    assert s["title"] and _meet(bk["labelScreen"], s["title"]) == 0, ("the title stands clear", bk["labelScreen"], s["title"])


@needs_browser
def test_an_authored_side_stands_as_written():
    s, errs = _serve(_bars3_page(), [_brace(1, side="left")], BRACE_T)
    assert not errs, errs
    (bk,) = s["bks"]
    assert bk["side"] == "left" and not bk["above"], ("s106: the author's side is taken as written", bk)


@needs_browser
def test_the_one_bar_golden_keeps_its_clean_side():
    tl, uris = G.brace_funding()
    page, species = tl["scenes"][0]["world"]["page"], tl["scenes"][0]["species"]
    s, errs = _serve(page, species, BRACE_T)
    assert not errs, errs
    (bk,) = s["bks"]
    assert bk["side"] == "left" and bk["fits"] and not bk["above"], bk


@needs_browser
def test_the_railway_brackets_label_is_written_in_free_ground():
    """The span's label on the railway page (fits False: no room beside it) is written above the span, clear of the
    title - the WARN names the span's foot on the end tag; the label itself meets nothing."""
    s, errs = _serve(_rail_page(), RAIL_BUILD + [dict(RAIL_BRACKET)], 14.5)
    assert not errs, errs
    (bk,) = s["bks"]
    assert not bk["brace"] and bk["fits"] is False and all(g == 1 for g in bk["glyphs"]), bk
    assert _meet(bk["labelScreen"], s["title"]) == 0, (bk["labelScreen"], s["title"])
