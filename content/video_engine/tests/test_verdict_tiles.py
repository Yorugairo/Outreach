"""P71 T19 (was P69 T60; the Bravos harvest v2 T26 "Mini-chart verdict tiles", R14 "Two verdict panels", A14, A59):
a CHART CARD dock carries a VERDICT - `verdict: {state: "tick" | "cross" | "buy" | "sell", at: <s>}` - a state on the
card painted by P71 T12's chip-state laws (one grammar): the badge spring lands it on its word; a tick is the check badge,
a cross the same disc in the negative ink with the X's two strokes, BUY / SELL the chip's tab in the sign inks.

At 42d0fab `dock_opts({"verdict": ...})` was REFUSED AS UNKNOWN ("dock option 'verdict' is not one of arrive|mass|...|
under"), the engine drew nothing, and the recipe `two-verdict-panels` did not exist. These tests pin: the option and every
by-name refusal it introduces (rule h, s106) - a key that is not state/at (a BUY / SELL tab is a scenario label, never a
trade record), a state or a second that is malformed, a verdict on a prop, a stamp, a cutout, a press card, a pile or a
card on a surface (a verdict tile is a state on a card, never a seal: E99 s121 / s128) and a tile whose chart is not drawn
from its own sourced series (the slice's constraint); the entry written only when the row names it (byte-identical
absent); the engine's placement against the reference [MEASURED: BUB frame_0095 - the disc 0.151 of the tile's width,
centred over it, its centre 0.342 diameters above the top edge; the tab lifted the same share of its own height]; the
landing on the word, pure in t; the state riding the tile across a park (the stop condition, answered); the golden's
words read off the take, never re-typed; and the recipe."""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "scripts"))
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests"))
sys.path.insert(0, str(ROOT / "content" / "video_engine" / "tests" / "golden"))
import build_scene_timeline_f as B  # noqa: E402

ENGINE = ROOT / "docs" / "content-video-engine" / "samples" / "scene-evidence-engine.mjs"
CARDS = ROOT / "content" / "video_engine" / "effects" / "cards" / "dock_option.json"
RECIPE = ROOT / "content" / "video_engine" / "effects" / "recipes" / "two-verdict-panels.json"
USE_WHEN = ROOT / "docs" / "research" / "bravos-style" / "BRAVOS-USE-WHEN.md"
GOLDEN = "verdict-tiles-three-questions"
# the reference [MEASURED: BUB frame_0095, scratchpad/p71-t19/logs/measure-bub-0095.json]: the disc 19 px on a 126 px tile,
# its centre 6.5 px above the top edge - the engine's DOCK_VERDICT dials are these two numbers
REF_D, REF_LIFT = round(19 / 126, 3), round(6.5 / 19, 3)
V = {"state": "tick", "at": 10.0}
LIVE_CHART = {"species": "chart", "title": "t", "source": "s", "badges": [],
              "chart": {"title": "t", "src": "Yahoo Finance", "series": [{"name": "a", "pts": [[0, 1], [1, 2]]}]}}
CARD_STILL = {"species": "chart", "title": "t", "source": "Yahoo Finance", "badges": [], "card": {"profile": "card"}}
PICTURE = {"species": "deck", "title": "t", "source": "s", "badges": []}


def _refusal(opts: dict) -> str:
    with pytest.raises(ValueError) as e:
        B.dock_opts(opts)
    return str(e.value)


# ------------------------------------------------------------------ the option
def test_verdict_is_a_dock_option_with_four_states():
    assert "verdict" in B.DOCK_OPTS
    assert B.DOCK_VERDICTS == ("tick", "cross", "buy", "sell")
    for s in B.DOCK_VERDICTS:
        assert B.dock_opts({"verdict": {"state": s, "at": 12.5}}) == {"verdict": {"state": s, "at": 12.5}}
    both = {"centre": True, "centre_w": 0.4, "card_aspect": 0.62, "under": "hover", "verdict": dict(V)}
    assert B.dock_opts(both) == both


@pytest.mark.parametrize("bad", ["tick", ["tick", 10.0], 10.0, None, True])
def test_a_verdict_that_is_not_a_dict_is_refused_by_name(bad):
    msg = _refusal({"verdict": bad})
    assert "verdict" in msg and "state" in msg and "at" in msg, msg


@pytest.mark.parametrize("state", ["pass", "TICK", "check", "hold", "", 1, None, "crossed"])
def test_a_state_that_is_not_one_of_four_is_refused_by_name(state):
    msg = _refusal({"verdict": {"state": state, "at": 10.0}})
    assert "verdict state" in msg and "tick|cross|buy|sell" in msg, msg


