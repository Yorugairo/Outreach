"""P71 T10 (was P69 T39) - THE LEVEL JOIN: a dashed rule from one datum to another, a ring at each end, the gap
written off the rule.

The Bravos harvest v2's A9 (n=5, rank 4): "a dashed LEVEL rule drawn from one datum to another". The token is a PAGE
species: `{"kind": "level_join", at, dur, from, to: <datum> | {series, index} | {y}, label, series?, color?, side?,
dy?, panel?, keep?}` on a ledger row. The law and the painter are species/level_join.mjs (pinned by
tests/kinetics/level_join.test.mjs); this file pins the compiler's grammar, the page's TRUTH rules (the gap the label
writes is the page's own arithmetic - E28 / s109; a `to` in another unit is refused), the placement WARN (s106: an
authored place on the rule is reported with its numbers, never refused), the engine's wiring, the card, and the join
read on the SERVED player (the golden `level-join-half-a-point`: Steel and Paper H row 14's yardstick page, "Today it's
twenty-eight, the most it has ever been" against the dot-com 23).
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
import ledger_page as LPG  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
MODULE = ROOT / "content/video_engine/scripts/species/level_join.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/page_species.json"
OBJECTS = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects"
PLATE = "ledger:ev-capital-formation-v1:line:225:right"
JOIN = {"kind": "level_join", "at": 11.63, "dur": 1.71, "from": 124, "to": 225, "label": "+5 pts"}


def _errs(entries, plate=PLATE):
    return B.validate_species([dict(e) for e in entries], (0, 0, 0), plate)


def _yard_world() -> dict:
    """Row 14's page as the compiler builds it: the committed yardstick object (tech 23.03 at 2001 Q1, index 124; 28.18
    at 2026 Q2, index 225; the scale line 'ALL EQUIPMENT + IP' in the same %, series 1)."""
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        return B.world_for_plate(PLATE + ";idle=live", (0, 0, 0), ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper")
    finally:
        B.ASPECT = saved


def _check(entries, world=None):
    return B.check_level_join(world or _yard_world(), [dict(e) for e in entries])


# ---- the grammar -------------------------------------------------------------------------------------------


def test_the_token_is_a_page_species_the_compiler_accepts():
    assert "level_join" in B.SPECIES_KINDS and "level_join" in B.PAGE_SPECIES
    assert "level_join" in B.PAGE_BOUND_SPECIES, "it writes a figure on its page, so it leaves with the page (R26-219)"
    assert "level_join" in B.PANEL_SPECIES, "a panel may carry it: both anchors are read on that panel"
    assert _errs([JOIN]) == []
    assert _errs([dict(JOIN, series=0, color="neg", side="above", dy=-0.5, keep=True)]) == []
    assert _errs([dict(JOIN, to={"series": 1, "index": 225})]) == [], "a datum on another series of the page"
    assert _errs([dict(JOIN, **{"from": 225, "to": {"y": 28}}, label="28%")]) == [], "the axis form: to the value axis"


def test_it_performs_on_a_ledger_page_only():
    errs = _errs([JOIN], plate="plate-plain")
    assert any("level_join is a page species" in e for e in errs), errs


@pytest.mark.parametrize("patch, needle", [
    ({"from": None}, "'from' must be a datum index"),
    ({"from": -1}, "'from' must be a datum index"),
    ({"from": 0.5}, "'from' must be a datum index"),
    ({"to": "x"}, "'to' must be a datum index"),
    ({"to": -3}, "'to' must be a datum index"),
    ({"to": {"y": 5, "index": 3}}, "'to' names ONE far end"),
    ({"to": {"series": 1}}, "'to' names ONE far end"),
    ({"to": {"y": "high"}}, "'to': y must be a number"),
    ({"to": {"series": -1, "index": 3}}, "'to': series and index must be non-negative integers"),
    ({"to": 124}, "a join needs two ends"),
    ({"to": {"series": 0, "index": 124}}, "a join needs two ends"),
    ({"label": ""}, "label must be the figure the claim turns on"),
    ({"label": None}, "label must be the figure the claim turns on"),
    ({"color": "gold"}, "color must be one of"),
    ({"series": -2}, "series must be a non-negative integer"),
    ({"side": "on"}, "side must be one of right|left|above|below"),
    ({"dy": "down"}, "dy must be a number"),
    ({"dy": 9}, "dy must be a number"),
    ({"text": "+5"}, "a level join takes only"),
])
def test_a_malformed_join_is_refused_by_name(patch, needle):
    errs = _errs([dict(JOIN, **patch)])
    assert any(needle in e for e in errs), (patch, errs)


def test_the_when_says_what_sentence_calls_for_it_and_when_not():
    when = B.SPECIES_WHEN["level_join"]
    assert 30 <= len(when) <= 300 and "\n" not in when, len(when)
    for word in ("TWO numbers", "joins", "never", "on the rule"):
        assert word in when, word


# ---- the truth rules (hard: E28 / s109) and the placement finding (a WARN: s106) ------------------------------


def test_the_gap_the_label_writes_is_the_pages_own_arithmetic():
    """23.028 (2001 Q1) -> 28.184 (2026 Q2) is +5.156 points: '+5 pts', '5.2 points higher' and '1.2x' agree (at their
    own written precision); '+7 pts', a '-5' that says it FELL, and '1.5x' do not, and are refused with the numbers."""
    assert _check([JOIN]) == []
    assert _check([dict(JOIN, label="5.2 points higher")]) == []
    assert _check([dict(JOIN, label="+5.16")]) == []
    assert _check([dict(JOIN, label="1.2x the dot-com high")]) == []
    with pytest.raises(ValueError, match=r"level_join at 11.63: label '\+7 pts' writes 7 but the two data it joins differ by 5.156 \(23.028 -> 28.184\)"):
        _check([dict(JOIN, label="+7 pts")])
    with pytest.raises(ValueError, match=r"writes a FALL \('-'\) but the join rises"):
        _check([dict(JOIN, label="-5 pts")])
    with pytest.raises(ValueError, match=r"label '1.5x' writes 1.5x but the two data it joins are 1.224x"):
        _check([dict(JOIN, label="1.5x")])


def test_a_long_form_figure_its_frame_cannot_hold_is_a_warn_never_a_refusal():
    world = _yard_world()
    LPG.apply_longform(world["page"])
    assert B._lj_figure_px(world["page"]) == LPG.longform_type(world["page"])["tag"], "the end tags' size, the preset's"
    assert _check([JOIN], world) == []
    long = "+5 pts" + " - five points above the dot-com high" * 3
    notes = _check([dict(JOIN, label=long)], world)
    assert len(notes) == 1 and "cannot be kept inside the frame" in notes[0] and "E99 s106" in notes[0], notes


def test_a_label_with_no_number_is_reported_with_the_gap_never_refused():
    notes = _check([dict(JOIN, label="the most it has ever been")])
    assert len(notes) == 1 and "carries no number" in notes[0] and "+5.156" in notes[0] and "E99 s106" in notes[0], notes


def test_a_to_on_another_series_joins_in_the_same_unit_and_is_refused_in_another():
    assert _check([dict(JOIN, to={"series": 1, "index": 225}, label="+42.3")]) == []   # 23.028 -> 65.366, one %
    world = _yard_world()
    world["page"]["series"][1]["unit"] = "$bn"
    with pytest.raises(ValueError, match=r"level_join at 11.63: 'to' is on series 1 in '\$bn' and 'from' on series 0 in '%'"):
        _check([dict(JOIN, to={"series": 1, "index": 225}, label="+42.3")], world)


def test_the_axis_form_names_the_datums_own_level():
    assert _check([dict(JOIN, **{"from": 225, "to": {"y": 28}}, label="28%")]) == []
    with pytest.raises(ValueError, match=r"to: \{y: 30\} is not the level of datum 225 \(28.184\)"):
        _check([dict(JOIN, **{"from": 225, "to": {"y": 30}}, label="30%")])
    with pytest.raises(ValueError, match=r"label '27%' writes 27 but the level it joins is 28"):
        _check([dict(JOIN, **{"from": 225, "to": {"y": 28}}, label="27%")])


@pytest.mark.parametrize("patch, needle", [
    ({"from": 400}, r"'from' 400 is past series 0's last datum \(225\)"),
    ({"to": 999}, r"'to' 999 is past series 0's last datum \(225\)"),
    ({"series": 2}, r"series 2 is past the page's last series \(1\)"),
])
def test_an_end_the_page_does_not_have_is_refused(patch, needle):
    with pytest.raises(ValueError, match=needle):
        _check([dict(JOIN, **patch)])


def test_it_joins_on_a_line_or_a_bars_page_and_is_refused_by_name_elsewhere():
    bars = {"kind": "ledger", "page": LPG.build_spec(LPG.load_series(OBJECTS / "ev-rail-vs-yardstick-bars-v1.series.json"),
                                                        "bars", None, "right")}
    assert bars["page"]["builder"] == "story"
    assert _check([dict(JOIN, **{"from": 0, "to": 1}, label="-22")], bars) == []   # 50 -> 28, the railways' bar to today's
    with pytest.raises(ValueError, match="differ by -22"):
        _check([dict(JOIN, **{"from": 0, "to": 1}, label="-20")], bars)
    tree = {"kind": "ledger", "page": {"builder": "treemap", "labels": ["a"], "values": [1]}}
    with pytest.raises(ValueError, match=r"level_join at 11.63: a treemap page has no level to join"):
        _check([JOIN], tree)


def test_the_join_is_read_on_the_state_standing_at_its_word():
    """Row 14's own page recasts to the railway bars on "In the 1840s": a join after the recast joins the BARS."""
    world = _yard_world()
    world["page_states"] = [LPG.build_spec(LPG.load_series(OBJECTS / "ev-rail-vs-yardstick-bars-v1.series.json"), "bars", None, "right")]
    recast = {"kind": "chart_to", "at": 15.0, "dur": 1.2, "to": "recast", "state": 1}
    assert _check([recast, dict(JOIN, at=17.0, **{"from": 0, "to": 1}, label="-22")], world) == []
    assert _check([recast, JOIN], world) == [], "before the recast the line page stands"


