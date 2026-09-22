"""Native-player T20 diagnostic: sourced icons, formula and reversible edges."""
import copy
import base64
from pathlib import Path

import pytest
import test_fed_chart_readability as H
import build_scene_timeline_f as B


def proof(mode):
    timeline = H._timeline("legacy")
    scene = copy.deepcopy(timeline["scenes"][0])
    sp = {"kind": "flow", "at": 1., "dur": 9., "readability": "landscape-phone",
          "target": {"kind": "region", "x0": .06, "y0": .23, "x1": .94, "y1": .78},
          "nodes": [{"id": "a", "icon": "landmark", "label": "FED\nASSETS"},
                    {"id": "b", "icon": "coins", "label": "GOVERNMENT\nCASH"},
                    {"id": "c", "icon": "coins", "label": "OVERNIGHT\nCASH"}],
          "edges": [["a", "b"], ["b", "c"]]}
    if mode == "formula":
        sp.update(operators=["-", "-"], tag="ANALYST PROXY · NOT BANK RESERVES")
    else:
        sp.update(edge_states=[{"at": 6., "edges": [["b", "a"]]}], tag="ILLUSTRATION · OTHER BALANCES FIXED")
        sp["nodes"][0]["label"] = "BANK\nRESERVES"
        sp["nodes"][1]["label"] = "GOVERNMENT\nACCOUNT"
        sp["nodes"][2]["label"] = "CUSTOMER\nDEPOSIT"
        sp["edges"] = [["a", "b"]]
    assert not B.validate_species([sp], (0, 0, 0), "synthetic-hall")
    scene.update(scene_id="flow-proof", span=[0, 11], species=[sp],
                 build_windows=[], build_lines=[], docks=[], exit="cut")
    scene["world"] = {"asset_id": "synthetic-hall", "kind": "image", "idle": "none",
                      "ken_burns": {"scale": 0, "x": 0, "y": 0}}
    timeline["scenes"] = [scene]
    cream = '<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="#F4E6C7"/></svg>'
    assets = {"__audio__": "", "synthetic-hall": "data:image/svg+xml;base64," + base64.b64encode(cream.encode()).decode()}
    for node in sp["nodes"]:
        assets["icon:" + node["icon"]] = B.icon_geometry(node["icon"])
    return timeline, assets


PROBE = """() => {
 const root=document.querySelector('g.flow');
 const stage=document.getElementById('stage').getBoundingClientRect();
 if (!root) return null;
 return {html:root.outerHTML,
  arrows:[...root.querySelectorAll('.flowarrow')].map(e=>e.getAttribute('d')),
  operators:root.querySelectorAll('.flowoperator').length,
  strokes:[...root.querySelectorAll('.flowarrow,.flowoperator,.chipglyph')].map(e=>getComputedStyle(e).stroke),
  labels:[...root.querySelectorAll('text')].map(e=>{
   const r=e.getBoundingClientRect(),m=e.getScreenCTM();
   return {text:e.textContent,x:r.x-stage.x,y:r.y-stage.y,w:r.width,h:r.height,
    phone:parseFloat(getComputedStyle(e).fontSize)*Math.hypot(m.a,m.b)*390/stage.width};
  })};
}"""


@H.needs_browser
@pytest.mark.parametrize("mode", ["formula", "accounts"])
def test_native_flow_phone_and_cold_reverse_seek(tmp_path: Path, mode):
    from playwright.sync_api import sync_playwright
    timeline, assets = proof(mode)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        td, server, page, errors, width, height = H._open_player(browser, timeline, assets)
        try:
            samples = {}
            for at in (8., 5., 6.15, 6.5, 8., 5.):
                H._at(page, at, (width, height), tmp_path / f"{mode}-{at}.png")
                state = page.evaluate(PROBE)
                assert state and not errors, errors
                if at in samples:
                    assert state == samples[at]
                samples[at] = state
            final = samples[8.]
            if mode == "formula":
                assert not final["arrows"]
                assert final["operators"] == 2
            else:
                assert final["arrows"] and final["arrows"] != samples[5.]["arrows"]
            assert final["labels"]
            assert final["labels"] == samples[5.]["labels"], "changing arrows must not move standing nodes"
            assert final["strokes"] and all(color == "rgb(37, 49, 60)" for color in final["strokes"])
            for label in final["labels"]:
                assert label["phone"] >= 9, label
                assert label["x"] >= 0 and label["x"] + label["w"] <= width, label
                assert label["y"] >= 0 and label["y"] + label["h"] <= height, label
        finally:
            page.context.close()
            server.shutdown()
            td.cleanup()
            browser.close()
