---
id: P13-VISUAL-V2-AUTOMATION
title: P13 Visual V2 Automation
status: complete
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-30
updated: 2026-07-30
---

# P13 Visual V2 Automation

## Summary

Replace the rejected repeated-pose video path with a rights-aware, evidence-backed visual
automation pipeline. Implement the operator-approved eight slices in dependency order:
technique evidence, shot planning, articulated BJJ action, multi-function coverage, a
pre-Gate-A animatic, visual QC, a Remotion editorial compositor, and deterministic sound design.

## Intent And Acceptance

The corpus-to-video automation must produce a storyboard and draft whose visuals follow the
technique and story instead of repeating whole-pose fades.

Acceptance:

- A rights-cleared technique reference sidecar validates and persists as a job artifact without
  changing the canonical transcript fact contract.
- Every instructional beat resolves to a visual function and reviewed
  `state_from -> action -> state_to` recipe.
- `BJJActionScene` renders a persistent, color-coded, articulated cast and exposes deterministic
  action phases rather than fading complete pose SVGs.
- The Armbar path includes result preview, wide setup, at least two detail cut-ins,
  wrong/right comparison, leverage reveal, and held result.
- Gate A receives a low-resolution animatic and shot/contact sheet before any paid provider call.
- QC detects missing coverage, repeated framing/function, unresolved references, continuity
  errors, visual-cadence breaches, and missing final artifacts.
- Remotion can assemble rendered scene clips, captions, overlays, and supported transitions
  from an immutable editorial manifest; FFmpeg remains the final audio-normalization boundary.
- Deterministic movement/contact/aftermath sound cues are scheduled from action phases; music
  remains optional.
- Focused tests and the complete repository suite pass without provider or publishing calls.

## Scope

- `content/video_engine/` contracts, stages, scenes, assets, guards, compositor, and tests.
- A local Remotion subproject owned by the video engine.
- Documentation and PRP evidence needed to operate the new path.
- Backwards compatibility for existing non-BJJ scene classes and old valid storyboards.

## Not Building

- No training or fine-tuning on downloaded YouTube videos.
- No Midjourney, Kling, or other paid visual-provider integration.
- No automated technique approval, Gate A, Gate B, publishing, commit, or push.
- No attempt to reproduce third-party characters, exact choreography, audio, or style.
- No photorealistic anatomy generation.

## Human Gates

- The operator's instruction to implement this plan approves local code, dependencies, tests,
  and deterministic local renders.
- Gate A and Gate B remain operator actions.
- Provider calls, publishing, commits, and pushes remain outside this plan.
- Reference manifests must declare an operator-owned, licensed, or internal source and reviewed
  mechanics before they may drive instructional rendering.

## Mandatory Reads

- `AGENTS.md`
- `content/video_engine/AGENTS.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `docs/content-video-engine/09-YOUTUBE-REFERENCE-PACK-LEARNINGS.md`
- `docs/content-video-engine/03-SYSTEM-ARCHITECTURE.md` section 5.1
- `docs/content-video-engine/06-SCRIPT-TRANSFORMATION-SPEC.md` section 4
- `content/video_engine/src/pipeline.py`
- `content/video_engine/src/services/ingest.py`
- `content/video_engine/src/services/script_transform.py`
- `content/video_engine/src/services/storyboard_build.py`
- `content/video_engine/src/services/manim_render.py`
- `content/video_engine/src/services/compositor.py`
- `content/video_engine/src/guards/storyboard_guard.py`
- `content/video_engine/src/guards/qc_checks.py`
- relevant focused tests

## Execution Path

1. Validate this plan and mark it running.
2. Implement technique evidence before shot planning.
3. Implement the articulated scene before wiring storyboard coverage.
4. Add animatic evidence before changing Gate A readiness.
5. Add visual QC before editorial polish.
6. Add Remotion as an optional, fail-closed editorial renderer with a deterministic manifest.
7. Add sound cues without relaxing narration timing or loudness contracts.
8. Integrate stage order, run focused tests, run a low-quality smoke render, run the full suite,
   and obtain an independent read-only review.

## Patterns To Mirror

- Persist stage artifacts under `runtime/jobs/<job_id>/`; never mutate `storyboard.json` after
  Gate A.
- Use `StageOutput` summaries and explicit pipeline events.
- Validate all references before provider or render spend.
- Keep the canonical corpus transcript contract separate from rights/provenance sidecars.
- Use measured narration timing as the post-Gate-A clock.
- Keep Manim deterministic and use Remotion only as the editorial/layering boundary.
- Preserve dependency injection so unit tests need neither Manim nor Chromium.

## Task Slices

### T1: Technique evidence sidecar and action vocabulary
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/configs/technique_visual_manifest.schema.json`, `content/video_engine/src/services/technique_manifest.py`, `content/video_engine/src/assets/references/README.md`, `content/video_engine/tests/test_technique_manifest.py`
- Acceptance: A service discovers or receives a slug-matched sidecar, validates rights and reviewed action states, writes `technique_manifest.json`, and fails with per-action errors for missing state, contact, motion path, or permission.
- Validate: `python -m pytest content/video_engine/tests/test_technique_manifest.py -q`
- Evidence: `8 passed` across manifest and shot-plan focused tests; Armbar manifest persisted with 6 reviewed actions and 1 internal corpus reference in run `1373fa59-3dec-44c0-bcc0-b67bfe1d5baf`.

