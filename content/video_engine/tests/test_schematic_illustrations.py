"""P71 T20 (was P69 T62; A55 folded in from P70's Not Building) - ILLUSTRATIONS DRAWN AS SCHEMATICS (E99 s109 (1)).

P70 T2's schematic draws a named shape with no data. This slice extends it:
- `candles`: candlestick bodies and wicks GENERATED along a ghost wave (the Bravos harvest v2 T8, BUB 04:47.3) - price
  action as illustration, a shape, never a series; the ghost is context (grey, no bloom) and a candle prints as the pen
  passes its x, in the sign inks (up / down).
- `motif`: an AXIS-FREE rising wave named by one word (T46, JPN 09:09-09:11 "Market"): no axis rule, no tick, no label.
- `datum_badge`: a page species - a tick or a cross in a filled disc ON a datum (A14, JPN 06:40 "X pins the two
  endpoints") or on a schematic's turning point (`vertex`, the motif's X at each named vertex), sweeping in left to right.
- A55: a `lit_stretch` with `phase_ink: true` on a schematic paints each phase it passes in that phase's own `ink`.
s109 (1) is the check: no axis value, no tick label and no figure a schematic cannot source; the tag "a shape, not a
series" stays on every shape; a page that names none of this compiles as it did.
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
MONITOR = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-memory-monitor-v1.series.json"
PLATE = "ledger:ev-x:line::right"
CANDLES = {"title": "Price action", "sub": "An illustration - a shape, not a series",
           "src": "Shape: candlesticks along a wave - a schematic, no data", "schematic": {"shape": "candles"}}
MOTIF = {"title": "Memory", "src": "Shape: a rising wave - a schematic, no data", "schematic": {"shape": "motif"}}
HYPE_PHASES = [{"name": "Trigger", "from": 0.0, "to": 0.12}, {"name": "Peak", "from": 0.12, "to": 0.3},
               {"name": "Trough", "from": 0.3, "to": 0.48}, {"name": "Slope", "from": 0.48, "to": 0.72},
               {"name": "Plateau", "from": 0.72, "to": 1.0}]


def _with(obj: dict, **sch) -> dict:
    out = copy.deepcopy(obj)
    out["schematic"].update(sch)
    return out


def _spec(obj: dict) -> dict:
    return LPG.build_spec(obj, "line", None, "right")


# ---- the two shapes: generated, pure, deterministic ------------------------------------------------------------------


def test_candles_and_motif_are_schematic_shapes_with_no_phases_required():
    """The expected RED: `candles` and `motif` are not schematic shapes at the base."""
    assert "candles" in LPG.SCHEMATIC_SHAPES and "motif" in LPG.SCHEMATIC_SHAPES
    assert LPG.validate(CANDLES, "line") == [] and LPG.validate(MOTIF, "line") == []
    assert LPG.pick_builder(CANDLES, "line") == "dense-line" and LPG.pick_builder(MOTIF, "line") == "dense-line"
    hype = {"title": "H", "src": "Shape", "schematic": {"shape": "hype"}}
    assert any("phases must be a list of 1 to 6" in e for e in LPG.validate(hype, "line")), "a phase model still names its phases"


def test_the_motif_is_a_rising_wave_with_eight_turning_points():
    pts = LPG.schematic_series(MOTIF["schematic"])["pts"]
    v = LPG.schematic_vertices(MOTIF["schematic"])
    assert len(v) == 8, v
    ys = [pts[i][1] for i in v]
    peaks, troughs = ys[0::2], ys[1::2]
    assert all(p > t for p, t in zip(peaks, troughs)), "peak, trough, peak ... from the bottom-left"
    assert all(b > a for a, b in zip(peaks, peaks[1:])) and all(b > a for a, b in zip(troughs, troughs[1:])), "it RISES"
    assert pts[0][1] < min(troughs) and pts[-1][1] > max(peaks), "from the bottom-left to past the last peak, on a rise"
    assert all(0.0 <= p[1] <= 1.0 for p in pts)
    assert LPG.schematic_vertices(MOTIF["schematic"]) == v, "pure"


def test_the_vertices_of_every_shape_are_its_interior_turning_points():
    for shape in LPG.SCHEMATIC_SHAPES:
        sch = {"shape": shape, "phases": HYPE_PHASES}
        pts = LPG.schematic_series(sch)["pts"]
        for i in LPG.schematic_vertices(sch):
            assert 0 < i < len(pts) - 1, (shape, i)
            a, b = pts[i][1] - pts[i - 1][1], pts[i + 1][1] - pts[i][1]
            assert a * b <= 0, (shape, i, a, b)
    assert len(LPG.schematic_vertices({"shape": "waves", "phases": HYPE_PHASES})) == 3   # top, bottom, top


def test_the_candles_ride_the_ghost_wave_and_print_up_or_down():
    sch = CANDLES["schematic"]
    cs = LPG.schematic_candles(sch)
    assert len(cs) == LPG.SCHEMATIC_CANDLES and cs == LPG.schematic_candles(sch), "a fixed count, pure"
    ghost = LPG.schematic_series(sch)["pts"]
    xs = [c[0] for c in cs]
    assert all(b > a for a, b in zip(xs, xs[1:])) and 0.0 < xs[0] and xs[-1] < 1.0
    up = down = 0
    for x, o, h, lo, c in cs:
        assert 0.0 <= lo <= min(o, c) < max(o, c) <= h <= 1.0, (x, o, h, lo, c)
        assert abs(c - o) >= LPG.SCHEMATIC_CANDLE_BODY_MIN - 1e-9, "never a body too thin to read its colour"
        g = min(ghost, key=lambda p: abs(p[0] - x))[1]
        assert abs((o + c) / 2 - g) <= 0.12, ("a candle rides the ghost wave", x, (o + c) / 2, g)
        up, down = up + (c > o), down + (c < o)
    assert up >= 8 and down >= 8, (up, down)


def test_the_candles_spec_carries_the_candles_and_a_ghost_that_is_context():
    spec = _spec(CANDLES)
    sch = spec["schematic"]
    assert sch["shape"] == "candles" and sch["tag"] == LPG.SCHEMATIC_TAG and sch["phases"] == []
    assert sch["candles"] == LPG.schematic_candles(CANDLES["schematic"])
    ser = spec["series"][0]
    assert ser["color"] == LPG.SCHEMATIC_GHOST == "deemph", "the ghost never blooms (context, E99 s117)"
    assert "label" not in ser and "xticks" not in spec["axes"] and spec["unit"] == ""


def test_the_motif_spec_is_axis_free_and_keeps_its_tag():
    spec = _spec(MOTIF)
    assert spec["schematic"] == {"shape": "motif", "tag": LPG.SCHEMATIC_TAG, "phases": [], "axis_free": True}
    assert spec["series"][0]["color"] == LPG.SCHEMATIC_INK


def test_an_illustration_with_no_phase_fills_its_plot():
    """The phase models keep SCHEMATIC_DOMAIN's room for their names; an illustration naming none fills its plot."""
    assert _spec(MOTIF)["axes"]["domain"] == list(LPG.SCHEMATIC_ILLUSTRATION_DOMAIN)
    assert _spec(CANDLES)["axes"]["domain"] == list(LPG.SCHEMATIC_ILLUSTRATION_DOMAIN)
    named = _with(CANDLES, phases=[{"name": "Run-up", "from": 0.0, "to": 0.33}])
    assert _spec(named)["axes"]["domain"] == list(LPG.SCHEMATIC_DOMAIN), "a named phase needs its room"
    lo, hi = LPG.SCHEMATIC_ILLUSTRATION_DOMAIN
    assert lo < 0.0 and hi > 1.0, "the shape's [0, 1] inside it, with a stroke's air"


