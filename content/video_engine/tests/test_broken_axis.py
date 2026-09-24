"""P69 T66 - THE BROKEN CROSS-ERA AXIS: one line across two eras on ONE x axis, the break drawn (E99 s111).

The operator, 2026-09-23, asked whether Bravos's broken x axis ("History is About to Be Made" 7:18-8:01, "AI and
Railway Spending As a % of GDP", the 1860s and 1985-on joined by a `//`) is how Bravos would handle it: "yes". A line
may run across two eras on ONE x axis with a visible break when the claim is that the LEVELS are comparable era to
era; the y is one unit for both, both eras are labelled, and the break is drawn so the gap is never read as
continuous time (E53 s3's "never a continuous axis" is met by the break, not broken). When the claim is that the
SHAPES match, the rebased overlay (row 15's "years from each era's start") stays the form.

REUSED, not rebuilt: the dense-line page (`buildLedgerLine`) is the page - its y scale, its rules, its ticks, its
end tags and its `build=lines` clock (R26-226) are the ones every line page has; the object carries one more axes
key, `break: {after, before, eras}`, and the page's `claim: "level"`. The retired zigzag of the breakthrough bars
("a broken-axis mark says abbreviated", CAPABILITIES:90 / E60) was refused because a bar's SCALE is not abbreviated;
an x axis across two eras IS abbreviated, and the mark says exactly that.

HONESTY: both eras' own dates are printed at their ticks and the gap is written at the break ("2001 // 2021"); the
`//` is DRAWN across the axis, and the stretch between the eras carries no mark at all (no gridline, no rule, no
trace) - the line lifts and resumes, no point is interpolated across the gap; both stretches are scaled on the
SAME years-per-pixel; the eras share ONE y scale in ONE unit - a second unit, an `independent` page or a right
axis is refused (that is E79's panels), and so is an unlabelled era.

The golden is the committed two-era 10-year yield object's own data (`ev-tnx-two-eras-v3`: 1998-2001 and
2021-today, Yahoo Finance ^TNX) - no railway-era share-of-GDP SERIES is committed (only the 7 % peak tile), so the
railway page waits for its sourced series and none is invented here.
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
import ledger_page as L  # noqa: E402
import render_baseline as RB  # noqa: E402

V3 = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-tnx-two-eras-v3.series.json"
V4 = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-tnx-two-eras-v4.series.json"
OBJECTS = sorted(ROOT.glob("content/video_engine/projects/*/*/evidence/objects/*.series.json"))
SURFACE = "broken-axis-two-eras"


def _golden():
    import build_golden_sources as G
    return G


def _page(**over) -> dict:
    s = _golden().broken_axis_series()
    s.update(over)
    return s


def _errs(s: dict) -> str:
    return " | ".join(L.validate(s, "line"))


# ---- the data: the committed object's own values, never re-typed ---------------------------------------------------


def test_the_golden_is_the_committed_two_era_objects_own_data():
    v3 = L.load_series(V3)   # the object as every page reads it: each number its own token (parse_float=str)
    s = _golden().broken_axis_series()
    assert [x["pts"] for x in s["series"]] == [p["series"][0]["pts"] for p in v3["panels"]], \
        "every point is v3's, verbatim - none added, dropped or moved"
    assert s["src"] == v3["src"] and s["hlines"] == v3["hlines"] and s["yunit"] == v3["yunit"]
    assert json.loads(V3.read_text(encoding="utf-8"))["panels"][0]["series"][0]["pts"][-1] == [2001.9692, 5.078]
    assert s["break"]["after"] == v3["panels"][0]["series"][0]["pts"][-1][0]
    assert s["break"]["before"] == v3["panels"][1]["series"][0]["pts"][0][0]
    assert s["claim"] == "level"
    assert L.validate(s, "line") == []


# ---- the grammar: `break` is an axes key, carried onto the spec -------------------------------------------------------


def test_break_is_an_axes_key_carried_onto_the_spec():
    assert "break" in L.AXES_KEYS
    spec = L.build_spec(_page(), "line")
    assert spec["builder"] == "dense-line"
    assert spec["axes"]["break"] == _page()["break"]


def test_a_page_without_a_break_carries_none_of_it():
    for path in OBJECTS:
        s = L.load_series(path)
        if "break" in s:
            continue
        variant = L.infer_variant(s) or "line"
        if L.validate(s, variant):
            continue
        spec = L.build_spec(s, variant)
        assert "break" not in (spec.get("axes") or {}), path.name


def test_every_committed_object_validates_as_it_did():
    """No committed object names a break, so no committed object gains an error from the break's checks."""
    for path in OBJECTS:
        s = L.load_series(path)
        variant = L.infer_variant(s) or "line"
        assert not [e for e in L.validate(s, variant) if "E99 s111" in e], path.name


