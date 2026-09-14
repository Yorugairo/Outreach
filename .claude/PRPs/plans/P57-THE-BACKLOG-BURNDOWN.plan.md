---
id: P57-THE-BACKLOG-BURNDOWN
title: The backlog burndown - twenty-five named rows closed by evidence, not by claim; the bookkeeping rows marked done against their commits, the six un-landed research runs ingested, the CAPABILITIES rows owed written, the housekeeping done, the dropped research and the unread dial retired, the six measured defects each proved closed on its own frames or built, the four ruled mechanisms built (slide, the living caption, the race's two settings and its rank swap), and the seven-species promotion queue drained to modules
status: running
operation: maintenance
risk: standard
owner: parent
branch: main
created: 2026-09-14
updated: 2026-09-14
---

# The backlog burndown

## Summary

The operator's scope, verbatim (2026-09-14): *"burndown for: R26-93, R26-94, R26-74: already built in P55 and the
embed lane; the rows just need marking done. R26-110: ingest the six un-landed research runs (the ingestion gate stays
red on the one orphan until then). R26-90: the CAPABILITIES rows owed for the 12th and 13th. R26-92: docs-layer and
review-server housekeeping (stale servers on :8750-:8758, the layer regen rule). R26-63, R26-64: drop the research the
triage said to drop; retire the two dials nothing reads. R26-66 to R26-71: five measured defects with exact specs (a
transition emptying the stage mid-narration, the ring chip at an apex, the span painting over its label, the free-ASR
clock, the bracket figure across its line) and the E76 metric-to-comparator morph."* Widened mid-draft: *"also include
R26-75 the slide transition, R26-77 the living caption, R26-78/79 the race's path setting and rank-swap collision, the
promotion queue R26-95 to R26-101 (seven species to modules)."*

**The finding that changes the shape of this plan: four of the six "defect" rows are already CURED in the tree, and
the cure was never carried back to the row.** R26-66's compiler default (`stamp_transition_pages`,
`build_scene_timeline_f.py:1470-1513`) implements the CORRECTED chart-to-chart rule of 2026-09-13 including the exit
convention, and M31 already FAILs a non-dip boundary with a page on both sides (`gate_motion_density.py:1312-1347`).
R26-67's flag goes UNDER the ring past the last `FLAG_EDGE` of the drawn extent (`scene-evidence-engine.mjs:9042-9055`,
`RING.FLAG_EDGE: 0.15` at `:8899`). R26-68's shade sinks to the chart state's ground and its pad yields under a page
label (`SPAN.LABEL_CLEAR: 0.55` at `:666`, applied at `:800`). R26-69's forced alignment to the SCRIPT shipped in
`3642f2a` (`align_take.py --script`, `word_units`, `tests/test_align_take.py`) after the row was written. So the
burndown's NEW engine work is: the bracket's label (R26-71), the E76 morph (R26-70), and the four ruled mechanisms
(R26-75 slide / E87 s3, R26-77 the living caption / E90, R26-78 the race's two path settings / E91 s1, R26-79 the rank
swap / E91 s2) - plus the seven promotions, which change no pixel by construction.

That is the discipline this plan is built on: *judge the frame, not the diff* - a row is not closed because the code
looks right, it is closed on a measurement and a frame read at the instant the defect was found. Each "already cured"
slice runs the ORIGINAL measurement on the ORIGINAL build and either closes the row with the number and the frame, or -
if the frame refuses - takes the engine lock and fixes it.

