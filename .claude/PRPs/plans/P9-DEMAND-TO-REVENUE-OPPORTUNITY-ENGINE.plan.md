---
id: P9-DEMAND-TO-REVENUE-OPPORTUNITY-ENGINE
title: Demand-to-Revenue Opportunity Engine
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-25
updated: 2026-07-25
---

# Demand-to-Revenue Opportunity Engine

## Summary

Strengthen the Outreach Program by connecting its observed SEO, AI, ranking,
Maps, competitor, authority, and conversion evidence to a transparent,
capacity-aware commercial opportunity model.

The product should answer four questions in order:

1. What is measurably true about this website and market?
2. How many search occasions and plausible unique prospects exist?
3. Given the business's price, capacity, and conversion funnel, what could
   improved visibility and signup reasonably capture?
4. Which of the three actual service paths best addresses the observed
   constraint?

This remains an internal expertise and acquisition product. Revenue outputs
are versioned forecasts with operator-reviewed assumptions, not scores,
guarantees, or claims of lost revenue.

The Nova Ryu premium run is the initial acceptance fixture:

- monthly membership: `$100`;
- comfortable capacity headroom: `20` members;
- current capacity ceiling: `$2,000` additional MRR and `$24,000` annual
  run-rate;
- SEO score: `26.67`;
- AI Readiness: `57.25`, with AEO as the primary AI weakness;
- live ranking, Maps, competitor, screenshot, and authority evidence exists;
- the provider run exposed retry, balance, status, volume-return, and immutable
  recovery weaknesses that this PRP must resolve.

## Intent And Acceptance

The default operator path remains:

**paste URL -> run once -> concise evidence -> optional premium evidence ->
reviewed opportunity model -> approved pitch package**

Acceptance requires:

- Preserve SEO, AI Readiness, market evidence, competitor evidence, and
  authority as independently versioned observed facts.
- Add a separate immutable demand and revenue-opportunity layer. It must never
  change SEO, AI, ranking, Maps, or competitor findings.
- Accept operator-supplied Google Keyword Planner or equivalent CSV evidence
  as the preferred demand source. Paid DataForSEO volume remains optional.
- Never sum all keyword volumes by default. Every approved keyword belongs to
  one reviewed intent/close-variant group.
- Treat keyword volume as search occasions, not unique people. Google Keyword
  Planner average monthly searches include close variants; Google Ads Unique
  Reach does not support Search campaigns.
- Estimate unique prospects as a versioned range from reviewed demand groups
  and explicit searches-per-prospect assumptions. Label the result `modeled`.
- Collect business economics: price, capacity headroom, retention, current
  funnel rates, and desired fill period. Each value records whether it is
  operator-observed, business-supplied, or assumed.
- Produce low, base, and high opportunity scenarios with:
  unique prospects, incremental visits, signups, attended trials/appointments,
  customers, time to fill, MRR, annual run-rate, and capacity constraint.
- Cap projected active customers at reviewed capacity. For Nova, no scenario
  may exceed 20 incremental active members without a separately approved
  expansion scenario.
- Expose the simple capacity ceiling even when demand evidence is missing, but
  suppress acquisition projections until demand and funnel assumptions are
  complete enough.
- Separate the three levers:
  visibility creates qualified visits; plugin/embed signup improvements affect
  visitor conversion; CRM/SaaS follow-up affects attendance and close rates.
  Do not add the levers as if their gains were independent.
- Add resumable provider collection. Retrying unresolved calls creates an
  immutable successor market run and reuses successful same-context evidence.
- Classify provider failures as transient, task-level, authentication,
  balance/payment, quota, invalid request, or unknown. Payment and
  authentication failures stop further paid calls.
- A market run with unresolved required calls is `partial`, never `complete`.
- Preflight reports planned calls, conservative maximum cost, recorded account
  readiness, reusable evidence, unresolved calls, and retry ceiling before an
  operator approves paid work.
