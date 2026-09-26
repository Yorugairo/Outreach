"""Measure a line chart's BLOOM and its SQUINT read off a frame's pixels (P69 T37b, E99 s117 / s120).

The operator, on our solo beside Bravos JPN 05:20 / 05:23.5 (E99 s117): Bravos's primary line is "a higher
vibrancy/contrast/electricity than we do ... then fades theirs to a higher contrast", and (s120), on the same sheet
shrunk small: "bravos chart still reads with its text/font, ours really doesn't". Both are MEASURED, never eyeballed:
this tool reads the numbers off the Bravos frames first, and the SAME tool reads ours (thresholds from the
reference, E38 - `content/video_engine/assets/bravos-line-bloom.v1.json` is the band; nothing here is fitted to ours).

ONE FRAME, ONE LIT LINE. Given a frame (PNG/JPG), the lit line's ink (a hex; `#FFFFFF` for a white line) and the
plot box (the plot's inner rectangle, legend strip and axes outside it), it reports:

  stroke     the lit stroke's width (2 x the median distance-to-edge along its skeleton)
  core       the peak along the stroke: relative luminance (p98), CIE L* and the HSV saturation there - a near-white
             hot core is a high L* at a LOW saturation
  ink        the stroke's own ink saturation (HSV S, median, the core excluded) and Lab chroma C*
  halo       the ring profile outside the stroke edge: the median luma of every ring at distance d, less the plot's
             ground; `r50` is where it falls to half its value at the edge (px, and as a multiple of the stroke's
             width), `edge` is the edge's excess as a share of the core's, `reach10` where it falls to 10 % of the core's
  lit/muted  the lit stroke's p90 luminance against every OTHER visible mark in the plot (the other series' strokes
             and ghosts; long straight rules and the lit line's own halo zone excluded): the WCAG-style ratio
             (Y1 + .05) / (Y2 + .05) and the ratio of their luma excess over the ground
  squint     the frame downsampled to 320 px wide (s120): the lit line's share of the plot's visible contrast
             (sum |luma - ground| inside its halo zone over the plot's), the title's and the named label's cap
             height at that width (measured at the frame's own size on its text box, then scaled), and the words
             on the plot (a count the caller supplies - `--words`, our DOM's text elements - or tesseract's, when
             `pytesseract` and its binary exist; the source is recorded)

Every px number is also given at the 1920-wide stage (`*_px1080`), so a 512 px Bravos frame and a 1920 px render
compare. Luma is Rec.709 on the sRGB-coded values, 0-255 (the Bravos spec's "lum",
`docs/research/bravos-style/mlib.py`); relative luminance is WCAG's.

THE SQUINT GATE'S READ (P71 T7, E99 s126: M48 FAILs, and reads the captions too). `--build <dir>` renders a built
player through the frozen-frames capture path and writes `<dir>/squint.json` for gate_motion_density's M48: every HELD
page (the timeline's own clocks: a gap between its builds, hand-overs and undraw, read at its middle) on the PAGE layer
alone (`?layers=page`) - its lit share at the band's 1024 px, its title's and its lit series' name's cap glyph by glyph
at 320 px wide, its words off the player's DOM - and every caption page on the whole frame once its last word is
written - its fill's cap and its WCAG contrast at 320 px (`caption_read`). The thresholds are the reference's:
`squint_band` in the band file (Bravos's five frames through `squint_gate_read`) and
`content/video_engine/assets/caption-squint-floor.v1.json` (Wealth Logic's burned-in strip; the shorts' strip has no
reference on disk yet).

    python measure_line_bloom.py FRAME --ink "#34F5C5" --box 150,250,1098,820 [--title-box ..] [--label-box ..] [--words N]
    python measure_line_bloom.py --band content/video_engine/assets/bravos-line-bloom.v1.json --check
    python measure_line_bloom.py FRAME --fill --ink "#FF8A4C" --box x0,y0,x1,y1            # P72 T10: a filled mark's halo
    python measure_line_bloom.py FRAME --spread --ink "#971E37" --box x0,y0,x1,y1 [--end right]   # P72 T49: a spread's halo
    python measure_line_bloom.py --caption-floor content/video_engine/assets/caption-squint-floor.v1.json --check
    python measure_line_bloom.py --build <build-dir> [--timeline NAME] [--at T ...] [--frames DIR]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

STAGE_W = 1920          # every px number is also reported at the 1920-wide stage
SQUINT_W = 320          # s120 / E67 Apply 4: "a page's landing frame must read at 320 px wide"
HUE_TOL = 24.0          # degrees: a stroke pixel's hue within this of the ink's
SAT_FLOOR = 0.45        # ... and at least this share of the ink's own saturation
VAL_FLOOR = 0.62        # ... and this share of its value (a muted history at 0.45 falls under it)
NEUTRAL_SAT = 0.18      # an ink under this saturation is a WHITE line: its stroke is bright and unsaturated
WHITE_VAL, WHITE_SAT = 0.80, 0.32
CORE_VAL = 0.86         # a hot-core pixel: this bright, inside the ink's own reach
RING_MAX_1080 = 96      # the halo profile's reach, stage px (Bravos's hero bloom is gone at ~82, SPEC (b))
MARK_LUMA = 12.0        # a visible mark: this much luma over the ground (JPEG noise is ~3)
RULE_SHARE = 0.35       # a row / column of marks longer than this share of the box is a rule, not a series
SPECK_PX = 6            # connected marks smaller than this are noise
BAND_TOL = 0.08         # --check: a recorded number reproduces within 8 % (or the absolute floor below)
BAND_ABS = {"core_sat": 0.03, "ink_sat": 0.03, "halo_edge": 0.03, "lit_share": 0.03}


def load_rgb(path: str | Path, at_width: int | None = None) -> np.ndarray:
    """The frame as float RGB; `at_width` first downsamples it (LANCZOS) - ours read at a Bravos frame's own width."""
    im = Image.open(path).convert("RGB")
    if at_width and at_width != im.width:
        im = im.resize((at_width, round(im.height * at_width / im.width)), Image.LANCZOS)
    return np.asarray(im).astype(np.float64) / 255.0


def luma(rgb: np.ndarray) -> np.ndarray:
    return (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) * 255.0


def rel_lum(rgb: np.ndarray) -> np.ndarray:
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def lstar(y: float) -> float:
    return float(116.0 * np.cbrt(y) - 16.0 if y > 216 / 24389 else y * 24389 / 27)


def hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mx, mn = rgb.max(axis=-1), rgb.min(axis=-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-9), 0.0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    dd = np.maximum(d, 1e-9)
    h = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60.0
    return np.where(d > 0, h, 0.0), s, mx


def lab_chroma(rgb: np.ndarray) -> np.ndarray:
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = lin @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.hypot(500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2]))


def hex_rgb(hx: str) -> np.ndarray:
    h = hx.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError(f"an ink is #RRGGBB, not {hx!r}")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64) / 255.0


def _box_mask(shape, box) -> np.ndarray:
    x0, y0, x1, y1 = (int(v) for v in box)
    m = np.zeros(shape, dtype=bool)
    m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
    return m


def _clean(mask: np.ndarray, min_px: int) -> np.ndarray:
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if not n:
        return mask
    sizes = ndimage.sum(mask, lab, index=np.arange(1, n + 1))
    keep = np.zeros(n + 1, dtype=bool)
    keep[1:] = sizes >= min_px
    return keep[lab]


def stroke_mask(rgb: np.ndarray, ink: str, box, exclude=()) -> tuple[np.ndarray, np.ndarray]:
    """The lit stroke (ink + hot core) and its ink-only part, inside the box and outside every exclude box."""
    h, s, v = hsv(rgb)
    ih, is_, iv = (float(c.ravel()[0]) for c in hsv(hex_rgb(ink)[None, None, :]))
    inside = _box_mask(s.shape, box)
    for ex in exclude:
        inside &= ~_box_mask(s.shape, ex)
    scale = rgb.shape[1] / STAGE_W
    if is_ < NEUTRAL_SAT:                      # a WHITE line: bright and unsaturated is the stroke
        ink_px = (v >= WHITE_VAL * max(iv, 0.9)) & (s <= WHITE_SAT) & inside
        ink_px = _clean(ink_px, SPECK_PX)
        return ink_px, ink_px
    dh = np.abs((h - ih + 180.0) % 360.0 - 180.0)
    ink_px = (dh <= HUE_TOL) & (s >= SAT_FLOOR * is_) & (v >= VAL_FLOOR * iv) & inside
    ink_px = _clean(ink_px, SPECK_PX)
    reach = ndimage.binary_dilation(ink_px, iterations=max(1, round(3 * scale / 0.55)))
    core = (v >= CORE_VAL) & (s < SAT_FLOOR * is_) & reach & inside
    return ink_px | core, ink_px


def stroke_width(stroke: np.ndarray) -> float:
    if not stroke.any():
        return 0.0
    dist = ndimage.distance_transform_edt(stroke)
    sk = skeletonize(stroke)
    vals = dist[sk] if sk.any() else dist[stroke]
    return float(2.0 * np.median(vals))


def ground_luma(lu: np.ndarray, box_m: np.ndarray, far: np.ndarray) -> float:
    zone = box_m & far
    return float(np.median(lu[zone] if zone.any() else lu[box_m]))


def halo_profile(lu: np.ndarray, stroke: np.ndarray, box_m: np.ndarray, ring_max: int) -> tuple[list[float], float]:
    """The median luma of each ring 1..ring_max px outside the stroke, less the ground; and the ground."""
    dist = ndimage.distance_transform_edt(~stroke)
    far = dist > ring_max
    g = ground_luma(lu, box_m, far)
    prof = []
    for d in range(1, ring_max + 1):
        ring = box_m & (dist > d - 1) & (dist <= d)
        prof.append(float(np.median(lu[ring]) - g) if ring.any() else 0.0)
    return prof, g


def _cross(prof: list[float], level: float) -> float:
    """The distance (px outside the edge, interpolated) where the profile - prof[0] at 1 px - first falls to `level`."""
    if prof[0] <= level:
        return 1.0
    for i in range(1, len(prof)):
        if prof[i] <= level:
            a, b = prof[i - 1], prof[i]
            return float(i + (a - level) / (a - b) if a != b else i + 1)
    return float(len(prof))


def muted_marks(lu: np.ndarray, box_m: np.ndarray, lit_zone: np.ndarray, g: float) -> np.ndarray:
    marks = box_m & ~lit_zone & (lu > g + MARK_LUMA)
    ys, xs = np.nonzero(box_m)
    bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
    rows = marks.sum(axis=1) > RULE_SHARE * bw
    cols = marks.sum(axis=0) > RULE_SHARE * bh
    marks[rows, :] = False
    marks[:, cols] = False
    return _clean(marks, SPECK_PX)


