"""P72 T15 - `page_boxes` carries every text box, and E65's `empty` room keeps them clear (R26-253, R26-270).

R26-253 (the parent's frame read of P69 T5, 2026-09-22): on the golden full-stage page a card placed in the `empty` room
landed on the basis label (`index - 100 = Aug 2025, log scale`) - T5's red frame, the card at (167, 224). P71 T5 round 3
(R26-313, E28) already keeps the DEFAULT card door off the page's words; what stayed open was the room itself - E65's
search read the data mask alone, so the room it answered (the stamp's tie-break, the raw search) still stood on the
label, and `page_boxes` carried no box for the label at all (it was made up inside `prop_obstacle_groups`).
R26-270 (the lane-B merge review F6): a bar's name on two lines (P69 T6c) was measured against nothing - neither the
page's source line nor the caption band. It is measured now, and a name that runs into either is a WARN with its
numbers (E99 s106: the engine advises, the author decides).
"""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_golden_sources as BGS  # noqa: E402
import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as M  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

T5_RED = {"x": 167, "y": 224, "w": 382, "h": 239}   # the card R26-253 names, where the room put it before this slice


def _overlap(a: dict, b: dict) -> float:
    return (max(0.0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
            * max(0.0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])))


def _golden_page() -> dict:
    """The golden full-stage page: the prop-stamp golden's own page, compiled as a real 16:9 row compiles it."""
    tl, _uris = BGS.SURFACES["prop-stamp"]()
    return copy.deepcopy(tl["scenes"][0]["world"]["page"])


def _box(got: dict) -> dict:
    return {k: got[k] for k in ("x", "y", "w", "h")}


# ---- R26-253 (1): page_boxes carries the basis label -------------------------------------------------------------------


def test_page_boxes_carries_the_golden_pages_basis_label_as_the_player_draws_it():
    page = _golden_page()
    boxes = LPG.page_boxes(page, "16:9")
    assert boxes["measured"], "the golden full-stage page is on file"
    basis = boxes.get(LPG.BASIS_BOX)
    assert isinstance(basis, dict), f"page_boxes carries no basis label: {sorted(boxes)}"
    strip = LPG.basis_strip(boxes["plot"], boxes.get("axis"))
    assert basis != strip, "a measured page carries the label AS DRAWN, not the strip's estimate"
    assert basis["w"] < boxes["plot"]["w"] and basis["h"] <= strip["h"] + 2, (basis, strip)
    assert _overlap(basis, strip) == basis["w"] * basis["h"], f"the label {basis} stands on its line {strip}"


def test_an_unmeasured_page_states_its_basis_label_as_the_strip_and_a_page_with_none_carries_none(monkeypatch):
    page = _golden_page()
    monkeypatch.setattr(LPG, "measured_boxes", lambda spec, aspect: None)
    boxes = LPG.page_boxes(page, "16:9")
    assert not boxes["measured"]
    assert boxes[LPG.BASIS_BOX] == LPG.basis_strip(boxes["plot"], boxes.get("axis"))
    assert boxes[LPG.BASIS_BOX]["h"] == LPG.BASIS_LINE_PX, "no measured tick band: one BASIS_LINE_PX line"
    bare = copy.deepcopy(page)
    bare.setdefault("axes", {}).pop("ylabel", None)
    assert LPG.BASIS_BOX not in LPG.page_boxes(bare, "16:9")


