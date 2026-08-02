---
id: P13-HISTORY-DOCUMENTARY-SYSTEM
title: P13 History Documentary V4 Research Rights And Editorial Motion System
status: running
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-07-30
updated: 2026-07-31
---

# P13 History Documentary V4 — Research, Rights, and Editorial Motion

## Summary

Pivot the P13 video engine from automated technique tutorials to a three-part History of BJJ
documentary-explainer series. Preserve the V1–V3 engine and Armbar proof as legacy/R&D evidence,
while adding research, rights, archival/editorial art, and human-gated V4 contracts.

## Intent And Acceptance

- Episode 1, *How Judo Became Brazilian Jiu-Jitsu*, is the only rendered acceptance pilot;
  its research master targets 10 minutes within an 8–12 minute acceptance band.
- Historical narration is compiled only from an approved, citation-complete research packet.
- Renderers receive approved local asset IDs and immutable hashes, never research URLs or study
  prompts.
- History V4 rejects `StickFigureScene`, multi-step technique tutorials, and mechanics exceeding
  15% of planned runtime.
- Archival photography and visibly stylized illustration alternate inside one original art bible.
- V4 stops at Research, Visual Direction, Gate A, and Gate B for operator approval.
- Approved masters yield two native vertical clips and chapter-level subvideos from
  self-contained claim clusters; no blind crops or context-losing excerpts.
- Snapshotted V1–V3 jobs and Armbar artifacts remain readable and resumable.
- Focused, render-smoke, Remotion, video-engine, and full repository verification pass without
  paid providers or external writes.

## Scope

- Durable P13 documentation and PRP state.
- Versioned history episode, research, asset, art-bible, shot, treatment, and storyboard contracts.
- V4 pipeline/CLI, research and rights guards, asset resolution, citations/credits, documentary
  compositions, style board, animatic, and QC.
- Three episode briefs; only Episode 1 advances to runtime gates.

## Not Building

- No technique-tutorial scale-out, realistic fight choreography, fair-use rendering,
  creator-style imitation, stock ElevenLabs voice, required provider dependency,
  academy promotion, publish, registry write, commit, or push. The user-authorized
  Magnific feasibility adapter produces review-only candidates and does not bypass
  the asset manifest or human gates.
- Episode 2 and Episode 3 do not receive approved scripts or final renders in this PRP.
- No human gate is auto-approved.

## Human Gates

- Research Gate approves thesis, source quality, contested framing, claim completeness,
  promotional neutrality, and rights readiness at 4/5 or higher.
- Visual Direction Gate approves six documentary still roles and six visual dimensions at 4/5 or
  higher.
- Gate A approves the motion/story animatic; Gate B approves the final publication candidate.
- Any new paid narration remains separately bounded after Gate A.

## Mandatory Reads

- `AGENTS.md`
- `content/video_engine/AGENTS.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/plans/P13-VISUAL-V3-ORIGINAL-ART.plan.md`
- `docs/content-video-engine/00-BRAINSTORM-AND-DECISIONS.md`
- `docs/content-video-engine/03-SYSTEM-ARCHITECTURE.md`
- `docs/content-video-engine/09-YOUTUBE-REFERENCE-PACK-LEARNINGS.md`

## Execution Path

1. Reconcile durable decisions and document ownership.
2. Add schemas, templates, validators, and immutable evidence contracts.
3. Curate Episode 1 research and rights-cleared local fixture assets.
4. Add the documentary art bible, scene grammar, style board, citations, and QC.
5. Integrate V4 stages and CLI while retaining frozen legacy stage snapshots.
6. Produce Episode 1 evidence and stop at each required human gate.
7. Run independent review and complete verification.

## Patterns To Mirror

- Immutable job-local artifacts and canonical SHA-256 hashes.
- Repository/service separation and explicit stage-event summaries.
- Research sources, study sources, and renderable assets remain separate domains.
- Manim owns deterministic maps/graphs/diagrams; Remotion owns local assets, editorial timing,
  captions, citations, transitions, and credits.
- External tools may create reviewed input assets but never become required pipeline dependencies.

## Task Slices

### T1: Durable documents and decision reconciliation
- Status: completed
- Owner: parent
- Depends on: none
- Write set: `docs/content-video-engine/`, this PRP, prior P13 PRP handoff notes
- Acceptance: authoritative doc index exists; technique-tutorial pivot, series scope, consultant
  disposition, gate ownership, and frozen Armbar status are consistent.
- Validate: cross-link search plus `python scripts/prp_validate.py .claude/PRPs/plans/P13-HISTORY-DOCUMENTARY-SYSTEM.plan.md`
- Evidence: `docs/content-video-engine/README.md`,
  `10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md`, and
  `11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md` created; V4 authority notices added to 00–04,
  06, 07, and 09. `python scripts/prp_validate.py ...` and the local Markdown-link check
  both returned `PASS` on 2026-07-30.

### T2: Episode and research contracts
- Status: completed
- Owner: implementation_luna
- Depends on: none
- Write set: history/research schemas and templates, history contract service, focused tests
- Acceptance: valid packets hash deterministically; uncited, contested, quote-locator, study
  leakage, and stale-review failures are actionable and fail closed.
- Validate: focused history/research contract tests
- Evidence: `configs/history_episode.schema.json`,
  `configs/research_packet.schema.json`, `src/services/history_contracts.py`, and
  `src/guards/research_gate.py`; focused contract verification returned `8 passed`.

### T3: Asset resolution and credits
- Status: completed
- Owner: implementation_luna
- Depends on: none
- Write set: asset schema/template, resolver/credits service, focused tests
- Acceptance: only path-contained, hash-matching, rights-reviewed local assets resolve; complete
  credits are emitted and fair-use/unapproved likeness/logo assets remain non-renderable.
- Validate: focused asset/credits tests
- Evidence: `configs/asset_manifest.schema.json`,
  `src/services/asset_resolver.py`, and asset/credits fixtures; focused resolver
  verification returned `11 passed`.

### T4: Documentary visual and editorial system
- Status: completed
- Owner: implementation_luna
- Depends on: T2 contract vocabulary
- Write set: V2 art/treatment contracts, history art bible, documentary scenes/style board/QC,
  Remotion documentary composition, focused tests
- Acceptance: eight composition functions, six style-board roles, local editorial assets,
  citations, maps/timelines/lineage, illustration labels, and technique-runtime limits validate.
- Validate: focused scene/style/QC tests plus Remotion typecheck/build
- Evidence: `configs/art_bible_v2.schema.json`,
  `configs/visual_treatment_v2.schema.json`,
  `configs/art_bibles/combat-history-archival-editorial-v1.json`,
  `src/scenes/documentary.py`, documentary treatment/style/QC services, and
  `editor/src/Documentary.tsx`; focused verification returned `5 passed`.
  Remotion `typecheck` and `build` both passed.

### T5: Episode 1 research packet and series briefs
- Status: completed
- Owner: parent
- Depends on: T2, T3
- Write set: `content/video_engine/projects/history-of-bjj/`
- Acceptance: Episode 1 claims and sources are reviewable without treating consultant statements
  as facts; Episode 2–3 contain research questions only; pilot asset manifest is rights-ready.
- Validate: history/research/assets CLI validators
- Evidence: `projects/history-of-bjj/episode-1.json`,
  `episode-1-research-packet.json`, `episode-1-asset-manifest.json`, two
  research-question-only follow-up briefs, two reviewed public-domain archive
  images, and four original SVG assets. Validators passed with episode hash
  `88b96b65e0efa8288c833b0aad35975d9f475879643a9fba12eb5fac668ce7e1`,
  research hash `72660fc3eda71b8c13d7e1aa345e65aed4e3700397311be554ff97cd011a1aef`,
  and asset-manifest hash
  `fe5ff84e5e9d77151657605ed4bb6874e5678580a1a077c3ff467856465047ae`.

