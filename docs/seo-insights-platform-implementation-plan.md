# SEO Insights Platform Implementation Plan

Prepared: 2026-07-07
Workspace: `C:\Users\Snipe\Downloads\Outreach Program`

## Goal
Reshape the current SEO ingestion work into a product/platform whose core workflow is:

**URL/domain in -> persisted SEO insight run out**

with stable DB objects, run-state tracking, search-intelligence enrichment, sitemap analysis, and operator-facing exports.

## Guiding decisions
1. competitor research is not a blocking v1 module
2. DataForSEO remains the search-intelligence backbone
3. the UI/API should talk to `InsightRun` objects, not scripts
4. scripts may still exist temporarily, but only as worker entrypoints around reusable services
5. every stage must persist state and artifacts

---

## Phase 1 — Data model hardening
Convert schema from generic ingestion support to explicit platform objects.

### Add / rename conceptual anchors
Treat these as core app concepts whether or not table names stay the same:
- `targets`
- `insight_runs`
- `run_stage_events`
- `page_records`
- `page_evidence`
- `keyword_clusters`
- `serp_snapshots`
- `coverage_scorecards`
- `sitemap_recommendations`
- `insight_reports`

### Immediate schema additions
Add tables or equivalents for:
- run status history / events
- artifact references (raw JSON, exports, screenshots, sitemap XML)
- report snapshots
- per-run summary scorecards

### Deliverable
A run-centric schema where every output ties back to a specific insight run.

---

## Phase 2 — Service layer extraction
Make reusable modules the source of truth.

### Core services
- `target_intake_service`
- `sitemap_discovery_service`
- `page_fetch_service`
- `page_analysis_service`
- `search_intelligence_service`
- `scorecard_service`
- `report_assembly_service`

### Rule
No important business logic should live only inside CLI scripts.

### Deliverable
`src/` contains reusable services; scripts become thin wrappers.

---

## Phase 3 — Run orchestration
Build a run coordinator.

### Coordinator responsibilities
- create `insight_run`
- advance run states
- invoke each stage in order
- capture failures/retries
- persist stage timings and summaries

### Minimum states
- queued
- discovering_sitemaps
- fetching_pages
- extracting_page_evidence
- classifying_pages
- pulling_search_intelligence
- scoring
- assembling_report
- completed
- failed

### Deliverable
A single orchestration path that can be triggered from API or CLI.

---

## Phase 4 — Product API
Add product-facing endpoints.

### Minimum endpoints
- create run
- get run status
- get pages
- get sitemap summary
- get keyword summary
- get report/export

### Deliverable
A stable API contract for the operator app.

---

## Phase 5 — Operator UI
Build minimal UI surfaces.

### Minimum screens
1. run launcher
2. run detail page
3. page inventory/evidence table
4. sitemap workbench
5. summary scorecard/export panel

### Deliverable
An operator can launch and inspect a run without touching CLI.

---

## Phase 6 — Deferred enrichments
Only after the core loop works:
- competitor research overlays
- LLM narration layers
- content-generation workflows
- outbound/commercial packaging

---

## What to change in the current implementation approach

### Keep
- normalized evidence mindset
- DataForSEO client
- sitemap/page fetch primitives
- scoring logic emphasis

### Change
- stop treating `scripts/*.py` as the product boundary
- introduce run-centric DB/state design
- introduce report objects
- design UI/API surfaces now, even if thin initially
- make exports first-class outputs of the run

---

## Immediate next engineering tasks
1. revise schema around `insight_runs` and `run_stage_events`
2. add repository/storage layer for runs and pages
3. wrap existing fetchers/client in service modules
4. build one `run_insight_pipeline.py` orchestrator that persists run states
5. emit one report JSON per completed run
6. define API payload contracts before more worker code is added

---

## Recommended v1 success definition
The platform is successful when you can:
- paste a URL into a launcher
- wait for a background run to complete
- open a run detail page
- inspect discovered sitemaps/pages/metadata/keyword evidence
- see a reliable sitemap + SEO scorecard
- export a machine-readable report

That is the product. Competitor analysis can sit on top of it later.
