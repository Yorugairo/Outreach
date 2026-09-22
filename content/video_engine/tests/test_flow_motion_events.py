"""T20 motion-density accounting for renderer-valid ``species:flow`` edge states."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
import gate_motion_density as G  # noqa: E402


INITIAL = [["assets", "cash"], ["cash", "overnight"]]
REVERSED = [["assets", "overnight"], ["overnight", "cash"]]
SWAPPED = [["overnight", "assets"], ["cash", "overnight"]]
THREE_EDGES = [["overnight", "cash"], ["assets", "overnight"], ["cash", "assets"]]


def _flow(*, scene_span=(0.0, 40.0), at=10.0, dur=10.0, states=None, swap=None, edges=None, nodes=None):
    row = {
        "kind": "flow", "at": at, "dur": dur,
        "nodes": nodes or [{"id": "assets"}, {"id": "cash"}, {"id": "overnight"}],
        "edges": INITIAL if edges is None else edges,
    }
    if states is not None:
        row["edge_states"] = states
    if swap is not None:
        row["swap"] = swap
    return [{"scene_id": "s-flow", "span": list(scene_span), "species": [row]}]


def test_legacy_flow_events_keep_at_and_swap_only():
    scenes = _flow(swap={"at": 11.0, "node": "cash", "icon": "x", "label": "new"})
    assert G._species_events(scenes) == [10.0, 11.0]


def test_multiple_real_reversals_add_one_event_per_graph_change():
    states = [
        {"at": 13.0, "edges": REVERSED},
        {"at": 15.0, "edges": THREE_EDGES},
        {"at": 17.0, "edges": SWAPPED},
    ]
    assert G._species_events(_flow(states=states)) == [10.0, 13.0, 15.0, 17.0]


def test_edge_order_duplicates_and_identical_holds_are_not_events():
    states = [
        {"at": 13.0, "edges": [INITIAL[1], INITIAL[0]]},
        {"at": 15.0, "edges": [INITIAL[0], INITIAL[1], INITIAL[1]]},
    ]
    assert G._species_events(_flow(states=states)) == [10.0]


def test_state_event_uses_both_scene_bounds_and_excludes_exact_scene_end():
    states = [
        {"at": 13.0, "edges": REVERSED},  # valid schedule, before this scene starts
        {"at": 14.0, "edges": SWAPPED},
        {"at": 15.0, "edges": THREE_EDGES},
        {"at": 17.0, "edges": INITIAL},   # onset at scene end has no rendered interval
    ]
    assert G._species_events(_flow(scene_span=(14.0, 17.0), states=states)) == [14.0, 15.0]


def test_invalid_schedule_falls_back_without_partial_edge_events():
    cases = [
        [{"at": 12.8, "edges": REVERSED}],  # before flowClock.tagEnd (12.845 for this row)
        [{"at": 13.0, "edges": REVERSED}, {"at": 13.5, "edges": SWAPPED}],  # overlap
        [{"at": 15.0, "edges": REVERSED}, {"at": 14.0, "edges": SWAPPED}],  # unsorted
        [{"at": 19.5, "edges": REVERSED}],  # retract + draw finishes after diagram end
        [{"at": 13.0, "edges": [["assets", "missing"]]}],  # unknown node id
    ]
    for states in cases:
        assert G._species_events(_flow(states=states)) == [10.0]


def test_nonfinite_bool_and_malformed_states_invalidate_the_whole_schedule():
    states = [
        {"at": 13.0, "edges": REVERSED},
        {"at": float("nan"), "edges": SWAPPED},
        {"at": 15.0, "edges": SWAPPED},
    ]
    assert G._species_events(_flow(states=states)) == [10.0]
    for malformed in (
        {"at": float("inf"), "edges": REVERSED},
        {"at": True, "edges": REVERSED},
        {"at": "13", "edges": REVERSED},
        {"at": 13.0, "edges": "not-edges"},
        {"at": 13.0, "edges": [["assets", "assets"]]},
        {"at": 13.0, "edges": [["assets"]]},
        {"at": 13.0, "edges": [[True, "cash"]]},
    ):
        assert G._species_events(_flow(states=[malformed])) == [10.0]


def test_edge_state_event_collection_is_cold_and_does_not_mutate_input():
    scenes = _flow(states=[
        {"at": 13.0, "edges": REVERSED},
        {"at": 15.0, "edges": SWAPPED},
        {"at": 17.0, "edges": INITIAL},
    ])
    sp = scenes[0]["species"][0]
    before = copy.deepcopy(scenes)
    forward = G._flow_edge_state_events(sp, 0.0, 40.0)
    again = G._flow_edge_state_events(sp, 0.0, 40.0)
    assert forward == [13.0, 15.0, 17.0]
    assert again == forward
    assert scenes == before


def test_valid_clock_predicate_rejects_bool_and_nonfinite_values():
    assert G._finite_clock(0.0)
    assert not G._finite_clock(True)
    assert not G._finite_clock(float("nan"))
    assert not G._finite_clock(float("inf"))