def test_an_authored_place_on_the_rule_is_a_warn_with_its_numbers_never_a_refusal():
    """s106: the engine places the figure OFF the rule by construction; an author who moves it (side / dy) is honoured,
    and a place the estimate puts ON the rule is reported with the numbers - C14's mislabel, for the frame read."""
    assert _check([dict(JOIN, side="right")]) == []
    notes = _check([dict(JOIN, side="left", dy=1.0)])
    assert len(notes) == 1, notes
    n = notes[0]
    assert n.startswith("WARN level_join at 11.63") and "ON the rule" in n and "C14" in n and "E99 s106" in n, n
    assert "px" in n and "side=left" in n and "dy=1" in n, n


def test_the_placement_estimate_mirrors_the_engines_label_law():
    """The compiler's box and species/level_join.mjs levelLabelAt are one law: the same dials, the same four sides."""
    src = MODULE.read_text(encoding="utf-8")
    for key, val in (("PAD_PX", B.LEVEL_JOIN_PAD_PX), ("CLEAR_PX", B.LEVEL_JOIN_CLEAR_PX),
                     ("FRAME_AIR_PX", B.LEVEL_JOIN_FRAME_AIR_PX), ("ASC", B.LEVEL_JOIN_ASC),
                     ("DESC", B.LEVEL_JOIN_DESC), ("MID", B.LEVEL_JOIN_MID)):
        assert f"{key}: {val:g}," in src, (key, val)
    k = float(src.split("RING_K: ")[1].split(",")[0])
    assert B.LEVEL_JOIN_RING_PX == pytest.approx((54.0 * k, 40.0 * k)), "RING.MIN_RX / MIN_RY at LEVEL.RING_K"
    E, g = (500.0, 300.0), {"rx": 54.0, "ry": 40.0, "pad": 14.0, "w": 120.0, "fs": 59.08, "dy": 0.0}
    right = B.level_join_label_box("right", E, g)
    assert right == pytest.approx((568.0, 300 + 59.08 * 0.3 - 59.08 * 0.8, 688.0, 300 + 59.08 * 0.3 + 59.08 * 0.22))
    above = B.level_join_label_box("above", E, g)
    assert above[3] == pytest.approx(300 - 40 - 14) and above[0] == pytest.approx(440.0)


