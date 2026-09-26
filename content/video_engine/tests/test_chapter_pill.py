"""P70 T9 (was P69 T61, A34) - THE CHAPTER PILL HELD OVER AN ACT.

The Bravos harvest v2's A34 "Chapter pill held over an act's charts" (BUB 12:22; BRAVOS-USE-WHEN :969 "a long form has
named acts and each chart should say which act it is in"; the don't: "a short with no acts"). Measured off BUB itself
(the scratch record p70-t9/bravos): "Strength of the Narrative" held from 12:30.6 to 15:03.6 over a line page, a bars
page, two title-less species scenes and a blur without ever landing again, the page's title standing 16 px UNDER the
pill - the page makes room for its act (the parent's ruling, 2026-09-25: option A, the white key-rail capsule, the s90
floor).

The token - `{kind: "chapter", at, until, text}` on a shot row - is lifted into the timeline's `chapters` and painted
by the engine's `paintChapters` on the stage, above the caption and under the dip's veils: it lands on `at` by the key
rail's spring, holds across every scene inside its window, and leaves from `until` on E50's exit. Every long-form page
inside the window makes room for it (`page.chapter_room`); every row inside it reserves its box (stamps, props, cards
avoid it); the probe reads it as the page's ink (M25) and as a label among the page's labels (M28).
"""
from __future__ import annotations

import json
import math
import sys
import tempfile
from pathlib import Path

import re

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import ledger_page as LPG  # noqa: E402

ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
CARDS = ROOT / "content/video_engine/effects/cards/species.json"
PAGE = "ledger:ev-index-concentration-bars-v1:bars::right:axes:cut;idle=live;readability=longform;bar_style=soft"
PLATE = "world-paper-and-steel-press-v1;use=reset"
CH = {"kind": "chapter", "at": 363.38, "until": 431.01, "text": "The turn"}   # H: "It was never the AI stocks" -> "Railway"
WORDS = [{"w": "It", "start": 363.38, "end": 363.49}, {"w": "was", "start": 363.49, "end": 363.62},
         {"w": "AI", "start": 384.12, "end": 384.49}, {"w": "Railway", "start": 431.01, "end": 431.38},
         {"w": "Now", "start": 464.25, "end": 464.4}, {"w": "top.", "start": 465.89, "end": 466.6}]


def _errs(entries, plate=PLATE):
    return B.validate_species([json.loads(json.dumps(e)) for e in entries], (0, 0, 0), plate)


def _with(**patch):
    e = dict(CH)
    for k, v in patch.items():
        if v is None:
            e.pop(k, None)
        else:
            e[k] = v
    return e


def _plan(*species_rows):
    """A minimal shot table: (start, species) per row, a plate each."""
    return [(a, None, PLATE, (0, 0, 0), [], None, sp) for a, sp in species_rows]


# ---- the grammar -------------------------------------------------------------------------------------------------


def test_the_token_is_a_species_the_compiler_accepts_on_a_plate_and_on_a_page():
    assert _errs([CH]) == []
    assert _errs([CH], plate=PAGE) == []
    assert B.SPECIES_CHAPTER == "chapter" and "chapter" in B.SPECIES_KINDS


def test_it_points_at_nothing_and_carries_a_when():
    assert B.SPECIES_TARGETS["chapter"] == ()
    assert "act" in B.SPECIES_WHEN["chapter"].lower() and "short" in B.SPECIES_WHEN["chapter"].lower()


@pytest.mark.parametrize("key, value", [("dur", 20.0), ("target", {"kind": "region", "x0": 0, "y0": 0, "x1": 1, "y1": 1}),
                                        ("colour", "crimson")])
def test_a_key_the_pill_does_not_take_is_refused_by_name(key, value):
    errs = _errs([_with(**{key: value})])
    assert errs and any(repr(key) in e and e.startswith("chapter") for e in errs), errs


@pytest.mark.parametrize("field", ["at", "until"])
@pytest.mark.parametrize("value", [None, "363", True])
def test_at_and_until_must_be_numbers(field, value):
    errs = _errs([_with(**{field: value})]) if value is not None else _errs([_with(**{field: None})])
    assert any(e.startswith("chapter") and repr(field) in e for e in errs), errs


@pytest.mark.parametrize("text", [None, "", "   ", 7, "The\nturn"])
def test_an_unnamed_pill_is_refused(text):
    errs = _errs([_with(text=text)]) if text is not None else _errs([_with(text=None)])
    assert any(e.startswith("chapter") and "text" in e for e in errs), errs


