"""Offline promotion metrics for repeated, human-reviewed agentic assessments."""

from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any, Iterable

from src.models import (
    AgenticAssessmentReviewEvent,
    AgenticAssessmentSnapshot,
)


PROMOTION_THRESHOLDS = {
    "schema_validity_rate": 1.0,
    "unsupported_exported_claims": 0,
    "evidence_reference_precision": 0.98,
    "service_fit_agreement": 0.85,
    "top_three_overlap": 0.80,
    "factual_correction_rate_max": 0.10,
    "gpt_escalation_rate_max": 0.20,
    "mean_cost_usd_max": 0.10,
    "median_review_time_minutes_max": 10.0,
    "minimum_evidence_packs": 22,
    "minimum_verticals": 2,
    "minimum_models_per_pack": 2,
}


class AgenticEvaluationService:
    def summarize(
        self,
        assessments: Iterable[AgenticAssessmentSnapshot],
        review_events: Iterable[AgenticAssessmentReviewEvent] = (),
        *,
        service_fit_labels: dict[str, bool] | None = None,
        review_durations_minutes: dict[str, float] | None = None,
        sample_metadata: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        records = list(assessments)
        events = list(review_events)
        if not records:
            return {
                "assessment_count": 0,
                "promotion_ready": False,
                "reason": "no frozen assessments were supplied",
            }
        schema_validity = sum(
            assessment.validation_result.get("schema_valid") is True
            for assessment in records
        ) / len(records)
        total_refs = 0
        invalid_refs = 0
        unsupported = 0
        for assessment in records:
            invalid_refs += int(
                assessment.validation_result.get("invalid_reference_count", 0)
            )
            total_refs += sum(
                len(item.get("evidence_refs", []))
                for item in assessment.findings
                if isinstance(item, dict)
            ) + int(assessment.validation_result.get("invalid_reference_count", 0))
            unsupported += int(
                assessment.validation_result.get("unsupported_exported_claims", 0)
            )
        precision = (
            (total_refs - invalid_refs) / total_refs if total_refs else 0.0
        )
        corrections = sum(
            event.event_type == "correction_recorded" for event in events
        )
        escalations = sum(
            event.event_type == "gpt_review_requested" for event in events
        )
        reviewed_ids = {event.assessment_id for event in events}
        review_denominator = max(1, len(reviewed_ids) or len(records))
        labels = service_fit_labels or {}
        durations = review_durations_minutes or {}
        samples = sample_metadata or {}
        service_fit_agreement = (
            sum(bool(value) for value in labels.values()) / len(labels)
            if labels
            else None
        )
        overlap = self._top_three_overlap(records)
        mean_cost = sum(item.total_cost_usd for item in records) / len(records)
        pack_models: dict[str, set[str]] = defaultdict(set)
        for assessment in records:
            pack_models[assessment.evidence_pack_sha256].add(
                f"{assessment.served_provider}:{assessment.served_model}"
            )
        distinct_packs = set(pack_models)
        sample_rows = [
            samples.get(pack_hash, {})
            for pack_hash in sorted(distinct_packs)
        ]
        verticals = {
            str(row.get("vertical_id"))
            for row in sample_rows
            if row.get("vertical_id")
        }
        targets = {
            str(row.get("target_domain")).casefold()
            for row in sample_rows
            if row.get("target_domain")
        }
        authentic_packs = sum(
            row.get("source_kind") == "recorded_model_output"
            for row in sample_rows
        )
        human_reviewed_packs = sum(
            row.get("human_reviewed") is True
            for row in sample_rows
        )
        median_review = (
            float(median(durations.values()))
            if durations
            else None
        )
        metrics = {
            "schema_validity_rate": round(schema_validity, 4),
            "unsupported_exported_claims": unsupported,
            "evidence_reference_precision": round(precision, 4),
            "service_fit_agreement": (
                round(service_fit_agreement, 4)
                if service_fit_agreement is not None
                else None
            ),
            "top_three_overlap": (
                round(overlap, 4) if overlap is not None else None
            ),
            "factual_correction_rate": round(
                corrections / review_denominator,
                4,
            ),
            "gpt_escalation_rate": round(
                escalations / review_denominator,
                4,
            ),
            "mean_cost_usd": round(mean_cost, 6),
            "median_review_time_minutes": (
                round(median_review, 4)
                if median_review is not None
                else None
            ),
            "distinct_evidence_pack_count": len(distinct_packs),
            "vertical_count": len(verticals),
            "authentic_recorded_pack_count": authentic_packs,
            "human_reviewed_pack_count": human_reviewed_packs,
            "model_routes": sorted(
                set().union(*pack_models.values()) if pack_models else set()
            ),
        }
        gates = {
            "schema_validity": schema_validity
            >= PROMOTION_THRESHOLDS["schema_validity_rate"],
            "unsupported_claims": unsupported
            == PROMOTION_THRESHOLDS["unsupported_exported_claims"],
            "evidence_precision": precision
            >= PROMOTION_THRESHOLDS["evidence_reference_precision"],
            "service_fit": service_fit_agreement is not None
            and service_fit_agreement
            >= PROMOTION_THRESHOLDS["service_fit_agreement"],
            "recommendation_stability": overlap is not None
            and overlap >= PROMOTION_THRESHOLDS["top_three_overlap"],
            "correction_rate": corrections / review_denominator
            < PROMOTION_THRESHOLDS["factual_correction_rate_max"],
            "escalation_rate": escalations / review_denominator
            < PROMOTION_THRESHOLDS["gpt_escalation_rate_max"],
            "cost": mean_cost < PROMOTION_THRESHOLDS["mean_cost_usd_max"],
            "review_time": median_review is not None
            and median_review
            < PROMOTION_THRESHOLDS["median_review_time_minutes_max"],
            "sample_policy": (
                len(distinct_packs)
                >= PROMOTION_THRESHOLDS["minimum_evidence_packs"]
                and len(verticals)
                >= PROMOTION_THRESHOLDS["minimum_verticals"]
                and {"novaryu.com", "laceyglass.com"}.issubset(targets)
                and all(
                    len(routes)
                    >= PROMOTION_THRESHOLDS["minimum_models_per_pack"]
                    for routes in pack_models.values()
                )
            ),
            "sample_authenticity": (
                authentic_packs == len(distinct_packs)
                and human_reviewed_packs == len(distinct_packs)
                and len(distinct_packs) > 0
            ),
            "audit_evidence": all(
                assessment.call_ids
                and assessment.evidence_pack_sha256
                and assessment.validation_result
                for assessment in records
            ),
        }
        return {
            "assessment_count": len(records),
            "reviewed_assessment_count": len(reviewed_ids),
            "metrics": metrics,
            "gates": gates,
            "promotion_ready": all(gates.values()),
            "thresholds": dict(PROMOTION_THRESHOLDS),
            "sample_disclosure": (
                "Promotion requires recorded model outputs and real human review "
                "for every frozen evidence pack; synthetic contract fixtures "
                "measure the harness but cannot satisfy the authenticity gate."
            ),
        }

    @staticmethod
    def _top_three_overlap(
        assessments: list[AgenticAssessmentSnapshot],
    ) -> float | None:
        by_pack: dict[str, list[set[str]]] = defaultdict(list)
        for assessment in assessments:
            top = [
                item
                for item in assessment.findings
                if isinstance(item, dict)
                and item.get("claim_type") == "recommendation"
            ][:3]
            identities = {
                str(item.get("title") or item.get("claim") or "").casefold().strip()
                for item in top
                if str(item.get("title") or item.get("claim") or "").strip()
            }
            by_pack[assessment.evidence_pack_sha256].append(identities)
        scores: list[float] = []
        for groups in by_pack.values():
            if len(groups) < 2:
                continue
            for left, right in zip(groups, groups[1:]):
                union = left | right
                scores.append(len(left & right) / len(union) if union else 1.0)
        return sum(scores) / len(scores) if scores else None
