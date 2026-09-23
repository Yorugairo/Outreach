---
id: P60-IMAGE-AND-PROP-CAPABILITY-TESTS
title: Image and prop capability tests using house references and reusable templates
status: complete
operation: spike
risk: standard
owner: parent
branch: main
created: 2026-09-14
updated: 2026-09-14
---

# Image and prop capability tests

## Summary

Find which image-generation workflows reliably produce useful inputs for the existing video engine: reusable prop families, controlled object edits, clean plates, and art with addressable surfaces. Test the operator's Images UI template idea explicitly. Extend the evidence from P59; feed P58's active layer probe without duplicating its compositor or implementing its camera work.

## Intent And Acceptance

The operator requests a PRP for image-generation and prop capability tests and asks whether the UI template used for the icon assets can generate props. The experiment must answer that with saved prompts, references, raw outputs and rendered proof, not a model capability claim.

Accept this investigation when:

1. Every test has a frozen brief, identified input images, observed generation surface, raw output hashes, measurement, visual verdict and labor/call count. Failed calls remain in the denominator.
2. Three useful prop subjects are compared under the same house style and camera, with native-alpha and chroma-key requests. No blanket assertion that either route wins.
3. A short prop adaptation of the operator-supplied template and the expanded production brief are compared on the same two subjects through the same image tool, with identical references and background requests. The template is supplied prompt text, not a separate capability or UI test.
4. Controlled state edits, clean-background repair, and framing changes have evidence for both the requested change and unintended drift.
5. At least two usable candidates, if produced, are exercised with existing prop/page or ART-embed consumers in a separate review fixture. Failed art is reported, not forced into a demonstration.
6. The final report gives an adopt / revise / defer recommendation per workflow and names the smallest missing integration. Small samples establish promising routes, not statistical reliability.

## Scope

Sixteen initial image calls, staged as 6 + 4 + 4 + 2 below. One output per call; all outputs remain review-only. Stop a dependent arm if its required reference or seed fails, and report it as not run. No automatic re-roll loop. Existing permission for image calls persists; this draft defines the experiment before execution.

| Arm | Calls | Question |
| --- | ---: | --- |
| A: three props, two backgrounds | 6 | Does the house brief produce useful shapes, and which extraction route preserves them? |
| B: short template / expanded brief on two props | 4 | Do extra production instructions improve usable results compared with the simple consistency prompt? |
| C: state, repair, framing, and illustration edits | 4 | Can image editing supply reusable scene ingredients while preserving specified invariants? |
| D: exact repeats of the best two prop briefs | 2 | Does the strongest result survive another attempt? |

### Subjects and reference policy

- Toll gate: front three-quarter view, raised-bar version reserved for the edit test; hinge is the measured anchor.
- Wooden shipping crate: blank label panel; lid and panel corners provide measurable geometry. No invented year or numerical claim in generated pixels.
- Locked industrial lever: isolated mechanism with a small legitimate green indicator. This deliberately tests preservation of real green; choose a magenta key for its keyed arm.
- Use the operator's existing approved icon art for visual-family reference and a real house plate for environment/style. Resolve them from manifests/library before opening the image. Use `rg --files --hidden --no-ignore` in named asset directories when gitignored files do not appear in ordinary `rg --files`; missing search results are not evidence of absent art.
- Reference roles are explicit: style reference, identity reference, layout reference, or edit target. Inspect every selected image. The text-only host from P59 is not an approved Mike identity reference.
- Shared style atom: "A light application of woodblock print and vox newspaper with rich anime colors." Do not dilute it with photographic or generic paper-craft instructions.

### Proposed reusable prop template

> Create a reusable editorial prop representing {subject} in state {state}. A light application of woodblock print and vox newspaper with rich anime colors. Use the supplied house artwork as the style reference. Match {camera}, {lighting}, and {palette}. This asset will be placed independently on our cream or charcoal stage and may later participate in a layered composition. Show the complete silhouette, including {required_parts}, with clear gaps and generous uncropped margins. Keep the functional anchor {anchor} visible. Make the prop identifiable at {display_size}. Background: {native_alpha_or_key_instruction}. No surrounding scene, ground plane, cast shadow, lettering, numbers or unrelated objects. Keep {invariants} unchanged across variants.

Background variants: (a) actual transparent PNG; (b) opaque uniform key selected outside the subject palette, with no key-colored lighting/reflections. Record actual key distribution; do not assume exact hex compliance. No background choice is universally safe.

### Operator-supplied template and short prop adaptation

Original template, supplied verbatim by the operator:

> Create an icon set that represents the requested idea clearly at the intended size. Keep symbols simple, legible, and consistent in shape, weight, detail, and perspective. Do not add unrelated imagery, labels, or mismatched visual styles.
> Ask clarifying questions to establish the icon subject, intended use, and visual style. Present relevant icon style directions when available.

