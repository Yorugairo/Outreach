"""Durable, out-of-request execution for P10 and P12 agentic work.

The API only enqueues immutable jobs/work items.  This service is the process
boundary that may invoke a configured runtime.  It intentionally accepts the
runtime and new-work executor as injected callables so tests and later P12
specialized services remain provider-neutral.
"""

from __future__ import annotations

import threading
from dataclasses import replace
from typing import Any, Callable, Mapping

from src.config import AgenticAnalysisSettings, load_config
from src.models import AgenticAnalysisJob, AgenticWorkItem
from src.services.agentic_analysis_service import AgenticAnalysisService
from src.services.agentic_job_service import AgenticJobService
from src.services.agentic_runtime import AgenticAnalysisRuntime


class AgenticWorkerError(RuntimeError):
    """An executor error with an explicit retry classification."""

    def __init__(self, message: str, *, failure_class: str = "unknown") -> None:
        super().__init__(message)
        self.failure_class = failure_class


class AgenticWorkerService:
    """Lease and execute queued P10 jobs and P12 work items.

    P10 jobs use the existing four-pass ``AgenticAnalysisService`` and retain
    its call ledger, validation, and cost accounting.  P12 work is delegated
    to a typed callback owned by the vertical/journey services; the worker
    only owns the queue, lease, retry, and usage envelope.
    """

    def __init__(
        self,
        repository: Any,
        *,
        artifact_root: str,
        settings: AgenticAnalysisSettings | None = None,
        runtime: AgenticAnalysisRuntime | None = None,
        work_item_executor: Callable[[AgenticWorkItem], AgenticWorkItem | Mapping[str, Any] | None] | None = None,
        worker_id: str = "agentic-worker",
        analysis_service: AgenticAnalysisService | None = None,
    ) -> None:
        if not worker_id.strip():
            raise ValueError("agentic worker requires an identity")
        self.repository = repository
        self.settings = settings or load_config().agentic
        self.runtime = runtime
        self.work_item_executor = work_item_executor
        self.worker_id = worker_id.strip()
        self.analysis_service = analysis_service or AgenticAnalysisService(
            repository,
            artifact_root=artifact_root,
            job_service=AgenticJobService(repository, settings=self.settings),
        )
        self._stop = threading.Event()

    def request_shutdown(self) -> None:
        """Ask a polling worker to stop after its current bounded pass."""

        self._stop.set()

    @property
    def shutdown_requested(self) -> bool:
        return self._stop.is_set()

    def run_once(self, *, max_jobs: int = 10, max_work_items: int = 10) -> dict[str, Any]:
        """Process one bounded queue pass without blocking an API request."""

        if max_jobs < 0 or max_work_items < 0:
            raise ValueError("worker queue limits cannot be negative")
        summary: dict[str, Any] = {
            "worker_id": self.worker_id,
            "p10": {"seen": 0, "completed": 0, "failed": 0, "skipped": 0, "errors": []},
            "p12": {"seen": 0, "completed": 0, "partial": 0, "failed": 0, "skipped": 0, "errors": []},
        }
        if not self.shutdown_requested:
            self._run_p10(summary["p10"], max_jobs)
        if not self.shutdown_requested:
            self._run_p12(summary["p12"], max_work_items)
        summary["shutdown_requested"] = self.shutdown_requested
        summary["processed"] = (
            summary["p10"]["completed"]
            + summary["p10"]["failed"]
            + summary["p12"]["completed"]
            + summary["p12"]["partial"]
            + summary["p12"]["failed"]
        )
        return summary

    def poll(
        self,
        *,
        interval_seconds: float = 5.0,
        max_jobs: int = 10,
        max_work_items: int = 10,
        max_iterations: int | None = None,
    ) -> list[dict[str, Any]]:
        """Run bounded passes until shutdown is requested.

        ``max_iterations`` is useful for health checks and tests; production
        callers normally rely on ``request_shutdown``/SIGTERM.
        """

        if interval_seconds < 0:
            raise ValueError("worker poll interval cannot be negative")
        if max_iterations is not None and max_iterations < 1:
            raise ValueError("worker max_iterations must be positive")
        results: list[dict[str, Any]] = []
        iteration = 0
        while not self.shutdown_requested:
            results.append(self.run_once(max_jobs=max_jobs, max_work_items=max_work_items))
            iteration += 1
            if max_iterations is not None and iteration >= max_iterations:
                break
            if interval_seconds and not self._stop.wait(interval_seconds):
                continue
        return results

    def _run_p10(self, summary: dict[str, Any], limit: int) -> None:
        jobs = self.repository.list_agentic_analysis_jobs(state="queued", limit=limit)
        summary["seen"] = len(jobs)
        if not jobs:
            return
        if self.runtime is None:
            summary["skipped"] = len(jobs)
            summary["errors"].append("P10 runtime is not configured; queued jobs were left untouched.")
            return
        for job in jobs:
            if self.shutdown_requested:
                break
            try:
                self.analysis_service.run_job(job.id, self.runtime, worker_id=self.worker_id)
            except Exception as exc:  # runtime/service persists terminal state
                summary["failed"] += 1
                summary["errors"].append({"job_id": job.id, "error": str(exc)[:500]})
            else:
                summary["completed"] += 1

    def _run_p12(self, summary: dict[str, Any], limit: int) -> None:
        if limit == 0:
            return
        items = self.repository.list_agentic_work_items(state="queued", limit=10_000)
        priority = {
            "business_fact_ledger": 0,
            "decision_coverage": 1,
            "target_journey": 2,
            "competitor_journey": 3,
            "ai_representation_accuracy": 4,
            "owner_diagnostic": 5,
            "remediation_blueprint": 6,
        }
        items.sort(
            key=lambda item: (
                priority.get(item.work_kind, 99),
                item.created_at,
                item.id,
            )
        )
        items = items[:limit]
        summary["seen"] = len(items)
        if not items:
            return
        if self.work_item_executor is None:
            summary["skipped"] = len(items)
            summary["errors"].append("P12 work-item executor is not configured; queued work was left untouched.")
            return
        for item in items:
            if self.shutdown_requested:
                break
            try:
                leased = self.repository.lease_agentic_work_item(item.id, self.worker_id)
                result = self.work_item_executor(leased)
                completed = self._apply_work_result(leased, result)
            except Exception as exc:
                self._handle_work_failure(item.id, exc)
                summary["failed"] += 1
                summary["errors"].append({"work_item_id": item.id, "error": str(exc)[:500]})
            else:
                if completed.state == "partial":
                    summary["partial"] += 1
                elif completed.state == "failed":
                    summary["failed"] += 1
                else:
                    summary["completed"] += 1

    def _apply_work_result(
        self,
        leased: AgenticWorkItem,
        result: AgenticWorkItem | Mapping[str, Any] | None,
    ) -> AgenticWorkItem:
        if isinstance(result, AgenticWorkItem):
            if result.id != leased.id:
                raise AgenticWorkerError("work-item executor returned a different identity", failure_class="policy")
            if result.state in {"queued", "leased", "running"}:
                return self.repository.update_agentic_work_item(
                    replace(result, state="complete", lease_owner=None, lease_expires_at=None,
                            completed_at=self._now(), updated_at=self._now())
                )
            return self.repository.update_agentic_work_item(result)
        updates = dict(result or {})
        allowed = {
            "state", "error_class", "error_text", "input_tokens", "output_tokens",
            "actual_cost_usd", "model_decisions_used", "browser_actions_used",
            "completed_at",
        }
        unknown = set(updates) - allowed
        if unknown:
            raise AgenticWorkerError(
                f"work-item executor returned unsupported fields: {sorted(unknown)}",
                failure_class="validation",
            )
        current = self.repository.get_agentic_work_item(leased.id)
        if current is None:
            raise AgenticWorkerError("leased work item disappeared", failure_class="persistence")
        updates.setdefault("state", "complete")
        updates["lease_owner"] = None
        updates["lease_expires_at"] = None
        updates.setdefault("completed_at", self._now())
        updates["updated_at"] = self._now()
        return self.repository.update_agentic_work_item(replace(current, **updates))

    def _handle_work_failure(self, item_id: str, error: Exception) -> None:
        current = self.repository.get_agentic_work_item(item_id)
        if current is None:
            return
        failure_class = str(getattr(error, "failure_class", "unknown"))
        transient = failure_class == "transient"
        retryable = transient and current.attempt_count <= current.retry_limit
        if retryable:
            updated = replace(
                current,
                state="queued",
                error_class=failure_class,
                error_text=str(error)[:500],
                lease_owner=None,
                lease_expires_at=None,
                updated_at=self._now(),
            )
        else:
            updated = replace(
                current,
                state="failed",
                error_class=failure_class,
                error_text=str(error)[:500],
                lease_owner=None,
                lease_expires_at=None,
                completed_at=self._now(),
                updated_at=self._now(),
            )
        self.repository.update_agentic_work_item(updated)

    @staticmethod
    def _now() -> str:
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()
