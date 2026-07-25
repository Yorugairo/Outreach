from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from src.models import DiscoveredAsset, InsightReport, InsightRun, PageRecord, RunStageEvent, SEOTarget, StageCheckpoint
from src.repositories.file_repository import FileBackedInsightRepository


class SQLiteInsightRepository:
    """SQLite source of truth with a file artifact mirror.

    SQLite runs in WAL mode with foreign keys and busy timeouts enabled on every
    connection. The JSON payload columns retain forward-compatible domain objects,
    while indexed columns support operational run queries.
    """

    MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

    def __init__(self, database_path: str | Path, artifact_root: str | Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.artifact_root = Path(artifact_root)
        self._files = FileBackedInsightRepository(self.artifact_root)
        self._migrate()

    def upsert_target(self, target: SEOTarget) -> SEOTarget:
        payload = target.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO seo_targets (id, normalized_domain, updated_at, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    normalized_domain = excluded.normalized_domain,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (target.id, target.normalized_domain, target.updated_at, self._encode(payload)),
            )
        self._files.upsert_target(target)
        return target

    def create_run(self, run: InsightRun) -> InsightRun:
        payload = run.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO insight_runs (
                    id, seo_target_id, requested_domain, status, current_stage,
                    created_at, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.id,
                    run.seo_target_id,
                    run.requested_domain,
                    run.status,
                    run.current_stage,
                    run.created_at,
                    run.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.create_run(run)
        return run

    def update_run(self, run: InsightRun) -> InsightRun:
        payload = run.to_dict()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE insight_runs
                SET status = ?, current_stage = ?, updated_at = ?, payload_json = ?
                WHERE id = ?
                """,
                (run.status, run.current_stage, run.updated_at, self._encode(payload), run.id),
            )
            if cursor.rowcount != 1:
                raise ValueError(f"run {run.id} not found")
        self._files.update_run(run)
        return run

    def append_stage_event(self, event: RunStageEvent) -> RunStageEvent:
        payload = event.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO run_stage_events (
                    id, insight_run_id, stage_name, status, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.insight_run_id,
                    event.stage_name,
                    event.status,
                    event.created_at,
                    self._encode(payload),
                ),
            )
        self._files.append_stage_event(event)
        return event

    def save_discovered_asset(self, asset: DiscoveredAsset) -> DiscoveredAsset:
        payload = asset.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO discovered_assets (id, insight_run_id, asset_type, url, payload_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET payload_json = excluded.payload_json
                """,
                (asset.id, asset.insight_run_id, asset.asset_type, asset.url, self._encode(payload)),
            )
        self._files.save_discovered_asset(asset)
        return asset

    def save_page_record(self, page: PageRecord) -> PageRecord:
        payload = page.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO page_records (id, insight_run_id, url, payload_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET url = excluded.url, payload_json = excluded.payload_json
                """,
                (page.id, page.insight_run_id, page.url, self._encode(payload)),
            )
        self._files.save_page_record(page)
        return page

    def save_report(self, report: InsightReport) -> InsightReport:
        payload = report.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO insight_reports (
                    id, insight_run_id, report_version, updated_at, payload_json
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(insight_run_id, report_version) DO UPDATE SET
                    id = excluded.id,
                    updated_at = excluded.updated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    report.id,
                    report.insight_run_id,
                    report.report_version,
                    report.updated_at,
                    self._encode(payload),
                ),
            )
        self._files.save_report(report)
        return report

    def save_checkpoint(self, checkpoint: StageCheckpoint) -> StageCheckpoint:
        payload = checkpoint.to_dict()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO stage_checkpoints (
                    id, insight_run_id, attempt_id, stage_name, payload_type,
                    schema_version, content_sha256, created_at, payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(insight_run_id, attempt_id, stage_name) DO UPDATE SET
                    id = excluded.id,
                    payload_type = excluded.payload_type,
                    schema_version = excluded.schema_version,
                    content_sha256 = excluded.content_sha256,
                    created_at = excluded.created_at,
                    payload_json = excluded.payload_json
                """,
                (
                    checkpoint.id,
                    checkpoint.insight_run_id,
                    checkpoint.attempt_id,
                    checkpoint.stage_name,
                    checkpoint.payload_type,
                    checkpoint.schema_version,
                    checkpoint.content_sha256,
                    checkpoint.created_at,
                    self._encode(checkpoint.payload),
                ),
            )
        self._files.save_checkpoint(checkpoint)
        return checkpoint

    def get_run(self, run_id: str) -> InsightRun | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM insight_runs WHERE id = ?", (run_id,)
            ).fetchone()
        return InsightRun(**self._decode(row[0])) if row else None

    def list_runs(self, limit: int = 20) -> list[InsightRun]:
        safe_limit = max(1, min(int(limit), 1000))
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM insight_runs ORDER BY updated_at DESC, id DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [InsightRun(**self._decode(row[0])) for row in rows]

    def list_stage_events(self, run_id: str) -> list[RunStageEvent]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json FROM run_stage_events
                WHERE insight_run_id = ?
                ORDER BY created_at, id
                """,
                (run_id,),
            ).fetchall()
        return [RunStageEvent(**self._decode(row[0])) for row in rows]

    def get_report(self, run_id: str, report_version: str) -> InsightReport | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM insight_reports
                WHERE insight_run_id = ? AND report_version = ?
                """,
                (run_id, report_version),
            ).fetchone()
        return InsightReport(**self._decode(row[0])) if row else None

    def get_checkpoint(self, run_id: str, attempt_id: str, stage_name: str) -> StageCheckpoint | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, insight_run_id, attempt_id, stage_name, payload_type,
                       schema_version, content_sha256, created_at, payload_json
                FROM stage_checkpoints
                WHERE insight_run_id = ? AND attempt_id = ? AND stage_name = ?
                """,
                (run_id, attempt_id, stage_name),
            ).fetchone()
        if row is None:
            return None
        return StageCheckpoint(
            id=row[0],
            insight_run_id=row[1],
            attempt_id=row[2],
            stage_name=row[3],
            payload_type=row[4],
            schema_version=row[5],
            content_sha256=row[6],
            created_at=row[7],
            payload=self._decode(row[8]),
        )

    def health(self) -> dict[str, Any]:
        with self._connect() as connection:
            connection.execute("SELECT 1").fetchone()
            journal_mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0]).lower()
            foreign_keys = bool(connection.execute("PRAGMA foreign_keys").fetchone()[0])
            migration_count = int(connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0])
        return {
            "status": "ok",
            "backend": "sqlite",
            "database_path": str(self.database_path),
            "journal_mode": journal_mode,
            "foreign_keys": foreign_keys,
            "migration_count": migration_count,
        }

    def close(self) -> None:
        """Connections are short-lived per operation; retained for repository parity."""

    def _migrate(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            applied = {
                row[0]
                for row in connection.execute("SELECT version FROM schema_migrations").fetchall()
            }
            for migration_path in sorted(self.MIGRATIONS_DIR.glob("*.sql")):
                version = migration_path.stem
                if version in applied:
                    continue
                connection.executescript(migration_path.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (?)", (version,)
                )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30.0)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def _decode(payload: str) -> dict[str, Any]:
        return json.loads(payload)
