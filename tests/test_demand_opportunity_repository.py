from __future__ import annotations

from pathlib import Path

import pytest

from src.models import (
    AcquisitionCalibrationRecord,
    BusinessEconomicsProfile,
    DemandEvidenceRow,
    DemandEvidenceSet,
    DemandGroup,
    OpportunityScenario,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository


def _repositories(tmp_path: Path):
    return [
        FileBackedInsightRepository(tmp_path / "files"),
        SQLiteInsightRepository(tmp_path / "seo-insights.db", tmp_path / "artifacts"),
    ]


def _demand(*, id: str = "demand-1", predecessor_id: str | None = None) -> DemandEvidenceSet:
    row = DemandEvidenceRow(
        keyword="bjj tacoma", market="Tacoma, WA", source="operator_csv",
        snapshot_period="2026-07", match_semantics="close_variants", source_row=2,
    )
    group = DemandGroup(
        intent_family="local_program", included_keyword_ids=[row.id], representative_term="bjj tacoma",
        aggregation_rule="max_close_variant", approved_monthly_search_occasions=100,
    )
    return DemandEvidenceSet(
        id=id, predecessor_id=predecessor_id, prospect_id="prospect-1", keyword_set_id="keywords-1",
        vertical_id="national_bjj_registry", market="Tacoma, WA", source_sha256="a" * 64,
        rows=[row.to_dict()], groups=[group.to_dict()], snapshot_period="2026-07",
    )


def _economics(*, id: str = "economics-1", predecessor_id: str | None = None) -> BusinessEconomicsProfile:
    return BusinessEconomicsProfile(
        id=id, predecessor_id=predecessor_id, prospect_id="prospect-1", vertical_id="national_bjj_registry",
        revenue_model="membership", monthly_price=100, currency="USD", capacity_headroom=20,
        field_provenance={"monthly_price": "business_supplied", "capacity_headroom": "business_supplied"},
    )


def _scenario(*, id: str = "scenario-1", predecessor_id: str | None = None) -> OpportunityScenario:
    assumptions = {band: {} for band in ("low", "base", "high")}
    outputs = {band: {} for band in ("low", "base", "high")}
    return OpportunityScenario(
        id=id, predecessor_id=predecessor_id, insight_run_id="run-1", prospect_id="prospect-1",
        demand_evidence_set_id="demand-1", demand_evidence_version=1,
        economics_profile_id="economics-1", economics_profile_version=1,
        assumptions=assumptions, outputs=outputs,
    )


def _calibration(*, id: str = "calibration-1") -> AcquisitionCalibrationRecord:
    return AcquisitionCalibrationRecord(
        id=id, prospect_id="prospect-1", vertical_id="national_bjj_registry", market="Tacoma, WA",
        source="ga4", period_start="2026-07-01", period_end="2026-07-31",
        artifact_ref={"path": "calibration/2026-07.json"}, clicks=10, total_users=8,
    )


def test_demand_opportunity_records_are_immutable_and_filterable(tmp_path: Path):
    for repository in _repositories(tmp_path):
        demand = repository.save_demand_evidence_set(_demand())
        economics = repository.save_business_economics_profile(_economics())
        scenario = repository.save_opportunity_scenario(_scenario())
        calibration = repository.save_acquisition_calibration_record(_calibration())

        assert repository.get_demand_evidence_set(demand.id).source_sha256 == "a" * 64
        assert repository.list_demand_evidence_sets(prospect_id="prospect-1")[0].id == demand.id
        assert repository.get_business_economics_profile(economics.id).capacity_headroom == 20
        assert repository.list_business_economics_profiles(vertical_id="national_bjj_registry")[0].id == economics.id
        assert repository.get_opportunity_scenario(scenario.id).formula_version == "opportunity-formula.v1"
        assert repository.list_opportunity_scenarios(insight_run_id="run-1")[0].id == scenario.id
        assert repository.get_acquisition_calibration_record(calibration.id).source == "ga4"
        assert repository.list_acquisition_calibration_records(market="Tacoma, WA")[0].id == calibration.id

        with pytest.raises(ValueError, match="immutable"):
            repository.save_demand_evidence_set(DemandEvidenceSet(**{**demand.to_dict(), "market": "Seattle, WA"}))


def test_successor_attribution_survives_reopen(tmp_path: Path):
    repository = SQLiteInsightRepository(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    predecessor = repository.save_demand_evidence_set(_demand())
    successor = repository.save_demand_evidence_set(_demand(id="demand-2", predecessor_id=predecessor.id))
    economics = repository.save_business_economics_profile(_economics())
    scenario = repository.save_opportunity_scenario(_scenario())
    calibration = repository.save_acquisition_calibration_record(_calibration())
    repository.close()

    reopened = SQLiteInsightRepository(tmp_path / "db.sqlite3", tmp_path / "artifacts")
    assert reopened.list_demand_evidence_sets(predecessor_id=predecessor.id)[0].id == successor.id
    assert reopened.get_business_economics_profile(economics.id).id == economics.id
    assert reopened.get_opportunity_scenario(scenario.id).id == scenario.id
    assert reopened.get_acquisition_calibration_record(calibration.id).id == calibration.id

