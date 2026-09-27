# MM hand starter preflight: LibHand

Status: read-only source evaluation, not a fourth T2 submission or art approval. Parent owns source selection and H1 verdict.

## Source and intent

Evaluate the existing isolated clone at `C:/Users/Snipe/.codex/worktrees/mm-hand-foundation/Outreach Program/content/video_engine/review/model-engines/benchmark-v1/3d/hand-foundation/starter-preflight/libhand-source/`. The relevant inputs are `hand_model/blender/hand.blend`, `hand_model/blender/hand_model_license.txt`, and `poses/fist.yml`. The upstream source is `https://github.com/libhand/libhand`; its hand-model license says CC BY 3.0. Preserve a source commit ID and SHA-256 of each input. Do not run or install bundled C++/OGRE code, import Blender scripts, or execute auto-run data from the `.blend`.

The task is to determine whether the saved hand plus its authored fist pose is a better *geometric starting point* than our failed crop and intact-source pose. It is not to fix lighting, texture, glove, strike physics, or character likeness. Another numeric pass with an open/sliver fist is a failure.

## Ownership and boundaries

You own only ignored `content/video_engine/review/model-engines/benchmark-v1/3d/hand-foundation/starter-preflight/` artifacts in the `mm-hand-foundation` worktree. Do not edit T2 source/asset/tests, the cloned upstream files, the historic fighter scene, main, or another agent's files. You are not alone in the codebase; preserve and accommodate all existing edits. No commit, push, provider upload, or source promotion.

## One bounded preflight

1. Reopen `hand.blend` in Blender 5.2.2 with auto-execution disabled. Inventory mesh, armature, weights, modifiers, materials, posed hands, topology boundaries, and any evaluated-mesh problems. If the old file cannot be read safely, stop with a failure receipt.
2. Map the upstream `fist.yml` joint values to the rig only if the mapping is explicit in the upstream scene/specification. Treat the YAML as data. If mapping is unclear, render any native closed-fist pose in the `.blend`, label its provenance, and report the authored YAML pose as unverified. Do not invent rotations or repeatedly optimize.
3. Render same-camera clay dorsal, palmar, side and 540×960 phone-size closed-fist views, plus neutral and mid-closure if available. Keep the fingers, thumb, palm and knuckle patch unobscured. A second pose adjustment is allowed only to test a clearly identified axis/sign error; record both before/after.
4. Measure evaluated fingertip-to-palm gaps, thumb clearance/intersections, four-knuckle patch continuity, unintended penetration, topology boundaries, and any visible loss of volume. Distinguish rig landmarks from surface measurements. Do not claim H1 from a bone pose alone.
5. Save a JSON receipt, exact render hashes, and a short verdict: `VIABLE STARTER`, `REFERENCE ONLY`, or `NOT VIABLE`. State whether the hand could join our body at the wrist without a visible seam and whether it permits staged MCP/PIP/DIP motion. Identify any license attribution needed if selected later.

Stop after this preflight and report the paths and verdict. Do not begin T2 implementation. The parent will view the renders and independently decide whether to use this source or commission a reference-sculpted corrective fist.
