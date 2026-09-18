"""R26-205 / E99 s82 - THE LEDGER PAGE IS THE PLATE AT 16:9.

The operator, on a bare frame of the Steel and Paper H unit's copy d (2026-09-18): *"why is the ledger
being used at like 20% size? the whole point of a ledger plate is that the chart IS the world, you
have it restricted to this square even when bare, it should be the whole plate."*

TWO reservations made that square and this row closes both:
  (a) THE CAPTION'S COLUMN. A landscape page's chart box is `(0.6 if quiet_zone else 0.9) * cb.w`,
      because the STAGE caption sits in the page's declared quiet zone. At 16:9 a page row's caption
      now goes to the ANCHORED strip (`ledger_page.CAPTION_ANCHOR["16:9"]`) - the strip E62 named and
      that only a live dock had ever demoted a caption to - so the chart takes the stage instead.
  (b) THE CARD'S COLUMN. E65's placer gives a card the plot's own room; nothing had to be kept empty.

WHAT THE BOX IS. `ledger_page.LAND_FULL`, in RENDERED stage fractions (the punch is in them), carrying
the chart's own 1000:560 viewBox aspect so there is no letterbox and the compiler's estimate is exact.
Its three feet were each MEASURED on the served player, and they are what cap it:
  1. the species' inline END TAGS stay on the stage (the first pass ran them 305 px off the right),
  2. the x tick labels clear the anchored caption's strip,
  3. the source line clears the strip's foot, where the landscape source line already sits.

BYTE-IDENTITY. `full_stage` is stamped by the COMPILER, so every committed golden timeline - and every
9:16 build - carries no such key and lays out exactly as it did. The ink key gains the flag only when
the page carries it, so the measured fixture's entries all still apply to the pages they were measured
for.
"""
from __future__ import annotations

import json
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
SURFACE = "ledger-page-mid-build"     # the dense-line golden: four series, the longest end tags in the repo
PROBE_T = 20.0                        # past the page's whole build (roll 0.7 + savor 0.8 + field + punch + build = 7.4 s)
PLOT_FLOOR = 0.48                     # the row's floor for "the chart is the world", read against the 0.408 it replaced

LONG = [{"label": "+613%", "name": "MEMORY MAKERS (hynix+Micron)"}, {"label": "+105%", "name": "SEMICONDUCTOR STOCKS"}]
SHORT = [{"label": "-9.9%", "name": "Japan"}, {"label": "+2%", "name": "Korea"}]


def _page(series=SHORT, **kw) -> dict:
    page = {"builder": "dense-line", "title": "Where the four lines end", "sub": "the sub",
            "source": "Yahoo Finance", "quiet_zone": "right", "axes": {"ylabel": "index"}, "series": series}
    page.update(kw)
    return page


