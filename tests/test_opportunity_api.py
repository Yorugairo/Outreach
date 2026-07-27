from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.models import (
    KeywordSet,
    KeywordTarget,
    MarketEvidenceRun,
    ProspectRecord,
    utc_now_iso,
)
from src.orchestrator import InsightRunOrchestrator
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.keyword_set_service import KeywordSetService
from tests.test_opportunity_model import _assumptions


HEADERS = {"X-API-Key": "opportunity-secret"}


def _case_fixture(
    tmp_path: Path,
    *,
    vertical_id: str,
    business_name: str,
):
    artifact_root = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(
        tmp_path / "seo-insights.db",
        artifact_root=artifact_root,
    )
    run = InsightRunOrchestrator(
        repository,
        artifact_root=artifact_root,
    ).start("example.com", mode="quick", max_pages=1)
    bjj = vertical_id == "national_bjj_registry"
    prospect = repository.save_prospect(
        ProspectRecord(
            business_name=business_name,
            website_url="https://example.com",
            normalized_domain="example.com",
            category="bjj academy" if bjj else "window and door",
            location="Tacoma, WA",
            contact_route="owner@example.com",
            source_provenance="pilot_fixture",
            vertical_id=vertical_id,
            vertical_pack_version=(
                "national_bjj_registry.v1"
                if bjj
                else "one_trade_network.v1"
            ),
            qualification_status="qualified",
        )
    )
    terms = (
        [
            ("bjj tacoma", "Primary Local Core", False),
            ("nova ryu tacoma", "Lineage, Authority & Brand", True),
        ]
        if bjj
        else [
            ("glass repair tacoma", "Primary Local Core", False),
            ("lacey glass tacoma", "Brand", True),
        ]
    )
    targets = [
        KeywordTarget(
            keyword=keyword,
            category=category,
            search_intent="Commercial / Transactional",
            optimization_focus="SEO",
            target_page_usage="Homepage / Main Landing",
            review_status="approved",
        )
        for keyword, category, _ in terms
    ]
    keyword_set = repository.save_keyword_set(
        KeywordSet(
            vertical_id=vertical_id,
            market="Tacoma, WA",
            market_slug="tacoma-pilot",
            location_code=1027773,
            version="v1",
            source_sha256="a" * 64,
            keyword_targets=[target.to_dict() for target in targets],
            state="approved",
            normalized_domain="example.com",
            scope_type="prospect",
            scope_id=prospect.id,
            approved_by="operator",
            approved_at=utc_now_iso(),
        )
    )
    KeywordSetService(repository).bind(
        keyword_set,
        normalized_domain=prospect.normalized_domain,
        prospect_id=prospect.id,
        operator="operator",
    )
    csv_text = (
        "Keyword,Avg. monthly searches,Category,Search Intent,"
        "Target Page Usage,Brand\n"
        f"{terms[0][0]},1000,{terms[0][1]},Commercial / Transactional,"
        "Homepage / Main Landing,false\n"
        f"{terms[1][0]},500,{terms[1][1]},Brand,"
        "Homepage / Main Landing,true\n"
    )
    app = create_app(
        repository=repository,
        artifact_root=artifact_root,
        api_key="opportunity-secret",
        environment="test",
    )
    return repository, app, run, prospect, keyword_set, csv_text


