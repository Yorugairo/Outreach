"""P57 T11 / R26-70a: the metric-to-comparator morph as the SIXTH `chart_to` verb - the COMPILER GRAMMAR.

E76 (the operator, 2026-09-13): *"showing the P/E and then morphing it to a more visual number would be a great
repeatable mechanism"*. The row quotes the market's figure (`metric`), names the number the viewer feels
(`comparator`), and carries the authored arithmetic between them (`inputs` + `derive`) with its provenance
(`source`, E77). The compiler checks the arithmetic rather than trusting it: a comparator the row cannot reproduce
is a fabricated figure, and a fabricated figure is refused, never tweened.

Compiler-only in this slice: a timeline that authors the verb compiles and M36 counts it as a chart-to-chart
transform; the engine paints nothing for it until P57 T12.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import gate_one_shot_floor as FLOOR  # noqa: E402

PLATE = "ledger:ev-meta-pe-v1:line"
FIGURE = {"kind": "figure", "at": 30.0, "dur": 2.0, "text": "24.8x",
          "target": {"kind": "datum", "index": 5}}


def compare_row(**over) -> dict:
    """The acceptance row: a P/E of 24.8x against its own 21.5x history, morphed into '15 % dearer'."""
    entry = {"kind": "chart_to", "at": 32.0, "dur": 1.2, "to": "compare",
             "metric": {"value": 24.8, "text": "24.8x", "label": "forward P/E"},
             "comparator": {"value": 0.1535, "text": "15 % dearer", "label": "dearer than its own history"},
             "inputs": {"pe": 24.8, "hist": 21.5},
             "derive": "pe / hist - 1",
             "source": "[DERIVED: from ev-meta-pe-v1 + the 10-year median, pe / hist - 1]"}
    entry.update(over)
    for k, v in list(entry.items()):
        if v is None:
            del entry[k]
    return entry


# ---- the verb exists, and the map says WHEN ------------------------------------------------------------------------

def test_compare_is_the_sixth_chart_to_verb_and_carries_its_when():
    assert B.CHART_TO_KINDS == ("recast", "rescale", "extend", "park", "morph", "compare")
    assert set(B.CHART_TO_WHEN) == set(B.CHART_TO_KINDS), "every verb carries a when (P50 T1)"
    when = B.CHART_TO_WHEN["compare"]
    assert "E76" in when and "authored" in when, when
    assert B.COMPARE_TOL == 0.005 and B.COMPARE_HOLDS == ("metric", "gone")


# ---- a valid row compiles, survives into the timeline, and M36 counts it ---------------------------------------------

def test_a_valid_compare_row_compiles():
    assert B.validate_species([FIGURE, compare_row()], (0, 0, 0), PLATE) == []


@pytest.mark.parametrize("hold", ["metric", "gone", None])
def test_hold_says_what_becomes_of_the_quoted_metric(hold):
    assert B._validate_page_fields("chart_to", compare_row(hold=hold)) == []


def test_a_compare_derives_no_page_state():
    """The two numbers ARE the states: nothing is built for the verb, as the park builds nothing."""
    world = {"kind": "ledger", "page": {"builder": "dense-line", "series": [{"pts": [[0, 1], [1, 2]]}]}}
    species = [FIGURE, compare_row()]
    B.derive_rescale_states(world, species, PLATE, ROOT)
    assert "page_states" not in world and "state" not in species[1]


def test_the_species_survives_into_the_timeline_and_m36_counts_it():
    scene = {"scene_id": "s1", "span": [30.0, 36.0], "world": {"kind": "ledger", "page": {"builder": "dense-line"}},
             "species": [FIGURE, compare_row()]}
    assert "chart_to" in B.timeline_species([scene])
    rows = FLOOR.chart_to_transforms({"scenes": [scene]})
    assert rows == [("s1", "species chart_to -> compare")], rows


# ---- the refusals ----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("entry, needle", [
    (compare_row(metric={"text": "24.8x", "label": "forward P/E"}), "metric.value must be a number"),
    (compare_row(metric="24.8x"), "'metric' must be"),
    (compare_row(comparator={"label": "dearer", "text": "15 %"}), "comparator.value must be a number"),
    (compare_row(comparator=None), "'comparator' must be"),
    (compare_row(comparator={"value": 0.1535, "text": "15 % dearer", "label": "  "}),
     "a morph with no comparator label"),
    (compare_row(metric={"value": 24.8, "label": "forward P/E"}), "metric.text must be the figure AS QUOTED"),
    (compare_row(method="arap"), "'method' belongs to the MORPH"),
    (compare_row(state=1), "'state' is not named"),
    (compare_row(derive="pe / hist"), "a near-miss is a refusal, never a tween"),
    (compare_row(derive="pe / median - 1"), "'median', which is not one of the inputs"),
    (compare_row(derive=None), "'derive' must be the arithmetic"),
    (compare_row(inputs={}), "'inputs' must be a non-empty dict"),
    (compare_row(inputs={"pe": "24.8x", "hist": 21.5}), "input 'pe' must be a number"),
    (compare_row(source=None), "'source' is required and starts with"),
    (compare_row(source="Bloomberg"), "figures are never fabricated"),
    (compare_row(hold="beside"), "hold must be one of metric|gone"),
    (compare_row(to="compared"), "'to' must be one of"),
])
def test_the_grammar_refuses_a_figure_the_row_cannot_stand_behind(entry, needle):
    errs = B._validate_page_fields("chart_to", entry)
    assert any(needle in e for e in errs), (needle, errs)


def test_a_derive_inside_the_tolerance_is_the_same_number():
    """0.5 % of the larger magnitude, RECAST_DATA_TOL's spirit - inside it the two numbers ARE one."""
    near = 0.1535 * (1 + B.COMPARE_TOL * 0.9)
    assert B._validate_page_fields("chart_to", compare_row(comparator={
        "value": near, "text": "15 % dearer", "label": "dearer than its own history"})) == []
    far = 0.1535 * (1 + B.COMPARE_TOL * 3)
    assert any("never a tween" in e for e in B._validate_page_fields("chart_to", compare_row(comparator={
        "value": far, "text": "15 % dearer", "label": "dearer than its own history"})))


