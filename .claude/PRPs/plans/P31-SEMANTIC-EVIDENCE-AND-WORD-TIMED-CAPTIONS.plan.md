---
id: P31-SEMANTIC-EVIDENCE-AND-WORD-TIMED-CAPTIONS
title: Bind PowerPoint evidence to world plates and add word-timed captions
status: review
operation: feature
risk: high
owner: parent
branch: codex/p31-semantic-evidence-and-word-timed-captions
created: 2026-08-11
updated: 2026-08-11
---

# Semantic Evidence And Word-Timed Captions

## Summary

Turn the P30 Production Editor from a generic visual-item editor into the
intended finance storytelling system: a full-frame woodblock world plate with
one subordinate, approved PowerPoint evidence crop drawn into available space,
one short annotation path, and readable captions synchronized to canonical
word timing.

The current screenshot is a contract failure, not a styling problem.
`overlay-map.v1.json` stores citation identifiers such as
`memory-bottleneck-not-bubble-inference` in its `text` field, and P30 compiles
that field into a visible annotation. P31 separates renderable copy from
editor/debug metadata so internal IDs, labels, paths, and semantic tags can
never appear in a normal render.

P31 also adds deterministic semantic recommendations that match the current
cue, claim, world plate, and open layout slot to approved, hash-bound semantic
crops extracted from the PowerPoint decks. The operator accepts or replaces a
recommendation; the matcher never silently authors the timeline. Finally, the
curated Remotion Bits Word by Word component is adapted as a caption renderer
driven by the immutable narration word records rather than its current fixed
stagger.

## Intent And Acceptance

- Normal Player and render output never displays internal claim IDs, asset
  IDs, source refs, filenames, semantic tags, fallback labels, or kebab-case
  slugs. Diagnostics may display them only behind an explicit diagnostic flag.
- Citation overlays become metadata/source bindings. A source marker may be
  displayed only through an explicit reviewed display contract; the claim ID
  itself is never display copy.
- The editor recommends approved PowerPoint semantic crops for a cue and world
  plate using a deterministic, inspectable score and records candidate scores,
  rejection reasons, source hashes, and the proposed layout slot.
- An operator can insert the recommended crop into the proposed slot, inspect
  why it matched, replace it, or leave the cue unmatched. Recommendations do
  not mutate the draft until accepted.
- The rendered visual grammar is enforced: one full-frame world plate, at most
  one active evidence crop, one reveal hand, one short annotation/leader path,
  and one small source marker. PowerPoint evidence is subordinate and never
  becomes the hero composition.
- `memory-skepticism-v2` uses its three bottom evidence slots sequentially;
  `hero-fab-constraint-v1` uses a smaller off-center field-note slot anchored
  away from the factory hero. A safe generic off-center profile handles plates
  without a reviewed custom profile.
- Word by Word captions use canonical word start/end frames, preserve the exact
  approved transcript, remain stable at punctuation and line wraps, and do not
  create a duplicate standalone Remotion Bit text item.
- One representative sequence proves semantic recommendation, operator
  acceptance, hand reveal, evidence retraction, word-timed captions, immutable
  revision save/reload, and deterministic Player/render parity.

## Scope

- Render-safe text/display contracts for timeline items and citation metadata.
- A versioned `plate_layout_profile.v1` contract for evidence, annotation,
  source-marker, and caption-safe regions.
- A versioned `semantic_evidence_binding.v1` derived artifact containing
  features, ranked candidates, score breakdowns, thresholds, rejections,
  accepted asset/slot bindings, and source hashes.
- Deterministic semantic feature extraction over existing cue, beat, claim,
  motion-plan, world-plate, and deck semantic-asset metadata.
- An editor recommendation panel with rationale and explicit accept/replace
  controls.
- A canonical-timing adapter for the curated Remotion Bits Word by Word
  component and a caption-style selector.
- A current-bubble proof using approved PowerPoint crops on
  `memory-skepticism-v2` and `hero-fab-constraint-v1`.

## Not Building

- No live LLM, embedding API, network search, browser-side model, or
  nondeterministic semantic ranking.
- No automatic evidence insertion, episode-wide auto-edit, or silent timeline
  mutation.
- No unapproved asset, full-slide takeover, second simultaneous evidence card,
  or evidence/rights promotion.
- No transcript rewrite, paraphrase, word retiming, narration replacement, or
  caption copy generated independently from canonical words.
- No arbitrary Remotion Bit props, arbitrary React execution, free-form
  caption animation graph, or new third-party runtime.
