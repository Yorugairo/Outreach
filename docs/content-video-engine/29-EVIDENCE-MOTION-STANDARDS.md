# 29 — Evidence Motion Standards (Gemini findings + v1 momentum + linked choreography)

Status: accepted working standard, 2026-08-24
Proven by: `claude.ai/code/artifact/57eacb95-7edd-41ca-aec3-086ea10a5ea3` (24s
interactive proof, beats 02–04 of the current-bubble opening, scrubbable)
Supersedes: nothing — this is the doc the `learning/` folder stopped writing
after 2026-08-16. It consolidates the Gemini evidence-dock findings, the
hyperframes-opening-v1 momentum mechanics, and the rules discovered while
rebuilding the braid with real teacher-stamped evidence.

## The format thesis (operator decision)

Complex, semantically related world plates overlaid with clear, clean evidence
displays. The narrative carries; the plates are themselves an evidence layer;
the evidence documents and motion exist to add authority and keep the eye
moving. Plates are the reusable back layer (amortizes across episodes when
semantically tagged); the evidence layer is the cheap per-episode carry layer.

---

## Part 1 — The Gemini evidence-dock grammar (most significant findings)

Source: `docs/content-video-engine/samples/gemini-decoupled-evidence-showcase.html` (archived copy; original landed in the gitignored review/ class)
(Gemini-authored). Four elements, all adopted:

### 1.1 Asymmetric scrim — never global dim

A directional gradient quiets ONLY the zone the evidence needs; the rest of
the world stays lit and alive. Global dims demote the world to wallpaper and
violate `world_plate_is_hero`.

```css
background: linear-gradient(to right,
  rgba(8,12,20,0) 0%, rgba(8,12,20,.65) 35%, rgba(8,12,20,.92) 100%);
```

Scrims arrive with their cards and leave at the callback. Mirror the gradient
per side (`to left`) when evidence occupies the left zone.

### 1.2 2.5D physical card — hard-edge shadow, no fake 3D blur

Evidence surfaces are physical documents on an editorial desk:

```css
background: #F4E6C7;               /* washi cream (finance lane) */
border: 3.5px solid #25313C;       /* woodblock ink */
border-radius: 14px;
box-shadow: 14px 14px 0px #25313C; /* hard-edge paper drop shadow */
```

The hard offset shadow gives depth that reads as paper, not web UI. (The
newsprint/v1 lane keeps its own dressing — gold `object-window` frames — per
operator preference; the hard-shadow rule applies to washi chips and docks.)

### 1.3 Micro-scale spring entrance — 0.88 → 1.00, never from zero

Scale-from-0 with bounce reads cartoon. Adult documentary feel:

- scale range **0.88 → 1.00** only (12% expansion)
- opacity 0 → 1 over the first ~8 frames
- damped spring (`damping 18, stiffness 90`) or `power3.out` — clamped
  overshoot. The document "snaps into focus," it does not float in from space.

### 1.4 Background parallax — the layers separate themselves

While evidence holds locked, the world plate drifts (scale 1.00 → 1.04, a few
px of translation over the shot). The eye separates narrative world from
evidence data with zero labeling. Corollary proven in the demo: **uniform
ken-burns across all plates reads as drift, not direction** — amplitude and
vector must vary per beat, and evidence typography never moves while readable.

---

## Part 2 — Momentum mechanics (recovered from hyperframes-opening-v1)

Source: `edit/hyperframes-opening-v1/index.html` (f10b worktree). These four
mechanics are why v1 felt alive and the first rebuild felt dead. Motion is
state, always — every move encodes a fact, or it is forbidden (`motion_rule`).

### 2.1 Entrances have a semantic direction

Cards fly in FROM where they come from, slightly rotated, settling hard:

| card | entry | reading |
| --- | --- | --- |
| memory | `x:+520, y:-40, rot:2°, scale:.72` | from off-right, beside the world |
| factory | `x:-460, y:+120, rot:-2°` | opens from the production side |
| fund | `x:+420, y:+360, rot:4°, scale:.38` | rises out of the flow itself |

Ease `power3.out`, ~1.0s, rotation settles to zero. The rotation is what
sells "physical document landing."

### 2.2 Nothing living is ever still

Every active card breathes: slow sine drift (±16px, ~1.8% scale swell,
`sine.inOut`, 5–16s periods) from settle until demotion. Card-level
ken-burns. A frozen card reads as a slide.

### 2.3 Demotion is continuous recession, not a step

v1 shrinks the memory card in four chained moves (.58 → .54 → .50 → .46 over
12s). Implement as fast drop (−16% scale, −30% brightness, ~1s) plus slow
creep (a further −10% scale, −12% brightness over ~9s). The argument trail
visibly compresses as the argument grows; demoted cards never park.

### 2.4 The world reacts to the evidence

At the callback the world pulses (scale 1.00 → 1.04 → 1.00) as cards retract.
Connection runs both directions between layers.

---

## Part 3 — Linked-evidence choreography (the chain is the transition)

From the v1 STORYBOARD rhythm: settle → open → braid → expand → qualify →
diagnose → resolve → callback. Cards are clauses; spatial relations do
rhetorical work: **beside** = comparison, **opens-from** = consequence,
**bridge** = inference, **retract + callback** = payoff.

- Gold mechanism lines draw the links (scaleX/scaleY reveal, `power2.inOut`).
- Max ONE fully lit card; prior cards demote (2.3) instead of exiting or
  colliding. Demotion replaces v1's card-pileup failure.
