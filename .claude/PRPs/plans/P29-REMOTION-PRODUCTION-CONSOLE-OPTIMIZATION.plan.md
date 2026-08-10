---
id: P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION
title: Optimize Remotion around a local Production Console
status: running
operation: feature
risk: high
owner: parent
branch: codex/p29-remotion-production-console
created: 2026-08-10
updated: 2026-08-10
---

# Remotion Production Console Optimization

## Summary

Build a finance-first local Production Console around the existing Remotion
compositor. The console will combine a real-time Remotion Player preview with
scene order, word timing, approved production visuals, evidence provenance,
claim context, and review state. It will permit only bounded visual adjustments
and will save those adjustments as immutable revision patches that the existing
Python pipeline validates, recompiles, renders, and hands to the durable
watch-review loop.

The optimization target is the total production loop, not a speculative rewrite
or a general video editor. Remotion remains the deterministic rendering engine;
the console becomes the operator control surface; existing JSON artifacts remain
the source of truth.

## Intent And Acceptance

### Intent

- Reduce the current edit/review loop from scattered JSON, scripts, Studio tabs,
  contact sheets, and rendered files to one locally observable workflow.
- Let the operator see what a visual means, where it came from, what it is
  approved for, and which narration/cue/claim it serves before selecting it.
- Make common visual corrections directly controllable without opening a
  general NLE or hand-editing canonical artifacts.
- Keep every preview and render reproducible from pinned dependencies, hashed
  inputs, a typed snapshot, and an immutable patch.
- Establish measured Remotion baselines and optimize proven bottlenecks only.

### Acceptance

- A single documented local command starts the loopback bridge and Production
  Console for the current-bubble pilot without external provider calls.
- The console loads a schema-valid snapshot compiled from the pilot's existing
  scene-flow, scene bundles, pacing, overlay, cue, edit, claim, asset, audio,
  word-timing, approval, and review artifacts.
- The center preview uses `@remotion/player` pinned exactly to Remotion `4.0.502`
  and the same browser-safe composition component used by deterministic renders.
- The UI provides a scene queue, player, inspector, word/cue timeline, asset and
  evidence pane, approval-scope labels, validation errors, render status, and
  input/output hashes. Loading, empty, stale, and failed states are explicit.
- The six approved teacher-stamped decks are available as stable, hashed
  `production_visuals`; their records retain deck/slide context and do not claim
  evidence eligibility unless a separate evidence gate already grants it.
- For one current-bubble scene, the operator can select an approved stamped
  visual, adjust bounded position/crop/motion fields, save a revision patch,
  recompile, preview, render normal and diagnostic outputs, and produce a
  watch-review packet without changing canonical inputs.
- The bridge binds only to loopback, rejects paths outside configured roots,
  rejects arbitrary commands and unsupported patch operations, uses structured
  subprocess arguments, and exposes a bounded one-worker render queue with
  explicit queued/running/succeeded/failed/cancelled states.
- Stale base hashes, unknown assets, approval-scope mismatches, cue-boundary
  violations, and protected-field edits fail closed with structured errors.
- `EditorialMotion` is registered to `EditorialMotionComposition`; compositions
  are organized through one typed registry and Remotion folders; metadata and
  default props remain deterministic.
- All sequences that need early loading use premounting, and all render-time
  animation remains frame/fps driven rather than CSS animation or transitions.
- Baseline and post-change measurements use the same pinned fixture, machine,
  codec, scale, and concurrency. The optimized path has no greater than a 10%
  median render-time regression; any claimed improvement includes raw benchmark
  evidence. Console scene selection and bounded-control updates meet a local
  p95 target of 150 ms on the fixture, excluding media decode/render time.
- TypeScript, Python contract/security tests, a UI state test suite, a browser
  smoke test, the fixture render, focused legacy tests, and `git diff --check`
  pass. An independent reviewer records correctness and regression findings.
- No source deck, approved artifact, canonical audio, word timings, script,
  claim ledger, or previous revision is modified in place. No publish action is
  invoked.