def test_a_page_that_never_wrote_the_quoted_figure_may_not_morph_it():
    """E50: the number the sentence turns on is WRITTEN at its datum before it can morph."""
    errs = B.validate_species([compare_row()], (0, 0, 0), PLATE)
    assert any("writes no `figure` species" in e and "E50" in e for e in errs), errs
    other = dict(FIGURE, text="21.5x")
    assert any("writes no `figure` species" in e for e in B.validate_species([other, compare_row()], (0, 0, 0), PLATE))


# ---- the evaluator: parsed and WALKED, never eval'd -------------------------------------------------------------------

@pytest.mark.parametrize("expr, needle", [
    ("abs(pe)", "Call is not plain arithmetic"),
    ("pe.real", "Attribute is not plain arithmetic"),
    ("inputs['pe']", "not plain arithmetic"),
    ("pe > hist", "not plain arithmetic"),
    ("pe ** 2", "not plain arithmetic"),
    ("__import__('os')", "not plain arithmetic"),
    ("median / 2", "it names 'median', which is not one of the inputs"),
    ("pe / (hist - 21.5)", "it divides by zero"),
    ("pe /", "it does not parse"),
    ("", "the arithmetic is empty"),
])
def test_the_derive_evaluator_refuses_everything_that_is_not_arithmetic(expr, needle):
    value, why = B.derive_compare(expr, {"pe": 24.8, "hist": 21.5})
    assert value is None and needle in (why or ""), (expr, value, why)


@pytest.mark.parametrize("expr, want", [
    ("pe / hist - 1", 24.8 / 21.5 - 1),
    ("-pe + hist", -24.8 + 21.5),
    ("(pe - hist) * 100 / hist", (24.8 - 21.5) * 100 / 21.5),
    ("10000 * hist / pe", 10000 * 21.5 / 24.8),
])
def test_the_derive_evaluator_reads_plain_arithmetic(expr, want):
    value, why = B.derive_compare(expr, {"pe": 24.8, "hist": 21.5})
    assert why is None and value == pytest.approx(want)
