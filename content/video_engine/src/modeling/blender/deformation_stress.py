"""Review-only stress measurements for the pinned native Rigify body mesh.

Run this module inside Blender through ``model_deformation_stress.py``.  It
opens the saved source with embedded scripts disabled, measures the saved
modifier stack at three authored frames, and never saves the source scene.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import struct
import stat
import sys
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[5]
SOURCE_RELATIVE = "content/video_engine/assets/modeling/native/fighter-family-v1.1.blend"
SOURCE_SHA256 = "5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade"
REVIEW_RELATIVE = "content/video_engine/review/model-engines/benchmark-v1/3d/deformation-stress"
SUPPORTED_BLENDER_VERSION = "5.2.2 LTS"
SUPPORTED_BLENDER_BUILD_HASH = "d13f752e3b9c"
SCHEMA = "model_deformation_stress.v1"
GEOMETRY_SCHEMA = "model_deformation_stress_geometry.v1"
FRAME_NUMBERS = (1, 27, 52)
FRAME_LABELS = {1: "neutral", 27: "arm_stress", 52: "hip_leg_stress"}
REGION_WEIGHT_THRESHOLD = 0.10
DEGENERATE_TRIANGLE_AREA_M2 = 1e-12
DEGENERATE_EDGE_LENGTH_M = 1e-9
DISTORTION_QUANTILES = (0.0, 0.05, 0.50, 0.95, 1.0)
MAX_RECEIPT_BYTES = 2_000_000
MAX_GEOMETRY_BYTES = 16_000_000
MAX_PNG_BYTES = 20_000_000
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_RUN_NAME = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_SOURCE_ID_ATTRIBUTE = "deformation_stress_source_vertex_id"

REGIONS: dict[str, dict[str, Any]] = {
    "shoulder_elbow": {
        "label": "right shoulder through elbow",
        "side": "R",
        "groups": (
            "DEF-shoulder.R",
            "DEF-shoulder-helper.R",
            "DEF-upper_arm.R",
            "DEF-upper_arm.R.001",
            "DEF-forearm.R",
            "DEF-forearm.R.001",
            "DEF-elbow-helper.R",
        ),
        "stress_frame": 27,
    },
    "hip_knee": {
        "label": "left hip through knee",
        "side": "L",
        "groups": (
            "DEF-pelvis-helper.L",
            "DEF-pelvis-helper.front.L",
            "DEF-thigh.L",
            "DEF-thigh.L.001",
            "DEF-shin.L",
            "DEF-shin.L.001",
            "DEF-knee-helper.L",
        ),
        "stress_frame": 52,
    },
}


class DeformationStressError(RuntimeError):
    """The pinned Blender deformation diagnostic could not be verified."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _assert_source_integrity(path: Path, expected_sha256: str) -> None:
    if not path.is_file() or _reparse_point(path):
        raise DeformationStressError("pinned source is missing or redirected")
    if sha256_file(path) != expected_sha256:
        raise DeformationStressError("pinned source hash does not match its expected digest")


def _round_float(value: Any, label: str, digits: int = 9) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DeformationStressError(f"invalid numeric value: {label}")
    result = float(value)
    if not math.isfinite(result):
        raise DeformationStressError(f"non-finite numeric value: {label}")
    return round(result, digits)


def _quantile_summary(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        raise DeformationStressError("cannot summarize an empty distortion sample")
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) for value in ordered):
        raise DeformationStressError("distortion sample contains a non-finite value")

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
    points = list(points)
    if not points:
        raise DeformationStressError("region has no measured vertices")
    return {
        "min": [round(min(float(point[axis]) for point in points), 9) for axis in range(3)],
        "max": [round(max(float(point[axis]) for point in points), 9) for axis in range(3)],
    }


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


def _edge_pairs(triangles: Sequence[Sequence[int]]) -> list[list[int]]:
    edges: set[tuple[int, int]] = set()
    for triangle in triangles:
        a, b, c = (int(value) for value in triangle)
        edges.update((tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((c, a)))))
    return [list(edge) for edge in sorted(edges)]


