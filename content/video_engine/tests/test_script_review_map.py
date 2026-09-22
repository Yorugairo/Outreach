"""Offline tests for the narrative_map.v1 semantic custody contract."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "content/video_engine/scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures/script_review"
sys.path.insert(0, str(SCRIPTS))

import script_review as R  # noqa: E402


def _map() -> dict:
    return json.loads((FIXTURES / "sustained-tension-map.json").read_text(encoding="utf-8"))


def test_complete_map_validates_and_reports_endpoint_coverage():
    result = R.validate_narrative_map(_map())
    assert result.ok, result.errors
    assert result.status == "CLEAR"
    windows = result.diagnostics["coverage"]["windows"]
    assert windows["90"]["ok"]
    assert windows["180"]["ok"]
    assert windows["300"]["effective_end_s"] == 240
    assert windows["300"]["ok"]


def test_non_question_tension_is_valid():
    data = _map()
    data["micro_loops"][0]["tension"] = {"start_s": 12, "end_s": 24, "kind": "constraint"}
    result = R.validate_narrative_map(data)
    assert result.ok, result.errors


@pytest.mark.parametrize(
    ("mutation", "needle"),
    [
        (lambda data: data["micro_loops"][1].pop("payoff"), "payoff"),
        (lambda data: data["micro_loops"][0].update({"next_loop": "missing-loop"}), "unknown loop"),
        (lambda data: data["micro_loops"][0].update({"shared_object_or_person": ""}), "shared object"),
        (lambda data: data["macro_phases"][0]["callbacks"].__setitem__(0, {"from": "loop-opening", "to": "missing"}), "unknown ID"),
    ],
)
def test_relationship_and_span_failures_are_explicit(mutation, needle):
    data = _map()
    mutation(data)
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any(needle in error for error in result.errors)


def test_duplicate_ids_fail_closed():
    data = _map()
    duplicate = copy.deepcopy(data["micro_loops"][0])
    data["micro_loops"].append(duplicate)
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any("duplicate narrative ID" in error for error in result.errors)


def test_temporal_order_and_endpoint_tail_are_not_hidden():
    data = _map()
    data["micro_loops"][2]["payoff"] = {"start_s": 110, "end_s": 115}
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any("temporally ordered" in error for error in result.errors)

    intervals = [(0, 30, "a"), (40, 70, "b")]
    coverage = R.coverage_diagnostics(intervals, 90)
    gaps = coverage["windows"]["90"]["gaps"]
    assert any(gap["kind"] == "endpoint_tail" for gap in gaps)
    assert coverage["windows"]["90"]["uncovered_s"] == 30


def test_micro_and_macro_spans_cannot_extend_beyond_runtime():
    data = _map()
    data["micro_loops"][-1]["payoff"]["end_s"] = 999
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any("must stay within runtime_s" in error for error in result.errors)


def test_middle_coverage_gap_and_self_loop_fail_closed():
    data = _map()
    data["micro_loops"] = [data["micro_loops"][0], data["micro_loops"][-1]]
    data["micro_loops"][0]["next_loop"] = data["micro_loops"][-1]["id"]
    data["macro_phases"] = [{**phase, "callbacks": [], "foreshadows": []}
                            for phase in data["macro_phases"]]
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any("full runtime without gaps" in error for error in result.errors)

    data = _map()
    for loop in data["micro_loops"]:
        loop["next_loop"] = loop["id"]
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any("cannot point to itself" in error for error in result.errors)
    assert any("cycle" in error or "reachable" in error for error in result.errors)

    data = _map()
    data["macro_phases"][-1]["end_s"] = 999
    result = R.validate_narrative_map(data)
    assert not result.ok
    assert any("must stay within runtime_s" in error for error in result.errors)


def test_markdown_render_is_readable():
    data = _map()
    result = R.validate_narrative_map(data)
    markdown = R.render_narrative_map_markdown(data, result)
    assert "## Micro loops" in markdown
    assert "## Macro phases" in markdown
    assert "## Coverage diagnostics" in markdown
    assert "loop-opening" in markdown
