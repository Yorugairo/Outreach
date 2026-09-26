"""P72 T19 - docks keep their box, leave with the dip, ride a park; the hatch rides the dock's camera; a press card holds.

R26-328  a card docked again on the next scene under the SAME asset id drew at the previous scene's box: the coalescer
         (DOCK_JOIN) merged two dockings of one id less than 2.5 s apart into one span and kept the FIRST's place, whatever
         the second's box, and on either slot. A docking at a different box is a new docking now; one at the same box
         still holds through the boundary (the coalescer's own case). H row 23's workaround (`dock-h-railway-share-ring`,
         a second id for the same certificate) is no longer needed - the same id renders the workaround's frames.
R26-285  a dip leaves the outgoing docks standing: the engine snaps a card's exit within 1.4 s of a boundary ONTO it and
         only a WIPE sweeps it with the front, so the card retracted over the incoming scene as the dip rose. A dip now
         takes the docks that end on its boundary with its black (and their wash); and the snap never moves an exit
         across a landing in the same slot (the card that lands there is the one shown).
R26-271  the prop's hatch lines stood in screen pixels while the dock's camera (a depth dock's plane, the camera
         arrival's prefix) zoomed or panned the prop: the lines swam across it. The hatch is fixed to the PAGE - it
         rides the dock camera's transform - and takes the arrival's blur with the mark.
R26-320  the drift-hold (`idle: hold`) never reached a PRESS card: the compiler accepted the key and the pile painter
         ignored it. A held press card drifts on its own span and carries the hold's light band.
R26-267  `rel: {pin: <dock>}` - the relation layer's first verb (E97): a dock parented to another dock's pose, so a stamp
         lands ON a card on its own word and rides the card's read-then-park. Translation by default (E97: "a pinned
         child inherits TRANSLATION only; widen explicitly"), `inherit: ["translate", "scale"]` to shrink with it. The
         target is refused by name when it is absent or docks later; the other E97 verbs are refused by name.
R26-202 (b) the throw's entry side was the engine's `flip++ % 2`, unauthorable: `side: left|right|bottom` on a throw
         enters from that EDGE of the stage; `top` is refused by name (a card from above is a drop). A throw with no
         side keeps the alternation, byte-identical.
R26-343  a park did not scale the page's legend chips (the long form's key rail): they ride the park now, about the
         chart's own anchor.
"""
from __future__ import annotations

import io
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
ARRIVAL_CARDS = ROOT / "content/video_engine/effects/cards/arrival.json"
DOCK_CARDS = ROOT / "content/video_engine/effects/cards/dock_option.json"
W16, H16 = 1920, 1080


# =============================================================================================== the compiler (fast)
# ---- R26-202 (b): the throw's side ----------------------------------------------------------------------------------
@pytest.mark.parametrize("side", ["left", "right", "bottom"])
def test_side_is_a_throws_entry_side(side):
    assert "side" in B.DOCK_OPTS and B.THROW_SIDES == ("left", "right", "bottom")
    assert B.dock_opts({"arrive": "throw", "side": side})["side"] == side


def test_side_top_is_refused_by_name():
    with pytest.raises(ValueError, match=r"^dock: side 'top'") as e:
        B.dock_opts({"arrive": "throw", "side": "top"})
    assert "land" in str(e.value), "the refusal names what a card from above is: a drop (arrive=land)"


@pytest.mark.parametrize("bad", ["up", "", 1, None, True, ["left"], "Left"])
def test_a_malformed_side_is_refused_by_name(bad):
    with pytest.raises(ValueError, match=r"^dock: side") as e:
        B.dock_opts({"arrive": "throw", "side": bad})
    assert "is not one of arrive" not in str(e.value), "refused BY NAME, not as an unknown key"


@pytest.mark.parametrize("raw", [{"side": "left"}, {"arrive": "land", "side": "left"}, {"arrive": "stamp", "side": "right"},
                                 {"arrive": "throw", "side": "left", "press": {"source": "s", "phrase": {}}}])
def test_side_off_a_throw_is_refused_by_name(raw):
    with pytest.raises(ValueError, match=r"^dock: side"):
        B.dock_opts(raw)


