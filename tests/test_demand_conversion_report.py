from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from src.models import (
    InsightReport,
    InsightRun,
    OwnedMeasurementSnapshot,
    canonical_sha256,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.services.demand_conversion_reporting_service import (
    DemandConversionReportingService,
)
from src.services.demand_conversion_service import DemandConversionService
from tests.test_demand_conversion_model import _assumptions, _demand, _economics


def _repository(tmp_path: Path) -> tuple[FileBackedInsightRepository, InsightRun]:
    repository = FileBackedInsightRepository(tmp_path / "artifacts")
    run = InsightRun(
        id="run-report-1",
        seo_target_id="target-report-1",
        requested_url="https://example.test/",
        requested_domain="example.test",
        status="completed",
        current_stage="completed",
        attempt_id="attempt-report-1",
        summary={"overall_score": 72},
    )
    repository.create_run(run)
    return repository, run


def _evidence(repository: FileBackedInsightRepository, run: InsightRun):
    demand = repository.save_demand_evidence_set(_demand())
    economics = repository.save_business_economics_profile(_economics())
    return DemandConversionService(repository).build(
        insight_run_id=run.id,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        demand=demand,
        economics=economics,
        assumptions=_assumptions(include_rates=True),
    )


def _legacy(repository: FileBackedInsightRepository, run: InsightRun, version: str) -> InsightReport:
    payload = {
        "report_contract": version,
        "executive_summary": "Existing SEO evidence remains available.",
        "scorecard": {"overall_score": 72},
    }
    report = InsightReport(
        id=f"legacy-{version}",
        insight_run_id=run.id,
        seo_target_id=run.seo_target_id,
        attempt_id=run.attempt_id,
        report_version=version,
        report_status="complete",
        report_payload=payload,
        export_json=payload,
        export_markdown="# Existing report\n",
        created_at="2026-07-26T00:00:00+00:00",
        updated_at="2026-07-26T00:00:00+00:00",
    )
    return repository.save_report(report)


def test_assembles_ordered_reports_snapshot_and_scoped_artifacts(tmp_path: Path) -> None:
    repository, run = _repository(tmp_path)
    _legacy(repository, run, "v2")
    evidence = _evidence(repository, run)

    reports = DemandConversionReportingService(repository).assemble(evidence.id)

    report = reports["demand-conversion-v1"]
    combined = reports["v5"]
    assert report.report_payload["report_contract"] == "demand-conversion-v1"
    assert combined.report_payload["report_contract"] == "v5"
    assert combined.report_payload["source_versions"]["legacy"] == "v2"
    assert combined.report_payload["v2"]["scorecard"]["overall_score"] == 72
    assert report.report_payload["demand_groups_and_trends"]["semantics"].startswith(
        "Monthly search occasions"
    )
    assert report.report_payload["observed_vs_modeled_funnel"]["formula"][
        "version"
    ] == "demand-conversion-formula.v1"

    headings = [
        "## Executive summary",
        "## Evidence hierarchy",
        "## Demand groups and trends",
        "## Observed vs modeled funnel",
        "## Capacity and revenue ranges",
        "## Confidence and completeness",
        "## Source age",
        "## Limitations",
        "## What would change this",
        "## Service fit",
    ]
    positions = [report.export_markdown.index(heading) for heading in headings]
    assert positions == sorted(positions)
    assert report.export_markdown.index("## Executive summary") < report.export_markdown.index(
        "demand-conversion-formula.v1"
    )

    snapshot = repository.list_demand_conversion_report_snapshots(
        run_id=run.id,
        demand_conversion_evidence_id=evidence.id,
    )[0]
    assert snapshot.payload_sha256 == canonical_sha256(report.report_payload)
    assert snapshot.manifest_sha256
    assert snapshot.payload_artifact_ref == (
        f"runs/{run.id}/opportunity/{evidence.id}/reports/demand-conversion-v1.json"
    )
    persisted_payload = json.loads(
        (tmp_path / "artifacts" / snapshot.payload_artifact_ref).read_text(
            encoding="utf-8"
        )
    )
    assert canonical_sha256(persisted_payload) == snapshot.payload_sha256
    run_reports = tmp_path / "artifacts" / "runs" / run.id / "reports"
    assert (run_reports / "demand-conversion-v1.json").exists()
    assert (run_reports / "demand-conversion-v1.md").exists()
    assert (run_reports / "v5.json").exists()
    assert (run_reports / "v5.md").exists()
    scoped = tmp_path / "artifacts" / "runs" / run.id / "opportunity" / evidence.id / "reports"
    assert (scoped / "demand-conversion-v1.json").exists()
    assert (scoped / "v5.md").exists()

    # Reassembly is deterministic and cannot replace the write-once report or
    # create a second snapshot for the same evidence/mode.
    second = DemandConversionReportingService(repository).assemble(evidence.id)
    assert second["demand-conversion-v1"].to_dict() == report.to_dict()
    assert len(
        repository.list_demand_conversion_report_snapshots(
            run_id=run.id,
            demand_conversion_evidence_id=evidence.id,
        )
    ) == 1

    (scoped / "demand-conversion-v1.json").write_text(
        '{"tampered": true}', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="scoped artifacts are immutable"):
        DemandConversionReportingService(repository).assemble(evidence.id)


def test_mode_versions_share_a_run_without_overwriting_each_other(tmp_path: Path) -> None:
    repository, run = _repository(tmp_path)
    prospect = _evidence(repository, run)
    owner = replace(
        prospect,
        id="owner-version-1",
        mode="owner_verified",
        source_snapshots=[
            {
                **prospect.source_snapshots[0],
                "source_class": "owner_first_party",
                "hierarchy_level": 1,
                "provenance_label": "observed",
            },
            *prospect.source_snapshots[1:],
        ],
    )
    repository.save_demand_conversion_evidence(owner)
    service = DemandConversionReportingService(repository)

    prospect_report = service.assemble(prospect.id)["demand-conversion-v1"]
    owner_report = service.assemble(owner.id)["demand-conversion-v1"]

    # Canonical run readers retain the first report as an additive alias.
    assert repository.get_report(run.id, "demand-conversion-v1").id == prospect_report.id
    assert owner_report.id != prospect_report.id
    owner_scoped = (
        tmp_path
        / "artifacts"
        / "runs"
        / run.id
        / "opportunity"
        / owner.id
        / "reports"
    )
    assert (owner_scoped / "demand-conversion-v1.json").exists()
    owner_snapshot = repository.list_demand_conversion_report_snapshots(
        run_id=run.id,
        demand_conversion_evidence_id=owner.id,
    )[0]
    assert owner_snapshot.payload_artifact_ref.endswith(
        f"opportunity/{owner.id}/reports/demand-conversion-v1.json"
    )


def test_prospect_payload_has_no_owner_evidence_and_refs_are_validated(tmp_path: Path) -> None:
    repository, run = _repository(tmp_path)
    evidence = _evidence(repository, run)
    # The model blocks owner source snapshots, but legacy hand-built records
    # can still contain owner-shaped baseline metadata.  The renderer strips it.
    unsafe = replace(
        evidence,
        id="prospect-unsafe",
        observed_inputs={
            **evidence.observed_inputs,
            "funnel_baseline": {
                "sources": [{"source_class": "owner_first_party"}],
                "status": "observed",
            },
        },
    )
    repository.save_demand_conversion_evidence(unsafe)
    report = DemandConversionReportingService(repository).assemble(unsafe.id)[
        "demand-conversion-v1"
    ]
    serialized = json.dumps(report.report_payload, sort_keys=True)
    assert "owner_first_party" not in serialized
    assert report.report_payload["evidence"]["observed_inputs"]["funnel_baseline"][
        "status"
    ] == "unknown"

    invalid = replace(
        evidence,
        id="prospect-invalid-ref",
        evidence_refs=[
            {
                "kind": "demand_evidence_set",
                "id": "missing-demand",
                "source_sha256": "a" * 64,
            }
        ],
    )
    repository.save_demand_conversion_evidence(invalid)
    with pytest.raises(ValueError, match="referenced demand evidence"):
        DemandConversionReportingService(repository).assemble(invalid.id)


def test_owner_export_requires_approved_evidence(tmp_path: Path) -> None:
    repository, run = _repository(tmp_path)
    _evidence(repository, run)
    owner = repository.save_owned_measurement_snapshot(
        OwnedMeasurementSnapshot(
            id="owner-1",
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            source="crm_csv",
            period_start="2026-04-01",
            period_end="2026-06-30",
            source_sha256="c" * 64,
            context={"market": "Tacoma, WA"},
            metrics={
                "signups_or_leads": 20,
                "attended_or_appointments": 10,
                "new_customers": 5,
            },
            artifact_ref="owned_measurements/owner-1.json",
        )
    )
    owner_draft = DemandConversionService(repository).build(
        insight_run_id=run.id,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        mode="owner_verified",
        demand=repository.get_demand_evidence_set("demand-1"),
        economics=repository.get_business_economics_profile("economics-1"),
        owner_snapshots=[owner],
        assumptions=_assumptions(include_rates=True),
    )
    service = DemandConversionReportingService(repository)
    with pytest.raises(ValueError, match="approved immutable evidence"):
        service.assemble(owner_draft.id, for_export=True)

    approved = DemandConversionService(repository).approve(owner_draft.id, operator="operator")
    exported = service.assemble(approved.id, for_export=True)
    assert exported["demand-conversion-v1"].report_payload["mode"] == "owner_verified"
    assert exported["demand-conversion-v1"].report_payload["validation"]["privacy"] == (
        "owner_aggregate"
    )
