---
id: P14-DIRECTOR-AND-SCENE-BOARD
title: Script-to-Scene-Board Director and Multi-Lane Animation Substrate
status: running
operation: feature
risk: elevated
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-22
updated: 2026-08-22
---

# Script-to-Scene-Board Director and Multi-Lane Animation Substrate

## Summary

Today the engine cannot accept a pasted script. `ScriptTransformService.build_corpus`
(`content/video_engine/src/services/script_transform.py:40`) emits a hardcoded armbar beat
template with literal narration strings, and no LLM exists anywhere in the video engine. The
only visual board is `style_board.png` — PIL-drawn placeholder rectangles from
`_draw_still` (`content/video_engine/src/services/style_board.py:497`).

Meanwhile the deterministic half of what the operator wants already exists and is unused on
this path: `editorial_coverage.schema.json` defines per-slot `semantic_purpose`,
`visual_archetype`, `motion_recipe`, `duration_s` and search terms;
`generated_visual_candidate_batch.schema.json` already carries N candidates with
`review_status`; `asset_selection_review.schema.json` already binds `slot_id` to
`candidate_id`; and stage `awaiting_asset_selection_approval` already exists in `V4_1_STAGES`.
The gap is a **director** that produces coverage from a pasted script *before* audio exists,
a **fan-out contract** that requests 2–3 candidates per slot, and a **board** the operator
can actually look at and choose from.

Separately, the reference channels the operator supplied (2026-08-22 review of three videos,
recorded in `docs/content-video-engine/21-ART-STYLE-REFERENCE-REVIEW.md`) establish that the
target art styles are **not** stick figures and **not** character animation. All three
references composite a **locked character design across many static poses** and move them with
2D transforms, cuts, and burned-in captions. The missing capability is therefore character
consistency plus a pose and expression library — not a rigging or animation runtime.
`flow_character_pack.v1` already contracts exactly that and is currently bound only to the BJJ
history art bible. The Manim `StickFigureScene` lane is retired from this plan; its output was
rejected by the operator.

## Intent And Acceptance

**Intent.** An operator pastes a script they have already sourced, and gets back: a proposed
scene breakdown with plate counts and editorial direction, 2–3 generated image options per
scene, and a visual board where they pick the final scene pack before any expensive video
generation runs.

**Acceptance.**

1. `python -m content.video_engine.cli ingest-script --script <file> --attest <json>` creates a
   run whose first artifact is `source_attestation.json`, with no research-gate stage in its
   stage order.
2. A director proposal is persisted as `director_proposal.json` carrying `artifact_hash`;
   re-running the run replays the stored proposal and produces byte-identical downstream
   artifacts. Only `--refresh-proposal` re-solicits the model.
3. The proposal compiles to a coverage artifact validating against
   `editorial_coverage.schema.json` with `timing_basis: "estimated"`, where every
   `slots[].duration_s` derives from word count ÷ WPM, never from audio.
4. `visual_prompt_pack.json` requests `variants_per_slot >= 2` for every slot and each request
   carries the originating `slot_id`.
5. A candidate batch returned by the run agent validates only if every item binds to a known
   `slot_id` with a distinct `variant_index`.
6. `runtime/jobs/<run>/board/index.html` opens offline and shows three tiers — evidence and
   resources, image candidates grouped by slot with exactly one selectable per slot, and a
   disabled video-generation slot per selected image.
7. Recording selections emits an `asset_selection_review.json` that validates against the
   existing schema and is rejected if any slot has zero or multiple selections. Every slot
   carries an auto-selected default, so a board with 150 slots requires operator input only on
   flagged exceptions.
8. One whiteboard unit and one Three.js unit each render through the HyperFrames lane and pass
   the existing `hyperframes_render` ffprobe duration check within the 2% drift ratio.
9. Full suite green: `python -m pytest content/video_engine/tests -q` (excluding the five
   pre-existing `test_history_v4_pipeline.py` failures tracked separately).

## Scope

- New paste-entry lane with operator-asserted provenance, parallel to the corpus lane.
- Director proposal contract: request pack out, validated proposal in. The engine never calls
  an image or text model directly; the run agent (Hermes/GPT) or an operator fills the pack.
- Provisional coverage compilation at estimated timing, explicitly non-authoritative for render.
- Multi-variant candidate fan-out and slot-bound candidate validation.
- Static scene board with three tiers and selection capture.
- Style-pack registry mapping seven art lanes (`expert_explainer`, `presenter_infographic`,
  `flat_cartoon_explainer`, `stick_explainer`, `cutout_history`, `woodblock`, `whiteboard`) to
  renderer, character policy, caption policy, colour semantics, and motion grammar.
- A character pose and expression library extending `flow_character_pack.v1` beyond the BJJ art
  bible, so one locked design can be reused across a whole episode.
- Two proof units establishing the whiteboard and Three.js lanes exist and are seek-safe.

## Not Building

Deliberately deferred, with the seam named so a follow-on PRP does not require rework:

- **Paid video generation.** The board renders a video slot per selected image and writes
  `video_intent` records, but no provider is called. Seam: `video_intent[].provider` is unset
  and `runtime/jobs/<run>/video_jobs/` stays empty. The standing constraint that the queue
  remains paused and no paid video job is released is unchanged by this plan.
- **Vertical short derivation.** Coverage slots carry `uniqueness_signature` and the storyboard
  keeps `target_s`; a derivation pass can select a slot span and re-emit a `vertical_short`
  HyperFrames unit, which `hyperframes_unit.schema.json` already enumerates. No derivation code
  ships here.
- **Infographic and slide-deck ingest.** Seam: `source_attestation.references[]` accepts
  arbitrary reference documents with `kind` and `sha256` now, so decks can be attached and
  hashed at paste time even though nothing reads them yet.
- **Paper (paper.design) integration.** Evaluated and deferred — see Execution Path.
- **Rive.** Excluded permanently for programmatic generation — see Execution Path.
- **Character animation** (rigged or keyframed limb motion). Out of scope in every lane, and
  the reference review confirms no target channel does it. Motion means camera, reveal,
  parallax, prop pop, draw-on, and cuts between re-posed stills.
- **Manim as the stick-figure renderer.** The Manim `StickFigureScene` stays in the tree
  untouched and no style pack targets it. Its rejection was valid for armbar technique
  diagrams, where anatomy must be correct; it does not carry to the `parametric_stick` lane,
  which is served by inline SVG in HyperFrames instead (T12).
- **Claim-bound prompt composition.** T4 composes prompts from the slot's `visual_intent` and
  narration excerpt. The stronger form takes the slot's bound fact-layer claim as the plate's
  subject, so a plate illustrates a specific figure rather than a mood. Seam:
  `provisional_coverage` slots already carry `uniqueness_signature` and
  `visual_prompt_pack._compose_prompt` is a single function with one call site, so adding a
  `claim` field to the slot and threading it into the prompt is additive. Deferred because
  retrofitting a completed and validated slice is worse than a named follow-on.
- **Retiring Manim, Remotion, or any V2–V4.1 stage.** No renderer is removed. `DEFAULT_STAGES`
  stays pinned to `V2_STAGES`.

## Human Gates

| Gate | Where | Who | Blocks |
| --- | --- | --- | --- |
| Provenance attestation | `ingest-script` | Operator | Run cannot start without a signed attestation naming the source |
| Scene pack selection | `awaiting_asset_selection_approval` | Operator | No video-generation intent is written until every slot has exactly one selection |
| Publish | `awaiting_publish_approval` | Operator | Paste-lane runs additionally require `source_attestation.json` present |

Product code must not auto-approve any of these. Tests may simulate them.

Additionally: the run agent generating images is an **external, cost-bearing** action. The
engine emits the prompt pack and validates what comes back; it never initiates generation.

## Mandatory Reads

- `content/video_engine/AGENTS.md` — determinism, audio-as-clock, gate ownership, runtime paths.
- `docs/runbooks/PRP_EXECUTION.md` — plan schema and slice contract.
- `content/video_engine/configs/editorial_coverage.schema.json` — the slot contract the
  director must produce, not replace.
- `content/video_engine/configs/generated_visual_candidate_batch.schema.json` and
  `asset_selection_review.schema.json` — the candidate and selection contracts to extend rather
  than reinvent.
- `content/video_engine/configs/hyperframes_unit.schema.json` and
  `content/video_engine/src/services/hyperframes_render.py` — the render/QC lane the new
  animation packs plug into.
