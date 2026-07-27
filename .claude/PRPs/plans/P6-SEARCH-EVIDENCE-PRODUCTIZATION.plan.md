---
id: P6-SEARCH-EVIDENCE-PRODUCTIZATION
title: Keyword and Google Ranking Evidence Productization
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

# Keyword and Google Ranking Evidence Productization

## Summary
Make the URL-first app load its approved DataForSEO runtime configuration, collect bounded paid keyword/SERP evidence by default, and present observed rankings as a first-class evidence-backed report section.

## Intent And Acceptance
Pasting a URL should run without interacting with provider controls. When the local operator policy is enabled, a run uses at most six DataForSEO calls and reports keywords, volume, observed Google position, ranking URL, market/device/date, opportunity band, SERP context, provider call count, and evidence limits. “Not observed in the sampled top 100” must never become an absolute “not ranking” claim.

## Scope
Runtime dotenv selection, request-policy precedence, deterministic search-evidence normalization, score validation, v2 JSON/Markdown reporting, API/dashboard rendering, outreach evidence brief, tests, and a paid Nova Ryu verification run.

## Not Building
Autonomous outreach, unbounded rank tracking, AI citation claims, third-party page fetching, revenue forecasts, or competitor health scoring.

## Human Gates
The user explicitly requested the app use `docs/local.env` and make the previously proposed paid-evidence improvements. Paid collection remains bounded by `DATAFORSEO_MAX_CALLS` (currently six) and applies only when the ignored local policy explicitly enables it.

## Mandatory Reads
`docs/runbooks/PRP_EXECUTION.md`, P4, P5, `src/config.py`, DataForSEO client/service, report assembly, outreach service, API/dashboard, and focused tests.

## Execution Path
First fix runtime configuration and approval precedence. Then normalize evidence and correct no-result score semantics. Finally render the view across report/API/dashboard/outreach, validate locally, and run Nova Ryu with the bounded paid budget.

## Patterns To Mirror
Immutable versioned artifacts, explicit provider approval, environment-over-dotenv precedence, observed-versus-inferred language, bounded raw artifacts, additive report fields, and evidence refs resolving to persisted checkpoints.

## Task Slices

### T1: Activate approved runtime configuration
- Status: completed
- Owner: parent
- Depends on: none
- Write set: `docs/local.env`, `src/config.py`, `src/api/app.py`, focused tests
- Acceptance: app defaults to `docs/local.env`; explicit request approval overrides the configured default; dashboard URL-first flow requires no provider interaction
- Validate: `python -m pytest tests/test_dataforseo_search.py tests/test_api.py -q`
- Evidence: runtime health reports configured/default-approved/six-call cap; request omission and explicit override tests pass

### T2: Normalize keyword and ranking evidence
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: DataForSEO/search services and focused tests
- Acceptance: keyword intent/volume, observed rank/URL, opportunity bands, top-100 non-observation, call usage, market/device/date, and SERP context are deterministic; sampled no-result queries count as observed zero visibility
- Validate: `python -m pytest tests/test_dataforseo_search.py tests/test_scorecard_semantics.py tests/test_integrity_regressions.py -q`
- Evidence: sampled non-observation fixture validates at zero visibility, preserves top-five SERP context, and labels the result without an absolute non-ranking claim

### T3: Present evidence across product surfaces
- Status: completed
- Owner: parent
- Depends on: T2
- Write set: reporting, API, dashboard, outreach brief, focused tests
- Acceptance: v2 JSON/Markdown, run API, dashboard, and evidence brief contain a dedicated search section without putting rankings in the cold-email opening
- Validate: `python -m pytest tests/test_api.py tests/test_dashboard_ui.py tests/test_revenue_services.py tests/test_integrity_regressions.py -q`
- Evidence: focused API/dashboard/report/outreach and integrity suite passes (62 tests); cold-email copy remains score/rank free

### T4: Verify and calibrate Nova Ryu
- Status: completed
- Owner: parent
- Depends on: T3
- Write set: generated artifacts and plan evidence only
- Acceptance: full suite passes and one valid Nova Ryu run contains attributable paid keyword/SERP artifacts within the six-call cap
- Validate: `python -m pytest -q`
- Evidence: valid run `4d690da7-8566-4622-a894-30864d5082cc`; final attempt `567344bd-2b4b-48a2-8678-4f7df217a88c`; 3 checked queries, 0 observed target results, 3 deduplicated topic-aligned external corroborations, and 6 provider calls in the final search attempt

## Verification
Focused contract tests, full pytest, PRP validation, tooling doctor, diff review, and a bounded paid Nova Ryu run with direct artifact inspection.

## Evidence And Handoff
The development app loads the gitignored `docs/local.env` runtime policy and reports configured/default-approved/six-call status without credential values. The dashboard retains one-field URL-first operation and renders a dedicated search table. Nova Ryu’s valid final report records SEO 26.67, AI Readiness 61.14 at 100% completeness, and search visibility 0.0 from three dated US desktop top-100 samples (`mma instructor`, `mma classes`, `houston mma classes`), all explicitly described as sampled non-observations. Three deduplicated topic-aligned external results support GEO; ambiguous gaming/forum exact-name matches are excluded. Calibration used two paid search attempts of six calls each; downstream rescoring used no paid calls. Full suite: 167 passed. PRP validation, tooling doctor, rendered dashboard inspection, artifact validation, and diff check pass.
