"""Security and contract tests for review-only model asset intake."""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
from pathlib import Path

import pytest

from content.video_engine.src.modeling.assets import AssetIntakeError
from content.video_engine.src.modeling.importers import intake_model_bundle
from content.video_engine.src.modeling.contracts import ModelContractError, validate_model_asset

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).parent / "fixtures" / "modeling" / "assets"
NATIVE_FIXTURE = FIXTURES / "native-fighter.blend"

WORLD_COORDINATES = {
    "space": "world_3d",
    "unit": "m",
    "up_axis": "Z",
    "forward_axis": "Y",
    "handedness": "right",
    "origin": "fixture origin; pending review",
    "rest_pose": "unknown pending inspection",
}


def _character_capabilities() -> dict:
    return {
        "semantic_joints": ["head", "jaw", "left_hand", "right_hand", "left_foot"],
        "face_controls": ["jaw_open", "brow_raise"],
        "sockets": ["right_hand_socket"],
    }


def _intake(source: Path, project: Path, run: Path, **overrides: object) -> dict:
    options = {
        "project_root": project,
        "run_dir": run,
        "allowed_source_root": source.parent,
        "asset_id": "native-fighter",
        "revision_id": "native-fighter-r1",
        "asset_kind": "character",
        "coordinate_system": WORLD_COORDINATES,
        "capabilities": _character_capabilities(),
    }
    options.update(overrides)
    return intake_model_bundle(source, **options)  # type: ignore[arg-type]


