"""Deterministic commercial prioritization for evidence-backed recommendations."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


class RecommendationPriorityService:
    VERSION = "recommendation-priority.v1"
    WEIGHTS = {
        "severity": 0.25,
        "affected_scope": 0.15,
        "commercial_intent": 0.15,
        "current_visibility": 0.15,
        "conversion_friction": 0.12,
        "confidence": 0.08,
        "effort": 0.05,
        "recorded_outcomes": 0.05,
    }
    LABEL_SCORES = {
        "severity": {
            "critical": 100,
            "high": 80,
            "medium": 55,
            "low": 30,
            "info": 10,
        },
        "commercial_intent": {
            "transactional": 100,
            "high": 90,
            "commercial": 80,
            "medium": 55,
            "informational": 35,
            "low": 25,
            "unknown": None,
        },
        "conversion_friction": {
            "blocking": 100,
            "high": 85,
            "medium": 55,
            "low": 25,
            "none": 0,
            "unknown": None,
        },
        "confidence": {"high": 100, "medium": 65, "low": 35},
        "effort": {
            "small": 100,
            "medium": 65,
            "large": 35,
            "discovery_required": 20,
            "unknown": None,
        },
    }

    def prioritize(
        self,
        recommendations: Iterable[Mapping[str, Any]],
        *,
        total_pages: int | None = None,
        outcome_rates: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        ranked = [
            self.score(
                recommendation,
                total_pages=total_pages,
                outcome_rates=outcome_rates,
            )
            for recommendation in recommendations
        ]
        ranked.sort(
            key=lambda item: (
                -item["priority_score"],
                -item["priority_completeness_percent"],
                str(item.get("id") or item.get("title") or "").casefold(),
            )
        )
        for index, item in enumerate(ranked, start=1):
            item["priority_rank"] = index
        return ranked

    rank = prioritize

    def score(
        self,
        recommendation: Mapping[str, Any],
        *,
        total_pages: int | None = None,
        outcome_rates: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = dict(recommendation)
        components = {
            "severity": self._label("severity", payload.get("severity")),
            "affected_scope": self._scope(payload, total_pages),
            "commercial_intent": self._label(
                "commercial_intent",
                payload.get("commercial_intent")
                or payload.get("intent"),
            ),
            "current_visibility": self._visibility(payload),
            "conversion_friction": self._label(
                "conversion_friction",
                payload.get("conversion_friction"),
            ),
            "confidence": self._label("confidence", payload.get("confidence")),
            "effort": self._label("effort", payload.get("effort")),
            "recorded_outcomes": self._outcomes(payload, outcome_rates),
        }
        known_weight = sum(
            self.WEIGHTS[name]
            for name, value in components.items()
            if value is not None
        )
        weighted = sum(
            self.WEIGHTS[name] * float(value)
            for name, value in components.items()
            if value is not None
        )
        score = round(weighted / known_weight, 2) if known_weight else 0.0
        payload.update(
            {
                "priority_version": self.VERSION,
                "priority_score": score,
                "priority_completeness_percent": round(known_weight * 100, 2),
                "priority_components": components,
                "priority_unknown_dimensions": sorted(
                    name for name, value in components.items() if value is None
                ),
            }
        )
        return payload

    @classmethod
    def _label(cls, dimension: str, value: Any) -> float | None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return max(0.0, min(float(value), 100.0))
        normalized = str(value or "unknown").casefold().strip()
        return cls.LABEL_SCORES[dimension].get(normalized)

    @staticmethod
    def _scope(payload: Mapping[str, Any], total_pages: int | None) -> float | None:
        percent = payload.get("affected_scope_percent")
        if isinstance(percent, (int, float)) and not isinstance(percent, bool):
            return max(0.0, min(float(percent), 100.0))
        affected = payload.get("affected_page_count")
        denominator = payload.get("total_page_count") or total_pages
        if (
            isinstance(affected, (int, float))
            and isinstance(denominator, (int, float))
            and not isinstance(affected, bool)
            and not isinstance(denominator, bool)
            and denominator > 0
        ):
            return max(0.0, min(float(affected) / float(denominator) * 100, 100.0))
        label = str(payload.get("affected_scope") or "").casefold()
        return {
            "sitewide": 100.0,
            "most_pages": 80.0,
            "multiple_pages": 60.0,
            "single_page": 25.0,
        }.get(label)

    @staticmethod
    def _visibility(payload: Mapping[str, Any]) -> float | None:
        value = payload.get("current_visibility")
        if isinstance(value, str):
            normalized = value.casefold().strip()
            if normalized in {"not_observed", "not observed", "absent_sample"}:
                return 100.0
            return {
                "very_low": 90.0,
                "low": 75.0,
                "medium": 50.0,
                "high": 20.0,
            }.get(normalized)
        rank = payload.get("observed_rank")
        if isinstance(rank, (int, float)) and not isinstance(rank, bool):
            if rank <= 3:
                return 20.0
            if rank <= 10:
                return 55.0
            if rank <= 20:
                return 70.0
            return 85.0
        return None

    @staticmethod
    def _outcomes(
        payload: Mapping[str, Any],
        outcome_rates: Mapping[str, Any] | None,
    ) -> float | None:
        # P12 outcome memory is explicitly gated.  A plain mapping is not
        # enough to change deterministic recommendation ordering; the outcome
        # service must attach its versioned ``__calibration_eligible__``
        # marker after the vertical sample thresholds are met.
        if outcome_rates is None:
            return RecommendationPriorityService._legacy_recorded_outcome(payload)
        if outcome_rates.get("__calibration_eligible__") is not True:
            return None
        key = str(
            payload.get("recommendation_type")
            or payload.get("check_id")
            or payload.get("id")
            or ""
        )
        value = outcome_rates.get(key)
        if isinstance(value, Mapping):
            if value.get("eligible") is False:
                return None
            value = value.get("value")
        if value is None:
            # ``recorded_outcome_rate`` predates P12 and remains a fixture and
            # compatibility field.  It is only consulted once the explicit
            # calibration gate is open; otherwise it cannot silently influence
            # the recommendation score.
            value = payload.get("recorded_outcome_rate")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            normalized = float(value) * 100 if 0 <= value <= 1 else float(value)
            return max(0.0, min(normalized, 100.0))
        return None

    @staticmethod
    def _legacy_recorded_outcome(payload: Mapping[str, Any]) -> float | None:
        """Preserve the pre-P12 fixture field without accepting new rates.

        Existing report fixtures may carry an explicitly recorded rate.  It
        is retained for backward-compatible rendering, while rates supplied
        by the new outcome-memory service always require the gate marker.
        """

        value = payload.get("recorded_outcome_rate")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            normalized = float(value) * 100 if 0 <= value <= 1 else float(value)
            return max(0.0, min(normalized, 100.0))
        return None


def prioritize_recommendations(
    recommendations: Iterable[Mapping[str, Any]],
    **kwargs: Any,
) -> list[dict[str, Any]]:
    return RecommendationPriorityService().prioritize(recommendations, **kwargs)
