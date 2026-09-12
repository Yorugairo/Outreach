---
id: P50-BRAVOS-GRAMMAR
title: The Bravos grammar and the burn-down - the species we lack, the art-embed world, the hand-offs that carry continuity, the last drawing-kinetics law, and a species-by-sentence map so an agent knows when to use what we have
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-10
updated: 2026-09-10 (amended the same night with the operator's burn-down)
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

**Amended the same night (the operator's burn-down, after Gemini's un-filed Bravos summary was mapped -
`REPORT.claude.md` §"mapped", `EXPLORATION-REVIEW-2026-09-10.md`):** *"we should probably add the additional morph
method. Parallax isn't all that important right now ... It also doesn't have to be a TV. If Bravos has the chart world and
the TV world, we could have the chart and the 'art' world -- our narrative plates/paintings ... the press card + tv embed
or art embed world. Probably the vector map, burst furniture, line-end tags as next chart's bars is a great add to help us
increase our continuity ... HF17, HF-15, HF-16, MC-8, r26-30 blend, r26-27, r26-25, R26-24, R26-22, r26-20, r26-16, TR-7's
ARAP invariants as compiler refusals ... with that, we should probably finish our drawing kinetics too."* And the question
that orders the plan: *"Do we already have an understanding mapped in docs to how/where to know when to use these
capabilities if we build them?"* - the surfaces yes (§9.28 A/B/C/D), the species and the verbs no: that is T1, and it
now covers E58's five verbs, E59's four reasons a camera moves, E60's burst, the dock read->park and the un-park.

**APPROVED 2026-09-11** (the operator: *"approve both plans"*). The order by slice across the two plans stands as written in the Execution Path: P50 T1 -> P51 T0, T2, T3 -> P50's species as modules -> P51 T1, T4-T7; P51 T8 in parallel.

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
- Parallax as a mechanism (the operator, 2026-09-10: *"Parallax isn't all that important right now"*): R26-32's sine
  micro-pan is dropped; only the planar homography survives, as the art-embed's surface projection (T7).
- A TV. Our second world is the ART world - the narrative plates and paintings we already make; the external lane lands
  on them (T7), never on a monitor.
- A GIS: the vector map is one simplified world outline (Natural Earth 110m, ~80 KB as paths) with country ids; no
  projection changes, no zoom levels beyond the camera the player already has.

## Human Gates

1. **The treemap ruling.** Ruled 2026-09-10 (*"yes, we want the exception"*): E53 §1's second amendment, the CENSUS
   exception - breadth or a named subset, the subset marked and its share written, labels only where they fit, a size
   claim takes its bar. T6 is unblocked under those four.
2. **The species-by-sentence taxonomy.** The ten sentence acts in T1 - the operator, 2026-09-10: *"sounds like it makes
   sense"* - approved as drafted.
3. **The art-embed slot (T7)**: the first narrative plate that carries a declared embed surface (a poster on the wall,
   a paper on the desk, a framed picture) needs a Flow order (ask before driving the session) - or a still the operator
   generates by hand, as with the fab plate.
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
   **The module rule (2026-09-11, so nothing built here is ported later):** from T2 on, no new species is written into the
   template's body. Each is a file under `content/video_engine/scripts/species/<kind>.mjs`, inlined by `sync_kinetics.py`
   exactly as the ten kinetics modules are, with its own `tests/kinetics/<kind>.test.mjs`; P51 T1 (the runtime apart
   from the document) then changes only how the modules are LOADED. The order across the two plans by slice: P50 T1 ->
   P51 T0 (the kit), T2 (eyes), T3 (the bar) -> P50 T2-T16 as modules -> P51 T1 (the split), T4-T7.
2. T2 the icon chip (the foundation the diagram, the press card's badges and the map's chips all use).
3. T3 press-card dock, T4 flow diagram, T5 vector map - independent write sets inside the template's species block
   (each behind its own kind name), dispatched one at a time; the parent integrates and reads every frame.
4. T7 the art embed after gate 3, right after T3 (the press card needs a world to land on). Then T4 + T14 together (the
   flow diagram's arrows are the clothoid fitter's first customer), T5 (the map's arcs its second), T11 (the tags-to-bars
   hand-off), T10 (the burst's furniture), T13 (the stop-motion burst), T12 (morph Method A + TR-7's refusals), T9, T15,
   T16. T6 the treemap when a beat asks for it (gate 1 is ruled). T8 the backlog blends ride on the slice they belong to.
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
- Status: complete (2026-09-11)
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
  RETRACTS a claim ("none of this happened") -> the icon board crossed out. **Widened the same night:** TURNS on a
  number that BREAKS the honest scale -> the burst (E60; the comparator's level, the hold, the shoot) with its
  furniture (T10); the SAME data in another form or window -> E58's five verbs (rescale / extend / keyed recast / park /
  morph_to), each with its beat, and the park's two laws (a park stands until the next park; 1.0 is the un-park when
  the cards leave and the chart re-takes the stage); a card that must be READ then KEPT beside the chart -> the dock
  read->park (`read` / `read_s` / `park_s`); the four reasons a camera moves (E59: a landing, a wider stage, the arrival,
  the three species) and the nevers. Each row: the surface, the species or verb, the target kind, the gate letters, an
  example sentence from the tariff or Tokyo take. `docs_find "<act>"` hits it. The
  lint reads a shot table's rows + the take's words, classifies each sentence by a keyword table (crude on purpose, like
  V05), and prints `sentence · act · species available · row has: <species or none>`; INFO, never FAIL.