def test_the_three_phase_models_carry_nothing_new():
    """Byte-identical absent the shapes: a hype / waves / debt_cycle spec has no `candles`, no `axis_free`."""
    for shape in ("hype", "waves", "debt_cycle"):
        sch = _spec({"title": "T", "src": "Shape", "schematic": {"shape": shape, "phases": HYPE_PHASES}})["schematic"]
        assert set(sch) == {"shape", "tag", "phases"}, sch


@pytest.mark.parametrize("obj, needle", [
    (_with(CANDLES, color="teal"), "a candles schematic takes no color"),
    (dict(copy.deepcopy(MOTIF), ylabel="Price"), "the motif is axis-free"),
    (_with(MOTIF, phases=[]), "phases must be a list of 1 to 6"),
    (_with(CANDLES, phases=[{"name": "A", "from": 0.0, "to": 0.5, "ink": "gold"}]), "ink must be one of"),
])
def test_a_malformed_illustration_is_refused_by_name(obj, needle):
    errs = LPG.validate(obj, "line")
    assert any(needle in e for e in errs), errs


def test_a_phase_may_name_its_ink():
    obj = {"title": "T", "src": "Shape", "schematic": {"shape": "waves", "phases": [
        {"name": "Up", "from": 0.0, "to": 0.25, "ink": "pos"}, {"name": "Down", "from": 0.25, "to": 0.5, "ink": "neg"}]}}
    assert LPG.validate(obj, "line") == []
    ph = _spec(obj)["schematic"]["phases"]
    assert [p.get("ink") for p in ph] == ["pos", "neg"]


