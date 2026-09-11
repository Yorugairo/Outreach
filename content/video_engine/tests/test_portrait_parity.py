"""PORTRAIT PARITY (operator, 2026-09-08: "how do we make sure that anything that is hard-coded to landscape is actually
responsive to mobile?"). Two gates:

1. A LINT on the player template: no landscape literal (1920 / 1080 / 960 / 540) in code outside the stage constants and
   an explicit allowlist (the two SVG viewBox defaults, which start-up re-fits to the stage; comment lines). The under
   species layer shipped with the landscape viewBox and put a portrait spotlight at the axis corner; the camera zoomed a
   portrait short about 960/540. Both were literals this lint would have refused.
2. A RUNTIME check: a golden surface rendered at 9:16 - every <svg> under #stage carries the stage's viewBox, and every
   full-stage layer's box equals the stage's box. A layer that is not re-fitted is exactly the bug class of the night.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "docs/content-video-engine/samples/scene-evidence-player.template.html"
ENGINE = ROOT / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
PLAYER = (TEMPLATE, ENGINE)   # P51 T1: the player is a shell and an engine - the lint reads BOTH
sys.path.insert(0, str(ROOT / "content/video_engine/scripts"))

LITERAL = re.compile(r"(?<![\w.])(1920|1080|960|540)(?![\w.])")
ALLOW = (
    'viewBox="0 0 1920 1080"',          # the two species SVG defaults - re-fitted to the stage at start-up (template: $("species").setAttribute("viewBox", ...))
    "STAGE_W", "STAGE_H",               # the constants themselves and any line that already speaks in them
    "PORTRAIT ?",                       # an explicit portrait branch
)


def _code_lines(path: Path = TEMPLATE):
    """One file's lines with comments removed - block comments (/* ... */ across lines), line comments, HTML comments."""
    in_block = False
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        code, i = "", 0
        while i < len(line):
            if in_block:
                j = line.find("*/", i)
                if j < 0:
                    i = len(line); break
                in_block, i = False, j + 2
            else:
                j = line.find("/*", i)
                k = line.find("//", i)
                if k >= 0 and (j < 0 or k < j) and "http" not in line[max(0, k - 6):k]:
                    code += line[i:k]; i = len(line); break
                if j < 0:
                    code += line[i:]; i = len(line); break
                code += line[i:j]; in_block, i = True, j + 2
        if code.strip().startswith("<!--"):
            continue
        yield n, code, line


def test_no_landscape_literal_in_player_code():
    offenders = []
    for path in PLAYER:
        for n, code, line in _code_lines(path):
            if LITERAL.search(code) and not any(a in line for a in ALLOW):
                offenders.append(f"{path.name}:{n}: {line.strip()[:110]}")
    assert not offenders, "landscape literals in player code (use STAGE_W / STAGE_H, or allowlist with a reason):\n" + "\n".join(offenders)


