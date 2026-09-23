# 2026-09-23 model-engine research intake

Status: **retrievable research, not an approved engine specification or measured benchmark**. This intake is for the shared 2.5D/3D engine plan; it does not change fighter-art, rendered-motion, or operator approval gates.

## Landed material and custody

- [3D rigging, WebGL, and impact blueprint](../motion/RIGGING_3D_MODELING_WEBGL_IMPACT_OPTIMIZATION_RESEARCH_BLUEPRINT.md): six local finding files in `docs/research/runs/2d-3d-rigging-webgl-optimizations-2026-09/`.
- [AI modeling and 2.5D blueprint](../tech/AI_LLM_3D_MODELING_AUTOMATION_RESEARCH_BLUEPRINT.md): four local finding files in `docs/research/runs/ai-llm-3d-modeling-automation-2026-09/`.
- Both blueprints are in the local docs index. Targeted format audits found 100% lead/term coverage and no generic headings (30 and 23 headings, respectively). The repository-wide local provenance audit found 432 anchors, 418 valid, and 14 failures, all reported in the separate sovereign-compute research set; this is **not** a clean global provenance verdict. Remote source URLs and the underlying experimental claims were not reverified here.
- The ten raw finding files exist locally but `docs/research/runs/` is gitignored. This intake tracks the two annotated blueprints and queue decision, **not** the raw evidence files. A local index entry does not make the full source chain portable; preserve the raw findings and separately review any decision to add them to Git.

## Creative-direction disposition

| Decision | Research direction | Required local proof before adoption |
| --- | --- | --- |
| **Active** | Source-timed contact, planted feet, hand/head separation, and rendered deformation review in the current generic two-rig exchange and later fighter-character stress poses | Reopened editable rig, dense source-frame contact/sole/floor metrics, rendered phone-size sequence, then operator visual review. Source footage sets timing; no universal hit-stop constant. |
| **Explore** | AI image-to-3D, Tripo/Meshy candidates, and procedural Blender detail as possible faster visual-skin/blockout paths | Same reference, camera, light, pose and deformation tests; inspect topology/editability, likeness, provenance/license, local runtime and human cleanup. No provider result bypasses character-art approval. |
| **Explore** | Depth/segmentation/inpainting for photographs or painted plates in the optional 2.5D lane | Small same-plate A/B with authored layers: edge quality, holes, parallax, cleanup time and seek-safe player output. Keep vector chart depth authored. |
| **Backlog** | QEM/LOD, MikkTSpace parity, compression and Rigify export pruning | Only after a detailed source character exists and actual delivery size/load/render bottlenecks are measured. Compare silhouette, material seams, joint stress, bytes, load/render time and animation parity; keep full editable Blender source. |
| **Backlog** | Three.js/WebGL batching or a separate live skinned runtime | Requires a measured interactive/browser need and seek-safe integration with the existing player on representative devices. Offline Blender rendering and raster-layer playback do not require it. |
| **Backlog** | Continuous collision, XPBD and GJK-style solvers | First show observed contact misses exceed a declared shot budget and simpler authored/IK correction fails; then compare stability, visual read and runtime. Stylized blows are not medical injury simulations. |
| **Reject as stated** | Universal DQS volume guarantee, exact benchmark/economic multipliers, and automatic watertightness or quality claims | These claims cannot be promoted by a link audit; replace them only with derived math, primary-source checks and local measurements. |

## Corrections and quarantined claims

1. The 3D blueprint's claim that blended DQS has a spatial Jacobian with determinant identically `+1`, hence guarantees whole-mesh volume preservation, is **not valid as stated**. Each sampled rigid transform can preserve local volume, but spatially varying blend weights add derivative terms; inspect the actual deformed mesh. The existing [animation inference map](../motion/ANIMATION_PRODUCTION_INFERENCE_MAP.md) already quarantines universal DQS volume claims.
2. The blueprint's exact Rigify reduction, four-weight requirement, GPU bone limits, 10,000 skinned instances, 71.4% fragment-work saving, and guaranteed 60 fps are hypotheses, not measured properties of this engine. The existing inference map also notes that glTF is not universally limited to four influences.
3. The AI blueprint's sub-second asset/2.5D throughput, 24/28/22 ms component timings, `>63,000x`/`8,000x` speedups, $0.0004 per shot, and 77.1% savings must not become cost, staffing, or acceptance assumptions. They mix model inference, hardware, preparation, correction, and artist-review costs without a benchmark on our actual assets.
4. Assertions that all generated meshes are unusable triangle soup, that LLM-authored `bpy` is inherently watertight B-Rep, or that human editing is mathematically impossible from prompts are overgeneralizations. Judge each candidate through the existing mesh audit, rig stress and editable-asset review.

The immediate engine priority remains hardening and reviewing the source-timed two-rig exchange, followed by a genuinely detailed fighter source asset and deformation/contact stress proof. The new research can inform bounded experiments; it does not waive the current PRP's acceptance sequence.

The durable queue entries are [BACKLOG.md §Model-engine research routing](../../content-video-engine/BACKLOG.md#model-engine-research-routing--2026-09-23): ME-EXP-01/02 and ME-BL-01/02/03. The intake table above is the rationale, not a substitute queue.