@pytest.mark.parametrize(
    ("vertical_id", "business_name", "price", "capacity", "revenue_model"),
    [
        ("national_bjj_registry", "Nova Ryu", 100, 20, "membership"),
        ("one_trade_network", "Lacey Glass", 750, 5, "won_job"),
    ],
)
def test_demand_to_v4_pitch_workflow_for_bjj_and_trades(
    tmp_path,
    vertical_id,
    business_name,
    price,
    capacity,
    revenue_model,
):
    repository, app, run, prospect, keyword_set, csv_text = _case_fixture(
        tmp_path,
        vertical_id=vertical_id,
        business_name=business_name,
    )
    demand_payload = {
        "csv_text": csv_text,
        "prospect_id": prospect.id,
        "keyword_set_id": keyword_set.id,
        "vertical_id": vertical_id,
        "market": "Tacoma, WA",
        "location_code": 1027773,
        "snapshot_period": "2026-07",
        "brand_terms": [business_name],
    }
    with TestClient(app) as client:
        preview = client.post(
            "/api/demand-evidence/csv-preview",
            headers=HEADERS,
            json=demand_payload,
        )
        committed = client.post(
            "/api/demand-evidence/csv-commit",
            headers=HEADERS,
            json=demand_payload,
        )
        draft = committed.json()["demand_evidence"]
        approved_demand_response = client.post(
            f"/api/demand-evidence/{draft['id']}/approve",
            headers=HEADERS,
            json={"operator": "operator"},
        )
        approved_demand = approved_demand_response.json()["demand_evidence"]

        economics_response = client.post(
            f"/api/prospects/{prospect.id}/economics",
            headers=HEADERS,
            json={
                "vertical_id": vertical_id,
                "revenue_model": revenue_model,
                "monthly_price": price,
                "currency": "USD",
                "capacity_headroom": capacity,
                "desired_fill_months": 12,
                "field_provenance": {
                    "monthly_price": "business_supplied",
                    "capacity_headroom": "business_supplied",
                    "desired_fill_months": "business_supplied",
                },
                "approve": True,
                "operator": "operator",
            },
        )
        economics = economics_response.json()["economics_profile"]

        scenario_response = client.post(
            f"/api/runs/{run.id}/opportunity-scenarios",
            headers=HEADERS,
            json={
                "prospect_id": prospect.id,
                "demand_evidence_set_id": approved_demand["id"],
                "economics_profile_id": economics["id"],
                "assumptions": _assumptions(),
            },
        )
        scenario = scenario_response.json()["opportunity_scenario"]
        approved_scenario_response = client.post(
            f"/api/opportunity-scenarios/{scenario['id']}/approve",
            headers=HEADERS,
            json={"operator": "operator"},
        )
        approved_scenario = approved_scenario_response.json()[
            "opportunity_scenario"
        ]
        opportunity = client.get(
            f"/api/runs/{run.id}/opportunity",
            headers=HEADERS,
        )
        v4 = client.get(
            f"/api/runs/{run.id}/report?version=v4",
            headers=HEADERS,
        )
        pitch = client.post(
            f"/api/runs/{run.id}/pitch-pack",
            headers=HEADERS,
            json={"prospect_id": prospect.id},
        )
        pitch_payload = pitch.json()["outreach_package"]
        blocked_export = client.get(
            f"/api/outreach-packages/{pitch_payload['id']}/export",
            headers=HEADERS,
        )
        pitch_approval = client.post(
            f"/api/outreach-packages/{pitch_payload['id']}/approve",
            headers=HEADERS,
            json={
                "operator": "operator",
                "acknowledge_partial_ai": True,
            },
        )
        exported = client.get(
            f"/api/outreach-packages/{pitch_payload['id']}/export",
            headers=HEADERS,
        )

        calibration_payload = {
            "csv_text": (
                "period_start,period_end,source,clicks,total_users,"
                "signups_or_leads,attended_or_appointments,new_customers,spend\n"
                "2026-06-01,2026-06-30,aggregate_analytics,100,80,10,8,4,200\n"
            ),
            "prospect_id": prospect.id,
            "vertical_id": vertical_id,
            "market": "Tacoma, WA",
        }
        calibration_preview = client.post(
            "/api/calibration/csv-preview",
            headers=HEADERS,
            json=calibration_payload,
        )
        calibration_commit = client.post(
            "/api/calibration/csv-commit",
            headers=HEADERS,
            json=calibration_payload,
        )

    assert preview.status_code == 200
    assert preview.json()["valid"] is True
    assert committed.status_code == 201
    assert approved_demand_response.status_code == 200
    assert approved_demand["state"] == "approved"
    assert approved_demand["version"] == 3
    assert economics_response.status_code == 201
    assert economics["state"] == "approved"
    assert economics_response.json()["capacity_ceiling"]["mrr"] == price * capacity
    assert scenario_response.status_code == 201
    assert scenario["status"] == "complete"
    assert approved_scenario_response.status_code == 200
    assert approved_scenario["state"] == "approved"
    assert max(
        band["capacity_adjusted_active_customers"]
        for band in approved_scenario["outputs"].values()
    ) <= capacity
    assert opportunity.status_code == 200
    assert v4.status_code == 200
    assert v4.json()["report_payload"]["report_contract"] == "v4"
    assert (
        v4.json()["report_payload"]["demand_groups"]["semantics"]
        == "Monthly search occasions, not unique people"
    )
    assert pitch.status_code == 201
    assert blocked_export.status_code == 422
    assert pitch_approval.status_code == 200
    assert exported.status_code == 200
    assert (
        exported.json()["json"]["opportunity_scenario_id"]
        == approved_scenario["id"]
    )
    assert "$" not in exported.json()["plaintext"]
    assert calibration_preview.status_code == 200
    assert calibration_preview.json()["valid"] is True
    assert calibration_commit.status_code == 201
    assert len(calibration_commit.json()["calibration_records"]) == 1
    repository.close()


def test_market_resume_api_keeps_paid_provider_action_explicit(tmp_path):
    repository, app, run, _, keyword_set, _ = _case_fixture(
        tmp_path,
        vertical_id="national_bjj_registry",
        business_name="Nova Ryu",
    )
    market_run = repository.save_market_evidence_run(
        MarketEvidenceRun(
            insight_run_id=run.id,
            insight_attempt_id=run.attempt_id,
            keyword_set_id=keyword_set.id,
            keyword_set_version=keyword_set.keyword_set_key,
            target_domain="example.com",
            target_entity_name="Nova Ryu",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            location_code=1027773,
            state="partial",
        )
    )
    with TestClient(app) as client:
        response = client.post(
            f"/api/market-evidence/{market_run.id}/resume",
            headers=HEADERS,
            json={
                "approve_paid_enrichment": False,
                "account_recovered": False,
            },
        )

    assert response.status_code == 409
    assert "explicit paid-enrichment approval" in response.json()["detail"]
    repository.close()
