---
id: P13-EDITORIAL-MOTION-SYSTEM
title: P13 Deterministic Editorial Motion System
status: review
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-01
updated: 2026-08-01
---

# P13 Deterministic Editorial Motion System

## Summary

Replace the documentary fallback's generic whole-plate zoom and pan behavior
with an explicit editorial motion plan executed by Remotion. The system must
edit narration into intentional shots; it must not merely animate every image.

The current engine already has the right upstream and downstream boundaries:
Storyboard 2.3, `editorial_coverage.v1`, `editorial_beat_plan.v1`, living-scene
bundles, canonical narration timings, approved assets, Remotion composition,
Manim diagrams, and quarantined provider clips. This slice adds the missing
contract between approved narration beats and the renderer.

The initial acceptance proof uses existing approved assets and matching local
audio only. Magnific, Flow, Higgsfield, and other generated motion remain
optional shot-level sources and are not called during this PRP.

## Intent And Acceptance

The intent is to make the local editor responsible for cinematography and
rhythm while reserving paid generation for organic motion that deterministic
layers cannot express.

Acceptance requires:

- One hash-bound `editorial_motion_plan.v1` covers a continuous 30–60 second
  excerpt without timing gaps or overlaps.
- The continuous canonical narration and word timings own the clock. Existing
  ten-second audio/provider blocks remain cache and delivery units, never
  editorial shot units.
- Each shot declares its purpose, scale, focal point, layers, hold/move/settle
  phases, information reveal, transition reason, and provider-motion need.
- A camera move alone never satisfies the living-scene visual-event rule.
- Remotion owns cuts, layered transforms, captions, citations, fact surfaces,
  and final timing. Manim supplies deterministic diagram/map clips or layers;
  FFmpeg performs inspection and encoding support rather than directing shots.
- Static shots are genuinely static. Moving shots use bounded easing, preserve
  safe zones, and settle before a cut unless `cut_on_motion` is explicit.
- The proof demonstrates shot hierarchy, meaningful stillness, subject or
  localized environmental motion, deterministic evidence, and at least one
  motivated transition.
- The proof is revision-only, uses zero provider calls, and leaves active Gate
  A artifacts byte-for-byte unchanged.
- Structural QC passes and a human watch-through approves the new edit before
  any paid motion bakeoff is proposed.

## Scope

- History V4/V4.1 documentary and P13 living-scene revision renders.
- An editorial motion plan and a small pacing-recipe contract.
- Compilation from the existing beat plan, scene bundles/flow graph, approved
  asset IDs, and canonical word timings.
- Remotion shot sequencing, focal-point camera transforms, layer animation,
  motivated transitions, and diagnostic overlays.
- Revision-only CLI/service integration and fail-closed QC.
- One A/B proof using the same narration excerpt and source assets: current
  deterministic fallback versus the new editorial render.
- Provider need classification per shot: `none`, `preferred`, or `required`.

## Not Building

- No full Episode 1 render or episode-scale motion batch.
- No new narration synthesis or paid image/video call.
- No automatic imitation or frame ingestion from reference creators.
- No per-frame LLM decisions and no renderer-authored editorial choices.
- No second narration clock and no forced cut every ten seconds.
- No generic requirement that every shot move.
- No wholesale FFmpeg filter-graph editor or full rewrite of the existing
  Remotion project.
- No mutation of Storyboard 2.3, Research/Visual approvals, active Gate A
  artifacts, provider manifests, credentials, or signed URLs.
- No provider clip promotion, publication, registry write, commit, or push.

## Human Gates

1. **Plan Gate** — approve this PRP and its contract/renderer ownership.
2. **Editorial Motion Proof Gate** — watch the 30–60 second A/B proof and score
   camera stability, focal clarity, shot hierarchy, cut motivation, pacing,
   evidence legibility, and continuity at least 4/5 each.
3. **Provider Motion Spend Gate** — only after the proof, separately authorize
   a bounded bakeoff for shots classified `preferred` or `required`.
4. **Living Scene Proof Gate** — remains owned by the parent
   `P13-LIVING-SCENE-COMMUNICATION-SYSTEM` PRP.

Plan approval does not approve provider spending, Gate A, or episode production.

## Mandatory Reads

