"""P70 T5 (was P69 T58; harvest v2 T24, v1 #63) - THE DECOMPOSITION BRACE: one total braced into its named parts.

Bravos RST 05:40 braces "Long-Term Interest Rates" into its two stacked components (short-term rate + term premium).
Ours braces a STACKED BAR (P69 T64's `segments`): `bracket {form: "brace", bar, at, dur, label, sub?, parts_at?, side?}`.

  * a curly brace stands beside the bar's side from zero to its top, its cusp toward the label (the whole's name);
    the curve is GENERATED geometry, so it is clothoid segments (doc 42 s42.4), never a cubic Bezier;
  * one notch at each segment boundary;
  * each part's NAME is written beside its own segment's span on its word (`parts_at`, else 0.4 s apart after the
    brace), in its segment's ink (E99 s118); the part FIGURES stay the segments' own and are never re-written;
  * a part named beside its own span hands its key entry over - the two would say it twice. The brace RECORDS how far
    each name is written (`st.keyHandoff`); lpSegPaint, the key's one painter, fades the entry (E99 s129 retired the
    plot-word limit: the count is INFO, the double statement is the reason);
  * truth (hard, E99 s109): a figure in `label` must be the bar's written total; a brace on a bar with no segments is
    refused by name, and a brace given `from` / `to` is pointed at the span form;
  * it follows the page's park as a bracket does (R26-28), on the bracket's clock (BRACKET_DRAW, the spring, the glyph
    write). A bracket without `form: "brace"` is byte-identical (the goldens `tiers-two`, `span-decade` pin it).

The browser rows need playwright + chromium and are skipped without them.
"""
from __future__ import annotations

import copy
import json
import re
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

STILL = (0, 0, 0)
PLATE = "ledger:fx-bars:bars"
PHONE_FLOOR_PX = 12 * 1920 / 390   # E99 s90: 59.08 stage px (test_longform_profile.PHONE_FLOOR / PHONE_W)
BRACE = {"kind": "bracket", "form": "brace", "at": 8.0, "dur": 1.6, "bar": 0, "label": "Cash from operations"}


def _errs(sp: dict) -> list[str]:
    return B.validate_species([sp], STILL, PLATE)


def _page(nbars: int = 1) -> dict:
    """The golden's page (T64's stacked funding object, the line dropped) - the last `nbars` bars."""
    s = G.brace_funding_series() if nbars == 1 else copy.deepcopy(G.stacked_funding_series())
    for k in ("series", "line_unit", "line_label"):
        s.pop(k, None)
    s["bars"] = s["bars"][-nbars:]
    assert LPG.validate(s, "bars") == [], LPG.validate(s, "bars")
    return B.stamp_full_stage(LPG.build_spec(s, "bars", None, "right"))


# ---- the grammar: a brace names ONE bar, not two data ------------------------------------------------------------------

def test_a_brace_entry_is_accepted_by_the_grammar():
    """The base refused it twice over: 'from'/'to' must be datum indices, and form must be span|bar."""
    assert _errs(BRACE) == []
    assert "brace" in B.BRACKET_FORMS


def test_a_brace_given_from_or_to_is_refused_and_points_to_the_span_form():
    for extra in ({"from": 0}, {"to": 1}, {"from": 0, "to": 1}):
        errs = _errs(dict(BRACE, **extra))
        assert len(errs) == 1 and "span" in errs[0] and "`bar`" in errs[0], errs


def test_a_brace_needs_the_bar_it_divides():
    for bad in (None, -1, 1.5, True, "0"):
        sp = dict(BRACE, bar=bad) if bad is not None else {k: v for k, v in BRACE.items() if k != "bar"}
        errs = _errs(sp)
        assert any("'bar'" in e for e in errs), (bad, errs)


def test_parts_at_is_a_list_of_times_at_or_after_the_brace():
    assert _errs(dict(BRACE, parts_at=[9.0, 10.5])) == []
    assert any("parts_at" in e for e in _errs(dict(BRACE, parts_at=9.0)))
    assert any("parts_at" in e for e in _errs(dict(BRACE, parts_at=[9.0, "10"])))
    assert any("parts_at" in e and "after" in e for e in _errs(dict(BRACE, parts_at=[7.0, 9.0])))


