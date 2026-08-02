from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from PIL import Image

from content.video_engine.src.services.history_contracts import canonical_sha256
from content.video_engine.src.services.living_scenes import (
    LivingSceneValidationError,
    build_creative_inventory,
    validate_creative_inventory,
)


def _png(path: Path, color: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 18), color=color).save(path)


def test_inventory_hashes_media_and_prefers_manifest_approval(tmp_path: Path) -> None:
    project = tmp_path / "project"
    assets = project / "assets"
    approved = assets / "approved.png"
    reference = assets / "quarantine" / "candidate.png"
    superseded = assets / "superseded" / "old.png"
    _png(approved, "navy")
    _png(reference, "green")
    _png(superseded, "red")

    manifest = project / "asset-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "asset_manifest.v1",
                "assets": [
                    {
                        "id": "approved-asset",
                        "path": "assets/approved.png",
                        "render_eligible": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    inventory = build_creative_inventory(
        roots={"project-assets": assets},
        project_root=project,
        asset_manifests=[manifest],
    )
    validated = validate_creative_inventory(inventory)

    by_path = {item["relative_path"]: item for item in validated["items"]}
    assert by_path["approved.png"]["classification"] == "approved_reusable"
    assert by_path["approved.png"]["manifest_asset_ids"] == ["approved-asset"]
    assert by_path["quarantine/candidate.png"]["classification"] == "reference_only"
    assert by_path["superseded/old.png"]["classification"] == "superseded"
    assert by_path["approved.png"]["width"] == 32
    assert by_path["approved.png"]["height"] == 18


def test_inventory_rejects_escape_missing_file_and_hash_drift(tmp_path: Path) -> None:
    root = tmp_path / "assets"
    _png(root / "one.png", "black")
    inventory = build_creative_inventory(
        roots={"assets": root},
        project_root=tmp_path,
    )

    escaped = copy.deepcopy(inventory)
    escaped["items"][0]["relative_path"] = "../one.png"
    escaped["artifact_hash"] = canonical_sha256(escaped)
    with pytest.raises(LivingSceneValidationError, match="escapes inventory root"):
        validate_creative_inventory(escaped)

    stale = copy.deepcopy(inventory)
    stale["items"][0]["sha256"] = "0" * 64
    stale["artifact_hash"] = canonical_sha256(stale)
    with pytest.raises(LivingSceneValidationError, match="SHA-256"):
        validate_creative_inventory(stale)

    (root / "one.png").unlink()
    with pytest.raises(LivingSceneValidationError, match="file is missing"):
        validate_creative_inventory(inventory)
