---
id: P12-VERTICAL-AGENTIC-DECISION-ENGINE
title: Vertical Agentic Decision, Journey, and Remediation Engine
status: complete
operation: feature
risk: high
owner: parent
branch: main
created: 2026-07-26
updated: 2026-07-26
---

# Vertical Agentic Decision, Journey, and Remediation Engine

## Summary

Extend the deterministic URL-first product with seven LLM-native capabilities:

1. An operational, durable agentic worker.
2. Vertical buyer-question coverage.
3. Browser-based customer and agent journey testing.
4. Business truth and AI representation accuracy.
5. Private owner-mode funnel diagnosis.
6. Evidence-backed offline “after” prototypes.
7. Outcome-calibrated recommendation memory.

The normal URL flow remains non-blocking. After P10 promotion gates pass, a
qualified prospect run automatically receives decision coverage, a fact ledger,
and three target-only journeys. Competitor journeys, paid AI-response
collection, owner analysis, and prototypes remain explicit operator actions.

No new universal score is introduced. LLM outputs remain immutable,
attributable evidence or labeled inference; they cannot modify deterministic
SEO, AI Readiness, visibility, demand, conversion, or revenue arithmetic.

## Intent And Acceptance

- Paste URL remains primary; deterministic reports complete when the agentic runtime is unavailable.
- Automatic processing requires configuration, operator enablement, and P10 promotion.
- Before promotion, execution is explicit shadow/review mode and cannot enter customer output without approval.
- Ship `national_bjj_registry.agentic.v1` and `one_trade_network.agentic.v1`.
- Automatically run offer discovery, decision resolution, and ready-to-convert journeys.
- Journey work never enters PII, submits forms, authenticates, purchases, messages, downloads, or sends state-changing requests.
- Unknown third-party hosts require approval and a new host-policy version.
- Every answer, fact, representation claim, journey result, and recommendation resolves to persisted evidence.
- Add immutable `decision-intelligence-v1` and additive combined `v6` reports.
- Offline prototypes are deterministic renderings of validated structured blueprints; models never emit executable HTML or JavaScript.
- Prospect mode cannot consume or expose owner evidence.
- Automatic prospect inference is capped at three journeys and `$0.25`; premium inference is capped at `$0.75`, excluding separately approved provider costs.
- Existing runs, P10/P11 artifacts, packages, and APIs remain readable without backfill.

## Scope

Add versioned contracts for `VerticalAgenticPack`, `AgenticWorkItem`,
`AgenticToolStep`, `BusinessFactLedgerSnapshot`,
`DecisionCoverageSnapshot`, `JourneyEvidenceRun`,
`AIRepresentationAccuracySnapshot`, `OwnerDiagnosticSnapshot`,
`RemediationBlueprintSnapshot`, and `RecommendationOutcomeLink`.

Add repository methods to file and SQLite implementations through additive
migration `012_vertical_agentic_evidence.sql`.

Add:

- `GET /api/vertical-agentic-packs/{version}`
- `POST /api/runs/{run_id}/agentic-evidence/preflight`
- `POST /api/runs/{run_id}/agentic-evidence`
- `GET /api/runs/{run_id}/agentic-evidence`
- `GET /api/agentic-work-items/{work_item_id}`
- `POST /api/agentic-work-items/{work_item_id}/retry`
- `POST /api/agentic-evidence/{snapshot_id}/review`
- `POST /api/runs/{run_id}/owner-agentic-analysis`
- `POST /api/runs/{run_id}/remediation-blueprints`
- `POST /api/remediation-blueprints/{blueprint_id}/review`

Permit `decision-intelligence-v1` and `v6` through the report reader.

## Not Building

- LLM-generated rankings, search volume, authority, revenue, or conversion rates.
- A combined LLM/agent-readiness score or synthetic-person forecast.
- Autonomous approval, outreach, publishing, deployment, or site modification.
- Form submission, competitor contact, payment, login, account creation, or PII entry.
- General browser, shell, filesystem, or unrestricted network tools for a model.
- Raw model-generated executable output entering client sites.
- Fine-tuning or outcome-based automatic reprioritization before sample gates.

