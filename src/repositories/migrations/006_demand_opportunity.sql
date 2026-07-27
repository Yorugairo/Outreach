-- Immutable demand, economics, opportunity, and aggregate calibration records.
-- These tables intentionally have no backfill or foreign-key dependency on
-- legacy records; payload JSON remains the forward-compatible source.
CREATE TABLE IF NOT EXISTS demand_evidence_sets (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    keyword_set_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    state TEXT NOT NULL,
    version INTEGER NOT NULL,
    predecessor_id TEXT,
    superseded_by_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_demand_evidence_scope
    ON demand_evidence_sets(prospect_id, keyword_set_id, state, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_demand_evidence_predecessor
    ON demand_evidence_sets(predecessor_id);
CREATE INDEX IF NOT EXISTS idx_demand_evidence_successor
    ON demand_evidence_sets(superseded_by_id);

CREATE TABLE IF NOT EXISTS business_economics_profiles (
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
CREATE INDEX IF NOT EXISTS idx_economics_profiles_scope
    ON business_economics_profiles(prospect_id, vertical_id, state, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_economics_profiles_predecessor
    ON business_economics_profiles(predecessor_id);
CREATE INDEX IF NOT EXISTS idx_economics_profiles_successor
    ON business_economics_profiles(superseded_by_id);

CREATE TABLE IF NOT EXISTS opportunity_scenarios (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    prospect_id TEXT NOT NULL,
    state TEXT NOT NULL,
    status TEXT NOT NULL,
    predecessor_id TEXT,
    calibrated_from_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_opportunity_scenarios_run
    ON opportunity_scenarios(insight_run_id, state, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_opportunity_scenarios_prospect
    ON opportunity_scenarios(prospect_id, state, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_opportunity_scenarios_predecessor
    ON opportunity_scenarios(predecessor_id);
CREATE INDEX IF NOT EXISTS idx_opportunity_scenarios_calibrated_from
    ON opportunity_scenarios(calibrated_from_id);

CREATE TABLE IF NOT EXISTS acquisition_calibration_records (
    id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    market TEXT NOT NULL,
    version INTEGER NOT NULL,
    period_end TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_calibration_scope
    ON acquisition_calibration_records(prospect_id, vertical_id, market, period_end DESC);
