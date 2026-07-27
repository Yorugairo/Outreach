-- Immutable client-report graph records. Legacy insight_reports remain separate
-- so existing readers continue to observe the historical contract unchanged.
CREATE TABLE IF NOT EXISTS report_snapshots (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    attempt_id TEXT NOT NULL,
    report_contract TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    payload_sha256 TEXT NOT NULL,
    manifest_sha256 TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_report_snapshots_scope
    ON report_snapshots(run_id, report_contract, created_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS report_aliases (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    report_contract TEXT NOT NULL,
    alias TEXT NOT NULL,
    snapshot_id TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    UNIQUE (run_id, report_contract, alias)
);
CREATE INDEX IF NOT EXISTS idx_report_aliases_scope
    ON report_aliases(run_id, report_contract, updated_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_report_aliases_snapshot
    ON report_aliases(snapshot_id);

CREATE TABLE IF NOT EXISTS client_report_bundles (
    id TEXT PRIMARY KEY,
    report_snapshot_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_client_report_bundles_run
    ON client_report_bundles(run_id, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_client_report_bundles_snapshot
    ON client_report_bundles(report_snapshot_id, created_at DESC, id DESC);
