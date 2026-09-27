"""P72 T53 (h) / R26-414 (a) - THE LEADER: a curved pointer from a figure, a datum or a point to a datum or a bar's
printed value, the multiple on the arc.

The Bravos harvest v2's R35 ("Flow -> the total -> a pointer back", STK 0:02-0:10): "$12,000,000,000" arcs to the ringed
peak, then the peak arcs back to the small bar it dwarfs with "10x" on the arc. P71 T35 found no card drew a leader - the
clothoid ran only between a species' own laid-out nodes - and stopped R35 (`the-total-points-back`). The token is a PAGE
species: `{"kind": "leader", at, dur, from: {kind: figure, text} | {kind: datum, index, series?} | {kind: point, x, y},
to: {kind: datum, index, series?, part?: "value"}, label?, multiple?, ring?, head?, bend?, color?, keep?}`. The law and
the painter are species/leader.mjs (pinned by tests/kinetics/leader.test.mjs); this file pins the compiler's grammar, the
page's TRUTH rules (a target the page does not draw, a source figure the row does not write by the word, a multiple the
page's arithmetic does not give, a claim's figure unmarked - refused by name), the placement WARN (s106: an authored
`bend` through the page's words is reported, never refused), the registries, the engine's wiring, the card, and the leader
read on the SERVED player at 16:9, at 9:16 and on a long-form page (the golden `leader-points-back`: H row 16's three
bars, the $150B total pointing back at the $28B year, "5.4x" on the arc).
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

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/leader.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
LINE_PLATE = "ledger:ev-capital-formation-v1:line:225:right"
LINE_EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
BARS_PLATE = "ledger:lab-issuance-three-bars:bars"
FIG = {"kind": "figure", "at": 8.5, "dur": 1.4, "target": {"kind": "datum", "index": 2}, "text": "$150B", "sub": "the total"}
LEAD = {"kind": "leader", "at": 11.0, "dur": 1.6, "from": {"kind": "figure", "text": "$150B"},
        "to": {"kind": "datum", "index": 0, "part": "value"}, "ring": True, "multiple": True}


def _errs(entries, plate=BARS_PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _bars_world(obj: dict | None = None, species: list | None = None) -> dict:
    """The golden's three bars (H row 16, every value read off ev-debt-issuance-line-v1) as the compiler builds them."""
    import build_golden_sources as G
    with tempfile.TemporaryDirectory() as td:
        ep = Path(td)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / f"evidence/objects/{G.LEADER_OID}.series.json").write_text(json.dumps(obj or G.leader_three_bars()), encoding="utf-8")
        saved = B.ASPECT
        B.ASPECT = "16:9"
        try:
            return B.world_for_plate(f"ledger:{G.LEADER_OID}:bars", (0, 0, 0), ep)
        finally:
            B.ASPECT = saved


def _check(entries, world=None):
    sps = [dict(e) for e in entries]
    return B.check_leader(world or _bars_world(), sps), sps


# ---- the grammar -------------------------------------------------------------------------------------------------------


def test_the_token_is_a_page_species_the_compiler_accepts():
    assert "leader" in B.SPECIES_KINDS and "leader" in B.PAGE_SPECIES
    assert "leader" in B.PAGE_BOUND_SPECIES, "it joins two things on its page, so it leaves with the page (R26-219)"
    assert "leader" not in B.PANEL_SPECIES, "its ends are one chart's data: a panels page is refused on the page"
    assert _errs([FIG, LEAD]) == []
    assert _errs([dict(LEAD, head="dot", bend=-0.4, color="neg", keep=True, label="5.4x")]) == []
    assert _errs([dict(LEAD, **{"from": {"kind": "datum", "index": 2}}, to={"kind": "datum", "index": 0})]) == []
    assert _errs([dict(LEAD, **{"from": {"kind": "point", "x": 0.8, "y": 0.1}}, multiple=True)]) == [], \
        "a point source is grammar; its multiple is the page's refusal (no datum to divide)"


