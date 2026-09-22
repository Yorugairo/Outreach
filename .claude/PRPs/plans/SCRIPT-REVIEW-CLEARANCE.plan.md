---
id: SCRIPT-REVIEW-CLEARANCE
title: Enforce complete script review without flattening the story
status: running
operation: fix
risk: high
owner: parent
branch: codex/Astra
created: 2026-09-20
updated: 2026-09-20
---

# Script Review Clearance

## Summary

Repair the existing script-review contract, not replace it with another writing framework. Mechanical PASS must never imply that the full map, declared beats, doctrinal judge, blind viewer, evidence, voice, or measured timing passed. Make omitted work visible and enforceable at the stage that actually needs it. Preserve free scratch and quarantined preview workflows.

Planning only. No script rewrite, gate implementation, paid review, recording, or release is authorized by this draft. American Debt Trap V14 is the regression case, not a script to optimize silently.

## Intent And Acceptance

1. A mechanically clean V14 with its current two-row opening receipt and missing viewer must report `MECHANICAL: PASS` and `CLEARANCE: INCOMPLETE`, listing the missing obligations. No unqualified terminal PASS.
2. Every applicable obligation in FULL-VIDEO-MAP, CHECK-RESPONSIBILITIES sections 3a-3i, the current craft roster and emitted strength screens has an owner, stage, evidence requirement and outcome. An explicit, reviewed N/A is different from omission. Deferral names the later stage; it never erases an obligation.
3. Every declared beat occurrence is separately reviewed with an exact quote and true/laundered finding. Every applicable JUDGE row receives an individual verdict and rationale. A generic anonymous score, VidIQ score, or J13/J14 receipt cannot substitute for these.
4. The micro/macro map is authored before clearance: connected setup, tension, payoff and next question, not just timestamps or tag counts. The first 180 seconds receives an explicit continuity review; reports show 90/180/300-second windows, separating tag spacing, reviewed hook spacing and open-loop coverage.
5. Missing, malformed, stale, wrong-version, wrong-scope or partial mandatory review receipts block the relevant stage before provider calls or final artifact promotion. Historical reports remain readable, never silently grandfathered into current clearance.
6. Scratch audio remains possible before measured review. A 90-180-second prefix preview cannot be classified as a complete short, clear the body, or authorize final recording/release.
7. Keep G20 advisory; preserve raw G01 3.06-second failure and the user's case-specific acceptance. No blanket threshold relaxation, new keyword quota or compulsory rehook sentence every N seconds.
8. Demonstrate both red and green cases offline: fail-open V14, missing middle review, fake tags, stale receipts, timing changes, legitimate sustained narrative tension, and a complete conforming fixture. Green means complete/clear for a named stage, not proof of audience retention or operator approval.

## Scope

Runner/report aggregation; review receipts; existing viewer custody; map coverage; recording preflight consumers; free-scratch and prefix boundaries; associated tests and routing/docs. All contract/integration edits remain parent-owned. Workers receive exact non-overlapping write sets only after approval.

### Grounded diagnosis

| Source | Observed behavior | Consequence |
|---|---|---|
| `content/video_engine/scripts/run_script_gates.py`, `verdict_line`, `viewer_block`, `render_report` | Missing viewer returns zero failures; final verdict counts tool/viewer failures, not completion of agent obligations | NOT RUN and outstanding JUDGE can end in PASS |
| Same file, `check_report` / `recording_preflight` | Report custody is based on spoken hash plus PASS; opening receipt is separately required for long form | Current receipt proves J13/J14 only, not full review |
| `gate_opening_structure.py`, G36 | `all_tags` resets the broad cycle clock | Activity is not an intentional hook or a closed STR loop |
| `CHECK-RESPONSIBILITIES.md`, R2-R4 and sections 3/5 | Individual declared, JUDGE, roster, loop, evidence reviews are already required; NOT RUN needs an operator-rulable reason | The contract exists but is not fully enforced by the runner |
| `REVISED-V14-GATES.md` | Estimated PASS, 14 JUDGE rows, VIEWER NOT RUN | It is not complete script clearance |
| `REVISED-V14-OPENING-REVIEW.json` | Exactly J13 and J14 | Narrow opening review was overgeneralized |
| `GATES-MEASURED-V14.md` | Measured failures remain separate from the estimated report | An estimated green must not overwrite measured blockers |