def cap_height(lu: np.ndarray, box) -> float | None:
    """The text's cap (ascender) band in a box: the first row at 8 % of the densest row to the last at 30 %."""
    x0, y0, x1, y1 = (int(v) for v in box)
    crop = lu[y0:y1 + 1, x0:x1 + 1]
    if crop.size == 0:
        return None
    ground = float(np.median(np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])))
    diff = np.abs(crop - ground)
    thr = max(18.0, 0.4 * float(np.percentile(diff, 99.5)))
    counts = (diff > thr).sum(axis=1)
    if counts.max() == 0:
        return None
    top = int(np.argmax(counts >= 0.08 * counts.max()))
    base = int(len(counts) - 1 - np.argmax(counts[::-1] >= 0.30 * counts.max()))
    return float(base - top + 1)


TITLE_COVER = 0.5                 # a text pixel: at least half the ink's excess over the ground (an antialiased edge)
TITLE_X_LETTERS = set("acemnorsuvwxz")   # the x-height letters: no ascender, no descender, no dot (the round ones overshoot ~5 %)


def _glyph_boxes(cov: np.ndarray) -> list[list[float]]:
    """Each glyph's [x0, x1, top, bottom] in the crop, left to right; a dot over its stem is one glyph. The top and
    bottom are sub-pixel: a flat edge covers the row just outside it by the fraction it reaches into it."""
    lab, _ = ndimage.label(cov >= TITLE_COVER)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        ys, xs = sl
        if (lab[sl] == i).sum() < 3:
            continue
        cs = slice(xs.start, xs.stop)
        above = float(cov[ys.start - 1, cs].max()) if ys.start > 0 else 0.0
        below = float(cov[ys.stop, cs].max()) if ys.stop < cov.shape[0] else 0.0
        out.append([xs.start, xs.stop, ys.start - (above if above < TITLE_COVER else 0.0),
                    ys.stop + (below if below < TITLE_COVER else 0.0)])
    out.sort()
    merged: list[list[float]] = []
    for g in out:
        if merged:
            p = merged[-1]
            if min(p[1], g[1]) - max(p[0], g[0]) >= 0.5 * min(g[1] - g[0], p[1] - p[0]):
                merged[-1] = [min(p[0], g[0]), max(p[1], g[1]), min(p[2], g[2]), max(p[3], g[3])]
                continue
        merged.append(list(g))
    return merged


def _map_glyphs(glyphs: list[list[float]], text: str) -> tuple[list[tuple[float, str]], str]:
    """(height, character) pairs for the glyphs that map onto `text`. The whole line when the counts agree
    ("glyphs"); else WORD BY WORD - the line split at its len(words) - 1 widest gaps, a word kept when its glyph count
    is its letter count ("words k/n": a hand face's joined pair or a stray mark costs only its own word)."""
    chars = text.replace(" ", "")
    if glyphs and len(glyphs) == len(chars):
        return [(g[3] - g[2], c) for g, c in zip(glyphs, chars)], "glyphs"
    words = text.split()
    if len(glyphs) < 2 or len(words) < 2:
        return [], "cluster"
    gaps = sorted(range(len(glyphs) - 1), key=lambda i: glyphs[i + 1][0] - glyphs[i][1], reverse=True)
    cuts = sorted(gaps[:len(words) - 1])
    runs, start = [], 0
    for c in cuts:
        runs.append(glyphs[start:c + 1])
        start = c + 1
    runs.append(glyphs[start:])
    pairs, kept = [], 0
    for run, word in zip(runs, words):
        if len(run) == len(word):
            pairs += [(g[3] - g[2], ch) for g, ch in zip(run, word)]
            kept += 1
    return (pairs, f"words {kept}/{len(words)}") if kept else ([], "cluster")


def _caps_of(glyphs: list[list[float]], text: str) -> tuple[list[float], list[float], str]:
    """(cap heights, x heights, method): the capitals and the x letters of the glyphs that map onto `text`; with no
    capital mapped, the TALL CLUSTER - the glyphs standing on the baseline at >= 85 % of their p90 (capitals and
    ascenders; an all-caps line is all of them)."""
    pairs, method = _map_glyphs(glyphs, text)
    caps = [hh for hh, c in pairs if c.isupper() and c not in "QJ"]
    xs = [hh for hh, c in pairs if c in TITLE_X_LETTERS]
    if pairs and caps:
        return caps, xs, method
    bots = np.array([g[3] for g in glyphs])
    base = float(np.median(bots)) if glyphs else 0.0
    on = np.array([g[3] - g[2] for g, b in zip(glyphs, bots) if abs(b - base) <= 1.5]) if glyphs else np.array([])
    top = float(np.percentile(on, 90)) if on.size else 0.0
    return ([float(v) for v in on if v >= 0.85 * top], [float(v) for v in on if 0.5 * top <= v < 0.85 * top],
            "cluster")


def title_size(frame: str | Path, box, text: str) -> dict:
    """E99 s122 (P69 T37c): a title's size read GLYPH BY GLYPH at the frame's own resolution - the capitals' height,
    the x-height, the stroke - each also as a share of the frame height (the one size that compares a 512, a 1024
    and a 1920 px frame). The glyphs map one to one onto `text` (spaces dropped): the cap is the median height of its
    capitals, the x-height of its x letters. A title whose glyphs do not map (touching letters, a stray mark) falls
    back to word-by-word mapping, then to the tall cluster (glyphs at least 85 % of the tallest standing on the
    baseline - capitals AND ascenders), and says which in `method`."""
    rgb = load_rgb(frame)
    h = rgb.shape[0]
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    lu = luma(rgb)[y0:y1 + 1, x0:x1 + 1]
    ground = float(np.median(np.concatenate([lu[0], lu[-1], lu[:, 0], lu[:, -1]])))
    diff = np.abs(lu - ground)
    cov = np.clip(diff / max(float(np.percentile(diff, 99.5)), 1e-6), 0.0, 1.0)
    glyphs = _glyph_boxes(cov)
    caps, xs, method = _caps_of(glyphs, text)
    mask = cov >= TITLE_COVER
    skel = skeletonize(mask)
    stroke = 2.0 * float(np.median(ndimage.distance_transform_edt(mask)[skel])) if skel.any() else None
    cap = float(np.median(caps)) if caps else None
    xh = float(np.median(xs)) if xs else None
    frac = lambda v: round(v / h, 5) if v else None  # noqa: E731
    return {"frame_h": h, "method": method, "chars": len(text), "glyphs": len(glyphs), "capitals": len(caps),
            "cap_px": round(cap, 2) if cap else None, "cap_frac": frac(cap),
            "cap_px1080": round(cap / h * 1080, 2) if cap else None,
            "x_px": round(xh, 2) if xh else None, "x_frac": frac(xh),
            "stroke_px": round(stroke, 2) if stroke else None, "stroke_frac": frac(stroke)}


TITLE_RING_1080 = 40              # the title halo's reach, stage px at 1080 high (a line's is 96: text is smaller)
TITLE_GLOW_FROM_1080 = 3          # rings from here out are GLOW - rings 1-2 hold the glyph's own antialiased edge
TITLE_GLOW_TO_1080 = 12


def title_halo(frame: str | Path, box, *, ring_1080: int = TITLE_RING_1080) -> dict:
    """E99 s122 amended (P69 T37c): the s117 halo read, in a TITLE mode. The text is the title box's pixels at >= half
    the ink's excess; the rings are 1..ring px outside it (px at 1080 high, scaled to the frame), inside the box grown
    by the ring's reach plus 8; the ground is the median of that grown box beyond the reach. Every OTHER mark in the
    grown box - a bright component that does not touch the text (a logo, a legend, a sub) - is left out of both; a
    glow touches its text, so it stays in. Reported as the line read is: `r50` (where the profile halves from ring 1),
    `edge` (ring 1's excess over the text's p90), `area` (sum of the profile, luma.px at 1080), `reach10`; and the
    title's own number, `glow` - the mean excess of rings 3..12 px, past the glyph's antialiased edge (0 = no halo)."""
    rgb = load_rgb(frame)
    h, w = rgb.shape[:2]
    k = h / 1080.0
    lu = luma(rgb)
    x0, y0, x1, y1 = (int(round(v)) for v in box)
    crop = lu[y0:y1 + 1, x0:x1 + 1]
    g0 = float(np.median(np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])))
    diff = np.abs(crop - g0)
    text = np.zeros(lu.shape, dtype=bool)
    text[y0:y1 + 1, x0:x1 + 1] = diff >= TITLE_COVER * max(float(np.percentile(diff, 99.5)), 1e-6)
    reach = max(4, int(round(ring_1080 * k)))
    pad = reach + max(2, int(round(8 * k)))
    grown = _box_mask(lu.shape, [x0 - pad, y0 - pad, x1 + pad, y1 + pad])
    marks = grown & (np.abs(lu - g0) > MARK_LUMA) & ~text
    lab, n = ndimage.label(marks | text, structure=np.ones((3, 3)))
    touching = set(np.unique(lab[ndimage.binary_dilation(text, iterations=2)])) - {0}
    other = marks & ~np.isin(lab, list(touching))
    keep = grown & ~ndimage.binary_dilation(other, iterations=max(1, int(round(2 * k))))
    dist = ndimage.distance_transform_edt(~text)
    far = keep & (dist > reach)
    g = float(np.median(lu[far])) if far.any() else g0
    prof = []
    for d in range(1, reach + 1):
        ring = keep & (dist > d - 1) & (dist <= d)
        prof.append(float(np.mean(lu[ring]) - g) if ring.any() else 0.0)
    core = float(np.percentile(lu[text], 90)) - g
    a = max(2, int(round(TITLE_GLOW_FROM_1080 * k)))            # never ring 1: at 288 px high that IS the antialiased edge
    b = max(a + 1, int(round(TITLE_GLOW_TO_1080 * k)))
    glow = float(np.mean(prof[a - 1:b])) if prof else 0.0
    k1080 = 1.0 / k
    return {"frame_h": h, "ground_luma": round(g, 2), "text_excess": round(core, 2),
            "halo_edge": round(prof[0] / core, 3) if core > 0 else 0.0,
            "halo_r50_px1080": round(_cross(prof, 0.5 * prof[0]) * k1080, 2),
            "halo_reach10_px1080": round(_cross(prof, 0.10 * core) * k1080, 2),
            "halo_area_1080": round(float(sum(max(v, 0.0) for v in prof)) * k1080, 1),
            "glow_3_12": round(glow, 2),
            "halo_profile": [round(v, 2) for v in prof]}


CAPTION_PAD = 0.25     # the contrast box: the caption's glyphs grown by this share of its cap, each side
CAP_PROXIES = set("bdfhkl0123456789")   # with no capital on the line: the ascenders and the figures stand at the cap
GLYPH_IN_BOX = (0.3, 0.95)   # a word's glyph stands between these shares of its DOM box's height (the line box, ~1.24 em);
                             # a fragment the shadow cut off or a fill run into a bright ground is a misread, not a letter


