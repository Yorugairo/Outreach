"""Review-only deep-flexion skinning comparison for the pinned native Rigify rig.

The worker runs inside an isolated, offline Blender process. It opens the pinned
source, authors two in-memory FK flexion poses, measures source-topology patches
under three modifier configurations, renders matched review views, and never
saves the source scene.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import stat
import struct
import sys
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[5]
SOURCE_RELATIVE = "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"
SOURCE_SHA256 = "5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade"
REVIEW_RELATIVE = "content/video_engine/review/model-engines/benchmark-v1/3d/deep-flexion"
SUPPORTED_BLENDER_VERSION = "5.2.2 LTS"
SUPPORTED_BLENDER_BUILD_HASH = "d13f752e3b9c"
LEGACY_SCHEMA = "model_deep_flexion.v1"
LEGACY_PROJECTION_SCHEMA = "model_deep_flexion.v2"
LEGACY_PROJECTION_CAMERA_SCHEMA = "model_deep_flexion.v3"
SCHEMA = "model_deep_flexion.v4"
GEOMETRY_SCHEMA = "model_deep_flexion_geometry.v1"
ATTEMPT_SCHEMA = "model_deep_flexion_attempt.v1"
SOURCE_ID_ATTRIBUTE = "deep_flexion_source_vertex_id"
TARGET_BEND_DEGREES = 90.0
BEND_VECTOR_ANGLE_TOLERANCE_DEGREES = 0.00001
PROJECTED_BEND_ANGLE_TOLERANCE_DEGREES = 0.05
BONE_PLANE_CAMERA_ALIGNMENT_MIN = 0.999
JOINT_CLOSEUP_CENTRAL_CROP_BOUNDS = (0.30, 0.30, 0.70, 0.70)
LEGACY_PROJECTION_ORTHO_SCALES_M = (0.90, 1.20)
CLOSEUP_CAMERA_PROFILES: dict[str, dict[str, Any]] = {
    "right_elbow": {
        "name": "right_elbow_bone_plane_oblique",
        "direction_mode": "measured_deform_bone_plane_normal_z_positive",
        "orthographic_scale_m": 0.90,
    },
    "left_knee": {
        "name": "left_knee_bone_plane_oblique",
        "direction_mode": "measured_deform_bone_plane_normal_z_positive",
        "orthographic_scale_m": 1.20,
    },
}
LEGACY_V3_CLOSEUP_CAMERA_PROFILES: dict[str, dict[str, Any]] = {
    "right_elbow": {
        "name": "right_elbow_oblique_45deg",
        "yaw_relative_to_saved_front_degrees": 45.0,
        "orthographic_scale_m": 0.90,
    },
    "left_knee": {
        "name": "left_knee_front_chain",
        "yaw_relative_to_saved_front_degrees": 0.0,
        "orthographic_scale_m": 1.20,
    },
}
REGION_WEIGHT_THRESHOLD = 0.10
DEGENERATE_TRIANGLE_AREA_M2 = 1e-12
DEGENERATE_EDGE_LENGTH_M = 1e-9
DISTORTION_QUANTILES = (0.0, 0.05, 0.50, 0.95, 1.0)
MAX_RECEIPT_BYTES = 3_000_000
MAX_GEOMETRY_BYTES = 64_000_000
MAX_PNG_BYTES = 24_000_000
MAX_LOG_BYTES = 32_000_000
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
RUN_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")

REGIONS: dict[str, dict[str, Any]] = {
    "right_elbow": {
        "label": "right upper arm through elbow and forearm",
        "bones": ("DEF-upper_arm.R", "DEF-forearm.R"),
        "controls": ("upper_arm_fk.R", "forearm_fk.R"),
        "switch": "upper_arm_parent.R",
        "groups": (
            "DEF-shoulder.R",
            "DEF-shoulder-helper.R",
            "DEF-upper_arm.R",
            "DEF-upper_arm.R.001",
            "DEF-forearm.R",
            "DEF-forearm.R.001",
            "DEF-elbow-helper.R",
        ),
    },
    "left_knee": {
        "label": "left pelvis through thigh and knee/shin",
        "bones": ("DEF-thigh.L", "DEF-shin.L"),
        "controls": ("thigh_fk.L", "shin_fk.L"),
        "switch": "thigh_parent.L",
        "groups": (
            "DEF-pelvis-helper.L",
            "DEF-pelvis-helper.front.L",
            "DEF-thigh.L",
            "DEF-thigh.L.001",
            "DEF-shin.L",
            "DEF-shin.L.001",
            "DEF-knee-helper.L",
        ),
    },
}

CONFIGURATIONS: dict[str, dict[str, Any]] = {
    "saved_stack": {
        "label": "saved source modifier stack",
        "preserve_volume": None,
        "armature_count": 2,
        "vertex_group_mask": "source stack masks PV to mhmask-preserve-volume",
    },
    "single_lbs": {
        "label": "single unmasked linear-blend Armature modifier",
        "preserve_volume": False,
        "armature_count": 1,
        "vertex_group_mask": "none",
    },
    "single_preserve_volume": {
        "label": "single unmasked preserve-volume Armature modifier",
        "preserve_volume": True,
        "armature_count": 1,
        "vertex_group_mask": "none",
    },
}

POSE_KEYS = ("neutral", "deep_flexion")
_ATTEMPT_DETAILS: dict[str, Any] = {}


class DeepFlexionError(RuntimeError):
    """The pinned Blender deep-flexion diagnostic could not be verified."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _write_json(path: Path, value: Any) -> None:
    path = Path(path)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(_json_bytes(value))
    temporary.replace(path)


def _reparse_point(path: Path) -> bool:
    path = Path(path)
    try:
        if path.is_symlink():
            return True
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _path_chain_has_reparse(path: Path) -> bool:
    current = Path(path)
    while True:
        if _reparse_point(current):
            return True
        if current.parent == current:
            return False
        current = current.parent


def _assert_pinned_source(path: Path) -> None:
    if not path.is_file() or _reparse_point(path):
        raise DeepFlexionError("pinned source is missing or redirected")
    if sha256_file(path) != SOURCE_SHA256:
        raise DeepFlexionError("pinned source hash does not match the expected digest")


def _round_float(value: Any, label: str, digits: int = 9) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeepFlexionError(f"invalid numeric value: {label}")
    result = float(value)
    if not math.isfinite(result):
        raise DeepFlexionError(f"non-finite numeric value: {label}")
    return round(result, digits)


def _bend_degrees_from_world_vectors(state: dict[str, Any], region_name: str, label: str) -> float:
    contract = REGIONS[region_name]
    bones = list(contract["bones"])
    if state.get("deform_bones") != bones:
        raise DeepFlexionError(f"{label} does not identify the expected DEF bones")
    vectors = state.get("bone_vectors_world_m")
    if not isinstance(vectors, dict) or set(vectors) != set(bones):
        raise DeepFlexionError(f"{label} has invalid world-bone vectors")

    normalized: list[tuple[float, float, float]] = []
    for bone_name in bones:
        vector = vectors[bone_name]
        if not isinstance(vector, list) or len(vector) != 3:
            raise DeepFlexionError(f"{label} has an invalid vector for {bone_name}")
        components_list: list[float] = []
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise DeepFlexionError(f"{label} has a non-numeric vector component for {bone_name}")
            component = float(value)
            if not math.isfinite(component):
                raise DeepFlexionError(f"{label} has a non-finite vector component for {bone_name}")
            components_list.append(component)
        components = tuple(components_list)
        magnitude = math.hypot(*components)
        if not math.isfinite(magnitude) or magnitude <= 0.0:
            raise DeepFlexionError(f"{label} has a zero-length or invalid vector for {bone_name}")
        normalized.append(tuple(component / magnitude for component in components))

    cosine = math.fsum(left * right for left, right in zip(normalized[0], normalized[1]))
    if not math.isfinite(cosine):
        raise DeepFlexionError(f"{label} has invalid normalized world-bone vectors")
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def _orthographic_projection_from_view_matrix(
    matrix: Sequence[Sequence[float]], world_point_m: Sequence[float], ortho_scale_m: float
) -> list[float]:
    homogeneous = [float(value) for value in world_point_m] + [1.0]
    camera_point = [
        math.fsum(float(matrix[row][column]) * homogeneous[column] for column in range(4))
        for row in range(3)
    ]
    return [0.5 + camera_point[0] / ortho_scale_m, 0.5 + camera_point[1] / ortho_scale_m]


def _finite_matrix4(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(
            isinstance(row, list)
            and len(row) == 4
            and all(
                not isinstance(component, bool)
                and isinstance(component, (int, float))
                and math.isfinite(float(component))
                for component in row
            )
            for row in value
        )
    )


def _camera_yaw_delta_degrees(
    saved_front_view: Sequence[Sequence[float]], closeup_view: Sequence[Sequence[float]]
) -> float:
    front_forward = (-float(saved_front_view[2][0]), -float(saved_front_view[2][1]))
    close_forward = (-float(closeup_view[2][0]), -float(closeup_view[2][1]))
    cross = front_forward[0] * close_forward[1] - front_forward[1] * close_forward[0]
    dot = math.fsum(front_forward[axis] * close_forward[axis] for axis in range(2))
    return math.degrees(math.atan2(cross, dot))