V14 source evidence lives in `docs/research/runs/american-debt-trap-20260920/script-review/`; measured artifacts live in `content/video_engine/projects/systems-and-blowups/american-debt-trap/`. Preserve these reports unchanged. Previously measured explicit rehook gap: 57.375 to 177.650 seconds, 120.275 seconds. The untagged lender question appears earlier; the gap is a diagnostic, NOT automatic proof of absent curiosity. Regression must check the missing semantic evidence, not manufacture a fixed-frequency writing rule.

Recall: CHECK-RESPONSIBILITIES R2 distinguishes a tag's presence from truth; R3 requires each JUDGE row; R4 names all remaining agent duties; section 5 says a missing block is not a review. FULL-VIDEO-MAP section 0 defines L2 setup-tension-resolution; section 2 distinguishes positional rehooks from the slow-bleed remedy. These are existing requirements.

## Not Building

- No new video renderer, dashboard, database, orchestration service, automatic script rewriter, or replacement of the map/craft registry.
- No new retention score presented as viewer behavior; LLM scores remain feedback, not audience measurements.
- No policing narrative quality with question marks, template-family phrases, filler hooks or source-name counts.
- No changing verified financial claims, title, voice, approved art, or V14 during this process repair.
- No flattening judge scores into mechanical truth or turning all WARNs into FAILs.
- No release/publish authorization, paid provider calls, commit or push.

## Human Gates

HG1: **APPROVED — E99 s86 (2026-09-20).** The operator invoked `$prp-implement` on this plan. Implement the stage requirements, backward compatibility and scoped exceptions before touching episode prose. No paid provider call, commit, push, episode rewrite or release is authorized.

Existing operator gates remain unchanged: script changes beyond approved scope/rewrite budget, final voice/art and release. The plan does not create an operator task for every agent review. Routine semantic work is the agents' responsibility; only genuine conflicts or requested exceptions reach the operator with evidence.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`, `docs/WORKTREE-REGISTER.md` before implementation; respect current lane ownership and claim a ruling only if one is needed.
- `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` (entire contract), `FULL-VIDEO-MAP.md`, applicable phase guides, `STRENGTH-LOOP.md` and `SENTENCE-STRENGTH-CHECK.md`.
- `.agents/skills/script-writer/SKILL.md`, including required Humanizer/persona references before any later prose revision. This plan does not revise prose.
- `docs/content-video-engine/PIPELINE.md`, `patterns/CRAFT-DEVICES.md`, generated `docs/CRAFT-MAP.jsonl` and `docs/GATES-REGISTRY.jsonl` with their builders. Generated joins are retrieval aids, not proof that semantics is implemented.
- `run_script_gates.py`, `opening_review.py`, `viewer_windows.py`, `viewer_run.py`, `viewer_score.py`, `gate_opening_structure.py`, recorder preflight callers and their focused tests.
- V14 raw source/reports, measured clock, and the user's G20/G01 decisions. Do not inherit unrelated Fed pilot exceptions.

## Execution Path

### A. One completeness contract, backed by the existing doctrine

Add a small versioned `script_review_contract.py` adapter that enumerates obligations from the existing checkers, source-backed craft roster and responsibility sections. Add only the stable stage/applicability mappings missing from those sources; do not copy doctrine prose into a competing registry. Emit source anchors and a coverage manifest. Every source row must map to one or more obligations or an explicit reviewed exclusion; a new/unmapped source row causes an INCOMPLETE coverage result, not silent omission.

Use identities scoped by tool/family/stage and occurrence: `opening:J01` differs from motion J01; two `[rehook]` tags have two occurrence IDs. Requirement coverage counts are inventory metrics, never quality scores. Include section 3h evidence/persona/thesis/ear duties and Humanizer; do not solve only the hook subset.

### B. Named stages avoid circular checks

