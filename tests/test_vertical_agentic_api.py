from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.config import AgenticAnalysisSettings, AppConfig, DataForSEOSettings
from src.models import BusinessFactLedgerSnapshot, ProspectRecord, canonical_sha256
from src.repositories.sqlite_repository import SQLiteInsightRepository


HEADERS = {"X-API-Key": "test-secret"}
SHA = canonical_sha256({"api": "p12"})


def app_with_prospect(
    tmp_path: Path,
    *,
    promotion_approved: bool,
):
    artifact_root = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(
        tmp_path / "insights.db",
        artifact_root=artifact_root,
    )
    repository.save_prospect(
        ProspectRecord(
            id="prospect-1",
            business_name="Example Plumbing",
            website_url="https://example.com/",
            normalized_domain="example.com",
            category="plumber",
            location="Lacey, WA",
            contact_route="https://example.com/contact",
            source_provenance="operator_fixture",
            vertical_pack_version="one_trade_network.v1",
            vertical_id="one_trade_network",
            qualification_status="qualified",
        )
    )
    config = AppConfig(
        dataforseo=DataForSEOSettings(None, None),
        agentic=AgenticAnalysisSettings(
            enabled=True,
            operator_approved=True,
            promotion_approved=promotion_approved,
        ),
    )
    return (
        create_app(
            repository=repository,
            artifact_root=artifact_root,
            config=config,
            api_key="test-secret",
            environment="test",
        ),
        repository,
    )


def test_url_run_automatically_queues_five_promoted_work_items(tmp_path: Path) -> None:
    app, repository = app_with_prospect(tmp_path, promotion_approved=True)
    with TestClient(app) as client:
        created = client.post(
            "/api/runs",
            headers=HEADERS,
            json={"url": "example.com", "mode": "quick", "max_pages": 1},
        )
        run_id = created.json()["run"]["id"]
        automatic = created.json()["agentic_evidence"]
        pack = client.get(
            "/api/vertical-agentic-packs/one_trade_network.agentic.v1",
            headers=HEADERS,
        )
        status = client.get(
            f"/api/runs/{run_id}/agentic-evidence",
            headers=HEADERS,
        )
        first_id = status.json()["work_items"][0]["id"]
        work = client.get(
            f"/api/agentic-work-items/{first_id}",
            headers=HEADERS,
        )

    assert created.status_code == 201
    assert automatic["preflight"]["available"] is True
    assert automatic["preflight"]["max_inference_cost_usd"] == 0.25
    assert len(automatic["work_items"]) == 5
    assert sum(item["max_cost_usd"] for item in automatic["work_items"]) == 0.25
    assert {
        item["vertical_pack_version"] for item in automatic["work_items"]
    } == {"one_trade_network.agentic.v1"}
    assert pack.status_code == 200
    assert len(pack.json()["vertical_agentic_pack"]["journey_tasks"]) == 3
    assert status.status_code == 200
    assert status.json()["owner_diagnostics"] == []
    assert status.json()["playwright_health"]["status"] in {
        "ok",
        "degraded",
        "unavailable",
    }
    assert work.json()["work_item"]["id"] == first_id
    assert work.json()["tool_steps"] == []
    repository.close()


def test_shadow_mode_is_explicit_review_only_before_promotion(tmp_path: Path) -> None:
    app, repository = app_with_prospect(tmp_path, promotion_approved=False)
    with TestClient(app) as client:
        created = client.post(
            "/api/runs",
            headers=HEADERS,
            json={"url": "example.com", "mode": "quick", "max_pages": 1},
        )
        run_id = created.json()["run"]["id"]
        automatic = created.json()["agentic_evidence"]["preflight"]
        preview = client.post(
            f"/api/runs/{run_id}/agentic-evidence/preflight",
            headers=HEADERS,
            json={"execution_mode": "shadow"},
        )
        queued = client.post(
            f"/api/runs/{run_id}/agentic-evidence",
            headers=HEADERS,
            json={"execution_mode": "shadow"},
        )

    assert automatic["available"] is False
    assert "P10 promotion" in automatic["unavailable_reason"]
    assert preview.status_code == 200
    assert preview.json()["preflight"]["available"] is True
    assert preview.json()["preflight"]["customer_export_eligible"] is False
    assert queued.status_code == 202
    assert {item["execution_mode"] for item in queued.json()["work_items"]} == {
        "shadow"
    }
    repository.close()


def test_snapshot_review_and_partial_decision_report_are_api_visible(tmp_path: Path) -> None:
    app, repository = app_with_prospect(tmp_path, promotion_approved=True)
    with TestClient(app) as client:
        created = client.post(
            "/api/runs",
            headers=HEADERS,
            json={"url": "example.com", "mode": "quick", "max_pages": 1},
        )
        run = created.json()["run"]
        fact_work = next(
            item
            for item in created.json()["agentic_evidence"]["work_items"]
            if item["work_kind"] == "business_fact_ledger"
        )
        ledger = repository.save_business_fact_ledger_snapshot(
            BusinessFactLedgerSnapshot(
                run_id=run["id"],
                attempt_id=run["attempt_id"],
                work_item_id=fact_work["id"],
                vertical_pack_version="one_trade_network.agentic.v1",
                source_sha256=SHA,
                facts=[
                    {
                        "fact_id": "service_area",
                        "name": "service area",
                        "normalized_value": None,
                        "source_status": "unknown",
                        "sensitivity_class": "public",
                        "approval_state": "needs_review",
                        "evidence_refs": [],
                    }
                ],
            )
        )
        reviewed = client.post(
            f"/api/agentic-evidence/{ledger.id}/review",
            headers=HEADERS,
            json={
                "snapshot_type": "business_fact_ledger",
                "event_type": "approved",
                "operator": "operator",
                "reason_code": "fixture_review",
            },
        )
        reports = client.post(
            f"/api/runs/{run['id']}/agentic-evidence/reports",
            headers=HEADERS,
        )
        read = client.get(
            f"/api/runs/{run['id']}/report?version=decision-intelligence-v1",
            headers=HEADERS,
        )

    assert reviewed.status_code == 201
    assert reviewed.json()["review_state"] == "approved"
    assert reports.status_code == 201
    assert reports.json()["reports"]["decision-intelligence-v1"]["report_payload"][
        "status"
    ] == "partial"
    assert read.status_code == 200
    assert read.json()["report_version"] == "decision-intelligence-v1"
    assert "score" not in read.json()["report_payload"]
    repository.close()