- Generate immutable `opportunity-v1` JSON/Markdown and a combined operator
  `v4` report without rewriting v1/v2/v3, AI, or market-v1 artifacts.
- Generate an approved pitch pack with:
  verified teaser, observed evidence, modeled opportunity, assumptions,
  sensitivity, service fit, screenshots, and limitations.
- Numeric revenue projections remain in the evidence brief and call deck, not
  the cold-email opening.
- Allow aggregate experiment calibration from Google Ads, GA4, Search Console,
  signup, trial, and customer counts without importing raw emails, phone
  numbers, or other lead PII.
- Record forecast-versus-actual calibration so assumptions improve by vertical.
- Old runs, reports, keyword sets, packages, and events remain readable without
  backfill.

Pilot acceptance:

- Nova produces a reviewed opportunity model using `$100/month`, `20` available
  spots, operator-selected retention and funnel assumptions, and an uploaded
  Tacoma demand file.
- Nova's output clearly states `$2,000 MRR / $24,000 annual run-rate` as a
  capacity ceiling, not as promised ranking revenue.
- Searcher estimates are ranges and expose the searches-per-prospect divisor.
- A missing volume file yields an actionable input request, not invented
  demand.
- A simulated payment-required response stops the paid queue, preserves cost,
  marks the run partial, and offers a bounded immutable resume.
- A resume retries only unresolved eligible work and regenerates the gap,
  opportunity, market, and combined reports from the successor evidence.
- Lacey Glass can use the same contracts with trade-specific economics and
  conversion stages, proving the implementation is vertical-neutral.
- Every pitch claim resolves to observed evidence or a named modeled assumption.

## Scope

### 1. Provider reliability and cost control

- Add a versioned `ProviderCallRecord` contract inside market evidence with:
  provider, operation, query/target, context, attempt, status, failure class,
  retryability, actual cost, raw artifact reference, started/completed time,
  and predecessor call ID.
- Add `MarketEvidenceCompleteness` with expected, successful, unresolved,
  inapplicable, and reused counts by operation.
- Replace call-count-only terminal logic with required-evidence completeness.
- Add an immutable `resume_unresolved` operation that:
  creates a successor market run;
  copies successful matching evidence by reference;
  retries only unresolved retryable work;
  stops on payment/authentication failures;
  recomputes competitor candidates, gaps, recommendations, and reports.
- Add provider account/readiness preflight without exposing credentials.
- Compute conservative provider ceilings from configured/provider price
  metadata and observed maximums. Use `$1.50` as the initial BJJ premium warning
  threshold, not a silently enforced global price.
- Treat an empty paid keyword-volume response as an evidence limit even when
  the provider task reports success.

### 2. Demand evidence and keyword de-duplication

- Add immutable `DemandEvidenceSet` and `DemandGroup` contracts.
- Each demand row records keyword, normalized keyword, keyword-set target ID,
  market/location, source, snapshot period, monthly searches, match semantics,
  source row, and evidence reference.
- Each demand group records intent family, included keywords, representative
  term, aggregation rule, approved monthly search occasions, excluded
  duplicates, reviewer, and rationale.
- Supported aggregation rules:
  - `provider_grouped`: use a provider-exported grouped value;
  - `max_close_variant`: default to the maximum row within a close-variant
    group;
  - `sum_distinct_intents`: allowed only after explicit operator review.
- Default grouping is deterministic from keyword category, normalized tokens,
  search intent, and target-page usage. Operators approve or correct groups.
- Brand/lineage demand is reported separately and excluded from net-new
  customer opportunity by default.
- Unsupported programs or locations remain excluded until approved.
- Add CSV preview, row errors, source hashing, commit, review, approve,
  supersede, and prospect/keyword-set binding.
- DataForSEO metrics may populate the same contract, but a zero-row provider
  response never replaces an approved operator upload.

### 3. Business economics and opportunity scenarios

- Add immutable, versioned `BusinessEconomicsProfile` with:
  revenue model, price, currency, gross-margin mode, retention months, active
  customer count, capacity headroom, desired fill period, current monthly
  leads/signups, attendance rate, close rate, and provenance per field.
