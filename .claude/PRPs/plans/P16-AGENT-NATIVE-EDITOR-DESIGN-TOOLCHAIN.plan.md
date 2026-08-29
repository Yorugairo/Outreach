---
id: P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN
title: Agent-Native Editorial And Design Toolchain
status: running
operation: feature
risk: high
owner: parent
branch: codex/p16-agent-native-editor-design-toolchain
created: 2026-08-07
updated: 2026-08-07
---

# Agent-Native Editorial And Design Toolchain

## Summary

Turn the existing P13 deterministic editorial-motion system into the canonical
agent-native assembly, review, QA, render, and interchange path for Martial
Matters. The first production fixture is the immutable Marshall Monday 001 r1
handoff: 567.804 seconds, 1,528 timed words, 192 contiguous cues, and exactly
192 selected plates.

P16 does not replace P13 or create another timeline. It activates the dedicated
Remotion composition, adapts the Marshall package into
`editorial_motion_plan.v1`, adds immutable human revision patches, optional
quarantined trace/depth derivatives, advisory semantic/visual QA, and OTIO/NLE
exports. Human approval remains mandatory at every promotion or publication
boundary.

The compact marked risk as standard. Planning elevates implementation risk to
high because the actual work crosses a dirty-worktree boundary, merges a large
media handoff, installs network-sourced skills and optional ML environments,
introduces a browser review surface, and exports into external NLEs. The
functional scope is unchanged.

## Intent And Acceptance

### Intent

- Remove routine transfer of plates, narration, captions, and timing into a
  separate design chat.
- Let an agent deterministically compile, preview, revise, validate, render,
  and export an episode from approved local artifacts.
- Preserve the canonical audio and word timings as the only production clock.
- Retain human editorial judgment without permitting Studio, an embedding
  model, a segmentation model, an NLE, or a provider to rewrite canonical
  inputs silently.

### Acceptance

P16 is complete only when all of the following are demonstrated with artifacts:

1. `EditorialMotion` resolves to `EditorialMotionComposition`; existing
   `Editorial` and `Documentary` compositions remain unchanged and usable.
2. A locked two-shot fixture typechecks and renders with canonical audio; all
   remote URLs, absolute paths, traversal paths, and unapproved assets fail.
3. The Marshall adapter verifies the exact r1 input hashes, maps all 192 cues to
   their selected plates and exact word ranges, and emits one
   `editorial_motion_plan.v1` covering 0.000–567.804 seconds without gaps or
   overlaps.
4. A 45–60 second first-minute proof uses 8–20 complete authored cues, the
   canonical audio, job-local staged media, and passes structural P13 QC plus a
   human watch-through.
5. Official Remotion skills are project scoped, hash/version identified,
   allowlisted through the existing generator, and absent from runtime output.
6. One Studio change exports an `editorial_revision_patch.v1`, survives reload
   and recompilation, produces a changed plan hash, and appears in a before/after
   review packet. A stale patch fails closed.
7. SAM 2.1 and Depth Anything V2 Small produce quarantined derivative manifests
   for 3–5 plates without changing source files. Failed derivatives fall back to
   flat plates.
8. Deterministic visual checks and a pinned SigLIP scorer flag deliberate
   mismatch, adjacent repetition, excess blank space, accidental OCR text, and
   unsafe collisions; a human may override only with a recorded reason.
9. Native `.otio` output exactly matches the approved plan’s duration, frame
   rate, audio placement, clip order, cue IDs, word ranges, hashes, and markers.
   One FCP XML/Resolve import proof is completed or explicitly remains blocked
   at its human gate without weakening native OTIO acceptance.
10. A full Marshall 001 internal-review preview is rendered only after Gates A,
    B, and C. No publication, catalog promotion, rights approval, voice
    regeneration, or provider spend occurs.

## Scope

### Workstream 1: compositor activation

- Correct `Root.tsx` registration and preserve all existing compositions.
- Lock dependency installation to the existing `package-lock.json` and Remotion
  4.0.502.
- Add deterministic fixture props and renderer tests.

### Workstream 2: Martial edit-package adapter

- Add a generic Martial Matters adapter with Marshall Monday 001 r1 as fixture.
- Normalize the immutable cue/edit package into the existing
  `timestamped_plate_plan.v1` and job-local asset-map contracts.
- Extend the timestamped compiler to accept verified explicit word and cue
  timeline ranges so it does not proportionally retime an already word-bound
  package or discard authored pause boundaries.
- Add a narrowly scoped internal-review authorization sidecar. It permits exact
  selected files to enter a local revision render; it does not promote catalog
  assets or authorize publication.

### Workstream 3: official project-scoped Remotion skills

- Install only best-practices, markup, Studio, render, captions,
  interactivity, and multimedia guidance.
- Pin the upstream revision and record every installed file hash.
- Integrate through P15’s allowlist-first router/generator foundation after that
  foundation exists as a reviewed commit.

