"""P58 T1 route (b): the depth split's pure functions and its serverless `--depth` path, and P61 T14b's
EDGE PASS (E99 s63 - a layered plate ships the processed planes, never the split's raw matte).

No ComfyUI is touched here - the server path is exercised only by the run. Every test below runs on a
synthetic plate with a hand-made depth map.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import comfy_depth_split as cds  # noqa: E402


# ---------------------------------------------------------------- band_edges


def _gradient(h: int = 64, w: int = 64) -> np.ndarray:
    """A left-to-right ramp in [0,1] - far on the left, near on the right."""
    return np.tile(np.linspace(0.0, 1.0, w), (h, 1))


def test_band_edges_are_monotone_and_span_the_depth():
    edges = cds.band_edges(_gradient(), 4)
    assert len(edges) == 5
    assert all(edges[i] < edges[i + 1] for i in range(4)), edges
    assert edges[0] == pytest.approx(0.0)
    assert edges[-1] == pytest.approx(1.0)


def test_band_edges_put_every_pixel_in_exactly_one_band():
    depth = _gradient()
    masks = cds.band_masks(depth, cds.band_edges(depth, 4))
    stack = np.stack(masks).astype(int).sum(axis=0)
    assert stack.min() == 1 and stack.max() == 1


def test_band_edges_on_a_gradient_split_the_frame_about_evenly():
    depth = _gradient(64, 64)
    masks = cds.band_masks(depth, cds.band_edges(depth, 4))
    shares = [float(m.mean()) for m in masks]
    assert sum(shares) == pytest.approx(1.0)
    assert all(0.15 < s < 0.35 for s in shares), shares


def test_band_edges_stay_monotone_on_a_flat_depth_map():
    flat = np.full((16, 16), 0.5)
    edges = cds.band_edges(flat, 4)
    assert all(edges[i] < edges[i + 1] for i in range(4)), edges
    masks = cds.band_masks(flat, edges)
    assert np.stack(masks).astype(int).sum(axis=0).max() == 1


def test_band_edges_refuses_fewer_than_two_bands():
    with pytest.raises(ValueError):
        cds.band_edges(_gradient(), 1)


def test_hand_edges_override_the_quantiles():
    depth = _gradient(32, 32)
    masks = cds.band_masks(depth, [0.0, 0.1, 0.2, 0.3, 1.0])
    assert masks[-1].mean() > 0.6  # the near band swallows the frame by construction


# ---------------------------------------------------------------- the dilation


@pytest.mark.parametrize("sigma,expected", [(0.0, 12), (2.0, 16), (2.5, 17), (3.0, 18)])
def test_grow_radius_is_doc45_ceil_two_sigma_plus_twelve(sigma, expected):
    assert cds.grow_radius(sigma) == expected == math.ceil(2 * sigma) + 12


def test_dilation_grows_a_dot_by_exactly_the_radius():
    m = np.zeros((81, 81), dtype=bool)
    m[40, 40] = True
    grown = cds.dilate(m, cds.grow_radius(2.0))  # 16 px
    row = np.where(grown[40])[0]
    assert row.min() == 24 and row.max() == 56


def test_hole_mask_is_the_margin_eaten_out_of_the_nearer_bands():
    depth = _gradient(64, 64)
    masks = cds.band_masks(depth, cds.band_edges(depth, 4))
    alpha, hole = cds.layer_alpha_and_hole(masks, 1, 2.0)
    nearer = masks[2] | masks[3]
    assert (hole & ~nearer).sum() == 0          # a hole only ever sits under a nearer band
    assert (hole & masks[1]).sum() == 0          # never over the layer's own pixels
    assert np.array_equal(alpha, masks[1] | hole)
    assert hole.any()


def test_the_far_layer_is_opaque_and_holes_everything_nearer():
    depth = _gradient(32, 32)
    masks = cds.band_masks(depth, cds.band_edges(depth, 4))
    alpha, hole = cds.layer_alpha_and_hole(masks, 0, 2.0)
    assert alpha.all()
    assert np.array_equal(hole, masks[1] | masks[2] | masks[3])


def test_the_nearest_layer_is_never_inpainted():
    depth = _gradient(32, 32)
    masks = cds.band_masks(depth, cds.band_edges(depth, 4))
    alpha, hole = cds.layer_alpha_and_hole(masks, 3, 2.0)
    assert not hole.any()
    assert np.array_equal(alpha, masks[3])


# ---------------------------------------------------------------- the Lab match


def test_lab_match_pulls_a_flat_patch_onto_its_ring():
    rgb = np.full((64, 64, 3), 120, dtype=np.uint8)
    rng = np.random.default_rng(0)
    rgb[:] = np.clip(rng.normal(120, 8, rgb.shape), 0, 255).astype(np.uint8)
    region = np.zeros((64, 64), dtype=bool)
    region[24:40, 24:40] = True
    rgb[region] = 30  # a dead grey patch, nothing like its surround
    ring = cds.ring_of(region, 6)
    out = cds.lab_match(rgb, region, ring)
    before = abs(float(rgb[region].mean()) - float(rgb[ring].mean()))
    after = abs(float(out[region].mean()) - float(out[ring].mean()))
    assert after < before / 4, (before, after)


def test_lab_match_never_mutates_its_input_and_leaves_the_ring_alone():
    rgb = np.full((32, 32, 3), 100, dtype=np.uint8)
    region = np.zeros((32, 32), dtype=bool)
    region[10:20, 10:20] = True
    ring = cds.ring_of(region, 4)
    keep = rgb.copy()
    out = cds.lab_match(rgb, region, ring)
    assert np.array_equal(rgb, keep)
    assert out is not rgb


def test_lab_match_is_a_no_op_with_an_empty_region():
    rgb = np.full((8, 8, 3), 77, dtype=np.uint8)
    empty = np.zeros((8, 8), dtype=bool)
    assert np.array_equal(cds.lab_match(rgb, empty, ~empty), rgb)


# ---------------------------------------------------------------- the --depth path


def _synthetic_plate(tmp_path: Path) -> tuple[Path, Path]:
    """A 64x64 plate with four visible depth steps, and its hand-made depth map."""
    rng = np.random.default_rng(7)
    rgb = np.zeros((64, 64, 3), dtype=np.uint8)
    depth = np.zeros((64, 64), dtype=np.uint8)
    for i, (lo, hi) in enumerate([(0, 16), (16, 32), (32, 48), (48, 64)]):
        rgb[:, lo:hi] = np.clip(rng.normal(40 + 60 * i, 6, (64, hi - lo, 3)), 0, 255).astype(np.uint8)
        depth[:, lo:hi] = 30 + 70 * i
    plate = tmp_path / "synthetic-plate.png"
    dmap = tmp_path / "synthetic-depth.png"
    Image.fromarray(rgb).save(plate)
    Image.fromarray(depth, mode="L").save(dmap)
    return plate, dmap


def test_depth_path_writes_four_rgba_layers_with_the_far_one_opaque(tmp_path):
    plate, dmap = _synthetic_plate(tmp_path)
    out = tmp_path / "split"
    meta = cds.split(plate, out, depth_png=dmap, inpainter="telea-fallback")

    for role in cds.ROLES:
        f = out / f"synthetic-plate-{role}.png"
        assert f.exists(), f
        im = Image.open(f)
        assert im.mode == "RGBA" and im.size == (64, 64)
    assert (out / "synthetic-plate-depth.png").exists()
    assert (out / "synthetic-plate.split.json").exists()

    far = np.asarray(Image.open(out / "synthetic-plate-far.png"))
    assert (far[..., 3] == 255).all(), "the far plane must ship opaque (doc 24 :168)"
    near = np.asarray(Image.open(out / "synthetic-plate-near.png"))
    assert (near[..., 3] == 0).any(), "the near occluder must be cut out"

    assert meta["inpainter"] == "telea-fallback"
    assert [lay["role"] for lay in meta["layers"]] == list(cds.ROLES)
    assert [lay["parallax_factor"] for lay in meta["layers"]] == [1.00, 1.15, 1.15, 1.40]
    assert meta["grow_px"] == 16
    assert meta["size"] == [64, 64]


def test_the_split_json_records_monotone_edges_and_shares_that_sum_to_one(tmp_path):
    plate, dmap = _synthetic_plate(tmp_path)
    meta = cds.split(plate, tmp_path / "split", depth_png=dmap, inpainter="telea-fallback")
    on_disk = json.loads((tmp_path / "split" / "synthetic-plate.split.json").read_text(encoding="utf-8"))
    assert on_disk == meta
    edges = meta["edges"]
    assert all(edges[i] < edges[i + 1] for i in range(len(edges) - 1)), edges
    assert sum(lay["band_share"] for lay in meta["layers"]) == pytest.approx(1.0, abs=1e-3)
    assert meta["notes"] == []


def test_the_same_plate_and_flags_give_byte_identical_layers(tmp_path):
    plate, dmap = _synthetic_plate(tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    cds.split(plate, a, depth_png=dmap, seed=0, inpainter="telea-fallback")
    cds.split(plate, b, depth_png=dmap, seed=0, inpainter="telea-fallback")
    for role in cds.ROLES:
        name = f"synthetic-plate-{role}.png"
        assert (a / name).read_bytes() == (b / name).read_bytes(), name


def test_a_hand_edges_override_reaches_the_json(tmp_path):
    plate, dmap = _synthetic_plate(tmp_path)
    meta = cds.split(plate, tmp_path / "split", depth_png=dmap, inpainter="telea-fallback",
                     edges_override=[0.0, 0.25, 0.5, 0.75, 1.0])
    assert meta["edges"] == [0.0, 0.25, 0.5, 0.75, 1.0]


def test_a_wrong_length_edges_override_is_refused(tmp_path):
    plate, dmap = _synthetic_plate(tmp_path)
    with pytest.raises(SystemExit):
        cds.split(plate, tmp_path / "split", depth_png=dmap, inpainter="telea-fallback",
                  edges_override=[0.0, 0.5, 1.0])


# ---------------------------------------------------------------- the SAM override (variant b-prime)


def _straddling_object(shape=(64, 64)) -> np.ndarray:
    """A blob deliberately laid ACROSS three quantile edges - the dock lamp's defect, in miniature."""
    m = np.zeros(shape, dtype=bool)
    m[20:40, 8:56] = True
    return m