- Vertical packs define funnel labels:
  - BJJ: visit -> signup -> attended trial -> member;
  - trades: visit -> lead -> qualified appointment -> won job.
- Add immutable `OpportunityScenario` with formula version, source run/report
  versions, demand-set version, economics-profile version, status,
  completeness, low/base/high assumptions, outputs, sensitivity, service
  levers, evidence references, and warnings.
- Version `opportunity-formula.v1`:

```text
unique_prospects =
  approved_nonbrand_search_occasions / searches_per_prospect

incremental_visits =
  unique_prospects * incremental_click_share

incremental_customers =
  incremental_visits
  * visit_to_signup
  * signup_to_attended
  * attended_to_customer

capacity_adjusted_customers =
  min(incremental_customers, capacity_headroom)

capacity_mrr =
  capacity_headroom * monthly_price

annual_run_rate =
  capacity_adjusted_active_customers * monthly_price * 12
```

- Add a ramp view. A 12-month linear fill of Nova's 20 spots yields an average
  of 10 incremental active members in the first year and `$12,000` first-year
  revenue, while ending at `$2,000 MRR`; instant fill is explicitly not assumed.
- Retention and churn affect cohort/LTV views, but never increase the
  capacity-constrained active-member ceiling.
- Ranking CTR/click-share values are editable assumptions, not universal
  constants. Organic and Maps opportunity remain separate before combination.
- Avoid double-counting people exposed through both organic and Maps by using
  an explicit overlap assumption in each scenario.
- Model status is `complete`, `partial`, or `limited` from input completeness;
  revenue may be calculated when inputs are known, but approval requires all
  material assumptions to be reviewed.

### 4. Calibration and learning

- Add aggregate `AcquisitionCalibrationRecord` with period, vertical, market,
  source, impressions, clicks, total users, signups/leads, attended
  trials/appointments, new customers, spend, and artifact/source reference.
- No raw lead identity or PII enters this product.
- Import aggregate Google Ads/GA4/Search Console/CRM CSVs with preview and
  validation; automated connectors are deferred.
- Derive observed:
  sessions per user, visit-to-signup, attendance, close, cost per signup, cost
  per customer, and capacity fill rate.
- Preserve original scenario versions and create a successor calibrated
  scenario; never rewrite forecasts after outcomes are known.
- Segment forecast error and funnel outcomes by vertical and service package.

### 5. Reporting, pitch package, and operator experience

- Add `opportunity-v1` and combined `v4` report contracts.
- Order v4:
  executive answer; verified evidence; SEO and AI; ranking/Maps; competitors;
  demand groups; unique-prospect range; capacity/revenue scenarios; conversion
  opportunities; service-path fit; sensitivity; provider cost/completeness;
  screenshots; assumptions and limitations.
- Add a concise pitch mode:
  - `Verified now`
  - `Potential if assumptions hold`
  - `What we need to confirm`
  - `Recommended first move`
- Keep paste-URL as the only required launcher input.
- After a run, show one primary action: `Build opportunity case`.
- Keep demand upload, economics, paid resume, competitor approval, and
  calibration under expandable operator tools.
- Display actual provider cost, clean-run ceiling, rework/retry cost, and
  evidence completeness separately.
- Display modeled values with a persistent `Forecast, not guarantee` label.
- Add an operator-editable assumption panel with low/base/high columns,
  validation, provenance selectors, and capacity warnings.
- Map output to the real service packages:
  1. website + sitemap/SEO + owned vertical visibility;
  2. vertical plugin/embed signup or lead conversion;
  3. custom website + optional CRM/SaaS follow-up.
- Create one immutable pitch export containing plaintext teaser, Markdown
  evidence brief, structured JSON, and selected screenshots.
- Package approval/export revalidates every evidence, demand, economics,
  scenario, report, and screenshot reference.

### 6. Persistence and public interfaces

