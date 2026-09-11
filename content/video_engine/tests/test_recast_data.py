"""R26-49 / E64 - THE DERIVED KEY, and the third key: the DATA.

The operator on Tokyo at 0:50 (2026-09-11): *"i think the chart needs to either re-write/re-draw itself or morph.
right now it basically just cuts a new chart"*. The line that cut was a `chart_to recast` with no `keyed` on a pair
that shares its data: `ev-japan-holdings-v1`'s last four months ARE `ev-japan-selling-v1`'s four change bars. So the
compiler stops waiting to be asked - it derives the key it can see (by series, by tags, by DATA), writes the
correspondence onto the species as a `key_map` so the engine never re-derives it, and names in the compile every
recast it could not key, which is the hand-over the author owns.

This file is the COMPILER half. Nothing here renders, seeks a player or writes a file: every test asks whether the
key the compiler derives is the one the two evidence objects' own numbers say, and whether the refusals name the row
and the reason. The figures are never fabricated - the key map is checked against both series.json files, not against
a number typed here.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
from authoring import table as T  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
SHOT_TABLE = TOKYO / "SHOT-TABLE-SHORT.py"
HOLDINGS = TOKYO / "evidence/objects/ev-japan-holdings-v1.series.json"
SELLING = TOKYO / "evidence/objects/ev-japan-selling-v1.series.json"
TARIFF_TABLE = ROOT / "content/video_engine/projects/systems-and-blowups/japan-tariff-trick/SHOT-TABLE-SHORT.py"
SHIPPED = TOKYO / "build-short/tokyo-short.timeline.json"
NEW_FIELDS = ("keyed", "keyed_derived", "key_map")
DERIVED_AT = 50.3   # "The Treasury prints the new total monthly" - the instant the operator read as a cut
PLAIN_AT = 56.72    # "to chips," - the holdings line against a bonds-vs-chips page: two charts that share nothing

needs_objects = pytest.mark.skipif(not (HOLDINGS.exists() and SELLING.exists()),
                                   reason="the Tokyo evidence objects are not on disk")


# ---- the fixtures: the real row, and the two evidence objects behind it -------------------------------


@pytest.fixture(scope="module")
def rows() -> list[tuple]:
    return T.load_rows(SHOT_TABLE)


def recast_row(rows) -> tuple[str, tuple]:
    """The scene id and row of the FIRST row carrying a plain `chart_to recast` - found by what the table
    contains, never by a hand-typed row number."""
    ids = B.row_ids(rows)
    for sid, i in ids.items():
        sp = rows[i][6] if len(rows[i]) > 6 and rows[i][6] else []
        if any(isinstance(e, dict) and e.get("kind") == "chart_to" and e.get("to") == "recast" for e in sp):
            return sid, rows[i]
    raise AssertionError("no recast row in the Tokyo table")


def compiled(row, sid: str, patch: dict | None = None) -> tuple[dict, list]:
    """The row's world and species as `main` compiles them: the page and its `then=` states off the plate id,
    then `derive_rescale_states` - which is where the key is derived."""
    species = [dict(e) for e in (row[6] or [])]
    if patch:
        for e in species:
            if e.get("kind") == "chart_to" and e.get("to") == "recast" and e.get("at") == patch["at"]:
                e.update(patch["set"])
    world = B.world_for_plate(row[2], (0, 0, 0), TOKYO, {})
    B.derive_rescale_states(world, species, row[2], TOKYO, sid=sid)
    return world, species


def recasts(species: list) -> list[dict]:
    return [e for e in species if e.get("kind") == "chart_to" and e.get("to") == "recast"]


# ---- the grammar: a rule, not a list of builder pairs -------------------------------------------------


def test_the_data_key_is_a_third_key_and_a_rule_rather_than_a_pair_list():
    """`keyed` gains "data" beside the two MARK keys. It cannot be a pair list: Tokyo's pair is (dense-line,
    story) - the very builders the series key uses - so only the two states' DATA can tell the two forms apart."""
    assert B.RECAST_DATA_KEY == "data"
    assert B.RECAST_KEYS_ALL == (True, "tags", "data"), "the two mark keys (P50 T11) and the data key (E64)"
    assert B.RECAST_PAIRS == B.RECAST_TAG_PAIRS == (("dense-line", "story"),), "the mark keys are still pair-gated"
    assert B.RECAST_DATA_TOL == 0.005, "0.5 % of the larger magnitude - a near-miss is a refusal, not a tween"
    assert not B._validate_page_fields("chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast", "state": 1, "keyed": "data"})
    assert any("keyed must be true" in e for e in B._validate_page_fields(
        "chart_to", {"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast", "state": 1, "keyed": "changes"}))


