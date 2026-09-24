# MM-HAND-01 — closed-fist contact on the editable fighter rig

Status: ready for a bounded modeling pass after the opt-in contact-transfer helper is reconciled. This is a review-only, option-gated strike pose/look; it must not silently change the existing source exchange, episode, or default builder. Parent owns visual approval and integration.

## Evidence and defect

- The Rigify fighter has weighted palm, finger, and thumb chains. The missing piece is not a finger skeleton: existing frame-0 Euler curls still render as a soft/open hand at jab f10 and hook f24.
- The present exchange carries a cached hand-IK world rotation into the strike while contact correction translates the IK target. A stable target quaternion is **not** evidence of a braced anatomical wrist. An independent v3 diagnostic found large actual hand/forearm axis deviations (~56° jab, ~78° hook); calibrate those numbers against rig rest axes before treating them as wrist flexion angles.
- The current contact-transfer proof makes the jab/hook recoil and quick withdrawal measurable, but its numeric proximity does not yet prove knuckle contact. Preserve the honest review-only status until the actual surface and wrist are verified.

Source entrypoints: `content/video_engine/src/modeling/blender/fight_motion.py` (`_hand_target`, `_key_exchange`, `_key_fists`), opt-in `content/video_engine/src/modeling/blender/contact_transfer.py` (`_key_strike_fists`, `_align_contact_hand`, `_arm_state`), pinned `content/video_engine/assets/modeling/native/fighter-family-v1.1.blend`. Read the final contact-transfer diff/receipt first; do not build against a preliminary v3/v4 receipt.

## Owned implementation

1. Add a strike-specific closed-fist pose using the existing finger/thumb/palm rig. At impact the thumb is wrapped, fingers compact, and the second/third knuckle region or an explicitly modeled glove pad leads. Do not use summed Euler magnitude as a closed-fist gate.
2. Orient the hand target relative to the approaching forearm and contact normal. Measure actual evaluated hand-versus-forearm orientation after the arm IK solves, calibrated to the rig's neutral wrist; target no more than 20° flexion/deviation during the brief contact window. Preserve elbow continuity and retreat to a relaxed guard pose afterward.
3. If the bare mesh cannot read as a fist at 540×960, add a small reusable MMA-glove shell bound to the existing hand/finger rig behind the same option. The shell is visual/contact geometry, not an artificial force multiplier or a claim to model tissue stiffness. Include its leading surface in the contact witness. Do not substitute a flat image or alter the pinned source `.blend`.

## Acceptance and evidence

- At source-timed f10–11 jab and f24 hook, phone renders show a compact closed fist and neutral-looking wrist with the knuckle/pad face pointed into the receiver, no splayed digits or bent-back hand. An independent reviewer must see the fist at normal phone size, not only in a zoomed crop.
- Evaluated leading surface to head is within 10 mm at contact, with axial penetration no deeper than 5 mm; report which surface vertices and contact normal were used. A small numerical gap without a visible touching silhouette is a fail.
- The hand separates promptly after contact; by f12/f25 the receiver reacts and fist/head distance grows at least 15 mm; the striking hand returns to within 60 mm of guard by f15/f28. Keep planted-foot checks green. The hook should retain the larger authored hip pivot/reaction, without claiming real injury or force simulation.
- Save a distinct review scene, eight 540×960 key renders, phone-size jab/hook comparison sheet, full 36-frame receipt, script-disabled reopen, exact input/output hashes, and focused tests that go red on open fist, wrist misalignment, over-penetration, deep follow-through, or floating feet. Do not mark the look or fight physically accurate by test result alone.

If the bounded shell/pose approach still fails phone-scale review, stop at diagnostic evidence and escalate the **art/rig design** decision. Do not silently weaken contact or wrist thresholds to obtain a passing receipt.
