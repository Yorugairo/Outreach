from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from content.video_engine.src.modeling.layered import LayeredScene, LayeredSceneError


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / 'content/video_engine/tests/fixtures/modeling/layered/authored/knockout-authored-layers.v1.json'
SIDECAR = ROOT / 'content/video_engine/tests/fixtures/modeling/layered/rig/attacker-planted-foot.planar-rig.v1.json'
LOCAL_SOLVER = ROOT / 'content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-foundation/rig_math.py'


def _inputs() -> tuple[dict, dict]:
    return json.loads(FIXTURE.read_text(encoding='utf-8')), json.loads(SIDECAR.read_text(encoding='utf-8'))


def _scene() -> LayeredScene:
    return LayeredScene.load(FIXTURE, planar_rig_path=SIDECAR)


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.dist(a, b)


def test_planted_foot_uses_shared_half_open_contact_and_rest_fk_on_release() -> None:
    scene = _scene()
    assert scene.timeline.clock.fps == Fraction(24)
    assert scene.planar_rig is not None
    poses = {frame: scene.evaluate(Fraction(frame)).planar_pose for frame in (0, 27, 40, 41)}
    target = (81.2, 515.4)
    anchor_at_zero = scene.evaluate(0).anchors_px['fighter-a']
    assert target == pytest.approx((anchor_at_zero[0] - 34, anchor_at_zero[1] - 3))
    for frame in (0, 27, 40):
        pose = poses[frame]
        assert pose is not None and pose.mode == 'ik_contact' and pose.reachable is True
        assert pose.requested_endpoint_canvas_px == target
        assert pose.solved_endpoint_canvas_px == pytest.approx(target, abs=1e-6)
        assert pose.residual_px <= 1e-6
        assert _distance(pose.root_canvas_px, pose.hinge_canvas_px) == pytest.approx(pose.upper_length_canvas_px)
        assert _distance(pose.hinge_canvas_px, pose.end_canvas_px) == pytest.approx(pose.lower_length_canvas_px)
    assert poses[0].root_canvas_px != poses[27].root_canvas_px
    assert poses[27].hinge_canvas_px != poses[40].hinge_canvas_px
    released = poses[41]
    assert released is not None and released.mode == 'fk_rest' and released.reachable is None
    assert released.end_local_px == (-34.0, -3.0)
    assert released.solved_endpoint_canvas_px != pytest.approx(target, abs=1e-3)
    assert 'attacker-planted-foot' not in scene.evaluate(41).contacts


def test_arbitrary_seek_is_stateless_and_no_sidecar_preserves_pixels() -> None:
    scene = _scene()
    expected = {frame: scene.evaluate(frame).planar_pose for frame in (0, 27, 40, 41)}
    for frame in (41, 27, 0, 40, 27, 41):
        assert scene.evaluate(frame).planar_pose == expected[frame]
    plain = LayeredScene.load(FIXTURE)
    assert plain.evaluate(27).planar_pose is None
    baseline = {
        0: 'a4f43977431e02926291cfe03bbe177b07e2f8290c53bd97235a4130fa104657',
        27: '2937e10f5ba39c9c579b95b8aff7cb39f3064e3e316c082ec3950caf6436f56e',
        40: 'ddfe76b7ec12df2925ce4867fb1e6d14f60fd3f918b0a9d4b433566e692178d3',
        41: '94236f55b7bf22d883a06889ad0aa7f718f1de7b45dbcc0a8f53a9efd2f8c40a',
    }
    for frame in (0, 27, 40, 41):
        original = plain.render(frame).image.tobytes()
        assert hashlib.sha256(original).hexdigest() == baseline[frame]
        assert scene.render(frame).image.tobytes() != original


def test_scale_and_flip_use_the_same_layer_transform_as_drawing() -> None:
    document, sidecar = _inputs()
    fighter = next(layer for layer in document['layers'] if layer['layer_id'] == 'fighter-a')
    fighter['flip_x'] = True
    scale = next(channel for channel in document['scene']['motion_channels']
                 if channel['channel_id'] == 'fighter-a-scale')
    scale['keyframes'][0]['value'] = 1.5
    sidecar['target_canvas_px'] = [166.2, 513.9]  # transformed frame-0 rest foot
    scene = LayeredScene(document, planar_rig=sidecar)
    pose = scene.evaluate(27).planar_pose
    assert pose is not None and pose.mode == 'ik_contact' and pose.reachable
    assert pose.end_canvas_px == pytest.approx(sidecar['target_canvas_px'], abs=1e-6)
    assert pose.upper_length_canvas_px == pytest.approx(pose.upper_length_local_px * 1.5)
    assert pose.lower_length_canvas_px == pytest.approx(pose.lower_length_local_px * 1.5)
    anchor = scene.evaluate(27).anchors_px['fighter-a']
    assert pose.root_canvas_px == pytest.approx((anchor[0] - pose.root_local_px[0] * 1.5,
                                                anchor[1] + pose.root_local_px[1] * 1.5))
    assert scene.render(27).image.size == (360, 640)


