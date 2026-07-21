from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.models import InsightReport, InsightRun, PageRecord, SEOTarget
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import SearchIntelligenceOutput


@dataclass(slots=True)
class ScorecardOutput:
    overall_score: float
    sitemap_quality_score: float
    metadata_quality_score: float
    page_coverage_score: float
    search_visibility_score: float
    metrics: dict[str, Any]


class ScorecardService:
    def build(self, crawl: CrawlDiscoveryOutput, pages: PageAnalysisOutput, search: SearchIntelligenceOutput) -> ScorecardOutput:
        page_count = len(pages.pages)
        sitemap_count = len(crawl.sitemap_urls)
        indexable_count = sum(1 for p in pages.pages if p.indexable)
        meta_complete = sum(1 for p in pages.pages if p.title and p.meta_description and p.h1)
        fetch_error_count = len(pages.errors)

        sitemap_quality = min(100.0, 40.0 + sitemap_count * 20.0) if sitemap_count else 20.0
        metadata_quality = round((meta_complete / page_count) * 100.0, 2) if page_count else 0.0
        page_coverage = min(100.0, page_count * 15.0)
        search_visibility = 60.0 if search.configured and search.approved else 10.0
        overall = round((sitemap_quality + metadata_quality + page_coverage + search_visibility) / 4.0, 2)

        return ScorecardOutput(
            overall_score=overall,
            sitemap_quality_score=round(sitemap_quality, 2),
            metadata_quality_score=round(metadata_quality, 2),
            page_coverage_score=round(page_coverage, 2),
            search_visibility_score=round(search_visibility, 2),
            metrics={
                "page_count": page_count,
                "sitemap_count": sitemap_count,
                "indexable_count": indexable_count,
                "meta_complete_count": meta_complete,
                "fetch_error_count": fetch_error_count,
                "search_configured": search.configured,
                "search_approved": search.approved,
            },
        )


