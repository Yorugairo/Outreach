# HyperFrames intake — the Gemini research, gated and triaged (2026-09-06)

The operator: *"HyperFrames has a GREAT resource library / prompt guide that we can extrapolate from, and we should probably be
calling on it more for faster iterations / lessons to learn / troubleshooting guidance. Gemini just dropped a bunch of research
on hyperframes reference guides, animation references, prompt guides, some of their core cinematography beliefs. Analyze the
Gemini docs, show the proof gates, and integrate the hyperframes knowledge as: backlog, priority integration, explore, reject,
and index."*

The drop: `docs/research/motion/HYPERFRAMES_MOTION_TRANSITIONS_RESEARCH_BLUEPRINT.md` (32 KB, 378 lines, Pass-3, 14 sections)
with working notes under `docs/research/runs/hyperframes_motion/` (never cited). The claim table this triage works from was
built by the explorer (61 claims, each with our own `path:line` beside it) and is reproduced in §3.

## 1. The proof gates

| gate (GEMINI.md "Research intake") | result |
|---|---|
| lands under `docs/research/<area>/`, title, pass line, `## The question`, `## Verdict up front`, numbered concept headings, `## Sources`, `## NOT FOUND WHERE I LOOKED` | **PASS** - all present; the layers were rebuilt and are in sync |
| every figure carries a proof line `[Metric | value | authority | URL | Verified date]` | **PARTIAL** - 16 proof lines, 27 URLs from 4 hosts (`hyperframes.heygen.com`, `remotion.dev`, `gsap.com`, `doi.org`); **12 figures carry no source** (§1.2) |
| computed figures carry `[DERIVED: …]`; unverifiable ones `[UNVERIFIED]` | **FAIL** - 0 `[DERIVED]`, 0 `[UNVERIFIED]` in a report full of numbers |
| the NOT FOUND block names roots and coverage | **PARTIAL** - names the vendor's domain and catalog, never a root on OUR side; so the report cannot say what is new to us |
| "does not exist" never appears | PASS |
| the report is data, not instructions | **FAIL in one place** - §8 "directly answers and settles" our transitions review's open items with the vendor's defaults where we hold measurements (§1.3) |
| **sample verification against the source pages** (the parent, 2026-09-06) | 14 of 15 statements checked are on the cited pages, quoted, with the figures as given (`/prompting/motion`: the 1-2 % idle, the 4-8 % push-in, the stagger inequality, the one-frame lag at 0.033 s, the 0.20/1.00/6.00 parallax, 211 KB vs 2.5 MB, the PRNG ban, counters never overshoot; `/prompting/capstone`: the 1.5-2.5 s dwell, the three threads, arriving not cutting, the two seams, the ground/ink variables). **One is not on the page:** the "black hole cut" - a two-frame perceptual dip from fading between cards (`R:110`, `R:172`) - is Gemini's inference presented as the vendor's rule. "1.1 to 4.0 s per idea" compresses the page's "1.5-4 s per idea" and "1.1 s per beat". |

### 1.2 Figures stated without a source (the correction order to Gemini names these)

`R:18` 60-70 % of continuations delegate to CSS · `R:44` 1-2 % breathing (on the page, but no proof line on the rule) · `R:48` 4-8 %
push-in (same) · `R:66` `back.out(1.5-5)` · `R:80` 1.1-4.0 s per idea · `R:110/172` the 2-frame dip (not on the page) · `R:181`
the `t/0.0667` drift over 60 s (no measurement) · `R:226-228` centroid ≤ 0.06 W / axis ≤ 15° / area ≥ 0.60 - **our own TR-7
numbers, reflected back unattributed** · `R:274` dissolve 0.35-0.45 s · `R:275` "HyperFrames' 0.50 s calm / 0.35 s fast wipe
benchmarks" (appear nowhere else in the report, and the symbol `WIPE_S` does not exist in our engine) · `R:278` the transition
"fits inside the gap" · `R:280` the cream scales 1.02 → 1.00.

### 1.3 Where the report argues with measurements

- `R:110/172` fade-through-black is "the cardinal anti-pattern" - **E47** enters the dip through black into our kit because the
  reference does it at 35 of 99 boundaries, 0.47 s each, measured (`46-REFERENCE-RHYTHM.md` §46.5).
- `R:275` "validates" the 0.62 s wipe - **E47 §3** retired the wipe as the default; the reference wipes 0 of 99.
- `R:126` cuts snap to musical beats - **M13 / doc 46 §46.6**: ours land in speech gaps, 3 frames before the next word's onset,
  measured on 99 boundaries.
