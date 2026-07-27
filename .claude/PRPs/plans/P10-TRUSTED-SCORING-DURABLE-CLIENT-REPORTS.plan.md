---
id: P10-TRUSTED-SCORING-DURABLE-CLIENT-REPORTS
title: Trusted Scoring, Agentic Analysis, and Durable Client Reports
status: review
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-26
updated: 2026-07-26
---

# Trusted Scoring, Agentic Analysis, and Durable Client Reports

## Summary

Productize the strongest findings from
`docs/research/2026-07-26-product-strength-competitive-research.md` without
turning the Outreach Program into a generic all-in-one audit suite.

The milestone replaces the customer-facing legacy SEO average with a
site-wide, issue-density-based **Technical SEO Health** contract while retaining
the existing `overall_score` for compatibility. It keeps Search Visibility,
Local Visibility, AI Readiness, Observed AI Visibility, Conversion Readiness,
and Evidence Confidence separate and plainly defined. No universal score is
introduced.

It also makes client output reproducible. Every client-facing HTML/PDF/JSON
bundle is generated from immutable report snapshots, copied and hashed assets,
and a manifest that resolves every displayed claim to source evidence. The
existing handcrafted Nova presentation remains a design fixture, not a source
of truth.

Between evidence collection and client rendering, add a provider-neutral
**agentic analysis layer**. A dedicated Hermes worker uses OpenRouter
DeepSeek V4 Flash for routine interpretation and routes only defined exceptions
to an operator-triggered GPT/Codex review. The agent may classify, compare,
prioritize, and draft; it may not recrawl, alter deterministic scores, invent
external search facts, or approve its own claims.

The product motion remains:

**paste URL -> bounded crawl -> concise evidence -> optional approved market
evidence -> validated agentic assessment -> generated client report -> measured
follow-up**

## Intent And Acceptance

### Strategic compact

The research and agent-runtime decision are reduced to six product decisions:

1. Trust comes from attributable evidence, stable formulas, explicit unknowns,
   and immutable history—not from adding more opaque scores.
2. Technical health, visibility, readiness, observed visibility, conversion,
   and evidence confidence answer different questions and must never be
   averaged into one number.
3. A single Tacoma Maps observation is useful evidence but not a service-area
   visibility picture; geographically distributed grids are required for the
   premium local product.
4. A client report is a generated, versioned product artifact. Hand-authored
   decks and mutable canonical report slots are not durable delivery.
5. Cold-prospect evidence stays permissionless and bounded. Owner-authorized
   measurement begins only after engagement and uses aggregate, non-PII data.
6. LLMs interpret an immutable evidence pack; they do not own crawling,
   deterministic scoring, evidence validation, or external-market truth.

### Default operator path

The primary launcher remains one URL field. A standard run performs one bounded
site crawl and returns:

- legacy `overall_score`, preserved but labeled legacy in operator detail;
- Technical SEO Health v2 with family scores, status, completeness, Evidence
  Confidence, affected-page counts, and stable check IDs;
- AI Readiness v3 with AEO/GEO/AIO and core/supporting cohorts;
- Conversion Readiness v1;
- search, local, and observed-AI evidence as unknown until a matching approved
  source exists;
- an optional validated agentic assessment with model, prompt, cost, and source
  provenance;
- three evidence-backed actions;
- a generated client preview sourced from immutable report snapshots.

Paid and owner-authorized layers remain secondary operator actions with
preflight, approval, cost/completeness, and source context.

### Score and evidence stack

| Surface | Customer question | Contract | Headline output |
| --- | --- | --- | --- |
| Technical SEO Health | Can search systems reliably crawl, index, and understand the collected site? | `seo-health.v2` | 0–100 score, families, completeness, confidence |
| Search Visibility | Is the domain visible for approved market demand? | `search-visibility.v2` | tracked coverage, top-3/10/20, weighted visibility, median rank |
| Local Visibility | Where does the business appear across the approved service area? | `local-visibility.v1` | top-3/top-10 grid coverage, median observed rank, heatmap |
| AI Readiness | Is the site ready to be extracted and cited? | `ai-readiness.v3` | 0–100 AEO/GEO/AIO readiness score |
| Observed AI Visibility | Is the business actually mentioned or cited in sampled AI results? | `ai-visibility.v1` | mention/citation/prompt coverage and share of voice |
| Conversion Readiness | Can a qualified visitor find and complete the next action? | `conversion-readiness.v1` | 0–100 score, funnel checks, completeness |
| Evidence Confidence | How much of the intended evidence contract was observed in the right context? | `evidence-confidence.v1` | 0–100 evidence measure and source ledger |

The report must not calculate, display, or imply a universal average across
these surfaces.

### Technical SEO Health v2

Technical health uses all applicable collected, non-utility pages and clearly
labels a capped crawl as collected-site evidence rather than a complete-site
claim.

Initial family weights:

- crawl and indexability: 30%;
- on-page and template quality: 20%;
- architecture and internal links: 20%;
- structured data and local entity: 15%;
- mobile performance and page experience: 15%.

Each executable check records:

- stable `check_id` and `check_version`;
- family, severity, maximum penalty weight, and applicable page classes;
- measured, failed, unknown, or inapplicable status;
- applicable and affected page IDs;
- page-importance-weighted affected ratio;
- evidence confidence and limitations;
- evidence references;
- deterministic remediation;
- whether the check affects the score.

Formula v2:

```text
weighted_affected_ratio =
  sum(page_importance for affected applicable pages)
  / sum(page_importance for all applicable pages)

check_penalty =
  severity_weight
  * weighted_affected_ratio
  * evidence_confidence

family_score =
  100
  - 100 * (
      sum(known check penalties)
      / sum(known applicable severity weights)
    )

Technical SEO Health =
  weighted mean of known applicable family scores
```

Unknown checks are excluded from score arithmetic but remain in completeness.
Inapplicable checks are excluded from both. Evidence below the deterministic
eligibility threshold is unknown, not a low-confidence pass. Scores are
clamped to 0–100 and rounded only at the presentation boundary.

Initial checks cover:

- response, redirect, robots, sitemap, indexability, canonical, and conclusive
  4xx/5xx behavior;
- title, description, H1, duplicate-template, and meaningful-text coverage;
- navigation discovery, internal broken links, crawl depth, sitemap membership,
  and orphan-risk evidence;
- valid visible-content-aligned JSON-LD and consistent business/entity facts;
- mobile viewport plus persisted CrUX/Lighthouse evidence when available.

Unavailable field performance evidence is unknown. It is never inferred from
HTML size or screenshot appearance.

### AI Readiness v3

Retain 40% AEO, 35% GEO, and 25% AIO until outcome calibration supports a new
formula. Replace binary "any item exists" checks with applicability-aware,
continuous measures:

- direct-answer coverage is eligible heading/section coverage, not page
  presence;
- heading quality uses violation density;
- structured answers measure useful blocks relative to eligible sections;
- conversational coverage uses distinct approved intent/follow-up families;
- entity, author, source, and freshness checks apply only to appropriate page
  classes;
- external corroboration uses distinct matching queries/domains and never
  becomes complete from one mention;
- text, link, crawler, and schema checks use affected-page ratios.

FAQPage and HowTo receive no automatic boost. `llms.txt` is recorded as an
observation only and does not affect scoring. AI Readiness never claims actual
AI mentions, citations, rankings, or traffic.

### Conversion Readiness v1

Use deterministic crawl/DOM evidence only:

- offer/program clarity;
- visible next action and CTA destination;
- schedule, pricing, eligibility, and expectation discoverability where
  applicable;
- functional signup/contact destination and form structure without submitting
  the form;
- mobile action accessibility;
- trust/proof and contact-route clarity;
- explicit handoff/follow-up path where visible.

The score measures website readiness, not actual lead quality, attendance,
close rate, CRM performance, or revenue.

### Search, local, and observed-AI visibility

- Search Visibility v2 consumes only an approved keyword set and matching
  market/device/date evidence. It exposes tracked-keyword coverage, top
  positions, demand-weighted visibility when reviewed demand exists, and
  unknown volume when it does not.
- Local Visibility v1 uses an immutable grid definition, approved business/place
  identity, exact coordinates, date, device, language, and provider evidence.
  The teaser is 3x3 over three high-intent terms; premium is 5x5 over five.
- Observed AI Visibility v1 consumes a versioned, operator-approved prompt/topic
  set and matching provider results. It reports observed mentions, citations,
  distinct cited pages, prompt coverage, and competitor share of voice. Sparse,
  unavailable, or mismatched evidence is unknown.
- None of these surfaces changes Technical SEO Health, AI Readiness, or
  Conversion Readiness.

### Agentic analysis layer

Add immutable `SiteEvidencePack`, `AgenticAnalysisJob`, `AgentCallRecord`,
`AgenticAssessmentSnapshot`, and append-only
`AgenticAssessmentReviewEvent` contracts behind a provider-neutral
`AgenticAnalysisRuntime` Protocol.

`SiteEvidencePack` is generated only from already-persisted Outreach artifacts.
It contains:

- run, attempt, report-snapshot, vertical-pack, keyword-set, market-run, and
  scenario identities and hashes;
- normalized target/business facts and explicit provenance;
- bounded page facts and excerpts with stable evidence references;
- deterministic health/readiness/conversion results;
- approved organic, Maps, authority, competitor, screenshot, demand, and
  economics evidence when present;
- permitted service-package mappings;
- collection completeness and evidence limitations.

It excludes raw credentials, cookies, owner analytics unless separately
authorized, arbitrary filesystem paths, scripts, and instructions embedded in
website content. Website text is untrusted data and can never change the
system/rubric/tool policy.

`AgenticAnalysisJob` states are `queued`, `packing`, `running`, `validating`,
`needs_review`, `complete`, `partial`, `failed`, and `superseded`. The
idempotency key is derived from the evidence-pack hash, vertical/rubric/prompt
versions, requested model route, and analysis mode. Retrying transient provider
failures creates an attributable call attempt; authentication, payment,
validation, budget, or policy failures stop immediately.

`AgentCallRecord` persists requested and served model/provider, routing mode,
prompt/rubric version, attempt, status/failure class, input/output/reasoning
tokens, actual or estimated cost, latency, raw response reference, and start/end
times. Provider fallbacks may not silently change an assessment: any served
model/provider change is recorded and either creates a new assessment execution
or requires review.

`AgenticAssessmentSnapshot` contains:

- evidence-pack/source hashes;
- runtime, requested/served model, provider, prompt, rubric, and schema
  versions;
- candidate findings classified as `observed`, `inference`, or
  `recommendation`;
- evidence references, confidence, severity, commercial relevance, service
  fit, customer-safety status, and review reason per finding;
- contradictions, limitations, model cost/latency summary, validation result,
  predecessor, and creation time.

The four fixed passes are:

1. evidence analyst;
2. vertical strategist;
3. recommendation prioritizer;
4. client editor.

Each pass consumes the same immutable evidence pack plus prior validated
structured output; it does not share unconstrained conversational memory. A
deterministic validator resolves every reference, checks claim type and
business-fact provenance, enforces vertical service mappings, rejects
prompt-injection effects, and strips unsupported customer-facing claims.

The default routine route is a dedicated, stateless Hermes
`outreach-analysis` profile using OpenRouter
`deepseek/deepseek-v4-flash`. The profile has no persistent learning/memory,
messaging integration, autonomous browser, network, shell, or unrestricted
filesystem tools. OpenRouter routing requires structured-output support and a
no-data-collection/ZDR-compatible endpoint; the served provider metadata is
persisted. Initial job caps are four model calls, bounded evidence-pack/output
tokens, two transient retries per call, and `$0.10` total inference.

Runtime configuration is additive and disabled by default:

- `AGENTIC_ANALYSIS_ENABLED`;
- runtime/provider/model/profile and pinned Hermes executable/version;
- evidence-pack, output-token, call, cost, timeout, and retry ceilings;
- OpenRouter provider allow/order, required-parameter, and data-policy rules;
- `ALLOW_CODEX_REVIEW`, false by default;
- artifact root and read-only MCP job scope.

Credentials remain in the existing secret-loading boundary. Run/config
snapshots record only booleans, policy/version identifiers, and sanitized model
routes—never API keys, OAuth material, environment dumps, or personal Hermes
paths.

Hermes is an adapter, not the product boundary:

```text
AgenticAnalysisRuntime
  HermesOpenRouterRuntime       # routine structured analysis
  DirectOpenRouterRuntime       # controlled operational fallback
  CodexReviewRuntime            # operator-triggered exception review
```

GPT through the existing Hermes OpenAI Codex subscription is permitted only
for operator-triggered review during this milestone. Unattended GPT review
requires a separately approved metered API route; production completion may not
depend on personal subscription allowance.

Escalation to GPT/human review occurs only for material contradictions,
unresolved references, identity/credential/lineage/pricing/capacity claims,
invalid service mapping, customer-safe completeness failure, material
recommendation instability, or an operator-designated premium target. GPT
reviews the evidence pack and candidate assessment; it does not recrawl.

Human acceptance, rejection, correction, or escalation is recorded as an
append-only review event; assessment payloads are never edited. Derived review
state is `unreviewed`, `needs_review`, `approved`, or `rejected`. Corrections
carry a reason code and may create a successor prompt/rubric/evidence-pack
execution for evaluation.

