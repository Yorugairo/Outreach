---
id: P13-LIVING-SCENE-COMMUNICATION-SYSTEM
title: P13 Living Scene and Communication System
status: running
operation: feature
risk: external-provider
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-31
updated: 2026-08-02
---

# P13 Living Scene and Communication System

## Summary

Reset P13 around a reusable visual communication language rather than a
full-video generator. The empirical Higgsfield result—approximately 600 credits
for three minutes—makes per-block provider generation economically unsuitable
as the default ten-minute production path.

The new system builds connected living scenes. Each scene has a stable,
high-quality illustrated world; character- or prop-led action; small localized
environmental loops; deterministic fact surfaces; and an entry/exit motif that
connects it to the next scene. Whole-background motion and generic plate pans
are de-emphasized.

Higgsfield remains available for selective hero moments and reusable character
motion assets, not the entire runtime. GPT Image 2 and other approved still
producers remain suitable for characters, locations, props, scene plates, and
style development. ElevenLabs remains the canonical narrator.

Before another episode is assembled, the system must define how it communicates
story, evidence, explanation, humor, and uncertainty.

## Intent And Acceptance

The intent is to make every production decision answer one of two questions:

1. What is the audience supposed to feel or picture?
2. What exact fact, relationship, date, or qualification must they understand?

Acceptance requires:

- Existing Armbar, documentary, Flow, Magnific, and Higgsfield outputs are
  preserved as R&D and excluded from new production unless explicitly promoted.
- One `communication_grammar.v1` defines the world, character, evidence,
  explanation, and transition surfaces and when each may carry meaning.
- One `creative_asset_map.v1` inventories selected and demanded style keys,
  characters, locations, props, archives, ambient loops, fact surfaces, and
  transition motifs.
- One `scene_bundle.v1` packages a scene's master world, depth layers,
  character slots, prop slots, ambient loops, fact anchors, narration beats,
  entry state, and exit state.
- One `scene_flow_graph.v1` proves that adjacent scenes connect through an
  intentional visual or motion motif rather than unrelated hard cuts.
- Factual text is never entrusted to generated pixels. Dates, claims,
  quotations, relationship verbs, maps, and citations resolve through reviewed
  editorial surfaces.
- Motion follows a strict priority: character/prop action, localized ambient
  motion, information reveal, then camera movement.
- A ten-minute episode can be planned as approximately twenty to thirty living
  scene bundles with two to four narration beats each. Bundles reuse world kits
  and continuity layers, while timestamped coverage slots receive distinct
  primary plates rather than collapsing the runtime into provider clips or one
  static plate per bundle.
- A bounded multi-scene proof demonstrates character continuity, ambient life,
  fact communication, and a designed scene-to-scene transition before full
  Episode 1 production resumes.
- Provider cost estimates use the observed Higgsfield rate until a cheaper live
  quote is verified and block execution fails closed at its approved ceiling.

## Scope

- P13 History of BJJ long-form episodes and their reusable visual language.
- Durable communication, scene-bundle, scene-flow, asset-map, motion-test, and
  provider-cost contracts.
- An asset demand map covering the three planned History of BJJ episodes.
- One recurring fictional on-screen narrator/learner and only the historical
  reconstructions demanded by approved scripts.
- High-quality still generation for worlds, characters, props, and reference
  assets.
- Character cutouts, reusable character-action loops, localized environmental
  loops, deterministic information overlays, and selective provider animation.
- Remotion as the final compositing, narration, caption, citation, and credits
  layer.
- Existing archival rights, historical claims, likeness, and human-gate rules.

## Not Building

- No complete episode, sixty-clip provider batch, publication, registry write,
  commit, or push.
- No default rule that generates one video for every ten-second block.
- No un-timestamped image-per-sentence rule or generic ten-second grouping.
  Primary imagery is scheduled from semantic coverage slots, normally about
  two to six seconds, with one plate assignment per slot.
- No generic pan-and-zoom treatment used merely to claim that a scene moves.
- No whole-background directional drift while the actual subject remains inert.
- No generated factual text, dates, maps, quotations, citations, or relationship
  claims.
- No multi-person technique choreography or stick-figure technique tutorial.
- No speculative characters, worlds, or props without near-term episode demand.
- No training, creator cloning, source-frame copying, or “in the style of”
  prompts.
- No automatic asset or provider-output promotion.

## Human Gates

1. **Reset Gate** — approve this PRP and the freeze of current episode assembly.
2. **Communication Language Gate** — approve the five surfaces, fact treatments,
   humor behavior, motion hierarchy, and representative wireframes.
3. **Asset Demand Gate** — approve the first-three-episode character, world,
   prop, ambient-loop, and transition inventory before generation.
4. **Asset Foundation Gate** — approve generated/reused assets and their
   readiness classifications.
5. **Living Scene Proof Gate** — approve the bounded connected-scene proof.
6. **Episode Production Gate** — separately approve Episode 1 production and
   any provider spending ceiling.

No paid provider call, likeness promotion, or episode-scale generation is
authorized by approving the planning document alone.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `docs/content-video-engine/10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md`
- `docs/content-video-engine/11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md`
- `docs/content-video-engine/12-HIGGSFIELD-EXPLAINER-LEARNINGS.md`
- `docs/content-video-engine/14-HIGGSFIELD-AUDIO-DRIVEN-LANE.md`
- `content/video_engine/projects/history-of-bjj/episode-1-flow-character-pack.json`
- `content/video_engine/projects/history-of-bjj/episode-1-asset-manifest.json`
- `content/video_engine/src/services/asset_resolver.py`
- `content/video_engine/src/services/producer_orchestration.py`
- `content/video_engine/src/services/higgsfield_explainer.py`
- `.agents/skills/higgsfield-video-explainer/SKILL.md`

## Execution Path

```text
freeze current production attempts as R&D
→ define the communication language
→ map Episode 1–3 asset demand
→ select one style key
→ establish recurring cast and world kits
→ create props, ambient loops, and fact surfaces
→ compile connected scene bundles
→ validate the scene-flow graph
→ build a bounded living-scene proof
→ human review
→ future Episode 1 production PRP
```

### Communication language

The system uses five surfaces. A beat may combine them, but the ownership of
meaning remains explicit.

| Surface | Audience function | Carries | Must not carry |
| --- | --- | --- | --- |
| **World** | place, period, mood, scale | architecture, terrain, weather, atmosphere, background activity | factual text, exact routes, dates, citations |
| **Character** | attention, empathy, humor, action | gesture, reaction, travel, object handling, conflict, point of view | unsourced historical claims or speaking/lip-sync generated by the provider |
| **Evidence** | credibility and precision | exact date, short claim, quotation, archival excerpt, citation, uncertainty status | invented paper texture presented as a real document |
| **Explanation** | relationships and causality | reviewed map route, timeline, entity/verb graph, comparison, sequence | decorative keyword graphs or generated geography |
| **Transition** | continuity between ideas | shared shape, direction, object, material, color, or motion | an unrelated effect that does not advance meaning |

### Documentary beat grammar

Every factual passage should resolve through a compact recurring grammar:

1. **Picture it** — a world or character establishes the human situation.
2. **Name it** — the evidence surface introduces the person, place, date, or
   proposition.
3. **Show the relationship** — character action or an explanation surface makes
   the consequence legible.
4. **Qualify it** — an archive, citation rail, correction stamp, or uncertainty
   card states what the evidence can and cannot prove.
5. **Carry it forward** — the scene's exit motif becomes the next scene's entry
   motif.

Humor belongs primarily to the fictional narrator/learner and prop behavior.
It may challenge a myth or release tension, but it never appears to authenticate
or settle a contested claim.

### Fact surfaces

The initial language uses six consistent information treatments:

1. **Date seal** — one date and one short event label.
2. **Fact folio** — one claim in a short headline plus a compact citation rail.
3. **Archive proof** — a rights-reviewed image or excerpt with source identity.
4. **Journey ribbon** — reviewed places, direction, and dates over an
   interpretive world.
5. **Relationship scroll** — named entities joined by sourced verbs; missing or
   contested edges are visibly marked.
6. **Uncertainty card** — “record confirms,” “evidence suggests,” “accounts
   differ,” or “record missing,” bound to the claim state.

Generated worlds reserve clean negative-space anchors for these surfaces. The
information is rendered locally after the generated imagery has been approved.

### Motion hierarchy

Motion is authored in this order:

1. **Character or prop:** enter, exit, turn, point, look, carry, open, stamp,
   hand over, react, or walk.
2. **Localized environment:** waterfall, river, leaves, fabric, steam, smoke,
   rain, firelight, lantern, mill wheel, paper dust, or crowd silhouette.
3. **Information reveal:** date seal, evidence highlight, route trace,
   relationship branch, archival crop, or correction stamp.
4. **Camera:** locked frame or restrained push-in by default. Directional pan,
   handheld motion, or whole-plate drift requires a specific narrative reason.

At least one of the first three layers must change within each meaningful
narration beat. Camera motion alone does not satisfy the rule.

### Living scene bundles

A scene bundle normally spans twenty to thirty seconds and supports two to four
narration beats. It may run longer only when its world, character blocking,
facts, and micro-events continue changing meaningfully.

Each bundle contains:

- a stable master world and optional depth-separated foreground;
- zero or more localized ambient loops with explicit masks;
- approved character slots and continuity references;
- approved props and interaction states;
- fact/explanation anchor rectangles and safe zones;
- narration, claim, and citation references;
- one entry state and one exit state;
- reusable character actions and scene-specific actions;
- a shot/micro-event timeline; and
- fallback behavior when a motion asset is unavailable.

### Scene-flow graph

Adjacent bundles must share at least one deliberate connector:

- motion direction, such as ship travel continuing into a route trace;
- shape, such as a water wheel becoming a date seal;
- material, such as river foam becoming torn paper;
- object, such as a ledger opening into an archive excerpt;
- color, such as rust ink becoming a correction stamp; or
- character action, such as the learner carrying an object into the next world.

Examples for the pilot include battlefield smoke dissolving into quiet dojo
steam, a river becoming an inked migration route, a rotating water mill becoming
a document seal, and a page turn revealing the next historical period.

## Patterns To Mirror

- `asset_manifest.v1` path containment, immutable hashing, rights, likeness,
  alteration, and attribution rules.
- `flow_character_pack.v1` candidate/promotion boundary, generalized beyond
  Google Flow.
- `editorial_coverage.v1` claim/citation linkage, extended by a timestamped
  plate plan that binds each selected slot to a distinct primary plate while
  retaining reusable world-kit continuity.
- `higgsfield_audio_job.v1` task-ID resume and duplicate prevention for the few
  provider clips still used.
- Existing Remotion caption, citation, credit, safe-zone, and audio ownership.
- Service-layer validation: compilers produce immutable artifacts; renderers
  consume only validated asset IDs and never search job folders by filename.

## Cost And Provider Policy

Until a new live quote is verified, planning uses the observed cost:

```text
600 Higgsfield credits / 180 seconds = approximately 3.33 credits per second
```

At that rate, ten minutes of unique provider motion would be approximately
2,000 credits before retries. Therefore:

- Higgsfield is not the default full-runtime renderer.
- The first living-scene proof may include no more than thirty seconds of paid
  provider motion and requires a separate ceiling.
- Prefer generating reusable five- to ten-second character actions or hero
  transitions that can appear more than once.
- Ambient loops should be generated once, isolated, and reused where visually
  appropriate.
- A provider retry is allowed only after a recorded failure diagnosis; blind
  variation batches are prohibited.
- Every provider plan records estimated credits, worst-case retry cost, reuse
  count, and effective cost per episode minute.

## Recommended Initial Asset Ceiling

This is a cost ceiling, not a generation quota. The Asset Demand Gate may
reduce it.

| Class | Initial ceiling | Readiness requirement |
| --- | ---: | --- |
| Selected style key | 1 from up to 3 candidates | passes wide, close, character, prop, and information-anchor stress tests |
| Recurring narrator | 1 | stable identity plus six reusable actions or poses |
| Historical/composite characters | 3 | stable required views plus one demanded interaction each |
| Reusable world kits | 6 | stable master plate, character staging, fact anchors, optional ambient regions |
| Props | 10 | isolated reference plus named character/world uses |
| Ambient loops | 8 | localized mask, clean loop, no camera movement |
| Fact surfaces | 6 | deterministic template, safe zones, citation behavior |
| Transition motifs | 8 | compatible entry and exit states with at least one planned use |

Likely Episode 1 candidates remain the Registry Learner, Kano reconstruction,
Maeda reconstruction, and Brazilian bridge composite. Likely worlds include the
battlefield myth, Kodokan/institution, archive desk, steamship/global circuit,
Belém port, and early Brazilian training/social space. The demand map—not this
list—decides what is actually built.

## Task Slices

### T1: Freeze and inventory P13 R&D
- Status: completed
- Owner: parent
- Depends on: Reset Gate
- Write set: `.context/p13-living-scenes/`, this PRP
- Acceptance: existing media and manifests are classified by path, hash, dimensions, provenance, manifest membership, observed quality, and reuse status; nothing is deleted or overwritten.
- Validate: `python -m content.video_engine.cli validate-creative-inventory .context/p13-living-scenes/inventory.json`
- Evidence: `.context/p13-living-scenes/inventory.json`; 1,563 media artifacts, 10 `approved_reusable`, 1,553 `reference_only`; artifact hash `942000741554784f1367d76e8485cfce2033fff74581fb6a03b88aaf8a6c97a9`.

### T2: Specify the communication language
- Status: completed
- Owner: parent
- Depends on: T1
- Write set: `docs/content-video-engine/15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md`, `content/video_engine/configs/communication_grammar.schema.json`, templates, focused tests
- Acceptance: the five surfaces, documentary beat grammar, fact treatments, humor rules, motion hierarchy, and representative layouts are versioned and validated.
- Validate: `python -m pytest content/video_engine/tests/test_communication_grammar.py -q`
- Evidence: `docs/content-video-engine/15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md`, `content/video_engine/projects/history-of-bjj/communication-grammar.v1.json`, `.context/p13-living-scenes/communication-language-board.png`; grammar hash `d1611cade9359c366f5e4964a179d7dd5cb2d848f0c2a8ab212094368d50221d`; the approved Reference Pack subset is encoded in visual, transition, and sound policies; focused contract verdict `12 passed` after style-pack expansion.

