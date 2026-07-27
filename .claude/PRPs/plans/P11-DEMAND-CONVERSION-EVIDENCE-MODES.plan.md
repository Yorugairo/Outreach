---
id: P11-DEMAND-CONVERSION-EVIDENCE-MODES
title: Owner-Verified Demand and Conversion Evidence Modes
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-26
updated: 2026-07-26
---

# Owner-Verified Demand and Conversion Evidence Modes

## Summary

Add a separate demand-to-conversion evidence layer to the URL-first product. It should answer the commercial question “how much qualified demand may be available, and what could converting it be worth?” without pretending that public keyword volume is unique people or that a ranking change guarantees revenue.

The layer has two explicit modes:

- **Prospect mode:** public crawl, public SERP/Maps observations, approved keyword/demand imports, Google Trends, and optional third-party estimates. It produces bounded opportunity ranges and a short list of what the owner must verify.
- **Owner-verified mode:** the same public evidence plus explicitly authorized, aggregate exports from Search Console, GA4, GBP, and booking/CRM systems. It replaces assumptions with observed query, traffic, and funnel evidence while preserving privacy and provenance.

The existing SEO, technical health, AI Readiness, conversion-readiness, market, and opportunity artifacts remain independent and immutable. Add `reports/demand-conversion-v1.json|md` and an additive combined report `v5` when available; v1/v2/v3/v4 artifacts remain readable without backfill.

## Intent And Acceptance

### Primary outcome

An operator can paste a URL and receive a prospect-mode report. If the owner supplies approved aggregate exports, the operator can produce an owner-verified report that calibrates demand, funnel, capacity, and recurring-revenue scenarios.

### Acceptance criteria

- A versioned `DemandConversionEvidence` contract records mode, source hierarchy, source context, freshness, provenance, confidence/completeness, demand intent groups, observed funnel inputs, modeled outputs, capacity, economics, assumptions, warnings, and evidence references.
- Every demand/conversion claim is labeled `observed`, `supplied`, `assumed`, or `modeled`; source class and retrieval/snapshot date are persisted. Unknown values are omitted from arithmetic and surfaced as evidence limits, never converted to zero.
- Public demand rows are clustered into distinct intent families and close variants before aggregation. The system never sums all keyword rows and calls the result unique searchers.
- Prospect mode cannot read owner-only sources. Owner-verified mode requires explicit operator/owner authorization, exact prospect/vertical/market context, and immutable aggregate snapshots; it never accepts credentials, raw PII, or cross-prospect data.
- Owner evidence can include Search Console query/page metrics, GA4 event/funnel aggregates, GBP performance exports, and booking/CRM aggregate outcomes. The import path is CSV-first and additive; live connectors are optional and gated.
- Modeled incremental outcomes use a deterministic, versioned formula with low/base/high ranges and a capacity cap:

  `incremental_members = min(incremental_qualified_visits × lead_rate × booking_rate × close_rate, available_capacity)`

  `incremental_recurring_revenue = incremental_members × monthly_price`

  The report clearly distinguishes baseline observed outcomes from modeled lift and does not claim causality, rank-one capture, or guaranteed revenue.
- Prospect mode includes relative trend/seasonality and market estimates only as supporting evidence; Google Trends, Keyword Planner exports, and Ahrefs estimates cannot be presented as unique people or first-party conversions.
- Owner mode can report actual GSC impressions/clicks/CTR/position, GA4 sessions/events, GBP actions, and aggregate bookings/customers/revenue when those artifacts are supplied and context-valid.
- A demand-conversion report and combined v5 report render source hierarchy, demand clusters, observed-vs-modeled funnel, capacity/revenue ranges, confidence, limitations, and “what would change this.” Client bundles hide owner-private data unless explicitly generated in owner-verified mode.
- URL-first remains the primary dashboard action. Source imports, mode selection, calibration, and report export are secondary operator tools.
- Historical reports, checkpoints, outreach packages, and existing opportunity scenarios remain readable. New reports revalidate all references before client export.
- Regression/security tests prove no PII leakage, source-context mismatch, unsupported claims, score contamination, or unresolved exported evidence.

## Evidence Hierarchy And Semantics

The hierarchy governs confidence and claim language; it is not a new SEO/AI score:

