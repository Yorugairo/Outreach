---
id: P4-AI-READINESS-SCORING
title: Evidence-Backed AI Readiness, AEO, GEO, and AIO Scoring
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

# Evidence-Backed AI Readiness Scoring

## Summary
Add a separate, versioned AI Readiness score from the same bounded site crawl used by SEO analysis.

## Intent And Acceptance
One URL run collects at most 100 internal HTML pages once, preserves the SEO score, emits AEO/GEO/AIO plus core/supporting views, and never treats missing paid enrichment as zero.

## Scope
Page evidence, robots access, deterministic scoring, `ai-v1` artifacts, API/dashboard display, and outreach-brief snapshotting.

## Not Building
AI citation/rank claims, LLM judging, direct third-party crawling, autonomous outreach, or historical backfill.

## Human Gates
Paid DataForSEO calls retain the existing explicit approval gate. Deployment and external writes are excluded.

## Mandatory Reads
`docs/runbooks/PRP_EXECUTION.md`, `docs/seo-insights-platform-architecture.md`, `src/pipeline.py`, and the score-semantic tests.

## Execution Path
Freeze contracts, collect evidence, add optional mentions, score/report, expose operator surfaces, then run focused and full verification.

## Patterns To Mirror
Run-scoped checkpoints, immutable versioned reports, independently resolvable evidence, unknown-not-zero semantics, and additive JSON persistence.

## Task Slices

### T1: Contracts
- Status: completed
- Owner: parent
- Depends on: none
- Write set: models, plan, contract tests
- Acceptance: typed versioned AI output and additive page/package fields
- Validate: `python -m pytest tests/test_ai_readiness_contract.py -q`
- Evidence: versioned constants, typed output, additive page/package fields, and contract fixtures

### T2: Single-crawl evidence
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: fetchers and page/crawl services
- Acceptance: bounded deterministic collection and persisted AI evidence
- Validate: `python -m pytest tests/test_ai_page_evidence.py tests/test_single_crawl.py -q`
- Evidence: bounded parser/crawl fixtures prove normalization, host restriction, fetch-once behavior, and cap reporting

### T3: Mentions and scoring
- Status: completed
- Owner: parent
- Depends on: T2
- Write set: search client/service and AI readiness service
- Acceptance: deterministic dimensions/cohorts with unknown mention handling
- Validate: `python -m pytest tests/test_ai_readiness_contract.py tests/test_dataforseo_search.py -q`
- Evidence: six-call allocation fixtures and unknown-not-zero scoring checks

### T4: Pipeline and artifacts
- Status: completed
- Owner: parent
- Depends on: T3
- Write set: pipeline, reporting, validation
- Acceptance: `ai-v1` JSON/Markdown plus additive run summary
- Validate: `python -m pytest tests/test_orchestration.py tests/test_integrity_regressions.py -q`
- Evidence: validated run `c8ef4ce4-e5fd-4c77-9c2d-debe5b390b11` emitted seven completed stages and immutable `ai-v1` JSON/Markdown

### T5: API, UI, and outreach
- Status: completed
- Owner: parent
- Depends on: T4
- Write set: API, dashboard, outreach service
- Acceptance: operator score display and immutable brief snapshot
- Validate: `python -m pytest tests/test_api.py tests/test_dashboard_ui.py tests/test_revenue_services.py -q`
- Evidence: API/UI/outreach regression coverage plus immutable AI score snapshot validation

## Verification
Focused tests, full `pytest`, PRP validation, tooling doctor, and artifact inspection from a quick local run.

## Evidence And Handoff
Full suite: `155 passed`. PRP validation and tooling doctor pass. Artifact inspection for run `c8ef4ce4-e5fd-4c77-9c2d-debe5b390b11` found AI Readiness 81.25, 55.8% completeness, AEO 75, GEO 75, AIO 100, and zero unresolved references across 25 check-level evidence references.
