# Editorial Motion System

*Specification of record for deterministic shot timing, local cinematography,
and provider-motion exceptions in the History documentary lane.*

## 1. Decision

The engine edits a film; it does not apply a generic animation to every image.
`editorial_motion_plan.v1` is the instruction boundary between approved
narration beats and Remotion. The renderer executes the plan and cannot invent
camera movement, transitions, asset substitutions, or factual overlays.

Remotion owns the editorial timeline, layer composition, camera transforms,
cuts, captions, citations, and canonical narration. Manim supplies exact maps,
routes, timelines, relationship diagrams, and other deterministic explanatory
layers. FFmpeg supports media inspection, trimming, encoding, and compatibility.

Generated motion is an optional source layer. It never becomes the editor.

## 2. Timing authority

The continuous, hash-matched canonical narration and its word timings are the
render clock. Storyboard scenes preserve approved claims and citations;
`editorial_beat_plan.v1` preserves semantic segmentation.

Ten-second audio or provider blocks are cache and delivery units. They do not
force cuts. A shot may cross one of those boundaries while the continuous audio
remains uninterrupted.

The motion plan must cover its selected audio interval exactly, with no gaps or
overlaps. A visual beat may become several shots only when all child shots retain
the original beat's claim/citation binding and word interval.

The coverage schedule is also the primary-image schedule: each selected slot
binds one approved primary plate at that slot's interval. Canonical narration
words—not a legacy duration estimate—are the timing authority. An inherited
plate can bind only to its exact, ordered narration phrase; any uncovered prose
becomes an explicit semantic-generation requirement. Proportional retiming of
an old image schedule across different prose is prohibited. Each primary plate
holds for **two to six seconds**, with six seconds a hard ceiling. Reusable
world and character layers preserve continuity around the plate; they do not
replace it. See
[`17-TIMESTAMPED-PLATE-PRODUCTION.md`](17-TIMESTAMPED-PLATE-PRODUCTION.md)
for prompt compilation and bounded image-review rules.

## 3. Motion ownership

Motion is authored in this order:

1. Character or prop action.
2. Localized environmental action.
3. Information reveal.
4. Camera action.

A camera move by itself is not a meaningful visual event. The camera defaults
to locked. A moving shot must name a focal point, use a bounded amount, and
declare hold, movement, and settle phases. Full-frame drift, shake, handheld
motion, and unmotivated diagonal movement are prohibited.

Stillness is intentional. A locked evidence insert or reaction may be more
legible than continuous motion.

### Semantic cut routing

Every shot declares one visual intent before asset selection: `academic`,
`martial`, `scenic`, `journey`, `evidence`, `explanation`, `humor`, or
`transition`. The intent chooses the image family; it is not a decoration
layer applied afterward.

- **Academic** passages cut to institutions, study, teaching, records, or
  classrooms.
- **Martial** passages cut to safe, non-instructional practice, contests, or
  martial artifacts.
- **Scenic** passages establish a place through ports, rivers, streets,
  weather, and architecture.
- **Journey** passages cut to a reviewed local map/route surface, then a
  place-specific world or travel object. Generated art may provide the world,
  but it never supplies factual geography.
- **Lists** receive one distinct action per meaningful item—an object cut-in,
  a character/prop action, an icon reveal, or a map step. This is deliberately
  a list-item rule, not a literal cut on every ordinary noun.

A bare text card, a generic book, or a floating box is not an action. If the
list cannot be pictured meaningfully, the beat needs an editorial rewrite or
a reviewed explanatory surface before it can render.

### Positive visual events

A cut to a newly loaded, narration-relevant archive, illustration, technique
plate, document, map, character, or prop is a positive visual event. A subject
action, localized environmental action, or information reveal may also qualify.

Removing a character, overlay, prop, or information surface does not qualify by
itself. A deletion-only beat leaves the viewer with less information and must
fail validation unless the shot also introduces a relevant asset or affirmative
action. A camera move and a transition effect do not rescue a deletion-only
beat. This prevents a blank background, cleared desk, or “overlay disappeared”
state from being counted as editorial progress.

## 4. Shot grammar

The v1 vocabulary is deliberately small:

- purposes: hook, establish, reveal, explain, detail, reaction, payoff, and
  chapter reset;
