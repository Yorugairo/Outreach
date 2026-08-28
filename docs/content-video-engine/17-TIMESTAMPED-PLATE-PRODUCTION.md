# Timestamped Plate Production

> **STATUS: DEPRECATED.** Kept for the reasoning trail; the held-still / hard-cut pattern is deprecated — see **29** Part 8–9. Do not follow this document as current doctrine.

*Specification of record for the still-image production schedule in the History
documentary lane.*

## 1. Decision

The production schedule is the approved, timestamped editorial coverage—not
generic scenes, narration excerpts, or provider block boundaries. A world pack
is reusable infrastructure. A **primary plate** is the unique visual assigned to
one timed coverage slot.

The frozen legacy candidate pack contains 138 slots over 607.999 seconds, but
it is **not** the active Episode 1 edit source. The frozen V3 and V4 schedules
have the same 139 contiguous slots over **559.922 seconds**, but the active
source is `canonical_visual_coverage.v9`, derived directly from the final
ElevenLabs word timings. V9 preserves the sentence-boundary correction,
recognizes meaningful subject-led enumerations (for example, “theaters,
demonstrations, challenges…”), and strips explanatory framing from lists (for
example, “It shows why techniques, labels, and teaching methods …”). Every
enumerated item, parallel modal clause, and explicit research inventory
therefore retains an explicit action
requirement. Each
canonical slot is
the image brief: it receives one distinct, narration-relevant primary plate or
one rights-approved archival/still selection. The goal is continuous visual
storytelling, not repeated plate movement.

```text
coverage slot (start, end, narration, claim/citation)
→ one timestamped primary plate prompt or approved archival selection
→ approved asset ID
→ timed editorial shot with local layers and restrained motion
```

The timing makes editorial assembly arithmetic: the selected primary plate
starts at the slot's `start_s`, occupies its `duration_s`, and hands the
following slot its next visual state. A longer idea receives multiple timed
slots; it does not receive one plate that is cropped, panned, or held until it
becomes repetitive.

The reusable operating workflow is
`.agents/skills/history-editorial-asset-foundation/SKILL.md`. This specification
remains the rule owner; the skill applies its schedule, world, quarantine, and
promotion rules without duplicating factual history.

## 2. Congruence before generation

`timestamped_plate_prompt_spine.v1` is the creative continuity contract. It
contains only original, internal rules:

- global palette, material, framing, safety, and generated-text prohibitions;
- a chapter-specific story world and visual arc;
- entry and exit motifs that make adjacent plates feel connected;
- safe character staging rules; and
- recurring motifs that can evolve across a chapter.

Each generated prompt combines its coverage slot with that spine and records
the preceding and following visual archetypes. It must describe one clear
visual action or state change that serves its narration excerpt. It must not
contain creator names, source frames, "in the style of" language, facts as
generated text, dates, labels, citations, or an invented identifiable
historical likeness.

The spine's `shot_sequences` carries a pre-written `plate_directions` sequence
for every parent shot. The compiler refuses to run unless every coverage parent
has exactly as many directions as timestamp slots. This prevents a generic
"period comic block" label or a repeated narration excerpt from becoming a
generic, repeated image prompt.

Facts remain local editorial elements. Generated image pixels communicate
world, action, mood, and metaphor; approved assets and Remotion carry dates,
claims, citations, maps, and relationship verbs.

For a qualified historical claim, a generated plate must not use a
document-shaped prop, certificate, source-like tabletop, or a visually complete
handoff as a substitute for proof. It may establish a social setting, but it
must not contradict a narration that says the record is incomplete,
multi-path, or contested. Reject the candidate rather than trying to repair
that evidentiary implication in post.

### World identity is independent of visual medium

“Woodblock” is a rendering language, never a substitute for location or
period. Each chapter must therefore declare a world lock that names the place,
architecture, clothing, vegetation, climate, and social setting it needs. The
Belém chapter, for example, requires an Amazonian Brazilian river-city world;
it must not silently default to Japanese tatami rooms, pagodas, or dress just
because the illustration medium uses carved ink and flat color.

For the active schedule, the job-local amendment
`content/video_engine/projects/history-of-bjj/episode-1-canonical-v9-prompt-amendment.v1.json`
applies that lock to coverage slots 081–116, including the parallel-role and
research-inventory actions. A failed generation is recorded as a rejected candidate
rather than being kept because its medium looks good.

## 3. Primary plate rule

For this lane:

- Every selected coverage slot has exactly one primary plate assignment.
- A reused world is a reusable **world kit**, not a reused primary plate. A
  different time, composition, action, or informational relationship requires a
  different plate.
- One primary plate may be generated, selected from a rights-reviewed archive,
  or selected from a rights-reviewed stock still. Its source and rights status
  stay in the asset manifest.
- Provider ten-second blocks are delivery/cache units only. They never collapse
  multiple timestamp slots into one visual assignment.