- Extend the repository Protocol, file-backed repository, and SQLite repository
  for demand sets, economics profiles, opportunity scenarios, and aggregate
  calibration records.
- Add additive migration `006_demand_opportunity.sql`; existing JSON-backed
  reports and market records require no backfill.
- Add APIs:
  - `POST /api/demand-evidence/csv-preview`
  - `POST /api/demand-evidence/csv-commit`
  - `POST /api/demand-evidence/{id}/approve`
  - `POST /api/prospects/{id}/demand-evidence/{id}/bind`
  - `POST /api/prospects/{id}/economics`
  - `GET /api/prospects/{id}/economics`
  - `POST /api/market-evidence/{id}/resume`
  - `POST /api/runs/{id}/opportunity-scenarios`
  - `GET /api/opportunity-scenarios/{id}`
  - `POST /api/opportunity-scenarios/{id}/approve`
  - `POST /api/calibration/csv-preview`
  - `POST /api/calibration/csv-commit`
  - `GET /api/runs/{id}/opportunity`
  - `POST /api/runs/{id}/pitch-pack`
- Preserve all existing endpoints and report readers.
- Store demand/economics/calibration independently; store opportunity and pitch
  artifacts beneath the originating run with immutable version attribution.

## Not Building

- No promise that a specific rank produces a specific revenue result.
- No single exact count of unique searchers from keyword volume.
- No summing of all keyword rows without reviewed de-duplication.
- No proprietary universal CTR curve presented as fact.
- No LLM judge in scoring, grouping, demand arithmetic, or revenue arithmetic.
- No Google Ads campaign creation or spend.
- No automated Google Ads, GA4, Search Console, CRM, billing, or payment
  connectors in this milestone.
- No raw lead/customer PII ingestion.
- No autonomous outreach, sending, follow-up, publishing, or ranking guarantee.
- No customer-facing multi-tenant SaaS.
- No mutation of historical runs, reports, packages, forecasts, or provider
  artifacts.
- No competitor score and no use of competitor evidence to alter target SEO or
  AI scores.
- No expansion beyond current capacity unless explicitly modeled and approved.

## Human Gates

- Operator approves demand groups and any `sum_distinct_intents` aggregation.
- Operator confirms business economics and provenance.
- Operator approves all low/base/high acquisition assumptions.
- Paid pilot, deepening, balance recovery, and resume remain explicit gates
  with preflight cost.
- Provider credential, account funding, and billing changes remain external
  user actions.
- Operator approves opportunity scenarios before revenue values enter a pitch
  export.
- Operator approves final outreach package. The product never sends it.
- Automated analytics/CRM connections, deployment, and external writes require
  separate future approval.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `docs/product-revenue-contract.md`
- `docs/seo-insights-platform-architecture.md`
- `.claude/PRPs/plans/P3-REVENUE-ENGINE.plan.md`
- `.claude/PRPs/plans/P6-SEARCH-EVIDENCE-PRODUCTIZATION.plan.md`
- `.claude/PRPs/plans/P8-BJJ-COMPETITIVE-OPPORTUNITY-ENGINE.plan.md`
- `src/models.py`
- `src/repositories/base.py`
- `src/repositories/file_repository.py`
- `src/repositories/sqlite_repository.py`
- `src/services/keyword_set_service.py`
- `src/services/market_evidence_service.py`
- `src/services/gap_analysis_service.py`
- `src/services/market_reporting_service.py`
- `src/services/outreach_service.py`
- `src/services/activation_service.py`
- `src/api/app.py`
- `src/api/static/dashboard.html`
- Relevant market, revenue, API, dashboard, and integrity tests.
- Google Ads Keyword Planner definitions:
  `https://support.google.com/google-ads/answer/3022575`
- Google Ads reach limitations:
  `https://support.google.com/google-ads/answer/2472714`
- GA4 user metric definitions:
  `https://support.google.com/analytics/answer/12253918`

## Execution Path

1. Freeze truth semantics, contracts, formulas, status transitions, and
   migrations.
