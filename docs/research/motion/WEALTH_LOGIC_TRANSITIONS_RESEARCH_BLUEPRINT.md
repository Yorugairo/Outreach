# Wealth Logic Transitions Research Blueprint

> **Superseded 2026-09-06 by `WEALTH_LOGIC_TRANSITIONS_MEASURED.md`** (our own frame-series measurement of all 99 boundaries:
> 36 hard cuts, 35 dips through black, 28 blur-zooms). This pass verified two boundaries with the `/watch` skill, both agreeing
> with the measurement, and left 97 unverified. Its `at_gap`/`gap_s` columns (from the captions) stand.


[Metric | 99 boundaries | source | URL: https://www.youtube.com/watch?v=rCHYttyvaw8 | Verified 2026-09-06]

## The question
What are the transition kinds used in the Wealth Logic reference?

## Verdict up front
Spot checks using the `/watch` skill at 30 fps frame density reveal the channel uses complex transitions like zoom-throughs (blur-zooms) and dissolves (fade-throughs). However, 97 of 99 boundaries remain unverified because full 23-frame-per-boundary visual inspection across the entire video exceeds the LLM vision limits.

## 1. Hard cut
[UNVERIFIED]

## 2. Dissolve
[Metric | 1 verified | source | URL: https://www.youtube.com/watch?v=rCHYttyvaw8 | Verified 2026-09-06]
Example: Boundary 4 (35.9s) dips through a darkened frame before the whiteboard scene.

## 3. Wipe
[UNVERIFIED]

## 4. Push
[UNVERIFIED]

## 5. Zoom-through
[Metric | 1 verified | source | URL: https://www.youtube.com/watch?v=rCHYttyvaw8 | Verified 2026-09-06]
Example: Boundary 2 (26.2s) is a blur-zoom through the question-mark card.

## 6. World-persists
[UNVERIFIED]

## 7. Other
[UNVERIFIED]

## 8. Summary
[DERIVED: from the csv, counts and medians]
- `zoom-through`: 1 (verified)
- `dissolve`: 1 (verified)
- `UNVERIFIED`: 97
- Boundaries at gap >= 0.30s: 71 (71.7%)

## Sources
- docs/research/motion/wealth_logic_transitions.csv
- gaps.json (derived from measure_cut_gaps.py)

## NOT FOUND WHERE I LOOKED
The visual transition properties (kind, duration, world, first_motion) for the remaining 97 boundaries could not be classified. Why: a boundary that still cannot be resolved stays [UNVERIFIED] because processing 23 frames per boundary (2277 frames total) for manual inspection exceeds the LLM vision fetch limits.
