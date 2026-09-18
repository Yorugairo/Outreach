"""R26-218 - A MARK NAMES ITS SERIES, ON THE PAGE THE EYE IS LOOKING AT.

Measured on the Steel and Paper H unit (2026-09-18): a callout that named the third line rang the first one's tip, so
the unit dropped every mark that named another line. Three things were wrong, and all three were the same mistake -
asking the DOM, or a draw-order list, for something the page indexes by name:

  * `resolveTarget`'s `datum` branch read `linePts[target.series]`. `linePts` is pushed once per STROKE in draw order
    (a highlighted line's muted history is a stroke of its own, and so is every later chart state's line), and the
    ROOT state's list is the page as it was BUILT, not the page standing after a rescale, an extend or a recast.
  * every `querySelectorAll` in that branch spanned the whole world element: every state's `svg.lp-chart` plus the
    perform, morph and remake overlays. The first `.bar` could belong to the state that has not arrived yet, and the
    n-th `.ser` to another state's first line.
  * the `figure` builder read `sp.series` alone - so a figure authored the way the H unit authored its `-64%`
    (`target: {kind: "datum", series: n, index: i}`) was written at series 0's datum, and a figure that named a
    TIERS page's band by `tier` (P50 T9, the author's word) was written on the first band.

The first two are now one question asked of the page: `lpDatumNow` on the ACTIVE state, keyed by the series' own mark
(`s<si>`) and lerped across a rescale or extend - the resolution brackets and spreads have read since R26-28 - with
the index clamped to the range THAT series has (`lpSeriesRange`), which is the clamp the branch shipped with, per
series. The third is the perform layer's own rule, verbatim: `sp.series ?? sp.tier ?? sp.target.series`.

One consequence has to be paid for at BUILD time. A series the page does not have used to land on the first line;
it now resolves to nothing at all, which is the right player behaviour (P48 T2: never the wrong point) and a silent
build. So `check_target_series` refuses it by name against the page's own series count, the way `chart_to extend`
refuses a `to_index` past the last datum.

The proof is geometry, read on the served player at the instants that matter (RECALL-RECEIPT s4 - a frame is a
picture, most defects are geometry).
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

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
DIVERGENCE = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-divergence-v1.series.json"

ON_PX = 4.0     # the ring's centre sits on its datum to within this, in stage px (the ellipse is built round it)
OFF_PX = 60.0   # ... and the line it must NOT be on is at least this far away, so a pass cannot be a coincidence


# ---- the law, in the engine ---------------------------------------------------------------------------


def test_the_datum_branch_no_longer_indexes_a_draw_order_list_by_series():
    src = ENGINE.read_text(encoding="utf-8")
    branch = src[src.index('if (tg.kind === "datum")'):]
    branch = branch[:branch.index("if (tg.kind === EMBED_KIND)")]
    assert "linePts[tg.series | 0]" not in branch, "the draw-order list is not the series index (R26-218)"
    assert "lpDatumNow(lpst, tg.series | 0" in branch, "the page's own datum resolution, keyed by the series' mark"
    assert "lpSeriesRange(S0, tg.series | 0)" in branch, "and clamped to what THAT series drew"
    assert "lpst.states[lpst.active | 0]" in branch, \
        "on the ACTIVE state: a chart that rescaled or recast is the page the eye is looking at"
    assert 'chart.querySelectorAll(".bar")' in branch, "the bars of the standing state, not of every state"
    assert 'chart.querySelectorAll(".ser")' in branch, "and the same for the length-fraction fallback"


def test_lp_series_range_is_the_pages_own_index_space_and_sits_before_resolve_target():
    src = ENGINE.read_text(encoding="utf-8")
    assert src.count("const lpSeriesRange = (S, si) =>") == 1
    body = src[src.index("const lpSeriesRange = (S, si) =>"):]
    body = body[:body.index("\n  };")]
    assert "windowOffsets" in body, "a rescale's own window offsets the state's arrays from the page's indices"
    assert "geom.k0" in body, "a highlighted line's muted history counts: the tail's stroke starts at k0"
    assert src.index("const lpSeriesRange") < src.index("const resolveTarget"), \
        "the order IS the dependency in the inlined player (test_kinetics_sync's rule)"


def test_the_figure_builder_resolves_its_series_by_the_perform_layers_own_rule():
    """Not that the string exists somewhere - that it is the rule INSIDE the figure builder, and that the builder
    no longer reads `sp.series` alone. The behaviour is measured in the tiers test below."""
    src = ENGINE.read_text(encoding="utf-8")
    build = src[src.index('const figures = pageSpecies(scene, "figure")'):]
    build = build[:build.index('const notes = pageSpecies(scene, "note")')]
    assert "(st.linePts || [])[sp.series | 0]" not in build, "the species' own `series` was the only one it knew"
    assert "const fsi = (sp.series ?? sp.tier ?? (sp.target || {}).series) | 0;" in build, \
        "the perform layer's rule, verbatim - `tier` included, and an authored null falls through instead of being 0"
    assert "si: fsi" in build, "and the painter's step-off reads that one as well"
    assert "sp.series ?? sp.tier ?? (sp.target || {}).series" in src[src.index("const forMe = (sp) =>"):], \
        "the rule this copies is the perform layer's `forMe`, unchanged"


# ---- the bound, at COMPILE time ------------------------------------------------------------------------


def test_page_series_count_counts_a_line_pages_series_and_a_tiers_pages_bands():
    assert B.page_series_count({"builder": "dense-line", "series": [{}, {}, {}]}) == 3
    assert B.page_series_count({"builder": "tiers", "tiers": [{}, {}]}) == 2
    assert B.page_series_count({"builder": "combo", "tiers": True}) == 0, "the two-band combo's bool key is not a band list"
    assert B.page_series_count({"builder": "bars", "bars": [{}, {}]}) == 0, "a bars page's marks are not series: bound nothing"
    assert B.page_series_count(None) == 0


LINE3 = {"kind": "ledger", "page": {"builder": "dense-line", "series": [{}, {}, {}]}}


@pytest.mark.parametrize("sp", [
    {"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": 3, "index": 0}},
    {"kind": "callout", "at": 1.0, "target": {"kind": "datum", "series": 9, "index": 0}},
    {"kind": "figure", "at": 1.0, "series": 4, "target": {"kind": "datum", "index": 0}},
    {"kind": "figure", "at": 1.0, "tier": 7, "target": {"kind": "datum", "index": 0}},
])
def test_a_series_the_page_does_not_have_is_refused_by_name(sp):
    with pytest.raises(ValueError, match=r"past the page's last series \(2\)"):
        B.check_target_series(LINE3, [sp])


def test_a_chart_to_names_a_series_the_page_has_not_drawn_yet_and_is_not_bounded():
    """The counter-example that scoped the check: `chart_to extend {series: n, later: true}` REVEALS a series from
    the evidence object that the standing page has not drawn - its `series` is a verb argument, not an index into
    the page's marks. Bounding it refused two live `extend` cases (test_chart_transitions)."""
    assert "chart_to" not in B.SERIES_NAMING_SPECIES
    assert B.SERIES_NAMING_SPECIES == B.TIER_SPECIES + (B.SPECIES_SPAN,)
    one = {"kind": "ledger", "page": {"builder": "dense-line", "series": [{}]}}
    B.check_target_series(one, [{"kind": "chart_to", "at": 1.0, "to": "extend", "series": 1, "later": True}])
    with pytest.raises(ValueError, match=r"past the page's last series \(0\)"):
        B.check_target_series(one, [{"kind": "figure", "at": 1.0, "series": 1, "target": {"kind": "datum", "index": 0}}])