def test_the_side_is_the_authors_left_or_right():
    assert _errs(dict(BRACE, side="left")) == [] and _errs(dict(BRACE, side="right")) == []
    assert any("side" in e for e in _errs(dict(BRACE, side="top")))


def test_the_braces_own_keys_on_a_span_bracket_are_refused_not_dropped():
    span = {"kind": "bracket", "at": 8.0, "dur": 1.6, "from": 0, "to": 1, "label": "3x"}
    assert _errs(span) == []
    for k, v in (("bar", 0), ("parts_at", [9.0]), ("side", "left")):
        errs = _errs(dict(span, **{k: v}))
        assert len(errs) == 1 and k in errs[0] and "brace" in errs[0], (k, errs)


def test_the_label_and_the_sub_stay_the_brackets():
    assert any("label" in e for e in _errs(dict(BRACE, label="")))
    assert any("sub" in e for e in _errs(dict(BRACE, sub=3)))


# ---- the page's truth: check_brace --------------------------------------------------------------------------------------

def test_a_brace_on_a_bar_with_no_segments_is_refused_by_name():
    page = B.stamp_full_stage(LPG.build_spec({"title": "t", "src": "s", "unit": "$",
                                              "bars": [{"label": "a", "value": 4.0}, {"label": "b", "value": 6.0}]},
                                             "bars", None, "right"))
    with pytest.raises(ValueError, match=r"a brace divides a whole into its parts.*T64's `segments`"):
        B.check_brace(page, [dict(BRACE, bar=1)])


def test_a_label_figure_must_be_the_bars_written_total():
    page = _page()
    B.check_brace(page, [dict(BRACE, label="Cash from operations")])      # no figure: nothing to be untrue
    B.check_brace(page, [dict(BRACE, label="$157.9bn from operations")])  # the written total
    B.check_brace(page, [dict(BRACE, label="$158bn of cash")])            # ... at the label's own precision
    B.check_brace(page, [dict(BRACE, label="Q1 cash from operations")])   # a digit inside a word is a name, not a figure
    with pytest.raises(ValueError, match=r"untrue"):
        B.check_brace(page, [dict(BRACE, label="$148.4bn of cash")])       # a part's figure, not the whole
    with pytest.raises(ValueError, match=r"157\.9"):
        B.check_brace(page, [dict(BRACE, label="$160bn of cash")])


def test_a_brace_names_a_bar_the_page_has():
    with pytest.raises(ValueError, match=r"bar 3 is not a bar of this page"):
        B.check_brace(_page(), [dict(BRACE, bar=3)])


def test_parts_at_names_one_time_per_part():
    B.check_brace(_page(), [dict(BRACE, parts_at=[9.0, 10.0])])
    with pytest.raises(ValueError, match=r"parts_at names 3 time\(s\) for 2 part"):
        B.check_brace(_page(), [dict(BRACE, parts_at=[9.0, 10.0, 11.0])])


def test_a_brace_off_a_bars_page_is_refused():
    line = B.stamp_full_stage(LPG.build_spec({"title": "t", "src": "s", "unit": "%",
                                              "series": [{"name": "y", "pts": [[2000 + i, i] for i in range(6)]}]},
                                             "line", None, "right"))
    with pytest.raises(ValueError, match=r"a brace stands on a bars page"):
        B.check_brace(line, [BRACE])
    with pytest.raises(ValueError, match=r"a brace stands on a bars page"):
        B.check_brace(None, [BRACE])


def test_a_brace_on_the_stacked_combo_is_refused_by_name():
    combo = B.stamp_full_stage(LPG.build_spec(G.stacked_funding_series(), "bars", None, "right"))
    assert combo["builder"] == "combo"
    with pytest.raises(ValueError, match=r"the combo's stacks"):
        B.check_brace(combo, [dict(BRACE, bar=2)])


def test_a_page_with_no_brace_is_untouched():
    B.check_brace(None, [{"kind": "bracket", "at": 1.0, "dur": 1.0, "from": 0, "to": 1, "label": "x"}])
    B.check_brace(_page(), [])


def test_the_compiler_path_runs_the_brace_check():
    world = {"kind": "ledger", "page": _page()}
    with pytest.raises(ValueError, match=r"untrue"):
        B.derive_rescale_states(world, [dict(BRACE, label="$99 of cash")], PLATE, ROOT)


