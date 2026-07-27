"""Offline evaluation harness for frozen product-strength pilot packs."""

from __future__ import annotations

from typing import Any, Mapping

from src.models import (
    AgenticAssessmentReviewEvent,
    AgenticAssessmentSnapshot,
    AgenticFinding,
    canonical_sha256,
)
from src.services.agentic_evaluation_service import AgenticEvaluationService


class ProductStrengthPilotService:
    CONTRACT_VERSION = "product-strength-pilot.v1"

    def evaluate(self, fixture: Mapping[str, Any]) -> dict[str, Any]:
        if fixture.get("contract_version") != self.CONTRACT_VERSION:
            raise ValueError("unsupported product-strength pilot contract")
        cases = fixture.get("cases")
        routes = fixture.get("routes")
        repeats = int(fixture.get("repeats_per_route") or 0)
        if not isinstance(cases, list) or len(cases) < 22:
            raise ValueError("pilot harness requires Nova, Lacey, and 20 additional packs")
        if not isinstance(routes, list) or len(routes) < 2 or repeats < 2:
            raise ValueError("pilot harness requires two model routes and repeated outputs")

        assessments: list[AgenticAssessmentSnapshot] = []
        events: list[AgenticAssessmentReviewEvent] = []
        labels: dict[str, bool] = {}
        durations: dict[str, float] = {}
        metadata: dict[str, dict[str, Any]] = {}
        for case in cases:
            pack_hash = canonical_sha256(
                {
                    "fixture_contract": self.CONTRACT_VERSION,
                    "case_id": case["id"],
                    "target_domain": case["target_domain"],
                    "vertical_id": case["vertical_id"],
                }
            )
            metadata[pack_hash] = {
                "target_domain": case["target_domain"],
                "vertical_id": case["vertical_id"],
                "source_kind": fixture.get("source_kind"),
                "human_reviewed": False,
            }
            for route in routes:
                for repeat in range(1, repeats + 1):
                    assessment_id = (
                        f"fixture-{case['id']}-"
                        f"{canonical_sha256(route)[:8]}-{repeat}"
                    )
                    findings = self._findings(case["vertical_id"])
                    assessment = AgenticAssessmentSnapshot(
                        id=assessment_id,
                        job_id=f"job-{assessment_id}",
                        evidence_pack_id=f"pack-{case['id']}",
                        evidence_pack_sha256=pack_hash,
                        runtime="frozen-evaluation-harness",
                        requested_model=str(route["model"]),
                        served_model=str(route["model"]),
                        served_provider=str(route["provider"]),
                        prompt_version="outreach-analysis.prompt.v1",
                        rubric_version="outreach-analysis.rubric.v1",
                        schema_version="agentic-assessment.v1",
                        findings=findings,
                        validation_result={
                            "schema_valid": True,
                            "customer_safe": True,
                            "invalid_reference_count": 0,
                            "unsupported_exported_claims": 0,
                            "fixture_only": True,
                        },
                        call_ids=[f"call-{assessment_id}"],
                        total_cost_usd=float(route["cost_usd"]),
                        total_latency_ms=500,
                    )
                    assessments.append(assessment)
                    events.append(
                        AgenticAssessmentReviewEvent(
                            assessment_id=assessment.id,
                            event_type="approved",
                            operator="fixture-harness",
                            reason_code="synthetic_contract_expectation",
                        )
                    )
                    labels[assessment.id] = True
                    durations[assessment.id] = float(case["review_minutes"])

        evaluation = AgenticEvaluationService().summarize(
            assessments,
            events,
            service_fit_labels=labels,
            review_durations_minutes=durations,
            sample_metadata=metadata,
        )
        return {
            "contract_version": self.CONTRACT_VERSION,
            "benchmark_class": "internal_fixture_dry_run",
            "disclosure": fixture.get("disclosure"),
            "case_count": len(cases),
            "assessment_count": len(assessments),
            "targets": [case["target_domain"] for case in cases],
            "vertical_counts": {
                vertical: sum(case["vertical_id"] == vertical for case in cases)
                for vertical in sorted({case["vertical_id"] for case in cases})
            },
            "routes": routes,
            "repeats_per_route": repeats,
            "evaluation": evaluation,
            "routine_agent_enabled": False,
            "required_next_gate": (
                "Replace synthetic fixtures with recorded DeepSeek and GPT/Codex "
                "outputs, then obtain real human reviews for all 22 packs."
            ),
        }

    @staticmethod
    def _findings(vertical_id: str) -> list[dict[str, Any]]:
        service = (
            "national_bjj_registry_visibility"
            if vertical_id == "national_bjj_registry"
            else "one_trade_network_visibility"
        )
        return [
            AgenticFinding(
                id=f"recommendation-{index}",
                claim_type="recommendation",
                title=title,
                claim=claim,
                confidence="high",
                severity="high" if index == 1 else "medium",
                commercial_relevance="Maps to an approved outreach offer.",
                service_fit=[service],
                evidence_refs=[
                    {
                        "artifact_path": "pages/page-1.json",
                        "field": "title",
                        "reason": "Frozen contract fixture.",
                        "observed": "Fixture evidence",
                    }
                ],
                customer_safe=True,
            ).to_dict()
            for index, (title, claim) in enumerate(
                (
                    ("Clarify the primary conversion path", "Make the next step explicit."),
                    ("Strengthen service or program coverage", "Match approved intent with a useful page."),
                    ("Add visible trust evidence", "Surface attributable business proof."),
                ),
                start=1,
            )
        ]
