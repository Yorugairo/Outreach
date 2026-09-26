"""Measure a moving mark's SPEED and its EDGE SHARPNESS off the pixels - the strobe's two terms (P72 T32, R26-85).

E99 s30 set `CADENCE.ON1_PX_S` = 154 px/s (RED's pan rule: 1/7 picture width per second on the 1080 stage, at 24 fps
WITH a 180-degree shutter) and left the rest "to REVIEW on real motion": the law is speed x edge sharpness (Watson,
Ahumada & Farrell 1986, Eq. 11 - sampled and smooth motion are indistinguishable when w_s >= w_l + r * u_0), so a
declared-cadence ceiling needs a sharpness term before it can state a number
(`docs/research/runs/strobe_stop_motion/VERIFICATION-2026-09-13.md` s3). This tool reads both terms off FRAMES, so the
reference (a YouTube download) and ours (a captured player) go through the same code (E38 - thresholds from the
reference, never fitted to ours). It measures; it sets nothing.

Per moving mark (a region of interest over a run of consecutive frames):

  v        speed, px/s - the summed phase-correlation shift of the region over the run, divided by the run's time
           (a hold counts as time), also given at the 1920-wide stage (`v_1920`) and in picture widths per second
  w_s      the step rate, Hz - the share of frame pairs in which the mark moved, times the frame rate (on 1s at 24 fps
           = 24, on 2s = 12)
  d        the step, px - the mean shift over the pairs that moved (the spacing between two shown positions)
  w_along  the edge's 10-90 % rise width ALONG the motion, px (the median over the mark's moving edges): what the
           strobe's eye sees; a shutter's motion blur widens it
  w_across the same width on the mark's edges PARALLEL to the motion - the mark's static sharpness
  u0       the edge's effective top spatial frequency, cycles/px: 0.8755 / w_along (where a Gaussian edge of that
           10-90 width keeps 10 % of its contrast), capped at the pixel Nyquist 0.5
  T        v * u0, Hz - Watson's r * u_0 in pixel units, so it is the same number at any screen size or distance
  S        d / w_along - how many edge widths one step jumps (S > 1: the shown positions do not overlap)

    python measure_strobe_sharpness.py survey  (--video V | --frames INDEX.json) [--stride-s 1] [--band 100 300] --out S.json
    python measure_strobe_sharpness.py measure (--video V | --frames INDEX.json) --t0 T --t1 T --box x,y,w,h
    python measure_strobe_sharpness.py --check [--record R.json --root DIR [--root DIR2]]

`--frames` reads an index json: {"fps", "width", "height", "mode": "pairs"|"run", "items": [{"t", "frames": [png..]}]}
beside its PNGs. `--check` runs the known-answer fixtures (a sharp bar on 1s and on 2s, and the RED parity bar at
154 px/s under a 180-degree shutter) and, given a record, re-measures every event in it; it exits 1 on a drift.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage, special

STAGE_W = 1920               # every speed is also given at the 1920-wide stage
TILE = 128                   # survey tile, px at the source's own size
MOVE_PX = 0.5                # a pair's shift under this is a hold
PEAK_MIN = 0.5               # a translation explaining under half the changed pixels' squared difference is no read
CHANGE_GREY = 12.0           # a pixel changed between two frames by more than this many grey levels
LK_ITERS = 12
DIFF_MIN = 0.6               # mean |b - a| (grey levels) under this: nothing moved in the region
TEXTURE_MIN = 4.0            # a survey tile flatter than this (grey std) carries no mark
EDGE_CONTRAST = 24.0         # a profile's plateaus must differ by this many grey levels
PROFILE_R = 6.0              # the edge profile is the pixel row (or column) +-6 px about the edge pixel
PROFILES_PER_PAIR = 150      # the strongest moving edges read per frame pair
RESID_MAX = 0.08             # a fit whose rms residual exceeds 8 % of the edge's contrast is not one clean edge
W_PER_SIGMA = 2.5631         # a Gaussian edge's 10-90 % width is 2.5631 sigma
GAUSS_10PCT = 0.8755         # u0 = 0.8755 / w10-90: a Gaussian edge's frequency at 10 % MTF (sqrt(ln10 / 2) / pi * 2.563)
NYQUIST = 0.5
MIN_PROFILES = 8
CHECK_TOL = 0.08             # --check: a recorded number reproduces within 8 %
CHECK_ABS = {"w_s": 0.6, "w_along": 0.25, "w_across": 0.25, "S": 0.15, "T": 2.0}


# ---------------------------------------------------------------- frame sources

def _ffmpeg_frames(video: Path, t0: float, n: int, w: int, h: int, vf: str | None = None):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.4f}", "-i", str(video)]
    if vf:
        cmd += ["-vf", vf, "-fps_mode", "passthrough"]
    cmd += ["-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    size = w * h
    return [np.frombuffer(raw[i * size:(i + 1) * size], np.uint8).reshape(h, w).astype(np.float32)
            for i in range(len(raw) // size)]


def video_info(video: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(video)],
                         capture_output=True, check=True, text=True).stdout
    d = json.loads(out)
    num, den = d["streams"][0]["r_frame_rate"].split("/")
    return {"width": d["streams"][0]["width"], "height": d["streams"][0]["height"],
            "fps": float(num) / float(den), "duration": float(d["format"]["duration"])}


def _load_png(path: Path) -> np.ndarray:
    from PIL import Image  # noqa: PLC0415 - only the frames source needs it
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32)


def load_index(index: Path) -> dict:
    d = json.loads(index.read_text(encoding="utf-8"))
    for key in ("fps", "width", "height", "mode", "items"):
        if key not in d:
            raise SystemExit(f"{index}: the frames index has no {key!r}")
    if d["mode"] not in ("pairs", "run"):
        raise SystemExit(f"{index}: mode {d['mode']!r} is neither 'pairs' nor 'run'")
    d["root"] = index.parent
    return d


def run_frames(src: dict, t0: float, t1: float) -> tuple[list[np.ndarray], float]:
    """Consecutive frames in [t0, t1) and the frame rate, from a video or a run index."""
    if src["kind"] == "video":
        n = max(2, int(round((t1 - t0) * src["fps"])))
        return _ffmpeg_frames(src["path"], t0, n, src["width"], src["height"]), src["fps"]
    items = [it for it in src["items"] if t0 - 1e-6 <= it["t"] < t1 - 1e-6]
    return [_load_png(src["root"] / it["frames"][0]) for it in items], src["fps"]


def survey_pairs(src: dict, stride_s: float):
    """(t, a, b) consecutive-frame pairs every `stride_s` seconds."""
    if src["kind"] == "frames":
        for it in src["items"]:
            a, b = (_load_png(src["root"] / f) for f in it["frames"][:2])
            yield it["t"], a, b
        return
    fps, step = src["fps"], max(2, int(round(stride_s * src["fps"])))
    chunk = 120 * step
    total = int(src["duration"] * fps)
    for n0 in range(0, total, chunk):
        vf = f"select='lt(mod(n\\,{step})\\,2)'"
        frames = _ffmpeg_frames(src["path"], n0 / fps, 2 * (chunk // step), src["width"], src["height"], vf)
        for k in range(0, len(frames) - 1, 2):
            yield (n0 + (k // 2) * step) / fps, frames[k], frames[k + 1]


def open_source(args) -> dict:
    if args.video:
        return {"kind": "video", "path": Path(args.video), **video_info(Path(args.video))}
    d = load_index(Path(args.frames))
    return {"kind": "frames", **d}


# ---------------------------------------------------------------- the shift

def _hann(h: int, w: int) -> np.ndarray:
    return np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)


def _subpixel(surface: np.ndarray, iy: int, ix: int) -> tuple[float, float]:
    h, w = surface.shape
    ys, xs = [(iy + k) % h for k in (-1, 0, 1)], [(ix + k) % w for k in (-1, 0, 1)]
    patch = np.clip(surface[np.ix_(ys, xs)], 0, None)
    tot = patch.sum() or 1.0
    return iy + float((patch.sum(axis=1) * (-1, 0, 1)).sum() / tot), ix + float((patch.sum(axis=0) * (-1, 0, 1)).sum() / tot)


def _phase_peak(a: np.ndarray, b: np.ndarray, skip_origin: bool) -> tuple[float, float]:
    """The phase-correlation peak of b against a (sub-pixel by the 3 x 3 centroid); with skip_origin, the strongest
    peak more than 2 px off (0, 0) - the moving mark's when a static ground holds the origin."""
    win = _hann(*a.shape)
    fa, fb = np.fft.fft2((a - a.mean()) * win), np.fft.fft2((b - b.mean()) * win)
    cross = fb * np.conj(fa)
    surf = np.real(np.fft.ifft2(cross / (np.abs(cross) + 1e-6)))
    h, w = surf.shape
    if skip_origin:
        for dy in (-2, -1, 0, 1, 2):
            surf[dy % h, [d % w for d in (-2, -1, 0, 1, 2)]] = -np.inf
    iy, ix = np.unravel_index(int(np.argmax(surf)), surf.shape)
    sy, sx = _subpixel(np.where(np.isfinite(surf), surf, 0.0), iy, ix)
    return float(sx - w if sx > w / 2 else sx), float(sy - h if sy > h / 2 else sy)