def test_the_entry_carries_the_side_only_when_authored():
    place = {"x": 1400, "y": 300, "w": 400, "h": 300}
    plain = B.dock_entry("ev-a", 0, 1.0, 5.0, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", True)
    assert "throw_side" not in plain, "a throw that names no side is the entry it always was"
    got = B.dock_entry("ev-a", 0, 1.0, 5.0, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", True, throw_side="right")
    assert got["throw_side"] == "right" and {k: v for k, v in got.items() if k != "throw_side"} == plain


# ---- R26-267: rel: pin -------------------------------------------------------------------------------------------------
def test_rel_pin_is_a_dock_option():
    assert "rel" in B.DOCK_OPTS and B.REL_VERBS == ("pin",) and B.REL_INHERIT == ("translate", "scale")
    got = B.dock_opts({"rel": {"pin": "dock-h-sell-ticket"}, "centre": True})
    assert got["rel"] == {"pin": "dock-h-sell-ticket"}
    got = B.dock_opts({"rel": {"pin": "t", "inherit": ["translate", "scale"]}, "prop": True, "arrive": "stamp",
                       "place": {"x": 0.5, "y": 0.5, "w": 0.1}})
    assert got["rel"]["inherit"] == ["translate", "scale"]


@pytest.mark.parametrize("bad", ["t", None, [], {}, {"pin": ""}, {"pin": 3}, {"pin": "t", "inherit": "scale"},
                                 {"pin": "t", "inherit": ["scale"]}, {"pin": "t", "inherit": ["translate", "rotate"]},
                                 {"pin": "t", "inherit": ["translate", "translate"]}, {"pin": "t", "at": 3.0}])
def test_a_malformed_rel_is_refused_by_name(bad):
    with pytest.raises(ValueError, match=r"^dock: rel") as e:
        B.dock_opts({"rel": bad, "centre": True})
    assert "is not one of arrive" not in str(e.value), "refused BY NAME, not as an unknown key"


@pytest.mark.parametrize("verb", ["aim", "group", "path", "derive", "camera", "weight", "parent"])
def test_the_other_relation_verbs_are_refused_by_name_as_not_built(verb):
    with pytest.raises(ValueError, match=r"^dock: rel") as e:
        B.dock_opts({"rel": {verb: "t"}, "centre": True})
    assert verb in str(e.value) and "pin" in str(e.value) and "E97" in str(e.value)


@pytest.mark.parametrize("other", [{"press": {"source": "s", "phrase": {}}}, {"embed": "tv"}, {"park_at": {"datum": 3}},
                                   {"moves": [{"at": 1.0, "x": 0.5, "y": 0.5}]}])
def test_rel_beside_another_placement_is_refused_by_name(other):
    raw = dict({"rel": {"pin": "t"}, "centre": True}, **other)
    with pytest.raises(ValueError, match=r"^dock: rel"):
        B.dock_opts(raw)


def test_a_pinned_dock_needs_a_box_of_its_own():
    with pytest.raises(ValueError, match=r"^dock: rel") as e:
        B.dock_opts({"rel": {"pin": "t"}})
    assert "place" in str(e.value) and "centre" in str(e.value)


def _pin_scenes(target_enter: float, target_exit: float, child_enter: float, target: str = "ev-ticket",
                target_place: bool = True) -> list[dict]:
    t = {"slide": "ev-ticket", "slot": 0, "enter": target_enter, "exit": target_exit}
    if target_place:
        t["place"] = {"x": 100, "y": 100, "w": 400, "h": 300}
    c = {"slide": "ev-sell", "slot": 1, "enter": child_enter, "exit": target_exit, "place": {"x": 200, "y": 200, "w": 100, "h": 50},
         "rel": {"pin": target}}
    return [{"scene_id": "s01", "span": [0.0, 30.0], "docks": [t, c]}]


def test_a_pin_to_a_live_placed_dock_is_clean():
    assert B.dock_pin_errors(_pin_scenes(2.0, 20.0, 5.0)) == []


@pytest.mark.parametrize("scenes, word", [
    (lambda: _pin_scenes(2.0, 20.0, 5.0, target="ev-nothing"), "absent"),
    (lambda: _pin_scenes(6.0, 20.0, 5.0), "later"),
    (lambda: _pin_scenes(1.0, 4.0, 5.0), "absent"),     # the target has left before the child lands
    (lambda: _pin_scenes(2.0, 20.0, 5.0, target_place=False), "placed"),
])
def test_a_pin_to_an_absent_later_or_unplaced_dock_is_refused_by_name(scenes, word):
    errs = B.dock_pin_errors(scenes())
    assert len(errs) == 1 and "rel.pin" in errs[0] and word in errs[0] and "ev-sell" in errs[0], errs


def test_the_main_loop_writes_side_and_rel_and_checks_the_pins():
    src = COMPILER.read_text(encoding="utf-8")
    assert re.search(r"docks\.append\(dock_entry\([^;]*?throw_side=dopt\.get\(\"side\"\)", src, re.S)
    assert re.search(r"docks\.append\(dock_entry\([^;]*?rel=dopt\.get\(\"rel\"\)", src, re.S)
    assert "dock_pin_errors(scenes)" in src, "the pins are checked across the whole cut (a target may be on another row)"
    got = B.dock_entry("ev-a", 1, 5.0, 9.0, 0, B.DOCK_KIND_IMAGE, {"x": 1, "y": 2, "w": 3, "h": 4}, centre=True,
                       rel={"pin": "ev-t"})
    assert got["rel"] == {"pin": "ev-t", "inherit": ["translate"]}, "the default is written out: translation only (E97)"
    assert "rel" not in B.dock_entry("ev-a", 1, 5.0, 9.0, 0, B.DOCK_KIND_IMAGE, {"x": 1, "y": 2, "w": 3, "h": 4}, centre=True)


def test_the_cards_carry_the_side_and_the_pin():
    arr = {c["id"]: c for c in json.loads(ARRIVAL_CARDS.read_text(encoding="utf-8"))["cards"]}
    assert [o["token"] for o in arr["arrival:throw"].get("options", []) if o.get("source_set") == "THROW_SIDES"] == list(B.THROW_SIDES)
    dk = {c["id"]: c for c in json.loads(DOCK_CARDS.read_text(encoding="utf-8"))["cards"]}
    assert "dock_option:rel" in dk and [o["token"] for o in dk["dock_option:rel"]["options"]] == ["pin"]


# =============================================================================================== the engine (frames)
def _chromium() -> bool:
    try:
        import served_player as SP
        with SP.browser():
            return True
    except Exception:  # noqa: BLE001 - no browser on this machine: the frame tests skip, never pass
        return False


needs_chromium = pytest.mark.skipif(not _chromium(), reason="chromium not available")


@pytest.fixture(scope="module")
def GS():
    import build_golden_sources as gs
    return gs


PLACE_A = {"x": 100, "y": 120, "w": 400, "h": 300}
PLACE_B = {"x": 1300, "y": 620, "w": 400, "h": 300}
KIN = {"stop_action": True, "camera": True}


def _plate(sid: str, a: float, b: float, docks: list[dict], exit_: str = "cut", species: list | None = None) -> dict:
    return {"scene_id": sid, "world": {"asset_id": "plate-plain", "sha256": "0" * 64, "ken_burns": {"scale": 0, "x": 0, "y": 0}},
            "exit": exit_, "span": [a, b], "docks": docks, "species": species or []}


def _card_ev(GS, aid: str, rgb: tuple[int, int, int], w: int = 400, h: int = 300) -> tuple[dict, str]:
    ev = {"title": aid, "source": "P72 T19", "species": "deck", "document": {"path": "golden", "sha256": "0" * 64}, "badges": []}
    return ev, GS.uri("image/png", GS.png_solid(w, h, rgb))


def _placed(aid: str, slot: int, enter: float, exit_: float, place: dict, **kw) -> dict:
    """A centred card at `place` - the entry the compiler writes; `throw_side` is written as the compiler writes it (the
    engine beds read the ENGINE, so they run on any compiler)."""
    side = kw.pop("throw_side", None)
    d = B.dock_entry(aid, slot, enter, exit_, 0, B.DOCK_KIND_IMAGE, place, kw.pop("arrive", None), kw.pop("mass", None),
                     True, **kw)
    return dict(d, throw_side=side) if side else d


def _tl(GS, title: str, scenes: list[dict], cards: dict, kinetics: dict | None = None) -> tuple[dict, dict]:
    ev, uris = {}, GS._base_uris()
    for aid, (e, u) in cards.items():
        ev[aid], uris[aid] = e, u
    tl = GS._timeline("P72 T19: " + title, scenes, ev, None)
    tl["kinetics"] = dict(kinetics or KIN)
    return tl, uris


READ = """() => {
  const s = document.getElementById('stage').getBoundingClientRect(), k = 1920 / s.width;
  const box = (e) => { const b = e.getBoundingClientRect(); return [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k]; };
  const slot = (n) => { const el = document.getElementById('dock-' + n);
    return {slide: el.dataset.slide || null, left: parseFloat(el.style.left), top: parseFloat(el.style.top), width: parseFloat(el.style.width),
            opacity: +getComputedStyle(el).opacity, visibility: getComputedStyle(el).visibility, transform: el.style.transform,
            box: box(el), light: (() => { const l = el.querySelector(':scope > .dock-hold-light'); return l && l.style.display !== 'none' ? l.style.background : null; })()}; };
  const press = [...document.querySelectorAll('.dock.press')].map((el) => ({id: el.id, transform: el.style.transform,
    opacity: +el.style.opacity, light: (() => { const l = el.querySelector(':scope > .dock-hold-light'); return l && l.style.display !== 'none' ? l.style.background : null; })()}));
  const wash = document.getElementById('wash');
  return {s1: slot(1), s2: slot(2), press, wash: wash ? wash.classList.contains('on') : null,
          dip: +getComputedStyle(document.getElementById('dipveil')).opacity};
}"""


def _frames(tl: dict, uris: dict, ts: list[float], js: str = READ, png: bool = True) -> list[tuple[bytes | None, dict]]:
    import render_baseline as RB
    import served_player as SP
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out = []
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "t19.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SP.served(html, w, h) as (page, errs):
            for t in ts:
                shot = RB.frame_png(page, t, (w, h))
                out.append((shot if png else None, page.evaluate(js)))
            assert not errs, errs
    return out


# ---- R26-328: the same id docks at the new scene's box ----------------------------------------------------------------
def _same_id_bed(GS, second: str = "ev-cert") -> tuple[dict, dict]:
    card = _card_ev(GS, "ev-cert", (23, 105, 194))
    s1 = _plate("s01", 0.0, 6.0, [_placed("ev-cert", 0, 1.0, 4.0, PLACE_A)])        # leaves 2.0 s before the turn: no snap
    s2 = _plate("s02", 6.0, GS.RUNTIME, [_placed(second, 0, 6.2, 14.0, PLACE_B)])   # ... and docks again 2.2 s later
    return _tl(GS, "the same id on the next scene", [s1, s2], {"ev-cert": card, second: card})


@needs_chromium
def test_a_card_docked_again_under_the_same_id_draws_at_the_new_scenes_box(GS):
    tl, uris = _same_id_bed(GS)
    (_p, a), (_p2, b) = _frames(tl, uris, [3.0, 10.0], png=False)
    assert (a["s1"]["left"], a["s1"]["top"], a["s1"]["width"]) == (PLACE_A["x"], PLACE_A["y"], PLACE_A["w"]), a["s1"]
    assert (b["s1"]["left"], b["s1"]["top"], b["s1"]["width"]) == (PLACE_B["x"], PLACE_B["y"], PLACE_B["w"]), \
        "the second docking is at ITS scene's box (R26-328: it drew at the first's)"


@needs_chromium
def test_row_23s_workaround_is_no_longer_needed_the_same_id_renders_the_second_ids_frames(GS):
    ts = [4.3, 5.0, 6.1, 6.5, 7.2, 10.0]
    same = _frames(*_same_id_bed(GS), ts)
    work = _frames(*_same_id_bed(GS, second="ev-cert-ring"), ts)
    for t, (pa, _a), (pb, _b) in zip(ts, same, work):
        assert pa == pb, f"t={t}: the same id and the workaround's second id render different frames"


@needs_chromium
def test_a_card_at_the_same_box_still_holds_through_the_boundary(GS):
    """The coalescer's own case stands: one document authored as a dock per scene at ONE box never leaves."""
    card = _card_ev(GS, "ev-cert", (23, 105, 194))
    s1 = _plate("s01", 0.0, 6.0, [_placed("ev-cert", 0, 1.0, 4.0, PLACE_A)])
    s2 = _plate("s02", 6.0, GS.RUNTIME, [_placed("ev-cert", 0, 6.2, 14.0, PLACE_A)])
    tl, uris = _tl(GS, "the same box", [s1, s2], {"ev-cert": card})
    got = [j["s1"] for _p, j in _frames(tl, uris, [4.5, 5.2, 6.1], png=False)]
    assert all(g["slide"] == "ev-cert" and g["opacity"] > 0.99 and g["left"] == PLACE_A["x"] for g in got), got


# ---- R26-285: a dip takes the outgoing docks ---------------------------------------------------------------------------
def _dip_bed(GS, exit_: str = "dip", leave: float = 5.0) -> tuple[dict, dict]:
    card = _card_ev(GS, "ev-desk", (194, 60, 40))
    s1 = _plate("s01", 0.0, 6.0, [_placed("ev-desk", 0, 1.0, leave, PLACE_A)])   # 1.0 s before the turn: snapped ONTO it
    s2 = _plate("s02", 6.0, GS.RUNTIME, [], exit_)
    return _tl(GS, "a dock that ends on a dip", [s1, s2], {"ev-desk": card})


@needs_chromium
def test_a_dip_takes_the_outgoing_docks_with_its_black(GS):
    tl, uris = _dip_bed(GS)
    got = [j for _p, j in _frames(tl, uris, [5.7, 5.95, 6.0, 6.08, 6.2, 6.5], png=False)]
    before, *after = got[:2], got[2:]
    assert all(g["s1"]["slide"] == "ev-desk" and g["s1"]["opacity"] > 0.99 for g in got[:2]), \
        "the card rides the dip's ramp DOWN with the world (the veil is above every layer)"
    assert all(g["s1"]["opacity"] == 0 for g in got[2:]), [(g["s1"], g["dip"]) for g in got[2:]]
    assert all(g["wash"] is False for g in got[2:]), "... and its wash goes with it"


@needs_chromium
def test_row_17s_docks_may_end_on_the_boundary(GS):
    """H row 17b's workaround ended its desk docks DOCKS_OFF_LEAD_S = 1.5 s early; ending ON the boundary now leaves with
    the dip - nothing of the desk is on the incoming page's first frames."""
    tl, uris = _dip_bed(GS, leave=6.0)
    got = [j for _p, j in _frames(tl, uris, [5.9, 6.04, 6.3], png=False)]
    assert got[0]["s1"]["opacity"] > 0.99 and got[1]["s1"]["opacity"] == 0 and got[2]["s1"]["opacity"] == 0, got


def _landing_bed(GS) -> tuple[dict, dict]:
    a, b = _card_ev(GS, "ev-old", (194, 60, 40)), _card_ev(GS, "ev-new", (40, 140, 90))
    s1 = _plate("s01", 0.0, 6.0, [_placed("ev-old", 0, 1.0, 5.0, PLACE_A), _placed("ev-new", 0, 5.1, 12.0, PLACE_B)])
    s2 = _plate("s02", 6.0, GS.RUNTIME, [])
    return _tl(GS, "a landing inside the snap window", [s1, s2], {"ev-old": a, "ev-new": b})


@needs_chromium
def test_the_snap_never_moves_an_exit_across_a_landing(GS):
    tl, uris = _landing_bed(GS)
    (_p, j), = _frames(tl, uris, [5.9], png=False)
    assert j["s1"]["slide"] == "ev-new" and (j["s1"]["left"], j["s1"]["top"]) == (PLACE_B["x"], PLACE_B["y"]), \
        "the card that LANDED in the slot is the one shown - the leaving card was not held over it to the boundary"


@needs_chromium
def test_a_wipe_still_sweeps_and_a_dip_is_pure_in_t(GS):
    tl, uris = _dip_bed(GS, exit_="wipe")
    got = [j for _p, j in _frames(tl, uris, [6.2], png=False)]
    assert got[0]["s1"]["opacity"] > 0, "a wipe's front still carries the card off (unchanged)"
    tl, uris = _dip_bed(GS)
    a, _b, c = _frames(tl, uris, [6.1, 3.0, 6.1])
    assert a[0] == c[0], "a seek back into the dip lands the same frame"
    assert a[1]["s1"]["opacity"] == c[1]["s1"]["opacity"] == 0 and a[1]["wash"] == c[1]["wash"] is False


# ---- R26-202 (b): the throw enters from its side ----------------------------------------------------------------------
RIGHT_SLOT = {"x": 1400, "y": 300, "w": 400, "h": 300}


def _throw_bed(GS, side: str | None, place: dict = RIGHT_SLOT) -> tuple[dict, dict]:
    a, b = _card_ev(GS, "ev-first", (194, 60, 40)), _card_ev(GS, "ev-thrown", (40, 140, 90))
    extra = {"throw_side": side} if side else {}
    s1 = _plate("s01", 0.0, GS.RUNTIME, [_placed("ev-first", 0, 1.0, 3.0, PLACE_A, arrive="throw", mass="paper"),   # flip 0 -> "r"
                                          _placed("ev-thrown", 0, 8.0, 14.0, place, arrive="throw", mass="paper", **extra)])   # flip 1 -> "l"
    return _tl(GS, f"a throw from the {side}", [s1], {"ev-first": a, "ev-thrown": b})


def _first_visible(tl, uris) -> dict:
    ts = [round(8.0 + i / 48, 4) for i in range(24)]
    for t, (_p, j) in zip(ts, _frames(tl, uris, ts, png=False)):
        x, y, w, h = j["s1"]["box"]
        if j["s1"]["slide"] == "ev-thrown" and j["s1"]["opacity"] > 0 and x < W16 and x + w > 0 and y < H16 and y + h > 0:
            return {"t": t, "box": j["s1"]["box"]}
    return {}


@needs_chromium
def test_a_throw_with_side_right_enters_from_the_right_edge(GS):
    got = _first_visible(*_throw_bed(GS, "right"))
    x, y, w, h = got["box"]
    assert x + w > W16 - 1 and x > W16 - w, f"the first visible frame's box touches the RIGHT edge: {got}"


@needs_chromium
def test_a_throw_with_side_bottom_enters_from_the_bottom_edge(GS):
    got = _first_visible(*_throw_bed(GS, "bottom"))
    x, y, w, h = got["box"]
    assert y + h > H16 - 1 and y > H16 - h, f"the first visible frame's box touches the BOTTOM edge: {got}"


@needs_chromium
def test_a_throw_with_side_left_to_a_right_slot_enters_from_the_left_edge(GS):
    got = _first_visible(*_throw_bed(GS, "left"))
    x, y, w, h = got["box"]
    assert x < 1 and x + w < w, f"the first visible frame's box touches the LEFT edge: {got}"


# ---- R26-320: a held press card ---------------------------------------------------------------------------------------
def _press_bed(GS, idle: str | None) -> tuple[dict, dict]:
    aid, (_, enter, src, phrase, bars, words) = GS.PRESS_CARDS[0][0], GS.PRESS_CARDS[0]
    ev = {aid: {"title": "Press card", "source": src, "species": "press", "document": {"path": "golden", "sha256": "0" * 64}, "badges": []}}
    d = {"slide": aid, "slot": 0, "enter": 2.0, "exit": 20.0, "badge_at": [], "kind": "press", "source": src, "phrase": phrase,
         "phrase_text": words, "img": round(GS.PRESS_CROP[1] / GS.PRESS_CROP[0], 5), **({"idle": idle} if idle else {})}
    uris = GS._base_uris()
    uris[aid] = GS.uri("image/png", GS.png_bars(GS.PRESS_CROP[0], GS.PRESS_CROP[1], (250, 247, 240), bars))
    tl = GS._timeline("P72 T19: a held press card", [_plate("s01", 0.0, GS.RUNTIME, [d])], ev, None)
    tl["kinetics"] = {"idle": True}
    return tl, uris


@needs_chromium
def test_a_held_press_card_drifts_and_catches_its_band(GS):
    got = [j["press"][0] for _p, j in _frames(*_press_bed(GS, "hold"), [6.0, 11.0, 16.0], png=False)]
    assert len({g["transform"] for g in got}) == 3, "the hold drifts across the card's span (R26-320: it stood still)"
    assert all("rotate" in g["transform"] for g in got), got
    assert all(g["light"] for g in got) and len({g["light"] for g in got}) == 3, "... and the light band crosses its face"


@needs_chromium
def test_a_press_card_that_names_no_hold_is_the_card_it_was(GS):
    got = [j["press"][0] for _p, j in _frames(*_press_bed(GS, None), [6.0, 11.0], png=False)]
    assert got[0]["transform"] == got[1]["transform"] and not got[0]["light"], got


# ---- R26-271: the hatch rides the dock's camera -----------------------------------------------------------------------
PROP_PLACE = {"x": 820, "y": 380, "w": 282, "h": 259}


def _hatch_bed(GS) -> tuple[dict, dict]:
    aid = "ev-prop-fed"
    ev = {aid: {"title": "The Federal Reserve", "source": "the operator's own cutout", "species": "prop", "badges": [],
                "document": {"path": "golden", "sha256": "0" * 64}, "kind": B.DOCK_KIND_PROP}}
    d = B.dock_entry(aid, 0, 2.0, GS.RUNTIME, 0, B.DOCK_KIND_PROP, PROP_PLACE, "land", "paper", True, prop=True, ink="own",
                     depth=1.15)
    P = PROP_PLACE
    zoom = [{"kind": "focus_zoom", "at": 8.0, "dur": 2.0, "target": {"kind": "region", "x0": (P["x"] - 300) / W16, "y0": P["y"] / H16,
                                                                     "x1": (P["x"] + 60) / W16, "y1": (P["y"] + P["h"]) / H16}}]
    uris = GS._base_uris()
    uris[aid] = GS.uri("image/png", GS.png_proxy(GS.PROP_CUTOUT, GS.PROP_PROXY_PX))
    tl = GS._timeline("P72 T19: the hatch under the dock's camera", [_plate("s01", 0.0, GS.RUNTIME, [d], species=zoom)], ev, None)
    tl["kinetics"] = {"stop_action": True, "camera": True}
    return tl, uris


HATCH = """() => {
  const s = document.getElementById('stage').getBoundingClientRect(), k = 1920 / s.width;
  const cv = document.getElementById('dock-hatch-0'), img = document.querySelector('#dock-1 .slide-frame img');
  const b = img.getBoundingClientRect();
  return {png: cv.toDataURL('image/png'), left: parseFloat(cv.style.left), top: parseFloat(cv.style.top), op: +cv.style.opacity,
          img: [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k]};
}"""


def _hatch_alpha(j: dict):
    from PIL import Image
    import base64
    return Image.open(io.BytesIO(base64.b64decode(j["png"].split(",", 1)[1]))).convert("RGBA").split()[3]


def _corr(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) if va and vb else 0.0


@needs_chromium
def test_the_hatch_rides_the_dock_cameras_zoom(GS):
    """At the zoom's hold the dock's plane is scaled s and moved T; the hatch at that frame, carried back through the
    camera (the prop's image box gives s and T exactly), is the hatch of the frame before the move - the lines ride the
    PAGE. Screen-fixed lines (R26-271) beat against the carried ones: the correlation collapses."""
    from PIL import Image
    (_p1, a), (_p2, b) = _frames(*_hatch_bed(GS), [7.5, 9.8], js=HATCH, png=False)
    assert a["op"] > 0 and b["op"] > 0, (a["op"], b["op"])
    s = b["img"][2] / a["img"][2]
    assert s > 1.05, f"the camera zoomed the prop ({s})"
    tx, ty = b["img"][0] - s * a["img"][0], b["img"][1] - s * a["img"][1]
    A, Bm = _hatch_alpha(a), _hatch_alpha(b)
    # output pixel (i, j) of A's canvas is the page point (a.left + i, a.top + j); at t2 it is at s * p + T in stage px
    back = Bm.transform(A.size, Image.AFFINE, (s, 0, s * a["left"] + tx - b["left"], 0, s, s * a["top"] + ty - b["top"]),
                        resample=Image.BILINEAR)
    w, h = A.size
    xs, ys = range(int(w * 0.3), int(w * 0.7)), range(int(h * 0.3), int(h * 0.7))   # the silhouette's interior
    pa = [A.getpixel((x, y)) for y in ys for x in xs]
    pb = [back.getpixel((x, y)) for y in ys for x in xs]
    assert sum(1 for v in pa if v > 0) > 0.2 * len(pa), "the interior carries hatch lines"
    c = _corr(pa, pb)
    assert c > 0.6, f"the hatch carried back through the camera is the hatch before the move: corr {c:.3f}"


# ---- R26-267: a pinned stamp rides its card's read-then-park ----------------------------------------------------------
TICKET_READ = {"x": 1200, "y": 250, "w": 576, "h": 518}
TICKET_PARK = {"x": 1382, "y": 107, "w": 384, "h": 345}


def _pin_bed(GS, inherit: list[str] | None = None) -> tuple[dict, dict]:
    tk, sell = "ev-ticket", "ev-sell"
    card = _card_ev(GS, tk, (236, 228, 205), 400, 360)
    ev = {"title": "SELL", "source": "the stamp", "species": "prop", "badges": [], "kind": B.DOCK_KIND_PROP,
          "document": {"path": "golden", "sha256": "0" * 64}}
    parent = B.dock_entry(tk, 0, 2.0, 20.0, 0, B.DOCK_KIND_IMAGE, TICKET_PARK, "throw", "paper", True, read_place=TICKET_READ,
                          read_s=3.0, park_s=0.7)
    cx, cy = TICKET_READ["x"] + TICKET_READ["w"] / 2, TICKET_READ["y"] + TICKET_READ["h"] / 2
    sp = {"x": round(cx - 120), "y": round(cy - 55), "w": 240, "h": 110}   # centred on the ticket as it READS
    child = B.dock_entry(sell, 1, 3.4, 20.0, 0, B.DOCK_KIND_PROP, sp, "stamp", "ink", True, prop=True, ink="own",
                         ring_to=1.6, from_to=1.8, paint=[0, 0, 1, 1])
    child["rel"] = {"pin": tk, "inherit": inherit or ["translate"]}   # the entry as the compiler writes it (the default spelled out)
    uris = GS._base_uris()
    uris[sell] = GS.uri("image/png", GS.png_cutout(240, 110, (237, 106, 74), [(0.05, 0.1, 0.95, 0.9)]))
    tl = GS._timeline("P72 T19: SELL pinned to the ticket", [_plate("s01", 0.0, GS.RUNTIME, [parent, child])],
                      {tk: card[0], sell: ev}, None)
    tl["kinetics"] = {"stop_action": True}
    uris[tk] = card[1]
    return tl, uris


def _rel(j: dict) -> tuple[float, float, float]:
    p, c = j["s1"], j["s2"]
    ph = p["width"] * TICKET_PARK["h"] / TICKET_PARK["w"]
    cw = c["width"]
    ccx, ccy = c["left"] + cw / 2, c["top"] + cw * 110 / 240 / 2
    return ((ccx - p["left"]) / p["width"], (ccy - p["top"]) / ph, cw)


@needs_chromium
def test_a_pinned_stamp_rides_its_cards_read_then_park(GS):
    got = [j for _p, j in _frames(*_pin_bed(GS), [4.5, 5.35, 7.0], png=False)]
    (u0, v0, w0), (u1, v1, w1), (u2, v2, w2) = [_rel(j) for j in got]
    assert abs(got[2]["s1"]["left"] - TICKET_PARK["x"]) < 0.6 and abs(got[2]["s1"]["width"] - TICKET_PARK["w"]) < 0.6, got[2]["s1"]
    assert abs(u0 - 0.5) < 0.01 and abs(v0 - 0.5) < 0.01, (u0, v0)
    for u, v in ((u1, v1), (u2, v2)):
        assert abs(u - u0) < 0.002 and abs(v - v0) < 0.002, "the stamp stays at its point ON the card through the park"
    assert w0 == w1 == w2 == 240, "E97: a pin inherits translation only - the mark keeps its size"


@needs_chromium
def test_a_pin_that_inherits_scale_shrinks_with_its_card(GS):
    got = [j for _p, j in _frames(*_pin_bed(GS, ["translate", "scale"]), [4.5, 7.0], png=False)]
    (u0, v0, w0), (u2, v2, w2) = [_rel(j) for j in got]
    assert abs(u2 - u0) < 0.002 and abs(v2 - v0) < 0.002
    assert abs(w2 / w0 - TICKET_PARK["w"] / TICKET_READ["w"]) < 0.002, (w0, w2)


@needs_chromium
def test_the_pin_is_pure_in_t(GS):
    a, _b, c = _frames(*_pin_bed(GS), [6.0, 3.0, 6.0])
    assert a[0] == c[0] and a[1] == c[1]


# ---- R26-343: the park scales the key rail ----------------------------------------------------------------------------
KEYJS = """() => {
  const s = document.getElementById('stage').getBoundingClientRect(), k = 1920 / s.width;
  const w = [...document.querySelectorAll('.world')].find((e) => e.__lp && e.querySelector('.lp-key') && getComputedStyle(e).display !== 'none');
  const box = (e) => { const b = e.getBoundingClientRect(); return [(b.x - s.left) * k, (b.y - s.top) * k, b.width * k, b.height * k]; };
  return {key: box(w.querySelector('.lp-key')), chart: box(w.querySelector('.lp-chart'))};
}"""


@needs_chromium
def test_a_park_scales_the_pages_key_rail(GS, tmp_path):
    import test_longform_key_rail as KR
    world = KR._compile("ledger:fx-lf-long:line" + KR.MID, tmp_path)
    park = [{"kind": "chart_to", "to": "park", "at": 20.0, "dur": 0.9, "scale": 0.34, "anchor": "left"}]
    scene = KR._scene(world, park)
    tl = GS._timeline("P72 T19: a parked keyed page", [scene], {}, KR.T.ASPECT)
    uris = dict(GS._base_uris(), **B.longform_assets(tl))
    (_p, a), (_p2, b) = _frames(tl, uris, [19.5, 22.0], js=KEYJS, png=False)
    kc = b["chart"][2] / a["chart"][2]
    assert abs(kc - 0.34) < 0.01, kc
    assert abs(b["key"][2] / a["key"][2] - kc) < 0.01, f"the key shrinks with the chart (R26-343): {a['key']} -> {b['key']}"
    for i in (0, 1):   # ... about the chart's own anchor: its offset from the chart's corner scales by the same share
        assert abs((b["key"][i] - b["chart"][i]) - kc * (a["key"][i] - a["chart"][i])) < 1.5, (a, b)