# ---- the rule itself, on specs built here so the tolerance is measured, not trusted --------------------


def _pair(values, labels=("Feb", "Mar"), pts=(("2026.0", "100.0"), ("2026.0833", "110.0"), ("2026.1667", "105.0"))):
    """A one-line page and a bars page of its own consecutive changes: +10.0 into Feb, -5.0 into Mar."""
    return ({"builder": "dense-line", "series": [{"name": "A", "pts": [list(p) for p in pts]}]},
            {"builder": "story", "labels": list(labels), "values": list(values)})


def test_the_bars_are_the_lines_own_changes_or_the_pair_is_not_keyed_on_data():
    key_map, why = B.recast_data_key(*_pair([10.0, -5.0]))
    assert why == "" and key_map == [{"datum": 1, "bar": 0, "from": 0}, {"datum": 2, "bar": 1, "from": 1}]
    near, _ = B.recast_data_key(*_pair([10.04, -5.0]))
    assert near, "0.4 % of the larger is the same number rounded"
    off, why = B.recast_data_key(*_pair([10.06, -5.0]))
    assert off is None and "bar 0 (Feb) is 10.06 and the line's own change into datum 1 is 10" in why, why


def test_the_bars_categories_must_be_the_lines_own_months():
    off, why = B.recast_data_key(*_pair([10.0, -5.0], labels=("Jan", "Mar")))
    assert off is None and "bar 0 is labelled 'Jan' and datum 1 is Feb" in why, why
    gap = ({"builder": "dense-line", "series": [{"pts": [["2000.0", "1.0"], ["2020.0", "2.0"], ["2020.0833", "3.0"]]}]},
           {"builder": "story", "labels": ["a", "b"], "values": [1.0, 1.0]})
    off, why = B.recast_data_key(*gap)
    assert off is None and "consecutive periods" in why, why


def test_a_page_that_draws_more_than_one_line_has_no_data_key():
    A, Bs = _pair([10.0, -5.0])
    A["series"] = A["series"] + [dict(A["series"][0])]
    off, why = B.recast_data_key(A, Bs)
    assert off is None and "ONE line's own data and this page draws 2 series" in why, why


def test_a_line_too_short_for_its_bars_is_named_not_guessed():
    A, Bs = _pair([1.0, 2.0, 3.0], labels=("Jan", "Feb", "Mar"))
    off, why = B.recast_data_key(A, Bs)
    assert off is None and "3 bar(s) need the line's last 4 data and it carries 3" in why, why


# ---- Tokyo 0:50: the key the compiler derives, and the map it writes -----------------------------------


@needs_objects
def test_the_tokyo_recast_derives_the_data_key_and_names_it_in_the_compile(rows, capsys):
    sid, row = recast_row(rows)
    _world, species = compiled(row, sid)
    first = next(e for e in recasts(species) if e["at"] == DERIVED_AT)
    assert first["keyed"] == "data" and first["keyed_derived"] is True, "no author asked - the data did"
    assert first["key_map"] == [{"datum": 312, "bar": 0, "from": 311}, {"datum": 313, "bar": 1, "from": 312},
                                {"datum": 314, "bar": 2, "from": 313}, {"datum": 315, "bar": 3, "from": 314}], \
        "the datum that travels, the bar it becomes, the datum it is measured from"
    out = capsys.readouterr().out
    assert f'{sid} chart_to recast at {DERIVED_AT}: keyed "data" (derived - E64)' in out, out