# ---- the engine's wiring -----------------------------------------------------------------------------------


def test_the_engine_carries_the_module_and_paints_it_from_the_perform_layer():
    src = ENGINE.read_text(encoding="utf-8")
    assert "/* KINETICS:BEGIN level_join */" in src
    assert src.index("/* KINETICS:BEGIN ease */") < src.index("/* KINETICS:BEGIN level_join */") < src.index("const paintPerform =")
    build = src[src.index("const buildPerform ="):src.index("const paintPerform =")]
    assert 'pageSpecies(scene, "level_join")' in build, "the builder makes the join's DOM"
    assert "ringDashes(" in build, "... with the ring species' OWN dashes (its law, handed in)"
    perform = src[src.index("const paintPerform ="):]
    perform = perform[:perform.index("\n  };\n")]
    assert "PAGE_PAINTERS.level_join" in perform, "... and the perform layer paints it through the page registry"
    kinds = src[src.index("const LP_PANEL_KINDS"):]
    assert '"level_join"' in kinds[:kinds.index(";")], "the panel filter hands the join to the panel it names"


def test_the_card_is_on_page_species_with_its_when_pulled_from_the_compiler():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["page_species:level_join"]
    assert card["token"] == "level_join" and card["when"] is None and card["serves"] == ["SPANS"]
    assert card["lives"] == {"form": "module", "path": "content/video_engine/scripts/species/level_join.mjs",
                             "symbol": "paintLevelJoin"}
    assert card["dials"] == {"module": "content/video_engine/scripts/species/level_join.mjs", "object": "LEVEL"}
    assert len(card["does"]) <= 240 and card["proof"]["golden"] == "level-join-half-a-point"
    assert "P71 T10" in card["doctrine"] and "C14" in " ".join(card["doctrine"])