def test_text_boxes_names_every_word_the_page_writes():
    names = [n for n, _r in LPG.text_boxes(LPG.page_boxes(_golden_page(), "16:9"))]
    for want in ("title", "sub", "source", "the basis label", "the x axis", "the y axis", "an end tag"):
        assert want in names, f"{want!r} missing from {names}"
    boxes = {"title": {"x": 0, "y": 0, "w": 10, "h": 10}, LPG.SCHEMATIC_BOX: {"x": 1, "y": 1, "w": 5, "h": 5},
             LPG.Y2_BOX: {"x": 2, "y": 2, "w": 5, "h": 5}, "sub": {"x": 0, "y": 0, "w": 0, "h": 9},
             LPG.BAR_NAMES_KEY: [{"x": 3, "y": 3, "w": 5, "h": 5, "lines": 2}, "not a box"]}
    assert LPG.text_boxes(boxes) == [("title", boxes["title"]), ("the schematic tag", boxes[LPG.SCHEMATIC_BOX]),
                                      ("the right axis", boxes[LPG.Y2_BOX]), ("a bar name", {"x": 3, "y": 3, "w": 5, "h": 5})]


# ---- R26-253 (2): the E65 room keeps them clear -------------------------------------------------------------------------


def test_T5s_red_frame_is_the_basis_label_covered():
    """The defect, stated on today's boxes: the card R26-253 names stands on the label's line and on the label."""
    boxes = LPG.page_boxes(_golden_page(), "16:9")
    assert _overlap(T5_RED, B.basis_obstacle(boxes)) > 0 and _overlap(T5_RED, boxes[LPG.BASIS_BOX]) > 0


def test_the_E65_empty_room_on_the_golden_page_keeps_the_basis_label_clear():
    """RED before this slice: the room read the data mask only and answered T5's red frame, (167, 224)."""
    page = _golden_page()
    got = B._page_place_search(page, "16:9")
    assert got["room"] == "empty", got
    assert _box(got) != T5_RED, "the room still answers T5's red frame"
    words = B.plot_words(page, "16:9")
    assert words, "the golden page states its basis inside its plot"
    for r in words + [LPG.page_boxes(page, "16:9")[LPG.BASIS_BOX]]:
        assert _overlap(got, r) == 0, f"the empty room's card {got} covers a word {r}"


def test_the_stamps_tie_break_is_the_room_it_always_was_and_the_stamp_stays_off_the_label():
    """`page_place(words=False)` is only the point `stamp_dock_place` breaks a scale tie toward - it reads the room as
    before (moving it moved the prop-stamp golden's seal 4 px for nothing: the seal is fitted round every word)."""
    page = _golden_page()
    assert _box(B.page_place(page, "16:9", words=False)) == T5_RED
    world = {"kind": B.SPECIES_LEDGER, "page": page}
    fit = B.stamp_dock_place(world, "16:9", B.dock_opts({"prop": True, "arrive": "stamp"}), None)
    label = LPG.page_boxes(page, "16:9")[LPG.BASIS_BOX]
    assert _overlap(fit, label) == 0 and _overlap(fit, B.basis_obstacle(LPG.page_boxes(page, "16:9"))) == 0, fit


def test_the_default_card_door_is_where_it_was_and_still_clear():
    """P71 T5 r3 already parked the default card off the label (the least-overlap spot at the park size): unchanged."""
    page = _golden_page()
    got = B.page_place(page, "16:9")
    assert got == {"x": 168, "y": 244, "w": 382, "h": 239, "room": "empty"}, got
    assert not any(_overlap(got, r) > 0 for _n, r in B.page_text_boxes(page, "16:9")), got


def test_the_default_park_is_still_sized_by_the_data_alone():
    """P71 T5 r4's legibility floor - the park the search gives with nothing in the way - is not shrunk by the words."""
    page = _golden_page()
    assert B._page_place_search(page, "16:9", room_words=False) == {**T5_RED, "room": "empty"}


def _representatives() -> list[tuple[str, str, dict]]:
    out = []
    for builder in M.BUILDERS:
        rep = M.representative(builder)
        for aspect in M.ASPECTS:
            if B.page_refused_at(rep, aspect):
                continue
            for key, drawn in M.variant_pages(rep, aspect).items():
                out.append((f"{builder} {key}", aspect, drawn))
    return out


REPS = _representatives()


