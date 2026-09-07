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
- Status: complete
- Owner: implementation_luna
- Depends on: none (T2 first in the path, but no file dependency)
- Write set: `content/video_engine/scripts/kinetics/stopaction.mjs` (new), `content/video_engine/scripts/sync_kinetics.py` (register the module), the template (the arrivals: dock / badge / bracket mounts take `arrive` + `mass`; the cadence report), `content/video_engine/scripts/build_scene_timeline_f.py` (validate `arrive`, `mass`), `content/video_engine/scripts/gate_motion_density.py` (a throw/land credited as motion; the cadence rule as an INFO row per motion piece), tests: `content/video_engine/tests/kinetics/test_stopaction.py` (new), `test_video_dock.py` (+ arrive cases), `test_gate_motion_density.py` (+ rows)
- HyperFrames intake (HF-1, HF-2, HF-6; `docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md`): the stepped clock quantises on the INTEGER frame index (`frame = round(t*fps)`, `step = floor(frame/hold)`), never on elapsed seconds - and `ink.mjs` `stepClock` + the template's `plate_life` step move to the same form; `land` and the dock's park give what a thing drags (a shadow, a tick, a housing) a `lag_frames: 1 [DERIVED: HyperFrames /prompting/motion, verified 2026-09-06; measure on ours]`; impacts ease IN, entrances ease OUT (the easing grammar).
- Acceptance: (1) the cadence rule `cadence(v_px_s, kind)` returns on-1s / on-2s / on-3s per the `[DERIVED]` thresholds (250 / 300 / 100 px/s, tagged, printed) and `stepped(u, cadence)` quantises a clock deterministically; (2) `throw(from, to, mass, t)` returns position, rotation and the squash tensor along an arc (a ballistic path under a gravity dial, min-jerk on release, the landing at `to` with the impact squash from `squash.mjs` and the settle from the material's spring), stepped on 2s while translating under 250 px/s and on 1s above; (3) `land(at, mass, t)` sells the weight first (a 100-250 ms anticipation lift `[DERIVED: 48 §48.4 APA]`), drops, squashes on impact (area-preserving), settles by the material spring; (4) a dock declared `arrive: throw` in the shot table flies onto the page and parks (E45's park still follows); a badge declared `arrive: land` lands with weight; (5) the registry lists every dial with its tag; goldens byte-identical
- Validate: `python -m pytest content/video_engine/tests/kinetics/test_stopaction.py content/video_engine/tests/test_video_dock.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py -q -p no:cacheprovider; python content/video_engine/scripts/sync_kinetics.py --check; python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: 2026-09-06 - `node --test` kinetics 48 pass (stopaction 8); `test_stop_action.py` 7 passed (browser: the thrown dock's box mid-flight differs from its landed box by > 150 px in x or > 60 px in y, the landed box matches the spring's pop box within 1 px on x/y/w/h, the transform right after the landing carries the squash matrix, a seek is the play; the landing pill sits > 40 px above its rest at +0.09 s and rests within 1 px of where the pop rests). Full suite: **{SUITE}** - every golden byte-identical (no flag golden for `stop_action`: the flag alone renders nothing, the authored `arrive` does - stated deviation from the P43 T6 pattern). Tokyo v3 second pass (T4): the panel thrown on "Three men", the two fingers landed (metal) on "Two numbers" - gate VERDICT PASS (0 FAIL); M18 no run of bit-identical frames over 0.50s ; [INFO ] M20 2 arrival(s): dock-c-blue-ties-panel throw ~1188 px/s -> on 1s; dock-g-two-fingers land (metal) - weight sold 0.32s before the impact. Deviation, stated: `ink.mjs` `stepClock` and `plate_life` stay on their elapsed-seconds form (moving them shifts goldens by a frame at a boundary - a golden refresh with the operator); the cadence rule is reported per arrival (M20) and not yet measured against our own motion (HG2 tunes by eye). Acceptance (4) "a badge declared arrive: land" is met by the page's pills (`;arrive=land` on the plate id); the bracket's ticks keep their spring landing (no `arrive` on a bracket).

### T2: Build-on - the page performs on a word (`build_to`, `bracket`, `retitle`)
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: the template (three species painters on the LP clock), `content/video_engine/scripts/build_scene_timeline_f.py` (validation + the shot-table grammar for the three), `content/video_engine/scripts/ledger_page.py` (ONLY if the bracket needs a geometry accessor it lacks; no change to existing outputs), tests: `content/video_engine/tests/test_page_performs.py` (new), `test_gate_motion_density.py` (a `build_to` cap is not stillness while the next cap is pending - it is a hold, INFO), `docs/content-video-engine/CAPABILITIES.md` (three rows)
- Acceptance: (1) `build_to {at, index}` caps the drawn series at the datum; the BUILD beat ends at the first cap and the remainder draws on the next cap's word, the same stroke engine (`stroke.mjs`), so the coral drop is its own stroke on "watching"; (2) `bracket {at, from, to, label, sub}` draws a measured vertical span between two data by the hand (min-jerk), lands its ticks, writes the label in Kalam, and `relight {at, target: bracket}` re-fires its colour on a word; the bracket never intersects the plot's own line (it sits in the quiet zone beside the two data, like the infographic's); (3) `retitle {at, text}` erases the title by the roll's carried light over 0.4 s and writes the new title per-glyph as the build did; (4) frames rendered through `render_baseline.render_frame` prove each: the series' last drawn x at a cap equals the datum's x (±2 px); the bracket's pixels lie between the two data's y and outside the plot box; the new title's ink appears after the old title's is gone; determinism across two browsers; (5) goldens byte-identical (no golden uses the three)
- Validate: `python -m pytest content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py content/video_engine/tests/test_video_dock.py -q -p no:cacheprovider; python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: 2026-09-06 - `test_page_performs.py` 15 passed (grammar: every field refused by name, a page species on a plain plate refused; gate: at/end credited for each kind, a relight one flash, M19 lists the hold 0:07+4.6s; browser on the soak golden's line (316 points, peak 191 of 235 drawn in the tail): at 9.0 s the capped line's drawn fraction equals the polyline fraction to the peak within 0.01 and its tip x is the datum's x within 2 px, unchanged at 11.9 s (the HOLD), mid-word at 12.75 s strictly between, 0.995+ at 13.7 s; the bracket is invisible before its word, mid-draw at +0.4 s with its label at 0, span drawn and every glyph at 1 by +2.0 s, y0/y1 exactly the two data's y, the span right of both data and the label stacked above the peak (no room beside on this page); the relight peaks at 1.000 mid-word and is 0 after; the retitle erases first glyph first (glyph 0 at 0 while the last is still > 0) with the new title unwritten, then old all 0 / new all 1; two browsers, one frame). Full suite (goldens, flag goldens, determinism, docks, E47, gate, idle): **144 passed in 131.59s** - every golden byte-identical. Found and fixed on the way: an empty caption-page list threw `PG[-1]` at load and skipped every later definition. The `dock_place` risk: the bracket lives inside the plot box, which the park already forbids - nothing to add. Tokyo v3 first pass authored on the species (T4): build_short.py rows 2/4/6.