def test_unreachable_target_is_clamped_and_reports_residual_and_lengths() -> None:
    document, sidecar = _inputs()
    sidecar['target_canvas_px'] = [330, 515.4]
    pose = LayeredScene(document, planar_rig=sidecar).evaluate(27).planar_pose
    assert pose is not None and pose.mode == 'ik_contact' and pose.reachable is False
    assert pose.residual_px > 100
    assert pose.residual_px == pytest.approx(_distance(pose.requested_endpoint_canvas_px,
                                                      pose.solved_endpoint_canvas_px))
    assert _distance(pose.root_canvas_px, pose.end_canvas_px) == pytest.approx(
        pose.upper_length_canvas_px + pose.lower_length_canvas_px, abs=1e-5
    )
    assert _distance(pose.root_canvas_px, pose.hinge_canvas_px) == pytest.approx(pose.upper_length_canvas_px)
    assert _distance(pose.hinge_canvas_px, pose.end_canvas_px) == pytest.approx(pose.lower_length_canvas_px)


@pytest.mark.parametrize(('path', 'bad', 'message'), [
    (('schema_version',), 'planar_rig.v2', 'schema_version'),
    (('review_state',), 'approved', 'review_only'),
    (('render_eligible',), True, 'non-render-eligible'),
    (('scene_id',), 'other', 'scene_id'),
    (('layer_id',), 'canvas-mat', 'character layer'),
    (('binding_id',), 'fighter_b', 'binding_id'),
    (('contact_id',), 'unknown', 'contact_id'),
    (('semantic_effector',), 'right_hand', 'semantics'),
    (('target_surface_id',), 'other-floor', 'semantics'),
    (('joint_unit',), 'world3d_m', 'layer_local_px'),
    (('target_unit',), 'normalized', 'canvas_px'),
    (('target_canvas_px',), [400, 515], 'inside the canvas'),
    (('bend_sign',), -1, 'bend_sign'),
    (('rest_joints_local_px', 'hinge'), [-27.5, -36], 'non-collinear'),
    (('rest_joints_local_px', 'root'), [-99, -69], 'silhouette'),
])
def test_invalid_sidecars_fail_closed(path: tuple[str, ...], bad: object, message: str) -> None:
    document, sidecar = _inputs()
    item = sidecar
    for key in path[:-1]:
        item = item[key]
    item[path[-1]] = bad
    with pytest.raises(LayeredSceneError, match=message):
        LayeredScene(document, planar_rig=sidecar)


def test_sidecar_refuses_its_own_clock_and_unsupported_camera_view() -> None:
    document, sidecar = _inputs()
    sidecar['duration_frames'] = 41
    with pytest.raises(LayeredSceneError, match='no clock or events'):
        LayeredScene(document, planar_rig=sidecar)
    sidecar.pop('duration_frames')
    document['view_envelope_deg']['yaw_deg'] = [-1, 1]
    with pytest.raises(LayeredSceneError, match='zero-angle yaw/pitch'):
        LayeredScene(document, planar_rig=sidecar)


def test_loaded_non_object_sidecar_cannot_silently_disable_the_rig(tmp_path: Path) -> None:
    bad = tmp_path / 'rig.json'
    bad.write_text('null', encoding='utf-8')
    with pytest.raises(LayeredSceneError, match='JSON root must be an object'):
        LayeredScene.load(FIXTURE, planar_rig_path=bad)


def test_tiny_layer_scale_is_rejected_before_inverse_target_math() -> None:
    document, sidecar = _inputs()
    scale = next(channel for channel in document['scene']['motion_channels']
                 if channel['channel_id'] == 'fighter-a-scale')
    scale['keyframes'][0]['value'] = 1.0e-300
    with pytest.raises(LayeredSceneError, match='finite scale in 1e-6..16'):
        LayeredScene(document, planar_rig=sidecar).evaluate(27)


def test_analytic_solution_matches_project_local_planar_ik() -> None:
    spec = importlib.util.spec_from_file_location('local_rig_math_for_planar_test', LOCAL_SOLVER)
    assert spec and spec.loader
    local = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = local
    spec.loader.exec_module(local)
    scene = _scene()
    rig = scene.planar_rig
    assert rig is not None
    for frame in (0, 27, 40):
        state = scene.evaluate(frame)
        pose = state.planar_pose
        assert pose is not None
        anchor = state.anchors_px['fighter-a']
        target_local = ( (rig.target_canvas_px[0] - anchor[0]),
                         (rig.target_canvas_px[1] - anchor[1]) )
        reference = local.two_bone_ik(rig.root, target_local, rig.upper_length,
                                      rig.lower_length, bend=rig.bend_sign)
        assert pose.hinge_local_px == pytest.approx(reference.elbow, abs=1e-7)
        assert pose.end_local_px == pytest.approx(reference.end, abs=1e-7)