def _fill_glyphs(lu: np.ndarray) -> list[list[float]]:
    """A caption's letters are its FILL: the pixels at least half-way from its dark (p5, the outline / shadow) to its
    light (p97), less every fill region touching the box's edge (the ground), read glyph by glyph (`_glyph_boxes`)."""
    lo, hi = float(np.percentile(lu, 5)), float(np.percentile(lu, 97))
    if hi - lo < MARK_LUMA:
        return []
    cov = np.clip((lu - lo) / (hi - lo), 0.0, 1.0)
    lab, _ = ndimage.label(cov >= TITLE_COVER)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    return _glyph_boxes(np.where(np.isin(lab, edge[edge > 0]), 0.0, cov))


def _crop(lu: np.ndarray, box) -> tuple[np.ndarray, int, int]:
    h, w = lu.shape
    x0, y0 = max(0, int(round(box[0]))), max(0, int(round(box[1])))
    x1, y1 = min(w - 1, int(round(box[2]))), min(h - 1, int(round(box[3])))
    return lu[y0:y1 + 1, x0:x1 + 1], x0, y0


def _word_caps(lu: np.ndarray, words) -> tuple[list[float], list[list[float]], str]:
    """Our captions carry their words' boxes (the player's DOM): each word is read on its own (a merged pair costs
    only its word), mapped one glyph to one letter, and a word whose letters stand outside GLYPH_IN_BOX of its box is
    dropped. The cap is the line's capitals' height - only those standing on the line's BASELINE (the median bottom of
    its non-descending letters; a capital fused with ink under the strip - a page's source line - is not one) - or, on
    a line with no capital, its ascenders' and figures' (CAP_PROXIES). A line with neither has no cap to read (None,
    never its x-height)."""
    mapped, boxes, n = [], [], 0
    for box, text in words:
        crop, x0, y0 = _crop(lu, box)
        bh = float(box[3] - box[1])
        gl = _fill_glyphs(crop) if crop.size else []
        boxes += [[x0 + g[0], x0 + g[1], y0 + g[2], y0 + g[3]] for g in gl]
        chars = str(text).replace(" ", "")
        if gl and len(gl) == len(chars) and all(GLYPH_IN_BOX[0] * bh <= g[3] - g[2] <= GLYPH_IN_BOX[1] * bh
                                                for g, c in zip(gl, chars) if c.isalnum()):
            n += 1
            mapped += [(y0 + g[3], g[3] - g[2], c) for g, c in zip(gl, chars) if c.isalnum()]
    base = float(np.median([bt for bt, _h, c in mapped if c not in "gjpqyQJ"])) if mapped else 0.0
    tol = max(1.5, 0.06 * float(np.median([h for _b, h, _c in mapped]))) if mapped else 0.0
    on = [(h, c) for bt, h, c in mapped if abs(bt - base) <= tol]
    caps = [h for h, c in on if c.isupper() and c not in "QJ"]
    proxies = [h for h, c in on if c in CAP_PROXIES]
    method = f"words {n}/{len(words)}" + ("" if caps else " (ascenders / figures)" if proxies else " (no cap letter)")
    return caps or proxies, boxes, method


def caption_read(frame: str | Path, box, text: str = "", *, words=None, width: int = SQUINT_W) -> dict:
    """E99 s126 (P71 T7): a CAPTION line's legibility at the gate's width. A caption is LIGHT ink held off its ground
    by an outline or a shadow (Wealth Logic's white caps in a black stroke; ours cream in a dark text-shadow), so its
    letters are its FILL (`_fill_glyphs`). The cap is read glyph by glyph at the frame's own size and given at `width`:
    word by word when the words' boxes are known (`_word_caps` - ours, off the DOM), else over the line (`_caps_of`:
    the capitals of `text`, else the tall cluster - the reference's all-caps strip is all of it). The contrast is
    WCAG's ratio of the p90 and p10 relative luminance inside the glyphs' box (grown by CAPTION_PAD of the cap) on the
    frame DOWNSAMPLED to `width` - what the thumbnail keeps."""
    rgb = load_rgb(frame)
    h, w = rgb.shape[:2]
    lu = luma(rgb)
    if words:
        caps, glyphs, method = _word_caps(lu, words)
    else:
        crop, x0, y0 = _crop(lu, box)
        gl = _fill_glyphs(crop)
        caps, _xs, method = _caps_of(gl, text)
        glyphs = [[x0 + g[0], x0 + g[1], y0 + g[2], y0 + g[3]] for g in gl]
    cap = float(np.median(caps)) if caps else None
    k = width / w
    if glyphs:
        pad = CAPTION_PAD * (cap or 0.0)
        gb = [min(g[0] for g in glyphs) - pad, min(g[2] for g in glyphs) - pad,
              max(g[1] for g in glyphs) + pad, max(g[3] for g in glyphs) + pad]
    else:
        gb = [box[0], box[1], box[2] + 1, box[3] + 1]
    small = load_rgb(frame, width)
    sy0, sy1 = max(0, int(np.floor(gb[1] * k))), min(small.shape[0], int(np.ceil(gb[3] * k)))
    sx0, sx1 = max(0, int(np.floor(gb[0] * k))), min(small.shape[1], int(np.ceil(gb[2] * k)))
    yl = rel_lum(small[sy0:sy1, sx0:sx1]) if sy1 > sy0 and sx1 > sx0 else np.zeros(1)
    contrast = (float(np.percentile(yl, 90)) + 0.05) / (float(np.percentile(yl, 10)) + 0.05)
    return {"frame_h": h, "frame_w": w, "width": width, "method": method if glyphs else "none",
            "glyphs": len(glyphs), "capitals": len(caps),
            "cap_px": round(cap * k, 3) if cap else None, "cap_frac": round(cap / h, 5) if cap else None,
            "cap_px1080": round(cap / h * 1080, 2) if cap else None, "contrast": round(contrast, 2),
            "box_gate": [sx0, sy0, sx1, sy1]}


def word_count(texts) -> int:
    """s120 (3): the WORDS on a plot - every token carrying at least two letters (a name, "(LHS)", "S&P"); a figure,
    a percentage or a tick ("240%", "$1.2T", "2000") is not a word. Bravos's hand counts (the band's `plot_words`)
    are the legend rows, read by the same rule."""
    return sum(1 for t in texts for tok in str(t).split() if sum(c.isalpha() for c in tok) >= 2)


def ocr_words(path: str | Path, box) -> int | None:
    """Words with a letter inside the box, by tesseract - only when pytesseract and its binary exist."""
    try:
        import pytesseract  # noqa: PLC0415 - optional: the repo does not require OCR
    except ImportError:
        return None
    exe = shutil.which("tesseract") or next((p for p in ("C:/Program Files/Tesseract-OCR/tesseract.exe",)
                                              if Path(p).exists()), None)
    if not exe:
        return None
    pytesseract.pytesseract.tesseract_cmd = exe
    im = Image.open(path).convert("L").crop(tuple(int(v) for v in box))
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    words = pytesseract.image_to_string(im).split()
    return sum(1 for w in words if any(c.isalpha() for c in w) and len(w.strip("()[]|.,:;")) >= 2)


def squint(rgb: np.ndarray, box, lit_zone: np.ndarray, g: float, width: int = SQUINT_W) -> float:
    """The lit line's share of the plot's visible contrast at 320 px wide (P72 T10: a fill's at the 256 px thumbnail)."""
    h, w = rgb.shape[:2]
    sh = round(h * width / w)
    small = np.asarray(Image.fromarray((rgb * 255).round().astype(np.uint8)).resize((width, sh), Image.LANCZOS))
    lu = luma(small.astype(np.float64) / 255.0)
    zone = np.asarray(Image.fromarray(lit_zone.astype(np.float32)).resize((width, sh), Image.BOX))
    k = width / w
    sbox = _box_mask(lu.shape, [box[0] * k, box[1] * k, box[2] * k, box[3] * k])
    c = np.abs(lu - g) * sbox
    tot = float(c.sum())
    return float((c * np.clip(zone, 0, 1)).sum() / tot) if tot > 0 else 0.0


def measure(frame: str | Path, ink: str, box, *, exclude=(), title_box=None, label_box=None,
            words: int | None = None, words_box=None, at_width: int | None = None) -> dict:
    """Every number for one lit line. Boxes are in the frame's OWN px; `at_width` scales them with the frame."""
    native_w = Image.open(frame).width
    rgb = load_rgb(frame, at_width)
    h, w = rgb.shape[:2]
    ks = w / native_w
    sc = lambda b: [v * ks for v in b] if b is not None else None  # noqa: E731
    box, title_box, label_box = sc(box), sc(title_box), sc(label_box)
    exclude = [sc(e) for e in exclude]
    k1080 = STAGE_W / w
    box_m = _box_mask((h, w), box)
    for ex in exclude:
        box_m &= ~_box_mask((h, w), ex)
    stroke, ink_px = stroke_mask(rgb, ink, box, exclude)
    if not stroke.any():
        raise ValueError(f"{frame}: no stroke of ink {ink} inside the box {box}")
    lu, yl = luma(rgb), rel_lum(rgb)
    _, sat, _ = hsv(rgb)
    ring_max = max(8, round(RING_MAX_1080 / k1080))
    prof, g = halo_profile(lu, stroke, box_m, ring_max)
    width = stroke_width(stroke)
    core_y = float(np.percentile(yl[stroke], 98))
    top = stroke & (yl >= np.percentile(yl[stroke], 95))
    core_luma = float(np.percentile(lu[stroke], 98)) - g
    r50 = _cross(prof, 0.5 * prof[0])
    reach10 = _cross(prof, 0.10 * core_luma)
    zone = ndimage.binary_dilation(stroke, iterations=max(1, int(round(reach10)) + 1))
    body = ink_px & ~top if (ink_px & ~top).any() else ink_px
    marks = muted_marks(lu, box_m, zone, g)
    lit_y = float(np.percentile(yl[stroke], 90))
    lit_l = float(np.percentile(lu[stroke], 90))
    out = {
        "frame": str(frame).replace("\\", "/"), "size": [w, h], "at_width": w, "ink": ink.upper(), "box": [round(v, 1) for v in box],
        "ground_luma": round(g, 2),
        "stroke_px": round(width, 2), "stroke_px1080": round(width * k1080, 2),
        "core_lum": round(core_y, 4), "core_L": round(lstar(core_y), 2), "core_sat": round(float(np.median(sat[top])), 3),
        "ink_sat": round(float(np.median(sat[body])), 3), "ink_chroma": round(float(np.median(lab_chroma(rgb)[body])), 2),
        "halo_edge": round(prof[0] / core_luma, 3) if core_luma > 0 else 0.0,
        "halo_r50_px": round(r50, 2), "halo_r50_px1080": round(r50 * k1080, 2),
        "halo_r50_x_stroke": round(r50 / width, 2) if width else None,
        "halo_reach10_px1080": round(reach10 * k1080, 2),
        "halo_area_1080": round(float(sum(max(v, 0.0) for v in prof)) * k1080, 1),
        "halo_profile": [round(v, 1) for v in prof[:ring_max]],
        "lit_lum": round(lit_y, 4), "muted_lum": None, "lit_muted_ratio": None, "lit_muted_excess": None,
        "muted_px": int(marks.sum()),
    }
    if marks.sum() >= SPECK_PX * 4:
        mut_y = float(np.percentile(yl[marks], 90))
        mut_l = float(np.percentile(lu[marks], 90))
        out.update(muted_lum=round(mut_y, 4), lit_muted_ratio=round((lit_y + 0.05) / (mut_y + 0.05), 2),
                   lit_muted_excess=round((lit_l - g) / max(mut_l - g, 1e-6), 2))
    k320 = SQUINT_W / w
    tcap = cap_height(lu, title_box) if title_box else None
    lcap = cap_height(lu, label_box) if label_box else None
    src = "given" if words is not None else None
    if words is None and words_box is not None:
        words = ocr_words(frame, words_box)
        src = "ocr" if words is not None else None
    out["squint"] = {"width": SQUINT_W, "lit_share": round(squint(rgb, box, zone, g), 3),
                     "title_cap_px": round(tcap * k320, 2) if tcap else None,
                     "label_cap_px": round(lcap * k320, 2) if lcap else None,
                     "plot_words": words, "plot_words_source": src}
    return out


