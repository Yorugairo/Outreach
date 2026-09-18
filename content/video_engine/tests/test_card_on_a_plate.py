"""R26-221 - A CARD CANNOT TAKE AN AUTHORED SLOT ON A PICTURE PLATE.

Measured on the Steel and Paper H unit (2026-09-18): `dock_place` answers None unless the world is a ledger page -
E45's "a dock on a plain plate keeps the solo card" - and that one answer was also swallowing the ROW's own box.
`centre / centre_w / centre_x / centre_y / read / read_s / park_s` are all gated behind `place`, so the unit's solo
card on the studio plate landed at the template's `.dock.solo` rectangle, straight across the host's face, and
"never over the host" could only be obeyed by docking nothing at all.

THE PLAYER NEEDED NOTHING. `dockGeom` and `dockReadRect` read `d.place` / `d.read_place` for any world, and the
`camera-layers` / `dock-depth` goldens have handed a hand-written place to a card on a PLATE since P58 T3
(`build_golden_sources.py` CAMERA_LAYERS_PLACE). The shut door was the compiler's alone.

Two ways a card is placed on a plate, and nothing else changes:
  (a) THE ROW'S OWN BOX - the same fields a page row takes (E99 s80, `OPERATOR-RULINGS.md:3278`: "a card that
      follows a card on one page takes the outgoing card's box"), decided by the page's own `centred_place` with no
      page, so a plate and a page can never disagree about where an authored box is;
  (b) THE PLATE'S DECLARED ROOM - `;room=x,y,w,h`, fractions of the stage: the plate's answer to a page's
      `quiet_zone`. The card takes the reading width the room holds, centred in it, with `DOCK_PLACE_PAD` of air,
      through `_fit_in` - the same fitter `page_place` uses on a page's free band - which is what lets `read` then
      `park` work on a plate.
A row that authors neither, on a plate that declares neither, still gets None: E45's solo card, to the byte.

THE ORDER between the two (pinned in `test_a_row_that_names_WHERE_outranks_the_room_...`): a row that names WHERE -
`centre`, `centre_x`, `centre_y` - outranks the declared room, a bare `centre: True` included, because that is the
stage's own centre and not the room's. `centre_w` and `card_aspect` name no place - they size a card - so a
room-declaring plate honours them inside its room.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import render_baseline as RB  # noqa: E402

SRC = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")

# the H unit's own studio row, as its author wrote the page rows (SHOT-TABLE-H.py line 2) - the shape this row owes
# a plate: a card of 0.17 of the stage width, centred on a named point, thrown in on paper
AUTHORED = {"centre": True, "centre_w": 0.17, "centre_x": 0.79, "centre_y": 0.737, "arrive": "throw", "mass": "paper"}
ROOM = "0.04,0.10,0.34,0.62"        # the clear third the host plates were generated with, as the plate declares it
ROOM_FRACTIONS = [0.04, 0.10, 0.34, 0.62]


# ---- the token's grammar ------------------------------------------------------------------------------


def test_room_is_a_plate_option_and_check_opt_routes_it():
    assert "room" in B.PLATE_OPTS
    assert B.split_plate_opts("world-h1-studio-v1;idle=drift;drift=20;room=" + ROOM)[1] == {
        "idle": "drift", "drift": "20", "room": ROOM}
    with pytest.raises(ValueError, match="is not x,y,w,h"):
        B.split_plate_opts("world-h1-studio-v1;room=0.1,0.2")


def test_the_room_is_four_fractions_of_the_stage():
    assert B.plate_room_spec(ROOM, "row") == ROOM_FRACTIONS
    assert B.plate_room_spec(" 0 , 0 , 1 , 1 ", "row") == [0.0, 0.0, 1.0, 1.0]


def test_a_room_that_is_not_four_numbers_or_runs_off_the_stage_is_refused():
    for bad in ("0.1,0.2,0.3", "0.1,0.2,0.3,0.4,0.5", "0.1,0.2,0.3,"):
        with pytest.raises(ValueError, match="is not x,y,w,h"):
            B.plate_room_spec(bad, "row")
    with pytest.raises(ValueError, match="is not four numbers"):
        B.plate_room_spec("left,top,wide,tall", "row")
    for empty in ("0.1,0.1,0,0.4", "0.1,0.1,0.4,-0.2"):
        with pytest.raises(ValueError, match="is empty"):
            B.plate_room_spec(empty, "row")
    for off in ("0.8,0.1,0.4,0.2", "0.1,0.8,0.2,0.4", "-0.1,0.1,0.2,0.2"):
        with pytest.raises(ValueError, match="runs off the stage"):
            B.plate_room_spec(off, "row")


def test_a_room_whose_numbers_are_not_FINITE_is_refused_by_the_parser():
    """The reviewer's round: `float("nan")` passes every `>` guard in the parser (`nan > 0` is False, and so is
    `nan < 0`, so `min(x, y) < 0` and `x + w > 1` both let it through) and `float("inf")` passes three of them.
    Either one used to reach `plate_room_px` and die there in `round()` with no row named."""
    for bad in ("nan,0.1,0.3,0.3", "0.1,0.1,inf,0.3", "0.1,0.1,0.3,-nan", "Infinity,0.1,0.3,0.3",
                "0.1,0.1,0.3,NaN"):
        with pytest.raises(ValueError, match="is not four numbers"):
            B.plate_room_spec(bad, "row")
        with pytest.raises(ValueError, match="is not four numbers"):
            B.split_plate_opts("world-h1-studio-v1;room=" + bad)   # ... and the row is refused at the token


def test_the_fractions_become_stage_pixels_at_either_aspect():
    assert B.plate_room_px(None, "16:9") is None
    assert B.plate_room_px([0.0, 0.0, 1.0, 1.0], "16:9") == {"x": 0, "y": 0, "w": 1920, "h": 1080}
    assert B.plate_room_px([0.0, 0.0, 1.0, 1.0], "9:16") == {"x": 0, "y": 0, "w": 1080, "h": 1920}
    assert B.plate_room_px([0.5, 0.25, 0.25, 0.5], "16:9") == {"x": 960, "y": 270, "w": 480, "h": 540}


def test_the_room_is_a_picture_plates_word_and_is_refused_on_a_world_that_computes_its_own():
    """A page's room is computed from its own ink (`page_place` / E65), so a page declaring one would be two
    truths about one space. The refusal names the kind, the way `;drift=` does."""
    td = tempfile.TemporaryDirectory()
    try:
        ep = Path(td.name)
        (ep / "evidence/objects").mkdir(parents=True)
        (ep / "evidence/objects/ev-lines-v1.series.json").write_text(json.dumps(
            {"title": "t", "sub": "s", "src": "the test bed", "unit": "",
             "series": [{"name": "A", "color": "crimson", "pts": [[1, 1], [2, 2], [3, 3]]},
                        {"name": "B", "color": "teal", "pts": [[1, 2], [2, 3], [3, 4]]}]}), encoding="utf-8")
        with pytest.raises(ValueError, match="room= is a PICTURE PLATE option"):
            B.world_for_plate("ledger:ev-lines-v1:line;room=" + ROOM, (0, 0, 0), ep)
    finally:
        td.cleanup()
    with pytest.raises(ValueError, match="room= is a PICTURE PLATE option"):
        B.world_for_plate("vecmap;room=" + ROOM, (0, 0, 0), Path("."))


def test_a_plate_that_declares_a_room_carries_it_as_fractions_and_nothing_else_moves(tmp_path):
    """Fractions, not pixels: the same timeline is instantiated at either aspect, so the world is authored once
    (the reason a species' `target` is written in fractions too)."""
    from PIL import Image
    objects = tmp_path / "evidence/objects"
    objects.mkdir(parents=True)
    Image.new("RGB", (64, 36), (43, 52, 60)).save(objects / "plate-room-test.png")
    old = B.R.EP
    try:
        B.R.EP = tmp_path
        plain = B.world_for_plate("plate-room-test;idle=drift;drift=20", (0.05, -12, 6), tmp_path)
        assert "room" not in plain, "a plate that declares none writes nothing - byte-identity"
        world = B.world_for_plate("plate-room-test;idle=drift;drift=20;room=" + ROOM, (0.05, -12, 6), tmp_path)
        assert world["room"] == ROOM_FRACTIONS
        del world["room"]
        assert world == plain, "the declared room is the ONLY difference the token makes"
    finally:
        B.R.EP = old


# ---- the placer ---------------------------------------------------------------------------------------


def test_a_plain_plate_with_nothing_authored_still_keeps_the_solo_card():
    """E45, unchanged: no box, no room, no place - so every build that came before this row compiles to the bytes
    it did and `dock_entry` writes no `place` key at all."""
    assert B.plate_dock_place(None, "16:9", {}) is None
    assert B.plate_dock_place(None, "16:9", {"card_aspect": 0.5625, "arrive": "throw"}) is None, \
        "card_aspect is the SHAPE of a box, never the reason for one"
    entry = B.dock_entry("ev-card", 0, 2.0, 10.0, 0, B.DOCK_KIND_IMAGE, None)
    assert "place" not in entry and "read_place" not in entry


def test_the_rows_own_box_is_honoured_on_a_plate_and_it_is_the_pages_own_door():
    box = B.plate_dock_place(None, "16:9", AUTHORED)
    assert box["room"] == B.PLATE_BOX_PLACED
    same = B.centred_place(None, "16:9", None, None, AUTHORED["centre_w"], None,
                           AUTHORED["centre_y"], AUTHORED["centre_x"])
    assert {k: box[k] for k in ("x", "y", "w", "h")} == same, \
        "ONE function decides an authored box, for a page and for a plate"
    # the box the H unit's author asked for: 0.17 of the stage wide, centred on (0.79, 0.737)
    assert box["w"] == round(0.17 * 1920)
    assert abs(box["x"] + box["w"] / 2 - 0.79 * 1920) <= 1 and abs(box["y"] + box["h"] / 2 - 0.737 * 1080) <= 1


def test_centre_alone_on_a_plate_is_the_stages_own_centre():
    box = B.plate_dock_place(None, "16:9", {"centre": True})
    assert abs(box["x"] + box["w"] / 2 - 960) <= 1, box
    assert box["room"] == B.PLATE_BOX_PLACED


def test_the_declared_room_places_a_card_that_authored_no_box_at_all():
    room = B.plate_room_px(ROOM_FRACTIONS, "16:9")
    box = B.plate_dock_place(room, "16:9", {})
    assert box["room"] == B.PLATE_ROOM_PLACED
    assert box["x"] >= room["x"] + B.DOCK_PLACE_PAD and box["y"] >= room["y"] + B.DOCK_PLACE_PAD
    assert box["x"] + box["w"] <= room["x"] + room["w"] - B.DOCK_PLACE_PAD
    assert box["y"] + box["h"] <= room["y"] + room["h"] - B.DOCK_PLACE_PAD
    # centred in the room it was given, both ways
    assert abs((box["x"] + box["w"] / 2) - (room["x"] + room["w"] / 2)) <= 1
    assert abs((box["y"] + box["h"] / 2) - (room["y"] + room["h"] / 2)) <= 1
    assert box["h"] == B.dock_card_h(box["w"]), "a card with no declared aspect keeps the 16:9 frame plus its chrome"


def test_a_narrower_centre_w_inside_the_room_is_honoured():
    room = B.plate_room_px(ROOM_FRACTIONS, "16:9")
    wide = B.plate_dock_place(room, "16:9", {})
    narrow = B.plate_dock_place(room, "16:9", {"centre_w": 0.17})
    assert narrow["w"] == round(0.17 * 1920) < wide["w"]
    assert narrow["room"] == B.PLATE_ROOM_PLACED


def test_a_row_that_names_WHERE_outranks_the_room_and_a_row_that_only_names_A_WIDTH_does_not():
    """The order, pinned (the reviewer's round). A bare `centre: True` is a PLACE - the stage's own centre - so it
    outranks the plate's declared room the way a named point does (E99 s80: the author names the slot). `centre_w`
    and `card_aspect` name no place: they SIZE a card, so the room honours them inside itself. Without this the
    docstring's "the row's box outranks the room" was true only of `centre_x` / `centre_y`."""
    assert B.PLATE_PLACE_POINT == ("centre", "centre_x", "centre_y")
    assert set(B.PLATE_PLACE_POINT) < set(B.PLATE_PLACE_FIELDS), "the places are a subset of what asks to be placed"
    assert set(B.PLATE_PLACE_FIELDS) - set(B.PLATE_PLACE_POINT) == {"centre_w"}
    room = B.plate_room_px(ROOM_FRACTIONS, "16:9")
    bare = B.plate_dock_place(room, "16:9", {"centre": True})
    assert bare["room"] == B.PLATE_BOX_PLACED, ("a bare `centre` is the STAGE's centre, not the room's", bare)
    assert abs(bare["x"] + bare["w"] / 2 - 960) <= 1 and bare == B.plate_dock_place(None, "16:9", {"centre": True})
    for sizing in ({"centre_w": 0.17}, {"card_aspect": 0.9113}, {"centre_w": 0.17, "card_aspect": 0.9113}):
        sized = B.plate_dock_place(room, "16:9", sizing)
        assert sized["room"] == B.PLATE_ROOM_PLACED, ("a width or an aspect names no place", sizing, sized)
        assert sized["x"] >= room["x"] and sized["x"] + sized["w"] <= room["x"] + room["w"], (sizing, sized, room)


def test_the_rows_own_box_outranks_the_plates_declared_room():
    """The author has named the slot; the room is where the compiler is asked to FIND one (E99 s80's own order -
    the outgoing card's box is a measured rectangle, not a search)."""
    room = B.plate_room_px(ROOM_FRACTIONS, "16:9")
    assert B.plate_dock_place(room, "16:9", AUTHORED) == B.plate_dock_place(None, "16:9", AUTHORED)
    assert B.plate_dock_place(room, "16:9", AUTHORED)["room"] == B.PLATE_BOX_PLACED


def test_a_declared_room_that_cannot_hold_a_legible_card_is_refused_by_name():
    """A room that has been named and cannot be used is an authoring fault, not a silent fall-back - the same call
    `;drift=` under E49's floor makes."""
    tiny = B.plate_room_px([0.0, 0.0, 0.06, 0.06], "16:9")
    with pytest.raises(ValueError, match="cannot hold a card"):
        B.plate_dock_place(tiny, "16:9", {}, "shot row 4 (54.9-66.15s) dock dock-h-mike")
    try:
        B.plate_dock_place(tiny, "16:9", {}, "shot row 4 (54.9-66.15s) dock dock-h-mike")
    except ValueError as exc:
        assert "shot row 4" in str(exc) and "dock-h-mike" in str(exc), str(exc)
        assert "centre_w" in str(exc) and ";room=" in str(exc), "and it says which way out there is"


def test_the_two_rooms_a_plate_card_can_come_from_are_named_on_the_entry():
    """`place_room` is how the build report, a gate and a reader see which of the two placed the card - the same
    role E65's four page rooms play."""
    assert (B.PLATE_BOX_PLACED, B.PLATE_ROOM_PLACED) == ("plate-box", "plate-room")
    assert not set((B.PLATE_BOX_PLACED, B.PLATE_ROOM_PLACED)) & set(B.PLACE_ROOMS), \
        "and they are never confused with a page's own four"
    entry = B.dock_entry("ev-card", 0, 2.0, 10.0, 0, B.DOCK_KIND_IMAGE, B.plate_dock_place(None, "16:9", AUTHORED))
    assert entry["place_room"] == B.PLATE_BOX_PLACED
    assert entry["place"] == {k: B.plate_dock_place(None, "16:9", AUTHORED)[k] for k in ("x", "y", "w", "h")}


# ---- the wiring: the three lines in the row loop that used to drop the box -----------------------------


def test_the_loop_reads_the_plates_room_once_per_scene():
    assert 'plate_room = plate_room_px(world.get("room"), ASPECT)' in SRC


def test_the_loop_places_a_plate_card_exactly_where_the_page_branch_answered_none():
    body = SRC[SRC.index("        place = dock_place(world, ASPECT"):]
    body = body[:body.index("assign_press_stack(docks)")]
    i_page = body.index("dplace = centred_place(place, ASPECT")
    i_plate = body.index("if place is None:")
    i_read = body.index('rd = dopt.get("read") or {}')
    i_eplace = body.index("eplace = dplace if (slot == 0 or centred")
    assert i_page < i_plate < i_eplace, "the plate branch answers after the page branch and before the slot rule"
    assert "plate_dock_place(plate_room, ASPECT, dopt," in body
    assert "if (dplace and rd) else None" in body[i_read:], \
        "the READ is placed off `dplace`, not off the page's `place` - a plate card pops too (R26-221)"
    assert "or (place is None and dplace)) else None" in body[i_eplace:], \
        "and on a plate the BOX is the slot: an authored box is honoured on either slot"


def test_a_plate_cards_place_error_fails_the_row_by_number():
    body = SRC[SRC.index("            if place is None:"):]
    body = body[:body.index("if dopt.get(\"press\"):")]
    assert 'raise SystemExit(f"FAIL: {exc}")' in body
    assert 'f"shot row {i + 1} ({a}-{b}s) dock {aid}"' in body


# ---- the frames: the compiled box IS the card's box ---------------------------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# Each dock's LAYOUT box in stage px - `offsetLeft/Top/Width/Height`, which is what the engine itself writes and
# reads (`dockGeom` -> `el.style.left/top/width`), so the pop spring's scale and the parked card's idle breath are
# not mistaken for a placement. A card off its span reports null.
DOCK_PROBE = """() => {
  const out = {};
  for (const s of [0, 1]) {
    const el = document.getElementById('dock-' + (s + 1));
    const up = el && parseFloat(el.style.opacity || '0') > 0.01 && el.offsetWidth > 2;
    out['d' + s] = up ? { x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight,
                          slide: el.dataset.slide || null, solo: el.classList.contains('solo') } : null;
  }
  return out;
}"""

CARD_A, CARD_B = "ev-golden-card-a", "ev-golden-card-b"
ENTER_A, ENTER_B, RUNTIME = 2.0, 5.0, 30.0


def _plate_player(dock_a: dict | None, dock_b: dict | None = None, room: list | None = None, pair: bool = True):
    """The `dock-pair-16x9` golden's own world - a picture plate with two cards on it - with the docks recompiled
    from the row options each case names. Nothing about the plate or the assets changes between cases."""
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface("dock-pair-16x9")
    scene = json.loads(json.dumps(tl["scenes"][0]))
    world = dict(scene["world"], ken_burns={"scale": 0, "x": 0, "y": 0})
    if room is not None:
        world["room"] = room
    plate_room = B.plate_room_px(world.get("room"), "16:9")
    docks = []
    rows = [(CARD_A, 0, ENTER_A, dock_a)] + ([(CARD_B, 1, ENTER_B, dock_b)] if pair else [])
    for aid, slot, enter, opts in rows:
        dopt = B.dock_opts(opts) if opts else {}
        place = B.plate_dock_place(plate_room, "16:9", dopt)
        rd = dopt.get("read") or {}
        rplace = B.centred_place(None, "16:9", rd.get("card_aspect", dopt.get("card_aspect")), None,
                                 rd.get("centre_w"), None, rd.get("centre_y"), rd.get("centre_x")) if (place and rd) else None
        docks.append(B.dock_entry(aid, slot, enter, RUNTIME, 2, B.DOCK_KIND_IMAGE, place,
                                  dopt.get("arrive"), dopt.get("mass"), bool(dopt.get("centre")),
                                  read_place=rplace, read_s=dopt.get("read_s"), park_s=dopt.get("park_s")))
    scene["world"], scene["docks"], scene["species"] = world, docks, []
    timeline = dict(tl, aspect="16:9", runtime_s=RUNTIME, scenes=[scene], caption_pages=[], captions=[])
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "plate.html"
    html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(html.parent)
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    page = br.new_context(viewport={"width": w, "height": h}).new_page()
    errs: list[str] = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, w, h)

    def at(t: float) -> dict:
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
        return page.evaluate(DOCK_PROBE)

    def close():
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return at, docks, errs, close


