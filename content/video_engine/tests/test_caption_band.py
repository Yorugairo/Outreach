"""E62 (2026-09-11): under a card the caption keeps its size and MOVES; it shrinks only when no
band fits.

The compiler states the band on the dock entry - `caption_band` in stage pixels, the strip's own
rectangle - from the page's boxes and every card live in that dock's window. These tests pin the
rule on the windows that produced the ruling (the Tokyo short's two-fingers card at 0:38 and its
record + fab pair at 0:57), on the order the candidates are tried in, and on the fallback: a card
that covers every band leaves `null` and the player takes the quiet anchor.

The Tokyo pages are MEASURED (R26-51: `assets/page-boxes.v1.json` carries every page this cut
compiles, keyed by ink) and every card on them is placed by E65's ladder - so these expectations are
read off the player's own boxes and the plot's own room, not off an estimate of either.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as BST  # noqa: E402
import ledger_page as LPG  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-r51/tokyo-short.timeline.json"
STRIP_H = 143          # two lines at 64 px / 1.12
HOME_Y = 1297          # the strip's home on a short: bottom 480 (G-l)


@pytest.fixture(scope="module")
def tokyo() -> dict:
    if not TOKYO.exists():
        pytest.skip(f"the Tokyo cut is not built here ({TOKYO})")
    return json.loads(TOKYO.read_text(encoding="utf-8"))


def _scene(tl: dict, sid: str) -> dict:
    return next(sc for sc in tl["scenes"] if sc["scene_id"] == sid)


def _dock(tl: dict, sid: str, slide: str) -> dict:
    return next(d for d in _scene(tl, sid)["docks"] if d["slide"] == slide)


# ---- the strip itself --------------------------------------------------------------------------

def test_the_strip_is_two_lines_at_the_stage_size() -> None:
    """64 px at line-height 1.12, twice - the template's own numbers, not a guess."""
    assert BST.caption_strip_h() == STRIP_H
    assert BST.caption_home_y("9:16") == 1920 - 480 - STRIP_H == HOME_Y
    assert BST.caption_strip_x("9:16", "right") == (80, 800)     # the mobile safe box (doc 49 s49.1)


# ---- the Tokyo windows that produced E62 -------------------------------------------------------

def test_the_tokyo_pages_are_measured_and_carry_the_plots_room(tokyo: dict) -> None:
    """Said out loud: these bands are cut out of the PLAYER's own boxes (R26-51), and the page hands
    the placer the plot's data mask and its axis bands with them (E65)."""
    page = _scene(tokyo, "s02")["world"]["page"]
    boxes = LPG.page_boxes(page, "9:16")
    assert boxes["measured"] is True
    assert len(boxes["data_mask"]) == 16 and boxes["axis"]["x"], "E65's room travels with the boxes"


def test_the_fingers_card_leaves_the_caption_its_home_at_stage_size(tokyo: dict) -> None:
    """0:38, the card that produced the ruling: 33 px at the anchor before, 64 px in the band now.

    The two-fingers card parks at y 399-815, so the strip's home (1297-1440) is clear of it by far
    more than a line - the caption never needed to shrink, it only needed to be left where it was."""
    sc, d = _scene(tokyo, "s02"), _dock(tokyo, "s02", "dock-g-two-fingers")
    cards = BST.dock_card_boxes(sc["docks"], d["enter"], d["exit"])
    band = BST.caption_band(sc["world"]["page"], "9:16", cards)
    assert band == {"y": HOME_Y, "h": STRIP_H, "band": "quiet"}
    assert all(c["y"] + c["h"] + 72 <= band["y"] for c in cards)      # a line of clear air, at least


def test_the_record_and_plant_window_has_no_band_and_falls_back(tokyo: dict) -> None:
    """0:57, both cards up: the fab card runs to y 1318, into the strip; the page's head is title
    and sub; the measured band under the plot is 136 px, and the record's own reading box is in it.
    Nothing holds two lines clear of all three -> the quiet anchor, as it was on the estimate."""
    sc = _scene(tokyo, "s04")
    for slide in ("dock-k-pledge-record", "dock-i-fab-wafer"):
        d = _dock(tokyo, "s04", slide)
        cards = BST.dock_card_boxes(sc["docks"], d["enter"], d["exit"])
        assert len(cards) == 3, cards      # two places and the record's reading box
        assert BST.caption_band(sc["world"]["page"], "9:16", cards) is None


def test_every_tokyo_dock_window_is_stamped_and_the_band_clears_its_cards(tokyo: dict) -> None:
    """The whole cut, end to end: every dock whose window carries a caption is stamped, and every
    band written is clear of every card live in that window and of the page's data."""
    scenes = json.loads(json.dumps(tokyo["scenes"]))
    placed = BST.stamp_caption_bands(scenes, tokyo["caption_pages"], "9:16")
    stamped = [(sc, d) for sc in scenes for d in sc.get("docks", []) if "caption_band" in d]
    assert len(stamped) == 6 and placed == 4
    for sc, d in stamped:
        band = d["caption_band"]
        if band is None:
            continue
        strip = {"x": 80, "y": band["y"], "w": 800, "h": band["h"]}
        plot = LPG.page_boxes(sc["world"]["page"], "9:16")["plot"]
        assert not BST._rects_meet(strip, plot)
        for c in BST.dock_card_boxes(sc["docks"], d["enter"], d["exit"]):
            assert not BST._rects_meet(strip, c, 72)


