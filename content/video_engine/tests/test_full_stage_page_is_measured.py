"""R26-235 - A FULL-STAGE PAGE IS SERVED THE MEASURED FIXTURE (2026-09-22).

R26-205 made the 16:9 ledger page the plate: the compiler stamps the row `full_stage` and the same ink
goes into `ledger_page._landscape_full_boxes` instead of `_landscape_boxes`. Nothing had ever MEASURED
that geometry, so `measured_entry` refused the fixture to a full-stage page and every card and every
camera move on a 16:9 page was placed by the ESTIMATE. The cost was E65's rooms: `mask_rooms` and
`axis_room` both need the measured `data_mask`, so a card on a full-stage page fell through `outside`
to `corner` - the emptiest quadrant at the legibility floor, 100 x 80 px, which is why the Steel and
Paper H bed's certificate had to name its own rectangle by hand.

THE KEY. A page's boxes are a function of its INK (`page_ink_key`) and of the GEOMETRY that ink is
drawn in. The geometry has always been the fixture's second key - the aspect - so the flag goes THERE
and not in the ink key: `16:9` and `16:9|full_stage` (`ledger_page.box_key`), measured separately by
`measure_page_boxes.variant_pages`, and every entry carries its own `full_stage` so an entry can never
be served to a page drawn in the other geometry. (The flag in the INK key was tried and reverted in
R26-205: the key does not know the aspect, so a caller that stamps a page with the compiler's `ASPECT`
unset and asks at 9:16 re-keyed every portrait page on file.)

WHAT THE MEASUREMENT CHANGED, and what it did not. The plot is the real one (y 198 -> 208, h 680 ->
666) and the title, source and rail carry their DRAWN widths instead of the ink column's - and the
entry carries the `data_mask` and the `axis` bands, which is what gives a card a real room. What the
measurement does NOT move is the title's own top edge: the estimate and the frame agree on y 44 to the
pixel, so R26-220's reachable zoom is 1.08 on both. The 1.3 px that row measured off the frame is the
page's KEN BURNS - `page_boxes` models no ken at either aspect, and the fixture is measured with the
ken zeroed (`measure_page_boxes._timeline`) - which the last rendered test here pins as a single scale
about the stage's centre rather than as a tolerance.
"""
from __future__ import annotations

import copy
import json
import math
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(ROOT / "content/video_engine/tests/golden"))

import build_scene_timeline_f as B  # noqa: E402
import ledger_page as LPG  # noqa: E402
import measure_page_boxes as MPB  # noqa: E402
import render_baseline as RB  # noqa: E402

STAGE_W, STAGE_H = LPG.STAGE_PX["16:9"]
SURFACE = "ledger-page-mid-build"     # the dense-line golden: the page the H bed's own s01 draws (same ink)
PROBE_T = MPB.MEASURE_T               # 20 s - past the page's whole build, the instant the fixture is read at
FULL = "16:9|full_stage"
FIXTURE = json.loads(LPG.PAGE_BOXES_FIXTURE.read_text(encoding="utf-8"))
TOL = 2.0                             # the brief's own bar: the measured boxes agree with the frame to 2 px


def _golden_page() -> dict:
    """The dense-line golden's page as the compiler wrote it, on its plain roll-out clock."""
    tl = json.loads((RB.SOURCES / f"{SURFACE}.timeline.json").read_text(encoding="utf-8"))
    world = next(s["world"] for s in tl["scenes"] if (s.get("world") or {}).get("page"))
    return {k: v for k, v in world["page"].items() if k not in MPB.TRANSIENT}


def _stamped(page: dict | None = None) -> dict:
    """The page as the compiler stamps it at 16:9 - the stamp itself, never a hand-typed pair."""
    return MPB.full_stage_variant(page if page is not None else _golden_page())


def _estimate(page: dict, aspect: str, tmp: Path) -> dict:
    """`page_boxes` with the fixture switched off - what the compiler had before this row."""
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = tmp / "no-such-fixture.json"
    try:
        return LPG.page_boxes(copy.deepcopy(page), aspect)
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


def _fixture_file(tmp: Path, builders: dict) -> Path:
    tmp.mkdir(parents=True, exist_ok=True)
    path = tmp / "page-boxes.v1.json"
    path.write_text(json.dumps({"schema": LPG.PAGE_BOXES_SCHEMA, "builders": builders}), encoding="utf-8")
    return path


def _served(page: dict, aspect: str, fixture: Path) -> dict:
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = fixture
    try:
        return LPG.page_boxes(copy.deepcopy(page), aspect)
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved


