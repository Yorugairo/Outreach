from __future__ import annotations

from pathlib import Path

import pytest

from src.models import AcquisitionCalibrationRecord
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.calibration_service import CalibrationService
from src.services.opportunity_model_service import OpportunityModelService
from tests.test_opportunity_model import _assumptions, _demand, _economics


CSV = """period_start,period_end,source,impressions,clicks,total_users,signups,attended_trials,new_customers,spend
2026-06-01,2026-06-30,ga4_crm,1000,100,80,20,10,5,250
"""


def test_aggregate_preview_and_metrics_are_deterministic():
    preview = CalibrationService().preview_csv(
        CSV,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
    )
    assert preview.valid
    record = preview.records[0]
    metrics = CalibrationService.observed_metrics(
        record,
        capacity_headroom=20,
    )
    assert metrics == {
        "sessions_per_user": 1.25,
        "visit_to_signup": 0.2,
        "attendance_rate": 0.5,
        "close_rate": 0.5,
        "cost_per_signup": 12.5,
        "cost_per_customer": 50.0,
        "capacity_fill_rate": 0.25,
    }


def test_preview_rejects_pii_formulas_negative_and_impossible_funnel():
    text = (
        "period_start,period_end,source,email,clicks,signups,attended_trials,new_customers\n"
        "2026-06-01,2026-06-30,crm,a@example.com,=100,10,11,-1\n"
    )
    preview = CalibrationService().preview_csv(
        text,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
    )
    assert not preview.valid
    assert any("PII" in issue.message for issue in preview.issues)
    assert any("formula" in issue.message for issue in preview.issues)
    with pytest.raises(ValueError, match="paths"):
        CalibrationService().preview_csv(
            Path("private.csv"),
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
        )


def test_zero_denominators_are_unknown_not_zero():
    record = AcquisitionCalibrationRecord(
        prospect_id="prospect-1",
        vertical_id="one_trade_network",
        market="Tacoma, WA",
        source="crm",
        period_start="2026-06-01",
        period_end="2026-06-30",
        clicks=0,
        total_users=0,
        signups_or_leads=0,
        attended_or_appointments=0,
        new_customers=0,
        spend=0,
        artifact_ref={"source_sha256": "a" * 64, "source_row": 2},
    )
    assert all(
        value is None
        for value in CalibrationService.observed_metrics(record).values()
    )


def test_calibration_creates_successor_and_preserves_original(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    demand = repository.save_demand_evidence_set(_demand())
    economics = repository.save_business_economics_profile(_economics())
    original = OpportunityModelService(repository).create_scenario(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        economics=economics,
        demand=demand,
        assumptions=_assumptions(),
    )
    service = CalibrationService(repository)
    calibration = service.commit(
        service.preview_csv(
            CSV,
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
        )
    )[0]

    successor = service.calibrate_scenario(original.id, calibration.id)

    assert successor.id != original.id
    assert successor.predecessor_id == original.id
    assert successor.calibrated_from_id == calibration.id
    assert successor.assumptions["base"]["visit_to_signup_rate"] == {
        "value": 0.2,
        "provenance": "aggregate_calibration",
        "reviewed": True,
        "material": True,
    }
    assert repository.get_opportunity_scenario(original.id).calibrated_from_id is None