def _near(got: dict, want: dict, tol: float = 2.0, keys=("x", "y", "w")) -> None:
    for k in keys:
        assert abs(got[k] - want[k]) <= tol, (k, got, want)


@needs_browser
def test_the_engines_default_is_what_a_plate_card_used_to_get_and_still_gets_with_no_box():
    """The row's measurement, read on the served player: with no authored box the solo card lands at the
    template's `.dock.solo` rectangle - the box that fell across the host's face."""
    at, docks, errs, close = _plate_player(None, None, pair=False)
    try:
        assert all("place" not in d for d in docks), "nothing placed them"
        p = at(12.0)["d0"]
        _near(p, B.DOCK_READ_CSS["16:9"], tol=8, keys=("x", "w"))
        assert p["x"] < 960 < p["x"] + p["w"], ("it crosses the middle of the frame - the H unit's own fault", p)
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_the_authored_box_is_the_cards_box_on_a_picture_plate():
    """R26-221's acceptance: the card's rendered bounding box equals the compiled box within 2 px, and the second
    card - which authored nothing - lands where it landed before, to the pixel."""
    at0, _docks0, errs0, close0 = _plate_player(None, None)
    try:
        base = at0(ENTER_B + 6.0)
    finally:
        close0()
    at, docks, errs, close = _plate_player(AUTHORED, None)
    try:
        place = docks[0]["place"]
        assert place and docks[0]["place_room"] == B.PLATE_BOX_PLACED
        p = at(ENTER_A + B.DOCK_READ_S + B.DOCK_PARK_S + 1.0)   # the park has landed: the box IS `place`
        _near(p["d0"], place)
        assert p["d0"] != base["d0"], ("the placed card MOVED off the default", p["d0"], base["d0"])
        later = at(ENTER_B + 6.0)
        assert later["d1"] == base["d1"], ("a card without a box is untouched, to the pixel", later["d1"], base["d1"])
        assert later["d1"]["x"] > 960, "and the engine's default for slot 1 is where it always was"
        # the HEIGHT is the card's content's, as it is on a page (CAPABILITIES:68 - `place.h` is the compiler's
        # prediction, never a forced box): the title, the source line and two badges make this card 278 px at 326
        assert p["d0"]["h"] >= place["h"], ("the card is at least as tall as predicted", p["d0"], place)
        assert not errs0 and not errs, (errs0, errs)
    finally:
        close()