- The chain replaces most cutting: new evidence entering IS the transition.

## Part 4 — The literal evidence layer (teacher-stamped deck slides)

Source of truth: `sources/decks/teacher-stamped-production-visuals/` — full
production slides (1376×768) with typeset claim boxes and the teacher stamp.

- **Species rule:** generated art gets the frame (object-window/gold =
  "window into the story world"); literal documents get NO frame — a paper
  document with a hard drop shadow, baked source typography. Cream document
  against dark world = automatic provenance contrast; no source badge needed.
- Two modes: **source-bound crop** (enlarge the legible region; crop to the
  outside edge of the teacher stamp, never clip/replace the stamp) and
  **full slide**.
- One reserved slot per zone; a document exits before the next enters
  (comparison is the only sanctioned exception, max 2 horizontal).
- Reveal: clip-path wipe left→right (the hand-led-mask analogue), ~0.7s
  `power3.out`, small settle; typography stays still while readable.
- Numbers that must be exact are code-drawn on washi chips, never asked of
  the image model (`generated_text_rule`); a counter authored in code is
  exact by construction.

### 4.1 Documents displace the trail (new rule, 2026-08-24)

A literal document's entrance pushes DEMOTED cards further into recession,
away from the document's zone (extra translate + ~7% scale, eased ~0.8s,
timed to the entrance). Active cards hold; only the trail moves. This is
choreography responding to the document — positions authored for one asset
shape must not be trusted for another.

### 4.2 One reading surface at a time (new rule, 2026-08-24)

While a literal document holds the stage, captions yield to **quiet mode**:
smaller, static, single fade, keywords still colored, no punch-in. Kinetic
captions run only when the caption is the sole text layer on stage.

## Part 5 — Captions (Alicia rhythm under the caption-grammar doc)

- One fixed lower-third anchor. Evidence roams by semantic slot; captions
  never follow it. Transparent glyphs + text shadow; no pill, no panel.
- Kinetic mode: 2–4 word groups punch into the anchor sequentially
  (~0.34s apart, `power3.out`, scale 1.14 → 1.0, y 12 → 0), keywords in the
  accent color. Group timings derive from `words.json` in production.
- Quiet mode per 4.2.

## Part 6 — Transitions (semantic palette, unchanged + one addition)

Clean cut = contrast/correction. Directional wipe = process continuation.
3D book-flip = structural reframe, sparing. All decorated transitions happen
on **evidence-free boundaries**: documents exit → cards retract → world
breathes (2.4) → then the wipe. The proof demonstrates the full sequence
(Callback → Wipe beats). Full-scene hand-draw replacement remains
not-production-ready (unchanged exclusion).

## Part 7 — Standing corrections recorded elsewhere but load-bearing here

- `caption-follows-active-evidence` (confidence .95 in
  `learning/continuous-learning-import.v1.md`, p29 branch) is SUPERSEDED by
  the fixed-anchor rule; the shipped p34 cut has all 290 captions at one
  anchor. The instinct file still says the opposite — pending edit on the
  p29 branch.
- Reveal-window motion units need a **cap**: a complete top element riding
  the clip edge so the artwork never shows a guillotined slice (proven in
  overlay-money-transfer-woodblock-v5).
- Alpha overlays: the pinned hyperframes CLI renders transparency natively
  (`--format mov|webm|png-sequence`); `hyperframes_render.py` just never
  passes `--format`. A composition rendered via `-c` needs its own GSAP
  script tag or it renders silently static under `--best-effort` — gate
  overlay renders with `--no-best-effort` or a no-timeline lint.

---

## Part 8 — The scene-evidence lane (default production pattern)

Status: accepted 2026-08-24. Proven by
`claude.ai/code/artifact/a2c4e4b1-a528-4b8f-a87c-966533522c21` (27s, two
scenes, real teacher-stamped slides and current-bubble world plates).
Origin: `samples/gemini-scene-evidence-pipeline-showcase.html`.

Parts 1–7 describe **linked choreography** — cards entering in semantic
relation to each other, hand-tuned per beat. This part describes the pattern
that carries the weekly schedule.

### 8.1 The shape

```
ken-burns world plate
  → evidence build 1 (dock + badge a + badge b)
  → evidence build 2 (dock + badge a + badge b)
  → wipe
  → repeat
```

One continuous ken-burns move per **scene**, not per beat, with a distinct
vector and amplitude per scene (§1.4). Docks enter with the micro-scale snap
(§1.3). Badges reveal one at a time and never retract inside a scene. The
wipe fires only after both docks clear.

### 8.2 The timeline is data, not tweens

This is the whole reason the lane is repeatable. Every visual state is one
row in a declarative array:

```js
{ t: 5.0, scene: "s1", wash: 1, d1: "e1", d2: 0, p: "XX--", cap: "..." }
```

`p` is a four-slot badge mask (dock1.a, dock1.b, dock2.a, dock2.b).
Everything else is CSS transitions. A generator emits the array from
`configs/scene_evidence_timeline.schema.json`; nobody authors motion per
episode. Linked choreography, by contrast, needs per-card entry vectors,
demotion directions, and yield offsets — authored, not generated. Use it for
openings and structurally argued sequences; use this lane for everything else.

### 8.3 Do not bury the plate (operator correction, 2026-08-24)

