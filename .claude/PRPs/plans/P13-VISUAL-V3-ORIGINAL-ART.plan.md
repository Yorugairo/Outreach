---
id: P13-VISUAL-V3-ORIGINAL-ART
title: P13 Visual V3 Original Art And Explanation System
status: review
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-30
updated: 2026-07-30
---

# P13 Visual V3 — Original Art and Explanation System

## Summary

Convert abstract lessons from the YouTube Reference Pack into an original, deterministic Combat
Science visual language and prove it with an Armbar V3 style board and animatic. Study sources
remain research-only and can never become renderer inputs.

## Intent And Acceptance

- Versioned `reference_study.v1`, `art_bible.v1`, and `visual_treatment.v1` contracts validate.
- Renderer-facing artifacts contain internal style atoms, never creator names, YouTube IDs,
  study paths, source frames, or imitation prompts.
- Pipeline v3 adds art-direction resolution, treatment compilation, a six-frame style board, and
  a human Visual Direction Gate before the motion animatic and Gate A.
- BJJ bodies use filled cutout anatomy and preserve ownership through occlusion and close-ups.
- Armbar V3 covers all eight composition functions, two contact macros, a matched wrong/right
  comparison, and two living-diagram transitions.
- Visual QC proves hashes, coverage, provenance separation, continuity, safe zones, diagram
  resolution, treatment coverage, signature diversity, and perceptual-frame diversity.
- Focused tests, real low-resolution smoke renders, Remotion checks, and the full suite pass
  without paid-provider calls.

## Scope

- `content/video_engine/` contracts, configuration, services, scenes, guards, CLI, and tests.
- Curated abstract study and original Combat Science art bible.
- Armbar V3 style-board and animatic evidence under a local `.context` artifact root.
- Compatibility for snapshotted v1/v2 jobs and legacy storyboards.

## Not Building

- No third-party frame ingestion, tracing, model training, or creator-style imitation.
- No vintage/history/comic renderer, paid image provider, new paid narration, publishing,
  registry write, staging, commit, or push.
- No automatic Visual, Gate A, or Gate B approval.

## Human Gates

- Visual approval requires six still roles and a rubric where all six dimensions score at least
  4/5 against the current art-bible hash.
- Gate A remains motion/story approval; Gate B remains final publication approval.
- The build may produce the style board and animatic but may not grant any human gate.

## Mandatory Reads

- `AGENTS.md`
- `content/video_engine/AGENTS.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `docs/content-video-engine/09-YOUTUBE-REFERENCE-PACK-LEARNINGS.md`
- `.claude/PRPs/plans/P13-VISUAL-V2-AUTOMATION.plan.md`
- relevant source and focused tests

## Execution Path

1. Add and validate the three contracts and original curated artifacts.
2. Resolve immutable art direction and compile deterministic per-shot treatments.
3. Implement the filled cast and eight composition functions.
4. Render a six-still style board and stop at the Visual Direction Gate.
5. Extend motion rendering and visual QC, then render a low-resolution Armbar V3 animatic.
6. Run independent review, comparison evidence, focused validation, and the full suite.

## Patterns To Mirror

- Persist immutable artifacts beneath the job directory and hash canonical JSON.
- Keep source-study provenance and renderable asset provenance in separate domains.
- Resolve instructional mechanics only from reviewed technique manifests.
- Keep Manim deterministic and Remotion editorial; narration remains the timing authority.
- Preserve pipeline stage snapshots for legacy resume behavior.

## Task Slices

### T1: Contracts, validators, and curated art direction
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/configs/reference_study.schema.json`, `content/video_engine/configs/art_bible.schema.json`, `content/video_engine/configs/visual_treatment.schema.json`, `content/video_engine/configs/studies/`, `content/video_engine/configs/art_bibles/`, `content/video_engine/src/services/art_direction.py`, `content/video_engine/tests/test_art_direction.py`
- Acceptance: all three contracts validate, immutable hashes are stable, the curated study is non-renderable, and prohibited provenance/imitation language fails closed.
- Validate: `python -m pytest content/video_engine/tests/test_art_direction.py -q`
- Evidence: `test_art_direction.py` 6 passed; both curated contracts validate through
  `validate-study`/`validate-art-bible`; current art-bible SHA-256 is
  `e0621e4f69ed04cd081ba737d12b430d8614690a4fb57519d20f9e289471b978`.

