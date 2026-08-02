# History Documentary Editorial Specification

*Specification of record for History Documentary V4 editorial behavior.*

## 1. Product

History V4 produces evidence-backed, entertainment-focused documentary explainers:
one approximately 10-minute landscape research master (8–12 minute acceptance
band), two independently planned vertical clips, and chapter-level subvideos per
episode. It does not produce automated technique tutorials.

The initial series is:

1. **How Judo Became Brazilian Jiu-Jitsu** — acceptance pilot.
2. **The Branches BJJ History Forgot** — George Gracie, São Paulo, and Lotus Club
   remain research questions until supported.
3. **How BJJ Became a Global Sport** — Brazil, the United States, competition, and
   Pacific Northwest arrival without academy promotion.

Episode 1 is the only acceptance render in this PRP. Episodes 2 and 3 may have
question briefs, but those briefs are not approved scripts.

## 2. Editorial invariant

Every sentence presented as historical fact resolves to an approved claim in the
current `research_packet.v1`. The transformer may condense, reorder, and qualify
approved claims; it may not add a causal link, date, motive, quotation, or
superlative.

Contested claims require:

- an explicit contested status;
- at least two independent citations;
- narration that signals uncertainty or competing accounts; and
- reviewer approval of the exact framing.

Weak evidence blocks the claim. The system does not silently rewrite the episode
around an unsourced replacement thesis.

## 3. Episode grammar

Each episode follows this documentary rhythm:

1. **Artifact cold open** — a document, date, object, or unresolved question.
2. **Thesis and stakes** — what changed, why the audience should care, and what
   popular simplification the evidence complicates.
3. **Chronological chapters** — each chapter advances time, place, or relationship.
4. **Evidence turn** — show the source category and distinguish record from
   reconstruction.
5. **Complication** — identify a disputed link, missing record, or competing force.
6. **Synthesis** — explain what the evidence supports without collapsing nuance.
7. **Recognition hold** — a stable map, timeline, relationship graph, or document
   that lets the conclusion land.
8. **CTA** — invite viewers to explore the Registry or the next history question;
   do not promote a named academy.

The conflict loop remains useful only when the conflict exists in the evidence.
Manufactured mysteries and inflated certainty are prohibited.

## 4. Visual modes

The current production direction is a **profile fork**, implemented by
`combat-history-longform-cutout-fork-v1`. It is derived from the reviewed,
research-only `longform-illustrated-history-v1` production profile. The earlier
`combat-history-archival-editorial-v1` and
`combat-history-branded-literature-v1` directions remain valid for
snapshotted jobs and revision comparison.

### Production-profile fork

The system may clone a reviewed production profile rather than reducing every
reference to independent abstract atoms. A profile preserves a coherent set of:

- composition and shot-scale grammar;
- limited-animation economics;
- edit cadence and transition patterns;
- visual hierarchy; and
- sound hierarchy.

The Episode 1 baseline is the long-form illustrated-history grammar reviewed
from the supplied `Historically` references. The derived Combat History fork
retains map-to-character transitions, layered cutout tableaux, prop-led acting,
earthy historical fields, economical parallax, and short reaction inserts.

The fork replaces the source identity with original Combat History character
construction, BJJ-specific locations and props, a new palette, local
typography, green evidence rails, red correction stamps, numbered folios, and
archive/citation proof blocks. The source profile itself remains
`render_eligible: false`; its videos, frames, maps, character designs, logos,
scripts, jokes, and exact visual assets cannot resolve into a render.

The resulting branded literature combines a recognizable entertainment voice with the
discipline of a cited essay:

1. **Low-fi comedy block.** Purposefully rough 2D drawings, limited frames,
   deadpan labels, imperfect perspective, and recurring visual gags. Comedy
   interprets a misconception or situation; it is never evidence and is not
   used to make a contested claim feel settled.
2. **Historical comic block.** Limited-palette sequential panels turn an
   approved historical statement into a clearly labeled illustration. Panels
   may compress time and space but may not invent a person, event, quotation,
   or causal link.
3. **Historical evidence block.** Rights-reviewed photographs, documents,
   dates, quotations, and citations receive restrained motion and clear source
   treatment. This mode proves or qualifies the factual proposition.

The preferred recurring rhythms are:

- `comic aside → historical comic → archive proof`; and
- `popular simplification → illustrated complication → sourced conclusion`.

No more than two adjacent beats should use the same mode. Humor and comic
reconstruction must resolve into an evidence block whenever the sequence makes
a historical proposition.

| Period / purpose | Visual mode |
|---|---|
| Early Japan and Brazil | warm paper, restrained ink, woodblock-inspired geometry, visibly illustrated reconstruction |
| Mid-century Brazil | editorial print texture, document panels, limited-color illustration |
| Modern/global | clean flat graphics, maps, data, lineage, and brief Combat Science diagrams |

Required composition vocabulary:

1. Artifact cold open
2. Archival portrait with parallax
3. Stylized illustrated reconstruction
4. Document or quotation close-up
5. Migration map and timeline
6. Lineage or relationship graph
7. Concept-mechanics cutaway
8. Chapter or CTA card