def test_the_registries_know_the_join():
    import gate_motion_density as G
    import lint_species_choice as L
    import recipe_walk as RW
    from authoring import shapes as SH
    assert G.SPECIES_EVENTS["level_join"] == ("at", "end"), "the rule TRAVELS (s99): it leaves on its word and lands at its end"
    assert "level_join" in G.PLOT_INK_MARKS and "level_join" in G.PLOT_HELD_MARKS
    assert "level_join" in SH.PLOT_MARKS and "level_join" in SH.HELD_MARKS
    assert "level_join" in L.ACT_SPECIES["SPANS"]
    assert "level_join" in RW.PAGE_SPECIES_KINDS
    assert SH.marks_live([dict(JOIN)], 20.0, 24.0) == ["level_join at 11.63s"], "the landed join is still on the data"


# ---- the join read on the served player ----------------------------------------------------------------------


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
  const st = world.__lp, PF = st.perform || {}, J = (PF.levelJoins || [])[0];
  if (!J) return null;
  const d = J.rule.getAttribute('d') || '', nums = d.replace(/[ML]/g, ' ').trim().split(/\\s+/).map(Number);
  const S = (st.states && st.states[st.active | 0]) || st;
  const ser = (S.markBy || {}).s0, sp = ser && ser.geom && ser.geom.pts, k0 = (ser && ser.geom.k0) | 0, off = (S.windowOffsets || [])[0] | 0;
  const pt = (i) => sp ? sp[i - off - k0] || null : null;
  const lb = J.label.getBBox(), dashesOn = (R) => R.dashes.filter(q => q.p.getAttribute('opacity') === '1').length;
  const tags = [...st.chart.querySelectorAll('text.sname')].map(e => { const b = e.getBBox(); return [b.x, b.y, b.x + b.width, b.y + b.height]; });
  const R = (e) => e.getBoundingClientRect(), over = (a, b) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
  const tagRects = [...st.chart.querySelectorAll('text.sname')].map(R);
  const onTag = J.ringB.dashes.filter(q => q.p.getAttribute('opacity') === '1' && tagRects.some(r => over(R(q.p), r))).length;
  const fr = S.lfPanelEl ? S.lfPanelEl.getBBox() : null, frame = fr ? [fr.x, fr.y, fr.x + fr.width, fr.y + fr.height] : null;
  const tagFs = [...st.chart.querySelectorAll('text.sname')].map(e => parseFloat(getComputedStyle(e).fontSize));
  return { frame, tagFs, g: parseFloat(J.g.getAttribute('opacity') || '0'), ruleOn: J.rule.getAttribute('opacity'), rule: nums,
           a: pt(124), b: pt(225), ringA: dashesOn(J.ringA), ringB: dashesOn(J.ringB), nA: J.ringA.dashes.length,
           glyphs: J.lg.map(t => parseFloat(t.getAttribute('opacity') || '0')), side: J.side,
           label: [lb.x, lb.y, lb.x + lb.width, lb.y + lb.height], fs: parseFloat(J.label.style.fontSize), k: st.stagePx, tags, onTag };
}"""


def _serve_timeline(tl: dict, uris: dict):
    import render_baseline as RB
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "probe.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    page, errs, close = SP.open_served(html, w, h, cleanup=td.cleanup)   # R26-351: guarded

    def at(t: float, probe: str = PROBE) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(probe)

    return at, errs, close


def _off_rule(label: list, rule_y: float, x0: float, x1: float) -> bool:
    return label[3] <= rule_y or label[1] >= rule_y or label[2] <= x0 or label[0] >= x1


@needs_browser
def test_the_rule_draws_by_length_the_rings_land_and_the_label_writes_off_the_rule():
    import build_golden_sources as G
    tl, uris = G.level_join_half_a_point()
    at, errs, close = _serve_timeline(tl, uris)
    try:
        a0, dur = G.LEVEL_AT, G.LEVEL_DUR
        before, early, mid, landed, after = (at(a0 - 0.2), at(a0 + 0.25 * dur), at(a0 + 0.45 * dur),
                                             at(a0 + dur), at(a0 + dur + 3.0))
    finally:
        close()
    assert not errs, errs
    assert before["g"] == 0, before
    A, Bp = landed["a"], landed["b"]
    for f in (early, mid):
        assert f["g"] == 1 and f["ruleOn"] == "1", f
        assert abs(f["rule"][0] - A[0]) < 0.2 and abs(f["rule"][1] - A[1]) < 0.2 and abs(f["rule"][3] - A[1]) < 0.2, (f["rule"], A)
        assert A[0] < f["rule"][2] < Bp[0], "the rule is part-way: it draws BY LENGTH from the dot-com peak"
    assert early["rule"][2] < mid["rule"][2], "the rule MOVES between two instants (s99: it travels)"
    assert early["ringA"] > 0 and early["ringB"] == 0, "the `from` ring lands as the rule leaves it; the far one waits"
    assert landed["ringA"] == landed["nA"], landed
    assert 0 < landed["ringB"] < landed["nA"] and landed["onTag"] == 0, ("the far ring OPENS toward the end tag beside today's "
                                                                        "datum: every dash drawn stands clear of it", landed)
    assert abs(landed["rule"][2] - Bp[0]) < 0.2 and abs(landed["rule"][3] - A[1]) < 0.2, "a LEVEL: at 23's height, to today's x"
    assert all(g == 1 for g in landed["glyphs"]), landed["glyphs"]
    assert _off_rule(landed["label"], A[1], A[0], Bp[0]), ("C14: the figure is written off the rule", landed["label"], A)
    assert not any(landed["label"][0] < t[2] and t[0] < landed["label"][2] and landed["label"][1] < t[3] and t[1] < landed["label"][3]
                   for t in landed["tags"]), ("the figure never lands on an end tag", landed["label"], landed["tags"])
    assert after["g"] == 1 and after["rule"] == landed["rule"] and after["label"] == landed["label"], "it HOLDS - an annotation now"
    assert all(g == 1 for g in after["glyphs"]) and after["ringB"] == landed["ringB"], after


@needs_browser
def test_it_follows_a_rescale_on_the_live_scale():
    import build_golden_sources as G
    tl, uris = G.level_join_half_a_point(extra=[{"kind": "chart_to", "at": 16.0, "dur": 1.2, "to": "rescale", "ymin": 0, "ymax": 36}])
    at, errs, close = _serve_timeline(tl, uris)
    try:
        held, moved = at(15.8), at(18.0)
    finally:
        close()
    assert not errs, errs
    assert held["g"] == 1 and moved["g"] == 1, (held, moved)
    assert abs(held["rule"][1] - held["a"][1]) < 0.2 and abs(moved["rule"][1] - moved["a"][1]) < 0.2, "the rule rides its datum"
    assert moved["rule"][1] < held["rule"][1] - 20, ("a tighter scale (0..36 for 0..72) lifts the level UP the page", held["rule"], moved["rule"])
    assert abs(moved["rule"][2] - moved["b"][0]) < 0.2, moved


@needs_browser
def test_it_leaves_with_the_line_on_an_undraw():
    import build_golden_sources as G
    tl, uris = G.level_join_half_a_point(extra=[{"kind": "undraw", "at": 16.0, "dur": 0.8, "series": 0, "target": {"kind": "datum", "index": 0}}])
    at, errs, close = _serve_timeline(tl, uris)
    try:
        standing, gone = at(15.9), at(17.0)
    finally:
        close()
    assert not errs, errs
    assert standing["g"] == 1 and gone["g"] == 0, (standing["g"], gone["g"])


@needs_browser
def test_in_the_long_form_the_figure_is_a_peer_of_the_end_tag_and_stays_inside_the_plot_frame():
    """The parent's frame read (2026-09-24): the figure is a PEER of the end tag, not a card - set at the end tags' own
    size for the active preset - and its box stays inside the long form's plot frame (nudged left from the far ring at
    the frame's right edge), off the rule."""
    import build_golden_sources as G
    tl, uris = G.level_join_half_a_point(longform=True)
    at, errs, close = _serve_timeline(tl, uris)
    try:
        landed = at(G.LEVEL_AT + G.LEVEL_DUR)
    finally:
        close()
    assert not errs, errs
    assert landed["tagFs"] and all(abs(landed["fs"] - f) < 1e-3 for f in landed["tagFs"]), (landed["fs"], landed["tagFs"])
    F, lb = landed["frame"], landed["label"]
    assert F and F[0] <= lb[0] and lb[2] <= F[2] and F[1] <= lb[1] and lb[3] <= F[3], ("inside the plot frame", lb, F)
    assert _off_rule(landed["label"], landed["a"][1], landed["a"][0], landed["b"][0]), landed


