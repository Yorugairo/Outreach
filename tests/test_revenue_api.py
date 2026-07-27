from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.repositories.sqlite_repository import SQLiteInsightRepository


@pytest.fixture()
def revenue_client(tmp_path: Path):
    root = tmp_path / "artifacts"
    repo = SQLiteInsightRepository(tmp_path / "insights.db", artifact_root=root)
    app = create_app(repository=repo, artifact_root=root, api_key="revenue-secret", environment="test")
    with TestClient(app) as client:
        yield client, repo
    repo.close()


HEADERS = {"X-API-Key": "revenue-secret"}
CSV = (
    "business_name,website_url,category,location,contact_route,source\n"
    "Example Plumbing,example.com,plumber,Austin TX,owner@example.com,fixture\n"
)


def test_app_seeds_packs_and_qualification_lifecycle(revenue_client):
    client, repo = revenue_client

    assert {pack.pack_id for pack in repo.list_vertical_packs()} >= {
        "one_trade_network.v1",
        "national_bjj_registry.v1",
    }
    preview = client.post(
        "/api/prospects/csv-preview",
        headers=HEADERS,
        json={"csv_text": CSV, "vertical_pack_version": "one_trade_network.v1"},
    )
    committed = client.post(
        "/api/prospects/csv-commit",
        headers=HEADERS,
        json={"csv_text": CSV, "vertical_pack_version": "one_trade_network.v1"},
    )
    prospect_id = committed.json()["prospects"][0]["id"]

    assert preview.status_code == 200
    assert committed.status_code == 201
    assert client.get(f"/api/prospects/{prospect_id}", headers=HEADERS).status_code == 200
    updated = client.patch(
        f"/api/prospects/{prospect_id}/qualification",
        headers=HEADERS,
        json={"qualification_status": "rejected", "rejection_reasons": ["operator review"]},
    )
    assert updated.status_code == 200
    assert updated.json()["prospect"]["qualification_status"] == "rejected"
    blocked = client.post(
        f"/api/prospects/{prospect_id}/runs",
        headers=HEADERS,
        json={"mode": "quick", "max_pages": 1},
    )
    assert blocked.status_code == 409


def test_csv_commit_is_deduplicated_by_vertical_and_domain(revenue_client):
    client, _ = revenue_client
    payload = {"csv_text": CSV, "vertical_pack_version": "one_trade_network.v1"}
    first = client.post("/api/prospects/csv-commit", headers=HEADERS, json=payload)
    second = client.post("/api/prospects/csv-commit", headers=HEADERS, json=payload)

    assert first.status_code == 201 and first.json()["saved_count"] == 1
    assert second.status_code == 201 and second.json()["saved_count"] == 0
    assert any("already exists" in issue["message"] for issue in second.json()["issues"])


def test_borderline_prospect_is_queued_for_operator_qualification(revenue_client):
    client, _ = revenue_client
    borderline_csv = (
        "business_name,website_url,category,location,contact_route,source\n"
        "Example Services,example-services.com,accountant,Austin TX,owner@example.com,fixture\n"
    )
    committed = client.post(
        "/api/prospects/csv-commit",
        headers=HEADERS,
        json={
            "csv_text": borderline_csv,
            "vertical_pack_version": "one_trade_network.v1",
        },
    )

    assert committed.status_code == 201
    assert committed.json()["saved_count"] == 1
    prospect = committed.json()["prospects"][0]
    assert prospect["qualification_status"] == "needs_review"

    qualified = client.patch(
        f"/api/prospects/{prospect['id']}/qualification",
        headers=HEADERS,
        json={
            "qualification_status": "qualified",
            "rejection_reasons": [],
            "operator": "reviewer@example.com",
        },
    )

    assert qualified.status_code == 200
    assert qualified.json()["prospect"]["qualification_status"] == "qualified"
    assert (
        qualified.json()["prospect"]["metadata"]["qualification_operator"]
        == "reviewer@example.com"
    )


