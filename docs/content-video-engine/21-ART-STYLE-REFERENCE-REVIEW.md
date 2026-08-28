# Art Style Reference Review

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

Status: current
Reviewed: 2026-08-22
Method: keyframe extraction and visual review of three operator-supplied videos plus three
operator-supplied thumbnails. Frames were extracted locally and discarded; only the derived
style contract is retained here.

This document exists because the previously planned `stick_figure` lane produced output the
operator rejected. It records what the target styles actually are, so style packs are written
from observed evidence rather than from the phrase "stick figure".

## The finding that matters

**None of the reference channels animate characters.** No articulated limbs, no rigs, no
inbetweens. Every one of them:

1. locks a single character design,
2. re-poses it as many discrete still illustrations,
3. composites those stills over props or a background, and
4. moves them with slide-in, scale-pop, fade, prop reveal, and hard cuts.

The consequence is that the engine's missing capability is **character consistency across
poses**, not an animation runtime. A twenty-minute reference video reuses one face across
roughly a hundred distinct poses without drift. That is a character-sheet-and-pose-library
problem, and `flow_character_pack.v1` already contracts it — front, three-quarter, profile,
full-body, and expression views, with face and costume drift as explicit rejection criteria.
It is currently bound only to the BJJ history art bible and needs generalizing.

A second consequence: motion is cheap here and art is expensive. Budget accordingly.

## Lane A — `cutout_history`

Reference: long-form Depression-era history explainer.

- **Characters.** Radically simplified. Flat rounded head, two dot eyes, no nose, no mouth or a
  vestigial one. Identity is carried entirely by silhouette, hair shape, facial hair, and
  period costume — never by facial features. Limbs are thin sticks; torsos are simple blocks.
- **Backgrounds.** The inverse — densely detailed hand-drawn sets with visible hatching and
  texture: factory floors, exchange steps, bank streets, domestic interiors, harbours,
  government offices.
- **The trick.** Detailed environments plus near-blank characters. Backgrounds carry production
  value; characters carry staging. Blank faces make face drift *structurally impossible*, which
  is why this is the cheapest lane to make consistent and the right one to build first.
- **Palette.** Desaturated period tones — greys, browns, olives, muted brick. Low saturation
  throughout.
- **Line.** Consistent dark contour with a slight hand-drawn wobble; hatching for shadow.
- **Evidence inserts.** Data moments switch register completely: flat chart cards on cream, one
  bold sans title, a single accent-colour data line, minimal axes, no decoration.
- **Titles.** Full-frame black with large bold white sans, animated as kinetic type.
- **Captions.** None.

Closest to the existing woodblock house style, and the natural sibling to it.

## Lane B — `flat_cartoon_explainer`

Reference: personal-finance channel, single recurring narrator.

- **Characters.** Heavy uniform black outline, flat fills, no gradients. Large white oval eyes
  with black pupils, pronounced jaw and chin, simple blocked hair. One recurring narrator
  appears across many outfits and apparent ages; secondary characters share the same
  construction rules.
- **Backgrounds.** Plain white or near-white. There is no environment — meaning is carried by
  floating props.
- **Props.** Icon-scale objects composited around the character: phone, piggy bank, coin stacks,
  calendars, scales, house, car, laptop, jar. Frequently rendered with a soft glow.
- **Colour semantics.** Green means money, growth, and the good branch; red means loss and the
  bad branch. Used literally and consistently — a two-sided frame will tint one half red and
  the other green.
- **Composition.** Character on one side, metaphor on the other. Simple, repeatable, and easy to
  template.
- **Metaphors are literal.** A money tree growing out of a car roof; a balance scale weighing a
  coffee cup against a house.
- **Captions.** Burned in, bottom third, bold white with a black stroke, roughly five to eight
  words at a time.

Directly applicable to the operator's finance lane.

## Lane C — `presenter_infographic`

Reference: personal-finance channel, presenter-anchored.

- **Characters.** A single semi-realistic, softly shaded presenter in business attire, anchored
  to one side of frame and gesturing toward the content zone. Noticeably more rendered than
  Lane B — soft shading, more detailed hair and features.
