---
id: P70-THE-BRAVOS-VERBS-WAVE-2
title: The Bravos verbs, wave 2 - the chip lands as a stamp, the schematic, the fill gauge, companion bars, the brace, the equation row, the balance, the rig, the chapter pill (P69 T12/T46/T51/T52/T58/T56/T59/T69/T61)
status: running
operation: feature
risk: standard
owner: parent
branch: claude/fable-p68 (the plan); engine slices land on claude/p69-s90 (lane B)
contract: tdd-v1
created: 2026-09-24
updated: 2026-09-24 (APPROVED by the operator - `/prp-implement p70` - and running; revision 2 folded in REVIEW.md 1-11)
---

# P70 - The Bravos verbs, wave 2

## Summary

The operator's request, verbatim: `/prp-plan T46 the schematic, T51 the fill gauge, T52 companion bars, T56 the
equation row, T58 the brace, T59 the balance scale, T61 the chapter pill, T69 the rig, and T12 the chip landing as a
stamp.`

These are nine P69 slice stubs. This plan turns each into a slice grounded in the code, keeping its P69 id as an alias
so the parent can point P69 at P70 (the parent edits P69, not this plan). P69 T61 carried two verbs, A34 (the chapter
pill) and A44 (the in-place swap). They are split into T9 and T10 here, because A44 has a blocker that A34 does not.

Recall was run on every verb (the `Recall:` lines in each slice), and then the code it pointed to was read. The verdicts:

| P70 | was P69 | verb | verdict | why, in one line |
|---|---|---|---|---|
| T1 | T12 | the chip lands as a stamp | EXTEND | `form: "stamp"` exists (`chip.mjs:44 CHIP_STAMP`), but it lands on the chip's spring, not on `stampXf` |
| T2 | T46 | the schematic | EXTEND | a generated closed-form series on the existing line page, with its values suppressed. There is no `page_builder:cycle` and one is not needed |
| T3 | T51 | the fill gauge | EXTEND | a third chart FORM (`gauge`) on the `progress` variant, which today has no painter (card status `declared`) |
| T4 | T52 | companion bars | REUSE (+ one WARN) | a PANELS page with a hidden bars panel revealed on its word already does this (`lpPanelStart`, T8b-T8d). It becomes a recipe and a golden. E79 / E53 s4 add the missing WARN for one measure drawn in two units |
| T5 | T58 | the decomposition brace | EXTEND | `bracket` already takes `form` (`BRACKET_FORMS = ("span", "bar")`). `brace` is added on a stacked bar (T64's `segments`) |
| T6 | T56 | the equation row | NEW | nothing lays out terms or computes a result. It is a new stage species module |
| T7 | T59 | the balance scale and the tip | NEW | no beam or balance exists. It is a new stage species module |
| T8 | T69 | the rig (the poof arrival) | NEW | `arrive: poof` is added to `ARRIVALS`, plus a candidate `recipe:the-rig` |
| T9 | T61 (A34) | the chapter pill | NEW | the timeline has no chrome track that crosses scenes. The pill's look reuses the key rail |
| T10 | T61 (A44) | the in-place badge swap | EXTEND (of T9) | BLOCKED: the harvest says verify BOOM's Gemini-only timings first (v2 `:318`) |

T1 feeds P69 T13 (P69-HG1, the chip landing and the contact instant). T13 stays in P69.

**Provenance (captured 2026-09-24 14:20; `scratchpad/p70-plan/provenance.txt`).**
- Lane A (fable-p68): `b67df03`. The brief expected `deceff3` or later; two commits have landed since: 3473082 (R26-305)
  and b67df03 (R26-306). Tracked dirty files (`git status --short | grep -v '^??'`): `effects/cards/dock_payload.json`,
  `effects/lab/candidates.jsonl`, `steel-and-paper/SHOT-TABLE-H.md`, `build-h/GATES-MOTION.md`, `build-h/SHOT-TABLE-H.py`,
  `build_episode_h.py`. P69's plan and CAPABILITIES are clean at b67df03.
- Lane B (p69-s90): `c0836b8` (P69 T64, the stacked bar and combo), branch `claude/p69-s90`, with no tracked dirty files at
  capture. By the review, P69 T37 (`solo`) was STAGED on top of it: 17 files, including the engine, the compiler, the
  gate, `lint_species_choice`, `recipe_walk`, `test_kinetics_sync`, the golden lists, SPECIES-BY-SENTENCE and
  `test_build_effects_catalog`.
- **P70's base is NOT c0836b8** (the parent's ruling 1). P70 starts after P69's in-flight lane-B slices land: T37 (solo),
  T37b (the bloom and series-inked names, E99 s117 / s118), T65 (rings), T85 (the bar stagger) and T87 (the empty-plot
  gate). T0 re-captures the head at dispatch time. Every `:line` anchor below is at c0836b8 and is re-read by its symbol
  in the brief.
- The sha256 of every file the slices edit, at c0836b8, is in `provenance.txt`. The engine's is `4e6676ea...ad36`.

`$SP` below means
`C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad`.
The planning evidence is in `$SP/p70-plan/`: `recall-raw.txt` (every docs_find run), `take-times.txt` (every H beat's
word times off `vo-h-scratch/scratch-kokoro.words.json`) and `provenance.txt`.

## Intent And Acceptance

Each verb is a capability an author can reach from a shot row, and each is proved on a real H body beat (E99 s60: a
proof is a scene, never a fixture). Every verb is opt-in. An existing row compiles and renders byte-identically, and so
do the committed H door and every golden it does not name. Honesty rules are hard, and placement findings are WARNs
(s106).

Plan-level acceptance:
1. T1-T9 are merged into lane B, one commit per slice, each with its own red, green and frame evidence in this plan.
2. The committed H door (lane B's `build_episode_h.py` at P70's base, T0) compiles identically (`engine_sha256` aside), and its
   rendered instants are identical before and after every slice.
3. The goldens are re-pinned once, at the merge, with a sha table in the commit message. `page-boxes.v1.json` is
   regenerated once by `measure_page_boxes.py --write`.
4. Each verb has its card or recipe, and each built capability has its CAPABILITIES row in the same commit (the shared
   registry process). The effects drift gate and `effects_catalog_check.py` report 0 failures.
5. P70-HG1 is framed on the review queue: the operator watches the nine beats at the end.

## Scope

- T1-T9 as specified below: the engine (`docs/content-video-engine/samples/scene-evidence-engine.mjs`), the species and
  kinetics modules, the compiler (`build_scene_timeline_f.py`), `ledger_page.py`, the gate registries, the cards and
  recipes, the goldens and the tests.
- T10 is specified, and blocked until its evidence exists.
- T0: the parent's bookkeeping (approval, register, queue row, P69 pointers).
- T11: the integration and merge in lane B.
- T12: P70-HG1.

## Not Building

- **P69 T13 (P69-HG1)** stays in P69. T1 only produces the mechanism and goldens that its proof door imports.
- **Laying real data over a schematic** (P69 T46 (3), "the shape meets the data"). There is no H beat for it, and one x
  axis for a shape and a series has no honesty rule yet.
- **A55, the traced state** (a point running along the curve and painting each phase's colour). T36's lit stretch is
  the travelling light. The point is left out.
- **A brace on flow nodes, chips or figures.** This is v1 harvest `#13` "`flow` option `brace`", which is the Bravos
  frame's own form. No H sentence decomposes a diagram, so T5 braces a stacked bar only.
- **The equation's term docking into the page as its figure** (P69 T56 (3)), and **T44's `the-formula-by-its-words`
  recipe (R25)**, which stays P69's.
- **A swap on the key-rail, span or axis_tag pills.** `axis_tag` is P69 T38 and still pending, and `span` draws no pill.
  T10 swaps the chapter pill only.
- **H body adoption** of any verb. The body rows are lane A's (P69 T15-T33), and the chapter pill waits on the
  operator's word (harvest v2 `:274`).
- **Flow orders, paid generators and new plates.** None are used. T8's one new prop, "the paper", is ordered by the
  image-claim flow (codex GPT Image, headless), which is not Flow and needs no consent (E36, `:1175`: "images are
  free"). It stays quarantined until the operator approves it at P70-HG1.
- **Anything P69's in-flight lane-B slices own** (Execution Path, "The base and the functions P70 must not touch").

## Human Gates

- **P70-HG1** (T12): at the end, the operator watches the nine verbs' beats as private test-bed builds played with the
  take (s60: never a golden served as a scene), each beside the Bravos frame it was harvested from. The standing
  instruction: "resolve all non-human blockers and i'll review human gates at the end". It blocks nothing inside P70.
  - It carries one question, (a): whether any verb's beat is adopted by an H body row, including the chapter pill's act
    markers. It is asked once, not again at P69-HG4.
  - It carries one approval: bringing T8's paper prop out of quarantine.
  - The record already answers the scale question (E79 / E53 s4) and the row-16 tip (USE-WHEN `:646`), so neither is
    asked.
- **P69-HG1** (P69 T13) is fed by P70 T1. It is framed in P69 and stays there.
- The runbook requires every gate a plan names to have a row in `docs/content-video-engine/REVIEW-QUEUE.md` in the same
  change that frames it. That file is not in the architect's write set, so T0 adds the P70-HG1 row.

## Mandatory Reads

No backend or frontend skill applies. This is a Python compiler plus a vanilla-JS, seek-safe render engine: no
React/Next, no server, no database. The repo contracts are the reads instead:

- `docs/AGENTS-VIDEO-ENGINE.md`, `docs/content-video-engine/PIPELINE.md`, `docs/content-video-engine/CAPABILITIES.md`
  (lane B `:79`, `:99`, `:100`, `:103`, `:124`, `:210-:238`).
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (Parts 3, 8, 9; §9.15).
- `docs/portable/OPERATOR-RULINGS.md`. Every slice cites what it respects. Lane A's copy carries s116 (`:3363`), s117
  (`:3365`, the lines bloom) and s118 (`:3367`, a chart's names wear their series' ink), which lane B's copy lacks. Also:
  E79 apply 1 (`:2517`), E53 s4 (`:1740`), E53 addendum (`:1784`), E36 (`:1175`), E81 (`:2542`).
- Doc 42 §42.4 (`docs/content-video-engine/42-*.md:102`, "Curve quality — Euler spirals for generated geometry"; quoted at
  engine `:442-:444`: it applies to "arrows, balance arms, connectors, axes") governs T5's brace curve and T7's arms.
  The s90 phone floor is 59.08 stage px (`ledger_page.CARD_TYPE_PX`, `:4187-:4188`) and holds for every label a slice
  adds.
- `docs/runbooks/HEADLESS_CLAIM_RESUME.md` (T8's claim).
- P69's in-flight slices T37, T37b, T65, T85 and T87 (their write sets: what P70 must not touch).
- `docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md` (§0 sources, §1 TYPES, §2 ACTIONS, §4 RECIPES, `:257-:274`,
  `:294`, `:317-:318`) and `docs/research/bravos-style/BRAVOS-USE-WHEN.md` (the entries quoted per slice).
- `content/video_engine/configs/effect_card.schema.json`: `does` minLength 10 / maxLength 240 (`:115-:119`), `when` null
  on `species` / `page_species` / `chart_to` (`:121-:127`), phase `name` maxLength 40 (`:212-:215`).
  `content/video_engine/configs/effect_recipe.schema.json`. `content/video_engine/scripts/effects_catalog_check.py:1-35`
  (the 12 checks).
- `docs/runbooks/PRP_EXECUTION.md` (Dispatch mapping, Hand-off policy, Lane write sets). The lane-B workflow as run for
  T64 and T84: `$SP/p69t84/NOTES.md` (Setup, Identity, Per-file pytest, Patch) and `$SP/p69t64/NOTES.md` (the CRLF
  correction).

## Execution Path

### The lane-B workflow (every engine slice)

1. The implementer works in a **scratch export of lane B at its head**, never in the lane-B checkout itself:
   - `git -C "<p69-s90>" archive <head> | tar -x -C $SP/p70-tN/tree`;
   - `git init`, then force-add the gitignored inputs the door and tests need. The lists are
     `$SP/p69t84/logs/missing-forced.txt` (1170) and `$SP/p69t81/logs/ft-inputs.txt` (1016 door inputs);
   - commit that as the base. The patch is `git diff --binary <base>`.
2. **The base fail set comes first.** Run every validation file, each in its own process, on the base. The known
   pre-existing failures at c0836b8 are `test_shape_skeletons::test_the_mix_re_derives_byte_for_byte` (CRLF) and
   `test_authoring_kit` x2 (`$SP/p69t64/NOTES.md`). A slice is green when its fail set equals the base's.
3. **RED, then GREEN, then REFACTOR**, each logged under `$SP/p70-tN/logs/`.
4. **Byte identity of the committed H door.** Use the method in `$SP/p69t84/scripts/door_identity.sh`: the same tree and
   inputs, with the slice's sources swapped between the base and the patch. Every output must be identical except
   `engine_sha256`, and the rendered instants must be identical (N of N).
5. **The return.** A patch against lane B's head that is LF-only (0 CR, counted by Python and not `grep -c $'\r'`, per
   T64's correction), is `git apply --check` clean on a fresh export, and comes with its sha256. Also return:
   - per-file pytest counts, base vs patch;
   - the door-identity log;
   - a suggested CAPABILITIES row (the parent writes it);
   - the card or recipe JSON inside the patch;
   - the frame PNGs the frame acceptance names.

   Golden sources are written LF (`build_golden_sources.write_surface` writes the platform newline, which is the T64
   trap). A patch never carries a generated file (see "Who owns what").
6. **The parent reviews** the diff, runs the slice's Validate itself, and reads the frames. For T1, T3, T6, T7, T8 and
   T9, `reviewer` reviews before integration. Then `release_steward` commits in lane B with explicit paths, one commit
   per slice.

### The base and the functions P70 must not touch (the parent's ruling 1)

Lane B has ONE writer per function. P70 is dispatched on the head re-captured by T0, after P69's in-flight lane-B slices
are committed. No P70 slice edits these; a slice that finds it must is stopped and the parent sequences it:
- **T37 (`solo`):** `species/solo.mjs`, its engine paint and dials, `_validate_solo`.
- **T37b (s117 / s118, the series ink):** the series stroke's bloom layers (`lpBloom` and the stroke paint of
  `buildLedgerLine`), the solo's lit / muted dials, the end tags' and series names' INK, and `measure_line_bloom.py`.
  P70 labels that name a series (T2's phases, T3's figure, T4's bars, T5's parts) READ T37b's series-ink helper and never
  set a colour of their own. T2's schematic line is a primary line, so it blooms by T37b's default and T2 does not touch
  the stroke.
- **T85 (the bar stagger):** `lpPaintChart`'s bar grow and label stagger. T3's gauge branch lives in `buildLedgerBars`
  and reads the build clock; it does not change the stagger.
- **T65 (ring targets):** `_validate_callout`, the ring species' target kinds (`:1165`), E56's messages.
- **T87 (the empty-plot gate):** its new M row in `gate_motion_density.py`. T2's schematic and T3's gauge must pass it,
  because a page with no drawn ink is exactly what it measures.

### Who owns what (parallel slices never edit the same function)

Every slice edits `scene-evidence-engine.mjs` and most edit `build_scene_timeline_f.py`. The runbook asks for disjoint
FILES when dispatching in parallel. Here each implementer edits its own scratch export, so no working tree is shared,
and the parent integrates with `git apply --3way` in the order below. That is a stated deviation (see Evidence And
Handoff). The rule that keeps it safe is that no two slices in one wave own the same function or region:

| slice | engine (functions / regions it owns) | compiler / Python (functions it owns) |
|---|---|---|
| T1 | the `chip` KINETICS region (via `species/chip.mjs` + `sync_kinetics.py --write` only) | `_validate_chip` (`:2471`), a new `CHIP_ARRIVALS`, the chip-stamp block of `main()` (`resolved_chip_stamps`, `:9926`), the stamped-chip case of the stamp-timing advice (`:7717-:7760`); gate `_landings` (`:3320`), `_arrivals` (`:3491`); `recipe_walk.py` arrival emission (`:219`) |
| T2 | `buildLedgerLine` (`:10780`): its tick-value and end-tag-VALUE writes only, behind `pg.schematic` (never the stroke or the tags' ink, T37b's); a new `lpSchematicTag` | `ledger_page.py`: a new `SCHEMATIC_SHAPES` + `schematic_series`, the `validate` dispatch for the object shape; `measure_page_boxes.py` (a representative, parent-merged) |
| T3 | `buildLedgerBars` (`:10336`): a `formOf(pg, "gauge")` branch only | `ledger_page.py` `CHART_FORMS` / `FORM_BUILDERS` / `FORM_READS` / `form_error` (`:846-:862`), `_validate_values` progress (`:2336`); compiler `page_form_geom` (`:5461`), `page_form_spec` (`:6116`); `measure_page_boxes.py` (a representative, parent-merged) |
| T4 | none | `ledger_page.scale_warnings` (`:1568`), the panel `measure` key; a recipe, a golden and a test |
| T5 | `buildPerform` (`:13841`): the bracket block only (`geomOf`, `mk`); `paintBracket` (`:14109`) | `BRACKET_FORMS` (`:456`), the bracket branch of the page-species validator (`:2219-:2232`, the brace branching BEFORE the `from`/`to` check), a new `check_brace` beside `check_members` (`:3039`) |
| T6 | a NEW KINETICS region `equation`, inserted immediately after the `freeze` region's `KINETICS:END` (`:19363` at c0836b8; its BEGIN is `:19216`) | a new `_validate_equation`; its dispatch line; the registries (below) |
| T7 | a NEW KINETICS region `balance`, inserted immediately before the `ring` region's BEGIN (`:18557`); the `paintSpecies` painter-ctx object (`:19383`), only to expose `propHatchLines` | a new `_validate_balance`; its dispatch line; the registries |
| T8 | `render()`'s dock-arrival branch (`:20281`, `stamped ? stampXf(...)`); the `stopaction` KINETICS region (a new `poofXf` export in `kinetics/stopaction.mjs`) | `ARRIVALS` (`:106`), `PLATE_ARRIVALS_REFUSED` (`:4778`), `dock_opts` (`:6222`); gate `_landings` / `_arrivals`; `authoring/audio.WEIGHTED_ARRIVALS` (`:137`), `landing_contact` (`:165`), `arrival_mass` (`:180`) |
| T9 | a new `paintChapters` const plus one call in `render()` after `paintSpecies(sc, t)` (`:20590`) | a new `_validate_chapter`; the chapter lift into the timeline dict in `main()` (`:10458`); the chapter box passed as `extra` to `ring_obstacles` (`:7273`) |
| T10 | `paintChapters` (the swap) | `_validate_chapter` (the `swap` keys) |

**The registries are the parent's integration points** (runbook: "shared integration points ... stay with the parent";
REVIEW.md 2). Each patch carries its own lines, and the parent unions them when applying:
- `measure_page_boxes.py` `GOLDEN_PAGES` (`:100`), `representative()` (`:374`), `BUILDERS` (`:391`) (T2 and T3 both add
  a representative);