# ---- the record: the golden and the card --------------------------------------------------------------------------------

def test_the_golden_is_read_from_the_committed_object_and_listed():
    s = G.brace_funding_series()
    whole = G.stacked_funding_series()["bars"][-1]
    assert s["bars"] == [whole], "the Q1 2026 bar exactly as T64's golden reads it, never re-typed"
    assert "series" not in s, "a bars page: the combo's line is not this beat's"
    assert "brace-funding" in G.SURFACES and "brace-funding" in G.FRAME_T
    src = (ROOT / "content/video_engine/tests/test_golden_frames.py").read_text(encoding="utf-8")
    assert '"brace-funding"' in src
    for suffix in ("timeline", "uris"):
        assert (RB.SOURCES / f"brace-funding.{suffix}.json").exists(), suffix
    assert (RB.FRAMES / "brace-funding.png").exists()
    sp = [x for x in G.BRACE_SPECIES if x.get("form") == "brace"]
    assert len(sp) == 1 and sp[0]["parts_at"] == sorted(sp[0]["parts_at"], reverse=True), \
        "Left over (the top part) is named first, on 'investing its surplus'; Cash capex on 'spending all of it'"


def test_the_bracket_card_carries_the_brace_option():
    cards = json.loads((ROOT / "content/video_engine/effects/cards/page_species.json").read_text(encoding="utf-8"))["cards"]
    card = next(c for c in cards if c["id"] == "page_species:bracket")
    tokens = [o["token"] for o in card["options"]]
    assert "brace" in tokens, tokens
    assert "brace" in card["does"]


# ---- the browser: the brace as drawn -------------------------------------------------------------------------------------

PROBE = """() => {
  const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')); if (!w) return null;
  const st = w.__lp, PF = st.perform || { brackets: [] };
  const B = (el) => { const r = el.getBBox(); return [r.x, r.y, r.width, r.height]; };
  const op = (el) => +(el.getAttribute('opacity') == null ? 1 : el.getAttribute('opacity'));
  const braces = (PF.brackets || []).filter(b => b.brace).map(b => ({
    side: b.side, cusp: b.cusp, ends: b.ends, R: b.R, d: b.main.line.getAttribute('d'), len: b.main.len,
    offset: +(b.main.line.getAttribute('stroke-dashoffset') || 0), opacity: op(b.main.g), path: B(b.main.line),
    label: B(b.main.label), labelText: b.main.label.textContent.replace(/\\u00a0/g, ' '), labelFs: parseFloat(b.main.label.style.fontSize),
    labelAnchor: b.main.label.getAttribute('text-anchor'),
    glyphs: b.main.lg.map(ts => op(ts)),
    notches: b.notches.map(n => ({ y: n.y, x: n.x, box: B(n.el), tf: n.el.getAttribute('transform') || '' })),
    names: b.names.map(n => ({ j: n.j, text: n.el.textContent.replace(/\\u00a0/g, ' '), box: B(n.el), fill: n.el.style.fill, fs: parseFloat(n.el.style.fontSize),
                              glyphs: n.glyphs.map(g => op(g)), at: n.at, ink: n.ink })) }));
  const bars = (st.marks || []).filter(m => m.role === 'bar').map(m => m.geom);
  const segs = (st.bars || []).map(b => (b.segs || []).map(s => ({ name: s.name, y0: s.y0, y1: s.y1, color: s.color })));
  const figs = (st.segFigs || []).map(f => ({ bar: f.bar, j: f.j, inside: f.inside, text: f.el.textContent, box: B(f.el) }));
  const vals = (st.bars || []).map(b => b.val ? B(b.val) : null).filter(Boolean);
  const K = st.segKey;
  const key = K ? { attr: op(K), entries: [...K.querySelectorAll('text.lp-seg-name')].map(tx => { const sw = tx.previousElementSibling;
    return { name: tx.textContent, op: op(tx), swOp: sw ? op(sw) : null, style: tx.getAttribute('style') || '',
             swStyle: sw ? (sw.getAttribute('style') || '') : null }; }) } : null;
  const m = st.chart.getScreenCTM();
  const chartBox = st.chart.getBoundingClientRect();
  /* s120 (3): the words on the plot - every visible, mostly-written text run of the chart and its perform layer */
  const eff = (el) => { let o = 1, e = el; while (e && e !== w) { const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0; o *= parseFloat(cs.opacity);
      const a = e.getAttribute && e.getAttribute('opacity'); if (a != null && a !== '') o *= parseFloat(a) || 0;
      e = e.parentNode instanceof Element ? e.parentNode : null; } return o; };
  const words = [];
  for (const root of [st.chart, st.performSvg].filter(Boolean)) for (const t of root.querySelectorAll('text')) {
    if (eff(t) <= 0.05) continue;
    const ts = [...t.querySelectorAll('tspan')];
    if (ts.length && ts.filter(g => op(g) > 0.5).length / ts.length <= 0.5) continue;
    words.push(t.textContent.replace(/\\u00a0/g, ' '));
  }
  return { braces, bars, segs, figs, vals, key, words, k: m ? m.a : 0, W: (st.geom || {}).W, H: (st.geom || {}).H,
           chartScreen: [chartBox.x, chartBox.y], errs: 0 };
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


class Served:
    def __init__(self, timeline: dict, uris: dict, aspect: str = "16:9"):
        self._td = tempfile.TemporaryDirectory()
        html = Path(self._td.name) / "brace.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        self.w, self.h = RB.STAGE[aspect]
        self.page, self.errs, self._close = SP.open_served(html, self.w, self.h, cleanup=self._td.cleanup)   # R26-351: guarded

    def at(self, t: float) -> dict:
        self.page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return self.page.evaluate(PROBE)

    def close(self) -> None:
        self._close()


def _meets(a: list[float], b: list[float], pad: float = 0.0) -> bool:
    return a[0] - pad < b[0] + b[2] and b[0] < a[0] + a[2] + pad and a[1] - pad < b[1] + b[3] and b[1] < a[1] + a[3] + pad


def _said_twice(texts, names) -> list[str]:
    """The part names written more than once among the plot's visible words (a key entry beside its own name)."""
    return [n for n in names if sum(1 for x in texts if str(x).strip() == n) > 1]


