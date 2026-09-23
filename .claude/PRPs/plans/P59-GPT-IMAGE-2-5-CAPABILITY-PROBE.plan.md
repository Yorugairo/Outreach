---
id: P59-GPT-IMAGE-2-5-CAPABILITY-PROBE
title: GPT Image 2.5 layered-plate capability probe
status: complete
operation: spike
risk: low
owner: parent
branch: main
created: 2026-09-14
updated: 2026-09-14
---

# GPT Image 2.5 layered-plate capability probe

## Summary

Run a four-asset, review-only GPT Image 2.5 probe for P58's generation-route decision: one opaque environment plate and three separate transparent foreground planes registered to its camera. This tests coherent spatial planning and native alpha; it does not claim that a selectable ChatGPT Images `6 Pro` driver is or is not behind the call.

## Intent And Acceptance

Accepted when a quarantined asset kit has (1) a shared scene/camera brief, (2) one far plate plus mid, subject, and near roles, (3) measured dimensions and alpha status, (4) a labelled contact sheet, and (5) an operator-readable verdict on registration, seams, and layer usefulness. It is input to P58 T1, not P58 implementation.

## Scope

- Four built-in image-generation calls, each producing one source asset.
- A reference-conditioned follow-up for every layer after the far plate.
- Quarantine, hashes, alpha/dimension measurement, and a review contact sheet.

## Not Building

- No API call, API key, CLI image-model selection, image-model billing claim, video render, asset promotion, canonical library intake, P58 code change, or edit of P58.
- No assertion that the exposed tool is driven by `6 Pro`; only surfaced metadata may establish that.

## Human Gates

The operator authorised image calls on 2026-09-14. This authorises exactly this four-call probe and review-only storage. A second cohort, re-rolls beyond this probe, canonical promotion, and any route decision remain operator gates.

## Mandatory Reads

- `C:/Users/Snipe/.codex/skills/.system/imagegen/SKILL.md`
- `C:/Users/Snipe/.codex/skills/asset-claim-and-quarantine/SKILL.md`
- `docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md`
- `docs/content-video-engine/45-PARALLAX-AND-PLATE-MOTION.md`
- `docs/content-video-engine/26-AGENT-GENERATION-LOOP.md`

## Patterns To Mirror

- `docs/content-video-engine/24-COMPOSITION-AND-SCALE-SPEC.md`: the existing far / board / mid / near depth vocabulary and registration requirements.
- `docs/content-video-engine/26-AGENT-GENERATION-LOOP.md`: source-first generation followed by alpha extraction or verification, deterministic measurement, and quarantined review.
- `content/video_engine/scripts/contact_sheet.py`: the existing labelled-review artifact rather than an ad-hoc visual proof.

## Execution Path

### Recall

`docs_find "2.5D"` and `docs_find "parallax"` identify the existing four-plane contract and the ban on single-image depth warps. P58 is the dependent implementation plan; this probe produces only its generation evidence.

1. Generate the opaque far plate with an intentionally fixed camera, horizon, palette, and empty staging areas.
2. Use that plate as the reference image for the three role-specific transparent assets.
3. Copy raw outputs to `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p59-gpt-image-2-5-capability-probe/`; preserve original generated files.
4. Measure binary SHA-256, dimensions, alpha presence and alpha coverage; create a labelled contact sheet.
5. Record the tool surface as `built-in image generation`; mark model-driver provenance `unverified` unless returned by the tool.

## Task Slices

### T1: Generate the registered source kit
- Status: complete
- Owner: parent
- Depends on: none
- Write set: built-in generated-image store; quarantine source directory
- Acceptance: far, mid, subject, and near sources exist; each layer call uses the far plate as its composition reference and explicitly requests transparency.
- Validate: visual inspection of all four returned images.
- Evidence: four source images at `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p59-gpt-image-2-5-capability-probe/` (generated 2026-09-14).

### T2: Measure and package review evidence
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: quarantine `manifest.json`, contact sheet PNG
- Acceptance: manifest records prompt role, source SHA-256, dimensions, file mode, alpha status and `driver_provenance: unverified`; contact sheet labels each role.
- Validate: `python content/video_engine/scripts/contact_sheet.py --help` and a manual manifest-to-files check.
- Evidence: `manifest.json` and `contact-sheet.png` in the same quarantine directory. Measurement: far RGB opaque; mid RGB/no alpha; subject RGB/no alpha; near RGBA with 80.34% fully transparent pixels and 68,424 partial-alpha pixels.

### T3: Record the route finding for P58
- Status: complete
- Owner: parent
- Depends on: T2
- Write set: this PRP's evidence section only
- Acceptance: records whether the kit is sufficient to enter P58 T1, what failed, and why no asset was promoted.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P59-GPT-IMAGE-2-5-CAPABILITY-PROBE.plan.md`
- Evidence: prompted native alpha is not yet a dependable four-layer route: only one of three explicit transparent requests had alpha. A subsequent house-style keyed-host pass on nominal `#00FF00` drifted from exact RGB but yielded an 88.17% dominant-green field and a preliminary RGBA extraction (`keyed-finance-host-extracted-rgba-v2.png`). White compositing hid the residual spill; house-cream and charcoal composites reveal a visible green fringe, so it is **not promotable** until the partial-alpha edge band is despilled. For non-environment layers, use a border-connected keyed extraction plus despill before segmentation/inpaint remediation; do not promote any asset.

## Verification

- `python scripts/prp_validate.py .claude/PRPs/plans/P59-GPT-IMAGE-2-5-CAPABILITY-PROBE.plan.md`
- Each raw asset is present, nonempty, independently hashed, and visually inspected.
- Transparent roles are reported from actual pixel alpha, not prompt intent.

## Evidence And Handoff

All imagery remains under the gitignored project quarantine path with `render_eligible: false`. The contact sheet and manifest, not an assertion, are the handoff to the operator and P58 T1. A route decision needs the operator's later ruling.