def _region_measurements(raw_region: dict[str, Any]) -> dict[str, Any]:
    vertex_ids = [int(value) for value in raw_region["measured_vertex_indices"]]
    triangles = [[int(value) for value in tri] for tri in raw_region["triangles"]]
    edges = [[int(value) for value in edge] for edge in raw_region["edges"]]
    frames = raw_region["frames"]
    coordinates: dict[str, dict[int, list[float]]] = {}
    for frame_text in ("1", "27", "52"):
        frame = frames[frame_text]
        points = frame["positions_world_m"]
        if len(points) != len(vertex_ids):
            raise DeformationStressError(f"raw vertex count mismatch at frame {frame_text}")
        coordinates[frame_text] = {
            vertex_id: [_round_float(value, f"frame {frame_text} coordinate") for value in point]
            for vertex_id, point in zip(vertex_ids, points)
        }

    baseline = coordinates["1"]
    base_triangle_areas = [
        _triangle_area(*(baseline[index] for index in tri)) for tri in triangles
    ]
    base_edge_lengths = [
        _distance(baseline[a], baseline[b]) for a, b in edges
    ]
    valid_triangle_indices = [
        index for index, area in enumerate(base_triangle_areas)
        if area > DEGENERATE_TRIANGLE_AREA_M2
    ]
    valid_edge_indices = [
        index for index, length in enumerate(base_edge_lengths)
        if length > DEGENERATE_EDGE_LENGTH_M
    ]
    if not valid_triangle_indices or not valid_edge_indices:
        raise DeformationStressError("neutral region has no non-degenerate triangle/edge samples")
    neutral_total_area = sum(base_triangle_areas)
    if neutral_total_area <= 0.0:
        raise DeformationStressError("neutral region area is zero")

    result: dict[str, Any] = {}
    for frame_text in ("1", "27", "52"):
        current = coordinates[frame_text]
        areas = [_triangle_area(*(current[index] for index in tri)) for tri in triangles]
        lengths = [_distance(current[a], current[b]) for a, b in edges]
        area_ratios = [areas[index] / base_triangle_areas[index] for index in valid_triangle_indices]
        edge_ratios = [lengths[index] / base_edge_lengths[index] for index in valid_edge_indices]
        if any(not math.isfinite(value) for value in area_ratios + edge_ratios):
            raise DeformationStressError(f"non-finite deformation ratio at frame {frame_text}")
        points = list(current.values())
        result[frame_text] = {
            "label": FRAME_LABELS[int(frame_text)],
            "evaluated_mesh_vertices": int(frames[frame_text]["evaluated_mesh_vertices"]),
            "evaluated_mesh_triangles": int(frames[frame_text]["evaluated_mesh_triangles"]),
            "source_id_map_sha256": str(frames[frame_text]["source_id_map_sha256"]),
            "retained_region_vertices": len(vertex_ids),
            "retained_region_triangles": len(triangles),
            "bounds_world_m": _bounds(points),
            "triangle_area_total_m2": round(sum(areas), 9),
            "triangle_area_total_ratio_to_frame_1": round(sum(areas) / neutral_total_area, 9),
            "degenerate_triangle_count": sum(area <= DEGENERATE_TRIANGLE_AREA_M2 for area in areas),
            "neutral_degenerate_triangle_count": sum(
                area <= DEGENERATE_TRIANGLE_AREA_M2 for area in base_triangle_areas
            ),
            "triangle_area_ratio": _quantile_summary(area_ratios),
            "triangle_area_relative_change": _quantile_summary(value - 1.0 for value in area_ratios),
            "edge_length_ratio": _quantile_summary(edge_ratios),
            "edge_length_relative_change": _quantile_summary(value - 1.0 for value in edge_ratios),
            "degenerate_edge_count": sum(length <= DEGENERATE_EDGE_LENGTH_M for length in lengths),
            "neutral_degenerate_edge_count": sum(
                length <= DEGENERATE_EDGE_LENGTH_M for length in base_edge_lengths
            ),
        }
    return result


def _mask_stats(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        raise DeformationStressError("cannot summarize an empty vertex-group selection")
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) for value in ordered):
        raise DeformationStressError("vertex-group weights contain non-finite values")
    return {
        "count": len(ordered),
        "positive_count": sum(value > 0.0 for value in ordered),
        "min": round(ordered[0], 9),
        "p25": round(ordered[round((len(ordered) - 1) * 0.25)], 9),
        "p50": round(ordered[round((len(ordered) - 1) * 0.50)], 9),
        "p75": round(ordered[round((len(ordered) - 1) * 0.75)], 9),
        "p95": round(ordered[round((len(ordered) - 1) * 0.95)], 9),
        "mean": round(sum(ordered) / len(ordered), 9),
        "max": round(ordered[-1], 9),
    }


