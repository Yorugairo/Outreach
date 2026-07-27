"""Deterministic, crawl-only conversion readiness checks.

The service evaluates visible DOM evidence persisted on :class:`PageRecord`.
It does not execute JavaScript, submit forms, or estimate visitor, lead, or
revenue outcomes. Missing conversion evidence is explicitly ``unknown``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from src.models import (
    CONVERSION_READINESS_VERSION,
    PageRecord,
    ProductSurfaceResult,
    ScoreCheckResult,
)
from src.services.page_analysis_service import PageAnalysisOutput


UTILITY_CLASSES = {"legal_utility", "low_value"}


VERTICAL_TERMS: dict[str, dict[str, tuple[str, ...]]] = {
    "national_bjj_registry": {
        "offer": ("class", "classes", "program", "lesson", "training", "membership"),
        "action": ("trial", "sign up", "signup", "join", "start", "book", "schedule", "contact", "call"),
        "expectation": ("schedule", "class times", "timetable", "price", "pricing", "tuition", "membership", "beginner", "kids", "adult", "ages"),
        "capture": ("trial", "sign up", "signup", "join", "book", "schedule", "contact", "call"),
    },
    "one_trade_network": {
        "offer": ("service", "repair", "installation", "maintenance", "replacement", "emergency", "quote", "estimate"),
        "action": ("quote", "estimate", "book", "schedule", "appointment", "contact", "call", "request"),
        "expectation": ("service area", "licensed", "insured", "price", "pricing", "estimate", "quote", "appointment", "schedule"),
        "capture": ("quote", "estimate", "book", "schedule", "appointment", "contact", "call", "request"),
    },
}


CHECKS: tuple[dict[str, str], ...] = (
    {"id": "offer_clarity", "family": "offer", "severity": "high"},
    {"id": "next_action", "family": "action", "severity": "high"},
    {"id": "schedule_pricing_eligibility", "family": "offer", "severity": "medium"},
    {"id": "signup_or_lead_capture", "family": "capture", "severity": "high"},
    {"id": "contact_route", "family": "trust", "severity": "high"},
    {"id": "mobile_action_accessibility", "family": "mobile", "severity": "medium"},
    {"id": "trust_proof", "family": "trust", "severity": "medium"},
)


class ConversionReadinessService:
    """Build ``conversion-readiness.v1`` from persisted page evidence."""

    def __init__(self, vertical_id: str | None = None) -> None:
        self.vertical_id = vertical_id

    def build(
        self,
        pages: PageAnalysisOutput | Iterable[PageRecord],
        vertical_id: str | None = None,
        *,
        page_limit: int = 100,
        vertical_pack: Any | None = None,
    ) -> ProductSurfaceResult:
        records = self._records(pages)
        collection_capped = pages.capped if isinstance(pages, PageAnalysisOutput) else False
        vertical = self._normalize_vertical(vertical_id or vertical_pack or self.vertical_id)
        eligible = [
            page
            for page in records
            if page.fetch_status == "fetched" and page.page_class not in UTILITY_CLASSES
        ]

        checks: list[ScoreCheckResult] = []
        for definition in CHECKS:
            checks.append(self._check(definition, eligible, vertical))

        intended = [check for check in checks if check.status != "inapplicable"]
        known = [check for check in intended if check.status in {"measured", "failed"}]
        score = (
            sum(float(check.score or 0.0) for check in known) / len(known)
            if known
            else None
        )
        completeness = len(known) / len(intended) * 100 if intended else 0.0
        evidence_confidence = (
            sum(float(check.evidence_confidence or 0.0) for check in known)
            / len(known)
            * 100
            if known
            else 0.0
        )
        families: dict[str, Any] = {}
        for family in ("offer", "action", "capture", "trust", "mobile"):
            family_checks = [check for check in checks if check.family == family]
            family_known = [
                check for check in family_checks if check.status in {"measured", "failed"}
            ]
            family_score = (
                sum(float(check.score or 0.0) for check in family_known) / len(family_known)
                if family_known
                else None
            )
            family_complete = (
                len(family_known) / len(family_checks) * 100 if family_checks else 100.0
            )
            families[family] = {
                "score": round(family_score, 4) if family_score is not None else None,
                "status": self._status(family_score, family_complete),
                "completeness_percent": round(family_complete, 4),
                "check_ids": [check.check_id for check in family_checks],
            }

        warnings: list[str] = [
            "Conversion Readiness measures visible website path integrity only; it does not measure lead quality, attendance, close rate, CRM performance, or revenue."
        ]
        if vertical == "unknown":
            warnings.append("No supported vertical was supplied; generic conversion terms were used and vertical-specific applicability is limited.")
        unknown_ids = [check.check_id for check in checks if check.status == "unknown"]
        if unknown_ids:
            warnings.append("Conversion DOM evidence was unavailable for: " + ", ".join(unknown_ids) + ".")
        if collection_capped:
            warnings.append(
                f"Collection reached the {page_limit}-page ceiling; this surface describes collected pages, not every URL on the domain."
            )

        recommendations = [
            {
                "check_id": check.check_id,
                "action": self._remediation(check.check_id, vertical),
                "evidence_refs": check.evidence_refs,
            }
            for check in checks
            if check.status == "failed"
        ]
        return ProductSurfaceResult(
            surface="conversion_readiness",
            version=CONVERSION_READINESS_VERSION,
            status=self._status(score, completeness),
            score=round(score, 4) if score is not None else None,
            completeness_percent=round(completeness, 4),
            evidence_confidence=round(evidence_confidence, 4),
            families=families,
            checks=[check.to_dict() for check in checks],
            metrics={
                "vertical_id": vertical,
                "eligible_page_count": len(eligible),
                "collected_page_count": len(records),
                "page_limit": page_limit,
                "evidence_version": "conversion-dom-evidence.v1",
                "forms_submitted": False,
                "funnel_performance_observed": False,
            },
            recommendations=recommendations,
            warnings=warnings,
        )

    @staticmethod
    def _records(pages: PageAnalysisOutput | Iterable[PageRecord]) -> list[PageRecord]:
        if isinstance(pages, PageAnalysisOutput):
            return list(pages.pages)
        return list(pages)

    @staticmethod
    def _normalize_vertical(value: str | Any | None) -> str:
        if not value:
            return "unknown"
        if not isinstance(value, str) and hasattr(value, "vertical_id"):
            value = getattr(value, "vertical_id")
        if not isinstance(value, str):
            return "unknown"
        return value.split(".", 1)[0].strip().casefold() or "unknown"

    def _check(
        self,
        definition: dict[str, str],
        pages: list[PageRecord],
        vertical: str,
    ) -> ScoreCheckResult:
        known_rows: list[tuple[PageRecord, bool]] = []
        for page in pages:
            observed = page.ai_evidence
            if observed.get("conversion_evidence_version") != "conversion-dom-evidence.v1":
                continue
            outcome = self._evaluate(definition["id"], observed, vertical)
            if outcome is not None:
                known_rows.append((page, outcome))
        applicable_ids = [page.id for page in pages]
        if not known_rows:
            return ScoreCheckResult(
                check_id=definition["id"],
                check_version=1,
                family=definition["family"],
                severity=definition["severity"],
                status="unknown",
                score_affecting=True,
                limitations=["The bounded conversion DOM evidence contract was not available on collected pages."],
                applicable_page_ids=applicable_ids,
                remediation=self._remediation(definition["id"], vertical),
            )
        affected = [page for page, passed in known_rows if not passed]
        refs = [self._evidence_ref(page, definition["id"], passed) for page, passed in known_rows]
        return ScoreCheckResult(
            check_id=definition["id"],
            check_version=1,
            family=definition["family"],
            severity=definition["severity"],
            status="failed" if affected else "measured",
            score_affecting=True,
            applicable_page_ids=applicable_ids,
            affected_page_ids=[page.id for page in affected],
            weighted_affected_ratio=len(affected) / len(known_rows),
            evidence_confidence=len(known_rows) / len(pages) if pages else 0.0,
            score=(len(known_rows) - len(affected)) / len(known_rows) * 100,
            evidence_refs=refs,
            remediation=self._remediation(definition["id"], vertical),
        )

    @staticmethod
    def _evaluate(check_id: str, evidence: dict[str, Any], vertical: str) -> bool | None:
        terms = VERTICAL_TERMS.get(vertical, VERTICAL_TERMS["one_trade_network"])
        def values(key: str) -> list[str]:
            value = evidence.get(key)
            return [str(item).casefold() for item in value] if isinstance(value, list) else []

        if check_id == "offer_clarity":
            return bool(set(values("offer_signals")) & set(terms["offer"]))
        if check_id == "next_action":
            ctas = evidence.get("cta_links")
            if not isinstance(ctas, list):
                return False
            return any(
                isinstance(cta, dict)
                and (
                    str(cta.get("kind") or "") == "button"
                    or (
                        isinstance(cta.get("href"), str)
                        and str(cta["href"]).strip().casefold()
                        not in {"", "#"}
                        and not str(cta["href"]).strip().casefold().startswith("javascript:")
                    )
                )
                for cta in ctas
            )
        if check_id == "schedule_pricing_eligibility":
            observed = set(values("schedule_signals")) | set(values("pricing_signals")) | set(values("eligibility_signals"))
            return bool(observed & set(terms["expectation"]))
        if check_id == "signup_or_lead_capture":
            forms = evidence.get("forms")
            has_form = isinstance(forms, list) and any(
                isinstance(form, dict) and int(form.get("field_count", 0)) > 0 for form in forms
            )
            ctas = " ".join(values("cta_links"))
            return has_form or bool(set(values("cta_links")) & set(terms["capture"])) or any(term in ctas for term in terms["capture"])
        if check_id == "contact_route":
            return bool(values("phone_numbers") or values("email_addresses") or values("contact_signals"))
        if check_id == "mobile_action_accessibility":
            return evidence.get("mobile_viewport") is True and bool(evidence.get("cta_links"))
        if check_id == "trust_proof":
            return bool(values("trust_signals"))
        return None

    @staticmethod
    def _evidence_ref(page: PageRecord, check_id: str, passed: bool) -> dict[str, Any]:
        fields = {
            "offer_clarity": "ai_evidence.offer_signals",
            "next_action": "ai_evidence.cta_links",
            "schedule_pricing_eligibility": "ai_evidence.schedule_signals",
            "signup_or_lead_capture": "ai_evidence.forms",
            "contact_route": "ai_evidence.contact_signals",
            "mobile_action_accessibility": "ai_evidence.mobile_viewport",
            "trust_proof": "ai_evidence.trust_signals",
        }
        field = fields.get(check_id, "ai_evidence.conversion_evidence_version")
        if check_id == "schedule_pricing_eligibility":
            for candidate in ("schedule_signals", "pricing_signals", "eligibility_signals"):
                if page.ai_evidence.get(candidate):
                    field = f"ai_evidence.{candidate}"
                    break
        elif check_id == "signup_or_lead_capture" and not page.ai_evidence.get("forms"):
            field = "ai_evidence.cta_links"
        elif check_id == "contact_route":
            for candidate in ("phone_numbers", "email_addresses", "contact_signals"):
                if page.ai_evidence.get(candidate):
                    field = f"ai_evidence.{candidate}"
                    break
        raw_field = field.split(".", 1)[1] if "." in field else field
        return {
            "artifact_path": f"pages/{page.id}.json",
            "page_id": page.id,
            "url": page.url,
            "field": field,
            "check_id": check_id,
            "reason": "Observed bounded conversion DOM evidence on the fetched page.",
            "observed": page.ai_evidence.get(raw_field),
            "check_result": passed,
        }

    @staticmethod
    def _remediation(check_id: str, vertical: str) -> str:
        actions = {
            "offer_clarity": "State the primary program or service, audience, and expected outcome on the page.",
            "next_action": "Expose a visible next-action CTA with a same-site destination or clear contact route.",
            "schedule_pricing_eligibility": "Make the applicable schedule, pricing, eligibility, or service-area expectations discoverable.",
            "signup_or_lead_capture": "Provide a usable signup/trial or quote/contact path and describe the handoff.",
            "contact_route": "Expose a clear phone, email, address, or contact destination for the next step.",
            "mobile_action_accessibility": "Keep the next-action CTA reachable on mobile and declare a responsive viewport.",
            "trust_proof": "Provide visible, relevant proof such as reviews, credentials, experience, or member/project evidence.",
        }
        return actions.get(check_id, f"Review the {check_id} evidence for the {vertical} site.")

    @staticmethod
    def _status(score: float | None, completeness: float) -> str:
        if score is None:
            return "unknown"
        return "complete" if completeness >= 100 else "partial"


__all__ = ["ConversionReadinessService", "VERTICAL_TERMS"]