def test_a_named_occluder_lands_whole_in_near_and_in_no_other_band():
    depth = _gradient()
    obj = _straddling_object()
    plain = cds.band_masks(depth, cds.band_edges(depth, 4))
    assert sum(1 for m in plain if (m & obj).any()) >= 3, "the fixture must straddle, or it proves nothing"

    masks, edges, free = cds.compose_masks(depth, occluder=obj)
    assert free == ["far", "mid", "subject"]
    assert len(edges) == 4
    assert np.array_equal(masks[3], obj)
    for m in masks[:3]:
        assert not (m & obj).any()


def test_a_named_subject_lands_whole_in_subject_and_the_occluder_wins_an_overlap():
    depth = _gradient()
    occ = _straddling_object()
    sub = np.zeros((64, 64), dtype=bool)
    sub[30:50, 30:60] = True  # deliberately overlaps the occluder
    masks, edges, free = cds.compose_masks(depth, occluder=occ, subject=sub)
    assert free == ["far", "mid"]
    assert len(edges) == 3
    assert np.array_equal(masks[3], occ)
    assert np.array_equal(masks[2], sub & ~occ)
    assert not (masks[2] & masks[3]).any()


def test_the_override_still_partitions_the_frame_exactly_once():
    depth = _gradient()
    occ = _straddling_object()
    sub = np.zeros((64, 64), dtype=bool)
    sub[48:60, 4:20] = True
    masks, _edges, _free = cds.compose_masks(depth, occluder=occ, subject=sub)
    stack = np.stack(masks).astype(int).sum(axis=0)
    assert stack.min() == 1 and stack.max() == 1


