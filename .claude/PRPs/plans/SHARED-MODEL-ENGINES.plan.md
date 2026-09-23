---
id: SHARED-MODEL-ENGINES
title: Shared 2.5D and 3D model engines with reusable stylized assets
status: running
operation: feature
risk: high
owner: parent
branch: codex/Astra
created: 2026-09-22
updated: 2026-09-22
---

# Shared 2.5D and 3D Model Engines

## Summary

Build shared local authoring and rendering services for **characters, props and environments**, proved first with the two-fighter knockout scene. Reuse the existing layered-plate/player, asset and render infrastructure; use Blender as the 3D DCC/render backend rather than build another general-purpose renderer or generative model.

The result must make good-looking editable assets and convincing motion, not merely schemas, proxy bodies, or passing math tests. Separate reusable proportion/body presets, recognizable identity additions, rig/deformation, materials/art treatment, motion, and shot presentation. Treat native and externally generated models as alternative inputs to the same inspection and production workflow.

The operator approved HG1 on 2026-09-22: shared engines, fighter scene first. The older `MM-KNOCKOUT-ANIMATED-5` plan remains the episode/variant owner; it excluded shared-engine migration, which this separate plan now implements. Neither plan is silently marked complete or superseded.

## Intent And Acceptance

### Confirmed requirements

- Recognizable fighter caricatures from reusable presets, with individual face shape, proportions, hair/beard, tattoos, clothing and characteristic pose—not texture-only identity swaps.
- Realistic weight transfer, planted contacts, readable strikes, head response, follow-through and floor impact with stylized characters. Smooth fighting; crude/comic interview acting remains an available treatment.
- 2.5D must support editable layered art, foreground/background separation, bounded camera depth and occlusion, and pose/expression changes. A camera pan across one flat still is not the complete engine.
- 3D must produce actual editable mesh/rig/material assets, meaningful head/face/hands, deformation-aware topology, expressions, modular costumes/props, and reproducible scenes. Primitive blockouts remain diagnostics.
- Existing five-variant direction stays available: Saitama, Roshi, detailed 2D, stylized 3D, minimal 2D. This plan delivers the reusable engine and first benchmark; it does not claim that a toon render alone completes the hand-authored 2D variants.
- Tripo comparison follows the first finished in-house asset: in-house, raw Tripo and cleaned/rigged Tripo under the same shot conditions. The operator accepts the discussed vendor risk and permits learning from visible results/improving our assets. Do not invent a blanket ban on that work or reopen that decision; record actual asset provenance and commercial status. Purchases still require explicit authorization.

### Observable acceptance

| ID | Acceptance evidence |
|---|---|
| AC1 | One shared versioned asset interface supports character, prop and environment; switching supported render lanes does not duplicate the authoritative identity/provenance record. |
| AC2 | Two finished-looking fighter identities from a shared preset family, shown front/three-quarter/side and under neutral material plus final shading; operator accepts recognition and stylization. |
| AC3 | Shoulder/elbow/hip/knee, hand and face stress tests produce inspection receipts and viewable frames; unacceptable collapse, interpenetration, eye/mouth defects and texture seams are fixed before motion approval. |
| AC4 | The same authored exchange renders in 2.5D and 3D with consistent contact/event times, readable silhouettes, full follow-through/fall/ground contact, and original-pitch audio. |
| AC5 | One identity/costume swap reuses the rig and action, with reach/contact refitting verified; no per-fighter fork of engine logic. |
| AC6 | A separate hinged/attachable prop and layered environment fixture run through the same interfaces without fighter-specific field hacks; diagnostic fixture status is explicit. |
| AC7 | Fresh and resumed local builds record source hashes, parameters, tool versions, stage timings, cache decisions and output checksums; missing/stale artifacts and failed render stages cannot report success. |
| AC8 | Tripo benchmark records retries, credit use, cleanup/rigging minutes, geometry/surface/deformation quality and time to an accepted shot. Vendor failure does not block the native engine; purchase choice remains human. |
| AC9 | Existing player/layer and project baselines remain unchanged unless a separately reviewed adapter change is necessary. No new player, unauthorized publication, source audio warp, or V12 overwrite. |
| AC10 | At least one available local-AI enhancement is compared against its Blender-authored source under the same shot and inspection criteria, with quality, editability, runtime, provenance and failure modes recorded. If the local stack is unavailable, record the exact dependency rather than claiming an enhanced result or blocking native delivery. |

## Scope

### Architecture and interface boundaries

**Local-first, offline final rendering; no new web editor or hosted API.** Proposed modules below are new work, not existing capabilities. Final source-grounded integration anchors are in the inventory evidence linked below.