### T6: Pipeline V4 and Storyboard 2.2 integration
- Status: completed
- Owner: parent
- Depends on: T2, T3, T4
- Write set: video models/pipeline/CLI, ingest/transform/shot/storyboard services, channel config,
  Storyboard 2.2 schemas, integration tests
- Acceptance: History V4 follows Research→Visual→A→B; renderer instructions use IDs only;
  V1–V3 stage snapshots and resumes remain unchanged.
- Validate: focused pipeline/CLI/storyboard/integration tests
- Evidence: V4 model/pipeline/CLI integration, `storyboard_v2_2.schema.json`,
  documentary storyboard guard, history pipeline services, series-lane routing,
  and `tests/test_history_v4_pipeline.py`. Frozen V1–V3 constants and stage
  snapshots remain separate. With Manim 0.20.1 installed, focused renderer tests
  returned `11 passed`; the complete video-engine suite returned `180 passed`.

### T7: Episode 1 runtime proof
- Status: in_progress
- Owner: parent
- Depends on: T5, T6
- Write set: local `.context` runtime evidence and this PRP
- Acceptance: research packet reaches Research Gate with zero approvals; after operator actions,
  style board reaches Visual Gate, animatic reaches Gate A, and final outputs reach Gate B.
- Validate: status/QC commands plus low-resolution real renders
- Evidence: authoritative job
  `.context/p13-history-v4/jobs/c41aafc0-bf12-4585-b025-394407693871`
  records the operator's explicit approval of research hash
  `72660fc3eda71b8c13d7e1aa345e65aed4e3700397311be554ff97cd011a1aef`
  and Visual Direction approval against art-bible hash
  `7a14c51a6109a440266c101ddb778119640b6b73706b86b4511f6d948034321b`.
  It is stopped at `awaiting_gate_a` with a 608.53-second silent editorial
  motion preview compiled into 83 evidence-bound visual beats, sentence/idea
  captions, citation rails, approved local archive/original assets, and zero
  provider calls. Gate A and Gate B remain pending. Earlier jobs
  `56560ef2-6ae8-416c-ab45-b24761111fdf` and
  `18388876-e35f-4034-86db-314e5a3d7f1d` are superseded evidence from the
  placeholder and first asset-aware style-board iterations. Jobs
  `8e97798c-26b3-439a-b131-8746a2f131a3` and
  `97e0aab9-ebd5-47df-b65d-fe9d863b3b5b` are superseded motion iterations
  rejected internally for repeated first-scene content and assetless Manim
  documentary frames.

### T8: Independent review and full verification
- Status: completed
- Owner: reviewer
- Depends on: T1–T7 implementation
- Write set: read-only review; parent owns any fixes and PRP evidence
- Acceptance: rights leakage, claim enforcement, path safety, legacy compatibility, attribution,
  provider boundaries, and missing tests receive an independent review.
- Validate: video-engine suite, Remotion checks, full repository suite, PRP validation
- Evidence: independent review found one high and two medium actionable issues.
  All were fixed: Manim manifest segment paths are now relative, job-contained,
  existing MP4 files; Visual approval snapshots the canonical documentary
  style-board hash and Gate A rejects drift; and targeted path/tamper regressions
  cover both boundaries. A Gate-A dry run also exposed and fixed legacy grappling
  QC routing in History V4 plus an over-strict global signature rule; V4 now uses
  documentary QC and rejects only adjacent signature repetition. Focused
  verification returned `19 passed`; `python -m pytest
  content/video_engine/tests -q` returned `187 passed`; serial `python -m pytest
  -q` returned `619 passed`; Remotion typecheck/build and PRP validation passed.

### T9: Sentence-level editorial beat refinement
- Status: completed
- Owner: parent
- Depends on: T7 Gate A feedback
- Write set: documentary animatic/editorial beat compiler, focused tests, local
  revised Gate A evidence, this PRP
- Acceptance: each complete narration sentence receives its own visual beat;
  semantically contrasted clauses may receive a deliberate hard cut; durations
  preserve the approved storyboard clock; captions and citations remain bound
  to the parent claim; adjacent beats vary visual intent and camera motion; the
  opening visibly contrasts a labeled battlefield illustration with a tranquil
  institution/Kodokan treatment.
- Validate: focused animatic/editorial tests, real low-resolution revised
  animatic, pre-Gate-A guards, complete video-engine and repository suites
- Evidence: `src/services/editorial_beats.py` compiles immutable,
  storyboard-hash-bound sentence/contrast beats while preserving the approved
  narration clock, claims, and citations. The revised candidate contains 83
  beats/82 cuts over 607.999 planned seconds with a maximum 11.902175-second
  visual hold. The opening hard-cuts from a labeled battlefield illustration
  to a tranquil institution, then Kano archive context. Remaining beats use
  excerpt-specific documents, named graphs, place/date maps, concept panels,
  and the correct rights-reviewed Kano/Maeda archive assets. Gate A rejects
  stale/tampered beat plans or holds over 12 seconds. Focused tests returned
  `17 passed`; video-engine tests `192 passed`; serial repository tests
  `624 passed`; Remotion typecheck/build passed.

### T10: Branded Literature tone system
- Status: complete
- Owner: parent
- Depends on: T9 Gate A tone feedback
- Write set: history art bible/configuration, branded-literature mode compiler
  and style board, relationship validation, editorial specification, focused
  tests, local Visual Direction evidence, this PRP
- Acceptance: the history lane alternates three explicit modes—purposefully
  rough low-fi comedy, historical comic blocks, and archival evidence blocks;
  humor interprets but never proves a claim; comic reconstruction is visibly
  labeled; archive/document blocks carry proof and citations; relationship
  diagrams render only named entities and typed evidence-backed edges; generic
  keyword graphs fail closed or fall back to a non-diagram mode.
- Validate: art-bible/schema/config tests, mode/relationship tests, six-frame
  real style board, Visual Direction gate packet, video-engine tests
- Evidence: `combat-history-branded-literature-v1` implements the three-mode
  identity and is selected by the `history-of-bjj` channel lane while the
  archival-editorial art bible remains valid for snapshotted jobs. The style
  board renders two low-fi blocks, two historical comic blocks, and two
  archival evidence blocks with a shared folio/citation system. Relationship
  rendering now fails closed unless narration contains two recognized named
  entities and an explicit typed relationship; the rejected
  `date / mean / every / older` fragment compiles to a low-fi aside instead.
  Authoritative revision job
  `.context/p13-history-v4/jobs/23a1cc20-54fa-4f7e-940a-de6c88f2da2e`
  carries the unchanged approved research hash and is stopped at Visual
  Direction with zero provider cost. Focused revision tests returned
  `29 passed`; complete video-engine tests `197 passed`; serial repository
  tests `629 passed`; Remotion typecheck/build passed.

### T11: Coherent production-profile fork
- Status: complete
- Owner: parent
- Depends on: T10 Visual Direction rejection
- Write set: production-profile schema/profile, derived history art bible,
  art-direction validation, channel selection, style-board profile binding,
  editorial documentation, focused tests, Visual Direction evidence, this PRP
- Acceptance: a single reviewed long-form history profile preserves its
  composition, limited-animation economics, edit cadence, visual hierarchy,
  and sound hierarchy as a hash-bound base; the Combat History fork declares
  explicit retained grammar, brand overrides, and differentiation; source
  frames, character designs, scripts, maps, logos, and assets remain
  non-renderable; legacy art bibles remain valid; a new Visual Direction job
  stops before approval.
- Validate: production-profile and art-bible schemas, stale-hash rejection,
  profile-bound style board, V4 pipeline, video-engine and repository suites
