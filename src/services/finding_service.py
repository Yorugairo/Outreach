from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from src.models import CommercialFinding, PageRecord
from src.services.crawl_discovery_service import CrawlDiscoveryOutput, sitemap_evidence_status
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import (
    SearchIntelligenceOutput,
    TargetContext,
    validate_target_search_evidence,
)


class FindingService:
    """Pure, deterministic evidence-to-finding rules in commercial priority order."""

    WEB_DEVELOPMENT = "web_development_rebuild"

    def build_findings(
        self,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        *,
        target_context: TargetContext | Mapping[str, Any],
        stage_artifacts: Mapping[str, str],
    ) -> list[CommercialFinding]:
        context = TargetContext.from_value(target_context)
        findings: list[CommercialFinding] = []
        sitemap = self._sitemap_finding(crawl, stage_artifacts["discovering_sitemaps"])
        if sitemap:
            findings.append(sitemap)
        metadata = self._metadata_finding(pages.pages)
        if metadata:
            findings.append(metadata)
        heading = self._h1_finding(pages.pages)
        if heading:
            findings.append(heading)
        fetch_warning = self._fetch_error_finding(pages.errors, stage_artifacts["fetching_pages"])
        if fetch_warning:
            findings.append(fetch_warning)
        search_warning = self._search_warning(
            search, context, stage_artifacts["pulling_search_intelligence"]
        )
        if search_warning:
            findings.append(search_warning)
        return findings

    def _sitemap_finding(self, crawl: CrawlDiscoveryOutput, artifact_path: str) -> CommercialFinding | None:
        state = sitemap_evidence_status(crawl)
        if state == "valid":
            return None
        candidates = sorted(set(crawl.candidate_sitemap_urls))
        errors = sorted(crawl.errors)
        refs = [
            self._ref(
                artifact_path,
                "output_summary.candidate_sitemap_urls",
                "Sitemap candidate URL(s) attempted by crawl discovery.",
                observed=candidates,
            )
        ]
        if errors:
            refs.append(
                self._ref(
                    artifact_path,
                    "output_summary.errors",
                    "Persisted outcomes from checking the sitemap candidate URL(s).",
                    observed=errors,
                )
            )
        if state == "prospect_issue":
            return self._finding(
                finding_type="prospect_issue",
                rule_key="no_validated_sitemap:conclusive_candidate_failure",
                category="sitemap_discovery",
                title="Attempted sitemap candidate did not provide a valid sitemap",
                observation="Sitemap candidate URL(s) were checked and produced conclusive absence or malformed XML evidence.",
                impact="Search engines may have less reliable support for discovering the site's intended indexable URLs.",
                recommended_action="Implement or repair an XML sitemap, expose it consistently, and verify that it validates.",
                severity="high",
                effort="medium",
                confidence="high",
                services=[self.WEB_DEVELOPMENT],
                service_fit_reason="The persisted candidate outcome supports website sitemap remediation.",
                refs=refs,
            )
        observation = (
            "No sitemap candidate URL was available to check in this run."
            if not candidates
            else "Sitemap candidate URL(s) were attempted, but the persisted result was inconclusive."
        )
        return self._finding(
            finding_type="evidence_limit",
            rule_key="sitemap_evidence_inconclusive",
            category="sitemap_discovery",
            title="Sitemap status remains unknown",
            observation=observation,
            impact="Whether the target has a valid sitemap remains unknown.",
            recommended_action="Recheck sitemap discovery and persist a conclusive HTTP or XML validation result.",
            severity="info",
            effort="discovery_required",
            confidence="high",
            services=[],
            service_fit_reason="No service route is supported by inconclusive collection evidence.",
            refs=refs,
        )

    def _metadata_finding(self, pages: list[PageRecord]) -> CommercialFinding | None:
        affected = [
            page for page in self._eligible_pages(pages)
            if not self._present(page.title) or not self._present(page.meta_description)
        ]
        if not affected:
            return None
        refs: list[dict[str, Any]] = []
        missing_title = 0
        missing_description = 0
        for page in affected:
            if not self._present(page.title):
                missing_title += 1
                refs.append(self._page_ref(page, "title", "Fetched indexable page has no title."))
            if not self._present(page.meta_description):
                missing_description += 1
                refs.append(self._page_ref(page, "meta_description", "Fetched indexable page has no meta description."))
        return self._finding(
            finding_type="prospect_issue",
            rule_key="indexable_pages_missing_metadata",
            category="page_metadata",
            title="Fetched indexable pages have incomplete search metadata",
            observation=(
                f"Across {len(affected)} fetched indexable page(s), {missing_title} lacked a title and "
                f"{missing_description} lacked a meta description."
            ),
            impact="Incomplete titles or descriptions can weaken how those pages communicate their subject in search results.",
            recommended_action="Write and implement page-specific titles and meta descriptions, then refetch the affected URLs.",
            severity="high",
            effort="medium",
            confidence="high",
            services=[self.WEB_DEVELOPMENT],
            service_fit_reason="The affected fields are persisted on fetched website pages and support direct website remediation.",
            refs=refs,
        )

    def _h1_finding(self, pages: list[PageRecord]) -> CommercialFinding | None:
        affected = [page for page in self._eligible_pages(pages) if not self._present(page.h1)]
        if not affected:
            return None
        return self._finding(
            finding_type="prospect_issue",
            rule_key="indexable_pages_missing_h1",
            category="page_heading",
            title="Fetched indexable pages are missing a primary heading",
            observation=f"{len(affected)} fetched indexable page(s) had no H1 in the persisted page record.",
            impact="Without a primary heading, those pages may communicate their main topic less clearly to visitors and crawlers.",
            recommended_action="Add one clear, page-specific H1 to each affected page and verify the rendered result.",
            severity="medium",
            effort="small",
            confidence="high",
            services=[self.WEB_DEVELOPMENT],
            service_fit_reason="The missing headings are persisted website implementation facts suitable for direct remediation.",
            refs=[self._page_ref(page, "h1", "Fetched indexable page has no H1.") for page in affected],
        )

    def _fetch_error_finding(self, errors: list[dict[str, str]], artifact_path: str) -> CommercialFinding | None:
        if not errors:
            return None
        ordered = sorted(errors, key=lambda item: (str(item.get("url", "")), str(item.get("error", ""))))
        refs = [
            self._ref(
                artifact_path,
                f"output_summary.errors[{index}]",
                "The page fetch error was persisted and requires a reproducibility check.",
                observed=error,
                url=str(error.get("url", "")),
            )
            for index, error in enumerate(ordered)
        ]
        return self._finding(
            finding_type="evidence_limit",
            rule_key="persisted_page_fetch_errors",
            category="page_fetch_evidence",
            title="Some requested pages could not be verified",
            observation=f"{len(ordered)} page fetch error(s) were persisted for this run.",
            impact="Evidence for those URLs is incomplete, so no site-remediation conclusion is supported until the failures are reproduced.",
            recommended_action="Recheck the failed URLs and record reproducible HTTP or indexability facts before scoping remediation.",
            severity="info",
            effort="discovery_required",
            confidence="high",
            services=[],
            service_fit_reason="No supported commercial route is assigned because a fetch exception alone is not remediation evidence.",
            refs=refs,
        )

    def _search_warning(
        self,
        search: SearchIntelligenceOutput,
        context: TargetContext,
        artifact_path: str,
    ) -> CommercialFinding | None:
        if validate_target_search_evidence(search, context) is not None:
            return None
        if not search.configured:
            state, field, observed = "unconfigured", "output_summary.configured", False
        elif not search.approved:
            state, field, observed = "unapproved", "output_summary.approved", False
        else:
            state, field, observed = "invalid_target_evidence", "output_summary.payload_keys", sorted(search.payload)
        reason = search.skipped_reason or "Search payload did not pass the target-specific evidence contract."
        return self._finding(
            finding_type="evidence_limit",
            rule_key=f"search_evidence_incomplete:{state}",
            category="search_evidence_completeness",
            title="Target-specific search evidence is incomplete",
            observation="Target-specific search evidence was not collected for this run.",
            impact="Search visibility and demand conclusions remain unknown; this is not a criticism of the target site.",
            recommended_action="Collect target-specific search evidence with matching run context before making visibility claims.",
            severity="info",
            effort="discovery_required",
            confidence="high",
            services=[],
            service_fit_reason="No supported commercial route is assigned from missing or invalid target-specific evidence.",
            refs=[self._ref(artifact_path, field, reason, observed=observed)],
        )

    @staticmethod
    def _eligible_pages(pages: list[PageRecord]) -> list[PageRecord]:
        return sorted(
            (page for page in pages if page.fetch_status == "fetched" and page.indexable is True),
            key=lambda page: page.url.casefold(),
        )

    @staticmethod
    def _present(value: str | None) -> bool:
        return isinstance(value, str) and bool(value.strip())

    @staticmethod
    def _page_ref(page: PageRecord, field: str, reason: str) -> dict[str, Any]:
        return FindingService._ref(
            f"pages/{page.id}.json", field, reason, observed=getattr(page, field), url=page.url
        )

    @staticmethod
    def _ref(artifact_path: str, field: str, reason: str, *, observed: Any, **extra: Any) -> dict[str, Any]:
        return {"artifact_path": artifact_path, "field": field, "reason": reason, "observed": observed, **extra}

    def _finding(
        self,
        *,
        finding_type: str,
        rule_key: str,
        category: str,
        title: str,
        observation: str,
        impact: str,
        recommended_action: str,
        severity: str,
        effort: str,
        confidence: str,
        services: list[str],
        service_fit_reason: str,
        refs: list[dict[str, Any]],
    ) -> CommercialFinding:
        ordered_refs = sorted(refs, key=self._sort_identity)
        stable_identities = sorted(self._stable_identity(ref) for ref in refs)
        digest = hashlib.sha256(
            json.dumps([rule_key, stable_identities], separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()[:16]
        return CommercialFinding(
            id=f"finding-{digest}",
            finding_type=finding_type,
            category=category,
            title=title,
            observation=observation,
            impact=impact,
            recommended_action=recommended_action,
            severity=severity,
            effort=effort,
            confidence=confidence,
            recommended_services=services,
            service_fit_reason=service_fit_reason,
            evidence_refs=ordered_refs,
        )

    @staticmethod
    def _stable_identity(ref: dict[str, Any]) -> tuple[str, str, str, str]:
        observed = json.dumps(ref.get("observed"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return str(ref["field"]), str(ref.get("url", "")), observed, str(ref["reason"])

    @staticmethod
    def _sort_identity(ref: dict[str, Any]) -> tuple[str, str, str, str, str]:
        stable = FindingService._stable_identity(ref)
        return (str(ref["artifact_path"]), *stable)