# ---- the key: the aspect, with the flag on it ---------------------------------------------------

def test_the_geometry_key_is_the_aspect_with_the_full_stage_flag_on_it():
    page = _golden_page()
    assert LPG.box_key(page, "16:9") == "16:9"
    assert LPG.box_key(page, "9:16") == "9:16"
    assert LPG.box_key(_stamped(page), "16:9") == FULL
    assert LPG.box_key(_stamped(page), "9:16") == "9:16", "a portrait page has one geometry"
    # the flag is NOT ink, and the ink key does not move (R26-205's own lesson, re-pinned)
    assert LPG.page_ink_key(_stamped(page)) == LPG.page_ink_key(page)


def test_the_variants_are_the_geometries_the_compiler_actually_writes():
    page = _golden_page()
    assert list(MPB.variant_pages(page, "16:9")) == ["16:9", FULL]
    assert list(MPB.variant_pages(page, "9:16")) == ["9:16"]
    # a host plate is never stamped (its board was measured around a hand), so it has ONE 16:9 geometry
    host = dict(page, chart_box={"x": 0.1, "y": 0.1, "w": 0.5, "h": 0.5})
    assert list(MPB.variant_pages(host, "16:9")) == ["16:9"]
    assert MPB.full_stage_variant(host) is None
    assert MPB.full_stage_variant(dict(page, punch=False)) is None
    # a page that ALREADY carries the stamp (a 16:9 project's compiled page) measures once, under its own key
    assert list(MPB.variant_pages(_stamped(page), "16:9")) == [FULL]


def test_the_stamp_is_the_compilers_own_and_the_aspect_global_cannot_lose_it(monkeypatch):
    """`stamp_full_stage` reads `ASPECT`, and this tool measures both aspects in one process: a 9:16
    build's global must not make the 16:9 variant silently disappear."""
    monkeypatch.setattr(B, "ASPECT", "9:16")
    assert list(MPB.variant_pages(_golden_page(), "16:9")) == ["16:9", FULL]
    assert B.ASPECT == "9:16", "the global is restored, not left where the measurement wanted it"


# ---- the fixture on disk -----------------------------------------------------------------------

def test_the_fixture_measures_both_16x9_geometries_for_every_builder():
    for builder in MPB.BUILDERS:
        entries = FIXTURE["builders"][builder]
        assert sorted(entries) == ["16:9", FULL, "9:16"], builder
        plain, full = entries["16:9"], entries[FULL]
        assert full["full_stage"] is True, builder
        assert "full_stage" not in plain, f"{builder}: the plain entry must not claim the other geometry"
        assert full["ink"] == plain["ink"] == LPG.page_ink_key(MPB.representative(builder)), builder
        assert full["boxes"]["plot"]["w"] > plain["boxes"]["plot"]["w"], (
            f"{builder}: the full-stage plot is not wider than the column's - one of the two was not measured")
        # P69 T6d + fixes4: a full-stage entry may also carry `tag_boxes` - the LINE end tags' drawn rects, read only
        # by the stamp's fit and only when the entry's `tag_ink` fingerprint matches; never a box of its own
        extra = set(full["boxes"]) - set(LPG.BOX_KEYS)
        assert extra <= {"tag_boxes"}, (builder, extra)
        assert set(full["boxes"]) - extra == set(LPG.BOX_KEYS), builder
        if extra:
            assert full.get("tag_ink"), f"{builder}: tag_boxes without the tag_ink fingerprint that guards them"
        assert len(full["data_mask"]) == 16 and "1" in "".join(full["data_mask"]), builder
        assert sorted(full["axis"]) == ["x", "y"], builder
        assert {k: bool(v) for k, v in full["axis"].items()} == {k: bool(v) for k, v in plain["axis"].items()}, (
            f"{builder}: a geometry cannot add or remove a label bank - the donut and the census have neither")


def test_the_full_stage_entry_is_served_to_a_full_stage_page(tmp_path):
    spec = _stamped()
    boxes = LPG.page_boxes(spec, "16:9")
    assert boxes["measured"] is True, "R26-235: the refusal is gone"
    for key in LPG.BOX_KEYS:
        assert boxes[key] == FIXTURE["builders"]["dense-line"][FULL]["boxes"][key], key
    assert boxes["data_mask"] == FIXTURE["builders"]["dense-line"][FULL]["data_mask"]
    assert boxes["axis"] == FIXTURE["builders"]["dense-line"][FULL]["axis"]
    est = _estimate(spec, "16:9", tmp_path)
    assert est["measured"] is False and "data_mask" not in est
    assert (est["plot"]["y"], est["plot"]["h"]) == (198, 680), "the estimate, for the record"
    assert (boxes["plot"]["y"], boxes["plot"]["h"]) == (208, 666), "the player's own plot"
    assert est["title"]["w"] - boxes["title"]["w"] == 321, (
        "the estimate gives the title the ink COLUMN's width; the frame draws the type")


