---
id: P65-THE-RECIPE-LAB
title: The recipe lab - the finite combination space enumerated as data, built as real beats on the Tokyo bed, filtered by the gates and the probe, presented to the operator AS BATCHES with approvals AND denials tracked (the bit, a reason category, the instant of proof, a timestamp), learned as a per-feature approval-rate table, promoted into proven recipes and the kit's DEFAULTS - and the fifteen proven recipes re-proved on today's clocks (R26-168)
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# The recipe lab

## Summary

E99 s68 (2026-09-16), the operator on how the combination knowledge gets built: *"C but we should present as batches,
and track approvals and denials so agents can start learning what make combinations work."* R26-176 names the space
and says it is finite: **beat shapes x the catalogue's members x the gates' clocks** (M44 6 s plate, M16 2.5 s event
gap, M12 6 s chart dock, M11 1.5 s first light, `PAGE_BUILD_END_S` 7.4 s). The blueprint's decisions 3 and 4 fix the
method: build each candidate on the test bed, keep what passes the gates and the probe, present the survivors as
batches - one card per beat shape, candidates side by side, about a quarter of each batch drawn as exploration
regardless of predicted approval, older approvals returning as calibration probes - and log each judgement as four
fields, never a bare bit (Gao et al. 2022: optimising an imperfect proxy at small N hurts ground truth).

The second reason this plan exists is R26-168: **the floor and the proven set contradict each other.** One-shot #3
planned every beat and measured `M38 0.03`. `card-becomes-the-chart` is proven on a 3-5 s plate and M44 now asks six;
`emphasized-bar-lit` is proven on a light 7.55 s after a build and E99 s67 wants the page lit as it builds; the badge
ladder's rails are illegible at 9:16 (R26-171). Fifteen recipes are `proven` against clocks that no longer exist. The
lab is the only machine that can re-prove them, so this plan owns both: the machine, and its first job.

What the lab is NOT: an author. `authoring/recipes.py`'s header ("NOT AN ALLOCATOR ... this module returns
CANDIDATES ... the AUTHOR binds") and `docs/content-video-engine/PIPELINE.md:33` ("Stage 7 is AUTHORED. There is no
allocator") both stand. The reconciliation is explicit and it is the plan's spine: **the lab enumerates candidates for
the operator's judgement on a TEST BED; it authors no episode, it fills no slot by count, and nothing it emits reaches
a cut except as a `proven` recipe or a tracked DEFAULT that an author may still refuse.** A candidate is a beat, not a
fixture: E99 s60 - a proof is a scene, and a candidate's clip must be a beat a short could carry.