@pytest.mark.parametrize("at", [None, True, -0.1, "10", float("nan"), float("inf")])
def test_an_at_that_is_not_a_second_is_refused_by_name(at):
    v = {"state": "tick"} if at is None else {"state": "tick", "at": at}
    msg = _refusal({"verdict": v})
    assert "verdict at" in msg and "word" in msg, msg


@pytest.mark.parametrize("key", ["price", "label", "qty", "size", "date", "seal", "tab_at"])
def test_a_key_beyond_state_and_at_is_refused_by_name_never_a_trade_record(key):
    msg = _refusal({"verdict": dict(V, **{key: 1})})
    assert repr(key) in msg and "state|at" in msg and "never a trade record" in msg, msg


@pytest.mark.parametrize("other,opts", [
    ("prop", {"prop": True}),
    ("stamp", {"arrive": "stamp"}),
    ("cutout", {"cutout": True}),
    ("press", {"press": {"source": "s", "phrase": "p"}}),
    ("embed", {"embed": "screen"}),
])
def test_a_verdict_is_a_state_on_a_card_never_a_seal(other, opts):
    msg = _refusal(dict(opts, verdict=dict(V)))
    assert f"verdict and {other} cannot be combined" in msg and "never a seal" in msg, msg


def test_the_verdict_does_not_collide_with_the_dock_seal_refusal():
    """P70 T1b's DOCK_SEAL_REFUSED (a dock stamp asking for a seal) is untouched, and `verdict` is not in it."""
    assert B.DOCK_SEAL_REFUSED == ("ring_text", "ring_text_bottom", "seal")
    assert "verdict" not in B.DOCK_SEAL_REFUSED
    assert "a dock stamp carries no seal" in _refusal({"seal": True})


# ------------------------------------------------------------------ the tile's chart and its word
def test_a_tile_is_a_chart_drawn_from_its_own_sourced_series():
    assert B.verdict_tile_error(LIVE_CHART, V, 5.0, 20.0) is None
    assert B.verdict_tile_error(CARD_STILL, V, 5.0, 20.0) is None
    msg = B.verdict_tile_error(PICTURE, V, 5.0, 20.0)
    assert msg and "sourced series" in msg, msg
    unsourced = dict(LIVE_CHART, source="", chart=dict(LIVE_CHART["chart"], src=""))
    assert "sourced series" in (B.verdict_tile_error(unsourced, V, 5.0, 20.0) or "")
    empty = dict(LIVE_CHART, chart={"title": "t", "src": "s"})
    assert "sourced series" in (B.verdict_tile_error(empty, V, 5.0, 20.0) or "")


@pytest.mark.parametrize("at", [4.99, 20.0, 25.0])
def test_a_verdict_lands_inside_its_tiles_life(at):
    msg = B.verdict_tile_error(LIVE_CHART, dict(V, at=at), 5.0, 20.0)
    assert msg and "outside the tile's life" in msg and "5.0" in msg and "20.0" in msg, msg


def test_the_entry_carries_the_verdict_only_when_the_row_names_it():
    place = {"x": 100.0, "y": 100.0, "w": 700.0, "h": 434.0}
    plain = B.dock_entry("ev-a", 0, 5.0, 20.0, 0, B.DOCK_KIND_IMAGE, place, None, None, True)
    again = B.dock_entry("ev-a", 0, 5.0, 20.0, 0, B.DOCK_KIND_IMAGE, place, None, None, True, verdict=None)
    assert plain == again and "verdict" not in plain
    named = B.dock_entry("ev-a", 0, 5.0, 20.0, 0, B.DOCK_KIND_IMAGE, place, None, None, True,
                         verdict={"state": "sell", "at": 12.3456})
    assert named["verdict"] == {"state": "sell", "at": 12.35}
    assert {k: v for k, v in named.items() if k != "verdict"} == plain


# ------------------------------------------------------------------ the golden, on the take's words
@pytest.fixture(scope="module")
def GS():
    import build_golden_sources as gs
    return gs


def _take_word(phrase: str, k: int = 0) -> float:
    words = json.loads((ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper/vo-h-scratch/"
                               "scratch-kokoro.words.json").read_text(encoding="utf-8"))["words"]
    toks = phrase.lower().split()
    norm = [w["w"].lower().strip(".,:;?!—–-") for w in words]
    for i in range(len(norm) - len(toks) + 1):
        if norm[i:i + len(toks)] == toks and words[i]["start_s"] > 460:
            return float(words[i + k]["start_s"])
    raise AssertionError(f"{phrase!r} is not in the take")


