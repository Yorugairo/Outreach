"""P39 T2: the same source rendered twice in two separate browsers yields identical pixels.

Requires playwright + chromium; skipped where they are absent so the suite still runs.
What this proves is the harness's capture path (render_baseline.render_frame), which
neutralises the two wall-clock dependencies found on 2026-09-04: CSS transitions and the
fit-scaled stage. The shipped render_episode.py inherits neither fix until P39 T6.
"""
from __future__ import annotations

import hashlib
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402


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
