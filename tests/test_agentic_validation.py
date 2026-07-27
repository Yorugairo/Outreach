from pathlib import Path

from src.models import SiteEvidencePack
from src.services.agentic_validation_service import AgenticValidationService


def _pack() -> SiteEvidencePack:
    return SiteEvidencePack(
        run_id="run-1",
        attempt_id="attempt-1",
        source_snapshot_ids={},
        source_hashes={},
        target_facts={"business_name": "Nova Ryu"},
        page_facts=[],
        deterministic_surfaces={},
        evidence_refs=[],
        permitted_service_mappings={
            "vertical_plugin_embed": "BJJ-specific embed",
        },
    )


def test_validator_resolves_refs_and_enforces_service_mapping(tmp_path: Path):
    page = tmp_path / "runs" / "run-1" / "pages" / "page-1.json"
    page.parent.mkdir(parents=True)
    page.write_text(
        '{"attempt_id":"attempt-1","title":"Nova Ryu"}',
        encoding="utf-8",
    )
    result = AgenticValidationService(tmp_path).validate(
        _pack(),
        {
            "findings": [
                {
                    "claim_type": "recommendation",
                    "title": "Clarify signup",
                    "claim": "Make the signup action visible.",
                    "confidence": "high",
                    "severity": "high",
                    "commercial_relevance": "Clarifies the next step.",
                    "service_fit": ["vertical_plugin_embed"],
                    "evidence_refs": [
                        {
                            "artifact_path": "pages/page-1.json",
                            "field": "title",
                            "reason": "Persisted page evidence.",
                            "observed": "Nova Ryu",
                        }
                    ],
                }
            ]
        },
    )
    assert result["validation_result"]["customer_safe"] is True
    assert result["validation_result"]["evidence_precision"] == 1.0
    assert result["findings"][0]["customer_safe"] is True

    invalid = AgenticValidationService(tmp_path).validate(
        _pack(),
        {
            "findings": [
                {
                    "claim_type": "recommendation",
                    "title": "Unsupported mapping",
                    "claim": "Use an unsupported service.",
                    "confidence": "low",
                    "severity": "low",
                    "commercial_relevance": "Unknown.",
                    "service_fit": ["autonomous_email"],
                    "evidence_refs": [],
                }
            ]
        },
    )
    assert invalid["validation_result"]["requires_review"] is True
    assert invalid["findings"][0]["customer_safe"] is False
    assert invalid["findings"][0]["service_fit"] == []