def _source_id_digest(values: Sequence[int]) -> str:
    encoded = json.dumps([int(value) for value in values], separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def _reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(attributes & reparse_flag)


def _assert_flat_child(output: Path, name: Any, expected_name: str, digest: Any, max_bytes: int) -> Path:
    if name != expected_name or Path(str(name)).name != expected_name:
        raise DeformationStressError(f"invalid artifact path: {expected_name}")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise DeformationStressError(f"invalid artifact digest: {expected_name}")
    output_resolved = output.resolve(strict=True)
    if _reparse_point(output):
        raise DeformationStressError("output directory is a symlink or reparse point")
    path = output / expected_name
    if not path.is_file() or _reparse_point(path):
        raise DeformationStressError(f"missing or unsafe artifact: {expected_name}")
    if path.resolve(strict=True).parent != output_resolved:
        raise DeformationStressError(f"artifact escapes output directory: {expected_name}")
    if path.stat().st_size > max_bytes:
        raise DeformationStressError(f"oversized artifact: {expected_name}")
    if sha256_file(path) != digest:
        raise DeformationStressError(f"artifact digest mismatch: {expected_name}")
    return path


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise DeformationStressError(f"invalid PNG header: {path.name}")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise DeformationStressError(f"invalid PNG dimensions: {path.name}")
    return width, height


def validate_receipt(
    receipt: Any,
    output: Path,
    *,
    review_root: Path | None = None,
) -> dict[str, Any]:
    """Reopen artifact bytes and recompute region metrics before trusting a receipt."""
    try:
        output = Path(output)
        if not output.is_dir() or _reparse_point(output):
            raise DeformationStressError("review output is missing or unsafe")
        if review_root is not None:
            root = Path(review_root).resolve(strict=True)
            resolved = output.resolve(strict=True)
            if resolved.parent != root or _reparse_point(Path(review_root)):
                raise DeformationStressError("review run is outside the allowed quarantine")
        if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
            raise DeformationStressError("invalid receipt schema")
        if receipt.get("status") != "diagnostic_only" or receipt.get("verdict") != "diagnostic_only":
            raise DeformationStressError("receipt must remain a diagnostic-only verdict")

        source = receipt["source"]
        if source != {
            "path": SOURCE_RELATIVE,
            "sha256_before": SOURCE_SHA256,
            "sha256_after": SOURCE_SHA256,
            "mutated": False,
        }:
            raise DeformationStressError("receipt source does not match the pinned read-only input")
        _assert_source_integrity(ROOT / SOURCE_RELATIVE, SOURCE_SHA256)
        tool = receipt["tool"]
        if (
            tool.get("name") != "Blender"
            or tool.get("version") != SUPPORTED_BLENDER_VERSION
            or tool.get("build_hash") != SUPPORTED_BLENDER_BUILD_HASH
            or tool.get("network") != "offline"
            or tool.get("embedded_scripts") != "disabled"
        ):
            raise DeformationStressError("receipt does not confirm pinned offline Blender 5.2.2")
        inventory = receipt["inventory"]
        body_inventory = inventory["body"]
        rig_inventory = inventory["rig"]
        expected_modifiers = [
            ("Armature", "ARMATURE", False, ""),
            ("Armature PV", "ARMATURE", True, "mhmask-preserve-volume"),
            ("Hide helpers", "MASK", None, None),
        ]
        actual_modifiers = [
            (
                item["name"],
                item["type"],
                item.get("use_deform_preserve_volume"),
                item.get("vertex_group_mask"),
            )
            for item in body_inventory["modifiers_in_stack_order"]
        ]
        if (
            body_inventory["object"] != "Human"
            or body_inventory["stored_vertices"] != 19158
            or rig_inventory["object"] != "Human.rigify"
            or rig_inventory["bone_count"] != 930
            or "Human.rigifyAction" not in rig_inventory["active_actions"]
            or actual_modifiers != expected_modifiers
        ):
            raise DeformationStressError("scene/rig/body inventory differs from the pinned source contract")
        if not isinstance(body_inventory["skin_groups"], list) or not body_inventory["skin_groups"]:
            raise DeformationStressError("receipt is missing the body skin-group inventory")
        if receipt["frames"] != [
            {"frame": frame, "label": FRAME_LABELS[frame]} for frame in FRAME_NUMBERS
        ]:
            raise DeformationStressError("receipt sample frames changed")
        if receipt["thresholds"] != {
            "region_weight_sum_inclusive_min": REGION_WEIGHT_THRESHOLD,
            "degenerate_triangle_area_m2_inclusive_max": DEGENERATE_TRIANGLE_AREA_M2,
            "degenerate_edge_length_m_inclusive_max": DEGENERATE_EDGE_LENGTH_M,
            "quality_pass_threshold": None,
            "distortion_quantiles": [0.0, 0.05, 0.5, 0.95, 1.0],
        }:
            raise DeformationStressError("receipt numeric selection/degeneracy thresholds changed")
        if receipt["volume_measurement"] != "not measured: an open selected surface patch is not a closed volume":
            raise DeformationStressError("receipt volume boundary changed")
        if receipt["configuration_comparison"] != (
            "not run: the saved arm/leg PV mask has zero positive weights in both measured regions; "
            "no LBS-versus-DQS or PV-benefit inference is made"
        ):
            raise DeformationStressError("receipt configuration-comparison caveat changed")
        pv_inventory = receipt["preserve_volume_mask_distribution"]
        if (
            pv_inventory["group"] != "mhmask-preserve-volume"
            or pv_inventory["source_positive_vertex_count"] != 2880
            or pv_inventory["evaluated_visible_vertex_count"] != 2880
            or not pv_inventory["top_deform_groups_by_mask_weighted_support"]
        ):
            raise DeformationStressError("receipt PV-mask inventory is incomplete")

        geometry_entry = receipt["raw_geometry"]
        geometry_path = _assert_flat_child(
            output, geometry_entry["path"], "geometry.json", geometry_entry["sha256"], MAX_GEOMETRY_BYTES
        )
        if geometry_path.stat().st_size != geometry_entry["bytes"]:
            raise DeformationStressError("raw geometry byte count mismatch")
        geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
        if geometry.get("schema") != GEOMETRY_SCHEMA or geometry.get("source_sha256") != SOURCE_SHA256:
            raise DeformationStressError("invalid raw geometry receipt")
        source_vertex_count = geometry["source_vertex_count"]
        if (
            type(source_vertex_count) is not int
            or source_vertex_count <= 0
            or source_vertex_count != body_inventory["stored_vertices"]
        ):
            raise DeformationStressError("invalid raw source vertex count")
        evaluated_ids = geometry["evaluated_source_vertex_ids"]
        expected_id_frames = {str(frame) for frame in FRAME_NUMBERS}
        if set(evaluated_ids) != expected_id_frames:
            raise DeformationStressError("evaluated source-index map is missing a sample frame")
        normalized_id_maps: dict[str, list[int]] = {}
        for frame_text, values in evaluated_ids.items():
            if (
                not isinstance(values, list)
                or not values
                or any(type(value) is not int or value < 0 or value >= source_vertex_count for value in values)
                or len(set(values)) != len(values)
            ):
                raise DeformationStressError(f"invalid evaluated source-index map at frame {frame_text}")
            normalized_id_maps[frame_text] = values
        if not (normalized_id_maps["1"] == normalized_id_maps["27"] == normalized_id_maps["52"]):
            raise DeformationStressError("evaluated source-index map changed across stress frames")

        if set(geometry["regions"]) != set(REGIONS) or set(receipt["regions"]) != set(REGIONS):
            raise DeformationStressError("receipt is missing an anatomical region")
        for region_name, contract in REGIONS.items():
            raw_region = geometry["regions"][region_name]
            selection = receipt["regions"][region_name]["selection"]
            if raw_region["groups"] != list(contract["groups"]) or selection["groups"] != list(contract["groups"]):
                raise DeformationStressError(f"anatomical group mapping changed: {region_name}")
            if raw_region["weight_threshold"] != REGION_WEIGHT_THRESHOLD:
                raise DeformationStressError(f"anatomical weight threshold changed: {region_name}")
            selected_ids = raw_region["selected_source_vertex_indices"]
            selected_weights = raw_region["selected_source_group_weight_sum"]
            selected_mask_weights = raw_region["selected_source_pv_mask_weights"]
            if (
                not isinstance(selected_ids, list)
                or len(selected_ids) < 100
                or selected_ids != sorted(set(selected_ids))
                or len(selected_weights) != len(selected_ids)
                or len(selected_mask_weights) != len(selected_ids)
                or any(type(value) is not int or value < 0 or value >= source_vertex_count for value in selected_ids)
            ):
                raise DeformationStressError(f"invalid static source region selection: {region_name}")
            if any(float(value) < REGION_WEIGHT_THRESHOLD for value in selected_weights):
                raise DeformationStressError(f"selected source vertex falls below its weight threshold: {region_name}")
            measured_ids = raw_region["measured_vertex_indices"]
            triangles = raw_region["triangles"]
            edges = raw_region["edges"]
            if (
                not isinstance(measured_ids, list)
                or len(measured_ids) < 100
                or measured_ids != sorted(set(measured_ids))
                or not isinstance(triangles, list)
                or not isinstance(edges, list)
                or not triangles
                or not edges
                or any(type(index) is not int or index not in set(selected_ids) for index in measured_ids)
            ):
                raise DeformationStressError(f"invalid retained source surface patch: {region_name}")
            visible_ids = set(normalized_id_maps["1"])
            if any(index not in visible_ids for index in measured_ids):
                raise DeformationStressError(f"measured region vertex was removed from evaluated mesh: {region_name}")
            if any(
                not isinstance(triangle, list)
                or len(triangle) != 3
                or any(type(index) is not int or index not in set(measured_ids) for index in triangle)
                for triangle in triangles
            ):
                raise DeformationStressError(f"invalid retained triangle mapping: {region_name}")
            if edges != _edge_pairs(triangles):
                raise DeformationStressError(f"edge list does not match retained triangles: {region_name}")
            if set(index for tri in triangles for index in tri) != set(measured_ids):
                raise DeformationStressError(f"region vertex list does not match its triangles: {region_name}")
            component_count = _connected_component_count(triangles)
            if component_count != 1 or selection["connected_components"] != component_count:
                raise DeformationStressError(f"region is not one stable connected surface patch: {region_name}")
            if selection["selected_source_vertex_count"] != len(selected_ids):
                raise DeformationStressError(f"source selection count mismatch: {region_name}")
            if selection["selected_source_triangle_count"] < len(triangles):
                raise DeformationStressError(f"retained triangles exceed source selection: {region_name}")
            if selection["retained_region_vertices"] != len(measured_ids):
                raise DeformationStressError(f"retained source vertex count mismatch: {region_name}")
            if selection["retained_region_triangles"] != len(triangles):
                raise DeformationStressError(f"retained source triangle count mismatch: {region_name}")
            if any(float(value) != 0.0 for value in selected_mask_weights):
                raise DeformationStressError(f"PV mask unexpectedly covers a measured limb region: {region_name}")
            recomputed_skin = _mask_stats(selected_weights)
            recomputed_pv = _mask_stats(selected_mask_weights)
            if receipt["regions"][region_name]["skin_group_weight_sum"] != recomputed_skin:
                raise DeformationStressError(f"skin-group selection stats mismatch: {region_name}")
            if receipt["regions"][region_name]["pv_mask_weights"] != recomputed_pv:
                raise DeformationStressError(f"PV mask selection stats mismatch: {region_name}")
            for frame_text, id_map in normalized_id_maps.items():
                frame_data = raw_region["frames"][frame_text]
                if frame_data["source_id_map_sha256"] != _source_id_digest(id_map):
                    raise DeformationStressError(f"source-index map digest mismatch: {region_name}/{frame_text}")
                if frame_data["evaluated_mesh_vertices"] != len(id_map):
                    raise DeformationStressError(f"evaluated vertex count mismatch: {region_name}/{frame_text}")
                if type(frame_data["evaluated_mesh_triangles"]) is not int or frame_data["evaluated_mesh_triangles"] <= 0:
                    raise DeformationStressError(f"invalid evaluated triangle count: {region_name}/{frame_text}")
            evaluated_topologies = {
                (
                    raw_region["frames"][frame_text]["evaluated_mesh_vertices"],
                    raw_region["frames"][frame_text]["evaluated_mesh_triangles"],
                )
                for frame_text in expected_id_frames
            }
            if len(evaluated_topologies) != 1:
                raise DeformationStressError(f"evaluated mesh topology changed across frames: {region_name}")
            recomputed = _region_measurements(raw_region)
            if receipt["regions"][region_name]["measurements"] != recomputed:
                raise DeformationStressError(f"receipt metrics do not recompute from raw points: {region_name}")

        camera = receipt["camera"]
        resolution = camera["resolution_px"]
        if (
            camera["name"] != "ReviewCamera_front"
            or camera["projection"] != "ORTHO"
            or not isinstance(resolution, list)
            or len(resolution) != 2
            or any(type(value) is not int or value <= 0 for value in resolution)
        ):
            raise DeformationStressError("receipt does not retain the matched saved review camera")
        renders = receipt["renders"]
        if set(renders) != {str(frame) for frame in FRAME_NUMBERS}:
            raise DeformationStressError("receipt render set is incomplete")
        for frame in FRAME_NUMBERS:
            label = f"frame-{frame:03d}.png"
            render = renders[str(frame)]
            path = _assert_flat_child(output, render["path"], label, render["sha256"], MAX_PNG_BYTES)
            if path.stat().st_size != render["bytes"]:
                raise DeformationStressError(f"PNG byte count mismatch: {label}")
            if list(_png_dimensions(path)) != resolution:
                raise DeformationStressError(f"PNG dimensions disagree with matched camera: {label}")
        return receipt
    except DeformationStressError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OSError, json.JSONDecodeError) as exc:
        raise DeformationStressError(f"malformed deformation receipt: {exc}") from exc


