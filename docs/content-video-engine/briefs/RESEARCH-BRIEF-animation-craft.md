# Research brief — what the drawing engine's builder does not know

For the Gemini deep-research pass, 2026-09-04. Same process as speech (docs 32–37)
and evidence (doc 39): research condenses the field, we extract to docs, the docs
become gates. This brief says what to look for and — more importantly — what shape
the answer has to arrive in to be usable.

---

## 1. The honest diagnosis

The operator's premise is that the math is already there. It is, and it is not the
bottleneck. Three things the builder has:

1. **Closed-form math.** Béziers, splines, arc-length reparameterisation, easing
   families, affine and projective transforms, spring integrators, signed-distance
   fields. All of it can be written on demand.
2. **API fluency.** SVG, Canvas, WebGL, CSS, GSAP, Remotion, Lottie, AE expressions.
3. **Principle names.** The Disney twelve. Murch's Rule of Six. Rule of thirds.
   Squash, anticipation, follow-through, staging. **This third one is the trap** —
   knowing the name feels like knowing the thing.

Four things it does not have:

**(a) The inverse model.** Parameters → motion is solved. Desired perception →
parameters is not. "Make it feel heavy" has no lookup that returns a number. An
animator's craft *is* that lookup table, built from thousands of playbacks.

**(b) Perceptual feedback.** Every other maker on this pipeline gets a loop — the
writer reads aloud, the recorder hears the take, the operator watches the render. The
builder writes and ships blind, never sees its own output move. This is *why* its
defaults drift generic: generic is what survives when you cannot check. It is the same
mechanism behind "background scenes, not action scenes."

**(c) Calibrated numbers behind qualitative rules.** Every principle known as prose
has a number the practitioner knows. Anticipation frames by implied mass. Overshoot
percentage by material. How long a held frame lasts before it reads as dead. The number
is the craft; the prose is the label.

**(d) Placement grammar.** Where an object goes is decided by where the eye already
is, where it just came from, and where it must go next. "Rule of thirds" is decorative.
Eye-trace, tangency, figure-ground and gaze-ownership after motion are the mechanics,
and they are missing.

### The fix is the one this repo has already run twice

Voice became transferable when we stopped describing tone and started counting
words per sentence and testing attribution position. Evidence became trustworthy when
we stopped asserting figures and started requiring a fetch date. Animation will go the
same way — **but only if the research comes back with numbers, thresholds and failure
signatures, not adjectives.**

## 2. The output contract (binding on the research)

Every finding must arrive as one of:

| form | example of the shape |
|---|---|
| **a number with a tolerance and its condition** | "anticipation = 3–5 frames @24 for a light object, 8–12 for a heavy one; source" |
| **a decision rule** | "if the shot is under N frames, the viewer registers a flash, not an image" |
| **a failure signature** | "a morph reads as a crossfade when correspondence points are more than X apart relative to the bounding box" |
| **an exemplar pair** | right / wrong, named and sourced — voice transferred by exemplar (VOICE-PACK), motion will too |

**Not wanted:** descriptions of the twelve principles, tool tutorials, listicles,
3D/character-rig material, game-engine material, generative-model prompting. The
builder already has the prose and it has not helped.

Every claim carries a source, and **every number carries a retrievable locator** —
page or section of the cited work, or a URL. A number whose source is a book or paper
with no page is a *design proposal* and must be labelled as one. Proposals are welcome;
proposals wearing citations are not. **The bibliography certifies nothing about the
body** — added 2026-09-04 after the first pass returned real papers attached to invented
figures (see [`VERDICT-research-brief-animation-craft.md`](VERDICT-research-brief-animation-craft.md)).

A number without a locator goes under SOURCES-TO-VERIFY, same as a figure in a script.

## 3. The questions, by role

Priority marked ★ — if the pass can only go deep on five, take the starred ones.

### Track A — the animator (timing and motion)

| # | question | why it matters here |
|---|---|---|
| **A1 ★** | **The timing charts.** Actual frame counts behind the principles: anticipation duration vs the action that follows; overshoot magnitude and settle count by implied mass; hold lengths in limited animation; the on-1s/2s/3s decision — when does a held drawing read as economy vs as broken? | Converts the whole vocabulary into parameters. Highest value single item. |
| A2 | **Ease equivalence.** Map traditional spacing charts to cubic-bezier / GSAP eases. What does "slow-in over five drawings" equal numerically? And the perceptual labels — which eases read as mechanical, organic, heavy, snappy, *arriving*, *slamming to a stop*? | We pick eases by habit. |
| A3 | **Spring vs curve.** When does a physical spring (stiffness/damping/mass) beat a keyframed ease? Parameter families that read as paper, metal, fabric, liquid — **and ink**, which is ours. | The ledger page is ink on paper. |
| A4 | **The threshold of "alive."** Minimum motion that keeps a frame from reading as static. Is there a measured attention curve for a held frame, and does sub-threshold ambient motion change it? | We have E21 and M10 (no still over 6 s) as operator-derived thresholds. Same shape as the sub-threshold-music question. |
| A5 | **Drawing-on.** What makes a progressive stroke read as *drawn by a hand* vs *a mask sliding*? Rate profile along arc length; pen-lift at corners; whether rate should track curvature. | Directly actionable on `drawOn(path, k)`. |
| A6 | **The secondary-motion budget.** How much follow-through sells weight before it becomes noise? Is there a ratio to primary motion? | The race "feels choppy" — likely under-budgeted secondary. |

### Track B — the editor (cutting and rhythm)

