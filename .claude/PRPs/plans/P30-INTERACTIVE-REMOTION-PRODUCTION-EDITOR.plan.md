---
id: P30-INTERACTIVE-REMOTION-PRODUCTION-EDITOR
title: Build the interactive Remotion Production Editor
status: running
operation: feature
risk: high
owner: parent
branch: codex/p30-interactive-remotion-production-editor
created: 2026-08-10
updated: 2026-08-11
---

# Interactive Remotion Production Editor

## Summary

Expand the P29 Production Console into a reusable evidence-aware timeline and
canvas editor, proven on `current-bubble-mechanism`. Remotion remains the
deterministic renderer. The browser owns a typed draft; immutable, hash-bound
revisions remain the only persistence path.

P29 was not merged when P30 was approved. Its tested Gate A baseline was
checkpointed as commit `8779ac9` and P30 branches directly from that commit.
P29 T8-T10 are superseded by the broader P30 revision, proof, and review slices;
P16 retains Martial adaptation, depth/SAM, advanced QA, OTIO/FCP, and full
preview ownership.

## Intent And Acceptance

- Provide a full-episode timeline with scene focus, ruler, playhead, zoom,
  scrolling, snapping, semantic tracks, and frame-accurate visual-item edits.
- Keep one approved narration source immutable while allowing word-gap
  head/tail trim, level, scene boundaries, and cue boundaries.
- Provide direct canvas selection, move/scale/rotate/crop/opacity/z controls,
  safe guides, multi-select, alignment, and property keyframes.
- Allow editable overlay text while transcript wording and word timing remain
  locked; caption style/grouping/line breaks may change.
- Expose a curated Remotion Bits palette with typed adapters and a reviewed
  on-demand intake path; never fetch or execute live code in the browser.
- Save a revision, reload it, recompile derived artifacts, and render the same
  draft without changing source audio, evidence, approval, or prior revisions.
- Stale hashes, path escape, unknown assets/components, invalid frames,
  unsupported props, transcript changes, and approval changes fail closed.

## Scope

- `production_console_snapshot.v2`, `editorial_timeline_revision.v1`,
  `editor_component_catalog.v1`, and `editor_component_preset.v1` contracts.
- Deterministic snapshot-v2 and component-catalog compilers over existing P29
  artifacts, including cached waveform peaks keyed to canonical audio hash.
- Fixed tracks for scenes/cues, captions, overlays/annotations, teacher stamp,
  evidence, world plates, and locked narration.
- A custom React timeline using only public `@remotion/player` APIs.
- Canvas and inspector editing plus a 100-command undo/redo draft history.
- Eleven pinned, adapted Remotion Bits and a local enable-request workflow.
- Loopback validation/application endpoints and one current-bubble proof.

## Not Building

- No narration replacement, splicing, word retiming, music/SFX mixer, arbitrary
  plugins, live code installation, graph editor, cloud collaboration, publish,
  evidence promotion, rights approval, or source-artifact mutation.
- No dependency on Remotion Studio internals or `@remotion/timeline-utils`.
- No automatic import of the remaining Remotion Bits catalog.

## Human Gates

- **Gate 0 — baseline:** satisfied by tested P29 commit `8779ac9`, explicit P30
  approval, isolated P30 branch, and recorded dependency deviation.
- **Gate A — interaction:** operator reviews timeline, canvas, inspector, and
  keyboard behavior on real current-bubble data.
- **Gate B — components:** operator reviews the curated Remotion Bits palette
  and editable component workflow.