1. **Owner first-party observed:** Search Console, GA4, GBP, and aggregate booking/CRM outcomes. Highest confidence for the owner’s actual queries, visits, actions, and funnel.
2. **Operator-supplied business facts:** approved capacity, pricing, retention, current baseline, service area, and keyword/intent approvals.
3. **Approved market evidence:** Keyword Planner or equivalent exported estimates, Google Trends relative interest/seasonality, and the supplied keyword set. Useful for market direction, never unique-person counts.
4. **Public observed evidence:** deterministic crawl, public organic/Maps samples, ranking URLs, landing-page and local-pack observations.
5. **Third-party modeled estimates:** Ahrefs or similar ranking/backlink/traffic estimates. Useful for discovery and comparative context, explicitly provider-specific and non-observed.
6. **Scenario assumptions and derived models:** operator-approved rates, capture ranges, economics, capacity constraints, and deterministic calculations.

`source_class` identifies the tier and `provenance_label` is one of `observed`, `supplied`, `assumed`, or `modeled`. Every row/snapshot includes source name, artifact hash, market/location, device/date range, prospect/vertical binding, and freshness. A report may be numerically useful with incomplete evidence, but its completeness/status and limitations are mandatory.

## Scope

### In scope

- Additive contracts, repository methods, file-backed and SQLite persistence paths for demand/conversion snapshots and reports.
- CSV preview/commit with safe parsing, source hashing, duplicate/intent-family validation, formula/PII/secret rejection, and row-level errors.
- Intent grouping, trend/seasonality evidence, GSC query/page alignment, funnel calibration, capacity-aware scenarios, and evidence references.
- Prospect/owner-verified mode gates, immutable successor versions, report assembly, API endpoints, dashboard operator tools, client bundle filtering, and regression/security tests.
- Pilot fixtures for Nova Ryu/Tacoma and Lacey Glass/trades using synthetic or operator-provided aggregate data.

### In Scope

The implementation adds the contracts, services, repository persistence, APIs,
dashboard operator tools, report artifacts, and tests required to support both
evidence modes. It is additive to the existing run/report/package contracts.

## Not Building

- No autonomous access requests, credential collection, OAuth connection, scraping of private properties, or live CRM replacement.
- No raw names, emails, phone numbers, booking records, or other PII in the evidence layer.
- No ranking, AI citation, traffic, lead, or revenue guarantees; no claim that a keyword volume equals people.
- No automatic causality inference from an SEO change, no LLM judge in score arithmetic, and no new headline SEO/AI score.
- No autonomous content publishing, outreach sending, billing, backlink acquisition, competitor contact, or mandatory DataForSEO paid runs.
- No silent mutation/backfill of existing artifacts; formula or contract changes require a new version.

## Mandatory Reads

- `AGENTS.md`, `docs/AGENT_START_HERE.md`, and
  `docs/agent-context/SKILL_ROUTER.md`.
- `docs/runbooks/PRP_EXECUTION.md` and
  `.claude/PRPs/templates/prp-template.md`.
- `docs/product-revenue-contract.md`,
  `docs/product-strength-contract.md`, and
  `docs/agentic-analysis-contract.md`.
- `src/models.py`, `src/pipeline.py`,
  `src/services/owned_measurement_service.py`,
  `src/services/demand_evidence_service.py`,
  `src/services/opportunity_reporting_service.py`,
  `src/api/app.py`, and `src/api/static/dashboard.html`.
- `.context/query-context.md` generated by SigMap for the current architecture
  trace.

## Execution Path

1. Freeze contracts and fixtures before changing persistence or UI.
2. Extend CSV-first source adapters and demand grouping with immutable hashes
   and context validation.
3. Align observed search evidence, then implement the deterministic model.
4. Add mode/privacy gates before exposing report or export paths.
5. Assemble the dedicated report and combined v5 artifact.
6. Expose API/dashboard operator tools while keeping URL-first simple.
7. Run the Nova/Lacey pilot with synthetic or explicitly supplied aggregate
   inputs, record calibration, and complete the release gate.

Each slice must be tested before the next dependent slice, and every completed
slice replaces `Evidence: pending` with exact command output, artifact paths,
and parent-reviewed diff evidence.

## Patterns To Mirror

- `OwnedMeasurementService` for aggregate-only CSV preview/commit, source hash,
  context validation, and immutable snapshots.
- `DemandEvidenceService` for keyword normalization, intent grouping, review
  states, and “occasions, not people” semantics.
- `OpportunityScenario` and `OpportunityReportingService` for capacity-aware
  low/base/high ranges, sensitivity, service-path fit, and limitations.
- `ProductSurfaceResult` and existing score services for versioned output,
  completeness/status, unknown/inapplicable semantics, and evidence refs.