All repo paths below are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`); `python` =
`C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`. This draft was written from the
sweet-villani worktree and copied into MAIN by script (the harness refuses the Write tool against the main checkout's
`.claude/`). No git state was changed while drafting - a steward is committing in parallel.

### Recall (run before drafting, 2026-09-14 - the receipt rule, `docs/runbooks/RECALL-RECEIPT.md`)

- Recall: docs_find "metric-to-comparator morph" = **1 hit**, the row itself: `BACKLOG.md:476` "R26-70 The
  metric-to-comparator morph (E76) - show the figure the market quotes (a P/E of 24.8x against 21.5x), then morph it
  into the number a v...". Nothing else in any layer describes the mechanism.
- Recall: docs_find "comparator" = 8 hits, and they are the BAR's comparator, not a number's:
  `[effects] The breakthrough burst overflow - overflow:burst`, `[effects] The stepped overflow - overflow:stack`,
  `[effects] recipe:ranked-bars-race-then-burst`, `[effects] recipe:stepped-overflow-off-the-page`,
  `[index] SPECIES-BY-SENTENCE.md:45 "The breaking sentence (BREAKS the honest scale)"`,
  `[manifest] docs/agent-memory/operator/first-pass-additive-capability-led.md`. **No effect turns one number into
  another** - E76's own Recall line said so and the layers agree.
- Recall: docs_find "chart to chart" = 3 hits: `[effects] recipe:chart-to-chart-with-no-cream` "Two pages in a row
  never show an empty page: the next chart a...", `[manifest]` + `[index]`
  `docs/agent-memory/operator/casebook/empty-cream-chart-to-chart/CASE.md:1` - the operator's own words, ledger
  `8086dab785f2`. The doctrine is E73 (`OPERATOR-RULINGS.md:2342`) and E88 (`:2647`).
- Recall: docs_find "slide transition" = **1 hit**, the row: `BACKLOG.md:481` "R26-75 The slide transition (E87 s3) -
  the incoming frame pushes the outgoing frame off along one axis, both moving together...". The ruling is E87 s3
  (`:2623-2646`): *"We should also have a push/slide option ... basically literally pushing out one frame with the
  next, so that you keep some of that congruency"*, named `slide` because `push` is the camera push-in.
- Recall: docs_find "rank swap" = **1 hit**, `BACKLOG.md:485` (R26-79, E91 s2, the measured "ALBETA" at 7.5 s);
  docs_find **0 hits** for "living caption" and "promotion queue" - E90 and P55 T11 are findable only by their rows.
- Recall: docs_find "clothoid" = 6+ hits, and the module already exists:
  `[effects] content/video_engine/scripts/kinetics/clothoid.mjs "The clothoid kinetics module - kinetics:clothoid"`,
  `[effects] species/vecmap.mjs "species:arc"`, `[effects] species/flow.mjs`. R26-78 is a PORT of
  `build-short-t17/engine-clothoid.mjs` (`clothoidFit`), not new math.
- Recall: docs_find **0 hits** for "bracket label", "forced alignment", "stage gaps", "empty stage", "flag_side",
  "icon catalogue", "docs layers", "research ledger". Most of this plan is findable only through the BACKLOG row and
  the code - which is exactly the failure mode R26-90 exists to fix.
- Recall: `sigmap_context.py query "stamp_transition_pages" --top 5` ranked the transition TESTS first
  (`tests/test_chart_transitions.py`, `scripts/proof_chart_transitions.py`) and did not name the definition; `rg`
  named it: `build_scene_timeline_f.py:1470`, its gate consumer `gate_motion_density.py:1347`, its golden-builder line
  `tests/golden/build_golden_sources.py:915`, `tests/test_transition_stamps.py` (6 call sites).
- Recall: `sigmap_context.py query "ring flag_side" --top 5` ranked the camera/player tests; `rg` named
  `scene-evidence-engine.mjs:8978 ringXExtent`, `:9042 ringFlagPlace`, `:9092` the call, `:8899 RING.FLAG_EDGE`.
  SigMap is the ranking layer, `rg` the naming layer - both receipts kept, per the retrieval benchmark's own warning.
- Recall: the ten docs layers are **all in sync right now** (measured 2026-09-14, `build_docs_layers.py --check`):
  `docs-index 4124 records / 339 files`, `research-ledger 19 runs (1 orphan, 9 referenced, 9 landed; 4 parked rows
  with a trigger)`, `effects-catalog 129 cards, 49 options, 39 recipes (15 proven)`, `docs-manifest 412 documents,
  **79178 bytes** of Markdown`, `gates-registry 160 records`, `animation-registry 810 records (535 implemented, 86
  tracked, 14 retired, 0 orphaned)`, `craft-map 81 devices`, `doc-overlap`, `topic-index`.
- Recall: `netstat -ano | grep LISTENING` (2026-09-14) = 58 listeners, **none on :87xx**. The review servers R26-92
  names are already down; what is left of that row is the `launch.json` entries (21 configurations) and the rule.

## What already exists (per row, on disk today)

| row | what is on disk | path:line | what is actually left |
|---|---|---|---|
| R26-93 `idle=live` | FIXED and committed | `3a6a645` (`kinetics/idle.mjs` +8, `tests/kinetics/idle.test.mjs` +20, `test_idle_e49.py` +13) | mark the row DONE with the hash |
| R26-94 `cutout` dock | FIXED and committed | `3a6a645` (`tests/test_dock_cutout_option.py` +57) | mark DONE; flip the P55 card `dock_option:cutout` `callable.today` |
| R26-74 embed surface | BUILT and committed | `3a6a645` (`tests/test_art_embed_media.py` +331) + the catalogue `364ecb9` | mark DONE with both hashes |
| R26-110 six runs | the ledger names them | `docs/RESEARCH-LEDGER.md:13,18-22`; the rule at `build_research_ledger.py:164-167` (`landed` = a BACKLOG row or plan slice cites the run PATH) | one citing row / doc cite / retirement each |
| R26-90 CAPABILITIES | rows NOT present | `CAPABILITIES.md` greps: `M32` 0, `M33` 0, `M34` 0, `G46` 0, `G47` 0, `G48` 0, `G13` 0, `independent` 0, `gated_pipe` 0, `melt` 1 (prose only) | write the eight rows owed |
| R26-92 housekeeping | servers already down; manifest at 79,178 B of 80,000 (`build_docs_manifest.py:97`) | `.claude/launch.json` (21 configurations, :8731-:8758) | prune the entries; the regen rule as a runbook line |
| R26-63 dropped research | the four items are `tracked` by the row itself | `ANIMATION-REGISTRY.md:943-952`; precedence `build_animation_registry.py:587` | make the verdict RETIRED, not tracked |
| R26-64 unread dials | `STOP.IMPACT_S` deleted (`stopaction.mjs:51-53`); `CADENCE.STROBE_PX_S: 300` declared, read nowhere | `kinetics/stopaction.mjs:26`, inlined at `scene-evidence-engine.mjs:1420` | retire the dial (or rule it an operator constant - R26-85) |
| R26-66 empty stage | CURED by the compiler default, corrected exit convention included | `build_scene_timeline_f.py:1470-1513`; M31 `gate_motion_density.py:1312-1347` | re-measure + the operator's frame read; close |
| R26-67 ring flag at an apex | CURED: past `FLAG_EDGE` the flag goes UNDER the ellipse | `scene-evidence-engine.mjs:8899, 8978, 9042-9055, 9092` | frame read 67.8-69.3 s; close |
| R26-68 span over its label | CURED: the shade sinks to the state's ground, the pad yields | `scene-evidence-engine.mjs:637, 666, 718, 800` | frame read 37-40 s; close |
| R26-69 free-ASR clock | forced alignment to the SCRIPT built | `align_take.py` "THE FIX (R26-69)" + `word_units`; `tests/test_align_take.py`; `3642f2a` | re-measure 155 words / 0.84 s; close or carry the residual |
| R26-71 bracket figure | NOT fixed | `scene-evidence-engine.mjs:5865-5873` (`geomOf`); M34 `gate_motion_density.py:2244-2265` | the engine fix |
| R26-70 E76 morph | NOT built; the machinery exists | `CHART_TO_KINDS` `build_scene_timeline_f.py:262`, `MORPH_METHODS:264`, `kinetics/morph_a.mjs`, `kinetics/arap.mjs`; M36 `gate_one_shot_floor.py:114` | grammar + paint |
| R26-75 slide | NOT built; the seam clock exists | `SCENE_EXITS` `build_scene_timeline_f.py:77`, `TIMED_EXITS:94`, `parse_exit:1381`; the engine's boundary block `scene-evidence-engine.mjs:10205-10301` (`dipIn`, `bzIn`, `wk`) | a new exit kind with a direction |
| R26-77 living caption | the base ships; the blend does not | the stagger module `kinetics/stagger.mjs` (inlined `scene-evidence-engine.mjs:157-194`, `RISE_PX 22`, `DUR_S 0.34`); STAGE-mode caption in `build_scene_timeline_f.py` | the pop-led blend + the idle, proven on a private build |
| R26-78 race path | arm B exists OUTSIDE the engine | `build-short-t17/engine-clothoid.mjs` (`clothoidFit`); the engine's race at `scene-evidence-engine.mjs:5144-5212` (`buildLedgerRace`, `LPX.RACE_PERIOD 1.2`) | port as an opt-in `path` key |
| R26-79 rank swap | NOT fixed | the same race block (`st.race = {..., ranks, swaps, ...}` at `:5192`); M34 the collision ledger | labels/values separate while crossing |
| R26-95..101 promotions | seven inline painters, ranked | `species.json` (trace/spotlight/callout), `page_species.json` (figure), `dock_payload.json` (record), `exit.json` (dip), `page_enter.json` (spiral); the recipe is P55 T7's, shipped twice (`species/verdict.mjs`, `species/checklist.mjs`) | module + region + node test + golden, `lives.form -> module` |

## Intent And Acceptance

Close twenty-five named BACKLOG rows with evidence on disk. Accepted when:

1. Every one of R26-63, 64, 66, 67, 68, 69, 70, 71, 74, 75, 77, 78, 79, 90, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101,
   110 carries a verdict in its row - **DONE**, **CLOSED**, **BUILT**, **RETIRED** or **WITHDRAWN** - with the commit
   hash, the measurement or the frame path that proves it. No row is closed by a claim.
2. `build_research_ledger.py` reads **0 orphan** and each of the six named runs reads `landed`, or carries a written
   retirement in a row that cites its path.
3. `CAPABILITIES.md` carries the eight rows owed for 2026-09-12/13, plus one row per NEW mechanism (slide, the caption
   blend, the race's two settings), each in `what it does / where it lives / state / proof` form.
4. The engine's behaviour is unchanged except where a slice says it changed: `sync_kinetics.py --check` in sync, the
   golden frames byte-identical (or a NEW golden with a proof frame read by the parent), and
   `gate_motion_density.py` on `japan-tariff-trick/build-short` and `tokyo-tea-break/build-short.v2` reading exactly
   what it reads today. **Every promotion is byte-identical by construction** - a promotion that moves a pixel is a
   failed promotion, not a new form.
5. The effects catalogue stays true: `effects_catalog_check.py` **0 failure(s)**, the seven promoted cards reading
   `lives.form: module` with their module path and symbol.
6. The whole `content/video_engine/tests` tree ends at the parent's 2026-09-14 baseline - **3 failed / 2,977 passed** -
   and no new red; `node --test content/video_engine/tests/kinetics/` green; `build_docs_layers.py` **10 layers in
   sync**; `prp_validate.py` PASS.

## Scope

- BACKLOG row verdicts, CAPABILITIES rows, the research ledger's citations, the animation registry's retirements.
- `.claude/launch.json` pruning and one runbook line for the layer-regen rule.
- Two engine fixes (R26-71's bracket label, R26-70's morph - the morph split into grammar and paint).
- Four ruled mechanisms: the slide (E87 s3), the caption blend (E90), the race's two path settings and its rank-swap
  separation (E91 s1/s2).
- The seven-species promotion queue (R26-95..101), each by the P55 T7 recipe.
- Re-measurement and frame reads for the four rows whose cure is already in the tree.

## Not Building

- No restage of any approved cut. Japan's 09-09 render and Tokyo's approved build are read, never rebuilt (E45);
  R26-77 is proven on a PRIVATE build and never rendered.
- No new gate rows beyond what a slice's acceptance names; the one-shot floor (M35-M42) is P56's and stays untouched.
- No research commissioned. R26-110 triages what is already on disk.
- No re-derivation of the strobe story beyond retiring an unread dial - R26-85's recommendation is a RULING the
  operator makes, not a burndown.
- No `DOCK_PAINTERS` registry (P55 T7 recorded the decision: a registry waits for a third dock painter).
- No push, no deploy, no credential change. The parent owns every protected action.
- R26-76 (the melt's look), R26-88 (the bridge pass 2), R26-102/105/106 stay out; they are named only where a row
  must cite them.

## Human Gates

**HG1 - the measured defects' frames, batched into one watch (the operator).** After T6-T12 each produce their frames,
the parent assembles one contact sheet / one served build per defect and the operator reads them in a single sitting:
R26-66 `<build>/self-watch/handoff/` (the suck's vortex and the melt's drip on stage - P53 gate 2's open register -
plus a chart-to-chart boundary with no cream); R26-67 the ring at the closing datum 67.8-69.3 s; R26-68 37-40 s (the
line and both figures over the wash); R26-71 0:27, 0:31, 0:52 of the bridge build; R26-70 the morph's first frames
(the quoted metric, the middle, the comparator standing).

**HG2 - the four new mechanisms, one watch (the operator).** T13-T16: the slide at its two golden instants and on a
real seam; the caption blend on Tokyo's PRIVATE build, judged by eye AND ear at the T10 instants (25.23 / 25.33 /
25.43 s) with the pop, the stagger and the blend side by side (E90's own test); the race's two settings A/B; the rank
swap at 7.5 s reading as two rows, not "ALBETA".

No operator gate for T1-T5 (bookkeeping, rows, housekeeping) or for T17-T23 (the promotions): a promotion's proof is
that every golden is byte-identical and the node test passes; the parent reads each diff and each new golden's frame.

## Mandatory Reads

- `docs/content-video-engine/BACKLOG.md` rows R26-63, 64, 66-71, 74, 75, 77, 78, 79, 85, 90, 92-101, 107, 110
  (verbatim; each carries its own measurement).
- `docs/portable/OPERATOR-RULINGS.md`: E76 (`:2442`), E73 (`:2342`), E88 (`:2647`), E87 (`:2623`, s3 the slide), E90
  (`:2678`, the caption), E91 (`:2699`, s1 the two settings, s2 the swap), E47, E49, E50, E60, E62, E96.
- `docs/runbooks/PRP_EXECUTION.md` - Dispatch mapping, Hand-off policy, Lane write sets.
- `docs/runbooks/RECALL-RECEIPT.md` - the receipt rule and the order of the layers.
- `.claude/PRPs/plans/P55-THE-EFFECTS-CATALOGUE.plan.md` **T7** (the promotion recipe, with its evidence: 157/202-line
  modules, `sync_kinetics: in sync (31 modules: 14 kinetics, 17 species)`, 47 golden sha256 identical) and **T11**
  (the queue and its measured ranks).
- `.claude/PRPs/plans/P56-...plan.md` - M36's definition (`:354`) and the Verification pattern this plan mirrors.
- `content/video_engine/scripts/species/verdict.mjs` + `species/checklist.mjs` (the two shipped precedents) and
  `content/video_engine/scripts/sync_kinetics.py` (the module rule, the region markers, `--check` / `--write`).
- `docs/RESEARCH-LEDGER.md` + `build_research_ledger.py:140-167`; `docs/content-video-engine/CAPABILITIES.md`.

## Execution Path

Bookkeeping first, then docs, then the engine - and inside each lane, one writer at a time.

1. **T1** (parent): the three already-built rows marked done.
2. **T2 -> T3 -> T4** (docs lane, serialised): the research ledger, the CAPABILITIES rows, the housekeeping. T4 owns
   the FINAL regeneration of all ten layers.
3. **T5**: the dropped research and the unread dial (takes the engine lock only if the dial is deleted).
4. **T6, T7, T8, T9**: the four rows whose cure is in the tree - measure, read the frames, close.
5. **T10 -> T11 -> T12**: the bracket's label, the morph's grammar, the morph's paint.
6. **T13 -> T14 -> T15 -> T16**: the slide, the caption blend, the race's path setting, the race's rank swap.
   T15 before T16 (the swap fix must hold on BOTH settings, so the second setting exists first).
7. **T17 -> T23**: the promotion queue, cheapest first (callout's golden already exists), the dip LAST because its
   module grouping depends on T13's answer.
8. The parent assembles HG1 and HG2, the operator watches twice, then the parent writes the verdicts and closes.

**The engine lock (contended files - never two writers at once):**
`docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/scripts/build_scene_timeline_f.py`,
`content/video_engine/scripts/kinetics/*.mjs`, `content/video_engine/scripts/species/*.mjs`,
`content/video_engine/tests/golden/**`, `content/video_engine/effects/cards/*.json`.
Order: T5 (if it deletes the dial) -> T7 (only if needed) -> T10 -> T11 -> T12 -> T13 -> T14 -> T15 -> T16 -> T17..T23.
**The row lock:** `docs/content-video-engine/BACKLOG.md` is edited one slice at a time, one row each (Lane write sets:
a shared file is edited by the lane that owns the fact, in the same commit as the change that made it true).

**Why the promotion queue is seven slices and not one.** The RECIPE is identical - every one of R26-95..101 ends with
the same sentence ("golden committed from the current inline code, lift every literal into a frozen dials object with
no value changed, pure math exported and node-tested, `sync_kinetics.py --check`, every golden byte-identical, the
card's `lives.form` -> module") - but the PREP is not: five need a NEW golden committed first from today's inline code
(`trace-hop`, `spotlight-hold`, `page-figure`, `record-typewriter`, `dip-boundary`, `spiral-return`), one (callout) is
already pinned by `chart-callout`, and two carry an open grouping question (R26-100's dip "with the scene-loop
transitions as one module beside R26-75's slide"; R26-101's spiral "with the page vortex RETRACT - one module, two
directions"). One slice with seven sub-items would also hold the engine lock for the whole queue and produce one diff
nobody can review as a unit. Seven small slices, serialised, each with its own golden and its own card edit.

## Patterns To Mirror

- **P55 T7** - the promotion recipe, proven twice: the module carries a WHEN / THE LAW header, every literal lifted
  into a frozen dials object with NO value changed, the pure math exported and node-tested, the engine calling the
  inlined region by name, `sync_kinetics --check` in sync, every golden's sha256 identical before and after, and the
  parent serving the real build to read the instants.
- **P56's slice shape**: Status / Owner / Depends on / Write set / Acceptance / Validate / Evidence, with the command
  written out in full and the evidence carrying numbers, not adjectives.
- **P53's defect slices**: measure with a tool that writes a JSON beside the build, then read the frames at the
  instants the defect was found; a gate row reads the measurement and stays INFO until measured.
- **R26-93's fix note** as the model closing verdict: the failing test named, the command, the counts, the frames,
  and the nit left behind with its reason.
- **E96 / M36** (`gate_one_shot_floor.py:114`): the E76 morph must be authored so M36 counts it - which ties R26-70 to
  E73's chart-to-chart doctrine rather than leaving it a free-floating trick.

## Task Slices

### T1: Mark R26-93, R26-94 and R26-74 done against their commits
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `docs/content-video-engine/BACKLOG.md` (three rows), `content/video_engine/effects/cards/dock_option.json` (`dock_option:cutout` `callable.today`)
- Acceptance: each row carries **DONE `<hash>`** with the evidence already in the row (R26-93: `3a6a645`, `kinetics/idle.mjs` restored + `test_idle_e49.py::test_every_compiler_idle_kind_is_a_kind_the_module_paints`, 44 golden frames byte-identical; R26-94: `3a6a645`, `tests/test_dock_cutout_option.py` 13 tests, 102 golden files byte-identical; R26-74: `3a6a645` for `embed_fit` + `364ecb9` for the P55 card, `tests/test_art_embed_media.py` +6, proof frame `scratchpad/proof/media@04.00.png`). The P55 card `dock_option:cutout` no longer says `callable.today: false` - R26-94 is what it was waiting for.
- Validate: `python content/video_engine/scripts/effects_catalog_check.py` and `python -m pytest content/video_engine/tests/test_effects_catalog_drift.py -q`
- Evidence: 2026-09-14 (parent). BACKLOG rows R26-93, R26-94, R26-74 carry **DONE (P57 T1)** with `3a6a645` (+ `364ecb9` for the card) and the counts already in the rows; the three rows' 'uncommitted' words replaced by the hash. The card `dock_option:cutout` ALREADY read `callable.today: true` with `proof.test: tests/test_dock_cutout_option.py` - no edit needed, verified by grep. Per the operator-accepted recommendation 1, the four cured defects close here: R26-66 (**RESTORED 2026-09-12 (E73 corrected)**), R26-67 (**CLOSED 2026-09-12**) and R26-68 (**CLOSED 2026-09-12**) already carried their P53 verdicts with the frames named in the rows, so nothing was written; R26-69 moved `open 2026-09-12` -> **CLOSED 2026-09-14 (P57 T1) - shipped in `3642f2a`**, with that commit's own measurement (kokoro 155/155 matched, 0 interpolated, onset error mean 0.086 s / p95 0.345 s; Chirp 155/155, all 20 phrase anchors resolve) and the residual named (the p95 onset error after a long pause). Validate: `effects_catalog_check.py` -> `0 failure(s), 3 example(s) skipped, 39 recipe(s) (15 proven, 7 decoration(s))`; `test_effects_catalog_drift.py` 53 passed. Baseline captured before T1: `gate_motion_density.py` Japan `RESULT: 3 FAIL / 0 WARN / 16 PASS / 1 JUDGE / 8 INFO` (M25, M27, M28), Tokyo v2 `RESULT: 1 FAIL / 2 WARN / 14 PASS / 1 JUDGE / 8 INFO` (M11) - `scratchpad/p57/baseline-gate-{japan,tokyo}.txt`.

### T2: R26-110 - the six un-landed research runs, ingested
- Status: complete
- Owner: junior_developer
- Depends on: T1
- Write set: `docs/content-video-engine/BACKLOG.md` (the R26-110 row + the citing rows it names), `docs/RESEARCH-LEDGER.md`, `docs/RESEARCH-LEDGER.jsonl`
- Acceptance: each of `motion_graphics_from_still_images` (09-03, the only orphan; `research_plan.md` + 4 findings - 2.5D parallax/depth, code-driven Remotion, generative I2V, pipeline architecture), `wealth-logic-cuts` (09-06, 1489 files - the reference cut measurements behind M13), `weight_mass` (09-07, 8 files - folded into P47's weight dials), `treasury_yield_spike_september_2026` (09-11), `video_engine_tooling_and_mcps` (09-11) and `vidiq_retention_zones` (09-12) gets ONE of: a BACKLOG row citing its `docs/research/runs/<name>` path (the only thing the ledger counts - `build_research_ledger.py:164-167`), a doc cite in the doctrine page that already carries the fact, or a written retirement **in a row that cites the path** (so the retirement is findable and the ledger's rule stays intact). Proposals for the parent to confirm: the orphan folds into R26-7 or R26-105/106 with "superseded by the scene-evidence engine's own motion" as the reason; `wealth-logic-cuts` cited from M13's docstring and doc 47; `weight_mass` from the animation registry's weight dials; `treasury_yield_spike` from R26-88's pass 2; `video_engine_tooling_and_mcps` from R26-102; `vidiq_retention_zones` from doc 46 s46.6. The ledger then reads **0 orphan**. No run's contents are edited (gitignored).
- Validate: `python content/video_engine/scripts/build_research_ledger.py --write` then `python content/video_engine/scripts/build_research_ledger.py --check`
- Evidence: 2026-09-14. Lane (junior_developer) triaged read-only into `docs/research/runs/p57-burndown/T2-research-triage.md` (gitignored, like every run); the parent applied the rows under the row lock. Disk overruled three proposals: the orphan is retired by the DATED ruling E32 (+E49), not folded into R26-105/106 (unrelated) -> new row R26-112 RETIRED; `weight_mass` has no row (the registry is a doc cite) -> R26-113 DONE, landed in `stopaction.mjs:32-33`; `treasury_yield_spike` is R26-109's payload (`REWRITE-ORDER-B.md:95`, DGS10 2026-09-09 4.83), not R26-88's; `vidiq_retention_zones` is not retired - doc 46 s46.6 is TR-2, and its Apex Chart Read reads against E24 -> R26-114 OPEN (a ruling). Citing sentences appended to R26-9 TOP, R26-102, R26-109; R26-110 also cites `docs/research/runs/p57-burndown` because the ledger counts that directory as a 20th run. `build_research_ledger.py --write` -> `20 runs (0 orphan, 4 referenced, 16 landed; 4 parked rows with a trigger)`; `--check` in sync. Deviation: the lane did not edit BACKLOG (row lock held by the parent).

### T3: R26-90 - the CAPABILITIES rows owed for 2026-09-12/13
- Status: complete
- Owner: junior_developer
- Depends on: T2
- Write set: `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md` (the R26-90 row only)
- Acceptance: eight rows added or amended in the file's four-column form, each naming the commit or golden that proves it: (1) the ART-embed media surface (`fit` cover/contain, stills and clips fill, the camera push carries embedded content - R26-74, E86, E95); (2) the melt's three endings (R26-76, E88); (3) M32 / M33 / M34 the collision ledger; (4) G13 by function and G46-G48; (5) the E79 scale WARN (`ledger_page.py` `independent`); (6) `check_gated_pipes.py` + the `gated_pipe_guard.py` PreToolUse hook; (7) the race A/B proof players fixed (silent clock + real plates); (8) the icons capability amended for E93/E94 (an agenda row's icon stamped once its sentence is read; the operator's set approved) over the sourced Lucide files at `assets/icons/` + `SOURCES.md`. The verdict-stack row's stale template path is NOT touched (P55 T5 owns it) - say so in the row.
- Validate: `python content/video_engine/scripts/build_docs_manifest.py --check` (expected STALE until T4 - record the byte count) and `python -m pytest content/video_engine/tests/test_build_docs_index.py -q`
- Evidence: 2026-09-14. Lane (junior_developer, resumed once at its turn limit; wrote by script because the harness refuses Edit on main from the worktree): `CAPABILITIES.md` +12,512 B, 8 insertions / 2 deletions, parent-read diff - SIX rows added (the embed surface E86/E95 `3a6a645`; the race A/B proof players fixed, `2684c2c` `player-check.json`; M32/M33/M34 `5aa0f8f`; G13 by function + G46/G47/G47b/G48 `5aa0f8f`; the E79 scale WARN `5aa0f8f`; `check_gated_pipes.py` + the PreToolUse hook `5aa0f8f`), TWO amended (the melt to E88's three endings with the six melt goldens; the icon CHIP row for E93/E94 - 44 cutouts approved, 220 semantic tags MEASURED, not the 214 an older memory records). The verdict-stack row's stale template path untouched (P55 T5). `build_docs_manifest.py --check` -> `in sync (412 documents, 79178 bytes of Markdown)` (rows, not headings - the manifest did not move); `test_build_docs_index.py` 15 passed. The R26-90 row closed by the parent with the lane's sentence and **DONE**.

### T4: R26-92 - the housekeeping, and the layer-regen rule as a runbook line
- Status: complete
- Owner: parent
- Depends on: T3
- Write set: `.claude/launch.json`, `docs/runbooks/RECALL-RECEIPT.md`, `docs/content-video-engine/BACKLOG.md` (the R26-92 row), the ten generated layers (`docs/DOCS-INDEX.*`, `DOCS-MANIFEST.*`, `DOCS-TOPICS.*`, `DOCS-CITATIONS.*`, `GATES-REGISTRY.*`, `ANIMATION-REGISTRY.*`, `CRAFT-MAP.*`, `EFFECTS-CATALOG.*`, `RESEARCH-LEDGER.*`, `DOC-OVERLAP.*`)
- Acceptance: (a) **measured 2026-09-14: nothing is listening on :87xx** (58 listeners, none in range), so the row's "stop them" is already true - what lands is pruning `.claude/launch.json` from 21 configurations to the live set (the dead entries `bridge-review-v1` :8750, `bridge-build-review` :8751, `gates-review` :8752, `p55-buildf-proof` :8753 pointing at a session scratchpad, `gate5-race-arm-a/b` :8754/:8755, `gate3-species-proof` :8756, `gate4-stagger-player` :8757) with the five-per-worktree limit written down; (b) the manifest headroom RECORDED in the row - **79,178 B against `MD_MAX_BYTES` 80,000** (`build_docs_manifest.py:97`), 822 B - and the mechanism named honestly: `MD_LADDER` (`:100-103`) drops a rung rather than failing, so the cost is detail per line, never a break; (c) the layer-regen rule as ONE line in `docs/runbooks/RECALL-RECEIPT.md`: regenerate all ten layers with `build_docs_layers.py --write` after an engine or doctrine lane settles, never while `scene-evidence-engine.mjs` is mid-edit (the animation registry reads the engine), and never inside a slice that does not own the layers; (d) all ten layers regenerated and in sync.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --write` then `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: 2026-09-14 (parent). DEVIATION: main's `.claude/launch.json` had 13 configurations, not 21 - the 21 with the :8750-:8758 proof entries is the sweet-villani WORKTREE's uncommitted copy, left alone. Main pruned 13 -> 5 (the episode, both approved shorts, the brand cards, Tokyo v2) with the five-per-worktree rule written into the file as `_rule`; `netstat` measured nothing on :87xx; the runbook paragraph added to `RECALL-RECEIPT.md` s3; the manifest at 79,178 / 80,000 B recorded in the row; `build_docs_layers.py --write` + `--check` -> `every layer in sync (10 layers)` after T5's rows (the animation registry reads BACKLOG). A second, FINAL regeneration runs after the engine lane (T11-T23 regenerate the effects catalogue and SPECIES-BY-SENTENCE themselves).

### T5: R26-63 and R26-64 - the dropped research retired, the unread dial retired
- Status: complete
- Owner: junior_developer
- Depends on: T4
- Write set: `docs/content-video-engine/BACKLOG.md` (R26-63, R26-64), `content/video_engine/scripts/kinetics/stopaction.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `stopaction` region only, via `sync_kinetics.py --write`), `docs/ANIMATION-REGISTRY.md` + `.jsonl`
- Acceptance: **R26-63** - the four items the 2026-09-05 triage said RETIRE (`2. Dynamic Nib Pooling [RECLASSIFIED: Engineering Heuristic Proposal]`, `2.1 The 5 Overlapping Synergies to Capitalize On`, `B5: Rhythm as a Distribution [Tier 1 Science - CLOSED]`, `C6: What Rive / Lottie / Flash Got Right [Tier 1 Architecture - CLOSED]`) read `retired` in the regenerated registry, not `tracked` - today they are tracked by the row itself (`ANIMATION-REGISTRY.md:943-952`, each citing `BACKLOG.md:468`) and the precedence is `implemented > retired > tracked > orphaned` with the verdict read off the row's words (`build_animation_registry.py:587, 693, 718-726`). **R26-64** - `CADENCE.STROBE_PX_S` (300 px/s, `kinetics/stopaction.mjs:26`, `[DERIVED: the brief ... Watson et al. 1986, not on file]`) deleted with a comment in `IMPACT_S`'s form (`:51-53`: what it was, why it went, what carries the behaviour now - here: nothing reads it, no painter ever applied the ceiling), the engine region re-synced, the row closed **RETIRED** naming both dials and `dd859b6` for the first. If the operator instead rules R26-85's recommendation, this slice becomes docs-only - see Open Decisions.
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py -q` and `node --test content/video_engine/tests/kinetics/` and `python content/video_engine/scripts/build_animation_registry.py --check`
- Evidence: 2026-09-14 (parent, per recommendation 2 - a comment edit, not a delete, so no lane). R26-63: the regenerated registry ALREADY read all four items `retired` (checked by name in `ANIMATION-REGISTRY.jsonl`: Dynamic Nib Pooling, the 5 Synergies, B5 Rhythm, C6 Rive/Lottie - the row's **WITHDRAWN** verdict is what `retirement()` reads), so the row gained a VERIFIED sentence and no registry edit. R26-64: `STOP.IMPACT_S` stays deleted (`dd859b6`); `ON1_PX_S` 250 and `STROBE_PX_S` 300 kept as OPERATOR-SET CONSTANTS, their Watson-derivation comments replaced with the R26-85 verification's finding and the space STROBE_PX_S waits for (`stopaction.mjs:25-26`); `sync_kinetics.py --write` -> `31 region(s) written`, `--check` in sync (31 modules); `stopaction.test.mjs` 11/11; `test_kinetics_sync.py test_golden_frames.py` 71 passed; registry: STROBE_PX_S `tracked` (a row names it), ON1_PX_S `implemented`. Row closed **RETIRED / RULED**.

### T6: R26-66 - the empty stage, re-measured and closed
- Status: complete (collapsed into T1 - recommendation 1, accepted by the operator's `/goal /prp-implement P57`)
- Owner: implementation_luna
- Depends on: T1
- Write set: `docs/content-video-engine/BACKLOG.md` (R26-66 only), `content/video_engine/tests/test_transition_stamps.py` (one test if a case is missing)
- Acceptance: `measure_stage_gaps.py` is run on `normal-for-which-bridge/build-short-axes` (the build the defect was found on, 69.8 s) and on `japan-tariff-trick/build-short`, and the numbers go into the row - the original read was **6.2 s empty, 8.9% of the runtime**, the suck at 13.79 s and the melt at 40.51 s each 3.1 s and each spoken over. The corrected rule is verified in the CODE, not assumed: `stamp_transition_pages` (`build_scene_timeline_f.py:1470-1513`) stamps `enter=axes` on any page following a page whatever the transition (`:1504-1506`), `exit=cut` on a page a suck or melt takes (`:1501-1503`), the hook on axes (`:1507-1512`); M31 (`gate_motion_density.py:1334-1347`) FAILs any non-dip boundary with a page on BOTH sides. A test covers the CUT-between-two-charts case if none does (the 2026-09-13 correction) - it must fail against the pre-correction guard and pass as written. Row closed **CLOSED** with `0.0 s / 0.0%` or the residual named. The handoff frames go to HG1.
- Validate: `python content/video_engine/scripts/measure_stage_gaps.py content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-short-axes` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-short-axes` and `python -m pytest content/video_engine/tests/test_transition_stamps.py -q`
- Evidence: see T1: the row already carried its P53 verdict and frames (T6/T7/T8), or was closed on `3642f2a`'s measurement (T9). No lane dispatched, no measurement re-run - the measurement in the row IS the evidence, and the frames it names are HG1's batch.

### T7: R26-67 - the ring's flag at an apex datum, read on the frames
- Status: complete (collapsed into T1 - recommendation 1, accepted by the operator's `/goal /prp-implement P57`)
- Owner: implementation_luna
- Depends on: T6
- Write set: `docs/content-video-engine/BACKLOG.md` (R26-67 only); the engine (`scene-evidence-engine.mjs`, `species/ring.mjs`) and `content/video_engine/tests/golden/**` ONLY if the frame refuses - engine lock in that case
- Acceptance: the frames at **67.8-69.3 s** of `normal-for-which-bridge/build-short-axes` are rendered and read - the chip stands UNDER the ring, clear of the terminal tag ("x3.9 Federal debt") and inside the page's card - against the rule at `scene-evidence-engine.mjs:9042-9055` (`f >= 1 - RING.FLAG_EDGE` -> `{x: e.cx, y: e.cy + e.ry + gap, side: "under"}`, `FLAG_EDGE 0.15` at `:8899`, the extent from `ringXExtent` at `:8978`). If the frames agree: **CLOSED** with the frame paths, no code moved (`git diff --stat` on the engine empty). If they refuse: the fix lands under the engine lock with `ring-dashed-chip` and `species-proof@proof-ring` byte-identical or re-goldened with a proof frame for HG1. The ellipse's own half-reach is NOT changed here - Open Decisions.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_gate_ring_mechanism.py -q` and `python content/video_engine/scripts/sync_kinetics.py --check` and `git diff --stat -- docs/content-video-engine/samples/scene-evidence-engine.mjs content/video_engine/scripts/species content/video_engine/tests/golden`
- Evidence: see T1: the row already carried its P53 verdict and frames (T6/T7/T8), or was closed on `3642f2a`'s measurement (T9). No lane dispatched, no measurement re-run - the measurement in the row IS the evidence, and the frames it names are HG1's batch.

### T8: R26-68 - the span's shade over the series label, read on the frames
- Status: complete (collapsed into T1 - recommendation 1, accepted by the operator's `/goal /prp-implement P57`)
- Owner: implementation_luna
- Depends on: T7
- Write set: `docs/content-video-engine/BACKLOG.md` (R26-68 only); the engine ONLY if the frame refuses (engine lock)
- Acceptance: the frames at **37-40 s** of the same build are read - the line and both figures read OVER the wash and the page's series tag stands on the ground outside the shade - and both halves are verified in the code: the shade sinks to the ACTIVE chart state's own svg every frame (idempotent, so a cold seek lands where a play does) and the band's PAD yields under a page label (`SPAN.LABEL_CLEAR: 0.55` of the span's own label size, `:666`, through `spanPageLabels(st)` at `:718` and `:800`), while the EDGES and the span's own name keep the RAW top so M28 reads the geometry it already passed. **CLOSED** with the frame paths; goldens byte-identical.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-short-axes`
- Evidence: see T1: the row already carried its P53 verdict and frames (T6/T7/T8), or was closed on `3642f2a`'s measurement (T9). No lane dispatched, no measurement re-run - the measurement in the row IS the evidence, and the frames it names are HG1's batch.

### T9: R26-69 - the free-ASR clock, re-measured against the script aligner
- Status: complete (collapsed into T1 - recommendation 1, accepted by the operator's `/goal /prp-implement P57`)
- Owner: implementation_luna
- Depends on: T8
- Write set: `content/video_engine/scripts/align_take.py`, `content/video_engine/tests/test_align_take.py`, `docs/content-video-engine/BACKLOG.md` (R26-69 only)
- Acceptance: `align_take.py --script` is run on the SAME audio the 2026-09-12 limit was measured on and the two numbers are re-measured - free-form `small.en` returned **141 words where kokoro's tokenizer had 155**, the last word's end lagging **0.84 s**. With `--script` the output's words ARE the script's spoken tokens in order, so the count must equal the script's exactly and `aligned {matched, interpolated, script_tokens}` must show how many times came from the recogniser rather than interpolation. The verdict is measured, not assumed: **CLOSED** (count exact, last-word lag inside the shot table's tolerance, `authoring/words.at` resolving every phrase of the take) or **the residual named in the row** (how many interpolated, the worst lag, what a shot row may not anchor on yet). A test fails before and passes after on whatever the measurement forces (a decimal, a year, a hyphenated token, the interpolation floor) - `word_units`' normalisation is the surface. Whisper stays LOCAL; no cloud STT call.
- Validate: `python -m pytest content/video_engine/tests/test_align_take.py -q` and `python content/video_engine/scripts/align_take.py <the take's audio> --script <the script txt> --out <scratch>/words.json`
- Evidence: see T1: the row already carried its P53 verdict and frames (T6/T7/T8), or was closed on `3642f2a`'s measurement (T9). No lane dispatched, no measurement re-run - the measurement in the row IS the evidence, and the frames it names are HG1's batch.

### T10: R26-71 - the bracket's figure printed across the line it measures
- Status: complete
- Owner: implementation_luna
- Depends on: T9 (engine lock)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the bracket's `geomOf`), `content/video_engine/tests/golden/**` (only if a golden moves, with a proof frame), `content/video_engine/tests/test_targeted_species.py`, `docs/content-video-engine/BACKLOG.md` (R26-71 only)
- Acceptance: M34 (`gate_motion_density.py:2244-2265`) stops FAILing on the three measured instances of `normal-for-which-bridge/build-review` - `bracket:31% of GDP` at **0:27**, `bracket:123%` at **0:31**, `bracket:31%` at **0:52** - with the rule kept STRICT (no own-line exemption: text over a line is unreadable wherever it belongs). The fix is in the label's placement, `scene-evidence-engine.mjs:5865-5873`: today `geomOf` writes the label beside the span at `ym` when `fits` (`lx = x + 12 + half`, `ly = ym + fs * 0.35`) and stacks above the whole series (`yClear`) only when the room to the right is too narrow. It must also stack - or step off the line - when the BESIDE box would cross drawn ink, measured against the same live points the bracket already reads (`ptsNow`), so the geometry stays a pure function of the anchors and the series and a re-read frame on a changed chart state lands identically (R26-28). A test fails before and passes after. Goldens byte-identical, or a new golden with a proof frame for HG1. Must not depend on R26-88's restage.
- Validate: `python content/video_engine/scripts/probe.py content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-review --gate` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-review` and `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_targeted_species.py -q` and `python content/video_engine/scripts/sync_kinetics.py --check`
- Evidence: 2026-09-14. DEVIATION found by the lane and accepted by the parent: the three M34 instances are FIGURE species (`bridge-short.timeline.json` carries zero brackets; the probe's `bklab` class holds both), so the surface is `paintFigure`, not `geomOf`; and M34 already read PASS because the own-line exemption is the operator's 2026-09-13 ruling (`5aa0f8f`) - the plan's 'kept STRICT (no own-line exemption)' was the parent's wording and is withdrawn; acceptance re-based on the measured PAIR COUNT: figure-on-own-line overlaps 20 -> 0 on `build-review`, M34 PASS before and after (480 -> 280 pairs checked). The fix: `segMeetsBox` / `figBox` / `figClearY` + six `PS.FIGURE_*` dials, engine +64/-6 (not a synced module; `sync_kinetics --check` in sync, 31 modules). `tests/test_figure_placement.py` 5 tests (built player via playwright; red before, green after); `test_golden_frames.py test_targeted_species.py test_figure_placement.py` 122 passed; 47 goldens byte-identical (112 files; `ledger-keyed`/`ledger-extend` flaked once and re-rendered at maxdelta 0). Frames read by the parent (judge the frame): before-t31p78 shows `31% of GDP` on the stroke, after-t31p78 and after-t53p92 show the figures clear below the trough - HG1 material at `build-review/self-watch/p57-t10/`. The review build's engine copy and `layout-probe.json` are modified in the working tree (patched to read the frames) and are NOT part of the commit.

### T11: R26-70a - the metric-to-comparator morph, the compiler grammar
- Status: complete
- Owner: implementation_luna
- Depends on: T10 (engine lock)
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/test_targeted_species.py` (or a new `test_metric_comparator.py`), `docs/content-video-engine/SPECIES-BY-SENTENCE.md`
- Acceptance: a grammar for E76's mechanism - *show the figure the market quotes (a P/E of 24.8x against 21.5x), then morph it into the number a viewer feels* - that a shot row can author and that **M36 counts as a chart-to-chart transform** (`gate_one_shot_floor.py:114`; P56's row definition at plan line 354: `species[].kind == "chart_to"`). The proposal for the parent to confirm: a sixth `chart_to` verb (`CHART_TO_KINDS` today `("recast", "rescale", "extend", "park", "morph")`, `build_scene_timeline_f.py:262`) carrying `from` (the quoted metric, label, units) and `to` (the comparator, label, units, and the arithmetic that derives it), with the derivation AUTHORED and validated, never invented by the engine (E77: `[DERIVED: from <sources>, <how>]`; figures are never fabricated). The validator refuses: a `to` whose arithmetic does not reproduce from the `from` and the authored inputs; a morph with no comparator label; a `method` key (that belongs to the line morph, `MORPH_METHODS:264`); a page with no `figure` species to morph (E50, `:613`). `CHART_TO_WHEN` (`:327`) gains the verb's "when the sentence needs..." line. Doctrine cites: E76 + E73 + E88. Compiler-only: a timeline that authors it compiles and the gate counts it, and the engine paints nothing until T12 - accepted with that stated, not hidden.
- Validate: `python -m pytest content/video_engine/tests/test_targeted_species.py content/video_engine/tests/test_chart_transitions.py -q` and `python content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`
- Evidence: 2026-09-14. Lane (implementation_luna; wrote by script). The sixth `chart_to` verb is `to: "compare"` (`CHART_TO_KINDS` +1, `CHART_TO_WHEN` line, s4 of SPECIES-BY-SENTENCE regenerated +1): keys `metric{value,text,label}`, `comparator{value,text,label}`, `inputs{name: number}`, `derive` (plain arithmetic over the input names, parsed and WALKED by `ast` against a node whitelist - never eval; a call, attribute, subscript, compare, pow, an unknown name, a divide by zero each refused by name), `source` (must start `[DERIVED:` / `[SOURCE:`), `hold: metric|gone`; `COMPARE_TOL` 0.005 of the larger magnitude - a derive that does not reproduce the comparator is refused ('a near-miss is a refusal, never a tween'); `method` and `state` refused; the E50 page check (`figure` species whose text equals `metric.text`) lives in `validate_species` where the row's species list is known. `tests/test_metric_comparator.py` NEW, 40 tests. Parent fixed the one pin outside the lane's write set (`test_chart_transitions.py:57`, five verbs -> six). Whole T11 set: `test_metric_comparator test_chart_transitions test_targeted_species test_effects_catalog_drift test_lint_species_choice` -> 271 passed. `gate_one_shot_floor.py` Japan: M36 unchanged `[INFO] M36 0 chart-to-chart transforms (none) - predates E96`. Card `chart_to:compare` planned, `callable.today: false` ('the paint lands in P57 T12'); `build_effects_catalog --check` in sync (130 cards); `effects_catalog_check` 0 failures, 4 examples skipped. Compiler-only, as the slice says: the engine paints nothing for it until T12.

### T12: R26-70b - the metric-to-comparator morph, the engine paint
- Status: complete
- Owner: implementation_luna
- Depends on: T11 (engine lock)
- Write set: `content/video_engine/scripts/species/<the new module>.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the synced region only), `content/video_engine/tests/kinetics/<module>.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + one new golden, `content/video_engine/effects/cards/chart_to.json`, `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md` (R26-70)
- Acceptance: the morph paints as a pure function of t and seeks exactly (a cold seek lands where a play does): the quoted metric stands, the comparator arrives out of it - the glyphs of one number becoming the glyphs of the other - and the comparator holds with the metric legible beside it or gone, as the grammar's option says. Existing machinery is reused, not re-derived: `kinetics/morph_a.mjs` (doc 43 s43.5 Method A - ring-normalise, resample by arc length, rotational alignment, vertex lerp reconstructed as cubic Beziers) and `kinetics/arap.mjs` (Method B, `ARAP.AXIS_MAX_DEG` the refusal rule); E60's counter already steps one number up a rescale. The module rule holds: no new species in the engine's body; the module registers its painter as its last statement. A node test asserts the pure-function property (two identical frames at one t; the ends exact) and a golden proves the middle. `sync_kinetics.py --check` in sync; every existing golden byte-identical; the NEW golden carries a proof frame the parent reads and the operator sees at HG1. The motion gate on Japan and Tokyo reads exactly what it read before. The catalogue gains the card; CAPABILITIES gains the row in the same slice.
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check` and `node --test content/video_engine/tests/kinetics/` and `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short.v2`
- Evidence: 2026-09-14. Lane (implementation_luna). DEVIATION accepted by the parent: the form is E60's COUNTER, not the glyph-outline morph - a page figure is SVG `<text>` (one tspan per character) and `morph_a.mjs` morphs outlines; glyph outlines would need a vendored font-to-path library (a second type engine), refused; the module header states it and quotes E76. `species/compare.mjs` 223 lines, `/* SPACE: page */`, `PAGE_PAINTERS.compare` registered last, dials `COMPARE` (11 named); dispatch in `paintPerform` after the figures (engine :6411) + two `continue` guards so a compare never un-draws its page. Node `compare.test.mjs` 18 tests; kinetics suite 366/366 (the bare-dir `node --test` form errors on node 24 - pre-existing, run the glob). Golden `compare-morph` + `@proof-quoted` (24.8x alone) / `@proof-mid` (12.84 s: `20.2x` in transition, not a cut) / base (`15 % dearer`, `24.8x` ghosted, the label beneath, clear of ink) - read by the parent; a CSS-vs-attribute opacity bug was found by reading the frame and fixed (`compareInk` writes the inline style). 47 existing goldens identical, 3 new. Further deviations, needed to register a golden: `render_baseline.py` (2 PROOF_FRAMES lines), `test_golden_frames.py` (SURFACES += compare-morph), `effects_catalog_check.py` (+7: a compare example is paired with its E50 figure - T11's card example had left the check red). `sync_kinetics: in sync (32 module(s): 14 kinetics, 18 species)`; pytest golden_frames + kinetics_sync + metric_comparator 114 passed; Japan `3 FAIL / 0 WARN / 16 PASS / 1 JUDGE / 8 INFO` and Tokyo `1 FAIL / 2 WARN / 14 PASS / 1 JUDGE / 8 INFO` unchanged; `effects_catalog_check: 0 failure(s), 3 example(s) skipped`. Card `chart_to:compare` wired, `lives {module, species/compare.mjs, paintCompare}`, `proof.golden compare-morph`; CAPABILITIES row at line 28. Row R26-70 closed **BUILT**.

### T13: R26-75 - the slide transition (E87 s3)
- Status: pending
- Owner: implementation_luna
- Depends on: T12 (engine lock)
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`SCENE_EXITS`, `TIMED_EXITS`, `parse_exit`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the boundary block), `content/video_engine/tests/golden/build_golden_sources.py` + two golden frames, `content/video_engine/tests/test_transition_stamps.py` / `test_chart_transitions.py`, `content/video_engine/effects/cards/exit.json`, `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md` (R26-75)
- Acceptance: a new exit kind **`slide`** with a DIRECTION (`slide:left|right|up|down`, plus its own seconds like the dip and the blur-zoom - `TIMED_EXITS`, `build_scene_timeline_f.py:94`, parsed by `parse_exit:1381`), in which the incoming frame pushes the outgoing frame off along one axis, **both moving together**, so the two worlds stay spatially continuous (E87 s3, the operator: *"literally pushing out one frame with the next, so that you keep some of that congruency"*). It lives in the engine's own boundary clock beside `dipIn` / `bzIn` (`scene-evidence-engine.mjs:10205-10301`), on min-jerk, and lands in the caption gap the way a cut does (M13's rule - it is a hand-off, not a world-taking transition, so `stamp_transition_pages`' chart-to-chart stamp applies to it exactly as to a cut). `push` stays the camera push-in - the name is not reused. Two goldens at two instants (mid-slide with both worlds on stage; the landing frame). The reference is `@remotion/transitions`' `slide` presentation (`editor/src/TransitionEvidence60sProof.tsx` already imports the package) - read for its geometry, never vendored. Every existing golden byte-identical; the motion gate on Japan and Tokyo unchanged; a test fails before and passes after (a row authoring `slide:left` compiles and the engine paints both frames moving).
- Validate: `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_transition_stamps.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T14: R26-77 - the Steel and Paper caption, alive (E90)
- Status: pending
- Owner: implementation_luna
- Depends on: T13 (engine lock)
- Write set: `content/video_engine/scripts/kinetics/stagger.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `stagger` region + the caption paint), `content/video_engine/scripts/build_scene_timeline_f.py` (the caption's option only), `content/video_engine/tests/kinetics/stagger.test.mjs`, `content/video_engine/effects/cards/caption.json`, `docs/content-video-engine/BACKLOG.md` (R26-77)
- Acceptance: a BLEND, not a switch (E90 s2). The base stays the caption shipped on Steel and Paper - STAGE mode, centred in the page's quiet zone, 64 px / 800, each word popping at its own spoken time (scale 1.16 -> 1.0, alternating +-2.5 degrees tilt), moving to the free band under a dock at the same size (E62). On top: the pop **leads and is a little stronger**, P52 T10's stagger envelope rides UNDER it (`stagger.mjs` `DUR_S` 0.34, `RISE_PX` 22, the 0.05 s anticipation), and E49's idle carries a held caption page. The caption-energy lessons bind: energy from continuous voice-timed motion, **no per-word cursor or flash that pins the eye**; where "more pop" and "nothing pins the eye" pull against each other the operator's eye decides (E90 s3), so the slice ships the BLEND AS A DIAL with the three settings renderable, not one baked answer. PROOF: Tokyo's PRIVATE build (never a render, R26-45) - the pop, the stagger and the blend side by side at the T10 instants **25.23 / 25.43 / 25.33 s** as frames, plus a served player for the ear. Every golden byte-identical unless a golden's caption is in frame, in which case the moved goldens are named and carry proof frames. Both approved shorts must be rebuildable clock-identical (the blend is opt-in until the operator rules at HG2).
- Validate: `node --test content/video_engine/tests/kinetics/stagger.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short.v2`
- Evidence: pending

### T15: R26-78 - the race's two path settings (E91 s1)
- Status: pending
- Owner: implementation_luna
- Depends on: T14 (engine lock)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the race block), `content/video_engine/scripts/build_scene_timeline_f.py` (the `path` key on a race page), `content/video_engine/tests/golden/build_golden_sources.py` + one golden pair, `content/video_engine/effects/cards/page_builder.json`, `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md` (R26-78)
- Acceptance: a race page accepts `path: "eased"` (the DEFAULT - the engine as it is, arm A) or `path: "clothoid"` (arm B, ported from `tokyo-tea-break/build-short-t17/engine-clothoid.mjs`'s `clothoidFit` through the period knots), **the period clock identical in both** (`LPX.RACE_PERIOD 1.2`, `buildLedgerRace` at `scene-evidence-engine.mjs:5144-5212`). The port reuses `kinetics/clothoid.mjs` (already a module, already node-tested - `docs_find "clothoid"` names it first) rather than re-deriving the fit. E91 s1: both ship as named settings, neither is discarded. Goldens byte-identical for the default; a NEW golden pair (one instant, both settings) proves the second. A test fails before and passes after (a race row with `path: "clothoid"` compiles and moves a mark along a different path at the same period times).
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and `node --test content/video_engine/tests/kinetics/` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T16: R26-79 - a race's rows collide at a rank swap (E91 s2)
- Status: pending
- Owner: implementation_luna
- Depends on: T15 (engine lock)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the race block's label/value placement), `content/video_engine/tests/golden/build_golden_sources.py` (one golden at a swap), `content/video_engine/tests/test_targeted_species.py`, `docs/content-video-engine/BACKLOG.md` (R26-79)
- Acceptance: at a rank swap two labels or two values never print on top of each other, **on either setting** (that is why this follows T15). The measured failure: arm B at **7.5 s** printed BETA and ALPHA in one row ("ALBETA") with "136" over "138"; the older stills showed DELTA over CHI at 8.7 s. The cure is the passing rows' own geometry - a lane offset while crossing, or the passing row's label yielding for the crossing's duration - computed from `st.race`'s own `ranks` / `swaps` (`:5192`) so it stays a pure function of u and a cold seek into a swap lands where a play does. M34's collision ledger on a probed race page must read clean at the swap instants. A test fails before and passes after on a fixture whose two rows cross.
- Validate: `python content/video_engine/scripts/probe.py <the race proof build> --gate` then `python content/video_engine/scripts/gate_motion_density.py <the race proof build>` and `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_targeted_species.py -q` and `python content/video_engine/scripts/sync_kinetics.py --check`
- Evidence: pending

### T17: R26-97 - promote `species:callout` to a module
- Status: pending
- Owner: junior_developer
- Depends on: T16 (engine lock)
- Write set: `content/video_engine/scripts/species/callout.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the region + the call), `content/video_engine/tests/kinetics/callout.test.mjs`, `content/video_engine/tests/test_kinetics_sync.py` (the `SPECIES` name list), `content/video_engine/effects/cards/species.json` (`lives`)
- Acceptance: the P55 T7 recipe, first because it is the cheapest - its golden `chart-callout` **already exists**, so no new golden is committed. `paintSpecies sp.kind === "callout"` + `calloutPath` (17 lines, rank 306, 9 uses, live) become `species/callout.mjs` with a WHEN / THE LAW header, every literal lifted into a frozen dials object with **no value changed**, the pure math exported and node-tested, the painter registered as the module's last statement (or called by name if the engine's slot demands it, as `verdict.mjs` does - state which). `sync_kinetics.py --check` in sync (the module count rises by one); **every golden byte-identical by sha256** (the promotion's whole proof); the card `species:callout` reads `lives.form: module` with its path and symbol; `effects_catalog_check.py` 0 failures.
- Validate: `node --test content/video_engine/tests/kinetics/callout.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_effects_catalog_drift.py -q` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T18: R26-95 - promote `species:trace` to a module
- Status: pending
- Owner: implementation_luna
- Depends on: T17 (engine lock)
- Write set: `content/video_engine/scripts/species/trace.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/tests/kinetics/trace.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + `tests/golden/frames/trace-hop.png`, `content/video_engine/tests/test_kinetics_sync.py`, `content/video_engine/effects/cards/species.json`
- Acceptance: the golden **first** - `trace-hop` (the hop drawn, a stamp stacked) committed from TODAY's inline code, so the promotion has something to be identical to. Then the P55 T7 recipe on `paintSpecies sp.kind === "trace"` (34 lines, rank 476 - the queue's head, 7 uses, live in the approved Japan short at t 9.22, including the opt-in bowed `hop` the compiler validates at `build_scene_timeline_f.py:1194-1202`). Every golden byte-identical after the lift; `sync_kinetics --check` in sync; node test over the pure math (the hop's bow, the stamp stack); the card's `lives.form -> module`; `effects_catalog_check.py` 0 failures. R26-95's own note holds: it may sit beside the race work because the race is `buildLedgerRace`, not `paintSpecies` - but the engine lock still serialises it.
- Validate: `node --test content/video_engine/tests/kinetics/trace.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T19: R26-96 - promote `species:spotlight` to a module
- Status: pending
- Owner: implementation_luna
- Depends on: T18 (engine lock)
- Write set: `content/video_engine/scripts/species/spotlight.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/tests/kinetics/spotlight.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + `tests/golden/frames/spotlight-hold.png` (+ a proof at the idle's two phases), `content/video_engine/tests/test_kinetics_sync.py`, `content/video_engine/effects/cards/species.json`
- Acceptance: the row's queue condition is now OPEN - it waited on R26-93 (`idle=live`) being committed, and that is `3a6a645`. Golden first: `spotlight-hold` (the dim, the lit datum) plus a proof at the live idle's two phases, committed from today's inline code; then the P55 T7 recipe on `paintSpecies sp.kind === "spotlight"` (20 lines, rank 320, 8 uses, live in Japan with `dur: hold`, `idle: live`). Every golden byte-identical; `sync_kinetics --check`; the node test covers the dim curve and the idle's phase (E56: a picture's focus is the light, and the life check runs on the addition's own region); `lives.form -> module`; `effects_catalog_check.py` 0 failures.
- Validate: `node --test content/video_engine/tests/kinetics/spotlight.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T20: R26-98 - promote `page_species:figure` to a module
- Status: pending
- Owner: junior_developer
- Depends on: T19 (engine lock)
- Write set: `content/video_engine/scripts/species/figure.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/tests/kinetics/figure.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + `tests/golden/frames/page-figure.png`, `content/video_engine/tests/test_kinetics_sync.py`, `content/video_engine/effects/cards/page_species.json`
- Acceptance: golden first (`page-figure`, the written number landed), then the P55 T7 recipe on `paintFigure` (17 lines, rank 204, 6 uses, live in Japan at t 77.02). The module is a PAGE painter (`/* SPACE: page */`, `sync_kinetics.py:122` - a page species registers into the page's registry, not the stage's), which is the one way this promotion differs from T17-T19 and must be stated in the module header. E50 is the doctrine (the number the sentence turns to, written by the hand at its datum). Every golden byte-identical; `sync_kinetics --check`; `lives.form -> module`; `effects_catalog_check.py` 0 failures. If R26-70b's morph lands on the figure (T12), this promotion rebases on it, never the other way round.
- Validate: `node --test content/video_engine/tests/kinetics/figure.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T21: R26-99 - promote `dock_payload:record` to a module
- Status: pending
- Owner: implementation_luna
- Depends on: T20 (engine lock)
- Write set: `content/video_engine/scripts/species/record.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/tests/kinetics/record.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + `tests/golden/frames/record-typewriter.png`, `content/video_engine/tests/test_kinetics_sync.py`, `content/video_engine/effects/cards/dock_payload.json`
- Acceptance: golden first (`record-typewriter`, mid-type and highlighted), then the P55 T7 recipe on `drawRecord` (the typewriter + per-word highlighter; rank 140 - the plan's guess that the record headed the queue did not hold, T1 measured it fourth among dock payloads). It is a DOCK payload, so it follows `verdict.mjs`'s precedent exactly: no registry - the engine's dock slot calls the inlined painter by name, and the `DOCK_PAINTERS` decision stays recorded and unbuilt. The stroke is synced to the NARRATOR's word timings (CAPABILITIES "Record-document species"), so the node test pins the type clock against the word onsets. Every golden byte-identical; `sync_kinetics --check`; `lives.form -> module`; `effects_catalog_check.py` 0 failures.
- Validate: `node --test content/video_engine/tests/kinetics/record.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T22: R26-101 - promote `page_enter:spiral` to a module
- Status: pending
- Owner: implementation_luna
- Depends on: T21 (engine lock)
- Write set: `content/video_engine/scripts/species/spiral.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/tests/kinetics/spiral.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + `tests/golden/frames/spiral-return.png`, `content/video_engine/tests/test_kinetics_sync.py`, `content/video_engine/effects/cards/page_enter.json`, `content/video_engine/effects/cards/page_exit.json` (only if the retract folds in)
- Acceptance: golden first (`spiral-return`, mid-unwind), then the P55 T7 recipe on `lpSpiral` (+ `lpVortex`, `lpParticles`; 39 lines, rank 195, 5 uses, wired on the Tokyo test bed and the bridge short). **The grouping decision this slice makes and records:** the row proposes one module holding both directions - the page's spiral IN and the vortex RETRACT (the implicit card `page_exit:retract`) - because they are the same geometry run two ways; the slice either folds both (and updates both cards) or states in the module header why it did not. Every golden byte-identical; `sync_kinetics --check`; `lives.form -> module`; `effects_catalog_check.py` 0 failures.
- Validate: `node --test content/video_engine/tests/kinetics/spiral.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T23: R26-100 - promote `exit:dip` to a module (and decide the transitions module)
- Status: pending
- Owner: implementation_luna
- Depends on: T22 and T13 (engine lock; the slide must exist first)
- Write set: `content/video_engine/scripts/species/transitions.mjs` (or `kinetics/transitions.mjs` - the slice states which and why), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the render loop's boundary block), `content/video_engine/tests/kinetics/transitions.test.mjs`, `content/video_engine/tests/golden/build_golden_sources.py` + `tests/golden/frames/dip-boundary.png`, `content/video_engine/tests/test_kinetics_sync.py`, `content/video_engine/effects/cards/exit.json`
- Acceptance: golden first (`dip-boundary`: the black boundary frame and the ramp's midpoint), then the P55 T7 recipe on THE DIP block + `dipIn` / `dipOut` (10 lines, rank 180, 9 uses, live - Japan x6, `scene-evidence-engine.mjs:10205, 10295-10301`). **The decision this slice makes and records in its header:** whether dip, blur-zoom, wipe, dissolve, suck **and T13's slide** share one `transitions` module (the row's own proposal) or each is its own - decided on what the code actually shares (the boundary clock and the ramp) rather than on tidiness, with the answer written where the next reader finds it. E47 s1 is the dip's law (a plain LINEAR ramp to black over the last `DIP_S`/2 and back) and must survive the lift unchanged - **no value changed**. Every golden byte-identical; `sync_kinetics --check`; `lives.form -> module` for `exit:dip` (and for any other exit card the module absorbs); `effects_catalog_check.py` 0 failures; the motion gate on Japan (6 dips) unchanged.
- Validate: `node --test content/video_engine/tests/kinetics/transitions.test.mjs` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_chart_transitions.py -q` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

## Open Decisions For The Operator

1. **Three defect rows are already cured in the tree (R26-66, R26-67, R26-68) and one (R26-69) shipped its fix in
   `3642f2a`.** T6-T9 as written are measure-and-close slices with a fix budget. Keep them as delegated slices, or
   have the parent close them on one measurement run and spend the four dispatches elsewhere?
2. **R26-64's dial.** Retire `CADENCE.STROBE_PX_S` (the scope's own word), or apply R26-85's verified recommendation -
   keep 250/300 as operator-set constants, strip the derivation, add 154 px/s as the cinema-parity reference and a
   sharpness term? The two are incompatible: the first is a delete, the second a ruling plus a reader.
3. **R26-67's ellipse reach.** Widening `ringMark`'s reach swells every dense-line ring (54x40 -> 70x52, a sharp peak
   -> 74x114) and moves two goldens - "a form change for the operator, not for a fix". Leave as measured, or rule it?
4. **R26-70's grammar.** A sixth `chart_to` verb (M36 counts it for free, the doctrine line is E73's) versus a new
   page species the floor's M36 row would have to learn. T11 proposes the verb; confirm before any code.
5. **R26-110's retirements.** A findable retirement has to be written in a row that CITES the run path, because the
   ledger is generated and counts only path citations. Confirm that reading, or name another mechanism.
6. **R26-77's blend is a dial, not an answer** (E90 s3 says the operator's eye decides where more pop and "nothing
   pins the eye" pull against each other). T14 ships three renderable settings for HG2. Confirm that, or name the one
   blend to build.
7. **T23's transitions module.** One module for dip + blur-zoom + wipe + dissolve + suck + slide, or one per
   transition? The slice decides on shared code and records it - unless the operator wants the shape ruled first.

## Verification

Every command from the main checkout, `python` =
`C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`, and **no gated step is ever piped into
`tail` or `head`** (`never-pipe-gated-steps-to-tail`: the pipe's exit code is the pager's, and a FAIL has shipped
twice that way). Run gated steps unpiped, or with `set -o pipefail`.

- **The whole tree at the end:** `python -m pytest content/video_engine/tests -q` - the baseline is the parent's
  2026-09-14 read, **3 failed / 2,977 passed** as drafted - superseded the same evening by `bb31d28` (the reds 62 -> 0): the binding baseline is **0 failed / 2,977 passed / 14 skipped**, no new red.
- **Node:** `node --test content/video_engine/tests/kinetics/` green (it grows by one file per promotion).
- **The modules:** `python content/video_engine/scripts/sync_kinetics.py --check` in sync - the module count rises by
  exactly one per promotion (P55 T7 ended at `31 module(s): 14 kinetics, 17 species`).
- **The goldens:** `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q`,
  and for every promotion the sha256 of every golden frame recorded before and after (identical).
- **The catalogue:** `python content/video_engine/scripts/effects_catalog_check.py` **0 failure(s)**, and the seven
  promoted cards reading `lives.form: module` with their module path and symbol.
- **The gates on the approved cuts:** `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`
  and `... /tokyo-tea-break/build-short.v2` reading exactly what they read before the plan (capture both before T1).
- **The engine moved only where a slice says it did:** `git diff --stat -- docs/content-video-engine/samples/scene-evidence-engine.mjs content/video_engine/scripts/build_scene_timeline_f.py content/video_engine/scripts/kinetics content/video_engine/scripts/species content/video_engine/tests/golden`
  naming only the slices' files.
- **The layers:** `python content/video_engine/scripts/build_docs_layers.py --check` ending
  `every layer in sync (10 layers)`, with `research-ledger` reading **0 orphan**.
- **Retrieval, after the rows land:** `python content/video_engine/scripts/docs_find.py "the collision ledger"`,
  `"embed"`, `"slide transition"`, `"living caption"` - each answers with the new CAPABILITIES row, not only the
  backlog row.
- **The plan:** `python scripts/prp_validate.py .claude/PRPs/plans/P57-THE-BACKLOG-BURNDOWN.plan.md` and
  `python scripts/prp_status.py`.

## Risks

- **Closing a row on the code instead of the frame.** Four rows read as cured in source. Source is not a frame; the
  first fix for R26-67 was refused by a frame after the code looked right. Every close in T6-T9 carries a rendered
  instant, not a reading of the diff.
- **The BACKLOG is a shared file and a steward is committing in parallel.** Most slices edit it. The row lock (one
  slice, one row, in the same commit as the change that made it true) is the whole mitigation; a slice that finds the
  row already moved stops and reports.
- **The engine lane is one lock and fourteen candidates** (T5, T7, T10-T16, T17-T23). Parallelising it is how a golden
  gets corrupted; the order in Execution Path is not advisory. This plan is LONG in wall-clock by construction.
- **A promotion that moves a pixel is a failed promotion.** The recipe's whole safety is "no value changed" and
  byte-identical goldens; a lift that "improves" a literal silently re-forms a shipped frame. Any diff in a golden
  stops the slice and comes to the parent.
- **A new golden is a form change in disguise.** T10, T12, T13, T15, T16 and five promotions add goldens. Each needs a
  proof frame and, for the new mechanisms, the operator's eye at HG1/HG2 - a fix never lowers motion (E96/E97).
- **R26-77 can regress the best thing we ship.** Steel and Paper's caption is the base and the operator said so; the
  blend is opt-in and proven on a private build until HG2 rules. No approved short is rebuilt with it.
- **R26-69 may not close.** Forced alignment can still interpolate; the acceptance allows a named residual rather than
  a forced pass, because a shot table that anchors on a phrase cannot use a clock that guesses one.
- **The manifest cap.** 822 B of headroom; `MD_LADDER` degrades a rung rather than failing, so the risk is silent
  detail loss in the cheapest retrieval layer. T4 records the rung and the bytes so the next drop is visible.
- **Scope creep from the rows themselves.** R26-90 touches seven subsystems and R26-110's six runs each invite a new
  plan; T2 and T3 write ROWS and CITES only. Anything that wants building becomes a new backlog row, named.

## Parent recommendations on the open decisions (2026-09-14 - the operator's word was `/goal /prp-implement P57` the same day, with no change to the five; they stand as the decisions)

1. The four defect rows already cured in the tree (R26-66 compiler + M31; R26-67 engine :9042-9055; R26-68 :666/:800; R26-69 shipped in `3642f2a`): the PARENT closes them in T1 with those evidence lines - no lane dispatched. T6-T9 collapse into T1.
2. R26-64: retire only the dials nothing reads; the strobe constants `ON1_PX_S 250` / `STROBE_PX_S 300` stay as operator-set constants per the R26-85 verification (the derivation is stripped, the numbers are not).
3. R26-70 (E76): the metric-to-comparator morph is a SIXTH `chart_to` verb, so P56's M36 counts it as a chart-to-chart transform with no gate change.
4. R26-110: a retirement is a BACKLOG row citing the run path, so `build_research_ledger.py` reads it as landed.
5. R26-77 (E90): one default blend ("pop leads, blended with stagger") plus named settings, never a single fixed blend.

## Evidence And Handoff

- Every slice records, in its `Evidence:` line: the commands run, the verbatim tail of the gated ones, the counts, the
  golden sha256s where a promotion claims byte-identity, the frame paths, and any deviation with its reason.
- Frames and contact sheets for HG1/HG2 go under each build's `self-watch/` or the session scratchpad, listed in one
  place per gate; a served review build is FROZEN once the link is handed over (never rebuilt under the operator).
- Anything longer than a slice's evidence line (a measurement transcript, the triage table for the six runs, the
  promotion sha256 tables) goes to `docs/research/runs/p57-burndown/` and the slice names the path.
- The parent reads every delegated diff and runs each slice's validation itself before integration; a subagent's
  completion claim is not evidence.
- On close: the twenty-five rows carry their verdicts, the ten layers are in sync, the catalogue reads seven more
  modules, and the PRP moves to `complete` with the final test counts pasted here by the parent.
