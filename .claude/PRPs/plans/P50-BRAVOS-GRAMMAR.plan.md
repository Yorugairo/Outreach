---
id: P50-BRAVOS-GRAMMAR
title: The Bravos grammar - four species we lack, and a species-by-sentence map so an agent knows when to use what we have
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-10
updated: 2026-09-10
---

# The Bravos grammar

## Summary

The operator, 2026-09-10, on Bravos Research's *China Just Triggered A New World Order*: *"the cleanest finance
YouTube production I ever saw"* - then `/prp-plan all of it and how best to allow llm agents to know when to use the
capabilities. Also analyze our current capability backlog to determine which of those items blend in best with what
you see from bravos.`

**Recall** (the receipt, `docs/runbooks/RECALL-RECEIPT.md`):
- `content/video_engine/sources/reference_analyses/bravos-china-just-triggered-a-new-world-order/REPORT.claude.md` - the
  measured read: 120 visual events (6.0/min) of which 50 compositions (2.5/min); 3,542 words at 177.7 WPM; the grammar
  in twelve lines. `docs/content-video-engine/46-REFERENCE-RHYTHM.md` §46.7 - events are not cuts.
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md:1706` §9.27 the MOTION MENU (the targeting law; what is
  shipped: plate life, punch/focus zoom/pull-back, callout, spotlight, squiggle; NOT built: beat-freeze exit, radial
  reveal, push hand-off, weight-shift captions, focus rack) and `:1775` §9.28 the SURFACE GRAMMAR (A1-A3 earn the
  page, B1-B4 keep the dock, C1-C6 choreography, D1-D4 density, the census form).
- `docs/content-video-engine/39-EVIDENCE-CHART-SYSTEM.md:225` §10 the record document (typewriter + highlighter) -
  the nearest sibling of a press card. `docs/content-video-engine/CAPABILITIES.md:54-55` (surface grammar, motion menu).
- `content/video_engine/scripts/build_scene_timeline_f.py:110-157` - `SPECIES_KINDS`, `SPECIES_TARGETS`, `PAGE_SPECIES`:
  the species registry is CODE; nothing in it says *when* a species is the right one.
- `docs/content-video-engine/PIPELINE.md:28` stage 7 - the shot table is authored by "a human or model reading the
  narration"; the episode-build skill says "reach for a different species before another plate" (B6) and no more.
- `docs_find` 0 hits for: flow diagram, press card, treemap, species selection, icon chip, world map. `vector map`
  hits only the Bravos report. **The four species are gaps in the record, not just in the code.**