- scales: wide, medium, medium detail, close, and insert;
- camera actions: locked, push-settle, pull-settle, lateral reveal, foreground
  parallax, and explicit cut-on-motion;
- transitions: hard cut, match cut, paper wipe, chapter fade, and crossfade.

Hard cuts are the default. Match cuts require a shared shape, object, material,
color, direction, or character motif recorded in `scene_flow_graph.v1`.
Crossfades require an explicit time or place change. Chapter effects are not
used to conceal a weak adjacency. A paper wipe is reserved for an actual
document, page, or chapter change; it must not replace a stronger archival or
illustrative cut.

Action cuts land on anticipation, contact, recoil, or result. The engine does
not cut randomly inside movement.

## 5. Plan contract

`editorial_motion_plan.v1` is a single job-level, content-addressed artifact.
It binds:

- storyboard and editorial-beat hashes;
- scene-bundle and scene-flow hashes;
- approved asset-map and canonical-audio hashes;
- an abstract pacing-recipe hash;
- exact shot timing and narration word ranges;
- approved asset IDs and layer roles;
- focal point, shot scale, action ownership, camera phases, transitions, and
  overlays; and
- provider-motion requirement and fallback.

Renderer-facing plans contain approved asset IDs rather than arbitrary paths.
The existing asset resolver verifies local containment and content hashes.

Unknown contract values fail closed. A locked shot has zero camera amount and
zero movement duration. Moving-shot phases must sum to the shot duration unless
an explicit cut-on-motion contract permits the final settle to be zero.

## 6. Pacing recipe

`editorial_pacing_recipe.v1` stores the channel's abstract edit grammar:
preferred shot-duration range, maximum repeated scale and movement signatures,
motion-density ceiling, transition policy, and chapter reset behavior.

The recipe is research-derived structure only. It cannot contain creator names,
source frames, URLs, copied prompts, or “in the style of” renderer instructions.

## 7. Provider boundary

Every shot declares one provider-motion classification:

- `none`: local layers express the shot;
- `preferred`: organic motion could improve the shot, but a reviewed local
  fallback remains acceptable; or
- `required`: the shot must be omitted or separately authorized because the
  intended action cannot be expressed honestly by local layers.

Provider candidates remain silent, local, hash-bound, non-renderable, and
quarantined until their existing promotion gate passes. Provider clips may
replace a source layer; they cannot alter shot timing, narration, facts,
citations, or final assembly.

## 8. Revision proof and QC

The first proof is a 30–60 second A/B revision using the same approved source
excerpt. It produces:

- baseline and revised previews;
- a diagnostic preview showing shot ID, focal point, motion phase, transform,
  and cut reason;
- the motion and pacing contracts;
- cut-adjacent frame samples and a contact sheet;
- FFprobe and structural-QC reports; and
- before/after hashes for every active Gate A artifact.

Structural QC rejects timing gaps or overlaps, stale hashes, unsafe asset
resolution, undeclared whole-frame movement, repeated treatment signatures,
missing settles, unmotivated transitions, provider leakage, and revision-path
escape. Metadata cannot prove cinematic quality, so a human must watch the
normal preview and score camera stability, focal clarity, shot hierarchy, cut
motivation, pacing, evidence legibility, and continuity at least 4/5.

The proof uses zero provider calls. Paid motion remains blocked until the
Editorial Motion Proof Gate passes and a separate spending ceiling is approved.

## 9. On-screen text and added-layer policy

- The default is no added text and no added prop. A layer must earn its place.
- English narration uses platform captions; it is not burned into the landscape
  master.
- Claim citations remain hash-bound to shots but resolve in end credits and the
  video description unless an operator explicitly requests an on-screen source.
- Text that merely restates narration is prohibited. On-screen text is reserved
  for information the image and narration cannot communicate efficiently, such
  as a critical date, comparison key, chapter label, or diagram measurement.
- A prop is prohibited when the plate already contains the same semantic object,
  and a non-evidence prop must never be presented as documentary evidence.
- If text is necessary, it uses a designed surface rather than a generic card.
  QC rejects surfaces outside frame or over character layers. Pacing recipes set
  explicit ceilings for information surfaces and non-evidence prop layers; the
  default proof recipe permits zero information surfaces and one contextual prop.