1. **Asset and preset service:** versioned supplemental `model_asset.v1` descriptors reference the existing asset identity/store and approval record. Fields cover asset kind, original/derived lineage and SHA-256, coordinate convention/scale, bounded proportion parameters, mesh/layer resources, rig capabilities and sockets, expression controls, materials/UV set, view envelope, editable source and provenance. Software/tool license and mesh/texture/motion licenses remain distinct. Never create an independent approval boolean that overrides the established manifest.
2. **Shared scene/motion contract:** proposed `model_scene.v1` records exact asset revisions, rational FPS, time origin and source-time mapping, duration, camera/lights, named environment collision surfaces, prop attachments, semantic motion channels, contacts/events, render profile and approved art treatment. Authored decisions remain authored; the engine evaluates them, it does not allocate shots by count.
3. **3D backend:** Blender Python scene construction plus editable `.blend` sources; version-pinned body/face presets, rig mapping, weight/corrective handling, materials and render passes. Blender MCP is permitted for interactive authoring, inspection and fast iteration, provided every accepted change is saved to versioned editable assets and can be reproduced or inspected by the headless Blender build. It is an authoring interface, not a mandatory final-render service. Evaluate MPFB/MakeHuman + Rigify as the first candidate, not as already installed or validated. Prefer existing Blender deformation tools to reimplementing them; custom math serves contact, retargeting, secondary response and diagnostics.
4. **2.5D backend:** preserve the existing layer/plate camera contract. Add model-derived and authored-art layers with explicit pivots, masks, pose/expression resources and depth roles. Use local 2D deformation or baked pose resources where appropriate, but state which is used. For views outside an asset's declared envelope, fail with a diagnostic or select an explicitly authored 3D shot; never silently invent unseen geometry.
5. **Optional local-AI enhancement:** Blender-authored meshes, rigs, motion and editable scenes are the primary source. Evaluate the local LoRA/Hugging Face/ComfyUI stack for bounded downstream enhancements such as texture/look variants, masks, depth and 2.5D layer preparation. Compare each enhanced result with the Blender-authored baseline under the same shot and inspection criteria; retain the unenhanced source, provenance, model/version/license and reproducible parameters. No AI output may silently replace rig geometry, contact timing or approved identity. The stack is not required for every build, and an unavailable service does not prevent an otherwise valid Blender build.
6. **Render and inspection adapters:** reuse existing local job/artifact services where their operations fit; add narrow adapters, not a parallel queue. Render requests emit a hash-bound model inspection receipt and existing player-compatible media/layer assets. The existing assembly lane owns captions, music and final mux.

### Asset authoring and quality path

Start with a clean base mesh and useful head/face/hands, then proportion and identity controls, refit rig/clothes, author weights and correctives, add final hair/beard/tattoo/material work, test expressions, and only then approve the character. A giant head on an unrefined proxy body cannot pass AC2. Export texture-only and geometry-only comparisons so attractive shading cannot conceal mesh defects.

Use explicit character/prop/environment capability profiles: a static environment need not pretend to have a facial rig; a hinged prop exposes its hinge and attach socket; a humanoid exposes semantic limbs and face controls. One coordinate contract (documented axes, handedness, units and rest pose) is converted at import/export boundaries. Authored pose transfer resolves targets against each body's actual limb lengths and records clamping/residuals; do not scale a skeleton and assume planted contacts survive.

Keep 3D world metres, projected screen coordinates, and P58's layer-depth factors as separate typed fields. The projection adapter produces pixel pivots/masks and dimensionless layer depth from the shared scene; it must not feed world-space Z directly into an existing parallax multiplier. Profile-specific silhouette or pose overrides are explicit authored deltas, never silently different contact clocks.

Geometry detail is shot-dependent, not one universal vertex target. Record stored and evaluated vertices, faces and triangles separately for each fighter and each render-detail variant; compare the riggable control mesh, subdivided/sculpted render mesh and baked material detail in identical full-body, face/hand close-up and impact stress shots. Increase density where silhouette or deformation visibly needs it, preserving editable topology and measured render cost. Vendor polygon or triangle settings are comparison inputs, not a directly comparable count of Blender control vertices.

Motion phases are approach → contact → follow-through → recovery/fall → floor contact. Preserve attack velocity through contact; a rest-to-rest easing curve is not a generic collision model. Visual hit-stop and audio timing are separate clocks. Any simulation is baked or explicitly seek-safe and deterministic within the declared tool/hardware profile; cross-GPU pixel identity is not promised.

### Fighter benchmark constraints

Bind to the existing V12 cut and measured source timing rather than new estimated offsets. Preserve the uninterrupted punch follow-through and ground impact, the completed interview excerpt, continuous balanced music, and native source audio pitch. Keep the original no-charge wording/allegation attribution unchanged. Transformation and symbolic non-gory brain ejection follow the user-locked beats; brain release is tied to contact/head snap, not an earlier flash or an invented force threshold. Skull fracture clutter is excluded. No legal, medical or injury claim is inferred from the visual effect.

### Tripo evaluation