- `content/video_engine/src/services/editorial_motion.py` —
  `compile_canonical_visual_coverage` and `analyze_timestamped_semantic_coverage` define the
  post-audio authoritative path the provisional path must reconcile with.
- `docs/content-video-engine/19-HYPERFRAMES-LANE.md`.
- Skill `hyperframes-core` — composition contract, `data-*` timing, `class="clip"`, seek safety.
- Skill `hyperframes-animation` — adapters `three.md` and `lottie.md` specifically.
- Skill `backend-patterns` — service, repository, and validation boundaries.

## Execution Path

**What the reference channels actually do.** The three supplied videos decompose into three
distinct but structurally identical systems. Every one of them is a locked character design,
re-posed as still art, composited over props or a background, moved with 2D transforms:

| Lane | Reference | Character policy | Background | Captions |
| --- | --- | --- | --- | --- |
| `cutout_history` | Depression-era explainer (video 1) | Near-blank faces — dot eyes, no mouth, no nose; period costume carries identity | Heavily detailed hand-drawn sets with visible hatching, desaturated period palette | None; kinetic white-on-black title cards between acts |
| `flat_cartoon_explainer` | Nick Invests | Heavy black outline, flat fill, large oval eyes, strong jaw; one recurring narrator across outfits and ages | Plain white; floating icon props carry meaning | Bold white with black stroke, bottom third, 5–8 words |
| `presenter_infographic` | Alicia Invests | Semi-realistic soft-shaded presenter anchored to one side, gesturing at the content zone | Alternating white / slate / near-black; icon sets and two-panel comparisons | Top-positioned, one keyword per phrase highlighted in accent |
| `stick_explainer` | Curiosity-gap comedy channel (thumbnails) | Deliberately crude paint-style stick figure; dot-and-line face, wobbly single-weight limbs | Flat black or single fill, sparse hand-drawn gag elements | Large bold block caps, often set on black |
| `expert_explainer` | **Recommended target.** Wealth Logic — 1.57M and 426K views on 83.3K subs | Recurring lab-coat expert plus per-episode civilians; the coat is the whole identity anchor | Cream ground, content zone beside the character | All-caps burned-in, bottom, one word per phrase in green |
| `woodblock` | Existing house style | Graphic silhouette, existing art bible | Existing world plates | Existing |
| `whiteboard` | Operator request; not present in references | Optional | White | Optional |

Two consequences decide the substrate:

1. **No reference animates a character.** Limbs do not articulate. Motion is slide-in,
   scale-pop, fade, prop reveal, and cuts — all of which the existing editorial-motion recipes
   already produce. The plan therefore needs no rigging runtime.
2. **The real hard problem is character consistency**, not motion. A 20-minute Nick Invests
   video reuses one face across roughly a hundred distinct poses without drift. That is a
   character-sheet-and-pose-library problem, which `flow_character_pack.v1` already contracts
   (front, three-quarter, profile, full-body, expression views; face and costume drift are
   explicit rejection criteria). T8 generalizes it off the BJJ art bible.

**Build order.** `stick_explainer` first: its art is nearly free — no anatomy, no face
consistency, no detailed environments, and pose drift reads as style — so it proves the whole
plate-and-motion path end to end at minimum cost. It also inverts the usual risk, because the
writing is the entire product there; ship it as a plumbing proof before treating it as a
channel, and gate it on script quality rather than plate quality. Then `cutout_history`, where
blank faces make face drift structurally impossible and consistency is likewise free, then
`flat_cartoon_explainer` for commercial relevance, then `presenter_infographic`.

One director constraint follows from Lane D's comedy register: model-written humour is
reliably poor, so there the director proposes **structure only** — setup, misdirection,
punchline placement, callback — and never authors the jokes. T2's proposal schema must be able
to express a beat whose copy is deliberately left to the operator.

**Floor and ceiling.** Both Lane D references are proven performers in the same format: the
floor reference earns 101K-159K views per episode *despite* visible execution defects, and the
ceiling reference earns ~262k with those defects absent. The ship gate is therefore matching
the floor, and every remaining gap to the ceiling is an enumerable defect rather than an
artistic unknown. The operator's stated position is that even the floor has so far been hard to
reach, so nothing in this plan should assume the ceiling.

**Two rules the reference pair forces on every lane.** The floor-to-ceiling gap tracks axes
this repo has already written down —
`contains_factual_text` in `generated_visual_candidate_batch.schema.json`, and face drift,
costume drift, ambiguous hands, logos and lettering as rejection criteria in
`13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md`. Enforcing what already exists closes most of that
gap:

1. **No generated text in a plate.** All on-screen typography is composited by the renderer as
   real text over the plate. Model-generated lettering — garbled digit strings, scribbled
   glyphs inside thought bubbles, half-formed labels — is the single most visible failure in
   the weak reference and is eliminated by contract rather than by review. Enforced in T4.
2. **Identity lives in silhouette and costume colour, not the face.** The strong reference
   distinguishes characters across 22 minutes using nothing but a flat T-shirt colour block.
   Encoding identity this way makes face drift unable to break continuity — the same property
   that makes `cutout_history` cheap. Enforced in T7's character policy and T8's pose library.

**Why one substrate instead of five renderers.** The repo already carries three renderers
(Manim, Remotion, HyperFrames), five stage lists, and ~50 config schemas, with
`DEFAULT_STAGES` still pinned to V2. Every lane above is generated plates plus 2D motion plus a
caption policy, so all five ride the existing HyperFrames plate lane and differ only by style
pack. `whiteboard` is the one lane needing new render code (SVG draw-on), and Three.js is
retained as a spike rather than a lane because **no reference uses 3D**.

**Answering the Rive/Lottie/Three question directly**, since it decides what the spikes prove:

- **Three.js — yes, but nothing in your references needs it.** It is code, which is what models
  author well, and HyperFrames ships a first-class `three` adapter that publishes time through `hf-seek` and `window.__hfThreeTime`
  for deterministic frame-exact rendering. One documented trap: the `three` adapter has **no
  duration auto-inference**, so the root `[data-composition-id]` must carry
  `data-duration="<seconds>"` or lint fails with `root_composition_missing_duration_source`.
  T9 must assert this.
- **Lottie — consume, do not author.** HyperFrames has a `lottie` adapter that seeks via
  `goToAndStop`, so pre-baked assets are usable. But Lottie JSON is an After Effects export
  format of raw bezier keyframe arrays; it is a poor authoring target for a model. Use it for
  acquired assets (logo reveals, icon sets), never as the generation target.
- **Rive — no.** `.riv` is a compiled binary authored only in Rive's editor; there is no text
  format a model can write. HyperFrames has no Rive adapter — the seven are GSAP, Lottie,
  Three.js, Anime.js, CSS keyframes, WAAPI, and TypeGPU. Rive is a dead end for programmatic
  generation and is excluded permanently.

**On Paper (paper.design).** Genuinely interesting and genuinely not ready for this. In its
favor: every element renders as HTML and CSS, which is exactly the substrate HyperFrames
consumes, and it exposes a bidirectional MCP server with 24 tools. Against it: the MCP is a
**local desktop server** (`http://127.0.0.1:29979/mcp`) requiring the authenticated desktop app
running, so it is an operator-attended tool and cannot run headless in a pipeline; and the
features that would matter here — Lottie/Rive embed, Three.js islands, particle systems, video
generation, and the script/prompt engine — are all listed **planned**, not shipped. Correct
role for Paper: an optional human authoring front-end for individual plate layouts and style
packs whose HTML/CSS output is imported as a HyperFrames composition. That is a follow-on, not
a dependency. Nothing in this plan should be blocked on it.

**Determinism.** `content/video_engine/AGENTS.md` requires every stage be deterministic and
idempotent from persisted inputs; an LLM director violates that if called inline. Resolution:
the engine emits `director_request.json`, an external agent returns a proposal, and the
validated `director_proposal.json` becomes the persisted input every downstream stage replays
from. The model is upstream of the pipeline, not inside it.

**Timing honesty.** `editorial_coverage` is normally compiled from word-level timings after
audio. A pasted script has no audio, and the operator must see a board before paying for
synthesis. The provisional coverage therefore carries `timing_basis: "estimated"` with
durations from word count ÷ WPM — the same basis `storyboard.schema.json` already documents for
`target_s`. It is valid for board layout, prompt fan-out, and slot counting, and is **invalid
for render timing**. When canonical audio lands, `compile_canonical_visual_coverage` produces
the authoritative artifact and the render path uses only that. Audio remains the clock.

