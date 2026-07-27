from __future__ import annotations

from pathlib import Path
import pytest

from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository
from src.services.owned_measurement_service import (
    ConnectorDisabledError,
    OwnedMeasurementService,
)


CSV_GSC = """period_start,period_end,impressions,clicks,market,device
2026-06-01,2026-06-30,1000,100,Tacoma,desktop
"""
CSV_GA4 = """period_start,period_end,users,sessions,signups
2026-06-01,2026-06-30,80,100,20
"""
CSV_CRM = """period_start,period_end,leads,appointments,customers
2026-06-01,2026-06-30,20,10,5
"""


def test_csv_import_validates_context_provenance_and_is_idempotent(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = OwnedMeasurementService(repository)
    preview = service.preview_csv(
        CSV_GSC,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="gsc",
        context={"property": "sc-domain:example.test"},
    )
    assert preview.valid
    first = service.commit(preview)
    second = service.commit(preview)
    assert first[0].id == second[0].id
    assert repository.get_owned_measurement_snapshot(first[0].id).source_sha256 == preview.source_sha256
    assert repository.list_owned_measurement_snapshots(prospect_id="prospect-1")[0].artifact_ref.endswith("#row=2")


def test_pii_and_formula_inputs_are_rejected():
    service = OwnedMeasurementService()
    preview = service.preview_csv(
        "period_start,period_end,emails,clicks\n2026-06-01,2026-06-30,a@example.test,=100\n",
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="ga4_csv",
        context={"property_id": "123"},
    )
    assert not preview.valid
    assert any("PII" in issue.message for issue in preview.issues)
    assert any("formula" in issue.message for issue in preview.issues)
    with pytest.raises(ValueError, match="filesystem paths"):
        service.preview_csv(
            Path("private.csv"),
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            source="ga4_csv",
            context={"property_id": "123"},
        )


def test_cross_source_baseline_and_calibration_record(tmp_path):
    repository = FileBackedInsightRepository(tmp_path)
    service = OwnedMeasurementService(repository)
    snapshots = []
    for csv_text, source in ((CSV_GSC, "gsc_csv"), (CSV_GA4, "ga4_csv"), (CSV_CRM, "crm_csv")):
        snapshots.extend(service.import_csv(
            csv_text,
            prospect_id="prospect-1",
            vertical_id="national_bjj_registry",
            source=source,
            context={"market": "Tacoma"},
        ))
    baseline = service.derive_funnel_baseline(snapshots)
    assert baseline["metrics"] == {
        "impressions": 1000,
        "clicks": 100,
        "total_users": 80,
        "signups_or_leads": 20,
        "attended_or_appointments": 10,
        "new_customers": 5,
        "spend": None,
    }
    assert baseline["context"] == {"market": "Tacoma"}
    record = service.create_calibration_record(snapshots)
    assert record.source == "owned_measurement"
    assert record.market == "Tacoma"
    assert set(record.artifact_ref["snapshot_ids"]) == {snapshot.id for snapshot in snapshots}


def test_sqlite_repository_persists_owned_measurements(tmp_path):
    repository = SQLiteInsightRepository(tmp_path / "db.sqlite", tmp_path / "artifacts")
    service = OwnedMeasurementService(repository)
    snapshot = service.import_csv(
        CSV_GA4,
        prospect_id="prospect-1",
        vertical_id="one_trade_network",
        source="ga4",
        context={"property_id": "123"},
    )[0]
    reopened = SQLiteInsightRepository(tmp_path / "db.sqlite", tmp_path / "artifacts")
    assert reopened.get_owned_measurement_snapshot(snapshot.id).metrics["users"] == 80
    assert any(path.name == "009_owned_measurements.sql" for path in repository.MIGRATIONS_DIR.iterdir())


def test_live_connectors_are_disabled_by_default():
    service = OwnedMeasurementService()
    with pytest.raises(ConnectorDisabledError, match="disabled by default"):
        service.collect_live(
            "ga4_csv",
            prospect_id="prospect-1",
            period_start="2026-06-01",
            period_end="2026-06-30",
            context={"property_id": "123"},
        )


def test_baseline_rejects_incompatible_contexts():
    service = OwnedMeasurementService()
    first = service.import_csv(
        CSV_GSC,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="gsc_csv",
        context={"market": "Tacoma"},
    )[0]
    second = service.import_csv(
        CSV_GA4,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="ga4_csv",
        context={"market": "Seattle"},
    )[0]
    with pytest.raises(ValueError, match="context is incompatible"):
        service.derive_funnel_baseline([first, second])


def test_baseline_rejects_mixed_prospects_and_nested_sensitive_context():
    service = OwnedMeasurementService()
    first = service.import_csv(
        CSV_GSC,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="gsc_csv",
        context={"market": "Tacoma"},
    )[0]
    second = service.import_csv(
        CSV_GA4,
        prospect_id="prospect-2",
        vertical_id="national_bjj_registry",
        source="ga4_csv",
        context={"market": "Tacoma"},
    )[0]
    with pytest.raises(ValueError, match="share a prospect"):
        service.derive_funnel_baseline([first, second])

    preview = service.preview_csv(
        CSV_GSC,
        prospect_id="prospect-1",
        vertical_id="national_bjj_registry",
        source="gsc_csv",
        context={"market": "Tacoma", "connector": {"api_key": "do-not-store"}},
    )
    assert not preview.valid
    assert any("credential" in issue.message for issue in preview.issues)
