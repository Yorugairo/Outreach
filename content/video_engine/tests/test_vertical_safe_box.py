"""P37 T0: on the 9:16 stage every dock, and the anchored caption, sits inside the mobile
safe box - x in [80, 880], y in [280, 1340] for docks, the caption in the strip below it
(y in [1340, 1440]) - and the 16:9 stage is untouched.

Doc 49 s49.1 / 50: platform chrome covers the top 280 px, the bottom 480 px and the right
200 px of a 1080x1920 short. Before this slice the docks were 952 px wide at x=64 (136 px
into the right rail) and the second dock ran to y=1780, under the caption bar.

Static checks always run; the rendered measurement needs playwright + chromium.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import render_baseline as RB  # noqa: E402

SAFE_X = (80, 880)
SAFE_Y = (280, 1340)
CAPTION_STRIP = (1340, 1440)


def _rule(selector: str) -> str:
    src = RB.TEMPLATE.read_text(encoding="utf-8")
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", src)
    assert m, f"no CSS rule for {selector!r}"
    return m.group(1)


def test_vertical_dock_css_is_inside_the_safe_box() -> None:
    dock = _rule('html[data-aspect="9:16"] .dock')
    assert "width: 800px" in dock and "top: 280px" in dock, dock
    assert "left: 80px" in _rule('html[data-aspect="9:16"] #dock-1')
    assert "left: 80px" in _rule('html[data-aspect="9:16"] #dock-2')
    assert "bottom: 480px" in _rule('html[data-aspect="9:16"] #caption.quiet')


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


def _measure(surface: str, ids: list[str]) -> dict[str, dict]:
    from playwright.sync_api import sync_playwright
    tl, uris, t, aspect = RB.load_surface(surface)
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "m.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": w, "height": h})
                page.goto(f"http://127.0.0.1:{port}/m.html", wait_until="networkidle")
                RB.prepare_page(page, w, h)
                page.evaluate("t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                page.wait_for_timeout(300)
                rects = page.evaluate("""(ids) => { const st = document.getElementById('stage').getBoundingClientRect();
                    return Object.fromEntries(ids.map(id => { const r = document.getElementById(id).getBoundingClientRect();
                      return [id, {x: r.x - st.x, y: r.y - st.y, w: r.width, h: r.height, right: r.right - st.x, bottom: r.bottom - st.y}]; })); }""", ids)
                browser.close()
        finally:
            srv.shutdown()
    return rects


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
def test_rendered_vertical_docks_and_caption_sit_inside_the_safe_box() -> None:
    r = _measure("dock-pair-9x16", ["dock-1", "dock-2", "caption"])
    for dock in ("dock-1", "dock-2"):
        d = r[dock]
        assert d["x"] >= SAFE_X[0] and d["right"] <= SAFE_X[1], f"{dock} x-span {d['x']:.0f}-{d['right']:.0f} leaves x{SAFE_X}"
        assert d["y"] >= SAFE_Y[0] and d["bottom"] <= SAFE_Y[1], f"{dock} y-span {d['y']:.0f}-{d['bottom']:.0f} leaves y{SAFE_Y}"
    assert r["dock-2"]["y"] >= r["dock-1"]["bottom"], "the stacked docks overlap"
    c = r["caption"]
    assert c["y"] >= CAPTION_STRIP[0] - 1 and c["bottom"] <= CAPTION_STRIP[1] + 1, f"caption y-span {c['y']:.0f}-{c['bottom']:.0f} is not in the strip {CAPTION_STRIP}"


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
def test_sixteen_nine_is_byte_identical_after_the_vertical_change() -> None:
    golden = (RB.FRAMES / "dock-pair-16x9.png").read_bytes()
    assert RB.rgb_bytes(golden)[1] == RB.rgb_bytes(RB.render_surface("dock-pair-16x9"))[1]