## Scope

- A clean P29 worktree and baseline evidence for the current Remotion/editorial
  path.
- Typed schemas for the derived console snapshot, immutable visual revision
  patch, and local render-job state.
- A deterministic Python snapshot compiler that adapts existing artifacts rather
  than replacing them.
- A centralized browser-safe Remotion composition registry and correction of the
  existing `EditorialMotion` registration.
- A stable production-visual catalog derived from the already approved
  teacher-stamped PPTX slide images, including deck/slide/source hashes and
  approval scope.
- A loopback-only local service for snapshot reads, patch submission, validation,
  recompilation, render job control, and artifact discovery.
- A separate React/TypeScript Production Console using `@remotion/player` and a
  compact operator layout:
  - left: scene/beat queue and review state;
  - center: player and direct selection outline;
  - right: bounded inspector and validation;
  - bottom: narration words, cue bounds, events, and render state;
  - evidence drawer: asset provenance, deck/slide, claim links, representation
    mode, rights/evidence status, and production-visual approval.
- Immutable revision recompilation into the existing editorial-motion render
  path.
- One current-bubble end-to-end proof, benchmark packet, watch review, and
  operator gates.

## Not Building

- No general-purpose nonlinear editor, multi-track freeform timeline, arbitrary
  keyframe graph, color-grading suite, audio editor, or collaborative cloud app.
- No replacement of Remotion Studio; it remains the code/composition debugging
  surface.
- No direct browser filesystem writes, shell access, unbounded subprocesses,
  remote binding, authentication system, deployment, or public hosting.
- No mutation of script, narration, canonical audio, word timings, claim text,
  citations, rights, source media, source PPTX files, or prior approvals.
- No automatic claim checking, evidence promotion, rights approval, visual
  approval, or publish approval.
- No image generation, external provider invocation, paid render service, or
  provider credential handling.
- No SAM/depth pipeline, semantic visual QA, OTIO/FCP export, broad Martial
  Matters adapter, or full P16 completion.
- No dependency upgrade beyond exact-version additions required by the console.
  Remotion itself stays at `4.0.502` in P29 unless a separate approved upgrade
  plan demonstrates need and compatibility.
- No premature raw-speed rewrite. Optimize only measured hot paths.

## Human Gates

- **Gate 0 — P16 ownership and clean execution:** The operator approves P29 as
  owner of the overlapping P16 T2/T6/T7 shared foundations, or explicitly
  chooses an alternate division. Create and verify a clean
  `codex/p29-remotion-production-console` worktree before any implementation.
  P16 retains its Martial adapter, skill routing, depth/SAM, advanced QA,
  OTIO/FCP, and full-preview work.
- **Gate A — read-only console:** Review the real current-bubble snapshot and UI
  with mutation disabled. Approve information density, layout, evidence labels,
  scene navigation, and the distinction between `production_visuals` and
  evidence eligibility.
- **Gate B — revision round trip:** Approve one bounded change to one real scene:
  select an approved stamped asset, adjust allowed placement/crop/motion fields,
  save a patch, recompile, and preview before rendering.
- **Gate C — render and review:** Approve queue behavior, cancellation/failure
  states, normal/diagnostic outputs, before/after packet, and watch-review
  handoff.
- **Gate D — optional full internal preview:** Required before any full episode
  render. This gate does not authorize publishing or external promotion.