- Validate: `python content/video_engine/scripts/lint_species_choice.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick`
  and the same for `tokyo-tea-break`; `python -m pytest content/video_engine/tests/test_lint_species_choice.py -q`;
  `python content/video_engine/scripts/build_docs_layers.py --check`; `python content/video_engine/scripts/docs_find.py "ranking sentence"`.
- Evidence: `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (the ten acts + the widened rows; s4 generated from the compiler); `SPECIES_WHEN` / `CHART_TO_WHEN` in `build_scene_timeline_f.py` (every kind, asserted at import); `lint_species_choice.py` + `tests/test_lint_species_choice.py` (12 tests: the three places agree, the classifier on the shipped sentences, INFO-only on both shorts, E61's WARN on a long-form plate); PIPELINE stage 7; the episode-build skill's authoring step; a `Use when` clause on 44 CAPABILITIES rows. Deviation: `;use=` is READ by the lint but not yet accepted by the compiler's `PLATE_OPTS` (no engine code in T1 by the operator's goal) - P51 T0 adds the token where the row grammar is consolidated; the registry export named in the write set is the docs layers (the map is indexed and `docs_find "ranking sentence"` hits it), not `build_animation_registry.py`, which covers the kinetics modules only.

### T2: The icon chip
- Status: complete (2026-09-11) - the first species MODULE; the mechanism shipped with it
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
- Evidence: (A) the mechanism - `sync_kinetics.py` scans `scripts/species/` with `kinetics/` (11 modules: 10 + 1), the template's `SPECIES_PAINTERS` registry + the one hook in `paintSpecies`, `tests/test_kinetics_sync.py` (13; the inline_text block-comment fix with its regression test); (B) the chip - `scripts/species/chip.mjs` (110), `tests/kinetics/chip.test.mjs` (node, 84 across the kinetics tests), `build_scene_timeline_f.py` (+82: the kind, the `when`, the validation, `icon_geometry`), `gate_motion_density.py` (+11: field-named edges), `tests/test_targeted_species.py` (+4), the golden `chip-board`, `assets/icons/` (Lucide v1.45.0 ISC, five files, SOURCES.md + LICENSE). Validated by the parent: `sync_kinetics --check` in sync; goldens + targeted species + portrait parity + lint + kinetics sync + the gate: 139 passed; node 84/84; the filmstrip (t=5.22 the first landing mid-spring, 6.42 the second beside it, 10.37 the cross mid-draw, 11.00 the settled board) read by the parent: the board lands, strikes and dims as designed; the life check alive (18,875 bytes between two 30 fps frames on the held board). CAPABILITIES rows (the mechanism, the chip); the map's rows 6 and 10 mark the chip built. Note for the first cut that uses it: the cross is sunflower; a blood-red strike for a RETRACTED claim is a dial to rule.

### T3: The press-card dock and the stack hand-off
- Status: complete (2026-09-11)
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
- Evidence: `scripts/press_card.py` (135; `tests/test_press_card.py` 130), `scripts/species/press.mjs` (115; `tests/kinetics/press.test.mjs` 162), `build_scene_timeline_f.py` (+173: `DOCK_KIND_PRESS`, `press_meta`, `assign_press_stack`, the `phrase` target and the `underline` form admitted for a callout alone, `press_plate_error`), the template (+237: `paintPress` outside the two slots, the underline riding the card's live geometry), `tests/test_press_dock.py` (113), `test_targeted_species.py` (+5), `test_gate_motion_density.py` (+1: a stack step is already a dock event, the underline counts at its word), the golden `press-stack`. Validated by the parent: sync_kinetics 12 modules (10 + 2); 235 tests across goldens (15, existing byte-identical), species, press, video dock, read->park, the gate, sync, portrait parity, lint, breakthrough, camera; node 96/96; the filmstrip (5.30 the first card mid-spring, 7.55 the second arriving as the first is shoved back, 9.95 the third, 10.75 the underline mid-draw, 11.40 the settled fan) read by the parent. Deviations: no new species KIND (a press card is a dock kind; `SPECIES_WHEN['push']` re-worded to say the hand-off shipped as the stack); an E45 guard the brief did not ask for (a press dock on a ledger plate is refused - reverse when a cut wants quotations beside a parked chart); the build-loop seam is unit-tested, not episode-built - the first cut with a press row closes it.

### T4: The flow diagram (chips + arrows + the swap) and the span bracket
- Status: complete (2026-09-11)
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
- Evidence: `scripts/species/flow.mjs` (248) + `tests/kinetics/flow.test.mjs` (250); `scripts/species/span.mjs` (103) + `tests/kinetics/span.test.mjs` (123); the compiler (`flow`, `span` in SPECIES_KINDS / SPECIES_WHEN / validate_species; `span` a PAGE species), the gate, the lint's availability table (EXPLAINS: chip + flow; SPANS: span), the template (the flow painter through the registry; the span on the perform layer); goldens `flow-swap` and `span-decade` (read by the parent: PLANTS -> CHIPS -> PRICE with smooth clothoid arrows and the 1973 tag; THE RUN-UP shaded behind the memory-makers lines). The parent's run: node 140/140 across the kinetics tests; sync_kinetics 15 modules (11 kinetics, 4 species); goldens byte-identical. The agent hit its turn limit at the span node test and was resumed for the compiler tests, the filmstrip and the report.

### T5: The vector map - a world that lights, an arc that crosses, a stamp that lands
- Status: complete (2026-09-11) - the data (06dae01) and the world + species
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
- Evidence: the data (commit 06dae01): `build_world_map.py`, `assets/maps/world-110m.paths.json` (186,741 bytes, 177 countries, nodes min 6 / median 36 / max 442, the source pinned by blob hash), `tests/test_world_map.py` (24). The world and the species: `scripts/species/vecmap.mjs` (357) + `tests/kinetics/vecmap.test.mjs` (272); the compiler (`vecmap[:<A3 list>]`, the focus fit for both aspects, the map shipped once in the asset map, `light` / `arc` / `stamp` with `size: figure|year`, the `country` and `mappoint` targets admitted only on a vecmap world), the gate, the lint (NAMES: light, arc, stamp; the pending line closed), the template's thin world branch; the golden `vecmap-arc` (read by the parent: the world in muted ink, IRN and CHN lit, the USA the focus outline, the Gulf -> US arc crossed with its X, 1996 and 1.4 Billion Barrels stamped). The parent's run: sync_kinetics 16 modules (11 + 5); node 159/159; 187 across goldens (existing byte-identical), targeted species, portrait parity, lint, sync, gate, world map. The agent hit its turn limit at the compiler tests and was resumed for the filmstrip and the report.

### T6: The treemap page builder with X marks
- Status: complete (2026-09-11) - gate 1 ruled 2026-09-10 (the census exception, E53 §1 second amendment)
- Owner: `implementation_luna`
- Depends on: T1
- Write set: `content/video_engine/scripts/ledger_page.py` (builder `treemap` from a `series.json` of shares; the
  squarified layout (Bruls 2000; the aspect tuned toward 3:2, never 1:1 - Heer & Bostock 2010's square penalty), labels
  only where the cell fits (the research's floors: value font >= 18 px, no text in a cell under 80 x 36 px; three tiers -
  two lines, one stacked line, none), the rest unnamed; `cross: [names]` on a word and the crossed share WRITTEN on the
  page (the census exception's (b)); the shrink afterwards is P48's `park` (one affine transform, never a re-layout -
  Sondag 2018); the builder REFUSES a series whose claim field names a size comparison); template (`paintLedger`
  treemap variant); tests; golden `treemap-cross`. Research: `docs/research/tech/TREEMAP_READABILITY_RESEARCH_BLUEPRINT.md`
  §6-7 and `docs/research/runs/treemap-readability/findings_typography_and_mobile.md` §5 (Gemini, 2026-09-10) - tiers:
  the Bravos teardown is CONFIRMED against our own frames; the perception papers and the ISO floors are PLAUSIBLE
  (cited by DOI, not on disk); the blueprint's "container x 60, y 280, w 960, h 1060" is EDITORIAL - the plot box is
  `page_boxes`'s, not a research doc's.
- Acceptance: shots 89-91's grammar: a treemap of exports by partner; on a word three partners take an X; the map
  shrinks to a chip on the next (a `chart_to: recast` or an exit).
- Validate: the test suite above + `python content/video_engine/scripts/ledger_page.py --check <series>`
- Evidence: `ledger_page.py` builder `treemap` (the squarify toward 3:2, the label tiers by the research floors, the size-claim refusal), `scripts/species/treemap.mjs` + `tests/kinetics/treemap.test.mjs`, the `cross` species in the compiler (the named cells' X's and the written share), the lint (DIVIDES: treemap page, cross; COMPARES: tiers page; the pending line closed), the golden `treemap-cross` (read by the parent: China's exports by partner, US / Japan / Korea crossed, "3 partners, 26 % of exports" written, "and 7 others"). The agent hit its turn limit and was resumed for the filmstrip and the report.

### T7: The ART-embed world for the external lane (was: the tv-embed)
- Status: built 2026-09-11 (night) - the mechanism WIRED against the poster's measured quad; gate 3 GRANTED the same night: "Plate order is approved." - the order in `docs/content-video-engine/briefs/ART-EMBED-PLATE-ORDER-2026-09-11.md` (the house style atom; the first still with the poster; the second with the TV on the wall and the laptop on the desk) goes to the Flow session next; the mechanism (the named quads on the manifest, the homography, the press card landing on a surface) follows the stills
- Owner: parent
- Depends on: T3
- Write set: `build_scene_timeline_f.py` (a narrative plate may declare `embed: {quad: [[x,y]x4], darken: <word>}` -
  a surface INSIDE the painting - a poster on the wall, a paper on the desk, a framed picture - that a press dock lands
  ONTO); the template (the dock projected onto the quad by a planar homography - the CSS `matrix3d` from the four
  corners, Gemini's H with `h22 = 1`; the room's vignette darkening on the word; the card's own idle stays); one
  plate per channel that carries such a surface under `channel-assets/money-physics/plates/` (gate 3); the press
  card's badges and underline in the projected space.
- Acceptance: Bravos has the chart world and the TV world; we have the chart world (the ledger page) and the ART world
  (our narrative plates). The tariff short's first press quote (if any) lands on a painted surface in perspective and
  reads; the argument's own charts never do (B1); the goldens hold; the life check on the embed's region.
- Validate: frames at the seam; the test suite
- Evidence: `kinetics/homography.mjs` (154; 9 node tests - the unit square to an axis-aligned rect is affine, a keystone's corners return within 1e-9, the identity quad gives the identity matrix3d), the compiler's `embed` grammar (+213: the named surfaces on `<plate>.layers.json`, the quad validated, an unknown name refused naming the plate's surfaces, a ledger page / a chart card refused - B1, `darken` resolved to a second, `embed {name, quad, darken, img}` on the entry), the engine (+334: the inscribed card under the homography, the arrive onto the surface, the idle kept, no park, the room's darkening on the word, the camera target `embed`), `tests/test_art_embed.py` (19), golden `art-embed` (two cold renders identical; every other golden byte-identical). The two stills (`channel-assets/money-physics/plates/stills/art-embed-study-{poster,tv-laptop}.png`, 768x1376, zero credit) are QUARANTINED until the operator approves the frames; the poster's quad measured from the still `[[0.3685,0.1941],[0.8307,0.1560],[0.8307,0.6247],[0.3685,0.6106]]` (0.462 wide; the order asked for 0.40); the still is 0.5581 aspect against 9:16's 0.5625, so re-measure on the rendered stage when writing the plate's layers file. Deviations: the golden's second surface (the desk paper) is synthetic; the poster came back portrait where the order asked for a near-horizontal long side (the card fits its width, not re-rolled).

### T8: The backlog blends - pulled onto the slices they belong to
- Status: pending
- Owner: parent (re-pointing rows); the owner of each host slice
- Depends on: the host slices
- Write set: `docs/content-video-engine/BACKLOG.md` rows re-pointed: **R26-20** badge-stamp two-spring landing ->
  T2 (the chip lands with it); **R26-25** the `span` species -> T4; **R26-24** N-tier pages (small multiples, shared
  x) -> a T5-adjacent slice on `ledger_page.py` (Bravos' two-panel SPR, shots 35-36 - the strongest blend of all;
  **T9**); **R26-32** the studio display stage -> T7 (the homography only; the sine pan dropped with parallax);
  **R26-33** the sonar ping -> T5 (a `ping` at a lit country: `r(t) = r_max ((t - t0) mod T) / T`, `alpha = 1 - r /
  r_max`); **R26-34** the tip-riding pill -> T11 (the pill rides the tip during the draw, then IS the terminal tag);
  **MC-8** spread / divergence -> CLOSED (built as the `spread` species, R26-26 - the intake's EXPLORE row is stale);
  **R26-1** field-coloured halo on direct labels -> the terminal
  tag + value bar (shots 104-105), on T1's table as the COMPARES row's finish; **motion menu: push hand-off** ->
  T3; **radial reveal** -> T5's light (a country reveals from its centroid); **beat-freeze chart exit** -> the
  COMPARES row's C1 (unchanged, cited); **R26-22** centred placement by E50's clock and **R26-27** page_boxes vs the
  player's layout -> T16 (one placement truth); **R26-16** the planted-element morph -> T12 (Method A's first use);
  **R26-20** the two-spring landing -> T2 (as before); **R26-30** the stop-motion burst -> T13; **HF-15 / HF-16 /
  HF-17** -> T15.
  Rows that do NOT blend (noted so nobody reaches): R26-4 the chart on the hook (Bravos opens on press cards, not a
  chart - a different answer to the same beat, not a contradiction), R26-6 a returning character (they have none),
  TR-14 the ink bloom (they cut and dip), weight-shift captions (they have no captions).
- Acceptance: every row above carries the slice id and the Bravos shot numbers; no row is closed without the build.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: pending

### T9: N-tier pages - small multiples on a shared x (R26-24; Bravos' two-panel SPR, shots 35-36)
- Status: complete (2026-09-11)
- Owner: `implementation_luna` (a `ledger_page.py` builder + the page's paint); parent reads the frames
- Depends on: T1
- Write set: `content/video_engine/scripts/ledger_page.py` (builder `tiers`: N series objects on one page, each its own
  y-scale and honest zero (E53 §4), one shared x, the tier titles as the series names, one source line); template
  (`paintLedger` tiers variant: the tiers draw in turn on their words, `build_to` per tier, the drop of one tier as a
  bar in the accent - shot 36); tests; golden `tiers-two`; CAPABILITIES row; BACKLOG R26-24 -> BUILT.
- Acceptance: Japan SPR | US SPR on one page, drawn in turn, the drop bar on a word; the page is OURS (A1-A3) when the
  series are; goldens byte-identical without it; the life check on the page region.
- Validate: the test suite in Verification + `python content/video_engine/scripts/ledger_page.py --check <series>`
- Evidence: `ledger_page.py` builder `tiers` (N in [2, 4], one shared x, each band its own honest scale; the two-band form byte-identical), `scripts/species/tiers.mjs` + `tests/kinetics/tiers.test.mjs`, `tests/test_ledger_page.py`, the golden `tiers-two` (read by the parent: JAPAN | UNITED STATES on 2015-2025, the -96 Mb drop bar in the accent). The parent's run with T6: node 173/173; 231 across goldens (existing byte-identical), species, portrait parity, lint, sync, gate, ledger, breakthrough; sync_kinetics 18 modules (11 + 7). R26-24 closed.

### T10: The burst's furniture (Bravos 8:01.8-8:03.2; E60 built the burst)
- Status: complete (2026-09-11)
- Owner: `implementation_luna`; parent reads the frames
- Depends on: T1
- Write set: template `buildLedgerBars` / `lpPaintBreakthrough` (a `placeholder: "?"` state: the breaking bar's track
  stands grey with a "?" stamp until its number is spoken, then the comparator level and the burst as today; the
  value capsule mounted ON THE AXIS under the bar's end, counting up, with a dotted leader from the bar's end to the
  axis - the pill above the tip stays the default, the capsule an option `capsule: "axis"`); `ledger_page.py`
  (`overflow_capsule`, `placeholder` keys); `test_breakthrough.py` (+3); the proof page grows a row.
- Acceptance: the Tokyo "beats our bonds" beat renders identically with the options off (goldens; the cut's frames
  byte-identical); with `placeholder` on, the chips track reads "?" through "if that works" and the capsule lands on
  the axis at 36.59 % with its leader; the life check on the page region.
- Validate: `python -m pytest content/video_engine/tests/test_breakthrough.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: `scripts/species/breakthrough.mjs` (160; `tests/kinetics/breakthrough.test.mjs` 19 node tests), the template (+254: the "?" track and stamp until the hold, the axis capsule with `breakCapsuleFit` and the dotted leader routed beside the bar), `ledger_page.py` (`overflow_placeholder` - `placeholder` already means SOURCES-TO-VERIFY, the collision caught by an existing test - and `overflow_capsule`), `proof_breakthrough.py` (four proof pages: burst, stack, furniture, stop), `test_breakthrough.py` (+3). The parent's run: sync 19 modules (11 + 8); node 192/192; 202 across breakthrough, goldens (byte-identical - the options are off), gate, probe, portrait parity, sync, lint, ledger; the filmstrip read by the parent (5.00 the "?" mid-build, 5.85 the count at the hold with the capsule and leader, 6.37 mid-shoot). A dial to rule on the first cut: the y-axis capsule for vertical bars.