2. Correct provider failure/completeness semantics and add immutable resume.
3. Add reviewed demand imports and close-variant/intent grouping.
4. Add economics profiles and deterministic capacity-aware opportunity
   scenarios.
5. Add calibration imports and successor forecasts.
6. Assemble opportunity-v1/v4 and pitch packages.
7. Add the URL-first operator experience and complete Nova/Lacey pilot
   validation.

## Patterns To Mirror

- `InsightRun`, `KeywordSet`, `MarketEvidenceRun`, `OutreachPackage`, and
  activation-event immutable attribution.
- SQLite JSON payloads plus indexed operational columns and file artifact
  mirrors.
- Additive migrations and legacy readers.
- Explicit unknown/inapplicable semantics from AI Readiness.
- Paid-call approval and raw artifact persistence from search/market services.
- Successor versions rather than terminal-record mutation.
- Evidence-reference validation at package approval and export.
- Pure deterministic services for grouping, forecasts, and sensitivity.
- Operator dashboard as decision context, with secondary advanced tools.
- Aggregate calibration records; never client-side private financial/lead
  queries.

## Task Slices

### T1: Freeze demand, economics, opportunity, and provider contracts
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `docs/product-revenue-contract.md`, `docs/seo-insights-platform-architecture.md`, `src/models.py`, contract tests
- Acceptance: search-occasion semantics, de-duplication, provider statuses, capacity constraints, formula v1, provenance, forecast labels, versioning, and legacy compatibility are executable typed contracts
- Validate: `python -m pytest tests/test_demand_opportunity_contract.py tests/test_ai_readiness_contract.py -q`
- Evidence: `python -m pytest tests/test_demand_opportunity_contract.py tests/test_ai_readiness_contract.py -q` -> `13 passed in 0.09s`; executable contracts and truth rules added to `src/models.py`, `docs/product-revenue-contract.md`, and `docs/seo-insights-platform-architecture.md`.

### T2: Persist additive opportunity state
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `src/repositories/base.py`, `src/repositories/file_repository.py`, `src/repositories/sqlite_repository.py`, `src/repositories/migrations/006_demand_opportunity.sql`, repository tests
- Acceptance: file and SQLite repositories persist immutable demand sets, economics profiles, scenarios, calibration records, and successor relationships without backfill
- Validate: `python -m pytest tests/test_demand_opportunity_repository.py tests/test_revenue_repository.py tests/test_market_repository.py -q`
- Evidence: `python -m pytest tests/test_demand_opportunity_repository.py tests/test_revenue_repository.py tests/test_market_repository.py -q` -> `6 passed in 0.60s`; parent reviewed migration `006_demand_opportunity.sql`, file/SQLite immutable loaders, successor filters, and scenario forecast-label hydration.

### T3: Make paid market collection resumable and truthful
- Status: complete
- Owner: parent
- Depends on: T1, T2
- Write set: `src/config.py`, `src/dataforseo_client.py`, `src/services/market_evidence_service.py`, `src/services/market_reporting_service.py`, focused provider/recovery tests
- Acceptance: failures are classified; payment/auth failures stop the queue; empty paid results are limited; partial cannot become complete; preflight exposes ceiling/readiness; immutable resume retries only unresolved work and rebuilds downstream market outputs
- Validate: `python -m pytest tests/test_market_recovery.py tests/test_market_evidence.py tests/test_dataforseo_search.py -q`
- Evidence: `python -m pytest tests/test_market_recovery.py tests/test_market_evidence.py tests/test_dataforseo_search.py tests/test_market_api.py -q` -> `24 passed in 3.06s`; payment/auth hard stops, typed failure classes, empty-volume limits, completeness accounting, local cost/readiness preflight, immutable retry-only successor recovery, and recovered comparison/report regeneration are covered.