def test_a_chapter_that_cannot_land_and_leave_is_refused():
    short = _with(until=CH["at"] + B.CHAPTER_LAND_S + B.CHAPTER_EXIT_S - 0.01)
    assert any(e.startswith("chapter") and "until" in e for e in _errs([short]))
    assert _errs([_with(until=CH["at"] + B.CHAPTER_LAND_S + B.CHAPTER_EXIT_S)]) == []


def test_the_clocks_mirror_the_engine():
    src = ENGINE.read_text(encoding="utf-8")
    assert B.CHAPTER_LAND_S == 0.36 and "LP_BADGE_IN = 0.36" in src, "the key rail's spring"
    assert abs(B.CHAPTER_EXIT_S - 16 / 30) < 1e-12 and "EXIT_S: 16 / 30" in src, "E50's exit, stopaction's STAMP_ARRIVAL"
    assert B.CHAPTER_PX == LPG.LONGFORM_KEY_PX["phone"] >= B.CHAPTER_FLOOR_PX == round(LPG.CARD_TYPE_PX, 2)


# ---- across the table ----------------------------------------------------------------------------------------------


def test_collect_finds_each_chapter_with_the_row_that_carries_it():
    plan = _plan((338.44, []), (363.38, [dict(CH)]), (384.12, []))
    got = B.collect_chapters(plan, 811.78)
    assert [(c["row"], c["span"], c["entry"]["text"]) for c in got] == [(1, (363.38, 384.12), "The turn")]


def test_a_well_formed_act_has_no_errors():
    plan = _plan((338.44, []), (363.38, [dict(CH)]), (384.12, []))
    assert B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9") == []


def test_a_chapter_on_a_short_is_refused():
    plan = _plan((363.38, [dict(CH)]), (384.12, []))
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "9:16")
    assert errs and "short" in errs[0], errs


def test_at_lands_inside_the_row_that_carries_it():
    plan = _plan((338.44, [dict(CH)]), (363.38, []), (384.12, []))   # authored on the row BEFORE its word
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9")
    assert errs and "row" in errs[0] and "363.38" in errs[0], errs


@pytest.mark.parametrize("field, value", [("at", 370.0), ("until", 431.2)])
def test_at_and_until_fall_on_words(field, value):
    e = _with(**{field: value})
    plan = _plan((338.44, []), (363.38, [e]), (384.12, []))
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9")
    assert errs and field in errs[0] and "word" in errs[0], errs


def test_until_may_be_the_end_of_the_take():
    plan = _plan((338.44, []), (363.38, [_with(until=811.78)]), (384.12, []))
    assert B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9") == []


def test_until_may_pass_the_row_s_end():
    plan = _plan((363.38, [dict(CH)]), (384.12, []), (408.60, []))
    assert B.collect_chapters(plan, 811.78)[0]["entry"]["until"] > 408.60
    assert B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9") == []


def test_two_chapters_never_overlap_their_exit_included():
    second = {"kind": "chapter", "at": 431.01, "until": 465.89, "text": "Skips a gear"}
    plan = _plan((363.38, [dict(CH)]), (431.01, [second]))
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9")
    assert errs and "overlap" in errs[0], errs   # the first is still leaving when the second lands
    later = dict(second, at=464.25)
    plan = _plan((363.38, [dict(CH)]), (464.25, [later]))
    assert B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9") == []


def test_a_pill_wider_than_the_ink_column_is_refused():
    wide = _with(text="The turn, the paper, the press and the railway share, all over again")
    plan = _plan((363.38, [wide]), (384.12, []))
    errs = B.chapter_errors(B.collect_chapters(plan, 811.78), WORDS, 811.78, "16:9")
    assert errs and "column" in errs[0], errs


# ---- the pill's box, the room, the reserve ---------------------------------------------------------------------------


def test_the_pill_stands_at_the_long_form_page_s_ink_origin_at_the_floor():
    box = B.chapter_box("The turn")
    x, y = LPG.longform_ink_origin()
    assert (box["x"], box["y"]) == (round(x, 2), round(y, 2))
    assert box["h"] == round(LPG.LONGFORM_KEY_EM["h"] * B.CHAPTER_PX, 2)
    want_w = LPG.longform_text_px("The turn", "key", B.CHAPTER_PX) + 2 * LPG.LONGFORM_KEY_EM["pad_r"] * B.CHAPTER_PX
    assert box["w"] == round(want_w, 2)