# ---- the datum badge: the grammar, refused by name ------------------------------------------------------------------


def _badge(**kw) -> dict:
    return dict({"kind": "datum_badge", "at": 2.0, "dur": 1.0, "glyph": "cross",
                 "target": {"kind": "datum", "series": 0, "index": 5}}, **kw)


def test_the_datum_badge_is_a_page_species_that_leaves_with_its_page():
    """The expected RED: `datum_badge` is an unknown species kind at the base."""
    assert B.SPECIES_DATUM_BADGE == "datum_badge"
    assert "datum_badge" in B.SPECIES_KINDS and "datum_badge" in B.PAGE_SPECIES and "datum_badge" in B.PAGE_BOUND_SPECIES
    assert B.DATUM_BADGE_GLYPHS == ("tick", "cross")
    assert B.SPECIES_WHEN["datum_badge"]


@pytest.mark.parametrize("sp", [
    _badge(),
    _badge(glyph="tick"),
    _badge(target={"kind": "vertex", "index": 3}),
    _badge(target=[{"kind": "vertex", "index": i} for i in (1, 3, 5, 7)]),
    _badge(target=[{"kind": "datum", "series": 0, "index": 42}, {"kind": "datum", "series": 1, "index": 42}], keep=True),
])
def test_a_well_formed_badge_validates(sp):
    assert B.validate_species([sp], (0, 0, 0), PLATE) == []


@pytest.mark.parametrize("patch, needle", [
    ({"glyph": None}, "glyph must be one of tick|cross"),
    ({"glyph": "check"}, "glyph must be one of tick|cross"),
    ({"target": None}, "names its datum"),
    ({"target": {"kind": "bar", "index": 1}}, "a target is {kind: datum, series?, index} or {kind: vertex, index}"),
    ({"target": {"kind": "datum", "index": -1}}, "index must be a non-negative integer"),
    ({"target": {"kind": "datum", "index": True}}, "index must be a non-negative integer"),
    ({"target": {"kind": "datum", "series": -2, "index": 1}}, "series must be a non-negative integer"),
    ({"target": {"kind": "vertex", "series": 1, "index": 1}}, "a vertex is the shape's own"),
    ({"target": []}, "names its datum"),
    ({"target": [{"kind": "vertex", "index": i} for i in range(13)]}, "at most 12"),
    ({"target": [{"kind": "vertex", "index": 2}, {"kind": "vertex", "index": 2}]}, "twice"),
    ({"label": "failed"}, "a badge writes no words"),
    ({"panel": 0}, "a badge writes no words"),
])
def test_a_malformed_badge_is_refused_by_name(patch, needle):
    sp = _badge(**patch)
    errs = B.validate_species([sp], (0, 0, 0), PLATE)
    assert any(needle in e for e in errs), errs