def test_the_quantiles_band_only_the_remainder():
    depth = _gradient()
    occ = _straddling_object()
    masks, edges, _free = cds.compose_masks(depth, occluder=occ)
    remainder = ~occ
    assert edges[0] == pytest.approx(float(depth[remainder].min()))
    assert edges[-1] == pytest.approx(float(depth[remainder].max()))
    for m in masks[:3]:
        assert (m & ~remainder).sum() == 0
    assert (masks[0] | masks[1] | masks[2]).sum() == remainder.sum()


def test_a_mask_that_eats_the_whole_frame_is_refused():
    with pytest.raises(ValueError):
        cds.compose_masks(_gradient(), occluder=np.ones((64, 64), dtype=bool))


def test_the_override_reaches_the_layers_and_the_split_json(tmp_path):
    plate, dmap = _synthetic_plate(tmp_path)
    occ = _straddling_object()
    meta = cds.split(plate, tmp_path / "sam", depth_png=dmap, inpainter="telea-fallback", occluder_mask=occ)
    assert meta["quantile_roles"] == ["far", "mid", "subject"]
    by_role = {lay["role"]: lay for lay in meta["layers"]}
    assert by_role["near"]["source"] == "sam2.1-mask" and by_role["near"]["depth_band"] is None
    assert by_role["near"]["band_share"] == pytest.approx(float(occ.mean()))
    assert by_role["far"]["source"] == "quantile"
    near = np.asarray(Image.open(tmp_path / "sam" / "synthetic-plate-near.png"))
    assert np.array_equal(near[..., 3] == 255, occ), "the near layer's alpha IS the named object"