| # | question | why it matters here |
|---|---|---|
| **B1 ★** | **The gap-cut finding, generalised.** We measured 82 % of reference cuts landing in acoustic gaps vs 32 % on ep1. Is that a known rule? Murch's Rule of Six; cutting on action; the saccade-masking claim (a cut during a blink or saccade is invisible) — verify or refute, with sources. | Becomes gate M13. |
| B2 | **Minimum shot length and reset cost.** How short before a shot reads as a flash? What is the re-orientation cost of a cut, and does it scale with dissimilarity between the two shots? | Sets our scene-length floor. |
| B3 | **L-cuts / J-cuts under continuous narration.** Our audio is wall-to-wall VO with no diegetic sound to cut on. What is the grammar for offsetting picture from the sentence boundary? | Every cut we make is against VO. |
| B4 | **Graphic match cuts.** The object → chart transformation is a match cut in disguise. What makes a graphic match read as *continuous* rather than as a dissolve — shared silhouette, shared centroid, shared dominant line? | The transformation architecture depends on this reading correctly. |
| B5 | **Rhythm as a distribution.** Is there measurable shot-length structure in high-retention short-form? Distribution, not mean — the WPM finding taught us the means were identical and the spread was the story. | We measure our own rhythm already; need the reference. |

### Track C — the drawing-engine builder

| # | question | why it matters here |
|---|---|---|
| C1 | **Shape interpolation.** Path A → path B with different vertex counts: which correspondence algorithm produces a morph that reads as *one object changing*? As-rigid-as-possible, Kabsch alignment, arc-length resampling, what the SVG morph libraries actually do. Failure modes: when does it read as crossfade, when as collapse? | "Everything transforms out of the chart plate." |
| **C2 ★** | **Rigging without a rig.** The operator's insight: everything was chart-drawn, so objects should link and move in relation like data. The general form is a scene graph with constraints — parent, aim/look-at, path-follow, distance, driver expressions. **What is the minimum constraint vocabulary that buys the most?** | The most consequential architecture question for the engine. |
| C3 | **Nested coordinate spaces.** Each builder defines `mx()/my()` locally. How do AE / Rive / Lottie / Flash handle nested spaces, and what is the right shape for "put this prop at data index 3"? | Backlog A6. |
| C4 | **Runtime under deterministic render.** SVG vs Canvas vs WebGL when every frame is rendered by seek: which primitives are cheap, what breaks determinism, where does SVG fall over (path count, filter cost)? | We render frame-by-frame; we have hit SVG filter cost before. |
| C5 | **Ink on paper, specifically.** How is a convincing hand-drawn line simulated — variable width along the path, pressure profiles, slight boil, texture? And the inverse: what makes vector ink look sterile? | The E22 signature; the thing that would most raise the bar. |
| C6 | **What Rive / Lottie / Flash got right.** The closest existing systems: declarative, timeline-driven, deterministic 2D. Their data model, where they hit walls. | Steal the model, do not re-derive it (harvest, never replace). |

### Track D — placement (the "where" question)

| # | question | why it matters here |
|---|---|---|
| D1 | **Eye-trace.** Where does a viewer look on a graphic frame, and for how long? *The last thing that moved owns the gaze* — is there a measured decay? | Lets us place the next object where the eye already is. |
| D2 | **The non-decorative composition rules.** Tangency (why touching edges kill depth), figure-ground, headroom, the 180 rule, negative-space direction — **and how each changes on 9:16 with a caption safe zone eating the bottom third.** | Our frame is constrained; we need the subset that survives the constraints. |
| D3 | **Predictable reading order.** Given title + chart + badge + caption, what determines the order they are read, and can it be predicted from size / contrast / position / motion? | If predictable, it is checkable, and becomes a gate. |
| D4 | **Motion-graphics grids.** Broadcast design has grid systems for lower-thirds and full frames. What are they, and the vertical equivalent? | Dock geometry is currently by hand. |
| **D5 ★** | **The abstract → concrete lookup.** `RULE-abstract-to-concrete` names the move but has no library behind it. Is there a taxonomy of visual metaphor for quantity, change, cause, constraint? Conceptual-metaphor theory (Lakoff/Johnson: *more is up*, *change is motion*, *time is a path*) is an academic base that would let the prop library be **derived** rather than invented one prop at a time. | Turns the prop library from a guessing game into a derivation. |

### Track E — the feedback loop (the structural gap)

| # | question | why it matters here |
|---|---|---|
| **E1 ★** | **What can be measured from a rendered frame sequence?** Per-frame motion energy, salience maps, centroid of change, contrast, optical flow. Which of these correlate with human judgments? | Closes gap (b). If we can compute it, we can gate it — the way we gate scripts. |
| E2 | **Existing perceptual metrics.** Is there literature measuring jank, choppiness, glance-readability? The operator has already given one verdict by eye ("the race feels choppy") — what is its measurable signature? | Converts an ear/eye verdict into a mechanical one. |

## 4. What the extraction will produce

Same as the speech pass. Research → a numbered doc (42-ANIMATION-TIMING or similar)
→ each calibrated number becomes a constant in the template or a gate in
`GATES-MOTION.md` → each exemplar pair goes in a MOTION-PACK the way VOICE-PACK holds
the hook pairs. A finding that cannot be turned into one of those three things stays
in the research doc as context and does not enter doctrine.

## 5. Where this sits

- [`BACKLOG.md`](../BACKLOG.md) — the open work this research feeds (A1–A6, C1–C6, R1–R5).
- [`RULE-abstract-to-concrete.md`](../RULE-abstract-to-concrete.md), [`RULE-the-page-is-the-ground.md`](../RULE-the-page-is-the-ground.md), [`FINDING-gaps-are-the-edit.md`](../FINDING-gaps-are-the-edit.md) — the three findings that opened the scope.
- Doc 29 — the production bar the answers have to land inside.
