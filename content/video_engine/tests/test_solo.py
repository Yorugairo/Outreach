"""P69 T37 - SOLO: the on-word isolate for a line or a bar (the rest mute to E67's dim).

The Bravos harvest v2 ranks it second (A12 lines, 8 of 9 videos; A49 bars; S9 the legend chip, left alone here):
"peers ghost, one series stays lit" - JPN 05:23.5 (`docs/research/runs/bravos-watch/nB1eXWQlW58/luna-recovery/
focus-05-treasury-holdings/frames/frame_0008.jpg`): Japan's line bright, China and the UK muted, the legend readable.

The token is a PAGE species: `{"kind": "solo", "at", "dur", "series": i}` on a line page or `{"kind": "solo", "at",
"dur", "bar": i}` on a bars page; `{"kind": "unsolo", "at", "dur"}` restores. The law and the painter are
species/solo.mjs (pinned by tests/kinetics/solo.test.mjs); this file pins the compiler's grammar and the page it may
stand on, the engine's wiring, the card, the gate's credit, the lint's acts, and the mute read on the SERVED player
(the golden `solo-chipmakers`: Steel and Paper H row 10's divergence page and its own sentence, "Chipmakers doubling
while their customers sit flat at the index is textbook profit-taking").
"""
from __future__ import annotations

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

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/solo.mjs"
# P69 T37b (E99 s117 (2)): the dim is the module's own dial, read off it - never re-typed here
DIM = float(re.search(r"DIM: ([0-9.]+),", MODULE.read_text(encoding="utf-8")).group(1))
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
PLATE = "ledger:ev-divergence-v1:line"
SOLO = {"kind": "solo", "at": 12.0, "dur": 0.71, "series": 1}
UNSOLO = {"kind": "unsolo", "at": 15.66, "dur": 0.54}


def _errs(entries, plate=PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _line_world(n: int = 4) -> dict:
    return {"kind": "ledger", "page": {"builder": "dense-line", "series": [{} for _ in range(n)]}}


def _bars_world(n: int = 3) -> dict:
    return {"kind": "ledger", "page": {"builder": "story", "values": list(range(1, n + 1)), "labels": ["x"] * n}}


# ---- the grammar -------------------------------------------------------------------------------------------


def test_the_tokens_are_page_species_the_compiler_accepts():
    for kind in ("solo", "unsolo"):
        assert kind in B.SPECIES_KINDS and kind in B.PAGE_SPECIES, kind
    assert _errs([SOLO]) == []
    assert _errs([SOLO, UNSOLO]) == []
    assert _errs([{"kind": "solo", "at": 3.0, "dur": 0.4, "bar": 0}], plate="ledger:ev-hbm-wafer-ratio-bars-v1:bars") == []


def test_it_performs_on_a_ledger_page_only():
    errs = _errs([SOLO], plate="plate-plain")
    assert any("solo is a page species" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"series": None}, "series must be a non-negative integer"),
    ({"series": -1}, "series must be a non-negative integer"),
    ({"series": True}, "series must be a non-negative integer"),
    ({"bar": 0}, "names ONE mark - a series (a line page) or a bar (a bars page), not both"),
    ({"series": 1.0}, "series must be a non-negative integer"),
    ({"dur": 0.1}, "the mute eases over 0.2-1.5 s"),
    ({"dur": 2.2}, "the mute eases over 0.2-1.5 s"),
    ({"label": "CHIPS"}, "a solo writes nothing"),
    ({"color": "teal"}, "a solo writes nothing"),
])
def test_a_malformed_solo_is_refused_by_name(patch, needle):
    errs = _errs([dict(SOLO, **patch)])
    assert any(needle in e for e in errs), (patch, errs)


def test_a_solo_that_names_nothing_is_refused():
    errs = _errs([{"kind": "solo", "at": 1.0, "dur": 0.5}])
    assert any("names ONE mark" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"series": 0}, "an unsolo names nothing"),
    ({"dur": 3.0}, "the mute eases over 0.2-1.5 s"),
])
def test_a_malformed_unsolo_is_refused_by_name(patch, needle):
    errs = _errs([SOLO, dict(UNSOLO, **patch)])
    assert any(needle in e for e in errs), (patch, errs)


