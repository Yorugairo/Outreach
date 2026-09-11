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