All repo paths are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`).

### Recall (2026-09-16, `docs/runbooks/RECALL-RECEIPT.md`)

- Recall: `docs/content-video-engine/GRILL-AGENTS-HARNESS-EFFECTS-2026-09-16.md:20-28` (decisions 3 and 4 verbatim),
  `:54-55` (gotcha 5: *"the lab re-proves the recipes on six-second plates and built pages before M38 is held at 0.60
  again; until then M38 prints its number and the parity row (M45) is the floor"*), `:58-61` (the build order).
- Recall: `docs/portable/OPERATOR-RULINGS.md:3254` (E99 s68, Q2 and Q5 verbatim), `:3252` (s67: the page BUILDS then
  holds built; a dock is an evidence still, never a chart card; the open starts ON the chart), `:3250` (s66: the beat
  plan is intelligence work, never a tool's).
- Recall: `docs/content-video-engine/BACKLOG.md:600` (R26-168, the three named contradictions), `:608` (R26-176 with
  its ruling in bold), `:603-604` (R26-171 rails, R26-172 park - the 9:16 defaults the lab promotes).
- Recall: `content/video_engine/effects/recipes/` = **45 files, 15 `proven`**; the schema is
  `content/video_engine/configs/effect_recipe.schema.json` (`effect_recipes.v1`; `status: proven` REQUIRES `proof` and
  `count >= 1`, `candidate` FORBIDS a proof - P56 T1). The catalogue `docs/EFFECTS-CATALOG.jsonl` is BUILD OUTPUT
  (`build_effects_catalog.py --write`, P63: never hand-edited).
- Recall: `content/video_engine/scripts/build_review_queue.py:47-56` - `KINDS = (watch, look, rule, approve, owed)`,
  `PROOF_TYPES = (clip, player, crop)`, `REQUIRED` twelve fields, `PROOF_FIELDS["clip"] = (label, t0, t1, route)`;
  `:100` refuses an open watch/look with no proof; `:94` refuses `"other"` in `options` (it is always offered). The
  page rules nothing: answers land only through `serve_review_queue.py` POST /answer into
  `docs/content-video-engine/review-answers.jsonl` as `{item, choice, note, at, by}` - and that file already carries
  **two answers under one item** (`r26-133-drift-idle-paints-nothing`, 15:32 and 15:34), so a repeated `item` key is
  an existing, tested shape, not a new one.
- Recall: `content/video_engine/scripts/gate_one_shot_floor.py:122` (`SRC_M38`), `:546-555` (`row_m38` - FAIL below
  `MIN_RECIPE_COVERAGE`, both readings already printed in the one row), `:103` (`PREDATES_E96`), `:128` (`ROW_ORDER`
  M35-M42); `recipe_walk.py:1-20` (`events` / `match` / `count`, shared by the drift gate and the floor).
- Recall: `docs/GATES-REGISTRY.md` M ids present up to **M44**; M45 and M46 are free and P66 takes them.
- Recall: `content/video_engine/scripts/authoring/` = `__init__.py, audio.py, docks.py, effects.py, recipes.py,
  table.py, words.py`. `rg DEFAULT authoring/*.py` = 3 hits, none a defaults table: **the kit has no DEFAULTS file
  today**, so R26-176's "the authoring kit's DEFAULTS" is a file this plan creates (T6).
- Recall: `docs/research/runs/p56-recipe-seeds/` exists on disk (gitignored): `derive_seeds.py`, `measures.md`,
  `seeds.jsonl` - the precedent for how the fifteen were proven, and the field reads `recipe_walk.events` copied
  verbatim.
- Recall: memories `review-link-frozen-copy` (a served build is never rebuilt under the operator - the lab builds in
  private dirs), `proof-is-a-scene` (E99 s60), `visible-difference-and-local-life` (E99 s38: a card is judged only on
  a visible difference), `generated-images-stay-out-of-git`, `never-pipe-gated-steps-to-tail`,
  `one-shot-floor-recipes-not-events`.

## Intent And Acceptance

Intent: the combination space stops being folklore. It is enumerated as data, built as beats, filtered by the gates,
judged by the operator in batches, logged with a reason, learned as a table, and promoted into the two places an
author actually reads - the proven recipes and the kit's defaults.

Acceptance (all observable from the main checkout):

1. `python content/video_engine/scripts/lab_enumerate.py --write` emits
   `content/video_engine/effects/lab/candidates.jsonl`: one record per candidate with a **stable id**
   (`lab:<shape>:<members-digest>`), the beat shape, the ordered members with offsets, the clocks it was generated
   against (the M44 / M16 / M12 / M11 / 7.4 s values) and `status: enumerated`. Re-running gives a byte-identical
   file; the space is closed (shapes and member slots come from a tracked table, never from a counter) and the tool
   has no `--n` and no `--fill`.
2. `python content/video_engine/scripts/lab_build.py --batch <id>` builds each candidate as a real beat on the Tokyo
   bed into a PRIVATE build dir (`TOKYO_BUILD_DIR=build-lab-<batch>`, gitignored), runs `self_watch.py` then
   `gate_motion_density.py`, `gate_one_shot_floor.py` and `probe.py --sheet`, and writes
   `content/video_engine/effects/lab/runs/<batch>.jsonl` - per candidate the gate rows that decided it, its clip
   window, and `survivor: true|false`. Only survivors reach a card; a candidate a gate FAILs is recorded with the row
   that killed it, never dropped silently.
3. `python content/video_engine/scripts/lab_batch.py --batch <id> --write` adds **one queue record per beat shape**
   to `docs/content-video-engine/review-queue.v1.json` with the candidates side by side (a clip proof each), and
   `build_review_queue.py --write` renders it with a per-candidate approve / deny + reason control. About a quarter
   of each batch is drawn as exploration regardless of the learner (the record says which and why), and a previously
   approved candidate rides along as a calibration probe when the log holds one older than 14 days.
4. `python content/video_engine/scripts/lab_log.py --write` derives
   `content/video_engine/effects/lab/judgements.jsonl` from `review-answers.jsonl` ONLY - four fields per judgement
   (`bit`, `reason` from the fixed list, `proof: {clip, t}`, `at`) plus the candidate id and the answer's timestamp.
   Nothing is hand-typed; a judgement whose candidate is unknown, whose reason is off the list, or whose proof
   instant is missing is refused by name.
5. `python content/video_engine/scripts/lab_log.py --table` writes
   `content/video_engine/effects/lab/approval-rates.json` and its markdown twin: approval rate per FEATURE (beat
   shape, each member, the clock) with shrinkage toward the prior, the count behind every cell, and a header naming
   the limit - no Bradley-Terry or ranking model until the table is in the hundreds (arXiv 2411.04991); the reason
   categories are carried, not collapsed (Gao et al. 2022).
6. `python content/video_engine/scripts/lab_promote.py <candidate-id>` writes
   `content/video_engine/effects/recipes/<id>.json` (`effect_recipes.v1`, `status: proven`, members with
   `offset_s`/`role`, `window_s`, `source`, `count`, the `proof` the lab build produced), refuses a candidate with no
   approval in `judgements.jsonl`, and regenerates the catalogue through `build_effects_catalog.py --write`. The same
   command writes or amends the row in `content/video_engine/scripts/authoring/defaults.py` when the candidate
   carries one - every default a tracked fact with the approval id that bought it and the ruling it obeys.
7. `gate_one_shot_floor.py` M38 is a **WARN with both readings** (the spanning share and the beat a fire opens in)
   plus the sentence naming R26-168 and the interim, until HG2 restores it to `FAIL` at 0.60; the test pins the WARN,
   its wording and the restoration path, and `docs/GATES-REGISTRY.md` carries the interim verbatim.
8. No PNG, MP4 or WAV enters git from this plan: `git status --porcelain content/video_engine/effects/lab/` shows
   only `.json` / `.jsonl` / `.md`. No figure is invented, no paid generator is used, the Tokyo bed renders locally.

## Scope

- `content/video_engine/configs/lab_candidate.schema.json`, `lab_judgement.schema.json` (new, T1).
- `content/video_engine/scripts/lab_enumerate.py`, `lab_build.py`, `lab_batch.py`, `lab_log.py`, `lab_promote.py`
  (new) and their tests under `content/video_engine/tests/`.
- `content/video_engine/effects/lab/` (new, tracked): `beat-shapes.json`, `candidates.jsonl`, `runs/<batch>.jsonl`,
  `judgements.jsonl`, `approval-rates.{json,md}`.
- `content/video_engine/scripts/authoring/defaults.py` (new) - the kit's tracked defaults with their approval ids.
- `build_review_queue.py` + `review-queue.v1.json` + `REVIEW-QUEUE.md` + `test_review_queue.py`: the smallest change
  that carries a batch (the grammar section below).
- `gate_one_shot_floor.py` M38's interim reading + `test_gate_one_shot_floor.py` + `docs/GATES-REGISTRY.{md,jsonl}`.
- The re-proof run over the fifteen `proven` recipes on today's clocks (R26-168) as the lab's first real batch.
- Doctrine last: `BACKLOG.md` R26-168 / R26-176 / R26-171 / R26-172, `CAPABILITIES.md`, the generated docs layers.

## Not Building

- **No allocator and no beat-plan writer.** E99 s66 closed that: the beat plan and the script are intelligence work.
  The lab proposes combinations for a TEST BED; it never chooses a beat for an episode.
- **No engine, compiler or golden change.** Not one line of `scene-evidence-engine.mjs`, `build_scene_timeline_f.py`
  or `kinetics/*.mjs`; the golden suite sits in Verification precisely to prove it.
- **No shape compiler, no M45, no M46** - P66 owns those. M38's interim leans on P66's parity row as the floor in the
  gap (see Human Gates, the open question the parent settles before T7 runs).
- **No ranking model, no Elo, no pairwise cards** (E99 s68 Q5 = B; arXiv 2411.04991). The learner is a table.
- **No LLM judge and no automated approval.** The gates and the probe FILTER; the operator JUDGES; the parent applies.
  Neither the queue page nor the server rules (`build_review_queue.py:14`).
- **No re-render of any approved cut.** The Tokyo bed builds into `build-lab-*` only; nothing touches `build-short`,
  a served port, or a link the operator holds.
- **No images or video in git**, no fabricated figures, no paid generator (E99 s37).
- **No BACKLOG row closed by an agent** - T9 is the parent's.

## Approval

Approved by the operator 2026-09-16: *"yes, run them in parallel /prp-implement"* - P65, P66 and P67 run as concurrent delegated slices on main (disjoint write sets; the two shared files sequenced as written), no new worktree.

## Human Gates

**HG1 - the first batch (operator, after T4).** *PULLED 2026-09-17 after the parent read six of its twelve sheets: three open on the dip's black frame, the card outlives its row onto empty cream, two show no card in the window - the translation's defects, not the combinations'; the card returns when every rendition has been read on its sheet. As first carded: `lab-batch-r1-plate-carries-a-card` - twelve `plate-carries-a-card` candidates drawn uniformly (seed 20260917; the anchor `9b5531bf` kept; no learner exists, so the batch is exploration in effect, three marked `exploration` by the tool's own draw; no calibration probe yet), all twelve built on the Tokyo bed's beat 12, all twelve survived (not one gate row fired inside the window; the eleven whole-cut rows are identical context), twelve clips side by side. It supersedes the one-candidate `lab-smoke-r2-plate-carries-a-card`, which stays open for you to close. The gates discriminated between none of them: the whole distinction is yours - that is the point of the lab.*  One batch of survivors on the queue: one card per beat shape, the
candidates side by side, each a clip that plays. Two things are being proved at once - the combinations, and the
**grammar**: does an approve / deny + reason per candidate, inside one card that asks one plain question, work for
the operator, or does he want one card per candidate at a lower rate? Blocks T5 (the log has nothing to derive until
an answer exists) and every later batch. Queue row written in T4, kind `batch`.

**HG2 - the re-proved set and M38's restoration (operator, after T8).** *REFRAMED 2026-09-17 on the operator's reads ("the whole idea of the recipes was that they worked"; "you literally just threw on a card dock, then dipped"): the eight clips were the lab's renditions, not the mechanisms, and the gates they were measured against post-date the cuts the recipes were proven in. The card is pulled to `owed`. It returns with the question "which gate clocks bend to the proven set" - every proven recipe on its own proof cut must pass M44/M16/M11/M25 or the clock is calibrated to it (E38, E99 s69) - and only after the parent has read each rendition beside its proof cut on a side-by-side sheet.*  The fifteen `proven` recipes rebuilt on
six-second plates and built pages: which survive as proven, which are retired, which are replaced by a combination
the lab found. The operator's word restores M38 to `FAIL` at 0.60 (or moves the number). Blocks the promotion of the
re-proved set and the closure of R26-168. Queue row written in T4 as kind `owed` (its proof does not exist until T8
builds it) and flipped to `batch` by T8.

**The open question the parent settles before T7** (stated, not hidden): the blueprint says M38 prints its number
while *"the parity row (M45) is the floor"* - but M45 ships in P66. Two readings: **(a)** T7 lands the WARN now and
the floor is genuinely thinner until P66's M45 exists (a window of days, with M35/M36/M37/M39/M41 still binding);
**(b)** T7 is held until P66's M45 slice lands, so no cut is ever measured without a recipe-or-mechanism floor. The
parent recommends **(b)**, and T7 is written with that cross-plan dependency in `Depends on`.

**RESOLVED by the parent (2026-09-16): reading (b).** T7 lands after P66 T5; until then M38 stays a FAIL row and
one-shot builds carry it as the known contradiction R26-168 names. P65 and P66 run in parallel worktrees: their
write sets are disjoint except `review-queue.v1.json` (T4 of each, landed one after the other) and
`gate_one_shot_floor.py` (different functions, separate commits, P66 T5 first).

Parent decisions recorded so they are not re-litigated (NOT operator gates): the candidate and judgement schemas
(T1); the fixed reason list; the batch's queue grammar (below); the lab's file names and directory.

### The batch's queue grammar (T4 - the smallest change to the queue)

The queue's grammar is one card, one plain question, a list of `options`, a free-text `note`
(`build_review_queue.py` `REQUIRED` / `validate_record`). A batch needs a bit and a reason **per candidate**, and
enumerating subsets of five candidates in `options` is combinatorial nonsense. Two readings were weighed:

- **Reading 1 - no schema change.** One `approve` card per beat shape whose `options` are the candidate labels; the
  operator picks a winner and writes the rest into the note. Cheapest, and it loses exactly what s68 asked for: the
  denials, with their reasons, per candidate.
- **Reading 2 - RECOMMENDED - a `batch` kind, per-candidate controls, one answer row per candidate.** `KINDS` grows
  `"batch"`; a batch record carries `candidates: [{id, label, one_line, proof}]`; the page renders the card's single
  question once (*"which of these beats earns its place, and why not the others?"*) with an approve / deny + reason
  select per candidate; each control POSTs through the existing `/answer` as
  `{item: "<card-id>#<candidate-id>", choice: "approve"|"deny", note: "<reason>: <free text>", at, by}`. The answers
  file already carries repeated `item` keys, so nothing downstream changes shape; `latest_answers` keys by `item`, so
  a re-judged candidate supersedes itself; the page still rules nothing.

Reading 2 is the plan of record. The reason list is fixed and short (T1): `reads-as-noise`, `too-fast`, `too-slow`,
`unattributable-motion`, `illegible-at-9-16`, `wrong-for-the-sentence`, `duplicate-of-an-approved`, `off-doctrine`,
`good`.

## Mandatory Reads

- `docs/content-video-engine/GRILL-AGENTS-HARNESS-EFFECTS-2026-09-16.md` - all of it (decisions 3-4, the rejected
  alternatives, the gotchas, the build order, appendix A s2).
- `docs/portable/OPERATOR-RULINGS.md` **E99 s68** (`:3254`), **s67** (`:3252`), **s66** (`:3250`); E96 (`:2801`);
  E99 s60 (a proof is a scene), s38 (a visible difference), s14 (a card reaches the operator only with a proof).
- `docs/content-video-engine/BACKLOG.md` R26-168 (`:600`), R26-176 (`:608`), R26-171 (`:603`), R26-172 (`:604`).
- `content/video_engine/scripts/authoring/recipes.py:1-20` (the NOT AN ALLOCATOR block, verbatim) and
  `docs/content-video-engine/PIPELINE.md:33`.
- `content/video_engine/scripts/build_review_queue.py:1-60` plus `validate_proof` / `validate_record` / `validate`;
  `content/video_engine/tests/test_review_queue.py`; `serve_review_queue.py` (POST /answer only);
  `review_queue_proofs.py --clips`.
- `content/video_engine/scripts/gate_one_shot_floor.py` (M35-M42, `load_recipes`, `row_m38`, `PREDATES_E96`,
  `OFFSET_TOL`) and `content/video_engine/tests/test_gate_one_shot_floor.py`; `recipe_walk.py` +
  `content/video_engine/tests/test_recipe_walk.py`.
- `content/video_engine/configs/effect_recipe.schema.json`; `build_effects_catalog.py`; `effects_catalog_check.py`;
  `content/video_engine/tests/{test_authoring_recipes.py,test_build_effects_catalog.py}`.
- `docs/research/runs/p56-recipe-seeds/{derive_seeds.py,measures.md,seeds.jsonl}` (on disk, gitignored) - the
  precedent for proving a recipe; and `.claude/PRPs/plans/P56-EFFECT-RECIPES-AND-THE-ONE-SHOT-FLOOR.plan.md`.
- `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py:39` (`TOKYO_BUILD_DIR`) and
  `:219` (the approved table) - the bed, and the shape a candidate is built into.
- `docs/WORKTREE-REGISTER.md` (read at start); `docs/runbooks/PRP_EXECUTION.md` (Dispatch mapping, Worktrees and
  lanes, PRP Format); `docs/runbooks/RECALL-RECEIPT.md`.

## Execution Path

T1 (schemas + the reason list) first and alone - every later slice validates against it. T2 (the enumerator) and T7
(M38's interim) are then independent of each other; T3 (build + filter) needs T2; T4 (the batch cards and the queue's
`batch` kind) needs T3 and frames both HG rows. **HG1 gates T5** - there is nothing to derive from an empty answers
file. T6 (promotion and the kit's defaults) needs T5. T8 (the re-proof run) needs T3 and T6's promote path and feeds
HG2. T9 (doctrine) is last and the parent's.

T7 carries the cross-plan dependency named in Human Gates: it lands after P66's M45 slice unless the parent takes
reading (a). T4 and P67 T5 both edit `build_review_queue.py`'s `validate_record` and `test_review_queue.py`: T4 lands first and P67 T5 is written on top of it (the steward never holds both open). Commits are the `release_steward`'s, from the main checkout, allowlisted paths; a commit touching a
mechanism file carries its `Recall: <path>:<line> (note)` lines (`scripts/hooks/recall_receipt.py`). Nothing is
pushed without the operator's word. Every gated step runs UNPIPED.

## Patterns To Mirror

- `content/video_engine/scripts/build_effects_catalog.py`: a generator with `--write` / `--check`, deterministic LF
  output, every truth pulled from a source rather than copied. `lab_enumerate.py` and `lab_log.py` take that shape.
- `content/video_engine/scripts/recipe_walk.py`: one walk, two readers, no re-implementation - `lab_build.py` reads
  its candidate's fires through `recipe_walk.match`, never with a matcher of its own.
- `content/video_engine/scripts/build_review_queue.py` `validate_record`: refuse by NAME, one message per defect.
  The lab's loaders do the same.
- `content/video_engine/tests/test_effects_catalog_drift.py`: every failure mode proved by a broken tmp copy.
- P56 T6's calibration habit (memory `thresholds-from-the-reference`): the reference measured with the same tool
  first, never a threshold fitted to our own work.

## Task Slices

### T1: The schemas and the fixed reason list
- Status: done
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/configs/lab_candidate.schema.json`, `content/video_engine/configs/lab_judgement.schema.json`, this plan's grammar section
- Acceptance: `lab_candidates.v1` (`id` matching `^lab:[a-z0-9-]+:[0-9a-f]{8}$`, `shape`, ordered `members` with `card`/`option`/`offset_s`/`role`, `clocks` naming each gate value the candidate was generated against, `status` in `enumerated|built|survivor|carded|approved|denied|retired`, `source`) and `lab_judgements.v1` (`candidate`, `bit` in `approve|deny`, `reason` from the nine-item list, `proof: {clip, t}` both required, `at`, `by`, `answer_at`), `additionalProperties: false` everywhere, Draft 2020-12 (what `load_cards` already uses). The reason list appears ONCE, in the schema, and every tool imports it from there.
- Validate: `python -c "import json;s=json.load(open('content/video_engine/configs/lab_judgement.schema.json',encoding='utf-8'));print(s['$id'], sorted(s['$defs']['judgement']['required']), len(s['$defs']['judgement']['properties']['reason']['enum']))"`
- Evidence: `content/video_engine/configs/lab_candidate.schema.json` (`lab_candidates.v1`: candidate requires clocks/id/members/shape/source/status; clocks require the five gate values; member requires card/offset_s/role) and `lab_judgement.schema.json` (`lab_judgements.v1`: answer_at/at/bit/by/candidate/proof/reason; reason enum 9 items) - the acceptance command printed `lab_judgements.v1 ['answer_at', 'at', 'bit', 'by', 'candidate', 'proof', 'reason'] 9`; good/bad instances validated with jsonschema 4.26.0 (report `scratchpad/assembly/P65-T1.md`).
- Deviation: the schemas were drafted by `junior_developer` from the plan's fixed reason list and reviewed by the parent (the decisions were already in the plan; the typing was not judgement).

### T2: The enumerator - the space as DATA, finite and closed
- Status: done
- Owner: `implementation_luna`
- Depends on: T1
- Write set: `content/video_engine/scripts/lab_enumerate.py`, `content/video_engine/effects/lab/beat-shapes.json`, `content/video_engine/effects/lab/candidates.jsonl`, `content/video_engine/tests/test_lab_enumerate.py`
- Acceptance: `beat-shapes.json` names at least the five shapes R26-176 and s67 give - a plate carrying a card; a page whose number lands at +N s; a page-to-page transform; a return; the open ON the chart - each with its member SLOTS (the axes a slot accepts, resolved against `docs/EFFECTS-CATALOG.jsonl` through `authoring/effects.py`, so no candidate can name a token the compiler refuses) and the clocks that bind it. `lab_enumerate.py --write` emits the full cross product as `candidates.jsonl`, one record per candidate, stable id, sorted, LF, byte-identical on a re-run; `--check` exits 1 when stale. The tool has NO `--n`, no `--fill` and no sampling: the test asserts the emitted count equals the product computed from the tables, that the count stays under a stated CEILING (`MAX_CANDIDATES`, a named constant - the space is expected in the low hundreds; a shape whose slot table pushes the product past it is refused by name, since a batch the operator cannot read in one sitting is not a batch), that every member resolves to a card or a listed option, and that a candidate violating its own clock (a plate under M44's 6 s, a light before the build ends, a gap over M16's 2.5 s) is refused by name at generation. The module docstring carries the reconciliation sentence: the lab generates candidates for a test bed and authors no episode (`recipes.py:1-20`, `PIPELINE.md:33`).
- Validate: `python -m pytest content/video_engine/tests/test_lab_enumerate.py -q` then `python content/video_engine/scripts/lab_enumerate.py --check`
- Evidence: `scripts/lab_enumerate.py` (`--write` / `--check`, `MAX_CANDIDATES = 400`, clocks imported from `gate_motion_density.py`), `effects/lab/beat-shapes.json` (five shapes with slot tables at clock offsets; a new shape or slot is a data change), `effects/lab/candidates.jsonl` (288 candidates: plate-carries-a-card 54, page-number-lands-at-n 90, page-to-page-transform 40, return 32, open-on-the-chart 72; every record valid against lab_candidates.v1), `tests/test_lab_enumerate.py` 18 passed (the parent re-ran it); `--check` in sync. The first write refused all 90 page candidates on a 5.0 s light-to-leave gap: the TABLE was fixed (a `hold` slot - the figure written while the number is said, E99 s67), never the clock (report `scratchpad/assembly/P65-T2.md`).

### T3: The test-bed builder and the gate + probe filter
- Status: done
- Owner: `implementation_luna`
- Depends on: T2
- Write set: `content/video_engine/scripts/lab_build.py`, `content/video_engine/tests/test_lab_build.py`, `content/video_engine/effects/lab/runs/` (the run records only)
- Acceptance: `lab_build.py --batch <id> [--candidates <ids>]` builds each named candidate as a REAL beat on the Tokyo bed - the bed's own take, words and assets, the kit's rows through `table.write_shot_table` - into `TOKYO_BUILD_DIR=build-lab-<batch>`, a private, gitignored dir; the tool REFUSES a build dir named `build-short*` or one a `serve_player.py` is listening on (`review-link-frozen-copy`, E99 s11). It then runs `self_watch.py <build>` (the fresh probe), `gate_motion_density.py`, `gate_one_shot_floor.py` and `probe.py <build> <the candidate's own instants> --sheet <png>` (the probe takes instants, never a bare `--sheet`), parses the rows with the existing `[LEVEL] Mxx` protocol, and writes `runs/<batch>.jsonl`: per candidate its `survivor` bit, every FAIL / WARN row that decided it, the clip window `{t0, t1}` a card would show, and the sheet path (untracked). A candidate whose clip is not a beat a short could carry is refused by name (E99 s60). `lab_build.py --batch <id> --check` re-reads `runs/<batch>.jsonl` and exits 1 when a candidate of the batch has no record or a record names a sheet or clip window that is not on disk (T8 leans on it). The test drives a `--dry-run` that stubs the render and asserts the refusal rules, the row parsing and the record shape - no pytest run renders video.
- Validate: `python -m pytest content/video_engine/tests/test_lab_build.py -q`
- Evidence: (first pass) `scripts/lab_build.py` (shape -> Tokyo beat table; member -> row translation; refuses `build-short*` and a served port; `--dry-run`; `--check`), `tests/test_lab_build.py` 26 passed; smoke run `smoke-r1` on two candidates built, compiled under `no_receipt`, gated. FINDINGS (the parent, 2026-09-17): (1) both smoke candidates were killed by WHOLE-CUT rows (M35/M37/M39 floors, M28, M34) firing outside the candidate's window - the filter must decide on the rows whose instants fall inside the window and print the whole-cut rows as context only; (2) the open candidate lit at 7.4 s and M11 refused it because an `axes` entry lands its build at ~3.0 s (LP_BUILD_S), not at PAGE_BUILD_END_S 7.4 (the mount's clock) - the light slot follows the ENTRY, a clock fact the lab just measured and `beat-shapes.json` must encode; (3) the record dir `runs/` is gitignored by the bare `runs/` rule - renamed to `effects/lab/batches/`; `build-lab-*/` gitignored by the parent; `self_watch.py` now passes the full build path so a nested private build resolves. RESOLVED (second pass): the filter decides on the rows whose instant falls inside the candidate's window (a FAIL kills, a WARN is recorded); whole-cut rows ride under `context`; the light and hold slots follow the ENTRY's landing; the record dir is `effects/lab/batches/`. `smoke-r2`: the open candidate `7f588cbb` reads `[PASS ] M11 ... enters at 0.0s, its build lands at 3.0s, with callout at 3.0s` and is killed by one in-window row, `[FAIL] M29 ... landing 2 (throw, paper) at 9.51s` (the bed's unrewritten SOUND-PLAN - a bed limitation, recorded); the plate candidate `9b5531bf` SURVIVES (no deciding row, 11 context rows). 31 + 22 tests pass; `--check` in sync on both tools. M11's landing per entry, from `gate_motion_density._page_land_offset` (:1178-1188): axes 3.0, spiral 1.6, built 0.0, mount = mount_s + 7.4 - 3.9 (5.5 on this bed) - the lab encoded the mount at 7.4, so the clocks gain `lp_spiral_in_s` and `mount_land_s` (the parent widened the schema) and the enumerator reads the landing from the gate's own function (T3 third pass, a small one). `self_watch.verdict_line` cannot read its own report (`:141-149` vs `:439`) - the lab falls back to `parse_report`; a backlog row for T9.

### T4: The batch cards - the queue's `batch` kind, the exploration share, the calibration probe, and both HG rows
- Status: done
- Owner: `implementation_luna`
- Depends on: T3
- Write set: `content/video_engine/scripts/lab_batch.py`, `content/video_engine/scripts/build_review_queue.py`, `content/video_engine/scripts/serve_review_queue.py`, `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md`, `content/video_engine/tests/test_review_queue.py`, `content/video_engine/tests/test_lab_batch.py`
- Acceptance: `build_review_queue.py` grows `"batch"` in `KINDS` and `ANSWERABLE_KINDS`, a `candidates` list validated the way `proofs` is (each `{id, label, one_line, proof}` with a `clip` proof), and a card that renders one plain question plus an approve / deny + reason `select` per candidate, each POSTing `{item: "<card>#<candidate>", choice, note}`; `serve_review_queue.py`'s answer check (`:56-61` today refuses an item that is not a record id and a choice outside the record's `options`) grows ONE branch: an item of the form `<batch-card-id>#<candidate-id>` resolves to that batch's candidate, its choices are `approve` / `deny`, and the note must open with a reason from T1's list - everything else about the server (POST /answer only, append-only, rules nothing) is unchanged, and the test drives the branch with a synthetic batch. `validate_record` refuses a batch with no candidates, a candidate with no clip proof, a duplicate candidate id, and a reason that is not on T1's list. `lab_batch.py --batch <id> --write` writes one batch record per beat shape from `runs/<batch>.jsonl` survivors, marks about 25 % of each batch `exploration: true` (drawn without reference to the learner, the draw seeded and the seed recorded), and attaches one previously approved candidate as `calibration: true` when `judgements.jsonl` holds one older than 14 days. The same change adds the **HG1** row (kind `batch`, blocks T5) and the **HG2** row (kind `owed`, its `owed` field naming the re-proof run T8 still owes); `REVIEW-QUEUE.md` is regenerated, never hand-edited.
- Validate: `python -m pytest content/video_engine/tests/test_review_queue.py content/video_engine/tests/test_lab_batch.py -q` then `python content/video_engine/scripts/build_review_queue.py --check`
- Evidence: `build_review_queue.py` grows the `batch` kind (`candidates[{id, label, one_line, proof, exploration?, calibration?}]`, one question, an approve / deny + reason select per candidate posting `<card>#<candidate>`; `validate_batch` refuses no candidates, no clip proof, a duplicate id, an off-list reason, and requires `proofs` to mirror the candidates' proofs in order so `review_queue_proofs.py` names each clip by index); `serve_review_queue.py` accepts the `#` form (choices approve/deny; the note opens with a reason from `lab_judgement.schema.json`); `lab_batch.py --batch <id> --write [--hg1] [--check]` groups survivors by shape, draws ~25 % exploration with a recorded seed, attaches a calibration probe from `judgements.jsonl` when one is older than 14 days (tested on a tmp file). 76 tests (the parent re-ran); `build_review_queue.py --check` ok (3 answerable, 2 owed, 77 ruled). HG1 `lab-smoke-r2-plate-carries-a-card` (kind batch; ONE candidate - smoke-r2's other was killed by M29 - so the side-by-side batch the operator asked for is re-cut from the first real batch after T8), its clip rendered (38.96-45.05 s, 9:16); HG2 `p65-hg2-the-reproved-set-and-m38` (kind owed, naming `batches/reproof-r1.jsonl`). `tests/fixtures/review-queue.fixture.json` carries no batch record (outside the write set); the batch is proved on in-test records and the live card.

