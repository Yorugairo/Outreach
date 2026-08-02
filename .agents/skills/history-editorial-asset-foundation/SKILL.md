---
name: history-editorial-asset-foundation
description: Build and review timestamp-bound still-image foundations for evidence-constrained history explainers. Use when translating approved narration into original documentary plates, visual action cut-ins, asset manifests, and contact-sheet gates before any animation or final assembly.
---

# History Editorial Asset Foundation

Use this project-scoped workflow for the History of BJJ lane or another
evidence-constrained illustrated history episode. Build the visual base before
attempting animation.

## 1. Establish the source of truth

1. Read the active `canonical_visual_coverage` schedule, prompt spine, and
   latest prompt amendment before selecting assets.
2. Bind every proposed asset to a slot ID, narration excerpt, coverage hash,
   intent, and any required visual action.
3. Treat a schedule or interpretation change as a compiler change first. Create
   a versioned schedule and update its hash before generating replacements.
4. Never reuse a nearby legacy image merely because it looks suitable. Adopt
   only exact approved asset IDs and hashes into a successor schedule.

## 2. Plan a bounded candidate wave

- Generate 8–12 consecutive primary plates per wave; use one primary plate per
  timestamp slot.
- Add a distinct cut-in for every meaningful enumerated item, parallel clause,
  or named role that the schedule marks as a visual action. Do not cut on every
  noun.
- Give each beat one clear visual job: setting, human role, contrast, evidence
  boundary, transition, or explanatory concept.
- Design adjacent shots as a sequence of different compositions, scales, and
  visual states. A world pack may recur; a primary plate may not.

## 3. Write grounded prompts

Always state both the **world** and the **medium**:

- Name place, period, architecture, vegetation, weather, clothing, and social
  setting. Woodblock is a rendering language, never a location.
- Keep the Combat Woodblock identity clean: sharp carved ink contours, broad
  flat indigo/ochre/rust/jade fields, faint paper only, no photographic grit.
- Use anonymous interpretive reconstructions. Generated pixels never establish
  a historical fact, named person, date, route, relationship, or likeness.
- Reserve clear, grounded staging. Keep people, props, boats, furniture, and
  later cutout lanes inside frame and supported by a credible surface.

Prohibit generated text, labels, logos, citations, maps, route arrows, charts,
lineage graphs, fake documents, blank book/card symbolism, and generic overlay
surfaces. Use local editorial layers for claims, citations, dates, and maps.

For History V4, avoid multi-person grappling choreography and instructional
technique sequences. Show social settings, training thresholds, public venues,
or ordinary objects instead.

## 4. Quarantine and inspect

1. Generate through the approved still-image path only; do not invoke narration,
   animation, video providers, or final assembly during a plate wave.
2. Copy each candidate into the job-local wave directory without overwriting a
   prior candidate. Record its source path, dimensions, SHA-256, prompt role,
   slot/action support, and `render_eligible: false`.
3. Build a labeled contact sheet in reading order and inspect it as a sequence.
4. Reject visibly wrong candidates before operator review. Preserve the rejected
   file, hash, and reason; generate a sibling replacement rather than editing
   history.

Reject a candidate for any of these: wrong geography, medium mistaken for
location, poor body/prop grounding, repeated adjacent composition, unwanted
technique choreography, generated text, false evidence cues, or a visual that
does not serve its narration.

## 5. Promote only after the gate

- Require an explicit operator selection for every candidate wave.
- Write a new partial `asset_manifest.v1` for approved assets. Bind the active
  coverage hash, review decision, rights/likeness/alteration guardrails, exact
  local byte hashes, and `render_eligible: true`.
- Validate it with `validate-assets`, then resolve it into a job-local
  `resolved_assets.json` and `credits.json` using `AssetResolverService`.
- A partial promotion never authorizes a full storyboard, animatic, narration,
  provider submission, Gate A, or publication.

## 6. Preserve learning

After each wave, append the evidence and any new guardrail to the active PRP.
Update the production specification only when the rule itself changes. Capture
repeated project-specific corrections as continuous-learning instincts and keep
them project-scoped unless they prove useful across separate projects.
