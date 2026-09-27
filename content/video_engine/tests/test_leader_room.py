"""P72 T53 (k) / R26-418 - THE LEADER'S TWO LIMITS, read on the served player.

  (a) at 9:16 the automatic side lifted into a word ($121B) at every bow and SAGGED through the bars; it now tries the
      wide lifts (LEADER.WIDE) before settling for ink, and may leave the chart's box upward into the free room the page
      has above it (lpLeaderSky) - the air arc of Bravos STK 0:08.
  (b) on the long form the arc rode the plot frame's top border (the frame was no obstacle to leaderChoose); a sample on
      the border now costs (LEADER.FRAME_COST), the pill straddling it costs as a word does, so the arc crosses the
      border cleanly or not at all.
The fixtures are test_leader's (the golden's three bars at 9:16; the AMD price page on the long form).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import served_player as SP  # noqa: E402


def _chromium_available() -> bool:
    try:
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')), st = w.__lp, L = ((st.perform || {}).leaders || [])[0];
  if (!L) return null;
  const sh = L.shaft, n = sh.getTotalLength(), pts = [];
  for (let i = 0; i <= 60; i++) { const q = sh.getPointAtLength(n * i / 60); pts.push([q.x, q.y]); }
  const BM = st.markBy || {}, bars = [];
  for (let i = 0; BM['b:' + i] && BM['b:' + i].geom; i++) { const q = BM['b:' + i].geom; bars.push([q.x, q.y, q.x + q.w, q.y + q.h]); }
  const pill = L.pill ? L.pill.g.getBBox() : null, pm = L.pill ? L.pill.g.getCTM() : null, cm = st.chart.getCTM();
  const pillBox = pill && pm && cm ? (() => { const inv = cm.inverse().multiply(pm);
    const a = new DOMPoint(pill.x, pill.y).matrixTransform(inv), b = new DOMPoint(pill.x + pill.width, pill.y + pill.height).matrixTransform(inv);
    return [a.x, a.y, b.x, b.y]; })() : null;
  const fr = st.lfPanelEl ? ['x', 'y', 'width', 'height'].map(a => +st.lfPanelEl.getAttribute(a)) : null;
  return { pts, bars, pillBox, k: L.k, pick: L.pick, frame: fr ? [fr[0], fr[1], fr[0] + fr[2], fr[1] + fr[3]] : null,
           W: +st.chart.viewBox.baseVal.width, H: +st.chart.viewBox.baseVal.height };
}"""


def _read(tl: dict, uris: dict, t: float) -> dict:
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    size = RB.STAGE[str(tl.get("aspect") or "16:9")]
    page, errs, close = SP.open_served(html, *size, cleanup=td.cleanup)
    try:
        RB.frame_png(page, t, size)
        out = page.evaluate(PROBE)
        assert not errs, errs
        return out
    finally:
        close()


def _in(p, b) -> bool:
    return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]


@needs_browser
def test_at_nine_sixteen_the_arc_lifts_over_the_words_and_never_sags_through_the_bars():
    import build_golden_sources as G
    tl, uris = G.leader_points_back(aspect="9:16")
    f = _read(tl, uris, G.LEADER_AT + G.LEADER_DUR + 0.4)
    through = [b for b in f["bars"] if any(_in(p, b) for p in f["pts"][3:-3])]
    assert not through, ("R26-418 (a): the automatic side sagged through the bars", f["pick"], through)
    assert min(p[1] for p in f["pts"]) < min(p[1] for p in (f["pts"][0], f["pts"][-1])), "an air arc: it rises off its source"


@needs_browser
@pytest.mark.parametrize("page", ["three-bars", "amd-prices"])
def test_on_the_long_form_the_arc_crosses_the_plot_frame_cleanly_and_its_pill_is_never_on_the_border(page):
    """three-bars: H row 16's page on the long form (P72 T53 (h)'s R35 strip, 17.92 s: the 5.4x pill ON the frame's top
    border); amd-prices: test_leader's long-form page, where the old side already cleared it - a control."""
    import build_golden_sources as G
    if page == "three-bars":
        tl, uris = G.leader_points_back(opts=";readability=longform")
        t = G.LEADER_AT + G.LEADER_DUR + 0.4
    else:
        lead = {"kind": "leader", "at": 11.0, "dur": 1.6, "from": {"kind": "datum", "index": 0, "part": "value"},
                "to": {"kind": "datum", "index": 3, "part": "value"}, "ring": True, "multiple": True, "head": "dot"}
        tl, uris = G.leader_points_back(species=[lead], obj=G.claim_price_object(), opts=";readability=longform")
        t = 13.2
    f = _read(tl, uris, t)
    fr, reach = f["frame"], 16.0 / f["k"]   # 16 stage px either side of the border's line
    assert fr, "the long form draws its plot frame"
    ride = [p for p in f["pts"] if fr[0] <= p[0] <= fr[2] and abs(p[1] - fr[1]) <= reach]
    assert len(ride) <= 4, ("R26-418 (b): the arc rides the frame's top border (a clean crossing is 2-4 of the 61 samples "
                            "in the band; the frame-blind side ran 6 and 12)", len(ride), ride[:6])
    pts = f["pts"]
    cross = [i for i in range(len(pts) - 1) if fr[0] <= pts[i][0] <= fr[2] and (pts[i][1] - fr[1]) * (pts[i + 1][1] - fr[1]) < 0]
    assert len(cross) <= 1, ("R26-418 (b): the arc goes out through the frame's top border and back in", len(cross))
    pb, pad = f["pillBox"], 6.0 / f["k"]   # the pill keeps LEADER.PILL_PAD_PX of air off a word - and off the border
    assert pb and not (pb[1] - pad < fr[1] < pb[3] + pad and pb[2] > fr[0] and pb[0] < fr[2]), (
        "the pill stands on the frame's border (within its own air)", pb, fr)