def test_the_compiler_bounds_the_mark_on_the_page_it_stands_on():
    B.check_solo(_line_world(), [dict(SOLO)])
    B.check_solo(_bars_world(), [{"kind": "solo", "at": 1.0, "dur": 0.4, "bar": 2}])
    with pytest.raises(ValueError, match=r"solo: series 4 is past the page's last series \(3\)"):
        B.check_target_series(_line_world(), [dict(SOLO, series=4)])   # R26-218's own bound, shared
    with pytest.raises(ValueError, match=r"solo: bar 3 is past the page's last bar \(2\)"):
        B.check_solo(_bars_world(), [{"kind": "solo", "at": 1.0, "dur": 0.4, "bar": 3}])
    with pytest.raises(ValueError, match="a LINE page's marks are its series - name `series`"):
        B.check_solo(_line_world(), [{"kind": "solo", "at": 1.0, "dur": 0.4, "bar": 0}])
    with pytest.raises(ValueError, match="a BARS page's marks are its bars - name `bar`"):
        B.check_solo(_bars_world(), [dict(SOLO)])


@pytest.mark.parametrize("world, needle", [
    (_line_world(1), "one series - there is nothing to dim"),
    (_bars_world(1), "one bar - there is nothing to dim"),
    ({"kind": "ledger", "page": {"builder": "tiers", "tiers": [{}, {}]}}, "tiers is not a page solo draws on"),
    ({"kind": "ledger", "page": {"builder": "panels", "panels": [{}, {}]}}, "panel_focus"),
    ({"kind": "ledger", "page": {"builder": "share"}}, "share is not a page solo draws on"),
    ({"kind": "ledger", "page": {"builder": "story", "values": [1, 2], "form": "extruded_bar"}}, "form=extruded_bar"),
    ({"kind": "ledger", "page": {"builder": "story", "values": [1, 2], "members": [[{"name": "A"}], None]}},
     "the member species' `light`"),
])
def test_a_page_solo_does_not_draw_is_refused_by_name(world, needle):
    sp = {"kind": "solo", "at": 1.0, "dur": 0.4, "bar": 0} if world["page"]["builder"] == "story" else dict(SOLO, series=0)
    with pytest.raises(ValueError, match=needle.replace("(", r"\(").replace(")", r"\)")):
        B.check_solo(world, [sp])


def test_an_unsolo_with_no_solo_before_it_restores_nothing_and_is_refused():
    with pytest.raises(ValueError, match="unsolo at 5.0: no solo stands before it"):
        B.check_solo(_line_world(), [{"kind": "unsolo", "at": 5.0, "dur": 0.4}, dict(SOLO, at=6.0)])
    B.check_solo(_line_world(), [dict(SOLO, at=4.0), {"kind": "unsolo", "at": 5.0, "dur": 0.4}])


def test_a_page_with_no_solo_is_untouched():
    B.check_solo({"kind": "ledger", "page": {"builder": "tiers"}}, [{"kind": "figure", "at": 1.0, "dur": 1.0}])
    B.check_solo({"kind": "plate"}, [])


def test_the_row_path_calls_the_check():
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    body = src[src.index("def derive_rescale_states"):]
    assert "check_solo(world, row_species)" in body[:body.index("for sp in")], "the page's marks are known here"


def test_the_whens_say_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["solo"]
    assert 30 <= len(when) <= 400 and "\n" not in when, len(when)
    for word in ("ONE", "COMPARES", "RANKS", "never", "comparison"):
        assert word in when, word
    assert "restores" in B.SPECIES_WHEN["unsolo"] and "comparison" in B.SPECIES_WHEN["unsolo"]


# ---- the lane's registries -------------------------------------------------------------------------------------