class ReportAssemblyService:
    def build_report(
        self,
        target: SEOTarget,
        run: InsightRun,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        scorecard: ScorecardOutput,
    ) -> InsightReport:
        key_actions = self._key_actions(run, crawl, pages, search)
        payload = {
            "target": target.to_dict(),
            "run": run.to_dict(),
            "crawl": {
                "robots_url": crawl.robots_url,
                "robots_status": crawl.robots_status,
                "sitemap_urls": crawl.sitemap_urls,
                "candidate_sitemap_urls": crawl.candidate_sitemap_urls,
                "errors": crawl.errors,
            },
            "pages": [page.to_dict() for page in pages.pages],
            "page_errors": pages.errors,
            "search": {
                "configured": search.configured,
                "approved": search.approved,
                "skipped_reason": search.skipped_reason,
                "payload": search.payload,
            },
            "scorecard": asdict(scorecard),
            "key_actions": key_actions,
        }
        markdown = self._markdown(target, scorecard, key_actions)
        return InsightReport(
            insight_run_id=run.id,
            seo_target_id=target.id,
            report_status="complete",
            headline=f"SEO Insight Run for {target.normalized_domain}",
            executive_summary=f"Generated a scaffolded SEO insight run for {target.normalized_domain} with {len(pages.pages)} analyzed pages.",
            key_actions=key_actions,
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
        )

    @staticmethod
    def _key_actions(
        run: InsightRun,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
    ) -> list[dict[str, Any]]:
        actions: list[dict[str, Any]] = []
        if not crawl.sitemap_urls:
            actions.append(
                {
                    "priority": "high",
                    "action": "Add or expose a sitemap.xml and reference it in robots.txt.",
                    "source_stage": "discovering_sitemaps",
                    "confidence": "high",
                    "evidence_refs": [
                        {
                            "artifact_type": "report",
                            "artifact_path": "reports/v1.json",
                            "field": "report_payload.crawl.sitemap_urls",
                            "reason": "No sitemap URLs were validated for this run.",
                            "observed": [],
                        }
                    ],
                }
            )
        missing_meta_pages = [page for page in pages.pages if page.meta_description is None]
        if missing_meta_pages:
            actions.append(
                {
                    "priority": "medium",
                    "action": "Fill missing meta descriptions on key indexable pages.",
                    "source_stage": "fetching_pages",
                    "confidence": "high",
                    "evidence_refs": [
                        {
                            "artifact_type": "page_record",
                            "artifact_path": f"pages/{page.id}.json",
                            "field": "meta_description",
                            "reason": "Page record has no meta description.",
                            "url": page.url,
                            "observed": page.meta_description,
                        }
                        for page in missing_meta_pages[:5]
                    ],
                }
            )
        missing_h1_pages = [page for page in pages.pages if page.h1 is None]
        if missing_h1_pages:
            actions.append(
                {
                    "priority": "medium",
                    "action": "Ensure each important page has a clear H1.",
                    "source_stage": "fetching_pages",
                    "confidence": "high",
                    "evidence_refs": [
                        {
                            "artifact_type": "page_record",
                            "artifact_path": f"pages/{page.id}.json",
                            "field": "h1",
                            "reason": "Page record has no H1.",
                            "url": page.url,
                            "observed": page.h1,
                        }
                        for page in missing_h1_pages[:5]
                    ],
                }
            )
        if search.configured and not search.approved:
            actions.append(
                {
                    "priority": "medium",
                    "action": "Approve paid DataForSEO enrichment when operator budget allows.",
                    "source_stage": "pulling_search_intelligence",
                    "confidence": "high",
                    "evidence_refs": [
                        {
                            "artifact_type": "run",
                            "artifact_path": "run.json",
                            "field": "config_snapshot.paid_api_approved",
                            "reason": search.skipped_reason or "Paid enrichment was configured but not approved for this run.",
                            "observed": run.config_snapshot.get("paid_api_approved"),
                        }
                    ],
                }
            )
        elif not search.configured:
            actions.append(
                {
                    "priority": "medium",
                    "action": "Configure DataForSEO credentials to enable keyword and SERP enrichment.",
                    "source_stage": "pulling_search_intelligence",
                    "confidence": "high",
                    "evidence_refs": [
                        {
                            "artifact_type": "run",
                            "artifact_path": "run.json",
                            "field": "config_snapshot.dataforseo_configured",
                            "reason": search.skipped_reason or "Search intelligence stage was skipped because DataForSEO is not configured.",
                            "observed": run.config_snapshot.get("dataforseo_configured"),
                        }
                    ],
                }
            )
        if not actions:
            actions.append(
                {
                    "priority": "low",
                    "action": "Expand analysis depth to more URLs and add ranking enrichment.",
                    "source_stage": "scoring",
                    "confidence": "medium",
                    "evidence_refs": [
                        {
                            "artifact_type": "run",
                            "artifact_path": "run.json",
                            "field": "summary.page_count",
                            "reason": "Current run completed cleanly; next action is to broaden collection depth.",
                            "observed": run.summary.get("page_count"),
                        }
                    ],
                }
            )
        return actions

    @staticmethod
    def _markdown(target: SEOTarget, scorecard: ScorecardOutput, key_actions: list[dict[str, Any]]) -> str:
        lines = [
            f"# SEO Insight Run — {target.normalized_domain}",
            "",
            f"- Overall score: {scorecard.overall_score}",
            f"- Sitemap quality: {scorecard.sitemap_quality_score}",
            f"- Metadata quality: {scorecard.metadata_quality_score}",
            f"- Page coverage: {scorecard.page_coverage_score}",
            f"- Search visibility readiness: {scorecard.search_visibility_score}",
            "",
            "## Recommended next actions",
        ]
        for action in key_actions:
            lines.append(f"- [{action['priority']}] {action['action']}")
            for ref in action.get("evidence_refs", [])[:3]:
                lines.append(f"  - Evidence: `{ref['artifact_path']}` → `{ref['field']}` ({ref['reason']})")
        return "\n".join(lines) + "\n"
