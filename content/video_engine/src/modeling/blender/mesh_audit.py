"""Read-only, source-neutral Blender mesh inspection for pinned model inputs.

Run by Blender through ``scripts/model_mesh_audit.py``. This module deliberately
does not import ``bpy`` at module load time so its path and GLB guards can also
be exercised by the regular Python test runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "model_mesh_audit.v1"
SUPPORTED_BLENDER_VERSION = "5.2.2 LTS"
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_GLB_MAGIC = b"glTF"
_GLB_JSON_CHUNK = b"JSON"
MAX_GLB_JSON_CHUNK_BYTES = 16 * 1024 * 1024


class MeshAuditError(ValueError):
    """Raised when an input cannot be safely or completely audited."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolved_root(root: str | Path) -> Path:
    try:
        resolved = Path(root).expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise MeshAuditError(f"caller root is unavailable: {root}") from exc
    if not resolved.is_dir():
        raise MeshAuditError(f"caller root is not a directory: {root}")
    return resolved


def _resolve_rooted_path(root: Path, candidate: str | Path, *, must_exist: bool, label: str) -> Path:
    raw_path = Path(candidate).expanduser()
    joined = raw_path if raw_path.is_absolute() else root / raw_path
    try:
        resolved = joined.resolve(strict=must_exist)
    except FileNotFoundError as exc:
        raise MeshAuditError(f"{label} does not exist: {candidate}") from exc
    except (OSError, RuntimeError) as exc:
        raise MeshAuditError(f"{label} cannot be resolved: {candidate}") from exc
    if not resolved.is_relative_to(root):
        raise MeshAuditError(f"{label} escapes caller root: {candidate}")
    return resolved