- No mutation of source decks, extracted semantic assets, source maps, P30
  revisions, canonical audio, or prior render artifacts.
- No publication.

## Current Evidence And Root Cause

- `edit/word-timed-v1/overlay-map.v1.json` contains citation entries whose
  `text` equals internal claim IDs such as
  `memory-bottleneck-not-bubble-inference`.
- `_overlay_track_items()` in
  `content/video_engine/src/services/production_editor.py` currently converts
  those citation entries into visible annotation items and copies `text` into
  the snapshot.
- `ProductionTimelineComposition.tsx` has generic text/label fallback paths;
  renderable copy and editor labels are not contractually separate.
- Approved deck crops already carry stable asset IDs, hashes, deck/slide
  provenance, `what_it_is`, `visual_role`, representation mode, factual-text
  state, claim/cue references, review state, and rights state. Some early crops
  have empty claim/cue references, so matching cannot depend on those fields
  alone.
- `editorial-beat-plan.v1.json` supplies narration excerpts and claim refs;
  `editorial-motion-plan.v1.json` connects beats, shots, and world plates.
- The curated Word by Word adapter currently splits text and applies one fixed
  `staggerFrames` value. It does not consume canonical per-word frame ranges.

## Product Rules

### Renderable text boundary

- `display_text` is the only general-purpose authored copy accepted by normal
  overlay rendering. `label`, `item_id`, `asset_id`, `source_ref`,
  `citation_id`, paths, and semantic fields are metadata-only.
- Transcript captions render only from canonical word records and their
  immutable text projection; they do not accept arbitrary `display_text`.
- Citation records bind a claim/source to evidence. Missing display copy
  renders nothing in normal mode rather than falling back to an identifier.
- Diagnostic labels are rendered through a separate diagnostic component and
  are impossible to enable in a normal render invocation by item props alone.
- Validation rejects attempts to copy protected identifiers into display text
  for generated citation/source items. Explicit operator-authored overlay text
  remains editable under the existing revision contract.

### Evidence hierarchy and clutter budget

Every evidence beat follows:

`world plate -> hand opens one evidence slot -> evidence crop appears -> one annotation connects it -> evidence retracts -> world continues`

At any frame the compiler permits:

- one full-frame `world_plate`;
- zero or one `evidence_image`;
- zero or one reveal hand associated with that evidence item;
- zero or one short annotation/leader path;
- zero or one compact source marker;
- one caption group within a non-conflicting safe region.

Evidence cards target approximately 18-32% of the frame and are placed in
reviewed negative space. The matcher penalizes overlap with the plate focal
point, principal character, factory/object hero, caption zone, and active
annotation. If no reviewed slot is safe, the recommendation is `manual_only`.

### Semantic recommendation model

The matcher is deterministic and ordered by evidence strength:

1. Exact cue reference and exact claim reference.
2. Claim relationships inherited from the parent beat and claim ledger.
3. Evidence-role compatibility (`mechanism`, `comparison`, `metric`,
   `timeline`, `source_quote`) with the cue's visual intent.
4. Normalized concept overlap among narration excerpt, claim title/summary,
   deck `what_it_is`, extracted factual text, deck/slide title, and controlled
   finance synonyms.
5. World-plate and slot compatibility from the layout profile.
6. Reuse policy, adjacency, readability, and clutter penalties.

The artifact records the contribution from every scoring feature. Only assets
that are render-eligible, factually approved, rights-eligible, hash-valid, and
compatible with the active cue may rank. A minimum score and minimum lead over
the runner-up are required. Below either threshold, the result is
`unmatched`; the system never guesses.

The first implementation uses structured references plus deterministic
normalized text/concept matching. It does not add a model dependency. A later
version may add a pinned local embedding index only if review evidence shows
the transparent matcher cannot rank the approved deck corpus reliably.

### Plate layout profiles

- `memory-skepticism-v2`: three sequential lower evidence slots corresponding
  to teal, navy, and orange cards; source marker remains inside the selected
  card boundary; caption zone avoids the active card.
- `hero-fab-constraint-v1`: one smaller off-center field-note slot anchored to
  a manufacturing station; no center overlay over the factory.
- Generic profile: one off-center negative-space card, conservative scale,
  no placement across the central focal region, and `manual_only` when the
  configured safe region is unavailable.
- Profiles use normalized geometry and are hash-bound configuration, not
  renderer conditionals scattered across React components.

### Word-timed caption behavior

