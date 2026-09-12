"""FROZEN FRAMES - the measurement behind the motion gate's M18 row (ruling E49, P47 T5).

E49: "nothing ever goes truly still" - a held thing is never bit-identical from frame to frame. This tool renders a
built player at a fixed frame rate through the same harness the shipped renderer uses (render_baseline: headless
Chromium seeks #scrub and screenshots #stage) and hashes every frame's RGB bytes. A run of identical consecutive
hashes is a freeze; its length is the time across which nothing on screen changed. The gate reads the file this
writes and WARNs on any run over FROZEN_MAX_S (0.5 s, [DERIVED: HyperFrames' "the final 1-2 seconds"; halved]).

    python measure_frozen_frames.py <build-dir> [--fps 12] [--start S] [--end S] [--timeline NAME.timeline.json]
                                                [--html player.html] [--out frame-hashes.json]
                                                [--layers page,docks,captions]

Writes <build-dir>/frame-hashes.json: {"fps", "start", "end", "html_sha256", "frames": [{"t", "sha256"}]} and prints
the runs. A 90 s short at 12 fps is ~1100 screenshots (a few minutes); 12 fps resolves a 0.5 s freeze to a frame.
Deterministic: the player is a pure function of t, so the same build hashes the same way twice.

PER LAYER (R26-13, 2026-09-11). The whole frame cannot see a frozen page beneath a boiling caption or a moving video
dock: Tokyo v2 measured 1036 distinct frames of 1066 and M18 passed while its pages were still. `--layers
page,docks,captions` runs ONE loop per layer with the shell's `?layers=` switch on the URL - the layers not named are
hidden before the first paint, with their geometry intact - and writes `frame-hashes.<layer>.json` beside the
whole-frame file. The gate then reads the page, the docks and the captions each on their own (M18) and still reports
the whole-frame verdict. The switch is a query read at load: a build's player.html is untouched by it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_baseline as RB  # noqa: E402

FRAME_HASHES_NAME = "frame-hashes.json"
FROZEN_MAX_S = 0.5   # [DERIVED: HyperFrames' "the final 1-2 seconds"; halved] - mirrored in gate_motion_density.FROZEN_MAX_S
LAYERS = ("page", "docks", "captions")   # R26-13: the shell's ?layers= switch - mirrored in gate_motion_density.FRAME_LAYERS


def layer_hashes_name(layer: str) -> str:
    """`frame-hashes.page.json` - one per layer, beside the whole-frame file. Mirrors gate_motion_density."""
    return f"frame-hashes.{layer}.json"


def frozen_runs(frames: list[dict], max_s: float = FROZEN_MAX_S) -> list[tuple[float, float]]:
    """(start t, frozen seconds) of every run of identical consecutive hashes longer than max_s, in time order.
    The frozen seconds of a run are the time between its first and last identical frame."""
    fs = sorted((float(f["t"]), str(f["sha256"])) for f in frames)
    out: list[tuple[float, float]] = []
    i = 0
    while i < len(fs):
        j = i
        while j + 1 < len(fs) and fs[j + 1][1] == fs[i][1]:
            j += 1
        dur = fs[j][0] - fs[i][0]
        if j > i and dur > max_s:
            out.append((fs[i][0], dur))
        i = j + 1
    return out


def hash_frames(html: Path, aspect: str, fps: float, start: float, end: float, progress=None,
                layer: str | None = None) -> list[dict]:
    """One browser, one seek per frame, one sha256 of the stage's RGB bytes per frame.

    `layer` asks the SHELL for one layer only (`?layers=<layer>`, R26-13): the other layers are hidden before the
    first paint and keep their geometry, so what stays is painted exactly where the whole frame paints it."""
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE[aspect]
    srv, port = RB.serve(html.parent)
    query = f"?layers={layer}" if layer else ""
    out: list[dict] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1.0).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}{query}", wait_until="networkidle", timeout=120000)
            RB.prepare_page(page, w, h)
            n = int(round((end - start) * fps))
            for i in range(n + 1):
                t = round(start + i / fps, 4)
                if t > end + 1e-9:
                    break
                png = RB.frame_png(page, t, (w, h))
                out.append({"t": t, "sha256": hashlib.sha256(RB.rgb_bytes(png)[1]).hexdigest()})
                if progress and i % int(fps) == 0:
                    progress(t, end)
            browser.close()
    finally:
        srv.shutdown()
    return out


def measure(build: Path, fps: float = 12.0, start: float | None = None, end: float | None = None,
            timeline_name: str | None = None, html_name: str = "player.html", out_name: str = FRAME_HASHES_NAME,
            progress=None, layer: str | None = None) -> tuple[Path, list[tuple[float, float]]]:
    """One loop over the build's player: the whole frame, or ONE layer (`layer="page"`, R26-13), whose hashes go to
    `frame-hashes.<layer>.json` unless `out_name` names the file."""
    tls = [build / timeline_name] if timeline_name else sorted(build.glob("*.timeline.json"))
    if not tls or not tls[0].exists():
        raise SystemExit(f"no timeline in {build}")
    if layer is not None and layer not in LAYERS:
        raise SystemExit(f"unknown layer {layer!r} - the shell knows {', '.join(LAYERS)}")
    tl = json.loads(tls[0].read_text(encoding="utf-8"))
    aspect = str(tl.get("aspect") or "16:9")
    runtime = float(tl.get("runtime_s") or max(s["span"][1] for s in tl["scenes"]))
    s0, s1 = (0.0 if start is None else start), (runtime if end is None else min(end, runtime))
    html = build / html_name
    if not html.exists():
        raise SystemExit(f"no {html_name} in {build}")
    frames = hash_frames(html, aspect, fps, s0, s1, progress, layer)
    runs = frozen_runs(frames)
    doc = {"fps": fps, "start": s0, "end": s1, "aspect": aspect, "timeline": tls[0].name,
           "html_sha256": hashlib.sha256(html.read_bytes()).hexdigest(), "frozen_max_s": FROZEN_MAX_S,
           "frames": frames, "frozen_runs": [{"t": a, "s": round(d, 4)} for a, d in runs]}
    if layer:
        doc["layer"] = layer
    if layer and out_name == FRAME_HASHES_NAME:
        out_name = layer_hashes_name(layer)
    out = build / out_name
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return out, runs


def parse_layers(spec: str | None) -> list[str]:
    """`"page,captions"` -> ["page", "captions"]; `"all"` or an empty spec after `--layers` -> every layer. An unknown
    name is an error, not a silent skip: a mistyped layer would otherwise read as "nothing froze"."""
    if spec is None:
        return []
    names = [s.strip().lower() for s in spec.replace(" ", ",").split(",") if s.strip()]
    if not names or names == ["all"]:
        return list(LAYERS)
    if bad := [n for n in names if n not in LAYERS]:
        raise SystemExit(f"unknown layer(s) {', '.join(bad)} - the shell knows {', '.join(LAYERS)}")
    return [n for n in LAYERS if n in names]   # the shell's order, once each


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("build", type=Path)
    ap.add_argument("--fps", type=float, default=12.0)
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--timeline")
    ap.add_argument("--html", default="player.html")
    ap.add_argument("--out", default=FRAME_HASHES_NAME)
    ap.add_argument("--layers", nargs="?", const="all", default=None,
                    help="also hash each layer on its own, one loop each: page,docks,captions (R26-13)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    layers = parse_layers(a.layers)
    for layer in [None] + layers:                     # the whole frame first, then one loop per layer
        print(f"[{layer or 'whole frame'}]", flush=True)
        # --out names the WHOLE-frame file only; a layer's file is always frame-hashes.<layer>.json, so
        # a custom --out cannot collide three ways (the gate looks for the layer names beside it)
        out, runs = measure(a.build, a.fps, a.start, a.end, a.timeline, a.html,
                            a.out if layer is None else FRAME_HASHES_NAME,
                            progress=lambda t, e: print(f"  {t:7.2f} / {e:.2f}", flush=True), layer=layer)
        print(f"frame-hashes ({layer or 'whole frame'}): {out}")
        if runs:
            print(f"FROZEN ({layer or 'whole frame'}): {len(runs)} run(s) over {FROZEN_MAX_S:.2f}s: "
                  + ", ".join(f"{a:.2f}s+{d:.2f}s" for a, d in runs[:12]))
        else:
            print(f"no run of identical frames over {FROZEN_MAX_S:.2f}s ({layer or 'whole frame'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
