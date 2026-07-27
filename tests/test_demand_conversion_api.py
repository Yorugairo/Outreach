from __future__ import annotations

from fastapi.testclient import TestClient

from tests.test_demand_conversion_model import _assumptions
from tests.test_opportunity_api import HEADERS, _case_fixture


TRENDS_CSV = """Category: All categories
Country: United States

Week,bjj tacoma,isPartial
2026-01-04,50,FALSE
2026-02-01,70,FALSE
2026-03-01,90,FALSE
"""

CRM_CSV = """period_start,period_end,funnel_stage,leads,bookings,customers,revenue,market
2026-04-01,2026-06-30,won,20,10,5,3000,"Tacoma, WA"
"""


def _approved_inputs(client, prospect, keyword_set, csv_text):
    demand_payload = {
        "csv_text": csv_text,
        "prospect_id": prospect.id,
        "keyword_set_id": keyword_set.id,
        "vertical_id": prospect.vertical_id,
        "market": "Tacoma, WA",
        "location_code": 1027773,
        "snapshot_period": "2026-07",
        "brand_terms": ["Nova Ryu"],
    }
    draft = client.post(
        "/api/demand-evidence/csv-commit",
        headers=HEADERS,
        json=demand_payload,
    ).json()["demand_evidence"]
    demand = client.post(
        f"/api/demand-evidence/{draft['id']}/approve",
        headers=HEADERS,
        json={"operator": "operator"},
    ).json()["demand_evidence"]
    economics = client.post(
        f"/api/prospects/{prospect.id}/economics",
        headers=HEADERS,
        json={
            "vertical_id": prospect.vertical_id,
            "revenue_model": "membership",
            "monthly_price": 100,
            "currency": "USD",
            "capacity_headroom": 20,
            "desired_fill_months": 12,
            "field_provenance": {
                "monthly_price": "business_supplied",
                "capacity_headroom": "business_supplied",
                "desired_fill_months": "business_supplied",
            },
            "approve": True,
            "operator": "operator",
        },
    ).json()["economics_profile"]
    return demand, economics


def test_prospect_mode_build_approval_and_v5_report(tmp_path):
    repository, app, run, prospect, keyword_set, csv_text = _case_fixture(
        tmp_path,
        vertical_id="national_bjj_registry",
        business_name="Nova Ryu",
    )
    with TestClient(app) as client:
        demand, economics = _approved_inputs(
            client,
            prospect,
            keyword_set,
            csv_text,
        )
        url_first = client.post(
            f"/api/prospects/{prospect.id}/runs",
            headers=HEADERS,
            json={"mode": "quick", "max_pages": 1},
        )
        readiness = client.get(
            f"/api/prospects/{prospect.id}/evidence-readiness",
            headers=HEADERS,
        )
        built = client.post(
            f"/api/runs/{run.id}/demand-conversion",
            headers=HEADERS,
            json={
                "prospect_id": prospect.id,
                "mode": "prospect",
                "market": "Tacoma, WA",
                "demand_evidence_set_id": demand["id"],
                "economics_profile_id": economics["id"],
                "assumptions": _assumptions(include_rates=True),
            },
        )
        approved = client.post(
            f"/api/demand-conversion/{built.json()['demand_conversion']['id']}/approve",
            headers=HEADERS,
            json={"operator": "operator"},
        )
        loaded = client.get(
            f"/api/runs/{run.id}/demand-conversion?mode=prospect",
            headers=HEADERS,
        )
        v5 = client.get(
            f"/api/runs/{run.id}/report?version=v5",
            headers=HEADERS,
        )

    assert readiness.status_code == 200
    assert url_first.status_code == 201
    assert url_first.json()["demand_conversion"]["mode"] == "prospect"
    assert url_first.json()["demand_conversion"]["modeled_outputs"] == {}
    assert readiness.json()["prospect_mode"]["approved_demand"] is True
    assert built.status_code == 201
    assert built.json()["demand_conversion"]["mode"] == "prospect"
    assert approved.status_code == 201
    assert set(approved.json()["reports"]) == {"demand-conversion-v1", "v5"}
    assert approved.json()["validation"]["valid"] is True
    assert loaded.json()["demand_conversion"]["state"] == "approved"
    assert v5.status_code == 200
    assert v5.json()["report_payload"]["mode"] == "prospect"
    assert "search occasions, not unique people" in v5.text.casefold()
    repository.close()


