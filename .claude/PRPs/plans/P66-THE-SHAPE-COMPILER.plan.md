---
id: P66-THE-SHAPE-COMPILER
title: The shape compiler - the authoring kit turns an AUTHORED per-sentence beat plan into the approved skeleton as a generated shot table (several skeletons per beat shape, chosen by the sentence act and a variety rule), the agent modifies that BASE through the table and the sidecar and names every departure in the ledger, and gate_one_shot_floor grows M45 parity by mechanism and M46 signature variety
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# The shape compiler

## Summary

E99 s68, Q1 = C and Q4 = A amended: the approved shape lives in the KIT and the GATE, and *"the compiler outcome
doesn't have to be the final solution, the agent can use it to establish the base of the video and then modify."*
The failure it answers is one-shot #3 (E99 s67): the docs were read, the mechanisms went unused, and the agent was
handed a blank shot table. The operator: *"you basically just started shining lights everywhere to call it
animation ... you also land your charts fully built ... This is a regression compared to tokyo tea or japan. I dont
think this should have gotten past yoru gates or comparison, and you didn't really blend the old and new
capabilities."*

P66 builds three things:

1. **`authoring/shapes.py`** - input: the build's AUTHORED `BEAT-PLAN.jsonl` (M41's schema: `beat`, `t0`, `t1`,
   `sentence`, `row`, `act`, `comparator.compared_to`, `capabilities[]`, `recipe|null`, `why_none`) plus the take's
   words; output: the kit's own row grammar written through `table.write_shot_table`. The skeleton it emits is the
   approved one: the page on the hook drawing on its axes, a MOUNT for any page whose number lands 7 s or more in,
   axes entries elsewhere, the dip for a world change, the suck or cut page to page, the spiral return for the ring,
   docks that read then park in the page's own room, a plate's six seconds, no rails and no park at 9:16.
2. **Several skeletons per beat shape**, derived from the three approved tables and today's proven recipes, chosen by
   the sentence act and a VARIETY rule - no signature twice running, the approved shorts' own mix as the target.
   The blueprint's gotcha: a compiler whose choreography vocabulary is smaller than the sentence-shape vocabulary
   converges every cut, and a parity gate cannot see repetition.
3. **M45 parity by mechanism and M46 signature variety** in `gate_one_shot_floor.py` - per approved mechanism:
   present / absent / replaced by what (E99 s67 Apply 7; R26-177 says the comparison owes a row per mechanism), and
   the cut's signature mix against the approved shorts'.

**The output is a BASE, never a cut.** The two doors already exist - the agent edits the generated rows in the shot
table, or layers `<build>/overrides.json` through `table.apply_sidecar` (P51 T5) - and every departure from the base
becomes a numbered decision in the project's `PRODUCTION-LEDGER.md`, read back by the CLI so an unnamed departure is
caught rather than trusted.

**The doctrine line, in one sentence:** `authoring/recipes.py:1-20` ("NOT AN ALLOCATOR") and
`docs/content-video-engine/PIPELINE.md:33` ("Stage 7 is AUTHORED. There is no allocator") both stand, because the
compiler consumes an AUTHORED beat plan - the intelligence work E99 s66 reserved to an agent or the operator - and
fills nothing by count; **s68 outranks the older reading of "authored" as "every row typed by hand": the author still
decides every beat, and now edits a base instead of a blank page.**

