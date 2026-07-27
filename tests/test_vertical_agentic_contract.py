from __future__ import annotations

import dataclasses

import pytest

from src.models import (
    AIRepresentationAccuracySnapshot,
    AgenticToolStep,
    AgenticWorkItem,
    BusinessFactLedgerSnapshot,
    DecisionCoverageSnapshot,
    JourneyEvidenceRun,
    OwnerDiagnosticSnapshot,
    RecommendationOutcomeLink,
    RemediationBlueprintSnapshot,
    VerticalAgenticPack,
    canonical_sha256,
)


SHA = canonical_sha256({"fixture": "p12"})


def evidence_ref(
    *,
    artifact: str = "runs/run-1/pages/page-1.json",
    span: str = "Classes are available Monday through Saturday.",
) -> dict[str, str]:
    return {
        "artifact_ref": artifact,
        "reference_kind": "source_span",
        "exact_span": span,
    }


def approved_pack() -> VerticalAgenticPack:
    return VerticalAgenticPack(
        vertical_id="national_bjj_registry",
        version="national_bjj_registry.agentic.v1",
        display_name="National BJJ Registry",
        buyer_questions=[
            {
                "question_id": "schedule",
                "question": "When are beginner classes?",
                "buyer_stage": "decision",
                "applicability": {"all": True},
            }
        ],
        journey_tasks=[
            {
                "task_id": "offer",
                "task_kind": "offer_discovery",
                "viewport": "desktop",
                "objective": "Find the primary programs.",
                "success_oracle": {"required_evidence": ["program_name"]},
                "applicability": {"all": True},
            },
            {
                "task_id": "decision",
                "task_kind": "decision_resolution",
                "viewport": "mobile",
                "objective": "Resolve schedule and first-visit questions.",
                "success_oracle": {"required_evidence": ["schedule"]},
                "applicability": {"all": True},
            },
            {
                "task_id": "cta",
                "task_kind": "ready_to_convert_cta",
                "viewport": "mobile",
                "objective": "Reach a non-submitting trial CTA.",
                "success_oracle": {"required_evidence": ["cta_destination"]},
                "applicability": {"all": True},
            },
        ],
        service_mappings={"website_upgrade": ["schedule", "offer"]},
        action_host_policy_version="known-hosts.v1",
        source_sha256=SHA,
        state="approved",
        approved_by="operator@example.test",
        approved_at="2026-07-26T12:00:00+00:00",
    )


def work_item(**overrides: object) -> AgenticWorkItem:
    payload: dict[str, object] = {
        "run_id": "run-1",
        "attempt_id": "attempt-1",
        "evidence_pack_id": "pack-1",
        "vertical_pack_version": "national_bjj_registry.agentic.v1",
        "work_kind": "target_journey",
        "mode": "prospect",
        "source_sha256": SHA,
        "idempotency_key": "run-1:target-journey:offer:v1",
        "requested_runtime": "hermes",
        "requested_provider": "openrouter",
        "requested_model": "deepseek/deepseek-v4-flash",
        "prompt_version": "journey.v1",
        "rubric_version": "journey.v1",
        "schema_version": "journey.v1",
    }
    payload.update(overrides)
    return AgenticWorkItem(**payload)


def test_vertical_pack_requires_all_three_bounded_journeys() -> None:
    pack = approved_pack()
    assert pack.state == "approved"
    assert {task["task_kind"] for task in pack.journey_tasks} == {
        "offer_discovery",
        "decision_resolution",
        "ready_to_convert_cta",
    }

    payload = pack.to_dict()
    payload.pop("id")
    payload.pop("created_at")
    payload["journey_tasks"] = payload["journey_tasks"][:2]
    with pytest.raises(ValueError, match="all three"):
        VerticalAgenticPack(**payload)


def test_work_item_enforces_cost_execution_and_owner_boundaries() -> None:
    item = work_item()
    assert item.max_cost_usd == 0.25
    assert item.max_model_decisions == 12
    assert item.max_browser_actions == 30
    assert item.timeout_seconds == 90

    with pytest.raises(ValueError, match=r"\$0.25"):
        work_item(max_cost_usd=0.26)
    with pytest.raises(ValueError, match="recorded consent"):
        work_item(mode="owner_verified")
    with pytest.raises(ValueError, match="cannot run in prospect"):
        work_item(work_kind="owner_diagnostic")
    with pytest.raises(ValueError, match="cannot bind owner"):
        work_item(consent_id="consent-1")

    premium = work_item(budget_class="premium", max_cost_usd=0.75)
    assert premium.max_cost_usd == 0.75