def _normalized_world_bone_vectors(
    state: dict[str, Any], region_name: str, label: str
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    _bend_degrees_from_world_vectors(state, region_name, label)
    vectors = state["bone_vectors_world_m"]
    result = []
    for bone_name in REGIONS[region_name]["bones"]:
        components = tuple(float(value) for value in vectors[bone_name])
        magnitude = math.hypot(*components)
        result.append(tuple(component / magnitude for component in components))
    return result[0], result[1]


def _bone_plane_normal_world(state: dict[str, Any], region_name: str, label: str) -> tuple[float, float, float]:
    upper, lower = _normalized_world_bone_vectors(state, region_name, label)
    normal = (
        upper[1] * lower[2] - upper[2] * lower[1],
        upper[2] * lower[0] - upper[0] * lower[2],
        upper[0] * lower[1] - upper[1] * lower[0],
    )
    magnitude = math.hypot(*normal)
    if not math.isfinite(magnitude) or magnitude <= 1e-9:
        raise DeepFlexionError(f"{label} bone vectors do not define a stable camera plane")
    normal = tuple(component / magnitude for component in normal)
    if normal[2] < -1e-12 or (abs(normal[2]) <= 1e-12 and normal[0] < 0.0):
        normal = tuple(-component for component in normal)
    return normal


def _projected_bone_vectors_camera(
    matrix: Sequence[Sequence[float]], state: dict[str, Any], region_name: str, label: str
) -> dict[str, list[float]]:
    _normalized_world_bone_vectors(state, region_name, label)
    vectors = state["bone_vectors_world_m"]
    projected: dict[str, list[float]] = {}
    for bone_name in REGIONS[region_name]["bones"]:
        vector = vectors[bone_name]
        camera_vector = [
            math.fsum(float(matrix[row][axis]) * float(vector[axis]) for axis in range(3))
            for row in range(2)
        ]
        magnitude = math.hypot(*camera_vector)
        if not math.isfinite(magnitude) or magnitude <= 1e-9:
            raise DeepFlexionError(f"{label} {bone_name} is foreshortened to an unmeasurable camera vector")
        projected[bone_name] = [round(component / magnitude, 9) for component in camera_vector]
    return projected


def _projected_bend_degrees_from_view_matrix(
    matrix: Sequence[Sequence[float]], state: dict[str, Any], region_name: str, label: str
) -> float:
    vectors = list(_projected_bone_vectors_camera(matrix, state, region_name, label).values())
    cosine = math.fsum(vectors[0][axis] * vectors[1][axis] for axis in range(2))
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def _camera_back_direction_world(matrix: Sequence[Sequence[float]]) -> tuple[float, float, float]:
    vector = tuple(float(value) for value in matrix[2][:3])
    magnitude = math.hypot(*vector)
    if not math.isfinite(magnitude) or magnitude <= 1e-9:
        raise DeepFlexionError("close-up camera has an invalid world-space view axis")
    return tuple(component / magnitude for component in vector)


def _camera_plane_alignment(
    matrix: Sequence[Sequence[float]], state: dict[str, Any], region_name: str, label: str
) -> float:
    camera_back = _camera_back_direction_world(matrix)
    normal = _bone_plane_normal_world(state, region_name, label)
    return math.fsum(camera_back[axis] * normal[axis] for axis in range(3))


def _distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((float(a[axis]) - float(b[axis])) ** 2 for axis in range(3)))


def _triangle_area(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    ab = [float(b[axis]) - float(a[axis]) for axis in range(3)]
    ac = [float(c[axis]) - float(a[axis]) for axis in range(3)]
    cross = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )
    return 0.5 * math.sqrt(sum(component * component for component in cross))


def _bounds(points: Iterable[Sequence[float]]) -> dict[str, list[float]]:
    materialized = list(points)
    if not materialized:
        raise DeepFlexionError("region has no measured vertices")
    return {
        "min": [round(min(float(point[axis]) for point in materialized), 9) for axis in range(3)],
        "max": [round(max(float(point[axis]) for point in materialized), 9) for axis in range(3)],
    }


def _edge_pairs(triangles: Sequence[Sequence[int]]) -> list[list[int]]:
    edges: set[tuple[int, int]] = set()
    for triangle in triangles:
        a, b, c = (int(value) for value in triangle)
        edges.update((tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((c, a)))))
    return [list(edge) for edge in sorted(edges)]


def _connected_component_count(triangles: Sequence[Sequence[int]]) -> int:
    adjacency: dict[int, set[int]] = {}
    for triangle in triangles:
        a, b, c = (int(value) for value in triangle)
        for left, right in ((a, b), (b, c), (c, a)):
            adjacency.setdefault(left, set()).add(right)
            adjacency.setdefault(right, set()).add(left)
    seen: set[int] = set()
    components = 0
    for vertex in adjacency:
        if vertex in seen:
            continue
        components += 1
        seen.add(vertex)
        stack = [vertex]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
    return components


def _source_id_digest(values: Sequence[int]) -> str:
    encoded = json.dumps([int(value) for value in values], separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _quantile_summary(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        raise DeepFlexionError("cannot summarize an empty distortion sample")
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) for value in ordered):
        raise DeepFlexionError("distortion sample contains a non-finite value")

    def at(q: float) -> float:
        position = (len(ordered) - 1) * q
        low = math.floor(position)
        high = math.ceil(position)
        return ordered[low] + (ordered[high] - ordered[low]) * (position - low)

    return {
        "count": len(ordered),
        "min": round(ordered[0], 9),
        "p05": round(at(0.05), 9),
        "p50": round(at(0.50), 9),
        "p95": round(at(0.95), 9),
        "max": round(ordered[-1], 9),
    }


def _mask_summary(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        raise DeepFlexionError("cannot summarize empty vertex-group coverage")
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) or value < 0.0 for value in ordered):
        raise DeepFlexionError("invalid vertex-group weight")
    return {
        "count": len(ordered),
        "positive_count": sum(value > 0.0 for value in ordered),
        "min": round(ordered[0], 9),
        "mean": round(sum(ordered) / len(ordered), 9),
        "max": round(ordered[-1], 9),
    }


def _metrics_for_region(raw_region: dict[str, Any]) -> dict[str, Any]:
    vertex_ids = [int(value) for value in raw_region["source_vertex_ids"]]
    triangles = [[int(value) for value in triangle] for triangle in raw_region["triangles"]]
    edges = [[int(value) for value in edge] for edge in raw_region["edges"]]
    samples = raw_region["samples"]
    if set(samples) != set(CONFIGURATIONS):
        raise DeepFlexionError("raw geometry configuration set is incomplete")

    results: dict[str, Any] = {}
    for configuration in CONFIGURATIONS:
        frame_samples = samples[configuration]
        if set(frame_samples) != set(POSE_KEYS):
            raise DeepFlexionError(f"raw geometry pose set is incomplete: {configuration}")
        positions: dict[str, dict[int, list[float]]] = {}
        for pose in POSE_KEYS:
            points = frame_samples[pose]["positions_world_m"]
            if not isinstance(points, list) or len(points) != len(vertex_ids):
                raise DeepFlexionError(f"raw position count mismatch: {configuration}/{pose}")
            positions[pose] = {
                vertex_id: [
                    _round_float(value, f"{configuration}/{pose} coordinate") for value in point
                ]
                for vertex_id, point in zip(vertex_ids, points)
            }

        neutral = positions["neutral"]
        base_areas = [_triangle_area(*(neutral[index] for index in triangle)) for triangle in triangles]
        base_lengths = [_distance(neutral[a], neutral[b]) for a, b in edges]
        valid_area = [index for index, area in enumerate(base_areas) if area > DEGENERATE_TRIANGLE_AREA_M2]
        valid_edge = [index for index, length in enumerate(base_lengths) if length > DEGENERATE_EDGE_LENGTH_M]
        if not valid_area or not valid_edge:
            raise DeepFlexionError(f"neutral geometry has no valid area/edge samples: {configuration}")
        base_total_area = sum(base_areas)
        if base_total_area <= 0.0:
            raise DeepFlexionError(f"neutral geometry has zero total area: {configuration}")

        configuration_results: dict[str, Any] = {}
        for pose in POSE_KEYS:
            current = positions[pose]
            areas = [_triangle_area(*(current[index] for index in triangle)) for triangle in triangles]
            lengths = [_distance(current[a], current[b]) for a, b in edges]
            area_ratios = [areas[index] / base_areas[index] for index in valid_area]
            edge_ratios = [lengths[index] / base_lengths[index] for index in valid_edge]
            if any(not math.isfinite(value) for value in area_ratios + edge_ratios):
                raise DeepFlexionError(f"non-finite deformation ratios: {configuration}/{pose}")
            configuration_results[pose] = {
                "evaluated_mesh_vertices": int(frame_samples[pose]["evaluated_mesh_vertices"]),
                "evaluated_mesh_triangles": int(frame_samples[pose]["evaluated_mesh_triangles"]),
                "source_id_map_sha256": str(frame_samples[pose]["source_id_map_sha256"]),
                "retained_region_vertices": len(vertex_ids),
                "retained_region_triangles": len(triangles),
                "bounds_world_m": _bounds(current.values()),
                "triangle_area_total_m2": round(sum(areas), 9),
                "triangle_area_total_ratio_to_neutral": round(sum(areas) / base_total_area, 9),
                "degenerate_triangle_count": sum(area <= DEGENERATE_TRIANGLE_AREA_M2 for area in areas),
                "neutral_degenerate_triangle_count": sum(
                    area <= DEGENERATE_TRIANGLE_AREA_M2 for area in base_areas
                ),
                "triangle_area_ratio": _quantile_summary(area_ratios),
                "edge_length_ratio": _quantile_summary(edge_ratios),
                "degenerate_edge_count": sum(length <= DEGENERATE_EDGE_LENGTH_M for length in lengths),
                "neutral_degenerate_edge_count": sum(
                    length <= DEGENERATE_EDGE_LENGTH_M for length in base_lengths
                ),
            }
        results[configuration] = configuration_results
    return results


def _safe_flat_child(
    output: Path,
    name: Any,
    expected_name: str,
    digest: Any,
    max_bytes: int,
) -> Path:
    if name != expected_name or Path(str(name)).name != expected_name:
        raise DeepFlexionError(f"invalid artifact path: {expected_name}")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise DeepFlexionError(f"invalid artifact digest: {expected_name}")
    if _reparse_point(output):
        raise DeepFlexionError("review output is a symlink or reparse point")
    resolved_output = output.resolve(strict=True)
    path = output / expected_name
    if not path.is_file() or _reparse_point(path):
        raise DeepFlexionError(f"missing or unsafe artifact: {expected_name}")
    if path.resolve(strict=True).parent != resolved_output:
        raise DeepFlexionError(f"artifact escapes its run directory: {expected_name}")
    if path.stat().st_size > max_bytes or sha256_file(path) != digest:
        raise DeepFlexionError(f"artifact size or digest mismatch: {expected_name}")
    return path


def _png_dimensions(path: Path) -> tuple[int, int]:
    with Path(path).open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise DeepFlexionError(f"invalid PNG header: {Path(path).name}")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise DeepFlexionError(f"invalid PNG dimensions: {Path(path).name}")
    return width, height