### Workstream 4: Studio review and immutable patches

- Add deterministic controls for approved alternates, crop/focal point, layer
  placement/depth, permitted motion/actions, permitted transitions, caption
  safe-band settings, approval state, rejection reason, and reviewer notes.
- Export a patch for CLI application; do not let browser code write arbitrary
  repository paths.

### Workstream 5: optional trace/depth preprocessing

- Isolate SAM 2.1 and Depth Anything V2 Small from the main Python environment.
- Record source/model/checkpoint/license/prompt/mask/depth/layer/QA hashes.
- Preserve complete hands, feet, weapons, microphones, crowns, and contact
  shadows where present.

### Workstream 6: semantic and visual QA

- Combine deterministic checks with a pinned local SigLIP advisory scorer.
- Bind thresholds, model identity, inputs, and reviewer decisions to the report.

### Workstream 7: OTIO and NLE interchange

- Emit native OTIO as the lossless interchange artifact.
- Emit FCP XML only through the pinned OTIO plugin and label it lossy.
- Preserve canonical source authority after external finishing.

## Not Building

- A prompt-to-video replacement for the deterministic edit.
- A second script, narration, word timing, or visual timeline.
- A full NLE clone, arbitrary keyframe editor, or per-frame LLM director.
- Automatic publication, catalog promotion, factual approval, rights approval,
  likeness approval, or provider spending.
- Automatic generation of new plates for gaps in this fixture.
- Automatic selection of contact sheets, alternates, audit frames, review
  renders, or files not listed in the immutable r1 package.
- Non-commercial Depth Anything Base/Large/Giant checkpoints.
- SAM/PyTorch/CUDA dependencies in the application’s normal Python environment.
- Direct NLE-to-canonical round trips.
- Reintroducing the Marshall puppet into in-scene episode plates. P16 assembles
  the exact approved handoff package; character/editorial changes require a
  separate approved revision artifact.

## Human Gates

### Gate 0: plan and workspace approval

- Operator approves this PRP before `prp-implement` runs.
- Approved 2026-08-07 by the user's explicit `prp-implement` invocation for
  this named plan.
- Parent confirms implementation begins from
  `f70a502ef8260a6f64535ba5559fe724d2096722` in a new isolated worktree and
  imports the handoff only from
  `ba69d1769191d9b0d463129b24dcd1afe548aa57`.
- Parent records the active dirty worktree status before and after worktree
  creation; any change to the active worktree blocks execution.

### Gate 1: licensing and internal-review authorization

- Operator records the applicable Remotion license/use classification before a
  production-scale render. The agent may not purchase or upgrade a license.
- Operator signs `editorial_review_authorization.v1` for the exact 192 r1 plate
  hashes and scope `internal_revision_render_only`.
- The authorization must state `publication_authorized: false` and
  `catalog_promotion_authorized: false`.

### Gate A: deterministic first-minute proof

- Operator watches the 45–60 second proof with sound and diagnostic render.
- Approval covers timing, crop, caption safe band, staging, and motion behavior;
  it does not approve publication or source rights.

### Gate B: Studio patch round trip

- Operator changes one shot in Studio, downloads the patch, recompiles, reloads,
  and verifies that only the declared field changed.

### Gate C: model and QA policy

- Operator approves checkpoint/license records, thresholds, and the
  human-override policy after positive and negative fixtures are reviewed.
- Any unverified or non-commercial checkpoint blocks that optional feature and
  falls back to flat plates; it does not block the canonical edit.

### Gate D: NLE import and final editorial approval

- Operator selects/opens the finishing NLE and performs the import proof.
- Operator watches the full internal preview before any later publication
  workflow. P16 ends before publish.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/agent-context/SKILL_ROUTER.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/compacts/P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.compact.md`
- `.claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md`
- `.claude/PRPs/plans/P15-MARTIAL-MATTERS-MULTI-STYLE-SKILL-SYSTEM.plan.md`
- `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md`
- `docs/content-video-engine/21-MARTIAL-MATTERS-AGENT-REPRODUCTION-RUNBOOK.md`
- `content/video_engine/src/services/editorial_motion.py`
- `content/video_engine/src/services/generated_block_images.py`
- `content/video_engine/src/services/animatic.py`
- `content/video_engine/src/guards/editorial_motion_qc.py`
- `content/video_engine/editor/src/Root.tsx`
- `content/video_engine/editor/src/EditorialMotion.tsx`
- `content/video_engine/editor/src/types.ts`
- `content/video_engine/editor/package.json`
- Marshall r1 edit package, word-timed cue sheet, canonical audio manifest, word
  timing, caption outputs, and exact selected plates at handoff commit
  `ba69d1769191d9b0d463129b24dcd1afe548aa57`
- Official Remotion skills repository and license:
  `https://github.com/remotion-dev/skills` and
  `https://github.com/remotion-dev/remotion/blob/main/LICENSE.md`
