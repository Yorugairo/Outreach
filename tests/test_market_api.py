from pathlib import Path

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.models import KeywordSet, KeywordTarget, MarketEvidenceRun, ProspectRecord, utc_now_iso
from src.orchestrator import InsightRunOrchestrator
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.market_reporting_service import MarketReportingService
from src.services.outreach_service import OutreachService


def _market_ready_fixture(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root)
    run = InsightRunOrchestrator(repository, artifact_root=artifact_root).start(
        "example.com",
        mode="quick",
        max_pages=1,
    )
    target = KeywordTarget(
        keyword="bjj tacoma",
        category="Primary Local Core",
        search_intent="Commercial / Transactional",
        optimization_focus="SEO",
        target_page_usage="Homepage / Main Landing",
        pilot_selected=True,
    )
    keyword_set = KeywordSet(
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        market_slug="fixture",
        location_code=1027773,
        version="v1",
        source_sha256="a" * 64,
        keyword_targets=[target.to_dict()],
        state="approved",
        normalized_domain="example.com",
        scope_type="domain",
        scope_id="example.com",
        approved_by="operator",
        approved_at=utc_now_iso(),
    )
    repository.save_keyword_set(keyword_set)
    snapshot = {
        "keyword": "bjj tacoma",
        "category": "Primary Local Core",
        "search_intent": "Commercial / Transactional",
        "optimization_focus": "SEO",
        "target_page_usage": "Homepage / Main Landing",
        "target_rank": None,
        "target_url": None,
        "results": [{"rank": 2, "url": "https://competitor.example", "title": "Competitor"}],
        "raw_artifact_ref": "raw/fixture.json",
    }
    market_run = MarketEvidenceRun(
        insight_run_id=run.id,
        insight_attempt_id=run.attempt_id,
        keyword_set_id=keyword_set.id,
        keyword_set_version=keyword_set.keyword_set_key,
        target_domain="example.com",
        target_entity_name="Example BJJ",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        location_code=1027773,
        state="partial",
        organic_evidence=[snapshot],
        approved_competitors=[{
            "candidate_id": "competitor.example",
            "domain": "competitor.example",
            "name": "Competitor",
            "approval_set_version": 1,
            "approved_by": "operator",
            "approved_at": utc_now_iso(),
        }],
        gap_matrix=[{
            "keyword": "bjj tacoma",
            "opportunity_classes": ["landing_page_gap"],
            "evidence_refs": [{
                "artifact_path": "placeholder",
                "field": "organic_evidence[0]",
                "reason": "fixture",
                "observed": snapshot,
            }],
        }],
    )
    market_ref = {
        "artifact_path": f"market/{market_run.id}.json",
        "field": "organic_evidence[0]",
        "reason": "Persisted dated Tacoma organic sample.",
        "observed": snapshot,
    }
    market_run.gap_matrix[0]["evidence_refs"] = [market_ref]
    market_run.recommended_gaps = [{
        "keyword": "bjj tacoma",
        "opportunity_class": "landing_page_gap",
        "priority_score": 12.0,
        "observation": "Example BJJ was not observed in the bounded organic sample while an approved competitor landing page was.",
        "recommended_action": "Improve the dedicated homepage for Tacoma BJJ intent.",
        "service_fit": ["website_seo_vertical_visibility", "national_bjj_registry_visibility"],
        "evidence_refs": [market_ref],
        "ranking_promise": False,
    }]
    repository.save_market_evidence_run(market_run)
    reports = MarketReportingService(repository).assemble(market_run.id)
    return repository, artifact_root, run, keyword_set, market_run, reports


