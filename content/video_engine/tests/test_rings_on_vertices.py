"""P69 T47 - RINGS IN TURN ON EVERY VERTEX, AND THE VALLEY LIT (E99 s109 (3), s110 (2), E56).

The operator, 2026-09-23: "the rings on every vertex is valid when the discussion is literally about the vertex - I
for example rings at repeating near similar peaks, and a highlight on the valley". s110 (2) then reads E56's one use
as "the ring marks what the sentence points at" - and here the sentence points at EACH vertex in turn.

THE FINDING (acceptance step 1): this is a RECIPE and a use-when, not engine work. N `ring` species on N datums
already compile - `validate_species` checks each entry on its own (`_validate_ring` restates E56 per ring: a datum
target or a label with a digit) and counts no rings per row - and already read: the engine paints every stage
species from its OWN `at` / `dur` (`paintSpecies`: `k = (t - sp.at) / dur`, painted while 0 <= k <= 1), so each ring
closes on its own word and the ones before it HOLD for as long as their `dur` runs. The approved Japan short's s03
fires six callouts in turn on one row, each held to the row's end (`recipe:trace-callout-ladder`, proven, count 4).
The valley's light is T36's `lit_stretch` from one peak to the next, untouched.

The beat is the golden `rings-on-vertices`: the 20-year Treasury yield (FRED DGS20, the american-debt-trap object,
REAL) topped out near five percent three times in 2025 - 5.06 % (Jan 14), 5.08 % (May 21), 5.02 % (Jul 15) - and
between the first two it fell to 4.44 % (Apr 4). Each peak is ringed on its word with its own value; the three hold
together to the row's word; then the light walks the valley from the first peak through the trough to the second,
and the trough's figure is written. This file pins the data's honesty, the grammar, the recipe, the golden's beat,
and the rings landing IN TURN on the served player (never all at once).
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/american-debt-trap"
SERIES = PROJECT / "evidence/objects/treasury-20y-yield.series.json"
RECIPE = ROOT / "content/video_engine/effects/recipes/rings-in-turn-on-the-vertices.json"
RECIPE_SCHEMA = ROOT / "content/video_engine/configs/effect_recipe.schema.json"
SURFACE = "rings-on-vertices"
PEAKS, VALLEY = (8, 96, 132), 64        # the series' own indices: three near-equal tops and the trough between the first two


def _pts() -> list:
    return json.loads(SERIES.read_text(encoding="utf-8"))["series"][0]["pts"]


def _golden():
    import build_golden_sources as G
    return G


# ---- the data: three REAL near-equal peaks and the valley between (E53 / s109 (4): the story on honest data) ------------


def test_the_three_vertices_are_the_series_own_near_equal_tops():
    pts = _pts()
    ys = [p[1] for p in pts]
    for i in PEAKS:
        lo, hi = max(0, i - 20), min(len(ys), i + 21)
        assert ys[i] == max(ys[lo:hi]), f"datum {i} ({ys[i]}) is not a top of its own neighbourhood"
    tops = [ys[i] for i in PEAKS]
    assert max(tops) - min(tops) <= 0.06 + 1e-9, tops                 # near-equal: 5.02 .. 5.08
    assert min(ys[PEAKS[0]:PEAKS[1] + 1]) == ys[VALLEY] == 4.44          # the trough between the first two peaks
    assert all(max(ys[a:b + 1]) <= max(ys[a], ys[b]) for a, b in zip(PEAKS, PEAKS[1:])), \
        "no higher top stands between two ringed vertices - they are the repeated tops, not three points on a climb"


def test_every_ring_writes_its_own_datum_value_and_the_trough_figure_its_own():
    G, pts = _golden(), _pts()
    rings = [e for e in G.VERTEX_SPECIES if e["kind"] == "ring"]
    assert [r["target"]["index"] for r in rings] == list(PEAKS)
    assert [r["label"] for r in rings] == [f"{pts[i][1]:.2f}%" for i in PEAKS]
    fig = next(e for e in G.VERTEX_SPECIES if e["kind"] == "figure")
    assert fig["target"]["index"] == VALLEY and fig["text"] == f"{pts[VALLEY][1]:.2f}%"


# ---- the grammar: N rings compile as they stand; E56 is still checked per ring ------------------------------------------


def _ring(at: float, i: int, label: str, until: float = 16.0) -> dict:
    return {"kind": "ring", "at": at, "dur": round(until - at, 2), "form": "dashed", "label": label,
            "target": {"kind": "datum", "index": i, "series": 0}}


THREE = [_ring(5.8, 8, "5.06%"), _ring(7.1, 96, "5.08%"), _ring(8.4, 132, "5.02%")]
VALLEY_LIGHT = {"kind": "lit_stretch", "at": 10.2, "dur": 1.6, "from": 8, "to": 96, "series": 0}


def test_three_rings_in_turn_and_the_valley_light_compile_on_one_ledger_row():
    plate = "ledger:treasury-20y-yield:line:427:right"
    assert B.validate_species([dict(e) for e in THREE + [VALLEY_LIGHT]], (0, 0, 0), plate) == []
    world = {"kind": "ledger", "page": {"builder": "dense-line", "series": [{}]}}
    B.check_target_series(world, [dict(e) for e in THREE + [VALLEY_LIGHT]])   # one series on the page: every target is on it


def test_e56_is_still_read_ring_by_ring_a_ring_on_a_picture_on_the_same_row_is_refused():
    off_chart = {"kind": "ring", "at": 9.0, "dur": 2.0, "form": "dashed", "label": "the top",
                 "target": {"kind": "region", "x0": 0.1, "y0": 0.1, "x1": 0.3, "y1": 0.3}}
    errs = B.validate_species([dict(e) for e in THREE + [off_chart]], (0, 0, 0), "ledger:treasury-20y-yield:line:427:right")
    assert len(errs) == 1 and "a ring circles a NUMBER or a POINT ON A CHART (E56)" in errs[0], errs


# ---- the golden's beat and the recipe -------------------------------------------------------------------------------


def test_the_golden_is_the_beat_rings_in_turn_on_their_words_then_the_valley_lit():
    G = _golden()
    assert SURFACE in G.SURFACES and SURFACE in G.FRAME_T
    ats = [e["at"] for e in G.VERTEX_SPECIES if e["kind"] == "ring"]
    assert ats == sorted(ats) and len(set(ats)) == 3, "each ring on its OWN word, in reading order"
    ends = {round(e["at"] + e["dur"], 2) for e in G.VERTEX_SPECIES if e["kind"] == "ring"}
    assert ends == {G.VERTEX_HOLD_UNTIL}, "the rings before the last HOLD: all three leave together on the row's word"
    light = next(e for e in G.VERTEX_SPECIES if e["kind"] == "lit_stretch")
    assert (light["from"], light["to"]) == PEAKS[:2] and light["at"] > max(ats), "the valley is lit after the last ring"
    tl, _uris = G.SURFACES[SURFACE]()
    assert tl["scenes"][0]["species"] == G.VERTEX_SPECIES
    assert G.FRAME_T[SURFACE] > light["at"] + light["dur"] * 0.8, "judged with the three rings standing and the valley lit"
    frames = sys.modules["build_golden_sources"].REPO / "content/video_engine/tests/golden"
    assert (frames / "sources" / f"{SURFACE}.timeline.json").is_file() and (frames / "frames" / f"{SURFACE}.png").is_file()
    import test_golden_frames as TG
    assert SURFACE in TG.SURFACES


def test_the_recipe_is_schema_valid_and_orders_the_rings_before_the_light():
    import jsonschema
    doc = json.loads(RECIPE.read_text(encoding="utf-8"))
    jsonschema.validate(doc, json.loads(RECIPE_SCHEMA.read_text(encoding="utf-8")))
    assert doc["id"] == "recipe:rings-in-turn-on-the-vertices" and doc["status"] == "candidate" and doc["count"] == 0
    cards = [m["card"] for m in doc["members"]]
    assert cards == ["page_builder:line", "species:ring", "species:ring", "species:ring", "page_species:lit_stretch",
                     "page_species:figure"], cards
    for word in ("vertices", "E56"):
        assert word in json.dumps(doc["use_when"]), word
    assert {"E99 s109", "E99 s110", "E56"} <= set(doc["doctrine"])


def test_the_recipe_fires_on_the_golden_at_the_offsets_it_names():
    """The golden is the recipe's proof on the drift gate's own matcher (a candidate carries no `proof`: no approved
    cut has played it yet, so the golden stands in, as `prop-stamped-onto-its-page`'s does)."""
    import recipe_walk as RW
    G = _golden()
    doc = json.loads(RECIPE.read_text(encoding="utf-8"))
    tl, _uris = G.SURFACES[SURFACE]()
    fires = RW.match(RW.events(tl), doc["members"], doc["window_s"], t0=0.0)
    assert fires, "the ordered members fire inside the window on the golden's clock"
    ats = [e["at"] for e in G.VERTEX_SPECIES if e["kind"] in ("ring", "lit_stretch", "figure")]
    assert fires[0].members_at == [0.0, *ats], fires[0].members_at


def test_the_walk_names_the_lit_stretch_by_its_card():
    """T36 carded the light on the page_species axis; the walk named it `species:lit_stretch`, a card that does not
    exist, so no recipe with the valley's light could ever fire (found by the test above)."""
    import recipe_walk as RW
    assert RW.species_card("lit_stretch") == "page_species:lit_stretch"
    assert RW.species_card("ring") == "species:ring"


# ---- the rings land IN TURN, read on the served player ----------------------------------------------------------------


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
  const gs = [...new Set([...document.querySelectorAll('#species path.rngdash, #species-under path.rngdash')].map(p => p.parentNode))];
  const rings = gs.map(g => {
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, n = 0;
    g.querySelectorAll('path.rngdash').forEach(p => {
      const v = ((p.getAttribute('d') || '').match(/-?\\d+(?:\\.\\d+)?/g) || []).map(Number);
      for (let i = 0; i + 1 < v.length; i += 2) { x0 = Math.min(x0, v[i]); x1 = Math.max(x1, v[i]); y0 = Math.min(y0, v[i + 1]); y1 = Math.max(y1, v[i + 1]); }
      n++;
    });
    const lab = g.querySelector('text.lab');
    return { n, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, label: lab ? lab.textContent : null };
  }).sort((a, b) => a.cx - b.cx);
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const L = world && world.__lp.perform && (world.__lp.perform.lits || [])[0];
  const datum = (i) => window.__lpDatum(null, 0, i);
  return { rings, lit: L ? parseFloat(L.g.getAttribute('opacity') || '0') : null, peaks: [8, 96, 132].map(datum) };
}"""


@pytest.fixture(scope="module")
def served():
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(SURFACE)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "probe.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        w, h = RB.STAGE[aspect]
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                page = br.new_context(viewport={"width": w, "height": h}).new_page()
                errs: list[str] = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)

                def at(t: float) -> dict:
                    page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                                  "s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                    return page.evaluate(PROBE)
                yield at, errs
                br.close()
        finally:
            srv.shutdown()


@needs_browser
def test_each_ring_lands_on_its_own_word_and_the_ones_before_it_hold(served):
    G = _golden()
    at, errs = served
    a1, a2, a3 = [e["at"] for e in G.VERTEX_SPECIES if e["kind"] == "ring"]
    closed = 0.6   # past the ring's DRAW_S (0.55): its ellipse has closed
    before, one, one_late, two, three = at(a1 - 0.2), at(a1 + closed), at(a2 - 0.05), at(a2 + closed), at(a3 + closed)
    assert not errs, errs
    assert before["rings"] == [], before
    assert len(one["rings"]) == 1 and len(one_late["rings"]) == 1, "the second ring waits for ITS word - never all at once"
    assert len(two["rings"]) == 2 and len(three["rings"]) == 3, (two, three)
    assert [r["label"] for r in three["rings"]] == ["5.06%", "5.08%", "5.02%"]
    for r_then, r_now in zip(one["rings"] + two["rings"][1:], three["rings"]):
        assert abs(r_then["cx"] - r_now["cx"]) < 0.5 and abs(r_then["cy"] - r_now["cy"]) < 0.5, "a landed ring HOLDS where it closed"
    # each ring sits on ITS peak: the rings are in stage px, `__lpDatum` in the page's own px (a uniform scale and an
    # offset apart), so the ring centres must be the peaks under ONE affine map - fitted on the outer two, read on the third
    xs, peaks_x = [r["cx"] for r in three["rings"]], [p[0] for p in three["peaks"]]
    k = (xs[2] - xs[0]) / (peaks_x[2] - peaks_x[0])
    assert k > 0 and abs(xs[1] - (xs[0] + k * (peaks_x[1] - peaks_x[0]))) < 1.5, (xs, peaks_x)
    assert all(abs(r["cy"] - (three["rings"][0]["cy"] + k * (p[1] - three["peaks"][0][1]))) < 1.5
               for r, p in zip(three["rings"], three["peaks"])), (three["rings"], three["peaks"])


@needs_browser
def test_the_valley_lights_after_the_rings_and_they_all_leave_together_on_the_rows_word(served):
    G = _golden()
    at, errs = served
    light = next(e for e in G.VERTEX_SPECIES if e["kind"] == "lit_stretch")
    dark, lit = at(light["at"] - 0.1), at(light["at"] + light["dur"] + 0.3)
    held, gone = at(G.VERTEX_HOLD_UNTIL - 0.1), at(G.VERTEX_HOLD_UNTIL + 0.1)
    assert not errs, errs
    assert dark["lit"] == 0 and len(dark["rings"]) == 3, dark
    assert lit["lit"] == 1 and len(lit["rings"]) == 3, "the valley lit UNDER the three standing rings"
    assert len(held["rings"]) == 3 and gone["rings"] == [], (held, gone)
