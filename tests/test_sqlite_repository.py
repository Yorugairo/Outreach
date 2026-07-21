from __future__ import annotations

import sqlite3
from pathlib import Path

from src.orchestrator import InsightRunOrchestrator
from src.repositories.sqlite_repository import SQLiteInsightRepository


def test_sqlite_repository_persists_pipeline_and_artifacts_across_reopen(tmp_path: Path):
    database_path = tmp_path / "seo-insights.db"
    artifact_root = tmp_path / "artifacts"
    repo = SQLiteInsightRepository(database_path, artifact_root=artifact_root)
    orch = InsightRunOrchestrator(repo, artifact_root=artifact_root)

    run = orch.start("example.com", mode="quick", max_pages=1)
    first_validation = orch.validate(run.id)
    repo.close()

    reopened = SQLiteInsightRepository(database_path, artifact_root=artifact_root)
    reopened_orch = InsightRunOrchestrator(reopened, artifact_root=artifact_root)
    persisted = reopened.get_run(run.id)
    report = reopened.get_report(run.id, "v1")

    assert persisted is not None
    assert persisted.status == "completed"
    assert report is not None
    assert reopened_orch.validate(run.id)["valid"] is True
    assert first_validation["valid"] is True
    assert len(reopened.list_stage_events(run.id)) >= 12
    assert (artifact_root / "runs" / run.id / "run.json").exists()
    assert (artifact_root / "runs" / run.id / "reports" / "v1.json").exists()

    health = reopened.health()
    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        assert {
            "schema_migrations",
            "seo_targets",
            "insight_runs",
            "run_stage_events",
            "discovered_assets",
            "page_records",
            "insight_reports",
        }.issubset(tables)
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal_mode.lower() == "wal"
    assert health["foreign_keys"] is True
    assert health["journal_mode"] == "wal"
    assert health["status"] == "ok"

    reopened.close()
