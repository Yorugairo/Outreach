---
id: P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION-COMPACT
title: Remotion Production Console optimization boundary
status: ready_for_prp_plan
next_skill: prp-plan
operation: feature
risk: high
owner: parent
created: 2026-08-10
updated: 2026-08-10
---

# Objective

Turn the existing Remotion compositor and finance-video artifacts into a fast,
operator-friendly local production loop. The target is not a general-purpose
NLE. It is a Production Console that lets an operator see the current scene,
narration timing, approved production visuals, evidence context, and review
state together; make a small allowlisted visual adjustment; preview it in the
Remotion Player; and emit an immutable revision/render packet.

# Proven State

- The repository already has a pinned Remotion editor at
  `content/video_engine/editor/` using Remotion `4.0.502`, React `18.3.1`, and
  TypeScript `5.7.3`.
- `npm --prefix content/video_engine/editor run typecheck` passes on
  2026-08-10.
- The editor registers six compositions. `EditorialMotion` is currently wired
  to `DocumentaryMotionComposition`, while the dedicated
  `EditorialMotionComposition` is exported from `EditorialMotion.tsx`.
- The current-bubble pilot already has scene-flow, scene-bundle, pacing,
  overlay, cue-sheet, edit-manifest, claim-ledger, narration, and word-timing
  artifacts.
- The existing Python render path is revision-only, preserves protected Gate A
  artifacts, writes below the job revision tree, records zero provider calls,
  and emits normal plus diagnostic previews.
- P19 established durable watch-review and learning artifacts. P28 established
  deterministic deck extraction and contextual asset manifests.
- Six teacher-stamped decks are operator-approved with scope
  `production_visuals`. That approval does not automatically promote their
  underlying source images to evidence status.
- The active worktree is very dirty and contains unrelated user work. P29 must
  execute from a fresh isolated branch/worktree.

# Locked Architecture

1. Keep Remotion as the deterministic renderer and composition runtime.
2. Build the Production Console as a separate local React application using
   `@remotion/player` at the exact same Remotion version as the compositor.
3. Do not customize Remotion Studio into a workflow database or production
   dashboard. Studio remains useful for code-native composition debugging.
4. Put project/file/process access behind a loopback-only Python bridge. The
   browser never receives arbitrary filesystem or shell access.
5. Read existing canonical artifacts into one derived, schema-backed console
   snapshot. Do not invent a second timing, claim, approval, or asset model.
6. Persist only immutable revision patches, render jobs, review notes, and
   approval artifacts. Never mutate source decks, canonical narration, word
   timing, claims, or prior revisions in place.
7. Optimize the operator loop first; measure raw rendering separately. Do not
   claim speed improvements without baseline and post-change measurements on
   the same fixture and machine.

# Allowed MVP Adjustments

- Select an already-approved production visual or approved alternate.
- Adjust crop/focal point and layer `x`, `y`, `scale`, `opacity`, and `z` within
  schema bounds.
- Select an approved motion, camera, transition, or caption-safe-band recipe.
- Offset a visual event only inside the canonical cue interval.
- Toggle an approved teacher-stamp variant.
- Record a reviewer note and shot status.

# Explicit Non-Goals

- No Premiere/Resolve clone, freeform timeline, arbitrary keyframe editor, or
  generic drag-anything canvas.
- No script, narration, canonical audio, word timing, claim, citation, rights,
  or source-file mutation.
- No external provider call, image generation, publishing, deployment, or paid
  rendering.
- No automatic evidence approval or inference that
  `production_visuals == factual_evidence`.
- No SAM/depth generation, semantic visual QA, OTIO/FCP export, or broad
  Martial Matters adapter work; those remain in P16.

# Ownership Boundary With P16

P16 already reserves its T2, T6, and T7 write areas for composition activation,
immutable revision patches, and a Studio review surface. P29 cannot start those
files until Gate 0 records one owner. Recommended resolution:

- P29 owns the shared Remotion registry correction, generic immutable visual
  patch contract, and finance-first Production Console.
- P16 consumes those shared foundations and retains the Martial Matters adapter,
  official skill routing, depth/SAM, deterministic/semantic QA, OTIO/FCP export,
  and its full internal preview.

# Human Gates

- **Gate 0 — ownership and isolation:** approve P29 as owner of the P16 overlap
  and create `codex/p29-remotion-production-console` in a clean worktree.
- **Gate A — information architecture:** approve the read-only console using a
  real current-bubble snapshot before mutation controls are added.
- **Gate B — bounded revision proof:** approve one scene where an approved
  stamped slide is selected, positioned, motion-adjusted, saved as a patch,
  recompiled, and previewed.
- **Gate C — render/review behavior:** approve queue behavior, failure display,
  before/after evidence, and the generated review packet.
- **Gate D — optional internal render:** approve any full-length render. No
  publish or promotion is authorized.
- **License checkpoint:** record the applicable Remotion use/license
  classification before production-scale rendering or broader operator access.

# Risk Controls

- Bind the bridge to `127.0.0.1`; reject non-loopback host configuration.
- Use root-contained, allowlisted paths and structured subprocess argument
  arrays; never accept shell command strings from the UI.
- Use a bounded single-worker render queue for MVP, with cancellation and
  explicit terminal states.
- Hash all canonical inputs and output patches; fail closed on stale hashes.
- Keep read-model compilation deterministic and artifact-backed.
- Run no external network/provider action from the console.
- Preserve source and approved artifacts; revisions are append-only.

# Recommended Sequence

1. Resolve P16 ownership and establish clean baseline evidence.
2. Define console snapshot and immutable revision-patch contracts.
3. Correct and centralize the Remotion composition registry.
4. Promote approved stamped slide renders into a stable production-visual
   catalog without changing their approval scope.
5. Build the loopback read/render bridge.
6. Build and approve the read-only Production Console.
7. Add bounded patch creation and deterministic recompilation.
8. Run one current-bubble scene through preview, patch, render, watch-review,
   and approval.
9. Measure, document, independently review, and only then consider expansion.

# Strategic Compact Decision

Research is complete enough for an implementation-ready PRP. After the PRP is
validated and approved, compact the task before invoking `prp-implement`; the
PRP and this file are the durable restart boundary.