After AC2 in-house art exists, use the same operator-selected reference design and framing for all candidates. Separate unmodified output quality from cleanup improvements. Inspect turntable, back/hands/face, UV/material seams, stress poses and the same exchange—not just the provider preview. Test whether generated geometry, rebaked appearance, retexturing, or a whole asset is useful; a texture map is not portable across different UVs without work. Capture the actual plan/export/model version at generation time. No subscription or paid generation is authorized by this draft.

## Not Building

- A competing 3D foundation model, training pipeline, general-purpose physics solver, Blender replacement, or new scene-evidence player.
- SaaS, REST endpoints, accounts, multi-tenant storage, browser modeling UI, distributed farm or new database.
- Photoreal humans as the default, physically exact injury simulation, universal fixed anime timing constants, or unverified research numbers copied into runtime defaults.
- Mandatory LoRA/Hugging Face/ComfyUI dependencies for every build, mandatory real-time glTF delivery, or blanket retopology of every imported asset regardless of deformation needs. This does not exclude evaluating or using the local AI stack for measured asset enhancement.
- Automatic visual approval, automatic purchase, provider calls during planning, publication, unrelated effects-catalog repairs or destructive cleanup of the dirty checkout.

## Human Gates

| Gate | Decision and artifact | Blocks |
|---|---|---|
| HG1 | Approved by operator 2026-09-22: shared engines, fighter scene first; local AI stack is an optional evaluated enhancement after Blender authoring; Blender MCP may be used for interactive authoring and inspection. | Closed; implementation may proceed. |
| HG2 | Judge finished native fighter design sheets, turntables, deformation/face tests and 2.5D view-envelope demonstration. | Expansion to the roster and final action production; diagnostic work may continue. |
| HG3 | Judge both rendered exchange lanes and the general prop/environment demonstration with inspection receipts. | Calling either engine production-ready or replacing approved episode assets. |
| HG4 | Review Tripo/native/hybrid comparison and explicitly choose any paid plan/budget. | Paid provider activity and use beyond recorded asset rights; not independent native development. |

Each gate has a corresponding review-queue item; HG2–HG4 start as agent-owed because no proof artifact exists yet. Scope approval is not art approval. HG2 consumes T4b, T5b, T6 and T7 artifacts; none of those tasks waits on HG2. HG4 is a post-result free-comparison verdict: remain native, defer, or request a separately authorized paid follow-on amendment. T10 never requires paid work to proceed, and HG4 does not block native handoff.

## Mandatory Reads

- `AGENTS.md`; `docs/AGENT_START_HERE.md`; `docs/agent-context/SKILL_ROUTER.md`; `docs/runbooks/PRP_EXECUTION.md`; `docs/WORKTREE-REGISTER.md`.
- `docs/AGENTS-VIDEO-ENGINE.md`; `docs/content-video-engine/README.md`; `PIPELINE.md`; `CAPABILITIES.md`; relevant E1–E6 rulings and current operator corrections.
- `.claude/PRPs/plans/P58-THE-2-5D-STAGE.plan.md`; `.claude/PRPs/plans/knockout-five-animated-variants.plan.md`; current fighter `LEDGER.md` and `RIG-ACCEPTANCE.md`.
- `docs/research/motion/ANIMATION_PRODUCTION_INFERENCE_MAP.md`; the five source blueprints it indexes; `docs/research/runs/anime-production-intake-2026-09-22/PROVENANCE-LIMITS.md`; `docs/research/runs/grill_stylized_character_starters/intake-review.md` and `reference-style-direction.md`.
- Research runs explicitly consumed: `docs/research/runs/3d-rigging-combat-mechanics-2026-09`, `docs/research/runs/anime-avatar-cg-production-2026-09`, `docs/research/runs/anime-auras-naruto-transitions-2026-09`, `docs/research/runs/gits-animation-production-2026-09`, `docs/research/runs/attack-on-titan-production-2026-09`, `docs/research/runs/tripo-comparison-2026-09-22`.
- Before any Blender state inspection/render validation, load `blender-motion-state-inspection`; before actual image or video generation, load the applicable generation skill and honor its review/budget boundaries.

## Execution Path

HG1 → baseline/fixtures → asset/scene contracts → base-model feasibility and detailed art → shared motion/deformation → 3D and 2.5D adapters → render/assembly integration → paired proof and generalization → HG3 → measured handoff.

The two backend implementations may run in parallel only after the shared contract is frozen. Parent owns contract changes and serial integration into the compiler/player, asset services and queue. Separate write sets and worktree/engine leases precede code work. No worker inherits provider spending or promotion authority.

The Tripo comparison follows native art HG2 and can run alongside non-overlapping renderer work. Failure or insufficient free-tier exports yields a recorded unavailable comparison, not an endless dependency or invented result. An explicit HG4 decision closes only the optional benchmark slice; native completion is independent.

## Patterns To Mirror

