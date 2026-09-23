"""Coordinate-safe inspection summaries for portable motion evaluations."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .motion import MotionSample, SemanticTarget


_COORDINATE_TYPES = {
    "world_3d": ("m", 3),
    "projected_screen": ("px", 2),
    "layer_depth": ("dimensionless", 1),
}
_SAFE_FRAME_ID = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class MotionInspectionError(ValueError):
    """Raised when a motion residual has missing or contradictory coordinates."""


@dataclass(frozen=True)
class CoordinateResidual:
    """Target-minus-solved residual expressed in one declared coordinate frame."""

    target: SemanticTarget
    frame: Fraction
    coordinate_space: str
    coordinate_frame_id: str
    unit: str
    components: tuple[float, ...]

    def __post_init__(self) -> None:
        expected = _COORDINATE_TYPES.get(self.coordinate_space)
        if expected is None:
            raise MotionInspectionError(f"unsupported coordinate_space {self.coordinate_space!r}")
        expected_unit, expected_components = expected
        if self.unit != expected_unit:
            raise MotionInspectionError(
                f"coordinate_space {self.coordinate_space!r} requires unit {expected_unit!r}"
            )
        if not isinstance(self.coordinate_frame_id, str) or not _SAFE_FRAME_ID.fullmatch(
            self.coordinate_frame_id
        ):
            raise MotionInspectionError("coordinate_frame_id must be a safe identifier")
        if not isinstance(self.frame, Fraction) or self.frame < 0:
            raise MotionInspectionError("residual frame must be a non-negative exact Fraction")
        if len(self.components) != expected_components:
            raise MotionInspectionError(
                f"coordinate_space {self.coordinate_space!r} requires {expected_components} components"
            )
        if any(
            isinstance(component, bool)
            or not isinstance(component, (int, float))
            or not math.isfinite(float(component))
            for component in self.components
        ):
            raise MotionInspectionError("residual components must be finite numbers")
        object.__setattr__(self, "components", tuple(float(component) for component in self.components))

    @property
    def magnitude(self) -> float:
        return math.sqrt(math.fsum(component * component for component in self.components))


@dataclass(frozen=True)
class ResidualGroup:
    coordinate_space: str
    coordinate_frame_id: str
    unit: str
    sample_count: int
    maximum_magnitude: float


@dataclass(frozen=True)
class MotionInspection:
    """A deterministic, non-approving diagnostic summary for one sampled frame."""

    scene_id: str
    frame: Fraction
    time_seconds: Fraction
    event_ids: tuple[str, ...]
    contact_ids: tuple[str, ...]
    channels: tuple
    residuals: tuple[CoordinateResidual, ...]
    residual_groups: tuple[ResidualGroup, ...]


def inspect_motion_sample(
    sample: MotionSample, residuals: Iterable[CoordinateResidual] = ()
) -> MotionInspection:
    """Summarize one sample and keep unlike residual spaces in separate groups.

    This report carries measurements only. It sets no pass/fail, art, or
    operator-approval verdict and compares no metre, pixel, or layer-depth
    magnitude against another coordinate space.
    """

    rows = tuple(residuals)
    if any(not isinstance(row, CoordinateResidual) for row in rows):
        raise MotionInspectionError("residuals must be CoordinateResidual records")
    if any(row.frame != sample.frame for row in rows):
        raise MotionInspectionError("every residual frame must match sample frame")
    ordered = tuple(
        sorted(
            rows,
            key=lambda row: (
                row.coordinate_space,
                row.coordinate_frame_id,
                row.target.binding_id,
                row.target.target_kind,
                row.target.semantic_name,
            ),
        )
    )
    groups: dict[tuple[str, str, str], list[CoordinateResidual]] = {}
    for row in ordered:
        groups.setdefault((row.coordinate_space, row.coordinate_frame_id, row.unit), []).append(row)
    summaries = tuple(
        ResidualGroup(
            coordinate_space=space,
            coordinate_frame_id=frame_id,
            unit=unit,
            sample_count=len(values),
            maximum_magnitude=max(row.magnitude for row in values),
        )
        for (space, frame_id, unit), values in sorted(groups.items())
    )
    return MotionInspection(
        scene_id=sample.scene_id,
        frame=sample.frame,
        time_seconds=sample.time_seconds,
        event_ids=tuple(event.event_id for event in sample.events),
        contact_ids=tuple(contact.contact_id for contact in sample.contacts),
        channels=sample.channels,
        residuals=ordered,
        residual_groups=summaries,
    )


__all__ = [
    "CoordinateResidual",
    "MotionInspection",
    "MotionInspectionError",
    "ResidualGroup",
    "inspect_motion_sample",
]