def validate_receipt(
    receipt: Any,
    output: Path,
    *,
    review_root: Path | None = None,
) -> dict[str, Any]:
    """Independently reopen artifacts, re-hash them, and recompute all patch metrics."""
    try:
        output = Path(output)
        if not output.is_dir() or _path_chain_has_reparse(output):
            raise DeepFlexionError("review output is missing or redirected")
        expected_root = Path(review_root) if review_root is not None else ROOT / REVIEW_RELATIVE
        if not expected_root.is_dir() or _path_chain_has_reparse(expected_root):
            raise DeepFlexionError("review quarantine is missing or redirected")
        root = expected_root.resolve(strict=True)
        resolved = output.resolve(strict=True)
        if resolved.parent != root:
            raise DeepFlexionError("review run is outside the allowed quarantine")
        if not isinstance(receipt, dict) or receipt.get("schema") not in {
            SCHEMA,
            LEGACY_SCHEMA,
            LEGACY_PROJECTION_SCHEMA,
            LEGACY_PROJECTION_CAMERA_SCHEMA,
        }:
            raise DeepFlexionError("invalid deep-flexion receipt schema")
        if receipt.get("status") != "diagnostic_only" or receipt.get("verdict") != "diagnostic_only":
            raise DeepFlexionError("receipt must remain diagnostic-only")

        expected_source = {
            "path": SOURCE_RELATIVE,
            "sha256_before": SOURCE_SHA256,
            "sha256_after": SOURCE_SHA256,
            "mutated": False,
        }
        if receipt.get("source") != expected_source:
            raise DeepFlexionError("receipt source does not match the pinned read-only input")
        _assert_pinned_source(ROOT / SOURCE_RELATIVE)
        tool = receipt.get("tool", {})
        if (
            tool.get("name") != "Blender"
            or tool.get("version") != SUPPORTED_BLENDER_VERSION
            or tool.get("build_hash") != SUPPORTED_BLENDER_BUILD_HASH
            or tool.get("network") != "offline"
            or tool.get("embedded_scripts") != "disabled"
        ):
            raise DeepFlexionError("receipt does not confirm pinned offline/scripts-disabled Blender")
        if receipt.get("target_bend_degrees") != TARGET_BEND_DEGREES:
            raise DeepFlexionError("deep-bend acceptance target changed")
        inventory = receipt.get("inventory", {})
        body = inventory.get("body", {})
        rig = inventory.get("rig", {})
        if (
            body.get("object") != "Human"
            or body.get("stored_vertices") != 19158
            or rig.get("object") != "Human.rigify"
            or rig.get("bone_count") != 930
            or rig.get("saved_action") != "Human.rigifyAction"
        ):
            raise DeepFlexionError("receipt scene inventory differs from pinned source contract")
        saved_front_view_matrix = None
        if receipt["schema"] == SCHEMA:
            camera_inventory = inventory.get("camera", {})
            saved_front_view_matrix = camera_inventory.get("view_matrix_world_to_camera")
            resolution = camera_inventory.get("resolution_px")
            if (
                camera_inventory.get("name") != "ReviewCamera_front"
                or not isinstance(resolution, list)
                or len(resolution) != 2
                or any(type(value) is not int or value <= 0 for value in resolution)
                or resolution[0] != resolution[1]
                or not _finite_matrix4(saved_front_view_matrix)
            ):
                raise DeepFlexionError("saved front camera view matrix or square crop is invalid")
        expected_saved_modifiers = [
            ("Armature", "ARMATURE", False, ""),
            ("Armature PV", "ARMATURE", True, "mhmask-preserve-volume"),
            ("Hide helpers", "MASK", None, None),
        ]
        actual_saved_modifiers = [
            (
                item.get("name"), item.get("type"), item.get("use_deform_preserve_volume"),
                item.get("vertex_group_mask"),
            )
            for item in body.get("saved_modifiers", [])
        ]
        if actual_saved_modifiers != expected_saved_modifiers:
            raise DeepFlexionError("receipt does not retain the saved modifier stack")
        if set(receipt.get("modifier_configurations", {})) != set(CONFIGURATIONS):
            raise DeepFlexionError("modifier comparison set is incomplete")
        for name, config in CONFIGURATIONS.items():
            actual = receipt["modifier_configurations"][name]
            if (
                actual.get("label") != config["label"]
                or actual.get("armature_count") != config["armature_count"]
                or actual.get("preserve_volume") != config["preserve_volume"]
                or actual.get("vertex_group_mask") != config["vertex_group_mask"]
            ):
                raise DeepFlexionError(f"modifier configuration changed: {name}")
            stack = actual.get("stack", [])
            armatures = [item for item in stack if item.get("type") == "ARMATURE"]
            if len(armatures) != config["armature_count"]:
                raise DeepFlexionError(f"Armature modifier count changed: {name}")
            if name == "saved_stack":
                stack_signature = [
                    (item.get("name"), item.get("type"), item.get("use_deform_preserve_volume"), item.get("vertex_group_mask"))
                    for item in stack
                ]
                if stack_signature != expected_saved_modifiers:
                    raise DeepFlexionError("saved modifier comparison does not match source stack")
            else:
                armature = armatures[0]
                if (
                    bool(armature.get("use_deform_preserve_volume")) != config["preserve_volume"]
                    or armature.get("vertex_group_mask") != ""
                    or [item.get("type") for item in stack] != ["ARMATURE", "MASK"]
                    or stack[1].get("name") != "Hide helpers"
                ):
                    raise DeepFlexionError(f"single-modifier comparison setup changed: {name}")

        thresholds = receipt.get("thresholds")
        if thresholds != {
            "source_region_weight_inclusive_min": REGION_WEIGHT_THRESHOLD,
            "deep_bend_degrees_inclusive_min": TARGET_BEND_DEGREES,
            "degenerate_triangle_area_m2_inclusive_max": DEGENERATE_TRIANGLE_AREA_M2,
            "degenerate_edge_length_m_inclusive_max": DEGENERATE_EDGE_LENGTH_M,
            "distortion_quantiles": list(DISTORTION_QUANTILES),
            "quality_pass_threshold": None,
        }:
            raise DeepFlexionError("receipt measurement thresholds changed")
        if receipt.get("volume_measurement") != (
            "not measured: selected limb patches are open surfaces, not enclosed volumes"
        ):
            raise DeepFlexionError("receipt violates the open-patch volume boundary")

        geometry_entry = receipt.get("raw_geometry", {})
        geometry_path = _safe_flat_child(
            output,
            geometry_entry.get("path"),
            "geometry.json",
            geometry_entry.get("sha256"),
            MAX_GEOMETRY_BYTES,
        )
        if geometry_path.stat().st_size != geometry_entry.get("bytes"):
            raise DeepFlexionError("raw geometry byte count mismatch")
        geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
        if geometry.get("schema") != GEOMETRY_SCHEMA or geometry.get("source_sha256") != SOURCE_SHA256:
            raise DeepFlexionError("raw geometry provenance is invalid")
        source_vertex_count = geometry.get("source_vertex_count")
        if type(source_vertex_count) is not int or source_vertex_count != body["stored_vertices"]:
            raise DeepFlexionError("raw source topology count is invalid")

        topology_maps = geometry.get("evaluated_topology", {})
        if set(topology_maps) != set(CONFIGURATIONS):
            raise DeepFlexionError("evaluated topology configuration set is incomplete")
        shared_ids: list[int] | None = None
        for configuration in CONFIGURATIONS:
            if set(topology_maps[configuration]) != set(POSE_KEYS):
                raise DeepFlexionError(f"evaluated topology pose set is incomplete: {configuration}")
            for pose in POSE_KEYS:
                item = topology_maps[configuration][pose]
                ids = item.get("source_vertex_ids")
                if (
                    not isinstance(ids, list)
                    or not ids
                    or any(type(value) is not int or value < 0 or value >= source_vertex_count for value in ids)
                    or len(set(ids)) != len(ids)
                    or item.get("source_id_map_sha256") != _source_id_digest(ids)
                    or type(item.get("evaluated_mesh_vertices")) is not int
                    or item["evaluated_mesh_vertices"] != len(ids)
                    or type(item.get("evaluated_mesh_triangles")) is not int
                    or item["evaluated_mesh_triangles"] <= 0
                ):
                    raise DeepFlexionError(f"invalid source-ID map: {configuration}/{pose}")
                if shared_ids is None:
                    shared_ids = ids
                elif ids != shared_ids:
                    raise DeepFlexionError("evaluated source-ID map changed across configurations or poses")

        raw_regions = geometry.get("regions", {})
        receipt_regions = receipt.get("regions", {})
        if set(raw_regions) != set(REGIONS) or set(receipt_regions) != set(REGIONS):
            raise DeepFlexionError("receipt is missing a measured limb region")
        for region_name, contract in REGIONS.items():
            raw_region = raw_regions[region_name]
            selection = receipt_regions[region_name].get("selection", {})
            if raw_region.get("groups") != list(contract["groups"]):
                raise DeepFlexionError(f"skin-group mapping changed: {region_name}")
            if raw_region.get("weight_threshold") != REGION_WEIGHT_THRESHOLD:
                raise DeepFlexionError(f"source-region threshold changed: {region_name}")
            source_ids = raw_region.get("source_vertex_ids")
            selected_ids = raw_region.get("selected_source_vertex_ids")
            triangles = raw_region.get("triangles")
            edges = raw_region.get("edges")
            weights = raw_region.get("selected_source_group_weight_sum")
            pv_weights = raw_region.get("original_pv_mask_weights")
            if (
                not isinstance(source_ids, list)
                or len(source_ids) < 100
                or source_ids != sorted(set(source_ids))
                or not isinstance(selected_ids, list)
                or len(selected_ids) < 100
                or selected_ids != sorted(set(selected_ids))
                or len(weights) != len(selected_ids)
                or len(pv_weights) != len(selected_ids)
                or any(type(value) is not int or value not in set(selected_ids) for value in source_ids)
                or any(type(value) is not int or value < 0 or value >= source_vertex_count for value in selected_ids)
                or any(not math.isfinite(float(value)) or float(value) < REGION_WEIGHT_THRESHOLD for value in weights)
                or any(float(value) != 0.0 for value in pv_weights)
                or not isinstance(triangles, list)
                or len(triangles) < 100
                or edges != _edge_pairs(triangles)
                or set(index for triangle in triangles for index in triangle) != set(source_ids)
                or any(
                    not isinstance(triangle, list)
                    or len(triangle) != 3
                    or any(type(index) is not int or index not in set(source_ids) for index in triangle)
                    for triangle in triangles
                )
                or _connected_component_count(triangles) != 1
            ):
                raise DeepFlexionError(f"invalid source-ID-stable limb patch: {region_name}")
            for configuration in CONFIGURATIONS:
                if set(raw_region.get("samples", {}).get(configuration, {})) != set(POSE_KEYS):
                    raise DeepFlexionError(f"missing raw sample geometry: {region_name}/{configuration}")
                for pose in POSE_KEYS:
                    sample = raw_region["samples"][configuration][pose]
                    topology = topology_maps[configuration][pose]
                    points = sample.get("positions_world_m")
                    if (
                        sample.get("source_id_map_sha256") != topology["source_id_map_sha256"]
                        or sample.get("evaluated_mesh_vertices") != topology["evaluated_mesh_vertices"]
                        or sample.get("evaluated_mesh_triangles") != topology["evaluated_mesh_triangles"]
                        or not isinstance(points, list)
                        or len(points) != len(source_ids)
                        or any(
                            not isinstance(point, list)
                            or len(point) != 3
                            or any(not math.isfinite(float(value)) for value in point)
                            for point in points
                        )
                    ):
                        raise DeepFlexionError(f"invalid raw patch coordinates: {region_name}/{configuration}/{pose}")
            if selection.get("source_vertex_count") != len(selected_ids):
                raise DeepFlexionError(f"source selection count mismatch: {region_name}")
            if selection.get("measured_vertex_count") != len(source_ids):
                raise DeepFlexionError(f"measured source vertex count mismatch: {region_name}")
            if selection.get("triangle_count") != len(triangles) or selection.get("edge_count") != len(edges):
                raise DeepFlexionError(f"patch topology count mismatch: {region_name}")
            coverage = receipt_regions[region_name].get("original_pv_mask_coverage", {})
            recomputed_coverage = _mask_summary(pv_weights)
            if coverage != recomputed_coverage or coverage["positive_count"] != 0:
                raise DeepFlexionError(f"original PV mask unexpectedly covers {region_name}")
            if receipt_regions[region_name].get("skin_group_weight_sum") != _mask_summary(weights):
                raise DeepFlexionError(f"skin-group weight summary mismatch: {region_name}")
            recomputed_metrics = _metrics_for_region(raw_region)
            if receipt_regions[region_name].get("measurements") != recomputed_metrics:
                raise DeepFlexionError(f"reported geometry metrics do not recompute: {region_name}")

        pose_states = receipt.get("pose_states", {})
        if set(pose_states) != {"neutral", "right_elbow_deep", "left_knee_deep"}:
            raise DeepFlexionError("pose-state evidence is incomplete")
        measured_bends: dict[tuple[str, str], float] = {}
        for pose_name in ("neutral", "right_elbow_deep", "left_knee_deep"):
            pose_state = pose_states[pose_name]
            if not isinstance(pose_state, dict) or set(pose_state) != set(REGIONS):
                raise DeepFlexionError(f"pose-state joint set is incomplete: {pose_name}")
            for region_name in REGIONS:
                state = pose_state[region_name]
                if not isinstance(state, dict):
                    raise DeepFlexionError(f"joint state is invalid: {pose_name}/{region_name}")
                label = f"{pose_name}/{region_name}"
                measured = _bend_degrees_from_world_vectors(state, region_name, label)
                reported = state.get("bend_degrees")
                if isinstance(reported, bool) or not isinstance(reported, (int, float)):
                    raise DeepFlexionError(f"{label} has an invalid reported bend angle")
                reported = float(reported)
                if not math.isfinite(reported):
                    raise DeepFlexionError(f"{label} has a non-finite reported bend angle")
                if abs(measured - reported) > BEND_VECTOR_ANGLE_TOLERANCE_DEGREES:
                    raise DeepFlexionError(
                        f"{label} reported bend angle does not match its world-bone vectors "
                        f"within {BEND_VECTOR_ANGLE_TOLERANCE_DEGREES:g} degrees"
                    )
                measured_bends[(pose_name, region_name)] = measured

        for pose_name, target_joint in (("right_elbow_deep", "right_elbow"), ("left_knee_deep", "left_knee")):
            if measured_bends[(pose_name, target_joint)] < TARGET_BEND_DEGREES:
                raise DeepFlexionError(f"measured bend target was not reached from bone vectors: {target_joint}")

        renders = receipt.get("renders", {})
        expected_renders = {
            f"{configuration}-{joint}-{view}.png"
            for configuration in CONFIGURATIONS
            for joint in REGIONS
            for view in ("context", "closeup")
        }
        if set(renders) != expected_renders:
            raise DeepFlexionError("matched render set is incomplete")
        reference_resolution: list[int] | None = None
        matched_view_matrices: dict[str, list[list[float]]] = {}
        for name in sorted(expected_renders):
            item = renders[name]
            path = _safe_flat_child(output, item.get("path"), name, item.get("sha256"), MAX_PNG_BYTES)
            dimensions = list(_png_dimensions(path))
            if path.stat().st_size != item.get("bytes") or dimensions != item.get("resolution_px"):
                raise DeepFlexionError(f"render metadata mismatch: {name}")
            expected_view = "full_body_context" if name.endswith("-context.png") else "matched_joint_closeup"
            expected_camera = "ReviewCamera_front" if expected_view == "full_body_context" else "DeepFlexionCloseupCamera"
            if item.get("view") != expected_view or item.get("camera") != expected_camera:
                raise DeepFlexionError(f"render view/camera does not match the comparison: {name}")
            if expected_view == "matched_joint_closeup":
                parts = name.split("-")
                joint_name = parts[1]
                expected_pose = "right_elbow_deep" if joint_name == "right_elbow" else "left_knee_deep"
                expected_target = pose_states[expected_pose][joint_name].get("joint_center_world_m")
                if item.get("target_world_m") != expected_target:
                    raise DeepFlexionError(f"matched close-up target differs from the measured joint: {name}")
                if receipt["schema"] == LEGACY_SCHEMA:
                    if item.get("orthographic_scale_m") != 0.60:
                        raise DeepFlexionError(f"legacy matched close-up camera changed: {name}")
                else:
                    projection = item.get("joint_projection_normalized")
                    bounds = list(JOINT_CLOSEUP_CENTRAL_CROP_BOUNDS)
                    if receipt["schema"] == LEGACY_PROJECTION_SCHEMA:
                        allowed_scales = LEGACY_PROJECTION_ORTHO_SCALES_M
                    elif receipt["schema"] == LEGACY_PROJECTION_CAMERA_SCHEMA:
                        allowed_scales = (LEGACY_V3_CLOSEUP_CAMERA_PROFILES[joint_name]["orthographic_scale_m"],)
                    else:
                        allowed_scales = (CLOSEUP_CAMERA_PROFILES[joint_name]["orthographic_scale_m"],)
                    if (
                        item.get("orthographic_scale_m") not in allowed_scales
                        or item.get("central_crop_bounds_normalized") != bounds
                        or not isinstance(projection, list)
                        or len(projection) != 2
                        or any(
                            isinstance(value, bool)
                            or not isinstance(value, (int, float))
                            or not math.isfinite(float(value))
                            for value in projection
                        )
                        or not (
                            bounds[0] <= float(projection[0]) <= bounds[2]
                            and bounds[1] <= float(projection[1]) <= bounds[3]
                        )
                    ):
                        raise DeepFlexionError(f"projected joint falls outside the central close-up crop: {name}")
                    if receipt["schema"] == LEGACY_PROJECTION_CAMERA_SCHEMA:
                        profile = LEGACY_V3_CLOSEUP_CAMERA_PROFILES[joint_name]
                        if (
                            item.get("camera_profile") != profile["name"]
                            or item.get("yaw_relative_to_saved_front_degrees")
                            != profile["yaw_relative_to_saved_front_degrees"]
                        ):
                            raise DeepFlexionError(f"matched close-up view profile changed: {name}")
                        matrix = item.get("camera_view_matrix_world_to_camera")
                        if not _finite_matrix4(matrix):
                            raise DeepFlexionError(f"matched close-up view matrix is invalid: {name}")
                        previous_matrix = matched_view_matrices.setdefault(joint_name, matrix)
                        if previous_matrix != matrix:
                            raise DeepFlexionError(f"modifier comparisons use mismatched joint cameras: {joint_name}")
                        yaw_delta = _camera_yaw_delta_degrees(saved_front_view_matrix, matrix)
                        if abs(yaw_delta - float(profile["yaw_relative_to_saved_front_degrees"])) > 0.01:
                            raise DeepFlexionError(f"matched close-up camera yaw does not match its profile: {name}")
                        expected_projection = _orthographic_projection_from_view_matrix(
                            matrix, expected_target, float(profile["orthographic_scale_m"])
                        )
                        if any(
                            abs(float(projection[axis]) - expected_projection[axis]) > 0.0001
                            for axis in range(2)
                        ):
                            raise DeepFlexionError(f"joint projection does not recompute from the view matrix: {name}")
                    if receipt["schema"] == SCHEMA:
                        profile = CLOSEUP_CAMERA_PROFILES[joint_name]
                        if item.get("camera_profile") != profile["name"] or item.get("camera_direction_mode") != profile[
                            "direction_mode"
                        ]:
                            raise DeepFlexionError(f"matched close-up view profile changed: {name}")
                        matrix = item.get("camera_view_matrix_world_to_camera")
                        if not _finite_matrix4(matrix):
                            raise DeepFlexionError(f"matched close-up view matrix is invalid: {name}")
                        previous_matrix = matched_view_matrices.setdefault(joint_name, matrix)
                        if previous_matrix != matrix:
                            raise DeepFlexionError(f"modifier comparisons use mismatched joint cameras: {joint_name}")
                        yaw_delta = _camera_yaw_delta_degrees(saved_front_view_matrix, matrix)
                        reported_yaw = item.get("yaw_relative_to_saved_front_degrees")
                        if (
                            isinstance(reported_yaw, bool)
                            or not isinstance(reported_yaw, (int, float))
                            or not math.isfinite(float(reported_yaw))
                            or abs(yaw_delta - float(reported_yaw)) > 0.01
                        ):
                            raise DeepFlexionError(f"matched close-up camera yaw does not recompute: {name}")
                        expected_projection = _orthographic_projection_from_view_matrix(
                            matrix, expected_target, float(profile["orthographic_scale_m"])
                        )
                        if any(
                            abs(float(projection[axis]) - expected_projection[axis]) > 0.0001
                            for axis in range(2)
                        ):
                            raise DeepFlexionError(f"joint projection does not recompute from the view matrix: {name}")
                        measured_state = pose_states[expected_pose][joint_name]
                        label = f"{expected_pose}/{joint_name} close-up"
                        expected_normal = _bone_plane_normal_world(measured_state, joint_name, label)
                        alignment = _camera_plane_alignment(matrix, measured_state, joint_name, label)
                        if (
                            item.get("bone_plane_normal_world") != [round(value, 9) for value in expected_normal]
                            or not math.isfinite(alignment)
                            or alignment < BONE_PLANE_CAMERA_ALIGNMENT_MIN
                            or not isinstance(item.get("bone_plane_camera_alignment"), (int, float))
                            or isinstance(item.get("bone_plane_camera_alignment"), bool)
                            or abs(alignment - float(item["bone_plane_camera_alignment"])) > 1e-6
                        ):
                            raise DeepFlexionError(f"close-up camera is not aligned to the measured bone plane: {name}")
                        projected_vectors = _projected_bone_vectors_camera(
                            matrix, measured_state, joint_name, label
                        )
                        if item.get("projected_bone_vectors_camera") != projected_vectors:
                            raise DeepFlexionError(f"projected DEF-bone vectors do not recompute: {name}")
                        projected_bend = _projected_bend_degrees_from_view_matrix(
                            matrix, measured_state, joint_name, label
                        )
                        reported_projected_bend = item.get("projected_bend_degrees")
                        if (
                            isinstance(reported_projected_bend, bool)
                            or not isinstance(reported_projected_bend, (int, float))
                            or not math.isfinite(float(reported_projected_bend))
                            or abs(projected_bend - float(reported_projected_bend)) > BEND_VECTOR_ANGLE_TOLERANCE_DEGREES
                            or abs(projected_bend - measured_bends[(expected_pose, joint_name)])
                            > PROJECTED_BEND_ANGLE_TOLERANCE_DEGREES
                        ):
                            raise DeepFlexionError(f"close-up visibly foreshortens the measured DEF-bone angle: {name}")
            if reference_resolution is None:
                reference_resolution = dimensions
            elif dimensions != reference_resolution:
                raise DeepFlexionError("matched render dimensions differ")

        execution = receipt.get("execution", {})
        if execution.get("return_code") != 0 or execution.get("offline") is not True or execution.get("embedded_scripts") != "disabled":
            raise DeepFlexionError("Blender execution receipt is missing successful isolated-run evidence")
        log_meta = execution.get("logs", {})
        for stream_name, expected_file in (("stdout", "blender.stdout.log"), ("stderr", "blender.stderr.log")):
            item = log_meta.get(stream_name, {})
            path = _safe_flat_child(output, item.get("path"), expected_file, item.get("sha256"), MAX_LOG_BYTES)
            if path.stat().st_size != item.get("bytes"):
                raise DeepFlexionError(f"Blender {stream_name} log byte count mismatch")
        attempt_meta = receipt.get("attempt", {})
        attempt_path = _safe_flat_child(
            output, attempt_meta.get("path"), "attempt.json", attempt_meta.get("sha256"), MAX_RECEIPT_BYTES
        )
        if attempt_path.stat().st_size != attempt_meta.get("bytes"):
            raise DeepFlexionError("attempt evidence byte count mismatch")
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        if (
            attempt.get("schema") != ATTEMPT_SCHEMA
            or attempt.get("status") != "complete"
            or attempt.get("source_sha256") != SOURCE_SHA256
            or attempt.get("return_code") != 0
            or attempt.get("observed_angles_deg") != {
                name: pose_states[name] for name in ("neutral", "right_elbow_deep", "left_knee_deep")
            }
            or attempt.get("execution", {}).get("logs") != log_meta
        ):
            raise DeepFlexionError("attempt evidence does not match the verified receipt")
        review_entry = receipt.get("review_markdown", {})
        review_path = _safe_flat_child(
            output, review_entry.get("path"), "REVIEW.md", review_entry.get("sha256"), MAX_RECEIPT_BYTES
        )
        if review_path.stat().st_size != review_entry.get("bytes"):
            raise DeepFlexionError("review markdown byte count mismatch")
        return receipt
    except DeepFlexionError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OSError, json.JSONDecodeError) as exc:
        raise DeepFlexionError(f"malformed deep-flexion receipt: {exc}") from exc