def test_the_two_geometries_are_never_confused(tmp_path):
    """The plain entry may not answer for a full-stage page and the full-stage entry may not answer for
    a plain one - a fixture that has to be reinterpreted is not a measurement."""
    dense = FIXTURE["builders"]["dense-line"]
    only_plain = _fixture_file(tmp_path / "a", {"dense-line": {"16:9": dense["16:9"]}})
    assert _served(_stamped(), "16:9", only_plain)["measured"] is False, "the column's boxes were served"
    only_full = _fixture_file(tmp_path / "b", {"dense-line": {FULL: dense[FULL]}})
    assert _served(_golden_page(), "16:9", only_full)["measured"] is False, "the stage's boxes were served"
    # ... and the flag on the entry is checked against the key it is filed under
    lying = _fixture_file(tmp_path / "c", {"dense-line": {FULL: dict(dense["16:9"])}})
    assert _served(_stamped(), "16:9", lying)["measured"] is False, "an unflagged entry answered for the stage"
    lying2 = _fixture_file(tmp_path / "d", {"dense-line": {"16:9": dict(dense[FULL])}})
    assert _served(_golden_page(), "16:9", lying2)["measured"] is False, "a flagged entry answered for the column"


def test_every_page_that_carries_no_stamp_is_untouched():
    """Byte-identity, the half this row must not move: the plain 16:9 page and every 9:16 page are
    served exactly the entries they were served before the key gained the flag."""
    page = _golden_page()
    plain = LPG.page_boxes(page, "16:9")
    assert plain["measured"] is True
    for key in LPG.BOX_KEYS:
        assert plain[key] == FIXTURE["builders"]["dense-line"]["16:9"]["boxes"][key], key
    assert LPG.page_boxes(page, "9:16") == LPG.page_boxes(_stamped(page), "9:16")
    assert LPG.measured_entry(page, "9:16") == LPG.measured_entry(_stamped(page), "9:16")
    for builder in MPB.BUILDERS:
        rep = MPB.representative(builder)
        for aspect in MPB.ASPECTS:
            got = LPG.page_boxes(rep, aspect)
            assert got["measured"] is True, (builder, aspect)
            assert all(got[k] == FIXTURE["builders"][builder][aspect]["boxes"][k] for k in LPG.BOX_KEYS), (builder, aspect)


# ---- E65: the card gets a real room ------------------------------------------------------------

def test_a_card_on_a_full_stage_page_lands_in_a_real_room(tmp_path):
    """The row's own symptom. On the ESTIMATE the placer has no `data_mask`, so `mask_rooms` and
    `axis_room` return nothing and it falls to `corner` - the emptiest quadrant at the legibility
    floor. On the measurement it takes the plot's own empty room, which is what E65 promised."""
    spec = _stamped()
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = tmp_path / "no-such-fixture.json"
    try:
        was = B.page_place(copy.deepcopy(spec), "16:9")
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved
    now = B.page_place(copy.deepcopy(spec), "16:9")
    assert was["room"] == "corner", ("the estimate's answer, for the record", was)
    assert (was["w"], was["h"]) == (100, 80), ("... at the legibility floor", was)
    assert now["room"] in ("empty", "axis"), ("R26-235: a real room, not a corner", now)
    assert now["h"] > B.PLACE_FLOOR_H["16:9"], now
    assert now["w"] * now["h"] > 3 * was["w"] * was["h"], (was, now)
    boxes = LPG.page_boxes(spec, "16:9")
    plot = boxes["plot"]
    assert plot["x"] <= now["x"] and now["x"] + now["w"] <= plot["x"] + plot["w"], (now, plot)
    assert plot["y"] <= now["y"] and now["y"] + now["h"] <= plot["y"] + plot["h"], (now, plot)
    assert B.mask_is_clear(boxes, now), ("a card in the plot's room touches no data ink", now)


