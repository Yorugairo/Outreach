---
id: P52-THE-SWEEP
title: The sweep - the five unbuilt capabilities the operator ranked (the newsreel band and the surface above it, the cut's engine clock, the caption's one envelope, the melt exit, the last three Bravos species) and the thirteen backlog rows that clear the ground under them
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-12
updated: 2026-09-12 (approved by the operator the same day: "p52 approved."; running)
---

# The sweep

## Summary

The operator, 2026-09-12: *"/prp-plan to build the top 5 unbuilt capabilities + R26-8, R26-55, R26-56, R26-42, R26-4,
5, 6, 0 r26-13, r26-48, r26-3, r26-38, r26-41"*. The five were ranked for them that morning; the thirteen rows are read
verbatim off the backlog and cited, never re-derived.

**Recall** (the receipt, `docs/runbooks/RECALL-RECEIPT.md`):
- **The newsreel band.** `content/video_engine/remotion-ui/HARVEST-2026-09-07.md:289` RU-4 news-ticker-bar - the three
  mechanisms worth taking are the seam-free modulo wrap against a stable upper-bound width, the gradient dissolve at the
  crawl's right edge, and `holdSeconds` as a LIFE on a standing element;
  `docs/content-video-engine/REMOTION-UI-INTAKE-2026-09-07.md:48` (the chrome is broadcast-dark and off-brand - the
  mechanisms port, the look does not) and `:75` (*"RU-4 waits for a script that wants a crawl - and read a licence off
  the registry before any of this code is quoted"*). Our `ticker` is not a crawl:
  `content/video_engine/scripts/build_scene_timeline_f.py:276` *"STILL LIFE: a tape of figures ticks across a named
  region of an approved still"*. `docs_find "newsreel"` 0 hits (also 0 for lower third, chyron). The caption is already
  in that strip: `caption_band` / `stamp_caption_bands` (`build_scene_timeline_f.py:2623`, `:2691`, E62), `capBand` in
  the engine (`docs/content-video-engine/samples/scene-evidence-engine.mjs:8192`, `:8283`), the strip's own geometry
  `caption_strip_h` / `caption_home_y` (`:2587`, `:2609`).
- **TR-13.** `docs/content-video-engine/BACKLOG.md:477` (R26-9's row: TR-2 DONE 2026-09-06 measured the placement - the
  picture changes 3 frames before the next word's onset, dips centred on the onset -
  `docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md` §7, `docs/content-video-engine/46-REFERENCE-RHYTHM.md:181`
  §46.6; TR-13 is its engine form). The clock it must read exists:
  `content/video_engine/scripts/authoring/words.py` (`CUT_AT = 0.8` of the gap, `MIN_GAP = 0.30`, *"the take is the
  clock"*). WHICH transition it is was corrected 2026-09-12 and is not in scope: `scene_exit`
  (`build_scene_timeline_f.py:1108`) with `SIGNATURE_ENTERS` (`:97`), `DEFAULT_EXIT_CHANGE = "dip"` (`:131`).
- **The caption's one envelope.** `content/video_engine/hyperframes/HARVEST-2026-09-07.md:27` staggered-fade-up (each
  word a span; one timeline drives y 22 px -> 0, scale 0.92 -> 1, blur 5 px -> 0 together, stagger 0.055 s) - the
  operator: *"incorporating this might be a solution for how to get more caption motion without overcrowding"*. The
  caption block is `scene-evidence-engine.mjs:8200-8262` (`STAGE_POP_S`, `stagePop` / `springPop`, `MARK.RISE_PX`, the
  per-word boil); the mode is stamped by the compiler (`build_scene_timeline_f.py:3473` `cap_mode`, `:3531`
  `caption_modes`). E21 (captions ARE the motion) and M08 (`gate_motion_density.py:893`) are what it answers to.
- **The melt exit.** `content/video_engine/hyperframes/HARVEST-2026-09-07.md:37` morph-text (the gooey alpha threshold),
  with the chain already named there and on `BACKLOG.md:433` (R26-15): the area polygon -> blur + the K-M alpha
  threshold (`kinetics/ink.mjs:77` `kmFilterMarkup`) -> a blob on the stepped clock (`kinetics/stopaction.mjs:85`
  `stepped`) -> `throwXf` (`scene-evidence-engine.mjs:1336`) or the soak's splash (`ink.mjs:158` `soakStepped`);
  `kinetics/morph_a.mjs` is the outline morph. Exits are authored by name: `SCENE_EXITS`
  (`build_scene_timeline_f.py:73`), `LEDGER_EXITS` (`:64`), `TIMED_EXITS` (`:90`).
- **The last three Bravos species.** `docs/content-video-engine/EXPLORATION-REVIEW-2026-09-10.md:57` #5 (the dashed
  ellipse on the datum with a flag chip beside - PARTIAL: the ring exists under E56's one use, the form dial and the
  chip do not), `:58` #9 (the numbered agenda - ABSENT; *"`figure` + `note` could compose it"*), `:59` (7:43) (the
  isometric icon array - ABSENT; *"a `count-array` species: N icons on an isometric grid, arriving in reading order,
  the count as the claim"*). Where a species is declared: `SPECIES_KINDS` / `SPECIES_WHEN` / `PAGE_SPECIES`
  (`build_scene_timeline_f.py:183`, `:276`, `:232`); the module rule `sync_kinetics.py:24`; the registry
  `SPECIES_PAINTERS` (`scene-evidence-engine.mjs:6550`); the WHEN row
  `docs/content-video-engine/SPECIES-BY-SENTENCE.md:1` (P50 T1, the ten acts).
