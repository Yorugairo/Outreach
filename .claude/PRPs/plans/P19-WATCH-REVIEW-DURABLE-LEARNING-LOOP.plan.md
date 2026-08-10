---
id: P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP
title: Watch Review Durable Learning Loop
status: complete
operation: feature
risk: standard
owner: parent
branch: codex/stickly-woodblock-variant
created: 2026-08-08
updated: 2026-08-08
---

# Watch Review Durable Learning Loop

## Summary

Add a repository-native bridge from `/watch` evidence to durable episode review packets, bounded edit deltas, PRP intake, and confidence-scored learning candidates. Keep extraction, execution planning, and rule promotion as separate stages.

## Intent And Acceptance

- A `/watch` review can be persisted as a hash-bound JSON manifest plus readable Markdown and selected evidence copies.
- Every finding is timestamped, classified by scope and kind, and carries a proposed fix and observable acceptance rule.
- Repeated findings can be aggregated into project/lane/global learning candidates without automatically editing skills.
- The repository routes systemic review findings through `prp-plan`; small episode corrections remain edit deltas.
- Focused tests prove hashing, schema validation, evidence copying, scope routing, and promotion thresholds.

## Scope

- Generic video-review schemas and deterministic compiler/aggregator service.
- Operator-facing scripts, template, runbook, and repository-local `watch-review` skill.
- Skill routing and allowlist integration.
- Focused tests and PRP evidence.

## Not Building

- Changes to the external `watch` package or its frame-extraction implementation.
- Automatic edits to production skills, global memory, or published videos.
- A dashboard, database, provider integration, or background observer.
- Storage of complete extracted frame dumps or copied source videos.

## Human Gates

- Operator approval remains required before a learning candidate changes a skill, runbook rule, or global instinct.
- A review-derived PRP remains subject to the ordinary PRP approval gate unless the user explicitly requests plan-and-execute.
- Publication and external-provider actions remain outside this implementation.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/agent-context/SKILL_ROUTER.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `.agents/skills/prp-plan/SKILL.md`
- `.agents/skills/prp-implement/SKILL.md`
- `C:/Users/Snipe/.agents/skills/watch/SKILL.md`
- `C:/Users/Snipe/.codex/skills/continuous-learning-v2/SKILL.md`

## Execution Path

1. Define versioned review and learning contracts.
2. Implement deterministic compilation, readable reports, and aggregation.
3. Add the operator workflow and PRP routing skill.
4. Validate focused behavior, documentation links, and PRP state.

## Patterns To Mirror

- Canonical JSON hashing and Draft 7 validation in `content/video_engine/src/services/finance_channel.py`.
- Evidence-first manifests under `content/video_engine/projects/*/review/`.
- PRP lifecycle and task-slice contracts in `docs/runbooks/PRP_EXECUTION.md`.
- Project-scoped, evidence-backed confidence rules from `continuous-learning-v2`.

## Task Slices

### T1: Define review and learning contracts
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/configs/video_watch_review_v1.schema.json`, `content/video_engine/configs/video_review_learning_v1.schema.json`, `content/video_engine/templates/watch-review-draft.v1.json`
- Acceptance: Schemas distinguish episode findings, evidence, scope, confidence, status, and promotion state without permitting unknown fields.
- Validate: `python -m pytest content/video_engine/tests/test_video_review_learning.py -q`
- Evidence: Schemas and draft template added; focused suite validates strict shapes and semantic timing rules.

### T2: Implement deterministic packet and learning compilation
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/src/services/video_review_learning.py`, `content/video_engine/scripts/compile_watch_review.py`, `content/video_engine/scripts/aggregate_review_learnings.py`, `content/video_engine/tests/test_video_review_learning.py`
- Acceptance: Valid drafts produce hashed JSON, Markdown review, edit delta, selected evidence copies, and learning candidates; invalid timings, hashes, paths, or schema shapes fail explicitly.
- Validate: `python -m pytest content/video_engine/tests/test_video_review_learning.py -q`
- Evidence: `7 passed in 0.19s`; compiler copies only selected evidence and emits hashed JSON plus readable review, edit delta, and learning reports.

### T3: Integrate the durable operator workflow
- Status: complete
- Owner: parent
- Depends on: T2
- Write set: `.agents/skills/watch-review/SKILL.md`, `docs/runbooks/VIDEO_REVIEW_LEARNING.md`, `docs/AGENT_START_HERE.md`, `docs/agent-context/SKILL_ROUTER.md`, `scripts/configure_codex_skill_allowlist.py`
- Acceptance: Agents are routed from `/watch` through compiled evidence to either an episode edit delta or `prp-plan`, then through focused rewatch and gated learning promotion.
- Validate: `python scripts/configure_codex_skill_allowlist.py --check`
- Evidence: Repository-local `watch-review` skill, runbook, start route, skill router entry, and allowlist registration added; allowlist check passes.

### T4: Verify and close the contract
- Status: complete
- Owner: parent
- Depends on: T1, T2, T3
- Write set: `.claude/PRPs/plans/P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP.plan.md`, `.claude/PRPs/evidence/P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP.md`
- Acceptance: PRP validation, focused tests, allowlist check, and diff checks pass; evidence records exact commands and outcomes.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP.plan.md`
- Evidence: Focused suite `11 passed`; syntax, PRP, allowlist, and diff checks pass. Broader suite result and unrelated stale-style-hash failures are recorded in the P19 evidence note.

## Verification

```powershell
python -m pytest content/video_engine/tests/test_video_review_learning.py -q
python scripts/prp_validate.py .claude/PRPs/plans/P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP.plan.md
python scripts/configure_codex_skill_allowlist.py --check
git diff --check
```

## Evidence And Handoff

Commands, results, deviations, and the final artifact list are recorded under `.claude/PRPs/evidence/P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP.md`. The review compiler does not mutate skills or memory; promotion remains a later operator-approved action.