| Stage | Required now | Not implied |
|---|---|---|
| Diagnostic draft | Valid input; raw tool results; full missing-work list | No clearance; a successful command only means diagnostics ran |
| Scratch | Valid script input and safe local/free provider route; review gaps retained | No measured-timing or final-voice approval prerequisite |
| Text review | Mechanical draft results, declared beats, textual JUDGE, full script map/roster/screens, evidence/persona/Humanizer review, current blind viewer | Visual counterpoint may be explicitly deferred to the shot plan; ear/timing to scratch |
| Prefix preview | Full-source identity plus exact measured prefix range, prefix-relevant map/reviews/evidence and named outstanding full-episode duties | Not a complete short, final recording, or whole-episode clearance |
| Final recording readiness | Complete applicable text reviews plus aligned scratch timing, measured rechecks and ear review; package/shot-plan judgments due at this stage | Final art/render QA and operator release remain separate |

Per-stage machine clearance is `CLEAR`, `INCOMPLETE`, `FAIL`, or `EXCEPTION`. Preserve individual `PASS/WARN/FAIL/NOT_RUN/STALE/DEFERRED/NA` findings. FAIL means a demonstrated applicable defect; INCOMPLETE means missing/unverifiable work. If both exist, retain both lists and use FAIL as headline. N/A needs an applicability basis validated against the contract; deferral cannot move a due obligation past the target stage. Never mark an operator-approved state automatically.

Default runner prints `MECHANICAL`, `REVIEW COMPLETENESS`, and stage-scoped `CLEARANCE`. Proposed CLI: `--stage diagnostic|text-review|prefix-preview|recording`, with `--review <receipt>` and explicit prefix/timeline arguments. Diagnostic invocation may exit 0 when tools executed cleanly even with INCOMPLETE review, but must not emit legacy `VERDICT: PASS`. Required-stage invocation exits nonzero unless clear; existing consumers migrate atomically to the structured clearance, not loose Markdown matching.

### C. Durable receipts, exact inputs and reviewers

Reuse `opening_review.py` validation patterns, exposing one full `script_review.v1` receipt and keeping old J13/J14 sidecars readable as PARTIAL imports. A receipt includes: canonical spoken SHA; annotated-source SHA; map SHA; rules/contract digest; form and full runtime; requested stage/scope; timing basis and timeline/take digests when measured; reviewer role/run identity; individual row IDs, quotes or span anchors, rationale, result, and linked evidence artifacts.

Spoken changes invalidate semantic/viewer coverage; tag-only changes invalidate declared/coverage reviews even if audio remains reusable. Measured timing changes invalidate temporal rows without pretending the wording changed. Package, evidence or shot-plan edits invalidate dependent judgments via explicit dependency hashes. Any reused finding names its original receipt, verifies unchanged dependencies and is reported as reused, never a new independent review. Default to full rerun when dependency reuse cannot be proved.

The judge sees doctrine and the map; the blind viewer sees only the package and narration windows, never tags, desired answers, author ratings or previous reviews. VidIQ remains a separately attributed editorial input; it neither clears missing rows nor automatically overrides a failing source/semantic finding. Require an independent semantic reviewer for the continuity map; preserve author and reviewer findings separately. Software can verify custody/completeness, not whether an LLM's judgment is true.

### D. Map relationships, not a new hook timer

Canonical artifact: `<script-stem>-NARRATIVE-MAP.json`, schema `narrative_map.v1`, stored beside the script, with a generated readable Markdown companion. This is the script's semantic map, not the visual `BEAT-MAP`/`BEAT-PLAN` or shot table. Reuse existing authored narrative relationships by explicit import with provenance; do not require authors to maintain two parallel semantic maps. Visual plans reference these stable narrative IDs. The receipt binds the canonical map digest. T3 owns its schema/validation and readable rendering.

Each authored micro-loop names: setup span, unresolved question/tension, consequential advance, payoff span, next-loop relationship and shared object/person. Macro rows trace phase intent, foreshadow-to-delivery, head-fake-to-reversal, callback/ring lifecycle and CTA placement using existing requirements and runtime geometry. Support overlapping micro and macro loops without letting a long macro promise mask an empty micro interval.

Tools check span validity, temporal ordering, missing links, cited payoff existence, measured durations and uncovered intervals. The judge checks whether tension actually persists, the payoff answers the setup, and the transition is causal rather than merely the next topic. The viewer reports what question it is holding and what changed. Valid non-interrogative hooks are allowed. A rhetorical question that is answered immediately without opening anything else is not automatically a retention loop.