# ---- a join on ONE panel of a panels page (`panel: <i>`; LP_PANEL_KINDS): both anchors are read on that panel ------

PANELS_V3 = OBJECTS / "ev-tnx-two-eras-v3.series.json"
PANEL_JOIN = {"kind": "level_join", "at": 12.0, "dur": 1.6, "from": 0, "to": 71, "panel": 1, "label": "+4"}   # the AI era: 0.917 -> 4.875


def _panels_world() -> dict:
    return {"kind": "ledger", "page": B.stamp_full_stage(LPG.build_spec(LPG.load_series(PANELS_V3), "line", None, "right"))}


def test_a_join_names_its_panel_and_is_judged_on_that_panels_data():
    assert _errs([PANEL_JOIN], plate="ledger:golden-panels:line") == []
    world = _panels_world()
    B.check_panels(world, [dict(PANEL_JOIN)])
    assert B.check_level_join(world, [dict(PANEL_JOIN)]) == []
    with pytest.raises(ValueError, match=r"label '\+5' writes 5 but the two data it joins differ by 3.958 \(0.917 -> 4.875\)"):
        B.check_level_join(world, [dict(PANEL_JOIN, label="+5")])
    with pytest.raises(ValueError, match=r"series 1 is past the page's last series \(0\)"):
        B.check_level_join(world, [dict(PANEL_JOIN, series=1)])