All repo paths are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`).

### Recall (2026-09-16, `docs/runbooks/RECALL-RECEIPT.md`)

- Recall: `docs/content-video-engine/GRILL-AGENTS-HARNESS-EFFECTS-2026-09-16.md:10-19` (decisions 1 and 2 verbatim,
  including the operator's sentence on the base), `:38-39` (rejected: one skeleton per beat shape), `:47-48`
  (templated reads as templated - the mitigation is several skeletons, the variety rule, M46 and the agent's edits).
- Recall: `docs/portable/OPERATOR-RULINGS.md:3252` (E99 s67 Apply 1-8: lights are punctuation not filler; every page
  BUILDS then holds built; a dock is an evidence still, never a chart card thrown on the open; the open STARTS ON THE
  CHART; parity BY MECHANISM; old and new capabilities BLEND), `:3250` (s66: the beat plan is intelligence work),
  `:3254` (s68).
- Recall: `docs/content-video-engine/BACKLOG.md:612` (R26-180, the skeleton list and both gate rows), `:609`
  (R26-177: M40's parity owes a row per mechanism), `:603-604` (R26-171 no rails at 9:16, R26-172 no park at 9:16),
  `:600` (R26-168 - why M38 is not the floor this plan leans on).
- Recall: the three approved tables, read in full - `tokyo-tea-break/build_short.py:219-226` (*"the holdings page
  ROLLS OUT ON THE HOOK and stays; the clips stop being scenes and arrive as DOCKS over it; the ring returns the page
  unwound and the host mounts on the last line"*); `japan-tariff-trick/build_short.py:169-176` (*"the REAL chart
  mounts over the podium on the hook line ... the parts page mounts over them on 'An engine block' ... the holdings
  page RETURNS by the spiral"*); `memory-trades-the-calendar/build_short.py:137-152` (v9b, E99 s67: *"THE OPEN IS THE
  CHART: the calendar page is the first frame, on its axes, its two lines drawing under the hook ... the into/after
  bars ENTER ON THEIR AXES ... and GROW while the sentence runs ... the calendar page RETURNS BY THE SPIRAL"*).
- Recall: `content/video_engine/scripts/authoring/table.py:1-16` - a row is a TUPLE and stays one,
  `(start, end, plate_id, ken_burns, [docks], exit[, species[, camera]])`; `:27` `write_shot_table`; `:43`
  `apply_sidecar` (P51 T5); `:89` `hold_until`; `:113` `compile_timeline`.
- Recall: the plate id grammar, `PIPELINE.md` stage 7 -
  `ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>]]` with the entry suffixes (`axes`, `mount=<s>`, `spiral`,
  `snap=<dock>`, `built`) and `:cut`; plates as `plate-x;idle=drift;drift=35` with a Ken Burns triple; pages STILL;
  exits `dip` / `cut` / `suck`.
- Recall: `content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/build-oneshot-3/BEAT-PLAN.jsonl`
  - beat 1 carries `act: "hook / the claim - THE OPEN IS THE CHART"`, `comparator.compared_to`, `capabilities[]`,
  `recipe: null` with a `why_none`, and a `plate` field already holding the row's plate id; the gate's reader is
  `gate_one_shot_floor.py` `SRC_M41` (`:125`).
- Recall: `docs/GATES-REGISTRY.md` M ids present up to **M44** - M45 and M46 are free, as the blueprint assumes.
- Recall: `docs/runbooks/ONE-SHOT.md:32-45` - the loop's table; step 4 is the beat plan, **step 5 (`:41`) is "The
  shot table - authored, never allocated"**, step 7 (`:43`) is the gates.
- Recall: `PRODUCTION-LEDGER.md` exists in three projects; `memory-trades-the-calendar/PRODUCTION-LEDGER.md:22` is
  the section *"Decisions taken without the operator (for the watch)"*, a numbered list. `rg PRODUCTION-LEDGER` over
  `scripts/*.py` and `docs/runbooks/*.md` = **0 hits: no tool reads it today** (T4 makes the first reader).
- Recall: memories `visible-difference-and-local-life` (E99 s38 - a card is judged only on a visible difference),
  `dip-is-a-world-change` (E47), `plate-life-is-directional`, `one-shot-lessons-2026-09-16` (what the 9:16 gates
  want), `judge-the-frame-not-the-diff`, `never-pipe-gated-steps-to-tail`.

## Intent And Acceptance

Intent: an agent that has authored a beat plan gets the approved shape as rows it can read, judge and change - and
the gate can say, per approved mechanism, whether the cut used it, dropped it, or replaced it with something named.

Acceptance (all observable from the main checkout):

1. `python content/video_engine/scripts/generate_base_table.py <project> <build>` reads the build's
   `BEAT-PLAN.jsonl` and the take's words and writes the generated rows through `table.write_shot_table`, plus
   `<build>/BASE-TABLE.md` naming, per row, the skeleton chosen, the act that chose it and the rule that applied
   (the page on the hook; the mount because the number lands at +N s; the dip because the world changes; the spiral
   because the beat returns). Re-running on the same plan is byte-identical.
2. The generated base obeys the approved shape without being told: the first beat is the page ON ITS AXES drawing
   (E99 s67 Apply 6); any page whose number lands 7.0 s or more after its entry gets `mount=<s>`, never `built`;
   every other page enters by its axes; a world change exits by `dip` (E47), page to page by `suck` or `cut`, never
   into a mount; a return uses `spiral`; docks read then park in the page's own room; no plate row is shorter than
   6 s (M44); no `badges` rail and no `chart_to park` is emitted at 9:16 (R26-171 / R26-172); a light is placed only
   on a sentence that POINTS, and never before the page's build ends (E99 s67 Apply 1-2).
3. The skeleton library holds **at least two skeletons for every beat shape** (T1's list), each carrying its source
   as `path:line` in an approved table, and `shapes.choose` refuses to use the same signature on two consecutive
   beats; `<build>/BASE-TABLE.md` prints the cut's signature mix beside the approved shorts' measured mix.
4. `python content/video_engine/scripts/generate_base_table.py <build> --departures` diffs the build's final table
   (and its `overrides.json`) against the generated base and lists every departure; it exits 1 naming any departure
   with no matching `BASE DEPARTURE` row in the project's `PRODUCTION-LEDGER.md` "Decisions taken without the
   operator" section. The row's format is fixed: `N. BASE DEPARTURE - row <n> <what changed>: <why>, <ruling or
   path:line>`.
5. `gate_one_shot_floor.py` prints **M45** - one line per approved mechanism (the page on the hook, the mount's
   build, the axes entry, the dip on a world change, the page-to-page transform, the spiral return, the dock that
   reads then parks, the callout or ring on a chart, the plate that carries a card): `present` / `absent` /
   `replaced by <mechanism>`; a mechanism that is absent with no replacement FAILs, a replacement WARNs with both
   names. And **M46** - the cut's signature mix against the approved shorts', WARNing on a signature used more than
   the approved maximum share or on two consecutive identical signatures.
6. `docs/GATES-REGISTRY.{md,jsonl}` carry M45 and M46 with their thresholds, regenerated by
   `build_gates_registry.py --write`; `docs/content-video-engine/CAPABILITIES.md` carries THE SHAPE COMPILER row and
   `docs_find.py "shape compiler"` finds it.
7. `docs/runbooks/ONE-SHOT.md` step 5 (`:41`) reads **"generate, then modify - and name every departure"**, with the
   command, the two doors (the table and the sidecar) and the `--departures` check in its Check column.
8. Nothing in the kit names an episode (`authoring/__init__.py:12-15`), no engine or compiler module is touched, and
   the golden suite is byte-identical.

## Scope

- `content/video_engine/configs/shape_skeleton.schema.json` (new, `shape_skeletons.v1`).
- `content/video_engine/effects/skeletons/*.json` (new, tracked) - the skeleton library, each with its `path:line`
  source in an approved table - and `approved-mix.json`, the target distribution measured from the three approved
  cuts' compiled timelines.
- `content/video_engine/scripts/authoring/shapes.py` (new) and `content/video_engine/scripts/generate_base_table.py`
  (new), with their tests.
- `gate_one_shot_floor.py`: M45 and M46 (+ `ROW_ORDER`), `test_gate_one_shot_floor.py`,
  `docs/GATES-REGISTRY.{md,jsonl}`.
- `docs/runbooks/ONE-SHOT.md` step 5 and its Check column; `docs/content-video-engine/CAPABILITIES.md`;
  `docs/content-video-engine/BACKLOG.md` R26-180 / R26-177; the generated docs layers.
- One queue row (HG1) in `docs/content-video-engine/review-queue.v1.json` + `REVIEW-QUEUE.md`.

## Not Building

- **No beat-plan writer.** E99 s66: the beat plan and the script are intelligence work. The compiler's INPUT is
  authored; if `BEAT-PLAN.jsonl` is missing or incomplete the tool refuses by name and points at M41.
- **No allocator.** Nothing is filled by count, nothing is chosen to hit a rate, and the tool has no "make it
  denser" mode. A beat with no plan record is a refusal, not a slot.
- **No engine, compiler or golden change**; no new species, page builder, transition or kinetics module. The
  compiler emits rows the existing compiler already accepts and the existing gates already read.
- **No recipe lab work** - P65 owns the enumerator, the batches, the log and the promotions. P66 starts on today's
  **15 proven recipes and the three approved tables**; P65's promotions widen the skeleton library later (T1 says
  where a new skeleton is added, and that adding one is a data change, not a code change).
- **No M38 change** (P65 T7) and no change to M35-M42's definitions.
- **No auto-editing of a build's table.** The compiler WRITES a base; it never rewrites a table an agent has edited,
  and it refuses to write over a table whose file is newer than the plan unless `--force` is given with a reason
  recorded in `BASE-TABLE.md`.
- **No render, no serve, no operator link** beyond HG1's frozen copy; no approved cut is rebuilt.
- **No BACKLOG row closed by an agent** - T6 is the parent's.

## Approval

Approved by the operator 2026-09-16: *"yes, run them in parallel /prp-implement"* - P65, P66 and P67 run as concurrent delegated slices on main (disjoint write sets; the two shared files sequenced as written), no new worktree.

## Human Gates

**HG1 - the first generated base (operator, after T4).** The Tokyo bed's own beat plan run through the compiler,
built, frozen and served, read beside the approved Tokyo cut at the same instants. The question is E99 s38's: is
there a **visible difference**, and is the generated base the right starting point - or does it read as templated
already at one cut? Options: take the base as the default opening move for the next one-shot; take it only for
named beat shapes; or send the skeleton library back for more variety. Blocks T5's thresholds (M46's maximum share
per signature is set by the answer) and the Opus one-shot that runs on the compiler's base (E99 s66 step 2). The
queue row is written in T4, kind `watch`, with a clip proof and the player link to the frozen copy.

Parent decisions recorded so they are not re-litigated (NOT operator gates): the skeleton schema and the skeleton
LIST (T1, below); the ledger's departure format (T4); the gate ids M45 / M46 (the next free ids after M44).

### The skeleton list (T1, parent-owned; every entry cites an approved table)

| skeleton | the shape it serves | source |
| --- | --- | --- |
| `open-on-the-chart-axes` | the open: the page is the first frame, on its axes, drawing under the hook | `memory-trades-the-calendar/build_short.py:138`; E99 s67 Apply 6 |
| `open-page-mounts-the-world` | the open: the page mounts over a world plate on the hook's last word | `japan-tariff-trick/build_short.py:170`; `tokyo-tea-break/build_short.py:235` |
| `page-mounts-over-the-world` | a page whose number lands 7 s or more in | `japan-tariff-trick/build_short.py:172-174` (the parts page, the receipt page, the vault) |
| `page-enters-on-its-axes` | a page whose number lands early, or a second page in a run | `memory-trades-the-calendar/build_short.py:141-147` (the into/after bars, the share page, the weak prints, the daily line) |
| `held-page-hosts-the-docks` | a page that stays while evidence arrives over it | `tokyo-tea-break/build_short.py:221-222` |
| `plate-carries-a-card` | a narrative beat: a plate with its idle, a card that reads then parks | `japan-tariff-trick/build_short.py:173` (the ship); `memory-trades-the-calendar/build_short.py:139-140, :147` |
| `page-to-page-no-cream` | a page-to-page transform (suck or cut, never into a mount) | `memory-trades-the-calendar/build_short.py:145-147`; recipe `chart-to-chart-with-no-cream` |
| `spiral-return` | the return: the page comes back unwound, the ring on its one use | `japan-tariff-trick/build_short.py:174`; `memory-trades-the-calendar/build_short.py:150-152`; `tokyo-tea-break/build_short.py:222` |

Two per shape is the floor (the blueprint's rejected alternative was one per shape); the open and the page shapes
each have two above, and T2 derives a second for `plate-carries-a-card` and `page-to-page-no-cream` from the same
three tables. A NEW skeleton is a JSON file plus its source cite - no code change - which is how P65's promotions
widen the library.

## Mandatory Reads

- `docs/content-video-engine/GRILL-AGENTS-HARNESS-EFFECTS-2026-09-16.md` - decisions 1, 2, the rejected
  alternatives, gotcha 1 and the build order.
- `docs/portable/OPERATOR-RULINGS.md` **E99 s67** (`:3252`, all eight Applies), **s68** (`:3254`), **s66**
  (`:3250`); E47 (the dip is a world change), E56 (the ring's one use), E65 (the page's own empty room), E96.
- `docs/content-video-engine/BACKLOG.md` R26-180 (`:612`), R26-177 (`:609`), R26-171 / R26-172 (`:603-604`).
- The three approved tables, in full: `tokyo-tea-break/build_short.py:219+`,
  `japan-tariff-trick/build_short.py:169+`, `memory-trades-the-calendar/build_short.py:137+` (v9b).
- `content/video_engine/scripts/authoring/table.py` (all of it), `authoring/__init__.py`, `authoring/words.py`,
  `authoring/docks.py`, `authoring/recipes.py:1-20`, and `authoring/defaults.py` once P65 T6 lands.
- `content/video_engine/scripts/gate_one_shot_floor.py` (M35-M42, `Measures`, `ROW_ORDER`, `SRC_M40`, `SRC_M41`) and
  `content/video_engine/tests/test_gate_one_shot_floor.py`; `gate_motion_density.py` (`PAGE_BUILD_END_S:248`,
  M11, M12, M16, M25, M44).
- `docs/content-video-engine/PIPELINE.md` stage 7 and `:33`; `docs/runbooks/ONE-SHOT.md:32-45`;
  `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (the 11 acts).
- `content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/BEAT-PLAN.jsonl` under
  `build-oneshot-3/`, and that project's `PRODUCTION-LEDGER.md:22` ("Decisions taken without the operator").
- `docs/WORKTREE-REGISTER.md` (read at start); `docs/runbooks/PRP_EXECUTION.md`; `docs/runbooks/RECALL-RECEIPT.md`.

## Execution Path

T1 (the schema and the skeleton list) first; T7 (the two approved cuts' beat plans, the parent's) runs beside it. T2 (the skeleton files and the approved mix) needs T1 and is pure
derivation from the three tables and their compiled timelines. T3 (`shapes.py` - the compiler and the chooser) needs
T2. T4 (the CLI, `BASE-TABLE.md`, the departures reader, the HG1 queue row) needs T3. **HG1 gates T5's thresholds**
(M46's maximum share per signature is the operator's answer); T5 may be written before the answer with the number as
a named constant and a test that reads it. T6 (doctrine) is last and the parent's.

Two sequencing notes for the parent: **(a)** P65 T4 and P66 T4 both write `review-queue.v1.json` - they land one
after the other, never in parallel; **(b)** P65 T7 (M38's interim WARN) is written to depend on **T5 of this plan**,
so the parity row exists before the recipe row stops binding. Both plans touch `gate_one_shot_floor.py` (P65 T7:
`row_m38` and `SRC_M38` only; P66 T5: M45, M46 and `ROW_ORDER`) - the two edits are in different functions, and the
steward lands them in separate commits, P66 T5 first.

Commits by the `release_steward` from the main checkout, allowlisted paths; a commit touching a mechanism file
carries its `Recall: <path>:<line> (note)` lines (`scripts/hooks/recall_receipt.py`). Nothing pushed without the
operator's word. Every gated step runs UNPIPED.

## Patterns To Mirror

- `content/video_engine/scripts/authoring/table.py`: the kit owns the mechanism, the episode owns every fact. The
  compiler takes the plan, the words and the defaults as ARGUMENTS and names no episode.
- `content/video_engine/scripts/authoring/recipes.py`: a module that returns data and refuses to allocate, saying so
  in its own docstring with the citation. `shapes.py` opens the same way, citing s68 for what changed.
- `content/video_engine/scripts/change_report.py`: the before / after pair at the instants a change touches - the
  shape `--departures` reports a departure in.
- `content/video_engine/scripts/gate_one_shot_floor.py` `row_m40`: a JUDGE row that measures the reference at run
  time rather than quoting a remembered number. M45 and M46 read the approved cuts the same way.
- P56 T6's fixture habit: the new rows are asserted on the approved cuts' own measured numbers, never on a hope.

## Task Slices

### T1: The skeleton schema and the skeleton list
- Status: done
- Owner: parent
- Depends on: none (P65's promoted recipes widen the library later; P66 starts on today's 15 proven recipes and the three approved tables)
- Write set: `content/video_engine/configs/shape_skeleton.schema.json`, this plan's skeleton-list section
- Acceptance: `shape_skeletons.v1` - `id`, `shape` (the beat shapes P65's `beat-shapes.json` names, so the two files agree), `acts` (from the 11), `signature` (the one word M46 counts: `axes`, `mount`, `spiral`, `suck`, `cut`, `dip`, `card`, `hold`), `rows` as a TEMPLATE of the kit's row grammar with named holes the build fills (`{page}`, `{plate}`, `{dock}`, `{t0}`, `{t1}`), `rules` (the clocks it must satisfy: the 7 s mount rule, M44's 6 s, M16's 2.5 s, the light after the build), `source` as `path:line` in an approved table, and `aspect_limits` (what it may not emit at 9:16 - rails, park). `additionalProperties: false`; at least two skeletons per shape is asserted by T2's test, not by the schema.
- Validate: `python -c "import json;s=json.load(open('content/video_engine/configs/shape_skeleton.schema.json',encoding='utf-8'));print(s['$id'], sorted(s['$defs']['skeleton']['required']))"`
- Evidence: `content/video_engine/configs/shape_skeleton.schema.json` (`shape_skeletons.v1`; required acts/aspect_limits/id/rows/rules/shape/signature/source; the act enum is the page's TWELVE - COUNTS included by the parent, the plan's "11" undercounted SPECIES-BY-SENTENCE.md:57; optional `schema_version`; `Draft202012Validator.check_schema` ok; good sample accepted, bad sample refused with 7 named errors - report `scratchpad/assembly/P66-T1.md`).
- Deviation: drafted by `junior_developer` from the plan's fixed list and reviewed by the parent (COUNTS and `schema_version` added on review).

### T2: The skeleton library and the approved mix, derived from the three approved tables
- Status: done
- Owner: `implementation_luna`
- Depends on: T1
- Write set: `content/video_engine/effects/skeletons/*.json`, `content/video_engine/effects/skeletons/approved-mix.json`, `content/video_engine/tests/test_shape_skeletons.py`
- Acceptance: every skeleton in T1's table exists as a file valid against `shape_skeletons.v1`, its `source` resolving to a real `path:line` whose text still contains the mechanism it claims (the test opens the file and greps the line, as `effects_catalog_check.check_anchors` does for a card's `lives`); at least TWO skeletons carry each `shape`. `approved-mix.json` is MEASURED, not typed: the signature counts and shares of the three approved cuts read from their compiled timelines with `recipe_walk.events`, each with the timeline path and the count behind it, plus the maximum share any one signature reaches in an approved cut (the number M46 will lean on). The test asserts the mix is re-derivable (re-running the deriver reproduces the file byte for byte) and that no skeleton emits a 9:16 rail or park.
- Validate: `python -m pytest content/video_engine/tests/test_shape_skeletons.py -q`
- Evidence: 13 skeleton files under `effects/skeletons/` (open-on-the-chart 2, page-number-lands-at-n 2, held-page-hosts-the-docks 2, plate-carries-a-card 2, page-to-page-transform 2, return 3), each citing a line inside an approved `shot_table` (two cites corrected: the Japan card `:279-281`, the memory suck `:211-213`; Japan `:174`'s 'returns by the spiral' is stale - its ring mounts a new page at `:313`); `approved-mix.json` MEASURED on the compiled timelines by `scripts/derive_approved_mix.py` (Tokyo 7 scenes, Japan 12; max share 0.3333; one-shot #3 beside, approved: false); `tests/test_shape_skeletons.py` 128 passed (the parent re-ran it). For T5: the approved cuts carry consecutive repeats (Japan's throw -> snap pair reads card, card), so M46's consecutive rule counts SKELETONS, not signature words.

### T3: `authoring/shapes.py` - the beat plan in, the approved skeleton out
- Status: done
- Owner: `implementation_luna`
- Depends on: T2, T7 (the Tokyo bed's beat plan is the test's input)
- Write set: `content/video_engine/scripts/authoring/shapes.py`, `content/video_engine/scripts/authoring/__init__.py` (the export line only), `content/video_engine/tests/test_authoring_shapes.py`
- Acceptance: `shapes.compile(plan, words, defaults, aspect)` returns the rows in the kit's grammar (tuples, `table.write_shot_table`'s input) plus a per-row `why` record (skeleton id, the act that chose it, the rule that applied). `shapes.choose(beat, history)` picks among the skeletons for the beat's shape by the sentence act and refuses the previous beat's signature (the variety rule), falling back in a documented order when only one is left. The approved shape is enforced by construction and asserted in the test on the Tokyo bed's plan: beat 1 is a page on its axes; a page whose number lands >= 7.0 s after entry gets `mount=<s>` and never `built`; a world change exits `dip`, page to page `suck`/`cut`, never into a mount; a return uses `spiral`; a plate row is never under 6 s; at 9:16 no `badges` rail and no `chart_to park` is emitted; a light is emitted only on a POINTING sentence and never before `PAGE_BUILD_END_S`. A plan that M41 would FAIL (a beat with no record, an empty comparator, a null recipe with no `why_none`) is REFUSED by name - the module never invents a beat. The module docstring carries the doctrine sentence with its citations (`recipes.py:1-20`, `PIPELINE.md:33`, E99 s68). The module names no episode.
- Validate: `python -m pytest content/video_engine/tests/test_authoring_shapes.py -q`
- Evidence: (third pass, 2026-09-17, after the compiled base's rows) a card that names no `centre_*` is placed in a room of the PAGE's own - `ledger_page.page_boxes` (the plot's empty rooms plus the bands outside it cut at every line of ink), at the `quiet_zone` end the token names, sized for a square card, never a box another live card holds, no `read` (a centred card with no read has no 800 px pop), dropped when no room exists (never the stage's centre over a page); a card leaves at the page's next `chart_to`; the light-after-build clock binds spotlight and focus_zoom only, a `build_to` on the open ends ON the landing (the annotation M11 counts, P47 T2) and `drop_flashes` mirrors the compiler's HOLD_MIN_S so the base never claims a light the cut loses. The base rebuilt (`p66-hg1-base-v2`): M11 FAIL -> PASS, M25 29 -> 11 faults (the eleven are the read-back plan's own docks: a 1.8-aspect chart card on a bars page with no room, and a card landing after a rescale whose state has no mask - the approved cut carries both `moving`), M27 1, M10/M16/M28/M34/M35/M39 the plan's and the bed's; M45 9 present / 2 not owed, M46 PASS. 118 tests. `shapes.py` 1294 lines - a split rides R26-182's row. Earlier: `authoring/shapes.py` (712 lines: `compile(plan, words, defaults, aspect) -> (rows, why)`, `choose`, `groups`, `check_plan`, `event_gaps` MEASURED never filled, `DEFAULTS`, gate constants imported), the `__init__` export, `tests/test_authoring_shapes.py` 26 tests; the kit's module pin moved by the parent (88 + 26 pass). The Tokyo base: 5 rows (`mount, card, spiral, cut, hold`, no skeleton twice running), the Japan plan compiles and round-trips. FINDING (the parent, 2026-09-17): one skeleton row per authored group leaves a long group with one event - M16 gaps to 32 s on the Tokyo base. The base must realise each BEAT's named moves, so RESOLVED (second pass): a plan record may carry `moves: [{kind, at_word, target?, label?, dur?, asset?}]`, realised as species and docks on the group's row at the word's instant, the rules still enforced (an early light or a phrase not in the sentence is refused by name); silent beats are named in `why`; `event_gaps` stays measured. `scripts/derive_beat_moves.py <build> [--check]` writes the moves the APPROVED cut actually carries into a read-back plan (transcription): Tokyo 15 of 25 beats carry moves, Japan 13 of 25; `--check` in sync on both; M41 PASS on both. Tokyo's base: max gap 32.0 s -> 9.86 s (3 -> 24 species, 3 -> 6 cards, the same five rows and skeletons); Japan 9.10 -> 8.16 s. 97 tests pass (the parent re-ran). Deviation accepted by the parent: an AUTHORED `snap=`/`camera=` entry stands when the plan's first light is spoken before the clock's own entry would finish drawing - the compiler never overwrites an authored entry to manufacture a rule violation.
- Evidence (E99 s70 pass, 2026-09-17): the vocabulary rebuilt FROM THE RECORD - 20 words (axes, mount, spiral, snap, throw-then-zoom, throw-then-push, door, suck, dip, cut, card, hold, rescale, recast, park, unpark, melt, morph, remake, object-becomes-chart), each with `record=` (a CAPABILITIES row or ruling line) and `cut=` (a shot-table line) the test greps; 22 skeletons (11 new; morph and remake declared but no approved table plays them as a beat - no skeleton invented); a `chart_to` renders its `;then=` chain and `states` or is refused: Tokyo's rescale (b8) and two recasts (b15/16) now render (`world.page_states` on the compiled base); M46 counts the vocabulary. 441 tests. THE PARENT'S READ of base v3 beside the approved cut at nine instants (`build-p66-base/s70-sheets/`): the rescale, the recast and the spiral bracket are real; still wrong - the open is bare cream (the hook's clip world dropped under the mount), the recast at 52 s lands fully built (s67), the approved cut PARKS the page to make room for its cards at 56.7/57.5 s while the base drops cards over the ink (R26-172 WITHDRAWN - the park is how a page makes room), the retitle on 'The opponent' is dropped, the camera-on-a-dock entry at 77.8 s renders a blurred page with no card. Not carded; the fourth pass owns those five.
- Evidence (fourth pass, 2026-09-17): the open keeps the hook's clip world and the page mounts over it at 1.78 s; the park restored (R26-172 withdrawn) - at 56.72 / 57.52 s the base's parked plot box equals the approved cut's (146,481 344x262) with both cards in the freed band, M25 14 -> 1; the retitle lands ('The opponent: a balance sheet' at 50.30 s; the deriver carries a pre-scene species to its scene's start); the camera-on-a-dock entry renders the Fed page with its ring at 77.80 s and a camera whose card no row carries is refused. 388 tests; `build-short/BEAT-PLAN.jsonl` re-derived. THE PARENT'S READ of v4 beside the approved cut (`s70-sheets/base-v4-vs-approved-diff.md`): nine of eleven instants the same, one a row boundary (64.39 s), ONE defect left - at 52.00 s the recast lands all four bars built (279/107/391/154 px) where the approved cut grows Mar alone (200 px): the compiler emits the approved table's plain hand-over (`keyed: false`) and `build_scene_timeline_f.py:2610` derives `keyed: "data"` because it reads `sp.get("keyed") or None` and cannot tell an authored false from an absent key. The parent's decision: an authored `false` is the author's explicit hand-over and is RESPECTED; the derivation runs only when the key is absent (E64 speaks to the absent case; s67 Apply 2 binds the landing) - one guarded line in the timeline compiler, dispatched, with the goldens as the net.
- Evidence (v5, 2026-09-17, after the engine's keyed-false line 290e82a): the parent probed the recast at 51.7 / 52.0 / 52.6 / 53.4 s (`s70-sheets/base-v5-recast.png`): empty axes, March alone, three bars, all four with the -$26.4 badge arriving - the recast BUILDS as the approved cut does (E99 s67 Apply 2). Ten of eleven instants read the same as the approved Tokyo cut; the eleventh (64.39 s) is a row boundary. v5 exits 8 FAIL / 5 WARN on the motion gate (M16's silent-beat gaps, M35/M39 the bed's shape, M25 1) - the base is offered for a watch, never judged by the gate (E99 s38). The base returns to the queue with a critic (T7's rule) for the operator's second read.
- Evidence (fifth pass + the runtime wire, 2026-09-17): a card after a camera push keeps the page's room - E65's room now counts the marks the row itself writes (`marks_live` drops the plot's holes, `quiet_live` the quiet-zone band); row 6 gains the placer's park (0.52 at 78.63 s) and at 79.50 s the probe reads the tea-cup card parked [545,914,320,204] beside the plot [153,568,305,278] and the note, overlaps none (v5: inside the plot, over the callout's label). The closing row: `shapes.close_the_cut` holds the plan's closing world (else the last row) to the build's runtime with its idle - the CLI now hands `runtime=read_runtime(build)` (the parent's one line; the lane's write set had excluded `generate_base_table.py`); 141 + 78 tests; base v7 rebuilt for the tail's read.
- Evidence (v7, the parent's read of the tail, 2026-09-17, `s70-sheets/base-v7-tail.png`): at 79.5 s the Fed page is PARKED top-left with its note beside it, the ring on 3.97 %, the tea-cup card in the room below; at 82.9 s the card has left; at 85.5 and 88.5 s the page holds with a visible idle - M05 PASS (live across the hold), M01 PASS; M16 names the 6.1 s after the last word, the base's last silent beat (`why`: the outro is the author's - the approved cut ends on its outro clip). v7: 7 FAIL / 5 WARN, the FAILs the plan's silence and the bed's shape. THE BASE RETURNS to the queue as a new card for the operator's second read, with the v5 critic's fractions (10/11, 5/6) and the note that its two first rows are fixed on v7 by the parent's probe.
- Evidence (sixth pass, E99 s72 Apply 6, 2026-09-17): the inks are decided in the EPISODE's series file and resolved by the player's `LP_INK` (`crimson` -> the Claude orange `#FF8A4C`, E67) - there is no `ink=` plate option and the compiler never rewrites a bed's series (s11); the base's holdings page reads live `#FF8A4C` with the 0.35 bloom and a same-hue 0.45 history on the DOM at 21.1 s, so the pages were E67 already and the compiler now NAMES each page's inks in `why` and WARNs a palette LP_INK cannot resolve or an all-`deemph` page. The cues: the bed's map read `:cut` off the raw plate id (every base page carries `;idle=live`, so no page read as a cut) and played a page-roll at any entry that is not a mount or a spiral - five cues marked nothing (the whirl and the two flips the operator heard, two roll-outs on axes/camera entries); `authoring.audio.bind_cues` (off `recipe_walk.events` + `world.page.enter/exit`) only ever REMOVES a cue the frame does not play - 11 -> 6 cues, 6 of 6 firing, three unmapped instants named never filled (s37); the approved cuts' maps byte-identical. The outro: `shapes.close_the_cut(..., outro=)` closes the cut on the project's own outro row (row 7 = 82.62 -> 88.82 `outro-v2.mp4`, `dip`, `life` 6.20 s; row 6 trimmed to 82.62; brand line stitched at 83.42 s) resolved by `generate_base_table.outro_resolver` reading `build_short.py` with `ast`, never running it; `check_outro` refuses a missing world/at/runtime or an outro that swallows the row before it. 170 tests (30 new). THE PARENT: the lane bound the cues from the outside (`--bind-cues`) and every `--table` rebuild re-embedded the five - `lab_build.bind_embedded_cues` now runs after the embed in table mode (v9 rebuild: `9 embedded` -> the same five DROPPED and named, the timeline and the private plan carry 6); `test_lab_build.py` moved to the current doctrine (seven rows with the outro; no dip before the snap, fd2861b). The parent's read of `s70-sheets/base-v8.png` (0.2 / 21.1 / 45.2 / 82.9 / 88.5 s): the hook's clip world, the orange holdings line with its panel card in the page's room, the spiral page 0.2 s into its unwind, the outro card dissolving in over the dip, the outro built with the triad and the handle - v7 froze the Fed page across the last two. Not carded: s72 Apply 6 judges the next base on the calendar cut's plan, and s74 (2026-09-17) reorders what the compiler reaches for first - the transforms before any cut or dip; the seventh pass owns that chooser (R26-189).
- Evidence (seventh pass, E99 s74, 2026-09-17): THE FINDING FIRST - the engine reads a row's transition column as the move INTO that row (`build_scene_timeline_f.py:2185` "exit names the transition INTO the scene it sits on"; `:5030`), and every earlier pass wrote it on the OUTGOING row: base v9 played a dip INTO its mount and dropped Tokyo's own suck, and the door could never fire (its token was offered as the plate's exit into the world after it, where "never into a mount" threw it away). Fixed: the chooser decides the boundary INTO each row, `_windows` reads the same index. `choose_transition` per pair with the refusal chain in `why` (rung 0 the plan's own arrival - mount, snap, camera, spiral, axes - is a cut; page->page recast, rescale, morph REFUSED "no approved skeleton", melt:splash:chart; page->plate melt:splash:plate, the door where the page arrived by snap/camera, the suck; plate->page the arrivals; plate->plate the continuity three named, then the dip - the pair E47 is for); `flow_count`/`flow_line` under the mix (R26-189's read, no gate). Tokyo read-back: dips 2 -> 0 (row 2 `melt:splash:plate` where the cut sucks), Japan dips 5 -> 1. `lab_build --table` generalised to the table's own bed (five reads off the bed; the candidate lab keeps its one bed); the outro reader resolves a constant built off an earlier one (`SIBLING /`). THE CALENDAR BASE (`memory-trades-the-calendar/build-p66-cal/`, v2): `flow: 11 world changes - transforms 3 (melt 2, suck 1), arrivals 5, last resort 3 (dip 2 + the outro); cuts+dips 8` vs the cut's 11; M45 9 present / 1 replaced (the mount); M46 WARN axes 0.42 with consecutive axes 4-5, 5-6; 280 tests. THE PARENT'S READ of `s74-sheets/cal-base-v2.{1,2,3}.png` beside `cal-approved-same-instants.{1,2,3}.png` (35 instants): the melts are real - at 9.50 s and 58.22 s the ink balls up on the board (E88) where the cut went to black; the suck at 48.42 lands the dock plate; the outro stands. FOUR DEFECTS the lane's table did not name, all from one cause: the compiler STRETCHED the narrative plates toward M44's six-second floor (row 7 `plate-dock` 1.28 s in the cut -> 6.00 s; row 10 `plate-customs` 3.28 s -> 4.98 s), which (1) pushed the chip-price page from the plan's 49.70 s to 54.42 s and squeezed it to 3.2 s, so it lost its docked plate card and its "-14% in two weeks" span (M37 FAIL is this), and (2) left the ring's page 1.5 s (69.62-71.12) where the cut plays 3.6 s - the spiral is still turning at 70.82 s when "trade it" lands; (3) the spiral return passes through BARE CREAM at 69.62 s before the board falls in (the cut's board is there at 69.32); (4) the coin-flip page's card is still leaving at 41.16 s over the next page's title. Also to verify: at 64.64 s the cut's frame reads as a cross-fade of the two plates and the base's as black under the same `dip` token. RULED by the parent for the eighth pass: a gate GUIDES (E99 s69) - the compiler never steals a page's seconds to lengthen a plate; the plan's windows stand and a plate under M44's floor is NAMED in `why`; an arrival keeps its lead (the spiral's unwind before the sentence); a card completes its leave before the boundary; no bare cream at a world change. Not carded until the eighth pass' sheets are read.
- Evidence (eighth pass, 2026-09-17 - the seventh's review fixes + the parent's ruling): A1 the variety rule DEFERS inside the chain (a refused melt falls to the door, then the suck, never straight to a dip; the `why` names the world change it compares against by index and instant); A2 `door_dock_error` mirrors the engine's `door_boundary_error`, a TAKEN door lands on the plate row; A3 `bed_output_dirs` refuses the bed's own approved build dir (`build-oneshot-3`) by name; A4 two tests repaired to their names; A5 the Tokyo base rebuilt (v11 exits None, cut, melt:splash:plate, cut, cut, cut, dip). B1 THE COMPILER NEVER STEALS: `MIN_ARRIVAL_S` and the M44 branch are gone from `_windows`; a row's window is the plan's own and a plate under the floor is named in `why` - the calendar base's row 7 back to 48.42-49.70 (1.28 s), row 8 the chip-price page back to 49.70 with `dock-g-july-host` at 52.08 and its `span` at 51.80 (M37 gone), row 11 the ring's page 3.76 s; M44 now WARNs four plates, which IS the ruling. B2 the spiral's 1.60 s lead is taken from the narrative plate before it (row 11 opens at 67.36 for the sentence at 68.96; the cut's own s11 opens at 67.82). B3 not a defect against the cut: the cut's own boundary frame is cream (mean 220) - the board falls in over cream before the spiral in both. B4 the coin-flip card's leave is over before 41.16 (`cards[-]` at 40.86/41.16). B5 not a defect: both boundary frames read black at +0.00; the parent had compared +0.00 against +0.10. THE PARENT'S READ of `s74-sheets/cal-base-v3.*.png`: at 57.62 the chip-price page carries the "-14% in two weeks" span and the +16.4% callout; at 58.22 the ink balls up; 67.80 the board falling in, 68.40 the spiral turning, 68.96 the chart built as "calendar: the" lands, 70.82-71.00 the ring on the last point under "trade"; the outro at 71.72 and 76.64. `flow: 11 world changes - transforms 3 (melt 2, suck 1), arrivals 5, last resort 3 (dip 2 + the outro); cuts+dips 8` vs the cut's 11. 603 tests. The remaining FAILs are the plan's (M16 two silences, M25 one label at 10.5 px, M28 the weak-prints page's labels at 0:44) - a base is offered for a watch, never judged by the gate (E99 s38).
- Evidence (ninth pass, 2026-09-17, after the director-critic's read of v3 - `build-p66-cal/CRITIC.md`: mechanisms 9/11, signature words 4/5; INFO 1 the plan's only MOUNT compiled as an axes cut with no departure line, INFO 2 the compare melt at 29.12 absent): (1) ANY authored entry stands (`mount=`, `snap=`, `camera=`, `:spiral`, `:axes`) - the compiler's landing clock holds a light or a figure to the entry's landing instead of rewriting the entry (`HELD_TO_THE_LANDING`); where an entry's own rules refuse it, a `BASE DEPARTURE` line names the plan's token and the reason and M45 reads `replaced` WITH the reason - the calendar base's row 4 compiles `mount=0.79` over the desk plate, M45 PASS 10 present / 1 not owed / 0 replaced, M46 axes 0.33 (the three consecutive axes gone); (2) a park never covers a transform the plan names - the card leaves at 27.92 and the un-park lands at 29.12 (`test_a_park_never_covers_the_transform_the_plan_named`), no park inside [29.12, 30.02]; THE MELT STILL DOES NOT PAINT, and the cause is measured and is not the park: the engine's `paintCompare` (`scene-evidence-engine.mjs:10460`) returns unless the figure it morphs carries a `label`, and the `figure +6.8%` on row 4 carries none - the calendar cut itself has the same figure and the same silence at 29.12, so its compare melt was never real (BACKLOG R26-190; the tenth pass hands the metric's label to the figure). Rows 7/8/10/11 unmoved; flow unchanged (cuts+dips 8); 363 tests. Deviations: the lane's first generate omitted `--table` and wrote the PROJECT's approved table, restored with git at once (the second time this hazard has bitten - the bare form now refuses when the project's table exists, tenth pass); `approval-rates.*` timestamp restored. THE PARENT'S READ of `s74-sheets/cal-base-v5-mount-melt.png`: 16.60 the desk plate; 16.90 BARE CREAM with the caption (the mount's boundary - the cut's own 16.91 frame is the same); 17.50 the soak's charcoal stains growing; 18.82 the page built with its two bars; 28.82-30.40 the bars page with the FRONT-RUN 3x card already docked and nothing moving - the compare's silence, INFO on the card. The bare cream at a plate->page mount is the soak entry's own canvas (E99 s35) and the cut plays it too - named on the card, not fixed here.

### T4: The CLI, `BASE-TABLE.md`, the departures reader, and HG1's queue row
- Status: done
- Owner: `junior_developer`
- Depends on: T3
- Write set: `content/video_engine/scripts/generate_base_table.py`, `content/video_engine/tests/test_generate_base_table.py`, `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: `generate_base_table.py <project> <build>` writes the generated rows through `table.write_shot_table` and `<build>/BASE-TABLE.md` (per row: the skeleton, the act, the rule; then the cut's signature mix beside `approved-mix.json`'s). It refuses to overwrite a table file newer than the plan unless `--force "<reason>"` is given, and the reason is recorded in `BASE-TABLE.md`. `--departures` re-generates the base, diffs it against the build's current table and `overrides.json` (through `table.load_rows` and `table.apply_sidecar`), prints one line per departure (row number, field, base value, final value) and exits 1 naming any departure with no matching row in the project's `PRODUCTION-LEDGER.md` "Decisions taken without the operator" section, matched on the fixed format `N. BASE DEPARTURE - row <n> <what changed>: <why>, <ruling or path:line>`. The test covers: a clean build (exit 0), one undocumented departure (exit 1, named), one documented departure (exit 0), a missing ledger section (exit 1 saying so). The same change adds the HG1 queue row (kind `watch`, a clip proof and the frozen player link, `blocks` naming T5's thresholds and the Opus one-shot); if P67 T5 has landed by then, the card carries the `critic` path a whole-cut watch owes (a `reviewer` pass on the generated base - the blueprint's order puts P66 before P67, so normally it has not).
- Validate: `python -m pytest content/video_engine/tests/test_generate_base_table.py -q` then `python content/video_engine/scripts/build_review_queue.py --check`
- Evidence: `scripts/generate_base_table.py <project> <build> [--table PATH] [--aspect] [--force "<reason>"] [--departures]` + `BASE-TABLE.md` (per row the skeleton/act/rule, the silent beats, the mix beside the target); `--departures` diffs the current table + `overrides.json` against a fresh base and exits 1 on a departure with no `BASE DEPARTURE` ledger row; 15 tests (49 with the queue's); the real base on the Tokyo bed in `build-p66-base/` (5 rows, 10 silent beats, mix card/cut/hold/mount/spiral 1 each), byte-identical, `--departures` CLEAN. The queue record `p66-hg1-the-first-generated-base` (kind watch, a player proof on :8769 unconfirmed until the parent serves it); `build_review_queue.py --check` ok. Deviation accepted: `--table PATH` was added and used because the bare form would have overwritten the APPROVED `SHOT-TABLE-SHORT.py` (the newer-than-plan guard does not fire on a copied plan) - the tool must never write the approved table; `build-p66-*/` gitignored by the parent.

### T5: M45 parity by mechanism and M46 signature variety
- Status: done
- Owner: `implementation_luna`
- Depends on: T2 (the mechanism list and the measured mix), T7 (the approved cuts' beat plans - M45 is read against a plan); the thresholds confirmed by HG1, written first as a named constant
- Write set: `content/video_engine/scripts/gate_one_shot_floor.py` (M45, M46, `ROW_ORDER`, their `SRC_` constants), `content/video_engine/tests/test_gate_one_shot_floor.py`, `docs/GATES-REGISTRY.md`, `docs/GATES-REGISTRY.jsonl`
- Acceptance: **M45** prints one line per approved mechanism (the nine of Acceptance 5, the list derived in T2 from the approved tables, never typed twice): `present` (with the instant), `absent`, or `replaced by <mechanism>` (a mechanism the cut does carry in that beat's place). A mechanism absent with no replacement FAILs naming it; a replacement WARNs naming both. **The list is read against the cut's own beat plan, never as a fixed checklist**: a mechanism is OWED only where a beat's shape calls for it (a return beat owes the spiral; a page whose number lands 7 s or more in owes the mount; the first beat owes the page on its axes; a world change owes the dip), and a mechanism no beat calls for prints `not owed`. Measured on the reference first (memory `thresholds-from-the-reference`): the approved Japan and Tokyo cuts must read `present` or `not owed` on every line before the row is turned on, and a fixture pins that. E99 s67 Apply 7 and R26-177 are its `SRC_`. **M46** reads the cut's signatures from the compiled timeline with `recipe_walk.events`, prints the mix beside `approved-mix.json`, and WARNs on a signature over the approved maximum share or on two consecutive identical signatures; it never FAILs (variety is a JUDGE-adjacent measure, and E96's rule that a rate is never a floor holds). Both rows join `ROW_ORDER` after M42 and appear in `SELF-WATCH.md` section 1 through the existing bar. The fixture asserts the rows on the approved Japan and Tokyo cuts (M45 all present) and on `build-oneshot-3` (the regression: the mechanisms E99 s67 named, absent). `build_gates_registry.py --write` regenerates both registry files.
- Validate: `python -m pytest content/video_engine/tests/test_gate_one_shot_floor.py -q` then `python content/video_engine/scripts/build_gates_registry.py --check`
- Evidence: `gate_one_shot_floor.py` M45 (the eleven-mechanism list `MECHANISMS_2026_09_16` shared with CRITIC-REPORT.md; owed from the beat plan; present read from `recipe_walk.events`) and M46 (the deriver's classifier; `M46_MAX_SHARE = 0.34`; consecutive repeats the approved mix itself records are exempt); `ROW_ORDER` after M42; 53 tests pass (the parent re-ran); registry `--check` in sync (165 records; both registry files are gitignored build output). Measured: Tokyo `9 present, 2 not owed`, M46 PASS; Japan `7 present, 4 not owed`, M46 PASS; `build-oneshot-3` (the rework) `10 present, 1 not owed, 0 absent`, M46 WARN on two consecutive repeats (scenes 2-3 dip, 5-6 axes). Two readings the reference decided: mechanism 4 is owed only where the plan's row says `:axes`; mechanism 9 does not re-check M44. The parent widened `self_watch.py`'s `FLOOR_ID_RE` to M46 so the rows reach SELF-WATCH.md section 1 (24 self-watch tests pass).

### T6: Doctrine - the runbook's step 5, the capability row, the backlog, the layers
- Status: running (HG1's answer owed; the card is complete)
- Owner: parent
- Depends on: T4, T5
- Write set: `docs/runbooks/ONE-SHOT.md` (step 5 at `:41` and its Check column), `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/PIPELINE.md` (the one sentence under "Stage 7 is AUTHORED"), `docs/content-video-engine/BACKLOG.md` (R26-180, R26-177), `docs/portable/OPERATOR-RULINGS.md` (HG1's answer), this plan's status, the generated docs layers
- Acceptance: step 5 reads "generate, then modify - and name every departure", with `generate_base_table.py` in the Do column and `--departures` plus M45/M46 in the Check column; the "no allocator" paragraph in `PIPELINE.md` gains ONE sentence citing E99 s68 - the compiler consumes an AUTHORED beat plan and emits a base the author edits; it fills nothing by count. `CAPABILITIES.md` gains THE SHAPE COMPILER row (the module, the CLI, the skeleton library, the two gate rows) and `docs_find.py "shape compiler"` finds it. R26-180 carries its verdict in bold with the paths; R26-177's parity half is marked done by M45 (its step-0 recall half stays open for P67). HG1's answer is written into the rulings and into this plan. `build_docs_layers.py --check` reports every layer in sync.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check` then `python content/video_engine/scripts/docs_find.py "shape compiler"` then `python scripts/prp_validate.py .claude/PRPs/plans/P66-THE-SHAPE-COMPILER.plan.md`
- Evidence: ONE-SHOT.md step 5 now reads GENERATE, THEN MODIFY - and name every departure (the command, the two doors, the ledger row format, `--departures` + M45/M46 in the Check column); PIPELINE.md "Stage 7 is AUTHORED" gains the one E99 s68 sentence; CAPABILITIES.md gains THE SHAPE COMPILER row after the kit's (`docs_find.py "shape compiler"` hits it); BACKLOG R26-180 BUILT (closes on HG1), R26-177's parity half DONE; the layers rebuilt (`build_docs_layers.py --write`, exit 0). HG1's answer into the rulings and this plan: owed.
- HG1 on the queue (2026-09-17): `p66-hg1-the-first-generated-base` - the base rebuilt after the compiler's third pass, served on :8769, its critic 10/11 and 4/5 as INFO with the three rows first (the 2.6 s open on bare cream; the spiral return on the full scale making the bracket a sliver and two recasts that render nothing; the fed-vs-yields chart card thrown full-frame - the read-back plan's own `camera=<dock>`, what the approved Tokyo cut did before E99 s67).

