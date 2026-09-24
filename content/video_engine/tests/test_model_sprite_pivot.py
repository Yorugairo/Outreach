from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from content.video_engine.src.modeling.layered import LayeredScene, LayeredSceneError


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "content/video_engine/tests/fixtures/modeling/layered/authored/knockout-authored-layers.v1.json"


def _write_asset(root: Path, name: str, image: Image.Image, bounds: list[float]) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    image.save(path, format="PNG", optimize=False)
    return {
        "path": name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bounds_local_px": bounds,
    }


def _synthetic_assets(root: Path) -> tuple[dict, dict]:
    torso = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(torso)
    draw.polygon([(19, 54), (38, 43), (90, 43), (109, 54), (124, 123), (4, 123)],
                 fill=(48, 104, 128, 255))
    draw.line([(36, 47), (92, 47)], fill=(242, 232, 205, 255), width=3)

    head = Image.new("RGBA", (48, 44), (0, 0, 0, 0))
    face = ImageDraw.Draw(head)
    face.ellipse((4, 2, 44, 42), fill=(224, 84, 60, 253))
    face.ellipse((13, 16, 17, 20), fill=(22, 28, 36, 255))
    face.ellipse((30, 16, 34, 20), fill=(22, 28, 36, 255))
    face.line((18, 31, 30, 30), fill=(55, 24, 22, 255), width=2)
    # A bright upper marker makes rigid rotation measurable without judging color drift.
    face.ellipse((32, 5, 37, 10), fill=(250, 222, 42, 255))
    return (
        _write_asset(root, "torso.png", torso, [0, 0, 128, 128]),
        _write_asset(root, "head.png", head, [-24, -22, 24, 22]),
    )


def _document(
    asset_root: Path,
    *,
    with_pivot: bool = True,
    angles: tuple[tuple[int, float], ...] = ((0, 0.0), (4, -6.0), (8, -12.0), (12, 0.0)),
    pivot: dict | None = None,
    head_anchor: tuple[float, float] = (64, 56),
    head_bounds: tuple[float, float, float, float] = (-24, -22, 24, 22),
) -> tuple[dict, Path]:
    torso_asset, head_asset = _synthetic_assets(asset_root)
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    document["canvas_px"] = [128, 128]
    document["clear_color"] = "#f5f3ee"
    document["camera"] = {
        "zoom_limits": [1, 1],
        "keyframes": [{
            "frame": 0, "zoom": 1, "look_px": [64, 64], "at_px": [64, 64], "yaw_deg": 0, "pitch_deg": 0,
        }],
    }
    document["scene"]["duration_frames"] = 16
    document["scene"]["events"] = []
    document["scene"]["contacts"] = []
    document["scene"]["motion_channels"] = [
        {
            "channel_id": "fighter-b-pose", "binding_id": "fighter_b", "target_kind": "articulation",
            "semantic_target": "pose", "value_unit": "normalized", "interpolation": "step",
            "keyframes": [{"frame": 0, "value": 0}],
        },
        {
            "channel_id": "fighter-b-expression", "binding_id": "fighter_b", "target_kind": "face_control",
            "semantic_target": "expression", "value_unit": "normalized", "interpolation": "step",
            "keyframes": [{"frame": 0, "value": 0}],
        },
        {
            "channel_id": "fighter-b-head-angle", "binding_id": "fighter_b", "target_kind": "articulation",
            "semantic_target": "head_pivot", "value_unit": "degrees", "interpolation": "linear",
            "keyframes": [{"frame": frame, "value": angle} for frame, angle in angles],
        },
    ]

    background = {
        "layer_id": "test-background", "kind": "environment", "role": "background", "depth": 1.0,
        "source_bounds_px": [0, 0, 128, 128], "painted_bounds_px": [0, 0, 128, 128],
        "shapes": [{"kind": "rect", "bounds_px": [0, 0, 128, 128], "fill": "#f5f3ee"}],
    }

    def character_layer(layer_id: str, asset: dict, bounds: tuple[float, float, float, float],
                        anchor: tuple[float, float]) -> dict:
        silhouette = list(bounds)
        return {
            "layer_id": layer_id, "kind": "character", "binding_id": "fighter_b", "role": "subject",
            "depth": 1.275, "source_bounds_px": [0, 0, 128, 128], "anchor_px": list(anchor),
            "shapes": [], "pose_channel": "fighter-b-pose", "expression_channel": "fighter-b-expression",
            "silhouette_bounds_local_px": silhouette,
            "pose_states": [{
                "state_id": "rest", "index": 0, "shapes": [], "raster_asset": asset,
            }],
            "expression_states": [{"state_id": "neutral", "index": 0, "shapes": []}],
            "disocclusion_budget_px": 0,
        }

    torso_layer = character_layer("fighter-b-torso", torso_asset, (0, 0, 128, 128), (0, 0))
    head_asset["bounds_local_px"] = list(head_bounds)
    head_layer = character_layer("fighter-b-head", head_asset, head_bounds, head_anchor)
    if with_pivot:
        head_layer["sprite_pivot"] = pivot or {
            "channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 12, "pivot_local_px": [0, 16],
        }
    document["layers"] = [background, torso_layer, head_layer]
    return document, asset_root


