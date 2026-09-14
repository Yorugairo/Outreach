# Work order - the morph that handles holes and topology: implicit-surface blends versus ring correspondence (2026-09-14)

**To:** the Gemini research lane (profile `video-researcher`). **From:** the Claude lane of `Outreach Program`, repo root
`C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `report-landed`. **Skills: use the `/research` skill** - run it as
`/research --deep morphing ink shapes with holes and topology change - implicit / signed-distance-field blends versus ring correspondence, at 12 fps in a browser canvas` (the deep two-pass form: discovery, then full-page primary extraction). Use
`python content/video_engine/scripts/docs_find.py "<term>"` for every claim you check against our docs. A QUESTION, never a design
(RECALL-RECEIPT s3 step 5): the answer is quarantined until the operator approves it, and lands only through a BACKLOG row (R26-120).


## Why

The compare verb (BACKLOG R26-70, E76 s4-s5) morphs the glyphs of one number into another's, and the melt's ball morphs into the
next chart (R26-117): the shapes have HOLES and their ring count changes (a "2" is one ring, an "8" three; a ball is one ring
becoming many). Today the plan pairs rings by a hand-written rule (surplus rings born from / dying into the nearest centroid) and
carries each pair with `kinetics/morph_a.mjs` (doc 43 s43.5 Method A: ring-normalise, resample by arc length, rotational
alignment, vertex lerp, cubic reconstruction) or `kinetics/arap.mjs` (Method B). The gooey threshold the melt already owns is a
blurred field cut at a level - an implicit surface. The question: is an IMPLICIT morph the right law for ink, and what does it cost?

## The questions

1. Variational implicit-surface shape transformation (Turk & O'Brien 1999, "Shape Transformation Using Variational Implicit
   Functions") and its descendants: the method, what it does at a topology change, its cost per frame - quote the primary.
2. Signed-distance-field blends for 2D shape morphing (SDF lerp, smooth-min/metaball unions, level-set interpolation): which give a
   mid-shape that reads as an in-between and not a dissolve; the known artefacts (ghost blobs, pinching) and their fixes.
3. Correspondence-based morphs with topology change: how the literature pairs rings and handles birth/death (Alexa/Cohen-Or ARAP
   variants, "Polymorph", Sederberg's physically based approach) - and where each breaks.
4. In a BROWSER at 12 fps on a canvas or an SVG filter chain: what is feasible per frame for a 200 x 60 px glyph run and for a
   400 px ball -> chart - SDF on a raster (a distance transform per state, cached, then a per-frame lerp + threshold + the gooey
   filter) versus polygon rings; numbers if any exist, else the algorithmic cost.
5. Hand-drawn RE-DRAW after a transform: stroke ordering and path generation for writing a number or drawing a chart "by the hand"
   from a shape (skeletonisation / medial axis to a stroke order) - what is standard, and what reads as a hand.

## Form (the intake's proof discipline - `docs/content-video-engine/HYPERFRAMES-INTAKE-2026-09-06.md` s1)

Every statement tagged `[source on file | practitioner doctrine | DERIVED | UNVERIFIED]`; every figure with a proof line
`[Metric | value | authority | URL | Verified 2026-09-14]` quoting the page it is on; the numbers in ONE table at the top (question, cue,
number, source, tag); a NOT FOUND block naming the roots you searched; no design proposals - questions answered, sources on disk under
`docs/research/runs/implicit_morph/`. Tiers: CONFIRMED (primary fetched and quoted) / PLAUSIBLE (secondary) / UNSOURCED-editorial / REJECTED.