**Volume, corrected 2026-08-22.** The sampled floor reference runs ~154 distinct plates at
~8.7s of hold, scaling to ~270 for a 39-minute episode. An earlier revision multiplied that by
three variants and concluded **450–810 generations per episode**. That was wrong by roughly
**10x**, because plates are **composites of reusable layers, not per-plate generations**.

The `systems-and-blowups` project already implements the layered model:
`asset-taxonomy.v1.json` defines a reusable vocabulary (19 actors, 13 objects, 8 mechanisms,
10 worlds), `assets/generated/cutouts/` holds keyed actor, building and mechanism cutouts, and
`style-profile.v1.json` declares four `depth_layers` — foreground cutout, actor or machine,
building or environment, evidence-safe region. A plate is one composite drawn from that
library. New generations per episode are the topic-specific props and any genuinely new pose:
plausibly **5–20**.

**Two production models coexist, and the volume estimate depends on which.** The composite
model above describes this repo's own `depth_layers` spec and the Wealth Logic reference. The
Alicia reference does the opposite: whole scenes generated per plate, with the character held
by reference conditioning — and its on-screen figures are consequently generated and often
wrong (`$12.991`, `$900,000 + 30% = $210,000`, `$10000` unseparated, a duplicated diagram
label). At 104K–1.95M views per episode that defect is evidently not fatal to distribution,
but it is exactly what `generated_text_rule` forbids and T4 rejects.

**Both models are supported; the rule is the same for both.** Whole-scene generation is
allowed provided scenes are generated **textless** and every figure is composited by the
renderer (T13). Composite recipes (T14) are then a *consistency* lever for recurring actors
and worlds rather than the only path, so the library need not be exhaustive before shipping.
Per-episode generation is ~5–20 under the composite model and ~150 under whole-scene, and a
lane may mix them slot by slot.

**Whole-scene ships today; composite is an optimisation, not a prerequisite.** The merged
slices (T1–T7 plus T13) already form a complete whole-scene path: paste script → coverage →
prompt pack → candidates → board → selection, with every figure composited as real type. T14
is net-new implementation *plus* a library build that gates nothing else. Given that the
reference evidence shows image quality is not what separates winners in this niche — one
static image earned 242K, wrong numbers earned 1.95M, good art earned 2.1K — **speed to
publish outranks plate quality, and composite should not block a first episode.**

**Take the cheap 80% instead: composite the host only.** The one asset that is already good is
the host character model. Compositing it as a foreground layer over whole-generated *textless*
backgrounds gives perfect host consistency — the single most visible continuity signal — at
zero library cost. The remaining taxonomy (worlds, mechanisms, secondary actors) stays
whole-generated until volume justifies building it. T14 is therefore re-scoped: **host-layer
compositing first, full catalog recipes deferred.**

**Per-episode generation cost, with sources (2026-08-22).** An earlier revision asserted
"$9–85 per episode" with no basis. Corrected against published pricing, for 450 generations
(150 slots x 3 variants) at 1024x1024:

| Route | Per image | 450 images |
| --- | --- | --- |
| GPT Image 2, low quality | $0.006 | **$2.70** |
| Nano Banana 2 Lite, batch tier | $0.0168 | **$7.56** |
| Kie GPT Image 2 1K | ~$0.03 | **$13.50** |
| Nano Banana 2, standard 1K | $0.039 | **$17.55** |
| GPT Image 2, medium | $0.053 | **$23.85** |
| GPT Image 2, high | $0.211 | **$94.95** |

The board already gates on a three-variant pick, so the efficient pattern is **draft low, finish
high**: 450 low-quality variants for selection, then re-render only the ~150 winners at high
quality — roughly $34 per episode. Given the operator's speed-over-quality position and the
evidence that plate quality is not what separates performers in this niche, **skipping the
finish pass entirely puts a full episode near $3.** Cost is not a constraint on this pipeline;
it never was.

**Manual subscription generation already works and is free at the margin** — the operator has
produced hundreds of plates that way. So the API decision is not about cost or capability; it
is about **attended time and what it makes possible.**

| | Manual via subscription | API |
| --- | --- | --- |
| Marginal cost per episode | $0 | ~$3 low-quality, ~$34 draft-then-finish |
| Wall clock for 450 variants | ~4–6 attended hours | ~4 minutes, parallelised |
| Attended? | Entirely | No |
| Three-variant selection | Impractical — nobody hand-generates 450 | The default |
| Asset capture | Manual download, rename, hash | Programmatic, sha256 at source |
| Prompt iteration mid-run | Natural | Needs a re-run |

Two consequences matter more than the hours:

1. **Manual generation makes plates the publishing bottleneck.** At ~5 attended hours per
   episode the cadence ceiling is a few episodes a week. On the API the ceiling moves to script
   writing — which is where the operator has identified the actual value (numbers and
   narrative), and where it should be.
2. **The board's variant gate only exists with the API.** Hand-generating three options for 150
   slots is not something anyone does, so manual collapses to one-shot-and-accept and the
   selection quality gate is lost.

**The split that follows** mirrors the design-tooling conclusion: manual for the **library
build** (one-time, attended, judgment-heavy — where a human iterating a prompt beats three
blind variants), API for **per-episode plate volume** (repetitive, unattended, variant-based).

**Cheapest viable middle:** given plate quality is not the differentiator, run **one variant per
slot** via API at low quality — ~150 images, roughly $1, about two minutes — and hand-generate
only the slots the exception-based board flags. That uses T5/T6 exactly as designed and reduces
manual work to the handful of plates that actually need judgment.

**Quality tier and consistency are separate axes — do not conflate them (2026-08-22).**

*Quality tier* controls refinement, and the gap is small. A 50-prompt blind benchmark scores
GPT Image 2 at 4.155 high / 4.108 medium / 3.946 low — a 0.209 spread across a roughly 15x
price range. Where high earns its cost is **dense text, close-up photoreal faces, and fine
material detail**. Two of those three are irrelevant here: plates carry **no generated text**
by rule, and the characters are stylized rather than photoreal. **Low is appropriate for
per-episode backgrounds and props.** The real risk at low is not softness but GPT Image 2's
documented **tiling/noise artifacts**, which are reported worse in backgrounds and
out-of-focus areas — spot-check for them and step to medium ($0.055) if they appear, still
about $8 per episode at 150 images.

*Consistency* comes from reference conditioning, not the quality tier, and the evidence on
GPT Image 2 there is genuinely split — some testers rate its reference adherence best in
class, others report the face shifting between generations **specifically when poses or
settings change**, which is this pipeline's exact use case. **OpenAI's own image guide lists
recurring-character and brand consistency among the model's current limitations.** Nano Banana
Pro accepts up to 14 reference images for character locking, with independent testing putting
the sweet spot at **4–6** (7+ degrades as the model averages conflicting details).

**The architecture makes this mostly moot, which is the point.** The host is composited as a
fixed cutout, so its consistency is structural, not model-dependent; backgrounds and props need
no character consistency at all. Reference conditioning therefore only has to hold during the
**library build** — a one-time job where the best available tool should be used regardless of
per-image cost. Concretely: build the library with Nano Banana Pro (or Nano Banana 2) at 4–6
references and high quality; generate per-episode backgrounds and props with GPT Image 2 low.

**The library is accretive, and that is the whole economic argument for compositing.** Each
episode's topic-specific props become permanent catalogue entries, so per-episode generation
falls as coverage rises: episode 1 buys the index-fund vocabulary, episode 5 buys the housing
vocabulary, and by episode 20 most slots resolve against existing assets. Whole-scene
generation throws its art away every time; this compounds.

The project catalogue already declares the right policy — `asset-catalog.v1.json` carries a
`resolution_order` cascade of `exact_semantic_match`, `reusable_component_composition`,
`deterministic_evidence_or_mechanism`, `bespoke_plate`, plus per-asset `semantic_tags`,
`identity_lenses`, `visual_worlds`, `resolution_tier`, sha256 and eligibility flags. **Nothing
executes it**, and it has no `style_version` field — which matters immediately, because the
25 assets about to be generated use a different style from the 18 already catalogued. T16
implements the resolver, the gap report and the style-version guard.

**A plate is illustrative or evidential, never both — decided 2026-08-22.** The p34 pilot
overlays evidence boards onto illustrative artwork, which forces the plate to reserve space it
was not composed for and puts a citation-density document where a viewer has ~8 seconds. The
performing references never do this: Wealth Logic *cuts* between an illustrative plate and a
plate that **is** the whiteboard.