### T2: Deterministic shot planning
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/src/services/shot_plan.py`, `content/video_engine/tests/test_shot_plan.py`
- Acceptance: Transcript beats and the technique manifest compile to `shot_plan.json` with visual function, style, cast, action/state, camera, overlays, transition motif, sound cues, and provenance; unresolved instructional beats fail closed.
- Validate: `python -m pytest content/video_engine/tests/test_shot_plan.py -q`
- Evidence: the same run wrote `shot_plan.json` with 12 shots, 11 instructional shots, explicit state/action/contact/camera/function/sound/provenance, and zero provider cost.

### T3: Articulated BJJ action scene
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/src/scenes/bjj_action.py`, `content/video_engine/src/assets/cast/`, `content/video_engine/tests/test_bjj_action_scene.py`
- Acceptance: A deterministic layered vector cast exposes named joints, body ownership, z-order, contact anchors, and anticipation/action/contact/recovery phases for one complete Armbar action chain; direct tests run without Manim.
- Validate: `python -m pytest content/video_engine/tests/test_bjj_action_scene.py -q`
- Evidence: `5 passed` in the focused scene contract plus a successful real `landscape_draft` Manim render using the persistent color-coded cast.

### T4: Multi-function storyboard coverage
- Status: complete
- Owner: parent
- Depends on: T2, T3
- Write set: `content/video_engine/src/models.py`, `content/video_engine/configs/storyboard.schema.json`, `content/video_engine/configs/style_presets.json`, `content/video_engine/src/services/script_transform.py`, `content/video_engine/src/services/storyboard_build.py`, `content/video_engine/src/guards/storyboard_guard.py`, `content/video_engine/src/scenes/__init__.py`, `content/video_engine/tests/test_storyboard_build.py`, `content/video_engine/tests/test_storyboard_guard.py`, `content/video_engine/tests/test_scene_contracts.py`
- Acceptance: Corpus transformation and storyboard construction consume the shot plan, register `BJJActionScene`, emit the required shot functions and action recipes, and reject repeated/missing coverage while retaining legacy storyboard compatibility.
- Validate: `python -m pytest content/video_engine/tests/test_storyboard_build.py content/video_engine/tests/test_storyboard_guard.py content/video_engine/tests/test_scene_contracts.py -q`
- Evidence: run `1373fa59-3dec-44c0-bcc0-b67bfe1d5baf` produced a guarded 12-scene storyboard containing result preview, wide setup, two contact close-ups, mechanic transitions, wrong/right comparison, force diagram, result hold, and CTA.

### T5: Pre-Gate-A animatic evidence
- Status: complete
- Owner: parent
- Depends on: T4
- Write set: `content/video_engine/src/services/animatic.py`, `content/video_engine/src/pipeline.py`, `content/video_engine/cli.py`, `content/video_engine/tests/test_animatic.py`, `content/video_engine/tests/test_pipeline.py`
- Acceptance: The pipeline renders a local low-resolution animatic plus shot strip and review packet before `awaiting_storyboard_approval`; Gate A cannot approve when required animatic evidence is absent; no provider call occurs.
- Validate: `python -m pytest content/video_engine/tests/test_animatic.py content/video_engine/tests/test_pipeline.py -q`
- Evidence: the run reached `awaiting_gate_a` with `animatic/motion-preview.mp4`, `animatic/shot-strip.png`, and `animatic/review-packet.json`; the packet records `renderer=manim`, 12 scenes, and zero provider cost.

### T6: Visual-quality QC
- Status: complete
- Owner: parent
- Depends on: T4
- Write set: `content/video_engine/src/guards/visual_qc.py`, `content/video_engine/src/guards/qc_checks.py`, `content/video_engine/tests/test_visual_qc.py`, `content/video_engine/tests/test_qc_checks.py`
- Acceptance: Deterministic checks cover shot-function diversity, repetition, state/action completeness, cast continuity, provenance, cadence, layout-safe zones, and final-to-plan coverage; technique correctness remains a human Gate-B item.
- Validate: `python -m pytest content/video_engine/tests/test_visual_qc.py content/video_engine/tests/test_qc_checks.py -q`
- Evidence: `14 passed` across visual-QC and shared QC focused tests; Gate A evaluates visual coverage before approval and Gate B rechecks final-plan coverage.