### T3: Add asset, scene-bundle, and scene-flow contracts
- Status: completed
- Owner: parent
- Depends on: T2
- Write set: `content/video_engine/configs/style_pack_library.schema.json`, `content/video_engine/configs/creative_asset_map.schema.json`, `content/video_engine/configs/world_pack.schema.json`, `content/video_engine/configs/scene_bundle.schema.json`, `content/video_engine/configs/scene_flow_graph.schema.json`, templates, `content/video_engine/src/services/living_scenes.py`, `content/video_engine/cli.py`, focused tests
- Acceptance: immutable validators cover parent style and pack selection, assets, dependencies, readiness, world layers, character/prop slots, fact anchors, ambient masks, micro-events, entry/exit states, and transition compatibility.
- Validate: `python -m pytest content/video_engine/tests/test_living_scene_contracts.py -q`
- Evidence: `style_pack_library.v1`, `creative_asset_map.v1`, `world_pack_library.v1`, `scene_bundle.v1`, and `scene_flow_graph.v1` schemas; fail-closed validators and five CLI validation commands; focused contract suite included in `12 passed`.

### T4: Compile the three-episode asset and scene demand map
- Status: completed
- Owner: parent
- Depends on: T3
- Write set: `content/video_engine/projects/history-of-bjj/series-asset-demand.json`, `content/video_engine/projects/history-of-bjj/world-packs.v1.json`, `content/video_engine/projects/history-of-bjj/series-scene-demand.json`, job-local review artifacts
- Acceptance: every demanded character, world, prop, loop, fact treatment, and transition traces to planned narration/claims and records recurrence, priority, reuse horizon, and fallback.
- Validate: `validate-asset-map`, `validate-world-packs`, and `validate-scene-flow`
- Evidence: one Combat Woodblock parent identity and three production variants (`e3ee2b98b5ffaf767903dee3719b44d7b751eefe2fc4977ba4fdbe0865e0dfd7`), an immutable 81-image calibration inventory (`807d5abf89436167f51679f0bd5e0e51e3a10b3fe18a93c399346fde068cab4e`), 49 asset demands (`67105651a451316ce065810e83e12a1f7c3c7047ad56795297e9382afc890304`), six historical-editorial world packs (`8488b9982566377608665145200e1c701a43c8f1d733884860ac278b17bf142a`), and twelve foundation scene families with nine explicit adjacencies (`62800d1e613b410f02fddd28149cedb533509aed67adff41dba731d130a4c2d9`). Episode 2–3 historical demand remains `question_only` and research-blocked where generation would imply a claim or likeness.

### T5: Create communication-language review boards
- Status: completed
- Owner: parent
- Depends on: T4
- Write set: job-local review boards and rubric only
- Acceptance: representative frames show world, character, evidence, explanation, and transition surfaces in isolation and combination; factual information remains locally rendered.
- Validate: contact-sheet completeness and rubric validation
- Evidence: `.context/p13-living-scenes/communication-language-board.png`, `.context/p13-living-scenes/COMMUNICATION-LANGUAGE-REVIEW.md`, and `.context/p13-living-scenes/ASSET-DEMAND-REVIEW.md`. The operator approved the Communication Language Gate and approved the revised Asset Demand Gate on 2026-08-01.

### T6: Establish the minimum character, world, and prop foundation
- Status: completed
- Owner: parent
- Depends on: Communication Language Gate and Asset Demand Gate
- Write set: job-local provider quarantine, project asset directories, manifests
- Acceptance: only approved demanded assets are generated or promoted; characters, worlds, props, fact anchors, and ambient regions pass identity, composition, rights, and hash checks.
- Validate: asset contact sheets, hash validation, rights/likeness validation, `validate-asset-map`
- Evidence: the preserved pre-promotion `asset_foundation_review.v1` contract
  `0a01e1f5bfdbddb3ac0a32345099c4954601ee52926ee1ae7019daca662c4129`,
  `.context/p13-living-scenes/asset-foundation-contact-sheet.png`, and
  `.context/p13-living-scenes/ASSET-FOUNDATION-REVIEW.md`. After the operator
  clarified that still generation is effectively free, the slice generated five
  world masters, one scene plate, four transparent motion sheets, sixteen cast
  sprites, and ten prop sprites through the Codex built-in path. The operator
  approved the Asset Foundation Gate on 2026-08-01. The 20 approved foundation
  masters plus 16 locally derived cast sprites were promoted without altering
  their quarantined inputs into
  `content/video_engine/projects/history-of-bjj/episode-1-asset-manifest.v2.json`
  (`5f70e8039ae303269d354ec35d89b08627dcb62babfe96ef070266df91d6fd9c`),
  and `episode-1.json` now pins that exact manifest. `validate-assets` and
  `validate-history` pass. Animation and voice calls remain separately
  unauthorized.

### T7: Prove the deterministic editorial motion system
- Status: completed
- Owner: parent
- Depends on: T6 and approval of `P13-EDITORIAL-MOTION-SYSTEM.plan.md`
- Write set: governed by `.claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md`
- Acceptance: a 30–60 second zero-provider-call A/B proof demonstrates intentional shot hierarchy, stable focal-point motion, meaningful stillness, deterministic fact surfaces, motivated cuts, and unchanged Gate A artifacts; the Editorial Motion Proof Gate records a decision.
- Validate: exact commands and review evidence in the child PRP
- Evidence: `.claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md` is implemented and validated. The 40.716-second, eleven-shot zero-provider A/B proof, diagnostic render, cut samples, contact sheets, and review packet are under `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v9/`. Structural QC passes and Gate A hashes are unchanged. The operator approved the current V9 proof on 2026-08-01; `editorial-motion-proof-gate.json` records that decision. No paid motion authorization is implied.

### T8: Classify and optionally build reusable organic motion assets
- Status: completed
- Owner: parent
- Depends on: T7 and separate provider authorization when paid generation is used
- Write set: job-local provider quarantine, motion manifests, focused tests
- Acceptance: every shot is classified `none`, `preferred`, or `required`; only authorized preferred/required character actions or localized ambient loops are generated; accepted assets are camera-stable, identity-stable, loopable where declared, cost-recorded, and non-renderable until approved. A zero-call result is valid when local layers satisfy the plan.
- Validate: task IDs, media hashes, duration/loop checks, alpha or mask checks, cost ledger, human contact sheet
- Evidence: the approved V9 `editorial_motion_plan.v1`
  (`87151d121ae8b90a96b35d0bdf627fb35712d1fb6da749f3503339b96781e986`)
  classifies ten proof shots as `none` and one maritime shot as `preferred`,
  with a local-layer fallback. The zero-call classification is valid for this
  bounded proof:
  local character blocking, discrete prop actions, and localized ambient
  actions take precedence over camera motion. No provider task was requested,
  created, or promoted; future `preferred` or `required` classifications remain
  subject to the separate Provider Motion Spend Gate.