Public interfaces:

- `POST /api/runs/{run_id}/agentic-analysis/preflight`;
- `POST /api/runs/{run_id}/agentic-analysis` returning `202` and a durable job;
- `GET /api/agentic-analysis/jobs/{job_id}`;
- `POST /api/agentic-analysis/jobs/{job_id}/retry`;
- `GET /api/runs/{run_id}/agentic-assessments`;
- `POST /api/agentic-assessments/{assessment_id}/review-events`;
- `POST /api/agentic-assessments/{assessment_id}/request-gpt-review`;
- `GET /api/agentic-analysis/evaluations/summary`.

Only the preflight and read endpoints are safe by default. Starting inference,
retrying spend, using GPT/Codex, and approving customer-facing findings require
the existing authenticated operator boundary and the corresponding human gate.

Agent output never changes deterministic SEO, AI, search, local, conversion,
authority, demand, or opportunity scores. It may prioritize already-supported
actions and draft copy only after validation.

### Immutable reporting and portability

Add immutable `ReportSnapshot`, mutable `ReportAlias`, and immutable
`ClientReportBundle` contracts.

`ReportSnapshot` includes:

- ID, run ID, attempt ID, report contract and schema version;
- source snapshot IDs and hashes;
- renderer version;
- payload SHA-256 and manifest SHA-256;
- completeness/status;
- created timestamp and immutable payload/artifact references.

`ReportAlias` points a convenient `(run, report_contract, alias)` such as
`latest` to one immutable snapshot. Moving an alias never changes a snapshot.

The bundle layout is:

```text
bundles/<bundle_id>/
  manifest.json
  report.html
  report.pdf
  data/report.json
  assets/<sha256>.<ext>
  hashes.sha256
```

The manifest contains report/renderer/theme versions, source IDs/hashes,
artifact hashes, collection dates/markets/devices, access state, completeness,
and limitations. The renderer copies only validated in-scope artifacts,
references canonical evidence once, emits no secret-bearing configuration, and
requires every displayed factual or modeled claim to resolve through the
manifest.

### Temporal proof and measurement

Add immutable comparison snapshots that align stable check IDs, normalized page
identities, keyword targets, grid points, prompt topics, and funnel metrics.
Comparisons report introduced, resolved, persisting, changed, and unknown due to
incomparable context. Numeric deltas are suppressed when formula versions,
markets, devices, grid definitions, or sampling contracts are incompatible.

Owner-authorized measurement uses aggregate `OwnedMeasurementSnapshot`
contracts for Search Console, GBP Performance, GA4, CRM, and future supported
AI-performance exports. CSV import is the required baseline. Live read-only
connectors are adapters behind explicit credentials and approval gates; raw
emails, phone numbers, names, query-level personal data, and autonomous external
writes are prohibited.

### Milestone acceptance

- Every new client-facing score has a documented formula, stable version,
  applicable scope, completeness, and Evidence Confidence.
- Legacy `overall_score`, v1/v2/v3/v4, ai-v1/ai-v2, market-v1,
  opportunity-v1, checkpoints, outreach packages, and old runs remain readable
  without backfill or silent recomputation.
- New pipeline contract v4 retains the legacy `scoring` output and adds
  `scoring_technical_health` and `scoring_conversion_readiness`; validation
  continues to accept legacy six-stage and v3 seven-stage runs.
- Standard URL runs fetch each normalized internal URL at most once in the core
  crawl. Optional screenshot/performance/provider collections are separate,
  capped evidence operations and are labeled as such.
- Agentic analysis consumes only a hashed `SiteEvidencePack`; it cannot fetch,
  browse, execute site instructions, or change deterministic score artifacts.
- Every agent call records prompt/rubric/schema, requested and served
  model/provider, tokens, cost, latency, retry/failure, and raw artifact
  provenance.
- Every completed agentic assessment is schema-valid, resolves all
  customer-safe claims deterministically, and preserves unsupported candidates
  only as rejected/review evidence.
- DeepSeek is not enabled as the routine route until the golden set proves 100%
  final schema validity, zero unsupported exports, at least 98% draft
  evidence-reference precision, at least 85% human service-fit agreement, at
  least 80% top-three recommendation overlap across repeat runs, under 10%
  correction rate, under 20% GPT escalation, and under `$0.10` inference per
  site.
- Subscription-backed GPT/Codex review remains human-triggered; unattended
  jobs require a separately approved metered API credential and budget.
- Every client claim and asset resolves to an immutable report manifest entry.
- Saving a different payload to an existing report-snapshot ID fails; canonical
  aliases may move without mutating history.
- A client HTML/PDF/JSON bundle is generated with no manual HTML editing and
  remains readable when copied away from the workspace.
- Local premium evidence represents more than one geographic point and exposes
  grid completeness and provider cost.
- AI Readiness and Observed AI Visibility are always separate.
- Comparisons never show a numeric delta across incompatible contract/context
  versions.
- Owner-authorized aggregate baselines can connect impressions to actions and
  downstream outcomes without importing lead PII.
- Median operator review time remains below 10 minutes in the Nova and Lacey
  Glass pilot.
- Unsupported-claim and factual-correction rates remain zero in acceptance
  fixtures and are recorded for future calibration.

## Scope

### Release A — credibility and repeatability

- Technical SEO Health v2 and Evidence Confidence v1.
- Immutable report snapshots, aliases, and portable client bundles.
- Provider-neutral agentic job/evidence/assessment contracts, a restricted
  Hermes DeepSeek runtime, deterministic claim validation, and golden-set
  evaluation.
- Generated BJJ, trades, client, and operator presentation themes.
- Search Visibility v2 and 3x3 Maps-grid evidence.
- Immutable technical/search/local comparison snapshots.

### Release B — stronger market proof

- AI Readiness v3.
- Conversion Readiness v1.
- Optional Observed AI Visibility v1.
- Premium 5x5 Maps grids and competitor local-share evidence.
- Owner-authorized aggregate measurement snapshots and CSV imports.
- Read-only live connector interfaces behind separate credential gates.

### Release C — calibration and moat

- Outcome-linked recommendation-priority calibration.
- Internal vertical distributions and confidence intervals.
- Published benchmark language only after a separately approved
  minimum-sample policy.
- Nova Ryu and Lacey Glass pilot bundles and review-time/correction evidence.

## Not Building

- One universal SEO/AI/visibility/revenue score.
- A Google Domain Authority or exposed Google PageRank claim.
- Actual ranking, citation, traffic, lead, or revenue guarantees.
- An `llms.txt` score or automatic FAQPage/HowTo boost.
- LLM judges in Technical SEO Health, AI Readiness, Conversion Readiness, or
  evidence validation.
- Agent-generated numeric site-health, ranking, authority, demand, conversion,
  or revenue scores.
