from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import RunCreateRequest, create_app, resolve_paid_enrichment_approval
from src.config import AppConfig, ApprovalPolicy, DataForSEOSettings
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
    assert health.json()["search_enrichment"]["configured"] is False
    assert health.json()["search_enrichment"]["default_approved"] is False
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in health.headers["content-security-policy"]


def test_paid_enrichment_request_omission_uses_operator_default():
    assert RunCreateRequest(url="example.com").approve_paid_enrichment is None
    assert resolve_paid_enrichment_approval(True, None) is True
    assert resolve_paid_enrichment_approval(False, None) is False
    assert resolve_paid_enrichment_approval(True, False) is False
    assert resolve_paid_enrichment_approval(False, True) is True


def test_health_exposes_safe_runtime_search_policy(tmp_path: Path):
    repo = SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root=tmp_path / "artifacts")
    config = AppConfig(
        dataforseo=DataForSEOSettings("configured-login", "configured-password", max_paid_calls=6),
        approval=ApprovalPolicy(allow_paid_api_calls=True),
    )
    app = create_app(
        repository=repo,
        artifact_root=tmp_path / "artifacts",
        config=config,
        api_key="test-secret",
        environment="development",
    )
    with TestClient(app) as client:
        health = client.get("/healthz").json()
    assert health["search_enrichment"] == {
        "configured": True,
        "default_approved": True,
        "max_paid_calls": 6,
    }
    assert "configured-login" not in str(health)
    assert "configured-password" not in str(health)
    repo.close()


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
    report_v2 = client.get(f"/api/runs/{first_id}/report?version=v2", headers=headers)
    ai_report = client.get(f"/api/runs/{first_id}/ai-readiness", headers=headers)
    search_visibility = client.get(f"/api/runs/{first_id}/search-visibility", headers=headers)
    offsite_authority = client.get(f"/api/runs/{first_id}/offsite-authority", headers=headers)
    diff = client.get(
        f"/api/diff?base_run_id={first_id}&comparison_run_id={second_id}",
        headers=headers,
    )

    assert listed.status_code == 200
    assert len(listed.json()["runs"]) == 2
    assert detail.status_code == 200
    assert ai_report.status_code == 200
    assert search_visibility.status_code == 200
    assert search_visibility.json()["status"] == "not_configured"
    assert offsite_authority.status_code == 200
    assert offsite_authority.json()["status"] == "unknown"
    assert offsite_authority.json()["link_rank"] is None
    assert offsite_authority.json()["metric_label"] == "DataForSEO Link Rank"
    assert ai_report.json()["score_version"] == "ai-readiness.v3"
    assert set(ai_report.json()["dimensions"]) == {"aeo", "geo", "aio"}
    assert detail.json()["run"]["status"] == "completed"
    assert validation.json()["valid"] is True
    assert report.status_code == 200
    assert report.json()["report_status"] == "complete"
    assert report.json()["report_version"] == "v1"
    assert report_v2.status_code == 200
    assert report_v2.json()["report_version"] == "v2"
    assert diff.status_code == 200
    assert diff.json()["same_target"] is True
    assert diff.json()["score_delta"] == 0


def test_api_revenue_workflow_import_package_export_and_funnel(api_client):
    client, _ = api_client
    headers = {"X-API-Key": "test-secret"}
    csv_text = (
        "business_name,website_url,category,location,contact_route,source\n"
        "Example Plumbing,example.com,plumber,Austin TX,owner@example.com,fixture\n"
    )

    packs = client.get("/api/vertical-packs", headers=headers)
    preview = client.post(
        "/api/prospects/csv-preview",
        headers=headers,
        json={"csv_text": csv_text, "vertical_pack_version": "one_trade_network.v1"},
    )
    commit = client.post(
        "/api/prospects/csv-commit",
        headers=headers,
        json={"csv_text": csv_text, "vertical_pack_version": "one_trade_network.v1"},
    )
    prospect_id = commit.json()["prospects"][0]["id"]
    run_response = client.post(
        "/api/prospects/{}/runs".format(prospect_id),
        headers=headers,
        json={"mode": "quick", "max_pages": 1},
    )
    run_id = run_response.json()["run"]["id"]
    package_response = client.post(
        f"/api/runs/{run_id}/outreach-packages",
        headers=headers,
        json={"prospect_id": prospect_id},
    )
    package = package_response.json()["outreach_package"]
    blocked_export = client.get(f"/api/outreach-packages/{package['id']}/export", headers=headers)
    approved = client.post(
        f"/api/outreach-packages/{package['id']}/approve",
        headers=headers,
        json={"operator": "operator", "acknowledge_partial_ai": True},
    )
    exported = client.get(f"/api/outreach-packages/{package['id']}/export", headers=headers)
    event = client.post(
        "/api/activation-events",
        headers=headers,
        json={
            "insight_run_id": run_id,
            "outreach_package_id": package["id"],
            "package_version": package["package_version"],
            "stage": "package_approved",
            "vertical_id": "one_trade_network",
            "operator": "operator",
            "service_packages": package["recommended_service_package"],
        },
    )
    funnel = client.get("/api/funnel", headers=headers)

    assert packs.status_code == 200
    assert {pack["pack_id"] for pack in packs.json()["vertical_packs"]} >= {"one_trade_network.v1"}
    assert preview.status_code == 200
    assert preview.json()["valid_prospects"][0]["normalized_domain"] == "example.com"
    assert commit.status_code == 201
    assert run_response.status_code == 201
    assert package_response.status_code == 201
    assert package["state"] == "needs_review"
    assert blocked_export.status_code == 422
    assert approved.status_code == 200
    assert approved.json()["outreach_package"]["ai_evidence_acknowledged"] is True
    assert approved.json()["outreach_package"]["state"] == "approved"
    assert exported.status_code == 200
    assert exported.json()["json"]["id"] == package["id"]
    assert event.status_code == 201
    assert funnel.json()["verticals"]["one_trade_network"]["stage_counts"]["package_approved"] == 1


def test_api_v1_only_run_defaults_to_v1_and_returns_clear_v2_404(api_client):
    client, repo = api_client
    headers = {"X-API-Key": "test-secret"}
    created = client.post(
        "/api/runs",
        headers=headers,
        json={"url": "example.com", "mode": "quick", "max_pages": 1},
    )
    run_id = created.json()["run"]["id"]
    with sqlite3.connect(repo.database_path) as connection:
        connection.execute(
            "DELETE FROM insight_reports WHERE insight_run_id = ? AND report_version = 'v2'",
            (run_id,),
        )
    report_dir = repo.artifact_root / "runs" / run_id / "reports"
    (report_dir / "v2.json").unlink()
    (report_dir / "v2.md").unlink()

    default = client.get(f"/api/runs/{run_id}/report", headers=headers)
    missing_v2 = client.get(f"/api/runs/{run_id}/report?version=v2", headers=headers)
    invalid = client.get(f"/api/runs/{run_id}/report?version=v3", headers=headers)

    assert default.status_code == 200
    assert default.json()["report_version"] == "v1"
    assert missing_v2.status_code == 404
    assert missing_v2.json()["detail"] == "report v2 not found"
    assert invalid.status_code == 404
    assert invalid.json()["detail"] == "report v3 not found"


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