def test_native_blend_is_copied_opaquely_and_round_trips_as_review_only(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    run = project / "runs" / "native-candidate"

    receipt = _intake(NATIVE_FIXTURE, project, run)

    staged = Path(receipt["staged_source_path"])
    assert staged.read_bytes() == NATIVE_FIXTURE.read_bytes()
    digest = hashlib.sha256(NATIVE_FIXTURE.read_bytes()).hexdigest()
    assert receipt["source_sha256"] == digest
    assert Path(receipt["store_path"]).read_bytes() == NATIVE_FIXTURE.read_bytes()
    assert Path(receipt["store_path"]).is_relative_to(run)

    descriptor = validate_model_asset(receipt["descriptor_path"], project_root=project)
    assert descriptor["provenance"]["authoring_method"] == "imported"
    assert descriptor["resources"][0]["sha256"] == digest
    catalog = json.loads(Path(receipt["catalog_path"]).read_text(encoding="utf-8"))
    row = catalog["assets"][0]
    assert row["review_state"] == "review_only"
    assert row["render_eligible"] is False
    record = json.loads(Path(receipt["intake_record_path"]).read_text(encoding="utf-8"))
    assert record["review_state"] == "review_only"
    assert record["render_eligible"] is False
    assert record["source_path"] == str(NATIVE_FIXTURE.absolute())
    assert record["source_sha256"] == digest
    assert record["dependency_claim"]["packed_claim"] is True
    assert record["dependency_claim"]["inspection_state"] == "unverified_blender_inspection"
    assert len(receipt["staged_resources"]) == 2

    with pytest.raises(ModelContractError, match="not render eligible"):
        validate_model_asset(
            receipt["descriptor_path"],
            project_root=project,
            for_render=True,
            trusted_catalog_path=receipt["catalog_path"],
            trusted_approval_path=receipt["intake_record_path"],
        )


def test_stale_source_hash_is_rejected_before_candidate_records_are_written(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    run = project / "runs" / "stale-hash"

    with pytest.raises(AssetIntakeError, match="expected_sha256"):
        _intake(NATIVE_FIXTURE, project, run, expected_sha256="0" * 64)

    assert not (run / "model-assets" / "candidates").exists()


def test_run_directory_must_be_strictly_contained_in_project_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside"

    with pytest.raises(AssetIntakeError, match="strict child"):
        _intake(NATIVE_FIXTURE, project, outside)

    assert not outside.exists()


def test_revision_collision_preserves_original_descriptor_catalog_and_store(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    allowed = tmp_path / "incoming"
    allowed.mkdir()
    source = allowed / "fighter.blend"
    shutil.copyfile(NATIVE_FIXTURE, source)
    shutil.copyfile(NATIVE_FIXTURE.with_name(NATIVE_FIXTURE.name + ".dependencies.json"),
                    source.with_name(source.name + ".dependencies.json"))
    run = project / "runs" / "immutable"
    first = _intake(source, project, run)
    descriptor_path = Path(first["descriptor_path"])
    catalog_path = Path(first["catalog_path"])
    store_path = Path(first["store_path"])
    original_descriptor = descriptor_path.read_bytes()
    original_catalog = catalog_path.read_bytes()
    original_store_object = store_path.read_bytes()

    source.write_bytes(b"different source bytes for the same revision\n")
    new_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    with pytest.raises(AssetIntakeError, match="different source bytes"):
        _intake(source, project, run)

    assert descriptor_path.read_bytes() == original_descriptor
    assert catalog_path.read_bytes() == original_catalog
    assert store_path.read_bytes() == original_store_object
    assert not (store_path.parent / new_digest).exists()


def test_gltf_external_resources_are_staged_relative_and_hash_verified(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    (incoming / "textures").mkdir(parents=True)
    (incoming / "meshes").mkdir()
    (incoming / "textures" / "skin.png").write_bytes(b"texture bytes")
    (incoming / "meshes" / "body.bin").write_bytes(b"mesh bytes")
    model = incoming / "fighter.gltf"
    model.write_text(json.dumps({"asset": {"version": "2.0"}, "buffers": [{"uri": "meshes/body.bin", "byteLength": 10}],
                                "images": [{"uri": "textures/skin.png"}]}), encoding="utf-8")
    run = project / "runs" / "gltf"
    options = {"project_root": project, "run_dir": run, "allowed_source_root": incoming,
               "asset_id": "fighter", "revision_id": "fighter-r1", "asset_kind": "character",
               "coordinate_system": WORLD_COORDINATES, "capabilities": _character_capabilities()}
    first = intake_model_bundle(model, **options)
    again = intake_model_bundle(model, **options)
    assert first["descriptor_path"] == again["descriptor_path"]
    assert len(first["staged_resources"]) == 3
    staged = {item["resource_id"]: Path(item["path"]) for item in first["staged_resources"]}
    assert staged["gltf-resource-1"].read_bytes() == b"mesh bytes"
    assert staged["gltf-resource-2"].read_bytes() == b"texture bytes"
    assert staged["gltf-resource-1"].relative_to(run).as_posix().endswith("meshes/body.bin")
    assert len(first["store_paths"]) == 3
    assert validate_model_asset(first["descriptor_path"], project_root=project)["revision"]["revision_id"] == "fighter-r1"


def test_glb_json_chunk_and_prop_environment_candidates(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    payload = json.dumps({"asset": {"version": "2.0"}, "buffers": [{"byteLength": 0}]}).encode()
    payload += b" " * (-len(payload) % 4)
    blob = b"glTF" + struct.pack("<II", 2, 20 + len(payload)) + struct.pack("<I4s", len(payload), b"JSON") + payload
    glb = incoming / "hinged-prop.glb"
    glb.write_bytes(blob)
    prop = intake_model_bundle(glb, project_root=project, run_dir=project / "runs" / "prop",
                               allowed_source_root=incoming, asset_id="hinged-prop", revision_id="r1",
                               asset_kind="prop", coordinate_system=WORLD_COORDINATES,
                               capabilities={"articulations": ["hinge"], "sockets": ["grip"]})
    assert prop["descriptor"]["asset_kind"] == "prop"
    env = intake_model_bundle(NATIVE_FIXTURE, project_root=project, run_dir=project / "runs" / "env",
                              allowed_source_root=NATIVE_FIXTURE.parent, asset_id="fight-stage", revision_id="r1",
                              asset_kind="environment", coordinate_system=WORLD_COORDINATES,
                              capabilities={"surfaces": [{"surface_id": "floor", "surface_type": "floor"}], "sockets": []})
    assert env["descriptor"]["asset_kind"] == "environment"
    assert env["review_state"] == "review_only"


def test_layer_sidecar_stages_planes_and_preserves_provenance(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "art"
    incoming.mkdir()
    plate = incoming / "stage.png"
    plate.write_bytes(b"diagnostic plate")
    (incoming / "back.png").write_bytes(b"diagnostic back")
    (incoming / "front.png").write_bytes(b"diagnostic front")
    sidecar = {"foreground": {"desk": "front.png"}, "layers": [
        {"path": "back.png", "role": "background", "depth": 1.0, "alpha": False, "generator": "depth-split"},
        {"path": "front.png", "role": "occluder", "depth": 1.4, "alpha": True, "generator": "depth-split"},
    ]}
    plate.with_suffix(".layers.json").write_text(json.dumps(sidecar), encoding="utf-8")
    receipt = intake_model_bundle(plate, project_root=project, run_dir=project / "runs" / "layered",
                                  allowed_source_root=incoming, asset_id="stage", revision_id="r1",
                                  asset_kind="environment", coordinate_system=WORLD_COORDINATES,
                                  capabilities={"surfaces": [{"surface_id": "floor", "surface_type": "floor"}], "sockets": []})
    record = json.loads(Path(receipt["intake_record_path"]).read_text(encoding="utf-8"))
    assert len(receipt["staged_resources"]) == 4
    assert [layer["role"] for layer in record["layers"]] == ["foreground", "background", "occluder"]
    assert record["review_state"] == "review_only"


@pytest.mark.parametrize("uri", ["../outside.bin", "%2e%2e/outside.bin", "https://example.com/a.bin",
                                      "file:///tmp/a.bin", "C:/Windows/a.bin", "//server/share.bin", "a\\b.bin"])
def test_gltf_refuses_nonlocal_or_traversing_uris_before_writes(tmp_path: Path, uri: str) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    model = incoming / "fighter.gltf"
    model.write_text(json.dumps({"buffers": [{"uri": uri}]}), encoding="utf-8")
    run = project / "runs" / "hostile"
    with pytest.raises(AssetIntakeError, match="local relative resource URI|escapes allowed_source_root"):
        intake_model_bundle(model, project_root=project, run_dir=run, allowed_source_root=incoming,
                            asset_id="fighter", revision_id="r1", asset_kind="character",
                            coordinate_system=WORLD_COORDINATES, capabilities=_character_capabilities())
    assert not run.exists()


def test_dependency_symlink_escape_is_refused(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside")
    link = incoming / "resource.bin"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation unavailable")
    model = incoming / "fighter.gltf"
    model.write_text(json.dumps({"buffers": [{"uri": "resource.bin"}]}), encoding="utf-8")
    with pytest.raises(AssetIntakeError, match="symlink"):
        intake_model_bundle(model, project_root=project, run_dir=project / "runs" / "hostile",
                            allowed_source_root=incoming, asset_id="fighter", revision_id="r1",
                            asset_kind="character", coordinate_system=WORLD_COORDINATES,
                            capabilities=_character_capabilities())


def test_layer_sidecar_refuses_traversal_before_any_run_files(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "art"
    incoming.mkdir()
    plate = incoming / "stage.png"
    plate.write_bytes(b"plate")
    (tmp_path / "outside.png").write_bytes(b"outside")
    plate.with_suffix(".layers.json").write_text(json.dumps({"foreground": {"front": "../outside.png"}}), encoding="utf-8")
    run = project / "runs" / "bad-layer"
    with pytest.raises(AssetIntakeError, match="local relative resource URI|escapes allowed_source_root"):
        intake_model_bundle(plate, project_root=project, run_dir=run, allowed_source_root=incoming,
                            asset_id="stage", revision_id="r1", asset_kind="environment",
                            coordinate_system=WORLD_COORDINATES,
                            capabilities={"surfaces": [{"surface_id": "floor", "surface_type": "floor"}], "sockets": []})
    assert not run.exists()


def test_additional_resource_stale_hash_and_output_symlink_are_refused(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    model = incoming / "fighter.gltf"
    model.write_text("{}", encoding="utf-8")
    texture = incoming / "skin.png"
    texture.write_bytes(b"skin")
    run = project / "runs" / "direct"
    resource = {"source_path": texture, "resource_id": "skin", "resource_kind": "texture", "expected_sha256": "0" * 64}
    with pytest.raises(AssetIntakeError, match="skin expected_sha256"):
        _intake(model, project, run, allowed_source_root=incoming, additional_resources=[resource],
                asset_id="fighter", revision_id="r1")
    assert not (run / "model-assets" / "candidates").exists()

    source = incoming / "original.blend"
    source.write_bytes(b"original")
    source.with_name(source.name + ".dependencies.json").write_text(
        json.dumps({"schema_version": "blend_dependencies.v1", "packed": True, "dependencies": []}), encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    target_dir = run / "model-assets" / "candidates" / "fighter" / "r1" / "resources"
    target_dir.parent.mkdir(parents=True)
    try:
        target_dir.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(AssetIntakeError, match="not a real directory"):
        _intake(source, project, run, allowed_source_root=incoming, asset_id="fighter", revision_id="r1")
    assert list(outside.iterdir()) == []


def test_derived_revision_links_immutable_parent_resource(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    original = incoming / "fighter.blend"
    original.write_bytes(b"original mesh")
    derived = incoming / "fighter-derived.blend"
    derived.write_bytes(b"derived mesh")
    for blend in (original, derived):
        blend.with_name(blend.name + ".dependencies.json").write_text(
            json.dumps({"schema_version": "blend_dependencies.v1", "packed": True, "dependencies": []}), encoding="utf-8")
    run = project / "runs" / "lineage"
    first = _intake(original, project, run, allowed_source_root=incoming, asset_id="fighter", revision_id="r1")
    second = _intake(derived, project, run, allowed_source_root=incoming, asset_id="fighter", revision_id="r2",
                     revision_number=2, parent_revision_id="r1", provenance={"authoring_method": "derived"})
    assert second["descriptor"]["revision"]["parent_revision_id"] == "r1"
    assert second["descriptor"]["source_lineage"][0]["sha256"] == first["source_sha256"]
    assert second["descriptor"]["source_lineage"][0]["relation"] == "derived_from"
    assert Path(first["staged_source_path"]).read_bytes() == b"original mesh"


def test_corrupt_existing_local_store_object_fails_closed(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    run = project / "runs" / "corrupt-store"
    digest = hashlib.sha256(NATIVE_FIXTURE.read_bytes()).hexdigest()
    object_path = run / "content-addressed-store" / "sha256" / digest
    object_path.parent.mkdir(parents=True)
    object_path.write_bytes(b"wrong bytes")
    with pytest.raises(AssetIntakeError, match="verification failed"):
        _intake(NATIVE_FIXTURE, project, run)
    assert object_path.read_bytes() == b"wrong bytes"
    assert not (run / "model-assets" / "candidates" / "native-fighter" / "native-fighter-r1" / "model_asset.v1.json").exists()


def test_blend_requires_manifest_and_stages_declared_external_dependencies(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    blend = incoming / "fighter.blend"
    blend.write_bytes(b"opaque blender bytes")
    run = project / "runs" / "blend"
    with pytest.raises(AssetIntakeError, match="requires a local .*dependencies.json"):
        _intake(blend, project, run, allowed_source_root=incoming)
    assert not run.exists()

    texture = incoming / "skin.png"
    texture.write_bytes(b"skin texture")
    declared = hashlib.sha256(texture.read_bytes()).hexdigest()
    manifest = blend.with_name(blend.name + ".dependencies.json")
    manifest.write_text(json.dumps({"schema_version": "blend_dependencies.v1", "packed": False,
                                    "dependencies": [{"uri": "skin.png", "sha256": declared}]}), encoding="utf-8")
    receipt = _intake(blend, project, run, allowed_source_root=incoming)
    assert len(receipt["staged_resources"]) == 3
    assert {item["resource_id"] for item in receipt["staged_resources"]} == {
        "primary-source", "blend-dependency-manifest", "blend-dependency-1"}
    assert receipt["dependency_claim"] == {
        "manifest_resource_id": "blend-dependency-manifest", "packed_claim": False,
        "declared_dependency_count": 1, "inspection_state": "unverified_blender_inspection"}
    assert receipt["render_eligible"] is False

    wrong = json.loads(manifest.read_text(encoding="utf-8"))
    wrong["dependencies"][0]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(wrong), encoding="utf-8")
    with pytest.raises(AssetIntakeError, match="expected_sha256"):
        _intake(blend, project, project / "runs" / "wrong-hash", allowed_source_root=incoming)


@pytest.mark.parametrize("uri", ["../outside.png", "https://example.com/skin.png", "C:/skin.png"])
def test_blend_manifest_rejects_unsafe_dependency_uri(tmp_path: Path, uri: str) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    blend = incoming / "fighter.blend"
    blend.write_bytes(b"opaque")
    blend.with_name(blend.name + ".dependencies.json").write_text(json.dumps({
        "schema_version": "blend_dependencies.v1", "packed": False,
        "dependencies": [{"uri": uri, "sha256": "0" * 64}],
    }), encoding="utf-8")
    run = project / "runs" / "unsafe"
    with pytest.raises(AssetIntakeError, match="resource URI|local relative resource URI"):
        _intake(blend, project, run, allowed_source_root=incoming)
    assert not run.exists()


def test_gltf_parent_relative_shared_resource_within_allowed_root(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    allowed = tmp_path / "incoming"
    (allowed / "models").mkdir(parents=True)
    (allowed / "shared").mkdir()
    shared = allowed / "shared" / "skin.png"
    shared.write_bytes(b"shared texture")
    model = allowed / "models" / "fighter.gltf"
    model.write_text(json.dumps({"images": [{"uri": "../shared/skin.png"}]}), encoding="utf-8")
    run = project / "runs" / "shared"
    receipt = _intake(model, project, run, allowed_source_root=allowed)
    staged_model = Path(receipt["staged_source_path"])
    assert (staged_model.parent / "../shared/skin.png").resolve().read_bytes() == b"shared texture"
    assert len(receipt["staged_resources"]) == 2


def test_file_aggregate_and_dependency_quotas_fail_before_staging(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    model = incoming / "fighter.gltf"
    (incoming / "a.bin").write_bytes(b"aaa")
    (incoming / "b.bin").write_bytes(b"bbb")
    model.write_text(json.dumps({"buffers": [{"uri": "a.bin"}, {"uri": "b.bin"}]}), encoding="utf-8")
    run = project / "runs" / "quotas"
    common = {"allowed_source_root": incoming, "asset_id": "fighter", "revision_id": "r1"}
    with pytest.raises(AssetIntakeError, match="per-file byte quota"):
        _intake(model, project, run, max_file_bytes=8, **common)
    assert not run.exists()
    with pytest.raises(AssetIntakeError, match="aggregate byte quota"):
        _intake(model, project, run, max_total_bytes=model.stat().st_size + 5, **common)
    assert not run.exists()
    with pytest.raises(AssetIntakeError, match="max_dependencies"):
        _intake(model, project, run, max_dependencies=1, **common)
    assert not run.exists()
    with pytest.raises(AssetIntakeError, match="finite nonnegative integer quota"):
        _intake(model, project, run, max_file_bytes=float("inf"), **common)
    assert not run.exists()


def test_dependency_count_preempts_missing_gltf_paths(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    (incoming / "present.bin").write_bytes(b"present")
    model = incoming / "fighter.gltf"
    model.write_text(json.dumps({"buffers": [
        {"uri": "present.bin"}, {"uri": "./present.bin"}, {"uri": "missing.bin"},
    ]}), encoding="utf-8")
    run = project / "runs" / "count-gltf"
    with pytest.raises(AssetIntakeError, match="max_dependencies quota"):
        _intake(model, project, run, allowed_source_root=incoming, max_dependencies=1)
    assert not run.exists()


def test_dependency_count_preempts_missing_blender_and_layer_paths(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    blend = incoming / "fighter.blend"
    blend.write_bytes(b"opaque")
    blend.with_name(blend.name + ".dependencies.json").write_text(json.dumps({
        "schema_version": "blend_dependencies.v1", "packed": False,
        "dependencies": [{"uri": "missing.png", "sha256": "0" * 64}],
    }), encoding="utf-8")
    with pytest.raises(AssetIntakeError, match="max_dependencies quota"):
        _intake(blend, project, project / "runs" / "count-blend",
                allowed_source_root=incoming, max_dependencies=1)
    assert not (project / "runs" / "count-blend").exists()

    plate = incoming / "stage.png"
    plate.write_bytes(b"plate")
    plate.with_suffix(".layers.json").write_text(json.dumps({"foreground": {"front": "missing.png"}}), encoding="utf-8")
    with pytest.raises(AssetIntakeError, match="max_dependencies quota"):
        _intake(plate, project, project / "runs" / "count-layer",
                allowed_source_root=incoming, max_dependencies=1)
    assert not (project / "runs" / "count-layer").exists()


def test_raw_duplicate_uri_cap_preempts_missing_resource_lookup(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    incoming = tmp_path / "incoming"
    incoming.mkdir()
    model = incoming / "fighter.gltf"
    model.write_text(json.dumps({"images": [{"uri": "missing.png"}] * 17}), encoding="utf-8")
    gltf_run = project / "runs" / "raw-gltf"
    with pytest.raises(AssetIntakeError, match="raw dependency declarations exceed quota"):
        _intake(model, project, gltf_run, allowed_source_root=incoming, max_dependencies=1)
    assert not gltf_run.exists()

    plate = incoming / "stage.png"
    plate.write_bytes(b"plate")
    plate.with_suffix(".layers.json").write_text(json.dumps({
        "foreground": {f"front-{index}": "missing.png" for index in range(17)},
    }), encoding="utf-8")
    layer_run = project / "runs" / "raw-layer"
    with pytest.raises(AssetIntakeError, match="raw dependency declarations exceed quota"):
        _intake(plate, project, layer_run, allowed_source_root=incoming, max_dependencies=1)
    assert not layer_run.exists()
