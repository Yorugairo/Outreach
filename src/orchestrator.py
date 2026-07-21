from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.config import AppConfig, load_config
from src.models import InsightRun, RunStageEvent
from src.pipeline import DEFAULT_STAGES, InsightRunPipeline
from src.repositories.base import InsightRepository


class InsightRunOrchestrator:
    """Thin 'First Mate' over InsightRunPipeline: start, resume, rerun, status, validate."""

    def __init__(
        self,
        repository: InsightRepository,
        config: Optional[AppConfig] = None,
        artifact_root: str | Path = "artifacts/seo_insight_runs",
    ):
        self.repository = repository
        self.config = config or load_config()
        self.artifact_root = Path(artifact_root)
        self._pipeline = InsightRunPipeline(
            repository=repository, config=self.config, artifact_root=self.artifact_root
        )

    def start(self, url: str, mode: str = "standard", max_pages: int = 5) -> InsightRun:
        result = self._pipeline.run(url, mode=mode, max_pages=max_pages)
        return result.run

    def status(self, run_id: str) -> dict:
        run = self.repository.get_run(run_id)
        if run is None:
            return {"run_id": run_id, "exists": False}
        events = self.repository.list_stage_events(run_id)
        return {
            "run_id": run_id,
            "exists": True,
            "status": run.status,
            "current_stage": run.current_stage,
            "summary": run.summary,
            "validation": self.validate(run_id),
            "lease": {
                "owner": run.lease_owner,
                "heartbeat_at": run.heartbeat_at,
                "lease_expires_at": run.lease_expires_at,
            },
            "stages": [
                {
                    "stage": e.stage_name,
                    "status": e.status,
                    "attempt": e.retry_count + 1,
                    "duration_ms": e.duration_ms,
                    "output_summary": e.output_summary,
                    "error_text": e.error_text,
                }
                for e in events
            ],
        }

    def validate(self, run_id: str) -> dict:
        """Validate artifact-backed completion for an InsightRun.

        This encodes the repo definition of done: a completed run is only valid when
        the persisted run record, stage events, reports, score summary, search
        intelligence skip/presence evidence, budget limits, provenance, and runtime
        execution metadata are all readable from disk/repository.
        """
        run_dir = self.artifact_root / "runs" / run_id
        run_json = run_dir / "run.json"
        report_json = run_dir / "reports" / "v1.json"
        report_md = run_dir / "reports" / "v1.md"
        events_dir = run_dir / "events"
        errors: list[str] = []

        run = self.repository.get_run(run_id)
        if run is None:
            return {
                "run_id": run_id,
                "exists": False,
                "valid": False,
                "errors": ["run.json is missing or unreadable"],
            }

        events = self.repository.list_stage_events(run_id)
        completed_by_stage = self._completed_stage_events(events)
        latest_search = completed_by_stage.get("pulling_search_intelligence")

        run_json_exists = run_json.exists()
        events_dir_exists = events_dir.exists()
        report_json_exists = report_json.exists()
        report_markdown_exists = report_md.exists()
        summary_has_overall_score = "overall_score" in run.summary
        run_limits_recorded = self._run_limits_recorded(run)
        run_execution_recorded = self._run_execution_recorded(run)
        report_actions_have_evidence_refs = self._report_actions_have_evidence_refs(run_id)

        if not run_json_exists:
            errors.append("run.json is missing")
        if run.status != "completed":
            errors.append(f"run status is {run.status!r}, expected 'completed'")
        if not events_dir_exists:
            errors.append("events directory is missing")

        missing_completed = [stage for stage in DEFAULT_STAGES if stage not in completed_by_stage]
        for stage in missing_completed:
            errors.append(f"completed stage event missing: {stage}")

        if not report_json_exists:
            errors.append("reports/v1.json is missing")
        if not report_markdown_exists:
            errors.append("reports/v1.md is missing")
        if not summary_has_overall_score:
            errors.append("run summary missing overall_score")
        if not run_limits_recorded:
            errors.append("run limit and budget metadata is not recorded")
        if not run_execution_recorded:
            errors.append("run execution lease/heartbeat metadata is not recorded")
        if not report_actions_have_evidence_refs:
            errors.append("report key actions are missing evidence_refs")

        search_intelligence_recorded = self._search_intelligence_recorded(run, latest_search)
        if not search_intelligence_recorded:
            if run.config_snapshot.get("dataforseo_configured"):
                errors.append("DataForSEO was configured but search intelligence output/skip is not recorded")
            else:
                errors.append("DataForSEO skip reason is not recorded in pulling_search_intelligence event")

        return {
            "run_id": run_id,
            "exists": True,
            "valid": not errors,
            "status": run.status,
            "current_stage": run.current_stage,
            "run_json_exists": run_json_exists,
            "events_dir_exists": events_dir_exists,
            "expected_stages": DEFAULT_STAGES,
            "completed_stages": [stage for stage in DEFAULT_STAGES if stage in completed_by_stage],
            "completed_stage_count": len(completed_by_stage),
            "missing_completed_stages": missing_completed,
            "report_json_exists": report_json_exists,
            "report_markdown_exists": report_markdown_exists,
            "summary_has_overall_score": summary_has_overall_score,
            "run_limits_recorded": run_limits_recorded,
            "run_execution_recorded": run_execution_recorded,
            "report_actions_have_evidence_refs": report_actions_have_evidence_refs,
            "overall_score": run.summary.get("overall_score"),
            "search_intelligence_recorded": search_intelligence_recorded,
            "artifact_paths": {
                "run_json": str(run_json),
                "events_dir": str(events_dir),
                "report_json": str(report_json),
                "report_markdown": str(report_md),
            },
            "errors": errors,
        }

    def resume(self, run_id: str, max_pages: int = 5) -> InsightRun:
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"run {run_id} not found")
        if run.status == "completed" and self.validate(run_id)["valid"]:
            return run
        return self.rerun_stage(run_id, self._resume_stage_for(run_id, run), max_pages=max_pages)

    def rerun_stage(self, run_id: str, stage_name: str, max_pages: int = 5) -> InsightRun:
        run = self.repository.get_run(run_id)
        if run is None:
            raise ValueError(f"run {run_id} not found")
        if stage_name not in DEFAULT_STAGES:
            raise ValueError(f"unknown stage {stage_name}")
        result = self._pipeline.rerun_from_stage(run, stage_name, max_pages=max_pages)
        return result.run

    def recover_stale_runs(self, worker_id: str = "reaper", reason: str = "stale lease") -> list[str]:
        recovered: list[str] = []
        now = self._now()
        for run in self.repository.list_runs(limit=10000):
            if run.status not in {"running", "queued"}:
                continue
            if not self._lease_is_expired(run):
                continue
            stage_name = run.current_stage if run.current_stage in DEFAULT_STAGES else "run_execution"
            stage_order = DEFAULT_STAGES.index(stage_name) + 1 if stage_name in DEFAULT_STAGES else None
            message = f"Recovered stale run by {worker_id}: {reason}"
            run.status = "failed"
            run.error_text = message
            run.completed_at = now
            run.updated_at = now
            run.heartbeat_at = run.heartbeat_at or now
            run.lease_owner = None
            run.lease_expires_at = None
            self.repository.update_run(run)
            self.repository.append_stage_event(
                RunStageEvent(
                    insight_run_id=run.id,
                    stage_name=stage_name,
                    stage_order=stage_order,
                    status="failed",
                    started_at=run.started_at,
                    completed_at=now,
                    error_text=message,
                    output_summary={"recovered_by": worker_id, "reason": reason},
                )
            )
            recovered.append(run.id)
        return recovered

    def diff_runs(self, base_run_id: str, comparison_run_id: str) -> dict:
        base = self.repository.get_run(base_run_id)
        comparison = self.repository.get_run(comparison_run_id)
        if base is None:
            raise ValueError(f"run {base_run_id} not found")
        if comparison is None:
            raise ValueError(f"run {comparison_run_id} not found")

        base_report = self.repository.get_report(base_run_id, "v1")
        comparison_report = self.repository.get_report(comparison_run_id, "v1")
        base_actions = [action.get("action", "") for action in (base_report.key_actions if base_report else [])]
        comparison_actions = [
            action.get("action", "") for action in (comparison_report.key_actions if comparison_report else [])
        ]
        base_action_set = set(base_actions)
        comparison_action_set = set(comparison_actions)
        base_score = base.summary.get("overall_score")
        comparison_score = comparison.summary.get("overall_score")
        base_page_count = base.summary.get("page_count")
        comparison_page_count = comparison.summary.get("page_count")
        return {
            "base_run_id": base_run_id,
            "comparison_run_id": comparison_run_id,
            "same_target": base.requested_domain == comparison.requested_domain,
            "base_status": base.status,
            "comparison_status": comparison.status,
            "base_overall_score": base_score,
            "comparison_overall_score": comparison_score,
            "score_delta": self._delta(base_score, comparison_score),
            "base_page_count": base_page_count,
            "comparison_page_count": comparison_page_count,
            "page_count_delta": self._delta(base_page_count, comparison_page_count),
            "recommendation_changes": {
                "added": sorted(comparison_action_set - base_action_set),
                "removed": sorted(base_action_set - comparison_action_set),
                "unchanged_count": len(base_action_set & comparison_action_set),
            },
        }

    def _resume_stage_for(self, run_id: str, run: InsightRun) -> str:
        events = self.repository.list_stage_events(run_id)
        for event in reversed(events):
            if event.status == "failed" and event.stage_name in DEFAULT_STAGES:
                return event.stage_name
        completed = self._completed_stage_events(events)
        for stage in DEFAULT_STAGES:
            if stage not in completed:
                return stage
        if run.current_stage in DEFAULT_STAGES:
            return run.current_stage
        return DEFAULT_STAGES[0]

    @staticmethod
    def _completed_stage_events(events: list[RunStageEvent]) -> dict[str, RunStageEvent]:
        completed: dict[str, RunStageEvent] = {}
        for event in events:
            if event.status == "completed" and event.stage_name in DEFAULT_STAGES:
                completed[event.stage_name] = event
        return completed

    @staticmethod
    def _search_intelligence_recorded(run: InsightRun, event: RunStageEvent | None) -> bool:
        if event is None:
            return False
        summary = event.output_summary
        dataforseo_configured = bool(run.config_snapshot.get("dataforseo_configured"))
        if dataforseo_configured:
            if summary.get("approved") is False:
                return bool(summary.get("skipped_reason"))
            return summary.get("configured") is True or bool(summary.get("payload_keys"))
        return summary.get("configured") is False and bool(summary.get("skipped_reason"))

    @staticmethod
    def _run_limits_recorded(run: InsightRun) -> bool:
        limits = run.input_payload.get("limits")
        budget = run.input_payload.get("budget")
        snapshot_limits = run.config_snapshot.get("run_limits")
        if not isinstance(limits, dict) or not isinstance(budget, dict) or not isinstance(snapshot_limits, dict):
            return False
        return (
            isinstance(limits.get("max_pages"), int)
            and isinstance(limits.get("max_dataforseo_calls"), int)
            and isinstance(budget.get("estimated_paid_api_calls"), int)
            and snapshot_limits.get("max_pages") == limits.get("max_pages")
        )

    def _report_actions_have_evidence_refs(self, run_id: str) -> bool:
        report = self.repository.get_report(run_id, "v1")
        if report is None or not report.key_actions:
            return False
        for action in report.key_actions:
            refs = action.get("evidence_refs")
            if not refs:
                return False
            for ref in refs:
                if not ref.get("artifact_path") or not ref.get("field") or not ref.get("reason"):
                    return False
        return True

    @staticmethod
    def _run_execution_recorded(run: InsightRun) -> bool:
        if not run.started_at or not run.heartbeat_at:
            return False
        if run.status in {"completed", "failed"}:
            return run.lease_owner is None and run.lease_expires_at is None
        return bool(run.lease_owner and run.lease_expires_at)

    @staticmethod
    def _lease_is_expired(run: InsightRun) -> bool:
        if not run.lease_expires_at:
            return False
        expires_at = InsightRunOrchestrator._parse_timestamp(run.lease_expires_at)
        return expires_at is not None and expires_at <= datetime.now(timezone.utc)

    @staticmethod
    def _parse_timestamp(value: str | None) -> datetime | None:
        if not value:
            return None
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _delta(base: object, comparison: object) -> object:
        if isinstance(base, (int, float)) and isinstance(comparison, (int, float)):
            return round(comparison - base, 2)
        return None