Short prop adaptation:

> Create a reusable illustrated prop representing {subject} clearly at {display_size}. Keep it legible and consistent with the supplied reference family in shape, line weight, detail and perspective. A light application of woodblock print and vox newspaper with rich anime colors. Do not add unrelated imagery, labels or mismatched visual styles. Show the complete object with uncropped margins on {background}. Intended use: an independently placed prop on our cream or charcoal video stage.

Subjects, use and style are already established in this brief; do not insert redundant clarification turns. Test toll gate and crate, one asset per call, under short and expanded prompts. This initial comparison tests instruction density; style/geometry are rated side by side with extraction readiness. Set/sheet batching is a later option if singles succeed, not a hidden format change in this comparison. Record both prompts exactly and keep the same reference inputs, output target and background mode within each pair.

### Editing arm

1. Raise only the toll-gate bar on the best valid seed; preserve base, hinge, camera, palette and canvas. Measure base/hinge drift; this tests state continuity, not skeletal animation.
2. Remove a single foreground object from an existing house plate and reconstruct the exposed background. Inspect changed and protected regions; generated reconstruction is illustration, not historical evidence.
3. Extend that same plate to a second aspect ratio while preserving its original central region. Record all changes inside the protected region; do not call this responsive layout generation.
4. Generate an illustrative vignette using the same toll gate and house reference, with the object as the message and a clear staging area. Judge whether composition/reuse gains justify generation compared with placing the existing prop.

## Not Building

- No new renderer, production intake subsystem, body rig, relation solver, or P58 depth implementation.
- No generated factual chart, invented evidence text, or argument chart embedded inside a TV. Existing ART-embed accepts appropriate press/still/video content; argument charts stay in their own lane.
- No canonical asset promotion, replacement of approved art, approved-cut rebuild, API fallback, billing-equivalence claim, or undocumented model/effort selection.

## Human Gates

The operator explicitly requested `prp-implement p60` on 2026-09-14, approving this test matrix. Image-call authorization has already been given and need not be requested again. Operator review selects any art for promotion separately; code never marks it approved.

The operator supplied the complete template text, removing the UI-access dependency. Run both prompt variants through the same built-in image tool. Record surfaced metadata without inferring hidden routing or subscription accounting.

## Mandatory Reads

- `docs/AGENTS-VIDEO-ENGINE.md`, `docs/runbooks/PRP_EXECUTION.md`, `docs/runbooks/RECALL-RECEIPT.md`.
- `docs/portable/OPERATOR-RULINGS.md`: E39 style, E94 icon-art approval, E95 surface fill, E97 relation layer, E98 layered-generation intent.
- `docs/content-video-engine/52-CONSTRUCT-DONT-INHERIT.md` section 52.3; `CAPABILITIES.md` ART-embed rows; `BACKLOG.md` A2b, X4, R26-61, R26-105, R26-122.
- P58 T1 and P59 evidence, plus the imagegen and asset-claim-and-quarantine skills at execution time.

## Execution Path

Recall: `docs_find "prop library"` found A2b's five Tokyo props, X4's composition question and the existing object-page contract. SigMap `ask "generated props asset catalog intake claim template"` found `test_ledger_object_variant.py` and `finance_channel.py` manifest/catalog validation. `ast-grep outline` located `asset_measurement.measure_asset`, `asset_catalog.load_catalog` and `register_assets`.

Recall: E97 explicitly defers the figure rig; R26-105 describes the evidence/camera relation layer. P58 T1 is running with `probe_2_5d.py`; its production depth/camera slices remain separate. `test_art_embed.py` explicitly refuses argument-chart embeds. These constraints determine the consumers tested here.

P59 baseline: three transparent requests yielded one actual RGBA; its keyed host yielded a preliminary matte with residual green fringe. It did not test a genuine character reference or verify layer registration. Border connectivity alone cannot protect a same-colored subject touching the background, and can retain enclosed background holes. The new tests include internal gaps and a legitimate green feature instead of asserting those problems solved.

Use experiment directory `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p60-image-props/`. Preserve raw sources and derive versioned outputs. Save protocol, prompts, reference hashes, measurements, reviews and contact sheets there. Use a draft local catalog only for a review fixture; keep production eligibility false.

## Patterns To Mirror

- Existing generation manifest validation in `src/services/finance_channel.py`; catalog rules in `src/services/asset_catalog.py`; alpha/color measurement in `src/services/asset_measurement.py` (paths under `content/video_engine/`).
- `content/video_engine/tests/test_ledger_object_variant.py`: asset IDs, distinct placements, datum indices and source requirements for numeric claims.
- `content/video_engine/scripts/contact_sheet.py`: labelled review output, supplemented with correctly alpha-composited cream/charcoal checks (plain RGB conversion is not a transparency proof).
- Existing player shell/runtime and P58 `probe_2_5d.py`; reuse their invocation/contracts if a preview needs them. No independent HTML renderer.