- `R:73-76` foreground at 6.00× the camera rate - **doc 49 §49.5**: parallax displacement over 20 px melts our plates, measured
  from the installed node source; 0.10-0.12 intensity is the gate.
- `R:80` 1.1-4.0 s per idea - doc 49 §49.6 for shorts agrees; for long form the reference's ASL is 6-10 s, measured.
- `R:44` vs `R:301`: the report says every hold breathes 1-2 % AND that holds must stay still - both as the vendor's doctrine.

**Verdict on the drop:** rich, mostly real, and usable - once its numbers are tagged and its §8 is read as a second opinion,
not a settlement. The correction order asks Gemini for exactly that.

## 2. The triage

**Priority integration** - cheap, sound, and lands in work already in flight (P47, TR-3, the skills):

| id | item | from | into |
|---|---|---|---|
| HF-1 | **Quantise stepped clocks on the integer frame index**: `frame = round(t·fps)`, `step = floor(frame / hold)` - never `floor(t / 0.0667)`. Ours quantise on elapsed seconds × fps at `plate_life` (template `:2794`, `LIFE_FPS: 10`) and `stepClock` (`ink.mjs:157`, `SOAK_STEP.FPS: 8`); the renderer seeks at `frame/fps` doubles, so the float product can sit a ulp under a boundary. The drift claim is unmeasured, the arithmetic is right, the fix is one line each. | `R:181-193` | **P47 T1** (the stop-action clock) + `ink.mjs` |
| HF-2 | **The one-frame lag for what a thing drags** (a shadow, a bracket's tick, a badge's housing settles exactly one frame after the primary, 0.033 s at 30 fps) - the number E45's docks and P47's `land` lack | `R:67-69`, verified on `/prompting/motion` | **P47 T1** `land` and the dock's park (a `lag_frames: 1 [DERIVED: HyperFrames, verified 2026-09-06; measure on ours]` dial) |
| HF-3 | **Stagger law**: every offset shorter than the animation it offsets (`τ_offset < τ_duration`), and **never delay the focal element** - only supporting elements stagger. Ours caps the total (`items × stagger ≤ ~0.5 s`, the skill) without the per-offset bound or the focal rule | `R:51-55` | doc 29 §9.15 (an authored rule), the dock/badge choreography (E45), the hyperframes skill's stagger adapter |
| HF-4 | **Three SVG draw-on hazards** into our stroke engine and the skill's `svg-path-draw.md`: `stroke-linecap: round` paints a dot at zero length (gate opacity until draw onset); a path needs a static `d` before `getTotalLength()` or Chromium returns 0; multi-value CSS dasharrays fight a draw-on. The skill file uses round caps without the warning. | `R:346-350` (the static-`d` line verified) | `stroke.mjs` / the template's draw-on; `.agents/skills/hyperframes-animation/rules/svg-path-draw.md` |
| HF-5 | **`min_jerk` on by default for directional moves and wipes** - an outside second to TR-3, which already orders the flip and the eye test | `R:276` | TR-3 (no new item) |
| HF-6 | **Directional easing grammar** as an authored rule in doc 29: entrances ease out, exits ease in, on-screen shifts in-out, impacts in - the skill holds it, doctrine does not name it | `R:60-63` (skill `gsap-easing-and-stagger.md:19`) | doc 29 §9.15 one paragraph; P47 T1's `throw`/`land` use "impacts ease in" |

**Backlog** - real gaps, bounded builds, not in flight:

| id | item | from | cost |
|---|---|---|---|
| HF-7 | **The four film-level invariants** (Message · Arc · Audience · Mood) as the declaration block at the head of every shot table and research order - E27's package and the FULL-VIDEO-MAP spine hold the first two; the block makes all four one line each | `R:290-295` (verified) | a header in `SCRIPT-PATTERN-KIT.md` and `build_short.py`'s table; the Gemini research profiles' storyboard prompting |
| HF-8 | **The One Breather**: name exactly one deliberately calm beat per film, so the rest is not over-animated to compensate; ours has the savor per page, nothing per film | `R:302-303` (verified) | one field on the shot table, one INFO row in the motion gate |
| HF-9 | **The per-frame job schema** `[focal]` and `[roles]` (the single entity the eye lands on; foreground / supporting / background) on every shot row - `[persuasion]` and `[beat]` we already carry in the craft map and the beat tags | `R:306-314` | two fields on the shot table; D3's reading-order gate (49 §49.6) gets its input |
| HF-10 | **The negative list** for generated plates (no purple-blue gradients, no bokeh, no faux OS chrome, no drop-shadow cards) into the Flow/Omni prompt plan (`FLOW-OMNI-EXPLAINER-PROMPT-PLAN.md`) and the design skills' anti-slop gate | `R:304` | a paragraph |
| HF-11 | **Text behind the subject with occlusion** - spoken keywords land as display text behind the cutout figure; for StickMike shots the caption strip could sit behind the host | `R:130-132` | a compositing layer in the player (the host as a cutout over the caption plane); measure against E21's captions-are-the-motion |
| HF-12 | **The encoder-size stillness signal**: the last second's encoded size (211 KB frozen vs 2.5 MB live) as a corroborating metric for M01/M10 on a render | `R:45` (verified) | a line in `render_episode.py` + an INFO row |

