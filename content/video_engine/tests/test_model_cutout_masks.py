from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from content.video_engine.src.modeling.layered import LayeredScene, LayeredSceneError


ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / 'content/video_engine/tests/fixtures/modeling/layered/authored/knockout-authored-layers.v1.json'


def _scene_document(tmp_path: Path, *, masked: bool = True) -> tuple[dict, Path]:
    asset_root = tmp_path / 'art'
    asset_root.mkdir(parents=True, exist_ok=True)
    source = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(source)
    draw.rectangle((1, 2, 7, 13), fill=(230, 40, 50, 255))
    draw.rectangle((8, 2, 14, 13), fill=(35, 85, 225, 255))
    path = asset_root / 'shared-character.png'
    source.save(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()

    doc = json.loads(FIXTURE.read_text(encoding='utf-8'))
    doc['canvas_px'] = [64, 64]
    doc['clear_color'] = '#ffffff'
    doc['camera'] = {
        'zoom_limits': [1, 1],
        'keyframes': [{'frame': 0, 'zoom': 1, 'look_px': [32, 32], 'at_px': [32, 32],
                       'yaw_deg': 0, 'pitch_deg': 0}],
    }
    doc['scene']['duration_frames'] = 16
    doc['scene']['events'] = []
    doc['scene']['contacts'] = []
    doc['scene']['motion_channels'] = [
        {'channel_id': 'pose', 'binding_id': 'fighter_b', 'target_kind': 'articulation',
         'semantic_target': 'pose', 'value_unit': 'normalized', 'interpolation': 'step',
         'keyframes': [{'frame': 0, 'value': 0}]},
        {'channel_id': 'expression', 'binding_id': 'fighter_b', 'target_kind': 'face_control',
         'semantic_target': 'expression', 'value_unit': 'normalized', 'interpolation': 'step',
         'keyframes': [{'frame': 0, 'value': 0}]},
        {'channel_id': 'arm-angle', 'binding_id': 'fighter_b', 'target_kind': 'articulation',
         'semantic_target': 'arm_pivot', 'value_unit': 'degrees', 'interpolation': 'linear',
         'keyframes': [{'frame': 0, 'value': 0}, {'frame': 8, 'value': 10}]},
    ]
    background = {
        'layer_id': 'background', 'kind': 'environment', 'role': 'background', 'depth': 1,
        'source_bounds_px': [-16, -16, 80, 80], 'painted_bounds_px': [-16, -16, 80, 80],
        'shapes': [{'kind': 'rect', 'bounds_px': [-16, -16, 80, 80], 'fill': '#ffffff'}],
    }

    def character(name: str, polygon: list[list[float]] | None, silhouette: list[int]) -> dict:
        raster = {
            'path': path.name, 'sha256': digest, 'bounds_local_px': [0, 0, 16, 16],
        }
        if polygon is not None:
            raster['mask_polygon_image_px'] = polygon
        return {
            'layer_id': name, 'kind': 'character', 'binding_id': 'fighter_b',
            'role': 'subject', 'depth': 1.25, 'source_bounds_px': [-16, -16, 80, 80],
            'anchor_px': [24, 24], 'shapes': [], 'pose_channel': 'pose',
            'expression_channel': 'expression',
            'silhouette_bounds_local_px': silhouette,
            'pose_states': [{'state_id': 'rest', 'index': 0, 'shapes': [], 'raster_asset': raster}],
            'expression_states': [{'state_id': 'neutral', 'index': 0, 'shapes': []}],
            'disocclusion_budget_px': 0,
        }

    left = character('left-part', [[0, 0], [7, 0], [7, 16], [0, 16]], [0, 0, 8, 16])
    if masked:
        right = character('right-part', [[8, 0], [16, 0], [16, 16], [8, 16]], [8, 0, 16, 16])
        doc['layers'] = [background, left, right]
    else:
        left['pose_states'][0]['raster_asset'].pop('mask_polygon_image_px')
        left['silhouette_bounds_local_px'] = [0, 0, 16, 16]
        doc['layers'] = [background, left]
    return doc, asset_root


def test_two_masks_recompose_one_source_at_rest_and_share_decoded_cache(tmp_path: Path) -> None:
    cutout_doc, root = _scene_document(tmp_path / 'masked')
    whole_doc, whole_root = _scene_document(tmp_path / 'whole', masked=False)
    cutout = LayeredScene(cutout_doc, asset_root=root)
    whole = LayeredScene(whole_doc, asset_root=whole_root)
    assert len(cutout._raster_cache) == 1
    assert cutout._raster_cache_decoded_bytes == 16 * 16 * 4
    assert cutout.render(Fraction(0), supersample=1).image.tobytes() == \
        whole.render(Fraction(0), supersample=1).image.tobytes()
    assert cutout.render(Fraction(8), supersample=1).image.tobytes() == \
        whole.render(Fraction(8), supersample=1).image.tobytes()


def test_masked_part_rotates_without_moving_other_part(tmp_path: Path) -> None:
    doc, root = _scene_document(tmp_path)
    doc['layers'][1]['sprite_pivot'] = {
        'channel_id': 'arm-angle', 'max_abs_angle_deg': 10, 'pivot_local_px': [7, 8],
    }
    scene = LayeredScene(doc, asset_root=root)
    neutral = scene.render(Fraction(0), supersample=1).image
    moved = scene.render(Fraction(8), supersample=1).image
    assert neutral.tobytes() != moved.tobytes()
    assert neutral.crop((32, 24, 40, 40)).tobytes() == moved.crop((32, 24, 40, 40)).tobytes()
    for frame in (Fraction(8), Fraction(0), Fraction(12), Fraction(8)):
        scene.render(frame, supersample=1)
    assert scene.render(Fraction(8), supersample=1).image.tobytes() == moved.tobytes()


@pytest.mark.parametrize('polygon, message', [
    ([[0, 0], [17, 0], [0, 16]], 'inside the raster dimensions'),
    ([[0, 0], [1, 1]], '3..128'),
    ([[0, 0], [4, 4], [8, 8]], 'nonzero area'),
    ([[0, 0], [1, 0], [1, 1], [0, 1]], 'does not select any visible'),
])
def test_mask_rejects_invalid_or_empty_polygon(tmp_path: Path, polygon: list[list[int]], message: str) -> None:
    doc, root = _scene_document(tmp_path)
    doc['layers'][1]['pose_states'][0]['raster_asset']['mask_polygon_image_px'] = polygon
    with pytest.raises(LayeredSceneError, match=message):
        LayeredScene(doc, asset_root=root)


def test_masked_visible_bounds_must_fit_declared_silhouette(tmp_path: Path) -> None:
    doc, root = _scene_document(tmp_path)
    doc['layers'][1]['silhouette_bounds_local_px'] = [0, 0, 3, 16]
    with pytest.raises(LayeredSceneError, match='raster bounds must stay inside'):
        LayeredScene(doc, asset_root=root)


def test_cached_source_does_not_bypass_second_mask_validation(tmp_path: Path) -> None:
    doc, root = _scene_document(tmp_path)
    doc['layers'][2]['pose_states'][0]['raster_asset']['mask_polygon_image_px'] = [
        [20, 0], [22, 0], [22, 16], [20, 16],
    ]
    with pytest.raises(LayeredSceneError, match='inside the raster dimensions'):
        LayeredScene(doc, asset_root=root)
