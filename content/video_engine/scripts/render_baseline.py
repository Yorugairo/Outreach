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
import hashlib
import http.server
import io
import json
import shutil
import sys
import tempfile
import threading
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEMPLATE = REPO / "docs/content-video-engine/samples/scene-evidence-player.template.html"
ENGINE = REPO / "docs/content-video-engine/samples/scene-evidence-engine.mjs"
ASSETS_NAME = "assets.json"        # the split form's fetched asset map
MANIFEST_NAME = "player.json"      # names the engine a served build is running, and its sha
GOLDEN = REPO / "content/video_engine/tests/golden"
SOURCES = GOLDEN / "sources"
FRAMES = GOLDEN / "frames"
DIFFS = GOLDEN / "diffs"
STAGE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}
# P43 T6: one golden per capability with its flag ON, at a t where the change is on screen. Each is checked like the
# base frames; test_kinetics_flags proves each differs from the flag-off render at the same t (a flag golden that
# matched the base would prove nothing). The squash frame has its spring-only twin so the squash is what differs.
FLAG_FRAMES = {
    "chart-callout@curvature_stroke": ("chart-callout", {"curvature_stroke": True}, 10.3),
    "ledger-page-mid-build@curvature_stroke": ("ledger-page-mid-build", {"curvature_stroke": True}, 5.6),
    "ledger-soak-page@km_ink": ("ledger-soak-page", {"km_ink": True}, 2.7),
    "ledger-soak-page@analytic_spring": ("ledger-soak-page", {"analytic_spring": True}, 7.86),
    "ledger-soak-page@area_squash": ("ledger-soak-page", {"analytic_spring": True, "area_squash": True}, 7.86),
    "ledger-soak-page@idle": ("ledger-soak-page", {"idle": True}, 11.0),   # the page holding after its build: the breath is the only difference (E49)
}


# P51 T1 - THE TWO FORMS OF ONE PAGE. The engine is a module on disk (scene-evidence-engine.mjs);
# the template is a shell (style + DOM + the two data slots + {{ENGINE}}). One engine text serves both:
#   SINGLE  the engine inlined as a classic script, the data inlined in the slots - the goldens, every
#           test that instantiates a surface, and every player.html committed before the split;
#   SPLIT   the engine imported as a module beside the page, the data fetched from the slots' data-src -
#           what a build writes, so a build dir holds a ~45 KB page instead of a 32 MB one.
# The boot line is identical in both, and __mounted is what a renderer waits on (prepare_page).
BOOT = "window.__mounted = false; mount().then(() => { window.__mounted = true; });"


def engine_script(engine: Path = ENGINE) -> str:
    """The engine as ONE inline classic script: its module syntax stripped by the same code that
    inlines the kinetics modules into it, so there is exactly one stripper in the repo."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import sync_kinetics as SK  # noqa: E402 - a sibling script, not a package
    return "<script>\n" + SK.inline_text(engine.read_text(encoding="utf-8"), "") + "\n" + BOOT + "\n</script>"


# P51 T4 - THE WATCH CLIENT. It rides in the SPLIT form only (a golden's single-file page is the
# text it always was) and does nothing at all unless ?watch=1 is on the URL - so a served build
# without the flag is exactly today's page. With the flag it long-polls the review server's
# /reload, which holds the request until the build's generation moves, and hands the new timeline
# to the engine's reload(): no page load, the scrub position kept. The server's answer carries
# `reload` false for a generation that only reports a determinism result, so the check can land
# after the frame without re-mounting the page.
WATCH_CLIENT = """
if (/[?&]watch=1/.test(location.search)) {
  const W = window.__watch = { gen: 0, applied: 0, reloads: 0, last: null, error: null };
  (async () => {
    while (window.__mounted === false) await new Promise(r => setTimeout(r, 25));
    for (;;) {
      try {
        const m = await (await fetch("reload?since=" + W.gen, { cache: "no-store" })).json();
        W.last = m; W.error = null;
        if (m.gen > W.gen) {
          W.gen = m.gen;
          if (m.reload) {
            const tl = await (await fetch(m.timeline + "?gen=" + m.gen, { cache: "no-store" })).json();
            await reload(tl);
            W.reloads++;
          }
          W.applied = m.gen;
        }
      } catch (e) { W.error = String(e); await new Promise(r => setTimeout(r, 500)); }
    }
  })();
}
"""


def module_script(engine_src: str = None) -> str:
    """The engine as a module fetched beside the page, with the watch client behind ?watch=1.

    The namespace import is deliberate: a build dir written before P51 T4 carries an engine copy
    with no `reload` export, and a NAMED import of a missing binding is a link error that kills
    the whole page - `import * as` degrades to an undefined function instead."""
    return ('<script type="module">import * as ENGINE from "./' + (engine_src or ENGINE.name) + '";\n'
            'const mount = ENGINE.mount, reload = ENGINE.reload;\n'
            + BOOT + "\n" + WATCH_CLIENT + "</script>")


def player_text(template: Path = TEMPLATE, engine: Path = ENGINE) -> str:
    """The shell and the engine as ONE text - what a lint or a grep-style check means by "the
    player's source". It is not a page (nothing is substituted): use instantiate() for that."""
    return template.read_text(encoding="utf-8") + "\n" + engine.read_text(encoding="utf-8")


