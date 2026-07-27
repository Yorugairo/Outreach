---
id: P5-EVIDENCE-PRODUCT-READINESS
title: AI Evidence and Product Readiness Hardening
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

# AI Evidence and Product Readiness Hardening

## Summary
Make AI Readiness evidence conservative, crawl accounting internally consistent, customer presentation confidence-aware, and report references compact enough for routine outreach review.

## Intent And Acceptance
`laceyglass.com` and `novaryu.com` produce reviewable reports without navigation/footer links masquerading as citations, generic numbers masquerading as first-party proof, duplicate redirect/canonical pages, misleading complete-looking bands on partial evidence, or repeated full-page payloads in every check reference.

## Scope
Page-region evidence parsing, applicability-aware checks, redirect/canonical identity, crawl inventory, provisional display and approval policy, compact evidence references, focused fixtures, and two real target runs.

## Not Building
LLM judges, actual AI citation tracking, third-party page scraping, autonomous outreach, PDF design, or formula-weight changes.

## Human Gates
The user explicitly authorized crawling the two primary target URLs and using repository/DB data from OTN, Insights, and the BJJ Registry. Paid provider calls remain separately gated and are not required for acceptance.

## Mandatory Reads
`docs/runbooks/PRP_EXECUTION.md`, `docs/seo-insights-platform-architecture.md`, P4, the AI readiness/parser/crawl services, outreach approval, dashboard, and focused tests.

## Execution Path
Freeze conservative evidence semantics, harden parsing and applicability, fix crawl identity/accounting, gate presentation and approval by completeness, compact references, then validate against fixtures and the two primary targets.

## Patterns To Mirror
Versioned score contracts, unknown-versus-inapplicable semantics, immutable artifacts, host-safe fetches, additive compatibility, and independently resolvable run-relative evidence.

## Task Slices

### T1: Freeze hardening contracts
- Status: completed
- Owner: parent
- Depends on: none
- Write set: plan, scoring/parser contract tests
- Acceptance: executable expectations cover content regions, applicability, provisional presentation, compact references, and crawl identity
- Validate: `python -m pytest tests/test_ai_readiness_contract.py tests/test_ai_page_evidence.py tests/test_single_crawl.py -q`
- Evidence: 10 focused parser/scoring/crawl contract tests pass

### T2: Tighten evidence semantics
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: `src/fetchers/page_fetcher.py`, `src/services/ai_readiness_service.py`, focused tests
- Acceptance: citations, direct answers, headings, first-party evidence, authorship, and JSON-LD use conservative page-aware evidence
- Validate: `python -m pytest tests/test_ai_page_evidence.py tests/test_ai_readiness_contract.py -q`
- Evidence: page evidence v2 excludes chrome/social links and generic numbers, validates one-H1 hierarchy, contextual answer blocks, applicability, and visible schema values

### T3: Fix crawl identity and confidence
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: `src/services/page_analysis_service.py`, crawl models/tests
- Acceptance: redirects/canonicals normalize to one persisted identity; counts satisfy collected <= attempted <= discovered; capped link evidence remains unknown
- Validate: `python -m pytest tests/test_single_crawl.py tests/test_http_safety.py -q`
- Evidence: redirect/www/canonical fixture persists one resolved identity; capped clean link health is unknown

### T4: Gate presentation and compact evidence
- Status: completed
- Owner: parent
- Depends on: T2, T3
- Write set: reporting, outreach approval, dashboard, API/service tests
- Acceptance: partial scores are visibly provisional, cannot silently become approved customer claims, and check references contain bounded observations rather than complete repeated page payloads
- Validate: `python -m pytest tests/test_api.py tests/test_dashboard_ui.py tests/test_revenue_services.py tests/test_orchestration.py -q`
- Evidence: 58 API/dashboard/outreach/orchestration/integrity tests pass; partial AI approval requires explicit acknowledgement and every compact check reference resolves

### T5: Calibrate and close
- Status: completed
- Owner: parent
- Depends on: T4
- Write set: generated artifacts and plan evidence only
- Acceptance: full suite passes; valid bounded runs for `laceyglass.com` and `novaryu.com` expose consistent inventory, compact references, and honest confidence language
- Validate: `python -m pytest -q`
- Evidence: 160 tests pass; valid after-runs `31b98008-5150-4f57-b53e-32436396880d` and `c3a2c663-007e-4e90-a2c4-5353f87b7eba`

## Verification
Focused fixtures, full pytest, PRP validation, tooling doctor, real target runs without paid enrichment, and direct artifact checks for size, reference resolution, counts, completeness, and provisional language.

## Evidence And Handoff
Full suite, PRP validation, tooling doctor, and diff checks pass. Lacey Glass changed from 60.36/Solid at 93% to 40.82/Developing at 89.25%; its report shrank from 1,378,241 to 154,165 bytes and inventory is 19 collected / 20 attempted / 119 discovered with one alias collapsed. Nova Ryu changed from 71.73/Solid at 93% to 65.03/Provisional — Solid at 84.45%; its report shrank from 1,080,712 to 74,663 bytes and inventory is 9 / 9 / 10. All 253 combined final check references independently resolve; maximum observed payload is 1,046 bytes.