def test_the_room_is_the_pill_and_bravos_s_gap_in_whole_css_px():
    assert B.CHAPTER_GAP_PX == 16
    assert B.chapter_room_css() == math.ceil((LPG.LONGFORM_KEY_EM["h"] * B.CHAPTER_PX + 16) / LPG.PUNCH_SCALE)


def _page_world():
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        return B.world_for_plate(PAGE, (0, 0, 0), ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper")
    finally:
        B.ASPECT = saved


def _overlap(a, b):
    return max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])) * \
        max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))


def test_without_the_room_the_pill_lands_on_the_page_s_title():
    """The stop that framed option A: H's page writes its title where Bravos's pill stands."""
    boxes = LPG.page_boxes(_page_world()["page"], "16:9")
    assert _overlap(B.chapter_box("The turn"), boxes["title"]) > 0


def test_a_long_form_page_in_the_window_makes_room_and_the_pill_clears_its_ink():
    world = _page_world()
    before = LPG.page_boxes(world["page"], "16:9")
    over = B.chapters_over(B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78), 384.12, 408.60)
    assert B.chapter_page_room(world, over) == []
    assert world["page"][LPG.CHAPTER_ROOM_KEY] == B.chapter_room_css()
    after = LPG.page_boxes(world["page"], "16:9")
    shift = B.chapter_room_css() * LPG.PUNCH_SCALE
    assert abs(after["title"]["y"] - before["title"]["y"] - shift) < 0.51   # the boxes are whole px
    assert after["chart"]["y"] >= before["chart"]["y"] - 1e-6, "the chart gives up height, never climbs back into the band"
    pill = B.chapter_box("The turn")
    for k in ("title", "sub", "chart", "plot", LPG.KEY_BOX):
        if isinstance(after.get(k), dict):
            assert _overlap(pill, after[k]) == 0, k
    assert after["title"]["y"] - (pill["y"] + pill["h"]) >= B.CHAPTER_GAP_PX - 0.51, "Bravos's 16 px under the pill"


def test_a_page_outside_the_window_is_untouched():
    world = _page_world()
    over = B.chapters_over(B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78), 500.0, 520.0)
    assert over == [] and B.chapter_page_room(world, over) == [] and LPG.CHAPTER_ROOM_KEY not in world["page"]


def test_the_window_includes_the_exit():
    chs = B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78)
    assert B.chapters_over(chs, CH["until"] + B.CHAPTER_EXIT_S - 0.01, 500.0)
    assert not B.chapters_over(chs, CH["until"] + B.CHAPTER_EXIT_S, 500.0)


def test_a_page_the_pill_only_leaves_over_makes_no_room():
    """The room is the ACT's: a page that arrives on `until` - the word that ends the act - sees only the pill's exit, so
    it keeps its own layout (the bed: H row 18's page arrives on "Railway", the act's last word). The reserve still
    covers the exit: nothing is placed under a pill that is fading."""
    chs = B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78)
    assert B.chapters_over(chs, CH["until"], 463.95, leave=False) == []
    assert B.chapters_over(chs, CH["until"], 463.95) != []
    world = _page_world()
    assert B.chapter_page_room(world, B.chapters_over(chs, CH["until"], 463.95, leave=False)) == []
    assert LPG.CHAPTER_ROOM_KEY not in world["page"]


def test_a_plain_page_in_the_window_is_advised_that_it_makes_no_room():
    saved = B.ASPECT
    B.ASPECT = "16:9"
    try:
        world = B.world_for_plate("ledger:ev-index-concentration-bars-v1:bars::right:axes:cut", (0, 0, 0),
                                  ROOT / "content/video_engine/projects/systems-and-blowups/steel-and-paper")
    finally:
        B.ASPECT = saved
    over = B.chapters_over(B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78), 384.12, 408.60)
    warns = B.chapter_page_room(world, over)
    assert warns and "room" in warns[0] and LPG.CHAPTER_ROOM_KEY not in world["page"], warns


def test_a_plate_needs_no_room():
    over = B.chapters_over(B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78), 363.38, 384.12)
    assert B.chapter_page_room({"asset_id": "world-paper-and-steel-press-v1"}, over) == []


def test_every_row_in_the_window_reserves_the_pill():
    chs = B.collect_chapters(_plan((363.38, [dict(CH)]), (384.12, [])), 811.78)
    assert B.chapter_reserve(B.chapters_over(chs, 384.12, 408.60)) == [B.chapter_box("The turn")]
    assert B.chapter_reserve([]) == []