def _as_before(monkeypatch) -> None:
    """The placer as it stood before this slice: the room read the data alone and the basis label was its line."""
    monkeypatch.setattr(B, "plot_words", lambda page, aspect: [])
    monkeypatch.setattr(B, "basis_obstacle", lambda boxes: LPG.basis_strip(boxes["plot"], boxes.get("axis")))


@pytest.mark.parametrize("name,aspect,page", REPS, ids=[r[0] for r in REPS])
def test_a_card_that_cleared_before_is_placed_exactly_where_it_was(name, aspect, page, monkeypatch):
    """Acceptance (4): every door's answer that covered none of the page's words is the answer it was, to the byte; one
    that covered a word may move (only the raw room does: the default card door and the stamp's tie-break never)."""
    words = [r for _n, r in B.page_text_boxes(page, aspect)]
    now = {"default": B.page_place(page, aspect), "raw": B._page_place_search(page, aspect),
           "tie": B.page_place(page, aspect, words=False)}
    _as_before(monkeypatch)
    before = {"default": B.page_place(page, aspect), "raw": B._page_place_search(page, aspect),
              "tie": B.page_place(page, aspect, words=False)}
    for door, box in before.items():
        if door != "raw" or not any(_overlap(box, r) > 0 for r in words):
            assert now[door] == box, f"{name} {door}: moved {box} -> {now[door]}"


def test_the_stamp_obstacle_is_the_line_it_was_where_the_label_stands_on_it_and_grows_where_it_does_not():
    boxes = LPG.page_boxes(_golden_page(), "16:9")
    strip = LPG.basis_strip(boxes["plot"], boxes.get("axis"))
    assert B.basis_obstacle(boxes) == strip, "a label inside its line: the obstacle it always was"
    wide = dict(boxes, **{LPG.BASIS_BOX: dict(boxes[LPG.BASIS_BOX], w=boxes["plot"]["w"] + 60, h=strip["h"] + 20)})
    got = B.basis_obstacle(wide)
    assert got["w"] == strip["w"] + 60 and got["h"] == strip["h"] + 20, got
    labels = dict(B.prop_obstacle_groups(_golden_page(), "16:9")[0]["label"])
    assert labels["the basis label"] == strip


# ---- R26-270: a wrapped bar name, measured against the source foot and the caption band --------------------------------


def _name_boxes(name: dict) -> dict:
    return {"source": {"x": 67, "y": 959, "w": 504, "h": 41}, "caption_anchor": {"x": 145, "y": 878, "w": 1630, "h": 82},
            LPG.BAR_NAMES_KEY: [name]}


def test_a_two_line_name_into_the_source_line_is_a_WARN_with_its_numbers():
    got = LPG.bar_name_findings(_name_boxes({"x": 300, "y": 930, "w": 180, "h": 60, "lines": 2}))
    assert any("a bar name [300, 930, 180, 60] (2 lines) runs 31 px into the source line [67, 959, 504, 41]" in w
               for w in got), got
    assert any("the caption band [145, 878, 1630, 82]" in w for w in got), got


def test_a_name_clear_of_both_or_flush_against_them_says_nothing():
    assert LPG.bar_name_findings(_name_boxes({"x": 300, "y": 800, "w": 180, "h": 78, "lines": 2})) == []
    assert LPG.bar_name_findings({"source": {"x": 0, "y": 0, "w": 9, "h": 9}}) == [], "an unmeasured page: nothing known"


