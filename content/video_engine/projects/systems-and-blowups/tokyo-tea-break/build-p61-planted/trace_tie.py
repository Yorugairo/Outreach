"""P61 T3d - TRACE THE PLANTED ELEMENT off this build's own last plate frame.

R26-16 (the operator, 2026-09-07): *"pull it off of the red tie at the last frame or two."* The
morph's source is a real element of the outgoing world, never a conjured shape. So the poly is
not drawn here - it is MEASURED:

  1. the built player is served and the STAGE frame one frame before the cut is captured
     (render_baseline.frame_png - the same door the clip renderer uses), so what is traced is the
     plate as the viewer last sees it: cover-fitted, lit, on its `live` idle;
  2. the middle panelist's TIE is thresholded on that frame - the caller's own bitmap, as
     contour.mjs says ("the bitmap is the caller's"): a sample is the tie where blue beats red by
     BLUE_MIN and the blue channel is above BLUE_FLOOR;
  3. `kinetics/contour.mjs` `contourSilhouette` walks it - the engine's own tracer, imported from
     the committed file, nothing re-implemented - and the ring is carried into STAGE FRACTIONS,
     which is what `world.morph.poly` is measured in.

Writes `planted-tie.poly.json` beside the build: the poly and everything needed to re-trace it.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BUILD = Path(__file__).resolve().parent
REPO = BUILD.parents[5]
SCRIPTS = REPO / "content/video_engine/scripts"
CONTOUR = SCRIPTS / "kinetics/contour.mjs"
sys.path.insert(0, str(SCRIPTS))

TIMELINE_NAME = "tokyo-planted.timeline.json"
OUT = BUILD / "planted-tie.poly.json"
FRAME_PNG = BUILD / "planted-tie-source-frame.png"   # the frame the poly was traced from, kept beside it

# the MIDDLE panelist's tie on the stage, with a margin - the box only says WHERE to look; the
# outline itself is the tracer's. Measured on the rendered stage: the body sits at x 360-394,
# y 801-891 of 1080x1920 (the knot above it is a second component, cut off by the collar).
BOX = (330, 770, 430, 920)          # x0, y0, x1, y1 in stage px
BLUE_MIN, BLUE_FLOOR = 35, 70       # blue beats red by this much, and is at least this bright
TOL = 0.6                           # Douglas-Peucker, in sample px (the golden's tolerance)
LEAD_S = 1 / 30                     # "the last frame or two": one frame before the cut


def cut_time() -> float:
    tl = json.loads((BUILD / TIMELINE_NAME).read_text(encoding="utf-8"))
    page = next(s for s in tl["scenes"] if (s.get("world") or {}).get("kind") == "ledger")
    return float(page["span"][0])


def stage_frame(t: float) -> bytes:
    import render_baseline as RB
    from playwright.sync_api import sync_playwright
    w, h = RB.STAGE["9:16"]
    srv, port = RB.serve(BUILD)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": w, "height": h}).new_page()
            page.goto(f"http://127.0.0.1:{port}/player.html", wait_until="networkidle", timeout=180000)
            RB.prepare_page(page, w, h)
            png = RB.frame_png(page, round(t, 4), (w, h))
            browser.close()
    finally:
        srv.shutdown()
    return png


def bitmap(png: bytes) -> tuple[int, int, bytes]:
    """The caller's bitmap: the tie's own pixels inside BOX, 1 where blue beats red."""
    import io
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(io.BytesIO(png)).convert("RGB")).astype(int)
    x0, y0, x1, y1 = BOX
    c = a[y0:y1, x0:x1]
    m = ((c[:, :, 2] - c[:, :, 0] > BLUE_MIN) & (c[:, :, 2] > BLUE_FLOOR)).astype("uint8")
    return x1 - x0, y1 - y0, m.tobytes()


def trace(w: int, h: int, data: bytes) -> list[list[float]]:
    """kinetics/contour.mjs contourSilhouette, on the real module, carried into stage fractions."""
    x0, y0, _x1, _y1 = BOX
    src = (
        f"const {{ contourSilhouette }} = await import({json.dumps(CONTOUR.as_uri())});\n"
        "const fs = await import('node:fs');\n"
        f"const data = new Uint8Array(fs.readFileSync({json.dumps(str(BIN))}));\n"
        f"const pts = contourSilhouette({{ w: {w}, h: {h}, data }}, {{ tol: {TOL} }});\n"
        "if (!pts) { console.log('null'); } else {\n"
        f"  console.log(JSON.stringify(pts.map((p) => [ +(((p[0] + 0.5) + {x0}) / 1080).toFixed(5),\n"
        f"                                              +(((p[1] + 0.5) + {y0}) / 1920).toFixed(5) ])));\n"
        "}\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, encoding="utf-8") as f:
        f.write(src)
        mjs = f.name
    out = subprocess.run(["node", mjs], capture_output=True, text=True, check=True).stdout.strip()
    Path(mjs).unlink(missing_ok=True)
    if out == "null":
        raise SystemExit("contourSilhouette found no ink in the box - the element is not there, or the threshold is wrong")
    return json.loads(out)


BIN = Path(tempfile.gettempdir()) / "p61-t3d-tie.bin"


def main() -> int:
    t = round(cut_time() - LEAD_S, 4)
    png = stage_frame(t)
    FRAME_PNG.write_bytes(png)
    w, h, data = bitmap(png)
    BIN.write_bytes(data)
    on = sum(data)
    poly = trace(w, h, data)
    BIN.unlink(missing_ok=True)
    sys.path.insert(0, str(SCRIPTS))
    import build_scene_timeline_f as C
    err = C.morph_poly_error(poly, "planted-tie: world.morph")
    if err:
        raise SystemExit(err)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    OUT.write_text(json.dumps({
        "what": "the middle panelist's blue tie on plate-c-blue-ties-panel, traced off this build's own last plate frame",
        "why": "R26-16 / P48 T5b: the morph's source is a real element of the outgoing world - world.morph.poly",
        "traced_by": "content/video_engine/scripts/kinetics/contour.mjs contourSilhouette (the committed engine)",
        "frame_s": t, "frame_png": FRAME_PNG.name,
        "frame_sha256": hashlib.sha256(png).hexdigest(),
        "box_stage_px": list(BOX), "stage": [1080, 1920],
        "threshold": {"blue_minus_red_gt": BLUE_MIN, "blue_gt": BLUE_FLOOR, "samples_on": int(on)},
        "tol_sample_px": TOL,
        "bbox_stage_fraction": [round(min(xs), 5), round(min(ys), 5), round(max(xs), 5), round(max(ys), 5)],
        "poly": poly,
    }, indent=1), encoding="utf-8")
    print(f"  traced      : {len(poly)} points, {on} samples of ink, at t={t:.4f}s")
    print(f"  bbox        : x {min(xs):.4f}-{max(xs):.4f}  y {min(ys):.4f}-{max(ys):.4f} (stage fractions)")
    print(f"  wrote       : {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
