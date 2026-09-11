"""P51 T5 - THE OVERRIDE SIDECAR: a human's or a flash agent's edit is a sidecar of overrides keyed
by row id and field, layered over the shot table the AGENT authored (the grill, 2026-09-11).

The fixture is the Tokyo short's own authored table, loaded as rows - nothing here touches a build,
renders a frame or writes a file. Every test asks the one question the sidecar has to answer: does
layering an edit give exactly what editing the source row would have given, and is anything the
shot table would have refused refused here too, with the row and the field named?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
from authoring import table as T, words as KW  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
SHOT_TABLE = TOKYO / "SHOT-TABLE-SHORT.py"
RECORD_DOCK = "dock-k-pledge-record"
PLACE = {"x": 227, "y": 880, "w": 626, "h": 294}   # a parked card's box, as `dock_place` hands one down


# ------------------------------------------------------------------ the fixture: the real rows
@pytest.fixture(scope="module")
def rows() -> list[tuple]:
    return T.load_rows(SHOT_TABLE)


@pytest.fixture(scope="module")
def words() -> list[dict]:
    """The build's own `timeline.json` words - the clock every anchor in that table was read off."""
    p = TOKYO / "build-short/timeline.json"
    if not p.is_file():
        pytest.skip(f"{p} has not been built")
    return json.loads(p.read_text(encoding="utf-8"))["words"]


def scene_of(rows, pred) -> tuple[str, int]:
    """The scene id and the authored index of the first row `pred` holds for - the table is found by
    what it CONTAINS, never by a hand-typed row number."""
    ids = B.row_ids(rows)
    for sid, i in ids.items():
        if pred(rows[i]):
            return sid, i
    raise AssertionError("no such row in the Tokyo table")


def has_dock(slide):
    return lambda r: any(str(d[0]) == slide for d in (r[4] or []))


def edit_dock(rows, i, slide, patch) -> list[tuple]:
    """THE SOURCE EDIT the sidecar has to equal: the option dict typed into the row by hand."""
    out = [list(r) for r in rows]
    ds = [list(d) for d in out[i][4]]
    for d in ds:
        if str(d[0]) == slide:
            d[4] = {**(d[4] or {}), **patch}
    out[i][4] = [tuple(d) for d in ds]
    return [tuple(r) for r in out]


def dock_of(row, slide) -> tuple:
    return next(d for d in row[4] if str(d[0]) == slide)


def compiled_dock(row, sid: str, slide: str) -> dict:
    """The card COMPILED, the way `main` compiles it: the options through `dock_opts`, the centred
    box through `centred_place`, the entry through `dock_entry` with its derived row id."""
    aid, slot, enter, exitt, *extra = dock_of(row, slide)
    o = B.dock_opts(extra[0] if extra else None)
    place = B.centred_place(PLACE, "9:16", o.get("card_aspect"), None, o.get("centre_w"),
                            o.get("centre_band"), o.get("centre_y"), o.get("centre_x")) if o.get("centre") else PLACE
    return B.dock_entry(aid, slot, enter, exitt, 0, B.DOCK_KIND_IMAGE, place, o.get("arrive"), o.get("mass"),
                        bool(o.get("centre")), read_s=o.get("read_s"), park_s=o.get("park_s"),
                        rid=B.dock_row_id(sid, aid))


# ------------------------------------------------------------------ the ids are DERIVED, and stable
def test_the_scene_ids_follow_the_compilers_own_order_not_the_authored_one():
    # `main` sorts the table before it compiles, so `s01` is the EARLIEST row whatever order it was typed in
    table = [(9.0, 12.0, "plate-b", (0, 0, 0), [], None), (1.0, 9.0, "plate-a", (0, 0, 0), [], None)]
    assert B.row_ids(table) == {"s01": 1, "s02": 0}
    assert B.scene_row_id(0) == "s01" and B.scene_row_id(11) == "s12"


def test_two_rows_that_open_at_the_same_second_cannot_be_keyed_and_say_so():
    table = [(1.0, 4.0, "plate-a", (0, 0, 0), [], None), (1.0, 9.0, "plate-b", (0, 0, 0), [], None)]
    with pytest.raises(ValueError) as e:
        B.row_ids(table)
    assert "two shot rows open at 1.0s" in str(e.value)