- `ReportSnapshot`, client bundles, and manifest validation for immutable
  report output and claim-level provenance.
- Existing FastAPI/Pydantic routes and dashboard secondary operator panels;
  URL paste remains the default action.

## Current implementation anchors

- `src/models.py`: `OwnedMeasurementSnapshot`, `DemandEvidenceRow`, `DemandGroup`, `DemandEvidenceSet`, `BusinessEconomicsProfile`, `OpportunityScenario`, `ProductSurfaceResult`, `ReportSnapshot`, and `InsightReport` are the additive model seams.
- `src/services/owned_measurement_service.py`: already provides aggregate-only CSV preview/commit, source hashes, context validation, immutable snapshots, and funnel baseline derivation for `gsc_csv`, `gbp_csv`, `ga4_csv`, `crm_csv`, and `ai_performance_csv`.
- `src/services/demand_evidence_service.py`: already imports/validates demand CSVs and warns that monthly searches are occasions, not people; extend rather than replace its grouping rules.
- `src/services/opportunity_reporting_service.py`: already emits demand groups, modeled prospect ranges, capacity/revenue scenarios, sensitivity, evidence completeness, and limitations; reuse its formula/evidence-reference patterns and add a dedicated demand-conversion artifact.
- `src/pipeline.py`: preserves the staged run contract and current SEO/AI/conversion stages; add a non-blocking demand-conversion stage/output after owner/public evidence is available.
- `src/api/app.py`: existing keyword-set, demand-evidence, opportunity, owner-measurement, report, and client-bundle endpoints are the API extension points.
- `src/api/static/dashboard.html`: already keeps paste-URL primary and has operator panels for keyword/demand imports, owner measurements, opportunity scenarios, and report display.
- `docs/product-revenue-contract.md`, `docs/product-strength-contract.md`, `docs/agentic-analysis-contract.md`, and `.context/query-context.md` define current immutable artifact, evidence, and operator-review conventions.

## Data model and persistence contract

Add versioned, immutable records (dataclasses with `slots=True`, `to_dict()`, repository protocol methods, file-backed implementation, and SQLite additive storage where applicable):

- `DemandConversionEvidence`: run/target/prospect/vertical binding; mode; hierarchy and source snapshots; intent groups; observed inputs; modeled outputs; economics/capacity; confidence/completeness/status; formula/version; assumptions, warnings, and evidence refs.
- `DemandTrendSnapshot`: normalized market/geo/timeframe/terms, Trends relative index/seasonality or Keyword Planner export fields, source hash, import metadata, and review status.
- `ConversionEventMap`: approved GA4/GBP/booking/CRM event names mapped to funnel stages (`visit`, `lead`, `booking`, `attended`, `customer`, `revenue`) with source/provenance and version.
- `DemandConversionReportSnapshot`: immutable JSON/Markdown payload plus manifest and source hashes; report contract `demand-conversion-v1`.

Store new artifacts beneath the originating run (`reports/demand-conversion-v1.*`, `reports/v5.*` when assembled) and store source snapshots independently so multiple runs and mode versions remain attributable. Do not rewrite legacy reports or owner snapshots. Enforce repository reads by exact IDs and prospect/vertical/context binding.

## Task Slices

### T1: Freeze evidence hierarchy and contracts

- Status: completed
- Owner: parent
- Depends on: none
- Write set: `src/models.py`, contract constants, docs, `tests/test_demand_conversion_contract.py`
- Acceptance: invalid mode/source combinations, missing context, unsupported labels, and unique-person claims fail contract validation; legacy models deserialize unchanged.
- Validate: `python -m pytest tests/test_demand_conversion_contract.py -q`
- Evidence: Added versioned demand-conversion, trend, conversion-event-map, and
  report-snapshot contracts plus hierarchy/mode/provenance constants and
  privacy/context validation in `src/models.py`; documented the two modes and
  formula in `docs/product-revenue-contract.md`.
  `python -m pytest tests/test_demand_conversion_contract.py -q` -> `6 passed`.

### T2: Harden owner evidence imports and source adapters