def test_the_row_loop_prints_each_pages_finding_once_as_a_WARN_never_a_refusal(monkeypatch):
    world = {"kind": B.SPECIES_LEDGER, "page": _golden_page(), "page_states": [dict(_golden_page(), title="State two")]}
    monkeypatch.setattr(LPG, "page_boxes", lambda p, a="16:9": _name_boxes({"x": 300, "y": 930, "w": 180, "h": 60, "lines": 2}))
    got = B.bar_name_warns(world, "16:9")
    assert len(got) == 4 and {ink for ink, _w in got} == {LPG.page_ink_key(p) for p in [world["page"], *world["page_states"]]}
    assert got[2][1].startswith("'State two': a bar name"), got[2]
    assert B.bar_name_warns({"kind": "plate"}, "16:9") == [] and B.bar_name_warns(None, "16:9") == []
    src = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
    body = src[src.index("for _ink, _w in bar_name_warns(world, ASPECT)"):][:400]
    assert "[WARN] P72 T15: shot row" in body and "bar_names_warned" in body and "SystemExit" not in body


def _chromium_available() -> bool:
    try:
        pw, br = SP.launch()
    except Exception:
        return False
    SP.closer(pw, br)()
    return True


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

LONG_NAMES = {"title": "Two long names on capped bars", "sub": "Synthetic bars for the name-room test",
              "src": "Synthetic series for the name-room test; not a figure about the world", "unit": "%",
              "bars": [{"label": "Hyperscaler capital spending", "value": 62, "color": "crimson"},
                       {"label": "Everything else in the index", "value": 38, "color": "deemph"}]}


def _drawn(page: dict, aspect: str) -> dict:
    """The player's own read of `page` (measure_page_boxes' READ_BOXES) at the fixture's instant, served guarded."""
    import render_baseline as RB
    w, h = RB.STAGE[aspect]
    td = tempfile.TemporaryDirectory()
    html = Path(td.name) / "names.html"
    tl = M._timeline(page, aspect)
    html.write_text(RB.instantiate(tl, {"__audio__": M._silence(), **B.longform_assets(tl)}), encoding="utf-8")
    with SP.served(html, w, h, cleanup=td.cleanup) as (pg, errs):
        RB.frame_png(pg, M.MEASURE_T, (w, h))
        dom = pg.evaluate(M.READ_BOXES)
    assert not errs, errs
    return dom


@needs_browser
@pytest.mark.parametrize("aspect", ["16:9", "9:16"])
def test_a_wrapped_bar_name_is_measured_and_clears_the_foot_or_warns_with_its_numbers(aspect):
    page = LPG.build_spec(LONG_NAMES, "bars", None, "right")
    if aspect == "16:9":
        page = M.full_stage_variant(page) or page
    dom = _drawn(page, aspect)
    names = dom.get(LPG.BAR_NAMES_KEY) or []
    assert len(names) == 2, f"both names read: {names}"
    assert any(n["lines"] == 2 for n in names), f"a name wider than its capped bar takes two lines: {names}"
    boxes = dict(LPG.page_boxes(page, aspect), source=dom["source"],
                 **{LPG.BAR_NAMES_KEY: [dict(M._box(n), lines=n["lines"]) for n in names]})
    found = LPG.bar_name_findings(boxes)
    for n in boxes[LPG.BAR_NAMES_KEY]:
        for what, r in (("the source line", boxes["source"]), ("the caption band", boxes["caption_anchor"])):
            assert _overlap(n, r) == 0 or any(f"into {what}" in f for f in found), f"{n} over {what} {r}, no WARN"


@needs_browser
def test_the_golden_pages_drawn_label_is_where_page_boxes_says_and_no_room_card_covers_it():
    """The frame test (R26-253): the served golden page's drawn basis label against the room's card and the card door's."""
    page = _golden_page()
    dom = _drawn(page, "16:9")
    drawn = M._box(dom[LPG.BASIS_BOX])
    assert drawn == LPG.page_boxes(page, "16:9")[LPG.BASIS_BOX], "the fixture holds the label as the player draws it now"
    assert _overlap(T5_RED, drawn) > 0, "T5's red frame covered the drawn label"
    for got in (B._page_place_search(page, "16:9"), B.page_place(page, "16:9")):   # the room's card, the card door's
        assert _overlap(got, drawn) == 0, f"{got} covers the drawn label {drawn}"