Adopted as an architectural constraint:

- **Evidential slots** are `composed_plate` (T13). One figure at broadcast size, arithmetic
  verified, drawn as real type. This is where numbers live.
- **Illustrative slots** are `generated_plate` or `composite_plate`. They may carry a short
  composited label or callout, but **never a multi-section document**.
- Provenance stays visible as a small persistent chip rather than a full citation card. The
  pilot's "This is not proof" labelling discipline is retained — it is a differentiator — but
  it does not compete with the figure for attention.

This removes the overlay-collision problem without requiring the artwork to be
context-aware, and it routes every figure through work already merged and tested. Draw-on
animation (`stroke-dashoffset`, the T9 whiteboard technique) applies to composed evidence
plates, not to overlays on illustration.

**The library is not ready.** Operator assessment 2026-08-22: of the existing cutouts only the
host character model is good; the building, actor and mechanism cutouts are not. So there is a
real up-front cost — building roughly 50–100 usable cutouts across the taxonomy — but it is a
**one-time, attended, art-directed job**, not a recurring per-episode pipeline cost. That job is
exactly the one the design-tooling assessment recommends borrowing a tool for
(`docs/research/2026-08-22-agent-design-tooling-assessment.md`), and it gates T14.

Two consequences that change the architecture, not just the estimate:

1. **Character consistency is perfect by construction where a cutout is composited.** The
   character is literally the same PNG in every plate — zero drift, the same property the
   parametric SVG rig gives. Identity anchoring, reference conditioning and detail tiering
   therefore govern **building the library** (a bounded, one-time job) and not episode
   production.
2. **Three-variant fan-out is the wrong shape for a character-bearing slot.** Those slots want
   *layer selection from the catalog* — which world, which actor pose, which mechanism — not
   three fresh whole-plate generations. Added as T14. T4's fan-out stays correct for slots that
   genuinely need new art.

This still invalidates a naive
selection gate: a 1-of-3 manual pick across 150 slots means 150 operator decisions per episode,
which contradicts the minimize-human-in-the-loop goal outright. T5 and T6 therefore
**auto-select a default variant per slot and surface exceptions only** — low-confidence slots,
`identity_anchor` violations, suspected generated text, and near-duplicate neighbours. This
mirrors the graduated-autonomy model already adopted elsewhere in these docs.

**Presentation is not the differentiator — corrected 2026-08-22.** A three-source natural
experiment in one niche (recorded in `21-ART-STYLE-REFERENCE-REVIEW.md`) shows a video that
reuses **one static image for its entire 20:38 runtime** at ~242,000 views, against a
better-drawn competitor with real scene variety at ~2,100, and a 20-video channel with
comparable production that never clears 3,000. Packaging confounds the comparison and a
two-video sample proves no single cause, but it bounds how much presentation can possibly
explain — and it rules out out-animating this niche as a strategy.

Two consequences:

1. **A `caption_unit` lane is the cheapest shippable format in the system and is proven at
   six-figure scale.** One plate plus accurate word-timed captions.
   `hyperframes_unit.schema.json` already enumerates `caption_unit`, and the narration word
   timings already exist. Added as T11.
2. **The real axis is claim-bound plates.** The trading-psychology channels assert without
   evidence; Mr. Finance drives plates from actual figures. This repo already has the fact
   layer and never-fabricate guards none of them has. Prompt composition should take a slot's
   bound claim as its subject rather than only the narration excerpt — named as a follow-on
   in Not Building rather than retrofitted into completed T4.

**Some plates should be code, not pixels — added 2026-08-22.** The Casual Finance reference
(~1.7M views, 334K subs, built pre-AI) decomposes to about ten SVG paths: an oval, a hair
scribble, two dots, one curve, five lines. The operator's finding that prompting an image
model to "make bad stick figure explainers" fails is correct and has a specific cause —
diffusion renders crude as *muddy* (variable stroke weight, wobbling duplicate contours,
a head that changes shape), while the reference's crudeness is *confident*, which is a
signature of intent that a denoising process cannot fake.

The conclusion is not that the lane is unreachable but that pixels are the wrong medium for
it. A parametric SVG rig makes identity drift **structurally impossible** (it is the same path
data every time), costs nothing per plate against 450–810 paid generations per episode in the
diffusion lanes, and never emits generated text. `content/video_engine/src/assets/poses/`
already holds checked-in pose SVGs. Added as T12, with the sterility risk named there.

A convention from the same reference generalizes to every lane: where a plate must *imply*
text, draw a squiggle; where it must *say* something, the renderer composites real type. The
reference never draws fake readable text, which is exactly the failure that disfigures the
Lane D floor reference.

**Most plates should not be generated at all — added 2026-08-22.** The Wealth Logic reference
(the strongest performer reviewed: ~19x views-per-subscriber, so distributed algorithmically
rather than carried by an audience) puts *typography* in the content zone, not illustration —
a whiteboard reading `YR 1: $55,000`, an arithmetic stack `$50K + $36K` over a rule giving
`$86K TOTAL IN.`, certificate props labelled `3% BOND` and `5% BOND`. All of that lettering is
crisp and correct, which is only possible if it is composited type rather than model output.

Its scripts are also **parametric models**: two named actors, identical stated starting
conditions, then every input named (20% down on $250,000, 30-year at 7%, $1,330 monthly,
$1,800 rent) with every later figure derived. The plates are downstream of the arithmetic, so
they can be generated *from the model* rather than authored.

This argues for an explicit plate-kind split — `generated_plate` (an image model produces
pixels) versus `composed_plate` (the renderer draws type, props and data deterministically) —
added as T13. Composed plates carry zero generation cost, zero garbling risk and perfect
reproducibility, and they remove a large share of slots from the 450–810 generations per
episode estimated for the diffusion lanes.

It also reorders the lane priority. Lane E's advantage is a human drawing hand accumulated
pre-AI, the least transferable asset available. Lane F's advantages — a costume-anchored cast,
composited data plates, and plate-from-model generation — are all machine strengths. Build
order after the spine is `expert_explainer` first.

**Existing host assets already satisfy most of T8 — reviewed 2026-08-22.** The
`systems-and-blowups` project in the sibling worktree
(`content/video_engine/projects/systems-and-blowups/`) already holds
`finance-host-flow-character-pack.v1.json`, a `style-profile.v1.json`, an asset catalog and
taxonomy, and rendered host assets under `assets/generated/host/` — including a proper
character sheet (`finance-host-identity-master-v3.png`: full body plus present, shrug,
arms-crossed and point poses), a keyed full-body presenter cutout, and corner-stamp brand
marks.

Two independent confirmations, and one correction:

1. **The identity anchor is already ideal.** Deep-indigo suit, copper tie, black rectangular
   glasses, sculpted loc twists, goatee, gold lapel pin. That silhouette survives any
   flattening and is immune to facial drift — exactly the property derived from the Mr.
   Finance and Wealth Logic references.
