"""ONE PLACEMENT TRUTH (P50 T16; R26-27, R26-22).

`ledger_page.page_boxes` used to be the compiler's ESTIMATE of where the player puts a page's ink,
and three placers - `free_bands`, `page_place`, `centred_place` - all placed against it. On a
portrait page the estimate and the player disagreed (R26-27), which is how the tea cup landed on the
chart in the sixth watch. `measure_page_boxes.py` now renders one representative page per builder
per aspect in the player itself and writes what it MEASURES to `assets/page-boxes.v1.json`;
`page_boxes` returns those boxes for any page carrying the same ink and says `measured: True`, and
falls back to the estimate (`measured: False`) for a page nobody has measured.

These tests pin: the fixture's shape, that a measured page is placed by the player's numbers and NOT
by the estimate, that the fallback is exactly today's behaviour, and R26-22 - a solo card that
arrives after E50's clock is centred in a MEASURED free band instead of parked over the title, while
an authored `centre_y` still wins and an unmeasured page keeps its parked rectangle.

No browser: every test reads the committed fixture. The measurement itself is `measure_page_boxes.py
--check`, which needs chromium and is not run here.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as M  # noqa: E402

FIXTURE = json.loads(LPG.PAGE_BOXES_FIXTURE.read_text(encoding="utf-8"))
CASES = [(b, a) for b in M.BUILDERS for a in M.ASPECTS]
PAGES = FIXTURE.get("pages") or {}

# R26-51: the ink keys of Tokyo's five compiled pages at 9:16 - the two holdings/Fed dense lines and
# the three bars states. Pinned because a fixture that quietly stops covering an episode's pages is
# exactly the staleness R26-51 closed: change a title and this list, and the measurement, must move
# with it (`measure_page_boxes.py --write --project <build dir>`).
TOKYO_9_16 = {
    "f5d19c2b33b60636": "Our biggest customer is selling",
    "33a14abf5cf88af6": "The monthly print: Japan sold, month by month",
    "f323771d22935b16": "Ten years, a year at a time",
    "392279b34c508b63": "What a Meta share is worth as the 10-year moves",
    "1fc04e19c40debcb": "The Fed hasn't moved. Your borrowing costs climbed anyway.",
}


def estimate(page: dict, aspect: str, tmp: Path) -> dict:
    """`page_boxes` with the fixture switched off - what the compiler had before T16."""
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = tmp / "no-such-fixture.json"
    try:
        return LPG.page_boxes(copy.deepcopy(page), aspect)
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


def test_the_fixture_names_every_builder_at_both_aspects_and_the_player_it_was_read_from():
    assert FIXTURE["schema"] == LPG.PAGE_BOXES_SCHEMA
    assert FIXTURE["player_sha256"] == M.template_sha(), (
        "the fixture was measured from a different player - re-run measure_page_boxes.py --write")
    assert sorted(FIXTURE["builders"]) == sorted(M.BUILDERS)
    for builder, aspect in CASES:
        entry = FIXTURE["builders"][builder][aspect]
        assert set(entry["boxes"]) == set(LPG.BOX_KEYS), f"{builder} {aspect}"
        for name, box in entry["boxes"].items():
            assert sorted(box) == ["h", "w", "x", "y"] and all(isinstance(v, int) for v in box.values()), f"{builder} {aspect} {name}"
        assert entry["ink"] == LPG.page_ink_key(M.representative(builder)), f"{builder}: the fixture describes another page"


@pytest.mark.parametrize("builder, aspect", CASES)
def test_a_measured_page_is_placed_by_the_players_own_numbers(builder, aspect, tmp_path):
    page = M.representative(builder)
    boxes = LPG.page_boxes(page, aspect)
    assert boxes["measured"] is True
    for key in LPG.BOX_KEYS:
        assert boxes[key] == FIXTURE["builders"][builder][aspect]["boxes"][key], f"{builder} {aspect} {key}"
    est = estimate(page, aspect, tmp_path)
    assert est["measured"] is False
    assert any(est[k] != boxes[k] for k in LPG.BOX_KEYS), (
        f"{builder} {aspect}: the measurement agrees with the estimate in every box - "
        "a fixture that changes nothing is not evidence of anything")


def test_the_portrait_band_below_the_plot_is_the_players_own_not_the_estimates(tmp_path):
    """R26-27 in one page: the 9:16 bars page. The estimate runs the plot to the source line and
    leaves a 42 px sliver under it; the player stops the plot 94 px short, and the band a card is
    centred in is the one the player draws."""
    page = M.representative("story")
    got = {b["band"]: b for b in B.free_bands(LPG.page_boxes(page, "9:16"))}
    was = {b["band"]: b for b in B.free_bands(estimate(page, "9:16", tmp_path))}
    assert (was["below"]["y"], was["below"]["h"]) == (1188, 42), "the estimate, for the record"
    assert (got["below"]["y"], got["below"]["h"]) == (1136, 94), "the player's own band under the plot"
    assert got["below"] == {"band": "below", **FIXTURE["builders"]["story"]["9:16"]["bands"]["below"]}
    plot, src = LPG.page_boxes(page, "9:16")["plot"], LPG.page_boxes(page, "9:16")["source"]
    assert got["below"]["y"] == plot["y"] + plot["h"] and got["below"]["y"] + got["below"]["h"] == src["y"], (
        "the band below the plot runs from the plot's foot to the source line, and nowhere else")


@pytest.mark.parametrize("builder, aspect", CASES)
def test_the_bands_on_file_are_the_bands_free_bands_cuts(builder, aspect):
    """One cutter. The fixture RECORDS the bands so a reader can see them; `free_bands` cuts them,
    and if the two ever drift the fixture is a second opinion, which is the thing T16 removes."""
    cut = {b["band"]: {k: b[k] for k in ("x", "y", "w", "h")}
           for b in B.free_bands(LPG.page_boxes(M.representative(builder), aspect))}
    assert cut == FIXTURE["builders"][builder][aspect]["bands"]


def test_a_page_the_fixture_never_saw_keeps_todays_estimate(tmp_path):
    page = dict(M.representative("dense-line"), title="A title nobody has ever measured")
    boxes = LPG.page_boxes(page, "9:16")
    assert boxes["measured"] is False
    assert all(boxes[k] == estimate(page, "9:16", tmp_path)[k] for k in LPG.BOX_KEYS), (
        "the fallback is not a new layout - it is exactly the model that shipped before T16")


def test_a_builder_absent_from_the_fixture_falls_back(tmp_path):
    thin = tmp_path / "page-boxes.v1.json"
    thin.write_text(json.dumps({"schema": LPG.PAGE_BOXES_SCHEMA, "builders": {"treemap": FIXTURE["builders"]["treemap"]}}),
                    encoding="utf-8")
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = thin
    try:
        assert LPG.page_boxes(M.representative("story"), "9:16")["measured"] is False
        assert LPG.page_boxes(M.representative("treemap"), "9:16")["measured"] is True
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


@pytest.mark.parametrize("broken", [{"schema": "page_boxes.v0"}, {"builders": "not a map"}, "[]"])
def test_a_missing_or_malformed_fixture_is_never_a_build_failure(broken, tmp_path):
    bad = tmp_path / "page-boxes.v1.json"
    bad.write_text(broken if isinstance(broken, str) else json.dumps(broken), encoding="utf-8")
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = bad
    try:
        assert LPG.page_boxes(M.representative("story"), "9:16")["measured"] is False
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved
    LPG.PAGE_BOXES_FIXTURE = tmp_path / "nothing-here.json"
    try:
        assert LPG.page_boxes(M.representative("story"), "9:16")["measured"] is False
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


def test_the_ink_key_is_everything_that_moves_a_box_and_nothing_else():
    page = M.representative("story")
    same_data_elsewhere = copy.deepcopy(page)
    same_data_elsewhere["values"] = [v for v in reversed(page.get("values") or [])]
    same_data_elsewhere["emphasize"] = 1
    assert LPG.page_ink_key(same_data_elsewhere) == LPG.page_ink_key(page), (
        "the DATA is drawn inside the plot: it cannot move a box, so it cannot change the key")
    for moved in (dict(page, title="Another title"), dict(page, quiet_zone="left"),
                  dict(page, badges=[{"label": "X", "value": "1", "tag": "t"}]),
                  dict(page, source="Another source line")):
        assert LPG.page_ink_key(moved) != LPG.page_ink_key(page)


# ---- R26-22: the solo card, centred by E50's clock, in a band the player drew -------------------
LAND = 7.4   # PAGE_BUILD_END_S: a rolled-out page's chart lands 7.4 s after the scene starts


def world(builder: str = "story") -> dict:
    return {"kind": B.SPECIES_LEDGER, "page": M.representative(builder), "ken_burns": {"scale": 0, "x": 0, "y": 0}}


def test_a_solo_card_after_the_pages_clock_is_centred_on_a_measured_page():
    w = world()
    assert B.page_is_measured(w, "9:16") is True
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0 + LAND, 20.0, {}) is True, "the chart has landed: the page is being read"
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0 + LAND - 0.1, 20.0, {}) is False, "still building: the card would cover the build"


def test_a_centred_solo_card_lands_in_a_measured_free_band_and_never_on_the_plot():
    w = world()
    boxes = LPG.page_boxes(w["page"], "9:16")
    card = B.centred_place(B.page_place(w["page"], "9:16"), "9:16", None, w["page"])
    bands = B.free_bands(boxes)
    assert any(bd["y"] <= card["y"] and card["y"] + card["h"] <= bd["y"] + bd["h"] + 1 for bd in bands), (
        f"the card at {card} is in none of the page's free bands {bands}")
    plot = boxes["plot"]
    assert card["y"] + card["h"] <= plot["y"] or card["y"] >= plot["y"] + plot["h"], (
        f"E45: a dock never covers the chart - card {card} against plot {plot}")


def test_a_pair_a_press_pile_and_an_authored_centre_are_never_auto_centred():
    w = world()
    assert B.solo_centre_by_clock(w, "9:16", 2, 0, 20.0 + LAND, 20.0, {}) is False, "a pair keeps the layout its slots declare"
    assert B.solo_centre_by_clock(w, "9:16", 1, 1, 20.0 + LAND, 20.0, {}) is False, "slot 1 is not the solo card"
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0 + LAND, 20.0, {"centre": True, "centre_y": 0.4}) is False, (
        "an authored centre outranks the clock - the caller centres it on the author's own box")
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0 + LAND, 20.0, {"press": {"source": "x"}}) is False
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0 + LAND, 20.0, {"stack": True}) is False


def test_an_unmeasured_page_keeps_its_parked_rectangle():
    """The conservative half of R26-22: the compiler will not centre a card in a band it only has an
    ESTIMATE of - that estimate is what put the tea cup on the chart."""
    w = {"kind": B.SPECIES_LEDGER, "page": dict(M.representative("story"), title="A page nobody measured")}
    assert B.page_is_measured(w, "9:16") is False
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0 + LAND, 20.0, {}) is False
    assert B.solo_centre_by_clock({"kind": "plate"}, "9:16", 1, 0, 99.0, 0.0, {}) is False, "a plain plate keeps the solo card (E45)"


def test_a_page_that_arrives_built_has_landed_at_its_first_frame():
    """E50's clock is the gate's own (`_page_land_offset`): a page that arrives BUILT has no build to
    cover, so a card entering with it is already reading the page."""
    w = world()
    w["page"]["enter"] = "built"
    assert B.solo_centre_by_clock(w, "9:16", 1, 0, 20.0, 20.0, {}) is True


# ---- R26-51: an EPISODE'S OWN pages, keyed by ink --------------------------------------------
# A builder has one representative here; Tokyo writes five pages and every one of them was an
# ESTIMATE until `--project` measured it. The `pages` section is keyed by ink key, is read before
# the per-builder representative, and is covered by the same `player_sha256` assertion above.


def test_every_page_the_projects_compiled_is_on_file_at_the_aspect_it_was_measured():
    assert isinstance(FIXTURE.get("projects"), list) and FIXTURE["projects"], (
        "the fixture records the compiled timelines its pages were measured from")
    for name in FIXTURE["projects"]:
        assert name.endswith(".timeline.json"), name
        assert not Path(name).is_absolute(), f"{name}: the record is repo-relative"
    for ink, by_aspect in PAGES.items():
        assert by_aspect, f"{ink}: an entry with no aspect measures nothing"
        for aspect, entry in by_aspect.items():
            assert aspect in M.ASPECTS, f"{ink} {aspect}"
            assert entry["ink"] == ink, f"{ink}: the entry describes another page"
            assert entry["timeline"] in FIXTURE["projects"], f"{ink}: measured from an unrecorded timeline"
            assert set(entry["boxes"]) == set(LPG.BOX_KEYS), f"{ink} {aspect}"
            for name, box in entry["boxes"].items():
                assert sorted(box) == ["h", "w", "x", "y"] and all(isinstance(v, int) for v in box.values()), (
                    f"{ink} {aspect} {name}")


def test_tokyos_five_pages_are_measured_at_portrait():
    """The episode that made R26-51: its first page's title is ONE line where the model says two,
    which moves every box under it by 76 px (R26-27, again)."""
    for ink, title in TOKYO_9_16.items():
        entry = PAGES.get(ink, {}).get("9:16")
        assert entry is not None, f"{title!r} ({ink}) is not measured - re-run --write --project"
        assert entry["title"] == title, f"{ink}: {entry['title']!r} is not {title!r}"


def test_a_page_measured_by_ink_is_placed_by_the_players_numbers_not_the_estimate(tmp_path):
    """Tokyo's dense-line page and the golden dense-line representative share a BUILDER and differ
    in ink - which is why an episode's pages cannot live in the per-builder section at all."""
    ink = "f5d19c2b33b60636"
    boxes = PAGES[ink]["9:16"]["boxes"]
    rep = LPG.page_ink_key(M.representative("dense-line"))
    assert ink != rep, "the fixture would be describing one page with another page's boxes"
    assert boxes != FIXTURE["builders"]["dense-line"]["9:16"]["boxes"], (
        "two different pages measured identically - one of them was not measured")


