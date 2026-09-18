"""R26-226 / E99 s82 - A MULTI-LINE PAGE BUILDS LINE BY LINE.

The operator, 2026-09-18, on frozen copy d of the Steel and Paper H unit: *"the crawl drawing on the
chart looks weird. The lines draw well while we're moving them, but drawing the first few years then
stopping for seemingly no reason is weird - it would be different if we were stopping to talk about
each section but that's not what the chart does. A better way to do this is to draw the first line
completely, label it, badge it, draw the 2nd line completely, badge it, draw the 3rd line completely,
badge it, draw the 4th line completely, badge it. Everything can be purposeful, and with rhythm and
direction without having to completely stop."*

WHAT WAS THERE. A dense-line page draws every series TOGETHER on the page's one build clock
(`scene-evidence-engine.mjs` `lpPaintChart`: `fr = clamp01((c - pp.stagger * 0.3) / 0.7)`), so four
lines crawl forward side by side and all four land at once; the H unit then staged them with one
`build_to` per spoken phrase, which is the crawl that stops.

THE DOOR is one token on the ledger id - `;build=lines` (or `;build=lines:<s>` for a per-series
length) - under which the page's N series draw SEQUENTIALLY: series 0 whole over its own share of the
build clock, its end label and its inline badge landing as it lands, then series 1, then series 2...
A `build_to` that names a datum on series i still caps that series there - the authored stop the
ruling allows ("if we were stopping to talk about each section") - and with no `build_to` no series
ever pauses mid-line.

BYTE-IDENTITY. A row that names no `build=` writes no key, `cs.lineBuild` is absent and the paint
expression is the one every golden was captured through.
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
import render_baseline as RB  # noqa: E402

SRC = (ROOT / "content/video_engine/scripts/build_scene_timeline_f.py").read_text(encoding="utf-8")
ENGINE = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")

# A FOUR-line object with no axes of its own - the shape the ruling is about (the divergence page's four
# lines), small enough to read: each series ends at its own level so the four end tags never stack.
LINES = {"title": "Four lines, one page", "sub": "index, 100 = the first period", "src": "the test bed",
         "unit": "",
         "series": [{"name": "A", "label": "+300%", "color": "crimson",
                     "pts": [[2020, 100], [2021, 160], [2022, 220], [2023, 300], [2024, 400]]},
                    {"name": "B", "label": "+200%", "color": "teal",
                     "pts": [[2020, 100], [2021, 140], [2022, 190], [2023, 250], [2024, 300]]},
                    {"name": "C", "label": "+100%", "color": "cobalt",
                     "pts": [[2020, 100], [2021, 120], [2022, 150], [2023, 175], [2024, 200]]},
                    {"name": "D", "label": "+18%", "color": "deemph",
                     "pts": [[2020, 100], [2021, 105], [2022, 108], [2023, 112], [2024, 118]]}],
         "badges": [{"label": "A", "value": "", "tag": "ours", "accent": "coral"},
                    {"label": "B", "value": "", "tag": "theirs", "accent": "teal"}]}
# a ONE-series page, DENSE (more points than `ledger_page.STORY_MAX_VALUES`, so `pick_builder` gives it the
# line builder rather than the story's) - the only shape that reaches the series-count refusal
ONE_LINE = {"title": "One line", "sub": "", "src": "the test bed", "unit": "",
            "series": [{"name": "A", "label": "+300%", "color": "crimson",
                        "pts": [[2000 + i, 100 + 12 * i] for i in range(14)]}]}
BARS = {"title": "Where the two stand", "sub": "", "src": "the test bed", "unit": "",
        "bars": [{"label": "A", "value": 300.0, "color": "crimson"},
                 {"label": "B", "value": 118.0, "color": "teal"}]}

SERIES_S = 1.2          # the per-series length this file authors, so the page's whole build is 4 x 1.2
GOLDEN_SURFACE = "page-build-lines"           # the same page at series 1's midpoint ...
GOLDEN_SURFACE_4TH = "page-build-lines-4th"   # ... and at series 3's
BUILD_START = 4.4       # ROLL 0.7 + SAVOR 0.8 + FIELD 2.4 + PUNCH 0.5: where the page's build clock opens
# The instants are MEASURED, not guessed: the build eases by `expoOut` (the pen law `strokeFrac` answers null
# unless `curvature_stroke` is on), which is front-loaded - at HALF of a series' 1.2 s window the line is already
# 96.9 % drawn (1 - 2^-5, read off the served page: dashoffset 37 of 1183). A line reads as DRAWING at u = 0.125
# of its own window: 1 - 2^-1.25 = 0.580 of its length, 0.15 s in.
T_IN_S1 = 5.75          # inside series 1's window (5.6-6.8): series 0 landed, series 1 0.58 drawn, 2 and 3 untouched
T_IN_S3 = 8.15          # inside series 3's window (8.0-9.2): series 0-2 landed, series 3 0.58 drawn


def _ep(obj: dict = LINES, name: str = "ev-lines-v1"):
    td = tempfile.TemporaryDirectory()
    ep = Path(td.name)
    (ep / "evidence/objects").mkdir(parents=True)
    (ep / f"evidence/objects/{name}.series.json").write_text(json.dumps(obj), encoding="utf-8")
    return td, ep


# ---- the token's grammar ------------------------------------------------------------------------------


def test_build_is_a_plate_option_and_check_opt_routes_it():
    assert "build" in B.PLATE_OPTS
    assert B.split_plate_opts("ledger:ev-lines-v1:line;build=lines")[1] == {"build": "lines"}
    assert B.split_plate_opts("ledger:ev-lines-v1:line;build=lines:1.2")[1] == {"build": "lines:1.2"}
    with pytest.raises(ValueError, match="is not one of"):
        B.split_plate_opts("ledger:ev-lines-v1:line;build=crawl")


def test_the_bare_mode_is_a_share_of_the_pages_own_build_window():
    assert B.PAGE_BUILD_MODES == ("lines",)
    assert B.page_build_spec("lines", None, None, "row") == {"mode": "lines"}
    assert B.page_build_spec("lines", "dense-line", 4, "row") == {"mode": "lines"}


def test_the_seconds_form_names_a_per_series_length_and_the_pages_whole_build():
    """`lines:<s>` is the length of ONE series' draw, so the page's build is N x s - and that total is written
    as `build_s`, the key the engine's `buildDur` and the motion gate's landing already read."""
    assert B.page_build_spec("lines:1.2", "dense-line", 4, "row") == {"mode": "lines", "series_s": 1.2, "build_s": 4.8}
    assert B.page_build_spec("lines:0.5", "dense-line", 3, "row") == {"mode": "lines", "series_s": 0.5, "build_s": 1.5}


def test_a_mode_the_engine_does_not_paint_is_refused_by_name():
    for bad in ("crawl", "sequential", "LINES", "", "line"):
        with pytest.raises(ValueError, match="is not one of"):
            B.page_build_spec(bad, None, None, "row")


def test_a_per_series_length_that_is_not_a_positive_finite_number_of_seconds_is_refused():
    for bad in ("lines:0", "lines:-1.2", "lines:abc", "lines:nan", "lines:inf", "lines:-inf", "lines:"):
        with pytest.raises(ValueError, match="seconds"):
            B.page_build_spec(bad, None, None, "row")


def test_a_per_series_length_under_the_floor_is_refused_with_the_frames_named():
    """The floor is the RENDER's own: `PAGE_BUILD_LINE_MIN_S` seconds at 24 fps is the fewest frames a pen can
    be seen moving through - under it a line does not draw, it pops."""
    assert B.PAGE_BUILD_LINE_MIN_S == 0.25
    with pytest.raises(ValueError, match="24 fps"):
        B.page_build_spec("lines:0.1", None, None, "row")
    assert B.page_build_spec("lines:0.25", None, None, "row")["series_s"] == 0.25


def test_the_bare_modes_SHARE_of_the_pages_window_meets_the_same_floor():
    """The bare mode divides a window it did not choose, so the floor is checked on the share: a page of many
    lines (or one with a short authored `build_s`) would otherwise give each line a draw nobody can see."""
    assert B.page_build_spec("lines", "dense-line", 4, "row", page_build_s=3.0) == {"mode": "lines"}
    with pytest.raises(ValueError, match="under the floor"):
        B.page_build_spec("lines", "dense-line", 13, "row", page_build_s=3.0)
    with pytest.raises(ValueError, match="under the floor"):
        B.page_build_spec("lines", "dense-line", 4, "row", page_build_s=0.8)
    # ... and a row that NAMES its seconds is measured on those, never on the window it is about to set
    assert B.page_build_spec("lines:1.2", "dense-line", 13, "row", page_build_s=3.0)["build_s"] == 15.6


def test_a_page_whose_own_build_is_too_short_for_its_lines_is_refused_on_the_row():
    td, ep = _ep(dict(LINES, build_s=0.8))
    try:
        with pytest.raises(ValueError, match="under the floor"):
            B.world_for_plate("ledger:ev-lines-v1:line;build=lines", (0, 0, 0), ep)
        world = B.world_for_plate("ledger:ev-lines-v1:line;build=lines:1.2", (0, 0, 0), ep)
        assert world["page"]["build_s"] == 4.8, "naming the seconds is the way out, and it sets the window"
    finally:
        td.cleanup()


def test_the_token_takes_one_setting_and_no_more():
    with pytest.raises(ValueError, match="takes one setting"):
        B.page_build_spec("lines:1.2:3", None, None, "row")


# ---- the builder bound -------------------------------------------------------------------------------


def test_only_a_builder_whose_PATHS_are_the_series_may_build_line_by_line():
    assert B.LINE_BUILD_BUILDERS == ("dense-line",)
    assert B.page_build_spec("lines", "dense-line", 4, "row") == {"mode": "lines"}
    for bad in ("story", "share", "race", "combo", "tiers", "treemap", "object", "decline", "progress"):
        with pytest.raises(ValueError, match="line by line"):
            B.page_build_spec("lines", bad, 4, "row")


def test_the_builder_bound_is_the_conservative_one_and_says_so():
    """`tiers` draws line BANDS and `combo` draws a line over its bars, so both have paths a sequence could run;
    they are refused anyway, because neither one's own painter reads the key and a build honoured by accident is a
    clock no author can predict (R26-223's rule, written once more here)."""
    block = SRC[SRC.index("LINE_BUILD_BUILDERS = ("):]
    block = block[:block.index("def page_build_spec")]
    assert "CONSERVATIVE bound" in block
    assert "tiers" in block and "combo" in block


def test_a_single_line_page_is_refused_because_there_is_no_sequence_in_one_line():
    """A one-series page has nothing to put in turn, and the mode would silently change its draw (the whole
    window instead of the 0.7 the shared clock gives it) - so it is refused by name rather than re-timed."""
    with pytest.raises(ValueError, match="one line"):
        B.page_build_spec("lines", "dense-line", 1, "row")
    with pytest.raises(ValueError, match="one line"):
        B.page_build_spec("lines", "dense-line", 0, "row")


# ---- what the row writes on the page ------------------------------------------------------------------


def test_the_row_writes_the_mode_onto_the_page():
    td, ep = _ep()
    try:
        world = B.world_for_plate("ledger:ev-lines-v1:line;build=lines", (0, 0, 0), ep)
        assert world["kind"] == B.SPECIES_LEDGER and world["page"]["builder"] == "dense-line"
        assert world["page"]["build"] == "lines"
        assert "build_s" not in world["page"], "the bare mode takes a SHARE of the page's own window"
        assert "build" not in world, "the option is consumed, never left on the world as a raw token"
    finally:
        td.cleanup()


def test_the_seconds_form_writes_the_pages_whole_build_length_too():
    td, ep = _ep()
    try:
        world = B.world_for_plate("ledger:ev-lines-v1:line;build=lines:1.2", (0, 0, 0), ep)
        assert world["page"]["build"] == "lines"
        assert world["page"]["build_s"] == 4.8, "four series at 1.2 s each"
    finally:
        td.cleanup()


def test_a_row_that_names_no_build_writes_nothing_at_all():
    """Byte-identity for every page compiled before this row."""
    td, ep = _ep()
    try:
        plain = B.world_for_plate("ledger:ev-lines-v1:line", (0, 0, 0), ep)
        assert "build" not in plain["page"]
        lines = B.world_for_plate("ledger:ev-lines-v1:line;build=lines", (0, 0, 0), ep)
        del lines["page"]["build"]
        assert lines == plain, "the mode is the ONLY difference the token makes"
    finally:
        td.cleanup()


def test_the_rows_length_outranks_an_objects_own_build_s():
    """The row is where a shot's timing is authored (`;domain=`'s rule): the object's seconds are the default."""
    td, ep = _ep(dict(LINES, build_s=9.0))
    try:
        plain = B.world_for_plate("ledger:ev-lines-v1:line", (0, 0, 0), ep)
        assert plain["page"]["build_s"] == 9.0
        world = B.world_for_plate("ledger:ev-lines-v1:line;build=lines:1.2", (0, 0, 0), ep)
        assert world["page"]["build_s"] == 4.8
    finally:
        td.cleanup()


def test_build_on_a_bars_page_is_refused_by_name():
    td, ep = _ep(BARS, "ev-bars-v1")
    try:
        with pytest.raises(ValueError, match="line by line"):
            B.world_for_plate("ledger:ev-bars-v1:bars;build=lines", (0, 0, 0), ep)
    finally:
        td.cleanup()


def test_build_on_a_single_line_page_is_refused_by_name():
    td, ep = _ep(ONE_LINE, "ev-one-v1")
    try:
        with pytest.raises(ValueError, match="one line"):
            B.world_for_plate("ledger:ev-one-v1:line;build=lines", (0, 0, 0), ep)
    finally:
        td.cleanup()


def test_build_is_refused_on_a_world_that_is_not_a_page():
    with pytest.raises(ValueError, match="build= is a LEDGER PAGE option"):
        B.world_for_plate("vecmap;build=lines", (0, 0, 0), Path("."))


# ---- the per-series clocks, on the timeline for the gates to read -------------------------------------


def _world(token: str = ";build=lines:1.2") -> dict:
    td, ep = _ep()
    try:
        return B.world_for_plate("ledger:ev-lines-v1:line" + token, (0, 0, 0), ep)
    finally:
        td.cleanup()


def test_a_page_that_builds_line_by_line_states_every_series_window():
    """One window per series, in the page's own order, in ABSOLUTE seconds - back to back, inside the page's
    build, ending exactly where the motion gate's landing says the chart lands."""
    world = _world()
    wins = B.page_line_windows(world, None, 10.0)
    land = 10.0 + B.MG._page_land_offset({"world": world})
    assert len(wins) == 4
    assert wins[0][0] == pytest.approx(land - 4.8)
    assert wins[-1][1] == pytest.approx(land)
    for (a, b), (c, d) in zip(wins, wins[1:]):
        assert b == pytest.approx(c), "back to back: no series waits and none overlaps"
        assert b - a == pytest.approx(SERIES_S) and d - c == pytest.approx(SERIES_S)


def test_the_bare_mode_shares_the_pages_own_window_between_the_series():
    world = _world(";build=lines")
    wins = B.page_line_windows(world, None, 0.0)
    assert len(wins) == 4
    assert wins[0][1] - wins[0][0] == pytest.approx(B.MG.LP_BUILD_S / 4)
    assert wins[-1][1] == pytest.approx(B.MG._page_land_offset({"world": world}))


def test_every_other_page_and_every_plate_states_no_series_window():
    assert B.page_line_windows(_world(""), None, 0.0) == []
    assert B.page_line_windows({"kind": "plate"}, None, 0.0) == []
    assert B.page_line_windows(None, None, 0.0) == []


def _cap(series: int, index: int, at: float = 7.0) -> dict:
    return {"kind": "build_to", "at": at, "dur": 1.0, "target": {"kind": "datum", "series": series, "index": index}}


def test_a_series_a_build_to_holds_at_index_0_takes_NO_turn():
    """The reviewer's MEDIUM: `capFrac` at index 0 is 0 and the build beat is spent on the first cap, so a series
    staged for a later reveal would draw NOTHING through a whole turn - a dead beat of still axes, the ruling's
    own enemy. It takes no turn; the lines that draw come earlier and the build ends earlier."""
    world = _world()
    wins = B.page_line_windows(world, [_cap(3, 0)], 10.0)
    land = 10.0 + B.MG._page_land_offset({"world": world})
    assert len(wins) == 3, wins
    assert wins[0][0] == pytest.approx(land - 4.8), "the build still opens where it did"
    for (a, b) in wins:
        assert b - a == pytest.approx(SERIES_S), "and a turn keeps its own length - the row named 1.2 s a line"
    assert wins[-1][1] == pytest.approx(land - SERIES_S), "the build ENDS one turn early: no empty beat in it"


def test_a_cap_past_the_first_datum_still_takes_its_turn():
    """A `build_to` that draws a line to a datum and stops IS the line drawing - the authored stop the ruling
    allows. Only a cap that holds a series at nothing costs it its turn."""
    assert len(B.page_line_windows(_world(), [_cap(3, 2)], 10.0)) == 4
    assert len(B.page_line_windows(_world(), [_cap(3, 1)], 10.0)) == 4
    assert len(B.page_line_windows(_world(), [{"kind": "undraw", "at": 7.0, "series": 3}], 10.0)) == 4


def test_the_first_cap_is_read_the_way_the_paint_reads_it():
    """One reading, written once: the EARLIEST `build_to` by `at`, and a cap naming no series applies to every
    one (the engine's own `forMe`)."""
    assert B.line_build_first_cap([_cap(3, 0, at=9.0), _cap(3, 4, at=5.0)], 3) == 4
    assert B.line_build_first_cap([_cap(3, 4, at=9.0), _cap(3, 0, at=5.0)], 3) == 0
    naked = {"kind": "build_to", "at": 5.0, "dur": 1.0, "target": {"kind": "datum", "index": 0}}
    assert B.line_build_first_cap([naked], 2) == 0, "a cap that names no series holds every one of them"
    assert B.line_build_first_cap([_cap(1, 0)], 2) is None
    assert B.line_build_first_cap(None, 0) is None


def test_every_series_held_at_zero_leaves_the_pages_own_order_standing():
    """Nothing to sequence - each line is 0 through the build either way - so the windows are the page's own
    rather than an empty list a reader would have to interpret."""
    caps = [_cap(i, 0) for i in range(4)]
    assert len(B.page_line_windows(_world(), caps, 10.0)) == 4


def test_the_row_loop_stamps_the_windows_beside_the_build_windows():
    """The wiring: the scene entry carries them, so a gate reads the clocks rather than re-deriving them."""
    body = SRC[SRC.index("bw = page_build_windows(world, row_species, a)"):]
    body = body[:body.index("\n\n")]
    assert "lw = page_line_windows(world, row_species, a)" in body
    assert 'scene["build_lines"]' in body


# ---- the engine: the default path is the one every golden was captured through ------------------------


def test_the_engine_keeps_the_shared_clock_when_no_page_names_a_mode():
    assert "const fr = LB ? (lb == null ? 1 : clamp01((c - lb / LB.n) * LB.n))" in ENGINE
    assert ": clamp01((c - pp.stagger * 0.3) / 0.7);" in ENGINE, "the old expression, unchanged, on the else arm"


def test_the_engine_reads_the_mode_off_the_page_the_compiler_writes():
    assert 'const LP_BUILD_LINES = "lines";' in ENGINE
    assert "pgBuildLines" in ENGINE and "st.lineBuild" in ENGINE


def test_the_engine_drops_a_held_series_from_the_turns_at_PAINT_time():
    """Which series take a turn depends on the row's species, which the builder never sees - so the load stamps
    the page's series and the paint (`lineBuildNow`, reading the same caps the fork below reads) decides."""
    assert "const lineBuildNow = (cs, caps) =>" in ENGINE
    assert "const LB = lineBuildNow(cs, caps);" in ENGINE
    assert "st.lineBuild = { slots };" in ENGINE, "one truth: the turn is the paint's, never a second copy at load"


# ---- THE FRAMES: the page on the served player, at the three instants ---------------------------------


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")

# Every series line as the player draws it: how much of it is drawn (the dashoffset the paint wrote), whether its
# END TAG has landed (the tag's own opacity, which carries its inline badge chip as a tspan), and whether its lead
# point is on the page. A failure names the series, not merely the frame.
LINES_PROBE = """() => {
  const world = [wA, wB].find(e => e.__lp && e.classList.contains('ledger'));
  const st = world.__lp, S = (st.states && st.states[st.active | 0]) || st;
  return (S.paths || []).map((pp) => {
    const off = parseFloat(pp.p.getAttribute("stroke-dashoffset") || "0");
    return { si: pp.si | 0, muted: !!pp.muted, off: off, len: pp.len, f: 1 - off / (pp.len || 1),
             tag: parseFloat(pp.name.getAttribute("opacity") || "0"), tagText: pp.name.textContent,
             chip: pp.name.querySelectorAll(".tagchip").length,
             tip: parseFloat(pp.tip.getAttribute("opacity") || "0"),
             tipR: parseFloat(pp.tip.getAttribute("r") || "0") };
  });
}"""


SEEK = ("t => { const s = document.getElementById('scrub'); s.value = t; "
        "s.dispatchEvent(new Event('input', {bubbles:true})); }")


def _measure(cases: dict) -> dict:
    """`{name: (timeline, uris, [t, ...])}` -> `{name: [the probe at each t]}`, in ONE browser session.

    One session because two `sync_playwright()` loops cannot be open at the same time in one process (the second
    start raises "using Playwright Sync API inside the asyncio loop"), and a module fixture that yields while its
    browser is up holds the first one open. The player is `test_page_born_with_a_domain`'s served harness."""
    from playwright.sync_api import sync_playwright
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    for name, (tl, uris, _ts) in cases.items():
        (root / f"{name}.html").write_text(RB.instantiate(tl, uris), encoding="utf-8")
    w, h = RB.STAGE["16:9"]
    srv, port = RB.serve(root)
    out: dict = {"errs": []}
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    try:
        for name, (_tl, _uris, ts) in cases.items():
            page = br.new_context(viewport={"width": w, "height": h}).new_page()
            page.on("pageerror", lambda e, n=name: out["errs"].append(f"{n}: {e}"))
            page.goto("http://127.0.0.1:%d/%s.html" % (port, name), wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            rows = []
            for tt in ts:
                page.evaluate(SEEK, tt)
                rows.append(page.evaluate(LINES_PROBE))
            out[name] = rows
            page.close()
    finally:
        br.close(); pw.stop(); srv.shutdown(); td.cleanup()
    return out


def _golden_timeline(lines: bool) -> tuple[dict, dict]:
    """The golden's own timeline, and the SAME page with the token taken off - the control."""
    tl, uris, _t, _a = RB.load_surface(GOLDEN_SURFACE)
    tl = json.loads(json.dumps(tl))
    if not lines:
        page = tl["scenes"][0]["world"]["page"]
        page.pop("build", None)
        page.pop("build_s", None)
    return tl, uris


@pytest.fixture(scope="module")
def measured():
    """The three cases the row is proved on: the page's own sequence at two instants, the SAME page with the
    token off (the crawl the ruling is about), and the sequence with an authored `build_to` on series 1."""
    lines_tl, uris = _golden_timeline(True)
    ctrl_tl, _ = _golden_timeline(False)
    cap_tl, _ = _golden_timeline(True)
    cap_tl["scenes"][0]["species"] = [{"kind": "build_to", "at": BUILD_START + 2 * SERIES_S, "dur": 1.0,
                                       "target": {"kind": "datum", "series": 1, "index": 2}}]
    held_tl, _ = _golden_timeline(True)
    held_tl["scenes"][0]["species"] = [
        {"kind": "build_to", "at": 4.4, "dur": 0.1, "target": {"kind": "datum", "series": 0, "index": 0}},
        {"kind": "build_to", "at": 20.0, "dur": 1.0, "target": {"kind": "datum", "series": 0, "index": 234}}]
    return _measure({"lines": (lines_tl, uris, [T_IN_S1, T_IN_S3]),
                     "control": (ctrl_tl, uris, [T_IN_S1]),
                     "cap": (cap_tl, uris, [T_IN_S1]),
                     "held": (held_tl, uris, [4.6, 8.0, 21.0])})


@needs_browser
def test_ON_THE_FRAME_series_0_is_whole_with_its_tag_landed_while_series_1_draws(measured):
    """The ruling, in one frame: inside series 1's window the FIRST line is finished and labelled, the second is
    part drawn and unlabelled, and the third and fourth have not started."""
    assert not measured["errs"], measured["errs"]
    p = measured["lines"][0]
    assert len(p) == 4, p
    s0, s1, s2, s3 = p
    assert s0["off"] == pytest.approx(0.0, abs=0.1), ("series 0 is drawn whole", s0)
    assert s0["tag"] == pytest.approx(1.0), ("... and its end tag has landed", s0)
    assert 0.2 < s1["f"] < 0.9, ("series 1 is mid-draw", s1)
    assert s1["tag"] == pytest.approx(0.0), ("... and says nothing yet", s1)
    assert s2["f"] == pytest.approx(0.0, abs=1e-3) and s3["f"] == pytest.approx(0.0, abs=1e-3), (s2, s3)


@needs_browser
def test_ON_THE_FRAME_the_landed_lines_lead_point_stays_and_the_drawing_ones_rides_the_pen(measured):
    """R26-228's lead point, landed per line: series 0's point is on the page with its spark radius while
    series 1's rides its own pen, and a line that has not started has no point at all."""
    s0, s1, s2, s3 = measured["lines"][0]
    assert s0["tip"] == pytest.approx(1.0) and s0["tipR"] > 0, ("the landed line keeps its lead point", s0)
    assert s1["tip"] == pytest.approx(1.0), ("the drawing line's tip rides the pen", s1)
    assert s2["tip"] == pytest.approx(0.0) and s3["tip"] == pytest.approx(0.0), (s2, s3)


@needs_browser
def test_ON_THE_FRAME_the_badge_lands_with_the_line_it_keys(measured):
    """"label it, badge it": a badge that keys a dense series IS that line's end tag (`ledger_page.badges_for`
    makes it `inline`), so it lands on the tag's own opacity - series 0's chip is up, series 1's is not."""
    s0, s1, _s2, _s3 = measured["lines"][0]
    assert s0["chip"] == 1 and s0["tag"] == pytest.approx(1.0), ("the first line's badge", s0)
    assert s1["chip"] == 1 and s1["tag"] == pytest.approx(0.0), ("the second's is on a tag not yet landed", s1)


@needs_browser
def test_ON_THE_FRAME_the_fourth_line_draws_last_with_the_other_three_standing(measured):
    p = measured["lines"][1]
    for s in p[:3]:
        assert s["off"] == pytest.approx(0.0, abs=0.1), ("landed", s)
        assert s["tag"] == pytest.approx(1.0), ("labelled", s)
    assert 0.2 < p[3]["f"] < 0.9, ("the fourth is still drawing", p[3])


@needs_browser
def test_ON_THE_FRAME_the_control_crawls_all_four_together(measured):
    """The before: the same page with no token draws every series at once, which is the crawl the ruling is
    about - so the sequence is the token's doing and nothing else's."""
    p = measured["control"][0]
    drawing = [s for s in p if 0.01 < s["f"] < 0.995]
    assert len(drawing) == 4, ("all four lines are mid-draw together", [s["f"] for s in p])
    assert max(s["f"] for s in p) - min(s["f"] for s in p) < 0.35, ("side by side", [s["f"] for s in p])
    lines = measured["lines"][0]
    assert max(s["f"] for s in lines) - min(s["f"] for s in lines) > 0.9, "and the token's page is a sequence"


# ---- the authored stop the ruling allows -------------------------------------------------------------


@needs_browser
def test_ON_THE_FRAME_a_build_to_on_one_series_still_stops_THAT_series_at_its_datum(measured):
    """*"it would be different if we were stopping to talk about each section"*: a `build_to` naming a datum on
    series 1 caps series 1 inside its own window and leaves every other series' sequence alone."""
    p, plain = measured["cap"][0], measured["lines"][0]
    assert p[0]["off"] == pytest.approx(0.0, abs=0.1), ("series 0 still lands whole", p[0])
    assert p[1]["f"] < plain[1]["f"], ("series 1 is held at its cap, not drawn to where it would be", p[1], plain[1])
    assert p[2]["f"] == pytest.approx(0.0, abs=1e-3), ("and series 2 has still not started", p[2])


@needs_browser
def test_ON_THE_FRAME_a_series_held_at_index_0_costs_the_page_no_beat(measured):
    """The reviewer's MEDIUM on the frame: series 0 is staged for a reveal at 20 s, so the page OPENS with series
    1 drawing (not 1.2 s of still axes), the three drawing lines take the first three turns, and series 0 arrives
    whole on its own word."""
    open_, done, revealed = measured["held"]
    assert open_[0]["f"] == pytest.approx(0.0, abs=1e-3), ("the held series draws nothing", open_[0])
    assert 0.2 < open_[1]["f"] < 0.995, ("0.2 s in, the page is ALREADY drawing a line", open_[1])
    assert open_[2]["f"] == pytest.approx(0.0, abs=1e-3) and open_[3]["f"] == pytest.approx(0.0, abs=1e-3)
    assert [round(s["f"], 3) for s in done[1:]] == [1.0, 1.0, 1.0], ("all three turns taken by 8.0 s", done)
    assert done[0]["f"] == pytest.approx(0.0, abs=1e-3), ("... and the held one is still waiting", done[0])
    assert revealed[0]["f"] == pytest.approx(1.0, abs=1e-3), ("it joins on its own cap clock", revealed[0])


# ---- the goldens ------------------------------------------------------------------------------------


def test_the_golden_pair_is_the_same_page_at_two_instants():
    """One page, two instants - series 1's midpoint and series 3's. (A second instant of ONE surface would live
    in `render_baseline.PROOF_FRAMES`, which is outside this lane's write set, so the pair is two surfaces off
    one source function instead.)"""
    import build_golden_sources as G
    assert G.FRAME_T[GOLDEN_SURFACE] == T_IN_S1
    assert G.FRAME_T[GOLDEN_SURFACE_4TH] == T_IN_S3
    a, b = G.SURFACES[GOLDEN_SURFACE]()[0], G.SURFACES[GOLDEN_SURFACE_4TH]()[0]
    assert a == b, "the same timeline: only the instant differs"
    page = a["scenes"][0]["world"]["page"]
    assert page["build"] == "lines" and page["build_s"] == 4.8
    assert len(page["series"]) == 4


def test_the_golden_source_carries_exactly_what_the_token_writes():
    """The golden is hand-built (as every golden source is), so it is pinned to the COMPILER's own answer: the
    two keys `;build=lines:1.2` writes on a four-series page, and no third."""
    import build_golden_sources as G
    page = G.SURFACES[GOLDEN_SURFACE]()[0]["scenes"][0]["world"]["page"]
    spec = B.page_build_spec("lines:%g" % SERIES_S, "dense-line", len(page["series"]), "row")
    assert page["build"] == spec["mode"] and page["build_s"] == spec["build_s"]


def test_the_goldens_are_registered_and_have_their_frames():
    import test_golden_frames as TGF
    for name in (GOLDEN_SURFACE, GOLDEN_SURFACE_4TH):
        assert name in TGF.SURFACES
        assert (RB.SOURCES / f"{name}.timeline.json").exists(), f"{name}: run build_golden_sources.py {name}"
        assert (RB.FRAMES / f"{name}.png").exists(), f"{name}: no golden frame"