### T5: The approval log and the learner
- Status: pending
- Owner: `implementation_luna`
- Depends on: T4, HG1
- Write set: `content/video_engine/scripts/lab_log.py`, `content/video_engine/effects/lab/judgements.jsonl`, `content/video_engine/effects/lab/approval-rates.json`, `content/video_engine/effects/lab/approval-rates.md`, `content/video_engine/tests/test_lab_log.py`
- Acceptance: `lab_log.py --write` reads `review-answers.jsonl` ONLY, splits `item` on `#`, and derives one `lab_judgements.v1` record per candidate answer - the bit, the reason category, the instant of proof (the card's clip and the second inside it the answer names, defaulting to the clip's `t0` when none is named), the timestamp - refusing by name an unknown candidate, an off-list reason or a missing clip. Re-running is idempotent and a later answer for the same candidate supersedes the earlier one (the earlier kept, `superseded: true`). `--table` writes the per-feature approval-rate table with shrinkage toward the batch prior over beat shape, member and clock, the count behind every cell, and a header naming the limit with its two citations (arXiv 2411.04991; Gao et al. 2022). The test asserts a single-observation cell is pulled toward the prior instead of printing 1.00, that reasons are carried per feature and not collapsed into the rate, and that no pairwise or ranking model is computed anywhere in the module.
- Validate: `python -m pytest content/video_engine/tests/test_lab_log.py -q`
- Evidence: pending