def _fixture_file(tmp_path: Path, builders: dict, pages: dict) -> Path:
    path = tmp_path / "page-boxes.v1.json"
    path.write_text(json.dumps({"schema": LPG.PAGE_BOXES_SCHEMA, "builders": builders, "pages": pages}),
                    encoding="utf-8")
    return path


def _shifted(entry: dict, ink: str, dy: int) -> dict:
    boxes = {k: dict(v, y=v["y"] + dy) for k, v in entry["boxes"].items()}
    return {"ink": ink, "title": entry.get("title"), "boxes": boxes, "bands": entry.get("bands", {})}


def test_the_ink_keyed_entry_is_read_before_the_builders_representative(tmp_path):
    page = M.representative("story")
    ink = LPG.page_ink_key(page)
    rival = _shifted(FIXTURE["builders"]["story"]["9:16"], ink, 7)
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = _fixture_file(tmp_path, FIXTURE["builders"], {ink: {"9:16": rival}})
    try:
        boxes = LPG.page_boxes(page, "9:16")
        assert boxes["measured"] is True
        assert boxes["plot"]["y"] == FIXTURE["builders"]["story"]["9:16"]["boxes"]["plot"]["y"] + 7, (
            "the per-builder representative won over this page's own measurement")
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


def test_the_builder_entry_still_serves_a_page_the_pages_section_never_saw(tmp_path):
    page = M.representative("story")
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = _fixture_file(
        tmp_path, FIXTURE["builders"], {"0" * 16: {"9:16": _shifted(FIXTURE["builders"]["story"]["9:16"], "0" * 16, 9)}})
    try:
        boxes = LPG.page_boxes(page, "9:16")
        assert boxes["measured"] is True
        for key in LPG.BOX_KEYS:
            assert boxes[key] == FIXTURE["builders"]["story"]["9:16"]["boxes"][key], key
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


