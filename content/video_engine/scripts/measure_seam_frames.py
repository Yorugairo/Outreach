"""THE BLACK FRAME AT A SEAM, measured (P54 follow-up, operator 2026-09-13).

The operator: "doesnt our dip lead to a black frame ultimately? it's really the flash before or a second black frame
that we're looking for right?" A declared `dip` fades to black and back on a LINEAR ramp over DIP_S, symmetric about
the boundary, and its darkest instant IS the boundary (engine: `dipA = 1 - clamp01(|t - boundary| / (dip_s / 2))`).
So one or two near-black frames at a dip's boundary are the dip working. The faults are read off the frames themselves:

  flash    a near-black frame within +-window of a boundary whose exit is NOT a dip (cut, wipe, suck, melt, dissolve...)
  jump     at a dip: a near-black run whose previous frame is bright - it was cut into, not faded into
  hold     at a dip: a near-black run longer than the dip's dark core (DIP_CORE_FRAMES at DIP_S, scaled by a longer dip)
  outside  at a dip: a near-black frame outside the dip's own window [boundary - dip_s/2, boundary + dip_s/2]

WHICH EXIT A BOUNDARY HAS. `exit` names the transition INTO the scene it sits on (the engine's E47 law: a scene
reads its OWN exit for the half after its start and the NEXT scene's for the half before its end). The boundary at
scenes[i].span[1] therefore takes scenes[i + 1].exit.

    python measure_seam_frames.py <build> [--fps 24] [--window 0.6] [--json] [--out <path>]

Opens the build's player ONCE in headless Chromium (render_baseline's server, prepare_page and frame_png), seeks every
boundary's window on the render's own frame grid (k / fps), and writes `<build>/seam-frames.json` (or --out).
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# the engine scripts this imports (render_baseline, gate_motion_density); VIDEO_ENGINE_SCRIPTS points a run from an
# isolated worktree at the current checkout's copies
SCRIPTS = Path(os.environ.get("VIDEO_ENGINE_SCRIPTS") or HERE)
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

FPS = 24.0                # THE RENDER CLOCK (E99 s36, P61 T12): render_episode.FPS - this script seeks the render's own
                          # frame grid (k / fps), so it follows the renderer. Every dial below is SECONDS or luma.
DIP_S = 0.47              # [DERIVED: the engine's DIP_S and gate_motion_density.DIP_S - the reference's 14 frames at 30 fps]
DIP_CORE_FRAMES = 2       # the dark core, IN FRAMES, on whatever grid --fps names: a linear dip is fully black only AT the
                          # boundary, so at most the two frames STRADDLING it read near-black. Grid-independent by that
                          # geometry, and the same-seconds re-expression agrees - 2 frames at 30 fps (0.067 s) is 1.6 at
                          # 24 fps, which rounds to 2 (0.083 s). Unchanged at 24 (measured: see NEAR_BLACK_LUMA)
NEAR_BLACK_LUMA = 8.0     # mean luma (0-255) of a downscaled frame below which a frame reads as black. MEASURED on the
                          # approved Japan short's six dips (2026-09-13, on the then-30 fps grid): the darkest dip frame read 6, 3, 4,
                          # 0, 0, 1; the ramp frames beside it read 10-17 on four of the six (6/6 and 7/4 over the darker
                          # 38- and 43-luma worlds); no cut boundary went below 56. 8 (~3 % of full scale) takes every
                          # dip's black core and none of its ramp over a cream world. A world darker than
                          # dark_world_luma() holds its ramp under 8 for more than the core by arithmetic, so such a
                          # hold is marked `dark_world` (the Japan outro clip settles at luma 18) - reported, not hidden.
JUMP_SLACK = 1.5          # a fade's per-frame step may overshoot the ideal linear step by this much (grid phase, ink)
LUMA_W = 64               # the frame is downscaled to this width before its mean is taken - noise-free and fast
FULL_LUMA = 255.0


def exit_parts(exit_id) -> tuple[str, float | None]:
    """`dip:0.8` -> ("dip", 0.8); `suck:0.5,0.52` -> ("suck", None); None -> ("none", None)."""
    raw = str(exit_id or "none")
    name, _, arg = raw.partition(":")
    if name in ("dip", "blurzoom") and arg:
        try:
            return name, float(arg)
        except ValueError:
            return name, None
    return name, None


def boundaries_of(tl: dict) -> list[dict]:
    """Every scene boundary inside the runtime, with the exit INTO the scene that starts there."""
    scenes = tl.get("scenes") or []
    runtime = float(tl.get("runtime_s") or 0.0)
    out = []
    for i in range(len(scenes) - 1):
        at = float(scenes[i]["span"][1])
        if runtime and at >= runtime - 1e-6:
            continue
        nxt = scenes[i + 1]
        kind, secs = exit_parts(nxt.get("exit"))
        page = ((nxt.get("world") or {}).get("page") or {})
        out.append({"t": round(at, 3), "exit": str(nxt.get("exit") or "none"), "kind": kind,
                    "dip_s": (secs or DIP_S) if kind == "dip" else None,
                    "from_scene": str(scenes[i].get("scene_id", "?")), "to_scene": str(nxt.get("scene_id", "?")),
                    "next_enter": str(page.get("enter") or "none") if isinstance(page, dict) else "none"})
    return out


def frame_times(at: float, window: float, fps: float) -> list[float]:
    """The render's own frames (k / fps) inside [at - window, at + window]."""
    k0, k1 = math.ceil((at - window) * fps - 1e-9), math.floor((at + window) * fps + 1e-9)
    return [round(k / fps, 4) for k in range(max(0, k0), k1 + 1)]