- **Content zone.** The rest of the frame is an information graphic: outlined icon sets, flat
  vector props, and labelled side-by-side comparison panels with icon flows inside them.
- **Backgrounds.** Alternate between white, muted slate blue-grey, and near-black. Sections fade
  through near-black as a transition device.
- **Annotation.** Red X marks over rejected items, check marks over accepted ones, accent-colour
  highlights.
- **Captions.** Top-positioned, bold white, with exactly one keyword per phrase highlighted in a
  bright accent colour.

This lane is closest to a slide deck with a host, which makes it the natural destination for
the deferred infographic and slide-deck ingest work.

## Lane D — `stick_explainer`

Two references in the same format with a ~400x view gap between them. Reviewed together on
2026-08-22 because the gap is the most instructive evidence in this document.

- **Strong reference:** "The Economics of Owning a Gym", Mr. Finance, 22:38, ~262,000 views.
- **Floor reference:** Stick Trader. The sampled episode, "The Hidden Energy Drainers That Are
  Secretly Ruining Your Trading" (22:18), showed ~659 views only because it was ~11 hours old
  at review time. The channel's established catalogue runs 101K-159K views per episode at
  27-39 minute runtimes. **This format is proven at scale despite visible execution defects** —
  which is the most important single fact in this document.
- **Related register:** the crude paint-style curiosity-gap thumbnails (Sam O'Nella lineage,
  already profiled in [`05-COMPETITIVE-BRIEF.md`](05-COMPETITIVE-BRIEF.md)). Same lane, cruder
  dial, comedy-first rather than psychology-first.

### Grading rubric

Operator position as of 2026-08-22: *"Mr Finance would be amazing if we can get there. Stick
Trader should be the low hanging fruit but even that has been hard for us to accomplish."*

- **Ship gate (floor).** Match Stick Trader. It carries visible defects and still earns
  100K+ views per episode, so it is the honest minimum bar — not an anti-example.
- **Target (ceiling).** Match Mr. Finance. Every gap between the two is a *known, enumerable*
  defect rather than an artistic mystery, which makes the climb a checklist rather than a
  search.

Both bars are the same pipeline. Nothing about the ceiling requires a different renderer,
model, or lane — only tighter enforcement of the two hard rules below.

### The ceiling reference, as a spec

- **Characters.** True stick figures — circle head, single-weight line limbs — but with a
  **solid coloured T-shirt block for the torso**. That colour block is the entire identity
  system: blue shirt, brown shirt, white shirt distinguish characters with no facial variation
  at all. Face is two dots, simple eyebrows, one curved mouth.
- **Line.** One uniform black contour weight with a consistent hand-drawn wobble, held across
  every frame in a 22-minute video. This is the single largest quality signal.
- **Environments.** Simple but *complete* — tiled locker room, gym exterior, office desk,
  living room with a couch. Flat fills, one or two accents per scene, palette family holds
  across scene changes (pale blue, cream, warm grey, sage, brown floor).
- **Props carry the argument.** A figure walking toward an EXIT dragging a chained LEASE
  document; a seesaw weighing "?" against "1/5"; a stack of licences under a stamp; a price tag
  reading an offer against a struck-through original.
- **Typography.** One large hand-lettered word or short phrase per frame, placed in negative
  space — DREAM, FOLLOWS, DEALS, LICENSED, MARGINAL COST, CLOSE TO ZERO. Red reserved for
  emphasis, sometimes hand-circled. Every character of it legible.
- **Framing.** Mostly full-bleed, occasionally a bordered panel. Consistent within a section.

### The floor reference, as a list of enumerable defects

Same concept, executed with an image model and no QC — and still a six-figure performer. What
separates it from the ceiling:

| Axis | Ceiling (Mr. Finance) | Floor (Stick Trader) |
| --- | --- | --- |
| Character identity | Locked; T-shirt colour is the identity system | Head shape, hair, and face change nearly every scene; only the yellow shirt persists |
| Line and render style | One line weight throughout | Alternates between clean line art and watercolour wash between shots |
| On-screen text | Hand-lettered, legible, one idea per frame | Garbled model output — nonsense digit strings, scribbled glyphs inside thought bubbles, half-formed labels |
| Motion | Cuts plus prop reveals | Effectively a slideshow; 76 of 230 keyframe candidates were near-duplicates |
| Framing | Consistent | Padding and letterboxing shift between shots |

**The finding that matters.** Every one of those failures is already named in contracts this
repo has written. `generated_visual_candidate_batch.schema.json` carries
`contains_factual_text`. [`13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md`](13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md)
already lists face drift, costume drift, ambiguous hands, logos, and lettering as rejection
criteria. Enforcing what is already written down closes most of the floor-to-ceiling gap.

**Hard rule this produces: never generate text into a plate.** Text is composited by the
renderer as real typography over the plate, never produced by the image model. Model-generated
lettering is the most visible failure in the weak reference and the easiest to eliminate
outright. Plates carrying generated text are not render-eligible.

**Second rule: identity belongs in the silhouette, not the face.** The ceiling reference proves
a flat colour block on the torso is sufficient to distinguish characters across a 22-minute
runtime. Encode identity in costume colour and silhouette so face drift cannot break
continuity — the same principle that makes `cutout_history` cheap.

### Volume math, and why it changes the selection gate

Measured from the sampled Stick Trader episode: 22:18 runtime, 230 keyframe candidates, 76
near-duplicates dropped — roughly **154 distinct plates at ~8.7 seconds of hold each**. Scaled
to the channel's 39-minute episodes that is ~270 plates. At the planned three variants per slot
this is **450-810 image generations per episode**.

Two consequences the plan must absorb:

1. **Throughput, not artistry, is the blocker.** The reason this has been hard to reproduce is
   almost certainly holding one character across 150+ plates and shipping that volume — not
   drawing any single frame. That is what the pose library and the fan-out contract exist for.
2. **A 1-of-3 manual pick across 150 slots is not a viable gate.** It would mean 150 operator
   decisions per episode, which contradicts the minimize-human-in-the-loop goal outright. The
   board must **auto-select a default variant per slot and surface exceptions only** —
   low-confidence slots, identity-anchor violations, suspected generated text, near-duplicate
   neighbours. This mirrors the graduated-autonomy model already adopted elsewhere in these
   docs: full review, then exception-based, then sampled.

### Register dial

The lane spans a dial rather than a single style, and the dial is set by the script, not the art:

- **Psychology / finance register** — the two references above. Second-person, chapter-marked,
  reframe-driven. Environments present, calmer palette.
- **Comedy register** — crude paint-style, flat black grounds, big block-capital
  curiosity-gap titles, sparse hand-drawn gag elements. Cheapest art in the set; the jokes are
  the product.

Both share the same plate-and-motion plumbing and the same two hard rules above.

**Why this lane inverts the usual risk.** In Lanes A-C the art is expensive and the writing is
routine. Here the art is nearly free while the **writing is the entire product**. Treat script
quality as the gate, not plate quality. It follows that for the comedy register an LLM director
is a genuine risk rather than a convenience: model-written humour is reliably poor, so the
director proposes *structure* — setup, misdirection, punchline placement, callback — and leaves
the jokes to the operator until there is evidence otherwise.

Do not confuse this lane with the retired Manim `StickFigureScene`. That lane failed carrying
technique and physics diagrams, where crude linework actively obscures the content. Here the
linework *is* the content.

## The natural experiment that reframes everything

Reviewed 2026-08-22 from three operator-supplied sources in one niche (trading
psychology), all 20-27 minutes, all long-form:

| Source | Presentation | Views |
| --- | --- | --- |
| The Spiritual Trader, "Why 95% Find Trading Impossible" | **One static image for the entire 20:38.** Split frame, stressed trader left / calm trader right. Zero plate changes. Yellow word-by-word captions are the only thing that moves. | **241,953** |
| The Zen Trader, "Why Trading Less Earns You More Money" | Consistent blue-shirt stick figure, genuine scene variety (desk, whiteboard equity curve, journaling), soft pastel gradients, branded corner mark, held plates per section | **2,110** |
| ZenTraderXBT, 20-video catalogue | Comparable production, consistent output cadence | **685-2,600 each; nothing above 3K** |

**The channel with better art and more scene variety got roughly 100x fewer
views than the one that reused a single drawing for twenty minutes.**

### What this does and does not prove

It does **not** support "we win on presentation." The 242K video has the worst
presentation of anything in this document. In this niche, production quality is
not the variable separating winners from losers, and any plan premised on
out-animating these channels is premised on the wrong axis.

It also does not isolate one cause. Packaging is doing visible work — "Why 95%
Find Trading Impossible — And 5% Find It Obvious" is a far stronger title than
"Why Trading Less Earns You More Money," and a two-video sample cannot separate
title, thumbnail, topic and presentation. Treat the 100x as a ceiling on how
much presentation could possibly explain, not as proof it explains nothing.

What it does prove is narrower and more useful: **a single well-chosen plate
plus accurate word-timed captions is a commercially viable format at six-figure
scale.** That is nearly free to produce, and `hyperframes_unit.schema.json`
already enumerates `caption_unit` as a unit kind. It is the cheapest shippable
lane in the entire system and it currently has no plan slice.

### Where the real differentiation is

Compare what is actually *said*. The trading-psychology channels are assertion
without evidence — "kill the need for certainty," "the brain interprets
inactivity as failure." No figures, no sources, nothing checkable.

Mr. Finance is doing something structurally different: "6000+ MEMBERS,"
"£249 was £499," "MARGINAL COST CLOSE TO ZERO," a seesaw weighing "?" against
"1/5." Those are *economics*. The plates are context-aware because there is
something specific to be aware of. Fact drives plate, not the reverse.

That is the axis worth competing on, and it is the one axis this repo is already
built for: a fact layer with provenance and never-fabricate guardrails
(`content/bjj-registry/src/llm_guard.py`, `llm_writer.py`) that none of these
channels has or wants. The moat is the claim binding, not the renderer.

**Implication for the plan.** Prompt composition should take the slot's bound
claim as its subject, not just the narration excerpt, so a plate illustrates a
specific figure rather than a mood. Slots with no bound claim should be visibly
distinguishable from slots that carry one.

## Lane E — `parametric_stick` (Casual Finance)

Reference: Casual Finance, "The SpaceX IPO... It's Worse Than You Think", 14:52,
~1,701,470 views, 334,000 subscribers, published 2026-05-21. Operator-flagged as
outperforming both finance channels above, and correctly flagged as the hardest
reference here. The channel predates the current generation of image models.

### What is actually on screen

- **One crude stick character.** Skin-fill oval head, black hair scribble, two dot
  eyes, one curved smile, single-line body with kinked elbows. Redrawn at many
  scales, positions and poses. No costume, no colour identity — the hair scribble
  and head shape are the whole identity system.
- **Hand-drawn props in the same hand.** Three grey cardboard boxes labelled
  "SPACEX BUSINESS 1/2/3"; a chalkboard as brown frame plus green field plus white
  hand-lettering; an office chair; a red diagonal band; a scribbled SpaceX form.
- **Real brand assets dropped in clean.** The Nasdaq logo full-bleed, platform
  logos, the sponsor's logo. These are genuine vector assets, not drawn and not
  generated.
- **Hand-lettered text** in the same crude hand — "demand", "401K", the outro.
- **Squiggle-as-text.** The 401K document uses wavy lines where body copy would be.
  They never draw fake readable text. This is the craft solution to the exact
  failure mode that ruins the floor reference in Lane D, and it generalizes: where
  a plate needs to *imply* text, draw a squiggle; where it needs to *say*
  something, the renderer composites real type.

### Why prompting an image model for this fails

