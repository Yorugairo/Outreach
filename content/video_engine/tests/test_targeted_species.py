"""P35 T7 - the targeting law as code (doc 29 s9.27 MOTION MENU, s9.28 C3/C4):
`build_scene_timeline_f.validate_species` rejects a pointing species with no
declared target, two camera moves on one row, a camera move over Ken Burns,
and any species firing inside the pivot's reversal; a well-formed list is
accepted and emitted verbatim. Pure function - no episode build needed."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
import build_scene_timeline_f as B  # noqa: E402

PLATE = "world-spike-desk-v1"
STILL = (0, 0, 0)
POINT = {"kind": "point", "x": 0.62, "y": 0.41, "semantic": "the iron spike"}
DATUM = {"kind": "datum", "index": 7}
SPAN = {"kind": "span", "from_word": 3, "to_word": 5}
REGION = {"kind": "region", "x0": 0.1, "y0": 0.2, "x1": 0.5, "y1": 0.6}


def _sp(kind, at=10.0, dur=1.2, target=None):
    e = {"kind": kind, "at": at, "dur": dur}
    if target is not None:
        e["target"] = target
    return e


# ---- the targeting law: no declared target, no firing - and we fail, not drop ----

def test_callout_without_a_target_is_an_error_naming_the_kind():
    errs = B.validate_species([_sp("callout")], STILL, PLATE)
    assert len(errs) == 1 and errs[0].startswith("callout: no declared target"), errs
    assert "does not fire" in errs[0]


def test_every_pointing_kind_requires_a_target():
    for kind in ("punch", "callout", "focus_zoom", "spotlight", "squiggle", "pull_back", "beat_freeze", "radial", "push"):
        errs = B.validate_species([_sp(kind)], STILL, PLATE)
        assert errs and errs[0].startswith(f"{kind}: no declared target"), (kind, errs)


def test_plate_life_needs_no_target():
    assert B.validate_species([_sp("plate_life", at=12.0, dur=18.0)], (0.04, 10, -6), PLATE) == []


def test_beat_freeze_radial_push_take_only_point_or_region():
    for kind in ("beat_freeze", "radial", "push"):
        assert B.validate_species([_sp(kind, target=POINT)], STILL, PLATE) == []
        assert B.validate_species([_sp(kind, target=REGION)], STILL, PLATE) == []
        errs = B.validate_species([_sp(kind, target=DATUM)], STILL, PLATE)
        assert errs == [f"{kind}: target kind 'datum' not allowed (takes point|region)"], errs


def test_target_shapes_are_validated():
    bad_point = {"kind": "point", "x": 1.4, "y": 0.2}
    assert any("not a 0..1 fraction" in e for e in B.validate_species([_sp("callout", target=bad_point)], STILL, PLATE))
    bad_datum = {"kind": "datum", "index": "seven"}
    assert any("needs numeric 'index'" in e for e in B.validate_species([_sp("callout", target=bad_datum)], STILL, PLATE))
    frac_datum = {"kind": "datum", "index": 2.5}
    assert any("non-negative integer index" in e for e in B.validate_species([_sp("callout", target=frac_datum)], STILL, PLATE))
    bad_span = {"kind": "span", "from_word": 9, "to_word": 2}
    assert B.validate_species([_sp("squiggle", target=bad_span)], STILL, PLATE) == ["squiggle: target span from_word > to_word"]
    no_kind = {"x": 0.1, "y": 0.1}
    assert any("must be a dict of kind datum|point|region|span" in e for e in B.validate_species([_sp("punch", target=no_kind)], STILL, PLATE))
    dense = {"kind": "datum", "index": 3, "series": 1}
    assert B.validate_species([_sp("callout", target=dense)], STILL, PLATE) == []


def test_unknown_kind_and_bad_timing_are_errors():
    assert B.validate_species([_sp("wiggle", target=POINT)], STILL, PLATE)[0].startswith("species entry")
    assert any("'at' must be a number" in e for e in B.validate_species([_sp("punch", at="ten", target=POINT)], STILL, PLATE))
    assert any("dur must be > 0" in e for e in B.validate_species([_sp("punch", dur=0, target=POINT)], STILL, PLATE))


# ---- one camera move per window (s9.28 C3) --------------------------------------

def test_two_camera_moves_on_one_row_is_an_exclusivity_error():
    errs = B.validate_species([_sp("punch", target=POINT), _sp("focus_zoom", at=14.0, dur=2.0, target=DATUM)], STILL, PLATE)
    assert errs == [f"{PLATE}: punch + focus_zoom on one row - one camera move per window (s9.28 C3)"], errs


def test_camera_move_over_ken_burns_is_an_error():
    errs = B.validate_species([_sp("punch", target=POINT)], (0.04, 10, -6), PLATE)
    assert len(errs) == 1 and "punch over Ken Burns scale 0.04" in errs[0] and "s9.28 C3" in errs[0], errs


def test_camera_move_on_a_still_plate_with_a_point_target_is_ok():
    rows = [_sp("punch", target=POINT)]
    assert B.validate_species(rows, STILL, PLATE) == []
    assert B.validate_species([_sp("pull_back", target=DATUM), _sp("callout", at=16.0, target=DATUM)], STILL, PLATE) == []


def test_non_camera_species_may_share_a_row_with_ken_burns():
    rows = [_sp("callout", target=DATUM), _sp("spotlight", at=13.0, dur=2.0, target=REGION), _sp("squiggle", target=SPAN)]
    assert B.validate_species(rows, (0.05, 12, 6), PLATE) == []


# ---- the pivot's reversal takes no species (s9.28 C4) ---------------------------

def test_species_inside_a_synthetic_pivot_span_is_an_error():
    errs = B.validate_species([_sp("callout", at=395.0, target=DATUM)], STILL, PLATE, pivot_span=(391.9, 399.6))
    assert errs == [f"{PLATE}: callout at 395.0s fires inside the pivot's reversal 391.9-399.6s (s9.28 C4)"], errs
    # overlapping the span from before it also fires inside it
    assert B.validate_species([_sp("spotlight", at=390.0, dur=3.0, target=REGION)], STILL, PLATE, pivot_span=(391.9, 399.6))
    # outside the span: fine; and the build's default (None) never checks
    assert B.validate_species([_sp("callout", at=400.5, target=DATUM)], STILL, PLATE, pivot_span=(391.9, 399.6)) == []
    assert B.validate_species([_sp("callout", at=395.0, target=DATUM)], STILL, PLATE) == []


# ---- emission: verbatim onto the scene, kinds onto the timeline -----------------

def test_species_list_is_emitted_verbatim_and_kinds_extend_the_timeline_species():
    rows = [_sp("punch", target=POINT), _sp("callout", at=12.0, target=DATUM)]
    assert B.validate_species(rows, STILL, PLATE) == []
    scenes = [{"world": {"asset_id": PLATE}, "species": rows},
              {"world": {"kind": "ledger"}, "species": [_sp("plate_life", dur=5.0), _sp("punch", target=POINT)]},
              {"world": {"asset_id": "world-x"}, "species": []}]
    assert scenes[0]["species"] is rows and scenes[0]["species"][0]["target"] == POINT
    assert B.timeline_species(scenes) == ["ledger", "punch", "callout", "plate_life"]
    assert B.timeline_species([{"world": {"asset_id": "world-x"}, "species": []}]) == []


def test_missing_or_none_species_is_an_empty_list():
    assert B.validate_species(None, STILL, PLATE) == []
    assert B.validate_species([], (0.04, 10, -6), PLATE) == []
    assert B.validate_species("punch", STILL, PLATE) == [f"{PLATE}: species must be a list of species dicts"]


# ---- the hop (2026-09-08, the crossings map): an opt-in on trace, validated when present ----

def test_trace_hop_is_accepted_with_fraction_endpoints():
    e = _sp("trace", target=REGION)
    e["hop"] = {"from": [0.215, 0.425], "to": [0.65, 0.34], "bow": -0.16, "draw_s": 0.55, "width": 7}
    assert B.validate_species([e], STILL, PLATE) == []


def test_trace_hop_endpoints_must_be_stage_fractions():
    e = _sp("trace", target=REGION)
    e["hop"] = {"from": [0.2, 1.4], "to": "Ontario"}
    errs = B.validate_species([e], STILL, PLATE)
    assert any("hop.from must be [x, y]" in x for x in errs) and any("hop.to must be [x, y]" in x for x in errs), errs


def test_trace_hop_draw_s_must_be_positive_and_plain_trace_is_untouched():
    e = _sp("trace", target=REGION)
    e["hop"] = {"from": [0.1, 0.1], "to": [0.5, 0.5], "draw_s": 0}
    assert any("hop.draw_s must be > 0" in x for x in B.validate_species([e], STILL, PLATE))
    assert B.validate_species([_sp("trace", target=REGION)], STILL, PLATE) == []


# ---- E56 (2026-09-09): a ring has ONE use - a number or a point on a CHART; a picture's focus is a light ----

def test_e56_a_callout_ring_on_a_picture_point_is_refused():
    errs = B.validate_species([_sp("callout", target=POINT)], STILL, PLATE)
    assert any("E56" in e and "spotlight" in e for e in errs), errs


def test_e56_a_datum_ring_and_a_numeric_stamp_pass():
    assert not [e for e in B.validate_species([_sp("callout", target=DATUM)], STILL, PLATE) if "E56" in e]
    stamp = dict(_sp("callout", target=POINT), label="25%")
    assert not [e for e in B.validate_species([stamp], STILL, PLATE) if "E56" in e]
    light = _sp("spotlight", target=POINT)
    assert not [e for e in B.validate_species([light], STILL, PLATE) if "E56" in e]


# ---- P50 T2: THE ICON CHIP (the Bravos icon board, shots 26-28) -------------------------------
# A chip lands on its word with a SOURCED glyph and a label, at a declared point or region, and is
# crossed out on a LATER word. Each refusal names the kind, the way every other species' does.

def _chip(**kw):
    e = {"kind": "chip", "at": 10.0, "dur": 6.0, "icon": "factory", "label": "STEEL",
         "target": {"kind": "point", "x": 0.3, "y": 0.5}}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def test_a_chip_without_a_target_is_refused_by_name():
    errs = B.validate_species([_chip(target=None)], STILL, PLATE)
    assert any(e.startswith("chip: no declared target") for e in errs), errs
    # ... and a datum is not one of its two: a chip is a card on the frame, not an annotation of a bar
    errs = B.validate_species([_chip(target=DATUM)], STILL, PLATE)
    assert errs == ["chip: target kind 'datum' not allowed (takes point|region)"], errs
    assert B.validate_species([_chip(target=REGION)], STILL, PLATE) == []


def test_a_chip_without_a_sourced_icon_is_refused_by_name():
    for bad, needle in ((None, "'icon' names a sourced glyph"), ("", "'icon' names a sourced glyph"),
                        ("../secrets", "'icon' names a sourced glyph"), (7, "'icon' names a sourced glyph"),
                        ("no-such-glyph", "is not in content/video_engine/assets/icons")):
        entry = _chip()
        if bad is None:
            entry.pop("icon")
        else:
            entry["icon"] = bad
        errs = B.validate_species([entry], STILL, PLATE)
        assert any(e.startswith("chip: ") and needle in e for e in errs), (bad, errs)
    # a chip with no label is refused the same way - a chip names the thing it stands for
    errs = B.validate_species([_chip(label=None)], STILL, PLATE)
    assert any(e.startswith("chip: 'label' must be a non-empty string") for e in errs), errs
    assert any(e.startswith("chip: 'label'") for e in B.validate_species([_chip(label="  ")], STILL, PLATE))


def test_a_chip_crossed_before_it_lands_is_refused_by_name():
    for bad in (10.0, 9.5, -1):
        errs = B.validate_species([_chip(cross_at=bad)], STILL, PLATE)
        assert any(e.startswith("chip: cross_at") and "LATER word" in e for e in errs), (bad, errs)
    assert any(e.startswith("chip: 'cross_at' must be a number")
               for e in B.validate_species([_chip(cross_at="later")], STILL, PLATE))
    assert any(e.startswith("chip: state must be one of")
               for e in B.validate_species([_chip(state="struck")], STILL, PLATE))
    assert B.validate_species([_chip(cross_at=13.5)], STILL, PLATE) == []
    assert B.validate_species([_chip(state="crossed")], STILL, PLATE) == []


def test_a_good_chip_passes_and_its_icon_lands_in_the_asset_map():
    assert B.validate_species([_chip(cross_at=14.0, state="on", idle="breath")], STILL, PLATE) == []
    assert B.SPECIES_WHEN["chip"] and B.SPECIES_TARGETS["chip"] == ("point", "region")
    # the asset route: the compiler embeds the SOURCED file's geometry under `icon:<name>`, keeping only
    # shapes and their geometry attributes - the player never receives markup it has to trust
    key = B.ICON_PREFIX + "factory"
    assert key == "icon:factory"
    geo = json.loads(B.icon_geometry("factory"))
    assert geo["vb"] == [0, 0, 24, 24]
    assert geo["el"] and all(n["t"] in B.ICON_TAGS for n in geo["el"]), geo["el"]
    assert all(set(n["a"]) <= set(B.ICON_ATTRS) and n["a"] for n in geo["el"]), geo["el"]
    assert not any("stroke" in n["a"] or "style" in n["a"] or "onload" in n["a"] for n in geo["el"])
    for name in ("no-such-glyph", "../../etc/passwd", "Factory"):
        with pytest.raises(ValueError, match="icon"):
            B.icon_geometry(name)


# ---- P50 T3: the press card's UNDERLINE - E56's one exception, and its refusals ----
# The species grammar gains no KIND here (a press card is a DOCK kind): it gains a target, `phrase`,
# which points INSIDE a press card, and a form, `underline`, which is the only thing allowed to point
# there. A ring on a card is still a ring, and E56 still refuses it by name.

PRESS_DOCKS = {"ev-press-herald": {"kind": "press", "source": "The Herald, 4 Mar 2026",
                                   "phrase": {"x0": 0.12, "y0": 0.2, "x1": 0.66, "y1": 0.44}}}
PHRASE = {"kind": "phrase", "dock": "ev-press-herald"}


def _underline(**kw):
    e = {"kind": "callout", "form": "underline", "at": 12.0, "dur": 2.0, "target": dict(PHRASE)}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def test_an_underline_on_a_press_cards_phrase_is_admitted():
    assert B.validate_species([_underline()], STILL, PLATE, press_docks=PRESS_DOCKS) == []
    assert B.SPECIES_TARGETS["callout"][-1] == B.PHRASE_TARGET
    assert B.PHRASE_TARGET not in B.SPECIES_TARGETS["spotlight"], "the callout alone may point inside a card"


def test_a_ring_on_a_press_card_is_still_refused_by_e56():
    errs = B.validate_species([_underline(form=None)], STILL, PLATE, press_docks=PRESS_DOCKS)
    assert len(errs) == 1 and "(E56)" in errs[0] and errs[0].startswith("callout: a ring circles"), errs
    assert 'form: "underline"' in errs[0], "the message names the one exception"
    # ... and a label full of numbers does not buy a ring onto a card either
    assert B.validate_species([_underline(form=None, label="4.6%")], STILL, PLATE, press_docks=PRESS_DOCKS) == errs


def test_a_phrase_target_that_names_no_press_dock_is_refused_by_name():
    errs = B.validate_species([_underline(target={"kind": "phrase", "dock": "ev-golden-chart"})], STILL, PLATE,
                              press_docks=PRESS_DOCKS)
    assert len(errs) == 1 and "is not a PRESS dock on this row" in errs[0], errs
    # the same row with no press dock at all - the safe direction is refusal
    assert "is not a PRESS dock on this row" in B.validate_species([_underline()], STILL, PLATE)[0]
    for bad in (None, "", 7):
        errs = B.validate_species([_underline(target={"kind": "phrase", "dock": bad})], STILL, PLATE,
                                  press_docks=PRESS_DOCKS)
        assert any("target phrase must name its card" in e for e in errs), (bad, errs)


def test_only_a_callout_may_point_inside_a_press_card():
    for kind in ("punch", "spotlight", "focus_zoom", "squiggle", "chip"):
        errs = B.validate_species([{"kind": kind, "at": 12.0, "dur": 2.0, "target": dict(PHRASE),
                                    "icon": "factory", "label": "STEEL"}], STILL, PLATE, press_docks=PRESS_DOCKS)
        assert any("target kind 'phrase' not allowed" in e for e in errs), (kind, errs)


def test_the_form_is_the_underline_and_it_belongs_to_a_phrase():
    errs = B.validate_species([_underline(form="highlight")], STILL, PLATE, press_docks=PRESS_DOCKS)
    assert errs == ["callout: form 'highlight' is not one of underline"], errs
    # a form on a point / datum target is the press card's underline in the wrong place
    errs = B.validate_species([_underline(target=POINT, label="4%")], STILL, PLATE, press_docks=PRESS_DOCKS)
    assert len(errs) == 1 and "it takes a phrase target" in errs[0], errs
    assert B.validate_species([_underline(form=None, target=DATUM)], STILL, PLATE, press_docks=PRESS_DOCKS) == []


def test_the_ring_on_a_picture_is_refused_exactly_as_it_was_before_the_exception():
    errs = B.validate_species([_sp("callout", target=POINT)], STILL, PLATE)
    assert len(errs) == 1 and "(E56)" in errs[0] and "use a spotlight (the light) on a picture" in errs[0], errs
    assert B.validate_species([{**_sp("callout", target=POINT), "label": "+613%"}], STILL, PLATE) == []


# ---- P50 T4: THE FLOW DIAGRAM and THE SPAN ----------------------------------------------------------------
# A flow names 2-6 things by SOURCED glyph, the arrows between them BY NAME, and - at most once - the node that
# swaps on a LATER word while the rest stands (Bravos shots 82-86). A span names a STRETCH OF TIME on a ledger
# page's chart. Everything is checked by name, so a typo is a build error and never a diagram missing an arrow.
LEDGER = B.LEDGER_PREFIX + "ev-golden:line"
BOX = {"kind": "region", "x0": 0.1, "y0": 0.5, "x1": 0.9, "y1": 0.9}


def _flow(**kw):
    e = {"kind": "flow", "at": 10.0, "dur": 8.0, "target": dict(BOX),
         "nodes": [{"id": "plant", "icon": "factory", "label": "PLANTS"},
                   {"id": "freight", "icon": "ship", "label": "FREIGHT"},
                   {"id": "price", "icon": "coins", "label": "PRICE"}],
         "edges": [["plant", "freight"], ["freight", "price"]]}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def _span(**kw):
    e = {"kind": "span", "at": 10.0, "dur": 6.0, "from": 10, "to": 60, "label": "THE DECADE"}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def test_a_flow_without_a_region_target_is_refused_by_name():
    errs = B.validate_species([_flow(target=None)], STILL, PLATE)
    assert any(e.startswith("flow: no declared target") for e in errs), errs
    # a diagram needs its ROOM: a point leaves its size to the painter, a datum is a chart's annotation
    for bad in (POINT, DATUM, SPAN):
        errs = B.validate_species([_flow(target=bad)], STILL, PLATE)
        assert errs == [f"flow: target kind {bad['kind']!r} not allowed (takes region)"], (bad, errs)
    assert B.SPECIES_TARGETS["flow"] == ("region",)


def test_a_flow_with_too_few_or_too_many_nodes_is_refused_by_name():
    one = [{"id": "plant", "icon": "factory", "label": "PLANTS"}]
    errs = B.validate_species([_flow(nodes=one, edges=[["plant", "plant"]])], STILL, PLATE)
    assert len(errs) == 1 and errs[0].startswith("flow: 'nodes' must be a list of 2-6") and "is a chip" in errs[0], errs
    seven = [{"id": f"n{i}", "icon": "factory", "label": f"N{i}"} for i in range(7)]
    assert any("must be a list of 2-6" in e for e in B.validate_species([_flow(nodes=seven)], STILL, PLATE))
    # ... and a node without an id, a label or a SOURCED glyph, each named
    twins = [{"id": "a", "icon": "factory", "label": "A"}, {"id": "a", "icon": "ship", "label": "B"}]
    errs = B.validate_species([_flow(nodes=twins, edges=[["a", "a"]])], STILL, PLATE)
    assert any("id 'a' is already a node" in e for e in errs), errs
    for bad, needle in ((None, "'icon' names a sourced glyph"), ("Factory", "'icon' names a sourced glyph"),
                        ("not-a-real-icon", "is not in content/video_engine/assets/icons")):
        nodes = [{"id": "a", "icon": bad, "label": "A"}, {"id": "b", "icon": "ship", "label": "B"}]
        errs = B.validate_species([_flow(nodes=nodes, edges=[["a", "b"]])], STILL, PLATE)
        assert any(e.startswith("flow: node 0") and needle in e for e in errs), (bad, errs)
    nodes = [{"id": "a", "icon": "factory", "label": "  "}, {"id": "b", "icon": "ship", "label": "B"}]
    errs = B.validate_species([_flow(nodes=nodes, edges=[["a", "b"]])], STILL, PLATE)
    assert any(e.startswith("flow: node 0: 'label'") for e in errs), errs


def test_a_flow_edge_naming_something_that_is_not_a_node_is_refused_by_name():
    errs = B.validate_species([_flow(edges=[["plant", "ghost"]])], STILL, PLATE)
    assert len(errs) == 1 and "edge 0 names 'ghost'" in errs[0] and "plant, freight, price" in errs[0], errs
    errs = B.validate_species([_flow(edges=[["plant", "plant"]])], STILL, PLATE)
    assert any("edge 0 runs from 'plant' to itself" in e for e in errs), errs
    errs = B.validate_species([_flow(edges=[])], STILL, PLATE)
    assert any("a diagram with no arrows is a chip board" in e for e in errs), errs
    assert any("edge 0 must be [from, to]" in e for e in B.validate_species([_flow(edges=[["plant"]])], STILL, PLATE))


def test_a_flow_swap_on_the_same_word_or_naming_no_node_is_refused_by_name():
    for bad in (10.0, 9.5, 0.0):
        errs = B.validate_species([_flow(swap={"at": bad, "node": "freight", "icon": "cpu", "label": "CHIPS"})], STILL, PLATE)
        assert any(e.startswith(f"flow: swap at {bad}") and "LATER word" in e for e in errs), (bad, errs)
    errs = B.validate_species([_flow(swap={"at": 19.0, "node": "freight", "icon": "cpu", "label": "CHIPS"})], STILL, PLATE)
    assert any("falls outside the diagram's window" in e and "would never fire" in e for e in errs), errs
    errs = B.validate_species([_flow(swap={"at": "later", "node": "freight", "icon": "cpu", "label": "CHIPS"})], STILL, PLATE)
    assert any(e.startswith("flow: swap 'at' must be a number") for e in errs), errs
    errs = B.validate_species([_flow(swap={"at": 13.0, "node": "ghost", "icon": "cpu", "label": "CHIPS"})], STILL, PLATE)
    assert any("swap names node 'ghost'" in e for e in errs), errs
    errs = B.validate_species([_flow(swap={"at": 13.0, "node": "freight", "icon": "no-such-glyph", "label": "CHIPS"})], STILL, PLATE)
    assert any(e.startswith("flow: swap: icon") for e in errs), errs
    errs = B.validate_species([_flow(swap={"at": 13.0, "node": "freight", "icon": "cpu", "label": ""})], STILL, PLATE)
    assert any(e.startswith("flow: swap 'label'") for e in errs), errs
    assert any(e.startswith("flow: 'swap' must be a dict") for e in B.validate_species([_flow(swap=13.0)], STILL, PLATE))


def test_a_span_out_of_order_or_off_a_ledger_page_is_refused_by_name():
    for lo, hi in ((60, 10), (10, 10), (0.6, 0.2)):
        errs = B.validate_species([_span(**{"from": lo, "to": hi})], STILL, LEDGER)
        assert any(e.startswith(f"span: from {lo} is not before to {hi}") for e in errs), (lo, hi, errs)
    errs = B.validate_species([_span(**{"from": 10, "to": 0.8})], STILL, LEDGER)
    assert any("name BOTH edges the same way" in e for e in errs), errs
    for bad, needle in ((-1, "is not a non-negative datum index"), (1.4, "is not a 0..1 fraction"),
                        ("Jan", "must be a datum index (an integer) or an x-fraction")):
        errs = B.validate_species([_span(**{"from": bad})], STILL, LEDGER)
        assert any(e.startswith("span: 'from'") or f"span: from={bad}" in e for e in errs), (bad, errs)
        assert any(needle in e for e in errs), (bad, errs)
    assert any(e.startswith("span: needs a non-empty string label") and "a bracket MEASURES" in e
               for e in B.validate_species([_span(label="  ")], STILL, LEDGER))
    assert any(e.startswith("span: color must be one of") for e in B.validate_species([_span(color="puce")], STILL, LEDGER))
    # ... and a span is a PAGE species: it performs on a ledger page, not on a plate
    errs = B.validate_species([_span()], STILL, PLATE)
    assert errs == [f"{PLATE}: span is a page species - it performs on a ledger page, not on {PLATE!r}"], errs
    assert "span" in B.PAGE_SPECIES and B.SPECIES_TARGETS["span"] == ()


def test_a_good_flow_and_a_good_span_pass_and_every_glyph_lands_in_the_asset_map():
    good = _flow(swap={"at": 13.0, "node": "freight", "icon": "cpu", "label": "CHIPS"}, tag="1973", idle="breath")
    assert B.validate_species([good], STILL, PLATE) == []
    assert B.validate_species([_span()], STILL, LEDGER) == []
    assert B.validate_species([_span(**{"from": 0.2, "to": 0.8}, color="cobalt", series=1)], STILL, LEDGER) == []
    # the asset-map route: every SOURCED glyph the row carries, in declaration order, embedded as geometry
    assert B.species_icons(good) == ["factory", "ship", "coins", "cpu"]
    assert B.species_icons(_span()) == [] and B.species_icons(None) == []
    assert B.species_icons({"kind": "chip", "icon": "landmark"}) == ["landmark"]
    for name in B.species_icons(good):
        geo = json.loads(B.icon_geometry(name))
        assert geo["el"] and len(geo["vb"]) == 4, name
    # and both kinds carry a `when` and an event edge (P50 T1's rule, the gate's table)
    assert B.SPECIES_WHEN["flow"].startswith("the sentence EXPLAINS a mechanism")
    assert B.SPECIES_WHEN["span"].startswith("the sentence SPANS a period on a chart")


# ---- P50 T5: THE VECTOR MAP - the world, the three species and their places -------
VECMAP = "vecmap:IRN,USA,CHN"
IRN = {"kind": "country", "id": "IRN"}
GULF = {"kind": "mappoint", "x": 644, "y": 178}


def _light(**kw):
    e = {"kind": "light", "at": 5.0, "dur": 6.0, "target": dict(IRN)}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def _arc(**kw):
    e = {"kind": "arc", "at": 6.6, "dur": 8.0, "from": dict(GULF), "to": {"kind": "country", "id": "USA"}}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def _stamp(**kw):
    e = {"kind": "stamp", "at": 8.0, "dur": 6.0, "text": "1.4 Billion Barrels", "target": {"kind": "country", "id": "CHN"}}
    e.update(kw)
    return {k: v for k, v in e.items() if v is not None}


def test_the_map_species_are_refused_off_a_vecmap_world_by_name():
    for entry in (_light(), _arc(), _stamp()):
        for plate in (PLATE, LEDGER, "clip:evidence/objects/x.mp4"):
            errs = B.validate_species([entry], STILL, plate)
            assert any(e.startswith(f"{plate}: {entry['kind']} is a vecmap species") and "vector map world" in e
                       for e in errs), (entry["kind"], plate, errs)
    # ... and a plate whose id merely BEGINS with the word is not a map
    assert any("is a vecmap species" in e for e in B.validate_species([_light()], STILL, "vecmap-desk-v1"))
    # every other species keeps its stage coordinates: a country target is not one of them
    errs = B.validate_species([_sp("callout", target=dict(IRN))], STILL, VECMAP)
    assert "callout: target kind 'country' not allowed (takes datum|point|region|span|phrase)" in errs, errs
    assert any("a ring circles a NUMBER or a POINT ON A CHART (E56)" in e for e in errs),         "E56 refuses it twice over: a ring around a country is exactly the light the map ships"


def test_a_light_on_a_country_that_is_not_in_the_map_is_refused_by_name():
    errs = B.validate_species([_light(target={"kind": "country", "id": "ATLANTIS"})], STILL, VECMAP)
    assert len(errs) == 1 and "country 'ATLANTIS' is not in world-110m" in errs[0] and "ISO A3" in errs[0], errs
    for bad in ({"kind": "country", "id": "irn"}, {"kind": "country"}, {"kind": "country", "id": 7}):
        assert any("is not in world-110m" in e for e in B.validate_species([_light(target=bad)], STILL, VECMAP)), bad
    # a light lights a COUNTRY: a map point has no outline to fill
    errs = B.validate_species([_light(target=dict(GULF))], STILL, VECMAP)
    assert errs == ["light: target kind 'mappoint' not allowed (takes country)"], errs
    # ... and the world id itself refuses a name that is not a place
    with pytest.raises(ValueError, match="is not a country in world-110m"):
        B.parse_vecmap_id("vecmap:IRN,ATLANTIS")
    with pytest.raises(ValueError, match="named twice"):
        B.parse_vecmap_id("vecmap:IRN,IRN")
    with pytest.raises(ValueError, match="VECMAP_FOCUS_MAX"):
        B.parse_vecmap_id("vecmap:IRN,USA,CHN,JPN,DEU,GBR,MEX")
    assert B.parse_vecmap_id("vecmap") == [] and B.parse_vecmap_id(VECMAP) == ["IRN", "USA", "CHN"]


def test_a_mappoint_outside_the_maps_own_box_is_refused_by_name():
    box = B.world_map()["box"]
    for bad in ({"kind": "mappoint", "x": box[0] + 1, "y": 100}, {"kind": "mappoint", "x": 100, "y": -2},
                {"kind": "mappoint", "x": "640", "y": 100}, {"kind": "mappoint", "y": 100}):
        errs = B.validate_species([_arc(**{"from": bad})], STILL, VECMAP)
        assert any("mappoint" in e and ("outside the map" in e or "needs numeric" in e) for e in errs), (bad, errs)
    assert any("outside the map's 1000 x 500 box" in e
               for e in B.validate_species([_stamp(target={"kind": "mappoint", "x": 1200, "y": 10})], STILL, VECMAP))
    # the two ENDS are required, and each is a place
    assert any(e.startswith("arc: no 'to'") for e in B.validate_species([_arc(to=None)], STILL, VECMAP))
    assert any("must be a place on the map" in e for e in B.validate_species([_arc(**{"from": POINT})], STILL, VECMAP))


def test_an_arc_cut_on_the_same_word_or_outside_its_window_is_refused_by_name():
    for bad in (6.6, 4.0):
        errs = B.validate_species([_arc(crossed=bad)], STILL, VECMAP)
        assert any(e.startswith(f"arc: crossed {bad}") and "LATER word" in e for e in errs), (bad, errs)
    errs = B.validate_species([_arc(crossed=20.0)], STILL, VECMAP)
    assert any("falls outside the arc's window" in e and "would never fire" in e for e in errs), errs
    assert any(e.startswith("arc: 'crossed' must be a number") for e in B.validate_species([_arc(crossed="later")], STILL, VECMAP))
    # a stamp says what it stamps, at one of two sizes
    assert any(e.startswith("stamp: 'text'") for e in B.validate_species([_stamp(text="  ")], STILL, VECMAP))
    assert any(e.startswith("stamp: size must be one of") for e in B.validate_species([_stamp(size="huge")], STILL, VECMAP))


def test_a_vecmap_world_is_built_from_the_plate_id_and_takes_no_ken_burns():
    world = B.world_for_plate(VECMAP + ";idle=drift", STILL, None)
    assert world["kind"] == "vecmap" and world["map"] == B.WORLD_MAP
    assert world["focus"] == ["IRN", "USA", "CHN"] and world["box"] == [1000, 500]
    assert world["ken_burns"] == {"scale": 0, "x": 0, "y": 0} and world["idle"] == "drift"
    assert B.world_for_plate("vecmap", STILL, None)["focus"] == []
    with pytest.raises(ValueError, match="takes no Ken Burns"):
        B.world_for_plate(VECMAP, (0.04, 10, -6), None)


def test_a_good_map_row_passes_and_the_map_lands_in_the_asset_map_once():
    good = [_light(idle="breath"), _arc(crossed=11.5), _stamp(size="year", text="1996", target=dict(GULF)), _stamp()]
    assert B.validate_species(good, STILL, VECMAP) == []
    # the asset route: ONE key for the whole world, whatever the build asks for it
    uris = {}
    for plate in (VECMAP, "vecmap", "vecmap:JPN"):
        world = B.world_for_plate(plate, STILL, None)
        uris[B.MAP_PREFIX + world["map"]] = B.world_map_json(world["map"])
    assert list(uris) == ["map:world-110m"]
    data = json.loads(uris["map:world-110m"])
    assert len(data["countries"]) == 177 and data["box"] == [1000, 500]
    assert all(data["countries"][a3]["centroid"] for a3 in ("IRN", "USA", "CHN"))
    assert B.species_icons(good[0]) == [], "a map species carries no sourced glyph - its geometry IS the map"
    # ... and each of the three carries a `when` (P50 T1's rule) naming the act the map answers
    assert B.SPECIES_WHEN["light"].startswith("the sentence NAMES a place")
    assert B.SPECIES_WHEN["arc"].startswith("the sentence NAMES a flow between two places")
    assert B.SPECIES_WHEN["stamp"].startswith("the sentence puts a NUMBER or a name on a place")


# ---- P50 T9: a TIER is a series index on a tiers page ------------------------

def test_a_build_to_names_its_tier_and_the_word_is_the_authors(tmp_path):
    """The bands draw in turn on their words: a `build_to` per tier. A tier IS a series index - one
    resolution, not two - so `tier` is admitted beside the datum and refused where it means nothing."""
    good = {"kind": "build_to", "at": 9.5, "dur": 2.0, "tier": 1, "target": DATUM}
    assert B.validate_species([good], STILL, "ledger:two-reserves:tiers") == []
    assert B.validate_species([{**good, "series": 1}], STILL, "ledger:two-reserves:tiers") == [], "the same index twice is not a disagreement"
    errs = B.validate_species([{**good, "series": 0}], STILL, "ledger:two-reserves:tiers")
    assert len(errs) == 1 and "tier 1 and series 0 disagree" in errs[0], errs
    errs = B.validate_species([{**good, "tier": -1}], STILL, "ledger:two-reserves:tiers")
    assert len(errs) == 1 and "tier must be a non-negative integer band index" in errs[0], errs
    errs = B.validate_species([{"kind": "note", "at": 9.5, "dur": 2.0, "text": "a side fact", "tier": 1}], STILL, "ledger:two-reserves:tiers")
    assert len(errs) == 1 and "'tier' belongs to the page species that name a series" in errs[0], errs


def test_the_brackets_bar_form_is_admitted_and_anything_else_named():
    bar = {"kind": "bracket", "at": 12.0, "dur": 2.5, "tier": 1, "from": 10, "to": 16,
           "label": "-96 Mb", "color": "crimson", "form": "bar"}
    assert B.validate_species([bar], STILL, "ledger:two-reserves:tiers") == []
    errs = B.validate_species([{**bar, "form": "blob"}], STILL, "ledger:two-reserves:tiers")
    assert len(errs) == 1 and "form must be one of span|bar" in errs[0], errs


# ---- P50 T6: the census's X marks -------------------------------------------
import ledger_page as LPG  # noqa: E402

CENSUS_PARTS = [("United States", 16.8), ("Hong Kong", 8.5), ("Japan", 4.7), ("Korea", 4.5),
                ("Vietnam", 4.1), ("India", 3.4), ("Saudi Arabia", 1.2), ("Rest of world", 58.8)]


def _census_world() -> dict:
    series = {"title": "China's exports, by partner", "src": "our reading", "unit": "%", "total": 100,
              "shares": [{"label": a, "value": b} for a, b in CENSUS_PARTS]}
    return {"kind": "ledger", "page": LPG.build_spec(series, "treemap", None, "right"),
            "ken_burns": {"scale": 0, "x": 0, "y": 0}}


def _cross(**extra) -> dict:
    return {"kind": "cross", "at": 9.0, "dur": 3.0, "cells": ["United States", "Japan"],
            "text": "2 partners, 22 % of exports", **extra}


def test_a_good_cross_passes_and_the_page_knows_its_cells(tmp_path):
    world, sp = _census_world(), _cross()
    assert B.validate_species([sp], STILL, "ledger:exports:treemap") == []
    B.derive_rescale_states(world, [sp], "ledger:exports:treemap", tmp_path)   # no exception: the cells are the page's own
    # ... and the shrink afterwards is P48's park: one affine transform on the standing chart, nothing new
    park = {"kind": "chart_to", "at": 13.0, "dur": 1.2, "to": "park", "scale": 0.72, "anchor": "top"}
    assert B.validate_species([sp, park], STILL, "ledger:exports:treemap") == []
    B.derive_rescale_states(world, [sp, park], "ledger:exports:treemap", tmp_path)
    assert not world.get("page_states"), "a park derives no state - it moves the chart that stands (E58)"


def test_a_cross_naming_a_cell_the_page_does_not_carry_is_refused_by_name(tmp_path):
    world = _census_world()
    with pytest.raises(ValueError) as exc:
        B.derive_rescale_states(world, [_cross(cells=["United States", "Atlantis"])], "ledger:exports:treemap", tmp_path)
    assert "no cell named 'Atlantis'" in str(exc.value) and "its parts are" in str(exc.value), exc.value


def test_a_cross_on_a_cell_the_page_could_not_LABEL_is_refused_by_the_census_bound(tmp_path):
    """E53 s1's census exception (c): no unlabelled cell is ever the argument. 'Saudi Arabia' is 1.2 %
    of the whole and its name is long - the floors cull its label, so it may not be crossed."""
    world = _census_world()
    with pytest.raises(ValueError) as exc:
        B.derive_rescale_states(world, [_cross(cells=["Saudi Arabia"])], "ledger:exports:treemap", tmp_path)
    assert "could not fit a label" in str(exc.value) and "census exception (c)" in str(exc.value), exc.value


def test_a_cross_off_a_treemap_page_is_refused(tmp_path):
    errs = B.validate_species([_cross()], STILL, PLATE)
    assert any("page species" in e for e in errs), errs   # a plate carries no page species at all
    with pytest.raises(ValueError) as exc:
        B.derive_rescale_states({"kind": "ledger", "page": {"builder": "story", "labels": []}}, [_cross()], "ledger:x:bars", tmp_path)
    assert "land on a TREEMAP page" in str(exc.value), exc.value


def test_a_cross_without_its_written_share_is_refused_by_the_other_half_of_the_bound():
    errs = B.validate_species([{"kind": "cross", "at": 9.0, "dur": 3.0, "cells": ["Japan"]}], STILL, "ledger:exports:treemap")
    assert len(errs) == 1 and "census exception (b)" in errs[0], errs
    errs = B.validate_species([_cross(text="the partners that left")], STILL, "ledger:exports:treemap")
    assert len(errs) == 1 and "carries no number" in errs[0], errs
    errs = B.validate_species([_cross(cells=[])], STILL, "ledger:exports:treemap")
    assert len(errs) == 1 and "'cells' must be a non-empty list" in errs[0], errs


# ---- HF-17 (P50 T15): one foreground occluder on a world plate ------------------------------------------------------
# "Occlusion beats blur as the depth cue" (the intake, against doc 29's open focus-rack proposal). A dock declares
# `behind: "<layer>"`; the plate declares its fronts beside itself in `<plate>.layers.json`. The compiler's whole job
# is that the layer EXISTS - the two ways this fails silently are a name the plate does not carry and a file that is
# not on disk, and both end as a card that simply never got occluded and a frame nobody can explain.
import json as _json  # noqa: E402


def _plate_with_layers(tmp_path, layers: dict, write_files=True):
    plate = tmp_path / "plate-desk.png"
    plate.write_bytes(b"\x89PNG\r\n\x1a\n")
    (tmp_path / "plate-desk.layers.json").write_text(_json.dumps({"foreground": layers}), encoding="utf-8")
    if write_files:
        for name in layers.values():
            (tmp_path / name).write_bytes(b"\x89PNG\r\n\x1a\n")
    return plate


def test_behind_is_a_dock_option_and_the_plate_declares_its_fronts(tmp_path):
    assert "behind" in B.DOCK_OPTS
    assert B.dock_opts({"behind": "desk"}) == {"behind": "desk"}
    for bad in ("", "  ", 3, True, None):
        with pytest.raises(ValueError) as e:
            B.dock_opts({"behind": bad})
        assert "foreground layer" in str(e.value)
    plate = _plate_with_layers(tmp_path, {"desk": "plate-desk.front.png", "lamp": "plate-desk.lamp.png"})
    got = B.plate_layers(plate)
    assert sorted(got) == ["desk", "lamp"] and got["desk"].name == "plate-desk.front.png"
    assert B.plate_layers(tmp_path / "nothing.png") == {}, "a plate is not required to have a front"
    (tmp_path / "plate-desk.layers.json").write_text("not json", encoding="utf-8")
    assert B.plate_layers(plate) == {}, "a malformed sidecar is no layers, never a crash"


def test_the_compiler_refuses_a_layer_the_plate_does_not_have(tmp_path):
    plate = _plate_with_layers(tmp_path, {"desk": "plate-desk.front.png"})
    layers = B.plate_layers(plate)
    world = {"asset_id": "plate-desk", "sha256": "0" * 64}
    assert B.behind_error(world, layers, "desk", "row 3 dock ev-x") is None
    miss = B.behind_error(world, layers, "lamp", "row 3 dock ev-x")
    assert miss and "is not a foreground layer of 'plate-desk'" in miss and "it declares desk" in miss
    gone = _plate_with_layers(tmp_path, {"ghost": "plate-desk.ghost.png"}, write_files=False)
    off = B.behind_error(world, B.plate_layers(gone), "ghost", "row 3 dock ev-x")
    assert off and "which is not on disk" in off
    for kind in ({"kind": B.SPECIES_LEDGER, "page": {}}, {"kind": B.VECMAP_KIND}, {"kind": B.SPECIES_CLIP, "asset_id": "clip"}):
        drawn = B.behind_error(kind, layers, "desk", "row 3 dock ev-x")
        assert drawn and "no front to hide a card behind" in drawn, kind


def test_a_dock_entry_carries_behind_and_its_layer_key_only_when_the_row_asks():
    d = B.dock_entry("ev-x", 0, 4.0, 20.0, 0, B.DOCK_KIND_IMAGE, {"x": 1, "y": 2, "w": 3, "h": 4},
                     behind="desk", fg=f"{B.FG_PREFIX}plate-desk:desk")
    assert d["behind"] == "desk" and d["fg"] == "fg:plate-desk:desk"
    plain = B.dock_entry("ev-x", 0, 4.0, 20.0, 0)
    assert "behind" not in plain and "fg" not in plain, "a build that never asks is byte-for-byte what it was"


def test_the_golden_docks_one_card_behind_the_plates_own_front():
    """The `occluder-dock` source, as committed: the layer rides the asset map under the key the compiler writes, the
    dock names it, and the PNG carries an alpha channel - colour type 6 - because the whole layer is its alpha."""
    import base64
    sources = ROOT / "content/video_engine/tests/golden/sources"
    tl = _json.loads((sources / "occluder-dock.timeline.json").read_text(encoding="utf-8"))
    uris = _json.loads((sources / "occluder-dock.uris.json").read_text(encoding="utf-8"))
    dock = tl["scenes"][0]["docks"][0]
    assert dock["behind"] == "desk" and dock["fg"] == f"{B.FG_PREFIX}plate-plain:desk"
    assert dock["fg"] in uris and uris[dock["fg"]].startswith("data:image/png;base64,")
    png = base64.b64decode(uris[dock["fg"]].split(",", 1)[1])
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and png[25] == 6, "the foreground layer must be RGBA - its alpha IS the cutout"


# ---- P52 T6: THE NEWSREEL BAND -----------------------------------------------------------------
NEWSREEL_HEADS = ["Treasury Secretary Bessent Boosts Buybacks of Long-Dated Debt",
                  "US Treasury to Buy Up to $6 Billion in Long-Dated Debt",
                  "Kevin Warsh: A new regime is needed at the Fed"]
NEWSREEL_BAND = {"kind": "region", "x0": 0.0, "y0": 0.78, "x1": 1.0, "y1": 0.92}


def _reel(**kw):
    e = {"kind": "newsreel", "at": 42.0, "dur": 9.0, "headlines": list(NEWSREEL_HEADS),
         "strap": "the wire, this week", "dateline": "SEPT 2026", "target": dict(NEWSREEL_BAND)}
    e.update(kw)
    return e


def test_the_newsreel_kind_validates_with_its_sourced_headlines_and_a_low_region():
    """The kind is declared, it takes a REGION and nothing else, and it carries a `when` like every other."""
    assert B.SPECIES_NEWSREEL in B.SPECIES_KINDS and B.SPECIES_TARGETS[B.SPECIES_NEWSREEL] == ("region",)
    assert B.SPECIES_WHEN[B.SPECIES_NEWSREEL].startswith("the sentence reports")
    assert B.SPECIES_NEWSREEL not in B.PAGE_SPECIES, "the band is a STAGE species - it does not perform on the page"
    assert B.validate_species([_reel()], STILL, PLATE) == []
    assert B.validate_species([_reel(hold=6.0, speed_px_s=120)], STILL, PLATE) == []
    assert B.validate_species([_reel(strap=None, dateline=None)], STILL, PLATE) == [], "the strap and the dateline are optional"
    for bad_target in (POINT, DATUM, SPAN):
        errs = B.validate_species([_reel(target=bad_target)], STILL, PLATE)
        assert errs and "not allowed" in errs[0], (bad_target, errs)
    assert B.validate_species([{"kind": "newsreel", "at": 1.0, "dur": 2.0, "headlines": NEWSREEL_HEADS[:1]}], STILL, PLATE), \
        "a band with no declared region does not fire (s9.27)"


def test_a_headline_the_author_did_not_source_or_cannot_read_is_refused():
    """`headlines` is the crawl and it is the episode's own SOURCED titles: non-empty, and short enough to read."""
    errs = B.validate_species([_reel(headlines=[])], STILL, PLATE)
    assert len(errs) == 1 and "non-empty list" in errs[0] and "never invented" in errs[0], errs
    errs = B.validate_species([_reel(headlines=["a real headline", "  "])], STILL, PLATE)
    assert len(errs) == 1 and "headline 1" in errs[0] and "non-empty string" in errs[0], errs
    errs = B.validate_species([_reel(headlines=["x" * (B.NEWSREEL_HEADLINE_MAX + 1)])], STILL, PLATE)
    assert len(errs) == 1 and str(B.NEWSREEL_HEADLINE_MAX) in errs[0], errs
    assert B.validate_species([_reel(headlines=["x" * B.NEWSREEL_HEADLINE_MAX])], STILL, PLATE) == []
    errs = B.validate_species([_reel(dateline=42)], STILL, PLATE)
    assert len(errs) == 1 and "no clock is invented" in errs[0], errs
    errs = B.validate_species([_reel(hold=8.9)], STILL, PLATE)   # 8.9 + the 0.38 retreat > dur 9.0
    assert len(errs) == 1 and "mid-retreat" in errs[0], errs
    for bad in (0, -4, True, "fast"):
        assert B.validate_species([_reel(speed_px_s=bad)], STILL, PLATE), bad