- Existing `plate_library.v2` and `<plate>.layers.json`: semantic roles, depth, alpha and explicit flat fallback; do not replace P58.
- Existing `scene_evidence_timeline.v1`, split player and asset embedding: integrate outputs through existing assembly.
- `local_render_job.v1`: job state and hash-bound artifact receipts, with cancellation/failure distinct from success.
- Existing asset store/catalog/resolver and review manifests: extend or reference, do not create a competing source of truth.
- Project-local two-bone IK and DQS proofs: reuse tested mathematics only after interface/adversarial review, not the proxy art or unsupported global-volume claims.
- Concrete source trace: `docs/research/runs/model-engines-prp-2026-09-22/3d-inventory.md` and `2_5d-inventory.md`. `src/scenes/bjj_action.py` (paths in this paragraph relative to `content/video_engine/`) supplies semantic joints, contact anchors and phases, but is Manim/2D, not a Blender rig. `src/services/living_scenes.py` scene bundles remain planning-only (`render_eligible:false`).
- Existing integration seams: `src/services/asset_store.py`, `asset_catalog.py`, `asset_resolver.py`; `src/services/local_render_queue.py`; `scripts/build_plate_library.py`; `scripts/build_scene_timeline_f.py`; `scripts/render_baseline.py`. Canonical player is `docs/content-video-engine/samples/scene-evidence-engine.mjs` at repository root; camera is `content/video_engine/scripts/kinetics/camera.mjs`. Existing strict timeline schema does not already guarantee support for proposed rig fields: emit compatible resources rather than insert arbitrary fields.
- `content/video_engine/src/services/martial_editorial_adapter.py::compile_martial_editorial` emits Remotion props and an adapter manifest. It is a separate assembly seam, not a direct scene-evidence-player adapter. Preserve that distinction and its `src/guards/editorial_motion_qc.py` checks.

## Task Slices

All paths below are proposed new write sets unless identified as existing. Tests/CLI commands in later slices are **contracts to implement**, not assertions those tools currently exist. `M` below means `content/video_engine/src/modeling`; `F` means `content/video_engine/tests/fixtures/modeling`; `B` means `content/video_engine/review/model-engines/benchmark-v1`.

### T1: Freeze baseline, benchmark inputs and runtime feasibility
- Status: complete (technical starter gate only; art unapproved)
- Owner: implementation_luna; parent reviews
- Depends on: HG1
- Write set: `F/baseline/`; `B/baseline/`; this plan's evidence fields (parent only)
- Acceptance: current V12/media hashes, measured FPS/audio/events, exact tool versions, existing tests and dirty-file baseline captured; no original cut modified. Test at most two documented starter candidates against the same import/pose fixture, beginning with MPFB/MakeHuman + Rigify. Inventory the local LoRA/Hugging Face/ComfyUI capability and Blender MCP availability without requiring either for this native baseline; later enhancement comparisons use the same source/shot and record model and asset provenance. After HG1, necessary free local assets/add-ons may be acquired into an isolated project tool/profile directory with hashes and license records; no global upgrade, paid acquisition or account change is included. Choose the passing candidate from measured compatibility/deformation evidence; if neither passes, return the concrete failures for a scoped decision rather than opening endless research.
- Validate: run all four Exact existing baseline commands below; `ffprobe -v error -show_format -show_streams -of json content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/assembly-v12/build/render/knockout-brain-matchcut-001-v12.mp4`; `& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --version`; retain before/after source hashes in benchmark-inputs.json.
- Evidence: `F/baseline/benchmark-inputs.json`, `F/baseline/baseline-receipt.md`, `F/baseline/impact-pose-fixture.v1.json`, `F/baseline/run_mpfb_rigify_probe.py`; local ignored `B/baseline/candidates/mpfb-2.0.17/` contains editable `.blend`, inspection JSON and two PNGs with hashes in the tracked manifest. MPFB 2.0.17 + Rigify is selected only as the T4a starter, not accepted art.
- Execution checkpoint (2026-09-22): worktree/main both began at `712ece1`; register/golden regression `163 passed`. V12 and source timing were read from main without copying or modifying the ignored media. MPFB attempt 1 failed because extension source was imported as a legacy add-on; Blender wrote four new MPFB user-resource files outside the fixture. Their hashes/timestamps were recorded, then exactly those four files and empty directories were removed after hash verification. `BLENDER_USER_RESOURCES` now redirects the top-level USER path inside the fixture. Packaged-extension attempts 2 and 3 created an MPFB human and Rigify rig, but the probe aborted at obsolete Blender API fields (`Bone.roll`, then `BLENDER_EEVEE_NEXT`) before scene save and rendered deformation review. Global MPFB paths remained absent on recheck. The three failures and partial results are recorded in `F/baseline/` and `B/baseline/`; the bounded inspector fix is escalated to `execution_sol` (GPT-6 Sol xhigh). T1 remains running; no model/art acceptance is claimed.
- Escalation checkpoint: Sol attempt 4 saved an editable `.blend`, two renders and structured inspection. MPFB produced a 13,380-vertex Human, `Human.rigify` (930 bones), and body armature modifiers, but the test's FK arm control caused zero evaluated-vertex movement. Read-only saved-scene inspection showed the rig's `IK_FK` switch at 0, so IK overrode the animated FK control; the default Cube also occluded the renders. Sol attempt 5 explicitly activated FK and hid Cube: `DEF-upper_arm.R` moved 0.0715166 m and 4,736/13,380 evaluated Human vertices moved, with Human floor minimum approximately 0 m. The isolated offline test saved a `.blend` and two unobscured PNGs; V12 hash stayed unchanged. This establishes technical starter feasibility, not likeness, polished deformation, fight choreography or art approval. T2 may begin; T4a must still test face/hands, stress poses, proportion controls and visual quality.