def dark_runs(lumas: list[float], threshold: float) -> list[tuple[int, int]]:
    """(first index, last index) of every run of consecutive frames below the threshold."""
    runs, start = [], None
    for i, v in enumerate(lumas):
        if v < threshold:
            start = i if start is None else start
        elif start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(lumas) - 1))
    return runs


def jump_step(dip_s: float, fps: float) -> float:
    """The largest per-frame luma drop a dip's linear ramp can make from a white frame, with slack."""
    return FULL_LUMA / max(1.0, (dip_s / 2) * fps) * JUMP_SLACK


def dark_world_luma(dip_s: float, fps: float, threshold: float, allowed: int) -> float:
    """The settled-world luma under which a LINEAR dip's own ramp stays below the threshold for more than `allowed`
    frames: the ramp is under it for dip_s * threshold / world seconds, so world < dip_s * fps * threshold / allowed."""
    return dip_s * fps * threshold / max(1, allowed)


def seam_faults(ts: list[float], lumas: list[float], at: float, kind: str, dip_s: float | None,
                fps: float = FPS, threshold: float = NEAR_BLACK_LUMA) -> list[dict]:
    """The faults in one boundary's luma series. Pure: no browser. The window's first and last frames stand for the
    settled worlds either side (a `dark_world` hold is one whose world is too dark for the threshold to separate)."""
    faults = []
    world = min(lumas[0], lumas[-1]) if lumas else FULL_LUMA
    for a, z in dark_runs(lumas, threshold):
        run = {"from": ts[a], "to": ts[z], "frames": z - a + 1, "min_luma": round(min(lumas[a:z + 1]), 2)}
        if kind != "dip":
            faults.append({"fault": "flash", **run})
            continue
        secs = dip_s or DIP_S
        if a > 0 and lumas[a - 1] - lumas[a] > jump_step(secs, fps):
            faults.append({"fault": "jump", "prev_luma": round(lumas[a - 1], 2), **run})
        allowed = max(DIP_CORE_FRAMES, round(DIP_CORE_FRAMES * secs / DIP_S))
        if run["frames"] > allowed:
            faults.append({"fault": "hold", "allowed": allowed, "world_luma": round(world, 2),
                           "dark_world": world < dark_world_luma(secs, fps, threshold, allowed), **run})
        tol = 0.5 / fps
        if ts[a] < at - secs / 2 - tol or ts[z] > at + secs / 2 + tol:
            faults.append({"fault": "outside", "dip_window": [round(at - secs / 2, 3), round(at + secs / 2, 3)], **run})
    return faults


