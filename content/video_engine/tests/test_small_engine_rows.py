"""P72 T27 - the small engine rows, one section (and one commit) each.

R26-57   the stage-space text at geometric precision (the page's own rule, R26-48, widened to the species' labels)
R26-72   a tiers page draws its same-unit tiers on the shared domain it carries (E79)
R26-73   the 9:16 newsreel default, measured against E84
R26-142  the agenda page's palette in the template's classes
R26-360  the hand (Kalam) served from the committed file, never from Google Fonts
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
ROOT = TESTS.parents[2]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))
sys.path.insert(0, str(TESTS / "golden"))
sys.path.insert(0, str(TESTS))

import render_baseline as RB  # noqa: E402
import served_player as SP  # noqa: E402 - R26-351: the one guarded Playwright opener

TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"


def _chromium_available() -> bool:
    try:
        from PIL import Image  # noqa: F401
        with SP.browser():
            return True
    except Exception:
        return False


needs_chromium = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _golden_html(surface: str, td: str) -> tuple[Path, float, tuple[int, int]]:
    tl, uris, t, aspect = RB.load_surface(surface)
    html = Path(td) / f"{surface}.html"
    html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
    return html, t, RB.STAGE[aspect]


# ---- R26-57: the stage-space text at geometric precision ------------------------------------------------------
# R26-48's rule covers the PAGE's glyphs (`.lp text, .lp-chart text`); the stage-space species write their SVG text
# at Chromium's default `auto`, which lets Skia pick hinted advances per raster pass - the warm / cold defect the
# page's labels had. Read off the rendered DOM: each class, as the engine writes it, computes the rule.

STAGE_TEXT = [("species", "lab"), ("species", "chiplab"), ("species", "flowtag"), ("species", "vmstamp"),
              ("species-under", "lab"), ("species-under", "chiplab"), ("species-under", "flowtag"),
              ("species-under", "vmstamp"),
              ("chartbox", "ct"), ("chartbox", "cs"), ("chartbox", "csr"), ("chartbox", "cl")]
PAGE_RULE = "  .lp text, .lp-chart text { text-rendering: geometricPrecision; }"

_TEXT_RENDERING_JS = """(pairs) => {
  const NS = 'http://www.w3.org/2000/svg', out = {};
  let box = document.querySelector('#stage svg.chartbox');
  if (!box) { box = document.createElementNS(NS, 'svg'); box.setAttribute('class', 'chartbox'); document.getElementById('stage').appendChild(box); }
  for (const [host, cls] of pairs) {
    const parent = host === 'chartbox' ? box : document.getElementById(host);
    const el = document.createElementNS(NS, 'text'); el.setAttribute('class', cls); el.textContent = 'x';
    parent.appendChild(el);
    out[host + ' .' + cls] = getComputedStyle(el).textRendering;
    el.remove();
  }
  const page = document.createElementNS(NS, 'svg'); page.setAttribute('class', 'lp-chart');
  const t = document.createElementNS(NS, 'text'); page.appendChild(t); document.getElementById('stage').appendChild(page);
  out['.lp-chart text'] = getComputedStyle(t).textRendering; page.remove();
  out['#caption'] = getComputedStyle(document.getElementById('caption')).textRendering;
  return out;
}"""


@needs_chromium
def test_r26_57_every_stage_space_text_class_computes_geometric_precision():
    with tempfile.TemporaryDirectory() as td:
        html, t, (w, h) = _golden_html("chip-board", td)
        with SP.served(html, w, h) as (page, errs):
            RB.frame_png(page, t, (w, h))   # the board as it is read: every chip landed
            got = page.evaluate(_TEXT_RENDERING_JS, [list(p) for p in STAGE_TEXT])
            written = page.evaluate("() => [...document.querySelectorAll('#species .chiplab')].map(e => getComputedStyle(e).textRendering)")
    wrong = {k: v for k, v in got.items() if k.split(" .")[0] in ("species", "species-under", "chartbox") and v != "geometricprecision"}
    assert not wrong, f"stage-space text still at Chromium's default: {wrong}"
    assert written and set(written) == {"geometricprecision"}, f"the chip board's own labels compute {written}"
    assert got[".lp-chart text"] == "geometricprecision"   # the page's rule (R26-48) stands
    assert got["#caption"] == "auto", "the rule is scoped to the named SVG classes - the caption layer is not in it"


def test_r26_57_the_pages_rule_is_unchanged_and_the_stage_rule_is_its_own_line():
    lines = TEMPLATE.read_text(encoding="utf-8").splitlines()
    assert PAGE_RULE in lines, "R26-48's page rule must stay exactly as it was"
    first = next(ln for ln in lines if "text-rendering: geometricPrecision" in ln)
    assert first == PAGE_RULE, "test_render_determinism reads the FIRST geometricPrecision line as the page's"
