# Living Scene Communication Language

> **STATUS: RECORD.** A point-in-time research note, review, or planning document. Not maintained, and not current doctrine — read it for how a decision was reached, not for what to do now. Live doctrine is indexed in [README.md](README.md).

*Specification of record for P13 living-scene communication and motion.*

## 1. Product decision

P13 does not use a full-video generator as its default renderer. The observed
Higgsfield result cost approximately 600 credits for three minutes—about 3.33
credits per second and roughly 2,000 credits for a unique ten-minute render
before retries.

The production unit is therefore a **living scene bundle**, not a generated
ten-second clip. A living scene combines a stable illustrated world, recurring
characters, props, localized environmental motion, reviewed information
surfaces, and a designed connector to the next scene.

A reusable world is not permission to hold one image across all of its beats.
The timestamped coverage slot owns the primary plate assignment; the world pack
supplies continuity, staging, and reusable layers around it. The scheduling and
prompt contract are owned by
[`17-TIMESTAMPED-PLATE-PRODUCTION.md`](17-TIMESTAMPED-PLATE-PRODUCTION.md).

Higgsfield or another video provider may create a selective hero transition,
character action, or difficult motion asset. It is not responsible for every
second of the episode.

## 2. Five communication surfaces

### Combat Woodblock parent identity

The channel's defining visual language is **Combat Woodblock**: clean graphic
woodblock blocks, deep indigo and sumi ink, muted rust/ochre/teal accents,
thick carved outlines, flat registered color, and recurring sun, wave, cloud,
scroll, route, and circular-medallion motifs. Warm paper is a faint substrate,
not a grainy, distressed, or photographic-noise overlay; crisp silhouette and
calm color fields take priority over texture.

Combat Woodblock has three production packs and one cross-cutting foreground
profile. They are controlled variants of one identity, not unrelated looks:

| Pack | Primary use | Distinguishing rule |
| --- | --- | --- |
| `woodblock-anime-action-v1` | Technique and fight analysis | Strong fighter color ownership, full limb attribution, decisive action silhouettes, and cuts at anticipation/contact/recoil/result |
| `woodblock-historical-editorial-v1` | Historical documentary | Layered period worlds, visibly illustrated reconstruction, local evidence anchors, and environmental rather than plate-driven motion |
| `woodblock-comic-whitespace-v1` | Rapid trending response | One approved anchor subject plus 40–65% paper whitespace for modular headlines, sources, screenshots, comparisons, and icons |
| `combat-woodblock-graphic-silhouette-explainer-v1` | History, culture, and timely explainers | A stable woodblock world plus a filled, grounded 2D silhouette actor or prop that carries one legible action; local editorial surfaces own all facts |

The first History of BJJ series uses the historical-editorial pack. The action
pack does not reactivate automated technique tutorials; it establishes a future
visual grammar for reviewed fight or technique analysis. The whitespace pack is
the rapid-response lane and must not solve urgency by generating filler worlds.

The versioned contract is
`content/video_engine/projects/history-of-bjj/woodblock-style-packs.v1.json`.
Images used to calibrate these rules remain human-study inputs and cannot enter
a renderer until individually reviewed and promoted through `asset_manifest.v1`.

The Graphic Silhouette foreground profile is deliberately versioned separately
at `content/video_engine/projects/history-of-bjj/combat-woodblock-graphic-silhouette-explainer-v1.json`.
It preserves the existing art-pack hashes and can be applied to either the
historical-editorial or comic-whitespace pack without passing external
reference identities or source images to a renderer. Its complete original
prompt, motion, and evidence-surface rules are in
[`18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md`](18-GRAPHIC-SILHOUETTE-WOODBLOCK-EXPLAINER-SPEC.md).

### World

The world establishes place, period, mood, weather, architecture, terrain, and
scale. It may be richly illustrated and interpretive. It cannot supply an exact
date, route, quotation, citation, or historical claim.

World movement is local: rivers run, waterfalls fall, leaves and fabric move,
steam rises, water wheels turn, firelight flickers, and distant silhouettes
cross. The entire world does not drift simply to create motion.

### Character

The recurring fictional learner is the audience's stable point of view.
Historical reconstructions and composites perform only actions supported by the
script's meaning: enter, leave, turn, point, carry, open, hand over, stamp,
react, or walk.

Characters own humor. A reaction or prop gag may challenge a myth or release
tension, but it cannot authenticate evidence or settle a contested claim.

### Evidence

The evidence surface carries exact dates, sourced claims, quotations, archival
excerpts, citation locators, and uncertainty language. It is rendered locally
from approved research and asset IDs.

Generated paper, scrolls, desks, and frames may surround evidence. They never
become the cited evidence themselves.

### Explanation

The explanation surface makes sequence and relationships legible. It owns
reviewed routes, timelines, comparisons, and entity-to-entity verbs. It does
not use extracted keywords as people or infer an edge merely to complete a
diagram.

### Transition

A transition carries meaning between scenes through a shared direction, shape,
object, material, color, or character action. It is planned as the first/last
state of adjacent scenes, not added after assembly as decoration.

## 3. Documentary beat grammar

Every factual passage uses this recurring sequence when applicable:

1. **Picture it** — establish the human situation through world or character.
2. **Name it** — introduce the exact person, place, date, or proposition.
3. **Show the relationship** — make the consequence legible through action or
   explanation.
4. **Qualify it** — show what the evidence can and cannot prove.
5. **Carry it forward** — transform the exit motif into the next scene's entry.

The grammar may span several scenes or compress into one, but the information
ownership does not change.

## 4. Fact surfaces