def _world(obj: dict) -> dict:
    return {"kind": "ledger", "page": _spec(obj)}


def _monitor() -> dict:
    return json.loads(MONITOR.read_text(encoding="utf-8"))


def test_the_badge_reads_the_page_it_stands_on():
    data = _world(_monitor())
    n = len(data["page"]["series"][0]["pts"])
    B.check_datum_badge(data, [_badge(target={"kind": "datum", "series": 0, "index": n - 1})])
    motif = _world(MOTIF)
    B.check_datum_badge(motif, [_badge(target=[{"kind": "vertex", "index": i} for i in range(8)])])
    with pytest.raises(ValueError, match="past the series' last datum"):
        B.check_datum_badge(data, [_badge(target={"kind": "datum", "series": 0, "index": n})])
    with pytest.raises(ValueError, match="series 7 is not on the page"):
        B.check_datum_badge(data, [_badge(target={"kind": "datum", "series": 7, "index": 1})])
    with pytest.raises(ValueError, match="a schematic has no data"):
        B.check_datum_badge(motif, [_badge(target={"kind": "datum", "series": 0, "index": 10})])
    with pytest.raises(ValueError, match="a vertex is a schematic's turning point"):
        B.check_datum_badge(data, [_badge(target={"kind": "vertex", "index": 1})])
    with pytest.raises(ValueError, match="the shape turns 8 times"):
        B.check_datum_badge(motif, [_badge(target={"kind": "vertex", "index": 8})])
    with pytest.raises(ValueError, match="a LINE page's"):
        B.check_datum_badge({"kind": "ledger", "page": {"builder": "story", "bars": []}}, [_badge()])
    with pytest.raises(ValueError, match="on a ledger page"):
        B.check_datum_badge({"kind": "plate"}, [_badge()])
    B.check_datum_badge({"kind": "plate"}, [{"kind": "figure", "at": 1.0, "dur": 1.0, "text": "x"}])   # no badge: untouched


def test_a_badge_on_a_line_s_last_datum_keeps_the_end_tag_clear():
    """The ring's TIP CLEAR (stamp_tip_marks): a badge on the last datum stamps `tip_mark`, so the line's end tag ends
    past the disc instead of under it (the first frame read: the X sat on "12m avg TRIGGER"). A list is read whole."""
    page = _spec(_monitor())
    n = len(page["series"][0]["pts"])
    sc = {"scene_id": "s", "world": {"kind": "ledger", "page": page},
          "species": [_badge(target=[{"kind": "datum", "series": 0, "index": 3}, {"kind": "datum", "series": 2, "index": n - 1}])]}
    notes = B.stamp_tip_marks([sc])
    assert page["tip_mark"] == [2] and len(notes) == 1, (page.get("tip_mark"), notes)   # the note's wording is the ring's (the H door's log unchanged)
    mid = {"scene_id": "s", "world": {"kind": "ledger", "page": _spec(_monitor())}, "species": [_badge()]}
    assert B.stamp_tip_marks([mid]) == [] and "tip_mark" not in mid["world"]["page"], "a badge off the tip moves nothing"


def test_the_registries_carry_the_badge():
    import gate_motion_density as GMD
    import lint_species_choice as LSC
    import recipe_walk as RW
    from authoring import shapes as SH
    assert GMD.SPECIES_EVENTS["datum_badge"] == ("at",)
    assert "datum_badge" in GMD.PLOT_INK_MARKS and "datum_badge" in GMD.PLOT_HELD_MARKS
    assert "datum_badge" in SH.PLOT_MARKS and "datum_badge" in SH.HELD_MARKS
    assert "datum_badge" in LSC.ACT_SPECIES["RETRACTS"]
    assert "datum_badge" in RW.PAGE_SPECIES_KINDS