- Status: completed
- Owner: implementation_luna
- Depends on: T1
- Write set: `src/services/owned_measurement_service.py`, repository methods, API schemas, `tests/test_owned_measurement_imports.py`
- Acceptance: preview/commit is deterministic and immutable; PII/formula/secret fields, wrong prospect/vertical/market, stale/mismatched context, and duplicate snapshots are rejected or marked as limits; no prospect-mode read path can access owner snapshots.
- Validate: `python -m pytest tests/test_owned_measurement_imports.py tests/test_revenue_services.py -q`
- Evidence: Extended aggregate-only owner imports with source-specific GSC
  query/page, GBP actions, GA4 events, and CRM funnel dimensions; added safe
  consent/freshness/event-map context, stable deduplication, and scope/privacy
  gates. `python -m pytest tests/test_owned_measurement_imports.py
  tests/test_owned_measurement.py tests/test_revenue_services.py -q` ->
  `17 passed`.

### T3: Add trend ingestion and intent-family clustering

- Status: completed
- Owner: implementation_luna
- Depends on: T1
- Write set: `src/services/demand_evidence_service.py`, new trend service/model persistence, keyword-set APIs, `tests/test_demand_trends.py`, `tests/test_keyword_intent_groups.py`
- Acceptance: supplied Tacoma terms produce deterministic groups without double-counting; Trends is clearly relative; group aggregation requires explicit rules/approval; unsupported factual terms remain `needs_review`; no output says “unique searchers.”
- Validate: `python -m pytest tests/test_demand_trends.py tests/test_keyword_intent_groups.py -q`
- Evidence: Added bounded Google Trends/Keyword Planner CSV parsing,
  relative-trend and seasonality semantics, deterministic close-variant and
  intent-family grouping, factual-risk exclusion, review/approval successors,
  and no-people-count gates. `python -m pytest tests/test_demand_trends.py
  tests/test_keyword_intent_groups.py tests/test_demand_evidence.py
  tests/test_keyword_sets.py -q` -> `18 passed`.

### T4: Align observed search visibility to demand groups

- Status: completed
- Owner: parent
- Depends on: T1, T2, T3
- Write set: `src/services/search_visibility_service.py`, new alignment service, `tests/test_demand_conversion_search_alignment.py`
- Acceptance: only exact context-compatible artifacts align; unavailable GSC remains unknown; market estimates and observed queries remain separate; every displayed metric resolves to persisted evidence.
- Validate: `python -m pytest tests/test_demand_conversion_search_alignment.py tests/test_search_visibility.py -q`
- Evidence: Added `DemandConversionSearchService` with exact/close-variant
  alignment, GSC query/page aggregation, public ranking references, context
  mismatch rejection, and unknown semantics. The parent-owned T4–T6 focused
  suite, including visibility and integrity regressions, completed with
  `59 passed`.

### T5: Implement deterministic demand-to-conversion modeling

- Status: completed
- Owner: parent
- Depends on: T2, T3, T4
- Write set: new `src/services/demand_conversion_service.py`, model fixtures, `tests/test_demand_conversion_model.py`
- Acceptance: exact fixtures are deterministic; missing rates remain unknown and reduce completeness rather than becoming zero; capacity limits are explicit; the output states that lift is a scenario, not a forecast guarantee or causal finding.
- Validate: `python -m pytest tests/test_demand_conversion_model.py tests/test_scorecard_semantics.py -q`
- Evidence: Added `DemandConversionService`, deterministic low/base/high
  visit-to-lead-to-booking-to-customer calculations, observed owner-rate
  substitution, capacity caps, source hierarchy, completeness, warnings, and
  additive file/SQLite persistence through migration
  `011_demand_conversion_evidence.sql`. Model/contract tests completed with
  `11 passed`; repository/model tests completed with `6 passed`.

### T6: Add prospect/owner-verified lifecycle and leakage gates

- Status: completed
- Owner: parent
- Depends on: T2, T5
- Write set: pipeline contracts, repository authorization helpers, `src/services/report_validation_service.py`, `tests/test_evidence_modes.py`, `tests/test_privacy_context.py`
- Acceptance: a mode cannot be silently upgraded; invalid/private references block approval/export; legacy package/report reads still work; no PII or owner data appears in a prospect/client bundle.
- Validate: `python -m pytest tests/test_evidence_modes.py tests/test_privacy_context.py tests/test_integrity_regressions.py -q`
- Evidence: Added immutable approval successors and
  `DemandConversionReportValidationService` with exact mode, state, source
  hash, context, safe-path, nested-private-field, and cross-prospect export
  gates. `python -m pytest tests/test_evidence_modes.py
  tests/test_privacy_context.py tests/test_demand_conversion_repository.py -q`
  -> `7 passed`.

### T7: Assemble demand-conversion and combined client reports

