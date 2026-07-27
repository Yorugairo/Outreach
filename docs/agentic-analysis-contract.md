# Agentic Analysis Contract: P10 Runtime and Governance

## 1) Evidence boundary

`SiteEvidencePack` is generated only from persisted Outreach artifacts and is
the only input to any agentic analysis. It must be immutable and hashed.

- Required identities in pack:
  - run/attempt/report-snapshot/vertical-pack/keyword-set/market-run/scenario IDs
  - normalized business/target facts
  - bounded excerpt + evidence references
- Excluded by default:
  - raw credentials, cookies, PII, owner analytics, local secrets, raw scripts/instructions.
- Website text is treated as untrusted data and cannot alter policy, model, or rubric.

## 2) Job lifecycle

`AgenticAnalysisJob` state machine:

- `queued` → `packing` → `running` → `validating` → (`needs_review` | `complete` | `partial`)
- `failed` for terminal hard errors
- `superseded` for replaced executions

Idempotency key is derived from:

- evidence-pack hash
- vertical version
- rubric version
- prompt version
- requested model route
- analysis mode

Retry on transient provider failure must create a new attempt record under same job
identity and preserve predecessor references.

## 3) Agent call ledger

`AgentCallRecord` is append-only and includes:

- requested and served model/provider/runtime
- prompt and rubric IDs/versions
- routing mode
- attempt number
- status and failure class
- input/output/reasoning token counts
- latency and cost (actual/estimate)
- raw response reference
- start/end timestamps

Any served provider/model change from requested route must be logged as explicit
routing divergence and must create a new attributed execution or review path.

## 4) Assessment lifecycle and review state

`AgenticAssessmentSnapshot` is immutable and contains:

- source/evidence hashes
- runtime/model/provider/prompt/rubric/schema IDs
- finding type (`observed`, `inference`, `recommendation`)
- evidence refs, confidence, severity, commercial relevance, service fit
- contradictions, limitations, validation result, predecessor

Assessment review state is derived only from append-only review events:

- `unreviewed`
- `needs_review`
- `approved`
- `rejected`

Corrective actions are represented as review events with structured reason codes
and may spawn successor executions where needed.

## 5) Validation and safety gates

- A validator resolves every candidate claim to evidence references and provenance.
- Rejects prompt-injection artifacts, unsupported business facts, invalid service
  mappings, and customer-unsafe claims before persistence/render.
- Unsupported candidates may be retained only as failed/review evidence, never shown as customer output.

## 6) Passes and sequencing

Four fixed passes execute over the same immutable evidence pack:

1. Evidence analyst
2. Vertical strategist
3. Recommendation prioritizer
4. Client editor

Each pass consumes prior validated output; no unconstrained conversational memory.

## 7) Runtime identities and policy

- Routine route:
  - Provider: OpenRouter
  - Model: `deepseek/deepseek-v4-flash`
  - Profile: `outreach-analysis`
- Defaults are disabled unless explicitly enabled and operator-gated.
- Runtime configuration records only sanitized booleans/version IDs; never secrets.
- Default invocation limits:
  - max 4 model calls
  - bounded output tokens
  - 2 transient retries per call
  - `$0.10` total inference ceiling per site

## 8) Promotion gates

Routine DeepSeek route remains disabled until measured pass conditions are met:

- 100% final schema validity
- zero unsupported exported claims
- at least 98% draft evidence-reference precision
- at least 85% human service-fit agreement
- at least 80% top-three recommendation overlap across repeated runs
- under 10% factual correction rate
- under 20% GPT escalation
- under `$0.10` routine inference per site
- full audit evidence recorded for each run

GPT/Codex review is operator-triggered only:

- allowed through reviewed endpoints/events
- never auto-routed
- never a required dependency for deterministic artifacts

## 9) Interfaces and provenance boundaries

Mandatory endpoints:

- preflight and status/read endpoints are safe-by-default
- start/retry/review/review-request endpoints require operator auth and gates

Every rendered client claim resolves to:

- immutable evidence references,
- assessment snapshot IDs,
- manifest entries, and
- manifest/source hashes.

## 10) Legacy-read and persistence compatibility

- Existing legacy assessment/rubric/model outputs must remain readable for old runs.
- Deterministic scores and report contracts in SEO/AI/local/conversion pipelines are never overwritten by agentic output.
- New agentic state is additive and does not mutate existing run or scoring artifacts.

## 11) Vertical decision and journey evidence v1

P12 adds a separate `vertical-agentic-pack.v1` contract. A reviewed pack owns
buyer questions, applicability rules, the three bounded target journeys, success
oracles, service mappings, and an action-host policy version. The required target
journeys are offer discovery on desktop, decision resolution on mobile, and
ready-to-convert CTA access on mobile.

Work is represented by durable `agentic-work-item.v1` records. Automatic work
is capped at 12 model decisions, 30 browser actions, 90 seconds, two transient
retries, and `$0.25` aggregate inference. Premium work requires preflight and is
capped at `$0.75`, excluding separately approved provider costs. A work item
cannot bind owner consent in prospect mode, and owner diagnostics cannot run in
prospect mode.

Browser steps are append-only. Models select an opaque candidate-action ID from
an enumerated accessibility/DOM view; they never supply URLs or selectors.
Allowed actions are navigation/activation of an approved candidate, scroll,
back, bounded wait, and evidence capture. Form fill/submission, personal-data
entry, authentication, purchase, message, upload, and download are prohibited.
Unknown hosts return `needs_approval` and cannot record an after-navigation URL.

Positive facts, answers, journey outcomes, representation classifications, and
recommendations require independently resolvable evidence:

- an exact span in a persisted source;
- an exact persisted-field path;
- a persisted DOM or screenshot reference; or
- an exact span in a provider response artifact.

Missing and unknown results remain reportable without fabricated evidence. No
P12 contract contains or alters SEO, AI Readiness, visibility, demand,
conversion, revenue, or authority score arithmetic.

Owner diagnostics are `owner_verified` and `private_owner_only`. They require
recorded consent plus unique approved aggregate P11 snapshot IDs. Owner
observations and hypotheses cannot enter prospect evidence, outreach, or
cross-prospect retrieval.

Models produce only `remediation-blueprint.v1` structured data. Raw HTML,
JavaScript, CSS, executable code, and script markup are invalid. Approved
blueprints may be rendered by the deterministic `offline-prototype.v1`
renderer. Rendering, publication, deployment, or production-site changes remain
separate actions.
