from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.repositories.sqlite_repository import SQLiteInsightRepository


def test_product_strength_snapshot_bundle_and_owner_import_workflow(tmp_path: Path):
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
        created = client.post(
            "/api/runs",
            headers=headers,
            json={"url": "example.com", "mode": "quick", "max_pages": 1},
        )
        run_id = created.json()["run"]["id"]
        product = client.get(
            f"/api/runs/{run_id}/product-strength",
            headers=headers,
        )
        snapshot = client.post(
            f"/api/runs/{run_id}/product-strength/snapshot",
            headers=headers,
        )
        bundle = client.post(
            f"/api/runs/{run_id}/client-bundles",
            headers=headers,
            json={},
        )
        bundle_id = bundle.json()["client_report_bundle"]["id"]
        history = client.get(
            f"/api/runs/{run_id}/client-bundles",
            headers=headers,
        )
        downloaded = client.get(
            f"/api/client-bundles/{bundle_id}/download/html",
            headers=headers,
        )

        preview = client.post(
            "/api/owned-measurements/csv-preview",
            headers=headers,
            json={
                "csv_text": (
                    "period_start,period_end,sessions,signups\n"
                    "2026-07-01,2026-07-31,100,10\n"
                ),
                "prospect_id": "prospect-1",
                "vertical_id": "one_trade_network",
                "source": "ga4_csv",
                "context": {"market": "Tacoma, WA"},
            },
        )
        committed = client.post(
            "/api/owned-measurements/csv-commit",
            headers=headers,
            json={
                "csv_text": (
                    "period_start,period_end,sessions,signups\n"
                    "2026-07-01,2026-07-31,100,10\n"
                ),
                "prospect_id": "prospect-1",
                "vertical_id": "one_trade_network",
                "source": "ga4_csv",
                "context": {"market": "Tacoma, WA"},
            },
        )

    assert product.status_code == 200
    strength = product.json()["product_strength"]
    assert strength["contract_version"] == "product-strength.v1"
    assert set(strength["score_stack"]) == {
        "technical_seo_health",
        "ai_readiness",
        "conversion_readiness",
    }
    assert snapshot.status_code == 201
    assert snapshot.json()["report_snapshot"]["report_contract"] == "product-strength.v1"
    assert bundle.status_code == 201
    assert bundle.json()["validation"]["valid"] is True
    assert history.json()["client_report_bundles"][0]["id"] == bundle_id
    assert downloaded.status_code == 200
    assert downloaded.text.startswith("<!doctype html>")
    assert preview.json()["valid"] is True
    assert committed.status_code == 201
    assert committed.json()["baseline"]["observed_metrics"]["visit_to_signup"] == 0.1
    repository.close()