### T2: Shared asset, preset and scene contracts
- Status: complete (contract validation only; no art or render approval)
- Owner: implementation_luna; parent owns schema decisions
- Depends on: T1
- Write set: `M/__init__.py`, `M/contracts.py`; `content/video_engine/configs/model_asset.v1.schema.json`, `model_scene.v1.schema.json`, `model_inspection.v1.schema.json`; `F/contracts/`; `content/video_engine/tests/test_model_contracts.py`
- Acceptance: versioned references, units/axes, semantic rig/socket capability profiles, timebase, authored contacts, source lineage and approval references validate; reject nonfinite values, out-of-root paths, unsupported versions, stale hashes and incompatible capabilities. No copied approval authority or implicit unknown-source promotion.
- Validate: `python -m pytest content/video_engine/tests/test_model_contracts.py -q`
- Evidence: `M/contracts.py`, the three v1 schemas, `F/contracts/`, and `test_model_contracts.py`; parent verified 36 passed, one symlink-permission skip on 2026-09-22. Negative tests cover wrong units, invalid time/geometry, stale hashes, path escape, capability mismatch, fabricated catalog/approval records, missing trusted authority anchors, ineligible render scenes, and self-asserted operator approval. Render-ready validation requires caller-supplied trusted catalog and approval paths; metadata validation alone conveys no approval. Independent reviewer identified five trust/schema gaps; Luna fixed the bounded slice after three failed attempts and escalated final test/scene-clock cleanup to Sol xhigh (attempt 4). T3/T5a integration hardening subsequently added explicit approved-record decision/attribution checks, duplicate event/contact ID checks, and zero-quaternion rejection (43 passed, one symlink skip). No native fighter art or motion-quality verdict follows from this contract pass.

### T3: Asset intake and reusable library integration
- Status: complete (review-only intake; render/art approval remains external)
- Owner: execution_sol escalation; parent retains integration and approval boundary
- Depends on: T2
- Write set: `M/assets.py`, `M/importers.py`; `F/assets/`; `content/video_engine/tests/test_model_assets.py`; existing asset service modifications only by parent after narrow interface review
- Acceptance: native/external model, layered artwork, prop and environment inputs resolve through the existing asset store; immutable originals plus derived versions; relative resource paths, lineage, sockets and provenance captured. No untrusted embedded Blender scripts execute; imported assets cannot write outside the run directory.
- Validate: `python -m pytest content/video_engine/tests/test_model_assets.py -q`
- Evidence: `M/assets.py`, `M/importers.py`, `F/assets/`, `test_model_assets.py` and `.gitattributes` landed in `708b64d` after Sol escalation preserved the core from three bounded Luna failures. The independent reviewer found missing `.blend` dependency declarations, overly strict in-root glTF `../` handling, and unbounded bundle intake; fixes and follow-up URI-count hardening passed 26 focused tests (two Windows symlink skips), with the combined relevant suite at 143 passed, three skips. Parent hardened T2 render approval so review-only intake records cannot serve as approvals (`aa6b634`). No provider calls or Blender execution; `.blend` packed/dependency claims require later Blender inspection and the 80-byte fixture is diagnostic, not art.

### T4a: Native preset authoring tooling
- Status: running (diagnostic editable preset family; no art approval)
- Owner: implementation_luna for bounded Blender authoring; parent art direction/integration
- Depends on: T3
- Write set: `M/blender/authoring.py`, `M/blender/presets.py`; `content/video_engine/assets/modeling/native/`; `F/presets/`; `content/video_engine/tests/test_model_presets.py`; `B/art/`
- Acceptance: one editable body/rig family with bounded face/proportion/hair/clothing controls, tested on diagnostic assets; no finished-art claim. T1 selects the primary starter or its single documented fallback based on usable license, offline import, editable topology, rig compatibility and face/hands baseline; failure blocks that choice rather than starting open-ended research.
- Validate: `python -m pytest content/video_engine/tests/test_model_presets.py -q`; the T4a test fixture launches the pinned Blender executable and checks reopened assets, independent of T8.
- Evidence: pending; per-candidate `.blend`, manifest, contact sheet, render metadata and art review.