def test_the_id_grammar_is_the_prop_path_from_the_start():
    assert B.dock_row_id("s04", RECORD_DOCK) == f"s04.dock.{RECORD_DOCK}"
    assert B.species_row_id("s04", 3) == "s04.species.3"
    assert B.camera_row_id("s02") == "s02.camera"


def test_a_compiled_dock_carries_its_row_id_and_one_without_is_unchanged():
    with_id = B.dock_entry("dock-x", 0, 1.0, 4.0, 0, rid="s03.dock.dock-x")
    assert with_id["id"] == "s03.dock.dock-x"
    assert {k: v for k, v in with_id.items() if k != "id"} == B.dock_entry("dock-x", 0, 1.0, 4.0, 0)


# ------------------------------------------------------------------ (a) a dock option
def test_an_overridden_centre_y_compiles_to_what_editing_the_row_would_have(rows):
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    layered = B.apply_overrides(rows, {f"{sid}.dock.{RECORD_DOCK}": {"centre_y": 0.32}})
    by_hand = edit_dock(rows, i, RECORD_DOCK, {"centre_y": 0.32})
    assert layered == by_hand, "the sidecar's rows ARE the hand-edited rows"
    assert compiled_dock(layered[i], sid, RECORD_DOCK) == compiled_dock(by_hand[i], sid, RECORD_DOCK)
    moved = compiled_dock(layered[i], sid, RECORD_DOCK)
    assert moved != compiled_dock(rows[i], sid, RECORD_DOCK), "and the card actually moved"
    assert moved["id"] == f"{sid}.dock.{RECORD_DOCK}"


def test_null_puts_a_dock_option_back_to_the_compilers_default(rows):
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    layered = B.apply_overrides(rows, {f"{sid}.dock.{RECORD_DOCK}": {"park_s": None}})
    assert "park_s" in dock_of(rows[i], RECORD_DOCK)[4] and "park_s" not in dock_of(layered[i], RECORD_DOCK)[4]
    assert compiled_dock(layered[i], sid, RECORD_DOCK)["park_s"] == B.DOCK_PARK_S


# ------------------------------------------------------------------ (b) a species' `at`, by word
def test_a_species_at_named_by_its_word_resolves_to_the_builds_own_second(rows, words):
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    ws = [{"w": w["w"], "start_s": w["start"], "end_s": w["end"]} for w in words]
    layered = B.apply_overrides(rows, {f"{sid}.species.3": {"at": {"word": "pledged"}}}, words=words)
    assert layered[i][6][3]["at"] == KW.at(ws, "pledged"), "the sidecar reads the take through the kit's own `at`"
    assert layered == B.apply_overrides(rows, {f"{sid}.species.3": {"at": KW.at(ws, "pledged")}}), \
        "... so the word form and the number form are the same edit"


def test_the_word_form_without_the_builds_words_refuses_rather_than_guesses(rows):
    sid, _ = scene_of(rows, has_dock(RECORD_DOCK))
    with pytest.raises(ValueError) as e:
        B.apply_overrides(rows, {f"{sid}.species.3": {"at": {"word": "pledged"}}})
    assert "needs the build's words" in str(e.value) and f"{sid}.species.3" in str(e.value)


# ------------------------------------------------------------------ (c) the camera
def test_turning_a_camera_off_gives_the_rows_the_camera_off_build_authors(rows):
    """`TOKYO_CAMERA=0` sets the row's 8th element to None and nothing else on that row - so a
    `null` camera in the sidecar has to land on exactly those rows, and on nothing else."""
    cam_rows = {sid: i for sid, i in B.row_ids(rows).items() if len(rows[i]) > 7 and rows[i][7] is not None}
    assert cam_rows, "the fixture table is the camera cut"
    layered = B.apply_overrides(rows, {B.camera_row_id(sid): None for sid in cam_rows})
    by_hand = [(r[:7] + (None,)) if len(r) > 7 else r for r in rows]
    assert layered == by_hand
    # the boundary: the ring row's `:camera=`/`:snap=` arrival is part of the BARE plate id, an authored
    # branch the sidecar does not reach - a different world is a different row, not an edit
    assert [r[2] for r in layered] == [r[2] for r in rows]