### T4: Add reviewed demand evidence and de-duplication
- Status: complete
- Owner: implementation_luna
- Depends on: T1, T2
- Write set: `src/services/demand_evidence_service.py`, keyword integration, CSV fixtures, demand tests
- Acceptance: Google Keyword Planner-style CSV preview/commit/review groups close variants and intents deterministically; brand demand is separate; default aggregation cannot inflate the market; operator corrections produce successor versions
- Validate: `python -m pytest tests/test_demand_evidence.py tests/test_keyword_sets.py -q`
- Evidence: `python -m pytest tests/test_demand_evidence.py tests/test_keyword_sets.py -q` -> `11 passed in 0.15s`; parent reviewed bounded CSV safeguards, KPlanner aliases, binding checks, close-variant grouping, max-volume default, brand separation, and immutable review/successor lifecycle.

### T5: Build capacity-aware opportunity scenarios
- Status: complete
- Owner: parent
- Depends on: T1, T2, T4
- Write set: `src/services/opportunity_model_service.py`, `src/vertical_packs.py`, formula fixtures and tests
- Acceptance: exact fixtures produce deterministic low/base/high unique-prospect, funnel, capacity, ramp, MRR, annual run-rate, and sensitivity outputs; incomplete inputs suppress unsupported projections; Nova never exceeds 20 added active members
- Validate: `python -m pytest tests/test_opportunity_model.py tests/test_commercial_findings.py -q`
- Evidence: `python -m pytest tests/test_opportunity_model.py tests/test_commercial_findings.py -q` -> `20 passed in 0.17s`; Nova fixture proves nonbrand demand, explicit organic/Maps overlap, sequential funnel, 20-member clamp, `$2,000` MRR/`$24,000` run-rate ceiling, and `$12,000` 12-month ramp while the trade pack reuses the same four-stage contract.

### T6: Add aggregate calibration and forecast learning
- Status: complete
- Owner: parent
- Depends on: T2, T5
- Write set: `src/services/calibration_service.py`, CSV fixtures, calibration tests
- Acceptance: aggregate campaign/analytics/funnel imports calculate observed conversion metrics without PII and create successor calibrated scenarios while preserving originals
- Validate: `python -m pytest tests/test_opportunity_calibration.py tests/test_revenue_services.py -q`
- Evidence: `python -m pytest tests/test_opportunity_calibration.py tests/test_revenue_services.py -q` -> `9 passed in 2.69s`; bounded aggregate-only CSV validation, no-PII/formula gates, observed funnel/cost metrics, unknown zero denominators, and immutable calibrated successor forecasts are covered.

### T7: Assemble opportunity reports and pitch-safe outreach
- Status: complete
- Owner: parent
- Depends on: T3, T5, T6
- Write set: `src/services/opportunity_reporting_service.py`, `src/services/outreach_service.py`, reporting/outreach tests
- Acceptance: opportunity-v1 and v4 preserve source versions; every value is labeled observed/modeled; revenue stays out of the opener; approved pitch exports revalidate all source snapshots and screenshots
- Validate: `python -m pytest tests/test_opportunity_reporting.py tests/test_market_api.py tests/test_revenue_services.py -q`
- Evidence: `python -m pytest tests/test_opportunity_reporting.py tests/test_market_api.py tests/test_revenue_services.py -q` -> `10 passed in 8.67s`; scenario-scoped immutable `opportunity-v1`/`v4`, observed-versus-modeled labels, pitch-safe v4 briefs, source/hash revalidation, and score/rank/revenue-free cold openers are covered.

### T8: Expose the URL-first operator workflow and pilot
- Status: complete
- Owner: parent
- Depends on: T3, T4, T5, T6, T7
- Write set: `src/api/app.py`, `src/api/static/dashboard.html`, API/UI tests, generated pilot artifacts
- Acceptance: paste URL remains primary; demand/economics/retry/calibration are secondary; Nova and Lacey Glass produce reviewable opportunity cases; provider cost/completeness and capacity constraints render clearly; no unresolved claim can be exported
- Validate: `python -m pytest tests/test_opportunity_api.py tests/test_dashboard_ui.py tests/test_api.py -q`
- Evidence: `python -m pytest tests/test_opportunity_api.py tests/test_dashboard_ui.py tests/test_api.py -q` -> `11 passed in 7.15s`; the URL remains the sole primary launcher, while the secondary workflow covers bound demand preview/commit/approval, business economics, scenario approval, provider recovery, aggregate calibration, v4 retrieval, and pitch-pack creation. Parameterized Nova/Lacey fixtures prove membership and trade economics, capacity clamping, human approval, and blocked pre-approval export.

