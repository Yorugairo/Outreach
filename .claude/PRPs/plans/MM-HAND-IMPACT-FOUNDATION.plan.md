---
id: MM-HAND-IMPACT-FOUNDATION
title: Hand-first, style-neutral strike and contact foundation
status: running
operation: feature
risk: high
owner: parent
branch: main
created: 2026-09-24
updated: 2026-09-24
---

# Hand-first strike and contact foundation

## Summary

Build one anatomically grounded, reusable **motion/contact source** before another glove shell or fighter render. An editable Blender hand proves the closed fist, wrist alignment, knuckle patch and deformation; a backend-neutral strike record carries pose, contact timing, calibrated mass/compliance parameters and receiver impulse. The detailed 3D fighter, layered 2.5D fighter and minimal 2D/stick-figure treatment consume that same record. The thin 2D arm may look light while the hidden full-body strike and reaction remain weighty; art treatment may exaggerate the response explicitly without falsifying the source contact clock.

This is a hand-first child of `SHARED-MODEL-ENGINES.plan.md` T5b and `MM-HAND-01`. It proposes starting the generic hand/contact proof **before** the finished fighter identities in T4b; final fighter-art and production gates in the parent plan remain unchanged. The first deliverable is the exchange, not a whole-short re-edit.

## Intent And Acceptance

The operator selected screen-plausible, reusable mechanics, **not** a quantitative injury/force-prediction model. The structure must be anatomically credible and its calibrated parameters and effects inspectable. “Real hand mass” means a hand/glove mass and inertia contribution inside a planted-feet, hip, torso, shoulder, elbow, wrist and fist kinetic chain; the nominal 4 oz glove does **not** equal the effective striking mass. No particular punch force, concussion, skull fracture or brain response may be inferred from a picture or an unvalidated formula.

| ID | Observable acceptance |
|---|---|
| H1 | A versioned editable hand/wrist asset has 27-bone anatomical reference landmarks (8 carpals, 5 metacarpals, 14 phalanges), forearm landmarks, joint axes, four-knuckle striking plane, a compact closed fist with the thumb bracing **outside** the folded fingers, and a skinned outer surface. Bare-hand closure visibly stages MCP flexion into the palm, PIP flexion toward the wrist/palm, then DIP fingertip tuck; the thumb must not be trapped under the fingers or pierce them. A glove-limited partial claw is not a bare-hand T2 pass. This does not require 27 independently simulated rigid bodies or literal ligament/tendon meshes. Document which ligament/tendon constraints are represented as joint limits/couplings and which are not modeled. |
| H2 | Neutral/guard, approach, first right-hand contact, left-hook contact and retraction show forearm-to-metacarpal alignment, no implausible wrist collapse, curled fingers inside the fist silhouette and no thumb/knuckle collision. Report anatomical landmark angles and evaluated-mesh distortion separately. Guard itself must pass; guard-relative quaternion delta alone is not a wrist measurement. |
| H3 | Contact is measured from the evaluated **knuckle/glove exterior patch to the target surface**, with signed separation/penetration and surface normal, not a palm world-X extremum or unsigned nearest distance. Approach velocity, normal, penetration budget, contact start/end, receiver displacement and retract-to-guard are traceable on the pinned source clock. No pre-contact head snap or hand tracking the moving head after impact. |
| H4 | A deterministic backend-neutral strike/contact record with explicit units, mass/inertia/compliance inputs, source timing, pose and impulse/reaction outputs yields identical event/contact ordering in Blender 3D and 2.5D/minimal 2D adapters. Render style may alter silhouette, hit-stop, squash, aura and camera response but must label such multipliers and preserve the physical baseline for comparison. |
| H5 | One straight punch and one lead hook, plus a body-target fixture, demonstrate distinct pivot/velocity paths while reusing the hand/contact contract. A minimal stick figure rendered with the same underlying record visibly communicates a compact heavy hit without enlarging its arm/hand. Operator judges phone-size contact sheets and motion clips; numerical tests alone are not visual acceptance. |

## Scope