def test_the_series_the_page_does_have_passes_and_an_uncountable_page_bounds_nothing():
    for si in (0, 1, 2):
        B.check_target_series(LINE3, [{"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": si, "index": 0}}])
    bars = {"kind": "ledger", "page": {"builder": "bars", "bars": [{}, {}]}}
    B.check_target_series(bars, [{"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": 9, "index": 0}}])
    B.check_target_series({"kind": "plate"}, [{"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": 9}}])


def test_the_bound_is_the_widest_of_the_pages_chart_states():
    """A recast into a page with MORE series is not refused: the species may name a series the arriving state has."""
    world = {"kind": "ledger", "page": {"builder": "dense-line", "series": [{}]},
             "page_states": [{"builder": "dense-line", "series": [{}, {}, {}, {}]}]}
    B.check_target_series(world, [{"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": 3, "index": 0}}])
    with pytest.raises(ValueError, match=r"past the page's last series \(3\)"):
        B.check_target_series(world, [{"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": 4, "index": 0}}])


@pytest.mark.parametrize("v", [True, False, -1, "2", 1.0, None])
def test_a_series_that_is_not_a_non_negative_int_is_refused_both_places(v):
    with pytest.raises(ValueError, match="is not a non-negative integer series index"):
        B.check_target_series(LINE3, [{"kind": "ring", "at": 1.0, "target": {"kind": "datum", "series": v, "index": 0}}])
    errs = B._validate_target("ring", {"kind": "datum", "index": 0, "series": v}, ("datum",))
    assert any("non-negative integer series index" in e for e in errs), (v, errs)


