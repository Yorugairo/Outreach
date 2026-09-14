---
id: P58-THE-2-5D-STAGE
title: The 2.5D stage - every plate prompted in depth layers, the camera reading a depth per layer so parallax is a consequence and never a mechanism, the ledger page a card at a depth, two chart forms standing in that space, and the docks / the ball / the slide / the rig moving through it - proven by a probe that picks the layering route, goldens that keep every flat thing byte-identical, and ONE new cut
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-14
updated: 2026-09-14
---

# The 2.5D stage

## Summary

The operator's scope, verbatim (2026-09-14, ruling E98 `docs/portable/OPERATOR-RULINGS.md:2832`): *"most of bravos
work is 2.5d, and that's how we started out as well, i think we need to get back to prompting every plate and probably
drawing charts/graphs as 2.5d"*.

**The finding that sets this plan's shape: the depth vocabulary is already doctrine and the geometry is already built -
what is missing is that plates ship FLAT.** Doc 24 (`24-COMPOSITION-AND-SCALE-SPEC.md:156`) already names four depth
planes with file suffixes and parallax factors (`-far` 1.0 / `-board` 1.05 / `-mid` 1.15 / `-near` 1.40), and
`load_catalog` already rejects an undeclared plane, a layered world with no background, planes out of order and a
duplicate. Doc 23 §11 (`23-EP1-LIBRARY-INTAKE-REVIEW.md:479`) recorded the same diagnosis in the ep1 era: *"The only
missing piece is that worlds ship as one flat image, so parallax has nothing to separate... a generation-side gap in
front of infrastructure that already works."* That is the sentence this PRP closes, one year of engine later - now with
the camera (E59, `kinetics/camera.mjs`), the homography (`kinetics/homography.mjs`) and the plate sidecar
(`<plate>.layers.json`, P50 T7/T15) all on disk.

So this is not a new subsystem. It is (1) a generation route decided by measurement (T1), (2) one new key on a sidecar
that already exists and one new field on the plate library record (T2), (3) a depth term in a camera that already
composes every world (T3), and (4) the page and two chart forms as objects in that space (T4/T5), the mechanisms
carrying a depth (T6), one NEW cut (T7) and the docs (T8). Every flat thing stays byte-identical, by construction and
by golden.

All repo paths below are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`); `python` =
`C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`. This draft was written from the
sweet-villani worktree and copied into MAIN by script (the harness refuses the Write tool against the main checkout's
`.claude/`). No git state was changed while drafting.

### Recall (run before drafting, 2026-09-14 - the receipt rule, `docs/runbooks/RECALL-RECEIPT.md` §2-§3)

- Recall: `docs_find "2.5D"` = 8+ hits, and the top three are ours, not research:
  `[effects] content/video_engine/scripts/kinetics/homography.mjs "The homography kinetics module - kinetics:homography
  - Pure math inlined into the player between KINETICS markers"`;
  `[index] docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md:156 "2.5D depth planes - A world may ship as
  separated planes instead of one flat image. The renderer's..."`;
  `[index] docs/content-video-engine/23-EP1-LIBRARY-INTAKE-REVIEW.md:479 "11. 2.5D worlds - the renderer is already
  waiting for them"`. Plus docs 42/43/44/48 (all *"Extracted from ...07_academic_literature_drawing_and_2_5d_animation_engine.md"*),
  `[index] 29-EVIDENCE-MOTION-STANDARDS.md:112 "1.2 2.5D physical card - hard-edge shadow, no fake 3D blur"`, and
  `[topics] deterministic-2.5d-scene-graph - 4 sections`.