def test_sam_points_take_comfy_sam2_masks_coordinate_form():
    assert json.loads(cds.sam_points("10,20;30,40")) == [{"x": 10, "y": 20}, {"x": 30, "y": 40}]


# ---------------------------------------------------------------- P61 T14b: the edge pass (E99 s63)
# The defect the pass exists for: a SAM matte grown by N px carries the BACKGROUND into the plane's alpha, and
# the plane paints at its own k, so the carried background slides off the real one and reads as a rim. The fix is
# geometric (shrink the matte) plus, where the shrink cannot reach, a nearest-interior recolour - never a blur.


def _rim_plate(size: int = 64, grow: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """A warm disc on a teal ground, and a matte GROWN by `grow` px - so the plane carries `grow` px of ground."""
    yy, xx = np.mgrid[0:size, 0:size]
    disc = (yy - size // 2) ** 2 + (xx - size // 2) ** 2 <= (size // 4) ** 2
    rgb = np.zeros((size, size, 3), dtype=np.uint8)
    rgb[...] = (40, 110, 150)           # the teal ground
    rgb[disc] = (190, 150, 90)          # the warm subject
    alpha = cds.dilate(disc, grow)
    return np.dstack([rgb, np.where(alpha, 255, 0).astype(np.uint8)]), disc


def test_erode_is_the_inverse_of_dilate_and_keeps_a_full_mask_full():
    m = np.zeros((32, 32), dtype=bool)
    m[12:20, 12:20] = True
    assert cds.erode(cds.dilate(m, 3), 3).sum() == m.sum()
    assert cds.erode(np.ones((16, 16), dtype=bool), 4).all(), "no matte, nothing to erode - the far wall is opaque"
    assert cds.erode(m, 0).tolist() == m.tolist(), "radius 0 is the identity, and never mutates its input"


def test_edge_band_is_the_outermost_pixels_inside_the_matte():
    m = np.zeros((32, 32), dtype=bool)
    m[8:24, 8:24] = True
    band = cds.edge_band(m, 2)
    assert band.sum() == m.sum() - cds.erode(m, 2).sum()
    assert not (band & cds.erode(m, 2)).any()


def test_edge_ring_stats_reads_the_carried_ground_and_then_the_subject():
    rgba, _ = _rim_plate(grow=4)
    mask = rgba[..., 3] > 0
    outer = cds.edge_ring_stats(rgba[..., :3], mask, 0)
    inner = cds.edge_ring_stats(rgba[..., :3], mask, 6)
    assert outer["chroma"] > 15 and 200 < outer["hue"] < 300, "the outermost ring IS the teal ground"
    assert inner["hue"] < 120, "six px in, the warm subject - the hue has flipped"
    assert cds.edge_ring_stats(rgba[..., :3], mask, 999) == {"depth": 999, "n": 0}


def test_the_shrink_alone_drops_the_carried_ground_and_leaves_the_plates_own_pixels():
    rgba, disc = _rim_plate(grow=4)
    out, rec = cds.process_matte(rgba, shrink_px=4, band_px=0)
    assert rec["alpha_px_after"] < rec["alpha_px_before"]
    kept = out[..., 3] > 0
    assert not (kept & ~disc).any(), "E99 s63: the plane no longer carries one pixel of the ground"
    assert (out[..., :3][kept] == rgba[..., :3][kept]).all(), "the colours are the flat plate's own - dE 0 by construction"
    assert cds.edge_ring_stats(out[..., :3], kept, 0)["hue"] < 120


def test_the_decontamination_takes_the_nearest_interior_colour_and_never_averages():
    rgba, _ = _rim_plate(grow=0)
    rgba[..., :3][cds.edge_band(rgba[..., 3] > 0, 2)] = (0, 255, 0)     # a screaming green fringe
    out, rec = cds.process_matte(rgba, shrink_px=0, band_px=2)
    kept = out[..., 3] > 0
    assert rec["decontaminated_px"] > 0
    assert not (out[..., :3][kept] == np.array([0, 255, 0])).all(-1).any(), "the fringe is gone"
    colours = {tuple(c) for c in out[..., :3][kept]}
    assert colours == {(190, 150, 90)}, "every band pixel took an INTERIOR colour - a blur would invent new ones"


def test_an_opaque_plane_is_returned_untouched():
    rgba = np.dstack([np.full((16, 16, 3), 200, np.uint8), np.full((16, 16), 255, np.uint8)])
    out, rec = cds.process_matte(rgba, shrink_px=3, band_px=2)
    assert rec["opaque"] is True and rec["dropped_px"] == 0
    assert (out == rgba).all()


def test_a_shrink_that_would_erase_the_whole_matte_is_refused_by_name():
    rgba, _ = _rim_plate(size=48, grow=0)
    with pytest.raises(SystemExit, match="erases the plane's whole matte"):
        cds.process_matte(rgba, shrink_px=30, band_px=0)


def test_process_plane_file_keeps_the_raw_beside_it_and_records_the_rim(tmp_path):
    rgba, _ = _rim_plate(grow=4)
    src = tmp_path / "plane-near.png"
    Image.fromarray(rgba, mode="RGBA").save(src)
    raw = tmp_path / "plane-near.raw.png"
    rec = cds.process_plane_file(src, src, 4, 0, keep_raw=raw)
    assert raw.exists(), "E99 s63 keeps the split's raw matte on disk; what SHIPS is the processed plane"
    assert 200 < rec["rings_before"][0]["hue"] < 300, "the raw rim IS the ground (on the Tokyo dock: h 254.8, the sky's own)"
    assert rec["rings_after"][0]["hue"] < 120, "the processed rim is the subject's own colour"
    assert (np.asarray(Image.open(src).convert("RGBA"))[..., 3] > 0).sum() == rec["alpha_px_after"]
