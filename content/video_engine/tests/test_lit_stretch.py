"""P69 T36 - THE LIT STRETCH: a light that TRAVELS along a stretch of a line on its word (E99 s99).

The operator, 2026-09-23: "Light can become motion when it's highlighting and moving along a length, blinking ...
Bravos does this well." The Bravos harvest v2 ranks it first (A11, 8 of 9 videos; A13 the comet head). The token is
a PAGE species: `{"kind": "lit_stretch", "at", "dur", "from", "to", "series"?, "color"?, "comet"?}` on a ledger row.
The law and the painter are species/lit_stretch.mjs (pinned by tests/kinetics/lit_stretch.test.mjs); this file pins
the compiler's grammar, the engine's wiring, the card, and the light's travel read on the SERVED player (the golden
`lit-stretch-crash` - the railway index's fall, Steel and Paper H row 5's "crashed by nearly two-thirds").
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402

sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/lit_stretch.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
PLATE = "ledger:ev-railway-index-v1:line:139:right"
LIT = {"kind": "lit_stretch", "at": 10.0, "dur": 2.2, "from": 53, "to": 139}


def _errs(entries, plate=PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


# ---- the grammar -------------------------------------------------------------------------------------------


def test_the_token_is_a_page_species_the_compiler_accepts():
    assert "lit_stretch" in B.SPECIES_KINDS and "lit_stretch" in B.PAGE_SPECIES
    assert _errs([LIT]) == []
    assert _errs([dict(LIT, series=0, color="neg", comet=True)]) == []
    assert _errs([dict(LIT, **{"from": 0.25, "to": 0.75})]) == [], "two x-fractions, the span's other edge form"
    assert _errs([dict(LIT, **{"from": 139, "to": 53})]) == [], "from > to: the light runs back along the line"


def test_it_performs_on_a_ledger_page_only():
    errs = _errs([LIT], plate="plate-plain")
    assert any("lit_stretch is a page species" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"from": None}, "'from' must be a datum index"),
    ({"to": "x"}, "'to' must be a datum index"),
    ({"from": -1}, "not a non-negative datum index"),
    ({"to": 1.5}, "not a 0..1 fraction"),
    ({"from": 53, "to": 0.5}, "name BOTH edges the same way"),
    ({"from": 53, "to": 53}, "a light that travels needs a stretch"),
    ({"color": "gold"}, "color must be one of"),
    ({"series": -2}, "series must be a non-negative integer"),
    ({"comet": "yes"}, "comet must be true or false"),
    ({"label": "THE FALL"}, "a lit stretch writes nothing"),
])
def test_a_malformed_light_is_refused_by_name(patch, needle):
    errs = _errs([dict(LIT, **patch)])
    assert any(needle in e for e in errs), (patch, errs)


def test_a_series_the_page_does_not_have_is_refused_r26_218():
    one = {"kind": "ledger", "page": {"builder": "dense-line", "series": [{}]}}
    B.check_target_series(one, [dict(LIT, series=0)])
    with pytest.raises(ValueError, match=r"lit_stretch: series 1 is past the page's last series \(0\)"):
        B.check_target_series(one, [dict(LIT, series=1)])


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["lit_stretch"]
    assert 30 <= len(when) <= 260 and "\n" not in when, len(when)
    for word in ("WALKS", "travel", "never"):
        assert word in when, word


# ---- the engine's wiring -----------------------------------------------------------------------------------


def test_the_engine_carries_the_module_and_paints_it_from_the_perform_layer():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN lit_stretch */" in src
    assert src.index("/* KINETICS:BEGIN span */") < src.index("/* KINETICS:BEGIN lit_stretch */") < src.index("const paintPerform =")
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert 'pageSpecies(scene, "lit_stretch")' in build, "the builder makes the light's DOM"
    perform = src[src.index("const paintPerform ="):]
    perform = perform[:perform.index("\n  };\n")]
    assert "PAGE_PAINTERS.lit_stretch" in perform, "... and the perform layer paints it through the page registry"


def test_the_card_is_on_page_species_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["page_species:lit_stretch"]
    assert card["token"] == "lit_stretch" and card["when"] is None and card["serves"] == ["SPANS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/lit_stretch.mjs",
                             "symbol": "paintLitStretch"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/lit_stretch.mjs", "object": "LIT"}
    assert len(card["does"]) <= 240 and card["proof"]["golden"] == "lit-stretch-crash"
    assert "E99 s99" in card["doctrine"]


# ---- the light's travel, read on the served player -----------------------------------------------------------


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
  const st = world.__lp, PF = st.perform || {}, L = (PF.lits || [])[0];
  if (!L) return null;
  const d = L.core.getAttribute('d') || '', pts = d ? d.slice(1).split(' L').map(s => s.split(' ').map(Number)) : [];
  const S = (st.states && st.states[st.active | 0]) || st;
  const ser = (S.markBy || {}).s0, sp = ser && ser.geom && ser.geom.pts;
  const j = (i) => i - ((S.windowOffsets || [])[0] | 0) - ((ser && ser.geom.k0) | 0);   /* the page's datum index -> the stroke's own point */
  return { g: parseFloat(L.g.getAttribute('opacity') || '0'), head: L.head ? parseFloat(L.head.getAttribute('opacity') || '0') : null,
           first: pts[0] || null, last: pts[pts.length - 1] || null, n: pts.length,
           peak: sp ? sp[j(53)] : null, trough: sp ? sp[j(139)] : null };
}"""