def _blender_vector_json(vector: Any, meters_per_unit: float) -> list[float]:
    return [round(float(component) * meters_per_unit, 9) for component in vector]


def _pose_bone_world(rig: Any, name: str) -> tuple[Any, Any]:
    bone = rig.pose.bones.get(name)
    if bone is None:
        raise DeepFlexionError(f"required deform bone missing: {name}")
    matrix = rig.matrix_world
    return matrix @ bone.head, matrix @ bone.tail


def _joint_state(rig: Any, region_name: str, meters_per_unit: float) -> dict[str, Any]:
    from mathutils import Vector  # type: ignore[import-not-found]

    contract = REGIONS[region_name]
    upper_name, lower_name = contract["bones"]
    upper_head, upper_tail = _pose_bone_world(rig, upper_name)
    lower_head, lower_tail = _pose_bone_world(rig, lower_name)
    upper_vector = upper_tail - upper_head
    lower_vector = lower_tail - lower_head
    if upper_vector.length <= 1e-9 or lower_vector.length <= 1e-9:
        raise DeepFlexionError(f"zero-length deform bone in {region_name}")
    cosine = max(-1.0, min(1.0, float(upper_vector.normalized().dot(lower_vector.normalized()))))
    angle = math.degrees(math.acos(cosine))
    controls = {}
    for control_name in contract["controls"]:
        control = rig.pose.bones.get(control_name)
        if control is None:
            raise DeepFlexionError(f"required FK control missing: {control_name}")
        controls[control_name] = {
            "rotation_mode": str(control.rotation_mode),
            "rotation_euler_rad": [round(float(value), 9) for value in control.rotation_euler],
        }
    switch = rig.pose.bones.get(contract["switch"])
    if switch is None or "IK_FK" not in switch:
        raise DeepFlexionError(f"required FK/IK switch missing: {contract['switch']}")
    joint_midpoint = (upper_tail + lower_head) * 0.5
    return {
        "deform_bones": [upper_name, lower_name],
        "bone_vectors_world_m": {
            upper_name: _blender_vector_json(upper_vector, meters_per_unit),
            lower_name: _blender_vector_json(lower_vector, meters_per_unit),
        },
        "joint_gap_m": round(float((upper_tail - lower_head).length) * meters_per_unit, 9),
        "joint_center_world_m": _blender_vector_json(joint_midpoint, meters_per_unit),
        "bend_degrees": round(angle, 6),
        "fk_controls": controls,
        "fk_ik_switch": {"bone": contract["switch"], "IK_FK": round(float(switch["IK_FK"]), 6)},
    }


