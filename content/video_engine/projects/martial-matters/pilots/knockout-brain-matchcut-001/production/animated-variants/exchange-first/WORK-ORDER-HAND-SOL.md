# MM-HAND-01 — Sol escalation: reusable closed-fist/glove assembly

Status: active, review-only. Three bounded Luna attempts failed phone-scale and geometric contact acceptance. This is a substantive modeling/design escalation, not another syntax retry. The Sol owner must resolve the assembly/contact contract before building. Parent owns integration and visual approval.

## Outcome

Make one reusable striking-hand assembly for the editable Rigify fighter that reads as a compact closed fist at phone size. Fit an MMA glove *to that posed hand*, not to the receiver's head or a world-space strike target. Use a configurable 4 oz (0.1134 kg) glove as the baseline added mass. The glove's knuckle pad, open-palm/finger structure, and wrist closure should support the fist silhouette and provide the collision surface; do not turn it into a rigid mitten. Separate glove mass/inertia, pad compliance/contact geometry, fist/wrist pose, and effective moving body mass in the data and claims. Do not use glove mass as an arbitrary force multiplier or claim that padding prevents injury.

The same assembly must support a head strike and a synthetic body strike without remodeling, rescaling, or relocating the glove relative to the hand. Contact target type only changes the receiving surface, strike placement, and receiver reaction. Brief contact, prompt withdrawal, guard recovery, and planted-foot motion remain essential. This is a visual/kinematic proof, not a tissue-injury or validated impulse solver.

## Existing evidence and negative examples

- Read `WORK-ORDER-HAND-CONTACT.md`, `content/video_engine/src/modeling/blender/contact_transfer.py`, and the 36-frame rehashed contact-transfer receipt under `content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange/contact-transfer-v5-rehashed/`.
- The native fighter already has weighted palm, finger and thumb chains; inspect their evaluated positions and bind axes. The old wrist-angle diagnosis used mismatched bone axes and must not be repeated.
- Read the failed candidates in `C:/Users/Snipe/.codex/worktrees/mm-hand-contact/Outreach Program/content/video_engine/review/model-engines/benchmark-v1/3d/source-fight-rig/exchange/hand-contact-shell-01/`, `-02/`, and `-03/`. The proposed blue capsule/strip loft was head-derived, visibly detached/sleeve-like, and failed the jab witness. These are negative evidence, not integration candidates. Do not merge that worktree's dirty `strike_glove.py` or `contact_transfer.py`.
- The pinned historical `fight_motion.py` and current `contact_transfer.py` produce hash-bound receipts. Keep them and the source `.blend` unchanged. Add an opt-in module/runner and a new review folder rather than invalidating those receipts.

## Bounded delivery

1. Write a short assembly/target interface note before geometry: hand-local glove vertices or an evaluated fitted asset; attachment to palm/finger/wrist bones; unit mass and center-of-mass/inertia metadata; separate head/body `StrikeContact` target. Mark any compliance value as illustrative unless independently measured.
2. Produce an opt-in pose and glove fitting proof on the saved fighter. Reuse existing Rigify hand chains or a properly weighted fitted glove asset. A head-centered pad, flat image, free-floating capsule, or hidden splayed fingers do not pass. The glove must remain on the fist through approach, load, and recoil.
3. Render both one jab-to-head and one straight/hook-to-body contact at 540x960, with approach, impact, separation, and guard-return frames. At contact show the pad/knuckle surface meeting the receiver, wrist braced in its calibrated neutral range, receiver displacement, and grounded feet. Neither strike may extend the fist through the target.
4. Save source/input/output hashes, hand-local fit and signed contact witnesses, render reopen/decode results, focused red/green tests, and a phone-size comparison sheet. Independently review visible continuity. Report any failure without weakening the threshold or claiming approved fighter art.

Initial geometric thresholds from `WORK-ORDER-HAND-CONTACT.md` remain: leading surface within 10 mm, no more than 5 mm penetration, no more than 20 degrees neutral-calibrated wrist deviation, separation >=15 mm by the next beat, return within 60 mm of guard at the specified later frames. A body target requires its own surface/normal witness; never reuse a head-specific extrema shortcut. If these thresholds conflict with a visually credible source pose, record the evidence and ask the parent to resolve it rather than silently alter them.

## Source discipline and stop condition

UFC's [official fight-glove redesign](https://www.ufc.com/news/ufc-announces-transformative-redesign-ufc-official-fight-glove?language_content_entity=en) describes curved finger holes, closed-fist fit, and wrist-locking construction. This informs *visual structure*, not a claim of injury prevention or a universal 4 oz specification. If a bounded fitted asset still cannot read at phone size, stop with a diagnosis of the art/rig constraint and hand it to the parent. Do not spend cycles on shorts fabric, broad new anatomy simulation, or a full-short render.
