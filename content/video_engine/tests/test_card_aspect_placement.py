"""R26-348 (P72 T46f (6)): A CARD IS PLACED AT THE ASPECT IT IS DRAWN AT.

The finding (P71 T5 round 3, bed b): the compiler parked a card at `dock_card_h(w)` - a 16:9 slide frame plus the card's
chrome - while the player draws a still card at its PICTURE's own aspect (`.slide-frame img { height: auto }`): the sell
ticket compiled 100 x 80 and drew 100 x 102, the base 197 x 134 and drew 197 x 190. Every overlap check (E45's park,
E63's read, E65's rooms, the stamp clash) measured a box ~27 % shorter than the card on the screen. A card whose row
names no `card_aspect` is now placed at the aspect the player draws it at:

  - a STILL: its picture's h / w inside the card's chrome (`PictureAspect` - the frame is `DOCK_CARD_CHROME_W` + the
    slide-frame's 2 px border narrower than the card, and `DOCK_CARD_CHROME_H` + that border taller);
  - a LIVE CHART card: the engine's chart canvas (1056 x 480) inside the same chrome;
  - a CUTOUT: its picture bare (no chrome, no rail);
  - a clip, a record, a press card, a stack, an embed, a prop: as before (their box is not the picture's).

An authored `card_aspect` (the card's whole h / w, as documented) is still the author's, and now reaches the page's
placer too (it never did: `page_place` sized every card at the default).
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import build_golden_sources as BGS  # noqa: E402
import ledger_page as LPG  # noqa: E402

SOURCES = ROOT / "content/video_engine/tests/golden/sources"
CARD = "ev-a-card"
SQUARE, TALL = (600, 600), (500, 800)   # a listing screenshot and a phone post: the two AMD shapes
ENTER, EXIT = 4.0, 20.0


def _png(path: Path, size: tuple[int, int]) -> Path:
    from PIL import Image
    Image.new("RGB", size, (236, 228, 210)).save(path)
    return path


def _drawn_h(w: float, pic: float) -> int:
    """The player's own layout of a still card `w` wide: padding 15 + 15, border 4 + 4 and the slide-frame's 2 + 2 round
    the picture; padding 13 + 13, border 4 + 4, the frame's 2 + 2 and the empty rail's 11 px foot under and over it."""
    return round((w - 42) * pic) + 49


# ---- the model: what the player draws ---------------------------------------------------------------------------------


def test_a_still_card_is_drawn_at_its_pictures_aspect_inside_the_chrome(tmp_path):
    src = _png(tmp_path / "card.png", SQUARE)
    a = B.drawn_card_aspect(src, {}, {})
    assert isinstance(a, B.PictureAspect) and float(a) == 1.0
    for w in (100, 197, 400, 922):
        assert B.card_h(w, a) == _drawn_h(w, 1.0), w
        assert abs(B.card_h(round(B.card_w_for(B.card_h(w, a), a)), a) - B.card_h(w, a)) <= 1, w


def test_a_live_chart_card_is_drawn_at_the_engines_chart_canvas(tmp_path):
    src = _png(tmp_path / "chart.png", (1400, 700))
    src.with_suffix(".series.json").write_text("{}", encoding="utf-8")
    a = B.drawn_card_aspect(src, {}, {})
    assert isinstance(a, B.PictureAspect) and abs(float(a) - 480 / 1056) < 1e-9
    assert B.card_h(1152, a) == 554, "H's tripwire board: drawn 1152 x 554 (the probe, 608.93 s)"


def test_a_cutout_is_drawn_bare(tmp_path):
    src = _png(tmp_path / "head.png", TALL)
    a = B.drawn_card_aspect(src, {}, {"cutout": True})
    assert not isinstance(a, B.PictureAspect) and float(a) == 1.6
    assert B.card_h(300, a) == 480


@pytest.mark.parametrize("meta, dopt", [({"record": {"quote": "x"}}, {}), ({"stack": ["a"]}, {}), ({}, {"press": "p"}),
                                        ({}, {"prop": True}), ({}, {"embed": "screen"})])
def test_a_card_whose_box_is_not_its_picture_keeps_the_default(tmp_path, meta, dopt):
    src = _png(tmp_path / "card.png", SQUARE)
    assert B.drawn_card_aspect(src, meta, dopt) is None


def test_a_clip_and_an_unreadable_file_keep_the_default(tmp_path):
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"\x00" * 64)
    assert B.drawn_card_aspect(clip, {}, {}) is None
    assert B.drawn_card_aspect(tmp_path / "missing.png", {}, {}) is None
    assert B.drawn_card_aspect(None, {}, {}) is None


def test_the_default_and_an_authored_aspect_are_measured_as_before():
    for w in (240, 518, 922):
        assert B.card_h(w, None) == B.dock_card_h(w)
        assert B.card_h(w, 0.62) == round(w * 0.62)
    assert B.card_w_for(400, None) == float(B._card_w_for(400))
    assert B.card_w_for(400, 0.5) == 800.0


# ---- the page's placer: E45 / E65 size the card they place -------------------------------------------------------------


def _world(aspect: str = "16:9") -> dict:
    tl = json.loads((SOURCES / "ledger-page-mid-build.timeline.json").read_text(encoding="utf-8"))
    return tl["scenes"][0]["world"]


@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
@pytest.mark.parametrize("pic", [1.0, 1.6])
def test_the_page_places_the_card_at_the_height_it_is_drawn(aspect, pic):
    world = _world()
    a = B.PictureAspect(pic)
    place = B.dock_place(world, aspect, card_aspect=a)
    assert place is not None
    assert place["h"] == B.card_h(place["w"], a), place
    boxes = LPG.page_boxes(world["page"], aspect)
    stage = boxes["stage"]
    assert place["y"] + place["h"] <= stage["h"] and place["x"] + place["w"] <= stage["w"], (place, stage)
    if place["room"] == "outside":   # E45: a band outside the plot - off the plot and the source
        for name in ("plot", "source"):
            assert B._overlap_area(place, boxes[name]) == 0, f"{name}: {place} vs {boxes[name]}"
    elif place["room"] in ("empty", "axis"):   # E65: inside the plot's frame, never on its data - the DRAWN card
        assert B.mask_is_clear(boxes, place), f"the {place['room']} room's card {place} lands on the data"


def test_a_page_with_no_aspect_is_placed_to_the_byte_as_before():
    world = _world()
    for aspect in ("16:9", "9:16"):
        assert B.dock_place(world, aspect) == B.dock_place(world, aspect, card_aspect=None)
        assert B.dock_place(world, aspect)["h"] == B.dock_card_h(B.dock_place(world, aspect)["w"])


# ---- the row loop: the card the row places is the card the player draws ------------------------------------------------


class _PastTheCard(Exception):
    """Raised once the row's card is written."""