## Human Gates

- Routine automatic inference requires P10 promotion and operator enablement.
- Paid AI-response collection retains explicit provider approval and preflight.
- Unknown action hosts require approval.
- Owner analysis requires recorded consent and approved P11 snapshot IDs.
- Sensitive facts, semantic claims without exact support, prototypes, and customer exports require review.
- Live Nova/Lacey runs, credentials, deployment, publishing, commits, and pushes remain separate approvals.

## Mandatory Reads

- `AGENTS.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `docs/agentic-analysis-contract.md`
- `docs/product-strength-contract.md`
- `docs/product-revenue-contract.md`
- `.claude/PRPs/plans/P10-TRUSTED-SCORING-DURABLE-CLIENT-REPORTS.plan.md`
- `.claude/PRPs/plans/P11-DEMAND-CONVERSION-EVIDENCE-MODES.plan.md`
- `docs/research/2026-07-26-product-strength-competitive-research.md`

## Execution Path

1. A deterministic InsightRun completes.
2. Reconciliation resolves the qualified prospect and approved vertical pack.
3. Eligible work is idempotently queued; ineligible work reports the exact reason.
4. A separate worker leases work and records every model/tool step.
5. Deterministic validators resolve fields/spans and enforce action policy.
6. Optional representation analysis consumes approved AI Visibility responses.
7. Optional owner analysis uses a separate private aggregate-only pack.
8. Approved evidence generates a structured blueprint and offline prototype.
9. Reports and packages bind exact snapshots and hashes.
10. Activation/correction history produces non-causal outcome summaries.

## Patterns To Mirror

- P10 evidence hashes, leases, retries, call ledger, promotion, injection controls, and append-only review.
- P11 prospect/owner separation, consent, aggregate-only evidence, provenance, and unknown semantics.
- `ScreenshotCaptureService` bounded Playwright behavior.
- `AIVisibilityService` topic identity, paid preflight, and sampling disclosures.
- Immutable report snapshots, content-addressed bundles, manifests, and source-hash validation.
- Append-only activation history and immutable calibration successors.

## Task Slices

### T1: Freeze agentic evidence and policy contracts
- Status: completed
- Owner: parent
- Depends on: none
- Write set: `src/models.py`, agentic/product contracts, schemas, contract tests
- Acceptance: new contracts, states, source requirements, cost/step ceilings, privacy boundaries, grounding, prohibitions, and compatibility are executable.
- Validate: `python -m pytest tests/test_vertical_agentic_contract.py tests/test_agentic_analysis_contract.py tests/test_privacy_context.py -q`
- Evidence: `src/models.py`; `config/agentic/schemas/vertical-agentic-evidence.v1.json`; `docs/agentic-analysis-contract.md`; `docs/product-strength-contract.md`; `tests/test_vertical_agentic_contract.py`; `18 passed in 0.61s`.

### T2: Operationalize the durable agentic worker
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- Write set: repository Protocol/implementations, migration `012`, worker service/script, worker tests
- Acceptance: `scripts/run_agentic_worker.py --once|--poll` leases current P10 and new work, records usage, resumes bounded transient failures, and never performs provider work in API requests.
- Validate: `python -m pytest tests/test_agentic_worker.py tests/test_agentic_job_service.py tests/test_agentic_evidence_repository.py tests/test_agentic_analysis_runtime.py -q`
- Evidence: repository Protocol/file/SQLite P12 persistence; `src/repositories/migrations/012_vertical_agentic_evidence.sql`; `src/services/agentic_worker_service.py`; `src/services/vertical_agentic_work_executor.py`; `scripts/run_agentic_worker.py`; `tests/test_vertical_agentic_work_executor.py`; focused persistence/worker/P10 runtime suite `11 passed`.

### T3: Build vertical decision coverage and business truth
- Status: completed
- Owner: implementation_luna
- Depends on: T1, T2
- Write set: vertical packs, fact/decision services, prompts/rubrics, validators, tests
- Acceptance: both packs use reviewed questions; exact spans/fields support answers and facts; sensitive or unsupported output remains review-only.
- Validate: `python -m pytest tests/test_vertical_agentic_packs.py tests/test_business_fact_ledger.py tests/test_decision_coverage.py tests/test_agentic_validation.py -q`
- Evidence: `src/vertical_agentic_packs.py`; `src/services/business_fact_ledger_service.py`; `src/services/decision_coverage_service.py`; `src/services/vertical_agentic_reconciliation_service.py`; P12 prompt/rubric configs; focused pack/ledger/coverage/validation/prompt-injection suite `15 passed`.

### T4: Add bounded browser journey evidence
- Status: completed
- Owner: parent
- Depends on: T1, T2, T3
- Write set: journey runner, typed browser bridge, host registry, Playwright security tests
- Acceptance: only enumerated actions are available; tasks stop at 12 model decisions, 30 browser actions, 90 seconds, or two retries; prohibited actions fail closed.
- Validate: `python -m pytest tests/test_agentic_journeys.py tests/test_journey_security.py tests/test_screenshot_service.py tests/test_market_security.py -q`
- Evidence: `src/services/agentic_journey_service.py`; `config/agentic/action-host-policies/known-hosts.v1.json`; `tests/test_agentic_journeys.py`; `tests/test_journey_security.py`; `12 passed in 1.77s`.

### T5: Add AI representation accuracy
- Status: completed
- Owner: implementation_luna
- Depends on: T2, T3
- Write set: representation service, AI Visibility integration, response validator, tests
- Acceptance: context-compatible response evidence is reused; collection remains gated; exact response spans compare only with validated ledger facts; readiness/visibility remain unchanged.
- Validate: `python -m pytest tests/test_ai_representation_accuracy.py tests/test_ai_visibility.py tests/test_dataforseo_search.py tests/test_ai_readiness_v3.py -q`
- Evidence: `src/services/ai_representation_accuracy_service.py`; `tests/test_ai_representation_accuracy.py`; `29 passed` across representation, AI Visibility, DataForSEO search, and AI Readiness v3.

### T6: Add private owner-mode agentic diagnosis
- Status: completed
- Owner: parent
- Depends on: T2, T3, T5 and completed P11
- Write set: owner pack/diagnostic services, privacy validator, tests
- Acceptance: only consented aggregate snapshots enter; output cannot change arithmetic, assert causality, or leak into prospect/cross-prospect surfaces.
- Validate: `python -m pytest tests/test_owner_agentic_analysis.py tests/test_owned_measurement_imports.py tests/test_evidence_modes.py tests/test_privacy_context.py -q`
- Evidence: `src/services/owner_agentic_analysis_service.py`; `tests/test_owner_agentic_analysis.py`; `14 passed in 0.56s`.

### T7: Generate remediation blueprints and offline prototypes
- Status: completed
- Owner: implementation_luna
- Depends on: T3, T4, T5, T6
- Write set: blueprint service/schema, deterministic renderer, bundle tests
- Acceptance: structured changes map to approved evidence and services; unknown facts stay placeholders; HTML is self-contained, manifest-valid, non-published, and contains no arbitrary model code.
- Validate: `python -m pytest tests/test_remediation_blueprint.py tests/test_prototype_bundle.py tests/test_report_manifest.py tests/test_client_report_bundle.py -q`
- Evidence: `src/services/remediation_blueprint_service.py`; `src/services/prototype_service.py`; `tests/test_remediation_blueprint.py`; `tests/test_prototype_bundle.py`; focused plus manifest/client-report/contract suite `18 passed`.

### T8: Integrate reports, API, dashboard, and outreach
- Status: completed
- Owner: parent
- Depends on: T2-T7
- Write set: API, dashboard, reporting, outreach validation, integration tests
- Acceptance: URL paste remains primary; agentic work is non-blocking; secondary gates are visible; reports and outreach revalidate all snapshots.
- Validate: `python -m pytest tests/test_vertical_agentic_api.py tests/test_dashboard_ui.py tests/test_decision_intelligence_report.py tests/test_revenue_services.py tests/test_api.py -q`
- Evidence: `src/services/decision_intelligence_reporting_service.py`; `src/services/vertical_agentic_evidence_service.py`; P12 API routes in `src/api/app.py`; the secondary operator controls in `src/api/static/dashboard.html`; v6 outreach bindings and source revalidation; exact validation command `21 passed in 21.93s`.

### T9: Add outcome-calibrated recommendation memory
- Status: completed
- Owner: implementation_luna
- Depends on: T7, T8
- Write set: outcome-link/calibration services, recommendation integration, tests
- Acceptance: recommendations bind to package/outcome history; summaries show denominators and association only; no weight adjustment before 20 sent packages, five positive replies, and three booked calls in that vertical.
- Validate: `python -m pytest tests/test_agentic_outcome_links.py tests/test_agentic_calibration.py tests/test_recommendation_priority.py tests/test_revenue_services.py -q`
- Evidence: `src/services/agentic_outcome_service.py`; `src/services/agentic_calibration_service.py`; gated recommendation-priority integration; `tests/test_agentic_outcome_links.py`; `tests/test_agentic_calibration.py`; focused plus revenue/priority suite `14 passed`.

### T10: Security review and two-vertical pilot
- Status: completed
- Owner: parent with independent `reviewer`
- Depends on: T1-T9
- Write set: pilot fixtures/artifacts and PRP evidence only; reviewer is read-only
- Acceptance: Nova/Tacoma and Lacey/trades fixtures exercise all layers without external writes; all claims resolve; no action submits; no private evidence leaks; cost/review ceilings hold.
- Validate: `python -m pytest tests/test_vertical_agentic_pilot.py tests/test_integrity_regressions.py tests/test_agentic_prompt_injection.py tests/test_journey_security.py -q`
- Evidence: `tests/test_vertical_agentic_pilot.py` exercises frozen Nova Ryu/Tacoma and Lacey Glass/trades fixtures without network/provider writes; exact validation command `33 passed in 6.52s`. Independent read-only reviewer findings were resolved with client-artifact contact/raw-source redaction, current-contract adoption on legacy reruns, and limited/unknown semantics for keyword-only paid evidence. Full regression: `417 passed in 93.42s`.

## Verification

```powershell
python -m pytest tests/test_vertical_agentic_contract.py tests/test_agentic_worker.py tests/test_decision_coverage.py tests/test_business_fact_ledger.py tests/test_journey_security.py tests/test_ai_representation_accuracy.py tests/test_owner_agentic_analysis.py -q
python -m pytest tests/test_remediation_blueprint.py tests/test_prototype_bundle.py tests/test_agentic_outcome_links.py tests/test_decision_intelligence_report.py tests/test_vertical_agentic_api.py tests/test_dashboard_ui.py tests/test_integrity_regressions.py -q
python -m pytest -q
python -m compileall -q src scripts
python scripts/prp_validate.py .claude/PRPs/plans/P12-VERTICAL-AGENTIC-DECISION-ENGINE.plan.md
python scripts/agent_tooling_doctor.py
```

Verification result: all commands passed on 2026-07-26. The full suite reported
`417 passed in 93.42s`; compileall completed without errors; the tooling doctor
reported `ok: true`. Runtime, operator, and P10 promotion flags remain disabled,
so no provider, live-site, form, deployment, publication, commit, or push action
occurred.

## Evidence And Handoff

- Record exact tests, work IDs, snapshot IDs/hashes, trace artifacts, route/cost totals, policy versions, and manifests per slice.
- P10 remains the model-promotion authority; P12 cannot bypass its unfinished real-output gate.
- P11 remains the owner-evidence and deterministic demand/revenue authority.
- Automatic hybrid behavior, deterministic offline HTML, and same-origin plus a versioned known-host registry are the selected defaults.