def _serve(surface: str):
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(surface)
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[aspect]
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
        return page.evaluate(PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, errs, close


@needs_browser
def test_the_light_travels_down_the_fall_on_its_word_and_holds_when_it_lands():
    """The golden's own beat, read as geometry at four instants: nothing before the word; the head part-way down the
    fall and moving; the whole fall lit when the word is done, the comet head gone; the light standing after."""
    import build_golden_sources as G
    at, errs, close = _serve("lit-stretch-crash")
    try:
        a0, dur = G.LIT_AT, G.LIT_DUR
        before, early, mid, landed = at(a0 - 0.2), at(a0 + 0.3 * dur), at(a0 + 0.5 * dur), at(a0 + dur + 0.6)
    finally:
        close()
    assert not errs, errs
    assert before["g"] == 0, before
    peak, trough = mid["peak"], mid["trough"]
    for f in (early, mid):
        assert f["g"] == 1 and f["head"] == 1, f
        assert abs(f["first"][0] - peak[0]) < 0.2 and abs(f["first"][1] - peak[1]) < 0.2, (f["first"], peak)
        assert peak[0] < f["last"][0] < trough[0], (f["last"], peak, trough)
    assert early["last"][0] < mid["last"][0], "the head MOVES along the fall between two instants (s99: it travels)"
    assert landed["g"] == 1 and landed["head"] == 0, landed
    assert abs(landed["last"][0] - trough[0]) < 0.2 and abs(landed["last"][1] - trough[1]) < 0.2, (landed["last"], trough)


# ---- P69 T36 follow-up: a light on ONE panel of a panels page (`panel: <i>`; row 21 needs it) ------------------------

PANELS_V3 = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-tnx-two-eras-v3.series.json"
PANEL_LIT = {"kind": "lit_stretch", "at": 12.0, "dur": 1.6, "from": 0, "to": 71, "panel": 1, "comet": True}   # the AI era's climb, 0.9% -> 4.9%


def _panels_world():
    import ledger_page as LPG
    page = B.stamp_full_stage(LPG.build_spec(LPG.load_series(PANELS_V3), "line", None, "right"))
    return {"kind": "ledger", "page": page}


def test_a_light_names_its_panel_and_the_compiler_bounds_it():
    assert "lit_stretch" in B.PANEL_SPECIES
    assert _errs([PANEL_LIT], plate="ledger:golden-panels:line") == []
    world = _panels_world()
    B.check_panels(world, [dict(PANEL_LIT)])
    with pytest.raises(ValueError, match=r"lit_stretch: panel 2 is past the page's last panel \(1\)"):
        B.check_panels(world, [dict(PANEL_LIT, panel=2)])
    with pytest.raises(ValueError, match=r"lit_stretch: series 1 is past panel 1's last series \(0\)"):
        B.check_panels(world, [dict(PANEL_LIT, series=1)])
    with pytest.raises(ValueError, match="this page has none"):
        B.check_panels({"kind": "ledger", "page": {"builder": "dense-line"}}, [dict(PANEL_LIT)])


def test_the_engine_routes_a_light_to_its_panel():
    src = ENGINE.read_text(encoding="utf-8")
    kinds = src[src.index("const LP_PANEL_KINDS"):]
    assert '"lit_stretch"' in kinds[:kinds.index(";")], "the panel filter hands the light to the panel it names"


PANEL_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp;
  return (st.panels || []).map((S, i) => {
    const L = ((S.perform || {}).lits || [])[0];
    const ser = (S.markBy || {}).s0, sp = ser && ser.geom && ser.geom.pts, k0 = (ser && ser.geom.k0) | 0;
    if (!L) return { i, lit: null };
    const d = L.core.getAttribute('d') || '', pts = d ? d.slice(1).split(' L').map(s => s.split(' ').map(Number)) : [];
    return { i, g: parseFloat(L.g.getAttribute('opacity') || '0'), first: pts[0] || null, last: pts[pts.length - 1] || null,
             a: sp ? sp[0 - k0] : null, b: sp ? sp[71 - k0] : null };
  });
}"""


@needs_browser
def test_the_light_travels_the_line_of_the_panel_it_names_and_no_other():
    """A two-era panels page (row 15's object; row 21 is the first body row to want it): the light rides panel 2's
    line from its first datum to its peak on the word, panel 1 carries no light at all."""
    import build_golden_sources as G
    from playwright.sync_api import sync_playwright
    import render_baseline as RB
    tl, uris = G._panels_page(G.LPG.load_series(PANELS_V3), [dict(PANEL_LIT)], "probe: a light on panel 2")
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(html.parent)
    errs: list[str] = []
    try:
        with sync_playwright() as pw:
            page = pw.chromium.launch(headless=True).new_context(viewport={"width": w, "height": h}).new_page()
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)

            def at(t):
                page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                return page.evaluate(PANEL_PROBE)
            before, mid, landed = at(11.8), at(12.0 + 0.5 * 1.6 * 0.8), at(14.5)
    finally:
        srv.shutdown(); td.cleanup()
    assert not errs, errs
    assert before[0].get("lit") is None and before[1]["g"] == 0, before
    p2 = mid[1]
    assert mid[0].get("lit") is None, "panel 1 carries no light"
    assert p2["g"] == 1 and abs(p2["first"][0] - p2["a"][0]) < 0.2 and p2["a"][0] < p2["last"][0] < p2["b"][0], p2
    q = landed[1]
    assert abs(q["last"][0] - q["b"][0]) < 0.2 and abs(q["last"][1] - q["b"][1]) < 0.2, q