def test_the_golden_lands_each_verdict_on_its_word_read_off_the_take(GS):
    tl, _uris = GS.SURFACES[GOLDEN]()
    docks = tl["scenes"][0]["docks"]
    assert len(docks) == 2 and [d["slot"] for d in docks] == [0, 1], "two tiles, one per slot"
    shift = GS.VT_SHIFT
    assert shift == round(_take_word("one is what") - 0.3, 2), "the clock: \"One:\", right after the ask, at 0.3 s"
    assert _take_word("ask it three questions") < _take_word("one is what"), "the ask comes first"
    for d, (enter_w, verdict_w) in zip(docks, GS.VT_WORDS):
        assert d["enter"] == round(_take_word(*enter_w) - shift, 2), (d, enter_w)
        assert d["verdict"] == {"state": "tick", "at": round(_take_word(*verdict_w) - shift, 2)}, (d, verdict_w)
        ev = tl["evidence"][d["slide"]]
        assert B.verdict_tile_error(ev, d["verdict"], d["enter"], d["exit"]) is None, "each tile draws its own sourced series"
    frame_t = GS.FRAME_T[GOLDEN]
    assert frame_t > max(d["verdict"]["at"] for d in docks) + 0.55 + 0.5 and frame_t < GS.RUNTIME, "read with both landed"


def test_the_golden_is_registered_and_pinned():
    import test_golden_frames as TG
    assert GOLDEN in TG.SURFACES
    assert (ROOT / "content/video_engine/tests/golden/frames" / f"{GOLDEN}.png").exists()


# ------------------------------------------------------------------ the engine
def _chromium() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except Exception:
        return False


needs_chromium = pytest.mark.skipif(not _chromium(), reason="chromium not available")

_PROBE = """(slot) => {
  const s = document.getElementById('stage').getBoundingClientRect();
  const el = document.getElementById('dock-' + (slot + 1)); const b = el.getBoundingClientRect();
  const vs = el.querySelector(':scope > .dock-verdict');
  const out = {tile: {x: b.x - s.x, y: b.y - s.y, w: b.width, h: b.height}, overflow: el.style.overflow,
               mounted: !!vs, state: vs ? vs.getAttribute('data-state') : null, disc: null, tab: null, marks: []};
  if (!vs) return out;
  const disc = vs.querySelector('circle');
  if (disc) { const r = disc.getBoundingClientRect(); out.disc = {cx: r.x + r.width / 2 - s.x, cy: r.y + r.height / 2 - s.y,
    d: r.width, fill: disc.style.fill, op: +(disc.closest('g').getAttribute('opacity'))}; }
  const tab = vs.querySelector('rect');
  if (tab) { const r = tab.getBoundingClientRect(); const lab = vs.querySelector('text');
    out.tab = {cx: r.x + r.width / 2 - s.x, cy: r.y + r.height / 2 - s.y, w: r.width, h: r.height, fill: tab.style.fill,
               word: lab ? lab.textContent : null, size: lab ? parseFloat(lab.style.fontSize) : null}; }
  out.marks = [...vs.querySelectorAll('path')].map((p) => +p.getAttribute('stroke-dashoffset'));
  return out; }"""


def _probe(tl: dict, uris: dict, ts: list[float], slots=(0, 1), shots: bool = False) -> list:
    """At each t (seeked in order, on ONE page): each slot's tile box and its verdict layer; with `shots`, the frame too."""
    import render_baseline as RB
    import served_player as SP
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "verdict.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            for t in ts:
                png = RB.frame_png(page, t, (w, h))
                row = [page.evaluate(_PROBE, s) for s in slots]
                out.append((row, png) if shots else row)
            assert not errs, errs
    return out


@pytest.fixture(scope="module")
def golden_probe(GS):
    tl, uris = GS.SURFACES[GOLDEN]()
    docks = tl["scenes"][0]["docks"]
    ats = [d["verdict"]["at"] for d in docks]
    ts = [ats[0] - 0.05, ats[0] + 0.2, ats[0] + 0.55 + 0.05, GS.FRAME_T[GOLDEN], ats[0] + 0.2, GS.FRAME_T[GOLDEN]]
    return ts, _probe(tl, uris, ts, shots=True)


