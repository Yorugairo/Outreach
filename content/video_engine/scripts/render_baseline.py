"""Render one frame of the scene-evidence player from a committed source (P39).

The same mechanism `render_episode.py` ships with - headless Chromium seeks `#scrub` to t
and screenshots `#stage` - reduced to a single frame from a self-contained player, so a
regression can be caught by pixels without an episode build or the :8731 server.

    python render_baseline.py --list
    python render_baseline.py --surface chart-callout --out frame.png      # one frame at its judged t
    python render_baseline.py --update                                      # rewrite every golden frame
    python render_baseline.py --check                                       # compare, write diffs, exit 1 on any change

Golden frames live in content/video_engine/tests/golden/frames/; their sources in
.../golden/sources/ (written by build_golden_sources.py). Frames are captured at device
scale 1 (1920x1080 or 1080x1920) - the check is exact, so resolution only costs bytes.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import io
import json
import sys
import tempfile
import threading
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
GOLDEN = REPO / "content/video_engine/tests/golden"
SOURCES = GOLDEN / "sources"
FRAMES = GOLDEN / "frames"
DIFFS = GOLDEN / "diffs"
STAGE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}


def instantiate(timeline: dict, uris: dict, template: Path = TEMPLATE) -> str:
    """The build step's exact substitution (build_scene_timeline_f.py) on the reviewed template."""
    html = template.read_text(encoding="utf-8")
    if "{{TIMELINE}}" not in html or "{{URIS}}" not in html:
        raise RuntimeError(f"{template} is not the template - it has no {{{{TIMELINE}}}}/{{{{URIS}}}} slots")
    return (html.replace("{{TIMELINE}}", json.dumps(timeline, separators=(",", ":")))
                .replace("{{URIS}}", json.dumps(uris, separators=(",", ":"))))


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):  # noqa: D401 - silence per-request logging
        pass


def serve(directory: Path):
    handler = functools.partial(_Quiet, directory=str(directory))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def frame_png(page, t: float, size: tuple[int, int]) -> bytes:
    page.evaluate(
        "t => { const s = document.getElementById('scrub');"
        " s.value = t; s.dispatchEvent(new Event('input', {bubbles:true})); }", t)
    # a CLIP world seeks a <video> to the scene clock; the frame is not a function of t until
    # the seek has landed (the template resolves __clipsSeeked once every pending seek fires)
    page.evaluate("() => window.__clipsSeeked ? window.__clipsSeeked() : null")
    # a clipped page shot at the stage's exact rectangle: an element screenshot inherits the
    # container's fractional offset and comes back a pixel wide (1081x1920 on 9:16)
    r = page.evaluate("(() => { const b = document.getElementById('stage').getBoundingClientRect(); return [b.x, b.y]; })()")
    return page.screenshot(type="png", clip={"x": round(r[0]), "y": round(r[1]), "width": size[0], "height": size[1]})


def prepare_page(page, w: int, h: int) -> None:
    """Make the loaded player a pure function of t, at the stage's native size.

    The four wall-clock / geometry dependencies P39 T2 found, neutralised in one place so
    the golden harness and the shipped renderer capture identically:
      - CSS transitions (.dock opacity .75s, pills .34s, captions .12s) run on the WALL CLOCK,
        so a seek-and-screenshot can land mid-transition (caught: run 2 of 3 differed on 9:16)
      - fitStage() scales #stage to the #fit container (~0.73x at 1920x1080), so an element
        screenshot is a downscaled stage that render_episode used to LANCZOS-upscale
      - document.fonts.ready.then(()=>1) is not awaited by page.evaluate; the bare promise is
      - an element screenshot inherits the container's fractional offset (1081x1920)
    """
    page.wait_for_selector("#stage", timeout=60000)
    page.evaluate("document.fonts.ready")
    page.evaluate("document.getElementById('vo').muted = true")
    page.evaluate("for (const id of ['sndbar']) { const e=document.getElementById(id); if (e) e.style.display='none'; }")
    page.add_style_tag(content=(
        "*, *::before, *::after { transition: none !important; animation: none !important; }"
        f" #shell {{ width: auto !important; max-width: none !important; }}"
        f" #fit {{ width: {w}px !important; height: {h}px !important; max-width: none !important; overflow: visible !important; }}"
        " #stage { transform: none !important; }"))
    page.set_viewport_size({"width": w + 64, "height": h + 64})
    page.wait_for_function("document.fonts.status === 'loaded'")
    page.wait_for_timeout(250)