- **License checkpoint:** Record whether this local workflow falls under the
  applicable Remotion creator, company, or automator license before
  production-scale use or access by additional operators.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/compacts/P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION.compact.md`
- `.claude/PRPs/plans/P16-AGENT-NATIVE-EDITOR-DESIGN-TOOLCHAIN.plan.md`, especially
  T2, T6, and T7 ownership
- `.claude/PRPs/plans/P19-WATCH-REVIEW-DURABLE-LEARNING-LOOP.plan.md`
- `.claude/PRPs/plans/P28-DECK-ASSET-CONTEXT-EXTRACTION.plan.md`
- `content/video_engine/editor/package.json`
- `content/video_engine/editor/src/Root.tsx`
- `content/video_engine/editor/src/EditorialMotion.tsx`
- `content/video_engine/editor/src/types.ts`
- `content/video_engine/src/services/editorial_motion.py`
- `content/video_engine/src/services/animatic.py`, especially
  `render_editorial_motion_revision`
- `content/video_engine/src/guards/editorial_motion_qc.py`
- `content/video_engine/src/services/video_review_learning.py`
- `content/video_engine/cli.py`, especially
  `render-editorial-motion-revision`
- `content/video_engine/configs/editorial_motion_plan.schema.json`
- `content/video_engine/configs/finance_edit_manifest.schema.json`
- `content/video_engine/configs/finance_visual_cue_sheet_v2.schema.json`
- `content/video_engine/configs/finance_claim_ledger.schema.json`
- `content/video_engine/configs/deck_asset_manifest.v1.schema.json`
- `content/video_engine/projects/systems-and-blowups/sources/decks/deck-asset-manifest.json`
- `content/video_engine/projects/systems-and-blowups/sources/decks/asset-selection-index.md`
- `content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/review/teacher-stamped-sheets/teacher-stamped-decks-approval.v1.json`
- Official Remotion Player guidance:
  `https://www.remotion.dev/docs/player/`
- Official Remotion performance guidance:
  `https://www.remotion.dev/docs/performance/`
- Official Remotion metadata guidance:
  `https://www.remotion.dev/docs/calculate-metadata`
- `C:/Users/Snipe/.codex/skills/remotion-video-creation/SKILL.md`
- `C:/Users/Snipe/.codex/skills/frontend-patterns/SKILL.md`
- `C:/Users/Snipe/.codex/skills/backend-patterns/SKILL.md`

## Execution Path

1. Resolve the P16 overlap and create a clean P29 branch/worktree. Record git
   status, Node/npm versions, exact Remotion versions, Python version, hardware,
   and baseline typecheck/render results before touching editor code.
2. Define a console snapshot as a deterministic projection over current
   artifacts. Each record keeps its canonical artifact path and hash; the
   snapshot contains no independent claims or timings.
3. Define an immutable revision patch with `base_snapshot_hash`,
   `base_artifact_hashes`, `revision_id`, operator metadata, and an allowlisted
   sequence of visual operations. Protected fields are unrepresentable in the
   schema and rejected if injected.
4. Centralize composition metadata in one browser-safe registry. Point
   `EditorialMotion` at the dedicated component, group compositions with
   `<Folder>`, and keep props JSON-serializable and metadata deterministic.
5. Inventory the six approved teacher-stamped PPTX files. Extract slide images
   deterministically without altering source files, calculate hashes, preserve
   deck/slide context, and register them only as approved production visuals.
6. Implement a local service layer that compiles snapshots and validates patches.
   Wrap the existing compiler/render methods instead of duplicating timeline,
   asset, path, or QC logic.
7. Add a loopback API/command bridge with typed success/error envelopes,
   request/job IDs, structured logs, configured root allowlists, atomic writes,
   and a one-worker bounded render queue. It accepts operation identifiers and
   typed arguments, never shell text. Serve media only through stable snapshot
   asset IDs whose expected hashes still match; never expose filesystem paths.
8. Build the read-only console first. Use one derived client state model, compact
   decision-oriented panels, memoized selectors, virtualized long lists, explicit
   loading/error/empty/stale states, keyboard navigation, visible focus, and
   semantic controls. During development, Vite proxies same-origin `/media` and
   `/api` routes to the loopback bridge; the production build is served by that
   bridge. The shared composition therefore receives stable public-relative
   asset URLs and never a machine-specific path or untrusted remote URL.
9. Stop for Gate A. Correct information architecture or semantics before adding
   mutation controls.
10. Add only allowlisted visual controls: approved asset selection, crop/focal
    point, bounded transform/opacity/z, approved motion/camera/transition recipe,
    visual-event offset within cue bounds, caption safe band, approved teacher
    stamp variant, reviewer note, and shot status.
