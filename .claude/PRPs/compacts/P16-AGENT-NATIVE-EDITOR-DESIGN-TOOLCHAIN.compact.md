---
id: P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN-COMPACT
title: Agent-Native Editorial And Design Toolchain Strategic Compact
status: ready_for_prp_plan
next_skill: prp-plan
operation: feature
risk: standard
owner: parent
created: 2026-08-06
updated: 2026-08-06
---

# Objective

Eliminate routine transfer of Martial Matters plates, narration, timing, and
captions into a separate design chat. Extend the existing deterministic
editorial-motion system so an agent can compile, preview, revise, validate,
render, and export an episode while a human retains final editorial approval.

Claude Design, Canva, Figma, and provider video tools remain optional concept,
hero-shot, or exceptional-design surfaces. They are not the canonical episode
assembler.

# Current Proven State

- `content/video_engine/editor/` already pins Remotion 4.0.502 and exposes
  `Editorial`, `Documentary`, and `EditorialMotion` compositions.
- `editor/src/EditorialMotion.tsx` already supports hash-resolved assets,
  canonical audio, exact shot timing, layer roles, masks, bounded camera moves,
  local actions, captions, citations, SFX, and diagnostic rendering.
- `editor/src/types.ts` already defines `editorial_motion_plan.v1`, including
  word ranges, layers, placement, masks, information surfaces, and render
  profiles.
- `src/services/editorial_motion.py` already compiles and validates deterministic
  editorial-motion plans and includes a timestamped-plate compiler.
- `src/guards/editorial_motion_qc.py` already rejects stale hashes, path escape,
  timing defects, unsupported motion, excessive holds, unsafe overlays, and
  provider leakage.
- P13 is the specification of record for motion ownership, timing authority,
  visual-event rules, and human approval gates. P16 extends P13 and must not
  fork its contracts without an explicit migration.
- Marshall Monday 001 has a canonical r1 package: 567.804 seconds, 192 contiguous
  word-timed cues, 192 selected plates, corrected narration, dynamic captions,
  and SHA-256 bindings. The pushed design-handoff branch is a delivery branch,
  not the implementation base.
- Registration defect to audit first: `editor/src/Root.tsx` registers the
  `EditorialMotion` composition with `DocumentaryMotionComposition` while the
  dedicated `EditorialMotionComposition` exists in `EditorialMotion.tsx`.

# Locked Architecture Decisions

1. Canonical narration audio and word timing remain the sole production clock.
2. The Marshall r1 edit package remains immutable input. An adapter compiles it
   into the existing `editorial_motion_plan.v1` contract; no second timeline is
   introduced.
3. Renderer-facing plans use approved asset IDs and job-local asset maps, never
   arbitrary provider URLs or unrestricted filesystem paths.
4. Human adjustments are stored as an immutable
   `editorial_revision_patch.v1` artifact. Studio must not silently rewrite the
   source script, word timing, selected-plate manifest, or generated plan.
5. The compiler applies the revision patch deterministically and recomputes the
   complete hash chain. Identical inputs produce identical plan and render-job
   manifests.
6. AI segmentation, depth estimation, and semantic scoring create quarantined
   derivatives or advisory reports. They never promote assets or approve an
   edit.
7. Remotion remains the production compositor. OpenTimelineIO is an interchange
   export; Resolve/Premiere/Final Cut/Kdenlive cannot become a competing source
   of truth through an unreviewed round trip.
8. Provider-generated motion remains shot-local, optional, and separately
   authorized under the existing P13 provider boundary.

# Recommended Workstreams 1–7

## 1. Activate The Existing Remotion Motion Compositor

Audit and correct composition registration, input-prop resolution, public asset
staging, canonical audio alignment, Windows long-path handling, and render CLI
selection. Preserve the current `Editorial` and `Documentary` compositions.

Primary files:

- `content/video_engine/editor/src/Root.tsx`
- `content/video_engine/editor/src/EditorialMotion.tsx`
- `content/video_engine/editor/src/types.ts`
- `content/video_engine/editor/package.json`
- focused TypeScript and renderer tests

Acceptance:

- `EditorialMotion` renders the dedicated component.
- Typecheck passes.
- A fixture render uses canonical audio and a two-shot layer plan.
- No absolute path, traversal path, remote URL, or unapproved asset resolves.

## 2. Compile Marshall Edit Packages Into Motion Plans