# ---- the claim: a LEVEL claim is a break; a SHAPE claim is the rebased overlay ----------------------------------------


def test_a_break_states_its_claim():
    s = _page()
    s.pop("claim")
    assert "claim" in _errs(s) and "level" in _errs(s)


def test_a_shape_claim_is_refused_with_the_pointer_to_the_rebased_overlay():
    e = _errs(_page(claim="shape"))
    assert "rebased overlay" in e and "years from each era's start" in e, e


def test_an_unknown_claim_is_refused_by_name():
    assert "'trend'" in _errs(_page(claim="trend"))


# ---- ONE unit, ONE y scale ---------------------------------------------------------------------------------------------


def test_a_break_writes_its_one_unit():
    s = _page()
    s.pop("yunit")
    assert "yunit" in _errs(s)


def test_a_series_in_a_second_unit_is_refused_naming_the_panels():
    s = _page()
    s["series"] = copy.deepcopy(s["series"])
    s["series"][1]["unit"] = "$bn"
    e = _errs(s)
    assert "one unit" in e.lower() and "panels" in e, e


def test_an_independent_page_or_a_right_axis_is_refused():
    assert "independent" in _errs(_page(independent=True))
    assert "line_unit" in _errs(_page(line_unit="$"))


# ---- both eras labelled, both eras' dates printed -----------------------------------------------------------------------


@pytest.mark.parametrize("eras", [None, [], ["DOT-COM ERA"], ["DOT-COM ERA", ""], ["DOT-COM ERA", "  "], "AI ERA"])
def test_an_unlabelled_era_is_refused(eras):
    s = _page()
    s["break"] = dict(s["break"])
    if eras is None:
        s["break"].pop("eras")
    else:
        s["break"]["eras"] = eras
    assert "era" in _errs(s) and "label" in _errs(s).lower()


def test_each_era_prints_its_own_dates():
    s = _page(xticks=[t for t in _page()["xticks"] if t[0] < 2010])
    assert "no tick" in _errs(s), "the AI era would print none of its dates"


def test_a_tick_in_the_gap_is_refused():
    s = _page(xticks=_page()["xticks"] + [[2010, "2010"]])
    assert "2010" in _errs(s) and "gap" in _errs(s)


# ---- the break is tight to the data, and nothing stands in the gap -------------------------------------------------------


def test_the_break_names_the_last_datum_of_one_era_and_the_first_of_the_next():
    brk = _page()["break"]
    assert "after" in _errs(_page(**{"break": dict(brk, after=2001.5)}))
    assert "before" in _errs(_page(**{"break": dict(brk, before=2021.5)}))
    assert "before" in _errs(_page(**{"break": dict(brk, after=2021.0082, before=2001.9692)}))


def test_a_point_inside_the_gap_is_refused():
    s = _page()
    s["series"] = copy.deepcopy(s["series"])
    s["series"][0]["pts"].append([2010.0, 3.2])
    e = _errs(s)
    assert "2010" in e and "gap" in e, e


def test_malformed_breaks_are_refused_by_name():
    for bad in (True, "2001//2021", {"after": "x", "before": 2021.0082, "eras": ["A", "B"]}, {"eras": ["A", "B"]}):
        assert "break" in _errs(_page(**{"break": bad})), bad


def test_a_break_is_a_dense_line_pages():
    bars = {"title": "t", "src": "s", "yunit": "%", "claim": "level",
            "break": {"after": 2001, "before": 2021, "eras": ["A", "B"]},
            "bars": [{"label": "2001", "value": 1}, {"label": "2021", "value": 2}]}
    assert "dense-line" in " | ".join(L.validate(bars, "bars"))


def test_a_window_across_a_broken_axis_is_refused():
    assert "xdomain" in _errs(_page(xdomain=[1999, 2024]))