def test_a_room_page_is_never_served_a_measurement_made_without_its_room():
    world = _page_world()
    page = dict(world["page"], **{LPG.CHAPTER_ROOM_KEY: B.chapter_room_css()})
    assert LPG.page_boxes(page, "16:9")["measured"] is False


def test_the_timeline_carries_the_lifted_chapter_and_the_scene_a_compiled_copy():
    chs = B.collect_chapters(_plan((363.38, [dict(CH, id="s14.species.0")]), (384.12, [])), 811.78)
    assert B.timeline_chapters(chs) == [{"id": "s14.species.0", "text": "The turn", "at": 363.38, "until": 431.01,
                                         "box": B.chapter_box("The turn")}]
    assert B.timeline_chapters([]) == []
    assert B.compiled_chapter(dict(CH))["dur"] == round(431.01 - 363.38, 2)
    assert B.compiled_chapter({"kind": "callout", "at": 1.0, "dur": 2.0}) == {"kind": "callout", "at": 1.0, "dur": 2.0}


def test_a_timeline_with_a_chapter_carries_the_long_form_face():
    tl = {"aspect": "16:9", "scenes": [{"world": {"asset_id": "x"}}], "chapters": [{"text": "The turn"}]}
    assert B.LONGFORM_FONT_ASSET in B.longform_assets(tl)
    assert B.longform_assets({"aspect": "16:9", "scenes": [{"world": {"asset_id": "x"}}]}) == {}


# ---- the gate, the probe, the lint, the card -----------------------------------------------------------------------


def test_the_gate_credits_the_landing():
    assert G.SPECIES_EVENTS["chapter"][0] == "at"   # P70 T10 adds "swaps" (test_chapter_swap); a chapter with none credits its landing alone
    scenes = [{"span": [363.38, 384.12], "species": [B.compiled_chapter(dict(CH))]}]
    assert G._species_events(scenes) == [363.38]


def test_a_card_on_the_pill_fails_m25_and_the_page_s_title_on_it_fails_m28():
    import probe as P
    assert "page.chapter" in G.LAYOUT_INK
    pill = [67.0, 44.0, 316.0, 119.0]
    dom = {"docks": [{"el": "dock-1", "name": "dock-x", "box": [100.0, 60.0, 400.0, 300.0], "op": 1, "arriving": False, "paper": True}],
           "items": [{"k": "chapter", "box": pill, "px": 61.4, "s": 1.0, "txt": "The turn"},
                     {"k": "title", "box": [67.0, 120.0, 800.0, 48.0], "px": 44.0, "s": 1.0, "txt": "One bet"}],
           "labels": [{"role": "chapter", "text": "The turn", "box": pill},
                      {"role": "title", "text": "One bet", "box": [67.0, 120.0, 800.0, 48.0]}],
           "plots": [], "data": [], "chart": None, "caption": None, "marks": None, "bars": None}
    inst = P.derive(dom, 390.0, "test", {"scene": "s15"}, "16:9", {"dock-x": {"place": {"x": 100.0, "y": 60.0, "w": 400.0, "h": 300.0}}},
                    {"dock-x": [100.0, 60.0, 400.0, 300.0]})
    assert inst["page"]["chapter"] == [67, 44, 316, 119]
    pairs = {(o["a"], o["b"]) for o in inst["overlaps"]}
    assert ("dock-x", "page.chapter") in pairs
    fails, _warns = G._layout_faults({"instants": [inst]})
    assert any("the chapter pill" in f for f in fails), fails
    lfails, _lw, _n = G._label_faults({"instants": [inst]})
    assert any("chapter" in f and "title" in f for f in lfails), lfails


def test_m43_never_crops_the_pill_by_the_camera_s_frame():
    """The pill is STAGE chrome - the camera moves the world under it, never the pill - so M43 (a text box the camera's
    landed frame cuts partway) leaves it out, as it leaves the caption out. Found on the H bed: camera 3's 1.2x key on row
    15 'cut' the pill by 87 px off its top edge (a false FAIL; the pill stood whole)."""
    inst = {"page": {"title": [67, 190, 800, 48]},
            "labels": [{"role": "chapter", "text": "The turn", "box": [67, 43, 316, 120]},
                       {"role": "title", "text": "One bet", "box": [67, 190, 800, 48]}]}
    names = [n for n, _b in G._instant_texts(inst)]
    assert "chapter:The turn" not in names and "page.title" in names and "title:One bet" in names


