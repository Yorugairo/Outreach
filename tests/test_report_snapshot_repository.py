from __future__ import annotations

from pathlib import Path

import pytest

from src.models import ClientReportBundle, ReportAlias, ReportSnapshot
from src.repositories.file_repository import FileBackedInsightRepository
from src.repositories.sqlite_repository import SQLiteInsightRepository


SHA_A = "a" * 64
SHA_B = "b" * 64


def _repositories(tmp_path: Path):
    return [
        FileBackedInsightRepository(tmp_path / "files"),
        SQLiteInsightRepository(tmp_path / "seo-insights.db", tmp_path / "artifacts"),
    ]


def _snapshot(snapshot_id: str, created_at: str) -> ReportSnapshot:
    return ReportSnapshot(
        id=snapshot_id,
        run_id="run-1",
        attempt_id=snapshot_id,
        report_contract="operator-v5",
        schema_version=1,
        source_snapshot_ids={"seo": snapshot_id},
        source_hashes={"seo": SHA_A},
        renderer_version="operator-renderer.v1",
        payload_sha256=SHA_B,
        payload_artifact_ref=f"snapshots/{snapshot_id}.json",
        created_at=created_at,
        completeness_percent=100,
        status="complete",
    )


def _bundle(snapshot_id: str, bundle_id: str) -> ClientReportBundle:
    return ClientReportBundle(
        id=bundle_id,
        report_snapshot_id=snapshot_id,
        run_id="run-1",
        manifest_sha256=SHA_A,
        manifest_artifact_ref=f"bundles/{bundle_id}/manifest.json",
        files=[{"path": "report.html", "sha256": SHA_B}],
    )


def test_snapshots_and_bundles_are_write_once_aliases_move(tmp_path: Path) -> None:
    for repository in _repositories(tmp_path):
        first = repository.save_report_snapshot(_snapshot("snapshot-1", "2026-07-25T10:00:00+00:00"))
        second = repository.save_report_snapshot(_snapshot("snapshot-2", "2026-07-26T10:00:00+00:00"))
        assert repository.save_report_snapshot(first).id == first.id

        with pytest.raises(ValueError, match="immutable"):
            repository.save_report_snapshot(
                ReportSnapshot(**{**first.to_dict(), "payload_sha256": SHA_A})
            )

        alias = ReportAlias(
            run_id="run-1", report_contract="operator-v5", alias="latest", snapshot_id=first.id
        )
        repository.save_report_alias(alias)
        assert repository.get_latest_report_snapshot("run-1", "operator-v5").id == first.id

        moved = ReportAlias(
            run_id="run-1", report_contract="operator-v5", alias="latest", snapshot_id=second.id
        )
        repository.save_report_alias(moved)
        assert repository.get_latest_report_snapshot("run-1", "operator-v5").id == second.id
        assert [item.id for item in repository.list_report_snapshot_history("run-1", "operator-v5")] == [
            second.id,
            first.id,
        ]

        bundle = repository.save_client_report_bundle(_bundle(second.id, "bundle-1"))
        assert repository.get_client_report_bundle(bundle.id).report_snapshot_id == second.id
        with pytest.raises(ValueError, match="immutable"):
            repository.save_client_report_bundle(
                ClientReportBundle(**{**bundle.to_dict(), "status": "partial"})
            )


def test_sqlite_snapshot_graph_survives_reopen(tmp_path: Path) -> None:
    database_path = tmp_path / "seo-insights.db"
    artifact_root = tmp_path / "artifacts"
    repository = SQLiteInsightRepository(database_path, artifact_root)
    snapshot = repository.save_report_snapshot(_snapshot("snapshot-1", "2026-07-26T10:00:00+00:00"))
    repository.save_report_alias(
        ReportAlias(run_id="run-1", report_contract="operator-v5", alias="latest", snapshot_id=snapshot.id)
    )
    repository.save_client_report_bundle(_bundle(snapshot.id, "bundle-1"))

    reopened = SQLiteInsightRepository(database_path, artifact_root)
    assert reopened.get_latest_report_snapshot("run-1", "operator-v5").id == snapshot.id
    assert reopened.list_client_report_bundles(run_id="run-1")[0].id == "bundle-1"