**Explore** - contradictions with our measured or ruled positions, worth a measurement before any adoption:

| id | item | the contradiction | the test |
|---|---|---|---|
| HF-13 | **Does a held page breathe?** Rule 1 (1-2 % idle on every hold) vs the storyboard page (holds stay still) vs E21/M16 (the captions and the species are the motion; a page holds while its datum is lit) | the report contradicts itself; ours is retention-measured only as "pages hold" | one Tokyo v3 build with a 1 % breath on the held page, judged by eye, then the curve |
| HF-14 | **The camera never rests** (a 4-8 % push-in per scene, never decaying at the boundary) vs M09 (one camera move per window) and E44 §2a (no move inside the opening window unless a page lands) | neither side measured | a global-motion estimate per shot on the reference (`measure_cut_kinds.py`'s frames, the whole shot): does Wealth Logic's camera ever rest inside a shot? |
| HF-15 | **Arriving, not cutting**: the next region visible at the frame edge before the camera reaches it; the previous leaves by parallax - for our page → page world changes (the Meta page could arrive from the edge under the holdings page) | E47 gives world changes the dip and the blur-zoom, measured; the edge-arrival is a third, unmeasured | author one page-to-page arrival from the edge in v3 and watch |
| HF-16 | **The three threads** (the wire, the ruler, the protagonist chip) - one continuous line as the film's spine; for us the chart's baseline or the deckle carrying across page returns | ours persists the page; a thread across different pages is new | the holdings page's baseline as the wire under the Meta bars |
| HF-17 | **Occlusion beats blur as the depth cue** vs doc 29's open focus-rack proposal (the wash beat the rack, operator 2026-09-06) | both unmeasured; the operator already preferred the wash | one foreground occluder on a world plate, judged by eye |
| HF-18 | **A shader seam** (`sdf-iris`) for a world change where the page must stay visible through the aperture - our renderer has no shader path | new capability, no evidence it beats the dip | only if a v3 world change wants it; otherwise nothing |

**Reject** - on provenance or against a measurement:

| id | item | why |
|---|---|---|
| HF-R1 | the "black hole cut" (a 2-frame perceptual dip from fading between cards, `R:110/172`) | not on the cited page; the reference dips through black at 35 of 99 boundaries, 0.47 s, measured (E47) |
| HF-R2 | §8's "settlements": TR-1/TR-11 "eliminates the reset cost of the cut", the `WIPE_S` validation, TR-9's 1.02 → 1.00 cream scale | TR-1 is closed by our measurement; the wipe is retired (E47 §3); the symbol and the scale are unsourced; §8 is a second opinion, not a settlement |
| HF-R3 | cuts snapped to musical beats (`R:126`) | we cut to speech, 3 frames before the next word's onset, measured on 99 boundaries (doc 46 §46.6) |
| HF-R4 | the 6.00× foreground parallax as a rule for our plates (`R:73-76`) | doc 49 §49.5: Δ > 20 px melts the plate, measured from the node source; the ratio stays as the vendor's number, indexed |
| HF-R5 | 1.1-4.0 s per idea for the long form (`R:80`) | the reference's long-form ASL is 6-10 s, measured; the shorts pulse (doc 49 §49.6) already agrees for shorts |
| HF-R6 | `back.out` overshoot as house physics (`R:66`) | our own skill demotes it to a playful register; the engine's spring is the analytic 4 % (doc 42 §42.2) |
| HF-R7 | the two-colour rule's third-hue ban (`R:299`) | our brand tokens assign five hues by role (coral negative, teal positive, sunflower attention, cobalt the one block); the principle "emphasis by scale, weight, density" is kept, the ban is not |
| HF-R8 | the ARAP invariants as a HyperFrames finding (`R:226-228`) | they are ours (TR-7), reflected back; the numbers stand, the attribution does not |

**Index** - already ours or already in the installed skills; indexed by the layers, no action:

motion is a claim (doc 51 §51.8, E21) · the slideshow anti-pattern (E46, retention-measured) · no `Math.random`, seeded PRNG (the
skills; our `lpHash`) · counters never overshoot (`counting-dynamic-scale.md`) · the 14 shader transitions and their duration
bands (`beat-direction.md`, the transition registry) · the GSAP cold-seek and relative-tween hazards (`rules-index.md:9-16`) ·
the FrameAdapter / seek-safety law (our template law, `29:2010`) · the Remotion transitions API (not our stack) · the dwell
1.5-2.5 s (the skills' "climax dwell", doc 29's savor) · the callback motif (the craft map, the spiral return) · the duration
tiers Calm 0.5-0.8 / Medium 0.3-0.5 / High 0.15-0.3 (a second reference beside our measured 0.47 and 0.27; TR-3's dissolve test
already sits inside it) · the single-file ground/ink variables (`brand-tokens.json`).

## 3. The claim table (explorer recall, 2026-09-06)

`R:` = the report; `T:` = the player template; `SK/` = `.agents/skills/hyperframes-animation/`; `OR:` = the rulings; `TR:` = the
transitions review. Relation: same / contradicts / new / adds a number.

| R:line | claim | proof | what we hold | relation |
|---|---|---|---|---|
| 11 | motion is an epistemic claim; more movement without motivation = a slideshow | none | doc 51 §51.8; E21 | same |
| 13 | movement does four things: direct attention, carry continuity, show change, express character; "this moves because…" | `/prompting/motion` ✓ | M06 (motion carries a beat), no taxonomy | new |
| 15 | one persistent element crosses every seam | none | doc 29 §9.15 item 2 (evidence persists), TR:42 | same |
| 16, 113-116 | dwell-and-sweep: 1.5-2.5 s at the hero moment | `/prompting/capstone` ✓ | doc 29 savor 0.7-1.5 s; the skills' dwell ≥ 1 s | same / adds a number |
| 17, 181-193 | quantise on the integer frame index, not `t/0.0667` | none | `T:2794`, `ink.mjs:157` quantise on seconds × fps | **contradicts** (unmeasured) → HF-1 |
| 17, 83, 196-207 | no `Math.random`; Mulberry32 | none | skills; `T:1901/2709/3232` seeded | same |
| 18, 145 | 14 typed shader transitions | `/packages/shader-transitions` ✓ | the skills' registry | same |
| 18 | 60-70 % of continuations are CSS | none (unsourced) | ours 100 % CSS | new |
| 18, 110, 172 | fade-to-black = a 2-frame "black hole cut" | none; **not on the page** | E47: the dip, 35/99 measured | **contradicts** (ours measured) → HF-R1 |
| 19, 237-241 | Remotion and HyperFrames share `p ∈ [0,1]` on a seek clock | none | `T:2975-3004` the same | same |
| 25-35 | displacement semantics; the justification sentence | none | M14 ties moves to events | new |
| 44 | Rule 1: every hold breathes 1-2 % | on the page, no proof line | M01/M02/M10/M16 events, no idle number | adds a number → HF-13 |
| 45 | 211 KB frozen vs 2.5 MB live | `/prompting/motion` ✓ | nothing | new → HF-12 |
| 48 | Rule 2: a 4-8 % push-in every scene, never a dead stop | none | M09 one move per window; `PUNCH_SCALE 1.14` | **contradicts** (unmeasured) → HF-14 |
| 48 | translating content = camera translation | none | the skills' viewport rules | same |
| 51-55 | Rule 3: `τ_offset < τ_duration`; never delay the focal | none | the skill caps the total | same rule, different number → HF-3 |
| 58 | Rule 4: compound properties only for one claim | none | the skill | same |
| 60-63 | easing grammar: out / in / in-out / impacts in | none | `gsap-easing-and-stagger.md:19` | same → HF-6 (into doctrine) |
| 66 | Rule 5: overshoot = mass; `back.out` | none | `spring.mjs` 4 % analytic; the skill demotes `back` | **contradicts** → HF-R6 |
| 67-69 | the one-frame shadow lag, 0.033 s | `/prompting/motion` ✓ | nothing | new → HF-2 |
| 68 | counters never overshoot | (untagged) | `counting-dynamic-scale.md:110` | same |
| 73-76 | Rule 6: 0.20× / 1.00× / 6.00× depth planes | `/prompting/motion` ✓ | doc 49 §49.5: Δ ≤ 8 px, > 20 px melts (measured) | **contradicts** (ours measured) → HF-R4 |
| 77 | occlusion, not blur, is the depth cue | none | doc 29's focus-rack proposal (blur) | contradicts (neither measured) → HF-17 |
| 80 | Rule 7: 1.1-4.0 s per idea | none (compressed from the page) | doc 49 §49.6 shorts 1.2-2.5 s; long-form ASL 6-10 s measured | same (shorts) / contradicts (long) → HF-R5 |
| 83 | Rule 8: on-twos by a seeded PRNG | none | `plate_life`, P47 T1 | same |
| 92-94 | the slideshow: enters → sits → fades | none | E46; TR:5 (n = 254) | same, ours measured |
| 107-109 | regions arrive, the previous leaves by parallax | none | §9.15, E45, §9.31 in spirit | new (the edge arrival) → HF-15 |
| 118-122 | the three threads: wire, ruler, protagonist chip | `/prompting/capstone` ✓ | §9.15 persistence per topic | new → HF-16 |
| 125 | seam 1: the `sdf-iris` | none | no shader path | new → HF-18 |
| 126 | seam 2: beat-grid hard cuts to music | none | M13, doc 46 §46.6 (speech gaps, measured) | **contradicts** → HF-R3 |
| 130-132 | footage order; text behind the subject | none | no such plate | new → HF-11 |
| 134-136 | one file, ground/ink variables | none | `brand-tokens.json`, the skills | same |
| 149-169 | per-shader genre table; tiers Calm/Medium/High | tiers ✓ (`/prompting/transitions`) | `WIPE 0.62`, `DISSOLVE_S 0.8`, `DIP_S 0.47`, `BLURZOOM_S 0.27` | adds a band → index; TR-3 |
| 214-220 | Flubber / MorphSVG / ARAP | ARAP ✓ (DOI) | doc 43 §43.5 methods A/B | same |
| 222 | ARAP polar decomposition (Alexa 2000) | DOI ✓ | doc 47 `det(J) > 0`; T4 | same |
| 226-228 | ΔC ≤ 0.06 W, Δθ ≤ 15°, area ≥ 0.60 | none | **TR-7's own numbers** | same (reflected) → HF-R8 |
| 246-250 | Remotion `TransitionSeries`, `Overlay` | `remotion.dev` ✓ | not our stack | index |
| 255-263 | FrameAdapter; bit-identical seeks | none | the template law; `render_episode.py` | same |
| 271-272 | TR-1/TR-11 "settled" by dwell-and-sweep + a wire | none | TR-1 closed by `measure_cut_kinds.py` | **contradicts the framing** → HF-R2 |
| 274 | dissolve 0.35-0.45 s | none | TR-3 already tests 0.35-0.5; the reference dissolves 0 of 99 | same item |
| 275 | `WIPE_S` 0.62 validated against 0.50 / 0.35 | none; the symbol does not exist | E47 §3 retired the wipe | **contradicts** → HF-R2 |
| 276 | `min_jerk` on by default | none | TR-3; `T:464` off | same → HF-5 |
| 278 | transitions inside the ≥ 0.30 s gap | none | M13 + doc 46 §46.6 (measured, finer) | same |
| 280 | the wipe-onto-cream mount, 1.02 → 1.00 | none | E45 §2 names both mounts; TR-9 | adds an unsourced number → HF-R2 |
| 288-295 | storyboard contract; Message · Arc · Audience · Mood | `/prompting/storyboards` ✓ | FULL-VIDEO-MAP, E27 | new as a block → HF-7 |
| 299-300 | two colours, never a third hue | ✓ | brand tokens: five hues by role | contradicts → HF-R7 |
| 301 | reveals on spoken cues; holds stay still | none | E44 (on the word); vs `R:44` | internal contradiction → HF-13 |
| 302-303 | the One Breather | ✓ | nothing per film | new → HF-8 |
| 304 | the negative list | none | anti-slop skills partly | new → HF-10 |
| 306-314 | per-frame schema: type · persuasion · beat · focal · roles | none | craft map, beat tags; no focal/roles | new → HF-9 |
| 316-317 | the callback motif | none | craft map; §9.31 | same |
| 323-344 | cold-seek and GSAP hazards (7 rules, 8 hazards) | 3 ✓ | `rules-index.md:9-16` | same (skills) |
| 346-350 | SVG draw-on hazards | static-`d` ✓ | `svg-path-draw.md` without the warnings | adds hazards → HF-4 |
| 353-354 | layout waivers scoped narrowly | none | the skills' data attributes | same |
| 377-378 | NOT FOUND: neural transition weights; Navier-Stokes shaders | roots: the vendor's docs | — | n/a |

## 4. The lesson for the intake

A vendor's prompt guide is a second reference, not a calibration source (E38). Its verified numbers (the one-frame lag, the
dwell, the stagger law, the frame-index quantisation) enter as `[DERIVED: HyperFrames docs, verified <date>; measure on ours]`
dials; its beliefs enter as authored rules where doctrine had none; its "settlements" of our open items are read against our
measurements and lose where they conflict. Gemini's next pass tags its figures or marks them unverified, and names OUR roots
in its NOT FOUND block so the report can say what is new.

