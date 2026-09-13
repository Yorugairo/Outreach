---
name: chart-form-rulings-e50-e53
description: "Four rulings written 2026-09-07 that govern how a chart lives, moves and is labelled - the deployed clock, the push tie, the citation, and chart form; E60 the breakthrough is a rescale (2026-09-10)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-08T01:53:14.811Z
---

Four operator rulings landed on 2026-09-07 in `docs/portable/OPERATOR-RULINGS.md`. They bind every page and override the
docs. The gist, so an agent knows they exist before designing a chart:

- **E50 - a chart's deployed life.** 6-8 s from its LAST DATA MARK on average, 12 s at most; then it un-draws or becomes the
  next thing. The clock starts when the last data point lands, not at the first cap; annotations (spotlight, callout,
  retitle) do not restart it. Gate **M21**. The 12 s ceiling exists so a chart can hold under a dock's clip.
- **E51 - a push is tied to a landing.** A punch or focus_zoom is punctuation on an ARRIVAL (a badge, a datum a build
  reached, a card that just landed). A zoom on something that has been sitting there is filler and is cut. Gate **M22**
  (tied = a landing within at - 1.5 s to at + 0.3 s). The largest legal push is the SNAP: a landed card grows to be the world.
- **E52 - a page cites, it does not footnote.** One short line, institution and month, small and low-ink (`src_style:
  compact`). The IDs, URLs and hashes live on the object and in the dossier. A chart must read with NO caption, and the
  number the sentence turns on is drawn, not left to the voice.
- **E53 - chart form is law, not taste.** The Cleveland & McGill hierarchy (position on a common scale first, area and
  saturation last) is why our refusals exist; never a stacked bar (baseline drift); bars are discrete and lines continuous,
  so uneven epochs never sit on a continuous axis; **one unit before two** - a page whose title claims in one unit is
  strongest in that unit alone, and when two are truly needed it is an OVERLAY, never separate tiers; a POLICY rate is a
  RULE (`axes.hlines`), not a series, and the window opens at its last change so it never steps; the GAP between what is set
  and what is paid is drawn (`spread`), because a number a viewer must subtract is one they will not; a declared colour
  outranks the sign default; the label lives at the line's end, never in a legend box.

The gating and triage of the research behind E53 is `docs/content-video-engine/MACRO-CHART-INTAKE-2026-09-07.md`.
Related: [chart-proof-not-homework](chart-proof-not-homework.md), [chart-reads-at-a-glance-e28](chart-reads-at-a-glance-e28.md), [judge-the-frame-not-the-diff](judge-the-frame-not-the-diff.md),
[nothing-ever-goes-truly-still](nothing-ever-goes-truly-still.md).

**2026-09-10, E53 second amendment - the CENSUS exception:** a treemap is allowed only for breadth or a named subset (how many, which), the subset marked and its share WRITTEN, labels only where they fit, a size claim takes its bar. The donut's four conditions have a sibling; everything else in the area tier stays refused. Bravos shots 89-91 are the reference; the icon board is the cheaper form for a pure count.


**E60 (2026-09-10) - the breakthrough is a RESCALE:** a bars page states the scale the honest bar reads on; the bar that
cannot fit builds to the comparator's level, holds, then shoots to its number while the scale rewrites under it (Bravos's own
move, measured at 8:02 of the SPR chart). Never a break glyph (a broken-axis mark says "abbreviated"). `overflow: "burst"` is
the breakthrough; `"stack"` (one comparator per step, off the page) is an option; the stop-motion blend is R26-30. The
compiler checks an overflow page (`_validate_overflow`). Operator: "the re-scale is the way ... But this works."
