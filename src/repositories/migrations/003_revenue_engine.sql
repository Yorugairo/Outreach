CREATE TABLE IF NOT EXISTS vertical_packs (
    pack_id TEXT PRIMARY KEY,
    vertical_id TEXT NOT NULL,
    version TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prospects (
    id TEXT PRIMARY KEY,
    vertical_id TEXT NOT NULL,
    vertical_pack_version TEXT NOT NULL,
    normalized_domain TEXT NOT NULL,
    qualification_status TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prospects_vertical_status
    ON prospects(vertical_id, qualification_status, updated_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_prospects_domain_vertical
    ON prospects(vertical_id, normalized_domain);

CREATE TABLE IF NOT EXISTS outreach_packages (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    prospect_id TEXT NOT NULL,
    report_version TEXT NOT NULL,
    package_version INTEGER NOT NULL,
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    UNIQUE(insight_run_id, prospect_id, report_version, package_version)
);

CREATE INDEX IF NOT EXISTS idx_outreach_packages_prospect_state
    ON outreach_packages(prospect_id, state, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_outreach_packages_run_version
    ON outreach_packages(insight_run_id, report_version, package_version);

CREATE TABLE IF NOT EXISTS outreach_activation_events (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    outreach_package_id TEXT NOT NULL,
    package_version INTEGER NOT NULL,
    stage TEXT NOT NULL,
    vertical_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_activation_events_run_occurred
    ON outreach_activation_events(insight_run_id, occurred_at, id);
CREATE INDEX IF NOT EXISTS idx_activation_events_package_occurred
    ON outreach_activation_events(outreach_package_id, occurred_at, id);
CREATE INDEX IF NOT EXISTS idx_activation_events_vertical_stage
    ON outreach_activation_events(vertical_id, stage, occurred_at);
