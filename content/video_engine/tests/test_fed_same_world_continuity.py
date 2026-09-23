"""Focused synthetic proof for the Fed pilot's same-world row continuity."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

TABLE_PATH = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure/SHOT-TABLE-PILOT.py"
TABLE_SPEC = importlib.util.spec_from_file_location("fed_same_world_shot_table", TABLE_PATH)
assert TABLE_SPEC and TABLE_SPEC.loader
TABLE = importlib.util.module_from_spec(TABLE_SPEC)
sys.modules[TABLE_SPEC.name] = TABLE
TABLE_SPEC.loader.exec_module(TABLE)


def _word_clock(phrases: tuple[str, ...]) -> tuple[list[dict[str, object]], float]:
    words: list[dict[str, object]] = []
    cursor = 0.0
    for phrase in phrases:
        for token in phrase.split():
            start = round(cursor, 3)
            words.append({"w": token, "start_s": start, "end_s": round(start + 0.2, 3)})
            cursor = round(start + 0.8, 3)
    return words, round(cursor + 1.0, 3)


def _assert_no_gaps(rows: list[tuple], runtime: float) -> None:
    assert rows[0][0] == 0.0
    assert rows[-1][1] == round(runtime, 2)
    for previous, current in zip(rows, rows[1:]):
        assert previous[1] == current[0]


def test_same_world_render_row_covers_intervening_semantic_span(monkeypatch) -> None:
    plate = "world:workshop"
    semantic = (
        TABLE.ShotSpec("P01", "Alpha.", plate, TABLE.NO_KEN),
        TABLE.ShotSpec("P01", "Beta.", plate, TABLE.NO_KEN),
        TABLE.ShotSpec("P01", "Gamma.", "world:ledger", TABLE.NO_KEN),
    )
    monkeypatch.setattr(TABLE, "semantic_specs_for", lambda _segment: semantic)

    rendered = TABLE.specs_for("bed")
    assert len(rendered) == 2
    assert rendered[0].start == "Alpha."
    assert rendered[1].start == "Gamma."

    words, runtime = _word_clock(tuple(spec.start for spec in semantic))
    rows = TABLE.build_rows(words, runtime, "bed")
    gamma_boundary = TABLE.W.cut_before(words, "Gamma.", exit="cut")
    beta_end = next(word["end_s"] for word in words if word["w"] == "Beta.")
    assert rows[0][2:4] == (plate, TABLE.NO_KEN)
    assert rows[0][1] == gamma_boundary
    assert rows[0][1] > beta_end
    _assert_no_gaps(rows, runtime)


def test_stateful_boundaries_and_transitions_are_not_coalesced() -> None:
    plate_a = "world:a"
    plate_b = "world:b"
    semantic = (
        TABLE.ShotSpec("P01", "Alpha.", plate_a, TABLE.NO_KEN),
        TABLE.ShotSpec("P01", "Beta.", plate_a, TABLE.NO_KEN, "dip"),
        TABLE.ShotSpec("P01", "Gamma.", plate_a, TABLE.NO_KEN),
        TABLE.ShotSpec("P01", "Delta.", plate_b, TABLE.NO_KEN),
        TABLE.ShotSpec("P01", "Epsilon.", plate_b, TABLE.NO_KEN, species=({"kind": "hold"},)),
        TABLE.ShotSpec("P01", "Zeta.", plate_b, TABLE.NO_KEN),
        TABLE.ShotSpec("P02", "Eta.", plate_b, TABLE.NO_KEN),
    )
    rendered = TABLE._coalesce_render_specs(semantic)
    assert [spec.start for spec in rendered] == ["Alpha.", "Beta.", "Delta.", "Epsilon.", "Zeta.", "Eta."]
    assert rendered[1].incoming == "dip"

    with_dock = (
        TABLE.ShotSpec("P01", "Theta.", plate_b, TABLE.NO_KEN),
        TABLE.ShotSpec("P01", "Iota.", plate_b, TABLE.NO_KEN, docks=({"id": "dock"},)),
    )
    assert len(TABLE._coalesce_render_specs(with_dock)) == 2


def test_all_six_group_receipts_follow_render_specs_and_retain_semantics(monkeypatch) -> None:
    semantic = TABLE.semantic_specs_for("pilot")
    rendered = TABLE.specs_for("pilot")
    assert semantic == TABLE.SHOT_SPECS

    # Every declared production group must survive rendering. In the current
    # table P06 is represented by the final P05 semantic row's receipt span.
    semantic_groups = tuple(dict.fromkeys(
        group
        for spec in semantic
        for group in (spec.covered_groups or (spec.group,))
    ))
    assert semantic_groups == TABLE.GROUPS
    assert semantic[-1].group == TABLE.GROUPS[-2]
    assert semantic[-1].covered_groups == TABLE.GROUPS[-2:]

    # Keep the real table and row-boundary logic under test; asset-specific
    # phrase resolution belongs to the focused pilot-schematic tests.
    monkeypatch.setattr(TABLE, "_resolve_docks", lambda _docks, _words, _end: [])
    monkeypatch.setattr(TABLE, "_resolve_species", lambda _species, _words: [])
    words, runtime = _word_clock(tuple(spec.start for spec in rendered))
    rows = TABLE.build_rows(words, runtime, "pilot")
    ranges = TABLE.group_ranges(rows)
    assert tuple(ranges) == TABLE.GROUPS

    expected_ranges: dict[str, tuple[float, float]] = {}
    for row, spec in zip(rows, rendered):
        for group in spec.covered_groups or (spec.group,):
            if group in expected_ranges:
                expected_ranges[group] = (expected_ranges[group][0], row[1])
            else:
                expected_ranges[group] = (row[0], row[1])
    assert ranges == expected_ranges
    _assert_no_gaps(rows, runtime)