- Letting Hermes or an LLM recrawl a target, query search engines independently,
  submit forms, contact prospects, follow embedded site instructions, or access
  unrestricted shell/browser/network tools during analysis.
- Persistent Hermes memory/learning, personal profile state, messaging
  integrations, or silent model/provider fallback in assessment jobs.
- A production dependency on a personal ChatGPT/Codex subscription allowance.
- Treating GPT, DeepSeek, or another model as the evaluation ground truth;
  reviewed evidence fixtures and human decisions remain authoritative.
- Historical score backfill or silent recomputation.
- Autonomous outreach, email sending, content publishing, backlink work, form
  submission, or competitor contact.
- Raw lead PII ingestion, CRM replacement, billing, multi-tenancy, or customer
  self-service account management.
- Unapproved paid provider calls or unapproved OAuth/account access.
- Stable public hosting, custom domains, or production deployment in this PRP;
  the bundle and access contracts are built locally first.
- Scraping third-party mention pages or following competitor external links.

## Human Gates

- The parent presents this PRP for approval before implementation.
- The operator approves customer-facing Technical SEO Health and Conversion
  Readiness labels, weights, severity registry, and AI Readiness v3 before they
  replace current presentation defaults.
- Every DataForSEO Maps-grid or AI-visibility collection requires a preflight
  with planned calls, conservative ceiling, reusable evidence, and explicit paid
  approval.
- Grid center, radius/spacing, business/place identity, keyword set, and prompt
  set require operator approval before collection.
- The operator approves the agentic rubric, prompt/schema versions, golden
  fixtures, model route, OpenRouter privacy/provider policy, per-job token/call
  budget, and promotion results before DeepSeek becomes routine.
- Creating or changing the dedicated Hermes profile, storing OpenRouter/OpenAI
  credentials, enabling a fallback provider, or using GPT/Codex subscription
  access is a separate operator action. No existing personal Hermes profile is
  reused by the product.
- A job may enter GPT review automatically only after a metered GPT API route
  and budget are separately approved. Until then, GPT/Codex escalation requires
  an operator click.
- Material prompt, rubric, evidence-pack, model, provider-policy, or output
  schema changes create new versions and require regression evaluation; they
  never silently reinterpret stored assessments.
- Owner measurement access requires proof of authorization, separate
  credentials, read-only scopes, and explicit approval. Credentials and refresh
  tokens never enter report artifacts.
- Applying production database migrations, enabling live connectors,
  publishing a client bundle, creating a stable share URL, or deploying remains
  a separate protected action.
- Customer-facing vertical benchmarks remain disabled until the operator
  approves a minimum-sample, recency, and confidence policy.
- Historical regeneration is opt-in and creates new snapshots; it never
  replaces old artifacts.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `docs/research/2026-07-26-product-strength-competitive-research.md`
