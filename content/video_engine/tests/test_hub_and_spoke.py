"""P71 T17 (was P69 T57): HUB AND SPOKE - one institution to many - and A LINK THAT FAILS (A26).

At 4e077e4 `layout: "hub"` was refused as unknown ("not one of row|ring"), while a flow's `fail` and a node's own `at`
were ACCEPTED AND IGNORED (review finding 7's class): `_validate_flow_extensions` returned [] for `fail: "soon"` and for
`{"at": 12.0}` on a row's node. These tests pin the hub's grammar and every by-name refusal of the keys the slice
introduces (rule h, s106), the compiler's hub clock against the module's, the gate's one event at the failure (s99: the
X is struck, the link retracts - motion), the card, and the golden."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402

FLOW_MJS = "./content/video_engine/scripts/species/flow.mjs"
CARDS = ROOT / "content" / "video_engine" / "effects" / "cards" / "species.json"
RIM = ["b1", "b2", "b3", "b4"]
ICONS = ("landmark", "factory", "cpu", "ship", "coins")


def hub(**extra) -> dict:
    """The bond market (the hub) lending out to four borrowers on its rim - H row 16's candidate beat."""
    ids = ["market"] + RIM
    entry = {"kind": "flow", "at": 10.0, "dur": 14.0, "layout": "hub",
             "target": {"kind": "region", "x0": 0.25, "y0": 0.08, "x1": 0.75, "y1": 0.95},
             "nodes": [{"id": i, "icon": icon, "label": i.upper()} for i, icon in zip(ids, ICONS)],
             "edges": [["market", r] for r in RIM]}
    entry.update(extra)
    return entry


def with_rim_at(entry: dict, ats: dict) -> dict:
    out = copy.deepcopy(entry)
    for n in out["nodes"]:
        if n["id"] in ats:
            n["at"] = ats[n["id"]]
    return out


def errors(entry: dict) -> list[str]:
    return B.validate_species([entry], (0, 0, 0), "world-test")


def node_json(js: str):
    r = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------- the grammar
def test_a_hub_validates_in_every_authored_form_and_is_not_mutated():
    many = hub(nodes=[{"id": f"n{i}", "icon": "landmark", "label": f"N{i}"} for i in range(9)],
               edges=[["n0", f"n{i}"] for i in range(1, 9)])
    inward = hub(edges=[[r, "market"] for r in RIM])
    mixed = hub(edges=[["market", "b1"], ["b2", "market"], ["market", "b3"], ["b4", "market"]])
    named = with_rim_at(hub(), {"b1": 12.0, "b2": 12.8, "b3": 13.6, "b4": 14.4})
    for entry in (hub(), many, inward, mixed, named, hub(tokens={"from_at": 12.0}), hub(tag="2025"),
                  hub(readability="landscape-phone"), hub(fail={"edge": ["market", "b3"], "at": 15.0}),
                  hub(swap={"at": 16.0, "node": "b2", "icon": "cpu", "label": "CHIPS"})):
        before = copy.deepcopy(entry)
        assert errors(entry) == [], (entry, errors(entry))
        assert entry == before


def test_a_row_and_a_ring_may_fail_a_link_too():
    row = {"kind": "flow", "at": 10.0, "dur": 10.0, "target": {"kind": "region", "x0": .1, "y0": .2, "x1": .9, "y1": .8},
           "nodes": [{"id": "a", "icon": "factory", "label": "A"}, {"id": "b", "icon": "coins", "label": "B"},
                     {"id": "c", "icon": "ship", "label": "C"}],
           "edges": [["a", "b"], ["b", "c"]], "fail": {"edge": ["b", "c"], "at": 14.0}}
    assert errors(row) == []
    ring = dict(row, layout="ring", edges=[["a", "b"], ["b", "c"], ["c", "a"]], fail={"edge": ["c", "a"], "at": 14.0})
    assert errors(ring) == []


def test_the_row_keeps_its_six_node_ceiling():
    seven = {"kind": "flow", "at": 10.0, "dur": 10.0, "target": {"kind": "region", "x0": .1, "y0": .2, "x1": .9, "y1": .8},
             "nodes": [{"id": f"n{i}", "icon": "landmark", "label": f"N{i}"} for i in range(7)],
             "edges": [[f"n{i}", f"n{i + 1}"] for i in range(6)]}
    assert any("'nodes' must be a list of 2-6" in e for e in errors(seven))


