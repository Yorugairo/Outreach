# Higgsfield Explainer Learnings and Producer Orchestration

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

This document records the transferable production ideas from the official
Higgsfield explainer skill and prompt templates. It is a creative and systems
reference, not a renderer license. Higgsfield source material, creator names,
source frames, and provider prompts never become factual evidence or renderer
inputs in this repository.

Official references: [explainer skill](https://raw.githubusercontent.com/higgsfield-ai/skills/main/higgsfield-video-explainer/SKILL.md)
and [prompt templates](https://raw.githubusercontent.com/higgsfield-ai/skills/main/higgsfield-video-explainer/references/prompts.md).

## Durable learnings

1. **Choose the visual system first.** A concise style key and descriptor are
   repeated on every block so palette, medium, line, fill, and finish remain
   stable. This is an internal art-bible hash in our pipeline, never a creator
   imitation prompt.
2. **Compile narration into typed blocks.** The reference workflow uses ordered
   ten-second blocks, one clear action per block, one narration take, and an
   exact block-to-clip pairing. Our editorial coverage stage keeps the finer
   1.5–3 second micro-events required for documentary pacing while allowing an
   external motion producer to receive a ten-second source block.
3. **Audio is a separate layer.** Narration is generated or recorded first;
   provider clips remain silent. Remotion owns captions, citations, credits,
   and final timing, so provider text cannot invent a claim or drift from the
   approved script.
4. **Consistency is a production contract.** A recurring fictional learner or
   mascot can be a useful visual anchor, but it is never a historical witness.
   Historical people and places come from approved local assets or explicitly
   labelled illustration/reconstruction.
5. **Retry by job identity.** Async provider work is resumed by task/job ID;
   the engine must not duplicate a running request. Every result is cached,
   hashed, reviewed, and remains a candidate until asset-manifest promotion.
6. **Prompts describe one action, not a whole film.** Scene, motion, audio, and
   negative constraints are structured separately. Research citations, rights
   state, URLs, and unresolved paths remain outside provider prompts.

## Candidate visual signature: woodblock comic

The recent GPT video experiment suggests a stronger anchor than generic flat
vectors: a Japanese woodblock-informed comic language with deep navy ink,
weathered paper, limited rust/ochre accents, carved-looking contours, and
deliberately illustrated martial-arts silhouettes. This can become a defining
profile for reconstruction and concept beats when a producer can preserve
character ownership and readable contact geometry.

The profile is a **period-informed visual abstraction**, not a reproduction of
an artist, anime franchise, historical print, or supplied frame. It should be
encoded as internal style atoms such as `woodblock-paper-field`,
`carved-ink-contour`, `limited-period-palette`, and
`illustrated-martial-silhouette`, then tested as a fork of the branded-literature
art bible. Archive photographs remain the evidence mode; woodblock comic frames
must carry an `ILLUSTRATION / RECONSTRUCTION` label. The first acceptance test is
not visual novelty alone: compare a generated still and a short motion clip for
silhouette continuity, absence of text artifacts, readable subject ownership,
and safe editorial contrast against the archive mode.

## Option A: orchestrate producers, keep our editor

The engine now compiles `producer_plan.v1` beside
`editorial_coverage.v1`. Each coverage slot becomes a typed block with:

- the reviewed narration excerpt, claim/citation and asset references;
- an immutable art-bible/style-key hash;
- preferred still producers (built-in GPT image generation, Magnific Nano
  Banana 2, approved stock, or deterministic assets);
- optional motion producers (Magnific Kling, an optional Higgsfield adapter,
  Remotion, or Manim);
- a provider-safe scene/motion/audio/negative prompt contract; and
- a hard boundary that provider output is not render-eligible.

The plan is deliberately additive to V4.1. Existing gates and legacy jobs do
not change. The sequence is:

```text
research + editorial coverage
→ producer plan
→ still producer(s)
→ human asset/visual review
→ optional short motion producer
→ local hash and rights/disclosure checks
→ Remotion/Manim assembly, captions, citations, and credits
→ Gate A → Gate B
```

Operators can inspect the handoff without invoking a provider:

```powershell
python -m content.video_engine.cli validate-producer-plan producer_plan.json
```

This makes the engine an orchestrator rather than a hand-drawn frame factory.
It also keeps a deterministic fallback: an external producer can be omitted,
and the same block can resolve to an approved local illustration, stock asset,
Manim diagram, or Remotion motion recipe.

## Provider boundary and current capability

The current Codex environment exposes the built-in GPT image generator, which
is suitable for original style keys, recurring fictional learners, and
illustrated reconstruction plates. It does not expose a GPT video-generation
tool in this session. A subscription alone does not add a callable video
adapter; video remains an optional Magnific/Kling, Higgsfield, or other provider
integration behind the same plan and review boundary.

No Higgsfield MCP/CLI dependency is required for V4.1. If an adapter is added,
it must consume producer blocks, preserve the shared style key, support task-ID
resume, and return a quarantined local candidate. It cannot approve facts,
rights, assets, or gates.

## What we intentionally do not copy

- No provider-generated narration, captions, logos, or historical claims.
- No raw consultant prompts, reference-pack frames, or “in the style of” text.
- No ten-minute opaque provider render as the canonical master.
- No automatic acceptance of a generated learner as a historical person.
- No provider cost or plan entitlement inferred from a successful API response.

## World plates for weak documentary roles

The first Episode 1 pass exposed a boundary in Option A: deterministic local
maps, relationship graphs, and concept cutaways were technically valid but
visually weak. The V4.1 revision therefore routes those roles through the same
high-quality still producers used for the woodblock learner, while preserving a
strict evidence boundary:

| Role | Generated plate supplies | Deterministic post layer supplies |
|---|---|---|
| `map_timeline` | period paper, port/ship atmosphere, unlabeled world, blank date rail | reviewed places, route, dates, chronology, citations |
| `lineage_concept` | woodblock scroll, branch texture, blank medallions, vignettes | named entities, typed verbs, uncertainty labels, citations |
| `concept_mechanics` | visual metaphor, silhouette, depth, material language | the reviewed concept sentence, explanatory labels, citations |

Generated geometry is never treated as a map, relationship, date, or factual
document. The plate is selected for hierarchy and tone; Remotion adds the
meaning-bearing overlays. This makes the image producer responsible for visual
quality without asking it to decide history.

The review-only contract is `motion_selected: true` in a generated candidate
batch. It is separate from `style_board_selected`, remains
`render_eligible: false`, and is hash-bound to a revision contact sheet. The
authoritative proof revision is stored under the Episode 1 job as
`generated_visuals/revisions/generated-world-first-v1/` and
`style_board/revisions/generated-world-first-v1/`; the approved active board is
not overwritten.
