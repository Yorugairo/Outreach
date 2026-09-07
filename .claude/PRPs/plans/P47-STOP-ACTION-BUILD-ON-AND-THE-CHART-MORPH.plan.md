---
id: P47-STOP-ACTION-BUILD-ON-AND-THE-CHART-MORPH
title: Stop-action mechanics (throw and land with weight), build-on (the page performs on a word), and the chart morph (the metaphor becomes the chart)
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-06
updated: 2026-09-06
---

# Stop-action, build-on, and the chart morph

## Summary

The operator, on Tokyo v2 (2026-09-06): *"we're being a bit too lazy with the world plates; we have to play more if we're going
to leave it on screen and not let the video run; learn some of the backlog skills, perform some transformations on the chart"*,
and, repeated for the third time today, *"we need to operationalize stop-action mechanics to be able to throw things on page or
land things with weight"*; named as the three skills: *"the hyperframes stop motion skill + build-on, and chart morph."*

This plan builds the three as engine capabilities the shot table can author by name, each proven on a Tokyo v3 page before it
becomes doctrine: **stop-action** (a stepped clock chosen by speed, a throw that lands with weight, a landing that sells its
weight before the drop), **build-on** (the page performs every sentence: build to a datum on a word, the measured bracket, the
title rewrite), and **the chart morph** (ARAP: the bar tab becomes the holdings line, the metaphor becomes the chart - the
transition that is ours alone).

## Intent And Acceptance

- A dock, a badge, a bracket or a prop can ARRIVE by `spring` (E45), `throw` (an arc onto the page, stepped on 2s, landing with
  squash and a settle by the material's spring) or `land` (weight sold first: a 100-250 ms anticipation, the drop, the impact
  squash, the settle), and the kinetics registry lists each with its `[DERIVED]` dials.
- The holdings page in Tokyo v3 does one thing on every sentence it is under (`tokyo-tea-break/SHOT-TABLE-V3-PROPOSAL.md` part B):
  the line builds to the February peak on one word and the coral drop on another; the bracket draws "−$122.6B · a tenth of the
  pile" from the peak to June; the title rewrites on "the opponent"; nothing on the page is still for a sentence.
- The bar tab (the object page) morphs into the holdings line by ARAP with `det(J(t)) > 0` at every frame and the three match-cut
  invariants (centroid ≤ 0.06 W, axis ≤ 15°, area ratio ≥ 0.60) as gates; it is authored as a page enter (`morph`) and reads as
  one thing changing, judged by the operator in the player.
- Every golden frame stays byte-identical; the motion gate credits a throw, a land and a morph as motion; Tokyo v3 PASSes.

## Scope

- `content/video_engine/scripts/kinetics/stopaction.mjs` (new: the cadence rule, `throw`, `land`), synced into the template by
  `sync_kinetics.py`; the dock / badge / bracket mounts take `arrive: spring|throw|land` and a `mass` (the material presets).
- Three page species in the template + compiler: `build_to`, `bracket`, `retitle`; the shot-table grammar for them.
- `kinetics/arap.mjs` (new: the polar-decomposition morph, triangle mesh, local/global with cotangent weights, Cholesky once) and
  the object → chart page enter `morph`; the object page renderer where it is still a spec (P38 T5).
- Gates: the three invariants for a morph; a throw/land credited by the motion gate; the cadence rule reported per motion piece
  (the on-1s/2s/3s decision, P45 O1) as INFO until measured.
- Tokyo v3: the cut ledger applied (part A) and the page choreography authored (part B) on the new species.

## Not Building

- A rig, joints, skinning (E42: poses first). A prop THROWN onto the page is a still with a path, not a limb.
- A new player runtime: everything is a pure function of `t` on the existing painter (the template law).
- The hyperframes composition surface: the hyperframes skills are read for their stepped-tween and scatter-assemble patterns
  (`.agents/skills/hyperframes-animation/rules/depth-scatter-assemble.md`, `vertical-spring-ticker.md`, `chromatic-glitch.md`'s
  quantized time) and the patterns are ported into our kinetics; no HyperFrames project is built.
- The long form. Every capability is proven on the short first (E46).

## Human Gates

