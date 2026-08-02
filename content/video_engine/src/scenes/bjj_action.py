"""Deterministic articulated BJJ action scene.

The technique renderer deliberately keeps the cast as a small, reviewed 2-D
vector library.  The geometry is represented by named joints and segments,
not by a generated whole-pose image.  That gives storyboard and QC code a
stable contract to inspect while still letting Manim animate the same
objects when the optional renderer is installed.

The scene is intentionally independent of the scene registry.  The registry
is shared integration-owned state and is wired by the parent slice (T4).
Importing this module remains safe when Manim is unavailable: ``base.py``
supplies the tiny fallback primitives used by the direct contract tests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .base import Arrow, Circle, Dot, FadeIn, Line, Text, ThemedScene, VGroup, color_value

try:  # pragma: no cover - exercised only when the optional renderer is installed
    from manim import Polygon as _ManimPolygon  # type: ignore
    from manim import Transform as _ManimTransform  # type: ignore
except ImportError:  # pragma: no cover - direct contract tests use the fallback path
    _ManimPolygon = None
    _ManimTransform = None


Point = tuple[float, float, float]


class _FallbackFilledMass(VGroup):
    """Metadata-first stand-in for an opaque anatomical cutout.

    The video engine intentionally keeps Manim optional.  Contract tests still
    need to see that a part is a filled mass (rather than a line skeleton), so
    this tiny object carries the same geometry/style fields as the render-time
    capsule helper.
    """

    def __init__(
        self,
        start: Point,
        end: Point,
        radius: float,
        color: Any,
        *,
        panel: str | None = None,
    ) -> None:
        super().__init__()
        self.start_point = start
        self.end_point = end
        self.radius = float(radius)
        self.fill_color = color
        self.fill_opacity = 1.0
        self.stroke_width = 8.0
        self.outline_color = "#F4F7FA"
        self.shape_type = "filled_capsule"
        self.panel = panel


def _capsule_mass(
    start: Point,
    end: Point,
    radius: float,
    color: Any,
    *,
    panel: str | None = None,
    outline_color: Any = "#F4F7FA",
    outline_width: float = 8.0,
    taper: float = 0.82,
) -> Any:
    """Build a tapered filled cutout mass with stable geometry metadata.

    A real Manim render gets a tapered polygon plus fill-only end caps.  The
    caps deliberately have no independent stroke: outlining every segment end
    produces visible joint rings and makes a filled character read like the
    retired skeletal rig.  Hands, feet, the head, and the belt provide the
    terminal outline shapes instead.

    The fallback object deliberately exposes the same fields so
    state/ownership contracts remain testable without importing Manim.
    """

    if _ManimPolygon is None:
        return _FallbackFilledMass(start, end, radius, color, panel=panel)

    import math

    dx = float(end[0]) - float(start[0])
    dy = float(end[1]) - float(start[1])
    length = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    start_radius = float(radius)
    end_radius = start_radius * max(0.55, min(float(taper), 1.0))
    start_nx, start_ny = -dy / length * start_radius, dx / length * start_radius
    end_nx, end_ny = -dy / length * end_radius, dx / length * end_radius
    corners = (
        (start[0] + start_nx, start[1] + start_ny, start[2]),
        (end[0] + end_nx, end[1] + end_ny, end[2]),
        (end[0] - end_nx, end[1] - end_ny, end[2]),
        (start[0] - start_nx, start[1] - start_ny, start[2]),
    )
    polygon = _ManimPolygon(
        *corners,
        color=color,
        fill_color=color,
        fill_opacity=1.0,
        stroke_color=outline_color,
        stroke_width=outline_width,
    )
    cap_a = Circle(
        radius=start_radius,
        color=color,
        fill_color=color,
        fill_opacity=1.0,
        stroke_width=0.0,
    )
    cap_b = Circle(
        radius=end_radius,
        color=color,
        fill_color=color,
        fill_opacity=1.0,
        stroke_width=0.0,
    )
    _safe_move_to(cap_a, start)
    _safe_move_to(cap_b, end)
    mass = VGroup(polygon, cap_a, cap_b)
    try:
        mass.start_point = start
        mass.end_point = end
        mass.radius = float(radius)
        mass.fill_color = color
        mass.fill_opacity = 1.0
        mass.stroke_width = float(outline_width)
        mass.outline_color = outline_color
        mass.shape_type = "filled_capsule"
        mass.panel = panel
        mass.taper = float(taper)
    except Exception:
        pass
    return mass


def _point(value: Sequence[float] | Point) -> Point:
    """Normalize a point to the three-value tuple used by the scene API."""

    values = tuple(float(item) for item in value)
    if len(values) == 2:
        return values[0], values[1], 0.0
    if len(values) != 3:
        raise ValueError(f"joint position must contain two or three values: {value!r}")
    return values  # type: ignore[return-value]


def _string_tuple(value: Any) -> tuple[str, ...]:
    """Normalize a scalar/list storyboard field without splitting strings."""

    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence):
        normalized: list[str] = []
        for item in value:
            if isinstance(item, Mapping):
                item = item.get("id") or item.get("anchor_id") or item.get("name")
            if item is not None:
                normalized.append(str(item))
        return tuple(normalized)
    return (str(value),)


def _safe_set_z_index(mobject: Any, value: int) -> None:
    """Set Manim's z-index while retaining a readable fallback attribute."""

    try:
        mobject.set_z_index(int(value))
    except (AttributeError, TypeError, RuntimeError):
        pass
    # Fallback mobjects accept arbitrary attributes; the explicit attribute is
    # useful to tests and to render adapters that inspect the cast without
    # importing Manim internals.
    try:
        mobject.z_index = int(value)
    except Exception:
        pass


def _safe_set_color(mobject: Any, value: Any) -> None:
    try:
        mobject.set_color(value)
    except (AttributeError, TypeError, RuntimeError):
        pass


def _safe_set_opacity(mobject: Any, value: float) -> None:
    try:
        mobject.set_opacity(float(value))
    except (AttributeError, TypeError, RuntimeError):
        # The fallback does not render; retaining the value is still useful
        # for inspection.
        try:
            mobject.opacity = float(value)
        except Exception:
            pass


def _safe_move_to(mobject: Any, position: Point) -> None:
    try:
        mobject.move_to(position)
    except (AttributeError, TypeError, RuntimeError):
        pass


def _move_filled_mass(mobject: Any, start: Point, end: Point) -> None:
    """Update a capsule's reviewed endpoints without changing its identity."""

    try:
        mobject.start_point = start
        mobject.end_point = end
    except Exception:
        pass
    if _ManimPolygon is not None and hasattr(mobject, "become"):
        target = _capsule_mass(
            start,
            end,
            float(getattr(mobject, "radius", 0.18)),
            getattr(mobject, "fill_color", "#F4F7FA"),
            panel=getattr(mobject, "panel", None),
            outline_color=getattr(mobject, "outline_color", "#F4F7FA"),
            outline_width=float(getattr(mobject, "stroke_width", 8.0)),
            taper=float(getattr(mobject, "taper", 0.82)),
        )
        try:
            mobject.become(target)
        except (AttributeError, TypeError, RuntimeError):
            pass


@dataclass(frozen=True, slots=True)
class JointSpec:
    """A named anchor in a practitioner's articulated skeleton."""

    name: str
    owner: str
    role: str
    z_index: int

    @property
    def id(self) -> str:
        return self.name

    @property
    def z(self) -> int:
        return self.z_index

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "owner": self.owner,
            "role": self.role,
            "z_index": self.z_index,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


# A short, descriptive alias is convenient for callers that call these
# records "joints" rather than "joint specs".
Joint = JointSpec


@dataclass(frozen=True, slots=True)
class BodyPartSpec:
    """A filled vector layer owned by exactly one cast member.

    ``start_joint``/``end_joint`` identify the reviewed endpoints of a mass.
    A ``circle`` part (the head) uses only ``start_joint``; both are retained
    in the contract so state updates can be deterministic for every layer.
    """

    name: str
    owner: str
    kind: str
    z_index: int
    start_joint: str
    end_joint: str | None = None
    color_role: str = "gi"
    stroke_width: float = 0.16
    radius: float = 0.26
    # V3 renders opaque cutout masses.  ``kind`` remains a string for
    # backwards-compatible manifests, while these explicit style fields let
    # QC distinguish a filled body from the legacy line rig.
    fill_opacity: float = 1.0
    shape: str = "filled_capsule"
    panel_role: str | None = None

    @property
    def id(self) -> str:
        return f"{self.owner}:{self.name}"

    @property
    def z(self) -> int:
        return self.z_index

    @property
    def body_owner(self) -> str:
        return self.owner

    @property
    def is_filled(self) -> bool:
        return self.fill_opacity > 0.0 and self.shape.startswith("filled_")

    @property
    def geometry(self) -> str:
        return self.shape

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "owner": self.owner,
            "kind": self.kind,
            "z_index": self.z_index,
            "start_joint": self.start_joint,
            "end_joint": self.end_joint,
            "color_role": self.color_role,
            "stroke_width": self.stroke_width,
            "radius": self.radius,
            "fill_opacity": self.fill_opacity,
            "shape": self.shape,
            "panel_role": self.panel_role,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