def test_the_bands_region_must_sit_low_and_its_box_is_the_strip_the_placer_reserves():
    """A band is a STRIP in the lower 40 % - above that it is the composition, which is the surface's job."""
    errs = B.validate_species([_reel(target={"kind": "region", "x0": 0.0, "y0": 0.3, "x1": 1.0, "y1": 0.44})], STILL, PLATE)
    assert len(errs) == 1 and "lower 40 %" in errs[0] and str(B.NEWSREEL_LOW) in errs[0], errs
    assert B.validate_species([_reel(target={"kind": "region", "x0": 0.0, "y0": B.NEWSREEL_LOW, "x1": 1.0, "y1": 0.74})],
                              STILL, PLATE) == [], "exactly at the line is low enough"
    assert B.newsreel_region_box(_reel(), "9:16") == {"x": 0, "y": 1498, "w": 1080, "h": 269}
    assert B.newsreel_boxes([_reel(), _sp("punch", target=POINT)], "16:9") == [{"x": 0, "y": 842, "w": 1920, "h": 151}]
    assert B.newsreel_boxes([], "16:9") == [] and B.newsreel_boxes(None, "16:9") == []
    # the placer reserves it exactly the way the anchored caption's strip is reserved: it clips the foot
    boxes = {"safe": {"x": 80, "y": 80, "w": 1760, "h": 920}, "plot": {"x": 200, "y": 200, "w": 1400, "h": 400},
             "source": {"x": 200, "y": 620, "w": 400, "h": 30}, "rail": {"x": 0, "y": 0, "w": 0, "h": 0},
             "caption_anchor": {"x": 145, "y": 878, "w": 1630, "h": 82}}
    band = B.newsreel_boxes([_reel()], "16:9")
    plain = {b["band"]: b for b in B.free_bands(boxes)}
    kept = {b["band"]: b for b in B.free_bands(boxes, band)}
    assert plain["foot"]["h"] > kept["foot"]["h"], "the reserved strip cuts the foot the card would have parked in"
    assert kept["foot"]["y"] + kept["foot"]["h"] <= band[0]["y"], "no free band reaches into the crawl"
    assert plain["below"] == kept["below"], "a band above the strip is untouched - the page compiles as it did"