No History V4 storyboard may contain `StickFigureScene`, raw skeletal bodies, or
generated multi-person grappling choreography. Concept mechanics may consume no
more than 15% of total runtime and must explain an idea, not teach a sequence.

## 5. Editorial motion ownership

- Remotion owns editorial assembly, captions, citation overlays, archive parallax,
  transitions, credits, and output compositions.
- Manim owns maps, timelines, relationship graphs, and concept diagrams.
- Documentary treatments reference approved asset IDs only.
- Documentary illustration carries a visible `Illustration` or `Reconstruction`
  label whenever it could be mistaken for evidence.

Motion must reveal meaning: a map line follows travel, a timeline establishes
sequence, a graph reveals a relationship, and a document crop lands on the cited
passage. Decorative camera movement does not substitute for an editorial beat.

### World first, vectors second

Fast local vectors are an annotation language, not a sufficient environment.
Historical-comic generation, rights-reviewed archives, or original layered
illustrations establish place, period, atmosphere, foreground, and depth.
Deterministic vectors then add the exact route, date, citation, highlight,
relationship verb, measurement, correction, or comedic annotation.

For document and map compositions, generated imagery is background-only. A
generated archive desk may surround a deterministic excerpt card, but it cannot
become the cited document. A generated travel world may support a deterministic
route overlay, but it cannot supply geography, dates, or location labels. The
world may be interpretive; the explanation layer must remain exact.

### V4.1 living-editorial cadence

`editorial_coverage.v1` resolves visual coverage before treatments:

- every complete sentence receives at least one distinct visual concept;
- long sentences split only at contrast or meaningful clause boundaries;
- a visual event occurs every 1.5–3 seconds;
- major shots target 3–6 seconds and may extend to 8 seconds only with multiple
  meaningful reveals;
- repeated or already-visible nouns never create cuts by themselves; and
- adjacent beats may not repeat the same asset, composition, crop, and motion
  recipe.