- `AGENTS.md`
- `docs/AGENT_START_HERE.md`
- `docs/runbooks/PRP_EXECUTION.md`
- `.claude/PRPs/plans/P13-LIVING-SCENE-COMMUNICATION-SYSTEM.plan.md`
- `docs/content-video-engine/03-SYSTEM-ARCHITECTURE.md`
- `docs/content-video-engine/10-HISTORY-DOCUMENTARY-EDITORIAL-SPEC.md`
- `docs/content-video-engine/15-LIVING-SCENE-COMMUNICATION-LANGUAGE.md`
- `content/video_engine/src/services/editorial_beats.py`
- `content/video_engine/src/services/living_scenes.py`
- `content/video_engine/src/services/history_narration.py`
- `content/video_engine/src/services/animatic.py`
- `content/video_engine/editor/src/types.ts`
- `content/video_engine/editor/src/Documentary.tsx`
- `content/video_engine/tests/test_animatic.py`
- `content/video_engine/tests/test_editorial_beats.py`

## Execution Path

```text
approved Storyboard 2.3 + editorial_coverage.v1
+ editorial_beat_plan.v1
+ approved scene_bundle.v1 / scene_flow_graph.v1
+ approved asset map
+ hash-matched canonical narration word timings
→ compile editorial_motion_plan.v1
→ validate timing, paths, hashes, pacing, and transition motivation
→ resolve approved asset IDs job-locally
→ Remotion editorial composition
   ├─ stable world and depth layers
   ├─ character/prop action
   ├─ localized ambient action
   ├─ deterministic information reveal
   ├─ restrained camera action
   └─ cuts, captions, citations, and audio
→ FFprobe/structural QC + diagnostic render
→ A/B review packet
→ Editorial Motion Proof Gate
→ optional separately authorized provider bakeoff
```

The compiler may subdivide a narration beat into multiple visual shots, but it
must preserve the beat's claim/citation binding and exact audio interval. A shot
may cross a ten-second cache-block boundary because the continuous narration is
the render clock; provider requests may not silently redefine that timing.

### `editorial_motion_plan.v1`

The plan is one job-level artifact, not one unconnected JSON document per shot:

```json
{
  "schema_version": "editorial_motion_plan.v1",
  "source_storyboard_hash": "...",
  "source_beat_plan_hash": "...",
  "scene_bundle_hashes": ["..."],
  "scene_flow_graph_hash": "...",
  "asset_map_hash": "...",
  "audio_manifest_hash": "...",
  "pacing_recipe_hash": "...",
  "duration_s": 42.4,
  "shots": [
    {
      "shot_id": "ep1-proof-001-b",
      "parent_beat_ids": ["coverage-slot-001"],
      "parent_scene_bundle_id": "archive-study",
      "start_s": 2.2,
      "duration_s": 1.8,
      "word_range": {"start_index": 9, "end_index": 16},
      "purpose": "reveal",
      "shot_scale": "medium_detail",
      "focal_point": {"x": 0.62, "y": 0.44},
      "layers": [
        {"asset_id": "world.archive-study", "role": "world"},
        {"asset_id": "prop.ledger", "role": "prop"}
      ],
      "subject_action": "ledger_opens",
      "ambient_actions": ["lamp_flicker"],
      "information_reveal": "none",
      "camera": {
        "kind": "push_settle",
        "amount": 0.018,
        "easing": "smoothstep",
        "hold_in_s": 0.25,
        "move_s": 1.15,
        "hold_out_s": 0.40
      },
      "transition_out": {
        "kind": "match_cut",
        "reason": "lamp glow matches paper highlight",
        "motif_id": "motif.lamp-to-paper"
      },
      "audio_bridge": "continuous_narration",
      "provider_motion": {
        "requirement": "none",
        "fallback": "local_layer_motion"
      },
      "overlay_ids": ["citation.claim-001"],
      "uniqueness_signature": "medium_detail:ledger:push_settle:highlight"
    }
  ],
  "artifact_hash": "..."
}
```

Renderer-facing plans contain approved asset IDs, not arbitrary source paths.
All paths resolve through the existing job-local asset boundary and are checked
for containment and content hash before rendering.

### Small v1 vocabulary

- Purpose: `hook`, `establish`, `reveal`, `explain`, `detail`, `reaction`,
  `payoff`, `chapter_reset`.
- Scale: `wide`, `medium`, `medium_detail`, `close`, `insert`.
- Camera: `locked`, `push_settle`, `pull_settle`, `lateral_reveal`,
  `foreground_parallax`, `cut_on_motion`.
