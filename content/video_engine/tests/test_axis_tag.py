"""P71 T9 (was P69 T38) - THE AXIS TAG and its DROP GUIDE: the named year becomes an accent pill on the x axis.

The Bravos harvest v2's A10 (n=7, rank 3; A42 / A43 the same pill): on its word the x-axis label the sentence NAMES
becomes an accent pill in its place - covering any neighbour it reaches - and on a line page a dotted guide drops
from the datum to it (never across a label, C14). A PAGE species; it stands until its page leaves (R26-219).

Pinned here: the grammar (refused by name when malformed or misplaced, P71 common rule (h)); the TRUTH on the page it
stands on (an x outside the domain, an x that is neither a tick nor a datum, a bars label no bar carries, a year the
pill would print over another year: refused - s109, E28); the crowding (a fourth tag standing in one hold WARNs with
its numbers, E99 s106); the registries; the engine's wiring; the card; and the golden's beat read on the served player.
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
import ledger_page as LPG  # noqa: E402

sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/axis_tag.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
PROJECT = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
PLATE = "ledger:ev-equip-ipp-gdp-v2:line"
TAG = {"kind": "axis_tag", "at": 10.0, "dur": 0.93, "x": 2000}


def _errs(entries, plate=PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _world(plate=PLATE):
    return B.world_for_plate(plate, (0, 0, 0), PROJECT)


# ---- the grammar -------------------------------------------------------------------------------------------


def test_the_token_is_a_page_species_the_compiler_accepts():
    assert B.SPECIES_AXIS_TAG == "axis_tag"
    for reg in (B.SPECIES_KINDS, B.PAGE_SPECIES, B.PANEL_SPECIES, B.PAGE_BOUND_SPECIES):
        assert "axis_tag" in reg
    assert B.SPECIES_TARGETS["axis_tag"] == (), "it names its x as the page's own value, never a coordinate"
    assert _errs([TAG]) == []
    assert _errs([dict(TAG, x="2000", label="2000", series=0, guide=False, keep=True)]) == []


def test_it_performs_on_a_ledger_page_only():
    errs = _errs([TAG], plate="plate-plain")
    assert any("axis_tag is a page species" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"x": None}, "axis_tag: 'x' must be"),
    ({"x": True}, "axis_tag: 'x' must be"),
    ({"x": ""}, "axis_tag: 'x' must be"),
    ({"x": float("nan")}, "axis_tag: 'x' must be"),
    ({"label": ""}, "axis_tag: label must be a non-empty string"),
    ({"label": 2000}, "axis_tag: label must be a non-empty string"),
    ({"series": -1}, "axis_tag: series must be a non-negative integer"),
    ({"guide": "yes"}, "axis_tag: guide must be true or false"),
    ({"keep": 1}, "keep must be true or false"),
    ({"text": "2000"}, "axis_tag: 'text' is not one of its keys"),
    ({"y": 11.5}, "axis_tag: 'y' is not one of its keys"),
])
def test_a_malformed_tag_is_refused_by_name(patch, needle):
    errs = _errs([dict(TAG, **patch)])
    assert any(needle in e for e in errs), (patch, errs)


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["axis_tag"]
    assert 30 <= len(when) <= 260 and "\n" not in when, len(when)
    for word in ("NAMES", "year", "never", "2-3"):
        assert word in when, word


# ---- the truth, on the page it stands on ------------------------------------------------------------------


def test_the_named_year_is_a_tick_and_a_datum_of_the_page_it_stands_on():
    w = _world()
    assert B.check_axis_tags(w, [dict(TAG)]) == []
    assert B.check_axis_tags(w, [dict(TAG, x="2000")]) == [], "a tick named by its own label"
    assert B.check_axis_tags(w, [dict(TAG, x=2000.25, label="Q2 2000")]) == [], "a datum between ticks, labelled"


@pytest.mark.parametrize("patch, needle", [
    ({"x": 1960}, "outside the page's domain [1970, 2026.25]"),
    ({"x": 2031}, "outside the page's domain [1970, 2026.25]"),
    ({"x": 2000.1}, "is neither one of the page's x ticks nor a datum"),
    ({"x": "the dot-com peak"}, "is not one of the page's x tick labels"),
    ({"label": "1999"}, "the pill would print 1999 at x=2000"),
    ({"label": "the 2010s"}, "the pill would print 2010s at x=2000"),
    ({"series": 1}, "series 1 is past the page's last series (0)"),
])
def test_a_tag_the_page_does_not_carry_is_refused_by_name(patch, needle):
    with pytest.raises(ValueError, match=None) as exc:
        B.check_axis_tags(_world(), [dict(TAG, **patch)])
    assert needle in str(exc.value), str(exc.value)


def test_an_era_label_and_a_datum_between_ticks_are_true():
    w = _world()
    assert B.check_axis_tags(w, [dict(TAG, x=1998, label="the late 1990s")]) == []
    warns = B.check_axis_tags(w, [dict(TAG, x=2000.25)])
    assert len(warns) == 1 and "no tick stands at x=2000.25" in warns[0] and "E99 s106" in warns[0], warns


def test_it_binds_to_the_state_on_screen_at_its_word():
    """Row 9's own world: the railway page (1844..1850) recasts to the GDP page on 'the internet'. A tag on 2000
    before the recast names a year the railway page does not carry; after it, the GDP page's own tick."""
    w = _world("ledger:ev-railway-index-v1:line:139:right;then=ev-equip-ipp-gdp-v2:line")
    recast = {"kind": "chart_to", "at": 9.5, "dur": 0.5, "to": "recast", "state": 1}
    assert B.check_axis_tags(w, [recast, dict(TAG)]) == []
    under = dict(recast, dur=1.2)   # H row 9's own: a tag on the word the page is still recasting
    warns = B.check_axis_tags(w, [under, dict(TAG)])
    assert len(warns) == 1 and "its page is still arriving (the chart_to recast at 9.5s runs to 10.7s)" in warns[0], warns
    with pytest.raises(ValueError, match=r"outside the page's domain"):
        B.check_axis_tags(w, [recast, dict(TAG, at=9.0)])