Keep G36 explicitly labelled broad beat-activity spacing. Report separate explicit-tag spacing and reviewed functional-hook spacing, plus semantic loop coverage for 0-90/180/300s, clipped to runtime and including endpoint tails. The 30-60s STR guidance is applied by loop type and reviewed rationale, not converted into a blanket new hard maximum between `[rehook]` tags. Unknown semantic coverage blocks readiness as INCOMPLETE; raw timing anomalies are surfaced for judgment. A later scoped exception remains visible.

### E. Exceptions and migration

No missing receipt becomes a PASS via `--force` or `--no-viewer-gate`. Retain diagnostic flags, but they cannot produce recording clearance. An exception must reference the actual operator decision, exact rule/occurrence, source hash, stage/scope, reason and expiry/supersession condition. Free-text agent rationale alone cannot authorize it. This implementation therefore fails closed on all recording-stage mechanical failures; no recording exception path is enabled until that operator-decision artifact and its validator exist. The 3.06s opening decision remains episode-specific evidence, not a global tolerance. Existing missing records do not block historical playback or rewrite old files.

Shorts use their actual short contract; full-episode prefixes use the full form plus a scope, never inference from excerpt duration. Visual-only duties are deferred until a shot plan/render exists, not marked N/A forever. Downstream release already has its own gates: preserve them and ensure no new script receipt implies release clearance.

## Patterns To Mirror

- `opening_review.py` and `test_opening_review*.py`: source-bound rows and preflight validation, but expand completeness beyond J13/J14.
- `run_script_gates.py`: retain raw checker outputs and exact severities; centralize the aggregate decision rather than alter every linter.
- `test_viewer_score.py` and `fixtures/viewer/`: offline perception/scorer fixtures; no paid model in unit tests.
- `build_craft_map.py` / `build_gates_registry.py`: source-derived inventories and stale checks, not hand-editing generated output.
- `CHECK-RESPONSIBILITIES` section 5: render the existing report blocks from validated receipts.

## Task Slices

### T1: Freeze the coverage and stage contract
- Status: complete
- Owner: parent
- Depends on: HG1
- Write set: this plan; `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`; new `content/video_engine/scripts/script_review_contract.py`; new `content/video_engine/tests/test_script_review_contract.py`
- Acceptance: complete source-to-obligation inventory, stage/applicability matrix, conflict list and identities; no doctrine item silently omitted; G20 and scoped G01 decision preserved. Resolve stale documentation such as P1-P2-only claims versus whole-runtime G36/G44. Inventory all preflight/report consumers before T5.
- Validate: `python -m pytest content/video_engine/tests/test_script_review_contract.py -q`
- Evidence: `script_review_contract.py`; focused tests PASS; the initial 196-row inventory expanded to 274 obligations after every emitted strength-screen candidate received its own row. `V14-COVERAGE-MANIFEST.json` records digest `90fa167f8abfb3a0c8594f5e544543cec859500dc846ab342735363a601f9f85`. Preflight consumers are the three recorder callers of `recording_preflight`: master, chained and short.

### T2: Reproduce the false clearance offline
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: new `content/video_engine/tests/fixtures/script_review/`; new `content/video_engine/tests/test_script_clearance_regression.py`
- Acceptance: minimal V14-based fixture preserves current false-PASS behavior as a documented baseline; expected new behavior fails until fixed. Add green complete fixture and sustained-tension case. No tests depend on gitignored episode paths or provider access.
- Validate: `python -m pytest content/video_engine/tests/test_script_clearance_regression.py -q` (red baseline retained until T4).
- Evidence: `tests/fixtures/script_review/` plus `test_script_clearance_regression.py`; the historical empty/partial receipt is `INCOMPLETE`, a source-bound complete fixture clears, and sustained semantic coverage remains valid.

### T3: Validate receipts and narrative-map relationships
- Status: complete
- Owner: implementation_luna
- Depends on: T1, T2
- Write set: new `content/video_engine/scripts/script_review.py`; new `content/video_engine/tests/test_script_review.py`; new `content/video_engine/tests/test_script_review_map.py`
- Acceptance: strict schema/completeness/custody checks, per-occurrence verdicts, dependency invalidation, map spans and stage deferrals; N/A and reuse cannot bypass obligations. Invalid/empty/duplicate receipts fail closed. Exact quotes use the same canonicalization as script hashing.
- Validate: `python -m pytest content/video_engine/tests/test_script_review.py content/video_engine/tests/test_script_review_map.py -q`
- Evidence: strict `script_review.v1` and `narrative_map.v1` validators; per-occurrence rows, distinct reviewer runs, exact spans, map identity/runtime, stage scope, 90/180/300 coverage and fail-closed INFO/NA/defer behavior are covered offline.

