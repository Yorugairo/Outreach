# MM Sharaf source-pose retarget: five-still feasibility gate

Status: Sol xhigh reframe after three failed full-rig affine replacement gates and one failed flat source-mask fallback. One targeted Luna retry. This is a review-only 3D proof, not an approved short or full animation.

## Pinned inputs and failure diagnosis

- Read `WORK-ORDER-SHARAF-RIG-OVER-FOOTAGE.md` and the failed review `TASK-LEDGER.md`, `REVIEW-RECEIPT.md`, contact sheets and manifests in the `mm-sharaf-rig-overlay` worktree. Preserve them. Prepared short SHA-256: `d16bc20d1f953ad149b6dd30c545a0146b7b04f0df5ada9a8cd7f2f1ebba8daf`; source rig SHA-256: `942ba684be00e87988330e6709c14a46fd54c34f64714c2253727b863a3d772f`; painted rig proof SHA-256: `b86a1282fc1fdb455d4bb4613cf4a9c8b5f32ba972ca7c6a6bd6bd75a66fda7d`.
- Root cause: the broadcast Sharaf is mostly back-to-camera at source f024, while the painted 3D rig renders in side profile. A global head/hip affine cannot correct yaw, limb pose or contact. The prior final fit left 42.9–60.2% of the source attacker silhouette exposed; glove/MCP residual reached 70.5 px by f026. The palette-mask fallback removed the duplicate actor but lost recognizable face/tattoo/glove detail. Do not repeat either method.

## Bounded implementation

1. In a separate registered worktree, duplicate the painted rig; keep all pinned sources unchanged. Use source frames f006, f010, f024, f025 and f026 only. Annotate at **720x1280 source resolution**: source attacker head, shoulders, elbows, both wrists/glove centers, pelvis/hips, knees, visible ankles/feet, silhouette, and opponent contact/holdout. Record confidence and occluded landmarks. Source f006 is the pre-strike freeze. Keep the 30 fps source clock; no early head reaction.
2. Solve one broadcast camera from cage/canvas perspective, then solve per-frame rig root yaw/pelvis and limb FK/IK against those source landmarks. At f024–f026 the rig must turn toward the source back view. Do not use independent 2D scale/translation as a substitute for yaw/pose. Preserve body proportions, guard, rigid gloved fist–wrist–forearm line and actual f10/f24 contact. Record requested versus projected joint positions, residuals, camera/yaw and source frame mapping. Feet cropped by the prepared video must be evaluated separately in full-alpha rig views, not claimed planted from the composite.
3. Render attacker-only RGBA, ID and depth at each keyed frame. Bind a recognizable Sharaf appearance (bald head, beard when visible, tattoos, white shorts, snug black four-ounce-style glove) to the moving mesh. The existing side-view paint projection does not cover the newly exposed back: source f006/f024 view-keyed image projection may provide temporary review skin/shorts detail, with unsupported hidden surfaces identified. Do not display a naked generic rig, source-photo rectangle, gray/incomplete glove, or flat mask-palette look.
4. Build precise source-attacker and opponent-arm holdouts for these five stills. Composite the rendered rig over the pinned short without altering the title, scorebar, referee, cage, canvas, opponent or f025 head snap. Only patch narrow source-attacker fringes after pose/coverage is solved; no broad speculative inpaint. No effect variants or 105-frame export at this gate.

## Gate and stop condition

- Submit matched 360x640 and 720x1280 source/candidate overlays, rig-only alpha, source/rig silhouette masks, opponent holdout, contact crops and a deterministic landmark/transform/asset/hash receipt. Parent reviews actual frames, not just metrics.
- Candidate targets: ≥95% coverage of the visible source-attacker silhouette, source/rig silhouette IoU ≥0.85 at phone size; projected head/hip/shoulder error ≤6 px and f024–f025 glove/contact error ≤5 px at 360x640. Report per-frame uncovered fraction, IoU, centroid/p95 contour error, joint residuals and any occlusion ambiguity. Targets do not override visible double Sharaf, contact miss, poor likeness, wrist collapse, gray glove or lost real head snap.
- If any keyed still cannot pass after this bounded source-pose retarget, stop the Luna retry and preserve negative evidence. No 105-frame render, treatments, production asset/approval, commit of media, or push. A separate source-driven high-fidelity rotoscope remains a possible editorial route, but is not a 3D rig proof and is outside this order.

## Ownership

Worker owns only a new opt-in retarget helper/recipe if needed, source-pose annotations, derived review scene, ignored proof output, ledger and worktree-register row. Parent owns art verdict, integration and protected actions. Do not edit the native player, episode, existing source rigs, earlier review attempts or other lanes' files. Other agents may be working in the repo; preserve their changes.