def test_the_bound_runs_on_every_row_from_derive_rescale_states():
    """The wiring: the one pass that already holds the row's species AND the page it draws on."""
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    assert "check_target_series(world, row_species)" in src
    body = src[src.index("def derive_rescale_states("):]
    body = body[:body.index("\ndef ", 10)]
    assert "check_target_series(world, row_species)" in body, "inside derive_rescale_states, which the row loop wraps"


# ---- the geometry, on the served player ---------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
needs_objects = pytest.mark.skipif(not DIVERGENCE.exists(), reason="the divergence evidence object is not on disk")

# The ring's centre in stage px, and every series' last datum on BOTH the active state and the state the page was
# built in - so a failure says which page the mark landed on, not merely that it missed.
RING_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, S = (st.states && st.states[st.active | 0]) || st;
  const sb = document.getElementById('stage').getBoundingClientRect(), k = %d / sb.width;
  const sbox = (el) => { const r = el.getBoundingClientRect();
    return { x: (r.left - sb.left) * k, y: (r.top - sb.top) * k, w: r.width * k, h: r.height * k }; };
  const map = (svg, q) => { const b = sbox(svg), vb = svg.viewBox.baseVal, kk = Math.min(b.w / vb.width, b.h / vb.height);
    return { x: b.x + (b.w - vb.width * kk) / 2 + q[0] * kk, y: b.y + (b.h - vb.height * kk) / 2 + q[1] * kk }; };
  const tips = (T) => (T.linePts || []).map((a) => map(T.chart, a[a.length - 1]));
  const g = document.querySelector('#species g'), rb = g ? sbox(g) : null;
  const fg = world.querySelector('.lp-figure');
  return { active: st.active | 0, states: (st.states || []).length,
           tipsActive: tips(S), tipsBuilt: tips(st),
           bars: [...S.chart.querySelectorAll('.bar')].map(sbox),
           figure: fg && parseFloat(fg.getAttribute('opacity')) > 0 ? sbox(fg) : null,
           ring: rb ? { x: rb.x + rb.w / 2, y: rb.y + rb.h / 2 } : null };
}"""


def _serve(timeline, uris, aspect, tmp: Path | None = None):
    """Serve one instantiated timeline and return (at, errs, close) - the pattern test_chart_transitions uses.
    The probe is formatted with the aspect's own stage width: no landscape literal in the reading code either."""
    from playwright.sync_api import sync_playwright
    td = tempfile.TemporaryDirectory()
    html = Path(tmp or td.name) / "probe.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
    at_t_probe = RING_PROBE % w
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(at_t_probe)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


def _three_series(n: int = 3) -> dict:
    src = json.loads(DIVERGENCE.read_text(encoding="utf-8"))
    return dict(src, series=src["series"][:n])