@needs_chromium
def test_the_disc_sits_where_the_reference_puts_it(GS, golden_probe):
    ts, rows = golden_probe
    (tiles, _png) = rows[3]
    for p in tiles:
        tile, disc = p["tile"], p["disc"]
        assert p["mounted"] and p["state"] == "tick" and disc, p
        d = REF_D * tile["w"]
        assert abs(disc["d"] - d) <= 1.0, f"the disc is {REF_D} of the tile's width: {disc['d']:.1f} vs {d:.1f}"
        assert abs(disc["cx"] - (tile["x"] + tile["w"] / 2)) <= 1.0, "centred over the tile"
        assert abs(disc["cy"] - (tile["y"] - REF_LIFT * d)) <= 1.5, \
            f"its centre {REF_LIFT} diameters above the top edge: {disc['cy']:.1f} vs {tile['y'] - REF_LIFT * d:.1f}"
        assert disc["fill"] in ("rgb(61, 220, 132)", "#3DDC84", "#3ddc84"), "the positive ink (T12's TICK_INK)"
        assert p["overflow"] == "visible"


@needs_chromium
def test_each_verdict_lands_on_its_word_on_the_badge_spring(golden_probe):
    ts, rows = golden_probe
    before, rising, settled = rows[0][0][0], rows[1][0][0], rows[2][0][0]
    assert before["mounted"] and before["disc"] is None, "before its word nothing of the state is drawn"
    assert 0 < rising["disc"]["op"] <= 1 and rising["marks"], "0.2 s into its word the badge is landing, the check drawing"
    assert settled["disc"]["op"] == 1 and all(m == 0 for m in settled["marks"]) and len(settled["marks"]) == 2, \
        "LAND_S after its word the badge has landed and the check's two strokes are whole"
    second_before = rows[1][0][1]
    assert second_before["disc"] is None, "the second tile's verdict waits for ITS word"


@needs_chromium
def test_the_verdict_is_pure_in_t(golden_probe):
    ts, rows = golden_probe
    assert rows[1][0] == rows[4][0], "a seek back to the landing reads the same state"
    assert rows[3][0] == rows[5][0] and rows[3][1] == rows[5][1], "a seek back to the frame reads the same bits"


@needs_chromium
@pytest.mark.parametrize("state", ["buy", "sell"])
def test_a_buy_or_sell_tab_is_the_chips_tab_lifted_over_the_top_edge(GS, state):
    """The chip's tab (its word at the s90 floor, the sign inks), lifted as the disc is - LIFT of its own height above the
    edge: centred ON the edge it covered the middle of the chart card's own title (the first frame read)."""
    at = 8.0
    tl, uris = GS.verdict_tiles_surface((state,), ats=(at,))
    [[p]] = _probe(tl, uris, [at + 0.9], slots=(0,))
    tab, tile = p["tab"], p["tile"]
    assert tab and tab["word"] == state.upper() and tab["size"] >= 59.08, p
    assert tab["fill"] in ({"buy": ("rgb(61, 220, 132)", "#3DDC84"), "sell": ("rgb(255, 77, 77)", "#FF4D4D")}[state]), tab
    assert abs(tab["cx"] - (tile["x"] + tile["w"] / 2)) <= 1.0, "centred over the tile"
    assert abs(tab["cy"] - (tile["y"] - REF_LIFT * tab["h"])) <= 1.5, f"lifted {REF_LIFT} of its height above the edge: {tab}"
    assert tab["cy"] + tab["h"] / 2 - tile["y"] <= 0.2 * tab["h"], "it overlaps the edge by a sliver, never the title band"


@needs_chromium
def test_a_cross_is_the_disc_in_the_negative_ink_with_the_xs_two_strokes(GS):
    at = 8.0
    tl, uris = GS.verdict_tiles_surface(("cross",), ats=(at,))
    [[p]] = _probe(tl, uris, [at + 0.9], slots=(0,))
    assert p["disc"]["fill"] in ("rgb(255, 77, 77)", "#FF4D4D") and len(p["marks"]) == 2 and all(m == 0 for m in p["marks"]), p


@needs_chromium
def test_the_state_rides_the_tile_across_a_park(GS):
    """The stop condition, answered: the park writes the dock element's own box, so the state is anchored on the tile
    at its reading size and at its parked place alike."""
    at = 2.2   # 0.2 s into the tile's read (it enters at 2.0, reads DOCK_READ_S, then parks over DOCK_PARK_S)
    tl, uris = GS.verdict_tiles_surface(("tick",), ats=(at,), park=True)
    d = tl["scenes"][0]["docks"][0]
    t_read, t_park = at + 0.8, d["enter"] + d["read_s"] + d["park_s"] + 0.3
    assert t_read < d["enter"] + d["read_s"] and t_park < d["exit"] and d["park"]
    rows = _probe(tl, uris, [t_read, t_park], slots=(0,))
    widths = []
    for [p] in rows:
        tile, disc = p["tile"], p["disc"]
        dd = REF_D * tile["w"]
        assert abs(disc["cx"] - (tile["x"] + tile["w"] / 2)) <= 1.5 and abs(disc["cy"] - (tile["y"] - REF_LIFT * dd)) <= 2.0, p
        widths.append(tile["w"])
    assert widths[1] < 0.8 * widths[0], f"the tile really parked smaller: {widths}"


