from src.models import (
    AgenticAssessmentReviewEvent,
    AgenticAssessmentSnapshot,
    AgenticFinding,
)
from src.services.agentic_evaluation_service import AgenticEvaluationService


def _assessment(identity: str) -> AgenticAssessmentSnapshot:
    findings = [
        AgenticFinding(
            claim_type="recommendation",
            title=title,
            claim=f"Action: {title}",
            confidence="high",
            severity="high",
            commercial_relevance="Material.",
            service_fit=["vertical_plugin_embed"],
            evidence_refs=[
                {
                    "artifact_path": "pages/page-1.json",
                    "field": "title",
                    "reason": "Persisted.",
                    "observed": "Nova Ryu",
                }
            ],
            customer_safe=True,
        ).to_dict()
        for title in ("Signup path", "Program clarity", "Trust proof")
    ]
    return AgenticAssessmentSnapshot(
        id=identity,
        job_id=f"job-{identity}",
        evidence_pack_id="pack-1",
        evidence_pack_sha256="a" * 64,
        runtime="hermes-openrouter",
        requested_model="deepseek/deepseek-v4-flash",
        served_model="deepseek/deepseek-v4-flash",
        served_provider="openrouter",
        prompt_version="prompt.v1",
        rubric_version="rubric.v1",
        schema_version="agentic-assessment.v1",
        findings=findings,
        validation_result={
            "schema_valid": True,
            "customer_safe": True,
            "invalid_reference_count": 0,
            "unsupported_exported_claims": 0,
        },
        call_ids=[f"call-{identity}"],
        total_cost_usd=0.02,
    )


def test_promotion_summary_requires_measured_human_and_stability_gates():
    assessments = [_assessment("one"), _assessment("two")]
    events = [
        AgenticAssessmentReviewEvent(
            assessment_id=item.id,
            event_type="approved",
            operator="operator",
            reason_code="evidence_verified",
        )
        for item in assessments
    ]

    result = AgenticEvaluationService().summarize(
        assessments,
        events,
        service_fit_labels={"one": True, "two": True},
    )

    assert result["metrics"]["schema_validity_rate"] == 1.0
    assert result["metrics"]["top_three_overlap"] == 1.0
    assert result["metrics"]["service_fit_agreement"] == 1.0
    assert result["gates"]["schema_validity"] is True
    assert result["gates"]["recommendation_stability"] is True
    assert result["gates"]["sample_policy"] is False
    assert result["gates"]["sample_authenticity"] is False
    assert result["promotion_ready"] is False
