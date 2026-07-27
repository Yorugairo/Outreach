from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from src.models import (
    ConversionEventMap,
    DemandConversionReportSnapshot,
    DemandTrendSnapshot,
    canonical_sha256,
)
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.demand_conversion_service import DemandConversionService
from tests.test_demand_conversion_model import _assumptions, _demand, _economics


SHA = "c" * 64


def _repositories(tmp_path: Path):
    return [
        FileBackedInsightRepository(tmp_path / "files"),
        SQLiteInsightRepository(
            tmp_path / "seo-insights.db",
            artifact_root=tmp_path / "artifacts",
        ),
    ]


def _trend() -> DemandTrendSnapshot:
    return DemandTrendSnapshot(
        id="trend-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        market="Tacoma, WA",
        source="google_trends_csv",
        period_start="2025-07-01",
        period_end="2026-06-30",
        source_sha256=SHA,
        terms=[
            {
                "keyword": "bjj tacoma",
                "intent_family": "primary",
                "provenance_label": "observed",
                "metrics": {"relative_interest": 70},
            }
        ],
        artifact_ref="demand-trends/trend-1.csv",
    )


def _event_map() -> ConversionEventMap:
    return ConversionEventMap(
        id="event-map-1",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        mappings={
            "visit": ["sessions"],
            "lead": ["start_signup"],
            "customer": ["new_members"],
        },
        source_snapshot_ids=["ga4-1", "crm-1"],
    )


def test_p11_records_persist_filter_and_remain_immutable(tmp_path: Path) -> None:
    for repository in _repositories(tmp_path):
        trend = repository.save_demand_trend_snapshot(_trend())
        event_map = repository.save_conversion_event_map(_event_map())
        evidence = DemandConversionService(repository).build(
            insight_run_id="run-1",
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            market="Tacoma, WA",
            demand=_demand(),
            economics=_economics(),
            assumptions=_assumptions(include_rates=True),
            trend_snapshots=[],
        )
        payload_hash = canonical_sha256(evidence.to_dict())
        report = repository.save_demand_conversion_report_snapshot(
            DemandConversionReportSnapshot(
                id="report-1",
                demand_conversion_evidence_id=evidence.id,
                run_id=evidence.insight_run_id,
                mode=evidence.mode,
                payload_sha256=payload_hash,
                payload_artifact_ref=(
                    f"runs/{evidence.insight_run_id}/reports/"
                    "demand-conversion-v1.json"
                ),
                source_hashes={"evidence": payload_hash},
                completeness_percent=evidence.completeness_percent,
                status=evidence.status,
            )
        )

        assert repository.get_demand_trend_snapshot(trend.id).id == trend.id
        assert repository.list_demand_trend_snapshots(
            prospect_id="prospect-1",
            market="Tacoma, WA",
        )[0].id == trend.id
        assert repository.get_conversion_event_map(event_map.id).id == event_map.id
        assert repository.list_conversion_event_maps(
            vertical_id="national_bjj_registry"
        )[0].id == event_map.id
        assert repository.get_demand_conversion_evidence(evidence.id).id == evidence.id
        assert repository.list_demand_conversion_evidence(
            insight_run_id="run-1",
            mode="prospect",
        )[0].id == evidence.id
        assert (
            repository.get_demand_conversion_report_snapshot(report.id).id
            == report.id
        )
        assert repository.list_demand_conversion_report_snapshots(
            run_id="run-1"
        )[0].id == report.id

        with pytest.raises(ValueError, match="immutable"):
            repository.save_demand_trend_snapshot(
                replace(trend, market="Seattle, WA")
            )
        with pytest.raises(ValueError, match="immutable"):
            repository.save_demand_conversion_evidence(
                replace(evidence, warnings=["changed"])
            )
