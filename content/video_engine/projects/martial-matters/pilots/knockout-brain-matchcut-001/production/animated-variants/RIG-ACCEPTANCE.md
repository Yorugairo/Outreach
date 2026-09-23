# Native rig/contact proof — parent acceptance

User approved implementing the deeper on-file rig, skinning and human-motion research. This is a new project-local proof, not approval of earlier Flow motion or finished five variants.

## Architecture boundary
- Pure frame/time pose evaluator, independent of renderer and appearance.
- Analytical two-link IK with explicit bend side and reachable-target handling; fixed bone lengths.
- FK for free swing, contact targets for planted extremities; explicit event timing, not a spring applied to the entire figure.
- Authored weight transfer and separate pelvis, torso and head response channels. Balance diagnostics inform choreography; do not present a stylized animation as a measured biomechanical reconstruction.
- Skin deformation is a distinct layer. A normalized rigid transform per vertex does not prove that the spatially varying mesh deformation preserves area or volume. Test mesh triangles and joint transitions directly.
- Render filled silhouettes with readable faces/shorts for the proof; detailed character art is a later acceptance, not implied by correct geometry.

## Required observations
1. Right fighter lands right straight then left hook; left fighter falls. Inspect arm ownership visually, not just event labels.
2. Sample densely around contact. Actual glove/head surfaces must meet before the recoil/brain event, with no premature recoil.
3. Every arm/leg link retains its declared rest length; targets outside reach are reported, never silently achieved through stretched bones.
4. Planted-foot positions remain fixed until explicit release. Report maximum slip and intervals.
5. Head response precedes torso response; complete follow-through remains visible.
6. Entire falling character stays in frame, reaches the mat, and settles without penetrating it. Bone-joint clearance alone is insufficient: account for rendered body radii.
7. Frame evaluation in reverse/random order equals sequential evaluation.
8. Four-second silent proof decodes fully. Silence is intentional for motion review; original source audio remains unchanged.
9. Skinning tests distinguish identity, rigid transformation, blended joint deformation and degenerate cases; no unsupported universal volume-preservation claim.

## Constraints
No new provider spend, no publishing, no shared engine changes, no overwrite of previous outputs. Current checkout is dirty; preserve unrelated files. TPM feature map and pre-staging register paths are absent in this checkout; existing video project scope and this acceptance document govern this slice.

## Review status
Technical checkpoint: parent rig-skinning suite passes 13 tests. Four-second joint skinning and rig/contact diagnostic videos rendered and fully decoded; parent viewed maximum joint bend, first contact and final ground frames. Actual DQS is integrated into the torso, with authored weights; BBW is not implemented. Diagnostic proxy artwork is explicitly NOT accepted character art. User called its roughness out, and the next visual stage must use the approved detailed direction. Tests alone cannot approve visual quality; authored pose refinement and art binding remain.