def single_file_shell(template: Path = TEMPLATE, engine: Path = ENGINE) -> str:
    """The shell with the engine inlined and the two DATA slots still open ({{TIMELINE}} / {{URIS}}).

    One caller needs this and not instantiate(): ep1's legacy F door patches the player's OWN JS
    (the caption loop, DUR, the title) before it substitutes its data - those anchors moved into
    the engine, so the door has to see the composed text."""
    html = template.read_text(encoding="utf-8")
    for slot in ("{{TIMELINE}}", "{{URIS}}", "{{ENGINE}}"):
        if slot not in html:
            raise RuntimeError(f"{template} is not the shell - it has no {slot} slot")
    return (html.replace("{{TIMELINE_SRC}}", "").replace("{{ASSETS_SRC}}", "")
                .replace("{{ENGINE}}", engine_script(engine)))


def instantiate(timeline: dict, uris: dict, template: Path = TEMPLATE, split: bool = False,
                engine: Path = ENGINE, timeline_src: str = "", assets_src: str = ASSETS_NAME) -> str:
    """The build step's exact substitution on the reviewed shell.

    split=False (the default, and what every golden and test takes): the single-file form.
    split=True: the shell with the two data slots EMPTY and their data-src filled - the engine
    fetches them. `timeline_src` is the compiled timeline's file name in the build dir."""
    html = template.read_text(encoding="utf-8")
    for slot in ("{{TIMELINE}}", "{{URIS}}", "{{ENGINE}}"):
        if slot not in html:
            raise RuntimeError(f"{template} is not the shell - it has no {slot} slot")
    if split and not timeline_src:
        raise ValueError("the split form needs the compiled timeline's file name (timeline_src)")
    return (html.replace("{{TIMELINE}}", "" if split else json.dumps(timeline, separators=(",", ":")))
                .replace("{{URIS}}", "" if split else json.dumps(uris, separators=(",", ":")))
                .replace("{{TIMELINE_SRC}}", timeline_src if split else "")
                .replace("{{ASSETS_SRC}}", assets_src if split else "")
                .replace("{{ENGINE}}", module_script(engine.name) if split else engine_script(engine)))


def write_split(build_dir: Path, timeline: dict, uris: dict, timeline_name: str,
                template: Path = TEMPLATE, engine: Path = ENGINE) -> Path:
    """Write a SELF-CONTAINED split build: the page, the compiled timeline, the asset map, and a COPY
    of the engine beside them (a served build never reaches back into docs/). player.json names the
    engine and its sha - the compiled timeline stays byte-identical to what the build always wrote."""
    build_dir = Path(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / timeline_name).write_text(json.dumps(timeline, indent=1), encoding="utf-8")
    (build_dir / ASSETS_NAME).write_text(json.dumps(uris, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(engine, build_dir / engine.name)
    out = build_dir / "player.html"
    out.write_text(instantiate(timeline, uris, template, split=True, engine=engine,
                               timeline_src=timeline_name), encoding="utf-8")
    (build_dir / MANIFEST_NAME).write_text(json.dumps({
        "form": "split",
        "engine": engine.name,
        "engine_sha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
        "timeline": timeline_name,
        "assets": ASSETS_NAME,
    }, indent=1), encoding="utf-8")
    return out


class _Quiet(http.server.SimpleHTTPRequestHandler):
    # .mjs is NOT in Python's mimetypes table on Windows, and a module served as
    # application/octet-stream is refused by the browser's strict MIME check - the split page
    # would load its shell and mount nothing. no-store so a rebuilt engine is never the cached one.
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".mjs": "text/javascript"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

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
    # P51 T1: the split page mounts after two fetches, so the DOM can exist before the engine has
    # run. __mounted is undefined on a single-file page and on every player committed before the
    # split, where the engine has already run by load - those pass this line without waiting.
    page.wait_for_function("window.__mounted !== false", timeout=300000)
    page.evaluate("document.fonts.ready")
    page.evaluate("document.getElementById('vo').muted = true")
    page.evaluate("for (const id of ['sndbar']) { const e=document.getElementById(id); if (e) e.style.display='none'; }")
    page.add_style_tag(content=(
        "*, *::before, *::after { transition: none !important; animation: none !important; }"
        f" #shell {{ width: auto !important; max-width: none !important; }}"
        f" #fit {{ width: {w}px !important; height: {h}px !important; max-width: none !important; overflow: visible !important; }}"
        " #stage { transform: none !important; }"))
    page.set_viewport_size({"width": w + 64, "height": h + 64})
    # the handwriting face loads on first use: fetch it explicitly so a portrait page never measures its ink
    # in the fallback face (P41) - the template rebuilds its pages when the load lands
    page.evaluate("() => document.fonts.load('700 68px Kalam').then(() => document.fonts.load('400 40px Kalam')).then(() => 1)")
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


def render_surface(name: str, t: float | None = None, template: Path = TEMPLATE, kinetics: dict | None = None) -> bytes:
    """A frame of a golden surface; `name` may be a FLAG_FRAMES key (surface@flag), which fixes the flags and the t."""
    if name in FLAG_FRAMES:
        surface, flags, t_flag = FLAG_FRAMES[name]
        return render_surface(surface, t if t is not None else t_flag, template, dict(flags, **(kinetics or {})))
    tl, uris, t_default, aspect = load_surface(name)
    if kinetics is not None:
        tl = dict(tl, kinetics=kinetics)
    with tempfile.TemporaryDirectory() as td:
        html = Path(td) / f"{name.replace('@', '-')}.html"
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
    ap.add_argument("--flags", help="comma-separated kinetics flags to turn ON for --surface")
    ap.add_argument("--out")
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    names = sorted(p.name[: -len(".timeline.json")] for p in SOURCES.glob("*.timeline.json")) + sorted(FLAG_FRAMES)
    if args.list:
        print("\n".join(names)); return 0
    if args.surface:
        png = render_surface(args.surface, args.t, kinetics={f: True for f in args.flags.split(",")} if args.flags else None)
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
