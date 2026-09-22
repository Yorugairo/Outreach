"""Surface handoff retains native chart states, annotations and undistorted type."""
import copy
import json

import pytest
import test_page_surface_player as S


@S.H.needs_browser
def test_surface_rescale_figures_and_isotropic_text_seek(tmp_path):
    from playwright.sync_api import sync_playwright
    timeline = S.surface_timeline()
    scene = timeline["scenes"][1]
    second = copy.deepcopy(scene["world"]["page"])
    second.pop("surface_from")
    second["axes"]["domain"] = [0, 5000]
    scene["world"]["page_states"] = [second]
    scene["species"] = [
        {"kind": "figure", "at": 4.15, "dur": .1, "series": 0,
         "target": {"kind": "datum", "index": 0}, "text": "First observation", "dy": -.5},
        {"kind": "chart_to", "at": 6, "dur": 1, "to": "rescale", "state": 1},
    ]
    probe = """() => {
      const st=document.getElementById('wB').__lp;
      const texts=[...st.page.querySelectorAll('svg.lp-chart text')].map(e=>{
        const m=e.getScreenCTM();
        return {text:e.textContent, ratio:Math.hypot(m.a,m.b)/Math.hypot(m.c,m.d),
          fill:getComputedStyle(e).fill};
      });
      return {active:st.active, states:st.states.length, texts,
        chartPaths:st.states.map(s=>s.paths.map(p=>p.p.getAttribute('d'))),
        opacity:st.states.map(s=>s.chart.style.opacity),
        tickInlineOpacity:st.states.map(s=>s.marks.filter(m=>m.role==='ylabel').map(m=>m.el.style.opacity)),
        figures:window.__lpProbe().figures};
    }"""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        td, server, page, errors, width, height = S.H._open_player(browser, timeline, S.synthetic_assets())
        try:
            records = {}
            for t in (8, 4.3, 5, 6.5, 8, 4.3, 5):
                S.H._at(page, t, (width, height), tmp_path / f"states-{t}.png")
                state = page.evaluate(probe)
                assert not errors, errors
                assert state["states"] == 2
                assert state["texts"]
                assert all(abs(e["ratio"] - 1) < .005 for e in state["texts"]), state["texts"]
                assert len(state["figures"]) == 1
                assert state["figures"][0]["opacity"] == 1
                if t == 8:
                    assert state["active"] == 1
                    assert float(state["opacity"][1]) == 1
                if t == 5:
                    assert state["active"] == 0
                if t == 6.5:
                    # Native axis handover owns individual tick opacity. The
                    # surface reveal must act on its wrapper, not force ticks1.
                    # A held common tick may legitimately remain fully visible.
                    assert any(value != "1" for values in state["tickInlineOpacity"] for value in values), state["tickInlineOpacity"]
                if t in records:
                    assert state == records[t]
                records[t] = state
            assert records[5]["chartPaths"] != records[6.5]["chartPaths"]
            (tmp_path / "state-probe.json").write_text(json.dumps(records, indent=2))
        finally:
            page.context.close()
            server.shutdown()
            td.cleanup()
            browser.close()