def _weight_quantiles(values: Sequence[float]) -> dict[str, Any]:
    ordered = sorted(float(value) for value in values)
    if not ordered or any(not math.isfinite(value) for value in ordered):
        raise DeformationStressError("invalid skin-group weight sample")

    def at(q: float) -> float:
        pos = (len(ordered) - 1) * q
        low, high = math.floor(pos), math.ceil(pos)
        return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)

    return {
        "count": len(ordered),
        "min": round(ordered[0], 9),
        "p05": round(at(0.05), 9),
        "p50": round(at(0.50), 9),
        "p95": round(at(0.95), 9),
        "mean": round(sum(ordered) / len(ordered), 9),
        "max": round(ordered[-1], 9),
    }


def _world_point(matrix: Any, point: Any, meters_per_unit: float) -> list[float]:
    transformed = matrix @ point
    return [round(float(component) * meters_per_unit, 9) for component in transformed]


def _pose_bones(bpy: Any, rig: Any, frame: int, meters_per_unit: float) -> dict[str, Any]:
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    selected = (
        "DEF-shoulder.R",
        "DEF-upper_arm.R",
        "DEF-forearm.R",
        "DEF-thigh.L",
        "DEF-shin.L",
    )
    result: dict[str, Any] = {}
    for name in selected:
        bone = rig.pose.bones.get(name)
        if bone is None:
            raise DeformationStressError(f"required stress bone missing: {name}")
        result[name] = {
            "head_world_m": _world_point(rig.matrix_world, bone.head, meters_per_unit),
            "tail_world_m": _world_point(rig.matrix_world, bone.tail, meters_per_unit),
            "length_m": round(float(bone.length) * meters_per_unit, 9),
        }
    return result


