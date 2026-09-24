# MM hand T2D: original posed-surface fist and wrist-integrated rig

Status: Sol xhigh reframe after three H1 failures on T2C. This is a new bounded T2 art/rig proof, not an accepted hand, glove, contact solve, or episode render.

## Source, ownership and provenance

- Duplicate the immutable full-body `content/video_engine/assets/modeling/native/fighter-family-v1.1.blend` (SHA-256 `5a99ce057520e332673230dd5367189a5e6dc7da56ca45da50c8a38b4f40bade`) into an isolated worktree and new versioned review scene. Keep the source unchanged. Read its manifest and the T2C attempt ledger/three rendered receipts before editing.
- Use the MPFB CC0-derived body and our Blender-authored sculpt/retopology. LibHand and CreativeMachine starter hands are **comparison references only**: do not transfer their geometry, topology, UVs, textures, weights or rigs. Avoid describing the resulting whole character as wholly scratch-built; identify the body basis accurately.
- Parent owns the H1 art verdict, integration, and any push. The execution worker owns only a new T2D derived hand asset/manifest, an opt-in rig/PSD helper and focused tests if the visual gate passes, and ignored review output. Register its separate worktree/write set before a commit. No edits to episode, player, fight/contact modules, T2C review artifacts or the original source.

## Sequence and stop gates

1. Inspect actual right-hand bone axes, MCP/PIP/DIP and thumb landmarks, edge loops, evaluated skin, weights/gradients, and both source Armature modifiers. Show neutral and staged closure at the same scale. Diagnose requested versus realized surface movement; nearest weighted-vertex gaps are not acceptance evidence.
2. On a **posed duplicate**, author an original closed-fist surface from the operator's anatomy references: compact fingers with distal pads seated behind the striking edge; four metacarpal-head/knuckle forms reading as one broad contact patch; continuous palm/web mass; thumb braced on the exterior of the index/middle fold. Sculpt the evaluated surface itself. Do not repeat broad weight-group tip translation, Gaussian bulges, or camera/lighting concealment.
3. First checkpoint is static bare-hand ordinary-clay art only: saved/reopened `.blend`, matched neutral/source versus candidate dorsal, palmar, side and 540×960 contact-size renders, plus a simple unlit silhouette. Parent must explicitly pass the rendered fist before rig transfer, glove, contact, or tracked production asset. If existing loops cannot carry a clean sculpt, create **original retopologized hand-region geometry** on a duplicate full-body mesh, joined at a measured wrist ring with no seam. This intentionally changes topology and requires a new asset version/manifest; do not force the 19,158-vertex source count.
4. After the static art pass, fit/paint deform weights to the existing Rigify family and bake a pose-space corrective into neutral/rest. Under both Armature modifiers, measure requested versus realized displacement. Render neutral → MCP → PIP → DIP → external thumb brace, then guard, wrist twist and contact orientation; inspect for collapse and mesh crossing. No impact physics or glove is authorized by this order.

## Acceptance and evidence

- H1 visual gate: at phone size and in dorsal/palmar/side views, the bare hand reads as a compact fist with a broad four-knuckle exterior, externally braced thumb, seated fingertips, no open palm cavity, exposed cylindrical finger ends, or wrist seam. Static sculpt failure stops rig tuning.
- Report evaluated triangle-level *signed* clearance at deliberate contacts and unintended crossings/penetration separately, with a ≤2 mm unintended-penetration target. BVH overlap-pair counts are broad diagnostics, not penetration depth or volume. Record local edge stretch, wrist continuity, volume/pinch failures, and source/derived file hashes.
- Preserve editable source, reproducible Blender version/scripts-disabled save-reopen, ordinary-clay camera/light settings, all iterations and ledger. Technical tests and numeric targets cannot override failed silhouette. No H1 approval is implied until parent visual acceptance; no T3, glove, or fight-scene integration before H1.