## Verification

- Golden formula fixtures for every low/base/high input, capacity clamp, ramp,
  retention, overlap, unknown, and inapplicable path.
- Demand tests for Google close variants, synonyms, reordered phrases, category
  boundaries, brand exclusion, unsupported programs, duplicate rows, missing
  volume, provider-grouped values, and operator corrections.
- Provider tests for transient task failures, paid unknowns, HTTP 401/402/429,
  insufficient balance, empty successful payloads, retries, hard stops, cost
  accumulation, evidence reuse, and immutable successors.
- Security tests for CSV size, formulas/cells, malformed numbers, negative
  economics, extreme assumptions, path traversal, raw PII columns, and
  credential redaction.
- Evidence tests proving every observed figure resolves to persisted crawl,
  SERP, Maps, authority, screenshot, or aggregate import evidence.
- Forecast tests proving every modeled figure resolves to an approved
  assumption and formula version.
- Lifecycle tests for draft/review/approved/superseded demand, economics,
  scenarios, calibration, market resume, reports, packages, and activation
  events.
- Compatibility tests for legacy runs, keyword sets, market runs, v1/v2/v3,
  AI reports, outreach packages, and migrations.
- Rendered dashboard tests for desktop/mobile, keyboard operation, partial
  states, empty states, cost preflight, and forecast labeling.
- Nova acceptance:
  `$100` price, `20` capacity, `$2,000` MRR ceiling, `$24,000` annual run-rate,
  explicit ramp, de-duplicated searcher range, complete provenance, and no
  guarantee language.
- Lacey Glass acceptance:
  trade funnel labels and job economics work without BJJ-specific code.
- Full verification:
  - `python -m pytest -q`
  - `python scripts/prp_validate.py .claude/PRPs/plans/P9-DEMAND-TO-REVENUE-OPPORTUNITY-ENGINE.plan.md`
  - `python scripts/agent_tooling_doctor.py`
  - `git diff --check`

## Evidence And Handoff

Planning evidence:

- Nova's completed core run proved the URL-first SEO/AI path.
- The premium market run proved the value of rankings, Maps, competitors,
  authority, and screenshots.
- The same run exposed four product weaknesses: paid volume can return no rows;
  task errors can consume money; payment failure can occur mid-run; terminal
  completeness can be overstated.
- Nova's `$100/month` price and 20-member headroom prove that capacity-aware
  revenue ceilings are more credible than generic traffic-value language.
- Google keyword tools report searches/close variants rather than de-duplicated
  people, so unique-prospect output must remain an explicit model calibrated by
  aggregate first-party outcomes.

Implementation approval: the user explicitly invoked `prp-implement` for this
plan on 2026-07-25. Local code, tests, migrations, and generated local artifacts
are authorized. Paid provider calls, account changes, deployment, commit, push,
and other external writes remain separate human gates.

Implementation verification:

- `python -m pytest -q` -> `224 passed in 46.37s`.
- `python -m compileall -q src tests` -> pass.
- `python scripts/prp_validate.py .claude/PRPs/plans/P9-DEMAND-TO-REVENUE-OPPORTUNITY-ENGINE.plan.md` -> pass.
- `python scripts/agent_tooling_doctor.py` -> all checks pass; SigMap grade A, 100% coverage, high confidence.
- `git diff --check` -> pass; only expected Git line-ending notices were emitted.
- No live paid-provider call or synthetic production demand artifact was
  generated. Nova/Lacey acceptance is covered by deterministic persisted
  fixtures until the operator uploads reviewed demand/economics inputs.
