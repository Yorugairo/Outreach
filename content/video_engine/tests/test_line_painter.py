"""P71 T28 (was P69 T76; the Bravos harvest v2 A41 and A21) - THE LINE PAINTER: the trace before the furniture, and the
line that changes ink at a point.

(1) `enter=trace` (A41, "trace first, furniture after"; Bravos HIS 00:00-00:06 and 05:50): a dense line page whose SHAPE
is the hook enters by its trace - the series draws on the bare ground over the page's build (the axes enter's clock),
and only then do the frame, the tick labels, the title, the end tags and the key land. Before this slice `trace` was
not one of LEDGER_ENTERS and was refused as unknown. Opt-in: E73 still opens row 1 on its axes.

(2) `ink_from: {x, color?}` on a series (A21; HIS 05:58 "red after the peak"): from x on the stroke is drawn in the new
ink - the stroke AND its bloom (P69 T37b's layers, E99 s117) - so the stretch past x draws in it on whatever word draws
it (H row 9's `build_to` on "crashed"). Before this slice the key was ACCEPTED AND IGNORED (`ledger_page.validate`
returned [] - R26-307's class). `color` is E67's four inks or a sign ink; absent, the stretch's sign (E28). A declared
colour outranks the default only where it does not lie (E53 s7 / E28): a sign ink on the wrong sign is refused with its
numbers. Byte-identical absent both (the H door and every golden).
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as MG  # noqa: E402
import ledger_page as LPG  # noqa: E402

RAIL = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-railway-index-v1.series.json"
PEAK_I, TROUGH_I = 53, 139


def _rail(ink_from=None, **top) -> dict:
    obj = json.loads(RAIL.read_text(encoding="utf-8"))
    if ink_from is not None:
        obj["series"][0]["ink_from"] = ink_from
    obj.update(top)
    return obj


def _peak_x() -> float:
    return json.loads(RAIL.read_text(encoding="utf-8"))["series"][0]["pts"][PEAK_I][0]


def _has(errors: list[str], *words: str) -> bool:
    return any(all(w in e for w in words) for e in errors)


# ---- THE PROBE'S CLASS FIRST: a malformed ink_from is refused BY NAME, never accepted and ignored ----------------------


def test_red_a_sign_ink_that_lies_is_refused_and_the_split_validates():
    """The RED the plan names: a fall painted in the pos ink is refused (E28); the peak split in the fall's ink is a page."""
    lie = LPG.validate(_rail({"x": _peak_x(), "color": "pos"}), "line")
    assert _has(lie, "series[0]", "pos", "falls", "E28"), lie
    assert LPG.validate(_rail({"x": _peak_x(), "color": "neg"}), "line") == []


@pytest.mark.parametrize("inkf, words", [
    ("red", ("ink_from is an object",)),
    ({"x": 1846.0, "colour": "neg"}, ("`colour` is not an ink_from key",)),
    ({"x": "late 1845", "color": "neg"}, ("ink_from.x must be a number",)),
    ({"x": True}, ("ink_from.x must be a number",)),
    ({"color": "neg"}, ("ink_from.x must be a number",)),
    ({"x": 1843.0, "color": "neg"}, ("is not inside the line",)),
    ({"x": 1860.0}, ("is not inside the line",)),
    ({"x": 1846.0, "color": "red"}, ("ink_from.color must be one of",)),
    ({"x": 1846.0, "color": "deemph"}, ("ink_from.color must be one of",)),
])
def test_a_malformed_ink_from_is_refused_by_name(inkf, words):
    errs = LPG.validate(_rail(inkf), "line")
    assert _has(errs, "series[0]", *words), errs


def _line(pts: list, inkf: dict) -> dict:
    return {"title": "t", "src": "s", "series": [{"label": "x", "color": "crimson", "pts": pts, "ink_from": inkf}]}


def test_a_rise_in_the_neg_ink_is_refused_too():
    """The same truth rule the other way: the climb to the peak painted blood red would lie as much."""
    climb = json.loads(RAIL.read_text(encoding="utf-8"))["series"][0]["pts"][:PEAK_I + 1]
    errs = LPG.validate(_line(climb, {"x": 1844.5, "color": "neg"}), "line")
    assert _has(errs, "neg", "rises", "E28"), errs
    assert LPG.validate(_line(climb, {"x": 1844.5, "color": "pos"}), "line") == []


def test_a_flat_stretch_with_no_colour_has_no_sign_to_take():
    flat = [[2000.0 + i, float(min(i, 6))] for i in range(14)] + [[2014.0, 6.0]]   # a dense line: a climb, then level
    errs = LPG.validate(_line(flat, {"x": 2006.0}), "line")
    assert _has(errs, "flat", "name an ink"), errs
    assert _has(LPG.validate(_line(flat, {"x": 2006.0, "color": "pos"}), "line"), "neither rises nor falls")
    assert LPG.validate(_line(flat, {"x": 2006.0, "color": "amber"}), "line") == []   # an electric ink claims no sign