def _scene(tmp_path: Path, **kwargs) -> LayeredScene:
    document, asset_root = _document(tmp_path / "art", **kwargs)
    return LayeredScene(document, asset_root=asset_root)


def _marker_centroid(image: Image.Image) -> tuple[float, float]:
    points = []
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = image.getpixel((x, y))
            if red > 220 and green > 180 and blue < 80 and alpha > 200:
                points.append((x, y))
    assert points
    return (sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points))


def test_sprite_pivot_zero_is_pixel_identical_to_opt_out_and_legacy_scene_bytes(tmp_path: Path) -> None:
    configured = _scene(tmp_path / "pivot-zero", angles=((0, 0.0), (8, 0.0)))
    unconfigured = _scene(
        tmp_path / "pivot-absent", with_pivot=False, angles=((0, 0.0), (8, 0.0)),
    )
    assert configured.render(Fraction(0), supersample=1).image.tobytes() == \
        unconfigured.render(Fraction(0), supersample=1).image.tobytes()

    legacy = LayeredScene.load(FIXTURE)
    expected = {
        0: "ae258c240fdb196f8a97376102bdc7d82acb84b602a79e1c0f9104f043bc89ac",
        27: "d139e97b5b063558ab110788001bb64f26a178bf10959840fa097f1c8b8e40ee",
        54: "bc4c82ae599eb7731dcd4066aa4231d19f3eb117f748a629c1d050cc113fda25",
    }
    actual = {
        frame: hashlib.sha256(legacy.render(Fraction(frame), supersample=1).image.tobytes()).hexdigest()
        for frame in expected
    }
    assert actual == expected


def test_sprite_pivot_moves_only_head_and_leaves_uncovered_torso_pixels_static(tmp_path: Path) -> None:
    scene = _scene(tmp_path)
    zero_state = scene.evaluate(Fraction(0))
    moved_state = scene.evaluate(Fraction(8))
    sample_zero = scene.timeline.evaluate(Fraction(0))
    sample_moved = scene.timeline.evaluate(Fraction(8))
    head = next(layer for layer in scene.layers if layer["layer_id"] == "fighter-b-head")
    torso = next(layer for layer in scene.layers if layer["layer_id"] == "fighter-b-torso")

    head_zero = scene._raster_layer(
        head, scene._layer_components(head, zero_state.selected_states[head["layer_id"]]),
        zero_state.anchors_px[head["layer_id"]], sample_zero, 1,
    )
    head_moved = scene._raster_layer(
        head, scene._layer_components(head, moved_state.selected_states[head["layer_id"]]),
        moved_state.anchors_px[head["layer_id"]], sample_moved, 1,
    )
    x0, y0 = _marker_centroid(head_zero)
    x1, y1 = _marker_centroid(head_moved)
    # Pillow's negative angle rotates this asymmetric upper-right marker right and down.
    assert x1 > x0 + 4
    assert y1 > y0 + 1

    torso_zero = scene._raster_layer(
        torso, scene._layer_components(torso, zero_state.selected_states[torso["layer_id"]]),
        zero_state.anchors_px[torso["layer_id"]], sample_zero, 1,
    )
    torso_moved = scene._raster_layer(
        torso, scene._layer_components(torso, moved_state.selected_states[torso["layer_id"]]),
        moved_state.anchors_px[torso["layer_id"]], sample_moved, 1,
    )
    assert torso_zero.tobytes() == torso_moved.tobytes()

    frame_zero = scene.render(Fraction(0), supersample=1).image
    frame_moved = scene.render(Fraction(8), supersample=1).image
    assert frame_zero.crop((5, 100, 123, 124)).tobytes() == frame_moved.crop((5, 100, 123, 124)).tobytes()


