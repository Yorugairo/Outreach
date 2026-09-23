"""Backend-neutral evaluation of authored scene timing and semantic motion.

Scene frame numbers are exact rational positions. Contacts use half-open
intervals ``[start_frame, end_frame)``. The ``cubic`` channel mode is defined
here as zero-tangent cubic smoothstep; no backend curve handles are implied.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Mapping, Sequence


_SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_TARGET_KINDS = {"semantic_joint", "face_control", "articulation", "object_transform"}
_VALUE_UNITS = {"normalized", "m", "radians", "degrees", "vector3_m", "quaternion"}
_INTERPOLATIONS = {"step", "linear", "cubic"}


class MotionContractError(ValueError):
    """Raised when a scene's portable motion intent is incomplete or ambiguous."""


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise MotionContractError(f"{label} must be an integer >= {minimum}")
    return value


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise MotionContractError(f"{label} must be a safe identifier")
    return value


def _semantic_name(value: Any, label: str) -> str:
    if not isinstance(value, str) or value == "":
        raise MotionContractError(f"{label} must be a non-empty semantic token")
    return value


def _rational(value: Any, label: str, *, allow_zero: bool = True) -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, int) and not isinstance(value, bool):
        result = Fraction(value, 1)
    elif isinstance(value, Mapping):
        numerator = _integer(value.get("numerator"), f"{label}.numerator")
        denominator = _integer(value.get("denominator"), f"{label}.denominator", minimum=1)
        result = Fraction(numerator, denominator)
    else:
        raise MotionContractError(f"{label} must be an exact rational frame or time")
    if result < 0 or (not allow_zero and result == 0):
        comparison = "non-negative" if allow_zero else "positive"
        raise MotionContractError(f"{label} must be {comparison}")
    return result


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MotionContractError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise MotionContractError(f"{label} must be finite")
    return number


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MotionContractError(f"{label} must be an object")
    return value


@dataclass(frozen=True)
class RationalClock:
    """An authored scene clock with exact FPS and frame-to-second conversion."""

    fps: Fraction
    duration_frames: int
    origin_seconds: Fraction = Fraction(0, 1)

    def __post_init__(self) -> None:
        fps = _rational(self.fps, "fps", allow_zero=False)
        duration = _integer(self.duration_frames, "duration_frames", minimum=1)
        origin_seconds = _rational(self.origin_seconds, "scene time origin")
        object.__setattr__(self, "fps", fps)
        object.__setattr__(self, "duration_frames", duration)
        object.__setattr__(self, "origin_seconds", origin_seconds)

    def seconds_at(self, frame: int | Fraction) -> Fraction:
        exact_frame = _rational(frame, "frame")
        return self.origin_seconds + exact_frame / self.fps


@dataclass(frozen=True, order=True)
class SemanticTarget:
    """A stable semantic address, independent of a rig or layer implementation."""

    binding_id: str
    target_kind: str
    semantic_name: str

    def __post_init__(self) -> None:
        _identifier(self.binding_id, "binding_id")
        if self.target_kind not in _TARGET_KINDS:
            raise MotionContractError(f"unsupported target_kind {self.target_kind!r}")
        _semantic_name(self.semantic_name, "semantic target")


@dataclass(frozen=True)
class MotionEvent:
    event_id: str
    event_type: str
    frame: int
    binding_id: str | None = None


@dataclass(frozen=True)
class MotionContact:
    contact_id: str
    actor_binding_id: str
    semantic_effector: str
    target_binding_id: str
    start_frame: int
    end_frame: int
    target_semantic_joint: str | None = None
    target_surface_id: str | None = None

    def active_at(self, frame: Fraction) -> bool:
        return Fraction(self.start_frame) <= frame < Fraction(self.end_frame)


@dataclass(frozen=True)
class MotionChannel:
    channel_id: str
    target: SemanticTarget
    value_unit: str
    interpolation: str
    keyframes: tuple[tuple[int, float | tuple[float, ...]], ...]