- Preserve the source fight footage, V12 edit, accepted episode, current `fight_motion.py`, `contact_transfer.py`, and saved diagnostic `.blend` as immutable baseline inputs. Implement opt-in successor modules and write review output under the ignored benchmark area. Never silently promote a failed review shell.
- Build the hand as an articulated, externally skinned **asset**, not a full finite-element anatomical simulation. The 27-bone guide establishes proportions and pivot placement; strike stability is a braced-wrist constraint/coupling, fitted fist pose, contact patch and body-driven hand trajectory. Use measured literature as a plausibility range and document calibration rather than treating generic constants as fighter-specific truth.
- Define effective mass along the contact normal from the chosen articulated-body approximation or a documented calibrated proxy. Store ordinary hand/glove mass separately from effective striking mass. A style multiplier acts on a copy of the baseline response with explicit provenance; it cannot move the physical contact earlier or hide a missed punch.
- Do not use a Hertz sphere-plane law as an unqualified fit for irregular gloved knuckles/head/body; select and calibrate a simple contact-response profile against the rendered reference and disclose its limits. Deterministic bakes/closed-form evaluations must survive out-of-order seeks.
- The 3D adapter owns mesh, skin, pose and render passes. The 2.5D/2D adapters consume the shared timed anchors, normal, velocity and impulse to drive authored layers, pivots, receiver arcs and effects; no requirement that a stick figure display 27 bones. The existing native scene-evidence player remains the assembly path.
- The glove is a second layer fitted to the proved closed fist: hand-shaped, wrist-opening and four-knuckle exterior, with its own contact material and nominal mass metadata. It must not substitute a cuff-like capsule for missing hand geometry or bend the wrist to achieve contact.

## Not Building

- Medical/injury prediction, fracture, brain dynamics, tissue damage, or a subject-specific finite-element hand.
- A new general physics engine, new video player, full octagon, broadcast booth, roster, or complete short in this slice.
- Production approval of fighter likeness, final glove art, or any of the five style variants merely because the contact contract or test scene passes.

## Human Gates

- **Plan approval:** operator chose the screen-plausible/non-medical boundary on 2026-09-24 and then invoked `$prp-implement` on this draft. Scope approved for local implementation; no push, production release, paid provider action or operator visual verdict is implied.
- Reuse parent plan **HG2** for fighter art/hand closeups and **HG3** for paired finished exchange. No new review-queue gate is invented. Parent visual review of each diagnostic proof is required but does not close HG2/HG3.

## Mandatory Reads

- `AGENTS.md`, `docs/AGENT_START_HERE.md`, `docs/agent-context/SKILL_ROUTER.md`, `docs/AGENTS-VIDEO-ENGINE.md`, `docs/runbooks/PRP_EXECUTION.md`, `docs/WORKTREE-REGISTER.md`.
- `.claude/PRPs/plans/SHARED-MODEL-ENGINES.plan.md` T4b/T5b/T7b and HG2/HG3; `.claude/PRPs/plans/knockout-five-animated-variants.plan.md`; `content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/exchange-first/HAND-CONTACT-LEDGER.md`.
- `content/video_engine/src/modeling/motion.py`, `blender/fight_motion.py`, `blender/contact_transfer.py`, `blender/hand_pose.py`, `blender/contact.py` and their focused tests.
- `docs/research/motion/3D_RIGGING_AND_COMBAT_IMPACT_PHYSICS_RESEARCH_BLUEPRINT.md` and linked raw impact/rigging evidence, with provenance and numerical claims checked before reuse. Operator-provided wrist diagrams and linked wrist anatomy article are anatomy references, not licensed production textures. The primary hand-FE and boxing-impact studies are bounds/validation examples, not directly portable calibration for this fighter.
- Load `blender-motion-state-inspection` before rig/pose inspection and the applicable generation skill before generating any new visual asset.

## Execution Path

Evidence/baseline and declared tolerances → hand landmarks/fist asset → arm/wrist/knuckle retarget → contact and response record → glove exterior and target variants → 3D/2.5D/minimal-2D proof → parent visual review → existing HG2/HG3 only when all their other inputs exist. Parent owns architecture, integration, protected actions and acceptance; bounded agents, if dispatched later, receive separate write sets and exact evidence/stop rules. No pushes or provider purchases are authorized by this plan.

## Patterns To Mirror

- `model_scene.v1` exact rational clock, semantic contacts/events and typed units in `src/modeling/motion.py`; extend compatibly rather than starting a rival timeline.
- Existing opt-in Blender review/reopen/hash receipts in `blender/hand_pose.py`; include saved-scene, code, fixture and source hashes, scripts-disabled reopen and shuffled seek.
- Existing T7a Blender-to-layer bridge for fixed-source-view 2.5D; same source contact event but explicit render-profile deltas.
- Existing 2D planar IK/DQS rig foundation is a math reference only; its proxy art and whole-volume claims are not accepted.

## Task Slices

