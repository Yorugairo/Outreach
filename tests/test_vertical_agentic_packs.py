from __future__ import annotations

import dataclasses

import pytest

from src.models import VerticalAgenticPack
from src.services.vertical_agentic_reconciliation_service import VerticalAgenticReconciliationService
from src.vertical_agentic_packs import (
    NATIONAL_BJJ_REGISTRY_AGENTIC_V1,
    ONE_TRADE_NETWORK_AGENTIC_V1,
    SERVICE_PACKAGE_IDS,
    get_vertical_agentic_pack,
    list_vertical_agentic_packs,
    reconcile_vertical_agentic_pack,
)


def test_both_reviewed_packs_have_exact_bounded_journeys_and_real_offers() -> None:
    packs = list_vertical_agentic_packs()
    assert {pack.version for pack in packs} == {
        "national_bjj_registry.agentic.v1",
        "one_trade_network.agentic.v1",
    }
    for pack in packs:
        assert pack.state == "approved"
        assert len(pack.source_sha256) == 64
        assert len(pack.journey_tasks) == 3
        assert {task["task_kind"] for task in pack.journey_tasks} == {
            "offer_discovery",
            "decision_resolution",
            "ready_to_convert_cta",
        }
        assert {task["viewport"] for task in pack.journey_tasks} == {"desktop", "mobile"}
        assert all(task["success_oracle"]["requires_form_submission"] is False for task in pack.journey_tasks)
        assert set(pack.service_mappings) == set(SERVICE_PACKAGE_IDS)
        assert all(isinstance(question["applicability"], dict) for question in pack.buyer_questions)
        assert all(question["reviewed"] is True for question in pack.buyer_questions)


def test_pack_loader_is_immutable_and_supports_legacy_vertical_aliases() -> None:
    loaded = get_vertical_agentic_pack("national_bjj_registry.v1")
    loaded.buyer_questions[0]["question"] = "mutated"
    assert get_vertical_agentic_pack("national_bjj_registry.agentic.v1").buyer_questions[0]["question"] != "mutated"
    assert get_vertical_agentic_pack("one_trade_network").vertical_id == "one_trade_network"
    with pytest.raises(ValueError, match="unknown vertical agentic pack"):
        get_vertical_agentic_pack("unknown.agentic.v1")


def test_reconciliation_exposes_exact_skip_reason() -> None:
    result = reconcile_vertical_agentic_pack("national_bjj_registry.agentic.v1", qualified=False)
    assert result.eligible is False
    assert "not qualified" in result.reason
    result = VerticalAgenticReconciliationService().resolve(
        {"vertical_pack_version": "one_trade_network.v1", "qualification_status": "qualified"}
    )
    assert result.eligible is True
    assert result.pack is not None


def test_contract_remains_typed_and_does_not_add_a_score_surface() -> None:
    assert dataclasses.is_dataclass(NATIONAL_BJJ_REGISTRY_AGENTIC_V1)
    assert dataclasses.is_dataclass(ONE_TRADE_NETWORK_AGENTIC_V1)
    assert "score" not in {item.name for item in dataclasses.fields(VerticalAgenticPack)}