11. Submit a patch to the Python service. Revalidate source hashes and approval
    scope, write the patch atomically, recompile a new revision directory, and
    return validation plus artifact hashes to the UI. Never edit the base
    snapshot or canonical artifact.
12. Stop for Gate B on one current-bubble scene. On approval, render normal and
    diagnostic previews through the bounded queue and emit a before/after packet.
13. Compile a watch-review artifact, surface its state in the console, and stop
    for Gate C. Full-episode rendering remains behind Gate D.
14. Re-run the exact baseline benchmark. Tune concurrency only through recorded
    `remotion benchmark` evidence; address measured JavaScript/media/GPU costs,
    use premounting/preloading where required, and avoid unmeasured rewrites.
15. Run full focused verification, independent read-only review, documentation,
    and final evidence collection. Do not publish.

## Patterns To Mirror

- Mirror `AnimaticService.render_editorial_motion_revision()` for protected
  artifact hashing, job-local staging, revision-only outputs, zero-provider-call
  packets, and normal/diagnostic renders.
- Mirror `run_editorial_motion_qc()` for root containment, known asset IDs,
  schema validation, and fail-closed structural evidence.
- Mirror P19's watch-review compiler and append-only learning artifacts for
  review status; never store review truth only in browser state.
- Mirror P28's stable deck/slide IDs, parent hashes, context labels, and explicit
  promotion state for stamped production visuals.
- Mirror the current finance manifest's cue/asset/hash bindings instead of
  embedding source metadata into React components.
- Follow the service-layer pattern: handlers parse/authorize/dispatch; services
  own business rules; repositories/filesystem adapters own persistence.
- Use structured errors such as `{code, message, details, request_id}` and stable
  render states rather than parsing logs in the UI.
- Use the frontend decision-context pattern: scene, preview, evidence, approval,
  and actionable validation are primary; decorative dashboard metrics are not.
- Share browser-safe Remotion composition code between the Player and renderer;
  do not import Python bridge concerns into composition components.
- Follow official Remotion guidance: exact package-version parity, frame/fps
  animation, typed JSON props, `calculateMetadata`, asset preloading/premounting,
  verbose render evidence, and benchmarked concurrency.

## Task Slices

### T1: Resolve ownership and record a clean baseline
- Status: complete
- Owner: parent
- Depends on: Gate 0
- Write set: `.claude/PRPs/evidence/P29/baseline/**`; this PRP's Gate 0 and T1 evidence fields only
- Acceptance: P16/P29 ownership is recorded; a clean isolated P29 worktree exists; exact git commit, dirty-state check, Node/npm/Python/Remotion versions, machine profile, `npm ci`, TypeScript result, composition listing, one fixed fixture render, verbose slow-frame log, and benchmark inputs/results are captured. No implementation file changes occur in the dirty planning worktree.
- Validate: `git status --short; node --version; npm --version; python --version; npm --prefix content/video_engine/editor ci; npx --prefix content/video_engine/editor remotion versions; npm --prefix content/video_engine/editor run typecheck; npx --prefix content/video_engine/editor remotion compositions content/video_engine/editor/src/index.tsx`
- Evidence: `.claude/PRPs/evidence/P29/gate-0/decision.md`; `.claude/PRPs/evidence/P29/baseline/baseline.md`; `.claude/PRPs/evidence/P29/baseline/editorial-motion-baseline.mp4`. Exact Remotion parity and TypeScript/composition checks passed; fixed render completed; initial concurrency results were 3.82121s (1), 1.19331s (4), and 0.83799s (8).

