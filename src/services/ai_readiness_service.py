from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable
from urllib.parse import urlsplit

from src.models import AI_READINESS_V3_VERSION, PageRecord
from src.services.crawl_discovery_service import CrawlDiscoveryOutput
from src.services.page_analysis_service import PageAnalysisOutput
from src.services.search_intelligence_service import (
    SearchIntelligenceOutput,
    corroborated_external_mentions,
)


SCORE_VERSION = "ai-readiness.v2"
V3_SCORE_VERSION = AI_READINESS_V3_VERSION
DIMENSION_WEIGHTS = {"aeo": 40.0, "geo": 35.0, "aio": 25.0}
COHORT_WEIGHTS = {"core": 60.0, "supporting": 40.0}
CORE_CLASSES = {"homepage", "service", "location", "service_location", "contact_about"}
UTILITY_CLASSES = {"legal_utility", "low_value"}


@dataclass(slots=True)
class AIReadinessOutput:
    score_version: str = SCORE_VERSION
    score: float | None = None
    band: str | None = None
    completeness_percent: float = 0.0
    status: str = "limited"
    presentation_label: str | None = None
    customer_claim_eligible: bool = False
    dimensions: dict[str, Any] = field(default_factory=dict)
    cohorts: dict[str, Any] = field(default_factory=dict)
    inventory: dict[str, Any] = field(default_factory=dict)
    broken_links: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AIReadinessService:
    """Deterministic readiness scoring; it does not measure AI citations."""

    CHECK_WEIGHTS = {
        "aeo": {
            "direct_answers": 30.0,
            "heading_hierarchy": 20.0,
            "structured_blocks": 25.0,
            "conversational_followups": 25.0,
        },
        "geo": {
            "entity_identity": 25.0,
            "author_attribution": 20.0,
            "cited_sources": 20.0,
            "specific_fresh_evidence": 15.0,
            "external_corroboration": 20.0,
        },
        "aio": {
            "crawl_index_eligibility": 30.0,
            "crawler_access": 20.0,
            "text_accessibility": 20.0,
            "link_health": 15.0,
            "structured_data_alignment": 15.0,
        },
    }

    def build(
        self,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        *,
        page_limit: int,
    ) -> AIReadinessOutput:
        eligible = [
            page for page in pages.pages
            if page.fetch_status == "fetched" and page.page_class not in UTILITY_CLASSES
        ]
        core = [
            page for page in eligible
            if page.page_class in CORE_CLASSES or bool(page.ai_evidence.get("in_navigation"))
        ]
        supporting = [page for page in eligible if page not in core]
        cohorts = {
            "core": self._score_cohort(core, crawl, pages, search),
            "supporting": self._score_cohort(supporting, crawl, pages, search),
        }
        available = {name: data for name, data in cohorts.items() if data["score"] is not None}
        score = self._weighted_known(
            {name: float(data["score"]) for name, data in available.items()},
            COHORT_WEIGHTS,
        )
        completeness = self._weighted_known(
            {name: float(data["completeness_percent"]) for name, data in cohorts.items()},
            COHORT_WEIGHTS,
            missing_as_zero=True,
        ) or 0.0
        dimensions: dict[str, Any] = {}
        for dimension in DIMENSION_WEIGHTS:
            known = {
                name: data["dimensions"][dimension]["score"]
                for name, data in available.items()
                if data["dimensions"][dimension]["score"] is not None
            }
            dimensions[dimension] = {
                "score": self._weighted_known(known, COHORT_WEIGHTS),
                "description": self._description(dimension),
            }
        broken = self._broken_links(pages)
        warnings = []
        if not supporting:
            warnings.append("No supporting-page evidence was collected; the supporting score is unknown.")
        attempted = max(pages.attempted_count, len(pages.pages))
        discovered = max(
            attempted,
            pages.discovered_count,
            len({*crawl.candidate_page_urls, *(p.url for p in pages.pages)}),
        )
        capped = bool(pages.capped)
        if capped:
            warnings.append(f"Collection reached the {page_limit}-page safety ceiling.")
        if not self._mention_score(search)[1]:
            warnings.append("External brand corroboration is unknown; paid evidence was not available.")
        recommendations = self._recommendations(cohorts, broken)
        return AIReadinessOutput(
            score=score,
            band=self._band(score),
            completeness_percent=round(completeness, 2),
            status=self._status(completeness),
            presentation_label=self._presentation_label(score, completeness),
            customer_claim_eligible=completeness >= 85,
            dimensions=dimensions,
            cohorts=cohorts,
            inventory={
                "collected_pages": len(pages.pages),
                "attempted_pages": attempted,
                "eligible_pages": len(eligible),
                "discovered_pages": discovered,
                "duplicate_alias_count": len(pages.duplicate_aliases),
                "core_pages": len(core),
                "supporting_pages": len(supporting),
                "page_limit": page_limit,
                "capped": capped,
            },
            broken_links=broken,
            recommendations=recommendations,
            warnings=warnings,
        )

    def _score_cohort(
        self,
        pages: list[PageRecord],
        crawl: CrawlDiscoveryOutput,
        page_output: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
    ) -> dict[str, Any]:
        if not pages:
            return {
                "score": None, "completeness_percent": 0.0, "status": "limited",
                "dimensions": {name: {"score": None, "completeness_percent": 0.0, "checks": []} for name in DIMENSION_WEIGHTS},
            }
        checks = {
            "aeo": [
                self._page_ratio("direct_answers", pages, lambda e: bool(e.get("direct_answer_count"))),
                self._page_ratio("heading_hierarchy", pages, lambda e: bool(e.get("heading_hierarchy_valid"))),
                self._page_ratio(
                    "structured_blocks",
                    pages,
                    lambda e: int(
                        e.get(
                            "structured_block_count",
                            int(e.get("list_count", 0)) + int(e.get("table_count", 0)),
                        )
                    ) > 0,
                ),
                self._page_ratio("conversational_followups", pages, lambda e: int(e.get("question_heading_count", 0)) >= 2),
            ],
            "geo": [
                self._page_ratio("entity_identity", pages, lambda e: bool(e.get("entity_names"))),
                self._page_ratio(
                    "author_attribution",
                    pages,
                    lambda e: bool(e.get("author_names")),
                    applicable=lambda page: page.page_class in {"blog_resource", "project_case_study"},
                ),
                self._page_ratio(
                    "cited_sources",
                    pages,
                    lambda e: int(e.get("external_citation_count", 0)) > 0,
                    applicable=lambda page: page.page_class in {"blog_resource", "project_case_study"},
                ),
                self._page_ratio(
                    "specific_fresh_evidence",
                    pages,
                    lambda e: bool(e.get("published_dates"))
                    or int(e.get("specific_evidence_count", 0)) > 0,
                    applicable=lambda page: page.page_class in {
                        "service",
                        "location",
                        "service_location",
                        "blog_resource",
                        "project_case_study",
                    },
                ),
                self._mention_check(search),
            ],
            "aio": [
                self._page_ratio("crawl_index_eligibility", pages, lambda _e, p=None: True, page_predicate=lambda p: p.http_status == 200 and p.indexable is True and "nosnippet" not in (p.robots_meta or "").casefold()),
                self._crawler_check(crawl),
                self._page_ratio("text_accessibility", pages, lambda _e, p=None: True, page_predicate=lambda p: (p.word_count or 0) >= 100),
                self._link_health_check(pages, page_output),
                self._page_ratio("structured_data_alignment", pages, lambda e: bool(e.get("json_ld_valid")) and bool(e.get("json_ld_visible_alignment"))),
            ],
        }
        dimensions: dict[str, Any] = {}
        for dimension, dimension_checks in checks.items():
            weights = self.CHECK_WEIGHTS[dimension]
            known = {item["id"]: item["score"] for item in dimension_checks if item["status"] == "measured"}
            score = self._weighted_known(known, weights)
            applicable_checks = [
                item for item in dimension_checks if item["status"] != "inapplicable"
            ]
            applicable_weight = sum(weights[item["id"]] for item in applicable_checks)
            measured_weight = sum(
                weights[item["id"]]
                for item in applicable_checks
                if item["status"] == "measured"
            )
            completeness = (
                measured_weight / applicable_weight * 100
                if applicable_weight
                else 100.0
            )
            dimensions[dimension] = {
                "score": score,
                "completeness_percent": round(completeness, 2),
                "checks": dimension_checks,
            }
        score = self._weighted_known(
            {name: data["score"] for name, data in dimensions.items() if data["score"] is not None},
            DIMENSION_WEIGHTS,
        )
        completeness = sum(
            DIMENSION_WEIGHTS[name] * data["completeness_percent"] / 100
            for name, data in dimensions.items()
        )
        return {
            "score": score,
            "completeness_percent": round(completeness, 2),
            "status": self._status(completeness),
            "dimensions": dimensions,
        }

    @staticmethod
    def _page_ratio(
        check_id: str,
        pages: list[PageRecord],
        evidence_predicate,
        *,
        page_predicate=None,
        applicable=None,
    ) -> dict[str, Any]:
        applicable_pages = [
            page for page in pages if applicable is None or applicable(page)
        ]
        if not applicable_pages:
            return {
                "id": check_id,
                "score": None,
                "status": "inapplicable",
                "observation": "This check is not applicable to the collected page classes.",
                "evidence_refs": [],
            }
        passed = 0
        for page in applicable_pages:
            if page_predicate(page) if page_predicate else evidence_predicate(page.ai_evidence):
                passed += 1
        score = round(passed / len(applicable_pages) * 100, 2)
        return {
            "id": check_id, "score": score, "status": "measured",
            "observation": f"{passed} of {len(applicable_pages)} applicable pages passed.",
            "evidence_refs": [
                {
                    "artifact_path": f"pages/{page.id}.json",
                    "field": AIReadinessService._check_field(check_id, page),
                    "reason": f"Persisted page evidence for {check_id}.",
                    "observed": AIReadinessService._resolve_page_field(
                        page,
                        AIReadinessService._check_field(check_id, page),
                    ),
                }
                for page in applicable_pages[:10]
            ],
        }

    def _mention_check(self, search: SearchIntelligenceOutput) -> dict[str, Any]:
        score, measured = self._mention_score(search)
        corroborated = corroborated_external_mentions(search)
        return {
            "id": "external_corroboration",
            "score": score if measured else None,
            "status": "measured" if measured else "unknown",
            "observation": (
                f"{len(corroborated)} external search results corroborated the entity and site topic."
                if measured else "External corroboration was not collected."
            ),
            "evidence_refs": [],
            "evidence_observed": (
                corroborated
                if "external_mentions" in search.payload
                else search.payload
            ),
            "evidence_field": (
                "payload.payload.external_mentions"
                if "external_mentions" in search.payload
                else "payload.payload"
            ),
        }

    @staticmethod
    def _mention_score(search: SearchIntelligenceOutput) -> tuple[float, bool]:
        mention_queries = search.payload.get("mention_queries")
        external_mentions = search.payload.get("external_mentions", [])
        provider_errors = search.payload.get("provider_errors", [])
        mention_failed = any(
            isinstance(item, dict) and item.get("operation") == "external_mention_serp"
            for item in provider_errors
        )
        if (
            not search.approved
            or "external_mentions" not in search.payload
            or not (
                (isinstance(mention_queries, list) and bool(mention_queries))
                or (mention_queries is None and bool(external_mentions))
            )
            or mention_failed
        ):
            return 0.0, False
        count = len(corroborated_external_mentions(search))
        return min(100.0, count * 25.0), True

    @staticmethod
    def _crawler_check(crawl: CrawlDiscoveryOutput) -> dict[str, Any]:
        rules = crawl.robots_access
        if not rules:
            return {"id": "crawler_access", "score": None, "status": "unknown", "observation": "Crawler rules are unknown.", "evidence_refs": [], "evidence_observed": rules}
        values = [rules.get(name) for name in ("googlebot", "bingbot", "oai-searchbot")]
        known = [value for value in values if isinstance(value, bool)]
        if not known:
            return {"id": "crawler_access", "score": None, "status": "unknown", "observation": "Crawler rules are unknown.", "evidence_refs": [], "evidence_observed": rules}
        score = round(sum(1 for value in known if value) / len(known) * 100, 2)
        return {"id": "crawler_access", "score": score, "status": "measured", "observation": f"{sum(known)} of {len(known)} checked crawlers are allowed.", "evidence_refs": [], "evidence_observed": rules}

    @staticmethod
    def _link_health_check(pages: list[PageRecord], output: PageAnalysisOutput) -> dict[str, Any]:
        conclusive = [item for item in output.errors if item.get("conclusive")]
        if output.capped and not conclusive:
            return {
                "id": "link_health",
                "score": None,
                "status": "unknown",
                "observation": "The crawl cap left internal link destinations unchecked.",
                "evidence_refs": [],
                "evidence_observed": output.errors,
            }
        total = sum(len(page.internal_links) for page in pages)
        score = 100.0 if not conclusive else max(0.0, round(100 - len(conclusive) / max(1, total) * 100, 2))
        return {"id": "link_health", "score": score, "status": "measured", "observation": f"{len(conclusive)} conclusive internal link failures.", "evidence_refs": [], "evidence_observed": output.errors}

    @staticmethod
    def _broken_links(output: PageAnalysisOutput) -> list[dict[str, Any]]:
        return [dict(item) for item in output.errors if item.get("conclusive")]

    @staticmethod
    def _weighted_known(values: dict[str, float], weights: dict[str, float], *, missing_as_zero: bool = False) -> float | None:
        if missing_as_zero:
            denominator = sum(weights.values())
            return round(sum(values.get(key, 0.0) * weight for key, weight in weights.items()) / denominator, 2)
        known = {key: value for key, value in values.items() if key in weights and value is not None}
        denominator = sum(weights[key] for key in known)
        if not denominator:
            return None
        return round(sum(float(value) * weights[key] for key, value in known.items()) / denominator, 2)

    @staticmethod
    def _status(completeness: float) -> str:
        return "complete" if completeness >= 85 else "partial" if completeness >= 50 else "limited"

    @staticmethod
    def _band(score: float | None) -> str | None:
        if score is None:
            return None
        return "Needs foundational work" if score < 40 else "Developing" if score < 60 else "Solid" if score < 80 else "Strong"

    @classmethod
    def _presentation_label(cls, score: float | None, completeness: float) -> str | None:
        band = cls._band(score)
        if band is None:
            return None
        return band if completeness >= 85 else f"Provisional — {band}"

    @staticmethod
    def _check_field(check_id: str, page: PageRecord) -> str:
        fields = {
            "direct_answers": "ai_evidence.direct_answer_count",
            "heading_hierarchy": "ai_evidence.heading_hierarchy_valid",
            "structured_blocks": "ai_evidence.structured_block_count",
            "conversational_followups": "ai_evidence.question_heading_count",
            "entity_identity": "ai_evidence.entity_names",
            "author_attribution": "ai_evidence.author_names",
            "cited_sources": "ai_evidence.external_citation_count",
            "specific_fresh_evidence": "ai_evidence.specific_evidence_count",
            "crawl_index_eligibility": "http_status",
            "text_accessibility": "word_count",
            "structured_data_alignment": "ai_evidence.json_ld_visible_alignment",
        }
        field = fields[check_id]
        if check_id == "structured_blocks" and "structured_block_count" not in page.ai_evidence:
            return (
                "ai_evidence.list_count"
                if "list_count" in page.ai_evidence
                else "ai_evidence"
            )
        if check_id == "specific_fresh_evidence" and "specific_evidence_count" not in page.ai_evidence:
            return (
                "ai_evidence.published_dates"
                if "published_dates" in page.ai_evidence
                else "ai_evidence"
            )
        if field.startswith("ai_evidence."):
            key = field.split(".", 1)[1]
            if key not in page.ai_evidence:
                return "ai_evidence"
        return field

    @staticmethod
    def _resolve_page_field(page: PageRecord, field: str) -> Any:
        value: Any = page.to_dict()
        for part in field.split("."):
            value = value[part]
        return value

    @staticmethod
    def _description(name: str) -> str:
        return {
            "aeo": "Answer Readiness: concise, structured answers and follow-up coverage.",
            "geo": "Entity and Source Authority: identity, attribution, sources, freshness, and corroboration.",
            "aio": "AI Accessibility: crawl, index, text, link, and structured-data accessibility.",
        }[name]

    @staticmethod
    def _recommendations(cohorts: dict[str, Any], broken: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates: list[tuple[float, str, str]] = []
        labels = {
            "direct_answers": ("Front-load direct answers", "Add a concise 2–3 sentence answer immediately after relevant headings."),
            "heading_hierarchy": ("Repair heading hierarchy", "Use one clear H1 and logical H2/H3 nesting."),
            "structured_blocks": ("Add extractable structures", "Use useful lists and real HTML tables where the content warrants them."),
            "conversational_followups": ("Cover follow-up questions", "Add natural-language questions that address the next likely intent."),
            "entity_identity": ("Clarify the business entity", "Align visible business facts with Organization or LocalBusiness JSON-LD."),
            "author_attribution": ("Add accountable authorship", "Attribute expert content to a named person with a useful bio."),
            "cited_sources": ("Support claims with sources", "Cite reliable external sources and label first-party evidence."),
            "specific_fresh_evidence": ("Add dated first-party proof", "Publish specific examples, dates, methods, and quantified evidence."),
            "crawler_access": ("Review crawler access", "Confirm Googlebot, Bingbot, and OAI-SearchBot can access intended public pages."),
            "text_accessibility": ("Expose meaningful text", "Ensure important content is present in the HTTP-delivered HTML."),
            "link_health": ("Repair broken internal links", "Fix conclusive internal 4xx/5xx destinations."),
            "structured_data_alignment": ("Align structured data", "Use valid JSON-LD that matches visible page facts."),
        }
        for cohort in cohorts.values():
            for dimension in cohort.get("dimensions", {}).values():
                for check in dimension.get("checks", []):
                    if check.get("score") is not None and check["id"] in labels:
                        title, action = labels[check["id"]]
                        candidates.append((float(check["score"]), title, action))
        if broken:
            candidates.append((0.0, "Repair broken internal links", "Fix conclusive internal 4xx/5xx destinations."))
        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for score, title, action in sorted(candidates, key=lambda item: (item[0], item[1])):
            if title in seen:
                continue
            seen.add(title)
            unique.append({"title": title, "action": action, "score": score})
            if len(unique) == 3:
                break
        return unique


class AIReadinessV3Service(AIReadinessService):
    """Applicability-aware continuous scoring over the same bounded crawl."""

    def build(
        self,
        crawl: CrawlDiscoveryOutput,
        pages: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        *,
        page_limit: int,
        attempt_id: str | None = None,
    ) -> AIReadinessOutput:
        eligible = [
            page
            for page in pages.pages
            if page.fetch_status == "fetched" and page.page_class not in UTILITY_CLASSES
        ]
        core = [
            page
            for page in eligible
            if page.page_class in CORE_CLASSES
            or bool(page.ai_evidence.get("in_navigation"))
        ]
        supporting = [page for page in eligible if page not in core]
        cohorts = {
            "core": self._score_cohort_v3(
                core,
                crawl,
                pages,
                search,
                attempt_id=attempt_id,
            ),
            "supporting": self._score_cohort_v3(
                supporting,
                crawl,
                pages,
                search,
                attempt_id=attempt_id,
            ),
        }
        available = {
            name: data for name, data in cohorts.items() if data["score"] is not None
        }
        score = self._weighted_known(
            {name: float(data["score"]) for name, data in available.items()},
            COHORT_WEIGHTS,
        )
        completeness = self._weighted_known(
            {
                name: float(data["completeness_percent"])
                for name, data in cohorts.items()
            },
            COHORT_WEIGHTS,
            missing_as_zero=True,
        ) or 0.0
        dimensions: dict[str, Any] = {}
        for dimension in DIMENSION_WEIGHTS:
            known = {
                name: data["dimensions"][dimension]["score"]
                for name, data in available.items()
                if data["dimensions"][dimension]["score"] is not None
            }
            dimensions[dimension] = {
                "score": self._weighted_known(known, COHORT_WEIGHTS),
                "description": self._description(dimension),
                "completeness_percent": self._weighted_known(
                    {
                        name: float(data["dimensions"][dimension]["completeness_percent"])
                        for name, data in cohorts.items()
                    },
                    COHORT_WEIGHTS,
                    missing_as_zero=True,
                )
                or 0.0,
            }
        broken = self._broken_links(pages)
        attempted = max(pages.attempted_count, len(pages.pages))
        discovered = max(
            attempted,
            pages.discovered_count,
            len({*crawl.candidate_page_urls, *(page.url for page in pages.pages)}),
        )
        capped = bool(pages.capped)
        warnings: list[str] = []
        if not supporting:
            warnings.append(
                "No supporting-page evidence was collected; the supporting score is unknown."
            )
        if capped:
            warnings.append(
                f"Collection reached the {page_limit}-page safety ceiling; readiness "
                "describes collected evidence."
            )
        if not self._mention_score_v3(search)[1]:
            warnings.append(
                "External brand corroboration is unknown; missing paid evidence did not lower the score."
            )
        if any(
            check.get("id") == "text_accessibility"
            and check.get("completeness_percent", 0) < 100
            for cohort in cohorts.values()
            for check in cohort.get("dimensions", {}).get("aio", {}).get("checks", [])
        ):
            warnings.append(
                "Rendered-text parity was not available for every applicable page; "
                "HTTP main-content evidence was scored without inferring rendered behavior."
            )
        minimum_dimension = min(
            (
                float(payload["score"])
                for payload in dimensions.values()
                if payload.get("score") is not None
            ),
            default=0.0,
        )
        all_dimensions_known = all(
            payload.get("score") is not None for payload in dimensions.values()
        )
        customer_claim_eligible = bool(
            score is not None
            and completeness >= 85
            and all_dimensions_known
            and minimum_dimension >= 40
            and not capped
        )
        return AIReadinessOutput(
            score_version=V3_SCORE_VERSION,
            score=score,
            band=self._band(score),
            completeness_percent=round(completeness, 2),
            status=self._status(completeness),
            presentation_label=self._presentation_label(score, completeness),
            customer_claim_eligible=customer_claim_eligible,
            dimensions=dimensions,
            cohorts=cohorts,
            inventory={
                "collected_pages": len(pages.pages),
                "attempted_pages": attempted,
                "eligible_pages": len(eligible),
                "discovered_pages": discovered,
                "duplicate_alias_count": len(pages.duplicate_aliases),
                "core_pages": len(core),
                "supporting_pages": len(supporting),
                "page_limit": page_limit,
                "capped": capped,
                "applicability_contract": "page-class.v3",
            },
            broken_links=broken,
            recommendations=self._recommendations(cohorts, broken),
            warnings=warnings,
        )

    def _score_cohort_v3(
        self,
        pages: list[PageRecord],
        crawl: CrawlDiscoveryOutput,
        page_output: PageAnalysisOutput,
        search: SearchIntelligenceOutput,
        *,
        attempt_id: str | None,
    ) -> dict[str, Any]:
        if not pages:
            return {
                "score": None,
                "completeness_percent": 0.0,
                "status": "limited",
                "dimensions": {
                    name: {
                        "score": None,
                        "completeness_percent": 0.0,
                        "checks": [],
                    }
                    for name in DIMENSION_WEIGHTS
                },
            }
        checks = {
            "aeo": [
                self._continuous_page_check(
                    "direct_answers",
                    pages,
                    self._direct_answer_page_score,
                    applicable=lambda page: bool(self._answerable_headings(page)),
                    field="ai_evidence.direct_answer_blocks",
                ),
                self._continuous_page_check(
                    "heading_hierarchy",
                    pages,
                    self._heading_page_score,
                    applicable=lambda page: "headings" in page.ai_evidence,
                    field="ai_evidence.headings",
                ),
                self._continuous_page_check(
                    "structured_blocks",
                    pages,
                    self._structured_page_score,
                    applicable=lambda page: bool(self._answerable_headings(page)),
                    field="ai_evidence.structured_block_count",
                ),
                self._intent_followup_check(
                    pages,
                    search,
                    attempt_id=attempt_id,
                ),
            ],
            "geo": [
                self._entity_consistency_check_v3(pages),
                self._continuous_page_check(
                    "author_attribution",
                    pages,
                    lambda page: (
                        100.0 if page.ai_evidence.get("author_names") else 0.0,
                        100.0,
                    ),
                    applicable=lambda page: page.page_class
                    in {"blog_resource", "project_case_study"},
                    field="ai_evidence.author_names",
                ),
                self._continuous_page_check(
                    "cited_sources",
                    pages,
                    lambda page: (
                        min(
                            100.0,
                            float(page.ai_evidence.get("external_citation_count", 0))
                            / 2
                            * 100,
                        ),
                        100.0,
                    ),
                    applicable=lambda page: page.page_class
                    in {"blog_resource", "project_case_study"},
                    field="ai_evidence.external_citations",
                ),
                self._continuous_page_check(
                    "specific_fresh_evidence",
                    pages,
                    self._specific_fresh_page_score,
                    applicable=lambda page: page.page_class
                    in {
                        "service",
                        "location",
                        "service_location",
                        "blog_resource",
                        "project_case_study",
                    },
                    field="ai_evidence.specific_evidence_excerpts",
                ),
                self._mention_check_v3(search),
            ],
            "aio": [
                self._continuous_page_check(
                    "crawl_index_eligibility",
                    pages,
                    lambda page: (
                        100.0
                        if page.http_status == 200
                        and page.indexable is True
                        and "nosnippet" not in (page.robots_meta or "").casefold()
                        else 0.0,
                        100.0,
                    ),
                    applicable=lambda _page: True,
                    field="http_status",
                ),
                self._crawler_check(crawl),
                self._continuous_page_check(
                    "text_accessibility",
                    pages,
                    self._text_accessibility_page_score,
                    applicable=lambda page: "main_content_word_count"
                    in page.ai_evidence,
                    field="ai_evidence.main_content_word_count",
                ),
                self._link_health_check(pages, page_output),
                self._continuous_page_check(
                    "structured_data_alignment",
                    pages,
                    self._schema_alignment_page_score,
                    applicable=lambda page: "json_ld_valid" in page.ai_evidence,
                    field="ai_evidence.json_ld_alignment",
                ),
            ],
        }
        dimensions: dict[str, Any] = {}
        for dimension, dimension_checks in checks.items():
            weights = self.CHECK_WEIGHTS[dimension]
            known = {
                item["id"]: item["score"]
                for item in dimension_checks
                if item.get("score") is not None
            }
            score = self._weighted_known(known, weights)
            applicable_checks = [
                item for item in dimension_checks if item["status"] != "inapplicable"
            ]
            applicable_weight = sum(weights[item["id"]] for item in applicable_checks)
            completeness_weight = sum(
                weights[item["id"]]
                * float(item.get("completeness_percent", 0))
                / 100
                for item in applicable_checks
            )
            completeness = (
                completeness_weight / applicable_weight * 100
                if applicable_weight
                else 100.0
            )
            dimensions[dimension] = {
                "score": score,
                "completeness_percent": round(completeness, 2),
                "checks": dimension_checks,
            }
        score = self._weighted_known(
            {
                name: data["score"]
                for name, data in dimensions.items()
                if data["score"] is not None
            },
            DIMENSION_WEIGHTS,
        )
        completeness = sum(
            DIMENSION_WEIGHTS[name] * data["completeness_percent"] / 100
            for name, data in dimensions.items()
        )
        return {
            "score": score,
            "completeness_percent": round(completeness, 2),
            "status": self._status(completeness),
            "dimensions": dimensions,
        }

    def _continuous_page_check(
        self,
        check_id: str,
        pages: list[PageRecord],
        scorer,
        *,
        applicable,
        field: str,
    ) -> dict[str, Any]:
        applicable_pages = [page for page in pages if applicable(page)]
        if not applicable_pages:
            return {
                "id": check_id,
                "score": None,
                "status": "inapplicable",
                "completeness_percent": 100.0,
                "observation": "This check is not applicable to the collected page classes.",
                "evidence_refs": [],
            }
        rows: list[tuple[PageRecord, float, float]] = []
        for page in applicable_pages:
            score, completeness = scorer(page)
            if score is None:
                continue
            rows.append((page, float(score), float(completeness)))
        if not rows:
            return {
                "id": check_id,
                "score": None,
                "status": "unknown",
                "completeness_percent": 0.0,
                "observation": "Applicable pages were collected, but the required evidence is unknown.",
                "evidence_refs": [],
            }
        weights = {
            "homepage": 1.5,
            "service": 1.25,
            "location": 1.25,
            "service_location": 1.25,
            "contact_about": 1.0,
            "blog_resource": 0.8,
            "project_case_study": 0.8,
        }
        denominator = sum(weights.get(page.page_class or "", 0.6) for page, _score, _complete in rows)
        applicable_denominator = sum(
            weights.get(page.page_class or "", 0.6) for page in applicable_pages
        )
        score = sum(
            score * weights.get(page.page_class or "", 0.6)
            for page, score, _complete in rows
        ) / denominator
        completeness = sum(
            complete / 100 * weights.get(page.page_class or "", 0.6)
            for page, _score, complete in rows
        ) / applicable_denominator * 100
        return {
            "id": check_id,
            "score": round(score, 2),
            "status": "measured",
            "completeness_percent": round(completeness, 2),
            "observation": (
                f"{len(rows)} of {len(applicable_pages)} applicable pages supplied "
                "continuous evidence."
            ),
            "evidence_refs": [
                {
                    "artifact_path": f"pages/{page.id}.json",
                    "field": self._evidence_field_for_page(page, field),
                    "reason": f"Persisted page evidence for {check_id}.",
                    "observed": self._resolve_page_field(
                        page,
                        self._evidence_field_for_page(page, field),
                    ),
                }
                for page, _score, _complete in rows
            ],
        }

    def _intent_followup_check(
        self,
        pages: list[PageRecord],
        search: SearchIntelligenceOutput,
        *,
        attempt_id: str | None,
    ) -> dict[str, Any]:
        keywords = (
            search.payload.get("keywords", [])
            if search.approved and isinstance(search.payload, dict)
            else []
        )
        intents = {
            self._normalize_text(str(item.get("keyword") or item.get("search_intent") or ""))
            for item in keywords
            if isinstance(item, dict)
            and str(item.get("keyword") or item.get("search_intent") or "").strip()
        }
        intents.discard("")
        if not intents:
            return {
                "id": "conversational_followups",
                "score": None,
                "status": "unknown",
                "completeness_percent": 0.0,
                "observation": "No approved demand intents were available for follow-up matching.",
                "evidence_refs": [],
                "evidence_observed": search.payload,
                "evidence_field": "payload.payload",
            }
        questions = [
            str(item.get("text", ""))
            for page in pages
            for item in page.ai_evidence.get("headings", [])
            if isinstance(item, dict)
            and (
                str(item.get("text", "")).strip().endswith("?")
                or str(item.get("text", "")).casefold().startswith(
                    ("what ", "how ", "why ", "when ", "where ", "who ", "can ", "does ", "is ", "are ")
                )
            )
        ]
        covered = {
            intent
            for intent in intents
            if any(self._intent_overlap(intent, question) for question in questions)
        }
        refs = [
            {
                "artifact_path": f"pages/{page.id}.json",
                "field": "ai_evidence.headings",
                "reason": "Persisted question headings matched to approved demand intents.",
                "observed": page.ai_evidence.get("headings", []),
            }
            for page in pages
        ]
        refs.append(
            {
                "artifact_path": self._checkpoint_path(
                    attempt_id,
                    "pulling_search_intelligence",
                ),
                "field": "payload.payload.keywords",
                "reason": "Approved demand intents used for conversational coverage.",
                "observed": keywords,
            }
        )
        return {
            "id": "conversational_followups",
            "score": round(len(covered) / len(intents) * 100, 2),
            "status": "measured",
            "completeness_percent": 100.0,
            "observation": f"{len(covered)} of {len(intents)} approved demand intents were covered.",
            "evidence_refs": refs,
        }

    def _entity_consistency_check_v3(self, pages: list[PageRecord]) -> dict[str, Any]:
        applicable = [
            page
            for page in pages
            if page.page_class in {"homepage", "location", "contact_about"}
        ]
        names = [
            self._normalize_text(str(name))
            for page in applicable
            for name in page.ai_evidence.get("entity_names", [])
            if str(name).strip()
        ]
        if not applicable:
            return {
                "id": "entity_identity",
                "score": None,
                "status": "inapplicable",
                "completeness_percent": 100.0,
                "observation": "No entity-bearing page class was collected.",
                "evidence_refs": [],
            }
        if not names:
            return {
                "id": "entity_identity",
                "score": None,
                "status": "unknown",
                "completeness_percent": 0.0,
                "observation": "No validated entity identity was observed.",
                "evidence_refs": [],
            }
        dominant = Counter(names).most_common(1)[0][0]
        scores = [
            100.0
            if dominant
            in {
                self._normalize_text(str(name))
                for name in page.ai_evidence.get("entity_names", [])
            }
            else 0.0
            for page in applicable
        ]
        return {
            "id": "entity_identity",
            "score": round(sum(scores) / len(scores), 2),
            "status": "measured",
            "completeness_percent": 100.0,
            "observation": (
                f"The dominant entity identity was consistent on "
                f"{sum(score == 100 for score in scores)} of {len(scores)} applicable pages."
            ),
            "evidence_refs": [
                {
                    "artifact_path": f"pages/{page.id}.json",
                    "field": "ai_evidence.entity_names",
                    "reason": "Visible/schema entity identity consistency evidence.",
                    "observed": page.ai_evidence.get("entity_names", []),
                }
                for page in applicable
            ],
        }

    def _mention_check_v3(self, search: SearchIntelligenceOutput) -> dict[str, Any]:
        score, measured = self._mention_score_v3(search)
        mentions = corroborated_external_mentions(search)
        evidence_field = (
            "payload.payload.external_mentions"
            if "external_mentions" in search.payload
            else "payload.payload"
        )
        evidence_observed: Any = (
            search.payload.get("external_mentions", [])
            if "external_mentions" in search.payload
            else search.payload
        )
        domains = sorted(
            {
                self._mention_domain(item)
                for item in mentions
                if self._mention_domain(item)
            }
        )
        return {
            "id": "external_corroboration",
            "score": score if measured else None,
            "status": "measured" if measured else "unknown",
            "completeness_percent": 100.0 if measured else 0.0,
            "observation": (
                (
                    f"{len(domains)} distinct external domains supplied sufficient "
                    "corroboration."
                    if len(domains) >= 2
                    else (
                        "One distinct external domain was observed; a single source "
                        "does not satisfy corroboration."
                        if domains
                        else "No external corroboration was observed in the returned sample."
                    )
                )
                if measured
                else "External corroboration was not collected."
            ),
            "evidence_refs": [],
            "evidence_observed": evidence_observed,
            "evidence_field": evidence_field,
            "distinct_domains": domains,
        }

    @staticmethod
    def _mention_score_v3(
        search: SearchIntelligenceOutput,
    ) -> tuple[float, bool]:
        mention_queries = search.payload.get("mention_queries")
        external_mentions = search.payload.get("external_mentions", [])
        provider_errors = search.payload.get("provider_errors", [])
        mention_failed = any(
            isinstance(item, dict)
            and item.get("operation") == "external_mention_serp"
            for item in provider_errors
        )
        if (
            not search.approved
            or "external_mentions" not in search.payload
            or not (
                isinstance(mention_queries, list)
                and bool(mention_queries)
                or mention_queries is None
                and bool(external_mentions)
            )
            or mention_failed
        ):
            return 0.0, False
        domains = {
            AIReadinessV3Service._mention_domain(item)
            for item in corroborated_external_mentions(search)
            if AIReadinessV3Service._mention_domain(item)
        }
        distinct = len(domains)
        if distinct < 2:
            return 0.0, True
        return min(100.0, distinct / 4 * 100), True

    @staticmethod
    def _direct_answer_page_score(page: PageRecord) -> tuple[float | None, float]:
        headings = AIReadinessV3Service._answerable_headings(page)
        if not headings:
            return None, 0.0
        answered = {
            AIReadinessV3Service._normalize_text(str(item.get("heading", "")))
            for item in page.ai_evidence.get("direct_answer_blocks", [])
            if isinstance(item, dict) and str(item.get("heading", "")).strip()
        }
        matched = sum(
            1
            for heading in headings
            if AIReadinessV3Service._normalize_text(str(heading.get("text", "")))
            in answered
        )
        return min(100.0, matched / len(headings) * 100), 100.0

    @staticmethod
    def _heading_page_score(page: PageRecord) -> tuple[float, float]:
        headings = [
            item
            for item in page.ai_evidence.get("headings", [])
            if isinstance(item, dict)
        ]
        levels = [
            int(item["level"])
            for item in headings
            if isinstance(item.get("level"), int)
        ]
        h1_count = sum(1 for level in levels if level == 1)
        violations = abs(h1_count - 1) + sum(
            1 for previous, current in zip(levels, levels[1:]) if current - previous > 1
        )
        denominator = max(1, len(levels))
        return max(0.0, 100 - violations / denominator * 100), 100.0

    @staticmethod
    def _structured_page_score(page: PageRecord) -> tuple[float | None, float]:
        eligible = len(AIReadinessV3Service._answerable_headings(page))
        if not eligible:
            return None, 0.0
        list_count = int(page.ai_evidence.get("list_count", 0))
        table_count = int(page.ai_evidence.get("table_count", 0))
        table_headers = int(page.ai_evidence.get("table_header_count", 0))
        useful = list_count + min(table_count, table_headers)
        return min(100.0, useful / eligible * 100), 100.0

    @staticmethod
    def _specific_fresh_page_score(page: PageRecord) -> tuple[float, float]:
        dated = bool(page.ai_evidence.get("published_dates"))
        specific = int(page.ai_evidence.get("specific_evidence_count", 0))
        return (50.0 if dated else 0.0) + min(50.0, specific / 2 * 50), 100.0

    @staticmethod
    def _text_accessibility_page_score(
        page: PageRecord,
    ) -> tuple[float | None, float]:
        evidence = page.ai_evidence
        if "main_content_word_count" not in evidence:
            return None, 0.0
        main_words = int(evidence.get("main_content_word_count", 0))
        http_words = int(evidence.get("http_text_word_count", page.word_count or 0))
        main_ratio = float(evidence.get("main_content_ratio", 0.0))
        minimum = (
            50
            if page.page_class == "contact_about"
            else 250
            if page.page_class in {"blog_resource", "project_case_study"}
            else 150
        )
        component_scores = [
            min(100.0, main_words / minimum * 100),
            min(100.0, main_ratio / 0.6 * 100),
        ]
        rendered_words = evidence.get("rendered_text_word_count")
        if isinstance(rendered_words, int) and rendered_words >= 0:
            parity = (
                min(http_words, rendered_words) / max(http_words, rendered_words)
                if max(http_words, rendered_words)
                else 1.0
            )
            component_scores.append(parity * 100)
        return (
            sum(component_scores) / len(component_scores),
            len(component_scores) / 3 * 100,
        )

    @staticmethod
    def _schema_alignment_page_score(page: PageRecord) -> tuple[float, float]:
        valid = page.ai_evidence.get("json_ld_valid") is True
        aligned = page.ai_evidence.get("json_ld_visible_alignment") is True
        return (50.0 if valid else 0.0) + (50.0 if valid and aligned else 0.0), 100.0

    @staticmethod
    def _answerable_headings(page: PageRecord) -> list[dict[str, Any]]:
        return [
            item
            for item in page.ai_evidence.get("headings", [])
            if isinstance(item, dict)
            and int(item.get("level", 0)) in {2, 3}
            and str(item.get("text", "")).strip()
        ]

    @staticmethod
    def _intent_overlap(intent: str, question: str) -> bool:
        stopwords = {
            "and",
            "are",
            "can",
            "does",
            "for",
            "how",
            "is",
            "near",
            "the",
            "what",
            "where",
            "with",
        }
        intent_tokens = {
            token for token in re.findall(r"[a-z0-9]+", intent) if token not in stopwords
        }
        question_tokens = {
            token
            for token in re.findall(r"[a-z0-9]+", question.casefold())
            if token not in stopwords
        }
        return bool(intent_tokens) and len(intent_tokens & question_tokens) >= min(
            2,
            len(intent_tokens),
        )

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.casefold().split())

    @classmethod
    def _evidence_field_for_page(cls, page: PageRecord, field: str) -> str:
        try:
            cls._resolve_page_field(page, field)
        except (KeyError, TypeError):
            return "ai_evidence"
        return field

    @staticmethod
    def _mention_domain(item: dict[str, Any]) -> str:
        domain = str(item.get("domain") or "").casefold().removeprefix("www.").rstrip(".")
        if domain:
            return domain
        return (
            (urlsplit(str(item.get("url") or item.get("result_url") or "")).hostname or "")
            .casefold()
            .removeprefix("www.")
            .rstrip(".")
        )

    @staticmethod
    def _checkpoint_path(attempt_id: str | None, stage: str) -> str:
        return (
            f"checkpoints/{attempt_id}/{stage}.json"
            if attempt_id
            else f"checkpoints/{stage}.json"
        )