# the rows that serve their OWN timeline run first: a sync playwright may not start inside the module fixture's loop
@needs_browser
def test_the_brace_follows_the_park():
    park = {"kind": "chart_to", "to": "park", "at": 17.0, "dur": 0.8, "scale": 0.7}
    tl, uris = G.brace_funding(extra=[park])
    P = Served(tl, uris)
    try:
        still = P.at(16.9)
        moved = P.at(18.5)
        assert not P.errs, P.errs
        assert still["braces"][0]["path"] == moved["braces"][0]["path"], "drawn in the chart's own units ..."
        assert abs(still["k"] - moved["k"]) > 0.05, "... and the chart itself moved: the brace rides it (R26-28)"
    finally:
        P.close()


@needs_browser
def test_in_the_long_form_the_brace_writes_at_the_pages_tag_size_and_the_phone_preset_clears_the_floor():
    for preset, floor in (("middle", None), ("phone", PHONE_FLOOR_PX)):
        tl, uris = G.brace_funding(longform=preset)
        P = Served(tl, uris)
        try:
            s = P.at(G.FRAME_T["brace-funding"])
        finally:
            P.close()
        (bk,) = s["braces"]
        sizes = [bk["labelFs"]] + [n["fs"] for n in bk["names"]]
        assert len(set(round(x, 3) for x in sizes)) == 1, ("the label and the names are one role", sizes)
        tag = LPG.longform_type({"axes": {"type_scale": preset}})["tag"]
        assert sizes[0] * s["k"] == pytest.approx(tag, abs=0.05), ("a PEER of the end tag, the page's own role", sizes, s["k"], tag)
        if floor:
            assert sizes[0] * s["k"] >= floor - 0.01, (preset, sizes[0] * s["k"], floor)