def _args_of(entry: dict) -> dict:
    return {"exclude": entry.get("exclude", ()), "title_box": entry.get("title_box"),
            "label_box": entry.get("label_box"), "words": entry.get("plot_words"), "words_box": None}


def resolve(frame: str, root: Path) -> Path:
    p = Path(frame)
    return p if p.is_absolute() else root / p


def check_band(band_path: Path, root: Path) -> list[str]:
    """Re-measure every recorded frame; a number that no longer reproduces is a finding."""
    band = json.loads(band_path.read_text(encoding="utf-8"))
    bad = []
    for e in band["frames"]:
        path = resolve(e["frame"], root)
        if not path.exists():
            bad.append(f"{e['id']}: frame not on disk ({path})")
            continue
        got = measure(path, e["ink"], e["box"], **_args_of(e))
        flat = {**got, **got["squint"]}
        for key, want in e["measured"].items():
            have = flat.get(key)
            if want is None or have is None:
                if want != have:
                    bad.append(f"{e['id']}.{key}: recorded {want}, measured {have}")
                continue
            tol = max(BAND_TOL * abs(want), BAND_ABS.get(key, 0.0), 0.05)
            if abs(have - want) > tol:
                bad.append(f"{e['id']}.{key}: recorded {want}, measured {have} (tol {tol:.3f})")
    return bad


# ---- P72 T10 (E99 s130 (1)): a FILLED mark's halo - a gauge's fill, a lit bar ------------------------------------
# The ruling: "a fill gauge's fill and bars (the lit / primary ones) carry an emissive halo in their own ink, measured
# off Bravos's fills first". A fill has no stroke and no core: what glows is its EDGE. The read is the halo ACROSS the
# fill's long edges - the two sides of a standing bar, the top and bottom of a lying one - row by row over the middle of
# its length (FILL_SPAN), so a capsule's track, a callout's dot and a zero rule at its ends never enter it, and at each
# distance the LOWER of the two sides (a neighbour or a brace beside one side only raises that side). `halo_exclude`
# boxes are out of the halo read only: a neighbouring bar is still a MUTED mark for the lit / muted read.
FILL_VAL = 0.85            # a fill pixel: this share of the ink's value (its own halo falls under it)
FILL_SPAN = (0.2, 0.8)     # the middle of the fill's length the side profile reads
FILL_RULE_1080 = 4.0       # a mark this thin (stage px) is a rule or a stub, not a muted fill
OUTLINE_1080 = 4.0         # a mark's own outline (a stack's separator) is this thin at most: the halo is read past it
THUMB_W = 256              # the thumbnail a fill is also read at (T10's frame acceptance: the sheet at 256 px wide)
FILL_KEYS = ("halo_edge", "halo_r50_px1080", "halo_reach10_px1080", "halo_area_x_fill")   # the band: at 1920 AND at THUMB_W
FILL_ABS = {"halo_edge": 0.03, "halo_r50_px1080": 0.5, "halo_reach10_px1080": 1.0, "halo_area_x_fill": 0.2,
            "thumb_lit_share": 0.03, "lit_muted_ratio": 0.1, "lit_muted_excess": 0.1, "thumb_lit_muted_ratio": 0.1}


def fill_mask(rgb: np.ndarray, ink: str, box, exclude=()) -> np.ndarray:
    """The largest connected region of the ink inside the box, its holes filled (a dot or a word on it stays in it)."""
    h, s, v = hsv(rgb)
    ih, is_, iv = (float(c.ravel()[0]) for c in hsv(hex_rgb(ink)[None, None, :]))
    if is_ < NEUTRAL_SAT:
        raise ValueError(f"a fill's ink is a colour; {ink} is neutral (a white fill has no hue to find it by)")
    inside = _box_mask(s.shape, box)
    for ex in exclude:
        inside &= ~_box_mask(s.shape, ex)
    dh = np.abs((h - ih + 180.0) % 360.0 - 180.0)
    m = (dh <= HUE_TOL) & (s >= SAT_FLOOR * is_) & (v >= FILL_VAL * iv) & inside
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    if not n:
        return m
    sizes = ndimage.sum(m, lab, index=np.arange(1, n + 1))
    return ndimage.binary_fill_holes(lab == int(np.argmax(sizes)) + 1)


def _side_rows(L: np.ndarray, F: np.ndarray, H: np.ndarray, ring_max: int) -> tuple[np.ndarray, np.ndarray]:
    """Per row of the fill's middle span: the luma 1..ring_max px out of its first and its last column (NaN outside
    the halo mask). A standing fill is read as is; a lying one comes in transposed."""
    rows = np.nonzero(F.any(axis=1))[0]
    a = rows[0] + int(FILL_SPAN[0] * (rows[-1] - rows[0]))
    b = rows[0] + int(np.ceil(FILL_SPAN[1] * (rows[-1] - rows[0])))
    out = np.full((2, b - a + 1, ring_max), np.nan)
    steps = np.arange(1, ring_max + 1)
    for k, r in enumerate(range(a, b + 1)):
        cols = np.nonzero(F[r])[0]
        if not cols.size:
            continue
        for side, idx in enumerate((cols[0] - steps, cols[-1] + steps)):
            ok = (idx >= 0) & (idx < L.shape[1])
            vals = np.full(ring_max, np.nan)
            vals[ok] = np.where(H[r, idx[ok]], L[r, idx[ok]], np.nan)
            out[side, k] = vals
    return out[0], out[1]


def side_profile(lu: np.ndarray, fill: np.ndarray, halo_m: np.ndarray, ring_max: int) -> np.ndarray:
    """The halo across the fill's long edges: per distance, the lower side's median over the rows (NaN: no data)."""
    import warnings
    ys, xs = np.nonzero(fill)
    standing = (ys.max() - ys.min()) >= (xs.max() - xs.min())
    L, F, H = (lu, fill, halo_m) if standing else (lu.T, fill.T, halo_m.T)
    left, right = _side_rows(L, F, H, ring_max)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # an all-NaN distance (past the box on both sides) stays NaN
        return np.fmin(np.nanmedian(left, axis=0), np.nanmedian(right, axis=0))


def fill_marks(lu: np.ndarray, box_m: np.ndarray, lit_zone: np.ndarray, g: float, k1080: float) -> np.ndarray:
    """Every other visible mark in the box - the muted bars, a capsule's track - with the thin rules and stubs out."""
    marks = box_m & ~lit_zone & (lu > g + MARK_LUMA)
    lab, _n = ndimage.label(marks, structure=np.ones((3, 3)))
    thin = FILL_RULE_1080 / k1080
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if min(hh, ww) <= thin or (lab[sl] == i).sum() < SPECK_PX:
            marks[sl] &= lab[sl] != i
    return marks


def _lit_muted(yl: np.ndarray, lu: np.ndarray, lit: np.ndarray, marks: np.ndarray, g: float) -> dict:
    if marks.sum() < SPECK_PX * 4 or not lit.any():
        return {"lit_muted_ratio": None, "lit_muted_excess": None}
    ly, my = float(np.percentile(yl[lit], 90)), float(np.percentile(yl[marks], 90))
    ll, ml = float(np.percentile(lu[lit], 90)), float(np.percentile(lu[marks], 90))
    return {"lit_muted_ratio": round((ly + 0.05) / (my + 0.05), 2),
            "lit_muted_excess": round((ll - g) / max(ml - g, 1e-6), 2)}


def _thumb(rgb: np.ndarray, box, fill: np.ndarray, zone: np.ndarray, marks: np.ndarray, g: float) -> dict:
    """The fill at THUMB_W: its zone's share of the box's contrast, and its lit / muted ratio there."""
    h, w = rgb.shape[:2]
    sh = round(h * THUMB_W / w)
    small = np.asarray(Image.fromarray((rgb * 255).round().astype(np.uint8)).resize((THUMB_W, sh), Image.LANCZOS))
    s01 = small.astype(np.float64) / 255.0
    cov = lambda m: np.asarray(Image.fromarray(m.astype(np.float32)).resize((THUMB_W, sh), Image.BOX))  # noqa: E731
    lm = _lit_muted(rel_lum(s01), luma(s01), cov(fill) >= 0.99, cov(marks) >= 0.5, g)
    return {"width": THUMB_W, "lit_share": round(squint(rgb, box, zone, g, THUMB_W), 3),
            "lit_muted_ratio": lm["lit_muted_ratio"]}


def _fill_ground(lu: np.ndarray, fill: np.ndarray, halo_m: np.ndarray, ring_max: int) -> float:
    far = halo_m & (ndimage.distance_transform_edt(~fill) > ring_max)
    return float(np.median(lu[far] if far.any() else lu[halo_m]))


def _fill_halo(lu: np.ndarray, fill: np.ndarray, halo_m: np.ndarray, ring_max: int, g: float, k1080: float) -> list[float]:
    """The side profile less the ground, cut where the read runs out of box (its first NaN). A mark with an OUTLINE of
    its own (a stack's part: a charcoal separator stroke round it) reads dark at its first rings; the halo starts at
    the profile's peak within OUTLINE_1080 of the edge - on an unstroked fill that peak is the edge itself (ring 1)."""
    raw = side_profile(lu, fill, halo_m, ring_max)
    n = int(np.argmax(np.isnan(raw))) if np.isnan(raw).any() else len(raw)
    prof = [float(v) - g for v in raw[:n]] or [0.0]
    head = prof[:max(1, int(round(OUTLINE_1080 / k1080)) + 1)]
    return prof[int(np.argmax(head)):]


