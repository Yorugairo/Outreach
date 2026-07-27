from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Mapping
from urllib.parse import urlsplit, urlunsplit

from src.models import InsightReport, InsightRun, PageRecord, ProductSurfaceResult, SEOTarget
from src.services.ai_readiness_service import AIReadinessOutput
from src.services.crawl_discovery_service import CrawlDiscoveryOutput, sitemap_evidence_status
from src.services.finding_service import FindingService
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import (
    SearchIntelligenceOutput,
    TargetContext,
    build_search_evidence_view,
    validate_target_search_evidence,
)
from src.services.offsite_authority_service import build_offsite_authority_view


_CLIENT_EMAIL_RE = re.compile(
    r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)
_CLIENT_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?1[\s.\-]?)?(?:\(\d{3}\)|\d{3})[\s.\-]\d{3}[\s.\-]\d{4}(?!\d)"
)
_CLIENT_PRIVATE_KEYS = {"raw_html", "phone_numbers", "email_addresses"}


def _redact_client_text(value: str) -> str:
    value = _CLIENT_EMAIL_RE.sub("[email redacted]", value)
    return _CLIENT_PHONE_RE.sub("[phone redacted]", value)


def _client_safe_payload(value: Any, *, key: str | None = None) -> Any:
    """Remove direct contact values and raw source material from client reports."""

    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for child_key, child_value in value.items():
            normalized_key = str(child_key).casefold()
            if normalized_key in _CLIENT_PRIVATE_KEYS:
                if isinstance(child_value, list):
                    count_key = (
                        "phone_number_count"
                        if normalized_key == "phone_numbers"
                        else "email_address_count"
                        if normalized_key == "email_addresses"
                        else None
                    )
                    if count_key and count_key not in value:
                        result[count_key] = len(child_value)
                continue
            result[str(child_key)] = _client_safe_payload(
                child_value,
                key=normalized_key,
            )
        return result
    if isinstance(value, list):
        return [_client_safe_payload(item, key=key) for item in value]
    if isinstance(value, str):
        if key in {"href", "action"}:
            parsed = urlsplit(value)
            if parsed.scheme.casefold() in {"mailto", "tel"}:
                return "[contact route redacted]"
            if parsed.scheme.casefold() in {"http", "https"}:
                value = urlunsplit(
                    (parsed.scheme, parsed.netloc, parsed.path, "", "")
                )
        return _redact_client_text(value)
    return value


def _markdown_label(value: str) -> str:
    return value.replace("_", " ").capitalize()


def _markdown_label_list(values: list[str]) -> str:
    return ", ".join(_markdown_label(value) for value in values) if values else "[]"


def _markdown_evidence_reason(reason: str) -> str:
    credential_names = ("DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD")
    if any(name in reason for name in credential_names):
        return "Target-specific search evidence is unavailable because search enrichment is not configured."
    return reason


@dataclass(slots=True)
class ScorecardOutput:
    overall_score: float | None
    sitemap_quality_score: float | None
    metadata_quality_score: float | None
    page_coverage_score: float | None
    search_visibility_score: float | None
    dimension_status: dict[str, str]
    scored_dimensions: list[str]
    completeness_percent: float
    warnings: list[str]
    metrics: dict[str, Any]