- Status: completed
- Owner: implementation_luna
- Depends on: T4, T5, T6
- Write set: `src/services/report_assembly_service.py`, `src/services/opportunity_reporting_service.py`, client bundle/manifest services, report templates, `tests/test_demand_conversion_report.py`
- Acceptance: every claim/reference resolves to a persisted artifact; prospect/owner output filtering is enforced; the evidence brief includes the score/formula only as context and never leads the cold-email opening with a score or ranking promise.
- Validate: `python -m pytest tests/test_demand_conversion_report.py tests/test_client_bundles.py tests/test_revenue_services.py -q`
- Evidence: Added `DemandConversionReportingService` with ordered
  `demand-conversion-v1` and additive `v5` JSON/Markdown, exact evidence
  revalidation, prospect privacy filtering, first-writer canonical aliases,
  evidence-scoped mode/version artifacts, and hash-matched immutable report
  snapshots. Mode coexistence and legacy v2/v4 preservation are covered by
  `tests/test_demand_conversion_report.py`. The report/client/revenue focused
  validation completed with `14 passed`.

### T8: Expose API and dashboard operator workflow

- Status: completed
- Owner: implementation_luna
- Depends on: T6, T7
- Write set: `src/api/app.py`, `src/api/static/dashboard.html`, API/dashboard tests
- Acceptance: URL run → prospect report works with no private sources; owner imports → validation → owner-verified report works with explicit approval; incomplete/unknown evidence is visible and cannot be exported as resolved; UI remains usable without interacting with advanced panels.
- Validate: `python -m pytest tests/test_api.py tests/test_dashboard_ui.py tests/test_demand_conversion_api.py -q`
- Evidence: Added trend preview/commit/approval, conversion-event maps,
  readiness, prospect/owner evidence build/approval, mode-scoped report reads,
  and immutable v5 report APIs. URL and qualified-prospect run routes now
  attach a non-blocking prospect evidence draft with unknown arithmetic when
  operator inputs are absent. The secondary dashboard supports mode choice,
  explicit owner consent, aggregate snapshot IDs, trend sources, event maps,
  report build/review, and visible limitations while keeping paste-URL first.
  `python -m pytest tests/test_demand_conversion_api.py
  tests/test_dashboard_ui.py tests/test_api.py tests/test_opportunity_api.py -q`
  passed within the parent-focused `74 passed` suite.

### T9: Pilot, calibration, durability, and release gate

- Status: completed
- Owner: parent
- Depends on: T1–T8
- Write set: pilot fixtures/runbook, `tests/test_demand_conversion_pilot.py`, docs/runbooks updates
- Acceptance: 90%+ exported claims resolve to artifacts; zero PII in reports; prospect runs complete without owner access; owner runs require explicit source approval; capacity/revenue ranges are reproducible; review corrections and limitations are persisted.
- Validate: `python -m pytest tests/test_demand_conversion_pilot.py -q`; then full verification below.
- Evidence: Added synthetic Nova Ryu/Tacoma and Lacey Glass/trades pilot
  fixtures, capacity/revenue reproducibility and 90%+ reference-resolution
  assertions, zero-owner/PII prospect assertions, and
  `docs/runbooks/DEMAND_CONVERSION_EVIDENCE.md`. The focused pilot completed
  with `1 passed`; the complete P11/API/integrity regression set completed with
  `74 passed`. A read-only reviewer identified mode-scoped report aliasing;
  the parent fixed it and added an end-to-end prospect/owner coexistence API
  regression plus missing-public-artifact export rejection.

## API And Operator Interfaces

Additive endpoints (exact names may follow existing route conventions):

- `POST /api/runs/{run_id}/demand-conversion` with `mode=prospect|owner_verified` and source readiness.
- `GET /api/runs/{run_id}/demand-conversion` and `GET /api/runs/{run_id}/reports/demand-conversion-v1`.
- `POST /api/demand-trends/csv-preview`, `POST /api/demand-trends/csv-commit`.
- `POST /api/owner-measurements/{snapshot_id}/approve` and event-map/economics approval routes where absent.
- `GET /api/prospects/{prospect_id}/evidence-readiness` and mode/report export status.

All writes create immutable versions and return artifact IDs/source hashes. Approval/export revalidates prospect, vertical, market, time range, source freshness, privacy classification, and every evidence reference.

Dashboard order:

1. Paste URL and run (prospect mode default).
2. SEO, AI, and existing conversion headlines.
3. Demand clusters/trend direction and public ranking observations.
4. Demand-to-conversion ranges, capacity, and service-path actions with labels.
5. Owner verification prompt showing exactly which aggregate exports would improve confidence.
6. Advanced operator tools for imports, event mapping, economics, calibration, and export.

