---
id: P28-DECK-ASSET-CONTEXT-EXTRACTION
title: Extract deck assets with durable semantic context
status: review
operation: feature
risk: standard
owner: parent
branch: codex/stickly-woodblock-variant
created: 2026-08-10
updated: 2026-08-10
---

# Deck Asset Extraction With Context

## Summary

Build a deterministic PPTX source-ingestion workflow for the three silicon decks. It will preserve each original deck and embedded slide image, create stable slide and region identifiers, generate semantic crop derivatives, and record enough provenance and editorial meaning that a renderer can tell what an asset is, where it came from, what claim or beat it supports, and how safely it may be reused.

The decks are operationally simple but semantically baked: each contains 15 slides, each slide contains one 1376x768 RGBA PNG, and the slide XML contains no live text or notes. PPTX is therefore the canonical container for extraction, while the slide PNG remains the canonical visual parent.

## Intent And Acceptance

### Intent

- Make the deck material reusable in whiteboard and 2D scenes without pasting an entire slide on screen.
- Preserve exact source bytes and a complete derivation chain for every crop or isolated element.
- Retain context at three levels: deck, slide, and semantic asset.
- Keep factual text and metrics traceable to the source slide and claim ledger, while separating literal evidence from explanatory metaphor.
- Make the first pass easy to review: source contact sheet, semantic crop contact sheet, and a machine-readable manifest.

### Acceptance

- Running the extractor on the three named PPTX files produces 45 slide records and 45 source-image records with deterministic IDs, dimensions, byte hashes, and slide-to-media mappings.
- The original PPTX files are never overwritten. Optional footer cleanup creates a separate derivative and records original and cleaned hashes plus the exact cleanup policy.
- Every derived crop records its parent deck, slide, media path, parent hash, pixel and normalized crop coordinates, extraction method, and context fields: `what_it_is`, `visual_role`, `representation_mode`, `claim_refs`, `cue_refs`, `factual_text`, `context_status`, and `reuse_policy`.
- No derivative is render-eligible until rights are reviewed and its context is `operator_verified`; automatic OCR or model inference may propose context but cannot approve it.
- Re-running extraction against unchanged inputs produces byte-identical image derivatives and the same manifest artifact hash.
- Contact sheets make it possible to inspect each slide and crop while retaining its stable ID and source slide label.
- Focused tests cover PPTX mapping, byte/hash stability, crop bounds, provenance links, watermark-derivative isolation, and render eligibility gates.

## Scope

- Inputs:
  - `C:/Users/Snipe/Downloads/The_Silicon_Reality_Gap.pptx`
  - `C:/Users/Snipe/Downloads/The_Silicon_Antidote.pptx`
  - `C:/Users/Snipe/Downloads/Silicon_Value_in_a_Software_Bubble.pptx`
- Deterministic extraction of embedded slide media directly from the PPTX ZIP package.
- Optional, non-destructive watermark cleanup for the known lower-right Gemini Notebook footer region, reusing the existing cleanup policy and recording the derivative relationship.
- Slide-level source plates plus semantic region crops.
- Rectangular crops first; polygon/alpha isolation only where a review-approved region needs it.
- A deck asset manifest and schema that can link into existing finance cue, resolution, edit, and asset manifest contracts.
- Contact sheets and a coverage report for human review.
- A small pilot mapping the best source regions for the opening silicon/value mechanism, memory/HBM mechanism, triopoly/consolidation, financial comparison, and valuation divergence beats.

## Not Building

- No re-drawing, image-generation, OCR-based rewriting, or generative reconstruction in this slice.
- No attempt to recover editable PowerPoint objects; the decks do not contain them.
- No raw PDF XObject extraction as a separate path; it previously produced color/mask artifacts and is not the source of truth when PPTX is available.
- No automatic claim verification from slide pixels. Metrics remain bound to the research/claim ledger and require human review.
- No silent removal of logos, citations, or substantive slide content; only the explicitly approved footer cleanup region may be altered.
- No renderer integration or replacement of P27 until the source/crop contact sheet is approved.

## Human Gates

