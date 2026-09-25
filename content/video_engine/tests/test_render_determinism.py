"""P39 T2: the same source rendered twice in two separate browsers yields identical pixels.
P72 T9 (below): the fonts settle before a capture, the repeat probe, the LF sources, the guarded opener.

Requires playwright + chromium; skipped where they are absent so the suite still runs.
What this proves is the harness's capture path (render_baseline.render_frame), which
neutralises the two wall-clock dependencies found on 2026-09-04: CSS transitions and the
fit-scaled stage. The shipped render_episode.py inherits neither fix until P39 T6.
"""
from __future__ import annotations

import hashlib
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(TESTS / "golden"))

import render_baseline as RB  # noqa: E402

import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_chromium_and_pillow = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


@needs_chromium_and_pillow
@pytest.mark.parametrize("surface", ["chart-callout", "dock-pair-9x16"])
def test_same_source_renders_identically_in_two_browsers(surface: str) -> None:
    first = RB.rgb_bytes(RB.render_surface(surface))
    second = RB.rgb_bytes(RB.render_surface(surface))
    assert first[0] == second[0] == RB.STAGE["9:16" if surface.endswith("9x16") else "16:9"]
    assert hashlib.sha256(first[1]).hexdigest() == hashlib.sha256(second[1]).hexdigest(), (
        f"{surface}: two renders of the same source differ - a wall-clock dependency is back")


# ---- R26-48 (P52 T4): the page's glyphs are a function of t, never of the page's history ----------

TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
TEXT_RULE = "text-rendering: geometricPrecision"
WARM_WALK_S = 0.25   # the step a scrub session walks in with - enough paints to warm the font cache


def test_the_template_writes_the_pages_glyphs_at_geometric_precision() -> None:
    """The static half of R26-48's cure: the rule is ON the page's SVG text, for every page surface.

    Chromium's default `text-rendering: auto` lets Skia pick hinted advances and a hinted ascent per
    raster pass, so the SAME <text> measured 0.80 px taller in its ink box on a page that had painted
    many frames than on a fresh one. A render arrives cold and the preview arrives warm; the two
    disagreed on every axis label. `geometricPrecision` takes the outline's own metrics.
    """
    css = TEMPLATE.read_text(encoding="utf-8")
    rule = [ln for ln in css.splitlines() if TEXT_RULE in ln]
    assert rule, f"the template no longer writes `{TEXT_RULE}` - R26-48's sub-pixel text class is back"
    selector = rule[0].split("{")[0]
    assert ".lp-chart text" in selector, (
        f"`{TEXT_RULE}` must cover the page CHART's text (every label the engine writes), got: {selector!r}")


def _page_text_boxes(page):
    """Every `.lp-chart text`'s ink box and advance width, keyed by its content and its written x/y -
    the measurement R26-48's element-by-element diff found the drift in."""
    return page.evaluate("""() => {
      const out = {};
      document.querySelectorAll('.lp-chart text').forEach((el, i) => {
        let bb = null; try { bb = el.getBBox(); } catch (e) { return; }
        let len = null; try { len = el.getComputedTextLength(); } catch (e) {}
        const k = i + '|' + (el.getAttribute('class') || '') + '|' + (el.textContent || '').slice(0, 24)
                + '|' + el.getAttribute('x') + ',' + el.getAttribute('y');
        out[k] = [+bb.x.toFixed(4), +bb.y.toFixed(4), +bb.width.toFixed(4), +bb.height.toFixed(4),
                  len === null ? null : +len.toFixed(4)];
      });
      return out;
    }""")


