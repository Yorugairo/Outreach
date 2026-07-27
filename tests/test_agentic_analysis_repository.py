from __future__ import annotations

from pathlib import Path

import pytest

from src.models import (
    AGENTIC_ASSESSMENT_SCHEMA_VERSION,
    AgentCallRecord,
    AgenticAnalysisJob,
    AgenticAssessmentReviewEvent,
    AgenticAssessmentSnapshot,
    AgenticFinding,
    SiteEvidencePack,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository


SHA_A = "a" * 64


def _repositories(tmp_path: Path):
    return [
        FileBackedInsightRepository(tmp_path / "files"),
        SQLiteInsightRepository(tmp_path / "seo-insights.db", tmp_path / "artifacts"),
    ]


def _pack() -> SiteEvidencePack:
    return SiteEvidencePack(
        run_id="run-1", attempt_id="attempt-1",
        source_snapshot_ids={"seo": "snapshot-1"}, source_hashes={"seo": SHA_A},
        target_facts={"business_name": "Nova Ryu"},
        page_facts=[{"page_id": "page-1", "title": "Brazilian Jiu-Jitsu"}],
        deterministic_surfaces={"technical_seo_health": {"score": 70}},
        evidence_refs=[{"artifact_path": "pages/page-1.json", "field": "title"}],
        completeness_percent=80,
    )


def _job(pack: SiteEvidencePack) -> AgenticAnalysisJob:
    return AgenticAnalysisJob(
        id="job-1", evidence_pack_id=pack.id, evidence_pack_sha256=pack.content_sha256 or "",
        idempotency_key="idempotency-1", requested_runtime="hermes-openrouter",
        requested_provider="openrouter", requested_model="deepseek/deepseek-v4-flash",
        prompt_version="prompt.v1", rubric_version="rubric.v1",
        schema_version=AGENTIC_ASSESSMENT_SCHEMA_VERSION,
    )


def _call(job: AgenticAnalysisJob) -> AgentCallRecord:
    return AgentCallRecord(
        id="call-1", job_id=job.id, pass_name="evidence_analyst",
        requested_runtime=job.requested_runtime, requested_provider=job.requested_provider,
        requested_model=job.requested_model, prompt_version=job.prompt_version,
        rubric_version=job.rubric_version, schema_version=job.schema_version,
        status="success", served_provider="openrouter", served_model=job.requested_model,
        raw_response_ref="agentic/raw/call-1.json", output_tokens=10, actual_cost_usd=0.01,
    )


def _assessment(job: AgenticAnalysisJob, pack: SiteEvidencePack) -> AgenticAssessmentSnapshot:
    finding = AgenticFinding(
        claim_type="recommendation", title="Clarify trial path", claim="Make signup visible.",
        confidence="high", severity="high", commercial_relevance="Reduces friction.",
        service_fit=["website_seo_vertical_visibility"],
        evidence_refs=[{"artifact_path": "pages/page-1.json", "field": "title"}],
        customer_safe=True,
    )
    return AgenticAssessmentSnapshot(
        id="assessment-1", job_id=job.id, evidence_pack_id=pack.id,
        evidence_pack_sha256=pack.content_sha256 or "", runtime=job.requested_runtime,
        requested_model=job.requested_model, served_model=job.requested_model,
        served_provider="openrouter", prompt_version=job.prompt_version,
        rubric_version=job.rubric_version, schema_version=AGENTIC_ASSESSMENT_SCHEMA_VERSION,
        findings=[finding.to_dict()], validation_result={"customer_safe": True},
    )


def test_agentic_records_are_immutable_or_append_only(tmp_path: Path) -> None:
    for repository in _repositories(tmp_path):
        pack = repository.save_site_evidence_pack(_pack())
        assert repository.save_site_evidence_pack(pack).id == pack.id
        with pytest.raises(ValueError, match="immutable"):
            repository.save_site_evidence_pack(
                SiteEvidencePack(**{**pack.to_dict(), "limitations": ["changed"], "content_sha256": None})
            )

        job = repository.save_agentic_analysis_job(_job(pack))
        assert repository.get_agentic_job_by_idempotency_key(job.idempotency_key).id == job.id
        call = repository.append_agent_call_record(_call(job))
        assert repository.append_agent_call_record(call).id == call.id
        with pytest.raises(ValueError, match="append-only"):
            repository.append_agent_call_record(
                AgentCallRecord(
                    **{key: value for key, value in call.to_dict().items() if key not in {"routing_diverged", "status", "failure_class"}},
                    status="failed", failure_class="policy",
                )
            )

        assessment = repository.save_agentic_assessment_snapshot(_assessment(job, pack))
        event = AgenticAssessmentReviewEvent(
            assessment_id=assessment.id, event_type="review_requested", operator="operator", reason_code="identity_claim"
        )
        repository.append_agentic_assessment_review_event(event)
        assert repository.get_agentic_assessment_review_state(assessment.id) == "needs_review"


def test_sqlite_agentic_records_survive_reopen(tmp_path: Path) -> None:
    db, artifacts = tmp_path / "db.sqlite3", tmp_path / "artifacts"
    repository = SQLiteInsightRepository(db, artifacts)
    pack = repository.save_site_evidence_pack(_pack())
    job = repository.save_agentic_analysis_job(_job(pack))
    repository.append_agent_call_record(_call(job))
    repository.save_agentic_assessment_snapshot(_assessment(job, pack))
    repository.close()

    reopened = SQLiteInsightRepository(db, artifacts)
    assert reopened.get_site_evidence_pack(pack.id).content_sha256 == pack.content_sha256
    assert reopened.list_agent_call_records(job_id=job.id)[0].id == "call-1"