def _bed(tmp_path, monkeypatch, docks: list, size: tuple[int, int] = SQUARE) -> dict:
    """`main()` on one ledger-page row (test_chip_stamp_reserved's bed) run until its first card is written: the card's
    real `dock_entry` and the world it stands on."""
    ep = tmp_path / "ep"
    (ep / "evidence/objects").mkdir(parents=True)
    _png(ep / "evidence/objects" / f"{CARD}.png", size)
    build = ep / "build"
    (build / "audio").mkdir(parents=True)
    shutil.copy2(BGS.SERIES, ep / "evidence/objects" / "ev-row-path.series.json")
    (build / "audio/episode.mp3").write_bytes(b"")
    (build / "timeline.json").write_text(json.dumps({"runtime_s": 30.0, "words": []}), encoding="utf-8")
    (build / "caption-pages.json").write_text("[]", encoding="utf-8")
    row = (0.0, 30.0, "ledger:ev-row-path:line", (0, 0, 0), docks, None, [])
    (ep / "SHOT-ROW-PATH.py").write_text("W = " + repr([row]) + "\n", encoding="utf-8")
    seen: dict = {}
    real_entry, real_rows = B.dock_entry, B.row_stamp_fits

    def entry(*a, **k):
        seen["card"] = real_entry(*a, **k)
        raise _PastTheCard

    def rows(*a, **k):
        seen["world"] = a[0]
        return real_rows(*a, **k)

    for name, value in (("BUILD", build), ("EP", ep), ("SHOT_TABLE_FILE", "SHOT-ROW-PATH.py"), ("ASPECT", "16:9"),
                        ("dock_entry", entry), ("row_stamp_fits", rows)):
        monkeypatch.setattr(B, name, value)
    monkeypatch.setattr(B.R, "EP", ep)
    with pytest.raises((_PastTheCard, SystemExit)) as info:
        B.main()
    assert info.type is _PastTheCard, f"the row failed: {info.value}"
    return seen