| Surface | Use | Constraint |
| --- | --- | --- |
| Date seal | Introduce one date and one event | One date only; source-bound |
| Fact folio | State one concise proposition | Short headline plus citation rail |
| Archive proof | Show an approved photograph or excerpt | Rights-reviewed source identity remains visible |
| Journey ribbon | Show reviewed place order and chronology | World art supplies atmosphere, not geography |
| Relationship scroll | Connect named entities with sourced verbs | Unknown or contested edges are labelled, never completed silently |
| Uncertainty card | State the evidence condition | Uses approved claim states such as `record confirms`, `evidence suggests`, `accounts differ`, or `record missing` |

Facts, dates, labels, maps, quotations, and citations are prohibited inside
generated pixels. Generated scene prompts reserve negative space and anchor
regions; Remotion supplies the reviewed information afterward.

## 5. Motion discipline

Motion is authored in this order:

1. Character or prop action.
2. Localized environmental action.
3. Information reveal.
4. Camera action.

A meaningful narration beat must change at least one of the first three layers.
A camera move alone is not a visual event.

Positive-event and deletion-only semantics are owned by
[`16-EDITORIAL-MOTION-SYSTEM.md`](16-EDITORIAL-MOTION-SYSTEM.md#positive-visual-events).

The default camera is locked or uses a restrained push-in. Directional pans,
background translation, handheld motion, and shake require a specific story
reason. Subject motion should occur against a stable world whenever possible.

## 6. Living scene bundle

A normal bundle lasts twenty to thirty seconds and supports two to four
narration beats. It contains:

- a stable master world and optional foreground/depth layers;
- local environmental loops and their masks;
- character and prop slots;
- fact/explanation anchors and safe zones;
- narration, claim, and citation references;
- a micro-event timeline;
- one entry state and one exit state; and
- fallbacks for unavailable motion assets.

Within a bundle, each selected coverage slot still receives its own
timestamp-bound primary plate. The bundle shares a world kit and transition
motif; it does not reuse one full-frame plate as a substitute for changing
story information.

Longer scenes are allowed only while character blocking, facts, props, or
environmental events continue changing meaningfully.

### Google Flow terminology

A Google Flow **character** is a persistent reference bundle. A Google Flow
**scene** in Scenebuilder is a sequence of generated clips in an edit; it is not
a persistent location profile.

This engine therefore defines a **world pack** before it uses Scenebuilder. A
world pack is a provider-neutral set of still/reference demands: a master
establishing composition, clean background, character staging view, prop detail,
fact anchors, entry/exit frames, and localized ambient regions. Approved world
pack assets may later become Flow ingredients, start/end frames, or collection
items. The world pack remains the durable planning unit even when Flow is not
used.

### Catalog and comparison rhythm

Section-title cards, color-coded icon changes, photo-to-diagram swaps, and
direct hard cuts are structural resets. The same title/icon and comparison
layouts recur so the audience compares content instead of relearning the
interface. Flat colors, thick outlines, and a stable camera grammar remain the
default readability system.

Action cuts land at anticipation, contact, recoil, or result. A chapter reuses
one or two transition motifs rather than introducing a different flourish for
every scene. Shape and direction matches are preferred.

## 7. Scene flow

Each adjacency declares at least one connector:

- `direction`: travel continues into a route trace;
- `shape`: a water wheel becomes a circular date seal;
- `material`: river foam becomes torn paper;
- `object`: a ledger opens into an archive excerpt;
- `color`: rust ink becomes a correction stamp; or
- `character`: the learner carries a prop into the next world.

Candidate Episode 1 transitions include:

- battlefield smoke dissolving into quiet dojo steam;
- a river becoming an inked migration route;
- a turning water wheel becoming a document seal; and
- a page turn revealing the next historical period.

## 8. Composition wireframes

### Story world plus narrator

```text
┌──────────────────────────────────────────────────────────────────┐
│ atmospheric world                         local waterfall loop   │
│                                                                  │
│                     historical action                            │
│                                                                  │
│  recurring learner                                               │
│  gesture / reaction             reserved evidence anchor         │
└──────────────────────────────────────────────────────────────────┘
```

### Evidence interruption

```text
┌──────────────────────────────┬───────────────────────────────────┐
│ stable world, dimmed         │ DATE SEAL                        │
│ character holds source  ───▶ │ short approved fact              │
│                              │ citation rail                    │
└──────────────────────────────┴───────────────────────────────────┘
```

### Journey and relationship explanation

```text
┌──────────────────────────────────────────────────────────────────┐
│ interpretive port / river world                                  │
│                                                                  │
│  JAPAN ── taught / travelled / arrived ──▶ BELÉM                 │
│  date        reviewed relationship verb          date            │
│                                                                  │
│ citation rail                            learner follows ribbon   │
└──────────────────────────────────────────────────────────────────┘
```

## 9. Cost control

Until a lower verified quote exists, estimates use 3.33 Higgsfield credits per
second. The first connected-scene proof may use at most thirty paid seconds and
requires separate authorization.

Provider motion should preferably create reusable five- to ten-second actions
or loops. Every call records task identity, estimated and actual credits, reuse
count, and retry reason. Blind variation batches are prohibited.

### Sound

The mix is narration-led. Music remains restrained, UI/card sounds stay subtle,
and impact accents are reserved for an actual demonstrated action or result.
Sound supports the edit's rhythm but does not become a second timing authority
competing with the voiceover.

## 10. Gate rubric

The Communication Language Gate scores each dimension at least 4/5:

- surface ownership is immediately understandable;
- the learner supplies a stable human anchor;
- factual information is legible and distinct from illustration;
- subject/environment motion has priority over camera motion;
- adjacent scenes have a meaningful connector;
- humor cannot be mistaken for evidence; and
- the system appears reusable across the three planned history episodes.

Gate approval selects the language only. It does not approve asset generation,
provider spending, an episode render, or publication.