def test_the_gate_credits_the_mute_and_the_restore_one_event_each():
    import gate_motion_density as G
    assert G.SPECIES_EVENTS["solo"] == ("at",) and G.SPECIES_EVENTS["unsolo"] == ("at",)


def test_the_lint_lists_it_under_its_two_acts_and_the_walk_names_its_card():
    import lint_species_choice as L
    import recipe_walk as RW
    assert "solo" in L.ACT_SPECIES["COMPARES"] and "solo" in L.ACT_SPECIES["RANKS"]
    assert "solo" in L.PROPOSE_FILL
    assert {"solo", "unsolo"} <= RW.PAGE_SPECIES_KINDS


def test_the_solo_adds_no_mark_to_the_plot():
    """A solo re-inks what the page drew; it draws nothing a card could cover (authoring/shapes.PLOT_MARKS)."""
    from authoring import shapes
    assert "solo" not in shapes.PLOT_MARKS and "unsolo" not in shapes.PLOT_MARKS


# ---- the engine's wiring -----------------------------------------------------------------------------------


def test_the_engine_carries_the_module_and_paints_it_from_the_perform_layer():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN solo */" in src
    assert (src.index("/* KINETICS:BEGIN lit_stretch */") < src.index("/* KINETICS:BEGIN solo */")
            < src.index("const paintPerform ="))
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert 'pageSpecies(scene, "solo")' in build and 'pageSpecies(scene, "unsolo")' in build
    perform = src[src.index("const paintPerform ="):]
    perform = perform[:perform.index("\n  };\n")]
    assert "PAGE_PAINTERS.solo" in perform, "the perform layer paints it through the page registry"
    assert perform.index("PAGE_PAINTERS.lit_stretch") < perform.index("PAGE_PAINTERS.solo"), \
        "after the lights, so a light on a muted series mutes with it"