- **The thirteen rows, each read on its own line:** `BACKLOG.md:429` R26-8 (the publish package + the one 1440x2560
  master - the render already makes that size, `scripts/render_episode.py:89`), `:432` R26-13 (M18 per layer), `:441`
  R26-37 + `:442` R26-38 (the probes answer for the FIRST ledger world; `__lpProbe`
  `scene-evidence-engine.mjs:8437`), `:445` R26-41 (one painter registry for PAGE species too; `paintSpan`
  `scene-evidence-engine.mjs:5377`, the space note at `:536`), `:446` R26-42 (`pillAt`
  `content/video_engine/scripts/species/tippill.mjs:66`), `:452` R26-48 (the sub-pixel text class; the bed
  `determinism_check.py build-short-t0 --all` = 26 ok / 34 mismatch / 1 known), `:459` R26-55 (`press_card.py`,
  `species/press.mjs:134` `pressTypeScale`, E66 `docs/portable/OPERATOR-RULINGS.md:2140`), `:460` R26-56 (the stale
  `treemap-cross` golden source; `content/video_engine/tests/golden/build_golden_sources.py:804` SURFACES), `:480`
  R26-4 (`docs/content-video-engine/51-THE-SHORTS-FORMAT.md:24` §51.2, S02 at `gate_opening_structure.py:392`), `:481`
  R26-5 (`tokyo-tea-break/sound/SOUND-PLAN.json`), `:482` R26-6, `:483` R26-0 (`viewer_windows.py` has NO screen
  fold-in today - 0 hits for "screen" in it; `viewer_score.py:239` V01), `:486` R26-3 (the A/B is the open half of the
  row; the fitter shipped as P50 T14).