- SAM 2 official install/license sources:
  `https://github.com/facebookresearch/sam2` and
  `https://github.com/facebookresearch/sam2/blob/main/INSTALL.md`
- Depth Anything V2 official repository:
  `https://github.com/DepthAnything/Depth-Anything-V2`
- SigLIP model card:
  `https://huggingface.co/google/siglip-base-patch16-224`
- OTIO documentation and adapters:
  `https://opentimelineio.readthedocs.io/en/latest/` and
  `https://opentimelineio.readthedocs.io/en/latest/tutorials/adapters.html`
- Pinned OTIO packages:
  `https://pypi.org/project/OpenTimelineIO/0.18.1/` and
  `https://pypi.org/project/OpenTimelineIO-Plugins/0.18.1/`

## Execution Path

```text
Gate 0
  -> T1 isolated foundation + handoff import
  -> T2 dedicated compositor activation
  -> T3 Marshall adapter + exact-word compiler path
  -> Gate 1 authorization sidecar
  -> T4 first-minute proof
  -> Gate A
  -> T5 official Remotion skills (requires reviewed P15 foundation commit)
  -> T6 immutable patch engine
  -> T7 Studio review surface
  -> Gate B
  -> T8 optional trace/depth preprocessing proof
  -> T9 semantic/visual QA proof
  -> Gate C
  -> T10 native OTIO + FCP XML/Resolve proof
  -> Gate D import approval
  -> T11 full internal preview, durable docs, and independent review
  -> final human editorial gate
```

Parallelism is permitted only after T4/Gate A:

- T5 and T6 may proceed in parallel because their write sets are disjoint.
- T8 and the deterministic half of T9 may proceed in parallel after their
  schemas are stable.
- T7 depends on T6; T9 model scoring depends on T8’s isolated model-runner
  contract; T10 depends on the approved plan/patch contract.
- Protected integration, external downloads, licensing decisions, full renders,
  commits, and pushes remain with the parent.

## Patterns To Mirror

### Repository patterns

- Mirror `compile_timestamped_editorial_motion_plan()` and
  `validate_editorial_motion_plan()` for hash-bound deterministic compilation.
- Mirror `AnimaticService.render_editorial_motion_revision()` for job-local
  public staging, render props, diagnostic output, and revision packets.
- Mirror `editorial_motion_qc.py` for fail-closed paths, hashes, provider count,
  and human-review state.
- Mirror existing `configs/*.schema.json` naming and JSON Schema validation.
- Mirror CLI command registration and focused CLI tests; do not add episode
  logic to `Root.tsx` or the renderer.
- Mirror P13’s motion grammar: canonical word clock, motivated visual events,
  maximum static-hold policy, local fact surfaces, and no provider leakage.

### Adapter contract

`editorial_review_authorization.v1` contains:

- `authorization_id`, `episode_id`, `scope`, `reviewer`, `reviewed_at`, and
  `reason`;
- `base_edit_package_hash`, `canonical_audio_manifest_hash`,
  `canonical_audio_hash`, `word_timing_sha256`, and `cue_sheet_hash`;
- exactly 192 records with `cue_id`, project-relative `candidate_path`, and
  `sha256`;
- `publication_authorized: false`,
  `catalog_promotion_authorized: false`, and `artifact_hash`.

The adapter outputs `martial_editorial_adapter_manifest.v1` with input hashes,
normalized plate-plan hash, staged asset-map hash, overlay-map hash, props hash,
compiled motion-plan hash, revision ID, and contained-file hashes. The
authorization creates render eligibility only inside that revision’s job-local
asset map. It never edits source package flags or the channel asset catalog.

Each normalized timestamped block carries its source `cue_id`, exact
`start_word_index`, `end_word_index`, `timeline_start_s`, `timeline_end_s`,
narration excerpt, claim refs, overlay timing, micro-events, and selected asset
hash. New optional `explicit_word_range` and `explicit_timeline_range` fields
are accepted only when all of these conditions hold:

- the source package and cue-sheet hashes are authorized;
- the words at both indices and the normalized narration excerpt match;
- ranges are ordered, contiguous, non-overlapping, and cover word 0 through
  word 1527;
- cue time bounds exactly match the authorized cue sheet;
- each interior cue boundary equals the cue sheet's deterministic midpoint
  between the preceding word's `end_s` and the following word's `start_s`
  within tolerance; first start and final end equal the authorized audio bounds;
- the final plan covers 0.000–567.804 seconds.

When either explicit field is absent, existing proportional timestamped-plan
behavior is unchanged. The explicit timing path is reachable only through a
validated adapter authorization and copies the already-authored cue boundaries;
it is not a generic second clock. This preserves P13 compatibility while
retaining narration pauses exactly.

### Revision patch contract

