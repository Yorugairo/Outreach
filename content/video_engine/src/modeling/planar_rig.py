"""Review-only, shared-clock planar contact diagnostic for an authored layer.

The sidecar owns geometry and a fixed canvas target, not timing. Its contact
interval comes exclusively from MotionTimeline. It is neither a skinning system
nor a claim that diagnostic vector art is finished character animation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .motion import MotionContact


Vec2 = tuple[float, float]
MAX_COORD = 16_384.0
_EPS = 1.0e-7
_FIELDS = frozenset({
    'schema_version', 'review_state', 'render_eligible', 'diagnostic_only',
    'scene_id', 'layer_id', 'binding_id', 'contact_id', 'semantic_effector',
    'target_binding_id', 'target_surface_id', 'joint_unit', 'target_unit',
    'rest_joints_local_px', 'bend_sign', 'target_canvas_px',
})


class PlanarRigError(ValueError):
    """Invalid or incompatible review-only planar rig sidecar."""


def _pair(value: Any, label: str) -> Vec2:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise PlanarRigError(f'{label} must be a two-number array')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in value):
        raise PlanarRigError(f'{label} must contain finite numbers')
    pair = (float(value[0]), float(value[1]))
    if any(not math.isfinite(v) or abs(v) > MAX_COORD for v in pair):
        raise PlanarRigError(f'{label} must contain finite bounded coordinates')
    return pair


def _distance(a: Vec2, b: Vec2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _world(local: Vec2, anchor: Vec2, scale: float, flip: int) -> Vec2:
    return (anchor[0] + flip * local[0] * scale, anchor[1] + local[1] * scale)


@dataclass(frozen=True)
class PlanarPose:
    contact_id: str
    semantic_effector: str
    mode: str
    root_local_px: Vec2
    hinge_local_px: Vec2
    end_local_px: Vec2
    root_canvas_px: Vec2
    hinge_canvas_px: Vec2
    end_canvas_px: Vec2
    requested_endpoint_canvas_px: Vec2
    solved_endpoint_canvas_px: Vec2
    residual_px: float
    reachable: bool | None
    upper_length_local_px: float
    lower_length_local_px: float
    upper_length_canvas_px: float
    lower_length_canvas_px: float


@dataclass(frozen=True)
class PlanarRig:
    scene_id: str
    layer_id: str
    binding_id: str
    contact: MotionContact
    root: Vec2
    hinge: Vec2
    end: Vec2
    bend_sign: int
    target_canvas_px: Vec2
    upper_length: float
    lower_length: float

    @classmethod
    def from_document(
        cls,
        value: Mapping[str, Any],
        *,
        scene_id: str,
        layers: Sequence[Mapping[str, Any]],
        contacts: Sequence[MotionContact],
        canvas_px: Vec2,
    ) -> PlanarRig:
        if not isinstance(value, Mapping) or set(value) != _FIELDS:
            raise PlanarRigError('planar rig sidecar must contain exactly the v1 fields; no clock or events')
        if value['schema_version'] != 'planar_rig.v1':
            raise PlanarRigError('schema_version must be planar_rig.v1')
        if (value['review_state'] != 'review_only' or value['render_eligible'] is not False
                or value['diagnostic_only'] is not True):
            raise PlanarRigError('planar rig must remain review_only, diagnostic_only and non-render-eligible')
        if value['scene_id'] != scene_id:
            raise PlanarRigError('planar rig scene_id must match the shared scene')
        for key in ('layer_id', 'binding_id', 'contact_id', 'semantic_effector',
                    'target_binding_id', 'target_surface_id'):
            if not isinstance(value[key], str) or not value[key]:
                raise PlanarRigError(f'{key} must be a non-empty string')
        if value['joint_unit'] != 'layer_local_px' or value['target_unit'] != 'canvas_px':
            raise PlanarRigError('planar rig requires layer_local_px joints and canvas_px target')
        matches = [layer for layer in layers if layer['layer_id'] == value['layer_id']]
        if len(matches) != 1 or matches[0]['kind'] != 'character':
            raise PlanarRigError('layer_id must identify one character layer')
        layer = matches[0]
        if layer['binding_id'] != value['binding_id']:
            raise PlanarRigError('binding_id must match the character layer')
        contact_matches = [item for item in contacts if item.contact_id == value['contact_id']]
        if len(contact_matches) != 1:
            raise PlanarRigError('contact_id must identify one shared MotionContact')
        contact = contact_matches[0]
        if (contact.actor_binding_id != value['binding_id']
                or contact.semantic_effector != value['semantic_effector']
                or contact.target_binding_id != value['target_binding_id']
                or contact.target_surface_id != value['target_surface_id']
                or contact.target_semantic_joint is not None):
            raise PlanarRigError('sidecar binding, effector or target semantics mismatch shared MotionContact')
        joints = value['rest_joints_local_px']
        if not isinstance(joints, Mapping) or set(joints) != {'root', 'hinge', 'end'}:
            raise PlanarRigError('rest_joints_local_px must declare root, hinge and end')
        root, hinge, end = (_pair(joints[name], f'rest_joints_local_px.{name}')
                            for name in ('root', 'hinge', 'end'))
        silhouette = layer['_silhouette_bounds']
        for name, joint in (('root', root), ('hinge', hinge), ('end', end)):
            if not (silhouette[0] <= joint[0] <= silhouette[2]
                    and silhouette[1] <= joint[1] <= silhouette[3]):
                raise PlanarRigError(f'{name} must remain inside character silhouette bounds')
        upper, lower = _distance(root, hinge), _distance(hinge, end)
        if not 1.0e-3 <= upper <= 4096 or not 1.0e-3 <= lower <= 4096:
            raise PlanarRigError('rest joint lengths must be positive and bounded')
        sign = value['bend_sign']
        if isinstance(sign, bool) or not isinstance(sign, int) or sign not in (-1, 1):
            raise PlanarRigError('bend_sign must be -1 or 1')
        cross = ((end[0] - root[0]) * (hinge[1] - root[1])
                 - (end[1] - root[1]) * (hinge[0] - root[0]))
        if abs(cross) <= 1.0e-6 or cross * sign <= 0:
            raise PlanarRigError('bend_sign must agree with a non-collinear bent rest chain')
        target = _pair(value['target_canvas_px'], 'target_canvas_px')
        if not (0 <= target[0] <= canvas_px[0] and 0 <= target[1] <= canvas_px[1]):
            raise PlanarRigError('target_canvas_px must lie inside the canvas')
        return cls(scene_id, value['layer_id'], value['binding_id'], contact,
                   root, hinge, end, sign, target, upper, lower)

    def evaluate(self, *, frame: Any, anchor: Vec2, scale: float, flip: int) -> PlanarPose:
        if not math.isfinite(scale) or not 1.0e-6 <= scale <= 16 or flip not in (-1, 1):
            raise PlanarRigError('layer transform must have finite scale in 1e-6..16 and explicit flip')
        root, hinge, end = self.root, self.hinge, self.end
        active = self.contact.active_at(frame)
        reachable: bool | None = None
        if active:
            # Invert the existing layer transform. The contact target is fixed in
            # pre-camera canvas space; a mirrored layer reverses its visual bend.
            target = ((self.target_canvas_px[0] - anchor[0]) / (flip * scale),
                      (self.target_canvas_px[1] - anchor[1]) / scale)
            dx, dy = target[0] - root[0], target[1] - root[1]
            distance = math.hypot(dx, dy)
            direction = (dx / distance, dy / distance) if distance > _EPS else (1.0, 0.0)
            reach_min = abs(self.upper_length - self.lower_length)
            reach_max = self.upper_length + self.lower_length
            safe_min = max(reach_min + _EPS, _EPS)
            safe_max = max(safe_min, reach_max - _EPS)
            solved_distance = min(max(distance, safe_min), safe_max)
            end = (root[0] + direction[0] * solved_distance,
                   root[1] + direction[1] * solved_distance)
            cosine = ((self.upper_length**2 + solved_distance**2 - self.lower_length**2)
                      / (2 * self.upper_length * solved_distance))
            beta = math.acos(min(1.0, max(-1.0, cosine)))
            angle = math.atan2(direction[1], direction[0]) + self.bend_sign * beta
            hinge = (root[0] + self.upper_length * math.cos(angle),
                     root[1] + self.upper_length * math.sin(angle))
            # Compute the endpoint from the second bone, retaining its exact
            # authored length even at reach boundaries.
            forearm = (end[0] - hinge[0], end[1] - hinge[1])
            forearm_length = math.hypot(*forearm)
            end = (hinge[0] + self.lower_length * forearm[0] / forearm_length,
                   hinge[1] + self.lower_length * forearm[1] / forearm_length)
            reachable = abs(distance - solved_distance) <= 1.0e-6
        root_world = _world(root, anchor, scale, flip)
        hinge_world = _world(hinge, anchor, scale, flip)
        end_world = _world(end, anchor, scale, flip)
        return PlanarPose(
            contact_id=self.contact.contact_id,
            semantic_effector=self.contact.semantic_effector,
            mode='ik_contact' if active else 'fk_rest',
            root_local_px=root, hinge_local_px=hinge, end_local_px=end,
            root_canvas_px=root_world, hinge_canvas_px=hinge_world, end_canvas_px=end_world,
            requested_endpoint_canvas_px=self.target_canvas_px,
            solved_endpoint_canvas_px=end_world,
            residual_px=_distance(self.target_canvas_px, end_world),
            reachable=reachable,
            upper_length_local_px=self.upper_length,
            lower_length_local_px=self.lower_length,
            upper_length_canvas_px=self.upper_length * scale,
            lower_length_canvas_px=self.lower_length * scale,
        )
