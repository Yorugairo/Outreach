"""Every measurement is pinned against an image built here, pixel by pixel.

The real episode-1 library lives in another worktree and is deliberately not a
test dependency — a measurement service whose tests need 25 binary assets is a
service nobody can change. Instead each synthetic image is constructed so its
answer is known by arithmetic before the service runs, which pins the
*definition* rather than a remembered number.

The committed figures from ``23-EP1-LIBRARY-INTAKE-REVIEW.md`` are reproduced by
building assets that must measure exactly those values under the definition, and
would measure something else under a wrong one.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from content.video_engine.src.services.asset_measurement import (
    BUSY_GRADIENT_THRESHOLD,
    COLOUR_BINS_PER_CHANNEL,
    RIGHT_ZONE_START,
    SILHOUETTE_EROSION_RADIUS,
    AssetMeasurementError,
    measure_asset,
    measure_frame,
)

# --- synthetic asset builders --------------------------------------------------

MARGIN = 8
FLAT_GREY = 128
_ERODE = SILHOUETTE_EROSION_RADIUS


def _write(tmp_path: Path, name: str, array: np.ndarray, mode: str = "RGBA") -> Path:
    path = tmp_path / name
    Image.fromarray(array, mode=mode).save(path)
    return path


def _blank_cutout(interior_w: int, interior_h: int, fill: tuple[int, int, int]):
    """An opaque rectangle on a transparent ground.

    Sized so that eroding the silhouette by ``SILHOUETTE_EROSION_RADIUS`` leaves
    exactly ``interior_w`` x ``interior_h`` measurable pixels — the rectangle is
    inset by the radius on all four sides.
    """

    rect_w = interior_w + 2 * _ERODE
    rect_h = interior_h + 2 * _ERODE
    array = np.zeros((rect_h + 2 * MARGIN, rect_w + 2 * MARGIN, 4), dtype=np.uint8)
    rows = slice(MARGIN, MARGIN + rect_h)
    cols = slice(MARGIN, MARGIN + rect_w)
    array[rows, cols, :3] = fill
    array[rows, cols, 3] = 255
    return array, rows, cols


def _cutout_with_busy_band(interior_w: int, interior_h: int, band_rows: int) -> np.ndarray:
    """A flat figure carrying a band of period-4 stripes.

    Period 4 because a checkerboard or period-2 stripe is invisible to a Sobel
    kernel — the symmetric neighbours cancel — so it would silently measure as
    perfectly flat. Every pixel of a period-4 stripe carries a full-amplitude
    step, and the flat ground either side contributes exactly one bleed row above
    and one below, because the kernel reaches one pixel.
    """

    array, rows, cols = _blank_cutout(interior_w, interior_h, (FLAT_GREY,) * 3)
    top = rows.start + (rows.stop - rows.start - band_rows) // 2
    for offset in range(band_rows):
        value = 255 if offset % 4 < 2 else 0
        array[top + offset, cols, :3] = value
    return array


def _band_rows_for(fraction: float, interior_h: int) -> int:
    """Band height that measures ``fraction`` once the two bleed rows are added."""

    return round(fraction * interior_h) - 2


def _flat_colour_cutout(colour: tuple[int, int, int]) -> np.ndarray:
    array, _, _ = _blank_cutout(60, 60, colour)
    return array


def _two_tone_world(
    width: int,
    height: int,
    *,
    zone_start: float,
    zone_pair: tuple[int, int],
    rest_pair: tuple[int, int],
) -> np.ndarray:
    """An opaque plate whose two bands have exact, known luminance sigmas.

    Two grey levels in equal proportion have a standard deviation of exactly half
    their difference, and a neutral grey's luma equals its channel value because
    the ITU-R 601-2 weights sum to one. So sigma is chosen, not approximated.
    """

    array = np.zeros((height, width, 3), dtype=np.uint8)
    split = int(round(width * zone_start))
    for col in range(width):
        low, high = rest_pair if col < split else zone_pair
        array[:, col, :] = low if col % 2 == 0 else high
    return array


# --- internal detail: the committed episode-1 figures ---------------------------

INTERIOR_H = 1000
INTERIOR_W = 200

RECORDED_DETAIL = {
    "host": 0.279,
    "civilian_a": 0.128,
    "objects_and_mechanisms": 0.517,
}


@pytest.mark.parametrize("group,recorded", sorted(RECORDED_DETAIL.items()))
def test_internal_detail_reproduces_the_recorded_episode_1_figure(
    tmp_path: Path, group: str, recorded: float
):
    """Host 27.9%, civilian A 12.8%, objects and mechanisms 51.7%.

    Each figure is built to carry exactly that proportion of busy interior, so a
    definition that eroded by the wrong amount, thresholded elsewhere, or divided
    by the untrimmed silhouette would miss it.
    """

    array = _cutout_with_busy_band(
        INTERIOR_W, INTERIOR_H, _band_rows_for(recorded, INTERIOR_H)
    )
    report = measure_asset(_write(tmp_path, f"{group}.png", array))

    detail = report["internal_detail"]
    assert detail["measured_pixels"] == INTERIOR_W * INTERIOR_H
    assert detail["fraction"] == pytest.approx(recorded, abs=0.0005)


def test_the_recorded_two_to_one_hierarchy_survives_the_definition(tmp_path: Path):
    """Civilian A's internal detail is 46% of the host's, as recorded."""

    host = measure_asset(
        _write(
            tmp_path,
            "host.png",
            _cutout_with_busy_band(INTERIOR_W, INTERIOR_H, _band_rows_for(0.279, INTERIOR_H)),
        )
    )
    civilian = measure_asset(
        _write(
            tmp_path,
            "civilian.png",
            _cutout_with_busy_band(INTERIOR_W, INTERIOR_H, _band_rows_for(0.128, INTERIOR_H)),
        )
    )

    ratio = civilian["internal_detail"]["fraction"] / host["internal_detail"]["fraction"]
    assert round(ratio, 2) == 0.46


def test_erosion_is_what_makes_this_internal_detail_and_not_outline(tmp_path: Path):
    """A perfectly flat figure has a strong outline and no content.

    Without the erosion its silhouette alone scores, which is the exact confusion
    the recorded measurement was defined to avoid.
    """

    array, _, _ = _blank_cutout(INTERIOR_W, 200, (FLAT_GREY,) * 3)
    path = _write(tmp_path, "flat-figure.png", array)

    eroded = measure_asset(path)["internal_detail"]
    raw = measure_asset(path, erosion_radius=0)["internal_detail"]

    assert eroded["fraction"] == 0.0
    assert raw["fraction"] > 0.01
    assert raw["measured_pixels"] > eroded["measured_pixels"]


def test_erosion_trims_exactly_the_radius_from_every_side(tmp_path: Path):
    array, _, _ = _blank_cutout(40, 30, (FLAT_GREY,) * 3)
    path = _write(tmp_path, "rect.png", array)

    assert measure_asset(path)["internal_detail"]["measured_pixels"] == 40 * 30
    assert measure_asset(path, erosion_radius=1)["internal_detail"]["measured_pixels"] == 44 * 34


def test_a_figure_thinner_than_the_erosion_radius_reports_no_measurement(tmp_path: Path):
    """Better than a fraction of nothing: say the interior could not be reached."""

    array = np.zeros((20, 20, 4), dtype=np.uint8)
    array[8:12, 8:12, :3] = FLAT_GREY
    array[8:12, 8:12, 3] = 255

    detail = measure_asset(_write(tmp_path, "sliver.png", array))["internal_detail"]

    assert detail["fraction"] is None
    assert detail["measured_pixels"] == 0


def test_a_full_bleed_opaque_plate_is_measured_edge_to_edge(tmp_path: Path):
    """The frame edge is a crop, not a silhouette, so erosion must not eat it."""

    world = np.full((60, 90, 3), FLAT_GREY, dtype=np.uint8)
    report = measure_asset(_write(tmp_path, "world.png", world, mode="RGB"))

    assert report["internal_detail"]["measured_pixels"] == 60 * 90
    assert report["frame_occupancy"] == 1.0


def test_the_busy_threshold_is_a_named_parameter_not_a_hidden_constant(tmp_path: Path):
    """A step of 30 levels counts at the default threshold and not above it."""

    array, rows, cols = _blank_cutout(40, 40, (FLAT_GREY,) * 3)
    for offset in range(rows.stop - rows.start):
        if offset % 4 < 2:
            array[rows.start + offset, cols, :3] = FLAT_GREY + 30

    path = _write(tmp_path, "gentle.png", array)

    assert measure_asset(path)["internal_detail"]["fraction"] > 0.9
    assert measure_asset(path, busy_threshold=60.0)["internal_detail"]["fraction"] == 0.0
    assert BUSY_GRADIENT_THRESHOLD == 20.0


# --- frame occupancy -----------------------------------------------------------


def test_frame_occupancy_is_the_opaque_share_of_the_whole_plate(tmp_path: Path):
    array = np.zeros((100, 200, 4), dtype=np.uint8)
    array[10:60, 20:120, :3] = FLAT_GREY
    array[10:60, 20:120, 3] = 255

    report = measure_asset(_write(tmp_path, "occupancy.png", array))

    assert report["frame_occupancy"] == pytest.approx((50 * 100) / (100 * 200))
    assert report["alpha"]["fully_transparent_fraction"] == pytest.approx(1 - 0.25)


def test_partially_transparent_pixels_are_not_counted_as_occupancy(tmp_path: Path):
    array = np.zeros((10, 10, 4), dtype=np.uint8)
    array[..., :3] = FLAT_GREY
    array[2:8, 2:8, 3] = 255
    array[1, 1, 3] = 128

    report = measure_asset(_write(tmp_path, "partial.png", array))

    assert report["frame_occupancy"] == pytest.approx(36 / 100)
    assert report["alpha"]["partial_pixel_count"] == 1


# --- saturation and brightness --------------------------------------------------

# Recorded in the review across all fifteen poses, alongside the detail figures.
RECORDED_TONE = {
    "host": ((105, 105, 35), 0.665, 0.414),
    "civilian_a": ((87, 87, 57), 0.347, 0.341),
    "civilian_b": ((120, 120, 73), 0.391, 0.473),
}


@pytest.mark.parametrize("group,colour,saturation,brightness", [
    (name, colour, sat, bright) for name, (colour, sat, bright) in sorted(RECORDED_TONE.items())
])
def test_mean_saturation_and_brightness_reproduce_the_recorded_figures(
    tmp_path: Path,
    group: str,
    colour: tuple[int, int, int],
    saturation: float,
    brightness: float,
):
    report = measure_asset(_write(tmp_path, f"{group}.png", _flat_colour_cutout(colour)))

    assert report["colour"]["mean_saturation"] == pytest.approx(saturation, abs=0.005)
    assert report["colour"]["mean_brightness"] == pytest.approx(brightness, abs=0.005)


def test_civilian_a_measures_roughly_half_the_hosts_saturation(tmp_path: Path):
    host = measure_asset(
        _write(tmp_path, "host.png", _flat_colour_cutout(RECORDED_TONE["host"][0]))
    )
    civilian = measure_asset(
        _write(tmp_path, "civ.png", _flat_colour_cutout(RECORDED_TONE["civilian_a"][0]))
    )

    ratio = civilian["colour"]["mean_saturation"] / host["colour"]["mean_saturation"]
    assert round(ratio, 2) == 0.52


def test_tone_is_measured_over_opaque_pixels_only(tmp_path: Path):
    """A bright transparent ground must not brighten the figure standing on it."""

    array = np.zeros((20, 20, 4), dtype=np.uint8)
    array[..., :3] = 255
    array[5:15, 5:15, :3] = (0, 0, 0)
    array[5:15, 5:15, 3] = 255

    colour = measure_asset(_write(tmp_path, "dark-on-white.png", array))["colour"]

    assert colour["mean_brightness"] == 0.0
    assert colour["mean_saturation"] == 0.0


# --- distinct colours -----------------------------------------------------------


def test_distinct_colours_counts_occupied_bins_not_raw_values(tmp_path: Path):
    """Two values inside one 8x8x8 bin are one colour; crossing a bin edge is two."""

    step = 256 // COLOUR_BINS_PER_CHANNEL
    same_bin = np.zeros((1, 2, 4), dtype=np.uint8)
    same_bin[0, 0, :3] = (0, 0, 0)
    same_bin[0, 1, :3] = (step - 1, step - 1, step - 1)
    same_bin[..., 3] = 255

    crossing = same_bin.copy()
    crossing[0, 1, :3] = (step, 0, 0)

    assert measure_asset(_write(tmp_path, "same.png", same_bin))["colour"]["distinct_colours"] == 1
    assert measure_asset(_write(tmp_path, "cross.png", crossing))["colour"]["distinct_colours"] == 2


def test_a_plate_built_with_126_distinct_bins_measures_126(tmp_path: Path):
    """126 is the host's recorded distinct-colour count."""

    step = 256 // COLOUR_BINS_PER_CHANNEL
    array = np.zeros((1, 126, 4), dtype=np.uint8)
    for index in range(126):
        array[0, index, :3] = (
            (index // 64) * step,
            ((index // 8) % 8) * step,
            (index % 8) * step,
        )
    array[..., 3] = 255

    assert measure_asset(_write(tmp_path, "palette.png", array))["colour"]["distinct_colours"] == 126


def test_transparent_pixels_contribute_no_colours(tmp_path: Path):
    step = 256 // COLOUR_BINS_PER_CHANNEL
    array = np.zeros((1, 6, 4), dtype=np.uint8)
    for index in range(6):
        array[0, index, :3] = (index * step, 0, 0)
    array[0, :2, 3] = 255

    assert measure_asset(_write(tmp_path, "mixed.png", array))["colour"]["distinct_colours"] == 2


# --- alpha presence and the halo test -------------------------------------------


def _rimmed_cutout(rim_colour: tuple[int, int, int], rim_alpha: int = 128) -> np.ndarray:
    array = np.zeros((20, 20, 4), dtype=np.uint8)
    array[4:16, 4:16, :3] = rim_colour
    array[4:16, 4:16, 3] = rim_alpha
    array[6:14, 6:14, :3] = (FLAT_GREY,) * 3
    array[6:14, 6:14, 3] = 255
    return array


def test_the_halo_test_reports_the_mean_colour_of_the_partial_rim(tmp_path: Path):
    """A dark antialias rim, as the accepted civilians carry."""

    report = measure_asset(_write(tmp_path, "dark-rim.png", _rimmed_cutout((50, 45, 40))))

    alpha = report["alpha"]
    assert alpha["edge_mean_rgb"] == pytest.approx([50.0, 45.0, 40.0])
    assert alpha["partial_pixel_count"] == 12 * 12 - 8 * 8
    assert alpha["partial_fraction_of_frame"] == pytest.approx(80 / 400)
    assert alpha["partial_fraction_of_figure"] == pytest.approx(80 / 144)


def test_a_cream_rim_is_reported_as_a_number_and_never_judged(tmp_path: Path):
    """The library ground is cream #F4E6C7. The service names it; it does not rule."""

    report = measure_asset(_write(tmp_path, "cream-rim.png", _rimmed_cutout((244, 230, 199))))

    assert report["alpha"]["edge_mean_rgb"] == pytest.approx([244.0, 230.0, 199.0])


def test_an_opaque_plate_reports_no_alpha_and_no_edge_colour(tmp_path: Path):
    world = np.full((30, 40, 3), FLAT_GREY, dtype=np.uint8)

    alpha = measure_asset(_write(tmp_path, "flat-world.png", world, mode="RGB"))["alpha"]

    assert alpha["has_alpha"] is False
    assert alpha["opaque_fraction"] == 1.0
    assert alpha["fully_transparent_fraction"] == 0.0
    assert alpha["partial_pixel_count"] == 0
    assert alpha["edge_mean_rgb"] is None


def test_an_rgba_plate_with_no_transparent_pixel_still_reports_alpha_presence(tmp_path: Path):
    """Presence is a property of the file, not of whether it happened to be used."""

    array = np.zeros((10, 10, 4), dtype=np.uint8)
    array[..., :3] = FLAT_GREY
    array[..., 3] = 255

    report = measure_asset(_write(tmp_path, "opaque-rgba.png", array))

    assert report["mode"] == "RGBA"
    assert report["alpha"]["has_alpha"] is True
    assert report["alpha"]["opaque_fraction"] == 1.0


# --- world clear zone ------------------------------------------------------------

# From the review's world table: a right third at sigma 4.9-7.6 against a body at
# 62-71 is genuinely empty wall.
RECORDED_ZONE_BAND = (4.9, 7.6)
RECORDED_REST_BAND = (62.0, 71.0)


@pytest.mark.parametrize("zone_pair,rest_pair,zone_sigma,rest_sigma", [
    ((120, 130), (58, 198), 5.0, 70.0),
    ((120, 135), (65, 191), 7.5, 63.0),
])
def test_clear_zone_flatness_reproduces_the_recorded_world_band(
    tmp_path: Path,
    zone_pair: tuple[int, int],
    rest_pair: tuple[int, int],
    zone_sigma: float,
    rest_sigma: float,
):
    world = _two_tone_world(
        1536, 64, zone_start=RIGHT_ZONE_START, zone_pair=zone_pair, rest_pair=rest_pair
    )
    report = measure_asset(
        _write(tmp_path, "world.png", world, mode="RGB"), clear_zone_start=RIGHT_ZONE_START
    )

    # The construction sits inside the recorded band by exact arithmetic, and the
    # service measures the construction back. Two steps, so a float epsilon in the
    # measurement can never be mistaken for a band failure.
    assert RECORDED_ZONE_BAND[0] <= zone_sigma <= RECORDED_ZONE_BAND[1]
    assert RECORDED_REST_BAND[0] <= rest_sigma <= RECORDED_REST_BAND[1]

    zone = report["clear_zone"]
    assert zone["zone_sigma"] == pytest.approx(zone_sigma, abs=0.01)
    assert zone["rest_sigma"] == pytest.approx(rest_sigma, abs=0.01)
    assert zone["ratio"] == pytest.approx(zone_sigma / rest_sigma, abs=0.001)


def test_the_clear_zone_split_follows_the_worlds_declared_figure_zone(tmp_path: Path):
    """Worlds declare figure_zone [0.45, 1.0] and [0.55, 1.0]; the split follows."""

    world = _two_tone_world(
        1000, 20, zone_start=0.45, zone_pair=(120, 130), rest_pair=(58, 198)
    )
    path = _write(tmp_path, "wide-zone.png", world, mode="RGB")

    declared = measure_asset(path, clear_zone_start=0.45)["clear_zone"]
    default = measure_asset(path, clear_zone_start=RIGHT_ZONE_START)["clear_zone"]

    assert declared["split_column"] == 450
    assert declared["zone_sigma"] == pytest.approx(5.0, abs=0.01)
    # Measured at the wrong split, part of the busy body lands inside the "zone".
    assert default["split_column"] == round(1000 * RIGHT_ZONE_START)
    assert default["zone_sigma"] == pytest.approx(5.0, abs=0.01)
    assert default["rest_sigma"] < declared["rest_sigma"]


def test_the_clear_zone_block_is_absent_unless_it_is_asked_for(tmp_path: Path):
    """Only a world has a clear zone; a cutout must not be given a meaningless one."""

    array, _, _ = _blank_cutout(30, 30, (FLAT_GREY,) * 3)

    assert measure_asset(_write(tmp_path, "cutout.png", array))["clear_zone"] is None


def test_a_clear_zone_start_outside_the_frame_is_refused_by_name(tmp_path: Path):
    world = np.full((20, 20, 3), FLAT_GREY, dtype=np.uint8)
    path = _write(tmp_path, "world.png", world, mode="RGB")

    with pytest.raises(AssetMeasurementError) as excinfo:
        measure_asset(path, clear_zone_start=1.0)

    assert "clear_zone_start" in " ".join(excinfo.value.errors)


# --- inputs, determinism, and the no-verdict rule ---------------------------------


def test_a_missing_file_is_refused_with_its_path(tmp_path: Path):
    with pytest.raises(AssetMeasurementError) as excinfo:
        measure_asset(tmp_path / "not-there.png")

    assert "not-there.png" in " ".join(excinfo.value.errors)


def test_a_file_that_is_not_an_image_is_refused_rather_than_crashing(tmp_path: Path):
    path = tmp_path / "notes.png"
    path.write_text("this is not a png", encoding="utf-8")

    with pytest.raises(AssetMeasurementError):
        measure_asset(path)


def test_measure_frame_refuses_an_array_that_is_not_rgb():
    with pytest.raises(AssetMeasurementError) as excinfo:
        measure_frame(np.zeros((4, 4), dtype=np.uint8))

    assert "RGB" in " ".join(excinfo.value.errors)


def test_measure_frame_refuses_an_alpha_channel_of_the_wrong_shape():
    with pytest.raises(AssetMeasurementError) as excinfo:
        measure_frame(np.zeros((4, 4, 3), dtype=np.uint8), np.zeros((5, 5), dtype=np.uint8))

    assert "alpha shape" in " ".join(excinfo.value.errors)


def test_measuring_the_same_asset_twice_returns_the_same_numbers(tmp_path: Path):
    array = _cutout_with_busy_band(40, 60, 20)
    path = _write(tmp_path, "stable.png", array)

    assert measure_asset(path, clear_zone_start=0.5) == measure_asset(path, clear_zone_start=0.5)


_VERDICT_KEYS = frozenset({
    "verdict", "status", "state", "pass", "passed", "fail", "failed", "flag",
    "flagged", "clean", "ok", "score", "grade", "acceptable", "too_busy",
    "render_eligible", "review_state",
})


def test_the_report_carries_measurements_only_and_never_a_verdict(tmp_path: Path):
    """Interpretation belongs to the caller. A threshold here would be a second
    implementation of a rule the verdict pack owns."""

    array = _cutout_with_busy_band(INTERIOR_W, 200, 60)
    report = measure_asset(_write(tmp_path, "asset.png", array), clear_zone_start=0.5)

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                assert key not in _VERDICT_KEYS, f"{key} is a judgement, not a measurement"
                walk(value)

    walk(report)
    assert set(report) == {
        "path", "mode", "size", "frame_occupancy", "internal_detail", "alpha",
        "colour", "clear_zone",
    }


def test_a_cutout_whose_alpha_never_reaches_255_is_still_measured():
    """Real cutouts do not reliably hit alpha 255.

    The episode-1 host tops out at 254 across the entire plate. Testing opacity
    with `alpha == 255` classified the whole figure as non-opaque and returned
    `fraction: None` — a silent total failure that every synthetic fixture missed,
    because fixtures are built with alpha exactly 255.
    """

    rgb = np.zeros((80, 80, 3), dtype=np.float64)
    rgb[20:60, 20:60] = 200.0
    alpha = np.zeros((80, 80), dtype=np.uint8)
    alpha[20:60, 20:60] = 254

    report = measure_frame(rgb, alpha)

    assert report["internal_detail"]["measured_pixels"] > 0
    assert report["internal_detail"]["fraction"] is not None
    assert report["frame_occupancy"] > 0