def test_an_electric_ink_is_a_declared_colour_and_claims_no_sign():
    assert LPG.validate(_rail({"x": _peak_x(), "color": "cobalt"}), "line") == []


def test_ink_from_is_refused_off_a_dense_line_page():
    bars = {"title": "t", "src": "s", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}],
            "series": [{"name": "x", "pts": [[1, 1], [2, 2], [3, 1]], "ink_from": {"x": 2}}]}
    errs = LPG.validate(bars, "bars")
    assert _has(errs, "ink_from", "dense line page"), errs


def test_ink_from_is_refused_on_a_panel_and_beside_highlight_from_and_on_a_projection():
    panel = {"title": "t", "src": "s", "panels": [
        {"sub": "a", "series": [{"name": "a", "pts": [[1, 1], [2, 2], [3, 1]], "ink_from": {"x": 2}}]},
        {"sub": "b", "series": [{"name": "b", "pts": [[1, 1], [2, 2], [3, 3]]}]}]}
    assert _has(LPG.validate(panel, "line"), "panels[0].series[0]", "ink_from", "panel"), LPG.validate(panel, "line")
    hl = _rail({"x": _peak_x()}, highlight_from=1847.0)
    assert _has(LPG.validate(hl, "line"), "highlight_from", "one change of ink"), LPG.validate(hl, "line")
    proj = {"title": "t", "src": "s", "series": [
        {"label": "a", "color": "crimson", "pts": [[2020.0, 1.0], [2021.0, 2.0]]},
        {"color": "crimson", "later": True, "pts": [[2021.0, 2.0], [2022.0, 3.0], [2023.0, 2.5]], "ink_from": {"x": 2022.0},
         "projection": {"label": "2023E", "tier": "PLAUSIBLE", "src": "a range"}}]}
    assert _has(LPG.validate(proj, "line"), "a projection never changes ink"), LPG.validate(proj, "line")


def test_the_colour_is_resolved_into_the_spec_and_the_file_is_never_mutated():
    obj = _rail({"x": _peak_x()})
    before = copy.deepcopy(obj)
    spec = LPG.build_spec(obj, "line", None, "right")
    assert spec["series"][0]["ink_from"] == {"x": _peak_x(), "color": "neg"}   # it falls: the fall's own ink (E28)
    assert obj == before
    declared = LPG.build_spec(_rail({"x": _peak_x(), "color": "amber"}), "line", None, "right")
    assert declared["series"][0]["ink_from"]["color"] == "amber"


def test_a_page_without_the_key_is_byte_identical():
    plain = _rail()
    assert json.dumps(LPG.build_spec(plain, "line", None, "right"), sort_keys=True) == \
        json.dumps(LPG.build_spec(copy.deepcopy(plain), "line", None, "right"), sort_keys=True)
    assert "ink_from" not in json.dumps(LPG.build_spec(plain, "line", None, "right"))


# ---- THE TRACE ENTER: the compiler's grammar and the clock the gate reads ------------------------------------------


def test_red_trace_is_a_ledger_enter():
    assert "trace" in B.LEDGER_ENTERS
    assert B.parse_ledger_id("ledger:ev-railway-index-v1:line::right:trace")[4] == "trace"


def _world(obj: dict, plate: str) -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{plate.split(':')[1]}.series.json").write_text(json.dumps(obj), encoding="utf-8")
            return B.world_for_plate(plate, (0, 0, 0), Path(td))
    finally:
        B.ASPECT = saved


def test_the_trace_takes_no_value_and_is_a_line_page_s_alone():
    with pytest.raises(ValueError, match=r"trace takes no value"):
        _world(_rail(), "ledger:ref-rail:line::right:trace=2")
    bars = {"title": "t", "src": "s", "bars": [{"label": "a", "value": 1}, {"label": "b", "value": 2}]}
    with pytest.raises(ValueError, match=r"enter=trace.*dense line page only"):
        _world(bars, "ledger:ref-bars:bars::right:trace")
    assert _world(_rail(), "ledger:ref-rail:line::right:trace")["page"]["enter"] == "trace"


def test_the_trace_runs_the_axes_enter_s_clock_in_the_gate_and_the_compiler():
    """The chart lands one build after the page opens (the gate's M-rows and the key's ladder read the same instant)."""
    for enter in ("axes", "trace"):
        page = {"enter": enter}
        assert MG._page_land_offset({"world": {"page": page}}) == pytest.approx(MG.LP_BUILD_S), enter
    assert B._page_entry_build_s({"enter": "trace"}, 3.0) == pytest.approx(B._page_entry_build_s({"enter": "axes"}, 3.0))


