from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.modeling.layered import (
    DIAGNOSTIC_LABEL,
    LayeredScene,
    LayeredSceneError,
    render_contact_sheet,
)


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "content/video_engine/tests/fixtures/modeling/layered/authored/knockout-authored-layers.v1.json"


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _scene() -> LayeredScene:
    return LayeredScene.load(FIXTURE)


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