def test_a_bars_tag_names_a_bar_and_a_label_no_bar_carries_is_refused():
    """Review finding 15 (s106, s109 (5)): a tag on a bars page is NOT refused by type - it binds to the bar the
    sentence names; the truth rule refuses a label no bar carries."""
    page = {"builder": "story", "labels": ["Railways", "Telecom", "AI"], "values": [50, 28, 40]}
    w = {"kind": "ledger", "page": page}
    assert B.check_axis_tags(w, [dict(TAG, x=2)]) == []
    assert B.check_axis_tags(w, [dict(TAG, x="Telecom")]) == []
    assert B.check_axis_tags(w, [dict(TAG, x=0, label="Railways")]) == []
    for patch, needle in [({"x": 3}, "bar 3 is past the page's last bar (2)"),
                          ({"x": "Cloud"}, "'Cloud' is not one of the page's bars"),
                          ({"x": 1, "label": "Cloud"}, "label 'Cloud' is not bar 1's category 'Telecom'"),
                          ({"x": 1.5}, "a bars page's x is a bar's index or its category")]:
        with pytest.raises(ValueError) as exc:
            B.check_axis_tags(w, [dict(TAG, **patch)])
        assert needle in str(exc.value), (patch, str(exc.value))
    warns = B.check_axis_tags(w, [dict(TAG, x=1, guide=True)])
    assert len(warns) == 1 and "a bars page draws no guide" in warns[0], warns


def test_a_page_without_an_x_axis_refuses_it_by_name():
    w = {"kind": "ledger", "page": {"builder": "share", "labels": ["a", "b"], "values": [1, 2]}}
    with pytest.raises(ValueError, match=r"a share page has no x axis a tag can name"):
        B.check_axis_tags(w, [dict(TAG)])


def test_a_fourth_tag_standing_in_one_hold_warns_with_its_numbers():
    w = _world()
    tags = [dict(TAG, at=10.0 + k, x=x) for k, x in enumerate((1970, 1990, 2000, 2020))]
    assert B.check_axis_tags(w, tags[:3]) == [], "three standing: the don't's own ceiling"
    warns = B.check_axis_tags(w, tags)
    assert len(warns) == 1, warns
    for needle in ("4 tags stand at once at 13s", "1970, 1990, 2000, 2020", "more than 3", "E99 s106"):
        assert needle in warns[0], (needle, warns[0])
    left = [dict(t) for t in tags]
    left[0]["leave_at"], left[0]["leave_s"] = 11.5, 1.0   # the first one's page was replaced: it is gone by 13
    assert B.check_axis_tags(w, left) == []


def test_it_leaves_with_its_page_r26_219():
    recast = {"kind": "chart_to", "at": 12.0, "dur": 1.0, "to": "recast", "state": 1}
    tag = dict(TAG)
    stamped, _clamped, dropped = B.stamp_page_leave([tag, recast])
    assert stamped == [tag] and not dropped and tag["leave_at"] == 12.0 and tag["leave_s"] == 1.0