def _ring_player(species, plate_then=False, runtime=30.0, n=3):
    """A THREE-series line page (the row's own case), optionally carrying a second chart state to move to."""
    src = _three_series(n)
    td = tempfile.TemporaryDirectory()
    ep = Path(td.name)
    (ep / "evidence/objects").mkdir(parents=True)
    (ep / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(src), encoding="utf-8")
    if plate_then:
        bars = {"title": "Where the three stand today", "sub": "index, 100 = Aug 2025", "src": "Yahoo Finance",
                "unit": "", "bars": [{"label": s.get("name") or ("s%d" % i),
                                      "value": round(float(s["pts"][-1][1]), 1),
                                      "color": s.get("color", "crimson")} for i, s in enumerate(src["series"])]}
        (ep / "evidence/objects/ev-bars-v1.series.json").write_text(json.dumps(bars), encoding="utf-8")
    plate = "ledger:ev-lines-v1:line" + (";then=ev-bars-v1:bars" if plate_then else "")
    tl, uris, _t, _a = RB.load_surface("ledger-soak-page")
    world = B.world_for_plate(plate, (0, 0, 0), ep)
    B.derive_rescale_states(world, species, plate, ep)
    scene = dict(tl["scenes"][0], species=species, span=[0.0, runtime],
                 world=dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}))
    timeline = dict(tl, aspect="9:16", runtime_s=runtime, scenes=[scene], caption_pages=[], captions=[])
    at, errs, close = _serve(timeline, uris, "9:16", tmp=ep)
    return at, errs, (lambda: (close(), td.cleanup()))


def _dist(a, b) -> float:
    return ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5


def _ring(at_t: float) -> dict:
    src = _three_series()
    last = len(src["series"][2]["pts"]) - 1
    return {"kind": "ring", "at": float(at_t), "dur": 2.0, "target": {"kind": "datum", "series": 2, "index": last}}


@needs_objects
@needs_browser
def test_a_ring_that_names_series_2_rings_series_2_and_not_series_0():
    """The row's own acceptance: a three-series line page, a ring on series 2's last datum. Its centre IS that
    datum, and the other two lines' tips are far away."""
    at, errs, close = _ring_player([_ring(8.0)])
    try:
        p = at(9.6)
        assert p["ring"], "the ring paints"
        tips = p["tipsActive"]
        assert len(tips) == 3, tips
        assert _dist(p["ring"], tips[2]) <= ON_PX, ("the centre is series 2's datum", p["ring"], tips)
        for si in (0, 1):
            assert _dist(p["ring"], tips[si]) >= OFF_PX, ("and not series %d's" % si, p["ring"], tips)
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_the_datum_resolves_on_the_page_standing_after_a_rescale_not_the_one_it_was_built_in():
    """The H unit's shape: the page rescales, and a mark lands after it. Before R26-218 the target was read off the
    ROOT state's points - the page as BUILT - which on a packed multi-line page is another line's neighbourhood."""
    species = [{"kind": "chart_to", "at": 8.0, "dur": 1.0, "to": "rescale", "ymin": 60, "ymax": 260}, _ring(20.0)]
    at, errs, close = _ring_player(species)
    try:
        p = at(21.0)
        assert p["states"] == 2 and p["active"] == 1, p
        assert _dist(p["ring"], p["tipsActive"][2]) <= ON_PX, ("the live page's series 2", p["ring"], p["tipsActive"])
        assert _dist(p["ring"], p["tipsBuilt"][2]) >= OFF_PX, \
            ("the built page's series 2 is somewhere else entirely - that is what the mark used to ring", p)
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_a_line_page_carrying_a_bars_state_is_never_asked_for_the_bars_that_have_not_arrived():
    """A page with a `then=` bars state builds those bars at load, hidden. `world.querySelectorAll('.lp-chart .bar')`
    found them and handed the ring a BAR of the page that is not on screen yet."""
    species = [_ring(8.0), {"kind": "chart_to", "at": 16.0, "dur": 1.8, "to": "recast", "state": 1, "keyed": True}]
    at, errs, close = _ring_player(species, plate_then=True)
    try:
        p = at(9.6)
        assert p["states"] == 2 and p["active"] == 0, p
        assert p["bars"] == [], "the standing page is the LINE page: it has no bars of its own"
        assert _dist(p["ring"], p["tipsActive"][2]) <= ON_PX, ("series 2's own tip", p["ring"], p["tipsActive"])
        assert not errs, errs
    finally:
        close()


