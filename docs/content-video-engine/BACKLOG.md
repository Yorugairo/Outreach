# Backlog — content video engine

Status: current active queue and 2026-09 first-pass cleanup. Last reviewed 2026-09-23.

This is the canonical active board for the video engine. There is no
`Consultant input/SPRINT_BACKLOG.md` in this repository. Historical detail is
preserved in [`BACKLOG-HISTORY-2026-09.md`](BACKLOG-HISTORY-2026-09.md); old
status words there are not current queue state. A commit alone does not close a
visual or operator gate.

**Active work** is grouped by execution context. Every row has a stable ID,
state, owner or trigger, next action, and evidence pointer. Historical R26
rationale and citations remain in the linked history file.

## Active queue — canonical

| ID | Work / lane | Status | Owner / trigger | Next action / acceptance | Evidence |
|---|---|---|---|---|---|
| P69; R26-253, R26-254, R26-255, R26-256, R26-257, R26-258, R26-259, R26-260, R26-261, R26-263, R26-264, R26-265, R26-266, R26-267, R26-268, R26-269, R26-270, R26-271, R26-272, R26-273, R26-274, R26-275, R26-276, R26-277, R26-278, R26-279, R26-280, R26-281, R26-282, R26-283, R26-284, R26-285, R26-286, R26-287, R26-288, R26-289, R26-290, R26-291, R26-292, R26-293, R26-294, R26-295, R26-296, R26-297, R26-298, R26-299, R26-300, R26-301, R26-302, R26-303, R26-304, R26-305, R26-306 | Current P69 page and body integration queue | 🔄 In progress | Parent / P69 owner | Update each open child row when its slice is reviewed; preserve operator gates until the corresponding frames are read. | [P69 plan](../../.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md); [historical child evidence](BACKLOG-HISTORY-2026-09.md) (search child ID) |
| MM-EXCH-01 | Martial Matters source-timed fight exchange in multiple looks | 🔄 In progress | Modeling/video parent; two-day exchange-first priority | Produce a reusable 105-frame source-clock recipe and at least two distinct playable review looks; preserve V12, real contact/ground timing and native-pitch audio; require phone-frame visual review before any approval. | [Exchange-first plan](../../.claude/PRPs/plans/knockout-five-animated-variants.plan.md#operator-priority-pivot--2026-09-24-exchange-first); project `production/animated-variants/exchange-first/PLAN.md` |
| R26-31 | Bravos exploration review and next selection | ⏸️ Deferred | Parent; trigger: next Bravos reference review | Select the next experiment only when that review is scheduled; retain its analysis in the review artifact. | [Exploration review](EXPLORATION-REVIEW-2026-09-10.md); [history: search R26-31](BACKLOG-HISTORY-2026-09.md) |
| R26-35 | Tokyo bed swell timing | ⏸️ Triggered | Audio lane; trigger: next sound-bed review | Recheck the swell against the actual camera arrival and record a listened comparison. | [history: search R26-35](BACKLOG-HISTORY-2026-09.md); P51 T0 context |
| R26-36 | Page-transition sound map | ⏸️ Triggered | Audio lane; trigger: next sound-bed review | Recheck the `:cut`/option parsing on a listened build and record the exact cue result. | [history: search R26-36](BACKLOG-HISTORY-2026-09.md); P51 T0 context |
| R26-43 | Long series tag placement | ⏸️ Triggered | Parent; trigger: first cut with a tag wider than its chart | Decide an authored refusal or shorter label behavior from that cut; retain the measurement. | [history: search R26-43](BACKLOG-HISTORY-2026-09.md) |
| R26-44 | Wire timing through a page build | ⏸️ Triggered | Parent; trigger: first cut that threads a line | Decide whether the wire belongs to the page or between pages, then review the seam. | [history: search R26-44](BACKLOG-HISTORY-2026-09.md); HF-16 |
| R26-45 | Measured page boxes for approved shorts | ⏸️ Triggered | Parent; trigger: next new short | Measure the episode fixture and compare the rendered boxes before changing a frozen approved cut. | [history: search R26-45](BACKLOG-HISTORY-2026-09.md); `page-boxes.v1.json` |
| R26-52 | Japan build-beat timing | ❓ Revalidate | Parent | Confirm whether the row’s roll-out-clock change has a completed proof; do not treat its old plan note as closure. | [history: search R26-52](BACKLOG-HISTORY-2026-09.md); P51 context |
| R26-57 | Stage-space text rendering | ❓ Revalidate | Parent | Compare the unresolved row with R26-48 and current text-rendering evidence; merge only if the defect and acceptance are identical. | [history: search R26-57](BACKLOG-HISTORY-2026-09.md); R26-48 is a possible, unconfirmed overlap |
| R26-65 | Hook-page built entry default | 🟡 Partially built | Parent; trigger: default decision / next hook build | Resolve the remaining default/register question, then prove the selected default on a rendered hook page. | P53 T1 evidence; [history: search R26-65](BACKLOG-HISTORY-2026-09.md) |
| R26-66 | Transition hand-off during narration | 🟡 Human review follow-up | Parent; operator frame review required | Restore the whole sequence so the hand-off transforms rather than reads as a jump; then show the frames for operator acceptance. | [E99 s19](../portable/OPERATOR-RULINGS.md); P57 plan; [history: search R26-66](BACKLOG-HISTORY-2026-09.md) |
| R26-85 | Strobe cadence and motion sharpness | 🟡 Measurement / visual review pending | Parent; trigger: representative real motion in the 100–300 px/s range | Keep 154 px/s as the cited cinema-parity reference; measure the remaining sharpness/space question on real motion before promoting a 250/300 threshold. | E99 s30; strobe research; [history: search R26-64](BACKLOG-HISTORY-2026-09.md) |
| R26-123 | Caption-life default | 🟡 Decision recorded; implementation pending | Parent | Make the operator-selected `blend` the compiler default only after a focused rendered check; keep opt-in behavior and approved cuts stable. | E99 s6; `_caption_life()` still returns `None` when no setting is authored |
| R26-124 | Race path default | ❓ Ruling needs reconciliation | Parent | Verify whether E99 s8 selected `eased` or `clothoid`; record the default explicitly, or leave both selectable if no default was chosen. | E99 s8; R26-78 two-path evidence; [history: search R26-124](BACKLOG-HISTORY-2026-09.md) |
| LEGACY-REVALIDATION-2026-09 | Older backlog rows outside this first-pass archive | 🟡 Parent review queue | Parent; next pass | Reconcile the remaining historical rows against direct plan, commit, artifact, and operator evidence before archiving or deleting any. The cleanup report names the close-marked census. | [First-pass cleanup report](BACKLOG-DISCIPLINE.md#first-pass-cleanup-report) |

## Model-engine research routing — 2026-09-23

Compatibility heading retained for the research-intake deep link. The current
ME-BL and ME-EXP queue entries are immediately below; historical rationale is
in [`BACKLOG-HISTORY-2026-09.md`](BACKLOG-HISTORY-2026-09.md#model-engine-research-routing--2026-09-23).

## Modeling research — triggered backlog

| ID | Work | Status | Owner / trigger | Next action / acceptance | Evidence |
|---|---|---|---|---|---|
| ME-BL-01 | Character delivery optimization: QEM/LOD, texture and mesh compression, baked deform-only Rigify export while preserving editable Blender source | ⏸️ Triggered | Modeling lane; trigger: approved detailed character exceeds a measured delivery budget | Compare silhouette, seams, joint deformation, animation parity, bytes and time on the same poses. | [3D rigging / WebGL blueprint](../research/motion/RIGGING_3D_MODELING_WEBGL_IMPACT_OPTIMIZATION_RESEARCH_BLUEPRINT.md) |
| ME-BL-02 | Optional Three.js live skinned-character runtime and batching | ⏸️ Triggered | Modeling lane; trigger: a concrete shot cannot be served by offline Blender renders and raster passes | Measure a representative interactive need and target hardware before a runtime is promoted. | [3D rigging / WebGL blueprint](../research/motion/RIGGING_3D_MODELING_WEBGL_IMPACT_OPTIMIZATION_RESEARCH_BLUEPRINT.md) |
| ME-BL-03 | Continuous strike contact methods, including XPBD/GJK-style candidates | ⏸️ Triggered | Modeling lane; trigger: authored motion and IK miss a measured contact/penetration budget | Compare residuals, stability, impact readability and render time; do not infer injury physics. | [3D rigging / WebGL blueprint](../research/motion/RIGGING_3D_MODELING_WEBGL_IMPACT_OPTIMIZATION_RESEARCH_BLUEPRINT.md) |
| ME-BL-04 | Resolve the saved fight-shorts rim/transition needle only if the chosen fighter costume retains it | ⏸️ Triggered; deferred behind likeness | Modeling lane; trigger: T4b first recognizable editable fighter head passes internal visual review and the final costume still uses this generic shorts mesh | The current generic shorts may be replaced. If reused, repair the source polygon-40/382 overlap and Solidify rim/offset interaction without T5a.12's 12/11 new flipped triangles or 12 new self-overlap pairs; then recheck neutral, knee, native/phone silhouette and body clearance. Do not change the saved asset now. | [Model-engine plan T4b and T5a.6–T5a.12](../../.claude/PRPs/plans/SHARED-MODEL-ENGINES.plan.md); ignored `artifacts/t5a12/T5A12-RESULTS.md` in `codex/model-garment-stress` |
| MM-HAND-01 | Reusable closed-fist/4 oz MMA glove assembly and head/body contact | 🟡 Next modeling gate — Sol proof negative | Modeling lane; retarget strike IK/contact path and bind a fitted glove before body-target expansion | Sol identified the incorrect lateral finger-curl axis and proved hand-local attachment, but phone renders still read as a capsule; f10 pad/head gap 52.9 mm and f10/f24 guard-relative wrist changes 46.6°/33.6° fail. Preserve failed shells as negative evidence. Next resolve hand/forearm orientation and pad-to-target trajectory, then fit actual glove art; only after a head-contact pass reuse that assembly for body contact. Do not merge the failed procedural shell or claim force/injury physics. | [Sol work order](../../content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/exchange-first/WORK-ORDER-HAND-SOL.md); [execution ledger](../../content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/exchange-first/HAND-CONTACT-LEDGER.md) |

## Explore — bounded comparisons

| ID | Experiment | Status | Owner / trigger | Next action / acceptance | Evidence |
|---|---|---|---|---|---|
| ME-EXP-01 | Compare image-to-3D candidates, including Tripo/Meshy, against procedural Blender detail on the same fighter reference | 🧪 Explore | Modeling lane; trigger: reference and candidate assets are available | Matched camera/light/pose; compare topology, editability, rig stress, identity, provenance/license, cleanup and time. Promote only after human review. | [AI 3D automation blueprint](../research/tech/AI_LLM_3D_MODELING_AUTOMATION_RESEARCH_BLUEPRINT.md) |
| ME-EXP-02 | Compare local depth, segmentation and inpainting as optional 2.5D plate preparation | 🧪 Explore | Modeling lane; trigger: a plate has a concrete parallax/disocclusion need | A/B against authored layers for edges, cleanup time and seek-safe compositing; keep chart/UI depth authored. | [AI 3D automation blueprint](../research/tech/AI_LLM_3D_MODELING_AUTOMATION_RESEARCH_BLUEPRINT.md); P45 T9 |
| ME-EXP-03 | Compare joint topology and corrective deformation on a detailed fighter source | 🧪 Explore | Modeling lane; trigger: detailed source asset and deep-flexion test poses exist | Same rig, weights, poses, cameras and lights; compare baseline LBS, correctly configured preserve-volume, joint-loop reroute and corrective candidates by local area/edge/twist, self-intersection, rendered silhouette and processing time. Closed-volume metrics only after validated caps. No universal loop or speedup target. | [Second-wave intake](../research/model-engines/NEW-RESEARCH-INTAKE-2026-09-23.md#second-wave-anatomy-deformation-and-topology-2026-09-23); T5a.4 diagnostic |
| MM-EXCH-02 | Anime and caricature effects beyond the exchange-first cut | 🧪 Explore | Martial Matters lane; trigger: MM-EXCH-01 has phone-reviewed source-timed proof | A/B recoil afterimage, world-anchored cage/mat glow, multi-view photo wrapping, and blocky/big-head 3D caricature against the accepted footage-backed shot for likeness, contact, clutter, render/edit time and provenance. Promote effects only after a rendered proof; full arena/booth are later assets. | [Project effect candidates](../../content/video_engine/projects/martial-matters/pilots/knockout-brain-matchcut-001/production/animated-variants/exchange-first/EFFECT-CANDIDATES.md); [anime blueprint](../research/motion/ANIME_AURAS_NARUTO_TRANSITIONS_RESEARCH_BLUEPRINT.md) |

Completed rows with source-bound proof are indexed in
[`backlog/archive/2026-09-completed.md`](backlog/archive/2026-09-completed.md).
Rules and the first-pass census are in [`BACKLOG-DISCIPLINE.md`](BACKLOG-DISCIPLINE.md).

## Historical record — retained, not the active queue

The complete source ledger from original `BACKLOG.md` lines 55–921 is preserved in [`BACKLOG-HISTORY-2026-09.md`](BACKLOG-HISTORY-2026-09.md). Historical status words are not current queue state; use the active tables above.
For old citations, original line n ≥ 55 maps to history line n - 47; for example, original line 218 maps to history line 171.