def test_the_gap_is_written_in_the_eras_own_years():
    assert L.break_gap_label(_page()["break"]) == "2001 // 2021"
    assert L.break_gap_label({"after": 1849.5, "before": 1985.0, "eras": ["A", "B"]}) == "1849 // 1985"


# ---- the compiler: a SHAPE claim stays the overlay; the break holds its page --------------------------------------------


def test_two_eras_on_an_unbroken_axis_warn_and_name_both_forms():
    s = _page()
    for k in ("break", "claim"):
        s.pop(k)
    w = L.era_void_warning(s, "ev-joined")
    assert w and "E53 s3" in w and "break" in w and "rebased overlay" in w and "years from each era's start" in w, w
    assert L.era_void_warning(_page(), "ev-broken") is None, "a declared break is the answer, not a warning"
    assert L.era_void_warning(L.load_series(V4), "v4") is None, "the rebased overlay is one continuous clock"


def test_no_committed_line_object_warns():
    for path in OBJECTS:
        s = L.load_series(path)
        if (L.infer_variant(s) or "line") != "line" or L.validate(s, "line"):
            continue
        assert L.era_void_warning(s, path.stem) is None, path.name


def _world(**over) -> dict:
    page = B.stamp_full_stage(L.build_spec(_page(**over), "line"))
    return {"kind": "ledger", "page": page}


def test_the_compiler_refuses_a_chart_state_change_on_a_broken_axis():
    for to in ("rescale", "extend", "recast", "morph"):
        sp = [{"kind": "chart_to", "at": 5.0, "dur": 1.0, "to": to}]
        with pytest.raises(ValueError, match="E99 s111"):
            B.check_broken_axis(_world(), sp)
    B.check_broken_axis(_world(), [{"kind": "build_to", "at": 5.0, "dur": 1.0, "series": 0,
                                    "target": {"kind": "datum", "index": 20}}])


def test_the_compiler_refuses_a_form_on_a_broken_axis():
    world = _world()
    world["page"]["form"] = {"kind": "tilted_line"}
    with pytest.raises(ValueError, match="form"):
        B.check_broken_axis(world, [])


def test_a_broken_axis_is_a_16x9_page():
    """Read in the frame: at 9:16 the plot is too narrow for both eras' dates and the written gap, the era's name runs
    past its stretch, and the portrait end tag stands over a line that ends mid-plot - refused by name, not shipped."""
    saved = B.ASPECT
    try:
        B.ASPECT = "9:16"
        with pytest.raises(ValueError, match="16:9"):
            B.check_broken_axis(_world(), [])
        B.ASPECT = "16:9"
        B.check_broken_axis(_world(), [])
    finally:
        B.ASPECT = saved


def test_a_page_without_a_break_passes_the_compiler_check_untouched():
    s = _page()
    for k in ("break", "claim"):
        s.pop(k)
    world = {"kind": "ledger", "page": L.build_spec(s, "line")}
    B.check_broken_axis(world, [{"kind": "chart_to", "at": 5.0, "dur": 1.0, "to": "rescale"}])


# ---- the frame ---------------------------------------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


PROBE = """t => {
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp;
  const S = (st.states && st.states[st.active | 0]) || st, K = S.brk;
  const bb = (e) => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; };
  const op = (e) => { let o = 1; for (let n = e; n && n.getAttribute; n = n.parentNode) { const a = n.getAttribute('opacity');
    if (a != null) o *= +a; if (n.style && n.style.opacity !== '') o *= +n.style.opacity; } return o; };
  const ticks = (S.marks || []).filter(m => m.role === 'xtick' && m.el && m.el !== (K && K.gapEl));
  return { has: !!K, chartOp: +S.chart.style.opacity,
    after: K ? K.after : null, before: K ? K.before : null, xa: K ? K.xa : null, xb: K ? K.xb : null,
    ppy: K ? [ (K.xa - S.scale.mx(S.scale.x0)) / (K.after - S.scale.x0), (S.scale.mx(S.scale.x1) - K.xb) / (S.scale.x1 - K.before) ] : null,
    slashes: K ? K.slashes.map(e => ({ cls: e.getAttribute('class'), d: e.getAttribute('d'), op: op(e), box: bb(e) })) : [],
    gap: K ? { text: K.gapEl.textContent, op: op(K.gapEl), box: bb(K.gapEl) } : null,
    eras: K ? K.eraEls.map(e => ({ text: e.textContent, op: op(e), box: bb(e), x: +e.getAttribute('x') })) : [],
    clipped: K ? [...S.chart.querySelectorAll('line.ax, line.grid, line.hrule')].map(e => e.getAttribute('clip-path')) : [],
    ticks: ticks.map(m => ({ v: m.geom.v, text: m.el.textContent, box: bb(m.el), op: op(m.el) })),
    paths: (S.paths || []).map(pp => ({ si: pp.si, f: 1 - parseFloat(pp.p.getAttribute('stroke-dashoffset') || '0') / (pp.len || 1),
      clip: pp.p.parentNode.getAttribute ? pp.p.parentNode.getAttribute('clip-path') : null, x0: pp.pts[0][0], x1: pp.pts[pp.pts.length - 1][0] })),
    stage: bb(document.getElementById('stage')) };
}"""