def test_browser_trace_accepts_only_enumerated_non_mutating_actions() -> None:
    allowed = AgenticToolStep(
        work_item_id="work-1",
        sequence=1,
        action_kind="activate_candidate",
        candidate_action_id="candidate-2",
        policy_decision="allowed",
        outcome="navigation_completed",
        before_url="https://example.test/",
        after_url="https://example.test/schedule",
    )
    assert allowed.sequence == 1

    with pytest.raises(ValueError, match="prohibited"):
        AgenticToolStep(
            work_item_id="work-1",
            sequence=2,
            action_kind="submit",
            candidate_action_id="candidate-3",
            policy_decision="blocked",
            policy_reason="state changing",
            outcome="blocked",
        )
    with pytest.raises(ValueError, match="cannot record"):
        AgenticToolStep(
            work_item_id="work-1",
            sequence=2,
            action_kind="navigate_candidate",
            candidate_action_id="candidate-3",
            policy_decision="needs_approval",
            policy_reason="unknown host",
            outcome="blocked",
            after_url="https://unknown.example/",
        )


def test_fact_and_decision_claims_require_exact_grounding() -> None:
    fact = {
        "fact_id": "schedule",
        "name": "class schedule",
        "normalized_value": "Monday through Saturday",
        "source_status": "observed",
        "sensitivity_class": "public",
        "approval_state": "approved",
        "evidence_refs": [evidence_ref()],
    }
    ledger = BusinessFactLedgerSnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        work_item_id="work-1",
        vertical_pack_version="national_bjj_registry.agentic.v1",
        source_sha256=SHA,
        facts=[fact],
    )
    assert len(ledger.content_sha256 or "") == 64

    unsupported = dict(fact)
    unsupported["evidence_refs"] = []
    with pytest.raises(ValueError, match="exact evidence"):
        BusinessFactLedgerSnapshot(
            run_id="run-1",
            attempt_id="attempt-1",
            work_item_id="work-1",
            vertical_pack_version="national_bjj_registry.agentic.v1",
            source_sha256=SHA,
            facts=[unsupported],
        )

    decision = DecisionCoverageSnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        work_item_id="work-2",
        fact_ledger_id=ledger.id,
        vertical_pack_version="national_bjj_registry.agentic.v1",
        source_sha256=SHA,
        coverage=[
            {
                "question_id": "schedule",
                "status": "answered",
                "answer": "Classes run Monday through Saturday.",
                "evidence_refs": [evidence_ref()],
            },
            {"question_id": "pricing", "status": "unknown", "evidence_refs": []},
        ],
        completeness_percent=50,
    )
    assert decision.coverage[1]["status"] == "unknown"

    with pytest.raises(ValueError, match="answered"):
        DecisionCoverageSnapshot(
            run_id="run-1",
            attempt_id="attempt-1",
            work_item_id="work-2",
            fact_ledger_id=ledger.id,
            vertical_pack_version="national_bjj_registry.agentic.v1",
            source_sha256=SHA,
            coverage=[
                {"question_id": "schedule", "status": "answered", "evidence_refs": []}
            ],
            completeness_percent=100,
        )


def test_journey_is_bounded_and_unknown_hosts_are_not_implicit() -> None:
    journey = JourneyEvidenceRun(
        run_id="run-1",
        attempt_id="attempt-1",
        work_item_id="work-1",
        task_id="offer",
        vertical_pack_version="national_bjj_registry.agentic.v1",
        viewport="desktop",
        allowed_hosts=["NOVARYU.COM", "signup.novaryu.com"],
        host_policy_version="known-hosts.v1",
        source_sha256=SHA,
        result_status="passed",
        tool_step_ids=["step-1"],
        model_decisions=3,
        browser_actions=7,
        elapsed_seconds=12.5,
    )
    assert journey.allowed_hosts == ["novaryu.com", "signup.novaryu.com"]

    with pytest.raises(ValueError, match="bounded"):
        JourneyEvidenceRun(
            run_id="run-1",
            attempt_id="attempt-1",
            work_item_id="work-1",
            task_id="offer",
            vertical_pack_version="national_bjj_registry.agentic.v1",
            viewport="desktop",
            allowed_hosts=["novaryu.com"],
            host_policy_version="known-hosts.v1",
            source_sha256=SHA,
            result_status="unknown",
            model_decisions=13,
        )
    with pytest.raises(ValueError, match="normalized"):
        JourneyEvidenceRun(
            run_id="run-1",
            attempt_id="attempt-1",
            work_item_id="work-1",
            task_id="offer",
            vertical_pack_version="national_bjj_registry.agentic.v1",
            viewport="desktop",
            allowed_hosts=["https://unknown.example/path"],
            host_policy_version="known-hosts.v1",
            source_sha256=SHA,
            result_status="blocked",
        )


