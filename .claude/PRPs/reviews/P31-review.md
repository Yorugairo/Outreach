# P31 independent review

Reviewer: `reviewer` subagent, read-only, 2026-08-11.

## Initial findings and disposition

1. Evidence binding hydration was not represented in the raw snapshot item
   type. **Fixed:** `FrameTrackItem` now carries the closed binding shape and
   `snapshotToTimelineDocument()` preserves it. A regression test proves all
   four binding identifiers survive hydration.
2. Manual palette placement used world-label substring heuristics. **Fixed:**
   manual placement now resolves exact `world_asset_id` profiles and ordered,
   safe slots from `plate_layout_profiles.v1`; no label substring selects a
   reviewed slot.
3. The reviewer interpreted the legacy standalone Word by Word Bit as the
   transcript-caption renderer. **Not a defect:** the standalone Bit remains
   available for authored text effects, while canonical captions route through
   `ProductionTimelineComposition` to `renderTranscriptCaption()` with
   immutable word tokens. Tests assert the transcript caption ID is absent
   from the standalone Bit registry.
4. The reviewer reported that explicit acceptance did not persist binding
   proof. **Not a defect:** acceptance inserts `bindingId`, `bindingHash`,
   `slotId`, and `worldAssetId`; the revision diff serializes the complete new
   item; the server rejects stale or altered binding fields.
5. Generic-profile fallback was reported as fail-open. **Not a defect:** the
   generic profile is `manual_only`; compiler state becomes `manual_only`
   whenever the resolved profile is not reviewed. An explicitly unknown
   profile remains an error. Focused tests assert both generic and unresolved
   profiles cannot produce a recommendation.

## Follow-up verdict

No unresolved blocker was found after the profile-routing and binding-hydration
changes. The reviewer retained three non-blocking residual risks:

- Operators could deliberately use the legacy authored-text Word by Word Bit
  for caption-like copy; it remains visually distinct from protected transcript
  captions.
- Render-input props omit the non-rendering binding object, while immutable
  `revision.json` and `timeline.json` retain it.
- Accepting a semantic recommendation inserts the bound evidence card; hand,
  annotation, and source-marker choreography remains a separate authored/proof
  step rather than an automatic side effect.

These are within P31 scope: the matcher never silently authors additional
timeline items, render props contain only render inputs, and the immutable
revision/timeline remain the audit authority.
