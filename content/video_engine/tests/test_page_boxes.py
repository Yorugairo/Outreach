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
    assert FIXTURE["player_sha256"] == hashlib.sha256(
        (ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html").read_bytes()).hexdigest(), (
        "the fixture was measured from a different player.html - re-run measure_page_boxes.py --write")
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