@pytest.mark.parametrize("size", [SQUARE, TALL])
def test_the_row_places_a_card_with_no_aspect_at_its_pictures(tmp_path, monkeypatch, size):
    card = _bed(tmp_path, monkeypatch, [(CARD, 0, ENTER, EXIT)], size)["card"]
    place = card["place"]
    want = _drawn_h(place["w"], size[1] / size[0])
    assert place["h"] == want, (f"the row placed the card {place['w']} x {place['h']}; the player draws it "
                                f"{place['w']} x {want} ({100.0 * (want - place['h']) / place['h']:+.1f} %)")


def test_the_row_places_an_authored_aspect_on_the_page_too(tmp_path, monkeypatch):
    card = _bed(tmp_path, monkeypatch, [(CARD, 0, ENTER, EXIT, {"card_aspect": 0.9})])["card"]
    assert card["place"]["h"] == round(card["place"]["w"] * 0.9), card["place"]


def test_the_rows_read_is_sized_at_the_drawn_aspect_too(tmp_path, monkeypatch):
    card = _bed(tmp_path, monkeypatch, [(CARD, 0, ENTER, EXIT)], TALL)["card"]
    read = card.get("read_place")
    if read:   # E63 moved the read into a band: the box it checked is the drawn card's
        assert read["h"] == _drawn_h(read["w"], 1.6), read


# ---- the frame: the compiled box IS the drawn card --------------------------------------------------------------------


def _chromium_available() -> bool:
    try:
        import served_player as SP
        pw, br = SP.launch()
        br.close()
        pw.stop()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@needs_browser
@pytest.mark.parametrize("size", [SQUARE, TALL])
def test_the_player_draws_the_card_in_the_box_the_row_placed(tmp_path, monkeypatch, size):
    import render_baseline as RB
    import served_player as SP
    seen = _bed(tmp_path, monkeypatch, [(CARD, 0, ENTER, EXIT)], size)
    entry, world = seen["card"], seen["world"]
    tl = json.loads((SOURCES / "ledger-page-mid-build.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / "ledger-page-mid-build.uris.json").read_text(encoding="utf-8"))
    tl["aspect"] = "16:9"
    tl["scenes"][0]["world"], tl["scenes"][0]["docks"], tl["scenes"][0]["species"] = world, [entry], []
    tl["evidence"] = {CARD: {"title": "a card", "source": "synthetic", "species": "deck", "badges": []}}
    uris[CARD] = B.dock_uri(tmp_path / "ep/evidence/objects" / f"{CARD}.png")
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "card.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    t = EXIT - 2.0   # read, parked and settled
    page, errs, close = SP.open_served(html, 1920, 1080, cleanup=td.cleanup)
    try:
        RB.frame_png(page, t, (1920, 1080))
        got = page.evaluate("() => { const el = document.getElementById('dock-1');"
                            " return {x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight}; }")
    finally:
        close()
    assert not errs, errs
    P = entry["place"]
    assert abs(got["w"] - P["w"]) <= 1 and abs(got["x"] - P["x"]) <= 1 and abs(got["y"] - P["y"]) <= 1, (got, P)
    assert abs(got["h"] - P["h"]) <= 1, (f"placed {P['w']} x {P['h']}, drawn {got['w']} x {got['h']} "
                                         f"({100.0 * (got['h'] - P['h']) / P['h']:+.1f} %)")
