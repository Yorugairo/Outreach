from __future__ import annotations

import json
from pathlib import Path

import pytest

from content.video_engine.src.models import StageContext, VideoRun
from content.video_engine.src.repositories.file_repository import FileBackedVideoJobRepository
from content.video_engine.src.services.technique_manifest import (
    MANIFEST_VERSION,
    TechniqueManifestService,
    TechniqueManifestValidationError,
)


def _manifest(slug: str = "armbar-from-guard") -> dict:
    return {
        "schema_version": MANIFEST_VERSION,
        "slug": slug,
        "style_preset": "flat_vector_bjj",
        "rights": {
            "permission": "operator_owned",
            "source": "operator:armbar-review",
            "reviewed": True,
            "reviewed_by": "operator",
        },
        "references": [
            {
                "id": "armbar-review",
                "source": "operator:armbar-review",
                "permission": "operator_owned",
                "reviewed": True,
            }
        ],
        "actions": [
            {
                "id": "wrist-control",
                "state_from": "closed_guard_posture_broken",
                "action": "two_on_one_wrist_control",
                "state_to": "wrist_control_hip_frame",
                "contact": "attacker_wrist",
                "motion_path": "linear",
                "reviewed": True,
                "reference_refs": ["armbar-review"],
            }
        ],
    }


def test_explicit_manifest_is_normalized_and_persisted(tmp_path: Path) -> None:
    service = TechniqueManifestService()
    output = tmp_path / "technique_manifest.json"

    normalized = service.persist(_manifest(), output)

    assert normalized["schema_version"] == MANIFEST_VERSION
    assert normalized["rights"]["permission"] == "operator_owned"
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["actions"][0]["state_to"] == (
        "wrist_control_hip_frame"
    )


def test_slug_matched_sidecar_is_discovered_from_configured_root(tmp_path: Path) -> None:
    root = tmp_path / "references"
    root.mkdir()
    path = root / "armbar-from-guard.visual.json"
    path.write_text(json.dumps(_manifest()), encoding="utf-8")

    discovered = TechniqueManifestService().discover("armbar-from-guard", manifest_root=root)

    assert discovered == path


def test_invalid_actions_report_each_missing_mechanic_and_permission() -> None:
    invalid = _manifest()
    invalid["rights"] = {"permission": "unknown", "source": "", "reviewed": False}
    invalid["actions"] = [
        {"id": "first", "reviewed": False},
        {
            "id": "second",
            "state_from": "start",
            "action": "move",
            "state_to": "end",
            "contact": "wrist",
            "motion_path": "arc",
            "reviewed": True,
        },
    ]

    with pytest.raises(TechniqueManifestValidationError) as raised:
        TechniqueManifestService().validate(invalid)

    detail = " ".join(raised.value.errors)
    assert "missing state_from" in detail
    assert "missing contact" in detail
    assert "missing motion_path" in detail
    assert "permission" in detail
    assert "reviewed action state is required" in detail


def test_run_stage_records_an_explicit_missing_sidecar_skip(tmp_path: Path) -> None:
    repository = FileBackedVideoJobRepository(tmp_path / "jobs")
    run = VideoRun(source_ref="armbar-from-guard.json")
    repository.create_run(run)
    context = StageContext(
        repository=repository,
        configs={"technique_manifest_root": tmp_path / "no-references"},
        job_dir=repository.job_dir(run.id),
    )

    output = TechniqueManifestService().run_stage(run, context)

    assert output.summary["available"] is False
    artifact = json.loads((context.job_dir / "technique_manifest.json").read_text(encoding="utf-8"))
    assert artifact["available"] is False
    assert artifact["actions"] == []