# ---- the rule, on pages built for the purpose ---------------------------------------------------

def _page(**over: object) -> dict:
    """A minimal ledger page spec: one line series, a title, a source. The boxes are what
    `ledger_page` estimates for it - the same call every placer in the compiler makes."""
    spec = {
        "builder": "line", "variant": "line", "title": "A page", "sub": "a sub",
        "source": "a source", "quiet_zone": "right", "badges": [],
        "series": [{"name": "s", "color": "#123456",
                    "pts": [[2024.0, 1.0], [2025.0, 2.0], [2026.0, 3.0]]}],
        "axes": {"x": [2024.0, 2026.0], "y": [0.0, 4.0]},
    }
    spec.update(over)
    return spec


def test_no_card_at_all_still_answers_the_home_band() -> None:
    """With nothing on the stage the strip keeps its home - the band the player already uses."""
    assert BST.caption_band(_page(), "9:16", [])["band"] == "quiet"


def test_a_card_over_every_band_answers_none() -> None:
    """E62's own fallback: no band can hold two lines clear of the card, so the caption shrinks to
    the quiet anchor (48 px / 800 on a short) - and the compiler says so with a null."""
    cover = {"x": 0, "y": 0, "w": 1080, "h": 1920}
    assert BST.caption_band(_page(), "9:16", [cover]) is None


def test_a_card_in_the_strip_pushes_the_caption_off_its_home() -> None:
    """A card parked in the strip's home band moves the caption; it does not shrink it."""
    page = _page(title="A page")
    home = BST.caption_band(page, "9:16", [])
    card = {"x": 80, "y": home["y"] - 40, "w": 800, "h": 300}
    band = BST.caption_band(page, "9:16", [card])
    assert band is None or band["y"] != home["y"]


def test_an_unknown_card_box_is_never_guessed_at() -> None:
    """A dock with no `place` (a card on its solo CSS geometry) is a box the compiler cannot state:
    `dock_card_boxes` answers None and the band answers None - the anchor, not a guess."""
    docks = [{"slide": "a", "enter": 1.0, "exit": 9.0}]
    assert BST.dock_card_boxes(docks, 1.0, 9.0) is None
    assert BST.caption_band(_page(), "9:16", None) is None


def test_a_card_outside_this_window_is_not_an_obstacle() -> None:
    """The obstacles are the cards live in THIS dock's window - a card that has left is not one."""
    docks = [{"slide": "a", "enter": 1.0, "exit": 9.0, "place": {"x": 0, "y": 0, "w": 10, "h": 10}},
             {"slide": "b", "enter": 20.0, "exit": 30.0, "place": {"x": 0, "y": 0, "w": 10, "h": 10}}]
    assert BST.dock_card_boxes(docks, 1.0, 9.0) == [{"x": 0, "y": 0, "w": 10, "h": 10}]
    assert len(BST.dock_card_boxes(docks, 1.0, 25.0)) == 2


def test_the_band_never_lands_on_the_page_ink() -> None:
    """A caption is white type with a shadow: a strip on the title or the source line is two texts
    in one place. E45 hands a CARD the title (it is opaque, and the heading has been read); the
    caption's bands are cut against the ink as well as the data."""
    page = _page()
    boxes = LPG.page_boxes(page, "9:16")
    for cards in ([], [{"x": 80, "y": 1200, "w": 800, "h": 400}]):
        band = BST.caption_band(page, "9:16", cards)
        if band is None:
            continue
        strip = {"x": 80, "y": band["y"], "w": 800, "h": band["h"]}
        for key in ("plot", "title", "sub", "source"):
            assert not BST._rects_meet(strip, boxes[key]), (key, band)


def test_only_a_dock_window_with_a_caption_is_stamped() -> None:
    """E62 states a band where there is a caption to place; a silent window is left alone."""
    scene = {"scene_id": "s1", "world": {"kind": "ledger", "page": _page()},
             "docks": [{"slide": "a", "enter": 1.0, "exit": 5.0, "place": {"x": 0, "y": 0, "w": 10, "h": 10}},
                       {"slide": "b", "enter": 40.0, "exit": 45.0, "place": {"x": 0, "y": 0, "w": 10, "h": 10}}]}
    BST.stamp_caption_bands([scene], [{"s": 0.5, "e": 4.0, "t": []}], "9:16")
    assert "caption_band" in scene["docks"][0]
    assert "caption_band" not in scene["docks"][1]


def test_a_plain_plate_keeps_the_anchor_it_always_had() -> None:
    """No page, no bands: a dock on a plain plate is stamped null and paints exactly as before."""
    scene = {"scene_id": "s1", "world": {"asset_id": "plate-plain"},
             "docks": [{"slide": "a", "enter": 1.0, "exit": 5.0}]}
    BST.stamp_caption_bands([scene], [{"s": 0.5, "e": 4.0, "t": []}], "9:16")
    assert scene["docks"][0]["caption_band"] is None


def test_the_band_is_pure_in_its_inputs() -> None:
    """Called twice with the same page and cards it answers the same thing, and mutates neither."""
    page, cards = _page(), [{"x": 80, "y": 400, "w": 400, "h": 300}]
    before = json.dumps(page, sort_keys=True), json.dumps(cards, sort_keys=True)
    first = BST.caption_band(page, "9:16", cards)
    second = BST.caption_band(page, "9:16", cards)
    assert first == second
    assert (json.dumps(page, sort_keys=True), json.dumps(cards, sort_keys=True)) == before
