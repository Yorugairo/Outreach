"""Deterministic, editable 2.5D authored-layer scene evaluation and raster preview.

This backend composes diagnostic vectors and caller-rooted, hash-pinned transparent
pose/expression PNGs on declared depth planes. Motion comes from the backend-neutral
RationalClock and MotionTimeline. Raster inputs remain local preview resources; T3
staged-asset integration belongs to later slices. It does not infer hidden geometry
or certify physical contact or finished art.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
from io import BytesIO
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Sequence

from PIL import Image, ImageColor, ImageDraw, ImageFont

from content.video_engine.scripts.build_plate_library import LAYER_PLANES
from .motion import MotionContractError, MotionSample, MotionTimeline
from .planar_rig import PlanarPose, PlanarRig, PlanarRigError


MAX_CANVAS_PIXELS = 2_304_000
MAX_SOURCE_PIXELS = 2_304_000
MAX_RASTER_ASSET_BYTES = 16_777_216
MAX_RASTER_PIXELS = 36_864_000
# Bound eager retention of pose/expression swaps to 64 MiB of decoded RGBA art.
MAX_SCENE_RASTER_ASSET_PIXELS = 16_777_216
MAX_SCENE_RASTER_ASSET_DECODED_BYTES = 67_108_864
MAX_SHEET_PIXELS = 24_000_000
MAX_LAYERS = 16
MAX_SHAPES = 128
MAX_STATES = 8
MAX_POINTS = 128
MAX_COORD = 16_384
DIAGNOSTIC_LABEL = 'DIAGNOSTIC — SYNTHETIC CONTACT CLOCK / NOT APPROVED ART OR PHYSICS'


class LayeredSceneError(ValueError):
    """An authored layer scene or requested camera state cannot be rendered safely."""


@dataclass(frozen=True)
class CameraState:
    zoom: float
    look_px: tuple[float, float]
    at_px: tuple[float, float]
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0


@dataclass(frozen=True)
class LayeredFrameState:
    scene_id: str
    frame: Fraction
    time_seconds: Fraction
    events: tuple[str, ...]
    contacts: tuple[str, ...]
    camera: CameraState
    selected_states: Mapping[str, Mapping[str, str]]
    anchors_px: Mapping[str, tuple[float, float]]
    layer_order: tuple[str, ...]
    diagnostic_status: str
    planar_pose: PlanarPose | None = None


@dataclass(frozen=True)
class LayeredRender:
    image: Image.Image
    state: LayeredFrameState


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LayeredSceneError(f'{label} must be numeric')
    result = float(value)
    if not math.isfinite(result):
        raise LayeredSceneError(f'{label} must be finite')
    return result


def _pair(value: Any, label: str, *, ordered: bool = False) -> tuple[float, float]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 2:
        raise LayeredSceneError(f'{label} must contain two numbers')
    result = (_finite(value[0], f'{label}[0]'), _finite(value[1], f'{label}[1]'))
    if any(abs(item) > MAX_COORD for item in result):
        raise LayeredSceneError(f'{label} exceeds the authored coordinate limit')
    if ordered and result[0] > result[1]:
        raise LayeredSceneError(f'{label} minimum must not exceed maximum')
    return result


def _rect(value: Any, label: str) -> tuple[float, float, float, float]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 4:
        raise LayeredSceneError(f'{label} must be [left, top, right, bottom]')
    result = tuple(_finite(item, f'{label}[{index}]') for index, item in enumerate(value))
    if result[0] >= result[2] or result[1] >= result[3]:
        raise LayeredSceneError(f'{label} must have positive width and height')
    if any(abs(item) > MAX_COORD for item in result):
        raise LayeredSceneError(f'{label} exceeds the authored coordinate limit')
    return result  # type: ignore[return-value]


def _color(value: Any, label: str) -> tuple[int, int, int, int]:
    if not isinstance(value, str):
        raise LayeredSceneError(f'{label} must be a CSS color string')
    try:
        return ImageColor.getcolor(value, 'RGBA')
    except ValueError as exc:
        raise LayeredSceneError(f'{label} is not a valid color') from exc


def _validate_shapes(shapes: Any, label: str) -> tuple[dict[str, Any], ...]:
    if not isinstance(shapes, list):
        raise LayeredSceneError(f'{label} must be an array of authored primitives')
    if len(shapes) > MAX_SHAPES:
        raise LayeredSceneError(f'{label} exceeds the {MAX_SHAPES}-shape diagnostic limit')
    checked: list[dict[str, Any]] = []
    for index, raw in enumerate(shapes):
        where = f'{label}[{index}]'
        if not isinstance(raw, Mapping):
            raise LayeredSceneError(f'{where} must be an object')
        shape = dict(raw)
        kind = shape.get('kind')
        if kind in {'rect', 'ellipse'}:
            shape['_bounds'] = _rect(shape.get('bounds_px'), f'{where}.bounds_px')
        elif kind in {'polygon', 'line'}:
            points = shape.get('points_px')
            minimum_points = 3 if kind == 'polygon' else 2
            if not isinstance(points, list) or not minimum_points <= len(points) <= MAX_POINTS:
                raise LayeredSceneError(f'{where}.points_px must contain {minimum_points}..{MAX_POINTS} authored points')
            shape['_points'] = tuple(_pair(point, f'{where}.points_px[{point_index}]')
                                     for point_index, point in enumerate(points))
        else:
            raise LayeredSceneError(f'{where}.kind must be rect, ellipse, polygon, or line')

        fill = shape.get('fill')
        stroke = shape.get('stroke')
        if fill is None and stroke is None:
            raise LayeredSceneError(f'{where} needs fill or stroke')
        if fill is not None:
            shape['_fill'] = _color(fill, f'{where}.fill')
        if stroke is not None:
            shape['_stroke'] = _color(stroke, f'{where}.stroke')
            stroke_width = _finite(shape.get('stroke_width_px', 1), f'{where}.stroke_width_px')
            if not 0 < stroke_width <= 1024:
                raise LayeredSceneError(f'{where}.stroke_width_px must be in 0..1024')
            shape['_stroke_width'] = stroke_width
        radius = _finite(shape.get('radius_px', 0), f'{where}.radius_px')
        if not 0 <= radius <= 4096:
            raise LayeredSceneError(f'{where}.radius_px must be in 0..4096')
        shape['_radius'] = radius
        checked.append(shape)
    return tuple(checked)


def _paint_rect_covers(shapes: Sequence[Mapping[str, Any]], rect: tuple[float, float, float, float]) -> bool:
    """A declared background coverage rectangle must be backed by opaque authored fill."""
    for shape in shapes:
        bounds = shape.get('_bounds')
        fill = shape.get('_fill')
        if shape.get('kind') != 'rect' or not bounds or not fill or fill[3] != 255:
            continue
        if bounds[0] <= rect[0] and bounds[1] <= rect[1] and bounds[2] >= rect[2] and bounds[3] >= rect[3]:
            return True
    return False


def _channel_value(sample: MotionSample, channel_id: str, label: str) -> float:
    for channel in sample.channels:
        if channel.channel_id == channel_id:
            if isinstance(channel.value, tuple):
                raise LayeredSceneError(f'{label} channel {channel_id!r} must be scalar')
            return float(channel.value)
    raise LayeredSceneError(f'{label} references missing motion channel {channel_id!r}')


def _ease(name: str, amount: float) -> float:
    clamped = min(1.0, max(0.0, amount))
    if name == 'linear':
        return clamped
    if name == 'smoothstep':
        return clamped * clamped * (3.0 - 2.0 * clamped)
    raise LayeredSceneError(f'unsupported authored interpolation {name!r}; use linear or smoothstep')


class LayeredScene:
    """Validated authored-layer input with a pure, random-seekable frame evaluator."""

    def __init__(
        self, document: Mapping[str, Any], *, asset_root: str | Path | None = None,
        planar_rig: Mapping[str, Any] | None = None,
    ):
        raw = dict(document)
        if raw.get('schema_version') != 'authored_layer_scene.v1':
            raise LayeredSceneError('schema_version must be authored_layer_scene.v1')
        if raw.get('review_state') != 'review_only' or raw.get('render_eligible') is not False:
            raise LayeredSceneError('authored-layer diagnostics must remain review_only and non-render-eligible')
        self.document = raw
        self.scene_id = raw.get('scene_id')
        if not isinstance(self.scene_id, str) or not self.scene_id:
            raise LayeredSceneError('scene_id must be a non-empty string')
        canvas = raw.get('canvas_px')
        if not isinstance(canvas, list) or len(canvas) != 2 or any(
            isinstance(value, bool) or not isinstance(value, int) or not 64 <= value <= 4096 for value in canvas
        ):
            raise LayeredSceneError('canvas_px must contain integer width and height in 64..4096')
        self.width, self.height = canvas
        if self.width * self.height > MAX_CANVAS_PIXELS:
            raise LayeredSceneError(f'canvas_px exceeds the {MAX_CANVAS_PIXELS}-pixel diagnostic limit')
        self._asset_root: Path | None = None
        self._raster_cache: dict[tuple[str, str], dict[str, Any]] = {}
        self._raster_cache_pixels = 0
        self._raster_cache_decoded_bytes = 0
        if asset_root is not None:
            try:
                trusted_root = Path(asset_root).resolve(strict=True)
            except (OSError, TypeError, ValueError) as exc:
                raise LayeredSceneError(f'cannot resolve caller-declared raster asset_root: {exc}') from exc
            if not trusted_root.is_dir():
                raise LayeredSceneError('caller-declared raster asset_root must be a directory')
            self._asset_root = trusted_root
        try:
            self.timeline = MotionTimeline.from_scene(raw.get('scene', {}))
        except MotionContractError as exc:
            raise LayeredSceneError(f'shared motion clock/scene contract: {exc}') from exc
        if self.timeline.scene_id != self.scene_id:
            raise LayeredSceneError('scene_id must match the shared motion scene_id')
        self._channel_contracts = {channel.channel_id: channel for channel in self.timeline.channels}
        self.layers = self._parse_layers(raw.get('layers'))
        self._projection_groups_by_start = self._parse_projection_groups(raw.get('projection_groups', []))
        self.camera = self._parse_camera(raw.get('camera'))
        self.view_envelope = raw.get('view_envelope_deg')
        if not isinstance(self.view_envelope, Mapping):
            raise LayeredSceneError('view_envelope_deg must declare yaw_deg and pitch_deg limits')
        self.yaw_limits = _pair(self.view_envelope.get('yaw_deg'), 'view_envelope_deg.yaw_deg', ordered=True)
        self.pitch_limits = _pair(self.view_envelope.get('pitch_deg'), 'view_envelope_deg.pitch_deg', ordered=True)
        if self.yaw_limits != (0.0, 0.0) or self.pitch_limits != (0.0, 0.0):
            raise LayeredSceneError('authored-layer preview supports only zero-angle yaw/pitch views')
        self.occlusion_policy = raw.get('occlusion_policy')
        if self.occlusion_policy != 'declared_depth_back_to_front':
            raise LayeredSceneError('occlusion_policy must be declared_depth_back_to_front')
        self.planar_rig: PlanarRig | None = None
        if planar_rig is not None:
            try:
                self.planar_rig = PlanarRig.from_document(
                    planar_rig, scene_id=self.scene_id, layers=self.layers,
                    contacts=self.timeline.contacts, canvas_px=(self.width, self.height),
                )
            except PlanarRigError as exc:
                raise LayeredSceneError(f'planar rig sidecar: {exc}') from exc

    @classmethod
    def load(
        cls, path: str | Path, *, asset_root: str | Path | None = None,
        planar_rig_path: str | Path | None = None,
    ) -> LayeredScene:
        try:
            value = json.loads(Path(path).read_text(encoding='utf-8'))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise LayeredSceneError(f'cannot read authored layer JSON: {exc}') from exc
        if not isinstance(value, Mapping):
            raise LayeredSceneError('authored layer JSON root must be an object')
        rig = None
        if planar_rig_path is not None:
            try:
                rig = json.loads(Path(planar_rig_path).read_text(encoding='utf-8'))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                raise LayeredSceneError(f'cannot read planar rig sidecar JSON: {exc}') from exc
            if not isinstance(rig, Mapping):
                raise LayeredSceneError('planar rig sidecar JSON root must be an object')
        return cls(value, asset_root=asset_root, planar_rig=rig)

    def _parse_layers(self, value: Any) -> tuple[dict[str, Any], ...]:
        if not isinstance(value, list) or not value:
            raise LayeredSceneError('layers must be a non-empty array')
        if len(value) > MAX_LAYERS:
            raise LayeredSceneError(f'layers exceeds the {MAX_LAYERS}-layer diagnostic limit')
        parsed: list[dict[str, Any]] = []
        seen: set[str] = set()
        previous_depth = -math.inf
        for index, raw in enumerate(value):
            label = f'layers[{index}]'
            if not isinstance(raw, Mapping):
                raise LayeredSceneError(f'{label} must be an object')
            layer = dict(raw)
            layer_id = layer.get('layer_id')
            if not isinstance(layer_id, str) or not layer_id or layer_id in seen:
                raise LayeredSceneError(f'{label}.layer_id must be unique and non-empty')
            seen.add(layer_id)
            role = layer.get('role')
            if role not in LAYER_PLANES:
                raise LayeredSceneError(f'{label}.role must be one of {", ".join(LAYER_PLANES)}')
            depth = _finite(layer.get('depth', LAYER_PLANES[role][1]), f'{label}.depth')
            if not 0 <= depth <= 4:
                raise LayeredSceneError(f'{label}.depth must be in the shared camera range 0..4')
            if depth < previous_depth:
                raise LayeredSceneError('layers must be authored back-to-front with depth ascending')
            previous_depth = depth
            kind = layer.get('kind')
            if kind not in {'environment', 'prop', 'character', 'occluder'}:
                raise LayeredSceneError(f'{label}.kind must be environment, prop, character, or occluder')
            binding_id = layer.get('binding_id')
            if kind in {'character', 'prop'} and (not isinstance(binding_id, str) or not binding_id):
                raise LayeredSceneError(f'{label}.binding_id must identify a character or prop motion owner')
            layer['depth'] = depth
            layer['_shapes'] = _validate_shapes(layer.get('shapes', []), f'{label}.shapes')
            source_bounds = _rect(layer.get('source_bounds_px', [0, 0, self.width, self.height]),
                                  f'{label}.source_bounds_px')
            source_width = source_bounds[2] - source_bounds[0]
            source_height = source_bounds[3] - source_bounds[1]
            if (source_width > 4096 or source_height > 4096
                    or source_width * source_height > MAX_SOURCE_PIXELS):
                raise LayeredSceneError(f'{label}.source_bounds_px exceeds the source raster limit')
            layer['_source_bounds'] = source_bounds
            painted_raw = layer.get('painted_bounds_px')
            if painted_raw is not None:
                painted = _rect(painted_raw, f'{label}.painted_bounds_px')
                if not (source_bounds[0] <= painted[0] and source_bounds[1] <= painted[1]
                        and source_bounds[2] >= painted[2] and source_bounds[3] >= painted[3]):
                    raise LayeredSceneError(f'{label}.painted_bounds_px must sit inside source_bounds_px')
                layer['_painted_bounds'] = painted
            if role == 'background':
                if painted_raw is None:
                    raise LayeredSceneError(f'{label} background needs declared painted_bounds_px for camera disocclusion checks')
                if not _paint_rect_covers(layer['_shapes'], layer['_painted_bounds']):
                    raise LayeredSceneError(f'{label} declared background coverage has no opaque authored rectangle')

            anchor = layer.get('anchor_px', [0, 0])
            layer['_anchor_px'] = _pair(anchor, f'{label}.anchor_px')
            anchor_channels = layer.get('anchor_channels', {})
            if not isinstance(anchor_channels, Mapping):
                raise LayeredSceneError(f'{label}.anchor_channels must be an object')
            layer['_anchor_channels'] = dict(anchor_channels)
            for axis in ('x', 'y'):
                channel_id = anchor_channels.get(axis)
                if channel_id is not None:
                    self._require_channel(
                        channel_id, f'{label}.anchor_channels.{axis}', 'normalized',
                        ('object_transform',), ('linear', 'cubic'), binding_id,
                    )
            scale_channel = layer.get('scale_channel')
            if scale_channel is not None:
                self._require_channel(
                    scale_channel, f'{label}.scale_channel', 'normalized',
                    ('object_transform',), ('linear', 'cubic'), binding_id,
                )
            if kind == 'character':
                if not all(layer.get(field) for field in ('pose_channel', 'expression_channel')):
                    raise LayeredSceneError(f'{label} character needs pose_channel and expression_channel')
                self._require_channel(
                    layer['pose_channel'], f'{label}.pose_channel', 'normalized',
                    ('articulation',), ('step',), binding_id,
                )
                self._require_channel(
                    layer['expression_channel'], f'{label}.expression_channel', 'normalized',
                    ('face_control',), ('step',), binding_id,
                )
                if layer.get('silhouette_bounds_local_px') is None:
                    raise LayeredSceneError(f'{label} character needs silhouette_bounds_local_px for disocclusion checks')
                layer['_silhouette_bounds'] = _rect(
                    layer.get('silhouette_bounds_local_px'), f'{label}.silhouette_bounds_local_px'
                )
                layer['_pose_states'] = self._parse_states(layer.get('pose_states'), f'{label}.pose_states')
                layer['_expression_states'] = self._parse_states(
                    layer.get('expression_states'), f'{label}.expression_states'
                )
                for state_group in (layer['_pose_states'], layer['_expression_states']):
                    for state in state_group:
                        raster = state.get('_raster_asset')
                        if raster is None:
                            continue
                        raster_bounds = raster['_bounds_local']
                        silhouette = layer['_silhouette_bounds']
                        if not (silhouette[0] <= raster_bounds[0] and silhouette[1] <= raster_bounds[1]
                                and silhouette[2] >= raster_bounds[2] and silhouette[3] >= raster_bounds[3]):
                            raise LayeredSceneError(
                                f"{label} {state['state_id']!r} raster bounds must stay inside "
                                'silhouette_bounds_local_px for disocclusion checks'
                            )
                budget = _finite(layer.get('disocclusion_budget_px'), f'{label}.disocclusion_budget_px')
                if budget < 0:
                    raise LayeredSceneError(f'{label}.disocclusion_budget_px cannot be negative')
                layer['_disocclusion_budget'] = budget
            elif layer.get('pose_channel') or layer.get('expression_channel'):
                raise LayeredSceneError(f'{label} only character layers may declare pose/expression channels')
            if kind in {'prop', 'environment'}:
                layer['_static_shapes'] = layer['_shapes']
            parsed.append(layer)
        return tuple(parsed)

    def _parse_projection_groups(self, value: Any) -> dict[int, int]:
        if not isinstance(value, list) or len(value) > MAX_LAYERS:
            raise LayeredSceneError('projection_groups must be an array within the layer limit')
        by_id = {layer['layer_id']: index for index, layer in enumerate(self.layers)}
        grouped: set[int] = set()
        groups: dict[int, int] = {}
        for group_index, raw in enumerate(value):
            label = f'projection_groups[{group_index}]'
            if not isinstance(raw, Mapping) or set(raw) != {'layer_ids', 'mode'}:
                raise LayeredSceneError(f'{label} must declare only layer_ids and mode')
            if raw.get('mode') != 'source_over_before_projection':
                raise LayeredSceneError(f'{label}.mode must be source_over_before_projection')
            layer_ids = raw.get('layer_ids')
            if (not isinstance(layer_ids, list) or len(layer_ids) != 2
                    or any(not isinstance(layer_id, str) for layer_id in layer_ids)
                    or layer_ids[0] == layer_ids[1]):
                raise LayeredSceneError(f'{label}.layer_ids must name exactly two distinct layers')
            if any(layer_id not in by_id for layer_id in layer_ids):
                raise LayeredSceneError(f'{label}.layer_ids must reference existing layers')
            indices = [by_id[layer_id] for layer_id in layer_ids]
            if indices[1] != indices[0] + 1:
                raise LayeredSceneError(f'{label}.layer_ids must be contiguous in authored back-to-front order')
            if any(index in grouped for index in indices):
                raise LayeredSceneError(f'{label} cannot overlap another projection group')
            back, front = (self.layers[index] for index in indices)
            if back['kind'] != 'character' or front['kind'] != 'character':
                raise LayeredSceneError(f'{label} may group only character raster layers')
            if back['depth'] != front['depth']:
                raise LayeredSceneError(f'{label} layers must have equal camera depth')
            if back['_source_bounds'] != front['_source_bounds']:
                raise LayeredSceneError(f'{label} layers must use the same source/world bounds')
            if any(state.get('_raster_asset') is None
                   for layer in (back, front) for state in layer['_pose_states']):
                raise LayeredSceneError(f'{label} requires every character pose state to use a pinned raster asset')
            grouped.update(indices)
            groups[indices[0]] = indices[1] + 1
        return groups

    def _require_channel(
        self,
        channel_id: Any,
        label: str,
        unit: str,
        target_kinds: Sequence[str],
        interpolations: Sequence[str],
        binding_id: Any,
    ) -> None:
        if not isinstance(channel_id, str) or channel_id not in self._channel_contracts:
            raise LayeredSceneError(f'{label} references missing motion channel {channel_id!r}')
        channel = self._channel_contracts[channel_id]
        if channel.value_unit != unit:
            raise LayeredSceneError(f'{label} channel {channel_id!r} must use {unit}')
        if channel.target.target_kind not in target_kinds:
            raise LayeredSceneError(
                f"{label} channel {channel_id!r} must use target kind {', '.join(target_kinds)}"
            )
        if channel.target.binding_id != binding_id:
            raise LayeredSceneError(
                f"{label} channel {channel_id!r} is bound to {channel.target.binding_id!r}, "
                f"expected {binding_id!r}"
            )
        if channel.interpolation not in interpolations:
            raise LayeredSceneError(
                f"{label} channel {channel_id!r} interpolation must be one of {', '.join(interpolations)}"
            )

    def _parse_states(self, value: Any, label: str) -> tuple[dict[str, Any], ...]:
        if not isinstance(value, list) or not value:
            raise LayeredSceneError(f'{label} must be a non-empty array')
        if len(value) > MAX_STATES:
            raise LayeredSceneError(f'{label} exceeds the {MAX_STATES}-state diagnostic limit')
        states: list[dict[str, Any]] = []
        names: set[str] = set()
        indices: set[int] = set()
        for index, raw in enumerate(value):
            if not isinstance(raw, Mapping):
                raise LayeredSceneError(f'{label}[{index}] must be an object')
            state_id = raw.get('state_id')
            state_index = raw.get('index')
            if not isinstance(state_id, str) or not state_id or state_id in names:
                raise LayeredSceneError(f'{label}[{index}].state_id must be unique and non-empty')
            if isinstance(state_index, bool) or not isinstance(state_index, int) or state_index < 0 or state_index in indices:
                raise LayeredSceneError(f'{label}[{index}].index must be a unique non-negative integer')
            names.add(state_id)
            indices.add(state_index)
            state = {
                'state_id': state_id,
                'index': state_index,
                '_shapes': _validate_shapes(raw.get('shapes', []), f'{label}[{index}].shapes'),
            }
            if raw.get('raster_asset') is not None:
                state['_raster_asset'] = self._load_raster_asset(
                    raw.get('raster_asset'), f'{label}[{index}].raster_asset'
                )
            states.append(state)
        return tuple(states)

    def _load_raster_asset(self, value: Any, label: str) -> dict[str, Any]:
        if self._asset_root is None:
            raise LayeredSceneError(f'{label} requires an explicit caller-declared asset_root')
        if not isinstance(value, Mapping):
            raise LayeredSceneError(f'{label} must declare path, sha256, and bounds_local_px')
        asset_path = value.get('path')
        if not isinstance(asset_path, str) or not asset_path or '\x00' in asset_path:
            raise LayeredSceneError(f'{label}.path must be a relative file inside asset_root')
        posix_path = PurePosixPath(asset_path.replace('\\', '/'))
        windows_path = PureWindowsPath(asset_path)
        if (posix_path.is_absolute() or windows_path.is_absolute() or windows_path.drive
                or any(part == '..' for part in posix_path.parts)):
            raise LayeredSceneError(f'{label}.path must stay inside the caller-declared asset_root')
        expected_digest = value.get('sha256')
        if not isinstance(expected_digest, str) or len(expected_digest) != 64 or any(
            character not in '0123456789abcdefABCDEF' for character in expected_digest
        ):
            raise LayeredSceneError(f'{label}.sha256 must be a 64-character hexadecimal SHA-256')
        bounds = _rect(value.get('bounds_local_px'), f'{label}.bounds_local_px')
        normalized_path = Path(*posix_path.parts)
        try:
            resolved_path = (self._asset_root / normalized_path).resolve(strict=True)
            resolved_path.relative_to(self._asset_root)
        except (OSError, ValueError) as exc:
            raise LayeredSceneError(f'{label}.path cannot resolve inside asset_root: {exc}') from exc
        if not resolved_path.is_file():
            raise LayeredSceneError(f'{label}.path must resolve to a regular file')
        cache_key = (str(resolved_path), expected_digest.lower())
        cached = self._raster_cache.get(cache_key)
        if cached is not None:
            return {**cached, '_bounds_local': bounds}
        try:
            if resolved_path.stat().st_size > MAX_RASTER_ASSET_BYTES:
                raise LayeredSceneError(f'{label} exceeds the {MAX_RASTER_ASSET_BYTES}-byte raster asset limit')
            with resolved_path.open('rb') as source:
                payload = source.read(MAX_RASTER_ASSET_BYTES + 1)
        except OSError as exc:
            raise LayeredSceneError(f'{label} cannot be read: {exc}') from exc
        if len(payload) > MAX_RASTER_ASSET_BYTES:
            raise LayeredSceneError(f'{label} exceeds the {MAX_RASTER_ASSET_BYTES}-byte raster asset limit')
        actual_digest = hashlib.sha256(payload).hexdigest()
        if not hmac.compare_digest(actual_digest, expected_digest.lower()):
            raise LayeredSceneError(f'{label} SHA-256 does not match its pinned digest')
        try:
            with Image.open(BytesIO(payload)) as encoded:
                if encoded.format != 'PNG':
                    raise LayeredSceneError(f'{label} must be a PNG raster asset')
                image_width, image_height = encoded.size
                if (image_width < 1 or image_height < 1 or image_width > 4096 or image_height > 4096
                        or image_width * image_height > MAX_SOURCE_PIXELS):
                    raise LayeredSceneError(
                        f'{label} dimensions exceed the 4096-side or {MAX_SOURCE_PIXELS}-pixel raster asset limit'
                    )
                asset_pixels = image_width * image_height
                asset_decoded_bytes = asset_pixels * 4
                if (self._raster_cache_pixels + asset_pixels > MAX_SCENE_RASTER_ASSET_PIXELS
                        or self._raster_cache_decoded_bytes + asset_decoded_bytes
                        > MAX_SCENE_RASTER_ASSET_DECODED_BYTES):
                    raise LayeredSceneError(
                        f'{label} exceeds the scene-wide decoded raster cache budget '
                        f'({MAX_SCENE_RASTER_ASSET_PIXELS} pixels / '
                        f'{MAX_SCENE_RASTER_ASSET_DECODED_BYTES} bytes)'
                    )
                if 'A' not in encoded.getbands() and 'transparency' not in encoded.info:
                    raise LayeredSceneError(f'{label} must have an alpha channel or PNG transparency')
                encoded.verify()
            with Image.open(BytesIO(payload)) as decoded:
                decoded.load()
                rgba = decoded.convert('RGBA')
                alpha_min, alpha_max = rgba.getchannel('A').getextrema()
                if alpha_min == 255 or alpha_max == 0:
                    raise LayeredSceneError(f'{label} alpha must contain both transparent and visible pixels')
                rgba.load()
        except LayeredSceneError:
            raise
        except (Image.DecompressionBombError, OSError, SyntaxError, ValueError) as exc:
            raise LayeredSceneError(f'{label} is not a valid bounded PNG raster asset: {exc}') from exc
        cached = {
            '_image': rgba.copy(),
            '_sha256': actual_digest,
            '_resolved_path': resolved_path,
        }
        self._raster_cache[cache_key] = cached
        self._raster_cache_pixels += asset_pixels
        self._raster_cache_decoded_bytes += asset_decoded_bytes
        return {**cached, '_bounds_local': bounds}

    def _parse_camera(self, value: Any) -> tuple[dict[str, Any], ...]:
        if not isinstance(value, Mapping):
            raise LayeredSceneError('camera must declare zoom_limits and keyframes')
        zoom_limits = _pair(value.get('zoom_limits'), 'camera.zoom_limits', ordered=True)
        if zoom_limits[0] <= 0:
            raise LayeredSceneError('camera.zoom_limits must be positive')
        self._zoom_limits = zoom_limits
        keyframes = value.get('keyframes')
        if not isinstance(keyframes, list) or not keyframes:
            raise LayeredSceneError('camera.keyframes must be a non-empty array')
        parsed: list[dict[str, Any]] = []
        previous = -1
        duration = self.timeline.clock.duration_frames
        for index, raw in enumerate(keyframes):
            if not isinstance(raw, Mapping):
                raise LayeredSceneError(f'camera.keyframes[{index}] must be an object')
            frame = raw.get('frame')
            if isinstance(frame, bool) or not isinstance(frame, int) or not previous < frame < duration:
                raise LayeredSceneError(f'camera.keyframes[{index}].frame must be strictly increasing and in range')
            zoom = _finite(raw.get('zoom'), f'camera.keyframes[{index}].zoom')
            if not zoom_limits[0] <= zoom <= zoom_limits[1]:
                raise LayeredSceneError(f'camera keyframe zoom {zoom:g} falls outside authored limits {zoom_limits}')
            look = _pair(raw.get('look_px', [self.width / 2, self.height / 2]),
                         f'camera.keyframes[{index}].look_px')
            at = _pair(raw.get('at_px', look), f'camera.keyframes[{index}].at_px')
            yaw = _finite(raw.get('yaw_deg', 0), f'camera.keyframes[{index}].yaw_deg')
            pitch = _finite(raw.get('pitch_deg', 0), f'camera.keyframes[{index}].pitch_deg')
            ease = raw.get('ease', 'smoothstep')
            if ease not in {'linear', 'smoothstep'}:
                raise LayeredSceneError(f'camera.keyframes[{index}].ease must be linear or smoothstep')
            parsed.append({'frame': frame, 'zoom': zoom, 'look_px': look, 'at_px': at,
                           'yaw_deg': yaw, 'pitch_deg': pitch, 'ease': ease})
            previous = frame
        for layer in self.layers:
            for key in parsed:
                plane_zoom = 1.0 + (key['zoom'] - 1.0) * layer['depth']
                if plane_zoom <= 0:
                    raise LayeredSceneError(
                        f"layer {layer['layer_id']!r} has nonpositive projected zoom at frame {key['frame']}"
                    )
        return tuple(parsed)

    def _camera_at(self, frame: Fraction) -> CameraState:
        center = (self.width / 2, self.height / 2)
        keys = self.camera
        if frame < keys[0]['frame']:
            return CameraState(1.0, center, center)
        if frame >= keys[-1]['frame']:
            key = keys[-1]
            return CameraState(key['zoom'], key['look_px'], key['at_px'], key['yaw_deg'], key['pitch_deg'])
        for left, right in zip(keys, keys[1:]):
            if left['frame'] <= frame <= right['frame']:
                amount = float((frame - left['frame']) / (right['frame'] - left['frame']))
                t = _ease(right['ease'], amount)

                def mix(a: float, b: float) -> float:
                    return a + (b - a) * t

                return CameraState(
                    mix(left['zoom'], right['zoom']),
                    (mix(left['look_px'][0], right['look_px'][0]), mix(left['look_px'][1], right['look_px'][1])),
                    (mix(left['at_px'][0], right['at_px'][0]), mix(left['at_px'][1], right['at_px'][1])),
                    mix(left['yaw_deg'], right['yaw_deg']),
                    mix(left['pitch_deg'], right['pitch_deg']),
                )
        return CameraState(1.0, center, center)

    def _plane_camera(self, camera: CameraState, depth: float) -> CameraState:
        if depth == 1.0:
            return camera
        lx, ly = camera.look_px
        ax, ay = camera.at_px
        plane_zoom = 1.0 + (camera.zoom - 1.0) * depth
        if plane_zoom <= 0:
            raise LayeredSceneError('projected plane zoom must stay positive')
        return CameraState(
            plane_zoom,
            camera.look_px,
            (lx + (ax - lx) * depth, ly + (ay - ly) * depth),
            camera.yaw_deg,
            camera.pitch_deg,
        )

    def _validate_view(self, camera: CameraState) -> None:
        if not self.yaw_limits[0] <= camera.yaw_deg <= self.yaw_limits[1]:
            raise LayeredSceneError(
                f'camera yaw {camera.yaw_deg:g} deg is outside authored view envelope '
                f'{self.yaw_limits}; add a reviewed view or stay inside the envelope'
            )
        if not self.pitch_limits[0] <= camera.pitch_deg <= self.pitch_limits[1]:
            raise LayeredSceneError(
                f'camera pitch {camera.pitch_deg:g} deg is outside authored view envelope '
                f'{self.pitch_limits}; add a reviewed view or stay inside the envelope'
            )

    def _anchor(self, layer: Mapping[str, Any], sample: MotionSample) -> tuple[float, float]:
        channels = layer['_anchor_channels']
        x_channel, y_channel = channels.get('x'), channels.get('y')
        if x_channel is None and y_channel is None:
            return layer['_anchor_px']
        if x_channel is None or y_channel is None:
            raise LayeredSceneError(f"layer {layer['layer_id']!r} needs both x and y anchor channels")
        x = _channel_value(sample, x_channel, f"layer {layer['layer_id']} anchor x")
        y = _channel_value(sample, y_channel, f"layer {layer['layer_id']} anchor y")
        if not 0 <= x <= 1 or not 0 <= y <= 1:
            raise LayeredSceneError(f"layer {layer['layer_id']!r} normalized anchor must be within 0..1")
        return x * self.width, y * self.height

    @staticmethod
    def _state_for(layer: Mapping[str, Any], sample: MotionSample, field: str, states_field: str) -> str:
        channel_id = layer[field]
        selected = _channel_value(sample, channel_id, f"layer {layer['layer_id']} {field}")
        rounded = round(selected)
        if not math.isclose(selected, rounded, abs_tol=1e-9):
            raise LayeredSceneError(f"layer {layer['layer_id']!r} {field} must select a whole authored index")
        for state in layer[states_field]:
            if state['index'] == rounded:
                return state['state_id']
        raise LayeredSceneError(f"layer {layer['layer_id']!r} {field} index {rounded} has no authored state")

    def evaluate(self, frame: int | Fraction) -> LayeredFrameState:
        try:
            sample = self.timeline.evaluate(frame)
        except MotionContractError as exc:
            raise LayeredSceneError(str(exc)) from exc
        camera = self._camera_at(sample.frame)
        self._validate_view(camera)
        selected: dict[str, dict[str, str]] = {}
        anchors: dict[str, tuple[float, float]] = {}
        for layer in self.layers:
            if layer['kind'] == 'character':
                selected[layer['layer_id']] = {
                    'pose': self._state_for(layer, sample, 'pose_channel', '_pose_states'),
                    'expression': self._state_for(
                        layer, sample, 'expression_channel', '_expression_states'
                    ),
                }
            if layer['kind'] in {'character', 'prop'}:
                anchors[layer['layer_id']] = self._anchor(layer, sample)
            if layer['kind'] == 'character':
                self._validate_disocclusion(layer, camera, anchors[layer['layer_id']], sample)
            if layer['role'] == 'background':
                self._validate_background_coverage(layer, camera)
        planar_pose = None
        if self.planar_rig is not None:
            rig_layer = next(layer for layer in self.layers if layer['layer_id'] == self.planar_rig.layer_id)
            scale_channel = rig_layer.get('scale_channel')
            scale = (_channel_value(sample, scale_channel, 'planar rig scale')
                     if scale_channel else 1.0)
            try:
                planar_pose = self.planar_rig.evaluate(
                    frame=sample.frame, anchor=anchors[rig_layer['layer_id']], scale=scale,
                    flip=-1 if rig_layer.get('flip_x') is True else 1,
                )
            except PlanarRigError as exc:
                raise LayeredSceneError(f'planar rig evaluation: {exc}') from exc
        return LayeredFrameState(
            scene_id=self.scene_id,
            frame=sample.frame,
            time_seconds=sample.time_seconds,
            events=tuple(event.event_id for event in sample.events),
            contacts=tuple(contact.contact_id for contact in sample.contacts),
            camera=camera,
            selected_states=selected,
            anchors_px=anchors,
            layer_order=tuple(layer['layer_id'] for layer in self.layers),
            diagnostic_status='review_only_diagnostic',
            planar_pose=planar_pose,
        )

    def _validate_disocclusion(
        self,
        layer: Mapping[str, Any],
        camera: CameraState,
        anchor: tuple[float, float],
        sample: MotionSample,
    ) -> None:
        depth = layer['depth']
        if depth == 1.0:
            return
        layered_camera = self._plane_camera(camera, depth)
        left, top, right, bottom = layer['_silhouette_bounds']
        scale_channel = layer.get('scale_channel')
        scale = _channel_value(sample, scale_channel, f"layer {layer['layer_id']} scale") if scale_channel else 1.0
        if not 0 < scale <= 16:
            raise LayeredSceneError(f"layer {layer['layer_id']!r} scale must be in 0..16")
        points = (
            (anchor[0] + left * scale, anchor[1] + top * scale),
            (anchor[0] + right * scale, anchor[1] + top * scale),
            (anchor[0] + right * scale, anchor[1] + bottom * scale),
            (anchor[0] + left * scale, anchor[1] + bottom * scale),
        )
        maximum = 0.0
        for point in points:
            base = _project(camera, point)
            layered = _project(layered_camera, point)
            maximum = max(maximum, math.hypot(layered[0] - base[0], layered[1] - base[1]))
        budget = layer['_disocclusion_budget']
        if maximum > budget + 1e-9:
            raise LayeredSceneError(
                f"layer {layer['layer_id']!r} camera exposes {maximum:.2f}px, exceeds its authored "
                f"disocclusion budget of {budget:.2f}px; widen the painted overlap or reduce the move"
            )

    def _validate_background_coverage(self, layer: Mapping[str, Any], camera: CameraState) -> None:
        plane_camera = self._plane_camera(camera, layer['depth'])
        left, top, right, bottom = layer['_painted_bounds']
        for screen in ((0.0, 0.0), (self.width, 0.0), (self.width, self.height), (0.0, self.height)):
            source = _unproject(plane_camera, screen)
            if source[0] < left or source[0] > right or source[1] < top or source[1] > bottom:
                raise LayeredSceneError(
                    f"background layer {layer['layer_id']!r} camera view exposes unpainted area at "
                    f"{source}; enlarge painted_bounds_px or reduce the camera move"
                )

    def render(self, frame: int | Fraction, *, supersample: int = 2) -> LayeredRender:
        output, state = self._render_rgba_frame(frame, supersample=supersample)
        return LayeredRender(output.convert('RGB'), state)

    def _render_rgba_frame(self, frame: int | Fraction, *, supersample: int = 2) -> tuple[Image.Image, LayeredFrameState]:
        if isinstance(supersample, bool) or not isinstance(supersample, int) or not 1 <= supersample <= 4:
            raise LayeredSceneError('supersample must be an integer in 1..4')
        if self.width * self.height * supersample * supersample > MAX_RASTER_PIXELS:
            raise LayeredSceneError('supersampled canvas exceeds the diagnostic raster limit')
        state = self.evaluate(frame)
        sample = self.timeline.evaluate(state.frame)
        output = Image.new('RGBA', (self.width, self.height), _color(self.document.get('clear_color', '#00000000'), 'clear_color'))
        selected_by_id = state.selected_states
        anchor_by_id = state.anchors_px
        if not self._projection_groups_by_start:
            for layer in self.layers:
                components = self._layer_components(layer, selected_by_id.get(layer['layer_id']))
                world_image = self._raster_layer(layer, components, anchor_by_id.get(layer['layer_id'], layer['_anchor_px']),
                                                 sample, supersample,
                                                 state.planar_pose if self.planar_rig is not None
                                                 and layer['layer_id'] == self.planar_rig.layer_id else None)
                plane = self._plane_camera(state.camera, layer['depth'])
                projected = _project_layer(world_image, layer['_source_bounds'], plane, self.width, self.height, supersample)
                output.alpha_composite(projected)
        else:
            index = 0
            while index < len(self.layers):
                group_end = self._projection_groups_by_start.get(index)
                if group_end is None:
                    layer = self.layers[index]
                    components = self._layer_components(layer, selected_by_id.get(layer['layer_id']))
                    world_image = self._raster_layer(
                        layer, components, anchor_by_id.get(layer['layer_id'], layer['_anchor_px']), sample, supersample,
                        state.planar_pose if self.planar_rig is not None
                        and layer['layer_id'] == self.planar_rig.layer_id else None,
                    )
                    plane = self._plane_camera(state.camera, layer['depth'])
                    projected = _project_layer(
                        world_image, layer['_source_bounds'], plane, self.width, self.height, supersample,
                    )
                    output.alpha_composite(projected)
                    index += 1
                    continue

                group = self.layers[index:group_end]
                world_image = None
                for layer in group:
                    components = self._layer_components(layer, selected_by_id.get(layer['layer_id']))
                    layer_image = self._raster_layer(
                        layer, components, anchor_by_id.get(layer['layer_id'], layer['_anchor_px']), sample, supersample,
                        state.planar_pose if self.planar_rig is not None
                        and layer['layer_id'] == self.planar_rig.layer_id else None,
                    )
                    if world_image is None:
                        world_image = layer_image
                    else:
                        world_image.alpha_composite(layer_image)
                assert world_image is not None
                plane = self._plane_camera(state.camera, group[0]['depth'])
                projected = _project_layer(
                    world_image, group[0]['_source_bounds'], plane, self.width, self.height, supersample,
                )
                output.alpha_composite(projected)
                index = group_end
        return output, state

    def _layer_shapes(
        self, layer: Mapping[str, Any], selected: Mapping[str, str] | None
    ) -> tuple[dict[str, Any], ...]:
        base, pose_shapes, _, expression_shapes, _ = self._layer_components(layer, selected)
        return tuple(base + pose_shapes + expression_shapes)

    def _layer_components(
        self, layer: Mapping[str, Any], selected: Mapping[str, str] | None
    ) -> tuple[
        tuple[dict[str, Any], ...],
        tuple[dict[str, Any], ...],
        Mapping[str, Any] | None,
        tuple[dict[str, Any], ...],
        Mapping[str, Any] | None,
    ]:
        if layer['kind'] == 'character' and selected:
            pose = next(state for state in layer['_pose_states'] if state['state_id'] == selected['pose'])
            expression = next(
                state for state in layer['_expression_states'] if state['state_id'] == selected['expression']
            )
            return (
                tuple(layer['_shapes']),
                tuple(pose['_shapes']),
                pose.get('_raster_asset'),
                tuple(expression['_shapes']),
                expression.get('_raster_asset'),
            )
        return tuple(layer['_shapes']), (), None, (), None

    def _raster_layer(
        self,
        layer: Mapping[str, Any],
        components: tuple[
            tuple[Mapping[str, Any], ...],
            tuple[Mapping[str, Any], ...],
            Mapping[str, Any] | None,
            tuple[Mapping[str, Any], ...],
            Mapping[str, Any] | None,
        ],
        anchor: tuple[float, float],
        sample: MotionSample,
        ss: int,
        planar_pose: PlanarPose | None = None,
    ) -> Image.Image:
        left, top, right, bottom = layer['_source_bounds']
        width = max(1, math.ceil((right - left) * ss))
        height = max(1, math.ceil((bottom - top) * ss))
        if width * height > MAX_RASTER_PIXELS:
            raise LayeredSceneError(f"layer {layer['layer_id']!r} exceeds the supersampled raster limit")
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        scale_channel = layer.get('scale_channel')
        scale = _channel_value(sample, scale_channel, f"layer {layer['layer_id']} scale") if scale_channel else 1.0
        if not 0 < scale <= 16:
            raise LayeredSceneError(f"layer {layer['layer_id']!r} scale must be in 0..16")
        flip = -1.0 if layer.get('flip_x') is True else 1.0

        def point(local: tuple[float, float]) -> tuple[float, float]:
            return ((anchor[0] + flip * local[0] * scale - left) * ss,
                    (anchor[1] + local[1] * scale - top) * ss)

        base_shapes, pose_shapes, pose_raster, expression_shapes, expression_raster = components

        def paint(shapes: Sequence[Mapping[str, Any]]) -> None:
            for shape in shapes:
                width_px = max(1, round(shape.get('_stroke_width', 1) * scale * ss))
                fill = shape.get('_fill')
                stroke = shape.get('_stroke')
                if shape['kind'] in {'rect', 'ellipse'}:
                    bounds = shape['_bounds']
                    corners = (point((bounds[0], bounds[1])), point((bounds[2], bounds[3])))
                    box = (corners[0][0], corners[0][1], corners[1][0], corners[1][1])
                    if box[0] > box[2]:
                        box = (box[2], box[1], box[0], box[3])
                    if shape['kind'] == 'rect':
                        radius = round(shape['_radius'] * scale * ss)
                        if radius:
                            draw.rounded_rectangle(box, radius=radius, fill=fill, outline=stroke, width=width_px)
                        else:
                            draw.rectangle(box, fill=fill, outline=stroke, width=width_px)
                    else:
                        draw.ellipse(box, fill=fill, outline=stroke, width=width_px)
                elif shape['kind'] == 'polygon':
                    points = [point(item) for item in shape['_points']]
                    draw.polygon(points, fill=fill)
                    if stroke:
                        draw.line(points + [points[0]], fill=stroke, width=width_px, joint='curve')
                else:
                    draw.line([point(item) for item in shape['_points']], fill=stroke or fill,
                              width=width_px, joint='curve')

        def composite_raster(asset: Mapping[str, Any] | None) -> None:
            if asset is None:
                return
            raster = asset['_image']
            bounds = asset['_bounds_local']
            if flip < 0:
                raster = raster.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            raster_width = max(1, round((bounds[2] - bounds[0]) * scale * ss))
            raster_height = max(1, round((bounds[3] - bounds[1]) * scale * ss))
            if raster_width * raster_height > MAX_RASTER_PIXELS:
                raise LayeredSceneError(
                    f"layer {layer['layer_id']!r} projected raster art exceeds the "
                    f'{MAX_RASTER_PIXELS}-pixel allocation limit'
                )
            if raster.size != (raster_width, raster_height):
                raster = raster.resize((raster_width, raster_height), Image.Resampling.LANCZOS)
            world_left = anchor[0] + min(flip * bounds[0], flip * bounds[2]) * scale
            world_top = anchor[1] + bounds[1] * scale
            dest_x = round((world_left - left) * ss)
            dest_y = round((world_top - top) * ss)
            clip_left = max(0, dest_x)
            clip_top = max(0, dest_y)
            clip_right = min(image.width, dest_x + raster.width)
            clip_bottom = min(image.height, dest_y + raster.height)
            if clip_left >= clip_right or clip_top >= clip_bottom:
                return
            clipped = raster.crop((
                clip_left - dest_x,
                clip_top - dest_y,
                clip_right - dest_x,
                clip_bottom - dest_y,
            ))
            image.alpha_composite(clipped, (clip_left, clip_top))

        paint(base_shapes)
        paint(pose_shapes)
        composite_raster(pose_raster)
        paint(expression_shapes)
        composite_raster(expression_raster)
        if planar_pose is not None:
            chain = [point(planar_pose.root_local_px), point(planar_pose.hinge_local_px),
                     point(planar_pose.end_local_px)]
            draw.line(chain, fill=(12, 22, 30, 255), width=max(1, round(13 * ss)), joint='curve')
            draw.line(chain, fill=(58, 224, 226, 255), width=max(1, round(6 * ss)), joint='curve')
            for joint in chain:
                radius = 5 * ss
                draw.ellipse((joint[0] - radius, joint[1] - radius,
                              joint[0] + radius, joint[1] + radius),
                             fill=(255, 225, 92, 255), outline=(12, 22, 30, 255), width=max(1, ss))
            target = planar_pose.requested_endpoint_canvas_px
            target_on_layer = ((target[0] - left) * ss, (target[1] - top) * ss)
            marker_radius = 9 * ss
            draw.ellipse((target_on_layer[0] - marker_radius, target_on_layer[1] - marker_radius,
                          target_on_layer[0] + marker_radius, target_on_layer[1] + marker_radius),
                         outline=(238, 91, 226, 255), width=max(1, 2 * ss))
        return image


def _project(camera: CameraState, point: tuple[float, float]) -> tuple[float, float]:
    # The caller supplies the per-plane state using the existing player law:
    # screen = at + zoom * (point - look).
    return (camera.at_px[0] + camera.zoom * (point[0] - camera.look_px[0]),
            camera.at_px[1] + camera.zoom * (point[1] - camera.look_px[1]))


def _unproject(camera: CameraState, screen: tuple[float, float]) -> tuple[float, float]:
    return (
        camera.look_px[0] + (screen[0] - camera.at_px[0]) / camera.zoom,
        camera.look_px[1] + (screen[1] - camera.at_px[1]) / camera.zoom,
    )


def _project_layer(
    source: Image.Image,
    source_bounds: tuple[float, float, float, float],
    camera: CameraState,
    width: int,
    height: int,
    ss: int,
) -> Image.Image:
    left, top, _, _ = source_bounds
    output_size = (width * ss, height * ss)
    inverse = (
        1.0 / camera.zoom, 0.0,
        ss * (camera.look_px[0] - left - camera.at_px[0] / camera.zoom),
        0.0, 1.0 / camera.zoom,
        ss * (camera.look_px[1] - top - camera.at_px[1] / camera.zoom),
    )
    moved = source.transform(output_size, Image.Transform.AFFINE, inverse,
                             resample=Image.Resampling.BICUBIC)
    return moved.resize((width, height), Image.Resampling.LANCZOS)


def render_contact_sheet(
    scene_path: str | Path,
    output_path: str | Path,
    frames: Sequence[int | Fraction],
    *,
    columns: int = 3,
    asset_root: str | Path | None = None,
) -> tuple[Path, Path]:
    """Render a labeled contact sheet and hash receipt into a review-only folder."""
    scene = LayeredScene.load(scene_path, asset_root=asset_root)
    if not frames or len(frames) > 12 or not 1 <= columns <= 6:
        raise LayeredSceneError('contact sheet needs 1..12 frames and 1..6 columns')
    renders = [scene.render(frame) for frame in frames]
    tile_w, tile_h, label_h = scene.width, scene.height, 36
    rows = math.ceil(len(renders) / columns)
    try:
        font = ImageFont.truetype('arial.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    measure = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    banner_lines: list[str] = []
    for word in DIAGNOSTIC_LABEL.split():
        candidate = f'{banner_lines[-1]} {word}' if banner_lines else word
        if banner_lines and measure.textlength(candidate, font=font) > columns * tile_w - 24:
            banner_lines.append(word)
        elif banner_lines:
            banner_lines[-1] = candidate
        else:
            banner_lines.append(word)
    banner_h = max(44, len(banner_lines) * 24 + 12)
    sheet_size = (columns * tile_w, banner_h + rows * (tile_h + label_h))
    if sheet_size[0] * sheet_size[1] > MAX_SHEET_PIXELS:
        raise LayeredSceneError('contact sheet exceeds the diagnostic image limit')
    sheet = Image.new('RGB', sheet_size, (16, 18, 24))
    draw = ImageDraw.Draw(sheet)
    for line_number, line in enumerate(banner_lines):
        draw.text((12, 8 + line_number * 24), line, font=font, fill=(255, 208, 77))
    for index, rendered in enumerate(renders):
        x, y = (index % columns) * tile_w, banner_h + (index // columns) * (tile_h + label_h)
        sheet.paste(rendered.image, (x, y))
        label = f"frame {rendered.state.frame} | contacts: {len(rendered.state.contacts)}"
        draw.text((x + 8, y + tile_h + 4), label, font=font, fill=(235, 239, 246))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, format='PNG', optimize=True)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    receipt = {
        'schema_version': 'authored_layer_preview_receipt.v1',
        'scene_id': scene.scene_id,
        'review_state': 'review_only',
        'render_eligible': False,
        'diagnostic_only': True,
        'diagnostic_label': DIAGNOSTIC_LABEL,
        'frames': [str(rendered.state.frame) for rendered in renders],
        'frame_states': [
            {
                'frame': str(rendered.state.frame),
                'events': list(rendered.state.events),
                'contacts': list(rendered.state.contacts),
                'selected_states': rendered.state.selected_states,
            }
            for rendered in renders
        ],
        'contact_sheet': destination.name,
        'sha256': digest,
        'canvas_px': list(sheet.size),
        'notes': [
            'Generic authored diagnostic primitives; not a finished character design or approved art.',
            'Depth ordering and the declared view/disocclusion limits are exercised; no hidden 3D is inferred.',
            'Contact labels are synthetic timing evidence from the shared rational scene clock.',
            'Inline authored vectors are T7a diagnostic input; T3 staged-asset integration remains future work.',
            'A contact label does not certify visible grounding or impact physics.',
        ],
    }
    receipt_path = destination.with_suffix('.receipt.json')
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return destination, receipt_path


def _main() -> None:
    parser = argparse.ArgumentParser(description='Render a review-only authored-layer contact sheet.')
    parser.add_argument('scene', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--frames', default='0,27,35,50,58,85')
    parser.add_argument('--columns', type=int, default=3)
    parser.add_argument('--asset-root', type=Path,
                        help='caller-declared trusted directory for relative, SHA-256-pinned PNG pose/expression assets')
    args = parser.parse_args()
    frames = [Fraction(item.strip()) for item in args.frames.split(',') if item.strip()]
    image, receipt = render_contact_sheet(
        args.scene, args.output, frames, columns=args.columns, asset_root=args.asset_root
    )
    print(json.dumps({'contact_sheet': str(image), 'receipt': str(receipt)}, indent=2))


if __name__ == '__main__':
    _main()
