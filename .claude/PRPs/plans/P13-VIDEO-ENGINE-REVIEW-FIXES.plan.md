---
id: P13-VIDEO-ENGINE-REVIEW-FIXES
title: Video Engine Review Fixes
status: complete
operation: bugfix
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-28
updated: 2026-07-28
---

# P13 Video Engine Review Fixes

## Summary

Resolve the four actionable findings from the uncommitted P13 video-engine review:
use measured narration timing after Gate A, make QC verify final video files, enforce
Gate-A validation inside the pipeline service boundary, and include the video-engine
tests in the repository's default pytest collection.

The implementation preserves the existing authoring contract: storyboard
`timing.target_s` remains an estimate used by pre-Gate-A guards, while persisted
`audio/scene_<id>.words.json` artifacts become the sole post-Gate-A timing clock.

## Intent And Acceptance

### Intent

As the video-engine operator, I need approvals, rendering, QC, and packaging to use
the same evidence-backed contracts so a valid provider-backed run cannot fail because
TTS differs from a WPM estimate, and a missing or corrupt final video cannot pass Gate B.

### Acceptance

- A storyboard whose `target_s` values differ materially from measured TTS durations
  can composite, package, and pass duration QC when the final videos are within 2% of
  the measured audio timeline.
- Compositor drift checks, package chapter offsets, package `duration_s`, and
  `VideoObject.duration` all derive from ordered `words.json` durations plus
  storyboard padding.
- Missing, malformed, non-finite, non-positive, duplicate, or unexpected scene timing
  artifacts fail closed after Gate A; no post-Gate-A production path silently falls
  back to `target_s`.
- QC requires every selected render profile's `video/<profile>/final.mp4`, probes each
  final independently, and fails on a missing, unprobeable, or >2%-drifted output even
  when an earlier render manifest remains valid.
- `VideoPipeline.approve(run_id, "a")` re-runs the storyboard guard before mutating
  gate state. Invalid edits leave the run at `awaiting_gate_a` with Gate A pending.
- `python -m pytest --collect-only -q` discovers both `tests/` and
  `content/video_engine/tests/` without explicit path arguments.
- Focused video-engine tests and the full repository suite pass with no network or
  paid-provider calls.

## Scope

- Add one neutral measured-timing helper under `content/video_engine/src/`.
- Replace post-Gate-A storyboard-estimate duration calculations in compositor,
  packaging, and QC.
- Make final MP4 existence and ffprobe duration part of deterministic Gate-B QC.
- Move the Gate-A validation invariant into `VideoPipeline` while preserving
  CLI-friendly validation output.
- Expand pytest discovery to include the video-engine test root.
- Add focused regression tests for estimate/measured divergence, final-artifact
  failures, direct pipeline approval, and default test collection.

## Not Building

- No storyboard schema or pre-Gate-A authoring-budget changes. `target_s` remains valid
  for storyboard arc, pacing, and maximum-duration guards before narration exists.
- No mutation of `storyboard.json` with measured values.
- No TTS provider calls, new voices, cache redesign, or credential handling.
- No Manim scene redesign, transition redesign, upload API, dashboard, or deployment.
- No relaxation of the existing 1% render-unit or 2% final-output drift limits.
- No completion claim for the provider-backed P13 thin slice or its human Gate A/B
  approvals.

## Human Gates

- The parent must approve this draft before implementation begins.
- These fixes do not authorize paid ElevenLabs calls, publishing, commits, pushes, or
  deployments.
- Regression tests may simulate Gate A/B decisions, but they do not replace the
  operator approvals required by the blocked P13 end-to-end run.

## Mandatory Reads

- `AGENTS.md`
- `content/video_engine/AGENTS.md`
- `docs/content-video-engine/03-SYSTEM-ARCHITECTURE.md` sections 3, 4, 7, and 9
- `docs/content-video-engine/04-STORYBOARD-CONTRACT.md` sections 3 and 4
- `content/video_engine/configs/storyboard.schema.json` timing definition
- `content/video_engine/src/services/audio_synth.py`
- `content/video_engine/src/services/manim_render.py`
- `content/video_engine/src/services/compositor.py`
- `content/video_engine/src/services/packaging.py`
- `content/video_engine/src/guards/qc_checks.py`
- `content/video_engine/src/guards/storyboard_guard.py`
- `content/video_engine/src/pipeline.py`
- `content/video_engine/cli.py`
- `pytest.ini`
- Focused tests named in each task slice

