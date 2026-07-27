from __future__ import annotations

from pathlib import Path

import pytest

from src.config import AgenticAnalysisSettings
from src.models import AgentCallRecord, SiteEvidencePack
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_job_service import AgenticJobPolicyError, AgenticJobService


SHA_A = "a" * 64


def _pack() -> SiteEvidencePack:
    return SiteEvidencePack(
        run_id="run-1", attempt_id="attempt-1", source_snapshot_ids={"seo": "s1"},
        source_hashes={"seo": SHA_A}, target_facts={"business_name": "Nova Ryu"},
        page_facts=[{"page_id": "p1"}], deterministic_surfaces={"seo": {"score": 70}},
        evidence_refs=[{"artifact_path": "pages/p1.json", "field": "title"}],
    )


def test_disabled_by_default_and_redacted_settings() -> None:
    settings = AgenticAnalysisSettings()
    assert settings.available is False
    assert "api_key" not in settings.to_dict()


def test_job_idempotency_leases_and_duplicate_spend_are_bounded(tmp_path: Path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    pack = _pack()
    repository.save_site_evidence_pack(pack)
    service = AgenticJobService(
        repository,
        AgenticAnalysisSettings(
            enabled=True,
            operator_approved=True,
            promotion_approved=True,
        ),
    )

    job = service.enqueue_job(pack)
    assert service.enqueue_job(pack).id == job.id
    claimed = service.claim_job(job.id, "worker-1", lease_seconds=60)
    assert claimed.lease_owner == "worker-1"
    with pytest.raises(AgenticJobPolicyError, match="held by another"):
        service.claim_job(job.id, "worker-2", lease_seconds=60)

    call = AgentCallRecord(
        id="call-1", job_id=job.id, pass_name="evidence_analyst",
        requested_runtime=job.requested_runtime, requested_provider=job.requested_provider,
        requested_model=job.requested_model, prompt_version=job.prompt_version,
        rubric_version=job.rubric_version, schema_version=job.schema_version,
        status="success", served_provider="openrouter", served_model=job.requested_model,
        raw_response_ref="raw/call-1.json", output_tokens=10, actual_cost_usd=0.01,
    )
    assert service.record_call(call).id == call.id
    with pytest.raises(AgenticJobPolicyError, match="duplicate agent call"):
        service.record_call(
            AgentCallRecord(
                **{key: value for key, value in call.to_dict().items() if key not in {"routing_diverged", "id"}},
                id="call-2",
            )
        )
    assert service.complete_job(job.id).state == "complete"


def test_preflight_does_not_enable_or_call_a_provider(tmp_path: Path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    pack = _pack()
    repository.save_site_evidence_pack(pack)
    service = AgenticJobService(repository, AgenticAnalysisSettings())
    preflight = service.preflight(pack)
    assert preflight["available"] is False
    with pytest.raises(AgenticJobPolicyError, match="disabled"):
        service.enqueue_job(pack)