def _refine(a: np.ndarray, b: np.ndarray, d0: tuple[float, float], weight: np.ndarray) -> tuple[float, float, float]:
    """Lucas-Kanade from d0: the translation d minimising sum weight * (b(x) - a(x - d))^2 over the changed pixels;
    returns (dx, dy, the weighted residual after)."""
    dx, dy = d0
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(np.float64)
    for _ in range(LK_ITERS):
        aw = ndimage.map_coordinates(a, [yy - dy, xx - dx], order=3, mode="nearest")
        gy, gx = np.gradient(aw)
        r = b - aw
        m = np.array([[np.sum(weight * gx * gx), np.sum(weight * gx * gy)],
                      [np.sum(weight * gx * gy), np.sum(weight * gy * gy)]])
        step = np.linalg.lstsq(m, -np.array([np.sum(weight * gx * r), np.sum(weight * gy * r)]), rcond=None)[0]
        dx, dy = dx + float(step[0]), dy + float(step[1])
        if abs(dx) > a.shape[1] / 2 or abs(dy) > a.shape[0] / 2:
            return d0[0], d0[1], math.inf
        if abs(step[0]) + abs(step[1]) < 1e-3:
            break
    aw = ndimage.map_coordinates(a, [yy - dy, xx - dx], order=3, mode="nearest")
    return dx, dy, float(np.sum(weight * (b - aw) ** 2))