### T2: Define console snapshot, patch, and render-job contracts
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/configs/production_console_snapshot.schema.json`; `content/video_engine/configs/editorial_visual_revision.schema.json`; `content/video_engine/configs/local_render_job.schema.json`; `content/video_engine/templates/production_console_snapshot.v1.json`; `content/video_engine/templates/editorial_visual_revision.v1.json`; `content/video_engine/tests/test_production_console_contracts.py`
- Acceptance: Schemas bind snapshots to canonical paths/hashes; distinguish production-visual approval, evidence eligibility, rights, and review state; model only allowlisted visual operations; require base hashes and append-only revision identity; and reject protected fields, unknown operations, stale versions, out-of-bounds timing/transforms, and malformed render states. Templates validate.
- Validate: `python -m pytest content/video_engine/tests/test_production_console_contracts.py -q`
- Evidence: `python -m pytest content/video_engine/tests/test_production_console_contracts.py -q` -> 7 passed. Schemas reject protected fields, arbitrary operations/commands, unsafe paths, and out-of-bounds transforms; both templates validate.

### T3: Compile a deterministic current-bubble console snapshot
- Status: complete
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/src/services/production_console_snapshot.py`; `content/video_engine/tests/test_production_console_snapshot.py`; fixture snapshots under `content/video_engine/tests/fixtures/production_console/**`; generated pilot snapshot under `content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/edit/production-console/`
- Acceptance: The compiler reads the existing scene, cue, edit, claim, asset, audio, word, approval, and review artifacts; emits stable ordering and hashes; records missing/degraded inputs explicitly; does not fabricate labels or approvals; and produces byte-identical output for unchanged inputs. No canonical source artifact is written.
- Validate: `python -m pytest content/video_engine/tests/test_production_console_snapshot.py content/video_engine/tests/test_production_console_contracts.py -q`
- Evidence: focused T2/T3/T5 contract tests -> 16 passed. Generated `edit/production-console/current-bubble.snapshot.v1.json` with hash `701befe9e657efd4ead0971a2645de843dc643ed486e3f3386e38e2e044d2f52`, 11 scenes, 2,445 canonical words, and 86 hash-verified production visuals; absent legacy project media is an explicit degradation.

### T4: Correct and centralize the Remotion composition registry
- Status: complete
- Owner: implementation_luna
- Depends on: T1, T2, and recorded P16 ownership transfer
- Write set: `content/video_engine/editor/src/Root.tsx`; `content/video_engine/editor/src/compositions.ts`; `content/video_engine/editor/src/EditorialMotion.tsx`; `content/video_engine/editor/src/types.ts`; `content/video_engine/editor/src/__fixtures__/production-console/**`; `content/video_engine/editor/src/__tests__/compositionRegistry.test.ts`; `content/video_engine/editor/package.json`; `content/video_engine/editor/package-lock.json`
- Acceptance: `EditorialMotion` uses `EditorialMotionComposition`; one typed browser-safe registry supplies IDs, components, default props, metadata, and folders; Player and renderer consume the same component contract; JSON props remain serializable; sequences needing early asset readiness premount; no CSS animation/transition controls render motion; exact Remotion version parity is enforced; legacy compositions still list and typecheck.
- Validate: `npm --prefix content/video_engine/editor ci; npm --prefix content/video_engine/editor run typecheck; npm --prefix content/video_engine/editor run test; npx --prefix content/video_engine/editor remotion versions; npx --prefix content/video_engine/editor remotion compositions content/video_engine/editor/src/index.tsx`
- Evidence: `npm --prefix content/video_engine/editor run typecheck` passed; registry tests -> 3 passed; exact Remotion parity remains `4.0.502`. All six legacy compositions are preserved, `EditorialMotion` maps to `EditorialMotionComposition`, and the shared `ProductionEvidence` Player/render composition is registered as a seventh console composition.