def test_a_camera_that_fights_the_rows_species_is_refused_by_the_same_law():
    """s9.28 C3: authored keys and a camera species cannot both drive one window. The sidecar runs
    `validate_camera_row` against the row it is landing on, so it refuses what the table refuses."""
    punch = {"kind": "punch", "at": 2.0, "dur": 1.0, "target": {"kind": "point", "x": 0.5, "y": 0.5}}
    table = [(1.0, 9.0, "plate-a", (0, 0, 0), [], None, [punch])]
    with pytest.raises(ValueError) as e:
        B.apply_overrides(table, {"s01.camera": {"keys": [{"t": 2.0, "zoom": 1.2}], "attention": "locked"}})
    assert "s01.camera" in str(e.value) and "one camera per window" in str(e.value)
    assert B.apply_overrides(table, {"s01.camera": None})[0][7] is None, "... and turning it off is fine"


# ------------------------------------------------------------------ the plate options and the exit
def test_a_plate_option_is_layered_through_the_plate_ids_own_grammar(rows):
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    layered = B.apply_overrides(rows, {f"{sid}.plate": {"idle": "drift"}})
    assert B.split_plate_opts(layered[i][2])[1]["idle"] == "drift"
    assert B.split_plate_opts(layered[i][2])[0] == B.split_plate_opts(rows[i][2])[0], "the bare plate id is untouched"
    assert B.apply_overrides(layered, {f"{sid}.plate": {"idle": "drift"}}) == layered, "and re-laying it changes nothing"


def test_an_exit_override_is_the_authored_sixth_element(rows):
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    layered = B.apply_overrides(rows, {f"{sid}.exit": "dip"})
    assert layered[i][5] == "dip"
    assert B.scene_exit(layered[i][5], True) == B.parse_exit("dip")


# ------------------------------------------------------------------ (d) the refusals, by name
@pytest.mark.parametrize("sidecar, needles", [
    ({"s99.camera": None}, ["'s99.camera'", "names no row", "s01.."]),
    ({"s02": {}}, ["'s02'", "names a scene but no field"]),
    ({"s02.wobble": 1}, ["'s02.wobble'", "'wobble' is not a field of a row"]),
    ({"s02.dock.dock-nope": {"centre_y": 0.3}}, ["s02.dock.dock-nope", "no dock 'dock-nope' on this row"]),
    ({"s02.dock.dock-c-blue-ties-panel": {"wobble": 1}}, ["s02.dock.dock-c-blue-ties-panel", "field 'wobble' is not one of"]),
    ({"s02.dock.dock-c-blue-ties-panel": {"centre_y": 4}}, ["s02.dock.dock-c-blue-ties-panel", "field 'centre_y'", "share of the stage"]),
    ({"s02.species.99": {"dur": 1}}, ["s02.species.99", "no species 99 on this row"]),
    ({"s02.species.nope": {"dur": 1}}, ["s02.species.nope", "keyed by its INDEX"]),
    ({"s02.species.0": {"kind": "note"}}, ["s02.species.0", "field 'kind' is AUTHORING"]),
    ({"s02.species.0": {"wobble": 1}}, ["s02.species.0", "field 'wobble' is not one of"]),
    ({"s02.species.0": {"dur": 0}}, ["s02.species.0", "field 'dur'", "does not fire"]),
    ({"s02.plate": {"idle": "wobble"}}, ["s02.plate", "field 'idle'", "is not one of"]),
    ({"s02.plate": {"wobble": "x"}}, ["s02.plate", "field 'wobble' is not one of"]),
    ({"s02.plate": "plate-something-else"}, ["s02.plate", "a plate override is a dict of"]),
    ({"s02.exit": "vanish"}, ["s02.exit", "field 'exit'", "is not one of cut|dip"]),
    ({"s02.camera": 7}, ["s02.camera", "field 'camera'", "null (the camera off) or a dict"]),
    ({"s02.camera": {"keys": [{"t": 1.0, "zoom": 0}]}}, ["s02.camera", "field 'camera'", "zoom must be a number > 0"]),
])
def test_an_unknown_id_an_unknown_field_and_a_bad_value_are_each_refused_by_name(rows, sidecar, needles):
    with pytest.raises(ValueError) as e:
        B.apply_overrides(rows, sidecar)
    for needle in needles:
        assert needle in str(e.value), f"{needle!r} missing from {str(e.value)!r}"


