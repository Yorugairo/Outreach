from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.composite_preview import (
    FRAME_HEIGHT,
    FRAME_WIDTH,
    PREVIEW_KIND,
    CompositePreviewError,
    measure_cutout,
    plan_composite,
    render_composite,
)

# A trimmed host cutout is roughly 891x1536; a civilian roughly 792x1456.
HOST = {"asset_id": "actor-host-v1", "trimmed_size": (891, 1536)}
CIVILIAN = {"asset_id": "actor-civilian-a-v1", "trimmed_size": (792, 1456)}


def _world(**over) -> dict:
    world = {
        "asset_id": "world-office-desk-v1",
        "kind": "world_board",
        "placement": {
            "figure_zone": [0.55, 1.0],
            "baseline_y": 0.98,
            "figure_height": 0.50,
            "max_figures": 2,
        },
    }
    world.update(over)
    return world


# --- geometry, no pixels -------------------------------------------------------


def test_a_figure_is_scaled_to_the_worlds_declared_figure_height():
    plan = plan_composite(_world(), [HOST])

    placed = plan["figures"][0]
    # Literal values, not the implementation expression: half of 1080 is 540 and
    # 98% of 1080 is 1058. Restating int(FRAME_HEIGHT * 0.50) would assert only
    # that the code equals itself.
    assert placed["height_px"] == 540
    assert placed["bottom_px"] == 1058


def test_figures_are_placed_inside_the_declared_zone():
    plan = plan_composite(_world(), [CIVILIAN, HOST])

    # Bound against the zone, not the frame. Using FRAME_WIDTH as the right bound
    # would miss a centring bug that pushed figures past x1 but not off-frame.
    zone_x0, zone_x1 = FRAME_WIDTH * 0.55, FRAME_WIDTH * 1.0
    for placed in plan["figures"]:
        assert placed["left_px"] >= zone_x0
        assert placed["left_px"] + placed["width_px"] <= zone_x1


def test_more_figures_than_the_world_allows_is_refused_by_name():
    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite(_world(), [HOST, CIVILIAN, HOST])

    joined = " ".join(excinfo.value.errors)
    assert "max_figures" in joined
    assert "world-office-desk-v1" in joined


def test_two_figures_at_080_exceed_every_current_clear_zone_and_are_refused():
    """The episode-1 finding, held as a regression.

    At 0.80 frame height the civilian needs 470px and the host 501px. With the
    inter-figure gap that is 1009px against the office world's 864px clear zone,
    so the frame that produced the "standing on the chair" composite is refused
    outright, and the error states every measurement it used.
    """

    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite(_world(), [CIVILIAN, HOST], figure_height=0.80)

    joined = " ".join(excinfo.value.errors)
    assert "864px" in joined, "the error must state the measured zone width"
    assert "470px" in joined and "501px" in joined, "and each figure's measured width"
    assert "1009px" in joined, "and the total it compared against the zone"


def test_the_same_two_figures_fit_at_the_050_standard():
    plan = plan_composite(_world(), [CIVILIAN, HOST], figure_height=0.50)

    assert plan["figure_height"] == 0.50
    assert len(plan["figures"]) == 2


def test_a_world_without_placement_is_refused_rather_than_guessed():
    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite({"asset_id": "world-bare-v1", "kind": "world_board"}, [HOST])

    assert any("placement" in e for e in excinfo.value.errors)


def test_a_plan_is_labelled_a_placement_check_not_a_render_preview():
    plan = plan_composite(_world(), [HOST])

    assert plan["preview_kind"] == PREVIEW_KIND == "placement_check"
    assert plan["answers"] == "size, zone and baseline only"


# --- pixels -------------------------------------------------------------------


def _png(path: Path, size: tuple[int, int], colour: tuple[int, int, int, int]) -> Path:
    Image.new("RGBA", size, colour).save(path)
    return path


def _opaque(path: Path, size: tuple[int, int], colour=(240, 230, 200)) -> Path:
    Image.new("RGB", size, colour).save(path)
    return path


def test_a_flat_world_renders_a_frame_with_the_figure_composited(tmp_path):
    world_png = _opaque(tmp_path / "world.png", (1536, 1024))
    host_png = _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))

    result = render_composite(
        _world(path="world.png"),
        [{"asset_id": "actor-host-v1", "path": "host.png"}],
        project_root=tmp_path,
        output_dir=tmp_path / "runtime" / "previews",
    )

    out = Image.open(result["path"])
    assert out.size == (FRAME_WIDTH, FRAME_HEIGHT)
    assert result["preview_kind"] == "placement_check"
    # Written under runtime/, never beside the catalogue assets.
    assert "runtime" in Path(result["path"]).parts


def test_two_renders_of_the_same_inputs_are_byte_identical(tmp_path):
    _opaque(tmp_path / "world.png", (1536, 1024))
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))
    args = dict(
        project_root=tmp_path,
        output_dir=tmp_path / "runtime" / "previews",
    )
    world = _world(path="world.png")
    figures = [{"asset_id": "actor-host-v1", "path": "host.png"}]

    first = render_composite(world, figures, **args)["path"]
    digest_one = hashlib.sha256(Path(first).read_bytes()).hexdigest()
    second = render_composite(world, figures, **args)["path"]
    digest_two = hashlib.sha256(Path(second).read_bytes()).hexdigest()

    assert digest_one == digest_two