### T9: Compile connected living scenes
- Status: completed
- Owner: parent
- Depends on: T6, T7, and T8
- Write set: `content/video_engine/src/services/living_scenes.py`, Remotion editor contracts/components, focused tests, job-local scene bundles
- Acceptance: scenes assemble from validated IDs only; character/prop action and localized ambient motion precede camera movement; fact surfaces resolve reviewed data; every adjacency passes the flow graph.
- Validate: focused Python tests, Remotion typecheck/build, low-resolution fixture renders
- Evidence: V10 replaces the last V9 scene-contract references with validated,
  revision-local `scene_bundle.v1` records and a `scene_flow_graph.v1` that
  bind only promoted V2 asset IDs. The two connected families are
  `myth-to-institution`
  (`fccbf02cb39db1de5300ac175c52117e769cdb8f3b8ef562d8e04ced67475ed3`)
  and `system-as-record`
  (`193e32b4fece8ce6964ef6cbeee66fc9efd6abcf6721d91a7a7dd40681a15f1c`),
  joined by `record-paper` in
  `scene-flow.json`
  (`300e2e13295e1479fa2288673a643fcb20bb4942c65849f8c7a63d951cb52f86`).
  The compiled eleven-shot plan is
  `bd110a2ae29326373af5c3657f33edfdb08984847a7a86dc99b80c23ae1d9b19`.
  Motion is character/prop or localized environmental action before any
  restrained camera movement; no scene shifts an entire background plate.
  Focused contract/QC/animatic tests passed `61 passed in 0.76s`; Remotion
  typecheck and build both passed.

### T10: Produce the bounded living-scene proof
- Status: in_progress
- Owner: parent
- Depends on: T9 and Asset Foundation Gate
- Write set: job-local proof artifacts only
- Acceptance: a short connected sequence demonstrates at least three worlds, the recurring narrator, one historical character, two fact surfaces, two ambient loops, and two meaningful transitions. Paid provider motion remains within the approved ceiling.
- Validate: QC report, cost ledger, contact sheet, audio/video inspection, no stale or superseded asset paths
- Evidence: the local V10 proof is rendered at
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v10-living-foundation/revised-preview.mp4`.
  Its revision packet records `provider_calls: 0`, `cost_usd: 0.0`, structural
  QC `pass`, and the immutable V2 asset-map hash
  `5f70e8039ae303269d354ec35d89b08627dcb62babfe96ef070266df91d6fd9c`.
  The 40.716-second sequence contains four promoted worlds, the recurring
  learner, Kano as the historical character, the direct 1882 scroll and the
  archival Kano portrait as the two evidence surfaces, localized
  smoke/light/paper/water/sky loops, and hard/match transitions. There are no
  on-screen transcript, citation, generic book, or label-card overlays. Frame
  inspection confirmed the date is centered on the scroll rather than Kano's
  face and the maritime subject/ship-wake treatment does not move the plate.
  It is awaiting the Living Scene Proof Gate; no final Episode 1 production
  decision is implied.

### T11: Close foundation and hand off Episode 1 production
- Status: pending
- Owner: parent
- Depends on: Living Scene Proof Gate
- Write set: this PRP, `docs/content-video-engine/README.md`, asset-readiness and production-handoff reports
- Acceptance: the handoff names the approved communication grammar, asset base, scene bundles, transition plan, measured cost, gaps, and exact Episode 1 production boundary.
- Validate: PRP validation and full verification below
- Evidence: pending

## Verification

Before this foundation can be marked complete:

```powershell
python -m pytest content/video_engine/tests/test_communication_grammar.py -q
python -m pytest content/video_engine/tests/test_living_scene_contracts.py -q
python -m content.video_engine.cli validate-style-packs content/video_engine/projects/history-of-bjj/woodblock-style-packs.v1.json --calibration-inventory .context/p13-living-scenes/woodblock-calibration-inventory.json --asset-map content/video_engine/projects/history-of-bjj/series-asset-demand.json
python -m pytest content/video_engine/tests -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run build
python -m pytest -q
python scripts/prp_validate.py .claude/PRPs/plans/P13-LIVING-SCENE-COMMUNICATION-SYSTEM.plan.md
```

Also verify:

- every promoted asset exists locally and matches its declared SHA-256;
- no renderer or assembler selects media by filename pattern or folder order;
- generated pixels contain no factual text used by the episode;
- every fact surface resolves approved claim/citation data;
- every scene adjacency has a valid transition connector;
- every paid provider task has a stable task ID and cost entry;
- no automated test performs a paid provider call;
- current P13 R&D artifacts remain present and unchanged.

## Evidence And Handoff

Planning evidence:

- The user's live Higgsfield result cost approximately 600 credits for three
  minutes, or roughly 3.33 credits per second. This supersedes the assumption
  that Higgsfield can economically generate every block of a ten-minute pilot.
- The strongest prior assets were high-quality generated worlds and character
  concepts. The weakest outputs were generic deterministic plates, unsupported
  maps/graphs, and camera movement applied to a static background.
- The successful motion examples depended on actual subject or environmental
  action. Shifting the entire image produced visible shake and did not improve
  storytelling.
- Existing project primitives already provide hashing, rights review, character
  candidates, task-ID resume, citations, captions, and local assembly. The new
  work adds the missing upstream communication and scene-flow contracts.

T3 added the scene contracts and T4 compiled the demand maps after Communication
Language approval. No new media generation occurred before the Asset Demand Gate.

## Implementation Checkpoint

T1 through T6 are complete. The operator approved the revised Asset Demand Gate
on 2026-08-01, then clarified that still-image generation may be used broadly
because animation and narration are the material cost centers. T6 generated 14
subscription-backed still-image calls through the Codex built-in path, which
does not disclose an underlying model name or per-call price. No animation,
video, or voice generation occurred. The operator approved the Asset Foundation
Gate on 2026-08-01; accepted candidates were promoted into immutable,
content-hashed manifest V2 before the bounded motion proof. The quarantine
review remains preserved as pre-promotion evidence.

Asset Demand Gate feedback on 2026-08-01 retained Combat Woodblock as the
parent identity and added three controlled pack variants: anime action,
historical editorial, and comic whitespace. The pre-existing 81-image GPT set
was inventoried rather than discarded; it remains human-directed calibration
evidence and cannot reach a renderer without individual manifest promotion.

The operator approved the Communication Language Gate on 2026-07-31 with the
instruction to proceed. The active Reference Pack carry-forward was narrowed to
catalog rhythm, motivated transitions, action-phase cut points, narration-led
sound, stable outline/color/camera grammar, concept-obedient motion, reusable
comparison layouts, and flat colors with thick outlines. All other Reference
Pack observations remain archived and non-operative for this lane.

On 2026-08-01 the operator made the production correction explicit: image
generation is inexpensive enough to schedule imagery from timestamps, and the
timestamps make editing arithmetic. The next lane compiles one unique primary
plate prompt per selected coverage slot under a chapter continuity spine; it
does not substitute old plates, generic scenes, or prose-excerpt grouping. The
compiler, prompt spine, and validation are being added without a provider call;
generation remains a separately reviewed bounded-wave operation.

The first timestamped still-image wave now covers 00:00–00:52.500 of Episode 1:
eleven new AI-assisted illustration candidates plus the already quarantined
operator-supplied Kodokan gate archive review insert at 00:13. The contact
sheet is at
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_visuals/timestamped_plates/wave-001/wave-001-contact-sheet.png`.
The first battlefield candidate was rejected for photographic grit; the shared
Combat Woodblock lock now requires clean graphic carved contours and flat color
fields, with only a faint smooth paper substrate. All new candidates remain
quarantined and none are in the render manifest. The gate archive remains
review-only pending its separately recorded source, date, license, and
attribution verification.