def _read_glb_document(path: Path) -> dict[str, Any]:
    """Read and validate the GLB container and its JSON chunk without loading BIN data."""
    size = path.stat().st_size
    with path.open("rb") as stream:
        header = stream.read(12)
        if len(header) != 12:
            raise MeshAuditError("GLB header is truncated")
        magic = header[:4]
        version = int.from_bytes(header[4:8], "little")
        declared_length = int.from_bytes(header[8:12], "little")
        if magic != _GLB_MAGIC or version != 2:
            raise MeshAuditError("unsupported GLB container; expected glTF 2.0 binary")
        if declared_length != size:
            raise MeshAuditError("GLB declared length does not match file size")

        json_payload: bytes | None = None
        offset = 12
        chunk_index = 0
        while offset < declared_length:
            chunk_header = stream.read(8)
            if len(chunk_header) != 8:
                raise MeshAuditError("GLB chunk header is truncated")
            chunk_length = int.from_bytes(chunk_header[:4], "little")
            chunk_type = chunk_header[4:8]
            offset += 8
            if chunk_length % 4 != 0 or offset + chunk_length > declared_length:
                raise MeshAuditError("GLB chunk has an invalid length")
            if chunk_index == 0 and chunk_type != _GLB_JSON_CHUNK:
                raise MeshAuditError("GLB JSON chunk must be first")
            if chunk_type == _GLB_JSON_CHUNK:
                if json_payload is not None:
                    raise MeshAuditError("GLB contains more than one JSON chunk")
                if chunk_length > MAX_GLB_JSON_CHUNK_BYTES:
                    raise MeshAuditError("GLB JSON chunk exceeds the 16 MiB safety limit")
                json_payload = stream.read(chunk_length)
                if len(json_payload) != chunk_length:
                    raise MeshAuditError("GLB JSON chunk is truncated")
            else:
                stream.seek(chunk_length, 1)
            offset += chunk_length
            chunk_index += 1

    if json_payload is None:
        raise MeshAuditError("GLB has no JSON chunk")
    try:
        document = json.loads(json_payload.rstrip(b"\x00 \t\r\n").decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MeshAuditError("GLB JSON chunk is invalid") from exc
    asset = document.get("asset") if isinstance(document, dict) else None
    if not isinstance(asset, dict) or asset.get("version") != "2.0":
        raise MeshAuditError("GLB asset version must be 2.0")

    for resource_type in ("buffers", "images"):
        entries = document.get(resource_type, [])
        if not isinstance(entries, list):
            raise MeshAuditError(f"GLB {resource_type} declaration is invalid")
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise MeshAuditError(f"GLB {resource_type}[{index}] declaration is invalid")
            uri = entry.get("uri")
            if uri is not None and (not isinstance(uri, str) or not uri.startswith("data:")):
                raise MeshAuditError(f"GLB external {resource_type} URI is not allowed: {uri}")
    return document


def validate_source(root: str | Path, candidate: str | Path, expected_sha256: str) -> dict[str, Any]:
    """Resolve an input inside ``root`` and verify its format and exact bytes."""
    if not isinstance(expected_sha256, str) or not _SHA256_RE.fullmatch(expected_sha256):
        raise MeshAuditError("expected SHA-256 must be exactly 64 hexadecimal characters")
    resolved_root = _resolved_root(root)
    source = _resolve_rooted_path(resolved_root, candidate, must_exist=True, label="source")
    if not source.is_file():
        raise MeshAuditError(f"source is not a regular file: {candidate}")
    extension = source.suffix.lower()
    if extension not in {".blend", ".glb"}:
        raise MeshAuditError(f"unsupported model format: {source.suffix or '<no extension>'}")

    actual_hash = sha256_file(source)
    if actual_hash.lower() != expected_sha256.lower():
        raise MeshAuditError(
            f"stale source hash: expected {expected_sha256.lower()}, received {actual_hash}"
        )
    if extension == ".glb":
        _read_glb_document(source)
    return {
        "path": source,
        "relative_path": source.relative_to(resolved_root).as_posix(),
        "format": extension[1:],
        "sha256": actual_hash,
        "byte_size": source.stat().st_size,
        "root": resolved_root,
    }


def resolve_receipt_path(root: str | Path, candidate: str | Path, source_path: Path) -> Path:
    """Resolve a JSON output path inside the caller root and keep it off the source."""
    resolved_root = _resolved_root(root)
    output = _resolve_rooted_path(resolved_root, candidate, must_exist=False, label="receipt path")
    if output == source_path.resolve(strict=True):
        raise MeshAuditError("receipt path must not overwrite the source asset")
    if output.suffix.lower() != ".json":
        raise MeshAuditError("receipt path must end in .json")
    if output.exists():
        raise MeshAuditError("receipt path already exists; choose a new output path")
    return output


def _blender_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only Blender mesh audit worker")
    parser.add_argument("--root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--output", required=True)
    delimiter = "--"
    if delimiter in argv:
        argv = argv[argv.index(delimiter) + 1 :]
    return parser.parse_args(argv)


def _float_value(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise MeshAuditError("mesh contains a non-finite coordinate or weight")
    result = round(result, 9)
    return 0.0 if result == 0 else result


def _scene_meters_per_unit(scene: Any) -> float:
    scale = float(scene.unit_settings.scale_length)
    if not math.isfinite(scale) or scale <= 0:
        raise MeshAuditError("scene unit scale must be finite and positive")
    return scale


def _bounds(
    vertices: Iterable[Any], matrix_world: Any | None = None, *, meters_per_unit: float
) -> dict[str, list[float]] | None:
    low = [math.inf, math.inf, math.inf]
    high = [-math.inf, -math.inf, -math.inf]
    found = False
    for vertex in vertices:
        point = matrix_world @ vertex.co if matrix_world is not None else vertex.co
        values = [_float_value(point[axis] * meters_per_unit) for axis in range(3)]
        for axis, value in enumerate(values):
            low[axis] = min(low[axis], value)
            high[axis] = max(high[axis], value)
        found = True
    if not found:
        return None
    return {"min": low, "max": high}


def _component_count(vertex_count: int, edges: Iterable[Any]) -> int:
    if vertex_count == 0:
        return 0
    parent = list(range(vertex_count))

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for edge in edges:
        left, right = edge.vertices
        root_left = find(int(left))
        root_right = find(int(right))
        if root_left != root_right:
            parent[root_right] = root_left
    return len({find(index) for index in range(vertex_count)})


def _topology_counts(mesh: Any) -> dict[str, int]:
    import bmesh

    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        return {
            "non_manifold_edges": sum(1 for edge in bm.edges if not edge.is_manifold),
            "boundary_edges": sum(1 for edge in bm.edges if len(edge.link_faces) == 1),
            "loose_edges": sum(1 for edge in bm.edges if edge.is_wire),
            "loose_vertices": sum(1 for vertex in bm.verts if not vertex.link_edges),
        }
    finally:
        bm.free()


def _uv_layer_summaries(mesh: Any) -> list[dict[str, Any]]:
    summaries = []
    for layer in mesh.uv_layers:
        coordinates = [(_float_value(loop.uv[0]), _float_value(loop.uv[1])) for loop in layer.data]
        bounds = None
        if coordinates:
            bounds = {
                "min": [min(point[axis] for point in coordinates) for axis in range(2)],
                "max": [max(point[axis] for point in coordinates) for axis in range(2)],
            }
        summaries.append({"name": layer.name, "loop_uv_count": len(coordinates), "bounds": bounds})
    return summaries


def _mesh_metrics(mesh: Any, matrix_world: Any, meters_per_unit: float) -> dict[str, Any]:
    mesh.calc_loop_triangles()
    topology = _topology_counts(mesh)
    return {
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "triangles": len(mesh.loop_triangles),
        "connected_components": _component_count(len(mesh.vertices), mesh.edges),
        **topology,
        "bounds_local_m": _bounds(mesh.vertices, meters_per_unit=meters_per_unit),
        "bounds_world_m": _bounds(mesh.vertices, matrix_world, meters_per_unit=meters_per_unit),
        "uv_layers": _uv_layer_summaries(mesh),
    }


def _shape_keys(obj: Any) -> list[dict[str, Any]]:
    keys = obj.data.shape_keys
    if keys is None:
        return []
    return [
        {
            "name": block.name,
            "value": _float_value(block.value),
            "slider_min": _float_value(block.slider_min),
            "slider_max": _float_value(block.slider_max),
        }
        for block in keys.key_blocks
    ]


def _armature_links(obj: Any) -> dict[str, Any]:
    parent = obj.parent if obj.parent and obj.parent.type == "ARMATURE" else None
    modifiers = []
    for modifier in obj.modifiers:
        if modifier.type != "ARMATURE":
            continue
        modifiers.append(
            {
                "modifier": modifier.name,
                "object": modifier.object.name_full if modifier.object else None,
                "use_vertex_groups": bool(modifier.use_vertex_groups),
                "use_bone_envelopes": bool(modifier.use_bone_envelopes),
            }
        )
    modifiers.sort(key=lambda item: (item["modifier"], item["object"] or ""))
    return {
        "parent": parent.name_full if parent else None,
        "armature_modifiers": modifiers,
    }


def _vertex_groups(obj: Any) -> list[dict[str, Any]]:
    member_counts = [0] * len(obj.vertex_groups)
    weighted_counts = [0] * len(obj.vertex_groups)
    for vertex in obj.data.vertices:
        for assignment in vertex.groups:
            index = int(assignment.group)
            if 0 <= index < len(member_counts):
                member_counts[index] += 1
                if assignment.weight > 0:
                    weighted_counts[index] += 1
    return [
        {
            "name": group.name,
            "member_vertices": member_counts[group.index],
            "positive_weight_vertices": weighted_counts[group.index],
        }
        for group in obj.vertex_groups
    ]


def _materials(obj: Any) -> list[dict[str, Any]]:
    return [
        {
            "slot": index,
            "name": slot.material.name_full if slot.material else None,
            "link": slot.link,
        }
        for index, slot in enumerate(obj.material_slots)
    ]


def _render_visibility(obj: Any, view_layer: Any) -> dict[str, Any]:
    """Record render flags for every collection path in the active view layer."""
    paths: list[dict[str, Any]] = []

    def visit(layer: Any, names: tuple[str, ...], excluded: bool, hidden: bool) -> None:
        collection = layer.collection
        names = (*names, collection.name_full)
        excluded = excluded or bool(layer.exclude)
        hidden = hidden or bool(collection.hide_render)
        if any(member == obj for member in collection.objects):
            paths.append(
                {
                    "collections": list(names),
                    "excluded_from_view_layer": excluded,
                    "hidden_for_render": hidden,
                }
            )
        for child in sorted(layer.children, key=lambda item: item.collection.name_full):
            visit(child, names, excluded, hidden)

    visit(view_layer.layer_collection, (), False, False)
    paths.sort(key=lambda item: item["collections"])
    return {
        "hide_render": bool(obj.hide_render),
        "hide_viewport": bool(obj.hide_viewport),
        "hidden_in_view_layer_viewport": bool(obj.hide_get(view_layer=view_layer)),
        "visible_in_viewport": bool(obj.visible_get(view_layer=view_layer)),
        "collection_paths": paths,
        "render_eligible": not obj.hide_render
        and any(not path["excluded_from_view_layer"] and not path["hidden_for_render"] for path in paths),
    }


def _sum_metric(meshes: list[dict[str, Any]], metric: str, geometry_state: str) -> int:
    return sum(int(mesh[geometry_state][metric]) for mesh in meshes)


def _union_bounds(meshes: list[dict[str, Any]], geometry_state: str) -> dict[str, list[float]] | None:
    bounds = [mesh[geometry_state]["bounds_world_m"] for mesh in meshes]
    present = [bound for bound in bounds if bound is not None]
    if not present:
        return None
    return {
        "min": [min(bound["min"][axis] for bound in present) for axis in range(3)],
        "max": [max(bound["max"][axis] for bound in present) for axis in range(3)],
    }


def _build_receipt(bpy: Any, source: dict[str, Any]) -> dict[str, Any]:
    if bpy.app.version_string != SUPPORTED_BLENDER_VERSION:
        raise MeshAuditError(
            f"Blender {SUPPORTED_BLENDER_VERSION} is required; received {bpy.app.version_string}"
        )
    scene = bpy.context.scene
    if scene is None:
        raise MeshAuditError("input has no active Blender scene")
    meters_per_unit = _scene_meters_per_unit(scene)
    objects = sorted((obj for obj in scene.objects if obj.type == "MESH"), key=lambda obj: obj.name_full)
    if not objects:
        raise MeshAuditError("input contains no mesh geometry")

    view_layer = bpy.context.view_layer
    view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    meshes: list[dict[str, Any]] = []
    for obj in objects:
        stored_metrics = _mesh_metrics(obj.data, obj.matrix_world, meters_per_unit)
        evaluated_object = obj.evaluated_get(depsgraph)
        evaluated_mesh = evaluated_object.to_mesh()
        if evaluated_mesh is None:
            raise MeshAuditError(f"evaluated mesh unavailable for object {obj.name_full}")
        try:
            evaluated_metrics = _mesh_metrics(evaluated_mesh, evaluated_object.matrix_world, meters_per_unit)
        finally:
            evaluated_object.to_mesh_clear()
        meshes.append(
            {
                "object": obj.name_full,
                "mesh_datablock": obj.data.name_full,
                "parent": obj.parent.name_full if obj.parent else None,
                "visibility": _render_visibility(obj, view_layer),
                "stored": stored_metrics,
                "evaluated": evaluated_metrics,
                "materials": _materials(obj),
                "shape_keys": _shape_keys(obj),
                "armature_links": _armature_links(obj),
                "vertex_groups": _vertex_groups(obj),
            }
        )

    if sum(mesh["stored"]["vertices"] for mesh in meshes) == 0 and sum(
        mesh["evaluated"]["vertices"] for mesh in meshes
    ) == 0:
        raise MeshAuditError("input contains no mesh geometry")

    count_fields = (
        "vertices",
        "edges",
        "faces",
        "triangles",
        "connected_components",
        "non_manifold_edges",
        "boundary_edges",
        "loose_edges",
        "loose_vertices",
    )
    summary: dict[str, Any] = {}
    for scope, scoped_meshes in (
        ("all_scene", meshes),
        ("render_eligible", [mesh for mesh in meshes if mesh["visibility"]["render_eligible"]]),
    ):
        scope_summary: dict[str, Any] = {
            "mesh_object_count": len(scoped_meshes),
            "unique_mesh_datablock_count": len({mesh["mesh_datablock"] for mesh in scoped_meshes}),
        }
        for geometry_state in ("stored", "evaluated"):
            scope_summary[geometry_state] = {
                field: _sum_metric(scoped_meshes, field, geometry_state) for field in count_fields
            }
            scope_summary[geometry_state]["bounds_world_m"] = _union_bounds(
                scoped_meshes, geometry_state
            )
        summary[scope] = scope_summary

    build_hash = getattr(bpy.app, "build_hash", b"")
    if isinstance(build_hash, bytes):
        build_hash = build_hash.decode("ascii", errors="replace")
    return {
        "schema": SCHEMA,
        "status": "diagnostic_only",
        "visual_quality_assessment": "not_performed",
        "art_approval_assessment": "not_performed",
        "source": {
            "path": source["relative_path"],
            "format": source["format"],
            "sha256": source["sha256"],
            "byte_size": source["byte_size"],
        },
        "tool": {
            "name": "Blender",
            "version": bpy.app.version_string,
            "build_hash": str(build_hash),
        },
        "inspection_mode": {
            "network": "offline",
            "embedded_scripts": "disabled",
            "source_mutated": False,
            "object_scope": "active scene mesh objects, including hidden objects",
            "render_eligible_definition": "object and collection render flags plus active view-layer exclusion; camera framing, occlusion and material opacity untested",
        },
        "evaluation": {
            "scene": scene.name_full,
            "view_layer": view_layer.name,
            "frame": int(scene.frame_current),
            "subframe": _float_value(scene.frame_subframe),
            "units": {
                "system": scene.unit_settings.system,
                "length_unit": scene.unit_settings.length_unit,
                "meters_per_blender_unit": meters_per_unit,
            },
        },
        "summary": summary,
        "meshes": meshes,
    }


def _write_json(path: Path, document: dict[str, Any]) -> None:
    encoded = (json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(encoded)
    temporary.replace(path)


def blender_main(argv: list[str] | None = None) -> None:
    """Blender process entry point; all path/hash guards are repeated in-process."""
    args = _blender_args(list(sys.argv[1:] if argv is None else argv))
    source = validate_source(args.root, args.input, args.sha256)
    output = resolve_receipt_path(args.root, args.output, source["path"])

    import bpy

    if bpy.app.version_string != SUPPORTED_BLENDER_VERSION:
        raise MeshAuditError(
            f"Blender {SUPPORTED_BLENDER_VERSION} is required; received {bpy.app.version_string}"
        )
    if source["format"] == "blend":
        result = bpy.ops.wm.open_mainfile(
            filepath=str(source["path"]),
            load_ui=False,
            use_scripts=False,
        )
        if "FINISHED" not in result:
            raise MeshAuditError("Blender did not finish opening the source .blend")
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        result = bpy.ops.import_scene.gltf(filepath=str(source["path"]))
        if "FINISHED" not in result:
            raise MeshAuditError("Blender did not finish importing the source GLB")

    if sha256_file(source["path"]) != source["sha256"]:
        raise MeshAuditError("source hash changed during Blender inspection")
    receipt = _build_receipt(bpy, source)
    _write_json(output, receipt)
    if sha256_file(source["path"]) != source["sha256"]:
        output.unlink(missing_ok=True)
        raise MeshAuditError("source hash changed while writing the Blender receipt")


if __name__ == "__main__":
    try:
        blender_main()
    except Exception as exc:
        print(f"MODEL_MESH_AUDIT_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