def test_a_layered_world_composites_planes_back_to_front_around_the_cast(tmp_path):
    # near plane is a full-frame opaque red band at the bottom; if it lands in
    # front of the cast, the bottom row is red rather than figure blue.
    _opaque(tmp_path / "far.png", (1536, 1024), (240, 230, 200))
    mid = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    mid.save(tmp_path / "mid.png")
    near = Image.new("RGBA", (1536, 1024), (0, 0, 0, 0))
    for y in range(1000, 1024):
        for x in range(0, 1536):
            near.putpixel((x, y), (220, 30, 30, 255))
    near.save(tmp_path / "near.png")
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))

    world = _world(
        layers=[
            {"depth_layer": "building_or_environment", "path": "far.png"},
            {"depth_layer": "actor_or_machine", "path": "mid.png"},
            {"depth_layer": "foreground_cutout", "path": "near.png"},
        ]
    )
    result = render_composite(
        world,
        [{"asset_id": "actor-host-v1", "path": "host.png"}],
        project_root=tmp_path,
        output_dir=tmp_path / "runtime" / "previews",
    )

    out = Image.open(result["path"]).convert("RGB")
    assert result["plane_count"] == 3
    # The near plane occludes the cast at the very bottom of the frame.
    assert out.getpixel((FRAME_WIDTH // 2, FRAME_HEIGHT - 4)) == (220, 30, 30)


def test_a_layered_world_with_mismatched_plane_sizes_is_refused_before_compositing(tmp_path):
    _opaque(tmp_path / "far.png", (1536, 1024))
    Image.new("RGBA", (1200, 800), (0, 0, 0, 0)).save(tmp_path / "mid.png")
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))

    world = _world(
        layers=[
            {"depth_layer": "building_or_environment", "path": "far.png"},
            {"depth_layer": "actor_or_machine", "path": "mid.png"},
        ]
    )
    with pytest.raises(CompositePreviewError) as excinfo:
        render_composite(
            world,
            [{"asset_id": "actor-host-v1", "path": "host.png"}],
            project_root=tmp_path,
            output_dir=tmp_path / "runtime" / "previews",
        )

    joined = " ".join(excinfo.value.errors)
    assert "1200x800" in joined and "1536x1024" in joined


def test_a_missing_file_is_named_rather_than_crashing(tmp_path):
    _opaque(tmp_path / "world.png", (1536, 1024))

    with pytest.raises(CompositePreviewError) as excinfo:
        render_composite(
            _world(path="world.png"),
            [{"asset_id": "actor-ghost-v1", "path": "absent.png"}],
            project_root=tmp_path,
            output_dir=tmp_path / "runtime" / "previews",
        )

    assert any("absent.png" in e for e in excinfo.value.errors)


def test_measure_cutout_reports_the_trimmed_extent(tmp_path):
    im = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    for y in range(100, 300):
        for x in range(200, 260):
            im.putpixel((x, y), (10, 10, 10, 255))
    im.save(tmp_path / "sparse.png")

    assert measure_cutout(tmp_path / "sparse.png") == (60, 200)


def test_planning_resolves_figure_paths_against_the_project_root(tmp_path):
    """Geometry and rendering resolve paths the same way.

    Without this, planning a frame from relative catalogue paths raised a bare
    Pillow FileNotFoundError while rendering the identical inputs succeeded.
    """

    (tmp_path / "assets").mkdir()
    im = Image.new("RGBA", (400, 800), (0, 0, 0, 0))
    for y in range(100, 700):
        for x in range(100, 300):
            im.putpixel((x, y), (20, 40, 120, 255))
    im.save(tmp_path / "assets" / "host.png")

    plan = plan_composite(
        _world(),
        [{"asset_id": "actor-host-v1", "path": "assets/host.png"}],
        project_root=tmp_path,
    )

    assert plan["figures"][0]["width_px"] > 0


def test_planning_names_a_missing_figure_rather_than_raising_from_pillow(tmp_path):
    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite(
            _world(),
            [{"asset_id": "actor-ghost-v1", "path": "assets/absent.png"}],
            project_root=tmp_path,
        )

    assert any("absent.png" in e for e in excinfo.value.errors)


def test_a_narrow_right_hand_zone_still_contains_its_figures():
    """The fixture zone ends at the frame edge, which hides right-edge bugs."""

    world = _world(placement={
        "figure_zone": [0.30, 0.70], "baseline_y": 0.98,
        "figure_height": 0.50, "max_figures": 1,
    })
    placed = plan_composite(world, [HOST])["figures"][0]

    assert placed["left_px"] >= FRAME_WIDTH * 0.30
    assert placed["left_px"] + placed["width_px"] <= FRAME_WIDTH * 0.70