### T5: Register approved teacher-stamped slides as production visuals
- Status: complete
- Owner: junior_developer
- Depends on: T2
- Write set: `content/video_engine/scripts/extract_teacher_stamped_visuals.py`; `content/video_engine/tests/test_extract_teacher_stamped_visuals.py`; generated catalog and slide images under `content/video_engine/projects/systems-and-blowups/sources/decks/teacher-stamped-production-visuals/`
- Acceptance: All six approved teacher-stamped PPTX files are read without mutation; slide images receive stable deck/slide IDs, dimensions, hashes, source PPTX hash, and approval reference; unchanged reruns are deterministic; the catalog labels them `production_visuals` and preserves separate evidence/rights fields; missing approval, stale PPTX hash, duplicate IDs, or ambiguous slide media fails closed.
- Validate: `python -m pytest content/video_engine/tests/test_extract_teacher_stamped_visuals.py content/video_engine/tests/test_extract_deck_assets.py -q`
- Evidence: `python -m pytest content/video_engine/tests/test_extract_teacher_stamped_visuals.py -q` -> 4 passed. Six approved decks produced 86 deterministic, context-labelled visuals under `sources/decks/teacher-stamped-production-visuals/`; catalog hash `1ece077d6db23320030dc64abd57ac6845dccfbbdc11773087bcd7ac57b6ab96`. Every record is `render_eligible=true` and `evidence_render_eligible=false`.

### T6: Build the loopback-only Production Console bridge
- Status: complete
- Owner: implementation_luna
- Depends on: T3, T4, T5
- Write set: `content/video_engine/src/services/production_console.py`; `content/video_engine/src/services/local_render_queue.py`; `content/video_engine/cli.py`; `content/video_engine/tests/test_production_console.py`; `content/video_engine/tests/test_local_render_queue.py`
- Acceptance: A documented CLI starts only on `127.0.0.1`; read routes return typed snapshots/assets/revisions/reviews; media routes resolve only snapshot-known asset IDs and verify expected hashes without disclosing paths; render routes accept only typed operation IDs and root-contained artifact IDs; unsupported hosts, paths, commands, patch types, stale hashes, or queue overflow fail closed; writes are atomic; the one-worker queue supports queued/running/succeeded/failed/cancelled states; subprocesses use argument arrays; provider and publish commands are unreachable.
- Validate: `python -m pytest content/video_engine/tests/test_production_console.py content/video_engine/tests/test_local_render_queue.py content/video_engine/tests/test_editorial_motion_qc.py -q; python -m content.video_engine.cli production-console --help`
- Evidence: `python -m pytest content/video_engine/tests/test_production_console.py content/video_engine/tests/test_local_render_queue.py content/video_engine/tests/test_editorial_motion_qc.py -q` -> 23 passed. `python -m content.video_engine.cli production-console --help` exposes no host option; real health response confirms `loopback_only=true`. Browser payloads omit filesystem routing fields; media remains asset-ID and hash gated.

### T7: Build and approve the read-only React Production Console
- Status: awaiting Gate A
- Owner: implementation_luna
- Depends on: T3, T4, T5, T6
- Write set: `content/video_engine/production_console/**`, excluding generated runtime evidence
- Acceptance: A separate Vite React app pins `@remotion/player` to `4.0.502`; displays the scene queue, shared composition preview, inspector in disabled/read-only mode, word/cue timeline, approved asset/evidence drawer, review state, hashes, and bridge health; uses same-origin proxied API/media routes so the browser sees asset IDs rather than local paths; clearly distinguishes production-visual approval from evidence eligibility; uses a single derived state model, memoized selectors, virtualized long lists, explicit failure/loading/empty/stale states, keyboard navigation, visible focus, and no fabricated data. Gate A screenshots and operator decision are recorded before T8.
- Validate: `npm --prefix content/video_engine/production_console ci; npm --prefix content/video_engine/production_console run typecheck; npm --prefix content/video_engine/production_console run test; npm --prefix content/video_engine/production_console run build; npm --prefix content/video_engine/production_console run test:e2e`
- Evidence: Console `npm ci`, typecheck, 2 UI tests, production build, real headless browser smoke, and zero-vulnerability audit passed. Real current-bubble screenshots: `.claude/PRPs/evidence/P29/gate-a/production-console-read-only.png` and `production-console-scene-asset-navigation.png`. Snapshot hash `701befe9e657efd4ead0971a2645de843dc643ed486e3f3386e38e2e044d2f52`; operator decision remains pending before T8.

