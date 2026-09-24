"""P69 T48 - THE PIE AND THE DONUT, FLAT OR 3D EXPLODED, AND THE PUSH ONTO THE LARGEST SLICE (E99 s109 (4) + amendment).

The operator, 2026-09-23: "donuts and pies, including an extruded or exploded one, are valid when WE draw them from
honest data: slice angles true to the values, the figures written, and the depth and the camera free to serve the
story" - AMENDED: "maybe a 3d pie chart exploded and then zoomed onto the largest portion when discussing NVDA's
market share of AI ... as long as it's created accurately that can be part of the story".

REUSED, not rebuilt: the `share` builder (P48 T4) is the page; a share page that names none of the new options draws
the pie it always drew. The new options live on the same object: `hole` (a donut), `extrude` (a 2.5D projection of
the TRUE-ANGLE slices: a tilt and a depth, the side shaded by the ONE stage light and, on `hatch`, T6b's engraving),
`explode` (which slice leaves the whole; the `explode` page species says WHEN, as `peel` does for the piece that
leaves). T26f's free camera is the push: a camera key whose `look` is a `datum` on a share page aims at that SLICE's
centroid as drawn, and while it pushes the other slices recede.

HONESTY (s100's two tests, s109 (4)): the angles are the data's - value / sum x 360, whatever the tilt; the figure is
WRITTEN on every slice, so the number, not the area, is the claim; the shares must sum to the page's `total` (within
the written figures' own rounding), and a remainder is refused by naming it as the slice the author owes ("Other").
A tilt makes the near slices look bigger: `pie_area_lie` measures the worst apparent-area factor of a tilt and a
depth, the default stays inside what a written figure carries, and a steeper page is REPORTED with its number.

The page under test is the registered DRAM market-share slide (silicon-silent-triopoly s08: Samsung 39 %, SK hynix
26 %, Micron 25 %, CXMT 7 %) - 97 of 100, so the check names the 3 % the page owes, and the golden draws it as
"Other" (the remainder the check named, never a figure invented).
"""
from __future__ import annotations

import json
import math
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

REGISTRATION = ROOT / "content/video_engine/projects/systems-and-blowups/registration/registration.silicon-silent-triopoly.json"
SLIDE = "silicon-silent-triopoly-s08"
MAKERS = (("Samsung", 39), ("SK hynix", 26), ("Micron", 25), ("CXMT", 7))


def _golden():
    import build_golden_sources as G
    return G


def _slide_figures() -> dict:
    reg = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    slide = next(s for s in reg["slides"] if s.get("slide_id") == SLIDE)
    return {f["label"]: f["value"] for f in slide["figures"]}


def _four() -> dict:
    """The slide's four makers, as a share object - 97 of the whole 100."""
    return {"title": "Who makes the world's DRAM", "src": "silicon-silent-triopoly deck, slide 8", "unit": "%",
            "total": 100, "emphasize": 0,
            "shares": [{"label": n, "value": v, "value_string": f"{v}%"} for n, v in MAKERS]}


def _solid(**over) -> dict:
    s = _golden().pie_series()
    s.update(over)
    return s


# ---- the data: the registered figures, and the remainder the check names ---------------------------------------------


def test_the_page_is_the_registered_slides_own_figures():
    figs = _slide_figures()
    for name, v in MAKERS:
        assert figs[f"{name} DRAM market share"] == f"{v}%", name
    s = _golden().pie_series()
    assert [(x["label"], x["value"]) for x in s["shares"][:4]] == list(MAKERS)
    other = s["shares"][4]
    assert other["label"] == "Other" and other["value"] == 100 - sum(v for _, v in MAKERS), \
        "the fifth slice is exactly the remainder the check names - never an invented figure"


def test_shares_that_do_not_sum_to_their_whole_are_refused_and_the_remainder_is_named():
    errs = L.validate(dict(_four(), extrude=True), "share")
    assert any("97" in e and "100" in e and "3" in e and "Other" in e for e in errs), errs
    over = _four()
    over["shares"] = over["shares"] + [{"label": "Other", "value": 9, "value_string": "9%"}]
    errs = L.validate(dict(over, extrude=True), "share")
    assert any("more than" in e and "106" in e for e in errs), errs