@dataclass(frozen=True)
class EvaluatedChannel:
    channel_id: str
    target: SemanticTarget
    value_unit: str
    value: float | tuple[float, ...]


@dataclass(frozen=True)
class MotionSample:
    scene_id: str
    frame: Fraction
    time_seconds: Fraction
    events: tuple[MotionEvent, ...]
    contacts: tuple[MotionContact, ...]
    channels: tuple[EvaluatedChannel, ...]


@dataclass(frozen=True)
class MotionExposureSample:
    """One output-frame exposure of a source-clock timeline.

    ``sample`` evaluates pose at the exposure midpoint. Point events and
    contacts are reported separately when their source intervals intersect the
    half-open output exposure; midpoint sampling alone can miss either one.
    """

    output_frame: int
    output_fps: Fraction
    source_start_frame: Fraction
    source_end_frame: Fraction
    sample: MotionSample
    exposed_events: tuple[MotionEvent, ...]
    exposed_contacts: tuple[MotionContact, ...]


@dataclass(frozen=True)
class BoundMotionChannel:
    """A semantic channel paired with an opaque backend-owned target handle."""

    channel_id: str
    target: SemanticTarget
    target_handle: object
    value_unit: str
    value: float | tuple[float, ...]


@dataclass(frozen=True)
class BoundMotionSample:
    """One portable sample with channels resolved by a backend target map."""

    scene_id: str
    frame: Fraction
    time_seconds: Fraction
    events: tuple[MotionEvent, ...]
    contacts: tuple[MotionContact, ...]
    channels: tuple[BoundMotionChannel, ...]


