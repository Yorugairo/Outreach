-- Additive P12 durable agentic work queue and evidence snapshots. Domain
-- payloads remain JSON source-of-truth; indexed columns support leases and
-- bounded operator queries. Snapshot tables are immutable at repository level.

CREATE TABLE IF NOT EXISTS vertical_agentic_packs (
    id TEXT PRIMARY KEY,
    vertical_id TEXT NOT NULL,
    version TEXT NOT NULL,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_vertical_agentic_pack_identity
    ON vertical_agentic_packs(vertical_id, version);
CREATE INDEX IF NOT EXISTS idx_vertical_agentic_pack_state
    ON vertical_agentic_packs(state, created_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS agentic_work_items (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    attempt_id TEXT NOT NULL,
    evidence_pack_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    work_kind TEXT NOT NULL,
    mode TEXT NOT NULL,
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agentic_work_queue
    ON agentic_work_items(state, updated_at, id);
CREATE INDEX IF NOT EXISTS idx_agentic_work_run
    ON agentic_work_items(run_id, state, updated_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_agentic_work_kind
    ON agentic_work_items(work_kind, mode, state, updated_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS agentic_tool_steps (
    id TEXT PRIMARY KEY,
    work_item_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    action_kind TEXT NOT NULL,
    policy_decision TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_agentic_tool_step_sequence
    ON agentic_tool_steps(work_item_id, sequence);
CREATE INDEX IF NOT EXISTS idx_agentic_tool_steps_work
    ON agentic_tool_steps(work_item_id, sequence, created_at, id);

CREATE TABLE IF NOT EXISTS vertical_agentic_snapshots (
    id TEXT PRIMARY KEY,
    snapshot_type TEXT NOT NULL,
    run_id TEXT,
    work_item_id TEXT,
    mode TEXT,
    prospect_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vertical_agentic_snapshots_run
    ON vertical_agentic_snapshots(snapshot_type, run_id, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_vertical_agentic_snapshots_work
    ON vertical_agentic_snapshots(snapshot_type, work_item_id, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_vertical_agentic_snapshots_prospect
    ON vertical_agentic_snapshots(snapshot_type, prospect_id, created_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS agentic_evidence_review_events (
    id TEXT PRIMARY KEY,
    snapshot_id TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,
    event_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agentic_evidence_review_snapshot
    ON agentic_evidence_review_events(snapshot_id, created_at, id);

CREATE TABLE IF NOT EXISTS recommendation_outcome_links (
    id TEXT PRIMARY KEY,
    recommendation_id TEXT NOT NULL,
    source_snapshot_id TEXT NOT NULL,
    outreach_package_id TEXT NOT NULL,
    prospect_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_recommendation_outcome_links_scope
    ON recommendation_outcome_links(prospect_id, vertical_id, recommendation_id, created_at DESC, id DESC);