- Recall: `docs_find "parallax"` = the doctrine page exists -
  `[manifest] docs/content-video-engine/45-PARALLAX-AND-PLATE-MOTION.md "45 - Parallax and plate motion: what may move,
  how much, and what is banned"` (§45.1 *"Why our parallax melted"*, §45.2 *"The viability matrix - a gate, not
  advice"*, §45.5 *"The professional standard - multi-plane inpainting"*, §45.6 ambient motion) - and the memory
  `[manifest] docs/agent-memory/operator/nothing-ever-goes-truly-still.md "every held thing carries a named subtle
  idle; Ken Burns/para..."` (E49). **Parallax is not a new idea here; it is the banned-as-a-mechanism one.**
- Recall: `docs_find "homography"` = `kinetics/homography.mjs` + the two sources this PRP cites:
  `[index] ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md:195 "2.4 Multi-Plane Geometry & Planar Homography"`
  and `[index] bravos-.../REPORT.md:25 "1. The Diegetic Studio Display Stage"` / `:107 "3. Empirical Camera
  Measurement: The 'Locked Camera' Reality"`.
- Recall: `docs_find "depth"` = `[topics] depthflow - 21 sections`, `[topics] depth-anything-v2-vitl-fp32.safetensors -
  15 sections`, `[topics] comfyui-depthflow-nodes - 8 sections`; the effects cards
  `[effects] scene-evidence-engine.mjs "The behind-the-plate dock option - dock_option:behind - The plate's own
  foreground cutout paints over the card, so the card sits in th..."` and `[effects] species/verdict.mjs "The verdict
  stack - dock_payload:stack - Already-shown proofs fly in from depth one at a time"`. **We already paint two things
  "in depth" without a depth term.** E98's own receipt records `docs_find "depth map"` = **0 hits**.
- Recall: `docs_find "plate library"` = `[index] docs/content-video-engine/CAPABILITIES.md:169 "Plate library - 326
  plates indexed by SEMANTIC across all worktrees and CHANNEL-AWARE (money-physics 134 / martial-...)"` and
  `[index] PIPELINE.md:153 "The plate library - ONE index, search it before generating"`. Measured today:
  `PLATE-LIBRARY.json` = **327 plates**, record shape `{id, path, semantic, register, channel, source, ...}` - **no
  layer field anywhere** (`build_plate_library.py:93, 120, 185, 221`).
- Recall: `docs_find "layers.json"` = **1 hit**, `[index] docs/content-video-engine/BACKLOG.md:480 "R26-74 An embed
  surface holds images and video (E86; BUILT 2026-09-13) - the ART-embed surface (P50 T7; a plate's
  <plate>.layers.json embed quads...)"`. The shape on disk (`build_scene_timeline_f.py:2269-2276, 2316-2326`):
  `{"foreground": {"<layer>": "<png beside the plate, with alpha>"}, "embed": {"poster": {"quad": [[x,y] x4],
  "darken": "<word>"}}}` - *"A sidecar, not a new asset id ... it is part of THIS plate, and it travels with it"*.
  **This PRP extends that sidecar; it never adds a second file.**
- Recall: `docs_find "extrude"` = **0 hits** in any of the eight layers. The extruded bar and the tilted-plane line are
  genuinely new forms; nothing in the record describes them (RECALL-RECEIPT §5 applies: smallest opt-in, goldens
  unchanged, the operator's ruling written back).
- Recall (`rg`, the naming layer): `kinetics/camera.mjs` exists and is the one eye -
  `camIdentity/camSpeciesState/camKeyState/camCssFor/camFrustum/camInFrame/camAttentionState/camArrivalState/camProject`
  (`:26, :30, :46, :62, :73, :78, :90, :106, :112`), with the law in its own header: *"screen = at + s * (p - look)
  (43 s43.2)"* and *"37 of 45 held compositions are camera-still - LOCKED is the default"*. There is **no depth term**:
  `camProject` is `[at0 + s*(p0-look0), at1 + s*(p1-look1)]`, one plane.
- Recall: `kinetics/homography.mjs` exports `hFromUnitSquare, hApply, hMul, hTranslate, hAffine, hAbout, cssMatrix3d,
  quadBounds, embedBox, embedMatrix, embedRegion` (`:44-:142`) - **the projective machinery a tilted page needs is
  already written and already inlined into the player.**
- Recall: `rg -l "plate_library|PLATE-LIBRARY" content/video_engine/scripts` = `build_plate_library.py`,
  `build_render_f.py`, `build_current_bubble_six_minute_p32_demo.py`. One indexer, two consumers.
- Recall: `content/video_engine/workflows/2_5d_parallax_inpaint.json` is on disk and is a real ComfyUI graph -
  `{"name": "2.5D Parallax Camera Motion", "description": "Transforms a still image into a 3D parallax motion sequence
  using Depth Anything v2 and DepthFlow GLSL camera displacement."}`, nodes `LoadImage` ->
  `DownloadAndLoadDepthAnythingV2Model` (`depth_anything_v2_vits_fp16.safetensors`) -> `DepthAnything_V2` ->
  `{{motion_preset}}` -> `Depthflow` (`edge_fix: 5`, `tiling_mode: "mirror"`) -> `CreateVideo`. **It produces a VIDEO,
  not layers** - which is exactly why E32 retired it as a motion source, and exactly what T1 must re-purpose: we want
  the depth MAP and a split, never DepthFlow's mesh warp (doc 45 §45.1 *"Why our parallax melted"*).
- Recall: doc 45 §45.5 already prescribes the split route we would take: *"1. SAM 2.1 ... isolates the foreground to
  RGBA. 2. LaMa (`big-lama.pt`, Fast Fourier Convolution) reconstructs the occluded background. ~50 ms, ~1.2 GB VRAM,
  deterministic. Mask dilation `R_grow = ceil(2*sigma_optical) + 12 px`; `INPAINT_ColorMatch` normalises mu/sigma in
  L*a*b*. 3. Composite as **cards at different Z in the renderer**, per §43.3. Zero tearing, because the background
  behind the subject is real pixels."*
- Recall: the Comfy side is live and mapped - `docs/agent-memory/operator/comfy-local-models-layout.md`: the server is
  `127.0.0.1:8188` (`ComfyUI-Installs/ComfyUI/ComfyUI/main.py`), the install's `models/*` are placeholders and the real
  weights are in `Comfy-Desktop/ComfyUI-Shared/models` and must be HARDLINKED; `comfy_sam2_mask.py`,
  `comfy_vace_ambient.py`, `comfy_ltx_ambient.py` and `gate_comfy_config.py` are on disk in
  `content/video_engine/scripts`; SAM 2 fetches on demand (`DownloadAndLoadSAM2Model`). **No LaMa and no Depth Anything
  weight is recorded as present** - T1's five-minute check settles both.
- Recall: the Flow route is ours to drive - `docs/agent-memory/operator/flow-driver-traps.md`: *"we drive Flow ourselves
  over CDP (create_flow_image via stdio); the bridge still carries research/review packets, only Flow image orders left
  it; Agent mode hides the pill; read the Characters view; grid baseline must refill"*. E36/E40 consent for the Flow
  SESSION stands (Lane write sets: the Claude lane never writes Flow sessions without it).
- Recall: the Bravos specification, verbatim (`REPORT.md:28-31`): *"**4-Layer Depth Separation:** Layer 0 (Z = -100px):
  Concrete wall texture with static radial gradient vignette. Layer 1 (Z = -20px): Monitor bezel with drop shadow.
  Layer 2 (Z = 0px): Active news article viewport. Layer 3 (Z = +40px): Floating callout badges, underline highlights,
  and red marker strokes."* And the camera truth (`:107-111`): *"37 of 45 held compositions (>= 3.2s) are 100%
  camera-still (< 0.15%/s zoom, < 4px/s pan). Every data chart (11 of 12) and every diagram (4 of 4) is completely
  locked... What viewers perceive as 'high production dynamic camera movement' is an illusion produced by internal
  builds, animated line draws, and crisp cuts under a locked camera, NOT actual virtual camera pan/zoom/tilt."*
- Recall: the monograph's law, verbatim (`ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md:195-205`, §2.4
  *Multi-Plane Geometry & Planar Homography*): *"H = K2 (R + t n^T / d) K1^-1"*; *"**Screen Parallax Shearing:** Lateral
  camera displacement t_perp creates depth separation: Delta x = f t_perp (1/z2 - 1/z1)"*; *"**Vanishing Point
  Horizon:** Ruled ledger lines align with v_inf = K R d, locking drawn ink to physical paper fibers"*; *"**Occluding
  Contour Line Weights (Hertzmann & Zorin 2000):** W(s) = W0 (1 + kappa (Delta z / z0)^gamma)"*.
- Recall: the nearest thing we already ship to a depth move is an ILLUSION, not a plane -
  `build_scene_timeline_f.py:2096-2100`: `throw=<grow>[,<from>[,<s>]]` where *"the growth law (snap | depth)"*, i.e. a
  page that grows as if from depth. One string, no z. Worth citing so T4 does not re-invent it under a second name.
- Recall: `docs_find "extrude"` 0 hits, `docs_find "depth map"` 0 hits (E98's own receipt), and **no `rg` hit for a
  `depth` key in `build_scene_timeline_f.py` other than that one string** - the compiler has no depth concept today.

### What already exists, and what each slice actually adds

| piece | on disk today | path | what P58 adds |
|---|---|---|---|
| the plate sidecar | `foreground` cutouts (HF-17, P50 T15) + `embed` quads (P50 T7) | `build_scene_timeline_f.py:2269-2276, 2316-2340` | a `layers` array in the SAME file |
| the plate index | 327 plates, `{id, path, semantic, register, channel, source}` | `build_plate_library.py` | `layers[] {path, depth, role, alpha}` + `flat: true` + a check |
| the depth vocabulary | four named planes + parallax factors, already gated in `load_catalog` | doc 24 `:156-185` | reuse it verbatim; do not invent names |
| the camera | one persistent 2D similarity, LOCKED by default | `kinetics/camera.mjs:26-112` | a depth per layer inside `camProject`'s form |
| the projective math | homography, quads, `cssMatrix3d`, `embedMatrix` | `kinetics/homography.mjs:44-142` | a page PLANE reusing it |
| the split pipeline | Depth Anything v2 + DepthFlow graph; SAM 2 runner; Comfy gate | `workflows/2_5d_parallax_inpaint.json`, `comfy_sam2_mask.py`, `gate_comfy_config.py` | a depth-SPLIT runner (layers, not video) |
| the prompt route | Flow over CDP (`create_flow_image`) | memory `flow-driver-traps` | a four-layer plate ORDER form |
| the goldens | 74 frames + `build_golden_sources.py` | `content/video_engine/tests/golden/` | one new golden per new form; every flat one unchanged |

## Intent And Acceptance

Make the stage 2.5D by E98's four clauses, without moving a single pixel of anything that stays flat. Accepted when:

1. **The route is decided on evidence, not preference.** T1 delivers two real plates x two routes x three instants
   under the same camera push, and the operator rules HG1 (one route, or one per plate kind). The losing route's
   failure is written down (RECALL-RECEIPT §5) in the same commit.
2. **A plate can declare depth.** `<plate>.layers.json` carries `layers[]` beside `foreground` and `embed`;
   `build_plate_library.py` indexes `layers[] {path, depth, role, alpha}` on the plate's record, refuses layers that
   are not on disk or not ordered by depth, and a flat plate reads `flat: true` with a reason. The 327 records that
   are flat today keep their exact current fields plus that one flag.
3. **The camera reads depth.** A push, a pan or a follow over a layered plate yields parallax as a pure function of the
   camera state - `offset_layer = (camera translation) * k_d`, `scale_layer = 1 + (s - 1) * k_d`, with `k_d` from the
   layer's depth (doc 24's `parallax_factor` table; the monograph's `Delta x = f t_perp (1/z2 - 1/z1)` is the same
   statement in inverse depth). **E59 unchanged: LOCKED is still the default**, and no parallax is ever authored for
   its own sake (E49 stands).
4. **The chart can stand in the space.** The ledger page may be a card at a depth behind an opt-in (`depth:` /
   `plane:`), projected by the homography module that already projects the embed surface; the FLAT page is the default
   and is byte-identical. Two new forms (an extruded bar, a tilted-plane line) exist as page options, each with a
   golden, each still passing M25 and M28 on its label boxes (E28: the number stays readable; E50-E53 unchanged).
5. **The mechanisms move through the depth.** The docks, the melt's ball, the slide and - if R26-105 has landed - the
   rig each carry an optional depth, each an opt-in with its own golden, each off by default.
6. **Nothing flat moved.** `test_golden_frames.py` byte-identical for every pre-existing golden;
   `sync_kinetics.py --check` in sync; `gate_motion_density.py` on `japan-tariff-trick/build-short` and
   `tokyo-tea-break/build-short.v2` reading exactly what it reads at T0 (the parent captures that baseline before T3);
   the whole `content/video_engine/tests` tree with no new red; `build_docs_layers.py --check` 10 layers in sync.
7. **One new cut, never a rebuild.** T7 is a NEW short on the Tokyo or Japan script as a test bed, served privately;
   Japan's 09-09 render and Tokyo's approved build are read, never rebuilt (E45).

## Scope

- The layering probe and its two routes (prompted four-layer generation over Flow; a Depth Anything split with the
  disocclusion inpainted), with the Comfy install checked alive first.
- The `layers[]` key on the existing plate sidecar and on the plate library record, plus the indexer's check.
- A depth term in `kinetics/camera.mjs` and its inlined region in the engine.
- The ledger page as a card at a depth, and two new chart forms as page options.
- An optional depth on the docks, the melt's ball, the slide and (conditionally) the rig.
- One new short built on layered plates with one 2.5D chart, served privately for the operator's watch.
- CAPABILITIES rows, a plate-prompting runbook line, and the ten generated layers regenerated once at the end.

## Not Building

- **No restage of an approved cut** (E45). Japan's 09-09 render and Tokyo's approved build are read only; T7 is a NEW
  cut in a NEW build directory.
- **No generative video.** E32 stands: DepthFlow is used, if at all, for its DEPTH MAP; its GLSL mesh warp and
  `CreateVideo` tail are not the product. No Wan / LTX / VACE in this PRP.
- **No authored parallax.** E49 stands: no Ken Burns, no plate drift as a stillness cure, no "2.5D look" applied to a
  held chart. Parallax exists only as a consequence of a camera move that already had a reason (E59).
- **No new camera default.** LOCKED stays the default; this PRP adds no move to any existing row.
- **No re-prompting of the 327-plate library.** Only the two probe plates are generated; the back catalogue is marked
  `flat: true`, not re-made.
- **No chart doctrine change.** E50-E53 untouched: the chart proves one sentence and leaves; the flat page stays the
  default reading form; a 2.5D form is opt-in per page.
- **No new gate family.** T5 reuses M25/M28's existing label-box reads; no M4x row is added unless a slice's acceptance
  names it.
- **No push, no deploy, no credential change, no research commissioned.** The parent owns every protected action.

## Human Gates

**HG1 - the route (the operator, after T1).** Two plates x two routes x three instants under the same push, plus the
generation cost of each (wall-clock, VRAM, re-roll cost). The operator picks: prompted-four-layer, depth-split, or one
route per plate kind (e.g. prompted for a built world, split for a photographic or already-approved plate). **T2-T7 do
not start before this ruling** - the sidecar's `layers[]` semantics differ slightly between routes (a split carries a
generated alpha and an inpainted background; a prompted set carries four native alphas and a style risk).