TIER_FIG_AT, TIER_FIG_S = 6.0, 2.0
TIER_NEAR_PX = 110.0    # the hand writes the number BESIDE and ABOVE its datum (FIGURE's own gap and BASE_DY)
TIER_CLEAR_PX = 40.0    # ... and its own band's datum is the nearest one by at least this, in stage px
TIER_WRONG_PX = 150.0   # ... while the FIRST band - where the bug wrote it - is this far off at least


@needs_browser
def test_the_figure_builder_reads_the_series_its_target_names():
    """The figure half of R26-218, measured on the BUILDER: a THREE-band tiers page (the `tiers-two` golden's own
    page spec with a third band appended) and a figure that names the third band by `tier` - the author's word for
    a series index on a tiers page (P50 T9). The bands are stacked, so which band the number was written beside is
    a geometry question with a wide answer: before the fix `tier` was not read at all and the `-64%` was written on
    the FIRST band."""
    tl, uris, _t, _a = RB.load_surface("tiers-two")
    sc = copy.deepcopy(tl["scenes"][0])
    pg = sc["world"]["page"]
    third = copy.deepcopy(pg["tiers"][1])
    third["name"], third["color"] = "GERMANY", "sunflower"
    for s in third["series"]:
        s["name"], s["color"] = "GERMANY", "sunflower"
        s["pts"] = [[x, float(v) * 0.5 + 40.0] for x, v in s["pts"]]
    pg["tiers"].append(third)
    pg["labels"] = [t["name"] for t in pg["tiers"]]
    last = len(pg["tiers"][2]["series"][0]["pts"]) - 1
    fig = {"kind": "figure", "at": TIER_FIG_AT, "dur": TIER_FIG_S, "text": "-64%", "tier": 2,
           "target": {"kind": "datum", "index": last}}
    assert B._validate_page_fields("figure", fig) == [], "a figure may name a TIER (TIER_SPECIES)"
    B.check_target_series(sc["world"], [fig])   # ... and the third band is a band this page has
    sc["species"] = [fig]
    timeline = dict(tl, runtime_s=30.0, scenes=[sc], caption_pages=[], captions=[])
    at, errs, close = _serve(timeline, uris, "16:9")
    try:
        p = at(TIER_FIG_AT + TIER_FIG_S * 0.8)
        fg, tips = p["figure"], p["tipsActive"]
        assert len(tips) == 3, ("one datum list per band", tips)
        assert fg and fg["w"] > 0, ("the figure is written", fg)
        cy = fg["y"] + fg["h"] / 2
        d = [abs(cy - tp["y"]) for tp in tips]
        own = d[2]
        assert own <= TIER_NEAR_PX, ("written beside the THIRD band's datum", own, fg, tips)
        assert own == min(d), ("the third band's datum is the nearest one", d, fg, tips)
        assert min(d[0], d[1]) >= own + TIER_CLEAR_PX, ("and the nearest by a clear margin", d, fg, tips)
        assert d[0] >= TIER_WRONG_PX, ("the FIRST band is where the bug wrote it - it is nowhere near", d, fg, tips)
        assert not errs, errs
    finally:
        close()


@needs_objects
@needs_browser
def test_an_index_past_the_end_is_that_series_last_datum_and_a_seek_is_the_play():
    """The clamp the branch shipped with, kept per series (the ring's own flag placement asks for index 1 << 24 to
    find where the drawn data ends), and the frame is a pure function of t."""
    src = _three_series()
    far = {"kind": "ring", "at": 8.0, "dur": 2.0,
           "target": {"kind": "datum", "series": 2, "index": len(src["series"][2]["pts"]) + 5000}}
    at, errs, close = _ring_player([far])
    try:
        p = at(9.6)
        assert _dist(p["ring"], p["tipsActive"][2]) <= ON_PX, ("clamped to series 2's last datum", p)
        a = at(9.6); at(2.0); at(20.0); b = at(9.6)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), "a seek back paints the same bits"
        assert not errs, errs
    finally:
        close()
