"""P72 T53 (j) / R26-417 - WHAT A PAGE'S LATER STATES STILL OWED AFTER P72 T26.

  (a) a PLAIN recast's SUB and SOURCE hand over WHOLE, like its title (T26's lpRetitleWhole): the standing ones stand
      whole until the standing data are off the plot, the arriving ones stand whole from that instant - never the
      arriving sub half-written under the standing title (H 81.5, 663.7).

The fixtures are T26's inline synthetic shapes (test_page_later_states). The browser half needs playwright + chromium.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import test_page_later_states as T26  # noqa: E402

needs_browser = T26.needs_browser

WORDS_JS = T26.PAGE_JS + """ const gw = (g) => parseFloat(g.style.getPropertyValue('--w')) || 0;
  const pf = lp.perform || { retitles: [] }, S = lp.states, span = (gs) => (gs || []).map(gw);
  const ink = (i) => i === 0 ? { sub: span(lp.subGlyphs), src: span(lp.srcGlyphs) }
    : { sub: span((S[i].subInk || {}).glyphs), src: span((S[i].srcInk || {}).glyphs) };
  return { st: [0, 1, 2].filter(i => S[i]).map(ink), title: (((pf.retitles || [])[1] || {}).glyphs || []).map(gw) };"""


def _whole(ws: list) -> bool:
    return bool(ws) and min(ws) >= 0.999


def _gone(ws: list) -> bool:
    return not ws or max(ws) <= 0.001


@needs_browser
@pytest.mark.parametrize("hop", ["0-to-1", "1-to-2"])
def test_a_plain_recasts_sub_and_source_hand_over_whole_with_the_title(hop, tmp_path):
    """At every instant of the recast one state's sub and source stand whole and the other's not at all, and they swap
    on the frame the arriving title does (H 81.5: 'US private nonresidential investment, sl' under the standing
    railway title)."""
    if hop == "0-to-1":
        row, a, b, pre = "ledger:t26-line-a:line;then=t26-line-b:line", 0, 1, []
    else:
        row, a, b = "ledger:t26-line-b:line;then=t26-line-a:line;then=t26-line-b:line", 1, 2
        pre = [{"kind": "chart_to", "to": "recast", "state": 1, "at": 4.0, "dur": T26.RECAST_S, "keyed": False}]
    species = pre + [{"kind": "retitle", "at": 5.0 + (2.0 if pre else 0), "dur": 1.2, "text": "The standing title, a retitle",
                      "leave_at": T26.RECAST_AT, "leave_s": 1.0},
                     {"kind": "chart_to", "to": "recast", "state": b, "at": T26.RECAST_AT, "dur": T26.RECAST_S, "keyed": False},
                     {"kind": "retitle", "at": T26.RECAST_AT + 0.1, "dur": T26.RECAST_S, "text": "The arriving title, written whole"}]
    tl, uris = T26._tl(T26._world(row, tmp_path), species)
    times = [round(T26.RECAST_AT - 0.2 + 0.05 * k, 2) for k in range(0, 38)]
    bad, off_clock = [], []
    for t, r in zip(times, T26._read(tl, uris, "(t) => {" + WORDS_JS + "}", times)):
        A, Bk = r["st"][a], r["st"][b]
        for part in ("sub", "src"):
            old_whole, old_gone, new_whole, new_gone = _whole(A[part]), _gone(A[part]), _whole(Bk[part]), _gone(Bk[part])
            if not ((old_whole and new_gone) or (old_gone and new_whole)):
                bad.append((t, part, round(min(A[part] or [0]), 3), round(max(Bk[part] or [0]), 3)))
            elif t >= T26.RECAST_AT + 0.1 and _whole(r["title"]) != new_whole:
                off_clock.append((t, part, _whole(r["title"]), new_whole))
        if a != 0 and b != 0:   # a hop between two LATER states: the page's own words (state 0's) stay erased throughout
            for part in ("sub", "src"):
                if not _gone(r["st"][0][part]):
                    bad.append((t, "page's own " + part, round(max(r["st"][0][part]), 3), None))
    assert not bad, f"a half-written sub or source (t, part, standing min, arriving max): {bad[:6]}"
    assert not off_clock, f"the words swap on another frame than the title (t, part, title whole, arriving whole): {off_clock[:6]}"


# ---- (d) mid-extend the two scales' y ticks never stack ------------------------------------------------------------------

YT_JS = T26.PAGE_JS + """ const stage = document.getElementById('stage').getBoundingClientRect(), k = 1920 / stage.width, out = [];
  const alpha = (e) => { let a = 1; for (let n = e; n && n.id !== 'stage'; n = n.parentElement) { const c = getComputedStyle(n);
    if (c.display === 'none' || c.visibility === 'hidden') return 0; a *= +c.opacity; if (n.getAttribute && n.getAttribute('opacity') != null) a *= +n.getAttribute('opacity'); } return a; };
  for (const S of lp.states) for (const m of S.marks || []) { if (m.role !== 'ylabel' || !m.el || !(m.el.textContent || '').trim()) continue;
    const a = alpha(m.el); if (a < 0.15) continue; const r = m.el.getBoundingClientRect();
    out.push({ text: m.el.textContent, a: +a.toFixed(2), y0: (r.top - stage.top) * k, y1: (r.bottom - stage.top) * k, x0: (r.left - stage.left) * k, x1: (r.right - stage.left) * k }); }
  return out;"""


@needs_browser
def test_mid_extend_the_two_scales_y_labels_never_print_on_each_other():
    """T26's fixture (the golden issuance page: a rescale to 2021-2023, then the extend to 2026E): through the extend's
    rescale phase the standing scale's labels (27 .. 29) compress toward the new scale's foot and met each other and the
    arriving '50' (R26-417 (d): '29 28.5 28 27.5 27' stacked at 10.62). A label is never drawn over another."""
    tl, uris = T26._issuance([{"kind": "chart_to", "at": 8.0, "dur": 1.2, "to": "rescale", "window": [2021, 2023]},
                              {"kind": "chart_to", "at": 10.5, "dur": 1.2, "to": "extend", "series": 1}])
    times = [round(10.5 + 0.02 * k, 2) for k in range(0, 28)]
    bad = []
    for t, labs in zip(times, T26._read(tl, uris, "(t) => {" + YT_JS + "}", times)):
        for i, a in enumerate(labs):
            for b in labs[i + 1:]:
                ov = min(a["y1"], b["y1"]) - max(a["y0"], b["y0"])
                if ov > 2.0 and min(a["x1"], b["x1"]) - max(a["x0"], b["x0"]) > 2.0:
                    bad.append((t, a["text"], a["a"], b["text"], b["a"], round(ov, 1)))
    assert not bad, f"two y labels on each other mid-extend (t, label, alpha, label, alpha, px): {bad[:6]}"


# ---- (e) a then= state draws its own inline badge chips ------------------------------------------------------------------

CHIP_JS = T26.PAGE_JS + """ return lp.states.map(S => [...S.chart.querySelectorAll('tspan.tagchip')].map(e => e.textContent));"""


@needs_browser
@pytest.mark.parametrize("row", ["ledger:t26-line-a:line;then=t26-long:line", "ledger:t26-long:line"])
def test_a_then_state_draws_its_inline_badge_chips_as_its_own_page_does(row, tmp_path):
    """The LONG line's object carries three inline badges (the tags 'our layer', 'their divergence', 'matches the market'):
    as its own page it writes them as chips on its end names; as a `then=` state it drew none (R26-417 (e), T26's F5)."""
    tl, uris = T26._tl(T26._world(row, tmp_path), [])
    (chips,) = T26._read(tl, uris, "(t) => {" + CHIP_JS + "}", [2.0])
    want = {"our layer", "their divergence", "matches the market"}
    assert set(chips[-1]) == want, (row, chips)
