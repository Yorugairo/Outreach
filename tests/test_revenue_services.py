from __future__ import annotations

from pathlib import Path
from dataclasses import replace

import pytest

from src.models import OutreachActivationEvent, ProspectRecord
from src.orchestrator import InsightRunOrchestrator
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.activation_service import ActivationService
from src.services.opportunity_service import OpportunityService
from src.services.outreach_service import OutreachService
from src.services.prospect_intake_service import ProspectIntakeService
from src.vertical_packs import get_vertical_pack


def _qualified_prospect():
    csv_text = (
        "business_name,website_url,category,location,contact_route,source\n"
        "Example Plumbing,example.com,plumber,Austin TX,owner@example.com,fixture\n"
    )
    return ProspectIntakeService().commit_csv(csv_text, "one_trade_network.v1")[0]


def _repo_with_run(tmp_path: Path):
    artifact_root = tmp_path / "artifacts"
    repo = SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root=artifact_root)
    run = InsightRunOrchestrator(repo, artifact_root=artifact_root).start("example.com", mode="quick", max_pages=1)
    prospect = repo.save_prospect(_qualified_prospect())
    return repo, artifact_root, run, prospect


def test_outreach_package_requires_valid_run_report_and_approval_before_export(tmp_path: Path):
    repo, artifact_root, run, prospect = _repo_with_run(tmp_path)
    service = OutreachService(repo, artifact_root=artifact_root)

    package = service.create_package(insight_run_id=run.id, prospect_id=prospect.id)

    assert package.state == "needs_review"
    assert package.report_snapshot_id
    assert package.report_snapshot_sha256
    assert package.approved_findings
    assert package.recommended_service_package == [
        "website_seo_vertical_visibility",
        "vertical_plugin_embed",
        "custom_website_crm_saas",
    ]
    assert "One Trade Network" in package.email_body
    assert "generic score pitch" in package.email_body
    assert "build client pSEO" not in package.email_body
    assert "Google rankings" not in package.email_body
    assert "## Keywords and Google rankings" in package.evidence_brief
    assert "- Evidence status: not_configured" in package.evidence_brief
    assert "## Off-site authority" in package.evidence_brief
    assert "DataForSEO Link Rank: Unknown" in package.evidence_brief
    assert "Google Domain Authority" in package.evidence_brief
    assert (artifact_root / "runs" / run.id / "outreach" / f"{package.id}.json").exists()
    with pytest.raises(ValueError, match="only approved"):
        service.export_package(package.id)

    with pytest.raises(ValueError, match="explicit operator acknowledgement"):
        service.approve_package(package.id, operator="operator")
    approved = service.approve_package(
        package.id,
        operator="operator",
        acknowledge_partial_ai=True,
    )
    exported = service.export_package(package.id)

    assert approved.state == "approved"
    assert approved.vertical_pack_version == "one_trade_network.v1"
    assert approved.approved_by == "operator"
    assert approved.approved_at
    assert (artifact_root / "runs" / run.id / "outreach" / f"{package.id}.txt").exists()
    assert (artifact_root / "runs" / run.id / "outreach" / f"{package.id}.md").exists()
    assert exported["plaintext"] == approved.email_body
    assert exported["json"]["id"] == package.id
    assert "evidence brief" in exported["markdown"].lower()


def test_outreach_approval_revalidates_product_strength_snapshot(tmp_path: Path):
    repo, artifact_root, run, prospect = _repo_with_run(tmp_path)
    service = OutreachService(repo, artifact_root=artifact_root)
    package = service.create_package(
        insight_run_id=run.id,
        prospect_id=prospect.id,
    )
    snapshot = repo.get_report_snapshot(package.report_snapshot_id)
    payload_path = artifact_root / Path(*snapshot.payload_artifact_ref.split("/"))
    payload_path.write_text('{"tampered":true}', encoding="utf-8")

    with pytest.raises(ValueError, match="payload hash"):
        service.approve_package(
            package.id,
            operator="operator",
            acknowledge_partial_ai=True,
        )


def test_outreach_package_fails_when_evidence_artifact_is_missing(tmp_path: Path):
    repo, artifact_root, run, prospect = _repo_with_run(tmp_path)
    report = repo.get_report(run.id, "v2")
    ref = report.report_payload["findings"][0]["evidence_refs"][0]
    (artifact_root / "runs" / run.id / ref["artifact_path"]).unlink()

    with pytest.raises(ValueError):
        OutreachService(repo, artifact_root=artifact_root).create_package(insight_run_id=run.id, prospect_id=prospect.id)


def test_outreach_package_without_supported_issue_cannot_be_approved(tmp_path: Path):
    repo, artifact_root, run, prospect = _repo_with_run(tmp_path)
    service = OutreachService(repo, artifact_root=artifact_root)
    package = service.create_package(insight_run_id=run.id, prospect_id=prospect.id)
    unsupported = replace(package, approved_findings=[])
    repo.save_outreach_package(unsupported)

    with pytest.raises(ValueError, match="no supported prospect issue"):
        service.approve_package(package.id, operator="operator")


