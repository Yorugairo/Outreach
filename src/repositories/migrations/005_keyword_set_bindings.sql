CREATE TABLE IF NOT EXISTS keyword_set_bindings (
    id TEXT PRIMARY KEY,
    keyword_set_id TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    normalized_domain TEXT NOT NULL,
    prospect_id TEXT,
    state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (keyword_set_id) REFERENCES keyword_sets(id) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_keyword_set_bindings_active_domain
    ON keyword_set_bindings(vertical_id, normalized_domain)
    WHERE state = 'active';

CREATE INDEX IF NOT EXISTS idx_keyword_set_bindings_keyword_prospect
    ON keyword_set_bindings(keyword_set_id, prospect_id, state);