def render_frame(html_path: Path, t: float, aspect: str = "16:9", device_scale_factor: float = 1.0) -> bytes:
    """One PNG of #stage at time t, from a fresh browser, served over a throwaway local server."""
    from playwright.sync_api import sync_playwright
    w, h = STAGE[aspect]
    srv, port = serve(html_path.parent)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=device_scale_factor).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html_path.name}", wait_until="networkidle", timeout=120000)
            prepare_page(page, w, h)
            png = frame_png(page, t, (w, h))
            size = rgb_bytes(png)[0]
            expect = (round(w * device_scale_factor), round(h * device_scale_factor))
            if size != expect:
                raise RuntimeError(f"stage captured at {size}, expected {expect} - fitStage is still scaling")
            browser.close()
    finally:
        srv.shutdown()
    return png


def rgb_bytes(png: bytes) -> tuple[tuple[int, int], bytes]:
    from PIL import Image
    im = Image.open(io.BytesIO(png)).convert("RGB")
    return im.size, im.tobytes()


def load_surface(name: str) -> tuple[dict, dict, float, str]:
    sys.path.insert(0, str(GOLDEN))
    from build_golden_sources import FRAME_T  # noqa: E402
    tl = json.loads((SOURCES / f"{name}.timeline.json").read_text(encoding="utf-8"))
    uris = json.loads((SOURCES / f"{name}.uris.json").read_text(encoding="utf-8"))
    return tl, uris, FRAME_T[name], str(tl.get("aspect") or "16:9")


def render_surface(name: str, t: float | None = None, template: Path = TEMPLATE) -> bytes:
    tl, uris, t_default, aspect = load_surface(name)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{name}.html"
        html.write_text(instantiate(tl, uris, template), encoding="utf-8")
        return render_frame(html, t if t is not None else t_default, aspect)


def write_diff(name: str, golden_png: bytes, actual_png: bytes) -> Path:
    """golden | actual | amplified difference, side by side - legible without reading code."""
    from PIL import Image, ImageChops, ImageDraw
    g = Image.open(io.BytesIO(golden_png)).convert("RGB")
    a = Image.open(io.BytesIO(actual_png)).convert("RGB")
    if a.size != g.size:
        a = a.resize(g.size)
    d = ImageChops.difference(g, a).point(lambda v: min(255, v * 8))
    w, h = g.size
    out = Image.new("RGB", (w * 3, h + 40), (8, 12, 16))
    for i, (im, label) in enumerate(((g, "GOLDEN"), (a, "ACTUAL"), (d, "DIFF x8"))):
        out.paste(im, (i * w, 40))
        ImageDraw.Draw(out).text((i * w + 12, 12), f"{label}  {name}", fill=(244, 230, 199))
    DIFFS.mkdir(parents=True, exist_ok=True)
    p = DIFFS / f"{name}.diff.png"
    out.save(p, "PNG")
    return p


def check(names: list[str]) -> list[str]:
    """Return one line per changed frame (empty = all identical)."""
    failures = []
    for name in names:
        golden = FRAMES / f"{name}.png"
        if not golden.exists():
            failures.append(f"{name}: no golden frame at {golden} (run --update)")
            continue
        actual = render_surface(name)
        if rgb_bytes(golden.read_bytes())[1] != rgb_bytes(actual)[1]:
            diff = write_diff(name, golden.read_bytes(), actual)
            failures.append(f"{name}: pixels changed - see {diff.relative_to(REPO)}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--surface")
    ap.add_argument("--t", type=float)
    ap.add_argument("--out")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    names = sorted(p.name[: -len(".timeline.json")] for p in SOURCES.glob("*.timeline.json"))
    if args.list:
        print("\n".join(names)); return 0
    if args.surface:
        png = render_surface(args.surface, args.t)
        Path(args.out or f"{args.surface}.png").write_bytes(png)
        print(args.out or f"{args.surface}.png"); return 0
    if args.update:
        FRAMES.mkdir(parents=True, exist_ok=True)
        for name in names:
            (FRAMES / f"{name}.png").write_bytes(render_surface(name)); print("golden", name)
        return 0
    if args.check:
        failures = check(names)
        print("\n".join(failures) if failures else f"PASS {len(names)} golden frames identical")
        return 1 if failures else 0
    ap.print_help(); return 2


if __name__ == "__main__":
    raise SystemExit(main())