- Transitions: `hard_cut`, `match_cut`, `paper_wipe`, `chapter_fade`.
  `crossfade` is allowed only for a declared time/place change.
- Action ownership: `subject`, `ambient`, `information`, `camera`.

Unknown values fail validation. Production defaults are `locked`, hard cut,
and no hidden transform.

### Pacing recipe

`editorial_pacing_recipe.v1` stores abstract channel grammar only: preferred
shot range, maximum repeated scale/motion signatures, transition policy,
motion-density ceiling, and chapter reset behavior. It cannot contain creator
names, source frames, URLs, or “in the style of” renderer instructions.

## Patterns To Mirror

- Use `history_contracts.canonical_sha256`; do not add another hash format.
- Extend `compile_editorial_beat_plan` outputs; do not duplicate sentence or
  claim segmentation.
- Mirror `render_documentary_revision` path containment and revision-only
  behavior.
- Extend the existing Remotion `DocumentaryComposition`, asset resolution,
  character layers, citation rail, and safe zones.
- Mirror `scene_bundle.v1` and `scene_flow_graph.v1` transition motifs.
- Treat `plate_motion_manifest.v1` clips as optional layer assets only after
  their existing review/promotion rules pass.
- Keep generated text out of images and provider motion.

## Task Slices

### T1: Establish the contract and baseline evidence
- Status: completed
- Owner: parent
- Depends on: Plan Gate
- Write set: `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md`, `docs/content-video-engine/README.md`, `content/video_engine/configs/editorial_motion_plan.schema.json`, `content/video_engine/configs/editorial_pacing_recipe.schema.json`, proof fixture metadata
- Acceptance: specification ownership is indexed; contracts define timing, layers, motion phases, transition reasons, provider need, hashes, and review rules; the existing fallback excerpt and hashes are preserved as baseline evidence.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md` and schema fixture validation
- Evidence: `docs/content-video-engine/16-EDITORIAL-MOTION-SYSTEM.md`, indexed by `docs/content-video-engine/README.md`; Draft-07-valid `editorial_motion_plan.schema.json` and `editorial_pacing_recipe.schema.json`; `content/video_engine/tests/fixtures/editorial_motion_baseline.json` records the immutable Storyboard, beat-plan, audio-manifest-file, and fallback-preview hashes. Schema and fixture JSON checks passed and PRP validation passed on 2026-08-01.

### T2: Compile and validate editorial motion plans
- Status: completed
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/src/services/editorial_motion.py`, `content/video_engine/tests/test_editorial_motion.py`
- Acceptance: a pure compiler consumes existing beat, scene, asset, and audio contracts; it produces deterministic hashes, exact continuous timing, approved asset IDs, and fail-closed errors for unsafe or incoherent plans.
- Validate: `python -m pytest --import-mode=importlib content/video_engine/tests/test_editorial_motion.py -q`
- Evidence: `content/video_engine/src/services/editorial_motion.py` compiles explicit shot decisions against the canonical word clock, validates all upstream artifact hashes, limits assets to approved IDs, enforces continuous shot/word coverage, and rejects excerpt timing beyond canonical audio. `content/video_engine/tests/test_editorial_motion.py` passed `13 passed in 0.16s` on 2026-08-01.