def luma_of_png(png: bytes) -> float:
    """Mean luma (0-255) of the frame, downscaled to LUMA_W wide."""
    from PIL import Image, ImageStat
    im = Image.open(io.BytesIO(png)).convert("L")
    h = max(1, round(im.height * LUMA_W / im.width))
    return float(ImageStat.Stat(im.resize((LUMA_W, h), Image.BILINEAR)).mean[0])


def _capture(build: Path, tl: dict, bounds: list[dict], window: float, fps: float) -> list[list[float]]:
    """One browser, every boundary's window: the luma series per boundary."""
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    html = build / "player.html"
    if not html.exists():
        raise SystemExit(f"no player.html in {build} - build the episode first")
    w, h = RB.STAGE[str(tl.get("aspect") or "16:9")]
    srv, port = RB.serve(build)
    series = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/{html.name}", wait_until="networkidle", timeout=300000)
            RB.prepare_page(page, w, h)
            for b in bounds:
                row = []
                for t in frame_times(b["t"], window, fps):
                    RB.frame_png(page, t, (w, h))          # WARM: a cold seek can read a card before it decodes
                    row.append(luma_of_png(RB.frame_png(page, t, (w, h))))
                series.append(row)
            browser.close()
    finally:
        srv.shutdown()
    return series


def measure(build: Path, fps: float, window: float, threshold: float = NEAR_BLACK_LUMA) -> dict:
    import gate_motion_density as G
    tl = json.loads(G._timeline_path(build, None).read_text(encoding="utf-8"))
    bounds = boundaries_of(tl)
    series = _capture(build, tl, bounds, window, fps)
    rows = []
    for b, lumas in zip(bounds, series):
        ts = frame_times(b["t"], window, fps)
        faults = seam_faults(ts, lumas, b["t"], b["kind"], b["dip_s"], fps, threshold)
        rows.append({**b, "frames": [[t, round(v, 2)] for t, v in zip(ts, lumas)], "faults": faults})
    return {"build": build.name, "runtime_s": float(tl.get("runtime_s") or 0.0), "fps": fps, "window_s": window,
            "near_black_luma": threshold, "boundaries": rows,
            "n_faults": sum(len(r["faults"]) for r in rows)}


def summary_lines(doc: dict) -> list[str]:
    out = [f"seam frames: {len(doc['boundaries'])} boundaries, {doc['n_faults']} faults "
           f"(near-black < {doc['near_black_luma']} luma, +-{doc['window_s']}s at {doc['fps']:g} fps)"]
    for r in doc["boundaries"]:
        darkest = min((v for _, v in r["frames"]), default=float("nan"))
        tag = "; ".join(f"{f['fault']} {f['from']:.3f}-{f['to']:.3f}s x{f['frames']}" for f in r["faults"]) or "clean"
        out.append(f"  {r['t']:7.2f}  {r['from_scene']}->{r['to_scene']} exit={r['exit']:<14} darkest {darkest:6.1f}  {tag}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="the black frame at a seam: the flash, the jump, the second black frame")
    ap.add_argument("build", type=Path)
    ap.add_argument("--fps", type=float, default=FPS)
    ap.add_argument("--window", type=float, default=0.6)
    ap.add_argument("--threshold", type=float, default=NEAR_BLACK_LUMA)
    ap.add_argument("--json", action="store_true", help="print the document instead of the summary")
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    doc = measure(a.build, a.fps, a.window, a.threshold)
    out = a.out or (a.build / "seam-frames.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(doc, indent=1) if a.json else "\n".join(summary_lines(doc) + [f"-> {out}"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
