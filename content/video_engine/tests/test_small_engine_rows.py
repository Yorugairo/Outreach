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


# ---- R26-142: the agenda page's palette in the template's classes ---------------------------------------------
# P61 T8 wrote the PAGE form's colours as presentation attributes because the template was outside its write set;
# the house convention keeps a species' palette in the template's species CSS beside `.agnum` / `.agrow`. The page
# paints the same pixels (the four agenda-page goldens stay byte-identical). The 9:16 half of the row is NOT here:
# measured (P72 T27), the page form does not hold on a short - its shares are of the ROW'S HEIGHT only, so a tall
# narrow row takes a 279 px medallion, a 326 px icon over the text and 24.6 px type - a layout row for the parent.

AGENDA_MODULE = ROOT / "content/video_engine/scripts/species/agenda.mjs"
AGENDA_PAGE_CLASSES = {   # class -> the computed style it painted with before the move (the old attributes' values)
    "rect.agplate": {"fill": "rgb(5, 19, 30)"},
    "circle.agmed": {"fill": "none", "stroke": "rgb(245, 183, 46)"},
    "text.agtitle": {"fill": "rgb(242, 242, 242)", "fontWeight": "800", "letterSpacing": "1.5px", "paintOrder": "stroke",
                     "stroke": "rgba(27, 30, 35, 0.85)", "strokeWidth": "9px", "fontFamily": "Inter, Arial, sans-serif"},
    "text.agfig": {"fill": "rgb(245, 183, 46)", "fontWeight": "700", "paintOrder": "stroke",
                   "stroke": "rgba(27, 30, 35, 0.85)", "strokeWidth": "6px", "fontFamily": "Inter, Arial, sans-serif"},
}
HEX = re.compile(r"#[0-9A-Fa-f]{3,8}\b|rgba?\(")


def _module_function(src: str, name: str) -> str:
    start = src.index(f"export function {name}(")
    return src[start: src.index("\n}\n", start) + 2]


def test_r26_142_the_agenda_page_painter_writes_no_colour():
    src = AGENDA_MODULE.read_text(encoding="utf-8")
    body = _module_function(src, "paintAgendaPage")
    code = "\n".join(ln.split("/*")[0] for ln in body.splitlines())   # the painter's code, its comments aside
    assert not HEX.findall(code), f"a colour literal is left in paintAgendaPage: {HEX.findall(code)}"
    for attr in ('fill: AGENDA', 'stroke: AGENDA', '"font-family"', '"paint-order"', '"letter-spacing"'):
        assert attr not in code, f"paintAgendaPage still writes {attr} - the palette lives in the template"
    dials = src[src.index("export const AGENDA"): src.index("});", src.index("export const AGENDA"))]
    for dial in ("PAGE_INK", "PAGE_EDGE", "PAGE_GOLD", "PAGE_CHALK", "PAGE_HALO", "PAGE_FACE"):
        assert f"{dial}:" not in dials, f"AGENDA.{dial} restates a template colour - one line per class in the template"


def test_r26_142_the_template_carries_one_line_per_agenda_page_class():
    lines = TEMPLATE.read_text(encoding="utf-8").splitlines()
    for cls in ("agplate", "agmed", "agtitle", "agfig"):
        rule = [ln for ln in lines if ln.startswith(f"#species .{cls}, #species-under .{cls} {{")]
        assert len(rule) == 1, f"the template has {len(rule)} rules for .{cls}"


@needs_chromium
def test_r26_142_the_agenda_page_paints_the_palette_it_always_did():
    surface = "agenda-page"
    with tempfile.TemporaryDirectory() as td:
        html, t, (w, h) = _golden_html(surface, td)
        with SP.served(html, w, h) as (page, errs):
            RB.frame_png(page, t, (w, h))
            got = page.evaluate("""(spec) => { const out = {};
              for (const [sel, props] of Object.entries(spec)) {
                const el = document.querySelector('#species ' + sel); if (!el) { out[sel] = null; continue; }
                const cs = getComputedStyle(el); out[sel] = Object.fromEntries(Object.keys(props).map(k => [k, cs[k]]));
              } return out; }""", AGENDA_PAGE_CLASSES)
    assert got == AGENDA_PAGE_CLASSES, got