def measure_fill(frame: str | Path, ink: str, box, *, exclude=(), halo_exclude=(), at_width: int | None = None) -> dict:
    """Every number for one lit FILL (a gauge's, a bar's). Boxes are in the frame's OWN px; `at_width` scales them."""
    native_w = Image.open(frame).width
    rgb = load_rgb(frame, at_width)
    h, w = rgb.shape[:2]
    ks, k1080 = w / native_w, STAGE_W / w
    sc = lambda b: [v * ks for v in b]  # noqa: E731
    box, exclude, halo_exclude = sc(box), [sc(e) for e in exclude], [sc(e) for e in halo_exclude]
    fill = fill_mask(rgb, ink, box, exclude)
    if not fill.any():
        raise ValueError(f"{frame}: no fill of ink {ink} inside the box {box}")
    box_m = _box_mask((h, w), box)
    for ex in exclude:
        box_m &= ~_box_mask((h, w), ex)
    halo_m = box_m & ~fill
    for ex in halo_exclude:
        halo_m &= ~_box_mask((h, w), ex)
    lu, yl = luma(rgb), rel_lum(rgb)
    ring_max = max(8, round(RING_MAX_1080 / k1080))
    g = _fill_ground(lu, fill, halo_m, ring_max)
    prof = _fill_halo(lu, fill, halo_m, ring_max, g, k1080)
    body = ndimage.binary_erosion(fill, iterations=max(1, round(2 / k1080)))
    fl = float(np.median(lu[body if body.any() else fill])) - g
    r50, reach10 = _cross(prof, 0.5 * prof[0]), _cross(prof, 0.10 * fl)
    area = float(sum(max(v, 0.0) for v in prof))
    zone = ndimage.binary_dilation(fill, iterations=max(1, int(round(reach10)) + 1))
    marks = fill_marks(lu, box_m, zone, g, k1080)
    th = _thumb(rgb, box, fill, zone, marks, g)
    return {
        "mode": "fill", "frame": str(frame).replace("\\", "/"), "size": [w, h], "ink": ink.upper(),
        "box": [round(v, 1) for v in box], "ground_luma": round(g, 2),
        "fill_px1080": round(2.0 * float(ndimage.distance_transform_edt(fill).max()) * k1080, 1),
        "fill_luma": round(fl, 2), "halo_edge": round(prof[0] / fl, 3) if fl > 0 else 0.0,
        "halo_r50_px1080": round(r50 * k1080, 2), "halo_reach10_px1080": round(reach10 * k1080, 2),
        "halo_area_1080": round(area * k1080, 1), "halo_area_x_fill": round(area * k1080 / fl, 2) if fl > 0 else 0.0,
        "halo_read_px1080": round(len(prof) * k1080, 1), "halo_profile": [round(v, 1) for v in prof],
        "lit_lum": round(float(np.percentile(yl[fill], 90)), 4), "muted_px": int(marks.sum()),
        **_lit_muted(yl, lu, fill, marks, g),
        "thumb_lit_share": th["lit_share"], "thumb_lit_muted_ratio": th["lit_muted_ratio"], "thumb": th,
    }


def bravos_fill_frame(entry: dict, root: Path, out_dir: Path) -> tuple[Path, str]:
    """A fills entry's frame, extracted from its video at its instant (BRAVOS-FRAME: ffmpeg -ss <t> -i <video>)."""
    import hashlib
    import subprocess
    video = resolve(entry["video"], root)
    if not video.exists():
        raise FileNotFoundError(f"{entry['id']}: video not on disk ({video})")
    png = out_dir / f"{entry['id']}.png"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(entry["t"]), "-i", str(video), "-frames:v", "1", str(png)],
                   check=True)
    return png, hashlib.sha256(png.read_bytes()).hexdigest()


def measure_fill_entry(entry: dict, png: Path, at_width: int | None = None) -> dict:
    return measure_fill(png, entry["ink"], entry["box"], exclude=entry.get("exclude", ()),
                        halo_exclude=entry.get("halo_exclude", ()), at_width=at_width)


def fills_band(frames: list[dict]) -> dict:
    """The band a fill is judged against: each FILL_KEYS number's min and max over the recorded Bravos fills, read at
    the frame's own 1920 (`full`) and at THUMB_W (`thumb`, the tool run on the frame downsampled)."""
    out = {}
    for side, rec in (("full", "measured"), ("thumb", "measured_thumb")):
        out[side] = {}
        for k in FILL_KEYS:
            v = [f[rec][k] for f in frames if f[rec].get(k) is not None]
            out[side][k] = {"min": min(v), "max": max(v), "n": len(v)}
    return out


def _fill_drift(e: dict, rec: str, got: dict, sha: str) -> list[str]:
    bad = []
    for key, want in e[rec].items():
        have = got.get(key)
        if want is None or have is None:
            if want != have:
                bad.append(f"{e['id']}.{rec}.{key}: recorded {want}, measured {have}")
            continue
        tol = max(BAND_TOL * abs(want), FILL_ABS.get(key, 0.05))
        if abs(have - want) > tol:
            why = "" if sha == e["frame_sha256"] else " (the decoded frame differs from the recorded one)"
            bad.append(f"{e['id']}.{rec}.{key}: recorded {want}, measured {have} (tol {tol:.3f}){why}")
    return bad


def check_fills(band_path: Path, root: Path) -> list[str]:
    """Re-extract and re-measure every recorded Bravos fill; a number that no longer reproduces is a finding."""
    import tempfile
    fb = json.loads(band_path.read_text(encoding="utf-8")).get("fills")
    if not fb:
        return []
    bad = [] if fb["band"] == fills_band(fb["frames"]) else ["fills.band: not the recorded frames' own min / max"]
    with tempfile.TemporaryDirectory() as td:
        for e in fb["frames"]:
            try:
                png, sha = bravos_fill_frame(e, root, Path(td))
            except FileNotFoundError as err:
                bad.append(str(err))
                continue
            bad += _fill_drift(e, "measured", measure_fill_entry(e, png), sha)
            bad += _fill_drift(e, "measured_thumb", measure_fill_entry(e, png, THUMB_W), sha)
    return bad


# ---- P72 T49 (R26-378): a SPREAD's halo - the fill between two lines ---------------------------------------------
# The operator, on P71 T36's divergence spread beside Bravos D40 04:48: "their red fill has more of a bloom than ours
# t36, but that should just be a dial not a recipe change". A spread's two long edges ARE its two lines (each with a
# bloom of its own, in another ink), so the fill's own halo is read where no line is: PAST THE FILL'S END - its last
# column (`end` "right") or its first ("left") - row by row over the middle SPREAD_SPAN of the rows the fill reaches
# that column in (the two lines' end dots, tips and tags sit at the end's top and foot). The read starts SPREAD_SKIP
# past the edge on both sides of the comparison: D40 draws its plot's frame rule exactly at the fill's end. The fill's
# luma is its own at the end (SPREAD_BODY in from the end of those rows - D40's fill deepens toward its end), the ground
# the same rows' past the halo (from `ground_from` stage px, 96 by default; a frame rule close past the end - BOOM
# 08:35's, 50 px - stops the box and the read before it). Every distance is from the fill's edge. The band is `spreads` in the band file.
SPREAD_SPAN = (0.25, 0.75)   # the middle of the end's height the read takes
SPREAD_SKIP_1080 = 2.0       # the read starts this many stage px past the edge (D40's frame rule, x 1520-1521 at 1920, reads
                             # as the fill's own last column - its hue is the fill's - and leaves one dark AA pixel past it);
                             # at a thumbnail at least ONE px: the first ring there is the edge's own resampled pixel (our
                             # NO-glow spread read 0.40 at 256 on it)
SPREAD_BODY_1080 = (6.0, 30.0)   # the fill's own luma: this far in from its end, stage px (clear of the rule's AA inside)
SPREAD_END_TOL = 2           # an end row: the fill reaches within this many px of its end column
SPREAD_KEYS = FILL_KEYS + ("fill_luma",)   # the band: the halo's four AND the fill's own brightness over its ground (the
                                           # coordinator's ruling on T49: the fill is a dial the reference sets too)


def _end_rows(fill: np.ndarray, end: str) -> tuple[np.ndarray, np.ndarray]:
    """The rows the fill reaches its end column in (the middle SPREAD_SPAN of them) and each row's end column."""
    if not fill.any():
        raise ValueError("an empty fill has no end")
    last = np.array([(np.nonzero(r)[0][-1] if end == "right" else np.nonzero(r)[0][0]) if r.any() else -10 ** 6
                     for r in fill])
    vals, counts = np.unique(last[last > -10 ** 6], return_counts=True)
    at = int(vals[np.argmax(counts)])   # the END is the column most rows stop at (a dot or a tip past it is one row's)
    rows = np.nonzero(np.abs(last - at) <= SPREAD_END_TOL)[0]
    a = rows[0] + int(SPREAD_SPAN[0] * (rows[-1] - rows[0]))
    b = rows[0] + int(np.ceil(SPREAD_SPAN[1] * (rows[-1] - rows[0])))
    rows = rows[(rows >= a) & (rows <= b)]
    return rows, last[rows]


def end_profile(lu: np.ndarray, fill: np.ndarray, halo_m: np.ndarray, reach: int, ground_at: int, end: str) -> tuple[np.ndarray, list]:
    """Per distance 1..reach past the fill's end: the median luma over the end rows (NaN outside the halo mask); and
    the same rows' luma from `ground_at` to 2 x `ground_at` (the ground past the halo, inside the box)."""
    import warnings
    rows, edge = _end_rows(fill, end)
    sgn, n = (1 if end == "right" else -1), 2 * max(reach, ground_at)
    steps = np.arange(1, n + 1)
    out = np.full((rows.size, n), np.nan)
    for k, (r, c) in enumerate(zip(rows, edge)):
        idx = c + sgn * steps
        ok = (idx >= 0) & (idx < lu.shape[1])
        vals = np.full(n, np.nan)
        vals[ok] = np.where(halo_m[r, idx[ok]], lu[r, idx[ok]], np.nan)
        out[k] = vals
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        far = out[:, ground_at - 1:2 * ground_at].ravel()
        return np.nanmedian(out[:, :reach], axis=0), [float(v) for v in far if not np.isnan(v)]


def _end_body(lu: np.ndarray, fill: np.ndarray, end: str, k1080: float) -> float:
    rows, edge = _end_rows(fill, end)
    sgn = 1 if end == "right" else -1
    d0, d1 = (max(1, int(round(v / k1080))) for v in SPREAD_BODY_1080)
    vals = [lu[r, c - sgn * d] for r, c in zip(rows, edge) for d in range(d0, max(d0 + 1, d1))
            if 0 <= c - sgn * d < lu.shape[1] and fill[r, c - sgn * d]]
    return float(np.median(vals))