- `docs/seo-insights-platform-architecture.md`
- `docs/seo-ingestion-pipeline-spec.md`
- `docs/product-revenue-contract.md`
- `.context/query-context.md`
- `.agents/skills/prp-plan/SKILL.md`
- `C:/Users/Snipe/.codex/skills/backend-patterns/SKILL.md`
- `C:/Users/Snipe/.codex/skills/frontend-patterns/SKILL.md`
- [Hermes CLI and provider configuration](https://github.com/nousresearch/hermes-agent/blob/main/website/docs/reference/cli-commands.md)
- [Hermes profiles](https://github.com/nousresearch/hermes-agent/blob/main/website/docs/user-guide/profiles.md)
- [Hermes fallback behavior](https://github.com/nousresearch/hermes-agent/blob/main/website/docs/user-guide/features/fallback-providers.md)
- [OpenRouter structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs)
- [OpenRouter provider and privacy routing](https://openrouter.ai/docs/guides/routing/provider-selection)
- [OpenRouter routing metadata](https://openrouter.ai/docs/guides/features/router-metadata)
- [DeepSeek V4 API contract](https://api-docs.deepseek.com/updates/)
- [OpenAI Codex authentication](https://developers.openai.com/codex/auth)
- `src/models.py`
- `src/config.py`
- `src/pipeline.py`
- `src/orchestrator.py`
- `src/services/reporting_service.py`
- `src/services/ai_readiness_service.py`
- `src/services/page_analysis_service.py`
- `src/services/provenance_service.py`
- `src/services/market_evidence_service.py`
- `src/services/market_reporting_service.py`
- `src/services/opportunity_reporting_service.py`
- `src/services/outreach_service.py`
- `src/services/screenshot_service.py`
- `src/dataforseo_client.py`
- `src/repositories/base.py`
- `src/repositories/file_repository.py`
- `src/repositories/sqlite_repository.py`
- `src/repositories/migrations/001_initial.sql`
- `src/repositories/migrations/002_stage_checkpoints.sql`
- `src/repositories/migrations/006_demand_opportunity.sql`
- `src/api/app.py`
- `src/api/static/dashboard.html`
- `tests/test_scorecard_semantics.py`
- `tests/test_ai_readiness_contract.py`
- `tests/test_integrity_regressions.py`
- `tests/test_market_evidence.py`
- `tests/test_market_recovery.py`
- `tests/test_market_api.py`
- `tests/test_opportunity_reporting.py`
- `tests/test_run_diff.py`
- `tests/test_dashboard_ui.py`

## Execution Path

1. Freeze product language, score mathematics, stable check registries,
   applicability, source context, comparison compatibility, and snapshot
   contracts before modifying services.
2. Build and golden-test Technical SEO Health, AI Readiness v3, Conversion
   Readiness, and Evidence Confidence as independent deterministic services.
3. Add immutable snapshot/alias/bundle persistence before routing any new client
   output through the renderer.
4. Persist immutable site-evidence packs, agent jobs/calls/assessments, and a
   provider-neutral runtime contract with prompt-injection and budget policy.
5. Configure a dedicated stateless Hermes test profile, implement the
   OpenRouter DeepSeek route, deterministic claim validator, explicit
   GPT/Codex review path, and golden-set evaluation. Do not promote the routine
   route until its gates pass.
6. Build the self-contained client renderer from snapshot and validated
   assessment references and
   content-addressed assets.
7. Add Search Visibility v2 and Local Visibility grids by extending existing
   approved market evidence and provider reliability contracts.
8. Add Observed AI Visibility as an optional paid child lifecycle with its own
   prompt set, completeness, and raw artifacts.
9. Replace the shallow run diff with immutable, context-aware comparison
   snapshots.
10. Add aggregate owner-measurement imports and read-only connector interfaces;
   do not enable live credentials by default.
11. Integrate URL-first API/dashboard/client views, agent job/review/cost
    surfaces, and outreach revalidation.
12. Run Nova Ryu and Lacey Glass fixtures, compare DeepSeek and GPT against
    human-reviewed outputs, measure review time/correction/escalation/cost, and
    calibrate recommendation ordering without rewriting formulas or
    historical outputs.

Task dependencies define implementation order. Release A, B, and C are
independent operator rollout gates; completing code does not enable models,
credentials, paid calls, benchmarks, publishing, or deployment.

## Patterns To Mirror

- Mirror `AIReadinessService` unknown/inapplicable/completeness behavior; do not
  copy its current binary page-ratio thresholds.
- Mirror attempt-scoped `StageCheckpoint` hashing and provenance validation.
- Mirror `_save_immutable_payload` in the file and SQLite repositories for
  write-once snapshot IDs.
- Mirror `MarketEvidenceRun` provider-call records, preflight, hard stops,
  partial state, immutable resume, and actual-cost accounting.
- Mirror `ProviderCallRecord` failure classes and immutable cost attribution for
  `AgentCallRecord`; retry only transient capacity/network failures.
- Mirror the repository Protocol/service separation for a provider-neutral
  `AgenticAnalysisRuntime`; no API route calls Hermes/OpenRouter directly.
- Use a dedicated Hermes profile to isolate model configuration, sessions,
  skills, memory, scheduled jobs, and credentials from personal agent state.
  Assessment execution is stateless and uses a versioned Outreach analysis
  skill plus structured output only.
- Treat model output as untrusted input: schema-validate it, resolve evidence
  references in ordinary code, reject unapproved business facts/service
  mappings, and persist rejected claims for audit without rendering them.
- Keep model routing explicit and attributable. A fallback model/provider is a
  new recorded execution, not an invisible continuation of a scored job.
- Mirror market-run-scoped artifacts in `MarketReportingService`, while
  replacing mutable canonical report persistence for all new contracts.
- Mirror scenario/source hashing and predecessor attribution in
  `OpportunityReportingService`.
- Mirror `ScreenshotService` host restrictions, pinned Playwright/Chromium
  checks, viewport metadata, and failure-as-limit behavior.
- Mirror `OutreachService` approval/export evidence revalidation.
- Preserve the API key dependency, bounded CSV parsing, SSRF protections,
  redirect-host checks, content-size limits, and URL normalization already used
  by crawl and market services.
- Keep the dashboard's single URL launcher as the primary action; all paid,
  agentic, connector, comparison, and evidence-expansion controls remain under
  operator tools. Agent status, cost, validation, escalation reason, and
  accepted/rejected findings must remain accessible without hover.

## Task Slices

### T1: Freeze scoring, snapshot, agentic, and comparison contracts
- Status: completed
- Owner: parent
- Depends on: none
- Write set: `docs/product-strength-contract.md`, `docs/agentic-analysis-contract.md`, `docs/seo-insights-platform-architecture.md`, `docs/AGENT_START_HERE.md`, `src/models.py`, contract fixtures and tests
- Acceptance: all seven product surfaces, formula/version constants, stable check registries, applicability, unknown/inapplicable semantics, Evidence Confidence, immutable snapshot/alias/bundle models, SiteEvidencePack/job/call/assessment lifecycle and schemas, append-only assessment review events and derived state, model/prompt/rubric identity, grid/prompt/measurement identities, comparison compatibility, and legacy-read rules are executable contracts
- Validate: `python -m pytest tests/test_product_strength_contract.py tests/test_agentic_analysis_contract.py tests/test_ai_readiness_contract.py tests/test_demand_opportunity_contract.py -q`
- Evidence: `python -m pytest tests/test_product_strength_contract.py tests/test_agentic_analysis_contract.py tests/test_ai_readiness_contract.py tests/test_demand_opportunity_contract.py -q` -> `26 passed`; contracts are documented in `docs/product-strength-contract.md` and `docs/agentic-analysis-contract.md`, with executable constants/models in `src/models.py`.

### T2: Implement Technical SEO Health v2 and evidence confidence
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: `src/services/technical_seo_health_service.py`, `src/services/performance_evidence_service.py`, `src/services/page_analysis_service.py`, `src/services/reporting_service.py`, `src/pipeline.py`, focused scoring/crawl tests
- Acceptance: all applicable collected pages produce deterministic issue-density family scores, affected-page evidence, stable remediation, capped-crawl language, optional persisted performance evidence, and confidence without changing legacy `overall_score`
- Validate: `python -m pytest tests/test_technical_seo_health.py tests/test_scorecard_semantics.py tests/test_single_crawl.py tests/test_integrity_regressions.py -q`
- Evidence: `python -m pytest tests/test_technical_seo_health.py tests/test_scorecard_semantics.py tests/test_single_crawl.py tests/test_integrity_regressions.py -q` -> `48 passed`; `python -m pytest tests/test_orchestration.py tests/test_phase_a_integrity.py -q` -> `33 passed`. Added `src/fetchers/page_fetcher.py` viewport evidence and `src/orchestrator.py` v3/v4 validation compatibility as directly required integration seams.

### T3: Strengthen AI Readiness to v3
- Status: completed
- Owner: parent
- Depends on: T1, T2
- Write set: `src/services/ai_readiness_service.py`, `src/services/reporting_service.py`, AI golden fixtures and tests
- Acceptance: continuous applicability-aware AEO/GEO/AIO checks preserve 40/35/25 and cohort semantics, prevent one-result corroboration completion, exclude `llms.txt`/FAQ/HowTo boosts, resolve every check to evidence, and leave ai-v1/ai-v2 readable
- Validate: `python -m pytest tests/test_ai_readiness_v3.py tests/test_ai_readiness_scoring.py tests/test_ai_readiness_contract.py tests/test_ai_evidence_refs.py -q`
- Evidence: `python -m pytest tests/test_ai_readiness_v3.py tests/test_ai_readiness_scoring.py tests/test_ai_readiness_contract.py tests/test_ai_evidence_refs.py -q` -> `14 passed`; `python -m pytest tests/test_orchestration.py tests/test_phase_a_integrity.py -q` -> `33 passed`. New runs emit `ai-v3`; legacy `ai-v1`/`ai-v2` readers and the v2 scoring service remain intact.

### T4: Add deterministic Conversion Readiness v1
- Status: completed
- Owner: implementation_luna
- Depends on: T1, T2
- Write set: `src/services/conversion_readiness_service.py`, bounded DOM evidence additions, vertical applicability rules, focused tests
- Acceptance: BJJ and trades produce deterministic, vertical-aware offer/action/signup/contact/mobile/trust checks without submitting forms or inferring actual funnel performance; unknown evidence cannot become a failure or sales claim
- Validate: `python -m pytest tests/test_conversion_readiness.py tests/test_ai_page_evidence.py tests/test_commercial_findings.py -q`
- Evidence: parent-reviewed `conversion-dom-evidence.v1` parser and vertical-aware deterministic service with resolvable page refs; `python -m pytest tests/test_conversion_readiness.py tests/test_ai_page_evidence.py tests/test_commercial_findings.py -q` -> `23 passed`; crawl/technical parser regressions -> `8 passed`.

### T5: Add immutable report snapshots and aliases
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- Write set: `src/repositories/base.py`, `src/repositories/file_repository.py`, `src/repositories/sqlite_repository.py`, `src/repositories/migrations/007_report_snapshots.sql`, snapshot repository tests
- Acceptance: file and SQLite implementations persist write-once report snapshots and bundles, allow separately mutable aliases, reject same-ID content changes, expose latest/history queries, and leave `InsightReport` legacy readers untouched
- Validate: `python -m pytest tests/test_report_snapshot_repository.py tests/test_phase_a_integrity.py tests/test_demand_opportunity_repository.py -q`
- Evidence: parent-reviewed file and SQLite write-once implementations plus alias-scope and bundle-scope validation; `python -m pytest tests/test_report_snapshot_repository.py tests/test_phase_a_integrity.py tests/test_demand_opportunity_repository.py tests/test_sqlite_repository.py -q` -> `13 passed`.

### T6: Persist the agentic job lifecycle and runtime policy
- Status: completed
- Owner: implementation_luna
- Depends on: T1, T5
- Write set: `src/config.py`, `src/repositories/base.py`, `src/repositories/file_repository.py`, `src/repositories/sqlite_repository.py`, `src/repositories/migrations/008_agentic_analysis.sql`, `src/services/agentic_job_service.py`, repository/job tests
- Acceptance: file and SQLite stores persist immutable evidence packs, call records, assessment snapshots, predecessor/supersession, append-only review events, derived review state, and durable leased jobs; idempotency prevents duplicate spend; token/call/cost/time budgets, retry classes, exact runtime/model policy, and credential redaction are enforced without changing report or run records
- Validate: `python -m pytest tests/test_agentic_analysis_repository.py tests/test_agentic_job_service.py tests/test_report_snapshot_repository.py tests/test_revenue_repository.py -q`
- Evidence: parent-reviewed disabled-by-default runtime policy, immutable file/SQLite lifecycle stores, additive migration `008_agentic_analysis.sql`, and budget/lease/idempotency controls; `python -m pytest tests/test_agentic_analysis_repository.py tests/test_agentic_job_service.py tests/test_report_snapshot_repository.py tests/test_revenue_repository.py -q` -> `9 passed`; orchestration/phase compatibility -> `33 passed`.

### T7: Implement restricted Hermes analysis, validation, and evaluation
- Status: completed
- Owner: parent
- Depends on: T1, T2, T3, T4, T5, T6
- Write set: `src/services/agentic_analysis_service.py`, `src/services/agentic_runtime.py`, `src/services/hermes_runtime.py`, `src/services/agentic_validation_service.py`, `src/services/agentic_evaluation_service.py`, `scripts/outreach_evidence_mcp.py`, `scripts/run_agentic_analysis.py`, `config/hermes/outreach-analysis/`, versioned prompts/rubrics, golden fixtures and tests
- Acceptance: the app generates a bounded hashed evidence pack; a dedicated stateless Hermes one-shot worker using OpenRouter DeepSeek V4 Flash can retrieve only that job through a scoped read-only local MCP tool; four structured passes record usage/routing; ordinary code rejects invalid refs, prompt injection, unsupported facts, and service mappings; transient retries are bounded; provider/model changes are explicit successors; Codex review is operator-triggered; DirectOpenRouterRuntime is available as a controlled adapter; no deterministic score changes; the routine route remains disabled until all promotion gates pass
- Validate: `python -m pytest tests/test_agentic_analysis_runtime.py tests/test_agentic_validation.py tests/test_agentic_prompt_injection.py tests/test_agentic_evaluation.py tests/test_market_security.py -q`
- Evidence: parent-owned scoped evidence packing, four-pass provider-neutral runtime, pinned Hermes one-shot adapter, DirectOpenRouter/Codex review boundaries, deterministic validation, prompt-injection rejection, and offline promotion metrics; routine execution additionally requires the disabled-by-default promotion gate. `python -m pytest tests/test_agentic_analysis_runtime.py tests/test_agentic_validation.py tests/test_agentic_prompt_injection.py tests/test_agentic_evaluation.py tests/test_market_security.py -q` -> `8 passed`; MCP/runner help and Python compilation succeeded. No provider call, profile install, credential mutation, or deterministic score mutation occurred.

### T8: Generate portable client HTML, PDF, JSON, and manifest bundles
- Status: completed
- Owner: implementation_luna
- Depends on: T2, T5, T7
- Write set: `src/services/client_report_service.py`, `src/services/report_manifest_service.py`, versioned renderer/templates/themes, bundle fixtures and tests
- Acceptance: one snapshot graph plus only validated customer-safe assessment findings deterministically generates the three-layer owner brief/evidence/methodology experience, content-addressed copied assets, offline HTML, PDF, JSON, manifest, model disclosure, and hashes without duplicated canonical evidence or manual HTML edits; reports still render when agentic analysis is unknown or needs review
- Validate: `python -m pytest tests/test_client_report_bundle.py tests/test_report_manifest.py tests/test_agentic_validation.py tests/test_screenshot_service.py -q`
- Evidence: `ClientReportService` and `ReportManifestService` render content-addressed offline HTML, JSON, and PDF bundles with immutable snapshot identity, three disclosure layers, model/runtime disclosure, manifest/hash verification, and bounded asset copying. Parent review hardened bundle identity against assessment variants, blocked artifact-root escape, structurally and independently revalidated every customer-safe agent finding, copied its JSON proof into the portable manifest, and attached snapshot proof to headline/summary claims. Exact validation: `python -m pytest tests/test_client_report_bundle.py tests/test_report_manifest.py tests/test_agentic_validation.py tests/test_screenshot_service.py -q` -> `5 passed`; expanded compatibility/security validation -> `15 passed`.

### T9: Add Search Visibility v2 and geographically distributed Local Visibility
- Status: completed
- Owner: implementation_luna
- Depends on: T1, T5
- Write set: `src/dataforseo_client.py`, `src/services/search_visibility_service.py`, `src/services/local_visibility_service.py`, `src/services/market_evidence_service.py`, `src/services/market_reporting_service.py`, provider/grid tests
- Acceptance: approved demand produces context-bound organic visibility metrics; approved 3x3/5x5 grids use deterministic coordinates and place identity, enforce 27/125-call preflight ceilings, reuse only exact matching evidence, persist heatmap cells/cost/completeness, and never alter health/readiness scores
- Validate: `python -m pytest tests/test_search_visibility_v2.py tests/test_local_visibility_grid.py tests/test_market_evidence.py tests/test_market_recovery.py tests/test_dataforseo_search.py -q`
- Evidence: parent-reviewed approved-demand visibility, strict market/device/date context, target-domain matching, and deterministic coordinate-bound 3x3/5x5 grids with exact reuse, call ceilings, cost, heatmap, and completeness. `python -m pytest tests/test_search_visibility_v2.py tests/test_local_visibility_grid.py tests/test_market_evidence.py tests/test_market_recovery.py tests/test_dataforseo_search.py -q` -> `29 passed`; no provider calls were made.

### T10: Add optional Observed AI Visibility v1
- Status: completed
- Owner: parent
- Depends on: T1, T5, T9
- Write set: `src/dataforseo_client.py`, `src/services/ai_visibility_service.py`, provider artifacts, focused tests
- Acceptance: an approved versioned prompt/topic set produces attributable mention, citation, distinct-page, coverage, and share-of-voice evidence within a paid preflight/call cap; sparse or unavailable evidence is unknown and never changes AI Readiness
- Validate: `python -m pytest tests/test_ai_visibility.py tests/test_dataforseo_search.py tests/test_ai_readiness_v3.py -q`
- Evidence: `AIVisibilityService` consumes only approved, versioned prompt/topic sets and exact market/location/language/device/date evidence to produce attributable mention, citation, distinct-page, coverage, share-of-voice, cost, and raw-artifact metrics; it has no score and cannot change AI Readiness. The DataForSEO adapter preserves raw/cost/context evidence behind a pure paid preflight and 20-call ceiling. Parent review changed collection to deny paid access by default, required exact topic-set version/context for reuse, required target identity for an observed result, and canonicalized target page identities. Exact validation: `python -m pytest tests/test_ai_visibility.py tests/test_dataforseo_search.py tests/test_ai_readiness_v3.py -q` -> `24 passed`; no provider calls were made.

### T11: Replace shallow run diff with immutable comparison snapshots
- Status: completed
- Owner: implementation_luna
- Depends on: T2, T3, T4, T5, T7, T9
- Write set: `src/services/report_comparison_service.py`, `src/orchestrator.py`, comparison fixtures and tests
- Acceptance: same-target snapshots align stable checks/pages/keywords/grid cells/prompts and separately versioned validated agent recommendations, report introduced/resolved/persisting/unknown changes, suppress incompatible numeric deltas or model/rubric comparisons, retain the legacy diff response, and persist comparison-v1 with source IDs/hashes
- Validate: `python -m pytest tests/test_report_comparison_v2.py tests/test_run_diff.py tests/test_integrity_regressions.py -q`
- Evidence: `ReportComparisonService` aligns stable checks, normalized pages, versioned keyword/grid/prompt evidence, and validated agent recommendations; it classifies introduced/resolved/persisting/unknown state and suppresses numeric/model comparisons when identities are missing or incompatible. The legacy diff envelope remains intact while adding `comparison_snapshot`. Parent review added write-once file/SQLite persistence through additive migration `010_report_comparisons.sql`, required validated customer-safe assessment state, rejected label-only evidence reuse without a version identity, and normalized target domains. Exact validation: `python -m pytest tests/test_report_comparison_v2.py tests/test_run_diff.py tests/test_integrity_regressions.py -q` -> `30 passed`.

### T12: Add owner-authorized aggregate measurement snapshots
- Status: completed
- Owner: parent
- Depends on: T1, T5
- Write set: `src/services/owned_measurement_service.py`, `src/repositories/base.py`, file/SQLite repositories, `src/repositories/migrations/009_owned_measurements.sql`, bounded CSV adapters, connector protocols and tests
- Acceptance: GSC/GBP/GA4/CRM-style aggregate imports validate context and provenance, reject PII, preserve immutable source snapshots, derive cross-source funnel baselines, and create calibrated successors; live connectors are read-only, disabled by default, and cannot expose credentials
- Validate: `python -m pytest tests/test_owned_measurement.py tests/test_opportunity_calibration.py tests/test_revenue_repository.py -q`
- Evidence: `OwnedMeasurementService` now performs bounded, aggregate-only GSC/GBP/GA4/CRM/AI-performance CSV preview and commit with immutable source hashes, row provenance, PII/formula/credential rejection, deterministic IDs, cross-source funnel deduplication, shared-context preservation, and calibrated opportunity successors. File and SQLite repositories implement the contract through additive migration `009_owned_measurements.sql`; live connector adapters are read-only, approval-gated, and disabled by default. Parent review added mixed-prospect rejection and recursive sensitive-context validation. Exact validation: `python -m pytest tests/test_owned_measurement.py tests/test_opportunity_calibration.py tests/test_revenue_repository.py -q` -> `13 passed`.

### T13: Expose URL-first operator, agent-review, and client experiences
- Status: completed
- Owner: parent
- Depends on: T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12
- Write set: `src/api/app.py`, `src/api/static/dashboard.html`, `src/services/outreach_service.py`, API/UI/export tests
- Acceptance: URL paste remains primary; starting agent analysis is a secondary action returning 202; durable job status, exact model/provider/cost, validation result, contradictions, escalation reasons, accepted/rejected findings, GPT-review button, score stack, confidence, heatmap, readiness-versus-visibility, comparisons, evidence drawers, client/operator views, bundle history/download, paid preflight, and owner imports are accessible; package approval/export revalidates snapshot and assessment manifests and keeps unsupported scores/projections out of the opener
- Validate: `python -m pytest tests/test_product_strength_api.py tests/test_agentic_analysis_api.py tests/test_dashboard_ui.py tests/test_market_api.py tests/test_revenue_services.py tests/test_api.py -q`
- Evidence: The primary dashboard remains paste-URL-first and now presents the Technical SEO Health, AI Readiness, and Conversion Readiness stack with Evidence Confidence and readiness-versus-visibility disclosure. Secondary controls expose agent preflight/202 queue/status/retry, route/cost/validation/contradiction/review detail, explicit GPT-review events, product-strength snapshots, manifest-validated client bundle history/downloads, immutable comparisons, local heatmap rendering, and aggregate owner imports. APIs expose all product reports including `ai-v3`; agent execution remains fail-closed behind evaluation/operator/promotion gates. New outreach packages snapshot product-strength identity and approval/export revalidate source payload hashes, optional bundle manifests, and optional operator-approved customer-safe assessments; legacy packages remain readable under their original contract. Exact validation: `python -m pytest tests/test_product_strength_api.py tests/test_agentic_analysis_api.py tests/test_dashboard_ui.py tests/test_market_api.py tests/test_revenue_services.py tests/test_api.py -q` -> `20 passed`.

### T14: Calibrate recommendation priority and run the two-vertical pilot
- Status: review
- Owner: parent
- Depends on: T7, T8, T9, T10, T11, T12, T13
- Write set: `src/services/recommendation_priority_service.py`, calibration summaries, Nova/Lacey fixtures, generated pilot artifacts and acceptance tests
- Acceptance: recommendation ordering uses severity, affected scope, commercial intent, current visibility, conversion friction, confidence, effort, and recorded outcomes; human-reviewed Nova/Lacey plus at least 20 additional frozen evidence packs compare repeated DeepSeek and GPT/Codex outputs without treating either model as truth; all agent promotion gates, under-10-minute median review, under-`$0.10` routine inference, under-20% escalation, and zero unresolved exported claims are measured; benchmarks remain internal until the sample-policy gate
- Validate: `python -m pytest tests/test_recommendation_priority.py tests/test_agentic_evaluation.py tests/test_product_strength_pilot.py tests/test_opportunity_reporting.py -q`
- Evidence: Deterministic recommendation priority is implemented in
  `src/services/recommendation_priority_service.py` with all eight accepted
  dimensions, unknown-dimension removal, completeness, and stable ordering.
  `tests/fixtures/product_strength_pilot_v1.json` freezes 22 two-vertical
  cases (Nova Ryu, Lacey Glass, ten additional BJJ, and ten additional trades)
  and the offline harness emits 88 repeated route fixtures. The fixture
  disclosure explicitly labels them `synthetic_contract_fixture`, so they
  cannot satisfy the human-reviewed recorded-output authenticity gate.
  `python scripts/run_product_strength_pilot.py` emitted
  `artifacts/product-strength-pilot/p10-fixture-dry-run.json` with 22 cases,
  88 assessments, a modeled `$0.05` mean routine cost, 6-minute median review,
  0% escalation, zero unresolved exported claims, and
  `promotion_ready=false` because `sample_authenticity=false`.
  `python -m pytest tests/test_recommendation_priority.py
  tests/test_agentic_evaluation.py tests/test_product_strength_pilot.py
  tests/test_opportunity_reporting.py -q` -> `6 passed`; the expanded
  runtime/calibration suite -> `12 passed`. Completing T14 requires explicit
  provider-call authorization plus real human review; routine agent execution
  remains disabled until that evidence exists.

## Verification

Run focused contracts and repositories first:

```powershell
python -m pytest `
  tests/test_product_strength_contract.py `
  tests/test_agentic_analysis_contract.py `
  tests/test_technical_seo_health.py `
  tests/test_report_snapshot_repository.py `
  tests/test_agentic_analysis_repository.py `
  tests/test_client_report_bundle.py -q
```

Run score/evidence semantics:

```powershell
python -m pytest `
  tests/test_scorecard_semantics.py `
  tests/test_ai_readiness_v3.py `
  tests/test_conversion_readiness.py `
  tests/test_search_visibility_v2.py `
  tests/test_local_visibility_grid.py `
  tests/test_ai_visibility.py `
  tests/test_agentic_analysis_runtime.py `
  tests/test_agentic_validation.py `
  tests/test_agentic_evaluation.py `
  tests/test_integrity_regressions.py -q
```

Run lifecycle, API, UI, security, and compatibility:

```powershell
python -m pytest `
  tests/test_market_recovery.py `
  tests/test_agentic_job_service.py `
  tests/test_agentic_prompt_injection.py `
  tests/test_agentic_analysis_api.py `
  tests/test_report_comparison_v2.py `
  tests/test_owned_measurement.py `
  tests/test_product_strength_api.py `
  tests/test_dashboard_ui.py `
  tests/test_api.py `
  tests/test_market_security.py -q
```

Run the full repository verification:

```powershell
python -m pytest -q
python scripts/prp_validate.py .claude/PRPs/plans/P10-TRUSTED-SCORING-DURABLE-CLIENT-REPORTS.plan.md
python scripts/agent_tooling_doctor.py
```

Artifact verification must confirm:

- the run is completed under the compatible pipeline contract;
- legacy reports remain readable;
- every new report is referenced by an immutable snapshot;
- every agent job resolves to one immutable evidence-pack hash, and every call
  records exact runtime/model/provider/token/cost/latency/failure metadata;
- Hermes receives only a short job instruction and the scoped read-only
  evidence MCP; its profile exposes no browser, shell, general network,
  messaging, memory/learning, or unrestricted filesystem capability;
- malicious instructions embedded in page evidence remain inert data and
  cannot affect tools, rubric, service mapping, or output validation;
- every rendered agentic claim is `customer_safe`, schema-valid, and
  independently resolved to an evidence-pack source;
- repeated DeepSeek and GPT comparison results, corrections, escalation rate,
  review time, and per-site cost are stored as evaluation evidence;
- every bundle file matches `hashes.sha256`;
- every displayed claim resolves through `manifest.json`;
- paid/provider and owner-authorized limits are explicit;
- bundle HTML works from a copied directory with the API unavailable;
- comparison deltas are contract/context compatible;
- Nova and Lacey outputs preserve observed/supplied/assumed/modeled labels.

## Evidence And Handoff

- Source research:
  `docs/research/2026-07-26-product-strength-competitive-research.md`.
- Current-code trace:
  `.context/query-context.md`.
- Agent-runtime trace: local Hermes `0.18.2` supports isolated profiles,
  OpenRouter/DeepSeek and OpenAI Codex providers, one-shot execution, usage
  reports, fallback controls, MCP tools, and an isolated backend; no runtime
  configuration or credentials were changed during planning.
- Plan validation:
  `python scripts/prp_validate.py .claude/PRPs/plans/P10-TRUSTED-SCORING-DURABLE-CLIENT-REPORTS.plan.md`
  -> `PASS` on 2026-07-26.
- Implementation authorization: the operator explicitly invoked
  `prp-implement` for the incorporated research on 2026-07-26; P10 is the sole
  durable PRP that implements that research.
- Implementation evidence: T1-T13 are complete with slice-local evidence
  above. The full repository suite completed with `308 passed`; Python source
  and scripts compile, dashboard JavaScript parses, and
  `git diff --check` reports no whitespace errors. T14 is in review because
  no paid/provider calls or real human calibration reviews were authorized;
  its synthetic dry run is preserved separately and cannot promote the agent
  route.
- Before implementation, strategically compact this approved PRP into the
  active execution context and treat the PRP file—not the planning transcript—
  as durable task state.
- Each completed slice must replace `Evidence: pending` with exact tests,
  artifact paths, snapshot IDs/hashes, provider cost/completeness where
  applicable, and parent-reviewed diffs.
- Release A, B, and C require separate parent integration reviews; protected
  migrations, credentials, publishing, and deployment remain human-gated.