- **H1 — Source authorization:** confirm these decks are operator-owned or otherwise authorized for alteration and production use; keep originals immutable.
- **H2 — Context labeling:** review the slide contact sheet and approve the human-readable meaning for every crop promoted beyond source/reference status.
- **H3 — Factual binding:** approve `claim_refs` and `factual_text` for metrics, labels, and tables. A crop may be visually useful without being evidence-eligible.
- **H4 — Visual promotion:** approve whether each crop is a clean reusable component, a full-slide evidence plate, a reference-only region, or a rejected crop because it reads as a pasted panel.
- **H5 — Renderer pilot:** approve one small scene using the promoted crops before broad extraction of the remaining deck regions.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`
- `content/video_engine/configs/asset_manifest.schema.json`
- `content/video_engine/configs/finance_asset_catalog_v2.schema.json`
- `content/video_engine/configs/finance_edit_manifest.schema.json`
- `content/video_engine/configs/finance_visual_resolution_v1.schema.json`
- `content/video_engine/configs/finance_visual_cue_sheet_v2.schema.json`
- `content/video_engine/src/services/asset_resolver.py`
- `content/video_engine/scripts/clean_pptx_watermarks.py`
- `content/video_engine/tests/test_asset_resolver.py`
- `content/video_engine/tests/test_martial_asset_reuse.py`
- `C:/Users/Snipe/.codex/skills/whiteboard-explainer/SKILL.md`, especially its isolated-art, provenance, and contact-sheet requirements

## Execution Path

1. Register each source deck by absolute input path, original SHA-256, deck ID, title, source family, and operator rights state.
2. Read the PPTX package with `zipfile`; map each `ppt/slides/slideN.xml` to its relationship target in `ppt/slides/_rels/slideN.xml.rels`, then extract the referenced `ppt/media/imageN.png` without recompression.
3. Emit a slide source record containing deck ID, one-based slide number, stable slide ID, original media path, dimensions, pixel format, byte hash, and a preview path. Preserve the deck's original ordering.
4. If cleanup is requested, produce a separate cleaned source deck/media set. Record the original deck hash, cleaned deck hash, media parent hash, cleaned media hash, cleanup rectangle, fill strategy, and operator approval state.
5. Create a human-reviewable slide context file. Structural facts are automatic; semantic labels are explicit fields with `context_status` set to `machine_proposed`, `review_only`, or `operator_verified`.
6. Define crop recipes against source slide coordinates. Store both `bbox_px` and normalized coordinates, plus optional polygon points or alpha-mask path. Generate each derivative from the recorded parent bytes and write its parent hash into the manifest.
7. Use a stable semantic ID format such as `deck-family-sNN-region-role-vN`. Keep source slide identity in the ID and metadata so a crop never loses its origin when copied into a project asset directory.
8. Attach editorial context to each derivative:
   - `what_it_is`: concrete visual description;
   - `visual_role`: hero, mechanism, evidence, transition, label, or reference;
   - `representation_mode`: `literal_evidence`, `accurate_mechanism`, or `declared_metaphor`;
   - `factual_text` and `claim_refs`;
   - `cue_refs` and intended scene/beat;
   - `not_what_it_means`: prohibited inference or overclaim;
   - `reuse_policy`, `review_state`, and `render_eligible`.
9. Generate two review surfaces: a complete deck/slide contact sheet and a semantic crop contact sheet. Each tile must display the stable asset ID, source slide, crop type, and context status.
10. Validate hashes, crop bounds, manifest schema, contact-sheet coverage, and render eligibility. Only after H2-H5 should the selected assets be copied or linked into the whiteboard proof.

## Patterns To Mirror

- Use the existing `asset_manifest.v1` and `AssetResolverService` for local path, hash, rights, and renderer eligibility behavior.
- Use the finance edit manifest's `cue_id`/`asset_id`/`sha256` binding for scene usage rather than duplicating source metadata in renderer code.
- Use finance visual resolution fields for `representation_mode`, selected asset IDs, reuse reason, and evidence surface IDs.
- Use the martial asset catalog/reuse pattern for stable IDs, explicit readiness, reuse scope, and human promotion.
- Use the existing `clean_pptx_watermarks.py` script for the known non-destructive cleanup operation instead of embedding a second ad hoc cleaner.
- Use the whiteboard-explainer asset-generation rules for isolated drawable elements, review contact sheets, context/provenance, and the prohibition on treating a whole composite slide as a hand-drawable element.

## Task Slices

### T1: Define the deck source and derivative contracts
- Status: complete
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/configs/deck_asset_manifest.v1.schema.json`, `content/video_engine/templates/deck_asset_manifest.v1.json`
- Acceptance: Schema distinguishes source deck, source slide, semantic crop, derivation, rights, context status, and render eligibility; template validates and documents the minimum context fields.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P28-DECK-ASSET-CONTEXT-EXTRACTION.plan.md` and a focused JSON Schema validation test.
- Evidence: `python scripts/prp_validate.py .claude/PRPs/plans/P28-DECK-ASSET-CONTEXT-EXTRACTION.plan.md`; `python -m pytest content/video_engine/tests/test_extract_deck_assets.py -q` -> 5 passed.

### T2: Build deterministic PPTX inventory and extraction
- Status: complete
- Owner: implementation_luna
- Depends on: T1
- Write set: `content/video_engine/scripts/extract_deck_assets.py`, `content/video_engine/tests/test_extract_deck_assets.py`
- Acceptance: Extracts exact embedded PNG bytes, maps slide relationships correctly, records dimensions and hashes, preserves ordering, and fails clearly on missing/ambiguous media.
- Validate: `python -m pytest content/video_engine/tests/test_extract_deck_assets.py -q` plus a three-deck fixture/inventory run.
- Evidence: `content/video_engine/projects/systems-and-blowups/sources/decks/deck-asset-manifest.json`; latest artifact hash `33ee064bd25c4d58bfb4aeaa90e1cb6a35b738925f174e5ff6be2c35299f683f`; extraction report -> 45 slides, 45 original source images, 45 cleaned derivatives.

### T3: Add context and crop-derivative generation
- Status: complete
- Owner: implementation_luna
- Depends on: T1, T2
- Write set: `content/video_engine/scripts/extract_deck_assets.py`, `content/video_engine/tests/test_extract_deck_assets.py`, project-local crop recipe and context files under `content/video_engine/projects/systems-and-blowups/sources/decks/`
- Acceptance: A crop is reproducible from a source slide and records parent hashes, pixel/normalized bounds, extraction method, semantic description, visual role, claim/cue links, prohibited implication, and review state.
- Validate: crop-boundary/hash stability tests, manifest schema validation, and a generated semantic crop contact sheet.
- Evidence: 9 semantic crops with parent slide IDs, source hashes, normalized/pixel bounds, context, and review state; three semantic contact sheets under `content/video_engine/projects/systems-and-blowups/sources/decks/*/review/`.

### T4: Create the three-deck source inventory and pilot crop map
- Status: complete
- Owner: parent
- Depends on: T2, T3
- Write set: `content/video_engine/projects/systems-and-blowups/sources/decks/`
- Acceptance: All 45 slides are inventoried; the pilot identifies reviewed candidate regions for the five required beat families and classifies each as reusable component, evidence plate, reference-only, or rejected.
- Validate: inventory count/hash report, contact-sheet inspection, and human gates H1-H4.
- Evidence: three per-deck `source-manifest.json` files validate with zero schema errors; source integrity check -> 45 exact embedded PNG matches; the operator accepted the reviewed crop set after the corrected capacity-penalty crop; render-eligible assets remain 0 because rights/context promotion is intentionally separate.

### T5: Wire one approved crop family into a whiteboard proof
- Status: complete
- Owner: parent
- Depends on: T4 and H5
- Write set: the selected P27 proof variant only, plus its local asset bindings and render manifest
- Acceptance: The review proof uses four selected crop derivatives as layered evidence plates with visible hand-led reveal and no whole-slide paste behavior; the render manifest points back to the deck asset IDs.
- Validate: HyperFrames check passed (0 errors, 0 warnings, WCAG AA text checks 17/17); focused video render, contact sheet, and proof tests passed.
- Evidence: `content/video_engine/projects/systems-and-blowups/pilots/current-bubble-mechanism/finance-whiteboard-deck-asset-proof-v1/render/finance-whiteboard-deck-asset-proof.mp4`; `proof-manifest.v1.json` binds four P28 asset IDs and source hashes; `python -m pytest content/video_engine/tests/test_finance_whiteboard_deck_asset_proof.py content/video_engine/tests/test_extract_deck_assets.py content/video_engine/tests/test_asset_resolver.py -q` -> 19 passed.

## Verification

- Structural: `python scripts/prp_validate.py .claude/PRPs/plans/P28-DECK-ASSET-CONTEXT-EXTRACTION.plan.md`.
- Focused: `python -m pytest content/video_engine/tests/test_extract_deck_assets.py content/video_engine/tests/test_asset_resolver.py -q`.
- Schema: validate the new manifest and template with the repository's JSON Schema tooling.
- Source integrity: compare each extracted slide hash to the exact `ppt/media` member hash; verify 45 slides across the three decks.
- Reproducibility: run extraction twice into separate temp output roots and compare manifest hashes plus every derivative hash.
- Context coverage: fail the promotion report if any render-eligible derivative lacks `what_it_is`, `visual_role`, `representation_mode`, source slide, parent hash, rights state, or operator verification.
- Visual: inspect the complete slide contact sheet and semantic crop contact sheet; reject crops with visible neighboring labels, torn context, watermark seams, or pasted-panel behavior unless explicitly classified as an evidence plate.
- Integration: after approval only, run the focused P27 renderer/test/watch loop and verify source asset IDs resolve through the manifest.

## Evidence And Handoff

- Source inventory: `content/video_engine/projects/systems-and-blowups/sources/decks/<deck-id>/source-manifest.json`
- Extracted slide media: `.../<deck-id>/slides/slide-001.png` through `slide-015.png`
- Crop recipes and context: `.../<deck-id>/semantic-assets/asset-context.json`
- Derived assets: `.../<deck-id>/semantic-assets/assets/`
- Review contact sheets: `.../<deck-id>/review/slide-contact-sheet.png` and `semantic-contact-sheet.png`
- Promotion report: `.../<deck-id>/review/coverage-report.json`
- Handoff must state which assets are source/reference-only, which are evidence-eligible, which are approved reusable components, and which are rejected. It must also include original/cleaned deck hashes and the exact human gates completed.

## Implementation Note

The optional cleaned slide media is recorded in a separate `cleaned_images` collection so the required 45 original source-image records remain exact and countable. Semantic crops may reference either variant through `source_variant`, while render eligibility remains false until the human gates approve rights and context.
