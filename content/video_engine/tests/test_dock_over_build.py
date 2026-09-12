"""E63 (operator, 2026-09-11) - a card never READS over a ledger page's plot, drawing or finished.

*"docking over the plate while it's drawing is not a good standard practice, it's somewhat okay here
because of timing, but as a rule we should probably use better handling now that we can manipulate
scale/depth/placement easier."* Ruled on the Tokyo cut at 0:09.5-0:10.5, where the panel card enters
on "Three men", pops to its solo reading box over the middle of the plot, and the line the page is
still drawing (`build_to` 7.69 + 3.0, landing on datum 311 at 10.69) runs on underneath it.

WIDENED the same evening, on the third self-watch. The cut's build beat was re-fitted to the mount
clock (the line lands at 7.49, the card enters at 9.1), the "while it draws" qualifier stopped firing,
and the pop came back centred over the FINISHED chart: *"im confused, because you just left the dock
over the chart now too. something went backwards."* The chart's state no longer enters the decision -
it is only recorded. E45's park is untouched; only the READ moves.

The fixture is the Tokyo short's own authored table, read through `authoring.table.load_rows` and
turned into the page world by the compiler's own `world_for_plate` - no build, no browser, no file
written. Every test asks the compiler what it decided and where, and the gate what it can see.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as MPB  # noqa: E402
from authoring import table as T  # noqa: E402

TOKYO = ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break"
SHOT_TABLE = TOKYO / "SHOT-TABLE-SHORT.py"
PANEL = "dock-c-blue-ties-panel"
ASPECT = "9:16"


# ------------------------------------------------------------------ the fixture: the real row
@pytest.fixture(scope="module")
def s02() -> dict:
    """The Tokyo row the ruling was made on, as the compiler sees it: the page world, the dock's
    clock, the scene's species and the rectangle E45 parks the card in."""
    rows = T.load_rows(SHOT_TABLE)
    row = next(r for r in rows if any(str(d[0]) == PANEL for d in (r[4] or [])))
    world = B.world_for_plate(row[2], row[3], TOKYO, None)
    dock = next(d for d in row[4] if str(d[0]) == PANEL)
    return {"start": float(row[0]), "world": world, "page": world["page"], "species": list(row[6] or []),
            "place": B.dock_place(world, ASPECT), "enter": float(dock[2]), "exit": float(dock[3]),
            "windows": B.page_build_windows(world, row[6], row[0])}


@pytest.fixture(scope="module")
def story() -> dict:
    """The rule's own bench: a page the fixture has MEASURED whose free bands still hold a card at
    E45's width. The Tokyo page's own boxes are the subject of a live re-measurement (P50 T16), and
    when a page holds no card in any band at all there is no park to defer to and nothing to move -
    that is E45's problem and M25's row, not this one."""
    page = MPB.representative("story")
    place = B.page_place(page, ASPECT)
    if place is None:
        pytest.skip("the representative story page holds no card in any band")
    return {"page": page, "place": place, "boxes": LPG.page_boxes(page, ASPECT)}


def RULED_ENTER(s02: dict) -> float:
    """The card's LIVE enter - 9.1 s, after the line lands at 7.49 on the mount clock. Before the
    widening this was an enter inside the build window, because only a drawing chart counted; the
    operator's second read is exactly that the finished chart counts too."""
    return s02["enter"]


def _read(s02: dict, enter: float) -> dict | None:
    """E63's decision for the panel card entering at `enter`, everything else the row's own."""
    return B.read_over_build(s02["place"], B.dock_read_box(ASPECT), s02["page"], ASPECT,
                             enter, enter + B.DOCK_READ_S, s02["windows"])


# ------------------------------------------------------------------ the clock
def test_each_drawing_beat_is_its_own_window(s02):
    """The page's own build clock and each `build_to` - separate windows, never one span. Between the
    Tokyo caps (10.69 -> 18.95) the line RESTS on its datum (M19's hold): a card reading in that gap
    is beside a finished chart, not over a build."""
    # R26-50 (2026-09-11): a mounting page lands its own build mount_s + 3.5 s after enter (7.49 on s02, was 10.69 on the
    # roll-out clock), and the cut's build_to was re-fitted to the same clock the same evening (4.49 -> 7.49, was 7.69 -> 10.69),
    # so the page's own beat and the authored cap draw as one window again
    assert s02["windows"] == [(1.99, pytest.approx(7.49)), (pytest.approx(4.49), pytest.approx(7.49)), (18.95, pytest.approx(20.15))]
    assert B.page_build_windows({"kind": B.SPECIES_LEDGER, "page": {"enter": "spiral"}}, [], 4.0) == [], "a page that arrives BUILT never draws"
    assert B.page_build_windows({"kind": "plate", "asset_id": "plate-x"}, [], 0.0) == [], "a plain plate has no chart to draw"


