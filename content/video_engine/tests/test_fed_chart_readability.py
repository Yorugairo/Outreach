"""T17 chart readability: closed phone profile, matched SVG geometry, and browser evidence.

The browser lane mutates only an in-memory copy of the existing Fed candidate timeline.  It does
not edit an episode source, opt a candidate in, render a video, or claim production acceptance.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

import ledger_page as LPG  # noqa: E402
import render_baseline as RB  # noqa: E402


FED = ROOT / "content/video_engine/projects/systems-and-blowups/fed-liquidity-pressure"
OBJECTS = FED / "evidence/objects"
TIMELINE = FED / "build-opening-chart-proof-v1/candidate-a/fed-opening-chart-proof.timeline.json"
HISTORY = OBJECTS / "fed-assets-reserves-history.series.json"
RRP = OBJECTS / "fed-on-rrp-history.series.json"


def _source(path: Path) -> dict:
    return LPG.load_series(path)


def _spec(source: dict, *, profile: bool = False, aspect: str = "16:9") -> dict:
    row = copy.deepcopy(source)
    if profile:
        row["readability"] = "landscape-phone"
    else:
        # Production sources opt in now; explicitly construct the legacy control.
        row.pop("readability", None)
    spec = LPG.build_spec(row, "line")
    # `full_stage` is a compiler stamp, deliberately supplied here only to exercise the geometry
    # mirror.  The episode/compiler opt-in remains outside this test's write set.
    if aspect == "16:9":
        spec["full_stage"] = True
    return spec


def test_closed_profile_authoring_and_matched_geometry():
    history = _source(HISTORY)
    phone = copy.deepcopy(history)
    phone["readability"] = "landscape-phone"
    assert LPG.validate(phone, "line") == []
    spec = _spec(history, profile=True)
    legacy = _spec(history)
    assert spec["axes"]["readability"] == "landscape-phone"
    assert "readability" not in legacy["axes"]
    assert spec["series"] == legacy["series"] and spec["axes"].get("domain") == legacy["axes"].get("domain")

    unknown = copy.deepcopy(phone)
    unknown["readability"] = "phone-wide"
    assert any("readability" in error and "landscape-phone" in error for error in LPG.validate(unknown, "line"))

    short = {
        "title": "Short",
        "src": "Source",
        "series": [{"label": "Only", "color": "crimson", "pts": [[0, 1], [1, 2]]}],
        "readability": "landscape-phone",
    }
    assert any("dense-line builder" in error for error in LPG.validate(short, "line"))

    host = copy.deepcopy(phone)
    host["chart_box"] = {"x": 0.1, "y": 0.1, "w": 0.8, "h": 0.6}
    assert any("full_stage" in error for error in LPG.validate(host, "line"))

    old_boxes = LPG.page_boxes(legacy, "16:9")
    repeat_boxes = LPG.page_boxes(_spec(history), "16:9")
    assert old_boxes == repeat_boxes, "an absent profile must remain the legacy geometry"
    phone_boxes = LPG.page_boxes(spec, "16:9")
    assert phone_boxes["chart"]["w"] > old_boxes["chart"]["w"]
    assert phone_boxes["plot"]["w"] > old_boxes["plot"]["w"]
    assert phone_boxes["tags"]["x"] + phone_boxes["tags"]["w"] <= 0.979 * 1920 + 1
    assert phone_boxes["plot"]["y"] + phone_boxes["plot"]["h"] < phone_boxes["caption_anchor"]["y"]
    assert phone_boxes["source"]["y"] >= phone_boxes["caption_anchor"]["y"] + phone_boxes["caption_anchor"]["h"] - 2
    assert phone_boxes["source"]["x"] >= 0 and phone_boxes["source"]["x"] + phone_boxes["source"]["w"] <= 1920

    portrait_phone = _spec(history, profile=True, aspect="9:16")
    portrait_legacy = _spec(history, aspect="9:16")
    assert LPG.page_boxes(portrait_phone, "9:16") == LPG.page_boxes(portrait_legacy, "9:16")
    assert LPG._landscape_profile_geometry(spec, 1920, 1080)["vw"] > LPG.LAND_VIEWBOX[0]
    assert LPG._landscape_profile_geometry(portrait_phone, 1080, 1920) is None


def test_phone_plot_and_tag_boxes_use_native_svg_margins():
    spec = _spec(_source(RRP), profile=True)
    geometry = LPG._landscape_profile_geometry(spec, 1920, 1080)
    boxes = LPG.page_boxes(spec, "16:9")
    scale = geometry["scale"]
    # page_boxes publishes whole pixels; half a pixel is the rounding bound.
    assert boxes["plot"]["x"] == pytest.approx(geometry["x"] + 120 * scale, abs=.5)
    assert boxes["plot"]["w"] == pytest.approx((geometry["vw"] - 120 - 220) * scale, abs=.5)
    assert boxes["tags"]["x"] == pytest.approx(geometry["x"] + (geometry["vw"] - 220 + 12) * scale, abs=.5)


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            pw.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not _chromium_available(), reason="playwright chromium not installed")


def _timeline(mode: str, aspect: str = "16:9") -> dict:
    timeline = json.loads(TIMELINE.read_text(encoding="utf-8"))
    timeline["aspect"] = aspect
    if mode == "profile":
        # This is deliberately a short display copy for the browser proof. It preserves the source
        # family and the date window while keeping the profile's larger outside-SVG type on-board.
        display = [
            ("Jun 2022 to Jun 2025 · cumulative change", "Fed H.4.1 / FRED · Jun 2022–Jun 2025"),
            ("Jan 2022 to Sep 2026 · daily USD billions", "FRED RRPONTSYD · daily USD billions · 2022–2026"),
        ]
        for scene, (sub, source) in zip(timeline["scenes"], display):
            page = scene["world"]["page"]
            page.setdefault("axes", {})["readability"] = "landscape-phone"
            page["sub"], page["source"] = sub, source
            if scene["scene_id"] == "s01":
                page["series"][0]["label"], page["series"][1]["label"] = "Assets", "Reserves"
                page["badges"] = [
                    {"label": "Assets", "value": "Total assets", "tag": "assets", "accent": "coral", "inline": True},
                    {"label": "Reserves", "value": "Bank reserves", "tag": "reserves", "accent": "teal", "inline": True},
                ]
            else:
                page["series"][0]["label"] = "ON RRP"
                page["badges"] = [
                    {"label": "ON RRP", "value": "ON RRP", "tag": "daily", "accent": "cobalt", "inline": True},
                ]
    else:
        for scene in timeline["scenes"]:
            scene["world"]["page"].setdefault("axes", {}).pop("readability", None)
    return timeline


PROBE = """() => {
  const stage = document.getElementById('stage').getBoundingClientRect();
  const box = (e) => { if (!e) return null; const r=e.getBoundingClientRect();
    return {x:r.left-stage.left,y:r.top-stage.top,w:r.width,h:r.height}; };
  const visible = (e) => { if (!e) return false; const c=getComputedStyle(e), r=e.getBoundingClientRect();
    return c.visibility !== 'hidden' && +c.opacity > .05 && r.width > .1 && r.height > .1; };
  const pages = [...document.querySelectorAll('.lp-page')].filter(visible);
  const read = (page) => {
    const chart = page.querySelector('svg.lp-chart'), vb = chart && chart.viewBox.baseVal;
    const cr = chart && chart.getBoundingClientRect(), scale = cr && vb && vb.height ? cr.height/vb.height : 0;
    const ps = page.offsetWidth ? page.getBoundingClientRect().width/page.offsetWidth : 1;
    const type = (e, kind) => { const fs=parseFloat(getComputedStyle(e).fontSize)||0;
      const k=kind === 'svg' ? scale : ps;
      return {text:e.textContent, kind, rect:box(e), css:fs, phone:fs*k*390/stage.width}; };
    const labels = chart ? [...chart.querySelectorAll('text.lab,text.sname')].filter(visible).map(e=>type(e,'svg')) : [];
    const tags = chart ? [...chart.querySelectorAll('tspan.tagchip')].filter(visible).map(e=>type(e,'svg')) : [];
    return {profile: page.classList.contains('lp-readability-landscape-phone'), page:box(page), chart:box(chart),
      viewBox: chart && chart.getAttribute('viewBox'), labels, tags,
      title:type(page.querySelector('.lp-title'),'page'), sub:type(page.querySelector('.lp-sub'),'page'),
      source:type(page.querySelector('.lp-src'),'page')};
  };
  const cap=document.getElementById('caption');
  return {pages:pages.map(read), caption:{visible:visible(cap), box:box(cap), opacity:getComputedStyle(cap).opacity},
          stage:{w:stage.width,h:stage.height}};
}"""


def _open_player(browser, timeline: dict, assets: dict | None = None):
    from tempfile import TemporaryDirectory

    td = TemporaryDirectory()
    html = Path(td.name) / "fed-t17.html"
    html.write_text(RB.instantiate(timeline, assets or {"__audio__": ""}), encoding="utf-8")
    server, port = RB.serve(html.parent)
    width, height = RB.STAGE[timeline["aspect"]]
    page = browser.new_context(viewport={"width": width + 64, "height": height + 64}).new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
    RB.prepare_page(page, width, height)
    return td, server, page, errors, width, height


def _at(page, t: float, size: tuple[int, int], out: Path) -> dict:
    out.write_bytes(RB.frame_png(page, t, size))
    page.wait_for_timeout(80)
    return page.evaluate(PROBE)


def _painted_chart_page(sample: dict) -> dict:
    """Choose the painted endpoint, not an overlapping transition page with no ink."""
    assert sample["pages"], "the chart page must remain painted"
    candidates = [p for p in sample["pages"] if p["labels"] or p["tags"]]
    return max(candidates or sample["pages"], key=lambda p: (len(p["labels"]) + len(p["tags"]), p["chart"]["w"]))


def _assert_profile_page(sample: dict, *, portrait: bool = False, require_tags: bool = True) -> None:
    page = _painted_chart_page(sample)
    assert page["profile"] is not portrait
    if portrait:
        # The closed profile is intentionally ignored outside the full-stage landscape route.
        assert page["viewBox"] != "0 0 1000 560"
        essentials = page["labels"] + page["tags"] + [page["title"], page["sub"], page["source"]]
        assert essentials
        assert all(item["rect"]["x"] >= -2 and item["rect"]["x"] + item["rect"]["w"] <= sample["stage"]["w"] + 2
                   for item in page["labels"] + page["tags"]), page
        return
    else:
        assert float(page["viewBox"].split()[2]) > 1000
        assert page["chart"]["w"] > 1334
        assert page["chart"]["x"] + page["chart"]["w"] < 0.979 * sample["stage"]["w"] + 2
        assert page["source"]["rect"]["y"] >= page["chart"]["y"] + page["chart"]["h"] - 2
    essentials = page["labels"] + page["tags"] + [page["title"], page["sub"], page["source"]]
    assert essentials and min(item["phone"] for item in essentials) >= 12, essentials
    if require_tags:
        assert page["tags"], "the profile proof must include actual inline end tags"
    assert all(item["rect"]["x"] >= -2 and item["rect"]["x"] + item["rect"]["w"] <= sample["stage"]["w"] + 2
               for item in page["labels"] + page["tags"]), page
    if sample["caption"]["visible"]:
        cap = sample["caption"]["box"]
        src = page["source"]["rect"]
        assert src["y"] + src["h"] <= cap["y"] + 2 or src["y"] >= cap["y"] + cap["h"] - 2


@needs_browser
def test_production_sources_render_with_phone_profile(tmp_path: Path):
    from playwright.sync_api import sync_playwright

    timeline = _timeline("legacy")
    for scene, source in zip(timeline["scenes"], (HISTORY, RRP)):
        previous = scene["world"]["page"]
        production = LPG.build_spec(_source(source), "line")
        for key in ("enter", "exit", "full_stage", "caption", "build", "build_s"):
            if key in previous:
                production[key] = previous[key]
        scene["world"]["page"] = production
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        td, server, page, errors, width, height = _open_player(browser, timeline)
        try:
            for t, source in zip((8.5, 17.5), (HISTORY, RRP)):
                sample = _at(page, t, (width, height), tmp_path / f"production-{t}.png")
                # Production has direct series labels, not the diagnostic's added tag badges.
                _assert_profile_page(sample, require_tags=False)
                expected = {tick[1] for tick in _source(source)["xticks"]}
                labels = sorted((label for label in _painted_chart_page(sample)["labels"]
                                 if label["text"] in expected), key=lambda label: label["rect"]["x"])
                assert {label["text"] for label in labels} == expected
                for left, right in zip(labels, labels[1:]):
                    assert left["rect"]["x"] + left["rect"]["w"] + 8 <= right["rect"]["x"]
                # A label-size check alone missed a zero-floor clipping every negative datum.
                path_bounds = page.evaluate("""() => [...document.querySelectorAll('svg.lp-chart')]
                    .filter(svg => svg.getBoundingClientRect().width > 0)
                    .flatMap(svg => [...svg.querySelectorAll('path.ser')].map(path => {
                        const b=path.getBBox(), v=svg.viewBox.baseVal;
                        return {y:b.y, bottom:b.y+b.height, height:v.height};
                    }))""")
                assert path_bounds
                assert all(p["y"] >= 0 and p["bottom"] <= p["height"] for p in path_bounds)
            assert not errors, errors
        finally:
            page.context.close()
            server.shutdown()
            td.cleanup()
            browser.close()


@needs_browser
def test_browser_profile_legacy_portrait_and_melt_frames(tmp_path: Path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            records = {}
            for mode, aspect in (("profile", "16:9"), ("legacy", "16:9"), ("profile", "9:16")):
                td, server, page, errors, width, height = _open_player(browser, _timeline(mode, aspect))
                try:
                    first = _at(page, 8.5, (width, height), tmp_path / f"fed-t17-{mode}-{aspect.replace(':', '-')}-first.png")
                    second = _at(page, 17.5, (width, height), tmp_path / f"fed-t17-{mode}-{aspect.replace(':', '-')}-second.png")
                    records[(mode, aspect)] = (first, second)
                    assert not errors, errors
                    if mode == "profile" and aspect == "16:9":
                        _assert_profile_page(first)
                        _assert_profile_page(second)
                        first_page = _painted_chart_page(first)
                        second_page = _painted_chart_page(second)
                        assert second_page["tags"], "the second Fed line source's inline tag must be measured"
                        assert first_page["viewBox"] != second_page["viewBox"], "per-source labels/tags must drive matched viewBox geometry"
                        seam = _at(page, 9.43, (width, height), tmp_path / "fed-t17-profile-16-9-melt.png")
                        assert seam["pages"], "melt seam must not blank the chart"
                        assert all(float(p["viewBox"].split()[2]) > 1000 for p in seam["pages"])
                    elif mode == "legacy":
                        legacy_page = _painted_chart_page(first)
                        assert not legacy_page["profile"] and legacy_page["viewBox"] == "0 0 1000 560"
                        assert legacy_page["chart"]["w"] < _painted_chart_page(records[("profile", "16:9")][0])["chart"]["w"]
                    else:
                        _assert_profile_page(first, portrait=True)
                        _assert_profile_page(second, portrait=True)
                finally:
                    page.context.close()
                    server.shutdown()
                    td.cleanup()
        finally:
            browser.close()
    # Keep the proof honest: the test generated real PNG bytes, not a DOM-only assertion.
    frames = sorted(tmp_path.glob("fed-t17-*.png"))
    assert len(frames) >= 7
    assert all(p.stat().st_size > 10000 and len(hashlib.sha256(p.read_bytes()).hexdigest()) == 64 for p in frames)