def test_an_ink_keyed_entry_for_another_page_is_never_borrowed(tmp_path):
    """The ink is the entry's own validity: an entry filed under a key it does not carry is ignored,
    not applied to whatever page asked."""
    page = M.representative("story")
    ink = LPG.page_ink_key(page)
    lying = _shifted(FIXTURE["builders"]["story"]["9:16"], "not-this-page", 11)
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = _fixture_file(tmp_path, {}, {ink: {"9:16": lying}})
    try:
        assert LPG.page_boxes(page, "9:16")["measured"] is False
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


def test_the_timeline_reader_takes_the_page_and_every_state_and_never_re_derives_one(tmp_path):
    """`--project` reads what the compiler WROTE: the world's page and each `page_states` entry,
    deduplicated by ink, at the aspect the timeline declares."""
    page = dict(M.representative("story"), enter="spiral", exit="cut", mount_s=2.0)
    other = dict(M.representative("tiers"))
    tl = tmp_path / "x.timeline.json"
    tl.write_text(json.dumps({"aspect": "9:16", "scenes": [
        {"world": {"page": page, "page_states": [page, other]}}, {"world": {}}]}), encoding="utf-8")
    aspect, pages = M.timeline_pages(tl)
    assert aspect == "9:16"
    assert sorted(pages) == sorted({LPG.page_ink_key(page), LPG.page_ink_key(other)})
    assert all(k not in got for got in pages.values() for k in M.TRANSIENT), (
        "a page is measured on its plain roll-out clock, never on how it arrives")
    assert M.project_timeline(tmp_path) == tl