`editorial_revision_patch.v1` is not arbitrary JSON Patch. It contains a base
motion-plan hash, base edit-package hash, patch ID, reviewer, timestamp, reason,
and ordered operations against stable `shot_id` values. Allowed operations are:

- choose an already approved alternate asset ID;
- set focal point or safe crop within normalized bounds;
- set declared layer placement/depth values within schema bounds;
- choose an existing motion recipe/action;
- choose `hard_cut`, approved motivated match cut, or another P13-permitted
  transition;
- set caption position/style within the approved lower safe band;
- record shot approval/rejection and reviewer note.

Operations may not alter timing, word ranges, narration/audio hashes, source
paths, selected source-package hash, claim text, or publication state. Patch
application is deterministic and produces a new plan hash plus a machine- and
human-readable before/after packet.

### Security and backend boundaries

- Treat all paths from manifests, Studio downloads, model outputs, and OTIO as
  untrusted input. Resolve them under an explicit job/project root and reject
  escape, symlink escape, remote URL, device path, and alternate data stream.
- Allowlist patch operations, layer roles, transition kinds, asset IDs, model
  IDs, and output extensions.
- Use structured subprocess argument arrays; never interpolate manifest values
  into shell command strings.
- Keep source media immutable. Stage/copy by verified SHA-256 into a revision
  directory and record hashes before and after render.
- Do not expose credentials to Remotion Studio or generated props.
- Rate/cost boundaries remain local: no provider call and no paid render API is
  part of P16.

### Frontend patterns

- Keep Studio controls derived from typed plan/patch schemas; do not maintain a
  second client state model.
- Keep render composition pure and deterministic. Interactive review state lives
  in a separate review composition/module.
- Provide explicit loading/error/invalid-patch states and accessible labels.
- Export/download patch JSON from the browser; import and apply it through the
  validated CLI.
- Use stable shot IDs and memoized derived views for the 192-shot list.

### External dependency policy

- Remotion remains pinned at 4.0.502. Run `npm ci` from the existing lockfile;
  do not upgrade in P16.
- Record the exact upstream Remotion skill commit before vendoring only the
  seven approved skills. No skill code enters runtime artifacts.
- Run SAM 2.1 in WSL/Linux per its official guidance. Store its environment and
  model cache outside the application environment and repository.
- Permit only Depth Anything V2 Small unless a later separate clearance changes
  policy. Record exact checkpoint revision, every downloaded file hash, and
  license text.
- Pin SigLIP to an exact Hugging Face revision and downloaded-file hash set.
  Its score remains advisory.
- Pin `opentimelineio==0.18.1` and
  `opentimelineio-plugins==0.18.1` in an editorial-tools requirements file.
  Native `.otio` is canonical interchange; `fcp_xml` is a labeled lossy export.

## Task Slices

### T1: Establish the isolated implementation foundation
- Status: completed
- Owner: parent
- Depends on: Gate 0
- Write set: Git metadata for `codex/p16-agent-native-editor-design-toolchain`; the approved `.claude/PRPs/plans/P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.plan.md` and `.claude/PRPs/compacts/P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.compact.md` copied hash-for-hash into the isolated worktree; `.claude/PRPs/evidence/P16/foundation.md`; no source writes in the active `codex/stickly-woodblock-variant` worktree
- Acceptance: A new worktree is created from `f70a502ef8260a6f64535ba5559fe724d2096722`; handoff commit `ba69d1769191d9b0d463129b24dcd1afe548aa57` is merged additively; only the approved P16 plan/compact are materialized from active uncommitted files and their source/destination SHA-256 values match; the active dirty worktree status hash is unchanged; the foundation record captures branch, base, merge base, handoff commit, plan/compact hashes, installed runtime versions, Remotion licensing gate state, and P15 foundation dependency state.
- Validate: `git -C "C:\Users\Snipe\.codex\worktrees\p16-editor-design\Outreach Program" merge-base --is-ancestor f70a502ef8260a6f64535ba5559fe724d2096722 HEAD; git -C "C:\Users\Snipe\.codex\worktrees\p16-editor-design\Outreach Program" merge-base --is-ancestor ba69d1769191d9b0d463129b24dcd1afe548aa57 HEAD; git -C "C:\Users\Snipe\.codex\worktrees\p16-editor-design\Outreach Program" status --short`
- Evidence: `.claude/PRPs/evidence/P16/foundation.md`; merge commit `c6f4f7db521510b371c1646e4aad470540552a0a`; active dirty status SHA-256 remained `94856bf9fa2a92911d0c9f2cfbe124dcdc2b357ff3f8c7125c82d42dec7b80ff`.

Implementation notes:

1. Verify the target path resolves beneath
   `C:\Users\Snipe\.codex\worktrees\p16-editor-design` and does not exist.
2. Record `git status --porcelain=v1 -uall` and SHA-256 it in the active
   worktree.
3. Create the worktree/branch from the exact base, then run
   `git merge --no-ff --no-edit ba69d1769191d9b0d463129b24dcd1afe548aa57`.
