---
id: P8-BJJ-COMPETITIVE-OPPORTUNITY-ENGINE
title: BJJ Competitive Opportunity Engine
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

# BJJ Competitive Opportunity Engine

## Summary
Add a versioned Tacoma BJJ keyword set and a separately scored market-evidence workflow: 12-keyword organic/Maps pilot, operator-approved competitors, bounded competitor crawl/authority/screenshots, deterministic gaps, optional 50-keyword deepening, and combined v3 report/outreach evidence.

## Intent And Acceptance
Nova Ryu can retain the URL-first core run while resolving `national_bjj_registry.tacoma.v1`. Market evidence remains immutable, attributable, cost-bounded, and separate from SEO/AI arithmetic. Operators approve factual-risk keywords, one-to-three competitors, deepening, and outreach export.

## Scope
Contracts, file/SQLite persistence, additive migration, keyword CSV intake, DataForSEO volume/organic/Maps evidence, lifecycle, competitor selection/crawl/authority, Playwright screenshots, gap analysis, market-v1/v3 reports, API/dashboard/outreach, seed data, and tests.

## Not Building
Autonomous outreach, competitor health scores, generative causal claims, content publishing, ranking guarantees, backlink acquisition, or trades rollout.

## Human Gates
The user approved implementation and the bounded paid workflows. Pilot, competitor authority, and deep-run actions remain explicit in-product gates. Deployment/browser installation and external account changes remain outside implementation.

## Mandatory Reads
P7, product/architecture contracts, repository Protocol and implementations, DataForSEO/search services, reporting/outreach, API/dashboard, screenshot runtime constraints, and focused tests.

## Execution Path
Freeze and persist contracts; implement keyword intake/selection; implement market provider evidence and lifecycle; add competitor enrichment/screenshots/gaps; surface v3/API/dashboard/outreach; validate fixtures and regressions.

## Patterns To Mirror
Run anchoring, immutable JSON payloads, additive migrations, explicit unknown semantics, safe HTTP, raw provider artifacts, evidence refs, human approval, and legacy compatibility.

## Task Slices

### T1: Contracts, persistence, and Tacoma seed
- Status: completed
- Owner: parent
- Depends on: none
- Write set: models, repository Protocol/implementations/migration, keyword service/seed, contract tests
- Acceptance: immutable keyword and market records persist in file/SQLite stores; 50-row seed validates and selects a deterministic 12-term pilot
- Validate: `python -m pytest tests/test_keyword_sets.py tests/test_market_repository.py -q`
- Evidence: `7 passed in 0.63s`; models, file/SQLite repositories, migration `004_market_evidence.sql`, bundled 50-row seed, factual-risk flags, and deterministic category replacement are persisted in the working tree.

### T2: Market provider evidence and lifecycle
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: DataForSEO client, market service, provider/lifecycle tests
- Acceptance: Tacoma-bound volume, organic, Maps, candidates, budgets, costs, partial failures, approval, and deepening are deterministic
- Validate: `python -m pytest tests/test_market_evidence.py tests/test_dataforseo_search.py -q`
- Evidence: `16 passed in 0.52s`; one-call 50-keyword metrics, organic/Maps collectors, 25-call pilot preflight under the 26-call cap, exact 40-call fully-approved deepening, cost accounting, evidence limits, candidate merging, and approval provenance are covered.

### T3: Competitor crawl, authority, screenshots, and gaps
- Status: completed
- Owner: parent
- Depends on: T2
- Write set: competitor/screenshot/gap services, runtime dependency, security/evidence tests
- Acceptance: up to three approved competitors produce ten-page safe evidence, authority, six screenshots maximum, and supported gap classifications without scores
- Validate: `python -m pytest tests/test_competitor_evidence.py tests/test_market_security.py -q`
- Evidence: `4 passed in 0.26s`; bounded ten-page host-scoped crawl, provider-specific authority, Playwright capture contract/health, private-network rejection, six-image ceiling, comparative evidence, gap classes, and non-scoring semantics are implemented.

### T4: Reports, API, dashboard, and outreach
- Status: completed
- Owner: parent
- Depends on: T3
- Write set: reporting, API/dashboard, outreach, integration tests
- Acceptance: market-v1/v3 artifacts and complete operator workflow render; approved evidence briefs revalidate references and cold-email copy stays restrained
- Validate: `python -m pytest tests/test_market_api.py tests/test_dashboard_ui.py tests/test_revenue_services.py -q`
- Evidence: market-run-scoped immutable `market-v1`/`v3` artifacts, canonical report readers, keyword/market APIs, secondary dashboard controls, v3 package snapshots, PNG hash checks, and score-free email openings are covered by the focused market/API/dashboard/revenue tests.

### T5: Pilot and full verification
- Status: completed
- Owner: parent
- Depends on: T4
- Write set: generated artifacts and plan evidence only
- Acceptance: fixture workflow passes, full regression suite passes, PRP/tooling/artifact contracts validate; paid Nova execution occurs only within explicit runtime gates
- Validate: `python -m pytest -q`
- Evidence: `191 passed in 40.53s`; PRP validation PASS; tooling doctor `ok: true`, SigMap coverage 100%/grade A; local SQLite health OK with five additive migrations; Playwright/Chromium health OK; `national_bjj_registry.tacoma.v1` persisted and approved with 34 directly supported terms, 16 factual-risk terms still excluded pending operator review, and a deterministic 12-term pilot.

## Verification
Focused contracts, provider budgets, security, screenshot failure semantics, API/rendered workflow, full pytest, PRP validation, tooling doctor, diff review, and artifact inspection.

## Evidence And Handoff
Implementation is complete in the working tree. No paid market calls, competitor
crawls, or outreach exports were executed against Nova during implementation.
The approved Nova-bound template now auto-resolves for future URL runs; the
pilot, competitor authority, deepening, and export actions remain explicit
operator gates.