@needs_chromium_and_pillow
@pytest.mark.parametrize("surface", ["ledger-page-mid-build", "span-decade"])
def test_a_page_label_measures_the_same_warm_and_cold(surface: str) -> None:
    """The behavioural half: one fresh page seeking straight to t, one page walked in frame by frame,
    and every label's ink box and advance identical to four decimals. RED before the rule above
    (`text.lab` at Tokyo 7.69: warm y 1008.64 / h 44.49, cold y 1008.04 / h 46.00, same attributes)."""
    from playwright.sync_api import sync_playwright

    tl, uris, t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris, RB.TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)

                def open_page():
                    p = br.new_context(viewport={"width": w, "height": h}).new_page()
                    p.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                    RB.prepare_page(p, w, h)
                    return p

                cold = open_page()                                  # as render_episode arrives
                RB.frame_png(cold, t, (w, h)); RB.frame_png(cold, t, (w, h))
                cold_boxes = _page_text_boxes(cold)

                warm = open_page()                                  # as a scrub session arrives
                u = 0.0
                while u < t:
                    RB.frame_png(warm, round(u, 3), (w, h))
                    u += WARM_WALK_S
                RB.frame_png(warm, t, (w, h))
                warm_boxes = _page_text_boxes(warm)
                br.close()
        finally:
            srv.shutdown()

    assert cold_boxes, f"{surface}: no .lp-chart text on the page - the surface cannot pin the class"
    assert sorted(cold_boxes) == sorted(warm_boxes), f"{surface}: the two pages do not carry the same labels"
    moved = {k: (warm_boxes[k], cold_boxes[k]) for k in cold_boxes if warm_boxes[k] != cold_boxes[k]}
    assert not moved, (
        f"{surface}: {len(moved)} label(s) measure differently warm vs cold (R26-48 is back) - "
        + "; ".join(f"{k!r} warm {v[0]} cold {v[1]}" for k, v in list(moved.items())[:4]))


# ---- P72 T9: the renders and the golden sources are deterministic --------------------------------------------
# - R26-243 / R26-251: the player's hand (Kalam) is fetched from Google Fonts when the page first uses it. A capture
#   taken when that stylesheet or a face never arrived rendered the title, the sub and the citation in the fallback
#   face with no error (race-path-eased's diff under a full-suite load), and a face fetch that failed raised a bare
#   NetworkError out of `prepare_page`. The shell now says when its faces have settled (`window.__fontsSettled`), and
#   `prepare_page` waits on that signal instead of a fixed 250 ms: a face that failed is fetched again on a reloaded
#   page, and a hand that never arrives refuses the capture by name.
# - R26-140: `render_baseline.py --repeat N` captures each surface N times in fresh pages and N times in one warm page,
#   and names every capture that differs, where, and whether the page's DOM differed with it.
# - R26-323: the golden sources are written LF on every platform.
# - R26-351: every test starts Playwright through the guarded helper in `served_player.py`.
#
# The probes that found each class are in the slice's evidence (P72 T9); these are the tests that keep them found.

# R26-360: the hand is served from the committed faces - a split page fetches them beside itself (a single-file page
# carries them inline and cannot drop one), so the fault tests break the face on the split form's own path.
HAND_FACES = "**/fonts/kalam/*.woff2"
THROTTLED = ["tiers-two", "treemap-cross", "race-path-eased"]   # R26-251's two titles and R26-243's golden
CPU_RATE = 6   # Chromium's own CPU throttle: 6x slower than the host (the probe also ran 20x: every frame matched)



def _golden_page(surface: str, route=None, cpu: float | None = None, split: bool = False):
    """A golden surface served in a fresh driver and loaded, NOT prepared: (page, t, (w, h), close).
    `route(page)` installs request routes before the load; `cpu` throttles the page's CPU by that factor;
    `split` serves the build form (the page, its timeline, its engine and its faces as files) instead of one page."""
    tl, uris, t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect]
    td = tempfile.TemporaryDirectory()
    if split:
        html = RB.write_split(Path(td.name), tl, uris, f"{surface}.timeline.json")
    else:
        html = Path(td.name) / f"{surface}.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    srv, port = RB.serve(html.parent)
    pw = br = None

    def close():
        SP.run_all(br.close if br is not None else None, pw.stop if pw is not None else None, srv.shutdown, td.cleanup)

    try:
        pw, br = SP.launch()
        page = br.new_context(viewport={"width": w, "height": h}).new_page()
        if cpu:
            page.context.new_cdp_session(page).send("Emulation.setCPUThrottlingRate", {"rate": float(cpu)})
        if route:
            route(page)
        page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
    except BaseException:
        close()
        raise
    return page, t, (w, h), close


def _golden_rgb(surface: str) -> bytes:
    return RB.rgb_bytes((RB.FRAMES / f"{surface}.png").read_bytes())[1]


# ---- R26-243 / R26-251: the fonts settle before a capture -------------------------------------------------------


