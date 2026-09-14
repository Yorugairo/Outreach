---
id: P56-EFFECT-RECIPES-AND-THE-ONE-SHOT-FLOOR
title: Effect recipes and the one-shot floor - a beat is authored as a proven COMBINATION of catalogue effects, generated into the P55 catalogue and the authoring kit, and a cut is measured against floors (chart forms, a chart-to-chart transform, docks on beats, recipe coverage, narrative:chart, parity with the best approved short) before it is offered for a watch
status: complete
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-13
updated: 2026-09-13
---

# Effect recipes and the one-shot floor

## Summary

E96 (2026-09-13), the operator: *"the individual effect is not really the key, it's blending a few of them together
that creates the effect ... I think we need the effect recipe and the capability comparator ... a mini engine in itself
where we require a capability and comparator plan per beat, effective combinations build the effective recipe, and what
the director-critic is actually auditing is if the effect recipes are effective."* On the thin one-shot: *"there was
minimal motion/transformation, and mixing of narrative panels and charts. You mostly changed words and used only 2
charts."* Round 2 answers: **Q1 = A + C** (recipe CARDS in the P55 catalogue, generated into authoring-kit presets),
**Q2 = (a)** (floors per short before the watch). The grill's build order (`GRILL-PIPELINE-VALUE-2026-09-13.md` s5)
puts this plan FIRST and says: *"P55's own generator and gate extend; no engine work."*

The measure that explains the failure (grill s1, re-derived below from the same four timelines): the thin one-shot ran
**17.9 events/min - as busy as Tokyo (18.2), 3x Bravos (6.0)** - with **1 chart form, 0 docks, 0 chart-to-chart
transforms, 0.20:1 narrative:chart, and no recurring combination at all** (every 3-5 member combination in it fires
exactly once; Steel has one that recurs 13x, Japan one that recurs 4x). 12 of the 15 measured recipes never fired, and
**9 of those 12 need a dock** - zero docks made nine of them unreachable by construction. So the unit that was missing
is not an effect, it is a COMBINATION, and the floor that was missing is not a rate.

This plan builds three things and nothing else: (1) **recipe cards** - a new data family beside P55's 125 effect cards,
one recipe = ordered card ids + offsets + the sentence act + a played instant that proves it; (2) the **beat plan** -
the comparator + capability + recipe choice per sentence, written before the rows; (3) the **one-shot floor v2** - a
gate that measures a COMPILED timeline against the five floors and the reference-parity table, wired into the
`self_watch.py` bar so a cut under a floor is `NOT CLEAN` and is never offered for a watch.