- **Gate C — revision:** operator reviews one immutable real-scene round trip.
- **Gate D — render:** operator reviews normal/diagnostic outputs and watch
  packet. No gate authorizes publication.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/plans/P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION.plan.md`
- `.claude/PRPs/plans/P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.plan.md`
- `content/video_engine/configs/editorial_visual_revision.schema.json`
- `content/video_engine/src/services/production_console_snapshot.py`
- `content/video_engine/src/services/production_console.py`
- `content/video_engine/production_console/src/App.tsx`
- `content/video_engine/editor/src/EditorialMotion.tsx`
- Official Remotion timeline and Player documentation and Remotion Bits 0.2.0
  documentation/repository.

## Execution Path

1. Add versioned contracts and compile snapshot v2 from existing canonical
   artifacts without changing v1 behavior.
2. Pin Remotion Bits metadata and build a closed typed component registry.
3. Implement a framework-independent draft reducer, frame math, snapping,
   keyframes, selection, history, and local recovery.
4. Synchronize the Player and timeline via `PlayerRef.seekTo()` and
   `frameupdate`; update the playhead imperatively rather than rerendering the
   full application each frame.
5. Add semantic timeline tracks, canvas handles, inspector, palettes, and
   explicit protected/read-only fields.
6. Validate and replay immutable revision operations server-side; write only
   new revision directories with hashes and structured errors.
7. Prove one real current-bubble edit and stop at human render gates.

## Patterns To Mirror

- P29 snapshot hashing, asset-ID media routing, loopback containment, and
  structured bridge errors.
- P16/P29 immutable revision-only artifacts and canonical hash chains.
- Remotion `<Sequence>` with premounting, frame/fps animation, typed JSON props,
  and one shared composition for Player and render.
- Remotion Studio's separation of zoom, scroll geometry, selection, and
  imperative playhead state without copying internal code.

## Task Slices

### T1: Add timeline and component contracts
- Status: complete
- Owner: implementation_luna
- Depends on: Gate 0
- Write set: `content/video_engine/configs/*timeline*`; `content/video_engine/configs/editor_component_*`; focused contract tests
- Acceptance: all four schemas validate deterministic fixtures and reject protected or unbounded fields.
- Validate: `python -m pytest content/video_engine/tests/test_production_editor_contracts.py -q`
- Evidence: `content/video_engine/configs/production_console_snapshot.v2.schema.json`; `content/video_engine/configs/editorial_timeline_revision.schema.json`; `content/video_engine/configs/editor_component_catalog.schema.json`; `content/video_engine/configs/editor_component_preset.schema.json`

### T2: Compile snapshot v2 and component catalog
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/src/services/production_editor.py`; focused compiler tests and generated current-bubble snapshot v2
- Acceptance: v2 contains project profile, fixed tracks/items, frames, words, cues, locks, waveform peaks, approved assets, catalog, and stable hashes; v1 output is unchanged.
- Validate: `python -m pytest content/video_engine/tests/test_production_editor.py content/video_engine/tests/test_production_console_snapshot.py -q`
- Evidence: `content/video_engine/src/services/production_editor.py`; current-bubble snapshot hash `e7f57f67471e440e050072829cebebc13f91aa7d6d78d65e81b060defe7266a0`

### T3: Add the editor kernel
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/production_console/src/editor/**`
- Acceptance: pure timeline math, command reducer, history, selection, snapping, keyframes, and draft recovery are covered by deterministic tests.
- Validate: `npm --prefix content/video_engine/production_console run test`
- Evidence: `content/video_engine/production_console/src/editor/`; 100-command history, frame math, snapping, keyframes, selection, and draft tests

### T4: Add the shared timeline composition and Bits adapters
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/editor/src/ProductionTimelineComposition.tsx`; `content/video_engine/editor/src/remotionBits/**`; editor tests
- Acceptance: all supported item types and eleven allowlisted Bits render from typed props using frame-driven animation and premounted Sequences.
- Validate: `npm --prefix content/video_engine/editor run typecheck; npm --prefix content/video_engine/editor run test`
- Evidence: `content/video_engine/editor/src/ProductionTimelineComposition.tsx`; `content/video_engine/editor/src/remotionBits/`; `.claude/PRPs/evidence/P30/remotion-bits-provenance.md`

### T5: Build timeline, canvas, inspector, and palettes
- Status: complete
- Owner: parent
- Depends on: T2, T3, T4
- Write set: `content/video_engine/production_console/src/**`; console tests and styles, excluding T3-owned editor kernel
- Acceptance: real snapshot v2 drives Player, tracks, zoom, scrub, drag/trim, canvas transforms, keyframes, assets, annotations, text, teacher stamp, Bits, evidence, and protected fields.
- Validate: `npm --prefix content/video_engine/production_console run typecheck; npm --prefix content/video_engine/production_console run test; npm --prefix content/video_engine/production_console run build; npm --prefix content/video_engine/production_console run test:e2e`
- Evidence: `.claude/PRPs/evidence/P30/gate-a/current-bubble-editor-assets.png`; `.claude/PRPs/evidence/P30/gate-b/current-bubble-edited-workspace.png`

### T6: Validate and apply immutable timeline revisions
- Status: complete
- Owner: implementation_luna
- Depends on: T1, T2
- Write set: `content/video_engine/src/services/production_editor_revisions.py`; production-console bridge/CLI endpoints; focused tests
- Acceptance: revision validation and replay fail closed, preserve canonical hashes, and write only new revision directories.
- Validate: `python -m pytest content/video_engine/tests/test_production_editor_revisions.py content/video_engine/tests/test_production_console.py -q`
- Evidence: `content/video_engine/src/services/production_editor_revisions.py`; runtime revision `revision-02e8c1d08dd68f98`

### T7: Run the current-bubble proof and review
- Status: complete
- Owner: parent
- Depends on: T5, T6, Gates A and B
- Write set: generated P30 revision/render evidence; P30 gate records; PRP status/evidence fields
- Acceptance: one real edit retimes scene/cue, places approved evidence, edits text, adds annotation/stamp, applies a Bit and keyframes, saves/reloads/recompiles, and produces review artifacts.
- Validate: focused Python/TypeScript/browser suites plus normal and diagnostic fixture renders
- Evidence: `.claude/PRPs/evidence/P30/gate-c/final-roundtrip.json`; `.claude/PRPs/evidence/P30/gate-d/current-bubble-normal-still.png`; `.claude/PRPs/evidence/P30/gate-d/current-bubble-diagnostic-still.png`; runtime revision `revision-02e8c1d08dd68f98`

### T8: Performance, documentation, and independent review
- Status: complete
- Owner: parent
- Depends on: T7
- Write set: P30 benchmark/review evidence and production-editor documentation
- Acceptance: the 980.806-second fixture remains responsive, no full-app frame rerender occurs, documentation is complete, and independent review has no unresolved blocker.
- Validate: complete focused suites, PRP validation, `git diff --check`
- Evidence: `.claude/PRPs/evidence/P30/benchmark/current-bubble-performance.md`; `.claude/PRPs/evidence/P30/gate-b/evidence-rail-proof.md`; `content/video_engine/production_console/README.md`; `.claude/PRPs/reviews/P30-review.md` (PASS)

## Verification

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P30-INTERACTIVE-REMOTION-PRODUCTION-EDITOR.plan.md
python -m pytest content/video_engine/tests/test_production_editor_contracts.py content/video_engine/tests/test_production_editor.py content/video_engine/tests/test_production_editor_revisions.py -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run test
npm --prefix content/video_engine/production_console run typecheck
npm --prefix content/video_engine/production_console run test
npm --prefix content/video_engine/production_console run build
npm --prefix content/video_engine/production_console run test:e2e
git diff --check
```

## Evidence And Handoff

- Store baseline, schema, UI, proof, benchmark, and human-gate evidence under
  `.claude/PRPs/evidence/P30/`.
- Store generated revisions beneath
  `content/video_engine/runtime/jobs/current-bubble-mechanism-p30/`.
- Store independent findings at `.claude/PRPs/reviews/P30-review.md`.
- Completion requires artifacts, hashes, tests, browser proof, and gate records;
  a passing mock UI is not completion.