def test_every_layer_is_fitted_to_the_portrait_stage():
    import tempfile
    import render_baseline as RB
    from playwright.sync_api import sync_playwright

    tl, uris, _t, _a = RB.load_surface("chart-callout")
    timeline = dict(tl, aspect="9:16")
    w, h = RB.STAGE["9:16"]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "p.html"
        html.write_text(RB.instantiate(timeline, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                pg = br.new_context(viewport={"width": w, "height": h}).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(pg, w, h)
                report = pg.evaluate("""() => {
                  const stage = document.getElementById('stage').getBoundingClientRect();
                  const same = (r) => Math.abs(r.width - stage.width) < 2 && Math.abs(r.height - stage.height) < 2;
                  const svgs = [...document.querySelectorAll('#stage > svg')].map(s => ({id: s.id, viewBox: s.getAttribute('viewBox')}));
                  const over = (r) => Math.abs(r.width - stage.width * 1.10) < 3 && Math.abs(r.height - stage.height * 1.10) < 3
                    && Math.abs((r.x + r.width / 2) - (stage.x + stage.width / 2)) < 3 && Math.abs((r.y + r.height / 2) - (stage.y + stage.height / 2)) < 3;
                  const layers = [...document.querySelectorAll('#stage > *')].filter(e => getComputedStyle(e).position === 'absolute' && e.id)
                    .map(e => ({id: e.id, fitted: same(e.getBoundingClientRect()), overscan: over(e.getBoundingClientRect()), display: getComputedStyle(e).display}));
                  return {stage: [Math.round(stage.width), Math.round(stage.height)], svgs, layers};
                }""")
                br.close()
        finally:
            srv.shutdown()
    bad_svg = [s for s in report["svgs"] if s["viewBox"] != f"0 0 {w} {h}"]
    assert not bad_svg, f"SVG layers not fitted to the {w}x{h} stage: {bad_svg}"
    # measured 2026-09-08: the WORLDS are 1.10x the stage, centred (the Ken Burns overscan) - by design, in both aspects;
    # the caption is a strip; every veil and species layer IS the stage
    FULL = {"wash", "spot", "plife", "species", "species-under", "bzveil", "dipveil"}
    unfitted = [l for l in report["layers"] if l["id"] in FULL and l["display"] != "none" and not l["fitted"]]
    assert not unfitted, f"full-stage layers whose box is not the stage's: {unfitted}"
    worlds = [l for l in report["layers"] if l["id"] in ("wA", "wB")]
    assert worlds and all(l["overscan"] for l in worlds), f"the worlds are not the stage x 1.10 centred: {worlds}"


def test_the_vector_map_fits_the_portrait_stage():
    """P50 T5: the map's own fit, measured in the browser at 9:16 - the land the composition FRAMES is inside
    the stage with its margin, and the species over it sit on the land, not beside it (the world is a div
    carrying the camera's CSS and the species layer is an svg that is not: vmGroupXf is what keeps them
    together). The `vecmap-arc` golden is authored portrait, so this is its own aspect."""
    import tempfile
    import render_baseline as RB
    from playwright.sync_api import sync_playwright

    tl, uris, t, aspect = RB.load_surface("vecmap-arc")
    assert aspect == "9:16", "the vector map's golden is the portrait one"
    w, h = RB.STAGE[aspect]
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / "p.html"
        html.write_text(RB.instantiate(tl, uris), encoding="utf-8")
        srv, port = RB.serve(html.parent)
        try:
            with sync_playwright() as pw:
                br = pw.chromium.launch(headless=True)
                pg = br.new_context(viewport={"width": w, "height": h}).new_page()
                pg.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=120000)
                RB.prepare_page(pg, w, h)
                pg.evaluate("t => { const s = document.getElementById('scrub');"
                            " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
                report = pg.evaluate("""() => {
                  const stage = document.getElementById('stage').getBoundingClientRect();
                  const box = (sel) => { const e = document.querySelector(sel); if (!e) return null;
                    const r = e.getBoundingClientRect();
                    return {x: r.x - stage.x, y: r.y - stage.y, w: r.width, h: r.height}; };
                  return {stage: [stage.width, stage.height], focus: box('.world svg.vm .vmfocus'),
                          lit: [...document.querySelectorAll('#species .vmlit')].length,
                          arc: box('#species .vmarc'), litBox: box('#species .vmlit')};
                }""")
                br.close()
        finally:
            srv.shutdown()
    W, H = report["stage"]
    assert report["focus"], "no framed country on the map"
    f = report["focus"]
    assert f["x"] >= 0 and f["y"] >= 0 and f["x"] + f["w"] <= W + 1 and f["y"] + f["h"] <= H + 1, \
        f"a framed country is outside the {W}x{H} stage: {f}"
    assert report["lit"], "no country is lit at the golden's t"
    lit = report["litBox"]
    assert lit["x"] >= 0 and lit["x"] + lit["w"] <= W + 1, f"a light is off the portrait stage: {lit}"
    a = report["arc"]
    assert a and a["w"] > W * 0.3, f"the arc does not cross the portrait frame: {a}"