@dataclass(frozen=True)
class MotionTimeline:
    scene_id: str
    clock: RationalClock
    events: tuple[MotionEvent, ...]
    contacts: tuple[MotionContact, ...]
    channels: tuple[MotionChannel, ...]

    @classmethod
    def from_scene(cls, value: Mapping[str, Any]) -> MotionTimeline:
        """Parse the motion-bearing fields of a validated ``model_scene.v1``.

        Full asset, path, hash, capability, and approval validation remains the
        responsibility of ``validate_model_scene``. This parser does not grant
        render eligibility or operator approval.
        """

        scene = _as_mapping(value, "scene")
        scene_id = _identifier(scene.get("scene_id"), "scene_id")
        duration = _integer(scene.get("duration_frames"), "duration_frames", minimum=1)
        fps_value = _as_mapping(scene.get("fps"), "fps")
        fps = _rational(fps_value, "fps", allow_zero=False)
        origin = _as_mapping(scene.get("time_origin"), "time_origin")
        origin_seconds = _rational(origin.get("scene_time_seconds"), "time_origin.scene_time_seconds")
        clock = RationalClock(fps=fps, duration_frames=duration, origin_seconds=origin_seconds)

        events = cls._parse_events(scene.get("events"), duration)
        contacts = cls._parse_contacts(scene.get("contacts"), duration)
        channels = cls._parse_channels(scene.get("motion_channels", []), duration)
        return cls(
            scene_id=scene_id,
            clock=clock,
            events=tuple(sorted(events, key=lambda item: (item.frame, item.event_id))),
            contacts=tuple(sorted(contacts, key=lambda item: item.contact_id)),
            channels=tuple(sorted(channels, key=lambda item: item.channel_id)),
        )

    @staticmethod
    def _parse_events(value: Any, duration: int) -> list[MotionEvent]:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise MotionContractError("events must be an array")
        parsed: list[MotionEvent] = []
        seen: set[str] = set()
        for index, raw in enumerate(value):
            row = _as_mapping(raw, f"events[{index}]")
            event_id = _identifier(row.get("event_id"), f"events[{index}].event_id")
            if event_id in seen:
                raise MotionContractError(f"duplicate event_id {event_id!r}")
            seen.add(event_id)
            event_type = row.get("event_type")
            if not isinstance(event_type, str) or not event_type.strip():
                raise MotionContractError(f"events[{index}].event_type must be non-empty")
            frame = _integer(row.get("frame"), f"events[{index}].frame")
            if frame >= duration:
                raise MotionContractError(f"events[{index}].frame must be less than duration_frames")
            binding = row.get("binding_id")
            if binding is not None:
                binding = _identifier(binding, f"events[{index}].binding_id")
            parsed.append(MotionEvent(event_id, event_type, frame, binding))
        return parsed

    @staticmethod
    def _parse_contacts(value: Any, duration: int) -> list[MotionContact]:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise MotionContractError("contacts must be an array")
        parsed: list[MotionContact] = []
        seen: set[str] = set()
        for index, raw in enumerate(value):
            row = _as_mapping(raw, f"contacts[{index}]")
            contact_id = _identifier(row.get("contact_id"), f"contacts[{index}].contact_id")
            if contact_id in seen:
                raise MotionContractError(f"duplicate contact_id {contact_id!r}")
            seen.add(contact_id)
            actor = _identifier(row.get("actor_binding_id"), f"contacts[{index}].actor_binding_id")
            effector = _semantic_name(row.get("semantic_effector"), f"contacts[{index}].semantic_effector")
            target_binding = _identifier(row.get("target_binding_id"), f"contacts[{index}].target_binding_id")
            start = _integer(row.get("start_frame"), f"contacts[{index}].start_frame")
            end = _integer(row.get("end_frame"), f"contacts[{index}].end_frame", minimum=1)
            if not start < end <= duration:
                raise MotionContractError(
                    f"contacts[{index}] contact interval must satisfy 0 <= start < end <= duration_frames"
                )
            target_joint = row.get("target_semantic_joint")
            target_surface = row.get("target_surface_id")
            if (target_joint is None) == (target_surface is None):
                raise MotionContractError(
                    f"contacts[{index}] requires exactly one semantic joint or surface target"
                )
            if target_joint is not None:
                target_joint = _semantic_name(target_joint, f"contacts[{index}].target_semantic_joint")
            if target_surface is not None:
                target_surface = _identifier(target_surface, f"contacts[{index}].target_surface_id")
            parsed.append(
                MotionContact(
                    contact_id=contact_id,
                    actor_binding_id=actor,
                    semantic_effector=effector,
                    target_binding_id=target_binding,
                    start_frame=start,
                    end_frame=end,
                    target_semantic_joint=target_joint,
                    target_surface_id=target_surface,
                )
            )
        return parsed

    @staticmethod
    def _parse_channels(value: Any, duration: int) -> list[MotionChannel]:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise MotionContractError("motion_channels must be an array")
        parsed: list[MotionChannel] = []
        seen: set[str] = set()
        for index, raw in enumerate(value):
            row = _as_mapping(raw, f"motion_channels[{index}]")
            channel_id = _identifier(row.get("channel_id"), f"motion_channels[{index}].channel_id")
            if channel_id in seen:
                raise MotionContractError(f"duplicate channel_id {channel_id!r}")
            seen.add(channel_id)
            target = SemanticTarget(
                binding_id=_identifier(row.get("binding_id"), f"motion_channels[{index}].binding_id"),
                target_kind=str(row.get("target_kind", "")),
                semantic_name=_semantic_name(
                    row.get("semantic_target"), f"motion_channels[{index}].semantic_target"
                ),
            )
            unit = row.get("value_unit")
            if unit not in _VALUE_UNITS:
                raise MotionContractError(f"motion_channels[{index}].value_unit is unsupported")
            interpolation = row.get("interpolation")
            if interpolation not in _INTERPOLATIONS:
                raise MotionContractError(f"motion_channels[{index}].interpolation is unsupported")
            raw_keyframes = row.get("keyframes")
            if not isinstance(raw_keyframes, Sequence) or isinstance(raw_keyframes, (str, bytes)) or not raw_keyframes:
                raise MotionContractError(f"motion_channels[{index}].keyframes must be a non-empty array")
            keyframes: list[tuple[int, float | tuple[float, ...]]] = []
            previous = -1
            for key_index, raw_key in enumerate(raw_keyframes):
                key = _as_mapping(raw_key, f"motion_channels[{index}].keyframes[{key_index}]")
                frame = _integer(
                    key.get("frame"), f"motion_channels[{index}].keyframes[{key_index}].frame"
                )
                if frame <= previous:
                    raise MotionContractError(
                        f"motion_channels[{index}].keyframes must be strictly increasing"
                    )
                if frame >= duration:
                    raise MotionContractError(
                        f"motion_channels[{index}].keyframes[{key_index}].frame must be less than duration_frames"
                    )
                previous = frame
                keyframes.append(
                    (
                        frame,
                        MotionTimeline._parse_value(
                            key.get("value"), unit, f"motion_channels[{index}].keyframes[{key_index}].value"
                        ),
                    )
                )
            MotionTimeline._assert_compatible_values(keyframes, unit, f"motion_channels[{index}]")
            parsed.append(MotionChannel(channel_id, target, unit, interpolation, tuple(keyframes)))
        return parsed

    @staticmethod
    def _parse_value(value: Any, unit: str, label: str) -> float | tuple[float, ...]:
        if unit in {"vector3_m", "quaternion"}:
            expected = 3 if unit == "vector3_m" else 4
            if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != expected:
                raise MotionContractError(f"{label} must contain exactly {expected} components for {unit}")
            components = tuple(_finite_number(item, f"{label}[{component}]") for component, item in enumerate(value))
            if unit == "quaternion":
                length = math.hypot(*components)
                if not math.isfinite(length) or length == 0.0:
                    raise MotionContractError(f"{label} quaternion must have finite non-zero length")
                return tuple(component / length for component in components)
            return components
        return _finite_number(value, label)

    @staticmethod
    def _assert_compatible_values(
        keyframes: Sequence[tuple[int, float | tuple[float, ...]]], unit: str, label: str
    ) -> None:
        if unit not in {"vector3_m", "quaternion"}:
            if any(not isinstance(value, float) for _, value in keyframes):
                raise MotionContractError(f"{label} scalar channel values are inconsistent")
            return
        expected = 3 if unit == "vector3_m" else 4
        if any(not isinstance(value, tuple) or len(value) != expected for _, value in keyframes):
            raise MotionContractError(f"{label} vector channel values are inconsistent")

    def evaluate(self, frame: int | Fraction) -> MotionSample:
        """Evaluate all authored events, contacts, and channels at an exact frame."""

        exact_frame = _rational(frame, "frame")
        if exact_frame >= self.clock.duration_frames:
            raise MotionContractError("frame is outside the scene frame range")
        events = tuple(event for event in self.events if exact_frame == event.frame)
        contacts = tuple(contact for contact in self.contacts if contact.active_at(exact_frame))
        channels = tuple(
            EvaluatedChannel(
                channel_id=channel.channel_id,
                target=channel.target,
                value_unit=channel.value_unit,
                value=self._evaluate_channel(channel, exact_frame),
            )
            for channel in self.channels
        )
        return MotionSample(
            scene_id=self.scene_id,
            frame=exact_frame,
            time_seconds=self.clock.seconds_at(exact_frame),
            events=events,
            contacts=contacts,
            channels=channels,
        )

    def evaluate_output_exposure(
        self, output_frame: int, output_fps: int | Fraction
    ) -> MotionExposureSample:
        """Sample a complete output frame against this timeline's source clock.

        Output frame zero begins at the scene origin. Exposures are half-open,
        so a point event on an output boundary appears in the following frame
        exactly once. Partial exposures beyond the authored duration are refused.
        This opt-in read does not change ``evaluate``'s exact-frame semantics.
        """

        frame = _integer(output_frame, "output_frame")
        fps = _rational(output_fps, "output_fps", allow_zero=False)
        start = Fraction(frame) * self.clock.fps / fps
        end = Fraction(frame + 1) * self.clock.fps / fps
        if end > self.clock.duration_frames:
            raise MotionContractError("output exposure is outside the scene frame range")
        midpoint = (start + end) / 2
        return MotionExposureSample(
            output_frame=frame,
            output_fps=fps,
            source_start_frame=start,
            source_end_frame=end,
            sample=self.evaluate(midpoint),
            exposed_events=tuple(event for event in self.events if start <= event.frame < end),
            exposed_contacts=tuple(
                contact
                for contact in self.contacts
                if contact.start_frame < end and contact.end_frame > start
            ),
        )

    @staticmethod
    def _evaluate_channel(channel: MotionChannel, frame: Fraction) -> float | tuple[float, ...]:
        keyframes = channel.keyframes
        if frame <= keyframes[0][0]:
            return keyframes[0][1]
        if frame >= keyframes[-1][0]:
            return keyframes[-1][1]
        left_index = next(index for index in range(len(keyframes) - 1) if keyframes[index][0] <= frame < keyframes[index + 1][0])
        left_frame, left_value = keyframes[left_index]
        right_frame, right_value = keyframes[left_index + 1]
        if channel.interpolation == "step":
            return left_value
        t = float((frame - left_frame) / (right_frame - left_frame))
        if channel.interpolation == "cubic":
            t = t * t * (3.0 - 2.0 * t)
        if channel.value_unit == "quaternion":
            assert isinstance(left_value, tuple) and isinstance(right_value, tuple)
            return _slerp(left_value, right_value, t)
        if isinstance(left_value, tuple) and isinstance(right_value, tuple):
            return tuple(a + (b - a) * t for a, b in zip(left_value, right_value))
        assert isinstance(left_value, float) and isinstance(right_value, float)
        return left_value + (right_value - left_value) * t