### T8: Implement immutable visual patches and recompilation
- Status: pending
- Owner: implementation_luna
- Depends on: T7 and Gate A
- Write set: `content/video_engine/src/services/editorial_revisions.py`; `content/video_engine/cli.py`; `content/video_engine/tests/test_editorial_revisions.py`; focused mutations under `content/video_engine/production_console/src/features/revisions/**`; generated revisions under `content/video_engine/runtime/jobs/current-bubble-mechanism-p29/animatic/revisions/`
- Acceptance: UI controls expose only the allowed operations; every patch binds base hashes and operator/revision identity; server validation rejects protected fields, stale inputs, unknown assets, approval mismatches, and cue-bound violations; successful application writes a new immutable revision, reuses canonical compile/QC logic, returns artifact hashes, and leaves base inputs byte-identical. The fixture change survives save, reload, recompile, and Player preview.
- Validate: `python -m pytest content/video_engine/tests/test_editorial_revisions.py content/video_engine/tests/test_editorial_motion.py content/video_engine/tests/test_editorial_motion_qc.py -q; npm --prefix content/video_engine/production_console run typecheck; npm --prefix content/video_engine/production_console run test; python -m content.video_engine.cli apply-editorial-revision --help`
- Evidence: pending

### T9: Run the current-bubble scene through render and watch review
- Status: pending
- Owner: parent
- Depends on: T8 and Gate B
- Write set: generated artifacts under `content/video_engine/runtime/jobs/current-bubble-mechanism-p29/`; generated review artifacts under `content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/review/production-console-p29/`; `.claude/PRPs/evidence/P29/gate-b/**`; `.claude/PRPs/evidence/P29/gate-c/**`
- Acceptance: One approved stamped visual is selected and adjusted without protected-field mutation; the exact patch and hashes are visible; normal and diagnostic renders complete through the queue; before/after stills and contact sheet are emitted; a durable watch-review artifact is compiled and displayed; queue failure/cancellation behavior is demonstrated; operator decisions for Gates B and C are recorded. No full render or publish occurs.
- Validate: `python -m content.video_engine.cli render-editorial-motion-revision --help; python content/video_engine/scripts/compile_watch_review.py --help; python -m pytest content/video_engine/tests/test_video_review_learning.py content/video_engine/tests/test_animatic.py -q`
- Evidence: pending

### T10: Measure optimization, close documentation, and review independently
- Status: pending
- Owner: parent
- Depends on: T9 and Gate C
- Write set: `content/video_engine/editor/package.json`; `content/video_engine/editor/package-lock.json`; measured optimization changes limited to reviewed hot-path files under `content/video_engine/editor/src/`; `content/video_engine/production_console/README.md`; `docs/content-video-engine/23-REMOTION-PRODUCTION-CONSOLE.md`; `.claude/PRPs/evidence/P29/benchmark/**`; `.claude/PRPs/reviews/P29-review.md`; this PRP status/evidence fields
- Acceptance: The same fixture and environment are used for before/after measurements; any concurrency change is supported by `remotion benchmark`; verbose logs identify addressed slow frames; render median regresses no more than 10%; UI local-state interaction p95 is at most 150 ms excluding media work; one command starts the local workflow; restart/recovery and artifact locations are documented; full focused tests pass; an independent reviewer records no unresolved blocking correctness, security, or regression issue. Gate D remains pending unless separately approved.
- Validate: `npm --prefix content/video_engine/editor run typecheck; npm --prefix content/video_engine/editor run test; npm --prefix content/video_engine/production_console run typecheck; npm --prefix content/video_engine/production_console run test; npm --prefix content/video_engine/production_console run build; npm --prefix content/video_engine/production_console run test:e2e; python -m pytest content/video_engine/tests/test_production_console_contracts.py content/video_engine/tests/test_production_console_snapshot.py content/video_engine/tests/test_extract_teacher_stamped_visuals.py content/video_engine/tests/test_production_console.py content/video_engine/tests/test_local_render_queue.py content/video_engine/tests/test_editorial_revisions.py content/video_engine/tests/test_editorial_motion.py content/video_engine/tests/test_editorial_motion_qc.py content/video_engine/tests/test_animatic.py content/video_engine/tests/test_video_review_learning.py -q; python scripts/prp_validate.py .claude/PRPs/plans/P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION.plan.md; git diff --check`
- Evidence: pending