- Evidence: `production_profile.v1` now records the reviewed long-form
  illustrated-history baseline as research-only grammar with source media and
  source assets explicitly disabled. The derived
  `combat-history-longform-cutout-fork-v1` art bible is hash-bound to that
  profile and declares retained composition, motion economics, editing,
  hierarchy, and sound rules plus original Combat History overrides and
  differentiation. Runtime and public CLI validation reject stale profile
  hashes. Authoritative revision job
  `.context/p13-history-v4/jobs/b1a831fe-d6f3-45d2-9a4d-1739ed5abf2e`
  retains the unchanged approved research hash and stops at Visual Direction
  with zero provider cost. Focused tests returned `30 passed`; complete
  video-engine tests `198 passed`; serial repository tests `630 passed`;
  Remotion typecheck/build passed.

### T12: Bounded Magnific feasibility slice
- Status: completed
- Owner: parent
- Depends on: T11 Visual Direction rejection
- Write set: bounded provider adapter/CLI/tests, ignored local bakeoff evidence,
  tooling/rights specifications, this PRP
- Acceptance: credentials load from the ignored shared env without disclosure;
  every paid request requires an explicit flag plus call and USD ceilings; inputs
  are local/hash-bound; prompts reject creator/reference leakage; outputs are
  cached, hashed, and non-renderable pending review; the provider's references,
  flows, Designer templates, agents/context, and stock catalog receive explicit
  production roles without weakening research or rights gates.
- Validate: focused adapter/pipeline tests, visual review of all outputs, PRP
  validation, and no additional provider call after the architecture review
- Evidence: seven Magnific image calls completed under the operator's $14
  authorization with a conservative aggregate ceiling of $0.75: one style
  transfer, two Flux voyage variants, and four Flux opening variants. The strongest
  candidates are the voyage print and battlefield print treatments. Raw prompting
  also produced an extra moon/route and carried a ship into an institution scene,
  proving the need for approved references plus reusable evaluator-gated flows.
  Every candidate remains `render_eligible: false`. The REST adapter supports only
  cost-known style-transfer and Flux 2 Pro experiments; no video call occurred.
  Magnific MCP was registered globally, but OAuth is currently blocked by the
  provider callback omitting the issuer expected by the client. REST authentication
  succeeds. Focused media/pipeline verification returned `18 passed`.

### T13: Magnific reference, flow, and stock intake contracts
- Status: completed
- Owner: parent
- Depends on: T12
- Write set: provider-reference registry, stock candidate/license receipt,
  flow snapshot, promotion CLI, focused tests, local operator templates
- Acceptance: styles, characters, elements, locations, templates, and flows are
  versioned against rights-cleared input hashes; stock downloads preserve provider
  resource/license/plan/attribution evidence; remote outputs remain quarantined
  until downloaded, hashed, reviewed, and promoted into `asset_manifest.v1`;
  evaluator gates and budget ceilings fail closed.
- Validate: contract tests for stale hashes, study-source leakage, missing stock
  attribution/license state, unsafe paths, stale flow versions, cost overflow, and
  promotion without operator review
- Evidence: `provider_reference_registry.v1`, `provider_flow_snapshot.v1`,
  `stock_candidate_batch.v1`, and `asset_selection_review.v1` schemas,
  templates, validators, CLI commands, HTTPS-only transport, quarantined preview
  intake, post-gate promotion, rights/attribution/cost checks, and focused tests.
  No reference training, flow publication, generated video, or full-resolution
  stock download occurred.

### T14: Living editorial coverage and deterministic still motion
- Status: completed
- Owner: parent
- Depends on: T13 contract vocabulary
- Write set: editorial coverage compiler/schema, motion recipes, animatic and
  Remotion still-motion rendering, focused tests
- Acceptance: every sentence or meaningful clause has a semantic visual slot;
  major shots target 3–6 seconds; micro-events occur every 1.5–3 seconds; long
  compositions carry multiple timed reveals; repeated nouns do not create
  redundant cuts; adjacent asset/composition/crop/motion signatures differ.
- Validate: semantic split/cadence tests, motion recipe tests, Remotion
  typecheck/build, and a low-resolution multi-source motion smoke render
- Evidence: `editorial_coverage.v1` compiles 138 Episode 1 semantic slots over
  607.999 seconds; each carries a purpose, source preference, 3–6 second target,
  micro-events, motion recipe, fallback, and unique signature. Storyboard 2.3
  preserves narration scenes while exposing these as visual beats. FFmpeg and
  Remotion consume the nine deterministic still-motion recipes. Focused
  coverage/editorial tests pass and Remotion typecheck passes.

### T15: Pipeline V4.1, Storyboard 2.3, and Asset Selection Gate
- Status: completed
- Owner: parent
- Depends on: T13, T14
- Write set: pipeline/model/CLI contracts, V4.1 stages, Storyboard 2.3 schema
  and guard, gate review packet, compatibility tests
- Acceptance: new History V4.1 jobs follow Research → Asset Selection → Visual
  Direction → A → B; asset approval is hash-bound and fail-closed; selected
  assets download/promote only after approval and known cost/license state;
  V1–V4 stage snapshots and resumability remain unchanged.
- Validate: gate-order/stale-hash/path/cost/rights tests, CLI tests, and frozen
  stage snapshots
- Evidence: new jobs snapshot pipeline `4.1` and Storyboard `2.3`; V4 stage
  snapshots remain unchanged. `VideoRun.asset_gate_status`, `approve --gate
  assets`, three public validators, hash-bound selection reviews, fail-closed
  cost/license/path validation, selected-asset resolution, and Storyboard 2.3
  guard/QC are implemented. Pipeline/documentary focused verification passes.

### T16: Episode 1 V4.1 asset-review proof
- Status: completed
- Owner: parent
- Depends on: T15
- Write set: ignored `.context` runtime evidence and this PRP
- Acceptance: create a new Episode 1 V4.1 job retaining the approved research
  hash, emit editorial coverage, quarantined stock candidates, an operator
  contact sheet, and an Asset Selection rubric; stop before downloads or later
  gates.
- Validate: job status, artifact hashes, zero paid/provider generation calls,
  and pre-gate validation
- Evidence: job
  `.context/p13-history-v4-1/jobs/2265aa0c-149f-48d2-8804-f28b488387e8`
  carries the unchanged approved research hash and is parked at
  `awaiting_asset_gate`. Its 138-slot coverage plan produced 38 stock search
  slots, 69 quarantined Magnific previews, 38 local fallbacks, 107 total
  candidates, a contact sheet, review template, and operator packet. Magnific
  REST authentication used 38 read-only searches and no paid generation or
  full-resolution download.

### T17: V4.1 independent review and full verification
- Status: completed
- Owner: parent
- Depends on: T13–T16
- Write set: parent-owned fixes and PRP evidence; review is read-only
- Acceptance: rights/cost leakage, gate bypass, path safety, cadence semantics,
  renderer correctness, and legacy compatibility receive a fresh review; all
  actionable findings are addressed or documented.
- Validate: focused tests, complete video-engine and repository suites,
  Remotion typecheck/build, PRP validation, and `git diff --check`
- Evidence: independent review identified two V4.1 hardening gaps: an
  unstructured scene/shot mapping failure and a Gate-A fallback when the
  treatment artifact was absent. Both now fail closed and the latter has a
  regression test. Final focused verification `30 passed`; video-engine suite
  `214 passed`; complete repository suite `646 passed`; Remotion typecheck and
  build, PRP validation, and `git diff --check` passed.

### T18: Theme-constrained stock discovery
- Status: completed
- Owner: parent
- Depends on: T14, T16
- Write set: editorial coverage router, stock relevance filter, schemas,
  editorial specification, focused tests, new ignored asset-review evidence,
  this PRP