def _collect_group_inventory(body: Any) -> tuple[list[dict[str, Any]], dict[int, dict[str, float]]]:
    weights: dict[int, dict[str, float]] = {index: {} for index in range(len(body.data.vertices))}
    stats: dict[int, dict[str, float]] = {
        group.index: {"member_vertices": 0, "weight_sum": 0.0, "max_weight": 0.0}
        for group in body.vertex_groups
    }
    for vertex in body.data.vertices:
        for assignment in vertex.groups:
            weight = float(assignment.weight)
            weights[vertex.index][assignment.group] = weight
            entry = stats[assignment.group]
            entry["member_vertices"] += 1
            entry["weight_sum"] += weight
            entry["max_weight"] = max(entry["max_weight"], weight)
    inventory = [
        {
            "index": group.index,
            "name": group.name,
            "member_vertices": int(stats[group.index]["member_vertices"]),
            "weight_sum": round(stats[group.index]["weight_sum"], 8),
            "max_weight": round(stats[group.index]["max_weight"], 8),
        }
        for group in body.vertex_groups
    ]
    return inventory, weights


def _camera_inventory(scene: Any) -> dict[str, Any]:
    camera = scene.camera
    if camera is None or camera.name != "ReviewCamera_front" or camera.data.type != "ORTHO":
        raise DeformationStressError("pinned scene lacks the saved orthographic ReviewCamera_front")
    return {
        "name": camera.name,
        "projection": camera.data.type,
        "location_world_m": [round(float(value), 9) for value in camera.matrix_world.translation],
        "rotation_euler_rad": [round(float(value), 9) for value in camera.rotation_euler],
        "ortho_scale_m": round(float(camera.data.ortho_scale), 9),
        "resolution_px": [int(scene.render.resolution_x), int(scene.render.resolution_y)],
        "resolution_percentage": int(scene.render.resolution_percentage),
        "render_engine": str(scene.render.engine),
    }