def _reset_fk_controls(rig: Any, baselines: dict[str, list[float]]) -> None:
    for region_name, contract in REGIONS.items():
        switch = rig.pose.bones[contract["switch"]]
        switch["IK_FK"] = 1.0
        for control_name in contract["controls"]:
            control = rig.pose.bones[control_name]
            control.rotation_mode = "XYZ"
            control.rotation_euler = baselines[control_name]


def _find_deep_pose(bpy: Any, rig: Any, region_name: str, baseline: list[float], meters_per_unit: float) -> dict[str, Any]:
    contract = REGIONS[region_name]
    switch = rig.pose.bones[contract["switch"]]
    switch["IK_FK"] = 1.0
    control = rig.pose.bones[contract["controls"][1]]
    control.rotation_mode = "XYZ"
    best: tuple[int, int, list[float], float] | None = None
    max_observed = -1.0
    max_state: dict[str, Any] | None = None
    for axis in range(3):
        for sign in (1, -1):
            for degree in range(1, 181):
                candidate = list(baseline)
                candidate[axis] += sign * math.radians(degree)
                control.rotation_euler = candidate
                bpy.context.view_layer.update()
                observed = _joint_state(rig, region_name, meters_per_unit)
                angle = float(observed["bend_degrees"])
                if angle > max_observed:
                    max_observed = angle
                    max_state = {
                        "axis": axis,
                        "sign": sign,
                        "rotation_euler_rad": [round(float(value), 9) for value in candidate],
                        "bend_degrees": observed["bend_degrees"],
                    }
                if angle >= TARGET_BEND_DEGREES:
                    if best is None or degree < best[0]:
                        best = (degree, axis, candidate, angle)
                    break
    control.rotation_euler = baseline
    bpy.context.view_layer.update()
    search_record = {
        "target_degrees": TARGET_BEND_DEGREES,
        "maximum_observed_bend_degrees": round(max_observed, 6),
        "maximum_observed_control_state": max_state,
        "selected_control": contract["controls"][1],
    }
    _ATTEMPT_DETAILS.setdefault("pose_searches", {})[region_name] = search_record
    if best is None:
        raise DeepFlexionError(
            f"{region_name} FK control did not reach {TARGET_BEND_DEGREES:.1f} degrees; "
            f"maximum measured bend was {max_observed:.6f} degrees"
        )
    _, axis, rotation, _ = best
    control.rotation_euler = rotation
    bpy.context.view_layer.update()
    actual = _joint_state(rig, region_name, meters_per_unit)
    if actual["bend_degrees"] < TARGET_BEND_DEGREES:
        raise DeepFlexionError(f"{region_name} deep pose fell below the measured 90-degree target")
    search_record.update(
        {
            "selected_axis_index": axis,
            "selected_rotation_euler_rad": [round(float(value), 9) for value in rotation],
            "actual_bend_degrees": actual["bend_degrees"],
        }
    )
    control.rotation_euler = baseline
    bpy.context.view_layer.update()
    return {"control": contract["controls"][1], "rotation_euler_rad": rotation}


def _world_point(matrix: Any, point: Any, meters_per_unit: float) -> list[float]:
    return [round(float(value) * meters_per_unit, 9) for value in (matrix @ point)]