# ---- P52 T7 / T8: THE LAST THREE BRAVOS SPECIES ---------------------------------------------------------------------
# The count array (EXPLORATION-REVIEW-2026-09-10.md:59, the reference at 7:43), the numbered agenda (:58 #9) and the
# ring's DASHED-ELLIPSE form with its flag chip (:57 #5). The grammar here is the compiler's half: the painters are
# modules (species/countarray.mjs, species/agenda.mjs, species/ring.mjs) with their own node tests.

def _count(**o):
    e = {"kind": "count_array", "at": 5.0, "dur": 12.0, "count": 6, "icon": "factory", "claim": "SIX PLANTS",
         "target": {"kind": "region", "x0": 0.08, "y0": 0.47, "x1": 0.92, "y1": 0.97}}
    e.update(o)
    return e


def _agenda(**o):
    e = {"kind": "agenda", "at": 6.0, "dur": 10.0,
         "rows": [{"text": "A Treasury page"}, {"text": "Your phone"}],
         "target": {"kind": "region", "x0": 0.30, "y0": 0.50, "x1": 0.95, "y1": 0.95}}
    e.update(o)
    return e


def _ring(**o):
    e = {"kind": "ring", "at": 8.0, "dur": 6.0, "form": "dashed", "target": {"kind": "datum", "index": 191}}
    e.update(o)
    return e


