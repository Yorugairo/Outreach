"""E63 (operator, 2026-09-11) - a card never READS over a chart that is still drawing.

*"docking over the plate while it's drawing is not a good standard practice, it's somewhat okay here
because of timing, but as a rule we should probably use better handling now that we can manipulate
scale/depth/placement easier."* Ruled on the Tokyo cut at 0:09.5-0:10.5, where the panel card enters
on "Three men", pops to its solo reading box over the middle of the plot, and the line the page is
still drawing (`build_to` 7.69 + 3.0, landing on datum 311 at 10.69) runs on underneath it.

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


def _read(s02: dict, enter: float) -> dict | None:
    """E63's decision for the panel card entering at `enter`, everything else the row's own."""
    return B.read_over_build(s02["place"], B.dock_read_box(ASPECT), s02["page"], ASPECT,
                             enter, enter + B.DOCK_READ_S, s02["windows"])


# ------------------------------------------------------------------ the clock
def test_each_drawing_beat_is_its_own_window(s02):
    """The page's own build clock and each `build_to` - separate windows, never one span. Between the
    Tokyo caps (10.69 -> 18.95) the line RESTS on its datum (M19's hold): a card reading in that gap
    is beside a finished chart, not over a build."""
    # R26-50 (2026-09-11): a mounting page lands its own build mount_s + 3.5 s after enter (7.49 on s02, was 10.69 on the roll-out clock);
    # the build_to at 7.69 still draws to 10.69, so the panel card at 9.1 is still inside a drawing window
    assert s02["windows"] == [(1.99, pytest.approx(7.49)), (7.69, pytest.approx(10.69)), (18.95, pytest.approx(20.15))]
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
def test_the_tokyo_panel_card_does_not_read_over_the_build(s02):
    """The ruling on the row it was ruled on. The page leaves a 208 px band above the plot - not room
    for a card at E45's own width - so the read is DEFERRED: the card enters at its parked box."""
    d = _read(s02, s02["enter"])
    assert d, "the compiler saw nothing to decide on the row the operator ruled on"
    if d.get("read_moved"):
        to = dict(zip(("x", "y", "w", "h"), d["read_moved"]["to"]))
        plot = LPG.page_boxes(s02["page"], ASPECT)["plot"]
        assert B._overlap_share(to, plot) <= B.READ_OVER_PLOT_SHARE, f"the moved read still lands on the plot: {to}"
        assert d["read_place"] == to and d["read_moved"]["from"] == [80, 553, 800, 474]
    else:
        assert d == {"read_deferred": True}


def test_a_dock_that_enters_after_the_landing_is_untouched(s02):
    """The line lands at 10.69; a card entering at 12.0 reads beside a chart that is done - and the
    entry compiles to exactly the bytes it did before the rule existed."""
    assert _read(s02, 12.0) is None
    assert _read(s02, 21.0) is None, "past the second cap's landing too"
    assert _read(s02, 19.0) is not None, "but a card INSIDE the second cap's window is the same defect"


def test_a_dock_on_a_plate_is_untouched(s02):
    """E45: a dock on a plain plate keeps the solo card - there is no page, no plot and no build."""
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
    assert d["read_moved"]["why"].endswith("12.00s") and d["read_moved"]["to"] == [to["x"], to["y"], to["w"], to["h"]]


def test_a_page_with_no_band_defers_the_read(monkeypatch):
    """Preference (b). Let the chart fill the page and the rule has nowhere to put the read: the card
    enters at its parked box and never pops, which is the only honest answer left."""
    page = MPB.representative("story")
    place = B.page_place(page, ASPECT)
    squeezed = dict(LPG.page_boxes(page, ASPECT))
    squeezed["plot"] = {"x": 80, "y": 300, "w": 800, "h": 980}
    monkeypatch.setattr(B.LPG, "page_boxes", lambda *_a, **_k: squeezed)
    assert B.read_over_build(place, B.dock_read_box(ASPECT), page, ASPECT, 9.09, 10.29,
                             [(1.0, 12.0)]) == {"read_deferred": True}
    assert B._read_fit({"band": "above", "x": 80, "y": 280, "w": 800, "h": 40}, B.dock_read_box(ASPECT),
                       float(place["w"]), ASPECT, None, squeezed["plot"]) is None, "a 40 px band holds no card at all"


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


@pytest.mark.parametrize("build_dir", ["build-short-t0", "build-short"])
def test_the_compiled_tokyo_timeline_carries_the_decision(build_dir):
    """The integration read, when a build is on disk: exactly the panel card carries a decision, and
    every other dock in the cut is untouched."""
    tl_path = TOKYO / build_dir / "tokyo-short.timeline.json"
    if not tl_path.is_file():
        pytest.skip(f"{tl_path} has not been built")
    tl = json.loads(tl_path.read_text(encoding="utf-8"))
    docks = {d["slide"]: d for s in tl["scenes"] for d in (s.get("docks") or [])}
    decided = {k: v for k, v in docks.items() if v.get("read_moved") or v.get("read_deferred")}
    if not decided:
        pytest.skip(f"{build_dir} predates E63 - nothing to read")
    assert set(decided) == {PANEL}, f"E63 touched a dock it had no business touching: {sorted(decided)}"


# ------------------------------------------------------------------ M27, the row that scores it
def _instant(t: float, drawn: float | None, state: str, share: int, area: int = 277066) -> dict:
    """One probed instant: a card over the page's plot while the marks say what they say."""
    return {"t": t, "why": "s02 dock reading size", "docks": [{"id": PANEL, "state": state, "box": [79, 552, 801, 474], "rest": 1}],
            "page": {"plot": [230, 464, 580, 681]}, "texts": [],
            "overlaps": [{"a": PANEL, "b": "page.plot", "area_px": area, "share_of_smaller": share}],
            "clearances": {"safe_pct": {}}, "camera": {"scene": "s02", "zoom": 1.0, "look": [540, 960]},
            "marks": {"n": 2, "drawn": drawn, "up": 1.0, "parked": False}}


def _m27(instants: list[dict], scenes: list[dict] | None = None):
    return G._over_build_gate({"aspect": ASPECT, "instants": instants}, scenes or [])


def test_m27_fails_a_card_reading_on_a_chart_that_is_still_drawing():
    g = _m27([_instant(10.29, 0.5, "reading", 40)])
    assert g.level == "FAIL", g.message
    assert PANEL in g.message and "0:10" in g.message and "277,066 px" in g.message and "50% drawn" in g.message, g.message


def test_m27_is_not_the_row_for_a_finished_chart_or_a_parked_card():
    assert _m27([_instant(10.29, 1.0, "reading", 40)]).level == "PASS", "the chart is complete - M25's business, not this row's"
    assert _m27([_instant(10.29, 0.0, "reading", 40)]).level == "PASS", "nothing drawn yet"
    assert _m27([_instant(10.29, None, "reading", 40)]).level == "PASS", "a page with no marks to read"
    assert _m27([_instant(11.04, 0.5, "parked", 40)]).level == "PASS", "a PARKED card is E45's contract and M25's row"


def test_m27_warns_a_card_merely_inside_the_plots_box():
    g = _m27([_instant(10.29, 0.5, "reading", 4, area=2147)])
    assert g.level == "WARN" and "inside the plot's box" in g.message, g.message


def test_m27_still_scores_a_read_the_compiler_answered():
    """The exemption that is not one: the entry records the decision, the frame decides. A card the
    compiler moved that STILL lands on the plot fails, and says the fix did not take."""
    scenes = [{"docks": [{"slide": PANEL, "read_moved": {"from": [], "to": [], "why": "x"}}]}]
    g = _m27([_instant(10.29, 0.5, "reading", 40)], scenes)
    assert g.level == "FAIL" and "the compiler moved this read" in g.message, g.message


def test_m27_says_so_when_the_probe_has_not_run():
    assert G._over_build_gate(None, []).level == "INFO"
    assert G._over_build_gate("stale", []).level == "INFO"
    assert G._over_build_gate({"instants": []}, []).level == "INFO"
