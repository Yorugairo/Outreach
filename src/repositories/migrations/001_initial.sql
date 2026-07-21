CREATE TABLE IF NOT EXISTS seo_targets (
    id TEXT PRIMARY KEY,
    normalized_domain TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS insight_runs (
    id TEXT PRIMARY KEY,
    seo_target_id TEXT NOT NULL,
    requested_domain TEXT NOT NULL,
    status TEXT NOT NULL,
    current_stage TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (seo_target_id) REFERENCES seo_targets(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_insight_runs_domain_updated
    ON insight_runs(requested_domain, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_insight_runs_status_updated
    ON insight_runs(status, updated_at DESC);

CREATE TABLE IF NOT EXISTS run_stage_events (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    stage_name TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (insight_run_id) REFERENCES insight_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_stage_events_run_created
    ON run_stage_events(insight_run_id, created_at, id);
CREATE INDEX IF NOT EXISTS idx_stage_events_run_stage
    ON run_stage_events(insight_run_id, stage_name, status);

CREATE TABLE IF NOT EXISTS discovered_assets (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    url TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (insight_run_id) REFERENCES insight_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_assets_run_type
    ON discovered_assets(insight_run_id, asset_type);

CREATE TABLE IF NOT EXISTS page_records (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    url TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (insight_run_id) REFERENCES insight_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_pages_run_url
    ON page_records(insight_run_id, url);

CREATE TABLE IF NOT EXISTS insight_reports (
    id TEXT PRIMARY KEY,
    insight_run_id TEXT NOT NULL,
    report_version TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (insight_run_id) REFERENCES insight_runs(id) ON DELETE CASCADE,
    UNIQUE (insight_run_id, report_version)
);

CREATE INDEX IF NOT EXISTS idx_reports_run_version
    ON insight_reports(insight_run_id, report_version);
