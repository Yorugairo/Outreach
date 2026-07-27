---
id: P7-OFFSITE-AUTHORITY-EVIDENCE
title: DataForSEO Off-site Authority Evidence
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

# DataForSEO Off-site Authority Evidence

## Summary
Add a bounded, separately presented off-site authority module using DataForSEO backlink evidence, and correct ranking presentation to distinguish organic position from absolute SERP placement.

## Intent And Acceptance
Each approved paid run may reserve one of the existing six provider calls for a backlink summary. The product reports DataForSEO Link Rank, backlinks, referring domains/main domains/pages/IPs/subnets, nofollow ratios, broken-link/spam signals, source/date/cost, and limitations. It never calls this Google Domain Authority and never changes SEO or AI Readiness arithmetic. Missing or failed evidence is unknown. Google ranking tables headline organic group position and retain absolute SERP position as secondary evidence.

## Scope
DataForSEO request/parsing and shared call budget, typed authority view, additive v2 report payload and Markdown, API endpoint, dashboard, outreach evidence brief, compatibility tests, and one bounded Nova Ryu verification.

## Not Building
A proprietary authority score, Google PageRank claims, backlink outreach, link-quality judgments, competitor backlink analysis, historical trend tracking, or autonomous link acquisition.

## Human Gates
The user explicitly approved adding the paid evidence module. Collection remains bounded by the existing configured six-call cap and local approval policy. No deployment, credential, provider-account, or external write changes are authorized.

## Mandatory Reads
`docs/runbooks/PRP_EXECUTION.md`, P6, DataForSEO Backlinks Summary documentation, DataForSEO/search services, reporting, API/dashboard, outreach, and focused tests.

## Execution Path
Freeze evidence semantics, add one provider call inside the existing shared budget, normalize it into a fail-closed view, surface it on all evidence-bearing product surfaces, then validate with fixtures and one Nova Ryu collection.

## Patterns To Mirror
Immutable raw provider artifacts, additive report fields, explicit unknown semantics, target-bound validation, provider-specific naming, and persisted evidence references.

## Task Slices

### T1: Freeze authority and rank contracts
- Status: completed
- Owner: parent
- Depends on: none
- Write set: plan, authority service, provider/search tests
- Acceptance: Link Rank terminology, unknown semantics, metric fields, non-scoring rule, and organic-versus-absolute rank meanings are executable
- Validate: `python -m pytest tests/test_offsite_authority.py tests/test_dataforseo_search.py -q`
- Evidence: `offsite-authority.v1`, DataForSEO-only terminology, fail-closed target/date/source/rank-scale validation, and organic/absolute rank fixtures pass

### T2: Collect within the shared paid-call budget
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: DataForSEO client, search-intelligence service, focused tests
- Acceptance: one Backlinks Summary request is attributable to its raw artifact; total calls never exceed configured maximum; provider failure remains unknown
- Validate: `python -m pytest tests/test_dataforseo_search.py tests/test_offsite_authority.py -q`
- Evidence: six-call allocation is 1 authority + 1 keyword discovery + up to 3 ranking checks + up to 1 mention; one-call mode collects authority only; raw artifacts and provider errors are attributable

### T3: Surface authority evidence
- Status: completed
- Owner: parent
- Depends on: T2
- Write set: reporting, API, dashboard, outreach brief, focused tests
- Acceptance: v2 JSON/Markdown, API, dashboard, and evidence brief show the module and disclaimer; cold-email opening and SEO/AI scores remain unchanged
- Validate: `python -m pytest tests/test_api.py tests/test_dashboard_ui.py tests/test_revenue_services.py tests/test_integrity_regressions.py -q`
- Evidence: v2 JSON/Markdown, `/offsite-authority`, dashboard cards/disclaimer, and outreach brief tests pass; rendered dashboard shows unknown-state semantics without console warnings

### T4: Verify Nova Ryu and regressions
- Status: completed
- Owner: parent
- Depends on: T3
- Write set: generated artifacts and plan evidence only
- Acceptance: a valid Nova Ryu report contains target-bound authority evidence and the full regression suite passes
- Validate: `python -m pytest -q`
- Evidence: valid Nova Ryu attempt `620bc87b-41e9-4902-8f6d-a3726a748ae2`; one $0.024036 call; Link Rank 12/100, 57 backlinks, 46 referring domains; 171 tests pass

## Verification
Focused authority/provider tests, report/API/dashboard/outreach tests, full pytest, PRP validation, tooling doctor, artifact validation, rendered dashboard inspection, and diff review.

## Evidence And Handoff
Nova Ryu run `4d690da7-8566-4622-a894-30864d5082cc` is valid and now contains a target-bound authority view backed by raw artifact `artifacts/seo_insight_runs/dataforseo_raw/1785031699497_v3__backlinks__summary__live.json`. The report presents Link Rank and link-count evidence separately from SEO 40.0 and AI Readiness; automatic keyword discovery was intentionally not rerun, leaving search status limited rather than reintroducing the previously rejected national keyword set. Full suite: 171 passed. PRP validation, tooling doctor, artifact validation, diff check, rendered dashboard inspection, and console check pass.