Add a generic Martial Matters adapter, with Marshall Monday 001 as the first
fixture. It must read the r1 edit package, canonical audio manifest, word timing,
caption track, and selected-plate hashes; stage the exact assets job-locally;
and emit `editorial_motion_plan.v1`, asset map, overlay map, and render props.

Prefer a new bounded service rather than episode-specific logic inside the
renderer. Reuse `compile_timestamped_editorial_motion_plan()` and P13 QC.

Likely files:

- new `content/video_engine/src/services/martial_editorial_adapter.py`
- `content/video_engine/src/services/editorial_motion.py`
- `content/video_engine/src/guards/editorial_motion_qc.py`
- `content/video_engine/cli.py`
- schemas and focused tests

Acceptance:

- All 192 Marshall cues resolve to their exact selected plate and word range.
- Coverage is 0.000–567.804 seconds with zero gaps or overlaps.
- Audio, timing, cue-sheet, script, plate, and plan hashes validate.
- No alternates, contact sheets, audit frames, or review renders enter the job.
- A low-resolution first minute and then the full episode render from one
  canonical audio track.

## 3. Add Official Remotion Agent Skills Project-Locally

Install the official `remotion-dev/skills` guidance in a project-scoped
location, route only the needed skills, and keep them out of runtime output.
Start with best practices, markup, Studio, render, captions, interactivity,
and multimedia. Maps remain optional until a geographic episode requires them.

Repository integration must respect the allowlist-first policy in
`docs/agent-context/SKILL_ROUTER.md`; update the generated allowlist through its
own generator rather than hand-editing generated blocks.

Acceptance:

- Skills are project scoped, version identifiable, and available to both Codex
  and Claude Code where supported.
- Runtime and rendered artifacts do not depend on skill files.
- No duplicate or conflicting local Remotion instructions remain active.

## 4. Add A Remotion Studio Review Surface

Expose only editorial controls that map to deterministic patch operations:

- selected plate or approved alternate;
- focal point and safe crop;
- layer placement and depth amount;
- declared action and motion recipe;
- hard cut, motivated match cut, or permitted transition;
- caption position/style within the approved safe band;
- shot approval, rejection reason, and reviewer note.

Studio writes or downloads `editorial_revision_patch.v1`; it does not mutate
the canonical edit package. The compiler reapplies the patch and regenerates
the preview.

Acceptance:

- One operator change survives reload and recompilation.
- The patch records base artifact hash, changed field, old value, new value,
  reviewer, timestamp, and reason.
- Stale-base patches fail closed.
- A before/after review packet identifies every changed shot.

## 5. Add Trace-Cut And Depth Preprocessing

Create an optional, isolated preprocessing lane:

- SAM 2.1 for prompted subject/prop/foreground segmentation;
- Depth Anything V2 Small for commercial-safe relative depth estimation;
- deterministic alpha cleanup, edge inspection, contact-shadow support, and
  authored foreground/midground/background grouping.

SAM 2 is best isolated in WSL/Linux on Windows because its official setup
recommends WSL and may compile CUDA extensions. Do not add its PyTorch/CUDA
requirements to the main application environment. Depth Anything V2 Small is
Apache-2.0; Base/Large checkpoints are non-commercial and prohibited for this
monetized workflow unless separately cleared.

New artifacts should include source hash, model/checkpoint identity and license,
prompt/box coordinates, alpha-mask hash, depth-map hash, layer order, QA state,
and fallback to the original flat plate.

Acceptance:

- The source plate remains unchanged.
- Trace cuts preserve complete hands, feet, weapons, microphones, crowns, and
  contact shadows where present.
- Alpha-edge, halo, missing-limb, and depth-order QA passes before reuse.
- Failure falls back to the flat plate; it never blocks the canonical edit.

## 6. Add Semantic And Visual QA

Use a local image-text embedding model such as CLIP or SigLIP to compare each
plate with its narration excerpt and intended visual action. Combine that
advisory score with deterministic checks:

- perceptual-hash adjacency and repetition;
- blank/parchment-area ratio;
- OCR detection of accidental generated text;
- caption/subject/weapon/feet safe-area collisions;
- static-hold and visual-change budgets;
- layer boundary and transparent-pixel inspection;
- expected aspect and resolution.

Embedding scores are triage signals, not truth. They may flag a shot for human
review or rank already-approved alternates; they may not invent claims, replace
rights review, or auto-promote an asset.

Acceptance:

- A deliberately mismatched plate is flagged.
- A repeated adjacent plate and excessive blank region are flagged.
- A valid metaphorical plate can be human-approved with a recorded reason.
- Reports bind model identity, thresholds, source hashes, and reviewer outcome.

