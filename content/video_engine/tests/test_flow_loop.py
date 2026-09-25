"""P71 T11 (was P69 T43): `loop` - a flow laid as a RING, and TOKENS moving on its arrows (A27).

At cd0b630 a flow's `layout` and `tokens` were ACCEPTED AND IGNORED (review finding 7): `_validate_flow_extensions`
returned [] for `layout: "ring"` on an open chain and for `tokens: "lots"`, and `flowLayout(box, 4, {layout:
"ring"})` returned a row. These tests pin the ring's geometry, the by-name refusal of every malformed or misplaced key
the slice introduces (rule h, s106: "a silent drop is neither advice nor refusal"), the gate's one event at the
tokens' start (s99: they travel), the compiler's clock against the module's, and the token's ink against the
arrow's."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402

FLOW_MJS = "./content/video_engine/scripts/species/flow.mjs"
TEMPLATE = ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-player.template.html"
CARDS = ROOT / "content" / "video_engine" / "effects" / "cards" / "species.json"
IDS = ["capex", "chips", "cloud", "profit"]
LOOP = [["capex", "chips"], ["chips", "cloud"], ["cloud", "profit"], ["profit", "capex"]]


def ring(**extra) -> dict:
    """A four-node loop (the capex money round the borrowers), tokens from the word after it is drawn."""
    entry = {"kind": "flow", "at": 10.0, "dur": 14.0, "layout": "ring",
             "target": {"kind": "region", "x0": 0.25, "y0": 0.12, "x1": 0.75, "y1": 0.95},
             "nodes": [{"id": i, "icon": icon, "label": i.upper()}
                       for i, icon in zip(IDS, ("factory", "cpu", "ship", "coins"))],
             "edges": copy.deepcopy(LOOP), "tokens": {"from_at": 13.5, "n": 2}}
    entry.update(extra)
    return entry


def errors(entry: dict) -> list[str]:
    return B.validate_species([entry], (0, 0, 0), "world-test")


def node_json(js: str):
    r = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------- the grammar
def test_a_closed_ring_with_tokens_validates_and_is_not_mutated():
    for entry in (ring(), ring(tokens={"from_at": 13.5}), ring(tokens={"from_at": 20.0, "n": 4, "speed": 300, "glyph": "coins"}),
                  ring(layout="row"), ring(readability="landscape-phone")):
        before = copy.deepcopy(entry)
        assert errors(entry) == [], entry
        assert entry == before


def test_a_row_flow_may_carry_tokens_too():
    row = ring(nodes=ring()["nodes"][:3], edges=[["capex", "chips"], ["chips", "cloud"]])
    del row["layout"]
    assert errors(row) == []


def test_an_open_chain_under_ring_is_refused_by_name():
    errs = errors(ring(edges=LOOP[:3]))
    assert any("a loop closes on itself" in e and "'profit'" in e and "'capex'" in e for e in errs), errs


@pytest.mark.parametrize("extra, needle", [
    ({"layout": "spiral"}, "layout 'spiral' is not one of row|ring"),
    ({"layout": None}, "layout None is not one of row|ring"),
    ({"edges": [["capex", "chips"], ["cloud", "profit"], ["chips", "cloud"], ["profit", "capex"]]}, "that loop exactly"),
    ({"edges": [["chips", "capex"], ["cloud", "chips"], ["profit", "cloud"], ["capex", "profit"]]}, "that loop exactly"),
    ({"edges": LOOP + [["capex", "cloud"]]}, "that loop exactly"),
    ({"tokens": "lots"}, "'tokens' must be a dict"),
    ({"tokens": {"from_at": 13.5, "count": 3}}, "tokens key 'count' is not one of"),
    ({"tokens": {"from_at": 13.5, "n": 0}}, "tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 13.5, "n": 5}}, "tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 13.5, "n": 1.5}}, "tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 13.5, "n": True}}, "tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 13.5, "speed": 10}}, "tokens speed must be 60-900"),
    ({"tokens": {"from_at": 13.5, "speed": "fast"}}, "tokens speed must be 60-900"),
    ({"tokens": {"from_at": 13.5, "glyph": "banknote"}}, "tokens glyph must be one of coins"),
    ({"tokens": {"n": 2}}, "tokens from_at must be a number"),
    ({"tokens": {"from_at": 11.0}}, "before the first arrow is drawn"),
    ({"tokens": {"from_at": 24.0}}, "falls outside the diagram's window"),
])
def test_every_malformed_layout_or_token_key_is_refused_by_name(extra, needle):
    errs = errors(ring(**extra))
    assert any(needle in e for e in errs), (needle, errs)


def test_a_ring_needs_three_nodes():
    two = ring(nodes=ring()["nodes"][:2], edges=[["capex", "chips"], ["chips", "capex"]])
    assert any("needs 3+ nodes" in e for e in errors(two))


def test_tokens_are_refused_beside_operators_and_edge_states():
    row = {"kind": "flow", "at": 10.0, "dur": 10.0, "target": {"kind": "region", "x0": .1, "y0": .2, "x1": .9, "y1": .8},
           "nodes": [{"id": "a", "icon": "factory", "label": "A"}, {"id": "b", "icon": "coins", "label": "B"},
                     {"id": "c", "icon": "ship", "label": "C"}],
           "edges": [["a", "b"], ["b", "c"]], "tokens": {"from_at": 13.0}}
    assert errors(row) == []
    assert any("tokens and operators are mutually exclusive" in e for e in errors(dict(row, operators=["-", "-"])))
    states = dict(row, edge_states=[{"at": 16.0, "edges": [["c", "b"]]}])
    assert any("tokens and edge_states are mutually exclusive" in e for e in errors(states))


def test_the_first_arrow_instant_is_the_modules():
    """The compiler's FLOW_CLOCK mirror and flow_edge_drawn against species/flow.mjs's own flowClock."""
    got = node_json(f"import {{ FLOW, flowClock, flowTokenStart }} from '{FLOW_MJS}'; import {{ CHIP }} from "
                    f"'./content/video_engine/scripts/species/chip.mjs'; const sp = {json.dumps(ring(tokens={'from_at': 0}))};"
                    "const C = flowClock(sp); console.log(JSON.stringify({clock: {BOX_S: FLOW.BOX_S, BOX_LEAD: FLOW.BOX_LEAD,"
                    " NODE_STEP: FLOW.NODE_STEP, LAND_S: CHIP.LAND_S, EDGE_LAG: FLOW.EDGE_LAG, EDGE_S: FLOW.EDGE_S},"
                    " drawn: C.edgeAt.map((a) => a + FLOW.EDGE_S), starts: C.edgeAt.map((_, j) => flowTokenStart(sp, j))}));")
    assert got["clock"] == B.FLOW_CLOCK
    entry = ring()
    for j, drawn in enumerate(got["drawn"]):
        assert B.flow_edge_drawn(entry, j) == pytest.approx(drawn, abs=1e-12)
        assert got["starts"][j] == pytest.approx(drawn, abs=1e-12), "from_at 0: each arrow's tokens wait for their arrow"


def test_species_icons_carries_a_named_token_glyph_and_no_other():
    assert B.species_icons(ring()) == ["factory", "cpu", "ship", "coins"]
    assert B.species_icons(ring(tokens={"from_at": 13.5, "glyph": "coins"}))[-1] == "coins"
    assert len(B.species_icons(ring(tokens={"from_at": 13.5, "glyph": "coins"}))) == 5


# ---------------------------------------------------------------- the gate
def test_the_gate_counts_the_tokens_start_once():
    scene = lambda sp: [{"scene_id": "s-loop", "span": [0.0, 40.0], "species": [sp]}]
    assert G._species_events(scene(ring())) == [10.0, 13.5]
    plain = ring()
    del plain["tokens"]
    assert G._species_events(scene(plain)) == [10.0], "no tokens, no event: every existing flow counts as it did"


# ---------------------------------------------------------------- the ring and the ink
def test_the_ring_lays_the_nodes_on_an_ellipse_first_at_twelve_clockwise():
    lay = node_json(f"import {{ flowLayout }} from '{FLOW_MJS}';"
                    "console.log(JSON.stringify(flowLayout({x: 480, y: 130, w: 960, h: 900}, 4, {layout: 'ring'})));")
    assert lay["ring"] is True and lay["column"] is False
    c = lay["cells"]
    assert len(c) == 4
    assert c[0]["x"] == pytest.approx(480 + 480, abs=1e-6), "the first node at 12 o'clock"
    assert c[0]["y"] < c[1]["y"] < c[2]["y"] and c[1]["x"] > c[0]["x"] > c[3]["x"], "then clockwise: right, bottom, left"
    assert c[1]["y"] == pytest.approx(c[3]["y"], abs=1e-6) and c[0]["x"] == pytest.approx(c[2]["x"], abs=1e-6)
    half = lay["half"]
    for p in c:
        assert 480 <= p["x"] - half and p["x"] + half <= 1440 and 130 <= p["y"] - half and p["y"] + half <= 1030


def test_the_row_is_what_it_was_when_no_layout_is_named():
    got = node_json(f"import {{ flowLayout }} from '{FLOW_MJS}'; const b = {{x: 200, y: 400, w: 1500, h: 420}};"
                    "console.log(JSON.stringify([flowLayout(b, 3), flowLayout(b, 3, null), flowLayout(b, 3, {layout: 'row'})]));")
    assert got[0] == got[1] == got[2]
    assert "ring" not in got[0] and "bows" not in got[0]


def test_the_token_ink_is_the_arrows_ink():
    css = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"#species \.flowarrow[^{]*\{[^}]*stroke:\s*(#[0-9A-Fa-f]{6})", css)
    assert m, "the template's .flowarrow rule"
    ink = node_json(f"import {{ FLOW }} from '{FLOW_MJS}'; console.log(JSON.stringify(FLOW.TOKEN_INK));")
    assert ink.lower() == m.group(1).lower()


# ---------------------------------------------------------------- the card and the golden
def test_the_card_names_layout_and_tokens_as_options():
    card = next(c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"] if c["id"] == "species:flow")
    opts = {o["token"]: o for o in card["options"]}
    assert opts["layout"]["source_set"] == "FLOW_LAYOUTS"
    assert opts["tokens"]["source_set"] == "FLOW_TOKEN_KEYS"
    assert "P71 T11" in card["doctrine"]


def test_the_loop_golden_is_registered():
    sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
    import build_golden_sources as S
    tl, uris = S.SURFACES["flow-loop-tokens"]()
    sp = tl["scenes"][0]["species"][0]
    assert sp["layout"] == "ring" and sp["tokens"]["from_at"] < S.FRAME_T["flow-loop-tokens"] < sp["at"] + sp["dur"]
    assert errors(sp) == []
    for suffix, payload in (("timeline", tl), ("uris", uris)):
        name = f"flow-loop-tokens.{suffix}.json"
        assert b"\r" not in committed_source_bytes(name, payload), name


def committed_source_bytes(name: str, payload: dict) -> bytes:
    """The golden source AS COMMITTED (golden sources are written LF): the index copy via `git show :<path>`, never the
    working tree - a `core.autocrlf=true` checkout holds every source as CRLF on disk and LF in git. Outside a git
    checkout (or before the file is staged) the generator's own serialisation, in memory: `write_surface`'s
    `json.dumps(payload, indent=1, sort_keys=True) + "\n"`."""
    rel = f"content/video_engine/tests/golden/sources/{name}"
    try:
        r = subprocess.run(["git", "show", f":{rel}"], cwd=ROOT, capture_output=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        r = None
    if r is not None and r.returncode == 0:
        return r.stdout
    return (json.dumps(payload, indent=1, sort_keys=True) + "\n").encode("utf-8")