def test_the_cast_stays_behind_the_foreground_when_no_actor_plane_exists(tmp_path):
    """A world may declare foreground_cutout without actor_or_machine.

    Only building_or_environment is required by the catalogue guards, so this
    shape is legal input. Splitting planes by list position rather than declared
    depth put the cast in front of the foreground plate for exactly these worlds.
    """

    _opaque(tmp_path / "far.png", (1920, 1080), (240, 230, 200))
    near = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    for y in range(1040, 1080):
        for x in range(1920):
            near.putpixel((x, y), (220, 30, 30, 255))
    near.save(tmp_path / "near.png")
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))

    world = _world(layers=[
        {"depth_layer": "building_or_environment", "path": "far.png"},
        {"depth_layer": "foreground_cutout", "path": "near.png"},
    ])
    result = render_composite(
        world,
        [{"asset_id": "actor-host-v1", "path": "host.png"}],
        project_root=tmp_path,
        output_dir=tmp_path / "runtime" / "previews",
    )

    out = Image.open(result["path"]).convert("RGB")
    assert out.getpixel((FRAME_WIDTH // 2, FRAME_HEIGHT - 8)) == (220, 30, 30)


def test_the_world_is_not_horizontally_distorted_to_reach_16_9(tmp_path):
    """A 3:2 plate stretched to 16:9 applies a 1.185x horizontal scale.

    The figure keeps its own aspect, so it reads about 18% narrow against the
    furniture in the one frame whose purpose is judging figure size against
    furniture. A square drawn in the world must still be square in the output.
    """

    world_im = Image.new("RGB", (1536, 1024), (240, 230, 200))
    for y in range(700, 900):
        for x in range(200, 400):
            world_im.putpixel((x, y), (20, 20, 20))
    world_im.save(tmp_path / "world.png")
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))

    result = render_composite(
        _world(path="world.png"),
        [{"asset_id": "actor-host-v1", "path": "host.png"}],
        project_root=tmp_path,
        output_dir=tmp_path / "runtime" / "previews",
    )

    out = Image.open(result["path"]).convert("RGB")
    dark = [(x, y) for y in range(FRAME_HEIGHT) for x in range(0, 800)
            if out.getpixel((x, y)) == (20, 20, 20)]
    assert dark, "the marker square was cropped out of the frame entirely"
    xs = [x for x, _ in dark]
    ys = [y for _, y in dark]
    width, height = max(xs) - min(xs), max(ys) - min(ys)

    assert abs(width - height) <= 3, f"square rendered {width}x{height}; the world was distorted"


def test_two_figure_heights_that_truncate_alike_get_distinct_filenames(tmp_path):
    _opaque(tmp_path / "world.png", (1536, 1024))
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))
    args = dict(project_root=tmp_path, output_dir=tmp_path / "runtime" / "previews")
    world = _world(path="world.png")
    figures = [{"asset_id": "actor-host-v1", "path": "host.png"}]

    # int(0.28 * 100) equals int(0.29 * 100), so these collided and the second
    # render silently overwrote the first.
    a = render_composite(world, figures, figure_height=0.28, **args)["path"]
    b = render_composite(world, figures, figure_height=0.29, **args)["path"]

    assert a != b


def test_a_preview_may_not_be_written_outside_runtime(tmp_path):
    _opaque(tmp_path / "world.png", (1536, 1024))
    _png(tmp_path / "host.png", (400, 800), (20, 40, 120, 255))

    with pytest.raises(CompositePreviewError) as excinfo:
        render_composite(
            _world(path="world.png"),
            [{"asset_id": "actor-host-v1", "path": "host.png"}],
            project_root=tmp_path,
            output_dir=tmp_path / "assets" / "generated",
        )

    assert any("runtime" in e for e in excinfo.value.errors)


def test_a_figure_taller_than_its_baseline_is_refused_not_silently_clipped():
    """Pillow composites a negative destination without complaint."""

    world = _world(placement={
        "figure_zone": [0.55, 1.0], "baseline_y": 0.60,
        "figure_height": 0.90, "max_figures": 1,
    })
    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite(world, [HOST])

    joined = " ".join(excinfo.value.errors)
    assert "972px" in joined and "648px" in joined


def test_an_unknown_depth_layer_is_refused_rather_than_sorted_to_the_front():
    world = _world(layers=[
        {"depth_layer": "building_or_environment", "path": "far.png"},
        {"depth_layer": "typo_layer", "path": "mid.png"},
    ])
    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite(world, [HOST])

    assert any("typo_layer" in e for e in excinfo.value.errors)


def test_a_duplicated_depth_layer_is_refused():
    world = _world(layers=[
        {"depth_layer": "building_or_environment", "path": "a.png"},
        {"depth_layer": "building_or_environment", "path": "b.png"},
    ])
    with pytest.raises(CompositePreviewError) as excinfo:
        plan_composite(world, [HOST])

    assert any("more than once" in e for e in excinfo.value.errors)


def test_the_plane_vocabulary_is_the_catalogues_not_a_second_copy():
    """A second copy of the depth vocabulary drifts the day a plane is added."""

    from content.video_engine.src.services import asset_catalog, composite_preview

    assert composite_preview._PLANE_ORDER is asset_catalog.DEPTH_LAYERS