def test_the_three_kinds_are_declared_with_a_when_and_the_targets_the_law_gives_them():
    for kind in (B.SPECIES_COUNT_ARRAY, B.SPECIES_AGENDA, B.SPECIES_RING):
        assert kind in B.SPECIES_KINDS and B.SPECIES_WHEN[kind], kind
    assert B.SPECIES_TARGETS[B.SPECIES_COUNT_ARRAY] == ("point", "region")
    assert B.SPECIES_TARGETS[B.SPECIES_AGENDA] == ("point", "region")
    assert B.SPECIES_TARGETS[B.SPECIES_RING] == ("datum", "point", "region")
    assert B.PHRASE_TARGET not in B.SPECIES_TARGETS[B.SPECIES_RING], "a phrase inside a press card is the callout's underline (P50 T3)"
    assert "span" not in B.SPECIES_TARGETS[B.SPECIES_RING], "a ring circles a number or a chart point - never a caption word span"
    for kind in (B.SPECIES_COUNT_ARRAY, B.SPECIES_AGENDA, B.SPECIES_RING):
        assert kind not in B.PAGE_SPECIES, f"{kind} is a STAGE species - it does not need a ledger page under it"


def test_a_well_formed_row_of_each_is_accepted_verbatim():
    for entry in (_count(), _agenda(), _ring(), _ring(flag="THE PEAK", flag_icon="landmark", flag_side="left", label="1,074")):
        assert B.validate_species([entry], STILL, PLATE) == [], entry["kind"]