### T1: Freeze reference clock, topology requirements and measurement budgets
- Status: complete (negative baseline proved; no hand/contact art acceptance)
- Owner: parent/architect
- Depends on: plan approval
- Write set: ignored `content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange/hand-foundation-baseline/`; scoped source-exchange fixture/probe and focused test; parent-plan amendment if execution order changes
- Acceptance: pin exact source `.blend`, code, fighter/target geometry, source frames and render profile. Declare signed-surface, wrist-angle, mesh-clearance, planted-foot and screen-space budgets **before** candidate review. Record current negative values: bind ~4.7°, guard ~93.4°, jab f10 ~60.3°, hook f24 ~106.6° skeletal elbow-wrist-MCP angles; f10 prior glove unsigned gap 52.9 mm. Distinguish these diagnostic values from physiological joint angle or signed contact.
- Validate: reproduce the saved-scene wrist diagnostic and existing focused hand/contact tests without modifying baselines.
- Evidence: `content/video_engine/tests/fixtures/modeling/blender/characters/source-exchange/hand-foundation-baseline.v1.json` pins the source video/clock/character/fixture and old code; `inspect_hand_wrist.py` prints all 11 selected frame landmark measurements from the saved scene. The ignored review folder holds `contact-transfer.blend` SHA-256 `3c1aad6de3d0a3b4525e547646ff79274ed55f0a931c86aaf42d8cf75656943e`, its receipt and eight 540×960 renders. Blender 5.2.2 reopened scripts-disabled and verified frames 0–35 plus the renders. Rest is 4.7005°, guard f0 93.4011°, jab f10 60.2714°, hook f24 106.5978° by the stated elbow-wrist-MCP centerline metric, not carpal flexion. Parent viewed f10/f24 and rejected the current closed-fist/contact silhouette. The fixture declares engineering budgets, not physiology: ≤30° guard/recovery, ≤20° strike contact, signed knuckle-target gap −5 to +8 mm, ≤6 projected px at 540×960, ≤2 mm unintended hand self-penetration, ≤10 mm planted-foot slip/floor penetration and ≤2 mm pre-contact head movement. Prior 52.9 mm unsigned glove gap remains separately labeled Sol evidence, not a measurement of this glove-free scene. New fixture tests: 2 passed on 2026-09-24. No source inputs changed.
- Budget rationale: the 20°/30° centerline gates demand visibly braced contact and a less strict moving guard; they are not clinical wrist ranges. The ±5–8 mm world gap and 6 px screen gap are paired so a mathematical near miss cannot pass at phone size. The 2 mm self-penetration tolerance applies only to unintended mesh overlap, not deliberate finger/palm contact. Foot and pre-contact head budgets are inherited from the pinned source-exchange fixture for parity. Parent may revise a budget only with a new measured fixture and visual comparison, never to turn a failed candidate green silently.

### T2: Editable anatomical hand, fist and skin stress proof
- Status: running
- Owner: bounded implementation; parent judges art/structure
- Depends on: T1
- Write set: new versioned hand asset/manifest under `content/video_engine/assets/modeling/native/hands/`; new opt-in `content/video_engine/src/modeling/blender/hand_foundation.py`; focused `content/video_engine/tests/test_model_hand_foundation.py`
- Acceptance: H1; source and rendered mesh, landmark/axis map, hand COM/inertia metadata, staged MCP/PIP/DIP bare-hand closure and thumb opposition into a compact fist, open/guard/impact stress poses. Record topology, weights, skin-volume mask coverage and evaluated surface distortion. No glove yet.
- Validate: focused pytest + headless Blender saved-scene reopen + same-camera palm/dorsal/side and 9:16 contact-size renders.
- Evidence: editable `.blend`, manifest, receipt, views and parent visual verdict. All three Luna submissions failed on 2026-09-24 in the isolated `mm-hand-foundation` worktree. Attempts 1–2 had thumb-to-finger skeletal clearance 0.1065 m, an invalid 1.89x volume ratio from an open crop, and overlit views; preserved group mapping did not improve geometry. Attempt 3 used evaluated shape-key surface and joint-response probes: middle/ring closure and thumb clearance improved, but the index tip remained 29.634 mm from palm and pinky DIP tuck was −0.884 mm. Parent inspected dorsal/palmar/side/phone renders and rejected the broken fist/skin silhouette; Blender reopen and 4 focused + 3 isolation tests pass only technical gates. The uncommitted v1.2 asset in the worktree is **negative evidence, not approved/integrated**. Sol xhigh diagnosed the derived crop (281 boundary edges, eight cap components) as the leading defect and recommended stopping v1.2 salvage. Separate read-only T2B on the untouched full source also failed H1: its best bounded pose left index/middle/ring/pinky tip-to-palm gaps of 12.6/11.3/8.2/8.7 mm and 413 nonadjacent thumb/finger triangle overlaps; the source hash remained unchanged. The full source has usable staged finger controls, but pose tuning alone is not a closed fist. Stop salvaging the crop or reposing the full source. Next, preflight an accessible commercially usable hand starter or build a reference-sculpted corrective fist from intact topology; judge actual evaluated mesh and phone-size silhouette before integration. No T3 dependency opens until a credible hand passes H1.