def test_the_probe_reads_the_stage_s_chapter_pill():
    src = (ROOT / "content/video_engine/scripts/probe.py").read_text(encoding="utf-8")
    assert "#chapters .lp-chpill" in src


def test_lint_names_it_a_tool_of_the_setup():
    import lint_species_choice as L
    assert "chapter" in L.ACT_SPECIES["SETS"]


def test_the_card_is_the_species_card():
    cards = {c["token"]: c for c in json.loads(CARDS.read_text(encoding="utf-8"))["cards"]}
    c = cards["chapter"]
    assert c["id"] == "species:chapter" and c["when"] is None and c["status"] == "wired"
    assert c["lives"]["path"] == "docs/content-video-engine/samples/scene-evidence-engine.mjs" and c["lives"]["symbol"] == "paintChapters"
    assert c["proof"]["golden"] == "chapter-held"


# ---- the engine ----------------------------------------------------------------------------------------------------


def test_render_paints_the_chapters_right_after_the_species():
    src = ENGINE.read_text(encoding="utf-8")
    assert "  const paintChapters = (t) => {" in src
    assert "    paintSpecies(sc, t);\n    paintChapters(t);" in src
    assert "SPECIES_PAINTERS.chapter = " in src, "the declaring scene's copy is owned by a painter that draws nothing"


def test_the_long_form_title_moves_by_the_room():
    src = ENGINE.read_text(encoding="utf-8")
    assert "pg.chapter_room" in src


# ---- the golden and the served player ------------------------------------------------------------------------------


def test_the_golden_is_registered_and_taken_after_the_cut():
    import build_golden_sources as GS
    assert "chapter-held" in GS.SURFACES and "chapter-held" in GS.FRAME_T
    tl, uris = GS.SURFACES["chapter-held"]()
    assert len(tl["chapters"]) == 1 and tl["chapters"][0]["text"] == "The turn"
    cut = tl["scenes"][1]["span"][0]
    assert tl["chapters"][0]["at"] < cut < GS.FRAME_T["chapter-held"] < tl["chapters"][0]["until"]
    assert tl["scenes"][1]["world"]["page"][LPG.CHAPTER_ROOM_KEY] == B.chapter_room_css()
    assert B.LONGFORM_FONT_ASSET in uris


LANDED = re.compile(r"translateY\(0(\.0)?px\) scale\(1(\.0+)?\)")   # the spring at rest, as the browser writes it back

PROBE = """() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect(); return [r.x - stg.x, r.y - stg.y, r.width, r.height]; };
  const p = document.querySelector('#chapters .lp-chpill');
  const wB = document.getElementById('wB');
  const title = wB && wB.querySelector('.lp-title'), sub = wB && wB.querySelector('.lp-sub');
  if (!p) return null;
  const cs = getComputedStyle(p);
  return { box: R(p), op: +cs.opacity, vis: cs.visibility, px: parseFloat(cs.fontSize), text: p.textContent,
           bg: cs.backgroundColor, z: +getComputedStyle(p.parentNode).zIndex, tf: p.style.transform,
           title: title ? R(title) : null, sub: sub ? R(sub) : null };
}"""


def _served(tl: dict, uris: dict, order: list[float]) -> dict[float, dict]:
    import render_baseline as RB
    import served_player as SPL
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    out: dict[float, dict] = {}
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "ch.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        with SPL.served(html, w, h) as (page, errs):
            for t in order:
                RB.frame_png(page, t, (w, h))
                out.setdefault(t, page.evaluate(PROBE))
            assert errs == [], errs
    return out


@pytest.fixture(scope="module")
def held():
    import build_golden_sources as GS
    tl, uris = GS.SURFACES["chapter-held"]()
    ch, cut, t = tl["chapters"][0], tl["scenes"][1]["span"][0], GS.FRAME_T["chapter-held"]
    times = [ch["at"] - 0.05, ch["at"] + 0.12, ch["at"] + B.CHAPTER_LAND_S + 0.2, cut - 0.3, cut + 0.3, t]
    return tl, uris, _served(tl, uris, times), times


def test_the_pill_is_not_there_before_its_word(held):
    _tl, _u, reads, times = held
    r = reads[times[0]]
    assert r is not None and (r["op"] == 0 or r["vis"] == "hidden"), r