@needs_browser
def test_two_braces_naming_one_key_entry_hand_it_over_whichever_paints_last():
    """The key's entry for a part is handed to the MOST written of the names that name it: a later brace whose names
    have not begun does not bring the entry back over an earlier brace's written name (a pure function of t)."""
    page = _page(3)
    species = [dict(BRACE, bar=0, at=8.0, parts_at=[9.0, 9.5]), dict(BRACE, bar=2, at=18.0, parts_at=[19.0, 19.5])]
    B.check_brace(page, species)
    world = {"kind": "ledger", "page": page, "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    scenes = [{"scene_id": "s01", "world": world, "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    P = Served(G._timeline("P70 T5: two braces, one key", scenes, {}, "16:9"), G._base_uris())
    try:
        s = P.at(12.0)
    finally:
        P.close()
    assert not P.errs, P.errs
    assert len(s["braces"]) == 2
    assert all(e["op"] == 0 and e["swOp"] == 0 for e in s["key"]["entries"]), ("the first brace named both parts", s["key"])


@pytest.fixture(scope="module")
def golden():
    tl, uris = G.brace_funding()
    P = Served(tl, uris)
    yield P
    P.close()


@needs_browser
def test_the_brace_stands_beside_the_bar_from_zero_to_its_top_with_a_notch_at_each_boundary(golden):
    s = golden.at(G.FRAME_T["brace-funding"])
    assert not golden.errs, golden.errs
    (bk,) = s["braces"]
    (bar,) = s["bars"]
    top, base = bar["end"], bar["base"]
    px, py, pw, ph = bk["path"]
    assert abs(py - top) < 1.0 and abs(py + ph - base) < 1.0, ("from zero to the bar's top", bk["path"], top, base)
    rect = [bar["x"], bar["y"], bar["w"], bar["h"]]
    assert not _meets(bk["path"], rect), ("beside the bar's side, never on its ink", bk["path"], rect)
    side = bk["side"]
    assert side in ("left", "right")
    if side == "left":
        assert px + pw < bar["x"] and bk["cusp"][0] == pytest.approx(px, abs=0.6), "the cusp points away from the bar"
        assert bk["labelAnchor"] == "end" and bk["label"][0] + bk["label"][2] < bk["cusp"][0], "the label beyond the cusp"
    else:
        assert px > bar["x"] + bar["w"] and bk["cusp"][0] == pytest.approx(px + pw, abs=0.6)
        assert bk["labelAnchor"] == "start" and bk["label"][0] > bk["cusp"][0]
    ly = bk["label"][1] + bk["label"][3] / 2
    assert abs(ly - bk["cusp"][1]) < bk["labelFs"], ("the label stands at the cusp", ly, bk["cusp"])
    assert abs(bk["cusp"][1] - (top + base) / 2) < 1.0, "the cusp at the whole's middle"
    (segs,) = s["segs"]
    bounds = [sg["y1"] for sg in segs[:-1]]   # the boundary between part j and j+1 is part j's top
    assert len(bk["notches"]) == len(segs) - 1
    for n, yb in zip(bk["notches"], bounds):
        assert abs(n["y"] - yb) < 1e-6, (n, yb)
        nb = n["box"]
        assert nb[1] - 1 <= yb <= nb[1] + nb[3] + 1, ("the notch stands at its boundary", nb, yb)
    assert bk["opacity"] == 1 and bk["offset"] < 0.5 and all(g == 1 for g in bk["glyphs"]), "drawn whole, labelled"


@needs_browser
def test_the_curve_is_clothoid_samples_never_a_cubic(golden):
    (bk,) = golden.at(G.FRAME_T["brace-funding"])["braces"]
    cmds = set(re.findall(r"[A-Za-z]", bk["d"]))
    assert cmds <= {"M", "L"}, ("doc 42 s42.4: generated geometry is clothoid samples drawn as a polyline", cmds)
    assert bk["d"].count("L") >= 4 * 12, "four curls of samples, not four straight strokes"


@needs_browser
def test_each_part_is_named_beside_its_own_span_on_its_word_in_its_ink(golden):
    sp = next(x for x in G.BRACE_SPECIES if x.get("form") == "brace")
    first, second = sorted(sp["parts_at"])
    early = golden.at(first - 0.05)
    (bk,) = early["braces"]
    assert all(all(g == 0 for g in n["glyphs"]) for n in bk["names"]), "no part is named before its word"
    mid = golden.at(first + 0.8)
    named = {n["j"]: all(g == 1 for g in n["glyphs"]) for n in mid["braces"][0]["names"]}
    assert sum(named.values()) == 1, ("one part named on the first word", named)
    s = golden.at(second + 0.8)
    (bk,), (segs,) = s["braces"], s["segs"]
    assert [n["text"] for n in sorted(bk["names"], key=lambda n: n["j"])] == [sg["name"] for sg in segs]
    for n in bk["names"]:
        assert all(g == 1 for g in n["glyphs"]), n
        sg = segs[n["j"]]
        assert n["at"] == pytest.approx(sp["parts_at"][n["j"]]), "parts_at is per part, bottom-up"
        assert n["ink"] == sg["color"] and n["fill"], ("E99 s118: the name wears its part's ink", n, sg)
        cy = n["box"][1] + n["box"][3] / 2
        fig = next((f for f in s["figs"] if f["j"] == n["j"] and not f["inside"]), None)
        lo, hi = min(sg["y0"], sg["y1"]), max(sg["y0"], sg["y1"])
        near = fig["box"][1] + fig["box"][3] / 2 if fig else None
        assert lo - 1 <= cy <= hi + 1 or (near is not None and abs(cy - near) < n["fs"] * 0.6), \
            ("beside its own span (or its own figure's leader)", n, sg, fig)
    bar = s["bars"][0]
    for n in bk["names"]:
        if bk["side"] == "left":
            assert n["box"][0] > bar["x"] + bar["w"], "the parts are named on the bar's other side (Bravos RST 05:40)"
        else:
            assert n["box"][0] + n["box"][2] < bar["x"]


@needs_browser
def test_the_part_figures_stay_the_segments_own(golden, tmp_path):
    before = golden.at(7.9)["figs"]
    after = golden.at(G.FRAME_T["brace-funding"])["figs"]
    assert [f["text"] for f in before] == [f["text"] for f in after] and len(after) == 2
    (bk,) = golden.at(G.FRAME_T["brace-funding"])["braces"]
    written = [bk["labelText"]] + [n["text"] for n in bk["names"]]
    assert not any(re.search(r"\d", w) for w in written[1:]), ("a name is a name, never the part's figure again", written)


@needs_browser
def test_the_brace_draws_on_the_brackets_clock(golden):
    sp = next(x for x in G.BRACE_SPECIES if x.get("form") == "brace")
    at, dur = sp["at"], sp["dur"]
    (b0,) = golden.at(at - 0.2)["braces"]
    assert b0["opacity"] == 0, "not on the page before its word"
    drawing = [golden.at(at + k * dur)["braces"][0] for k in (0.01, 0.03, 0.08, 0.2, 0.4)]
    offs = [b["offset"] for b in drawing]
    assert offs == sorted(offs, reverse=True) and any(0.05 * b["len"] < b["offset"] < 0.95 * b["len"] for b in drawing), \
        ("the hand draws it over BRACKET_DRAW (0.5 of dur), end to end", offs, drawing[0]["len"])
    for b1 in drawing:
        assert all(n["tf"] in ("scale(0 1)", "scale(0.0000 1)") for n in b1["notches"]), ("the notches wait", b1["notches"])
        assert all(g == 0 for g in b1["glyphs"]), "the label waits for BRACKET_LABEL"
    (b2,) = golden.at(at + 0.52 * dur)["braces"]
    assert b2["offset"] < 0.5, "drawn whole at BRACKET_DRAW"
    (b3,) = golden.at(at + dur)["braces"]
    assert all(g == 1 for g in b3["glyphs"]) and all("scale(1" in n["tf"] for n in b3["notches"])


@needs_browser
def test_nothing_the_brace_writes_meets_a_bar_a_figure_a_value_or_another_word(golden):
    s = golden.at(G.FRAME_T["brace-funding"])
    (bk,) = s["braces"]
    boxes = [("label", bk["label"])] + [(n["text"], n["box"]) for n in bk["names"]]
    ink = [[b["x"], b["y"], b["w"], b["h"]] for b in s["bars"]] + [f["box"] for f in s["figs"]] + s["vals"]
    for name, box in boxes:
        for o in ink:
            assert not _meets(box, o), (name, box, o)
        assert not _meets(box, bk["path"]), (name, "on the brace", box, bk["path"])
    for i, (a, ab) in enumerate(boxes):
        for c, cb in boxes[i + 1:]:
            assert not _meets(ab, cb), (a, c)


@needs_browser
def test_the_key_yields_each_part_to_its_name_so_no_part_is_named_twice(golden):
    sp = next(x for x in G.BRACE_SPECIES if x.get("form") == "brace")
    first, second = sorted(sp["parts_at"])
    j_first = sp["parts_at"].index(first)
    names = [s["name"] for s in G.brace_funding_series()["bars"][0]["segments"]]
    before = golden.at(sp["at"] - 0.2)
    assert [e["name"] for e in before["key"]["entries"]] == names and before["key"]["attr"] > 0.9
    assert all(e["op"] == 1 and e["swOp"] == 1 for e in before["key"]["entries"]), "the key names the parts until the brace does"
    mid = golden.at(first + 0.8)
    ops = {e["name"]: (e["op"], e["swOp"]) for e in mid["key"]["entries"]}
    assert ops[names[j_first]] == (0, 0) and ops[names[1 - j_first]] == (1, 1), ("a part's entry yields to ITS name", ops)
    half = golden.at(first + 0.3)
    assert 0 < {e["name"]: e["op"] for e in half["key"]["entries"]}[names[j_first]] < 1, "it fades while the name writes"
    after = golden.at(G.FRAME_T["brace-funding"])
    assert all(e["op"] == 0 and e["swOp"] == 0 for e in after["key"]["entries"]), \
        "each part named beside its own span: its key entry would say it twice"
    for t in (sp["at"] - 0.2, sp["at"] + sp["dur"], first + 0.3, first + 0.8, second + 0.3, G.FRAME_T["brace-funding"]):
        s = golden.at(t)
        assert not _said_twice(s["words"], names), (t, s["words"])


@needs_browser
def test_nothing_but_the_keys_painter_writes_on_the_key(golden):
    """The parent's ruling (2026-09-25): one element, one painter. Over the whole beat - played forward, then scrubbed
    back - no `style` is written on the key or anything in it (lpSegPaint writes the entries' opacity ATTRIBUTE; the
    key was laid at build), and every entry's opacity follows the hand-off."""
    golden.at(7.0)
    golden.page.evaluate("""() => { const w = [wB, wA].find(e => e.__lp && e.classList.contains('ledger')), K = w.__lp.segKey;
      window.__keyStyleWrites = []; window.__keyObs = new MutationObserver((ms) => { for (const m of ms)
        window.__keyStyleWrites.push((m.target.getAttribute('class') || m.target.tagName) + ' ' + m.attributeName); });
      window.__keyObs.observe(K, { subtree: true, attributes: true, attributeFilter: ['style', 'class', 'visibility', 'filter'] }); }""")
    for k in range(0, 41):
        golden.at(7.0 + 0.25 * k)
    for t in (15.5, 13.3, 9.0):
        golden.at(t)
    writes = golden.page.evaluate("() => { window.__keyObs.disconnect(); return window.__keyStyleWrites; }")
    assert writes == [], ("only lpSegPaint paints the key, and it writes no style", writes[:6])
    s = golden.at(G.FRAME_T["brace-funding"])
    assert all(e["style"] == e["style"].replace("visibility", "").replace("filter", "") for e in s["key"]["entries"])


def test_the_brace_never_names_the_keys_elements_and_only_lpsegpaint_reads_the_hand_off():
    src = re.sub(r"/\*.*?\*/", "", (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs")
                 .read_text(encoding="utf-8"), flags=re.S)   # the code, not the prose that names it
    a, b = src.index("  const LPBRACE = Object.freeze("), src.index("  const buildPerform = (st, scene, pg) => {")
    c, d = src.index("  const paintBrace = (b, t, ud, st) => {"), src.index("  const paintBracket = (b, t, ud, st) => {")
    brace = src[a:b] + src[c:d]
    for token in ("lp-seg-name", "lp-seg-sw", ".style.visibility", ".style.filter", "keyEntries"):
        assert token not in brace, f"the brace reaches into the key: {token!r}"
    assert "keyHandoff" not in src[a:b] and "keyHandoff" in src[c:d], "the brace's painter WRITES the hand-off; nothing else of the key"
    e, f = src.index("  const lpSegPaint = (S) => {"), src.index("\n  };\n", src.index("  const lpSegPaint = (S) => {"))
    readers = [k for k in range(len(src)) if src.startswith("keyHandoff", k)]
    outside = [k for k in readers if not (e <= k < f) and not (c <= k < d)]
    assert not outside, ("the hand-off is read by lpSegPaint alone", [src[k - 40:k + 20] for k in outside])