### T3: Wrist/arm/knuckle retarget, head-contact proof
- Status: pending
- Owner: bounded implementation; parent reviews math
- Depends on: T2
- Write set: new opt-in `content/video_engine/src/modeling/blender/strike_retarget.py`; focused `content/video_engine/tests/test_model_strike_retarget.py`; review artifacts
- Acceptance: H2 and skeletal part of H3. Solve arm IK and hand orientation together to put the braced knuckle patch at the authored target; report clamped solved endpoint and residual. Keep shoulder/elbow/wrist/knuckle axes, normal and target local frames explicit. Recheck hand skin volume independently. Do not change old fight or contact-transfer modules in place.
- Validate: Blender evaluated-bone and mesh witness tests at guard, f10/11, f24/25 and retract; negative tests for unreachable target, mirrored side, invalid pose, surface miss and out-of-order frame seeks.
- Evidence: same-view before/after and diagnostic receipt; stop if actual signed contact or wrist alignment fails.

### T4: Style-neutral contact/response contract
- Status: pending
- Owner: parent contract; bounded implementation in new module
- Depends on: T3
- Write set: compatible additive schema/evaluator in `content/video_engine/src/modeling/motion.py` or a narrowly named companion `strike_contact.py`; `content/video_engine/tests/test_model_strike_contact.py`; schema fixtures
- Acceptance: H3/H4. Separate mass of hand, glove and articulated effective strike; record approach velocity, signed patch separation, normal, impulse/contact duration, receiver mass/inertia approximation, translation/rotation response, recoil/retraction and floor reaction. Source event times are authoritative; effect timing is a separately marked stylization. Report units, calibration values, residuals and uncertainty. Do not claim empirical force or injury accuracy.
- Validate: pure deterministic property/unit tests, symmetry and conservation/sanity checks where assumptions apply, missing-value/out-of-bounds tests, head/body target variants, rational-time and shuffled-seek parity.
- Evidence: versioned contract fixture and machine-readable baseline-vs-stylized receipt.

### T5: Fitted glove and cross-style exchange proof
- Status: pending
- Owner: bounded separate art/adapter tasks after T4; parent integrates
- Depends on: T4
- Write set: new glove asset under `content/video_engine/assets/modeling/native/hands/`; opt-in 3D and existing-layer adapters in their owned modules; targeted tests/review artifacts
- Acceptance: H5. Glove's exterior is fitted to and weighted with the hand, not a free-floating shell; its 4 oz nominal mass is recorded separately from effective punch mass. Straight and hook use distinct paths; same contact/receiver data drives an editable 3D scene, layered 2.5D view and a minimal 2D/stick-figure view. For each, show pre-contact, peak contact, first response, hand retraction and follow-up frames in motion and at phone size. An explicit stylization control increases visible response without shifting contact time.
- Validate: adapter contract parity tests, full frame decode, reopened Blender scene, exact source-clock correspondence and parent side-by-side visual review. Existing fighter art/production gates remain open.
- Evidence: hash-bound source scene, layer metadata, 3 preview clips/contact sheets, timings and parent verdict.

## Verification

From repository root, first run the existing baseline suites below; each slice then adds its own focused tests and visual receipts. Exact new commands are pinned in T1 before implementation rather than pretending they already exist.

```powershell
python -m pytest content/video_engine/tests/test_model_hand_pose.py content/video_engine/tests/test_model_fight_motion.py content/video_engine/tests/test_model_fight_motion_contact_transfer.py -q
python -m pytest content/video_engine/tests/test_model_motion.py -q
```

Four independent verdicts remain separate: contract/math, saved artifact integrity, visual/contact quality, operator approval. A numerical signed-gap pass cannot approve a fist that looks wrong; a compelling frame cannot prove contact, wrist geometry or source timing. Measure the floor and whole body as well as the hand so a convincing fist does not float.

## Evidence And Handoff

Recall: `docs_find.py` found the shared-engine capability/backlog and the combat-impact blueprint, but no direct hit for “hand wrist rigging”; this plan is grounded in source modules and the saved `HAND-CONTACT-LEDGER.md`. The raw combat research contains secondary/unverified numerical claims; none becomes a runtime constant without a primary source or benchmark calibration. Primary hand FE work demonstrates the validation burden of detailed tissue simulation, while boxing studies support treating effective punch mass as more than glove/hand mass.

Keep the approved video assets, source fight media, old `.blend`, failed glove shells and operator-provided references unchanged. Commit only reviewed source/test/doc slices; ignore generated review outputs as specified by the existing engine plan. Update `CAPABILITIES.md`, `BACKLOG.md` and the parent PRP only when corresponding proofs have actually passed, checking concurrent Fable edits before integration. Nothing in this draft certifies finished fighter art, injury science, a production-ready short or permission to push.