@needs_chromium_and_pillow
def test_the_player_says_when_its_fonts_have_settled():
    """The shell's signal: every face the page asked for loaded, the hand among them, none failed."""
    page, _t, _size, close = _golden_page("race-path-eased")
    try:
        report = page.evaluate("() => window.__fontsSettled()")
    finally:
        close()
    assert report["ok"] is True, report
    assert report["failed"] == [] and report["missing"] == [], report
    hand = [f for f in report["faces"] if f["family"] == "Kalam" and f["status"] == "loaded"]
    assert {f["weight"] for f in hand} >= {"400", "700"}, report


@needs_chromium_and_pillow
def test_prepare_page_waits_on_the_signal_not_a_fixed_clock():
    """R26-251: a fixed 250 ms outlived by a slow rebuild is not a wait. On a page that carries the signal,
    `prepare_page` never sleeps on the wall clock."""
    page, t, size, close = _golden_page("race-path-eased")
    slept: list[float] = []
    try:
        page.wait_for_timeout = lambda ms: slept.append(ms)
        RB.prepare_page(page, *size)
        png = RB.frame_png(page, t, size)
    finally:
        close()
    assert slept == [], f"prepare_page slept {slept} ms on the wall clock"
    assert RB.rgb_bytes(png)[1] == _golden_rgb("race-path-eased")


@needs_chromium_and_pillow
def test_a_hand_that_never_arrives_refuses_the_capture_by_name():
    """R26-243's diff class, made on purpose: the hand never arrives (every face request refused - the Google Fonts
    sheet until R26-360, the committed faces beside a split page since). The base captured the title, the sub and the
    citation in the fallback face without a word; the capture is now refused, naming the hand."""
    page, _t, size, close = _golden_page("race-path-eased", route=lambda p: p.route(HAND_FACES, lambda r: r.abort()),
                                         split=True)
    try:
        with pytest.raises(RB.FontsUnsettled) as err:
            RB.prepare_page(page, *size)
    finally:
        close()
    assert "Kalam" in str(err.value), err.value
    assert f"{RB.FONT_TRIES} loads" in str(err.value), err.value


@needs_chromium_and_pillow
def test_a_face_fetch_that_fails_once_is_fetched_again_and_the_frame_is_the_golden():
    """The session's flake, made on purpose: the first face request fails (the base raised NetworkError out of
    `prepare_page`). The page is loaded again, the face arrives, and the frame is the golden's to the byte."""
    left = {"n": 1}

    def flaky(route):
        if left["n"] > 0:
            left["n"] -= 1
            route.abort()
        else:
            route.continue_()

    page, t, size, close = _golden_page("race-path-eased", route=lambda p: p.route(HAND_FACES, flaky), split=True)
    try:
        RB.prepare_page(page, *size)
        png = RB.frame_png(page, t, size)
    finally:
        close()
    assert left["n"] == 0, "the route never saw a face request - the probe proved nothing"
    assert RB.rgb_bytes(png)[1] == _golden_rgb("race-path-eased")


@needs_chromium_and_pillow
@pytest.mark.parametrize("surface", THROTTLED)
def test_a_cpu_throttled_capture_matches_the_golden(surface: str):
    """Acceptance (1): a page under a 6x CPU throttle captures the golden's own bytes."""
    page, t, size, close = _golden_page(surface, cpu=CPU_RATE)
    try:
        RB.prepare_page(page, *size)
        png = RB.frame_png(page, t, size)
    finally:
        close()
    assert RB.rgb_bytes(png)[1] == _golden_rgb(surface), f"{surface}: the throttled capture differs from its golden"


# ---- R26-140: the repeat probe ----------------------------------------------------------------------------------


@needs_chromium_and_pillow
def test_the_repeat_probe_reports_each_capture_against_the_golden_and_names_a_drift():
    """`--repeat 2` on data-to-bars: two fresh-page captures, each the golden's to the byte (the fresh-page rule
    the goldens stand on), and two warm-page captures, each either identical or named with its bytes, its box and
    whether the DOM moved with it."""
    (rec,) = RB.repeat(["data-to-bars"], 2)
    assert rec["surface"] == "data-to-bars" and rec["t"] == RB.load_surface("data-to-bars")[2]
    assert [c["bytes"] for c in rec["fresh"]] == [0, 0], rec["fresh"]
    assert len(rec["warm"]) == 2 and rec["warm"][0]["bytes"] == 0, rec["warm"]
    for c in rec["warm"]:
        assert c["cause"] in RB.REPEAT_CAUSES, c
        assert (c["bytes"] == 0) == (c["cause"] == "identical") == (c["box"] is None), c
    lines = RB.repeat_lines(rec)
    assert lines[0].startswith("data-to-bars") and "fresh 2/2 identical to the golden" in lines[0], lines


