from __future__ import annotations

import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from src.config import AppConfig
from src.models import InsightRun, RunStageEvent, SEOTarget
from src.repositories.base import InsightRepository
from src.services.crawl_discovery_service import CrawlDiscoveryOutput, CrawlDiscoveryService
from src.services.page_analysis_service import PageAnalysisOutput, PageAnalysisService
from src.services.reporting_service import ReportAssemblyService, ScorecardOutput, ScorecardService
from src.services.search_intelligence_service import SearchIntelligenceOutput, SearchIntelligenceService
from src.stage_errors import classify_stage_error, is_retryable


DEFAULT_STAGES = [
    "normalizing_target",
    "discovering_sitemaps",
    "fetching_pages",
    "pulling_search_intelligence",
    "scoring",
    "assembling_report",
]
STAGE_ORDER = {stage: index + 1 for index, stage in enumerate(DEFAULT_STAGES)}
LEASE_SECONDS = 15 * 60


@dataclass(slots=True)
class PipelineResult:
    run: InsightRun
    report_path: str | None


class InsightRunPipeline:
    def __init__(self, repository: InsightRepository, config: AppConfig, artifact_root: str | Path):
        self.repository = repository
        self.config = config
        self.artifact_root = Path(artifact_root)
        self.target_intake = TargetIntakeService(config)
        self.crawl_discovery = CrawlDiscoveryService(timeout_seconds=config.dataforseo.timeout_seconds)
        self.page_analysis = PageAnalysisService(timeout_seconds=config.dataforseo.timeout_seconds)
        self.search_intelligence = SearchIntelligenceService(config, artifact_dir=str(self.artifact_root / "dataforseo_raw"))
        self.scorecards = ScorecardService()
        self.reporting = ReportAssemblyService()

    def run(self, url: str, mode: str = "standard", max_pages: int = 5) -> PipelineResult:
        target = self.target_intake.build_target(url)
        self.repository.upsert_target(target)

        run = InsightRun(
            seo_target_id=target.id,
            requested_url=target.normalized_url,
            requested_domain=target.normalized_domain,
            mode=mode,
            location_code=target.default_location_code,
            language_code=target.default_language_code,
            input_payload={
                "target": {
                    "input_url": url,
                    "normalized_url": target.normalized_url,
                    "normalized_domain": target.normalized_domain,
                },
                "mode": mode,
                "limits": self._run_limits(max_pages),
                "budget": self._budget_snapshot(max_pages),
            },
            config_snapshot={
                "dataforseo_configured": self.config.dataforseo.configured,
                "paid_api_approved": self.config.approval.allow_paid_api_calls,
                "default_location_code": self.config.dataforseo.default_location_code,
                "default_language_code": self.config.dataforseo.default_language_code,
                "run_limits": self._run_limits(max_pages),
            },
        )
        self.repository.create_run(run)
        run.status = "running"
        run.started_at = run.updated_at = self._now()
        self._acquire_lease(run)
        self.repository.update_run(run)
        return self._execute_stages(run, target, mode=mode, max_pages=max_pages, start_stage="normalizing_target")

    def rerun_from_stage(self, run: InsightRun, stage_name: str, max_pages: int = 5) -> PipelineResult:
        if stage_name not in DEFAULT_STAGES:
            raise ValueError(f"unknown stage {stage_name}")

        target = self.target_intake.build_target(run.requested_url)
        # Preserve the original run/target linkage while refreshing normalized target facts.
        target.id = run.seo_target_id
        self.repository.upsert_target(target)

        run.status = "running"
        run.current_stage = stage_name
        run.error_text = None
        run.completed_at = None
        run.attempt_count += 1
        run.input_payload.setdefault("limits", {}).update(self._run_limits(max_pages))
        run.input_payload.setdefault("budget", {}).update(self._budget_snapshot(max_pages))
        run.config_snapshot["run_limits"] = self._run_limits(max_pages)
        run.config_snapshot["paid_api_approved"] = self.config.approval.allow_paid_api_calls
        self._acquire_lease(run)
        run.updated_at = self._now()
        if run.started_at is None:
            run.started_at = run.updated_at
        self.repository.update_run(run)
        return self._execute_stages(run, target, mode=run.mode, max_pages=max_pages, start_stage=stage_name)

    def _execute_stages(
        self,
        run: InsightRun,
        target: SEOTarget,
        *,
        mode: str,
        max_pages: int,
        start_stage: str,
    ) -> PipelineResult:
        start_index = DEFAULT_STAGES.index(start_stage)

        def should_record(stage_name: str) -> bool:
            return DEFAULT_STAGES.index(stage_name) >= start_index

        report_path: str | None = None
        try:
            if should_record("normalizing_target"):
                started = time.perf_counter()
                self._stage_start(run, "normalizing_target", STAGE_ORDER["normalizing_target"], {"url": run.requested_url})
                self._stage_complete(
                    run,
                    "normalizing_target",
                    STAGE_ORDER["normalizing_target"],
                    {
                        "normalized_url": target.normalized_url,
                        "normalized_domain": target.normalized_domain,
                        "artifact_paths": [f"targets/{target.id}.json"],
                    },
                    duration_ms=self._duration_ms(started),
                )

            if should_record("discovering_sitemaps"):
                crawl_output, assets = self._run_stage(
                    run,
                    "discovering_sitemaps",
                    STAGE_ORDER["discovering_sitemaps"],
                    lambda: self._discover_and_save(target, run.id),
                    {"domain": target.normalized_domain},
                    summarize=self._summarize_crawl,
                )
            else:
                crawl_output, assets = self.crawl_discovery.discover(target, run.id)

            urls_to_analyze = [target.normalized_url, *crawl_output.candidate_page_urls][:max_pages]
            if should_record("fetching_pages"):
                page_output = self._run_stage(
                    run,
                    "fetching_pages",
                    STAGE_ORDER["fetching_pages"],
                    lambda: self._analyze_and_save_pages(target, run.id, urls_to_analyze),
                    {"url_count": len(urls_to_analyze)},
                    summarize=self._summarize_pages,
                )
            else:
                page_output = self.page_analysis.analyze_urls(target, run.id, urls_to_analyze)

            if should_record("pulling_search_intelligence"):
                search_output = self._run_stage(
                    run,
                    "pulling_search_intelligence",
                    STAGE_ORDER["pulling_search_intelligence"],
                    lambda: self.search_intelligence.gather(),
                    {},
                    summarize=self._summarize_search,
                )
            else:
                search_output = self.search_intelligence.gather()

            if should_record("scoring"):
                scorecard = self._run_stage(
                    run,
                    "scoring",
                    STAGE_ORDER["scoring"],
                    lambda: self.scorecards.build(crawl_output, page_output, search_output),
                    {},
                    summarize=self._summarize_scorecard,
                )
            else:
                scorecard = self.scorecards.build(crawl_output, page_output, search_output)

            final_summary = {
                "sitemap_count": len(crawl_output.sitemap_urls),
                "page_count": len(page_output.pages),
                "page_error_count": len(page_output.errors),
                "search_configured": search_output.configured,
                "search_approved": search_output.approved,
                "overall_score": scorecard.overall_score,
                "limits": run.input_payload.get("limits", {}),
                "budget": run.input_payload.get("budget", {}),
                "artifact_paths": [
                    f"runs/{run.id}/run.json",
                    f"runs/{run.id}/reports/v1.json",
                    f"runs/{run.id}/reports/v1.md",
                ],
            }
            final_completed_at = self._now()

            if should_record("assembling_report"):
                report = self._run_stage(
                    run,
                    "assembling_report",
                    STAGE_ORDER["assembling_report"],
                    lambda: self._build_and_save_report(
                        target,
                        run,
                        crawl_output,
                        page_output,
                        search_output,
                        scorecard,
                        final_summary=final_summary,
                        completed_at=final_completed_at,
                    ),
                    {},
                    summarize=lambda saved_report: {
                        "report_version": saved_report.report_version,
                        "artifact_paths": [
                            f"reports/{saved_report.report_version}.json",
                            f"reports/{saved_report.report_version}.md",
                        ],
                    },
                )
                report_path = str(self.artifact_root / "runs" / run.id / "reports" / f"{report.report_version}.json")

            run.status = "completed"
            run.current_stage = "completed"
            run.summary = final_summary
            run.completed_at = final_completed_at
            run.updated_at = final_completed_at
            self._release_lease(run)
            self.repository.update_run(run)
            return PipelineResult(run=run, report_path=report_path)
        except Exception as exc:
            run.status = "failed"
            run.current_stage = "failed"
            run.error_text = str(exc)
            run.completed_at = self._now()
            run.updated_at = self._now()
            self._release_lease(run)
            self.repository.update_run(run)
            raise

    def _discover_and_save(self, target: SEOTarget, run_id: str) -> tuple[CrawlDiscoveryOutput, list]:
        crawl_output, assets = self.crawl_discovery.discover(target, run_id)
        for asset in assets:
            self.repository.save_discovered_asset(asset)
        return crawl_output, assets

    def _analyze_and_save_pages(self, target: SEOTarget, run_id: str, urls: list[str]) -> PageAnalysisOutput:
        page_output = self.page_analysis.analyze_urls(target, run_id, urls)
        for page in page_output.pages:
            self.repository.save_page_record(page)
        return page_output

    def _build_and_save_report(
        self,
        target: SEOTarget,
        run: InsightRun,
        crawl_output: CrawlDiscoveryOutput,
        page_output: PageAnalysisOutput,
        search_output: SearchIntelligenceOutput,
        scorecard: ScorecardOutput,
        *,
        final_summary: dict[str, Any],
        completed_at: str,
    ):
        final_run_snapshot = replace(run)
        final_run_snapshot.status = "completed"
        final_run_snapshot.current_stage = "completed"
        final_run_snapshot.summary = final_summary
        final_run_snapshot.completed_at = completed_at
        final_run_snapshot.updated_at = completed_at
        report = self.reporting.build_report(target, final_run_snapshot, crawl_output, page_output, search_output, scorecard)
        return self.repository.save_report(report)

    def _run_stage(
        self,
        run,
        stage_name,
        stage_order,
        work: Callable[[], Any],
        payload: dict[str, Any],
        summarize: Callable[[Any], dict[str, Any]] | None = None,
    ):
        """Execute `work()` with retry. `work` is a zero-arg callable returning a value.

        On fatal error, records a failed stage event and re-raises the classified error.
        """
        policy = self.config.retry
        last_exc = None
        for attempt in range(1, policy.max_attempts + 1):
            stage_started = time.perf_counter()
            self._stage_start(run, stage_name, stage_order, {**payload, "attempt": attempt})
            try:
                result = work()
                output_summary = {"attempt": attempt}
                if summarize is not None:
                    output_summary.update(summarize(result))
                self._stage_complete(
                    run,
                    stage_name,
                    stage_order,
                    output_summary,
                    duration_ms=self._duration_ms(stage_started),
                )
                return result
            except Exception as exc:  # noqa: BLE001 - classified below
                last_exc = classify_stage_error(exc)
                self.repository.append_stage_event(
                    RunStageEvent(
                        insight_run_id=run.id,
                        stage_name=stage_name,
                        stage_order=stage_order,
                        status="failed",
                        started_at=self._now(),
                        completed_at=self._now(),
                        duration_ms=self._duration_ms(stage_started),
                        retry_count=attempt - 1,
                        input_payload={**payload, "attempt": attempt},
                        error_text=str(last_exc),
                    )
                )
                if not is_retryable(last_exc) or attempt >= policy.max_attempts:
                    run.status = "failed"
                    run.current_stage = stage_name
                    run.error_text = str(last_exc)
                    run.completed_at = self._now()
                    self.repository.update_run(run)
                    raise last_exc
                delay = min(policy.base_delay_seconds * attempt, policy.max_delay_seconds)
                time.sleep(delay)
        raise last_exc  # pragma: no cover - defensive

    def _stage_start(self, run: InsightRun, stage_name: str, stage_order: int, payload: dict) -> None:
        run.current_stage = stage_name
        run.updated_at = self._now()
        self._heartbeat(run)
        self.repository.update_run(run)
        self.repository.append_stage_event(
            RunStageEvent(
                insight_run_id=run.id,
                stage_name=stage_name,
                stage_order=stage_order,
                status="started",
                started_at=self._now(),
                input_payload=payload,
            )
        )

    def _stage_complete(
        self,
        run: InsightRun,
        stage_name: str,
        stage_order: int,
        summary: dict,
        duration_ms: int | None = None,
    ) -> None:
        run.current_stage = stage_name
        run.updated_at = self._now()
        self._heartbeat(run)
        self.repository.update_run(run)
        self.repository.append_stage_event(
            RunStageEvent(
                insight_run_id=run.id,
                stage_name=stage_name,
                stage_order=stage_order,
                status="completed",
                completed_at=self._now(),
                duration_ms=duration_ms,
                output_summary=summary,
            )
        )

    @staticmethod
    def _summarize_crawl(result: tuple[CrawlDiscoveryOutput, list]) -> dict[str, Any]:
        crawl_output, assets = result
        return {
            "robots_url": crawl_output.robots_url,
            "robots_status": crawl_output.robots_status,
            "sitemap_count": len(crawl_output.sitemap_urls),
            "candidate_page_count": len(crawl_output.candidate_page_urls),
            "asset_count": len(assets),
            "error_count": len(crawl_output.errors),
            "artifact_paths": [f"assets/{asset.id}.json" for asset in assets],
            "degraded": bool(crawl_output.errors),
        }

    @staticmethod
    def _summarize_pages(page_output: PageAnalysisOutput) -> dict[str, Any]:
        return {
            "pages_saved": len(page_output.pages),
            "error_count": len(page_output.errors),
            "artifact_paths": [f"pages/{page.id}.json" for page in page_output.pages],
            "degraded": bool(page_output.errors),
        }

    @staticmethod
    def _summarize_search(search_output: SearchIntelligenceOutput) -> dict[str, Any]:
        return {
            "configured": search_output.configured,
            "approved": search_output.approved,
            "skipped_reason": search_output.skipped_reason,
            "payload_keys": list(search_output.payload.keys()),
            "degraded": not search_output.configured,
        }

    @staticmethod
    def _summarize_scorecard(scorecard: ScorecardOutput) -> dict[str, Any]:
        return {
            "overall_score": scorecard.overall_score,
            "metrics": scorecard.metrics,
            "scorecard": asdict(scorecard),
        }

    @staticmethod
    def _duration_ms(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))

    def _run_limits(self, max_pages: int) -> dict[str, Any]:
        paid_calls_allowed = self.config.dataforseo.configured and self.config.approval.allow_paid_api_calls
        return {
            "max_pages": max_pages,
            "max_dataforseo_calls": 1 if paid_calls_allowed else 0,
            "network_fetches_allowed": True,
        }

    def _budget_snapshot(self, max_pages: int) -> dict[str, Any]:
        paid_calls = 1 if self.config.dataforseo.configured and self.config.approval.allow_paid_api_calls else 0
        return {
            "estimated_paid_api_calls": paid_calls,
            "paid_api_providers": ["dataforseo"] if paid_calls else [],
            "cost_posture": "low_fixed_cost",
            "page_fetch_limit": max_pages,
        }

    def _acquire_lease(self, run: InsightRun, owner: str = "inline-worker") -> None:
        run.lease_owner = owner
        self._heartbeat(run)

    def _heartbeat(self, run: InsightRun) -> None:
        run.heartbeat_at = self._now()
        run.lease_expires_at = self._seconds_from_now(LEASE_SECONDS)

    @staticmethod
    def _release_lease(run: InsightRun) -> None:
        run.lease_owner = None
        run.lease_expires_at = None

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    @staticmethod
    def _seconds_from_now(seconds: int) -> str:
        return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


from src.services.target_intake_service import TargetIntakeService  # noqa: E402
