from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.services.production_console_snapshot import (
    ProductionConsoleSnapshotError,
    compile_production_console_snapshot,
    validate_production_console_snapshot,
)


ROOT = Path(__file__).resolve().parents[3]
PROJECT = (
    ROOT
    / "content"
    / "video_engine"
    / "projects"
    / "systems-and-blowups"
    / "pilots"
    / "current-bubble-mechanism"
)


def test_compile_real_current_bubble_snapshot_is_deterministic(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"
    first = compile_production_console_snapshot(PROJECT, output_path=first_path)
    second = compile_production_console_snapshot(PROJECT, output_path=second_path)

    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    assert len(first["scenes"]) == 11
    assert len(first["words"]) > 2_000
    assert first["scenes"][0]["scene_id"] == "finance-scene-01"
    assert first["scenes"][0]["start_s"] == 0
    assert first["reviews"][0]["scope"] == "production_visuals"
    assert first["reviews"][0]["state"] == "approved"
    assert all(asset["path_root"] in {"project", "repository"} for asset in first["assets"])
    assert any("catalog has not been generated" in item for item in first["degraded_inputs"])
    validate_production_console_snapshot(first)


def test_snapshot_requires_explicit_catalog_evidence_eligibility(tmp_path: Path) -> None:
    catalog_dir = PROJECT / "edit" / "production-console-test-catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    image_path = catalog_dir / "slide.png"
    image_path.write_bytes(b"approved-visual")
    import hashlib

    catalog_path = catalog_dir / "catalog.json"
    catalog_path.write_text(
        json.dumps(
            {
                "assets": [
                    {
                        "asset_id": "deck-s01-production-v1",
                        "label": "Deck slide 1",
                        "path": "slide.png",
                        "sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
                        "deck_id": "deck",
                        "slide_number": 1,
                        "width": 1376,
                        "height": 768,
                        "rights_state": "operator_authorized",
                        "context_status": "operator_verified",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    try:
        snapshot = compile_production_console_snapshot(
            PROJECT,
            production_visual_catalog=catalog_path,
            output_path=tmp_path / "snapshot.json",
        )
    finally:
        image_path.unlink(missing_ok=True)
        catalog_path.unlink(missing_ok=True)
        catalog_dir.rmdir()

    asset = next(item for item in snapshot["assets"] if item["asset_id"] == "deck-s01-production-v1")
    assert asset["approval_scope"] == "production_visuals"
    assert asset["evidence_eligible"] is False
    assert asset["path_root"] == "repository"


def test_real_teacher_stamped_catalog_retains_context_and_factual_approval(tmp_path: Path) -> None:
    catalog = (
        ROOT
        / "content"
        / "video_engine"
        / "projects"
        / "systems-and-blowups"
        / "sources"
        / "decks"
        / "teacher-stamped-production-visuals"
        / "teacher-stamped-production-visuals-manifest.v1.json"
    )
    snapshot = compile_production_console_snapshot(
        PROJECT,
        repository_root=ROOT,
        production_visual_catalog=catalog,
        output_path=tmp_path / "catalog-snapshot.json",
    )

    visuals = [asset for asset in snapshot["assets"] if asset["source_kind"] == "production_visual"]
    assert len(visuals) == 86
    assert all(asset["path_root"] == "repository" for asset in visuals)
    assert all(asset["approval_scope"] == "production_visuals" for asset in visuals)
    assert all(asset["evidence_eligible"] is True for asset in visuals)
    assert all(asset["context_status"] == "operator_verified" for asset in visuals)
    assert visuals[0]["label"] != visuals[0]["asset_id"]


def test_snapshot_fails_closed_when_required_input_is_missing(tmp_path: Path) -> None:
    with pytest.raises(ProductionConsoleSnapshotError, match="scene_flow"):
        compile_production_console_snapshot(tmp_path)


def test_snapshot_rejects_stale_artifact_hash() -> None:
    snapshot = compile_production_console_snapshot(PROJECT)
    snapshot["project_id"] = "tampered"
    with pytest.raises(ProductionConsoleSnapshotError, match="artifact_hash"):
        validate_production_console_snapshot(snapshot)