## Security, Durability, And Failure Behavior

- Reuse existing SSRF, redirect-host, body-size, timeout, CSV formula-injection, path-containment, and artifact-integrity protections.
- Reject raw PII and credentials; allow only aggregate owner exports with explicit field allowlists.
- Bind every source to prospect, normalized domain, vertical, market/location, device, and period; mismatches are hard validation errors.
- Paid/external absence is `unknown`/evidence limit, never a score penalty. Provider failures create partial snapshots and preserve successful artifacts.
- Never fetch or infer private owner data from a public URL; never mix owner evidence into a prospect outreach package.
- Formula/check changes create a new report version. Historical runs and reports are never silently recomputed.

## Human Gates

- Owner explicitly authorizes aggregate exports and confirms property/market/time period.
- Operator approves keyword/intent grouping, business economics, conversion event mapping, and any external estimate source.
- Operator reviews any factual-risk keyword or unsupported claim before inclusion.
- Client/outreach export requires evidence revalidation and owner/prospect mode confirmation.
- No credential, deployment, paid-provider, email-send, or third-party write action is implied by this plan.

## Verification

Focused checks per slice are listed above. Full verification:

```bash
python -m pytest -q
python scripts/prp_validate.py .claude/PRPs/plans/P11-DEMAND-CONVERSION-EVIDENCE-MODES.plan.md
python scripts/agent_tooling_doctor.py
```

Artifact acceptance for a completed run:

- `run.json` remains completed with the existing summary fields.
- Existing report artifacts remain readable and unchanged.
- New `reports/demand-conversion-v1.json|md` exists when the stage is run; combined `reports/v5.json|md` exists only when assembled.
- Stage/event/checkpoint references identify mode, source snapshots, formula version, and completeness/status.
- Client bundle manifest resolves every displayed demand, funnel, capacity, revenue, and recommendation claim to a persisted artifact.

Primary documentation anchors:

- [Search Console performance data and metrics](https://support.google.com/webmasters/answer/7042828?hl=en), [Search Console data aggregation and limits](https://support.google.com/webmasters/answer/17011364?hl=en), and [Search Console property access](https://support.google.com/webmasters/answer/34592?hl=en).
- [GA4 events](https://support.google.com/analytics/answer/9356037?hl=en), [GA4 key events](https://support.google.com/analytics/answer/9356034?hl=en), and [GA4 permissions](https://support.google.com/analytics/answer/12996377?hl=en).
- [GBP performance](https://support.google.com/business/answer/9918094?hl=en-en) and [GBP owners/managers](https://support.google.com/business/answer/3403100).
- [Google Trends methodology](https://support.google.com/trends/answer/4365533?hl=en), [comparison](https://support.google.com/trends/answer/4359550), and [regional interest](https://support.google.com/trends/answer/4355212).
- [Google Keyword Planner](https://support.google.com/google-ads/answer/3022575?hl=en).
- [Ahrefs organic traffic estimates](https://help.ahrefs.com/en/articles/1863206-what-is-organic-traffic-in-ahrefs-and-how-do-we-calculate-it) and [organic keyword limitations](https://help.ahrefs.com/en/articles/3410559-what-are-organic-keywords).

## Evidence And Handoff

- Current-code trace: `.context/query-context.md`, generated by the required
  SigMap architecture query before planning.
- Evidence hierarchy and official-source links are documented above; the
  hierarchy is a confidence/provenance contract, not another score.
- Existing owner measurement, demand evidence, opportunity, report snapshot,
  and dashboard surfaces are additive anchors; no existing report is rewritten.
- Validation command: `python scripts/prp_validate.py
  .claude/PRPs/plans/P11-DEMAND-CONVERSION-EVIDENCE-MODES.plan.md`.
- Implementation was explicitly authorized by the operator through
  `prp-implement` on 2026-07-26. Persist slice status and evidence here.
- Final release verification on 2026-07-26:
  `python -m pytest -q` -> `349 passed in 59.51s`;
  `python scripts/prp_validate.py
  .claude/PRPs/plans/P11-DEMAND-CONVERSION-EVIDENCE-MODES.plan.md` -> `PASS`;
  `python scripts/agent_tooling_doctor.py` -> `ok: true`;
  `python -m compileall -q src scripts`, dashboard JavaScript parsing, and
  `git diff --check` completed successfully (line-ending notices only).
