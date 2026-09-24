# MM-HAND-IMPACT-FOUNDATION T2 — editable hand and closed-fist proof

Status: frozen on dispatch. Owner: `implementation_luna` in its own worktree. Parent owns contract changes, review, integration, gates and Git actions. This is the **hand before glove** slice; no head contact, force solver, episode cut or fighter-art approval is claimed.

## Recall and fixed inputs

- Plan: `.claude/PRPs/plans/MM-HAND-IMPACT-FOUNDATION.plan.md`, T2 and H1. The source-clock/negative-budget fixture is `content/video_engine/tests/fixtures/modeling/blender/characters/source-exchange/hand-foundation-baseline.v1.json`; source character `.blend` SHA-256 `5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade`.
- Read the tracked `content/video_engine/src/modeling/blender/hand_pose.py`, `authoring.py` (only relevant hand/asset sections), `fight_motion.py` (fist controls), and `content/video_engine/tests/test_model_hand_pose.py`. `HAND-CONTACT-LEDGER.md` explains why the prior three Luna glove shells and Sol capsule failed. Do not reuse those shapes.
- The saved review-only Blender scene is in the main checkout under `content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange/hand-foundation-baseline/`. Its scripts-disabled reopen verifies 36 frames. The parent viewed f10/f24: neither hand reads as a good closed fist. The measured elbow-wrist-MCP centerline is rest 4.7005°, guard 93.4011°, jab f10 60.2714°, hook f24 106.5978°. These are skeletal centerline angles, not physiological flexion; T3, not T2, will correct arm/wrist placement.
- Use operator-provided wrist anatomy diagrams and the linked anatomy article as references for bone groups/pivots, not as production textures. Primary subject-specific hand FE research (`https://pmc.ncbi.nlm.nih.gov/articles/PMC7089907/`) shows why detailed tissue force prediction is outside scope. Do not copy a source mesh unless its license/provenance is recorded and compatible.

## One bounded deliverable

Produce a versioned, editable, hand-local Blender asset and matching manifest that can be attached to the existing Rigify fighter without altering its source `.blend`. Include a believable closed fist with four fingertips folded into the palm, thumb safely outside/tucked, visible knuckle plane, wrist transition, and intact dorsal/palmar volume. A 27-bone **anatomical reference guide** (8 carpals, 5 metacarpals, 14 phalanges) must locate the pivots and contact plane, but do not simulate all 27 as rigid bodies. State which hand/wrist ligament/tendon effects are approximated as joint limits/couplings and which are omitted. Separately record hand mass/COM/inertia as declared metadata; no impact force or injury claim.

You may refine/retopologize the hand from the existing native fighter family or use a compatible, provenance-documented open starter. The decision is yours within the above constraints. Keep neutral outer mesh, control/guide rig and skinned final mesh inspectable separately; material/texture must not conceal geometry defects. Do not add a glove or remodel the target head to make the hand appear successful. If the available base cannot yield a credible fist in this bounded pass, return a negative art/rig diagnosis and a source recommendation rather than another capsule/proxy.

## Ownership and stop rules

Own only new `content/video_engine/assets/modeling/native/hands/` files, new `content/video_engine/src/modeling/blender/hand_foundation.py`, new `content/video_engine/tests/test_model_hand_foundation.py`, and ignored T2 review output under `content/video_engine/review/model-engines/benchmark-v1/3d/hand-foundation/`. You may add a small runner under `content/video_engine/tests/fixtures/modeling/blender/characters/hand-foundation/` if needed. Do not edit `fight_motion.py`, `contact_transfer.py`, `hand_pose.py`, the T1 baseline fixture/probe/test, the plan, player, docs, source footage or source `.blend`. You are not alone in the codebase; preserve others' edits, do not revert them, and adjust around concurrent changes. No provider generation, install, commit, push or production promotion.

Stop and report if: source license is uncertain; fist looks claw-like, mitten-like or capsule-like at 540×960; thumb intersects the knuckle patch; evaluated mesh collapses or tears under flexion; hand attachment requires changing the historic rig; or the work exceeds the named write set. One first submission and at most one bounded correction after parent visual notes—not unlimited polishing.

## Acceptance evidence

1. Editable `.blend` and versioned asset manifest: source/provenance hashes, topology counts at control/render levels, semantic axes and attachment, 27 reference labels, deform/control map, declared mass/COM/inertia and limitations.
2. Saved-scene neutral/open/guard/closed-fist stress poses; same-camera palm, dorsal, side, and 540×960 fist/forearm renders. Show clay and material views so shading cannot hide hand shape.
3. Measurements: four fingertip-to-palm paths, thumb-to-finger skeletal clearance and evaluated-surface interpenetration witness, local volume/edge distortion, knuckle plane and wrist attachment. Report actual values and explicit visual verdict, not only test booleans.
4. Headless Blender build and scripts-disabled reopen with source/code/render hashes; seek-order check across the stress poses. Focused pytest must run as `python -m pytest content/video_engine/tests/test_model_hand_foundation.py -q`. Run old hand-pose test to confirm isolation. Parent will inspect the source, diff and phone renders before integration.

Return at most 200 words with exact artifact paths, test verdict, source method and whether the first submission passes your own visual inspection. Do not call it approved; the parent/operator decide that gate.