def test_a_panel_tag_names_its_panel():
    import ledger_page as L
    v3 = PROJECT / "evidence/objects/ev-tnx-two-eras-v3.series.json"
    w = {"kind": "ledger", "page": B.stamp_full_stage(L.build_spec(L.load_series(v3), "line", None, "right"))}
    assert B.check_axis_tags(w, [dict(TAG, x=2024, panel=1)]) == []
    with pytest.raises(ValueError, match=r"outside the page's domain \[1998"):
        B.check_axis_tags(w, [dict(TAG, x=2024, panel=0)])
    with pytest.raises(ValueError, match=r"name the `panel` whose axis it stands on"):
        B.check_axis_tags(w, [dict(TAG, x=2024)])


# ---- the registries ----------------------------------------------------------------------------------------


def test_the_registries_carry_it():
    import authoring.shapes as SH
    import gate_motion_density as G
    import lint_species_choice as LSC
    import recipe_walk as RW
    assert "axis_tag" in SH.PLOT_MARKS and "axis_tag" in SH.HELD_MARKS, "a card never parks over the pill or its guide"
    assert G.SPECIES_EVENTS["axis_tag"] == ("at",), "the pop is one arrival; the pill that stands is 0 events (s91)"
    assert "axis_tag" in LSC.ACT_SPECIES["COMPARES"]
    assert "axis_tag" in RW.PAGE_SPECIES_KINDS
    assert B.AXIS_TAG_MAX == 3


# ---- the engine's wiring -----------------------------------------------------------------------------------


def test_the_engine_carries_the_module_and_paints_it_from_the_perform_layer():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN axis_tag */" in src
    for dep in ("ease", "spring", "span", "lit_stretch", "breakthrough"):
        assert src.index(f"/* KINETICS:BEGIN {dep} */") < src.index("/* KINETICS:BEGIN axis_tag */"), dep
    assert src.index("/* KINETICS:BEGIN axis_tag */") < src.index("const paintPerform =")
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert 'pageSpecies(scene, "axis_tag")' in build, "the builder makes the pill's DOM"
    perform = src[src.index("const paintPerform ="):]
    perform = perform[:perform.index("\n  };\n")]
    assert "PAGE_PAINTERS.axis_tag" in perform, "... and the perform layer paints it through the page registry"
    kinds = src[src.index("const LP_PANEL_KINDS"):]
    assert '"axis_tag"' in kinds[:kinds.index("\n")], "a panel may carry it"