4. Copy only the approved P16 plan and compact into the isolated worktree with
   `Copy-Item -LiteralPath`; compare `Get-FileHash -Algorithm SHA256` at both
   locations and stop on any mismatch.
5. Recompute the active status hash. A mismatch stops the PRP.
6. Do not import the active unstaged History-of-BJJ or P14/P15 files. T5 waits
   for a separately reviewed P15 foundation commit.

### T2: Activate the dedicated Remotion composition
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/editor/src/Root.tsx`; `content/video_engine/editor/package.json`; `content/video_engine/editor/fixtures/editorial-motion-two-shot/**`; `content/video_engine/tests/test_remotion_editorial_fixture.py`
- Acceptance: `EditorialMotion` imports and renders `EditorialMotionComposition`; `Editorial` and `Documentary` registrations are unchanged; the two-shot fixture uses staged local media and canonical fixture audio; path/URL negative fixtures fail; TypeScript and a 640x360/15fps render pass.
- Validate: `npm --prefix content/video_engine/editor ci; npm --prefix content/video_engine/editor run typecheck; python -m pytest content/video_engine/tests/test_remotion_editorial_fixture.py -q; npm --prefix content/video_engine/editor run render:editorial-motion-fixture`
- Evidence: `.claude/PRPs/evidence/P16/t2-compositor.md`; 13 focused tests and TypeScript typecheck passed; local render SHA-256 `8f10358be9acaef30422375777e3c0d139091e53e57104c05a4182d86dd854f4`.

The render script must select `EditorialMotion`, pass fixture props explicitly,
write beneath `content/video_engine/runtime/jobs/p16-fixture/`, and never invoke
Remotion Automator or another paid service.

### T3: Add the generic Martial adapter and exact-word compiler path
- Status: completed
- Owner: parent (completed from implementation_luna checkpoint)
- Depends on: T2
- Write set: `content/video_engine/configs/editorial_review_authorization.schema.json`; `content/video_engine/configs/martial_editorial_adapter_manifest.schema.json`; `content/video_engine/configs/editorial_pacing_recipe.default.json`; `content/video_engine/src/services/martial_editorial_adapter.py`; `content/video_engine/src/services/editorial_motion.py`; `content/video_engine/src/guards/editorial_motion_qc.py`; `content/video_engine/cli.py`; `content/video_engine/tests/test_martial_editorial_adapter.py`; focused additions to `content/video_engine/tests/test_editorial_motion.py` and `content/video_engine/tests/test_editorial_motion_qc.py`
- Acceptance: The adapter fails without a valid internal-review authorization; with a valid fixture authorization it verifies all immutable r1 hashes, exact 192 cue/plate pairs, explicit word ranges and midpoint-derived cue time ranges, contiguous 0.000–567.804 coverage, selected-file hashes, and cue-local entry/micro-event/exit instructions; it emits the existing motion-plan schema plus job-local asset/overlay/props and adapter manifests; a cue longer than 3.35 seconds carries at least one timed material event; legacy timestamped compilation remains byte-stable for existing fixtures.
- Validate: `python -m pytest content/video_engine/tests/test_martial_editorial_adapter.py content/video_engine/tests/test_editorial_motion.py content/video_engine/tests/test_editorial_motion_qc.py -q; python -m content.video_engine.cli compile-martial-editorial --help`
- Evidence: `.claude/PRPs/evidence/P16/t3-adapter.md`; 58 focused tests,
  real 192-plate hash verification, CLI help, TypeScript, and diff checks pass.

Required CLI inputs are explicit paths for edit package, cue sheet, audio
manifest, word timing, caption plan/output, authorization, pacing recipe, job
root, and revision ID. The CLI must refuse an output root outside
`content/video_engine/runtime/jobs/` unless an existing test-only dependency is
injected.

### T4: Compile and render the first-minute proof
- Status: in_progress (awaiting Gate A operator watch-through)
- Owner: parent
- Depends on: T3 and Gate 1
- Write set: `content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/editorial-review-authorization.v1.json`; generated artifacts under `content/video_engine/runtime/jobs/marshall-monday-001-p16/animatic/revisions/gate-a-first-minute/`; `.claude/PRPs/evidence/P16/gate-a.md`
- Acceptance: The authorization lists exactly the 192 handoff assets and hashes; the sample ends on the nearest complete authored cue between 45 and 60 seconds and contains 8–20 cues; normal and diagnostic 640x360/15fps previews use the r1 canonical audio segment; structural QC, contained-file hash verification, ffprobe duration, and human watch-through pass.
- Validate: `python -m content.video_engine.cli compile-martial-editorial --edit-package content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/marshall-monday-001-edit-package.v1.json --cue-sheet content/video_engine/projects/martial-matters/pilots/marshall-monday-001/continuity/revisions/r1/word-timed-visual-cues-r1.v1.json --audio-manifest content/video_engine/projects/martial-matters/pilots/marshall-monday-001/audio/revisions/r1/marshall-monday-001-canonical-audio-r1.v1.json --word-timings content/video_engine/projects/martial-matters/pilots/marshall-monday-001/audio/revisions/r1/marshall-monday-001-master-r1.words.json --caption-plan content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/captions/marshall-monday-001-dynamic-captions.v1.json --caption-output content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/captions/marshall-monday-001-anchor.en-US.srt --authorization content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/editorial-review-authorization.v1.json --pacing-recipe content/video_engine/configs/editorial_pacing_recipe.default.json --sample-max-seconds 60 --sample-max-cues 20 --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id gate-a-first-minute; python -m content.video_engine.cli validate-editorial-motion --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id gate-a-first-minute; python -m content.video_engine.cli render-editorial-motion-revision --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id gate-a-first-minute --width 640 --height 360 --fps 15 --diagnostic`
- Evidence: `.claude/PRPs/evidence/P16/gate-a.md`; 20 authored cues ending at
  58.833 seconds; structural QC passed; normal and diagnostic previews rendered.

If exact CLI flag names differ from the existing parser convention, T3 must add
these names and its CLI test must lock them. The first-minute render stops for
Gate A; it does not cascade into a full render.

### T5: Install and route official Remotion skills project-locally
- Status: pending
- Owner: junior_developer
- Depends on: T4, Gate A, and a reviewed P15 foundation commit
- Write set: `.agents/skills/remotion-best-practices/**`; `.agents/skills/remotion-markup/**`; `.agents/skills/remotion-studio/**`; `.agents/skills/remotion-render/**`; `.agents/skills/remotion-captions/**`; `.agents/skills/remotion-interactivity/**`; `.agents/skills/remotion-multimedia/**`; `.agents/skills/remotion-source-manifest.v1.json`; `docs/agent-context/SKILL_ROUTER.md`; `scripts/configure_codex_skill_allowlist.py`; generated allowlist output owned by that script
- Acceptance: Only the seven approved official skills are installed; the upstream commit and every copied file hash are recorded; router text names the precise triggers; the generator recreates the allowlist without manual generated-block edits; Codex and Claude project discovery succeeds where supported; runtime and render manifests contain no skill path.
- Validate: `python scripts/configure_codex_skill_allowlist.py --check; python scripts/configure_codex_skill_allowlist.py --write; python scripts/configure_codex_skill_allowlist.py --check; python -m pytest content/video_engine/tests/test_martial_style_skill_routing.py -q; git diff --check`
- Evidence: pending

Before copying files, the implementer must inspect the installed CLI’s
`npx skills add --help`, resolve the official repository HEAD to an exact commit,
and preview installation in a disposable directory. Network download is a
parent-owned action. Any unexpected file outside the declared write set blocks
installation. Before T5 starts, the parent cherry-picks or merges only the
reviewed P15 foundation commit(s), records those SHA values in P16 evidence, and
reruns the P15 routing tests. If no reviewed P15 foundation commit exists, T5
remains blocked; the parent must not copy the active unstaged router changes.

### T6: Implement immutable editorial revision patches
- Status: pending
- Owner: implementation_luna
- Depends on: T4 and Gate A
- Write set: `content/video_engine/configs/editorial_revision_patch.schema.json`; `content/video_engine/configs/editorial_revision_packet.schema.json`; `content/video_engine/src/services/editorial_revisions.py`; `content/video_engine/src/guards/editorial_motion_qc.py`; `content/video_engine/cli.py`; `content/video_engine/tests/test_editorial_revisions.py`
- Acceptance: Allowed operations apply by stable shot ID, verify old values, enforce field/value allowlists, reject stale bases and forbidden timing/hash/path mutations, recompute the plan hash, and emit a before/after packet listing every changed shot. Identical base+patch inputs produce identical patched content hashes apart from separately excluded provenance timestamps.
- Validate: `python -m pytest content/video_engine/tests/test_editorial_revisions.py content/video_engine/tests/test_editorial_motion_qc.py -q; python -m content.video_engine.cli apply-editorial-revision --help`
- Evidence: pending

### T7: Add the Remotion Studio review surface
- Status: pending
- Owner: implementation_luna
- Depends on: T6
- Write set: `content/video_engine/editor/src/EditorialReview.tsx`; `content/video_engine/editor/src/editorialReviewState.ts`; `content/video_engine/editor/src/Root.tsx`; `content/video_engine/editor/src/types.ts`; `content/video_engine/editor/src/__fixtures__/editorial-review/**`; `content/video_engine/editor/src/__tests__/editorialReviewState.test.ts`; `content/video_engine/editor/package.json`
- Acceptance: A separate `EditorialReview` composition exposes only schema-backed controls, displays validation/error states, exports a patch download without direct filesystem writes, and remains isolated from render composition state. The fixture operation survives patch import, Python recompilation, and Studio reload; the review packet shows exactly one intended change.
- Validate: `npm --prefix content/video_engine/editor run typecheck; npm --prefix content/video_engine/editor run test; python -m pytest content/video_engine/tests/test_editorial_revisions.py -q; npm --prefix content/video_engine/editor run studio -- --help`
- Evidence: pending

Gate B uses the first-minute job. Browser automation may verify controls and
download, but the operator must judge the resulting visual change.

### T8: Add isolated trace-cut and depth preprocessing
- Status: pending
- Owner: implementation_luna
- Depends on: T4 and Gate A
- Write set: `content/video_engine/configs/editorial_preprocess_job.schema.json`; `content/video_engine/configs/editorial_preprocess_derivative.schema.json`; `content/video_engine/src/services/editorial_preprocessing.py`; `content/video_engine/tools/vision_preprocess/**`; `content/video_engine/tests/test_editorial_preprocessing.py`; generated quarantined proof artifacts under `content/video_engine/runtime/jobs/marshall-monday-001-p16/preprocess/`
- Acceptance: The main service validates requests and subprocess outputs without importing torch; the WSL worker pins SAM 2.1 and Depth Anything V2 Small revisions and file hashes; 3–5 source plates produce trace-cut alpha, depth, contact-shadow/layer metadata, and QA previews while originals remain byte-identical; missing limbs, halos, bad depth, unavailable WSL/CUDA, or model failure returns `flat_plate_fallback` rather than blocking the edit.
- Validate: `python -m pytest content/video_engine/tests/test_editorial_preprocessing.py -q; python -m content.video_engine.cli validate-editorial-preprocess --help; wsl.exe --status`
- Evidence: pending

Tests use an injected fake runner and tiny fixtures. Model downloads and the
3–5 plate proof occur only after the parent records exact upstream revisions,
licenses, cache paths, and SHA-256 values; model files are not committed.

### T9: Add deterministic and semantic visual QA
- Status: pending
- Owner: implementation_luna
- Depends on: T6; SigLIP scoring also depends on T8's isolated-runner contract
- Write set: `content/video_engine/configs/editorial_visual_qa.schema.json`; `content/video_engine/src/services/editorial_visual_qa.py`; `content/video_engine/src/guards/editorial_motion_qc.py`; `content/video_engine/cli.py`; `content/video_engine/tests/fixtures/editorial_visual_qa/**`; `content/video_engine/tests/test_editorial_visual_qa.py`; generated proof reports under `content/video_engine/runtime/jobs/marshall-monday-001-p16/qa/`
- Acceptance: Deterministic checks cover pHash adjacency/repetition, blank ratio, OCR text, safe-area collisions, static-hold budget, alpha edges, transparent-pixel bounds, depth order, aspect, and resolution; pinned SigLIP inference binds model revision and downloaded-file hashes and remains advisory; deliberate mismatch/repetition/blank/OCR/collision fixtures fail; a metaphor override requires reviewer, timestamp, and reason.
- Validate: `python -m pytest content/video_engine/tests/test_editorial_visual_qa.py content/video_engine/tests/test_editorial_motion_qc.py -q; python -m content.video_engine.cli validate-editorial-visuals --help`
- Evidence: pending

Gate C records thresholds after fixture reports are inspected. Threshold changes
are versioned configuration, not hidden constants or model output.

### T10: Export native OTIO and a labeled NLE package
- Status: pending
- Owner: implementation_luna
- Depends on: T6 and Gate B
- Write set: `content/video_engine/requirements-editorial-tools.txt`; `content/video_engine/configs/editorial_timeline_export.schema.json`; `content/video_engine/src/services/editorial_timeline_export.py`; `content/video_engine/cli.py`; `content/video_engine/tests/test_editorial_timeline_export.py`; generated exports under `content/video_engine/runtime/jobs/marshall-monday-001-p16/exports/`; `.claude/PRPs/evidence/P16/gate-d-nle-import.md`
- Acceptance: With `opentimelineio==0.18.1` and `opentimelineio-plugins==0.18.1`, native OTIO round-trips without changing duration/frame rate/clip order/audio placement/cue/word/hash metadata; all media references resolve within the job package and match hashes; FCP XML is labeled lossy and records unsupported Remotion actions as markers/metadata; an operator imports it into Resolve or records the exact external blocker without altering canonical artifacts.
- Validate: `python -m pytest content/video_engine/tests/test_editorial_timeline_export.py -q; python -m content.video_engine.cli export-editorial-timeline --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id gate-a-first-minute --format otio; python -m content.video_engine.cli validate-editorial-timeline --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id gate-a-first-minute`
- Evidence: pending

Use rational frame times derived from the approved render profile. Native OTIO
is validated by reading it back with OTIO and comparing it to the motion plan;
adapter output never becomes canonical input.

### T11: Render the full internal preview and close documentation
- Status: pending
- Owner: parent
- Depends on: T5, T7, T8, T9, T10, Gates A, B, C, and D
- Write set: generated artifacts under `content/video_engine/runtime/jobs/marshall-monday-001-p16/animatic/revisions/full-internal-preview/`; `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md`; `docs/content-video-engine/21-MARTIAL-MATTERS-AGENT-REPRODUCTION-RUNBOOK.md`; `docs/content-video-engine/22-AGENT-NATIVE-EDITORIAL-TOOLCHAIN.md`; `.claude/PRPs/evidence/P16/**`; this PRP status/evidence fields
- Acceptance: The full preview uses one canonical audio track and the exact 192 authorized plates, passes all structural/hash/path/timing/visual QA, produces diagnostic and review packets plus OTIO export, and receives an independent read-only reviewer report and final human editorial decision. No publish or promotion action is invoked.
- Validate: `python -m content.video_engine.cli compile-martial-editorial --edit-package content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/marshall-monday-001-edit-package.v1.json --authorization content/video_engine/projects/martial-matters/pilots/marshall-monday-001/edit/revisions/r1/editorial-review-authorization.v1.json --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id full-internal-preview; python -m content.video_engine.cli validate-editorial-motion --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id full-internal-preview; python -m content.video_engine.cli render-editorial-motion-revision --job-root content/video_engine/runtime/jobs/marshall-monday-001-p16 --revision-id full-internal-preview --diagnostic; python -m pytest content/video_engine/tests -q; npm --prefix content/video_engine/editor run typecheck; git diff --check`
- Evidence: pending

## Verification

### Baseline recorded during planning

```text
python -m pytest content/video_engine/tests/test_editorial_motion.py \
  content/video_engine/tests/test_editorial_motion_qc.py -q
51 passed in 0.29s
```

`npm --prefix content/video_engine/editor run typecheck` is currently blocked in
the planning worktree because `node_modules` is absent (`tsc` not found). T2
must run `npm ci` from the committed lockfile before recording TypeScript
baseline evidence.

### Focused verification order

```powershell
python -m pytest content/video_engine/tests/test_remotion_editorial_fixture.py -q
python -m pytest content/video_engine/tests/test_martial_editorial_adapter.py -q
python -m pytest content/video_engine/tests/test_editorial_revisions.py -q
python -m pytest content/video_engine/tests/test_editorial_preprocessing.py -q
python -m pytest content/video_engine/tests/test_editorial_visual_qa.py -q
python -m pytest content/video_engine/tests/test_editorial_timeline_export.py -q
python -m pytest content/video_engine/tests/test_editorial_motion.py -q
python -m pytest content/video_engine/tests/test_editorial_motion_qc.py -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run test
```

### Full verification

```powershell
python -m pytest content/video_engine/tests -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run test
npm --prefix content/video_engine/editor run build
python scripts/configure_codex_skill_allowlist.py --check
python scripts/prp_validate.py .claude/PRPs/plans/P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.plan.md
git diff --check
git status --short
```

### Required artifact inspections

- Compare the source-package, cue-sheet, audio, word-timing, authorization,
  normalized plate-plan, asset-map, motion-plan, patch, render-job, QA, and OTIO
  hash chain.
- Verify the 192 cue IDs, plate paths, and hashes exactly equal the r1 handoff.
- Verify cue word ranges are exact, contiguous, and unchanged after patching.
- Verify every staged and exported media path remains beneath its job root.
- Verify no generated provider URL, model cache, secret, skill file, contact
  sheet, alternate, audit frame, or review render appears in production props.
- Verify source plate and canonical audio hashes remain unchanged after
  preprocessing, Studio review, full render, and OTIO export.
- Watch both normal and diagnostic first-minute/full previews with sound.

## Evidence And Handoff

The parent updates each slice’s `Evidence` field with exact commands, verdicts,
artifact paths, hashes, and human-gate decisions. Required durable evidence:

- `.claude/PRPs/evidence/P16/foundation.md`
- `.claude/PRPs/evidence/P16/gate-a.md`
- `.claude/PRPs/evidence/P16/gate-b.md`
- `.claude/PRPs/evidence/P16/gate-c.md`
- `.claude/PRPs/evidence/P16/gate-d-nle-import.md`
- `.claude/PRPs/evidence/P16/reviewer-report.md`
- adapter, authorization, motion-plan, patch, QA, render-job, and OTIO manifest
  paths beneath the P16 runtime job
- normal and diagnostic preview paths plus SHA-256 values

Independent review is read-only and checks correctness, path security, hash
chain integrity, legacy P13 compatibility, dependency/license records, model
advisory boundaries, and missing tests. The parent reviews all delegated diffs,
records the final human editorial gate, and stops before commit, push,
publication, catalog promotion, or provider spend unless the user separately
authorizes those actions.
