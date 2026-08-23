"""Asset measurement — the numbers, and nothing else.

The episode-1 intake was settled by measurement, not by opinion. "The props are
too busy" was an argument; *internal detail 51.7% against the host's 27.9%* was a
fact two people could check. Every one of those numbers was produced by throwaway
Python that no longer exists, so the next review would have started from opinion
again. This module is that arithmetic, kept.

**It reports and never judges.** No thresholds, no verdicts, no pass/fail. Whether
51.7% is too much depends on the asset's kind, tier and role in a frame — that is
the caller's call (T4's verdict pack), and putting it here would make the same
rule live in two places.

Two measurements need explaining, because the naive version of each is wrong:

*Internal detail* is the fraction of pixels carrying a real luminance step, with
the cutout silhouette **eroded away first**. Without the erosion a plain figure on
a transparent ground scores high purely for having an outline, and the number
stops meaning "how much is going on inside this asset" — which is the only
question worth asking of it.

*The halo test* looks at partially transparent pixels only. A cutout generated on
a cream ground and matted out badly keeps a rim of that ground; the rim's mean
colour is the evidence. Reporting the rim's mean RGB lets a reader see a cream
halo without the module having to decide what cream is.

Reads one image and touches nothing else. ``measure_frame`` is the whole
computation as pure arithmetic over arrays; ``measure_asset`` is the thin wrapper
that opens a file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np
from PIL import Image
from scipy import ndimage

#: An alpha value is either fully opaque, fully transparent, or an edge pixel.
OPAQUE_ALPHA = 255
#: A pixel counts as opaque at or above this alpha, rather than at exactly 255.
#: Real cutouts do not reliably reach 255 — the episode-1 host tops out at 254
#: across the whole plate — and a strict equality test silently classified the
#: entire figure as non-opaque and returned no measurement at all.
OPAQUE_ALPHA_MIN = 250

#: Sobel returns 4x the amplitude of a one-pixel luminance step, so dividing by
#: this puts the gradient back in "levels of luminance change" units. A threshold
#: is then readable: 20 means "at least 20 of 255 levels across a pixel".
SOBEL_STEP_SCALE = 4.0
BUSY_GRADIENT_THRESHOLD = 20.0
#
# Calibrated against the real episode-1 library, not chosen blind. At 20.0 the
# service measures host 30.0%, civilian A 10.4%, objects 50.2% against the
# figures committed in 23-EP1-LIBRARY-INTAKE-REVIEW.md of 27.9 / 12.8 / 51.7 —
# every group within 2.4 points. A sweep from 6 to 20 showed error falling
# monotonically to this value.
#
# The residual is real and worth knowing: the committed figures came from a
# central-difference gradient at threshold 12, this uses Sobel/4 at 20, and no
# single threshold reconciles all three groups because the two operators weight
# edges differently. The hierarchy claim survives — host is still far busier than
# a civilian — but the exact ratio moves from 2.2:1 to 2.9:1 depending on the
# operator, so quote the ratio as approximate, never as a measured constant.

#: How far the silhouette is eaten back before internal detail is measured. Three
#: pixels clears a typical antialias rim (1-2px) plus the 1px reach of the Sobel
#: kernel, so no part of the outline can be counted as content.
SILHOUETTE_EROSION_RADIUS = 3

#: Distinct-colour count quantises to this many bins per channel: 8x8x8 = 512
#: possible colours. Fine enough to separate a palette, coarse enough that
#: antialiasing and compression noise do not read as extra colours.
COLOUR_BINS_PER_CHANNEL = 8

#: The recorded episode-1 clear-zone measurement split the frame here. Worlds now
#: declare their own ``placement.figure_zone``, so callers should pass that
#: instead; this is the default the committed figures were taken at.
RIGHT_ZONE_START = 2.0 / 3.0

#: ITU-R 601-2 luma, the same transform Pillow's "L" conversion uses.
_LUMA_WEIGHTS = (0.299, 0.587, 0.114)

_ALPHA_MODES = frozenset({"RGBA", "RGBa", "LA", "La", "PA"})


class AssetMeasurementError(ValueError):
    """The asset cannot be measured as asked."""

    def __init__(self, errors: Sequence[str]):
        self.errors = [str(item) for item in errors]
        super().__init__("; ".join(self.errors) or "cannot measure asset")


def _luma(rgb: np.ndarray) -> np.ndarray:
    red, green, blue = (rgb[..., i].astype(np.float64) for i in range(3))
    r_w, g_w, b_w = _LUMA_WEIGHTS
    return red * r_w + green * g_w + blue * b_w


def _gradient_magnitude(luma: np.ndarray) -> np.ndarray:
    """Sobel magnitude in luminance levels per pixel.

    ``mode="nearest"`` rather than the default reflect: reflecting at the frame
    edge invents a gradient that is not in the picture.
    """

    gy = ndimage.sobel(luma, axis=0, mode="nearest")
    gx = ndimage.sobel(luma, axis=1, mode="nearest")
    return np.hypot(gx, gy) / SOBEL_STEP_SCALE


def _erode(mask: np.ndarray, radius: int) -> np.ndarray:
    """Eat ``radius`` pixels off every edge of ``mask``.

    ``border_value=1`` on purpose: the frame edge is a crop, not a silhouette, so
    a full-bleed world keeps its whole area and a figure standing on the bottom
    edge is not shaved for it. ``iterations`` below 1 means "erode to convergence"
    in scipy, which is never what a radius of zero should mean, so that case skips
    erosion outright.
    """

    if radius < 1:
        return mask
    structure = ndimage.generate_binary_structure(2, 2)
    return ndimage.binary_erosion(
        mask, structure=structure, iterations=int(radius), border_value=1
    )


def _internal_detail(
    luma: np.ndarray,
    opaque: np.ndarray,
    *,
    erosion_radius: int,
    busy_threshold: float,
) -> dict[str, Any]:
    interior = _erode(opaque, erosion_radius)
    measured = int(interior.sum())
    if measured == 0:
        # Thinner than the erosion radius, or nothing opaque at all. Saying so
        # beats reporting a fraction of nothing.
        return {
            "fraction": None,
            "busy_pixels": 0,
            "measured_pixels": 0,
            "erosion_radius": int(erosion_radius),
            "busy_threshold": float(busy_threshold),
        }

    busy = int(((_gradient_magnitude(luma) >= busy_threshold) & interior).sum())
    return {
        "fraction": busy / measured,
        "busy_pixels": busy,
        "measured_pixels": measured,
        "erosion_radius": int(erosion_radius),
        "busy_threshold": float(busy_threshold),
    }


def _alpha_report(alpha: np.ndarray, rgb: np.ndarray, *, has_alpha: bool) -> dict[str, Any]:
    total = int(alpha.size)
    opaque = alpha >= OPAQUE_ALPHA_MIN
    clear = alpha == 0
    partial = ~opaque & ~clear
    present = ~clear

    partial_count = int(partial.sum())
    present_count = int(present.sum())
    edge_mean = (
        [float(rgb[..., i][partial].mean()) for i in range(3)] if partial_count else None
    )

    return {
        "has_alpha": bool(has_alpha),
        "opaque_fraction": float(opaque.sum()) / total,
        "fully_transparent_fraction": float(clear.sum()) / total,
        # Two denominators because "1-9% of each figure" is genuinely ambiguous:
        # of the whole plate, or of the figure standing in it. Both are cheap.
        "partial_fraction_of_frame": partial_count / total,
        "partial_fraction_of_figure": (
            partial_count / present_count if present_count else None
        ),
        "partial_pixel_count": partial_count,
        "edge_mean_rgb": edge_mean,
    }


def _colour_report(rgb: np.ndarray, opaque: np.ndarray) -> dict[str, Any]:
    if not opaque.any():
        return {
            "mean_saturation": None,
            "mean_brightness": None,
            "distinct_colours": 0,
            "bins_per_channel": COLOUR_BINS_PER_CHANNEL,
        }

    picked = rgb[opaque]
    channels = picked.astype(np.float64)
    high = channels.max(axis=1)
    low = channels.min(axis=1)
    # HSV value and saturation. Saturation is undefined on pure black; the usual
    # convention is zero, and the guarded divisor keeps numpy from warning.
    brightness = high / 255.0
    divisor = np.where(high > 0, high, 1.0)
    saturation = np.where(high > 0, (high - low) / divisor, 0.0)

    step = 256 // COLOUR_BINS_PER_CHANNEL
    binned = picked.astype(np.int64) // step
    keys = (
        binned[:, 0] * COLOUR_BINS_PER_CHANNEL**2
        + binned[:, 1] * COLOUR_BINS_PER_CHANNEL
        + binned[:, 2]
    )

    return {
        "mean_saturation": float(saturation.mean()),
        "mean_brightness": float(brightness.mean()),
        "distinct_colours": int(np.unique(keys).size),
        "bins_per_channel": COLOUR_BINS_PER_CHANNEL,
    }


def _band_sigma(luma: np.ndarray, opaque: np.ndarray) -> float | None:
    values = luma[opaque]
    if values.size == 0:
        return None
    return float(values.std())


def _clear_zone_report(
    luma: np.ndarray, opaque: np.ndarray, *, zone_start: float
) -> dict[str, Any]:
    """Luminance flatness of the clear zone against the rest of the plate.

    A world earns a composited figure by having somewhere empty to put one. Sigma
    says how empty: flat wall varies by a few levels, drawn furniture by dozens.
    """

    if not 0.0 <= zone_start < 1.0:
        raise AssetMeasurementError([
            f"clear_zone_start must be at least 0.0 and below 1.0, got {zone_start}"
        ])

    width = luma.shape[1]
    split = int(round(width * zone_start))
    zone_sigma = _band_sigma(luma[:, split:], opaque[:, split:])
    rest_sigma = _band_sigma(luma[:, :split], opaque[:, :split])
    ratio = (
        zone_sigma / rest_sigma
        if zone_sigma is not None and rest_sigma not in (None, 0.0)
        else None
    )

    return {
        "zone_start": float(zone_start),
        "split_column": split,
        "zone_sigma": zone_sigma,
        "rest_sigma": rest_sigma,
        "ratio": ratio,
    }


def measure_frame(
    rgb: np.ndarray,
    alpha: np.ndarray | None = None,
    *,
    has_alpha: bool | None = None,
    clear_zone_start: float | None = None,
    erosion_radius: int = SILHOUETTE_EROSION_RADIUS,
    busy_threshold: float = BUSY_GRADIENT_THRESHOLD,
) -> dict[str, Any]:
    """Measure one frame of pixels. Pure arithmetic — no files, no verdicts.

    ``rgb`` is ``(h, w, 3)`` of ``uint8``; ``alpha`` is ``(h, w)`` or ``None`` for
    an opaque plate. ``clear_zone_start`` asks for the right-zone flatness block,
    which only means anything for a world — pass the world's declared
    ``placement.figure_zone[0]``, or ``RIGHT_ZONE_START`` for the split the
    episode-1 figures were recorded at.
    """

    rgb = np.asarray(rgb)
    if rgb.ndim != 3 or rgb.shape[2] < 3:
        raise AssetMeasurementError([
            f"expected an (h, w, 3) RGB array, got shape {rgb.shape}"
        ])
    rgb = rgb[..., :3]

    if alpha is None:
        alpha = np.full(rgb.shape[:2], OPAQUE_ALPHA, dtype=np.uint8)
    alpha = np.asarray(alpha)
    if alpha.shape != rgb.shape[:2]:
        raise AssetMeasurementError([
            f"alpha shape {alpha.shape} does not match rgb shape {rgb.shape[:2]}"
        ])

    opaque = alpha >= OPAQUE_ALPHA_MIN
    luma = _luma(rgb)
    # Callers reading a file know the mode; callers passing arrays do not, so fall
    # back to what the channel itself shows.
    carries_alpha = bool(alpha.min() < OPAQUE_ALPHA_MIN) if has_alpha is None else has_alpha

    report: dict[str, Any] = {
        "size": [int(rgb.shape[1]), int(rgb.shape[0])],
        "frame_occupancy": float(opaque.sum()) / int(alpha.size),
        "internal_detail": _internal_detail(
            luma, opaque, erosion_radius=erosion_radius, busy_threshold=busy_threshold
        ),
        "alpha": _alpha_report(alpha, rgb, has_alpha=carries_alpha),
        "colour": _colour_report(rgb, opaque),
        "clear_zone": None,
    }
    if clear_zone_start is not None:
        report["clear_zone"] = _clear_zone_report(luma, opaque, zone_start=clear_zone_start)
    return report


def measure_asset(
    path: str | Path,
    *,
    clear_zone_start: float | None = None,
    erosion_radius: int = SILHOUETTE_EROSION_RADIUS,
    busy_threshold: float = BUSY_GRADIENT_THRESHOLD,
) -> dict[str, Any]:
    """Open one asset and measure it. The only I/O in this module."""

    src = Path(path)
    if not src.exists():
        raise AssetMeasurementError([f"{src}: no file to measure"])

    try:
        with Image.open(src) as im:
            mode = im.mode
            has_alpha = mode in _ALPHA_MODES or "transparency" in im.info
            rgba = np.asarray(im.convert("RGBA"), dtype=np.uint8)
    except OSError as exc:
        raise AssetMeasurementError([f"{src}: cannot be read as an image ({exc})"]) from exc

    report = measure_frame(
        rgba[..., :3],
        rgba[..., 3],
        has_alpha=has_alpha,
        clear_zone_start=clear_zone_start,
        erosion_radius=erosion_radius,
        busy_threshold=busy_threshold,
    )
    return {"path": str(src), "mode": mode, **report}