### T4: Wire runner and blind-viewer custody
- Status: complete
- Owner: parent
- Depends on: T3
- Write set: `content/video_engine/scripts/run_script_gates.py`, `opening_review.py`, `viewer_windows.py`, `viewer_run.py`, `viewer_score.py`, `gate_opening_structure.py` (G36 labelling only); their existing tests; T2 regression test
- Acceptance: missing/malformed/stale/partial viewer results cannot clear review; propagate verified source/window/timeline identity through the viewer chain. Raw warnings/failures retained. Missing JUDGE/screens/map rows yield INCOMPLETE. Two-row opening receipt is reported as partial, never discarded or upgraded silently.
- Validate: `python -m pytest content/video_engine/tests/test_run_script_gates.py content/video_engine/tests/test_opening_review.py content/video_engine/tests/test_opening_review_wiring.py content/video_engine/tests/test_viewer_windows.py content/video_engine/tests/test_viewer_score.py content/video_engine/tests/test_script_clearance_regression.py -q`
- Evidence: runner emits separate mechanical/completeness/stage clearance. Viewer custody binds annotated/spoken/timeline/windows/raw-report hashes, requires complete contiguous windows and valid answers, deterministically recomputes V01-V05, rejects duplicate IDs, and compares the emitted viewer artifact exactly.

### T5: Enforce consumers without blocking diagnostic production
- Status: complete
- Owner: parent
- Depends on: T4
- Write set: `run_script_gates.py` preflight; `record_master_take.py`, `record_chained_take.py`, `record_short_take.py` under `content/video_engine/scripts/`; `scratch_take.py` only if needed; new `content/video_engine/tests/test_script_clearance_preflight.py`; exact additional consumers discovered in T1 require a plan write-set amendment before edits
- Acceptance: final recorder refuses incomplete/stale receipts before provider calls; scratch still works without measured clearance; prefix cannot clear full episode or masquerade as short; diagnostic flags cannot bypass clearance. Normalize scratch `start_s/end_s` through the existing native word-clock adapter into gate/viewer `start/end`; bind the original and normalized hashes, validate token alignment and monotonicity, and refuse silent estimated fallback when measured review is requested. Mock providers prove zero calls on refusal. Paid voice remains uncalled during verification.
- Validate: `python -m pytest content/video_engine/tests/test_script_clearance_preflight.py content/video_engine/tests/test_opening_review_wiring.py -q`
- Evidence: all three recorder consumers route through `recording_preflight`; offline tests prove missing/stale/incomplete custody and mechanical failure stop before provider lookup. Prefix/full form boundaries and native measured clock normalization are covered. Free-text force cannot authorize recording.