BodyPart = BodyPartSpec


@dataclass(frozen=True, slots=True)
class ContactAnchor:
    """A reviewed contact between two named joints.

    Contact IDs are stable across shots.  They are the bridge between the
    action scene, shot planning, overlays, and deterministic sound cues.
    """

    anchor_id: str
    owner: str
    joint: str
    target_owner: str
    target_joint: str
    kind: str
    z_index: int = 80

    @property
    def id(self) -> str:
        return self.anchor_id

    @property
    def z(self) -> int:
        return self.z_index

    @property
    def source(self) -> str:
        return f"{self.owner}:{self.joint}"

    @property
    def target(self) -> str:
        return f"{self.target_owner}:{self.target_joint}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.anchor_id,
            "owner": self.owner,
            "joint": self.joint,
            "target_owner": self.target_owner,
            "target_joint": self.target_joint,
            "kind": self.kind,
            "z_index": self.z_index,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(frozen=True, slots=True)
class ActionPhase:
    """One causal step in an action recipe.

    The four phase names are intentionally fixed.  A phase is not merely a
    timer: it moves from one named state to another and identifies the
    contacts, overlays, and sound cues that explain that change.
    """

    name: str
    state_from: str
    action: str
    state_to: str
    motion_path: str
    duration_s: float
    contact_anchors: tuple[str, ...] = ()
    camera_focus: str | None = None
    overlays: tuple[str, ...] = ()
    sound_cues: tuple[str, ...] = ()

    @property
    def phase(self) -> str:
        return self.name

    @property
    def path(self) -> str:
        return self.motion_path

    @property
    def contacts(self) -> tuple[str, ...]:
        return self.contact_anchors

    @property
    def motion(self) -> dict[str, Any]:
        return {"path": self.motion_path, "phases": list(PHASE_NAMES)}

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.name,
            "phase_name": self.name,
            "name": self.name,
            "state_from": self.state_from,
            "action": self.action,
            "state_to": self.state_to,
            "motion_path": self.motion_path,
            "duration_s": self.duration_s,
            "contact_anchors": list(self.contact_anchors),
            "camera_focus": self.camera_focus,
            "overlays": list(self.overlays),
            "sound_cues": list(self.sound_cues),
            # This mirrors the storyboard recipe shape used by T2/T4 while
            # retaining the compact fields above for direct scene tests.
            "motion": self.motion,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(slots=True)
