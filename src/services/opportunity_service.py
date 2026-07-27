from __future__ import annotations

"""Deterministic commercial opportunity rules.

This module deliberately does not persist anything.  It turns a completed v2
report into normalized evidence families and a conservative coverage decision;
the run and its artifacts remain the source of truth.
"""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

from src.models import CommercialFinding, InsightReport, ProspectRecord, VerticalPack
from src.services.provenance_service import validate_evidence_ref
from src.services.search_intelligence_service import (
    SearchIntelligenceOutput,
    TargetContext,
    validate_target_search_evidence,
)
from src.vertical_packs import resolve_vertical_pack


_FAMILY_BY_CATEGORY = {
    "sitemap_discovery": "technical_seo",
    "page_metadata": "technical_seo",
    "page_heading": "technical_seo",
    "page_fetch_evidence": "technical_seo",
    "search_evidence_completeness": "answer_readiness",
    "profile": "local_entity",
    "local": "local_entity",
    "entity": "local_entity",
    "answer": "answer_readiness",
    "service": "service_coverage",
    "location": "location_coverage",
}


@dataclass(frozen=True, slots=True)
class CoverageAssessment:
    vertical_id: str
    vertical_pack_version: str
    expected_services: tuple[str, ...]
    expected_locations: tuple[str, ...]
    observed_services: tuple[str, ...]
    observed_locations: tuple[str, ...]
    missing_services: tuple[str, ...]
    missing_locations: tuple[str, ...]
    fetched_indexable_pages: int
    crawl_sufficient: bool
    demand_valid: bool
    coverage_gap: bool
    pseo_eligible: bool
    evidence_refs: tuple[dict[str, Any], ...]
    evidence_limits: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class OpportunityService:
    """Classify report findings and apply the pSEO evidence gate."""

    def classify_evidence_family(self, finding: Mapping[str, Any] | CommercialFinding) -> str:
        category = finding.category if isinstance(finding, CommercialFinding) else str(finding.get("category", ""))
        existing = finding.evidence_family if isinstance(finding, CommercialFinding) else finding.get("evidence_family")
        if existing in {"technical_seo", "local_entity", "answer_readiness", "service_coverage", "location_coverage"}:
            return str(existing)
        lowered = category.casefold()
        for prefix, family in _FAMILY_BY_CATEGORY.items():
            if prefix in lowered:
                return family
        return "technical_seo"

    def normalize_findings(self, report: InsightReport | Mapping[str, Any]) -> list[dict[str, Any]]:
        payload = self._payload(report)
        normalized: list[dict[str, Any]] = []
        for raw in payload.get("findings", []):
            if not isinstance(raw, Mapping):
                continue
            item = dict(raw)
            item["evidence_family"] = self.classify_evidence_family(item)
            normalized.append(item)
        return normalized

    def classify_findings(self, report: InsightReport | Mapping[str, Any]) -> list[dict[str, Any]]:
        """Compatibility name for callers that treat family assignment as classification."""
        return self.normalize_findings(report)

    def assess(
        self,
        report: InsightReport | Mapping[str, Any],
        vertical_pack: VerticalPack | str,
        prospect: ProspectRecord | None = None,
    ) -> CoverageAssessment:
        pack = resolve_vertical_pack(vertical_pack)
        payload = self._payload(report)
        target = payload.get("target", {}) if isinstance(payload.get("target", {}), Mapping) else {}
        run = payload.get("run", {}) if isinstance(payload.get("run", {}), Mapping) else {}
        pages = payload.get("pages", []) if isinstance(payload.get("pages", []), list) else []
        eligible_pages = [
            page for page in pages
            if isinstance(page, Mapping)
            and page.get("fetch_status") == "fetched"
            and page.get("indexable") is True
        ]
        expected_services, expected_locations = self._expected_coverage(payload, pack, prospect)
        observed_services, observed_locations = self._observed_coverage(eligible_pages, expected_services, expected_locations)
        missing_services = tuple(item for item in expected_services if item not in observed_services)
        missing_locations = tuple(item for item in expected_locations if item not in observed_locations)
        coverage_gap = bool(missing_services or missing_locations)

        # A complete small inventory is an explicit crawl declaration, not an
        # assumption made from a short sample.
        limits = run.get("input_payload", {}).get("limits", {}) if isinstance(run.get("input_payload", {}), Mapping) else {}
        complete_inventory = bool(
            payload.get("coverage", {}).get("inventory_complete")
            if isinstance(payload.get("coverage", {}), Mapping)
            else False
        ) or bool(limits.get("inventory_complete"))
        crawl_sufficient = len(eligible_pages) >= 3 or (complete_inventory and len(eligible_pages) > 0)

        context = payload.get("target_context", {})
        search_payload = payload.get("search", {}) if isinstance(payload.get("search", {}), Mapping) else {}
        search = SearchIntelligenceOutput(
            configured=bool(search_payload.get("configured")),
            approved=bool(search_payload.get("approved")),
            skipped_reason=search_payload.get("skipped_reason"),
            payload=dict(search_payload.get("payload", {}) or {}),
        )
        try:
            demand_valid = validate_target_search_evidence(search, TargetContext.from_value(context)) is not None
        except (TypeError, ValueError):
            demand_valid = False
        refs = self._coverage_refs(payload, missing_services, missing_locations)
        limits_out: list[str] = []
        if not demand_valid:
            limits_out.append("target-specific demand evidence is unavailable or invalid")
        if not crawl_sufficient:
            limits_out.append("crawl evidence contains fewer than three fetched indexable pages and no complete inventory")
        if not expected_services and not expected_locations:
            limits_out.append("vertical coverage taxonomy has no target-specific expected service/location values")
        pseo_eligible = demand_valid and crawl_sufficient and coverage_gap and bool(refs)
        return CoverageAssessment(
            vertical_id=pack.vertical_id,
            vertical_pack_version=pack.pack_id,
            expected_services=expected_services,
            expected_locations=expected_locations,
            observed_services=observed_services,
            observed_locations=observed_locations,
            missing_services=missing_services,
            missing_locations=missing_locations,
            fetched_indexable_pages=len(eligible_pages),
            crawl_sufficient=crawl_sufficient,
            demand_valid=demand_valid,
            coverage_gap=coverage_gap,
            pseo_eligible=pseo_eligible,
            evidence_refs=tuple(refs),
            evidence_limits=tuple(limits_out),
        )

    def assess_coverage(
        self,
        report: InsightReport | Mapping[str, Any],
        vertical_pack: VerticalPack | str,
        prospect: ProspectRecord | None = None,
    ) -> CoverageAssessment:
        return self.assess(report, vertical_pack, prospect)

    def validate_report(self, report: InsightReport | Mapping[str, Any]) -> None:
        payload = self._payload(report)
        version = report.report_version if isinstance(report, InsightReport) else report.get("report_version", "v2")
        status = report.report_status if isinstance(report, InsightReport) else report.get("report_status", "complete")
        if version != "v2":
            raise ValueError("commercial opportunities require a v2 report")
        if status not in {"complete", "completed"}:
            raise ValueError("commercial opportunities require a complete v2 report")
        run = payload.get("run", {})
        if isinstance(run, Mapping) and run.get("status") not in {None, "completed", "complete"}:
            raise ValueError("commercial opportunities require a completed insight run")

    @staticmethod
    def _payload(report: InsightReport | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(report, InsightReport):
            return report.report_payload
        if isinstance(report, Mapping):
            payload = report.get("report_payload", report)
            return dict(payload) if isinstance(payload, Mapping) else {}
        raise TypeError("report must be InsightReport or mapping")

    @staticmethod
    def _expected_coverage(
        payload: Mapping[str, Any],
        pack: VerticalPack,
        prospect: ProspectRecord | None = None,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        coverage = payload.get("coverage", {}) if isinstance(payload.get("coverage", {}), Mapping) else {}
        target = payload.get("target", {}) if isinstance(payload.get("target", {}), Mapping) else {}
        metadata = target.get("metadata", {}) if isinstance(target.get("metadata", {}), Mapping) else {}
        services = coverage.get("expected_services", metadata.get("expected_services", pack.service_taxonomy.get("core_services", [])))
        locations = coverage.get("expected_locations", metadata.get("expected_locations", []))
        if isinstance(metadata.get("service_areas"), list) and not locations:
            locations = metadata["service_areas"]
        if prospect is not None and prospect.location.strip() and not locations:
            locations = [prospect.location]
        return OpportunityService._clean_values(services), OpportunityService._clean_values(locations)

    @staticmethod
    def _clean_values(values: Any) -> tuple[str, ...]:
        if not isinstance(values, (list, tuple, set)):
            return ()
        return tuple(sorted({str(value).strip().casefold() for value in values if str(value).strip()}))

    @staticmethod
    def _observed_coverage(pages: list[Mapping[str, Any]], expected_services: tuple[str, ...], expected_locations: tuple[str, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
        observed_services: set[str] = set()
        observed_locations: set[str] = set()
        for page in pages:
            haystack = " ".join(str(page.get(key, "")) for key in ("url", "normalized_path", "title", "h1", "meta_description")).casefold()
            for value in expected_services:
                if value in haystack:
                    observed_services.add(value)
            for value in expected_locations:
                if value in haystack:
                    observed_locations.add(value)
        return tuple(sorted(observed_services)), tuple(sorted(observed_locations))

    @staticmethod
    def _coverage_refs(payload: Mapping[str, Any], missing_services: tuple[str, ...], missing_locations: tuple[str, ...]) -> list[dict[str, Any]]:
        refs: list[dict[str, Any]] = []
        pages = payload.get("pages", []) if isinstance(payload.get("pages", []), list) else []
        for page in pages:
            if (
                not isinstance(page, Mapping)
                or not page.get("id")
                or page.get("fetch_status") != "fetched"
                or page.get("indexable") is not True
            ):
                continue
            for field_name in ("url", "title", "h1", "meta_description"):
                refs.append(
                    {
                        "artifact_path": f"pages/{page['id']}.json",
                        "field": field_name,
                        "reason": "Fetched indexable page inventory used to assess systematic coverage.",
                        "observed": page.get(field_name),
                    }
                )
        coverage = payload.get("coverage", {})
        if isinstance(coverage, Mapping) and isinstance(coverage.get("evidence_refs"), list):
            refs.extend(ref for ref in coverage["evidence_refs"] if isinstance(ref, dict))
        return refs if (missing_services or missing_locations) else []


__all__ = ["CoverageAssessment", "OpportunityService"]
