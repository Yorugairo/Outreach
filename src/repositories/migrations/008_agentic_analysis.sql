-- Additive agentic analysis lifecycle. Payload JSON remains the forward-
-- compatible source; indexed columns support idempotency and queue queries.
CREATE TABLE IF NOT EXISTS site_evidence_packs (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    attempt_id TEXT NOT NULL,
    content_sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_site_evidence_packs_run
    ON site_evidence_packs(run_id, created_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS agentic_analysis_jobs (
    id TEXT PRIMARY KEY,
    evidence_pack_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agentic_jobs_queue
    ON agentic_analysis_jobs(state, updated_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_agentic_jobs_evidence
    ON agentic_analysis_jobs(evidence_pack_id, updated_at DESC, id DESC);

CREATE TABLE IF NOT EXISTS agent_call_records (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agent_calls_job
    ON agent_call_records(job_id, started_at, id);

CREATE TABLE IF NOT EXISTS agentic_assessment_snapshots (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    evidence_pack_id TEXT NOT NULL,
    predecessor_id TEXT,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agentic_assessments_job
    ON agentic_assessment_snapshots(job_id, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_agentic_assessments_evidence
    ON agentic_assessment_snapshots(evidence_pack_id, created_at DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_agentic_assessments_predecessor
    ON agentic_assessment_snapshots(predecessor_id);

CREATE TABLE IF NOT EXISTS agentic_assessment_review_events (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agentic_review_events_assessment
    ON agentic_assessment_review_events(assessment_id, created_at, id);