# ---- T7: a count with no number in the sentence is refused ---------------------------------------------------------

def test_a_count_array_whose_claim_does_not_say_the_number_is_refused():
    errs = B.validate_species([_count(claim="THE PLANTS")], STILL, PLATE)
    assert len(errs) == 1 and "does not say 6" in errs[0] and "no number in the sentence is refused" in errs[0], errs
    assert B.validate_species([_count(claim="SIX PLANTS")], STILL, PLATE) == [], "the word IS the number"
    assert B.validate_species([_count(claim="6 PLANTS")], STILL, PLATE) == [], "... and so is the numeral"
    assert B.validate_species([_count(count=12, claim="TWELVE REFINERIES", dur=12.0)], STILL, PLATE) == []
    off = B.validate_species([_count(count=3, claim="30 PLANTS")], STILL, PLATE)
    assert len(off) == 1 and "does not say 3" in off[0], "30 is not three - the digits have to BE the count"


def test_a_count_outside_the_bound_or_with_no_sourced_glyph_is_refused():
    for n in (1, 13):
        errs = B.validate_species([_count(count=n, claim=f"{n} PLANTS")], STILL, PLATE)
        assert any("is outside 2-12" in e for e in errs), (n, errs)
    assert any("not an integer" in e or "must be an integer" in e for e in B.validate_species([_count(count="six")], STILL, PLATE))
    errs = B.validate_species([_count(icon="a-glyph-we-never-sourced")], STILL, PLATE)
    assert len(errs) == 1 and "assets/icons" in errs[0] and "never generate one" in errs[0], errs
    assert B.species_icons(_count()) == ["factory"], "the field's ONE glyph rides the asset map like the chip's"