The operator then authorized the complete timestamped still-image production
run. All 138 planned slots have a unique selected primary visual assignment:
137 new clean Combat Woodblock AI-assisted illustration candidates and the
single review-only Kodokan archive insert at slot 004. The derived,
content-hashed candidate inventory is
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/timestamped-plate-candidate-inventory.v1.json`
(`3af7c2a26e80aa39e1b690ea950d3f9a220b1a6d320a27ad9526ef3b4753eb0e`).
The full contact sheet is
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_visuals/timestamped_plates/contact-sheets/episode-1-all-138-contact-sheet.png`,
and per-wave contact sheets are adjacent. Direct verification confirmed
contiguous orders 001–138, 138 unique coverage slots and selected paths, and
SHA-256 agreement for every selected file against timestamped plate plan
`5c45a292438cd0579667a1222aad1c519848ea7a7d6554a6f9005c597e6320cd`.
All generated images remain non-renderable quarantine candidates; the archive
remains review-only. This is an asset-production completion, not a promotion,
animatic, Gate A, or publication decision.

The operator approved the timestamped candidate pack on 2026-08-01. A
dedicated promotion compiler now validates the immutable candidate inventory
against the timestamped plan, checks every local SHA-256, and produces a
standard `asset_manifest.v1` without altering the pre-promotion inventory or
the frozen V2 foundation manifest. The resulting
`content/video_engine/projects/history-of-bjj/episode-1-timestamped-plates-asset-manifest.v1.json`
has artifact hash
`4bb6a61acbff1b30a21651ce04786ddca1649f50d781b57c208bd1b5ced819ad`:
137 original AI-assisted illustrations are render eligible. Slot 004 remains a
quarantined `unverified` Kodokan archive and cannot resolve into a renderer
until its source, date, licence, and attribution are separately reviewed. The
job-local resolver output hash is
`8f7305f503320ad6bc8779fd4e117aad2b1ab8803755d92ed6c6f0d50c20d3f7`;
it contains 137 renderer-safe local asset records and no provenance URLs.
Promotion passed `validate-assets`, `19 passed` focused promotion/resolver
tests, and `325 passed, 1 warning` for the complete video-engine suite. The
warning is the pre-existing `pydub`/`audioop` deprecation. It is an
asset-readiness checkpoint only: no episode manifest was repinned, no
animation/narration/assembly started, and Gate A/B remain untouched.

Verification after immutable foundation promotion: `42 passed, 1 warning` for
the documentary, asset, living-scene, and History V4 focused contracts;
`316 passed, 1 warning` for the complete video-engine suite; `748 passed,
1 warning` for the full repository; and successful Remotion typecheck/build.
`validate-assets` confirmed manifest V2 and `validate-history` confirmed the
episode's hash-bound reference; the preserved quarantine review and PRP
validator also passed. The warning is the existing Python `audioop`
deprecation emitted through `pydub`.

One bounded deviation was required: T1's approved validation command did not
exist before implementation. The isolated `living_scenes.py` service and CLI
commands were added so inventory, grammar, asset demand, world packs, scene
bundles, and scene flow could be validated rather than asserted.

## Timestamped Editorial Render Checkpoint — 2026-08-01

The user supplied the Web Japan Kodokan page as provenance for the temporary
slot-004 archive. The source is retained for research/citation provenance, but
its footer states “All rights reserved”; it was not promoted as render media.
Slot 004 is instead an original illustrated compound exterior. The immutable
candidate inventory V2 is all-original (`9d1dba3df788337a79fcdd6401297bbcfe0b3a4479aa83af1d8cada9fb2e22b8`), and the promoted 138/138
timestamped-plate manifest V2 has hash
`268625f2b4c11e63b256a9d139f1f008e171ccba1a4b98c5b76932a92a81027b`.
The job-local resolver artifact has hash
`ec202044b8ce8d30f78ff13c6d6451200013d52defe2d6fc615df34cae6b31db`.

`compile-timestamped-editorial-motion` was added to bind each approved primary
plate to the canonical ElevenLabs words, not the earlier visual-duration
estimate. It fail-closes on stale plate/asset hashes, missing slots, unmatched
narration, unaccounted-for words, or a render-ineligible asset. The V17 plan
contains exactly 138 distinct primary assets, no legacy asset IDs, no burned
captions/citations/information surfaces, 559.922 seconds of canonical audio,
and only sparse 1% focal pushes amid narration-timed hard cuts. Its hash is
`1c8dd9bcce036e7734fc91141df2ff5dbdd712964c3f22774bad989678389b5f`.