def test_the_repeat_probe_names_a_raster_drift_and_a_state_drift_apart():
    """The cause is read, not guessed: the same DOM with other pixels is the raster's; a DOM that moved is state."""
    same = RB.repeat_cause(b"a" * 12, b"a" * 12, "<svg/>", "<svg/>")
    raster = RB.repeat_cause(b"a" * 12, b"b" * 12, "<svg/>", "<svg/>")
    state = RB.repeat_cause(b"a" * 12, b"b" * 12, "<svg/>", "<svg x='1'/>")
    unseen = RB.repeat_cause(b"a" * 12, b"a" * 12, "<svg/>", "<svg x='1'/>")
    assert (same, raster, state, unseen) == ("identical", "raster (same DOM)", "state (the DOM moved)", "identical")


def test_the_repeat_flag_is_on_the_command_line():
    src = (ROOT / "content/video_engine/scripts/render_baseline.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--repeat", type=int', src), "render_baseline.py has no --repeat N"


# ---- R26-323: the sources land LF ---------------------------------------------------------------------------------


def test_the_golden_sources_are_written_lf(tmp_path, monkeypatch):
    """R26-323: `write_surface` used `write_text` without `newline`, so every source landed CRLF on Windows and
    each integrator normalised new sources by hand. A timeline surface and a page surface are written to a temp dir;
    their bytes carry no CR."""
    import build_golden_sources as G
    monkeypatch.setattr(G, "SOURCES", tmp_path)
    page_surface = sorted(G.PAGE_SURFACES)[0]
    written = G.write_surface("chart-callout") + G.write_surface(page_surface)
    assert len(written) == 3, written
    crs = {p.name: p.read_bytes().count(b"\r") for p in written}
    assert all(n == 0 for n in crs.values()), f"CR bytes in the written sources: {crs}"
    assert all(p.read_bytes().endswith(b"}\n") for p in written)


# ---- R26-351: one guarded opener ----------------------------------------------------------------------------------


# A file whose opener cannot move onto served_player stays as it is, named here with its reason. None today.
UNMOVED: dict[str, str] = {}


def test_no_test_starts_playwright_outside_the_guarded_helper():
    """R26-351: `sync_playwright().start()` is written once, in served_player.launch; every other test file reaches
    the driver through it (or through `with sync_playwright()`, which closes itself)."""
    offenders = sorted(p.name for p in TESTS.glob("*.py")
                       if p.name not in ("served_player.py", Path(__file__).name) and p.name not in UNMOVED
                       and "sync_playwright().start()" in p.read_text(encoding="utf-8"))
    assert offenders == [], f"{len(offenders)} test files start Playwright unguarded: {offenders}"


@needs_chromium_and_pillow
def test_a_setup_that_raises_leaves_no_driver_running(tmp_path, monkeypatch):
    """R26-145 / R26-351's defect, made on purpose: the served page's preparation raises. The opener closes what it
    opened and re-raises, and the next driver in this process starts (the leak made it raise 'using Playwright Sync
    API inside the asyncio loop')."""
    from playwright.sync_api import sync_playwright
    html = tmp_path / "blank.html"
    html.write_text("<!doctype html><title>blank</title>", encoding="utf-8")

    def boom(*_a, **_k):
        raise RuntimeError("the preparation failed on purpose")

    monkeypatch.setattr(RB, "prepare_page", boom)
    with pytest.raises(RuntimeError, match="on purpose"):
        SP.open_served(html, 320, 240)
    with sync_playwright() as pw:
        pw.chromium.launch(headless=True).close()


def test_a_close_runs_every_step_when_one_raises():
    ran: list[str] = []

    def bad():
        ran.append("browser")
        raise RuntimeError("the browser close failed")

    with pytest.raises(RuntimeError, match="browser close"):
        SP.run_all(bad, lambda: ran.append("driver"), None, lambda: ran.append("server"))
    assert ran == ["browser", "driver", "server"]
