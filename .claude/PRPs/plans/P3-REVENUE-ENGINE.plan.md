---
id: P3-REVENUE-ENGINE
title: Verticalized SEO Insight Revenue Engine
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

## Summary

Extend the run-centric SEO insight engine into one internal operator product for
One Trade Network and National BJJ Registry. Add qualified prospect intake,
versioned vertical packs, evidence-gated outreach packages, append-only funnel
events, manual exports, and segmented operator analytics without changing the
existing six-stage pipeline or v1/v2 report contracts.

## Intent And Acceptance

- Import, validate, deduplicate, qualify, and reject prospects from curated CSV.
- Run only qualified prospects using the existing `InsightRun` path.
- Produce a reviewable website+pSEO outreach package only from a valid v2 report.
- Require operator approval before plaintext, Markdown, or JSON export.
- Record funnel progress as append-only events and derive segmented metrics.
- Preserve all existing API, artifact, scoring, security, and repository tests.

## Scope

- Models and built-in vertical-pack definitions.
- CSV preview/commit and qualification workflow.
- File and SQLite persistence with additive migration.
- Deterministic coverage assessment and immutable outreach-package lifecycle.
- Activation events, funnel summaries, API endpoints, and operator dashboard.
- Focused contract, repository, service, API, and UI tests.

## Not Building

- Automated discovery, outbound email, CRM replacement, billing, multi-tenancy,
  generative publishing, fabricated GEO/AEO/AIO scores, or competitor scoring.
- Backfills or mutations of existing runs and reports.
- Deployment, push, external writes, or production data migration.

## Human Gates

- User has explicitly approved local implementation.
- Commit, push, deployment, credentials, paid calls, and third-party writes remain
  unapproved and out of scope.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/product-revenue-contract.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `src/models.py`
- `src/repositories/base.py`
- `src/api/app.py`

## Execution Path

Implement model contracts first, then persistence and domain services in
parallel, followed by API/dashboard integration and full verification.

## Patterns To Mirror

- Slotted dataclasses with deterministic `to_dict()` serialization.
- `InsightRepository` Protocol with file-backed artifacts and SQLite JSON payloads.
- Additive numbered SQLite migrations.
- Pydantic API request validation and API-key protection.
- Evidence references that resolve to independently persisted run artifacts.

## Task Slices

### T1: Models, vertical packs, and CSV intake
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `src/models.py`, `src/vertical_packs.py`, `src/services/prospect_intake_service.py`, `tests/test_prospect_intake.py`
- Acceptance: both packs validate; CSV preview reports row errors; commit-ready prospects normalize and deduplicate by vertical plus domain; only qualified prospects are runnable.
- Validate: `python -m pytest tests/test_prospect_intake.py -q`
- Evidence: `python -m pytest tests/test_prospect_intake.py -q` -> 5 passed.

### T2: Persistence and additive migration
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `src/repositories/base.py`, `src/repositories/file_repository.py`, `src/repositories/sqlite_repository.py`, `src/repositories/migrations/003_revenue_engine.sql`, `tests/test_revenue_repository.py`
- Acceptance: vertical packs, prospects, packages, and activation events persist across reopen; activation events have no update/delete path.
- Validate: `python -m pytest tests/test_revenue_repository.py tests/test_sqlite_repository.py -q`
- Evidence: `python -m pytest tests/test_revenue_repository.py tests/test_sqlite_repository.py -q` -> 6 passed.

### T3: Opportunity, package, activation, and funnel services
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `src/services/opportunity_service.py`, `src/services/outreach_service.py`, `src/services/activation_service.py`, `tests/test_revenue_services.py`, `tests/test_commercial_findings.py`
- Acceptance: evidence families are additive; website+pSEO requires valid target demand, sufficient crawl evidence, and deterministic coverage gaps; only valid reports can create/approve/export immutable packages; funnel state derives from append-only events.
- Validate: `python -m pytest tests/test_revenue_services.py tests/test_commercial_findings.py -q`
- Evidence: `python -m pytest tests/test_revenue_services.py tests/test_commercial_findings.py -q` -> 18 passed.

### T4: API and dashboard workflow
- Status: complete
- Owner: implementation_luna
- Depends on: T2, T3
- Write set: `src/api/app.py`, `src/api/static/dashboard.html`, `tests/test_api.py`, `tests/test_dashboard_ui.py`
- Acceptance: authenticated endpoints cover pack listing, CSV preview/commit, prospect qualification/run, package create/review/approve/export, activation append, and funnel summaries; dashboard exposes the same workflow.
- Validate: `python -m pytest tests/test_api.py tests/test_dashboard_ui.py -q`
- Evidence: focused API/dashboard suites passed; Playwright confirmed API-key connection, dynamic vertical packs, a one-row CSV preview, responsive semantic controls, and zero console errors.

### T5: Integration and completion proof
- Status: complete
- Owner: parent
- Depends on: T1, T2, T3, T4
- Write set: `.claude/PRPs/plans/P3-REVENUE-ENGINE.plan.md`
- Acceptance: focused tests, full suite, diff review, tooling doctor, and PRP validation pass; no external actions occur.
- Validate: `python -m pytest -q; python scripts/agent_tooling_doctor.py; python scripts/prp_validate.py .claude/PRPs/plans/P3-REVENUE-ENGINE.plan.md; git diff --check`
- Evidence: `python -m pytest -q` -> 147 passed; `python -m compileall -q src tests` -> clean; `python scripts/agent_tooling_doctor.py` -> ok true; `python scripts/prp_validate.py .claude/PRPs/plans/P3-REVENUE-ENGINE.plan.md` -> PASS; `git diff --check` -> exit 0; independent review findings resolved.

## Verification

Run each focused command after its slice, then the full suite. Review existing
user-owned dirty files before accepting overlap. Confirm package artifacts live
under the originating run and prospect/event data remain separately attributable.

## Evidence And Handoff

Completed local implementation only. No commit, push, deployment, paid calls, credentials, or third-party writes were performed.