@pytest.mark.parametrize("make, needle", [
    (lambda: hub(nodes=hub()["nodes"][:3], edges=[["market", "b1"], ["market", "b2"]]),
     "layout 'hub' needs one hub and 3-8 rim nodes"),
    (lambda: hub(nodes=[{"id": f"n{i}", "icon": "landmark", "label": f"N{i}"} for i in range(10)],
                 edges=[["n0", f"n{i}"] for i in range(1, 10)]), "layout 'hub' needs one hub and 3-8 rim nodes"),
    (lambda: hub(edges=[["market", "b1"], ["market", "b2"], ["market", "b3"], ["b3", "b4"]]), "a hub's edges are spokes"),
    (lambda: hub(edges=[["market", "b1"], ["market", "b2"], ["market", "b3"]]), "rim node 'b4' has no spoke"),
    (lambda: hub(edges=[["market", "b1"], ["b1", "market"], ["market", "b2"], ["market", "b3"], ["market", "b4"]]),
     "rim node 'b1' has 2 spokes"),
    (lambda: with_rim_at(hub(), {"market": 12.0}), "the hub lands on the diagram's own clock"),
    (lambda: with_rim_at(hub(), {"b2": 10.2}), "a rim node lands after its hub"),
    (lambda: with_rim_at(hub(), {"b2": "soon"}), "rim node 'b2': 'at' must be a number"),
    (lambda: with_rim_at(hub(), {"b2": 23.9}), "rim node 'b2': at 23.9 leaves its spoke unfinished"),
    (lambda: hub(edge_states=[{"at": 16.0, "edges": [["market", "b1"]]}]), "layout 'hub' and edge_states are mutually exclusive"),
    (lambda: hub(operators=["-", "-", "-", "-"]), "layout 'hub' and operators are mutually exclusive"),
    (lambda: hub(fail="soon"), "'fail' must be a dict {edge, at}"),
    (lambda: hub(fail={"edge": ["market", "b1"], "at": 15.0, "when": 1}), "fail key 'when' is not one of edge|at"),
    (lambda: hub(fail={"edge": ["b1", "b2"], "at": 15.0}), "fail edge ['b1', 'b2'] is not one of this diagram's edges"),
    (lambda: hub(fail={"edge": "market", "at": 15.0}), "fail edge 'market' is not one of this diagram's edges"),
    (lambda: hub(fail={"edge": ["market", "b1"]}), "fail at must be a number"),
    (lambda: hub(fail={"edge": ["market", "b1"], "at": 11.0}), "before its link is drawn"),
    (lambda: hub(fail={"edge": ["market", "b1"], "at": 23.8}), "leaves the X unstruck"),
    (lambda: hub(layout="row", fail={"edge": ["market", "b1"], "at": 15.0},
                 edge_states=[{"at": 16.0, "edges": [["market", "b1"]]}]), "fail and edge_states are mutually exclusive"),
])
def test_every_malformed_or_misplaced_hub_or_fail_key_is_refused_by_name(make, needle):
    errs = errors(make())
    assert any(needle in e for e in errs), (needle, errs)


def test_a_nodes_own_at_is_refused_off_a_hub():
    row = hub(layout="row", edges=[["market", "b1"], ["b1", "b2"], ["b2", "b3"], ["b3", "b4"]])
    assert errors(row) == []
    errs = errors(with_rim_at(row, {"b2": 12.0}))
    assert any("node 'b2': a node's own 'at' is a hub rim's word" in e for e in errs), errs
    ops = {"kind": "flow", "at": 10.0, "dur": 10.0, "target": {"kind": "region", "x0": .1, "y0": .2, "x1": .9, "y1": .8},
           "nodes": [{"id": "a", "icon": "factory", "label": "A"}, {"id": "b", "icon": "coins", "label": "B"}],
           "edges": [["a", "b"]], "operators": ["-"], "fail": {"edge": ["a", "b"], "at": 14.0}}
    assert any("fail and operators are mutually exclusive" in e for e in errors(ops))


def test_tokens_on_a_hub_wait_for_the_first_spoke_drawn():
    named = with_rim_at(hub(tokens={"from_at": 12.5}), {"b1": 13.0, "b2": 13.4, "b3": 13.8, "b4": 14.2})
    first = min(B.flow_edge_drawn(named, j) for j in range(4))
    assert first == pytest.approx(13.0 + B.FLOW_CLOCK["EDGE_S"])
    assert any("before the first arrow is drawn" in e for e in errors(named))
    named["tokens"]["from_at"] = 13.4
    assert errors(named) == []


