"""P47 T3 - THE MORPH: the object becomes the chart (43 s43.5 method B, ARAP; E48 s4: the tab as the protagonist).

The math is in tests/kinetics/arap.test.mjs (node: det J(t) > 0 through 150 degrees where the vertex lerp collapses).
Here: the compiler's grammar (`:morph[=<s>]` enter, `;morph=<shape>`), the gate (the morph's events, the build's landing,
M17's states), the template's wiring behind `kinetics.arap_morph`, and the browser proof on the soak golden: the prop
outline exists mid-morph, ends on the area under the line, and the three match-cut invariants hold by construction.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import build_scene_timeline_f as B  # noqa: E402
import gate_motion_density as G  # noqa: E402
import measure_morph as MM  # noqa: E402
import render_baseline as RB  # noqa: E402

TEMPLATE = RB.TEMPLATE
MORPH_S = 2.0


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


# ---- the compiler ----------------------------------------------------------------------------


def test_the_ledger_id_takes_a_morph_enter_with_its_seconds():
    assert "morph" in B.LEDGER_ENTERS
    parts = B.parse_ledger_id("ledger:ev-x:line:5:right:morph=2.5:cut")
    assert parts[4] == "morph=2.5" and parts[5] == "cut"
    with pytest.raises(ValueError, match="enter 'fade' is not one of"):
        B.parse_ledger_id("ledger:ev-x:line:5:right:fade")


def test_the_plate_option_names_the_prop_outline():
    assert B.split_plate_opts("ledger:ev-x:line:5:right:morph;morph=plate") == ("ledger:ev-x:line:5:right:morph", {"morph": "plate"})
    with pytest.raises(ValueError, match="morph 'receipt' is not one of"):
        B.split_plate_opts("ledger:ev-x:line;morph=receipt")
    assert B.MORPH_SHAPES == ("tab", "plate", "card")
    assert B.build_kinetics()["arap_morph"] is True


# ---- the gate --------------------------------------------------------------------------------


def _morph_scene(morph_s=MORPH_S):
    return {"scene_id": "s02", "span": [2.0, 30.0], "world": {"kind": "ledger", "page": {"enter": "morph", "morph_s": morph_s, "title": "t", "series": [{"pts": [[0, 1], [1, 2]]}]}}}


def test_a_morph_page_lands_its_build_after_the_morph_and_its_window_is_continuous_motion():
    sc = _morph_scene()
    assert abs(G._page_land_offset(sc) - (MORPH_S + G.LP_BUILD_S)) < 1e-9
    beats, starts = G._page_events([sc])
    assert starts == [2.0]
    for t in (2.0, 2.5, 3.0, 3.5, 4.0, 4.0 + G.LP_BUILD_S):
        assert t in beats, (t, beats)


def test_m17_is_absent_without_a_morph_info_until_measured_stale_on_a_rebuild_and_names_the_failing_invariant(tmp_path: Path):
    plain = {"scene_id": "s01", "span": [0.0, 10.0], "world": {"kind": "ledger", "page": {"title": "t"}}}
    assert G._morph_gate([plain], None) is None
    info = G._morph_gate([_morph_scene()], None)
    assert info.level == "INFO" and "measure_morph.py" in info.message
    assert G._morph_gate([_morph_scene()], "stale").level == "INFO"
    good = {"scenes": {"s02": {"centroid_shift": 0.01, "centroid_ok": True, "axis_deg": 3.0, "axis_ok": True, "area_ratio": 0.8, "area_ok": True, "min_det": 0.4}}}
    assert G._morph_gate([_morph_scene()], good).level == "PASS"
    bad = {"scenes": {"s02": {"centroid_shift": 0.2, "centroid_ok": False, "axis_deg": 40.0, "axis_ok": False, "area_ratio": 0.8, "area_ok": True, "min_det": 0.4}}}
    w = G._morph_gate([_morph_scene()], bad)
    assert w.level == "WARN" and "FAILS centroid, axis" in w.message
    (tmp_path / "player.html").write_text("<html>x</html>", encoding="utf-8")
    (tmp_path / G.MORPH_INVARIANTS_NAME).write_text(json.dumps({"html_sha256": "0" * 64, "scenes": {}}), encoding="utf-8")
    assert G.load_morph_invariants(tmp_path) == "stale"


# ---- the template ----------------------------------------------------------------------------


def test_the_morph_hangs_off_the_existing_arap_flag_and_falls_back_to_a_mount():
    html = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(r"const KINETICS_DEFAULTS = Object\.freeze\(\{(.*?)\}\);", html, re.S)
    assert m and re.search(r"\barap_morph:\s*false", m.group(1))
    assert "/* KINETICS:BEGIN arap */" in html and "const paintMorph = " in html
    assert 'const morphOn = pg.enter === "morph" && kin("arap_morph")' in html
    assert '(pg.enter === "morph" && !morphOn)' in html, "with the flag off a morph page is a mount of the same length"
    assert "window.__morphInvariants = () =>" in html


# ---- the browser -----------------------------------------------------------------------------


def _morph_build(shape: str = "tab") -> tuple[dict, dict, str]:
    tl, uris, _t, aspect = RB.load_surface("ledger-soak-page")
    sc = tl["scenes"][0]
    page = dict(sc["world"]["page"], enter="morph", morph_s=MORPH_S)
    world = dict(sc["world"], page=page, morph=shape, ken_burns={"scale": 0, "x": 0, "y": 0})
    tl2 = dict(tl, caption_pages=[], captions=[], scenes=[dict(sc, world=world)], kinetics={"arap_morph": True, "min_jerk": True})
    return tl2, uris, aspect


@needs_browser
def test_the_tab_becomes_the_area_under_the_line_and_the_invariants_hold():
    from playwright.sync_api import sync_playwright
    tl, uris, aspect = _morph_build("tab")
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "morph.html"
        html.write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_context(viewport={"width": w, "height": h}).new_page()
                page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(page, w, h)
                seek = "t => { const s = document.getElementById('scrub'); s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }"
                page.evaluate(seek, MORPH_S / 2)
                mid = page.evaluate("() => window.__lpProbe().morph")
                assert mid and abs(mid["u"] - 0.5) < 1e-6 and mid["on"] == "1" and mid["bbox"][2] > 50, mid
                inv = page.evaluate("() => window.__morphInvariants()")
                assert inv and inv["centroid_ok"] and inv["axis_ok"] and inv["area_ok"], inv
                assert inv["min_det"] > 0 and inv["end_error"] < 1e-3, inv
                assert inv["n"] == 96
                page.evaluate(seek, MORPH_S + 0.05)
                end = page.evaluate("() => window.__lpProbe().morph")
                assert end["u"] >= 1 and end["on"] == "1", "the area fill holds as the line starts to draw"
                page.evaluate(seek, MORPH_S + G.LP_BUILD_S + 1.0)
                gone = page.evaluate("() => window.__lpProbe().morph")
                assert gone["on"] == "0" and gone["fill"] == 0, "the fill has left once the line is drawn"
                # the tab's outline is the ledger line's area at the end: every vertex of the morph's target lies on the line or the axis
                pts = page.evaluate("() => { const st = [document.getElementById('wA'), document.getElementById('wB')].find(e => e.__lp && e.__lp.morph).__lp; return { B: st.morph.B, line: st.linePts[0], axisB: st.axisB }; }")
                line, axisB = pts["line"], pts["axisB"]
                def dist_to_line(p):
                    best = abs(p[1] - axisB)
                    for a, b in zip(line, line[1:]):
                        dx, dy = b[0] - a[0], b[1] - a[1]; L2 = dx * dx + dy * dy or 1e-9
                        u = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
                        best = min(best, ((p[0] - a[0] - u * dx) ** 2 + (p[1] - a[1] - u * dy) ** 2) ** 0.5)
                    return best
                worst = max(dist_to_line(p) for p in pts["B"])
                assert worst < 1.0, f"the target outline sits on the series or the axis (worst {worst:.2f} units)"
                browser.close()
        finally:
            srv.shutdown()


@needs_browser
def test_measure_morph_writes_the_invariants_beside_the_timeline_and_the_gate_reads_them(tmp_path: Path):
    tl, uris, aspect = _morph_build("plate")
    (tmp_path / "x.timeline.json").write_text(json.dumps(tl), encoding="utf-8")
    (tmp_path / "player.html").write_text(RB.instantiate(tl, uris, TEMPLATE), encoding="utf-8")
    (tmp_path / "motion-plan.json").write_text("{}", encoding="utf-8")
    out, res = MM.measure(tmp_path, "x.timeline.json")
    assert out.exists() and "s01" in res and res["s01"]["centroid_ok"], res
    rep, n_fail = G.write_report(tmp_path, "x.timeline.json")
    text = rep.read_text(encoding="utf-8")
    assert "M17" in text and "[PASS ] M17" in text, text


@needs_browser
def test_with_the_flag_off_a_morph_page_renders_as_a_mount_of_the_same_length():
    tl, uris, aspect = _morph_build("tab")
    off = dict(tl, kinetics={"min_jerk": True})
    sc = tl["scenes"][0]
    mount = dict(tl, kinetics={"min_jerk": True}, scenes=[dict(sc, world=dict(sc["world"], page=dict(sc["world"]["page"], enter="mount", mount_s=MORPH_S)))])
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "off.html", Path(td) / "mount.html"
        a.write_text(RB.instantiate(off, uris, TEMPLATE), encoding="utf-8")
        b.write_text(RB.instantiate(mount, uris, TEMPLATE), encoding="utf-8")
        fa = RB.rgb_bytes(RB.render_frame(a, 5.0, aspect))[1]
        fb = RB.rgb_bytes(RB.render_frame(b, 5.0, aspect))[1]
    assert fa == fb, "the fallback is byte-identical to the mount"