def test_the_rooms_e65_reads_exist_only_because_the_page_is_measured(tmp_path):
    spec = _stamped()
    assert B.mask_rooms(_estimate(spec, "16:9", tmp_path)) == [], "an unmeasured page has no room to read"
    assert B.axis_room(_estimate(spec, "16:9", tmp_path)) is None
    boxes = LPG.page_boxes(spec, "16:9")
    assert B.mask_rooms(boxes), "the measured page's empty rectangles"
    assert B.axis_room(boxes) is not None, "and the band under the data"
    assert B.page_is_measured({"kind": B.SPECIES_LEDGER, "page": spec}, "16:9") is True


# ---- R26-220: the reachable zoom, re-checked on the measured boxes ------------------------------

def _look(boxes: dict) -> tuple[float, float]:
    """The compiler's own proxy for a DATUM target: the plot's centre (`gate_motion_density._cam_point`)."""
    plot = boxes["plot"]
    return plot["x"] + plot["w"] / 2, plot["y"] + plot["h"] / 2


def test_the_reachable_zoom_is_the_same_1_08_on_the_measurement(tmp_path):
    """R26-235 expected the ceiling to move. It does not, and the number is the finding: the estimate
    and the frame put this page's TITLE at y 44 alike, so the title's top edge - the glyph that binds -
    binds at 1.0885 measured against 1.0891 estimated. Both floor to the 1.08 R26-220 published."""
    spec = _stamped()
    measured, est = LPG.page_boxes(spec, "16:9"), _estimate(spec, "16:9", tmp_path)
    assert measured["title"]["y"] == est["title"]["y"] == 44, (measured["title"], est["title"])
    z_now, el_now, edge_now, _t = B.page_zoom_ceiling(spec, "16:9", _look(measured))
    saved = LPG.PAGE_BOXES_FIXTURE
    LPG.PAGE_BOXES_FIXTURE = tmp_path / "no-such-fixture.json"
    try:
        z_was, el_was, edge_was, _t2 = B.page_zoom_ceiling(spec, "16:9", _look(est))
    finally:
        LPG.PAGE_BOXES_FIXTURE = saved
    assert (el_was, edge_was) == ("title", "top") and (el_now, edge_now) == ("title", "top")
    assert round(z_was, 4) == 1.0891 and round(z_now, 4) == 1.0885, (z_was, z_now)
    assert math.floor(z_now * 100) / 100 == math.floor(z_was * 100) / 100 == 1.08
    # and the SECOND ceiling is still silent on a full-stage page: its ink already runs past the strip's
    # foot, so the page's own crop line can never walk into the anchored caption (R26-220's 16:9 half)
    assert B.page_crop_line_ceiling(spec, "16:9", _look(measured)) == (math.inf, "-")


# ---- THE FRAMES --------------------------------------------------------------------------------

def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            br = pw.chromium.launch(headless=True)
            br.close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _kenned_frame() -> tuple[dict, list[str]]:
    """The golden surface's own page, STAMPED full stage, on the served player at `PROBE_T` - so it
    carries the page's Ken Burns exactly as a built cut does. Read with the probe the fixture is
    measured with (`measure_page_boxes.READ_BOXES`), so these are the player's own boxes."""
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    tl = json.loads(json.dumps(tl))
    tl["scenes"][0]["world"]["page"].update(full_stage=True, caption="anchor")
    td = tempfile.TemporaryDirectory()
    try:
        html = Path(td.name) / "page.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        pw = sync_playwright().start()
        br = pw.chromium.launch(headless=True)
        page = br.new_context(viewport={"width": STAGE_W, "height": STAGE_H}).new_page()
        errs: list[str] = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(page, STAGE_W, STAGE_H)
        page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                      "s.dispatchEvent(new Event('input', {bubbles:true})); }", PROBE_T)
        boxes = page.evaluate(MPB.READ_BOXES)
        br.close(); pw.stop(); srv.shutdown()
        return boxes, errs
    finally:
        td.cleanup()


@pytest.fixture(scope="module")
def frames():
    """Two renders of the same full-stage page: the fixture's own (no ken, `measure_page_boxes`'
    one-scene timeline) and the built one (the golden's own ken on)."""
    return {"fresh": MPB.measure("dense-line", "16:9", _stamped()), "kenned": _kenned_frame()}


