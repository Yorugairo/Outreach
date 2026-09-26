"""P71 T29 (was P69 T77) - GLOW EDGES: a glow outline on the named bar or region.

The Bravos harvest v2's F2 (n=3; BRAVOS-USE-WHEN.md:195): "the part the sentence names must read as lit, not just
coloured" - BUB #3's hidden block, its region edged in a near-white line with a halo in its own pink. The token is a PAGE
species: `{"kind": "glow", at, dur, bar: <i> | span: <k>, pulse?: true, keep?}` on a ledger row. It is the ONE glow
system (E99 s130, s117): the edge's halos are the fill glow's (lpFillGlow / lpFillFilter, T10) on a dial object in the
spread's form (LP_GLOW_EDGE, T49's), and its light is the chip's `lit` (chipLitF, T12): held it is an annotation (0
events, s91), `pulse: true` blinks it (motion, s99). F14 (a red perimeter on a card) is DROPPED and F19 (the bevelled
stamp slab) RETIRED by the plan. This file pins the grammar (every key refused by name when malformed or misplaced),
the page's truth rules, the WARNs (s106: one glow per row; s71: a glow before its region has arrived), the gate's
credit, the engine's wiring, the card, the dials against BUB #3 read by measure_line_bloom's LINE mode at its own 512 px,
and the edge read on the SERVED player (the golden `glow-outline-bar`: Steel and Paper H row 18b's 20 bar lit on
"twenty percent").
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BARS = "ledger:ev-index-concentration-bars-v1:bars::right:axes:cut;idle=live;readability=longform;bar_style=soft"
TWO = "ledger:ev-two-clocks-bars-v1:bars::right:axes:cut"
LINE = "ledger:ev-capital-formation-v1:line:225:right"
GLOW = {"kind": "glow", "at": 1.09, "dur": 0.68, "bar": 0}
SPAN = {"kind": "span", "at": 1.0, "dur": 2.0, "from": 124, "to": 225, "label": "DOT-COM TO TODAY", "color": "cobalt"}
BUB3 = Path("content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/frames/frame_0003.jpg")
# BUB #3's lit edge read by measure_line_bloom's LINE mode at its own 512 px (the bottom edge of the hidden block, the
# region's inside left out) - p71-t29/scripts/m_bub.py. reach10 / area are NOT pinned: past ~10 px the ring reads the
# strip under the edge (a gradient ~81 -> ~69 luma), not the halo.
BUB_BOX, BUB_EXCLUDE = [240, 229, 368, 287], [[240, 229, 368, 232]]
BUB_READ = {"stroke_px": 2.0, "core_L": 93.7, "core_sat": 0.096, "halo_edge": 0.546, "halo_r50_px1080": 10.22}
# ... and ours is judged against it with these tolerances (one Bravos frame: a point, not a band - the tool's own
# reproduction tolerance, BAND_TOL 8 % / BAND_ABS, widened where one 512 px JPEG's quantisation is the limit, and named)
TOL = {"stroke_px": 0.5,          # one px at 512: a 1-px line's anti-alias reads 2 either way
       "core_L": 6.0,             # the edge burns near-white: L* 93.7 +- 6
       "core_sat": 0.10,          # ... at a LOW saturation (the ink's own is ~0.7)
       "halo_edge": 0.08,         # the tool's halo_edge floor is 0.03; one 512 px ring is 3.75 stage px
       "halo_r50_px1080": 3.75}   # one ring at 512


def _errs(entries, plate=BARS):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _world(plate=BARS) -> dict:
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        return B.world_for_plate(plate, (0, 0, 0), PROJECT)
    finally:
        B.ASPECT = saved


def _check(entries, plate=BARS):
    return B.check_glow(_world(plate), [dict(e) for e in entries])


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_the_token_is_a_page_species_the_compiler_accepts():
    assert "glow" in B.SPECIES_KINDS and "glow" in B.PAGE_SPECIES
    assert "glow" in B.PAGE_BOUND_SPECIES, "an edge on the page's mark leaves with the page (R26-219)"
    assert "glow" not in B.PANEL_SPECIES, "a panel carries no edge - not built there, so not accepted"
    assert _errs([GLOW]) == []
    assert _errs([dict(GLOW, pulse=True, keep=True)]) == []
    assert _errs([SPAN, {"kind": "glow", "at": 3.2, "dur": 0.5, "span": 0}], plate=LINE) == []


def test_it_performs_on_a_ledger_page_only():
    errs = _errs([GLOW], plate="plate-plain")
    assert any("glow is a page species" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"bar": None}, "names ONE mark"),
    ({"span": 0}, "names ONE mark"),                       # both a bar and a span
    ({"bar": -1}, "bar must be a non-negative integer"),
    ({"bar": 0.5}, "bar must be a non-negative integer"),
    ({"bar": True}, "bar must be a non-negative integer"),
    ({"pulse": "yes"}, "pulse is `true` or absent"),
    ({"pulse": 3}, "pulse is `true` or absent"),
    ({"color": "teal"}, "glow: 'color'"),                         # the edge is the mark's own ink - never authored
    ({"panel": 0}, "glow: 'panel'"),
    ({"target": {"kind": "datum", "index": 0}}, "glow: 'target'"),
    ({"blink": True}, "glow: 'blink'"),                           # the light grammar is the chip's: `pulse`
])
def test_a_malformed_glow_is_refused_by_name(patch, needle):
    e = dict(GLOW, **patch)
    if patch.get("bar", 0) is None:
        e.pop("bar")
    errs = _errs([e])
    assert any(needle in x for x in errs), (patch, errs)


def test_a_span_glow_names_a_span_index():
    errs = _errs([SPAN, {"kind": "glow", "at": 3.2, "dur": 0.5, "span": "the run-up"}], plate=LINE)
    assert any("span must be a non-negative integer" in e for e in errs), errs


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    w = B.SPECIES_WHEN["glow"]
    assert "LIT" in w and "RANKS" in w and "ARRIVE" in w and "one per row" in w, w


# ---- the page's truth (hard) and its advice (WARN, s106) -----------------------------------------------------------


@pytest.mark.parametrize("entries, plate, needle", [
    ([dict(GLOW, bar=1)], BARS, "bar 1 is not on the page"),
    ([GLOW], LINE, "a line page"),
    ([{"kind": "glow", "at": 3.2, "dur": 0.5, "span": 0}], LINE, "span 0 is not on the row"),
    ([SPAN, {"kind": "glow", "at": 3.2, "dur": 0.5, "span": 1}], LINE, "span 1 is not on the row"),
])
def test_a_mark_the_page_does_not_have_is_refused(entries, plate, needle):
    with pytest.raises(ValueError, match=re.escape(needle)):
        _check(entries, plate)


def test_a_glow_off_a_ledger_world_is_refused():
    with pytest.raises(ValueError, match="a glow edges a mark on a ledger page"):
        B.check_glow({"kind": "plate"}, [dict(GLOW)])


def test_a_gauge_or_an_extruded_bar_is_refused_by_name():
    for form, plate in (("gauge", "ledger:ev-capex-ocf-94-bars-v1:progress::right;form=gauge"),
                        ("extruded_bar", TWO + ";form=extruded_bar")):
        with pytest.raises(ValueError, match=form):
            B.check_glow(_world(plate), [dict(GLOW)])


def test_one_glow_is_quiet_and_a_second_on_the_row_is_a_warn_never_a_refusal():
    assert _check([GLOW], TWO) == []
    notes = _check([GLOW, dict(GLOW, at=3.0, bar=1)], TWO)
    assert len(notes) == 1 and "2 glows on one row" in notes[0] and "the glow stops meaning anything" in notes[0], notes


def test_a_glow_before_its_region_has_arrived_is_a_warn_with_its_numbers():
    notes = _check([dict(SPAN, at=4.0), {"kind": "glow", "at": 3.2, "dur": 0.5, "span": 0}], LINE)
    assert len(notes) == 1 and "s71" in notes[0] and "3.2" in notes[0] and "4.0" in notes[0], notes
    assert _check([SPAN, {"kind": "glow", "at": 3.2, "dur": 0.5, "span": 0}], LINE) == []


def test_the_rows_page_checks_run_the_glows():
    src = Path(B.__file__).read_text(encoding="utf-8")
    hub = src[src.index("def derive_rescale_states("):]
    assert "check_glow(world, row_species)" in hub[:hub.index("\ndef ")], "the row's own page checks run it (main and the goldens)"


# ---- the gate's credit (s91 / s99) ---------------------------------------------------------------------------------


def _events(sp: dict) -> list[float]:
    import gate_motion_density as G
    return G._species_events([{"span": [0.0, 30.0], "species": [sp]}])


def test_a_held_glow_earns_nothing_and_a_pulsed_one_earns_each_blink():
    import gate_motion_density as G
    assert G.SPECIES_EVENTS["glow"] == ("pulse",), "held: an annotation (s91); pulsed: one event per blink onset (s99)"
    assert _events(dict(GLOW, dur=4.0)) == []
    got = _events(dict(GLOW, dur=4.0, pulse=True))
    cp = G.CHIP_PULSE
    assert got == [round(GLOW["at"] + cp["land_s"] + k * cp["s"], 2) for k in range(cp["n"])], got
    assert _events(dict(GLOW, dur=0.5, pulse=True)) == [], "only inside its window (the chip's rule: the first blink is at 1.64)"


# ---- the engine: ONE glow system, the chip's light --------------------------------------------------------------


def _block() -> str:
    src = ENGINE.read_text(encoding="utf-8")
    return src[src.index("const LP_GLOW_EDGE = "):src.index("const lpPaintGlowEdges = ")]


def test_the_edge_is_the_fill_glow_on_its_stroke_never_a_second_glow_system():
    src = ENGINE.read_text(encoding="utf-8")
    paint = src[src.index("const lpPaintGlowEdges = "):]
    paint = paint[:paint.index("\n  };\n")]
    assert "lpFillGlow(st, g.path, edge, null, 1, LP_GLOW_EDGE)" in paint, "the halos are T10's filter on T49's dial form"
    assert "chipLitF(" in paint, "the light is the chip's `lit` (T12): its fade, its pulse"
    for prim in ("feGaussianBlur", "feFlood", "drop-shadow", "feMorphology"):
        assert prim not in _block() + paint, f"{prim}: the edge builds no filter of its own"
    assert src.index("const lpFillGlow = ") < src.index("const LP_GLOW_EDGE = ") < src.index("const buildPerform =")
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert "lpBuildGlowEdges(st, scene, surf)" in build and "datumBadges, glows }" in build
    perform = src[src.index("const paintPerform ="):]
    perform = perform[:perform.index("\n  };\n")]
    assert perform.index("lpPaintBarMorphs(st, scene, t, PF)") < perform.index("lpPaintGlowEdges(PF, t, st)"), \
        "the edge is drawn round the bar as the morph left it this frame"


def _dials() -> dict:
    m = re.search(r"const LP_GLOW_EDGE = Object\.freeze\(\{(.*?)\}\);", ENGINE.read_text(encoding="utf-8"), re.S)
    assert m, "LP_GLOW_EDGE"
    return {k: float(v) for k, v in re.findall(r"(\w+): ([0-9.]+),", m.group(1))}


def test_the_dials_are_the_fill_glows_four_plus_the_stroke_each_carrying_its_measured_frame():
    m = re.search(r"const LP_GLOW_EDGE = Object\.freeze\(\{(.*?)\}\);", ENGINE.read_text(encoding="utf-8"), re.S)
    for k in ("STROKE_PX", "CORE_MIX", "INNER_PX", "INNER_A", "OUTER_PX", "OUTER_A"):
        assert re.search(k + r": [0-9.]+,?\s*/\*[^*]*\[MEASURED: [^\]]*BUB #3[^\]]*\]", m.group(1)), k
    assert set(_dials()) == {"STROKE_PX", "CORE_MIX", "INNER_PX", "INNER_A", "OUTER_PX", "OUTER_A"}, \
        "T49's dial form (INNER / OUTER) and the outline's own two - nothing else"


def _bub_root() -> Path | None:
    cands = [os.environ.get("BRAVOS_FRAMES_ROOT"), str(ROOT)]
    if ".claude" in ROOT.parts:
        cands.append(str(Path(*ROOT.parts[:ROOT.parts.index(".claude")])))
    return next((Path(c) for c in cands if c and (Path(c) / BUB3).exists()), None)


def test_the_bravos_edge_reads_back_as_pinned():
    import measure_line_bloom as M
    root = _bub_root()
    if root is None:
        pytest.skip("BUB #3's frame is not on disk (gitignored): set BRAVOS_FRAMES_ROOT")
    got = M.measure(root / BUB3, "#FFFFFF", BUB_BOX, exclude=BUB_EXCLUDE)
    for k, v in BUB_READ.items():
        assert got[k] == pytest.approx(v, abs=0.01 if k != "core_L" else 0.05), (k, got[k], v)


# ---- the card ----------------------------------------------------------------------------------------------------


def test_the_card_is_on_page_species_with_its_use_when():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["page_species:glow"]
    assert card["token"] == "glow" and card["when"] is None and card["serves"] == ["RANKS"]
    assert card["lives"]["form"] == "inline" and card["lives"]["symbol"] == "lpPaintGlowEdges"
    assert any(a["source"].startswith("docs/research/bravos-style/BRAVOS-USE-WHEN.md:") for a in card["aliases"])
    assert len(card["does"]) <= 240 and card["proof"]["golden"] == "glow-outline-bar"
    assert "P71 T29" in card["doctrine"] and "E99 s130" in card["doctrine"] and "E99 s71" in card["doctrine"]


def test_the_registries_know_the_glow():
    import gate_motion_density as G
    import lint_species_choice as L
    import recipe_walk as RW
    from authoring import shapes as SH
    assert "glow" in G.PLOT_INK_MARKS and "glow" in G.PLOT_HELD_MARKS
    assert "glow" in SH.PLOT_MARKS and "glow" in SH.HELD_MARKS
    assert "glow" in L.ACT_SPECIES["RANKS"]
    assert "glow" in RW.PAGE_SPECIES_KINDS
    assert SH.marks_live([dict(GLOW)], 20.0, 24.0) == ["glow at 1.09s"], "the landed edge is still on the bar"


# ---- the edge read on the served player --------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        with SP.browser():
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = r"""() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  if (!world) return null;
  const st = world.__lp, PF = st.perform || {}, S = (st.states && st.states[st.active | 0]) || st;
  const sr = document.getElementById('stage').getBoundingClientRect(), ox = Math.round(sr.x), oy = Math.round(sr.y);   // frame_png clips the stage here
  const R = (e) => { const r = e.getBoundingClientRect(); return [r.left - ox, r.top - oy, r.right - ox, r.bottom - oy]; };
  const out = { n: (PF.glows || []).length, fills: document.querySelectorAll('filter[id^="lpfill-"]').length,
                bars: (S.bars || []).map(b => ({ box: R(b.bar), ink: b.bar.style.fill || '' })),
                spans: (PF.spans || []).map(sd => R(sd.rect)), glows: [] };
  for (const g of PF.glows || []) {
    const p = g.path, id = ((p.style.filter || '').match(/#([^")]+)/) || [])[1], f = id ? document.getElementById(id) : null;
    const so = p.getAttribute('stroke-opacity');   // the level: the edge is lit by its stroke's opacity (its halos are that stroke's gaussian)
    out.glows.push({ op: +(p.getAttribute('opacity') || 0) * (so == null ? 1 : +so), filter: p.style.filter || '', box: R(p), stroke: p.getAttribute('stroke'),
      sw: +p.getAttribute('stroke-width'), prev: p.previousSibling && p.previousSibling.getAttribute ? (p.previousSibling.getAttribute('class') || '') : '',
      flood: f ? [...f.querySelectorAll('feFlood')].map(e => [e.getAttribute('flood-color'), +e.getAttribute('flood-opacity')]) : null,
      blur: f ? [...f.querySelectorAll('feGaussianBlur')].map(e => +e.getAttribute('stdDeviation')) : null });
  }
  return out;
}"""


def _serve(tl: dict, uris: dict):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    page, errs, close = SP.open_served(html, 1920, 1080, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    def png(t: float) -> bytes:
        return RB.frame_png(page, t, (1920, 1080))

    return at, png, errs, close


def _near(a, b, tol=1.5) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def _mix(hx: str, m: float) -> str:
    h = hx.lstrip("#")
    return "#" + "".join("%02x" % round(int(h[i:i + 2], 16) + (255 - int(h[i:i + 2], 16)) * m) for i in (0, 2, 4))


def _bar_ink_hex() -> str:
    src = ENGINE.read_text(encoding="utf-8")
    return re.search(r'const LP_INK = \{ crimson: "(#[0-9A-Fa-f]{6})"', src).group(1).lower()


@needs_browser
def test_the_edge_lands_on_its_word_round_the_bar_as_it_is_drawn_and_holds():
    import build_golden_sources as G
    tl, uris = G.glow_outline_bar()
    at, _png, errs, close = _serve(tl, uris)
    try:
        before, landing, growing, stood, later = at(G.GLOW_AT - 0.2), at(G.GLOW_AT + 0.05), at(1.3), at(G.FRAME_T["glow-outline-bar"]), at(8.0)
    finally:
        close()
    assert not errs, errs
    assert before["glows"][0]["op"] == 0 and before["glows"][0]["filter"] == "" and before["fills"] == 0, before
    assert 0 < landing["glows"][0]["op"] < 1, ("it comes up on the chip's landing fade from its word", landing["glows"][0])
    for f in (growing, stood):
        g, bar = f["glows"][0], f["bars"][0]
        assert g["op"] == 1 and "#lpfill-" in g["filter"], g
        assert _near(g["box"], bar["box"], 0.5), ("the edge follows the bar AS IT IS DRAWN (the grow)", g["box"], bar["box"])
    assert growing["bars"][0]["box"][1] > stood["bars"][0]["box"][1] + 1, "(the bar was still growing at 1.3: its ease's tail)"
    g, ink = stood["glows"][0], _bar_ink_hex()
    assert g["stroke"] == _mix(ink, _dials()["CORE_MIX"]), ("the edge burns near-white: the bar's ink mixed CORE_MIX to white", g)
    assert [c.lower() for c, _ in g["flood"]] == [g["stroke"]] * 2, ("both halos in the edge's own light - the bar's ink burning "
                                                                  "toward white (BUB #3's glow is the hot line's)", g["flood"])
    d = _dials()
    assert [a for _, a in g["flood"]] == pytest.approx([d["INNER_A"], d["OUTER_A"]]), g["flood"]
    assert g["blur"][1] / g["blur"][0] == pytest.approx(d["OUTER_PX"] / d["INNER_PX"], rel=1e-3), g["blur"]
    assert "bar" in g["prev"] or "lp-bar-glow" in g["prev"], ("it stands on the bar's own layer, right over it", g["prev"])
    assert later["glows"][0] == g, "it HOLDS - an annotation (s91)"


@needs_browser
def test_a_pulsed_glow_blinks_on_the_chips_clock_then_holds():
    import build_golden_sources as G
    import gate_motion_density as GM
    tl, uris = G.glow_outline_bar(glow={"pulse": True, "dur": 3.0})
    at, _png, errs, close = _serve(tl, uris)
    cp = GM.CHIP_PULSE
    on0 = G.GLOW_AT + cp["land_s"]
    try:
        mid = [at(on0 + k * cp["s"] + cp["s"] / 2)["glows"][0]["op"] for k in range(cp["n"])]
        between, after = at(on0 + cp["s"] - 0.01)["glows"][0]["op"], at(on0 + cp["n"] * cp["s"] + 0.2)["glows"][0]["op"]
    finally:
        close()
    assert not errs, errs
    low = float(re.search(r"PULSE_LOW: ([0-9.]+)", ENGINE.read_text(encoding="utf-8")).group(1))
    assert all(m == pytest.approx(low, abs=0.01) for m in mid), ("each blink dips to the chip's PULSE_LOW", mid)
    assert between > 0.95 and after == 1, (between, after)


@needs_browser
def test_absent_its_word_the_page_is_the_page_without_the_species():
    import build_golden_sources as G
    at1, png1, errs1, close1 = _serve(*G.glow_outline_bar())
    try:
        a = png1(G.GLOW_AT - 0.05)
    finally:
        close1()
    at0, png0, errs0, close0 = _serve(*G.glow_outline_bar(glow={}))
    try:
        b = png0(G.GLOW_AT - 0.05)
    finally:
        close0()
    assert not errs1 and not errs0, (errs1, errs0)
    from PIL import Image
    assert Image.open(io.BytesIO(a)).convert("RGB").tobytes() == Image.open(io.BytesIO(b)).convert("RGB").tobytes(), \
        "before its word the glow adds not one pixel"


@needs_browser
def test_it_leaves_with_its_page():
    import build_golden_sources as G
    tl, uris = G.glow_outline_bar(glow={"leave_at": 6.0, "leave_s": 0.5})
    at, _png, errs, close = _serve(tl, uris)
    try:
        held, gone = at(5.9)["glows"][0], at(6.6)["glows"][0]
    finally:
        close()
    assert not errs, errs
    assert held["op"] == 1 and gone["op"] == 0 and gone["filter"] == "", (held, gone)


def _two_bars(species: list) -> tuple[dict, dict]:
    import build_golden_sources as G
    world = _world(TWO)
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        B.stamp_full_stage(world["page"])
        B.check_solo(world, [s for s in species if s["kind"] == "solo"])
        B.check_glow(world, species)
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline("probe: a glow under a solo", scenes, {}, "16:9"), G._base_uris()


@needs_browser
def test_a_solo_on_another_bar_sheds_the_glow_and_on_its_own_bar_keeps_it():
    other = _two_bars([dict(GLOW, at=3.5), {"kind": "solo", "at": 6.0, "dur": 0.6, "bar": 1}])
    own = _two_bars([dict(GLOW, at=3.5), {"kind": "solo", "at": 6.0, "dur": 0.6, "bar": 0}])
    reads = {}
    for name, (tl, uris) in (("other", other), ("own", own)):
        at, _png, errs, close = _serve(tl, uris)
        try:
            reads[name] = (at(5.5)["glows"][0]["op"], at(9.0)["glows"][0])
        finally:
            close()
        assert not errs, errs
    assert reads["other"][0] == 1 and reads["other"][1]["op"] == 0 and reads["other"][1]["filter"] == "", \
        ("a muted bar carries no glow (s130)", reads["other"])
    assert reads["own"][0] == 1 and reads["own"][1]["op"] == 1, ("the named bar keeps its light", reads["own"])


@needs_browser
def test_a_span_glow_edges_the_region_in_its_ink():
    import build_golden_sources as G
    species = [dict(SPAN), {"kind": "glow", "at": 3.2, "dur": 0.5, "span": 0}]
    world = _world(LINE)
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        B.stamp_full_stage(world["page"])
        assert B.check_glow(world, species) == []
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    at, _png, errs, close = _serve(G._timeline("probe: a span's edge", scenes, {}, "16:9"), G._base_uris())
    try:
        f = at(5.0)
    finally:
        close()
    assert not errs, errs
    g = f["glows"][0]
    cobalt = re.search(r'cobalt: "(#[0-9A-Fa-f]{6})"', ENGINE.read_text(encoding="utf-8").split("const LP_INK = ")[1]).group(1).lower()
    assert g["op"] == 1 and _near(g["box"], f["spans"][0]), (g["box"], f["spans"])
    assert g["stroke"] == _mix(cobalt, _dials()["CORE_MIX"]) and [c.lower() for c, _ in g["flood"]] == [g["stroke"]] * 2, g


def _our_box(bar_box: list) -> tuple[list, list]:
    """The bar's RIGHT edge (the plot beside it is empty on a one-bar page): the middle 60 % of its height, 130 px out,
    the bar's own inside left out - the same geometry as BUB's read (one straight edge, its outside)."""
    x0, y0, x1, y1 = bar_box
    h = y1 - y0
    top, bot = y0 + 0.2 * h, y0 + 0.8 * h
    return [x1 - 20, top, x1 + 130, bot], [[x1 - 20, top, x1 - 3, bot]]


@needs_browser
def test_our_edge_reads_as_bravos_lit_region_at_its_own_512_px(tmp_path):
    import build_golden_sources as G
    import measure_line_bloom as M
    tl, uris = G.glow_outline_bar()
    at, png, errs, close = _serve(tl, uris)
    t = G.FRAME_T["glow-outline-bar"]
    try:
        f = at(t)
        (tmp_path / "ours.png").write_bytes(png(t))
    finally:
        close()
    assert not errs, errs
    box, ex = _our_box(f["glows"][0]["box"])
    got = M.measure(tmp_path / "ours.png", "#FFFFFF", box, exclude=ex, at_width=512)
    for k, v in BUB_READ.items():
        assert abs(got[k] - v) <= TOL[k], (k, got[k], v, TOL[k])


SEEK_T = [2.0, 4.0, 6.5]


@needs_browser
@pytest.mark.parametrize("t", SEEK_T)
def test_a_cold_seek_and_a_played_frame_paint_the_same_edge(t):
    """The lpHotFilter rule, on the edge's own region (the bar and 150 px round it): forward play in 0.1 s steps into
    each instant paints the cold seek's pixels - mid-grow, held, and mid-blink."""
    import build_golden_sources as G
    from PIL import Image
    tl, uris = G.glow_outline_bar(glow={"pulse": True, "dur": 6.0})
    at, png, errs, close = _serve(tl, uris)
    try:
        cold, box = png(t), at(t)["glows"][0]["box"]
    finally:
        close()
    at, png, errs2, close = _serve(tl, uris)
    try:
        for x in [round(t - 1.0 + 0.1 * i, 2) for i in range(10)]:
            png(x)
        played = png(t)
    finally:
        close()
    assert not errs and not errs2, (errs, errs2)
    crop = (int(box[0]) - 150, int(box[1]) - 150, int(box[2]) + 150, int(box[3]) + 60)
    rd = lambda b: Image.open(io.BytesIO(b)).convert("RGB").crop(crop).tobytes()  # noqa: E731
    assert rd(played) == rd(cold), f"at {t}: forward play paints another edge than the cold seek"
