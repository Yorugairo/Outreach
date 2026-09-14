"""R26-71 (P57 T10) - A FIGURE'S NUMBER MAY NOT BE WRITTEN ACROSS ITS OWN LINE.

The bridge short's `31% of GDP` (s04, datum 63) printed straight through the rising debt line: the figure was
placed off its datum alone - `x = D[0] + 14`, `y = D[1] + fs*0.35 + dy*fs*1.2` - and never asked where the ink
went next. M34 reads those boxes as `bracket:` because `paintFigure` writes into the same `bklab` class as the
bracket's label; the species is a FIGURE and the placement is `paintFigure`'s, not `geomOf`'s.

The fix steps the box off the ink in fixed quanta (PS.FIGURE_STEP), the authored `dy`'s side first, capped at
PS.FIGURE_STEPS, and it is a pure function of the datum, the series' points and the authored `dy` - so a cold
seek lands where a play does (R26-28).

These tests drive the BUILT PLAYER through playwright (the engine's placement lives in the browser, not in a
python module): one page per case, the figure's box read back in the chart's own viewBox units with getBBox,
the series' polyline parsed out of the path it is drawn from. They skip without chromium, like the E67 tests.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402

SURFACE = "ledger-soak-page"
AT, DUR = 6.0, 1.2          # the figure's word; every read is at AT + DUR (fully written)
ROUND = 0.1001              # the baseline AND the datum I read it back from are both written to one decimal:
                            # two last digits is not a move - a step is PS.FIGURE_STEP * fs, two orders above it
DY = -0.8                   # the bridge short's own authored offset: a line of its own size, up


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

READ = """() => {
  const el = document.querySelector('text.bklab');
  if (!el) return null;
  const bb = el.getBBox(), cs = getComputedStyle(el);
  const path = document.querySelector('.lp-chart path.ser:not(.muted)') || document.querySelector('.lp-chart path.ser');
  const pts = (path.getAttribute('d') || '').split(/[ML]/).slice(1)
    .map((s) => s.trim().split(/\\s+/).map(Number)).filter((p) => p.length === 2 && p.every(Number.isFinite));
  return { text: el.textContent, x: +el.getAttribute('x'), y: +el.getAttribute('y'),
           anchor: el.getAttribute('text-anchor'), fs: parseFloat(cs.fontSize),
           box: [bb.x, bb.y, bb.width, bb.height], pts,
           hw: parseFloat(getComputedStyle(path).strokeWidth) / 2 };
}"""


class _FigurePage:
    """One golden surface's page, its series and its one FIGURE replaced with the case under test."""

    def __init__(self, values: list[float], index: int, text: str = "31% of GDP", dy: float = DY):
        from playwright.sync_api import sync_playwright
        tl, uris, _t, aspect = RB.load_surface(SURFACE)
        sc = tl["scenes"][0]
        pg = sc["world"]["page"]
        series = [{"name": "Debt", "color": "teal", "pts": [[str(1970 + i), str(v)] for i, v in enumerate(values)]}]
        page_spec = dict(pg, series=series, axes=dict(pg.get("axes") or {}))
        page_spec.pop("highlight_from", None)
        species = [{"kind": "figure", "at": AT, "dur": DUR, "text": text,
                    "target": {"kind": "datum", "index": index}, "dy": dy, "id": "t.figure.0"}]
        scene = dict(sc, species=species,
                     world=dict(sc["world"], page=page_spec, ken_burns={"scale": 0, "x": 0, "y": 0}))
        timeline = dict(tl, scenes=[scene], caption_pages=[], captions=[])
        self.td = tempfile.TemporaryDirectory()
        html = Path(self.td.name) / "figure.html"
        html.write_text(RB.instantiate(timeline, uris, engine=RB.ENGINE), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        self.srv, port = RB.serve(html.parent)
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=True)
        self.page = self.browser.new_context(viewport={"width": w, "height": h}).new_page()
        self.page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
        RB.prepare_page(self.page, w, h)

    def read(self, t: float = AT + DUR) -> dict:
        for _ in range(2):   # WARM: the probe's rule - the first seek settles the page, the second is the frame
            self.page.evaluate(
                "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        got = self.page.evaluate(READ)
        assert got, "no figure label on the page"
        assert len(got["pts"]) >= 2, f"no series polyline to measure against: {got['pts']}"
        return got

    def close(self):
        self.browser.close()
        self.pw.stop()
        self.srv.shutdown()
        self.td.cleanup()


# ---- the measurement (the test owes nobody's arithmetic) ----------------------------------------


def _seg_meets_box(p0, p1, box, pad: float) -> bool:
    """Liang-Barsky: does the segment meet the box grown by `pad` on every side?"""
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[0] + box[2] + pad, box[1] + box[3] + pad
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, p0[0] - x0), (dx, x1 - p0[0]), (-dy, p0[1] - y0), (dy, y1 - p0[1])):
        if p == 0:
            if q < 0:
                return False
            continue
        r = q / p
        if p < 0:
            if r > t1:
                return False
            t0 = max(t0, r)
        else:
            if r < t0:
                return False
            t1 = min(t1, r)
    return True


