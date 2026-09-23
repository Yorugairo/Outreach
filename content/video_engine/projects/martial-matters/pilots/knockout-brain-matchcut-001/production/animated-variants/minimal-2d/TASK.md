# Minimal 2D fight proof — bounded task

## Acceptance criteria

- Produce an editable, code-native flat-vector animation with two readable adult fighters, simplified cage/floor, and no rasterized source art or generative providers.
- Render a 4.0 s MP4 at 540x960, 24 fps (96 frames), with central action and planted support feet.
- Show the authored beat order: guard anticipation -> right-hand contact -> head recoil/follow-through -> the same fighter's left-hook follow-up -> continuing fall to the ground.
- Actor assignment is fixed: the right bald/blue fighter lands both the right-hand contact and the left-hand hook; the left dark/red fighter recoils and falls.
- Keep the left fighter dark-skinned with short black hair/beard, black shorts and red wraps; keep the right fighter light-skinned, bald/bearded, white shorts and blue wraps.
- Show one symbolic golden cartoon brain leaving the head only during visible recoil; no gore, skull fracture, or injury detail.
- Ship a style render before final animation, the final MP4, a readable contact sheet, and timing JSON naming contact, recoil, follow-up, and fall.
- Validate frame count, dimensions, frame rate, duration, and full decode with ffprobe/ffmpeg; inspect representative rendered frames.

## Anti-goals

- Do not edit parent ledgers, shared engines, neighboring animated variants, or existing source assets.
- Do not use Blender, external providers, downloaded assets, or a third-party scene assembly engine.
- Do not claim operator approval, editorial release, or integration into the pilot from this proof.
- Do not use thin stick figures, photographic pixels, skull overlays, blood, or other gore.

## Write set

This task owns only this directory. Expected files are the editable renderer, timing manifest, style preview, final MP4, contact sheet, and local validation receipt.

## Execution status

- [x] Style preview rendered and sent for parent review.
- [x] Final 96-frame MP4 rendered from editable SVG geometry.
- [x] Contact and follow-up contact geometry recorded in timing.json.
- [x] Contact sheet inspected; fall recentered to keep the action readable.
- [x] Focused pytest and ffprobe/full-decode validation passed.