def _player(surface: str = SURFACE, aspect: str | None = None, mutate=None):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, asp = RB.load_surface(surface)
    if mutate:
        tl = mutate(copy.deepcopy(tl))
    if aspect:
        tl = dict(tl, aspect=aspect)
    asp = aspect or asp
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "brk.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[asp]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return page, close


def _at(page, t: float) -> dict:
    page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    return page.evaluate(PROBE, t)


def _apart(a: list, b: list) -> bool:
    return a[0] + a[2] <= b[0] + 0.5 or b[0] + b[2] <= a[0] + 0.5 or a[1] + a[3] <= b[1] + 0.5 or b[1] + b[3] <= a[1] + 0.5


def _drawn(d: dict) -> None:
    assert d["has"] and d["chartOp"] == 1
    assert d["gap"]["text"] == "2001 // 2021" and d["gap"]["op"] >= 0.99
    assert [e["text"] for e in d["eras"]] == ["DOT-COM ERA", "AI ERA"] and min(e["op"] for e in d["eras"]) >= 0.99
    assert len(d["slashes"]) == 2 and min(s["op"] for s in d["slashes"]) >= 0.99
    assert all("ax" in s["cls"].split() for s in d["slashes"]), "the // is drawn in the AXIS's own ink"
    for s in d["slashes"]:
        cx = s["box"][0] + s["box"][2] / 2
        assert d["gap"]["box"][0] <= cx <= d["gap"]["box"][0] + d["gap"]["box"][2], "the // stands over the written gap"


@needs_browser
def test_the_break_is_drawn_and_both_eras_are_labelled():
    G = _golden()
    page, close = _player()
    try:
        d = _at(page, G.FRAME_T[SURFACE])
        _drawn(d)
        assert d["after"] == pytest.approx(2001.9692) and d["before"] == pytest.approx(2021.0082)
        assert d["clipped"] and all(c for c in d["clipped"]), "no axis, gridline or rule runs through the gap"
        era1 = [t for t in d["ticks"] if t["v"] <= d["after"] and t["op"] > 0.5]
        era2 = [t for t in d["ticks"] if t["v"] >= d["before"] and t["op"] > 0.5]
        assert era1 and era2, "both eras print their own dates at their ticks"
        for t in d["ticks"]:
            assert _apart(t["box"], d["gap"]["box"]), ("no tick is written over the gap's label", t["text"])
        e1, e2 = d["eras"]
        assert e1["box"][0] + e1["box"][2] <= d["gap"]["box"][0] + d["gap"]["box"][2] / 2 <= e2["box"][0], \
            "each era's name stands over its own stretch"
    finally:
        close()


@needs_browser
def test_both_stretches_share_one_years_per_pixel():
    G = _golden()
    page, close = _player()
    try:
        d = _at(page, G.FRAME_T[SURFACE])
        a, b = d["ppy"]
        assert a == pytest.approx(b, rel=1e-9), "a year is the same width in both eras"
        assert d["xb"] - d["xa"] > 0, "the gap is a drawn width, not a point"
    finally:
        close()


@needs_browser
def test_the_break_is_visible_at_every_instant_the_axis_is():
    G = _golden()
    page, close = _player()
    try:
        for t in (G.BROKEN_BUILD_T0 + 0.2, G.BROKEN_BUILD_T0 + 1.5, G.FRAME_T[SURFACE], G.FRAME_T[SURFACE] + 2.0):
            d = _at(page, t)
            if d["chartOp"] == 1:
                _drawn(d)
    finally:
        close()