def test_ai_representation_uses_response_spans_and_unknown_semantics() -> None:
    response_ref = {
        "artifact_ref": "runs/run-1/provider/response.json",
        "reference_kind": "provider_artifact",
        "response_span": "The academy offers evening classes.",
    }
    snapshot = AIRepresentationAccuracySnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        work_item_id="work-3",
        fact_ledger_id="ledger-1",
        source_sha256=SHA,
        claims=[
            {
                "claim_id": "claim-1",
                "classification": "unverifiable",
                "response_evidence_ref": response_ref,
                "fact_evidence_refs": [],
            }
        ],
        completeness_percent=25,
    )
    assert snapshot.claims[0]["classification"] == "unverifiable"

    with pytest.raises(ValueError, match="ledger evidence"):
        AIRepresentationAccuracySnapshot(
            run_id="run-1",
            attempt_id="attempt-1",
            work_item_id="work-3",
            fact_ledger_id="ledger-1",
            source_sha256=SHA,
            claims=[
                {
                    "claim_id": "claim-1",
                    "classification": "correct",
                    "response_evidence_ref": response_ref,
                    "fact_evidence_refs": [],
                }
            ],
        )


def test_owner_diagnostics_are_private_consent_bound_and_evidence_backed() -> None:
    observation = {
        "observation_id": "obs-1",
        "text": "Aggregate visits rise before trial bookings.",
        "evidence_refs": [
            {
                "artifact_ref": "owned/ga4-1.json",
                "reference_kind": "persisted_field",
                "field_path": "metrics.sessions",
            }
        ],
    }
    owner = OwnerDiagnosticSnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        prospect_id="prospect-1",
        work_item_id="work-owner",
        consent_id="consent-1",
        approved_source_snapshot_ids=["ga4-1"],
        source_sha256=SHA,
        observations=[observation],
        hypotheses=[dict(observation, observation_id="hyp-1")],
    )
    assert owner.privacy_scope == "private_owner_only"

    with pytest.raises(ValueError, match="private owner-mode"):
        OwnerDiagnosticSnapshot(
            run_id="run-1",
            attempt_id="attempt-1",
            prospect_id="prospect-1",
            work_item_id="work-owner",
            consent_id="consent-1",
            approved_source_snapshot_ids=["ga4-1"],
            source_sha256=SHA,
            observations=[observation],
            hypotheses=[],
            mode="prospect",
        )


def test_blueprints_are_structured_not_model_generated_code() -> None:
    blueprint = RemediationBlueprintSnapshot(
        run_id="run-1",
        attempt_id="attempt-1",
        work_item_id="work-blueprint",
        mode="prospect",
        source_snapshot_ids=["decision-1", "journey-1"],
        source_sha256=SHA,
        blueprint={
            "pages": [{"page_type": "program", "sections": ["answer_block", "cta"]}],
            "navigation": [{"label": "Programs", "destination": "programs"}],
        },
        evidence_refs=[evidence_ref()],
    )
    assert blueprint.renderer_version == "offline-prototype.v1"

    with pytest.raises(ValueError, match="executable"):
        RemediationBlueprintSnapshot(
            run_id="run-1",
            attempt_id="attempt-1",
            work_item_id="work-blueprint",
            mode="prospect",
            source_snapshot_ids=["decision-1"],
            source_sha256=SHA,
            blueprint={"html": "<main>model output</main>"},
            evidence_refs=[evidence_ref()],
        )


def test_outcome_links_bind_versions_without_causal_or_score_fields() -> None:
    link = RecommendationOutcomeLink(
        recommendation_id="recommendation-1",
        source_snapshot_id="blueprint-1",
        outreach_package_id="package-1",
        outreach_package_version=2,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        service_fit=["website_upgrade"],
        activation_event_ids=["sent-1", "reply-1"],
    )
    assert link.outreach_package_version == 2

    snapshot_types = (
        BusinessFactLedgerSnapshot,
        DecisionCoverageSnapshot,
        JourneyEvidenceRun,
        AIRepresentationAccuracySnapshot,
        OwnerDiagnosticSnapshot,
        RemediationBlueprintSnapshot,
        RecommendationOutcomeLink,
    )
    for snapshot_type in snapshot_types:
        fields = {item.name for item in dataclasses.fields(snapshot_type)}
        assert "score" not in fields
        assert "conversion_rate" not in fields
        assert "revenue" not in fields