## Execution Path

1. Approve this PRP and change its status to `approved`, then `running`.
2. Implement the measured-audio timeline contract first; downstream slices may consume
   it but must not duplicate duration parsing.
3. Update final-artifact QC after the timing contract is available.
4. Implement the independent Gate-A approval invariant and pytest-discovery fix in
   parallel only if their write sets remain disjoint.
5. Run focused tests after each slice, then the complete video-engine and repository
   suites.
6. Request an independent read-only `reviewer` pass over the integrated diff.
7. Record exact commands and verdicts here; move to `complete` only when all acceptance
   items are evidenced. Provider-backed P13 blockers remain in the original plan.

## Patterns To Mirror

- Mirror `audio_synth.py`'s persisted
  `{"scene_id", "duration_s", "words"}` artifact contract.
- Mirror `manim_render._duration_from_words()` for the rule that measured narration plus
  explicit padding is the render clock, but centralize strict shared parsing rather than
  copying it into more consumers.
- Keep measured state in artifacts as required by `content/video_engine/AGENTS.md`;
  never write it into the approved storyboard.
- Keep validation at the service boundary: the CLI may preflight for friendly output,
  but `VideoPipeline.approve()` owns the approval invariant for every caller.
- Preserve dependency injection for subprocess probes and approval validators so fast
  tests remain deterministic and do not require real media.
- Follow existing `StageOutput.summary` and QC report shapes; add explicit evidence
  fields rather than replacing unrelated fields.

## Task Slices

### T1: Centralize the measured audio timeline
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/src/timing.py`, `content/video_engine/src/services/compositor.py`, `content/video_engine/src/services/packaging.py`, `content/video_engine/tests/test_timing.py`, `content/video_engine/tests/test_compositor.py`, `content/video_engine/tests/test_packaging.py`
- Acceptance: A strict helper returns ordered per-scene audio duration, padding, start, and end values from `words.json`; compositor compares final output with its total; package chapters and JSON-LD use the same timeline; a fixture with measured durations differing by at least 10% from `target_s` succeeds when output matches measured audio; missing or malformed timing artifacts fail with scene-specific errors.
- Validate: `python -m pytest content/video_engine/tests/test_timing.py content/video_engine/tests/test_compositor.py content/video_engine/tests/test_packaging.py -q`
- Evidence: Added strict `timing.py` artifact parsing and switched compositor drift/audio filters plus packaging chapters/JSON-LD to the measured timeline. Regression values use 6.0s and 3.0s against 5.0s authoring estimates, proving 20%/40% divergence. Parent aligned zero-length word timing with `audio_synth.py`; `python -m pytest content/video_engine/tests/test_timing.py content/video_engine/tests/test_compositor.py content/video_engine/tests/test_packaging.py -q` → 22 passed in 0.77s.

### T2: Make QC verify selected final videos
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/src/guards/qc_checks.py`, `content/video_engine/tests/test_qc_checks.py`
- Acceptance: Duration QC uses the shared measured timeline, requires every explicitly selected profile's `final.mp4`, probes each final through an injectable duration probe, records expected/actual/drift details, and fails for missing, unprobeable, or >2%-drifted finals regardless of stale manifest content; the fast unit tests use placeholder files and a fake probe.
- Validate: `python -m pytest content/video_engine/tests/test_qc_checks.py -q`
- Evidence: QC now uses `load_measured_timeline`, requires and probes every compositor-selected `video/<profile>/final.mp4`, and records measured expected/actual/drift evidence. Tests cover a 20% target/measured divergence with stale manifests, two-profile pass, missing final, unprobeable final, and >2% final drift. `python -m pytest content/video_engine/tests/test_qc_checks.py -q` → 8 passed in 0.21s on parent rerun.