def test_the_card_is_on_page_species_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["page_species:solo"]
    assert card["token"] == "solo" and card["when"] is None and card["serves"] == ["COMPARES", "RANKS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/solo.mjs", "symbol": "paintSolo"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/solo.mjs", "object": "SOLO"}
    assert [o["token"] for o in card["options"]] == ["unsolo"]
    assert len(card["does"]) <= 240 and len(card["title"]) <= 40 and card["proof"]["golden"] == "solo-chipmakers"
    assert "E67" in card["doctrine"]
    assert any("BRAVOS-USE-WHEN.md" in a["source"] for a in card["aliases"]), "the use-when guide's entries name it"


# ---- the mute, read on the served player ----------------------------------------------------------------------


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
  const st = world.__lp, a = (el, k) => (el && el.getAttribute(k) !== null ? +el.getAttribute(k) : 1);
  return { paths: (st.paths || []).map(pp => ({ si: pp.si | 0, op: a(pp.p, 'opacity'), tip: a(pp.tip, 'fill-opacity'),
                                                name: a(pp.name, 'fill-opacity'), nameOp: a(pp.name, 'opacity') })),
           bars: (st.bars || []).map(b => ({ i: b.i, op: a(b.bar, 'opacity'), val: a(b.val, 'fill-opacity'),
                                             lab: a(b.lab, 'fill-opacity') })),
           lits: ((st.perform || {}).lits || []).map(L => ({ si: L.si, g: a(L.g, 'opacity') })) };
}"""


def _serve_tl(tl: dict, uris: dict, aspect: str = "16:9"):
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


def _by_series(frame: dict) -> dict[int, float]:
    out: dict[int, float] = {}
    for p in frame["paths"]:
        out[p["si"]] = p["op"]
    return out


@needs_browser
def test_on_its_word_the_other_series_mute_and_the_named_one_keeps_its_ink():
    """The golden's own beat, read as alpha at five instants: nothing before "Chipmakers"; the chips alone at full ink
    once the mute has eased; on "customers" the mute hands over to the mega-cap line (continuously - mid-hand-over
    both sit between the two alphas); on "textbook" every series is back."""
    import build_golden_sources as G
    import render_baseline as RB
    tl, uris, _t, aspect = RB.load_surface("solo-chipmakers")
    at, errs, close = _serve_tl(tl, uris, aspect)
    try:
        s1, s2, un = G.SOLO_CHIPS_AT, G.SOLO_CUSTOMERS_AT, G.SOLO_UNSOLO_AT
        before, chips, mid, customers, back = (at(s1 - 0.3), at(s1 + G.SOLO_CHIPS_DUR + 0.2), at(s2 + G.SOLO_CUSTOMERS_DUR / 2),
                                               at(s2 + G.SOLO_CUSTOMERS_DUR + 0.2), at(un + G.SOLO_UNSOLO_DUR + 0.2))
    finally:
        close()
    assert not errs, errs
    assert set(_by_series(before).values()) == {1}, before
    dim = DIM
    got = _by_series(chips)
    assert got[G.SOLO_CHIPS] == 1 and all(abs(v - dim) < 1e-3 for k, v in got.items() if k != G.SOLO_CHIPS), got
    for p in chips["paths"]:
        want = 1 if p["si"] == G.SOLO_CHIPS else dim
        assert abs(p["tip"] - want) < 1e-3 and abs(p["name"] - want) < 1e-3, p   # the lead point and the end tag mute with it
    m = _by_series(mid)
    assert dim < m[G.SOLO_CHIPS] < 1 and dim < m[G.SOLO_CUSTOMERS] < 1, m
    got = _by_series(customers)
    assert got[G.SOLO_CUSTOMERS] == 1 and abs(got[G.SOLO_CHIPS] - dim) < 1e-3, got
    assert set(_by_series(back).values()) == {1}, back


BARS_OBJ = "ev-hbm-wafer-ratio-bars-v1"   # H row 21's wafer compare: "Standard DRAM" and "HBM (stacked dies)"


@needs_browser
def test_on_a_bars_page_the_other_bars_and_their_values_mute_and_the_names_stay():
    import build_golden_sources as G
    plate = "ledger:%s:bars" % BARS_OBJ
    species = [{"kind": "solo", "at": 10.0, "dur": 0.5, "bar": 1}]
    assert _errs(species, plate=plate) == []
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(plate, (0, 0, 0), PROJECT)
        B.stamp_full_stage(world["page"])
        B.check_solo(world, species)
    finally:
        B.ASPECT = saved
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    at, errs, close = _serve_tl(G._timeline("probe: a bar solo", scenes, {}, "16:9"), G._base_uris())
    try:
        before, after = at(9.8), at(11.0)
    finally:
        close()
    assert not errs, errs
    assert all(b["op"] == 1 and b["val"] == 1 for b in before["bars"]), before
    lit, other = after["bars"][1], after["bars"][0]
    assert lit["op"] == 1 and lit["val"] == 1, lit
    assert abs(other["op"] - DIM) < 1e-3 and abs(other["val"] - DIM) < 1e-3, other
    assert all(b["lab"] == 1 for b in after["bars"]), "the category names are the page's key - never muted"


@needs_browser
def test_a_light_on_a_muted_series_mutes_with_it_and_a_light_on_the_named_one_keeps_its_ink():
    import build_golden_sources as G
    tl, uris = G.solo_chipmakers()
    sc = tl["scenes"][0]
    lits = [{"kind": "lit_stretch", "at": 9.0, "dur": 1.0, "from": 0, "to": 120, "series": G.SOLO_CHIPS},
            {"kind": "lit_stretch", "at": 9.0, "dur": 1.0, "from": 0, "to": 120, "series": 0}]
    sc["species"] = lits + [s for s in sc["species"] if s["kind"] == "solo"][:1]
    at, errs, close = _serve_tl(tl, uris)
    try:
        f = at(G.SOLO_CHIPS_AT + G.SOLO_CHIPS_DUR + 0.2)
    finally:
        close()
    assert not errs, errs
    by = {L["si"]: L["g"] for L in f["lits"]}
    assert by[G.SOLO_CHIPS] == 1, by
    assert abs(by[0] - DIM) < 1e-3, by
