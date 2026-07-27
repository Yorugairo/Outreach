from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.config import (
    AgenticAnalysisSettings,
    AppConfig,
    DataForSEOSettings,
)
from src.models import AgenticAssessmentSnapshot
from src.repositories.sqlite_repository import SQLiteInsightRepository


def test_agentic_preflight_queue_status_and_review_are_durable(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(
        tmp_path / "insights.db",
        artifact_root=artifact_root,
    )
    config = AppConfig(
        dataforseo=DataForSEOSettings(None, None),
        agentic=AgenticAnalysisSettings(
            enabled=True,
            operator_approved=True,
            promotion_approved=True,
        ),
    )
    app = create_app(
        repository=repository,
        artifact_root=artifact_root,
        config=config,
        api_key="test-secret",
        environment="test",
    )
    headers = {"X-API-Key": "test-secret"}
    with TestClient(app) as client:
        created = client.post(
            "/api/runs",
            headers=headers,
            json={"url": "example.com", "mode": "quick", "max_pages": 1},
        )
        run_id = created.json()["run"]["id"]
        request = {
            "vertical_pack_version": "one_trade_network.v1",
            "analysis_mode": "standard",
            "target_facts": {"business_name": "Example Plumbing"},
        }
        preflight = client.post(
            f"/api/runs/{run_id}/agentic-analysis/preflight",
            headers=headers,
            json=request,
        )
        started = client.post(
            f"/api/runs/{run_id}/agentic-analysis",
            headers=headers,
            json=request,
        )
        job = repository.get_agentic_analysis_job(started.json()["job"]["id"])
        assessment = repository.save_agentic_assessment_snapshot(
            AgenticAssessmentSnapshot(
                job_id=job.id,
                evidence_pack_id=job.evidence_pack_id,
                evidence_pack_sha256=job.evidence_pack_sha256,
                runtime=job.requested_runtime,
                requested_model=job.requested_model,
                served_model=job.requested_model,
                served_provider=job.requested_provider,
                prompt_version=job.prompt_version,
                rubric_version=job.rubric_version,
                schema_version=job.schema_version,
                findings=[],
                validation_result={
                    "schema_valid": True,
                    "customer_safe": True,
                },
            )
        )
        status = client.get(
            f"/api/agentic-analysis/jobs/{job.id}",
            headers=headers,
        )
        reviewed = client.post(
            f"/api/agentic-assessments/{assessment.id}/review",
            headers=headers,
            json={
                "event_type": "approved",
                "operator": "operator",
                "reason_code": "evidence_reviewed",
            },
        )
        gpt_review = client.post(
            f"/api/agentic-assessments/{assessment.id}/gpt-review",
            headers=headers,
            json={
                "event_type": "gpt_review_requested",
                "operator": "operator",
                "reason_code": "second_opinion",
            },
        )

    assert preflight.status_code == 200
    assert preflight.json()["preflight"]["available"] is True
    assert started.status_code == 202
    assert started.json()["job"]["state"] == "queued"
    assert status.json()["assessments"][0]["id"] == assessment.id
    assert reviewed.json()["review_state"] == "approved"
    assert gpt_review.status_code == 202
    assert gpt_review.json()["review_state"] == "needs_review"
    assert gpt_review.json()["execution_status"] == "recorded_but_codex_review_disabled"
    repository.close()


def test_agentic_start_fails_closed_when_promotion_is_disabled(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(
        tmp_path / "insights.db",
        artifact_root=artifact_root,
    )
    app = create_app(
        repository=repository,
        artifact_root=artifact_root,
        api_key="test-secret",
        environment="test",
    )
    headers = {"X-API-Key": "test-secret"}
    with TestClient(app) as client:
        run_id = client.post(
            "/api/runs",
            headers=headers,
            json={"url": "example.com", "mode": "quick", "max_pages": 1},
        ).json()["run"]["id"]
        blocked = client.post(
            f"/api/runs/{run_id}/agentic-analysis",
            headers=headers,
            json={"vertical_pack_version": "one_trade_network.v1"},
        )
    assert blocked.status_code == 409
    repository.close()