## Task Slices

### T1: Freeze references and the prompt comparison
- Status: complete
- Owner: parent
- Depends on: none
- Write set: experiment directory `protocol.md`, `references.json`, `prompts/`
- Acceptance: real references are located, opened and hashed; the operator-supplied template and both prop adaptations are preserved; 16 call slots and their dependencies are named before dispatch; prompts include house atom and intended downstream use.
- Validate: `python -m json.tool content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p60-image-props/references.json`
- Evidence: experiment `references.json`, `protocol.md`, `prompts/`, and sixteen slots in `calls.json`; parent opened both real references before dispatch. Original template retained verbatim in protocol.

### T2: Produce the prop/background and template arms
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: experiment directory `raw/`, `calls.json`, frozen generation work orders from the existing claim workflow
- Acceptance: A's six outputs and B's four outputs, or explicit blocked/skipped slots, preserve reference and prompt provenance. Short/expanded comparisons hold subject, references, background and tool surface constant. Report any other observed setting differences.
- Validate: `python -m json.tool content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p60-image-props/calls.json`
- Evidence: ten raw A/B PNGs and frozen orders saved with prompt/output hashes and runtime in calls.json. A-gate-green has one interrupted no-output attempt plus one explicit recovery; failed attempt remains in denominator. Seven native-alpha requests: six RGB, one RGBA (B-crate-short); edge readiness not inferred from mode. Final byte-level inspection finds C2PA softwareAgent gpt-image version2.0 in all16 P60 originals, matching P58's reported provenance. Signatures not verified; driver unknown. This does not test2.5.

### T3: Test controlled edits and repeatability
- Status: complete
- Owner: parent
- Depends on: T2
- Write set: experiment directory `raw/`, `calls.json`, `prompts/`
- Acceptance: four edit/vignette outcomes and two repeats recorded. Repeat selection follows initial geometry/style/alpha scores, with all failures retained; no extra calls hidden as retries. A missing valid seed skips its dependent edit.
- Validate: `python -m json.tool content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p60-image-props/calls.json`
- Evidence: all four C and two D outputs saved. D repeats B-crate-short and A-lever-magenta exactly; reasons frozen in calls.json before dispatch. Native-alpha crate repeat returned RGB, lever repeated semantics/style but changed mechanism/orientation. C-gate uses inspected A-gate-green; C repair/outpaint use actual study plate. Sixteen outputs, seventeen attempts including recorded interruption; final drift/edge evaluation belongs to T4/T5.

### T4: Measure the assets and prove current consumer usefulness
- Status: complete
- Owner: implementation_luna
- Depends on: T3
- Write set: experiment directory `measure_probe.py`, `derived/`, `measurements.json`, `review/`, `fixture/`; no production modules
- Execution split: original measurement writer retains harness/proofs/fixture input JSON; a second implementation_luna owns only `fixture/render_consumer.py` and `fixture/render_proofs/` for actual existing-consumer captures. Parent owns integration; no overlapping writes. Named Spark reviewer hit usage limit; independent read-only Luna fallback returned findings and70passing tests.
- Acceptance: a bounded reproducible experiment harness reuses measurement services and existing renderer interfaces; records hashes, dimensions, alpha, key distribution, silhouette bounds, declared-anchor drift and protected-region differences. Review cream and charcoal at intended display sizes and 4x edge crops. Inspect real-green indicator and enclosed gaps; never use largest-component filtering as a universal repair. Despill may need opaque contaminated edge pixels too, so measure before choosing its band. Distinguish extraction damage from generator drift. Exercise up to two acceptable props on an existing object-page review fixture and a suitable press/still on an existing embed fixture if its reference supports one. Evidence stays review-only.
- Validate: `python content/video_engine/projects/systems-and-blowups/tokyo-tea-break/assets/quarantine/p60-image-props/measure_probe.py --check`
- Evidence: measure_probe.py --check rerun by parent: PASS, 16/16 measured, 0 pending. Required three-file pytest suite rerun: 70 passed in 1.20s. measurements.json binds raw/derived hashes; review/ holds 180px cream/charcoal proofs and exact4x display-edge crops. fixture/render_proofs/receipt.json records actual existing-player captures and exact invocation. Independent review/baseline-final-audit.md verifies all four capture hashes/dimensions. Object props use supported cutout docks, not direct object-builder painting; keyed fringe and fixture axis/caption overlap remain explicitly non-production. C-vignette is exercised in the existing TV ART-embed as an illustrative still.

