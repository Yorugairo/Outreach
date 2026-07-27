CREATE TABLE IF NOT EXISTS keyword_sets (
    id TEXT PRIMARY KEY,
    keyword_set_key TEXT NOT NULL UNIQUE,
    vertical_id TEXT NOT NULL,
    normalized_domain TEXT,
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_keyword_sets_scope_state
    ON keyword_sets(vertical_id, normalized_domain, state, updated_at DESC);

CREATE TABLE IF NOT EXISTS market_evidence_runs (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    keyword_set_id TEXT NOT NULL,
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (insight_run_id) REFERENCES insight_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_set_id) REFERENCES keyword_sets(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_market_evidence_run_state
    ON market_evidence_runs(insight_run_id, state, updated_at DESC);