- The legacy `generated_image_block_plan.v1` excerpt-grouping behavior remains
  available for old jobs. New production uses `timestamped_plate_plan.v1`.
- Reusing a primary plate needs an explicit future `continuity_reprise` record,
  including its editorial reason and a human approval. No such exception is
  part of the Episode 1 baseline.

## 4. Batch and review policy

The complete production plan may contain all 138 prompts. Generation and human
promotion happen in bounded review waves of **8–12 images**, with 12 as the
maximum default. Each wave receives a contact sheet and checks:

- chapter palette/material continuity and a readable next-scene connector;
- subject hierarchy, full-frame composition, and valid character/prop contact;
- no accidental anatomical, object, or staging conflicts;
- a usable quiet region for any later local fact surface; and
- one clearly distinguishable visual purpose for the associated time interval.

Do not generate an entire episode blind merely because still generation is
inexpensive. A weak first wave should update the prompt spine before further
generation. Rejected candidates remain quarantined; selected assets still need
the existing rights/hash promotion process before rendering.

## 5. Episode 1 commands

The Episode 1 source spine is
[`episode-1-timestamped-plate-prompt-spine.v1.json`](../../content/video_engine/projects/history-of-bjj/episode-1-timestamped-plate-prompt-spine.v1.json).
Compile the job-local plan with:

```powershell
python content/video_engine/cli.py compile-timestamped-plate-plan `
  --coverage ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/editorial_coverage.selected.json" `
  --prompt-spine content/video_engine/projects/history-of-bjj/episode-1-timestamped-plate-prompt-spine.v1.json `
  --art-bible-id combat-history-longform-cutout-fork-v1 `
  --art-bible-hash e588e5d262b5de173022c34ecaa6e24d39f3ad447500dc13a44545ccbd62c559 `
  --output ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/timestamped-plate-plan.v1.json"

python content/video_engine/cli.py validate-timestamped-plate-plan `
  ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/timestamped-plate-plan.v1.json" `
  --coverage ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/editorial_coverage.selected.json" `
  --prompt-spine content/video_engine/projects/history-of-bjj/episode-1-timestamped-plate-prompt-spine.v1.json
```

The compiler and validator perform no provider calls. Image generation, asset
promotion, animation, narration, and final assembly retain their existing
operator gates.

## 6. Promotion after candidate-pack approval

An approved contact sheet does not mutate the candidate inventory. The
`promote-timestamped-plates` command creates a new, immutable
`asset_manifest.v1`, verifies every local byte against its candidate SHA-256,
and binds the resulting asset ID to its exact coverage slot in metadata. The
standard asset resolver then becomes the only renderer-facing source of these
plates.

```powershell
python -m content.video_engine.cli promote-timestamped-plates `
  --inventory ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/timestamped-plate-candidate-inventory.v1.json" `
  --plan ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/timestamped-plate-plan.v1.json" `
  --job-dir ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080" `
  --manifest-id history-of-bjj-episode-1-timestamped-plates-v1 `
  --project-id history-of-bjj `
  --episode-id how-judo-became-brazilian-jiu-jitsu `
  --approved-by "Operator timestamped plate pack approval" `
  --approved-at 2026-08-01 `
  --output content/video_engine/projects/history-of-bjj/episode-1-timestamped-plates-asset-manifest.v1.json
```

The older manifests V1 and V2 are frozen candidate inventories only. They
cannot become assignments merely because their images are nearby in timestamp
order. The new action waves are also `quarantined_review_required`; no new
wave asset is render-eligible until an explicit canonical-slot assignment,
hash check, and asset review bind it to the active canonical coverage hash.

This distinction is essential: the all-original legacy manifest V2 proves
that prior images are locally available, not that they match the 559.922-second
canonical narration. A future Episode Production Gate must bind the active
episode to a newly promoted canonical assignment manifest deliberately. It
does not start animation, narration, assembly, Gate A, or publication.

## 7. Canonical-audio editorial binding

The plate plan is a candidate visual inventory; canonical ElevenLabs word
timings are the final spoken timebase. `analyze-timestamped-semantic-coverage`
first binds each authored plate group to its exact ordered narration phrase and
emits every missing interval as a `generation_required` semantic slot. A new
plate prompt and asset assignment are required for each emitted slot before
`compile-timestamped-editorial-motion` may render.

The compiler rejects an unmatched excerpt, uncovered canonical prose, missing
plate, stale plan hash, unpromoted asset, or an image hold above **six
seconds**. It must never absorb unrepresented narration into the preceding
plate, proportionally retime an unrelated plate across it, or fill a gap with a
legacy asset. Those failures create a static or semantically false pseudo-scene
and are rejected rather than hidden by a slow zoom.

When an inherited coverage plan is incomplete, the replacement planning command
is `compile-canonical-visual-coverage`. It derives contiguous **2–6 second**
slots directly from the final word timings, assigns each slot an intent and any
journey/list action, and intentionally emits no asset IDs. Existing plates are
then candidates for explicit semantic selection, never defaults. This preserves
the useful prior art while preventing a plate from being chosen because it
happens to sit near the right timestamp.