- Acceptance: stock eligibility is assigned by a finite documentary archetype
  rather than a global rotation; queries use concrete historical entities,
  places, actions, periods, and media; every candidate matches its required
  subject/style facets before preview download; generic senior, travel-booking,
  hotel, golf, business, and effect-template results fail closed; graphs,
  documents, chapter cards, approved portraits, and distance maps remain local.
- Validate: focused coverage/stock/pipeline tests, real provider-backed contact
  sheet review, complete video-engine and repository suites, Remotion checks,
  PRP validation, and `git diff --check`
- Evidence: `editorial_coverage.v1` now assigns ten finite visual
  archetypes before provider discovery. The Episode 1 revision contains 19
  eligible stock slots instead of 38 rotation-selected slots: 11 martial-arts
  b-roll, four period-comic searches, and four historical-travel searches.
  Candidate scoring requires archetype subject/style facets, blocks category
  mismatches and generated/effect-template metadata, and deduplicates provider
  IDs plus 64-bit perceptual preview hashes before the gate. Authoritative job
  `.context/p13-history-v4-1/jobs/6b3c24bc-87e9-45fa-bdfc-b0b2c0058904`
  is parked at Asset Selection with 18 unique provider previews and 19 local
  fallbacks; 341 theme mismatches and 15 duplicates were rejected. No
  full-resolution asset was downloaded.

### T19: Historical martial archive lane and stock-integrated style board
- Status: completed
- Owner: parent
- Depends on: T18
- Write set: editorial archetype router, style-board asset resolution and
  composition, animatic asset resolution, focused tests, ignored runtime
  evidence, this PRP
- Acceptance: `historical judo` and `historical martial arts` form a separate
  discovery lane requiring both a judo/jujutsu subject and a period/archive
  facet; word matching cannot treat `scholarship` as `ship`; job-local promoted
  assets resolve without weakening project/job containment; the Visual
  Direction board visibly demonstrates selected stock inside the branded
  archive and map compositions.
- Validate: focused routing/style/animatic tests, complete video-engine and
  repository suites, Remotion checks, PRP validation, and `git diff --check`
- Evidence: `historical_martial_archive` searches the explicit phrases
  `historical judo` and `historical martial arts` but requires both a
  judo/jujutsu/Kodokan match and a period/archive facet. Magnific returned no
  candidates satisfying both, so those slots retained their verified local
  archive/illustration fallbacks. Whole-word matching prevents `scholarship`
  from routing as `ship`. Job-local promoted assets now resolve alongside
  project assets in the style board and animatic without relaxing containment.
  Job `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080`
  promoted three operator-selected assets at zero cost and is parked at Visual
  Direction. Style-board hash
  `04b7bd1cbb896ed4290420957ae3823cc7535f09916482a218e4d0be0f996138`
  visibly integrates selected judo and historical-ship stock while preserving
  the six required documentary roles.

### T20: Generated Visual Direction lane
- Status: completed
- Owner: parent
- Depends on: T19
- Write set: generated-visual candidate contract and schema, CLI validator,
  documentary style-board integration, focused tests, ignored runtime evidence,
  this PRP
- Acceptance: original AI-assisted historical-comic plates may appear in the
  pending Visual Direction board without becoming evidence or renderer assets;
  candidate files are job-local and hash-bound; remote paths, stale hashes,
  factual text, evidence eligibility, source-imitation language, and premature
  render eligibility fail closed; factual archive, document, map, and lineage
  roles remain deterministic or rights-reviewed.
- Validate: generated-visual CLI validation, focused documentary visual tests,
  complete video-engine and repository suites, Remotion checks, PRP validation,
  and `git diff --check`
- Evidence: six original project-bound plates were created with the built-in
  image-generation path at recorded cost `$0.00`: battlefield myth,
  institutional contrast, transoceanic voyage, a deadpan research-myth comic,
  an archival research environment, and a Japan-to-Brazil travel world. Five
  are selected only for the six-frame gate board; all six retain
  `render_eligible: false` and `evidence_eligible: false`. Candidate batch hash
  `4afc760cd89eb9fd0efbf15d68ac90623b7813680df783ecbc19be1cdd64e9c5`;
  revised style-board hash
  `57d936f9733792ee6217ca5b1066440b2d775b3c477a75ce0c7e621f6a444544`;
  contact-sheet hash
  `b045b97d0ee30d58f77616bdc22866e218f0031ca13f975709aca6f87d5e09b6`.
  The stock-only board remains preserved under
  `style_board/revisions/stock-only-v1`; the first generated revision remains
  under `style_board/revisions/generated-folio-1-3-v1`. Folios 4 and 5 enforce
  `usage: background_only`: deterministic excerpt, locator, citation, route,
  dates, and locations remain composited above the generated world.
  Generated-visual validation passed; focused documentary visuals returned
  `14 passed`; complete video-engine tests returned `225 passed`; complete
  repository tests returned `657 passed`.

### T21: World-first Gate A animatic revision
- Status: completed
- Owner: parent
- Depends on: T20 and operator Visual Direction approval
- Write set: documentary animatic composition, focused tests, ignored runtime
  evidence, this PRP
- Acceptance: every documentary function begins with its approved
  style-board world and adds deterministic evidence, map, concept, document,
  or chapter overlays; only archival portraits may substitute a selected
  rights-reviewed asset; the opening creates battlefield/institution contrast
  cuts; unsupported relationship claims render as an explicit evidence field
  without a fabricated graph; the approved style-board and storyboard hashes
  remain unchanged; Gate A remains pending.
- Validate: focused animatic/editorial/documentary tests, complete video-engine
  and repository suites, Remotion typecheck/build, Gate-A preflight, PRP
  validation, and `git diff --check`.
- Evidence: the automatically produced placeholder-heavy animatic is preserved
  under `animatic/revisions/pre-world-first-v1`. Revised preview SHA-256
  `ebe6fca641efb10c05b014d75e952de2eeaef5fd2beea1c58b6e02f6e110df99`;
  motion contact-sheet SHA-256
  `97bb82081608dc27fd637d32661cf7498c86841a074f99fd011411517ca920af`;
  review-packet SHA-256
  `9622685578dcaa8993f057e0c2719a3e360bb9c693ce6af45ae209e8140bede9`.
  The draft contains 138 editorial beats and 137 cuts across 607.999 planned
  seconds; `ffprobe` reports 608.333333 seconds at 854x480, 15 fps, H.264.
  Storyboard guard, storyboard hash binding, style-board integrity, animatic
  validation, and documentary visual QC all returned zero violations. Focused
  verification returned `50 passed`; complete video-engine tests returned
  `232 passed`; complete repository tests returned `664 passed`; Remotion
  typecheck/build, PRP validation, and `git diff --check` passed.

### T22: Higgsfield-informed producer orchestration
- Status: completed
- Owner: parent
- Depends on: T15, T20, T21
- Write set: producer orchestration service, V4.1 coverage/treatment/storyboard
  integration, Higgsfield learning specification, focused tests, ignored
  producer proof artifacts, this PRP
- Acceptance: every semantic coverage slot can compile into a typed producer
  block with a shared art-bible/style-key hash, provider-safe scene/motion/audio
  prompts, still and optional short-motion routes, task-resume boundary, and a
  fail-closed `render_eligible: false` provider candidate. Existing V1–V4.1
  jobs and human gates remain compatible.
- Validate: producer-plan tests, history pipeline integration tests, complete
  video-engine suite, PRP validation, and `git diff --check`.
