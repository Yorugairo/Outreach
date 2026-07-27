from __future__ import annotations

from typing import Any, Mapping

from src.models import PageRecord, ScoreCheckResult


class PerformanceEvidenceService:
    """Normalize optional persisted CrUX/Lighthouse evidence without fetching it."""

    @classmethod
    def build_field_page_experience_check(
        cls,
        pages: list[PageRecord],
        evidence_by_page: Mapping[str, Mapping[str, Any]] | None,
    ) -> ScoreCheckResult:
        applicable = [page.id for page in pages]
        if not pages:
            return ScoreCheckResult(
                check_id="field_page_experience",
                check_version=1,
                family="mobile_performance",
                severity="medium",
                status="inapplicable",
                score_affecting=True,
            )
        evidence_by_page = evidence_by_page or {}
        observed: list[tuple[PageRecord, Mapping[str, Any], bool]] = []
        refs: list[dict[str, Any]] = []
        for page in pages:
            payload = evidence_by_page.get(page.id) or evidence_by_page.get(page.url)
            if not isinstance(payload, Mapping):
                continue
            passed = cls._passes(payload)
            if passed is None:
                continue
            observed.append((page, payload, passed))
            refs.append(
                {
                    "artifact_path": str(
                        payload.get("artifact_ref")
                        or f"performance/{page.id}.json"
                    ),
                    "field": "metrics",
                    "reason": "Persisted CrUX or Lighthouse page-experience evidence.",
                    "observed": dict(payload),
                }
            )
        if not observed:
            return ScoreCheckResult(
                check_id="field_page_experience",
                check_version=1,
                family="mobile_performance",
                severity="medium",
                status="unknown",
                score_affecting=True,
                applicable_page_ids=applicable,
                limitations=[
                    "No persisted CrUX or Lighthouse evidence was available; "
                    "performance was not inferred from HTML or screenshots."
                ],
            )
        affected = [page.id for page, _payload, passed in observed if not passed]
        confidence = len(observed) / len(pages)
        score = sum(1 for _page, _payload, passed in observed if passed) / len(observed) * 100
        return ScoreCheckResult(
            check_id="field_page_experience",
            check_version=1,
            family="mobile_performance",
            severity="medium",
            status="failed" if affected else "measured",
            score_affecting=True,
            applicable_page_ids=applicable,
            affected_page_ids=affected,
            weighted_affected_ratio=len(affected) / len(observed),
            evidence_confidence=confidence,
            score=round(score, 4),
            evidence_refs=refs,
            limitations=(
                []
                if len(observed) == len(pages)
                else [f"Performance evidence covered {len(observed)} of {len(pages)} applicable pages."]
            ),
            remediation=(
                "Measure affected templates with CrUX and Lighthouse, then improve "
                "Core Web Vitals without treating lab data as field traffic."
            ),
        )

    @staticmethod
    def _passes(payload: Mapping[str, Any]) -> bool | None:
        status = str(payload.get("status", "")).casefold()
        if status in {"good", "pass", "passed"}:
            return True
        if status in {"poor", "failed", "needs_improvement"}:
            return False
        metrics = payload.get("metrics")
        if not isinstance(metrics, Mapping):
            return None
        web_vitals = [
            ("lcp_ms", 2500.0),
            ("inp_ms", 200.0),
            ("cls", 0.1),
        ]
        known_vitals = [
            float(metrics[name]) <= threshold
            for name, threshold in web_vitals
            if isinstance(metrics.get(name), (int, float))
        ]
        if known_vitals:
            return all(known_vitals)
        performance_score = metrics.get("performance_score")
        if isinstance(performance_score, (int, float)):
            normalized = float(performance_score)
            if normalized <= 1:
                normalized *= 100
            return normalized >= 90
        return None