def test_the_cards_solo_reading_box_is_the_players_own(s02):
    """The box `dockReadRect` measures when nothing is forced on the card - the probe read the Tokyo
    panel card at [79, 552, 801, 474] against this [80, 553, 800, 474]."""
    assert B.dock_read_box(ASPECT) == {"x": 80, "y": 553, "w": 800, "h": 474}
    assert B.dock_read_box(ASPECT, {"x": 1, "y": 2, "w": 3, "h": 4}) == {"x": 1, "y": 2, "w": 3, "h": 4}, "the row's own box wins"
    plot = LPG.page_boxes(s02["page"], ASPECT)["plot"]
    assert B._overlap_share(B.dock_read_box(ASPECT), plot) > B.READ_OVER_PLOT_SHARE, "the defect itself: the read lands on the plot"


# ------------------------------------------------------------------ the decision
def test_the_tokyo_panel_card_is_placed_in_the_plots_empty_room(s02):
    """E65 on the page that produced it. The measured page leaves NO band outside the plot that holds
    a card - the title is one line, the chart 89 px taller than the estimate - so the placer takes the
    plot's own empty room: the lower right, the quiet side the row declares, which the holdings line
    (rising to the top right) leaves clear. A place, never None; and never on the data."""
    place = s02["place"]
    assert place is not None, "E65: the placer always finds a place"
    assert place["room"] in ("empty", "axis"), f"the room this page had to offer: {place}"
    boxes = LPG.page_boxes(s02["page"], ASPECT)
    assert B.mask_is_clear(boxes, place), f"the parked card sits on the data: {place}"
    assert not any(bd for bd in B.free_bands(boxes) if B._fit_in(bd, B.DOCK_ON_PAGE_MIN_W, B._floor_h(ASPECT))), \
        "this page is the ruling's own case: no band outside the plot holds a card at all"


def test_the_tokyo_panel_cards_read_is_off_the_data(s02):
    """The ruling on the row it was ruled on, at the LIVE enter (9.1, after the 7.49 landing) - the
    frame the operator read the second time. The read is MOVED, and where it lands is the plot's own
    empty room: over the page's plot BOX, and over no ink the chart drew (E65; M25's row reads the
    ink, M27's still reads the box - see the gate)."""
    d = _read(s02, RULED_ENTER(s02))
    assert d, "the compiler saw nothing to decide on the frame the operator ruled on"
    assert d.get("read_moved"), f"E65 leaves nothing to defer to: {d}"
    to = dict(zip(("x", "y", "w", "h"), d["read_moved"]["to"]))
    boxes = LPG.page_boxes(s02["page"], ASPECT)
    assert B.mask_is_clear(boxes, to), f"the moved read lands on the data: {to}"
    assert d["read_place"] == to and d["read_moved"]["from"] == [80, 553, 800, 474]
    assert "E65" in d["read_moved"]["why"], d["read_moved"]["why"]
    assert to["h"] >= B._floor_h(ASPECT), "and never under the legibility floor"


def test_the_chart_state_does_not_change_the_decision(story):
    """The widening itself: drawing or finished, the same read on the same plot gets the same answer.
    Only `why` differs, and only to RECORD that the read fell while the chart was drawing."""
    box = B.dock_read_box(ASPECT)
    mid = B.read_over_build(story["place"], box, story["page"], ASPECT, 9.09, 10.29, [(1.0, 12.0)])
    done = B.read_over_build(story["place"], box, story["page"], ASPECT, 9.09, 10.29, [(1.0, 2.0)])
    none = B.read_over_build(story["place"], box, story["page"], ASPECT, 9.09, 10.29, [])
    assert mid and mid.get("read_moved"), f"the bench page should move this read: {mid}"
    assert mid["read_place"] == done["read_place"] == none["read_place"], \
        "the chart's state is not part of the decision any more - only of the record"
    assert "while the chart draws" in mid["read_moved"]["why"] and mid["read_moved"]["why"].endswith("12.00s"), mid["read_moved"]["why"]
    assert done["read_moved"]["why"] == "a card never reads over the plot (E63)", done["read_moved"]["why"]
    assert none["read_moved"]["why"] == done["read_moved"]["why"], "no windows at all is not an exemption"


