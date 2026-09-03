# 29 — Evidence Motion Standards (Gemini findings + v1 momentum + linked choreography)

Status: accepted working standard, 2026-08-24
Proven by: `claude.ai/code/artifact/57eacb95-7edd-41ca-aec3-086ea10a5ea3` (24s
interactive proof, beats 02–04 of the current-bubble opening, scrubbable)
Supersedes: nothing — this is the doc the `learning/` folder stopped writing
after 2026-08-16. It consolidates the Gemini evidence-dock findings, the
hyperframes-opening-v1 momentum mechanics, and the rules discovered while
rebuilding the braid with real teacher-stamped evidence.

> **STATUS: DOCTRINE — the production bar for every channel.**
> This document grew by amendment: Parts 1–8 are the original build,
> Part 9 is fourteen operator corrections layered on top. **Read the
> current state below and stop there.** Everything under it is the
> reasoning trail — go there to learn *why* a rule exists, never to learn
> what the rule is.

## Current state — what actually governs production

Consolidated 2026-08-28. Where this section and anything below it
disagree, this section wins.

**The lane.** Every channel ships on the scene-evidence lane (Part 8):
one ken-burns vector per scene, translucent washi docks with opaque
documents inside, verbatim badges, word-timed kinetic captions, wipes on
evidence-free boundaries - except evidence that PERSISTS across a boundary, which holds untouched while the front passes (s9.15). Held stills with hard cuts are a defect. Lanes
differ only in scripting — theme, audience, voice. *(§9 C1)*

**Plate density is runtime-derived.** Target **runtime ÷ 12s** distinct
world plates — a 7-minute episode needs ~38, not 10. Hard ceiling 20s on
one plate, and only when two strong evidence documents dock over it.
Thumbnails, avatars and banners are not world plates. *(§9.13)*

**Captions are dynamic, always** — word-by-word punch at canonical
timings from the voice-track words sidecar, numerals accented, never
resampled. A caption that swaps as a static block is a defect. *(§9.1)*

**Evidence is sharp, never an info card.** Three species, all specified
in doc **39**: the *data document* (dark ground, sans, a measurement), the
*record document* (paper, typewriter, one highlighter stroke — quotes,
transcripts, filings), and the *instrument reading* (our own measurement,
with method, period, tripwire, status, signal class and its caveat).
Prose on a rectangle is banned. *(§9.3, 39 §10/§12)*

**Rebuild, don't extract.** Every chart is ours, built from real data or
cited verbatim figures with attribution. Frame extraction from
third-party video is retired except the brief on-screen citation moment.
Series we cannot fetch wait — they are never eyeballed. *(§9.11)*

**A stored label is evidence, not authority.** A label change is a flag to
investigate, not a verdict: check whether the product changed or only the
annotation, and resolve against the authoritative map. *(39 §12 —
recorded after a wrong retraction in both directions)*

**Style vocabulary.** World plates are prompted **woodblock vox
newsprint**; washi paper is reserved for dock chrome only. World plates
**may** show screens, monitor walls, boards, gauges and gestural trend
lines as scenery — what they may not carry is a *legible* numeral or
label asserting an unsourced figure. *(§9.4, §9.14)*

**Host and evidence.** Host-in-world plates are approved; the **diegetic
composite** is the default form — host gestures at a surface, real
evidence composites into it. Generated text is licensed only with real
reference images, agent-verified against the required string list, and
operator-approved. *(§9.7–§9.9)*

**Docks.** Finance-niche single-plate episodes run docks ~20% larger
(paired 864px, solo 1056px) with sleek one-baseline pills. *(§9.10)*

**Narration hygiene.** Editorial flags (`[verify]` and kin) never reach
narration — verification precedes scripting. Recording follows the
MASTER TAKE rule in doc **37 §8**: episodes ≤~9k characters record as one
request; scene cuts are timestamps, never audio seams; splice-repair is
banned. *(§9.5, §9.6)*

**Process.** A dispatched `WORK-ORDER.md` is frozen — corrections open a
new claim, never a patch to an order a running agent already holds.
Nothing promotes out of review quarantine without an operator-approved
contact sheet. *(§9.12)*

---

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

### 9.15 The curtain, persistence, and the recovered showcase mechanisms (operator, 2026-08-29)