### T7: The Tokyo and Japan beat plans, read back from the approved cuts
- Status: done
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short/BEAT-PLAN.jsonl`, `content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short/BEAT-PLAN.jsonl`
- Acceptance: no `BEAT-PLAN.jsonl` exists for either approved short today (only `memory-trades-the-calendar/build-oneshot-3/` and `ai-slower-useful-faster/build-private/f/` carry one), and the compiler, its test and M45's calibration all take a plan as input. The parent writes both in M41's schema (one record per sentence of the approved take's `timeline.json`, `t0` = the sentence start, `comparator.compared_to`, `capabilities[]`, `recipe|why_none`) by READING THE APPROVED CUT BACK, sentence by sentence, and marks every record `source: "read back from the approved cut (P66 T7)"` - a description of what the cut did, never a plan for a rebuild (E99 s11's practice: the approved cuts are not rebuilt). `gate_one_shot_floor.py` M41 reads PASS on both. This is intelligence work (E99 s66) and stays with the parent.
- Validate: `python content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short` and the same on `japan-tariff-trick/build-short` (unpiped; M41 PASS on each)
- Evidence: `tokyo-tea-break/build-short/BEAT-PLAN.jsonl` (25 records, 3 with a recipe) and `japan-tariff-trick/build-short/BEAT-PLAN.jsonl` (25 records, 19 with a recipe), sentences from `lint_species_choice.load_sentences(timeline.json)` - the gate's own loader; every record `source: "read back from the approved cut (P66 T7)"`. `gate_one_shot_floor.py` on each: `[PASS ] M41 the beat plan covers all 25 beats (25 records), each with a comparator and a recipe or a why_none` (Tokyo's M35/M38/M39 FAIL pre-exist on that dir - PREDATES_E96 pins `build-short.v2`; nothing touched). The parent reviewed the 19 uncertain records (report `scratchpad/assembly/P66-T7.md` s A-E) and kept them: twelve sentences carry none of the acts and say so (`act: "none of the 11 - <what it does>"`) rather than a forced name - the compiler chooses those beats by SHAPE and position (T3); the two Japan records describe the approved 09-10 timeline, not the 09-11 script; the Tokyo 16 burst is attributed to the row's note, not asserted.
- Deviation: the draft was written by `implementation_luna` from the approved timelines and tables and every record was reviewed by the parent (the 19 it flagged individually); the intelligence stayed the parent's, the transcription did not.
- Evidence (extended, 2026-09-17 - the operator: "using the japan short version where we implemented the door originally might be better, since it has more recent mechanics and includes more of our polishes"): `japan-tariff-trick/build-p58-door/BEAT-PLAN.jsonl` - 25 records read back from the DOOR cut (E98 s7), 13 with derived moves; beat 12 the receipt page SNAPS up from the landed card (`build_short_door.py:34`, the arrival pinned to snap), beat 15 the world changes by THE EVIDENCE DOOR - `door:right` onto `plate-vault` (`:43`, `:59`; timeline s07); `--check` in sync; M41 PASS 25/25; M45 7 present / 4 not owed / 0 absent; M46 reads `door 0.08` - the vocabulary's door word on a real cut. Two stale `exit:dip` fire members corrected on beats 1 and 10. The door cut is the compiler's reference and the lab's second bed from here; the Tokyo read-back stays the regression test.

## Verification

- Unpiped, from the main checkout: `python -m pytest content/video_engine/tests/test_shape_skeletons.py content/video_engine/tests/test_authoring_shapes.py content/video_engine/tests/test_generate_base_table.py content/video_engine/tests/test_gate_one_shot_floor.py content/video_engine/tests/test_authoring_kit.py -q`.
- The blast radius: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and
  `python content/video_engine/scripts/sync_kinetics.py --check` pass unchanged; no engine, compiler or golden file
  is in any write set.
- The real proof is a build: `generate_base_table.py` on the Tokyo bed's plan into a PRIVATE build dir, then
  `gate_motion_density.py`, `gate_one_shot_floor.py` and `self_watch.py` on it - the base must come out gate-clean
  on M11 / M12 / M16 / M25 / M44 and `present` across M45 before it is offered for HG1.
- `python content/video_engine/scripts/build_gates_registry.py --check`;
  `python content/video_engine/scripts/build_review_queue.py --check`;
  `python content/video_engine/scripts/build_docs_layers.py --check`.
- `python scripts/prp_validate.py .claude/PRPs/plans/P66-THE-SHAPE-COMPILER.plan.md`; `python scripts/prp_status.py`.
- Risks named: (1) **templated reads as templated** - the plan's own central risk; the mitigations are several
  skeletons per shape, the variety rule, M46 and HG1's read, and if the first base reads templated the answer is
  more skeletons (a data change), never a looser gate; (2) the skeleton library is derived from three cuts, so it
  inherits their blind spots - P65's lab is the widening path and T1 says a new skeleton is a file; (3) the
  compiler could become an allocator by drift - the refusal on an incomplete plan, the absence of any count-driven
  mode and the docstring's doctrine line are what hold it, and the test asserts the refusal; (4) M45's mechanism
  list is a judgement about what the approved cuts did - it is derived in T2 with `path:line` cites so it can be
  argued with, not re-remembered.

## Evidence And Handoff

- Per-slice reports under `scratchpad/assembly/P66-T<n>.md`: changed files, the validation command, its verbatim tail.
- HG1's artefacts: the generated base's `BASE-TABLE.md`, the built cut's `SELF-WATCH.md` with M45 / M46, the frozen
  player link and one clip - the operator reads a visible difference, not a diff (E99 s38).
- Commits by the `release_steward` from the main checkout, allowlisted paths, `Recall:` lines on every mechanism
  file; P66 T5 lands before P65 T7. Nothing pushed without the operator's word.
- Handoff: the Opus one-shot (E99 s66 step 2) runs on the compiler's base, then Astra's in its own worktree (P62);
  P67 adds the verified recall receipt and the director-critic over the same loop.