- **The first customer.** `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/` (the next
  episode, Gemini's bundle): `assets/evidence_clips/` five broadcast clips (Bloomberg x2, CNBC x2, Fox Business) and
  `assets/heads/` six head cutouts (Volcker, Greenspan, Powell, Bessent, Warsh, Cabana) - the operator ruled the heads
  usable. `grep -i "newsreel|ticker|headline|crawl"` across its SCREENS / CHOREOGRAPHY / PRODUCTION: 0 hits. **The band
  has no script line yet: T6 writes the line with the operator before it writes the module.**
- **The lane that is moving under us.** The chart inks are being changed right now (E67: the electric-field palette and
  the line bloom) in `scene-evidence-engine.mjs:4209` (`PAL`), `:4281` (the sign fallback to `var(--lp-neg)` /
  `var(--lp-pos)`), `:4377` (`LP_PAL`) and the shell's token block
  (`docs/content-video-engine/samples/scene-evidence-player.template.html:50`). No slice here writes those four places;
  T17 (the race, `buildLedgerRace` at `scene-evidence-engine.mjs:4478`) is the nearest neighbour and waits for them.

**What shapes the order.** Four rows are the ground everything else stands on: a golden two agents reverted rather than
ship (R26-56) means nobody trusts the harness; a probe that answers for the wrong world (R26-37/38) means nobody trusts
the eyes; 34 reproducible warm/cold mismatches (R26-48) mean nobody trusts a frame hash; and until the painter registry
is keyed by space (R26-41) every new species is half a module. Those four first, then the registry, then the species
that should be built ON it.

## Intent And Acceptance

Intent: (a) five mechanisms shipped as modules with goldens and a frame the operator reads - a newsreel band with a
docked surface above it, the cut placed by the take's own word clock, a caption arrival that is one envelope, a page
that melts and is thrown, and the three Bravos species that close `EXPLORATION-REVIEW-2026-09-10.md` §2; (b) the
thirteen rows closed or re-pointed in the commit that makes them true; (c) nothing already approved moves without the
operator's word.

Acceptance:
- Every existing golden byte-identical unless the slice says which one moves and why (T1 is the one slice whose whole
  job is to move one on purpose; T18 moves `press-stack`). `test_golden_frames.py`, `test_portrait_parity.py`,
  `test_kinetics_sync.py`, `test_kinetics_flags.py` green on every slice.
- `python content/video_engine/scripts/determinism_check.py <build> --all` reports **0 mismatch of the R26-48 class**
  (from 34) after T4, and stays 0 after every later slice.
- Each new species is a module under `content/video_engine/scripts/species/` with a node test under
  `content/video_engine/tests/kinetics/`, a `SPECIES_WHEN` line, a row in `SPECIES-BY-SENTENCE.md`, a golden surface
  and a `CAPABILITIES.md` row - and passes the life check on its own region (E56 §3: 0 identical 0.25 s pairs).
- The two approved shorts (`tokyo-tea-break`, `japan-tariff-trick`) rebuild byte-identical on every slice, or the diff
  is named in the slice's Evidence and approved. Tokyo is the test bed only: no Tokyo render in this plan.
- Every commit that builds a mechanism carries `Recall: path:line` lines (`scripts/hooks/recall_receipt.py`).

## Scope

- Species modules and their goldens: `content/video_engine/scripts/species/`, `content/video_engine/tests/kinetics/`,
  `content/video_engine/tests/golden/{sources,frames}` through `build_golden_sources.py` + `render_baseline.py`.
- The compiler (`build_scene_timeline_f.py`): the species and exit registries, the caption fields, the cut clock, the
  dock fields. The authoring kit (`content/video_engine/scripts/authoring/words.py`) for the placement law.
- The engine (`scene-evidence-engine.mjs`) at four places only: the painter registries (T5), the caption block (T10),
  the probes (T3), the page text rule (T4). The shell (`scene-evidence-player.template.html`) for the `?layers=`
  switch (T15) and the text rule (T4).
- Gates: `gate_motion_density.py` (the new kinds' events, the sound row, the mount row, M18 per layer),
  `gate_opening_structure.py` (S02), `gate_ring_mechanism.py` (the ring's form dial),
  `measure_frozen_frames.py`, the viewer (`viewer_windows.py`, `viewer_score.py`).
- Docs: `BACKLOG.md` rows, `CAPABILITIES.md` rows, `SPECIES-BY-SENTENCE.md`, `51-THE-SHORTS-FORMAT.md` §51.2,
  `46-REFERENCE-RHYTHM.md` §46.6, `PIPELINE.md` stage 8, `docs/GATES-REGISTRY.md` through its builder, and the
  `script-writer` skill's `references/SHORTS-SHAPE.md`.
- One publish package (`publish/` under a short's build) and its checklist.

## Not Building

- The chart ink tables (E67's lane): `scene-evidence-engine.mjs:4209`, `:4281`, `:4377`, the shell's `:50`. Named as a
  dependency, never written here.
- A broadcast look. The band takes RU-4's three mechanisms on our tokens (cream / charcoal / coral / sunflower); the
  dark chrome, the flag block and the Inter font stay out, and no registry code is quoted before a licence is read
  (`REMOTION-UI-INTAKE-2026-09-07.md:75`).
- A re-cut of approved work. TR-13 does not move a cut in the two shipped shorts (T11), and R26-5's gain change is
  measured on the plan, not by a re-render.
- A new transition VOCABULARY. TR-13 changes WHEN a transition lands, never WHICH one (E47 as corrected 2026-09-12).
- The melt as a default: an authored exit, one page, one beat, behind the operator's eye.
- A second caption mode. The stagger is an ARRIVAL on the existing stage caption, default off; the boil is untouched.
- A face decision for the press card (R26-55): the display face that stands in for a masthead is the operator's call
  (gate 7), not the implementer's.
- Scheduling or API posting (R26-8's own row draws that line), a second render size, any paid audio or cloud STT.
- The remaining page species' moves (bracket, figure, spread): T5 opens the registry and names them; moving them is a
  later plan.

## Human Gates

1. **The band's first frame** (T6): the operator reads one frame of the newsreel band with a head cutout docked above
   it and rules the strip law - does the caption take the E62 band ABOVE the crawl, or does the band yield the strip?
   The module is not written until the script line and this answer exist.
2. **The melt on a page** (T9): the operator's eye on the chain at four instants (the polygon, the threshold, the blob
   on 2s, the throw or splash) before it is offered to any cut.
3. **The three species on a proof page** (T7, T8): the count array, the numbered agenda and the ring's dashed-ellipse
   form with its flag chip, read as frames on one clock, then in motion.
4. **The caption stagger by eye** (T10): a private Tokyo build (`TOKYO_BUILD_DIR=build-short-t10`), the pop and the
   stagger side by side at the same instants. Never a render.
5. **The race A/B verdict** (T17): the operator's ear and eye decide whether the race adopts the clothoid, after the
   measurement says whether the choppiness is curvature or timing.
6. **The publish package's first use** (T16) on the next short: is the folder what a posting pass actually needs?
7. **The press card's stand-in display face** (T18).
8. Push authorization per commit, as standing.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (dispatch mapping, lane write sets, the return contract),
  `docs/runbooks/RECALL-RECEIPT.md`.
- `docs/content-video-engine/BACKLOG.md` rows R26-0, 3, 4, 5, 6, 8, 9, 13, 15, 37, 38, 41, 42, 48, 55, 56 - the row IS
  the mechanism; cite it, do not restate it.
- `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (which species on which sentence; every new species adds a row),
  `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.27 (the targeting law) and §9.28 (the surface
  grammar), `docs/content-video-engine/46-REFERENCE-RHYTHM.md` §46.5-46.6.
- `docs/portable/OPERATOR-RULINGS.md` E21, E25, E45, E47 (as corrected 2026-09-12), E49, E50, E56, E58, E62, E66.
- `content/video_engine/scripts/sync_kinetics.py` (the module rule, the one name space, `--check`),
  `content/video_engine/scripts/render_baseline.py` (`FLAG_FRAMES`, the SINGLE / SPLIT forms, `write_split`),
  `content/video_engine/tests/golden/build_golden_sources.py` (`SURFACES`).
- `.claude/PRPs/plans/P50-BRAVOS-GRAMMAR.plan.md` (the species module rule, T1's map, T14's fitter) and
  `P51-THE-ANIMATORS-LOOP.plan.md` (T1 the split, T2 the probe, T3 the self-watch, T5 the sidecar).

## Execution Path

1. **The ground, in parallel** (disjoint write sets): T1 the golden nobody trusts, T2 the leader behind its pill, T3
   the probes' active world, T4 the sub-pixel text class. T4 gates everything that later claims a frame hash.
2. **T5 the registry keyed by space** (parent): the newsreel and the three species are built ON it, so it lands before
   them and after T3 (both touch the engine's paint layers).
3. **The species, one owner each, after T5**: T6 the newsreel band and the surface above it (gate 1 first), T7 the
   count array, T8 the agenda plus the ring form and its chip, T9 the melt exit (parent; it chains four owned laws).
4. **T10 the caption envelope** - independent of the species; the engine's caption block is its own region.
5. **T11 TR-13** (parent; the compiler's clock, the one slice that can move a cut).
6. **The rows that ride the gates and the docs**: T12 R26-4, T13 R26-5 + R26-6, T14 R26-0, T15 R26-13.
7. **T16 the publish package**, then **T17 the race A/B** (after E67's ink lane lands - it reads the same builder's
   neighbourhood), then **T18 R26-55** last: it needs gate 7.
8. Every slice: `sync_kinetics.py --check`, the golden suite, the two shorts' builds diffed, the commit's recall lines.

## Patterns To Mirror

- A species is a MODULE (`sync_kinetics.py:24`): pure math plus a painter, registering itself as its last statement, a
  node test beside it, nothing written into the engine's body. `species/chip.mjs` + `tests/kinetics/chip.test.mjs` is
  the reference pair; `species/flow.mjs` is the reference for generated geometry on the clothoid fitter.
- A page species today is a module with a thin call (`paintSpan`, `scene-evidence-engine.mjs:5377`) - T5 is what
  removes the thinness.
- A dock kind, not a species, when the thing is a card: `DOCK_KIND_PRESS` (`build_scene_timeline_f.py:131`) and
  `DOCK_OPTS` (`:85`) are the shape T6's surface-above uses.
- A golden surface is a source plus a frame through `SURFACES` and the two `render_baseline` forms; a flag golden
  proves a difference (`FLAG_FRAMES`).
- A gate row cites its ruling and names its tests - the rows in `docs/GATES-REGISTRY.md` (M18 at `:130`, M25 at `:137`)
  are the form.
- A measurement before an adoption (R26-3's own words): `measure_cut_offsets.py`, `measure_motion_energy.py`,
  `determinism_check.py` are the house instruments.

## Task Slices

### T1: The treemap golden, regenerated on purpose (R26-56)
- Status: complete (2026-09-12, 5c076e0)
- Owner: `junior_developer`
- Depends on: none
- Write set: `content/video_engine/tests/golden/sources/treemap-cross.timeline.json`,
  `content/video_engine/tests/golden/frames/treemap-cross.png`, `docs/content-video-engine/BACKLOG.md` (R26-56 at
  `:460`).
- Acceptance: the commit names WHICH change moved the cells (the row's candidate is the E65 page-boxes re-measure,
  207b00c - shown by regenerating against that commit's fixture and against HEAD) and regenerates the source and the
  frame with that reason in the message; `h_px` in the committed source equals what `build_golden_sources.py` writes
  today (329.6 vs the committed 284.3 is the delta to explain); no other golden source appears in the diff.
- Validate: `python content/video_engine/tests/golden/build_golden_sources.py` then `python -m pytest
  content/video_engine/tests/test_golden_frames.py -q`
- Evidence: the cause proven against six fixture versions (3eba5de the measured page-boxes fixture, not E65: `T1-REPORT.md` in the session scratchpad carries the table); one source and one frame moved; test_golden_frames 28 passed; the frame re-rendered against the committed engine matches (sha 06944a98463ee702). Follow-up named on the row: the player-sha check of test_page_boxes fails against the working tree.

### T2: The tip pill's leader ends on the pill's near edge (R26-42)
- Status: complete (2026-09-12, 4f698cd; the parent built it after the speedster returned no change)
- Owner: `speedster`
- Depends on: none
- Write set: `content/video_engine/scripts/species/tippill.mjs` (`pillAt` at `:66` takes the pill's BOX, not its
  horizontal span), `content/video_engine/tests/kinetics/tippill.test.mjs`.
- Acceptance: for an end-anchored tag the leader's terminus lies ON the capsule's boundary and never inside it, at both
  anchor ends and in both aspects (the node test asserts the terminus against the box, not the span); every golden
  byte-identical; `BACKLOG.md:446` closed.
- Validate: `node --test content/video_engine/tests/kinetics/tippill.test.mjs`; `python -m pytest
  content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q`
- Evidence: `leaderEnd` + `pillAt(box)` in the module, `P.boxRel` at the engine's call site, the region synced; node 11 passed; sync in sync (23); goldens: 19 plain surfaces byte-identical with the HEAD template + this engine (`p52/attrib/t2-attrib-rest.txt`; the flag variants are settled frames of the same pages), the live template's moves being T4's rule.

### T3: The probes answer for the ACTIVE world, and reset on a backward seek (R26-37, R26-38)
- Status: complete (2026-09-12, 8186f1a)
- Owner: `implementation_luna`
- Depends on: none
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`window.__lpProbe` at `:8437` and its
  siblings `__camera` / `__lpDatum`: `[wA, wB].find(ledger)` becomes the ACTIVE world, and the `__lp` bookkeeping is
  cleared when the seek runs backwards), `content/video_engine/scripts/probe.py` (the work-around removed, the DOM read
  kept), `content/video_engine/tests/test_probe.py`.
- Acceptance: under a mount where both worlds hold a page (Tokyo 0:58 and 0:81 on a private build) the probe names the
  page on TOP; `test_probe.py::test_a_seek_is_the_play_for_the_probe_too` passes with the work-around gone; every
  rendered frame byte-identical (the player was never wrong - only the bookkeeping); `BACKLOG.md:441` and `:442`
  closed.
- Validate: `python -m pytest content/video_engine/tests/test_probe.py content/video_engine/tests/test_golden_frames.py
  content/video_engine/tests/test_self_watch.py -q`
- Evidence: `[wB, wA]` at the three probes, `__lp` re-pointed every painted frame, `scene` / `world` on the probe; probe.py's work-around gone; test_probe 11 (the new test cannot pass on HEAD's engine); eight Tokyo frames and two goldens byte-identical against the HEAD engine; `T3-REPORT.md` in the session scratchpad carries the before/after probe reads.

### T4: The sub-pixel text class - warm and cold agree (R26-48)
- Status: complete (2026-09-12, 81ccef9)
- Owner: `implementation_luna` (the fix); parent (the verdict on which cure)
- Depends on: none
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html` (the text-rendering rule on the
  page's SVG text classes) and/or `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the label y snapped to
  an integer where the page writes it), `content/video_engine/tests/test_render_determinism.py`,
  `docs/content-video-engine/BACKLOG.md` (R26-48 at `:452`).
- Acceptance: `determinism_check.py <build> --all` on a private Tokyo build reports 0 mismatch of this class (from 34)
  with the 1 known left; the cure is the cheapest one that works, tried in the row's own order
  (`text-rendering: geometricPrecision` plus an integer-snapped y first; labels on a canvas the engine owns only if
  that fails); goldens byte-identical, or the moved goldens regenerated in the same commit with the ink-box delta
  printed per surface.
- Validate: `python content/video_engine/scripts/determinism_check.py
  content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short-t4 --all`; `python -m pytest
  content/video_engine/tests/test_render_determinism.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: cure 1 alone (the row's order honoured; cure 2 measurably unavailable, cure 3 not built); the per-element diff and the pixel attribution in `build-short-t4/determinism/` (ink_diff.py, px_diff.py, the frame pairs); 38 -> 7 mismatch with the seven named; 11 goldens regenerated on purpose (the table in the commit); test_render_determinism 5 (RED/GREEN proved); two rows opened: R26-57 (stage-space text), R26-58 (the thrown dock at 75.79).

### T5: One painter registry, keyed by space (R26-41)
- Status: complete (2026-09-12, c115f81)
- Owner: parent (architecture); `implementation_luna` for the mechanical moves under the parent's contract
- Depends on: T3
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`SPECIES_PAINTERS` at `:6550` becomes two
  registries keyed by space - `stage` (the px overlay, `resolveTarget`, the scene clock) and `page` (the chart's
  viewBox, the page state, the active park transform, per the note at `:536`); `paintSpan` at `:5377` becomes a
  registered page painter instead of a thin call), `content/video_engine/scripts/sync_kinetics.py` (a species module
  declares its space), `content/video_engine/scripts/species/span.mjs` (the first page species registered end to end),
  `content/video_engine/tests/test_kinetics_sync.py`, `docs/content-video-engine/BACKLOG.md` (R26-41 at `:445`).
- Acceptance: `span` paints with no code in the engine's perform layer beyond the registry hook; a module that declares
  the wrong space fails `sync_kinetics --check` with a message naming the space; every golden byte-identical
  (`span-decade` especially); `bracket`, `figure` and `spread` are named as the next page species to move, with the
  hook in place and their moves explicitly NOT in this slice.
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`; `python -m pytest
  content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_golden_frames.py
  content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_portrait_parity.py -q`
- Evidence: the registry, the ctx, the hook, span's painter moved, the SPACE rule (RED/GREEN by flipping span's line); 63 pytest + 233 node; 25/25 goldens byte-identical with the HEAD template and this engine (`p52/t5-golden-table.txt`); bracket / figure / spread named at the hook, not moved.

### T6: The newsreel band, and the surface above it
- Status: pending
- Owner: parent (the strip law and the script line - gate 1); `implementation_luna` for the module
- Depends on: T5; human gate 1
- Write set: `content/video_engine/scripts/species/newsreel.mjs` (new: a stage-space band - the seam-free modulo wrap
  against a stable upper-bound width, the gradient dissolve at the crawl's right edge, `hold` as a life, per
  `remotion-ui/HARVEST-2026-09-07.md:289`; the strapline and dateline in our type),
  `content/video_engine/tests/kinetics/newsreel.test.mjs` (new),
  `content/video_engine/scripts/build_scene_timeline_f.py` (`SPECIES_KINDS` at `:183`, `SPECIES_WHEN` at `:276`, the
  target table at `:479`, `validate_species`; the band against `caption_band` at `:2623` and `stamp_caption_bands` at
  `:2691`), `content/video_engine/scripts/gate_motion_density.py` (a crawl is a standing element with a life, not an
  event per frame), `content/video_engine/tests/test_targeted_species.py`,
  `content/video_engine/tests/golden/build_golden_sources.py` plus the `newsreel-band` source and frame,
  `docs/content-video-engine/SPECIES-BY-SENTENCE.md`, `docs/content-video-engine/CAPABILITIES.md`, the episode's
  script line under `content/video_engine/projects/systems-and-blowups/myth-of-historical-normal/`.
- Acceptance: the band runs UNDER a surface the row docks - a head cutout from `myth-of-historical-normal/assets/heads/`,
  a clip from `assets/evidence_clips/` on E45's springs, or the plate itself - and never fills the frame with text; on
  9:16 the caption takes its E62 band above the crawl and the compiler REFUSES a row where the two want the same strip,
  naming both boxes; the crawl is a pure function of t (two renders of one second identical; the wrap seamless across
  the modulo); the life check passes on the band's own region; goldens byte-identical without it.
- Validate: `node --test content/video_engine/tests/kinetics/newsreel.test.mjs`; `python -m pytest
  content/video_engine/tests/test_targeted_species.py content/video_engine/tests/test_caption_band.py
  content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_portrait_parity.py -q`
- Evidence: pending

### T7: The isometric count array
- Status: pending
- Owner: `implementation_luna`
- Depends on: T5
- Write set: `content/video_engine/scripts/species/countarray.mjs` (new: N identical icons on an isometric grid,
  arriving in reading order on their words, the count as the claim; glyphs from
  `content/video_engine/assets/icons/` under rule A2a), `content/video_engine/tests/kinetics/countarray.test.mjs`
  (new), `content/video_engine/scripts/build_scene_timeline_f.py` (the kind, its `when`, its validation - a count with
  no number in the sentence is refused), `content/video_engine/scripts/gate_motion_density.py`,
  `content/video_engine/tests/test_targeted_species.py`, the `count-array` source and frame through
  `content/video_engine/tests/golden/build_golden_sources.py`, `docs/content-video-engine/SPECIES-BY-SENTENCE.md`,
  `docs/content-video-engine/CAPABILITIES.md`.
- Acceptance: `EXPLORATION-REVIEW-2026-09-10.md:59` satisfied - the array arrives in reading order, the count is
  printed, the grid is isometric with no perspective cheat, nothing spins; the life check passes on the finished
  field; goldens byte-identical without it; gate 3 read on the proof page.
- Validate: `node --test content/video_engine/tests/kinetics/countarray.test.mjs`; `python -m pytest
  content/video_engine/tests/test_targeted_species.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T8: The numbered agenda, and the ring's dashed-ellipse form with its flag chip
- Status: pending
- Owner: `implementation_luna`
- Depends on: T5, T7 (the chip placement math the flag chip reuses)
- Write set: `content/video_engine/scripts/species/agenda.mjs` (new: numbered rows revealed on their own words -
  `EXPLORATION-REVIEW-2026-09-10.md:58` says `figure` plus `note` could compose it; the module is what makes it one
  declaration), `content/video_engine/scripts/species/ring.mjs` (new: the form dial - a dashed ellipse beside the
  circle - and the optional flag chip, `EXPLORATION-REVIEW-2026-09-10.md:57`),
  `content/video_engine/tests/kinetics/agenda.test.mjs` and `ring.test.mjs` (new),
  `content/video_engine/scripts/build_scene_timeline_f.py` (the kinds, the `when` lines, the E56 compiler gate
  unchanged in scope), `content/video_engine/scripts/gate_ring_mechanism.py`,
  `content/video_engine/tests/test_gate_ring_mechanism.py`, `content/video_engine/tests/test_targeted_species.py`, the
  `agenda-two` and `ring-dashed-chip` goldens, `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (the SETS an agenda
  row and the TURNS on a number row), `docs/content-video-engine/CAPABILITIES.md`.
- Acceptance: an agenda of two or three rows reveals one row per word and holds with a named idle; the ring takes
  `form: dashed` and an optional flag chip WITHOUT widening E56 (the gate still FAILs a ring on a picture and a ring
  that circles neither a number nor a chart point); goldens byte-identical without them; gate 3 read on the proof page.
- Validate: `node --test content/video_engine/tests/kinetics/agenda.test.mjs`; `node --test
  content/video_engine/tests/kinetics/ring.test.mjs`; `python -m pytest
  content/video_engine/tests/test_gate_ring_mechanism.py content/video_engine/tests/test_targeted_species.py
  content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T9: The melt exit - the page melts, balls up on 2s, and is thrown or splashed
- Status: pending
- Owner: parent (the chain crosses four owned laws); `implementation_luna` for the module under the parent's contract
- Depends on: T5; human gate 2
- Write set: `content/video_engine/scripts/species/melt.mjs` (new: the area polygon -> blur plus the K-M alpha
  threshold (`kinetics/ink.mjs:77`) -> a blob on the stepped clock (`kinetics/stopaction.mjs:85`) -> `throwXf` or
  `soakStepped`'s splash; the outline from `kinetics/morph_a.mjs`),
  `content/video_engine/tests/kinetics/melt.test.mjs` (new),
  `content/video_engine/scripts/build_scene_timeline_f.py` (`melt` as an AUTHORED exit - the slice's first act is to
  say which registry owns it, `SCENE_EXITS` at `:73` or `LEDGER_EXITS` at `:64`, and to give it seconds in
  `TIMED_EXITS` at `:90`), `content/video_engine/tests/test_transitions_e47.py`,
  `content/video_engine/scripts/gate_motion_density.py` (a melt is ONE world change, not four events), the `melt-page`
  golden, `docs/content-video-engine/BACKLOG.md` (R26-15's melt lesson at `:433`),
  `docs/content-video-engine/CAPABILITIES.md`.
- Acceptance: `exit=melt` on a real ledger page runs the whole chain as a pure function of t (the four instants render
  identically twice); the default exit table is untouched (E47 as corrected 2026-09-12 - a melt is authored by name,
  never mechanical) and a line still leaves by length (E50) when no melt is named; gate 2 passed on the four frames.
- Validate: `node --test content/video_engine/tests/kinetics/melt.test.mjs`; `python -m pytest
  content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_golden_frames.py
  content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: pending

### T10: The caption's arrival as one stagger envelope
- Status: pending
- Owner: `implementation_luna`; parent for the eye (gate 4)
- Depends on: T4 (a frame hash must mean something before an arrival is judged by one)
- Write set: `content/video_engine/scripts/kinetics/stagger.mjs` (new: one envelope with per-word offsets - y 22 px ->
  0, scale 0.92 -> 1, blur 5 px -> 0, stagger 0.055 s, all `[DERIVED: HyperFrames staggered-fade-up]`),
  `content/video_engine/tests/kinetics/stagger.test.mjs` (new),
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the caption block at `:8200-8262` ONLY: a `fade_up`
  arrival beside the pop; the boil unchanged), `content/video_engine/scripts/build_scene_timeline_f.py` (a
  `cap_arrive` field stamped beside `cap_mode` at `:3473` and declared with `caption_modes` at `:3531`, defaulting to
  the pop), `content/video_engine/tests/test_caption_arrive.py` (new),
  `content/video_engine/scripts/gate_motion_density.py` (M08 at `:893` reads the envelope as caption motion),
  `docs/content-video-engine/CAPABILITIES.md`.
- Acceptance: with `cap_arrive` absent every golden and both shorts are byte-identical (the default is today's pop);
  with `fade_up` the words arrive on one envelope with per-word offsets, M08 still PASSes, the life check holds, and
  two renders of one second are identical; the blur is a filter on the word span, never on the strip; the kill-switch
  flag names in `test_kinetics_flags.py` are unchanged.
- Validate: `node --test content/video_engine/tests/kinetics/stagger.test.mjs`; `python -m pytest
  content/video_engine/tests/test_caption_arrive.py content/video_engine/tests/test_caption_band.py
  content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_flags.py -q`
- Evidence: pending

### T11: TR-13 - the cut is placed by the take's word clock
- Status: complete (2026-09-12, 35d0cec)
- Owner: parent (the compiler's clock)
- Depends on: T3
- Write set: `content/video_engine/scripts/authoring/words.py` (the placement beside `CUT_AT` and `MIN_GAP`: a cut lands
  at the next word's onset minus 3 frames; a dip's black is centred ON the onset - `BACKLOG.md:477`, doc 46 §46.6 at
  `46-REFERENCE-RHYTHM.md:181`), `content/video_engine/scripts/build_scene_timeline_f.py` (the dip's phase, so its
  black falls on the onset and not at the boundary), `content/video_engine/tests/test_authoring_kit.py`,
  `content/video_engine/tests/test_transitions_e47.py`, `content/video_engine/scripts/measure_cut_offsets.py` (the
  verdict on OUR build, not only the reference), `docs/content-video-engine/46-REFERENCE-RHYTHM.md` §46.6 (the engine
  form recorded), `docs/content-video-engine/BACKLOG.md` (TR-13 on the R26-9 row at `:477`).
- Acceptance: on a build with measured word times (`--timeline`) every mechanical cut sits within one frame of onset
  minus 3 frames and every dip's black midpoint within one frame of the onset, measured by `measure_cut_offsets.py` on
  our own timeline; WHICH transition a boundary takes is unchanged (`scene_exit` at `:1108` untouched); **the two
  approved shorts do not move** - they keep the 0.8-of-the-gap placement under a pin this slice adds and names, so both
  rebuild byte-identical; a build with estimated times only says so and keeps the old rule.
- Validate: `python -m pytest content/video_engine/tests/test_authoring_kit.py
  content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_measure_cut_offsets.py -q`; both
  shorts rebuilt into private dirs and diffed against their pre-slice artifacts
- Evidence: `CUT_LEAD_S` / `CUT_RULES` / `cut_before(rule, exit)` in words.py; the pins in both build files; `--scenes` + `tr13_rows` in measure_cut_offsets.py; doc 46 s46.6's engine-form paragraph; 48 kit + offsets tests. Deviation: no compiler change - the engine already centres the dip's black on the boundary, so the boundary on the onset IS the rule. Proof: both shorts rebuilt into build-short-t11, every span / species / dock clock identical to the frozen copies (Tokyo vs build-short-t0 - only s05's exit differs, E47's corrected default; Japan vs build-short). Verdict on the approved builds recorded in the commit (Tokyo 2/5 within a frame; Japan's dips 100-110 ms early).

### T12: The chart on the hook (R26-4)
- Status: complete (2026-09-12, 2e6740d)
- Owner: parent (doctrine plus the gate condition)
- Depends on: none
- Write set: `docs/content-video-engine/51-THE-SHORTS-FORMAT.md` §51.2 (at `:24`: hook 0:00-0:03 -> the first ledger
  page rolls out under sentence two -> the mechanism ON the page by 0:10 -> the host after or over it),
  `C:/Users/Snipe/.claude/skills/script-writer/references/SHORTS-SHAPE.md` (the same shape for the author),
  `content/video_engine/scripts/gate_opening_structure.py` (S02 at `:392` accepts a ledger page as the mechanism
  surface), `content/video_engine/tests/test_gate_opening_structure.py`, `docs/content-video-engine/BACKLOG.md` (R26-4
  at `:480`).
- Acceptance: S02 PASSes on a short whose mechanism lands as a page by 0:10 and still FAILs when the mechanism sentence
  is undeclared or late; the doc, the skill and the gate say one thing; any change to the two shipped shorts' gate
  reports is named in the Evidence.
- Validate: `python -m pytest content/video_engine/tests/test_gate_opening_structure.py -q`; `python
  content/video_engine/scripts/gate_opening_structure.py` on both shorts' scripts; `python
  content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: `load_pages` / `find_scene_timeline` / `--scenes` on the gate and the runner; S02's four cases pinned in test_gate_opening_structure (22 passed); doc 51 s51.2 + SHORTS-SHAPE.md; both shorts: S02 PASS unmoved, first_page 1.99 s / 1.82 s; their stored gate reports untouched.

### T13: The cut's sound, and a returning character mounts (R26-5, R26-6)
- Status: complete (2026-09-12, d16155e)
- Owner: `junior_developer`
- Depends on: none
- Write set: `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/sound/SOUND-PLAN.json` (the transient
  gain 0.16 -> 0.08 `[DERIVED: from the 2026-09-05 metering, halved]` - read the plan's own note first: the V2 cut
  already dropped `press 3`), `content/video_engine/scripts/gate_motion_density.py` (two rows: no transient cue inside
  0:05-0:12 unless a page lands with it, `BACKLOG.md:481`; a `cut` exit into a scene whose first species is a character
  already seen FAILs, `:482`), `content/video_engine/tests/test_gate_motion_density.py`,
  `content/video_engine/tests/test_sound_design.py`, `docs/GATES-REGISTRY.md` through
  `content/video_engine/scripts/build_gates_registry.py`, `docs/content-video-engine/BACKLOG.md` (`:481`, `:482`).
- Acceptance: each row FAILs on a fixture that breaks it and PASSes on one that does not; Tokyo's report shows the
  sound row's verdict under the new gain with no re-render (the plan is data; the render is out of scope); each
  registry entry names its ruling and its tests.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py
  content/video_engine/tests/test_sound_design.py content/video_engine/tests/test_motion_gate_wiring.py -q`; `python
  content/video_engine/scripts/build_gates_registry.py --check`
- Evidence: M29 + M30 (`_drop_window_sound_gate`, `_mount_gate`, `_page_landings`), 7 new tests (102 passed), registry in sync (144 records; carries T12's S02 too); `transient_gain` 0.08 on the plan + `PRESS_GAIN` 0.08; Tokyo read-only: M29 FAIL at 9.51 s (the card throw), M30 no row (no cast declared). Open: a dock landing as licence (the operator); the next short declares its cast.

### T14: The short's viewer sees the screens (R26-0)
- Status: complete (2026-09-12, 45f17c2)
- Owner: `junior_developer`
- Depends on: none
- Write set: `content/video_engine/scripts/viewer_windows.py` (a `[screen]` line per named screen folded into each
  window's text from the SCREENS file - there is no screen fold-in today),
  `content/video_engine/scripts/viewer_score.py` (V01 at `:239` counts a chart-carried beat as perceived when the
  reader names the screen's figure), the prompt the runner sends,
  `content/video_engine/tests/test_viewer_windows.py`, `content/video_engine/tests/test_viewer_score.py`,
  `docs/content-video-engine/BACKLOG.md` (R26-0 at `:483`).
- Acceptance: a window carrying a chart shows its title and the figures it displays and NO doctrine (the tags are still
  stripped - P36's "Not Building" holds); Tokyo's windows regenerate with `[screen]` lines at the beats E43 named
  (0:30-0:45) and V01's verdict on the stored reports changes only where a figure was carried by a chart; no model is
  called by the tests.
- Validate: `python -m pytest content/video_engine/tests/test_viewer_windows.py
  content/video_engine/tests/test_viewer_score.py -q`; `python content/video_engine/scripts/viewer_windows.py
  content/video_engine/projects/systems-and-blowups/tokyo-tea-break/SCRIPT-90S-VO.txt --timeline <private build>`
- Evidence: Deviation: screens read off the scene timeline, not `-SCREENS.md` (doctrine, no chart). 54 viewer tests; Tokyo's .claude windows regenerated (words byte-identical, 6/6 with screens); stored reports re-scored 21/24 -> 23/24, the re-scored report committed beside the stored one as `SCRIPT-90S.claude-VIEWER.after-screens.md`; no model called.

### T15: M18 per layer (R26-13)
- Status: pending
- Owner: `implementation_luna`
- Depends on: T3
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html` (a `?layers=` switch on the shell
  - the runtime is a module since P51 T1, so the shell can hide the caption and dock layers before a capture),
  `content/video_engine/scripts/measure_frozen_frames.py` (a `--layers` option; one loop per layer),
  `content/video_engine/scripts/gate_motion_density.py` (M18 at `:1187` reads page, docks and captions each on their
  own), `content/video_engine/tests/test_gate_motion_density.py`, `content/video_engine/tests/test_idle_e49.py`,
  `docs/GATES-REGISTRY.md` through its builder, `docs/content-video-engine/BACKLOG.md` (R26-13 at `:432`).
- Acceptance: on a fixture where a caption boils over a frozen page, M18 WARNs on the PAGE layer while the whole-frame
  hash passes - the defect the row was written for (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still);
  the whole-frame verdict is still reported; goldens byte-identical (the switch is off by default and absent from a
  build's player).
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py
  content/video_engine/tests/test_idle_e49.py content/video_engine/tests/test_golden_frames.py -q`; `python
  content/video_engine/scripts/measure_frozen_frames.py <private build> --layers page,docks,captions`
- Evidence: pending

### T16: The publish package (R26-8)
- Status: complete (2026-09-12, b00cba7)
- Owner: `implementation_luna`; parent for the first use (gate 6)
- Depends on: none
- Write set: `content/video_engine/scripts/publish_package.py` (new: a `publish/` folder written by the build - the
  YouTube description, the Facebook description with the link for the first comment, the pinned comment, the tags, the
  first frame, and the checklist), `content/video_engine/tests/test_publish_package.py` (new),
  `content/video_engine/scripts/self_watch.py` (the package joins the one-shot bar),
  `content/video_engine/tests/test_self_watch.py`, `docs/content-video-engine/PIPELINE.md` (stage 8),
  `docs/content-video-engine/BACKLOG.md` (R26-8 at `:429`).
- Acceptance: the package regenerates byte-identically from the build's own artifacts (no hand text inside the tool);
  Tokyo's hand-written `SCRIPT-90S-DESCRIPTION.md` is the fixture the tool is measured against and is NOT overwritten;
  the master stays the existing 1440x2560 render path (`scripts/render_episode.py:89`) - no second render is added; the
  checklist is one page and says what a human still does.
- Validate: `python -m pytest content/video_engine/tests/test_publish_package.py
  content/video_engine/tests/test_self_watch.py -q`; `python content/video_engine/scripts/publish_package.py <private
  build>` and the folder read by the parent
- Evidence: `publish_package.py` (528 lines) + 16 tests; `publish_row` on the bar + the 0:00 frame; PIPELINE stage 8; the folder for gate 6: `tokyo-tea-break/build-short-t16/publish/` (8 files; `CHECKLIST.md` names the master render and the two things not on disk). Two self-watch browser rows re-baselined on the frozen build's standing FAILs.

### T17: The race A/B on the clothoid fitter (R26-3's open half)
- Status: pending
- Owner: `implementation_luna` (the measurement); the operator decides (gate 5)
- Depends on: T4; E67's ink lane landed (`scene-evidence-engine.mjs:4209`, `:4281`, `:4377` neighbour the race builder
  at `:4478`)
- Write set: `content/video_engine/scripts/measure_motion_energy.py` (per-frame curvature and timing read on a race
  window), `content/video_engine/tests/test_measure_motion_energy.py`, a proof page under a private build directory,
  `docs/content-video-engine/BACKLOG.md` (R26-3 at `:486`), `docs/content-video-engine/CAPABILITIES.md` only if the
  race adopts the fitter. No write to `buildLedgerRace` before the verdict.
- Acceptance: the A/B answers the row's question with numbers - is the choppiness curvature at the joins (the fitter's
  case, `kinetics/clothoid.mjs`) or timing (`RACE_PERIOD` at `:4364`)? Both arms measured at the same instants on the
  same data, the frames paired for the operator; the row records the answer either way; the fitter is adopted only on
  the operator's word.
- Validate: `python content/video_engine/scripts/measure_motion_energy.py <private build> --window <race>` for both
  arms; `python -m pytest content/video_engine/tests/test_measure_motion_energy.py
  content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T18: The press card's pulled phrase as live type (R26-55)
- Status: pending
- Owner: `implementation_luna`; parent for the face (gate 7)
- Depends on: T5; human gate 7
- Write set: `content/video_engine/scripts/press_card.py` (the phrase's WORDS carried as data beside the raster, which
  stays as the provenance strip), `content/video_engine/scripts/species/press.mjs` (`pressTypeScale` at `:134` sets
  live type re-lined to the surface instead of a scaled raster),
  `content/video_engine/scripts/build_scene_timeline_f.py` (the press dock's phrase field, `DOCK_KIND_PRESS` at
  `:131`), `content/video_engine/tests/test_press_card.py`, `content/video_engine/tests/test_press_dock.py`,
  `content/video_engine/tests/kinetics/press.test.mjs`, the `press-stack` golden source and frame (they move -
  regenerated on purpose in this commit), `docs/content-video-engine/BACKLOG.md` (R26-55 at `:459`).
- Acceptance: on the poster surface (E66, `docs/portable/OPERATOR-RULINGS.md:2140`) the phrase re-lines and reads at or
  above the 17 CSS px phone floor (from 13.4); the provenance raster is still visible and still cites its source; the
  `press-stack` golden's move is named and shown; the stand-in display face is the operator's choice, recorded in the
  commit.
- Validate: `python -m pytest content/video_engine/tests/test_press_card.py
  content/video_engine/tests/test_press_dock.py content/video_engine/tests/test_golden_frames.py -q`; `node --test
  content/video_engine/tests/kinetics/press.test.mjs`
- Evidence: pending

## Verification

- Per slice, before integration: `python content/video_engine/scripts/sync_kinetics.py --check`; `python -m pytest
  content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_portrait_parity.py
  content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_kinetics_flags.py -q`; the slice's
  own suite as written above; `node --test content/video_engine/tests/kinetics/` for every module slice.
- The determinism bar on every slice that touches the engine or the shell: `python
  content/video_engine/scripts/determinism_check.py <private build> --all` - 0 mismatch of the R26-48 class after T4.
- Both approved shorts rebuilt into private directories (`TOKYO_BUILD_DIR=build-short-<slice>`) and every artifact
  diffed against the pre-slice baseline; a non-empty diff is named in the slice's Evidence and approved before the
  commit. No Tokyo render, and a served review link is a frozen copy never rebuilt under the operator.
- The frames read as a viewer at the instants that matter for every mechanism slice, plus the life check on the
  addition's own region (E56 §3).
- `python scripts/prp_validate.py .claude/PRPs/plans/P52-THE-SWEEP.plan.md`; `python
  content/video_engine/scripts/build_docs_layers.py --check` on every doc slice; `python scripts/prp_status.py`.

## Evidence And Handoff

- Per slice: the commit hash with its `Recall: path:line` lines, the module and test line counts, the golden's path
  (and, where one moved, the before and after with the reason), the gate report's changed rows, the probe or
  determinism numbers, the CAPABILITIES and BACKLOG rows closed.
- Human gates 1-7 answered in this file as they are ruled, in the operator's words, with the frame that was read.
- The first customer is `myth-of-historical-normal`: T6's band, T7's count array and T8's agenda are declared built
  only when its shot table uses them and `lint_species_choice.py` reports them chosen on the sentences that want them.
- Cross-plan: P50's species module rule and T1 map and P51's split, probe and self-watch are the ground; T5 finishes
  R26-41 which both plans deferred, and T15 spends P51 T1's split. Anything this plan finds and does not fix goes back
  onto `BACKLOG.md` as a numbered row in the same commit.
