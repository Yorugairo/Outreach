# Rig foundation slice

## Scope

This directory owns a deterministic, seek-safe planar pose/contact foundation
for the 4-second review proof. It is intentionally schematic diagnostic
geometry, not approved character art or a final production rig.

The pose layer provides:

- analytic fixed-length two-bone IK for hands and feet, with explicit
  reachability and target error;
- FK-authored right straight and same-fighter left-hook arcs, including a
  nonzero velocity through each contact and a separate head/torso response;
- explicit planted-foot constraints, an authored attacker step release, and a
  victim fall that keeps rendered capsule surfaces above the mat;
- a deforming filled torso mesh using the parent-owned planar unit
  dual-quaternion implementation when available;
- per-frame measurements for contact gaps, velocities, link lengths, foot
  slip, head/torso lag, brain release, floor clearance, and signed triangle
  orientation.

## Acceptance receipt

`measurements.json` is the generated deterministic receipt and
`timing.json` is the compact event timeline. The current receipt reports:

- 96 frames at 540x960, 24 fps, 4 seconds;
- right straight contact frame 27 (1.125 s), head recoil/brain release frame
  28, left hook contact frame 50 (2.083 s), fall release frame 54, ground
  frame 85 (3.55 s);
- zero measured surface gap at both contacts, nonzero contact velocities,
  zero fixed-link error, zero unreachable targets, zero planted-foot slip
  before release, and zero rendered capsule penetration;
- seek-order equivalence and signed triangle orientation checks passing;
- `global_volume_claim: false`: area is measured for this mesh and is not
  presented as a DQS volume-preservation guarantee.

## Commands

From the repository root:

```powershell
python -m pytest content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-foundation/test_rig_foundation.py content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-skinning/test_dqs.py content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-skinning/test_pose_contract.py -q
python content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/rig-foundation/build_measurements.py
```

The review MP4/contact frames are rendered by the parent-owned
`animated-variants/rig-skinning/render_rig_diagnostic.py`; this slice does not
change the shared scene engine and does not claim BBW weights or polished
character art.

## Review artifacts

- `measurements.json` and `timing.json` — pose/contact receipts;
- `contact-sheet.png` — 16-sample sheet from the parent diagnostic frames;
- sibling review render: `../rig-skinning/rig-contact-diagnostic.mp4` (540x960,
  24 fps, 96 frames; ffprobe/decode verified by the parent render command).