- Word by Word is a `transcript_caption` presentation preset, not a separate
  `remotion_bit` timeline item.
- The adapter receives immutable word tokens with absolute or item-relative
  start/end frames. A token activates at its canonical start frame; punctuation
  stays attached to its word.
- Caption grouping remains operator-selectable within protected transcript
  boundaries. The proof compares the current compact caption treatment with a
  Word by Word treatment before changing any default.
- The prototype supports at most two stable lines, avoids per-word layout
  reflow, preserves approved line breaks, and uses restrained emphasis rather
  than every word entering from a large offset.
- Caption placement uses the plate profile and current evidence slot so it does
  not compete with the evidence rail or hero subject.

## Contracts And Architecture

### `plate_layout_profile.v1`

Each profile contains:

- stable profile and world-asset IDs plus source asset hash;
- normalized focal/protected regions;
- ordered evidence slots with size limits, alignment, and semantic roles;
- caption-safe regions and conflict fallbacks;
- annotation anchors and maximum leader-line length;
- source-marker placement;
- maximum simultaneous item counts;
- profile status (`reviewed`, `experimental`, `manual_only`).

### `semantic_evidence_binding.v1`

Each immutable derived artifact contains:

- project, snapshot, cue, beat, claim, motion-plan, plate-profile, asset-catalog,
  and approval hashes;
- normalized cue/claim/world semantic features;
- eligible and rejected asset candidates;
- per-feature score breakdown, total score, rank, threshold, and lead margin;
- proposed evidence slot, caption zone, annotation anchor, and frame range;
- recommendation state (`recommended`, `unmatched`, `manual_only`);
- accepted asset and slot only after an operator revision operation;
- compiler version and deterministic artifact hash.

### Snapshot and revision compatibility

- Extend snapshot v2 additively with display-safe fields, plate profiles, and
  semantic recommendations; do not change v1 behavior.
- Add a bounded `accept_evidence_binding` revision operation or compile an
  accepted recommendation into the existing typed `insert_item` operation
  with immutable binding provenance. Select the smaller contract after T1
  fixture validation; never accept an opaque recommendation blob.
- Preserve existing visual revisions. Recompilation derives new runtime
  artifacts without changing source maps, approvals, or prior revisions.
- Player and deterministic render consume the same resolved timeline document,
  word records, layout profile, and asset map.

## Human Gates

- **Gate 0 — baseline and ownership:** P30 reaches a reviewed, reproducible
  checkpoint; P31 has an isolated branch/worktree or an explicitly approved
  continuation; current dirty files are inventoried; P30 contracts remain
  compatible. No P31 implementation starts before this gate.
- **Gate A — safe render and placement:** operator reviews normal/diagnostic
  stills proving internal labels are absent and approves the plate slot/profile
  overlays for `memory-skepticism-v2` and `hero-fab-constraint-v1`.
- **Gate B — semantic ranking:** operator reviews grouped recommendations and
  score rationales for representative valuation, capacity-penalty, supply-shock,
  and fab-constraint cues. False matches or ambiguous results must remain
  unmatched.
- **Gate C — captions:** operator compares current captions against Word by Word
  on short, medium, punctuation-heavy, and fast cues and approves the treatment
  before it becomes a selectable production preset.