## 7. Export OpenTimelineIO And Professional NLE Packages

Compile the same approved motion plan into canonical `.otio` JSON with media
references, video/audio tracks, cue IDs, word ranges, claim IDs, captions, and
review markers. Add secondary adapters only where the target NLE supports them,
starting with FCP XML or the most reliable Resolve ingest path discovered in
implementation research.

OTIO is the interchange master because its native JSON is lossless. Adapter
outputs are explicitly labeled lossy; unsupported Remotion effects remain
rendered plates/clips or documented markers rather than silently disappearing.

Acceptance:

- OTIO duration, frame rate, audio placement, and 192 plate intervals equal the
  approved motion plan.
- Every media reference resolves and matches its recorded hash.
- Import into the selected finishing NLE retains cuts, audio, captions/markers,
  and clip order.
- NLE changes do not overwrite canonical source artifacts. A requested change
  returns as a reviewed revision patch or a clearly labeled finishing-only
  render.

# Execution Sequence And Gates

```text
Preflight: isolate branch/worktree and preserve dirty user files
  -> Slice 1: compositor registration + fixture render
  -> Slice 2: Marshall adapter + first-minute proof
  -> Gate A: operator watches deterministic first-minute proof
  -> Slice 3: official project-scoped Remotion skills
  -> Slice 4: Studio revision-patch workflow
  -> Gate B: operator edits one shot and approves round trip
  -> Slice 5: SAM/depth optional preprocessing proof on 3-5 plates
  -> Slice 6: semantic/visual QA proof with positive and negative fixtures
  -> Gate C: operator approves QA thresholds and commercial model policy
  -> Slice 7: OTIO export + one NLE import proof
  -> Full Marshall 001 deterministic preview
  -> Final human editorial gate
```

The first implementation proof should use a 45–60 second Marshall excerpt with
8–20 cues, not the full 192-plate episode. Full-episode rendering begins only
after timing, asset staging, caption placement, and motion behavior pass Gate A.

# Validation Baseline

Run the smallest focused suite first:

```powershell
python -m pytest content/video_engine/tests/test_editorial_motion.py -q
python -m pytest content/video_engine/tests/test_editorial_motion_qc.py -q
npm --prefix content/video_engine/editor run typecheck
```

The PRP should add focused tests for the Martial adapter, revision-patch schema,
preprocessing manifests, semantic-QA report, OTIO export, and a low-resolution
Remotion fixture render. Full-suite validation follows only after focused tests
pass.

# Branch And Workspace Boundary

- Do not implement on `codex/episode1-claude-design-handoff`; it is an editing
  delivery branch containing large media artifacts.
- The active `codex/stickly-woodblock-variant` worktree contains extensive
  user-owned uncommitted Martial Matters work. Preserve it exactly.
- Before implementation, inventory the intended base commit and create or
  select an isolated `codex/` implementation branch/worktree without importing
  unstaged changes from `main`.
- If the required P14/P15 foundation is still uncommitted, the PRP must define
  a reviewed foundation commit or an explicit bounded file-transfer strategy
  before any implementation slice starts.

# Out Of Scope

- Prompt-to-video replacement of the deterministic edit.
- Automatic publication or asset promotion.
- Voice regeneration or a second narration clock.
- Full NLE clone inside the repository.
- Per-frame LLM direction.
- Automatic factual, rights, or likeness approval.
- Non-commercial depth checkpoints in monetized production.
- Provider spending without a separate explicit approval.

# Mandatory Reads For The Next Planning Turn

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/agent-context/SKILL_ROUTER.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md`
- `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md`
- `docs/content-video-engine/21-MARTIAL-MATTERS-AGENT-REPRODUCTION-RUNBOOK.md`
- `content/video_engine/src/services/editorial_motion.py`
- `content/video_engine/src/guards/editorial_motion_qc.py`
- `content/video_engine/editor/src/Root.tsx`
- `content/video_engine/editor/src/EditorialMotion.tsx`
- `content/video_engine/editor/src/types.ts`
- Marshall Monday 001 r1 edit package, canonical audio manifest, word timing,
  captions, and word-timed cue sheet

# Next Action

Run `prp-plan` against this compact to produce an implementation-ready
`P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.plan.md`. The plan must resolve the
implementation-base/worktree boundary, dependency isolation, exact schemas,
write sets, ownership, tests, and Gate A proof command before `prp-implement`
is invoked.