PANEL_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  return (world.__lp.panels || []).map((S, i) => {
    const J = ((S.perform || {}).levelJoins || [])[0];
    const ser = (S.markBy || {}).s0, sp = ser && ser.geom && ser.geom.pts, k0 = (ser && ser.geom.k0) | 0;
    if (!J) return { i, join: null };
    const nums = (J.rule.getAttribute('d') || '').replace(/[ML]/g, ' ').trim().split(/\\s+/).map(Number);
    return { i, g: parseFloat(J.g.getAttribute('opacity') || '0'), rule: nums, a: sp ? sp[0 - k0] : null, b: sp ? sp[71 - k0] : null };
  });
}"""


@needs_browser
def test_the_join_draws_on_the_panel_it_names_and_no_other():
    import build_golden_sources as G
    tl, uris = G._panels_page(LPG.load_series(PANELS_V3), [dict(PANEL_JOIN)], "probe: a level join on panel 2")
    at, errs, close = _serve_timeline(tl, uris)
    try:
        landed = at(14.5, PANEL_PROBE)
    finally:
        close()
    assert not errs, errs
    assert landed[0].get("join") is None, "panel 1 carries no join"
    p = landed[1]
    assert p["g"] == 1 and abs(p["rule"][0] - p["a"][0]) < 0.2 and abs(p["rule"][1] - p["a"][1]) < 0.2, p
    assert abs(p["rule"][2] - p["b"][0]) < 0.2 and abs(p["rule"][3] - p["a"][1]) < 0.2, "the level at the panel's own first datum, to its 71st"
