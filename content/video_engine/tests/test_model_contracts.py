from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

from content.video_engine.src.modeling.contracts import (
    ModelContractError,
    validate_model_asset,
    validate_model_inspection,
    validate_model_scene,
)


ENGINE_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "modeling" / "contracts"
SCHEMA_NAMES = (
    "model_asset.v1.schema.json",
    "model_scene.v1.schema.json",
    "model_inspection.v1.schema.json",
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _materialize_project(tmp_path: Path) -> tuple[Path, dict[str, dict[str, Any]]]:
    root = tmp_path / "project"
    shutil.copytree(FIXTURE_ROOT, root)
    templates = json.loads((root / "models.json").read_text(encoding="utf-8"))["models"]

    catalog_rows: list[dict[str, Any]] = []
    for template in templates:
        resource_path = template["path"]
        resource_digest = _sha(root / resource_path)
        catalog_kind = {
            "character": "actor",
            "prop": "prop",
            "environment": "world",
        }[template["asset_kind"]]
        catalog_rows.append(
            {
                "asset_id": template["asset_id"],
                "path": resource_path,
                "sha256": resource_digest,
                "kind": catalog_kind,
                "style_version": "model-contract-fixture-v1",
                "semantic_tags": [template["asset_kind"], "fixture"],
                "resolution_tier": 1,
                "render_eligible": True,
                "review_state": "operator_approved",
                "provenance": {"approved_by": "fixture-operator", "approved_on": "fixture"},
            }
        )
    catalog = {
        "schema_version": "asset_catalog.v1",
        "project_root": ".",
        "resolution_order": ["exact_semantic_match"],
        "assets": catalog_rows,
    }
    catalog_path = root / "records" / "asset-catalog.json"
    _write_json(catalog_path, catalog)
    approval = {
        "schema_version": "model_approval_record.v1",
        "approval_id": "contract-fixture-approval",
        "assets": [
            {"asset_id": row["asset_id"], "path": row["path"], "sha256": row["sha256"]}
            for row in catalog_rows
        ],
    }
    approval_path = root / "records" / "approval.json"
    _write_json(approval_path, approval)

    catalog_digest = _sha(catalog_path)
    approval_digest = _sha(approval_path)
    models: dict[str, dict[str, Any]] = {}
    for template in templates:
        resource_specs = [
            {
                "resource_id": template["resource_id"],
                "resource_kind": template["resource_kind"],
                "path": template["path"],
            },
            *template.get("additional_resources", []),
        ]
        resources = [
            {
                **resource,
                "sha256": _sha(root / resource["path"]),
            }
            for resource in resource_specs
        ]
        resource_digest = next(row["sha256"] for row in resources if row["resource_id"] == template["resource_id"])
        model = {
            "schema_version": "model_asset.v1",
            "asset_id": template["asset_id"],
            "revision": {"revision_id": template["revision_id"], "revision_number": 1},
            "asset_kind": template["asset_kind"],
            "resources": resources,
            "catalog_reference": {
                "asset_id": template["asset_id"],
                "path": "records/asset-catalog.json",
                "sha256": catalog_digest,
                "resource_id": template["resource_id"],
            },
            "approval_reference": {
                "record_id": "contract-fixture-approval",
                "path": "records/approval.json",
                "sha256": approval_digest,
                "resource_id": template["resource_id"],
            },
            "coordinate_system": template["coordinate_system"],
            "capabilities": template["capabilities"],
            "source_lineage": [],
            "provenance": {
                "authoring_method": "native",
                "tool_name": "fixture-builder",
                "tool_version": "1",
                "licenses": {
                    "tool": "GPL-3.0-or-later",
                    "mesh": "CC0-1.0",
                    "texture": "CC0-1.0",
                    "motion": "not_applicable",
                },
            },
        }
        for optional_key in ("proportion_parameters", "materials", "uv_sets", "view_envelope"):
            if optional_key in template:
                model[optional_key] = template[optional_key]
        model_path = root / "models" / f"{template['asset_id']}.json"
        _write_json(model_path, model)
        models[template["asset_id"]] = model
    return root, models


def _scene(root: Path) -> dict[str, Any]:
    scene = json.loads((root / "scene-template.json").read_text(encoding="utf-8"))
    for binding in scene["bindings"]:
        binding["descriptor_sha256"] = _sha(root / binding["descriptor_path"])
    source_path = root / "assets" / "source-video.fixture"
    scene["source_time_mappings"][0]["sha256"] = _sha(source_path)
    return scene


def _trusted_paths(root: Path) -> dict[str, Path]:
    return {
        "trusted_catalog_path": root / "records" / "asset-catalog.json",
        "trusted_approval_path": root / "records" / "approval.json",
    }


def _spoofed_record_paths(root: Path, model: dict[str, Any]) -> dict[str, Any]:
    catalog_path = root / "records" / "asset-catalog.json"
    approval_path = root / "records" / "approval.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    spoof_catalog_path = root / "records" / "spoof-catalog.json"
    spoof_approval_path = root / "records" / "spoof-approval.json"
    spoof_approval = json.loads(json.dumps(approval))
    spoof_approval["approval_id"] = "spoof-approval"
    _write_json(spoof_catalog_path, catalog)
    _write_json(spoof_approval_path, spoof_approval)
    spoofed = json.loads(json.dumps(model))
    spoofed["catalog_reference"]["path"] = "records/spoof-catalog.json"
    spoofed["catalog_reference"]["sha256"] = _sha(spoof_catalog_path)
    spoofed["approval_reference"]["path"] = "records/spoof-approval.json"
    spoofed["approval_reference"]["record_id"] = "spoof-approval"
    spoofed["approval_reference"]["sha256"] = _sha(spoof_approval_path)
    return spoofed


def _inspection(root: Path) -> dict[str, Any]:
    descriptor_path = "models/fighter-a.json"
    return {
        "schema_version": "model_inspection.v1",
        "inspection_id": "fixture-inspection-r1",
        "asset_id": "fighter-a",
        "revision_id": "fighter-a-r1",
        "descriptor_path": descriptor_path,
        "descriptor_sha256": _sha(root / descriptor_path),
        "verdicts": {
            "contract": "pass",
            "render": "not_run",
            "art": "not_reviewed",
            "operator": "not_reviewed",
        },
        "geometry": {
            "stored": {"vertices": 19158, "faces": 18486, "triangles": 36972},
            "evaluated": {"vertices": 13380, "faces": 13378, "triangles": 26756},
        },
        "render_artifacts": [],
    }


@pytest.mark.parametrize("schema_name", SCHEMA_NAMES)
def test_model_schemas_are_valid_draft7_documents(schema_name: str) -> None:
    schema = json.loads((ENGINE_ROOT / "configs" / schema_name).read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)


def test_character_prop_and_environment_assets_validate_and_keep_approval_external(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    assert {model["asset_kind"] for model in models.values()} == {"character", "prop", "environment"}
    for asset_id in models:
        result = validate_model_asset(
            root / "models" / f"{asset_id}.json",
            project_root=root,
            for_render=True,
            **_trusted_paths(root),
        )
        assert result["asset_id"] == asset_id
        assert "approval_reference" in result
        assert "approved" not in result
    assert "approval_status" not in result


def test_optional_asset_authoring_fields_validate_and_are_bounded(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    fighter = models["fighter-a"]
    assert fighter["materials"][0]["uv_set_id"] == "body_uv0"
    assert fighter["view_envelope"]["yaw_degrees"]["maximum"] == 90
    assert fighter["proportion_parameters"]["head_scale"] == 1.2
    assert set(fighter["provenance"]["licenses"]) == {"tool", "mesh", "texture", "motion"}
    validate_model_asset(fighter, project_root=root)

    oversized = json.loads(json.dumps(fighter))
    oversized["proportion_parameters"]["head_scale"] = 4.1
    with pytest.raises(ModelContractError, match="maximum"):
        validate_model_asset(oversized, project_root=root)

    bad_material = json.loads(json.dumps(fighter))
    bad_material["materials"][0]["roughness"] = 1.01
    with pytest.raises(ModelContractError, match="roughness"):
        validate_model_asset(bad_material, project_root=root)

    bad_view = json.loads(json.dumps(fighter))
    bad_view["view_envelope"]["yaw_degrees"] = {"minimum": 80, "maximum": -80}
    with pytest.raises(ModelContractError, match="minimum"):
        validate_model_asset(bad_view, project_root=root)

    bad_uv_resource = json.loads(json.dumps(fighter))
    bad_uv_resource["uv_sets"][0]["texture_resource_ids"] = ["missing-texture"]
    with pytest.raises(ModelContractError, match="unknown texture resource"):
        validate_model_asset(bad_uv_resource, project_root=root)


def test_imported_assets_require_hash_bound_source_lineage(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    imported = json.loads(json.dumps(models["fighter-a"]))
    imported["provenance"]["authoring_method"] = "imported"
    with pytest.raises(ModelContractError, match="source_lineage.*non-empty"):
        validate_model_asset(imported, project_root=root)

    source = root / "assets" / "source-video.fixture"
    imported["source_lineage"] = [
        {
            "source_id": "import-record",
            "relation": "created_from",
            "path": "assets/source-video.fixture",
            "sha256": _sha(source),
        }
    ]
    assert validate_model_asset(imported, project_root=root)["provenance"]["authoring_method"] == "imported"


def test_unknown_approval_authority_fields_are_rejected(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    model = models["fighter-a"] | {"approved": True}
    with pytest.raises(ModelContractError, match="Additional properties are not allowed"):
        validate_model_asset(model, project_root=root)


def test_world_units_are_typed_and_wrong_units_fail(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    model = json.loads(json.dumps(models["fighter-a"]))
    model["coordinate_system"]["unit"] = "cm"
    with pytest.raises(ModelContractError, match="unit"):
        validate_model_asset(model, project_root=root)

    model = json.loads(json.dumps(models["fighter-a"]))
    model["coordinate_system"]["forward_axis"] = model["coordinate_system"]["up_axis"]
    with pytest.raises(ModelContractError, match="must be distinct"):
        validate_model_asset(model, project_root=root)


def test_out_of_root_paths_and_stale_resource_hashes_fail(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    escaped = json.loads(json.dumps(models["fighter-a"]))
    escaped["resources"][0]["path"] = "../outside.blend"
    with pytest.raises(ModelContractError):
        validate_model_asset(escaped, project_root=root)

    stale = json.loads(json.dumps(models["fighter-a"]))
    stale["resources"][0]["sha256"] = "0" * 64
    with pytest.raises(ModelContractError, match="SHA-256 does not match"):
        validate_model_asset(stale, project_root=root)


def test_catalog_identity_and_approval_record_must_link_to_exact_resource(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    wrong_catalog_identity = json.loads(json.dumps(models["fighter-a"]))
    wrong_catalog_identity["catalog_reference"]["asset_id"] = "fighter-b"
    with pytest.raises(ModelContractError, match="asset_id does not match"):
        validate_model_asset(wrong_catalog_identity, project_root=root)

    broken_approval = json.loads(json.dumps(models["fighter-a"]))
    broken_approval["approval_reference"]["record_id"] = "another-record"
    with pytest.raises(ModelContractError, match="record_id does not match"):
        validate_model_asset(broken_approval, project_root=root)

    missing_approval = json.loads(json.dumps(models["fighter-a"]))
    del missing_approval["approval_reference"]
    with pytest.raises(ModelContractError, match="approval_reference"):
        validate_model_asset(missing_approval, project_root=root)

    mismatched_resources = json.loads(json.dumps(models["fighter-a"]))
    mismatched_resources["approval_reference"]["resource_id"] = "albedo"
    with pytest.raises(ModelContractError, match="same resource_id"):
        validate_model_asset(mismatched_resources, project_root=root)


def test_approval_record_must_cover_the_exact_catalogued_asset_bytes(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    approval_path = root / "records" / "approval.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    approval["assets"][0]["sha256"] = "0" * 64
    _write_json(approval_path, approval)
    model = json.loads(json.dumps(models["fighter-a"]))
    model["approval_reference"]["sha256"] = _sha(approval_path)

    with pytest.raises(ModelContractError, match="not linked to the exact asset id/path/hash"):
        validate_model_asset(model, project_root=root)


def test_approval_record_requires_explicit_asset_identity(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    approval_path = root / "records" / "approval.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    del approval["assets"][0]["asset_id"]
    _write_json(approval_path, approval)
    model = json.loads(json.dumps(models["fighter-a"]))
    model["approval_reference"]["sha256"] = _sha(approval_path)

    with pytest.raises(ModelContractError, match="not linked to the exact asset id/path/hash"):
        validate_model_asset(model, project_root=root)


def test_ineligible_catalogue_asset_is_valid_metadata_but_not_render_ready(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    catalog_path = root / "records" / "asset-catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    row = next(item for item in catalog["assets"] if item["asset_id"] == "fighter-a")
    row["render_eligible"] = False
    _write_json(catalog_path, catalog)
    new_digest = _sha(catalog_path)
    model_path = root / "models" / "fighter-a.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    model["catalog_reference"]["sha256"] = new_digest
    _write_json(model_path, model)

    validate_model_asset(model_path, project_root=root)
    with pytest.raises(ModelContractError, match="not render eligible"):
        validate_model_asset(model_path, project_root=root, for_render=True, **_trusted_paths(root))


def test_operator_approval_requires_existing_audit_provenance(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    catalog_path = root / "records" / "asset-catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    row = next(item for item in catalog["assets"] if item["asset_id"] == "fighter-a")
    row.pop("provenance")
    _write_json(catalog_path, catalog)
    model_path = root / "models" / "fighter-a.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))
    model["catalog_reference"]["sha256"] = _sha(catalog_path)
    _write_json(model_path, model)

    with pytest.raises(ModelContractError, match="requires provenance.approved_by"):
        validate_model_asset(model_path, project_root=root, for_render=True, **_trusted_paths(root))


def test_render_ready_validation_requires_independent_trusted_record_paths(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    model_path = root / "models" / "fighter-a.json"
    model = models["fighter-a"]
    validate_model_asset(model, project_root=root)
    with pytest.raises(ModelContractError, match="trusted_catalog_path"):
        validate_model_asset(model, project_root=root, for_render=True)

    spoofed = _spoofed_record_paths(root, model)
    _write_json(model_path, spoofed)
    validate_model_asset(model_path, project_root=root)
    with pytest.raises(ModelContractError, match="caller-supplied trusted catalogue"):
        validate_model_asset(model_path, project_root=root, for_render=True, **_trusted_paths(root))

    spoofed["catalog_reference"] = model["catalog_reference"]
    _write_json(model_path, spoofed)
    with pytest.raises(ModelContractError, match="caller-supplied trusted approval record"):
        validate_model_asset(model_path, project_root=root, for_render=True, **_trusted_paths(root))


def test_scene_binds_exact_revisions_authored_contacts_and_source_time(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    scene = _scene(root)
    result = validate_model_scene(scene, project_root=root)
    assert result["fps"] == {"numerator": 24, "denominator": 1}
    assert result["contacts"][0]["start_frame"] == 4
    assert result["events"][1]["event_type"] == "ground_impact"
    assert result["time_origin"] == {"scene_frame": 0, "scene_time_seconds": {"numerator": 0, "denominator": 1}}
    assert result["source_time_mappings"][0]["source_time_start_seconds"] == {"numerator": 5, "denominator": 1}
    assert result["camera"]["projection"] == "perspective"
    assert result["render_profile"]["resolution_px"] == [1080, 1920]
    assert result["motion_channels"][0]["semantic_target"] == "right_hand"


def test_render_ready_scene_uses_trusted_catalog_and_approval_anchors(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    scene = _scene(root)
    with pytest.raises(ModelContractError, match="trusted_catalog_path"):
        validate_model_scene(scene, project_root=root, for_render=True)
    validate_model_scene(scene, project_root=root, for_render=True, **_trusted_paths(root))

    model_path = root / "models" / "fighter-a.json"
    spoofed = _spoofed_record_paths(root, models["fighter-a"])
    _write_json(model_path, spoofed)
    scene = _scene(root)
    with pytest.raises(ModelContractError, match="caller-supplied trusted catalogue"):
        validate_model_scene(scene, project_root=root, for_render=True, **_trusted_paths(root))


def test_authored_scene_has_required_but_empty_source_mappings(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    scene = _scene(root)
    scene["source_time_mappings"] = []
    assert validate_model_scene(scene, project_root=root)["source_time_mappings"] == []
    assert validate_model_scene(scene, project_root=root, for_render=True, **_trusted_paths(root))["time_origin"]["scene_frame"] == 0

    del scene["source_time_mappings"]
    with pytest.raises(ModelContractError, match="source_time_mappings.*required property"):
        validate_model_scene(scene, project_root=root)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda s: s["participants"][0]["semantic_joint_requirements"].append("tail"), "unsupported semantic joint"),
        (lambda s: s["participants"][0]["face_control_requirements"].append("blink"), "unsupported face control"),
        (lambda s: s["attachments"][0].update(parent_socket="unknown_socket"), "parent socket"),
        (lambda s: s["attachments"][0].update(child_socket="unknown_socket"), "child socket"),
        (lambda s: s["contacts"][0].update(end_frame=11), "interval must satisfy"),
        (lambda s: s["events"][0].update(frame=10), "frame must be less than"),
        (lambda s: s["fps"].update(numerator=float("nan")), "number must be finite"),
        (lambda s: s["camera"].update(focal_length_mm=0), r"scene\['camera'\]"),
        (lambda s: s["time_origin"].update(scene_frame=1), "time_origin.*0 was expected"),
        (lambda s: s["motion_channels"][0]["keyframes"][1].update(frame=10), "frame must be less than"),
        (lambda s: s["motion_channels"][0].update(semantic_target="tail"), "target is not supported"),
        (lambda s: s["environment_collision_surfaces"][0].update(binding_id="fighter_a"), "must reference an environment"),
        (lambda s: s["art_treatment"].update(outline_width_px=33), "maximum"),
    ],
)
def test_scene_rejects_capability_mismatch_and_invalid_time(mutation: Any, message: str, tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    scene = _scene(root)
    mutation(scene)
    with pytest.raises(ModelContractError, match=message):
        validate_model_scene(scene, project_root=root)


def test_scene_rejects_stale_descriptor_hash_and_unsupported_version(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    scene = _scene(root)
    scene["bindings"][0]["descriptor_sha256"] = "0" * 64
    with pytest.raises(ModelContractError, match="SHA-256 does not match"):
        validate_model_scene(scene, project_root=root)

    scene = _scene(root)
    scene["schema_version"] = "model_scene.v2"
    with pytest.raises(ModelContractError, match="model_scene.v1"):
        validate_model_scene(scene, project_root=root)


def test_inspection_keeps_stored_and_evaluated_topology_and_verdicts_separate(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    receipt = validate_model_inspection(_inspection(root), project_root=root)
    assert receipt["geometry"]["stored"] == {"vertices": 19158, "faces": 18486, "triangles": 36972}
    assert receipt["geometry"]["evaluated"] == {"vertices": 13380, "faces": 13378, "triangles": 26756}
    assert receipt["verdicts"] == {
        "contract": "pass",
        "render": "not_run",
        "art": "not_reviewed",
        "operator": "not_reviewed",
    }


def test_operator_approved_inspection_requires_trusted_existing_approval_chain(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    receipt = _inspection(root)
    receipt["verdicts"]["operator"] = "approved"
    with pytest.raises(ModelContractError, match="trusted_catalog_path"):
        validate_model_inspection(receipt, project_root=root)
    validate_model_inspection(receipt, project_root=root, **_trusted_paths(root))

    spoofed = _spoofed_record_paths(root, models["fighter-a"])
    _write_json(root / "models" / "fighter-a.json", spoofed)
    receipt["descriptor_sha256"] = _sha(root / receipt["descriptor_path"])
    with pytest.raises(ModelContractError, match="caller-supplied trusted catalogue"):
        validate_model_inspection(receipt, project_root=root, **_trusted_paths(root))


def test_inspection_rejects_stale_render_artifact_and_negative_geometry(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    receipt = _inspection(root)
    receipt["geometry"]["evaluated"]["vertices"] = -1
    with pytest.raises(ModelContractError, match="minimum"):
        validate_model_inspection(receipt, project_root=root)

    receipt = _inspection(root)
    receipt["render_artifacts"] = [
        {"path": "../outside.png", "sha256": "0" * 64, "kind": "beauty"}
    ]
    with pytest.raises(ModelContractError):
        validate_model_inspection(receipt, project_root=root)

    receipt = _inspection(root)
    receipt["geometry"]["evaluated"].update(faces=3, triangles=0)
    with pytest.raises(ModelContractError, match="non-empty faces require"):
        validate_model_inspection(receipt, project_root=root)


def test_path_symlink_cannot_escape_project_root_when_supported(tmp_path: Path) -> None:
    root, models = _materialize_project(tmp_path)
    outside = tmp_path / "outside.fixture"
    outside.write_bytes(b"outside project")
    link = root / "assets" / "outside-link.fixture"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable on this host: {exc}")
    model = json.loads(json.dumps(models["fighter-a"]))
    model["resources"][0]["path"] = "assets/outside-link.fixture"
    model["resources"][0]["sha256"] = _sha(outside)
    with pytest.raises(ModelContractError, match="resolves outside"):
        validate_model_asset(model, project_root=root)


def test_schema_error_sorting_handles_mixed_array_and_property_paths(tmp_path: Path) -> None:
    root, _ = _materialize_project(tmp_path)
    scene = _scene(root)
    del scene["fps"]
    del scene["contacts"][0]["semantic_effector"]
    with pytest.raises(ModelContractError):
        validate_model_scene(scene, project_root=root)
