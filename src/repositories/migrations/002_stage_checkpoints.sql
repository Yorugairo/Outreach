CREATE TABLE IF NOT EXISTS stage_checkpoints (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    attempt_id TEXT NOT NULL,
    stage_name TEXT NOT NULL,
    payload_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    content_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    UNIQUE(insight_run_id, attempt_id, stage_name)
);

CREATE INDEX IF NOT EXISTS idx_stage_checkpoints_lookup
    ON stage_checkpoints(insight_run_id, attempt_id, stage_name);
