---
id: P49-THE-CAMERA
title: The camera as a first-class component of the physics - the eye in the world
status: draft
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-08
updated: 2026-09-08
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
- Status: pending
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/test_camera.py`
- Acceptance: a timeline with no authored camera carries identity keys; an authored key list validates (monotonic t,
  zoom > 0, ease in the kinetics set); the three camera species compile to keys with the same numbers `camXf` produces.
- Validate: `python -m pytest content/video_engine/tests/test_camera.py -q`
- Evidence: pending

### T2: One camera transform at the world root
- Status: pending
- Owner: parent
- Depends on: T1
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`, `content/video_engine/scripts/kinetics/camera.mjs`, `content/video_engine/scripts/sync_kinetics.py`
- Acceptance: behind `kinetics.camera`, worlds/docks/species compose through `M_camera`; with the flag off the goldens
  are byte-identical; with it on, the three species render pixel-identical to today on the tariff short's frames
  (measured by `measure_frozen_frames.py`-style hashes on the affected windows).
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and the window hashes
- Evidence: pending

### T3: The probe - what is in frame
- Status: pending
- Owner: junior_developer
- Depends on: T2
- Write set: template (`window.__camera`), `content/video_engine/tests/test_camera_probe.py`
- Acceptance: `__camera(t)` returns `{frustum: {x0,y0,x1,y1}, zoom}` and `inFrame(target)` with the on-screen scale;
  a target off frame at t reports false.
- Validate: `python -m pytest content/video_engine/tests/test_camera_probe.py -q`
- Evidence: pending

### T4: The attention law
- Status: pending
- Owner: parent
- Depends on: T2, T3
- Write set: `kinetics/camera.mjs`, template, `docs/portable/OPERATOR-RULINGS.md` (E54)
- Acceptance: a dock landing pulls focus toward it by the servo law and settles; dials `[DERIVED]`; HG1 by eye on the
  tariff hook.
- Validate: rendered frames at the landing and the settle; `gate_motion_density.py` M09/M14 PASS
- Evidence: pending

### T5: The camera arrival (the card becomes the world by the eye going to it)
- Status: pending
- Owner: parent
- Depends on: T4
- Write set: template, `build_scene_timeline_f.py` (`enter=camera=<dock>`), `japan-tariff-trick/build_short.py`
- Acceptance: the hook page's card lands; the camera goes to it; at the match the world is the ledger page with no
  seam (the ARAP invariants exact at the switch); the whoosh rides the camera's speed; M11 reads the card as the page's
  own preview (already true for snap).
- Validate: rendered frames across the arrival; goldens; the gate 0 FAIL
- Evidence: pending

### T6: The in-frame gate
- Status: pending
- Owner: junior_developer
- Depends on: T3
- Write set: `content/video_engine/scripts/gate_motion_density.py`, `docs/GATES-REGISTRY.md` (generated), tests
- Acceptance: M24 FAILs a pointing species whose target is out of frame when it fires; M09/M14 read the camera track.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: pending

### T7: The record
- Status: pending
- Owner: parent
- Depends on: T5, T6
- Write set: `docs/portable/OPERATOR-RULINGS.md`, `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md`,
  `docs/content-video-engine/CAPABILITIES.md`, `japan-tariff-trick/CHART-CHOREOGRAPHY.md`, the docs layers
- Acceptance: E54 carries the operator's words; §9.27's "one camera move per window" is restated for a persistent camera;
  the layers regenerate in sync.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --write`
- Evidence: pending

## Decisions For The Operator (Stage 1 of the grill, restated for the camera)

1. **Who drives the camera by default** - (a) attention: landings and declared targets pull it, authored keys override
   (recommended: the eye follows what lands, which is what the operator described); (b) authored keys only, attention
   opt-in.
2. **The arrival** - (a) the camera arrival replaces `snap` for every chart card (recommended once HG1 passes);
   (b) opt-in per page beside `snap`.
3. **What rides the camera** - (a) worlds, docks, species; captions in screen space (recommended - Z5 is the viewer's
   layer); (b) captions ride too.

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