def measure_spread(frame: str | Path, ink: str, box, *, end: str = "right", exclude=(), halo_exclude=(),
                   ground_from: float = RING_MAX_1080, at_width: int | None = None) -> dict:
    """Every number for one SPREAD (the fill between two lines), read past its end. Boxes are in the frame's own px."""
    if end not in ("right", "left"):
        raise ValueError(f"a spread's end is 'right' or 'left', not {end!r}")
    native_w = Image.open(frame).width
    rgb = load_rgb(frame, at_width)
    h, w = rgb.shape[:2]
    ks, k1080 = w / native_w, STAGE_W / w
    sc = lambda b: [v * ks for v in b]  # noqa: E731
    box, exclude, halo_exclude = sc(box), [sc(e) for e in exclude], [sc(e) for e in halo_exclude]
    fill = fill_mask(rgb, ink, box, exclude)
    if not fill.any():
        raise ValueError(f"{frame}: no fill of ink {ink} inside the box {box}")
    box_m = _box_mask((h, w), box)
    for ex in exclude:
        box_m &= ~_box_mask((h, w), ex)
    halo_m = box_m & ~fill
    for ex in halo_exclude:
        halo_m &= ~_box_mask((h, w), ex)
    lu = luma(rgb)
    ring_max = max(8, round(RING_MAX_1080 / k1080))
    ground_at = max(4, min(ring_max, round(ground_from / k1080)))   # a frame rule close past the end: the box stops at it
    raw, far = end_profile(lu, fill, halo_m, ground_at, ground_at, end)
    if not far:
        raise ValueError(f"{frame}: no ground inside the box past the halo ({ground_from} stage px past the end)")
    g = float(np.median(far))
    skip = min(len(raw) - 1, max(1, int(round(SPREAD_SKIP_1080 / k1080))))   # at a thumbnail: at least the edge's own resampled px
    n = int(np.argmax(np.isnan(raw))) if np.isnan(raw).any() else len(raw)
    prof = [float(v) - g for v in raw[skip:n]] or [0.0]
    fl = _end_body(lu, fill, end, k1080) - g
    off = skip   # every distance is from the fill's edge: the profile starts at ring skip + 1
    r50, reach10 = _cross(prof, 0.5 * prof[0]) + off, _cross(prof, 0.10 * fl) + off
    area = float(sum(max(v, 0.0) for v in prof))
    rows, _edge = _end_rows(fill, end)
    return {
        "mode": "spread", "frame": str(frame).replace("\\", "/"), "size": [w, h], "ink": ink.upper(), "end": end,
        "box": [round(v, 1) for v in box], "ground_luma": round(g, 2), "end_rows": [int(rows[0]), int(rows[-1])],
        "fill_luma": round(fl, 2), "halo_edge": round(prof[0] / fl, 3) if fl > 0 else 0.0,
        "halo_r50_px1080": round(r50 * k1080, 2), "halo_reach10_px1080": round(reach10 * k1080, 2),
        "halo_area_1080": round(area * k1080, 1), "halo_area_x_fill": round(area * k1080 / fl, 2) if fl > 0 else 0.0,
        "halo_read_px1080": round((len(prof) + off) * k1080, 1), "halo_profile": [round(v, 1) for v in prof],
    }


def measure_spread_entry(entry: dict, png: Path, at_width: int | None = None) -> dict:
    return measure_spread(png, entry["ink"], entry["box"], end=entry.get("end", "right"),
                          exclude=entry.get("exclude", ()), halo_exclude=entry.get("halo_exclude", ()),
                          ground_from=entry.get("ground_from", RING_MAX_1080), at_width=at_width)


def spreads_band(frames: list[dict]) -> dict:
    """The band a spread is judged against: each SPREAD_KEYS number's min and max over the recorded Bravos spreads, at
    1920 (`full`) and at THUMB_W (`thumb`)."""
    out = {}
    for side, rec in (("full", "measured"), ("thumb", "measured_thumb")):
        out[side] = {}
        for k in SPREAD_KEYS:
            v = [f[rec][k] for f in frames if f[rec].get(k) is not None]
            out[side][k] = {"min": min(v), "max": max(v), "n": len(v)}
    return out


def check_spreads(band_path: Path, root: Path) -> list[str]:
    """Re-extract and re-measure every recorded Bravos spread (the `spreads` entry); a drift is a finding."""
    import tempfile
    sb = json.loads(band_path.read_text(encoding="utf-8")).get("spreads")
    if not sb:
        return []
    bad = [] if sb["band"] == spreads_band(sb["frames"]) else ["spreads.band: not the recorded frames' own min / max"]
    with tempfile.TemporaryDirectory() as td:
        for e in sb["frames"]:
            try:
                png, sha = bravos_fill_frame(e, root, Path(td))
            except FileNotFoundError as err:
                bad.append(str(err))
                continue
            bad += _fill_drift(e, "measured", measure_spread_entry(e, png), sha)
            bad += _fill_drift(e, "measured_thumb", measure_spread_entry(e, png, THUMB_W), sha)
    return bad


# ---- M48 (P71 T7; E99 s120 / s126): the squint read of a BUILD, and the reference it is judged against ------------

SQUINT_NAME = "squint.json"          # written beside the timeline; gate_motion_density.load_squint reads it
SQUINT_SCHEMA = "squint.v1"
BAND_W = 1024                        # the band's lit share is read at its 1024 px frames' width - ours at the same
HELD_MIN_S = 1.0                     # [DERIVED: a state held under a second is a pass-through, not a page a thumbnail catches]
TRANSIENT_S = 2.5                    # [DERIVED: M16's 2.5 s pulse] a species this short is a WRITE (a retitle, a figure, a
                                     # note, a ring) - the page is not at rest under it; a longer one (a solo, a held
                                     # spotlight) is a state the page is held in
AXIS_ROLES = ("xtick", "ylabel", "tick", "axislabel", "axis")   # axis furniture - Bravos's counts leave the axes out


def squint_gate_read(entry: dict, root: Path) -> dict:
    """One band frame's squint numbers, as the gate reads ours: the lit share at BAND_W, the title's and the named
    label's cap (glyph by glyph, T37c's `title_size`) at the gate's width, and the hand-counted plot words."""
    path = resolve(entry["frame"], root)
    got = measure(path, entry["ink"], entry["box"], **_args_of(entry), at_width=BAND_W)
    nat_w = Image.open(path).width
    t = title_size(path, entry["title_box"], entry["title"]["text"])
    lab = None if entry.get("label_unread") else title_size(path, entry["label_box"], entry["label_text"])
    at = lambda r: round(r["cap_px"] * SQUINT_W / nat_w, 3) if r and r["cap_px"] else None  # noqa: E731
    return {"width": SQUINT_W, "at_width": BAND_W, "lit_share": got["squint"]["lit_share"],
            "title_cap_px": at(t), "label_cap_px": at(lab), "label_method": lab["method"] if lab else None,
            "plot_words": entry["plot_words"]}


def squint_band(frames: list[dict]) -> dict:
    keys = ("lit_share", "title_cap_px", "label_cap_px", "plot_words")
    out = {"width": SQUINT_W, "at_width": BAND_W, "frames": [f["id"] for f in frames],
           "unread": {f["id"]: f["label_unread"] for f in frames if f.get("label_unread")}}
    for k in keys:
        v = [f["squint_gate"][k] for f in frames if f["squint_gate"][k] is not None]
        out[k] = {"min": min(v), "max": max(v), "n": len(v)}
    return out


def _drift(fid: str, want: dict, have: dict, keys) -> list[str]:
    bad = []
    for key in keys:
        a, b = want.get(key), have.get(key)
        if a is None or b is None:
            if a != b:
                bad.append(f"{fid}.{key}: recorded {a}, measured {b}")
        elif abs(a - b) > max(BAND_TOL * abs(a), BAND_ABS.get(key, 0.0), 0.05 if key != "cap_px" else 0.02):
            bad.append(f"{fid}.{key}: recorded {a}, measured {b}")
    return bad


def check_squint_band(band_path: Path, root: Path) -> list[str]:
    band = json.loads(band_path.read_text(encoding="utf-8"))
    bad = []
    for e in band["frames"]:
        if "squint_gate" in e and resolve(e["frame"], root).exists():
            bad += _drift(e["id"], e["squint_gate"], squint_gate_read(e, root),
                          ("lit_share", "title_cap_px", "label_cap_px", "plot_words"))
    return bad


def check_caption_floor(floor_path: Path, root: Path) -> list[str]:
    """Re-read every reference caption the floor records; a number that no longer reproduces is a finding."""
    doc = json.loads(floor_path.read_text(encoding="utf-8"))
    bad = []
    for lane in doc["lanes"].values():
        for fr in lane.get("frames") or []:
            p = resolve(fr["frame"], root)
            if not p.exists():
                bad.append(f"{fr['frame']}: not on disk")
                continue
            bad += _drift(fr["frame"], fr["measured"], caption_read(p, fr["box"], fr.get("text", "")),
                          ("cap_px", "contrast"))
    return bad


def held_instants(tl: dict) -> list[dict]:
    """Every HELD state of every ledger page, read off the timeline's own clocks (the gate's): the page's changes are
    its build_to / bracket windows, its data-changing chart_to hand-overs and its undraw; a hold is a gap between
    them from the page's landing on, at least HELD_MIN_S long, read at its MIDDLE (clear of the landing's settle and
    of the exit's start). Every other species up to TRANSIENT_S long is a write in progress and splits a hold too."""
    import gate_motion_density as G  # noqa: PLC0415 - the gate owns the clocks; imported where a build is read
    out = []
    for s in tl.get("scenes", []):
        if not G._is_page(s) or not s.get("span"):
            continue
        a, z = float(s["span"][0]), float(s["span"][1])
        win = []
        for x in s.get("species", []):
            at, k = float(x.get("at", -1e9)), x.get("kind")
            if not a <= at <= z:
                continue
            if k in ("build_to", "bracket"):
                win.append((at, at + float(x.get("dur", 0.0)), f"{k} lands"))
            elif k == "chart_to" and x.get("to") in G.TRANSITION_DATA_KINDS:
                win.append((at, G._transition_land(s, x), f"chart_to {x.get('to')} lands"))
            elif k == "undraw":
                win.append((at, z, "undraw"))
            elif 0.0 < float(x.get("dur", 0.0)) <= TRANSIENT_S:
                win.append((at, at + float(x["dur"]), f"{k} lands"))
        cur, why = a + G._page_land_offset(s), "the page lands"
        for w0, w1, wwhy in sorted(win) + [(z, z, "")]:
            if w0 - cur >= HELD_MIN_S:
                out.append({"t": round((cur + w0) / 2, 3), "scene": str(s.get("scene_id", "?")),
                            "why": f"{why} {cur:.2f}s, held to {w0:.2f}s", "hold": [round(cur, 3), round(w0, 3)]})
            if w1 > cur:
                cur, why = w1, wwhy
    return out


