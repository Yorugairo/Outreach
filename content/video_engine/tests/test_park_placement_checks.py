"""P72 T53 (f), R26-413 (b) - THE PLACEMENT CHECKS READ THE PAGE AFTER A PARK.

P71 T33 (the inset echo, BOOM 08:48's stack) parks the host page left to 0.58 on "overshoots" and lands two twin cards
in the column the park freed. Three advisors WARNed as if both cards sat over the plot - T15's choose-under
(`under_choice_note`), T5's covers-the-end-names / basis-label (`text_cover_notes` over `page_text_boxes`) and E65's
no-room (the placer's "corner" copied onto a centred card) - because each read the page AS BUILT. The engine's park
(`lpPaintPark`) scales the CHART element about PARK_ORIGIN's corner (the key rail with it, the source only under
anchor=top); the checks now read that parked page at the dock's enter. Placement itself is untouched (s106: advice).

The fixture is T33's own: the committed `ev-equip-ipp-gdp-v2` page (the host's measure, full stage at 16:9) and the
twins' authored boxes, [1181, 135, 672, 378] and [1181, 529, 672, 378] (proof_t33 FORMS["stack"]).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
COMPILER = ROOT / "content/video_engine/scripts/build_scene_timeline_f.py"
EP = ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper"
PLATE = "ledger:ev-equip-ipp-gdp-v2:line::right:built:cut;idle=live;readability=longform"
ASPECT = "16:9"
TWINS = ({"x": 1181, "y": 135, "w": 672, "h": 378}, {"x": 1181, "y": 529, "w": 672, "h": 378})
PARK = {"kind": "chart_to", "at": 2.6, "dur": 1.0, "to": "park", "scale": 0.58, "anchor": "left"}
UNPARK = {"kind": "chart_to", "at": 19.8, "dur": 1.0, "to": "park", "scale": 1.0, "anchor": "left"}
PARKED = {"scale": 0.58, "anchor": "left"}


@pytest.fixture(scope="module")
def world() -> dict:
    saved = B.ASPECT
    B.ASPECT = ASPECT
    try:
        w = B.world_for_plate(PLATE, (0, 0, 0), EP)
    finally:
        B.ASPECT = saved
    return w


@pytest.fixture(scope="module")
def boxes(world) -> dict:
    return B.LPG.page_boxes(world["page"], ASPECT)


# ------------------------------------------------------------------ the park standing at the dock's enter
def test_the_park_standing_is_the_last_begun_by_the_docks_enter():
    rows = [UNPARK, {"kind": "unknown", "at": 1.0}, PARK, {"kind": "chart_to", "at": 3.0, "to": "recast", "state": 1}]
    assert B.park_standing(rows, 2.0) is None, "before the park: the page as built"
    assert B.park_standing(rows, 2.6) == PARKED, "a park begun at the enter stands (its destination)"
    assert B.park_standing(rows, 10.0) == PARKED
    assert B.park_standing(rows, 19.8) is None, "the un-park (scale 1.0) returns the page as built"
    assert B.park_standing(None, 5.0) is None and B.park_standing([], 5.0) is None
    assert B.park_standing([{"kind": "chart_to", "at": 0.0, "to": "park"}], 1.0) == {"scale": 0.72, "anchor": "top"}, \
        "the verb's defaults (scale 0.72, anchor top) - as the engine's lpPaintPark"


def test_parked_boxes_scale_the_charts_own_boxes_about_the_engines_origin(boxes):
    chart = boxes["chart"]
    for anchor, (ox, oy) in (("top", (chart["x"], chart["y"])), ("left", (chart["x"], chart["y"])),
                             ("bottom", (chart["x"], chart["y"] + chart["h"])),
                             ("right", (chart["x"] + chart["w"], chart["y"]))):
        got = B.parked_boxes(boxes, {"scale": 0.5, "anchor": anchor})
        for k in ("chart", "plot", "tags", "basis"):
            r = boxes[k]
            assert got[k] == dict(r, x=round(ox + (r["x"] - ox) * 0.5, 1), y=round(oy + (r["y"] - oy) * 0.5, 1),
                                  w=round(r["w"] * 0.5, 1), h=round(r["h"] * 0.5, 1)), (anchor, k)
        assert got["title"] == boxes["title"], "the title stands (it is not the chart's)"
        assert got["source"] == boxes["source"] or anchor == "top", "the source rides the park only under anchor=top"
    top = B.parked_boxes(boxes, {"scale": 0.5, "anchor": "top"})
    assert top["source"]["x"] == boxes["source"]["x"] and top["source"]["y"] < boxes["source"]["y"]
    assert B.parked_boxes(boxes, None) is boxes, "no park: the boxes themselves"
    assert boxes["plot"] == B.LPG.page_boxes(B.world_for_plate(PLATE, (0, 0, 0), EP)["page"], ASPECT)["plot"], \
        "pure: the page's own boxes are not moved"


def test_the_origins_are_the_engines_park_origin():
    src = ENGINE.read_text(encoding="utf-8")
    assert 'const PARK_ORIGIN = Object.freeze({ top: "0 0", bottom: "0 100%", left: "0 0", right: "100% 0" });' in src
    assert 'if (S.page && (sp.anchor || "top") === "top")' in src, "the citation rides the park under anchor=top only"


# ------------------------------------------------------------------ T15's choose-under
def test_a_twin_in_the_column_the_park_freed_is_not_asked_to_choose(world):
    for box in TWINS:
        assert B.under_choice_note(world, {}, "x", [box, None], ASPECT), "RED pin: the page as built reads it over the plot"
        assert B.under_choice_note(world, {}, "x", [box, None], ASPECT, PARKED) is None, box


def test_a_card_over_the_parked_plot_is_still_asked(world, boxes):
    plot = B.parked_boxes(boxes, PARKED)["plot"]
    over = {"x": round(plot["x"] + 100), "y": round(plot["y"] + 80), "w": 400, "h": 225}
    note = B.under_choice_note(world, {}, "shot row 1 (0.0-22.4s) dock ev-a", [over, None], ASPECT, PARKED)
    assert note and "over the chart's plot" in note and "shot row 1 (0.0-22.4s) dock ev-a" in note
    assert B.under_choice_note(world, {"under": "hover"}, "x", [over], ASPECT, PARKED) is None, "a dock that chose"


# ------------------------------------------------------------------ T5's page words
def test_a_twin_in_the_freed_column_covers_none_of_the_parked_pages_words(world):
    built = B.page_text_boxes(world["page"], ASPECT)
    parked = B.page_text_boxes_at(world["page"], ASPECT, PARKED)
    assert [n for n, _r in parked] == [n for n, _r in built], "the same words, where the parked page draws them"
    for box in TWINS:
        assert B.text_cover_notes("x", box, built), "RED pin: the end names / the basis label as built"
        assert B.text_cover_notes("x", box, parked) == [], box
    assert B.page_text_boxes_at(world["page"], ASPECT, None) == built


def test_a_card_over_the_parked_end_names_still_warns(world):
    parked = dict(B.page_text_boxes_at(world["page"], ASPECT, PARKED))
    names = parked["the end names"]
    over = {"x": round(names["x"] - 50), "y": round(names["y"] + 20), "w": 300, "h": 170}
    notes = B.text_cover_notes("shot row 1 (0.0-22.4s) dock ev-a (its park)", over, list(parked.items()))
    assert any("covers the end names" in n for n in notes), notes


# ------------------------------------------------------------------ E65's room
def test_e65_reads_a_corner_card_beside_the_parked_chart_as_the_room_the_park_freed(world, boxes):
    page = world["page"]
    for box in TWINS:
        assert B.park_freed_room("corner", box, page, ASPECT, PARKED) == "park"
        assert B.park_freed_room("corner", box, page, ASPECT, None) == "corner", "no park: as placed"
    plot = B.parked_boxes(boxes, PARKED)["plot"]
    over = {"x": round(plot["x"] + 100), "y": round(plot["y"] + 80), "w": 400, "h": 225}
    assert B.park_freed_room("corner", over, page, ASPECT, PARKED) == "corner", "a card over the parked plot still WARNs"
    for room in ("right", "above", None):
        assert B.park_freed_room(room, TWINS[0], page, ASPECT, PARKED) == room, "only the no-room corner is re-read"


# ------------------------------------------------------------------ the row loop
def test_the_row_loop_hands_the_park_at_the_docks_enter_to_all_three_checks():
    src = COMPILER.read_text(encoding="utf-8")
    i_park = src.index("_park = park_standing(row_species, float(enter))")
    i_uc = src.index("_uc = under_choice_note(")
    assert i_park < i_uc
    assert re.search(r"_uc = under_choice_note\(world, dopt, f\"shot row \{i \+ 1\} \(\{a\}-\{b\}s\) dock \{aid\}\",\n"
                     r"\s+\[eplace, _drawn_read\], ASPECT, _park\)", src)
    assert "_text = page_text_boxes_at((world or {}).get(\"page\"), ASPECT, _park)" in src
    assert re.search(r"card_rooms\.append\(\(f\"\{sid\}\.\{aid\}\", park_freed_room\(eplace\[\"room\"\], eplace, "
                     r"\(world or \{\}\)\.get\(\"page\"\),\n\s+ASPECT, _park\)", src)
    assert src.count("park_standing(") == 2, "defined once, called once - in the dock loop"
