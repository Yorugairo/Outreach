from __future__ import annotations

import pytest

from src.models import OwnedMeasurementSnapshot
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.demand_conversion_service import DemandConversionService
from src.services.report_validation_service import (
    DemandConversionReportValidationService,
)
from tests.test_demand_conversion_model import (
    SHA,
    _assumptions,
    _demand,
    _economics,
)


def _owner(snapshot_id: str, source: str, metrics: dict) -> OwnedMeasurementSnapshot:
    return OwnedMeasurementSnapshot(
        id=snapshot_id,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source=source,
        period_start="2026-04-01",
        period_end="2026-06-30",
        source_sha256=SHA,
        context={"market": "Tacoma, WA"},
        metrics=metrics,
        artifact_ref=f"owned_measurements/{snapshot_id}.json",
    )


def _persist_inputs(repository):
    demand = repository.save_demand_evidence_set(_demand())
    economics = repository.save_business_economics_profile(_economics())
    return demand, economics


def test_prospect_mode_is_public_only_and_approval_is_an_immutable_successor(
    tmp_path,
) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand, economics = _persist_inputs(repository)
    service = DemandConversionService(repository)
    draft = service.build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=demand,
        economics=economics,
        assumptions=_assumptions(include_rates=True),
    )
    approved = service.approve(draft.id, operator="operator")

    assert approved.id != draft.id
    assert approved.predecessor_id == draft.id
    assert repository.get_demand_conversion_evidence(draft.id).state == "draft"
    validation = DemandConversionReportValidationService(repository).validate(
        approved.id,
        requested_mode="prospect",
        for_export=True,
    )
    assert validation["privacy"] == "public_and_supplied_only"
    assert validation["valid"] is True

    with pytest.raises(ValueError, match="cannot be changed"):
        DemandConversionReportValidationService(repository).validate(
            approved.id,
            requested_mode="owner_verified",
            for_export=True,
        )


def test_owner_verified_mode_requires_persisted_owner_refs(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand, economics = _persist_inputs(repository)
    owner = [
        repository.save_owned_measurement_snapshot(
            _owner("gsc-1", "gsc_csv", {"impressions": 100, "clicks": 10})
        ),
        repository.save_owned_measurement_snapshot(
            _owner("ga4-1", "ga4_csv", {"sessions": 50})
        ),
        repository.save_owned_measurement_snapshot(
            _owner(
                "crm-1",
                "crm_csv",
                {"signups": 5, "appointments": 4, "customers": 2},
            )
        ),
    ]
    service = DemandConversionService(repository)
    draft = service.build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        mode="owner_verified",
        demand=demand,
        economics=economics,
        owner_snapshots=owner,
        assumptions=_assumptions(include_rates=False),
    )
    approved = service.approve(draft.id, operator="operator")
    payload = DemandConversionReportValidationService(repository).client_payload(
        approved.id,
        requested_mode="owner_verified",
    )

    assert payload["mode"] == "owner_verified"
    assert payload["validation"]["privacy"] == "owner_aggregate"
    assert {
        ref["id"]
        for ref in payload["evidence_refs"]
        if ref.get("kind") == "owned_measurement"
    } == {"gsc-1", "ga4-1", "crm-1"}


def test_draft_or_missing_reference_cannot_export(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand, economics = _persist_inputs(repository)
    draft = DemandConversionService(repository).build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=demand,
        economics=economics,
        assumptions=_assumptions(include_rates=True),
    )
    validator = DemandConversionReportValidationService(repository)
    with pytest.raises(ValueError, match="requires approved"):
        validator.validate(draft.id, for_export=True)

    approved = DemandConversionService(repository).approve(
        draft.id,
        operator="operator",
    )
    demand_path = repository.demand_evidence_sets_dir / f"{demand.id}.json"
    demand_path.rename(demand_path.with_suffix(".missing"))
    with pytest.raises(ValueError, match="missing or mismatched"):
        validator.validate(approved.id, for_export=True)


def test_missing_public_artifact_cannot_export(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand, economics = _persist_inputs(repository)
    draft = DemandConversionService(repository).build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=demand,
        economics=economics,
        assumptions=_assumptions(include_rates=True),
        public_sources=[
            {
                "source_name": "public_serp_sample",
                "source_class": "public_observed",
                "hierarchy_level": 4,
                "provenance_label": "observed",
                "source_sha256": SHA,
                "artifact_ref": "runs/run-1/market/missing-serp.json",
                "snapshot_date": "2026-07-26",
            }
        ],
    )
    approved = DemandConversionService(repository).approve(
        draft,
        operator="operator",
    )

    with pytest.raises(ValueError, match="referenced artifact is missing"):
        DemandConversionReportValidationService(repository).validate(
            approved,
            requested_mode="prospect",
            for_export=True,
        )
