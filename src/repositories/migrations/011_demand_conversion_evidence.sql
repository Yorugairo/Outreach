-- Additive P11 evidence storage. JSON payloads remain the forward-compatible
-- source of truth; indexed columns enforce scoped operational queries.

CREATE TABLE IF NOT EXISTS demand_trend_snapshots (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    market TEXT NOT NULL,
    source TEXT NOT NULL,
    state TEXT NOT NULL,
    version INTEGER NOT NULL,
    predecessor_id TEXT,
    superseded_by_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_demand_trends_scope
    ON demand_trend_snapshots(
        prospect_id,
        vertical_id,
        market,
        source,
        state,
        created_at DESC
    );

CREATE TABLE IF NOT EXISTS conversion_event_maps (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    state TEXT NOT NULL,
    version INTEGER NOT NULL,
    predecessor_id TEXT,
    superseded_by_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conversion_event_maps_scope
    ON conversion_event_maps(
        prospect_id,
        vertical_id,
        state,
        created_at DESC
    );

CREATE TABLE IF NOT EXISTS demand_conversion_evidence (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    prospect_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    market TEXT NOT NULL,
    status TEXT NOT NULL,
    state TEXT NOT NULL,
    predecessor_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_demand_conversion_run_mode
    ON demand_conversion_evidence(
        insight_run_id,
        mode,
        state,
        created_at DESC
    );
CREATE INDEX IF NOT EXISTS idx_demand_conversion_prospect
    ON demand_conversion_evidence(
        prospect_id,
        vertical_id,
        market,
        created_at DESC
    );

CREATE TABLE IF NOT EXISTS demand_conversion_report_snapshots (
    id TEXT PRIMARY KEY,
    demand_conversion_evidence_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_demand_conversion_reports_run
    ON demand_conversion_report_snapshots(
        run_id,
        mode,
        created_at DESC
    );
CREATE INDEX IF NOT EXISTS idx_demand_conversion_reports_evidence
    ON demand_conversion_report_snapshots(
        demand_conversion_evidence_id,
        created_at DESC
    );