@needs_browser
def test_the_lines_clock_draws_era_by_era():
    G = _golden()
    page, close = _player()
    try:
        # u 0.125 of a series' own window: the build's expoOut has the line ~0.58 drawn (page-build-lines' measure)
        d = _at(page, G.BROKEN_BUILD_T0 + G.BROKEN_SERIES_S * 0.125)
        f = {p["si"]: p["f"] for p in d["paths"]}
        assert 0.02 < f[0] < 0.99 and f[1] < 0.01, ("the first era draws while the second waits", f)
        d = _at(page, G.BROKEN_BUILD_T0 + G.BROKEN_SERIES_S * 1.125)
        f = {p["si"]: p["f"] for p in d["paths"]}
        assert f[0] > 0.99 and 0.01 < f[1] < 0.99, ("the second era draws after the first has landed", f)
    finally:
        close()


def _joined(tl: dict) -> dict:
    """The same page as ONE series across both eras - the line must lift at the break and resume."""
    page = tl["scenes"][0]["world"]["page"]
    a, b = page["series"]
    page["series"] = [dict(a, pts=a["pts"] + b["pts"], label=b["label"])]
    page["labels"] = [page["labels"][0]]
    page.pop("build", None)
    return tl


@needs_browser
def test_one_line_across_both_eras_lifts_at_the_break_and_resumes():
    G = _golden()
    page, close = _player(mutate=_joined)
    try:
        d = _at(page, G.FRAME_T[SURFACE])
        _drawn(d)
        (p,) = d["paths"]
        assert p["clip"], "the one line is held out of the gap by the break's clip"
        # the pixels: the stretch between the eras carries no ink of the line's own colour, from the plot's top down to
        # the `//` (which is the axis's grey, drawn across the axis line)
        box = page.evaluate("""() => { const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
          const S = w.__lp, K = S.brk, m = S.chart.getScreenCTM(), st = document.getElementById('stage').getBoundingClientRect();
          const x = (v) => m.a * v + m.e - st.x, y = (v) => m.d * v + m.f - st.y;
          const ink = getComputedStyle(S.paths[0].p).stroke.match(/[0-9.]+/g).slice(0, 3).map(Number);
          const top = K.slashes.map(e => e.getBoundingClientRect().top - st.y).reduce((a, b) => Math.min(a, b));
          return { box: [x(K.xa) + 3, y(S.plot.T), x(K.xb) - x(K.xa) - 6, top - 3 - y(S.plot.T)], ink }; }""")
        png = page.locator("#stage").screenshot()
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(png)).convert("RGB")
        x0, y0, w, h = (int(round(v)) for v in box["box"])
        ink = box["ink"]
        assert w > 10 and h > 100, box
        hot = sum(1 for xx in range(x0, x0 + w) for yy in range(y0, y0 + h)
                  if sum(abs(a - b) for a, b in zip(im.getpixel((xx, yy)), ink)) < 90)
        assert hot == 0, f"{hot} px of the line's own ink {ink} inside the gap"
    finally:
        close()


@needs_browser
def test_the_break_is_a_function_of_t():
    G = _golden()
    page, close = _player()
    try:
        t = G.FRAME_T[SURFACE] - 1.0
        a = _at(page, t)
        _at(page, 1.0)
        b = _at(page, t)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    finally:
        close()


@needs_browser
def test_a_phone_reads_the_break():
    """16:9 on a 390 px-wide phone: the gap's years and the eras' names are written as large as the page's own dates
    (the tick labels are the floor the page already reads at; the break never writes smaller than the axis it cuts)."""
    G = _golden()
    page, close = _player()
    try:
        d = _at(page, G.FRAME_T[SURFACE])
        k = 390 / d["stage"][2]
        tick_h = min(t["box"][3] for t in d["ticks"] if t["op"] > 0.5) * k
        assert tick_h > 0
        assert d["gap"]["box"][3] * k >= tick_h - 0.01, (d["gap"], tick_h)
        assert min(e["box"][3] for e in d["eras"]) * k >= tick_h - 0.01, (d["eras"], tick_h)
    finally:
        close()
