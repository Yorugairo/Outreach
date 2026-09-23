"""Pure, seek-safe planar rig math for the rig-foundation proof.

The renderer consumes these functions but owns no state.  The skinning helper
is deliberately named and described as a *normalized per-point rigid-transform
blend*: it combines translations and shortest-arc rotations per vertex.  It is
not DQS, BBW, or a claim about whole-mesh area/volume preservation; the caller
must inspect triangle areas/Jacobians for the particular mesh.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence


Vec2 = tuple[float, float]
EPS = 1.0e-9


def add(a: Vec2, b: Vec2) -> Vec2:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Vec2, b: Vec2) -> Vec2:
    return (a[0] - b[0], a[1] - b[1])


def scale(a: Vec2, factor: float) -> Vec2:
    return (a[0] * factor, a[1] * factor)


def dot(a: Vec2, b: Vec2) -> float:
    return a[0] * b[0] + a[1] * b[1]


def length(a: Vec2) -> float:
    return math.hypot(a[0], a[1])


def distance(a: Vec2, b: Vec2) -> float:
    return length(sub(a, b))


def normalized(a: Vec2, fallback: Vec2 = (1.0, 0.0)) -> Vec2:
    magnitude = length(a)
    if magnitude <= EPS:
        return fallback
    return (a[0] / magnitude, a[1] / magnitude)


def lerp(a: float, b: float, u: float) -> float:
    return a + (b - a) * u


def lerp_point(a: Vec2, b: Vec2, u: float) -> Vec2:
    return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def wrap_angle(angle: float) -> float:
    """Wrap to (-pi, pi]."""
    wrapped = (angle + math.pi) % (2.0 * math.pi) - math.pi
    return math.pi if wrapped <= -math.pi else wrapped


def minimum_jerk(u: float) -> float:
    """Rest-to-rest quintic; used only on explicitly declared lift/settle spans."""
    u = clamp(u, 0.0, 1.0)
    return 10.0 * u**3 - 15.0 * u**4 + 6.0 * u**5


def fast_out(u: float) -> float:
    u = clamp(u, 0.0, 1.0)
    return 1.0 - (1.0 - u) ** 3


def fall_in(u: float) -> float:
    u = clamp(u, 0.0, 1.0)
    return u * u


def cubic_bezier(p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2, u: float) -> Vec2:
    u = clamp(u, 0.0, 1.0)
    v = 1.0 - u
    return (
        v**3 * p0[0] + 3.0 * v**2 * u * p1[0] + 3.0 * v * u**2 * p2[0] + u**3 * p3[0],
        v**3 * p0[1] + 3.0 * v**2 * u * p1[1] + 3.0 * v * u**2 * p2[1] + u**3 * p3[1],
    )


def cubic_bezier_derivative(p0: Vec2, p1: Vec2, p2: Vec2, p3: Vec2, u: float) -> Vec2:
    u = clamp(u, 0.0, 1.0)
    v = 1.0 - u
    return (
        3.0 * v**2 * (p1[0] - p0[0]) + 6.0 * v * u * (p2[0] - p1[0]) + 3.0 * u**2 * (p3[0] - p2[0]),
        3.0 * v**2 * (p1[1] - p0[1]) + 6.0 * v * u * (p2[1] - p1[1]) + 3.0 * u**2 * (p3[1] - p2[1]),
    )


def hermite(p0: Vec2, p1: Vec2, v0: Vec2, v1: Vec2, u: float, duration_s: float) -> Vec2:
    """Cubic Hermite arc with explicit boundary velocities.

    The velocity at p1 is intentionally allowed to be non-zero.  Punch
    contact therefore flows into follow-through instead of easing to a dead
    stop exactly on the glove/head event.
    """
    u = clamp(u, 0.0, 1.0)
    u2 = u * u
    u3 = u2 * u
    h00 = 2.0 * u3 - 3.0 * u2 + 1.0
    h10 = u3 - 2.0 * u2 + u
    h01 = -2.0 * u3 + 3.0 * u2
    h11 = u3 - u2
    d0 = scale(v0, duration_s)
    d1 = scale(v1, duration_s)
    return (
        h00 * p0[0] + h10 * d0[0] + h01 * p1[0] + h11 * d1[0],
        h00 * p0[1] + h10 * d0[1] + h01 * p1[1] + h11 * d1[1],
    )


@dataclass(frozen=True)
class RigidTransform2D:
    tx: float = 0.0
    ty: float = 0.0
    angle: float = 0.0

    def apply(self, point: Vec2) -> Vec2:
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        return (self.tx + c * point[0] - s * point[1], self.ty + s * point[0] + c * point[1])

    def matrix(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        return ((c, -s, self.tx), (s, c, self.ty))


@dataclass(frozen=True)
class IKResult:
    root: Vec2
    elbow: Vec2
    end: Vec2
    requested_target: Vec2
    solved_target: Vec2
    upper_length: float
    lower_length: float
    reach_min: float
    reach_max: float
    requested_distance: float
    target_error: float
    reachable: bool
    bend: int

    @property
    def upper_error(self) -> float:
        return distance(self.root, self.elbow) - self.upper_length

    @property
    def lower_error(self) -> float:
        return distance(self.elbow, self.end) - self.lower_length


def two_bone_ik(root: Vec2, target: Vec2, upper_length: float, lower_length: float, bend: int = 1) -> IKResult:
    """Solve a planar two-link chain in closed form with explicit reach clamp."""
    if not all(math.isfinite(value) for value in (*root, *target, upper_length, lower_length)):
        raise ValueError("two-bone inputs must be finite")
    if upper_length <= 0.0 or lower_length <= 0.0:
        raise ValueError("two-bone lengths must be positive")
    bend = 1 if bend >= 0 else -1
    delta = sub(target, root)
    requested_distance = length(delta)
    reach_min = abs(upper_length - lower_length)
    reach_max = upper_length + lower_length
    # Keep the law-of-cosines triangle non-degenerate while reporting whether
    # the authored target itself was reachable.
    safe_min = max(reach_min + 1.0e-7, 1.0e-7)
    safe_max = max(safe_min, reach_max - 1.0e-7)
    solved_distance = clamp(requested_distance, safe_min, safe_max)
    direction = normalized(delta)
    solved_target = add(root, scale(direction, solved_distance))
    alpha = math.atan2(direction[1], direction[0])
    cos_beta = clamp((upper_length * upper_length + solved_distance * solved_distance - lower_length * lower_length) / (2.0 * upper_length * solved_distance), -1.0, 1.0)
    beta = math.acos(cos_beta)
    shoulder_angle = alpha + bend * beta
    elbow = add(root, (upper_length * math.cos(shoulder_angle), upper_length * math.sin(shoulder_angle)))
    forearm_direction = normalized(sub(solved_target, elbow), (math.cos(shoulder_angle), math.sin(shoulder_angle)))
    end = add(elbow, scale(forearm_direction, lower_length))
    reachable = abs(requested_distance - solved_distance) <= 1.0e-6
    return IKResult(
        root=root,
        elbow=elbow,
        end=end,
        requested_target=target,
        solved_target=solved_target,
        upper_length=upper_length,
        lower_length=lower_length,
        reach_min=reach_min,
        reach_max=reach_max,
        requested_distance=requested_distance,
        target_error=distance(target, solved_target),
        reachable=reachable,
        bend=bend,
    )


def _weight_items(influences: Mapping[str, float]) -> list[tuple[str, float]]:
    if not influences:
        raise ValueError("a skin point needs at least one influence")
    raw_weights = [float(weight) for weight in influences.values()]
    if any(not math.isfinite(weight) or weight < 0.0 for weight in raw_weights):
        raise ValueError("skin influence weights must be finite and nonnegative")
    total = sum(raw_weights)
    if total <= EPS:
        raise ValueError("skin influence weights must sum above zero")
    # Stable highest-weight/lexical order fixes the reference hemisphere for
    # antipodal rotations and keeps the simple fallback deterministic.
    items = [(name, float(weight) / total) for name, weight in influences.items() if float(weight) > 0.0]
    return sorted(items, key=lambda item: (-item[1], item[0]))


def blend_rigid_point(point: Vec2, transforms: Mapping[str, RigidTransform2D], influences: Mapping[str, float]) -> Vec2:
    """Apply a normalized shortest-arc rigid-transform blend to one point.

    Translation is weighted directly. Rotation is blended along the shortest
    angular offsets relative to the first influence, then applied to the point.
    Because weights may vary over the mesh, this is a spatially varying
    deformation; triangle area must be measured rather than assumed preserved.
    """
    items = _weight_items(influences)
    for name, _ in items:
        if name not in transforms:
            raise KeyError(f"missing skin transform: {name}")
        transform = transforms[name]
        if not all(math.isfinite(value) for value in (transform.tx, transform.ty, transform.angle)):
            raise ValueError("skin transforms must be finite")
    reference = transforms[items[0][0]].angle
    blended_angle = reference + sum(weight * wrap_angle(transforms[name].angle - reference) for name, weight in items)
    tx = sum(weight * transforms[name].tx for name, weight in items)
    ty = sum(weight * transforms[name].ty for name, weight in items)
    return RigidTransform2D(tx, ty, blended_angle).apply(point)


def skin_mesh(points: Sequence[Vec2], transforms: Mapping[str, RigidTransform2D], weights: Sequence[Mapping[str, float]]) -> list[Vec2]:
    if len(points) != len(weights):
        raise ValueError("one influence map is required per mesh point")
    return [blend_rigid_point(point, transforms, influence) for point, influence in zip(points, weights)]


def polygon_area(points: Sequence[Vec2]) -> float:
    if len(points) < 3:
        return 0.0
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points)))


def triangle_area(a: Vec2, b: Vec2, c: Vec2) -> float:
    return 0.5 * ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))


def bounds(points: Iterable[Vec2]) -> tuple[float, float, float, float]:
    points = list(points)
    if not points:
        raise ValueError("bounds requires at least one point")
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return (min(xs), min(ys), max(xs), max(ys))