def test_trend_and_owner_verified_aggregate_flow(tmp_path):
    repository, app, run, prospect, keyword_set, csv_text = _case_fixture(
        tmp_path,
        vertical_id="national_bjj_registry",
        business_name="Nova Ryu",
    )
    with TestClient(app) as client:
        demand, economics = _approved_inputs(
            client,
            prospect,
            keyword_set,
            csv_text,
        )
        prospect_built = client.post(
            f"/api/runs/{run.id}/demand-conversion",
            headers=HEADERS,
            json={
                "prospect_id": prospect.id,
                "mode": "prospect",
                "market": "Tacoma, WA",
                "demand_evidence_set_id": demand["id"],
                "economics_profile_id": economics["id"],
                "assumptions": _assumptions(include_rates=True),
            },
        ).json()["demand_conversion"]
        prospect_approved = client.post(
            f"/api/demand-conversion/{prospect_built['id']}/approve",
            headers=HEADERS,
            json={"operator": "operator"},
        )
        assert prospect_approved.status_code == 201
        trend_payload = {
            "csv_text": TRENDS_CSV,
            "prospect_id": prospect.id,
            "vertical_id": prospect.vertical_id,
            "market": "Tacoma, WA",
            "source": "google_trends_csv",
            "period_start": "2026-01-01",
            "period_end": "2026-03-31",
            "location_code": 1027773,
            "keyword_set_id": keyword_set.id,
        }
        trend_preview = client.post(
            "/api/demand-trends/csv-preview",
            headers=HEADERS,
            json=trend_payload,
        )
        trend_draft = client.post(
            "/api/demand-trends/csv-commit",
            headers=HEADERS,
            json=trend_payload,
        ).json()["demand_trend"]
        trend = client.post(
            f"/api/demand-trends/{trend_draft['id']}/approve",
            headers=HEADERS,
            json={"operator": "operator"},
        ).json()["demand_trend"]
        owner_payload = {
            "csv_text": CRM_CSV,
            "prospect_id": prospect.id,
            "vertical_id": prospect.vertical_id,
            "source": "crm_csv",
            "context": {"market": "Tacoma, WA"},
            "owner_verified": True,
            "owner_consent": {
                "confirmed": True,
                "operator": "owner",
                "confirmed_at": "2026-07-26T12:00:00Z",
            },
            "data_freshness": {
                "status": "fresh",
                "snapshot_date": "2026-06-30",
            },
        }
        owner_preview = client.post(
            "/api/owned-measurements/csv-preview",
            headers=HEADERS,
            json=owner_payload,
        )
        owner = client.post(
            "/api/owned-measurements/csv-commit",
            headers=HEADERS,
            json=owner_payload,
        ).json()["owned_measurements"]
        event_map = client.post(
            "/api/conversion-event-maps",
            headers=HEADERS,
            json={
                "prospect_id": prospect.id,
                "vertical_id": prospect.vertical_id,
                "mappings": {
                    "lead": ["lead"],
                    "booking": ["booking"],
                    "customer": ["won"],
                },
                "source_snapshot_ids": [item["id"] for item in owner],
                "approve": True,
                "operator": "operator",
            },
        ).json()["conversion_event_map"]
        built = client.post(
            f"/api/runs/{run.id}/demand-conversion",
            headers=HEADERS,
            json={
                "prospect_id": prospect.id,
                "mode": "owner_verified",
                "market": "Tacoma, WA",
                "demand_evidence_set_id": demand["id"],
                "economics_profile_id": economics["id"],
                "owner_snapshot_ids": [item["id"] for item in owner],
                "trend_snapshot_ids": [trend["id"]],
                "event_map_id": event_map["id"],
                "assumptions": _assumptions(include_rates=True),
            },
        )
        approved = client.post(
            f"/api/demand-conversion/{built.json()['demand_conversion']['id']}/approve",
            headers=HEADERS,
            json={"operator": "operator"},
        )
        prospect_view = client.get(
            f"/api/runs/{run.id}/demand-conversion?mode=prospect",
            headers=HEADERS,
        )
        owner_view = client.get(
            f"/api/runs/{run.id}/demand-conversion?mode=owner_verified",
            headers=HEADERS,
        )
        owner_v5 = client.get(
            f"/api/runs/{run.id}/report?version=v5&mode=owner_verified",
            headers=HEADERS,
        )

    assert trend_preview.status_code == 200
    assert trend_preview.json()["valid"] is True
    assert owner_preview.status_code == 200
    assert owner_preview.json()["valid"] is True
    assert built.status_code == 201
    assert built.json()["demand_conversion"]["mode"] == "owner_verified"
    assert approved.status_code == 201
    assert prospect_view.json()["demand_conversion"]["mode"] == "prospect"
    assert prospect_view.json()["report"]["report_payload"]["mode"] == "prospect"
    assert owner_view.json()["demand_conversion"]["mode"] == "owner_verified"
    assert owner_view.json()["report"]["report_payload"]["mode"] == (
        "owner_verified"
    )
    assert owner_v5.json()["report_payload"]["mode"] == "owner_verified"
    assert approved.json()["reports"]["demand-conversion-v1"]["report_payload"][
        "validation"
    ]["privacy"] == "owner_aggregate"
    assert "owner@example.com" not in approved.text
    repository.close()