def test_it_performs_on_a_ledger_page_only():
    errs = _errs([LEAD], plate="plate-plain")
    assert any("leader is a page species" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"from": None}, "'from' must be {kind: figure|datum|point"),
    ({"from": {"kind": "dock", "dock": "card-1"}}, "a card joins its datum by the dock option `park_at`"),
    ({"from": {"kind": "region"}}, "'from' kind 'region' must be one of figure|datum|point"),
    ({"from": {"kind": "figure", "text": ""}}, "names the figure by its written `text`"),
    ({"from": {"kind": "figure", "text": "$150B", "index": 2}}, "'from' figure takes only kind|text"),
    ({"from": {"kind": "datum", "index": -1}}, "'from' datum index must be a non-negative integer"),
    ({"from": {"kind": "datum", "index": 2, "part": "top"}}, "'from' part must be one of value"),
    ({"from": {"kind": "point", "x": 1.4, "y": 0.2}}, "'from' point x must be a share of the chart's box"),
    ({"to": None}, "'to' must be {kind: datum"),
    ({"to": {"kind": "point", "x": 0.2, "y": 0.2}}, "a leader points at a DATUM the page draws"),
    ({"to": {"kind": "datum", "index": 0, "part": "top"}}, "'to' part must be one of value"),
    ({"to": {"kind": "datum", "index": "zero"}}, "'to' datum index must be a non-negative integer"),
    ({"from": {"kind": "datum", "index": 0}, "to": {"kind": "datum", "index": 0}}, "a leader joins two things"),
    ({"label": ""}, "label must be a non-empty string"),
    ({"multiple": False}, "multiple must be true"),
    ({"ring": "yes"}, "ring must be true or false"),
    ({"head": "star"}, "head must be one of arrow|dot"),
    ({"bend": 3}, "bend must be a number from -1 to 1"),
    ({"bend": True}, "bend must be a number from -1 to 1"),
    ({"color": "gold"}, "color must be one of"),
    ({"side": "left"}, "a leader takes only"),
])
def test_a_malformed_leader_is_refused_by_name(patch, needle):
    errs = _errs([FIG, dict(LEAD, **patch)])
    assert any(needle in e for e in errs), (patch, errs)


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["leader"]
    assert 30 <= len(when) <= 300 and "\n" not in when, len(when)
    for word in ("POINTS", "back", "multiple", "never"):
        assert word in when, word


# ---- the truth rules (hard: E28 / s109 / E77) and the placement finding (a WARN: s106) ---------------------------------


def test_the_multiple_is_the_pages_own_ratio_written_by_the_compiler():
    notes, sps = _check([FIG, LEAD])
    assert notes == []
    assert sps[1]["label"] == "5.4x", "150 / 28 = 5.36 -> '5.4x', written on the species: the timeline carries what the player writes"
    assert B.leader_multiple(28, 150) == B.leader_multiple(150, 28) == "5.4x"
    assert B.leader_multiple(1.2, 12.5) == "10x", "ten and over is written whole (Bravos STK 0:08's '10x')"
    _n, ok = _check([FIG, dict(LEAD, label="5.4x")])
    assert ok[1]["label"] == "5.4x", "a typed multiple the page gives stands"
    with pytest.raises(ValueError, match=r"writes 6x but the two data it joins are 5\.357x"):
        _check([FIG, dict(LEAD, label="6x")])
    with pytest.raises(ValueError, match=r"writes 7x but"):
        _check([FIG, dict(LEAD, multiple=True, label="7x")])


def test_a_difference_on_the_arc_is_the_pages_arithmetic_too():
    _check([FIG, {k: v for k, v in LEAD.items() if k != "multiple"} | {"label": "+$122B"}])
    with pytest.raises(ValueError, match="write 122"):
        _check([FIG, {k: v for k, v in LEAD.items() if k != "multiple"} | {"label": "+$100B"}])