## Verification

### Planning validation

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION.plan.md
```

### Baseline and dependency parity

```powershell
npm --prefix content/video_engine/editor ci
npx --prefix content/video_engine/editor remotion versions
npm --prefix content/video_engine/editor run typecheck
npx --prefix content/video_engine/editor remotion compositions content/video_engine/editor/src/index.tsx
```

### Python contracts, bridge, security, and revision behavior

```powershell
python -m pytest `
  content/video_engine/tests/test_production_console_contracts.py `
  content/video_engine/tests/test_production_console_snapshot.py `
  content/video_engine/tests/test_extract_teacher_stamped_visuals.py `
  content/video_engine/tests/test_production_console.py `
  content/video_engine/tests/test_local_render_queue.py `
  content/video_engine/tests/test_editorial_revisions.py `
  content/video_engine/tests/test_editorial_motion.py `
  content/video_engine/tests/test_editorial_motion_qc.py `
  content/video_engine/tests/test_animatic.py `
  content/video_engine/tests/test_video_review_learning.py -q
```

### Console and shared Remotion component

```powershell
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run test
npm --prefix content/video_engine/production_console ci
npm --prefix content/video_engine/production_console run typecheck
npm --prefix content/video_engine/production_console run test
npm --prefix content/video_engine/production_console run build
npm --prefix content/video_engine/production_console run test:e2e
```

### Fixed-fixture benchmark

Record the exact fixture, commit, hardware, codec, scale, concurrency, fps,
resolution, frame range, command, wall time, slow-frame log, and output hash for
every run. Use at least three baseline and three post-change runs and compare
medians. Use `npx remotion benchmark` before changing concurrency. Do not mix
warm and cold runs without labeling them.

```powershell
npx --prefix content/video_engine/editor remotion benchmark `
  content/video_engine/editor/src/index.tsx EditorialMotion `
  --props content/video_engine/editor/src/__fixtures__/production-console/current-bubble-scene.json
```

The implementation slice must add a deterministic fixture-render script with
fixed output options rather than relying on an undocumented ad hoc command.

### Final repository checks

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P29-REMOTION-PRODUCTION-CONSOLE-OPTIMIZATION.plan.md
git diff --check
git status --short
```

## Evidence And Handoff

- Store baseline and post-change environment, command, raw logs, timing samples,
  medians, output hashes, and slow-frame findings under
  `.claude/PRPs/evidence/P29/benchmark/`.
- Store Gate 0 ownership/worktree evidence under
  `.claude/PRPs/evidence/P29/gate-0/`.
- Store Gate A screenshots, snapshot hash, information-architecture notes, and
  operator decision under `.claude/PRPs/evidence/P29/gate-a/`.
- Store Gate B base hashes, patch, recompiled hashes, before/after stills, and
  operator decision under `.claude/PRPs/evidence/P29/gate-b/`.
- Store Gate C queue-state proof, normal/diagnostic renders, contact sheet,
  watch-review artifact, and operator decision under
  `.claude/PRPs/evidence/P29/gate-c/`.
- Generated runtime media belongs below
  `content/video_engine/runtime/jobs/current-bubble-mechanism-p29/`; canonical
  project artifacts remain immutable.
- Independent review belongs at `.claude/PRPs/reviews/P29-review.md` and must
  identify exact files, tests, and unresolved findings rather than summarize
  agent confidence.
- Completion requires artifact paths, hashes, test output, benchmark evidence,
  and recorded human gate decisions. A passing UI demo alone is not completion.
- After this draft is approved, use `strategic-compact` before
  `prp-implement`; resume from this PRP, the compact, and Gate 0 rather than the
  conversation transcript.
