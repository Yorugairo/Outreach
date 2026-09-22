"""Native T19 player proof on a synthetic cream stage, not an approved art asset."""
import copy
import json
import base64
from pathlib import Path

import pytest
import test_fed_chart_readability as H

QUAD = [[.305622, .185972], [.693182, .187035], [.693182, .407014], [.305622, .407014]]


def synthetic_assets():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="#234252"/><rect x="586" y="200" width="745" height="240" fill="#F4E6C7"/></svg>'
    return {"__audio__": "", "synthetic-hall": "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()}


def surface_timeline():
    timeline = H._timeline("legacy")
    hall = copy.deepcopy(timeline["scenes"][0])
    hall.update(scene_id="hall", span=[0, 4], species=[], build_windows=[], build_lines=[])
    hall["world"] = {"asset_id": "synthetic-hall", "kind": "image", "idle": "none",
                     "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    hall["surface_page"] = {"to_scene": "chart", "span": [2.8, 4], "quad": QUAD}
    chart = copy.deepcopy(timeline["scenes"][1])
    chart.update(scene_id="chart", span=[4, 10], species=[], exit="cut")
    page = H.LPG.build_spec(H._source(H.RRP), "line")
    page.update(enter="surface", full_stage=True, caption="anchor",
                surface_from={"scene": "hall", "surface": "center-paper", "quad": QUAD,
                              "lead_s": 1.2, "grow_s": .45})
    chart["world"] = {"kind": "ledger", "page": page, "idle": "none",
                      "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    timeline["scenes"] = [hall, chart]
    return timeline


PROBE = """() => [...document.querySelectorAll('.surface-page-cream')].map(p => {
 const s=p.querySelector('svg.lp-chart'), r=s.getBoundingClientRect(), v=s.viewBox.baseVal;
 const world=p.closest('.world');
 return {world:world.id,worldOpacity:getComputedStyle(world).opacity,clip:world.style.clipPath,
   progress:p.dataset.surfaceProgress,view:[v.width,v.height],rect:[r.x,r.y,r.width,r.height],
   paths:[...s.querySelectorAll('path.ser')].map(n=>n.getAttribute('d')),
   labels:[...s.querySelectorAll('text')].map(n=>[n.textContent,n.getAttribute('x'),n.style.opacity]),
   background:p.style.backgroundColor,stroke:s.querySelector('path.ser').getAttribute('stroke'),
   labelFill:getComputedStyle(s.querySelector('.lab')).fill,
   labelFills:[...s.querySelectorAll('.lab')].map(n=>getComputedStyle(n).fill),
   worldImage:getComputedStyle(world).backgroundImage};
})"""


@H.needs_browser
def test_surface_landed_figure_paints_and_reverse_seek_hides_it(tmp_path: Path):
    from playwright.sync_api import sync_playwright
    timeline = surface_timeline()
    timeline["scenes"][1]["species"] = [{
        "kind": "figure", "at": 5, "dur": .5, "series": 0,
        "target": {"kind": "datum", "index": 0},
        "text": "First observation", "dy": -.5,
    }]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        td, server, page, errors, width, height = H._open_player(browser, timeline, synthetic_assets())
        try:
            observations = {}
            for t in (6, 4.225, 4.6, 6):
                H._at(page, t, (width, height), tmp_path / f"figure-{t}.png")
                state = page.evaluate("() => window.__lpProbe()")
                assert not errors, errors
                assert len(state["figures"]) == 1
                figure = state["figures"][0]
                assert figure["opacity"] == (1 if t >= 5 else 0)
                if t == 6:
                    assert all(alpha == 1 for alpha in figure["label"])
                if t in observations:
                    assert figure == observations[t]
                observations[t] = figure
        finally:
            page.context.close()
            server.shutdown()
            td.cleanup()
            browser.close()


@H.needs_browser
@pytest.mark.parametrize("entry", ["surface", "built"])
def test_surface_full_stage_labels_have_safe_horizontal_margins(tmp_path: Path, entry: str):
    from playwright.sync_api import sync_playwright
    timeline = surface_timeline()
    if entry == "built":
        timeline["scenes"][0].pop("surface_page")
        timeline["scenes"][1]["world"]["page"].pop("surface_from")
        timeline["scenes"][1]["world"]["page"]["enter"] = "built"
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        td, server, page, errors, width, height = H._open_player(browser, timeline, synthetic_assets())
        try:
            sample = H._at(page, 6, (width, height), tmp_path / "surface-safe-margins.png")
            chart = H._painted_chart_page(sample)
            # A large font is not readable if its leading digit hits the frame.
            # Use 2% stage inset, below the source/title's existing safe margin.
            inset = sample["stage"]["w"] * .02
            for label in chart["labels"]:
                box = label["rect"]
                assert box["x"] >= inset, label
                assert box["x"] + box["w"] <= sample["stage"]["w"] - inset, label
            assert not errors, errors
        finally:
            page.context.close()
            server.shutdown()
            td.cleanup()
            browser.close()


@H.needs_browser
def test_surface_arrival_growth_and_reverse_seek(tmp_path: Path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        assets = synthetic_assets()
        td, server, page, errors, width, height = H._open_player(browser, surface_timeline(), assets)
        try:
            records = {}
            for t in (3.5, 4, 4.1125, 4.225, 4.3375, 4.45, 5, 4.225, 3.5, 5):
                H._at(page, t, (width, height), tmp_path / f"surface-{t}.png")
                rows = page.evaluate(PROBE)
                assert not errors, errors
                assert rows, (t, rows)
                active = next(r for r in rows if r["world"] == "wB")
                assert len(active["paths"]) == 1
                assert active["stroke"] == "#1769C2"
                assert active["labelFill"] == "rgb(37, 49, 60)"
                assert set(active["labelFills"]) == {"rgb(37, 49, 60)"}
                assert "data:image/svg+xml" in active["worldImage"]
                assert abs(active["rect"][2] / active["rect"][3] / (active["view"][0] / active["view"][1]) - 1) < .01
                if t in records:
                    assert active == records[t]
                records[t] = active
            assert records[3.5]["progress"] == "0"
            assert records[5]["progress"] == "1"
            assert records[5]["background"] == "rgb(244, 230, 199)"
            (tmp_path / "geometry.json").write_text(json.dumps(records, indent=2))
        finally:
            page.context.close()
            server.shutdown()
            td.cleanup()
            browser.close()