@pytest.mark.parametrize("patch, needle", [
    ({"to": {"kind": "datum", "index": 5, "part": "value"}}, "'to' 5 is past the chart's last bar (2)"),
    ({"to": {"kind": "datum", "index": 0, "series": 1}}, "names series 1 on a bars chart"),
    ({"from": {"kind": "figure", "text": "$151B"}}, "from figure '$151B' - no figure on this row writes it (the row's figures: '$150B')"),
    ({"from": {"kind": "datum", "index": 7}}, "'from' 7 is past the chart's last bar (2)"),
    ({"from": {"kind": "point", "x": 0.8, "y": 0.1}}, "multiple - a leader from a point has no datum to divide"),
])
def test_a_thing_the_page_does_not_have_is_refused_by_name(patch, needle):
    with pytest.raises(ValueError) as e:
        _check([FIG, dict(LEAD, **patch)])
    assert needle in str(e.value), str(e.value)


def test_a_source_figure_written_after_the_word_is_refused():
    with pytest.raises(ValueError, match=r"is written at 12\.0, after the leader's word at 11\.0 - it would point from nothing"):
        _check([dict(FIG, at=12.0), LEAD])


def test_a_number_on_an_arc_from_a_point_is_refused_a_word_is_not():
    point = {k: v for k, v in LEAD.items() if k != "multiple"} | {"from": {"kind": "point", "x": 0.8, "y": 0.12}}
    with pytest.raises(ValueError, match="writes a figure on an arc from a point"):
        _check([dict(point, label="5x")])
    notes, sps = _check([dict(point, label="the total")])
    assert notes == [] and sps[0]["label"] == "the total"


def test_a_line_page_has_no_printed_value_to_point_at():
    world = B.world_for_plate(LINE_PLATE, (0, 0, 0), LINE_EP)
    lead = {"kind": "leader", "at": 5.0, "dur": 1.5, "from": {"kind": "datum", "index": 225}, "to": {"kind": "datum", "index": 124}}
    notes, sps = _check([dict(lead, multiple=True)], world)
    assert sps[0]["label"] == "1.2x", "28.18 / 23.03 on the yardstick line - the page's own data"
    with pytest.raises(ValueError, match="to part 'value' names a bar's printed number"):
        _check([dict(lead, to={"kind": "datum", "index": 124, "part": "value"})], world)
    with pytest.raises(ValueError, match="from part 'value' names a bar's printed number"):
        _check([dict(lead, **{"from": {"kind": "datum", "index": 225, "part": "value"}})], world)


def test_a_multiple_off_a_claim_says_whose_or_is_refused():
    import build_golden_sources as G
    world = _bars_world(G.claim_price_object())
    lead = {"kind": "leader", "at": 5.0, "dur": 1.5, "from": {"kind": "datum", "index": 0}, "to": {"kind": "datum", "index": 5}}
    with pytest.raises(ValueError, match=r"an end stands on a claim .* \(P73 T1\)"):
        _check([dict(lead, multiple=True)], world)
    _check([dict(lead, label="36x on Patel's figure")], world)
    notes, sps = _check([dict(lead, to={"kind": "datum", "index": 3, "part": "value"}, multiple=True)], world)
    assert sps[0]["label"] == "14x", "36 / 2.5 = 14.4 - two sourced bars, no claim"


def test_an_authored_bend_through_the_pages_words_is_a_warn_with_its_numbers_never_a_refusal():
    notes, _sps = _check([FIG, dict(LEAD, bend=0.35)])   # a low lift: the arc runs through 2025's printed $121B
    assert len(notes) == 1 and notes[0].startswith("WARN leader at 11.0: bend 0.35 is the author's and it stands"), notes
    assert "bar 1's value '$121B'" in notes[0] and "px" in notes[0] and "REPORTED" in notes[0], notes
    assert _check([FIG, dict(LEAD, bend=1.0)])[0] == [], "a high lift clears the $121B"
    assert _check([FIG, dict(LEAD, bend=-0.35)])[0] == [], "... and so does a sag under it"
    assert _check([FIG, LEAD])[0] == [], "no bend: the engine chooses its side clear of the words (nothing estimated)"