### T5: Review and recommend the smallest integration
- Status: complete
- Owner: parent (independent reviewer reads T4 evidence)
- Depends on: T4
- Write set: this PRP evidence; experiment directory `RESULTS.md`
- Acceptance: per-arm verdict includes all attempted/failed/skipped calls, raw-vs-repaired quality, editing labor, reference fidelity, composition utility and repeatability. Native alpha, key extraction, short template and expanded template get separate findings. Adopt only when subject/geometry and cream/charcoal edge review pass; no false claim that one successful asset proves reliability. Recommendations name existing services to extend and concrete unresolved gaps, with P58 handoff paths. No automatic CAPABILITIES/BACKLOG promotion.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P60-IMAGE-AND-PROP-CAPABILITY-TESTS.plan.md`
- Evidence: RESULTS.md records per-workflow adopt/revise/defer findings, all17 attempts/16 outputs, raw-vs-repaired quality and unmeasured labor, failed repeat alpha and exact registration/canvas constraints. verification.md and independent review/baseline-final-audit.md retain limitations. Smallest extension wraps existing generation_claim/asset_measurement/asset_catalog provenance and validation; P58 HG1 receives flat-plate/depth-intent evidence, no competing camera implementation. These baseline findings are complete; overall P60 remains running for operator-added T6 comparison.

### T6: Operator extension — Flow generation through intake preparation
- Status: complete
- Owner: Gemini via existing bridge; parent verified and integrated findings
- Depends on: T4
- Write set: experiment flow-comparison/; existing provider claim artifacts; separate parent fixture/flow-render-proofs/
- Authorization: operator requested Flow/Nano Banana Pro comparison, treats Flow/Gemini usage as zero marginal cost, and assigned Gemini editing/intake preparation. No additional GPT calls were made.
- Acceptance: three matched cases retain frozen prompts/references and original hashes; Gemini prepares derivatives, masks/provenance and visual proofs; compare raw/prepared quality and labor with GPT; verify actual consumer use and keep review-only.
- Validate: parent reran prepare_props.py --run (exit0, matching final hashes), render_flow_consumer.py --check (PASS), focused three-file pytest (70passed1.29s), and plan validator. JSON parsing is syntax validation only.
- Evidence: flow-comparison/calls.json, manifest.json, INTAKE.md, COMPARISON.md, contact-sheet-cream.png and contact-sheet-charcoal.png; review/flow-raw-audit.md and flow-prepared-audit.md; fixture/flow-render-proofs/receipt.json and actual PNGs; parent COMPLETION-AUDIT.md.
- Findings: three calls/three RGB1376x768 outputs (recorded147seconds total). Crate painted checkerboard was locally segmented with pinned cached U2Net, preserving initial BRIA evidence. Lever keying plus one bounded two-pixel edge cleanup retained green and improved actual larger-placement proof; thin residuals remain a review caveat. Vignette works as a full illustrative TV still. Exact geometry and native-alpha reliability were not established.
- Provenance: all three original metadata records contain the Nano Banana Pro pill; only crate includes separate drawer model/credit quote fields. No inferred API billing/charge equivalence. Parent corrections and unmeasured non-generation labor are recorded.
- Recovery history: authentication initially blocked the job; operator signed in. Same Gemini conversation fd6f6e4c-46b7-4a40-b783-7dcbfc5b797d resumed using documented continuation helpers after original bridge packet was closed. FLOW-RESUME.md records scope. Final conversation is terminal; no generation remains running.
- Handoff: case-scoped intake prototype and candidates are ready for operator review, not production-approved. No production intake subsystem, new renderer, rigging or P58 camera implementation was added.

## Verification

- Plan: `python scripts/prp_validate.py .claude/PRPs/plans/P60-IMAGE-AND-PROP-CAPABILITY-TESTS.plan.md`.
- Measurement harness: check exact hashes and derivation links; finite metrics; correct alpha modes; all 16 planned slots accounted for, including not-run entries.
- Before using current consumers: `python -m pytest content/video_engine/tests/test_asset_measurement.py content/video_engine/tests/test_ledger_object_variant.py content/video_engine/tests/test_art_embed.py -q`.
- Visual review is separate from test success: cream/charcoal composites, useful phone-scale prop recognition, gap preservation, state-anchor continuity and protected-region drift. Flag visible fringe; do not infer a pass from alpha coverage.
- Small harness sanity cases: fully opaque source, genuine alpha, key-colored foreground, enclosed background hole, and soft edge. Expected masks are authored independently of the keyer. No new broad test suite for an experiment.

## Evidence And Handoff

Deliver both reusable prop briefs, the operator-supplied source template, full call ledger, reference hashes, raw/derived asset links, labelled comparisons and a per-workflow decision table. Record exact runtime commands used for review fixtures. P58 receives asset evidence and failure conditions, not a competing camera implementation. The intake proposal follows measured gaps in existing services; it is not preselected as the outcome.
