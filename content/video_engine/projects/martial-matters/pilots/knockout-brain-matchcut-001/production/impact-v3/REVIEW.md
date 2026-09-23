# Modeled-brain correction

Status: revised full short rendered and verified for private review.

- Rejected version: a brain-textured plane with black-background transparency defects. It is not the delivered moving object.
- Replacement: both anatomical cortical hemispheres from Nilearn/FreeSurfer fsaverage5, 20,484 vertices and 40,960 triangles. The surface has depth; it is not an inflated flat silhouette.
- `brain_model.py` creates the Blender mesh and physical gold/cyan-lit material. Brain material has zero image textures.
- `mesh-inspection.json` records model bounds and geometry counts. `motion-projections.json` records actual Blender camera-space bounds and three-axis rotation at contact, launch and exit.
- Effect frame 31: projected brain width 25.73% of the portrait frame; geometry camera-depth span approximately 146.67 scene units.
- Effect frame 80 / 2.1 seconds: rightmost projected brain vertex is left of screen; the entire mesh has exited. Rotation continues on all three axes.
- Parent inspected actual rendered frames 31 and 65: cortical folds, physical shading, no black rectangle, matched skull framing. Denoising enabled for final frames.
- Skull/arena remain composited background plates, not a claimed fully modeled anatomical skull. The background plate was cleaned of its painted brain before adding the real mesh.
- All imagery is stylized and bloodless; the generic mesh is not evidence of a clinically diagnosed injury.

## Reproduction

Run `assets/convert_surfaces.py`, then Blender with `../impact-v2/motion/xray_impact.py -- --render`. That scene imports `brain_model.py` and saves `../impact-v2/motion/xray-impact.blend`.

After rendering, run `../impact-v2/prepare_revision.py --picture` and the separate `../assembly-v2/build_assembly_v2.py` adapter. The old v1 output remains unchanged.

## Complete export

- `../assembly-v2/build/render/knockout-brain-matchcut-001-v2.mp4`: 1080x1920, H.264/AAC, 24 fps, 590 frames, 24.618 s container duration.
- SHA-256: `529174A7E639533CEDDD830F109C8B1C150955DB68823C06912CB211D6B3653A`.
- Full video/audio decode: ffmpeg exit 0. Merged impact module: 111 frames at 30 fps, exactly 3.700 s; decode exit 0.
- Parent inspected `final-boundary-review.jpg` extracted from the actual final MP4: live punch -> scan/push -> modeled brain inside skull -> fracture/ejection -> empty skull -> Henderson/Bisping. No standalone brain diagram or black brain rectangle.
- Packed Blender scene: `knockout-xray-3d.blend`, 7,162,641 bytes, all four background images packed. Real cortical geometry is stored inside the blend.
- Two assembly tests passed. Parent fixed the adapter's invalid `BASE.MG` reference found only by real compile; the full render subsequently completed exit 0.
- Existing general motion gate still reports M11 (no chart) and M16 (clip motion not credited). Specific private-review override retained in the render receipt; no claim these gates passed.