The operator's finding — *"telling them 'make bad stick figure explainers' does
not work"* — is correct, and the reason is specific. Diffusion renders crude as
**muddy**: variable stroke weight, duplicated wobbling contours, a head that
changes shape every generation. Casual Finance's crudeness is **confident**: one
pass, uniform weight, deliberate asymmetry. Confident crudeness is a signature of
intent, and intent is the one thing a denoising process cannot fake.

### Why that does not mean this lane is out of reach

Count the primitives. An oval, a hair scribble, two dots, one curve, five lines —
roughly ten paths. A pose is a set of joint coordinates. **This is the one style in
this document that should never be generated as pixels at all; it should be drawn
as code.** A parametric SVG rig gives, by construction:

- **Consistency for free.** It is literally the same path data every time, so
  identity drift is not reduced, it is impossible.
- **Unlimited poses at zero marginal cost**, versus 450-810 paid generations per
  episode in the diffusion lanes.
- **Seek-safe rendering**, since inline SVG animates deterministically in
  HyperFrames.
- **No generated text, ever** — type is real type and implied text is a squiggle
  path.

The substrate already exists in this repo: `content/video_engine/src/assets/poses/`
holds checked-in pose SVGs and `StickFigureScene` interpolates between them.

### Correcting the earlier retirement of the stick-figure lane

An earlier revision of this document retired the stick-figure lane outright
because the operator rejected its output. That conflated two different jobs. The
lane failed at **armbar technique diagrams**, where anatomy has to be correct and
crude linework actively obscures the content being explained. Here anatomy does
not have to be correct — crudeness *is* the content. The rejection was valid for
the old job and does not carry to this one.

### The honest risk

A parametric rig can read as sterile. Part of Casual Finance's charm is that no
two drawings are identical, and a rig that reuses exact path data will look
mechanical next to a human hand. Mitigation is seeded per-instance jitter on the
path control points — deterministic from the slot id, so renders stay reproducible,
while no two plates are pixel-identical. This is a real risk, not a solved one,
and it should be judged on a rendered side-by-side before the lane is trusted.

### What still cannot be automated

- **The writing.** Every sentence in the opening carries a figure: a $1.75 trillion
  target valuation, more than every American defence contractor combined, more than
  Coca-Cola plus McDonald's plus Disney plus Nike plus Starbucks, losing $5 billion
  a year. The comparisons are chosen to be *visualizable*, which is an editorial
  skill, not a rendering one.
- **Prop invention.** Deciding that "three SpaceX businesses" becomes three labelled
  cardboard boxes is a metaphor choice. A director can propose prop metaphors from a
  bound claim, but the operator should hold veto.
- **The accumulated hand.** 334K subscribers built pre-AI. The moat is the writing
  and the drawing hand, not the tooling — which is the argument for competing on
  claim-bound substance rather than on imitation.

## Lane F — `expert_explainer` (Wealth Logic) — the recommended target

Reference: Wealth Logic, 83,300 subscribers.

| Episode | Runtime | Views | Views per subscriber |
| --- | --- | --- | --- |
| "Real Estate Vs Stocks — The Real Math" | 15:15 | 1,565,707 | ~19x |
| "If You Don't Understand Bonds, You Don't Understand Money" | 18:30 | 425,970 | ~5x |

A 19:1 views-per-subscriber ratio means these are **algorithmically distributed on
topic and packaging, not carried by an audience**. That matters strategically: a
channel that wins on distribution is reachable by a new entrant, whereas one that
wins on accumulated loyalty is not.

### The cast

- **A recurring expert**: white lab coat, black tie, dark slicked hair, heavy black
  outline, flat fill, large oval eyes. The **same character appears across both
  episodes**, so this is a cast, not a one-off.
- **Per-episode civilians**: Jake in a navy polo, Brian in a blue shirt and khakis.
- Identity is carried entirely by **costume block** — the lab coat *is* the expert.
  It is a large flat white shape, unmistakable at any scale, and completely
  insensitive to facial drift. This is the strongest possible `identity_anchor`
  and it confirms the rule derived from Mr. Finance independently.