# ---------------------------------------------------------------- the clock, both sides
def test_the_hub_clock_is_the_modules():
    """The compiler's hub clock (flow_hub_clock / flow_edge_drawn) against species/flow.mjs's flowClock, for the
    default schedule, rim words, and spokes both ways (out: the spoke then its node; in: the node then its spoke)."""
    cases = [hub(), hub(edges=[["market", "b1"], ["b2", "market"], ["market", "b3"], ["b4", "market"]]),
             with_rim_at(hub(edges=[["market", "b1"], ["b2", "market"], ["market", "b3"], ["b4", "market"]]),
                         {"b1": 12.5, "b3": 14.0, "b4": 13.1})]
    for sp in cases:
        got = node_json(f"import {{ FLOW, flowClock }} from '{FLOW_MJS}'; const sp = {json.dumps(sp)};"
                        "const C = flowClock(sp); console.log(JSON.stringify({nodeAt: C.nodeAt, edgeAt: C.edgeAt, "
                        "drawn: C.edgeAt.map((a) => a + FLOW.EDGE_S), hub: C.hub === true}));")
        py = B.flow_hub_clock(sp)
        assert got["hub"] is True
        assert py["nodeAt"] == pytest.approx(got["nodeAt"], abs=1e-12)
        assert py["edgeAt"] == pytest.approx(got["edgeAt"], abs=1e-12)
        for j, drawn in enumerate(got["drawn"]):
            assert B.flow_edge_drawn(sp, j) == pytest.approx(drawn, abs=1e-12)


def test_a_row_clock_is_what_it_was():
    row = hub(layout="row", edges=[["market", "b1"], ["b1", "b2"], ["b2", "b3"], ["b3", "b4"]])
    got = node_json(f"import {{ flowClock }} from '{FLOW_MJS}'; console.log(JSON.stringify(flowClock({json.dumps(row)})));")
    assert set(got) == {"box", "nodeAt", "landed", "edgeAt", "tagAt", "tagEnd"}, "no hub key leaks into a row's clock"


def test_the_compilers_mirrors_are_the_modules_dials():
    """FLOW_FAIL_S is CHIP.CROSS_S (the X's two strokes and the retract), and the failed link's ink is the chip's SELL
    ink - the template's --lp-neg, which T12's tests pin to the template."""
    got = node_json(f"import {{ FLOW }} from '{FLOW_MJS}'; import {{ CHIP }} from "
                    "'./content/video_engine/scripts/species/chip.mjs'; console.log(JSON.stringify({cross: CHIP.CROSS_S, "
                    "fail: FLOW.FAIL_INK, sell: CHIP.TAB_INK.sell}));")
    assert B.FLOW_FAIL_S == got["cross"]
    assert got["fail"] == got["sell"]


# ---------------------------------------------------------------- the gate
def test_the_gate_counts_the_failure_once():
    scene = lambda sp: [{"scene_id": "s-hub", "span": [0.0, 40.0], "species": [sp]}]
    assert G._species_events(scene(hub(fail={"edge": ["market", "b2"], "at": 15.0}))) == [10.0, 15.0]
    assert G._species_events(scene(hub())) == [10.0], "no fail, no event: every existing flow counts as it did"


# ---------------------------------------------------------------- the card and the golden
def test_the_card_names_the_hub_and_the_failed_link():
    card = next(c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"] if c["id"] == "species:flow")
    opts = {o["token"]: o for o in card["options"]}
    assert "hub" in B.FLOW_LAYOUTS and "hub" in opts["layout"]["means"]
    assert opts["fail"]["source_set"] == "FLOW_FAIL_KEYS"
    assert "P71 T17" in card["doctrine"]


def test_the_hub_golden_is_registered():
    sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
    import build_golden_sources as S
    tl, uris = S.SURFACES["hub-spoke-fail"]()
    sp = tl["scenes"][0]["species"][0]
    assert sp["layout"] == "hub" and sp["fail"]["at"] < S.FRAME_T["hub-spoke-fail"] < sp["at"] + sp["dur"]
    assert errors(sp) == []
    for suffix, payload in (("timeline", tl), ("uris", uris)):
        name = f"hub-spoke-fail.{suffix}.json"
        rel = f"content/video_engine/tests/golden/sources/{name}"
        r = subprocess.run(["git", "show", f":{rel}"], cwd=ROOT, capture_output=True, timeout=60)
        raw = r.stdout if r.returncode == 0 else (json.dumps(payload, indent=1, sort_keys=True) + "\n").encode("utf-8")
        assert b"\r" not in raw, name