def test_a_field_whose_last_icon_lands_after_its_window_is_refused():
    errs = B.validate_species([_count(dur=1.0)], STILL, PLATE)
    assert len(errs) == 1 and "the last icon would land after the field has gone" in errs[0], errs
    assert B.validate_species([_count(step=0.5, dur=3.0)], STILL, PLATE) == [], "5 * 0.5 + 0.45 fits in 3.0"
    assert any("'step' must be a positive number" in e for e in B.validate_species([_count(step=0)], STILL, PLATE))


# ---- T8: the agenda -------------------------------------------------------------------------------------------------

def test_an_agenda_is_two_to_four_rows_each_with_words_of_its_own():
    for rows in ([{"text": "only one"}], [{"text": str(i)} for i in range(5)]):
        errs = B.validate_species([_agenda(rows=rows)], STILL, PLATE)
        assert len(errs) == 1 and "must be a list of 2 to 4 rows" in errs[0], (len(rows), errs)
    errs = B.validate_species([_agenda(rows=[{"text": "a"}, {"text": "  "}])], STILL, PLATE)
    assert len(errs) == 1 and errs[0].startswith("agenda: row 2: 'text'"), errs
    assert B.validate_species([_agenda(rows=[{"text": "a", "n": 4, "sub": "the sellers"}, {"text": "b"}])], STILL, PLATE) == []
    assert any("'n' must be a positive integer" in e for e in B.validate_species([_agenda(rows=[{"text": "a", "n": 0}, {"text": "b"}])], STILL, PLATE))


