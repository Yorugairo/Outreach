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

    python measure_line_bloom.py FRAME --ink "#34F5C5" --box 150,250,1098,820 [--title-box ..] [--label-box ..] [--words N]
    python measure_line_bloom.py --band content/video_engine/assets/bravos-line-bloom.v1.json --check
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


def squint(rgb: np.ndarray, box, lit_zone: np.ndarray, g: float) -> float:
    """The lit line's share of the plot's visible contrast at 320 px wide."""
    h, w = rgb.shape[:2]
    sh = round(h * SQUINT_W / w)
    small = np.asarray(Image.fromarray((rgb * 255).round().astype(np.uint8)).resize((SQUINT_W, sh), Image.LANCZOS))
    lu = luma(small.astype(np.float64) / 255.0)
    zone = np.asarray(Image.fromarray(lit_zone.astype(np.float32)).resize((SQUINT_W, sh), Image.BOX))
    k = SQUINT_W / w
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
    a = ap.parse_args(argv)
    if a.band and a.check:
        bad = check_band(a.band, a.root)
        print("\n".join(bad) if bad else f"{a.band}: every recorded frame reproduces")
        return 1 if bad else 0
    if not (a.frame and a.ink and a.box):
        ap.error("a frame, --ink and --box (or --band --check)")
    got = measure(a.frame, a.ink, _box(a.box), exclude=[_box(x) for x in a.exclude], title_box=_box(a.title_box),
                  label_box=_box(a.label_box), words=a.words, words_box=_box(a.words_box))
    print(json.dumps(got, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
