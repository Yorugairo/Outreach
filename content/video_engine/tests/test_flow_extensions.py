"""T20: formula/connectivity opt-ins fail closed without changing legacy flows."""
import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_scene_timeline_f as B


def flow(**extra):
    return {"kind": "flow", "at": 10., "dur": 10.,
            "target": {"kind": "region", "x0": .1, "y0": .2, "x1": .9, "y1": .8},
            "nodes": [{"id": "a", "icon": "factory", "label": "A"},
                      {"id": "b", "icon": "coins", "label": "B"},
                      {"id": "c", "icon": "ship", "label": "C"}],
            "edges": [["a", "b"], ["b", "c"]], **extra}


def errors(entry):
    return B.validate_species([entry], (0, 0, 0), "world-test")


def test_legacy_and_opt_ins_validate_without_mutating_declarations():
    for entry in (flow(), flow(operators=["-", "-"], readability="landscape-phone"),
                  flow(edge_states=[{"at": 14., "edges": [["c", "b"], ["b", "a"]]},
                                    {"at": 16., "edges": [["a", "b"]]}])):
        original = copy.deepcopy(entry)
        assert errors(entry) == []
        assert entry == original


@pytest.mark.parametrize("extra", [
    {"readability": "tiny"}, {"readability": None},
    {"operators": []}, {"operators": ["-"]}, {"operators": ["+", "-"]},
    {"operators": "--"}, {"operators": ["-", "-"], "edge_states": []},
    {"operators": ["-", "-"], "edges": [["a", "c"], ["c", "b"]]},
    {"edge_states": []}, {"edge_states": None},
    {"edge_states": [None]}, {"edge_states": [{"at": 14., "edges": []}]},
    {"edge_states": [{"at": 14., "edges": [["a", "missing"]]}]},
    {"edge_states": [{"at": 14., "edges": [["a", "a"]]}]},
    {"edge_states": [{"at": 14., "edges": [["a"]]}]},
    {"edge_states": [{"at": 14., "edges": [[{}, "a"]]}]},
    *({"edge_states": [{"at": value, "edges": [["a", "b"]]}]}
      for value in (True, "14", float("nan"), float("inf"), 10., 11., 19.9)),
    {"edge_states": [{"at": 15., "edges": [["a", "b"]]},
                     {"at": 14., "edges": [["b", "a"]]}]},
    {"edge_states": [{"at": 15., "edges": [["a", "b"]]},
                     {"at": 15.3, "edges": [["b", "a"]]}]},
])
def test_bad_opt_ins_fail_closed(extra):
    assert errors(flow(**extra))


def test_edge_change_must_finish_inside_window():
    entry = flow(edge_states=[{"at": 19.02, "edges": [["a", "b"], ["b", "c"]]}])
    assert errors(entry) == []
    entry["edge_states"][0]["at"] += .001
    assert any("complete change" in error for error in errors(entry))


@pytest.mark.parametrize("key", ["at", "dur"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), True])
def test_nonfinite_diagram_clocks_rejected_for_edge_states(key, value):
    entry = flow(edge_states=[{"at": 14., "edges": [["b", "a"]]}])
    entry[key] = value
    assert errors(entry)
