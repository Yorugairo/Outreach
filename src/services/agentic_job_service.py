from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any

from src.config import AgenticAnalysisSettings, load_config
from src.models import (
    AgentCallRecord,
    AgenticAnalysisJob,
    AgenticAssessmentReviewEvent,
    AgenticAssessmentSnapshot,
    SiteEvidencePack,
    canonical_sha256,
)


class AgenticJobPolicyError(RuntimeError):
    """Raised when an agentic operation violates its explicit policy gate."""


class AgenticJobService:
    """Durable, provider-neutral agentic job lifecycle.

    This service owns queue identity, leases, retry/cost accounting, and
    append-only provenance. It deliberately has no provider/runtime callback;
    T7 adapters consume the persisted job and call ledger.
    """

    def __init__(self, repository: Any, settings: AgenticAnalysisSettings | None = None):
        self.repository = repository
        self.settings = settings or load_config().agentic

    def preflight(
        self,
        pack: SiteEvidencePack,
        *,
        analysis_mode: str = "standard",
    ) -> dict[str, Any]:
        key = self.idempotency_key(pack, analysis_mode=analysis_mode)
        existing = self.repository.get_agentic_job_by_idempotency_key(key)
        return {
            "enabled": self.settings.enabled,
            "operator_approved": self.settings.operator_approved,
            "promotion_approved": self.settings.promotion_approved,
            "available": self.settings.available,
            "idempotency_key": key,
            "planned_calls": self.settings.max_calls,
            "max_cost_usd": self.settings.max_cost_usd,
            "max_output_tokens": self.settings.max_output_tokens,
            "timeout_seconds": self.settings.timeout_seconds,
            "retry_limit": self.settings.retry_limit,
            "existing_job_id": existing.id if existing else None,
            "route": {
                "runtime": self.settings.runtime,
                "provider": self.settings.provider,
                "model": self.settings.model,
                "profile": self.settings.profile,
                "prompt_version": self.settings.prompt_version,
                "rubric_version": self.settings.rubric_version,
                "schema_version": self.settings.schema_version,
            },
        }

    def idempotency_key(self, pack: SiteEvidencePack, *, analysis_mode: str = "standard") -> str:
        return canonical_sha256(
            {
                "evidence_pack_sha256": pack.content_sha256,
                "vertical_pack_version": pack.vertical_pack_version,
                "rubric_version": self.settings.rubric_version,
                "prompt_version": self.settings.prompt_version,
                "requested_runtime": self.settings.runtime,
                "requested_provider": self.settings.provider,
                "requested_model": self.settings.model,
                "analysis_mode": analysis_mode,
            }
        )

    def enqueue_job(
        self,
        pack: SiteEvidencePack,
        *,
        analysis_mode: str = "standard",
    ) -> AgenticAnalysisJob:
        self._require_available()
        if not isinstance(pack, SiteEvidencePack):
            raise TypeError("agentic jobs require a SiteEvidencePack")
        existing = self.repository.get_agentic_job_by_idempotency_key(
            self.idempotency_key(pack, analysis_mode=analysis_mode)
        )
        if existing is not None:
            return existing
        job = AgenticAnalysisJob(
            evidence_pack_id=pack.id,
            evidence_pack_sha256=pack.content_sha256 or "",
            idempotency_key=self.idempotency_key(pack, analysis_mode=analysis_mode),
            requested_runtime=self.settings.runtime,
            requested_provider=self.settings.provider,
            requested_model=self.settings.model,
            prompt_version=self.settings.prompt_version,
            rubric_version=self.settings.rubric_version,
            schema_version=self.settings.schema_version,
            profile=self.settings.profile,
            analysis_mode=analysis_mode,
            max_calls=self.settings.max_calls,
            max_cost_usd=self.settings.max_cost_usd,
            max_output_tokens=self.settings.max_output_tokens,
            timeout_seconds=self.settings.timeout_seconds,
            retry_limit=self.settings.retry_limit,
        )
        return self.repository.save_agentic_analysis_job(job)

    create_job = enqueue_job

    def claim_job(
        self,
        job_id: str,
        owner: str,
        *,
        lease_seconds: int | None = None,
    ) -> AgenticAnalysisJob:
        self._require_available()
        if not owner.strip():
            raise ValueError("agentic job leases require an owner")
        job = self._require_job(job_id)
        now = self._now()
        if job.lease_expires_at and job.lease_expires_at > now and job.lease_owner not in {None, owner}:
            raise AgenticJobPolicyError("agentic job lease is held by another owner")
        if job.state in {"complete", "partial", "failed", "superseded"}:
            raise AgenticJobPolicyError(f"cannot lease terminal agentic job: {job.state}")
        seconds = lease_seconds if lease_seconds is not None else self.settings.timeout_seconds
        if seconds < 1:
            raise ValueError("agentic lease duration must be positive")
        claimed = replace(
            job,
            state="running",
            lease_owner=owner,
            lease_expires_at=self._iso(datetime.fromisoformat(now) + timedelta(seconds=seconds)),
            updated_at=now,
        )
        return self.repository.update_agentic_analysis_job(claimed)

    def release_lease(self, job_id: str, owner: str) -> AgenticAnalysisJob:
        job = self._require_job(job_id)
        if job.lease_owner not in {None, owner}:
            raise AgenticJobPolicyError("agentic job lease is held by another owner")
        return self.repository.update_agentic_analysis_job(
            replace(job, lease_owner=None, lease_expires_at=None, updated_at=self._now())
        )

    def record_call(self, call: AgentCallRecord) -> AgentCallRecord:
        job = self._require_job(call.job_id)
        if call.requested_runtime != job.requested_runtime or call.requested_provider != job.requested_provider:
            raise AgenticJobPolicyError("agent call route does not match requested job route")
        if call.requested_model != job.requested_model:
            raise AgenticJobPolicyError("agent call model does not match requested job model")
        if call.prompt_version != job.prompt_version or call.rubric_version != job.rubric_version:
            raise AgenticJobPolicyError("agent call contract does not match requested job")
        existing_calls = self.repository.list_agent_call_records(job_id=job.id, limit=50000)
        duplicate = next((item for item in existing_calls if item.pass_name == call.pass_name and item.attempt == call.attempt), None)
        if duplicate is not None:
            if duplicate.to_dict() == call.to_dict():
                return duplicate
            raise AgenticJobPolicyError("duplicate agent call attempt would risk duplicate spend")
        if len(existing_calls) >= job.max_calls * (job.retry_limit + 1):
            raise AgenticJobPolicyError("agent call retry budget exhausted")
        cost = call.actual_cost_usd if call.actual_cost_usd is not None else (call.estimated_cost_usd or 0.0)
        if job.actual_cost_usd + cost > job.max_cost_usd + 0.000001:
            raise AgenticJobPolicyError("agent call would exceed job cost ceiling")
        total_output = sum(item.output_tokens + item.reasoning_tokens for item in existing_calls)
        if total_output + call.output_tokens + call.reasoning_tokens > job.max_output_tokens:
            raise AgenticJobPolicyError("agent call would exceed output token ceiling")
        stored = self.repository.append_agent_call_record(call)
        updated = replace(
            job,
            call_attempts=len(existing_calls) + 1,
            actual_cost_usd=job.actual_cost_usd + cost,
            updated_at=self._now(),
        )
        if call.status == "failed" and call.failure_class not in {"transient"}:
            updated = replace(updated, state="failed", error_class=call.failure_class, error_text="agent call failed")
        elif call.routing_diverged:
            updated = replace(updated, state="needs_review", error_class="policy",
                              error_text="served provider/model diverged from requested route")
        elif call.status == "success":
            updated = replace(updated, state="validating")
        self.repository.update_agentic_analysis_job(updated)
        return stored

    def retry_job(self, job_id: str) -> AgenticAnalysisJob:
        job = self._require_job(job_id)
        calls = self.repository.list_agent_call_records(job_id=job.id, limit=50000)
        latest_failed = next((call for call in reversed(calls) if call.status == "failed"), None)
        if latest_failed is None or latest_failed.failure_class != "transient":
            raise AgenticJobPolicyError("only transient agent failures may be retried")
        attempts_for_pass = sum(1 for call in calls if call.pass_name == latest_failed.pass_name)
        if attempts_for_pass > job.retry_limit:
            raise AgenticJobPolicyError("agent transient retry limit exhausted")
        return self.repository.update_agentic_analysis_job(
            replace(job, state="queued", error_class=None, error_text=None,
                    lease_owner=None, lease_expires_at=None, updated_at=self._now())
        )

    def save_assessment(self, assessment: AgenticAssessmentSnapshot) -> AgenticAssessmentSnapshot:
        job = self._require_job(assessment.job_id)
        if assessment.evidence_pack_id != job.evidence_pack_id or assessment.evidence_pack_sha256 != job.evidence_pack_sha256:
            raise AgenticJobPolicyError("assessment evidence does not match job evidence pack")
        if assessment.total_cost_usd > job.max_cost_usd + 0.000001:
            raise AgenticJobPolicyError("assessment cost exceeds job ceiling")
        return self.repository.save_agentic_assessment_snapshot(assessment)

    def complete_job(self, job_id: str, *, state: str = "complete") -> AgenticAnalysisJob:
        if state not in {"complete", "partial", "needs_review"}:
            raise ValueError("invalid completed agentic job state")
        job = self._require_job(job_id)
        return self.repository.update_agentic_analysis_job(
            replace(job, state=state, lease_owner=None, lease_expires_at=None,
                    completed_at=self._now(), updated_at=self._now())
        )

    def fail_job(
        self,
        job_id: str,
        *,
        error_class: str,
        error_text: str,
    ) -> AgenticAnalysisJob:
        job = self._require_job(job_id)
        return self.repository.update_agentic_analysis_job(
            replace(
                job,
                state="failed",
                error_class=error_class,
                error_text=error_text[:500],
                lease_owner=None,
                lease_expires_at=None,
                completed_at=self._now(),
                updated_at=self._now(),
            )
        )

    def append_review_event(self, event: AgenticAssessmentReviewEvent) -> AgenticAssessmentReviewEvent:
        if self.repository.get_agentic_assessment_snapshot(event.assessment_id) is None:
            raise ValueError(f"assessment {event.assessment_id} does not exist")
        return self.repository.append_agentic_assessment_review_event(event)

    def review_state(self, assessment_id: str) -> str:
        return self.repository.get_agentic_assessment_review_state(assessment_id)

    def _require_available(self) -> None:
        if not self.settings.available:
            raise AgenticJobPolicyError(
                "agentic analysis is disabled, lacks operator approval, or has not passed promotion gates"
            )

    def _require_job(self, job_id: str) -> AgenticAnalysisJob:
        job = self.repository.get_agentic_analysis_job(job_id)
        if job is None:
            raise ValueError(f"agentic job {job_id} not found")
        return job

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _iso(value: datetime) -> str:
        return value.astimezone(timezone.utc).isoformat()

    # Service-facing spellings retained for API/job adapters.
    start_job = enqueue_job
    lease_job = claim_job
    record_agent_call = record_call
    persist_assessment = save_assessment
    request_review = append_review_event