All repo paths below are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`). This draft was written in the
sweet-villani worktree because the harness refuses writes to the main checkout's `.claude/`; the parent copies it on
approval.

### Recall (run before drafting, 2026-09-13 - the receipt rule, `docs/runbooks/RECALL-RECEIPT.md`)

- Recall: `sigmap_context.py query "effect recipe" --top 5` ranks `content\video_engine\tests\test_build_docs_index.py`
  (6.35), `scripts\effects_card.py` (5.67), `scripts\build_effects_catalog.py` (5.17),
  `tests\test_build_effects_gallery.py` (5.07), `scripts\authoring\effects.py` (4.86) - i.e. every hit is P55's
  machinery; there is no recipe code anywhere.
- Recall: docs_find "recipe" = 15 hits, none of them an effect recipe: `16-EDITORIAL-MOTION-SYSTEM.md:147` "6. Pacing
  recipe - `editorial_pacing_recipe.v1` stores the channel's abstract edit grammar" (a DIFFERENT runtime, the editorial
  motion system), `09-YOUTUBE-REFERENCE-PACK-LEARNINGS.md:199` "Reference-derived recipes should compile into a...",
  `GRILL-PIPELINE-VALUE-2026-09-13.md:92` "3. Decisions - effect recipes, the one-shot floor...",
  `OPERATOR-RULINGS.md:2759` "E96 - A one-shot is measured against floors before it is watched; recipes are the unit
  of authoring", `MOTION_GRAPHICS_FROM_STILL_IMAGES_BLUEPRINT.md:94` "Complete Remotion Implementation Recipe".
- Recall: docs_find **0 hits** for "beat plan", "capability comparator", "recipe coverage", "audit sheet", "badge
  ladder". The badge ladder's 2.05/1.30 law exists only in the grill ledger and in `recipes_r1.md` R1 - nothing in the
  docs layers names it, so it is un-findable today.
- Recall: docs_find "one-shot floor" = 2 hits, both the grill ledger (`:92` decisions). There is no floor tool.
- Recall: docs_find "wipe_right" = 6+ hits: `TRANSITIONS-REVIEW-2026-09-06.md:132`, `BUILD-PIPELINE.md:98`,
  `OPERATOR-RULINGS.md:1419` (E47), topic `wipe-right` (5 sections) - and the effects layer answers with **`exit:wipe`**
  ("The wipe scene exit", `wired`, aliases "wipe/peel", "carried-light cross-reveal", "page wipe", "Directional wipe"),
  whose `options` ALREADY carry the token `wipe_right`. R26-108's wipe half is closed by P55's option list; what is
  missing is a way for a recipe MEMBER to name that option (below, T1 + T4).
- Recall: docs_find "Ken Burns" = 6+ hits, none an effects-layer card (memory `nothing-ever-goes-truly-still`,
  `shorts-lane-phase1-standard`, `OPERATOR-RULINGS.md:1398` E46, two ComfyUI research reports). Confirmed by reading the
  catalogue: no card on any axis carries `ken` or `burns` in id, title or alias. R26-108's Ken Burns half is real.
- Recall: BACKLOG read verbatim - **R26-103** (recipe cards: "one recipe = ordered card ids + offsets + the sentence act
  + `proof: {project, build, t}`; status `proven` ... / `candidate`; the P55 generator writes them into
  `docs/EFFECTS-CATALOG.md` and `effects_card.py` resolves a recipe by name; the drift gate refuses a `proven` recipe
  without an instant and a member that is not a card; `authoring/recipes.py` presets"), **R26-104** (the floor v2: the
  five floors + "the parity table against the best approved short (Japan) - events/min reported, never a floor. The
  measures and their extraction from a compiled timeline are in `recipes_r1.md` s1 (`walk.py`, `cooc.py`)"),
  **R26-108** (the catalogue gaps).
- Recall: memory `one-shot-floor-recipes-not-events` ("a thin cut is busy, not slow"; "an effect the author never
  combines is an effect the viewer never sees"), `first-pass-additive-capability-led` ("the comparator before the
  series, a capability inventory per beat, parity with the approved shorts, a fix never lowers motion; gate-clean is not
  ready"), casebook `the-thin-one-shot/CASE.md` ("**The gate:** none - JUDGE. Gate-clean is not ready. A
  reference-parity reading ... would catch part of it."), `thresholds-from-the-reference` (measure the reference first
  with the same tool), `judge-the-frame-not-the-diff`, `composite-effects-keep-every-phase`.
- Recall: `docs/GATES-REGISTRY.jsonl` id families measured - G 0..48 (58 records), J, M 1..34 (36 records, M13 absent),
  S, V. **The next free M id is M35**; the registry's scan covers 5 checkers only (`build_gates_registry.py` `FAMILY`).

### What already exists - and exactly what it does not do

| piece | what it covers | what it does NOT cover |
| --- | --- | --- |
| P55 cards: `configs/effect_card.schema.json` (`effect_cards.v1`, closed, 18 axes), `effects/cards/*.json` - **125 cards** (43 live, 73 wired, 7 declared, 1 draft, 1 planned), with `phases`, `blends`, `options`, `dials`, `lives`, `doctrine`, `proof.first_use`, `implicit` | one card per EFFECT, axis-qualified ids, aliases with sources, the WHEN pulled from the compiler, dial values pulled from the module | a COMBINATION. No card names another card; no order, no offsets, no "these five fired together at 50.40 in Steel". The operator's unit of authoring has no file |
| `build_effects_catalog.py` (462 lines): `load_cards`, `check_unique`, `compiler_when`, `dial_values`, `resolve_cite` (through `DOCS-INDEX.jsonl`, `NAMED_DOCS`, `BACKLOG_ROW`, `RULING_ID`), `AMBIGUOUS_NAMES`, `AXIS_ORDER`, `render_md` / `render_jsonl`, `--write`/`--check`, deterministic LF | the generator pattern to extend: cards in, `docs/EFFECTS-CATALOG.{jsonl,md}` out, every truth pulled not copied | `AXIS_ORDER` has no `recipe`; `load_cards` reads one directory; nothing reads a members list |
| `effects_catalog_check.py` (459 lines, the drift gate's 8 checks): `check_coverage` (every compiler token has a card or is a parent's option), `check_phantoms`, `check_anchors` (`lives.symbol` grepped in `lives.path`), `check_proof` (golden + test exist), `check_examples` (run through the compiler's own validators), `check_aliases` (folded uniqueness), `check_phases`, `check_when` | the failure modes a card can have, each proved by a broken tmp copy in `test_effects_catalog_drift.py` | no check that a member exists, that a `proven` proof is real, or that a recipe's members actually fire together at the instant it claims |
| `authoring/effects.py` (`normalise`, `load`, `find` with 4 tiers - id, token, title/alias equality, substring - `suggest`, `card` raising `LookupError` on ambiguity), `effects_card.py`, `build_effects_gallery.py`, the `docs_find.py` `Layer("effects", …, ("id","title","aliases","does","token"), detail_only=True)` scanned FIRST | name -> card resolution from the generated layer only, one source for every reader | `find`'s tiers key on `token` and `lives.path`, which a recipe has not; no `preset()`; the gallery has no Recipes section |
| `self_watch.py` (516 lines): `run_gate` -> `parse_gate` (`ROW_RE = ^\s*\[(PASS \|FAIL \|WARN \|INFO \|JUDGE)\]\s*(\S+)\s*(.*)$`), `section1` (6 tool-filled rows), `O_ROWS` (O1-O10, the agent's read), `verdict` (**a FAIL in section 1 = `NOT CLEAN - <row>`**), `opening_sheets` via `probe.contact_sheet`, `write_html` | the exact hook E96 needs: a bar that runs tools, keeps rows, and refuses to offer a watch on a FAIL | it has no richness row at all: the motion gate caps errors (stillness, collisions, cadence) and sets no floor. M01-M34 would have passed the thin cut, and did |
| `lint_species_choice.py` (609 lines): `ACTS` (11), `ACT_SPECIES`, `load_sentences` (**the build's `timeline.json` `sentences` [{text,start,end}] on the take's clock** - the beat), `--propose` (P53 T8) with `PROPOSE_FILL`, `draft_row`, `propose_target`, and its documented limit: *"`--propose` reads the WORLD UNDER a sentence, never the referent"*; `--when` generates `SPECIES-BY-SENTENCE.md` s4 | act -> single species, per sentence, with a stale-check test; the sentence clock every floor row needs | it proposes ONE species at a time. Nothing proposes a recipe, so an author who follows the proposer authors exactly what E96 forbids |
| `gate_motion_density.py` (2,637 lines, rows M01-M34 on the compiled timeline + `evidence-dock.json` + `motion-plan.json`), `build_gates_registry.py` (`FAMILY`, 5 checkers, `--write`/`--check`, cites through DOCS-INDEX) | the row protocol (`[LEVEL] Mxx text`), the registry generated from source by `ast`, ids greppable with their thresholds | every row is a per-window defect check. The M family has no whole-cut aggregate, no reference-parity table, and no recipe awareness |
| `probe.py` (`--sheet`, `contact_sheet(pngs, out, tile, per_sheet)`), `change_report.py` ("the diff line, the two frames at the affected instant and the gate delta"; the BEFORE build is produced, never guessed) | the two-frames-at-an-instant pattern the recipe audit sheet needs, already used by SELF-WATCH's opening sheets | nothing sets a build's frames beside ANOTHER build's frames at a different instant (the proof cut) |
| The spike `docs/research/runs/grill_pipeline-value/recipes_r1.{md,jsonl}` (15 seeds with members, offsets, first-fire instants, the act each serves; s4 slots all 67 unused cards; s5 the negatives with the places searched) mined by `walk.py` / `cooc.py` / `cards.py` | the DATA this plan turns into files, and the two algorithms the gate reuses: the timeline walk (events with a class + card id + t) and the 6 s-window n-gram co-occurrence | both files and all three scripts are **gitignored / in a session scratchpad that will be deleted**. Nothing in the repo can re-derive them; T2 exists for that reason |
| The four compiled timelines (the calibration set) | `schema_version: scene_evidence_timeline.v1`; `scenes[].{scene_id, span, world, docks, species, exit}`; `world.page.{builder, variant, enter, snap_from}` or `world.{asset_id, ken_burns{scale,x,y}, kind}`; `docks[].{slide, slot, enter, exit, badge_at, kind, park, read_s, ...}`; `evidence[slide].{species, chart{...}, document, badges}`; `narration.words_path` -> the build's `timeline.json` | Steel's timeline carries **`species: []` on all 75 scenes and 0 ledger pages** (75/75 worlds are plates): the long form and the shorts speak disjoint vocabularies, so no seed can be `proven` on both (T8 states the consequence) |

**The gap, in one line:** the catalogue knows 125 effects and not one combination; the bar refuses a cut for defects
and accepts one for being empty; and the proposer teaches an author to pick single effects, which is the habit E96 was
ruled against.

## Intent And Acceptance

Intent: an author (agent or human) asks for a BEAT and gets a proven combination with offsets and the instant that
proves it; writes the comparator and the recipe per beat before any row; and cannot offer a cut for a watch that is
below the floors the operator ruled - with the floors measured by the same tool on the best approved short first.

Acceptance (all observable, all from the main checkout):

1. `python content/video_engine/scripts/effects_card.py "badge ladder"` prints `recipe:badge-ladder` - its members in
   order with offsets (`dock_kind:image` + `dock_payload:chart` -> badge +2.05 s -> badge +1.30 s ...), its act, its
   dials (`FIRST_BADGE_S 2.05`, `BADGE_GAP_S 1.30`), and its proof (`steel-and-paper / build-f / 50.40`).
   `python content/video_engine/scripts/docs_find.py "badge ladder"` finds it (0 hits today).
2. `docs/EFFECTS-CATALOG.jsonl` carries the recipes as records with `axis: "recipe"` and `members` as card ids;
   `docs/EFFECTS-CATALOG.md` gains a "Recipes" section; both generated by `build_effects_catalog.py --write`;
   `build_docs_layers.py` reports every layer in sync.
3. `effects_catalog_check.py` FAILS, naming the recipe, when: a member is neither a card id, a listed option of a
   member card, nor another recipe; a `proven` recipe has no `proof`; a `proven` recipe's proof timeline is absent on
   disk; a `proven` recipe's members do NOT all fire within its window at that instant (the co-occurrence matcher); an
   alias collides with any card or recipe alias (or sits in `AMBIGUOUS_NAMES`); a recipe names fewer than 2 members.
4. `from authoring import recipes as RX; RX.preset("the badge ladder")` returns the ordered members with offsets and
   option defaults as DATA the author binds assets and targets into - no episode facts, no allocator.
5. `lint_species_choice.py <project> --propose` proposes RECIPES per act beside single species, keeping the proposer's
   stated limit verbatim and adding no allocator.
6. `python content/video_engine/scripts/gate_one_shot_floor.py <build>` prints rows M35-M42 in the gate row protocol
   and a parity table against Japan (measured at run time from Japan's own timeline) and Bravos (quoted); the same rows
   appear in `<build>/SELF-WATCH.md` section 1, and a cut under a floor makes the report say
   `NOT CLEAN - the one-shot floor (M3x): ...`.
7. The floor's fixture asserts the measured truth, not a hope: on `japan-tariff-trick/build-short` the rows read
   `2 chart forms`, `0 chart-to-chart transforms`, `docks on 0.36 of 25 beats`, `narrative:chart 1.00`,
   `28.1 events/min (INFO)`; on `normal-for-which-bridge/review-v1` the same rows read
   `1 / 0 / 0.00 / 0.20` and the verdict is `NOT CLEAN`.
8. `<build>/self-watch/recipes/<beat>.png` holds, per beat that carries a recipe, the build's frames at the recipe's
   instants beside the PROOF cut's frames at its own instants, listed in SELF-WATCH as INFO (the critic's raw
   material; no judge in this plan).
9. `sync_kinetics.py --check` passes unchanged and every golden frame is byte-identical: this plan touches no engine
   module, no compiler and no golden.

## Scope

- T1 the recipe schema (`effect_recipes.v1`) and the name ledger; T2 the seeds re-derived from disk (read-only,
  because the spike's files are gitignored and its scripts live in a temp scratchpad); T3 the 15 `proven` recipe files.
- T4 the generator, the drift gate's four new checks, the name resolver, the CLI and the gallery.
- T5 `authoring/recipes.py` and `--propose` recipes.
- T6 `gate_one_shot_floor.py` + the calibration fixture (the reference measured first).
- T7 the SELF-WATCH rows and the recipe audit sheet.
- T8 R26-108's real gaps (the Ken Burns card, the member-option form, the long-form verdict).
- T9 the candidate recipes (the 67 unused cards in their slots).
- T10 doctrine: CAPABILITIES rows, a doc 29 pointer, BACKLOG marks, the routing line, the kit's `__init__`.

## Not Building

- **No engine, no compiler, no goldens.** Not one line of `scene-evidence-engine.mjs`, `build_scene_timeline_f.py`,
  `kinetics/*.mjs`, `species/*.mjs`, `tests/golden/**`. The grill's build order: *"P55's own generator and gate extend;
  no engine work."* Verification asserts it (`sync_kinetics --check`, the golden suite).
- **No `chart_to` implementation, no new page builder, no relation layer, no brush.** R26-105 (E97, the rig) and
  R26-106 (the vector brush) are separate plans; the floor MEASURES the absence of a chart-to-chart transform, it does
  not build one.
- **No LLM judge and no viewer run.** The audit sheet is raw material for a critic (human or agent); JUDGE rows stay
  where they are (E96: *"JUDGE keeps sequence and taste, read against the best approved short, never against the
  gates"*).
- **No events/min floor.** E96 (3): *"Events per minute is NOT a floor: the thin cut would have passed it."* It is
  reported (M42) and can never FAIL.
- **No re-judging of shipped cuts.** No approved build is re-authored, re-rendered or marked failing by this plan
  (HG1's recommendation is exactly this).
- **No allocator.** `recipes.py` and `--propose` return candidates; the author binds. PIPELINE.md: *"Stage 7 is
  AUTHORED. There is no allocator."*
- **No new retrieval layer.** Recipes ride the existing effects layer in `docs/EFFECTS-CATALOG.jsonl` (one source, one
  budget); `docs_find.py` and `build_docs_layers.py` `LAYERS` are unchanged.
- **No studio, editor or console work** (R26-102, P30). The editor's panel is untouched.
- **No BACKLOG row closed by an agent**: T10 marks R26-103 / R26-104 / R26-108 and is the parent's.

## Human Gates

**HG1 - the floor calibration (operator, BEFORE T6 writes a threshold).** This is the plan's one open decision and it
is surfaced, not hidden: **three of E96's five floors fail the approved Japan short.** Measured 2026-09-13 by the
parent from the four compiled timelines with the grill's own walk (numbers reproduced in T2's artifact):

| floor (E96) | Japan (APPROVED 09-09) | Tokyo v2 (render approved 09-06) | Steel (shipped long) | the thin one-shot |
| --- | --- | --- | --- | --- |
| >= 3 distinct chart forms | **2** (line, bars) FAIL | **2** FAIL | 5 (its 32 chart docks) PASS | **1** FAIL |
| >= 1 chart-to-chart transform | **0** FAIL | **0** FAIL | **0** FAIL | **0** FAIL |
| docks on >= 1/3 of beats | **0.36** of 25 PASS (0.32 under the other definition - see below) | 0.28 FAIL | 0.80 PASS | **0.00** FAIL |
| >= 60% of beats on a proven recipe | <= **0.44** (11 seed instances in 25 beats; exact number measured in T6) | lower | n/a (no `species` array) | ~0.16 (3 seeds, degraded) |
| narrative : chart >= 1:1 | **1.00** PASS (exactly) | 1.00 PASS | 2.34 PASS | **0.20** FAIL |
| events/min (never a floor) | 28.1 | 18.2 | 16.8 | 17.9 |

The definition itself decides one verdict: a beat "carries a dock" at **0.36** if the dock is ON SCREEN during the
beat (windows intersect) and **0.32** if the dock ENTERS during it. The parent recommends the on-screen reading - a
held dock is precisely Bravos' "builds inside a held frame" (`bravos-reference`), and it makes the reference pass the
rule as ruled.

**The recommendation (one of two; the operator picks):**

- **(A) recommended - the floors bind, the past is not re-judged.** The four cuts on disk are an enumerated
  `PREDATES_E96` set in the gate (japan/build-short, tokyo/build-short.v2, steel-and-paper/build-f,
  normal-for-which-bridge/review-v1); every other build - i.e. everything authored from now on - is judged by the
  floors as E96 states them (3 forms, 1 chart-to-chart, 1/3 docks on the on-screen reading, 60% recipe coverage,
  1:1 narrative:chart). On a predating build those two never-shipped rows print `INFO ... predates E96` with the
  measured number, and the fixture asserts that wording on Japan. The parity floors are additionally held to the
  reference's own numbers measured at run time (`>= Japan's docks-per-beat`, `>= Japan's narrative:chart`), per
  `thresholds-from-the-reference`. A build cannot opt out by deleting a file; adding a build to `PREDATES_E96` needs a
  ruling, and the test asserts the tuple's contents.
- **(B) the alternative - every floor WARNs until the first approved cut carries them.** Honest about the fact that no
  cut has ever cleared 3 forms + a chart_to, but it reproduces the exact failure mode E96 was ruled against: the thin
  one-shot was offered at 0 FAIL / 1 WARN. A WARN does not stop an offer.

Also inside HG1, the one number that is an ADVANCE on the reference rather than parity: **60% proven-recipe coverage**.
Japan's own coverage is at most 0.44. The parent recommends keeping 0.60 as ruled (it is the point of the rule) with
Japan's measured coverage printed in the same row, so the operator sees the gap it demands.

**HG1 ANSWERED 2026-09-13 (the operator):** *"For HG1, A sounds righ for approval. 60% sounds like a good target to start with for the new reference."* -> (A) binds: the floors as E96 states them on everything authored from now on; the four cuts on disk are the enumerated `PREDATES_E96` set (INFO with the measured number, never re-judged); the parity floors additionally held to Japan's own run-time numbers; the on-screen reading of "a beat carries a dock" (the parent's recommendation, unopposed); 60% proven-recipe coverage KEPT as the new reference's target, Japan's measured coverage printed beside it. T6 is unblocked.

**HG2 - the first cut measured under the floor (operator, after T7 and the first real build).** One read of a
SELF-WATCH report carrying M35-M42 and one recipe audit sheet: keep the thresholds, move them, or retire a row. Nothing
in the plan depends on the answer; the rows are data until then.

Parent decisions recorded so they are not re-litigated (NOT operator gates): the recipe schema (T1, below); the recipe
NAMES and aliases (the operator delegated naming to the parent - the P55 HG1 precedent - and the names use the doc's or
the operator's own words where they exist: THE VERDICT STACK, the badge ladder, the card becomes the chart); a NEW
script rather than a section of `self_watch.py` or of `gate_motion_density.py` (rationale in Execution Path); the gate
row ids **M35-M42** (rationale in Execution Path).

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` - Dispatch mapping, Lane write sets, Hand-off policy, PRP Format.
- `docs/content-video-engine/GRILL-PIPELINE-VALUE-2026-09-13.md` - s0 (what the operator settled, verbatim), s1 (the
  measures table), s3 decisions 1, 2 and 6, s4 (rejected: events/min as the floor), s5 (the build order).
- `docs/portable/OPERATOR-RULINGS.md` **E96** (the whole entry: a beat is a RECIPE; floors before a watch; events/min
  never a floor), plus E21, E25, E49, E56, E60, E61, E87, E93, E95 (the rulings a floor row must not contradict).
- `docs/content-video-engine/BACKLOG.md` **R26-103**, **R26-104**, **R26-108** verbatim (and R26-105/106/107 to see
  what this plan is NOT).
- `docs/research/runs/grill_pipeline-value/recipes_r1.md` (all of it: s1 measures, s2 the 15 seeds with members,
  offsets and fired instants, s3 the thin cut's gap, s4 the 67 slots, s5 the negatives) and `recipes_r1.jsonl`.
- The spike's mining scripts, while they still exist:
  `C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad/grill-pipeline/`
  `walk.py` (`events()` - the class/card/t walk; `measure()` - comps, builds, forms, docks, narrative:chart,
  transforms), `cooc.py` (`tok()` normalisation, `WIN = 6.0`, `ngrams(nmin=2, nmax=5)`), `cards.py`.
- P55 machinery, read before extending: `content/video_engine/configs/effect_card.schema.json`,
  `content/video_engine/effects/cards/*.json` (read `exit.json` - `exit:wipe` options - and `dock_payload.json`,
  `chart_dock.json` for the taken titles/aliases), `scripts/build_effects_catalog.py` (`AXIS_ORDER`,
  `AMBIGUOUS_NAMES`, `load_cards`, `check_unique`, `resolve_cite`, `dial_values`, `render_md`),
  `scripts/effects_catalog_check.py` (all 8 checks + `Source`, `check_examples`, `_fold`),
  `scripts/authoring/effects.py` (`_tiers`, `find`, `card`), `scripts/effects_card.py`,
  `scripts/build_effects_gallery.py`, `scripts/docs_find.py` (the `LAYERS` effects entry and the two budget rules:
  *"each layer takes a fair share of what is left (`ceil(remaining / layers left)`, at least one)"*),
  `scripts/build_docs_layers.py` (`LAYERS`), and the tests `test_build_effects_catalog.py`,
  `test_effects_catalog_drift.py`, `test_authoring_effects.py`, `test_build_effects_gallery.py`.
- The bar: `scripts/self_watch.py` (`ROW_RE`, `parse_gate`, `run_gate`, `section1`, `verdict`, `render`,
  `opening_sheets`, `write_html`), `docs/content-video-engine/SELF-WATCH.md`, `tests/test_self_watch.py`.
- The beat clock and the proposer: `scripts/lint_species_choice.py` (`ACTS`, `ACT_SPECIES`, `load_sentences`,
  `resolve_inputs`, the proposer block's header comment and `PROPOSE_FILL`), `docs/content-video-engine/SPECIES-BY-SENTENCE.md`.
- The row protocol and the registry: `scripts/gate_motion_density.py` (its header's row table and how a row is
  printed), `scripts/build_gates_registry.py` (`FAMILY`, `FAMILIES`, `LEVELS`, the `ast` read), `docs/GATES-REGISTRY.md`
  (scope note: 5 checkers).
- The sheets: `scripts/probe.py` (`--sheet`, `contact_sheet`), `scripts/change_report.py` (header - the BEFORE build is
  produced, never guessed).
- Memory: `docs/agent-memory/operator/one-shot-floor-recipes-not-events.md`,
  `first-pass-additive-capability-led.md`, `casebook/the-thin-one-shot/CASE.md`, `bravos-reference.md`,
  `thresholds-from-the-reference.md`, `never-pipe-gated-steps-to-tail.md`.
- `.claude/PRPs/plans/P55-THE-EFFECTS-CATALOGUE.plan.md` (its T3/T4/T8 acceptance, its Not Building, and its lesson:
  three test pins went red because only the slice's suites were run).

## Execution Path

1. **Decide, then re-derive.** T1 (parent) fixes the schema and the names. T2 (explorer, read-only) reproduces the 15
   seeds from the four timelines on disk: the spike's evidence is gitignored and its scripts live in a session
   scratchpad, so without T2 every `proven` proof in T3 would rest on a file that will not exist.
2. **Data before machinery.** T3 writes the 15 recipe files; T4 extends the generator, the gate, the resolver, the CLI
   and the gallery in one slice because the drift gate and the generator share `load_cards`/`check_unique` and must
   land together (P55's `--check` is called by `build_effects_catalog.py --check`, which `build_docs_layers.py` runs).
3. **The author's surface, then the measure.** T5 (kit + proposer) and T6 (the floor gate) are independent of each
   other and both depend on T4; the parent may run them in parallel (disjoint write sets).
4. **Wire the bar last.** T7 needs T6's rows and T4's catalogue. T8 (R26-108) and T9 (candidates) both regenerate the
   catalogue artifacts, so they are serialised AFTER T4 and after each other. T10 (doctrine) is last.
5. **Why a new script, not a section of an existing one.** `gate_motion_density.py` is 2,637 lines and owns per-window
   DEFECT rows on one input family; the floor rows are whole-cut AGGREGATES over three inputs (the compiled timeline,
   `docs/EFFECTS-CATALOG.jsonl` + the recipes, and the reference cut's own timeline), and one of them shells out to no
   one. `self_watch.py` already composes gates as subprocesses through `run_gate` -> `parse_gate` and is 516 lines of
   report; a floor computation inside it would make the bar its own gate. So: a new `gate_one_shot_floor.py` printing
   the same `[LEVEL] id text` rows, added to `build_gates_registry.py` `FAMILY` as family `floor` (the registry's
   generated scope note becomes 6 checkers), and called by `self_watch.py` exactly as the motion gate is.
6. **The ids: M35-M42.** M34 is the highest M and M13 is absent; the M family means "measured from the built episode",
   which is what these rows are. Rejected: a fresh prefix (`F01+`) - the docs, the memories and the operator's reading
   of a report all treat an M row as a measured-build row, and `parse_gate`'s `ROW_RE` does not care about the prefix;
   the registry keys on the id and prints each row's source path, so two scripts sharing the family stays greppable.
   Rejected: extending the G family (script-side / speech rows).

### The recipe schema (T1 proposal - the parent confirms or amends)

`content/video_engine/configs/effect_recipe.schema.json`, `$id: effect_recipes.v1`, one file per recipe under
`content/video_engine/effects/recipes/<slug>.json` (one file per recipe, not per axis: a recipe is the merge-collision
unit - two lanes adding recipes never touch the same file).

```
schema_version  "effect_recipes.v1"
id              "recipe:<slug>"                     slug = [a-z0-9-]+
title           the canonical human name             ("The badge ladder")   - the doc's or the operator's word where one exists
aliases         [{name, source}]                     unique across cards AND recipes; never a name in AMBIGUOUS_NAMES
acts            [<act>]                              >= 1 of the 11 SPECIES-BY-SENTENCE acts (the schema's own enum, as effect_card.schema.json `serves`)
members         [{card, option?, offset_s, role, options?, optional?}]   ORDERED, >= 2
                  card      a card id in docs/EFFECTS-CATALOG.jsonl, OR another recipe id (nesting, acyclic)
                  option    a token listed in that card's `options` (this is how a member names `exit:wipe` + `wipe_right`)
                  offset_s  seconds from the recipe's first member (the first member is 0.0); a range as [lo, hi]
                  role      one line: what this member does IN the combination ("the claim's qualification stamps")
                  options   authoring defaults the preset hands the author (e.g. {"dur": 0.9}); never episode facts
                  optional  true when the seed fired with and without it (the matcher does not require it)
window_s        the span the members must fall inside for a fire to count (default 6.0 - cooc.py's WIN)
dials           {NAME: value} the measured laws, as measured  (badge ladder: {"FIRST_BADGE_S": 2.05, "BADGE_GAP_S": 1.30};
                R14: {"EMPHASIZE_EQUALS_DATUM": true})   - each with a `dials_source` line naming where it was measured
does            one sentence: what the viewer sees the COMBINATION do
doctrine        cites resolved through DOCS-INDEX at build (E96, 29 s9.24, CAPABILITIES <row>, BACKLOG R26-103)
status          proven | candidate
proof           REQUIRED when proven: {project, build, timeline, t, members_at: [t...]}   - t = the first-fire instant
source          the seed id in the spike ("recipes_r1 R1") and T2's re-derived artifact path
count           how many times the ordered set fired in an approved cut (a recipe that fires once is a decoration; 4x is a grammar)
```

Two rules the gate enforces and the schema cannot: a `proven` recipe's `proof.timeline` exists on disk AND its members
fire inside `window_s` at `proof.t` (the matcher); a member's `card` resolves in the generated catalogue (so a recipe
can never name an effect the compiler does not accept - the card already carries that guarantee).

### The recipe names (T1, parent-owned; the words come from the record)

`recipe:badge-ladder` "The badge ladder" (R1, proven, steel/build-f @50.40) · `recipe:plate-dock-wipe` "The plate, the
dock and the carried wipe" (R2, @317.80) · `recipe:held-dock-across-the-cut` "The dock outlives the world change"
(R3, @492.30) · `recipe:verdict-recap` "The nine-proof recap" (R4, @701.73 - NOT "the verdict stack": that title and
its seven aliases belong to the card `dock_payload:stack`, so the recipe's name must differ or `check_aliases` fails)
· `recipe:test-card-rows` "The test card's rows on their words" (R5, @492.30) · `recipe:card-becomes-the-chart` "The
card becomes the chart" (R6, japan @0.82) · `recipe:trace-callout-ladder` "The trace-callout ladder" (R7, japan @9.22)
· `recipe:held-page-hosts-the-docks` "The held page that hosts the docks" (R8, tokyo @1.99) ·
`recipe:spotlight-held-past-the-cut` "The spotlight that holds past its boundary" (R9, japan @2.67) ·
`recipe:read-park-build-write` "Read, park, build to the datum, write the figure" (R10, japan @71.10) ·
`recipe:still-life-breather` "The still-life breather" (R11, tokyo @38.96) · `recipe:punch-then-callout` "The punch,
then the callout names it" (R12, tokyo @44.88) · `recipe:outro-clip-life` "The outro clip carries life" (R13, japan
@79.08) · `recipe:emphasized-bar-lit` "The emphasized bar, badged then lit" (R14, japan @42.81) ·
`recipe:dock-lands-page-renames` "The dock lands, the page renames itself" (R15, japan @25.58).

### The beat plan (T5) - the artifact the author writes BEFORE rows

`<build>/BEAT-PLAN.md` + `<build>/BEAT-PLAN.jsonl`, one record per beat (a sentence of `load_sentences`), each:
`{beat, t0, t1, text, acts, comparator: {claim, compared_to, series, source}, recipe: <id> | null, why_none,
capabilities: [<card id>...], bound: {asset|target per member}}`. It is AUTHORED (the proposer drafts candidates; the
author keeps or deletes - no allocator). The floor gate reads it for **M41**: a beat with no record, or a record whose
`comparator.compared_to` is empty, or `recipe: null` with no `why_none`, is a gap named in the row; the floors that
measure the CUT (M35-M40) never read it - they read the compiled timeline, so a beat plan cannot talk a thin cut
through.

### The floor rows (T6) - definitions from the timeline schema, exactly

| id | row | measured from the compiled timeline | level |
| --- | --- | --- | --- |
| M35 | distinct chart forms >= 3 | a ledger page's `(world.page.builder, world.page.variant)`, plus each chart dock's form from its own `evidence[slide].chart` block's discriminator (series / values+bars / shares / checklist rows / panels). Japan 2, Tokyo 2, Steel 5, thin 1 - reproduces the grill's table | FAIL / PASS (INFO "predates E96" on the enumerated set) |
| M36 | chart-to-chart transforms >= 1 | a `species[].kind == "chart_to"` (any of the 5 verbs), OR a ledger page whose `page.enter` is `morph` or `stamped` AND whose previous scene's world is also a ledger page. NOT counted: `enter: snap` with `snap_from` naming a dock (that is R6, a card->chart hand-off - Japan's two), `spiral`, `mount`, `axes`. All four cuts: 0 | FAIL / PASS (INFO predates) |
| M37 | docks on >= 1/3 of beats | a beat (a `sentences[]` window from `narration.words_path`) carries a dock when a dock's `[enter, exit]` intersects it (HG1's on-screen reading). Japan 0.36, Tokyo 0.28, Steel 0.80, thin 0.00. The floor is `max(1/3, Japan's own)` under HG1 (A) | FAIL / PASS |
| M38 | proven-recipe coverage >= 60% of beats | a beat carries a recipe when that recipe's ordered members all fire within `window_s` inside (or overlapping) the beat - `cooc.py`'s matcher over the walk's token stream. The row names the recipes found and their counts (a recipe firing once is named as a decoration) | FAIL / PASS |
| M39 | narrative : chart >= 1:1 | `(plate scenes + clip scenes) / (ledger pages + chart docks)`. Japan 1.00, Tokyo 1.00, Steel 2.34, thin 0.20 | FAIL / PASS |
| M40 | parity with the best approved short | the table: this cut vs Japan (measured at run time from Japan's own timeline with this same tool) vs Bravos (quoted from `bravos-reference`: 6.0 events/min, 2.5 compositions/min, ~6 forms, 50 docks) on all rows above plus compositions/min and builds:compositions | JUDGE (never FAIL - E96: JUDGE against the best approved short) |
| M41 | the beat plan covers every beat | `BEAT-PLAN.jsonl`: a record per beat, a comparator with a `compared_to` and a series/source, a recipe or a `why_none` | FAIL / PASS (WARN "no beat plan on disk" on a predating build) |
| M42 | events/min, compositions/min, builds:compositions | the walk's counts (event = cut + build; composition = cut - Bravos' own definitions) | INFO always - never a floor (E96 (3)) |

## Patterns To Mirror

- `build_effects_catalog.py` / `build_gates_registry.py` / `build_animation_registry.py`: stdlib only, deterministic,
  LF, `--write` / `--check`, the recipe in the generated file's header, cites resolved through `docs/DOCS-INDEX.jsonl`,
  values PULLED (a recipe's member `does` is never copied - it is read from the card at build).
- `effects_catalog_check.py`'s shape: one `check_*` function per failure mode, each returning problem strings that name
  the id; every one proved by a deliberately broken copy in a tmp dir (`test_effects_catalog_drift.py`).
- `gate_motion_density.py`'s row protocol and `self_watch.py`'s `run_gate` / `parse_gate`: a gate is a subprocess that
  prints `[LEVEL] id text` and a `RESULT:` line; the bar parses, never re-computes.
- `lint_species_choice.py`'s proposer header (the six-line refusal to become an allocator) copied in spirit into
  `authoring/recipes.py` and the `--propose` extension, and its stated limit repeated verbatim, not softened.
- `probe.contact_sheet` + `self_watch.opening_sheets` for the audit sheet; `change_report.py`'s "two frames at the
  affected instant" for its layout.
- `authoring/effects.py`: read ONLY the generated layer, one source for every reader; ambiguity raises and names the
  candidates.
- P55's own lesson, in Verification: run the whole `content/video_engine/tests` tree at the end, not the slice's suites.

## Task Slices

### T1: The recipe schema and the name ledger
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/configs/effect_recipe.schema.json`; this plan's schema and names sections (amended in place)
- Acceptance: `effect_recipes.v1` as proposed above, confirmed or amended: `members` ordered with `card`/`option`/`offset_s`/`role`, `acts` from the 11, `dials` with a `dials_source`, `status` + `proof` (required when `proven`, carrying `timeline` and `members_at`), `window_s` defaulting to 6.0, `count`, `source`; `additionalProperties: false` everywhere; the 15 names fixed (each distinct from every card title and alias - `recipe:verdict-recap` is the known collision) and recorded in this plan.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import json; s=json.load(open('content/video_engine/configs/effect_recipe.schema.json',encoding='utf-8')); print(s['$id'], sorted(s['$defs']['recipe']['required']))"`
- Evidence: 2026-09-13 `content/video_engine/configs/effect_recipe.schema.json` written (`$ref: #/$defs/recipe`; the Validate command prints `effect_recipes.v1 ['acts', 'aliases', 'count', 'does', 'id', 'members', 'schema_version', 'source', 'status', 'title']`). Amendments to the proposal, in the schema itself: `proof` gains an optional `scene`; `proof.timeline` must match `^content/video_engine/projects/.+\.timeline\.json$`; `dials_source` is a top-level string required whenever `dials` is present (`dependentRequired`); `status: proven` REQUIRES `proof` and `count >= 1`, `status: candidate` FORBIDS `proof` and pins `count: 0` (`if/then/else` - jsonschema Draft 2020-12, which `load_cards` already uses, enforces it, so the generator gets these for free); `backlog` rows allowed as on a card; member `options` values are number/string/boolean. Self-check (`scratchpad/p56/t1_schema.py`): one good recipe accepted, 7 broken variants refused (candidate with a proof, proven without one, one member, an unknown act, dials without a source, an upper-case slug, an extra key). The 15 names checked against all 125 cards' titles and aliases (lower-cased equality): no collision; `recipe:test-card-rows`' title contains the card title "The test card" as a SUBSTRING only (the id/title-equality tiers of `find` still resolve the card first - T4 pins it). Plan marked `running`, `prp_validate` PASS.

### T2: Re-derive the 15 seeds from the timelines on disk (read-only)
- Status: complete
- Owner: explorer
- Depends on: T1
- Write set: `docs/research/runs/p56-recipe-seeds/seeds.jsonl`, `docs/research/runs/p56-recipe-seeds/measures.md` (gitignored disk-as-bus; if the harness refuses the write, the parent saves the returned pack there)
- Acceptance: for each of the 15 seeds in `recipes_r1.md` s2, one JSONL row re-derived FROM the four compiled timelines (`japan-tariff-trick/build-short/japan-short.timeline.json`, `tokyo-tea-break/build-short.v2/tokyo-short.timeline.json`, `steel-and-paper/build-f/steel-and-paper.timeline.json`, `normal-for-which-bridge/review-v1/bridge-short.timeline.json`): the ordered member tokens as they appear in the timeline, the offsets, the first-fire instant, the count, the scenes, and whether the spike's number reproduces (state the delta when it does not - the spike's scripts are in a temp scratchpad and may be deleted before this runs; do not import them, re-derive). `measures.md` reproduces the grill s1 table plus the four HG1 columns (chart forms, chart-to-chart transforms, docks-per-beat under BOTH definitions, narrative:chart, events/min, compositions/min) and Japan's proven-recipe coverage counted by hand from the seed instants. Every negative stated as "not found in <the files searched>".
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import json; rows=[json.loads(l) for l in open('docs/research/runs/p56-recipe-seeds/seeds.jsonl',encoding='utf-8')]; print(len(rows), sorted(r['seed'] for r in rows))"` (the parent then spot-checks three instants in the timelines)
- Evidence: 2026-09-13 explorer wrote `docs/research/runs/p56-recipe-seeds/{derive_seeds.py, seeds.jsonl, measures.md}` (gitignored); the Validate command prints `15 ['R1','R10',...,'R9']`. Parent spot-check on the timelines: Steel s02 `ev-bravos-original-v1` enter 9.50, badge_at [11.55, 12.85] (+2.05, +1.30); Japan s01 `dock-b-holdings` 0.82-1.82 and s02 `page.enter: snap`, `snap_from: dock-b-holdings` at 1.82; Japan s06 `page.emphasize: 1` and the spotlight at 42.81 targets datum index 1 (+7.55 from the page at 35.26). Reproduction: 13 of 15 reproduce; R2 counts 23 as the full five-member set (the spike's 16 was the four-member head; its 317.80/457.80/595.50 were scene END times); R12 counts 1 (Tokyo s05 is reversed - callout before punch); R6 has NO `idle:live` member (`world.page.idle` absent on Japan s02/s06); R9: 3 of 4 spotlights truly outlive the span (s02's `until` equals the span end). CORRECTIONS to the grill s1 table / this plan's HG1 table: Steel is 124 builds / 199 events / **14.8 events/min** (the spike's 151/226/16.8 was a hand-entry error; its own walk printed 14.8), builds:compositions 1.65; Japan's enters-during docks-per-beat is **0.28** (7 of 25), not 0.32 (Japan has only 6 dock enters); Japan narrative:chart is 1.00 (the plan was right, the spike's 1.40 ignored the 2 chart docks). On-screen docks-per-beat 0.80 / 0.36 / 0.28 / 0.00, forms 5 / 2 / 2 / 1, chart-to-chart 0 / 0 / 0 / 0, narrative:chart 2.34 / 1.00 / 1.00 / 0.20 all reproduce. T6's fixture uses the re-derived numbers (Steel 14.8), never the spike's.

### T3: The 15 proven recipe files
- Status: complete (T3b amendment landed 2026-09-13 - see the end of Evidence)
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/effects/recipes/*.json` (15 files)
- Acceptance: one file per seed, valid against `effect_recipe.schema.json`, `status: proven`, each carrying T2's re-derived members (card ids only - every member resolves in `docs/EFFECTS-CATALOG.jsonl`; `exit:wipe` + `option: wipe_right` where Steel's exit is `wipe_right`), offsets, `acts` from SPECIES-BY-SENTENCE, `count`, `proof {project, build, timeline, t, members_at}`, `source` naming both `recipes_r1 R<n>` and T2's row, and the measured dials where a law exists (`recipe:badge-ladder` `FIRST_BADGE_S 2.05` / `BADGE_GAP_S 1.30` with `dials_source` "41 of 43 Steel docks, 40 gaps all exactly 1.30"; `recipe:emphasized-bar-lit` `EMPHASIZE_EQUALS_DATUM true` with "3 of 3, Japan s06/s08 + Tokyo s05"). No recipe title or alias collides with a card's (`dock_payload:stack` holds "The verdict stack", "evidence wall", "nine-proof wall", "the verdict pile-up"; `chart_dock:checklist` holds "The test card" and 11 more) - checked by running T4's gate once it exists, and by `rg` in the meantime.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "import json,glob; ps=sorted(glob.glob('content/video_engine/effects/recipes/*.json')); rs=[json.load(open(p,encoding='utf-8')) for p in ps]; print(len(rs), [r['id'] for r in rs], sorted({m['card'] for r in rs for m in r['members']}))"`
- Evidence: 2026-09-13 luna wrote the 15 files; parent re-validated every file with `jsonschema.Draft202012Validator` + a member/option/proof-path check (`15 files, 0 with problems` from the lane; the parent's own pass agrees except the badge members below). Collision check `no collisions` / `unique across recipes` / `in AMBIGUOUS_NAMES: none`. Lane deviations accepted: R2/R3/R11/R13 dropped the UNCARDED world plate, clip world, Ken Burns and dock-exit members (no card id exists; the roles name them) - R2/R3 rebased to the dock (proof t 9.50, s02); R3 counts 15 (the 15 of 20 held docks whose world change is `wipe_right`; the 5 `cut` ones named in the role); R13 gained `exit:dip` at +6.20 (measured on both instances) so it keeps two members; R14's page-badge member folded into the bars member's role (count 2, window 8.0); windows widened where the seed spans longer (R2 31.0, R3 22.0, R4 26.0, R5 10.0, R8 35.0, R9 12.0, R14 8.0, R15 11.0, each stated in `does`); E60 not cited (it is the breakthrough rescale, not a hand-off) - E61/E49 cited instead. PARENT FINDING, NOT accepted: the badge ladder's four badge members were written as `dock_kind:image` because a BADGE has no card (`dock_kind:image` only mentions badges in prose). A badge is an effect the viewer sees, so T8 adds `dock_option:badge` (the badge rail: `badge_at` on a dock, `badges[]` on a page) beside `plate_option:ken`, plus `plate_option:world` (the narrative plate world) and `plate_option:clip` (the clip world) as implicit cards; then a T3 amendment re-members badge-ladder (badges -> `dock_option:badge`), plate-dock-wipe (plate + ken), held-dock-across-the-cut, still-life-breather and outro-clip-life (their worlds). Until then the T4 gate correctly fails `recipe:badge-ladder`'s members. **T3b (luna, after T8):** badge-ladder -> `dock_kind:image` @0 then `dock_option:badge` @2.05/3.35/4.65/5.95 (the last three optional), proof steel s05 50.40 [50.4, 52.45, 53.75, 55.05, 56.35], count 41 (= T2); plate-dock-wipe -> `plate_option:world`, `plate_option:ken`, `dock_kind:image`, `dock_payload:chart` @0, `dock_option:badge` @2.05 (optional), `exit:wipe`+`wipe_right` @[2.4, 30.0], proof steel s57 595.5 [595.5, 595.5, 595.6, 595.6, 597.65, 598.0], count 15 (window 31.0 kept - the dock is held to the wipe at the scene end; 7.0 would drop the count to 4 - parent accepts); held-dock-across-the-cut -> `dock_payload:chart` @0 + `exit:wipe`+`wipe_right` @[0, 21.9], proof steel s05 50.4 [50.4, 57.3] (the 9.50 dock is a `data` payload with no card), count 16; still-life-breather + `plate_option:world` @0 (tokyo s03 38.96, count 1); outro-clip-life + `plate_option:clip` @0 (japan s12 79.08 + tokyo s08 82.62, count 2); emphasized-bar-lit + `dock_option:badge` @0 (Japan s06 page badges; 35.26 [35.26, 35.26, 42.81], count 2). `effects_catalog_check: 0 failure(s), 3 example(s) skipped, 15 recipe(s) (15 proven, 6 decoration(s))`; `in sync (129 cards, 49 options, 15 recipes (15 proven), 291/327 cites resolved)`; drift + catalog + walk suites `83 passed`. The docs-manifest layer reports STALE from the memory file `resume-2026-09-12.md` (another lane's heading) - the parent regenerates the layers in T10.

### T4: Generator, drift gate, resolver, CLI and gallery read recipes
- Status: complete (machinery; the three proof drifts it correctly reports close with T8 + the T3 amendment) (started in parallel with T3 - parent deviation: the machinery develops on tmp fixtures and picks up the T3 files as they land; the parent runs the final `--write`/`--check` after both; T4 also owns a NEW shared module `content/video_engine/scripts/recipe_walk.py` (the walk + matcher) that T6 imports instead of re-implementing the walk)
- Owner: implementation_luna
- Depends on: T3
- Write set: `content/video_engine/scripts/build_effects_catalog.py`, `content/video_engine/scripts/effects_catalog_check.py`, `content/video_engine/scripts/authoring/effects.py`, `content/video_engine/scripts/effects_card.py`, `content/video_engine/scripts/build_effects_gallery.py`, `docs/EFFECTS-CATALOG.jsonl`, `docs/EFFECTS-CATALOG.md`, `content/video_engine/tests/test_build_effects_catalog.py`, `content/video_engine/tests/test_effects_catalog_drift.py`, `content/video_engine/tests/test_authoring_effects.py`, `content/video_engine/tests/test_build_effects_gallery.py`
- Acceptance: (a) the generator loads the recipes beside the cards, validates them against their schema, and writes them into `docs/EFFECTS-CATALOG.jsonl` as records with `axis: "recipe"`, `members` as ids with offsets and roles, `does`, `dials`, `status`, `proof`, `count`, and each member's `title` pulled from its card (never copied into the recipe file); `AXIS_ORDER` gains `recipe` LAST so the cards keep their order; `docs/EFFECTS-CATALOG.md` gains a "Recipes" section with the count table; two `--write` runs are byte-identical; `--check` exits 1 when stale. (b) the drift gate gains four checks, each proved by a broken copy in a tmp dir: a member that is not a card id / a listed option of its card / another recipe (and no cycle); a `proven` recipe with no proof, a proof whose `timeline` is absent on disk, or a proof whose members do NOT all fire within `window_s` at `proof.t` (the matcher, over the walk of that timeline); alias uniqueness across cards AND recipes plus the `AMBIGUOUS_NAMES` refusal; fewer than 2 members. (c) `authoring/effects.find`/`card` resolve a recipe (its `_tiers` keys tolerate a record with no `token` and no `lives`), so `find("badge ladder")` returns `[recipe:badge-ladder]` and an id tier still wins; `effects_card.py "<recipe>"` prints the members in order with offsets and roles, the dials, the act(s) and the proof instant in under 40 lines. (d) the gallery gains a Recipes section, one tile per recipe listing its members in order (with each member's proof frame where the card has one). (e) `docs_find.py "badge ladder"` returns the recipe first; **`docs_find.py "stack"` still returns the three axis-qualified cards before any recipe** (the layer's fair-share budget is unchanged and recipes must not crowd cards - the risk below). `docs_find.py` and `build_docs_layers.py` are NOT edited.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_build_effects_catalog.py content/video_engine/tests/test_effects_catalog_drift.py content/video_engine/tests/test_authoring_effects.py content/video_engine/tests/test_build_effects_gallery.py -q` then `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_docs_layers.py` then `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/effects_card.py "badge ladder"` (unpiped - never into `tail`)
- Evidence: 2026-09-13 luna: NEW `scripts/recipe_walk.py` (354 lines: `events`, `match`, `count`), `build_effects_catalog.py` 462->632 (`load_recipes`, `AXIS_ORDER` + `recipe` last, Recipes section), `effects_catalog_check.py` 459->649 (`check_recipe_members` incl. cycles + options, `check_recipe_proof` via the matcher, `check_recipe_aliases`, `check_recipe_count` with the count==1 INFO "decoration"), `authoring/effects.py` 95->107, `effects_card.py` 132->184, `build_effects_gallery.py` 258->342 (Recipes section); tests: `test_recipe_walk.py` NEW 223, catalog 246->390, drift 323->559, authoring 120->157, gallery 112->161 - every new check proved on a broken tmp copy (names in the lane return, e.g. `test_recipe_proof_names_the_member_that_does_not_fire_and_the_instant`). `--write` twice byte-identical (jsonl sha 2751b8e3..., md 1e349ee9...); `in sync (125 cards, 49 options, 15 recipes (15 proven), 284/317 cites resolved)`; the 125 card records byte-identical (cards-only render sha dce2710abb5cfb51 == the first 125 lines). Retrieval: `docs_find "badge ladder"` -> `recipe:badge-ladder` 1 hit; `"stack"` -> `overflow:stack`, `dock_option:stack`, `dock_payload:stack` first, no recipe in the answer; `"the card becomes the chart"` -> the recipe, 1 hit. Seeds: 12/15 proofs reproduce `members_at` within 0.05; R6=2, R7=4 pinned. Reported drifts (expected, outside T4): badge-ladder + plate-dock-wipe name `dock_kind:image` for badges; held-dock-across-the-cut + plate-dock-wipe claim `dock_payload:chart` at 9.5 where `ev-bravos-original-v1` is a `data` payload (real first fires [50.4, 57.3] / [595.6, 598.0, 619.2]); R1/R3/R5 counts not reproduced (T2 scoped them per DOCK, which the schema cannot express - the matcher counts ordered fires). Deviation kept: a ledger world event carries `page_builder:<variant>` (the axis is inventoried from `ledger_page.VARIANTS`; Japan is builder story / variant bars). Deviation: `docs/DOCS-INDEX.{jsonl,md}` regenerated (+1 record, stale before T4 from another lane's memory heading). 5 suites `1 failed, 107 passed` - the one red is the real-catalogue assert on the 3 drifts.

### T5: The authoring kit's presets, the beat plan and recipes in --propose
- Status: complete
- Owner: implementation_luna
- Depends on: T4
- Write set: `content/video_engine/scripts/authoring/recipes.py`, `content/video_engine/scripts/lint_species_choice.py` (the proposer block and its `--propose` output only), `content/video_engine/tests/test_authoring_recipes.py`, `content/video_engine/tests/test_lint_species_choice.py`
- Acceptance: `recipes.preset(name)` returns the ordered members with `offset_s`, `role` and option DEFAULTS as data, plus a `binds` list naming what the author must supply per member (the asset, the target, the label) - it reads only `docs/EFFECTS-CATALOG.jsonl`, names no episode, chooses nothing by count and writes no shot table (the header says so, in the proposer's words); `preset` on a `candidate` recipe returns it flagged `candidate` with the reason it has no proof; an unknown name raises naming the nearest titles. `--propose` prints, for a sentence with an act and no row, the RECIPES whose `acts` include that act (id, title, members with offsets, the proof instant, `candidate` marked) ABOVE the single-species drafts it prints today - the existing report stays byte-for-byte what it was (the P53 T8 rule: the proposal is appended), the proposer's documented limit is repeated verbatim (*"reads the WORLD UNDER a sentence, never the referent"*) with the recipe case added to it (a recipe whose members need a dock is proposed even where no dock is authored - the author binds or deletes), and `test_lint_species_choice.py::test_every_kind_and_verb_carries_a_when` still passes. A `BEAT-PLAN.jsonl` writer is NOT in this slice: the author writes the plan (the schema of a record is fixed in this plan's Execution Path and asserted by T6's M41 reader).
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_authoring_recipes.py content/video_engine/tests/test_lint_species_choice.py -q` then `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/lint_species_choice.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick --build build-short --propose`
- Evidence: 2026-09-13 luna: NEW `authoring/recipes.py` (142 lines: `load`, `preset`, `for_act`; the header in the proposer's words - candidates, no episode, nothing chosen by count, no shot table), `lint_species_choice.py` 609->680 (a `recipes for <ACT>` block above the single-species drafts; the limit repeated verbatim + the recipe case), NEW `test_authoring_recipes.py` (238 lines, 34 cases), `test_lint_species_choice.py` 251->314 (+6). `68 passed in 0.37s`. Byte pin measured against the output captured BEFORE the edit: `report prefix byte-identical: True`, `propose(recipes=False) == todays propose block: True`. `preset("the badge ladder")` -> members in order with offsets, dials `{BADGE_GAP_S 1.3, FIRST_BADGE_S 2.05}`, `binds` one need per member (the table: dock_kind -> asset; dock_payload -> asset+data; dock_option -> asset (+target for read/embed/behind); page_builder/chart_dock -> data + builder args; species -> target (+label for callout/figure/stamp/chip); plate_option -> asset; exit/enter -> nothing; an absent card -> one need naming it). Mutation checks bit (shallow copy, id-only sort, lost comment mark). OWED to the parent (T10): `tests/test_authoring_kit.py:277` pins the kit inventory and needs `"recipes.py"` added beside `__init__.py`'s import (the P55 T8 precedent).

### T6: The one-shot floor gate and its calibration fixture
- Status: complete (HG1 answered 2026-09-13: A, 60% kept)
- Owner: implementation_luna
- Depends on: T4
- Write set: `content/video_engine/scripts/gate_one_shot_floor.py`, `content/video_engine/scripts/build_gates_registry.py` (one `FAMILY` entry + `FAMILIES`), `docs/GATES-REGISTRY.jsonl`, `docs/GATES-REGISTRY.md` (regenerated by `--write`), `content/video_engine/tests/test_gate_one_shot_floor.py`
- Acceptance: the script reads a BUILD dir (the compiled `*.timeline.json`, its `narration.words_path` for the beats via `lint_species_choice.load_sentences`, `docs/EFFECTS-CATALOG.jsonl` for the recipes, and the reference cut's own timeline) and prints rows **M35-M42** exactly as the table in Execution Path defines them, plus a `RESULT:` line; the walk and the 6 s co-occurrence matcher are implemented HERE (stdlib, pure functions, no import of the spike) and unit-tested on synthetic timelines; HG1's answer is implemented as written - under (A) `PREDATES_E96` is a 4-entry tuple, the test asserts its contents, and the two never-shipped rows print `INFO ... predates E96` with the measured number on those builds only; the reference's numbers are MEASURED at run time from Japan's timeline (never hard-coded) and Bravos' are quoted with their source; events/min can never emit FAIL (asserted by a test); the fixture asserts, on the real builds: Japan `2` forms, `0` chart-to-chart, `0.36` docks-per-beat, `1.00` narrative:chart, `28.1` events/min, and the two `predates E96` rows; the thin one-shot `1 / 0 / 0.00 / 0.20` and a FAIL verdict; Steel `5` forms and `0.80`; a build with no `BEAT-PLAN.jsonl` WARNs on M41 and never dies. `build_gates_registry.py --check` passes with the new family (the generated scope note reads 6 checkers).
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_gate_one_shot_floor.py content/video_engine/tests/test_build_gates_registry.py -q` then `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short` and the same on `.../normal-for-which-bridge/review-v1` (unpiped)
- Evidence: 2026-09-13 luna: NEW `gate_one_shot_floor.py` (589 lines; imports `recipe_walk`; `PREDATES_E96` 4-tuple asserted by a test; the reference measured at run time from Japan's timeline; Bravos quoted from `bravos-reference.md`), NEW `test_gate_one_shot_floor.py` (378 lines, 30 tests), `build_gates_registry.py` +2 (family `floor`), `docs/GATES-REGISTRY.{jsonl,md}` regenerated (`in sync (160 records, 146 ids, 197/197 cites resolved)`, scope note "6 script-side checkers"). `53 passed in 8.04s`. The four calibration outputs (saved whole in the session scratchpad `p56/out-<cut>.txt`): **Japan** `[INFO] M35 2 chart forms ... predates E96 (measured 2)`, `[INFO] M36 0 ... predates E96`, `[PASS] M37 docks on 0.36 of 25 beats (9 on screen, 7 entering) - the floor is 0.36 = max(1/3, the reference's own)`, `[PASS] M38 coverage 0.76 ... the floor is 0.60; the reference measures 0.76`, `[PASS] M39 1.00 (5 plates + 2 clips / 5 pages + 2 chart docks)`, `[JUDGE] M40` + 8-row table, `[WARN] M41 no beat plan on disk`, `[INFO] M42 28.1 events/min (40 = 12 + 28)`, `RESULT: 0 FAIL / 1 WARN / 3 PASS / 1 JUDGE / 3 INFO`, exit 0. **Tokyo v2** M37 0.28 FAIL, M38 0.56 FAIL, M39 1.00, M42 18.2, exit 1. **Steel** M35 5 forms INFO (bars 7, checklist 4, panels 1, series 12, shares 4), M37 0.80 PASS, M38 0.45 FAIL, M39 2.34, M42 14.8, exit 1. **The thin one-shot** M35 1 INFO, M36 0 INFO, M37 0.00 of 19 FAIL, M38 0.00 FAIL (no proven recipe fires), M39 0.20 FAIL, M42 17.9, `RESULT: 3 FAIL`, exit 1. Every number equals T2's `measures.md`. FOR HG2 (parent finding): under the matcher's reading (a beat carries a recipe when a FIRE overlaps it) Japan measures **0.76**, not the plan's hand estimate of <= 0.44 - the long-window recipes (a dock held to a wipe, 31 s; the held page hosting docks, 35 s) credit every beat they span; the row still separates the cuts (0.76 / 0.56 / 0.45 / 0.00) and the thin cut stays at zero; the operator reads this at HG2 (keep the reading, or credit only the beat the fire STARTS in). Deviations: Steel's M38 moved 0.35 -> 0.45 during the slice as the catalogue was regenerated under the lane, so the fixture pins M38's shape (floor 0.60 + the reference's measured coverage) and matches RESULT counts by regex; `docs/GATES-REGISTRY.*` also absorbed another lane's uncommitted `gate_motion_density.py` line shifts (whole-file `--write`); `lint_species_choice.resolve_inputs` is unusable on a long form (demands `SHOT-TABLE-SHORT.py`) and the compiled `narration.words_path` is stale on 2 of 4 cuts (tokyo v2 points at `build-short/`), so the gate's `beats_path()` reads the build's own `timeline.json` first (docstring) - reported, not patched into T5's file; M41 matches a plan record by `t0` first, then a 1-based `beat`.

### T7: The bar carries the floor, and the recipe audit sheet
- Status: complete
- Owner: implementation_luna
- Depends on: T6
- Write set: `content/video_engine/scripts/self_watch.py`, `content/video_engine/tests/test_self_watch.py`, `docs/content-video-engine/SELF-WATCH.md`
- Acceptance: `section1` gains a row per floor id (M35-M42) from a `run_floor(build)` that mirrors `run_gate`/`parse_gate` (one subprocess, rows parsed, nothing re-computed), so a FAIL makes `verdict()` say `NOT CLEAN - the one-shot floor (M3x): ...` and the cut is never offered for a watch; the M40 parity table and the M42 rates ride as JUDGE / INFO rows and never end the report; the **recipe audit sheet** is written per beat that carries a recipe - `<build>/self-watch/recipes/<beat>-<recipe>.png`, the build's frames at the recipe's member instants beside the PROOF cut's frames at its own `members_at` instants (both through `probe.Probe` + `probe.contact_sheet`, the proof build served read-only and never rebuilt - `review-link-frozen-copy`), listed in SELF-WATCH as an INFO row naming the sheets, with `O11` added to the O-rows for the agent's read of them ("the recipe fired as its proof does: the members in order, at their offsets - name the beat where it did not"); a build whose proof cut is not on disk WARNs and names it; `SELF-WATCH.md` (the doctrine page) documents the new rows and the sheet.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_self_watch.py content/video_engine/tests/test_gate_one_shot_floor.py -q`
- Evidence: 2026-09-13 luna: `self_watch.py` 516->764 (`run_floor` one subprocess parsed by `ROW_RE`, M40 table lines ignored; `section1` gains one row per floor id `the one-shot floor (M3x)`; `verdict` says `NOT CLEAN - the one-shot floor (M3x): ...` on a floor FAIL; `write_recipe_sheets` via `probe.Probe` + `contact_sheet`, the proof build read-only; `O11` + its PLAIN question), `test_self_watch.py` 268->482 (+8: a stubbed floor gate, a fake Probe), NEW `docs/content-video-engine/SELF-WATCH.md` (121 lines - the page did not exist before). `2 failed, 52 passed` - the two reds are the baseline's (`test_the_tokyo_report_is_written_with_the_sheets`, `test_a_failing_script_gate_makes_it_not_clean`); the first now trips one assert earlier because it found the publish row by INDEX 6 - the parent changed that assert to find the row by name (the test stays red on its pre-existing reason). Real run on `japan-tariff-trick/build-short` (exit 1 on the motion gate's own M25/M27 - pre-existing): section 1 carries `INFO M35 2 chart forms ... predates E96`, `INFO M36`, `PASS M37 0.36 of 25`, `PASS M38 0.76 of 25 (19 carry a recipe)`, `PASS M39 1.00`, `JUDGE M40`, `WARN M41 no beat plan`, `INFO M42 28.1 events/min`, `INFO the recipe audit sheets (O11): 11 sheet(s) over 9 beat(s)`; every floor number equals T6's. Sheets under `build-short/self-watch/recipes/` (beat01-card-becomes-the-chart ... beat25-outro-clip-life, 0 misses); the parent read `beat03-trace-callout-ladder.png` as a frame. The bar's normal run added only untracked report files to the approved build (`SELF-WATCH.{md,html}`, `layout-probe.json`, `publish/`, `candidates/`, `docks/`, `self-watch/`) - no tracked file changed, nothing rebuilt. For HG2: the cross-build path was exercised on a temp copy of Tokyo v2 against Japan's proof (0 warns); on clip worlds a member instant can land on a black frame (the sheet is right, the read is thin).

### T8: R26-108's real gaps
- Status: complete (extended by the parent to FOUR cards: `plate_option:ken`, `plate_option:world`, `plate_option:clip`, `dock_option:badge` - the badge, the plate world and the clip world were uncarded and the recipes could not name them)
- Owner: junior_developer
- Depends on: T4
- Write set: `content/video_engine/effects/cards/plate_option.json` (one card added), `docs/EFFECTS-CATALOG.jsonl`, `docs/EFFECTS-CATALOG.md` (regenerated), `content/video_engine/tests/test_effects_catalog_drift.py` (two cases added)
- Acceptance: (a) the Ken Burns gap is closed by ONE card - `plate_option:ken`, `implicit: true` (the schema's existing mechanism for an effect with no token of its own), title "The Ken Burns push and drift", `does` naming both halves of the pair as the timeline carries them (`world.ken_burns {scale, x, y}`: the push is `scale`, the drift is `x`/`y`, authored as the shot row's 4th element `ken_burns(scale, x, y)`), aliases "Ken Burns", "the slow push", `lives` on the engine's Ken Burns application, `proof.first_use` steel-and-paper/build-f (75 of 75 scenes; `(scale,x,y)` present on every one), `status: live`, and the drift gate accepting it as implicit (its token is not in `PLATE_OPTS`); a test asserts the card exists and that `docs_find.py "Ken Burns"` now answers with it first. (b) `exit:wipe_right` needs NO new card - the token is already an `option` of `exit:wipe` (verified 2026-09-13) - so the gap was the MATCHER: a test asserts a recipe member `{card: "exit:wipe", option: "wipe_right"}` is accepted by the gate and that Steel's 32 `wipe_right` exits count as fires of it. (c) the long-form verdict is recorded as a test, not a hope: Steel's timeline carries `species: []` on all 75 scenes and 0 ledger pages, so **no seed whose members include a species or a page can be `proven` on the long form today**; the test asserts that every `proven` recipe whose proof is `steel-and-paper` uses only dock/world/exit/badge members (R1, R2, R3, R4, R5 - the five Steel seeds), and that a recipe naming a species with a Steel proof FAILS. The finding for R26-108's "stop speaking disjoint vocabularies" half is REPORTED to the parent for a BACKLOG row; this slice does not touch the compiler.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_effects_catalog_drift.py content/video_engine/tests/test_build_effects_catalog.py -q` then `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/docs_find.py "Ken Burns"`
- Evidence: 2026-09-13 junior: `cards/plate_option.json` 6->9, `cards/dock_option.json` 7->8 (all four `implicit: true`, `status: live`, `author.check: none` - `_ex_plate`/`_ex_dock` need a real option key; `lives.symbol` `ken_burns`+`KB_MAX` / `asset_id` / `paintClip` / `badge_at`+`LP_BADGE_IN`,`LP_BADGE_STEP`,`LP_BADGE_COL`; first_use steel build-f t 0.0 / 0.0 / japan s12 79.08 / steel 11.55; aliases each with a `path:line`, "the badge ladder" asserted NOT an alias). Catalogue regenerated once: `in sync (129 cards, 49 options, 15 recipes (15 proven), 291/327 cites resolved)`. `test_effects_catalog_drift.py` 559->729 (+13 cases): (b) a member `{exit:wipe, option: wipe_right}` accepted, Steel walks to 32 `exit:wipe`+`wipe_right` events and 81 dock badges (first 11.55 = 9.50 + 2.05, then +1.30) + 2 page badges (Japan s06/s08); (c) 75 of 75 Steel scenes `species: []`, 0 ledger pages, 75/75 bare plates, 43 docks (41 badged); the five Steel-proven recipes use only {dock_kind, dock_payload, chart_dock, exit} - pinned as a SUBSET of `STEEL_SPEAKABLE_AXES` (equality would break on the T3b re-membering); a tmp recipe naming a species with a Steel proof fails `check_recipe_proof`. pytest `1 failed, 68 passed` - the one red is the real-catalogue assert on the 3 recipe-proof drifts T3b is closing. `docs_find "Ken Burns"` answers `plate_option:ken` first (13 hits). Deviations accepted: `serves` omitted (0 of 129 cards carry it); no count pin existed for 125 cards. FINDING for the BACKLOG (T10): the long form speaks no species vocabulary - the compiler plan that closes R26-108's open half.

### T9: The candidate recipes - the 67 unused cards in their slots
- Status: complete
- Owner: implementation_luna
- Depends on: T8
- Write set: `content/video_engine/effects/recipes/*.json` (new candidate files only - no file written by T3 is edited), `docs/EFFECTS-CATALOG.jsonl`, `docs/EFFECTS-CATALOG.md` (regenerated)
- Acceptance: every one of the 67 `wired` cards in `recipes_r1.md` s4 appears as a member of at least one recipe - either added to a `candidate` variant of the seed it slots into (never to the `proven` file: a proven recipe's members are what actually fired) or in a new `candidate` recipe - with `status: candidate`, no `proof`, the s4 slot line as its `role`, and `source` naming `recipes_r1 s4`; the nine `kinetics:*` cards are named only as the `dials`/mechanism of the effect above them (s4's own note: "the viewer sees it only through the effects that call it") and never as a standalone member; the five `chart_to:*` verbs each appear in a candidate that would satisfy M36 (so an author looking for "a chart-to-chart transform" finds a combination, not a bare verb); a test asserts the coverage claim by counting cards with `status: wired` that appear in no recipe (expected 0, the nine kinetics excluded with their reason).
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pytest content/video_engine/tests/test_build_effects_catalog.py content/video_engine/tests/test_effects_catalog_drift.py -q` then `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_effects_catalog.py --check`
- Evidence: 2026-09-13 luna: 24 NEW candidate files (22 new recipes + 2 variants `badge-ladder-embedded`, `outro-clip-life-still`), each `status: candidate`, no proof, `count: 0`, `source: recipes_r1 s4 (R<n> slot)`; every one of the 59 non-kinetics `wired` cards is a member of >= 1 recipe (s4's 67 = 59 + `exit:wipe` already in plate-dock-wipe + 7 kinetics rows); the layer holds 12 wired `kinetics:*` cards (s4 said nine), each named only in a member's `role` and a member of nothing; the five `chart_to` verbs each sit behind a ledger page + `page_species:chart_to` in a candidate that would satisfy M36 (`chart-extends-at-the-pen`, `chart-recast-into-the-other-form`, `chart-rescales-under-the-held-light`, `chart-parks-for-their-claim`, `chart-morphs-between-two-lines`). `in sync (129 cards, 49 options, 39 recipes (15 proven), 339/375 cites resolved)`; `effects_catalog_check: 0 failure(s), 3 example(s) skipped, 39 recipe(s) (15 proven, 6 decoration(s))`; `71 passed`; collision check `no collisions` / `unique across recipes`; `docs_find "stack"` still answers the three cards first. The coverage test `test_every_wired_card_is_in_a_recipe` reads the generated layer. Deviation: `test_every_recipe_file_validates_and_lands_in_the_catalogue` compared sorted file names against sorted ids (a `-variant` file sorts before its parent while its id sorts after) - changed to set equality. The docs-manifest layer stays STALE from the memory file + no manifest row for `docs/EFFECTS-CATALOG.md` - the parent's T10 regeneration.

### T10: Doctrine, routing and the kit's integration point
- Status: complete
- Owner: parent
- Depends on: T7, T9
- Write set: `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (one pointer), `docs/content-video-engine/BACKLOG.md`, `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (one pointer in s5), `content/video_engine/scripts/authoring/__init__.py` (one line), `CLAUDE.md`, `GEMINI.md`, `docs/AGENTS-VIDEO-ENGINE.md`, `docs/agent-context/SKILL_ROUTER.md`
- Acceptance: CAPABILITIES gains rows for RECIPES (what, where, state, proof, Use when) and for the one-shot floor, each naming the generated artifacts; doc 29 gains ONE pointer line (the recipes are generated - no prose copy); SPECIES-BY-SENTENCE s5 points at the recipes per act; BACKLOG R26-103 / R26-104 / R26-108 marked with what landed and what did not (the long-form vocabulary half of R26-108 stays open with T8's finding quoted, and carries a `trigger:`); the entry files and the router gain exactly one line each - "author a beat as a recipe: `python content/video_engine/scripts/effects_card.py \"<recipe>\"` (the catalogue: `docs/EFFECTS-CATALOG.md`; the floor: `gate_one_shot_floor.py`)"; `authoring/__init__.py` gains `recipes` to its imports and `__all__` (the parent's one-line integration edit, as in P55 T8); AGENTS.md unchanged; `build_docs_layers.py` in sync.
- Validate: `C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe content/video_engine/scripts/build_docs_layers.py` then `git diff --stat -- CLAUDE.md GEMINI.md AGENTS.md docs/AGENTS-VIDEO-ENGINE.md docs/agent-context/SKILL_ROUTER.md content/video_engine/scripts/authoring/__init__.py`
- Evidence: 2026-09-13 parent (`scratchpad/p56/t10_doctrine.py`): CAPABILITIES gained ONE section "The effects catalogue, the recipes and the one-shot floor (P55 / P56)" with three rows (the catalogue - P55 had no row of its own -, the recipe cards, the one-shot floor v2: what / where / state / proof / Use when, every artifact named as generated); doc 29 s9.24 gained one pointer paragraph (the stack's shipped use is `recipe:verdict-recap`; the recipes are generated, never copied); SPECIES-BY-SENTENCE s5 one pointer (recipes per act via `--propose` and `authoring.recipes.for_act`); BACKLOG R26-103 LANDED, R26-104 LANDED with HG2 open (the coverage reading named), R26-108 PART LANDED with the open half quoted from T8's measurement and a `trigger:` (the next long-form build, or the compiler emitting a `species` array for the long form); the grill ledger's Steel events/min corrected 16.8 -> 14.8 with the reason; exactly one routing line each in `CLAUDE.md`, `GEMINI.md`, `docs/AGENTS-VIDEO-ENGINE.md`, `docs/agent-context/SKILL_ROUTER.md` ("author a beat as a RECIPE ... `effects_card.py \"<recipe>\"` ... `gate_one_shot_floor.py <build>`"); `authoring/__init__.py` imports `recipes` and lists it in `__all__` (+ the docstring's import line) and `test_authoring_kit.py`'s inventory pin gained `recipes.py`; AGENTS.md unchanged (`git diff --stat` shows CLAUDE.md +2, GEMINI.md +2, AGENTS-VIDEO-ENGINE.md +2, SKILL_ROUTER.md +2, `__init__.py` +5/-1, AGENTS.md absent). `build_docs_layers.py`: every layer in sync (9 layers).

## Verification

Every command from the main checkout, `python` =
`C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`, and **no gated step is ever piped into
`tail`** (`never-pipe-gated-steps-to-tail`).

- Catalogue in sync: `python content/video_engine/scripts/build_effects_catalog.py --check` and
  `python content/video_engine/scripts/build_docs_layers.py` (every layer, including the effects layer with recipes in it).
- Drift: `python -m pytest content/video_engine/tests/test_effects_catalog_drift.py content/video_engine/tests/test_build_effects_catalog.py -q`.
- Retrieval: `python content/video_engine/scripts/docs_find.py "badge ladder"` (the recipe first),
  `"the card becomes the chart"`, `"Ken Burns"` (the new card first), `"stack"` (the three CARDS still first),
  `python content/video_engine/scripts/effects_card.py "the nine-proof recap"`.
- The kit: `python -c "import sys; sys.path.insert(0,'content/video_engine/scripts'); from authoring import recipes as RX; print([m['card'] for m in RX.preset('the badge ladder')['members']])"`.
- The floor, measured on the calibration set (the reference first - `thresholds-from-the-reference`):
  `python content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`,
  then `.../tokyo-tea-break/build-short.v2`, `.../steel-and-paper/build-f`, `.../normal-for-which-bridge/review-v1`
  (the thin cut must FAIL; the approved cuts must read as HG1 ruled).
- The bar: `python content/video_engine/scripts/self_watch.py <a build> --project <project>` on one real build; the
  report carries M35-M42 and the recipe sheets, and the verdict line matches the floor rows.
- **Nothing moved in the engine:** `python content/video_engine/scripts/sync_kinetics.py --check` (unchanged) and
  `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q`
  (every golden frame byte-identical), plus `git diff --stat -- docs/content-video-engine/samples/scene-evidence-engine.mjs content/video_engine/scripts/build_scene_timeline_f.py content/video_engine/scripts/kinetics content/video_engine/scripts/species content/video_engine/tests/golden` returning nothing.
- **The whole tree at the end** (the P55 lesson - three test pins went red because only the slice's suites ran):
  `python -m pytest content/video_engine/tests -q` and `node --test content/video_engine/tests/kinetics/`; the reds
  must be the same set as before the plan (the P30 lane's 9, per the readiness review s7) and no more.
- Plan: `python scripts/prp_validate.py .claude/PRPs/plans/P56-EFFECT-RECIPES-AND-THE-ONE-SHOT-FLOOR.plan.md`.

## Risks

- **Recipe detection on the long form.** Steel's compiled timeline has `species: []` on all 75 scenes and no ledger
  pages, so a species- or page-based recipe can never be `proven` there and M38 on a long form measures only the
  dock/world/exit/badge vocabulary. T8 turns this into a test instead of a surprise; the fix (the long form speaking
  the species vocabulary) is R26-108's open half and belongs to a compiler plan.
- **A false `proven` on a coincidental co-occurrence.** Two effects landing inside 6 s is not a grammar. Mitigations:
  `count` is carried on every recipe and printed in M38's row (the spike's own line - *"a recipe that fires once is a
  decoration; a recipe that fires four times is a grammar"*), the matcher requires the ORDER and the offsets, and the
  audit sheet puts the frames beside the proof's frames so a human sees whether it read as one effect. Residual: a
  2-member recipe with `count: 1` is barely evidence; the parent may raise the bar to `count >= 2` at HG2.
- **The proposer's referent limit is inherited, not fixed.** `--propose` reads the world under a sentence, never the
  referent, so it will propose a dock-bearing recipe onto a beat with no dock. T5 keeps the limit verbatim and adds the
  recipe case to it; anything more is an allocator, which the pipeline forbids.
- **Gaming the floors.** A cut can add a dock per beat and three chart forms with no story and pass M35-M39. The
  defence is unchanged by design: M40 is a JUDGE row against the best approved short, the O-rows (now with O11) are an
  agent's read of the frames, and the operator's watch is the gate. E96 says the floors come BEFORE the watch, not
  instead of it. A floor is a floor, never a target.
- **The catalogue's retrieval budget.** The effects layer is scanned first and takes a fair share of the hit budget
  (`ceil(remaining / layers left)`); 15 + candidate recipes landing in the same file can push cards out of a 20-hit
  answer. T4's acceptance pins the case that matters (`"stack"` still answers with the three cards first) and no
  recipe may take a card's alias; if crowding shows up anyway the cheapest fix is ranking (an exact-token card before
  a substring recipe), not a new layer.
- **The proof cuts must stay on disk and frozen.** The audit sheet reads approved builds (`japan-tariff-trick/build-short`
  et al). A served proof build is never rebuilt under the operator (`review-link-frozen-copy`); T7 serves it read-only
  and WARNs when it is absent rather than re-compiling anything.
- **Two slices regenerate the same artifacts.** T4, T8 and T9 all write `docs/EFFECTS-CATALOG.{jsonl,md}`; they are
  serialised (T4 -> T8 -> T9) and each ends with `--write` then `--check`. The parent never runs them in parallel.

## Evidence And Handoff

- Reviewer pass (fresh, read-only, 2026-09-13; 92 passed on the three P56 suites, drift gate 0 failures; Not Building s7 verified by diff content - P56 touched no engine file). Findings and dispositions: (1) HIGH a proven recipe's `count` was authored, never verified (outro-clip-life said 2, walks 1; spotlight-held-past-the-cut 4 / 2; test-card-rows 4 / 5) -> FIX: `check_recipe_count` re-walks the proof and refuses a mismatch; the files carry the matcher's number. (2) HIGH `match` enforced INDEX order not TIME order (a constructed pair of overlapping spans fired `[0.0, 10.0, 9.0]`; Steel has 20 docks whose exit outlives their scene) -> FIX: each member's instant >= the previous one's. (3) MED M38 credits every beat a fire spans (Japan 0.76) -> KEPT as ruled for HG2, the by-start-beat reading printed beside it in the same row. (4) MED `PREDATES_E96` matched on path segments only -> FIX: each entry pinned to its timeline's sha256. (5) MED schema `members_at` refused `null` for an absent optional -> FIX: nullable. (6) MED a `recipe:` member was declared but never matchable -> FIX: `match`/`count` expand nested recipes (acyclic). (7) LOW KeyErrors on a partial timeline; an unreadable reference killed the gate -> FIX: `.get` defaults, WARN rows. (8) LOW the first member's offset 0.0 never enforced -> FIX: gate check. (9) LOW missing tests (range offsets, tolerance edges, time order, count-vs-walk, nesting, malformed timeline), dead `seen` dedupe -> FIX with tests. (10) T10 status open -> closed below. Fix lane: luna, 2026-09-13; its evidence follows.
- Fix lane landed (luna, 2026-09-13): (1) `check_recipe_count` re-walks the proof through a shared walker cache and refuses a count the matcher does not reproduce - the files now carry the matcher's numbers (outro-clip-life 2->1, spotlight-held-past-the-cut 4->2, test-card-rows 4->5; 7 decorations); (2) `candidates(..., t_prev)`/`_chain` require time order (all 15 proofs still fire, no `members_at` changed); (3) M38 prints `coverage 0.76 spanning / 0.16 by the beat a fire starts in` (Japan; Tokyo 0.56 / 0.08, Steel 0.45 / 0.08, thin 0.00 / 0.00) - the floor stays on the spanning number pending HG2; (4) `PREDATES_E96` = `{(project, build): sha256 of the compiled timeline}`, a re-authored timeline in the same dir stops predating (test); (5) `members_at` items nullable; (6) `recipe_walk.flatten` expands a `recipe:` member (offsets shifted, ranges on both ends), `match`/`count` take `recipes=`, both gates pass the registry; (7) `.get` + schema defaults in the walk, an unreadable reference turns M37/M38/M39 into WARN `reference <path> not readable - floor held at the rule's own number`; (8) the first member's offset must open at 0; (9) the dead `seen` dedupe removed (0 duplicate chains over 4 cuts x 15 recipes). Five suites `2 failed, 151 passed` (the two pre-existing `test_self_watch` reds); `effects_catalog_check: 0 failure(s), 3 example(s) skipped, 39 recipe(s) (15 proven, 7 decoration(s))`; catalogue + gates registry in sync; the four calibration verdicts unchanged (Japan 0 FAIL; Tokyo 2; Steel 1; the thin cut 3). Style note: `test_effects_catalog_drift.py` is 808 lines (8 over the cap) - left. Memories exported (`sync_operator_memory.py --export`: 1 written, 74 unchanged); `build_docs_layers.py --write` then check: `every layer in sync (9 layers)` (docs-manifest 410 documents, 79,070 bytes - under the 80 KB cap).
- Whole tree, run 1 (after T1-T10, before the reviewer fixes; 15:22): `64 failed, 2874 passed, 5 skipped, 2 errors` vs the baseline before the plan `63 failed, 2737 passed, 5 skipped, 2 errors` (the two errors are the known `src.config` collection collision). Set difference: 2 NEW reds, both stale pins from the T3b re-membering (`test_authoring_effects::test_a_recipes_printed_card_lists_its_members_in_order_with_the_proof` expected `dock_kind:image` at +2.05 - now `dock_option:badge`; `test_authoring_recipes::test_every_member_of_the_badge_ladder_carries_a_need` expected every member to need `asset` - a badge member needs its `label`) -> fixed by the parent: the pins updated and `authoring/recipes.py` gained `NEEDS_BY_CARD` for the four implicit cards (badge -> label, world/clip -> asset, ken -> nothing), applied only when `author.check == "none"`; the four authoring suites `125 passed`. 1 baseline red FIXED by the plan (`test_build_docs_layers::test_the_committed_tree_passes_check` - the layers are in sync again). The whole tree runs a second time after the reviewer's fix lane.
- Whole tree, run 2 (after the reviewer's fix lane; 16:16): `62 failed, 2890 passed, 5 skipped, 2 errors`. Against the baseline before the plan (`63 failed, 2737 passed`): NO new red; one baseline red fixed (`test_build_docs_layers::test_the_committed_tree_passes_check`); the 62 remaining reds are the pre-existing set (the P30 console lane, the finance-whiteboard proofs, the two `test_self_watch` reds, audio_synth, bridge, etc. - ids saved in the session scratchpad `p56/verify/final2_failed_ids.txt` beside `baseline_pytest_failed_ids.txt`). COMPLETE 2026-09-13 night: every acceptance item 1-9 proven above; HG2 (the operator's first read of a cut under the floor, incl. the coverage reading and the count>=2 bar) stays open on BACKLOG R26-104; the commit batch (R26-83, now including P56) is the operator's word; nothing pushed.
- Final verification (parent, 2026-09-13, every command unpiped, outputs under the session scratchpad `p56/verify/`): `build_docs_layers.py --write` then check -> `every layer in sync (9 layers)` (docs-index 4103 records / 337 files; effects-catalog `129 cards, 49 options, 39 recipes (15 proven), 339/375 cites resolved`; gates-registry `160 records, 146 ids, 197/197 cites`); `effects_catalog_check: 0 failure(s), 3 example(s) skipped, 39 recipe(s) (15 proven, 6 decoration(s))`; `sync_kinetics: in sync (31 module(s): 14 kinetics, 17 species)`; node kinetics `tests 348 / pass 348 / fail 0` (31 files named); NOTHING MOVED IN THE ENGINE, proved by mtime: of 181 engine/compiler/kinetics/species/golden files, 0 were modified after this plan's first write (the T1 schema, 19:37:36) except the golden test's own scratch output `tests/golden/diffs/dock-pair-16x9.perturbed.diff.png` (written by the baseline pytest run at 19:50) - the `git diff --stat` on those paths shows only the pre-P56 uncommitted batch (the melt rework, E95, R26-93, the P55 modules), recorded before this plan; the whole pytest tree and the reviewer's pass are recorded below when they land.
- APPROVED 2026-09-13 (the operator: "A sounds righ for approval"; HG1 answered); copied from the sweet-villani worktree to main by the parent. Implementation starts on `/prp-implement P56`.

- Drafted 2026-09-13 by `architect_sol` from the MAIN checkout (read-only; head `43a26e9` in the worktree, main's own
  head is the uncommitted R26-83 batch). Written into the sweet-villani worktree's `.claude/PRPs/plans/` because the
  harness refuses writes to the main checkout's `.claude/`; the parent copies it to main on approval.
- Deviation: the brief's `npm run prp:validate` has no `package.json` in either checkout; validated with
  `python scripts/prp_validate.py` (the runbook's PRP Format command).
- Measured by the parent during drafting (reproducible with the commands in T2's Validate; these are the HG1 numbers):
  Japan 25 beats / 2 chart forms / 0 chart-to-chart / 9 beats with a dock on screen (0.36; 8 = 0.32 on the
  enters-during-the-beat reading) / narrative:chart 1.00; Tokyo 25 / 2 / 0 / 7 (0.28) / 1.00; Steel 240 / 5 (its 32
  chart docks; 0 ledger pages, `species: []` on all 75 scenes) / 0 / 192 (0.80) / 2.34; the thin one-shot 19 / 1 / 0 /
  0 (0.00) / 0.20.
- Contention at draft time: main carries the uncommitted R26-83 batch including all of P55's implementation. Every
  slice here writes NEW files or P55 files that landed in that batch - so this plan's first action after approval is
  the parent's: get R26-83 committed (the grill's own prerequisite: *"Prerequisite for all engine work: the commit
  batch (R26-83) so lanes work from a commit"*) before T3 onward run.
- Slice evidence (the seed re-derivation, generator runs, each drift-gate failure proved, the floor gate's output on
  all four calibration builds, the SELF-WATCH report path and the audit sheets) is recorded under each slice's Evidence
  line as it lands. A subagent's summary is not evidence: the artifact path, the command and its verbatim tail are.
