-- Immutable owner-authorized aggregate measurement snapshots.  The payload is
-- the forward-compatible source of truth; indexed columns support scope and
-- temporal queries without exposing raw connector credentials or row-level PII.
CREATE TABLE IF NOT EXISTS owned_measurement_snapshots (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    source TEXT NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    predecessor_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_owned_measurements_scope
    ON owned_measurement_snapshots(prospect_id, vertical_id, source, period_end DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_owned_measurements_predecessor
    ON owned_measurement_snapshots(predecessor_id);
