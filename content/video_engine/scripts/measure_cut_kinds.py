"""E38/TR-1: what KIND of transition does the Wealth Logic reference use at each of its 99
boundaries? The Gemini pass called all 99 "hard cut" from the shot ledger alone; the operator
spot-checked two boundaries in the video and both contradicted it. So the classification is
measured here, from the pixels, with rules a human can re-run.

For every boundary t the script decodes the window [t - 0.6 s, t + 0.8 s] at the native frame
rate as 160-px-wide grey frames (ffmpeg raw pipe - no opencv), and reduces each frame to three
series:

    L  mean luminance          (0..255)
    D  mean |frame - previous| (0..255) - how much of the image changed
    S  variance of the Laplacian - sharpness; motion blur and defocus collapse it

`classify()` is a pure function of those three series plus `sim` (the structural similarity of
the frame 0.5 s before to the frame 0.5 s after, i.e. "is it the same world"), so the rules are
testable on synthetic series without a video (see tests/test_measure_cut_kinds.py).

Every threshold below is [DERIVED] - a starting reference read off this reference video, not a
law. They are printed in the report header and in `--print-thresholds`.

    python measure_cut_kinds.py --video <mp4> --boundaries <csv> --out <csv> \
        [--only 2,4,26] [--frames-out DIR] [--summary-json PATH] [--jobs 4]
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

# --- window ------------------------------------------------------------------
PRE_S = 0.6          # [DERIVED] seconds decoded before the boundary
POST_S = 0.8         # [DERIVED] seconds decoded after it
WIDTH = 160          # [DERIVED] downscale width; kills codec noise, keeps structure
PEAK_SEARCH_S = 0.25  # [DERIVED] the ledger's times are +-0.1 s, so hunt the peak in +-0.25 s

# --- classification thresholds ([DERIVED], all of them) ----------------------
EDGE_FRAMES = 4          # the steady levels are read from the window edges, 0.5-0.8 s out
D_FLOOR = 0.4            # grey levels; a static plate has D ~ 0.1, so ratios need a floor
HARD_PEAK_RATIO = 6.0    # D_peak > 6x the window median (peak excluded) = a step
TRANSITION_FRAC = 0.25   # the transition spans the frames carrying > 25% of the peak change;
#                          a span of 1 IS "no ramp: back to baseline within one frame"
DISSOLVE_MIN_FRAMES = 4  # a dissolve holds D up for >= 4 frames
DISSOLVE_DOMINANCE = 3.0  # ...with no frame > 3x the mean of the run (no single dominant peak)
DIP_MIN_FRAMES = 3       # a dip through dark/light spans >= 3 frames
DIP_DARK_FRAC = 0.60     # L falls under 0.60x the darker of the two steady levels
DIP_BRIGHT_FRAC = 1.60   # or rises over 1.60x the brighter one
BLUR_VALLEY_FRAC = 0.50  # S drops under 0.50x the SOFTER of the two steady levels: a valley
BLUR_MIN_FRAMES = 2      # ...for >= 2 frames. Below BOTH levels = it recovered, by construction
WORLD_PEAK_RATIO = 2.0   # D peak under 2x baseline: nothing switched
SIM_SAME_WORLD = 0.60    # SSIM(t-0.5, t+0.5) >= 0.60 = the same world persisted
SETTLE_RATIO = 1.5       # the new scene has "settled" when D drops under 1.5x baseline
L_FLAT = 3.0             # grey levels; L before/after closer than this = no level change

KINDS = ("hard-cut", "dissolve", "dip", "blur-zoom", "world-persists", "other")

CSV_FIELDS = [
    "boundary", "t_s", "kind", "duration_frames", "first_motion_frames", "motion_after_0_5s",
    "D_peak", "D_median", "L_before", "L_min", "L_after", "S_before", "S_min", "at_gap", "gap_s",
]


def thresholds() -> dict[str, float]:
    """Every [DERIVED] dial, for the report header and the run log."""
    return {
        "PRE_S": PRE_S, "POST_S": POST_S, "WIDTH": WIDTH, "EDGE_FRAMES": EDGE_FRAMES,
        "D_FLOOR": D_FLOOR, "HARD_PEAK_RATIO": HARD_PEAK_RATIO,
        "TRANSITION_FRAC": TRANSITION_FRAC, "DISSOLVE_MIN_FRAMES": DISSOLVE_MIN_FRAMES,
        "DISSOLVE_DOMINANCE": DISSOLVE_DOMINANCE, "DIP_MIN_FRAMES": DIP_MIN_FRAMES,
        "DIP_DARK_FRAC": DIP_DARK_FRAC, "DIP_BRIGHT_FRAC": DIP_BRIGHT_FRAC,
        "BLUR_VALLEY_FRAC": BLUR_VALLEY_FRAC, "BLUR_MIN_FRAMES": BLUR_MIN_FRAMES,
        "WORLD_PEAK_RATIO": WORLD_PEAK_RATIO, "SIM_SAME_WORLD": SIM_SAME_WORLD,
        "SETTLE_RATIO": SETTLE_RATIO, "L_FLAT": L_FLAT,
    }


# --- decode ------------------------------------------------------------------

def probe_fps(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True, check=True).stdout.strip()
    num, _, den = out.partition("/")
    return float(num) / float(den or 1)


def decode_window(video: Path, start: float, dur: float, height: int) -> np.ndarray:
    """(n, h, w) float32 grey frames. Fast seek (-ss before -i), accurate since ffmpeg 2.1."""
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, start):.4f}", "-i", str(video),
           "-t", f"{dur:.4f}", "-vf", f"scale={WIDTH}:{height}", "-pix_fmt", "gray",
           "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (WIDTH * height)
    if n == 0:
        raise RuntimeError(f"ffmpeg returned no frames for {start:.2f}s of {video.name}")
    return np.frombuffer(raw[: n * WIDTH * height], dtype=np.uint8).reshape(n, height, WIDTH).astype(np.float32)


# --- per-frame measures ------------------------------------------------------

def laplacian_var(f: np.ndarray) -> float:
    """Sharpness. 4-neighbour Laplacian on the interior, variance of the response."""
    lap = (4.0 * f[1:-1, 1:-1] - f[:-2, 1:-1] - f[2:, 1:-1] - f[1:-1, :-2] - f[1:-1, 2:])
    return float(lap.var())


def series(frames: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """L (mean luminance), D (mean abs diff to previous; D[0]=0), S (Laplacian variance)."""
    L = frames.mean(axis=(1, 2))
    D = np.zeros(len(frames), dtype=np.float64)
    if len(frames) > 1:
        D[1:] = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    S = np.array([laplacian_var(f) for f in frames], dtype=np.float64)
    return L, D, S


def _box(a: np.ndarray, r: int) -> np.ndarray:
    """Mean over a (2r+1)^2 window, numpy-only, edges clamped by padding."""
    p = np.pad(a, r, mode="edge")
    c = p.cumsum(0).cumsum(1)
    c = np.pad(c, ((1, 0), (1, 0)))
    k = 2 * r + 1
    s = c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]
    return s / (k * k)


def ssim(a: np.ndarray, b: np.ndarray, r: int = 3) -> float:
    """Mean SSIM with a uniform window - "is this the same world" as one number."""
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu_a, mu_b = _box(a, r), _box(b, r)
    va = np.maximum(_box(a * a, r) - mu_a * mu_a, 0.0)
    vb = np.maximum(_box(b * b, r) - mu_b * mu_b, 0.0)
    cov = _box(a * b, r) - mu_a * mu_b
    num = (2 * mu_a * mu_b + c1) * (2 * cov + c2)
    den = (mu_a ** 2 + mu_b ** 2 + c1) * (va + vb + c2)
    return float((num / den).mean())


# --- classification (pure; the test drives this with synthetic series) -------

def _run_around(mask: np.ndarray, idx: int) -> tuple[int, int]:
    """The contiguous True run containing idx (half-open); (idx, idx) when idx is False."""
    if idx >= len(mask) or not mask[idx]:
        return idx, idx
    lo = idx
    while lo > 0 and mask[lo - 1]:
        lo -= 1
    hi = idx + 1
    while hi < len(mask) and mask[hi]:
        hi += 1
    return lo, hi


def _peak_index(D: np.ndarray, nominal: int, radius: int) -> int:
    lo, hi = max(1, nominal - radius), min(len(D), nominal + radius + 1)
    if hi <= lo:
        return min(nominal, len(D) - 1)
    return int(lo + np.argmax(D[lo:hi]))


@dataclass
class Measurement:
    kind: str
    reason: str
    peak_index: int
    duration_frames: int
    first_motion_frames: int
    motion_after_0_5s: float
    D_peak: float
    D_median: float
    L_before: float
    L_min: float
    L_after: float
    S_before: float
    S_min: float
    sim: float


def classify(L: np.ndarray, D: np.ndarray, S: np.ndarray, sim: float, fps: float,
             nominal: int | None = None) -> Measurement:
    """The rules, most specific mechanism first. `sim` = SSIM(t-0.5 s, t+0.5 s).

    dip        L excursion past 0.60x/1.60x the steady levels for >= 3 frames
    blur-zoom  S valley under 0.50x of BOTH steady levels for >= 2 frames
    dissolve   D elevated >= 4 frames, no frame > 3x the run mean, L monotone between levels
    hard-cut   D_peak > 6x the window median AND the transition spans one frame (no ramp)
    world-persists  D peak < 2x baseline and SSIM(t-0.5, t+0.5) >= 0.60: same background
    other      none of the above; the series stay in the csv for a human

    dip runs before blur-zoom because a frame that goes black has no detail either: the
    sharpness valley is a CONSEQUENCE of the dip, not a second mechanism (boundary 4).
    The steady levels are read from the window EDGES (+-0.5-0.8 s), never from frames next
    to the boundary, so a multi-frame transition cannot contaminate its own reference.
    """
    n = len(D)
    nominal = int(round(PRE_S * fps)) if nominal is None else nominal
    p = _peak_index(D, nominal, max(1, int(round(PEAK_SEARCH_S * fps))))
    guard = max(1, int(round(0.07 * fps)))                       # +-2 frames at 30 fps
    keep = np.ones(n, dtype=bool)
    keep[max(0, p - guard): p + guard + 1] = False
    keep[0] = False                                              # D[0] is undefined
    d_med = float(np.median(D[keep])) if keep.any() else 0.0
    base = max(d_med, D_FLOOR)

    e = min(EDGE_FRAMES, max(1, n // 6))
    l_before, l_after = float(L[1:1 + e].mean()), float(L[n - e:].mean())
    s_before, s_after = float(S[1:1 + e].mean()), float(S[n - e:].mean())

    # The transition span: frames carrying > 25 % of the peak change AND actually above the
    # still-frame baseline, so a static plate's noise peak never spans the whole window.
    lo, hi = _run_around((D > TRANSITION_FRAC * max(float(D[p]), 1e-6))
                         & (D > WORLD_PEAK_RATIO * base), p)
    valley = S < BLUR_VALLEY_FRAC * max(min(s_before, s_after), 1e-6)
    vlo, vhi = _run_around(valley, int(np.argmin(S[lo: hi + 2])) + lo)
    core = slice(max(0, min(lo, vlo) - 1), min(n, max(hi, vhi) + 1))
    l_min, l_max = float(L[core].min()), float(L[core].max())
    s_min = float(S[core].min())
    duration = max(hi - lo, vhi - vlo)

    settle = int(min(n, hi))
    while settle < n and D[settle] > SETTLE_RATIO * base:
        settle += 1
    first_motion = max(0, settle - hi)

    a, b = min(n - 1, p + int(round(0.1 * fps))), min(n, p + int(round(0.6 * fps)) + 1)
    motion_after = float(D[a:b].mean() / base) if b > a else 0.0

    kind, reason = _decide(L, D, S, sim, p, lo, hi, vlo, vhi, base, l_before, l_after,
                           l_min, l_max, s_before, s_after, s_min)
    return Measurement(kind, reason, p, int(duration), int(first_motion), round(motion_after, 3),
                       round(float(D[p]), 3), round(d_med, 3), round(l_before, 2), round(l_min, 2),
                       round(l_after, 2), round(s_before, 1), round(s_min, 1), round(sim, 3))


def _decide(L, D, S, sim, p, lo, hi, vlo, vhi, base, l_before, l_after,
            l_min, l_max, s_before, s_after, s_min) -> tuple[str, str]:
    # SSIM decides ONE rule, world-persists, where the D peak is too small to say anything on its
    # own. It is deliberately not a guard on dip or blur-zoom: the caller already asserts a shot
    # ended here, and an excursion that leaves the band between BOTH steady levels is an excursion
    # whatever the two plates look like. Boundaries 98 (fade to black, SSIM 0.62) and 26 (zoom
    # through, SSIM 0.61) are why - as a guard it only ever produced false negatives, because this
    # channel's plates are all cream backgrounds with one or two figures on them.
    for mask, word, extreme in ((L < DIP_DARK_FRAC * min(l_before, l_after), "dark", l_min),
                                (L > DIP_BRIGHT_FRAC * max(l_before, l_after), "light", l_max)):
        dlo, dhi = _run_around(mask, int(np.argmin(L) if word == "dark" else np.argmax(L)))
        if (dhi - dlo) >= DIP_MIN_FRAMES and dlo <= hi and dhi >= lo:
            return "dip", (f"L through {word} {extreme:.0f} for {dhi - dlo}f "
                           f"between steady {l_before:.0f} and {l_after:.0f}")

    if (vhi - vlo) >= BLUR_MIN_FRAMES:
        return "blur-zoom", (f"S valley {vhi - vlo}f down to {s_min:.0f} between steady "
                             f"{s_before:.0f} and {s_after:.0f}")

    run = D[lo:hi]
    if len(run) >= DISSOLVE_MIN_FRAMES and float(D[p]) <= DISSOLVE_DOMINANCE * float(run.mean()):
        mono = abs(l_after - l_before) < L_FLAT or _monotone(L[lo:hi])
        if mono:
            return "dissolve", (f"D elevated {len(run)}f, peak {D[p]:.1f} vs run mean "
                                f"{run.mean():.1f}, L {l_before:.0f}->{l_after:.0f}")

    if D[p] > HARD_PEAK_RATIO * base and (hi - lo) == 1:
        left = D[p - 1] if p >= 1 else 0.0
        right = D[p + 1] if p + 1 < len(D) else 0.0
        return "hard-cut", (f"one frame D {D[p]:.1f} = {D[p] / base:.0f}x median {base:.2f}, "
                            f"neighbours {left:.1f}/{right:.1f} = {max(left, right) / D[p]:.2f} of the peak")

    if D[p] < WORLD_PEAK_RATIO * base and sim >= SIM_SAME_WORLD:
        return "world-persists", f"D peak {D[p]:.2f} only {D[p] / base:.1f}x baseline, SSIM {sim:.2f}"

    return "other", (f"D peak {D[p]:.1f} ({D[p] / base:.1f}x), span {hi - lo}f, "
                     f"S {s_before:.0f}->{s_min:.0f}->{s_after:.0f}, SSIM {sim:.2f}")


def _monotone(seg: np.ndarray, tol: float = 2.0) -> bool:
    """Non-decreasing or non-increasing to within `tol` grey levels of backtracking."""
    d = np.diff(seg)
    return bool(d[d < 0].sum() > -tol or d[d > 0].sum() < tol)


# --- driver ------------------------------------------------------------------

def load_boundaries(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return [{"boundary": int(r["boundary"]), "t_s": float(r["t_s"]),
                 "at_gap": r.get("at_gap", ""), "gap_s": r.get("gap_s", "")}
                for r in csv.DictReader(fh)]


def measure_boundary(video: Path, row: dict, fps: float, height: int,
                     frames_out: Path | None = None) -> dict:
    t = row["t_s"]
    frames = decode_window(video, t - PRE_S, PRE_S + POST_S, height)
    L, D, S = series(frames)
    nominal = min(len(frames) - 1, int(round(PRE_S * fps)))
    half = int(round(0.5 * fps))
    a, b = max(0, nominal - half), min(len(frames) - 1, nominal + half)
    sim = ssim(frames[a], frames[b])
    m = classify(L, D, S, sim, fps, nominal=nominal)
    if frames_out is not None:
        _dump_frames(frames, frames_out / str(row["boundary"]), t, fps, L, D, S, m)
    return {**row, **asdict(m), "n_frames": len(frames),
            "L": [round(float(x), 2) for x in L], "D": [round(float(x), 3) for x in D],
            "S": [round(float(x), 1) for x in S]}


def _dump_frames(frames: np.ndarray, out: Path, t: float, fps: float,
                 L, D, S, m: Measurement) -> None:
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    for i, f in enumerate(frames):
        rel = (i - int(round(PRE_S * fps))) / fps
        Image.fromarray(f.astype(np.uint8), mode="L").save(out / f"{i:02d}_{rel:+.3f}s.png")
    (out / "series.json").write_text(json.dumps({
        "t_s": t, "fps": fps, "kind": m.kind, "reason": m.reason, "peak_index": m.peak_index,
        "L": [round(float(x), 2) for x in L], "D": [round(float(x), 3) for x in D],
        "S": [round(float(x), 1) for x in S], **asdict(m)}, indent=1), encoding="utf-8")


def write_csv(rows: list[dict], out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})
    return out


def summarise(rows: list[dict]) -> dict:
    """Shares and median shot length per kind. The shot that ENDS at boundary N runs from
    boundary N-1 (or 0.0) to N, so its length is the difference of the two times."""
    times = {r["boundary"]: r["t_s"] for r in rows}
    out: dict[str, dict] = {}
    for kind in KINDS:
        got = [r for r in rows if r["kind"] == kind]
        if not got:
            out[kind] = {"n": 0, "share": 0.0}
            continue
        lens = [round(r["t_s"] - times.get(r["boundary"] - 1, 0.0), 1) for r in got]
        out[kind] = {
            "n": len(got), "share": round(len(got) / len(rows), 3),
            "median_shot_s": round(float(np.median(lens)), 2),
            "median_first_motion_frames": round(float(np.median([r["first_motion_frames"] for r in got])), 1),
            "median_motion_after_0_5s": round(float(np.median([r["motion_after_0_5s"] for r in got])), 2),
            "boundaries": [r["boundary"] for r in got],
        }
    return {"n": len(rows), "kinds": out, "thresholds": thresholds()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--video", required=True)
    ap.add_argument("--boundaries", required=True)
    ap.add_argument("--out")
    ap.add_argument("--only", help="comma-separated boundary ids")
    ap.add_argument("--frames-out", help="write the decoded pngs + series.json per boundary here")
    ap.add_argument("--summary-json")
    ap.add_argument("--series-json")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--print-thresholds", action="store_true")
    args = ap.parse_args()

    if args.print_thresholds:
        for k, v in thresholds().items():
            print(f"{k:<24} {v}")
    video = Path(args.video)
    fps = probe_fps(video)
    height = 2 * round(714 * WIDTH / 1280 / 2)
    rows_in = load_boundaries(Path(args.boundaries))
    if args.only:
        want = {int(x) for x in args.only.split(",")}
        rows_in = [r for r in rows_in if r["boundary"] in want]
    frames_out = Path(args.frames_out) if args.frames_out else None
    print(f"video={video.name} fps={fps:g} window=[-{PRE_S},+{POST_S}]s scale={WIDTH}x{height} boundaries={len(rows_in)}")

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        rows = list(ex.map(lambda r: measure_boundary(video, r, fps, height, frames_out), rows_in))
    rows.sort(key=lambda r: r["boundary"])
    elapsed = time.time() - t0

    for r in rows:
        print(f"  {r['boundary']:>3} t={r['t_s']:>7.1f}  {r['kind']:<14} {r['reason']}")
    if args.out:
        print(f"wrote {write_csv(rows, Path(args.out))}")
    summary = summarise(rows)
    if args.summary_json:
        Path(args.summary_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.summary_json).write_text(json.dumps(summary, indent=1), encoding="utf-8")
    if args.series_json:
        Path(args.series_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.series_json).write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for kind, s in summary["kinds"].items():
        if s["n"]:
            print(f"{kind:<16} {s['n']:>3}  {s['share'] * 100:5.1f}%  median shot {s['median_shot_s']}s")
    print(f"{len(rows)} boundaries in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
