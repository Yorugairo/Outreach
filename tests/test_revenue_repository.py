from __future__ import annotations

from pathlib import Path

import pytest

from src.models import OutreachActivationEvent, OutreachPackage
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.prospect_intake_service import ProspectIntakeService
from src.vertical_packs import get_vertical_pack


def _repositories(tmp_path: Path):
    return [
        FileBackedInsightRepository(tmp_path / "files"),
        SQLiteInsightRepository(tmp_path / "seo-insights.db", artifact_root=tmp_path / "artifacts"),
    ]


def _prospect():
    csv_text = (
        "business_name,website_url,category,location,contact_route,source\n"
        "Austin Plumbing,example.com,plumber,Austin TX,owner@example.com,fixture\n"
    )
    return ProspectIntakeService().commit_csv(csv_text, "one_trade_network.v1")[0]


def _package(prospect_id: str, *, state: str = "needs_review") -> OutreachPackage:
    return OutreachPackage(
        insight_run_id="run-1",
        prospect_id=prospect_id,
        vertical_pack_version="one_trade_network.v1",
        report_version="v2",
        package_version=1,
        state=state,
        approved_findings=[
            {
                "finding_type": "prospect_issue",
                "category": "page_metadata",
                "title": "Missing title",
                "observation": "A page title is missing.",
                "impact": "Search snippets may be unclear.",
                "recommended_action": "Add a specific title.",
                "severity": "medium",
                "effort": "small",
                "confidence": "high",
                "recommended_services": ["web_development_rebuild"],
                "service_fit_reason": "Website evidence supports remediation.",
                "evidence_refs": [{"artifact_path": "pages/page-1.json", "field": "title", "reason": "missing", "observed": None}],
                "evidence_family": "technical_seo",
            }
        ],
        executive_answer="A concrete website issue was found.",
        what_we_found="A page title is missing.",
        why_it_matters="Search snippets may be unclear.",
        what_we_would_fix="Add a specific title.",
        confidence="high",
        effort="small",
        recommended_service_package=["web_development_rebuild"],
        subject_line="Search evidence worth reviewing",
        email_body="Manual outreach copy.",
        evidence_brief="# Evidence brief\n",
        approved_by="operator" if state == "approved" else None,
        approved_at="2026-07-25T00:00:00Z" if state == "approved" else None,
    )


def test_revenue_contracts_persist_and_filter_in_file_and_sqlite(tmp_path: Path):
    for repo in _repositories(tmp_path):
        pack = repo.save_vertical_pack(get_vertical_pack("one_trade_network.v1"))
        prospect = repo.save_prospect(_prospect())
        package = repo.save_outreach_package(_package(prospect.id))
        outreach_dir = repo.root / "runs" / package.insight_run_id / "outreach" if hasattr(repo, "root") else repo.artifact_root / "runs" / package.insight_run_id / "outreach"
        assert not (outreach_dir / f"{package.id}.txt").exists()
        assert not (outreach_dir / f"{package.id}.md").exists()
        approved = repo.save_outreach_package(OutreachPackage(**{**_package(prospect.id, state="approved").to_dict(), "id": package.id}))
        assert (outreach_dir / f"{package.id}.txt").exists()
        assert (outreach_dir / f"{package.id}.md").exists()
        event = repo.append_activation_event(
            OutreachActivationEvent(
                insight_run_id=approved.insight_run_id,
                outreach_package_id=approved.id,
                package_version=approved.package_version,
                stage="package_approved",
                vertical_id=pack.vertical_id,
                operator="operator",
                service_packages=approved.recommended_service_package,
            )
        )

        assert repo.get_vertical_pack(pack.pack_id).pack_id == pack.pack_id
        assert repo.get_prospect(prospect.id).normalized_domain == "example.com"
        assert repo.list_prospects(vertical_id="one_trade_network", qualification_status="qualified")[0].id == prospect.id
        assert repo.get_outreach_package(package.id).state == "approved"
        assert repo.list_outreach_packages(prospect_id=prospect.id, state="approved")[0].id == package.id
        assert repo.list_activation_events(outreach_package_id=package.id)[0].id == event.id

        changed = OutreachActivationEvent(**{**event.to_dict(), "operator": "other"})
        with pytest.raises(ValueError, match="append-only"):
            repo.append_activation_event(changed)

        changed_package = OutreachPackage(**{**approved.to_dict(), "subject_line": "Changed"})
        with pytest.raises(ValueError, match="immutable"):
            repo.save_outreach_package(changed_package)


def test_sqlite_revenue_tables_survive_reopen(tmp_path: Path):
    database_path = tmp_path / "seo-insights.db"
    artifact_root = tmp_path / "artifacts"
    repo = SQLiteInsightRepository(database_path, artifact_root=artifact_root)
    prospect = repo.save_prospect(_prospect())
    package = repo.save_outreach_package(_package(prospect.id, state="approved"))
    repo.append_activation_event(
        OutreachActivationEvent(
            insight_run_id=package.insight_run_id,
            outreach_package_id=package.id,
            package_version=package.package_version,
            stage="outreach_sent",
            vertical_id=prospect.vertical_id,
            operator="operator",
            service_packages=package.recommended_service_package,
        )
    )
    repo.close()

    reopened = SQLiteInsightRepository(database_path, artifact_root=artifact_root)

    assert reopened.get_prospect(prospect.id).id == prospect.id
    assert reopened.get_outreach_package(package.id).state == "approved"
    assert reopened.list_activation_events(vertical_id=prospect.vertical_id)[0].stage == "outreach_sent"