- Staging is consistent: expert to one side, gesturing at a content zone.

### The content zone is mostly type, not illustration

This is the finding that makes the lane reproducible. Sampled plates include:

- a whiteboard reading `YR 1: $55,000 ↑ / YR 2: $61,000 ↑`
- an arithmetic stack rendered as real type: `$50K + $36K` over a rule, `$86K TOTAL IN.`
- two certificate props labelled `3% BOND` and `5% BOND`
- a broken air-conditioning unit with a `$7,000` price tag
- a basket of bond certificates with a `DAILY` label

**All of that lettering is crisp and correct.** If these plates came from an image
model the numerals would be garbled, as they are in the Lane D floor reference.
They are not. The numbers are composited as real type over simple vector props —
precisely the no-generated-text rule already adopted for every lane.

### The script is a parametric model

The opening specifies the entire calculation before any conclusion: two named
actors with identical starting conditions ($50,000 saved, $55,000 income, same age
and city), then every parameter named — 20% down on a $250,000 property, 30-year
mortgage at 7%, $1,330 monthly payment, $1,800 rent. Every later figure is
*derived* from those inputs.

That is the crucial structural fact: **the plates are downstream of a model, so
they can be generated from it rather than authored.** A divergence chart, a running
total, a comparison stack all fall out of the arithmetic. Vibes channels cannot do
this because they have no numbers; this repo's fact layer and deterministic
pipeline are built for exactly it.

### Craft details

- **Captions**: burned in, bottom, all caps, white with exactly one word per phrase
  highlighted in green.
- **Palette**: cream ground, heavy black contours, muted flat fills, green for
  positive and emphasis, red for cost — the same green/red semantics as Lane B.
- **Their bar is not perfection.** One sampled frame in the 1.5M-view episode shows
  a badly smeared transition with ghosted, multiplied house shapes. Elite performers
  ship visible artifacts.

### Why this is the target rather than Casual Finance

Lane E's moat is a human drawing hand accumulated pre-AI, which is the least
transferable asset in this document. Lane F's advantages are a costume-anchored
cast, typographic data plates, and a worked numeric model — and a deterministic
pipeline does all three *better* than a human, not worse. Consistency, arithmetic
correctness, and plate-from-model generation are machine strengths.

### Plan implication: plates are not all generated

A large share of Lane F plates need no image model at all. That argues for an
explicit plate-kind distinction: `generated_plate` (an image model produces pixels)
versus `composed_plate` (the renderer draws type, props and data deterministically).
The composed kind has zero generation cost, zero garbling risk, and perfect
reproducibility — and it cuts hard into the 450-810 generations per episode
estimated for the diffusion lanes.

## Retraction: rendition level is not a consistency risk

An earlier revision of this document argued that the existing host assets were
"over-detailed for the job," on three grounds. Re-reviewed 2026-08-22 against three
Alicia Invests episodes. **All three grounds were wrong or overstated, and the
central one was wrong.**

| Episode | Runtime | Views | Subs |
| --- | --- | --- | --- |
| "Minimalist Money Rules You MUST Follow" | 23:37 | 1,945,818 | 99,600 |
| "The High Income Poverty Trap" | 20:13 | 325,643 | 99,600 |
| "10 Signs Someone Is Genuinely Rich" | 33:23 | 103,929 | 99,600 |

### What was claimed, and what the evidence shows

**Claim 1 — "every rendered detail is another drift axis across 150 plates."**
*Refuted.* The Alicia presenter is soft-shaded with volumetric hair, fabric folds,
detailed facial features and visible jewellery, and holds identity across a 20-minute
and a 33-minute episode through wildly different environments — office, gas station,
open road, a conveyor-belt diagram, a kitchen. Reference-image conditioning handles
consistency at this rendition level. This was the load-bearing argument and it does
not hold.

**Claim 2 — "the detail does not survive playback scale."** *Mostly wrong, and badly
reasoned.* The evidence used was the project's own corner-stamp asset reducing to a
blue blob — but that asset is a **watermark, sized as a watermark**. Extrapolating
plate legibility from a watermark was an error. In the reference, the presenter
occupies roughly 40-60% of frame height, and at that scale the rendering reads
clearly.