### T6: Promotion - a proven recipe and a tracked DEFAULT
- Status: pending
- Owner: `implementation_luna`
- Depends on: T5
- Write set: `content/video_engine/scripts/lab_promote.py`, `content/video_engine/scripts/authoring/defaults.py`, `content/video_engine/tests/test_lab_promote.py`, `content/video_engine/tests/test_authoring_defaults.py`
- Acceptance: `lab_promote.py <candidate-id>` refuses a candidate with no `approve` in `judgements.jsonl`, refuses one whose run record is not a survivor, and otherwise writes `content/video_engine/effects/recipes/<id>.json` valid against `effect_recipe.schema.json` (`status: proven`, members with `offset_s`/`role`, `window_s`, `source: lab:<batch>`, `count`, and the `proof` the T3 build produced, confirmed at that instant by `recipe_walk.match`), then runs `build_effects_catalog.py --write` and `effects_catalog_check.py` so the catalogue stays BUILD OUTPUT (P63). `authoring/defaults.py` is the kit's tracked defaults table - one entry per default (a page enters by axes or mount unless told; the light lands after the build, never on arrival; a card sits in the page's own room; no rails and no park at 9:16; a plate holds six seconds), each carrying `value`, `why` (its ruling id) and `approval` (the judgement id that bought it, or `ruling-only` with the ruling cited). The test asserts every entry has one of those two provenances and that the module names no episode (the kit's rule, `authoring/__init__.py:12-15`).
- Validate: `python -m pytest content/video_engine/tests/test_lab_promote.py content/video_engine/tests/test_authoring_defaults.py -q`
- Evidence: pending

### T7: M38's interim reading - a WARN that prints both numbers and names R26-168
- Status: done
- Owner: `junior_developer`
- Depends on: T1; and P66 T5 AS LANDED (M45 with its provisional constant) - not on P66 HG1's answer (reading (b), resolved above)
- Write set: `content/video_engine/scripts/gate_one_shot_floor.py` (`row_m38` and `SRC_M38` only), `content/video_engine/tests/test_gate_one_shot_floor.py`, `docs/GATES-REGISTRY.md`, `docs/GATES-REGISTRY.jsonl`
- Acceptance: `row_m38` returns `WARN` instead of `FAIL` below `MIN_RECIPE_COVERAGE`, keeps both readings in the one row (the spanning share and the beat a fire opens in - the existing text unchanged), and appends one sentence: the proven set is being re-proved on today's clocks (R26-168) so this row does not stop a cut until P65 HG2, and the parity row (M45) is the floor in the interim. A build at or above 0.60 still reads `PASS`. The test pins the level at a coverage of 0.03 (one-shot #3's number), the wording of the interim sentence, that the row can never read `FAIL` while the interim flag is set, and that one constant flips it back to the floor. `build_gates_registry.py --write` regenerates both registry files from the source; neither is hand-edited.
- Validate: `python -m pytest content/video_engine/tests/test_gate_one_shot_floor.py -q` then `python content/video_engine/scripts/build_gates_registry.py --check`
- Evidence: `gate_one_shot_floor.py` `M38_INTERIM_WARN = True` beside `MIN_RECIPE_COVERAGE`; `row_m38` WARNs below 0.60 with both readings and the interim sentence (R26-168; M45 the floor meanwhile), PASSes at 0.60, FAILs again with the constant False (tests pin all four; 52 -> 57 test names, none removed); `SRC_M38` carries the clause; registry `--check` in sync (gitignored build output). One-shot #3 reads `[WARN ] M38 proven-recipe coverage 0.09 spanning / 0.00 by the beat a fire starts in, of 32 beats ... interim (R26-168) ...` and the build exits 0 FAIL / 2 WARN. 62 passed (the parent re-ran).