The local V17 review animatic was rendered at 426×240/8fps with the existing
canonical ElevenLabs master and no provider calls or cost. Its packet is at
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v17-timestamped-original/review-packet.json`;
it reports structural QC `pass`, `gate_a_unchanged: true`, and requires human
review. FFprobe verified an AAC narration stream of 559.936 seconds alongside
the H.264 preview. Focused tests were `33 passed`; full-suite validation and
Gate A review remain pending. No publishing, registry write, commit, or push
occurred.

## Timestamped Cadence and Intent Correction — 2026-08-01

The V17 preview was deliberately a low-cost 426×240/8fps review render; it was
not a production-quality image render. Review exposed a separate timing defect:
the original prose-excerpt retimer assigned narration that had no exact prior
coverage excerpt to the preceding plate. The most visible result was a
23.68-second hold from 00:17.03 to 00:40.72. V17 is retained as rejected
diagnostic evidence and must not be treated as a candidate for Gate A.

V20 temporarily repaired the duration defect by proportionally placing the
inherited plate schedule on canonical word boundaries. It restored a 5.70-second
maximum hold and twelve cuts in the first 45 seconds, but review of the actual
spoken content exposed a stronger defect: a plate can still drift onto prose it
was never prompted to depict. V20 is therefore retained only as a timing and
image-quality diagnostic, not an episode candidate or Gate-A input.

The replacement compiler binds an inherited plate only to its exact ordered
narration phrase. `analyze-timestamped-semantic-coverage` then emits a distinct
`generation_required` slot for each uncovered canonical interval; it is
impossible to compile a render until those slots have an approved visual asset.
Every slot records visual intent (`academic`, `martial`, `scenic`, `journey`,
`evidence`, `explanation`, `humor`, or `transition`) and required visual
actions. Travel beats require locally rendered, reviewed map cut-ins for each
named location; meaningful lists require one concrete visual action per item.
This is explicitly not a cut-on-every-noun rule, and actions must resolve to
approved visual assets—not generic text boxes, books, or cards.

The V20 timing diagnostic plan is
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v20-timestamped-cadence-intent/editorial-motion-plan.json`
with hash `e2ed867a04fee297b811c85c1188bc12419a39746410d1394240439751b6710e`.
The sharp local review sample ends on a planned cut at 44.373 seconds and is
1280×720/24fps at
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v20-timestamped-cadence-intent/first-45s-720p/revised-preview.mp4`.
Its packet records zero provider calls/cost, structural QC pass, unchanged Gate
A state, and required human review. The first coverage report is preserved as
an immutable diagnostic. The current sentence-aware semantic coverage report is
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/semantic-coverage.v4.json`
with hash `7e6b11cd51d3eaf9fc942504a0ed5ad3359cb005604d62f83b136b95aa8175f3`.
It identifies 71 missing semantic slots; V20 deliberately does not fake those
maps or list actions with arbitrary overlays. The new authoritative schedule,
compiled directly from canonical narration rather than inherited plate timing,
is `canonical-visual-coverage.v3.json`
(`ae4bf7b24e40b87fa6a233c6560e4bfe42766803559bf52459c2589e0d6780ed`):
139 contiguous slots, each 2.554–4.644 seconds, covering all 559.922 seconds.
It contains no automatic legacy asset assignments and is not render-ready until
each slot receives an explicit reviewed asset. The first six original action
candidates (school, unarmed teacher, formalization ledger, public audience,
Brazilian arrival, and a non-geographic route backing) are quarantined at
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_visuals/action_assets/wave-001/`
under immutable brief `action-asset-wave.v1.json`
(`71dcebd323562c3a8b34839d3862bc5f95a0450de7b07eba7a53b7ad22ccefd3`).
The route backing may never itself carry geography, labels, routes, dates, or
historical claims; those remain deterministic local map elements. None of the
six candidates is render eligible until the corrected semantic plan selects it.

## Canonical Image-Led Production — 2026-08-01

The approved art direction is now being materialized against the canonical
schedule rather than the legacy plate order. Waves 002–005 add original,
quarantined 16:9 historical-editorial plates for the opening contrast, the
institutional turn, practice continuity, the evidence question, formalization,
selection and reorganization, multiple school thresholds, education, internal
adaptation, institutional practice, travel, a record anchor, and later-label
correction. Every file is byte-hashed in its adjacent
`action-asset-wave.v1.json`; rejected candidates are preserved by generated
file name and explicit reason rather than silently reused.

The six most recent promoted-to-quarantine waves are at
`.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_visuals/action_assets/wave-002/`
through `wave-005/`. In particular, the new record-anchor, label-correction,
institution, and efficient-practice plates are assets for canonical slots
009, 020, 021, and 022; they are not additions to V17/V20. Both draft renders
remain rejected diagnostic evidence. The next implementation boundary is an
immutable, explicit canonical assignment manifest which binds a selected asset
to every canonical slot (including per-item list micro-cuts) before the new
renderer is allowed to assemble any image-led review render.

The first binding now exists as
`canonical-visual-assignment.wave-001.v1.json`. It covers 25/139 canonical
slots (001–025) with new wave assets only; it was structurally checked for all
25 expected slots with zero duplicate slot IDs and remains explicitly
`partial_quarantined_not_renderable`. Slot 001 has an intentional battlefield
foil → institution hard cut at 2.2 seconds, and slots 008 and 024 enumerate
their approved action assets rather than using a list card. No legacy image is
referenced by this artifact.

## Canonical action coverage V4 — 2026-08-01

The operator approved canonically mapped image generation as the active
production rule. `canonical_visual_coverage.v4.json`
(`f6aee53b8d8388e596364c4c33836f43d872f91cc33b51a2c740546ee3158b26`)
is now the active 139-slot schedule. It preserves V3's verified 559.922-second
word-timing boundaries, while making meaningful enumerations enforceable:
comma-separated `entered` and `used for` contexts, in addition to the prior
list patterns, produce a separate required action for each narrated item.
This is still not a noun-per-cut rule.

V3 and `canonical-visual-assignment.wave-001.v1.json` remain immutable audit
evidence. They cannot be silently reused as V4 renderer input. Wave 008 adds
five quarantined original plates for the school, theater, challenge-match,
immigrant-community, and reduction-correction beats (canonical slots 026–028),
each with its own content hash. A successor assignment will bind all selected
assets to the V4 hash before any editorial render is allowed. No old V17/V20
asset, generation provider, narration call, gate decision, publication,
registry write, commit, or push was used.

## Canonical action coverage V5 — 2026-08-01

V4 review found a sentence-boundary defect: a timed slot that crossed from one
sentence into another could analyze both together, allowing a later list to
hide items in the first. The V5 compiler evaluates each overlapping sentence
independently and records only the action whose spoken subject begins inside
the slot. `canonical_visual_coverage.v5.json`
(`16e3602d4d1b140c4b82a48d027f420c0048b9ad03da17cbcdab6e5b5fabb61a`)
is now active: 139 contiguous slots across 559.922 seconds, non-renderable
until full review and promotion. It correctly maps `advertisements`,
`demonstrations`, `newspapers`, `translations`, and `later memories` to their
respective timestamp slots.

Focused planner/QC evidence: `46 passed in 0.75s` for
`test_editorial_motion.py` and `test_editorial_motion_qc.py`, including a new
sentence-boundary regression test. V3/V4 coverage files and all prior wave
manifests remain immutable provenance; the next canonical assignment will bind
selected original candidates to V5. This changed no narration, provider usage,
rights state, Gate A, Gate B, publication, registry state, commit, or push.

## Canonical action coverage V6 — 2026-08-01

V5 still missed subject-led enumerations whose governing verb landed later in
the sentence. The compiler now recognizes explicit comma-separated subjects
such as “theaters, demonstrations, challenges, and advertised lessons put …”
without becoming a noun-per-cut scraper. It still requires a real enumeration
and binds each item to the slot containing that spoken item.

`canonical-visual-coverage.v6.json`
(`f6970503f46596eddba7b2b98948df6c72aaeb51cd7db80d11f10ac33d1e8c26`)
is the active 139-slot / 559.922-second non-renderable schedule. It records
the theatre/demonstration/challenge/lesson rhythm in slots 073–074 and the
audience/venue/local-economy/instructor-promise rhythm in slots 078–079.
V5 candidate waves remain immutable quarantined inputs; a future V6 assignment
must explicitly bind their content hashes before any render.

Focused evidence: `47 passed in 0.30s` for the editorial-motion and QC tests,
including the new subject-led-list regression. No paid provider call, gate
decision, publication, registry write, commit, or push occurred.

## Canonical action coverage V7 — 2026-08-01

V6 uncovered a narrower semantic defect: the explanatory frame in “It shows
why techniques, labels, and teaching methods could shift …” was being treated
as part of the first list item. The V7 compiler recognizes this sentence form
and emits only the intended actions: `techniques`, `labels`, and `teaching
methods`.

`canonical-visual-coverage.v7.json`
(`6c81bf078c5ba80dcfdc7958f7e01ca3ccf3c324851009f4b469ad558ae28bce`)
is the active 139-slot / 559.922-second non-renderable schedule. Its initial
candidate map explicitly binds the earlier V6 action candidates by exact path
and hash, and adds V7 wave 023 for venue, local economy, instructor promise,
and disciplined study. All candidates remain quarantined and no assignment is
a promotion or render authorization.

Focused evidence: `48 passed in 0.30s` for the editorial-motion and QC tests,
including the explanatory-enumeration regression. No paid provider call, gate
decision, publication, registry write, commit, or push occurred.

### V7 candidate-foundation progress — 2026-08-01

The active V7 candidate map now binds 21 exact local candidates for the
Belém/action sequence, leaving 118 canonical slots unresolved and explicitly
non-renderable. Waves 021–022 are V6 provenance explicitly adopted by hash;
V7 waves 023–026 add venue, local economy, instructor promise, disciplined
study, public testing, neighboring sport culture, the Belém public
challenge/class/environment contrast, and the later qualified network context.

Wave 025 is deliberately all rejected: the generated scenes used Japanese
architecture and dress after the audio had entered the Belém chapter. The new
prompt amendment makes geographic world identity a first-class constraint
separate from the woodblock illustration medium. Candidate-map verification
confirms 21 assignments, zero missing paths, zero hash mismatches, zero
unknown slot references, zero duplicate primary slots, and `render_eligible:
false`. No render, narration, video provider call, gate decision, publication,
registry write, commit, or push occurred.

Video-engine verification after V7: `339 passed, 1 warning in 39.95s`; editor
`npm run typecheck` passed. The V7 contact sheet is review-only evidence bound
to candidate-map hash
`044b64f954fd5a71c82b7cdffc73d0f50d35327b2f94b604b824a84dd26cb152`.

## Canonical action coverage V8 — 2026-08-02

V7 exposed one remaining semantic loss: a parallel sequence of role changes
(`a student can …, a local teacher can …, and later memory can …`) was treated
as prose rather than as three meaningful editorial actions. V8 recognizes a
parallel modal-clause sequence only when every comma-separated clause contains
a modal action, so it fixes the role progression without becoming noun-driven
literalism. `canonical-visual-coverage.v8.json`
(`bc9837bd834f55b4937a3082e5d62a5b7103c501145a0659036eb32967b27829`) is
the active 139-slot / 559.922-second non-renderable schedule. Slots 107–108
now explicitly require the student-to-instructor, teacher-to-community, and
memory-compression visual actions.

`canonical-visual-candidate-adoption.v8.json` explicitly carries forward the
24 V7 candidate assignments by exact candidate-map hash
(`9b1a8a6ce161d1af8af8e540947c296855f1a18c506263597002042f69a1f937`),
leaves 115 slots unresolved, and remains `render_eligible: false`. This is an
audit adoption, not a promotion or permission to render. The V8 prompt
amendment locks the Brazilian Amazonian Belém world through slots 081–108 and
prohibits Japanese-location defaults, evidence-like props, and invented
historical claims. Wave 029 adds three further original, quarantined V8
candidates for the two role-progression slots: learner-to-instructor,
teacher-to-community, and several stages held apart by later memory. The wave
declares exact slot/action support and SHA-256 values, but it is deliberately
outside the adoption map until explicit candidate selection; its three byte
hashes were verified locally and all retain `render_eligible: false`. Focused
planner/QC evidence: `49 passed in 0.69s` for the editorial-motion suites,
including the parallel-modal-clause regression. No paid provider call, render,
narration call, gate decision, publication, registry write, commit, or push
occurred.

### Wave 029 promotion — 2026-08-02

The operator then explicitly approved promotion of the three Wave 029 plates
reviewed for V8 slots 107–108. The immutable partial manifest
`canonical-v8-wave-029-asset-manifest.v1.json` has hash
`d3cdb07dd759e3b9fc23ed5456db12a9b2e019b9e118af2f6f09a3132f1cb863` and
marks exactly three original AI-assisted illustrations renderer-eligible:
student-to-instructor, teacher-to-community, and memory-holds-many-stages.
Its job-local resolved artifact has hash
`1ace77784c3105a1a1a889477c273db928d2deb09a1c791ea6fd722d872fe6a9`; it
contains only the three local asset IDs, paths, and byte hashes and no research
or rights provenance. `validate-assets` and PRP validation passed. This is a
partial asset readiness record for the two covered V8 slots—not an episode
manifest, storyboard pin, animatic authorization, or approval to promote the
earlier V7 candidates.

### Wave 030 — V8 network sequence — 2026-08-02

The next bounded V8 generation wave supplies eight quarantined candidate plates
for canonical slots 099–106: network/place context, multiple settings,
intermediate local role, multi-path river transition, shared-circle teacher,
two equally weighted community roles, intermediary thresholds, and an evening
human network. One initial candidate was rejected because it repeated the
adjacent indoor-class composition and failed the required two-role courtyard;
the replacement passed the composition, geographic-world, evidence, and
adjacent-uniqueness checks. The 4×2 review sheet is at
`generated_visuals/action_assets/wave-030/wave-030-contact-sheet.png` with
SHA-256 `2ad30fc95df0dfc49990eab4a2b2b70e31501d01bb151c6b57efe1037f0fa7e2`.
Wave 030 is `awaiting_operator_selection` and all eight assets remain
`render_eligible: false` until an explicit promotion approval.

For the earlier 24 candidate assignments, a separate V8 reconciliation sheet
is now available at
`generated_visuals/review_sheets/canonical-v8-inherited-candidates-contact-sheet.png`
with SHA-256 `a0103567abd10a1f451f65eecf70ec93fec1c9c5b09380d261a293d0584a7cd6`.
The review packet binds that sheet to the V7 candidate-map hash and requires
an explicit candidate-by-candidate V8 accept/reject decision; it is not a
promotion. No provider call beyond approved built-in still generation, no
narration/video generation, no render, gate decision, publication, registry
write, commit, or push occurred.

### Wave 030 promotion — 2026-08-02

The operator explicitly approved all eight reviewed Wave 030 plates. The
immutable partial manifest `canonical-v8-wave-030-asset-manifest.v1.json` has
hash `afb7b5ee033dfd88f69ae5563615bd0b3dbc15653637548133fbd9dee30205bc`
and marks exactly the eight original AI-assisted illustrations for slots
099–106 renderer-eligible. Its job-local resolver artifact has hash
`eb9a2e5704cf5875d9087bbfc120e358dd093507a0904dd0c49bd6b91c06e9bd`.
This is still a partial selection: it does not select the inherited review
sheet, create a full asset manifest, authorize rendering, or advance a gate.

## Canonical action coverage V9 — 2026-08-02

V8 review found one remaining list-action loss in the Brazilian research
sentence: “Studies of Brazilian judo identify immigrant teachers, professional
fighters, and community networks …” did not schedule its three meaningful
social-role actions. V9 adds a narrow verb-led `identify` inventory detector,
after more-specific `used to` handling, so it does not become noun-per-cut
literalism. `canonical-visual-coverage.v9.json`
(`fbf3c6dbf0824cffe57464129fefc7e9d63d3c28a4b377d6bfdebe27f1db5754`) is
the active 139-slot / 559.922-second non-renderable schedule. It records the
three actions at canonical-112: immigrant teachers, professional fighters,
and community networks.

Focused editorial-motion/QC validation passed: `50 passed in 0.30s`, including
the new identifying-inventory regression. The V9 prompt amendment extends the
Brazilian world lock through slots 081–116 and prohibits a map, relationship
graph, fake document, generated text, or named historical claim from standing
in for the three role actions.

Because V9 changes only canonical-112, the exact eleven operator-approved V8
assets for unchanged slots 099–108 are explicitly carried through
`canonical-visual-promoted-adoption.v9.json`, bound to both source manifests
and their resolver hashes. The adoption is `partial_promoted_not_renderable`:
it does not silently reuse any quarantined candidate, bind a storyboard, start
a render, generate narration, call a provider, or change any gate. No paid
provider call, render, narration call, publication, registry write, commit, or
push occurred.

### Wave 031 — V9 Brazilian research field — 2026-08-02

The next V9 candidate wave covers canonical slots 109–116 with eight original
16:9 primary plates and three list-action cut-ins for the required research
inventory at slot 112: immigrant teachers, professional fighters, and
community networks. All eleven selected candidates are quarantined at
`generated_visuals/action_assets/wave-031/` and carry exact dimensions and
SHA-256 hashes in `action-asset-wave.v1.json`. Their 3×4 contact sheet is
`wave-031-contact-sheet.png` with SHA-256
`906eae3210de8d6343e6e794bdea1cb12372b9679a3b4333a0c313b7c64a2652`.

One generated regional-spread candidate was rejected and retained by exact
path/hash because it used multi-person grappling choreography. Its replacement
uses a river pier, street, and empty practice threshold, meeting the History
V4 prohibition on technique-tutorial visual sequences. The review packet
records Brazilian-world, material, composition, evidence, uniqueness, and
technique-prohibition checks; it remains `awaiting_operator_selection` and
all candidate assets remain `render_eligible: false`. No animation, narration,
video-provider call, render, gate advance, publication, registry write,
commit, or push occurred.

### Wave 031 promotion and learned workflow — 2026-08-02

The operator explicitly approved the eleven Wave 031 candidates. The immutable
partial manifest `canonical-v9-wave-031-asset-manifest.v1.json` has hash
`6b21dbd03007698455bdb5bc5a1594d1794e8d3e49927f45b5fc14051ec9e473`; its
resolver artifact has hash
`04c8b285a7cb5e544a97d0f2b3dbc504b073090b32a003b061bc4e864a8b025f` and
its credits artifact has hash
`eb6222ab518d1d76b2e639711e0c6b94af36ca74d2ba7fc30181e746d6fb5c38`.
`validate-assets` passed before resolver output. This promotes exactly slots
109–116 and the three explicit slot-112 actions; it is still a partial asset
selection and does not authorize storyboarding, animation, narration, video
generation, Gate A, or publication.

The approved recurring workflow is now encoded as the project-scoped skill
`.agents/skills/history-editorial-asset-foundation/`. It applies canonical
time binding, geography-versus-medium locking, semantic list actions,
quarantine/contact-sheet review, early rejection, and hash-bound promotion.
Continuous Learning v2 imported six matching instincts for this worktree at
85–90% confidence only: canonical-time binding, medium/world separation,
quarantine before promotion, list visibility, low-value surface rejection, and
the History V4 technique-choreography prohibition. No instinct was promoted
globally. No provider, render, narration, gate, publication, registry write,
commit, or push occurred.

### V11 inventory correction and Wave 032 — 2026-08-02

The next narration sentence exposed a second subject-led inventory gap:
“public performances, institutions, promotion, and nationalism helped
distinguish …” was not scheduling separate actions. The planner now recognizes
the governed `help/helped distinguish` form and removes a temporal `when` or
`while` lead-in before splitting the actual inventory. Focused editorial-motion
and QC validation passed: `51 passed in 0.33s`.

`canonical-visual-coverage.v11.json` is the active 139-slot, 559.922-second,
non-renderable schedule with artifact hash
`ffeb5bc4eb0707cd34e21a74a7fbbc17523de6fd2fdb1319fe355140348df784`.
The earlier V10 artifact is immutable diagnostic evidence only; it retained
the word `when` as part of a list subject. V11 corrects it and emits the four
meaningful actions across slots 121–122.

The V11 prompt amendment locks the new early-to-mid twentieth-century Brazilian
public-life world and preserves the no-text/no-fake-document/no-technique-
choreography guardrails. Wave 032 generated twelve original 1672×941 candidates
in the built-in image lane: eight consecutive primaries for canonical 117–124
and four inventory action cut-ins. Their file hashes, source paths, and
non-renderable status are recorded in
`generated_visuals/action_assets/wave-032/action-asset-wave.v1.json`; the
3×4 review sheet is `wave-032-contact-sheet.png` with SHA-256
`a9c859de0e3923bf905d21df6be7b72127268d0634598d36b5da7abd09bb607f`.
Local manifest validation confirmed all 12 paths, byte hashes, dimensions, and
`render_eligible:false` values. Visual inspection passed Brazilian-world,
material, grounding, evidence, no-low-value-surface, technique-prohibition,
and adjacent-uniqueness checks. The wave is `awaiting_operator_selection`; no
asset is promoted and no render, animation, narration, provider call, gate
advance, publication, registry write, commit, or push occurred.

`canonical-visual-promoted-adoption.v11.json` independently carries the exact
22 previously operator-approved assets for canonical slots 099–116 through the
V11 contract. It binds their approved V8/V9 manifest and resolver hashes,
remains `partial_promoted_not_renderable`, and makes no claim about Wave 032 or
full-episode readiness.

### V12 clone-ready learning and style handoff — 2026-08-02

The operator requested a portable handoff of the durable learning, documents,
and approved sample sets so a branch clone can develop an original blend of
high-contrast graphic silhouettes and Combat Woodblock worlds. The new
`combat-woodblock-graphic-silhouette-explainer-v1` profile separates the four
layers that had previously drifted together: stable period world, filled
foreground actor, one meaningful story signal, and locally authored fact
surface. It prohibits skeletal figures, whole-plate drift, generic gray
callouts, blank-book shorthand, generated factual text, source identity, and
technical grappling choreography.

The accompanying external explainer observations were distilled into
`reference_study.v1` with `render_eligible:false`; source media, creator
identity, source frames, and imitation language remain prohibited from every
renderer. Three new original calibration plates and the retained twelve-plate
Wave 032 historical editorial review set are copied under the project-local
style-sample directory with immutable byte hashes. They are visual calibration
only: a later job must still create its own prompt plan, asset manifest, and
operator selection. No narration, animation provider, render, or gate was
advanced by this handoff.

Validation for the clone handoff: the strict `reference_study.v1` validator,
PRP validator, focused editorial-motion suite (`51 passed`), complete
video-engine suite (`342 passed, 1 warning`), Remotion typecheck, and complete
repository suite (`774 passed, 1 warning`) all passed on 2026-08-02. The sole
warning is the external `pydub`/`audioop` Python 3.13 deprecation notice.