def test_a_sidecar_that_is_not_an_object_is_refused(rows):
    with pytest.raises(ValueError) as e:
        B.apply_overrides(rows, [{"s02.exit": "dip"}])
    assert "keyed by row id and field" in str(e.value)


# ------------------------------------------------------------------ (e) and (f): pure, idempotent
def test_the_layering_is_idempotent(rows, words):
    sid, _ = scene_of(rows, has_dock(RECORD_DOCK))
    sidecar = {f"{sid}.dock.{RECORD_DOCK}": {"centre_y": 0.32},
               f"{sid}.species.3": {"at": {"word": "pledged"}},
               f"{sid}.plate": {"idle": "drift"},
               f"{sid}.exit": "dip",
               "s02.camera": None}
    once = B.apply_overrides(rows, sidecar, words=words)
    assert B.apply_overrides(once, sidecar, words=words) == once
    assert B.apply_overrides(rows, dict(reversed(list(sidecar.items()))), words=words) == once, \
        "and the key order in the file is not part of the edit"


def test_with_no_sidecar_the_rows_come_back_untouched(rows):
    for empty in ({}, None):
        out = B.apply_overrides(rows, empty)
        assert len(out) == len(rows) and all(a is b for a, b in zip(out, rows)), "identity, not a rebuild"


def test_the_authored_rows_are_never_mutated(rows, words):
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    before = repr(rows)
    B.apply_overrides(rows, {f"{sid}.dock.{RECORD_DOCK}": {"centre_y": 0.32},
                             f"{sid}.species.3": {"at": {"word": "pledged"}}}, words=words)
    assert repr(rows) == before, "the sidecar layers over the table; it does not edit it"


# ------------------------------------------------------------------ the kit's door
def test_the_kit_does_nothing_at_all_when_there_is_no_sidecar(tmp_path):
    assert T.apply_sidecar(TOKYO, tmp_path, "SHOT-TABLE-SHORT.py") == []


def test_the_kit_writes_the_effective_rows_into_the_literal(tmp_path):
    """The literal is what the compiler reads, so it has to show what was compiled - the sidecar
    lands BEFORE the table is handed over, not after."""
    ep, build = tmp_path / "ep", tmp_path / "build"
    ep.mkdir(); build.mkdir()
    rows = T.load_rows(SHOT_TABLE)
    T.write_shot_table(ep / "SHOT-TABLE-SHORT.py", rows, '"""a copy of the Tokyo table."""\n')
    sid, i = scene_of(rows, has_dock(RECORD_DOCK))
    (build / T.OVERRIDES_NAME).write_text(json.dumps({f"{sid}.dock.{RECORD_DOCK}": {"centre_y": 0.32}}), encoding="utf-8")
    assert T.apply_sidecar(ep, build, "SHOT-TABLE-SHORT.py") == [f"{sid}.dock.{RECORD_DOCK}"]
    effective = T.load_rows(ep / "SHOT-TABLE-SHORT.py")
    assert dock_of(effective[i], RECORD_DOCK)[4]["centre_y"] == 0.32
    assert effective == edit_dock(rows, i, RECORD_DOCK, {"centre_y": 0.32})
    assert (ep / "SHOT-TABLE-SHORT.py").read_text(encoding="utf-8").startswith('"""a copy of the Tokyo table."""\n')


def test_a_bad_sidecar_stops_the_build_naming_the_file_the_row_and_the_field(tmp_path):
    ep, build = tmp_path / "ep", tmp_path / "build"
    ep.mkdir(); build.mkdir()
    T.write_shot_table(ep / "SHOT-TABLE-SHORT.py", T.load_rows(SHOT_TABLE), '"""a copy."""\n')
    (build / T.OVERRIDES_NAME).write_text(json.dumps({"s02.dock.dock-c-blue-ties-panel": {"centre_y": 4}}), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        T.apply_sidecar(ep, build, "SHOT-TABLE-SHORT.py")
    assert "overrides.json" in str(e.value) and "s02.dock.dock-c-blue-ties-panel" in str(e.value) and "centre_y" in str(e.value)