# ---- A55: the comet paints the phases ----------------------------------------------------------------------------------


INKED = {"title": "The debt cycle", "src": "Shape: a long-term debt cycle - a schematic, no data", "schematic": {
    "shape": "waves", "phases": [{"name": "Boom", "from": 0.0, "to": 0.25, "ink": "pos"},
                                 {"name": "Bust", "from": 0.25, "to": 0.5, "ink": "neg"},
                                 {"name": "Recovery", "from": 0.5, "to": 0.75, "ink": "pos"}]}}


def test_phase_ink_is_a_lit_stretch_key_refused_where_no_phase_names_an_ink():
    sp = {"kind": "lit_stretch", "at": 2.0, "dur": 2.0, "from": 0.05, "to": 0.7, "comet": True, "phase_ink": True}
    assert B.validate_species([sp], (0, 0, 0), PLATE) == []
    errs = B.validate_species([dict(sp, phase_ink="yes")], (0, 0, 0), PLATE)
    assert any("phase_ink must be true or false" in e for e in errs), errs
    errs = B.validate_species([dict(sp, color="amber")], (0, 0, 0), PLATE)
    assert any("phase_ink and color" in e for e in errs), errs
    B.check_schematic(_world(INKED), [sp])
    with pytest.raises(ValueError, match="phase_ink on a page with no schematic"):
        B.check_schematic(_world(_monitor()), [sp])
    bare = copy.deepcopy(INKED)
    for p in bare["schematic"]["phases"]:
        p.pop("ink")
    with pytest.raises(ValueError, match="no phase it passes names an ink"):
        B.check_schematic(_world(bare), [sp])


# ---- the engine and the cards ------------------------------------------------------------------------------------------


def test_the_cards_name_the_shapes_the_badge_and_their_use_when():
    pb = {c["id"]: c for c in json.loads((CARDS / "page_builder.json").read_text(encoding="utf-8"))["cards"]}
    blob = json.dumps(pb["page_builder:line+schematic"])
    assert "candles" in blob and "motif" in blob and "BRAVOS-USE-WHEN.md:571" in blob and "BRAVOS-USE-WHEN.md:989" in blob
    ps = {c["id"]: c for c in json.loads((CARDS / "page_species.json").read_text(encoding="utf-8"))["cards"]}
    card = ps["page_species:datum_badge"]
    assert card["status"] == "wired" and "RETRACTS" in card["serves"]
    assert "BRAVOS-USE-WHEN.md:995" in json.dumps(card) and card["proof"]["golden"] == "schematic-motif"
    blob = json.dumps(ps["page_species:lit_stretch"])
    assert "phase_ink" in blob and "BRAVOS-USE-WHEN.md:655" in blob


