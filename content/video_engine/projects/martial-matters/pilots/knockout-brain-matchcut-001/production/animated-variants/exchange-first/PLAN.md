# Exchange-first style variants — 2026-09-24

Status: approved direction, not yet a completed render or release approval. Two-day priority within `MM-KNOCKOUT-ANIMATED-5`; the five full remakes remain separate.

## Source and output contract

- Use the immutable Sharaf–Steveson source (`assets/raw/source-short/ufc-sharaf-steveson-high.mkv`, SHA-256 `c162dcb7e7a11336c5b0bd3b29d51ecbf2f8cd5a49f90a3b851775165da64758`) as the 105-frame, 30 fps exchange clock. The timing reference is `content/video_engine/tests/fixtures/modeling/motion/source-exchange-clock.v1.json`: first right contact near f10–11, left-hook contact f24, visible head snap f25. These are timing observations, not force or injury claims.
- Preserve V12 and source files. Output review-only 540×960 (or higher) MP4s with receipts, frame hashes, full decode and phone-size before/contact/recoil/ground sheets. Source audio remains original-pitch and continuous in any assembled short; image-layer effects may hold visually without time-warping audio.
- First playable looks: (A) footage-backed anime/2D transformation and impact composite; (B) characterized blocky/big-head 2.5D/3D look on the same clock, if it clears contact and recognizable-caricature review. Existing Saitama overlay is the baseline, not proof that full 3D is needed.
- Keep the native scene-evidence player as final assembly host. Use existing layered imagery for fixed-camera fighter looks; call Blender when actual depth/occlusion/head turn is needed. Do not build a second player. The generator/look provider is swappable; the source clock and composition contract are not.

## Fast-path shot grammar

1. Extract or reuse real source poses around pre-contact, f10–12, f23–26, and follow/recovery. Source frames provide fighter likeness, stance, direction, and contact geometry. A stylized still must be matched to one of those poses before animation or overlay.
2. Keep source action for velocity and reaction. Put the aura behind the attacker and contact accents over the image at authored frames. Do not obscure gloves, head snap, or grounded feet.
3. If a styled fighter is composited across frames, track body/head/hand/foot anchors and alpha occlusion explicitly. A single portrait texture is a fixed-view approximation, not a full 3D likeness or unseen-side solution. Reject drift and airborne feet at phone size.
4. The jab reads fast and linear; the stronger knockout hook reads as a tighter arc with hip pivot. On contact the fist stops tunneling and promptly retracts, the receiver recoils, and next-hand/head/foot motion may overlap at different rates. Do not hold the fist against the moving head.

## Two-day gate

- At least two distinct looks are playable for the **exchange**, source-timed and source-audio-safe, with a reusable style-swap recipe/manifest rather than hand-edited one-off clips. One may be an anime overlay over real footage; the other may use 2.5D/3D caricature if its visual gate passes.
- Contact, likeness, grounding, alpha edges, occlusion, and readability inspected on rendered phone frames. A decode or numeric motion pass alone is not visual approval.
- Report the actual completed styles; do not claim five finished shorts or a production-ready full 3D fighter scene. If B fails, preserve its evidence and ship A plus a second viable overlay/look variant, not a mislabeled 3D final.

## Non-gating exploration

Multi-view photo wrapping, video-wide identity-consistent rotoscoping, full 3D fight generation, broadcast booth, and reusable octagon are useful later. They are not prerequisites for this shot. `EFFECT-CANDIDATES.md` ranks the anime-research-derived effects without promoting any unrendered candidate to the proven effect catalogue.