def test_market_and_combined_report_order_and_score_separation(tmp_path):
    repository, artifact_root, run, _, market_run, reports = _market_ready_fixture(tmp_path)
    market = reports["market-v1"]
    combined = reports["v3"]

    assert market.report_payload["market_run_id"] == market_run.id
    assert market.report_payload["scoring_separation"].startswith("Market and competitor evidence")
    assert combined.report_payload["source_versions"]["seo"] == "v2"
    assert combined.report_payload["source_versions"]["market_run_id"] == market_run.id
    markdown = combined.export_markdown
    headings = [
        "## Executive summary",
        "## SEO",
        "## AI Readiness",
        "## Tacoma rankings",
        "## Local-pack evidence",
        "## Competitor gap matrix",
        "## Off-site authority",
        "## Screenshot comparison",
        "## Three recommended actions",
        "## Service fit",
        "## Limitations",
    ]
    assert [markdown.index(heading) for heading in headings] == sorted(markdown.index(heading) for heading in headings)
    assert (artifact_root / "runs" / run.id / "reports" / "market-v1.json").exists()
    assert (artifact_root / "runs" / run.id / "reports" / "v3.json").exists()
    assert (artifact_root / "runs" / run.id / "market" / market_run.id / "reports" / "v3.json").exists()
    repository.close()


def test_v3_outreach_revalidates_market_snapshot_and_keeps_email_score_free(tmp_path):
    repository, artifact_root, run, _, market_run, _ = _market_ready_fixture(tmp_path)
    prospect = repository.save_prospect(ProspectRecord(
        business_name="Example BJJ",
        website_url="https://example.com",
        normalized_domain="example.com",
        category="bjj academy",
        location="Tacoma, WA",
        contact_route="owner@example.com",
        source_provenance="fixture",
        vertical_id="national_bjj_registry",
        vertical_pack_version="national_bjj_registry.v1",
        qualification_status="qualified",
    ))
    service = OutreachService(repository, artifact_root=artifact_root)
    package = service.create_package(
        insight_run_id=run.id,
        prospect_id=prospect.id,
        report_version="v3",
    )

    assert package.market_evidence_run_id == market_run.id
    assert package.market_snapshot_sha256
    assert "## Tacoma competitive opportunities" in package.evidence_brief
    assert "bjj tacoma" in package.evidence_brief
    assert "SEO score" not in package.email_body
    assert "AI Readiness" not in package.email_body
    assert "guarantee" not in package.email_body.casefold()
    approved = service.approve_package(
        package.id,
        operator="operator",
        acknowledge_partial_ai=True,
    )
    assert approved.state == "approved"
    assert service.export_package(package.id)["json"]["market_evidence_run_id"] == market_run.id
    repository.close()


def test_keyword_management_and_paid_market_api_gates(tmp_path):
    repository, artifact_root, run, _, _, _ = _market_ready_fixture(tmp_path)
    app = create_app(
        repository=repository,
        artifact_root=artifact_root,
        api_key="test-secret",
        environment="test",
    )
    headers = {"X-API-Key": "test-secret"}
    with TestClient(app) as client:
        keyword_sets = client.get(
            "/api/keyword-sets?vertical_id=national_bjj_registry",
            headers=headers,
        )
        assert keyword_sets.status_code == 200
        assert keyword_sets.json()["keyword_sets"]

        draft = next(
            item for item in keyword_sets.json()["keyword_sets"]
            if item["normalized_domain"] == "novaryu.com"
        )
        approved = client.post(
            f"/api/keyword-sets/{draft['id']}/approve",
            headers=headers,
            json={"approved_keywords": [], "rejected_keywords": [], "operator": "operator"},
        )
        assert approved.status_code == 200
        assert approved.json()["pilot_preflight"]["planned_calls"] == 25

        no_approval = client.post(
            f"/api/runs/{run.id}/market-evidence/pilot",
            headers=headers,
            json={
                "keyword_set_id": approved.json()["keyword_set"]["id"],
                "approve_paid_enrichment": False,
            },
        )
        configured_missing = client.post(
            f"/api/runs/{run.id}/market-evidence/pilot",
            headers=headers,
            json={
                "keyword_set_id": approved.json()["keyword_set"]["id"],
                "approve_paid_enrichment": True,
            },
        )
        assert no_approval.status_code == 409
        assert "explicit paid-enrichment approval" in no_approval.json()["detail"]
        assert configured_missing.status_code == 409
        assert "credentials are not configured" in configured_missing.json()["detail"]

        v3 = client.get(f"/api/runs/{run.id}/report?version=v3", headers=headers)
        assert v3.status_code == 200
        assert v3.json()["report_version"] == "v3"
    repository.close()