def test_the_engine_draws_the_shapes_behind_the_schematic_branch_only():
    src = ENGINE.read_text(encoding="utf-8")
    body = src[src.index("const lpSchematicTag"):src.index("const buildLedgerRace")]
    assert "SCH.candles" in body and "SCH.axis_free" in body, "the two shapes live in the schematic's own functions"
    assert "const lpBuildDatumBadges" in src and "const lpPaintDatumBadges" in src


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
  const st = world.__lp, S = st.schematic || {}, PF = st.perform || {};
  const vis = (el) => !!el && el.getAttribute('visibility') !== 'hidden' && getComputedStyle(el).display !== 'none'
                      && +(el.getAttribute('opacity') ?? 1) > 0.05;
  const texts = [...st.page.querySelectorAll('text, .lp-ink')].filter(e => vis(e) && (e.textContent || '').trim()).map(e => e.textContent);
  const ser = (st.paths || [])[0];
  const badges = (PF.datumBadges || []).flatMap(b => b.marks.map(m => {
    const tr = (m.g.getAttribute('transform') || '').match(/translate\\(([-\\d.]+)[ ,]+([-\\d.]+)\\)\\s*scale\\(([-\\d.]+)\\)/);
    const at = window.__lpDatum(null, m.si, m.i);
    return { op: +(m.g.getAttribute('opacity') || 0), x: tr ? +tr[1] : null, y: tr ? +tr[2] : null, s: tr ? +tr[3] : null,
             want: at, fill: m.disc.style.fill, marks: m.strokes.map(p => +(p.getAttribute('stroke-dashoffset') || 0)),
             markInk: m.strokes[0] ? m.strokes[0].style.stroke : null, at: m.at }; }));
  const lit = (PF.lits || [])[0];
  return {
    texts,
    tag: st.chart.querySelector('.lp-schematic') ? st.chart.querySelector('.lp-schematic').textContent : null,
    axis: st.markBy.axis ? vis(st.markBy.axis.el) : null, yaxis: st.markBy.yaxis ? vis(st.markBy.yaxis.el) : null,
    ylabs: [...st.chart.querySelectorAll('.lab')].filter(e => vis(e) && !e.classList.contains('lp-schematic') && !e.classList.contains('lp-phase')).length,
    vertices: (S.vertices || []).map(v => [v.i, +v.x.toFixed(1), +v.y.toFixed(1)]),
    candles: (S.candles || []).map(c => ({ op: +(c.g.getAttribute('opacity') || 0), x: c.x, up: c.up, fill: c.body.style.fill,
                                           h: +(c.body.getAttribute('height') || 0) })),
    drawnX: (() => { if (!ser || !ser.p.getPointAtLength) return null; const f = 1 - (+ser.p.getAttribute('stroke-dashoffset') || 0) / ser.len;
                     return ser.p.getPointAtLength(ser.len * Math.max(0, Math.min(1, f))).x; })(),
    ghost: ser ? { stroke: ser.p.getAttribute('stroke'), context: !!ser.context, filter: ser.p.style.filter || '' } : null,
    badges,
    litSegs: lit && lit.segs ? lit.segs.map(s => ({ ink: s.core.getAttribute('stroke'), d: s.core.getAttribute('d') || '',
                                                    op: +(lit.g.getAttribute('opacity') || 0) })) : null,
    headFill: lit && lit.head ? lit.head.getAttribute('fill') : null,
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


def _row(obj_id: str, obj: dict, species: list, plate_tail: str = "") -> tuple[dict, dict]:
    import build_golden_sources as G
    plate = f"ledger:{obj_id}:line::right{plate_tail}"
    assert not B.validate_species(species, (0, 0, 0), plate), B.validate_species(species, (0, 0, 0), plate)
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        with tempfile.TemporaryDirectory() as td:
            objects = Path(td) / "evidence/objects"
            objects.mkdir(parents=True)
            (objects / f"{obj_id}.series.json").write_text(json.dumps(obj), encoding="utf-8")
            world = B.world_for_plate(plate, (0, 0, 0), Path(td))
        B.stamp_full_stage(world["page"])
    finally:
        B.ASPECT = saved
    B.check_datum_badge(world, species)
    B.check_schematic(world, species)
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}),
               "exit": "cut", "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    B.stamp_tip_marks(scenes)   # main()'s own pass: a mark on a line's last datum keeps its end tag clear
    return G._timeline("T20 probe", scenes, {}, "16:9"), G._base_uris()


def _digits(texts: list) -> list:
    return [t for t in texts if re.search(r"\d", t)]


@needs_browser
def test_candles_print_along_the_ghost_wave_as_the_pen_passes():
    import build_golden_sources as G
    at, errs, close = _serve("schematic-candles")
    try:
        mid, done = at(G.CANDLES_WORD_AT + 0.125 * G.CANDLES_WORD_DUR), at(G.CANDLES_WORD_AT + G.CANDLES_WORD_DUR + 0.6)
    finally:
        close()
    assert not errs, errs
    assert _digits(done["texts"]) == [], "s109 (1): no value anywhere on the page"
    assert done["tag"] == LPG.SCHEMATIC_TAG
    assert done["ghost"]["context"] and "drop-shadow" not in done["ghost"]["filter"], ("the ghost is context: no bloom", done["ghost"])
    assert len(done["candles"]) == LPG.SCHEMATIC_CANDLES and all(c["op"] > 0.95 for c in done["candles"])
    ups = [c for c in done["candles"] if c["up"]]
    assert ups and all(c["fill"] == "var(--lp-pos)" for c in ups)
    assert all(c["fill"] == "var(--lp-neg)" for c in done["candles"] if not c["up"])
    drawn = mid["drawnX"]
    printed = [c for c in mid["candles"] if c["op"] > 0.5]
    assert 0 < len(printed) < LPG.SCHEMATIC_CANDLES, "on the word: part of the wave has its candles"
    assert all(c["x"] <= drawn + 1 for c in printed), "a candle never prints ahead of the pen"


