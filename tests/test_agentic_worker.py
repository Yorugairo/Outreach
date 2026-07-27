from __future__ import annotations

from pathlib import Path

from src.config import AgenticAnalysisSettings
from src.models import AgenticAnalysisJob, AgenticWorkItem
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.agentic_worker_service import AgenticWorkerError, AgenticWorkerService


SHA = "a" * 64


def _work_item() -> AgenticWorkItem:
    return AgenticWorkItem(
        id="work-1",
        run_id="run-1",
        attempt_id="attempt-1",
        evidence_pack_id="pack-1",
        vertical_pack_version="national_bjj_registry.agentic.v1",
        work_kind="business_fact_ledger",
        mode="prospect",
        source_sha256=SHA,
        idempotency_key="work-key-1",
        requested_runtime="hermes-openrouter",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version="schema.v1",
    )


def _p10_job() -> AgenticAnalysisJob:
    return AgenticAnalysisJob(
        id="job-1",
        evidence_pack_id="pack-1",
        evidence_pack_sha256=SHA,
        idempotency_key="job-key-1",
        requested_runtime="hermes-openrouter",
        requested_provider="openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version="schema.v1",
    )


class FakeAnalysisService:
    def __init__(self, repository):
        self.repository = repository
        self.calls: list[str] = []

    def run_job(self, job_id: str, runtime, *, worker_id: str):
        self.calls.append(job_id)
        job = self.repository.get_agentic_analysis_job(job_id)
        self.repository.update_agentic_analysis_job(
            type(job)(**{**job.to_dict(), "state": "complete", "lease_owner": None, "lease_expires_at": None})
        )


def test_worker_executes_p10_and_p12_outside_request_path(tmp_path: Path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    repository.save_agentic_analysis_job(_p10_job())
    repository.save_agentic_work_item(_work_item())
    attempts = {"count": 0}

    def execute(item: AgenticWorkItem):
        attempts["count"] += 1
        return {"state": "complete", "output_tokens": 12, "actual_cost_usd": 0.01}

    analysis = FakeAnalysisService(repository)
    worker = AgenticWorkerService(
        repository,
        artifact_root=str(tmp_path),
        settings=AgenticAnalysisSettings(enabled=True, operator_approved=True, promotion_approved=True),
        runtime=object(),
        work_item_executor=execute,
        analysis_service=analysis,
    )
    result = worker.run_once()
    assert analysis.calls == ["job-1"]
    assert attempts["count"] == 1
    assert result["p10"]["completed"] == 1
    assert result["p12"]["completed"] == 1
    assert repository.get_agentic_work_item("work-1").state == "complete"


def test_transient_work_errors_are_requeued_with_bounded_retries(tmp_path: Path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    repository.save_agentic_work_item(_work_item())
    attempts = {"count": 0}

    def execute(item: AgenticWorkItem):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise AgenticWorkerError("provider timeout", failure_class="transient")
        return None

    worker = AgenticWorkerService(
        repository,
        artifact_root=str(tmp_path),
        work_item_executor=execute,
    )
    first = worker.run_once(max_jobs=0)
    assert first["p12"]["failed"] == 1
    assert repository.get_agentic_work_item("work-1").state == "queued"
    second = worker.run_once(max_jobs=0)
    assert second["p12"]["completed"] == 1
    assert repository.get_agentic_work_item("work-1").state == "complete"


def test_worker_leaves_queued_items_when_runtime_or_executor_missing(tmp_path: Path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    repository.save_agentic_analysis_job(_p10_job())
    repository.save_agentic_work_item(_work_item())
    worker = AgenticWorkerService(repository, artifact_root=str(tmp_path))
    result = worker.run_once()
    assert result["p10"]["skipped"] == 1
    assert result["p12"]["skipped"] == 1
    assert repository.get_agentic_work_item("work-1").state == "queued"