def test_the_agenda_reveals_one_row_per_word_in_order_and_inside_its_window():
    assert B.validate_species([_agenda(rows=[{"text": "a", "at": 6.0}, {"text": "b", "at": 7.4}])], STILL, PLATE) == []
    back = B.validate_species([_agenda(rows=[{"text": "a", "at": 9.0}, {"text": "b", "at": 8.0}])], STILL, PLATE)
    assert len(back) == 1 and "one row per word, in order" in back[0], back
    early = B.validate_species([_agenda(rows=[{"text": "a", "at": 3.0}, {"text": "b", "at": 7.0}])], STILL, PLATE)
    assert any("before the agenda's own at" in e for e in early), early
    late = B.validate_species([_agenda(dur=2.0, rows=[{"text": "a"}, {"text": "b", "at": 7.9}])], STILL, PLATE)
    assert any("a row that cannot finish arriving is not revealed, it flashes" in e for e in late), late


# ---- T8: the ring's FORM widens; E56's USE does not -----------------------------------------------------------------

def test_the_ring_takes_the_dashed_form_and_only_that_form():
    assert B.RING_FORMS == ("dashed",)
    for bad in (None, "solid", "circle", "underline"):
        errs = B.validate_species([_ring(form=bad)], STILL, PLATE)
        assert any("'form' must be one of dashed" in e for e in errs), (bad, errs)
    assert "the hand's closed circle is a `callout`" in B.validate_species([_ring(form=None)], STILL, PLATE)[0]