### T3: Implement the Remotion editorial-motion vocabulary
- Status: completed
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/editor/src/types.ts`, `content/video_engine/editor/src/Documentary.tsx`, new helpers under `content/video_engine/editor/src/`, focused local fixtures
- Acceptance: Remotion executes locked shots, focal-point push/pull settle, lateral reveal, bounded foreground parallax, layer actions, deterministic reveals, motivated transitions, and continuous narration without implicit whole-plate motion.
- Validate: `npm run typecheck` and `npm run build` from `content/video_engine/editor`, plus a low-resolution fixture render
- Evidence: `content/video_engine/editor/src/EditorialMotion.tsx`, `types.ts`, `Documentary.tsx`, and `Root.tsx` implement safe job-local asset/audio resolution, continuous canonical audio, locked/push/pull/lateral/parallax/cut-on-motion camera behavior, hold/move/settle phases, localized layer actions, deterministic overlays, motivated transitions, and diagnostic burn-in without implicit whole-plate motion. Parent verification passed `npm run typecheck`, `npm run build`, and a three-frame 320x180 Remotion render using installed Chrome on 2026-08-01.

### T4: Integrate revision-only compilation and rendering
- Status: completed
- Owner: parent
- Depends on: T2 and T3
- Write set: `content/video_engine/src/services/animatic.py`, `content/video_engine/cli.py`, `content/video_engine/tests/test_animatic.py`, `content/video_engine/tests/test_history_v4_pipeline.py`
- Acceptance: the revision command compiles/validates the motion plan, launches Remotion, writes normal and diagnostic previews, records all source hashes, and cannot mutate active Gate A artifacts.
- Validate: focused animatic/pipeline tests and a fixture-only CLI smoke render
- Evidence: `AnimaticService.render_editorial_motion_revision` and the `compile-editorial-motion`, `validate-editorial-motion`, and `render-editorial-motion-revision` CLI commands validate/hash inputs, copy only promoted local assets plus canonical audio into a revision-local Remotion public boundary, render normal/diagnostic previews, and compare active Gate A hashes before and after. Focused compiler/QC/animatic verification passed `40 passed in 0.65s`; the editor also passed typecheck/build after adding bounded character/prop placement.

### T5: Add editorial stability and continuity QC
- Status: completed
- Owner: implementation_luna
- Depends on: T2
- Write set: `content/video_engine/src/guards/editorial_motion_qc.py`, `content/video_engine/tests/test_editorial_motion_qc.py`
- Acceptance: QC rejects timing gaps/overlaps, stale hashes, unsafe asset resolution, undeclared whole-frame movement, excessive repeated signatures, missing settles, unmotivated transitions, provider leakage, and revision-path escape; it never claims cinematic quality from metadata alone.
- Validate: `python -m pytest --import-mode=importlib content/video_engine/tests/test_editorial_motion_qc.py -q`
- Evidence: `content/video_engine/src/guards/editorial_motion_qc.py` validates contract/hash integrity, asset promotion/hash/path containment, revision-only output containment, motion density, scale/signature repetition, whole-frame action ownership, and the zero-provider boundary while explicitly requiring human review. Combined compiler/QC verification passed `21 passed in 2.64s` on 2026-08-01.

### T6: Produce the local A/B editorial-motion proof
- Status: completed
- Owner: parent
- Depends on: T3, T4, and T5
- Write set: job-local `animatic/revisions/editorial-motion-v1/` only
- Acceptance: a 30–60 second hash-matched excerpt renders as baseline, revised preview, diagnostic preview, cut-frame samples, contact sheet, motion plan, and review packet; provider calls equal zero and Gate A hashes are unchanged.
- Validate: FFprobe media checks, QC command, Gate A hash comparison, and complete human review rubric
- Evidence: job-local revision `.context/p13-history-v4-1/jobs/6f02a2f3-6d87-4d46-a6fc-88b034ccc080/animatic/revisions/editorial-motion-v1/`; 40.716-second/10-shot plan hash `3c90fa1b5f95939da81f45361464b2e4376c43f433a862f0c031f6a9db3d525d`; asset-map hash `a223604c6da27cee881cdff5127968d13c7af6fdc1366172e5246f89811e35be`; audio-manifest hash `5e35c5b027c695babe072cb645021dbec0f9d9bda7bb82259fc37f63f016685e`. Baseline, revised, and diagnostic previews are present with SHA-256 `56c97aa13bae4edd72252f79c8c250cc65083254a77d1a0430af1b7d07ebe099`, `18b03e2760b0dc7d61a3bf490d26568d51071f8741a7ba96be3fc6ea1b6aa846`, and `8f93feeaebe1742c0d41b91dcfe5ddcdcccfb6250be9efa193a4650b36f622df`. FFprobe confirms 854x480 H.264 at 15 FPS with AAC narration; revised duration is `40.789333s`, mean volume `-21.3 dB`, and max volume `-4.7 dB`. `cut-samples/`, `shot-stills/`, `contact-sheet.png`, `baseline-contact-sheet.png`, `diagnostic-contact-sheet.png`, `review-packet.json`, and `editorial-motion-proof-gate.json` are present. Structural QC passes, provider calls/cost are `0`/`$0.00`, revision-only output is true, and the renderer-recorded Gate A before/after hashes are identical.

### T7: Perform independent correctness and regression review
- Status: completed
- Owner: reviewer
- Depends on: T6
- Write set: none (read-only review)
- Acceptance: review covers timing authority, hash/path safety, renderer determinism, evidence-layer stability, provider boundaries, Gate A immutability, legacy behavior, and missing tests.
- Validate: findings cite exact files/lines and parent dispositions every actionable item
- Evidence: independent `reviewer` review found two actionable issues. The compiler's next-shot word lookup could raise a raw `KeyError`; it now uses guarded integer extraction for every word-range index and has a missing-index regression test. Repeated `MapNetworkScene` construction could hit a Windows text-SVG file-handle conflict; node and fallback labels now use SVG caching. Reviewer re-review verified both fixes (`23 passed` focused compiler/scene tests and `302 passed` non-render video-engine tests) and reported no remaining actionable issues in the reviewed scope.

### T8: Integrate evidence and stop at the proof gate
- Status: completed
- Owner: parent
- Depends on: T7
- Write set: this PRP, parent living-scene PRP evidence/status, job-local review packet
- Acceptance: focused and full suites pass, Remotion verification passes, exact results and artifact hashes are recorded, and work stops at Editorial Motion Proof Gate without provider spending.
- Validate: commands in Verification plus `python scripts/prp_status.py`
- Evidence: post-review verification passed: focused editorial/history suite `59 passed, 1 warning in 24.77s`; complete video-engine suite `307 passed, 1 warning in 52.42s`; full repository `739 passed, 1 warning in 127.62s`; Remotion `npm run typecheck` and `npm run build` both passed. The only warning is the existing Python 3.13 `audioop` deprecation emitted by `pydub`. The proof gate packet remains `awaiting_human_review`, with blank rubric scores and `approval_granted: false`. No provider call, publication, registry write, staging, commit, or push occurred.

### Proof Gate Revision V2

Operator feedback rejected burned-in English narration, in-scene fact citations,
generic text cards, and information placement over character faces. Revision
`editorial-motion-v2` makes platform captions and credits-only citations the
defaults, adds typed `surface_ink` treatments, and rejects information bounds
that leave frame or overlap character layers. The new proof is under the same
job at `animatic/revisions/editorial-motion-v2/`; plan hash
`4f37ca7499689f4976855a4a622a68b3cee5ba0bb614e5458797091c4167fd54`,
preview hash `dbae7f14230118efeadfdc9808248512f2eab20752f0dbc19cb6b103f4234d50`.
Structural QC and information-surface safety pass, Gate A remains unchanged,
provider calls/cost remain `0`/`$0.00`, focused tests passed `44`, complete
video-engine tests passed `310` with the existing `audioop` warning, and
Remotion typecheck/build passed. V2 is awaiting human proof-gate review.

### Proof Gate Revision V3

Operator feedback found that V2 still optimized decorative overlays instead of
asking whether they should exist. Revision `editorial-motion-v3` removes all
information surfaces, every ledger overlay, every narration-restatement label,
and the redundant interpretive-world label. Only the opening reconstruction
disclosure remains. The sole non-evidence prop is the travel trunk that supplies
journey context; the Kano portrait is verified evidence. The pacing contract now
caps information surfaces at `0` and non-evidence prop-layer occurrences at `1`,
with structural QC enforcement. V3 plan hash is
`918174a91531580d5a0b719f8d39e92290b9d7df8c2051049870cefea8dd8934`;
preview hash is `903b5a2d443fd1138fb2c9f8a36f59c3850a3916538a96c0285860d1a18bf8a7`.
Structural QC passes, Gate A is unchanged, provider cost is `$0.00`, complete
video-engine verification passed `312 passed, 1 warning`, and Remotion
typecheck passed. V3 supersedes V2 and awaits human proof-gate review.

### Proof Gate Revision V4

Operator feedback requested one additional cut at the contrast after
“battlefield legend,” while explicitly preserving the following interior beat.
Revision `editorial-motion-v4` replaces only shot 2 (2.694–4.609 seconds) with
an original nighttime woodblock gate and a right-to-left Kano entrance. Shot 3
remains the approved daytime Kodokan interior, creating a deliberate
night-outside → day-inside progression; all later shots and timings remain
unchanged. The gate is recorded as interpretive illustration and is not
historical evidence. V4 plan hash is
`a9e9553b4b46d33af5a53e624c62fc010299ea8f334894449757e8cdbec8b40f`;
asset-map hash is
`4b8d1613cf61e9c599c2988f7db770224429b747ab9813c4990694857dafc186`;
preview hash is
`6156b515e254247e780853830b180adfcffbcbaa4821d112fb92b3f3593f4557`.
Structural QC passes, active Gate A artifacts remain unchanged, local motion
rendering used zero provider calls/cost, and the requested original gate used
one subscription image-generation call. V4 supersedes V3 and awaits human
proof-gate review.

### Proof Gate Revision V5

Operator feedback requested localized cloud motion and coherent Kano continuity
across the night-exterior → day-interior cut. Revision `editorial-motion-v5`
adds a deterministic translucent cloud layer that moves only `2.4%` across the
upper sky; the gate, courtyard, and camera remain locked. Kano completes his
exterior entrance at `x=.67, y=.17, w=.27, h=.72`, then begins the interior at
the exact same layout and performs a restrained gesture instead of entering a
second time. The transition is recorded as a match-position cut. All later
shots and timings remain unchanged. V5 plan hash is
`50e56021ce82a6d4e3bc6a7beb988e90a1b4385037069c23280e86a0913ccebe`;
preview hash is
`490dee11f8b0ba95f836e7e76ca9171662e32c875e7e9870a62212f40dccdfc7`.
Structural QC passes, Gate A is unchanged, Remotion typecheck passes, and the
focused QC suite passes `12 passed`. Complete video-engine verification passes
`313 passed, 1 warning in 44.07s`; the warning is the existing Python 3.13
`audioop` deprecation from `pydub`. V5 used no provider calls or new image
generation and supersedes V4 at the human proof gate.

### Proof Gate Revision V6

Operator feedback rejected the 13-second paper transition and the 23-second
deletion-only event. Revision `editorial-motion-v6` replaces the effect with a
hard cut to the operator-supplied historical Kodokan image at `13.340s`, then
returns to the existing living interior at the canonical ElevenLabs start of
“home” (`16.347s`). The prior learner-deletion beat now cuts at `22.767s` to
the supplied full-frame technique-negation plate. The technique plate is
interpretive, not evidence. The Kodokan archive is review-renderable but
publication-ineligible until its source, date, rights, and attribution are
verified. The specification and validator now define positive visual events:
a relevant new asset qualifies, but removing a character, prop, overlay, or
information surface by itself does not. Paper wipes are limited to motivated
document/page/chapter changes. V6 plan hash is
`87d7c37d1a4f8a832775e648cd5364edabcf88dc422ec05f31a18c4a8dccd675`;
asset-map hash is
`471e9e488f64bff66d63d198f0aa97ec1af7b25bfd2eb498cdf0a29e16b37e70`;
preview hash is
`fa072705600ce2b455816bdff5cd419c15204fa4936a9c559078c93437ca7a10`.
Structural QC passes, Gate A remains unchanged, and complete video-engine
verification passes `315 passed, 1 warning in 42.82s` with only the existing
`pydub`/`audioop` deprecation warning. V6 supersedes V5 at the human proof gate.

### Proof Gate Revision V7

Operator feedback identified that the technique-negation artwork was authored
for a portrait/mobile surface and therefore required a destructive landscape
crop. Revision `editorial-motion-v7` uses a new original 16:9 composition built
from the same abstract visual concept: the complete central grappling pair and
all six crossed-out technique vignettes are visible inside landscape-safe
margins. The renderer uses centered `contain` placement, so no figure or
correction mark is cropped. All other V6 timing, assets, and shots remain
unchanged. V7 plan hash is
`ce91cf5126b47b0866248e58dee23c16ceb1391de1f123c0408d718e8a624315`;
asset-map hash is
`ffd1cd8386e5cd54932c76ecc2e09d6dd80ba8fe783260e632132e6237c3921b`;
landscape plate hash is
`05a76622a70c559d8a380ab157c878a9e74a2584beb5975f8fe1687005d6142d`;
preview hash is
`4b22e2cf2efddb784a258f2d17b41a23dea8e79b14d9b110d915e8be8b1893cc`.
Structural QC passes, Gate A remains unchanged, motion-provider cost is `$0`,
and one subscription image-generation call produced the replacement. V7
supersedes V6 at the human proof gate.

### Proof Gate Revision V8

Operator review found an extra or ambiguously owned limb in the V7 central
grappling pair. Revision `editorial-motion-v8` preserves the approved 16:9
woodblock composition but replaces only the central pair with a simpler,
anatomy-constrained two-person open-guard pose. The generation contract
requires exactly two people, four arms, and four legs, with each limb visibly
owned by one practitioner. All six surrounding crossed-out vignettes remain
inside landscape-safe margins. Agent visual inspection found no duplicated
limb, but this remains a human anatomy-review candidate rather than an
automatic quality approval. V8 plan hash is
`d501031d2b1806e447c736c4e265e5ab09f7e08ccd37e1257c44a6c678d3351f`;
asset-map hash is
`7242724112b16e29dafb3e04b7637a7475c717ce76d6caa6abc5f325b35e5191`;
corrected landscape plate hash is
`5244b1c53dca95bd2c7adf9ca46e5d2f358704615bcdea4496fce68cd29304e4`;
preview hash is
`4d49282722d52e7a7086b65d163bf92b1685c14ee779f812695b12233e0dd8da`.
Structural QC passes, Gate A remains unchanged, motion-provider cost is `$0`,
and one subscription image-edit call produced the anatomy correction. V8
supersedes V7 at the human proof gate.

### Proof Gate Revision V9

Operator review found that the V8 bottom practitioner’s raised right hand did
not have a legible gi-sleeve-to-lapel connection. Revision
`editorial-motion-v9` replaces only that plate: the right hand now emerges
from a continuous ivory gi sleeve and wraps a continuous dark lapel at the
top practitioner’s chest. The two-person, four-arm, four-leg anatomy, six
crossed-out vignettes, and 16:9 composition remain locked. The first edit
attempt produced a foot-like grip and was rejected without promotion. V8 is
retained as evidence but is marked non-renderable in the V9 asset map. V9 plan
hash is
`87151d121ae8b90a96b35d0bdf627fb35712d1fb6da749f3503339b96781e986`;
asset-map hash is
`12202a40cb18dddeb3705da7bd9977cbdc846a72a6fcbdf301136b4604f68337`;
corrected landscape plate hash is
`7260b60adce7f057cd4183753243364936b39ee1d8ab45ea1fd773a515a61eeb`;
preview hash is
`a4aeda2655097524422e33b85d55da52ae12acf7c78140b53a676ed515181a2b`.
Structural QC passes, Gate A remains unchanged, motion-provider cost is `$0`,
and two subscription image-edit calls were made: one rejected result and one
promoted result. V9 supersedes V8 at the human proof gate and remains pending
operator mechanics review.

## Verification

```powershell
python -m pytest --import-mode=importlib `
  content/video_engine/tests/test_editorial_motion.py `
  content/video_engine/tests/test_editorial_motion_qc.py `
  content/video_engine/tests/test_editorial_beats.py `
  content/video_engine/tests/test_animatic.py `
  content/video_engine/tests/test_history_v4_pipeline.py `
  content/video_engine/tests/test_plate_motion.py -q

