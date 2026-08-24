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