def test_the_written_figures_own_rounding_is_not_a_missing_slice():
    """Three thirds written as 33 % each sum to 99: that is the figures' rounding (+-0.5 each), not a slice owed."""
    s = {"title": "t", "src": "s", "unit": "%", "total": 100, "emphasize": 0, "extrude": True,
         "shares": [{"label": n, "value": 33, "value_string": "33%"} for n in ("A", "B", "C")]}
    assert L.validate(s, "share") == []


def test_a_solid_page_declares_its_whole():
    s = _solid()
    s.pop("total")
    assert any("total" in e for e in L.validate(s, "share"))


# ---- the grammar: the share options, carried onto the spec ------------------------------------------------------------


def test_extrude_explode_and_hole_are_share_options_carried_onto_the_spec():
    spec = L.build_spec(_solid(hole=0.5), "share")
    assert spec["builder"] == "share"
    assert spec["hole"] == 0.5
    assert spec["extrude"] == {"tilt": L.PIE_TILT_DEG, "depth": L.PIE_DEPTH, "hatch": True}
    assert spec["explode"] == {"index": 0, "out": L.PIE_EXPLODE_OUT}
    assert spec["total"] == 100


def test_true_is_the_default_of_each_option():
    spec = L.build_spec(_solid(extrude=True, explode=True), "share")
    assert spec["extrude"] == {"tilt": L.PIE_TILT_DEG, "depth": L.PIE_DEPTH, "hatch": False}
    assert spec["explode"] == {"index": spec["emphasize"], "out": L.PIE_EXPLODE_OUT}


def test_every_slice_writes_its_figure_on_a_solid_page():
    spec = L.build_spec(_solid(), "share")
    assert spec["value_strings"] == ["39%", "26%", "25%", "7%", "3%"]
    s = _solid()
    s["shares"] = [dict(x) for x in s["shares"]]
    del s["shares"][3]["value_string"]
    assert L.build_spec(s, "share")["value_strings"][3] == "7%", "a slice with no string is written as its value and unit"


def test_a_solid_page_needs_no_peel():
    assert "peel" not in _solid()
    assert L.validate(_solid(), "share") == []
    assert L.infer_variant(_solid()) == "share", "a shares object naming a solid option is a share page, not a census"


@pytest.mark.parametrize("over, needle", [
    ({"extrude": {"tilt": 80}}, "extrude.tilt"),
    ({"extrude": {"depth": 0.9}}, "extrude.depth"),
    ({"extrude": {"zoom": 2}}, "extrude: unknown"),
    ({"extrude": "yes"}, "extrude must be"),
    ({"explode": {"index": 9}}, "explode.index"),
    ({"explode": {"out": 0.8}}, "explode.out"),
    ({"explode": {"slice": 0}}, "explode: unknown"),
    ({"hole": 0.95}, "hole"),
    ({"peel": {"index": 0, "value": -3, "value_string": "-3%"}}, "peel"),
])
def test_a_malformed_option_is_refused_by_name(over, needle):
    errs = L.validate(_solid(**over), "share")
    assert any(needle in e for e in errs), (needle, errs)


def test_an_existing_share_page_carries_none_of_the_new_keys():
    """Byte-identity at the spec: the Tokyo pie (P48 T4) names no new option and gains no key."""
    import test_share_page as TS
    spec = L.build_spec(TS._series(), "share")
    assert not {"hole", "extrude", "explode", "total", "warnings"} & set(spec), sorted(spec)


# ---- the honesty measure: what a tilt does to the apparent areas ------------------------------------------------------


def test_the_default_tilt_keeps_the_apparent_area_inside_what_a_figure_carries():
    lie = L.pie_area_lie(L.PIE_TILT_DEG, L.PIE_DEPTH)
    assert 1.0 < lie <= L.PIE_AREA_LIE_MAX, lie
    assert L.pie_area_lie(0, L.PIE_DEPTH) == pytest.approx(1.0), "face-on, the areas are the shares"
    assert L.pie_area_lie(L.PIE_TILT_DEG, 0) == pytest.approx(1.0), "a tilt with no depth scales every area alike"


def test_the_measure_is_the_analytic_rim_over_the_whole():
    """A thin slice at six o'clock gains the most: its top shrinks with every other top (cos tilt), and it owns a
    strip of the rim 2 R sin(pi p) wide; as p -> 0 the factor is (1 + 2 d tan) / (1 + 2 d tan / pi)."""
    t, d = 50.0, 0.12
    q = 2 * d * math.tan(math.radians(t))
    assert L.pie_area_lie(t, d) == pytest.approx(max((1 + q) / (1 + q / math.pi), 1 + q / math.pi), rel=1e-6)