def _meets(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"]
            and a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"])


# ---- the stamp: who is a full-stage page and who is not ---------------------------------------

def test_the_compiler_stamps_a_16x9_page_row_as_the_plate(monkeypatch):
    monkeypatch.setattr(B, "ASPECT", None)          # a landscape build declares no aspect
    assert B.stamp_full_stage({}) == {"full_stage": True, "caption": "anchor"}
    monkeypatch.setattr(B, "ASPECT", "16:9")
    assert B.stamp_full_stage({}) == {"full_stage": True, "caption": "anchor"}


def test_a_short_is_untouched_because_a_portrait_page_already_fills_the_frame(monkeypatch):
    monkeypatch.setattr(B, "ASPECT", "9:16")
    assert B.stamp_full_stage({}) == {}
    assert B.stamp_full_stage(_page()) == _page()    # not one key added


def test_a_host_plate_keeps_its_own_board(monkeypatch):
    """`proofs/ledger/build_ledger_proof.py` measures a host's board around the hand and pins the
    caption to the anchor itself - its chart box is the host's, never the stage's."""
    monkeypatch.setattr(B, "ASPECT", "16:9")
    for host in ({"board": {"x": 0.1, "y": 0.1, "w": 0.5, "h": 0.5}},
                 {"chart_box": {"x": 0.1, "y": 0.1, "w": 0.5, "h": 0.5}},
                 {"punch": False, "caption": "anchor"}):
        assert "full_stage" not in B.stamp_full_stage(dict(host))


def test_a_page_that_declared_its_own_caption_keeps_it(monkeypatch):
    monkeypatch.setattr(B, "ASPECT", "16:9")
    assert B.stamp_full_stage({"caption": "stage"})["caption"] == "stage"


def test_full_stage_is_a_16x9_word_and_never_a_host_plates():
    assert LPG.full_stage({"full_stage": True}, "16:9") is True
    assert LPG.full_stage({"full_stage": True}, "9:16") is False
    assert LPG.full_stage({}, "16:9") is False
    assert LPG.full_stage({"full_stage": True, "chart_box": {"x": 0, "y": 0, "w": 1, "h": 1}}, "16:9") is False
    assert LPG.full_stage({"full_stage": True, "punch": False}, "16:9") is False


def test_the_two_readers_of_the_stamp_agree():
    world = {"kind": "ledger", "page": {"full_stage": True}}
    assert B.page_is_full_stage(world, "16:9") is True
    assert B.page_is_full_stage(world, "9:16") is False
    assert B.page_is_full_stage({"asset_id": "plate-plain"}, "16:9") is False
    assert B.page_is_full_stage(None, "16:9") is False


# ---- the box, and the three feet that cap it ---------------------------------------------------

def test_the_box_carries_the_viewboxs_own_aspect_so_nothing_is_letterboxed():
    """A box that is not 1000:560 wastes its spare side to the SVG's `meet` - which is what made the
    plot 21 % in the first place. Within half a pixel over the box's own width."""
    ch = LPG.page_boxes(_page(full_stage=True), "16:9")["chart"]
    vw, vh = LPG.LAND_VIEWBOX
    assert abs(ch["w"] / ch["h"] - vw / vh) * ch["h"] < 0.5, ch


def test_the_x_tick_labels_clear_the_anchored_caption():
    boxes = LPG.page_boxes(_page(full_stage=True), "16:9")
    ch, cap = boxes["chart"], boxes["caption_anchor"]
    assert ch["y"] + LPG.LAND_TICK_B * ch["h"] <= cap["y"], (ch, cap)


def test_the_source_line_clears_the_strips_foot():
    boxes = LPG.page_boxes(_page(full_stage=True), "16:9")
    src, cap = boxes["source"], boxes["caption_anchor"]
    assert src["y"] >= cap["y"] + cap["h"] - 1, (src, cap)


def test_the_widest_end_tag_the_species_writes_still_lands_on_the_stage():
    """The worst case is the BOX's own cap: `X + LAND_TAG_REACH * W` is the frame, less a hair."""
    F = LPG.LAND_FULL
    assert F["X"] + LPG.LAND_TAG_REACH * F["W"] <= 0.979, F


def test_the_plot_is_the_world_not_a_square():
    bare, full = LPG.page_boxes(_page(), "16:9"), LPG.page_boxes(_page(full_stage=True), "16:9")
    assert full["plot"]["w"] / STAGE_W >= PLOT_FLOOR, full["plot"]
    assert full["plot"]["w"] > bare["plot"]["w"] * 1.4, (bare["plot"], full["plot"])


def test_the_pages_own_ink_still_stands_above_and_below_the_chart():
    b = LPG.page_boxes(_page(full_stage=True), "16:9")
    assert b["sub"]["y"] + b["sub"]["h"] <= b["plot"]["y"], (b["sub"], b["plot"])
    assert b["source"]["y"] >= b["plot"]["y"] + b["plot"]["h"], (b["source"], b["plot"])
    for k in ("title", "sub", "source"):
        assert b[k]["x"] >= 0 and b[k]["y"] >= 0 and b[k]["y"] + b[k]["h"] <= STAGE_H, (k, b[k])


def test_the_boxes_are_pure_and_the_spec_is_never_mutated():
    spec = _page(full_stage=True)
    before = json.dumps(spec, sort_keys=True)
    first = LPG.page_boxes(spec, "16:9")
    assert json.dumps(spec, sort_keys=True) == before
    assert LPG.page_boxes(spec, "16:9") == first


# ---- the end tag column ------------------------------------------------------------------------

def test_the_tag_column_is_this_pages_own_names():
    assert LPG.tag_units(_page(series=SHORT)) == len("-9.9% Japan") * LPG.LAND_TAG_NAME_U
    assert LPG.tag_units(_page(series=LONG)) == len("+613% MEMORY MAKERS (hynix+Micron)") * LPG.LAND_TAG_NAME_U


def test_an_inline_badge_rides_the_name_it_keys_and_widens_that_column():
    """The badge that keys a line is written INSIDE the same element (E22: one reveal, one real
    estate), so the column is the name plus that badge's tag - and the badge is matched to the series
    by the player's own accent table, never to the longest name on the page."""
    bare = _page(series=[dict(s, color=c) for s, c in zip(SHORT, ("crimson", "teal"))])
    keyed = dict(bare, badges=[{"accent": "coral", "inline": True, "tag": "the one that moved"}])
    assert LPG.tag_units(keyed) > LPG.tag_units(bare)
    other = dict(bare, badges=[{"accent": "sunflower", "inline": True, "tag": "the one that moved"}])
    assert LPG.tag_units(other) == LPG.tag_units(bare), "no series carries the amber it keys"
    assert LPG.tag_units(dict(bare, badges=[{"accent": "coral", "tag": "x" * 40}])) == LPG.tag_units(bare), \
        "a RAIL badge is under the chart, not on a line"


def test_a_builder_that_writes_no_inline_name_has_no_tag_column():
    assert LPG.tag_units(_page(series=LONG, builder="story")) == 0
    assert LPG.tag_units(_page(series=LONG, builder="treemap")) == 0
    assert LPG.tag_units(_page(series=[dict(s, muted=True) for s in LONG])) == 0   # history carries no name


def test_the_tag_column_stands_beside_the_plot_and_grows_with_the_name():
    short = LPG.page_boxes(_page(series=SHORT, full_stage=True), "16:9")
    long_ = LPG.page_boxes(_page(series=LONG, full_stage=True), "16:9")
    assert short["tags"]["x"] >= short["plot"]["x"] + short["plot"]["w"] - 1
    assert long_["tags"]["w"] > short["tags"]["w"] * 2
    assert short["tags"]["x"] == long_["tags"]["x"], "the column starts at the line's end either way"


def test_only_a_full_stage_page_reports_a_tag_column():
    assert LPG.TAGS_KEY not in LPG.page_boxes(_page(series=LONG), "16:9")
    assert LPG.TAGS_KEY not in LPG.page_boxes(_page(series=LONG), "9:16")


# ---- the card: no reserved column, and never on the tags ----------------------------------------

def test_the_right_band_starts_after_the_pages_own_end_tags():
    boxes = LPG.page_boxes(_page(series=SHORT, full_stage=True), "16:9")
    band = next(b for b in B.free_bands(boxes) if b["band"] == "right")
    assert band["x"] >= boxes["tags"]["x"] + boxes["tags"]["w"] - 1, (band, boxes["tags"])


def test_a_page_with_no_tag_column_cuts_its_bands_exactly_where_it_always_did():
    """Every page compiled before this row, and every 9:16 page: `free_bands` is byte-identical."""
    boxes = LPG.page_boxes(_page(), "16:9")
    band = next(b for b in B.free_bands(boxes) if b["band"] == "right")
    assert band["x"] == boxes["plot"]["x"] + boxes["plot"]["w"]


def test_a_card_on_a_full_stage_page_is_placed_clear_of_the_plot_and_of_the_tags():
    spec = _page(series=SHORT, full_stage=True)
    boxes = LPG.page_boxes(spec, "16:9")
    place = B.dock_place({"kind": "ledger", "page": spec}, "16:9")
    assert place and place["room"] == "outside", place
    assert not _meets(place, boxes["plot"]), (place, boxes["plot"])
    assert not _meets(place, boxes["tags"]), (place, boxes["tags"])
    assert place["x"] + place["w"] <= boxes["safe"]["x"] + boxes["safe"]["w"]


def test_a_page_whose_names_take_the_whole_band_is_told_so_rather_than_covered():
    """E65 (4): the placer never answers nothing - it takes the emptiest corner at the legibility
    floor and the build WARNs. On a full-stage page with tags this long that is the honest answer,
    and it is what the author has to see."""
    spec = _page(series=LONG, full_stage=True)
    place = B.dock_place({"kind": "ledger", "page": spec}, "16:9")
    assert place and place["room"] == "corner", place


# ---- the caption: anchored on a page row, STAGE everywhere it always was -------------------------

def _scenes(kind: str) -> list[dict]:
    world = ({"kind": "ledger", "page": _page(full_stage=True)} if kind == "page"
             else {"kind": "ledger", "page": _page()} if kind == "page-9x16" else {"asset_id": "plate-plain"})
    return [{"scene_id": "s1", "span": [0.0, 20.0], "world": world, "docks": []}]


def test_a_16x9_page_rows_caption_pages_are_stamped_anchor():
    assert B._full_stage_page_at(_scenes("page"), 5.0, "16:9") is True
    assert B._full_stage_page_at(_scenes("page"), 25.0, "16:9") is False    # past the scene


def test_a_plate_rows_caption_keeps_the_stage_at_either_aspect():
    assert B._full_stage_page_at(_scenes("plate"), 5.0, "16:9") is False
    assert B._full_stage_page_at(_scenes("plate"), 5.0, "9:16") is False


def test_a_9x16_pages_caption_is_exactly_what_it_was():
    assert B._full_stage_page_at(_scenes("page-9x16"), 5.0, "9:16") is False


def test_a_dock_on_a_full_stage_page_takes_no_band_because_its_caption_never_held_the_stage():
    scene = {"scene_id": "s1", "span": [0.0, 20.0], "world": {"kind": "ledger", "page": _page(full_stage=True)},
             "docks": [{"slide": "a", "enter": 1.0, "exit": 5.0, "place": {"x": 1300, "y": 300, "w": 400, "h": 300}}]}
    B.stamp_caption_bands([scene], [{"s": 0.5, "e": 4.0, "t": []}], "16:9")
    assert scene["docks"][0]["caption_band"] is None


def test_a_dock_on_a_9x16_page_still_takes_E62s_band():
    scene = {"scene_id": "s1", "span": [0.0, 20.0], "world": {"kind": "ledger", "page": _page()},
             "docks": [{"slide": "a", "enter": 1.0, "exit": 5.0, "place": {"x": 80, "y": 1000, "w": 300, "h": 200}}]}
    B.stamp_caption_bands([scene], [{"s": 0.5, "e": 4.0, "t": []}], "9:16")
    assert scene["docks"][0]["caption_band"] is not None


# ---- byte-identity: the fixture, the ink key, and every page that carries no stamp ----------------

def test_the_stamp_is_not_INK_and_never_touches_the_fixtures_key():
    """The fixture is keyed by ink, and `full_stage` is not ink - it is a geometry the same ink takes
    at ONE aspect, which the key does not know. It was in the key for one round and re-keyed every
    9:16 page any caller had stamped with the compiler's `ASPECT` unset: the Tokyo cut's measured
    pages fell back to the estimate and E65's placer lost the plot's own room
    (`test_dock_over_build.py::test_the_tokyo_panel_card_is_placed_in_the_plots_empty_room`). The
    refusal lives in `measured_entry`, where the aspect is in hand."""
    spec = _page()
    assert LPG.page_ink_key(spec) == LPG.page_ink_key(dict(spec, full_stage=True))
    stamped = dict(spec, full_stage=True)
    assert LPG.measured_entry(stamped, "9:16") == LPG.measured_entry(spec, "9:16")
    assert LPG.page_boxes(stamped, "9:16")["measured"] == LPG.page_boxes(spec, "9:16")["measured"]


def test_the_measured_fixture_still_answers_for_the_page_it_measured():
    """The dense-line representative in `assets/page-boxes.v1.json` IS this golden's own page. It is
    still measured with the stamp absent, at both aspects; WITH the stamp it is a different layout and
    the fixture is correctly silent rather than handing over the old box's numbers."""
    spec = json.loads((RB.SOURCES / f"{SURFACE}.timeline.json").read_text(encoding="utf-8"))["scenes"][0]["world"]["page"]
    for aspect in ("16:9", "9:16"):
        assert LPG.measured_boxes(spec, aspect) is not None, aspect
    assert LPG.measured_boxes(dict(spec, full_stage=True), "16:9") is None
    assert LPG.page_boxes(spec, "16:9")["measured"] is True


def test_a_9x16_page_lays_out_exactly_as_it_did():
    """The portrait law is not touched by this row: same boxes with the flag on or off."""
    spec = _page()
    assert LPG.page_boxes(spec, "9:16") == LPG.page_boxes(dict(spec, full_stage=True), "9:16")


# ---- THE FRAMES -----------------------------------------------------------------------------------

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

CAP_PROBE = """() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const c = document.getElementById('caption');
  const r = c.getBoundingClientRect(), cs = getComputedStyle(c);
  return {x: r.x - stg.x, y: r.y - stg.y, w: r.width, h: r.height, cls: c.className,
          fs: cs.fontSize, stage: c.classList.contains('stage'), quiet: c.classList.contains('quiet')};
}"""

TAG_PROBE = """() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  return [...document.querySelectorAll('.lp-chart text.sname')].map((el) => {
    const r = el.getBoundingClientRect();
    return {x: r.x - stg.x, r: r.x - stg.x + r.width, w: r.width};
  });
}"""


def _frame(stamp: bool) -> tuple[dict, dict, list, list]:
    """The dense-line golden's own page on the SERVED player, with and without the stamp, read with
    the probe `measure_page_boxes` measures the fixture with - so these are the player's own boxes."""
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    tl = json.loads(json.dumps(tl))
    if stamp:
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
        boxes, cap, tags = page.evaluate(MPB.READ_BOXES), page.evaluate(CAP_PROBE), page.evaluate(TAG_PROBE)
        br.close(); pw.stop(); srv.shutdown()
        return boxes, cap, tags, errs
    finally:
        td.cleanup()


@pytest.fixture(scope="module")
def frames():
    return {"before": _frame(False), "after": _frame(True)}


@needs_browser
def test_ON_THE_FRAME_the_chart_is_the_world(frames):
    """The row's own measurement: the bare page's plot against the square it replaced."""
    (b_boxes, _bc, _bt, b_errs), (a_boxes, _ac, _at, a_errs) = frames["before"], frames["after"]
    assert not b_errs and not a_errs, (b_errs, a_errs)
    before, after = b_boxes["plot"]["w"], a_boxes["plot"]["w"]
    assert before / STAGE_W < 0.42, ("the square the ruling is about", before)
    assert after / STAGE_W >= PLOT_FLOOR, ("the plot is not the world yet", after, after / STAGE_W)
    assert after > before * 1.2


@needs_browser
def test_ON_THE_FRAME_the_pages_own_ink_is_all_still_on_the_stage(frames):
    boxes = frames["after"][0]
    for k in ("title", "sub", "source", "plot", "chart"):
        bx = boxes[k]
        assert bx["x"] >= 0 and bx["y"] >= 0, (k, bx)
        assert bx["x"] + bx["w"] <= STAGE_W + 1 and bx["y"] + bx["h"] <= STAGE_H + 1, (k, bx)
    assert not _meets(boxes["title"], boxes["plot"]), (boxes["title"], boxes["plot"])
    assert not _meets(boxes["sub"], boxes["plot"]), (boxes["sub"], boxes["plot"])
    assert not _meets(boxes["source"], boxes["plot"]), (boxes["source"], boxes["plot"])


@needs_browser
def test_ON_THE_FRAME_the_end_tags_never_leave_the_frame(frames):
    """The first pass put the box on the whole stage and ran these 305 px off the right."""
    for tag in frames["after"][2]:
        assert tag["r"] <= STAGE_W, tag
    assert frames["after"][2], "the dense-line page writes its inline names"


@needs_browser
def test_ON_THE_FRAME_the_caption_is_in_the_anchored_strip_and_clear_of_the_page(frames):
    (_bb, before, _bt, _be), (after_boxes, after, _at, _ae) = frames["before"], frames["after"]
    assert before["stage"] and not before["quiet"], ("today's page keeps the stage caption", before)
    assert before["x"] > STAGE_W * 0.55, ("... in the column the chart was cut for", before)
    anchor = LPG.CAPTION_ANCHOR["16:9"]
    assert after["quiet"] and not after["stage"], after
    assert after["x"] >= anchor[0] - 1 and after["y"] >= anchor[1] - 1, (after, anchor)
    assert after["x"] + after["w"] <= anchor[0] + anchor[2] + 1, (after, anchor)
    assert after["y"] + after["h"] <= anchor[1] + anchor[3] + 1, (after, anchor)
    for k in ("plot", "source", "title", "sub"):
        assert not _meets(after_boxes[k], {"x": after["x"], "y": after["y"], "w": after["w"], "h": after["h"]}), \
            (k, after_boxes[k], after)


DOCK_PROBE = """() => {
  const el = document.getElementById('dock-1');
  const stg = document.getElementById('stage').getBoundingClientRect();
  if (!el || !(parseFloat(el.style.opacity || '0') > 0.01)) return null;
  const r = el.getBoundingClientRect();
  return {x: r.x - stg.x, y: r.y - stg.y, w: r.width, h: r.height};
}"""


@needs_browser
def test_ON_THE_FRAME_a_card_on_a_full_stage_page_covers_neither_the_chart_nor_a_name():
    """E65's placer with NO column kept for it. The page is the dense-line golden's, re-named so its
    end tags are a short page's rather than the longest in the repo (a page whose names take the whole
    band is told so instead - `test_a_page_whose_names_take_the_whole_band_is_told_so_rather_than_covered`);
    the card is the dock goldens' own asset, placed by `dock_place` exactly as the row loop places it."""
    from playwright.sync_api import sync_playwright
    tl, uris, _t, _a = RB.load_surface(SURFACE)
    dtl, duris, _dt, _da = RB.load_surface("dock-pair-16x9")
    tl, uris = json.loads(json.dumps(tl)), dict(duris, **uris)
    scene = tl["scenes"][0]
    page = scene["world"]["page"]
    for i, ser in enumerate(page.get("series") or []):
        ser["name"], ser["label"] = ("Memory", "Semis", "Market", "Mega")[i % 4], ser.get("label")
    page["badges"] = [dict(b, inline=False) for b in page.get("badges") or []]   # no badge rides a name here
    page.update(full_stage=True, caption="anchor")
    place = B.dock_place(scene["world"], "16:9")
    assert place and place["room"] == "outside", place
    aid = next(k for k in duris if k.startswith("ev-golden-card"))
    scene["docks"] = [B.dock_entry(aid, 0, 2.0, 30.0, 2, B.DOCK_KIND_IMAGE, place, None, None, False)]
    tl["scenes"] = [scene]
    td = tempfile.TemporaryDirectory()
    try:
        html = Path(td.name) / "card.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        pw = sync_playwright().start()
        br = pw.chromium.launch(headless=True)
        pg = br.new_context(viewport={"width": STAGE_W, "height": STAGE_H}).new_page()
        errs: list[str] = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://127.0.0.1:%d/%s" % (port, html.name), wait_until="networkidle", timeout=120000)
        RB.prepare_page(pg, STAGE_W, STAGE_H)
        pg.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; "
                    "s.dispatchEvent(new Event('input', {bubbles:true})); }", PROBE_T)
        card, boxes, tags = pg.evaluate(DOCK_PROBE), pg.evaluate(MPB.READ_BOXES), pg.evaluate(TAG_PROBE)
        br.close(); pw.stop(); srv.shutdown()
    finally:
        td.cleanup()
    assert not errs, errs
    assert card, "the card is up"
    assert not _meets(card, boxes["plot"]), ("0 px over the chart", card, boxes["plot"])
    for tag in tags:
        assert card["x"] >= tag["r"] - 1, ("0 px over an end tag", card, tag)
    assert card["x"] + card["w"] <= STAGE_W and card["y"] + card["h"] <= STAGE_H, card
    assert card["y"] + card["h"] <= LPG.CAPTION_ANCHOR["16:9"][1], ("never in the caption's strip", card)


@needs_browser
def test_ON_THE_FRAME_the_python_law_and_the_player_agree(frames):
    """`ledger_page._landscape_full_boxes` is the mirror of the engine's own geometry block. The page
    carries a Ken Burns zoom the estimate has never modelled (as the fixture's own numbers do), so the
    two agree up to ONE scale about the stage's centre - not up to a fudge."""
    boxes = frames["after"][0]
    est = LPG.page_boxes(dict(_page(), title="x", full_stage=True), "16:9")
    k = boxes["plot"]["w"] / est["plot"]["w"]
    assert 1.0 <= k <= 1.04, ("the only difference is the Ken Burns zoom", k)
    for key in ("chart", "plot"):
        cx = boxes[key]["x"] + boxes[key]["w"] / 2
        assert abs(cx - (STAGE_W / 2 + (est[key]["x"] + est[key]["w"] / 2 - STAGE_W / 2) * k)) <= 3, (key, boxes, est)