def test_the_page_checks_run_it_from_derive_rescale_states(capsys):
    import build_golden_sources as G
    tl, _uris = G.leader_points_back(species=[FIG, dict(LEAD, bend=0.35)])
    lead = [s for s in tl["scenes"][0]["species"] if s["kind"] == "leader"][0]
    assert lead["label"] == "5.4x"
    assert "[WARN] leader at 11.0: bend 0.35" in capsys.readouterr().out


def test_it_leaves_with_its_page_when_a_verb_replaces_it():
    sps = [dict(FIG), dict(LEAD), {"kind": "chart_to", "at": 16.0, "dur": 1.0, "to": "recast", "state": 1}]
    stamped, _clamped, _dropped = B.stamp_page_leave(sps)
    assert any(s["kind"] == "leader" for s in stamped), stamped
    assert sps[1]["leave_at"] == 16.0 and sps[1]["leave_s"] == B.PAGE_LEAVE_S
    assert _errs(sps[:2]) == [], "the leave's own record is grammar"


# ---- the registries, the engine's wiring and the card -----------------------------------------------------------------


def test_the_registries_know_the_leader():
    import gate_motion_density as G
    import lint_species_choice as L
    import recipe_walk as RW
    from authoring import shapes as SH
    assert G.SPECIES_EVENTS["leader"] == ("at", "end"), "the arc TRAVELS (s99): it leaves on its word and lands at its end"
    assert "leader" in G.PLOT_INK_MARKS and "leader" in G.PLOT_HELD_MARKS
    assert "leader" in SH.PLOT_MARKS and "leader" in SH.HELD_MARKS
    assert "leader" in L.ACT_SPECIES["TURNS"]
    assert "leader" in RW.PAGE_SPECIES_KINDS
    assert [f for f, _ in L.PROPOSE_FILL["leader"]] == ["from", "to"]


def test_the_engine_carries_the_module_and_paints_it_from_the_perform_layer():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN leader */" in src
    order = [src.index(f"/* KINETICS:BEGIN {m} */") for m in ("clothoid", "level_join", "axis_tag", "leader")]
    assert order == sorted(order) and order[-1] < src.index("const paintPerform ="), "after every law it reads, before the perform layer"
    build = src[src.index("const lpBuildLeaders ="):src.index("const paintPerform =")]
    assert build.index("const lpBuildLeaders =") < build.index("const buildPerform =") < build.index("lpBuildLeaders(st, scene, surf, figures, P, G)")
    assert 'pageSpecies(scene, "leader")' in build, "the builder makes the leader's DOM"
    assert "ringDashes(" in build and "figBox(" in build and "axtagPillBox(" in build, "... from the ring's, the figure's and the pill's own laws"
    perform = src[src.index("const paintPerform ="):]
    perform = perform[:perform.index("\n  };\n")]
    assert "PAGE_PAINTERS.leader" in perform, "... and the perform layer paints it through the page registry"
    assert perform.index("PAGE_PAINTERS.leader") > perform.index("PAGE_PAINTERS.figure("), "after the figures: it leaves where they stand"