def test_a_steep_page_is_reported_with_its_number_not_refused():
    spec = L.build_spec(_solid(extrude={"tilt": 60, "depth": 0.28}), "share")
    ws = spec.get("warnings") or []
    assert any("apparent area" in w and "60" in w for w in ws), ws
    assert L.validate(_solid(extrude={"tilt": 60, "depth": 0.28}), "share") == [], "s106: the engine advises"


# ---- the species and the camera grammar --------------------------------------------------------------------------------


def test_explode_is_a_page_species_that_says_only_when():
    assert "explode" in B.SPECIES_KINDS and "explode" in B.PAGE_SPECIES
    assert B.SPECIES_TARGETS["explode"] == ()
    assert B.SPECIES_WHEN["explode"]
    assert B.validate_species([{"kind": "explode", "at": 9.0, "dur": 0.8}], (0, 0, 0), "ledger:x:share") == []


def test_a_camera_key_names_a_slice_and_the_compiler_bounds_it_to_the_page():
    world = {"kind": "ledger", "page": L.build_spec(_solid(), "share")}
    cam = _golden().pie_push_camera()
    assert B.validate_camera(cam, "ledger:x:share", "16:9") == []
    assert B.share_slice_errors(world, cam, "ledger:x:share") == []
    bad = json.loads(json.dumps(cam))
    bad["keys"][-1]["look"]["index"] = 5
    errs = B.share_slice_errors(world, bad, "ledger:x:share")
    assert errs and "slice" in errs[0] and "5" in errs[0], errs


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
  const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger')); const st = w.__lp, S = st.share;
  const bb = (e) => { const r = e.getBBox(); return [r.x, r.y, r.width, r.height]; };
  const vis = (e) => +(e.getAttribute('opacity') ?? 1);
  return { solid: !!S.solid, cx: S.cx, cy: S.cy, R: S.R, c: S.c, h: S.h, rho: S.rho,
    cam: window.__camera ? window.__camera(t) : null,
    centroid: (() => { const c = window.__camera(t, { kind: 'datum', index: 0 });
                       return c && c.target ? [c.target.box.x + c.target.box.w / 2, c.target.box.y + c.target.box.h / 2] : null; })(),
    wedges: S.wedges.map(x => ({ i: x.i, a0: x.a0, a1: x.a1, name: x.lab.textContent, fig: x.val ? x.val.textContent : null,
      op: vis(x.lab), gop: x.g ? +(x.g.getAttribute('opacity') ?? 1) : 1, off: x.off ? [x.off[0], x.off[1]] : [0, 0],
      box: bb(x.lab), vbox: x.val ? bb(x.val) : null, faces: x.faces ? x.faces.filter(f => f.el.getAttribute('d')).length : 0 })),
    hatch: S.hatch ? S.hatch.length : 0, apparent: S.apparent || null };
}"""


def _player(surface: str, aspect: str | None = None):
    from playwright.sync_api import sync_playwright
    tl, uris, _t, asp = RB.load_surface(surface)
    if aspect:
        tl = dict(tl, aspect=aspect)
    asp = aspect or asp
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "pie.html"
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


def _apart(a: list, b: list, what: str) -> None:
    assert (a[0] + a[2] <= b[0] + 1 or b[0] + b[2] <= a[0] + 1
            or a[1] + a[3] <= b[1] + 1 or b[1] + b[3] <= a[1] + 1), what


def _true_angles(d: dict) -> None:
    vals = [v for _, v in MAKERS] + [3]
    for w in d["wedges"]:
        assert w["a1"] - w["a0"] == pytest.approx(vals[w["i"]] / sum(vals) * 2 * math.pi, abs=1e-9), \
            ("the slice's ANGLE is its share of the whole, whatever the tilt", w["name"])


def _labels_readable(d: dict) -> None:
    boxes = []
    for w in d["wedges"]:
        assert w["op"] >= 0.99 and w["fig"], ("every slice's figure is written", w["name"], w["fig"], w["op"])
        boxes += [(w["name"], w["box"]), (w["name"] + " figure", w["vbox"])]
    for i in range(len(boxes)):
        for j in range(i + 2 - (i % 2), len(boxes)):
            _apart(boxes[i][1], boxes[j][1], "%s overprints %s" % (boxes[i][0], boxes[j][0]))


@needs_browser
def test_the_flat_donut_draws_true_angles_with_every_figure_written():
    G = _golden()
    page, close = _player("share-donut-flat")
    try:
        d = _at(page, G.FRAME_T["share-donut-flat"])
        assert d["solid"] and d["rho"] == pytest.approx(G.PIE_HOLE) and d["c"] == pytest.approx(1.0) and d["h"] == 0
        _true_angles(d)
        _labels_readable(d)
        assert [w["fig"] for w in sorted(d["wedges"], key=lambda w: w["i"])] == ["39%", "26%", "25%", "7%", "3%"]
    finally:
        close()


@needs_browser
def test_the_3d_pie_explodes_its_slice_on_its_word_and_keeps_the_true_angles():
    G = _golden()
    page, close = _player("share-pie-3d")
    try:
        before = _at(page, G.PIE_EXPLODE_AT - 0.2)
        assert before["c"] < 1 and before["h"] > 0, "a tilted, extruded pie"
        assert all(w["off"] == [0, 0] for w in before["wedges"]), "nothing has left the whole before its word"
        d = _at(page, G.FRAME_T["share-pie-3d"])
        _true_angles(d)
        _labels_readable(d)
        big = next(w for w in d["wedges"] if w["i"] == 0)
        mid = (big["a0"] + big["a1"]) / 2
        out = L.build_spec(G.pie_series(), "share")["explode"]["out"]
        want = (out * d["R"] * math.sin(mid), -out * d["R"] * math.cos(mid) * d["c"])
        assert big["off"] == pytest.approx(list(want), abs=0.05), "the slice leaves along its own bisector, in the plane"
        assert all(w["off"] == [0, 0] for w in d["wedges"] if w["i"] != 0)
        assert any(w["faces"] for w in d["wedges"]), "the extrusion's sides are drawn"
        assert d["hatch"] > 0, "the sides away from the one light carry T6b's hatch"
    finally:
        close()


@needs_browser
def test_the_apparent_area_distortion_is_measured_and_inside_the_bound():
    G = _golden()
    page, close = _player("share-pie-3d")
    try:
        d = _at(page, G.FRAME_T["share-pie-3d"])
        ap = d["apparent"]
        assert ap and len(ap) == 5
        worst = max(max(a["ratio"], 1 / a["ratio"]) for a in ap)
        assert worst <= L.PIE_AREA_LIE_MAX + 0.02, ap
    finally:
        close()


@needs_browser
def test_the_camera_pushes_onto_the_largest_slice_while_the_others_recede():
    G = _golden()
    page, close = _player("share-pie-3d-push")
    try:
        rest = _at(page, G.PIE_PUSH_T0 - 0.1)
        assert rest["cam"]["zoom"] == pytest.approx(1.0, abs=1e-6)
        assert all(w["gop"] == pytest.approx(1.0) for w in rest["wedges"]), "nothing recedes before the push"
        held = _at(page, G.FRAME_T["share-pie-3d-push"])
        assert held["cam"]["zoom"] == pytest.approx(G.PIE_PUSH_ZOOM, abs=1e-4)
        assert held["cam"]["look"] == pytest.approx(held["centroid"], abs=0.5), "the look is the slice's centroid as drawn"
        big = max(held["wedges"], key=lambda w: w["a1"] - w["a0"])
        assert big["i"] == 0 and big["gop"] == pytest.approx(1.0), "the largest slice is the one pushed onto"
        assert all(w["gop"] < 0.5 for w in held["wedges"] if w["i"] != 0), "the others recede"
    finally:
        close()


@needs_browser
def test_the_pie_is_a_function_of_t():
    """Seek purity: the explode, the push and the recession land the identical state on a seek back."""
    G = _golden()
    page, close = _player("share-pie-3d-push")
    try:
        t = G.FRAME_T["share-pie-3d-push"] - 0.4
        a = _at(page, t)
        _at(page, 2.0)
        b = _at(page, t)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    finally:
        close()


@needs_browser
def test_a_phone_reads_every_figure():
    """9:16, the stage a 390 px phone shows at 390 / 1080 of its size: every figure stays at or over the page's floor."""
    G = _golden()
    page, close = _player("share-pie-3d", "9:16")
    try:
        d = _at(page, G.FRAME_T["share-pie-3d"])
        _true_angles(d)
        _labels_readable(d)
        px = page.evaluate("""() => { const w = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
            return w.__lp.share.wedges.map(x => x.val.getBoundingClientRect().height); }""")
        assert min(px) * 390 / 1080 >= 9.0, px
    finally:
        close()