# ---- E65: the plot's own room - the data mask and the axis bands ------------------------------
# A page's boxes said where the ink is; they did not say where the ink ISN'T. E65 places a card in
# the plot's empty room when no band outside it holds one, so the fixture measures the data's own
# footprint (a 16 x 16 mask over the plot) and the axis bands a card may partially overlap.
PROBE = (ROOT / "content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-r51/layout-probe.json")


def entries():
    """Every measured entry on file: the per-builder representatives and the projects' own pages."""
    for builder, by_aspect in FIXTURE["builders"].items():
        for aspect, entry in by_aspect.items():
            yield f"{builder} {aspect}", aspect, entry
    for ink, by_aspect in PAGES.items():
        for aspect, entry in by_aspect.items():
            yield f"{entry.get('builder')} {ink} {aspect}", aspect, entry


def test_every_measured_entry_carries_the_plots_data_mask_and_its_axis_bands():
    for name, _aspect, entry in entries():
        mask = entry["data_mask"]
        assert isinstance(mask, list) and len(mask) == 16, name
        assert all(isinstance(row, str) and len(row) == 16 and set(row) <= {"0", "1"} for row in mask), name
        assert "1" in "".join(mask), f"{name}: a plot with no data ink at all was not measured"
        axis = entry["axis"]
        assert sorted(axis) == ["x", "y"], name
        for box in axis.values():
            assert box is None or (sorted(box) == ["h", "w", "x", "y"] and all(isinstance(v, int) for v in box.values())), name