# ---- ON THE SERVED PLAYER ----------------------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, S = (st.states || [st])[0];
  const FRAME = ['axis', 'tick', 'axislabel'], LABELS = ['ylabel', 'xtick'];
  const op = (m) => m.el.getAttribute('opacity');
  const pp = S.paths[0], I = pp.inkFrom || null;
  const flood = (p) => { const f = p.style.filter || ''; const m = /url\\(["']?#([^"')]+)/.exec(f); if (!m) return null;
    const fl = document.getElementById(m[1]).querySelectorAll('feFlood'); return [...fl].map(e => e.getAttribute('flood-color')); };
  const out = {
    chart: getComputedStyle(S.chart).opacity,
    frame: S.marks.filter(m => FRAME.includes(m.role)).map(op),
    labels: S.marks.filter(m => LABELS.includes(m.role)).map(op),
    glyphs: st.glyphs.map(g => +(g.__w || 0)),
    name: +pp.name.getAttribute('opacity'),
    off: parseFloat(pp.p.getAttribute('stroke-dashoffset')), len: pp.len,
    stroke: pp.p.getAttribute('stroke'), pmask: pp.p.getAttribute('mask'), pflood: flood(pp.p),
    tipFill: pp.tip.getAttribute('fill'), tipOp: +pp.tip.getAttribute('opacity'),
    peakX: pp.pts[53] ? pp.pts[53][0] : null,
  };
  if (I) {
    const q = I.q, rb = I.after, fade = I.fade;
    Object.assign(out, {q: {stroke: q.getAttribute('stroke'), d: q.getAttribute('d') === pp.p.getAttribute('d'),
      dash: q.getAttribute('stroke-dasharray') === pp.p.getAttribute('stroke-dasharray'),
      off: q.getAttribute('stroke-dashoffset') === pp.p.getAttribute('stroke-dashoffset'),
      op: q.style.opacity === pp.p.style.opacity, mask: q.getAttribute('mask'), flood: flood(I.g), next: pp.p.nextSibling === I.g && q.parentNode === I.g},
      X: I.X, after: [+rb.getAttribute('x'), +rb.getAttribute('width')], fade: [+fade.getAttribute('x1'), +fade.getAttribute('x2')],
      neg: getComputedStyle(q).getPropertyValue('--lp-neg').trim(),   // the sign tokens live on .lp (the template)
      mark: (S.markBy['s0'].geom || {}).ink_from || null});
  }
  return out;
}"""

PIXELS = """(ks) => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const pp = world.__lp.paths[0], M = pp.p.getScreenCTM();
  return ks.map(k => { const [x, y] = pp.pts[k]; return [M.a * x + M.c * y + M.e, M.b * x + M.d * y + M.f]; });
}"""


def _serve(surface):
    import render_baseline as RB
    import served_player as SP  # R26-351 (P72 T9): the one guarded Playwright start
    tl, uris = surface()
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    return at, page, errs, close


@needs_browser
def test_the_trace_draws_the_line_then_the_furniture_lands():
    import build_golden_sources as G
    at, _page, errs, close = _serve(G.enter_trace)
    try:
        mid, just, landing, landed = at(1.5), at(3.02), at(3.3), at(4.4)
        back = at(1.5)   # a seek back is the play
    finally:
        close()
    assert not errs, errs
    assert mid == back, "a seek back paints the frame it painted before"
    # mid-trace: the line is drawing on the bare ground - no frame, no tick label, no title, no tag
    assert 0 < mid["off"] < mid["len"] and mid["chart"] == "1", mid
    assert set(mid["frame"]) == {"0.000"} and set(mid["labels"]) == {"0.000"}, (mid["frame"], mid["labels"])
    assert max(mid["glyphs"]) == 0 and mid["name"] == 0, mid
    # the trace done: the whole line drawn, the frame starting to land, the labels and the title not yet
    assert just["off"] <= 0.5 and 0 < float(just["frame"][0]) < 1 and set(just["labels"]) == {"0.000"}, just
    # landing: the frame nearly down, the labels arriving, the title part-written - and still no tag
    assert all(0.5 < float(v) < 1 for v in landing["frame"]) and any(0 < float(v) < 1 for v in landing["labels"]), landing
    assert 0 < sum(1 for g in landing["glyphs"] if g >= 1) < len(landing["glyphs"]) and landing["name"] == 0, landing
    # landed: every furniture mark back to the attribute it was built with (none), every letter written, the tag whole
    assert set(landed["frame"]) == {None} and set(landed["labels"]) == {None}, landed
    assert min(landed["glyphs"]) == 1 and landed["name"] == 1, landed


@needs_browser
def test_the_axes_enter_keeps_its_furniture_on_frame_zero():
    """The control: the same page on `axes` stands on its frame and ticks while the line draws (E73, unchanged)."""
    import build_golden_sources as G
    at, _page, errs, close = _serve(lambda: G.trace_surface("axes"))
    try:
        mid = at(1.5)
    finally:
        close()
    assert not errs, errs
    assert 0 < mid["off"] < mid["len"]
    assert set(mid["frame"]) == {None} and set(mid["labels"]) == {None} and max(mid["glyphs"]) > 0, mid


@needs_browser
def test_the_ink_changes_at_the_peak_on_the_word_that_draws_the_fall():
    import build_golden_sources as G
    at, page, errs, close = _serve(G.ink_from_crash)
    try:
        before = at(G.INK_CRASH_AT - 0.1)
        drawing = at(G.INK_CRASH_AT + 0.5)
        landed = at(G.FRAME_T["ink-from-crash"])
        xy = page.evaluate(PIXELS, [30, 45, 90, 120])
        shot = page.screenshot()
        again = at(G.INK_CRASH_AT - 0.1)
    finally:
        close()
    assert not errs, errs
    assert again == before, "a seek back paints the frame it painted before"
    # the twin: the new ink, right over its line (its group carries the bloom), wearing the line's own d, dash and opacity every frame
    for f in (before, drawing, landed):
        q = f["q"]
        assert q["stroke"] == "var(--lp-neg)" and q["next"] and q["d"] and q["dash"] and q["off"] and q["op"], q
    assert landed["stroke"] == "#FF8A4C", "the climb keeps its own crimson"
    # the split sits AT the peak: the two masks meet at the peak datum's x on the path as drawn
    assert abs(landed["X"] - landed["peakX"]) < 0.05, (landed["X"], landed["peakX"])
    assert landed["fade"][0] == pytest.approx(landed["X"], abs=0.01) and landed["fade"][1] > landed["fade"][0]   # the line's glow fades out past x
    assert landed["after"][0] == pytest.approx(landed["X"], abs=0.01)
    assert landed["pmask"] and landed["q"]["mask"] and landed["pmask"] != landed["q"]["mask"]
    # ON ITS WORD: before "crashed" the line stands at the peak (nothing past x is drawn); drawing, the pen is past it
    peak_len_share = 1 - before["off"] / before["len"]
    assert 0.2 < peak_len_share < 0.7, peak_len_share
    assert drawing["off"] < before["off"] and landed["off"] <= 0.5, (before["off"], drawing["off"], landed["off"])
    # the nib wears the ink it draws: the fall's while it runs the fall
    assert drawing["tipOp"] == 1 and drawing["tipFill"] == "var(--lp-neg)", drawing
    # THE BLOOM FOLLOWS THE INK (s117): the line's halo floods crimson, the twin's floods the fall's red
    assert landed["pflood"] and set(landed["pflood"]) == {"#FF8A4C"}, landed["pflood"]
    assert landed["q"]["flood"] and set(landed["q"]["flood"]) == {landed["neg"]}, (landed["q"]["flood"], landed["neg"])
    assert landed["neg"].upper() == "#FF4D4D", landed["neg"]   # a hex the flood can take, never the var() itself
    assert landed["mark"] == {"x": pytest.approx(_peak_x()), "col": "var(--lp-neg)"}
    # the pixels: the climb reads orange-crimson, the fall reads blood red
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(shot)).convert("RGB")

    def ink(x, y):   # the most saturated pixel in a 7 px box round the datum (the stroke, not the ground beside it)
        px = [im.getpixel((int(x) + dx, int(y) + dy)) for dx in range(-3, 4) for dy in range(-3, 4)]
        return max(px, key=lambda c: max(c) - min(c))
    climb, fall = [ink(*p) for p in xy[:2]], [ink(*p) for p in xy[2:]]
    for r, g, b in climb:
        assert r > 200 and g - b > 30, climb             # #FF8A4C: orange (green well over blue), hot-cored toward white
    for r, g, b in fall:
        assert r - g > 120 and abs(g - b) < 20, fall    # #FF4D4D: the fall's blood red (green and blue level)


def test_the_goldens_are_registered_and_read_the_committed_object():
    import build_golden_sources as G
    for name in ("enter-trace", "ink-from-crash"):
        assert name in G.SURFACES and name in G.FRAME_T
        assert f'"{name}"' in (ROOT / "content/video_engine/tests/test_golden_frames.py").read_text(encoding="utf-8")
    obj = json.loads(RAIL.read_text(encoding="utf-8"))
    ser = G.rail_series(ink_from=True)
    assert ser["series"][0]["pts"] == obj["series"][0]["pts"]
    assert ser["series"][0]["ink_from"] == {"x": obj["series"][0]["pts"][PEAK_I][0]}
    assert "ink_from" not in json.dumps(G.rail_series())
