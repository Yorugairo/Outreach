from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

import pytest

from content.video_engine.src.modeling.blender.mesh_audit import (
    MAX_GLB_JSON_CHUNK_BYTES,
    MeshAuditError,
    _bounds,
    _read_glb_document,
    _render_visibility,
    _scene_meters_per_unit,
    resolve_receipt_path,
    sha256_file,
    validate_source,
)
from content.video_engine.scripts.model_mesh_audit import execute_audit


ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = ROOT / "content/video_engine/tests/fixtures/modeling/mesh-audit"
if str(FIXTURE_DIR) not in sys.path:
    sys.path.insert(0, str(FIXTURE_DIR))
from synthetic_glb import _pack_glb, empty_glb_bytes, triangle_glb_bytes  # noqa: E402


BLENDER_INPUTS = ROOT / "content/video_engine/tests/fixtures/modeling/baseline/benchmark-inputs.json"


def _blender_executable() -> Path:
    benchmark = json.loads(BLENDER_INPUTS.read_text(encoding="utf-8"))
    return Path(benchmark["tools"]["blender"]["path"])


def test_hash_pinned_source_is_resolved_inside_caller_root(tmp_path: Path) -> None:
    root = tmp_path / "inputs"
    root.mkdir()
    source = root / "triangle.glb"
    source.write_bytes(triangle_glb_bytes())

    record = validate_source(root, "triangle.glb", sha256_file(source))

    assert record["relative_path"] == "triangle.glb"
    assert record["format"] == "glb"
    assert record["sha256"] == sha256_file(source)
    assert record["byte_size"] == source.stat().st_size


def test_stale_hash_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "inputs"
    root.mkdir()
    source = root / "candidate.blend"
    source.write_bytes(b"pinned bytes")

    with pytest.raises(MeshAuditError, match="stale source hash"):
        validate_source(root, source.name, "0" * 64)


def test_missing_and_unsupported_inputs_are_rejected(tmp_path: Path) -> None:
    root = tmp_path / "inputs"
    root.mkdir()

    with pytest.raises(MeshAuditError, match="does not exist"):
        validate_source(root, "missing.blend", "0" * 64)

    unsupported = root / "candidate.obj"
    unsupported.write_bytes(b"v 0 0 0\n")
    with pytest.raises(MeshAuditError, match="unsupported model format"):
        validate_source(root, unsupported.name, sha256_file(unsupported))


def test_path_escape_is_rejected_even_for_an_existing_hash_pinned_file(tmp_path: Path) -> None:
    root = tmp_path / "inputs"
    root.mkdir()
    outside = tmp_path / "outside.blend"
    outside.write_bytes(b"outside")

    with pytest.raises(MeshAuditError, match="escapes caller root"):
        validate_source(root, outside, sha256_file(outside))


def test_glb_external_resources_are_rejected(tmp_path: Path) -> None:
    document = {
        "asset": {"version": "2.0"},
        "buffers": [{"uri": "../outside.bin", "byteLength": 0}],
    }
    source = tmp_path / "external.glb"
    source.write_bytes(_pack_glb(document))

    with pytest.raises(MeshAuditError, match="external buffers URI is not allowed"):
        _read_glb_document(source)


def test_glb_oversized_json_chunk_is_rejected_before_read(tmp_path: Path) -> None:
    source = tmp_path / "oversized.glb"
    chunk_length = MAX_GLB_JSON_CHUNK_BYTES + 4
    with source.open("wb") as stream:
        stream.write(b"glTF" + struct.pack("<II", 2, 20 + chunk_length))
        stream.write(struct.pack("<I4s", chunk_length, b"JSON"))
        stream.truncate(20 + chunk_length)

    with pytest.raises(MeshAuditError, match="JSON chunk exceeds"):
        _read_glb_document(source)


