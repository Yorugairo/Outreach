"""P71 T39 (was P69 T46 (3); E99 s125) - THE SHAPE MEETS THE DATA: a real series laid over a schematic.

P70 T2's schematic draws a named shape with no data (s109 (1)). s125 lets a MEASURED series join it, on four conditions,
all truth rules (hard refusals, by name):
  (1) a real series may be laid over a schematic on its word;
  (2) the series keeps ITS OWN real, labelled axis (dates and values) and is never rescaled or stretched to hug the
      curve - a series fitted to a shape claims a fit the data never showed;
  (3) the schematic keeps its "shape" tag, so the page reads as two kinds of thing, a drawn shape and a measured line;
  (4) where the series sits on the shape is the script's CLAIM and the page draws it as one - a marker or ring with the
      claim's words - never implied by alignment alone.
The schematic object carries `overlay: {series: {name?, pts, src, tier?, color?}, axis: {unit, label}, xticks?, at,
dur?, claim: {at, x, text}}`; `overlay` is the ONE sanctioned way a measured line joins a shape (P70 T2's refusal of
`series` beside `schematic` stands). A page with no overlay compiles, draws and measures as it did.
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

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards"
RAIL = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-railway-index-v1.series.json"
SURFACE = "schematic-meets-the-data"


def _rail() -> dict:
    return json.loads(RAIL.read_text(encoding="utf-8"))


def _overlay(**kw) -> dict:
    rail = _rail()
    ov = {"series": {"name": "Railway shares", "pts": rail["series"][0]["pts"], "src": rail["src"], "tier": "CONFIRMED"},
          "axis": {"unit": "pts", "label": "Railway share index"}, "xticks": rail["xticks"], "at": 8.0, "dur": 2.4,
          "claim": {"at": 11.0, "x": 0.4, "text": "then crashed by nearly two-thirds"}}
    ov.update(kw)
    return ov


def _hype(ov: dict | None = None, **top) -> dict:
    obj = {"title": "The hype cycle", "src": "Shape: Gartner's hype cycle - a schematic, no data", "ylabel": "Expectations",
           "schematic": {"shape": "hype", "phases": [{"name": "Peak", "from": 0.12, "to": 0.3},
                                                     {"name": "Trough", "from": 0.3, "to": 0.48},
                                                     {"name": "Plateau", "from": 0.72, "to": 1.0}]}}
    if ov is not None:
        obj["schematic"]["overlay"] = ov
    obj.update(top)
    return obj


def _spec(obj: dict) -> dict:
    return LPG.build_spec(obj, "line", None, "right")


def _errs(obj: dict) -> str:
    return " | ".join(LPG.validate(obj, "line"))


# ---- (1) the overlay joins the shape: validated, carried by the spec ---------------------------------------------------


def test_a_schematic_takes_a_measured_overlay():
    """The expected RED: `overlay` is not a schematic key at the base (refused as unknown)."""
    obj = _hype(_overlay())
    assert LPG.validate(obj, "line") == []
    spec = _spec(obj)
    ov = spec["schematic"]["overlay"]
    rail = _rail()
    assert ov["series"]["pts"] == [[float(x), float(v)] for x, v in rail["series"][0]["pts"]], "the data verbatim, as numbers"
    assert ov["series"]["name"] == "Railway shares" and ov["series"]["color"] in LPG.SCHEMATIC_INKS
    assert ov["series"]["color"] != LPG.SCHEMATIC_INK, "s125 (3): the measured line never wears the shape's ink"
    assert ov["axis"] == {"unit": "pts", "label": "Railway share index", "header": "Railway share index (pts)"}
    assert ov["xticks"] == [[float(x), str(lab)] for x, lab in rail["xticks"]]
    assert (ov["at"], ov["dur"]) == (8.0, 2.4)
    assert ov["claim"] == {"at": 11.0, "x": 0.4, "text": "then crashed by nearly two-thirds"}
    assert spec["series"] == [LPG.schematic_series(obj["schematic"])], "the shape is the page's one series, unchanged"
    assert spec["schematic"]["tag"] == LPG.SCHEMATIC_TAG, "s125 (3): the tag stays"
    assert rail["src"] in spec["source"] and obj["src"] in spec["source"], "the source line names the measured series"


def test_the_overlay_names_its_dates_when_the_author_does_not():
    ov = _overlay()
    ov.pop("xticks")
    spec = _spec(_hype(ov))
    ticks = spec["schematic"]["overlay"]["xticks"]
    pts = _rail()["series"][0]["pts"]
    assert [t[0] for t in ticks] == [float(pts[0][0]), float(pts[-1][0])], "its own first and last date - a range"
    assert all(t[1] for t in ticks) and ticks[0][1] != ticks[1][1]


def test_the_overlay_ink_defaults_off_the_shape_and_a_shared_ink_is_refused():
    ov = _overlay()
    ov["series"] = dict(ov["series"], color="teal")
    msg = _errs(_hype(ov))
    assert "s125 (3)" in msg and "two kinds of thing" in msg, msg
    sch = _hype(_overlay())
    sch["schematic"]["color"] = "crimson"
    got = _spec(sch)["schematic"]["overlay"]["series"]["color"]
    assert got not in ("crimson",) and got in LPG.SCHEMATIC_INKS


# ---- (2) its own labelled axis, never fitted ------------------------------------------------------------------------------


@pytest.mark.parametrize("axis", [{"label": "Railway share index"}, {"unit": "pts"}, {"unit": " ", "label": "x"},
                                  {"unit": "pts", "label": ""}, None])
def test_an_overlay_without_its_labelled_axis_is_refused(axis):
    ov = _overlay(axis=axis) if axis is not None else {k: v for k, v in _overlay().items() if k != "axis"}
    msg = _errs(_hype(ov))
    assert "a series over a schematic keeps its own labelled axis" in msg and "s125 (2)" in msg, msg


@pytest.mark.parametrize("where", ["overlay", "axis", "series"])
@pytest.mark.parametrize("key", ["domain", "y_domain", "scale", "fit", "align", "stretch"])
def test_an_overlay_fitted_to_the_curve_is_refused(where, key):
    ov = _overlay()
    target = ov if where == "overlay" else ov[where]
    target[key] = [0, 1] if "domain" in key else True
    msg = _errs(_hype(ov))
    assert "never rescaled to hug the curve" in msg and "s125 (2)" in msg and repr(key) in msg, msg


# ---- (4) where it sits is a claim, drawn with its words ------------------------------------------------------------------


@pytest.mark.parametrize("claim", [None, {"at": 11.0, "x": 0.4}, {"at": 11.0, "x": 0.4, "text": ""},
                                   {"at": 11.0, "x": 0.4, "text": "   "}, {"at": 11.0, "x": 0.4, "text": 7}])
def test_an_overlay_without_its_claim_is_refused(claim):
    ov = _overlay(claim=claim) if claim is not None else {k: v for k, v in _overlay().items() if k != "claim"}
    msg = _errs(_hype(ov))
    assert "where it sits is a claim, drawn with its words" in msg and "s125 (4)" in msg, msg


# ---- every key refused BY NAME when malformed or misplaced (R26-307, s106) ------------------------------------------------


@pytest.mark.parametrize("patch,needle", [
    (lambda ov: ov.update(glow=True), "'glow' is not an overlay key"),
    (lambda ov: ov["axis"].update(side="left"), "'side' is not an overlay axis key"),
    (lambda ov: ov["claim"].update(ring=True), "'ring' is not an overlay claim key"),
    (lambda ov: ov["series"].update(label="741"), "'label' is not an overlay series key"),
    (lambda ov: ov.update(series=[1, 2]), "overlay: series must be an object"),
    (lambda ov: ov["series"].update(pts=[[1843, 1000]]), "at least 2 [date, value] points"),
    (lambda ov: ov["series"].update(pts=[[1843, 1000], [1843, 1100]]), "its dates must rise"),
    (lambda ov: ov["series"].update(pts=[[1843, 1000], [1844, "high"]]), "at least 2 [date, value] points"),
    (lambda ov: ov["series"].pop("src"), "overlay: series needs its src"),
    (lambda ov: ov["series"].update(tier="scenario"), "tier must be one of"),
    (lambda ov: ov["series"].update(color="gold"), "color must be one of"),
    (lambda ov: ov["claim"].update(x=1.4), "claim: x must be an x-fraction of the shape (0..1)"),
    (lambda ov: ov["claim"].update(x=True), "claim: x must be an x-fraction of the shape (0..1)"),
    (lambda ov: ov["claim"].update(at="soon"), "claim: at must be"),
    (lambda ov: ov.pop("at"), "overlay: at must be"),
    (lambda ov: ov.update(dur=0), "overlay: dur must be"),
    (lambda ov: ov.update(xticks=[[1850.9, "1851"]]), "xticks"),
    (lambda ov: ov.update(xticks="1844"), "xticks"),
    (lambda ov: ov.update(axis="pts"), "overlay: axis must be an object"),
])
def test_a_malformed_overlay_is_refused_by_name(patch, needle):
    ov = _overlay()
    ov["series"] = dict(ov["series"])
    ov["axis"] = dict(ov["axis"])
    ov["claim"] = dict(ov["claim"])
    patch(ov)
    msg = _errs(_hype(ov))
    assert needle in msg, msg


@pytest.mark.parametrize("obj", [
    lambda: dict(_rail(), overlay=_overlay()),                     # a data page
    lambda: _hype(None, overlay=_overlay()),                       # beside a schematic, at the page's level
])
def test_a_misplaced_overlay_is_refused_by_name(obj):
    """The probe at the base: a PAGE-level `overlay` was accepted and ignored (R26-307's class)."""
    msg = _errs(obj())
    assert "overlay" in msg and "inside the schematic" in msg, msg


def test_y2_beside_a_schematic_names_the_overlay():
    obj = _hype(None, y2={"series": [0], "unit": "pts", "label": "x"}, claim="comove")
    msg = _errs(obj)
    assert "overlay" in msg, msg


# ---- (3) and the bytes: the tag stays, a page with no overlay is what it was ---------------------------------------------


def test_a_schematic_with_no_overlay_carries_nothing_new():
    import build_golden_sources as G
    for obj in (G.SCHEMATIC_OBJECT, G.CANDLES_OBJECT, G.MOTIF_OBJECT):
        spec = _spec(copy.deepcopy(obj))
        assert "overlay" not in spec["schematic"] and "overlay" not in LPG.page_ink_key(spec)
    spec = _spec(copy.deepcopy(G.SCHEMATIC_OBJECT))
    full = dict(spec, full_stage=True)
    assert LPG.measured_entry(full, "16:9") is not None, "the fixture still measures the plain schematic's ink"


def test_page_boxes_keep_the_tag_and_carry_the_right_axis_on_an_overlay_page():
    plain, over = _spec(_hype()), _spec(_hype(_overlay()))
    assert LPG.page_ink_key(plain) != LPG.page_ink_key(over), "the overlay's column moves the plot: its own ink"
    for aspect in ("16:9",):
        boxes = LPG.page_boxes(over, aspect)
        assert isinstance(boxes.get(LPG.SCHEMATIC_BOX), dict) and boxes[LPG.SCHEMATIC_BOX]["w"] > 0, "s125 (3)"
        y2 = boxes.get(LPG.Y2_BOX)
        assert isinstance(y2, dict) and y2["w"] > 0 and y2["x"] >= boxes["plot"]["x"] + boxes["plot"]["w"] - 1
        names = [n for n, _b in LPG.text_boxes(boxes)]
        assert "the schematic tag" in names and "the right axis" in names
        pb = LPG.page_boxes(plain, aspect)
        assert boxes[LPG.SCHEMATIC_BOX]["y"] == pb[LPG.SCHEMATIC_BOX]["y"], "the tag keeps its own place (under the dates)"
        assert boxes["plot"]["h"] < pb["plot"]["h"], "the plot gave up one x-tick row to the overlay's dates"


def test_the_card_names_the_overlay_and_its_ruling():
    pb = {c["id"]: c for c in json.loads((CARDS / "page_builder.json").read_text(encoding="utf-8"))["cards"]}
    card = pb["page_builder:line+schematic"]
    blob = json.dumps(card)
    assert "overlay" in [o["token"] for o in card["options"]]
    assert "E99 s125" in card["doctrine"] and "OPERATOR-RULINGS.md:3381" in blob and SURFACE in blob


def test_the_engine_draws_the_overlay_behind_the_schematic_branch_only():
    src = ENGINE.read_text(encoding="utf-8")
    line = src[src.index("const buildLedgerLine = "):src.index("const lpMarkDatum = ")]
    assert "pg.schematic.overlay ? lpOverlayPlan(" in line and "if (SCH && OV) lpOverlayDraw(" in line, \
        "the overlay is planned and drawn behind pg.schematic only"
    assert "lpY2Plan(" in src[src.index("const lpOverlayPlan"):src.index("const lpOverlayDraw")], \
        "the right axis is T13's shared plan and writer (lpY2Plan -> lpRightAxis)"
    assert "const lpBuildSchematicClaim" in src and "const lpPaintSchematicOverlay" in src


# ---- the served player ---------------------------------------------------------------------------------------------------


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
  const st = world.__lp, S = st.schematic || {}, O = S.overlay || null, PF = st.perform || {}, C = PF.schematicClaim || null;
  const op = (el) => el ? +(el.getAttribute('opacity') ?? 1) : 0;
  const norm = (c) => { const e = document.createElementNS('http://www.w3.org/2000/svg', 'text'); e.style.fill = c; return e.style.fill; };
  const vis = (el) => !!el && el.getAttribute('visibility') !== 'hidden' && getComputedStyle(el).display !== 'none'
                      && op(el) > 0.05 && +getComputedStyle(el).opacity > 0.05;
  const bb = (el) => { const b = el.getBBox(); return [b.x, b.y, b.width, b.height]; };
  const shown = [...st.page.querySelectorAll('text, .lp-ink')].filter(e => vis(e) && (e.textContent || '').trim()
                                                             && !e.closest('.lp-src'));   /* the source line cites; it draws no value */
  const shape = (st.paths || [])[0];
  const drawnF = (p, len) => 1 - (+p.getAttribute('stroke-dashoffset') || 0) / len;
  const curveY = (x) => { const pts = shape.pts; if (x <= pts[0][0]) return pts[0][1];
    for (let k = 1; k < pts.length; k++) if (x <= pts[k][0]) { const [a, ya] = pts[k - 1], [b, yb] = pts[k]; return ya + (yb - ya) * (x - a) / (b - a); }
    return pts[pts.length - 1][1]; };
  const ovEls = O ? new Set([...O.ticks.map(q => q.el), O.head, ...O.dates]) : new Set();
  const claimX = O ? st.scale.mx(O.claim.x) : null;
  return {
    plot: st.plot, viewH: +(st.chart.getAttribute('viewBox') || '0 0 0 0').split(' ')[3],
    digits: shown.filter(e => /\\d/.test(e.textContent)).map(e => ({ text: e.textContent, overlay: ovEls.has(e) })),
    tag: S.tag ? { text: S.tag.textContent, op: op(S.tag), box: bb(S.tag) } : null,
    shape: shape ? { stroke: shape.p.getAttribute('stroke'), filter: shape.p.style.filter || '', f: drawnF(shape.p, shape.len) } : null,
    phases: (S.phases || []).map(p => ({ name: p.name, box: bb(p.el) })),
    ov: O ? {
      col: norm(O.col), f: drawnF(O.p, O.len), pathOp: op(O.p), filter: O.p.style.filter || '', stroke: O.p.getAttribute('stroke'),
      pts: O.pts, data: O.data, ticks: O.ticks.map(q => ({ v: q.v, y: +q.el.getAttribute('y'), x: +q.el.getAttribute('x'), op: op(q.el),
                                                        text: q.el.textContent, fill: q.el.style.fill })),
      head: { text: O.head.textContent, op: op(O.head), fill: O.head.style.fill },
      dates: O.dates.map(e => ({ text: e.textContent, x: +e.getAttribute('x'), op: op(e), fill: e.style.fill, box: bb(e) })),
      claimX, claimY: claimX === null ? null : curveY(claimX),
    } : null,
    claim: C ? { op: op(C.g), cx: C.cx, cy: C.cy, text: [...C.text.children].map(e => e.textContent).join(' '), textOp: op(C.text), textBox: bb(C.text),
                 ringBox: [C.cx - C.r, C.cy - C.r, 2 * C.r, 2 * C.r], fill: C.text.style.fill, ring: norm(C.ring.style.stroke) } : null,
  };
}"""


def _open(tl: dict, uris: dict, aspect: str):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    return at, errs, close


def _serve(surface: str):
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface(surface)
    return _open(tl, uris, aspect)


def _overlaps(a, b) -> bool:
    return not (a[0] + a[2] <= b[0] or b[0] + b[2] <= a[0] or a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1])


@pytest.fixture(scope="module")
def served():
    import build_golden_sources as G
    at, errs, close = _serve(SURFACE)
    try:
        frames = {"before": at(G.MEETS_OVERLAY_AT - 0.2), "drawing": at(G.MEETS_OVERLAY_AT + 0.5 * G.MEETS_OVERLAY_DUR),
                  "drawn": at(G.MEETS_OVERLAY_AT + G.MEETS_OVERLAY_DUR + 0.3), "claim_before": at(G.MEETS_CLAIM_AT - 0.05),
                  "held": at(G.MEETS_CLAIM_AT + 1.0)}
    finally:
        close()
    return frames, errs


@needs_browser
def test_the_shape_draws_first_and_the_series_joins_on_its_word(served):
    f, errs = served
    assert not errs, errs
    before, drawing, drawn = f["before"], f["drawing"], f["drawn"]
    assert before["shape"]["f"] > 0.99 and before["tag"]["op"] > 0.95, "the shape and its tag stand first"
    assert before["ov"]["pathOp"] == 0 and all(t["op"] == 0 for t in before["ov"]["ticks"]) and before["ov"]["head"]["op"] == 0
    assert [d for d in before["digits"]] == [], "s109 (1): before its word the page is the shape alone - no value"
    assert 0.05 < drawing["ov"]["f"] < 0.99, "on its word the measured line draws"
    assert drawn["ov"]["f"] > 0.999 and drawn["ov"]["head"]["op"] > 0.95 and all(t["op"] > 0.95 for t in drawn["ov"]["ticks"])
    assert all(d["overlay"] for d in drawn["digits"]), ("every figure on the page is the measured series' own", drawn["digits"])


@needs_browser
def test_the_series_keeps_its_own_labelled_axis_and_is_never_fitted(served):
    f, _errs = served
    ov, plot = f["drawn"]["ov"], f["drawn"]["plot"]
    import build_golden_sources as G
    assert ov["head"]["text"] == f"{_rail()['ylabel']} ({G.MEETS_UNIT})" and ov["head"]["fill"] == ov["col"]
    assert all(t["text"].endswith(" pts") and t["fill"] == ov["col"] for t in ov["ticks"]), "each tick in its unit and ink"
    vals = [v for _x, v in ov["data"]]
    (a, b) = ov["ticks"][0], ov["ticks"][-1]
    k = (b["y"] - a["y"]) / (b["v"] - a["v"])   # the axis's own value -> y, read off its written ticks
    for (px, py), (_x, v) in zip(ov["pts"], ov["data"]):
        assert abs(py - (a["y"] - 8 + k * (v - a["v"]))) < 0.6, ("each datum on its OWN axis", v, py)
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.06
    assert abs((a["y"] - 8 + k * (lo - pad - a["v"])) - plot["B"]) < 0.6 and abs((a["y"] - 8 + k * (hi + pad - a["v"])) - plot["T"]) < 0.6, \
        "its domain is its own data's, by the page's ordinary law (6 % air) - never the shape's"
    xs = [p[0] for p in ov["pts"]]
    assert abs(xs[0] - plot["L"]) < 0.6 and abs(xs[-1] - (plot["W"] - plot["R"])) < 0.6, "its own dates across the plot"
    assert [d["text"] for d in ov["dates"]] == [str(y) for y in range(1844, 1851)]
    assert all(d["op"] > 0.95 and d["fill"] == ov["col"] for d in ov["dates"]), "its dates, in its ink, under the plot"


@needs_browser
def test_the_page_reads_as_two_kinds_of_thing(served):
    import render_baseline as RB  # noqa: F401
    f, _errs = served
    held = f["held"]
    assert held["tag"]["text"] == LPG.SCHEMATIC_TAG and held["tag"]["op"] > 0.95, "s125 (3): the tag stays"
    assert not any(_overlaps(held["tag"]["box"], d["box"]) for d in held["ov"]["dates"]), "the tag stands clear of the dates"
    assert held["tag"]["box"][1] + held["tag"]["box"][3] <= held["viewH"] + 0.5, "... and on the page"
    assert "lphot" in held["ov"]["filter"], "s117: the measured line is primary - it blooms (the hot core)"
    assert held["shape"]["filter"], "the shape keeps P70 T2's own bloom"
    assert held["ov"]["stroke"] != held["shape"]["stroke"], "two inks: a drawn shape and a measured line"


@needs_browser
def test_the_claim_is_drawn_as_one_at_its_point_with_its_words(served):
    import build_golden_sources as G
    f, _errs = served
    assert f["claim_before"]["claim"]["op"] == 0, "nothing before its word"
    c, ov = f["held"]["claim"], f["held"]["ov"]
    assert c["op"] > 0.99 and c["textOp"] > 0.95
    assert abs(c["cx"] - ov["claimX"]) < 0.6 and abs(c["cy"] - ov["claimY"]) < 0.6, "ON the shape at the claimed x"
    assert c["text"] == G.MEETS_CLAIM_TEXT
    assert not _overlaps(c["textBox"], c["ringBox"]), "C14: the words stand off the mark"
    assert not any(_overlaps(c["textBox"], p["box"]) for p in f["held"]["phases"]), "... and off the phase names"
    assert c["fill"] == ov["col"] and c["ring"] == ov["col"], "the claim wears the measured series' ink"


@needs_browser
def test_m48_reads_the_overlay_page_at_the_squint_width(tmp_path):
    import measure_line_bloom as M
    import render_baseline as RB
    from gate_motion_density import _squint_page_faults, squint_thresholds
    tl, uris, t, _aspect = RB.load_surface(SURFACE)
    (tmp_path / "player.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
    (tmp_path / f"{SURFACE}.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    doc = json.loads(M.measure_build(tmp_path, at=[t]).read_text(encoding="utf-8"))
    band, _floors = squint_thresholds()
    assert doc["pages"], doc
    for p in doc["pages"]:
        assert _squint_page_faults(p, band) == [], p


def test_the_golden_is_built_from_the_committed_objects():
    import build_golden_sources as G
    tl, _uris = G.SURFACES[SURFACE]()
    page = tl["scenes"][0]["world"]["page"]
    ov = page["schematic"]["overlay"]
    assert ov["series"]["pts"] == [[float(x), float(v)] for x, v in _rail()["series"][0]["pts"]], "read, never re-typed"
    assert ov["claim"]["x"] == G.schematic_peak_trough()[1], "the claim sits at the shape's own trough, read off the curve"
    assert re.search(re.escape(G.MEETS_CLAIM_TEXT), (ROOT / "content/video_engine/projects/systems-and-blowups/"
                     "steel-and-paper/SCRIPT-H-VO.txt").read_text(encoding="utf-8")), "the claim's words are the script's own"