def test_a_dock_whose_read_is_off_the_plot_is_untouched(story):
    """The rule only ever meets a read that lands on the evidence. A card that reads clear of the plot -
    a read box in the page's own free band, or a centred card with no pop at all - compiles to exactly
    the bytes it did before the rule existed, drawing or not."""
    plot = story["boxes"]["plot"]
    band = max((bd for bd in B.free_bands(story["boxes"])), key=lambda bd: bd["w"] * bd["h"])
    clear = {"x": band["x"] + 4, "y": band["y"] + 4, "w": min(300, band["w"] - 8), "h": min(120, band["h"] - 8)}
    assert B._overlap_share(clear, plot) == 0.0, f"this box has to be off the plot to mean anything: {clear} vs {plot}"
    for windows in ([(1.0, 12.0)], [(1.0, 2.0)], []):
        assert B.read_over_build(story["place"], clear, story["page"], ASPECT, 9.09, 10.29, windows) is None, \
            f"an off-plot read is untouched, windows={windows}"
    assert B.read_over_build(story["place"], None, story["page"], ASPECT, 9.09, 10.29, [(1.0, 12.0)]) is None, \
        "a CENTRED card with no pop has no read to move at all"


def test_a_dock_on_a_plate_is_untouched(s02):
    """E45: a dock on a plain plate keeps the solo card - there is no page and no plot."""
    assert B.read_over_build(None, B.dock_read_box(ASPECT), None, ASPECT, 9.09, 10.29, []) is None
    assert B.read_over_build(s02["place"], B.dock_read_box(ASPECT), None, ASPECT, 9.09, 10.29, s02["windows"]) is None
    assert B.read_over_build(s02["place"], None, s02["page"], ASPECT, 9.09, 10.29, s02["windows"]) is None, \
        "a CENTRED card has no reading pop to move - it takes its parked box from its first frame"


def test_a_page_with_room_moves_the_read_rather_than_defer():
    """Preference (a). On a page the fixture has MEASURED the band above the plot holds the card, so
    the read is re-placed there - centred, clear of the plot, never under E45's own parked width."""
    page = MPB.representative("story")
    boxes = LPG.page_boxes(page, ASPECT)
    assert boxes.get("measured"), "this test needs the fixture's own boxes"
    place = B.page_place(page, ASPECT)
    d = B.read_over_build(place, B.dock_read_box(ASPECT), page, ASPECT, 9.09, 10.29, [(1.0, 12.0)])
    assert d and d.get("read_moved"), f"a page with a band of its own should MOVE the read, not defer: {d}"
    to = d["read_place"]
    assert B._overlap_share(to, boxes["plot"]) == 0.0, f"the moved read touches the plot: {to} vs {boxes['plot']}"
    assert to["w"] >= place["w"], "the read never shrinks below the card's own parked width"
    assert to["w"] <= B.dock_read_box(ASPECT)["w"], "and never grows past the reading scale"
    assert d["read_moved"]["why"].startswith("a card never reads over the plot (E63)"), d["read_moved"]["why"]
    assert d["read_moved"]["why"].endswith("12.00s") and d["read_moved"]["to"] == [to["x"], to["y"], to["w"], to["h"]]


def test_a_page_with_no_band_reads_in_the_plots_own_room(monkeypatch):
    """Preference (b), as E65 rewrote it. Let the chart fill the page and there is no band to move the
    read to - so it goes into the plot's empty room instead of being deferred, and it lands on no ink."""
    page = MPB.representative("story")
    place = B.page_place(page, ASPECT)
    squeezed = dict(LPG.page_boxes(page, ASPECT))
    squeezed["plot"] = {"x": 80, "y": 300, "w": 800, "h": 980}
    monkeypatch.setattr(B.LPG, "page_boxes", lambda *_a, **_k: squeezed)
    got = B.read_over_build(place, B.dock_read_box(ASPECT), page, ASPECT, 9.09, 10.29, [(1.0, 12.0)])
    assert got and got.get("read_place"), f"E65: the room is the answer, not a deferral: {got}"
    assert B.mask_is_clear(squeezed, got["read_place"]), got["read_place"]
    assert "E65" in got["read_moved"]["why"]
    assert B._read_fit({"band": "above", "x": 80, "y": 280, "w": 800, "h": 40}, B.dock_read_box(ASPECT),
                       float(place["w"]), ASPECT, None, squeezed["plot"]) is None, "a 40 px band holds no card at all"