def _modifier_inventory(body: Any) -> list[dict[str, Any]]:
    result = []
    for index, modifier in enumerate(body.modifiers):
        item: dict[str, Any] = {
            "order": index,
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
        result.append(item)
    expected = [
        ("Armature", "ARMATURE", False, ""),
        ("Armature PV", "ARMATURE", True, "mhmask-preserve-volume"),
        ("Hide helpers", "MASK", None, None),
    ]
    actual = [
        (
            item["name"],
            item["type"],
            item.get("use_deform_preserve_volume"),
            item.get("vertex_group_mask"),
        )
        for item in result
    ]
    if actual != expected:
        raise DeformationStressError(f"unexpected canonical body modifier stack: {actual}")
    return result


def _source_selection(body: Any, weights: dict[int, dict[str, float]], mask_group_index: int) -> dict[str, Any]:
    mesh = body.data
    mesh.calc_loop_triangles()
    source_triangles = [tuple(int(index) for index in triangle.vertices) for triangle in mesh.loop_triangles]
    regions: dict[str, Any] = {}
    for name, contract in REGIONS.items():
        missing = [group for group in contract["groups"] if body.vertex_groups.get(group) is None]
        if missing:
            raise DeformationStressError(f"body lacks anatomical skin groups for {name}: {missing}")
        group_indices = {body.vertex_groups[group].index for group in contract["groups"]}
        selected_ids = []
        combined_weights = []
        mask_weights = []
        for vertex in mesh.vertices:
            assignment = weights[vertex.index]
            combined = sum(assignment.get(index, 0.0) for index in group_indices)
            if combined >= REGION_WEIGHT_THRESHOLD:
                selected_ids.append(vertex.index)
                combined_weights.append(round(combined, 9))
                mask_weights.append(round(assignment.get(mask_group_index, 0.0), 9))
        if len(selected_ids) < 100:
            raise DeformationStressError(f"anatomical group selection is too small: {name}")
        selected_set = set(selected_ids)
        region_triangles = [
            list(triangle) for triangle in source_triangles
            if all(index in selected_set for index in triangle)
        ]
        if len(region_triangles) < 100:
            raise DeformationStressError(f"anatomical selection contains too few source triangles: {name}")
        regions[name] = {
            "contract": contract,
            "selected_source_vertex_indices": selected_ids,
            "selected_source_group_weight_sum": combined_weights,
            "selected_source_pv_mask_weights": mask_weights,
            "source_triangles": region_triangles,
        }
    return regions


def _global_pv_distribution(
    body: Any,
    weights: dict[int, dict[str, float]],
    mask_group_index: int,
    world_positions_by_source_id: dict[int, list[float]],
) -> dict[str, Any]:
    mask_values: dict[int, float] = {
        index: assignment.get(mask_group_index, 0.0)
        for index, assignment in weights.items()
        if assignment.get(mask_group_index, 0.0) > 0.0
    }
    if not mask_values:
        raise DeformationStressError("preserve-volume mask group has no positive source weights")
    visible = [index for index in mask_values if index in world_positions_by_source_id]
    if len(visible) != len(mask_values):
        raise DeformationStressError("some preserve-volume mask vertices are absent after Hide helpers")
    points = [world_positions_by_source_id[index] for index in visible]
    weighted_groups: dict[str, float] = {}
    group_support: dict[str, int] = {}
    for index, mask_weight in mask_values.items():
        for group_index, skin_weight in weights[index].items():
            group = body.vertex_groups[group_index].name
            if group.startswith("DEF-") and skin_weight > 0.0:
                weighted_groups[group] = weighted_groups.get(group, 0.0) + mask_weight * skin_weight
                group_support[group] = group_support.get(group, 0) + 1
    top_groups = [
        {
            "name": name,
            "mask_times_skin_weight_sum": round(total, 8),
            "positive_skin_weight_vertices": group_support[name],
        }
        for name, total in sorted(weighted_groups.items(), key=lambda entry: (-entry[1], entry[0]))[:12]
    ]
    return {
        "group": "mhmask-preserve-volume",
        "source_positive_vertex_count": len(mask_values),
        "evaluated_visible_vertex_count": len(visible),
        "evaluated_world_bounds_m": _bounds(points),
        "weight_distribution": _mask_stats(list(mask_values.values())),
        "top_deform_groups_by_mask_weighted_support": top_groups,
    }


def _render_frame(bpy: Any, output: Path, frame: int, meters_per_unit: float) -> dict[str, Any]:
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    path = output / f"frame-{frame:03d}.png"
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(path)
    result = bpy.ops.render.render(write_still=True)
    if "FINISHED" not in result or not path.is_file() or _reparse_point(path):
        raise DeformationStressError(f"Blender did not create a safe frame {frame} PNG")
    size = path.stat().st_size
    if size <= 24 or size > MAX_PNG_BYTES or path.read_bytes()[:8] != PNG_SIGNATURE:
        raise DeformationStressError(f"Blender created an invalid frame {frame} PNG")
    return {
        "path": path.name,
        "sha256": sha256_file(path),
        "bytes": size,
        "resolution_px": list(_png_dimensions(path)),
        "frame": frame,
        "meters_per_blender_unit": meters_per_unit,
    }


def _build_inventory(bpy: Any, body: Any, rig: Any, group_inventory: list[dict[str, Any]], modifiers: list[dict[str, Any]], meters_per_unit: float) -> dict[str, Any]:
    scene = bpy.context.scene
    objects = sorted(scene.objects, key=lambda obj: obj.name_full)
    type_counts: dict[str, int] = {}
    for obj in objects:
        type_counts[obj.type] = type_counts.get(obj.type, 0) + 1
    actions = sorted({
        obj.animation_data.action.name
        for obj in objects
        if obj.animation_data is not None and obj.animation_data.action is not None
    })
    return {
        "scene": {
            "name": scene.name_full,
            "frame_start": int(scene.frame_start),
            "frame_end": int(scene.frame_end),
            "fps": int(scene.render.fps),
            "fps_base": round(float(scene.render.fps_base), 9),
            "unit_system": str(scene.unit_settings.system),
            "meters_per_blender_unit": round(meters_per_unit, 9),
            "object_type_counts": dict(sorted(type_counts.items())),
            "objects": [
                {
                    "name": obj.name_full,
                    "type": obj.type,
                    "parent": obj.parent.name_full if obj.parent else None,
                    "hide_render": bool(obj.hide_render),
                }
                for obj in objects
            ],
        },
        "body": {
            "object": body.name_full,
            "mesh_datablock": body.data.name_full,
            "stored_vertices": len(body.data.vertices),
            "stored_edges": len(body.data.edges),
            "stored_polygons": len(body.data.polygons),
            "stored_triangles": len(body.data.loop_triangles),
            "world_matrix": [
                [round(float(value), 9) for value in row]
                for row in body.matrix_world
            ],
            "modifiers_in_stack_order": modifiers,
            "skin_groups": group_inventory,
        },
        "rig": {
            "object": rig.name_full,
            "bone_count": len(rig.data.bones),
            "bone_names": [bone.name for bone in rig.data.bones],
            "active_actions": actions,
        },
    }


def run_in_blender(source: Path, output: Path) -> dict[str, Any]:
    """Open the pinned scene, measure stable source topology, render, and write receipt."""
    import bpy  # type: ignore[import-not-found]

    source = Path(source).resolve(strict=True)
    output = Path(output).resolve(strict=True)
    expected_source = (ROOT / SOURCE_RELATIVE).resolve(strict=True)
    expected_review_root = (ROOT / REVIEW_RELATIVE).resolve(strict=True)
    if source != expected_source:
        raise DeformationStressError("worker accepts only the canonical pinned source asset")
    if output.parent != expected_review_root:
        raise DeformationStressError("worker output must be a direct child of the review quarantine")
    if bpy.app.version_string != SUPPORTED_BLENDER_VERSION:
        raise DeformationStressError(
            f"Blender {SUPPORTED_BLENDER_VERSION} required; received {bpy.app.version_string}"
        )
    if sha256_file(source) != SOURCE_SHA256:
        raise DeformationStressError("source hash differs from pinned fighter-family v1.1 asset")
    if _reparse_point(output):
        raise DeformationStressError("run output is a symlink or reparse point")
    result = bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    if "FINISHED" not in result:
        raise DeformationStressError("Blender did not finish opening the pinned scene")
    if sha256_file(source) != SOURCE_SHA256:
        raise DeformationStressError("source hash changed while opening the scene")

    scene = bpy.context.scene
    body = bpy.data.objects.get("Human")
    rig = bpy.data.objects.get("Human.rigify")
    if body is None or body.type != "MESH" or rig is None or rig.type != "ARMATURE":
        raise DeformationStressError("pinned scene lacks the Human body or Rigify armature")
    if body.parent is not rig:
        raise DeformationStressError("Human body is not parented to the expected Rigify armature")
    if scene.unit_settings.scale_length != 1.0:
        raise DeformationStressError("pinned scene units are not 1 meter per Blender unit")
    meters_per_unit = float(scene.unit_settings.scale_length)
    action_name = rig.animation_data.action.name if rig.animation_data and rig.animation_data.action else None
    if action_name != "Human.rigifyAction":
        raise DeformationStressError(f"unexpected saved Rigify action: {action_name}")
    scene.frame_set(1)
    bpy.context.view_layer.update()

    modifiers = _modifier_inventory(body)
    group_inventory, weights = _collect_group_inventory(body)
    mask_group = body.vertex_groups.get("mhmask-preserve-volume")
    if mask_group is None:
        raise DeformationStressError("preserve-volume mask vertex group is missing")
    selection = _source_selection(body, weights, mask_group.index)
    scene_inventory = _build_inventory(bpy, body, rig, group_inventory, modifiers, meters_per_unit)
    camera = _camera_inventory(scene)

    if body.data.attributes.get(_SOURCE_ID_ATTRIBUTE) is not None:
        raise DeformationStressError("reserved source-index attribute already exists")
    source_attribute = body.data.attributes.new(
        name=_SOURCE_ID_ATTRIBUTE,
        type="INT",
        domain="POINT",
    )
    for index, datum in enumerate(source_attribute.data):
        datum.value = index

    raw_regions: dict[str, Any] = {}
    evaluated_ids_by_frame: dict[str, list[int]] = {}
    frame_bones: dict[str, Any] = {}
    try:
        body.data.calc_loop_triangles()
        source_vertex_count = len(body.data.vertices)
        reference_id_sequence: list[int] | None = None
        for frame in FRAME_NUMBERS:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            depsgraph = bpy.context.evaluated_depsgraph_get()
            evaluated = body.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
            if mesh is None:
                raise DeformationStressError(f"evaluated Human mesh unavailable at frame {frame}")
            try:
                id_attribute = mesh.attributes.get(_SOURCE_ID_ATTRIBUTE)
                if id_attribute is None or id_attribute.domain != "POINT" or id_attribute.data_type != "INT":
                    raise DeformationStressError("source vertex IDs did not survive the saved modifier stack")
                source_ids = [int(item.value) for item in id_attribute.data]
                if (
                    len(source_ids) != len(mesh.vertices)
                    or len(set(source_ids)) != len(source_ids)
                    or any(index < 0 or index >= source_vertex_count for index in source_ids)
                ):
                    raise DeformationStressError(f"invalid evaluated source index map at frame {frame}")
                if reference_id_sequence is None:
                    reference_id_sequence = source_ids
                elif source_ids != reference_id_sequence:
                    raise DeformationStressError("evaluated source vertex mapping changed between frames")
                evaluated_ids_by_frame[str(frame)] = source_ids
                source_index_to_world = {
                    source_id: _world_point(evaluated.matrix_world, vertex.co, meters_per_unit)
                    for source_id, vertex in zip(source_ids, mesh.vertices)
                }
                if not source_index_to_world:
                    raise DeformationStressError(f"evaluated mesh has no vertices at frame {frame}")
                for region_name, data in selection.items():
                    if region_name not in raw_regions:
                        visible_ids = set(source_ids)
                        retained_triangles = [
                            triangle for triangle in data["source_triangles"]
                            if all(index in visible_ids for index in triangle)
                        ]
                        measured_ids = sorted({index for triangle in retained_triangles for index in triangle})
                        if len(measured_ids) < 100 or len(retained_triangles) < 100:
                            raise DeformationStressError(f"evaluated anatomical region is too small: {region_name}")
                        components = _connected_component_count(retained_triangles)
                        if components != 1:
                            raise DeformationStressError(
                                f"source group selection does not yield one connected evaluated patch: "
                                f"{region_name} ({components})"
                            )
                        raw_regions[region_name] = {
                            "label": data["contract"]["label"],
                            "side": data["contract"]["side"],
                            "groups": list(data["contract"]["groups"]),
                            "weight_threshold": REGION_WEIGHT_THRESHOLD,
                            "selected_source_vertex_indices": data["selected_source_vertex_indices"],
                            "selected_source_group_weight_sum": data["selected_source_group_weight_sum"],
                            "selected_source_pv_mask_weights": data["selected_source_pv_mask_weights"],
                            "selected_source_triangle_count": len(data["source_triangles"]),
                            "measured_vertex_indices": measured_ids,
                            "triangles": retained_triangles,
                            "edges": _edge_pairs(retained_triangles),
                            "connected_components": components,
                            "frames": {},
                        }
                    raw_region = raw_regions[region_name]
                    points = []
                    for source_id in raw_region["measured_vertex_indices"]:
                        if source_id not in source_index_to_world:
                            raise DeformationStressError(
                                f"source vertex {source_id} disappeared at frame {frame}/{region_name}"
                            )
                        points.append(source_index_to_world[source_id])
                    raw_region["frames"][str(frame)] = {
                        "evaluated_mesh_vertices": len(mesh.vertices),
                        "evaluated_mesh_triangles": len(mesh.loop_triangles),
                        "source_id_map_sha256": _source_id_digest(source_ids),
                        "positions_world_m": points,
                    }
                if frame == 1:
                    global_pv = _global_pv_distribution(
                        body, weights, mask_group.index, source_index_to_world
                    )
            finally:
                evaluated.to_mesh_clear()
            frame_bones[str(frame)] = _pose_bones(bpy, rig, frame, meters_per_unit)
    finally:
        current_attribute = body.data.attributes.get(_SOURCE_ID_ATTRIBUTE)
        if current_attribute is not None:
            body.data.attributes.remove(current_attribute)

    geometry = {
        "schema": GEOMETRY_SCHEMA,
        "source_sha256": SOURCE_SHA256,
        "source_vertex_count": len(body.data.vertices),
        "evaluated_source_vertex_ids": evaluated_ids_by_frame,
        "regions": raw_regions,
    }
    raw_path = output / "geometry.json"
    _atomic_json(raw_path, geometry)
    if raw_path.stat().st_size > MAX_GEOMETRY_BYTES:
        raise DeformationStressError("raw deformation geometry exceeds the size limit")

    regions: dict[str, Any] = {}
    for region_name, raw_region in raw_regions.items():
        selection_weights = raw_region["selected_source_group_weight_sum"]
        pv_weights = raw_region["selected_source_pv_mask_weights"]
        if any(value > 0.0 for value in pv_weights):
            raise DeformationStressError(f"preserve-volume mask unexpectedly overlaps {region_name}")
        regions[region_name] = {
            "selection": {
                "label": raw_region["label"],
                "side": raw_region["side"],
                "groups": raw_region["groups"],
                "weight_threshold": REGION_WEIGHT_THRESHOLD,
                "selected_source_vertex_count": len(raw_region["selected_source_vertex_indices"]),
                "selected_source_triangle_count": raw_region["selected_source_triangle_count"],
                "retained_region_vertices": len(raw_region["measured_vertex_indices"]),
                "retained_region_triangles": len(raw_region["triangles"]),
                "connected_components": raw_region["connected_components"],
            },
            "skin_group_weight_sum": _mask_stats(selection_weights),
            "pv_mask_weights": _mask_stats(pv_weights),
            "measurements": _region_measurements(raw_region),
        }

    render_records = {}
    for frame in FRAME_NUMBERS:
        render_records[str(frame)] = _render_frame(bpy, output, frame, meters_per_unit)

    build_hash = bpy.app.build_hash
    if isinstance(build_hash, bytes):
        build_hash = build_hash.decode("ascii", errors="replace")
    receipt = {
        "schema": SCHEMA,
        "status": "diagnostic_only",
        "verdict": "diagnostic_only",
        "scope": "saved canonical generic MPFB/Rigify body; arm/leg deformation measurements only",
        "source": {
            "path": SOURCE_RELATIVE,
            "sha256_before": SOURCE_SHA256,
            "sha256_after": sha256_file(source),
            "mutated": False,
        },
        "tool": {
            "name": "Blender",
            "version": bpy.app.version_string,
            "build_hash": str(build_hash),
            "network": "offline",
            "embedded_scripts": "disabled",
        },
        "inventory": scene_inventory,
        "camera": camera,
        "frames": [{"frame": frame, "label": FRAME_LABELS[frame]} for frame in FRAME_NUMBERS],
        "pose_bones_world_m": frame_bones,
        "thresholds": {
            "region_weight_sum_inclusive_min": REGION_WEIGHT_THRESHOLD,
            "degenerate_triangle_area_m2_inclusive_max": DEGENERATE_TRIANGLE_AREA_M2,
            "degenerate_edge_length_m_inclusive_max": DEGENERATE_EDGE_LENGTH_M,
            "quality_pass_threshold": None,
            "distortion_quantiles": list(DISTORTION_QUANTILES),
        },
        "modifier_configuration": "saved canonical stack only; no modifiers toggled",
        "configuration_comparison": (
            "not run: the saved arm/leg PV mask has zero positive weights in both measured regions; "
            "no LBS-versus-DQS or PV-benefit inference is made"
        ),
        "preserve_volume_mask_distribution": global_pv,
        "regions": regions,
        "volume_measurement": "not measured: an open selected surface patch is not a closed volume",
        "renders": render_records,
        "raw_geometry": {
            "path": raw_path.name,
            "sha256": sha256_file(raw_path),
            "bytes": raw_path.stat().st_size,
        },
        "limitations": [
            "generic proxy body only; no fighter likeness or finished-art verdict",
            "the selected arm/leg surfaces have zero preserve-volume mask weight, so DQS is not evaluated there",
            "regional area/edge distortion is descriptive and has no pass threshold",
            "selected surface patches are open and do not justify a volume measurement",
            "no combat impact, choreography, T5b, HG2, or operator art approval claim",
        ],
    }
    if sha256_file(source) != SOURCE_SHA256:
        raise DeformationStressError("source hash changed during measurement/rendering")
    receipt_path = output / "receipt.json"
    _atomic_json(receipt_path, receipt)
    if receipt_path.stat().st_size > MAX_RECEIPT_BYTES:
        raise DeformationStressError("deformation receipt exceeds the size limit")
    return receipt


def _blender_args(argv: list[str]) -> list[str]:
    return argv[argv.index("--") + 1 :] if "--" in argv else argv


def blender_main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(_blender_args(sys.argv[1:] if argv is None else argv))
    try:
        run_in_blender(Path(args.source), Path(args.output))
    except Exception as exc:
        print(f"MODEL_DEFORMATION_STRESS_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(blender_main())