def _source_selection(body: Any) -> dict[str, Any]:
    body.data.calc_loop_triangles()
    source_triangles = [tuple(int(index) for index in tri.vertices) for tri in body.data.loop_triangles]
    groups = {group.name: group.index for group in body.vertex_groups}
    mask_group = groups.get("mhmask-preserve-volume")
    if mask_group is None:
        raise DeepFlexionError("pinned body lacks the preserve-volume mask group")
    weights_by_vertex: dict[int, dict[int, float]] = {}
    for vertex in body.data.vertices:
        weights_by_vertex[vertex.index] = {item.group: float(item.weight) for item in vertex.groups}

    result: dict[str, Any] = {}
    for name, contract in REGIONS.items():
        missing = [group for group in contract["groups"] if group not in groups]
        if missing:
            raise DeepFlexionError(f"source skin groups missing for {name}: {missing}")
        group_indices = {groups[group] for group in contract["groups"]}
        selected_ids: list[int] = []
        selected_weights: list[float] = []
        pv_weights: list[float] = []
        for vertex_index, assignments in weights_by_vertex.items():
            total = sum(assignments.get(index, 0.0) for index in group_indices)
            if total >= REGION_WEIGHT_THRESHOLD:
                selected_ids.append(vertex_index)
                selected_weights.append(round(total, 9))
                pv_weights.append(round(assignments.get(mask_group, 0.0), 9))
        selected_set = set(selected_ids)
        triangles = [
            list(triangle) for triangle in source_triangles if all(index in selected_set for index in triangle)
        ]
        if len(selected_ids) < 100 or len(triangles) < 100:
            raise DeepFlexionError(f"source-ID selected patch is too small: {name}")
        selected_weight_by_id = dict(zip(selected_ids, selected_weights))
        pv_weight_by_id = dict(zip(selected_ids, pv_weights))
        result[name] = {
            "groups": list(contract["groups"]),
            "weight_threshold": REGION_WEIGHT_THRESHOLD,
            "selected_source_vertex_ids": sorted(selected_ids),
            "selected_source_group_weight_sum": [selected_weight_by_id[index] for index in sorted(selected_ids)],
            "original_pv_mask_weights": [pv_weight_by_id[index] for index in sorted(selected_ids)],
            "source_triangle_count": len(triangles),
            "source_triangles": triangles,
        }
    return result


def _modifier_description(modifier: Any) -> dict[str, Any]:
    item: dict[str, Any] = {
        "name": modifier.name,
        "type": modifier.type,
        "show_viewport": bool(modifier.show_viewport),
        "show_render": bool(modifier.show_render),
    }
    if modifier.type == "ARMATURE":
        item.update(
            {
                "armature_object": modifier.object.name if modifier.object else None,
                "vertex_group_mask": modifier.vertex_group,
                "use_deform_preserve_volume": bool(modifier.use_deform_preserve_volume),
            }
        )
    elif modifier.type == "MASK":
        item.update(
            {
                "vertex_group": modifier.vertex_group,
                "invert_vertex_group": bool(modifier.invert_vertex_group),
            }
        )
    return item


def _create_variant(bpy: Any, source_body: Any, rig: Any, configuration: str) -> Any:
    variant = source_body.copy()
    variant.data = source_body.data.copy()
    variant.name = f"Human__deepflex_{configuration}"
    variant.data.name = f"HumanMesh__deepflex_{configuration}"
    for collection in source_body.users_collection:
        collection.objects.link(variant)
    variant.hide_render = True
    if configuration == "saved_stack":
        return variant

    source_armature = next(mod for mod in source_body.modifiers if mod.type == "ARMATURE" and mod.name == "Armature")
    source_mask = next(mod for mod in source_body.modifiers if mod.type == "MASK" and mod.name == "Hide helpers")
    mask_settings = {
        "vertex_group": source_mask.vertex_group,
        "invert_vertex_group": bool(source_mask.invert_vertex_group),
        "threshold": float(source_mask.threshold),
        "show_viewport": bool(source_mask.show_viewport),
        "show_render": bool(source_mask.show_render),
    }
    for modifier in list(variant.modifiers):
        variant.modifiers.remove(modifier)
    armature = variant.modifiers.new("Deep Flexion Single Armature", "ARMATURE")
    armature.object = rig
    armature.use_deform_preserve_volume = bool(CONFIGURATIONS[configuration]["preserve_volume"])
    armature.vertex_group = ""
    armature.invert_vertex_group = False
    armature.use_vertex_groups = bool(source_armature.use_vertex_groups)
    armature.use_bone_envelopes = bool(source_armature.use_bone_envelopes)
    armature.use_multi_modifier = False
    armature.show_viewport = True
    armature.show_render = True
    mask = variant.modifiers.new("Hide helpers", "MASK")
    for key, value in mask_settings.items():
        if hasattr(mask, key):
            setattr(mask, key, value)
    return variant


def _evaluate_patch(bpy: Any, variant: Any, region_name: str, selection: dict[str, Any], meters_per_unit: float) -> tuple[dict[str, Any], list[int]]:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = variant.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    try:
        mesh.calc_loop_triangles()
        attribute = mesh.attributes.get(SOURCE_ID_ATTRIBUTE)
        if attribute is None or attribute.domain != "POINT" or attribute.data_type != "INT":
            raise DeepFlexionError(f"evaluated source-ID attribute missing: {region_name}")
        source_ids = [int(item.value) for item in attribute.data]
        if (
            len(source_ids) != len(mesh.vertices)
            or len(set(source_ids)) != len(source_ids)
            or any(index < 0 for index in source_ids)
        ):
            raise DeepFlexionError(f"evaluated source-ID map is invalid: {region_name}")
        local_by_source = {source_id: index for index, source_id in enumerate(source_ids)}
        evaluated_triangles = {
            tuple(sorted(source_ids[index] for index in triangle.vertices)) for triangle in mesh.loop_triangles
        }
        region_selection = selection[region_name]
        if "triangles" not in region_selection:
            visible_ids = set(source_ids)
            retained_triangles = [
                triangle
                for triangle in region_selection["source_triangles"]
                if all(index in visible_ids for index in triangle)
                and tuple(sorted(triangle)) in evaluated_triangles
            ]
            retained_ids = sorted({index for triangle in retained_triangles for index in triangle})
            if len(retained_ids) < 100 or len(retained_triangles) < 100:
                raise DeepFlexionError(f"evaluated anatomical region is too small: {region_name}")
            components = _connected_component_count(retained_triangles)
            if components != 1:
                raise DeepFlexionError(
                    f"saved evaluated limb patch is disconnected: {region_name} ({components} components)"
                )
            region_selection["source_vertex_ids"] = retained_ids
            region_selection["triangles"] = retained_triangles
            region_selection["edges"] = _edge_pairs(retained_triangles)
            region_selection["connected_components"] = components
        wanted = region_selection["triangles"]
        if any(tuple(sorted(triangle)) not in evaluated_triangles for triangle in wanted):
            raise DeepFlexionError(f"selected source triangles changed under modifiers: {region_name}")
        source_vertices = region_selection["source_vertex_ids"]
        positions = [
            _world_point(evaluated.matrix_world, mesh.vertices[local_by_source[source_id]].co, meters_per_unit)
            for source_id in source_vertices
        ]
        return (
            {
                "positions_world_m": positions,
                "source_id_map_sha256": _source_id_digest(source_ids),
                "evaluated_mesh_vertices": len(mesh.vertices),
                "evaluated_mesh_triangles": len(mesh.loop_triangles),
            },
            source_ids,
        )
    finally:
        evaluated.to_mesh_clear()


def _render_png(bpy: Any, output: Path, name: str) -> dict[str, Any]:
    scene = bpy.context.scene
    path = output / name
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    result = bpy.ops.render.render(write_still=True)
    if "FINISHED" not in result or not path.is_file() or _reparse_point(path):
        raise DeepFlexionError(f"Blender did not create safe render {name}")
    size = path.stat().st_size
    if size <= 24 or size > MAX_PNG_BYTES:
        raise DeepFlexionError(f"render size is invalid: {name}")
    return {
        "path": name,
        "sha256": sha256_file(path),
        "bytes": size,
        "resolution_px": list(_png_dimensions(path)),
    }


def _render_views(
    bpy: Any,
    output: Path,
    variant: Any,
    region_name: str,
    configuration: str,
    measured_joint_state: dict[str, Any],
    meters_per_unit: float,
) -> dict[str, Any]:
    from mathutils import Vector  # type: ignore[import-not-found]
    from bpy_extras.object_utils import world_to_camera_view  # type: ignore[import-not-found]

    scene = bpy.context.scene
    base_camera = bpy.data.objects.get("ReviewCamera_front")
    if base_camera is None or base_camera.type != "CAMERA" or base_camera.data.type != "ORTHO":
        raise DeepFlexionError("pinned scene lacks the saved orthographic ReviewCamera_front")
    scene.camera = base_camera
    for item in bpy.data.objects:
        if item.type == "MESH" and (item.name == "Human" or item.name.startswith("Human__deepflex_")):
            item.hide_render = item is not variant
    variant.hide_render = False
    bpy.context.view_layer.update()
    context_name = f"{configuration}-{region_name}-context.png"
    context = _render_png(bpy, output, context_name)

    target_m = measured_joint_state["joint_center_world_m"]
    target = Vector(tuple(float(value) / meters_per_unit for value in target_m))
    profile = CLOSEUP_CAMERA_PROFILES[region_name]
    camera_name = "DeepFlexionCloseupCamera"
    close_camera = bpy.data.objects.get(camera_name)
    if close_camera is None:
        close_camera = bpy.data.objects.new(camera_name, base_camera.data.copy())
        scene.collection.objects.link(close_camera)
    close_camera.data.type = "ORTHO"
    close_camera.data.ortho_scale = profile["orthographic_scale_m"] / meters_per_unit
    label = f"{region_name} measured close-up"
    bone_plane_normal = _bone_plane_normal_world(measured_joint_state, region_name, label)
    camera_back = Vector(bone_plane_normal)
    close_camera.rotation_euler = (-camera_back).to_track_quat("-Z", "Y").to_euler()
    direction = close_camera.rotation_euler.to_matrix() @ Vector((0.0, 0.0, -1.0))
    close_camera.location = target - direction * 5.0
    scene.camera = close_camera
    bpy.context.view_layer.update()
    projected = world_to_camera_view(scene, close_camera, target)
    joint_projection = [round(float(projected.x), 6), round(float(projected.y), 6)]
    view_matrix = close_camera.matrix_world.inverted()
    view_matrix_payload = [
        [round(float(view_matrix[row][column]), 9) for column in range(4)]
        for row in range(4)
    ]
    saved_front_matrix = base_camera.matrix_world.inverted()
    saved_front_matrix_payload = [
        [round(float(saved_front_matrix[row][column]), 9) for column in range(4)]
        for row in range(4)
    ]
    camera_back_alignment = _camera_plane_alignment(
        view_matrix_payload, measured_joint_state, region_name, label
    )
    if camera_back_alignment < BONE_PLANE_CAMERA_ALIGNMENT_MIN:
        raise DeepFlexionError(f"{region_name} close-up camera failed to align with its measured DEF-bone plane")
    projected_bone_vectors = _projected_bone_vectors_camera(
        view_matrix_payload, measured_joint_state, region_name, label
    )
    projected_bend = _projected_bend_degrees_from_view_matrix(
        view_matrix_payload, measured_joint_state, region_name, label
    )
    measured_bend = float(measured_joint_state["bend_degrees"])
    if abs(projected_bend - measured_bend) > PROJECTED_BEND_ANGLE_TOLERANCE_DEGREES:
        raise DeepFlexionError(f"{region_name} close-up foreshortens its measured DEF-bone angle")
    yaw_delta = _camera_yaw_delta_degrees(saved_front_matrix_payload, view_matrix_payload)
    bounds = JOINT_CLOSEUP_CENTRAL_CROP_BOUNDS
    if not (bounds[0] <= joint_projection[0] <= bounds[2] and bounds[1] <= joint_projection[1] <= bounds[3]):
        raise DeepFlexionError(f"measured {region_name} joint projects outside the central close-up crop")
    close_name = f"{configuration}-{region_name}-closeup.png"
    closeup = _render_png(bpy, output, close_name)
    scene.camera = base_camera
    return {
        context_name: {**context, "view": "full_body_context", "camera": "ReviewCamera_front"},
        close_name: {
            **closeup,
            "view": "matched_joint_closeup",
            "camera": camera_name,
            "target_world_m": [round(float(value), 9) for value in target_m],
            "joint_projection_normalized": joint_projection,
            "central_crop_bounds_normalized": list(bounds),
            "camera_profile": profile["name"],
            "camera_direction_mode": profile["direction_mode"],
            "yaw_relative_to_saved_front_degrees": round(yaw_delta, 6),
            "camera_view_matrix_world_to_camera": view_matrix_payload,
            "bone_plane_normal_world": [round(value, 9) for value in bone_plane_normal],
            "bone_plane_camera_alignment": round(camera_back_alignment, 9),
            "projected_bone_vectors_camera": projected_bone_vectors,
            "projected_bend_degrees": round(projected_bend, 6),
            "orthographic_scale_m": profile["orthographic_scale_m"],
        },
    }