- **HG1 (after T2):** the operator watches Tokyo v3 in the player - the cut ledger applied, the page performing - and rules on
  which cuts stay (part A's operator column) before any render.
- **HG2 (after T1):** the first throw and the first land on a real page, judged by eye in the player: does it read as weight?
  The dials (mass presets, the step cadence, the squash) are tuned against the operator's ear, not the table.
- **HG3 (after T3):** the bar tab → holdings line morph in the player: does it read as one thing changing? The three invariants
  are gates only after the operator says the shape reads.

## Mandatory Reads

- `docs/portable/OPERATOR-RULINGS.md` E44 (the chart on the hook), E45 (docks by the springs; the mount is the roll-out), E46
  (E44/E45 are the shorts standard), E47 (dip and blur-zoom for world changes; the signatures).
- `docs/content-video-engine/42-DRAWING-KINETICS.md` §42.1-42.3 (the stroke, the analytic spring, squash), §42.4 (Euler spirals);
  `48-THE-FIGURE-AND-THE-GROUND.md` §48.6 (mass before motion, the phase lag), §48.4 (APA: weight sold before the lift);
  `43-SCENE-GRAPH-AND-TRANSFORM.md` §43.5 (the morph, method B = ARAP); `briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md:185-193`
  (the cadence rule, `[DERIVED]`), `:226-232` (material spring presets, `[DERIVED]`), `:390-396` (the match-cut invariants).
- `content/video_engine/scripts/kinetics/spring.mjs`, `squash.mjs`, `ink.mjs` (`stepClock`, `soakStepped`), `ease.mjs` (min-jerk);
  `docs/content-video-engine/samples/scene-evidence-player.template.html` (the dock choreography `:843-880`, species painters,
  the LP clock `:1784`); `content/video_engine/scripts/build_scene_timeline_f.py` (species validation, `dock_place`);
  `content/video_engine/scripts/ledger_page.py` (`VARIANTS` incl. `object`, `page_boxes`).
- `tokyo-tea-break/SHOT-TABLE-V3-PROPOSAL.md` (parts A, B, C - the authoring target).
- `docs/ANIMATION-REGISTRY.md` (every dial lands there; the scanner's bare-token trap: name constants distinctively).
- Skills: `quality-rules`, `retrieval-layers`.

## Execution Path

T5 (the idle, E49) and T2 (build-on) first - the idle is what stops the page freezing under a sentence and T2 is what makes it perform; HG1. Then T1 (stop-action) -
the arrivals gain `throw` and `land`; HG2. Then T3 (the morph) - the largest, its own gate; HG3. T4 (Tokyo v3 authored) runs
after T2 and again after T1/T3 land. Every slice: tests on synthetic series first, then the goldens (byte-identical), then the
real page in the player.

## Patterns To Mirror

- E45's dock choreography (spring in, read, park by min-jerk): a species is a pure function of `t` with named `[DERIVED]` dials
  at the template top, mirrored in the gate, listed in the registry; `test_video_dock.py` is the test shape (browser-measured
  rects, determinism across two browsers).
- E47's exits (`dip`, `blurzoom`): the compiler validates names, emits durations, the gate credits the span.
- `measure_cut_kinds.py`: thresholds are `[DERIVED]` starting references, printed in the report header, tested on synthetic series.
- `ink.mjs` `stepClock` / `soakStepped`: the stepped clock is a seeded staircase on quantized time, never `Math.random`.

## Task Slices

### T1: Stop-action mechanics - the stepped clock, `throw`, `land`
- Status: pending
- Owner: implementation_luna
- Depends on: none (T2 first in the path, but no file dependency)
- Write set: `content/video_engine/scripts/kinetics/stopaction.mjs` (new), `content/video_engine/scripts/sync_kinetics.py` (register the module), the template (the arrivals: dock / badge / bracket mounts take `arrive` + `mass`; the cadence report), `content/video_engine/scripts/build_scene_timeline_f.py` (validate `arrive`, `mass`), `content/video_engine/scripts/gate_motion_density.py` (a throw/land credited as motion; the cadence rule as an INFO row per motion piece), tests: `content/video_engine/tests/kinetics/test_stopaction.py` (new), `test_video_dock.py` (+ arrive cases), `test_gate_motion_density.py` (+ rows)
- HyperFrames intake (HF-1, HF-2, HF-6; `docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md`): the stepped clock quantises on the INTEGER frame index (`frame = round(t*fps)`, `step = floor(frame/hold)`), never on elapsed seconds - and `ink.mjs` `stepClock` + the template's `plate_life` step move to the same form; `land` and the dock's park give what a thing drags (a shadow, a tick, a housing) a `lag_frames: 1 [DERIVED: HyperFrames /prompting/motion, verified 2026-09-06; measure on ours]`; impacts ease IN, entrances ease OUT (the easing grammar).
- Acceptance: (1) the cadence rule `cadence(v_px_s, kind)` returns on-1s / on-2s / on-3s per the `[DERIVED]` thresholds (250 / 300 / 100 px/s, tagged, printed) and `stepped(u, cadence)` quantises a clock deterministically; (2) `throw(from, to, mass, t)` returns position, rotation and the squash tensor along an arc (a ballistic path under a gravity dial, min-jerk on release, the landing at `to` with the impact squash from `squash.mjs` and the settle from the material's spring), stepped on 2s while translating under 250 px/s and on 1s above; (3) `land(at, mass, t)` sells the weight first (a 100-250 ms anticipation lift `[DERIVED: 48 §48.4 APA]`), drops, squashes on impact (area-preserving), settles by the material spring; (4) a dock declared `arrive: throw` in the shot table flies onto the page and parks (E45's park still follows); a badge declared `arrive: land` lands with weight; (5) the registry lists every dial with its tag; goldens byte-identical
- Validate: `python -m pytest content/video_engine/tests/kinetics/test_stopaction.py content/video_engine/tests/test_video_dock.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py -q -p no:cacheprovider; python content/video_engine/scripts/sync_kinetics.py --check; python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: pending

### T2: Build-on - the page performs on a word (`build_to`, `bracket`, `retitle`)
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: the template (three species painters on the LP clock), `content/video_engine/scripts/build_scene_timeline_f.py` (validation + the shot-table grammar for the three), `content/video_engine/scripts/ledger_page.py` (ONLY if the bracket needs a geometry accessor it lacks; no change to existing outputs), tests: `content/video_engine/tests/test_page_performs.py` (new), `test_gate_motion_density.py` (a `build_to` cap is not stillness while the next cap is pending - it is a hold, INFO), `docs/content-video-engine/CAPABILITIES.md` (three rows)
- Acceptance: (1) `build_to {at, index}` caps the drawn series at the datum; the BUILD beat ends at the first cap and the remainder draws on the next cap's word, the same stroke engine (`stroke.mjs`), so the coral drop is its own stroke on "watching"; (2) `bracket {at, from, to, label, sub}` draws a measured vertical span between two data by the hand (min-jerk), lands its ticks, writes the label in Kalam, and `relight {at, target: bracket}` re-fires its colour on a word; the bracket never intersects the plot's own line (it sits in the quiet zone beside the two data, like the infographic's); (3) `retitle {at, text}` erases the title by the roll's carried light over 0.4 s and writes the new title per-glyph as the build did; (4) frames rendered through `render_baseline.render_frame` prove each: the series' last drawn x at a cap equals the datum's x (±2 px); the bracket's pixels lie between the two data's y and outside the plot box; the new title's ink appears after the old title's is gone; determinism across two browsers; (5) goldens byte-identical (no golden uses the three)
- Validate: `python -m pytest content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py content/video_engine/tests/test_video_dock.py -q -p no:cacheprovider; python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: 2026-09-06 - `test_page_performs.py` 15 passed (grammar: every field refused by name, a page species on a plain plate refused; gate: at/end credited for each kind, a relight one flash, M19 lists the hold 0:07+4.6s; browser on the soak golden's line (316 points, peak 191 of 235 drawn in the tail): at 9.0 s the capped line's drawn fraction equals the polyline fraction to the peak within 0.01 and its tip x is the datum's x within 2 px, unchanged at 11.9 s (the HOLD), mid-word at 12.75 s strictly between, 0.995+ at 13.7 s; the bracket is invisible before its word, mid-draw at +0.4 s with its label at 0, span drawn and every glyph at 1 by +2.0 s, y0/y1 exactly the two data's y, the span right of both data and the label stacked above the peak (no room beside on this page); the relight peaks at 1.000 mid-word and is 0 after; the retitle erases first glyph first (glyph 0 at 0 while the last is still > 0) with the new title unwritten, then old all 0 / new all 1; two browsers, one frame). Full suite (goldens, flag goldens, determinism, docks, E47, gate, idle): **144 passed in 131.59s** - every golden byte-identical. Found and fixed on the way: an empty caption-page list threw `PG[-1]` at load and skipped every later definition. The `dock_place` risk: the bracket lives inside the plot box, which the park already forbids - nothing to add. Tokyo v3 first pass authored on the species (T4): build_short.py rows 2/4/6.

### T3: The chart morph - ARAP, and the object → chart page enter
- Status: pending
- Owner: implementation_luna (architect_sol reviews the mesh design before the build)
- Depends on: T2 (the page's clock hooks)
- Write set: `content/video_engine/scripts/kinetics/arap.mjs` (new: triangulate two closed outlines to one topology, polar decomposition per triangle `J = R·S` in closed form for 2×2, local/global ARAP with cotangent weights, the Laplacian factored once, `det(J(t)) > 0` asserted), `sync_kinetics.py`, the template (the `morph` page enter: the object page's props morph into the chart's line/bars over `MORPH_S` `[DERIVED]`), `ledger_page.py` (the object page renderer where P38 T5 left it a spec; `--variant object` already validates), `build_scene_timeline_f.py` (`enter=morph`), `gate_motion_density.py` (the three invariants as a gate row `M17` `[DERIVED: briefs:390-396]`; a morph credited as motion), tests: `content/video_engine/tests/kinetics/test_arap.py` (new: a square → a rotated bar through 120° never inverts; centroid / axis / area invariants computed), `test_page_performs.py` (+ the morph frames), `CAPABILITIES.md`
- Acceptance: (1) on synthetic outlines the morph keeps `det(J) > 0` at every sampled `t` through > 90° of rotation where linear blending collapses (the test shows the linear case collapsing); (2) the bar tab (Tokyo's object page: the receipt) becomes the holdings line on "unfunded bar tab" as one continuous thing in the player (HG3); (3) M17 reports the three invariants per morph; (4) goldens byte-identical; the kinetics registry lists `arap` with its sources (Alexa 2000 / Sorkine & Alexa 2007, on file or "not on file")
- Validate: `python -m pytest content/video_engine/tests/kinetics/test_arap.py content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py -q -p no:cacheprovider; python content/video_engine/scripts/sync_kinetics.py --check; python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: pending

### T4: Tokyo v3 - the cut ledger applied and the page choreography authored
- Status: pending
- Owner: parent (authoring is judgment), junior_developer for the shot-table edits
- Depends on: T2 (first pass), T1 and T3 (second pass)
- Write set: `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py` (the shot table + species), `sound/SOUND-PLAN.json` (cues follow the new arrivals: a throw's landing gets the press cue's successor at the E44 gain), the build outputs
- Acceptance: part A's operator column applied (the cuts that add nothing removed, the two misplaced moved, the callout datum fixed); part B authored on the real species; motion gate PASS; the operator watches in the player (HG1) before any render; the analytics read of the next post is recorded against v3's scene list
- Validate: `python build_short.py` from the project folder; `build-short/GATES-MOTION.md` VERDICT PASS; the player served on :8731
- Evidence: pending

### T5: The idle - nothing ever goes truly still (E49)
- Status: complete
- Owner: implementation_luna
- Depends on: none (small; can run first)
- Write set: the template (an `idle` on every held element: the page's body, a parked dock, badges, the bracket, a plate; kinds `breath` (scale 1-2 %, a slow sine or the stepped clock), `drift` (px/s along a direction), `pulse` (luminance); the figure's asymmetric breath from doc 48 §48.4 as the `figure` kind), `content/video_engine/scripts/kinetics/idle.mjs` (new, synced), `build_scene_timeline_f.py` (defaults per element class; an authored `idle` on a shot row overrides; `idle: none` is explicit), `gate_motion_density.py` (the `frozen frames` row: hashes of rendered frames or the player's per-frame state, a run of identical frames > `FROZEN_MAX_S` WARNs; an idle never counts as an event for M01/M10/M16), tests (`content/video_engine/tests/kinetics/test_idle.py`, the gate test), `CAPABILITIES.md`
- Acceptance: on the golden ledger scene with no species, two frames 0.5 s apart differ by the idle alone (a measured 1-2 % scale on the page body, nothing else moving); the frozen-frames row WARNs on the pre-E49 build and passes after; the goldens stay byte-identical (idle off on golden timelines by an explicit `idle: none` written into their sources, or the default applies only to timelines that declare `idle`); the Tokyo v3 page never freezes while it holds under a sentence
- Validate: `python -m pytest content/video_engine/tests/kinetics/test_idle.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py -q -p no:cacheprovider; python content/video_engine/scripts/sync_kinetics.py --check`
- Evidence: 2026-09-06 (commit d39a08e + 4e3678b) - `kinetics/idle.mjs` synced (6 modules in sync); `node --test` 40 pass; pytest
  `test_idle_e49.py test_kinetics_flags.py test_gate_motion_density.py test_golden_frames.py test_render_determinism.py
  test_video_dock.py test_transitions_e47.py` = **126 passed in 119.69s** (the five base goldens + six flag goldens byte-identical;
  the new flag golden `ledger-soak-page@idle` at t=11.0). **The freeze, then its cure (browser, the soak golden's page under a bare
  hold - captions off, Ken Burns zeroed):** flag off, the frames at 11.0 s and 11.5 s hash identical (the frozen frame E49 names);
  flag on, they differ, the page's box breathes 1.0092 at the sampled t and its width ratio over a 4 s period sits in (1.008, 1.02)
  (dial 1.2 %), the transform string is `translate(0px, 0px) scale(1.00xx)` - scale only - and a seek is the play. **The golden
  itself carried a 0.04 Ken Burns push** (capped to 0.03 by the player): the blunt cure E49 retires, found by the test the moment
  it was written. **Tokyo v2 measured at 12 fps (1066 frames, `measure_frozen_frames.py`):** pre-E49 build (preserved as
  `build-short.v2-pre-e49/`, its `frame-hashes.json` + `GATES-MOTION.md` beside it) - 1036 distinct frames of 1066, longest
  identical run 5 frames = 0.33 s at 1:01, **M18 PASS**; rebuilt with `kinetics.idle` on - 1065 distinct of 1066, longest run
  2 frames = 0.08 s at 0:19, **M18 PASS**, VERDICT PASS (0 FAIL / 1 WARN / 14 PASS). **Finding, stated plainly:** the acceptance
  assumed the pre-E49 build would WARN; it does not, because a short's PHRASE captions boil at 10 fps on every landed word for the
  whole runtime (E49 s1: the captions were already at an idle) and a video dock moves - the whole-frame hash cannot see a frozen
  page beneath a boiling caption. The per-element freeze is proven on the golden (captions off); M18 as built is the necessary
  whole-frame check, and a per-layer hash (the caption and dock layers hidden) is the sharper tool - backlog R26-13. The Tokyo v2
  player on :8731 now carries the idle (the operator's watch is still pending; nothing rendered).

## Verification

```bash
python -m pytest content/video_engine/tests/kinetics content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_video_dock.py content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py -q -p no:cacheprovider
python content/video_engine/scripts/sync_kinetics.py --check
python content/video_engine/scripts/build_docs_layers.py --check
```

## Evidence And Handoff

- Per slice: the verbatim test tail, the frame proofs (browser-measured rects / luminance / sharpness through
  `render_baseline.render_frame`), the registry rows for every new dial with its `[DERIVED]` tag, and the goldens' byte-identity.
- HG1/HG2/HG3: the operator's words on what the player showed, recorded in this plan's slice evidence and, when a call becomes
  doctrine, as a ruling in `docs/portable/OPERATOR-RULINGS.md`.
- Handoff: Tokyo v3 in `build-short/` (v2 preserved as `build-short.v2/`), the player served on :8731 for the watch; the render
  only after the operator's word; the next post's analytics read against v3's scene list in `tokyo-tea-break/ANALYTICS-*.md`.
- The transitions review (`docs/content-video-engine/TRANSITIONS-REVIEW-2026-09-06.md`) gains a §8 when T3 lands: the morph as
  the match cut (TR-7 closed) and what the stepped clock did to the shorts' pulse (M16).

## Risks

- The stepped clock on a translating dock can strobe (Watson 1986, the brief's failure signature); the cadence rule is the guard
  and its thresholds are untested on our own motion - HG2 is the test, the dials move by ear.
- The bracket can collide with the parked dock (E45's `place`); `dock_place` must treat a bracket's rect as forbidden - T2 adds
  it to `page_boxes`' forbidden set or reports why it cannot.
- ARAP on outlines with different vertex counts needs a correspondence (arc-length resampling first); a bad correspondence reads
  as a smear, not a morph - the architect's mesh review before T3 builds.
- Three species and a morph on the same 36 s page can crowd it; the rule stays one thing per sentence (part B), never two.

## Backlog And Evidence Updates

- BACKLOG: R26-10 (the page performs) → this plan; P38 T4 (ARAP) and T6 (object → chart) → T3 here; P45 O1 (the cadence module)
  → T1 here; R26-7 (the world is the stage) gains the three verbs.
- `docs/ANIMATION-REGISTRY.md` after each slice: the new dials with their tags; `docs/GATES-REGISTRY.md`: M17.
- `tokyo-tea-break/ANALYTICS-*.md`: the next post's curve read against v3's scene list (E44 §3's test).
