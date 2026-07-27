from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

from src.models import InsightRun
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.demand_conversion_reporting_service import (
    DemandConversionReportingService,
)
from src.services.demand_conversion_service import DemandConversionService
from src.services.report_validation_service import (
    DemandConversionReportValidationService,
)
from tests.test_demand_conversion_model import _demand, _economics


FIXTURE = Path("tests/fixtures/demand_conversion_pilot_v1.json")


def test_nova_and_lacey_prospect_pilot_is_reproducible_and_resolved(tmp_path):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    repository = FileBackedInsightRepository(tmp_path / "artifacts")
    outputs = {}

    for case in fixture["cases"]:
        case_id = case["case_id"]
        prospect_id = f"prospect-{case_id}"
        run = InsightRun(
            id=f"run-{case_id}",
            seo_target_id=f"target-{case_id}",
            requested_url=f"https://{case_id}.example/",
            requested_domain=f"{case_id}.example",
            status="completed",
            current_stage="completed",
            attempt_id=f"attempt-{case_id}",
            summary={"overall_score": 70},
        )
        repository.create_run(run)
        demand = repository.save_demand_evidence_set(
            replace(
                _demand(),
                id=f"demand-{case_id}",
                prospect_id=prospect_id,
                vertical_id=case["vertical_id"],
                market=case["market"],
            )
        )
        economics = repository.save_business_economics_profile(
            replace(
                _economics(),
                id=f"economics-{case_id}",
                prospect_id=prospect_id,
                vertical_id=case["vertical_id"],
                monthly_price=case["monthly_price"],
                capacity_headroom=case["capacity_headroom"],
            )
        )
        service = DemandConversionService(repository)
        draft = service.build(
            insight_run_id=run.id,
            prospect_id=prospect_id,
            vertical_id=case["vertical_id"],
            market=case["market"],
            mode="prospect",
            demand=demand,
            economics=economics,
            assumptions=case["assumptions"],
            target_id=run.seo_target_id,
            normalized_domain=run.requested_domain,
            attempt_id=run.attempt_id,
        )
        approved = service.approve(draft, operator="pilot-operator")
        reports = DemandConversionReportingService(repository).assemble(
            approved,
            requested_mode="prospect",
            for_export=True,
        )
        validation = DemandConversionReportValidationService(repository).validate(
            approved,
            requested_mode="prospect",
            for_export=True,
        )
        payload = reports["demand-conversion-v1"].report_payload

        assert validation["valid"] is True
        assert validation["resolved_reference_count"] == len(
            approved.evidence_refs
        )
        assert validation["resolved_reference_count"] / max(
            1, len(approved.evidence_refs)
        ) >= 0.9
        assert payload["mode"] == "prospect"
        assert "owner_first_party" not in json.dumps(payload, sort_keys=True)
        assert "@" not in json.dumps(payload, sort_keys=True)
        assert payload["limitations"]
        assert payload["observed_vs_modeled_funnel"]["formula"]["version"] == (
            fixture["formula_version"]
        )
        for band in ("low", "base", "high"):
            modeled = approved.modeled_outputs[band]
            assert modeled["incremental_members"] <= case["capacity_headroom"]
            assert modeled["incremental_recurring_revenue"] == pytest.approx(
                modeled["incremental_members"] * case["monthly_price"]
            )
        outputs[case_id] = approved.modeled_outputs

    assert set(outputs) == {
        "nova-ryu-tacoma-prospect",
        "lacey-glass-trades-prospect",
    }
