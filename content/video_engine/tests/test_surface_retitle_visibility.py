"""A surface retitle copies layout, never its parent's temporary hidden state."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]


def test_retitle_clones_geometry_but_not_arrival_opacity():
    source = (ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs").read_text(encoding="utf-8")
    start = source.index('const retitles = pageSpecies(scene, "retitle")')
    end = source.index("/* E50 (P47 T6)", start)
    actual_constructor = source[start:end]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content('<div id="page"><div id="title" style="left:42px;top:24px;opacity:0"></div></div>')
        result = page.evaluate("""(body) => {
          const st = {page:document.getElementById('page'),titleEl:document.getElementById('title'),seed:1};
          const scene = {}, P = false;
          const pageSpecies = () => [{text:'New title'}];
          const lpEl = (tag, cls, parent) => { const e=document.createElement(tag); e.className=cls; parent.append(e); return e; };
          const lpGlyphs = (e,text) => { e.textContent=text; return []; };
          const lpGlyphsWrap = lpGlyphs;
          return eval(body + '; ({opacity:getComputedStyle(retitles[0].div).opacity,left:retitles[0].div.style.left,text:retitles[0].div.textContent})');
        }""", actual_constructor)
        browser.close()
    assert result == {"opacity": "1", "left": "42px", "text": "New title"}