def _render_review_markdown(receipt: dict[str, Any]) -> str:
    lines = [
        "# T5a.5 deep-flexion skinning comparison",
        "",
        "Status: diagnostic-only review evidence. Generic source rig; no fighter-art, production, or T5b approval.",
        "",
        f"Source SHA-256: `{SOURCE_SHA256}`. Blender: `{SUPPORTED_BLENDER_VERSION}` (`{SUPPORTED_BLENDER_BUILD_HASH}`), offline with embedded scripts disabled.",
        "",
        "## Measured pose bends",
        "",
        "Angles use evaluated world-space DEF bone vectors (upper arm→forearm and thigh→shin). Control Euler values are recorded as authoring state, not used as the angle measurement.",
        "Joint close-up views are aligned to the measured DEF-bone plane; the receipt recomputes projected vector directions and bend angles to reject foreshortened crops.",
        "",
        "| Pose | Right elbow | Left knee |",
        "| --- | ---: | ---: |",
    ]
    for pose in ("neutral", "right_elbow_deep", "left_knee_deep"):
        state = receipt["pose_states"][pose]
        lines.append(
            f"| {pose} | {state['right_elbow']['bend_degrees']:.3f}° | {state['left_knee']['bend_degrees']:.3f}° |"
        )
    lines.extend(["", "## Matched joint close-ups", ""])
    lines.append("| Joint | Camera profile | Measured angle | Projected angle | Camera-plane alignment | Relative yaw |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")
    for joint_name in REGIONS:
        pose_name = "right_elbow_deep" if joint_name == "right_elbow" else "left_knee_deep"
        render = receipt["renders"][f"saved_stack-{joint_name}-closeup.png"]
        state = receipt["pose_states"][pose_name][joint_name]
        lines.append(
            f"| {joint_name} | {render['camera_profile']} | {state['bend_degrees']:.3f}° | "
            f"{render['projected_bend_degrees']:.3f}° | {render['bone_plane_camera_alignment']:.6f} | "
            f"{render['yaw_relative_to_saved_front_degrees']:.3f}° |"
        )
    lines.extend(
        [
            "",
            "## Local distortion measurements",
            "",
            "Ratios compare each configuration's deep pose with its own neutral pose. Values describe the selected open surface patches; no volume was measured.",
            "",
            "| Joint | Configuration | Area ratio min / p05 / median / p95 / max | Edge ratio min / p05 / median / p95 / max | Degenerate triangles / edges |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for joint in REGIONS:
        for configuration in CONFIGURATIONS:
            metrics = receipt["regions"][joint]["measurements"][configuration]["deep_flexion"]
            area = metrics["triangle_area_ratio"]
            edge = metrics["edge_length_ratio"]
            lines.append(
                f"| {joint} | {configuration} | {area['min']:.4f} / {area['p05']:.4f} / {area['p50']:.4f} / {area['p95']:.4f} / {area['max']:.4f} | "
                f"{edge['min']:.4f} / {edge['p05']:.4f} / {edge['p50']:.4f} / {edge['p95']:.4f} / {edge['max']:.4f} | "
                f"{metrics['degenerate_triangle_count']} / {metrics['degenerate_edge_count']} |"
            )
    lines.extend(
        [
            "",
            "The saved `mhmask-preserve-volume` vertex group has zero positive weights on both measured limb patches. The single preserve-volume comparison is unmasked to exercise that modifier on the patch. This does not establish a universal DQS guarantee or visual-quality verdict.",
            "",
        "Render filenames pair each configuration and joint pose: `*-context.png` uses the saved front camera; matched joint close-ups center the measured DEF-bone joint and view along its measured bone-plane normal. Elbow and knee use 0.90 m and 1.20 m orthographic crops, respectively.",
            "",
        ]
    )
    return "\n".join(lines)


def _run_in_blender(source: Path, output: Path) -> dict[str, Any]:
    import bpy  # type: ignore[import-not-found]

    source = Path(source).resolve(strict=True)
    output = Path(output).resolve(strict=True)
    expected_source = (ROOT / SOURCE_RELATIVE).resolve(strict=True)
    expected_review_root = (ROOT / REVIEW_RELATIVE).resolve(strict=True)
    if source != expected_source or output.parent != expected_review_root:
        raise DeepFlexionError("worker accepts only the pinned source and direct quarantine child")
    if _path_chain_has_reparse(output) or _path_chain_has_reparse(expected_review_root):
        raise DeepFlexionError("source or review path contains a symlink/junction")
    if bpy.app.version_string != SUPPORTED_BLENDER_VERSION:
        raise DeepFlexionError(f"expected Blender {SUPPORTED_BLENDER_VERSION}, received {bpy.app.version_string}")
    build_hash = bpy.app.build_hash
    if isinstance(build_hash, bytes):
        build_hash = build_hash.decode("ascii", errors="replace")
    if build_hash != SUPPORTED_BLENDER_BUILD_HASH:
        raise DeepFlexionError("Blender build hash differs from the pinned benchmark")
    _assert_pinned_source(source)
    before_hash = sha256_file(source)
    result = bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    if "FINISHED" not in result:
        raise DeepFlexionError("Blender did not finish opening the pinned source")
    _assert_pinned_source(source)

    scene = bpy.context.scene
    body = bpy.data.objects.get("Human")
    rig = bpy.data.objects.get("Human.rigify")
    if body is None or body.type != "MESH" or body.parent is not rig or rig is None or rig.type != "ARMATURE":
        raise DeepFlexionError("pinned scene lacks the expected parented Human body and Rigify armature")
    if scene.unit_settings.scale_length != 1.0:
        raise DeepFlexionError("pinned scene is not in meter scale")
    meters_per_unit = float(scene.unit_settings.scale_length)
    action = rig.animation_data.action if rig.animation_data and rig.animation_data.action else None
    action_name = action.name if action else None
    if action_name != "Human.rigifyAction" or len(body.data.vertices) != 19158 or len(rig.data.bones) != 930:
        raise DeepFlexionError("pinned body/rig/action inventory differs from the reviewed source contract")
    source_modifiers = [_modifier_description(modifier) for modifier in body.modifiers]
    if [item["name"] for item in source_modifiers] != ["Armature", "Armature PV", "Hide helpers"]:
        raise DeepFlexionError("saved source modifier stack changed")
    if body.data.attributes.get(SOURCE_ID_ATTRIBUTE) is not None:
        raise DeepFlexionError("reserved source-ID mesh attribute already exists")

    scene.frame_set(1)
    bpy.context.view_layer.update()
    # Freeze the saved frame-1 rig state so deep-pose edits are not overwritten by action evaluation.
    saved_action = action
    if rig.animation_data is not None:
        rig.animation_data.action = None
    bpy.context.view_layer.update()
    baseline_rotations: dict[str, list[float]] = {}
    for contract in REGIONS.values():
        switch = rig.pose.bones.get(contract["switch"])
        if switch is None or "IK_FK" not in switch:
            raise DeepFlexionError(f"required Rigify FK/IK switch missing: {contract['switch']}")
        for control_name in contract["controls"]:
            control = rig.pose.bones.get(control_name)
            if control is None:
                raise DeepFlexionError(f"required Rigify FK control missing: {control_name}")
            control.rotation_mode = "XYZ"
            baseline_rotations[control_name] = [float(value) for value in control.rotation_euler]
    _reset_fk_controls(rig, baseline_rotations)
    bpy.context.view_layer.update()
    neutral_state = {name: _joint_state(rig, name, meters_per_unit) for name in REGIONS}

    deep_rotations: dict[str, dict[str, Any]] = {}
    for region_name in REGIONS:
        deep_rotations[region_name] = _find_deep_pose(
            bpy, rig, region_name, baseline_rotations[REGIONS[region_name]["controls"][1]], meters_per_unit
        )

    pose_states: dict[str, Any] = {"neutral": neutral_state}
    for region_name, pose_name in (("right_elbow", "right_elbow_deep"), ("left_knee", "left_knee_deep")):
        _reset_fk_controls(rig, baseline_rotations)
        control = rig.pose.bones[deep_rotations[region_name]["control"]]
        control.rotation_euler = deep_rotations[region_name]["rotation_euler_rad"]
        bpy.context.view_layer.update()
        pose_states[pose_name] = {name: _joint_state(rig, name, meters_per_unit) for name in REGIONS}
        if pose_states[pose_name][region_name]["bend_degrees"] < TARGET_BEND_DEGREES:
            raise DeepFlexionError(f"reconstructed {region_name} pose missed the 90-degree target")
    _reset_fk_controls(rig, baseline_rotations)
    bpy.context.view_layer.update()

    selection = _source_selection(body)
    attribute = body.data.attributes.new(name=SOURCE_ID_ATTRIBUTE, type="INT", domain="POINT")
    for index, datum in enumerate(attribute.data):
        datum.value = index
    bpy.context.view_layer.update()

    body.hide_render = True
    variants = {
        name: _create_variant(bpy, body, rig, name)
        for name in CONFIGURATIONS
    }
    geometry: dict[str, Any] = {
        "schema": GEOMETRY_SCHEMA,
        "source_sha256": SOURCE_SHA256,
        "source_vertex_count": len(body.data.vertices),
        "evaluated_topology": {name: {} for name in CONFIGURATIONS},
        "regions": {},
    }
    for region_name, source_region in selection.items():
        geometry["regions"][region_name] = {
            **source_region,
            "samples": {name: {} for name in CONFIGURATIONS},
        }
    renders: dict[str, Any] = {}
    for configuration, variant in variants.items():
        for item in variants.values():
            item.hide_render = item is not variant
        for region_name in REGIONS:
            _reset_fk_controls(rig, baseline_rotations)
            bpy.context.view_layer.update()
            for sample_pose in POSE_KEYS:
                if sample_pose == "deep_flexion":
                    control = rig.pose.bones[deep_rotations[region_name]["control"]]
                    control.rotation_euler = deep_rotations[region_name]["rotation_euler_rad"]
                    bpy.context.view_layer.update()
                measurements, source_ids = _evaluate_patch(
                    bpy, variant, region_name, selection, meters_per_unit
                )
                topologies = geometry["evaluated_topology"][configuration]
                topology = {
                    "source_vertex_ids": source_ids,
                    "source_id_map_sha256": measurements["source_id_map_sha256"],
                    "evaluated_mesh_vertices": measurements["evaluated_mesh_vertices"],
                    "evaluated_mesh_triangles": measurements["evaluated_mesh_triangles"],
                }
                previous = topologies.get(sample_pose)
                if previous is not None and previous != topology:
                    raise DeepFlexionError("evaluated topology changed between the elbow and knee pose")
                topologies[sample_pose] = topology
                geometry["regions"][region_name]["samples"][configuration][sample_pose] = measurements
            _reset_fk_controls(rig, baseline_rotations)
            control = rig.pose.bones[deep_rotations[region_name]["control"]]
            control.rotation_euler = deep_rotations[region_name]["rotation_euler_rad"]
            bpy.context.view_layer.update()
            measured_pose_name = "right_elbow_deep" if region_name == "right_elbow" else "left_knee_deep"
            renders.update(
                _render_views(
                    bpy,
                    output,
                    variant,
                    region_name,
                    configuration,
                    pose_states[measured_pose_name][region_name],
                    meters_per_unit,
                )
            )
            _reset_fk_controls(rig, baseline_rotations)
            bpy.context.view_layer.update()

    for region_name, raw_region in geometry["regions"].items():
        finalized = selection[region_name]
        raw_region.pop("source_triangles", None)
        raw_region.update(
            {
                "source_vertex_ids": finalized["source_vertex_ids"],
                "triangles": finalized["triangles"],
                "edges": finalized["edges"],
                "connected_components": finalized["connected_components"],
            }
        )
    geometry_path = output / "geometry.json"
    _write_json(geometry_path, geometry)
    if geometry_path.stat().st_size > MAX_GEOMETRY_BYTES:
        raise DeepFlexionError("raw source-ID geometry exceeds the size limit")
    regions = {}
    for region_name, raw_region in geometry["regions"].items():
        selected_weights = raw_region["selected_source_group_weight_sum"]
        pv_weights = raw_region["original_pv_mask_weights"]
        regions[region_name] = {
            "selection": {
                "groups": raw_region["groups"],
                "weight_threshold": raw_region["weight_threshold"],
                "source_vertex_count": len(raw_region["selected_source_vertex_ids"]),
                "measured_vertex_count": len(raw_region["source_vertex_ids"]),
                "triangle_count": len(raw_region["triangles"]),
                "edge_count": len(raw_region["edges"]),
                "connected_components": raw_region["connected_components"],
            },
            "skin_group_weight_sum": _mask_summary(selected_weights),
            "original_pv_mask_coverage": _mask_summary(pv_weights),
            "measurements": _metrics_for_region(raw_region),
        }
    body_inventory = {
        "object": body.name_full,
        "stored_vertices": len(body.data.vertices),
        "saved_modifiers": source_modifiers,
        "skin_group_count": len(body.vertex_groups),
    }
    pose_states = {
        name: {
            region_name: state[region_name]
            for region_name in REGIONS
        }
        for name, state in pose_states.items()
    }
    source_after = sha256_file(source)
    if before_hash != SOURCE_SHA256 or source_after != SOURCE_SHA256:
        raise DeepFlexionError("pinned source SHA changed before, during, or after evaluation")
    receipt = {
        "schema": SCHEMA,
        "status": "diagnostic_only",
        "verdict": "diagnostic_only",
        "scope": "in-memory FK joint-flexion measurement on the saved generic Rigify body",
        "source": {
            "path": SOURCE_RELATIVE,
            "sha256_before": before_hash,
            "sha256_after": source_after,
            "mutated": False,
        },
        "tool": {
            "name": "Blender",
            "version": bpy.app.version_string,
            "build_hash": build_hash,
            "network": "offline",
            "embedded_scripts": "disabled",
            "factory_startup": True,
            "isolated_user_resources": True,
        },
        "inventory": {
            "body": body_inventory,
            "rig": {
                "object": rig.name_full,
                "bone_count": len(rig.data.bones),
                "saved_action": saved_action.name if saved_action else None,
                "action_muted_in_memory": True,
                "required_deform_bones_present": all(
                    rig.pose.bones.get(bone) is not None
                    for contract in REGIONS.values() for bone in contract["bones"]
                ),
            },
            "camera": {
                "name": "ReviewCamera_front",
                "projection": "ORTHO",
                "resolution_px": [int(scene.render.resolution_x), int(scene.render.resolution_y)],
                "resolution_percentage": int(scene.render.resolution_percentage),
                "render_engine": str(scene.render.engine),
                "orthographic_scale_m": round(float(bpy.data.objects["ReviewCamera_front"].data.ortho_scale), 9),
                "view_matrix_world_to_camera": [
                    [
                        round(float(bpy.data.objects["ReviewCamera_front"].matrix_world.inverted()[row][column]), 9)
                        for column in range(4)
                    ]
                    for row in range(4)
                ],
            },
        },
        "target_bend_degrees": TARGET_BEND_DEGREES,
        "pose_states": pose_states,
        "deep_pose_authoring": {
            region_name: {
                "target": TARGET_BEND_DEGREES,
                "selected_control": deep_rotations[region_name]["control"],
                "selected_rotation_euler_rad": [
                    round(float(value), 9) for value in deep_rotations[region_name]["rotation_euler_rad"]
                ],
                "measured_bend_degrees": pose_states[
                    "right_elbow_deep" if region_name == "right_elbow" else "left_knee_deep"
                ][region_name]["bend_degrees"],
            }
            for region_name in REGIONS
        },
        "modifier_configurations": {
            name: {
                **config,
                "stack": [_modifier_description(modifier) for modifier in variant.modifiers],
            }
            for name, config in CONFIGURATIONS.items()
            for variant in (variants[name],)
        },
        "thresholds": {
            "source_region_weight_inclusive_min": REGION_WEIGHT_THRESHOLD,
            "deep_bend_degrees_inclusive_min": TARGET_BEND_DEGREES,
            "degenerate_triangle_area_m2_inclusive_max": DEGENERATE_TRIANGLE_AREA_M2,
            "degenerate_edge_length_m_inclusive_max": DEGENERATE_EDGE_LENGTH_M,
            "distortion_quantiles": list(DISTORTION_QUANTILES),
            "quality_pass_threshold": None,
        },
        "regions": regions,
        "renders": renders,
        "raw_geometry": {
            "path": geometry_path.name,
            "sha256": sha256_file(geometry_path),
            "bytes": geometry_path.stat().st_size,
        },
        "volume_measurement": "not measured: selected limb patches are open surfaces, not enclosed volumes",
        "limitations": [
            "generic diagnostic body; no fighter likeness or finished-art verdict",
            "original preserve-volume vertex group has no positive weights on either selected limb patch",
            "the single preserve-volume comparison is unmasked to exercise that modifier on the selected patch",
            "area and edge ratios describe selected source-topology patches only; they are not whole-body volume claims",
            "rendered images require human visual review; no automatic quality threshold is defined",
            "no fighter choreography, T5b, HG2, production or operator art approval claim",
        ],
    }
    review_path = output / "REVIEW.md"
    review_path.write_text(_render_review_markdown(receipt), encoding="utf-8", newline="\n")
    receipt["review_markdown"] = {
        "path": review_path.name,
        "sha256": sha256_file(review_path),
        "bytes": review_path.stat().st_size,
    }
    receipt_path = output / "receipt.json"
    _write_json(receipt_path, receipt)
    if receipt_path.stat().st_size > MAX_RECEIPT_BYTES:
        raise DeepFlexionError("deep-flexion receipt exceeds the size limit")
    return receipt


def _attempt_payload(output: Path, error: Exception) -> dict[str, Any]:
    return {
        "schema": ATTEMPT_SCHEMA,
        "status": "failed",
        "error": f"{type(error).__name__}: {error}",
        "source_sha256": SOURCE_SHA256,
        "target_bend_degrees": TARGET_BEND_DEGREES,
        "pose_searches": _ATTEMPT_DETAILS.get("pose_searches", {}),
        "artifacts_written": sorted(path.name for path in output.iterdir() if path.is_file()),
    }


def blender_main(argv: list[str] | None = None) -> int:
    import argparse

    args_vector = list(sys.argv if argv is None else argv)
    args_vector = args_vector[args_vector.index("--") + 1 :] if "--" in args_vector else args_vector
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(args_vector)
    output = Path(args.output)
    try:
        _run_in_blender(Path(args.source), output)
        return 0
    except Exception as exc:
        try:
            resolved = output.resolve(strict=True)
            expected_root = (ROOT / REVIEW_RELATIVE).resolve(strict=True)
            if resolved.parent == expected_root and not _path_chain_has_reparse(resolved):
                _write_json(resolved / "attempt.json", _attempt_payload(resolved, exc))
        except Exception:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(blender_main())