Push-Location content/video_engine/editor
npm run typecheck
npm run build
Pop-Location

python -m pytest --import-mode=importlib -q
python scripts/prp_validate.py .claude/PRPs/plans/P13-EDITORIAL-MOTION-SYSTEM.plan.md
python scripts/prp_status.py
git diff --check
```

The proof review additionally requires:

- FFprobe verification of duration, dimensions, FPS, streams, and silent
  provider layers;
- plan/audio coverage with no timing gaps or overlaps;
- frame samples immediately before and after every cut;
- an optional diagnostic burn-in showing shot ID, focal point, motion phase,
  transform amount, and cut reason;
- byte/hash comparison proving active Gate A artifacts are unchanged; and
- an end-to-end human watch-through of both baseline and revised previews.

## Evidence And Handoff

The implementation must record:

- motion-plan, pacing-recipe, source, and output hashes;
- selected excerpt and matching audio/word-timing hash;
- baseline and revised preview paths;
- diagnostic preview and cut-frame sample paths;
- structural QC output and FFprobe results;
- provider call count and cost (`0` for this PRP);
- Gate A before/after hashes;
- exact focused/full test and Remotion verdicts; and
- Editorial Motion Proof Gate rubric status.

If the proof passes, the next plan may request a two- to four-shot provider
bakeoff only for shots marked `preferred` or `required`. The bakeoff must use
the same editorial motion plan and may replace source layers, never timing,
facts, citations, or final editorial authority.
