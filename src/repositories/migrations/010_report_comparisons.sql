-- Immutable temporal comparison snapshots. The JSON payload retains the full
-- compatibility contract; indexed identities support history lookups.
CREATE TABLE IF NOT EXISTS report_comparison_snapshots (
    id TEXT PRIMARY KEY,
    target_id TEXT NOT NULL,
    baseline_snapshot_id TEXT NOT NULL,
    current_snapshot_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_report_comparisons_target
    ON report_comparison_snapshots(target_id, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_report_comparisons_sources
    ON report_comparison_snapshots(
        baseline_snapshot_id,
        current_snapshot_id,
        created_at DESC
    );