def test_the_card_is_on_page_species_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["page_species:leader"]
    assert card["token"] == "leader" and card["when"] is None and card["serves"] == ["TURNS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/leader.mjs", "symbol": "paintLeader"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/leader.mjs", "object": "LEADER"}
    assert len(card["does"]) <= 240 and card["proof"]["golden"] == "leader-points-back"
    assert "P72 T53 (h)" in card["doctrine"] and "E56" in " ".join(card["doctrine"])


# ---- the leader read on the served player -----------------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        with SP.browser() as _b:
            return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, PF = st.perform || {}, L = (PF.leaders || [])[0];
  if (!L) return null;
  const S = (st.states && st.states[st.active | 0]) || st;
  const sh = L.shaft, n = sh.getTotalLength ? sh.getTotalLength() : 0, pts = [];
  for (let i = 0; i <= 40; i++) { const q = sh.getPointAtLength(n * i / 40); pts.push([q.x, q.y]); }
  const val = S.bars[0].val, vb = val.getBBox(), fg = (PF.figures || [])[0], fb = fg ? fg.g.getBBox() : null;
  const pill = L.pill ? L.pill.g.getBBox() : null, pm = L.pill ? L.pill.g.getCTM() : null, cm = st.chart.getCTM();
  const pillBox = pill && pm && cm ? (() => { const inv = cm.inverse().multiply(pm);
    const a = new DOMPoint(pill.x, pill.y).matrixTransform(inv), b = new DOMPoint(pill.x + pill.width, pill.y + pill.height).matrixTransform(inv);
    return [a.x, a.y, b.x, b.y]; })() : null;
  const words = (st.labBoxes || []).map(b => [b[0], b[1], b[0] + b[2], b[1] + b[3]]);
  return { g: parseFloat(L.g.getAttribute('opacity') || '0'), off: parseFloat(sh.getAttribute('stroke-dashoffset') || '1'),
           len: n, pts, head: parseFloat(L.head.el.getAttribute('opacity') || '0'),
           val: [vb.x, vb.y, vb.x + vb.width, vb.y + vb.height], fig: fb ? [fb.x, fb.y, fb.x + fb.width, fb.y + fb.height] : null,
           ringOn: L.ring ? L.ring.dashes.filter(d => d.p.getAttribute('opacity') === '1').length : 0,
           pillOn: L.pill ? L.pill.g.getAttribute('opacity') : null, pillBox, pillText: L.pill ? L.pill.text.textContent : null,
           words, W: +st.chart.viewBox.baseVal.width, H: +st.chart.viewBox.baseVal.height, errs: window.__errs || [] };
}"""


def _serve(tl: dict, uris: dict):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(PROBE)

    return at, errs, close


def _inside(p, b, pad=0.0) -> bool:
    return b[0] - pad <= p[0] <= b[2] + pad and b[1] - pad <= p[1] <= b[3] + pad


def _meet(a, b) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _same(a, b, eps=0.6) -> bool:
    return all(abs(x - y) <= eps for x, y in zip(a, b))


def _clear_of_words(f: dict) -> tuple[list, list]:
    """(the words the drawn arc runs through, the words the pill stands on) - the target's own value and the source
    figure are the arc's own ends, not words in its way."""
    own = [w for w in f["words"] if _same(w, f["val"], 2.0) or (f["fig"] and _meet(w, f["fig"]))]
    others = [w for w in f["words"] if w not in own]
    through = [w for w in others if any(_inside(p, w) for p in f["pts"][2:-2])]
    under = [w for w in others if f["pillBox"] and _meet(f["pillBox"], w)]
    return through, under


def _read(tl, uris, times):
    at, errs, close = _serve(tl, uris)
    try:
        frames = [at(t) for t in times]
    finally:
        close()
    return frames, errs