class ScorecardService:
    DIMENSIONS = ("sitemap_quality", "metadata_quality", "page_coverage", "search_visibility")

    def build(
        self,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        *,
        target_context: TargetContext | Mapping[str, Any],
    ) -> ScorecardOutput:
        context = TargetContext.from_value(target_context)
        page_count = len(pages.pages)
        sitemap_count = len(crawl.sitemap_urls)
        indexable_count = sum(1 for p in pages.pages if p.indexable)
        fetch_error_count = len(pages.errors)

        sitemap_state = sitemap_evidence_status(crawl)
        sitemap_quality: float | None = (
            min(100.0, 40.0 + sitemap_count * 20.0)
            if sitemap_state == "valid"
            else 20.0 if sitemap_state == "prospect_issue" else None
        )
        primary_page = next(
            (
                page for page in pages.pages
                if page.fetch_status == "fetched" and self._is_primary_page(page, context.primary_url)
            ),
            None,
        )
        meta_complete = int(bool(
            primary_page
            and primary_page.title
            and primary_page.meta_description
            and primary_page.h1
        ))
        metadata_quality: float | None = 100.0 if meta_complete else (0.0 if primary_page else None)
        page_coverage: float | None = None
        search_visibility = validate_target_search_evidence(search, context)

        dimension_scores = {
            "sitemap_quality": sitemap_quality,
            "metadata_quality": metadata_quality,
            "page_coverage": page_coverage,
            "search_visibility": search_visibility,
        }
        dimension_status = {
            name: "valid" if score is not None else "unknown" for name, score in dimension_scores.items()
        }
        warnings: list[str] = []
        if sitemap_state == "unknown":
            warnings.append("Sitemap quality is unknown because discovery evidence was inconclusive.")
        elif crawl.errors and sitemap_state == "valid":
            dimension_status["sitemap_quality"] = "degraded"
            warnings.append("Sitemap quality evidence is degraded because crawl discovery reported errors.")
        if primary_page is None:
            warnings.append("Metadata quality is unknown because the primary requested URL was not fetched.")
        warnings.append(
            "Page coverage is unknown: sampled page count is a run limit/completeness fact, not a site-health measure; "
            "a real demand/inventory denominator is required."
        )
        if search_visibility is None:
            warnings.append("Target-specific search evidence was not collected for this run.")

        scored_dimensions = [name for name in self.DIMENSIONS if dimension_scores[name] is not None]
        measured_scores = [dimension_scores[name] for name in scored_dimensions]
        overall = round(sum(measured_scores) / len(measured_scores), 2) if measured_scores else None

        return ScorecardOutput(
            overall_score=overall,
            sitemap_quality_score=round(sitemap_quality, 2) if sitemap_quality is not None else None,
            metadata_quality_score=metadata_quality,
            page_coverage_score=round(page_coverage, 2) if page_coverage is not None else None,
            search_visibility_score=search_visibility,
            dimension_status=dimension_status,
            scored_dimensions=scored_dimensions,
            completeness_percent=len(scored_dimensions) / 4 * 100,
            warnings=warnings,
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

    @classmethod
    def _is_primary_page(cls, page: PageRecord, primary_url: str) -> bool:
        requested_url = page.fetch_metadata.get("fetched_url")
        identity_url = requested_url if isinstance(requested_url, str) and requested_url.strip() else page.url
        return cls._normalize_url(identity_url) == cls._normalize_url(primary_url)

    @staticmethod
    def _normalize_url(value: str) -> str:
        parsed = urlsplit(value)
        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/")
        return urlunsplit((parsed.scheme.casefold(), parsed.netloc.casefold(), path, parsed.query, ""))


class ReportAssemblyService:
    def build_technical_health_report(
        self,
        target: SEOTarget,
        run: InsightRun,
        output: ProductSurfaceResult,
    ) -> InsightReport:
        payload = _client_safe_payload(output.to_dict())
        payload["target"] = {
            "id": target.id,
            "normalized_url": target.normalized_url,
            "normalized_domain": target.normalized_domain,
        }
        payload["run_id"] = run.id
        payload["attempt_id"] = run.attempt_id
        lines = [
            f"# Technical SEO Health — {target.normalized_domain}",
            "",
            f"- Score: {payload['score']}/100",
            f"- Formula: {payload['version']}",
            f"- Evidence completeness: {payload['completeness_percent']}% ({payload['status']})",
            f"- Evidence Confidence: {payload['evidence_confidence']}%",
            "- Scope: collected-site technical health; rankings are reported separately.",
            "",
            "## Families",
        ]
        for name, family in payload["families"].items():
            lines.append(
                f"- {_markdown_label(name)}: {family.get('score')} "
                f"({family.get('completeness_percent')}% complete)"
            )
        lines.extend(["", "## Priority actions"])
        for item in payload.get("recommendations", []):
            lines.append(
                f"- **{item['check_id']}** — {item['action']} "
                f"({item['affected_page_count']} affected pages)"
            )
        if payload.get("warnings"):
            lines.extend(["", "## Evidence limits"])
            lines.extend(f"- {warning}" for warning in payload["warnings"])
        markdown = "\n".join(lines) + "\n"
        return InsightReport(
            insight_run_id=run.id,
            seo_target_id=target.id,
            report_version="seo-health-v2",
            attempt_id=run.attempt_id,
            report_status="complete",
            headline=f"Technical SEO Health for {target.normalized_domain}",
            executive_summary=(
                f"Technical SEO Health is {output.score}/100 at "
                f"{output.completeness_percent}% evidence completeness."
            ),
            key_actions=output.recommendations,
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
        )

    def build_ai_report(
        self,
        target: SEOTarget,
        run: InsightRun,
        output: AIReadinessOutput,
    ) -> InsightReport:
        payload = _client_safe_payload(output.to_dict())
        payload["target"] = {
            "id": target.id,
            "normalized_url": target.normalized_url,
            "normalized_domain": target.normalized_domain,
        }
        payload["run_id"] = run.id
        checkpoint_by_check = {
            "crawler_access": (
                "discovering_sitemaps",
                "payload.crawl.robots_access",
            ),
            "link_health": ("fetching_pages", "payload.errors"),
            "external_corroboration": (
                "pulling_search_intelligence",
                "payload.payload.external_mentions",
            ),
        }
        for cohort in payload.get("cohorts", {}).values():
            for dimension in cohort.get("dimensions", {}).values():
                for check in dimension.get("checks", []):
                    evidence_observed = check.pop(
                        "evidence_observed",
                        check.get("score"),
                    )
                    evidence_field = check.pop("evidence_field", None)
                    if check.get("evidence_refs"):
                        continue
                    contract = checkpoint_by_check.get(check.get("id"))
                    if contract:
                        stage, field = contract
                        field = evidence_field or field
                        check["evidence_refs"] = [{
                            "artifact_path": f"checkpoints/{run.attempt_id}/{stage}.json",
                            "field": field,
                            "reason": check.get("observation", "Persisted scoring evidence."),
                            "observed": evidence_observed,
                        }]
        markdown = _redact_client_text(self._markdown_ai(target, payload))
        report_version = (
            "ai-v3"
            if output.score_version == "ai-readiness.v3"
            else "ai-v2"
        )
        return InsightReport(
            insight_run_id=run.id,
            seo_target_id=target.id,
            report_version=report_version,
            attempt_id=run.attempt_id,
            report_status="complete",
            headline=f"AI Readiness for {target.normalized_domain}",
            executive_summary=(
                f"AI Readiness is {output.score}/100 ({output.presentation_label}) at "
                f"{output.completeness_percent}% evidence completeness. "
                "Readiness does not prove AI citation or ranking."
            ),
            key_actions=output.recommendations,
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
        )

    def build_conversion_readiness_report(
        self,
        target: SEOTarget,
        run: InsightRun,
        output: ProductSurfaceResult,
    ) -> InsightReport:
        payload = _client_safe_payload(output.to_dict())
        payload["target"] = {
            "id": target.id,
            "normalized_url": target.normalized_url,
            "normalized_domain": target.normalized_domain,
        }
        payload["run_id"] = run.id
        payload["attempt_id"] = run.attempt_id
        lines = [
            f"# Conversion Readiness — {target.normalized_domain}",
            "",
            f"- Score: {payload['score']}/100",
            f"- Formula: {payload['version']}",
            (
                f"- Evidence completeness: {payload['completeness_percent']}% "
                f"({payload['status']})"
            ),
            f"- Evidence Confidence: {payload['evidence_confidence']}%",
            (
                "- Scope: visible website paths only; this does not measure lead "
                "quality, attendance, close rate, CRM performance, or revenue."
            ),
            "",
            "## Checks",
        ]
        for check in payload.get("checks", []):
            lines.append(
                f"- {_markdown_label(check['check_id'])}: "
                f"{check.get('score')} ({check.get('status')})"
            )
        if payload.get("recommendations"):
            lines.extend(["", "## Priority actions"])
            for item in payload["recommendations"]:
                lines.append(
                    f"- **{_markdown_label(item['check_id'])}** — "
                    f"{item['action']}"
                )
        if payload.get("warnings"):
            lines.extend(["", "## Evidence limits"])
            lines.extend(f"- {warning}" for warning in payload["warnings"])
        markdown = _redact_client_text("\n".join(lines) + "\n")
        return InsightReport(
            insight_run_id=run.id,
            seo_target_id=target.id,
            report_version="conversion-v1",
            attempt_id=run.attempt_id,
            report_status="complete",
            headline=f"Conversion Readiness for {target.normalized_domain}",
            executive_summary=(
                f"Conversion Readiness is {output.score}/100 at "
                f"{output.completeness_percent}% evidence completeness. "
                "It measures visible website path readiness, not funnel results."
            ),
            key_actions=output.recommendations,
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
        )

    @staticmethod
    def _markdown_ai(target: SEOTarget, payload: dict[str, Any]) -> str:
        lines = [
            f"# AI Readiness — {target.normalized_domain}",
            "",
            f"- Score: {payload['score']}/100 ({payload['presentation_label']})",
            f"- Formula: {payload['score_version']} — 40% AEO, 35% GEO, 25% AIO",
            f"- Evidence completeness: {payload['completeness_percent']}% ({payload['status']})",
            f"- Customer-claim eligible: {payload['customer_claim_eligible']}",
            "- Scope: readiness only; this does not prove AI citation, visibility, or ranking.",
            "",
            "## Dimensions",
        ]
        for name in ("aeo", "geo", "aio"):
            dimension = payload["dimensions"].get(name, {})
            lines.append(f"- {name.upper()}: {dimension.get('score')} — {dimension.get('description', '')}")
        lines.extend(["", "## Page cohorts"])
        for name in ("core", "supporting"):
            cohort = payload["cohorts"].get(name, {})
            lines.append(
                f"- {name.capitalize()}: {cohort.get('score')} "
                f"({cohort.get('completeness_percent', 0)}% complete)"
            )
        lines.extend(["", "## Prioritized actions"])
        for item in payload.get("recommendations", []):
            lines.append(f"- **{item['title']}** — {item['action']}")
        if payload.get("broken_links"):
            lines.extend(["", "## Conclusive crawl errors"])
            for item in payload["broken_links"]:
                lines.append(f"- {item.get('url')}: {item.get('http_status')} {item.get('error', '')}")
        if payload.get("warnings"):
            lines.extend(["", "## Evidence limits"])
            lines.extend(f"- {warning}" for warning in payload["warnings"])
        return "\n".join(lines) + "\n"

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
        payload = _client_safe_payload(payload)
        safe_key_actions = _client_safe_payload(key_actions)
        markdown = _redact_client_text(
            self._markdown(target, scorecard, key_actions)
        )
        return InsightReport(
            insight_run_id=run.id,
            seo_target_id=target.id,
            attempt_id=run.attempt_id,
            report_status="complete",
            headline=f"SEO Insight Run for {target.normalized_domain}",
            executive_summary=f"Generated a scaffolded SEO insight run for {target.normalized_domain} with {len(pages.pages)} analyzed pages.",
            key_actions=safe_key_actions,
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
        )

    def build_report_v2(
        self,
        target: SEOTarget,
        run: InsightRun,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        scorecard: ScorecardOutput,
        *,
        target_context: TargetContext | Mapping[str, Any],
        stage_artifacts: Mapping[str, str],
    ) -> InsightReport:
        context = TargetContext.from_value(target_context)
        search_visibility = build_search_evidence_view(
            search,
            context,
            checkpoint_path=stage_artifacts.get("pulling_search_intelligence"),
        )
        offsite_authority = build_offsite_authority_view(
            search,
            context,
            checkpoint_path=stage_artifacts.get("pulling_search_intelligence"),
        )
        findings = FindingService().build_findings(
            crawl,
            pages,
            search,
            target_context=context,
            stage_artifacts=stage_artifacts,
        )
        finding_payloads = [finding.to_dict() for finding in findings]
        next_best_action = next(
            (
                finding.to_dict()
                for finding in findings
                if finding.finding_type == "prospect_issue" and finding.recommended_services
            ),
            None,
        )
        if next_best_action:
            executive_answer = (
                f"The strongest supported issue is: {next_best_action['observation']} "
                f"We would {next_best_action['recommended_action'][0].lower()}"
                f"{next_best_action['recommended_action'][1:]}"
            )
        elif findings:
            executive_answer = (
                "The collected evidence supports completeness warnings but no commercial service route; "
                "additional target-specific evidence is required."
            )
        else:
            executive_answer = (
                "The collected evidence did not produce a supported commercial finding or service route."
            )
        method_and_limits = {
            "mode": run.mode,
            "limits": run.input_payload.get("limits", {}),
            "budget": run.input_payload.get("budget", {}),
            "scored_dimensions": scorecard.scored_dimensions,
            "completeness_percent": scorecard.completeness_percent,
            "warnings": scorecard.warnings,
        }
        key_actions = [
            {
                "finding_type": finding.finding_type,
                "category": finding.category,
                "priority": finding.severity,
                "action": finding.recommended_action,
                "confidence": finding.confidence,
                "recommended_services": finding.recommended_services,
                "evidence_refs": finding.evidence_refs,
            }
            for finding in findings
            if finding.finding_type == "prospect_issue" and finding.recommended_services
        ]
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
            "pages": [page.to_dict() for page in sorted(pages.pages, key=lambda item: (item.url.casefold(), item.id))],
            "page_errors": sorted(
                pages.errors,
                key=lambda item: (str(item.get("url", "")), str(item.get("error", ""))),
            ),
            "search": {
                "configured": search.configured,
                "approved": search.approved,
                "skipped_reason": search.skipped_reason,
                "payload": search.payload,
            },
            "search_visibility": search_visibility,
            "offsite_authority": offsite_authority,
            "target_context": context.to_dict(),
            "scorecard": asdict(scorecard),
            "findings": finding_payloads,
            "executive_answer": executive_answer,
            "method_and_limits": method_and_limits,
            "next_best_action": next_best_action,
            "key_actions": key_actions,
        }
        payload = _client_safe_payload(payload)
        safe_key_actions = _client_safe_payload(key_actions)
        safe_executive_answer = _redact_client_text(executive_answer)
        markdown = _redact_client_text(
            self._markdown_v2(
                target,
                executive_answer,
                finding_payloads,
                method_and_limits,
                search_visibility,
                offsite_authority,
            )
        )
        return InsightReport(
            insight_run_id=run.id,
            seo_target_id=target.id,
            report_version="v2",
            attempt_id=run.attempt_id,
            report_status="complete",
            headline=f"Evidence-backed SEO opportunity for {target.normalized_domain}",
            executive_summary=safe_executive_answer,
            key_actions=safe_key_actions,
            report_payload=payload,
            export_json=payload,
            export_markdown=markdown,
        )

    @staticmethod
    def _markdown_v2(
        target: SEOTarget,
        executive_answer: str,
        findings: list[dict[str, Any]],
        method_and_limits: dict[str, Any],
        search_visibility: dict[str, Any] | None = None,
        offsite_authority: dict[str, Any] | None = None,
    ) -> str:
        lines = [
            f"# Evidence-backed SEO opportunity — {target.normalized_domain}",
            "",
            "## Executive answer",
            executive_answer,
            "",
        ]
        search_view = search_visibility or {}
        lines.extend(
            [
                "## Keywords and Google rankings",
                "",
                f"- Evidence status: {_markdown_label(str(search_view.get('status', 'unknown')))}",
                f"- Search visibility: {search_view.get('visibility_score') if search_view.get('visibility_score') is not None else 'Unknown'}",
                f"- Market/device: {search_view.get('market') or 'Unknown'} / {search_view.get('device') or 'Unknown'}",
                f"- Snapshot date: {search_view.get('snapshot_date') or 'Unknown'}",
                f"- Provider calls: {search_view.get('provider_call_count', 0)}",
                "",
            ]
        )
        search_rows = search_view.get("keywords", [])
        if search_rows:
            lines.extend(
                [
                    "| Keyword | Volume | Intent | Organic position | Overall SERP position | Ranking page | Opportunity |",
                    "| --- | ---: | --- | ---: | ---: | --- | --- |",
                ]
            )
            for row in search_rows:
                if not isinstance(row, Mapping):
                    continue
                position = row.get("observed_rank")
                if row.get("checked") and position is None:
                    position = "Not observed in sampled top 100"
                elif not row.get("checked"):
                    position = "Not checked"
                lines.append(
                    "| "
                    + " | ".join(
                        str("Unknown" if value is None or value == "" else value).replace("|", "\\|")
                        for value in (
                            row.get("keyword"),
                            row.get("search_volume"),
                            row.get("intent"),
                            position,
                            row.get("observed_absolute_position"),
                            row.get("observed_url"),
                            row.get("opportunity_label"),
                        )
                    )
                    + " |"
                )
        else:
            lines.append("No target-specific paid keyword or Google ranking evidence was collected.")
        for limitation in search_view.get("limitations", []):
            lines.append(f"- Evidence limit: {limitation}")
        lines.append("")
        if offsite_authority is not None:
            authority = offsite_authority
            lines.extend(
                [
                    "## Off-site authority",
                    "",
                    f"- Evidence status: {_markdown_label(str(authority.get('status', 'unknown')))}",
                    (
                        f"- DataForSEO Link Rank: {authority.get('link_rank')}/100"
                        if authority.get("link_rank") is not None
                        else "- DataForSEO Link Rank: Unknown"
                    ),
                    f"- Backlinks: {authority.get('backlinks') if authority.get('backlinks') is not None else 'Unknown'}",
                    f"- Referring domains: {authority.get('referring_domains') if authority.get('referring_domains') is not None else 'Unknown'}",
                    f"- Referring main domains: {authority.get('referring_main_domains') if authority.get('referring_main_domains') is not None else 'Unknown'}",
                    f"- Referring pages: {authority.get('referring_pages') if authority.get('referring_pages') is not None else 'Unknown'}",
                    f"- Referring IPs/subnets: {authority.get('referring_ips') if authority.get('referring_ips') is not None else 'Unknown'} / {authority.get('referring_subnets') if authority.get('referring_subnets') is not None else 'Unknown'}",
                    (
                        f"- Rel=nofollow referring domains: {authority.get('referring_domains_nofollow_percent')}%"
                        if authority.get("referring_domains_nofollow_percent") is not None
                        else "- Rel=nofollow referring domains: Unknown"
                    ),
                    f"- Backlink spam score: {authority.get('backlinks_spam_score') if authority.get('backlinks_spam_score') is not None else 'Unknown'}",
                    f"- Snapshot date: {authority.get('snapshot_date') or 'Unknown'}",
                    "",
                ]
            )
            for limitation in authority.get("limitations", []):
                lines.append(f"- Evidence limit: {limitation}")
            lines.append("")
        prospect_issues = [item for item in findings if item["finding_type"] == "prospect_issue"]
        evidence_limits = [item for item in findings if item["finding_type"] == "evidence_limit"]
        if not prospect_issues:
            lines.extend(
                [
                    "## What is wrong",
                    "No supported target finding was produced from the collected evidence.",
                    "",
                    "## Why it matters",
                    "No impact claim is supported without a persisted prospect issue.",
                    "",
                    "## What we would fix",
                    "No remediation scope is recommended from this run.",
                    "",
                    "## Service fit",
                    "No supported commercial service route.",
                    "",
                ]
            )
        service_labels = {
            "web_development_rebuild": "Website development / rebuild",
            "profile_management_reputation": "Profile management / reputation",
            "pseo_search_architecture": "pSEO / search architecture",
        }
        for finding in prospect_issues:
            services = ", ".join(service_labels[item] for item in finding["recommended_services"])
            lines.extend(
                [
                    f"## {finding['title']}",
                    "",
                    "### What is wrong",
                    finding["observation"],
                    "",
                    "### Why it matters",
                    finding["impact"],
                    "",
                    "### What we would fix",
                    finding["recommended_action"],
                    "",
                    "### Service fit",
                    f"{services}. {finding['service_fit_reason']}",
                    "",
                    f"- Confidence: {_markdown_label(finding['confidence'])}",
                    f"- Effort: {_markdown_label(finding['effort'])}",
                    "",
                    "### Evidence",
                ]
            )
            for ref in finding["evidence_refs"]:
                lines.append(
                    f"- `{ref['artifact_path']}` → `{ref['field']}` ({_markdown_evidence_reason(ref['reason'])})"
                )
            lines.append("")
        if evidence_limits:
            lines.extend(["## Evidence limits (operator review)", ""])
            for finding in evidence_limits:
                lines.extend(
                    [
                        f"### {finding['title']}",
                        "",
                        "#### What remains unknown",
                        finding["impact"],
                        "",
                        "#### How to verify",
                        finding["recommended_action"],
                        "",
                        f"- Confidence: {_markdown_label(finding['confidence'])}",
                        f"- Effort: {_markdown_label(finding['effort'])}",
                        "",
                        "#### Evidence",
                    ]
                )
                for ref in finding["evidence_refs"]:
                    lines.append(f"- `{ref['artifact_path']}` → `{ref['field']}`")
                lines.append("")
        lines.extend(
            [
                "## Method and limits",
                f"- Mode: {method_and_limits['mode']}",
                f"- Limits: {method_and_limits['limits']}",
                f"- Budget: {method_and_limits['budget']}",
                f"- Scored dimensions: {_markdown_label_list(method_and_limits['scored_dimensions'])}",
                f"- Completeness: {method_and_limits['completeness_percent']}%",
            ]
        )
        for warning in method_and_limits["warnings"]:
            lines.append(f"- Warning: {warning}")
        return "\n".join(lines) + "\n"

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
                            "artifact_type": "run",
                            "artifact_path": "run.json",
                            "field": "summary.sitemap_count",
                            "reason": "No sitemap URLs were validated for this run.",
                            "observed": run.summary.get("sitemap_count", 0),
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
                lines.append(
                    f"  - Evidence: `{ref['artifact_path']}` → `{ref['field']}` "
                    f"({_markdown_evidence_reason(ref['reason'])})"
                )
        return "\n".join(lines) + "\n"