### T4b: Two fighter identities and bounded art packet
- Status: pending
- Owner: implementation_luna; parent directs art and records operator verdict
- Depends on: T4a
- Write set: `content/video_engine/assets/modeling/native/fighters/`; `B/art/fighters/`
- Acceptance: `fighter-a.blend`, `fighter-b.blend` and per-fighter `model-asset.json`; front, three-quarter, side, back, face and hand closeups in neutral and final materials. Both share the preset family but remain recognizable caricatures. One first submission and at most two correction passes per explicit review; unresolved rejection requires a scoped operator decision, not unlimited polishing.
- Validate: `python -m pytest content/video_engine/tests/test_model_presets.py -q`; this suite must enumerate both fighter manifests. HG2 also consumes T5b stress poses and T7b view proof.
- Evidence: pending; detailed editable assets and review packet, not proxies.

### T4c: Non-fighter generalization fixtures
- Status: pending
- Owner: implementation_luna
- Depends on: T4a
- Write set: `content/video_engine/assets/modeling/native/generalization/`; `F/generalization/`
- Acceptance: `hinged-prop.blend`, `environment.blend` and model manifests; socket/hinge behavior plus layered environment demonstrated without humanoid-only fields. Diagnostic fixture labeling retained.
- Validate: `python -m pytest content/video_engine/tests/test_model_presets.py -q` including both fixtures.
- Evidence: pending; consumed by T9, not a prerequisite for fighter art approval.

### T5a: Backend-neutral motion semantics
- Status: complete (implementation and targeted independent re-review; no backend/art approval)
- Owner: implementation_luna; parent owns shared contract
- Depends on: T2
- Write set: `M/motion.py`, `M/inspection.py`; `F/motion/`; `content/video_engine/tests/test_model_motion.py`
- Acceptance: rational clock, event/contact intervals, semantic targets, coordinate-tagged residuals and deterministic seek evaluation; no Blender control names or mesh assumptions in portable intent.
- Validate: `python -m pytest content/video_engine/tests/test_model_motion.py -q`
- Evidence: `M/motion.py`, `M/inspection.py`, `F/motion/`, and `test_model_motion.py` landed in `411c957`; 15 focused tests passed on 2026-09-22, and a distinct opaque 3D/2.5D target map consumes the same authored clock/contact fixture. Independent reviewer found and verified fixes for T2 semantic-token compatibility, quaternion endpoint normalization/antipodal SLERP, and exact direct RationalClock construction. Parent aligned T2 on duplicate event/contact IDs and zero quaternions in `aa6b634`; contract tests passed 43 with one Windows symlink skip. Portable intent names remain semantic keys resolved through backend maps; T5b must bind stable semantic aliases to actual controls, not serialize Blender control paths into shared intent. This fixture is diagnostic timing evidence, not motion-quality approval.

### T5b: 3D rig mapping, deformation and contact
- Status: pending
- Owner: implementation_luna; parent reviews mathematical contracts
- Depends on: T5a, T4b
- Write set: `M/retarget.py`, `M/blender/rigging.py`; `F/deformation/`; `content/video_engine/tests/test_model_deformation.py`
- Acceptance: semantic FK/IK mapping, stable poles, planted-contact intervals, per-proportion refitting, facial controls and pose correctives; measured surface contacts, endpoint residuals and joint/floor diagnostics. Pure deterministic evaluation or recorded bake; full force/action phase continuity, no minimum-jerk impact shortcut or universal DQS volume claim.
- Validate: `python -m pytest content/video_engine/tests/test_model_motion.py content/video_engine/tests/test_model_deformation.py -q`; pose-order/seek tests and rendered stress-frame review.
- Evidence: pending; tolerances declared in fixtures before verdicts, with world-space and screen-space residuals. New numeric thresholds are engineering test budgets, not claimed biomechanical laws.

### T6: Editable Blender 3D backend
- Status: pending
- Owner: implementation_luna
- Depends on: T3, T5a, T5b
- Write set: `M/blender/scene.py`, `M/blender/render.py`, `M/blender/materials.py`; `F/blender/`; `content/video_engine/tests/test_model_blender.py`; `B/3d/`
- Acceptance: asset instances, camera/lights, stylized material/outline treatment, attachments and event-driven FX produce an editable scene and render sequence. Beauty/alpha, depth and object masks are declared pass capabilities, not assumed on every format. Preserve rig control versus skin geometry separation.
- Validate: `python -m pytest content/video_engine/tests/test_model_blender.py -q`; the suite must launch background Blender, render the fixture, reopen its scene and inspect frame sequence/state (not mock those checks).
- Evidence: pending; full frames and scene inspection with hidden/disabled-object and render-engine state captured.

