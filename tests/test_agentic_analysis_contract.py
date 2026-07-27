from __future__ import annotations

import pytest

from src.models import (
    AGENTIC_ANALYSIS_VERSION,
    AGENTIC_ASSESSMENT_SCHEMA_VERSION,
    AgentCallRecord,
    AgenticAnalysisJob,
    AgenticAssessmentReviewEvent,
    AgenticAssessmentSnapshot,
    AgenticFinding,
    SiteEvidencePack,
    derive_agentic_review_state,
)


SHA_A = "a" * 64


def _pack(**overrides) -> SiteEvidencePack:
    payload = {
        "run_id": "run-1",
        "attempt_id": "attempt-1",
        "source_snapshot_ids": {"seo": "snapshot-1"},
        "source_hashes": {"seo": SHA_A},
        "target_facts": {"business_name": "Nova Ryu", "market": "Tacoma, WA"},
        "page_facts": [{"page_id": "page-1", "title": "Brazilian Jiu-Jitsu"}],
        "deterministic_surfaces": {"technical_seo_health": {"score": 70}},
        "evidence_refs": [{"artifact_path": "pages/page-1.json", "field": "title"}],
        "permitted_service_mappings": {
            "website": "website_seo_vertical_visibility",
        },
        "completeness_percent": 80,
    }
    payload.update(overrides)
    return SiteEvidencePack(**payload)


def _finding(*, customer_safe: bool = True) -> AgenticFinding:
    return AgenticFinding(
        claim_type="recommendation",
        title="Clarify the trial path",
        claim="Make the first-class signup action visible from core program pages.",
        confidence="high",
        severity="high",
        commercial_relevance="Reduces friction between discovery and a trial request.",
        service_fit=["vertical_plugin_embed"],
        evidence_refs=[{"artifact_path": "pages/page-1.json", "field": "ai_evidence"}],
        customer_safe=customer_safe,
        review_reason=None if customer_safe else "The supporting page reference was unresolved.",
    )


def test_site_evidence_pack_is_hashed_and_rejects_secret_fields() -> None:
    pack = _pack()
    assert pack.contract_version == AGENTIC_ANALYSIS_VERSION
    assert pack.content_sha256 == pack.compute_hash()

    with pytest.raises(ValueError, match="forbidden secret fields"):
        _pack(target_facts={"business_name": "Nova Ryu", "api_key": "never-persist"})


def test_agent_job_freezes_route_identity_and_budget() -> None:
    pack = _pack()
    job = AgenticAnalysisJob(
        evidence_pack_id=pack.id,
        evidence_pack_sha256=pack.content_sha256 or "",
        idempotency_key="job-key",
        requested_runtime="hermes-openrouter",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        prompt_version="outreach-analysis.prompt.v1",
        rubric_version="outreach-analysis.rubric.v1",
        schema_version=AGENTIC_ASSESSMENT_SCHEMA_VERSION,
    )
    assert job.state == "queued"
    assert job.max_calls == 4
    assert job.max_cost_usd == 0.10
    assert job.retry_limit == 2

    with pytest.raises(ValueError, match="no more than \\$0.10"):
        AgenticAnalysisJob(
            evidence_pack_id=pack.id,
            evidence_pack_sha256=pack.content_sha256 or "",
            idempotency_key="overspend",
            requested_runtime="hermes-openrouter",
            requested_provider="openrouter",
            requested_model="deepseek/deepseek-v4-flash",
            prompt_version="prompt.v1",
            rubric_version="rubric.v1",
            schema_version=AGENTIC_ASSESSMENT_SCHEMA_VERSION,
            max_cost_usd=0.11,
        )


def test_agent_call_records_actual_route_usage_and_divergence() -> None:
    call = AgentCallRecord(
        job_id="job-1",
        pass_name="evidence_analyst",
        requested_runtime="hermes-openrouter",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        served_provider="provider-a",
        served_model="deepseek/deepseek-v4-flash",
        routing_mode="fixed-zdr",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version=AGENTIC_ASSESSMENT_SCHEMA_VERSION,
        status="success",
        input_tokens=1000,
        output_tokens=250,
        actual_cost_usd=0.004,
        latency_ms=1200,
        raw_response_ref="agentic/raw/call-1.json",
    )
    assert call.routing_diverged is True
    assert call.to_dict()["routing_diverged"] is True


def test_customer_safe_findings_require_resolvable_evidence() -> None:
    finding = _finding()
    assert finding.customer_safe is True
    with pytest.raises(ValueError, match="require evidence references"):
        AgenticFinding(
            claim_type="observed",
            title="Missing evidence",
            claim="Unsupported statement.",
            confidence="low",
            severity="low",
            commercial_relevance="Unknown.",
            service_fit=[],
            evidence_refs=[],
            customer_safe=True,
        )


def test_assessment_snapshot_has_fixed_evidence_and_schema_identity() -> None:
    pack = _pack()
    finding = _finding()
    assessment = AgenticAssessmentSnapshot(
        job_id="job-1",
        evidence_pack_id=pack.id,
        evidence_pack_sha256=pack.content_sha256 or "",
        runtime="hermes-openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        served_model="deepseek/deepseek-v4-flash",
        served_provider="openrouter-provider-a",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version=AGENTIC_ASSESSMENT_SCHEMA_VERSION,
        findings=[finding.to_dict()],
        validation_result={"customer_safe": True, "invalid_reference_count": 0},
        call_ids=["call-1"],
        total_cost_usd=0.01,
        total_latency_ms=2400,
    )
    assert assessment.evidence_pack_sha256 == pack.content_sha256
    assert assessment.findings[0]["claim_type"] == "recommendation"


def test_review_state_is_derived_from_append_only_events() -> None:
    assert derive_agentic_review_state([]) == "unreviewed"
    requested = AgenticAssessmentReviewEvent(
        assessment_id="assessment-1",
        event_type="review_requested",
        operator="operator",
        reason_code="identity_claim",
        created_at="2026-07-26T00:00:00+00:00",
    )
    approved = AgenticAssessmentReviewEvent(
        assessment_id="assessment-1",
        event_type="approved",
        operator="operator",
        reason_code="evidence_resolved",
        created_at="2026-07-26T00:01:00+00:00",
    )
    corrected = AgenticAssessmentReviewEvent(
        assessment_id="assessment-1",
        event_type="correction_recorded",
        operator="operator",
        reason_code="service_mapping",
        created_at="2026-07-26T00:02:00+00:00",
    )
    assert derive_agentic_review_state([requested]) == "needs_review"
    assert derive_agentic_review_state([requested, approved]) == "approved"
    assert derive_agentic_review_state([requested, approved, corrected]) == "needs_review"