**Claim 3 — "a high-information character competes with the data for focal
attention."** *Refuted as stated, and the real rule is different.* Alicia's frames
carry a large, fully rendered character **and** legible figures simultaneously —
`$900,000 + 30% = $210,000` with a held cheque reading `$300,000 / 30%`; a pie chart
labelled `48% / $100,000 Earners`; bar charts at `$32.98`, `$31.51`, `$12.991`,
`$11.90`; a phone screen reading `10.2% INCREASE IN SPENDING`. It works because the
data lives in a **distinct zone with its own contrast** — background, held prop, or
chart beside the figure. **Zone separation is what protects legibility, not
flattening.**

### Correction to this correction: Alicia does not composite her figures

A closer read of the same frames shows the numbers are **generated into the plate**, not
composited as type. The tells:

- a bar set reading `$32.98`, `$31.51`, `$12.991`, `$11.90` — `$12.991` is a malformed
  currency value with three decimals;
- `$900,000 + 30% = $210,000`, which is not arithmetic;
- a cheque reading `$300,000` and `$10000` — the second without a thousands separator;
- a labelled diagram with `ITEM TO ENERGY TRANSFORM` appearing twice verbatim.

Those are model artifacts. An earlier revision of this section described her figures as
composited and legible; that was over-credited. **Wealth Logic's figures are crisp and
internally consistent; Alicia's are plausible-looking and frequently wrong.**

This does not disturb the retraction above, which rests on character consistency across a
20- and a 33-minute episode — that evidence is unaffected. It disturbs a different claim.

### Two production models, and they are a real choice

| | Composite from library | Generate whole plates |
| --- | --- | --- |
| Reference | Wealth Logic; this repo's own `depth_layers` spec | Alicia Invests |
| Per-episode generations | ~5-20 topic props | ~150, one per plate |
| Character consistency | Perfect by construction — same cutout every time | Reference-conditioned; holds well in practice |
| Scene variety | Bounded by the catalog | Unbounded |
| On-screen figures | Composited type, verifiable | Generated, **frequently wrong** |
| Up-front cost | A good cutout library | None |

Alicia earns 104K-1.95M views per episode *with* visibly wrong numbers, so the defect is
evidently not fatal to distribution. But it is precisely what
`style-profile.v1.json`'s `generated_text_rule` forbids and what T4 rejects.

**The reconciliation, and the intended edge:** whole-scene generation is allowed, but scenes
must be generated **textless** and every figure composited by the renderer. That keeps
Alicia's scene variety without inheriting her defect, and it is a quality edge no reviewed
channel currently holds. It also means the library matters less as a *cost* lever than as a
*consistency* lever — worth building for recurring actors and worlds, not worth building
exhaustively before shipping.

### The rule that stands

Rendition level and data legibility are **independent axes**. The earlier draft
bundled them and drew a false trade-off. A high-rendition character is compatible
with dense figures provided:

- figures are composited type in a reserved zone, never generated into the character
  plate (the existing `evidence_safe_region` in `style-profile.v1.json`); and
- that zone carries its own contrast against whatever sits behind it.

Nothing about the existing host assets needs flattening. What survives from the
earlier note is narrower and is an asset-pipeline concern rather than an
art-direction one: a 2.9 MB master is not what you composite 150 times — you
composite an optimised keyed cutout derived from it.

### Numeric density, measured

Figures per 1,000 transcript words, counting currency amounts, percentages and
magnitudes:

| Episode | Words | Figures | Per 1,000 words |
| --- | --- | --- | --- |
| "The High Income Poverty Trap" (325,643 views) | 2,709 | 120 | **44.3** |
| "10 Signs Someone Is Genuinely Rich" (103,929 views) | 5,135 | 32 | **6.2** |

Same channel, same format, same presenter: the seven-times-denser script drew about
three times the views. Two episodes with different topics and ages is weak evidence
on its own, but it points the same direction as every other comparison in this
document — **figures track performance.**