def _slerp(left: tuple[float, ...], right: tuple[float, ...], t: float) -> tuple[float, ...]:
    """Shortest-path quaternion SLERP with stable normalized linear fallback."""

    left_norm = math.hypot(*left)
    right_norm = math.hypot(*right)
    a = tuple(component / left_norm for component in left)
    b = tuple(component / right_norm for component in right)
    dot = math.fsum(x * y for x, y in zip(a, b))
    if dot < 0.0:
        b = tuple(-component for component in b)
        dot = -dot
    dot = min(1.0, max(-1.0, dot))
    if dot > 0.9995:
        blended = tuple(x + (y - x) * t for x, y in zip(a, b))
        length = math.sqrt(math.fsum(component * component for component in blended))
        return tuple(component / length for component in blended)
    angle = math.acos(dot)
    sin_angle = math.sin(angle)
    left_weight = math.sin((1.0 - t) * angle) / sin_angle
    right_weight = math.sin(t * angle) / sin_angle
    return tuple(x * left_weight + y * right_weight for x, y in zip(a, b))


def bind_motion_targets(
    sample: MotionSample, target_map: Mapping[SemanticTarget, object]
) -> BoundMotionSample:
    """Resolve sample channels through a backend-owned opaque semantic map.

    The map may contain Blender controls, layer pivots, or another backend's
    handles; none of those names are copied into the portable motion intent.
    """

    bound: list[BoundMotionChannel] = []
    for channel in sample.channels:
        if channel.target not in target_map:
            raise MotionContractError(
                f"unmapped semantic target {channel.target.binding_id}:{channel.target.semantic_name}"
            )
        target_handle = target_map[channel.target]
        if target_handle is None:
            raise MotionContractError(
                f"semantic target {channel.target.binding_id}:{channel.target.semantic_name} resolved to None"
            )
        bound.append(
            BoundMotionChannel(
                channel_id=channel.channel_id,
                target=channel.target,
                target_handle=target_handle,
                value_unit=channel.value_unit,
                value=channel.value,
            )
        )
    return BoundMotionSample(
        scene_id=sample.scene_id,
        frame=sample.frame,
        time_seconds=sample.time_seconds,
        events=sample.events,
        contacts=sample.contacts,
        channels=tuple(bound),
    )


__all__ = [
    "BoundMotionChannel",
    "BoundMotionSample",
    "EvaluatedChannel",
    "MotionChannel",
    "MotionContact",
    "MotionContractError",
    "MotionEvent",
    "MotionSample",
    "MotionTimeline",
    "RationalClock",
    "SemanticTarget",
    "bind_motion_targets",
]