What qualifies as a visual event—including the prohibition on deletion-only
beats—is defined once in
[`16-EDITORIAL-MOTION-SYSTEM.md`](16-EDITORIAL-MOTION-SYSTEM.md#positive-visual-events).

The approved recipes are `parallax_push`, `detail_punch`, `masked_reveal`,
`evidence_highlight`, `map_trace`, `comic_pop`, `split_compare`, `type_build`,
and `paper_transition`. Storyboard 2.3 stores these as narration-safe visual
beats inside the original scene; extra cuts never repeat the voiceover.

Stock discovery is template-routed, not keyword-rotated. Each eligible beat
first resolves to one finite visual archetype:

| Archetype | Provider discovery | Required treatment |
|---|---|---|
| `historical_martial_archive` | Stock photo | Both a judo/jujutsu/Kodokan subject and a historical, archival, vintage, black-and-white, or early-20th-century facet |
| `martial_arts_broll` | Stock photo | Judo, jujutsu, dojo, tatami, grappling, or another explicit martial-arts match |
| `historical_travel_broll` | Stock photo | Ship, port, voyage, route, or named Japan/Brazil location |
| `period_comic_block` | Stock vector | Both a historical/martial subject and a comic, halftone, woodblock, ukiyo-e, or vintage style facet |
| `lofi_stick_figure_comic` | Stock vector | Both a rough comic/doodle facet and a martial/explanatory subject |
| `distance_map` | Local deterministic render | Named places, chronology, and claim-bound route data |
| `entity_graph` | Local deterministic render | Named entities and typed, cited relationships |
| `document_evidence` | Local deterministic render | Claim-bound excerpt and locator |
| `archive_portrait` | Approved local archive | Exact approved person asset |
| `chapter_card` | Local typography | Chapter thesis or CTA only |

Search queries use named people, places, dates, actions, and period/media terms.
Abstract grammatical words such as “date,” “older,” “mean,” “changed,” or
“starting point” are never discovery concepts. A candidate must match every
required archetype facet in its title or catalog metadata, must pass the
category-mismatch blocklist, and is ranked before its preview is downloaded.
If no catalog result passes, the slot uses its deterministic local fallback;
the engine does not lower the threshold merely to fill the contact sheet.

Relationship diagrams are allowed only when the input identifies at least two
named historical entities and a typed relationship supported by the current
claim/citation set. Extracted keywords, grammatical filler, and inferred edges
are prohibited. If the relationship cannot be resolved, the renderer must use a
comic, archive, document, map, or typography block instead of fabricating a
graph.

## 6. Narration and citation behavior

Narration should be precise, conversational, and explicit about uncertainty.
Avoid institutional voice, mythic filler, and false omniscience.

- Paraphrases receive a compact source marker and full credit entry.
- Direct quotations require a verified locator and quotation fidelity check.
- On-screen citations must be readable at the target aspect ratio and must not
  occupy caption or platform-control safe zones.
- Citations point to research records. They never resolve an image.
- Illustrations and reconstructions are never cited as proof.

Existing custom ElevenLabs or operator-recorded narration remains the audio path.
No stock consultant voice is selected. A new paid synthesis remains a separately
authorized action even after editorial gates are approved.

## 7. Human gates

### Research Gate

The operator reviews thesis clarity, source quality, contested framing, claim
completeness, promotional neutrality, and rights readiness. Each dimension must
score at least 4/5 against the current research hash.

### Visual Direction Gate

The style board contains cold open, archive, illustration, document, map/timeline,
and lineage/concept frames. The current art, asset, and treatment hashes must
match. Each dimension—originality, hierarchy, asset integration, typography,
citation legibility, and audience clarity—must score at least 4/5.

The gate may display hash-bound AI-assisted illustration candidates for the
`cold_open`, `illustration`, or `map_timeline` roles. Generated plates must be
visibly labeled, carry no factual text, and remain both `evidence_eligible:
false` and `render_eligible: false` while under review. Archive portraits,
documents, citations, named relationships, and map facts are never replaced by
generated evidence. Promotion after approval follows the generated-asset rules
in [11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md](11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md).

### Gate A

Gate A reviews motion, story comprehension, pacing, narration fit, transition
logic, and the accuracy of visualized relationships. It does not retroactively
approve research or asset rights.

### Gate B

Gate B reviews the landscape master, both native vertical clips, captions,
citations, credits, disclosure labels, and packaging. Passing QC is necessary but
does not grant publication approval.

## 8. Native verticals

Vertical clips are authored from an approved claim cluster, not cropped from the
landscape master. Each clip has its own hook, layout, citation placement, and
recognition frame. A clip preserves all qualifications needed to keep the claim
accurate outside the episode’s context.

## 9. Chapter subvideos

Each chapter may become a landscape or vertical subvideo only when it has a
self-contained question, approved claim cluster, hook, conclusion, and citation
set. Subvideos inherit the exact research and asset hashes of the master. They are
re-authored packages, not blind timeline cuts, and may not omit a qualification
that changes the meaning of a contested claim.

The 8–12 minute band is an evidence budget rather than a quota. Repetition,
generic context, or slower delivery cannot be used to reach it.

### World-first generated plates for documentary explanation

The map, lineage, and concept functions use a hybrid composition when a
reviewed generated candidate is available. GPT image generation or an approved
Nano Banana/Magnific still producer supplies an original, unlabeled woodblock
world plate. It may establish paper, ink, ports, ships, blank medallions,
silhouettes, and depth. It may not supply names, dates, routes, relationship
verbs, quotations, or factual document text.

Remotion then adds the meaning-bearing layer from the approved episode:

- `migration_map_timeline`: reviewed place labels, route order, dates, and a
  citation rail over the generated travel world;
- `lineage_graph`: a generated lineage scroll with named entities and sourced
  relationship verbs placed into blank medallions; unresolved edges become
  explicitly labelled research questions rather than invented arrows; and
- `concept_mechanics_cutaway`: a generated visual metaphor (for example a
  lever, bridge, or layered scene) with a short reviewed concept caption, not a
  multi-step technique tutorial.

The renderer records `motion_selected` and the generated batch hash in a
revision-only animatic packet. The candidate remains preview-only and is never
promoted to the rights-cleared asset manifest without a separate operator
decision. This is the preferred quality path for V4.1 because the producer
handles visual world-building while the local editor retains factual control.

### One generated plate per narration block

When a documentary beat needs a fully authored world, V4.1 may compile
`generated_image_block_plan.v1` from editorial coverage. The compiler groups
continuation slots by their complete narration excerpt: every unique sentence
or meaningful clause receives one distinct generated plate, while repeated
continuations reuse that plate. This is a semantic cadence rule, not a
literal noun-per-cut rule.

The Episode 1 proof contains 138 coverage slots and 71 unique generated blocks.
Each block prompt requests an original, text-free Japanese woodblock-informed
editorial plate and explicitly keeps facts, captions, citations, dates, maps,
logos, and quotations out of the pixels. `generated_image_block_batch.v1`
binds every plate to its coverage slots and a local SHA-256. The validator
rejects missing files, unsafe paths, stale hashes, duplicated slots, provider
source leakage, and any `render_eligible` or `evidence_eligible` promotion.

The generated-block style board and animatic are review-only revisions. They
are parked at Visual Direction until a human approves the new contact sheet;
the active board, Gate A snapshot, research packet, and rights-cleared asset
manifest remain unchanged.

### Plate-to-video motion handoff

The generated plate is now the input to an optional image-to-video producer,
not a canvas for a generic editor zoom. `plate_motion_plan.v1` creates one
silent clip request per generated block. The request carries the block's
narration excerpt as direction, a single action recipe (`route_trace`,
`branch_reveal`, `page_turn_or_highlight`, and similar), and explicit negative
constraints for camera shake, background wobble, new characters, costume drift,
and generated text.

Provider clips remain quarantined. A completed Magnific/Kling manifest must be
content-addressed, job-local, and `render_eligible: false` before the animatic
can consume it. Remotion overlays the same reviewed captions and citation rail
over the moving clip; it does not ask the provider to render facts or
narration. If no motion manifest exists, the previous deterministic renderer
remains the fallback, but it is explicitly reported as
`motion_mode: deterministic_fallback`.