def test_sprite_pivot_accepts_envelope_and_rejects_angle_outside_it(tmp_path: Path) -> None:
    scene = _scene(tmp_path)
    assert scene.render(Fraction(8), supersample=1).image.mode == "RGB"

    engineering_limit = _scene(
        tmp_path / "fifteen-degree-limit", angles=((0, 0.0), (8, 15.0)), pivot={
            "channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 15, "pivot_local_px": [0, 16],
        },
    )
    assert engineering_limit.evaluate(Fraction(8)).frame == Fraction(8)

    out_of_range = _scene(
        tmp_path / "too-far", angles=((0, 0.0), (8, 12.5)),
    )
    with pytest.raises(LayeredSceneError, match="exceeds its authored envelope of 12 deg"):
        out_of_range.evaluate(Fraction(8))


@pytest.mark.parametrize("invalid", [
    {"channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 16, "pivot_local_px": [0, 16]},
    {"channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 12, "pivot_local_px": [0, 100]},
    {"channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 12, "pivot_local_px": [0, 16], "extra": True},
    {"channel_id": "missing-angle", "max_abs_angle_deg": 12, "pivot_local_px": [0, 16]},
])
def test_sprite_pivot_rejects_invalid_configuration(tmp_path: Path, invalid: dict) -> None:
    document, asset_root = _document(tmp_path / "invalid-art", pivot=invalid)
    with pytest.raises(LayeredSceneError, match="sprite_pivot"):
        LayeredScene(document, asset_root=asset_root)


def test_sprite_pivot_requires_degrees_articulation_channel_bound_to_layer(tmp_path: Path) -> None:
    document, asset_root = _document(tmp_path / "wrong-channel-art")
    channel = next(item for item in document["scene"]["motion_channels"]
                   if item["channel_id"] == "fighter-b-head-angle")
    channel["value_unit"] = "normalized"
    with pytest.raises(LayeredSceneError, match="must use degrees"):
        LayeredScene(document, asset_root=asset_root)

    document, asset_root = _document(tmp_path / "wrong-binding-art")
    channel = next(item for item in document["scene"]["motion_channels"]
                   if item["channel_id"] == "fighter-b-head-angle")
    channel["binding_id"] = "other_character"
    with pytest.raises(LayeredSceneError, match="is bound to"):
        LayeredScene(document, asset_root=asset_root)


def test_sprite_pivot_rejects_silhouette_clipping_and_noncharacter_opt_in(tmp_path: Path) -> None:
    clipped = _scene(
        tmp_path / "clipped", angles=((0, 0.0), (8, 12.0)), head_anchor=(103, 64),
        head_bounds=(-10, -20, 25, 20), pivot={
            "channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 12, "pivot_local_px": [-10, 0],
        },
    )
    with pytest.raises(LayeredSceneError, match="clips its declared silhouette by source_bounds_px"):
        clipped.evaluate(Fraction(8))

    document, asset_root = _document(tmp_path / "noncharacter-art")
    document["layers"][0]["sprite_pivot"] = {
        "channel_id": "fighter-b-head-angle", "max_abs_angle_deg": 12, "pivot_local_px": [0, 0],
    }
    with pytest.raises(LayeredSceneError, match="only valid on character layers"):
        LayeredScene(document, asset_root=asset_root)


def test_sprite_pivot_is_deterministic_after_arbitrary_random_seeks(tmp_path: Path) -> None:
    scene = _scene(tmp_path)
    requested = [Fraction(8), Fraction(0), Fraction(4), Fraction(12), Fraction(8)]
    expected = {frame: scene.render(frame, supersample=1).image.tobytes() for frame in requested}
    for frame in (Fraction(7), Fraction(1), Fraction(15), Fraction(8), Fraction(0)):
        scene.render(frame, supersample=1)
    assert {frame: scene.render(frame, supersample=1).image.tobytes() for frame in requested} == expected
