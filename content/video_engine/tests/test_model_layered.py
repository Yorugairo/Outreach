from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from content.video_engine.src.modeling.layered import (
    DIAGNOSTIC_LABEL,
    LayeredScene,
    LayeredSceneError,
    MAX_RASTER_ASSET_BYTES,
    MAX_SCENE_RASTER_ASSET_DECODED_BYTES,
    MAX_SCENE_RASTER_ASSET_PIXELS,
    render_contact_sheet,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "content/video_engine/tests/fixtures/modeling/layered/authored/knockout-authored-layers.v1.json"


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _scene() -> LayeredScene:
    return LayeredScene.load(FIXTURE)


def _write_synthetic_art(
    asset_root: Path,
    name: str,
    color: tuple[int, int, int, int],
    bounds: tuple[int, int, int, int],
) -> dict:
    asset_root.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle(bounds, fill=color)
    path = asset_root / name
    image.save(path, format="PNG", optimize=False)
    return {
        "path": name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bounds_local_px": [-40.8, -40.4, -32.8, -32.4],
    }


def _raster_scene(tmp_path: Path) -> tuple[dict, Path]:
    document = _fixture()
    asset_root = tmp_path / "trusted-art"
    background = next(layer for layer in document["layers"] if layer["role"] == "background")
    background["shapes"] = [{
        "kind": "rect",
        "bounds_px": background["painted_bounds_px"],
        "fill": "#ffffff",
    }]
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["shapes"] = []
    pose_colors = ((255, 0, 0, 128), (255, 196, 0, 128), (0, 96, 255, 128))
    for index, state in enumerate(fighter["pose_states"]):
        state["shapes"] = []
        state["raster_asset"] = _write_synthetic_art(
            asset_root, f"pose-{index}.png", pose_colors[index], (1, 1, 6, 6)
        )
    expression_colors = ((0, 255, 0, 128), (0, 64, 255, 128))
    for index, state in enumerate(fighter["expression_states"]):
        state["shapes"] = []
        state["raster_asset"] = _write_synthetic_art(
            asset_root, f"expression-{index}.png", expression_colors[index], (3, 3, 4, 4)
        )
    document["layers"] = [background, fighter]
    return document, asset_root


def _write_large_raster_assets(asset_root: Path, count: int) -> list[dict]:
    asset_root.mkdir(parents=True, exist_ok=True)
    source_path = asset_root / "large-source.png"
    image = Image.new("RGBA", (2048, 1025), (0, 0, 0, 0))
    image.putpixel((0, 0), (255, 32, 16, 128))
    image.save(source_path, format="PNG", optimize=False)
    payload = source_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    assets = []
    for index in range(count):
        name = f"large-{index}.png"
        (asset_root / name).write_bytes(payload)
        assets.append({
            "path": name,
            "sha256": digest,
            "bounds_local_px": [-40.8, -40.4, -32.8, -32.4],
        })
    return assets


def _document_with_raster_states(asset_root: Path, unique_assets: int) -> dict:
    document = _fixture()
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    assets = _write_large_raster_assets(asset_root, unique_assets)
    poses = fighter["pose_states"]
    for index, state in enumerate(poses):
        state["shapes"] = []
        state["raster_asset"] = assets[index]
    for index in range(len(poses), unique_assets):
        poses.append({
            "state_id": f"extra-pose-{index}",
            "index": index,
            "shapes": [],
            "raster_asset": assets[index],
        })
    for state in fighter["expression_states"]:
        state["shapes"] = []
        state["raster_asset"] = assets[0]
    return document


def _set_channel_value(document: dict, channel_id: str, value: int) -> None:
    channel = next(item for item in document["scene"]["motion_channels"] if item["channel_id"] == channel_id)
    for keyframe in channel["keyframes"]:
        keyframe["value"] = value


def test_authored_fixture_uses_the_shared_rational_contact_clock() -> None:
    scene = _scene()
    contact = scene.evaluate(Fraction(27))
    after_contact = scene.evaluate(Fraction(28))

    assert scene.timeline.clock.fps == Fraction(24, 1)
    assert contact.time_seconds == Fraction(9, 8)
    assert contact.events == ("right-straight-contact",)
    assert "right-hand-to-head" in contact.contacts
    assert "right-hand-to-head" not in after_contact.contacts
    assert after_contact.events == ("head-recoil",)
    assert scene.evaluate(Fraction(85)).contacts == ("victim-on-mat",)
    assert contact.diagnostic_status == "review_only_diagnostic"


def test_pose_and_expression_swaps_are_evaluated_on_the_shared_clock() -> None:
    scene = _scene()

    before_contact = scene.evaluate(Fraction(26))
    contact = scene.evaluate(Fraction(27))
    recoil = scene.evaluate(Fraction(28))
    fall = scene.evaluate(Fraction(54))

    assert before_contact.selected_states["fighter-a"] == {"pose": "cross", "expression": "focused"}
    assert contact.contacts == ("attacker-planted-foot", "right-hand-to-head")
    assert recoil.selected_states["fighter-b"] == {"pose": "recoil", "expression": "dazed"}
    assert fall.selected_states["fighter-b"]["pose"] == "fall"


def test_saved_authored_resource_edits_reload_and_change_the_render(tmp_path: Path) -> None:
    document = _fixture()
    destination = tmp_path / "editable-character-scene.json"
    destination.write_text(json.dumps(document), encoding="utf-8")
    first = LayeredScene.load(destination).render(Fraction(24)).image

    edited = copy.deepcopy(document)
    fighter = next(layer for layer in edited["layers"] if layer["layer_id"] == "fighter-a")
    cross = next(state for state in fighter["pose_states"] if state["state_id"] == "cross")
    cross["shapes"][0]["stroke"] = "#ff36dd"
    destination.write_text(json.dumps(edited), encoding="utf-8")

    reloaded = LayeredScene.load(destination)
    second = reloaded.render(Fraction(24)).image
    assert reloaded.evaluate(Fraction(24)).selected_states["fighter-a"]["pose"] == "cross"
    assert hashlib.sha256(first.tobytes()).digest() != hashlib.sha256(second.tobytes()).digest()


def test_environment_prop_character_and_foreground_planes_are_authored_in_depth_order() -> None:
    scene = _scene()
    by_id = {layer["layer_id"]: layer for layer in scene.layers}

    assert tuple((layer["layer_id"], layer["depth"]) for layer in scene.layers) == (
        ("arena-background", 1.0),
        ("canvas-mat", 1.05),
        ("corner-glove", 1.15),
        ("fighter-a", 1.275),
        ("fighter-b", 1.275),
        ("near-ring-ropes", 1.4),
    )
    assert by_id["corner-glove"]["kind"] == "prop"
    assert by_id["canvas-mat"]["kind"] == "environment"
    assert by_id["near-ring-ropes"]["kind"] == "occluder"


def test_declared_foreground_occluder_paints_over_character_at_overlap() -> None:
    frame = _scene().render(Fraction(0)).image

    # Fighter A's torso is underneath the near rope at this pixel.
    assert frame.getpixel((115, 380)) == (215, 201, 165)


def test_camera_uses_declared_view_envelope_and_rejects_unpainted_background() -> None:
    yaw_outside = _fixture()
    yaw_outside["camera"]["keyframes"][1]["yaw_deg"] = 1
    with pytest.raises(LayeredSceneError, match="camera yaw 1 deg is outside authored view envelope"):
        LayeredScene(yaw_outside).evaluate(Fraction(27))

    uncovered = _fixture()
    uncovered["camera"]["keyframes"][1]["at_px"] = [300, 318]
    for layer in uncovered["layers"]:
        if layer["kind"] == "character":
            layer["disocclusion_budget_px"] = 1000
    with pytest.raises(LayeredSceneError, match="camera view exposes unpainted area"):
        LayeredScene(uncovered).evaluate(Fraction(27))


def test_nonzero_angle_envelope_is_refused_without_angle_projection() -> None:
    document = _fixture()
    document["view_envelope_deg"]["yaw_deg"] = [-2, 2]
    with pytest.raises(LayeredSceneError, match="only zero-angle yaw/pitch views"):
        LayeredScene(document)

    document = _fixture()
    document["view_envelope_deg"]["pitch_deg"] = [-1, 1]
    with pytest.raises(LayeredSceneError, match="only zero-angle yaw/pitch views"):
        LayeredScene(document)


def test_relative_plane_motion_fails_when_it_exceeds_authored_disocclusion_budget() -> None:
    document = _fixture()
    document["camera"]["keyframes"][1]["at_px"] = [240, 318]
    with pytest.raises(LayeredSceneError, match="exceeds its authored disocclusion budget"):
        LayeredScene(document).evaluate(Fraction(27))


def test_camera_zoom_limits_fail_closed_at_load() -> None:
    document = _fixture()
    document["camera"]["keyframes"][1]["zoom"] = 1.5
    with pytest.raises(LayeredSceneError, match="falls outside authored limits"):
        LayeredScene(document)


def test_depth_extrapolation_rejects_nonpositive_plane_zoom() -> None:
    document = _fixture()
    document["layers"][-1]["depth"] = 4.0
    document["camera"]["zoom_limits"] = [0.7, 1.08]
    document["camera"]["keyframes"][1]["zoom"] = 0.7
    with pytest.raises(LayeredSceneError, match="nonpositive projected zoom"):
        LayeredScene(document)


def test_authored_layer_sizes_and_counts_are_bounded_before_raster_allocation() -> None:
    document = _fixture()
    document["canvas_px"] = [4096, 4096]
    with pytest.raises(LayeredSceneError, match="canvas_px exceeds"):
        LayeredScene(document)

    document = _fixture()
    document["layers"][0]["source_bounds_px"] = [-16000, 0, 16000, 100]
    with pytest.raises(LayeredSceneError, match="source_bounds_px exceeds"):
        LayeredScene(document)

    document = _fixture()
    document["layers"] *= 3
    with pytest.raises(LayeredSceneError, match="layers exceeds"):
        LayeredScene(document)

    document = _fixture()
    document["layers"][0]["shapes"] *= 50
    with pytest.raises(LayeredSceneError, match="shape diagnostic limit"):
        LayeredScene(document)

    document = _fixture()
    document["layers"][0]["shapes"][1]["points_px"] = [[0, 1]] * 129
    with pytest.raises(LayeredSceneError, match="authored points"):
        LayeredScene(document)

    document = _fixture()
    document["layers"][0]["shapes"][1]["points_px"][0] = [1e30, 120]
    with pytest.raises(LayeredSceneError, match="authored coordinate limit"):
        LayeredScene(document)

    document = _fixture()
    document["layers"][0]["shapes"][1]["stroke_width_px"] = 1e30
    with pytest.raises(LayeredSceneError, match="stroke_width_px must be in"):
        LayeredScene(document)


def test_render_is_repeatable_after_arbitrary_random_seek_order() -> None:
    scene = _scene()
    requested = [Fraction(85), Fraction(27), Fraction(50), Fraction(0), Fraction(28), Fraction(27)]
    first = {frame: scene.render(frame).image.tobytes() for frame in requested}

    for frame in (Fraction(12), Fraction(70), Fraction(1), Fraction(54), Fraction(12)):
        scene.render(frame)

    second = {frame: scene.render(frame).image.tobytes() for frame in requested}
    assert first == second


def test_contact_sheet_carries_visible_diagnostic_label_and_exact_receipt(tmp_path: Path) -> None:
    image_path, receipt_path = render_contact_sheet(FIXTURE, tmp_path / "diagnostic.png", [0])
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["diagnostic_label"] == DIAGNOSTIC_LABEL
    assert receipt["sha256"] == hashlib.sha256(image_path.read_bytes()).hexdigest()
    assert receipt["frame_states"][0]["contacts"] == ["attacker-planted-foot"]
    with Image.open(image_path) as image:
        banner = image.crop((0, 0, image.width, 44))
        assert banner.tobytes() != Image.new("RGB", banner.size, (16, 18, 24)).tobytes()


def test_review_only_authority_cannot_be_enabled_by_editing_the_fixture() -> None:
    document = _fixture()
    document["render_eligible"] = True
    with pytest.raises(LayeredSceneError, match="must remain review_only"):
        LayeredScene(document)


def test_scene_frame_range_stays_half_open() -> None:
    scene = _scene()
    with pytest.raises(LayeredSceneError, match="outside the scene frame range"):
        scene.evaluate(Fraction(96))


def test_transparent_pose_and_expression_rasters_use_rgba_compositing_and_seek_deterministically(
    tmp_path: Path,
) -> None:
    document, asset_root = _raster_scene(tmp_path)
    scene = LayeredScene(document, asset_root=asset_root)

    guard_focused = scene.render(Fraction(0), supersample=1)
    recoil_dazed = scene.render(Fraction(28), supersample=1)
    assert guard_focused.image.mode == "RGB"
    assert guard_focused.state.selected_states["fighter-b"] == {"pose": "guard", "expression": "focused"}
    assert recoil_dazed.state.selected_states["fighter-b"] == {"pose": "recoil", "expression": "dazed"}
    # A half-alpha red pose sample composites over the opaque white stage.
    assert guard_focused.image.getpixel((279, 479)) == (255, 127, 127)
    # The independently swappable expression raster overlays the pose raster with its own alpha.
    focused_pixel = guard_focused.image.getpixel((281, 481))
    dazed_document = copy.deepcopy(document)
    _set_channel_value(dazed_document, "fighter-b-pose", 0)
    _set_channel_value(dazed_document, "fighter-b-expression", 1)
    dazed_scene = LayeredScene(dazed_document, asset_root=asset_root)
    dazed_pixel = dazed_scene.render(Fraction(0), supersample=1).image.getpixel((281, 481))
    assert focused_pixel[1] > focused_pixel[2]
    assert dazed_pixel[2] > dazed_pixel[1]
    assert focused_pixel != dazed_pixel

    requested = [Fraction(28), Fraction(0), Fraction(54), Fraction(27), Fraction(28)]
    first = {frame: scene.render(frame, supersample=1).image.tobytes() for frame in requested}
    for frame in (Fraction(12), Fraction(70), Fraction(1), Fraction(54), Fraction(12)):
        scene.render(frame, supersample=1)
    second = {frame: scene.render(frame, supersample=1).image.tobytes() for frame in requested}
    assert first == second
    assert first[Fraction(0)] != first[Fraction(28)]


def test_scene_raster_cache_accepts_unique_assets_under_aggregate_decoded_budget(tmp_path: Path) -> None:
    asset_root = tmp_path / "trusted-large-art"
    document = _document_with_raster_states(asset_root, 7)

    scene = LayeredScene(document, asset_root=asset_root)

    expected_pixels = 7 * 2048 * 1025
    assert expected_pixels <= MAX_SCENE_RASTER_ASSET_PIXELS
    assert expected_pixels * 4 <= MAX_SCENE_RASTER_ASSET_DECODED_BYTES
    assert len(scene._raster_cache) == 7
    assert scene._raster_cache_pixels == expected_pixels
    assert scene._raster_cache_decoded_bytes == expected_pixels * 4


def test_scene_raster_cache_rejects_asset_that_exceeds_aggregate_decoded_budget(tmp_path: Path) -> None:
    asset_root = tmp_path / "trusted-large-art"
    document = _document_with_raster_states(asset_root, 8)

    with pytest.raises(LayeredSceneError, match="scene-wide decoded raster cache budget"):
        LayeredScene(document, asset_root=asset_root)


def test_raster_resources_require_an_explicit_trusted_asset_root(tmp_path: Path) -> None:
    document, _ = _raster_scene(tmp_path)
    with pytest.raises(LayeredSceneError, match="explicit caller-declared asset_root"):
        LayeredScene(document)


@pytest.mark.parametrize("asset_path", ["../outside.png", "C:/outside.png"])
def test_raster_resource_paths_cannot_escape_the_declared_root(tmp_path: Path, asset_path: str) -> None:
    document, asset_root = _raster_scene(tmp_path)
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["pose_states"][0]["raster_asset"]["path"] = asset_path
    with pytest.raises(LayeredSceneError, match="stay inside the caller-declared asset_root"):
        LayeredScene(document, asset_root=asset_root)


def test_raster_resources_reject_missing_and_stale_hash_pins(tmp_path: Path) -> None:
    document, asset_root = _raster_scene(tmp_path)
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["pose_states"][0]["raster_asset"]["sha256"] = "0" * 64
    with pytest.raises(LayeredSceneError, match="does not match its pinned digest"):
        LayeredScene(document, asset_root=asset_root)

    missing, _ = _raster_scene(tmp_path / "missing")
    missing_fighter = next(layer for layer in missing["layers"] if layer["layer_id"] == "fighter-b")
    missing_fighter["pose_states"][0]["raster_asset"]["path"] = "does-not-exist.png"
    with pytest.raises(LayeredSceneError, match="cannot resolve inside asset_root"):
        LayeredScene(missing, asset_root=tmp_path / "missing" / "trusted-art")


def test_raster_resource_symlink_cannot_escape_the_declared_root(tmp_path: Path) -> None:
    document, asset_root = _raster_scene(tmp_path)
    outside = _write_synthetic_art(tmp_path, "outside.png", (255, 0, 255, 128), (1, 1, 6, 6))
    outside_path = tmp_path / outside["path"]
    link_path = asset_root / "escape.png"
    try:
        link_path.symlink_to(outside_path)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation is unavailable in this environment: {exc}")
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["pose_states"][0]["raster_asset"].update({
        "path": link_path.name,
        "sha256": outside["sha256"],
    })
    with pytest.raises(LayeredSceneError, match="cannot resolve inside asset_root"):
        LayeredScene(document, asset_root=asset_root)


def test_raster_resources_require_bounded_transparent_pngs(tmp_path: Path) -> None:
    document, asset_root = _raster_scene(tmp_path)
    opaque_path = asset_root / "opaque.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(opaque_path, format="PNG")
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["pose_states"][0]["raster_asset"].update({
        "path": opaque_path.name,
        "sha256": hashlib.sha256(opaque_path.read_bytes()).hexdigest(),
    })
    with pytest.raises(LayeredSceneError, match="alpha must contain both transparent and visible pixels"):
        LayeredScene(document, asset_root=asset_root)

    oversized_path = asset_root / "oversized.png"
    Image.new("RGBA", (4097, 1), (255, 0, 0, 128)).save(oversized_path, format="PNG")
    fighter["pose_states"][0]["raster_asset"].update({
        "path": oversized_path.name,
        "sha256": hashlib.sha256(oversized_path.read_bytes()).hexdigest(),
    })
    with pytest.raises(LayeredSceneError, match="dimensions exceed the 4096-side"):
        LayeredScene(document, asset_root=asset_root)

    large_pixel_path = asset_root / "too-many-pixels.png"
    Image.new("RGBA", (2000, 1200), (255, 0, 0, 128)).save(large_pixel_path, format="PNG")
    fighter["pose_states"][0]["raster_asset"].update({
        "path": large_pixel_path.name,
        "sha256": hashlib.sha256(large_pixel_path.read_bytes()).hexdigest(),
    })
    with pytest.raises(LayeredSceneError, match="pixel raster asset limit"):
        LayeredScene(document, asset_root=asset_root)

    oversized_file = asset_root / "too-large.png"
    with oversized_file.open("wb") as stream:
        stream.truncate(MAX_RASTER_ASSET_BYTES + 1)
    fighter["pose_states"][0]["raster_asset"]["path"] = oversized_file.name
    with pytest.raises(LayeredSceneError, match="byte raster asset limit"):
        LayeredScene(document, asset_root=asset_root)


def test_raster_extent_must_fit_the_declared_silhouette_envelope(tmp_path: Path) -> None:
    document, asset_root = _raster_scene(tmp_path)
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["pose_states"][0]["raster_asset"]["bounds_local_px"] = [-100, -40, -92, -32]
    with pytest.raises(LayeredSceneError, match="must stay inside silhouette_bounds_local_px"):
        LayeredScene(document, asset_root=asset_root)


def test_raster_local_bounds_are_bounded_before_large_resize(tmp_path: Path) -> None:
    document, asset_root = _raster_scene(tmp_path)
    fighter = next(layer for layer in document["layers"] if layer["layer_id"] == "fighter-b")
    fighter["silhouette_bounds_local_px"] = [-16000, -16000, 16000, 16000]
    fighter["pose_states"][0]["raster_asset"]["bounds_local_px"] = [-15000, -15000, 15000, 15000]
    scene = LayeredScene(document, asset_root=asset_root)
    with pytest.raises(LayeredSceneError, match="projected raster art exceeds the .*pixel allocation limit"):
        scene.render(Fraction(0), supersample=1)


def test_contact_sheet_can_render_caller_rooted_raster_assets(tmp_path: Path) -> None:
    document, asset_root = _raster_scene(tmp_path)
    scene_path = tmp_path / "scene.json"
    scene_path.write_text(json.dumps(document), encoding="utf-8")
    image_path, receipt_path = render_contact_sheet(
        scene_path, tmp_path / "raster-contact.png", [0], asset_root=asset_root
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["diagnostic_only"] is True
    assert receipt["sha256"] == hashlib.sha256(image_path.read_bytes()).hexdigest()
