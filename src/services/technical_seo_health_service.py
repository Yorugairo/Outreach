from __future__ import annotations

from collections import Counter
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit, urlunsplit

from src.models import (
    EVIDENCE_CONFIDENCE_VERSION,
    PRODUCT_SURFACE_VERSIONS,
    TECHNICAL_SEO_CHECK_REGISTRY,
    TECHNICAL_SEO_FAMILY_WEIGHTS,
    TECHNICAL_SEO_SEVERITY_WEIGHTS,
    PageRecord,
    ProductSurfaceResult,
    ScoreCheckResult,
)
from src.services.crawl_discovery_service import CrawlDiscoveryOutput, sitemap_evidence_status
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.performance_evidence_service import PerformanceEvidenceService


UTILITY_CLASSES = {"legal_utility", "low_value"}
CORE_CLASSES = {"homepage", "service", "location", "service_location", "contact_about"}
PAGE_IMPORTANCE = {
    "homepage": 1.50,
    "service": 1.25,
    "location": 1.25,
    "service_location": 1.25,
    "contact_about": 1.00,
    "blog_resource": 0.80,
    "project_case_study": 0.80,
    "unclassified": 0.60,
}


class TechnicalSEOHealthService:
    """Deterministic, site-wide technical issue-density scoring."""

    def build(
        self,
        crawl: CrawlDiscoveryOutput,
        page_output: PageAnalysisOutput,
        *,
        page_limit: int = 100,
        attempt_id: str | None = None,
        performance_evidence: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> ProductSurfaceResult:
        pages = [
            page
            for page in page_output.pages
            if page.fetch_status == "fetched" and page.page_class not in UTILITY_CLASSES
        ]
        checks = self._build_checks(
            crawl,
            page_output,
            pages,
            attempt_id=attempt_id,
            performance_evidence=performance_evidence,
        )
        families: dict[str, Any] = {}
        for family, family_weight in TECHNICAL_SEO_FAMILY_WEIGHTS.items():
            family_checks = [
                check
                for check in checks
                if check.family == family and check.score_affecting
            ]
            known = [
                check
                for check in family_checks
                if check.status in {"measured", "failed"}
            ]
            intended = [
                check for check in family_checks if check.status != "inapplicable"
            ]
            known_weight = sum(
                TECHNICAL_SEO_SEVERITY_WEIGHTS[check.severity] for check in known
            )
            intended_weight = sum(
                TECHNICAL_SEO_SEVERITY_WEIGHTS[check.severity] for check in intended
            )
            penalty = sum(
                TECHNICAL_SEO_SEVERITY_WEIGHTS[check.severity]
                * float(check.weighted_affected_ratio or 0.0)
                * float(check.evidence_confidence or 0.0)
                for check in known
            )
            score = (
                max(0.0, min(100.0, 100 - 100 * penalty / known_weight))
                if known_weight
                else None
            )
            completeness = (
                known_weight / intended_weight * 100 if intended_weight else 100.0
            )
            families[family] = {
                "weight": family_weight,
                "score": round(score, 4) if score is not None else None,
                "status": self._status(completeness) if score is not None else "unknown",
                "completeness_percent": round(completeness, 4),
                "known_check_count": len(known),
                "intended_check_count": len(intended),
                "check_ids": [check.check_id for check in family_checks],
            }
        known_families = {
            name: payload
            for name, payload in families.items()
            if payload["score"] is not None
        }
        known_weight = sum(
            TECHNICAL_SEO_FAMILY_WEIGHTS[name] for name in known_families
        )
        score = (
            sum(
                float(payload["score"]) * TECHNICAL_SEO_FAMILY_WEIGHTS[name]
                for name, payload in known_families.items()
            )
            / known_weight
            if known_weight
            else None
        )
        completeness = sum(
            float(families[name]["completeness_percent"]) * weight
            for name, weight in TECHNICAL_SEO_FAMILY_WEIGHTS.items()
        )
        discovered = max(page_output.discovered_count, page_output.attempted_count, len(page_output.pages))
        attempted = max(page_output.attempted_count, len(page_output.pages))
        crawl_collection = min(1.0, attempted / discovered) if discovered else 0.0
        evidence_confidence = completeness / 100 * crawl_collection * 100
        warnings: list[str] = []
        if page_output.capped:
            warnings.append(
                f"Collection reached the {page_limit}-page ceiling; Technical SEO Health "
                "describes the collected site evidence, not every URL on the domain."
            )
        if not performance_evidence:
            warnings.append(
                "Field and lab performance evidence is unknown; performance was not "
                "inferred from HTML size or screenshots."
            )
        unknown_ids = [check.check_id for check in checks if check.status == "unknown"]
        if unknown_ids:
            warnings.append(
                f"{len(unknown_ids)} intended technical checks remain unknown: "
                + ", ".join(sorted(unknown_ids))
                + "."
            )
        recommendations = self._recommendations(checks)
        return ProductSurfaceResult(
            surface="technical_seo_health",
            version=PRODUCT_SURFACE_VERSIONS["technical_seo_health"],
            status=self._status(completeness) if score is not None else "unknown",
            score=round(score, 4) if score is not None else None,
            completeness_percent=round(completeness, 4),
            evidence_confidence=round(evidence_confidence, 4),
            families=families,
            checks=[check.to_dict() for check in checks],
            metrics={
                "eligible_page_count": len(pages),
                "collected_page_count": len(page_output.pages),
                "attempted_page_count": attempted,
                "discovered_page_count": discovered,
                "conclusive_error_count": sum(
                    1 for item in page_output.errors if item.get("conclusive")
                ),
                "crawl_capped": page_output.capped,
                "page_limit": page_limit,
                "evidence_confidence_version": EVIDENCE_CONFIDENCE_VERSION,
                "legacy_overall_score_affected": False,
            },
            recommendations=recommendations,
            warnings=warnings,
        )

    def _build_checks(
        self,
        crawl: CrawlDiscoveryOutput,
        page_output: PageAnalysisOutput,
        pages: list[PageRecord],
        *,
        attempt_id: str | None,
        performance_evidence: Mapping[str, Mapping[str, Any]] | None,
    ) -> list[ScoreCheckResult]:
        return [
            self._response_check(page_output, pages, attempt_id),
            self._redirect_check(pages),
            self._page_check(
                "robots_indexability",
                pages,
                lambda page: page.indexable is not True
                or "noindex" in (page.robots_meta or "").casefold(),
                "robots_meta",
                "Remove unintended noindex directives and confirm indexability.",
            ),
            self._page_check(
                "canonical_integrity",
                pages,
                self._canonical_failed,
                "canonical_url",
                "Add a valid same-site canonical that resolves to the intended page identity.",
            ),
            self._page_check(
                "metadata_completeness",
                self._eligible_pages("metadata_completeness", pages),
                lambda page: not (page.title and page.meta_description and page.h1),
                "title/meta_description/h1",
                "Provide unique, descriptive title, meta description, and H1 values.",
            ),
            self._page_check(
                "heading_integrity",
                self._eligible_pages("heading_integrity", pages),
                lambda page: page.ai_evidence.get("h1_count") != 1
                or page.ai_evidence.get("heading_hierarchy_valid") is not True,
                "ai_evidence.headings",
                "Use one clear H1 and a logical H2/H3 hierarchy.",
                unknown_if=lambda page: "h1_count" not in page.ai_evidence,
            ),
            self._page_check(
                "meaningful_text",
                self._eligible_pages("meaningful_text", pages),
                lambda page: (page.word_count or 0) < self._minimum_words(page),
                "word_count",
                "Expose enough meaningful HTTP-delivered text for the page purpose.",
            ),
            self._duplicate_check(self._eligible_pages("duplicate_template_risk", pages)),
            self._internal_link_check(page_output, pages, attempt_id),
            self._page_check(
                "navigation_discovery",
                self._eligible_pages("navigation_discovery", pages),
                lambda page: page.page_class != "homepage"
                and page.ai_evidence.get("in_navigation") is not True,
                "ai_evidence.in_navigation",
                "Link important service, location, and contact pages from primary navigation.",
                unknown_if=lambda page: "in_navigation" not in page.ai_evidence,
            ),
            self._sitemap_membership_check(crawl, pages),
            self._crawl_depth_check(
                self._eligible_pages("crawl_depth_orphan_risk", pages)
            ),
            self._page_check(
                "structured_data_alignment",
                self._eligible_pages("structured_data_alignment", pages),
                lambda page: page.ai_evidence.get("json_ld_valid") is not True
                or page.ai_evidence.get("json_ld_visible_alignment") is not True,
                "ai_evidence.json_ld_alignment",
                "Use valid JSON-LD that matches visible page facts.",
                unknown_if=lambda page: "json_ld_valid" not in page.ai_evidence,
            ),
            self._entity_consistency_check(
                self._eligible_pages("entity_fact_consistency", pages)
            ),
            self._page_check(
                "mobile_viewport",
                pages,
                lambda page: page.ai_evidence.get("mobile_viewport") is not True,
                "ai_evidence.mobile_viewport",
                "Declare a responsive mobile viewport on public HTML pages.",
                unknown_if=lambda page: "mobile_viewport" not in page.ai_evidence,
            ),
            PerformanceEvidenceService.build_field_page_experience_check(
                pages,
                performance_evidence,
            ),
        ]

    def _response_check(
        self,
        output: PageAnalysisOutput,
        pages: list[PageRecord],
        attempt_id: str | None,
    ) -> ScoreCheckResult:
        conclusive = [item for item in output.errors if item.get("conclusive")]
        ambiguous = [item for item in output.errors if not item.get("conclusive")]
        applicable = [page.id for page in pages] + [
            f"error:{index}" for index, _item in enumerate(conclusive)
        ]
        if not applicable:
            return self._unknown_or_inapplicable("response_eligibility", [], "unknown", [
                "No fetched page or conclusive HTTP response was available."
            ])
        affected = [f"error:{index}" for index, _item in enumerate(conclusive)]
        refs = [
            self._page_ref(page, "http_status", page.http_status)
            for page in pages
        ]
        if conclusive:
            refs.append(
                {
                    "artifact_path": self._checkpoint_path(attempt_id, "fetching_pages"),
                    "field": "payload.errors",
                    "reason": "Persisted conclusive internal HTTP failures.",
                    "observed": conclusive,
                }
            )
        ratio = len(affected) / len(applicable)
        confidence = len(applicable) / max(1, len(applicable) + len(ambiguous))
        return self._make_check(
            "response_eligibility",
            applicable,
            affected,
            ratio=ratio,
            confidence=confidence,
            refs=refs,
            limitations=(
                [f"{len(ambiguous)} ambiguous fetch failures were excluded from scoring."]
                if ambiguous
                else []
            ),
            remediation="Repair conclusive internal 4xx/5xx responses and preserve intended public URLs.",
        )

    def _redirect_check(self, pages: list[PageRecord]) -> ScoreCheckResult:
        redirected = [
            page
            for page in pages
            if self._normalize_url(str(page.fetch_metadata.get("fetched_url") or page.url))
            != self._normalize_url(page.url)
        ]
        if redirected:
            return self._unknown_or_inapplicable(
                "redirect_integrity",
                pages,
                "unknown",
                [
                    "Redirect destinations were observed, but redirect-chain length and "
                    "intermediate responses were not persisted."
                ],
            )
        return self._page_check(
            "redirect_integrity",
            pages,
            lambda _page: False,
            "fetch_metadata",
            "Keep redirects bounded, same-host, and pointed directly at canonical destinations.",
        )

    def _internal_link_check(
        self,
        output: PageAnalysisOutput,
        pages: list[PageRecord],
        attempt_id: str | None,
    ) -> ScoreCheckResult:
        conclusive = [item for item in output.errors if item.get("conclusive")]
        if output.capped and not conclusive:
            return self._unknown_or_inapplicable(
                "internal_link_health",
                pages,
                "unknown",
                ["The crawl cap left some discovered internal destinations unchecked."],
            )
        by_url = {self._normalize_url(page.url): page for page in pages}
        affected_ids = {
            by_url[self._normalize_url(str(item.get("source_url", "")))].id
            for item in conclusive
            if self._normalize_url(str(item.get("source_url", ""))) in by_url
        }
        refs = [self._page_ref(page, "internal_links", page.internal_links) for page in pages]
        if conclusive:
            refs.append(
                {
                    "artifact_path": self._checkpoint_path(attempt_id, "fetching_pages"),
                    "field": "payload.errors",
                    "reason": "Persisted conclusive internal link failures.",
                    "observed": conclusive,
                }
            )
        applicable = [page.id for page in pages]
        if not applicable:
            return self._unknown_or_inapplicable(
                "internal_link_health", [], "inapplicable", []
            )
        ratio = self._weighted_ratio(pages, affected_ids)
        return self._make_check(
            "internal_link_health",
            applicable,
            sorted(affected_ids),
            ratio=ratio,
            confidence=1.0,
            refs=refs,
            remediation="Repair conclusive internal 4xx/5xx destinations and update their source links.",
        )

    def _sitemap_membership_check(
        self,
        crawl: CrawlDiscoveryOutput,
        pages: list[PageRecord],
    ) -> ScoreCheckResult:
        eligible = self._eligible_pages("sitemap_membership", pages)
        state = sitemap_evidence_status(crawl)
        if state == "unknown":
            return self._unknown_or_inapplicable(
                "sitemap_membership",
                eligible,
                "unknown",
                ["Sitemap discovery was inconclusive."],
            )
        sitemap_identities = {
            self._normalize_url(url) for url in crawl.candidate_page_urls
        }
        return self._page_check(
            "sitemap_membership",
            eligible,
            lambda page: self._normalize_url(page.url) not in sitemap_identities,
            "url",
            "Include canonical, indexable commercial and supporting pages in a valid sitemap.",
        )

    def _crawl_depth_check(self, pages: list[PageRecord]) -> ScoreCheckResult:
        if pages and all("crawl_depth" not in page.fetch_metadata for page in pages):
            return self._unknown_or_inapplicable(
                "crawl_depth_orphan_risk",
                pages,
                "unknown",
                ["Crawl depth was not persisted for the collected pages."],
            )
        return self._page_check(
            "crawl_depth_orphan_risk",
            pages,
            lambda page: int(page.fetch_metadata.get("crawl_depth", 99)) > 3
            or (
                page.ai_evidence.get("in_navigation") is not True
                and page.ai_evidence.get("in_sitemap") is not True
            ),
            "fetch_metadata.crawl_depth",
            "Move important pages within three internal-link steps and expose them in navigation or sitemaps.",
        )

    def _duplicate_check(self, pages: list[PageRecord]) -> ScoreCheckResult:
        if not pages:
            return self._unknown_or_inapplicable(
                "duplicate_template_risk",
                [],
                "inapplicable",
                [],
            )
        clusters: dict[str, list[PageRecord]] = {}
        for page in pages:
            key = page.duplicate_cluster_key
            if not key:
                title = " ".join((page.title or "").casefold().split())
                h1 = " ".join((page.h1 or "").casefold().split())
                if title and h1:
                    key = f"{title}|{h1}"
            if key:
                clusters.setdefault(key, []).append(page)
        affected = {
            page.id
            for cluster in clusters.values()
            if len({self._normalize_url(page.url) for page in cluster}) > 1
            for page in cluster
        }
        if pages and not clusters:
            return self._unknown_or_inapplicable(
                "duplicate_template_risk",
                pages,
                "unknown",
                ["No stable template/title identity was available for duplicate comparison."],
            )
        return self._make_check(
            "duplicate_template_risk",
            [page.id for page in pages],
            sorted(affected),
            ratio=self._weighted_ratio(pages, affected),
            confidence=1.0,
            refs=[
                self._page_ref(
                    page,
                    "duplicate_cluster_key/title/h1",
                    {
                        "duplicate_cluster_key": page.duplicate_cluster_key,
                        "title": page.title,
                        "h1": page.h1,
                    },
                )
                for page in pages
            ],
            remediation="Differentiate duplicate templates and consolidate pages that serve the same intent.",
        )

    def _entity_consistency_check(self, pages: list[PageRecord]) -> ScoreCheckResult:
        names = [
            self._normalize_entity(str(name))
            for page in pages
            for name in page.ai_evidence.get("entity_names", [])
            if str(name).strip()
        ]
        if not names:
            return self._unknown_or_inapplicable(
                "entity_fact_consistency",
                pages,
                "unknown",
                ["No validated Organization or LocalBusiness identity was observed."],
            )
        dominant = Counter(names).most_common(1)[0][0]
        return self._page_check(
            "entity_fact_consistency",
            pages,
            lambda page: dominant
            not in {
                self._normalize_entity(str(name))
                for name in page.ai_evidence.get("entity_names", [])
            },
            "ai_evidence.entity_names",
            "Align visible and structured business identity across home, location, and contact pages.",
        )

    def _page_check(
        self,
        check_id: str,
        pages: list[PageRecord],
        failed: Callable[[PageRecord], bool],
        evidence_field: str,
        remediation: str,
        *,
        unknown_if: Callable[[PageRecord], bool] | None = None,
    ) -> ScoreCheckResult:
        if not pages:
            return self._unknown_or_inapplicable(check_id, [], "inapplicable", [])
        if unknown_if is not None and all(unknown_if(page) for page in pages):
            return self._unknown_or_inapplicable(
                check_id,
                pages,
                "unknown",
                [f"{check_id} evidence was not persisted for applicable pages."],
            )
        known = [
            page for page in pages if unknown_if is None or not unknown_if(page)
        ]
        affected = {page.id for page in known if failed(page)}
        ratio = self._weighted_ratio(known, affected)
        confidence = (
            sum(self._importance(page) for page in known)
            / sum(self._importance(page) for page in pages)
        )
        refs = [
            self._page_ref(
                page,
                evidence_field,
                self._resolve_field(page, evidence_field),
            )
            for page in known
        ]
        return self._make_check(
            check_id,
            [page.id for page in pages],
            sorted(affected),
            ratio=ratio,
            confidence=confidence,
            refs=refs,
            limitations=(
                []
                if len(known) == len(pages)
                else [f"{check_id} was observed for {len(known)} of {len(pages)} applicable pages."]
            ),
            remediation=remediation,
        )

    def _make_check(
        self,
        check_id: str,
        applicable_ids: list[str],
        affected_ids: list[str],
        *,
        ratio: float,
        confidence: float,
        refs: list[dict[str, Any]],
        remediation: str,
        limitations: list[str] | None = None,
    ) -> ScoreCheckResult:
        registry = TECHNICAL_SEO_CHECK_REGISTRY[check_id]
        return ScoreCheckResult(
            check_id=check_id,
            check_version=int(registry["version"]),
            family=str(registry["family"]),
            severity=str(registry["severity"]),
            status="failed" if affected_ids else "measured",
            score_affecting=bool(registry["score_affecting"]),
            applicable_page_ids=applicable_ids,
            affected_page_ids=affected_ids,
            weighted_affected_ratio=round(ratio, 6),
            evidence_confidence=round(confidence, 6),
            score=round((1 - ratio) * 100, 4),
            evidence_refs=refs,
            limitations=limitations or [],
            remediation=remediation,
        )

    def _unknown_or_inapplicable(
        self,
        check_id: str,
        pages: list[PageRecord],
        status: str,
        limitations: list[str],
    ) -> ScoreCheckResult:
        registry = TECHNICAL_SEO_CHECK_REGISTRY[check_id]
        return ScoreCheckResult(
            check_id=check_id,
            check_version=int(registry["version"]),
            family=str(registry["family"]),
            severity=str(registry["severity"]),
            status=status,
            score_affecting=bool(registry["score_affecting"]),
            applicable_page_ids=[page.id for page in pages] if status == "unknown" else [],
            limitations=limitations,
        )

    @staticmethod
    def _eligible_pages(check_id: str, pages: list[PageRecord]) -> list[PageRecord]:
        classes = set(TECHNICAL_SEO_CHECK_REGISTRY[check_id]["page_classes"])
        return pages if "*" in classes else [page for page in pages if page.page_class in classes]

    @staticmethod
    def _canonical_failed(page: PageRecord) -> bool:
        if not page.canonical_url:
            return True
        page_host = (urlsplit(page.url).hostname or "").casefold().removeprefix("www.")
        canonical_host = (
            urlsplit(page.canonical_url).hostname or ""
        ).casefold().removeprefix("www.")
        return page_host != canonical_host

    @staticmethod
    def _minimum_words(page: PageRecord) -> int:
        if page.page_class == "contact_about":
            return 50
        if page.page_class in {"blog_resource", "project_case_study"}:
            return 250
        return 150

    @staticmethod
    def _importance(page: PageRecord) -> float:
        return PAGE_IMPORTANCE.get(page.page_class or "", 0.60)

    def _weighted_ratio(self, pages: list[PageRecord], affected_ids: set[str]) -> float:
        denominator = sum(self._importance(page) for page in pages)
        if not denominator:
            return 0.0
        return (
            sum(self._importance(page) for page in pages if page.id in affected_ids)
            / denominator
        )

    @staticmethod
    def _page_ref(page: PageRecord, field: str, observed: Any) -> dict[str, Any]:
        return {
            "artifact_path": f"pages/{page.id}.json",
            "field": field,
            "reason": "Persisted page evidence used by Technical SEO Health.",
            "observed": observed,
        }

    @staticmethod
    def _resolve_field(page: PageRecord, field: str) -> Any:
        if "/" in field:
            return {name: TechnicalSEOHealthService._resolve_field(page, name) for name in field.split("/")}
        value: Any = page.to_dict()
        for part in field.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    @staticmethod
    def _checkpoint_path(attempt_id: str | None, stage: str) -> str:
        return (
            f"checkpoints/{attempt_id}/{stage}.json"
            if attempt_id
            else f"checkpoints/{stage}.json"
        )

    @staticmethod
    def _normalize_url(value: str) -> str:
        if not value:
            return ""
        parsed = urlsplit(value)
        host = (parsed.hostname or "").casefold().removeprefix("www.").rstrip(".")
        path = parsed.path or "/"
        if path != "/":
            path = path.rstrip("/")
        return urlunsplit(("", host, path, parsed.query, ""))

    @staticmethod
    def _normalize_entity(value: str) -> str:
        return " ".join(value.casefold().split())

    @staticmethod
    def _status(completeness: float) -> str:
        return "complete" if completeness >= 85 else "partial" if completeness >= 50 else "limited"

    @staticmethod
    def _recommendations(checks: list[ScoreCheckResult]) -> list[dict[str, Any]]:
        ranked = sorted(
            (
                (
                    TECHNICAL_SEO_SEVERITY_WEIGHTS[check.severity]
                    * float(check.weighted_affected_ratio or 0)
                    * float(check.evidence_confidence or 0),
                    check,
                )
                for check in checks
                if check.status == "failed" and check.remediation
            ),
            key=lambda item: (-item[0], item[1].check_id),
        )
        return [
            {
                "check_id": check.check_id,
                "severity": check.severity,
                "affected_page_count": len(check.affected_page_ids),
                "action": check.remediation,
                "priority_basis": round(priority, 6),
                "evidence_refs": check.evidence_refs[:5],
            }
            for priority, check in ranked[:3]
        ]