@needs_browser
def test_a_card_on_a_plate_that_declares_a_room_stands_in_that_room():
    """The plate's quiet zone, on the frames: the card authored no box at all and the whole of it is inside the
    rectangle the plate declared, with the same air `page_place` keeps from a page's ink."""
    at, docks, errs, close = _plate_player({}, None, room=ROOM_FRACTIONS)
    try:
        place = docks[0]["place"]
        assert place and docks[0]["place_room"] == B.PLATE_ROOM_PLACED
        room = B.plate_room_px(ROOM_FRACTIONS, "16:9")
        p = at(ENTER_A + B.DOCK_READ_S + B.DOCK_PARK_S + 1.0)
        _near(p["d0"], place)
        got = p["d0"]
        assert got["h"] > place["h"], ("the card's real height is its content's, not the prediction", got, place)
        assert got["x"] >= room["x"] and got["y"] >= room["y"], (got, room)
        assert got["x"] + got["w"] <= room["x"] + room["w"], (got, room)
        assert got["y"] + got["h"] <= room["y"] + room["h"], (got, room)
        assert not errs, errs
    finally:
        close()


@needs_browser
def test_read_then_park_works_on_a_plate_too():
    """The half the row names last: with a `read` box the card POPS at reading size, holds `read_s`, then travels
    the minimum-jerk path to its parked box over `park_s` - the choreography a page's card has had since E45."""
    read = {"centre_w": 0.52, "centre_x": 0.5, "centre_y": 0.44}
    at, docks, errs, close = _plate_player(dict(AUTHORED, read=read, read_s=1.2, park_s=0.7), None)
    try:
        d = docks[0]
        place, rplace = d["place"], d["read_place"]
        assert rplace and d["park"] is True and (d["read_s"], d["park_s"]) == (1.2, 0.7)
        assert abs(rplace["w"] - round(0.52 * 1920)) <= 1, rplace
        reading = at(ENTER_A + 1.0)["d0"]                # inside the hold: the card is at its READING box
        _near(reading, rplace)
        parked = at(ENTER_A + 1.2 + 0.7 + 0.5)["d0"]     # the park has landed: the card is at `place`
        _near(parked, place)
        mid = at(ENTER_A + 1.2 + 0.35)["d0"]             # ... and it travelled, rather than cutting
        assert min(place["x"], rplace["x"]) - 2 <= mid["x"] <= max(place["x"], rplace["x"]) + 2, (mid, rplace, place)
        assert rplace["w"] > mid["w"] > place["w"], ("it shrinks on the way", mid, rplace, place)
        assert not errs, errs
    finally:
        close()