@needs_browser
def test_it_draws_by_length_on_its_word_lands_at_the_value_and_rings_it():
    import build_golden_sources as G
    tl, uris = G.leader_points_back()
    a0, dur = G.LEADER_AT, G.LEADER_DUR
    (before, early, landed, after), errs = _read(tl, uris, [a0 - 0.2, a0 + 0.3 * dur, a0 + dur, a0 + dur + 4.0])
    assert not errs, errs
    assert before["g"] == 0, before
    assert early["g"] == 1 and 0 < early["off"] < 1, ("part-way along its own length", early["off"])
    assert early["head"] == 0 and early["pillOn"] == "0", "the head and the multiple wait for the arc"
    assert landed["off"] == 0 and landed["head"] == 1 and landed["ringOn"] > 0, landed
    tip, tail, val = landed["pts"][-1], landed["pts"][0], landed["val"]
    cx, cy = (val[0] + val[2]) / 2, (val[1] + val[3]) / 2
    assert tip[0] > val[2] or tip[1] < val[1], ("the tip stops OUTSIDE the $28B it points at", tip, val)
    assert abs(tip[0] - cx) < 140 and abs(tip[1] - cy) < 90, ("... at its ring", tip, val)
    assert landed["fig"] and _inside(tail, landed["fig"], 30), ("the tail leaves the $150B figure's own box", tail, landed["fig"])
    assert after["g"] == 1 and after["pts"] == landed["pts"], "it HOLDS - an annotation now"


@needs_browser
def test_the_multiple_sits_on_the_arc_and_the_arc_clears_the_pages_words():
    import build_golden_sources as G
    tl, uris = G.leader_points_back()
    (landed,), errs = _read(tl, uris, [G.LEADER_AT + G.LEADER_DUR + 0.4])
    assert not errs, errs
    assert landed["pillOn"] == "1" and landed["pillText"] == "5.4x", landed["pillText"]
    pb = landed["pillBox"]
    mid = ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2)
    assert min(abs(p[0] - mid[0]) + abs(p[1] - mid[1]) for p in landed["pts"]) < 6, ("the pill is ON the arc", mid)
    through, under = _clear_of_words(landed)
    assert through == [] and under == [], ("the arc and its multiple clear the page's words (R26-414 (g): the bracket's "
                                           "5.4x collided with the total)", through, under)


@needs_browser
def test_it_leaves_with_its_page():
    import build_golden_sources as G
    lead = dict(G.LEADER_SPECIES[1], leave_at=16.0, leave_s=1.0)   # stamp_page_leave's record, as a replacing verb writes it
    tl, uris = G.leader_points_back(species=[G.LEADER_SPECIES[0], lead])
    (standing, going, gone), errs = _read(tl, uris, [15.9, 16.5, 17.2])
    assert not errs, errs
    assert standing["g"] == 1 and 0 < going["g"] < 1 and gone["g"] == 0, (standing["g"], going["g"], gone["g"])


@needs_browser
def test_at_nine_sixteen_it_lands_and_clears_the_words():
    import build_golden_sources as G
    tl, uris = G.leader_points_back(aspect="9:16")
    (landed,), errs = _read(tl, uris, [G.LEADER_AT + G.LEADER_DUR + 0.4])
    assert not errs, errs
    assert landed["g"] == 1 and landed["off"] == 0 and landed["pillText"] == "5.4x", landed
    through, under = _clear_of_words(landed)
    assert through == [] and under == [], (through, under)
    assert all(0 <= p[0] <= landed["W"] and 0 <= p[1] <= landed["H"] for p in landed["pts"]), "inside the chart's box"


@needs_browser
def test_on_a_long_form_page_it_points_from_one_printed_value_to_another():
    import build_golden_sources as G
    lead = {"kind": "leader", "at": 11.0, "dur": 1.6, "from": {"kind": "datum", "index": 0, "part": "value"},
            "to": {"kind": "datum", "index": 3, "part": "value"}, "ring": True, "multiple": True, "head": "dot"}
    tl, uris = G.leader_points_back(species=[lead], obj=G.claim_price_object(), opts=";readability=longform")
    assert tl["scenes"][0]["species"][0]["label"] == "14x"
    (landed,), errs = _read(tl, uris, [13.2])
    assert not errs, errs
    assert landed["g"] == 1 and landed["pillText"] == "14x" and landed["head"] == 1, landed
    through, under = _clear_of_words(landed)
    assert through == [] and under == [], (through, under)
