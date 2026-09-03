"""P35 T7 - the targeting law as code (doc 29 s9.27 MOTION MENU, s9.28 C3/C4):
`build_scene_timeline_f.validate_species` rejects a pointing species with no
declared target, two camera moves on one row, a camera move over Ken Burns,
and any species firing inside the pivot's reversal; a well-formed list is
accepted and emitted verbatim. Pure function - no episode build needed."""
from __future__ import annotations

import sys
from pathlib import Path

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