@needs_objects
def test_the_key_map_is_the_two_evidence_objects_own_numbers(rows):
    """The map is checked against the SPECS, both of them: each bar is the holdings line's own month-on-month
    change, and each keyed datum is the month the bar is labelled with. Feb -> Jun 2026, TIC Table 5."""
    sid, row = recast_row(rows)
    world, species = compiled(row, sid)
    first = next(e for e in recasts(species) if e["at"] == DERIVED_AT)
    bars = ([world["page"]] + world["page_states"])[first["state"]]
    pts = world["page"]["series"][0]["pts"]
    raw_line = json.loads(HOLDINGS.read_text(encoding="utf-8"))["series"][0]["pts"]
    raw_bars = json.loads(SELLING.read_text(encoding="utf-8"))["bars"]
    assert [b["label"] for b in raw_bars] == ["Mar", "Apr", "May", "Jun"]
    for m in first["key_map"]:
        v = float(bars["values"][m["bar"]])
        change = round(float(pts[m["datum"]][1]) - float(pts[m["from"]][1]), 4)
        assert abs(v - change) <= B.RECAST_DATA_TOL * max(abs(v), abs(change)), (m, v, change)
        assert v == raw_bars[m["bar"]]["value"], "the bar the page draws is the bar the series.json carries"
        assert round(float(raw_line[m["datum"]][1]) - float(raw_line[m["from"]][1]), 4) == change, \
            "and the change is the raw series' own, not the rounded page's"
        assert B.month_of_x(pts[m["datum"]][0]) == bars["labels"][m["bar"]]
    assert [float(bars["values"][m["bar"]]) for m in first["key_map"]] == [-47.7, 18.3, -66.8, -26.4], \
        "TIC Table 5, Mar-Jun 2026 ($bn): the four prints the bars are"


@needs_objects
def test_a_recast_the_compiler_cannot_key_is_named_and_left_plain(rows, capsys):
    """The second recast at 0:56 puts the holdings line against a bonds-vs-chips page: two charts that share
    nothing. E64's compiler half does not refuse it - it names it, and the entry carries keyed: null."""
    sid, row = recast_row(rows)
    _world, species = compiled(row, sid)
    second = next(e for e in recasts(species) if e["at"] == PLAIN_AT)
    assert second["keyed"] is None and "key_map" not in second and "keyed_derived" not in second
    out = capsys.readouterr().out
    assert f"{sid} chart_to recast at {PLAIN_AT}: no key - the plain recast (E64: a hand-over to name)" in out, out


@needs_objects
def test_an_explicit_data_key_on_a_non_matching_pair_is_refused_with_the_numbers(rows):
    sid, row = recast_row(rows)
    with pytest.raises(ValueError) as exc:
        compiled(row, sid, patch={"at": PLAIN_AT, "set": {"keyed": "data"}})
    msg = str(exc.value)
    assert 'chart_to recast keyed "data": the bars are not the line\'s own changes' in msg, msg
    assert "bar 0 (Bon) is 1.52 and the line's own change into datum 314 is -66.8" in msg, msg
    assert "use keyed: true" in msg and "the plain recast, or a cut" in msg, msg


@needs_objects
def test_an_explicit_key_is_never_overwritten_and_carries_no_derived_flag(rows):
    sid, row = recast_row(rows)
    _world, species = compiled(row, sid, patch={"at": DERIVED_AT, "set": {"keyed": "data"}})
    first = next(e for e in recasts(species) if e["at"] == DERIVED_AT)
    assert first["keyed"] == "data" and "keyed_derived" not in first, "the author asked; nothing was derived"
    assert first["key_map"][0] == {"datum": 312, "bar": 0, "from": 311}, "the map is written for the author's key too"