class CastMember:
    """Persistent practitioner identity plus its layered vector parts."""

    cast_id: str
    variant_id: str
    gi_color: str
    belt_color: str
    skin_color: str = "#F4C7A1"
    z_base: int = 10
    joints: dict[str, JointSpec] = field(default_factory=dict)
    body_parts: dict[str, BodyPartSpec] = field(default_factory=dict)
    joint_positions: dict[str, Point] = field(default_factory=dict)
    part_mobjects: dict[str, Any] = field(default_factory=dict)
    joint_mobjects: dict[str, Any] = field(default_factory=dict)
    group: Any | None = None

    @property
    def id(self) -> str:
        return self.cast_id

    @property
    def variant(self) -> str:
        """Short alias used by storyboard cast dictionaries."""

        return self.variant_id

    @property
    def ownership(self) -> dict[str, str]:
        return {name: self.cast_id for name in self.body_parts}

    @property
    def z_order(self) -> dict[str, int]:
        return {name: part.z_index for name, part in self.body_parts.items()}

    @property
    def gi_panels(self) -> dict[str, BodyPartSpec]:
        return {
            name: part
            for name, part in self.body_parts.items()
            if part.panel_role in {"gi_panel", "sleeve", "pants", "belt"}
        }

    @property
    def colors(self) -> dict[str, str]:
        return {
            "gi": self.gi_color,
            "belt": self.belt_color,
            "skin": self.skin_color,
        }

    def position(self, joint: str, state: str | None = None) -> Point:
        # ``state`` is accepted for symmetry with BJJCast.position.  A member
        # stores the currently active state; state-specific positions are
        # resolved by BJJCast before this method is called.
        del state
        try:
            return self.joint_positions[joint]
        except KeyError as exc:
            raise KeyError(f"unknown {self.cast_id} joint: {joint}") from exc

    def to_dict(self) -> dict[str, Any]:
        return {
            "cast_id": self.cast_id,
            "variant_id": self.variant_id,
            "gi_color": self.gi_color,
            "belt_color": self.belt_color,
            "skin_color": self.skin_color,
            "z_base": self.z_base,
            "joints": {name: value.to_dict() for name, value in self.joints.items()},
            "body_parts": {
                name: value.to_dict() for name, value in self.body_parts.items()
            },
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(slots=True)
class BJJCast:
    """Two persistent, opposing practitioners and their reviewed contacts."""

    members: dict[str, CastMember]
    contact_anchors: dict[str, ContactAnchor]
    states: dict[str, dict[str, dict[str, Point]]]
    current_state: str
    group: Any | None = None

    @property
    def cast_ids(self) -> tuple[str, ...]:
        return tuple(self.members)

    @property
    def attacker(self) -> CastMember:
        return self.members["attacker"]

    @property
    def defender(self) -> CastMember:
        return self.members["defender"]

    @property
    def body_parts(self) -> dict[str, BodyPartSpec]:
        return {
            f"{member_id}:{name}": part
            for member_id, member in self.members.items()
            for name, part in member.body_parts.items()
        }

    @property
    def joints(self) -> dict[str, JointSpec]:
        return {
            f"{member_id}:{name}": joint
            for member_id, member in self.members.items()
            for name, joint in member.joints.items()
        }

    @property
    def joints_by_owner(self) -> dict[str, dict[str, JointSpec]]:
        return {member_id: dict(member.joints) for member_id, member in self.members.items()}

    @property
    def body_ownership(self) -> dict[str, str]:
        return {
            f"{member_id}:{name}": member_id
            for member_id, member in self.members.items()
            for name in member.body_parts
        }

    @property
    def joint_ownership(self) -> dict[str, str]:
        return {
            f"{member_id}:{name}": member_id
            for member_id, member in self.members.items()
            for name in member.joints
        }

    @property
    def ownership(self) -> dict[str, str]:
        return self.body_ownership

    @property
    def z_order(self) -> dict[str, int]:
        return {
            f"{member_id}:{name}": part.z_index
            for member_id, member in self.members.items()
            for name, part in member.body_parts.items()
        }

    @property
    def gi_panels(self) -> dict[str, BodyPartSpec]:
        return {
            f"{member_id}:{name}": part
            for member_id, member in self.members.items()
            for name, part in member.gi_panels.items()
        }

    @property
    def cast_z_order(self) -> dict[str, int]:
        return {member_id: member.z_base for member_id, member in self.members.items()}

    @property
    def layers(self) -> tuple[BodyPartSpec, ...]:
        """All vector layers in deterministic back-to-front order."""

        return tuple(sorted(self.body_parts.values(), key=lambda part: (part.z_index, part.id)))

    @property
    def filled_layers(self) -> tuple[BodyPartSpec, ...]:
        """Opaque V3 masses/panels; joint metadata is kept separately."""

        return tuple(
            part for part in self.layers
            if part.kind in {"mass", "panel", "capsule", "circle"}
            and float(part.fill_opacity) > 0.0
        )

    @property
    def joint_metadata(self) -> dict[str, dict[str, Any]]:
        return {key: value.to_dict() for key, value in sorted(self.joints.items())}

    @property
    def layer_order(self) -> tuple[str, ...]:
        return tuple(part.id for part in self.layers)

    @property
    def joint_positions(self) -> dict[str, Point]:
        return {
            f"{member_id}:{name}": position
            for member_id, member in self.members.items()
            for name, position in member.joint_positions.items()
        }

    @property
    def contact_anchor_positions(self) -> dict[str, Point]:
        return {
            name: self.anchor_position(name)
            for name in self.contact_anchors
        }

    def position(self, owner: str, joint: str, state: str | None = None) -> Point:
        state_id = STATE_ALIASES.get(state, state) if state else self.current_state
        try:
            return self.states[state_id][owner][joint]
        except KeyError as exc:
            raise KeyError(f"unknown cast position: {state_id}/{owner}/{joint}") from exc

    def anchor_position(self, anchor: str | ContactAnchor, state: str | None = None) -> Point:
        if isinstance(anchor, str):
            anchor = CONTACT_ANCHOR_ALIASES.get(anchor, anchor)
        item = self.contact_anchors[anchor] if isinstance(anchor, str) else anchor
        left = self.position(item.owner, item.joint, state)
        right = self.position(item.target_owner, item.target_joint, state)
        return tuple(round((a + b) / 2.0, 6) for a, b in zip(left, right))  # type: ignore[return-value]

    @property
    def state_ids(self) -> tuple[str, ...]:
        return tuple(self.states)

    def state_ids_list(self) -> list[str]:
        return list(self.state_ids)

    def __getitem__(self, key: str) -> Any:
        if key in self.members:
            return self.members[key]
        if key == "body_ownership":
            return self.body_ownership
        if key == "z_order":
            return self.z_order
        if key == "contact_anchors":
            return self.contact_anchors
        raise KeyError(key)

    def set_state(self, state: str) -> None:
        state = STATE_ALIASES.get(state, state)
        if state not in self.states:
            raise KeyError(f"unknown BJJ cast state: {state}")
        self.current_state = state
        for member_id, member in self.members.items():
            member.joint_positions = dict(self.states[state][member_id])

    def to_dict(self) -> dict[str, Any]:
        return {
            "members": {name: member.to_dict() for name, member in self.members.items()},
            "contact_anchors": {
                name: anchor.to_dict() for name, anchor in self.contact_anchors.items()
            },
            "states": {
                state: {
                    owner: {joint: list(position) for joint, position in joints.items()}
                    for owner, joints in owners.items()
                }
                for state, owners in self.states.items()
            },
            "current_state": self.current_state,
        }


CAST_ROOT = Path(__file__).resolve().parents[1] / "assets" / "cast"
CAST_MANIFEST_PATH = CAST_ROOT / "cast_manifest.json"

CAST_IDS: tuple[str, str] = ("attacker", "defender")
PHASE_NAMES: tuple[str, str, str, str] = (
    "anticipation",
    "action",
    "contact",
    "recovery",
)

JOINT_ROLES: dict[str, str] = {
    "head": "head",
    "neck": "spine",
    "shoulder_left": "shoulder",
    "shoulder_right": "shoulder",
    "elbow_left": "elbow",
    "elbow_right": "elbow",
    "wrist_left": "wrist",
    "wrist_right": "wrist",
    "hip_left": "hip",
    "hip_right": "hip",
    "knee_left": "knee",
    "knee_right": "knee",
    "ankle_left": "ankle",
    "ankle_right": "ankle",
}
JOINT_NAMES: tuple[str, ...] = tuple(JOINT_ROLES)


def _joints(owner: str, z_base: int) -> dict[str, JointSpec]:
    return {
        name: JointSpec(name, owner, role, z_base + 25)
        for name, role in JOINT_ROLES.items()
    }


def _body_parts(owner: str, z_base: int) -> dict[str, BodyPartSpec]:
    # Body parts are local names; BJJCast prefixes them with the persistent
    # cast id when exposing the aggregate ownership/z-order maps.
    return {
        # ``kind`` values are intentionally V3-specific.  The reviewed joints
        # remain the sole positional source of truth; these parts only define
        # how the silhouette is filled around those anchors.
        "head": BodyPartSpec(
            "head", owner, "circle", z_base + 35, "head", color_role="skin", radius=0.28,
            shape="filled_circle",
        ),
        "torso": BodyPartSpec(
            "torso", owner, "mass", z_base + 20, "neck", "hip_left",
            stroke_width=0.42, radius=0.44, shape="filled_torso", panel_role="gi_panel",
        ),
        "belt": BodyPartSpec(
            "belt", owner, "panel", z_base + 22, "hip_left", "hip_right",
            color_role="belt", stroke_width=0.20, radius=0.11, shape="filled_panel", panel_role="belt",
        ),
        "upper_arm_left": BodyPartSpec(
            "upper_arm_left", owner, "mass", z_base + 24, "shoulder_left", "elbow_left",
            stroke_width=0.24, radius=0.19, shape="filled_capsule", panel_role="sleeve",
        ),
        "forearm_left": BodyPartSpec(
            "forearm_left", owner, "mass", z_base + 25, "elbow_left", "wrist_left",
            stroke_width=0.22, radius=0.16, shape="filled_capsule", panel_role="sleeve",
        ),
        "upper_arm_right": BodyPartSpec(
            "upper_arm_right", owner, "mass", z_base + 24, "shoulder_right", "elbow_right",
            stroke_width=0.24, radius=0.19, shape="filled_capsule", panel_role="sleeve",
        ),
        "forearm_right": BodyPartSpec(
            "forearm_right", owner, "mass", z_base + 25, "elbow_right", "wrist_right",
            stroke_width=0.22, radius=0.16, shape="filled_capsule", panel_role="sleeve",
        ),
        "hand_left": BodyPartSpec(
            "hand_left", owner, "circle", z_base + 28, "wrist_left",
            color_role="skin", radius=0.11, shape="filled_circle",
        ),
        "hand_right": BodyPartSpec(
            "hand_right", owner, "circle", z_base + 28, "wrist_right",
            color_role="skin", radius=0.11, shape="filled_circle",
        ),
        "thigh_left": BodyPartSpec(
            "thigh_left", owner, "mass", z_base + 21, "hip_left", "knee_left",
            stroke_width=0.34, radius=0.27, shape="filled_capsule", panel_role="pants",
        ),
        "shin_left": BodyPartSpec(
            "shin_left", owner, "mass", z_base + 22, "knee_left", "ankle_left",
            stroke_width=0.27, radius=0.21, shape="filled_capsule", panel_role="pants",
        ),
        "thigh_right": BodyPartSpec(
            "thigh_right", owner, "mass", z_base + 21, "hip_right", "knee_right",
            stroke_width=0.34, radius=0.27, shape="filled_capsule", panel_role="pants",
        ),
        "shin_right": BodyPartSpec(
            "shin_right", owner, "mass", z_base + 22, "knee_right", "ankle_right",
            stroke_width=0.27, radius=0.21, shape="filled_capsule", panel_role="pants",
        ),
        "foot_left": BodyPartSpec(
            "foot_left", owner, "circle", z_base + 24, "ankle_left",
            radius=0.15, shape="filled_circle", panel_role="pants",
        ),
        "foot_right": BodyPartSpec(
            "foot_right", owner, "circle", z_base + 24, "ankle_right",
            radius=0.15, shape="filled_circle", panel_role="pants",
        ),
    }


# State geometry is intentionally plain tuples.  It can be reviewed in a
# diff, serialized in a shot plan, and consumed by fallback tests without
# importing Manim.  The positions are stylized teaching geometry, not an
# anatomical source of truth.
STATE_POSES: dict[str, dict[str, dict[str, Point]]] = {
    "closed_guard_posture_broken": {
        "attacker": {
            "head": (-2.45, -0.05, 0.0),
            "neck": (-2.22, -0.30, 0.0),
            "shoulder_left": (-2.60, -0.35, 0.0),
            "shoulder_right": (-1.90, -0.35, 0.0),
            "elbow_left": (-2.88, -0.72, 0.0),
            "elbow_right": (-1.62, -0.78, 0.0),
            "wrist_left": (-3.12, -0.90, 0.0),
            "wrist_right": (-1.42, -0.95, 0.0),
            "hip_left": (-1.95, -1.15, 0.0),
            "hip_right": (-1.28, -1.12, 0.0),
            "knee_left": (-0.95, -0.05, 0.0),
            "knee_right": (-0.72, 0.32, 0.0),
            "ankle_left": (0.05, -0.72, 0.0),
            "ankle_right": (0.18, 0.92, 0.0),
        },
        "defender": {
            "head": (1.65, 1.18, 0.0),
            "neck": (1.58, 0.88, 0.0),
            "shoulder_left": (1.15, 0.78, 0.0),
            "shoulder_right": (1.98, 0.78, 0.0),
            "elbow_left": (0.78, 0.24, 0.0),
            "elbow_right": (2.36, 0.20, 0.0),
            "wrist_left": (0.18, -0.02, 0.0),
            "wrist_right": (2.75, -0.05, 0.0),
            "hip_left": (1.23, -0.25, 0.0),
            "hip_right": (1.98, -0.28, 0.0),
            "knee_left": (2.32, -1.15, 0.0),
            "knee_right": (2.90, -0.96, 0.0),
            "ankle_left": (3.25, -1.95, 0.0),
            "ankle_right": (3.70, -1.58, 0.0),
        },
    },
    "wrist_control_hip_frame": {
        "attacker": {
            "head": (-2.20, -0.02, 0.0),
            "neck": (-1.97, -0.28, 0.0),
            "shoulder_left": (-2.30, -0.35, 0.0),
            "shoulder_right": (-1.55, -0.35, 0.0),
            "elbow_left": (-2.78, -0.68, 0.0),
            "elbow_right": (-1.28, -0.68, 0.0),
            "wrist_left": (-3.14, -0.85, 0.0),
            "wrist_right": (-0.96, -0.87, 0.0),
            "hip_left": (-1.68, -1.15, 0.0),
            "hip_right": (-0.98, -1.12, 0.0),
            "knee_left": (-0.22, -0.14, 0.0),
            "knee_right": (0.02, 0.70, 0.0),
            "ankle_left": (0.78, -0.65, 0.0),
            "ankle_right": (0.98, 1.18, 0.0),
        },
        "defender": {
            "head": (1.75, 1.05, 0.0),
            "neck": (1.65, 0.74, 0.0),
            "shoulder_left": (1.20, 0.64, 0.0),
            "shoulder_right": (2.08, 0.64, 0.0),
            "elbow_left": (0.54, 0.18, 0.0),
            "elbow_right": (2.22, 0.12, 0.0),
            "wrist_left": (-0.05, -0.08, 0.0),
            "wrist_right": (2.82, -0.13, 0.0),
            "hip_left": (1.22, -0.37, 0.0),
            "hip_right": (2.02, -0.35, 0.0),
            "knee_left": (2.46, -1.18, 0.0),
            "knee_right": (3.02, -1.04, 0.0),
            "ankle_left": (3.32, -1.97, 0.0),
            "ankle_right": (3.82, -1.68, 0.0),
        },
    },
    "hip_angle_and_leg_control": {
        "attacker": {
            "head": (-1.88, -0.05, 0.0),
            "neck": (-1.62, -0.32, 0.0),
            "shoulder_left": (-2.08, -0.42, 0.0),
            "shoulder_right": (-1.24, -0.42, 0.0),
            "elbow_left": (-2.54, -0.74, 0.0),
            "elbow_right": (-1.02, -0.78, 0.0),
            "wrist_left": (-2.92, -0.88, 0.0),
            "wrist_right": (-0.78, -0.92, 0.0),
            "hip_left": (-1.30, -1.03, 0.0),
            "hip_right": (-0.56, -1.02, 0.0),
            "knee_left": (0.32, 0.03, 0.0),
            "knee_right": (0.78, 0.76, 0.0),
            "ankle_left": (1.20, -0.76, 0.0),
            "ankle_right": (1.58, 1.12, 0.0),
        },
        "defender": {
            "head": (1.68, 0.90, 0.0),
            "neck": (1.57, 0.60, 0.0),
            "shoulder_left": (1.06, 0.52, 0.0),
            "shoulder_right": (2.02, 0.48, 0.0),
            "elbow_left": (0.28, 0.02, 0.0),
            "elbow_right": (2.25, -0.02, 0.0),
            "wrist_left": (-0.28, -0.16, 0.0),
            "wrist_right": (2.86, -0.22, 0.0),
            "hip_left": (1.13, -0.42, 0.0),
            "hip_right": (1.95, -0.44, 0.0),
            "knee_left": (2.48, -1.23, 0.0),
            "knee_right": (3.08, -1.16, 0.0),
            "ankle_left": (3.35, -2.00, 0.0),
            "ankle_right": (3.88, -1.78, 0.0),
        },
    },
    "armbar_extension_contact": {
        "attacker": {
            "head": (-1.72, -0.52, 0.0),
            "neck": (-1.45, -0.68, 0.0),
            "shoulder_left": (-1.95, -0.78, 0.0),
            "shoulder_right": (-0.98, -0.80, 0.0),
            "elbow_left": (-2.34, -1.02, 0.0),
            "elbow_right": (-0.63, -1.05, 0.0),
            "wrist_left": (-2.58, -1.16, 0.0),
            "wrist_right": (-0.28, -1.24, 0.0),
            "hip_left": (-1.08, -1.14, 0.0),
            "hip_right": (-0.34, -1.12, 0.0),
            "knee_left": (0.42, -0.10, 0.0),
            "knee_right": (0.88, 1.02, 0.0),
            "ankle_left": (1.34, -0.90, 0.0),
            "ankle_right": (1.86, 0.96, 0.0),
        },
        "defender": {
            "head": (1.44, 0.68, 0.0),
            "neck": (1.34, 0.38, 0.0),
            "shoulder_left": (0.83, 0.32, 0.0),
            "shoulder_right": (1.78, 0.25, 0.0),
            "elbow_left": (0.28, -0.08, 0.0),
            "elbow_right": (2.15, -0.14, 0.0),
            "wrist_left": (-0.33, -0.26, 0.0),
            "wrist_right": (2.75, -0.36, 0.0),
            "hip_left": (0.90, -0.58, 0.0),
            "hip_right": (1.68, -0.60, 0.0),
            "knee_left": (2.28, -1.36, 0.0),
            "knee_right": (2.92, -1.38, 0.0),
            "ankle_left": (3.24, -2.12, 0.0),
            "ankle_right": (3.82, -2.02, 0.0),
        },
    },
    "armbar_extension_held": {
        "attacker": {
            "head": (-1.66, -0.55, 0.0),
            "neck": (-1.39, -0.70, 0.0),
            "shoulder_left": (-1.90, -0.80, 0.0),
            "shoulder_right": (-0.94, -0.81, 0.0),
            "elbow_left": (-2.28, -1.05, 0.0),
            "elbow_right": (-0.58, -1.08, 0.0),
            "wrist_left": (-2.52, -1.20, 0.0),
            "wrist_right": (-0.20, -1.27, 0.0),
            "hip_left": (-1.02, -1.17, 0.0),
            "hip_right": (-0.28, -1.15, 0.0),
            "knee_left": (0.46, -0.08, 0.0),
            "knee_right": (0.92, 1.06, 0.0),
            "ankle_left": (1.38, -0.88, 0.0),
            "ankle_right": (1.90, 1.00, 0.0),
        },
        "defender": {
            "head": (1.40, 0.65, 0.0),
            "neck": (1.30, 0.35, 0.0),
            "shoulder_left": (0.80, 0.30, 0.0),
            "shoulder_right": (1.74, 0.22, 0.0),
            "elbow_left": (0.24, -0.10, 0.0),
            "elbow_right": (2.12, -0.16, 0.0),
            "wrist_left": (-0.37, -0.28, 0.0),
            "wrist_right": (2.72, -0.38, 0.0),
            "hip_left": (0.86, -0.61, 0.0),
            "hip_right": (1.64, -0.63, 0.0),
            "knee_left": (2.26, -1.39, 0.0),
            "knee_right": (2.90, -1.41, 0.0),
            "ankle_left": (3.22, -2.15, 0.0),
            "ankle_right": (3.80, -2.05, 0.0),
        },
    },
}


# A few legacy aliases make the state library easy to consume from existing
# pose names while keeping one canonical state for action validation.
STATE_ALIASES: dict[str, str] = {
    "reviewed_start_state": "closed_guard_posture_broken",
    "reviewed_end_state": "armbar_extension_held",
    "armbar_start": "closed_guard_posture_broken",
    "armbar_finish": "armbar_extension_held",
    "closed_guard": "closed_guard_posture_broken",
    "posture_broken": "closed_guard_posture_broken",
    "wrist_frame": "wrist_control_hip_frame",
    "hip_angle": "hip_angle_and_leg_control",
    "leg_control": "hip_angle_and_leg_control",
    "wrist_control": "wrist_control_hip_frame",
    "hip_frame": "wrist_control_hip_frame",
    "armbar_extension": "armbar_extension_held",
    "result": "armbar_extension_held",
    "result_hold": "armbar_extension_held",
}


CONTACT_ANCHOR_SPECS: tuple[ContactAnchor, ...] = (
    ContactAnchor("wrist_control", "attacker", "wrist_right", "defender", "wrist_left", "grip"),
    ContactAnchor("hip_fulcrum", "attacker", "hip_right", "defender", "elbow_right", "fulcrum"),
    ContactAnchor("elbow_load", "defender", "elbow_right", "attacker", "hip_right", "load"),
    ContactAnchor("knee_over_head", "attacker", "knee_right", "defender", "head", "frame"),
    ContactAnchor("leg_control", "attacker", "ankle_right", "defender", "shoulder_right", "control"),
    ContactAnchor("elbow_line", "defender", "elbow_right", "attacker", "hip_right", "extension"),
)

CONTACT_ANCHOR_ALIASES: dict[str, str] = {
    "attacker_wrist": "wrist_control",
    "defender_wrist": "wrist_control",
    "attacker_hip": "hip_fulcrum",
    "defender_elbow": "elbow_line",
    "attacker_knee": "knee_over_head",
}


ARM_BAR_ACTION_CHAIN: tuple[ActionPhase, ...] = (
    ActionPhase(
        "anticipation",
        "closed_guard_posture_broken",
        "two_on_one_wrist_control",
        "wrist_control_hip_frame",
        "linear",
        0.48,
        ("wrist_control",),
        "attacker_wrist",
        ("wrist_lock", "hip_frame_arrow"),
        ("movement",),
    ),
    ActionPhase(
        "action",
        "wrist_control_hip_frame",
        "hip_angle_and_leg_swing",
        "hip_angle_and_leg_control",
        "arc",
        0.68,
        ("hip_fulcrum", "elbow_load"),
        "attacker_hip",
        ("hip_pivot_arc",),
        ("movement",),
    ),
    ActionPhase(
        "contact",
        "hip_angle_and_leg_control",
        "leg_over_head_elbow_pin",
        "armbar_extension_contact",
        "pivot",
        0.48,
        ("knee_over_head", "leg_control", "elbow_line"),
        "defender_elbow",
        ("elbow_line", "knee_frame"),
        ("contact",),
    ),
    ActionPhase(
        "recovery",
        "armbar_extension_contact",
        "extend_and_settle",
        "armbar_extension_held",
        "compression",
        0.56,
        ("hip_fulcrum", "elbow_line"),
        "attacker_hip",
        ("force_arrow", "result_badge"),
        ("aftermath",),
    ),
)

# Names without spaces are retained as the public spelling expected by
# Python callers.  The variable with the descriptive name above is declared
# via globals below so the serialized contract can still use ``armbar``.
ARM_BAR_PHASES = ARM_BAR_ACTION_CHAIN
ARMBAR_ACTION_CHAIN = ARM_BAR_ACTION_CHAIN
ARMBAR_PHASES = ARM_BAR_ACTION_CHAIN
ACTION_PHASES = PHASE_NAMES
ACTION_PHASE_SPECS = ARM_BAR_ACTION_CHAIN


def _manifest_payload() -> dict[str, Any]:
    """Load cast metadata, falling back to the checked-in defaults."""

    try:
        payload = json.loads(CAST_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        payload = {}
    return payload if isinstance(payload, dict) else {}


def _variant(payload: Mapping[str, Any], variant_id: str, default: Mapping[str, Any]) -> dict[str, Any]:
    variants = payload.get("variants")
    if isinstance(variants, Mapping) and isinstance(variants.get(variant_id), Mapping):
        merged = dict(default)
        merged.update(dict(variants[variant_id]))
        return merged
    return dict(default)


def _build_member(cast_id: str, variant_id: str, config: Mapping[str, Any]) -> CastMember:
    z_base = int(config.get("z_base", 10))
    gi_color = str(config.get("gi_color", "#FFFFFF"))
    belt_color = str(config.get("belt_color", "#2563EB"))
    skin_color = str(config.get("skin_color", "#F4C7A1"))
    return CastMember(
        cast_id=cast_id,
        variant_id=variant_id,
        gi_color=gi_color,
        belt_color=belt_color,
        skin_color=skin_color,
        z_base=z_base,
        joints=_joints(cast_id, z_base),
        body_parts=_body_parts(cast_id, z_base),
    )


def build_bjj_cast(
    *,
    attacker_variant: str = "white_gi_blue_belt",
    defender_variant: str = "black_gi_purple_belt",
    initial_state: str = "closed_guard_posture_broken",
) -> BJJCast:
    """Build the persistent Armbar cast and validate its reviewed contract."""

    payload = _manifest_payload()
    defaults = {
        "white_gi_blue_belt": {
            "gi_color": "#F4F7FA",
            "belt_color": "#3B82F6",
            "skin_color": "#F4C7A1",
            "z_base": 20,
        },
        "black_gi_purple_belt": {
            "gi_color": "#151C24",
            "belt_color": "#8B5CF6",
            "skin_color": "#C68663",
            "z_base": 10,
        },
    }
    manifest_variants = payload.get("variants")
    known_variants = set(defaults)
    if isinstance(manifest_variants, Mapping):
        known_variants.update(str(value) for value in manifest_variants)
    for role, variant_id in (
        ("attacker", attacker_variant),
        ("defender", defender_variant),
    ):
        if variant_id not in known_variants:
            raise KeyError(f"unknown {role} cast variant: {variant_id}")
    attacker_config = _variant(payload, attacker_variant, defaults["white_gi_blue_belt"])
    defender_config = _variant(payload, defender_variant, defaults["black_gi_purple_belt"])
    members = {
        "attacker": _build_member("attacker", attacker_variant, attacker_config),
        "defender": _build_member("defender", defender_variant, defender_config),
    }
    states = {
        state: {
            owner: {joint: _point(position) for joint, position in joints.items()}
            for owner, joints in owner_states.items()
        }
        for state, owner_states in STATE_POSES.items()
    }
    canonical_state = STATE_ALIASES.get(initial_state, initial_state)
    if canonical_state not in states:
        raise KeyError(f"unknown BJJ cast state: {initial_state}")
    cast = BJJCast(
        members=members,
        contact_anchors={item.anchor_id: item for item in CONTACT_ANCHOR_SPECS},
        states=states,
        current_state=canonical_state,
    )
    cast.set_state(canonical_state)
    return cast


build_cast = build_bjj_cast
build_layered_cast = build_bjj_cast


def _safe_part_animation(mobject: Any, part: BodyPartSpec, joints: Mapping[str, Point]) -> Any | None:
    """Return a Manim animation for a body mass, or ``None`` on fallback."""

    animator = getattr(mobject, "animate", None)
    if animator is None:
        return None
    try:
        if part.kind == "circle":
            return animator.move_to(joints[part.start_joint])
        if part.end_joint is not None:
            if part.kind in {"mass", "panel", "capsule"} or part.shape.startswith("filled_"):
                start = joints[part.start_joint]
                end = joints[part.end_joint]
                if _ManimTransform is None:
                    return None
                target = _capsule_mass(
                    start,
                    end,
                    float(getattr(mobject, "radius", part.radius)),
                    getattr(mobject, "fill_color", "#F4F7FA"),
                    panel=getattr(mobject, "panel", part.panel_role),
                    outline_color=getattr(mobject, "outline_color", "#F4F7FA"),
                    outline_width=float(getattr(mobject, "stroke_width", 8.0)),
                )
                return _ManimTransform(mobject, target)
            return animator.put_start_and_end_on(
                joints[part.start_joint], joints[part.end_joint]
            )
    except (AttributeError, TypeError, RuntimeError):
        return None
    return None


class BJJActionScene(ThemedScene):
    """Render one deterministic, articulated Armbar action chain.

    The cast is constructed exactly once per scene section and remains in the
    scene throughout all four phases.  In Manim, filled masses move through
    the ``animate`` API; on the fallback path the same state metadata and
    phase timeline are updated while a marker animation keeps the
    entrance/timing contract testable.
    """

    recipe_version = "shot_recipe.v1"
    action_id = "armbar_from_guard"
    visual_type = "bjj_action"
    actions = tuple(phase.action for phase in ARM_BAR_ACTION_CHAIN)
    phase_contract_names = PHASE_NAMES

    def __init__(
        self,
        scene_spec: dict[str, Any] | None = None,
        layout: str = "landscape",
        audio_duration: float = 0.0,
        theme: dict[str, Any] | None = None,
        *,
        cast: BJJCast | None = None,
    ) -> None:
        super().__init__(scene_spec, layout, audio_duration, theme)
        self.cast = cast or build_bjj_cast(
            attacker_variant=self.cast_variants["attacker"],
            defender_variant=self.cast_variants["defender"],
            initial_state=self.initial_state,
        )
        self._apply_cast_style_overrides()
        # Private spelling retained for integrations that treat the scene as
        # a renderer object while the public ``cast`` remains the contract.
        self._cast = self.cast
        self._cast_group: Any | None = None
        self._ground: Any | None = None
        self._phase_markers: dict[str, Any] = {}
        self._shot_overlay: Any | None = None
        self._phase_history: list[dict[str, Any]] = []
        self._current_phase: str | None = None
        self._current_state = self.cast.current_state

    def _apply_cast_style_overrides(self) -> None:
        """Apply non-authoritative shot colors while retaining reviewed IDs."""

        value = self.scene_spec.get("cast") or self.parameters.get("cast") or {}
        if not isinstance(value, Mapping):
            return
        for role, member_id in (("attacker", "attacker"), ("defender", "defender")):
            candidate = value.get(role)
            if not isinstance(candidate, Mapping):
                continue
            member = self.cast.members[member_id]
            gi_color = candidate.get("gi_color") or candidate.get("color")
            belt_color = candidate.get("belt_color")
            skin_color = candidate.get("skin_color")
            if gi_color:
                member.gi_color = str(gi_color)
            if belt_color:
                member.belt_color = str(belt_color)
            if skin_color:
                member.skin_color = str(skin_color)

    @property
    def parameters(self) -> Mapping[str, Any]:
        value = self.scene_spec.get("parameters") or {}
        return value if isinstance(value, Mapping) else {}

    @property
    def cast_variants(self) -> dict[str, str]:
        value = self.scene_spec.get("cast") or self.parameters.get("cast") or {}
        if not isinstance(value, Mapping):
            value = {}

        def variant(role: str, fallback: str) -> str:
            candidate = value.get(role)
            if isinstance(candidate, Mapping):
                explicit = candidate.get("variant_id") or candidate.get("variant")
                if explicit:
                    return str(explicit)
                gi = candidate.get("gi")
                belt = candidate.get("belt")
                if gi and belt:
                    combined = f"{gi}_{belt}"
                    if combined in {"white_gi_blue_belt", "black_gi_purple_belt"}:
                        return combined
                    # Provenance objects may carry descriptive colour labels
                    # rather than a registered variant ID; retain the
                    # reviewed role default in that case.
                    return fallback
                candidate = candidate.get("id")
                if candidate in {"attacker", "defender"}:
                    return fallback
            return str(candidate or fallback)

        return {
            "attacker": variant("attacker", "white_gi_blue_belt"),
            "defender": variant("defender", "black_gi_purple_belt"),
        }

    @property
    def initial_state(self) -> str:
        value = (
            self.scene_spec.get("state_from")
            or self.parameters.get("state_from")
            or ARM_BAR_ACTION_CHAIN[0].state_from
        )
        return STATE_ALIASES.get(str(value), str(value))

    @property
    def requested_action(self) -> str:
        value = self.scene_spec.get("action") or self.parameters.get("action") or self.action_id
        return str(value)

    def _phase_specs(self) -> tuple[ActionPhase, ...]:
        raw = (
            self.scene_spec.get("phases")
            or self.scene_spec.get("action_chain")
            or self.scene_spec.get("action_recipe")
            or self.parameters.get("phases")
            or self.parameters.get("action_chain")
            or self.parameters.get("action_recipe")
        )
        if isinstance(raw, Mapping) and isinstance(raw.get("phases"), Sequence):
            raw = raw.get("phases")
        elif isinstance(raw, Mapping):
            # A shot plan may carry one recipe object while the articulated
            # scene still renders the complete reviewed Armbar chain.
            raw = None
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            phase_names = tuple(str(value) for value in raw)
            if phase_names == PHASE_NAMES:
                return ARM_BAR_ACTION_CHAIN
        if raw is None:
            return ARM_BAR_ACTION_CHAIN
        if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
            raise ValueError("BJJActionScene phases must be an array")
        phases: list[ActionPhase] = []
        for item in raw:
            if isinstance(item, ActionPhase):
                phase = item
            elif isinstance(item, Mapping):
                name = str(item.get("phase", item.get("name", "")))
                motion_value = item.get("motion")
                motion_path = (
                    motion_value.get("path", "linear")
                    if isinstance(motion_value, Mapping)
                    else (str(motion_value) if motion_value else "linear")
                )
                phase = ActionPhase(
                    name=name,
                    state_from=str(item.get("state_from", "")),
                    action=str(item.get("action", "")),
                    state_to=str(item.get("state_to", "")),
                    motion_path=str(item.get("motion_path", motion_path)),
                    duration_s=float(item.get("duration_s", item.get("duration", 0.1))),
                    contact_anchors=tuple(
                        CONTACT_ANCHOR_ALIASES.get(value, value)
                        for value in _string_tuple(
                            item.get("contact_anchors", item.get("contacts", ()))
                        )
                    ),
                    camera_focus=(str(item["camera_focus"]) if item.get("camera_focus") is not None else None),
                    overlays=_string_tuple(item.get("overlays", ())),
                    sound_cues=_string_tuple(item.get("sound_cues", ())),
                )
            else:
                raise ValueError("BJJActionScene phase entries must be objects")
            if phase.name not in PHASE_NAMES:
                raise ValueError(f"unknown BJJ action phase: {phase.name}")
            if not phase.state_from or not phase.state_to or not phase.action:
                raise ValueError(f"phase {phase.name} must define state_from/action/state_to")
            phase_state_from = STATE_ALIASES.get(phase.state_from, phase.state_from)
            phase_state_to = STATE_ALIASES.get(phase.state_to, phase.state_to)
            if phase_state_from not in STATE_POSES or phase_state_to not in STATE_POSES:
                raise KeyError(f"unknown BJJ action state in phase {phase.name}")
            # Anticipation, contact confirmation, and held-result shots may
            # intentionally preserve a reviewed state while changing camera,
            # overlays, or contact emphasis. State IDs must still resolve;
            # movement shots carry their actual state transition in the
            # action phase supplied by the reviewed recipe.
            unresolved_contacts = [
                contact
                for contact in phase.contact_anchors
                if contact not in self.contact_anchors
            ]
            if unresolved_contacts:
                raise KeyError(
                    f"unknown BJJ contact anchor(s) in phase {phase.name}: "
                    + ", ".join(unresolved_contacts)
                )
            phases.append(
                ActionPhase(
                    phase.name,
                    phase_state_from,
                    phase.action,
                    phase_state_to,
                    phase.motion_path,
                    max(0.001, phase.duration_s),
                    phase.contact_anchors,
                    phase.camera_focus,
                    phase.overlays,
                    phase.sound_cues,
                )
            )
        if tuple(phase.name for phase in phases) != PHASE_NAMES:
            raise ValueError("BJJActionScene requires anticipation/action/contact/recovery phases")
        return tuple(phases)

    @property
    def phases(self) -> tuple[ActionPhase, ...]:
        return self._phase_specs()

    @property
    def action_phases(self) -> tuple[ActionPhase, ...]:
        return self.phases

    @property
    def phase_names(self) -> tuple[str, ...]:
        return tuple(phase.name for phase in self.phases)

    @property
    def phase_ids(self) -> tuple[str, ...]:
        return self.phase_names

    @property
    def phase_sequence(self) -> tuple[ActionPhase, ...]:
        return self.phases

    @property
    def state_ids(self) -> tuple[str, ...]:
        return self.cast.state_ids

    @property
    def contact_anchor_ids(self) -> tuple[str, ...]:
        return tuple(self.contact_anchors)

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def current_phase(self) -> str | None:
        return self._current_phase

    @property
    def body_ownership(self) -> dict[str, str]:
        return self.cast.body_ownership

    @property
    def body_owners(self) -> dict[str, str]:
        return self.body_ownership

    @property
    def joint_ownership(self) -> dict[str, str]:
        return self.cast.joint_ownership

    @property
    def z_order(self) -> dict[str, int]:
        return self.cast.z_order

    @property
    def gi_panels(self) -> dict[str, BodyPartSpec]:
        return self.cast.gi_panels

    @property
    def cast_z_order(self) -> dict[str, int]:
        return self.cast.cast_z_order

    @property
    def state_positions(self) -> dict[str, dict[str, dict[str, Point]]]:
        return self.cast.states

    @property
    def contact_anchor_positions(self) -> dict[str, Point]:
        return self.cast.contact_anchor_positions

    def contact_anchor(self, name: str, state: str | None = None) -> Point:
        return self.cast.anchor_position(name, state)

    @property
    def joints(self) -> dict[str, JointSpec]:
        return self.cast.joints

    @property
    def body_parts(self) -> dict[str, BodyPartSpec]:
        return self.cast.body_parts

    @property
    def cast_parts(self) -> dict[str, BodyPartSpec]:
        return self.body_parts

    @property
    def joints_by_owner(self) -> dict[str, dict[str, JointSpec]]:
        return self.cast.joints_by_owner

    @property
    def joint_map(self) -> dict[str, JointSpec]:
        return self.joints

    @property
    def layers(self) -> tuple[BodyPartSpec, ...]:
        return self.cast.layers

    @property
    def filled_layers(self) -> tuple[BodyPartSpec, ...]:
        """V3 opaque anatomy layers, excluding the reviewed joint metadata."""

        return tuple(
            part for part in self.layers
            if part.kind in {"mass", "panel", "capsule", "circle"}
            and float(part.fill_opacity) > 0.0
        )

    @property
    def joint_metadata(self) -> dict[str, dict[str, Any]]:
        """Expose reviewed joints without drawing them as visible skeleton lines."""

        return {
            key: value.to_dict()
            for key, value in sorted(self.joints.items())
        }

    @property
    def contact_anchors(self) -> dict[str, ContactAnchor]:
        return self.cast.contact_anchors

    @property
    def phase_history(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(item) for item in self._phase_history)

    @property
    def phase_timeline(self) -> tuple[dict[str, Any], ...]:
        return self.phase_history

    @property
    def state_change_log(self) -> tuple[dict[str, Any], ...]:
        return self.phase_history

    @property
    def action_log(self) -> tuple[dict[str, Any], ...]:
        return self.phase_history

    @property
    def cast_group(self) -> Any | None:
        return self._cast_group

    def action_contract(self) -> dict[str, Any]:
        """Return the immutable-looking recipe consumed by planning/QC code."""

        phases = self.phases
        overlays = tuple(
            dict.fromkeys(overlay for phase in phases for overlay in phase.overlays)
        )
        sound_cues = tuple(
            dict.fromkeys(cue for phase in phases for cue in phase.sound_cues)
        )
        camera_focus = phases[0].camera_focus
        reference_value = (
            self.scene_spec.get("reference_refs")
            or self.parameters.get("reference_refs")
            or []
        )
        if isinstance(reference_value, str):
            reference_refs = [reference_value]
        elif isinstance(reference_value, Sequence):
            reference_refs = [str(value) for value in reference_value]
        else:
            reference_refs = []
        camera_value = self.scene_spec.get("camera") or self.parameters.get("camera") or {}
        camera = camera_value if isinstance(camera_value, Mapping) else {}
        function = str(
            self.scene_spec.get("function")
            or self.parameters.get("function")
            or "mechanic_transition"
        )
        return {
            "recipe_version": self.recipe_version,
            "function": function,
            "action": self.requested_action,
            "cast": {
                "attacker": self.cast.members["attacker"].variant_id,
                "defender": self.cast.members["defender"].variant_id,
            },
            "state_from": phases[0].state_from,
            "state_to": phases[-1].state_to,
            "motion": {
                "path": phases[1].motion_path,
                "phases": list(PHASE_NAMES),
            },
            "camera": {
                "framing": str(
                    self.scene_spec.get("framing")
                    or self.parameters.get("framing")
                    or camera.get("framing")
                    or "wide_action"
                ),
                "move": str(camera.get("move", phases[1].motion_path)),
                "focus": camera.get("focus", camera_focus),
            },
            "overlays": list(overlays),
            "sound_cues": list(sound_cues),
            "reference_refs": reference_refs,
            "phases": [phase.to_dict() for phase in phases],
            "joints": sorted(self.joints),
            "layers": [part.to_dict() for part in self.layers],
            "render_style": {
                "version": "cutout.v3",
                "body_geometry": "filled_masses",
                "gi_panels": sorted(self.gi_panels),
                "joint_visibility": "metadata_only",
            },
            "body_ownership": dict(sorted(self.body_ownership.items())),
            "joint_ownership": dict(sorted(self.joint_ownership.items())),
            "cast_z_order": dict(sorted(self.cast_z_order.items())),
            "z_order": dict(sorted(self.z_order.items())),
            "contact_anchors": {
                name: anchor.to_dict()
                for name, anchor in sorted(self.contact_anchors.items())
            },
        }

    # Alias used by callers that call a scene's recipe its action chain.
    action_chain = action_contract

    def armbar_action_chain(self) -> dict[str, Any]:
        return self.action_contract()

    def phase_contract(self) -> list[dict[str, Any]]:
        return [phase.to_dict() for phase in self.phases]

    def phase_for_action(self, action: str) -> ActionPhase:
        for phase in self.phases:
            if phase.action == action or phase.name == action:
                return phase
        raise KeyError(f"unknown BJJ action phase/action: {action}")

    def _member_color(self, member: CastMember, role: str) -> Any:
        return color_value(member.colors.get(role, member.gi_color))

    @property
    def camera_spec(self) -> Mapping[str, Any]:
        value = self.scene_spec.get("camera") or self.parameters.get("camera") or {}
        return value if isinstance(value, Mapping) else {}

    def _view_point(self, point: Point, state: str | None = None) -> Point:
        framing = str(self.camera_spec.get("framing") or "wide").casefold()
        scale = {
            "wide": 0.88,
            "wide_action": 0.88,
            "medium": 1.10,
            "split": 0.84,
            "grip_closeup": 1.52,
            "contact_closeup": 1.52,
        }.get(framing, 1.0)
        focus_x = 0.0
        focus_y = -0.35
        if "closeup" in framing:
            contact_value = self.parameters.get("contact")
            if isinstance(contact_value, Sequence) and not isinstance(contact_value, str):
                contact_value = next(iter(contact_value), None)
            contact = CONTACT_ANCHOR_ALIASES.get(
                str(contact_value or "wrist_control"),
                str(contact_value or "wrist_control"),
            )
            anchor = self.contact_anchors.get(contact)
            if anchor is not None:
                focus = self.cast.anchor_position(anchor, state or self.initial_state)
                focus_x, focus_y = focus[0], focus[1]
        return (
            (float(point[0]) - focus_x) * scale,
            (float(point[1]) - focus_y) * scale - 0.2,
            float(point[2]),
        )

    def _function_overlay(self) -> Any:
        function = str(
            self.scene_spec.get("visual_function")
            or self.scene_spec.get("function")
            or self.parameters.get("function")
            or "mechanic_transition"
        )
        labels = {
            "result_preview": "RESULT PREVIEW",
            "wide_setup": "POSITION SETUP",
            "contact_closeup": "CONTACT DETAIL",
            "mechanic_transition": "MECHANIC",
            "wrong_right_compare": "WRONG  →  RIGHT",
            "force_diagram": "FULCRUM  /  LOAD  /  EFFORT",
            "result_hold": "CONTROLLED RESULT",
        }
        label = Text(
            labels.get(function, function.replace("_", " ").upper()),
            font_size=28 if self.aspect == "landscape" else 34,
            color=self._theme_color("accent_color"),
            font=self._theme_font(),
        )
        _safe_move_to(label, (0.0, 3.35 if self.aspect == "landscape" else 5.8, 0.0))
        _safe_set_z_index(label, 120)
        layers = [label]
        if function == "wrong_right_compare":
            wrong = Text(
                "WRONG: ELBOW DROPS",
                font_size=20,
                color=self._theme_color("error_color"),
                font=self._theme_font(),
            )
            right = Text(
                "RIGHT: ELBOW ALIGNED",
                font_size=20,
                color=self._theme_color("secondary_accent"),
                font=self._theme_font(),
            )
            _safe_move_to(wrong, (-3.0, 2.75, 0.0))
            _safe_move_to(right, (3.0, 2.75, 0.0))
            layers.extend([wrong, right])
        elif function == "force_diagram":
            state = self.initial_state
            points = self.cast.states[state]
            start = self._view_point(points["attacker"]["hip_right"], state)
            end = self._view_point(points["defender"]["elbow_left"], state)
            force = Arrow(
                start,
                end,
                color=self._theme_color("secondary_accent"),
                stroke_width=7.0,
            )
            effort = Text(
                "HIP DRIVE",
                font_size=18,
                color=self._theme_color("secondary_accent"),
                font=self._theme_font("measurement_font"),
            )
            load = Text(
                "ELBOW LOAD",
                font_size=18,
                color=self._theme_color("active_emphasis"),
                font=self._theme_font("measurement_font"),
            )
            _safe_move_to(effort, (start[0] - 0.7, start[1] - 0.45, 0.0))
            _safe_move_to(load, (end[0] + 0.7, end[1] + 0.45, 0.0))
            layers.extend([force, effort, load])
        overlay = VGroup(*layers)
        _safe_set_z_index(overlay, 120)
        return overlay

    def _build_member_mobjects(self, member: CastMember) -> list[Any]:
        joints = member.joint_positions
        result: list[tuple[int, Any]] = []
        for name, part in sorted(member.body_parts.items(), key=lambda item: (item[1].z_index, item[0])):
            color = self._member_color(member, part.color_role)
            if part.kind == "circle":
                mobject = Circle(
                    radius=part.radius * 1.22,
                    color=color,
                    fill_opacity=1.0,
                    stroke_width=8.0,
                )
                _safe_move_to(mobject, self._view_point(joints[part.start_joint]))
                try:
                    mobject.shape_type = "filled_circle"
                    mobject.fill_opacity = 1.0
                    mobject.panel_role = part.panel_role
                except Exception:
                    pass
            else:
                if part.end_joint is None:
                    continue
                start = self._view_point(joints[part.start_joint])
                end = self._view_point(joints[part.end_joint])
                if part.kind in {"mass", "panel", "capsule"} or part.shape.startswith("filled_"):
                    # Opaque capsules keep the cast readable when limbs
                    # overlap.  Joint IDs remain attached as metadata rather
                    # than being rendered as the old visible line rig.
                    mobject = _capsule_mass(
                        start,
                        end,
                        max(0.04, float(part.radius)),
                        color,
                        panel=part.panel_role,
                        outline_color=self._theme_color("primary_text"),
                        outline_width=8.0,
                    )
                else:  # legacy custom manifests may still request a line
                    mobject = Line(
                        start,
                        end,
                        color=color,
                        stroke_width=max(11.0, part.stroke_width * 90),
                    )
            _safe_set_z_index(mobject, part.z_index)
            try:
                mobject.body_owner = member.cast_id
                mobject.body_part = part.name
                mobject.joint_names = (part.start_joint, part.end_joint)
                mobject.fill_opacity = float(part.fill_opacity)
                mobject.shape = part.shape
                mobject.panel_role = part.panel_role
            except Exception:
                pass
            member.part_mobjects[name] = mobject
            result.append((part.z_index, mobject))

        for name, joint in sorted(member.joints.items(), key=lambda item: (item[1].z_index, item[0])):
            marker = Dot(
                self._view_point(joints[name]),
                radius=0.035,
                color=self._member_color(member, "belt"),
            )
            _safe_set_z_index(marker, joint.z_index)
            # Joint markers are metadata-first.  They are kept faint in a real
            # render so the articulated skeleton remains inspectable without
            # dominating the gi silhouette.
            _safe_set_opacity(marker, 0.05)
            try:
                marker.body_owner = member.cast_id
                marker.joint_name = name
            except Exception:
                pass
            member.joint_mobjects[name] = marker
            result.append((joint.z_index, marker))
        return [mobject for _z, mobject in sorted(result, key=lambda item: item[0])]

    def _ensure_cast_mobjects(self) -> Any:
        if self._cast_group is not None:
            return self._cast_group
        layers: list[tuple[int, Any]] = []
        for member in self.cast.members.values():
            member_layers = self._build_member_mobjects(member)
            member.group = VGroup(*member_layers)
            layers.extend(
                (getattr(mobject, "z_index", 0), mobject)
                for mobject in member_layers
            )
        children = [mobject for _z, mobject in sorted(layers, key=lambda item: item[0])]
        self._cast_group = VGroup(*children)
        self.cast.group = self._cast_group
        try:
            self._cast_group.body_ownership = dict(self.body_ownership)
            self._cast_group.z_order = dict(self.z_order)
            self._cast_group.joints = tuple(sorted(self.joints))
            self._cast_group.member_ids = self.cast.cast_ids
            self._cast_group.gi_panels = tuple(sorted(self.gi_panels))
            self._cast_group.filled_layers = tuple(
                f"{part.owner}:{part.name}" for part in self.filled_layers
            )
            self._cast_group.joint_visibility = "metadata_only"
        except Exception:
            pass
        return self._cast_group

    def _apply_state_metadata(self, state: str) -> None:
        self.cast.set_state(state)
        self._current_state = state
        for member in self.cast.members.values():
            joints = member.joint_positions
            for name, part in member.body_parts.items():
                mobject = member.part_mobjects.get(name)
                if mobject is None:
                    continue
                if part.kind == "circle":
                    _safe_move_to(mobject, self._view_point(joints[part.start_joint], state))
                elif part.end_joint is not None:
                    start = self._view_point(joints[part.start_joint], state)
                    end = self._view_point(joints[part.end_joint], state)
                    if part.kind in {"mass", "panel", "capsule"} or part.shape.startswith("filled_"):
                        _move_filled_mass(mobject, start, end)
                    else:
                        try:
                            mobject.put_start_and_end_on(start, end)
                        except (AttributeError, TypeError, RuntimeError):
                            # Fallback lines carry their endpoints in ``args``;
                            # tests still use the authoritative cast state map.
                            try:
                                mobject.start_point = start
                                mobject.end_point = end
                            except Exception:
                                pass
            for name, mobject in member.joint_mobjects.items():
                _safe_move_to(mobject, self._view_point(joints[name], state))

    def _state_animations(self, state: str) -> list[Any]:
        animations: list[Any] = []
        target = self.cast.states[state]
        for member_id, member in self.cast.members.items():
            joints = {
                name: self._view_point(point, state)
                for name, point in target[member_id].items()
            }
            for name, part in member.body_parts.items():
                mobject = member.part_mobjects.get(name)
                if mobject is None:
                    continue
                animation = _safe_part_animation(mobject, part, joints)
                if animation is not None:
                    animations.append(animation)
            for name, mobject in member.joint_mobjects.items():
                animator = getattr(mobject, "animate", None)
                if animator is not None:
                    try:
                        animations.append(animator.move_to(joints[name]))
                    except (AttributeError, TypeError, RuntimeError):
                        pass
        return animations

    def _phase_marker(self, phase: ActionPhase, state: str) -> Any:
        anchor_name = phase.contact_anchors[0] if phase.contact_anchors else "hip_fulcrum"
        anchor = self.contact_anchors.get(anchor_name, self.contact_anchors["hip_fulcrum"])
        position = self._view_point(self.cast.anchor_position(anchor, state), state)
        marker = Circle(radius=0.11, color=self._theme_color("secondary_accent"), stroke_width=2.0)
        _safe_move_to(marker, position)
        _safe_set_z_index(marker, anchor.z_index)
        try:
            marker.contact_anchor = anchor.anchor_id
            marker.body_ownership = {
                "source": anchor.owner,
                "target": anchor.target_owner,
            }
        except Exception:
            pass
        return marker

    def entrance(self) -> None:
        group = self._ensure_cast_mobjects()
        self._apply_state_metadata(self.initial_state)
        if self._ground is None:
            self._ground = Line((-5.8, -2.20, 0.0), (5.8, -2.20, 0.0), color=self._theme_color("primary_text"), stroke_width=1.2)
            _safe_set_z_index(self._ground, 0)
            self.add(self._ground)
        first_cast_entrance = group not in getattr(self, "mobjects", [])
        if first_cast_entrance:
            self.add(group)
        if self._shot_overlay is not None:
            try:
                self.remove(self._shot_overlay)
            except (AttributeError, TypeError, RuntimeError):
                pass
        self._shot_overlay = self._function_overlay()
        self.add(self._shot_overlay)
        animations = [FadeIn(self._shot_overlay)]
        if first_cast_entrance:
            animations.insert(0, FadeIn(group))
        self.play(*animations, run_time=0.2)

    def _transition_phase(self, phase: ActionPhase, duration: float) -> None:
        self._current_phase = phase.name
        animations = self._state_animations(phase.state_to)
        marker = self._phase_marker(phase, phase.state_to)
        self._phase_markers[phase.name] = marker
        start_s = max(0.0, self._play_timeline - self._section_start)
        self.add(marker)
        # On Manim, segment animations move the persistent cast.  On fallback,
        # no ``animate`` attribute exists, so the marker animation still gives
        # the phase a deterministic clock entry before metadata is updated.
        if animations:
            try:
                self.play(*animations, FadeIn(marker), run_time=duration)
            except (AttributeError, TypeError, RuntimeError):
                self.play(FadeIn(marker), run_time=duration)
        else:
            self.play(FadeIn(marker), run_time=duration)
        self._apply_state_metadata(phase.state_to)
        self._phase_history.append(
            {
                "phase": phase.name,
                "start_s": round(float(start_s), 6),
                "end_s": round(float(self._play_timeline - self._section_start), 6),
                "state_from": phase.state_from,
                "action": phase.action,
                "state_to": phase.state_to,
                "motion_path": phase.motion_path,
                # ``ThemedScene.play`` applies the active pace scale.  Record
                # the effective phase duration, not the unscaled plan value.
                "duration_s": round(float(duration * self._pace_scale), 6),
                "contact_anchors": list(phase.contact_anchors),
                "camera_focus": phase.camera_focus,
                "overlays": list(phase.overlays),
                "sound_cues": list(phase.sound_cues),
            }
        )

    def body(self, audio_duration: float) -> None:
        phases = self.phases
        total = max(float(audio_duration or self.audio_duration or 1.0), 0.3)
        elapsed = max(0.0, self._play_timeline - self._section_start)
        remaining = max(0.05, total - elapsed)
        planned = sum(max(0.001, phase.duration_s) for phase in phases)
        self.pace_to(remaining, planned_duration=planned)
        for phase in phases:
            # ``play`` applies ``_pace_scale`` itself.  Passing the raw plan
            # here avoids applying the scale twice and keeps the audio clock
            # exact on both the Manim and fallback paths.
            self._transition_phase(phase, max(0.001, phase.duration_s))
        spent = sum(max(0.001, phase.duration_s) * self._pace_scale for phase in phases)
        tail = max(0.0, remaining - spent)
        if tail:
            self.wait(tail)

    def preview_result(self) -> None:
        """Expose a deterministic result-preview operation for shot planning."""

        self._ensure_cast_mobjects()
        self._apply_state_metadata("armbar_extension_held")

    def hold_result(self, duration: float = 0.5) -> None:
        """Hold the reviewed final state without replacing the persistent cast."""

        self.preview_result()
        self.wait(max(0.0, float(duration)))


# Compatibility aliases: callers use both spellings in manifests and tests.
ArmbarActionScene = BJJActionScene
ArticulatedBJJCast = BJJCast


__all__ = [
    "ACTION_PHASES",
    "ACTION_PHASE_SPECS",
    "ARM_BAR_ACTION_CHAIN",
    "ARM_BAR_PHASES",
    "ARMBAR_ACTION_CHAIN",
    "ARMBAR_PHASES",
    "ArmbarActionScene",
    "ActionPhase",
    "ArticulatedBJJCast",
    "BJJActionScene",
    "BJJCast",
    "BodyPart",
    "BodyPartSpec",
    "CAST_IDS",
    "CAST_MANIFEST_PATH",
    "CAST_ROOT",
    "CastMember",
    "CONTACT_ANCHOR_ALIASES",
    "ContactAnchor",
    "JOINT_NAMES",
    "Joint",
    "JointSpec",
    "PHASE_NAMES",
    "STATE_ALIASES",
    "STATE_POSES",
    "build_bjj_cast",
    "build_cast",
    "build_layered_cast",
]
