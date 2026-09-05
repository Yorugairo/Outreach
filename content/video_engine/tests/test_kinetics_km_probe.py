"""P43 T3: the rendered probe. The module (kinetics/ink.mjs) is the truth; the SVG filter the template uses -
white stains summed with mix-blend-mode: plus-lighter, alpha moved into the colour channels, a per-channel
K-M table - is its approximation. This test renders that exact filter (the INLINED module text, not the .mjs)
over two overlapping rects and checks three pixels against the module's own numbers: a single stain, the
overlap (one full stain = the ink), and bare paper. Skipped without playwright + chromium."""
from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import sync_kinetics as SK  # noqa: E402

CREAM, CHARCOAL = "#F4E6C7", "#25313C"
TOL = 3   # 8-bit channels: the table is linear between entries and the coverage lands on an entry, so this is rounding


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


def _module_numbers() -> dict:
    """The module's own prediction for the probe geometry, from node (the same file the template inlines)."""
    src = ("import { INK, kmTable } from " + json.dumps((SK.MODULES / "ink.mjs").resolve().as_uri()) + ";\n"
           f"const t = kmTable({CREAM!r}, {CHARCOAL!r}), i = Math.round(0.25 * (t.n - 1));   // coverage 0.25 lands on an entry\n"
           "const single = [t.r[i], t.g[i], t.b[i]].map((v) => Math.round(v * 255));\n"
           "console.log(JSON.stringify({ single, coverage: INK.COVERAGE, slope: INK.ALPHA_SLOPE }));\n")
    out = subprocess.run(["node", "--input-type=module", "-e", src], capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


def _probe_html() -> str:
    inlined = SK.inline_text((SK.MODULES / "ink.mjs").read_text(encoding="utf-8"), "  ")
    return f"""<!doctype html><html><body style="margin:0;background:#000">
<div id="host"></div>
<script>
{inlined}
  const m = kmFilterMarkup({CREAM!r}, {CHARCOAL!r});
  document.getElementById("host").innerHTML =
    '<svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg" style="display:block">'
    + '<defs><filter id="km" x="0" y="0" width="1" height="1" color-interpolation-filters="sRGB">' + m + '</filter></defs>'
    + '<rect width="300" height="200" fill="{CREAM}"/>'
    + '<g filter="url(#km)">'
    + '<rect x="20" y="20" width="160" height="160" fill="#fff" opacity="0.25" style="mix-blend-mode:plus-lighter"/>'
    + '<rect x="120" y="20" width="160" height="160" fill="#fff" opacity="0.25" style="mix-blend-mode:plus-lighter"/>'
    + '</g></svg>';
</script></body></html>"""


@pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")
def test_the_svg_filter_reproduces_the_module(tmp_path: Path) -> None:
    from PIL import Image
    from playwright.sync_api import sync_playwright
    want = _module_numbers()
    html = tmp_path / "probe.html"
    html.write_text(_probe_html(), encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 320, "height": 220}, device_scale_factor=1).new_page()
        page.goto(html.as_uri())
        page.wait_for_timeout(100)
        png = page.screenshot(type="png", clip={"x": 0, "y": 0, "width": 300, "height": 200})
        browser.close()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    single, overlap, paper = im.getpixel((60, 100)), im.getpixel((150, 100)), im.getpixel((290, 195))
    ink = tuple(int(CHARCOAL[i:i + 2], 16) for i in (1, 3, 5))
    cream = tuple(int(CREAM[i:i + 2], 16) for i in (1, 3, 5))
    assert all(abs(a - b) <= TOL for a, b in zip(paper, cream)), f"bare paper {paper} != {cream}"
    assert all(abs(a - b) <= TOL for a, b in zip(overlap, ink)), f"two stains (one full coverage) {overlap} != the ink {ink} - is plus-lighter summing the coverage?"
    assert all(abs(a - b) <= TOL for a, b in zip(single, want["single"])), f"one stain {single} != the module's K-M {want['single']}"
    # and the defect the flag removes, for the record: alpha at the same coverage is not what K-M says
    alpha = tuple(round(c * (1 - 0.5) + k * 0.5) for c, k in zip(cream, ink))
    assert any(abs(a - b) > TOL for a, b in zip(single, alpha)), "K-M and a 50% film agree here - the probe would prove nothing"
