from __future__ import annotations

from dataclasses import replace

import pytest

from src.models import DemandConversionEvidence
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.demand_conversion_service import DemandConversionService
from src.services.report_validation_service import (
    DemandConversionReportValidationService,
)
from tests.test_demand_conversion_model import (
    _assumptions,
    _demand,
    _economics,
)


def test_nested_private_fields_are_blocked_at_report_boundary(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand = repository.save_demand_evidence_set(_demand())
    economics = repository.save_business_economics_profile(_economics())
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
    payload = draft.to_dict()
    payload["id"] = "private-payload"
    payload["observed_inputs"]["funnel_baseline"] = {
        "metrics": {"clicks": 10},
        "raw": {"email": "person@example.test"},
    }
    private = DemandConversionEvidence(**payload)
    repository.save_demand_conversion_evidence(private)

    with pytest.raises(ValueError, match="private field"):
        DemandConversionReportValidationService(repository).validate(private.id)


def test_cross_prospect_and_unsafe_artifact_refs_fail_closed(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand = repository.save_demand_evidence_set(_demand())
    economics = repository.save_business_economics_profile(_economics())
    draft = DemandConversionService(repository).build(
        insight_run_id="run-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=demand,
        economics=economics,
        assumptions=_assumptions(include_rates=True),
    )

    unsafe_payload = draft.to_dict()
    unsafe_payload["id"] = "unsafe-source"
    unsafe_payload["source_snapshots"][0]["artifact_ref"] = "../escape.json"
    unsafe = DemandConversionEvidence(**unsafe_payload)
    repository.save_demand_conversion_evidence(unsafe)
    with pytest.raises(ValueError, match="repository-relative"):
        DemandConversionReportValidationService(repository).validate(unsafe.id)

    mismatch_payload = draft.to_dict()
    mismatch_payload["id"] = "mismatched-ref"
    mismatch_payload["evidence_refs"][0]["id"] = "missing-demand"
    mismatched = DemandConversionEvidence(**mismatch_payload)
    repository.save_demand_conversion_evidence(mismatched)
    with pytest.raises(ValueError, match="missing or mismatched"):
        DemandConversionReportValidationService(repository).validate(
            mismatched.id
        )


def test_prospect_client_payload_has_no_owner_baseline(tmp_path) -> None:
    repository = FileBackedInsightRepository(tmp_path)
    demand = repository.save_demand_evidence_set(_demand())
    economics = repository.save_business_economics_profile(_economics())
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
    payload = DemandConversionReportValidationService(repository).client_payload(
        approved.id,
        requested_mode="prospect",
    )

    assert payload["observed_inputs"]["funnel_baseline"]["status"] == "unknown"
    assert all(
        source["source_class"] != "owner_first_party"
        for source in payload["source_snapshots"]
    )