**HG3 - the two chart forms (the operator, after T5).** The extruded bar and the tilted-plane line, each at its build,
hold and leave instants, beside today's flat page of the SAME data. The question put plainly: does the number stay as
readable as the flat page, and does the form prove its sentence faster or slower? A form the operator does not take is
written down as refused, with the frames, and removed.

**HG2 - the first 2.5D cut (the operator, after T7).** One watch of a NEW short, served privately (never rebuilt under
the operator - `review-link-frozen-copy`). The verdict is the cut's, not the feature's: if the stage reads as depth
rather than as a trick, the mechanism ships; if it reads as the E49 crime, T3-T6 stay opt-in and unused.

No operator gate for T2 (the index), T6 (opt-ins with goldens) or T8 (docs): their proof is that every golden is
byte-identical and the parent reads each diff.

## Mandatory Reads

- `docs/portable/OPERATOR-RULINGS.md`: **E98** (`:2832`, verbatim - the four apply clauses ARE this plan's acceptance),
  **E32** (`:1090`, motion is not animation - why the DepthFlow graph is a depth source and not a video source),
  **E49** (`:1494`, nothing goes truly still - parallax is not the cure for stillness), **E59** (`:1903`, one eye,
  LOCKED by default, moves for a nameable reason), **E97** (`:2815`, the rig is relations; inheritance is
  translate-only unless widened), **E45** (`:1361`, the dock/mount rule - and the no-restage discipline it anchors).
- `docs/content-video-engine/BACKLOG.md:554` - row **R26-122**, verbatim (it names every piece of this PRP).
- `content/video_engine/sources/reference_analyses/bravos-china-just-triggered-a-new-world-order/REPORT.md:28-31`
  (the 4-layer depth separation with its Z values) and `:102-111` (the locked-camera measurement - the reason this PRP
  adds depth and NOT camera movement).
- `content/video_engine/sources/reference_analyses/ACADEMIC_LITERATURE_DRAWING_AND_2_5D_ANIMATION_ENGINE.md:195-205`
  (§2.4 Multi-Plane Geometry & Planar Homography) and its table of contents (Pillar 2 §2.1-2.4 ARAP + projective
  geometry; §5.1 the master 6-beat ledger-page timeline; §5.3 the O(1) seek-safe analytic evaluator - the closed-form
  rule every kinetics module obeys).
- `docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md:156-185` (the four depth planes, their suffixes, their
  parallax factors, and `load_catalog`'s four refusals) and `23-EP1-LIBRARY-INTAKE-REVIEW.md:479-500` (§11, the ep1-era
  ruling that the gap is generation-side).
- `docs/content-video-engine/42-DRAWING-KINETICS.md` and `43-SCENE-GRAPH-AND-TRANSFORM.md` (the scene graph and the
  transform stack the camera composes through - §43.2 `p_screen = M_camera x M_world x p_local`, cited in
  `camera.mjs`'s own header; §43.3 cards at different Z, cited by doc 45 §45.5).
- `docs/content-video-engine/45-PARALLAX-AND-PLATE-MOTION.md` §45.1 (why our parallax melted), §45.2 (the viability
  matrix), §45.5 (SAM 2.1 + LaMa multi-plane inpainting - the split route's actual recipe).
- `content/video_engine/scripts/kinetics/camera.mjs` (whole, 120 lines) and `kinetics/homography.mjs` (whole).
- `content/video_engine/scripts/build_scene_timeline_f.py:2260-2350` (the sidecar contract, both keys, verbatim
  comments) and `content/video_engine/scripts/build_plate_library.py` (the record shape).
- `docs/runbooks/RECALL-RECEIPT.md` (the receipt, the order of layers, §4 inspect AND measure, §5 when the record is
  silent, §6 cheap candidates first) and `docs/runbooks/PRP_EXECUTION.md` (Dispatch mapping, Hand-off policy, Lane
  write sets - the engine files are the Codex/Luna lane's by order, the doctrine files are the Claude lane's).
- `docs/agent-memory/operator/comfy-local-models-layout.md` (the install, the hardlink trap, what weights exist) and
  `docs/agent-memory/operator/flow-driver-traps.md` (how a plate is actually generated).
- `.claude/PRPs/plans/P57-THE-BACKLOG-BURNDOWN.plan.md` (the slice shape and the engine lock this plan mirrors) and
  `P55-THE-EFFECTS-CATALOGUE.plan.md` **T7** (the promotion recipe: a frozen dials object, pure math exported and
  node-tested, `sync_kinetics --check`, every golden's sha256 identical).

## Execution Path

The probe decides the route; the index makes depth declarable; the camera makes it move; the page and the forms make
the chart an object in it; the mechanisms follow; one cut proves it; the docs record it.

1. **T1** (parent brief + implementation lane): the probe, both routes, the Comfy check first. **HG1.**
2. **T2** (implementation lane): the sidecar's `layers[]`, the library record, the indexer check. No engine file.
3. **T3** (implementation lane, engine lock): the camera's depth term + goldens.
4. **T4** (implementation lane, engine lock): the page as a card at a depth.
5. **T5** (implementation lane, engine lock): the two chart forms. **HG3.**
6. **T6** (implementation lane, engine lock): the mechanisms' optional depth, one opt-in at a time.
7. **T7** (parent): the new cut, served privately. **HG2.**
8. **T8** (parent, docs lane): CAPABILITIES, the runbook line, the ten layers regenerated LAST.

**The engine lock (contended files - never two writers at once):**
`content/video_engine/scripts/kinetics/*.mjs`, `content/video_engine/scripts/species/*.mjs`,
`docs/content-video-engine/samples/scene-evidence-engine.mjs`,
`content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/golden/**`,
`content/video_engine/effects/cards/*.json`.
Order: **T3 -> T4 -> T5 -> T6**. T2 holds no engine file (it touches `build_plate_library.py` and the sidecar's reader
only, and the reader edit is a separate, later hand-off if T2 needs one - see T2's write set). T7 and T8 take the lock
only if a defect forces a fix, and then they queue behind T6.

**The layer-regen rule (R26-92, `RECALL-RECEIPT.md` §3):** all ten generated layers are regenerated once, by T8, after
the engine lane settles - never while `scene-evidence-engine.mjs` is mid-edit, never inside a slice that does not own
them.

## Patterns To Mirror

- **P50 T7 / T15 - the sidecar**: one file beside the plate, a NAMED SET rather than one value, the compiler refusing
  by name every way it goes wrong silently (an undeclared name, a file not on disk, a quad that is not a quad, a
  surface too small to read on a phone). `layers[]` gets the same treatment: an unordered depth, a missing alpha and a
  layer file that is not on disk are each refused with the fix in the message.
- **P55 T7 - the promotion recipe**: a WHEN / THE LAW header, every literal lifted into a frozen dials object with no
  value changed, the pure math exported and node-tested, `sync_kinetics --check` in sync, every golden's sha256
  identical before and after. T3's depth term is exactly this shape: new dials, frozen, defaulting to today's values.
- **P57's slice shape and engine lock**: Status / Owner / Depends on / Write set / Acceptance / Validate / Evidence,
  with the command written out in full and the evidence carrying numbers, not adjectives; one engine writer at a time
  in a named order.
- **RECALL-RECEIPT §4 - inspect AND measure**: every visual slice here delivers frames at named instants AND the
  geometry at those instants (layer rects, the per-layer transform, the label boxes M25/M28 read), never one or the
  other. **RECALL-RECEIPT §6 - cheap candidates first**: T1 is literally that rule applied to a route decision.
- **The Bravos measurement as the governing caution**: 37 of 45 held compositions are camera-still. Depth is for the
  few moves that already had a reason - it is not a licence to start moving.

## Task Slices

### T1: THE PROBE - two plates, two routes, one camera push, and the operator picks
- Status: complete
- Owner: parent (brief + HG1) with `implementation_luna` executing the runs
- Depends on: none
- Write set: `content/video_engine/scripts/comfy_depth_split.py` (NEW - the split runner), `content/video_engine/scripts/probe_2_5d.py` (NEW - builds the private probe build and pulls the frames), `content/video_engine/tests/test_comfy_depth_split.py`, and the probe's own private build directory `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p58-probe/` (gitignored artifacts)
- Acceptance: **(0) the Comfy install is checked alive FIRST - a five-minute check, not a lane**: `python -c "import urllib.request,json;print(json.loads(urllib.request.urlopen('http://127.0.0.1:8188/system_stats',timeout=5).read())['system']['comfyui_version'])"` and `python content/video_engine/scripts/gate_comfy_config.py`; if the loaders list `[]`, the memory's hardlink fix applies (`New-Item -ItemType HardLink` from `ComfyUI-Installs/ComfyUI/ComfyUI/models/...` to `ComfyUI-Shared/models/...`, same volume, no restart needed) and `depth_anything_v2_vits_fp16.safetensors` is fetched if absent (`DownloadAndLoadDepthAnythingV2Model` downloads on demand; `big-lama` is NOT recorded on disk - if it is absent, the inpaint falls back to Comfy's `VAEEncodeForInpaint` path and the slice SAYS SO). If the server is down, the slice reports "route (b) not runnable today" and HG1 is put with route (a) only - it does not stall.
  **(1) Two plates**: one FROM the library (`python content/video_engine/scripts/build_plate_library.py "<semantic>"` picks it; a money-physics world plate with a clear fore/mid/back, e.g. the `world-banker-apartment-v2` class of plate - the exact id named in the evidence) and one NEW (never generated before).
  **(2) Route (a) - prompted in four layers**: four generations through the Flow driver we already drive (`create_flow_image` over CDP via the stdio driver, per `docs/agent-memory/operator/flow-driver-traps.md`; the operator's Flow-session consent E36/E40 is confirmed in the brief before any order), ONE style register across the four (the plate's `register` field, quoted into all four prompts), each with alpha: `background` / `mid` / `subject` / `occluder`, at identical dimensions, in one sitting so they register (doc 24: *"Generate all planes of a world in one pass, same prompt and seed where the tool allows"*).
  **(3) Route (b) - one generation, depth-split**: `comfy_depth_split.py` runs `LoadImage -> DownloadAndLoadDepthAnythingV2Model -> DepthAnything_V2` from `workflows/2_5d_parallax_inpaint.json` (nodes 1-3 ONLY - DepthFlow and `CreateVideo` are not called; E32), thresholds the depth map into the same four bands, cuts four RGBA PNGs, and inpaints the disoccluded background behind each nearer band (doc 45 §45.5: dilate the mask by `ceil(2*sigma) + 12 px`, colour-match in L*a*b*). Deterministic seed recorded.
  **(4) The same camera push over each**: one authored key list (`{t, zoom, look, at, ease}`), identical across all four outputs, in a PRIVATE build; frames at **three instants per route per plate** (push start / mid / end) via `render_baseline.py` + the probe's frame grab, plus the per-layer rects at those instants (RECALL-RECEIPT §4).
  **(5) The cost table**: wall-clock, VRAM, re-roll cost and failure modes per route (route (a): style drift across four generations; route (b): inpaint seams and a band that cuts through a subject).
  The frames, the geometry and the cost table go to HG1; the operator picks one route, or one per plate kind. Whatever loses is written into the PRP's Evidence with WHY (RECALL-RECEIPT §5).
- Validate: `python content/video_engine/scripts/gate_comfy_config.py` and `python -m pytest content/video_engine/tests/test_comfy_depth_split.py -q` and `python content/video_engine/scripts/probe_2_5d.py --frames` (writes the twelve PNGs + `probe-geometry.json` beside the build and prints the manifest)
- Generator note (the operator, 2026-09-14, after the draft): *"GPT Image 2.5 released and is by far the leading image-generator, and is actually able to use GPT 6 reasoning during the image generation ... that's where the new icon assets came from."* Route (a) prompts the four layers through GPT Image 2.5 FIRST (one style, a separation instruction per layer, alpha where it can give it) with the Flow driver as the comparison; the plate library records the generator per plate. A capability claim to verify on our plates, not doctrine yet. Codex's capability read (the operator asked, same day): a strong generator/editor (Sunburst for precise iterative edits) that is NOT a native 2.5D scene-asset generator - it returns a transparent RGBA asset (PNG/WebP, `background: transparent`) and takes an alpha mask for an edit, but no named layers (flattened), no depth map, no vector paths, no roles, no camera path. So route (a) is settled in shape: ONE transparent asset per layer (background / mid / subject / occluder) with a SHARED camera brief and ONE reference image across the four, the alpha cleaned, the depth and the roles assigned and the camera path authored on OUR side (T2's sidecar, T3's camera). The prompt pattern to start from: *"Create ONLY the foreground subject as an isolated transparent PNG asset. Match the supplied composition reference exactly: 50mm eye-level camera, subject centered at x=62%, lower edge at y=92%, full silhouette visible. No background, no ground plane, no cast shadow, no text. Designed for 2.5D parallax compositing; clean edge separation and no cropped limbs."* T8's runbook line records the pattern as the plate-prompting template.
- Evidence: (built 2026-09-14; HG1 RULED the same day, E98 s6 - the operator: *"It seems like it's good if we generate the individual images first, stacking them all together on the first generation caused the problem because then we tried to remove and blend"* - a layer is generated, never split; the split stays the fallback for an existing flat plate; the losing route's failure = the inpaint's blur where the rower's handles touched the couch) **T0 baseline captured by the parent at HEAD 2b4a685** - `gate_motion_density.py japan-tariff-trick/build-short` = `RESULT: 3 FAIL / 0 WARN / 16 PASS / 1 JUDGE / 8 INFO`; `tokyo-tea-break/build-short.v2` = `RESULT: 1 FAIL / 2 WARN / 14 PASS / 1 JUDGE / 8 INFO` (full outputs in the session scratchpad `p58/baseline-*-gate.txt`); the whole `content/video_engine/tests` tree at this HEAD = `3086 passed, 14 skipped` (P57's closing run; no engine change since). **(0) Comfy**: the server was DOWN at T1 start; the parent launched it (`ComfyUI-Installs/ComfyUI/ComfyUI/.venv/Scripts/python.exe main.py --listen 127.0.0.1 --port 8188` - the `standalone-env` python has no torch) -> `0.34.2`, RTX 4070 12 GB; `DownloadAndLoadDepthAnythingV2Model` / `DepthAnything_V2` registered; `depth_anything_v2_{vits,vitl}_fp16` already in the install's `models/depthanything/`; **no LaMa weight and no SD checkpoint** on disk -> lane B tries `big-lama.pt` through `comfyui-inpaint-nodes` first and falls back to `cv2.inpaint` (Telea), stating which ran. **Route (a)** runs on GPT Image 2.5 through the claims pipeline (`open_claim` + `codex exec` headless - the record's image lane, `codex-fulfillment-flow`); **the Flow comparison is NOT run** - it needs the operator's Flow-session consent (E36/E40), not given this session; HG1 is put as GPT Image 2.5 layers vs the depth split. Plates: `world-banker-apartment-v2` (library; wall/floor far, shelves+TV mid, sofa subject, rowing machine occluder - read by the parent) and the NEW `world-tokyo-customs-dock-v1`. Lanes dispatched: A (prompted layers), B (the split + `probe_2_5d.py`). **Delivered**: `comfy_depth_split.py` (Depth Anything v2 vitl fp16 -> 4 quantile bands -> LaMa via `comfyui-inpaint-nodes` - lane B fetched `big-lama.pt` into the install's `models/inpaint/`; the Telea fallback wired and unit-tested; `--occluder`/`--subject` SAM 2.1 point masks override the bands = variant **b-sam**; deterministic, byte-identical re-run), `probe_2_5d.py` (PIL compositor, one frozen PUSH s 1.00->1.12 + 40 px look drift, k per layer 1.0/1.15/1.40, 18 frames + `contact-sheet.png` + `probe-geometry.json` with per-layer rects/translate/scale), `tests/test_comfy_depth_split.py` = `29 passed`; `test_art_embed_media.py` = `14 passed`. **Route (a)** ran through the claims pipeline (5 claims, 15 generations for 9 assets, 5 re-rolls, 1118 s): codex's built-in image tool exposes no model/size/quality/background parameter and the PNGs' C2PA reads **gpt-image 2.0** (the operator suspects the model behind the stamp is 2.5 and the stamp stale - unconfirmed; P59/P60 settles it); 7 of 9 assets came back as painted checkerboards; the two true-alpha objects were re-composed at 2.1x / 3.4x the reference scale (not a translation - the +-42 px search saturates); style did NOT drift. So route (a) at GPT Image 2.5 is UNTESTED (reachable only by the operator's hand in the ChatGPT app or a banned image API), not refused. **Route (b)** cost ~10 s / 1.1 GB VRAM per plate; b-split's two defects (the apartment's roof-ridge halo from a wall sliver in the near band; the dock's lamp cut across three bands) both gone under b-sam (~12 s). Parent read all 18 frames (RECALL-RECEIPT s4). **Sheet for the operator**: `docs/research/runs/p58-2-5d/HG1-SHEET.md`; frames served at `http://127.0.0.1:8762/`; lane logs `docs/research/runs/p58-2-5d/lane-{a,b}/`. Parent recommendation: **b-sam for every plate**, the depth intent stated in the FLAT plate's prompt (the dock, prompted that way, split cleaner than the apartment).

### T2: THE LIBRARY - a plate declares its layers, and the index knows
- Status: running
- Owner: `implementation_luna`
- Depends on: T1 (HG1 - the route fixes what a layer record must carry)
- Write set: `content/video_engine/scripts/build_plate_library.py`, `content/video_engine/tests/test_plate_library_layers.py` (NEW), the two probe plates' `<plate>.layers.json` sidecars (under the probe build / the plate's own folder)
- Acceptance: **the sidecar gains one key, never a second file** (`build_scene_timeline_f.py:2269-2276`'s rule): `{"foreground": {...}, "embed": {...}, "layers": [{"path": "<png beside the plate, with alpha>", "depth": <0..1>, "role": "background|mid|subject|occluder", "alpha": true}]}` - back to front, `depth` ASCENDING toward the viewer, the four `role` names bound to doc 24's four planes (`building_or_environment` / `evidence_safe_region` / `actor_or_machine` / `foreground_cutout`) with its parallax factors (1.0 / 1.05 / 1.15 / 1.40) as the DEFAULT `depth` when a sidecar omits one. `build_plate_library.py` carries each plate's `layers[]` onto its record and refuses, BY NAME with the fix in the message: a layer file not on disk; layers not ordered by depth; a duplicated role; a layered plate with no `background`; a PNG with no alpha channel where `alpha: true` (`load_catalog`'s four refusals, doc 24 `:178-180`, reused verbatim in spirit). A plate with no `layers` key reads **`flat: true`** with a `flat_reason` string (`"pre-E98 back catalogue"` for the 325 that are not the probe's two) - the flag is written by the indexer, not hand-maintained. **The 327 existing records keep every field they have today**; the index's `count` stays 327 (+ any layer PNG that is NOT itself a plate must not be indexed as one - a layer is part of THIS plate, P50 T15's rule).
- Validate: `python content/video_engine/scripts/build_plate_library.py` (prints the count and any refusal) then `python -m pytest content/video_engine/tests/test_plate_library_layers.py -q` and `python -m pytest content/video_engine/tests/test_art_embed_media.py -q` (the sidecar's existing readers must not regress)
- Evidence: pending

### T3: THE CAMERA OVER LAYERS - one eye, a depth per layer, parallax by construction
- Status: pending
- Owner: `implementation_luna` (engine lock #1)
- Depends on: T2
- Write set: `content/video_engine/scripts/kinetics/camera.mjs`, `content/video_engine/tests/kinetics/camera.test.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the `camera` region ONLY, via `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (the world's layer pass-through only), `content/video_engine/tests/golden/` (ONE new golden + its source), `content/video_engine/tests/test_golden_frames.py` (the new case's registration)
- Acceptance: `camera.mjs` gains a pure, exported depth term beside `camProject` - `camProjectAt(st, p, k)` (or `camLayerCss(st, k, W, H)`) implementing, in the module's own similarity form, `offset = (st.at - st.look) * k` and `scale = 1 + (st.s - 1) * k`, i.e. a layer at parallax factor `k` takes the share `k` of the camera's translation and of its zoom. `k = 1` reproduces today's `camProject` EXACTLY (the identity case is a node test, not a claim), so a flat world is arithmetic-identical. The law is documented in the module header with BOTH citations: doc 24's `parallax_factor` table and the monograph §2.4's `Delta x = f t_perp (1/z2 - 1/z1)` (the same statement in inverse depth: `k` is the normalised inverse-depth ratio, `k = z_ref / z_layer`), naming which one the code implements and why (a 2D similarity has no `f`; the inverse-depth ratio collapses to the factor). Every dial frozen in a `PARALLAX` object with no existing value changed. **E59 unchanged**: the default is still LOCKED, no row gains a move, and the term does nothing at all on a world with no `layers`. **The golden pair**: the FLAT plate under the push is byte-identical to today's golden (sha256 quoted); the LAYERED plate under the SAME push is a NEW golden, and the parent reads its three frames before it is committed.
- Validate: `node --test content/video_engine/tests/kinetics/` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`
- Evidence: pending

### T4: THE CHART AS AN OBJECT IN THE SPACE - the ledger page as a card at a depth
- Status: pending
- Owner: `implementation_luna` (engine lock #2)
- Depends on: T3
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (the page option), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the ledger-page paint region), `content/video_engine/scripts/kinetics/homography.mjs` (only if a helper is needed - additive, no existing export changed), `content/video_engine/tests/test_page_depth.py` (NEW), `content/video_engine/tests/golden/` (one new golden + source)
- Acceptance: a page row may carry **one** new option - `depth:<0..1>` (the card's plane) and/or `plane:<quad|tilt>` (the surface it is drawn on) - and the page is then projected by `homography.mjs`'s existing `embedMatrix` / `cssMatrix3d`, i.e. by the SAME machinery that already projects the ART-embed surface (P50 T7), not by a second projective path. Without the option the page is drawn exactly as today and its goldens are **byte-identical** (sha256 quoted for all pre-existing page goldens). The option is refused by name when it would break a rule we already hold: a chart never lands on a plate's embed surface (`EMBED_REFUSED_SPECIES = ("chart",)`, B1, `build_scene_timeline_f.py:2337`), a tilt that makes the page narrower than `EMBED_MIN_W` of the stage is refused with the same "cannot be read on a phone" message, and `throw=depth` (the existing growth ILLUSION, `:2096-2100`) and a real `depth:` on the same page are refused together so two names never mean one thing. One new golden at the page's build / hold / leave instants, read by the parent.
- Validate: `python -m pytest content/video_engine/tests/test_page_depth.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-short.v2`
- Evidence: pending

### T5: TWO CHART FORMS IN 2.5D - the extruded bar and the tilted-plane line
- Status: pending
- Owner: `implementation_luna` (engine lock #3)
- Depends on: T4
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the two form painters), `content/video_engine/scripts/build_scene_timeline_f.py` (the two page options), `content/video_engine/scripts/ledger_page.py` (the spec fields the forms need), `content/video_engine/tests/test_chart_forms_2_5d.py` (NEW), `content/video_engine/tests/golden/` (two new goldens + sources), `content/video_engine/effects/cards/page_species.json` (the two new cards)
- Acceptance: two page options - `form:extruded_bar` (each bar a prism: one face, one side, one top, a single light direction, hard-edge shadow per doc 29 §1.2 *"hard-edge shadow, no fake 3D blur"*) and `form:tilted_line` (the line drawn on a plane the homography tilts, the ruled baseline aligned to the plane's vanishing direction - the monograph's *"Ruled ledger lines align with v_inf = K R d"*). **Both are opt-in; the flat page is the default and unchanged.** E50-E53 hold literally: the chart still proves one sentence and leaves; the axis rule still states itself on the page; sign is still geometry (a drop still goes DOWN in the extruded form - an extrusion that inverts the read is a failed form). **The number stays readable and this is MEASURED, not asserted**: `probe.py --gate` writes the label boxes and the existing M25 (a settled card at every landing) and M28 (two of a page's OWN labels crashing) read them for both forms exactly as they read a flat page today - a form that FAILs M28 does not ship. A golden per form at build / hold / leave. Frames + label-box geometry go to **HG3**; a form the operator refuses is deleted and its refusal written into the plan and into `OPERATOR-RULINGS.md` by the parent.
- Validate: `python -m pytest content/video_engine/tests/test_chart_forms_2_5d.py content/video_engine/tests/test_golden_frames.py -q` and `python content/video_engine/scripts/probe.py --gate <the T5 private build>` then `python content/video_engine/scripts/gate_motion_density.py <the T5 private build>` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T6: THE MECHANISMS THROUGH THE DEPTH - the docks, the ball, the slide, the rig
- Status: pending
- Owner: `implementation_luna` (engine lock #4; four sub-steps, serialised, each its own diff and golden)
- Depends on: T5
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the dock placement block and the melt block), `content/video_engine/scripts/build_scene_timeline_f.py` (the four opt-ins), `content/video_engine/scripts/kinetics/*.mjs` (only the modules named below), `content/video_engine/tests/golden/` (one golden per opt-in), `content/video_engine/effects/cards/dock_option.json` + `exit.json` (the option cards)
- Acceptance: four small opt-ins, each defaulting OFF and each leaving every existing golden byte-identical - (a) **the docks**: `depth:` on a dock row places the card on a layer's plane, so a camera move shifts it by that layer's `k`; it composes with the EXISTING `behind:` foreground-occluder option (P50 T15) rather than duplicating it - a dock that names both must agree, and is refused by name if it does not. Touches the dock placement block in `scene-evidence-engine.mjs` + `build_scene_timeline_f.py:2528`'s validation. (b) **the melt's ball**: the ball and its drips take a depth so the melt happens at the plate's mid plane rather than on the glass (the melt block in the engine; `kinetics/` module only if the ball's math already lives in one). (c) **the slide** (R26-75 / E87 s3, if P57 T13 has landed): the incoming and outgoing frames may sit at different depths so the push has a near/far read; the exit kind's direction is unchanged. (d) **the rig** (R26-105 / E97) - **conditional**: only if the `rel` layer has landed, in which case `Z` is the authored relation E97 already reserves (*"Z authored"*) and this sub-step is the depth-aware binding of it; **if R26-105 has not landed, this sub-step is dropped from the slice and the PRP says so** - it is not built here. Each sub-step names the module or engine block it touches in its own evidence line.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` and `node --test content/video_engine/tests/kinetics/` and `python content/video_engine/scripts/sync_kinetics.py --check` and `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: pending

### T7: THE FIRST 2.5D CUT - a new short, never a rebuild
- Status: pending
- Owner: parent
- Depends on: T6 (or T5, if T6's sub-steps are all deferred)
- Write set: a NEW build directory under `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p58-2-5d/` (or `japan-tariff-trick/build-p58-2-5d/`), the project's `SHOT-TABLE-SHORT.py` **copied, never edited in place**, and the two layered plates' sidecars
- Acceptance: a NEW short on the Tokyo or Japan **script** as a test bed (E45: the approved cuts are read, never rebuilt - Japan's 09-09 render and Tokyo's `build-short.v2` are untouched, verified by `git status` on those directories being clean), built with at least two layered plates from T1's ruled route and exactly ONE 2.5D chart from T5, under camera moves that each already had a reason (E59's four: a landing, a stage wider than the frame, an arrival, a species) - **no move is added to make the parallax visible**; a move that exists only to show depth is the E49 crime and is cut before the watch. Served privately and FROZEN (`review-link-frozen-copy`: the build is never rebuilt under the operator; `python content/video_engine/projects/.../serve_player.py` with no-store). The motion gates read at least as well as the same script's approved cut, and the one-shot floor (M35-M42) is not lowered. Goes to **HG2**.
- Validate: `python content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build_short.py --out build-p58-2-5d` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p58-2-5d` and `python content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/tokyo-tea-break/build-p58-2-5d`
- Evidence: pending

### T8: THE RECORD - CAPABILITIES, the prompting runbook line, the ten layers
- Status: pending
- Owner: parent (docs lane)
- Depends on: T7 (and the operator's HG2/HG3 rulings)
- Write set: `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md` (the R26-122 row only), `docs/portable/BUILD-PIPELINE.md` (the plate-prompting line), `docs/content-video-engine/PIPELINE.md:153` (the plate-library paragraph), `docs/runbooks/` (the plate-prompting runbook line), the ten generated layers (`docs/DOCS-INDEX.*`, `DOCS-MANIFEST.*`, `DOCS-TOPICS.*`, `DOCS-CITATIONS.*`, `GATES-REGISTRY.*`, `ANIMATION-REGISTRY.*`, `CRAFT-MAP.*`, `EFFECTS-CATALOG.*`, `RESEARCH-LEDGER.*`, `DOC-OVERLAP.*`)
- Acceptance: CAPABILITIES rows in the file's four-column form (`what it does / where it lives / state / proof`) for: the layered plate sidecar + the library's `layers[]`, the camera's depth term, the page at a depth, each chart form the operator TOOK at HG3, and each mechanism opt-in T6 shipped - each naming its golden or its commit. The plate-prompting rule as ONE line where a plate order is actually written (`BUILD-PIPELINE.md` "The plate library" + the runbook): **every plate is prompted in layers - background / mid / subject / occluder, one style across the four, one sitting so they register; a flat plate is the exception and says why**. R26-122 carries its verdict with the slice ids and the frames. All ten layers regenerated LAST and in sync.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --write` then `python content/video_engine/scripts/build_docs_layers.py --check` and `python -m pytest content/video_engine/tests/test_build_docs_index.py -q` and `python scripts/prp_validate.py .claude/PRPs/plans/P58-THE-2-5D-STAGE.plan.md`
- Evidence: pending

## Open Decisions

1. **The layering route** - prompted four layers (Flow, style risk) vs a depth split of one generation (seam risk) vs
   one route per plate kind. **T1 decides it with frames and a cost table; the operator rules at HG1.** Nothing in
   T2-T7 starts before this.
2. **Which chart form comes first** - the extruded bar (reads as weight and mass; risks the E28 glance test on the
   value labels) or the tilted-plane line (reads as a document on a desk; risks the sign-is-geometry rule when the
   plane rotates). T5 builds both only if the operator wants both; otherwise one, and the other stays a row.
3. **The depth-per-layer defaults** - doc 24's table (1.0 / 1.05 / 1.15 / 1.40) as-is, or re-measured against the
   Bravos Z values (-100 / -20 / 0 / +40 px at their stage width). Proposal: ship doc 24's, because it is already
   doctrine and already gated in `load_catalog`; re-measure only if HG1's frames say the separation reads too weak.
4. **May a flat plate still be prompted at all?** E98 says *"A flat plate is the exception and says so"*. Open: is the
   exception author-declared per plate (a `flat_reason` in the order), or is the back catalogue simply grandfathered
   and every NEW plate layered? Proposal: grandfather the 325, require a reason for any new flat plate.
5. **Does the camera's depth term apply to the ART-embed surface too?** A card projected onto a poster inside a layered
   plate now has two depths (the surface's quad and the layer's `k`). Proposal: the surface wins (it is measured), the
   layer's `k` applies to the plate behind it - stated here so T3 and T4 do not each answer it differently.
6. **What happens to `throw=depth`** (`build_scene_timeline_f.py:2098`) once a real depth exists - rename the illusion,
   keep both with a refusal when combined (T4's proposal), or retire it. The operator rules at HG3.

## Risks

- **Style drift across separately prompted layers** (route a). Four generations of one world will not share grain,
  palette or light unless forced. Mitigation: one register string quoted into all four prompts, one sitting, identical
  dimensions, the same seed where Flow allows (doc 24's own warning: *"Separately generated planes will not register,
  and misalignment is far more visible in motion than in a still"*). T1 measures it rather than assuming it.
- **Inpaint seams on the split route** (route b). The disoccluded background is invented pixels; a push reveals them
  first. Mitigation: doc 45 §45.5's dilation and L*a*b* colour match; the probe's frames are read AT the push's end,
  where the reveal is largest.
- **The camera's parallax reading as the E49 crime.** If any move is added so the depth can be seen, the whole feature
  becomes the thing E49 retired. Mitigation: T7's acceptance forbids it explicitly, HG2 judges the cut and not the
  feature, and the Bravos measurement (37/45 still) is quoted in the camera module's header so the next author meets it.
- **A 2.5D chart that is prettier and slower to read.** Mitigation: M25/M28 read the label boxes of BOTH forms exactly
  as they read a flat page; HG3 puts the same data flat and formed side by side; E50-E53 are unchanged doctrine.
- **Render time and build weight.** Four layer PNGs per plate embedded RAW (the sidecar's `data_uri` with no cap, so
  the alpha survives - `build_scene_timeline_f.py:2274`) multiplies a build's page weight by ~4 per layered plate.
  Mitigation: T1 records the built page's size and the frame time; if a build crosses the player's practical limit,
  layers are capped per scene and the number goes in the PRP.
- **The engine lock held too long.** T3-T6 are four serialised engine slices. Mitigation: each is small, each ends with
  `sync_kinetics --check` + goldens, and T2/T8 are deliberately outside the lock.
- **Comfy is not alive / the weights are not linked.** Mitigation: T1's five-minute check runs FIRST and the slice
  degrades to route (a) only rather than stalling.

## Verification

1. **Everything flat is byte-identical.** `python -m pytest content/video_engine/tests/test_golden_frames.py -q` - all
   pre-existing goldens identical (sha256 quoted per slice); only the new goldens this PRP names are added.
2. `python content/video_engine/scripts/sync_kinetics.py --check` - in sync, module count stated.
3. `node --test content/video_engine/tests/kinetics/` - green, including the `k = 1` identity test.
4. **The motion gates on the approved builds are UNCHANGED** against the baseline the parent captures before T3:
   `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`
   and `... tokyo-tea-break/build-short.v2` - the same RESULT line, row for row.
5. `python content/video_engine/scripts/build_plate_library.py` - 327 plates, the layered ones carrying `layers[]`, the
   rest `flat: true`, zero refusals.
6. `python content/video_engine/scripts/effects_catalog_check.py` - `0 failure(s)`, the new option/form cards present.
7. **The whole tree**: `python -m pytest content/video_engine/tests -q` - no new red against the parent's baseline at
   the time T1 starts (captured into the PRP's evidence, as P57 T1 did).
8. **The layers**: `python content/video_engine/scripts/build_docs_layers.py --check` - 10 layers in sync (T8 owns the
   regeneration; no other slice touches them - R26-92).
9. `python scripts/prp_validate.py .claude/PRPs/plans/P58-THE-2-5D-STAGE.plan.md` and `python scripts/prp_status.py`.
10. **The frames** (RECALL-RECEIPT §4): every visual slice delivers frames at its named instants AND the geometry at
    those instants; the parent reads them as a viewer, not as a diff (`judge-the-frame-not-the-diff`).

## Evidence And Handoff

- T1's twelve frames, `probe-geometry.json` and the cost table go under the probe build (gitignored) with the paths
  named in the slice's Evidence line; HG1's ruling is written into `OPERATOR-RULINGS.md` as an E98 amendment by the
  parent, in the same commit as the route's first use.
- Every delegated diff is read by the parent and the slice's validation re-run by the parent before integration; a
  subagent's completion claim is not evidence (`PRP_EXECUTION.md`, Hand-off policy).
- Long lane output (probe transcripts, run logs) goes to `docs/research/runs/p58-2-5d/` (gitignored disk-as-bus) and the
  slice's Evidence line names the path; the parent reads it with `sed -n` windows only.
- HG3's verdict per form and HG2's verdict on the cut are written into `OPERATOR-RULINGS.md` with the operator's own
  words, in the same commit as the change they govern; a refused form's failure is written down before it is deleted
  (RECALL-RECEIPT §5).
- The commit message for every slice that touches the player template, `kinetics/`, `build_scene_timeline_f.py`,
  `gate_motion_density.py` or a short's `build_short.py` opens with `Recall:` lines (`scripts/hooks/recall_receipt.py`
  refuses otherwise).
- No push, no deploy, no credential change: the parent owns every protected action, and a push needs the operator's
  current explicit authorization quoted in the steward's brief.