def _hits(got: dict, pad: float | None = None) -> list[int]:
    """Every segment index of the series whose stroke crosses the figure's box."""
    pts, box = got["pts"], got["box"]
    pad = got["hw"] if pad is None else pad
    return [i for i in range(1, len(pts)) if _seg_meets_box(pts[i - 1], pts[i], box, pad)]


def _default_y(got: dict, datum_y: float, dy: float = DY) -> float:
    """Where paintFigure has always written the baseline when nothing is in the way."""
    return datum_y + got["fs"] * 0.35 + dy * got["fs"] * 1.2


def test_the_measurement_finds_a_crossing_and_a_clear_box():
    """The helper is right on both ends before it judges the engine."""
    box = [100.0, 100.0, 200.0, 60.0]
    assert _seg_meets_box([90, 130], [310, 130], box, 0.0), "a segment straight through the box"
    assert not _seg_meets_box([90, 400], [310, 400], box, 0.0), "a segment far below the box"
    assert _seg_meets_box([90, 95], [310, 95], box, 8.0), "a segment inside the pad counts as ink"


# a line that stands flat and then CLIMBS - the bridge's own shape, the figure written on the flat
# datum just before the climb, exactly where `31% of GDP` was printed across the rise
CLIMB = [31.0, 31.5, 31.2, 31.8, 32.0, 62.0, 92.0, 118.0, 123.0, 123.5]
CLIMB_AT = 4

# a line that FALLS away to the right, the figure lifted a clear line and a half above the datum it names -
# nothing stands in the band where it is written, and nothing should move it
FALL = [123.0, 70.0, 50.0, 42.0, 38.0, 35.0, 33.0, 32.0, 31.5, 31.0]
FALL_AT, FALL_DY = 1, -1.6


@needs_browser
def test_a_figure_over_a_climbing_line_steps_off_the_ink():
    """R26-71: `31% of GDP` was printed across the line it names. The box must stand clear of the stroke."""
    p = _FigurePage(CLIMB, CLIMB_AT)
    try:
        got = p.read()
        hit = _hits(got)
        assert not hit, (f"the figure's box {got['box']} is crossed by its own series at segment(s) {hit} "
                         f"- the number is printed across the line it names (R26-71)")
    finally:
        p.close()


@needs_browser
def test_the_figure_that_steps_off_moves_only_by_whole_quanta_from_its_authored_place():
    """The step is a named quantum, not a search: the baseline lands on `dy` plus k steps of PS.FIGURE_STEP."""
    src = ENGINE.read_text(encoding="utf-8")
    step = float(re.search(r"FIGURE_STEP:\s*([0-9.]+)", src).group(1))
    steps = int(re.search(r"FIGURE_STEPS:\s*(\d+)", src).group(1))
    p = _FigurePage(CLIMB, CLIMB_AT)
    try:
        got = p.read()
        datum_y = got["pts"][CLIMB_AT][1]
        delta = got["y"] - _default_y(got, datum_y)
        k = delta / (step * got["fs"])
        assert abs(k - round(k)) < 0.02, f"the figure moved {delta:.1f} - not a whole quantum of {step} * fs"
        assert 1 <= abs(round(k)) <= steps, f"moved {round(k)} step(s); the cap is {steps}"
    finally:
        p.close()


@needs_browser
def test_a_figure_with_a_clear_box_does_not_move_at_all():
    """The no-collision case is byte-stable: nothing on the ink, nothing to step off, the authored place stands."""
    p = _FigurePage(FALL, FALL_AT, dy=FALL_DY)
    try:
        got = p.read()
        assert not _hits(got), f"the fixture is wrong - the box {got['box']} already meets the line"
        datum_y = got["pts"][FALL_AT][1]
        want = _default_y(got, datum_y, FALL_DY)
        assert abs(got["y"] - want) <= ROUND, (   # the engine writes the baseline to one decimal
            f"a figure with nothing in its way moved: y={got['y']} against the authored {want:.1f}")
    finally:
        p.close()


@needs_browser
def test_the_placement_is_the_same_on_a_cold_seek_as_in_a_play():
    """R26-28: the geometry is a function of the datum, the points and `dy` - never of how the page got there."""
    p = _FigurePage(CLIMB, CLIMB_AT)
    try:
        cold = p.read()
        for t in (0.5, 2.0, 4.0, AT, AT + 0.4, AT + DUR):
            p.read(t)
        played = p.read()
        assert cold["y"] == played["y"] and cold["x"] == played["x"], (cold["x"], cold["y"], played["x"], played["y"])
    finally:
        p.close()
