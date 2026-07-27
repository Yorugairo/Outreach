from __future__ import annotations

import json
from pathlib import Path

from src.services.recommendation_priority_service import (
    RecommendationPriorityService,
)


def test_priority_uses_all_eight_dimensions_and_is_deterministic():
    fixture = json.loads(
        (
            Path(__file__).parent
            / "fixtures"
            / "nova_ryu_product_strength.json"
        ).read_text(encoding="utf-8")
    )
    service = RecommendationPriorityService()
    first = service.prioritize(
        fixture["recommendations"],
        total_pages=fixture["total_pages"],
    )
    second = service.prioritize(
        reversed(fixture["recommendations"]),
        total_pages=fixture["total_pages"],
    )

    assert [item["id"] for item in first] == [
        "online-trial-path",
        "program-answers",
        "decorative-polish",
    ]
    assert [item["id"] for item in first] == [item["id"] for item in second]
    assert set(first[0]["priority_components"]) == set(service.WEIGHTS)
    assert first[0]["priority_completeness_percent"] == 100
    assert first[0]["priority_version"] == "recommendation-priority.v1"


def test_unknown_priority_inputs_are_removed_from_arithmetic_and_disclosed():
    result = RecommendationPriorityService().score(
        {"id": "limited", "severity": "high", "confidence": "medium"}
    )
    assert result["priority_score"] > 0
    assert result["priority_completeness_percent"] == 33
    assert "current_visibility" in result["priority_unknown_dimensions"]