@needs_browser
def test_the_motif_is_axis_free_and_an_x_lands_on_each_named_vertex():
    import build_golden_sources as G
    at, errs, close = _serve("schematic-motif")
    try:
        before, sweep, held = at(G.MOTIF_BADGE_AT - 0.05), at(G.MOTIF_BADGE_AT + 0.05), at(G.MOTIF_BADGE_AT + 1.2)
    finally:
        close()
    assert not errs, errs
    assert held["axis"] is False and held["yaxis"] in (False, None), "axis-free: no rule on either side"
    assert _digits(held["texts"]) == [] and held["tag"] == LPG.SCHEMATIC_TAG
    assert len(held["vertices"]) == 8
    named = G.MOTIF_VERTICES
    assert len(held["badges"]) == len(named)
    assert all(b["op"] == 0 for b in before["badges"]), "nothing before its word"
    lit = [b["op"] > 0 for b in sweep["badges"]]
    assert lit[0] and lit == sorted(lit, reverse=True), ("the sweep runs left to right", lit)
    for b, k in zip(held["badges"], named):
        v = held["vertices"][k]
        assert abs(b["x"] - v[1]) < 0.6 and abs(b["y"] - v[2]) < 0.6, (b, v)
        assert b["op"] > 0.99 and abs(b["s"] - 1) < 1e-3 and b["fill"] == "rgb(255, 77, 77)", b
        assert all(o < 0.01 for o in b["marks"]), "the X is struck whole"


@needs_browser
def test_a_tick_lands_on_a_real_chart_s_datum():
    obj = _monitor()
    n = len(obj["series"][0]["pts"])
    species = [{"kind": "datum_badge", "at": 8.0, "dur": 1.0, "glyph": "tick", "target": {"kind": "datum", "series": 0, "index": n - 1}}]
    tl, uris = _row("ev-memory-monitor-v1", obj, species)
    at, errs, close = _open(tl, uris, "16:9")
    try:
        f = at(9.5)
    finally:
        close()
    assert not errs, errs
    (b,) = f["badges"]
    assert b["op"] > 0.99 and abs(b["x"] - b["want"][0]) < 0.6 and abs(b["y"] - b["want"][1]) < 0.6, b
    assert b["fill"] == "rgb(61, 220, 132)" and b["markInk"] == "rgb(37, 49, 60)", "T12's check: the positive disc, the charcoal check"


@needs_browser
def test_the_comet_paints_each_phase_it_passes_in_that_phase_s_ink():
    species = [{"kind": "lit_stretch", "at": 8.0, "dur": 2.0, "from": 0.05, "to": 0.7, "comet": True, "phase_ink": True}]   # the page has built
    tl, uris = _row("ev-inked-cycle", INKED, species)
    at, errs, close = _open(tl, uris, "16:9")
    try:
        early, done = at(8.3), at(10.5)
    finally:
        close()
    assert not errs, errs
    segs = done["litSegs"]
    assert segs is not None and [s["ink"] for s in segs] == ["var(--lp-pos)", "var(--lp-neg)", "var(--lp-pos)"], segs
    assert all(s["d"] for s in segs), "every phase the light passed is lit"
    assert early["litSegs"][0]["d"] and not early["litSegs"][2]["d"], "a phase the head has not reached is dark"
