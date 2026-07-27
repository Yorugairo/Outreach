from __future__ import annotations

import json
from pathlib import Path

from src.services.product_strength_pilot_service import (
    ProductStrengthPilotService,
)


def test_frozen_two_vertical_harness_measures_every_gate_without_self_promotion():
    fixture = json.loads(
        (
            Path(__file__).parent
            / "fixtures"
            / "product_strength_pilot_v1.json"
        ).read_text(encoding="utf-8")
    )
    result = ProductStrengthPilotService().evaluate(fixture)
    evaluation = result["evaluation"]

    assert result["case_count"] == 22
    assert result["assessment_count"] == 88
    assert {"novaryu.com", "laceyglass.com"}.issubset(result["targets"])
    assert result["vertical_counts"] == {
        "national_bjj_registry": 11,
        "one_trade_network": 11,
    }
    assert evaluation["metrics"]["median_review_time_minutes"] < 10
    assert evaluation["metrics"]["mean_cost_usd"] < 0.10
    assert evaluation["metrics"]["gpt_escalation_rate"] < 0.20
    assert evaluation["metrics"]["unsupported_exported_claims"] == 0
    assert evaluation["gates"]["sample_policy"] is True
    assert evaluation["gates"]["sample_authenticity"] is False
    assert evaluation["promotion_ready"] is False
    assert result["routine_agent_enabled"] is False