def test_package_lookup_and_activation_reject_vertical_mismatch(revenue_client):
    client, _ = revenue_client
    committed = client.post(
        "/api/prospects/csv-commit",
        headers=HEADERS,
        json={"csv_text": CSV, "vertical_pack_version": "one_trade_network.v1"},
    )
    prospect_id = committed.json()["prospects"][0]["id"]
    run = client.post(
        f"/api/prospects/{prospect_id}/runs",
        headers=HEADERS,
        json={"mode": "quick", "max_pages": 1},
    ).json()["run"]
    package = client.post(
        f"/api/runs/{run['id']}/outreach-packages",
        headers=HEADERS,
        json={"prospect_id": prospect_id},
    ).json()["outreach_package"]
    lookup = client.get(f"/api/outreach-packages/{package['id']}", headers=HEADERS)
    mismatch = client.post(
        "/api/activation-events",
        headers=HEADERS,
        json={
            "insight_run_id": run["id"],
            "outreach_package_id": package["id"],
            "package_version": package["package_version"],
            "stage": "package_approved",
            "vertical_id": "national_bjj_registry",
            "operator": "operator",
        },
    )

    assert lookup.status_code == 200
    assert lookup.json()["outreach_package"]["id"] == package["id"]
    assert mismatch.status_code == 422
    assert "vertical" in mismatch.json()["detail"]


def test_approved_package_export_and_activation_funnel_lifecycle(revenue_client):
    client, repo = revenue_client
    prospect = client.post(
        "/api/prospects/csv-commit",
        headers=HEADERS,
        json={"csv_text": CSV, "vertical_pack_version": "one_trade_network.v1"},
    ).json()["prospects"][0]
    run = client.post(
        f"/api/prospects/{prospect['id']}/runs",
        headers=HEADERS,
        json={"mode": "quick", "max_pages": 1},
    ).json()["run"]
    package = client.post(
        f"/api/runs/{run['id']}/outreach-packages",
        headers=HEADERS,
        json={"prospect_id": prospect["id"]},
    ).json()["outreach_package"]
    outreach_dir = repo.artifact_root / "runs" / run["id"] / "outreach"

    assert not (outreach_dir / f"{package['id']}.txt").exists()
    blocked_export = client.get(
        f"/api/outreach-packages/{package['id']}/export",
        headers=HEADERS,
    )
    assert blocked_export.status_code == 422

    approved = client.post(
        f"/api/outreach-packages/{package['id']}/approve",
        headers=HEADERS,
        json={
            "operator": "reviewer@example.com",
            "acknowledge_partial_ai": True,
        },
    )
    approved_package = approved.json()["outreach_package"]

    assert approved.status_code == 200
    assert approved_package["approved_by"] == "reviewer@example.com"
    assert approved_package["approved_at"]
    assert (outreach_dir / f"{package['id']}.txt").exists()
    assert (outreach_dir / f"{package['id']}.md").exists()
    assert client.get(
        f"/api/outreach-packages/{package['id']}/export",
        headers=HEADERS,
    ).status_code == 200

    base_event = {
        "insight_run_id": run["id"],
        "outreach_package_id": package["id"],
        "package_version": package["package_version"],
        "vertical_id": "one_trade_network",
        "operator": "reviewer@example.com",
        "service_packages": approved_package["recommended_service_package"],
    }
    sent = client.post(
        "/api/activation-events",
        headers=HEADERS,
        json={**base_event, "stage": "outreach_sent"},
    )
    won = client.post(
        "/api/activation-events",
        headers=HEADERS,
        json={
            **base_event,
            "stage": "closed_won",
            "revenue_amount": 2500,
            "currency": "USD",
        },
    )
    funnel = client.get(
        "/api/funnel?vertical_id=one_trade_network",
        headers=HEADERS,
    ).json()["verticals"]["one_trade_network"]

    assert sent.status_code == 201
    assert won.status_code == 201
    assert funnel["stage_counts"]["package_approved"] == 1
    assert funnel["stage_counts"]["outreach_sent"] == 1
    assert funnel["stage_counts"]["closed_won"] == 1
    assert funnel["conversion_rates"]["qualified_to_approved"] == 1
    assert funnel["closed_won_revenue"] == 2500
    route_key = "+".join(sorted(approved_package["recommended_service_package"]))
    segment = funnel["service_package_segments"][route_key]
    assert segment["stage_counts"]["closed_won"] == 1
    assert segment["closed_won_revenue"] == 2500