- Evidence: `producer_plan.v1` is emitted beside Episode 1 editorial coverage
  with 138 blocks and hash
  `1ec8b4f89a0b358f61c1c39dbb816d1ad14c142246278fb2f5791d8d8cef0404`.
  The built-in GPT image generator produced one quarantined woodblock-informed
  learner plate under the authoritative job's `producer-proof/gpt-image`
  directory; it is not evidence or an approved render asset. Focused producer
  and history tests returned `25 passed`; complete video-engine verification
  returned `240 passed` with one existing `audioop` deprecation warning.

## Verification

```powershell
python scripts/prp_validate.py .claude/PRPs/plans/P13-HISTORY-DOCUMENTARY-SYSTEM.plan.md
python -m pytest content/video_engine/tests -q
npm --prefix content/video_engine/editor run typecheck
npm --prefix content/video_engine/editor run build
python -m pytest -q
```

## Evidence And Handoff

Record exact commands, verdicts, artifacts, gate states, deviations, and review findings here.
No provider call, gate approval, publish, registry write, staging, commit, or push is authorized
by implementation alone.

### 2026-07-30 verification checkpoint

- The user-directed episode expansion is contractual: a 600-second target inside a
  480–720-second acceptance band, exactly two native vertical clips, and one
  self-contained chapter subvideo per chapter.
- Manim `0.20.1` imports locally and matches the engine requirement.
  Focused Manim/documentary tests: `11 passed`.
- Complete video-engine tests after independent-review fix: `181 passed`.
- Complete repository tests after independent-review fix: `613 passed`.
- Remotion typecheck and build: passed.
- Independent review: no high-severity blocker; one confirmed Storyboard/Gate-A
  hash-binding issue fixed and covered by a drift regression test.
- Authoritative Episode 1 run:
  `.context/p13-history-v4/jobs/8e97798c-26b3-439a-b131-8746a2f131a3`;
  Research Gate approved by the operator, status `awaiting_visual_gate`, with
  zero provider calls and no later gate action.

### 2026-07-30 Visual Direction checkpoint

- The first generated board was rejected internally before handoff because it
  displayed placeholders instead of resolved assets.
- `DocumentaryStyleBoardService` now selects exact documentary functions,
  resolves only rights-approved local asset IDs, rasterizes reviewed SVG assets
  in a JavaScript-disabled/network-blocked local Chromium context, reserves a
  dedicated citation rail, and renders archive, reconstruction, document,
  map/timeline, and lineage compositions without creator-reference inputs.
- A regression proves the archive role resolves
  `archive-jigoro-kano` rather than reusing the cold-open treatment.
- Focused V4 visual/pipeline verification returned `9 passed`; complete
  video-engine verification returned `181 passed`; the complete repository
  returned `613 passed`.

### 2026-07-30 Gate A checkpoint

- The operator approved Visual Direction at the required minimum 4/5 rubric
  scores; the approval is bound to style-board hash
  `b3d9e3745088ebb595ecbb27f20049da10e5ec1c28009874123624e824bfaddc`.
- Authoritative job:
  `.context/p13-history-v4/jobs/c41aafc0-bf12-4585-b025-394407693871`.
  Research and Visual Direction are approved; Gate A and Gate B remain pending.
- `animatic/motion-preview.mp4` is a 608.266667-second, landscape-draft,
  asset-aware editorial animatic. Its review packet reports 15 scenes,
  607.999 planned seconds, `editorial_ffmpeg`, and zero provider calls.
- The full pre-Gate-A dry run passed Storyboard 2.2 validation, storyboard and
  style-board hash integrity, animatic path/existence checks, and documentary
  visual QC with zero violations. It did not grant Gate A approval.
- Independent review fixes: fail-closed Manim segment containment, immutable
  style-board binding through Gate A, targeted tamper/path tests, correct V4
  documentary QC routing, and adjacent-only treatment-signature repetition.
- Final verification: focused regressions `19 passed`; video engine `187 passed`;
  serial repository suite `619 passed`; Remotion typecheck/build, PRP validation,
  and `git diff --check` passed. One overlapping dual-pytest run produced a
  shared-runtime failure; the isolated test and the serial full suite both
  passed, so serial results are the authoritative evidence.

### 2026-07-30 Gate A revision request

- Gate A remains pending. The operator requested materially greater editorial
  motion: a cut for every identifiable sentence or unique idea, with contrast
  cuts inside semantically opposed clauses where useful.
- Required opening revision: contrast a visibly illustrated battlefield legend
  against a tranquil institution/Kodokan image, then continue the 1882
  historical thread. The illustration is editorial metaphor, labeled as such,
  and is not treated as factual evidence.

### 2026-07-30 revised Gate A candidate

- The paragraph-hold candidate was preserved under
  `animatic/revisions/paragraph-hold-v1`; the first sentence-cut iteration was
  preserved under `animatic/revisions/sentence-cuts-v1`.
- The authoritative `animatic/editorial-beat-plan.json` is hash-bound to the
  unchanged approved Storyboard 2.2 and carries each parent scene, claim,
  citation, start time, duration, visual intent, camera move, and transition.
- Current review packet: 15 narration/claim scenes, 83 editorial beats, 82
  cuts, 607.999 planned seconds, 608.532682 measured MP4 seconds, maximum
  11.902175-second visual hold, `editorial_ffmpeg`, and zero provider calls.
- Visual variety no longer relies on six repeated representative stills:
  deterministic context frames render sentence-specific document excerpts,
  named relationship graphs, place/date maps, concept transforms, and exact
  approved Kano/Maeda portraits. The battlefield and institution frames are
  visibly labeled editorial illustration, not evidence.
- Pre-Gate-A validation returned zero violations without granting approval.
  Final verification: focused revision tests `17 passed`; complete video
  engine `192 passed`; serial repository suite `624 passed`; Remotion
  typecheck/build passed.

### 2026-07-30 Branded Literature revision request

- Gate A remains pending and the sentence-cut candidate is retained only as
  revision evidence.
- The requested identity is **Branded Literature**: deadpan writing and
  purposefully low-effort 2D comedy create the recurring brand voice;
  historical comic blocks carry narrative reconstruction; historical archive
  and document blocks carry evidentiary weight.
- The mode contrast is structural, not random decoration:
  `comic aside → historical comic → archive proof` or
  `popular simplification → illustrated complication → sourced conclusion`.
- The relationship frame containing `date / mean / every / older` is rejected
  evidence. Those are extracted words, not historical entities or
  relationships.

### 2026-07-30 Branded Literature Visual Direction candidate

- New immutable art direction:
  `content/video_engine/configs/art_bibles/combat-history-branded-literature-v1.json`;
  hash `47ffc76f0d010edcdf73cfefc1198847cb68afb154747bd7a82ea05d0be8490d`.
- New authoritative job:
  `.context/p13-history-v4/jobs/23a1cc20-54fa-4f7e-940a-de6c88f2da2e`.
  The unchanged research hash
  `72660fc3eda71b8c13d7e1aa345e65aed4e3700397311be554ff97cd011a1aef`
  retains the operator's Research Gate approval. Visual Direction, Gate A, and
  Gate B remain pending.
- Review artifact:
  `style_board/style_board.png`; style-board hash
  `79a80ca1e4c6559931c983aa4b89bf8c438c78c635e3b308c00bce8c5aa263b9`;
  contact-sheet hash
  `2bded38803410885eecb1a522f1fa079330fbc2068bf605ff403a15602dbad3b`.
- The board demonstrates the structural rhythm: crude myth joke and correction,
  authored three-panel historical comic, rights-reviewed Kano archive,
  citation-bearing document close-up, illustrated migration map, and typed
  `Jigoro Kano — founded (1882) → Kodokan` /
  `Mitsuyo Maeda — taught in → Belém` relationships.
- Verification: focused revision tests `29 passed`; complete video engine
  `197 passed`; serial repository suite `629 passed`; Remotion typecheck and
  build passed. No paid provider, narration, publish, registry, staging,
  commit, or push action occurred.