def test_e56_is_re_stated_for_the_ring_word_for_word_and_never_widened():
    """The dashed form is a FORM. The USE is E56's, and the refusal is the callout's own, message included."""
    errs = B.validate_species([_ring(target=dict(POINT))], STILL, PLATE)
    assert len(errs) == 1 and "(E56)" in errs[0] and "use a spotlight (the light) on a picture" in errs[0], errs
    assert B.validate_species([_ring(target=dict(POINT), label="25%")], STILL, PLATE) == [], "a stamp whose label IS the number"
    assert B.validate_species([_ring(target=dict(REGION), label="+613%")], STILL, PLATE) == []
    region = B.validate_species([_ring(target=dict(REGION))], STILL, PLATE)
    assert len(region) == 1 and "(E56)" in region[0], region
    assert B.validate_species([_ring()], STILL, PLATE) == [], "a datum IS a point on a chart"
    # ... and the CALLOUT's own gate is untouched by all of it: the same row, refused with the same words
    callout = B.validate_species([_sp("callout", target=POINT)], STILL, PLATE)
    assert len(callout) == 1 and callout[0].startswith("callout: a ring circles") and "(E56)" in callout[0], callout
    assert B.validate_species([_sp("callout", target=DATUM)], STILL, PLATE) == []


def test_the_flag_chip_needs_a_sourced_glyph_and_a_side_it_understands():
    assert B.validate_species([_ring(flag="THE PEAK", flag_icon="landmark")], STILL, PLATE) == []
    errs = B.validate_species([_ring(flag="THE PEAK")], STILL, PLATE)
    assert len(errs) == 1 and "assets/icons" in errs[0], errs
    assert any("a glyph with no card" in e for e in B.validate_species([_ring(flag_icon="landmark")], STILL, PLATE))
    assert any("'flag_side' must be left or right" in e
               for e in B.validate_species([_ring(flag="THE PEAK", flag_icon="landmark", flag_side="above")], STILL, PLATE))
    assert B.species_icons(_ring(flag="THE PEAK", flag_icon="landmark")) == ["landmark"]
    assert B.species_icons(_ring()) == [], "no flag, no glyph in the asset map"


def test_the_three_goldens_carry_what_the_species_declare():
    """The committed sources are the proof the grammar and the painter agree - read back, not re-derived."""
    sources = ROOT / "content/video_engine/tests/golden/sources"
    field = json.loads((sources / "count-array.timeline.json").read_text(encoding="utf-8"))["scenes"][0]["species"][0]
    assert field["kind"] == "count_array" and field["count"] == 6 and "SIX" in field["claim"].upper()
    uris = json.loads((sources / "count-array.uris.json").read_text(encoding="utf-8"))
    assert (B.ICON_PREFIX + field["icon"]) in uris, "the sourced glyph travels in the asset map (A2a)"
    block = json.loads((sources / "agenda-two.timeline.json").read_text(encoding="utf-8"))["scenes"][0]["species"][0]
    assert block["kind"] == "agenda" and len(block["rows"]) == 2
    ring = json.loads((sources / "ring-dashed-chip.timeline.json").read_text(encoding="utf-8"))["scenes"][0]["species"][0]
    assert ring["kind"] == "ring" and ring["form"] == "dashed" and ring["target"]["kind"] == "datum"
    assert ring["flag"] and ring["label"], "the proof carries both halves of #5: the dashed ellipse and the flag chip"
    proof = json.loads((sources / "species-proof.timeline.json").read_text(encoding="utf-8"))
    assert [s["species"][0]["kind"] for s in proof["scenes"]] == ["ring", "count_array", "agenda"], "the three on one clock"
    for scene in proof["scenes"]:
        assert not B.validate_species(scene["species"], STILL,
                                      "ledger:golden-line:line" if scene["world"].get("kind") == "ledger" else PLATE)
