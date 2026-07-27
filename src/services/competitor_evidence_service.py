"""Bounded, host-isolated competitor evidence collection."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Protocol
from urllib.parse import urlsplit

from src.fetchers.sitemap_fetcher import SitemapFetcher
from src.models import MarketEvidenceRun, SEOTarget, utc_now_iso
from src.repositories.base import InsightRepository
from src.services.gap_analysis_service import GapAnalysisService
from src.services.page_analysis_service import PageAnalysisService
from src.services.screenshot_service import ScreenshotCaptureService


class AuthorityProvider(Protocol):
    def collect_offsite_authority(self, target_domain: str) -> dict[str, Any]: ...


class CompetitorEvidenceService:
    def __init__(
        self,
        repository: InsightRepository,
        *,
        page_analysis_factory: Callable[[], PageAnalysisService] | None = None,
        sitemap_factory: Callable[[], SitemapFetcher] | None = None,
        authority_provider_factory: Callable[[], AuthorityProvider] | None = None,
        screenshot_service: ScreenshotCaptureService | None = None,
    ) -> None:
        self.repository = repository
        self.page_analysis_factory = page_analysis_factory or PageAnalysisService
        self.sitemap_factory = sitemap_factory or SitemapFetcher
        self.authority_provider_factory = authority_provider_factory
        self.screenshot_service = screenshot_service or ScreenshotCaptureService(repository)
        self.gap_service = GapAnalysisService()

    def enrich(
        self,
        market_run_id: str,
        *,
        capture_screenshots: bool = True,
        target_program_url: str | None = None,
    ) -> MarketEvidenceRun:
        market_run = self.repository.get_market_evidence_run(market_run_id)
        if market_run is None:
            raise ValueError(f"market evidence run not found: {market_run_id}")
        if market_run.state != "enriching" or not market_run.approved_competitors:
            raise ValueError("competitor enrichment requires an approved competitor set")
        if market_run.competitor_evidence:
            raise ValueError("competitor evidence has already been collected for this immutable approval set")

        authority_provider = self.authority_provider_factory() if self.authority_provider_factory else None
        market_run.provider_call_cap += min(3, len(market_run.approved_competitors)) if authority_provider else 0
        evidence: list[dict[str, Any]] = []
        for competitor in market_run.approved_competitors[:3]:
            domain = self._normalize_domain(str(competitor.get("domain") or ""))
            if not domain:
                market_run.evidence_limits.append({
                    "kind": "competitor_missing_domain",
                    "candidate_id": competitor.get("candidate_id"),
                    "message": "The approved Maps identity had no validated website domain, so no competitor crawl was attempted.",
                })
                continue
            competitor_evidence = self._crawl_competitor(market_run, competitor, domain)
            if authority_provider is not None:
                authority = self._collect_authority(market_run, authority_provider, domain)
            else:
                authority = {
                    "status": "unknown",
                    "target_domain": domain,
                    "source": "dataforseo_backlinks_summary_live",
                    "provider_error": {"status_message": "Competitor authority collection was not configured."},
                }
                market_run.evidence_limits.append({
                    "kind": "competitor_authority_unknown",
                    "domain": domain,
                    "message": "Competitor Link Rank is unknown because paid authority collection was unavailable.",
                })
            competitor_evidence["offsite_authority"] = authority
            relative_artifact = f"market/{market_run.id}/competitors/{domain}/evidence.json"
            self.repository.save_market_artifact(
                market_run.insight_run_id,
                market_run.id,
                f"competitors/{domain}/evidence.json",
                competitor_evidence,
            )
            competitor_evidence["artifact_path"] = relative_artifact
            evidence.append(competitor_evidence)
        market_run.competitor_evidence = evidence

        if capture_screenshots:
            self._capture_screenshots(
                market_run,
                target_program_url=target_program_url,
            )
        else:
            market_run.evidence_limits.append({
                "kind": "screenshots_not_requested",
                "message": "Automated screenshot capture was not requested for this enrichment action.",
            })

        target_pages = self.repository.list_page_records(market_run.insight_run_id)
        target_authority = self._target_authority(market_run.insight_run_id)
        matrix, recommendations, limitations = self.gap_service.analyze(
            market_run,
            target_pages=target_pages,
            target_authority=target_authority,
        )
        market_run.gap_matrix = matrix
        market_run.recommended_gaps = recommendations
        market_run.evidence_limits.extend(limitations)
        if market_run.phase == "deep":
            market_run.state = "complete"
            market_run.completed_at = utc_now_iso()
        else:
            market_run.state = "partial"
            market_run.evidence_limits.append({
                "kind": "deep_keyword_collection_not_run",
                "message": "Competitor evidence is complete for the pilot sample; the optional 50-keyword deep collection has not run.",
            })
        market_run.updated_at = utc_now_iso()
        return self.repository.save_market_evidence_run(market_run)

    def _crawl_competitor(
        self,
        market_run: MarketEvidenceRun,
        competitor: dict[str, Any],
        domain: str,
    ) -> dict[str, Any]:
        homepage = f"https://{domain}"
        observed_urls = [
            str(item.get("url"))
            for item in competitor.get("observations", [])
            if item.get("url") and self._normalize_domain(str(item.get("url"))) == domain
        ]
        sitemap_urls, sitemap_errors = self._discover_sitemap_pages(domain)
        seed_urls = list(dict.fromkeys([homepage, *observed_urls, *sitemap_urls]))
        target = SEOTarget(
            input_url=homepage,
            normalized_url=homepage,
            normalized_domain=domain,
            canonical_domain=domain,
            display_name=str(competitor.get("name") or domain),
            source_system="market_competitor",
        )
        analyzer = self.page_analysis_factory()
        output = analyzer.crawl_site(
            target,
            market_run.insight_run_id,
            seed_urls,
            max_pages=10,
        )
        pages = []
        for page in output.pages[:10]:
            ai = page.ai_evidence if isinstance(page.ai_evidence, dict) else {}
            conversion_links = [
                url for url in page.internal_links
                if any(token in url.casefold() for token in ("schedule", "contact", "book", "trial", "signup", "sign-up"))
            ]
            pages.append({
                "url": page.url,
                "http_status": page.http_status,
                "content_type": page.content_type,
                "title": page.title,
                "meta_description": page.meta_description,
                "h1": page.h1,
                "schema_types": list(page.schema_types),
                "word_count": page.word_count,
                "page_class": page.page_class,
                "canonical_url": page.canonical_url,
                "indexable": page.indexable,
                "conversion_links": conversion_links[:20],
                "bounded_excerpts": {
                    "direct_answers": list(ai.get("direct_answer_blocks", []))[:3],
                    "specific_evidence": list(ai.get("specific_evidence_excerpts", []))[:3],
                    "first_text_after_headings": list(ai.get("first_text_after_headings", []))[:3],
                },
            })
        errors = [*sitemap_errors, *output.errors]
        if errors:
            market_run.evidence_limits.append({
                "kind": "competitor_crawl_partial",
                "domain": domain,
                "error_count": len(errors),
                "message": "Some bounded competitor URLs or sitemaps could not be collected.",
            })
        return {
            "candidate_id": competitor.get("candidate_id"),
            "domain": domain,
            "name": competitor.get("name"),
            "crawl_status": "complete" if pages and not errors else "partial" if pages else "failed",
            "page_cap": 10,
            "pages_collected": len(pages),
            "pages_attempted": output.attempted_count,
            "discovered_count": output.discovered_count,
            "capped": output.capped,
            "sitemap_url_count": len(sitemap_urls),
            "pages": pages,
            "errors": errors[:50],
            "source_observations": competitor.get("observations", []),
            "no_competitor_score": True,
        }

    def _discover_sitemap_pages(self, domain: str) -> tuple[list[str], list[dict[str, Any]]]:
        fetcher = self.sitemap_factory()
        urls: list[str] = []
        errors: list[dict[str, Any]] = []
        try:
            discovery = fetcher.discover(domain)
        except Exception as exc:
            return [], [{"source": "robots", "error": f"{type(exc).__name__}: {str(exc)[:240]}"}]
        for message in discovery.errors:
            errors.append({"source": "robots", "error": message})
        queue = list(discovery.sitemap_urls[:5])
        seen_sitemaps: set[str] = set()
        while queue and len(seen_sitemaps) < 5 and len(urls) < 100:
            sitemap_url = queue.pop(0)
            if sitemap_url in seen_sitemaps:
                continue
            seen_sitemaps.add(sitemap_url)
            try:
                document = fetcher.fetch_sitemap_document(sitemap_url)
            except Exception as exc:
                errors.append({
                    "source": sitemap_url,
                    "error": f"{type(exc).__name__}: {str(exc)[:240]}",
                })
                continue
            if document.root_type == "sitemapindex":
                for child in document.urls:
                    if self._normalize_domain(child) == domain and child not in seen_sitemaps:
                        queue.append(child)
            else:
                for page_url in document.urls:
                    if self._normalize_domain(page_url) == domain and page_url not in urls:
                        urls.append(page_url)
                        if len(urls) >= 100:
                            break
        return urls, errors

    def _collect_authority(
        self,
        market_run: MarketEvidenceRun,
        provider: AuthorityProvider,
        domain: str,
    ) -> dict[str, Any]:
        try:
            payload = provider.collect_offsite_authority(domain)
        except Exception as exc:
            payload = {
                "status": "unknown",
                "target_domain": domain,
                "source": "dataforseo_backlinks_summary_live",
                "provider_cost_usd": 0.0,
                "provider_error": {"status_message": f"{type(exc).__name__}: {str(exc)[:240]}"},
            }
        cost = payload.get("provider_cost_usd")
        safe_cost = float(cost) if isinstance(cost, int | float) and not isinstance(cost, bool) else 0.0
        market_run.actual_provider_cost = round(market_run.actual_provider_cost + max(0.0, safe_cost), 6)
        market_run.provider_calls.append({
            "operation": "competitor_authority",
            "query": domain,
            "status": payload.get("status") or "unknown",
            "cost_usd": max(0.0, safe_cost),
            "snapshot_date": payload.get("snapshot_date"),
            "raw_artifact_ref": payload.get("raw_artifact_ref"),
        })
        if payload.get("status") != "complete":
            market_run.evidence_limits.append({
                "kind": "competitor_authority_unknown",
                "domain": domain,
                "message": "The provider did not return a complete competitor backlink summary.",
                "provider_error": payload.get("provider_error"),
            })
        return payload

    def _capture_screenshots(
        self,
        market_run: MarketEvidenceRun,
        *,
        target_program_url: str | None,
    ) -> None:
        target_home = f"https://{market_run.target_domain}"
        captures = [
            {
                "url": target_home,
                "viewport_name": "desktop",
                "caption": "Target homepage at desktop viewport; visual evidence only and excluded from scoring.",
                "artifact_name": "target-home-desktop.png",
            },
            {
                "url": target_home,
                "viewport_name": "mobile",
                "caption": "Target homepage at mobile viewport; visual evidence only and excluded from scoring.",
                "artifact_name": "target-home-mobile.png",
            },
        ]
        program_url = target_program_url or self._target_program_url(market_run.insight_run_id)
        if program_url:
            captures.append({
                "url": program_url,
                "viewport_name": "desktop",
                "caption": "Highest-priority collected target program page at desktop viewport; selected from persisted crawl classification.",
                "artifact_name": "target-program-desktop.png",
            })
        for competitor in market_run.competitor_evidence[:3]:
            landing = self._competitor_landing_url(competitor)
            if not landing:
                continue
            domain = str(competitor.get("domain") or "competitor")
            captures.append({
                "url": landing,
                "viewport_name": "desktop",
                "caption": "Approved competitor landing page observed in persisted Tacoma SERP evidence; visual evidence only.",
                "artifact_name": f"competitor-{domain}-desktop.png",
            })
        for request in captures[:6]:
            artifact = self.screenshot_service.capture(
                insight_run_id=market_run.insight_run_id,
                market_run_id=market_run.id,
                **request,
            )
            market_run.screenshots.append(artifact)
            if artifact.get("capture_status") != "complete":
                market_run.evidence_limits.append({
                    "kind": "screenshot_capture_failed",
                    "url": artifact.get("url"),
                    "message": artifact.get("error") or "Screenshot capture failed.",
                })

    def _target_program_url(self, run_id: str) -> str | None:
        pages = self.repository.list_page_records(run_id)
        candidates = [
            page for page in pages
            if page.page_class in {"service", "service_location", "blog_resource"}
            and page.http_status is not None
            and 200 <= page.http_status < 400
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda page: (-(page.word_count or 0), page.url))
        return candidates[0].url

    @staticmethod
    def _competitor_landing_url(competitor: dict[str, Any]) -> str | None:
        observations = [
            item for item in competitor.get("source_observations", [])
            if item.get("url")
        ]
        observations.sort(key=lambda item: (int(item.get("rank") or 10_000), str(item.get("url"))))
        if observations:
            return str(observations[0]["url"])
        pages = competitor.get("pages") if isinstance(competitor.get("pages"), list) else []
        return str(pages[0]["url"]) if pages and pages[0].get("url") else None

    def _target_authority(self, run_id: str) -> dict[str, Any] | None:
        report = self.repository.get_report(run_id, "v2")
        if report is None:
            return None
        value = report.report_payload.get("offsite_authority")
        return value if isinstance(value, dict) else None

    @staticmethod
    def _normalize_domain(value: str) -> str:
        candidate = value.strip().casefold().rstrip(".")
        if "://" in candidate:
            candidate = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
        return candidate.removeprefix("www.")
