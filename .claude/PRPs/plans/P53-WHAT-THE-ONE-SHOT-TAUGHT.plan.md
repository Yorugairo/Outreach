---
id: P53-WHAT-THE-ONE-SHOT-TAUGHT
title: What the one-shot taught - the page's opening register, the hand-off that empties the stage, the two species defects its frames found, and the rows that stand between us and a better second one
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-12
updated: 2026-09-12
---

# What the one-shot taught

## Summary

The operator, 2026-09-12, after the first one-shot of a NEW short (`normal-for-which-bridge`, built end to end in
one pass): *"and yes, we need to build the ability to land with the ledger already built. I'm surprised we don't
already have that capability, shouldn't be hard to add"*, then *"/prp-plan all of the fixes you learned that you
need from R26"*.

The one-shot passed the script gates, the motion gate and the layout probe, and its FRAMES still showed four
defects no gate can see (E71 is the ruling that came out of it). This plan is those defects plus the R26 rows that
stand between the engine and a better second one-shot. Nothing here is re-derived: every slice quotes its row.

**One correction lands before the work does.** R26-65 claimed the page cannot arrive built. It can:
`enter=built` has been in the grammar since 2026-09-08. The row is corrected, the capability is proved on disk
(`build-short-built/`, frame 0 carries the whole page), and what remains is the AXES register the operator named
plus the default.

**Recall** (the receipt, `docs/runbooks/RECALL-RECEIPT.md`):
- **The page's enters already exist.** `content/video_engine/scripts/build_scene_timeline_f.py:56` -
  `LEDGER_ENTERS = ("spiral", "mount", "morph", "snap", "built", "throw", "drop", "camera")`, and `built` is
  *"the page ARRIVES with its chart already drawn, by the row's own transition - it NEVER mounts"* (operator,
  2026-09-08). Pinned: `content/video_engine/tests/test_page_performs.py:552` *"enter=built arrives drawn"*, and
  the gate's own arrival offset `:165` *"a snapped page arrives built: its mark is its entry"*. Proved again
  2026-09-12 in `content/video_engine/projects/systems-and-blowups/normal-for-which-bridge/build-short-built/`.
  `docs_find "axes"` returns the page's axis drawing, no enter that lands on axes alone.
- **The hold ceiling is already withdrawn.** `docs/portable/OPERATOR-RULINGS.md` E69 (2026-09-12) and doc 29
  §9.13's amendment: the hold is legal while the frame LIVES; `content/video_engine/scripts/gate_motion_density.py`
  M05 reads the longest gap inside the hold against the pulse (2.5 s, M16) or the long form's target (8 s, M02).
  So no slice here manufactures worlds to clear a hold.
- **The transitions.** `content/video_engine/scripts/build_scene_timeline_f.py:1374` `scene_exit` and `:97`
  `SIGNATURE_ENTERS`, `:131` `DEFAULT_EXIT_CHANGE = "dip"`; the dip is the one transition that may empty the
  stage (the dip is a world change, 2026-09-12 memory). `docs/content-video-engine/BACKLOG.md:472` R26-66 carries
  the measurement: three holes of 1.5-3.5 s, 8% of a 69 s short, each under a live sentence.
- **The two species defects.** `content/video_engine/scripts/species/ring.mjs` (the flag chip and `flag_side`,
  P52 T8) and `content/video_engine/scripts/species/span.mjs` (P50 T4; R26-25 wrote *"shaded behind the line"* and
  the shade is painted over it). Rows: `BACKLOG.md:473` R26-67, `:474` R26-68.
- **The row proposer has a reader already.** `content/video_engine/scripts/lint_species_choice.py:1` - the map is
  `docs/content-video-engine/SPECIES-BY-SENTENCE.md`, it classifies every sentence by ACT and prints
  `· no row` where an act has an available species and nothing fires. What is missing is the emit.
  `docs/content-video-engine/PIPELINE.md` is the constraint: *"Stage 7 is AUTHORED. There is no allocator"* -
  a proposer offers semantic candidates and never fills slots by count.
- **The voice.** `docs/portable/OPERATOR-RULINGS.md` E70 (2026-09-12): Chirp does not ship on YouTube, the lane
  splits by platform again, a one-shot renders BOTH takes, and a Chirp clock is aligned with LOCAL Whisper
  (`docs/.../local-whisper-no-paid-stt` memory: never cloud STT). `content/video_engine/scripts/scratch_take.py`
  already has `--engine both`.