The emitted plan deliberately contains no burn-in captions, fact citations,
generic text boxes, or information surfaces. Its default is a hard cut to each
new plate and a locked camera; only sparse, 1% focal-point pushes are allowed.
This makes plate changes—not background drift—the primary editorial motion.

The first explicit binding is a deliberately non-renderable V3 review artifact at
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/canonical-visual-assignment.wave-001.v1.json`.
It covers canonical slots 001–025 only, binds only newly generated wave assets,
and records sub-slot hard cuts for the opening contrast and the two meaningful
lists. It is proof that new imagery is being mapped to spoken semantics, not a
license for an editor to insert old material. A renderer must reject this
partial/quarantined assignment until all 139 active canonical slots have an
approved promoted asset manifest. Every successor binding must name its exact
coverage hash; it may not silently treat an earlier V3–V10 binding as current.
V5–V9 asset waves remain candidate provenance until a successor assignment or
explicit promoted-adoption record carries their exact source hashes forward.

```powershell
python -m content.video_engine.cli compile-timestamped-editorial-motion `
  --plate-plan ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/timestamped-plate-plan.v1.json" `
  --asset-map content/video_engine/projects/history-of-bjj/episode-1-timestamped-plates-asset-manifest.v2.json `
  --audio ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/higgsfield-audio-lane/canonical-audio-v2.json" `
  --words ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/audio/canonical/history_episode_1_master.words.json" `
  --pacing-recipe ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v16-contained-kano/pacing-recipe.json" `
  --output ".context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v17-timestamped-original/editorial-motion-plan.json"
```

For the current pilot, plan slot 004 was replaced by an original, approved
illustration. The Web Japan Kodokan page is retained as research/citation
provenance only: its footer says “All rights reserved,” so its credited photo
does not enter the render manifest. The all-original manifest V2 has 138/138
render-eligible timestamped plates and hash
`268625f2b4c11e63b256a9d139f1f008e171ccba1a4b98c5b76932a92a81027b`.

## 8. Intent and action brief before generation

Each timestamped prompt also receives an editorial intent and an action brief
before image generation or assembly. This prevents an otherwise attractive
image from being semantically interchangeable with its neighbors.

| Spoken intent | Required visual response |
| --- | --- |
| Academic / institutional | school, archive, desk, teaching, classroom, or formal setting |
| Martial | safe practice, contest, artifact, rule marker, or training setting—not a complex technique tutorial |
| Scenic / setting | place-first world: architecture, river, port, weather, or street activity |
| Travel / region change | reviewed map or route cut-in, then a place-specific travel or arrival image |
| Enumerated list | one meaningful action per list item: cutaway, pop-out asset, route step, or prop/character beat |

The list rule does not mean cutting on every noun. It applies where the
narration intentionally enumerates items, such as schools, teachers, rules,
and public meaning. Those items need distinct on-screen events, not a single
static image while the voice does all the explanatory work.

## 9. Active V11 coverage and 1930s Brazilian reinvention wave

`canonical-visual-coverage.v11.json` is the current authoritative schedule:
139 contiguous, non-renderable slots over 559.922 seconds, with artifact hash
`ffeb5bc4eb0707cd34e21a74a7fbbc17523de6fd2fdb1319fe355140348df784`.
V11 corrects a missed subject-led inventory in the reinvention sentence. It
creates one action at canonical-121 for **public performances** and three at
canonical-122 for **institutions**, **promotion**, and **nationalism**. The
detector recognizes the governed `helped distinguish` construction and strips
the temporal framing phrase, so it still does not become a noun-per-cut rule.

The immutable V10 artifact is retained as a diagnostic only: its first pass
included the temporal word `when` in the public-performances action. V11 is
the first usable successor and no earlier coverage artifact is a fallback.

The V11 prompt amendment moves the plate world from the Belém research field
to 1930s Brazilian public life—Brazilian neighborhood thresholds, rail
platforms, public halls, civic facades, and local public-identity cues. It
continues to separate world from medium: Combat Woodblock is a crisp rendering
language, not Japanese geography. It also prohibits flags, political claims,
fake documents, blank poster/book/card shorthand, maps, generated text, and
technical grappling choreography.

Wave 032 is the corresponding **quarantined** candidate set. It contains eight
16:9 primary plates for canonical slots 117–124 and four action cut-ins for
the V11 inventory. The contact sheet and its review packet live in
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_visuals/action_assets/wave-032/`.
All twelve candidates are `render_eligible: false` pending a fresh operator
selection. The selected V9 assets for slots 099–116 are carried to the V11
contract only by `canonical-visual-promoted-adoption.v11.json`, which binds
their prior manifest and resolver hashes and remains partial/non-renderable.
