"""P71 T22 (was P69 T63): THE ROUTE MAP - routes lighting in turn with money on them, and the ping.

At 4e077e4 `tokens` on an arc and `ping` on a light, a stamp or an arc were ACCEPTED AND IGNORED (review finding 7's
class: `_validate_vecmap_species` returned [] for `tokens: {"n": 3}`, `tokens: "lots"` and `ping: "yes"`). These tests
pin the by-name refusal of every malformed or misplaced key the slice introduces (rule h, s106), the compiler's mirror
of the module's draw clock, the ping's measured dials (step 0: CHN 02:21.1, D40 13:56.5 - one pulse, never a repeating
sonar), the route token's look against T11's, the cards, and the golden. The tilted plane is DROPPED (VERIFY.md: BOOM's
map is flat): no `plane` key exists to test."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
import build_scene_timeline_f as B  # noqa: E402

VECMAP_MJS = "./content/video_engine/scripts/species/vecmap.mjs"
ENGINE = ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-engine.mjs"
CARDS = ROOT / "content" / "video_engine" / "effects" / "cards" / "species.json"
PLATE = "vecmap:KOR,CHN,VNM,TWN"


def arc(**extra) -> dict:
    """A route out of Korea, drawn on its word; the money starts on a later one."""
    entry = {"kind": "arc", "at": 6.0, "dur": 12.0, "from": {"kind": "country", "id": "KOR"},
             "to": {"kind": "country", "id": "VNM"}, "tokens": {"from_at": 7.9, "n": 2}}
    entry.update(extra)
    return entry


def place(kind: str, **extra) -> dict:
    entry = {"kind": kind, "at": 5.0, "dur": 10.0, "target": {"kind": "country", "id": "KOR"}, "ping": True}
    if kind == "stamp":
        entry["text"] = "customs"
    entry.update(extra)
    return entry


def errors(entry: dict) -> list[str]:
    return B.validate_species([entry], (0, 0, 0), PLATE)


def node_json(js: str):
    r = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------- the RED: the probe's three keys, now refused by name
def test_the_probed_keys_are_refused_by_name_not_accepted_and_ignored():
    assert any("tokens from_at must be a number" in e for e in errors(arc(tokens={"n": 3}))), errors(arc(tokens={"n": 3}))
    assert any("'tokens' must be a dict" in e for e in errors(arc(tokens="lots")))
    assert any("ping must be true or absent" in e for e in errors(place("light", ping="yes")))


# ---------------------------------------------------------------- the grammar
def test_a_route_with_tokens_and_a_pinging_place_validate_and_are_not_mutated():
    for entry in (arc(), arc(tokens={"from_at": 6.9}), arc(tokens={"from_at": 10.0, "n": 4, "speed": 300}),
                  arc(tokens={"from_at": 8.0}, crossed=11.0), place("light"), place("stamp")):
        before = copy.deepcopy(entry)
        assert errors(entry) == [], (entry, errors(entry))
        assert entry == before


def test_every_existing_vecmap_species_validates_as_it_did():
    plain = arc()
    del plain["tokens"]
    for entry in (plain, dict(plain, crossed=11.0), {k: v for k, v in place("light").items() if k != "ping"},
                  {k: v for k, v in place("stamp").items() if k != "ping"}):
        assert errors(entry) == [], errors(entry)


@pytest.mark.parametrize("extra, needle", [
    ({"tokens": "lots"}, "arc: 'tokens' must be a dict {from_at, n, speed}"),
    ({"tokens": [7.9]}, "arc: 'tokens' must be a dict"),
    ({"tokens": {"from_at": 7.9, "count": 3}}, "arc: tokens key 'count' is not one of from_at|n|speed"),
    ({"tokens": {"from_at": 7.9, "glyph": "coins"}}, "a route token is the plain dot; the sourced glyph is a flow's"),
    ({"tokens": {"from_at": 7.9, "n": 0}}, "arc: tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 7.9, "n": 5}}, "arc: tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 7.9, "n": 2.5}}, "arc: tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 7.9, "n": True}}, "arc: tokens n must be a whole number 1-4"),
    ({"tokens": {"from_at": 7.9, "speed": 10}}, "arc: tokens speed must be 60-900"),
    ({"tokens": {"from_at": 7.9, "speed": "fast"}}, "arc: tokens speed must be 60-900"),
    ({"tokens": {"n": 2}}, "arc: tokens from_at must be a number"),
    ({"tokens": {"from_at": True}}, "arc: tokens from_at must be a number"),
    ({"tokens": {"from_at": 6.5}}, "is before the route is drawn (6.900s)"),
    ({"tokens": {"from_at": 18.0}}, "falls outside the arc's window (6.0-18.0s)"),
    ({"tokens": {"from_at": 11.0}, "crossed": 11.0}, "the money stops when the flow is cut"),
    ({"tokens": {"from_at": 12.0}, "crossed": 11.0}, "the money stops when the flow is cut"),
    ({"ping": True}, "arc: ping is a place's (light | stamp)"),
])
def test_every_malformed_or_misplaced_route_key_is_refused_by_name(extra, needle):
    errs = errors(arc(**extra))
    assert any(needle in e for e in errs), (needle, errs)


@pytest.mark.parametrize("kind", ["light", "stamp"])
@pytest.mark.parametrize("value", ["yes", 1, 0, False, None, {"at": 9.0}, [True]])
def test_a_ping_is_true_or_absent(kind, value):
    errs = errors(place(kind, ping=value))
    assert any(f"{kind}: ping must be true or absent, not {value!r}" in e and "repeating sonar is not witnessed" in e
               for e in errs), errs


def test_the_compiler_mirrors_the_modules_draw_clock():
    got = node_json(f"import {{ ARC }} from '{VECMAP_MJS}'; console.log(JSON.stringify({{DRAW_S: ARC.DRAW_S}}));")
    assert got["DRAW_S"] == B.VECMAP_ARC_DRAW_S
    assert B.ARC_TOKEN_KEYS == ("from_at", "n", "speed")
    assert B.PING_KINDS == (B.SPECIES_LIGHT, B.SPECIES_STAMP)


# ---------------------------------------------------------------- the module: T11's law, the reference's ping
def test_the_route_token_rides_t11s_dials_and_look():
    got = node_json(f"import {{ arcTokenSpeed, PING, pingStyle }} from '{VECMAP_MJS}';"
                    "import { FLOW, flowTokenStyle } from './content/video_engine/scripts/species/flow.mjs';"
                    "console.log(JSON.stringify({ping: PING, style: pingStyle(), tok: flowTokenStyle(1, false),"
                    " fast: arcTokenSpeed({tokens: {from_at: 1, speed: 900}}, 100), floor: 100 / FLOW.TOKEN_MIN_CROSS_S,"
                    " slow: arcTokenSpeed({tokens: {from_at: 1, speed: 80}}, 1000), dflt: arcTokenSpeed({tokens: {from_at: 1}}, 1000),"
                    " TOKEN_SPEED: FLOW.TOKEN_SPEED}));")
    assert got["fast"] == pytest.approx(got["floor"]), "no route crossed faster than Bravos DOM's 0.49 s"
    assert got["slow"] == 80 and got["dflt"] == got["TOKEN_SPEED"]
    assert got["ping"] == {"LAG_S": 0.35, "EXPAND_S": 0.67, "R0": 27, "R1": 69, "FADE_POW": 3, "STROKE": 5,
                           "GLOW_PX": 18, "GLOW_A": 0.9, "GLOW_W": 9}   # P72 T46d (R26-383): the glow, measured off CHN 02:21.4
    assert "#F5B72E" in got["style"] and "#F5B72E" in got["tok"], "the ping and the token are in the route's ink"


def test_the_engine_carries_the_synced_module():
    eng = ENGINE.read_text(encoding="utf-8")
    region = eng[eng.index("/* KINETICS:BEGIN vecmap */"):]
    region = region[:region.index("/* KINETICS:END */")]
    for sym in ("const arcTokens", "const pingPose", '"vmtoken"', '"vmping"', "flowTokenStyle(1, false)"):
        assert sym in region, sym
    assert eng.index("/* KINETICS:BEGIN flow */") < eng.index("/* KINETICS:BEGIN vecmap */"), "flow's region is earlier - the import's order"


# ---------------------------------------------------------------- the cards
def _card(cid: str) -> dict:
    return next(c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"] if c["id"] == cid)


def test_the_cards_name_the_new_options_and_the_ruling_line():
    arc_card = _card("species:arc")
    assert [o["token"] for o in arc_card["options"]] == ["tokens"]
    assert arc_card["options"][0]["source_set"] == "ARC_TOKEN_KEYS"
    assert any(p["name"] == "tokens ride" and p["trigger"].startswith("`tokens.from_at`") for p in arc_card["phases"])
    assert "P71 T22" in arc_card["doctrine"]
    assert any("BRAVOS-USE-WHEN.md:527" in b["record"] for b in arc_card["blends"]), "the USE-WHEN the route map answers to"
    for cid in ("species:light", "species:stamp"):
        card = _card(cid)
        assert [o["token"] for o in card["options"]] == ["ping"], cid
        assert card["options"][0]["source_set"] == "PING_KINDS"
        assert any("BRAVOS-USE-WHEN.md:539" in b["record"] for b in card["blends"]), cid
        assert "P71 T22" in card["doctrine"]


# ---------------------------------------------------------------- the golden
def test_the_route_golden_is_registered_and_its_species_validate():
    import build_golden_sources as GS
    assert "vecmap-route-tokens" in GS.SURFACES and "vecmap-route-tokens" in GS.FRAME_T
    tl, _uris = GS.SURFACES["vecmap-route-tokens"]()
    sc = tl["scenes"][0]
    assert sc["world"]["kind"] == "vecmap" and sc["world"]["focus"] == ["KOR", "CHN", "VNM", "TWN"]
    assert B.validate_species(sc["species"], (0, 0, 0), PLATE) == []
    arcs = [s for s in sc["species"] if s["kind"] == "arc"]
    assert len(arcs) == 3 and [a["at"] for a in arcs] == sorted(a["at"] for a in arcs), "the routes light IN TURN"
    assert all("tokens" in a for a in arcs)
    assert sum(1 for s in sc["species"] if s.get("ping") is True) == 2


def test_the_golden_frame_holds_a_ping_in_flight_and_tokens_mid_route():
    import build_golden_sources as GS
    tl, _uris = GS.SURFACES["vecmap-route-tokens"]()
    t = GS.FRAME_T["vecmap-route-tokens"]
    pings = [s for s in tl["scenes"][0]["species"] if s.get("ping") is True]
    assert any(0.2 < (t - (s["at"] + 0.35)) / 0.67 < 0.8 for s in pings), "one pulse mid-flight at the judged instant"
    for a in (s for s in tl["scenes"][0]["species"] if s["kind"] == "arc"):
        assert a["tokens"]["from_at"] < t, "the money is moving at the judged instant"


def test_the_golden_sources_are_written_lf():
    for suffix in (".timeline.json", ".uris.json"):
        raw = (ROOT / "content/video_engine/tests/golden/sources" / f"vecmap-route-tokens{suffix}").read_bytes()
        assert b"\r" not in raw, suffix
