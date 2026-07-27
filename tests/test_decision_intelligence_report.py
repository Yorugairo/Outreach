from __future__ import annotations

import pytest

from src.models import (
    AgenticEvidenceReviewEvent,
    AgenticWorkItem,
    BusinessFactLedgerSnapshot,
    DecisionCoverageSnapshot,
    InsightRun,
    JourneyEvidenceRun,
    OwnerDiagnosticSnapshot,
    ProspectRecord,
    SEOTarget,
    canonical_sha256,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.decision_intelligence_reporting_service import (
    DecisionIntelligenceReportingService,
)


SHA = canonical_sha256({"report": "fixture"})
REF = {
    "artifact_ref": "runs/run-1/pages/home.json",
    "reference_kind": "source_span",
    "exact_span": "Beginner classes are offered Monday and Wednesday.",
}


def seed(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    target = repository.upsert_target(
        SEOTarget(
            input_url="https://novaryu.test",
            normalized_url="https://novaryu.test/",
            normalized_domain="novaryu.test",
        )
    )
    run = repository.create_run(
        InsightRun(
            id="run-1",
            seo_target_id=target.id,
            requested_url="https://novaryu.test/",
            requested_domain="novaryu.test",
            status="completed",
            current_stage="completed",
        )
    )
    repository.save_prospect(
        ProspectRecord(
            id="prospect-1",
            business_name="Nova Ryu",
            website_url="https://novaryu.test/",
            normalized_domain="novaryu.test",
            category="bjj_academy",
            location="Tacoma, WA",
            contact_route="https://novaryu.test/contact",
            source_provenance="registry",
            vertical_pack_version="national_bjj_registry.v1",
            vertical_id="national_bjj_registry",
            qualification_status="qualified",
        )
    )
    fact_work = _work("fact-work", "business_fact_ledger")
    decision_work = _work("decision-work", "decision_coverage")
    repository.save_agentic_work_item(fact_work)
    repository.save_agentic_work_item(decision_work)
    ledger = repository.save_business_fact_ledger_snapshot(
        BusinessFactLedgerSnapshot(
            run_id=run.id,
            attempt_id=run.attempt_id,
            work_item_id=fact_work.id,
            vertical_pack_version="national_bjj_registry.agentic.v1",
            source_sha256=SHA,
            review_state="approved",
            facts=[
                {
                    "fact_id": "beginner_schedule",
                    "name": "beginner schedule",
                    "normalized_value": "Monday and Wednesday",
                    "source_status": "observed",
                    "sensitivity_class": "public",
                    "approval_state": "approved",
                    "evidence_refs": [REF],
                }
            ],
        )
    )
    decision = repository.save_decision_coverage_snapshot(
        DecisionCoverageSnapshot(
            run_id=run.id,
            attempt_id=run.attempt_id,
            work_item_id=decision_work.id,
            fact_ledger_id=ledger.id,
            vertical_pack_version="national_bjj_registry.agentic.v1",
            source_sha256=SHA,
            review_state="approved",
            coverage=[
                {
                    "question_id": "beginner_schedule",
                    "status": "answered",
                    "answer": "Beginner classes are listed Monday and Wednesday.",
                    "evidence_refs": [REF],
                },
                {
                    "question_id": "first_visit",
                    "status": "missing",
                    "answer": None,
                    "evidence_refs": [],
                },
            ],
            completeness_percent=50,
        )
    )
    journeys = []
    for index, task in enumerate(
        (
            "national_bjj_registry.offer-discovery.v1",
            "national_bjj_registry.decision-resolution.v1",
            "national_bjj_registry.ready-to-convert-cta.v1",
        )
    ):
        work = _work(f"journey-work-{index}", "target_journey")
        repository.save_agentic_work_item(work)
        journey = repository.save_journey_evidence_run(
            JourneyEvidenceRun(
                run_id=run.id,
                attempt_id=run.attempt_id,
                work_item_id=work.id,
                task_id=task,
                vertical_pack_version="national_bjj_registry.agentic.v1",
                viewport="desktop" if index == 0 else "mobile",
                allowed_hosts=["novaryu.test"],
                host_policy_version="known-hosts.v1",
                source_sha256=SHA,
                result_status="unknown",
                limitations=["Frozen fixture has no live browser execution."],
            )
        )
        repository.append_agentic_evidence_review_event(
            AgenticEvidenceReviewEvent(
                snapshot_id=journey.id,
                snapshot_type="journey_evidence",
                event_type="approved",
                operator="reviewer",
                reason_code="fixture_review",
            )
        )
        journeys.append(journey)
    return repository, run, ledger, decision, journeys


def _work(identifier: str, kind: str) -> AgenticWorkItem:
    return AgenticWorkItem(
        id=identifier,
        run_id="run-1",
        attempt_id="attempt-1",
        evidence_pack_id="pack-1",
        vertical_pack_version="national_bjj_registry.agentic.v1",
        work_kind=kind,
        mode="prospect",
        source_sha256=SHA,
        idempotency_key=f"run-1:{kind}:{identifier}",
        requested_runtime="hermes",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        prompt_version="p12.v1",
        rubric_version="p12.v1",
        schema_version="p12.v1",
    )


def test_report_preserves_scores_and_adds_evidence_not_new_arithmetic(tmp_path) -> None:
    repository, run, _, _, _ = seed(tmp_path)
    reports = DecisionIntelligenceReportingService(repository).assemble(run.id)
    decision = reports["decision-intelligence-v1"]
    combined = reports["v6"]

    assert decision.report_payload["status"] == "complete"
    assert decision.report_payload["completeness_percent"] == 100
    assert decision.report_payload["outreach_teaser"]["kind"] == "decision_evidence"
    assert len(decision.report_payload["journeys"]) == 3
    assert "score" not in decision.report_payload
    assert "revenue" not in decision.report_payload
    assert combined.report_payload["decision_intelligence"]["report_contract"] == (
        "decision-intelligence-v1"
    )
    assert repository.get_latest_report_snapshot(
        run.id, "decision-intelligence-v1"
    ) is not None


def test_export_revalidates_review_and_mode_separation(tmp_path) -> None:
    repository, run, _, decision, _ = seed(tmp_path)
    reports = DecisionIntelligenceReportingService(repository).assemble(
        run.id,
        mode="prospect",
        for_export=True,
    )
    payload = reports["decision-intelligence-v1"].report_payload
    assert "owner_diagnostic" not in payload
    assert payload["customer_export"] is True

    # A successor review-required snapshot becomes latest and therefore blocks
    # export instead of silently reusing the older approved result.
    work = _work("decision-work-2", "decision_coverage")
    repository.save_agentic_work_item(work)
    repository.save_decision_coverage_snapshot(
        DecisionCoverageSnapshot(
            run_id=run.id,
            attempt_id=run.attempt_id,
            work_item_id=work.id,
            fact_ledger_id=decision.fact_ledger_id,
            vertical_pack_version="national_bjj_registry.agentic.v1",
            source_sha256=SHA,
            coverage=[
                {
                    "question_id": "first_visit",
                    "status": "missing",
                    "evidence_refs": [],
                }
            ],
            completeness_percent=0,
        )
    )
    with pytest.raises(ValueError, match="review approval"):
        DecisionIntelligenceReportingService(repository).assemble(
            run.id,
            mode="prospect",
            for_export=True,
        )


def test_shadow_evidence_cannot_enter_customer_export_even_if_approved(tmp_path) -> None:
    repository, run, _, decision, _ = seed(tmp_path)
    base = _work("shadow-decision-work", "decision_coverage")
    shadow = AgenticWorkItem(
        **{
            **base.to_dict(),
            "execution_mode": "shadow",
            "state": "complete",
        }
    )
    repository.save_agentic_work_item(shadow)
    repository.save_decision_coverage_snapshot(
        DecisionCoverageSnapshot(
            id="zzzz-shadow-decision",
            run_id=run.id,
            attempt_id=run.attempt_id,
            work_item_id=shadow.id,
            fact_ledger_id=decision.fact_ledger_id,
            vertical_pack_version="national_bjj_registry.agentic.v1",
            source_sha256=SHA,
            review_state="approved",
            coverage=[
                {
                    "question_id": "first_visit",
                    "status": "missing",
                    "answer": None,
                    "evidence_refs": [],
                }
            ],
            completeness_percent=0,
        )
    )

    with pytest.raises(ValueError, match="review approval"):
        DecisionIntelligenceReportingService(repository).assemble(
            run.id,
            mode="prospect",
            for_export=True,
        )


def test_owner_report_adds_private_diagnostic_without_leaking_to_prospect(tmp_path) -> None:
    repository, run, _, _, _ = seed(tmp_path)
    base = _work("owner-work", "business_fact_ledger")
    owner_work = AgenticWorkItem(
        **{
            **base.to_dict(),
            "work_kind": "owner_diagnostic",
            "mode": "owner_verified",
            "consent_id": "consent-1",
            "execution_mode": "premium",
            "budget_class": "premium",
            "source_snapshot_ids": ["owner-measurement-1"],
            "state": "complete",
        }
    )
    repository.save_agentic_work_item(owner_work)
    repository.save_owner_diagnostic_snapshot(
        OwnerDiagnosticSnapshot(
            run_id=run.id,
            attempt_id=run.attempt_id,
            prospect_id="prospect-1",
            work_item_id=owner_work.id,
            consent_id="consent-1",
            approved_source_snapshot_ids=["owner-measurement-1"],
            source_sha256=SHA,
            observations=[
                {
                    "observation_id": "owner-observation-1",
                    "text": "Aggregate lead activity is available for private review.",
                    "evidence_refs": [REF],
                }
            ],
            hypotheses=[],
        )
    )
    service = DecisionIntelligenceReportingService(repository)

    prospect = service.assemble(run.id, mode="prospect")[
        "decision-intelligence-v1"
    ].report_payload
    owner = service.assemble(run.id, mode="owner_verified")[
        "decision-intelligence-v1"
    ].report_payload

    assert "owner_diagnostic" not in prospect
    assert owner["owner_diagnostic"]["privacy_scope"] == "private_owner_only"
    assert owner["decision_coverage"]["questions"]
    assert len(owner["journeys"]) == 3