### T7a: Independent editable 2.5D model/layer backend
- Status: running (authored-layer diagnostic input; independent of T4a/T5b)
- Owner: implementation_luna
- Depends on: T3, T5a
- Write set: `M/layered.py`; `F/layered/authored/`; `content/video_engine/tests/test_model_layered.py`; `B/2_5d/authored/`; shared player source remains read-only
- Acceptance: independent backend development uses one editable authored-layer character fixture with pose/expression swaps, plus props/environment planes. This proves independent input support, not completion of the detailed 2D episode variant. Shared contact clock, explicit view limits and disocclusion failures; no dependency on T5b or Blender. Fighter-derived resources belong to T7b.
- Validate: `python -m pytest content/video_engine/tests/test_model_layered.py content/video_engine/tests/test_plate_library_layers.py content/video_engine/tests/test_page_depth.py content/video_engine/tests/test_dock_depth.py -q`; the new suite includes contact/camera/occlusion and random-seek frame checks.
- Evidence: pending; editable layers and metadata, bounded camera proof and invalid-view refusal fixture.

### T7b: Fighter-derived layer bake and view proof
- Status: pending
- Owner: implementation_luna
- Depends on: T7a, T6
- Write set: `M/bake_layers.py`; `F/layered/fighters/`; `B/2_5d/fighters/`; `content/video_engine/tests/test_model_layer_bake.py`
- Acceptance: first paired fighter proof uses 3D-baked articulated pose resources, preserving the shared contact clock; deliver editable layer metadata, expression/pose resources and bounded view-envelope proof for HG2. When the local LoRA/Hugging Face/ComfyUI stack is available, compare one bounded texture/look, mask, or depth enhancement against the unenhanced Blender-derived resource; the Blender source and pose timing remain authoritative. Record measured benefit, artifacts, model/license/provenance and reproducible settings, or the exact availability blocker.
- Validate: `python -m pytest content/video_engine/tests/test_model_layer_bake.py -q`; real Blender bake and layer-output checks required.
- Evidence: pending; include the native/enhanced comparison or a concrete unavailable result. No claim this completes the hand-authored detailed 2D variant.

### T8: Local execution, inspection CLI and existing assembly adapter
- Status: pending
- Owner: parent integration with bounded implementation_luna worker
- Depends on: T6, T7b
- Write set: `M/runner.py`, `M/assembly.py`; `content/video_engine/scripts/model_engine.py`; `content/video_engine/tests/test_model_runner.py`; `B/jobs/`. Parent-only existing integration allowlist: `content/video_engine/src/services/local_render_queue.py`, `asset_catalog.py`, `asset_resolver.py`, `asset_store.py`, `martial_editorial_adapter.py` (all under the same services directory), and corresponding existing test files. Existing player/compiler source is read-only for this slice; if compatible emitted layers/media are insufficient, amend the PRP before changing its schema or runtime.
- Acceptance: proposed `validate`, `build`, `render`, `inspect`, `compare` commands invoke one declared lane with version/hash receipts; resume/cancel/failure never duplicate provider work or overwrite originals. Existing assembly consumes media/layer outputs; audio is not stretched. No new player or independent job database.
- Validate: `python content/video_engine/scripts/model_engine.py --help`; `python -m pytest content/video_engine/tests/test_model_runner.py -q`; interruption/retry and stale-cache tests; existing adapter regression suites.
- Evidence: pending; live handles and per-stage outputs retained, error states tested, build hash changes invalidate affected derived assets.

### T9: Paired fighter proof and generalization demonstration
- Status: pending
- Owner: parent; implementation_luna for bounded scene authoring
- Depends on: T8, T4c, HG2
- Write set: `B/scenes/`, `B/proofs/`; project-local integration order under fighter `production/animated-variants/model-engine-benchmark/`; no V12 overwrite
- Acceptance: same source-timed exchange in both lanes, identity/costume swap, separate prop/environment proof, full follow-through and floor impact; side-by-side authored neutral/finished comparisons. Operator judges HG3; technical passes alone cannot close it.
- Validate: `python content/video_engine/scripts/model_engine.py compare --manifest content/video_engine/review/model-engines/benchmark-v1/comparison.json`; `python content/video_engine/scripts/model_engine.py inspect --manifest content/video_engine/review/model-engines/benchmark-v1/baseline/benchmark-inputs.json`; the latter enumerates and fully decodes every proof. Operator picture/audio review is an additional HG3 verdict.
- Evidence: pending; record FPS/frame count/duration, source event mapping, before/contact/head-snap/follow-through/floor frames, and time/resource costs.

### T10: Tripo raw versus hybrid versus native benchmark
- Status: pending
- Owner: parent; bounded provider worker only when required and authorized
- Depends on: T4b, HG2, T8
- Write set: `B/tripo/`, `B/comparison.json`; provider order and provenance receipts only
- Acceptance: same design/render conditions and evaluation criteria; record raw and cleaned candidates separately, generation limits/credits, cleanup labor and relevant rights metadata. Do not require an external output to satisfy native-engine tests. HG4 records buy/remain-native/defer with reasons; no silent subscription.
- Validate: proposed `model_engine.py compare --manifest` command in T9; asset provenance/hash check; manual quality and cost review. If unavailable, record actual blocker and HG4 decision rather than fabricate a sample.
- Evidence: pending; benchmark definition in `docs/research/runs/tripo-comparison-2026-09-22/COMPARISON.md`, supplemented by the operator's subsequent risk acceptance.