### Audience fit

The operator's position is that a more formal, fully rendered presenter suits the
intended audience. That is an audience judgment the operator holds evidence on and
this review does not. It is also consistent with the reference: a Black woman
presenter, formally dressed and fully rendered, at 99,600 subscribers with episodes
between 104K and 1.95M views.

## Methodology correction

An earlier draft of this document used the keyframe near-duplicate rate as a
proxy for how much a video animates ("76 of 230 candidates were near-duplicates,
effectively a slideshow"). **That proxy is unreliable when captions are burned
in.** The near-duplicate pass measures pixel change, and changing caption text
registers as change even when the artwork is frozen. The Spiritual Trader video
dropped only 67 of 300 candidates while being a single unchanging image for
twenty minutes.

Treat near-duplicate rate as a signal about *caption cadence*, not about
animation. Judging motion requires looking at the frames.

## Additional thumbnail-only references

Supplied as thumbnails without video, so treated as weaker evidence:

- A clean whiteboard-style explainer character — rounded cartoon figure with visible clothing
  and an expressive face, thought bubbles as the framing device, light grey ground. Sits between
  Lane A and Lane B.
- A sketchy stickman with real clothing and hair on white — closer to Lane B construction than
  to a true stick figure, and closer still to Lane D once the linework loosens.

## What this changes

- `stick_figure` is removed as a lane name — but not as a capability. Lane D *is* a
  stick-figure lane; it is built from generated stills rather than Manim technique diagrams. The Manim `StickFigureScene` remains in the tree, unreferenced by any style pack.
- Lanes are defined by **character policy, background policy, caption policy, and colour
  semantics** — four axes that a style pack can encode and a validator can check.
- Build order is `stick_explainer` first (cheapest art, proves the plate-and-motion plumbing
  end to end for almost nothing, and has a directly comparable strong/weak reference pair to
  grade against), then `cutout_history` (consistency is free), then `flat_cartoon_explainer`
  (highest commercial relevance), then `presenter_infographic`. `stick_explainer` ships as a
  plumbing proof before it ships as a channel — its editorial gate is script quality.
- Two rules now apply to **every** lane, not just Lane D: no generated text in a plate, and
  identity encoded in silhouette and costume colour rather than facial features.
- A `caption_unit` lane — one static plate plus accurate word-timed captions — is proven at
  241K views and is the cheapest shippable format in the system. It has no plan slice yet.
- Lane E (`parametric_stick`) is drawn as SVG code, not generated as pixels. It is the only
  lane where identity drift is structurally impossible and per-plate cost is zero.
- The squiggle-as-text convention generalizes to every lane: imply text with a drawn squiggle,
  say text with renderer-composited real type.
- Lane F (`expert_explainer`, Wealth Logic) is the recommended target: a costume-anchored cast,
  content zones that are mostly composited type rather than illustration, and scripts that are
  parametric models whose plates fall out of the arithmetic. Its strengths are machine
  strengths.
- Plates split into `generated_plate` and `composed_plate`. Most Lane F plates are composed,
  which removes them from the generation budget entirely.
- Rendition level and data legibility are independent axes. A fully rendered character is
  compatible with dense figures when the figures occupy a reserved, self-contrasting zone.
  An earlier claim that high rendition risks drift or costs legibility is retracted above.
- Plates should be bound to specific claims, not moods. That is the differentiator this repo
  is uniquely equipped for and no reference channel is attempting.
- No 3D appears anywhere in the references. Three.js stays a spike, not a lane.

## Related

- [`08-TOOLING-ALTERNATIVES.md`](08-TOOLING-ALTERNATIVES.md) — provider verdicts.
- [`13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md`](13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md) — the
  character-sheet workflow this review makes central rather than optional.
- [`18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md`](18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md)
  — the existing house style, now one lane among five.
- `.claude/PRPs/plans/P14-DIRECTOR-AND-SCENE-BOARD.plan.md` — the plan this review reshaped.
