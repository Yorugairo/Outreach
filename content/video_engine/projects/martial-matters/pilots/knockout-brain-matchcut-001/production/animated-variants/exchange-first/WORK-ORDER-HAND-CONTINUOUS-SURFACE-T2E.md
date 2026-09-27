# MM hand T2E: continuous fist surface blockout

Status: Sol xhigh rewrite after three failed T2D static submissions. One targeted Luna retry only. This is not an approved hand, glove, rig transfer, contact solve, or episode asset.

## Pinned basis and diagnosis

- Duplicate the immutable `content/video_engine/assets/modeling/native/fighter-family-v1.1.blend` (SHA-256 `5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade`). Keep the source unchanged and work in a registered isolated worktree.
- Read `WORK-ORDER-HAND-ORIGINAL-SURFACE-T2D.md` and its thumb/wrist addenda, then the T2D v1/v2/v3 receipts and matched rendered views in `review/model-engines/benchmark-v1/3d/hand-foundation/original-surface-v1/`. The Sol diagnosis is: v1 remeshed an incomplete selected patch; v2 moved only 391 vertices by at most 3.135 mm and retained the finger tubes; v3 fused palm/knuckle ellipsoids and full finger capsules into a manifold but mitten-like form. More vertices or smoothing do not address the silhouette.
- Preserve the source thumb pose (CMC X -25 degrees, Z +30 degrees; MCP/IP X +40 degrees) as a starting bone guide only. Its measured clearance does not validate a newly built surface. The thumb must stay compact at the radial side through, at most, over the outside/top of the index; never across the palm or middle/ring fingers.

## Bounded task

1. Trace matched dorsal, striking-edge, side, and palmar fist silhouettes from the source anatomy references. Before subdivision, build **one continuous posed hand surface** with a broad, subtly four-peaked transverse contact brow at the MCP row. Folded digits sit behind/below that brow; their distal capsule ends and independent oval pads must not form the visible striking face. Keep the palm/web volume and an exterior, compact thumb. Do not repeat ellipsoid/capsule unions, broad weight-group translations, or lighting concealment.
2. Stop at low-resolution ordinary-clay blockout. Save/reopen a derived `.blend` and render source-versus-candidate dorsal, palmar, side, unlit silhouette, and 540x960 contact views at matched camera/scale. Report shell integrity, thumb/index signed clearance, unintended penetrations separately, local wrist boundary, source/derived hashes, and exact script/scene paths. The existing open wrist boundary is documented; welding and rig transfer are deferred at this gate.
3. Parent visually judges the static H1 gate. Fail if the shape reads as a mitten, tube-ended fingers, separate oval pads, long thumb loop, open palm cavity, or an unconvincing four-knuckle contact edge at phone size. If it fails, **stop this Luna retry**. No second smoothing/density pass, glove, skinning, fight integration, commit of an asset, or production approval.

## Separate urgent shot proof

The Sharaf-over-footage diagnostic may use a shot-specific black glove shell or rig-driven 2.5D glove contour without waiting for bare-hand H1. Label it a contextual composite proof, not a reusable hand pass. At source f10 require a rigid fist-wrist-forearm line and first contact without through-head extension; at f24 a compact hook contact edge with no visible finger capsules; at f25 glove retraction and an unobscured real head snap. Keep the actual source clock, opponent, cage, and broadcast layer. Supply source/candidate glove masks, elbow/wrist/MCP anchors, contour/centroid errors, and 360x640 plus 720x1280 composites. Reject gray/incomplete glove, double Sharaf, wrist collapse, or a persistent glove attached to the head.

## Ownership

The worker owns only a new T2E derived scene, focused authoring script, quarantine renders/receipt, and worktree-register row. Parent owns the visual verdict and integration. Do not alter the immutable source, T2D evidence, episode, player, fight/contact modules, or any third-party starter hand geometry. No push is authorized.