## 5. Read by hand: the transitions page (operator, same day)

The operator pasted `hyperframes.heygen.com/prompting/transitions` and asked what it adds beyond the analysis. Two things the
report and the claim table did not carry:

- **One primary, accents, one hero** - the structural rule for a short's transition vocabulary, now **E48**: cut-in-the-gap and
  the mount as primaries, the dip and the blur-zoom as accents, the spiral as the hero spent once or twice. The report had the
  tiers, the seams and the catalog; it never had the rule that governs them.
- **The black-hole cut is a renderer artifact.** The page's own words: an explicit fade-out then an entrance "renders as a jump
  cut with a dip in the middle" because the renderer holds each scene's final state. Gemini turned a two-tween tooling note
  into a two-frame perceptual law. HF-R1 stands, with that as the reason (E48 §4).

Indexed from the page (already ours or the skills'): the semantic table (a crossfade "continues", a whip pan "next point", a
burn "something changed" - doc 29 Part 6 had the idea; E48 §3 maps it onto our measured kinds), the energy and mood
catalogues, the knobs (duration by energy, blur 20-30 px calm / 3-6 px high, the easing presets), per-seam authoring
language, "don't invent transition names" (our compiler validates `SCENE_EXITS`), "the transition IS the exit" (our law).

The motion page itself was extracted faithfully (nine of nine statements verified on the page), so pasting it adds nothing;
the page that would add something is `/prompting/vocabulary` (the transitions table with its meanings) or
`/prompting/specification-dial`, neither of which the report opened.