def phase_shift(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """(dx, dy, explained) of b against a: two phase-correlation starts (the strongest peak, and the strongest off
    the origin), each refined by Lucas-Kanade on the changed pixels; the start that leaves the smaller residual wins.
    `explained` is the share of the changed pixels' squared difference the translation accounts for (0..1)."""
    a, b = a.astype(np.float64), b.astype(np.float64)
    weight = ndimage.binary_dilation(np.abs(b - a) > CHANGE_GREY, iterations=3).astype(np.float64)
    before = float(np.sum(weight * (b - a) ** 2))
    if before <= 0:
        return 0.0, 0.0, 0.0
    best = min((_refine(a, b, _phase_peak(a, b, skip), weight) for skip in (False, True)), key=lambda r: r[2])
    return best[0], best[1], max(0.0, 1.0 - best[2] / before)


# ---------------------------------------------------------------- the edge

def _area_step(i: np.ndarray, lo: float, hi: float, x0: float, sigma: float) -> np.ndarray:
    """A step at x0 blurred by a Gaussian of `sigma` px, then area-sampled by the pixel [i - .5, i + .5] - so the
    fitted sigma is the edge's own softness, free of where the edge happens to fall inside a pixel."""
    sg = max(sigma, 1e-3)

    def g(t):
        z = t / sg
        return t * special.ndtr(z) + sg * np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    z = i - x0
    return lo + (hi - lo) * (g(z + 0.5) - g(z - 0.5))


def _templates() -> tuple[np.ndarray, np.ndarray]:
    """Every (x0, sigma) of the grid as a centred, unit-norm template over the profile's pixels."""
    i = np.arange(2 * int(PROFILE_R) + 1, dtype=np.float64) - int(PROFILE_R)
    x0s, sgs = np.meshgrid(np.arange(-1.5, 1.5001, 0.02), np.arange(0.0, 4.0001, 0.03))
    tpl = np.stack([_area_step(i, 0.0, 1.0, x0, sg) for x0, sg in zip(x0s.ravel(), sgs.ravel())])
    tpl -= tpl.mean(axis=1, keepdims=True)
    return tpl / np.linalg.norm(tpl, axis=1, keepdims=True), sgs.ravel()


_TPL: tuple[np.ndarray, np.ndarray] | None = None


def fit_sigmas(profiles: np.ndarray) -> np.ndarray:
    """The fitted softness (px) of each pixel-sampled edge profile (rows), NaN where a row is not one clean edge:
    lo + c * template least squares over the (x0, sigma) grid, the best template per row."""
    global _TPL
    if _TPL is None:
        _TPL = _templates()
    tpl, sgs = _TPL
    out = np.full(len(profiles), np.nan)
    for k0 in range(0, len(profiles), 512):
        p = profiles[k0:k0 + 512].astype(np.float64)
        pc = p - p.mean(axis=1, keepdims=True)
        m = pc @ tpl.T
        best = np.argmax(m * m, axis=1)
        mb = m[np.arange(len(p)), best]
        resid = np.sqrt(np.clip((pc * pc).sum(axis=1) - mb * mb, 0, None) / p.shape[1])
        contrast = np.abs(p[:, -3:].mean(axis=1) - p[:, :3].mean(axis=1))
        ok = (contrast >= EDGE_CONTRAST) & (resid <= RESID_MAX * contrast)
        out[k0:k0 + 512] = np.where(ok, sgs[best], np.nan)
    return out


def edge_sigma(profile: np.ndarray) -> float | None:
    """The fitted softness (px) of one edge profile, or None when it is not a clean single edge."""
    sg = fit_sigmas(np.asarray(profile, dtype=np.float64)[None, :])[0]
    return None if np.isnan(sg) else float(sg)


def edge_sigmas(img: np.ndarray, moved: np.ndarray, axis: int, cap: int = PROFILES_PER_PAIR) -> list[float]:
    """Fitted softness of the moving edges whose gradient lies along `axis` (1 = x, 0 = y), sampled on that axis."""
    gx, gy = ndimage.sobel(img, axis=1) / 8.0, ndimage.sobel(img, axis=0) / 8.0
    g = np.hypot(gx, gy)
    along = np.abs(gx if axis == 1 else gy)
    sel = moved & (along > 0.92 * g) & (g > 6.0)
    r = int(PROFILE_R)
    sel[:r + 1, :] = sel[-r - 1:, :] = False
    sel[:, :r + 1] = sel[:, -r - 1:] = False
    ys, xs = np.nonzero(sel)
    keep = np.argsort(-g[ys, xs])[:cap]
    if len(keep) == 0:
        return []
    ys, xs = ys[keep], xs[keep]
    offs = np.arange(-r, r + 1)
    profs = img[ys[:, None], xs[:, None] + offs] if axis == 1 else img[ys[:, None] + offs, xs[:, None]]
    sg = fit_sigmas(profs)
    return [float(v) for v in sg[~np.isnan(sg)]]


# ---------------------------------------------------------------- one mark over a run

def _crop(img: np.ndarray, box) -> np.ndarray:
    x, y, w, h = box
    return img[y:y + h, x:x + w]


def pair_reads(frames: list[np.ndarray]) -> list[dict]:
    reads = []
    for a, b in zip(frames[:-1], frames[1:]):
        diff = float(np.abs(b - a).mean())
        if diff < DIFF_MIN:
            reads.append({"dx": 0.0, "dy": 0.0, "moved": False, "diff": diff})
            continue
        dx, dy, peak = phase_shift(a, b)
        moved = math.hypot(dx, dy) >= MOVE_PX and peak >= PEAK_MIN
        reads.append({"dx": dx if moved else 0.0, "dy": dy if moved else 0.0, "moved": moved, "diff": diff})
    return reads


def _widths_over(frames, reads, axis: int) -> tuple[list[float], list[float]]:
    along, across = [], []
    for (a, b), r in zip(zip(frames[:-1], frames[1:]), reads):
        if not r["moved"]:
            continue
        moved = ndimage.binary_dilation(np.abs(b - a) > CHANGE_GREY, iterations=2)
        along += [W_PER_SIGMA * sg for sg in edge_sigmas(a, moved, axis)]
        across += [W_PER_SIGMA * sg for sg in edge_sigmas(a, moved, 1 - axis)]
    return along, across


def mark_read(frames: list[np.ndarray], fps: float, width: int) -> dict:
    """The strobe terms of one mark over consecutive frames (already cropped to its region)."""
    reads = pair_reads(frames)
    n = len(reads)
    sx, sy = sum(r["dx"] for r in reads), sum(r["dy"] for r in reads)
    moving = [r for r in reads if r["moved"]]
    v = math.hypot(sx, sy) / (n / fps) if n else 0.0
    out = {"pairs": n, "moved_pairs": len(moving), "fps": round(fps, 3), "v": round(v, 1),
           "v_1920": round(v * STAGE_W / width, 1), "pw_s": round(v / width, 4),
           "w_s": round(fps * len(moving) / n, 2) if n else 0.0,
           "d": round(sum(math.hypot(r["dx"], r["dy"]) for r in moving) / len(moving), 2) if moving else 0.0,
           "direction": [round(sx, 1), round(sy, 1)]}
    if not moving:
        return {**out, "w_along": None, "w_across": None, "u0": None, "T": None, "S": None, "profiles": [0, 0]}
    axis = 1 if abs(sx) >= abs(sy) else 0          # the edges are read on the motion's dominant pixel axis
    along, across = _widths_over(frames, reads, axis)
    w_a = float(np.median(along)) if len(along) >= MIN_PROFILES else None
    w_x = float(np.median(across)) if len(across) >= MIN_PROFILES else None
    u0 = min(NYQUIST, GAUSS_10PCT / w_a) if w_a is not None and w_a > 0 else (NYQUIST if w_a == 0 else None)
    return {**out, "w_along": _r(w_a), "w_across": _r(w_x), "u0": _r(u0, 3),
            "T": _r(v * u0 if u0 else None, 1), "S": _r(out["d"] / max(w_a, 1.0 / NYQUIST / 2) if w_a is not None else None),
            "profiles": [len(along), len(across)]}


def _r(x, nd: int = 2):
    return None if x is None else round(float(x), nd)


def measure(src: dict, t0: float, t1: float, box) -> dict:
    frames, fps = run_frames(src, t0, t1)
    if len(frames) < 3:
        raise SystemExit(f"measure: {len(frames)} frames in [{t0}, {t1}) - a run needs at least 3")
    return {"t0": t0, "t1": t1, "box": list(box), **mark_read([_crop(f, box) for f in frames], fps, src["width"])}


# ---------------------------------------------------------------- the survey

def survey(src: dict, stride_s: float, band: tuple[float, float]) -> list[dict]:
    """Every tile whose content translated inside the band (1920-stage px/s) in a consecutive pair; a hit's `peak`
    is the share of the tile's change the translation explains (phase_shift's third value)."""
    hits = []
    fps, scale = src["fps"], STAGE_W / src["width"]
    for t, a, b in survey_pairs(src, stride_s):
        h, w = a.shape
        for y in range(0, h - TILE + 1, TILE):
            for x in range(0, w - TILE + 1, TILE):
                ta, tb = a[y:y + TILE, x:x + TILE], b[y:y + TILE, x:x + TILE]
                if ta.std() < TEXTURE_MIN or float(np.abs(tb - ta).mean()) < DIFF_MIN:
                    continue
                dx, dy, peak = phase_shift(ta, tb)
                v = math.hypot(dx, dy) * fps * scale
                if peak >= PEAK_MIN and band[0] <= v <= band[1]:
                    hits.append({"t": round(t, 3), "box": [x, y, TILE, TILE], "v_1920": round(v, 1),
                                 "dx": round(dx, 2), "dy": round(dy, 2), "peak": round(peak, 3)})
    return hits


def events(hits: list[dict], gap_s: float = 1.5) -> list[dict]:
    """Survey hits grouped by time (hits within gap_s chain); each event keeps its hits' union box."""
    out: list[dict] = []
    for h in sorted(hits, key=lambda r: r["t"]):
        if out and h["t"] - out[-1]["t_last"] <= gap_s:
            e = out[-1]
            e["t_last"], e["tiles"] = h["t"], e["tiles"] + [h]
        else:
            out.append({"t_first": h["t"], "t_last": h["t"], "tiles": [h]})
    for e in out:
        best = max(e["tiles"], key=lambda r: r["peak"])
        e.update({"n_tiles": len(e["tiles"]), "best": best,
                  "v_1920_median": float(np.median([r["v_1920"] for r in e["tiles"]]))})
        del e["tiles"]
    return out


# ---------------------------------------------------------------- --check: the known answers

def _bar_frames(v: float, fps: float, n: int, on: int = 1, shutter: float = 0.0, size=(96, 256)) -> list[np.ndarray]:
    """A 40 px wide bright bar on a dark ground moving right at v px/s, area-sampled (x 16 in space), stepped on `on`s,
    optionally blurred by a shutter open for `shutter` of the frame interval (x 16 in time)."""
    h, w = size
    xs = (np.arange(w * 16) + 0.5) / 16.0
    frames = []
    for k in range(n):
        t_step = (k // on) * on / fps
        subs = np.linspace(0, shutter / fps, 16, endpoint=False) if shutter else [0.0]
        row = np.zeros(w)
        for dt in subs:
            left = 40.0 + v * (t_step + dt)
            row += ((xs >= left) & (xs < left + 40.0)).reshape(w, 16).mean(axis=1)
        row = 30.0 + 200.0 * row / len(subs)
        img = np.tile(row, (h, 1)).astype(np.float32)
        img[:24, :] = img[-24:, :] = 30.0      # top and bottom edges: the across-motion widths
        frames.append(img)
    return frames


def _parity_width(v: float, fps: float, shutter: float) -> float:
    """The 10-90 % width of a sharp edge smeared by a shutter: the box of L = v * shutter / fps px ramps the edge
    linearly over L, so 10 % to 90 % spans 0.8 L."""
    return 0.8 * v * shutter / fps


FIXTURES = (
    {"id": "sharp-on1-200", "v": 200.0, "on": 1, "shutter": 0.0,
     "want": {"v": 200.0, "w_s": 24.0, "w_along": 0.0, "w_across": 0.0}},
    {"id": "sharp-on2-200", "v": 200.0, "on": 2, "shutter": 0.0,
     "want": {"v": 200.0, "w_s": 12.0, "d": 16.67, "w_along": 0.0, "T": 100.0}},
    {"id": "red-parity-154-180deg", "v": 154.0, "on": 1, "shutter": 0.5,
     "want": {"v": 154.0, "w_s": 24.0, "w_along": _parity_width(154.0, 24.0, 0.5), "w_across": 0.0}},
)


def _drift(name: str, got, want, key: str) -> str | None:
    if got is None:
        return f"{name}: {key} not measured (want {want})"
    tol = max(CHECK_TOL * abs(want), CHECK_ABS.get(key, 0.0))
    return None if abs(got - want) <= tol else f"{name}: {key} {got} vs {want:.3f} (tol {tol:.3f})"


def check_fixtures() -> list[str]:
    faults = []
    for fx in FIXTURES:
        r = mark_read(_bar_frames(fx["v"], 24.0, 25, fx["on"], fx["shutter"]), 24.0, 1920)
        faults += [f for k, want in fx["want"].items() if (f := _drift(fx["id"], r.get(k), want, k))]
        print(f"  fixture {fx['id']}: v {r['v']} w_s {r['w_s']} d {r['d']} w_along {r['w_along']} "
              f"w_across {r['w_across']} T {r['T']} S {r['S']}")
    return faults


def check_record(record: Path, roots) -> list[str]:
    rec = json.loads(record.read_text(encoding="utf-8"))
    faults = []
    for m in rec.get("marks", []):
        src = _record_source(m, [roots] if isinstance(roots, Path) else list(roots))
        got = measure(src, m["t0"], m["t1"], m["box"])
        for key in ("v", "w_s", "w_along", "w_across", "S"):
            if m.get(key) is not None and (f := _drift(m["id"], got.get(key), m[key], key)):
                faults.append(f)
        print(f"  mark {m['id']}: v {got['v']} w_s {got['w_s']} w_along {got['w_along']} S {got['S']}")
    print(f"  record: {len(rec.get('marks', []))} mark(s) re-measured")
    return faults


def _record_source(m: dict, roots: list[Path]) -> dict:
    """The mark's source under the first root that holds it (a research run and the main checkout may differ)."""
    found = [r / m["source"] for r in roots if (r / m["source"]).exists()]
    if not found:
        raise SystemExit(f"{m['id']}: its source {m['source']} is under none of {[str(r) for r in roots]}")
    p = found[0]
    if p.suffix == ".json":
        return {"kind": "frames", **load_index(p)}
    return {"kind": "video", "path": p, **video_info(p)}


# ---------------------------------------------------------------- CLI

def _box(text: str) -> tuple[int, int, int, int]:
    parts = [int(float(v)) for v in text.split(",")]
    if len(parts) != 4 or parts[2] < 16 or parts[3] < 16:
        raise argparse.ArgumentTypeError(f"--box {text!r}: x,y,w,h with w and h at least 16 px")
    return tuple(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="The strobe's two terms - speed and edge sharpness - off the pixels.")
    ap.add_argument("mode", nargs="?", choices=("survey", "measure"))
    ap.add_argument("--video")
    ap.add_argument("--frames")
    ap.add_argument("--stride-s", type=float, default=1.0)
    ap.add_argument("--band", nargs=2, type=float, default=(100.0, 300.0), metavar=("LO", "HI"))
    ap.add_argument("--t0", type=float)
    ap.add_argument("--t1", type=float)
    ap.add_argument("--box", type=_box)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true", help="the known-answer fixtures, then a record's re-measure")
    ap.add_argument("--record", type=Path)
    ap.add_argument("--root", type=Path, action="append",
                    help="where a record's sources live (repeatable; the first root holding a source wins)")
    args = ap.parse_args(argv)
    if args.check:
        faults = check_fixtures() + (check_record(args.record, args.root or [Path(".")]) if args.record else [])
        for f in faults:
            print(f"FAIL {f}")
        print(f"--check: {len(faults)} drift(s)")
        return 1 if faults else 0
    if not args.mode or bool(args.video) == bool(args.frames):
        ap.error("survey / measure need exactly one of --video, --frames")
    src = open_source(args)
    if args.mode == "survey":
        hits = survey(src, args.stride_s, tuple(args.band))
        result = {"source": args.video or args.frames, "band_1920": list(args.band), "hits": hits, "events": events(hits)}
    else:
        if args.t0 is None or args.t1 is None or args.box is None:
            ap.error("measure needs --t0, --t1 and --box")
        result = measure(src, args.t0, args.t1, args.box)
    text = json.dumps(result, indent=1)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text if args.mode == "measure" else f"{len(result['hits'])} hit(s), {len(result['events'])} event(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