### 2026-07-30 Production-profile fork candidate

- The operator rejected atom-by-atom synthesis and requested a coherent clone
  followed by explicit modification. The selected baseline is the closest
  supplied product analogue: the long-form illustrated-history production
  grammar reviewed from the two `Historically` references.
- Research-only profile:
  `configs/production_profiles/longform-illustrated-history-v1.json`; hash
  `6762c8c43e8d80aef7e0b8b39dc2cb5d5f77e46e259135cdc5fed0a4fab3cd35`.
  It preserves composition, limited-animation economics, measured edit
  cadence, visual hierarchy, and sound hierarchy. It forbids rendering source
  media, source assets, exact characters, maps, titles, scripts, jokes, logos,
  and frames.
- Derived art direction:
  `configs/art_bibles/combat-history-longform-cutout-fork-v1.json`; hash
  `e588e5d262b5de173022c34ecaa6e24d39f3ad447500dc13a44545ccbd62c559`.
  Its differentiators are an original angular cutout cast, BJJ-specific
  environments and props, green evidence rails, red correction stamps,
  numbered folios, citation proof blocks, and map-line-to-editorial-rule
  transitions.
- Authoritative job:
  `.context/p13-history-v4/jobs/b1a831fe-d6f3-45d2-9a4d-1739ed5abf2e`;
  status `awaiting_visual_gate`. Style-board hash
  `700e9d4973f2dc98c189b80934adfef7eb3a74c7306cd1bcb1f3f8baef82dab1`;
  contact-sheet hash
  `9ea508a37e03165bdeede58680c80267740086bfaec4631898a373e443fd97d8`.
  Research remains approved; Visual Direction, Gate A, and Gate B remain
  pending.
- Verification: focused tests `30 passed`; complete video engine `198 passed`;
  serial repository suite `630 passed`; Remotion typecheck/build passed. No
  paid provider, narration, publish, registry, staging, commit, or push action
  occurred.

### 2026-07-30 Living Editorial V4.1 Asset Selection checkpoint

- Pipeline `4.1`, Storyboard `2.3`, `editorial_coverage.v1`, the Asset
  Selection Gate, provider-reference/flow contracts, deterministic still
  motion, direct Magnific REST stock discovery, and post-gate asset promotion
  are implemented.
- Authoritative job:
  `.context/p13-history-v4-1/jobs/2265aa0c-149f-48d2-8804-f28b488387e8`;
  status `awaiting_asset_gate`. The unchanged research hash
  `72660fc3eda71b8c13d7e1aa345e65aed4e3700397311be554ff97cd011a1aef`
  retains the operator's approval.
- The packet contains 138 semantic coverage slots, 38 stock slots, 69
  quarantined Magnific previews, 38 local fallbacks, and 107 total candidates.
  The operator-confirmed Premium entitlement records included stock downloads
  and a 100-download/day cap; approving at most one candidate per slot remains
  under that cap. No full-resolution stock asset has been downloaded.
- Independent review findings were addressed. Final verification: focused
  tests `30 passed`; video-engine suite `214 passed`; complete repository suite
  `646 passed`; Remotion typecheck/build, PRP validation, and
  `git diff --check` passed.

### 2026-07-30 theme-constrained stock revision

- The earlier asset packet is retained as rejected evidence. Its abstract
  queries (`older`, `date`, `starting point`, and generic `travel`) explain the
  senior-couple, golf, ruin, hotel, and booking/immigration mismatches.
- Stock is no longer assigned by a five-beat rotation. The router selects a
  finite visual archetype first; graphs, evidence documents, chapter cards,
  approved portraits, and distance maps never enter provider search.
- Candidate titles and catalog metadata must satisfy each archetype's required
  facets. Provider resource IDs and perceptually near-identical previews are
  unique across the whole batch. A failed search retains the authored local
  fallback instead of weakening relevance.
- Authoritative revision job:
  `.context/p13-history-v4-1/jobs/6b3c24bc-87e9-45fa-bdfc-b0b2c0058904`;
  status `awaiting_asset_gate`. It contains 138 coverage slots, 19 stock slots,
  18 unique Magnific previews, and 19 local fallbacks. The filter rejected 341
  theme mismatches and 15 duplicates before review. Premium entitlement and
  the 100-download daily ceiling are bound separately; no full-resolution
  download occurred.
- Verification: focused stock/coverage/pipeline tests `19 passed`; complete
  video-engine tests `218 passed`; complete repository tests `650 passed`;
  Remotion typecheck/build, PRP validation, and `git diff --check` passed.

### 2026-07-30 historical-martial and Visual Direction checkpoint

- Whole-word concept matching removed the last false-positive route:
  `scholarship` no longer triggers the travel term `ship`.
- `historical_martial_archive` now searches `historical judo` and
  `historical martial arts` independently from contemporary training b-roll.
  Catalog results must match both the martial subject and a period/archive
  facet. The current catalog produced no qualifying assets, so the pipeline
  retained verified Kano/Maeda archives and authored fallbacks.
- The operator authorized continuation through Asset Selection. Three assets
  were promoted at zero cost: one judo-training cut-in, one BJJ/grappling
  cut-in, and one historical-ship cut-in. Premium entitlement remains capped
  at 100 downloads/day.
- Authoritative job:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080`;
  status `awaiting_visual_gate`. The revised six-frame board resolves both
  project-local archives and job-local selected stock. Style-board hash
  `04b7bd1cbb896ed4290420957ae3823cc7535f09916482a218e4d0be0f996138`;
  contact-sheet hash
  `777520cf7971421b013e6178c269ff3cb333ccdf7b0892b25c0966029c784ab1`.
- Verification: focused routing/style/animatic tests `33 passed`; complete
  video-engine tests `221 passed`; complete repository tests `653 passed`;
  Remotion typecheck/build, PRP validation, and `git diff --check` passed.

### 2026-07-31 Higgsfield learnings and Option A producer orchestration

- Official Higgsfield explainer guidance was distilled into the durable
  [`12-HIGGSFIELD-EXPLAINER-LEARNINGS.md`](../../../docs/content-video-engine/12-HIGGSFIELD-EXPLAINER-LEARNINGS.md)
  specification: shared style key, one typed block per narration beat, silent
  provider clips, audio-first sequencing, one clear action, task-ID retries,
  and human review before promotion. No Higgsfield MCP or CLI dependency was
  added.
- V4.1 now compiles `producer_plan.v1` beside editorial coverage. The
  authoritative job
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080`
  contains 138 typed producer blocks in
  `producer_plan.json` with hash
  `1ec8b4f89a0b358f61c1c39dbb816d1ad14c142246278fb2f5791d8d8cef0404`.
  Original illustration slots route to GPT image/Magnific still producers and
  optional Magnific Kling/Higgsfield motion producers; archives, stock,
  documents, maps, graphs, and typography retain local deterministic fallbacks.
- The producer plan carries the art-bible hash and abstract style atoms into
  beat-level treatments/storyboards while keeping provider output
  `render_eligible: false`. Remotion remains the narration/caption/citation/
  credit editor; Manim remains the deterministic diagram renderer.