@needs_browser
def test_ON_THE_FRAME_the_measured_boxes_are_the_frames_to_within_2px(frames):
    """The brief's bar, and the fixture's own contract: what `page_boxes` hands a placer for a
    full-stage page is what the player draws. The estimate is not - its plot is 14 px too tall."""
    fresh = frames["fresh"]
    entry = FIXTURE["builders"]["dense-line"][FULL]
    for key in LPG.BOX_KEYS:
        got, want = fresh["boxes"][key], entry["boxes"][key]
        assert all(abs(got[k] - want[k]) <= TOL for k in ("x", "y", "w", "h")), (key, want, got)
    for bank in ("x", "y"):
        got, want = fresh["axis"][bank], entry["axis"][bank]
        assert got and want and all(abs(got[k] - want[k]) <= TOL for k in ("x", "y", "w", "h")), (bank, want, got)
    assert fresh["data_mask"] == entry["data_mask"], "the plot's own ink moved under the fixture"


@needs_browser
def test_ON_THE_FRAME_the_estimate_is_the_one_that_disagrees(frames, tmp_path):
    """The other half of the same frame: the numbers the compiler had before this row are out by more
    than the bar on the plot the card and the camera are placed against."""
    fresh, est = frames["fresh"], _estimate(_stamped(), "16:9", tmp_path)
    plot = fresh["boxes"]["plot"]
    assert abs(est["plot"]["h"] - plot["h"]) >= 10, (est["plot"], plot)
    assert max(abs(est[k]["w"] - fresh["boxes"][k]["w"]) for k in ("title", "source")) > 300, (
        "the estimate gives the title and the source the ink column's width")
    assert abs(est["title"]["y"] - fresh["boxes"]["title"]["y"]) <= TOL, (
        "the title's TOP is the one thing the estimate had right - which is why R26-220's ceiling does not move")


@needs_browser
def test_ON_THE_FRAME_a_card_in_the_measured_room_is_clear_of_the_data(frames):
    """E65 on a re-render: the room the placer takes is empty in the frame's own ink, at the cell the
    mask is read on, and the card in it is above the legibility floor."""
    fresh = frames["fresh"]
    spec = _stamped()
    card = B.page_place(copy.deepcopy(spec), "16:9")
    boxes = dict(LPG.page_boxes(spec, "16:9"), plot=fresh["boxes"]["plot"], data_mask=fresh["data_mask"])
    assert card["room"] in ("empty", "axis"), card
    assert B.mask_is_clear(boxes, card), (card, fresh["data_mask"])
    assert card["h"] >= B.PLACE_FLOOR_H["16:9"], card


@needs_browser
def test_ON_THE_FRAME_the_built_pages_own_ken_is_ONE_scale_and_not_a_box_error(frames):
    """R26-220 measured its 1.3 px off a BUILT frame, and read it as the estimate's error. It is not:
    the page's Ken Burns (`ken_burns.scale` 0.04, no pan) is a similarity about the stage's centre
    which `page_boxes` does not model at either aspect, and which the fixture zeroes to measure the
    layout. ONE scale carries the fixture's boxes onto the built frame, within the same 2 px."""
    kenned, errs = frames["kenned"]
    assert not errs, errs
    entry = FIXTURE["builders"]["dense-line"][FULL]["boxes"]
    scale = kenned["plot"]["w"] / entry["plot"]["w"]
    assert 1.0 < scale < 1.04, ("a ken push of scale 0.04, part way through its scene", scale)
    cx, cy = STAGE_W / 2, STAGE_H / 2
    for key in ("title", "sub", "chart", "plot"):
        want = {"x": cx + (entry[key]["x"] - cx) * scale, "y": cy + (entry[key]["y"] - cy) * scale,
                "w": entry[key]["w"] * scale, "h": entry[key]["h"] * scale}
        got = kenned[key]
        assert all(abs(got[k] - want[k]) <= TOL for k in ("x", "y", "w", "h")), (key, want, got, scale)
    # ... and the residual at the title's TOP - the glyph R26-220's ceiling binds on - is the ken alone,
    # `(cy - y) * (scale - 1)`, which is 10.0 px at this instant of this golden's push and 0 at its start.
    # R26-220 read 4.8 px of it (the estimate's 44 against its frame's 39.2) and filed it as the box
    # model's error; the scale that lifts this title 4.8 px is 1.0097, inside this page's own ken range.
    lift = entry["title"]["y"] - (cy + (entry["title"]["y"] - cy) * scale)
    assert lift == pytest.approx((cy - entry["title"]["y"]) * (scale - 1), abs=0.01), (lift, scale)
    assert TOL < lift < (cy - entry["title"]["y"]) * 0.04 + 0.01, ("the whole push is the ceiling", lift)
    r26_220 = 44 - 39.2
    assert 1.0 < 1 + r26_220 / (cy - entry["title"]["y"]) < 1.04, "R26-220's 4.8 px is this same ken, earlier"