def caption_instants(tl: dict) -> list[dict]:
    """Every caption page, read when its LAST word has been written: halfway from that word's start to the page's end."""
    out = []
    for p in tl.get("caption_pages") or []:
        ws = p.get("t") or []
        if not ws:
            continue
        last, e = max(float(w["s"]) for w in ws), float(p["e"])
        out.append({"t": round(last + 0.5 * max(0.0, e - last), 3), "text": " ".join(str(w["w"]) for w in ws),
                    "mode": p.get("cap_mode") or "", "span": [float(p["s"]), e]})
    return out


READ_SQUINT = r"""
() => {
  const stg = document.getElementById('stage').getBoundingClientRect();
  const R = (el) => { const r = el.getBoundingClientRect();
    return [r.x - stg.x, r.y - stg.y, r.x - stg.x + r.width, r.y - stg.y + r.height]; };
  const U = (a, b) => !a ? b : [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])];
  const eff = (el) => { let o = 1, e = el;   /* probe.py's READ_DOM: the effective opacity up the tree */
    while (e && e !== document.documentElement) { const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity); if (!(o > 0)) return 0;
      const a = e.getAttribute && e.getAttribute('opacity'); if (a != null && a !== '') o *= parseFloat(a) || 0;
      e = e.parentNode instanceof Element ? e.parentNode : null; }
    return o; };
  const written = (el) => { const gs = el.querySelectorAll('.g'); if (!gs.length) return 1; let n = 0;
    for (const g of gs) if (parseFloat(g.style.getPropertyValue('--w') || '0') > 0.02) n++; return n / gs.length; };
  const TX = (x) => (x || '').replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
  /* an SVG text's runs (a tag's value, name and chip are tspans) read as words apart, never run together */
  const RUNS = (el) => { if (el.tagName !== 'text') return TX(el.textContent);
    const parts = [...el.childNodes].map((n) => n.textContent || '');   /* a glyph-by-glyph write is one tspan a letter */
    return TX(parts.join(parts.every((x) => x.length <= 1) ? '' : ' ')); };
  const out = { page: null, caption: null };
  const cap = document.getElementById('caption');
  if (cap && eff(cap) > 0.05) {
    const ws = [...cap.querySelectorAll('.cw')].filter((w) => eff(w) > 0.05 && w.getBoundingClientRect().width > 0);
    let u = null; for (const w of ws) u = U(u, R(w));
    if (u) out.caption = { box: u, text: TX(ws.map((w) => w.textContent).join(' ')), mode: cap.className,
                           words: ws.map((w) => [R(w), TX(w.textContent)]) };
  }
  /* the page on screen: wB, the last world (probe.py's and the template's own rule, R26-37) */
  const worlds = [...document.querySelectorAll('.world')];
  const wB = document.getElementById('wB') || worlds[worlds.length - 1];
  const world = wB && wB.__lp && wB.classList.contains('ledger') && eff(wB) > 0.05 ? wB : null;
  if (!world) return out;
  const S = world.__lp, pg = { title: null, plot: null, lit: null, label: null, words: [], wboxes: [], panels: !!S.panels,
                               panel_plots: [] };
  /* a PANELS page: each SHOWN panel's plot box through its own screen CTM (measure_page_boxes' pplot), in panel order */
  if (S.panels) for (const P of S.panels) {
    if (!(+getComputedStyle(P.box).opacity > 0.05)) continue;
    const m = P.chart && P.chart.getScreenCTM(), Q = P.plot; if (!m || !Q) continue;
    const pt = (x, y) => [m.a * x + m.c * y + m.e - stg.x, m.b * x + m.d * y + m.f - stg.y];
    const a = pt(Q.L, Q.T), b = pt(Q.W - Q.R, Q.B);
    pg.panel_plots.push([Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])]);
  }
  const t = world.querySelector('.lp-title');
  if (t && eff(t) > 0.05) {   /* the FIRST written line of the title (a retitle's new run; the old run is unwritten) */
    const gs = [...t.querySelectorAll('.g')].filter((g) => parseFloat(g.style.getPropertyValue('--w') || '0') > 0.5
      && g.getBoundingClientRect().width > 0);
    /* a glyph's INK box: its rect less the padding the glow is given room by (P69 T37c pads each glyph .36em) */
    const G = (g) => { const r = R(g), cs = getComputedStyle(g); return [r[0] + parseFloat(cs.paddingLeft), r[1] + parseFloat(cs.paddingTop),
      r[2] - parseFloat(cs.paddingRight), r[3] - parseFloat(cs.paddingBottom)]; };
    if (gs.length) { const y0 = Math.min(...gs.map((g) => G(g)[1])); const row = gs.filter((g) => G(g)[1] < y0 + (G(g)[3] - G(g)[1]) / 2);
      row.sort((a, b) => G(a)[0] - G(b)[0]);   /* the spaces are not glyphs: a gap over a quarter of the line's height is one */
      const lh = Math.max(...row.map((g) => G(g)[3] - G(g)[1]));
      let u = null, txt = ''; row.forEach((g, i) => { u = U(u, G(g));
        if (i && G(g)[0] - G(row[i - 1])[2] > 0.25 * lh) txt += ' '; txt += g.textContent; });
      pg.title = { box: u, text: TX(txt) }; }
    else pg.title = { box: R(t), text: TX(t.textContent) };
  }
  /* the STATE on screen: a page with page_states keeps every state's chart in the DOM (st.states), and the one
     painted need not be wB.__lp - the visible chart that draws the most visible line ink is the page read */
  const inked = (st) => (st.marks || []).filter((mk) => mk.role === 'line' && mk.el && eff(mk.el) > 0.05).length;
  const V = [S, ...(S.states || [])].filter((st) => st.chart && eff(st.chart) > 0.05)
    .sort((a, b) => inked(b) - inked(a))[0] || S;
  const chart = V.chart || world.querySelector('.lp-chart');
  if (chart && !S.panels) {
    const m = chart.getScreenCTM();
    if (V.plot && m) { const P = V.plot, pt = (x, y) => [m.a * x + m.c * y + m.e - stg.x, m.b * x + m.d * y + m.f - stg.y];
      const a = pt(P.L, P.T), b = pt(P.W - P.R, P.B);
      pg.plot = [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])]; }
    else for (const el of chart.querySelectorAll('rect.bar, path.ser, path.wedge, line.ax, line.grid')) {
      const r = R(el); if (r[2] - r[0] >= 1 || r[3] - r[1] >= 1) pg.plot = U(pg.plot, r); }
  }
  /* the LIT line: the unmuted series drawn hot (E99 s117's lphot filter; a solo moves it), most visible first */
  const lines = (V.marks || []).filter((mk) => mk.role === 'line' && mk.el && !(mk.rec && mk.rec.muted) && eff(mk.el) > 0.05);
  const hot = (mk) => /lphot/.test((mk.el.getAttribute('filter') || '') + (mk.el.style.filter || ''));
  const rank = lines.map((mk) => [(hot(mk) ? 2 : 1) * eff(mk.el) * (parseFloat(getComputedStyle(mk.el).strokeWidth) || 1), mk])
    .sort((p, q) => q[0] - p[0]);
  if (rank.length) { const mk = rank[0][1]; pg.lit = { key: mk.key, stroke: getComputedStyle(mk.el).stroke, hot: hot(mk) };
    const nm = V.markBy && V.markBy['name:' + mk.key];
    if (nm && nm.el && eff(nm.el) > 0.05) pg.label = { box: R(nm.el), text: RUNS(nm.el) }; }
  /* the WORDS on the page: every visible text run of the world and the species layers, less the title, the sub,
     the source and the axis furniture (a glyph-written run and an SVG text count once, whole) */
  /* a PANELS page's axis marks live on each panel (P.marks), not on the page's own list */
  /* E99 s129 (3): axis ticks and axis titles are not words. They are marks on whichever STATE drew them (st.states: a
     page with page_states keeps each state's own list - the one on screen need not be wB.__lp's) and on each panel */
  const owners = [S, ...(S.states || []), ...(S.panels || [])];
  for (const st of S.states || []) owners.push(...(st.panels || []));
  const allMarks = [].concat(...owners.map((o) => o.marks || []));
  const skip = new Set(allMarks.filter((mk) => AXIS.includes(mk.role) && mk.el).map((mk) => mk.el));
  const blocks = new Set();
  for (const root of [world, document.getElementById('species'), document.getElementById('species-under')]) {
    if (!root) continue;
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    for (let n = tw.nextNode(); n; n = tw.nextNode()) {
      if (!(n.textContent || '').trim()) continue;
      const p = n.parentElement; if (!p) continue;
      const blk = p.closest('text') || p.closest('.lp-ink') || p;
      /* the page's title / sub / source, and a panel's own title (.lp-psub: each panel reads as its own chart, whose
         title - like Bravos's - is judged for size, not counted as plot words) */
      if (blocks.has(blk) || blk.closest('.lp-title, .lp-sub:not(.lp-note), .lp-src, .lp-psub')) continue;
      let sk = false; for (let e = blk; e && e !== root; e = e.parentElement) if (skip.has(e)) { sk = true; break; }
      if (sk || eff(blk) <= 0.05 || written(blk) <= 0.5) continue;
      const r = blk.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue;
      blocks.add(blk); pg.words.push(RUNS(blk)); pg.wboxes.push(R(blk));
    }
  }
  out.page = pg;
  return out;
}
""".replace("AXIS.includes", json.dumps(list(AXIS_ROLES)) + ".includes")


def _hex(css: str) -> str | None:
    nums = [float(v) for v in css.replace("rgba(", "").replace("rgb(", "").rstrip(")").split(",")[:3]] \
        if css and css.startswith("rgb") else None
    return "#" + "".join(f"{int(round(v)):02X}" for v in nums) if nums else None


def _grow(box, px: float, w: int, h: int) -> list[float]:
    return [max(0.0, box[0] - px), max(0.0, box[1] - px), min(w - 1.0, box[2] + px), min(h - 1.0, box[3] + px)]


def panel_word_counts(texts: list[str], boxes: list, plots: list) -> list[int]:
    """The words on each plot panel (the parent's T7 ruling: Bravos's band is single-chart pages, so a PANELS page
    reads as one chart per panel and each carries its own limit). A run belongs to the panel whose plot box holds
    its centre; one outside every panel counts toward the nearest (the distance from its centre to the box)."""
    counts = [0] * len(plots)
    for text, b in zip(texts, boxes):
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        d = [max(p[0] - cx, 0, cx - p[2]) ** 2 + max(p[1] - cy, 0, cy - p[3]) ** 2 for p in plots]
        counts[d.index(min(d))] += word_count([text])
    return counts