- the cards `page_builder.json`, `species.json`, `page_species.json`, `arrival.json`, `plate_option.json` (one card
  object per slice);
- the compiler's `_validate_entry` dispatch chain (`:3185-:3215` at c0836b8) and the new `_validate_*` defs beside it
  (T6, T7 and T9 each add one);
- `test_build_effects_catalog.py`'s exception list in `test_every_wired_card_is_in_a_recipe` (`:385`, the
  `assert uncovered == [...]` list and its comment). Every slice that adds a wired card runs that test and names the
  line it adds or removes: T2 `page_builder:line+schematic`, T3 `page_builder:progress`, T6 `species:equation`,
  T7 `species:balance`, T9 `species:chapter`. T4 REMOVES `page_species:panel_focus`, because its recipe composes it. T8
  adds none, because `recipe:the-rig` composes `arrival:poof` and `recipes_of` counts every recipe regardless of status.
  T1 and T5 add options to existing cards, not cards;
- `SPECIES_KINDS` (`:408`), `SPECIES_WHEN` (`:572`);
- `lint_species_choice.ACT_SPECIES` (`:74`), `recipe_walk.PAGE_SPECIES_KINDS` (`:87`),
  `authoring/shapes.PLOT_MARKS` (`:631`);
- `gate_motion_density.SPECIES_EVENTS` (`:357`), `tests/test_kinetics_sync.SPECIES` (`:42`);
- `SPECIES-BY-SENTENCE.md` §4 (regenerated by `lint_species_choice.py --when --write-doc`);
- `golden/build_golden_sources.py` (appended surfaces), `test_golden_frames.py` (the name list).

**Generated files are never in a patch:** `docs/EFFECTS-CATALOG.*`, `content/video_engine/assets/page-boxes.v1.json`,
`docs/content-video-engine/SPECIES-BY-SENTENCE.md` (and the other docs layers). The implementer runs their `--write` in
the scratch tree only, to prove `--check` passes. The parent regenerates them once per applied slice (T11).

**Order.** Concurrency is at most four. Waves are dispatched on P70's base (T0), in parallel, and integrated in the
listed order.
- **Wave 1: T1, T2, T3, T4.** The functions are disjoint. T1 is on the gate and the stamp.
- **Wave 2: T5, T6, T7.** They are disjoint. T6 and T7 meet only in the registries.
- **Wave 3: T8, then T9, in sequence.** Both own hunks of `render()`, and T8 shares the gate's `_landings` /
  `_arrivals` with T1, so it is built on T1's merged commit.
- **T10** waits on its blocker. **T11** integrates, and **T12** is the operator's gate.

**Routing.**
- `implementation_luna` (Opus) builds each verb.
- `reviewer` (Opus) reviews T1, T3, T6, T7, T8 and T9, the slices that touch the stamp, the sound, a gate or a truth
  gate (M26).
- `release_steward` commits. It never pushes without the operator's current word.
- The parent owns the briefs, the frame reads, the registry unions, CAPABILITIES and the merge.

## Patterns To Mirror

- **A new page species with its checklist**: P69 T36, `104af07` (19 files).
  - `species/lit_stretch.mjs` plus its region;
  - `SPECIES_WHEN`, `lint_species_choice`, `authoring/shapes.py`, `gate_motion_density.py`;
  - the card in `page_species.json`;
  - the golden in `build_golden_sources.py` and `test_golden_frames.py`, and `SPECIES-BY-SENTENCE.md`;
  - "H door compiles identical ... renders 10 of 10 instants identical".
- **A new field on an existing builder, refused by name and honest**: P69 T45 `9caa76b` (`members`) and T64 `c0836b8`
  (`segments`, `BAR_FIELDS`; "a stack that does not sum to its written total" refused).
- **A new builder form**: P58 T5's `extruded_bar` (`CHART_FORMS`, `form_error`, `formOf(pg, "extruded_bar")`: "null is
  today's page, to the byte").
- **The stamp and its sound**: P69 T2-T4 (`STAMP_CONTACT_S = 0.1542`), T81 `de6af2a` (the word-END anchor, the advice),
  and T84 `e416df5`. T84's rule (s116): the binder retimes a bound `landing` cue to its compiled contact, through
  `authoring/audio.fired`, which reads `recipe_walk.events` arrivals.