2. **`style-profile.v1.json` already encodes two of the three cross-lane rules**, written
   before this review: `generated_text_rule` ("Generated imagery contains no authoritative
   facts numbers dates quotations or financial labels") and `motion_rule` ("Every movement
   must explain a causal or state change; decorative motion is forbidden"). Its
   `depth_layers` also names an `evidence_safe_region`, which is precisely the composed-plate
   content zone T13 should render into.
3. **An earlier claim that the host is "over-detailed" is retracted** — see the retraction
   section in `21-ART-STYLE-REFERENCE-REVIEW.md`. Three Alicia Invests episodes (99.6K subs;
   104K, 326K and 1.95M views) carry a fully rendered, soft-shaded presenter *and* dense
   composited figures at the same time, holding identity across 20- and 33-minute runtimes.
   Reference-image conditioning handles consistency at that rendition level, so rendition is
   not a drift risk. The legibility argument rested on the project's own corner-stamp asset,
   which is a **watermark sized as a watermark** — a bad basis for judging plate scale.

   The correct rule is that **rendition level and data legibility are independent axes**. A
   fully rendered character is compatible with dense figures provided the figures are
   composited type in a reserved, self-contrasting zone — the `evidence_safe_region` the
   style profile already declares. **Zone separation protects legibility, not flattening.**
   Nothing about the existing host assets needs redrawing.

**Sequencing.** T1–T6 are the spine and must land in order; nothing downstream is useful until
an operator can paste a script and look at a board. T7–T10 are independent of the spine and can
run in parallel with it. Within that group, T7 then T8 is the real critical path — character
consistency is the capability the reference channels actually depend on. T9 and T10 are spikes
whose failure would change the substrate decision above before anything is built on it.

## Patterns To Mirror

- Schema-plus-service-plus-CLI triad: `hyperframes_render.py` +
  `hyperframes_unit.schema.json` + `render-unit`/`verify-editor` subcommands in `cli.py`.
- Canonical hashing and artifact binding: `canonical_json` / `sha256_json` in `style_board.py`,
  and `_artifact_hash` / `_schema_errors` in `editorial_motion.py`.
- Validation-error accumulation returning a list rather than raising on first failure:
  `_semantic_plan_checks` (`editorial_motion.py:330`).
- Asset-ID-only binding with sha256 verification against a manifest:
  `validate_generated_visual_candidates` (`generated_visuals.py:104`).
- Stage function shape `run_stage(job: VideoRun, ctx: StageContext) -> StageOutput`:
  `shot_plan.py:774`, `style_board.py:949`.
- Named module constants over magic numbers: `_PLATE_MIN_HOLD_S`, `_DURATION_DRIFT_RATIO` in
  `hyperframes_render.py`.

## Task Slices

### T1: Paste-entry contract and provenance attestation
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/configs/source_attestation.schema.json`, `content/video_engine/configs/director_brief.schema.json`, `content/video_engine/src/services/script_ingest.py`, `content/video_engine/tests/test_script_ingest.py`, `content/video_engine/cli.py`
- Acceptance: `ingest-script` writes `source_attestation.json` and `director_brief.json` into a new run directory; a run without an attestation naming source, asserter, and asserted-at is rejected before any artifact is written; `references[]` accepts documents with `kind` and `sha256` so decks attach now and are read later; the paste-lane stage order omits `validating_research` and `awaiting_research_approval` while retaining `awaiting_publish_approval`.
- Validate: `python -m pytest content/video_engine/tests/test_script_ingest.py -q`
- Evidence: `content/video_engine/src/services/script_ingest.py`, `configs/source_attestation.schema.json`, `configs/director_brief.schema.json`, CLI `ingest-script`. 10 tests green. `paste_lane_stages()` proves the research gate is absent and the publish gate retained. A run missing any provenance field raises before the job directory is created.

### T2: Director request pack and validated proposal ingest
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: `content/video_engine/configs/director_proposal.schema.json`, `content/video_engine/src/services/director.py`, `content/video_engine/tests/test_director.py`, `content/video_engine/cli.py`
- Acceptance: `compile-director-request` emits `director_request.json` carrying the script, brief, lane options, and the exact proposal schema the agent must satisfy; `record-director-proposal` validates and persists `director_proposal.json` with `artifact_hash`; a second run of any downstream command replays the stored proposal and re-solicits only under `--refresh-proposal`; the engine makes no network call in either direction.
- Validate: `python -m pytest content/video_engine/tests/test_director.py -q`
- Evidence: `content/video_engine/src/services/director.py`, `configs/director_proposal.schema.json`, CLI `compile-director-request` and `record-director-proposal`. 12 tests green, including the rewrite guard: a proposal whose beats do not reconstruct the attested script is rejected as truncated, additive, or a rewrite. Two recordings of one proposal are byte-identical.

### T3: Provisional coverage compilation at estimated timing
- Status: complete
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/src/services/provisional_coverage.py`, `content/video_engine/tests/test_provisional_coverage.py`, `content/video_engine/cli.py`
- Acceptance: proposal compiles to an artifact validating against `editorial_coverage.schema.json` with `timing_basis: "estimated"`; every `slots[].duration_s` derives from word count ÷ configured WPM and the sum equals the script estimate within 1%; the artifact is refused by any render-timing consumer; slot count, `semantic_purpose`, `visual_archetype`, and `motion_recipe` come from the proposal but are repaired to legal enum values and to the cadence bounds rather than passed through.
- Validate: `python -m pytest content/video_engine/tests/test_provisional_coverage.py -q`
- Evidence: `content/video_engine/src/services/provisional_coverage.py`, CLI `compile-provisional-coverage`. 12 tests green. E2E run compiled 8 slots at `timing_basis: estimated` with `duration_drift_ratio: 0.0`. `assert_render_ready` refuses estimated coverage.

### T4: Multi-variant prompt fan-out and slot-bound candidate validation
- Status: complete
- Owner: implementation_luna
- Depends on: T3
- Write set: `content/video_engine/configs/visual_prompt_pack.schema.json`, `content/video_engine/configs/generated_visual_candidate_batch.schema.json`, `content/video_engine/src/services/visual_prompt_pack.py`, `content/video_engine/src/services/generated_visuals.py`, `content/video_engine/tests/test_visual_prompt_pack.py`, `content/video_engine/cli.py`
- Acceptance: `compile-visual-prompt-pack` emits one prompt group per coverage slot with `variants_per_slot` defaulting to 3 and never below 2; every prompt carries a negative-prompt clause forbidding lettering, numerals, logos, and watermarks; the candidate batch schema gains required `slot_id` and `variant_index` on each item; validation rejects a batch containing an unknown `slot_id`, a duplicate `variant_index` within a slot, or fewer than `variants_per_slot` items for any slot; a candidate marked `contains_factual_text: true` is refused render eligibility with an explicit message naming the no-generated-text rule; existing `generated_visuals` tests still pass.
- Validate: `python -m pytest content/video_engine/tests/test_visual_prompt_pack.py content/video_engine/tests/test_generated_block_images.py -q`
- Evidence: `content/video_engine/src/services/visual_prompt_pack.py`, `configs/visual_prompt_pack.schema.json`, CLI `compile-visual-prompt-pack` and `validate-candidate-batch`. 13 tests green. E2E: 8 groups x 3 variants = 24 requested generations, all 24 validated. Unknown slot, duplicate variant index, missing slot_id, short batch, and `contains_factual_text` are each rejected by name.

### T5: Three-tier scene board renderer
- Status: complete
- Owner: implementation_luna
- Depends on: T4
- Write set: `content/video_engine/src/services/scene_board.py`, `content/video_engine/tests/test_scene_board.py`, `content/video_engine/cli.py`
- Acceptance: `render-scene-board` writes `runtime/jobs/<run>/board/index.html` plus `board.json`; the page opens from `file://` with no network dependency, referencing candidate images by relative path; tier 1 lists attested sources and reference documents, tier 2 groups candidates by slot showing narration excerpt, archetype, motion recipe and duration with single-select per slot and an auto-selected default already applied, exception slots sorted to the top and visually flagged with their reason (low confidence, `identity_anchor` violation, suspected generated text, near-duplicate neighbour); tier 3 shows one video slot per selected image in a visibly disabled state; the page emits a selection JSON payload to the clipboard; no candidate lacking a verified sha256 is rendered.
- Validate: `python -m pytest content/video_engine/tests/test_scene_board.py -q`
- Evidence: `content/video_engine/src/services/scene_board.py`, CLI `render-scene-board`. 14 tests green. E2E board: 8 slots, 8 auto-selected, 0 exceptions. Page is 13,753 bytes, references only `assets/*.png` relative paths, and a regex assert proves no remote host is referenced.

### T6: Selection capture into the existing review contract
- Status: complete
- Owner: junior_developer
- Depends on: T5
- Write set: `content/video_engine/src/services/scene_selection.py`, `content/video_engine/tests/test_scene_selection.py`, `content/video_engine/cli.py`
- Acceptance: `record-scene-selection` accepts the board payload and emits `asset_selection_review.json` validating against the existing schema with `coverage_hash` and `candidate_batch_hash` bound; every slot without an explicit operator choice falls back to its auto-selected default so a 150-slot board records cleanly with zero operator input; a payload with zero or multiple explicit selections for any slot is rejected naming the slot; the review records which slots were auto-selected versus operator-chosen; `approved` cannot be set by product code without an explicit operator flag; a `video_intent` record is written per selected slot with `provider` unset.
- Validate: `python -m pytest content/video_engine/tests/test_scene_selection.py -q`
- Evidence: `content/video_engine/src/services/scene_selection.py`, CLI `record-scene-selection`. 12 tests green. E2E recorded 8 selections with `auto_selected: 8`, `operator_selected: 0`, `approved: false` and 8 video intents with `provider: null`, `status: not_requested`.

### T7: Style-pack registry for the seven art lanes
- Status: complete
- Owner: implementation_luna
- Depends on: none
- Write set: `content/video_engine/configs/video_style_pack.schema.json`, `content/video_engine/configs/style_packs/`, `content/video_engine/src/services/style_packs.py`, `content/video_engine/tests/test_style_packs.py`, `content/video_engine/cli.py`
- Acceptance: `validate-video-style-packs` (distinct from the existing `validate-style-packs`, which owns `style_pack_library.v1`) accepts seven packs whose `lane` values are exactly `expert_explainer`, `presenter_infographic`, `flat_cartoon_explainer`, `stick_explainer`, `cutout_history`, `woodblock`, `whiteboard`; each declares renderer, character policy (`stick_colour_block`, `blank_face`, `outlined_flat`, `soft_shaded_presenter`, `silhouette`, `none`) with a required `identity_anchor`, background policy, caption policy including position and highlight rule, and permitted motion recipes; a pack naming a HyperFrames runtime adapter outside the seven is rejected; a pack naming `rive` is rejected with an explicit message.
- Validate: `python -m pytest content/video_engine/tests/test_style_packs.py -q`
- Evidence: `content/video_engine/configs/video_style_pack.schema.json`, seven packs under `configs/style_packs/`, `src/services/style_packs.py`, CLI `validate-video-style-packs`. 19 tests green. Registry loads all seven lanes with `expert_explainer` first in build priority; `rive` is rejected with its reason (compiled binary, editor-only); an adapter outside the seven is rejected by name; burned-in captions without a position or highlight rule are rejected; every lane reserves an evidence region and offers `composed_plate`.

### T8: Character pose and expression library
- Status: pending
- Owner: parent
- Depends on: T7
- Write set: `content/video_engine/configs/character_pose_library.schema.json`, `content/video_engine/src/services/character_pose_library.py`, `content/video_engine/tests/test_character_pose_library.py`, `content/video_engine/cli.py`
- Acceptance: a pose library binds one `flow_character_pack.v1` character to N named poses and expressions, each carrying its own prompt delta, `asset_id`, and sha256, with the character sheet as the required reference; it ingests the existing `systems-and-blowups` host assets rather than regenerating them, using `finance-host-identity-master-v3.png` as the sheet and the keyed presenter cutout as the first pose. Each character declares an `identity_anchor` (costume colour block and silhouette) that every pose must preserve, so face drift cannot break continuity. The anchor carries an **episode-scoped garment slot**: the jacket may be swapped between episodes but is locked within one, and a pose whose garment differs from its episode's declared variant is rejected. Each pose declares a `detail_tier` of `master` or `plate`, distinguishing the full-resolution source from the optimised keyed cutout actually composited; this is an asset-pipeline concern (a 2.9 MB master is not composited 150 times) and carries no art-direction meaning — rendition level is explicitly not restricted, per the retraction recorded in the reference review. `art_bible_hash` becomes a binding to any registered art bible rather than only the BJJ history bible; a pose whose sheet reference is missing, whose `render_eligible` is still false, or which drops a required `reference_view` is rejected; the director can request a pose by name and receive a stable `asset_id`.
- Validate: `python -m pytest content/video_engine/tests/test_character_pose_library.py content/video_engine/tests/test_flow_character_pack.py -q`
- Evidence: pending

### T9: Whiteboard lane proof unit
- Status: pending
- Owner: implementation_luna
- Depends on: T7
- Write set: `content/video_engine/hyperframes/compositions/unit-whiteboard-proof-v1.html`, `content/video_engine/src/services/hyperframes_render.py`, `content/video_engine/tests/test_hyperframes_render.py`
- Acceptance: an SVG draw-on composition using `stroke-dasharray`/`stroke-dashoffset` driven by the paused timeline renders through the existing unit lane and passes the ffprobe duration check within `_DURATION_DRIFT_RATIO`; seeking to an arbitrary frame produces the same output as playing to it; `hyperframes_unit.schema.json` gains `whiteboard_unit` to `unit_kind` without breaking the four existing kinds.
- Validate: `python -m pytest content/video_engine/tests/test_hyperframes_render.py -q`
- Evidence: pending

### T10: Three.js lane proof spike
- Status: pending
- Owner: parent
- Depends on: T7
- Write set: `content/video_engine/hyperframes/compositions/unit-three-proof-v1.html`, `content/video_engine/src/services/hyperframes_render.py`, `content/video_engine/tests/test_hyperframes_render.py`
- Acceptance: a Three.js composition renders from `hf-seek` time with no `requestAnimationFrame` or `setAnimationLoop` as the source of truth; the root `[data-composition-id]` carries `data-duration` and a composition missing it is rejected by a unit-lane precheck rather than failing late at render with zero duration; assets load before seeking; the render passes the ffprobe duration check within `_DURATION_DRIFT_RATIO`.
- Validate: `python -m pytest content/video_engine/tests/test_hyperframes_render.py -q`
- Evidence: pending

### T11: Caption-unit lane — one plate, word-timed captions
- Status: pending
- Owner: implementation_luna
- Depends on: T7
- Write set: `content/video_engine/src/services/hyperframes_render.py`, `content/video_engine/configs/hyperframes_unit.schema.json`, `content/video_engine/tests/test_hyperframes_render.py`
- Acceptance: a `caption_unit` renders from exactly one plate plus canonical narration word timings, with caption groups drawn by the renderer as real typography and never baked into the plate; the unit passes the existing ffprobe duration check within `_DURATION_DRIFT_RATIO`; a unit supplying more than one plate is rejected naming the lane; caption grouping honours `_CAPTION_GROUP_WORDS`.
- Validate: `python -m pytest content/video_engine/tests/test_hyperframes_render.py -q`
- Evidence: pending

### T16: Asset resolver and the accretion loop
- Status: complete
- Owner: parent
- Depends on: T7
- Write set: `content/video_engine/src/services/asset_catalog.py`, `content/video_engine/configs/asset_catalog.schema.json`, `content/video_engine/tests/test_asset_catalog.py`, `content/video_engine/cli.py`
- Acceptance: a resolver executes the catalogue's declared `resolution_order` cascade in order — `exact_semantic_match`, then `reusable_component_composition`, then `deterministic_evidence_or_mechanism`, then `bespoke_plate` — matching a coverage slot against `semantic_tags`, `kind`, `visual_worlds` and `identity_lenses`, and returning the resolved `asset_id` with the tier it resolved at. Every asset carries a required `style_version`; a resolution that would mix style versions within one episode is rejected naming both. Assets with `render_eligible: false` never resolve for render, only for preview. `resolve-episode-assets` emits a **gap report** listing every slot that fell through to `bespoke_plate` — that report *is* the generation worklist, and each asset it produces is registered back into the catalogue, so library coverage rises and per-episode generation falls with every episode. The report also lists catalogue assets unused for N episodes as pruning candidates. Two runs against an unchanged catalogue and coverage produce byte-identical resolutions.
- Validate: `python -m pytest content/video_engine/tests/test_asset_catalog.py -q`
- Evidence: `content/video_engine/configs/asset_catalog.schema.json`, `src/services/asset_catalog.py`, CLI `resolve-episode-assets` and `register-assets`. 17 tests green. Cascade resolves in declared order and falls through tier by tier; the evidence tier only matches mechanism and board kinds; `--for-render` refuses assets that are not `render_eligible`; a coverage mixing `paper-cut-reduced-density-v2` with `crinkle-cut-v1` is rejected naming both. A four-slot fixture run reported `coverage_ratio: 0.5` with the two uncovered slots named as the generation worklist, and `test_accretion_closes_the_gap_it_reported` proves registering the missing asset takes the same coverage to 1.0. Two runs produce identical `artifact_hash`. **Intake of the real episode-1 library (25 assets, 2026-08-22) exposed two resolver defects, both now fixed and covered by tests.** (1) `resolve_slot` returned the first tier holding *any* candidate, so a host pose tagged `comparison` beat `mechanism-growth-comparison-v1` which matched on two tags; the cascade now breaks ties only, with strongest overlap winning. (2) Asset tags were split on `-` while slot tags were added whole, so identical tags never matched and `world-exchange-floor-v1` was unreachable; slot tags now contribute both forms. 19 tests green. Against the real catalogue the batch arrived registered at `resolution_tier: 3` with `kind: actor`/`prop`, which tier 3 excludes — 19 of 25 assets were unreachable and every actor slot fell through to `bespoke_plate`. Re-tiered to the catalogue's own convention and re-verified: 0 of 25 unreachable, 8 realistic probe slots each resolving to the correct asset of the correct kind. All 25 also arrived self-promoted to `rights_state: approved` / `render_eligible: true` and were reset to `review_only`; promotion is the operator's. See `docs/content-video-engine/23-EP1-LIBRARY-INTAKE-REVIEW.md`.

### T18: Sentence-level audio patch — fix a word without re-recording an episode
- Status: pending
- Owner: parent
- Depends on: T15, T17
- Write set: `content/video_engine/src/services/audio_patch.py`, `content/video_engine/configs/audio_patch.schema.json`, `content/video_engine/tests/test_audio_patch.py`, `content/video_engine/cli.py`
- Acceptance: `locate-audio-phrase` takes a phrase and the canonical word timings and returns the enclosing **sentence** span, its character count, its share of the episode, and the silence gap on each seam — proven against the real `current-bubble-mechanism` take, where "trillion won" resolves to a 6.281s, 94-character sentence at 320.643–326.924s carrying 0.813s and 0.511s seam gaps against a 0.383s median. A patch is **refused when either seam gap falls below the 10th-percentile gap for that take**, because a tight seam splices audibly; the refusal names the measured gaps. `compile-audio-patch` emits the sentence text plus the pronunciation dictionary id for re-synthesis and performs no network call and no paid request. **The patch operates on the narration stem, never on a final mix.** Measured on the p34 render: the "silent" seams around the target sentence sit at −28.5 dB and −22.9 dB mean against −23.2 dB for speech, so a music or ambience bed runs continuously underneath and the gaps are not gaps. Splicing narration into that track would cut the bed audibly. The service therefore requires a stem — pulled from ElevenLabs history, or re-synthesised — and refuses a source whose inter-word seams are not at least 20 dB below its speech mean, reporting both figures. Re-mixing after the patch is a separate deterministic step. `apply-audio-patch` splices the replacement at the seam midpoints, then rebuilds the master word list by offsetting every downstream word by `new_duration - old_duration`, so timings stay coherent without re-recording. Re-running `ingest-canonical-audio` on the patched master re-times all coverage slots automatically — **no plate, storyboard or render artifact is edited by hand**. The original master and its words file are retained beside the patched pair.
- Validate: `python -m pytest content/video_engine/tests/test_audio_patch.py -q`
- Evidence: pending

### T17: Pronunciation dictionary as a versioned, accretive artifact
- Status: complete
- Owner: parent
- Depends on: T15
- Write set: `content/video_engine/configs/pronunciation_dictionary.schema.json`, `content/video_engine/src/services/pronunciation_dictionary.py`, `content/video_engine/tests/test_pronunciation_dictionary.py`, `content/video_engine/cli.py`
- Acceptance: a repo-held dictionary artifact holds ordered rules, each either `alias` (`string_to_replace`, `alias`) or `phoneme` (`string_to_replace`, `phoneme`, `alphabet` of `ipa` or `cmu`), plus the ElevenLabs `dictionary_id` and `version_id` returned on sync. `sync-pronunciation-dictionary` pushes rules through `POST /v1/pronunciation-dictionaries/add-from-rules` on first run and `.../{id}/add-rules` thereafter, and is a no-op when the local artifact hash matches the recorded sync hash. **A phoneme rule is rejected unless the configured model is `eleven_flash_v2` or `eleven_v3`** — other models silently skip phoneme tags, so an unusable rule must fail loudly at authoring time rather than appear to work. Rules are matched longest-`string_to_replace`-first so a phrase rule wins over a bare-word rule. The artifact is accretive: each episode's corrections are appended and inherited by every later episode, and a rule replacing an existing `string_to_replace` is reported as an override rather than silently applied. No API key is read at validation time; only `sync` touches the network.
- Validate: `python -m pytest content/video_engine/tests/test_pronunciation_dictionary.py -q`
- Evidence: `content/video_engine/configs/pronunciation_dictionary.schema.json`, `src/services/pronunciation_dictionary.py`, CLI `preview-pronunciation` and `compile-pronunciation-sync`. 18 tests green. A phoneme rule declared against `eleven_multilingual_v2` is rejected naming the capable models; the same rule passes on `eleven_v3` and `eleven_flash_v2`. Rules order longest-target-first so a phrase beats a bare word; duplicate targets, alias-without-alias and phoneme-without-alphabet are all rejected. `compile_sync_request` targets `add-from-rules` when no `dictionary_id` is recorded and `add-rules` thereafter, and a monkeypatched socket proves it makes no network call. Accretion verified: adding a rule reopens `needs_sync`, replacing a target is reported as an override rather than applied silently, and earlier episodes' fixes survive later additions. Run against the real 2,445-word `current-bubble-mechanism` narration, `preview` showed the proposed `'Korean won'` rule was **dead** (0 matches) because the script actually reads "5,370 trillion won"; the scoped `'trillion won'` rule matches exactly once.

### T15: Canonical audio ingest — flip estimated timing to the render clock
- Status: complete
- Owner: parent
- Depends on: T3
- Write set: `content/video_engine/src/services/canonical_coverage_ingest.py`, `content/video_engine/tests/test_canonical_coverage_ingest.py`, `content/video_engine/cli.py`
- Acceptance: an operator supplies an ElevenLabs result — audio plus character-level word timings — and it validates against the existing `elevenlabs_canonical_audio.schema.json` with `status: ready`; the narration text must reconcile with the attested script exactly, using the same rule the director is held to, so a re-recorded or edited read is rejected rather than silently re-timed; slot boundaries are re-derived from real word timings and the coverage artifact is re-emitted with `timing_basis: canonical`, replacing rather than mutating the estimated artifact; `assert_render_ready` then passes where it previously raised; total duration comes from the audio, never from word count, and a slot whose measured duration exceeds the 8s contract cap is reported rather than clamped; the estimated artifact is retained alongside for diff.
- Validate: `python -m pytest content/video_engine/tests/test_canonical_coverage_ingest.py content/video_engine/tests/test_provisional_coverage.py -q`
- Evidence: `content/video_engine/src/services/canonical_coverage_ingest.py`, CLI `ingest-canonical-audio`. 14 tests green, plus an end-to-end run against the **real** `current-bubble-mechanism` take: 99 blocks, 980.806s, 2,445 master word timings, monotonic, and the read reconciled against the real script exactly. The estimate put the episode at 1047.794s across 223 slots; measured came back at **980.806s**, off by 67s (6.8%) — which is precisely why render never runs off the estimate. `assert_render_ready` refused the estimate and accepted the canonical artifact; 0 slots exceeded the 8s cap. A rewritten, truncated or extended take is rejected naming the divergence word.

### T14: Composite recipes — plates assembled from the catalog
- Status: deferred
- Owner: parent
- Depends on: T7, T8
- Write set: `content/video_engine/configs/composite_recipe.schema.json`, `content/video_engine/src/services/composite_recipe.py`, `content/video_engine/src/services/visual_prompt_pack.py`, `content/video_engine/src/services/scene_board.py`, `content/video_engine/tests/test_composite_recipe.py`, `content/video_engine/cli.py`
- Acceptance: **Phase 1 (host-layer only, the shippable part):** a slot may composite one approved character cutout as a foreground layer over a whole-generated textless background, bound by `asset_id` plus sha256, with the evidence-safe region left clear; two renders of the same pairing are byte-identical. **Phase 2 (full catalog, deferred until volume justifies it):** a coverage slot may declare `plate_kind: composite_plate` alongside the existing generated and composed kinds; a recipe names one asset per `depth_layer` declared by the active style profile (foreground cutout, actor or machine, building or environment) and binds each by `asset_id` plus sha256 against the project asset catalog, never by raw path; a recipe naming an asset absent from the catalog, or one whose sha256 does not match, is rejected; composite slots are excluded from the prompt pack exactly as composed slots are, and counted separately in the pack summary; two renders of the same recipe are byte-identical because the same cutouts are composited; the scene board offers layer alternatives per slot rather than whole-plate variants for these slots; a recipe leaving the evidence-safe region occupied is rejected so composed type always has somewhere to land.
- Validate: `python -m pytest content/video_engine/tests/test_composite_recipe.py -q`
- Evidence: pending

### T13: Composed plates — typography and data without an image model
- Status: complete
- Owner: parent
- Depends on: T7
- Write set: `content/video_engine/configs/composed_plate.schema.json`, `content/video_engine/src/services/composed_plate.py`, `content/video_engine/src/services/visual_prompt_pack.py`, `content/video_engine/tests/test_composed_plate.py`, `content/video_engine/cli.py`
- Acceptance: composed content renders into the `evidence_safe_region` declared by the active style profile's `depth_layers`, never over the character; a coverage slot declares `plate_kind` of `generated_plate` or `composed_plate`, defaulting to generated so existing behaviour is unchanged; composed slots are excluded from the prompt pack entirely and the pack's `requested_generations` drops accordingly; a composed plate renders whiteboard figures, an arithmetic stack, and a labelled two-item comparison from structured values rather than a prompt, emitting real type; two renders of the same values are byte-identical; a composed plate whose declared figures do not match its source values is rejected rather than rendered.
- Validate: `python -m pytest content/video_engine/tests/test_composed_plate.py content/video_engine/tests/test_visual_prompt_pack.py -q`
- Evidence: `content/video_engine/configs/composed_plate.schema.json`, `src/services/composed_plate.py`, CLI `compose-plate`, plus prompt-pack integration. 14 tests green. Four layouts render deterministic SVG from structured values with `generation_cost_usd: 0.0`; an arithmetic stack whose operands do not match its declared total is refused rather than drawn; composed slots are excluded from the prompt pack and counted in `composed_slot_count`; an all-composed coverage needs no pack at all; operator text is HTML-escaped into the markup.

### T12: Parametric stick rig — SVG poses, no image generation
- Status: pending
- Owner: parent
- Depends on: T7
- Write set: `content/video_engine/configs/stick_rig.schema.json`, `content/video_engine/src/services/stick_rig.py`, `content/video_engine/src/assets/poses/`, `content/video_engine/tests/test_stick_rig.py`, `content/video_engine/cli.py`
- Acceptance: a rig renders a named pose to inline SVG from joint coordinates plus fixed head, hair and face parts, with no image provider involved and no raster asset produced; two renders of the same pose and seed are byte-identical, and two different slot ids produce visibly different control-point jitter so plates are not mechanically identical; a pose referencing an unknown joint or a missing part is rejected by name; text is emitted either as real type or as an explicit squiggle path, and a rig asked to render readable lettering into the artwork is refused.
- Validate: `python -m pytest content/video_engine/tests/test_stick_rig.py -q`
- Evidence: pending

## Deviations

Recorded during T1-T6 implementation on 2026-08-22.

1. **Added `content/video_engine/src/services/artifact_io.py`** (not in any slice write
   set). Six new modules all need canonical JSON hashing. The existing helpers live in
   `style_board.canonical_json` (pulls Pillow) and `editorial_motion._artifact_hash`
   (pulls the full motion compiler), neither of which the paste lane needs. Duplicating
   the hash contract six times would violate DRY; importing either would drag heavy
   dependencies into a lane that has none.

2. **Added `content/video_engine/tests/conftest.py`** (not in any slice write set).
   Shared paste-lane fixtures and builders for six test modules. No conftest previously
   existed under `content/video_engine/tests/`.

3. **`slot_id` and `variant_index` are optional in
   `generated_visual_candidate_batch.schema.json`, not required.** T4's acceptance said
   required. Making them required in that shared schema would invalidate every existing
   documentary-lane batch, which carries `role` but no slot binding. They are instead
   **required by the paste lane** in `visual_prompt_pack.validate_candidate_batch`, which
   is where the plan's acceptance behaviour is actually tested and enforced. Net effect
   on the paste lane is identical; the documentary lane keeps working.

4. **Added optional properties to two existing schemas.** `editorial_coverage` gained
   `timing_basis` and `source_artifact_kind`; `asset_selection_review` gained
   `timing_basis`, `auto_selected_slot_ids`, and `selections[].selection_source`. All are
   optional and absent-means-previous-behaviour, so existing artifacts still validate —
   confirmed by `test_configs.py`, `test_editorial_motion.py`, and
   `test_living_editorial_stock.py` staying green.

5. **`_bound_hash` fallback in `scene_board.py`.** A run agent may return a candidate
   batch without stamping `artifact_hash`; the first end-to-end run did exactly that and
   left `candidate_batch_hash: null` in the selection review. The board now derives the
   digest from batch content when it is unstamped, so the review is always bound to the
   exact batch that produced it. Found by `test_scene_selection.py`, fixed in the service
   rather than the test.

6. **Named agents were not used.** `docs/runbooks/PRP_EXECUTION.md` routes slices to
   `implementation_luna`, `junior_developer`, and `speedster`. Those agent types are not
   registered in this session, and the session carries a standing instruction not to
   invoke subagents unless the user asks. The parent implemented and verified every slice.

7. **T7-T10 not started.** This pass delivered the T1-T6 spine only. The lane work
   (style-pack registry, character pose library, whiteboard and Three.js proofs) remains
   `pending`, so the plan stays `running` rather than `complete`.

8. **`validate-style-packs` was already taken.** That command owns
   `style_pack_library.v1` (woodblock calibration packs). T7's command is
   `validate-video-style-packs`, and the plan text was corrected to match before
   implementation.

9. **The lane count moved from five to seven during the reference review.**
   `expert_explainer` was added after the Wealth Logic review and `stick_explainer`
   replaced `crude_stick_comedy`. T7's title, scope line and acceptance disagreed with
   the Execution Path table; all four were reconciled to seven lanes before writing code.

10. **Adapter validation runs before schema validation in `style_packs.py`.** The schema
    enum would otherwise reject `rive` with a bare "not one of [...]" and swallow the
    actionable reason, which is precisely what T7's acceptance asks for. Found by
    `test_rive_is_rejected_by_name_with_the_reason`.

11. **`plate_kind` is optional on coverage slots, defaulting to `generated_plate`.** T13's
    acceptance specified the default; recording it here because it means existing coverage
    artifacts keep their behaviour with no migration.

12. **Two policies were de-duplicated into the style-pack registry, touching files owned by
    completed slices.** `visual_prompt_pack.identity_anchor_for_lane` (T4) and the director's
    operator-copy policy (T2) each held their own copy of a value the registry now owns.
    Duplicated policy is exactly what drifts, so both now read from `style_packs.get_pack`.
    Both slices' tests still pass unchanged. The `expert_explainer` lane also had to be added
    to the `lane` enum in three schemas written before it existed.

## Verification

Per slice, the command named in that slice. Full gate before the plan closes:

```bash
python -m pytest content/video_engine/tests -q
```

```bash
python scripts/prp_validate.py .claude/PRPs/plans/P14-DIRECTOR-AND-SCENE-BOARD.plan.md
```

Known baseline: five failures in `content/video_engine/tests/test_history_v4_pipeline.py` are
pre-existing on a clean tree, proved by `git stash` in an earlier session and tracked
separately as task `task_5672544a`. Any sixth failure is a regression from this plan.

End-to-end acceptance, run once after T6:

```bash
python -m content.video_engine.cli ingest-script --script docs/content-video-engine/samples/paste-sample.txt --attest runtime/attestations/sample.json
```

followed by `compile-director-request`, `record-director-proposal`,
`compile-visual-prompt-pack`, `record-generated-visuals`, `render-scene-board`, and
`record-scene-selection`, ending with a board that opens offline and an
`asset_selection_review.json` that validates.

Determinism check: run the full sequence twice against the same stored proposal and diff
`runtime/jobs/<run>/` — every artifact except timestamps must be byte-identical.

## Evidence And Handoff

- Plan: this file.
- Report on completion: `.claude/PRPs/reports/P14-DIRECTOR-AND-SCENE-BOARD-report.md`.
- Doc updates on completion: a new `docs/content-video-engine/20-DIRECTOR-AND-SCENE-BOARD.md`
  covering the paste lane, the estimated-vs-canonical timing rule, and the selection gate; plus
  an amendment to `docs/content-video-engine/08-TOOLING-ALTERNATIVES.md` recording the Rive
  exclusion, the Lottie consume-only rule, and the Paper deferral with its stated reasons.
- Reference evidence: `docs/content-video-engine/21-ART-STYLE-REFERENCE-REVIEW.md`, written
  from the 2026-08-22 frame review of five operator-supplied videos and three thumbnails,
  including a strong/weak reference pair in the same format for Lane D. Frames were extracted
  locally and are not retained; the document records the derived style contract, not the
  source frames.
- Standing constraints unchanged by this plan: the Google Flow queue remains paused, no paid
  video job is released, generated outputs stay quarantined and are not promoted to the asset
  catalog, and provider keys live only in environment variables.
- Open item carried in: canonical ElevenLabs audio for episode 1 still does not exist, so no
  paste-lane run can reach authoritative coverage or final render until that operator-gated,
  paid step happens. The board and selection gate are deliberately reachable without it.