Re-reading `samples/gemini-scene-evidence-pipeline-showcase.html` (the
actual Gemini artifact, not this doc's summary of it) recovered two
mechanisms Parts 6/8 lost in translation, and the operator issued three
rulings. Where these conflict with anything above, THESE win.

1. **The wipe is the CROSS-REVEAL with carried light** (settled same day,
   after the curtain was tried and rejected on review). The showcase's
   opaque curtain was ported first and read as a blackout blink at every
   boundary - a flat panel sweeping a full frame is the crudest mechanism
   in that demo, and s8.15 had already evolved past it. The reviewed form:
   the incoming plate cross-reveals under the quart front with the ink
   seam, and everything that belongs to the outgoing page - a card ending
   at the boundary, the wash, the spotlight, the card's shadow - is
   CARRIED OFF BY THE SAME FRONT at the same progress. Nothing fades on
   its own schedule at a boundary. Lesson: an ancestor artifact is where
   doctrine CAME from, not where it is - a reviewed refinement outranks
   the demo it refined.
   *Implementation check (2026-09-01):* this ruling was silently
   overwritten on 2026-08-30 by the remotion-ui directional-wipe port
   (dd9e476), which swapped the reviewed hard `inset()` front for a
   feathered gradient mask + DEPTH parallax. On review the feather read
   as a fade, the two moving pages read as a wipe going both directions,
   the reveal direction flipped, and the outgoing-light mask was the
   MIRROR of the front (`100 - edge`), so the wash vanished the instant
   a wipe began and dimmed the clean incoming plate as it finished - a
   bright pop at every carried-light boundary. Symptom patches hid it
   for a day; `git log -S` found it; the hard front was restored
   (75a0f13). Two standing checks: (1) a port that changes what a
   reviewed shot looks like is a proposal for A/B, not a change; (2)
   verify carried light by measuring right-half luminance across a
   boundary - a wipe is a monotonic ramp; a pop-then-fall is a light
   leaving on its own schedule.
2. **Evidence may persist across a boundary** (operator): a document whose
   claim spans scenes holds untouched while the world wipes beneath it.
   Same-slide docks in adjacent scenes coalesce into one span; the entrance
   never re-runs. This supersedes Part 6's evidence-free-boundary rule FOR
   SPANNING EVIDENCE ONLY; a card ending at the boundary is carried off by
   the front.
3. **Near-boundary exits snap to the boundary.** An exit authored within
   ~1.4s of a scene turn used to fire fade + wash-off + wipe in under a
   second (the "repaste" flash). Those exits snap to the boundary; exits
   further out are deliberate early clears and keep their fade.
4. **The world leans in with the argument** (showcase `worldScale` steps
   1.02 -> 1.08 across a build): each card landing and badge stamping eases
   the plate in another notch (+0.008, 0.6s expo-out) on top of the
   authored drift. Continuous drift alone reads as weather.
5. **No title layer on the dock** (operator): the card IS the document; a
   label above it spends the frame's best real estate restating what the
   viewer sees. `title` lives in the timeline for manifests, never drawn.
   (The showcase's EVIDENCE-n chips and citation footers were already
   retired by 8.8; the title bar follows them.)
6. **The plate cadence** (operator): two evidence pieces per 12-20s plate,
   two badges each, a breath between, then wipe; a plate that cannot field
   two honestly carries ONE BIG piece (solo 1056px); under ~8s, one or
   none. Documents with no readable figure clear early and small.
7. **Caption safe zone** (operator, 2026-09-02): YouTube's hover controls
   bar overlays roughly the bottom 10-12% of the frame in the normal and
   embedded player; anything placed there is hidden whenever the mouse is
   on the video, and only fullscreen looks right. The kinetic caption
   baseline sits at **120px from the bottom of the 1080p stage (11.1%)**,
   never lower. Was 38px (3.5%) through episode one and got cut off. The
   check: with the player at normal size and the pointer on the video,
   every caption word is fully visible above the scrub bar.

### 9.16 Motion verification and authority (operator decisions, 2026-08-29)

1. **The gold standard is a RENDERED reference, not a table of constants.**
   `current-bubble-five-minute-v4` (the reviewed Gemini-era build) is the
   motion reference; any motion change ships with a side-by-side boundary
   comparison against it. Constants describe the reference; they do not
   replace it.
2. **The boundary filmstrip is a HARD GATE.** Any change touching motion
   produces played-through frame strips of all three boundary classes -
   bare-to-bare, evidence-ending, evidence-persisting - judged by eye
   before it reports done. A single still at a chosen instant is how a
   mis-mapped clip shipped twice in one day: the swept-card clip was
   computed in the card's own coordinate space and only happened to align
   with the stage front at the verified frame. The front is a STAGE
   position; per-element clips map it into element coordinates.
3. **Exit style is hybrid-authored.** Mechanical default (docks wipe, bare
   cut) with an authored per-window override in the shot table where the
   meaning differs (Part 6: cut = contrast, wipe = continuation) - the
   register shifts take cuts.
4. **The lean-in is cut until proven.** It returns, if ever, as a
   side-by-side A/B of one scene judged in isolation. Item 4 of 9.15 is
   suspended accordingly.

### 9.17 The choreography statement, and the scrim serves the evidence (operator, 2026-08-29)

1. **Every build emits a CHOREOGRAPHY STATEMENT** (`emit_choreography.py` ->
   `build-f/CHOREOGRAPHY.md`): the time-ordered ledger of every element
   entering and exiting - slot, side, hold, HOW it leaves (carried by the
   front vs fades in place), when light rises and falls - with slot-level
   gates run on it (min hold, drive-by, awkward-zone exits, wash-gap
   merging, same-slide re-entry). This is s8.2's "the timeline is data"
   made enforceable: the reference builds were auditable because state was
   declared; state that is only derived per-frame cannot be reviewed, and
   every motion defect of 2026-08-29 was caught by the operator's eye
   instead of a gate. On its FIRST emission the ledger exposed a swept
   card re-landing 0.3s later on the opposite side.
2. **A lone dock takes slot 0** - the stage - always. Coalescing keys on
   the SLIDE alone: the same document persists across an authored slot
   change rather than being swept and re-landed.
3. **The scrim quiets the evidence zone; it is not stage lighting.**
   Gradient peak .34 (was .62), spotlight edge .24 (was .44). At the old
   strength every card arrival and departure was a lighting event - with
   evidence on screen ~80% of runtime, darkness sloshed across every
   scene. The document is opaque cream on a dark plate; it needs a
   whisper. If removing the scrim would not hurt legibility, it is still
   too strong.

### 9.18 Strong match or nothing (operator, 2026-08-30)

*"Let's not carry weak evidence for the sake of carrying evidence anymore
— if we don't have strong matches drop the evidence and we can either
create proper evidence or leave the plate blank if that's the proper
move."*

- **A dock exists to prove a spoken claim.** `anchor_kind: claim` is the
  standard; `contextual` — a slide that merely shares a theme with the
  beat — is no longer a reason to dock. A bare plate beats a weak dock.
- **A slide that carries complexities the narration never discusses is a
  weak match by definition**, however handsome: the ladder ("the froth
  cracks before the giants do"), the racetrack, the CXMT battlefield and
  the paper-bubble mechanics all belong to a memory/Korea episode, not
  this one. Fifteen deck/matrix docks were cut from Steel and Paper under
  this ruling; the episode's own instruments (THE TEST scorecard, the
  yardstick) took the primary slots their placement had been demoting.
- **Applied test:** if the viewer paused on the card, would the narration
  they just heard explain what they're reading? If not, drop it — and
  either build the proper evidence or let the plate carry the beat.

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

### 9.10 Finance-niche dock scale + era-correct clip extraction (operator, 2026-08-25)

1. **Dock scale is niche-tuned.** Chart-reading niches (finance) run
   evidence docks ~20% larger than the base grammar: paired docks ~864px
   (base 720), solo ~1056px (base 880) on a 1920 stage, tops raised to
   keep them seated. The plate-is-hero rule still binds — the wash stays
   banded and the chrome translucent.
2. **"First stable frame" is NOT a sufficient extraction criterion.** An
   animated source chart's stable end-state often shows the PRESENT-DAY
   view, which contradicts a badge naming a historical era (caught: a
   "Fed 1999" dock showing a chart panned to 2026). The criterion is
   ERA-CORRECT FOCUS: capture at the moment the claimed figures are the
   visual focus (callouts drawn, era marker highlighted), inside the
   narration span, and verify the visible era matches the badge before
   binding. Evidence orders must state the claimed era per clip slot and
   require the agent to record which visual state was captured.
3. **Pills are sleek, one-baseline rows.** Badge pills run label · value ·
   tag on a single baseline (slim padding, value ~23px) so the document
   fills its own card; the stacked two-row pill is retired. The badge
   remains a stamp, not a panel.

### 9.11 Rebuild source charts — do not extract frames (operator, 2026-08-25)

Operator ruling, superseding the clip-extraction workflow in 9.10:
*"We should stop trying to take the images from their video, we will
either get the approval or simply remake the charts — there is no
copyright on charts, and we aren't using the animation effect they're
using anyways. We could literally just rebuild the charts using
hyperframes / yfinance."*

- **Default: rebuild.** Every evidence chart is OURS — built sharp
  (hyperframes/SVG/plot code) from real data (yfinance, public series,
  or the source's cited verbatim figures), labeled with the underlying
  source and window. Chart data carries no copyright; the source's
  *rendered pixels* are what we stop taking.
- **Frame extraction from a third-party video is retired** for the
  evidence layer. It returns only for the brief on-screen citation
  moment (crediting the source video, their branding visible) or when
  the source grants chart exports (outreach pending — their exports
  then supersede our rebuilds).
- Rebuilds citing a source's own figures use the verified-text lane
  (9.8): numerals verbatim from the cited claim, attribution label on
  the chart ("figures via Bravos Research / <their cited source>").
- Series we cannot fetch or verify are NOT approximated by eyeballing
  the source's chart — they wait for the export grant or
  operator-supplied data, and narration is written to survive their
  absence (doc 35 sources-to-verify discipline).

### 9.12 Work orders are immutable after dispatch (operator, 2026-08-25)

The mp-thumbs-wave-2 order was patched in place after the batch
dispatcher launched; the BM claim in the same batch delivered rotated
filenames and reference drift. Operator diagnosis: *"you tried to swap
after you already sent the workorder to codex, it probably already had
the context in memory."*

- Once a claim is dispatched, its WORK-ORDER.md is frozen. A correction
  means: stop/let the claim finish → reject at review → open a NEW
  claim (fresh id) with the corrected order. Never edit a dispatched
  order and hope the agent re-reads it.

### 9.13 Plate density is runtime-derived, not a flat floor (operator, 2026-08-25)

The ">=10 plates per episode" floor in 9.2 is a MINIMUM for a short
episode, never a target. Operator correction on the Steel and Paper
build: *"You don't have enough plates if you're running 80 second
deficits. You need 1 plate for every 12 seconds at least."* And the
ceiling: *"20 seconds on 1 plate would be the max, and that would be
expecting 2 pieces of strong evidence to cover."*

- **Target: runtime / 12s.** A 446s episode needs ~38 world plates, not
  10. Compute the target from runtime before opening any plate claim.
- **Hard ceiling: 20s on a single plate**, and only when TWO strong
  evidence documents dock over that stretch. A bare plate held past 12s
  with nothing docking is a defect.
- The 12s bare-stretch ceiling (9.2/Part 8) governs BOTH layers. A long
  bare stretch is not automatically an evidence shortfall — diagnose
  which layer is thin before ordering work. On Steel and Paper the
  83s stretch was read as an evidence deficit when the plate count (14
  world plates against a 38 target) was the larger half of the problem.
- Thumbnails, avatars, and banners are NOT world plates. Count only
  plates that can carry a scene.

### 9.14 World plates MAY show screens, boards, and trend imagery (operator, 2026-08-25)

Correction to an over-triggered review guard. On the wave-3 contact sheet
I rejected two good plates — a broadcast set whose monitor wall showed
charts, and a whiteboard with a descending trend arrow — reasoning that a
plate must not "assert a data claim it cannot source." That reasoning was
wrong. Operator: *"we should not be trying to cancel out screens and
chart type things. The way our evidence layers work will be more than
enough to prevent the clash"* and *"the downtrend arrow is not a real
chart and doesn't claim it, it's a vague image that the narration
covers."*

- **Screens, monitor walls, exchange boards, whiteboards, gauges,
  gestural trend lines and arrows are legitimate world-plate scenery.**
  They set a room. They do not claim a figure.
- **The evidence layer is what separates claim from décor.** Docks are
  visually distinct by construction — sharp vector inside washi chrome,
  verbatim badges, source-and-window labels. A soft carved arrow behind a
  translucent dock will never be mistaken for the dock's document, so the
  clash the guard was defending against does not exist.
- **The line that still holds is 9.8/C6**: no *legible* numerals or
  labels asserting a specific figure baked into a plate. Vague is fine;
  specific-and-unsourced is not.
- Review lesson: a rule's REASON is its scope. "The evidence layer is
  sharp, never soft" governs the evidence layer — extending it to police
  the world layer cost two good plates and would have thinned an episode
  already short on plate density (9.13).

### 9.19 The metallic slate text ramp (operator, 2026-08-30)

"We use too many greys on black" — and the operator's fix names the
direction: **the grey palette moves from neutral grey to metallic slate.**
Cool steel, not ash. On-theme for the channel and measurably brighter.

Text on the dark chart ground (#16181c) uses exactly three steps:

| step | hex | role |
|---|---|---|
| bright steel | `#F4F6F8` | titles, numerals, mark labels |
| polished slate | `#DCE3EA` | subtitles, row labels, series names |
| brushed slate | `#B8C4D0` | ticks, source lines, shares notes — **the floor** |

**Nothing dimmer than brushed slate ever renders as text.** The old
`#8b8f98` small-text grey (~4:1 on charcoal, gone after YouTube
compression) is what made "one bet / the old normal" unreadable.

**The two-tier rule extends INSIDE the chart.** The graphic palette
(crimson/teal/cobalt/amber/deemph) draws strokes and fills only. Any text
it colors — series end-labels, threshold labels — takes the TEXT tier
(`TPAL`: same hue, lifted: coral #FF8A8C, teal #3BC9B0, cobalt #8FB3F0,
sunflower #F5B72E, deemph → brushed slate). Graphic cobalt as label text
is the same failure as graphic cobalt on the pills.

Mirrored in the same commit: player template (`.ct/.cs/.csr` + `TPAL`),
evidence builder constants (`INK_1/INK_2/INK_MUTE`), pill label + ink
accent. DEEMPH `#6b6f78` survives as a *graphic* de-emphasis color only.

### 9.20 Topic-governed exits, and the two-chart open (operator, 2026-08-30)

**Evidence leaves when its TOPIC ends, never because a plate ended.**
"We shouldn't be removing evidence layers from the screen just for the
sake of removing evidence layers." A dock's exit is authored against the
narration - the last sentence that reads, cites, or leans on the card -
and holds across as many plates as that topic runs (the §9.15
persistence machinery carries it through the wipes). Plate boundaries
are for the WORLD layer; the evidence layer answers to the argument.
The old reflex - exit at the plate edge, re-enter on the next - is the
clipping look with extra steps.

**The answer-format credit beat is visual, not just spoken.** For an
answer video, the audience sees the chart being answered BEFORE ours:
ev-bravos-original-v1 (their two lines, their scale, credited in the
title block) holds from the hook's "fourth version of the same chart"
through both of their reads; our four-line version takes the same slot
at the moment narration starts adding layers. Draw delays are tuned to
the reads - semis erupt at "the chart's second line," memory at "one
layer their chart never drew." The handoff lands on a plate boundary so
the wipe carries the swap.


### 9.21 Purpose-built beats reuse, and audience units (operator, 2026-08-30)

**A non-specific card never appears twice when a specific one can be
built.** The concentration card was docked at two close beats; the
operator's ruling: build the evidence the beat deserves instead
(ev-hynix-steel-v1 - price vs its own operating profit - for the "More
bullish" beat). Reuse is a smell that the beat's real evidence hasn't
been made yet. A deliberate claim-then-verdict recurrence is still legal
when each appearance IS the card's claim - but reach for a purpose-built
card first.

**Figures speak the audience's currency.** The audience is American:
foreign-currency figures convert to USD at a real spot rate (source the
rate), with the conversion named in the source line. ₩37.6T is "a
$27 billion quarter."

### 9.22 Charts read like analysts, not toys (operator, 2026-08-30)

"We should be building actual charts that read like financial analysts."
A time series is a LINE, never a bar trio of period changes. The
analyst chrome is mandatory on data cards: labeled axes with units
($-formatted ticks via `yfmt:"usd"`, x-axis date ticks via `xticks`),
the basis stated in the subtitle, the source AND release named, the
last print called out (end labels carry the level), and reference/
trigger lines drawn dashed (`dash` on a series - fades in, never
draw-animated). The instrument's own decision rule belongs ON the
chart: the memory monitor shows its 12-month-average trigger line, not
just readings.

**Layout hygiene (operator, same day):** the x-axis band is RESERVED
(bottom padding widens when xticks exist) so the source line never sits
under the date labels; y ticks carry units (`yfmt:"usd"` or a `yunit`
suffix like "%"); every chart states its basis as a `ylabel` floating
top-left INSIDE the plot (FT convention - never on the subtitle line),
e.g. "index · 100 = 1 May 2026" or "USD per kilogram, log scale"; end
labels stay short (~6 chars) - the right margin is 120px and "off peak"
belongs in the badge tag, not the label.

**The combo convention (operator, same day):** when the story is
"event series drives a price," use the terminal layout - price line
above, the events as a volume-style HISTOGRAM in the plot's bottom band
(`eventbars`: teal up / crimson down, value atop each bar, landing on
the draw). One red bar in a row of teal bars needs no arrow. And PRINTS
ARE NAMED BY LANDING MONTH ("the August print" carries July's numbers)
and PLOTTED on information time - the day the market could know - never
on data time. A data-time plot misaligns cause and reaction.

**Ledger data hygiene:** SCML series queries filter
`data_tier='production'` and full periods only - beta ten-day partials
(`-P1/-P2/-P3`) are a different basis and print false spikes. The
ledger is DRIVABLE (its CLI ingests, monitors, briefs) - drive it for
fresh reads rather than settling for stale rows.
### 9.23 A chart carries its OWN story (operator, 2026-08-30)

"The charts need to fully communicate their own story without
narration." The monitor failed this three ways at once: an unlabeled
reference line ("what is the white dotted line?"), a floating
annotation with no leader to its point ("looks like an accident"),
and no date axis. The gates, all template-enforced now:

- **Every series on the plot is named** - reference/dashed series
  included (their end labels fade in with the line).
- **An offset annotation is TIED to its point** - |dy| > 40 draws a
  dotted leader from dot to chip automatically.
- **Log charts get date ticks too** (the my(y0) double-transform bug
  rendered them dateless - fixed; baseline is the pixel constant).
- The test: mute the narration, screenshot the chart, hand it to a
  stranger. If any ink needs the voiceover to explain it, the chart
  is not done.

### 9.24 The VERDICT STACK species (operator, s68, 2026-08-30)

At a verdict beat ("Everything we checked holds") the episode's best
evidence PILES UP over the world plate - not inside a dock card. The
stack mounts on the STAGE, full-frame (operator: "the evidence is
dancing around the world plate, not static on the evidence layer"):

- **Members are documents already shown** - each card is the PNG of an
  asset docked with its own source earlier; the stack re-presents, it
  never introduces.
- **Word-matched enters**: each card flies in from depth (translateZ
  -940, rotateY, transform3d-showcase vocabulary) on its verbatim
  narration beat; scattered asymmetric SPOTS keep the plate visible
  through the gaps; idle cards float.
- **The burst**: on the pivot line every card is thrown RADIALLY off
  its own bearing from stage center, spinning, staggered 60ms - the
  clear is part of the rhetoric (the case is made; now the turn).
- The host dock is an invisible lifecycle anchor; its window must
  extend ~1s past clear_at so the burst finishes ticking.
- Item beats are absolute times on the authoring clock - a retime
  regenerates them from their verbatim phrases.

**9.24b - the HYPERFRAMES blend (operator: "in that cut the evidence
is actually dancing").** What makes the pilot dance is not the
fly-ins, it is the FOCUS HAND-OFF: each proof enters LARGE near stage
center and stays there WHILE ITS PHRASE IS SPOKEN, then recedes to
its small rail spot exactly when the next proof's beat lands - the
composition renegotiates space on every beat. The active card drifts
continuously (slow sine wander + scale breathing); railed cards hold
almost still. Pose is a pure function of t (rail rect = base CSS,
active pose = transform), so scrubbing is exact. The last proof holds
focus until the burst.

**9.23b - a nickname is not a label; a citation is not a key (operator,
2026-08-31).** Failure class 11: INSIDER SHORTHAND. Every series names
WHAT IT TRACKS in audience words, inline on the chart (template renders
sr.name at the line's start, FT-style, revealed with the line). A
nickname ("the yardstick") may appear ONLY alongside its descriptor -
the measure leads, the nickname follows. Acronyms get a plain-word
gloss ("US Bureau of Economic Analysis data via FRED", never bare
"BEA"). The audit that caught this: the yardstick chart shipped with
TWO ENTIRELY UNNAMED SERIES - seven docked charts had unnamed lines.
The mute test now includes: "could a stranger say what each line IS?"

### 9.25 The screen never goes still; captions take the stage (operator, 2026-09-02)

Ruling E21. Steel and Paper shipped with 23% of its runtime in stretches
over 12s where nothing moved but the Ken Burns and a lower-third caption,
and its opening minute was the thinnest minute of the video (8.6 visual
events/min, 0.9 docks/min; a 14s still stretch from 0:57 - the first-drop
point). The s8.19 gap-fill existed but lived in the five-minute cut
builder and printed a number; the hand-authored Script F shot table never
had a density check run on it.

**Three mechanics, all gated by `scripts/gate_motion_density.py` on the
built timeline (exit 1):**

1. **Stillness ceiling.** No stretch longer than 12s without a visual
   event beyond Ken Burns - dock enter or exit, badge reveal, scene
   change, or captions in stage mode. 8s is the working target (industry
   6-8s; 12s is our justified ceiling because a stamped document costs
   reading time). Evidence enters at least every 45s in every phase
   including P1 and P6. Plate density runtime/12s and the 20s hold
   ceiling (s9.13) are checked on the same pass.

2. **Caption STAGE mode.** Part 5 defined one fixed lower-third anchor.
   That anchor is now the *shared-stage* position only. When no dock is
   up, captions move to the stage: centred in the frame (vertically in
   the plate's quiet zone, horizontally centred), ~64px at 1080 (vs 40px
   lower-third), 2-4 word groups, each word entering with an explosive
   pop (scale 1.4 -> 1.0 with overshoot, ~0.18s, `power3.out`), keywords
   in the accent colour, the spoken word at full white. When a dock
   enters, the caption demotes to the lower-third anchor inside the
   dock's enter duration (0.75s) and comes back to the stage when the last
   dock clears. The timeline carries the mode per row (`cap_mode:
   "stage" | "anchor"`); the player template implements both. Until the
   template ships stage mode, the gate lists every still stretch where
   stage captions are REQUIRED so the shot table can be authored against
   them, and prints the mode check as a JUDGE row.

3. **Savor beats keep their picture.** A savor is the payoff held on
   screen - the card up, the badge lit, the plate pushing in on it -
   never a bare plate with a slow drift. The `savour` duration in the
   motion plan (2.2s) is a dock hold, and a savour never extends a
   stretch past the 12s ceiling.

**Authoring rule for the shot table (stage 7):** every window row is
either under a dock, inside 12s of one, or carries stage captions. The
density rules were always "the check on this table, never its source";
the check now runs and fails.

Origin lesson: the Alicia kinetic caption study (Part 5) was read as a
caption style. It was a motion budget: on that channel the captions *are*
the screen whenever the evidence is down.

### 9.26 The LEDGER PAGE — the plate-chart species, the channel's signature (operator, 2026-09-02)

Ruling E22. Operator: *"if we could roll out a cream paper that gets
colored in with charcoal ink, writes on the graph, then builds the graph,
THAT would become the true channel-defining feature."*

**What it is.** A chart that is the WORLD layer, not a dock. The full
vision (operator, same day): *"cream page rolls out, hand scribbles the
charcoal/black fill, outlines a clean edge around what is now essentially
a chalkboard, then draws the axes etc, then builds the graph."* So the
page becomes a CHALKBOARD before the chart exists: a hand scribbles a
charcoal field onto the cream (scribble strokes accumulating, the
hw-callout-circle / whiteboard-ink stroke law), a clean outline draws
clockwise around the scribbled field and closes (outline-draw's hollow
conic border), and only then do the axes, labels and source get written
and the graph build - in chalk-light ink on the charcoal, with the cream
margin still visible as the page. Evidence may still dock over it in its
quiet zone. **The chalkboard is the default, not a stretch goal.**
Earlier attempts at "hand" work were hard because they tried to draw a
hand. The registry components the operator pointed at (hw-callout-circle,
whiteboard-ink, outline-draw, hw-underline) render NO hand: the scribble
is accumulating stroke paths with a nib dot at the ink front, the outline
is a border drawing itself clockwise, the marks are stroke reveals - and
they read cleanly because the stroke's motion carries the effect. That is
the mechanism here, verbatim: every "hand" beat is a stroke or mask reveal
derived from t (scribble field = strokes accumulating with a nib at the
front; outline = a conic-gradient border; writing = the per-glyph wipe).
The plain cream page is a comparison candidate in the prototype, not a
fallback; the cleanliness of a drawn hand is not a criterion, because no
hand is drawn. Operator, closing the point: *"if there is no good hand,
we just roll out the cream, bleed in the charcoal, use the outline
component, then build the chart - it's literally just stitching the
components together at that point."* That stitch (roll-out →
ink-bleed-reveal → outline-draw → chart-story) is the reference build;
the prototype is made in the hyperframes lane by mounting those
components in sequence on one timeline, and the player species is a port
of the picked stitch. It exists
because every chart the channel has shipped is an evidence card, and the
motion gate found the still stretches are exactly the windows with no
card - a plate that builds is a plate that is never still.

**Register (decided).** Cream paper `#F4E6C7` (the spine's paper token,
never the record-document's off-white), charcoal ink `#25313C`, one
accent from the six tokens for the emphasized datum, subtle newsprint
grain. It is the woodblock world's own ledger page. Docks stay near-black
so the two registers never blur. It is deterministic and real-data, so it
lives under the EVIDENCE text rule (exact numerals, source line on the
page), not the generated-imagery ban.

**Geometry and crispness (operator, decided 2026-09-02).** The page is
FULL cream first; the charcoal is then bled or drawn over it so that
only a cream-stained margin the bleed did not fully cover remains - not
a framed board on a page, a stained page. **The set-up is the drawn
part; the chart is not.** Axes, lines, bars and labels land crisp, exactly
as they appear in the components and in our current docks. Where a
display trick and legibility conflict, legibility wins: nothing muddies
the chart for a visual effect. The chalkboard is a WORLD plate; the
standard evidence docks remain exactly as they are today and may land on
it, so a busy variant (the bar race) is not held back by the board.

**The four beats, all derived from t (seek-safe, screenshot-render
safe, no wall clock, no Math.random):**

1. **Roll-out (0-0.6s).** The page unrolls from one edge: a `clip-path`
   inset that opens across the frame with a rolled-edge highlight riding
   the front (a narrow gradient band, like the wipe's carried light,
   s9.15). Seeded paper grain (feTurbulence, fixed seed) rides the whole
   piece.
2. **Ink writes (0.4-2.4s).** Axes, tick labels, title and the source
   line are WRITTEN, not faded: per glyph, a left-to-right `mask-image`
   wipe with an ink-soft edge (~18% of a glyph) and a nib dot riding the
   wet edge; each character carries a fixed seeded tilt and baseline
   drift (~±1.6°) so it reads as a hand and never wriggles after it is
   written; writing order is reading order, never re-ranked (harvested
   from remotion-ui `handwriting-text`, which is the whole distinction:
   a string is wiped, a real path is stroked). A pinned handwriting
   webfont; the generic cursive fallback is banned because it resolves
   per machine.
3. **Graph builds (2.0-4.0s).** Our existing draw: `getTotalLength`
   dash-offset for lines with the tip head and deposited dots (s9.23b
   series names revealed with the line); bars grow from the baseline
   (`scaleY`, origin bottom) in reading order; the emphasized datum takes
   the accent and its callout number rolls to the exact value
   (chart-story's contract: lands on the raw supplied value, never a
   re-rounded one).
4. **Accent mark (optional, on the tell).** An ink-bleed bloom (gooey
   filter: blur + alpha threshold, blobs merging then contracting) that
   resolves into the callout or a circled figure - reserved for the
   payoff, the tell, and the ring token, never decorative.

**Correction (operator, 2026-09-03) - the bleed is a SOAK, and the outline is
tight.** Seen on candidate C: *"that's not what I meant by bleed. The world
plate should enter as an unravelling, textured cream. Then a half savor,
then we literally bleed/seep the charcoal on to the page as if it is
soaking up ink, and then we use the outline component to draw the border
(100% tight match, not the open space like your example)."* So the beats
are now FIVE, and beat 2 changes mechanism:

1. **Unravel (0-0.7s).** The cream page enters as a textured unravelling -
   paper grain and fibre visible, the rolled edge carrying a curl shadow -
   never a flat cream slab sliding in.
2. **Half savor (0.7-1.5s).** The page holds, still, textured, empty. A
   breath before the ink.
3. **Soak (1.5-3.9s).** Charcoal SEEPS into the paper from several seed
   points and spreads outward as if the page were absorbing ink: feathered
   wet edges, darkening as it saturates, never contracting. The seep is
   clipped to the field's rounded rectangle, so the ink fills to a definite
   edge - a stained page with a cream margin. The registry
   `ink-bleed-reveal` (blobs bloom, merge and CONTRACT to reveal a mark) is
   the wrong mechanism for this slot and is retired here; the soak is ours,
   in the player, from t.
4. **Outline (+0.8s).** The clean edge draws clockwise EXACTLY on the
   field's boundary - same box, same radius, the stroke sitting on the
   charcoal edge. No gap, no open cream between the ink and the line.
5. **Ink writes, then the build** as before.

Operator, same exchange: *"that's why originally the idea was to
'scribble' the charcoal on to the page."* So the field has TWO mechanisms
and the page spec names one (`field: "scribble" | "soak"`): **scribble** -
the original idea - strokes accumulating one at a time with a nib at the
front (the whiteboard-ink stroke law), clipped to the field; **soak** - the
no-hand path - ink absorbed by the paper. Both end on the same definite
edge, and the outline traces that edge in both. The pick (Human Gate 1)
decides the default; until then the species defaults to soak.

And the paper itself: *"the border of the card would kind of appear
'textured' and 'splotched' - like a real woodblock parchment would look
after aging, 'coffee stained' might be the way to describe it."* The cream
margin carries seeded blotches with tide-line rings (a radial gradient
darkest at its rim, displaced by fractal noise so no edge is clean),
multiplied onto the paper at low opacity, concentrated at the corners and
the four bands where the margin meets the field. It is part of the page
from the first frame of the unravel - aged paper, not a stain that
arrives. Seeded by lpHash; never animated.

**Candidates rendered (P35 T1, 2026-09-03) - Human Gate 1 open.** The
stitch was built in the hyperframes lane from the verbatim registry
components (`content/video_engine/hyperframes/compositions/ledger-page-v1-{A,B,C}.html`;
lane-tokened copies of chart-story / outline-draw / ink-bleed-reveal in
`compositions/components/*-ledger*.html`, whiteboard-ink with a
14-stroke seeded field in `whiteboard-ink-field.html`). Three candidates,
one data set (the divergence end values 712.52 / 204.62 / 120.75 / 121.49,
exact): **A** plain cream page (comparison only); **B** the field
SCRIBBLED (whiteboard-ink strokes, nib riding, 3.55s); **C** the field
BLED (ink-bleed-reveal, six blobs merging then contracting, 2.8s) - the
operator's own sentence, so C is the working reference until the pick.
Filmstrips at 0.5s: `steel-and-paper/evidence/prototypes/filmstrip-ledger-page-{A,B,C}.jpg`;
renders under `hyperframes/renders/ledger-page-v1-{A,B,C}.mp4` (untracked).
Found while building: a mounted sub-composition does not inherit the
host's CSS variables, so the six tokens are set on each component copy's
`#root`; a sub-composition ends on its own intrinsic clock, so the page
composition ends with the chart's hold rather than outliving it. The
pick, the font (Human Gate 2) and the roll speed are recorded here when
the operator rules.

**Variants (same page, same ink):** line, bars, bar race (ranked bars
overtaking across periods, axis rescaling, accent handing to the leader),
decline (a line drawing downward while its value counts down), progress.

**Rules.** Data only from a `series.json` beside the page, with the
source written on the page last. One page per window; a page holds like
a plate (20s ceiling, s9.13) and its build phase counts as visual events
for the motion gate; its still hold does not. Ken Burns on a page is a
slow push only. Docks land in the page's declared quiet zone; a dock
never covers the graph's emphasized datum. The species is a PROPOSAL until
the operator picks from rendered candidates (harvest rule).

### 9.27 The MOTION MENU — opt-in species, each with a slot, a mechanism, and a gate treatment (operator, 2026-09-02)

Ruling E22 addendum. The registry items the operator flagged, read from
source, mapped to the slot each may occupy in THIS lane. Every entry is
harvested as a mechanism into the player (HTML + t-derived motion), never
imported as a runtime; every entry that changes a reviewed shot is a
proposal rendered side by side (REMOTION-UI-HARVEST lesson). Nothing here
replaces the s9.15 wipe or the dock choreography by default.

**Targeting law (operator: "one problem with this type of thing has always
been that we circle the wrong thing").** Any species that points, circles,
zooms, spotlights or underlines takes its target as a DECLARED coordinate
in the shot table - a datum index or series point on a ledger page or
chart dock, a plate `semantic` region for a world plate, a word span for
captions - resolved to pixels by the player at render time. Nobody
eyeballs a pixel. A species with no declared target does not fire.

| Species | Harvested from | Slot in this lane | Mechanism (all from t) | Gate treatment |
|---|---|---|---|---|
| **Ledger page** (s9.26) | chart-story value contract · bar-chart-race ranking · decline-chart · handwriting-text ink wipe · outline-draw · whiteboard-ink stroke law · ink-bleed | world layer; the payoff chart by default | roll-out → scribble field → outline → ink writes → graph builds | build = events; start = evidence entry; hold = still |
| **Plate life** | stop-motion-cadence | a bare world plate with no evidence | quantize t to 8/10/12 fps FIRST, derive all motion from the step; our cutouts throw-and-land with squash; 2-frame seeded boil | events while stepping |
| **Camera punch** | yt-camera-move | punctuation on a named object ("this iron spike") - the ring token, a plate object, a datum | ONE world-wrapper transform: zoom/slide/tilt with cubic ease and an edge-defocus pulse; never stacked with Ken Burns in the same window | one event at the punch |
| **Scribble callout** | hw-callout-circle | circling a DECLARED target on a page or dock; the label pops with momentum, shapes squash on contact | wobbled ellipse draws, optional scribble fill, connector; boils; stroke family plain/soft/sharp/spray | event at draw; target must be declared |
| **Focus zoom** | ui-focus-zoom | after a chart or document has entered, zoom + pan to an anchored region and hold dead still (the camera-servo law: micro-drift from integer sine cycles ending at zero) | one wrapper transform; optional halo at the anchor | event at departure and arrival |
| **Pull-back reveal** | pull-back-reveal | hooks that open on ONE large number, then recontextualize it: the detail holds, one decelerating pull-back reveals the headline and cards around it | reverse build of the evidence | events across the pull |
| **Focus rack** (proposal against s9.15's wash/spot) | focus-rack | two-evidence plates: focus shifts once between two cards at different depths through synchronized blur, dimming, scale and parallax, instead of clipping the wash/spot to the front | the operator's read: "this should stop a lot of the image cutting"; rendered side by side against the current light handling before any change | event at the rack |
| **Feathered spotlight** | yt-feather-highlight | dim the frame except a feathered ellipse that GLIDES between declared targets (a document region → a datum) | CSS-variable hole position/size, helpers tween it | events per glide |
| **Squiggle marks** | hw-underline | captions and page labels: hand-drawn underline, double-pass strikethrough, brackets that draw on; a CAPTION treatment layered under stage/anchor captions, on a declared word span | stroke reveal | counts as a caption event in stage mode only |
| **Whiteboard ink** | whiteboard-ink | the scribble field and any diagram the page needs: multi-stroke SVG paths drawn one measured stroke at a time with a nib at the active front, per-stroke cadence | strokes slot | events while drawing |
| **Outline draw** | outline-draw | the chalkboard's clean edge; also "proving" a callout box | hollow conic-gradient border drawn clockwise with a clean closure, ~0.8s | one event |
| **Radial reveal** | transitions-radial | revealing the ring token or a callback object FROM the point the narration names | `clip-path: circle()` / diamond polygon from a declared point | scene event |
| **Push hand-off** | transitions-push | dock A pushes dock B in (evidence hand-off), not scene transitions | x / scaleX / skewX on two stacked cards | event |
| **Beat-freeze chart exit** | beat-freeze-cut | leaving a chart: the final state freezes as a hit (flash, contour, badge) then a directional-stretch cut into the next plate; NOT a held still (that is the defect) | ramp → freeze → connector | events at hit and cut |
| **Weight-shift captions** | caption-weight-shift | the ANCHOR (quiet) caption when a document holds the stage: 300↔700 weight swap between lines in 100ms | font-weight tween | not an event |

Precedence: a species never fires inside the pivot's reversal, never
covers an emphasized datum, and never stacks two camera moves in one
window (punch, focus zoom, pull-back, Ken Burns are mutually exclusive per
window). The motion gate counts events as tabled above once the timeline
carries the species rows; until then the shot table declares them and the
agent verdicts them (CHECK-RESPONSIBILITIES R2).

### 9.28 The SURFACE GRAMMAR — page, dock, or transition, decided by rule (operator, 2026-09-03)

P35 T0. Operator: *"the first part of the plan is getting components
aligned and understanding how these things map over to our evidence
layer - what determines the full page surface, what belongs as pop-out
evidence on the plate, how do we determine the choreography that leads to
different outcomes / plate / evidence layers / transitions."* This section
is that map. Every shot-table row from here on names a **surface** and,
where a chart is drawn, a **builder**; the two axes are independent and
never merged (P35 Builder Architecture: `dense-line` is ours in the
player, `story` / `race` / `decline` / `combo` are each ported from their
own component).

**The surfaces.**

| Surface | Register | What lives on it | Motion it contributes |
|---|---|---|---|
| **PAGE** (s9.26) | cream `#F4E6C7` → charcoal bleed, chalk-light ink | a chart that is OURS, built from a `series.json` we own | roll-out → bleed → outline → ink → build (~4s of events); then a plate hold |
| **DOCK** (Part 3, s9.15) | near-black card, unchanged | anything READ: their document, their chart, a citation, a stamped slide, a record, an instrument | enter / badge reveals / exit (the events the gate already counts) |
| **PLATE LIFE** (s9.27) | the world plate itself | our cutouts on a bare plate, stepped-time | events while stepping |
| **NONE** | bare plate + Ken Burns | a savor that holds its picture (s9.25 #3), the pivot's reversal, a breath | none — must be < 12s or carry stage captions |

**(a) What earns the FULL PAGE.** All three must hold; any one missing
sends the chart to a dock.

- **A1 — the proof is ours.** We ran it, pulled it, counted it, drew it.
  The narration says so in the first person (the gate's `OUR_CLAIM`
  family: *I ran / pulled / checked / drew / measured / counted*) and the
  data lives in a `series.json` beside the asset with OUR source line.
  A series that re-plots their chart (`ev-bravos-original-v1`) is theirs
  even though we drew it: it docks.
- **A2 — it is carried by a series we own.** Exact values, labels aligned,
  source present (`ledger_page.py` validates; P35 T2). No series, no page.
- **A3 — it lands at a beat that TURNS the argument, or fills a still.**
  Turning beats: the mini-payoff before the promise (P1 B4), the catalyst's
  close (P2), the best evidence spent in P3's last unit, the pivot's
  THEREFORE (never the reversal itself — rule C4), the payoff delivery
  (P5, 60–70%), the tell, the ring close. Or: the window sits in the
  motion gate's M01 / M08 list with no dock inside 12s either side, and
  the chart under narration there is ours (A1, A2).

One page per window; the payoff chart of every episode is a page by
default (P35 intent); at least one more per episode.

**(b) What stays POP-OUT evidence (a dock).**

- **B1 — their evidence always docks.** Their chart, their document, a
  quote card, a stamped slide, a screenshot, a record: read, not built.
  Near-black, exactly as today. A page never carries their document.
- **B2 — our proof docks when the beat does not turn.** A supporting
  number mid-unit, a second view of a page already shown, a tile beside a
  page. `dense-line` on a dock is the ship state and stays available.
- **B3 — a dock may land ON a page**, in the page's declared quiet zone
  (`quiet_zone: left|right`), never over the emphasized datum (C2). Two
  docks over a page keep the s9.13 20s hold rule for the page.
- **B4 — a chart that is theirs but we extend** (the divergence pairing:
  their two lines plus our layer) is OURS for the layer we added and
  theirs for the rest: it pages only at a turning beat where the narration
  claims our layer ("one layer never drew" → page; "here's the original"
  → dock).

**(c) CHOREOGRAPHY at a boundary.**

- **C1 — leaving a page.** If the next beat continues the same proof
  (another datum, the callout, the comparison) → **beat-freeze chart
  exit** (s9.27: freeze as a hit, then the directional cut). If the next
  beat changes topic → the **s9.15 wipe**, with the page as the departing
  plate. A page never simply fades.
- **C2 — a dock landing on a page** enters in the declared quiet zone
  with the s9.15 carried light; the page's emphasized datum stays
  uncovered for the dock's whole hold.
- **C3 — one camera move per window.** Punch, focus zoom, pull-back and
  Ken Burns are mutually exclusive per window (s9.27 precedence). On a
  page, Ken Burns is a slow push only.
- **C4 — the pivot's reversal takes no species.** The visual register
  shift IS the motion (P4 QC); a page or a targeted species fires only on
  the THEREFORE after it.
- **C5 — a page holds like a plate.** 20s ceiling (s9.13); its build
  phase counts as visual events and its start as an evidence entry; its
  hold is still and needs a dock, plate life, or stage captions past 12s.
- **C6 — entering a page.** From a bare plate → the roll-out is the
  transition (no wipe before it). From a dock-bearing plate → the dock
  exits first (its own exit), then the roll-out; a page never rolls out
  under a live dock.

**(d) DENSITY — the E21 link, restated for surfaces.**

- **D1** — no window > 12s without a dock, a page build, or plate life
  (the gate's M01 with the page and plate-life events counted, P35 T4).
- **D2** — evidence enters at least every 45s in every phase; a page
  start counts (M03).
- **D3** — the opening minute is never the thinnest (M07); a page in P1
  is allowed only under (a), and the mini-payoff chart is the P1
  candidate by default.
- **D4** — stage captions cover what (a)–(c) leave bare (s9.25 #2);
  they are the floor, not the plan.

**The decision, per window (the census form).** For every shot-table
row: `start–end · plate · beat · current docks · SURFACE (page / dock /
plate-life / none) · builder (if a chart) · rule letters`. A row whose
surface is `none` for more than 12s cites D4 (stage captions) or is a
defect. The census for Steel and Paper build-f is
`build-f/SURFACE-CENSUS.md`; the re-script's shot table starts from it,
after the verbal rewrite names the pages (P35 execution path 7).

**Who verdicts.** (a)–(d) are declared by the shot table and verdicted by
the runtime agent per window until the timeline carries the species rows
(CHECK-RESPONSIBILITIES §3, R2); the motion gate then counts what it can
(P35 T4).
