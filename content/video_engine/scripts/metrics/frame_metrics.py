"""E1 frame metrics (P40 T2): what the frames themselves say about motion, computed over a
directory of rendered frames. Two metrics in numpy, two in OpenCV (present on this host since
2026-09-04; they fall away cleanly and say so when cv2 is absent).

    motion_energy   mean absolute luminance change between consecutive frames (0..255)
    flow            mean dense optical-flow magnitude, downsampled px/frame - real motion, not a fade
    saliency_concentration  share of the spectral-residual saliency mass in the top 5 % of pixels -
                    low means the eye has nowhere in particular to go
    change_centroid where the change happened - the luminance-weighted centroid of |diff|,
                    as a fraction of width/height; None when nothing changed

    python frame_metrics.py <frames_dir> [--fps 2] [--windows 0,15,30,45,60] [--json out]

Every number this produces is a measurement of ONE render. Thresholds do not come from here
(P40's human gate: n = 1 proposes, a second episode's curve promotes).
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import cv2  # opencv-contrib-python-headless, installed 2026-09-04 under the operator's standing permission
    HAVE_CV2 = True
except ImportError:  # the two OpenCV metrics fall away cleanly on a bare checkout
    cv2 = None
    HAVE_CV2 = False
DEFERRED = {} if HAVE_CV2 else {"saliency": "needs OpenCV (cv2 not installed)", "optical_flow": "needs OpenCV (cv2 not installed)"}
SALIENCY_TOP = 0.05   # concentration = share of saliency mass in the top 5 % of pixels: ~0.05 diffuse, -> 1.0 one clear focus


def luminance(path: Path, scale: int = 4) -> np.ndarray:
    """Grey frame, downsampled `scale`x for speed - the metrics are about where and how much, not detail."""
    im = Image.open(path).convert("L")
    if scale > 1:
        im = im.resize((im.width // scale, im.height // scale), Image.BILINEAR)
    return np.asarray(im, dtype=np.float32)


def pair_metrics(a: np.ndarray, b: np.ndarray) -> dict:
    d = np.abs(b - a)
    energy = float(d.mean())
    total = float(d.sum())
    if total <= 0:
        return {"motion_energy": 0.0, "change_centroid": None}
    h, w = d.shape
    ys, xs = np.mgrid[0:h, 0:w]
    cx = float((d * xs).sum() / total) / max(1, w - 1)
    cy = float((d * ys).sum() / total) / max(1, h - 1)
    return {"motion_energy": round(energy, 4), "change_centroid": [round(cx, 4), round(cy, 4)]}


def flow_magnitude(a: np.ndarray, b: np.ndarray) -> float | None:
    """Mean dense optical-flow magnitude (Farneback), in downsampled px per frame. Real motion,
    as opposed to luminance change: a fade changes every pixel and moves nothing."""
    if not HAVE_CV2:
        return None
    flow = cv2.calcOpticalFlowFarneback(a.astype(np.uint8), b.astype(np.uint8), None, 0.5, 3, 15, 3, 5, 1.2, 0)
    return round(float(np.linalg.norm(flow, axis=2).mean()), 4)


def saliency_concentration(frame: np.ndarray) -> float | None:
    """Spectral-residual saliency: what share of the map's mass sits in its top 5 % of pixels.
    Low = the eye has nowhere in particular to go (a bare plate); high = one clear focus."""
    if not HAVE_CV2:
        return None
    ok, sal = cv2.saliency.StaticSaliencySpectralResidual_create().computeSaliency(frame.astype(np.uint8))
    if not ok:
        return None
    v = np.sort(sal.ravel())[::-1]
    total = float(v.sum())
    if total <= 0:
        return None
    k = max(1, int(len(v) * SALIENCY_TOP))
    return round(float(v[:k].sum() / total), 4)


def sequence_metrics(frames: list[Path]) -> list[dict]:
    out = []
    prev = luminance(frames[0]) if frames else None
    for i, f in enumerate(frames[1:], start=1):
        cur = luminance(f)
        out.append({"index": i, "frame": f.name, **pair_metrics(prev, cur),
                    "flow": flow_magnitude(prev, cur), "saliency_concentration": saliency_concentration(cur)})
        prev = cur
    return out


def window_summary(rows: list[dict], fps: float, edges: list[float]) -> list[dict]:
    """Per-window mean/max motion energy and the mean centroid drift, edges in seconds."""
    out = []
    for a, b in zip(edges, edges[1:]):
        sel = [r for r in rows if a <= r["index"] / fps < b]
        energies = [r["motion_energy"] for r in sel]
        cents = [r["change_centroid"] for r in sel if r["change_centroid"]]
        drift = [abs(c2[0] - c1[0]) + abs(c2[1] - c1[1]) for c1, c2 in zip(cents, cents[1:])]
        flows = [r["flow"] for r in sel if r.get("flow") is not None]
        sals = [r["saliency_concentration"] for r in sel if r.get("saliency_concentration") is not None]
        out.append({"window": f"{a:g}-{b:g}s", "frames": len(sel),
                    "flow_mean": round(st.mean(flows), 4) if flows else None,
                    "saliency_concentration_mean": round(st.mean(sals), 4) if sals else None,
                    "motion_energy_mean": round(st.mean(energies), 4) if energies else None,
                    "motion_energy_max": round(max(energies), 4) if energies else None,
                    "still_share": round(sum(1 for e in energies if e < 0.5) / len(energies), 3) if energies else None,
                    "centroid_drift_mean": round(st.mean(drift), 4) if drift else None})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("frames_dir"); ap.add_argument("--fps", type=float, default=2.0)
    ap.add_argument("--windows", default="0,15,30,45,60,75,90,105,120"); ap.add_argument("--json")
    args = ap.parse_args()
    frames = sorted(Path(args.frames_dir).glob("*.png"))
    rows = sequence_metrics(frames)
    edges = [float(x) for x in args.windows.split(",")]
    summary = window_summary(rows, args.fps, edges)
    report = {"frames": len(frames), "fps": args.fps, "deferred": DEFERRED, "windows": summary}
    for w in summary:
        print(f"  {w['window']:<10} energy {w['motion_energy_mean']!s:>8}  max {w['motion_energy_max']!s:>8}  flow {w['flow_mean']!s:>7}  saliency-conc {w['saliency_concentration_mean']!s:>7}  drift {w['centroid_drift_mean']!s}")
    if args.json:
        Path(args.json).write_text(json.dumps({**report, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