### T7: Remotion editorial compositor
- Status: complete
- Owner: implementation_luna
- Depends on: T4
- Write set: `content/video_engine/editor/`, `content/video_engine/src/services/editorial.py`, `content/video_engine/tests/test_editorial.py`, `.gitignore`
- Acceptance: A pinned local Remotion project consumes `edit_manifest.json`, sequences and layers scene clips/captions/overlays with supported transitions, and can be invoked through an injected runner; tests validate commands and manifests without Chromium.
- Validate: `python -m pytest content/video_engine/tests/test_editorial.py -q`
- Evidence: `6 passed` in editorial tests; `npm ci --ignore-scripts` installed 21 pinned packages with 0 vulnerabilities; `npm run typecheck` and `npm run build` passed.

### T8: Deterministic sound design and integration
- Status: complete
- Owner: parent
- Depends on: T5, T6, T7
- Write set: `content/video_engine/configs/sound_palette.json`, `content/video_engine/src/services/sound_design.py`, `content/video_engine/src/services/compositor.py`, `content/video_engine/src/pipeline.py`, `content/video_engine/tests/test_sound_design.py`, `content/video_engine/tests/test_compositor.py`, `content/video_engine/tests/test_integration.py`, `.claude/PRPs/plans/P13-VISUAL-V2-AUTOMATION.plan.md`
- Acceptance: Action phases compile to an immutable sound manifest with movement/contact/aftermath cues, the editorial/compositor path mixes available licensed local cues without changing the narration clock, all eight slices run in dependency order, and mocked end-to-end automation reaches Gate B.
- Validate: `python -m pytest content/video_engine/tests/test_sound_design.py content/video_engine/tests/test_compositor.py content/video_engine/tests/test_integration.py -q`
- Evidence: sound/compositor focused tests passed; mocked provider/render integration reached Gate B and then packaged; complete repository verification is `555 passed, 2 warnings`.

## Verification

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P13-VISUAL-V2-AUTOMATION.plan.md
python -m pytest content/video_engine/tests/test_technique_manifest.py -q
python -m pytest content/video_engine/tests/test_shot_plan.py -q
python -m pytest content/video_engine/tests/test_bjj_action_scene.py -q
python -m pytest content/video_engine/tests/test_storyboard_build.py content/video_engine/tests/test_storyboard_guard.py content/video_engine/tests/test_scene_contracts.py -q
python -m pytest content/video_engine/tests/test_animatic.py content/video_engine/tests/test_pipeline.py -q
python -m pytest content/video_engine/tests/test_visual_qc.py content/video_engine/tests/test_qc_checks.py -q
python -m pytest content/video_engine/tests/test_editorial.py -q
python -m pytest content/video_engine/tests/test_sound_design.py content/video_engine/tests/test_compositor.py content/video_engine/tests/test_integration.py -q
python -m pytest content/video_engine/tests -q
python -m pytest -q
```

No validation command may call ElevenLabs, publish, or use a paid visual provider.

## Evidence And Handoff

- Record every exact command and verdict in the relevant slice.
- Preserve manifests, animatic packet paths, low-quality render paths, and QC report paths.
- Obtain independent reviewer findings before marking complete.
- Do not stage, commit, push, publish, or approve Gate A/B in this plan.

Final local evidence:

- Run: `.context/p13-visual-v2-final2/jobs/1373fa59-3dec-44c0-bcc0-b67bfe1d5baf`
- Motion animatic: `animatic/motion-preview.mp4` (854x480, 15 fps)
- Shot strip: `animatic/shot-strip.png`
- Review packet: `animatic/review-packet.json`
- Full suite: `555 passed, 2 warnings in 82.83s`
- Independent review completed; its cached-timing integrity and early packaging-URL findings were fixed with focused regression tests.
- No ElevenLabs, paid visual provider, publish, commit, or push call was made.

Post-plan operational render:

- Gate-A-approved run: `.context/p13-visual-v2-final2/jobs/1373fa59-3dec-44c0-bcc0-b67bfe1d5baf`
- Gate B state: `awaiting_gate_b`; QC `pass` across 14 checks.
- Landscape: `video/landscape_final/final.mp4` (1920x1080, 60 fps, 54.002s).
- Vertical: `video/vertical_final/final.mp4` (1080x1920, 30 fps, 54.002s).
- Audio: 923 ElevenLabs characters, estimated `$0.1846`; final measured loudness `-14.11 LUFS`.
- Production retries exposed and fixed the missing pinned `@remotion/cli`, Remotion public-directory
  asset resolution, Windows UTF-8 subprocess decoding, and raw-manifest metadata selection.
- Full repository verification after those fixes: `556 passed, 2 warnings in 74.47s`.
- No corpus footage, publishing, registry write, staging, commit, or push occurred.
