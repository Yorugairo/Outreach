# Planar dual-quaternion skinning proof

`dqs.py` embeds planar rotation/translation in unit dual quaternions. Blends sign-align rotations, normalize the real quaternion and project the dual component to satisfy the Study condition. Input transforms must already include inverse bind transforms. This is a project-local prototype, not shared engine integration.

`render_joint.py` creates a four-second side-by-side linear-blend / dual-quaternion mesh-deformation demonstration with 96 frames and authored smooth weights. The sampled 0–120 degree bend has zero inverted triangles for the DQS mesh. The mesh visibly deforms; it is not a collection of rotating capsules.

## Verified
- `python -m pytest .../rig-skinning/test_dqs.py -q`: 8 passed.
- `python .../rig-skinning/render_joint.py`: 96 frames, FFmpeg full decode PASS.
- Parent inspected maximum-bend frame `joint-frames/0048.png`.
- Independent review checked multiplication, transform encoding, sign alignment and normalization. Malformed-transform and rotation-continuity tests added following review.

## Limits
- Planar points only, not a general 3D character pipeline.
- Weights are authored: bounded biharmonic weight optimization is NOT implemented.
- Each blended transform is rigid, but differing weights across a mesh can change its area; explicit counterexample is tested.
- Exact half-turn blend ambiguities need authored angle continuity. Tests do not establish all possible rig configurations.
- The joint demo does not establish fighter animation quality, balance, collision response or full-cut readiness.

Output: `joint-skinning-proof.mp4`, measurements in `joint-measurements.json`. All review-only.