- Option A proof: the built-in GPT image generator produced and copied the
  quarantined candidate
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/producer-proof/gpt-image/woodblock-learner-plate.png`
  (SHA-256
  `a2005332a1b9203dd0439b3343448394ef70cad0bd03adf559ea674a2e2d4228`).
  It uses an original woodblock-informed editorial comic language with a
  fictional learner, clean caption space, and no historical likeness or
  factual text. It remains pending human review and is not in the asset
  manifest.
- Current environment capability is explicit: built-in GPT image generation
  is callable; no GPT video-generation tool is exposed in this session. The
  existing Magnific Nano Banana 2 still proof and Kling 2.5 motion proof remain
  provider candidates with pricing/entitlement recorded as unverified by the
  API wrapper.
- The bounded Option A motion pass completed from the GPT plate through
  Magnific Kling 2.5 Pro: one provider call, task
  `f93964e7-5314-45e0-a4e5-cbe1e5a939f4`, 10.04 seconds at 1916x1080/24fps,
  output hash
  `dda2d51c43acc347aa923839d4c72e08202f4123d48d729fc35bc9ab63330e4a`.
  Manifest:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/producer-proof/magnific-kling-output/manifest.json`.
  The frame pair shows a restrained push-in and folio-page action; it is
  promising as a producer candidate but remains pending review because the
  provider can still drift facial detail and geometry. The wrapper records the
  `$14` ceiling and `pricing_status: provider_plan_or_api_pricing_not_verified`;
  it does not claim the user's Premium entitlement as an API price.
- Verification after orchestration changes: focused producer/history tests
  `25 passed`; complete video-engine suite `243 passed` with one existing
  `audioop` deprecation warning; complete repository suite `675 passed` with
  the same warning. Remotion typecheck/build, PRP validation, and
  `git diff --check` passed. No publish, registry write, commit, or push.

### 2026-07-31 world-first visual revision

The first V4.1 animatic made three deterministic functions visibly weaker than
the GPT/Nano-generated plates. The implementation now supports a review-only
world-first revision without mutating the approved active board:

- `generated_visual_candidates.v1` accepts `lineage_concept` and
  `concept_mechanics` roles plus `motion_selected`.
- Producer planning routes `map`, `graph`, `document`, and concept sources to
  the GPT image/Nano still path with explicit deterministic overlay ownership.
- Remotion uses generated woodblock plates for migration, lineage, and concept
  beats while keeping reviewed places, dates, names, verbs, captions, and
  citations local and hash-bound.
- A new contact sheet and animatic revision were produced under the Episode 1
  job. The existing Visual Direction and Gate A snapshots remain unchanged;
  this revision requires a fresh Visual Direction review before it can replace
  the active board.

Evidence:

- Candidate batch:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_visuals/revisions/generated-world-first-v1/candidate_batch.json`
- Style board contact sheet:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/style_board/revisions/generated-world-first-v1/style_board.png`
- Style board hash:
  `e932344ceee80ec39d75ade26a648b4d11bb13cf820dfff1d54598d34967d160`
- Motion contact sheet:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/generated-world-first-v1/motion-contact-sheet.png`
- Review animatic:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/generated-world-first-v1/motion-preview.mp4`
- The revision contains 138 editorial beats across 607.999 seconds and
  reports generated world plates for `migration_map_timeline`, `lineage_graph`,
  and `concept_mechanics_cutaway`. No provider output is render-eligible.

### 2026-07-31 generated-image-per-block revision

The prior revision still allowed deterministic folios to fill most beats. A
new review-only lane now compiles one original generated plate for every unique
narration block (continuation slots share the same plate rather than producing
noun-per-cut noise). The Episode 1 coverage contains 138 slots and 71 unique
blocks, so the generated-image target exceeds the ten-minute minimum of 60.

Implementation and evidence:

- Compiler/validator:
  `content/video_engine/src/services/generated_block_images.py`
- Plan (71 blocks, coverage hash bound):
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_blocks/plan.json`
- Candidate batch (71 local SHA-256-bound plates):
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_blocks/batch.json`
- Batch artifact hash:
  `71c360cba63a7b6b1f29f054340a14d66cfe4fd477e2c6e80adc4753a328f924`
- Generated source originals remain under:
  `C:\Users\Snipe\.codex\generated_images\019fab7f-09a7-7353-b2e1-f5c0b8871a1e`
  and are copied into the job only as review artifacts.
- Generated-block style board:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/style_board/revisions/generated-blocks-v1/style_board.png`
- Generated-block animatic contact sheet:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/generated-blocks-v2/motion-contact-sheet.png`
- Generated-block review animatic (138 beats, 607.999 seconds):
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/generated-blocks-v2/motion-preview.mp4`
- CLI validation passed with `block_count: 71` and
  `one_generated_plate_per_block: true`.

The active board and Gate A snapshot remain unchanged. This revision is
parked for a fresh Visual Direction review; generated pixels remain
non-evidence and non-renderable until the operator approves the new board.
Focused tests now pass `37` with one existing `audioop` deprecation warning.

### 2026-07-31 plate-to-video motion handoff

The generated plates are now ready for an image-to-video producer instead of
the generic zoom/pan fallback. `plate_motion_plan.v1` compiles one silent
Magnific/Kling-compatible request per generated block and binds each request to
the source SHA-256, narration excerpt, semantic function, and one-action motion
recipe. The animatic can consume a completed, quarantined motion manifest and
composite Remotion's captions/citations over the provider clip. Without a
manifest it reports `motion_mode: deterministic_fallback`.

Evidence:

- Motion plan:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/generated_blocks/motion-plan.json`
- Motion plan hash:
  `3c761769cd907278ac2d633066485cd7d603d0330a280b968ec1c08ae0cdb665`
- CLI validation passed with `item_count: 71`.
- Tests: `20` focused plate-motion/animatic tests passed.

At the time this slice was recorded, no provider motion calls had been made.
The active board and Gate A snapshot remain unchanged until a motion sample is
reviewed.

### 2026-07-31 Kling API motion sample

The operator authorized a bounded API test after the browser upload path proved
unreliable. One generated block was submitted through the existing Magnific
REST boundary to Kling 2.5 Pro at the selected 10-second duration; no other
blocks were submitted.

Evidence:

- Provider manifest:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/provider/kling-api-10s/manifest.json`
- Manifest hash:
  `7fade32eb66bac3a753760e9408893c3d454e7d9760f2525f015bbd862d59a63`
- Provider task:
  `4858f1da-bef0-4d21-bf13-4377841baacd`
- Output:
  `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/provider/kling-api-10s/image-block-001-history-001-unit-01-part-01.mp4`
- Output SHA-256:
  `76fd1567e58ba60c0ba92fe2f9caaeac651d41e805dacdf777477bb49373ea38`
- Media verification: H.264, 1176x1764, 24fps, 10.041667 seconds.
- CLI manifest validation passed with `item_count: 1`.

The provider candidate remains `render_eligible: false` and `review_status:
pending`. The manifest records the `$14` request ceiling and unverified API
pricing; it does not authorize a 71-clip run.

### 2026-07-31 Google Flow character-builder slice

The recurring-cast path now has a provider-neutral, hash-bound prompt packet for
Google Flow's character builder with Nano Banana Pro. It is opt-in and does not
change legacy V1–V4 jobs.

Evidence:

- Schema: `content/video_engine/configs/flow_character_pack.schema.json`
- Validator/service: `content/video_engine/src/services/flow_character_pack.py`
- Episode-1 packet: `content/video_engine/projects/history-of-bjj/episode-1-flow-character-pack.json`
- Specification: `docs/content-video-engine/13-GOOGLE-FLOW-CHARACTER-BUILDER-SPEC.md`
- CLI: `python content/video_engine/cli.py validate-character-pack content/video_engine/projects/history-of-bjj/episode-1-flow-character-pack.json`
- Validation result: `valid: true`, `artifact_hash: 45e15f899301567e0165696bb47dfdfb971a52df9bccfceaecb0fe67437019df`, `character_count: 4`, `render_eligible: false`
- Focused tests: `22 passed`

The packet contains a fictional learner, Kano and Maeda illustrated
reconstructions, and a named-person-free Brazilian composite. The operator
selected the Flow account and authorized one bounded Nano Banana Pro
character-sheet generation. The resulting learner sheet was reviewed and
approved; no video generation or additional character generation was requested.

Evidence from the bounded generation:

- Provider media ID: `5d020540-a2e5-4df6-bbc2-66bfd6cc2797`
- Local review image:
  `content/video_engine/projects/history-of-bjj/assets/quarantine/flow/learner-character-sheet-nano-banana-pro-20260731.png`
- Image SHA-256:
  `169f18a87d7a186fa4aba2283a10654a269eaf944f69abfa14bcdbb98a55b0c5`
- Output record:
  `content/video_engine/projects/history-of-bjj/assets/quarantine/flow/learner-character-sheet-nano-banana-pro-20260731.json`
- Dimensions: `1376x768`

Promotion evidence:

- Approved manifest asset: `flow-learner-character-sheet-20260731`
- Promoted local asset:
  `content/video_engine/projects/history-of-bjj/assets/generated/flow/learner-character-sheet-nano-banana-pro-20260731.png`
- Updated asset-manifest hash:
  `2bb7590ca7d0e6fb402151b34d0779f6692230d3eeddeec9d27b5c50f5125997`
- Asset CLI validation: `valid: true`
- Episode validation after promotion: `valid: true`, artifact hash
  `65d2855fc72b82a6c30154b3cc2851873dbc957db4981857d65dabd81dcabda6`

The original provider output record remains quarantined and non-renderable;
only the separately hashed, operator-approved manifest asset is render-eligible.

### 2026-07-31 Google Flow cast expansion

The remaining three approved cast prompts were generated one at a time with
Nano Banana Pro. The operator reviewed and approved all three sheets, so each
was copied into the generated-asset directory and bound into the episode
manifest. The original provider records remain preserved in quarantine; no
animation or episode rendering was performed.

| Character | Provider media ID | Promoted output | SHA-256 |
| --- | --- | --- | --- |
| Kano reconstruction | `ef3038b4-e868-4dc9-a599-99a8eab0d299` | `content/video_engine/projects/history-of-bjj/assets/generated/flow/kano-reconstruction-nano-banana-pro-20260731.png` | `62162d8d629074340b9ed0132df1f328cecf0bb81ba4d6afc1c202aa73f23a41` |
| Maeda reconstruction | `7e841b23-24fa-4ac5-9bb6-fefda659ac23` | `content/video_engine/projects/history-of-bjj/assets/generated/flow/maeda-reconstruction-nano-banana-pro-20260731.png` | `a7253b9f42f359a32291e82a204b765109d37ae767de8abfd8ce932edb7d58ec` |
| Brazilian bridge composite | `b02e4131-4172-409d-ba78-617e9b96fe53` | `content/video_engine/projects/history-of-bjj/assets/generated/flow/brazilian-bridge-composite-nano-banana-pro-20260731.png` | `8a6b17d32b5e7e64c583b1eab8f248af4665120b45efb85108b5fc5226580e65` |

Each output has a matching `flow_character_output.v1` record with
`source_kind: generated_original` and an explicit illustration/reconstruction
label. The provider records remain `render_eligible: false`; only the
separately hashed manifest assets are render-eligible.

Final promotion hashes:

- Character-pack artifact hash: `98f1db351edaf0276af7dd7b9ce13ac0f5654195db0b9b817d8df74eca4d9b02`
- Asset-manifest hash: `208211b443673bdadb1395f9a402e2b987e91eb7e6eb3d586adb20cbe43a4152`
- Episode artifact hash after final cast promotion: `de82e26958a5da0521d063ffbac03c01e139686f5c00a71497a8bf9734c01be5`

### 2026-07-31 character-in-scene motion proof

The editor now accepts reviewed character plates as timed layers over a
documentary shot. The background stays fixed while approved cast plates enter,
react, and hand the frame back to the historical reconstruction. This is the
first bounded proof of the approved Flow cast moving through an episode scene;
it is not a full-episode render or provider video call.

Evidence:

- Treatment: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-sample/treatment.json`
- Output: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-sample/character-motion-sample.mp4`
- Output SHA-256: `7622A382B93C5AA3BC93F1D8696B62F1D01A30F97DEBC80751DE59926FDF8EA1`
- Review frames: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-sample/frames/`
- Sample manifest: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-sample/manifest.json`
- Editor contract: `content/video_engine/editor/src/types.ts` and `content/video_engine/editor/src/Documentary.tsx`
- Remotion typecheck: passed (`npm run typecheck`)
- Provider calls: none; the sample uses only local copies of approved manifest assets.

### 2026-07-31 full cast-enabled production estimate

The approved cast is now compiled into a complete episode producer plan without
making provider calls. The plan covers 138 editorial blocks: 121 remain local
Remotion/Manim work and 17 original-illustration blocks are eligible for
optional ten-second Flow ingredient clips. Four character sheets are reused;
no new character generation is budgeted.

Evidence:

- Cast-enabled plan: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-production/producer_plan.with-cast.json`
- Plan hash: `c85e8bc8e3dbd25b72a5ce4e959a2c88da9a94d7f7f2655eae99120b442c7f32`
- Cost estimate: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-production/cost-estimate.json`
- Local-only incremental estimate: `$0` with cached narration, `$0.9106` uncached ElevenLabs narration.
- Signed-in Google Flow credit history showed `1,050` credits available (`1,000` plan credits plus `50` daily complimentary credits) and no recent activity before this pricing check.
- The Flow generation menu showed 10-second Ingredients-to-Video at `15` credits for Omni Flash x1 or `20` credits for Veo 3.1 Fast x1. The 17 optional provider blocks therefore cost `255` or `340` credits respectively, leaving `795` or `710` credits from the observed balance.
- A provider-every-block route would require `2,070` Omni Flash credits or `2,760` Veo 3.1 Fast credits for all 138 blocks and remains rejected by budget.
- Magnific/Kling fallback ceiling remains `$238` for 17 calls at the configured `$14` ceiling each; `$14` is an old approval ceiling, not a Google Flow block price or an invoice.
- No Google video generation was submitted during the pricing observation; the credit debit is a preflight UI value.

The next protected action is selecting the 17-clip Omni Flash or Veo scenario
and authorizing a bounded batch; the existing `$14` ceiling does not need to be
applied to Google Flow credits.

### 2026-07-31 Google Flow ten-second pricing/motion test

One bounded test was submitted through the signed-in Google Flow UI using an
existing Episode 1 project plate, Ingredients mode, Omni Flash, 16:9, 10
seconds, and x1. The UI preflight showed `15` credits; Google One credit history
recorded exactly `-15`, reducing the balance from `1,050` to `1,035` (daily
complimentary credits from `50` to `35`). The provider job failed at 11% and
produced no downloadable output, so it remains non-renderable evidence. No
second attempt or batch was submitted.

Evidence:

- Test manifest: `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/character-motion-production/google-flow-10s-test/manifest.json`
- Manifest SHA-256: `c46b1e46b6113e076c271db4abda1f1e1ea585bdfa68cd7d4ecf8a681ef56918`
- Flow edit: `https://labs.google/fx/tools/flow/project/10984a51-81dd-49f9-928c-70ff31bb8751/edit/d1897700-34d7-45f8-b431-01a6fc4be092`
- Credit history: `https://one.google.com/ai/activity?utm_source=flow&utm_medium=web&utm_campaign=flow_ai_credits_page&dm=1&g1_landing_page=0`

The failure does not change the observed unit price. A 17-clip Omni Flash
batch remains `255` credits; a Veo 3.1 Fast batch remains `340` credits. After
this test, the account has `1,035` credits, so a fresh 17-clip Omni Flash batch
would leave `780` credits. The batch is not authorized until the failure cause
is resolved or the operator chooses to proceed with a known retry budget.
