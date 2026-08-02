from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

from content.video_engine.src.services.asset_resolver import (
    ASSET_MANIFEST_VERSION,
    AssetManifestImmutableError,
    AssetManifestValidationError,
    AssetResolverService,
    canonical_sha256,
    file_sha256,
    validate_asset_manifest,
)


ENGINE_ROOT = Path(__file__).resolve().parents[1]


def _manifest(
    tmp_path: Path,
    *,
    permission: str = "operator_owned",
    render_eligible: bool | None = True,
    file_name: str = "archive/kano.jpg",
    **asset_overrides: object,
) -> tuple[dict[str, object], Path, Path]:
    project_root = tmp_path / "project"
    job_dir = tmp_path / "job"
    asset_path = project_root / file_name
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_bytes(b"rights-reviewed-local-fixture")
    asset: dict[str, object] = {
        "id": "kano-portrait",
        "path": file_name,
        "sha256": file_sha256(asset_path),
        "kind": "archival_photo",
        "role": "archive",
        "origin": "operator:history-of-bjj",
        "rights": {
            "permission": permission,
            "reviewed": permission not in {"unverified", "research_only", "fair_use"},
            "reviewed_by": "operator",
            "source_url": "https://archive.example/kano",
        },
    }
    if render_eligible is not None:
        asset["render_eligible"] = render_eligible
    asset.update(asset_overrides)
    return {
        "schema_version": ASSET_MANIFEST_VERSION,
        "manifest_id": "history-of-bjj-episode-1-assets",
        "job_id": "job-1",
        "assets": [asset],
    }, project_root, job_dir


def test_schema_and_template_are_valid_contract_documents() -> None:
    schema = json.loads(
        (ENGINE_ROOT / "configs" / "asset_manifest.schema.json").read_text(
            encoding="utf-8"
        )
    )
    template = json.loads(
        (ENGINE_ROOT / "templates" / "asset_manifest.json").read_text(encoding="utf-8")
    )
    assert list(Draft7Validator(schema).iter_errors(template)) == []
    assert template["schema_version"] == ASSET_MANIFEST_VERSION


def test_resolver_verifies_hashes_and_emits_local_renderer_contract(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(tmp_path)
    result = AssetResolverService(project_root, job_dir).resolve(manifest)

    resolved_path = job_dir / "resolved_assets.json"
    credits_path = job_dir / "credits.json"
    assert resolved_path.exists()
    assert credits_path.exists()
    resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
    credits = json.loads(credits_path.read_text(encoding="utf-8"))
    assert result["asset_ids"] == ["kano-portrait"]
    assert resolved["assets"][0]["asset_id"] == "kano-portrait"
    assert resolved["assets"][0]["path"] == "archive/kano.jpg"
    assert "source_url" not in json.dumps(resolved)
    assert credits["credits"][0]["asset_id"] == "kano-portrait"
    assert credits["credits"][0]["source_url"] == "https://archive.example/kano"


def test_hash_mismatch_and_path_escape_fail_closed(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(tmp_path)
    manifest["assets"][0]["sha256"] = "0" * 64  # type: ignore[index]
    with pytest.raises(AssetManifestValidationError, match="does not match local bytes"):
        AssetResolverService(project_root, job_dir).resolve(manifest)

    escaped, project_root, job_dir = _manifest(tmp_path / "escaped")
    outside = tmp_path / "outside.jpg"
    outside.write_bytes(b"outside")
    escaped["assets"][0]["path"] = "../outside.jpg"  # type: ignore[index]
    escaped["assets"][0]["sha256"] = file_sha256(outside)  # type: ignore[index]
    with pytest.raises(AssetManifestValidationError, match="inside project/job roots"):
        AssetResolverService(project_root, job_dir).resolve(escaped)


def test_remote_asset_is_rejected_even_when_hash_is_declared(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(tmp_path)
    manifest["assets"][0]["path"] = "https://archive.example/kano.jpg"  # type: ignore[index]
    with pytest.raises(AssetManifestValidationError, match="local path"):
        AssetResolverService(project_root, job_dir).validate(manifest)


@pytest.mark.parametrize(
    ("permission", "reason"),
    [
        ("fair_use", "permission:fair_use"),
        ("unverified", "permission:unverified"),
        ("research_only", "permission:research_only"),
    ],
)
def test_quarantined_permissions_never_render(
    tmp_path: Path, permission: str, reason: str
) -> None:
    manifest, project_root, job_dir = _manifest(
        tmp_path,
        permission=permission,
        render_eligible=False,
    )
    result = AssetResolverService(project_root, job_dir).resolve(manifest)
    assert result["assets"] == []
    assert result["quarantined_assets"][0]["asset_id"] == "kano-portrait"
    assert reason in result["quarantined_assets"][0]["reasons"]


def test_likeness_logo_and_alteration_gates_quarantine_assets(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(
        tmp_path,
        render_eligible=False,
        living_person=True,
        likeness={"living": True, "approved": False},
        is_logo=True,
        logo_permission=False,
        altered=True,
        alteration_policy={"allowed": False},
    )
    result = AssetResolverService(project_root, job_dir).resolve(manifest)
    reasons = result["quarantined_assets"][0]["reasons"]
    assert "living_person_likeness_requires_operator_approval" in reasons
    assert "logo_permission_required" in reasons
    assert "alteration_not_permitted_by_policy" in reasons


def test_cc_by_requires_attribution_and_credits_are_complete(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(
        tmp_path,
        permission="cc_by",
        attribution={"creator": "Archive Creator", "title": "Kano"},
    )
    result = AssetResolverService(project_root, job_dir).resolve(manifest)
    assert result["assets"][0]["asset_id"] == "kano-portrait"
    credits = json.loads((job_dir / "credits.json").read_text(encoding="utf-8"))
    assert "Archive Creator" in credits["credits"][0]["credit"]

    missing, project_root, job_dir = _manifest(tmp_path / "missing-credit", permission="cc_by")
    missing["assets"][0]["render_eligible"] = False  # type: ignore[index]
    result = AssetResolverService(project_root, job_dir).resolve(missing)
    assert result["assets"] == []
    assert "attribution_required_for_license" in result["quarantined_assets"][0]["reasons"]


def test_job_local_artifacts_are_immutable_and_hash_stable(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(tmp_path)
    service = AssetResolverService(project_root, job_dir)
    first = service.resolve(manifest)
    second = service.resolve(manifest)
    assert first["artifact_hash"] == second["artifact_hash"]
    assert canonical_sha256(first) == canonical_sha256(second)

    changed = json.loads(json.dumps(manifest))
    changed["assets"][0]["role"] = "changed"
    with pytest.raises(AssetManifestImmutableError, match="immutable"):
        service.resolve(changed)


def test_validation_helper_is_importable_by_a_cli(tmp_path: Path) -> None:
    manifest, project_root, job_dir = _manifest(tmp_path)
    path = tmp_path / "asset_manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    normalized = validate_asset_manifest(
        path,
        project_root=project_root,
        job_dir=job_dir,
    )
    assert normalized["schema_version"] == ASSET_MANIFEST_VERSION