def test_a_page_with_no_room_and_no_mask_still_defers_the_read(monkeypatch):
    """The honest answer is still there for a page nobody has measured: no mask, no room to reason
    about, so the card enters at its parked box and never pops."""
    page = MPB.representative("story")
    place = B.page_place(page, ASPECT)
    squeezed = {k: v for k, v in LPG.page_boxes(page, ASPECT).items() if k != "data_mask"}
    squeezed["plot"] = {"x": 80, "y": 300, "w": 800, "h": 980}
    monkeypatch.setattr(B.LPG, "page_boxes", lambda *_a, **_k: squeezed)
    assert B.read_over_build(place, B.dock_read_box(ASPECT), page, ASPECT, 9.09, 10.29,
                             [(1.0, 12.0)]) == {"read_deferred": True}


def test_a_page_with_a_band_outside_the_plot_still_takes_it():
    """E65 changes nothing for a page that has room outside its plot: the bench page still parks in
    its own band, and the room is named `outside`."""
    page = MPB.representative("story")
    place = B.page_place(page, ASPECT)
    assert place["room"] == "outside", place
    boxes = LPG.page_boxes(page, ASPECT)
    assert B._overlap_share(place, boxes["plot"]) == 0.0, f"an outside place is outside the plot: {place}"


# ------------------------------------------------------------------ the entry the decision writes
def test_the_entry_records_the_decision_and_nothing_else_changes():
    """A dock the rule never touched compiles to the same bytes it did before E63; a MOVED read keeps
    the choreography and states where it came from; a DEFERRED read enters at the parked box (which is
    what the player's `centre` already renders) and says so."""
    place = {"x": 594, "y": 297, "w": 270, "h": 175}
    plain = B.dock_entry("dock-x", 0, 9.09, 18.95, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", False)
    assert json.dumps(plain) == json.dumps(B.dock_entry("dock-x", 0, 9.09, 18.95, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", False,
                                                        read_moved=None, read_deferred=False)), "untouched is byte-identical"
    assert "read_moved" not in plain and "read_deferred" not in plain and "centre" not in plain

    moved_box = {"x": 408, "y": 296, "w": 263, "h": 172}
    why = {"from": [80, 553, 800, 474], "to": [408, 296, 263, 172], "why": "the chart builds until 10.69s"}
    moved = B.dock_entry("dock-x", 0, 9.09, 18.95, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", False,
                         read_place=moved_box, read_moved=why)
    assert moved["read_place"] == moved_box and moved["read_moved"] == why
    assert "read_deferred" not in moved and "centre" not in moved, "a moved read still pops, then parks"

    deferred = B.dock_entry("dock-x", 0, 9.09, 18.95, 0, B.DOCK_KIND_IMAGE, place, "throw", "paper", False,
                            read_deferred=True)
    assert deferred["read_deferred"] is True and deferred["centre"] is True and "read_place" not in deferred
    assert B.dock_entry("dock-x", 0, 9.09, 18.95, 0, B.DOCK_KIND_IMAGE, None, None, None, False,
                        read_deferred=True).get("read_deferred") is None, "no place, no page: nothing to defer to"


@pytest.mark.parametrize("build_dir", ["build-short-e63", "build-short-t0", "build-short"])
def test_the_compiled_tokyo_timeline_carries_the_decision(build_dir):
    """The integration read, when a build is on disk: the panel card carries a decision, every decision
    is one of the two the rule can make, and no MOVED read lands back on its page's plot."""
    tl_path = TOKYO / build_dir / "tokyo-short.timeline.json"
    if not tl_path.is_file():
        pytest.skip(f"{tl_path} has not been built")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    pages = {d["slide"]: (s.get("world") or {}).get("page") for s in tl["scenes"] for d in (s.get("docks") or [])}
    docks = {d["slide"]: d for s in tl["scenes"] for d in (s.get("docks") or [])}
    decided = {k: v for k, v in docks.items() if v.get("read_moved") or v.get("read_deferred")}
    if not decided:
        pytest.skip(f"{build_dir} predates E63 - nothing to read")
    assert PANEL in decided, f"the row the rule was ruled on carries no decision: {sorted(decided)}"
    for slide, d in decided.items():
        assert d.get("read_deferred") or d.get("read_place"), f"{slide}: a decision with no answer in it"
        if d.get("read_place") and pages.get(slide):
            plot = LPG.page_boxes(pages[slide], tl.get("aspect") or ASPECT)["plot"]
            assert B._overlap_share(d["read_place"], plot) <= B.READ_OVER_PLOT_SHARE, \
                f"{slide}: the moved read is back on the plot: {d['read_place']} vs {plot}"


# ------------------------------------------------------------------ M27, the row that scores it
def _instant(t: float, drawn: float | None, state: str, share: int, area: int = 277066) -> dict:
    """One probed instant: a card over the page's plot while the marks say what they say."""
    return {"t": t, "why": "s02 dock reading size", "docks": [{"id": PANEL, "state": state, "box": [79, 552, 801, 474], "rest": 1}],
            "page": {"plot": [230, 464, 580, 681]}, "texts": [],
            "overlaps": [{"a": PANEL, "b": "page.plot", "area_px": area, "share_of_smaller": share}],
            "clearances": {"safe_pct": {}}, "camera": {"scene": "s02", "zoom": 1.0, "look": [540, 960]},
            "marks": {"n": 2, "drawn": drawn, "up": 1.0, "parked": False}}


# the scene the instants belong to, with the compiler's own build windows (E63: `build_windows` on the scene). Since the
# widening the windows do not decide anything - a not-parked card on the plot counts either way - they only choose the row's
# WORDS ("while the chart draws" / "on the finished chart"). `marks.drawn` is reported and never scored (the probe averages
# every drawn path and reads 0.52 on a finished line whose second path is a stub by design).
S02_SCENE = {"scene_id": "s02", "span": [1.99, 38.96], "build_windows": [[1.99, 10.69], [18.95, 20.15]], "docks": []}


def _m27(instants: list[dict], scenes: list[dict] | None = None):
    return G._over_build_gate({"aspect": ASPECT, "instants": instants}, scenes if scenes is not None else [S02_SCENE])


def test_m27_fails_a_card_reading_on_a_chart_that_is_still_drawing():
    g = _m27([_instant(10.29, 0.5, "reading", 40)])
    assert g.level == "FAIL", g.message
    assert PANEL in g.message and "0:10" in g.message and "277,066 px" in g.message and "marks 50% drawn" in g.message, g.message
    assert "while the chart draws" in g.message, g.message


def test_m27_fails_a_card_reading_on_a_chart_that_has_finished():
    """The widening, as the gate sees it: the same card on the same plot after the landing - outside
    every window - is the same defect, and the row says which frame it was."""
    g = _m27([_instant(12.0, 0.52, "reading", 40)])
    assert g.level == "FAIL", g.message
    assert "on the finished chart" in g.message and "while the chart draws" not in g.message, g.message
    assert _m27([_instant(12.0, 0.52, "reading", 40)], [{"scene_id": "s02", "span": [1.99, 38.96], "docks": []}]).level == "FAIL", \
        "a scene that never draws at all is still a page with a plot"
    assert _m27([_instant(12.0, 0.52, "reading", 40)], []).level == "FAIL", "no scenes: the frame still decides"


def test_m27_is_not_the_row_for_a_parked_card():
    assert _m27([_instant(10.04, 0.5, "parked", 40)]).level == "PASS", "a PARKED card is E45's contract and M25's row"
    assert _m27([_instant(12.0, 0.52, "parked", 40)]).level == "PASS", "and that is true after the landing too"
    assert _m27([_instant(10.29, None, "reading", 40)]).level == "FAIL", "the marks are never consulted - the frame decides"


def test_m27_warns_a_card_merely_inside_the_plots_box():
    g = _m27([_instant(10.29, 0.5, "reading", 4, area=2147)])
    assert g.level == "WARN" and "inside the plot's box" in g.message and "while the chart draws" in g.message, g.message
    done = _m27([_instant(12.0, 0.52, "reading", 4, area=2147)])
    assert done.level == "WARN" and "on the finished chart" in done.message, done.message


def test_m27_still_scores_a_read_the_compiler_answered():
    """The exemption that is not one: the entry records the decision, the frame decides. A card the
    compiler moved that STILL lands on the plot fails, and says the fix did not take."""
    scenes = [dict(S02_SCENE, docks=[{"slide": PANEL, "read_moved": {"from": [], "to": [], "why": "x"}}])]
    g = _m27([_instant(10.29, 0.5, "reading", 40)], scenes)
    assert g.level == "FAIL" and "the compiler moved this read" in g.message, g.message


def test_m27_says_so_when_the_probe_has_not_run():
    assert G._over_build_gate(None, []).level == "INFO"
    assert G._over_build_gate("stale", []).level == "INFO"
    assert G._over_build_gate({"instants": []}, []).level == "INFO"