### T2: Filled cast and composition grammar
- Status: complete
- Owner: implementation_luna
- Depends on: T1 contract shape only
- Write set: `content/video_engine/src/scenes/bjj_action.py`, `content/video_engine/src/scenes/combat_science.py`, `content/video_engine/src/scenes/__init__.py`, `content/video_engine/tests/test_bjj_action_scene.py`, `content/video_engine/tests/test_combat_science_scene.py`
- Acceptance: filled anatomical masses, context insets, matched comparison panels, living diagrams, and all eight composition functions are deterministic and mechanically anchored.
- Validate: `python -m pytest content/video_engine/tests/test_bjj_action_scene.py content/video_engine/tests/test_combat_science_scene.py -q`
- Evidence: post-polish scene verification 14 passed, 1 expected render-platform skip; a real
  480p15 Manim smoke render completed at
  `.context/p13-visual-v3-render-smoke2/video/landscape_draft/scene_1.mp4`
  with a probed duration of 10.466667 seconds. The cast uses tapered filled masses plus explicit
  hand and foot layers; joint anchors remain metadata-only.

### T3: Style board, visual gate, and concept QC
- Status: complete
- Owner: implementation_luna
- Depends on: T1 contract shape
- Write set: `content/video_engine/src/services/style_board.py`, `content/video_engine/src/guards/visual_direction.py`, `content/video_engine/src/guards/visual_qc.py`, `content/video_engine/tests/test_style_board.py`, `content/video_engine/tests/test_visual_direction.py`, `content/video_engine/tests/test_visual_qc.py`
- Acceptance: six required stills and rubric validation are enforced; QC covers source leakage, hash integrity, composition/treatment coverage, signatures, perceptual duplicates, continuity, safe zones, and reviewed overlay anchors.
- Validate: `python -m pytest content/video_engine/tests/test_style_board.py content/video_engine/tests/test_visual_direction.py content/video_engine/tests/test_visual_qc.py -q`
- Evidence: focused V3 gate/QC verification passed; the authoritative six-still board is
  `.context/p13-visual-v3-candidate/bbc55518-8b38-4549-a460-19be3414948a/style_board/style_board.png`.
  Its review packet records six distinct perceptual hashes, zero provider calls, and no approval.

### T4: Pipeline v3 and CLI integration
- Status: complete
- Owner: parent
- Depends on: T1, T3
- Write set: `content/video_engine/src/models.py`, `content/video_engine/src/pipeline.py`, `content/video_engine/src/services/shot_plan.py`, `content/video_engine/src/services/storyboard_build.py`, `content/video_engine/configs/channels/combat-science.json`, `content/video_engine/configs/storyboard.schema.json`, `content/video_engine/cli.py`, integration tests
- Acceptance: V3 jobs resolve art direction, compile treatments, render a style board, stop at Visual Gate, and resume in the documented order; legacy jobs retain their snapshotted order.
- Validate: focused pipeline, CLI, storyboard, and integration tests.
- Evidence: V3-focused pipeline/integration group passed 36 tests. Armbar pilot job
  `bbc55518-8b38-4549-a460-19be3414948a` stopped at `awaiting_visual_gate` with
  `visual_gate_status: pending`; all other corpus slugs retain V2 selection.