## Intent And Acceptance

**Intent.** Make the second one-shot better than the first by fixing what the first one's frames and gates
actually found, in the order that buys the most per slice: the opening register first (it changes every short's
first second), then the hand-off (8% of the runtime), then the two species defects, then the rows that unblock a
richer world (the cutout dock, the compiler's `:cut` stamp, the dials).

**Acceptance.**
1. A hook row can declare `enter=axes` and frame 0 carries the charcoal page with its ground, frame, title and
   axes while the line draws from the first frame - proved on a rendered frame, not on a timeline field.
2. `enter=built` and `enter=axes` are read by M11 as annotated on arrival when the light lands within 1.5 s of the
   line's own finish, and a hook row with no declared enter is named by a lint.
3. The share of a short's runtime with no world on stage is MEASURED per transition kind, and the suck, the melt
   and the spiral lay the incoming page's ground under the outgoing world so that share falls to 0 outside a
   declared dip.
4. The ring's flag chip never crosses the page box; the span's shade is behind the ink and never covers a series
   label. Both proved on the frame that showed the defect.
5. `STOP.IMPACT_S` is gone or justified in place; a declared cadence faster than `CADENCE.STROBE_PX_S` is a gate
   row; `ON1_PX_S` is measured against the brief's own 100 px/s on our own motion.
6. A ledger page under a `suck` or a `melt` gets its `:cut` from the compiler, which says so.
7. `lint_species_choice.py --propose` emits DRAFT rows for the sentences that have an act and no row, each row
   carrying the act and the `when` that proposed it, and the parent keeps or deletes each one by hand.
8. A one-shot renders both takes and can run its clock off either.

**Anti-goals.** No allocator (PIPELINE.md). No new species. No change to the cut placement rule (TR-13/M13's gap
rule is the pin the two approved shorts carry). No render and no publish inside this plan.

## Scope

`content/video_engine/scripts/build_scene_timeline_f.py` (the enter grammar, the `:cut` stamp),
`docs/content-video-engine/samples/scene-evidence-engine.mjs` + `content/video_engine/scripts/species/*.mjs` (the
axes register, the ring's flag, the span's shade), `content/video_engine/scripts/gate_motion_density.py` (M11's
arrival read, the new stage-gap row), `content/video_engine/scripts/lint_species_choice.py` (`--propose`),
`content/video_engine/scripts/scratch_take.py` + a Whisper alignment, `content/video_engine/scripts/kinetics/stopaction.mjs`,
the tests beside each, the goldens each moves on purpose, and the rows in `docs/content-video-engine/BACKLOG.md`.

## Not Building

- The Apex Chart Read as a fixed opening TEMPLATE (the research recommends it twice; the operator has not ruled it,
  and T1 gives the register it would be built from).
- The YouTube lane's voice (E70 leaves it open on purpose).
- The press-card lane for a one-shot: a press card needs a screenshot of a published page and its rights posture is
  E68's, not this plan's.
- R26-57's stage-space text measurement: it needs a build that writes `#species` text, which none of these slices
  produce. It stays a trigger on the first chip board, flow diagram or map.

## Human Gates

1. **The opening register** (T1): the operator reads frame 0 and frame 0.5 of the axes register against the built
   register, on the same short, and rules which is the hook's default.
2. **The hand-off rule** (T2): after the measurement, the operator rules whether the incoming ground goes under the
   outgoing world for every non-dip transition, or whether the cut simply lands later.
3. **The strobe row** (T5): the threshold a declared cadence must obey, given P50 T13's own burst travels 359 px/s.
4. **The cutout dock's first frame** (T7): gate 1's 16:9 frame re-rendered with a head that carries no card.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (dispatch mapping, lane write sets, hand-off policy).
- `docs/portable/OPERATOR-RULINGS.md` E69 (the hold), E70 (the voice), E71 (the ship bar), E72 (generation is the
  agent's, the video is the operator's), E40 (a returning page unwinds, never redraws), E44, E49, E56, E58.
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.13 (as amended), §9.26-§9.31.
- `docs/content-video-engine/PIPELINE.md` (stage 7 is authored; the render contract).
- `docs/content-video-engine/BACKLOG.md` rows R26-57 to R26-68.
- `docs/content-video-engine/SPECIES-BY-SENTENCE.md` (the ten acts) for T7's proposer.

## Execution Path

Parent owns T1, T2 and T7 (shared files, the enter grammar and the transition clock). `implementation_luna` takes
T5, T6 and T8. `junior_developer` takes T3 and T4 (one module each, a golden each). `speedster` takes T9's
`--engine both` wiring. Every delegated diff is reviewed by the parent before integration, and the frames are read
by the parent in every case - a subagent's PASS is not evidence (E71).

## Patterns To Mirror

- A species module registers its painter as its last statement and is inlined by `sync_kinetics.py --write` (the
  module rule); the engine's copy is never edited by hand.
- A gate row carries its SRC string and a test that pins both verdicts (the dead case and the live case), the shape
  E69's pair just used.
- A measurement lands as a script that writes a JSON beside the build, then a gate reads that JSON (M25 reads
  `layout-probe.json`; T2's stage-gap row reads its own).

## Task Slices

### T1: `enter=axes`, and M11 reads an arrival
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/scripts/gate_motion_density.py`, `content/video_engine/tests/test_page_performs.py`, `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: a row declaring `ledger:<series>:line:<i>:right:axes:cut` lands the page with ground, frame, title and axes at frame 0 and draws the line from the first frame; `enter=built` and `enter=axes` both read as annotated on arrival by M11 when the light lands within 1.5 s of the line's finish; a hook row (first row, t=0) with no declared enter is named INFO by the species lint
- Validate: `python -m pytest content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_gate_motion_density.py -q`; rebuild `normal-for-which-bridge` into `build-short-axes` and read frames 0.0, 0.3, 0.8, 1.5
- Evidence: pending

### T2: the hand-off - measure the empty stage, then close it
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/measure_stage_gaps.py` (new), `content/video_engine/scripts/gate_motion_density.py`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: the measure writes the share of runtime with no world on stage and the per-transition gap (suck, melt, spiral, dip, cut) for a build; the gate FAILs a non-dip transition whose gap carries spoken words; the engine lays the incoming page's ground under the outgoing world for the suck, the melt and the spiral so the measured share is 0 outside a dip
- Validate: `python content/video_engine/scripts/measure_stage_gaps.py <build>` on `normal-for-which-bridge/build-short` before and after; `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: pending

### T3: the ring's flag chip stays on the page (R26-67)
- Status: pending
- Owner: junior_developer
- Depends on: none
- Write set: `content/video_engine/scripts/species/ring.mjs`, `content/video_engine/tests/golden/frames/` (the frames this moves on purpose), `content/video_engine/tests/test_species_ring.py` if it exists else the species test beside it
- Acceptance: with the ring on a datum inside the last 15% of the x extent the flag goes left; a chip that would still cross the page box is placed under the ring; the ellipse encloses the datum's own mark including a spike
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`; `python -m pytest content/video_engine/tests -k ring -q`; re-shoot the closing frame of `normal-for-which-bridge/build-short` at 69.0 s
- Evidence: pending

### T4: the span's shade goes behind the ink (R26-68)
- Status: pending
- Owner: junior_developer
- Depends on: none
- Write set: `content/video_engine/scripts/species/span.mjs`, the goldens it moves
- Acceptance: the shade paints under the line and under every label; a series label inside the span's x range is moved out of the shade or the shade stops short of it; the span's own label never collides with the page's y-axis label (M28 stays clean)
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`; `python -m pytest content/video_engine/tests -k span -q`; re-shoot 38-40 s of `normal-for-which-bridge/build-short`
- Evidence: pending

### T5: R26-64's two dials
- Status: pending
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/scripts/kinetics/stopaction.mjs`, `content/video_engine/scripts/gate_motion_density.py`, `content/video_engine/tests/test_kinetics_stopaction.py` (or the test beside the module), `docs/content-video-engine/47-FINDINGS-TO-CHECKS.md`
- Acceptance: `STOP.IMPACT_S` is deleted (or carries, in place, the reason a time decay returns); a declared cadence (`break_cadence`, an authored hold, a boil) faster than `CADENCE.STROBE_PX_S` fails a gate row naming the speed; `ON1_PX_S` is measured on our own motion against the brief's E2 §7 100 px/s and the measurement is written into the row
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check`; `python -m pytest content/video_engine/tests -k stopaction -q`; `python content/video_engine/scripts/build_animation_registry.py --check`
- Evidence: pending

### T6: the compiler stamps `:cut` under a suck or a melt (R26-60)
- Status: pending
- Owner: implementation_luna
- Depends on: T2 (the same transition code path)
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/test_build_scene_timeline_f.py`
- Acceptance: when a scene's exit is `suck` or `melt`, a ledger page row with no declared exit compiles as `:cut` and the build prints that it stamped it; a page that declares its own exit is untouched
- Validate: `python -m pytest content/video_engine/tests/test_build_scene_timeline_f.py -q`; rebuild `normal-for-which-bridge` and confirm the printed stamp
- Evidence: pending

### T7: the cutout dock kind (R26-59)
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`, `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/samples/scene-evidence-player.template.html`, the tests and goldens beside them
- Acceptance: a dock declared `cutout` renders with no card frame and no paper; `centred_place` takes the band's `reserve`; `cap_band: "above"` is legal on a crawl with nothing docked; gate 1's 16:9 frame is re-rendered with a real head
- Validate: `python -m pytest content/video_engine/tests -k "dock or newsreel" -q`; re-render `tests/golden/frames/newsreel-band.png` on purpose and read it
- Evidence: pending

### T8: the row proposer and the short-form shape
- Status: pending
- Owner: implementation_luna
- Depends on: T1 (the shape's opening row declares an enter)
- Write set: `content/video_engine/scripts/lint_species_choice.py`, `docs/content-video-engine/patterns/SHORT-FORM-SHAPE.md` (new), `content/video_engine/tests/test_lint_species_choice.py`
- Acceptance: `--propose` prints a draft row per sentence that has an act, an available species and no row, each carrying the ACT and the `when` that proposed it and a target read off the series' own facts; it never proposes by count, never writes a shot table, and says so in its own header; the shape doc names the short's five positions (the apex read, the instances, the turn, the cost, the ring) with the enter each takes
- Validate: `python content/video_engine/scripts/lint_species_choice.py <project> --propose`; `python -m pytest content/video_engine/tests/test_lint_species_choice.py -q`
- Evidence: pending

### T9: both takes, and a clock off either (E70)
- Status: pending
- Owner: speedster
- Depends on: none
- Write set: `content/video_engine/scripts/scratch_take.py`, `content/video_engine/scripts/align_take.py` (new, local Whisper), `docs/portable/VOICE-PACK.md`
- Acceptance: one command renders both takes for a script; `align_take.py` turns a Chirp mp3 into a words.json in the take's schema using LOCAL Whisper only; a build can point at either take's words and says which it used
- Validate: `python content/video_engine/scripts/scratch_take.py --engine both --script <script>`; `python content/video_engine/scripts/align_take.py <mp3> --out <words.json>`; a rebuild of `normal-for-which-bridge` on the Chirp clock
- Evidence: pending

### T10: R26-58, a thrown dock's flight warm versus cold
- Status: pending
- Owner: implementation_luna
- Depends on: none
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the dock loop's contact placement), `content/video_engine/tests/` the determinism test beside it
- Acceptance: at Tokyo 75.79 the contact shadow is identical warm and cold; the cure is in the contact placement, not in the throw law
- Validate: `python content/video_engine/scripts/determinism_check.py <build> --instants 75.79`; `px_diff.py` on the pair
- Evidence: pending

## Verification

- `python -m pytest content/video_engine/tests -q` (the whole suite; the pre-existing headless smoke against the
  stale single-file `build-short/player.html` stays red and is named in the evidence, not fixed here).
- `python content/video_engine/scripts/sync_kinetics.py --check` after any species or kinetics module moves.
- `python content/video_engine/scripts/build_docs_layers.py --check` (8 layers in sync) after any doc or row moves.
- `python content/video_engine/scripts/build_animation_registry.py --check` after T5.
- A rebuild of `normal-for-which-bridge` per slice that touches the compiler or the engine, its frames read by the
  parent (E71: gate-clean is necessary, not sufficient), and the four rows' own instants re-shot.

## Evidence And Handoff

Each slice appends its evidence to its own row: the command, its output, the frames read and the rows closed or
amended. The plan is complete when the acceptance list above is proved on frames and the four human gates are
ruled. The second one-shot is the acceptance test for the whole plan: a new short, written and built in one pass,
whose frames carry no defect the parent can see.