def test_the_axis_bands_sit_under_and_beside_the_plot_never_on_it():
    """The x tick labels are below the plot's own box (or inside its foot, on a page whose plot was
    widened over them); the y tick column is to its left. Both are furniture: E65 lets a card
    partially overlap them, which is only safe because they are not the data."""
    for name, _aspect, entry in entries():
        plot, axis = entry["boxes"]["plot"], entry["axis"]
        if axis["x"]:
            assert axis["x"]["y"] + axis["x"]["h"] >= plot["y"] + plot["h"] - 2, f"{name}: the x labels are not under the plot"
        if axis["y"]:
            assert axis["y"]["x"] < plot["x"] + plot["w"] / 2, f"{name}: the y labels are not beside the plot"


def test_the_tokyo_masks_say_which_corner_each_chart_leaves_empty():
    """The ruling's own page: the holdings line rises to the top right, so the mask's ink runs from
    the bottom left to the top right and the room is the LOWER right - the quiet side the row
    declares. The Meta bars fill their plot, which is why that page falls through to the axis."""
    holdings = PAGES["f5d19c2b33b60636"]["9:16"]["data_mask"]
    assert "1" in "".join(holdings[:4]), "the line's top: the first rows carry ink"
    assert all(c == "0" for row in holdings[:4] for c in row[:6]), "the upper LEFT is empty"
    assert all(c == "0" for row in holdings[11:] for c in row[8:]), "and so is the lower RIGHT - the quiet side"
    assert any(row[12] == "1" for row in holdings[:6]), "the line ends high on the right"
    meta = PAGES["392279b34c508b63"]["9:16"]["data_mask"]
    assert sum(row.count("1") for row in meta) > 200, "the Meta bars fill their plot"


def test_the_mask_and_the_players_own_ink_read_are_the_same_ink():
    """The mask is measured through the player the same way probe.py reads the data for M25. On the
    built cut, the data's box at an instant where the holdings chart stands finished maps onto the
    mask's ink within a cell either way - the camera's push and the page's park are why it is not to
    the pixel. Skipped when the cut is not built here (a build directory is an artifact)."""
    if not PROBE.exists():
        pytest.skip(f"the Tokyo cut is not built here ({PROBE})")
    doc = json.loads(PROBE.read_text(encoding="utf-8"))
    shot = next((i for i in doc["instants"] if 11.0 <= i["t"] <= 13.0 and i["page"].get("data")), None)
    if shot is None:
        pytest.skip("no probed instant holds the finished holdings chart")
    plot, data = shot["page"]["plot"], shot["page"]["data"]
    mask = PAGES["f5d19c2b33b60636"]["9:16"]["data_mask"]
    n = len(mask)
    ink = [(r, c) for r in range(n) for c in range(n) if mask[r][c] == "1"]
    cells = ((data[0] - plot[0]) / plot[2] * n, (data[1] - plot[1]) / plot[3] * n,
             (data[0] + data[2] - plot[0]) / plot[2] * n, (data[1] + data[3] - plot[1]) / plot[3] * n)
    for got, want, edge in ((cells[0], min(c for _r, c in ink), "left"), (cells[1], min(r for r, _c in ink), "top"),
                            (cells[2], max(c for _r, c in ink) + 1, "right"), (cells[3], max(r for r, _c in ink) + 1, "bottom")):
        assert abs(got - want) <= 2.0, f"the {edge} of the data: the probe reads {got:.1f}, the mask says {want}"