- **An authored place, where the fit advises**: P69 T26d `5c6871c` ("`read`/`read_s`/`park_s`/`centre_band` on a stamp
  are REPORTED as a WARN and not applied").
- **A panels page with a hidden panel revealed on a word**: P69 T8b-T8d, the golden `panels-resize` ("panel 2 hidden"),
  `lpPanelStart` (`:12371`).
- **A candidate recipe proved as a beat**: P69 T47 `5bb0743`, `recipe:rings-in-turn-on-the-vertices` (members, offsets,
  `use_when` block).
- **Golden sources read from committed objects, never re-typed**: T64's `stacked_funding_series()` in
  `build_golden_sources.py`.

## Task Slices

### T0: The base, the approval, the register, the review-queue row and the P69 pointers
- Status: in_progress (the parent)
- Owner: parent
- Depends on: the operator's approval of this plan, and P69's in-flight lane-B slices committed: T37 (`solo`, staged on
  c0836b8 at the review), T37b (the bloom and series-inked names, E99 s117 / s118), T65 (rings on the named thing), T85
  (the bar stagger), T87 (the empty-plot gate)
- Write set: this plan (status, the base, T0 evidence); `$SP/p70-plan/provenance.txt` (re-captured); `docs/WORKTREE-REGISTER.md`
  (lane B's row names P70 and its one engine writer); `docs/content-video-engine/REVIEW-QUEUE.md` and
  `docs/content-video-engine/review-queue.v1.json` (the P70-HG1 row); `.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`
  (T12, T46, T51, T52, T56, T58, T59, T61 and T69 each point to their P70 slice; T13's `Depends on` names P70 T1)
- Acceptance:
  1. **The base is re-captured at dispatch time.** Record `git rev-parse HEAD` and `git status --short | grep -v '^??'` in
     lane B once the five P69 slices above are committed, and the sha256 of every file P70 edits. That head is P70's
     base. Every slice's brief names it, and re-reads every `:line` anchor in this plan by its SYMBOL, because the anchors
     here are at c0836b8 and T37 alone moves the engine (+113 lines) and the compiler.
  2. The approval is quoted here.
  3. The register row is updated before lane B's first P70 commit. Lane B keeps ONE writer per function.
  4. The queue row `p70-hg1-the-nine-verbs` exists, naming what to judge, where to look and what it blocks.
  5. Each of P69's nine stubs reads "moved to P70 T<n>".
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P70-THE-BRAVOS-VERBS-WAVE-2.plan.md` then `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md` then `python -m pytest content/video_engine/tests/test_worktree_register.py -q`
- Evidence: (2) APPROVAL, the operator 2026-09-24: `/prp-implement p70` (after the plan was presented READY WITH FIXES, fixes applied). (5) P69's nine stubs point here (this commit). (3) the register row names P70 on lane B (this commit). (4) queue row `p70-hg1-the-nine-verbs` added (this commit). (1) the base is re-captured per slice at dispatch. DEVIATION (the parent): T1 (the chip stamp) is dispatched on lane B ffa2877 BEFORE T37b lands - T1 owns `chip.mjs`, `_validate_chip`, the gate's `_landings` / `_arrivals` and the binder's chip branch, none of which T37b touches (T37b owns the series ink: `lpBloom`, the stroke, end tags, series names, the solo dials); T2-T9 wait for T37b as planned.

### T1: The chip lands as a stamp - `arrive: "stamp"` on the stamp-form chip, rendered both ways (was P69 T12)
- Status: done - lane B `5c25444` (the chip lands as a stamp; frame-read, reviewed MERGE WITH FIXES applied)
- Owner: implementation_luna (LANE B), then reviewer (the stamp, the gate, the sound)
- Depends on: P70's base (T0); done P69 slices T2-T5 (the stamp as a landing), T26d `5c6871c` (the fit advises), T81
  `de6af2a`, T84 `e416df5`. Nothing in P70.
- Harvest: none. The stamp is remotion-ui RU-2's badge-stamp port (E99 s87, CAPABILITIES `:79`), not a Bravos verb. The
  chip is Bravos's icon board (CAPABILITIES `:100`: shots 26-28).
- Recall: docs_find "stampXf" -> `docs/content-video-engine/CAPABILITIES.md:79` "The STAMP arrival (arrive: stamp) and the BARE PROP payload (prop: True) — BUILT - remotion-ui RU-2's badge-stamp PORTED from its source on disk, not re-deri…"
- Recall: docs_find "stamp" -> `CAPABILITIES.md:210` "The stamp is a landing to the gate, the cue and the camera — WIRED - all three read its contact, 0.1542 s after the enter."; `:211` "The stamp is punctuation - it lands just AFTER the word it names"
- Recall: docs_find "chip" -> `CAPABILITIES.md:100` "The icon CHIP - a named thing as one of a set, crossed out on a later word — WIRED"; `:103` "The FLOW DIAGRAM - chips, clothoid arrows, the swap — WIRED"
- Recall: docs_find "chip form stamp" -> 3 hits, none a capability row. The form lives in code only: `species/chip.mjs:44` "OPT-IN STAMP FORM (P62)" `CHIP_STAMP`
- Verdict: EXTEND.
  - `chip.mjs paintChipStamp` poses the art with `chipPose` = `chipLand` = `springPop` (the spring), so it never reaches
    `kinetics/stopaction.mjs` `stampXf` (`:423`), `stampRing` (`:401`) or `stampExit` (`:413`).
  - `build_scene_timeline_f._validate_chip` (`:2471`) reads no `arrive`.
  - The gate's `_landings` (`:3320`) and `_arrivals` (`:3491`) read docks only.
  - `authoring/audio.fired` (`:313`) pairs cues to `recipe_walk.events` arrivals, which are emitted for docks only
    (`recipe_walk.py:219`).
  - stopaction's region (`:1763`) precedes chip's (`:16498`), so the import is legal.
- Write set: all existing unless marked new -
  - `content/video_engine/scripts/species/chip.mjs` (the stamp branch of the pose and `paintChipStamp`; the glyph chip
    and the `landscape-phone` branch untouched);
  - the engine's `chip` region, via `sync_kinetics.py --write` only;
  - `content/video_engine/scripts/build_scene_timeline_f.py` (`_validate_chip`, `CHIP_ARRIVALS`, the `main()`
    chip-stamp block, the stamp-timing advice);
  - `content/video_engine/scripts/gate_motion_density.py` (`_landings`, `_arrivals`);
  - `content/video_engine/scripts/recipe_walk.py` (the arrival emission);
  - `content/video_engine/scripts/authoring/audio.py`, only if `fired` cannot see the chip through `recipe_walk`;
  - `content/video_engine/effects/cards/species.json` (`species:chip` options);
  - `content/video_engine/tests/kinetics/chip.test.mjs`;
  - `content/video_engine/tests/test_chip_stamp_arrival.py` (new);
  - `content/video_engine/tests/golden/build_golden_sources.py`, `content/video_engine/tests/test_golden_frames.py`;
  - `content/video_engine/tests/golden/sources/chip-stamp-{pop,arrival}.*` (new),
    `content/video_engine/tests/golden/frames/chip-stamp-{pop,arrival}.png` (new).
- Input evidence: H row 7's "And it isn't Bravos Research ... and it isn't Nvidia" (take `isn't Nvidia` 58.35-59.60;
  SHOT-TABLE-H #4, `ledger:ev-divergence-v1:line:234:right:...`, where the door's `NVIDIA_CHIP` lands at 58.60). The
  golden recasts that chip as `form: "stamp"` on `prop-icon-gpu-ai-accelerator-v1` (icons catalogue), label `NVIDIA`.
  The two goldens differ only in `arrive`.
- Constraints:
  - Byte-identical absent `arrive`.
  - The glyph chip, `flow`'s node chips and the count array keep `chipLand` (goldens `chip-board`, `flow-swap`,
    `ring-dashed-chip`, `count-array` unchanged).
  - `longform` is not a chip option (the stamp form refuses `readability`, `:2502`).
  - No new motion dials. Every motion number is `STAMP_ARRIVAL`'s.
  - **The label's size (the s90 floor).** `CHIP_STAMP.LABEL_SIZE` is 48 stage px (`chip.mjs:55`), under the floor of
    59.08 (`ledger_page.CARD_TYPE_PX` `:4188`). Under `arrive: "stamp"` the label is drawn at `CHIP_STAMP.LABEL_FLOOR` =
    59.08 [DERIVED: `ledger_page.CARD_TYPE_PX`], with `LABEL_GAP` / `LABEL_LINE_H` scaled with it. A stamp-form chip
    WITHOUT `arrive` keeps 48 (byte identity), and the compiler WARNs with the numbers that its label is under the s90
    floor (s106 advice; the author adds `arrive` or a `size`).
- Acceptance:
  1. `arrive: "stamp"` is legal only on a `form: "stamp"` chip. On a glyph chip it is refused by name ("the stamp arrival
     is the stamp form's"). Any other value is refused, naming `CHIP_ARRIVALS`.
  2. With it, the art's pose at `t - at` is `stampXf`'s:
     - the scale comes down from 2.1 in area space and is exactly 1 from `STAMP_LAND.tc` (0.1542 s);
     - the free rotation overshoots and rests at `LAND_DEG`, off-square;
     - the ink runs [1, 0.86] and the opacity rides `FADE`;
     - the impact ring runs on its split curves around the art's own radius and is never held;
     - `stampExit` runs inside `dur` (the exit owed, E50).
  3. Without it, `chipPose` is identical to today's over 200 sampled instants.
  4. The ring's peak (`RING_TO` x the radius) is fitted by `stamp_fit` against `ring_obstacles` at compile time and
     written on the species. When nothing fits it is a WARN with numbers, never a refusal (s106; this amends the P69
     stub's "or refused").
  5. The gate counts a stamped chip's landing at `at + STAMP_CONTACT_S`. `recipe_walk` emits `arrival:stamp` for it, so
     `fired` pairs a `landing` cue to that contact (s116). A glyph chip's events are unchanged.
  6. s112: the stamp-timing advice WARNs when a stamped chip's contact falls inside its own word or within
     `STAMP_DATA_CLEAR_S` of a data mark. `at` may be authored with `authoring.words.after` (T81).
  7. There are two goldens from one source. The H door is byte-identical: it has no stamp-form chip, because
     `NVIDIA_CHIP` is `icon: "cpu"`.
- Exclusions: the camera's landing pull on a stamped chip (T4's `_attention_moves` reads placed docks; a chip has no
  `place`); flow nodes landing as stamps; any change to `STAMP_ARRIVAL`.
- Stop conditions: `paintChipStamp` already calls `stampXf` at P70's base (stop and report); `_with_stamp_catalogue`
  refuses the icons-catalogue glyph (report, and do not widen the catalogue).
- Regression: `node --test content/video_engine/tests/kinetics/chip.test.mjs`
- Expected RED: `chipPose` returns the springPop pose with and without `arrive: "stamp"`; `_validate_chip` accepts
  `arrive: "stamp"` on a glyph chip; `gate_motion_density._landings` has no entry at `at + 0.1542` for a stamped chip.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `node --test content/video_engine/tests/kinetics/chip.test.mjs` then `node --test content/video_engine/tests/kinetics/stopaction-stamp.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_chip_stamp_arrival.py`, `test_chip_stamp.py`, `test_the_stamp_arrival.py`, `test_the_stamp_lands_after.py`, `test_stamp_is_a_landing.py`, `test_landing_sound_follows_the_landing.py`, `test_gate_motion_density.py`, `test_recipe_walk.py`, `test_kinetics_sync.py`, `test_build_effects_catalog.py` (no exception-list line: an option on the existing `species:chip`), `test_golden_frames.py`, `test_effects_catalog_drift.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `chip-stamp-pop.png` beside `chip-stamp-arrival.png` (FRAME_T = contact + 0.10 s,
  the rotation still off its rest), a strip at contact -0.05 / +0.00 / +0.10 / +0.154 / +0.30 s
  (`$SP/p70-t1/frames/`), and the dock's `prop-stamp` golden for parity.
- Return: the common lane-B return (Execution Path, step 5). CAPABILITIES row suggestion: amend `:100`, "the stamp form
  may land by the stamp arrival".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending (the base fail set at c0836b8)
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T1b: A seal-type stamp is a seal - the solid border, ring text on two half-arcs, the shockwave from the impact frame, the ink easing back (E99 s121)
- Status: done - lane B `50b2f85` (the six fixes + the parent's no-squash default `CHIP_STAMP.SQUASH: 0`; 182/182 goldens, kinetics 727, test_stamp_is_a_seal 30; known gap: the impact ring inks charcoal on a dark non-ledger plate)
- Owner: implementation_luna (LANE B), then reviewer (the stamp's law on every door)
- Depends on: T1 integrated
- Harvest: remotion-ui badge-stamp (RU-2) - the port's source `content/video_engine/remotion-ui/src/remotion/primitives/badge-stamp.tsx` (ringText / ringTextBottom, the border rings, the shockwave's start, the ink ease) and the component's docs https://remotionui.com/docs/components/badge-stamp; REUSE the port (`kinetics/stopaction.mjs` STAMP_ARRIVAL / stampRing / stampXf), never re-derive
- Write set: `content/video_engine/scripts/kinetics/stopaction.mjs` (the shockwave's clock from the contact; the ink ease), `content/video_engine/scripts/species/chip.mjs` (the seal border + ring text on the stamp form), the dock's stamp paint in `docs/content-video-engine/samples/scene-evidence-engine.mjs` (a badge/verdict stamp's seal; a bare prop unchanged but for the shockwave clock), `content/video_engine/scripts/build_scene_timeline_f.py` (`ring_text`, `ring_text_bottom` options, refused on a bare prop by name citing s87 / s121), the cards, tests, goldens re-pinned where the shockwave clock moves them
- Acceptance: s121 (1)-(4): a seal-type stamp (stamp-form chip, badge, verdict) carries a solid outer + thin inner ring that stay; ring text on two half-arcs both reading left to right, each refused past the ring's side (a length WARN with numbers); a bare prop stamp has no border; EVERY stamp's shockwave starts at the contact (0.1542 s) - measured, zero shockwave ink before it; the ink eases back after the hit on the chip; the parent reads ours beside the remotion-ui reference frames on one sheet; P69-HG1's 'the ring fires from the enter' item closed by this
- Regression: `node --test content/video_engine/tests/kinetics/stopaction-stamp.test.mjs` then `node --test content/video_engine/tests/kinetics/chip.test.mjs`
- Expected RED: shockwave ink present before the contact; no seal border on a stamp-form chip; `ring_text` refused as unknown
- Validate: `node --test "content/video_engine/tests/kinetics/*.test.mjs"`, `python -m pytest content/video_engine/tests/test_the_stamp_arrival.py content/video_engine/tests/test_chip_stamp_arrival.py content/video_engine/tests/test_golden_frames.py -q` (each file its own process)
- Evidence: pending

### T1c: The seal's shockwave is gold; a bare prop's ring reads on any ground; the seal stays open (E99 s127 / s128)
- Status: done - lane B `cd0b630` (seal ring gold; dock-stamp ring by the measured ground: charcoal plate 1.04 -> 4.29:1, photo 1.27 -> 2.76:1; seal open tested; H: only s19's phone ring changes; open: the gold seal reads 1.55:1 on a mid-tone photo)
- Owner: implementation_luna (LANE B), then the parent's frame read
- Depends on: T1b committed (`50b2f85`)
- Harvest: the operator, 2026-09-24: "keep #E8B86D", "if reference is gold, make ours gold too" (s127); "i dont mind it being drawn over" (s128). T1b's finding: `RING_INK.ground` inks the ring charcoal on a dark non-ledger plate, where it nearly vanishes (`chip-stamp-seal-text`).
- Write set: the stamp's impact-ring ink (`stampRing` / `RING_INK` in `kinetics/stopaction.mjs` and/or `species/chip.mjs`, the engine region via `sync_kinetics.py --write`, and the engine's dock-stamp ring paint if separate); the matching compiler constant in `build_scene_timeline_f.py` if one exists; the stamp tests; the re-pinned goldens (on purpose).
- Acceptance: (1) a SEAL's shockwave is `CHIP_SEAL.GOLD` (#E8B86D), darkened on cream by the seal's own contrast law, timing unchanged; (2) a BARE PROP's stamp ring picks chalk or charcoal by the measured luminance of the ground under it (not by the world kind), so it holds contrast on cream, the charcoal ledger, a charcoal plate and a photo plate; (3) the seal has no fill (s128) - a test asserts the chart shows through; (4) a sheet: seal + bare prop at contact +0.05/+0.15/+0.30 s on cream, charcoal ledger, charcoal plate, a photo plate, with measured ring contrast; (5) byte-identical doors except ring pixels; goldens re-pinned on purpose only where a ring shows.
- Validate: node `tests/kinetics/*.test.mjs`, `test_stamp_is_a_seal`, `test_chip_stamp_arrival`, `test_the_stamp_arrival`, `test_golden_frames`, `test_kinetics_sync`, each in its own process.
- Evidence: pending

### T2: The schematic - a shape drawn with no data, carrying the narrative (was P69 T46)
- Status: done - lane B `3600ec5` (the schematic; no end tag - the title names the shape; digits refused unless sourced; golden schematic-hype-trough on the title-glow engine; a real series over it is P71 T39 / s125)
- Owner: implementation_luna (LANE B)
- Depends on: P70's base (T0), which carries T37b's bloom and T87's empty-plot gate; done P69 T36 `104af07` (the lit
  stretch), T50 `f63b569`. Nothing in P70.
- Harvest: v2 T7 "Schematic cycle: phase waves, a mania arc, the hype cycle, the debt cycle", n=5 (BUB 4:35; STK 1:42;
  HIS 03:26, 04:00-05:10; DOM 07:30, 11:00; BOOM 09:35 (G)). R6 "Cycle model". Blueprint `#12 page_builder:cycle`
  (`:266`). C9 was cleared by s109 (1) (`:294`).
- Use when (USE-WHEN `:565`, copied to the card): "a phase model carrying the narrative, named as a model: 'the world's
  art carrying the narrative' (s109 (1))". Don't: "axis values, figures it cannot source, or no mark on the page that it
  is 'a shape, not a series' (s109 (1))".
- Recall: docs_find "schematic" -> `docs/research/bravos-style/BRAVOS-USE-WHEN.md:563` "6. EXPLAINS a mechanism — T7 Schematic cycle (waves, a mania arc, the hype cycle): TYPE · MISSING · n=5 · C9 cleared by s109…" (4 hits, 0 capability rows)
- Recall: docs_find "cycle" -> no cycle page; the capability hits are `CAPABILITIES.md:35` (the inks) and `:269` (the opening gate)
- Recall: docs_find "shape without data" -> 4 manifest hits (docs 29, 35, 36, the SEO plan), 0 capability rows
- Recall: docs_find "hype cycle" -> 10 hits: `docs/research/bravos-chart-watch-2026-09-23/Jw8ykhoOVBQ.md:31` "TYPES — visual forms and encoding", `briefs/ANSWER-BRAVOS-IMAGE-PACK.md:1`, USE-WHEN `:563`
- Verdict: EXTEND the line page.
  - `ledger_page.VARIANTS` (`:73`) and `page_builder.json` have no `cycle`, and none is needed.
  - A schematic is a dense series the compiler GENERATES from a named closed form. The existing `dense-line` builder
    (`pick_builder` `:818`, engine `buildLedgerLine` `:10780`) draws it, so T36's `lit_stretch`, `span` (x-fraction
    edges) and `bracket` compose on it unchanged.
  - `evidence/ev-three-manias.html` is a table, not a shape (harvest v2 `:46`).
- Write set:
  - `content/video_engine/scripts/ledger_page.py` (new `SCHEMATIC_SHAPES`, `schematic_series`, the object-shape
    validation);
  - `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`buildLedgerLine` value suppression behind
    `pg.schematic`; new `lpSchematicTag`);
  - `content/video_engine/scripts/build_scene_timeline_f.py` (only if the plate grammar must pass the key);
  - `content/video_engine/scripts/measure_page_boxes.py` (a representative; parent-merged);
  - `content/video_engine/effects/cards/page_builder.json` (a `page_builder:line+schematic` card; parent-merged);
  - `content/video_engine/tests/test_build_effects_catalog.py` (exception list: `page_builder:line+schematic`, no
    committed beat plays it until HG1; parent-merged);
  - `content/video_engine/tests/test_schematic_page.py` (new);
  - the golden files for `schematic-hype-trough` (new), in `build_golden_sources.py`, `test_golden_frames.py` and
    `golden/{sources,frames}/`.
  - `page-boxes.v1.json` is generated by the parent at the merge and is never in the patch.
- Input evidence: none. A schematic needs no data (s109 (1)). The sentence is H row 12's "And that isn't the peak of
  inflated expectations. It's the trough already doing its job":
  - take: `peak of inflated expectations` 133.69-136.10, `trough already doing its job` 136.39-138.43;
  - SHOT-TABLE-H #6, 104.31-147.82, `world-internal-memo-v1`.

  The phase names are Gartner's hype-cycle terms, attributed on the page's source line ("Shape: Gartner's hype cycle - a
  schematic, no data").
- Constraints:
  - Byte-identical for every page without `schematic`; composes with `;readability=longform`.
  - The shapes are pure and deterministic (fixed N points, x in [0, 1]); no randomness.
  - The line blooms by T37b's default (s117), and T2 never touches the stroke.
  - The phase names take the series' ink by T37b's helper (s118) and sit at least at 59.08 stage px.
  - The page passes T87's empty-plot gate, because the line draws on the build.
- Acceptance:
  1. A line object may carry `schematic: {shape: "hype" | "waves" | "debt_cycle", phases: [{name, from, to}], n?}` in
     place of `series`. `schematic_series` generates ONE series from the named closed form. `series` or `pts` beside
     `schematic` is refused ("a schematic carries no data").
  2. The page writes NO values: no tick numbers on either axis and no end-tag value. A small `schematic` tag ("a shape,
     not a series") is on the page and in `page_boxes`.
  3. Each phase's `from` / `to` is an x-fraction that `span` and `lit_stretch` address. A `bracket` may name a lag in
     words. A bracket, figure or note on a schematic page whose text carries a digit is refused unless it names its `src`
     ("no figures it cannot source", s109 (1)). This is a truth rule, so it is hard.
  4. Seek-safe; one golden: the hype cycle with its phases named, and the light walking from the peak to the trough on
     "It's the trough".
- Exclusions: the shape meeting real data (P69 T46 (3)); A55's traced point; a `mania_arc` separate from `hype`.
- Stop conditions: suppressing values needs an edit to a tick helper shared with other builders (keep it behind
  `pg.schematic`, or stop and report); `lit_stretch` cannot address a generated series (report: that would be T36's
  defect).
- Regression: `python -m pytest content/video_engine/tests/test_schematic_page.py -q`
- Expected RED (probed read-only at c0836b8): `ledger_page.validate({... "schematic": {...}}, "line")` returns "no
  chartable values: expected bars[], series[].pts, panels[], or periods + series[].values".
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --write` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_schematic_page.py`, `test_ledger_page.py`, `test_lit_stretch.py`, `test_page_boxes.py`, `test_gate_motion_density.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `schematic-hype-trough.png` beside HIS `Jw8ykhoOVBQ` 04:24-04:30 ("peak of inflated
  expectations"):
  `ffmpeg -ss 264.5 -i "C:/Users/Snipe/Downloads/Outreach Program/docs/research/runs/bravos-watch/Jw8ykhoOVBQ/watch/download/video.mp4" -frames:v 1 $SP/p70-t2/frames/bravos-HIS-0424.png`,
  and beside STK `4AkB4c0tTfU` 01:42 (same path pattern, `-ss 102`).
- Return: the common lane-B return. CAPABILITIES row: "The schematic - a shape drawn with no data".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T3: The fill gauge - one share of one whole fills a capsule on its word (was P69 T51)
- Deviation (the parent, from the review 2026-09-24): acceptance 1's horizontal form `gauge:h` is REFUSED BY NAME, not drawn - M26 reads heights only; filed R26-319. The `whole` is named by the 100 hline's label (acceptance 3's second route); a `whole` key is not built. M26 cannot read long-form bars pages at all (pre-existing, R26-318); the gauge keeps its own rules visible so M26 reads it.
- Status: done - lane B `e43c3d8` (the fill gauge; reviewed MERGE WITH FIXES, fixes applied - two-bar pitch, ceiling stubs, TRACK_A 0.19 off Bravos's 1.741:1, page-boxes representative, figure-ink WARN; golden gauge-94 on the title-glow engine; no fill glow - awaits the operator)
- Owner: implementation_luna (LANE B), then reviewer (M26, a truth gate, must read the fill)
- Depends on: P70's base (T0), which carries T85's stagger and T37b's series ink; done P69 T50 `f63b569`, T10b
  `91de567` (`bar_style=soft`), T8 (`longform`). Nothing in P70.
- Harvest: v2 T34 "Fill gauge / meter (a capsule filling to a share)", PARTIAL, n=2 (BOOM 10:55 (G); D40 17:24 (G:
  two-thirds filled)).
- Use when (USE-WHEN `:483`): "one share of one whole ('two-thirds', '94 %')". Don't: "comparing shares (use bars)".
- Recall: docs_find "fill gauge" -> 0 hits
- Recall: docs_find "gauge" -> asset `content/video_engine/assets/props/cutouts/prop-treasury-yield-gauge-5pct-v1.png` "10Y Treasury Yield Speedometer" (a still, not this form)
- Recall: docs_find "progress" -> effects `page_builder:progress` "A progress-to-target reading on the ledger page (builder resolves through p…" (card: status `declared`, "no dedicated painter found")
- Recall: docs_find "share of one whole" -> `CAPABILITIES.md:107` treemap, `:123` remake, effects `page_builder:share` (the pie and donut, P69 T48)
- Recall: docs_find "capsule" -> `CAPABILITIES.md:219` "Badges are the key" (capsule pills: a look, not a fill)
- Verdict: EXTEND.
  - The `progress` variant already bounds a share (`PROGRESS_MAX` `:61`; `_validate_values` `:2336` "0..100 unless a
    denominator"). It builds as `story` and has no painter of its own.
  - A chart FORM is "how a page's chart is DRAWN, never what it says" (`ledger_page.py:838-:845`), so `gauge` joins
    `CHART_FORMS` (`:846`) beside `extruded_bar`.
  - The engine branches on `formOf(pg, "gauge")` inside `buildLedgerBars` (`:10336`), as it does for `extruded_bar`.
  - `chart_dock:shares` fills tracks on a CARD (`fillDock`), not on a page.
- Write set:
  - `content/video_engine/scripts/ledger_page.py` (`CHART_FORMS`, `FORM_BUILDERS`, `FORM_READS`, `form_error`, which
    learns the variant as an optional argument that the two existing forms ignore; `_validate_values` progress);
  - `content/video_engine/scripts/build_scene_timeline_f.py` (`page_form_geom`'s message and `page_form_spec`; `gauge[:h]`);
  - `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`buildLedgerBars` gauge branch);
  - `content/video_engine/scripts/measure_page_boxes.py` (a representative; parent-merged);
  - `content/video_engine/effects/cards/page_builder.json` (`page_builder:progress` gains its painter, status `wired`)
    and `content/video_engine/effects/cards/plate_option.json` (`plate_option:form` lists `gauge`), both parent-merged;
  - `content/video_engine/tests/test_build_effects_catalog.py` (exception list: `page_builder:progress`, now wired, no
    committed beat until HG1; parent-merged);
  - `content/video_engine/tests/test_fill_gauge.py` (new);
  - the golden files (`gauge-94`, new).
  - `page-boxes.v1.json` is generated by the parent, never in the patch.
- Input evidence: `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-capex-ocf-94-bars-v1.series.json`:
  - `bars [{value: 94, note: "94%"}]`, `domain [0, 100]`;
  - hline 100, "every dollar from operations", which names the whole;
  - research tier PLAUSIBLE (PIMCO Fig. 3).

  The page is compiled as the `progress` variant. The sentence is H row 17 (SHOT-TABLE-H #12, 324.62-338.44): take
  `ninety-four percent` 328.00, `Ninety-four. That` 332.21.
- Constraints:
  - Byte-identical for every page without `form=gauge`.
  - Composes with `;readability=longform` and `;bar_style=soft`: the capsule's ends take `LPBAR_SOFT.SHOULDER_PX`, and
    the hatch follows.
  - The value is written verbatim (`value_strings`), at least at 59.08 stage px, and in its bar's ink by T37b's helper
    (s118).
  - T85's stagger is untouched.
- Acceptance:
  1. `;form=gauge[:h]` is legal only on a `progress` page. On any other page it is refused by name through `form_error`
     ("a PROGRESS page - one share of one whole, drawn as a capsule"). That refusal is the only one, and it concerns
     the builder, not the bar count.
  2. One capsule, vertical by default. Its inner fill rises from empty to value / ceiling on the page's bar-grow clock,
     and the figure is written at the fill line as the fill lands.
  3. The capsule's full length IS the whole, and the whole is named on the page (a `whole` label, or the 100 hline's
     label). A gauge whose whole is unnamed is refused (E28: it reads at a glance or it is not on the page).
  4. M26: the probe's printed value and the drawn fill agree at every instant, checked through the probe. A value
     outside 0..ceiling is refused by the existing bound.
  5. A progress page with a second bar under `form=gauge` is a WARN with its numbers, pointing to bars (s106 advice;
     the USE-WHEN don't "comparing shares (use bars)"). It is never a refusal, and it draws one capsule per bar. The
     `plate_option:form` card's `does` is at most 240 characters.
- Exclusions: a gauge on a card (the `shares` card stays); the speedometer prop.
- Stop conditions: the probe's M26 cannot read a capsule's fill without a gate edit (report; the reviewer decides
  whether T3 carries the probe change).
- Regression: `python -m pytest content/video_engine/tests/test_fill_gauge.py -q`
- Expected RED (probed at c0836b8): `page_form_geom("gauge", ...)` raises "form 'gauge' is not one of
  extruded_bar|tilted_line (the two 2.5D chart forms; ...)".
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --write` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_fill_gauge.py`, `test_forms_by_honesty.py`, `test_ledger_page.py`, `test_bar_style.py`, `test_longform_profile.py`, `test_gate_motion_density.py`, `test_page_boxes.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `gauge-94.png` beside the bars page it would replace (the H door's #12 frame at
  332.21) and beside D40 `u70oUWgVoYU` 17:24:
  `ffmpeg -ss 1044 -i "C:/Users/Snipe/Downloads/Outreach Program/docs/research/runs/bravos-watch/u70oUWgVoYU/video_1080p.mp4" -frames:v 1 $SP/p70-t3/frames/bravos-D40-1724.png`
  (the Gemini timing is spot-checked against the 591 survey frames on disk).
- Return: the common lane-B return. CAPABILITIES row: "The fill gauge".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T4: Companion bars beside a held line - a recipe on the panels page, and the E79 WARN for one measure in two units (was P69 T52)
- Status: done - lane B `d0dd19b` (recipe candidate + the E79 one-measure-two-units WARN + `recipe_walk` names `panel_focus`; golden `companion-railway-yardstick`; H door identical. Acceptance 2 (the bars build IN VIEW) NOT met: a hidden panel builds while invisible - R26-315, strict xfail; the phone preset collapse R26-316; doors don't print the WARN R26-317)
- Owner: implementation_luna (LANE B)
- Depends on: P70's base (T0); done P69 T8b `7369f12`, T8c, T8d `91477ae`, T8e `eb58794` (the panels page, bars panels,
  first-reveal credit). Nothing in P70.
- Harvest: v2 T39 "Companion bars beside a held line", PARTIAL, n=2 (DOM 06:00-06:04; HIS 11:01). The harvest names the
  gap: "an in-page companion inset does not" exist (`:78`). That was written before T8b-T8d shipped.
- Use when (USE-WHEN `:287`): "the line stays as context while two magnitudes are set against each other beside it".
  Don't: "the bars cover the plot, ticks or source (E63, E45)".
- Recall: docs_find "companion bars" -> 0 hits; docs_find "companion" -> 4 hits, 0 capability rows
- Recall: docs_find "bars beside a line" -> `CAPABILITIES.md:124` "park: the chart makes room by one affine transform, WIRED"; effects `page_species:bracket`
- Recall: docs_find "share of one whole" -> `CAPABILITIES.md:229` "The ledger page draws PANELS, and focus moves among them on a word — WIRED - a panels object (2-4 charts...)" ("T8d (lane B): a panel may be BARS")
- Recall: `docs/portable/OPERATOR-RULINGS.md:2517` (E79 apply 1) "Panels of the same measure compute one scale across all panels - the standard."; `:1740` (E53 s4) "The honest zero, and one unit before two."
- Verdict: REUSE for the verb, plus one small EXTEND for the honesty rule.
  - **The verb is built.** The engine's `lpPanelStart` (`:12371`): "panel i's build starts on its turn ... or - hidden
    then - on the word that shows it". `ledger_page.py:3606-:3612`: "ONE active panel stands exactly where a
    single-chart page's chart stands". `panel_focus` roles are `active | receded | hidden` (`:3617`). The golden
    `panels-resize` already stands a page as one chart with panel 2 hidden. So the beat is a recipe and a golden.
  - **The honesty rule has a gap.** E79 and E53 s4 decide the scale: one measure takes one scale and one unit. The code
    groups panels by their unit STRING (`ledger_page.shared_panel_domains` `:1736`, `_same_unit_groups`), and
    `scale_warnings` (`:1568`) WARNs only on same-unit panels with different domains. A "%" line beside "¢" bars, which
    are one measure (a share of every dollar invested), silently draws two scales. T4 adds that WARN.
  - **Layout.** The computed `row` layout is used, not `free` boxes. `free` boxes are only checked for presence (compiler
    `:2035`, `:2070-:2073`), so a free box's clearance would be unmeasured.
  - **What a bars panel refuses.** The compiler's `PANEL_BARS_REFUSED` (`build_scene_timeline_f.py:2085`) refuses
    `bracket` on a bars panel, so a written multiple is a `figure` (allowed on bars panels, CAPABILITIES `:229`).
    ledger_page's own `PANEL_BARS_REFUSED` (`:1649`) is a list of bars-panel object FIELDS (`overflow`, `series`, ...)
    and does not refuse `bracket`.
- Write set: all existing unless marked new -
  - `content/video_engine/scripts/ledger_page.py`: `scale_warnings`, plus an optional panel key `measure` (the named
    quantity a panel draws). Two panels naming one `measure` in different units WARN: "E79 / E53 s4: <measure> is drawn
    in '%' and '¢' - one measure, one unit, one scale; re-express one panel". The WARN is s106 advice, never a refusal;
    a page without `measure` is unchanged;
  - `content/video_engine/effects/recipes/companion-bars-beside-the-held-line.json` (new);
  - `content/video_engine/tests/test_companion_bars.py` (new);
  - `content/video_engine/tests/test_build_effects_catalog.py` (the exception list: `page_species:panel_focus` LEAVES it,
    because the new recipe composes it; parent-merged);
  - the golden files (`companion-railway-yardstick`, new).
- Input evidence: the golden composes a panels object inside `build_golden_sources.py`, READ from two committed objects
  and never re-typed.
  - Panel 0 is `ev-capital-formation-v1.series.json`, the line, `measure: "share of all US private investment"`. Its
    railway `hlines` entry is dropped here, because the bars panel carries the 50 (a value is drawn once: E53 addendum
    `:1784`).
  - Panel 1 is `ev-rail-vs-yardstick-bars-v1.series.json` (`builder: bars`, the same `measure`), RE-EXPRESSED in the
    line's unit. Cents per dollar are percent, so 50 and 28 carry over unchanged, the notes read "~50%" / "28%", and the
    source line says so (our arithmetic layer, E77). Its `domain` and `overflow: burst` stay off.
  - One unit gives E79's shared scale.
  - The sentence is H row 14 (SHOT-TABLE-H #8, 162.60-195.82): take `twenty-eight, the most` 180.93, `railways took
    roughly half` 185.16.
- Constraints: byte-identical for every page without `measure`; the recipe's `does` is at most 240 characters; members
  are card ids (`page_builder:line`, `page_species:panel_focus`, `page_species:figure` optional); `window_s` covers the
  beat; every label at least the s90 phone floor, 59.08 stage px (`ledger_page.CARD_TYPE_PX` `:4188`); the bars and names
  take their series' ink by T37b's helper (s118), never a local colour.
- Acceptance:
  1. The page stands as the line alone (`panel_focus` at the page's `at`, roles `[active, hidden]`).
  2. On "railways took roughly half", a `row` focus state makes both panels active. The bars build on that word, on the
     line's one scale.
  3. The line keeps its ink, its bloom (T37b) and its idle.
  4. On the leave word the focus returns to `[active, hidden]`, and the line re-grows by T8c's resize.
  5. The golden, compiled WITHOUT the re-expression ("¢" bars, `measure` named on both panels), prints the new E79 /
     E53 s4 WARN. With it, the golden prints none.
  6. `recipe_walk` walks the recipe in order inside `window_s` at `proof.t`.
- Exclusions: a companion over a non-panels page (the park plus a card is `recipe:chart-parks-for-their-claim`, HAVE); a
  unit-equivalence table (the author names the measure); any engine change.
- Stop conditions: the `row` state crowds the line below its phone floor (report the measured sizes; the parent opens a
  fix slice for a measured free box); the recipe cannot be expressed without an engine change (stop, and report the
  defect with its frame).
- Regression: `python -m pytest content/video_engine/tests/test_companion_bars.py -q`
- Expected RED: the recipe file and the golden are absent; `scale_warnings` is silent for one `measure` in "%" and "¢".
  The mechanism assertions (panel 1 has no ink before its word) are EXPECTED GREEN on the base, and that green is the
  REUSE proof.
- Validate: each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_companion_bars.py`, `test_ledger_panels.py`, `test_ledger_page.py`, `test_recipe_walk.py`, `test_recipe_use_when.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: a golden is never served as a scene (s60). The parent reads `companion-railway-yardstick.png`
  beside DOM `PWMhM2_dj3s` 06:02
  (`ffmpeg -ss 362 -i ".../docs/research/runs/bravos-watch/PWMhM2_dj3s/watch/download/video.mp4" -frames:v 1 $SP/p70-t4/frames/bravos-DOM-0602.png`)
  and HIS 11:01 (`-ss 661`, the HIS path). The beat played with the take is P70-HG1's (T12).
- Return: the common lane-B return, with door identity, since `ledger_page.py` changes. CAPABILITIES row: a line on `:229`
  ("the companion recipe; one measure, one unit").
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T5: The decomposition brace - one total braced into its named parts, on a stacked bar (was P69 T58)
- Status: done - lane B 4a9a10e (the decomposition brace; the key hand-over through lpSegPaint)
- Owner: implementation_luna (LANE B)
- Depends on: P70's base (T0); done P69 T50 `f63b569` (a bracket on bars), T64 `c0836b8` (`segments`). Integrated
  after wave 1.
- Harvest: v2 T24 "Decomposition brace", MISSING, n=1 (RST 5:40). v1 `BRAVOS-VOCABULARY-HARVEST.md:63`: "'Long-Term
  Interest Rates' braces two stacked components (short-term rate + term premium)".
- Use when (USE-WHEN `:465`): "one quantity is the sum of named parts ('the rate = policy + term premium')". Don't: "the
  parts are not additive".
- Recall: docs_find "brace" -> 3 hits, 0 capability rows (`docs/research/bravos-chart-watch-2026-09-23/nB1eXWQlW58.md:1`, a rigging blueprint)
- Recall: docs_find "decomposition" -> `CAPABILITIES.md:125` "The morph: the object becomes the chart" (ARAP polar decomposition, unrelated)
- Recall: docs_find "parts of a whole" -> `CAPABILITIES.md:107` "The TREEMAP page with X marks - the census exception"; effects `page_builder:treemap`
- Recall: effects `page_species:bracket` "The hand draws a measured span between two data, the number as its label - on a line, or on a bars page between two bar tops, beside the bars' sides (R26-272)."
- Verdict: EXTEND.
  - `BRACKET_FORMS = ("span", "bar")` (`:456`) is already a form switch, validated at `:2231`.
  - The engine's bracket block in `buildPerform` (`:13854`, with `form === "bar"` in `geomOf` / `mk`) and `paintBracket`
    (`:14109`) draw the span.
  - `brace` is the same span with a curly path and notches. The curve is GENERATED geometry, so it is drawn as clothoid
    segments (`kinetics/clothoid.mjs` `clothoid` / `clothoidPath`) under doc 42 §42.4's law (`42-*.md:102`), never a
    cubic Bezier.
  - T64's `segments` already REFUSE a stack that does not sum to its written total, so the additivity check exists on a
    stacked bar.
- Write set:
  - `content/video_engine/scripts/build_scene_timeline_f.py` (`BRACKET_FORMS`, the bracket branch, a new
    `check_brace(page, species)` called beside `check_members` in `main()`);
  - `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the bracket block of `buildPerform`, `paintBracket`);
  - `content/video_engine/effects/cards/page_species.json` (`page_species:bracket` option `brace`);
  - `content/video_engine/tests/test_decomposition_brace.py` (new);
  - the golden files (`brace-funding`, new).
- Input evidence: T64's `stacked_funding_series()` (`build_golden_sources.py`), which READS
  `steel-and-paper/evidence/objects/ev-capex-funding-v1.series.json`. The Q1 2026 bar is the builders' cash from
  operations, stacked into cash capex and what was left.

  The sentence is H row 17's "That is not a company investing its surplus. That is a company spending all of it"
  (SHOT-TABLE-H #12): take `investing its surplus` 333.45-335.60 names "Left over", and `spending all of it` 336.32
  names "Cash capex".
- Constraints:
  - Byte-identical for every bracket without `form: "brace"` (goldens `tiers-two`, `span-decade` and the bars-bracket
    test).
  - The same clock as the bracket: `BRACKET_DRAW` 0.5 of dur, ticks by the spring, label by the glyph write.
  - `longform` type. The label and part names are at least 59.08 stage px, and the part names take their segment's ink
    by T37b's helper (s118).
- Acceptance:
  1. `bracket {form: "brace", bar: i, at, dur, label, sub?, parts_at?}` on a bars page whose bar i carries `segments`:
     - a curly brace stands beside the bar's side from zero to its top, with its cusp toward the label (the whole's
       name);
     - there is one notch at each segment boundary;
     - each part's NAME is written beside its own segment's span on its word (`parts_at`, else 0.4 s apart after the
       brace draws);
     - the part figures stay the segments' own and are not re-written.
  2. A figure in `label` must equal the bar's written total, and a mismatch is refused as untrue.
  3. `form: "brace"` on a bar with no segments is refused by name ("a brace divides a whole into its parts ... T64's
     `segments`"). A brace given `from`/`to` is refused, pointing to the span form.
  4. It follows the page's park and states as a bracket does (R26-28).
- Exclusions: a brace on flow nodes, chips or figures (v1 `#13`); a brace over several bars.
- Stop conditions: `buildPerform` cannot read a segment's boundaries without reaching into `lpSegBuild` (`:10178`). In
  that case report the geometry it needs. T5 does not edit `lpSegBuild`, which is T64's.
- Regression: `python -m pytest content/video_engine/tests/test_decomposition_brace.py -q`
- Expected RED: a brace entry returns two errors, "bracket: 'from' must be a non-negative integer datum index" (the
  `from`/`to` check, `:2220-:2222`) and "bracket: form must be one of span|bar". The fix branches on `form == "brace"`
  BEFORE the `from`/`to` requirement, because a brace names `bar`, not two data.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_decomposition_brace.py`, `test_forms_by_honesty.py`, `test_stacked_combo.py`, `test_chart_transitions.py`, `test_build_effects_catalog.py` (no exception-list line: an option on `page_species:bracket`), `test_golden_frames.py`, `test_effects_catalog_drift.py`, then `node --test content/video_engine/tests/kinetics/clothoid.test.mjs`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `brace-funding.png` beside RST `_rwFYNlKtEc` 05:40
  (`ffmpeg -ss 340 -i "C:/Users/Snipe/Downloads/Outreach Program/content/video_engine/sources/reference_analyses/pivot-_rwFYNlKtEc/download/video.mp4" -frames:v 1 $SP/p70-t5/frames/bravos-RST-0540.png`),
  knowing that Bravos braces a DIAGRAM's components there and ours braces a stacked bar.
- Return: the common lane-B return. CAPABILITIES row: an amendment of the bracket row ("form: brace").
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T6: The equation row - the inputs, the relation and the signed result, in spoken order (was P69 T56)
- Amendment (the parent, from the review 2026-09-25): the truth rule computes from each term's WRITTEN text (not `value`); units are a closed list - `%` / `pts` count x0.01, + and - need one unit across the row, x and / give the derived unit, B/M/K/T scale; `tier: CONFIRMED|PLAUSIBLE` needs a `src` naming an existing evidence object (only `scenario` stands alone); a negative result's red comes from its text's sign; optional per-term and result `label` captions (a row with none WARNs, E28); operators in a sans. The page dim behind the row is P71 T15's.
- Status: done - lane B 8a9fc02 (the equation row, computed from the written text)
- Owner: implementation_luna (LANE B), then reviewer (the gate's `SPECIES_EVENTS`, the arithmetic truth rule)
- Depends on: P70's base (T0); done P69 T50. Integrated after wave 1.
- Harvest: v2 T38 "Equation row: inputs, relation, signed result", MISSING, n=1 (DOM 09:30-09:39: 3 %, 5 %, "Real Yield"
  -2 %). A60 "Equation built in spoken order". R25.
- Use when (USE-WHEN `:595` / `:673`): "the arithmetic IS the claim ('real yield = coupon − inflation')"; "a narrated sum
  or difference, each input spoken before the result". Don't: "the inputs are unsourced, or the result is not spoken".
- Recall: docs_find "equation" -> 20+ hits, all research mathematics (`complete_research_evidence_bundle/09_...md:349` "Re-Parenting Invariant Matrix Equation") and `46-REFERENCE-RHYTHM.md:79-119` (the script spine); 0 capability rows
- Recall: docs_find "relation" -> research only (Flash & Hogan, `ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md:74`); 0 capability rows
- Recall: docs_find "signed result" -> `BACKLOG-HISTORY-2026-09.md:251`; 0 capability rows
- Verdict: NEW stage species `species/equation.mjs`, registered in `SPECIES_PAINTERS` (CAPABILITIES `:99`, the module
  rule).
  - It reuses `species/figure.mjs` `figureGlyph` (`:149`, the hand's glyph-by-glyph write) and `kinetics/spring.mjs`
    `springPop` for the operators.
  - Nothing existing lays out a row of terms or computes a result: `compare` morphs a quoted figure into a felt one, and
    `figure` writes one number at a datum.
- Write set:
  - `content/video_engine/scripts/species/equation.mjs` (new), plus its region inserted immediately after the `freeze`
    region's `KINETICS:END` (`:19363` at c0836b8), then `sync_kinetics.py --write`;
  - `content/video_engine/scripts/build_scene_timeline_f.py` (a new `_validate_equation`; its `_validate_entry`
    dispatch line, `SPECIES_KINDS` and `SPECIES_WHEN` are parent-merged);
  - `content/video_engine/scripts/gate_motion_density.py` (`SPECIES_EVENTS["equation"]` = each term's `at`, the result's
    `at`; parent-merged);
  - `content/video_engine/scripts/lint_species_choice.py` (`ACT_SPECIES["EXPLAINS"]`, parent-merged).
    `SPECIES-BY-SENTENCE.md` is generated by the parent;
  - `content/video_engine/effects/cards/species.json` (`species:equation`, `when: null`, parent-merged);
  - `content/video_engine/tests/test_build_effects_catalog.py` (exception list: `species:equation`, until R25's recipe
    (P69 T44) composes it; parent-merged);
  - `content/video_engine/tests/kinetics/equation.test.mjs` (new), `content/video_engine/tests/test_equation_row.py`
    (new), `content/video_engine/tests/test_kinetics_sync.py` (`SPECIES`);
  - the golden files (`equation-halving`, new).
- Input evidence: H row 18's "Run the arithmetic. At a fifth of the index, if the AI names fall by half, that erases ten
  percent of 'the market'", over `ev-index-concentration-bars-v1.series.json` (SHOT-TABLE-H #15, 384.12-408.60). The
  terms and their times on the take:

  | term | text | cue word | take time | source |
  |---|---|---|---|---|
  | input | "20%" | `a fifth` | 400.18 | `src: ev-index-concentration-bars-v1`, PLAUSIBLE |
  | operator | "×" | | | |
  | input | "−½" | `fall by half` | 402.38 | `tier: "scenario"`, the sentence's own "if" |
  | result | "−10%" | `erases ten percent` | 403.62 | computed |
- Constraints: a pure function of t; every term, operator and result at least 59.08 stage px (the s90 floor); E28 (a negative result is written
  with its minus and in the page's `neg` token); byte-identical elsewhere. The new-species checklist is `SPECIES_WHEN`,
  `ACT_SPECIES`, `SPECIES_EVENTS`, `test_kinetics_sync.SPECIES` and the SPECIES-BY-SENTENCE regen. It is a stage
  species, so it is not in `PAGE_SPECIES_KINDS` or `PLOT_MARKS`.
- Acceptance:
  1. `{kind: "equation", at, dur, target: region, terms: [{text, value, at, src? | tier?}] (2-3), ops: [x | − | + | ÷]
     (one fewer), result: {text, value, at}}`. Each term lands on its own word, strictly in order with the result last
     (A60), written by the hand; the operators spring in between, and "=" lands with the result.
  2. The compiler COMPUTES the result left to right. A written result that disagrees beyond its text's precision is
     refused (untrue). A term whose `text` does not parse to its `value` is refused. Every term names `src` (an evidence
     object) or `tier` (CONFIRMED | PLAUSIBLE | scenario). A result with no `at` is refused (the don't).
  3. Seek-safe; one golden; H door byte-identical.
- Exclusions: a term docking as the page's figure; the formula recipe R25 (P69 T44); more than three inputs.
- Stop conditions: `figureGlyph` cannot be imported by a stage module without moving `figure.mjs`'s region (report; do
  not move it).
- Regression: `python -m pytest content/video_engine/tests/test_equation_row.py -q`
- Expected RED (probed at c0836b8): `validate_species` returns "kind must be one of punch|callout|...|member" for
  `kind: "equation"`.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `node --test content/video_engine/tests/kinetics/equation.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/lint_species_choice.py --when --check-doc` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_equation_row.py`, `test_kinetics_sync.py`, `test_lint_species_choice.py`, `test_gate_motion_density.py`, `test_targeted_species.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, and each `content/video_engine/tests/test_authoring_*.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `equation-halving.png` beside DOM `PWMhM2_dj3s` 09:35
  (`ffmpeg -ss 575 -i ".../bravos-watch/PWMhM2_dj3s/watch/download/video.mp4" -frames:v 1 $SP/p70-t6/frames/bravos-DOM-0935.png`)
  and beside the halving compare it precedes (golden `bar-value-morph`).
- Return: the common lane-B return. CAPABILITIES row: "The equation row".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T7: The balance scale, and the balance tips (was P69 T59)
- Status: done - lane B 4950a91 (the balance scale; placement advised, truth refused)
- Owner: implementation_luna (LANE B), then reviewer (the gate's `SPECIES_EVENTS`, the no-figures truth rule)
- Depends on: P70's base (T0); done P69 T6b `041e2ff` (the hatch), T26d `5c6871c`. Integrated after T6 (they share only
  parent-merged registry lines).
- Harvest: v2 T27 "Balance scale (a tip, or a flag / scale / flag trio)", MISSING, n=2 (CHN 19:10; JPN 06:41). A40 "The
  balance tips", n=1 (CHN 19:10).
- Use when (USE-WHEN `:589` / `:643`): "two forces weighed ('threat' vs 'opportunity', US vs Japan)"; "two forces are
  weighed and the sentence says which way it tips". Don'ts: "one side is unnamed or unweighed"; `:646` "a real balance
  of figures (use two bars)".
- Recall: docs_find "balance" -> `CAPABILITIES.md:216` "A bar is narrow" (unrelated), `48-THE-FIGURE-AND-THE-GROUND.md:39` "48.2 Balance — why a gesturing figure must move its hips"; 0 capability rows for a balance
- Recall: docs_find "balance scale" -> research only (`briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md:120`); 0 capability rows
- Recall: docs_find "tips" -> `39-EVIDENCE-CHART-SYSTEM.md:12`, `patterns/CRAFT-DEVICES.md`; 0 capability rows. docs_find "scale" -> rescale and park rows only
- Verdict: NEW stage species `species/balance.mjs`. It builds on:
  - `kinetics/spring.mjs` (the closed form, the beam's settle and tip);
  - `kinetics/clothoid.mjs` (`clothoid`, `clothoidPath`) for every GENERATED arm and hanger. This is doc 42 §42.4's
    curve law (`42-*.md:102`; engine `:442-:444`: "Applies to geometry the engine GENERATES - arrows, balance arms,
    connectors, axes");
  - `kinetics/stopaction.mjs` (`MASS` `:45`, `landXf` `:227`) for a pan's load;
  - `species/chip.mjs` `chipLand` / `chipGeometry` for a pan's named load;
  - `PROP_SHADOW` (`:98`) for the resting hatch.

  The engine's `propHatchLines` (`:19536`) is inline and is not in the species ctx.
- Write set: all existing unless marked new -
  - `content/video_engine/scripts/species/balance.mjs` (new), plus its region inserted immediately before the `ring`
    region's BEGIN (`:18557` at c0836b8);
  - the engine's `paintSpecies` painter-ctx object (to expose `propHatchLines`, only if used);
  - `content/video_engine/scripts/build_scene_timeline_f.py` (a new `_validate_balance`; its `_validate_entry` dispatch
    line and the registries are parent-merged);
  - `content/video_engine/scripts/gate_motion_density.py` (`SPECIES_EVENTS["balance"]`, parent-merged);
  - `content/video_engine/effects/cards/species.json` (`species:balance`, `when: null`, parent-merged);
  - `content/video_engine/tests/test_build_effects_catalog.py` (exception list: `species:balance`, no committed beat
    plays it yet; parent-merged);
  - `content/video_engine/tests/kinetics/balance.test.mjs` (new), `content/video_engine/tests/test_balance_scale.py`
    (new);
  - the golden files (`balance-level`, new).
  - The private test bed `$SP/p70-t7/testbed/` (never committed).
- Input evidence:
  - **Level (the golden, a real H beat):** H row 19 (SHOT-TABLE-H #18, 431.01-463.95, `ev-two-clocks-bars-v1` page).
    The take: `the moat` 452.65, `the paper stacked` 456.56, `Both are true at once` 460.29.
  - **The tip (a private test-bed beat, s60):** no H sentence tips two unquantified forces. Row 16's "the bills got
    bigger than the cash" is a real balance of figures, so it stays two bars (USE-WHEN `:646`; P69 T59 (3)). The tip is
    therefore proved on a private test-bed beat built from Bravos CHN 19:10.2-19:14.2 (shots 113-114, "not just threats
    ... opportunities"), timed off that video's own VTT (`bravos-china-just-triggered-a-new-world-order/claude-watch/download/video.en.vtt`,
    main checkout). It is a reference bed in the scratchpad only: never committed, never in a door, never a golden.
- Constraints: a pure function of t; byte-identical elsewhere; our hand (charcoal on cream, chalk on charcoal); every
  label at least 59.08 stage px (the s90 floor, `ledger_page.CARD_TYPE_PX` `:4188`); the new-species checklist as in T6.
- Acceptance:
  1. `{kind: "balance", at, dur, target: region, left: {label, icon? | prop?, at}, right: {...}, tip?: {at, to: left |
     right}}`. The beam and fulcrum draw on `at`, with the arms and hangers as clothoid segments (§42.4). Each pan's load
     lands on its word. With one pan loaded, the beam leans to it on the spring. With both loaded, it settles LEVEL.
  2. A40: on `tip.at` the beam tips to `TIP_DEG` toward `tip.to` on an underdamped spring with ONE visible overshoot
     (the second is under 1°). The pans hang plumb. It is a mass, never a fade. Proved by the kinetics test and the
     test-bed strip.
  3. Truth: a label with a digit is refused by name, pointing to two bars. An unnamed side is refused.
  4. The base rests on T6b's hatch if the ctx exposes it. Otherwise it has no shadow, and the reviewer decides.
  5. Seek-safe; the one golden, `balance-level`; H door byte-identical.
- Exclusions: the flag / scale / flag trio (JPN); numeric weights; a balance on a ledger page's plot; a tip on row 16.
- Stop conditions: exposing `propHatchLines` changes any existing painter's bytes (drop the hatch, and report).
- Regression: `python -m pytest content/video_engine/tests/test_balance_scale.py -q`
- Expected RED: `validate_species` returns "kind must be one of ..." for `kind: "balance"`.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `node --test content/video_engine/tests/kinetics/balance.test.mjs` then `node --test content/video_engine/tests/kinetics/clothoid.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_balance_scale.py`, `test_kinetics_sync.py`, `test_lint_species_choice.py`, `test_gate_motion_density.py`, `test_targeted_species.py`, `test_prop_shadow.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, and each `test_authoring_*.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `balance-level.png` and the test-bed tip strip (`$SP/p70-t7/frames/tip-strip.png`:
  tip.at +0.00 / +0.15 / +0.35 / +0.60 / +1.20 s) beside CHN shots 113-114,
  `content/video_engine/sources/reference_analyses/bravos-china-just-triggered-a-new-world-order/claude-watch/shots/shot_113_t19-10.8.jpg`
  and `shot_114_t19-14.8.jpg` in the main checkout (Threat vs Opportunity tipping), and JPN 06:41
  (`ffmpeg -ss 401 -i ".../bravos-watch/nB1eXWQlW58/watch/download/video.mp4" -frames:v 1 $SP/p70-t7/frames/bravos-JPN-0641.png`).
- Return: the common lane-B return. CAPABILITIES row: "The balance scale".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T8: The rig - a prop arrives in a puff (`arrive: poof`), its sound, the paper prop's claim, and the candidate `recipe:the-rig` (was P69 T69)
- Status: done - lane B ad55411: `arrive: poof` (Bravos-fitted), its cue at E81's start (9 dB under, `audio.e81_gain`), the ring rule = the stamped prop's (no refusal, s106), card `arrival:poof`, recipe `the-rig` (candidate), golden `prop-poof`; the paper = claim `review/claims/p70-t8-the-paper-v1` (2 clean cutouts, QUARANTINED for P70-HG1)
- Owner: implementation_luna (LANE B for the arrival; the claim in lane A), then reviewer (an arrival: the gate, the
  sound)
- Depends on: P70 T1 merged (it shares the gate's `_landings` / `_arrivals`); done P69 T26d, T6b, T84 `e416df5` (the
  binder retimes a bound landing cue to its compiled contact).
- Harvest: v2 A35 "Poof arrival under a load", MISSING, n=1 (BUB 11:58). R16 "The rig", PARTIAL.
- Use when (USE-WHEN `:631` / `:715`): "a metaphor prop (the rig lane)"; "a metaphor carries a load (the risk sitting on a
  thin support)". Don'ts: "the prop stands in for a figure (s106 ...)"; "a data claim".
- Recall: docs_find "poof" -> 0 hits
- Recall: docs_find "puff" -> `docs/research/motion/WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md:279` "3. Dust Puff Dispersal Timing (Whitaker & Halas 1981, p. 74)" ("Requires not less than 12 frames at 24 fps (500 ms) to dissipate")
- Recall: docs_find "metaphor prop" -> `content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/REPORT.md:136` "Technique 3: The Circus Elephant Metaphor Prop (Shot #59–#60 & Shot #82–#83)"
- Recall: docs_find "rig" -> `CAPABILITIES.md:184` / `:189` (character rigs, unrelated); 0 rows for a metaphor rig
- Recall: `docs/portable/OPERATOR-RULINGS.md:1175` (E36) "The Flow driver is standing-approved; images are free"; `:2542` (E81) "foley and accents begin 8-10 dB under the voice in every video"
- Verdict: NEW arrival.
  - `ARRIVALS = ("spring", "throw", "land", "stamp")` (`:106`).
  - The dock painter's arrival branch is in `render()` (`:20281`).
  - `species:steam` (`paintSpecies` `:19410`) is wisps off a region ("Never a particle system").
  - `melt.mjs splashDrops` (`:1022`) is a liquid splat. Neither is a puff.
  - A pure `poofXf` joins `kinetics/stopaction.mjs`, where every arrival's math lives.
  - The binder only pairs a cue to an arrival in `authoring/audio.WEIGHTED_ARRIVALS` (`:137`), and `arrival_mass`
    (`:180`) defaults a non-stamp arrival to `paper`. So the poof's sound needs both.
- Write set: all existing unless marked new -
  - `content/video_engine/scripts/kinetics/stopaction.mjs` (new export `poofXf`, `POOF` dials);
  - the engine's `render()` dock-arrival branch, and the `stopaction` region via `sync_kinetics.py --write`;
  - `content/video_engine/scripts/build_scene_timeline_f.py` (`ARRIVALS`, `PLATE_ARRIVALS_REFUSED`, `dock_opts`);
  - `content/video_engine/scripts/gate_motion_density.py` (`_landings`, `_arrivals`);
  - `content/video_engine/scripts/authoring/audio.py`:
    - `WEIGHTED_ARRIVALS` gains `"poof"`;
    - a `POOF` constant;
    - `landing_contact` gives a poof's contact as `t_enter + POOF.EJECT_S`, read from the module as `stamp_contact_s`
      is;
    - `arrival_mass` gives a poof its own `mass`, else `paper`, which is explicit and tested rather than the default
      falling through;
  - `content/video_engine/effects/cards/arrival.json` (`arrival:poof`, parent-merged);
  - `content/video_engine/effects/recipes/the-rig.json` (new, `candidate`; it composes `arrival:poof`, so no
    exception-list line);
  - `content/video_engine/tests/kinetics/stopaction.test.mjs`;
  - `content/video_engine/tests/test_poof_arrival.py` (new), and `test_landing_sound_follows_the_landing.py` (a poof
    case);
  - the golden files (`prop-poof`, new).
  - **The claim (lane A):** `review/claims/<claim-id>/**` (the quarantined delivery and its WORK-ORDER.md) and the
    committed claim record only, never the image (generated images stay out of git).
- Input evidence:
  - H row 17's "The steel kept building. The paper just got heavier." (SHOT-TABLE-H #13, 338.44-363.38,
    `world-internal-memo-v1` with `dock-h-leases-record`; take `The steel kept building` 350.70, `The paper just got
    heavier` 352.30).
  - The support is `prop-memory-steel-ibeam-v1` (props catalogue).
  - **The load, "the paper", is ordered.** The catalogue has none, and E36 says images are free. The slice opens an image
    claim by the headless claim flow (`docs/runbooks/HEADLESS_CLAIM_RESUME.md`):
    1. `open_claim(...)` (`content/video_engine/src/services/generation_claim.py`) with a WORK-ORDER for a woodblock
       "stack of bond certificates" prop cutout in the props catalogue's style (text only if named and verified, s113:
       "BOND" or none);
    2. `codex exec` GPT Image, headless;
    3. `claim-resume`.

    The output stays in quarantine. This is not Flow, and it needs no consent. Only the operator's approval brings it
    out of quarantine, at P70-HG1.
- Constraints:
  - Byte-identical for docks without `poof`.
  - A poof never lands on a card or a page pill (`PLATE_ARRIVALS_REFUSED`).
  - The puff disperses over at least 12 frames at 24 fps (0.5 s; W&H p. 74) and ejects over 1-2 frames (`EJECT_S`).
  - Seeded, deterministic, a pure function of t.
  - Callout labels are at least 59.08 stage px (the s90 floor).
- Acceptance:
  1. `arrive: "poof"` on a prop dock: the prop appears at its authored `place` inside a ring of seeded puffs. The puffs
     eject radially and disperse, while the prop springs from 0.6 to 1 (`springPop`).
  2. The gate counts the poof's contact as an arrival, and `recipe_walk` emits `arrival:poof`.
  3. **The sound.** The poof's cue is slot `landing <n> (poof, paper)`, variant A `fs-whoosh-1-706679.mp3` (on disk and
     sourced in `steel-and-paper/sound/SOURCES.md`), at the landing gain the shipped plans use (0.12).
     - Its level is measured against the voice and written on the cue: 8-10 dB under it is the start (E81 apply 1), and a
       departure carries its reason on the cue.
     - `fired` pairs it, and T84's binder retimes it to the poof's contact (s116); a test proves a cue authored 0.3 s
       off moves onto the contact.
  4. A poof dock's label carrying a figure is refused (the prop never stands for a figure; s106's truth rule).
  5. `recipe:the-rig` (candidate): a support prop lands or stamps, a load poofs onto its top (`place` above the
     support's box), and callouts name each part. Props come from the catalogue only. The recipe's proof waits on the
     paper prop's approval at P70-HG1.
  6. One golden: `prop-poof` (the I-beam poofs in on "The steel kept building").
- Exclusions: a camera pull on a poof; a rig on a data page as a figure; putting the quarantined prop into the catalogue
  before the operator's approval.
- Stop conditions: the claim fails twice (the golden proves `poof` alone, the recipe stays `candidate`, and the parent
  is told); a poof needs a change to `STOP` or `STAMP_ARRIVAL` (report).
- Regression: `python -m pytest content/video_engine/tests/test_poof_arrival.py -q`
- Expected RED (probed at c0836b8): `dock_opts({"arrive": "poof"})` raises "dock: arrive 'poof' is not one of
  spring|throw|land|stamp"; `audio.landing_contact(t, "poof", dials)` returns the land formula, not the poof's contact.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `node --test content/video_engine/tests/kinetics/stopaction.test.mjs` then `node --test content/video_engine/tests/kinetics/stopaction-stamp.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then (in the scratch tree only) `python content/video_engine/scripts/build_effects_catalog.py --write` then `--check`, then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_poof_arrival.py`, `test_the_stamp_arrival.py`, `test_prop_free_placement.py`, `test_prop_shadow.py`, `test_landing_sound_follows_the_landing.py`, `test_authoring_kit.py`, `test_gate_motion_density.py`, `test_recipe_walk.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, and each `test_authoring_*.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `prop-poof.png` and a 5-instant strip (enter +0.00 / +0.04 / +0.20 / +0.50 /
  +0.70 s) beside BUB `frame_0061.jpg` (11:58.2-12:10.2, "an elephant on a ball on a tightrope"),
  `content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/frames/frame_0061.jpg` in
  the main checkout, and the claim's contact sheet.
- Return: the common lane-B return, plus the claim id and its delivery path. CAPABILITIES row: "The poof arrival".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T9: The chapter pill held over an act (was P69 T61, A34)
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (`render()`, the room, the gate's chrome)
- Depends on: P70 T8 merged (both own hunks of `render()`); P70's base, which carries T65 (ring targets, which T9's
  `ring_obstacles` extra must not change); done P69 T26f `1100c0b`, T10 (the key rail's pill).
- Harvest: v2 A34 "Chapter pill held over an act's charts", MISSING, n=1 (BUB 12:22). §6 (`:274`): "Keep it for rows 13 /
  18 / 23 only if the operator wants act markers".
- Use when (USE-WHEN `:969`): "a long form has named acts and each chart should say which act it is in". Don't: "a short
  with no acts".
- Recall: docs_find "chapter pill" -> 0 hits; docs_find "chapter" -> 20+ doc hits (from `01-PRD.md`), 0 capability rows
- Recall: docs_find "act pill" -> `CAPABILITIES.md:219` "Badges are the key — WIRED - the long form's key rail." (the pill's look), `:78`, `:79`, `:110`; effects `plate_option:arrive`. None is a held act marker
- Verdict: NEW.
  - The timeline's top-level keys are `captions`, `caption_pages`, `caption_modes`, `sound`, `evidence` and `scenes`
    (read off `build-h/steel-and-paper-h.timeline.json`), so there is no chrome that crosses scenes.
  - T26f's `chrome` (`CHROME_ELEMENTS` `:1240`) is per-row camera chrome.
  - `recipe:held-dock-across-the-cut` holds a DOCK, not chrome.
  - The pill's look reuses the key rail (`longform_key`, CAPABILITIES `:219`: "white capsule pills").
- Write set:
  - `content/video_engine/scripts/build_scene_timeline_f.py` (a new `_validate_chapter`, the lift into the timeline's
    `chapters` in `main()`, the chapter's box as `ring_obstacles` `extra`; the dispatch line, `SPECIES_KINDS` and
    `SPECIES_WHEN` are parent-merged);
  - the engine (a new `paintChapters`, and one call in `render()` after `paintSpecies`);
  - `content/video_engine/scripts/probe.py` (the pill read as chrome), only if M25 / M28 cannot see it otherwise;
  - `content/video_engine/scripts/gate_motion_density.py` (`SPECIES_EVENTS["chapter"]`) and `lint_species_choice.py`
    (`ACT_SPECIES["SETS"]`), both parent-merged. `SPECIES-BY-SENTENCE.md` is generated by the parent;
  - `content/video_engine/effects/cards/species.json` (`species:chapter`, `when: null`, parent-merged);
  - `content/video_engine/tests/test_build_effects_catalog.py` (exception list: `species:chapter`, until the operator
    adopts act markers; parent-merged);
  - `content/video_engine/tests/test_chapter_pill.py` (new);
  - the golden files (`chapter-held`, new).
- Input evidence: the treatment's own act names (REBUILD-TREATMENT-H.md `:78`: "18 | 6:04-7:13 P20 the turn ... RESET 2
  on 'It was never the AI stocks'"). The chapter "The turn" lands on `It was never the AI stocks` (363.38; SHOT-TABLE-H
  #14 starts at 363.38) and holds across the cut into #15 (384.12, the index-concentration page). The text is authored
  and verified against the treatment (s113).
- Constraints: byte-identical for a timeline with no chapter (no `chapters` key written); the pill's type at least
  59.08 stage px; the key rail's dials, not new ones. The pill is chrome, not a series name, so s118's series ink does
  not apply.
- Acceptance:
  1. `{kind: "chapter", at, until, text}` on a row. The compiler lifts it into the timeline's `chapters: [{text, at,
     until, box}]`. `until` may pass the row's end. Chapters never overlap, and `at` / `until` fall on words.
  2. The pill lands at `at` by the key rail's spring, in one corner measured from BUB `frame_0063.jpg`. It HOLDS through
     recasts, parks, returns, dips and world changes without re-landing, and leaves on `until` on the E50 exit curve.
  3. Its box is room chrome for every scene inside its window: docks, stamps (`ring_obstacles`), captions and the camera
     avoid it, and the probe reads it (a collision is caught by M25 / M28).
  4. One golden, `chapter-held`, taken after the cut. No H body row adopts it before HG1.
- Exclusions: a chapter on a short (the don't); the swap (T10); numbered acts (the agenda species is `SETS`'s other
  tool).
- Stop conditions: a cross-scene painter cannot be added without changing the overlay's existing stacking for other
  elements (report).
- Regression: `python -m pytest content/video_engine/tests/test_chapter_pill.py -q`
- Expected RED: `kind: "chapter"` is refused as unknown.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/lint_species_choice.py --when --check-doc` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_chapter_pill.py`, `test_page_chrome_moves.py`, `test_the_stamp_arrival.py`, `test_gate_motion_density.py`, `test_lint_species_choice.py`, `test_build_effects_catalog.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`, and each `test_authoring_*.py`, then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: the parent reads `chapter-held.png` beside BUB `frame_0063.jpg` (12:22.1-12:34.1, "two crucial
  things"), `content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/frames/frame_0063.jpg`
  in the main checkout.
- Return: the common lane-B return. CAPABILITIES row: "The chapter pill".
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T10: The in-place badge swap on the chapter pill (was P69 T61, A44)
- Status: pending (UNBLOCKED 2026-09-24: BOOM read on real frames - A44 CONFIRMED in place at 02:27.0-02:27.5, "Dot-Com Bust" rolls into "Lost Decade" in the same pill; the 02:47-02:49 instance is NOT in place (old pill leaves, new one arrives) and is not a witness. `docs/research/runs/bravos-watch/jx3Ll-GJtMY/verify/VERIFY.md`, frames `A44_A45_T37_swap1/frames/t02m27.0s.jpg`)
- Owner: implementation_luna (LANE B)
- Depends on: P70 T9 merged. **Blocker:** harvest v2 `:318` says "Verify the Gemini-only timings for BOOM (`jx3Ll-GJtMY`
  has no frames on disk) before any of R32 / R36 / A44 / A54 / A56 is built from them". `docs/research/runs/bravos-watch/jx3Ll-GJtMY/`
  holds only `GEMINI-REVIEW.md`.
  - Unblock: the research lane (Gemini / Antigravity owns `docs/research/**`) fetches BOOM's frames at 02:19-03:00 and
    confirms A44 at 02:23-02:27 ("Dot-Com Bust" -> "Lost Decade").
  - If A44 is not on the frames, T10 is retired.
- Harvest: v2 A44 "In-place badge swap: the pill's text flips, the pill stays", MISSING, n=1 (BOOM 02:23->02:27 (G)).
- Use when (USE-WHEN `:771`): "the same period is renamed ('Dot-Com Bust' → 'Lost Decade')". Don't: "the rename changes
  the period (move the pill instead)".
- Recall: docs_find "badge swap" -> 1 hit (the CAPABILITIES manifest), 0 rows; harvest v2 `:136` "MISSING. `retitle` rewrites only the title"
- Verdict: EXTEND T9's pill with the retitle's glyph write (`buildPerform`'s retitles block `:13920`, `lpGlyphs`,
  `rtSpanGlyphs`), called, not edited.
- Write set: the engine's `paintChapters`; `build_scene_timeline_f.py` `_validate_chapter` (`swap: [{at, text}]`);
  `effects/cards/species.json` (`species:chapter` option `swap`); `content/video_engine/tests/test_chapter_swap.py`
  (new); the golden files (`chapter-swap`, new).
- Input evidence: the chapter pill of T9. Among H's candidate swaps, row 22's "The flip" is now a red retitle (T86), so
  the parent names the H beat once the BOOM frame is read, or T10 is proved on the R22 epoch walk's beat.
- Acceptance: the constraints included -
  1. A swap rewrites the text in place on its word (the old glyphs erase, the new ones write, and the width springs).
  2. A swap never moves `at` / `until`, which is the mechanical form of "the rename never changes the period". A new
     period is a new chapter.
  3. Byte-identical without `swap`.
- Exclusions: swaps on other pills.
- Stop conditions: the BOOM frames do not show A44.
- Regression: `python -m pytest content/video_engine/tests/test_chapter_swap.py -q`
- Expected RED: `swap` is an unknown key on a chapter.
- Validate: `node --check docs/content-video-engine/samples/scene-evidence-engine.mjs` then, each in its own process, `python -m pytest -q` on `content/video_engine/tests/test_chapter_swap.py`, `test_chapter_pill.py`, `test_retitle_color.py`, `test_golden_frames.py`, `test_effects_catalog_drift.py`
- Frame acceptance: `chapter-swap.png` beside the fetched BOOM frame at 02:25.
- Red evidence: pending
- Green evidence: pending
- Evidence: pending

### T13: The drift-hold - a held chart card or evidence dock breathes, turns a fraction and catches a light, one whole cycle per hold (the operator, 2026-09-24; HyperFrames drift-hold)
- Deviation (the parent, 2026-09-24): the acceptance (one cycle per HELD span; a light sweep) cannot be met inside the idle region - `idleCssFor` (engine, outside the region) passes no span and the idle runs on the life clock (only the engine knows the freeze windows), and nothing paints a light band on a card (the cited sheen/glint `~:1828` records 0 hits). APPROVED: T13 also edits the engine's dock painter (`idleCssFor` gains an optional span converted to the life clock; the 4 dock call sites pass `[d.enter, d.exit]`; a new `paintHoldLight`). T8 (which owns `render()`'s dock-arrival branch) has not started and builds on top. `hold` is a card-only idle kind (`IDLE_CARD_KINDS`), not in `IDLE_KINDS` (`test_idle_e49.py:65`). Press cards (`paintPress`) are not covered - filed.
- Status: done - lane B 35a2130 (the drift-hold)
- Owner: implementation_luna (LANE B)
- Depends on: T37b (the page's inks) integrated; nothing else in P70
- Harvest: the operator, 2026-09-24: "npx hyperframes add drift-hold i think this becomes an interesting reference to hold charts/evidence docks with". The component is already on disk, harvested 2026-09-07 as a reference only (fc71e49 - "nothing in the engine changes"): `content/video_engine/hyperframes/compositions/components/drift-hold.html` - sub-degree rotation, restrained scale breathing and a soft light sweep, each ONE complete sine cycle across the mounted duration, the endpoint phase wrapped so t=0 equals t=duration (loop-safe); intensities `whisper` / `standard`.
- Recall: docs_find "drift-hold" -> 0 capability hits (R26-15 names the harvest); CAPABILITIES :72 "The idle, WIRED" (E49): kinds breath / drift / pulse / figure in `kinetics/idle.mjs` - no rotation idle, no light sweep, no whole-cycle-per-hold law; the opt-in sheen/glint (OPERATOR-RULINGS ~:1828) is the light to REUSE for the sweep
- Verdict: EXTEND - a new idle kind `hold` in `kinetics/idle.mjs` (rotation + breath + sweep, each one whole cycle over the held span, phase-wrapped), opt-in per dock / chart card (`idle: hold[:whisper|standard]`), never a default change; the dials read off drift-hold.html's own amplitudes (a DERIVED tag per dial), not invented
- Write set: `content/video_engine/scripts/kinetics/idle.mjs` (the `hold` kind), the engine's idle region via `sync_kinetics.py --write`, `content/video_engine/scripts/build_scene_timeline_f.py` (the dock / card option's validation), `content/video_engine/effects/cards/<idle card>.json`, `content/video_engine/tests/kinetics/idle.test.mjs`, a new test, one golden on a real H held dock (s60), the parent's sheet
- Acceptance: a dock or chart card with `idle: hold` breathes, turns under a degree and carries one light sweep, each exactly one cycle across its held span (t=0 pose == t=end pose, measured); the sweep never crosses the dock's text at a read-hurting alpha (E28); `whisper` for a card carrying a chart, `standard` for a picture; absent the option every door byte-identical; the parent reads ours beside drift-hold.html rendered by `npx hyperframes@0.7.101 render` on one sheet
- Regression: `node --test content/video_engine/tests/kinetics/idle.test.mjs`
- Expected RED: `hold` refused as an unknown idle kind
- Validate: `node --test "content/video_engine/tests/kinetics/*.test.mjs"`, `python content/video_engine/scripts/sync_kinetics.py --check`, `python -m pytest content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T11: Integration and merge - the registries, the regenerations, CAPABILITIES, one commit per slice
- Status: pending
- Owner: parent (integration), release_steward (commits)
- Depends on: each slice's review and frame read
- Write set:
  - lane B: each slice's patched files;
  - the registries (the union);
  - the parent-merged registries, the unions of every patch's lines;
  - the generated files, which only the parent writes: `content/video_engine/assets/page-boxes.v1.json`,
    `docs/content-video-engine/SPECIES-BY-SENTENCE.md`, `docs/EFFECTS-CATALOG.*` (`build_effects_catalog.py --write`);
  - `docs/content-video-engine/CAPABILITIES.md` (one row per built verb, in its slice's commit), and the goldens.
- Acceptance:
  1. Patches are applied with `git apply --3way` in the listed order (T1, T2, T3, T4, T5, T6, T7, T8, T9), each
     committed in lane B with explicit paths. Each commit carries a `Recall:` line citing a committed path.
  2. After each apply: `sync_kinetics.py --write` then `--check`; `measure_page_boxes.py --write`;
     `lint_species_choice.py --when --write-doc`; `build_effects_catalog.py --write`, then `--check`.
  3. The goldens are re-pinned ONCE after T9, with the sha table in that commit's message.
  4. The full suite is diffed against the base fail set (the grammar rule: `test_authoring_*` plus a full-suite diff
     before any push).
  5. The committed H door is identical after the last slice.
  6. The shared-registry process: pushes touching CAPABILITIES or cards need the registry check and a Claude bridge
     REGISTRY-ACK.
  7. No push without the operator's current word. The merge to main follows the register's checklist
     (`docs/runbooks/PRP_EXECUTION.md` "Before anything reaches main").
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --check` then `python content/video_engine/scripts/lint_species_choice.py --when --check-doc` then `python content/video_engine/scripts/build_effects_catalog.py --check` then `python content/video_engine/scripts/effects_catalog_check.py` then `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T12: P70-HG1 - the operator watches the nine verbs' beats, played with the take
- Status: pending
- Owner: parent (frames the gate; a proof door built by implementation_luna in lane A); the operator rules
- Depends on: T11. It is batched to the end on the operator's standing word ("resolve all non-human blockers and i'll
  review human gates at the end").
- Write set:
  - `content/video_engine/projects/systems-and-blowups/steel-and-paper/proof_p70_verbs.py` (new, lane A). This is the
    proof door, on the pattern of P69 T13's `proof_chip_landing.py`: it imports the H door's read-only constants and
    builds each verb's ONE beat on the take (`vo-h-scratch/scratch-kokoro.words.json` and its audio). There is one
    private test-bed build per verb.
  - `.../steel-and-paper/build-p70-<verb>/**` (gitignored, frozen, served on its own port, never :8731, never rebuilt
    while linked).
  - `docs/content-video-engine/REVIEW-QUEUE.md`, `docs/content-video-engine/review-queue.v1.json` (the row framed in T0,
    updated with the links).
  - Then `docs/portable/OPERATOR-RULINGS.md` and this plan with the ruling.
- Acceptance:
  1. **Scenes, not fixtures (s60, `:3238`).** Each verb is served as its test-bed beat PLAYED WITH THE TAKE. No golden
     PNG is served as a scene; the goldens stay the mechanism's pin. Each beat is shown beside its Bravos frame (the
     paths in each slice's frame acceptance) and labelled with the H sentence it carries. T7's tip is served from its
     private reference bed, labelled as reference.
  2. **The one question.** The card asks (a) only: whether any verb's beat is adopted by an H body row, with the chapter
     pill's act markers named (harvest v2 `:274`). It is asked once, here, and not again at P69-HG4.
  3. **The one approval.** The card asks for the approval of T8's quarantined "paper" prop, which brings it out of
     quarantine into the props catalogue (E36: generating it needed no consent). This is an approval, not a question.
  4. Rulings already on record are not re-asked: the scale is settled by E79 and E53 s4, and the row-16 tip by
     USE-WHEN `:646` (check the rulings before asking).
- Validate: `python content/video_engine/projects/systems-and-blowups/steel-and-paper/proof_p70_verbs.py` then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

## Verification

- Each slice's Validate is run by the parent in lane B after integration, each pytest file in its own process and
  unpiped (never `| tail`).
- Byte identity: the committed H door compiles identically (`engine_sha256` aside) and renders N of N instants
  identically before and after every slice. Log: `$SP/p70-tN/logs/door-identity.log`.
- The rulings each slice respects:

  | ruling | where it is in the rulings file | what it requires | slices |
  |---|---|---|---|
  | E25 | `:761` | a chart proves one sentence | T2, T3, T4 |
  | E28 | `:835` | reads at a glance; drops go down | T3 (the whole named), T6 (the sign) |
  | E53 | `:1705` | census and honesty forms | T3, T4, T5 |
  | E56 / s110 (2) | `:1815` / `:3351` | ring use | T1's impact ring is not E56's ring (`stopaction.mjs:311`); no slice adds a ring |
  | E99 s60 | `:3238` | a proof is a scene | every golden sits on an H beat; T7's tip is a private test-bed beat; HG1 serves test-bed builds played with the take, never goldens |
  | s99 | `:3329` | a light that travels is motion | T2 |
  | s100 / s109 | `:3331` / `:3349` | forms judged by honesty | T2's (1), T3, T5 |
  | s105 amended | `:3341` | a move is an arrival when it lands on its word and names a new thing | T4's reveal, T9's pill |
  | s106 | `:3343` | the engine advises, the author decides | T1's fit, T4's placement, T3's two gauges |
  | s112 / s116 | `:3355` / lane A `:3363` | the stamp is punctuation; its sound follows it | T1, T8 |
  | s113 | `:3357` | text on a plate when verified | T9's act names, T8's prop ("BOND" or none) |
  | s117 / s118 | lane A `:3365` / `:3367` | the lines bloom; names wear their series' ink | owned by P69 T37b; P70 reads its helper (T2, T3, T4, T5) and never paints series ink itself |
  | E79 / E53 s4 | `:2517` / `:1740` | one measure, one scale, one unit | T4 (the new WARN and the re-expression) |
  | E53 addendum | `:1784` | a value is drawn once | T4 drops the line's railway hline |
  | E36 | `:1175` | images are free | T8's claim, quarantined |
  | E81 | `:2542` | foley starts 8-10 dB under the voice | T8's poof cue |
  | doc 42 §42.4 | `42-*.md:102` | generated curves are clothoids | T5's brace, T7's arms |
  | s90 floor | `ledger_page.py:4187-:4188` | 59.08 stage px | every label in T1-T9 |

## Evidence And Handoff

- Planning evidence is in `$SP/p70-plan/`: `recall-raw.txt` (34 docs_find runs from the lane-B root), `take-times.txt`
  (every H word time cited) and `provenance.txt` (both heads, both dirty sets, the sha256 of every edited file).
- The docs layers were STALE during recall. docs_find reported "FAILED to build capabilities-index - 233 records, 4
  flagged". Every capability claim above was therefore also read directly in lane B's `CAPABILITIES.md` (`:79`, `:99`,
  `:100`, `:103`, `:124`, `:210-:238`) and the code. A slice that finds a capability recall missed stops and reports.
- **Deviations:**
  1. Parallel wave slices edit the same files (the engine, the compiler) in separate scratch exports, with disjoint
     functions. Every shared registry, card file, dispatch chain and exception list is parent-merged, and no generated
     file is in a patch. The parent integrates by `git apply --3way`. The runbook's rule is disjoint files.
  2. P69 T61 is split into T9 and T10.
  3. The P69 T12 stub's "or refused by name" becomes a WARN (s106, P69 T26d).
- **Revision 2 (2026-09-24)** folds in `$SP/p70-plan/REVIEW.md` 1-11 and the parent's eleven rulings. The revision 1
  text is kept as `$SP/p70-plan/fix/P70.before-review.md`. The fix script is `$SP/p70-plan/fix/apply_fixes.py` (with
  `blocks.py`).
- **Handoff to the parent:**
  - T0's re-captured base, the P69 pointer edits and the REVIEW-QUEUE row.
  - The research-lane commission for T10's BOOM frames.
  - T8's claim approval at HG1.