### T8: R26-168 - the fifteen proven recipes re-proved on today's clocks
- Status: done
- Owner: `implementation_luna`
- Depends on: T3, T6
- Write set: `content/video_engine/effects/lab/runs/reproof-r1.jsonl`, `docs/content-video-engine/review-queue.v1.json` (the HG2 row only, flipped from `owed` to `batch`), `docs/content-video-engine/REVIEW-QUEUE.md`
- Acceptance: each of the fifteen `proven` recipes is rebuilt on the Tokyo bed under today's clocks - six-second plates (M44), pages that BUILD then hold built (E99 s67), no rails and no park at 9:16 (R26-171 / R26-172) - through `lab_build.py`; `reproof-r1.jsonl` records per recipe: survives as proven / needs an amended offset (naming it) / is unreachable under the clocks (naming the row that kills it - e.g. `card-becomes-the-chart` on M44, `emphasized-bar-lit` on M11, the badge ladder on M25). The three contradictions R26-168 names each get a measured row, not an opinion. The HG2 card then carries the survivors and the casualties side by side with clips. NO recipe file is edited in this slice - promotion runs through T6's tool after the operator's word.
- Validate: `python content/video_engine/scripts/lab_build.py --batch reproof-r1 --check` then `python -m pytest content/video_engine/tests/test_lab_build.py -q`
- Evidence: `lab_build.py` now re-derives the cues INSIDE a candidate's window from the candidate's rows (the approved cues outside kept verbatim; smoke-r3's M29 row is the candidate's own `page retract 1 (flip) at 9.50s`, no longer a stale approved landing) and takes `--recipes <ids|all-proven>` (a recipe's members at their offsets in a Tokyo beat chosen by its acts, under today's clocks; a rail dropped at 9:16 and recorded). `batches/reproof-r1.jsonl`: 15 records - SURVIVE 5 (held-dock-across-the-cut, outro-clip-life, punch-then-callout, still-life-breather, trace-callout-ladder); AMEND 3 (card-becomes-the-chart: M44, exit:dip 5.12 -> 6.00; emphasized-bar-lit: M11, spotlight 7.56 -> 3.00; held-page-hosts-the-docks: M11, callout 8.80 -> 3.00); UNREACHABLE 7 (badge-ladder on M16 after the rails drop; dock-lands-page-renames and read-park-build-write on M25; plate-dock-wipe on M05; spotlight-held-past-the-cut, test-card-rows, verdict-recap - the last three need their own beds). R26-168's three contradictions each measured. 50 tests (the parent re-ran); `--check` in sync. No recipe file touched. `lab_build.py` is 1585 lines against the 800 guideline - a split is R26-182. (the card, 2026-09-17) `lab_batch.py --batch reproof-r1 --hg2 --write` flipped `p65-hg2-the-reproved-set-and-m38` from owed to `batch` in place: the eight survivors and amendments side by side with their clips (8 of 8 rendered), the seven unreachable named in the judge text with the row that killed each and carded nowhere (E99 s60), no draw and no probe; 33 batch tests; `--check` ok (4 answerable, 1 owed). The live-data WARN test now pins the RULE (every open whole-cut watch without a critic warns) instead of a count of two, since one-shot #3's critic landed.
- Evidence (the parent's read of the eight reproof-r2 sheets, 2026-09-17 - `build-lab-reproof-r2/<recipe>/lab-members.png`, this cut's members over the proof cut): READS RIGHT - card-becomes-the-chart (the thrown card is the holdings chart's own card at 4.57 s and the page grows out of it through the veil at 5.34 s; the window ends on cream - the beat, not the recipe), dock-lands-page-renames (the clipping lands, the title rewrites to 'The opponent' at 55.5 s; the card's placement is a companion note), plate-dock-wipe (the wipe at 21.1 s; the 30 dead seconds are a 31 s beat against a three-second recipe - s70), spotlight-held-past-the-cut (the light on -9.9 % persists across the boundary at 56.4 -> 57.0 s - the recorded `not on this bed` names a still card the bed lacks, but the essential move is on the frame). NOT YET - badge-ladder (one static $617 pill for five seconds where the proof cut stamps badge after badge; the lane's 'pills carry the pulse' is not what the frame shows), read-park-build-write (the wafer card lands over the plot's lower half - the PARK member is still dropped; R26-172 is withdrawn and the park must be restored). NOT ON THIS BED, correctly - test-card-rows (the checklist card is Steel's), verdict-recap (the stack payload). EVERY window still opens on a BLACK frame (38.96 s, 44.88 s): the window-start fix did not hold - the first tile must be after the boundary's black. Nothing carded until those three are fixed and re-read.

### T9: Doctrine, the backlog and the layers
- Status: running (the part the finished slices earned; HG1/HG2's answers and T6's pointers owed)
- Owner: parent
- Depends on: T6, T7, T8
- Write set: `docs/content-video-engine/BACKLOG.md` (R26-168, R26-176, R26-171, R26-172), `docs/content-video-engine/CAPABILITIES.md`, `docs/runbooks/ONE-SHOT.md` (step 4's pointer to the lab's defaults), `docs/portable/OPERATOR-RULINGS.md` (HG1 and HG2's answers), this plan's status, the generated docs layers
- Acceptance: R26-176 carries its verdict in bold with the lab's paths; R26-168 carries the re-proof verdict per recipe and closes only when HG2 restores M38; R26-171 / R26-172 point at `authoring/defaults.py` as the place their rule now lives. `CAPABILITIES.md` gains a THE RECIPE LAB row (the five tools, one line each) and `docs_find.py "recipe lab"` finds it. Both human-gate answers are written into the rulings and into this plan. `build_docs_layers.py --check` reports every layer in sync.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check` then `python content/video_engine/scripts/docs_find.py "recipe lab"` then `python scripts/prp_validate.py .claude/PRPs/plans/P65-THE-RECIPE-LAB.plan.md`
- Evidence: (partial, 2026-09-17) BACKLOG R26-168 carries the MEASURED verdict per recipe (5 survive / 3 amend with the offsets / 7 unreachable with the row) and closes on HG2's word; R26-176 BUILT (the paths, what is owed); two new rows R26-182 (`lab_build.py` 1585 lines - split by concern) and R26-183 (`self_watch.verdict_line` cannot read its own report); CAPABILITIES gains THE RECIPE LAB row after THE SHAPE COMPILER (`docs_find.py "recipe lab"` hits it). Owed: R26-171/172 pointing at `authoring/defaults.py` (T6), both HG answers into the rulings and this plan.

## Verification

- Unpiped, from the main checkout: `python -m pytest content/video_engine/tests/test_lab_enumerate.py content/video_engine/tests/test_lab_build.py content/video_engine/tests/test_lab_batch.py content/video_engine/tests/test_lab_log.py content/video_engine/tests/test_lab_promote.py content/video_engine/tests/test_authoring_defaults.py content/video_engine/tests/test_review_queue.py content/video_engine/tests/test_gate_one_shot_floor.py -q`.
- The blast radius is proved by the untouched layers: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/sync_kinetics.py --check` pass unchanged (no engine, no compiler, no golden).
- `python content/video_engine/scripts/build_review_queue.py --check`; `python content/video_engine/scripts/effects_catalog_check.py`; `python content/video_engine/scripts/build_gates_registry.py --check`; `python content/video_engine/scripts/build_docs_layers.py --check`.
- `git status --porcelain content/video_engine/effects/lab/` lists only `.json`, `.jsonl` and `.md`.
- `python scripts/prp_validate.py .claude/PRPs/plans/P65-THE-RECIPE-LAB.plan.md`; `python scripts/prp_status.py`.
- Risks named: (1) the enumerated space is only as good as `beat-shapes.json` - a shape nobody wrote is a shape the
  lab cannot find, so T9's CAPABILITIES row says where shapes are added; (2) a batch spends operator time, and the
  exploration share spends part of it deliberately on candidates the table expects to fail - that is the Goodhart
  mitigation and the card says so; (3) M38's interim WARN is a real loosening for as long as it lasts (the Human
  Gates question); (4) the lab's builds are renders - local, on the Tokyo bed, never on a served port.

## Evidence And Handoff

- Per-slice reports under `scratchpad/assembly/P65-T<n>.md`: changed files, the validation command, its verbatim tail.
- The tracked record of the whole lab is five files under `content/video_engine/effects/lab/` plus the promoted
  recipes; sheets, clips and builds stay out of git.
- Commits by the `release_steward` from the main checkout, allowlisted paths, `Recall:` lines on every mechanism
  file. Nothing pushed without the operator's word.
- Handoff to P66: the promoted recipes and `authoring/defaults.py` are the compiler's vocabulary, and HG2's answer is
  what restores M38 so P66's variety row (M46) is read beside a floor that binds.