### T11: Line-end tags become the next chart's bars (Bravos shots 104-105; continuity)
- Status: complete (2026-09-11)
- Owner: `implementation_luna`; parent integrates
- Depends on: T1
- Write set: `build_scene_timeline_f.py` (`RECAST_PAIRS` gains `("dense-line", "story")` KEYED ON THE TERMINAL TAGS:
  each series' end tag is the mark that becomes its bar - the tag slides and grows into the bar, the line un-draws by
  length beneath it); template `lpPaintRecastKeyed` (a `tag` role in the keyed tween beside `datum`); the tip-riding
  pill (R26-34) as the tag's life during the draw: `X_pill(u) = P_tip(u) + D_offset`, a leader from the tip, popping
  on `springPop(Mp = 0.05)` at its milestone, and at the end it IS the terminal tag; `test_chart_transitions.py` (+2).
- Acceptance: a four-line yield page hands its four tags to a four-bar page with no cut and no re-draw of the values;
  the tag rides the tip during the draw and names the line at its end (E53 unchanged); goldens byte-identical.
- Validate: `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: `RECAST_TAG_PAIRS` / `RECAST_KEYS` (`keyed: "tags"`), the template's `lpPaintRecastKeyed` tag role (the hand-over on the clock, `KEYED_TAG_HAND` 0.92), `scripts/species/tippill.mjs` (103; `tests/kinetics/tippill.test.mjs` 7) with `;pill=yes|no|<n>` on the plate id, `test_chart_transitions.py` (+104), the golden `tags-to-bars` (read by the parent: the lines un-drawing, the tags standing, the bars rising to take them; the filmstrip 11.50 / 12.20 / 14.60 and the pill mid-draw at 4.75). Three defects found on the frames and fixed in place: the pill copied the tag flat (it clones the tag now), it measured its width before the webfont loaded, the hand-over ran on the eased slide. R26-34 closed; R26-42 (the pill's leader behind its capsule) and R26-43 (a tag wider than the chart: no pill, silently) logged.

### T12: Morph Method A (vertex-based) and TR-7's ARAP invariants as compiler refusals
- Status: complete (2026-09-11)
- Owner: parent (the invariants); `implementation_luna` (Method A)
- Depends on: none
- Write set: `content/video_engine/scripts/kinetics/morph_a.mjs` (new: ring-normalise, resample to N, the rotational
  alignment `argmin_k sum ||v_A,i - v_B,(i+k)||^2` - `arap.mjs` `correspond` already has it - then a direct vertex lerp
  and a cubic reconstruction per frame; doc 43 §43.5 Method A); the compiler (`morph_to` gains `method: "a" | "arap"`,
  default by doc 43's decision rule: outline-to-outline with modest rotation -> A, real rotation -> ARAP) and the
  REFUSALS (TR-7): a morph whose pair fails centroid <= 0.06 W, axis <= 15 deg, or area ratio >= 0.60 is a build error
  naming the number, never a silent bad match; `measure_morph.py` prints the three invariants; R26-16's planted
  element (the tie) as Method A's first use; `test_morph.py` (+4); M17 reads the method.
- Acceptance: the same morph renders by A and by ARAP and the frames are read side by side (a human gate on the demo,
  as HG3 was); a pair outside the invariants is refused with the measured number; goldens byte-identical.
- Validate: `python -m pytest content/video_engine/tests/test_morph.py content/video_engine/tests/test_kinetics_sync.py -q`
- Evidence: `kinetics/morph_a.mjs` (106; `tests/kinetics/morph_a.test.mjs` 8: every intermediate ring simple, the area monotone, the alignment minimal, the endpoints exact), `measure_morph.py` (+211: the three invariants for a pair, `--pair A B`; M17 opens with the method and the numbers - for A the min det measured on the strip's triangles), the compiler (`MORPH_METHODS`, `METHOD_A_MAX_DEG` 15, the three refusals naming the measured number and the limit - verbatim in the commit), the template's `lpPaintMorphTo` routing (ARAP when `method` is absent: old timelines byte-identical), `test_morph.py` (+86), `proof_morph_a.py` + `steel-and-paper/build-f/morph-a-proof.html` and `morph-a-arap-proof.html` (the same pair by both methods, for the operator's read - the human gate on the demo). The parent's run: sync 21 modules (12 + 9); node 207/207; 248 across morph, transitions, goldens (byte-identical), sync, gate, portrait parity, species, breakthrough; the filmstrip read (7.10 by A and by ARAP). Default ratified: every admitted pair defaults to A. Open: R26-16's planted element (`morph_from` across a scene boundary) is a different write set - the rule stands, the row re-worded.

### T13: The stop-motion burst (R26-30, the operator's blend)
- Status: complete (2026-09-11)
- Owner: `implementation_luna`; parent reads the frames
- Depends on: T10 (the furniture rides it)
- Write set: template `lpPaintBreakthrough` (`cadence: "stop"`: the shoot and the counter step on `stopaction.mjs`'s
  frame-index cadence, the scale rewriting stepwise, the ticks crossing per step, the glow on the landing frame;
  `overflow: "burst"` + `break_cadence` on the object); `ledger_page.py`; `test_breakthrough.py` (+2); the proof page's
  third row.
- Acceptance: the continuous burst is byte-identical with the option off; the stepped one lands on the same final
  frame; the operator reads both.
- Validate: as T10
- Evidence: `break_cadence: "stop"` on the object; the cadence on 1s at 24 fps (the tip travels 359 px/s, past stopaction's 250 rule; the frame index taken explicitly since the renderer runs 30 fps), the scale jumping per step, the ticks crossing per step, the glow full on the landing step; `test_breakthrough.py` (+2: the stepped V piecewise constant and monotone; the settled frame equal to the continuous mode's - the rendered PNGs hash equal, 39072a119f9140c3). The filmstrip: 6.43 / 6.48 two consecutive steps (22.7 -> 26.9 %), 6.73 the landing frame with the glow. R26-30 closed. Also in this commit: M26 (R26-40) - `probe.py` records `page.bars` (<= 197 bytes an instant), `gate_motion_density.py` M26 with VALUE_TOL 4 % + the burst's 5 % overshoot; Tokyo `[PASS ] M26 41 printed value(s) over 61 instants ... worst 2.9 % - May at 0:56`; R26-39's numbers as a fixture FAIL by name (303 px at "0.00 %").

### T14: The last drawing-kinetics law - the clothoid fitter for generated geometry (doc 42 §42.4)
- Status: complete (2026-09-11)
- Owner: `implementation_luna`
- Depends on: none (its first customers are T4's arrows and T5's arcs; the leaders of T10/T11 its third)
- Write set: `content/video_engine/scripts/kinetics/clothoid.mjs` (new: an Euler-spiral segment between two points with
  end tangents - `dk/ds = const`, Fresnel integrals by series, sampled to a polyline the stroke engine draws by length;
  a two-segment fit for an S-curve; G2 at the joins); the template's generated curves (the flow diagram's arrows, the
  map's arcs, the offset-annotation leaders) take it in place of cubic Beziers; `sync_kinetics.py` MODULES + the flags
  test; `tests/kinetics/clothoid.test.mjs` (curvature monotone along the segment; the tangents met; a Bezier of the
  same ends shows the parasitic inflection the doc names); CAPABILITIES row; doc 42's status line updated.
- Acceptance: an arrow drawn by the fitter has monotone curvature (measured on the samples) where the Bezier's ripples;
  hand-authored art untouched; goldens byte-identical (no golden carries a generated curve today).
- Validate: `node --test content/video_engine/tests/kinetics/clothoid.test.mjs`; `python -m pytest content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_kinetics_flags.py -q`
- Evidence: `kinetics/clothoid.mjs` (290) + `tests/kinetics/clothoid.test.mjs` (210): the segment with end tangents by the Fresnel series, the S-fit G2 at the join, the curvature monotone along the segment where the Bezier of the same ends inflects; its region in the template after `stroke`; the flow diagram's arrows are its first customer (the flow-swap golden). Doc 42 s42.4 carries the status line.

### T15: The continuity three - arriving from the edge, the three threads, the occlusion cue (HF-15, HF-16, HF-17)
- Status: complete (2026-09-11)
- Owner: parent (authoring + the frames); `junior_developer` for the compiler checks
- Depends on: T1
- Write set: HF-15 - a camera key law (E59 reason 2): the next region is visible at the frame edge BEFORE the move (a
  key's `look` must leave the target's box partly in frame at the key before it; `validate_camera` refuses a key whose
  target is wholly off-frame); HF-16 - the wire: one element carried across worlds (`extend` across a page boundary -
  the holdings baseline drawn on under the Meta bars; a `thread:` option naming the mark that survives the cut); HF-17
  - one foreground occluder on a world plate (a dock may declare `behind: <plate layer>` so the plate's foreground
  cutout paints over it: the depth cue by occlusion, not blur - judged by eye); tests; one Tokyo or tariff beat each.
- Acceptance: each of the three on one real beat, read in frames by the operator; the gate rows that read them.
- Validate: the camera, transitions and gate suites
- Evidence: HF-15: `camera_edge_errors` in `validate_camera` evaluates the previous key's frustum (the gate's M24 mirror of camera.mjs) and refuses a key whose target is wholly off-frame, naming the key's t and the distance; the vecmap IRN -> USA move passes at 1.35x (two thirds of the USA in frame) and is refused at 2.6x (`test_camera.py` +95). HF-16: `;thread=<mark key>` on the ARRIVING page's plate id (a species addresses one scene's states; the wire is a property of the page - "this page starts with that mark already on it" - and survives a cut, a mount or a spiral); the compiler checks the key against the page that hands it over; `species/thread.mjs` (70; 8 node tests to 1e-9) composes the two fits so the mark stands on the SAME stage pixels after the cut; E50's clock does not restart (the wire is the page's first mark, never its latest); golden `thread-baseline`. HF-17: `behind: "<layer>"` on the dock with the plate's fronts in a sidecar `<plate>.layers.json` (`{"foreground": {"desk": "...png"}}`) - the compiler refuses an undeclared layer or a missing file and embeds the PNG raw (the capped data_uri path drops the alpha); painted above the docks and below the species and caption layers; golden `occluder-dock`. The parent's run: sync 22 modules (12 + 10); node 215/215; 392 across page boxes, read->park, video dock, camera, transitions, goldens (byte-identical), sync, gate, portrait parity, species, lint, kit. The 6-up read by the parent. Open: the wire becomes visible when the chart layer does, not on the page's first cream frame (a doctrine call, R26-44); HF-17 is judged by eye on a real beat.

### T16: One placement truth (R26-22, R26-27)
- Status: complete (2026-09-11)
- Owner: `junior_developer`
- Depends on: none
- Write set: `build_scene_timeline_f.py` (`page_boxes` measured from the player's own layout once per aspect and
  written to a fixture the compiler reads, so `centred_place` and the player agree on a portrait page's bands - R26-27:
  y 536 vs 1250); a solo card centred by E50's clock instead of the reading rect over the title (R26-22: the read box
  from `_page_land_offset`); tests on both.
- Acceptance: a row that names no `centre_y` lands where the player draws the band; the Tokyo and tariff cuts are
  byte-identical (they name their centres).
- Validate: `python -m pytest content/video_engine/tests/test_dock_read_park.py content/video_engine/tests/test_video_dock.py -q` + the two builds' gates
- Evidence: `measure_page_boxes.py` (266) -> `assets/page-boxes.v1.json` (five builders x two aspects, keyed by the page's INK - `ledger_page.page_ink_key`: builder, title, sub / source first clause, rail count, ylabel, quiet zone - because a page's boxes are a pure function of its ink and a fixture keyed by builder alone would hand page B the boxes measured from page A); `page_boxes` reads a measured page and keeps the estimate for one not on file, the build saying so; the solo card auto-centres only on a MEASURED page (centring against an estimate is what put the tea cup on the chart); `tests/test_page_boxes.py` (204), `test_dock_read_park.py` (+36), `test_video_dock.py` (+49). The portrait dense-line page: the plot {215, 568, 607, 618} where the estimate said {230, 564, 580, 624}; the free band below the plot {80, 1186, 800, 44}; the story page's below-band y 1136 h 94 vs the estimate's y 1188 h 42; every 16:9 box 50-120 px off. The byte-identical proof on both shorts against the T0 baselines (the agent twice, the parent once on Tokyo): IDENTICAL on every artifact (GATES-MOTION differs by the new M25 / M26 rows only). Frames: the same row by the estimate (no band fits, the card covers the chart) and by the fixture (centred in the measured band, the chart readable). Open: the approved shorts' pages are not on file - measuring them moves four dock rectangles and flips two docks to E50-centred, a re-cut of approved work; the treemap squarifies into the plot it feeds (`--passes 2` converges it).

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