The first build washed the world to ~86% and used opaque docks. The plates
are the expensive, reusable layer — covering them wastes the asset.

- **Wash is light and banded**: peak ~34% over the dock band, feathered to
  zero at the top and ~44% at the very bottom. Never a full-frame dim.
- **Dock chrome is translucent washi**: `rgba(244,230,199,.90)` with a 3px
  backdrop blur. This is *more* in register, not less — the style profile
  builds the world from "thin hand-cut washi, layered rice paper", and thin
  washi is translucent. Plate texture reads through the document.
- **The literal document inside the dock stays fully opaque.** Source
  evidence is never translucent; only the chrome around it is.
- Docks are sized and seated so the plate stays legible around them
  (~726px wide on a 1920 stage, top ~232px).

### 8.4 Badge provenance — the checkable property

Every badge numeral is quoted **verbatim** from the stamped document it sits
under (`18% → 23%`, `2 to 3`, `716%`, `70%`, `$400M`, `11T won` all appear in
their source slides). The schema requires `verbatim_in_document: true` per
badge, and the validator OCRs the bound slide and fails the build when the
string is absent. This extends the code-drawn-numeral guarantee from single
counters to the entire evidence layer: the numbers are exact by construction
AND traceable to a source, without a visible source badge.

### 8.5 Lane selection

| | scene-evidence lane | linked choreography |
| --- | --- | --- |
| authoring | generated from schema | hand-tuned per beat |
| world presence | co-star (translucent docks) | co-star (roaming cards) |
| argument shape | sequence of exhibits | chain with relations |
| cost per episode | near zero above evidence prep | high |
| use for | weekly cadence, dense factual runs | opening 60–90s, structured arguments |

### 8.6 Evidence selection rules (operator correction, 2026-08-24)

The first v4 pass failed review on three counts. Each is now enforced in
`scripts/build_scene_evidence_cut.py` rather than left to judgement:

1. **Captions keep their canonical timings.** The first pass attached the
   nearest caption to each beat, collapsing 89 word-timed lines onto 48 beat
   boundaries — captions held ~6s and drifted off the narration. Captions are
   a SEPARATE track resolved by time; beats never resample them.
2. **Evidence comes from the approved stamped catalogue, and never repeats.**
   The first pass inherited v3's asset list — 13 items with several used two
   or three times, including cropped, unstamped one-offs whose edges ran off
   frame. The project holds **86 render-eligible teacher-stamped slides**
   (`sources/decks/teacher-stamped-production-visuals/`), each carrying a
   label, summary, sha256, and `evidence_render_eligible`. Selection is an
   IDF-weighted match of each slide's label+summary against the narration
   inside that scene's window, with a used-set so no slide repeats and a
   one-slide-per-deck rule inside a pair.
3. **No badge without a read numeral.** Only 5 of 86 slides carry a quotable
   figure in their metadata, so badges cannot be auto-derived. Emit a badge
   only where the numeral was read off the bound slide; otherwise ship the
   dock with no rail. The stamped slide already carries its own typeset
   figures — inventing a figure to fill the rail is the failure this
   prevents.

Layout follow-on: a single-dock beat uses a wide centred dock (940px) so a
16:9 stamped slide reads large; paired docks stay side by side at 720px.

### 8.7 Evidence matching is a global assignment, not a per-scene pick

