from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.repositories.sqlite_repository import SQLiteInsightRepository


@pytest.fixture()
def api_client(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    repo = SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root=artifact_root)
    app = create_app(
        repository=repo,
        artifact_root=artifact_root,
        api_key="test-secret",
        environment="test",
    )
    with TestClient(app) as client:
        yield client, repo
    repo.close()


def test_api_requires_key_and_exposes_database_health(api_client):
    client, _ = api_client

    unauthorized = client.get("/api/runs")
    health = client.get("/healthz")

    assert unauthorized.status_code == 401
    assert unauthorized.json()["detail"] == "invalid or missing API key"
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["database"]["backend"] == "sqlite"
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in health.headers["content-security-policy"]


def test_api_run_lifecycle_and_diff(api_client):
    client, _ = api_client
    headers = {"X-API-Key": "test-secret"}

    first = client.post(
        "/api/runs",
        headers=headers,
        json={"url": "example.com", "mode": "quick", "max_pages": 1},
    )
    second = client.post(
        "/api/runs",
        headers=headers,
        json={"url": "example.com", "mode": "quick", "max_pages": 1},
    )

    assert first.status_code == 201
    assert second.status_code == 201
    first_payload = first.json()
    second_payload = second.json()
    first_id = first_payload["run"]["id"]
    second_id = second_payload["run"]["id"]
    assert first_payload["validation"]["valid"] is True
    assert first_payload["run"]["config_snapshot"]["paid_api_approved"] is False

    listed = client.get("/api/runs?limit=10", headers=headers)
    detail = client.get(f"/api/runs/{first_id}", headers=headers)
    validation = client.get(f"/api/runs/{first_id}/validation", headers=headers)
    report = client.get(f"/api/runs/{first_id}/report", headers=headers)
    diff = client.get(
        f"/api/diff?base_run_id={first_id}&comparison_run_id={second_id}",
        headers=headers,
    )

    assert listed.status_code == 200
    assert len(listed.json()["runs"]) == 2
    assert detail.status_code == 200
    assert detail.json()["run"]["status"] == "completed"
    assert validation.json()["valid"] is True
    assert report.status_code == 200
    assert report.json()["report_status"] == "complete"
    assert diff.status_code == 200
    assert diff.json()["same_target"] is True
    assert diff.json()["score_delta"] == 0


def test_production_app_fails_closed_without_api_key(tmp_path: Path):
    repo = SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root=tmp_path / "artifacts")
    with pytest.raises(RuntimeError, match="SEO_INSIGHTS_API_KEY"):
        create_app(
            repository=repo,
            artifact_root=tmp_path / "artifacts",
            api_key=None,
            environment="production",
        )
    repo.close()