### T11: Independent regression review, recall and operator handoff
- Status: pending
- Owner: reviewer (read-only); parent fixes/integration and documentation
- Depends on: T9, HG3; T10/HG4 only for the optional comparison addendum
- Write set: `docs/runbooks/MODEL-ENGINES.md`; parent-owned plan/queue/evidence updates; capability/catalog entries only for actually proved work
- Acceptance: independent review has no unresolved blocking correctness issues; all new code regressions plus affected existing suites pass; exact reproduction commands and asset creation/reskin/retarget recipes documented. Search retrieves implemented entry points and known limits. Five-variant plan receives a handoff, not a false completion stamp.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/SHARED-MODEL-ENGINES.plan.md`; `python -m pytest content/video_engine/tests -k model_ -q`; all four Exact existing baseline commands below; `python content/video_engine/scripts/docs_find.py "model engines"`; independent diff review. Refresh affected docs indexes using the existing docs-layer builder if retrieval is stale.
- Evidence: pending; capability claims link to actual renders and receipts. Track unrelated catalog failures separately rather than weaken their checks.

## Verification

### Exact existing baseline commands

Run from repository root. During planning, camera tests passed **10/10**, the four layer suites passed **119/119**, and the inventory's focused rig run passed **20/20**. These establish current technical baselines, not art approval.

```powershell
node --test content/video_engine/tests/kinetics/camera.test.mjs
python -m pytest content/video_engine/tests/test_plate_library_layers.py content/video_engine/tests/test_comfy_depth_split.py content/video_engine/tests/test_page_depth.py content/video_engine/tests/test_dock_depth.py -q
python -m pytest content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-foundation/test_rig_foundation.py content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-skinning/test_dqs.py content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-skinning/test_pose_contract.py -q
python -m pytest content/video_engine/tests/test_local_render_queue.py content/video_engine/tests/test_asset_catalog.py content/video_engine/tests/test_asset_store.py content/video_engine/tests/test_asset_resolver.py content/video_engine/tests/test_martial_editorial_adapter.py content/video_engine/tests/test_editorial_motion_qc.py -q
```

The last integration suite also passed during planning: **83/83**. Rerun all baselines before implementation. T1 must create `B/baseline/benchmark-inputs.json` containing the exact V12 path, tool executable paths, source hashes, expected frames/events and fixture artifacts. T8 must implement the following **future** exact command, replacing illustrative `<V12>`/`<each-proof.mp4>` notation above: it reads that manifest, invokes recorded Blender/ffprobe and full ffmpeg decode for every expected artifact, checks missing outputs/hashes/timebase, and saves unabridged verdicts. T4a's pytest fixture performs its own Blender checks before T8 exists.

```powershell
python content/video_engine/scripts/model_engine.py inspect --manifest content/video_engine/review/model-engines/benchmark-v1/baseline/benchmark-inputs.json
python -m pytest content/video_engine/tests -k model_ -q
```

Source selection is slice-specific: all workers read the inference map and provenance limits; T4/T5 consult the rigging and avatar blueprints, T6/T7 consult only the linked art/pass/layer sections. Raw research bundles are evidence lookup targets, not blanket mandatory full reads. Provider facts are rechecked during T10 rather than assumed current from research notes.

Planning: validate this PRP, review the source-grounding inventories, register all human gates, and record assumptions/caveats. Implementation commands above are future acceptance obligations. No new engine tests or renders have run merely because this document names them.

Implementation has four independent verdicts: **contract/math**, **artifact/render integrity**, **visual/motion quality**, and **operator approval**. Every proof must identify its verdicts. Required negative tests include missing asset, stale hash, unsupported rig/view, unit mismatch, out-of-range time, invalid path, unreachable limb target, incorrect seek order, interrupted job, broken frame sequence and absent required audio. Test results and measurements are retained verbatim.

Set initial numeric tolerances and render-time budgets in T1/T5 from the fixed benchmark before judging candidates; record hardware/version dependence. Measure quality at intended delivery resolution as well as preview size. Zero claims of whole-mesh volume preservation, exact physiology or universal anime timing follow from a small sampled test.

## Evidence And Handoff

Planning ledger: `docs/research/runs/model-engines-prp-2026-09-22/PLANNING-LEDGER.md`. Inventories: `3d-inventory.md`, `2_5d-inventory.md` in that directory. Proposed production receipts: `content/video_engine/review/model-engines/benchmark-v1/`.

Current repository is dirty; original cut, existing accepted assets and unrelated changes remain user-owned. No commits, provider uploads, purchases, installations or production code are part of this planning turn. The absent TPM feature/pre-staging documents are recorded in the ledger; no substitute acceptance is invented from them.

Approval request: accept this shared-engine architecture and phased proof-first scope, or revise the specific boundary before implementation starts.
