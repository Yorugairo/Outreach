"""Bravos's camera, MEASURED (E38: the threshold comes from the reference). For every composition in the Claude shot ledger
that holds >= 3.2 s, estimate the global similarity transform between two frames 2 s apart (ORB + RANSAC partial affine):
the zoom rate (%/s), the pan (px/s at 1280 wide) and the residual. Compositions are classed by the ledger's species text.
Writes claude-watch/camera.json and prints the table."""
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

D = Path("C:/Users/Snipe/Downloads/Outreach Program/content/video_engine/sources/reference_analyses/bravos-china-just-triggered-a-new-world-order")
VID = D / "claude-watch/download/video.mp4"
LEDGER = D / "SHOT_LEDGER.claude.md"
W, H = 640, 360


def mmss(s: str) -> float:
    m, rest = s.split(":"); return int(m) * 60 + float(rest)


rows = []
for line in LEDGER.read_text(encoding="utf-8").splitlines():
    if not line.startswith("| ") or "| COMP |" not in line and "| build |" not in line:
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    try:
        n, start, end, dur, kind, _frame, species, lane = cells[:8]
    except ValueError:
        continue
    rows.append({"n": int(n), "start": mmss(start), "end": mmss(end), "kind": kind, "species": species, "lane": lane})

# compositions = from each COMP to the next COMP (builds inside belong to the composition)
comps = []
for i, r in enumerate(rows):
    if r["kind"] != "COMP":
        continue
    end = next((q["start"] for q in rows[i + 1:] if q["kind"] == "COMP"), rows[-1]["end"])
    comps.append({"n": r["n"], "start": r["start"], "end": end, "species": r["species"], "lane": r["lane"]})


def classify(sp: str) -> str:
    s = sp.lower()
    if "map" in s: return "map"
    if "chart" in s or "bars" in s or "line" in s or "treemap" in s or "multiples" in s: return "chart"
    if "diagram" in s or "flow" in s: return "diagram"
    if "headline" in s or "press" in s or "card" in s or "screenshot" in s or "tv" in s or "mock" in s: return "card"
    if "sponsor" in s: return "sponsor"
    return "other"


def frame_at(t: float):
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(VID), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-"], capture_output=True).stdout
    if len(out) < W * H:
        return None
    return np.frombuffer(out[:W * H], dtype=np.uint8).reshape(H, W)


orb = cv2.ORB_create(1500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)


def similarity(a, b):
    ka, da = orb.detectAndCompute(a, None); kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None or len(ka) < 12 or len(kb) < 12:
        return None
    m = sorted(bf.match(da, db), key=lambda x: x.distance)[:400]
    if len(m) < 12:
        return None
    pa = np.float32([ka[x.queryIdx].pt for x in m]); pb = np.float32([kb[x.trainIdx].pt for x in m])
    M, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=2.0)
    if M is None:
        return None
    s = float(np.hypot(M[0, 0], M[0, 1])); cx, cy = W / 2, H / 2
    # the translation of the frame CENTRE (a zoom about the centre moves the corners, not the centre)
    tx = float(M[0, 0] * cx + M[0, 1] * cy + M[0, 2] - cx); ty = float(M[1, 0] * cx + M[1, 1] * cy + M[1, 2] - cy)
    return {"scale": s, "dx": tx, "dy": ty, "inliers": int(inl.sum()), "matches": len(m)}


GAP = 2.0
out = []
for c in comps:
    dur = c["end"] - c["start"]
    if dur < 3.2:
        continue
    samples = []
    t0 = c["start"] + 0.6
    while t0 + GAP <= c["end"] - 0.2 and len(samples) < 3:
        a, b = frame_at(t0), frame_at(t0 + GAP)
        if a is None or b is None:
            break
        r = similarity(a, b)
        if r and r["inliers"] >= 12:
            samples.append({"t": round(t0, 2), "zoom_pct_s": round((r["scale"] - 1) / GAP * 100, 3), "pan_px_s": round(np.hypot(r["dx"], r["dy"]) / GAP * (1280 / W), 2), "inliers": r["inliers"]})
        t0 += GAP + 0.4
    if samples:
        z = [s["zoom_pct_s"] for s in samples]; p = [s["pan_px_s"] for s in samples]
        out.append({**c, "dur": round(dur, 1), "cls": classify(c["species"]), "zoom_pct_s": round(float(np.median(z)), 3), "pan_px_s": round(float(np.median(p)), 2), "samples": samples})
    print(f"{c['n']:>3} {c['start']:7.1f} {dur:5.1f}s {classify(c['species']):8} zoom {out[-1]['zoom_pct_s'] if out and out[-1]['n'] == c['n'] else '   -'} %/s  pan {out[-1]['pan_px_s'] if out and out[-1]['n'] == c['n'] else '-'} px/s  | {c['species'][:60]}", flush=True)

(D / "claude-watch/camera.json").write_text(json.dumps({"method": "ORB+RANSAC partial affine between frames 2 s apart, 640x360 grey; zoom = (scale-1)/2s; pan = the frame centre's travel at 1280 wide", "compositions": out}, indent=1), encoding="utf-8")
print("\nSUMMARY (compositions >= 3.2 s, measured):", len(out))
for cls in ("map", "chart", "diagram", "card", "sponsor", "other"):
    xs = [o for o in out if o["cls"] == cls]
    if not xs: continue
    z = np.array([abs(o["zoom_pct_s"]) for o in xs]); p = np.array([o["pan_px_s"] for o in xs])
    print(f"  {cls:8} n={len(xs):2}  |zoom| median {np.median(z):.2f} %/s  p90 {np.percentile(z, 90):.2f}   pushes(>0.3%/s) {int((z > 0.3).sum())}   pan median {np.median(p):.1f} px/s  pans(>8px/s) {int((p > 8).sum())}   still(<0.15%/s & <4px/s) {int(((z < 0.15) & (p < 4)).sum())}")