## 6. Read by hand: the storyboards page (operator, same day) - and the amendment to E48

The operator on the first E48: *"I thought what we just learned from Wealth Logic is that maybe the cut in the gap is actually
supposed to be a fade in the gap? … it's too early to prescriptively see what our primaries and accents are. I know the swirl is
the hero. I wouldn't consider the mount as a transition really, it's more of a build … cut minimally, because every cut is a
disconnect … they keep one thread on the screen that ties everything together the whole time."* E48 is amended: the hero is
the spiral, the primaries are decided by the next shorts' curves, the mount is a build, cut minimally, one thread.

What the storyboards page adds beyond the report's §9 (which had the four invariants, the two-colour rule, the reveals, the
breather, the negative list, the schema and the callback):

- **The callback's contract**: say both halves in the plan - where the motif is planted and how it changes on return - and the
  return is the *same element*, never a lookalike; the capstone's protagonist chip rides the whole film and is the thing that
  finally renders. For us: the tab (the receipt) planted on the hook, the line it becomes, the bracket that measures it, the
  ring where it returns - P47 T3's morph is the device. → E48 §4.
- **A hold names its behaviour**: fully still, or a subtle idle - never a slow drift or "breathing", which reads as unfinished.
  This is the nuance that resolves the report's Rule 1 vs Rule 9 contradiction: the vendor allows a *named subtle idle* and bans
  an *unnamed drift*. HF-13's test is on the named idle only.
- **"Never skip persuasion and beat"** on a frame: a scene that shows the stat versus a scene that proves it and says how it
  feels to land. Ours already carries both (the craft map's devices, the beat tags); the per-frame `[focal]` and `[roles]`
  remain HF-9.
- **Prompt the plan, not the scenes** - the direction block every frame inherits is our doctrine layer; the light per-frame
  spec is our shot row. Same shape; indexed.

The seam table in `tokyo-tea-break/SHOT-TABLE-V3-PROPOSAL.md` part D keeps its column but its "role" entries are the
parent's draft, not a ruling: the hero is the spiral; the rest is measured.