### T3: The chart morph - ARAP, and the object → chart page enter
- Status: complete
- Owner: implementation_luna (architect_sol reviews the mesh design before the build)
- Depends on: T2 (the page's clock hooks)
- Write set: `content/video_engine/scripts/kinetics/arap.mjs` (new: triangulate two closed outlines to one topology, polar decomposition per triangle `J = R·S` in closed form for 2×2, local/global ARAP with cotangent weights, the Laplacian factored once, `det(J(t)) > 0` asserted), `sync_kinetics.py`, the template (the `morph` page enter: the object page's props morph into the chart's line/bars over `MORPH_S` `[DERIVED]`), `ledger_page.py` (the object page renderer where P38 T5 left it a spec; `--variant object` already validates), `build_scene_timeline_f.py` (`enter=morph`), `gate_motion_density.py` (the three invariants as a gate row `M17` `[DERIVED: briefs:390-396]`; a morph credited as motion), tests: `content/video_engine/tests/kinetics/test_arap.py` (new: a square → a rotated bar through 120° never inverts; centroid / axis / area invariants computed), `test_page_performs.py` (+ the morph frames), `CAPABILITIES.md`
- Acceptance: (1) on synthetic outlines the morph keeps `det(J) > 0` at every sampled `t` through > 90° of rotation where linear blending collapses (the test shows the linear case collapsing); (2) the bar tab (Tokyo's object page: the receipt) becomes the holdings line on "unfunded bar tab" as one continuous thing in the player (HG3); (3) M17 reports the three invariants per morph; (4) goldens byte-identical; the kinetics registry lists `arap` with its sources (Alexa 2000 / Sorkine & Alexa 2007, on file or "not on file")
- Validate: `python -m pytest content/video_engine/tests/kinetics/test_arap.py content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_render_determinism.py -q -p no:cacheprovider; python content/video_engine/scripts/sync_kinetics.py --check; python content/video_engine/scripts/build_docs_layers.py --check`
- Evidence: 2026-09-07 - `node --test` kinetics 57 pass (arap 9: the polar decomposition exact; a shape turned 150 deg vertex-locked collapses under the lerp to < 10 % of its area while ARAP keeps det > 0 on every interpolated Jacobian and every solved triangle; the strip on a jagged series never inverts where the fan flips at least one triangle; the invariants fail by name); `test_morph.py` 8 passed (browser on the soak golden: at u = 0.5 the tab is mid-morph, the invariants hold, det > 0, the end outline equals the target within 1e-3 and sits on the series or the axis within 1 unit, the fill leaves once the line is drawn; `measure_morph.py` writes and M17 reads PASS; with the flag off the frame is byte-identical to a mount). Full suite: **159 passed in 145.15s (node 57 pass)** - every golden byte-identical. **HG3 material:** `tokyo-tea-break/build-morph-demo/player.html` - the holdings page entering by morph from the tab on "unfunded bar tab" (v3 itself untouched): M17 PASS - centroid 0.1 % W, axis 0.0 deg, oriented area 0.69, min det 0.056; stills sent. Two things learned on the real page and built in: a fan from one centre flips 12 of 96 triangles on the holdings series (not star-shaped) - the strip mesh replaces it for area-under-a-series targets; the dominant axis by vertex covariance read a strip as vertical (its vertices sit in two rows) - the axis is the polygon's inertia now, and the bounding area is read in the target's principal frame. Deviation, stated: the object page renderer (P38 T5's spec, `ledger_page.py` `object` variant with registered props) is NOT built - the morph's source is a NAMED prop outline (tab | plate | card) drawn on the board, not a registered prop asset; the receipt as an image asset that morphs is a later slice. The morph shifts the build 3.7 s earlier than the mount did (it replaces the roll, the savor, the soak and the punch) - whether v3's hook takes it is the operator's call at HG3, and the shot table's build_to caps would move with it.
- **HG3, the operator's first read of the stills (2026-09-07):** *"the stills look really cool, we have to learn about the morphs, we can't have an overlay of a chart portion on the screen that doesn't exist for 3 frames just to pretend that we're holding on-screen continuity. I think the better thing would be to try and pull it off of the red tie at the last frame or two as the best bet, but I see the vision."* Read: the demo's source shape (the tab strip) is conjured over the outgoing clip during the world's dissolve - a thing that was never in the frame - which is exactly the lookalike E48 s4 forbids. The morph's SOURCE must be a real element of the outgoing world (the panelist's red tie), lifted at its last frame or two, and THAT becomes the chart. Not built; the follow-up is backlog R26-16. The demo stays as the proof of the mechanism, not of the seam.
- **T1 follow-up 2, the dials read onto the SOURCED report (2026-09-07, "proceed"):** `WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md` (repaired: 24 proof lines, 8 sources on disk) contradicted three of the four mechanisms built by eye the same morning, and they moved: (Q1) the hit's squash is ONE frame at 24 fps for a deformable inanimate thing and NONE for a rigid one, the contact frame itself uncompressed, released at once [source on file: Williams pp. 93-94, 263; Lasseter 1987; Whitaker & Halas 1981] - `MASS.*.squash_frames` (paper 1, ink 1, liquid 2 [DERIVED], metal 0) replaces the 5-step envelope; (Q2) the contact shadow's depth is its BLUR, sigma 16 px high to 0.8 px at contact, and its offset; alpha is the weakest cue [source on file: Kersten, Mamassian & Knill 1997 Dem. 6] - `contactShadow` returns `blur`, painted as `filter: blur()`, the alpha ramp narrowed 0.55->0.85; (Q3) a stage shake reads as violence, mass reads as the SURFACE dipping 2-6 px and settling in 4-8 frames [DERIVED in the report] - `groundDip(ts, mass)` (`DIP_PX` 4 x impact: metal 6, paper 2.8; the material's own spring brings it back - metal recovers dead at ~7 frames, paper flutters 5.8 % past) replaces `groundShake` on the world layer, which stays as an opt-in (`{"violent": true}` on the dock) for a hit that IS violent; (Q4) a heavy mass has no pre-contact deceleration [source on file: Whitaker & Halas p. 30] - the throw's chord is now linear (ballistic: the last tenth of the flight covers a tenth of the chord; min-jerk gone from the flight), the object no longer sinks into the surface (`IMPACT_PX` deleted - invented), it RIDES the dip; restitution `MASS.*.e` (h1 = e^2 h0, a parabola under `G_PX_S2` 2400 [DERIVED]) as `rebound()`, tagged [UNVERIFIED: Warren 1987 not on disk], paper 0.15 / ink 0.1 / metal and liquid 0; (Q5) the landing SOUND lands on the contact frame or one frame early, never two ahead [source on file: Williams pp. 263, 309-311] - `build_short.py` writes a `landing N (arrive, mass)` cue per dock arrival at contact - 1/24, the contact read from `stopaction.mjs`'s own dials (`stop_dials()`, a throw's contact on the stepped clock's frame ceil(FLIGHT_S x 24)); the file is the documented quiet page turn for both (fs-riserhit-754771.mp3 sits in the folder with NO provenance line in sound/SOURCES.md and is not used; a documented hit file for metal is still to find). Damping presets confirmed by the report (dense = critically damped, no overshoot: metal zeta 0.88, ink 0.98). Tests: `stopaction.test.mjs` 11 pass (the contact frame uncompressed, the one squash frame, a rigid thing never squashes, the blur ramp 16->0.8, the dip's overshoot by material, the dip settled within 8 frames, e^2, no shake by default, the ballistic tail); `test_stop_action.py` 7 pass (browser: the shadow's blur 16 px in flight -> 0.8 at the hit, the world DIPS vertically on the hit frame - "translate(0px, 2.78px)" - and is still after). Tokyo v3 rebuilt: gate VERDICT PASS (0 FAIL), M18 re-measured (1066 frames, no identical run), M20 the two arrivals, the two landing cues at 9.51 s (throw, paper; contact 9.55) and 36.86 s (land, metal; contact 36.90). Stills (this session's scratch `v3-hg2-stills/`): the panel's one squash frame, the shadow a 16 px blur in flight and a slit at contact, the two fingers with no squash while the ground takes 6 px. Full engine suite: **1708 passed / 59 failed (the two pipeline modules ignored: pre-existing collection errors) - 57 of the failures are outside this change and pre-date it (finance-whiteboard proofs on missing generated deck assets, production console 409s, audio_synth's `duration_s`); the other 2 were `test_kinetics_sync.py`'s own MODULES list, stale at five since T5 - now the eight modules, 8 pass**. Not done, stated: the numbers are still for the operator's ear (the second watch on :8731); the report's "+6 to +12 dB" for a hit is a doctrine line, not our measurement - the cue gain stays at ACCENT 0.12.
- **HG2 second read, v3 on the sourced dials (2026-09-07 evening):** *"We have to sync up on the details ultimately but especially considering that you're cutting this from prior footage and not from scratch, I see the potential. One thing is we're leaving the chart up for too long. We should un-draw it or morph it into something else after it's been fully deployed for 6-8 seconds, depending on what the scene calls for - in this scene we start talking about the treasury number, we could reverse the draw / transform the graph into the treasury."* Read against the clock: the line caps at the February peak at ~7.4 s, draws its June stroke on "watching:" (19.7), is spotlit on "our biggest lender" (20.3), called out on "over a trillion" (23.0), retitled on "The opponent" (32.5), and is cut on "went:" (38.96) - fully deployed for 19 s after its last stroke, 30 s after its first cap. The rule, RULED the same hour as E50 (the operator: *"6-8 seconds FULLY DEPLOYED ... after the final point in time the chart uses its last data point/series. Maybe 12 seconds is a better max with 6-8 seconds average. This allows for the chart to stay still while a video plays in a dock"*): **the clock starts at the last data mark; 6-8 s on average, 12 s at most; then un-draw or become the next thing.** On that clock v3 reads: row 2 18.9 s (last mark the June build_to at 20.1, cut 39.0), row 4 12.7 s (the bracket at 49.1, exit 61.8), row 5 6.6 s, row 6 5.0 s - rows 2 and 4 are over the ceiling. Gate spec: > 8 s INFO, > 12 s WARN, annotations without data do not restart the clock. Two mechanisms: (a) UN-DRAW - the line unwinds from its tip back to a datum or to nothing, the reverse of `build_to` (today `build_to` is `Math.max`-guarded: a cap to an earlier datum never retracts - a new page species `undraw`, an afternoon); (b) MORPH - the line's ink becomes the treasury figure (R26-16's mechanism, the ARAP strip into a glyph shape, planted). Proposed cut for this scene, the details for the sync: on "The Treasury's table shows" (20.9) the line un-draws from June back to the origin over ~1.2 s and the ink lands as the figure **$1,239.3B** (the February peak, `facts.peak`) written by the hand at the peak's spot on "over a trillion" (22.5); "selling since February" (24.4) writes the June figure **$1,116.7B** beside it (`facts.latest`); the two figures hold under the JPMorgan anecdote and take the retitle at 32.5 and the two fingers at 36.6; the cut on "went:" stands. Not built; backlog R26-18.
- **HG2 second read, part two (2026-09-07 evening):** *"we also show the same chart a couple too many times, there has to be another one that we can pull in of value."* The holdings page carries rows 2, 4 and 6 (2-39 s, 45-62 s, 74-80 s) - three deployments of one line; only row 5 (the Meta yield bars) is a second chart. Read against the script and the dossier: the HOOK's claim - "The Fed hasn't moved, but your borrowing costs climbed anyway" (6.5 s) and its ring "The Fed still hasn't moved" (74-76 s) - is sourced in `EVIDENCE-DOSSIER.md` (30-year mortgage 6.55 % on 07-16 -> 6.71 % on 09-03; 10-year 4.63 % on 08-04 -> 4.79 % on 09-01; FRED `MORTGAGE30US`, `DGS10`) and was NEVER charted. That is the chart of value: the Fed's target flat (FRED `DFEDTARU`) against the 10-year and the 30-year mortgage rising over the same window - a two-line page, the flat line and the climbing line, sign as geometry (E28). Where: row 6, the ring (74-80 s) - "The Fed still hasn't moved" draws the flat line, "Tokyo is still on its tea break" holds it, "that unfunded bar tab is still ours" is the callout - in place of the holdings page's third return; row 4 keeps the holdings for the -$122.6B bracket and "a tenth of the pile". Second candidate for "Tokyo has pledged ten trillion yen to chips, and if that works, it beats our bonds" (54.6-58.4): the JGB 10-year against the UST 10-year (MoF Japan / FRED) - a fetch, not on disk. Third option, no fetch (operator, same read: "or even just a different display method, or a comparison of it"): the holdings object's own `facts` already carry the comparison - Japan $1,116.7B against the UK $939.9B and China $633.4B (`rank_2_uk`, `rank_3_china`), the -$122.6B as a tenth of the $1,239.3B pile (`drop_bn`, `peak`, `share_pct` 12.0) - so row 4's "a tenth of the pile" can be a BAR page (the `ledger_page.py --variant bars` form the Meta page already uses) and row 6's ring a COMPARISON (the three holders), the same sourced object shown two more ways instead of the same line three times. Not built; backlog R26-19 (the fetch is a bridge `fetch` order or our own FRED CSV pull; the object is a `meta_yield()`-style builder writing `ev-fed-vs-yields-v1.series.json` with its proof lines).
- **HG1 / HG2 / HG3, the operator's reads (2026-09-07, from the players on :8731 and :8733):** HG1 - *"the only thing that is bad is the dock at 0:16 is useless, that's the tea clip but at that point we're not talking about tea. No, nothing reads as drift."* The tea dock on "sixty-three" is removed (the panel holds parked through the joke, retracts on "watching" - part B row 4 as written); E49's idle CONFIRMED by eye: nothing reads as drift. HG2 - *"The throw comes on, but it doesn't land with much weight/impact, no shadow coming in, and doesn't feel like it has density/weight on the landing, but it's a cool effect still, I don't know if it's dials missing, the nature of the fact that we have animation and other things on screen, or the dials ... check against our math/research."* Diagnosis against the reference (HyperFrames stop-motion-cadence, headline-slam - pulled verbatim) and our research (48 s48.6; the floating-sticker rule): FOUR mechanisms were missing, not dials - (1) no CONTACT SHADOW (ours was the card's own drop shadow, present in flight; the reference pins a ground shadow to the landing spot that grows and darkens as the thing nears the floor); (2) the impact squash lived two frames, speed-driven (the reference holds a 5-step envelope on the stepped clock, about the ground contact); (3) nothing RECEIVED the weight (the reference's landing shakes the stage for three frames); (4) mass only shaped the settle. Built the same morning as T1's follow-up: `impactSquash` (the stepped envelope x the material's `impact`), `contactShadow` (0.55->1.05 scale, 0.25->0.85 alpha by height, spread by the hit), `groundShake` (three frames on the world), `.dock.arriving` squashes about its base; `MASS.*.impact` paper 0.7 / metal 1.5 / liquid 0.5 / ink 1.0 - all `[DERIVED]` dials for the ear. The research brief for the numbers: `docs/research/motion/BRIEF-WEIGHT-DENSITY-MASS-2026-09-07.md` (the operator offered to run it). HG3 - *"it reads but not effectively, we have to see it on the tie because they're the same color, but I think it's going to be a tough sell without building something into every scene that allows it. I also think you can't do it on a mount like that, it's too long of a duration that the morph is there."* Read: the morph's source must be PLANTED in the outgoing scene (a scripting and asset discipline, E48's one thread - every scene that hands to a chart carries the element that becomes it), and the morph must be SHORT - a seam's length, not a 2 s mount; not on a mount at all. R26-16 amended. v3's hook keeps its mount.