def test_receipt_path_rejects_escape_and_existing_output(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    source = root / "candidate.glb"
    source.write_bytes(triangle_glb_bytes())
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    existing = root / "existing.json"
    existing.write_text("{}", encoding="utf-8")

    with pytest.raises(MeshAuditError, match="escapes caller root"):
        resolve_receipt_path(root, outside, source)
    with pytest.raises(MeshAuditError, match="already exists"):
        resolve_receipt_path(root, existing, source)

    linked = root / "linked.json"
    try:
        linked.symlink_to(outside)
    except OSError:
        pytest.skip("creating a symlink requires unavailable local privileges")
    with pytest.raises(MeshAuditError, match="escapes caller root"):
        resolve_receipt_path(root, linked, source)


def test_scene_scale_converts_local_and_world_bounds_to_meters() -> None:
    scene = SimpleNamespace(unit_settings=SimpleNamespace(scale_length=0.01))
    vertices = [SimpleNamespace(co=(0.0, 0.0, 0.0)), SimpleNamespace(co=(100.0, 200.0, 300.0))]

    class Translate:
        def __matmul__(self, point: tuple[float, float, float]) -> tuple[float, float, float]:
            return (point[0] + 50.0, point[1], point[2])

    scale = _scene_meters_per_unit(scene)
    assert _bounds(vertices, meters_per_unit=scale) == {
        "min": [0.0, 0.0, 0.0],
        "max": [1.0, 2.0, 3.0],
    }
    assert _bounds(vertices, Translate(), meters_per_unit=scale) == {
        "min": [0.5, 0.0, 0.0],
        "max": [1.5, 2.0, 3.0],
    }
    for invalid in (0.0, -1.0, float("nan"), float("inf")):
        scene.unit_settings.scale_length = invalid
        with pytest.raises(MeshAuditError, match="scene unit scale"):
            _scene_meters_per_unit(scene)


def test_render_eligibility_records_object_and_collection_flags() -> None:
    obj = SimpleNamespace(hide_render=False, hide_viewport=True)
    obj.hide_get = lambda *, view_layer: True
    obj.visible_get = lambda *, view_layer: False

    def layer(name: str, *, contains: bool, hidden: bool = False, excluded: bool = False):
        collection = SimpleNamespace(
            name_full=name, hide_render=hidden, objects=[obj] if contains else []
        )
        return SimpleNamespace(collection=collection, exclude=excluded, children=[])

    hidden = layer("Hidden widgets", contains=True, hidden=True)
    visible = layer("Renderable", contains=True)
    root = layer("Scene", contains=False)
    root.children = [hidden, visible]
    view_layer = SimpleNamespace(layer_collection=root)

    facts = _render_visibility(obj, view_layer)
    assert facts["render_eligible"] is True
    assert facts["hide_viewport"] is True
    assert facts["visible_in_viewport"] is False
    assert len(facts["collection_paths"]) == 2
    visible.exclude = True
    assert _render_visibility(obj, view_layer)["render_eligible"] is False
    visible.exclude = False
    obj.hide_render = True
    assert _render_visibility(obj, view_layer)["render_eligible"] is False


def test_synthetic_glb_audit_is_deterministic_and_reports_mesh_facts(tmp_path: Path) -> None:
    blender = _blender_executable()
    if not blender.is_file():
        pytest.skip(f"pinned Blender executable unavailable: {blender}")
    source = tmp_path / "synthetic-triangle.glb"
    source.write_bytes(triangle_glb_bytes())
    source_hash = sha256_file(source)

    first = execute_audit(
        root=tmp_path,
        input_path=source.name,
        expected_sha256=source_hash,
        output_path="first.json",
        blender_path=blender,
    )
    second = execute_audit(
        root=tmp_path,
        input_path=source.name,
        expected_sha256=source_hash,
        output_path="second.json",
        blender_path=blender,
    )

    assert sha256_file(source) == source_hash
    assert first == second
    assert first["schema"] == "model_mesh_audit.v1"
    assert first["source"]["path"] == "synthetic-triangle.glb"
    assert first["source"]["sha256"] == source_hash
    assert first["tool"]["version"] == "5.2.2 LTS"
    assert first["inspection_mode"]["embedded_scripts"] == "disabled"
    assert first["visual_quality_assessment"] == "not_performed"
    assert first["art_approval_assessment"] == "not_performed"
    assert first["summary"]["all_scene"]["mesh_object_count"] == 1
    assert first["summary"]["render_eligible"]["mesh_object_count"] == 1
    assert first["summary"]["render_eligible"]["stored"]["vertices"] == 3
    assert first["evaluation"]["units"]["meters_per_blender_unit"] == 1.0
    mesh = first["meshes"][0]
    assert mesh["visibility"]["render_eligible"] is True
    assert mesh["stored"]["vertices"] == 3
    assert mesh["stored"]["faces"] == 1
    assert mesh["stored"]["triangles"] == 1
    assert mesh["stored"]["connected_components"] == 1
    assert mesh["stored"]["boundary_edges"] == 3
    assert mesh["stored"]["loose_edges"] == 0
    assert len(mesh["stored"]["uv_layers"]) == 1
    assert mesh["stored"]["uv_layers"][0]["loop_uv_count"] == 3
    assert mesh["stored"]["uv_layers"][0]["bounds"] == {"min": [0.0, 0.0], "max": [1.0, 1.0]}
    assert "SyntheticBlue" in {material["name"] for material in mesh["materials"]}


def test_empty_geometry_is_rejected_by_blender_import(tmp_path: Path) -> None:
    blender = _blender_executable()
    if not blender.is_file():
        pytest.skip(f"pinned Blender executable unavailable: {blender}")
    source = tmp_path / "empty.glb"
    source.write_bytes(empty_glb_bytes())

    with pytest.raises(MeshAuditError, match="no mesh geometry"):
        execute_audit(
            root=tmp_path,
            input_path=source.name,
            expected_sha256=sha256_file(source),
            output_path="empty-receipt.json",
            blender_path=blender,
        )
    assert not (tmp_path / "empty-receipt.json").exists()
