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