def test_it_lands_on_its_word_by_the_key_rail_s_spring(held):
    _tl, _u, reads, times = held
    mid, landed = reads[times[1]], reads[times[2]]
    assert 0 < mid["op"] <= 1 and "translateY(" in mid["tf"] and not LANDED.match(mid["tf"]), mid
    assert landed["op"] == 1 and LANDED.match(landed["tf"]), landed


def test_it_is_the_white_capsule_at_the_floor_over_the_caption(held):
    _tl, _u, reads, times = held
    r = reads[times[2]]
    assert r["text"] == "The turn" and r["px"] >= 59.08 and r["bg"] == "rgb(255, 255, 255)"
    assert 50 < r["z"] < 60, "above the caption (50), under E47's veils (60)"


def test_it_holds_across_the_cut_without_landing_again(held):
    _tl, _u, reads, times = held
    a, b = reads[times[3]], reads[times[4]]
    assert a["op"] == 1 and b["op"] == 1
    assert all(abs(x - y) < 3.0 for x, y in zip(a["box"], b["box"])), (a["box"], b["box"])   # E49's breath, no re-landing
    assert LANDED.match(b["tf"]), b


def test_after_the_cut_the_page_has_made_room_under_it(held):
    _tl, _u, reads, times = held
    r = reads[times[5]]
    pill, title, sub = r["box"], r["title"], r["sub"]
    assert title and pill[1] + pill[3] <= title[1], (pill, title)   # the box: never on the title, whatever the breath
    assert sub[1] >= title[1] + title[3] - 1


def test_the_golden_keeps_bravos_s_air_between_the_pill_and_the_title_s_ink():
    """Measured the way the reference was: the pill's last row and the title's first row of INK (BUB 12:35.0 / 15:12.0:
    121 -> 136 / 137, 14-15 px of air). The golden, the committed frame, keeps at least that."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(ROOT / "content/video_engine/tests/golden/frames/chapter-held.png").convert("RGB")).astype(int)
    white = a.min(2) > 235
    rows = np.nonzero(white[:, 60:400].sum(1) > 50)[0]
    pink = (a[..., 0] > 180) & (a[..., 0] - a[..., 2] > 40) & (a[..., 1] < 170)   # the long-form title's own ink
    ink = [y for y in np.nonzero(pink[:, 40:700].sum(1) > 3)[0] if y > rows.max()]
    assert ink and ink[0] - rows.max() - 1 >= 14, (rows.max(), ink[:1])


def test_the_pill_s_drawn_box_is_the_compiler_s(held):
    tl, _u, reads, times = held
    got, want = reads[times[5]]["box"], tl["chapters"][0]["box"]
    assert abs(got[0] - want["x"]) < 1.5 and abs(got[1] - want["y"]) < 3.0 and abs(got[3] - want["h"]) < 1.5
    assert abs(got[2] - want["w"]) < 4.0, (got, want)


def test_it_leaves_from_until_on_the_exit_curve_and_a_seek_is_the_play():
    import build_golden_sources as GS
    tl, uris = GS.SURFACES["chapter-held"]()
    ch = dict(tl["chapters"][0], until=round(tl["scenes"][1]["span"][0] + 1.0, 2))   # a short act, so the leave is on screen
    tl = dict(tl, chapters=[ch])
    mid, gone = ch["until"] + B.CHAPTER_EXIT_S / 2, ch["until"] + B.CHAPTER_EXIT_S + 0.02
    forward = _served(tl, uris, [ch["until"] - 0.02, mid, gone])
    scrubbed = _served(tl, uris, [gone + 3.0, 1.0, mid])
    assert forward[ch["until"] - 0.02]["op"] == 1
    assert 0.3 < forward[mid]["op"] < 1.0, forward[mid]   # the ease-IN cubic: slow first, most of it still there
    assert forward[gone]["op"] == 0 or forward[gone]["vis"] == "hidden"
    assert scrubbed[mid]["op"] == forward[mid]["op"] and scrubbed[mid]["box"] == forward[mid]["box"]


def test_a_timeline_with_no_chapter_mounts_no_chapter_layer():
    import build_golden_sources as GS
    tl, uris = GS.SURFACES["chapter-held"]()
    tl = {k: v for k, v in tl.items() if k != "chapters"}
    for sc in tl["scenes"]:
        sc["species"] = [s for s in sc.get("species") or [] if s.get("kind") != "chapter"]
    r = _served(tl, uris, [10.0])[10.0]
    assert r is None