### T3: Enforce Gate-A validation in the pipeline
- Status: complete
- Owner: junior_developer
- Depends on: none
- Write set: `content/video_engine/src/pipeline.py`, `content/video_engine/cli.py`, `content/video_engine/tests/test_pipeline.py`
- Acceptance: `VideoPipeline.approve(..., "a")` invokes the storyboard guard before changing or persisting gate/run state; all violations are returned through a specific approval error; invalid approval leaves status, gate state, and downstream events unchanged; valid direct and CLI approvals retain existing behavior; isolated orchestration tests can inject a deterministic validator without weakening the production default.
- Validate: `python -m pytest content/video_engine/tests/test_pipeline.py -q`
- Evidence: Added pipeline-owned validation with `VideoPipelineGateApprovalError`, production-default guard behavior, validator injection for isolated orchestration tests, and CLI JSON handling. `python -m pytest content/video_engine/tests/test_pipeline.py -q` → 8 passed in 0.48s on parent rerun; rejected approval preserved the persisted run and event list exactly.

### T4: Include video-engine tests in default discovery
- Status: complete
- Owner: speedster
- Depends on: none
- Write set: `pytest.ini`
- Acceptance: `testpaths` includes both repository test roots, existing marker declarations remain intact, and default collection contains node IDs from both `tests/` and `content/video_engine/tests/`.
- Validate: `python -m pytest --collect-only -q`
- Evidence: `python -m pytest --collect-only -q` → 488 tests collected in 0.72s; output contained node IDs under both `tests/` and `content/video_engine/tests/`. Parent reviewed the `pytest.ini`-only diff and confirmed the marker block is unchanged.

### T5: Integrate, regress, and independently review
- Status: complete
- Owner: parent
- Depends on: T1, T2, T3, T4
- Write set: `content/video_engine/tests/test_integration.py`, `.claude/PRPs/plans/P13-VIDEO-ENGINE-REVIEW-FIXES.plan.md`
- Acceptance: The mocked end-to-end pipeline uses measured audio durations that intentionally differ from storyboard estimates, reaches `packaged`, emits existing final/package/QC artifacts, the full suites pass, and an independent reviewer reports no unresolved actionable correctness or regression findings.
- Validate: `python -m pytest content/video_engine/tests -q && python -m pytest -q`
- Evidence: The mocked provider emits narration durations 20% above `target_s`; render, compositor, packaging, and QC follow the measured timeline and the FFmpeg integration reaches `packaged`. `python -m pytest content/video_engine/tests/test_integration.py -q` → 1 passed in 5.74s; `python -m pytest content/video_engine/tests -q` → 81 passed, 2 skipped in 7.52s. The required existing Python 3.11 environment ran Manim/FFmpeg coverage with `.\.venv\Scripts\python.exe -m pytest -q` → 505 passed, 2 warnings in 75.56s. Independent read-only reviewer verdict: no actionable correctness, contract-drift, security/path-handling, or regression findings.

## Verification

Run in dependency order from the exact worktree root:

```powershell
python -m pytest content/video_engine/tests/test_timing.py content/video_engine/tests/test_compositor.py content/video_engine/tests/test_packaging.py -q
python -m pytest content/video_engine/tests/test_qc_checks.py -q
python -m pytest content/video_engine/tests/test_pipeline.py -q
python -m pytest --collect-only -q
python -m pytest content/video_engine/tests -q
python -m pytest -q
python scripts/prp_validate.py .claude/PRPs/plans/P13-VIDEO-ENGINE-REVIEW-FIXES.plan.md
```

Collection evidence must show node IDs under both configured roots. Test evidence must
preserve exact pass/fail/skip counts. Do not use compressed output for final verdicts.
No verification command may call ElevenLabs or publish externally.

## Evidence And Handoff

- Record each slice's exact command, verdict, and affected artifact paths in its
  `Evidence` field.
- T1 evidence must include the regression values proving `target_s` and measured audio
  differ while measured-clock validation passes.
- T2 evidence must include missing-final and drifted-final failures plus a passing
  multi-profile case.
- T3 evidence must show the persisted run remains unchanged after rejected approval.
- T4 evidence must show default collection from both test roots.
- T5 evidence must include full-suite counts and the independent review result.
- The parent reviews every delegated diff and owns integration. Do not stage, commit,
  push, or mark the original P13 provider-backed plan complete without separate
  authorization and its remaining human/provider evidence.

Final handoff: all five fixes slices are complete and parent-reviewed. The original
P13 provider-backed plan remains blocked on its separately authorized credentials,
paid call, source record, and operator Gate A/B evidence; this fixes PRP does not
change those blockers.