Reviewing the first stamped build, the opening beat ("AI memory stocks have
gone vertical and the **earnings** numbers look almost fake") was illustrated
with *The S&P 500 Paper Bubble Mechanics*. Two defects produced that:

1. **Scoring compared unlike things.** Raw overlap divided by slide length let
   two generic hits (`earnings`, `bubble`) beat one specific hit, and the top
   candidates were effectively tied (1.52 / 1.48 / 1.45). Scoring is now an
   IDF-weighted **cosine**, with hits inside the slide's curated label boosted
   2.2x — the label is operator-written and carries more signal than prose.
2. **Allocation was greedy in time order.** Each scene took its own local best,
   so an early scene could consume a slide a later scene needed far more.
   Selection is now a **global assignment**: every (dock-slot, slide) pair is
   scored, pairs are consumed in descending score order across the whole
   episode, and the strongest match anywhere is placed first. A slot whose
   top slide is taken falls through to its next-best unused one.

Supporting rules:

- **Per-slot windows.** A two-dock scene splits its window so each slot
  matches what is being said while *that* dock is on screen, not a blob of
  the whole scene.
- **Rare-token exception.** A single shared word normally fails
  `MIN_DISTINCT`, unless that word is genuinely rare (IDF >= 3.4).
- **Coverage pass.** A scene left with no evidence takes its best remaining
  slide above a lower floor; a scene whose narration matches nothing stays
  bare rather than showing a misleading document.
- **`match_score` is written into every evidence record** so the weakest
  matches can be reviewed instead of trusted. On the v4 cut the range is
  0.14 to 0.94; anything below ~0.2 deserves an operator look.

Result on the five-minute cut: 16 scenes, 23 unique stamped slides, no
repeats, opening beat now on *The Earnings Concentration Funnel*.

Note the honest side effect: badge count fell to 1. Slides are chosen by
meaning, not by whether a verified numeral happens to exist for them — and
that is the correct precedence. Raising badge coverage means OCRing the
catalogue, not biasing selection toward slides that already have badges.

### 8.8 No production chrome in the frame (operator correction, 2026-08-24)

The v4 dock shipped with a citation footer reading
`Memory Supercycle deck &middot; slide 003` and a `STAMPED` tag, plus an
`EVIDENCE 1` / `EVIDENCE 2` chip in the header. All of it is removed.

This was already ruled out and got re-introduced anyway: the shipped p32/p33/
p34 manifests all carry `visible_source_badge: false`, and Part 4 states that
a cream document against the dark world produces the provenance contrast
without a badge.

Three reasons it has to go:

1. **It is our filing system, not a source.** "Memory Supercycle deck, slide
   003" is an internal artifact path. A viewer cannot check it, and naming a
   deck we produced as if it were a citation is worse than showing nothing.
2. **`STAMPED` is an internal QA state.** The stamp is already visible in the
   artwork; restating its approval status is production plumbing on screen.
3. **`EVIDENCE 1` / `EVIDENCE 2` is scaffolding.** The slot index is a
   generator concept. The dock title carries the meaning.

**Provenance lives in the manifest, not the frame.** The timeline still binds
every document by `path` + `sha256` and records `match_score`; the render
stays clean. If real attribution is wanted on screen later, it must name the
external source the slide draws on (a filing, an index methodology, a dated
transcript) — which needs a per-slide source field the catalogue does not
carry today. Do not substitute the deck name for it.

### 8.9 Documents draw on, and they leave (operator correction, 2026-08-24)

Two failures in the v4 build, one cause: the dock was a state, not an event.
It appeared instantly and then squatted on the plate until the scene ended.

**The hand comes back for evidence reveals.** This was always sanctioned —
the rail doc calls for "a hand-led mask or trace reveal", and the
not-production-ready exclusion covers only *full-scene* hand-draw
replacement, never the evidence card itself. A dock now reveals under a
left-to-right clip wipe (~1.05s, ease-in-out) with the hand riding the
leading edge, and the hand **exists only while an artifact is being
revealed** — it fades in and out inside the wipe and is never on screen
during a hold. `draw-hand-a-v1` is trace-cut off its black ground by an
edge flood-fill; a luminance key eats the sleeve.

**Seven seconds, then out.** Every dock carries an explicit lifetime in the
timeline — `enter`, `exit`, and `badge_at[]` — capped at
`DOCK_HOLD_MAX = 7.0s` including the reveal, and forced to clear at least
0.6s before the scene's exit so the transition still lands on an
evidence-free boundary (Part 6). A dock whose window would be shorter than
2.2s is dropped rather than flashed.

**The plate gets its screen time back.** On the five-minute cut this is the
whole point: scene 15 runs 47s with documents present only from 241s to
253s — 33 seconds of pure plate with its ken-burns move. Across the cut, 23
docks average a 6.8s hold. The world is the hero again by scheduling, not
by opacity.

Data-model consequence: `scenes[].docks[]` replaces per-beat `docks`/`badges`
masks entirely. The renderer derives dock state from time — hidden,
revealing, held, exiting — so nothing has to be re-declared per beat, and a
generator only has to emit an enter/exit pair per document.

### 8.10 The hand follows the reveal-engine contract (correction, 2026-08-24)

The first hand pass slid a marker along a straight clip-path edge. That is
not how the hand works. The `whiteboard-explainer` skill
(`~/.codex/skills/whiteboard-explainer`) already carries the debugged
architecture and this project's own evidence grammar; use it, do not
improvise. Everything below is now implemented in the player template.

**The mechanic.** Professional whiteboard tools do not animate stroke paths.
They reveal a finished, detailed image through an **animated mask sweeping a
serpentine path**, with a photographed hand riding the mask tip. Line quality
comes from the artwork; the animation only controls WHEN each region appears.

What that means concretely, and what the first pass got wrong:

| Contract | First pass |
| --- | --- |
| SVG `<mask>` + serpentine path, revealed by `stroke-dashoffset`, ease `none` | straight `clip-path` wipe |
| Hand position from `getPointAtLength` on the mask path | hand slid along a linear interpolation |
| A/B pose swap by stroke direction (`ahead.x - pt.x`) — the swap IS the wrist motion | one pose for every direction |
| Nib pixel-calibrated, pinned to the path tip, `transform-origin` on the nib | hardcoded -66px guess |
| Hand ~40-60% of frame height, forearm running off the frame edge | 300px sticker, arm cropped mid-canvas |
| `mix-blend-mode: multiply` on the WRAPPER — on the masked `<image>` Chrome leaks the mask | absent |
| Camera LOCKED during a stroke; never reveal while it travels | ken-burns ran straight through reveals |
| Rows are stroke centerlines inset by sw/2; row step <= stroke width | n/a |

Measured on `draw-hand-a-v1`: nib at (0.287, 0.886) of the cutout. The cut
keeps full image height so the sleeve leaves the frame — cropping to the
alpha bbox ends the forearm mid-canvas, which the skill names as the number
one amateur tell.

**Still outstanding:** a real B pose. The engine swaps to it on right-to-left
rows and is currently fed a mirrored A, which flips the sleeve to the wrong
shoulder. Generate a true B ("the SAME hand, same sleeve, same lighting, wrist
tilted a few degrees") from the A reference through the codex lane, plus an
erase pose if erase beats are ever wanted.

**Note on skill choice:** the local `whiteboard-explainer` skill is the better
base than a generic upstream one — it already carries our evidence-led
world-plate grammar (attention budget, source-card crop rule, semantic
transition palette, the full-scene hand-draw exclusion) alongside the generic
mechanics, and its `templates/reveal-engine.js` has the Chrome mask-leak and
cap-scallop fixes baked in.

### 8.11 Do not blend a literal document (bug, 2026-08-24)

The first reveal-engine build drew nothing visible. The mask was correct —
sampling the rendered SVG at full reveal showed 12.9% ink, exactly right for
a typeset slide. The fault was `mix-blend-mode: multiply`.

The skill puts multiply on the artblock wrapper, and that is right *in its
context*: hand-drawn ink art sitting on a white paper canvas, where multiply
is what makes ink read as ink. It does not transfer to this lane:

1. **A blend group escapes its parent.** The dock background is translucent
   cream over a dark world plate, so the artwork multiplied against the
   *plate*, not the white frame, and rendered near-black. `isolation: isolate`
   on the white `.slide-frame` confines any blend group to it.
2. **Literal evidence must stay literal.** Multiply tints a source document.
   Part 4 already forbids altering it; a blend mode is an alteration.

Fix: no blend mode on a literal-document artwrap, plus `isolation: isolate`
on the frame so nothing downstream can reintroduce one. The serpentine mask,
the hand follower, and the camera lock are unchanged — only the compositing
was wrong.

**General rule:** skill mechanics written for drawn artwork must be re-checked
before being applied to a literal source document. Reveal timing, hand
choreography, and mask geometry transfer directly. Anything that changes the
document's pixels — blend modes, filters, recolors — does not.

### 8.12 The actual bug: a stale hide-state clip (2026-08-24)

8.11 fixed a real compositing fault but not the reported symptom. The reveal
still showed nothing. The cause was mine, not the skill's:

```js
if (!d) { el.style.opacity = 0; el.style.clipPath = "inset(0 100% 0 0)"; continue; }
```

The empty-dock branch clips the dock to zero width. When the clip-path wipe
was replaced by the SVG mask, the live branch stopped clearing it — so every
dock stayed clipped to nothing for its whole lifetime while the mask swept
correctly underneath. Computed style read `clip-path: inset(0px 100% 0px 0px)`
with `opacity: 1`.

Two things worth carrying forward:

1. **When a reveal mechanism is replaced, audit the hide state too.** The
   hidden and visible branches must write the same property set. A property
   set only in one branch persists into the other.
2. **Verify the composited element, not the mechanism in isolation.** The
   earlier check rendered the SVG standalone and measured 12.9% ink, which
   proved the mask worked and hid the fact that its container was invisible
   on the page. Sample the live element's computed style, not a detached copy.

Also added while fixing: the card lands before it is drawn on. A 0.3s
micro-scale entrance places the sheet, then the mask sweep begins — the paper
arrives, then the hand writes on it, rather than an empty card sitting through
the whole reveal.

### 8.13 Hand pose set v2 — host-consistent, two poses, per-pose nib

The asset pack shipped exactly one hand: `draw-hand-a-v1`, light-skinned, and
no B pose. Both gaps are now closed by a single generation
(`scripts/mat_drawing_hands.py` does the cut and calibration).

**Skin tone is a continuity fix, not a preference.** The teacher-stamp
presenter in the corner of all 86 stamped slides is a Black man in a suit. A
light-skinned drawing hand contradicts the host identity the evidence layer
already establishes on screen. This is not the `identity_rule`'s prohibited
"cosmetic recoloring" of a character — it is matching the hand to the
presenter the deck already shows.

**One generation, both poses, same person.** `hand-prep.md` requires the pose
set be generated from ONE reference so skin, sleeve, marker, and lighting
match. The work order supplied `draw-hand-a-v1` as the reference and asked for
A (default, left-to-right) and B (same hand, wrist rotated a few degrees for
right-to-left rows), with hard rejects for: an arm ending inside the frame, a
non-flat background, the two hands reading as different people, an unnatural
grip, an illustrated look, or B being a mirror of A rather than a rotation.

**Per-pose nib calibration is mandatory.** The wrist rotation moves the marker
tip, so B cannot reuse A's numbers or the ink lands off the path:

| pose | cut | nib (fraction) |
| --- | --- | --- |
| A | 816x1536 | 0.2868, 0.8913 |
| B | 807x1536 | 0.3222, 0.8763 |

Stored in `hyperframes/assets/hands/nib-calibration.v1.json`; each pose's CSS
`transform-origin` is set from its own nib so jitter pivots on the tip.

**Matting:** edge flood-fill from the black ground, never a luminance key —
the heather sleeve is dark and a threshold key eats it. Horizontal slack is
trimmed but **full image height is kept** so the forearm still runs off the
frame edge.

Remaining pose gap: an erase pose (hand gripping a folded cloth) if erase
beats are ever wanted. Not needed by the current lane.

### 8.14 The camera lock does not apply to this lane (correction, 2026-08-24)

8.10 imported the skill's camera rule verbatim — "camera LOCKED between
moves; never run a mask reveal while the camera travels" — and froze the
world plate's ken-burns for the duration of every stroke. Two problems.

**It produced a visible fault.** The implementation pinned the ken-burns
parameter to the reveal's start time and released it at the end, so the plate
froze for 1.35s and then jumped forward by the whole locked interval in a
single frame. Reviewed as "freeze, then jutter back in".

**The rule should never have been applied.** In a whiteboard composition the
camera moves the *drawing surface*: travelling during a stroke slides the
paper under the pen and destroys the illusion. In this lane the drawing
surface is the **dock**, which is fixed in screen space and never moves, and
the world plate is a separate layer *behind* it. Plate parallax cannot move
the paper, so it has nothing to do with the reveal. Parallax now runs
continuously and independently — verified linear across a stroke (scale
1.01480 -> 1.02400 -> 1.03330 over 4-6s, max frame delta 0.001).

This is the third instance of the same mistake (see 8.11, blend mode). The
pattern is now explicit:

> **Porting rule.** The whiteboard skill assumes the composition *is* the
> drawing surface. In the scene-evidence lane the drawing surface is one
> layer among several. Mechanics that govern the pen and the paper — mask
> geometry, serpentine coverage, hand follower, pose swap, nib calibration,
> hand-visible-iff-drawing — transfer directly. Mechanics that govern the
> *canvas as a whole* — camera lock, blend modes, full-frame erase — do not,
> because our canvas is a card inside a live world, not the world itself.

### 8.15 Timing constants, measured against the reference

Reviewed side by side, our build read less polished than
`samples/gemini-scene-evidence-pipeline-showcase.html` despite doing more.
The gap was not the mechanics — it was durations and curves. Reading the
reference's actual CSS gave the numbers:

| element | reference | ours (before) | ours (now) |
| --- | --- | --- | --- |
| dock entrance | 0.75s expo-out, `translateY(32px) scale(.96)` | 0.30s, scale only | 0.75s expo-out, y32 + scale |
| dock shadow | animated over the same 0.75s | static | animated with the card |
| wash fade | 0.75s | 0.50s | 0.75s |
| stat pill | 0.65s expo-out, `translateY(12px)` | 0.60s (matched) | 0.65s |
| scene wipe | 0.35s quart-in-out | 1.25s quad-in-out | 0.62s quart-in-out |
| dock exit | n/a | 0.55s | 0.72s expo-out |

Three principles fall out of that table:

1. **Settles are slow, moves are fast.** Every arrival uses expo-out
   (`cubic-bezier(.16,1,.3,1)`) at 0.65-0.75s — long enough to read as
   weight. Every transition uses quart-in-out at well under a second. Our
   1.25s wipe was the single most sluggish thing in the cut.
2. **Animate the shadow with the card.** A hard-edge paper shadow that snaps
   to full depth on frame one reads as a sticker; growing 0 -> 12px across
   the settle is what sells the card as a physical object landing.
3. **Overlap the phases.** The draw no longer waits for the card to finish
   arriving: `DRAW_LAG = 0.42s` against a 0.75s entrance, so the hand starts
   as the sheet settles. Sequential phases read as a machine executing steps;
   overlapped phases read as one gesture.

Current constants: `CARD_IN 0.75`, `DRAW_LAG 0.42`, `REVEAL 1.5`,
`EXIT 0.72`, `WIPE 0.62`. The mask sweep itself stays LINEAR (`ease: none`)
per the reveal-engine contract — easing the sweep makes the hand accelerate
against its own stroke.

### 8.16 Region reveals may ease slightly; line traces may not

The reveal-engine contract specifies a LINEAR mask sweep. That rule exists for
line tracing: pen speed must match the rate ink appears, or the nib visibly
outruns the line it is supposedly drawing. We reveal a finished document
through a region mask, so there is no traced line to fall out of step with and
a small ease is admissible.

Settled by eye at **`SWEEP_EASE = 0.08`**, implemented as a blend rather than
a swap: `rk = linear*(1-w) + easeInOut(linear)*w`.

Measured percent-drawn per 0.25s sample across a reveal:

| ease | step profile | spread | read |
| --- | --- | --- | --- |
| 0.00 | 17, 16, 17, 17, 16 | 1 | steady, slightly mechanical |
| **0.08** | **16, 16, 18, 18, 16** | **2** | **shipped** |
| 0.12 | 15, 17, 18, 18, 17 | 3 | softer, still holds |
| 0.22 | 14, 17, 19, 19, 17 | 5 | ends ~40% slower; reads as hesitation |

The first attempt used 0.22 and was rejected on review as worse than linear —
worth recording that "very minor ease" is roughly 0.08, and that the curve
becomes visible as hesitation well before it reaches a quarter of the way to
full ease-in-out.

Two constraints hold at any value:

1. **Hand and mask must read the same progress.** Both derive from `rk`, so
   they stay locked whatever the curve. Easing one and not the other — or
   easing them on different curves — is the failure the linear rule was
   implicitly guarding against.
2. **The dial stays in the player.** A curve judged by eye should be
   re-judgeable by eye; the control bar keeps a live SWEEP EASE slider so the
   value can be re-tuned against a real cut instead of argued about.

`DRAW_LAG` is **0.30s** against a 0.75s card entrance: the card reaches ~0.61
opacity before the first ink appears, so the sheet reads as landing before the
hand starts on it.

### 8.17 The hand is retired from this lane (operator decision, 2026-08-24)

After building the reveal engine correctly (8.10-8.16), the hand-drawn
reveal was cut. Reviewed against
`samples/gemini-scene-evidence-pipeline-showcase.html`, the plain card
entrance reads cleaner.

**What the lane is now.** A dock's entire entrance is the card settle: a
0.75s expo-out rise (`translateY 32 -> 0`, `scale .96 -> 1`) with the
hard-edge shadow growing `0 -> 12px` alongside, and the document simply
present on the card. Exit is a 0.72s expo-out lift. Everything else stands —
7s dock lifetime, translucent washi chrome, sequenced badges, canonical
caption track, continuous plate parallax, quart wipe between scenes.

**Why it wins here.** The mask sweep spends about 1.5s per document
performing the *arrival* of evidence. In a whiteboard explainer that
performance IS the content. In this lane the world plate is the content and
the document is a citation dropped onto it — a long draw makes a supporting
element behave like a headline, and at two docks a scene it competes with
both the plate and the narration.

**When to bring it back.** The machinery is not lost — the full engine sits
in git history (`7880c01`, `1e6612f`) and the pose set with nib calibration
stays in `hyperframes/assets/hands/`. It earns its place when the artwork is
*drawn* rather than sourced (an isolated illustration built to be revealed),
or in a dedicated whiteboard format where drawing is the format itself. It
does not earn its place decorating a stamped slide.

**Cost note:** dropping the hand removed ~2.6MB of embedded pose assets from
the cut and simplified the render to CSS-driveable transforms — relevant for
the Remotion port, where a serpentine SVG mask plus a per-frame
`getPointAtLength` follower is meaningfully more work than a transform.

### 8.18 Regional shading, and the choreographic rhythm

Two corrections from review, both about restraint rather than mechanism.

**Shading is regional, never global.** The bottom-banded wash darkened the
whole frame including the half doing narrative work. Replaced with two
layers that only touch the evidence region:

1. **Directional gradient** — fully clear to 44% of the frame, then deepening
   to `rgba(5,19,30,.62)` at the evidence side. Nothing darkens until past
   the midpoint, so the world half is untouched.
2. **Radial spotlight** — clear to 46% of a `58% x 62%` ellipse centred on
   the active card, falling to `.44` at the edges. The card sits in light and
   the surround recedes.

Consequence for layout: a solo card **anchors to a side** rather than
centring, so the gradient has a direction to run toward. Sides alternate by
scene index so the world is not always cropped the same way. A paired build
spans the frame, so its gradient runs bottom-up and the spotlight centres.

**The badge spring was missing.** Pills used the same expo-out decay as the
card, which reads as a fade. They now use a back-out curve —
`cubic-bezier(.34,1.56,.64,1)` over 0.58s from `translateY(15px) scale(.9)` —
overshooting about 4% before settling. The overshoot is what makes a pill
land like a stamp; the opacity still rides a plain 0.34s decay so only the
motion springs, not the ink.

**The cadence now matches the reference rhythm**, including the two beats
that were missing entirely:

| beat | duration |
| --- | --- |
| world plate alone | 1.7s |
| card 1 settles | -> |
| badge 1a | +1.3s |
| badge 1b | +2.6s |
| **settle — read card 1** | **1.1s** |
| card 2 enters (card 1 stays) | -> |
| badge 2a / 2b | +1.3 / +2.6s |
| **savour — whole board** | **2.2s** |
| wipe | 0.62s |

The settle and savour beats are the difference between a build that reads as
a sequence of arrivals and one that reads as an argument being assembled and
then presented.

**Hold-time exception.** A solo card still caps at 7s (8.9). A *paired* build
now runs to a shared `board_end` — both cards clear together after the savour
— which can reach ~8.5s for the first card. Without that, card 1 exits while
card 2 is still building and the viewer never sees the pair, which is the
whole point of a two-dock scene.

### 8.19 Dead-air ceiling, and the one-sided semantic join

**Dead air is bounded.** A long scene previously ran one build and then sat
untouched — up to 38s of bare plate. Two mechanisms fix it:

1. **Build cycles.** A scene now runs as many cycles as fit
   (`world -> card(s) -> badges -> savour -> GAP 3.4s -> next cycle`), pairs
   while there is room, solos after.
2. **Gap-fill pass.** Cycle planning still leaves holes when the assigner
   finds no match for a slot, so a second pass works on the *finished
   schedule*: it finds every bare stretch over `MAX_BARE = 12s` and drops a
   solo build into it, matched against that specific window. A gap that
   straddles a scene boundary takes whichever overlapping scene offers the
   most room.

Result on the five-minute cut: **longest bare stretch 8.2s**, median 4.2s,
39 unique slides (was 23). Industry practice is a visual event every 6-8s;
12s is our justified ceiling because reading a stamped document costs time
those channels do not spend.

**The scoring problem was a join failure, not a tuning problem.** Zero-score
fallbacks were not evidence of a weak scorer — they were evidence that the
semantics are registered on only one side:

| side | registered |
| --- | --- |
| cues (`full-episode-evidence-coverage.v1.json`) | **290/290** carry `claim_refs` from an 18-term controlled vocabulary, plus `active_world_plate.semantic_action` |
| approved source surfaces | **0/95** carry `claim_refs` or `cue_refs` |
| world plate library | 40/76 carry `semantic_tags` |

Selection was matching transcript prose against slide prose while a
controlled vocabulary sat unused on the narration side. The query is now
weighted — `claim_refs` x3.0, `semantic_action` x2.0, spoken excerpt x1.0 —
which took zero-score picks from 2 to **0** and lifted the median match from
0.19 to 0.26.

**The protocol gap that remains.** Evidence carries no `claim_refs`, so the
join is one-sided: we infer the evidence's meaning from its label and summary
rather than reading a registered claim. The real fix is to register the 86
stamped slides against the same 18-claim vocabulary the cues already use,
which turns selection from a lexical guess into a lookup. Also note
`candidate_evidence` already exists on 59/290 cues but is itself
`match_basis: lexical_*` — a cached version of the same guess, not a
registration.

Naming protocol to adopt alongside it: slide ids are deck-and-number
(`memory-supercycle-s03`), which says where a slide lives but nothing about
what it claims. Registration should attach meaning as data
(`claim_refs`, `semantic_tags`), never encode it in the filename.

## Part 9 — Operator corrections, 2026-08-25 (Steel and Paper build)

1. **Dynamic captions are mandatory, always.** Word-by-word (or word-group
   with per-word punch-in at canonical timestamps) — the Alicia kinetic
   grammar. A caption that swaps as a static block is a defect. Numeral
   words take the accent color.
2. **Plate floor: every episode ships ≥10 distinct world plates minimum**,
   OR a semantic-match plate board (existing plates, vision-passed against
   the script's scenes) approved BEFORE production, with gaps filled by
   generation.
3. **The evidence layer is sharp, never soft — and never an info card.**
   Text-on-a-rectangle "info cards" are banned as evidence documents
   ("fill-in paper toys", operator, 2026-08-25). An evidence document is
   one of exactly three species, in preference order:
   a. **the cited source's real chart** — for answer-format videos, a
      clean frame from the target's own video, their branding and source
      line intact (the frame IS the citation; matches the open-attribution
      ruling in doc 35);
   b. **a real chart we build** — crisp vector (hyperframes/Remotion in
      production; sharp SVG in review builds), typeset numerals, and REAL
      data wherever a public series exists (yfinance needs no key) with
      the source and window labeled exactly;
   c. **a registered generated infographic** — the DMP/teacher-stamped
      deck pattern: typeset slides produced by the generation loop, then
      figure-verified and registered before use.
   A statement that is pure prose (no figure, no chart) belongs in
   narration or captions, not in a dock.
4. **Style vocabulary split**: generated world plates are prompted as
   **woodblock vox newsprint** (the style family's actual register —
   carved ink contours, flat editorial color). **Washi paper is reserved
   for the evidence-dock chrome** — the translucent layer evidence is
   pasted onto. Prompting plates as "paper collage" drifts the world
   toward paper toys; the paper texture belongs to the dock, not the
   world.
5. **Editorial flags never reach narration.** `[verify]` and kin are
   pre-production workflow marks; verification completes BEFORE
   scripting. The TTS layer now strips any leaked bracket flag with a
   warning (audio_synth `_EDITORIAL_FLAG`), but the standard is that
   scripts arrive clean.
6. **Structure narration around the provider's cut points.** Scene/segment
   boundaries fall on paragraph ends with a settle pause; segments respect
   the ≤3-break-tag ration (split the segment rather than exceed it —
   overload causes audible speed-ups); full-episode audio is re-encoded
   through one concat pass so seams never emit fragments.

### 9.7 Host-in-world plates approved (operator, 2026-08-25)

The host-in-world experiment passed: generated host shots inside world
scenes are an approved PLATE species (claim `finance-host-in-world-exp-1`
is the reference wave — identity held across six scenes via reference
conditioning). Follow-on standard under test (exp-2): host-EVIDENCE
interaction plates — the host gestures at diegetic evidence surfaces.
Generated pixels carry only stylized chart SHAPES or BLANK framed
surfaces (generated_text_rule holds); the edit composites the real sharp
evidence into the blank surface, so the host physically presents the
evidence layer. Open item: glasses render cobalt vs spec black — pending
operator canon call.

### 9.8 Generated text, conditionally re-licensed (operator, 2026-08-25)

Amendment to the generated-text prohibition: when a generation is
conditioned on ACTUAL reference images (a real chart, a registered slide,
a verified evidence frame), the generated output MAY carry typeset text —
under a two-gate release:

1. **Codex verification**: the generating/verifying agent reads every
   legible string and numeral off the generated image and checks each one
   against the reference images and the claim's figure manifest; any
   string not present in a reference is a FAIL (regenerate or blank the
   surface). The verification report ships with the delivery.
2. **Operator approval**: verified-text assets remain quarantined until
   explicitly approved on the contact sheet — text assets never ride a
   wave approval implicitly.

Unreferenced generation keeps the absolute ban: no text, shapes-only
echoes, blank diegetic surfaces. This is the DMP-deck pattern
(antigravity-registered slides) generalized to the claim loop.

### 9.9 Preference order for host+evidence (operator, 2026-08-25)

The DIEGETIC COMPOSITE is the default whenever it can be prompted
cleanly: generated pixels carry the host's gesture and a blank (or
shape-echo) evidence surface; the edit composites the real sharp evidence
into the surface the host is physically presenting. Rationale: the
interaction is baked into the plate — motion and life come built in —
while the evidence layer stays code-perfect and swappable. Verified-text
generation (9.8) is the exception path, for assets where the type must
live in the artwork itself (title worlds, stylized prints). Prompting
craft for the default: blank surface as flat-on as composition allows,
simple charcoal frame, explicit "the blankness is the deliverable,"
gesture vocabulary named (presenting, pointing, holding toward camera,
fingertips beside).
