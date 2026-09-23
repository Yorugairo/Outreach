# Stylized 3D fight preview — technical proof

Status: **review-only quarantine / rough rig-blockout experiment**. This is a real Blender scene and playable motion proof, not final character art, operator approval, or a finished short.

## Evidence

- `build_stylized_fight.py` builds the scene from editable mesh primitives and creates two hidden-from-render armatures plus nested `CTRL_*` controls.
- `stylized-fight-preview.blend` contains the portrait scene, materials, camera, lights, modeled characters, animation, and inspection metadata.
- `scene-contact-inspection.json` records 94 scene meshes, both armatures and controls, face/garment roles, and samples at frames 1/24/48/60/72/84/96.
- `character-still-guard.png`, `character-still-contact.png`, and `character-still-fall.png` are actual Blender renders.
- `stylized-fight-preview.mp4` is 540x960, 24 fps, 96 frames, 4.000 seconds. `ffprobe.json` returned 0; `full-decode.json` returned 0.

Frame evidence: frame 1 is guard; frame 48 has `contact_candidate=true` with the right fist at 1.1015 units from the left head; frame 60 is follow-through; frame 96 records `left_head_ground_contact=true`, `left_torso_ground_contact=true`, `left_body_ground_contact=true`, and `support_hand_ground_contact=true` while the right fighter remains upright.

Blender 5.2 did not expose the legacy FFMPEG output enum, so the animation was rendered as 96 PNGs in `render_frames/` and encoded locally with ffmpeg. No audio or brain symbol is included in this bounded proof.

## Explicit limitations

The parent review identified visible crop/coverage at the left fall, loose-looking joint gaps, and a long-lived oversized impact ring. The scene is therefore quarantined and not visually accepted for the final 3D short. Do not expand it as final film work without a separate character-art/rig pass and renewed review.
