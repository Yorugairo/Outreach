---
id: P49-THE-CAMERA
title: The camera as a first-class component of the physics - the eye in the world
status: complete
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-08
updated: 2026-09-10
---

# The camera as a first-class component of the physics

## Summary

The operator, 2026-09-08, on the tariff short's chart arrival: *"We've added almost everything to our production
process except a truly first class viewer/camera perspective. Our engine, and also you therefore, don't know what it's
seeing until it's rendered back essentially. We need to add the camera as a first class component of our physics. It
wouldn't make sense that the card lands, and then grows. It would make sense that as the card came into view, our focus
shifted, and we went to see what that card was. We've talked a lot about 'building the world' - and forgot to make the
eyes a first class part of it."*

**This is an integration gap, not a knowledge gap** (the operator: *"refer to our documents, we added research on
cameras and components; it's not that we neglected to know the importance, it's that we didn't fully integrate"*). The
record holds the camera four times over, and the scene-evidence player integrated three species of it:

- **Doc 16 §4 (the editorial lane's camera contract, P13):** *"A moving shot must name a focal point, use a bounded
  amount, and declare hold, movement, and settle phases"*; camera actions `locked | push-settle | pull-settle | lateral
  reveal | foreground parallax | cut-on-motion`; the plan contract binds focal point, shot scale, camera phases; *"a
  locked shot has zero camera amount"*; QC scores camera stability and focal clarity. That contract runs in the Remotion
  editorial lane and never crossed into the scene-evidence player.
- **The research brief C3 (Tier 1, CLOSED):** `M_world = M_viewport x M_camera x M_ledger x M_chart x M_local`; **doc 43
  §43.2-43.4:** `p_screen = M_camera x M_world x p_local`, the anchor sandwich, the Z-stack, and `X_proj = X·f/(Z+d)` -
  *"a small camera drift produces parallax with no shader at all"*. **D1:** eye-trace - a 260-330 ms fixation, 180-220 ms
  search latency after an abrupt transition, the 15 deg cone (R <= 260 px between consecutive focal items).
- **The HyperFrames blueprint (2026-09-06):** *Rule 2 - the camera is an actor* (a continuous 4-8 % push, an orbital
  pan or a parallax translation, never decaying to a dead stop at a boundary); *the dwell-and-sweep rhythm* (sweep
  between beats, a genuine 1.5-2.5 s dwell at each hero moment while the world keeps resolving); *Rule 6* parallax
  ratios 0.20x / 1.00x / 6.00x by depth; **doc 24** ships the depth planes those ratios need.
- **The weight blueprint Q3:** a camera shake reads as violence, never mass - the receiver dips (built: `worldAnswer`).
  The camera must not be used to sell weight.
- **remotion-ui, harvested:** `zoom-pan-frame` (a camera move on a still DRIVEN BY FOCAL POINTS, settling before the
  cut), `zoom-through` (the push-through cut with a velocity-envelope blur), `bento-pan`. Mechanisms port; code does not.

What the player has: `camXf` (template:4010) - three one-shot species (`punch`, `focus_zoom`, `pull_back`) that borrow
the stage for a window and hand it back, applied to the plate-life layer and per element. No persistent state, nothing
composes through it, nothing can ask "what is in frame at t". Every arrival built this week (throw, hop, stamps, snap)
had to move the OBJECT because nothing else could look at it - the operator's read: *"It wouldn't make sense that the
card lands, and then grows. It would make sense that as the card came into view, our focus shifted, and we went to see
what that card was."*

## Amended 2026-09-10 - after P48 (a chart changes state) and Bravos's camera, MEASURED

The operator, 2026-09-10: *"how does P49 change with our new capabilities & after watching bravos? they did a lot of
camera stuff."* Measured before answering (E38: the threshold comes from the reference), on the source video in the
dossier (`claude-watch/camera.json`; `measure_bravos_camera.py` in the session scratchpad - ORB + RANSAC partial affine
between frames 2 s apart, 640x360, per held composition of the Claude shot ledger, three samples each, the median):

| held compositions >= 3.2 s | n | camera-still (< 0.15 %/s zoom and < 4 px/s pan) | pushes > 0.3 %/s | pans > 8 px/s |
| --- | --- | --- | --- | --- |
| charts | 12 | **11** | 0 | 0 |
| diagrams | 4 | 4 | 0 | 0 |
| cards / press | 9 | 8 | 1 (the press collage, +1.25 %/s over ~10 s) | 0 |
| maps | 10 | 6 | 1 (#68: +0.6 %/s, then a ~6 %/s push between countries) | 3 |
| other (icon boards, CTA) | 10 | 8 | 0 | 2 (icon boards sliding) |
| **all** | **45** | **37** | 2 | 5 |

**What "a lot of camera stuff" is, measured: it is not the camera.** 37 of 45 held compositions are camera-still, and
every chart and every diagram is - the line draws, the tag lands, the bar stamps under a LOCKED camera. The motion the
eye reads is 6.0 events/min of builds inside a held frame and 2.5 compositions/min of cuts (46 §46.7). The camera moves
in exactly two places: on the MAP, where the stage is wider than the frame (a push or a pan between countries, once per
composition, then still), and a slow push on a press collage that stacks. So:

1. **The default is LOCKED, and it is the reference's default, not a fallback.** Doc 16's *"a locked shot has zero
   camera amount"* is Bravos's practice on every chart. The HyperFrames rule 2 (*"a continuous 4-8 % push"*) is REJECTED
   as a default: zero of twelve chart holds carry one. T4's attention law is re-scoped: the camera holds while a thing
   builds (the build leads the eye - E50's amendment), and moves only (a) tied to a landing (E51, already the law for
   `punch`), (b) between focal points on a stage wider than the frame - the map, a wide diagram - as ONE move per
   composition that settles, (c) as an authored key. "Attention drives the camera" stays the operator's decision; what
   attention means is now measured: it moves the eye to a NEW composition, it does not drift on a held one.
2. **P48 took the object-moves-for-the-eye cases away.** `park` (the chart shrinks to a corner so the next thing has
   room - Bravos 91), `rescale`/`extend` (the axes retarget instead of a push-in on a window), the keyed recast and
   `morph_to` are all "the world moves under a locked camera" - which is what the reference does. The plan's Rejected
   Alternative ("the object grows because nothing could look at it") is narrowed: `snap` and `throw` stay as arrivals;
   the chart's own changes of state are NOT camera work and P49 must not re-implement them as pushes.
3. **T3 (the probe) and T6 (the in-frame gate) gain a customer:** after a `park` or a docked card beside a parked chart
   (the Tokyo cut, "Two numbers") the engine needs to know what is in frame and what is covered - `__camera(t)` +
   `inFrame(target)` should read the park's transform and the docks' `place`. This is now the first slice worth building,
   before any camera MOVE: it answers "is the card over the chart" at compile time, which the operator has asked three
   times by eye.
4. **T5 (the camera arrival) stays opt-in and behind HG2**, and the reference argues against it: Bravos brings a new
   composition in by a CUT (2.5/min) or a build, never by the eye travelling to a card. The operator's read (*"as the
   card came into view, our focus shifted"*) is still the ask; the measurement says build it as a short, settled move
   (a push-through of 1-2 s, blur riding the velocity), watched against `snap` on the same beat - not as the default.
5. **T7's record** carries this table; E54 in the plan's write set is now E59 (E54-E58 exist).

The revised order: **T1 -> T2 -> T3 + T6 (the probe and the gate, the value P48 exposed) -> T4 (locked by default; the
map/wide-stage move; the landing tie) -> T5 (opt-in, HG2) -> T7.** Approved to run by the operator's `/prp-implement P49`
(2026-09-10: *"let's see how it changes the play through"*).

## Intent And Acceptance

**Intent.** One persistent camera per timeline - position, zoom, (later) tilt - with its own kinetics and its own
attention law, through which every world-space thing is composed, and which the engine can interrogate before a frame is
rendered.

**Acceptance.**
1. `world.camera` state exists at every t as a pure function of the timeline (C6: `State(f) = SceneGraph(t)`), and the
   player composes worlds, docks, species and page through it; captions stay in screen space (Z5).
2. A probe `window.__camera(t)` returns the frustum in stage coordinates and, for any declared target, whether it is in
   frame and at what on-screen scale - the engine knows what it is seeing.
3. **The attention law**: a LANDING (a dock's `arrive`, a thrown card, a page's badge) pulls the camera's focus toward it
   by the servo law already in `focus_zoom` (zoom + pan to the anchor, then dead still) - E51's "a push is tied to a
   landing" becomes the camera's default behaviour, not an authored species.
4. **The camera arrival**: a chart that arrives as a card no longer grows (`snap`); the camera goes to it. When the
   frustum matches the card's rectangle (the graphic-match invariants from the ARAP research: centroid <= 0.06 W, axis
   <= 15 deg, area ratio >= 0.60, exact at the switch), the world switches to the ledger page with no visible seam - the
   match cut we said was ours alone, delivered by the camera.
5. Goldens byte-identical: the camera defaults to identity; every new behaviour is opt-in until a ruling makes it the
   default.
6. Gates: M09 / M14 read the camera track, not species windows; a new row (M24) checks that every declared target of a
   pointing species is IN FRAME when it fires (the engine knows before render, not after).

## Scope

- A `camera` object on the timeline (per scene, keyframed, or derived), with kinetics: min-jerk for rest-to-rest
  (42 §42.2), the servo law for attention, a settle after every move.
- The player: one `M_camera` applied at the world root; the existing three species become authored camera keyframes.
- The probe and the gate row.
- The card-arrival replacement on the tariff short's two chart pages (the first use).

## Not Building

- 3D. The camera is a 2D similarity transform (pan, zoom) with doc 43 §43.3's Z-parallax as the only depth cue; tilt is a
  later slice.
- A generative camera (the Flow/Omni prompts' "locked tripod" rule is that lane's, doc 53).
- Re-authoring the mounted pages (parts, selling, customs): the mount is a build, not a camera event.

## Human Gates

- HG1: the attention law's dials (how far the eye travels toward a landing, how fast, how long it rests) - tuned by eye
  on the tariff short's hook, the operator's word.
- HG2: whether the camera arrival REPLACES the snap for every chart card or stays opt-in per page.
- HG3: whether captions ride the camera (they do not, by default - Z5 is screen space).

## Mandatory Reads

- `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md` §4 (camera actions, the focal point / amount / phases
  contract) and §5 (the plan contract's camera fields) - the contract to INTEGRATE, not re-derive
- `docs/research/motion/HYPERFRAMES_MOTION_TRANSITIONS_RESEARCH_BLUEPRINT.md` Rule 2, the dwell-and-sweep rhythm, Rule 6
- `docs/research/motion/WEIGHT_DENSITY_MASS_RESEARCH_BLUEPRINT.md` Q3 (camera shake = violence, never mass)
- `docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md` (depth planes, `parallax_factor`)
- remotion-ui `zoom-pan-frame` and `zoom-through` (via the MCP: `get-component-detail`) - the focal-point drive and the
  velocity-envelope blur, as mechanisms

- `docs/content-video-engine/briefs/ANSWERS-RESEARCH-BRIEF-animation-craft.md` C3, C6, D1 (eye-trace, the 15 deg cone)
- `docs/content-video-engine/43-SCENE-GRAPH-AND-TRANSFORM.md` §43.2-43.4
- `docs/content-video-engine/42-DRAWING-KINETICS.md` §42.2 (the settle), the FINDING doc §3 (min-jerk)
- `docs/portable/OPERATOR-RULINGS.md` E47, E48, E50 (amended 2026-09-08, the throw/snap ladder), E51
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §8.14 (the camera lock does NOT apply to this lane), §9.27
  (one camera move per window), §9.28 C3/C4
- `docs/content-video-engine/samples/scene-evidence-player.template.html` `camXf` / `camCss` (template:4010-4031), the
  species loop, `worldAnswer` (the ground's answer - the only place today where the world reacts to a landing)
- `content/video_engine/scripts/gate_motion_density.py` M09, M14
- `frontend-patterns` (the player is DOM/SVG; seek-exact, no async)

## Execution Path

1. **T1 the model** - `camera` on the timeline: `{keys: [{t, cx, cy, zoom, ease}], attention: {...}}`; the compiler
   emits identity when nothing is authored; `build_scene_timeline_f.validate_camera`.
2. **T2 the root transform** - the player composes wA/wB/docks/species through `M_camera` (one CSS transform on a world
   root, the anchor sandwich of 43 §43.2); `punch` / `focus_zoom` / `pull_back` re-expressed as keyframes on it, pixel
   identical on the goldens (a flag guards the new path until proven).
3. **T3 the probe** - `__camera(t)` (frustum, in-frame test, on-screen scale of a target); the tests' fixture.
4. **T4 the attention law** - landings pull focus by the servo law; dials `[DERIVED]`; E51 becomes default behaviour.
5. **T5 the camera arrival** - the card lands, the eye goes to it, the frustum meets the card's rectangle, the world
   switches on the match: `enter=camera=<dock>` beside `snap`; the tariff hook and receipt pages take it.
6. **T6 the gate** - M24 in-frame; M09/M14 read the camera track.
7. **T7 the record** - E54 (the ruling the operator gave above), doc 29 §9.27 amended, CAPABILITIES row, the choreography
   ledger's arrives column.

## Patterns To Mirror

- The stop-action mechanics (P47 T1): kinetics live in `content/video_engine/scripts/kinetics/*.mjs` and are inlined by
  `sync_kinetics.py` - the camera's kinetics go in `kinetics/camera.mjs` the same way.
- `worldAnswer` (template): the one existing "the world reacts to a landing" - the attention law is its camera-side twin.
- `snap` (P47 T7) for the world switch on a card's rectangle; the ARAP invariants (brief B, `:390-396`) for the match.
- Opt-in flags + byte-identical goldens (P48, every capability this week).

## Task Slices

### T1: The camera model on the timeline
- Status: complete (2026-09-10)
- Owner: parent (built with T2/T3 - the model's shape is the player's)
- Depends on: none
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/test_camera.py`
- Acceptance: a timeline with no authored camera carries identity keys; an authored key list validates (monotonic t,
  zoom > 0, ease in the kinetics set); the three camera species compile to keys with the same numbers `camXf` produces.
- Validate: `python -m pytest content/video_engine/tests/test_camera.py -q`
- Evidence: (2026-09-10) a shot row's optional 8th element `{"keys": [{t, zoom, look, at?, ease?}], "attention":
  "locked"|"landings"}`; `look`/`at` as stage fractions or a declared target (resolved by the player at load);
  `validate_camera` names every fault (ascending t, zoom > 0, the ease set, the attention set, a target's own errors);
  `validate_camera_row` refuses keys and a camera species on one row (s9.28 C3); every compiled scene carries `camera`
  (identity `{keys: [], attention: "locked"}` when nothing is authored); `build_kinetics` turns `camera` on. Deviation:
  the species do NOT compile to keys - a datum target resolves only in the player (its page geometry), so the species
  stay species and the PLAYER routes them through the one camera (T2); the numbers are the same by construction.

### T2: One camera transform at the world root
- Status: complete (2026-09-10) - the root is LOGICAL (one state per frame), not a DOM wrapper: see the deviation
- Owner: parent
- Depends on: T1
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`, `content/video_engine/scripts/kinetics/camera.mjs`, `content/video_engine/scripts/sync_kinetics.py`
- Acceptance: behind `kinetics.camera`, worlds/docks/species compose through `M_camera`; with the flag off the goldens
  are byte-identical; with it on, the three species render pixel-identical to today on the tariff short's frames
  (measured by `measure_frozen_frames.py`-style hashes on the affected windows).
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and the window hashes
- Evidence: (2026-09-10) `kinetics/camera.mjs` (synced into the template after chartxf): `camSpeciesState` (the three
  envelopes factored UNCHANGED), `camKeyState` (keys: identity before the first, lerp by the arriving key's ease, hold
  after the last), `camCssFor` (a zoom in place writes the byte-identical string the player always wrote; a pan takes
  `translate(t) scale(s)` with t = at - s*look - (1-s)*O), `camFrustum`, `camInFrame`, `camProject`. The player:
  `camNow(sc, t)` (behind `kinetics.camera`; keys win when authored, else the species window, else identity) feeds the
  same two call sites `camXf` fed (plife, the world element). **Pixel-identical, measured:** a punch, a focus zoom and a
  pull-back on the golden page, flag off vs on, 11 instants - the same transform string and the same frame hash at each.
  13 goldens byte-identical. Deviation, stated: no DOM wrapper - the same string on the same three elements IS one
  transform, and a wrapper would risk sub-pixel drift for nothing; docks stay in screen space (doc 29: the drawing
  surface), so "docks compose through it" is NOT done and is HG-level (the plan's acceptance 1 is met for worlds, plate
  life and species; docks are a ruling to take, not a slice).

### T3: The probe - what is in frame
- Status: complete (2026-09-10)
- Owner: junior_developer
- Depends on: T2
- Write set: template (`window.__camera`), `content/video_engine/tests/test_camera_probe.py`
- Acceptance: `__camera(t)` returns `{frustum: {x0,y0,x1,y1}, zoom}` and `inFrame(target)` with the on-screen scale;
  a target off frame at t reports false.
- Validate: `python -m pytest content/video_engine/tests/test_camera.py -q` (the probe's tests live with the model's)
- Evidence: (2026-09-10) `window.__camera(t, target?)` -> `{scene, on, zoom, look, at, frustum{x0,y0,x1,y1}, target:
  {inside, visible, scale, box, screen}}` - the frustum in world (pre-camera) stage px, a target's visible share, its
  on-screen scale and where it lands. Measured on the punch's hold: zoom 1.14, the frustum 1080/1.14 x 1920/1.14 inside
  the stage, the punch's own target inside, the far corner out and projecting off screen; identity before the window.
  `test_camera.py` 14 (the model 11 rows, the pixel identity, the probe, authored keys pan+zoom+hold+seek);
  `kinetics/camera.test.mjs` 6.

### T4: The attention law
- Status: complete, LOCKED by default; the landings pull is opt-in per row - HG1 CLOSED by the operator's watch (2026-09-10: "8742>8738", the dials stand as derived)
- Owner: parent
- Depends on: T2, T3
- Write set: `kinetics/camera.mjs`, template, `docs/portable/OPERATOR-RULINGS.md` (E54)
- Acceptance: a dock landing pulls focus toward it by the servo law and settles; dials `[DERIVED]`; HG1 by eye on the
  tariff hook.
- Validate: rendered frames at the landing and the settle; `gate_motion_density.py` M09/M14 PASS
- Evidence: (2026-09-10) the default is `attention: "locked"` - Bravos measured (37 of 45 held compositions still, every
  chart and diagram): the camera does not move on a held thing. `attention: "landings"` on a row: `camAttentionState`
  (kinetics/camera.mjs, `ATTN = {SCALE 1.06, IN 0.5, OUT 0.6}` [DERIVED: Bravos #68's map push ~6 % between countries])
  - a dock that ARRIVES (throw | land) with a parked `place` pulls the eye by a zoom in place about its box, in over
  ATTN.IN from the CONTACT frame (the stop-action clock: a throw's FLIGHT_S 0.45, a landing's ANTIC_S + DROP_S 0.32 - the
  push is tied to the landing, E51), held while the card is up, released over ATTN.OUT before it leaves; the last landing
  wins. The compiler refuses attention landings with a camera species on one row; the gate mirrors the dials: M09
  clashes attention + a species, M14 counts the pull as a move that is EXEMPT against its own dock's build (the tie) and
  clashes with any other build, M24 evaluates the pull's frustum. Measured in the player: identity until the contact
  frame, 1.06 about the card's centre at contact + 0.5 s, held at 9.0 s, releasing at exit - 0.3 s, identity after; a
  locked row with the same dock moves nothing. HG1 (the three dials by eye on a real landing) is open - the tariff hook
  and the Tokyo fingers are the candidates; nothing ships with landings on until the operator's word.

### T5: The camera arrival (the card becomes the world by the eye going to it)
- Status: complete, opt-in beside `snap` - HG2 CLOSED by the operator's watch on the Tokyo short (2026-09-10: "8742>8738" - the arrival is the ring's entrance in the Tokyo cut; the tariff's approved cut keeps its snap until re-cut)
- Owner: parent
- Depends on: T4
- Write set: template, `build_scene_timeline_f.py` (`enter=camera=<dock>`), `japan-tariff-trick/build_short.py`
- Acceptance: the hook page's card lands; the camera goes to it; at the match the world is the ledger page with no
  seam (the ARAP invariants exact at the switch); the whoosh rides the camera's speed; M11 reads the card as the page's
  own preview (already true for snap).
- Validate: rendered frames across the arrival; goldens; the gate 0 FAIL
- Evidence: (2026-09-10) `enter=camera=<dock>` (`LEDGER_ENTERS`; the page's `snap_from` as for a snap). The card lands on
  the previous scene as today; then over SNAP_S the EYE goes to it: `camArrivalState` (kinetics/camera.mjs) looks at the
  card's box and carries it to the stage's centre while zooming to the fill scale (min-jerk, the whoosh on the snap's
  own velocity envelope on the outgoing world and the card); the outgoing world rides the arrival (`camNow` returns
  the arrival for that scene), the card rides it as a prefix composed BEFORE its own transform about its own
  transform-origin (a thrown card's is its bottom edge - the first cut scaled about the centre and the card climbed 250
  px off the top at the match), the page waits hidden and shows at the match, at identity; the card hides on the SAME
  predicate the page shows on (a second clock put one bare frame of world between them - the scrub's 10 ms step). The
  card's box is its parked `place`, else its LAYOUT box (left/top/width from the solo CSS, the height from the image -
  untouched by transforms), else the recorded rect. The compiler extends that card's exit to the arrival's end
  (`extend_camera_cards` - it fell out of the dock list 5 ms before the match). M14 exempts the arrival against its own
  card (E51). **Measured on the tariff hook** (`build-short-p49`, `TARIFF_BUILD_DIR` + `TARIFF_CHART_ARRIVAL=camera`,
  the approved build untouched; `japan-short-player-p49` on :8741): the card's rect at the match [5, -9, 1071, 1928] -
  the stage to within the card's 1.3 % aspect mismatch; consecutive frames inside the arrival differ by a mean |delta|
  of 0.2-10 (motion), the match frame to the page by 18.5 (the card is a 758 px rendering of the page scaled 1.33 -
  its softness and its cream border against the live page's crisp ink and deckle). That residual is the seam HG2
  judges; the snap has the same. Cold-seek limitation, stated (R26-21's class): the first frame after a cold seek INTO
  the arrival window reads the card's layout before the dock loop lays it out and skips the arrival for that frame -
  sequential rendering is exact; the renderer's shards start at scene boundaries or hold frames.
  `test_camera.py` 20 (+4: the eye goes to the card and the world switches at the match; the compiler admits
  enter=camera and the gate ties the arrival; the compiler keeps the card up to the match); goldens byte-identical.
  HG2 material: `frames/tariff-hg2-sheet.png` (1.62 / 1.94 / 2.07 / 2.20 / 2.26 / 2.27 / 2.30 / 2.82 s).

### T6: The in-frame gate
- Status: complete (2026-09-10)
- Owner: junior_developer
- Depends on: T3
- Write set: `content/video_engine/scripts/gate_motion_density.py`, `docs/GATES-REGISTRY.md` (generated), tests
- Acceptance: M24 FAILs a pointing species whose target is out of frame when it fires; M09/M14 read the camera track.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: (2026-09-10) `_camera_key_segments` (a key segment that changes zoom, look or at is a camera move; a `hold`
  key is a step credited CAMERA_MOVE_S); M09 clashes keys + a camera species and keys over Ken Burns; M14 checks key
  segments against the build windows ("camera keys 4.0-7.0s over dock-x build"); **M24**: for every pointing species on
  a scene with keys, the camera's state at `at` is evaluated the way the player evaluates it (`camera_state_at`: identity
  before the first key, lerp by the arriving key's ease, hold after) and the target's world box (point, region; a datum =
  the page's plot from `page_boxes`; a span is not a box) must be fully in the frustum - FAIL names the species, its
  target kind, the visible share and the zoom; no row without keys (the identity camera frames everything). 65 gate
  tests (+3). Found on the way: `build_animation_registry.code_status` passed names where rows were expected (a latent
  unpack error, first hit by an export nothing called) - fixed at the call.

### T7: The record
- Status: complete (2026-09-10)
- Owner: parent
- Depends on: T5, T6
- Write set: `docs/portable/OPERATOR-RULINGS.md`, `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md`,
  `docs/content-video-engine/CAPABILITIES.md`, `japan-tariff-trick/CHART-CHOREOGRAPHY.md`, the docs layers
- Acceptance: E54 carries the operator's words; §9.27's "one camera move per window" is restated for a persistent camera;
  the layers regenerate in sync.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --write`
- Evidence: (2026-09-10) **E59** in `docs/portable/OPERATOR-RULINGS.md` - the operator's words of 2026-09-08 and the
  three settled decisions, the Bravos measurement, the ruling (one persistent eye, LOCKED by default; the four reasons it
  moves: a landing, a wider stage, the arrival, the three species; the nevers: a drift on a held chart, weight, a move
  over a build, two moves, captions, and - until ruled - docks; the laws). Doc 29 §9.28 C3 restated for the persistent
  camera. CAPABILITIES: the camera rows (the model + probe; the arrival + the attention law). The tariff choreography
  ledger's arrives note (snap in the approved cut, camera in the side build, HG2 decides). The docs layers regenerated.
  The plan stays `running` on the two human gates: HG1 (the attention dials by eye), HG2 (does the arrival replace the
  snap); HG3 is closed by the operator's word (captions do not ride). Docks riding the camera is a ruling to take, not a
  slice (stated in T2). E54 in the original write set is E59 (E54-E58 were written between).

## Decisions - SETTLED by the operator (2026-09-08)

1. **Attention drives the camera by default; authored keys override.** (*"attention drives the camera by default with
   authored keys overriding"*)
2. **The camera arrival stays opt-in** beside `snap` until it has been watched. (*"camera arrival stays opt-in for now,
   has to be tested"*) - HG2 stays open.
3. **Captions do not ride the camera.** Z5 is the viewer's layer. (*"no, captions don't ride the camera"*) - HG3 closed.

Also settled the same hour, on the card's flight (the tariff hook): the in-flight size change is PERSPECTIVE, not a
snap - a few percent (4-6 %) following the arc's depth, enough to read as approach/flutter, never a warp - and the fill is
the CAMERA's punch-to-fill, not the object growing. The card lands CENTRED over the imagery (Tokyo adapted its spot
because its dock stayed; here the card lands and the eye goes to it fast). No black frame on a card or a page: the edge
is the cream (or the deckle); corners rounded whenever the card is not full-frame.

## Rejected Alternatives

- The object grows (`snap`, `throw`'s post-contact growth): built and working, but the operator's read stands - it is
  the object moving because nothing could look at it.
- A per-species camera (today): three windows that cannot compose, cannot be interrogated, and cannot follow a landing.

## Verified Gotchas

- Seek-exactness (C6): the camera state must be a pure function of t - no springs integrated frame to frame; the
  analytic spring (42 §42.2) and min-jerk are closed-form and qualify.
- Captions: the caption strip is composited over the stage; if it rode the camera, the strip would zoom - HG3.
- The goldens: `ledger-soak-page` and `ledger-page-mid-build` have no camera species; identity by default keeps them.
- `worldAnswer` already translates the worlds for a landing's dip - the camera root must compose ABOVE it or the dip
  becomes a camera move.

## Verification

- `python -m pytest content/video_engine/tests/test_golden_frames.py -q` - byte-identical with the camera flag off (every slice).
- `python -m pytest content/video_engine/tests/test_camera.py content/video_engine/tests/test_camera_probe.py content/video_engine/tests/test_gate_motion_density.py -q`
- `python content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build_short.py --arm sig` then
  `python content/video_engine/scripts/gate_motion_density.py .../japan-tariff-trick/build-short --timeline japan-short.timeline.json` - 0 FAIL.
- Rendered frames across the hook arrival (the scratchpad `beat_frames.py` pattern: `render_baseline.serve` + `frame_png`
  on `build-short/player.html`) read as a viewer, and the element rects inspected in the pane at the instants that matter
  (the 2026-09-08 lesson: measure the page / field / title rects, do not read instants).
- The operator's watch on :8734 (HG1, HG2). DONE 2026-09-10 on the Tokyo short: "8742>8738" (E59 amended) - both gates closed; the
  camera cut is Tokyo's default build; the plan is complete.
- (2026-09-10) HG1/HG2 material on the Tokyo short too: `TOKYO_CAMERA=1 TOKYO_BUILD_DIR=build-short-cam` → :8742
  (`tokyo-short-player-cam`): the attention pull on the row-2 landings and the fab card, the arrival on the ring in place
  of the snap; gate PASS (M24 in frame). The operator asked for it ("let's test out those camera changes"); it is watched
  against the locked cut on :8738, never over it.

## Evidence And Handoff

- Evidence lands per slice in this file (`Evidence:` lines): test output, the gate's RESULT line, frame paths, commit SHAs.
- Handoff: the ruling (E54) in `docs/portable/OPERATOR-RULINGS.md` with the operator's words; `CAPABILITIES.md` row;
  the choreography ledger's arrives column; the docs layers regenerated (`build_docs_layers.py --write`, 8 in sync).
- The player is served by `serve_player.py 8734 build-short` (no-store); the render after the word per `REVIEW-CLAUDE.md`.