### T6: Align operating instructions and regression evidence
- Status: complete
- Owner: parent
- Depends on: T5
- Write set: `.agents/skills/script-writer/SKILL.md`; `docs/content-video-engine/PIPELINE.md`; `patterns/CHECK-RESPONSIBILITIES.md`; this plan; `docs/research/runs/script-review-clearance/**`; generated doc layers through existing builders only
- Acceptance: workflow starts with the semantic map, runs the two distinct judge/viewer roles, gathers receipts, and reports exact remaining duties. No second hand-kept roster. Fresh diagnostic V14 report in a new evidence directory shows INCOMPLETE/FAIL as applicable without changing narration or historical artifacts. Related shared skill content is not silently copied/overwritten; route divergence is recorded for a scoped follow-up if outside this write set.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/SCRIPT-REVIEW-CLEARANCE.plan.md`; `python content/video_engine/scripts/build_docs_layers.py --refresh`; `python content/video_engine/scripts/build_gates_registry.py --check`; `python content/video_engine/scripts/build_craft_map.py --check`
- Evidence: skill, pipeline and responsibility docs align; unchanged V14 evidence reports diagnostic `INCOMPLETE`/`FAIL`; all 12 generated layers refreshed current; gates registry 204/204 cites, craft map 181/181 definitions, and PRP validation pass.

### T7: Independent adversarial review and parent integration
- Status: complete
- Owner: reviewer (read-only); parent integrates
- Depends on: T6
- Write set: parent only, named corrective files from prior slices and this plan; reviewer writes no production code
- Acceptance: challenge fake all-PASS receipts, missing middle windows, wrong hashes, tag-only edits, viewer leakage, generic scores passed as review, unsupported N/A, stage spoofing and --force. Verify valid long/short/preview workflows. Zero unaddressed high-severity clearance bypasses; preserve independent review findings even when resolved.
- Validate: `python -m pytest content/video_engine/tests/test_script_review_contract.py content/video_engine/tests/test_script_review.py content/video_engine/tests/test_script_review_map.py content/video_engine/tests/test_script_clearance_regression.py content/video_engine/tests/test_script_clearance_preflight.py content/video_engine/tests/test_run_script_gates.py content/video_engine/tests/test_opening_review.py content/video_engine/tests/test_opening_review_wiring.py content/video_engine/tests/test_viewer_windows.py content/video_engine/tests/test_viewer_score.py content/video_engine/tests/test_gate_opening_structure.py tests/test_cadence_advisory.py -q`; `git diff --check`
- Evidence: independent review found and parent fixed viewer-score laundering, duplicate viewer IDs, shared reviewer run IDs, free-text force, partial full-scope, beyond-runtime spans, middle coverage gaps and cyclic/disconnected loop graphs. Final independent pass found no high-severity false-completion path. The full focused command passes 222 tests; scoped syntax/diff checks and generated-layer checks pass.

## Verification

Beyond per-slice commands, require tests for: a missing artifact; stale spoken hash; tag-only hash change; altered rules or map; changed timeline; wrong form/scope; incomplete viewer window count; duplicate/unexpected IDs; missing screen verdict; unsupported quote; out-of-order payoff; absent next-loop link; numerical gap without semantic failure; semantic failure despite dense tags; unknown obligation; reviewed N/A; valid stage deferral; no-viewer/force diagnostics; operator exception outside its scope; provider refusal before spending; and script-ready status never authorizing release.

Do not rewrite or relabel V14 to make the test green. The negative fixture becomes correctly INCOMPLETE, while an independently authored conforming fixture demonstrates CLEAR. Software checks that required reviews exist and match inputs; it does not certify the truth of subjective judgments. Review sampled semantic verdicts independently, including all first-three-minute loops, rather than rewarding artifact volume.

## Evidence And Handoff

Planning evidence: live code/doc inspection on 2026-09-20; SigMap query located the runner and preflight; index reported stale layers, so direct source files were used. No implementation or provider call in this planning turn.

Execution authorization: E99 s86. Implementation began on `codex/Astra` with a heavily dirty user worktree; only named write sets may be touched and every overlapping diff must be preserved/reviewed. No commit or push authorization.

Draft validation: `prp_validate.py` PASS; review queue generator `--check` PASS; focused `git diff --check` clean (line-ending notices only). Added HG1 through `review-queue.v1.json` and regenerated its Markdown/HTML with the existing generator; pre-existing queue entries were retained. Implementation test commands above are planned, not claimed as run.

Read-only delegated trace confirmed fail-open viewer/report paths and the scratch-to-viewer timestamp schema mismatch. Its canonical-map-artifact concern is resolved in section D; tag-only invalidation is explicit in section C. Existing focused test seeds: `test_run_script_gates.py:183-259`, `test_opening_review_wiring.py:53-125`, `test_viewer_windows.py:115-155`, `test_viewer_score.py:186-212`. Parent verified the runner paths and three recorder callers directly. No delegated implementation diff exists.

Store subsequent baseline, source coverage, input hashes, stage matrix, fixture reports, review findings and exact validation output under `docs/research/runs/script-review-clearance/`; retain tracked offline fixtures in tests. Update slice status only after verified evidence. On completion, report process correctness separately from the episode's still-pending script/visual readiness. Next episode action is a targeted first-three-minute semantic review against the unchanged script, then only justified, authorized edits.

Rollback: restore only this feature's changes through a reviewed diff; preserve all user changes and historical reports. Do not re-enable the ambiguous PASS consumer while continuing to claim complete review enforcement. If rollout is stopped, mark enforcement unavailable and keep final recording blocked on unresolved completeness.