def test_activation_service_is_append_only_and_derives_funnel_summary(tmp_path: Path):
    repo, artifact_root, run, prospect = _repo_with_run(tmp_path)
    outreach = OutreachService(repo, artifact_root=artifact_root)
    package = outreach.approve_package(
        outreach.create_package(insight_run_id=run.id, prospect_id=prospect.id).id,
        acknowledge_partial_ai=True,
    )
    activation = ActivationService(repo)

    first = activation.append_event(
        OutreachActivationEvent(
            insight_run_id=run.id,
            outreach_package_id=package.id,
            package_version=package.package_version,
            stage="package_approved",
            vertical_id=prospect.vertical_id,
            operator="operator",
            service_packages=package.recommended_service_package,
        )
    )
    sent = activation.append_event(
        OutreachActivationEvent(
            insight_run_id=run.id,
            outreach_package_id=package.id,
            package_version=package.package_version,
            stage="outreach_sent",
            vertical_id=prospect.vertical_id,
            operator="operator",
            service_packages=package.recommended_service_package,
        )
    )

    assert first.stage == "package_approved"
    assert sent.stage == "outreach_sent"
    summary = activation.summarize()["verticals"][prospect.vertical_id]
    assert summary["stage_counts"]["package_approved"] == 1
    assert summary["stage_counts"]["outreach_sent"] == 1
    assert summary["conversion_rates"]["approved_to_sent"] == 1
    state = activation.current_state(repo.list_activation_events(outreach_package_id=package.id))
    assert state["last_stage"] == "outreach_sent"

    with pytest.raises(ValueError, match="vertical"):
        activation.append_event(
            OutreachActivationEvent(
                insight_run_id=run.id,
                outreach_package_id=package.id,
                package_version=package.package_version,
                stage="positive_reply",
                vertical_id="national_bjj_registry",
                operator="operator",
                service_packages=package.recommended_service_package,
            )
        )
    with pytest.raises(ValueError, match="service packages"):
        activation.append_event(
            OutreachActivationEvent(
                insight_run_id=run.id,
                outreach_package_id=package.id,
                package_version=package.package_version,
                stage="positive_reply",
                vertical_id=prospect.vertical_id,
                operator="operator",
                service_packages=[],
            )
        )

    with pytest.raises(ValueError, match="revenue"):
        OutreachActivationEvent(
            insight_run_id=run.id,
            outreach_package_id=package.id,
            package_version=package.package_version,
            stage="proposal_sent",
            vertical_id=prospect.vertical_id,
            operator="operator",
            revenue_amount=1000,
            currency="USD",
        )


def test_pseo_gate_requires_valid_demand_crawl_and_systematic_coverage_evidence():
    pages = [
        {
            "id": f"page-{index}",
            "url": f"https://example.com/page-{index}",
            "fetch_status": "fetched",
            "indexable": True,
            "title": "General company information",
            "h1": "Welcome",
            "meta_description": "Learn about the company.",
        }
        for index in range(3)
    ]
    report = {
        "report_version": "v2",
        "report_status": "complete",
        "report_payload": {
            "target": {
                "normalized_domain": "example.com",
                "metadata": {"expected_services": ["emergency service"]},
            },
            "run": {
                "status": "completed",
                "input_payload": {"limits": {"max_pages": 5}},
            },
            "pages": pages,
            "search": {
                "configured": True,
                "approved": True,
                "skipped_reason": None,
                "payload": {
                    "visibility_score": 25,
                    "target_domain": "example.com",
                    "snapshot_date": "2026-07-25",
                    "language_code": "en",
                    "device": "desktop",
                    "market": "United States",
                    "source": "test-fixture",
                    "observed_ranking_urls": ["https://example.com/"],
                },
            },
            "target_context": {
                "primary_url": "https://example.com/",
                "target_domain": "example.com",
                "language_code": "en",
                "device": "desktop",
                "location_code": None,
                "market": "United States",
            },
        },
    }
    prospect = ProspectRecord(
        business_name="Example Plumbing",
        website_url="https://example.com/",
        normalized_domain="example.com",
        category="plumber",
        location="Austin TX",
        contact_route="owner@example.com",
        source_provenance="fixture",
        vertical_id="one_trade_network",
        vertical_pack_version="one_trade_network.v1",
        qualification_status="qualified",
    )

    assessment = OpportunityService().assess(
        report,
        get_vertical_pack("one_trade_network.v1"),
        prospect,
    )

    assert assessment.demand_valid is True
    assert assessment.crawl_sufficient is True
    assert assessment.coverage_gap is True
    assert assessment.pseo_eligible is True
    assert assessment.missing_services == ("emergency service",)
    assert assessment.missing_locations == ("austin tx",)
    assert len(assessment.evidence_refs) == 12
    coverage_finding = OutreachService._coverage_finding(assessment.to_dict())
    assert coverage_finding["finding_type"] == "prospect_issue"
    assert coverage_finding["recommended_services"] == []
    assert "do not present it as an offer to build client pSEO" in coverage_finding["recommended_action"]
    assert coverage_finding["evidence_refs"] == list(assessment.evidence_refs)

    report["report_payload"]["search"]["payload"]["target_domain"] = "competitor.example"
    assert OpportunityService().assess(
        report,
        get_vertical_pack("one_trade_network.v1"),
        prospect,
    ).pseo_eligible is False