def test_the_card_is_on_page_species_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["page_species:axis_tag"]
    assert card["token"] == "axis_tag" and card["when"] is None and card["serves"] == ["COMPARES"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/axis_tag.mjs",
                             "symbol": "paintAxisTags"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/axis_tag.mjs", "object": "AXTAG"}
    assert len(card["does"]) <= 240 and card["proof"]["golden"] == "axis-tag-two-thousand"
    assert "BRAVOS-USE-WHEN.md:323" in json.dumps(card)


# ---- the golden's beat, read on the served player ------------------------------------------------------------


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
  const st = world.__lp, AT = (st.perform || {}).axisTags;
  if (!AT) return null;
  const td = AT.tags[0], S = (st.states && st.states[st.active | 0]) || st;
  const marks = (st.states || [st]).flatMap(Q => Q.marks || []);   /* the 2000 tick is the state's that carries it */
  const tick = marks.find(m => m.role === 'xtick' && Math.abs(m.geom.v - 2000) < 1e-9);
  const others = marks.filter(m => m.role === 'xtick' && m !== tick).map(m => m.el.style.visibility || '');
  const r = td.rect.getBoundingClientRect(), tb = tick.el.getBoundingClientRect();
  const d = td.guide.getAttribute('d') || '';
  const nums = d ? d.replace(/[ML]/g, ' ').trim().split(/\\s+/).map(Number) : [];
  const ser = (S.markBy || {}).s0, j = 120 - ((S.windowOffsets || [])[0] | 0) - ((ser && ser.geom.k0) | 0);
  return { g: parseFloat(td.g.getAttribute('opacity') || '0'), text: parseFloat(td.text.getAttribute('opacity') || '0'),
           label: td.text.textContent, tickHidden: tick.el.style.visibility === 'hidden', tickX: tick.geom.x,
           others, transform: td.g.getAttribute('transform') || '', guide: parseFloat(td.guide.getAttribute('opacity') || '0'),
           guideXs: nums.filter((_, k) => k % 2 === 0), guideYs: nums.filter((_, k) => k % 2 === 1),
           datum: ser && ser.geom.pts ? ser.geom.pts[j] : null,
           pillCoversTick: r.left <= tb.left && r.right >= tb.right && r.top <= tb.top && r.bottom >= tb.bottom };
}"""


def _serve(surface):
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    tl, uris, _t, aspect = RB.load_surface(surface) if isinstance(surface, str) else surface
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
def test_the_named_year_becomes_the_pill_and_the_guide_drops_to_it_from_the_datum():
    """The golden's beat at four instants: nothing before the word; mid-pop, the tick still shows and the text waits;
    landed, the tick has BECOME the pill (hidden under it, the pill's text is its string) and the dotted guide runs
    from the 2000 datum down to the pill; the neighbours keep their labels."""
    import build_golden_sources as G
    at, errs, close = _serve("axis-tag-two-thousand")
    try:
        a0 = G.AXTAG_AT
        before, early, landed, held = at(a0 - 0.2), at(a0 + 0.03), at(a0 + 0.4), at(a0 + 0.93)
    finally:
        close()
    assert not errs, errs
    assert before["g"] == 0 and not before["tickHidden"], before
    assert early["g"] == 1 and early["text"] == 0 and not early["tickHidden"], early
    for f in (landed, held):
        assert f["g"] == 1 and f["text"] == 1 and f["label"] == "2000", f
        assert f["tickHidden"] and f["pillCoversTick"], f
        assert all(v == "" for v in f["others"]), f["others"]
        assert f["transform"].startswith("translate(%.1f " % f["tickX"]), (f["transform"], f["tickX"])
        assert f["guide"] == 1 and set(f["guideXs"]) == {round(f["datum"][0], 1)}, f
        assert abs(min(f["guideYs"]) - (f["datum"][1] + 6)) < 0.11, (f["guideYs"], f["datum"])


# ---- a tag on a page that arrives by a RECAST (H row 9's own shape): the pop waits, and a play is a seek --------------

RECAST_PLATE = "ledger:ev-railway-index-v1:line:139:right;idle=live;then=ev-equip-ipp-gdp-v2:line"
RECAST_AT, RECAST_DUR = 8.0, 1.2


def _recast_surface():
    import build_golden_sources as G
    species = [{"kind": "chart_to", "at": RECAST_AT, "dur": RECAST_DUR, "to": "recast", "state": 1},
               dict(TAG, at=RECAST_AT + 0.01)]
    assert _errs(species, RECAST_PLATE) == []
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate(RECAST_PLATE, (0, 0, 0), PROJECT)
        B.stamp_full_stage(world["page"])
        warns = B.check_axis_tags(world, species)
    finally:
        B.ASPECT = saved
    assert len(warns) == 1 and "still arriving" in warns[0], warns
    scenes = [{"scene_id": "s01", "world": dict(world, ken_burns={"scale": 0, "x": 0, "y": 0}), "exit": "cut",
               "span": [0.0, G.RUNTIME], "docks": [], "species": species}]
    return G._timeline("axis_tag on a recast page", scenes, {}, "16:9"), G._base_uris(), None, "16:9"


@needs_browser
def test_on_a_recast_page_the_pop_waits_for_the_page_and_a_play_lands_what_a_cold_seek_does():
    """The first test bed's frame read (H row 9): a tag on the recast's word popped UNDER the hand-over and appeared whole
    at the switch - and a play through the recast measured the arriving page's ticks while the hand had not yet written
    them (empty strings), so it placed nothing at all. The pop now waits for the state to stand (axtagStart), and every
    label is measured on its whole string, so the path to an instant cannot change what it paints."""
    surf = _recast_surface()
    at, errs, close = _serve(surf)
    try:
        played = [at(t) for t in (RECAST_AT - 1.0, RECAST_AT + 0.5, RECAST_AT + RECAST_DUR + 0.05, RECAST_AT + RECAST_DUR + 0.6)]
    finally:
        close()
    at2, errs2, close2 = _serve(surf)
    try:
        cold = at2(RECAST_AT + RECAST_DUR + 0.6)
    finally:
        close2()
    assert not errs and not errs2, (errs, errs2)
    under, arriving, landed = played[1], played[2], played[3]
    assert under["g"] == 0, "nothing pops under the hand-over"
    assert arriving["g"] == 1 and "scale(1.0000)" not in arriving["transform"], arriving["transform"]
    assert landed["tickHidden"] and landed["text"] == 1 and landed["transform"].endswith("scale(1.0000)"), landed
    for k in ("transform", "tickHidden", "guideXs", "guideYs", "text", "label"):
        assert landed[k] == cold[k], (k, landed[k], cold[k])