- `docs/portable/OPERATOR-RULINGS.md` E53 (chart form is law; §7 the donut is the one part-to-whole exception), E56 (a
  ring circles a number or a point on a chart; a picture's focus is a light; every addition passes the life check),
  E50 (a chart's deployed life), E25 (a chart proves one sentence and leaves), E21 (never still).
- `docs/content-video-engine/BACKLOG.md:420-457` the registry read and the R26 rows; `:284` A2a the icon ring (sourced).

**What Bravos does that we cannot**, read from the frames (the report's §"The grammar"): (1) a **vector map** as a
live stage - countries light as named, dashed arcs with X's for blocked flows, year stamps, a figure stamp on a
country; (2) a **flow diagram** of icon chips in a dashed box joined by arrows, REUSED with one node swapped - the
rhyme as a picture; (3) the **press card** as the proof species - a real screenshot cropped to its headline, the key
phrase underlined in the accent, cards stacking with the newest lit and the rest dimmed; (4) a **treemap** with X marks
for a part-to-whole. Under all four: an **icon chip** system (a dark rounded square, one glyph, one label) that we do
not have either.

**What Bravos does that we already hold** and only need to say WHEN: terminal tags (E53), the ring on a datum (E56;
theirs is a dashed ellipse), ranked bars that race and stamp (story bars + the reference rule), figure stamps
(`figure`), span brackets (`bracket`), a numbered agenda (a `figure` pair), the draw of a line (build_to), the held
light, the morph from a line's end to a bar (P48 `chart_to`).

**The finding that shapes the plan:** their clean feel is BUILDS inside a held composition (70 of 120 events), not
cuts. Every species below is therefore a build ON a held surface, keyed to a word, with a declared target - the motion
menu's law - never a new plate.

## Intent And Acceptance

Intent: (a) four species ported as mechanisms into the scene-evidence player, each opt-in, each a pure function of t,
each passing the life check on its own region (E56 §3); (b) a **species-by-sentence map** - a table keyed by what a
sentence DOES (quotes someone, ranks, compares over time, names places and flows, explains a mechanism, divides a
whole, turns on a number, spans a period, sets an agenda, retracts a claim) that names the surface (§9.28) and the
species (§9.27 + the four) an author reaches for, with the gate letters - written where an agent finds it at authoring
time (the skill, the pipeline page, the registry) and checked by a lint that reads the narration beside each row;
(c) the backlog rows that blend with (a) pulled into the slices rather than left standing.

Acceptance:
- Goldens byte-identical with every new species absent (`test_golden_frames.py`); one new golden surface per species;
  `test_portrait_parity.py` green; `test_targeted_species.py` extended per species.
- A proof page on one clock (`steel-and-paper/build-f/bravos-grammar-proof.html`, the house pattern of
  `ledger-species-proof.html`): a press-card stack, a flow diagram with a swap, a vector map with two lights and an
  arc, a treemap with two X marks - read by the operator as frames, judged in motion.
- The species-by-sentence table exists in three places that agree (`docs/content-video-engine/SPECIES-BY-SENTENCE.md`,
  the `when` field on every kind in the compiler's registry, the episode-build skill's authoring step) and
  `docs_find "ranking sentence"` (or any act name) hits it; `lint_species_choice.py` runs on the tariff and Tokyo
  shot tables and reports every sentence-act with an available species and no row (INFO on the shipped shorts).
- The backlog rows named in T8 are closed or re-pointed in the same commits that ship them.

## Scope

- Player template (`docs/content-video-engine/samples/scene-evidence-player.template.html`) species block; the
  compiler's registry and validation (`build_scene_timeline_f.py`); `ledger_page.py` for the treemap builder;
  `gate_motion_density.py` event tables for the new kinds; tests; the proof page; the docs named below; the
  episode-build skill's authoring step; CAPABILITIES rows and the backlog.

## Not Building

- Their look: one accent, the pink, the black stage, no captions. Our tokens (charcoal 60 / chalk 30 / coral +
  sunflower 10) and E21's stage captions stand; the operator may rule on a single accent separately (a human gate).
- A runtime import of anything (motion menu law: mechanisms port, code does not).
- A host removal or a caption removal because Bravos has none.
- The camera (P49 has it), the ink bloom (TR-14), the chart-to-chart family (P48) - referenced, not re-planned.
- A GIS: the vector map is one simplified world outline (Natural Earth 110m, ~80 KB as paths) with country ids; no
  projection changes, no zoom levels beyond the camera the player already has.

## Human Gates

1. **The treemap ruling.** Ruled 2026-09-10 (*"yes, we want the exception"*): E53 §1's second amendment, the CENSUS
   exception - breadth or a named subset, the subset marked and its share written, labels only where they fit, a size
   claim takes its bar. T6 is unblocked under those four.
2. **The species-by-sentence taxonomy.** The ten sentence acts in T1 - the operator, 2026-09-10: *"sounds like it makes
   sense"* - approved as drafted.
3. **The tv-embed plate (T7)** needs a Flow order (ask before driving the session) - or a still the operator generates
   by hand, as with the fab plate.
4. **One accent?** Ruled 2026-09-10: *"I think 2 accents is fine"* - coral + sunflower stand; no change.
5. Push authorization per commit, as standing.

## Mandatory Reads

- `docs/runbooks/RECALL-RECEIPT.md`; `docs/portable/OPERATOR-RULINGS.md` E21, E25, E50, E53, E56.
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.27, §9.28 (and 9.15, 9.26).
- The Bravos report and ledger (above); `46-REFERENCE-RHYTHM.md` §46.7.
- `docs/content-video-engine/39-EVIDENCE-CHART-SYSTEM.md` §10; `CAPABILITIES.md`; `BACKLOG.md` §"Registry read".
- `content/video_engine/scripts/build_scene_timeline_f.py` (`SPECIES_KINDS` … `validate_species`); the template's
  species block (`const SP`, `resolveTarget`, `paintSpecies`); `ledger_page.py` (builders); `tests/test_targeted_species.py`,
  `tests/test_golden_frames.py`, `tests/test_portrait_parity.py`.
- Skills: `evidence-motion-engine` (the ruling set), `episode-build` (the authoring step this plan extends). No
  `backend-patterns` / `frontend-patterns` (no server, no React).

## Execution Path

1. T1 first - the map is what makes the rest usable, and it is cheap. It ships with a `when` for every EXISTING species
   before any new one is built (the operator's second ask outranks the first).
2. T2 the icon chip (the foundation the diagram, the press card's badges and the map's chips all use).
3. T3 press-card dock, T4 flow diagram, T5 vector map - independent write sets inside the template's species block
   (each behind its own kind name), dispatched one at a time; the parent integrates and reads every frame.
4. T6 treemap after gate 1. T7 tv-embed after gate 3. T8 the backlog blends ride on the slice they belong to.
5. Every slice: goldens byte-identical, the new golden, the life check on the addition, the proof page grows one row,
   the CAPABILITIES row lands in the same commit (the recall rule 3), a `Recall:` line in the commit.

## Patterns To Mirror

- Opt-in species with a declared target and a pure-function-of-t paint: `spotlight` / `callout` in the template; the
  `idle` field (E56 §4) for life.
- A dock still with a source-aware card: `dock_png()` (Tokyo) / `dock_card()` (tariff) - the press card is this with an
  underline callout and a stack.
- The crossings map's `hop` trace on a plate (`crossings_species()`): the arc on the vector map is the same stroke on
  an SVG world instead of a painted plate.
- `chart_to` / `undraw` for a diagram node swap (the standing state runs its law backwards, the new state draws on).
- The proof page pattern `build-f/ledger-species-proof.html`; the golden surfaces list in `render_baseline.py`.
- The census form (§9.28 "The decision, per window") is the shape of the lint's output.

## Task Slices

### T1: The species-by-sentence map, the `when` on every kind, the lint, the skill step
- Status: pending
- Owner: parent (the taxonomy and the doc); `junior_developer` for the lint once the table exists
- Depends on: none (human gate 2 before the skill edit)
- Write set: `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (new); `content/video_engine/scripts/build_scene_timeline_f.py`
  (`SPECIES_WHEN: dict[kind -> one line]` beside `SPECIES_KINDS`, exported by `build_animation_registry.py`);
  `content/video_engine/scripts/lint_species_choice.py` (new) + `content/video_engine/tests/test_lint_species_choice.py`;
  `docs/content-video-engine/PIPELINE.md` stage 7 (one line: the map); `C:/Users/Snipe/.claude/skills/episode-build/SKILL.md`
  (one authoring step: classify each sentence's act, look up the row); `docs/content-video-engine/CAPABILITIES.md`
  (a `Use when` clause on every species row).
- Acceptance: the table keys ten sentence acts - QUOTES someone (their claim) -> press-card dock (B1); RANKS ->
  race bars (page A1-A3 or dock B2); COMPARES over time -> line page / dense-line dock, terminal tags; DIVIDES a whole
  -> share page (donut) / treemap after gate 1; NAMES places and flows -> vector map (light, arc, stamp); EXPLAINS a
  mechanism (A causes B via C) -> flow diagram (chips + arrows), the swap for a rhyme; TURNS on a number -> figure
  stamp / the light on the datum; SPANS a period -> bracket / span; SETS an agenda ("two things") -> numbered figures;
  RETRACTS a claim ("none of this happened") -> the icon board crossed out. Each row: the surface, the species, the
  target kind, the gate letters, an example sentence from the tariff or Tokyo take. `docs_find "<act>"` hits it. The
  lint reads a shot table's rows + the take's words, classifies each sentence by a keyword table (crude on purpose, like
  V05), and prints `sentence · act · species available · row has: <species or none>`; INFO, never FAIL.
- Validate: `python content/video_engine/scripts/lint_species_choice.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick`
  and the same for `tokyo-tea-break`; `python -m pytest content/video_engine/tests/test_lint_species_choice.py -q`;
  `python content/video_engine/scripts/build_docs_layers.py --check`; `python content/video_engine/scripts/docs_find.py "ranking sentence"`.
- Evidence: pending

### T2: The icon chip
- Status: pending
- Owner: `implementation_luna` (bounded: one species, one CSS block, one test); parent reviews the frames
- Depends on: T1 (the `when`)
- Write set: template species block (`kind: "chip"`: a rounded dark square with one glyph from
  `content/video_engine/assets/icons/` (SVG, sourced per A2a) and a label beneath, at a declared point or region, with
  `idle`); `build_scene_timeline_f.py` (`SPECIES_KINDS += chip`, targets point|region, fields `icon`, `label`,
  `state: on|crossed`); `tests/test_targeted_species.py`; a golden `chip-board`; CAPABILITIES row.
- Acceptance: a chip lands on a word with the badge spring (R26-20's two-spring landing rides here), can be CROSSED on a
  later word (the Bravos icon board: predictions crossed out one by one - shots 26-28); the life check 0 identical
  pairs; goldens byte-identical without it.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_targeted_species.py content/video_engine/tests/test_portrait_parity.py -q`
- Evidence: pending

### T3: The press-card dock and the stack hand-off
- Status: pending
- Owner: parent (the dock kinetics touch the throw/land code); `junior_developer` for the crop tool
- Depends on: T2
- Write set: `content/video_engine/scripts/press_card.py` (new: a screenshot -> a card cropped to its headline, source
  line stamped, the key phrase's region declared); template (dock kind `press`: the card lands, a `callout` with
  `form: "underline"` on the declared phrase region, and a `stack` option: the previous press card dims and slides
  back, the newest lit - the motion menu's **push hand-off**, unbuilt until now); `build_scene_timeline_f.py`
  (`DOCK_OPTS += press, stack`); `gate_motion_density.py` (a stack step is an event); tests; golden `press-stack`.
- Acceptance: three cards stack on three words on a bare plate (shots 5-10's grammar); each landing is an event; the
  underline draws on the phrase (E56: a label of a value or a datum is allowed; an underline on a quoted phrase is the
  squiggle law, §9.27); B1 holds: their claim never pages.
- Validate: the test suite above + `python content/video_engine/scripts/gate_motion_density.py <proof build>`
- Evidence: pending

### T4: The flow diagram (chips + arrows + the swap) and the span bracket
- Status: pending
- Owner: `implementation_luna` for the SVG layout (a dashed box, N chips, arrows between named chips); parent for
  the swap (it reuses `chart_to`'s law: the standing node un-draws, the new node draws on the same spot)
- Depends on: T2
- Write set: template (`kind: "flow"`: fields `nodes: [{id, icon, label}]`, `edges: [[a, b]]`, `box: region`,
  `swap: {node, icon, label}` on a later word, `tag: "1973"` a year stamp); `build_scene_timeline_f.py`; R26-25's
  `span` species (a shaded region with a label between two declared points - the "Decades" bracket, shots 107-110)
  lands here; tests; golden `flow-swap`.
- Acceptance: the Bravos rhyme (shots 82-86): a three-node diagram draws on a word; on a later word one node swaps
  and the rest stands; the swap is one event; the life check passes; nothing spins.
- Validate: the test suite above
- Evidence: pending

### T5: The vector map - a world that lights, an arc that crosses, a stamp that lands
- Status: pending
- Owner: `implementation_luna` for the data (Natural Earth 110m -> `assets/maps/world-110m.paths.json`, ids by ISO
  A3, simplified to <= 450 path nodes per country per the C4 seek envelope); parent for the species
- Depends on: T2 (the chips on the map)
- Write set: `content/video_engine/assets/maps/` (new); template (world kind `vecmap`: the outline in the muted ink
  on the stage, `light: [countries]` on a word (fill to the accent with a 0.3 s ease, `idle` breath), `arc: {from, to,
  crossed}` (the hop trace's stroke between two centroids, an X at the midpoint when crossed), `stamp: {country,
  text}` (a `figure` at the centroid), `year: "1996"` (a figure at a declared point)); `build_scene_timeline_f.py`
  (`world.kind == "vecmap"`); tests; golden `vecmap-arc`; `test_portrait_parity.py` (the map fits both aspects).
- Acceptance: shots 57-80's grammar on one clock: Iran lights, an arc from the Gulf to the US crosses, "1996" stamps,
  China lights and takes "1.4 Billion Barrels"; every event keyed to a word; M16 counts each light and arc; the light
  on a country is the spotlight species' cousin, never a ring (E56).
- Validate: the test suite above; `python content/video_engine/scripts/measure_frozen_frames.py <proof build>`
- Evidence: pending

### T6: The treemap page builder with X marks
- Status: pending (gate 1 ruled 2026-09-10 - the census exception, E53 §1 second amendment)
- Owner: `implementation_luna`
- Depends on: T1
- Write set: `content/video_engine/scripts/ledger_page.py` (builder `treemap` from a `series.json` of shares; the
  squarified layout, labels only where the cell fits, the rest unnamed; `cross: [names]` on a word and the crossed
  share WRITTEN on the page (the census exception's (b)); the builder REFUSES a series whose claim field names a size
  comparison); template (`paintLedger` treemap variant); tests; golden `treemap-cross`.
- Acceptance: shots 89-91's grammar: a treemap of exports by partner; on a word three partners take an X; the map
  shrinks to a chip on the next (a `chart_to: recast` or an exit).
- Validate: the test suite above + `python content/video_engine/scripts/ledger_page.py --check <series>`
- Evidence: pending

### T7: The tv-embed world for the external lane
- Status: pending (human gate 3)
- Owner: parent
- Depends on: T3
- Write set: one generated plate (a TV in a dark room, the screen as a declared dock slot) per channel under
  `channel-assets/money-physics/plates/`; `build_scene_timeline_f.py` (a plate may declare `slots: [{region}]` that a
  press dock lands INTO, with the room's vignette darkening on a word - shots 20-22).
- Acceptance: the tariff short's first press quote (if any) plays on the TV; the argument's own charts never do (B1).
- Validate: frames at the seam; the test suite
- Evidence: pending

### T8: The backlog blends - pulled onto the slices they belong to
- Status: pending
- Owner: parent (re-pointing rows); the owner of each host slice
- Depends on: the host slices
- Write set: `docs/content-video-engine/BACKLOG.md` rows re-pointed: **R26-20** badge-stamp two-spring landing ->
  T2 (the chip lands with it); **R26-25** the `span` species -> T4; **R26-24** N-tier pages (small multiples, shared
  x) -> a T5-adjacent slice on `ledger_page.py` (Bravos' two-panel SPR, shots 35-36 - the strongest blend of all;
  **T9**); **R26-1** field-coloured halo on direct labels -> the terminal
  tag + value bar (shots 104-105), on T1's table as the COMPARES row's finish; **motion menu: push hand-off** ->
  T3; **radial reveal** -> T5's light (a country reveals from its centroid); **beat-freeze chart exit** -> the
  COMPARES row's C1 (unchanged, cited); **R26-22** centred placement by E50's clock -> the press stack's park.
  Rows that do NOT blend (noted so nobody reaches): R26-4 the chart on the hook (Bravos opens on press cards, not a
  chart - a different answer to the same beat, not a contradiction), R26-6 a returning character (they have none),
  TR-14 the ink bloom (they cut and dip), weight-shift captions (they have no captions).
- Acceptance: every row above carries the slice id and the Bravos shot numbers; no row is closed without the build.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: pending

### T9: N-tier pages - small multiples on a shared x (R26-24; Bravos' two-panel SPR, shots 35-36)
- Status: pending
- Owner: `implementation_luna` (a `ledger_page.py` builder + the page's paint); parent reads the frames
- Depends on: T1
- Write set: `content/video_engine/scripts/ledger_page.py` (builder `tiers`: N series objects on one page, each its own
  y-scale and honest zero (E53 §4), one shared x, the tier titles as the series names, one source line); template
  (`paintLedger` tiers variant: the tiers draw in turn on their words, `build_to` per tier, the drop of one tier as a
  bar in the accent - shot 36); tests; golden `tiers-two`; CAPABILITIES row; BACKLOG R26-24 -> BUILT.
- Acceptance: Japan SPR | US SPR on one page, drawn in turn, the drop bar on a word; the page is OURS (A1-A3) when the
  series are; goldens byte-identical without it; the life check on the page region.
- Validate: the test suite in Verification + `python content/video_engine/scripts/ledger_page.py --check <series>`
- Evidence: pending

## Verification

- `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_targeted_species.py content/video_engine/tests/test_portrait_parity.py content/video_engine/tests/test_lint_species_choice.py -q`
- The proof page `build-f/bravos-grammar-proof.html` rendered at the instants that matter (the scratch frames
  pattern), read as a viewer, the life check on every addition's region (0 identical 0.25 s pairs), M16/M18 on the
  proof build.
- `python scripts/prp_validate.py .claude/PRPs/plans/P50-BRAVOS-GRAMMAR.plan.md`; `build_docs_layers.py --check`.
- Judgement stays the operator's: each species is declared when its frames are approved, never when its test passes.

## Evidence And Handoff

- Per slice: the commit hash, the golden's path, the proof frames, the life-check numbers, the CAPABILITIES row.
- The species-by-sentence table's first real use: the next short's shot table is authored against it and the lint's
  report is attached to its REVIEW.
- All four gates answered 2026-09-10; R26-24 joins as T9 and
  every matching backlog row rides its slice (operator: *"yes we should add all of the backlog blends that are matches"*).
