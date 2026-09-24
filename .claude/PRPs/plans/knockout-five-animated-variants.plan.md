---
id: MM-KNOCKOUT-ANIMATED-5
title: Five animated knockout variants
status: running
operation: feature
risk: standard
owner: parent
branch: codex/Astra
created: 2026-09-20
updated: 2026-09-24
---

## Summary
Build five private-review variations from the existing V12 short: Saitama, Roshi, detailed 2D, deliberately stylized actual 3D, and minimalist 2D.

## Operator priority pivot — 2026-09-24, exchange first

The five full remakes remain a longer-term goal, but the next two-day target is the **source-timed fight exchange**, not five full re-edits. The operator explicitly selected "fight exchange first" and accepted footage-backed still overlays, source-image tracking, or photo-derived looks on a rig as a valid near-term path. This supersedes the earlier "full animated styles must replace scenes, not be filters over footage" rule **for this exchange-first proof only**; it does not make a posterization filter or an untracked static jump cut an accepted animated remake.

Use the real Sharaf–Steveson source as the 105-frame/30 fps action, contact, recoil, ground, and audio clock. Preserve V12 and all raw sources. First produce a reusable review-only exchange recipe and at least two genuinely distinct, playable look proofs at the source timing: one 2D/anime-footage composite and one characterized blocky/big-head 3D or 2.5D look. Existing Saitama overlay is the baseline to beat, not a new deliverable. If the blocky look cannot retain recognizable fighters or convincing contact within the two-day window, show a measured failure and ship the successful exchange proof rather than labeling a rough rig final art. Full scenes, interviews, booth, octagon, and five complete shorts are not the two-day gate.

Near-term effect selection from `docs/research/motion/ANIME_AURAS_NARUTO_TRANSITIONS_RESEARCH_BLUEPRINT.md`: pose-matched transformation flash/aura before the strike; directional speed/energy accents during acceleration; a contact-anchored single-frame flash/ink burst; brief visual impact punctuation and recoil accents **without slowing or warping the source audio**. These are candidates until rendered and visually reviewed; numerical anime/impact constants in the research are not production truth. Do not stack all effects merely because they are available. Larger environment shockwaves, volumetric auras, multi-angle view-dependent wraps, and full simulated fights stay experimental.

Mechanics gate: a fast linear jab and a stronger pivot-driven hook must read differently. At contact the fist does not tunnel, stick to the target, or push deeper; the striking hand returns toward guard while the opponent reacts and the next-hand/head/foot transitions overlap naturally. The visually floating foot in a generated still is an art failure even if the underlying rig's sole metric passes. Source-clock contact and ground landmarks, likeness at phone size, audio continuity, full MP4 decode, and parent visual review are required. No provider spending or publication is implied.

## Intent And Acceptance
User said proceed after selecting more characterized 3D models and a fifth minimalist 2D version. Preserve clear contact/recoil/full follow-through, original allegation attribution/no-charge wording, continuous balanced music, and original-pitch source sound. For the eventual five full remakes, animated styles must replace scenes, not be filters over footage; the exchange-first pivot above explicitly permits source-footage composites as its near-term proof. First checkpoint is genuine motion proofs, not another static concept board.

## Scope
Project-local asset generation, model and animation authoring, audio reactions and assembly. New outputs under production/animated-variants. Preserve V12.

## Not Building
No publication, purchases, global configuration, shared engine migration, photoreal 3D, graphic injuries or unverified accusations. No forced Git changes.

## Human Gates
Style direction accepted with the operator's 3D correction and subsequent proceed. Generated output remains review-only pending operator judgement; no release approval claimed. Any unapproved provider spending or login dependency is escalated rather than silently worked around.

## Mandatory Reads
AGENTS.md, AGENT_START_HERE, SKILL_ROUTER, AGENTS-VIDEO-ENGINE, PIPELINE, relevant imagegen/Flow/Blender inspection skills; project production ledger and V12 timeline.

## Execution Path
Parallel disjoint local minimalist and Blender proofs; parent produces detailed character assets and retains assembly; isolated Flow preflight establishes video-generation viability. Review actual motion before expansion. Record dependencies and failed attempts.

## Patterns To Mirror
Existing production/assembly-v11 adapter and V12 baseline. Existing impact-v3 real brain mesh can supply the symbolic brain effect. Do not recreate shared player.

## Task Slices
### T1: Detailed 2D and transformation assets
- Status: running
- Owner: parent
- Depends on: none
- Write set: production/animated-variants/plates, prompts and parent ledgers
- Acceptance: three distinct consistent styles, source likeness, usable movement framing
- Validate: visual inspection and file hashes
- Evidence: existing style-board-v1.png; new renders pending

### T2: Minimalist motion
- Status: running
- Owner: minimal_2d_motion
- Depends on: none
- Write set: production/animated-variants/minimal-2d
- Acceptance: 4 second native animated fight proof with readable contact and fall
- Validate: ffprobe and ffmpeg full decode; contact-frame inspection
- Evidence: pending

### T3: Actual modeled 3D motion
- Status: running
- Owner: stylized_3d_proof
- Depends on: none
- Write set: production/animated-variants/stylized-3d
- Acceptance: editable character meshes/controls, stylized face and proportions, contact-follow-through proof
- Validate: Blender structured state, ffprobe and ffmpeg full decode
- Evidence: pending

### T4: Provider preflight
- Status: running
- Owner: flow_motion_preflight
- Depends on: none
- Write set: production/animated-variants/flow-preflight
- Acceptance: verified availability/cost without submitting paid work
- Validate: saved read-only evidence
- Evidence: pending

### T5: Assembly and review
- Status: pending
- Owner: parent
- Depends on: T1, T2, T3, T4
- Write set: production/animated-variants/assembly and audio
- Acceptance: five playable variants, honest proof vs final status
- Validate: full decode, actual picture and audio review, source timing preservation
- Evidence: pending

### T6: Research-backed native 2D rig/contact proof
- Status: running
- Owner: minimal_2d_motion; parent integration/review
- Depends on: user approval of native rig foundation ("agreed")
- Write set: worker production/animated-variants/rig-foundation; parent production/animated-variants/rig-skinning and RIG-ACCEPTANCE.md
- Acceptance: deterministic fixed-length two-bone IK, planted feet, body weight transfer, measured contact before recoil, torso lag, first-contact brain release, and complete fall in a playable four-second proof. Separate actual skinning validation from rigid-piece animation; do not claim the research is already a production solver.
- Validate: project-local pytest, per-frame contact/limb/ground measurements, MP4 full decode, parent picture review.
- Evidence: parent rig-skinning/test_dqs.py six tests passed; rendered integration pending
- Anti-goals: no shared engine migration, no additional Flow spending, no overwrite of prior cuts; no claim that rigid-transform blending guarantees volume preservation of an entire deforming mesh. BBW optimization is not implemented in this slice; authored normalized weights must be labeled honestly.

## Verification
Decode every MP4, check duration/resolution/frame count; inspect before/contact/recoil/ground frames; inspect actual 3D scene state and continuous sound. No generic gate override may be described as an unqualified pass.

## Evidence And Handoff
production/animated-variants/LEDGER.md owns current live handles and next runnable steps. Private review only; completion requires actual artifacts.