@needs_chromium
def test_a_tile_with_no_verdict_mounts_nothing_and_a_reused_slot_drops_the_last_ones(GS):
    tl, uris = GS.verdict_tiles_surface((None,), ats=(None,))
    [[p]] = _probe(tl, uris, [9.0], slots=(0,))
    assert not p["mounted"] and p["overflow"] == "", p
    # the same slot: a verdict tile, then a plain card
    tl, uris = GS.verdict_tiles_surface(("tick", None), ats=(6.0, None))
    sc = tl["scenes"][0]
    first, second = sc["docks"]
    first["exit"] = 12.0
    second.update(slot=0, place=dict(first["place"]), enter=13.0, exit=GS.RUNTIME)   # another document takes slot 0
    assert "verdict" not in second
    a, b = _probe(tl, uris, [9.0, 16.0], slots=(0,))
    assert a[0]["mounted"] and not b[0]["mounted"] and b[0]["overflow"] == "", (a, b)


# ------------------------------------------------------------------ the engine's one call line
def test_the_engines_dials_are_the_references():
    import re
    src = ENGINE.read_text(encoding="utf-8")
    block = src[src.index("const DOCK_VERDICT = Object.freeze({"):]
    block = block[:block.index("});")]
    dial = lambda name: float(re.search(r"\s" + name + r": ([0-9.]+),", block).group(1))  # noqa: E731
    assert dial("D") == REF_D == 0.151
    assert dial("LIFT") == REF_LIFT == 0.342
    states = re.search(r"STATES: Object.freeze\(\[([^\]]+)\]\)", block).group(1)
    assert [x.strip().strip('"') for x in states.split(",")] == list(B.DOCK_VERDICTS), "the engine's states are the compiler's"


def test_the_engine_paints_the_verdict_from_one_line_after_the_hover():
    src = ENGINE.read_text(encoding="utf-8")
    assert src.count("paintDockVerdict(el, d, t);") == 1
    render = src.index("const render = (t) => {")
    call, hover = src.index("paintDockVerdict(el, d, t);"), src.index("const hov = dockHover(d, t, dockContactAt(d));")
    assert render < hover < call, "the one call line sits in render()'s dock loop, after T15's hover lines"


# ------------------------------------------------------------------ the card and the recipe
def test_the_dock_option_card_names_the_verdict_and_its_four_states():
    cards = {c["id"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    card = cards["dock_option:verdict"]
    assert card["token"] == "verdict" and [o["token"] for o in card["options"]] == list(B.DOCK_VERDICTS)
    assert card["proof"]["golden"] == GOLDEN and card["lives"]["symbol"] == "paintDockVerdict"


def test_the_two_panel_recipe_carries_r14s_use_when():
    r = json.loads(RECIPE.read_text(encoding="utf-8"))
    assert r["id"] == "recipe:two-verdict-panels" and r["status"] == "candidate" and r["count"] == 0
    assert [m["card"] for m in r["members"]] == ["dock_option:verdict", "dock_option:verdict"]
    uw = USE_WHEN.read_text(encoding="utf-8")
    assert "the close rejects two strategies side by side." in uw and "either option is left unexplained." in uw
    assert r["use_when"]["use"].startswith("the close rejects two strategies side by side")
    assert r["use_when"]["dont"].startswith("either option is left unexplained")


@needs_chromium
def test_the_two_panel_recipe_is_proved_two_tiles_side_by_side_each_on_its_word(GS):
    """R14 as a beat: two tiles side by side, each rejecting its option with a cross on its own word - disjoint, both on
    the stage, the second's cross waiting for its word."""
    tl, uris = GS.verdict_tiles_surface(("cross", "cross"), ats=(8.0, 11.0))
    mid, end = _probe(tl, uris, [9.2, 12.2])
    (a, b), (a2, b2) = mid, end
    assert a["disc"] and b["disc"] is None and a2["disc"] and b2["disc"], (mid, end)
    ta, tb = a2["tile"], b2["tile"]
    assert ta["x"] + ta["w"] < tb["x"], "side by side, disjoint"
    assert ta["x"] >= 0 and tb["x"] + tb["w"] <= 1920 and min(a2["disc"]["cy"], b2["disc"]["cy"]) - a2["disc"]["d"] / 2 >= 0