### T4: Tokyo v3 - the cut ledger applied and the page choreography authored
- Status: running
- Owner: parent (authoring is judgment), junior_developer for the shot-table edits
- Depends on: T2 (first pass), T1 and T3 (second pass)
- Write set: `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py` (the shot table + species), `sound/SOUND-PLAN.json` (cues follow the new arrivals: a throw's landing gets the press cue's successor at the E44 gain), the build outputs
- Acceptance: part A's operator column applied (the cuts that add nothing removed, the two misplaced moved, the callout datum fixed); part B authored on the real species; motion gate PASS; the operator watches in the player (HG1) before any render; the analytics read of the next post is recorded against v3's scene list
- Validate: `python build_short.py` from the project folder; `build-short/GATES-MOTION.md` VERDICT PASS; the player served on :8731
- Evidence: 2026-09-06/07 - two passes authored on the real species in `build_short.py` (rows 2/4/6): pass 1 (after T2) the line builds to the February peak and the coral drop draws on "watching:", the title rewrites to "The opponent: a balance sheet" on "The opponent" and rides the returning pages, the bracket "-$122.6B / a tenth of the pile" draws on "a hundred and twenty-two billion", stands on the ring and is re-lit on the second "unfunded bar tab"; pass 2 (after T1) the panel THROWN on "Three men" and the two fingers LANDED (metal) on "Two numbers", the host by the spring. Gate PASS (0 FAIL / 1 WARN - the pre-existing sound cue), M18 measured on the rebuilt player at 12 fps (1066 frames, no identical run), M19 lists the build_to hold 0:10+8.3s, M20 the two arrivals. v2 preserved as `build-short.v2/` (and the pre-E49 build as `build-short.v2-pre-e49/`). The player is served on :8731 from the main checkout, UNRENDERED. NOT done, stated: part A's operator column is empty (no cut of the ledger applied - the cuts that add nothing were the parent's draft, never ruled); the SOUND-PLAN carries no cue for the throw's landing yet; the morph (T3) is a separate demo player, not v3's hook. HG1 / HG2 / HG3 are one watch: the operator opens :8731 (and build-morph-demo/player.html), rules on the cut ledger, the throw and the landing by eye, and the morph's shape; then the render.

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
