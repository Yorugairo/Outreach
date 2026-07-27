from __future__ import annotations

import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from src.config import AppConfig
from src.models import (
    DiscoveredAsset,
    InsightRun,
    PageRecord,
    ProductSurfaceResult,
    RunStageEvent,
    SEOTarget,
    StageCheckpoint,
    new_id,
)
from src.repositories.base import InsightRepository
from src.services.ai_readiness_service import (
    AIReadinessOutput,
    AIReadinessV3Service,
)
from src.services.crawl_discovery_service import CrawlDiscoveryOutput, CrawlDiscoveryService
from src.services.conversion_readiness_service import ConversionReadinessService
from src.services.page_analysis_service import PageAnalysisOutput, PageAnalysisService
from src.services.reporting_service import ReportAssemblyService, ScorecardOutput, ScorecardService
from src.services.search_intelligence_service import (
    SearchIntelligenceOutput,
    SearchIntelligenceService,
    TargetContext,
)
from src.stage_errors import classify_stage_error, is_retryable
from src.services.technical_seo_health_service import TechnicalSEOHealthService


LEGACY_STAGES = [
    "normalizing_target",
    "discovering_sitemaps",
    "fetching_pages",
    "pulling_search_intelligence",
    "scoring",
    "assembling_report",
]
V3_STAGES = [*LEGACY_STAGES[:-1], "scoring_ai_readiness", LEGACY_STAGES[-1]]
V4_STAGES = [
    *LEGACY_STAGES[:-1],
    "scoring_technical_health",
    "scoring_ai_readiness",
    LEGACY_STAGES[-1],
]
DEFAULT_STAGES = [
    *V4_STAGES[:-1],
    "scoring_conversion_readiness",
    LEGACY_STAGES[-1],
]
PIPELINE_CONTRACT_VERSION = 5
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
        self.technical_health = TechnicalSEOHealthService()
        self.ai_readiness = AIReadinessV3Service()
        self.conversion_readiness = ConversionReadinessService()
        self.reporting = ReportAssemblyService()

    def run(self, url: str, mode: str = "standard", max_pages: int = 100) -> PipelineResult:
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
                "pipeline_contract_version": PIPELINE_CONTRACT_VERSION,
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

    def rerun_from_stage(self, run: InsightRun, stage_name: str, max_pages: int = 100) -> PipelineResult:
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
        source_attempt_id = run.attempt_id
        run.attempt_count += 1
        run.attempt_id = new_id()
        self._inherit_checkpoints(run.id, source_attempt_id, run.attempt_id, stage_name)
        run.input_payload.setdefault("limits", {}).update(self._run_limits(max_pages))
        run.input_payload.setdefault("budget", {}).update(self._budget_snapshot(max_pages))
        # A rerun is a new attempt executed by the current pipeline. Preserve the
        # historical events/checkpoints while making the active attempt validate
        # against the contract that actually produced it.
        run.config_snapshot["pipeline_contract_version"] = PIPELINE_CONTRACT_VERSION
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
        target_context = TargetContext(
            primary_url=run.requested_url,
            target_domain=run.requested_domain,
            language_code=run.language_code,
            device=run.device,
            location_code=run.location_code,
            market=target.country_code,
        )

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
            else:
                self._stage_complete(
                    run,
                    "normalizing_target",
                    STAGE_ORDER["normalizing_target"],
                    {
                        "normalized_url": target.normalized_url,
                        "normalized_domain": target.normalized_domain,
                        "inherited": True,
                    },
                    duration_ms=0,
                )

            if should_record("discovering_sitemaps"):
                crawl_output, assets = self._run_stage(
                    run,
                    "discovering_sitemaps",
                    STAGE_ORDER["discovering_sitemaps"],
                    lambda: self._discover_and_save(target, run.id, run.attempt_id),
                    {"domain": target.normalized_domain},
                    summarize=self._summarize_crawl,
                )
            else:
                crawl_output, assets = self._load_crawl_checkpoint(run)
                self._record_inherited_stage(run, "discovering_sitemaps", self._summarize_crawl((crawl_output, assets)))

            if should_record("fetching_pages"):
                page_output = self._run_stage(
                    run,
                    "fetching_pages",
                    STAGE_ORDER["fetching_pages"],
                    lambda: self._analyze_and_save_pages(
                        target,
                        run.id,
                        crawl_output.candidate_page_urls,
                        run.attempt_id,
                        max_pages=max_pages,
                    ),
                    {"page_limit": max_pages},
                    summarize=self._summarize_pages,
                )
            else:
                page_output = self._load_page_checkpoint(run)
                self._record_inherited_stage(run, "fetching_pages", self._summarize_pages(page_output))

            target_context = replace(
                target_context,
                entity_name=self._entity_name(page_output),
                entity_name_source="page_evidence" if self._entity_name(page_output) else None,
            )
            if should_record("pulling_search_intelligence"):
                search_output = self._run_stage(
                    run,
                    "pulling_search_intelligence",
                    STAGE_ORDER["pulling_search_intelligence"],
                    lambda: self.search_intelligence.gather(target_context),
                    {},
                    summarize=lambda output: self._summarize_search(output, target_context),
                )
            else:
                search_output = self._load_search_checkpoint(run)
                self._record_inherited_stage(
                    run,
                    "pulling_search_intelligence",
                    self._summarize_search(search_output, target_context),
                )

            if should_record("scoring"):
                scorecard = self._run_stage(
                    run,
                    "scoring",
                    STAGE_ORDER["scoring"],
                    lambda: self.scorecards.build(
                        crawl_output, page_output, search_output, target_context=target_context
                    ),
                    {},
                    summarize=self._summarize_scorecard,
                )
            else:
                scorecard = self._load_scorecard_checkpoint(run)
                self._record_inherited_stage(run, "scoring", self._summarize_scorecard(scorecard))

            if should_record("scoring_technical_health"):
                technical_health = self._run_stage(
                    run,
                    "scoring_technical_health",
                    STAGE_ORDER["scoring_technical_health"],
                    lambda: self.technical_health.build(
                        crawl_output,
                        page_output,
                        page_limit=max_pages,
                        attempt_id=run.attempt_id,
                    ),
                    {},
                    summarize=self._summarize_technical_health,
                )
            else:
                technical_health = self._load_technical_health_checkpoint(run)
                self._record_inherited_stage(
                    run,
                    "scoring_technical_health",
                    self._summarize_technical_health(technical_health),
                )

            if should_record("scoring_ai_readiness"):
                ai_readiness = self._run_stage(
                    run,
                    "scoring_ai_readiness",
                    STAGE_ORDER["scoring_ai_readiness"],
                    lambda: self.ai_readiness.build(
                        crawl_output,
                        page_output,
                        search_output,
                        page_limit=max_pages,
                        attempt_id=run.attempt_id,
                    ),
                    {},
                    summarize=self._summarize_ai_readiness,
                )
            else:
                checkpoint = self.repository.get_checkpoint(
                    run.id,
                    run.attempt_id,
                    "scoring_ai_readiness",
                )
                if checkpoint is None:
                    ai_readiness = self._run_stage(
                        run,
                        "scoring_ai_readiness",
                        STAGE_ORDER["scoring_ai_readiness"],
                        lambda: self.ai_readiness.build(
                            crawl_output,
                            page_output,
                            search_output,
                            page_limit=max_pages,
                            attempt_id=run.attempt_id,
                        ),
                        {"compatibility_upgrade": True},
                        summarize=self._summarize_ai_readiness,
                    )
                else:
                    ai_readiness = self._load_ai_readiness_checkpoint(run)
                    self._record_inherited_stage(
                        run,
                        "scoring_ai_readiness",
                        self._summarize_ai_readiness(ai_readiness),
                    )

            vertical_id = self._vertical_id_for_domain(target.normalized_domain)
            if should_record("scoring_conversion_readiness"):
                conversion_readiness = self._run_stage(
                    run,
                    "scoring_conversion_readiness",
                    STAGE_ORDER["scoring_conversion_readiness"],
                    lambda: self.conversion_readiness.build(
                        page_output,
                        vertical_id,
                        page_limit=max_pages,
                    ),
                    {"vertical_id": vertical_id},
                    summarize=self._summarize_conversion_readiness,
                )
            else:
                checkpoint = self.repository.get_checkpoint(
                    run.id,
                    run.attempt_id,
                    "scoring_conversion_readiness",
                )
                if checkpoint is None:
                    conversion_readiness = self._run_stage(
                        run,
                        "scoring_conversion_readiness",
                        STAGE_ORDER["scoring_conversion_readiness"],
                        lambda: self.conversion_readiness.build(
                            page_output,
                            vertical_id,
                            page_limit=max_pages,
                        ),
                        {
                            "vertical_id": vertical_id,
                            "compatibility_upgrade": True,
                        },
                        summarize=self._summarize_conversion_readiness,
                    )
                else:
                    conversion_readiness = (
                        self._load_conversion_readiness_checkpoint(run)
                    )
                    self._record_inherited_stage(
                        run,
                        "scoring_conversion_readiness",
                        self._summarize_conversion_readiness(
                            conversion_readiness
                        ),
                    )

            final_summary = {
                "sitemap_count": len(crawl_output.sitemap_urls),
                "page_count": len(page_output.pages),
                "page_error_count": len(page_output.errors),
                "search_configured": search_output.configured,
                "search_approved": search_output.approved,
                "overall_score": scorecard.overall_score,
                "technical_seo_health_score": technical_health.score,
                "technical_seo_health_completeness": technical_health.completeness_percent,
                "technical_seo_health_status": technical_health.status,
                "technical_seo_health_version": technical_health.version,
                "evidence_confidence": technical_health.evidence_confidence,
                "evidence_confidence_version": technical_health.metrics.get(
                    "evidence_confidence_version"
                ),
                "ai_readiness_score": ai_readiness.score,
                "ai_readiness_completeness": ai_readiness.completeness_percent,
                "ai_readiness_status": ai_readiness.status,
                "ai_readiness_version": ai_readiness.score_version,
                "conversion_readiness_score": conversion_readiness.score,
                "conversion_readiness_completeness": (
                    conversion_readiness.completeness_percent
                ),
                "conversion_readiness_status": conversion_readiness.status,
                "conversion_readiness_version": conversion_readiness.version,
                "score_completeness_percent": scorecard.completeness_percent,
                "scored_dimensions": scorecard.scored_dimensions,
                "score_dimension_status": scorecard.dimension_status,
                "score_warnings": scorecard.warnings,
                "limits": run.input_payload.get("limits", {}),
                "budget": run.input_payload.get("budget", {}),
                "report_versions": [
                    "v1",
                    "v2",
                    "seo-health-v2",
                    "ai-v3",
                    "conversion-v1",
                ],
                "primary_report_version": "v2",
                "artifact_paths": [
                    f"runs/{run.id}/run.json",
                    f"runs/{run.id}/reports/v1.json",
                    f"runs/{run.id}/reports/v1.md",
                    f"runs/{run.id}/reports/v2.json",
                    f"runs/{run.id}/reports/v2.md",
                    f"runs/{run.id}/reports/seo-health-v2.json",
                    f"runs/{run.id}/reports/seo-health-v2.md",
                    f"runs/{run.id}/reports/ai-v3.json",
                    f"runs/{run.id}/reports/ai-v3.md",
                    f"runs/{run.id}/reports/conversion-v1.json",
                    f"runs/{run.id}/reports/conversion-v1.md",
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
                        technical_health,
                        ai_readiness,
                        conversion_readiness,
                        target_context=target_context,
                        final_summary=final_summary,
                        completed_at=final_completed_at,
                    ),
                    {},
                    summarize=lambda saved_report: {
                        "report_version": saved_report.report_version,
                        "report_versions": [
                            "v1",
                            "v2",
                            "seo-health-v2",
                            "ai-v3",
                            "conversion-v1",
                        ],
                        "primary_report_version": "v2",
                        "artifact_paths": [
                            "reports/v1.json",
                            "reports/v1.md",
                            "reports/v2.json",
                            "reports/v2.md",
                            "reports/seo-health-v2.json",
                            "reports/seo-health-v2.md",
                            "reports/ai-v3.json",
                            "reports/ai-v3.md",
                            "reports/conversion-v1.json",
                            "reports/conversion-v1.md",
                        ],
                    },
                )
                report_path = (self.artifact_root / "runs" / run.id / "reports" / "v1.json").as_posix()

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

    def _discover_and_save(
        self,
        target: SEOTarget,
        run_id: str,
        attempt_id: str,
    ) -> tuple[CrawlDiscoveryOutput, list]:
        crawl_output, assets = self.crawl_discovery.discover(target, run_id)
        for asset in assets:
            asset.attempt_id = attempt_id
            self.repository.save_discovered_asset(asset)
        return crawl_output, assets

    def _analyze_and_save_pages(
        self,
        target: SEOTarget,
        run_id: str,
        urls: list[str],
        attempt_id: str,
        *,
        max_pages: int,
    ) -> PageAnalysisOutput:
        page_output = self.page_analysis.crawl_site(
            target,
            run_id,
            urls,
            max_pages=max_pages,
        )
        for page in page_output.pages:
            page.attempt_id = attempt_id
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
        technical_health: ProductSurfaceResult,
        ai_readiness: AIReadinessOutput,
        conversion_readiness: ProductSurfaceResult,
        *,
        target_context: TargetContext,
        final_summary: dict[str, Any],
        completed_at: str,
    ):
        final_run_snapshot = replace(run)
        final_run_snapshot.status = "completed"
        final_run_snapshot.current_stage = "completed"
        final_run_snapshot.summary = final_summary
        final_run_snapshot.completed_at = completed_at
        final_run_snapshot.updated_at = completed_at
        report_v1 = self.reporting.build_report(
            target, final_run_snapshot, crawl_output, page_output, search_output, scorecard
        )
        self.repository.save_report(report_v1)
        completed_events: dict[str, str] = {}
        completed_event_records = sorted(
            (
                event
                for event in self.repository.list_stage_events(run.id)
                if event.status == "completed"
                and event.attempt_id == run.attempt_id
                and event.artifact_path
            ),
            key=lambda event: (event.completed_at or "", event.created_at, event.id),
        )
        for event in completed_event_records:
            completed_events[event.stage_name] = event.artifact_path
        report_v2 = self.reporting.build_report_v2(
            target,
            final_run_snapshot,
            crawl_output,
            page_output,
            search_output,
            scorecard,
            target_context=target_context,
            stage_artifacts=completed_events,
        )
        self._assert_report_evidence_exists(run.id, report_v2.report_payload.get("findings", []))
        technical_report = self.reporting.build_technical_health_report(
            target,
            final_run_snapshot,
            technical_health,
        )
        self.repository.save_report(technical_report)
        ai_report = self.reporting.build_ai_report(target, final_run_snapshot, ai_readiness)
        self.repository.save_report(ai_report)
        conversion_report = self.reporting.build_conversion_readiness_report(
            target,
            final_run_snapshot,
            conversion_readiness,
        )
        self.repository.save_report(conversion_report)
        return self.repository.save_report(report_v2)

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
                self._save_checkpoint(run, stage_name, result)
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
                    self._new_stage_event(
                        insight_run_id=run.id,
                        stage_name=stage_name,
                        stage_order=stage_order,
                        status="failed",
                        attempt_id=run.attempt_id,
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

    def _save_checkpoint(self, run: InsightRun, stage_name: str, result: Any) -> None:
        payload_type = {
            "discovering_sitemaps": "crawl_discovery",
            "fetching_pages": "page_analysis",
            "pulling_search_intelligence": "search_intelligence",
            "scoring": "scorecard",
            "scoring_technical_health": "technical_seo_health",
            "scoring_ai_readiness": "ai_readiness",
            "scoring_conversion_readiness": "conversion_readiness",
        }.get(stage_name)
        if payload_type is None:
            return
        checkpoint = StageCheckpoint.create(
            insight_run_id=run.id,
            attempt_id=run.attempt_id,
            stage_name=stage_name,
            payload_type=payload_type,
            payload=self._checkpoint_payload(stage_name, result),
        )
        self.repository.save_checkpoint(checkpoint)

    @staticmethod
    def _checkpoint_payload(stage_name: str, result: Any) -> dict[str, Any]:
        if stage_name == "discovering_sitemaps":
            crawl_output, assets = result
            return {"crawl": asdict(crawl_output), "assets": [asset.to_dict() for asset in assets]}
        if stage_name in {
            "fetching_pages",
            "pulling_search_intelligence",
            "scoring",
            "scoring_technical_health",
            "scoring_ai_readiness",
            "scoring_conversion_readiness",
        }:
            return asdict(result)
        raise ValueError(f"stage does not have a checkpoint contract: {stage_name}")

    def _inherit_checkpoints(
        self,
        run_id: str,
        source_attempt_id: str,
        target_attempt_id: str,
        start_stage: str,
    ) -> None:
        start_index = DEFAULT_STAGES.index(start_stage)
        for stage_name in DEFAULT_STAGES[:start_index]:
            source = self.repository.get_checkpoint(run_id, source_attempt_id, stage_name)
            if source is None:
                continue
            self.repository.save_checkpoint(
                StageCheckpoint.create(
                    insight_run_id=run_id,
                    attempt_id=target_attempt_id,
                    stage_name=stage_name,
                    payload_type=source.payload_type,
                    payload=source.payload,
                )
            )

    def _load_checkpoint(self, run: InsightRun, stage_name: str, payload_type: str) -> StageCheckpoint:
        checkpoint = self.repository.get_checkpoint(run.id, run.attempt_id, stage_name)
        if checkpoint is None:
            raise ValueError(f"missing checkpoint for {stage_name} in attempt {run.attempt_id}")
        if checkpoint.payload_type != payload_type:
            raise ValueError(
                f"checkpoint type mismatch for {stage_name}: expected {payload_type}, got {checkpoint.payload_type}"
            )
        return checkpoint

    def _load_crawl_checkpoint(self, run: InsightRun) -> tuple[CrawlDiscoveryOutput, list[DiscoveredAsset]]:
        checkpoint = self._load_checkpoint(run, "discovering_sitemaps", "crawl_discovery")
        crawl_output = CrawlDiscoveryOutput(**checkpoint.payload["crawl"])
        assets = [DiscoveredAsset(**payload) for payload in checkpoint.payload.get("assets", [])]
        for asset in assets:
            asset.attempt_id = run.attempt_id
            self.repository.save_discovered_asset(asset)
        return crawl_output, assets

    def _load_page_checkpoint(self, run: InsightRun) -> PageAnalysisOutput:
        checkpoint = self._load_checkpoint(run, "fetching_pages", "page_analysis")
        output = PageAnalysisOutput(**checkpoint.payload)
        for page in output.pages:
            page = page if isinstance(page, PageRecord) else PageRecord(**page)
            page.attempt_id = run.attempt_id
            self.repository.save_page_record(page)
        output.pages = [page if isinstance(page, PageRecord) else PageRecord(**page) for page in output.pages]
        return output

    def _load_search_checkpoint(self, run: InsightRun) -> SearchIntelligenceOutput:
        checkpoint = self._load_checkpoint(run, "pulling_search_intelligence", "search_intelligence")
        return SearchIntelligenceOutput(**checkpoint.payload)

    def _load_scorecard_checkpoint(self, run: InsightRun) -> ScorecardOutput:
        checkpoint = self._load_checkpoint(run, "scoring", "scorecard")
        return ScorecardOutput(**checkpoint.payload)

    def _load_technical_health_checkpoint(self, run: InsightRun) -> ProductSurfaceResult:
        checkpoint = self._load_checkpoint(
            run,
            "scoring_technical_health",
            "technical_seo_health",
        )
        return ProductSurfaceResult(**checkpoint.payload)

    def _load_ai_readiness_checkpoint(self, run: InsightRun) -> AIReadinessOutput:
        checkpoint = self._load_checkpoint(run, "scoring_ai_readiness", "ai_readiness")
        return AIReadinessOutput(**checkpoint.payload)

    def _load_conversion_readiness_checkpoint(
        self,
        run: InsightRun,
    ) -> ProductSurfaceResult:
        checkpoint = self._load_checkpoint(
            run,
            "scoring_conversion_readiness",
            "conversion_readiness",
        )
        return ProductSurfaceResult(**checkpoint.payload)

    def _record_inherited_stage(self, run: InsightRun, stage_name: str, summary: dict[str, Any]) -> None:
        checkpoint = self.repository.get_checkpoint(run.id, run.attempt_id, stage_name)
        if checkpoint is None:
            raise ValueError(f"cannot inherit missing checkpoint for {stage_name}")
        inherited_summary = {
            **summary,
            "inherited": True,
            "checkpoint_schema_version": checkpoint.schema_version,
            "checkpoint_sha256": checkpoint.content_sha256,
        }
        self._stage_complete(
            run,
            stage_name,
            STAGE_ORDER[stage_name],
            inherited_summary,
            duration_ms=0,
        )

    def _stage_start(self, run: InsightRun, stage_name: str, stage_order: int, payload: dict) -> None:
        run.current_stage = stage_name
        run.updated_at = self._now()
        self._heartbeat(run)
        self.repository.update_run(run)
        self.repository.append_stage_event(
            self._new_stage_event(
                insight_run_id=run.id,
                stage_name=stage_name,
                stage_order=stage_order,
                status="started",
                attempt_id=run.attempt_id,
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
            self._new_stage_event(
                insight_run_id=run.id,
                stage_name=stage_name,
                stage_order=stage_order,
                status="completed",
                attempt_id=run.attempt_id,
                completed_at=self._now(),
                duration_ms=duration_ms,
                output_summary=summary,
            )
        )

    @staticmethod
    def _new_stage_event(**kwargs: Any) -> RunStageEvent:
        """Create a pipeline event with a stable, independently addressable artifact path."""
        event = RunStageEvent(**kwargs)
        event.artifact_path = f"events/{event.id}.json"
        return event

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
            "sitemap_urls": sorted(set(crawl_output.sitemap_urls))[:100],
            "candidate_sitemap_urls": sorted(set(crawl_output.candidate_sitemap_urls))[:100],
            "candidate_page_urls": sorted(set(crawl_output.candidate_page_urls))[:100],
            "robots_access": crawl_output.robots_access,
            "errors": sorted(crawl_output.errors)[:100],
            "artifact_paths": [f"assets/{asset.id}.json" for asset in assets],
            "degraded": bool(crawl_output.errors),
        }

    @staticmethod
    def _summarize_pages(page_output: PageAnalysisOutput) -> dict[str, Any]:
        ordered_errors = sorted(
            page_output.errors,
            key=lambda item: (str(item.get("url", "")), str(item.get("error", ""))),
        )
        return {
            "pages_saved": len(page_output.pages),
            "pages_discovered": page_output.discovered_count,
            "pages_attempted": page_output.attempted_count,
            "capped": page_output.capped,
            "error_count": len(page_output.errors),
            "errors": ordered_errors[:100],
            "artifact_paths": [f"pages/{page.id}.json" for page in page_output.pages],
            "degraded": bool(page_output.errors),
        }

    @staticmethod
    def _summarize_search(
        search_output: SearchIntelligenceOutput,
        target_context: TargetContext,
    ) -> dict[str, Any]:
        return {
            "configured": search_output.configured,
            "approved": search_output.approved,
            "skipped": bool(search_output.skipped_reason),
            "skipped_reason": search_output.skipped_reason,
            "payload_keys": sorted(search_output.payload)[:100],
            "requested_context": target_context.to_dict(),
            "degraded": not search_output.configured,
        }

    def _assert_report_evidence_exists(self, run_id: str, findings: list[dict[str, Any]]) -> None:
        run_dir = (self.artifact_root / "runs" / run_id).resolve()
        for finding in findings:
            for ref in finding.get("evidence_refs", []):
                relative = Path(str(ref.get("artifact_path", "")))
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("v2 evidence path must be safe and run-relative")
                resolved = (run_dir / relative).resolve()
                try:
                    resolved.relative_to(run_dir)
                except ValueError as exc:
                    raise ValueError("v2 evidence path escapes its run") from exc
                if resolved.suffix.casefold() != ".json" or not resolved.is_file():
                    raise FileNotFoundError(
                        f"v2 evidence artifact is missing or not JSON: {relative.as_posix()}"
                    )

    @staticmethod
    def _summarize_scorecard(scorecard: ScorecardOutput) -> dict[str, Any]:
        return {
            "overall_score": scorecard.overall_score,
            "metrics": scorecard.metrics,
            "scorecard": asdict(scorecard),
        }

    @staticmethod
    def _summarize_technical_health(output: ProductSurfaceResult) -> dict[str, Any]:
        return {
            "technical_seo_health_score": output.score,
            "technical_seo_health_completeness": output.completeness_percent,
            "technical_seo_health_status": output.status,
            "technical_seo_health_version": output.version,
            "evidence_confidence": output.evidence_confidence,
            "families": output.families,
            "affected_check_count": sum(
                1 for check in output.checks if check.get("status") == "failed"
            ),
        }

    @staticmethod
    def _summarize_ai_readiness(output: AIReadinessOutput) -> dict[str, Any]:
        return {
            "ai_readiness_score": output.score,
            "ai_readiness_completeness": output.completeness_percent,
            "ai_readiness_status": output.status,
            "ai_readiness_version": output.score_version,
            "dimensions": output.dimensions,
            "inventory": output.inventory,
            "broken_link_count": len(output.broken_links),
        }

    @staticmethod
    def _summarize_conversion_readiness(
        output: ProductSurfaceResult,
    ) -> dict[str, Any]:
        return {
            "conversion_readiness_score": output.score,
            "conversion_readiness_completeness": output.completeness_percent,
            "conversion_readiness_status": output.status,
            "conversion_readiness_version": output.version,
            "vertical_id": output.metrics.get("vertical_id"),
            "affected_check_count": sum(
                1
                for check in output.checks
                if check.get("status") == "failed"
            ),
        }

    def _vertical_id_for_domain(self, normalized_domain: str) -> str | None:
        prospects = self.repository.list_prospects(limit=10_000)
        matches = [
            prospect
            for prospect in prospects
            if prospect.normalized_domain.casefold()
            == normalized_domain.casefold().removeprefix("www.")
            and prospect.qualification_status in {"qualified", "needs_review"}
        ]
        matches.sort(key=lambda prospect: (prospect.updated_at, prospect.id), reverse=True)
        return matches[0].vertical_id if matches else None

    @staticmethod
    def _entity_name(page_output: PageAnalysisOutput) -> str | None:
        ordered = sorted(
            page_output.pages,
            key=lambda page: (
                page.page_class != "homepage",
                page.page_class not in {"contact_about", "service", "location"},
                page.url,
            ),
        )
        for page in ordered:
            names = page.ai_evidence.get("entity_names", [])
            if isinstance(names, list):
                for name in names:
                    value = str(name).strip()
                    if value:
                        return value[:200]
        return None

    @staticmethod
    def _duration_ms(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))

    def _run_limits(self, max_pages: int) -> dict[str, Any]:
        paid_calls_allowed = self.config.dataforseo.configured and self.config.approval.allow_paid_api_calls
        return {
            "max_pages": max_pages,
            "max_dataforseo_calls": self.config.dataforseo.max_paid_calls if paid_calls_allowed else 0,
            "network_fetches_allowed": True,
        }

    def _budget_snapshot(self, max_pages: int) -> dict[str, Any]:
        paid_calls = 1 if self.config.dataforseo.configured and self.config.approval.allow_paid_api_calls else 0
        paid_calls = self.config.dataforseo.max_paid_calls if paid_calls else 0
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