- **Gate D — revision and render:** operator reviews one immutable accepted
  evidence binding through save/reload/recompile plus normal and diagnostic
  renders. No gate authorizes publication.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/plans/P28-DECK-ASSET-CONTEXT-EXTRACTION.plan.md`
- `.claude/PRPs/plans/P30-INTERACTIVE-REMOTION-PRODUCTION-EDITOR.plan.md`
- `content/video_engine/src/services/production_editor.py`
- `content/video_engine/src/services/production_editor_revisions.py`
- `content/video_engine/production_console/src/App.tsx`
- `content/video_engine/production_console/src/features/production-editor/snapshotDocument.ts`
- `content/video_engine/editor/src/ProductionTimelineComposition.tsx`
- `content/video_engine/editor/src/remotionBits/adapters.tsx`
- Current-bubble beat, claim, cue, motion, overlay, asset, approval, and deck
  semantic-context artifacts.

## Execution Path

1. Checkpoint P30, reproduce the screenshot from the saved snapshot/revision,
   and freeze normal-versus-diagnostic display semantics.
2. Stop citation-ID leakage at the compiler and renderer boundaries, with
   contract and frame-level regression tests.
3. Add reviewed plate profiles and compile a deterministic semantic evidence
   index from existing approved artifacts.
4. Rank evidence candidates with transparent scoring, strict eligibility, and
   ambiguity thresholds; persist recommendations as derived artifacts.
5. Expose recommendations and rationale in the editor; require explicit
   operator acceptance and preserve manual override.
6. Adapt Word by Word to canonical word timings and expose it as a protected
   transcript-caption preset.
7. Prove the complete world/evidence/annotation/caption grammar on two real
   plates, save an immutable revision, and render from the accepted artifact.

## Patterns To Mirror

- P28 hash-bound semantic crop provenance and grouped review artifacts.
- P30 snapshot hashing, closed typed item/component registries, asset-ID media
  routing, revision replay, structured bridge errors, and shared Player/render
  composition.
- Existing hand-drawn evidence reveal and evidence-rail proof, retaining the
  hand, one-card limit, and subordinate crop scale.
- Remotion frame/fps-driven animation with no timers, random values, live
  fetches, or per-frame application rerenders.
- Frontend-patterns separation of domain state, command state, interaction
  state, and render state; item-specific inspector controls rather than raw
  JSON.

## Task Slices

### T0: Checkpoint P30 and freeze the failing fixture
- Status: complete
- Owner: parent
- Depends on: approved P31 plan
- Write set: P31 baseline evidence and plan status only
- Acceptance: P30 has a reproducible tested checkpoint; the exact citation-ID
  leak is captured from a hash-bound snapshot/revision; dirty user changes are
  inventoried and preserved; branch/worktree ownership is recorded.
- Validate: focused P30 Python/TypeScript suites; `git status --short`;
  `git diff --check`
- Evidence: `.claude/PRPs/evidence/P31/baseline/checkpoint.md`; P30 focused
  Python suite `17 passed`; editor `11 passed`; console `19 passed`; console
  production build passed; branch
  `codex/p31-semantic-evidence-and-word-timed-captions` preserves the reviewed
  P30 working tree without rewriting its uncommitted files.

### T1: Enforce render-safe text and citation contracts
- Status: complete
- Owner: implementation_luna
- Depends on: T0
- Write set: `content/video_engine/configs/production_console_snapshot.v2.schema.json`;
  focused compiler/renderer display contracts and tests
- Acceptance: authored display copy, transcript copy, citation metadata, and
  diagnostic labels are distinct typed fields; normal snapshots cannot route
  protected IDs into display text; old valid visual revisions still load.
- Validate: `python -m pytest content/video_engine/tests/test_production_editor_contracts.py -q`;
  editor contract tests
- Evidence: `.claude/PRPs/evidence/P31/t1/render-safe-contract.md`; focused
  compiler/contracts `7 passed`; editor typecheck and `11 passed`; console
  typecheck and `19 passed`.

### T2: Remove identifier leakage from compilation and rendering
- Status: complete
- Owner: junior_developer
- Depends on: T1
- Write set: focused citation compilation in
  `content/video_engine/src/services/production_editor.py`; focused text paths
  in `content/video_engine/editor/src/ProductionTimelineComposition.tsx`;
  regression tests
- Acceptance: citation entries compile as metadata/source bindings; missing
  display copy renders nothing in normal mode; explicit diagnostic mode remains
  useful; no generic label fallback reaches normal frames.
- Validate: `python -m pytest content/video_engine/tests/test_production_editor.py -q`;
  `npm --prefix content/video_engine/editor run typecheck`;
  `npm --prefix content/video_engine/editor run test`
- Evidence: grouped normal/diagnostic memory and fab stills, source hashes, and
  render-boundary notes under `.claude/PRPs/evidence/P31/gate-a/`; normal mode
  has no identifier fallback.

### T3: Add plate profiles and semantic evidence binding compiler
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: new plate-profile and semantic-binding schemas/configs;
  `content/video_engine/src/services/semantic_evidence_binding.py`; focused
  compiler tests and current-bubble derived fixtures
- Acceptance: reviewed profiles encode protected/negative-space geometry;
  eligible PowerPoint crops are ranked deterministically from cue, beat, claim,
  world, and deck context; score components and rejections are inspectable;
  low-confidence or ambiguous matches fail closed.
- Validate: `python -m pytest content/video_engine/tests/test_semantic_evidence_binding.py -q`
- Evidence: versioned schemas/config, deterministic compiler fixtures, focused
  tests, and grouped ranking rationale in `.claude/PRPs/evidence/P31/gate-b/`.

### T4: Add semantic recommendations to snapshot and editor
- Status: complete
- Owner: parent
- Depends on: T2, T3
- Write set: additive snapshot/revision service fields and endpoints;
  `content/video_engine/production_console/src/**` excluding P30 kernel files
  not required by the feature; focused browser tests
- Acceptance: the editor shows approved candidate crop, proposed slot, score
  rationale, provenance, and rejection state; accept inserts one evidence item
  with binding provenance; replace/manual/unmatched paths work; no suggestion
  silently changes the draft.
- Validate: `python -m pytest content/video_engine/tests/test_production_editor.py content/video_engine/tests/test_production_editor_revisions.py content/video_engine/tests/test_production_console.py -q`;
  console typecheck/test/build/E2E
- Evidence: grouped recommendation review and live-editor screenshot under
  `.claude/PRPs/evidence/P31/gate-b/`; immutable accepted revision v3 under the
  P31 runtime root.

### T5: Adapt Word by Word to canonical caption timing
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/editor/src/remotionBits/**`; protected caption
  conversion/render paths; caption inspector/preset UI; focused tests
- Acceptance: Word by Word consumes canonical tokens and start/end frames,
  preserves transcript text exactly, attaches punctuation, keeps stable line
  layout, avoids duplicate Bit items, and remains deterministic in Player and
  render.
- Validate: editor and console typecheck/tests; exact-frame caption fixtures for
  short, medium, punctuation-heavy, and fast cues
- Evidence: Gate C A/B stills, short render, and exact-frame fixture summary
  under `.claude/PRPs/evidence/P31/gate-c/`.

### T6: Prove the complete visual grammar on current-bubble
- Status: pending
- Owner: parent
- Depends on: T4, T5, Gates A, B, and C
- Write set: new P31 runtime revision/render artifacts and gate evidence only
- Acceptance: one approved PowerPoint crop at a time is hand-revealed into the
  reviewed plate slot, connected by one annotation, retracted, and accompanied
  by approved Word by Word captions; world heroes remain unobstructed; accepted
  binding survives save/reload/recompile; Player/render inputs are identical.
- Validate: focused full suites, normal and diagnostic deterministic renders,
  artifact hashes, and watch review
- Evidence: `.claude/PRPs/evidence/P31/gate-d/` and
  `content/video_engine/runtime/jobs/current-bubble-mechanism-p31/`
- Review note: the immutable revision, normal/diagnostic renders, retraction
  stills, and hashes are complete; Gate A/B/C/D operator review remains.

### T7: Performance, security, documentation, and independent review
- Status: pending
- Owner: parent
- Depends on: T6
- Write set: P31 documentation, benchmark evidence, review record, and plan
  status/evidence fields
- Acceptance: ranking and recommendation loading do not degrade editor
  interaction; render has no network/model/runtime dependency; stale hashes,
  path escape, unapproved assets, protected text, ambiguous matches, and clutter
  violations fail closed; independent review has no unresolved blocker.
- Validate: complete verification suite, `python scripts/prp_validate.py`,
  `git diff --check`
- Evidence: `.claude/PRPs/evidence/P31/benchmark/` and
  `.claude/PRPs/reviews/P31-review.md`
- Review note: full automated verification, benchmark, and independent
  read-only review pass are recorded; final completion remains gated by T6
  operator review.

## Verification

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P31-SEMANTIC-EVIDENCE-AND-WORD-TIMED-CAPTIONS.plan.md
python -m pytest content/video_engine/tests/test_production_editor_contracts.py content/video_engine/tests/test_production_editor.py content/video_engine/tests/test_production_editor_revisions.py content/video_engine/tests/test_production_console.py content/video_engine/tests/test_semantic_evidence_binding.py -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run test
npm --prefix content/video_engine/production_console run typecheck
npm --prefix content/video_engine/production_console run test
npm --prefix content/video_engine/production_console run build
npm --prefix content/video_engine/production_console run test:e2e
git diff --check
```

## Evidence And Handoff

- Store baseline, schema, ranking, UI, caption, proof, benchmark, and human-gate
  evidence beneath `.claude/PRPs/evidence/P31/`.
- Store generated current-bubble revisions and renders beneath
  `content/video_engine/runtime/jobs/current-bubble-mechanism-p31/`.
- Store the independent read-only review at
  `.claude/PRPs/reviews/P31-review.md`.
- Completion requires grouped human review of ranking and caption alternatives,
  immutable artifact hashes, deterministic Player/render parity, and no
  unresolved label leakage or clutter-budget violation.