### T5: Armbar proof, review, and verification
- Status: in_progress
- Owner: parent
- Depends on: T2, T3, T4
- Write set: V3 runtime evidence, comparison evidence, this PRP
- Acceptance: real low-resolution style board and animatic exist; no gate is auto-approved; independent review is addressed; full repository verification passes.
- Validate: video-engine suite, Remotion typecheck/build, full repository suite.
- Evidence: authoritative Armbar V3 style board is ready for human Visual Direction review.
  A separate synthetic gate-flow smoke job produced a low-resolution animatic without paid
  providers, but it is not treated as human approval or as the release candidate. Post-change
  verification: video engine `150 passed, 3 skipped`; Remotion typecheck/build passed; repository
  `582 passed, 3 skipped`; PRP validation passed. Independent review reported no actionable code
  findings. T5 remains open until the operator approves the fresh candidate's Visual Direction
  Gate, after which the authoritative animatic can be rendered for Gate A.

## Verification

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P13-VISUAL-V3-ORIGINAL-ART.plan.md
python -m pytest content/video_engine/tests/test_art_direction.py -q
python -m pytest content/video_engine/tests/test_bjj_action_scene.py content/video_engine/tests/test_combat_science_scene.py -q
python -m pytest content/video_engine/tests/test_style_board.py content/video_engine/tests/test_visual_direction.py content/video_engine/tests/test_visual_qc.py -q
python -m pytest content/video_engine/tests/test_pipeline.py content/video_engine/tests/test_integration.py -q
python -m pytest content/video_engine/tests -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run build
python -m pytest -q
```

## Evidence And Handoff

Record exact commands, verdicts, artifact paths, deviations, and review findings here. No
provider call, gate approval, publish, registry write, staging, commit, or push is authorized.

### Handoff checkpoint

- Authoritative candidate:
  `.context/p13-visual-v3-candidate/bbc55518-8b38-4549-a460-19be3414948a`
- Current state: `awaiting_visual_gate`; Visual, Gate A, and Gate B are all pending.
- Visual approval requires the six canonical scores at 4/5 or higher against art-bible hash
  `e0621e4f69ed04cd081ba737d12b430d8614690a4fb57519d20f9e289471b978`.
- After human Visual approval, the approval command resumes the job, generates the motion
  animatic, and stops at Gate A.

### Verification evidence

- `python scripts/prp_validate.py .claude/PRPs/plans/P13-VISUAL-V3-ORIGINAL-ART.plan.md` → `PASS`
- `python -m pytest content/video_engine/tests/test_art_direction.py -q` → `6 passed`
- `python -m pytest content/video_engine/tests/test_bjj_action_scene.py content/video_engine/tests/test_combat_science_scene.py -q` → `14 passed, 1 skipped`
- `python -m pytest content/video_engine/tests/test_style_board.py content/video_engine/tests/test_visual_direction.py content/video_engine/tests/test_visual_qc.py -q` → `15 passed`
- `python -m pytest content/video_engine/tests/test_pipeline.py content/video_engine/tests/test_integration.py -q` → `15 passed`
- `python -m pytest content/video_engine/tests -q` → `150 passed, 3 skipped`
- `npm --prefix content/video_engine/editor run typecheck` → success
- `npm --prefix content/video_engine/editor run build` → success
- `python -m pytest -q` → `582 passed, 3 skipped`
- `python -m content.video_engine.cli --artifact-root .context/p13-visual-v3-candidate status bbc55518-8b38-4549-a460-19be3414948a`
  → status `awaiting_visual_gate`, with all three human gates pending and total provider cost `$0`.
- `.context/p13-visual-v3-candidate/bbc55518-8b38-4549-a460-19be3414948a/style_board/style_board.png`
  and `.context/p13-visual-v3-candidate/bbc55518-8b38-4549-a460-19be3414948a/style_board/review-packet.json`
  contain all six canonical roles and explicitly record `approval_granted: false`.
- Pre-gate concept QC passes all checks, including study-source leakage, current hashes,
  composition/treatment coverage, signature diversity, perceptual diversity, safe zones, and
  reviewed overlay anchors. Final-manifest coverage is correctly deferred until Gate B.