@needs_objects
def test_the_derived_key_is_the_only_thing_the_compile_gained(rows, monkeypatch):
    """The stripped-equal check: with the derivation switched off, the row compiles to exactly what it compiles
    to with it on, once the three new fields are taken off - the species and the page states both."""
    sid, row = recast_row(rows)
    world, species = compiled(row, sid)
    monkeypatch.setattr(B, "derive_recast_key", lambda A, Bs: (None, None, ""))
    world_off, species_off = compiled(row, sid)
    stripped = [{k: v for k, v in e.items() if k not in NEW_FIELDS} for e in species]
    stripped_off = [{k: v for k, v in e.items() if k not in NEW_FIELDS} for e in species_off]
    assert json.dumps(stripped, sort_keys=True) == json.dumps(stripped_off, sort_keys=True)
    assert json.dumps(world, sort_keys=True) == json.dumps(world_off, sort_keys=True), "no state was added or moved"


@needs_objects
@pytest.mark.skipif(not SHIPPED.is_file(), reason="the Tokyo short has not been compiled")
def test_the_shipped_tokyo_timeline_is_unchanged_but_for_the_new_fields(rows):
    """Against the artifact on disk: every scene's species, compiled now and stripped of the new fields, is the
    species list the shipped `tokyo-short.timeline.json` already carries - and that file carries none of them."""
    shipped = {s["scene_id"]: s.get("species") or [] for s in json.loads(SHIPPED.read_text(encoding="utf-8"))["scenes"]}
    assert not any(k in e for s in shipped.values() for e in s for k in NEW_FIELDS), "the shipped file predates E64"
    # The shipped cut predates R26-50 (2026-09-11 evening): the first page's build beat was re-fitted to the mount clock
    # (the build_to at 7.69 on a landing of 10.69 -> 4.49 on 7.49, build_short.py taking the landing from the gate's own
    # _page_land_offset). The one authored second that moved is normalised here so the test keeps proving E64's claim -
    # nothing but the new fields - rather than the clock's.
    for e in shipped.get("s02", []):
        if e.get("kind") == "build_to" and e.get("at") == 7.69:
            e["at"] = 4.49
    seen = 0
    for sid, i in B.row_ids(rows).items():
        if sid not in shipped or not shipped[sid]:
            continue
        row = rows[i]
        if not (str(row[2]).startswith("ledger:") and row[6]):
            continue
        _world, species = compiled(row, sid)
        stripped = [{k: v for k, v in e.items() if k not in NEW_FIELDS} for e in species]
        assert json.dumps(stripped, sort_keys=True) == json.dumps(shipped[sid], sort_keys=True), sid
        seen += 1
    assert seen >= 2, "the two ledger rows with species were checked"


@pytest.mark.skipif(not TARIFF_TABLE.is_file(), reason="the japan-tariff-trick short is not on disk")
def test_the_japan_tariff_short_has_no_recast_for_the_derivation_to_touch():
    """The other shipped short: its table carries no `chart_to` at all, so E64 changes nothing in it."""
    rows = T.load_rows(TARIFF_TABLE)
    assert not [e for r in rows if len(r) > 6 and r[6] for e in r[6]
                if isinstance(e, dict) and e.get("kind") == "chart_to"]


def test_a_recast_on_a_world_with_no_page_is_left_alone():
    """The derivation never raises where the plain recast did not: a still, or a state index the grammar owns."""
    sp = [{"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast", "state": 1}]
    B.derive_rescale_states({"kind": "still"}, sp, "plate-x", TOKYO)
    assert "keyed" not in sp[0], "no page, no key - and no crash"
    sp2 = [{"kind": "chart_to", "at": 1.0, "dur": 1.0, "to": "recast", "state": 9}]
    B.derive_rescale_states({"kind": "ledger", "page": {"builder": "dense-line"}}, sp2, "ledger:x:line", TOKYO)
    assert "keyed" not in sp2[0], "a state the page does not have is validate_species' refusal, not the key's"