def read_page(png: Path, dom: dict, size: tuple[int, int]) -> dict:
    """The gate's numbers for one held page: its lit share (at BAND_W), its title's and its lit series' name's cap at
    the gate's width, and its words. A page with no lit line (bars, panels) has no lit share: the Bravos band is line
    pages only, and a number with no reference is not judged (E38)."""
    w, h = size
    k = SQUINT_W / w
    rec = {"title": None, "title_cap_px": None, "label": None, "label_cap_px": None, "lit_share": None, "lit_ink": None,
           "lit_note": None, "plot_words": word_count(dom.get("words") or []), "words": dom.get("words") or []}
    if dom.get("panel_plots"):   # the parent's T7 ruling: the band is single-chart pages - 7 words PER PLOT PANEL
        rec["panel_words"] = panel_word_counts(dom["words"], dom.get("wboxes") or [], dom["panel_plots"])
        rec["plot_words"] = max(rec["panel_words"])
    if dom.get("title"):
        rec["title"] = dom["title"]["text"]
        rec["title_cap_px"] = (lambda r: round(r["cap_px"] * k, 3) if r["cap_px"] else None)(
            title_size(png, _grow(dom["title"]["box"], 6, w, h), dom["title"]["text"]))
    if dom.get("label"):
        rec["label"] = dom["label"]["text"]
        rec["label_cap_px"] = (lambda r: round(r["cap_px"] * k, 3) if r["cap_px"] else None)(
            title_size(png, _grow(dom["label"]["box"], 4, w, h), dom["label"]["text"]))
    lit, plot = dom.get("lit"), dom.get("plot")
    if dom.get("panels") or not lit or not plot:
        rec["lit_note"] = "no lit line on this page (a bars / panels page): the Bravos band is line pages only"
        return rec
    rec["lit_ink"] = _hex(lit.get("stroke") or "")
    try:
        got = measure(png, rec["lit_ink"], plot, at_width=BAND_W)
        rec["lit_share"] = got["squint"]["lit_share"]
    except ValueError as exc:
        rec["lit_note"] = f"the lit line's ink was not found in the plot ({exc})"
    return rec


def _instants(tl: dict, at: list[float] | None) -> tuple[list[dict], list[dict]]:
    if at is None:
        return held_instants(tl), caption_instants(tl)
    return ([{"t": float(t), "scene": _scene_of(tl, float(t)), "why": "given"} for t in at],
            [{"t": float(t)} for t in at])


def _shot(view, t: float, size: tuple[int, int], fdir: Path, tag: str) -> tuple[Path, dict]:
    """One frame at t through render_baseline's capture path, and the player's DOM read at the same t. The first seek
    settles (a cold seek reads a card before its body decodes - probe.py's rule); the second is the frame."""
    import render_baseline as RB  # noqa: PLC0415
    RB.frame_png(view, t, size)
    view.wait_for_timeout(120)
    p = fdir / f"{tag}-{t:08.3f}.png"
    p.write_bytes(RB.frame_png(view, t, size))
    return p, view.evaluate(READ_SQUINT)


PAGE_ONLY_CSS = ("#caption, .dock, .stackbox { visibility: hidden !important; }")   # the shell's R26-13 rule, for a
                                                                                      # player built before the switch


def _page_layer(view) -> str:
    """The page read wants the PAGE alone. A shell with R26-13's `?layers=` switch set it on <html>; a player built
    before it (the Japan short, 2026-09-10) ignores the query, so the same rule is put on the page by hand."""
    if view.evaluate("() => document.documentElement.getAttribute('data-layers')") == "page":
        return "shell ?layers=page"
    view.add_style_tag(content=PAGE_ONLY_CSS)
    return "injected (a player older than the ?layers= switch): " + PAGE_ONLY_CSS


def _caption_rec(p: Path, cap: dict, t: float, tl: dict, size: tuple[int, int], keep: bool) -> dict:
    r = caption_read(p, _grow(cap["box"], 4, *size), cap["text"],
                     words=[(_grow(b, 3, *size), t) for b, t in cap.get("words") or []])
    return {"t": t, "scene": _scene_of(tl, t), "text": cap["text"], "mode": cap.get("mode"), "cap_px": r["cap_px"],
            "contrast": r["contrast"], "cap_px1080": r["cap_px1080"], "method": r["method"],
            "frame": p.name if keep else None, "box": [round(v, 1) for v in cap["box"]],
            "words": [[[round(v, 1) for v in b], t_] for b, t_ in cap.get("words") or []]}


def measure_build(build: Path, *, timeline_name: str | None = None, html_name: str = "player.html",
                  at: list[float] | None = None, frames_dir: Path | None = None) -> Path:
    """The --build mode: each held page's frame (the PAGE layer only, the shell's `?layers=page` - its docks and
    caption hidden, their geometry kept) and each caption page's WHOLE frame (the caption over what is behind it),
    rendered through the frozen-frames capture path (render_baseline's serve / prepare_page / frame_png), read off
    the player's own DOM and measured at the gate's width. `at` restricts both to those instants (the caption on
    screen at each). Writes <build>/squint.json."""
    import hashlib  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    import render_baseline as RB  # noqa: PLC0415
    from playwright.sync_api import sync_playwright  # noqa: PLC0415
    build, html = Path(build), Path(build) / html_name
    tls = [build / timeline_name] if timeline_name else sorted(build.glob("*.timeline.json"))
    if not tls or not tls[0].exists():
        raise SystemExit(f"no timeline in {build}")
    tl = json.loads(tls[0].read_text(encoding="utf-8"))
    aspect = str(tl.get("aspect") or "16:9")
    size = RB.STAGE[aspect]
    pages, caps = _instants(tl, at)
    doc = {"schema": SQUINT_SCHEMA, "player_sha256": hashlib.sha256(html.read_bytes()).hexdigest(),
           "timeline": tls[0].name, "aspect": aspect, "gate_width": SQUINT_W, "band_width": BAND_W,
           "pages": [], "captions": []}
    keep = frames_dir is not None
    srv, port = RB.serve(build)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as pw:
        fdir = Path(frames_dir) if keep else Path(tmp)
        fdir.mkdir(parents=True, exist_ok=True)
        try:
            br = pw.chromium.launch(headless=True)
            views = {}
            for tag, q in (("page", "?layers=page"), ("whole", "")):
                views[tag] = br.new_context(viewport=dict(zip(("width", "height"), size))).new_page()
                views[tag].goto(f"http://127.0.0.1:{port}/{html.name}{q}", wait_until="networkidle", timeout=300000)
                RB.prepare_page(views[tag], *size)
            doc["page_layer"] = _page_layer(views["page"])
            for pgi in pages:
                p, dom = _shot(views["page"], pgi["t"], size, fdir, "page")
                if dom.get("page"):
                    doc["pages"].append({**pgi, **read_page(p, dom["page"], size), "frame": p.name if keep else None})
            for ci in caps:
                p, dom = _shot(views["whole"], ci["t"], size, fdir, "whole")
                if (dom.get("caption") or {}).get("text"):
                    doc["captions"].append(_caption_rec(p, dom["caption"], ci["t"], tl, size, keep))
            br.close()
        finally:
            srv.shutdown()
    out = build / SQUINT_NAME
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    return out


def _scene_of(tl: dict, t: float) -> str | None:
    return next((str(s.get("scene_id")) for s in tl.get("scenes", [])
                 if s.get("span") and float(s["span"][0]) <= t < float(s["span"][1])), None)


def _box(s: str | None):
    return [float(v) for v in s.split(",")] if s else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("frame", nargs="?")
    ap.add_argument("--ink", help="the lit line's ink, #RRGGBB (#FFFFFF for a white line)")
    ap.add_argument("--box", help="the plot's inner box x0,y0,x1,y1 (frame px)")
    ap.add_argument("--exclude", action="append", default=[], help="a box inside the plot to leave out (a badge)")
    ap.add_argument("--title-box"), ap.add_argument("--label-box"), ap.add_argument("--words-box")
    ap.add_argument("--words", type=int, help="the words on the plot, counted by the caller (a DOM, a hand count)")
    ap.add_argument("--band", type=Path, help="a band file (bravos-line-bloom.v1.json)")
    ap.add_argument("--check", action="store_true", help="re-measure every band frame; exit 1 when one drifts")
    ap.add_argument("--root", type=Path, default=Path.cwd(), help="where a band's relative frame paths resolve")
    ap.add_argument("--caption-floor", type=Path, help="a caption floor file (caption-squint-floor.v1.json) to --check")
    ap.add_argument("--build", type=Path, help="M48: read every held page and caption of a built player -> squint.json")
    ap.add_argument("--timeline", help="--build: the timeline file name inside the build dir")
    ap.add_argument("--at", type=float, nargs="+", help="--build: only these instants (the page and the caption at each)")
    ap.add_argument("--frames", type=Path, help="--build: keep the rendered frames in this dir")
    ap.add_argument("--fill", action="store_true", help="P72 T10: read a FILLED mark's halo (a gauge's fill, a lit bar)")
    ap.add_argument("--halo-exclude", action="append", default=[], help="--fill: a box left out of the halo read only")
    ap.add_argument("--spread", action="store_true", help="P72 T49: read a SPREAD's halo (the fill between two lines) past its end")
    ap.add_argument("--end", default="right", help="--spread: the fill's end the halo is read past, right | left")
    ap.add_argument("--ground-from", type=float, default=RING_MAX_1080,
                    help="--spread: the ground is read from this many stage px past the end (a frame rule close past it)")
    a = ap.parse_args(argv)
    if a.build:
        out = measure_build(a.build, timeline_name=a.timeline, at=a.at, frames_dir=a.frames)
        doc = json.loads(out.read_text(encoding="utf-8"))
        print(f"{out}: {len(doc['pages'])} held page(s), {len(doc['captions'])} caption(s) at {SQUINT_W} px wide")
        return 0
    if a.check and (a.band or a.caption_floor):
        bad = (check_band(a.band, a.root) + check_squint_band(a.band, a.root) + check_fills(a.band, a.root)
               + check_spreads(a.band, a.root) if a.band else []) \
            + (check_caption_floor(a.caption_floor, a.root) if a.caption_floor else [])
        print("\n".join(bad) if bad else f"{a.band or a.caption_floor}: every recorded frame reproduces")
        return 1 if bad else 0
    if not (a.frame and a.ink and a.box):
        ap.error("a frame, --ink and --box (or --band --check)")
    if a.spread:
        print(json.dumps(measure_spread(a.frame, a.ink, _box(a.box), end=a.end, exclude=[_box(x) for x in a.exclude],
                                        halo_exclude=[_box(x) for x in a.halo_exclude], ground_from=a.ground_from), indent=1))
        return 0
    if a.fill:
        print(json.dumps(measure_fill(a.frame, a.ink, _box(a.box), exclude=[_box(x) for x in a.exclude],
                                      halo_exclude=[_box(x) for x in a.halo_exclude]), indent=1))
        return 0
    got = measure(a.frame, a.ink, _box(a.box), exclude=[_box(x) for x in a.exclude], title_box=_box(a.title_box),
                  label_box=_box(a.label_box), words=a.words, words_box=_box(a.words_box))
    print(json.dumps(got, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
