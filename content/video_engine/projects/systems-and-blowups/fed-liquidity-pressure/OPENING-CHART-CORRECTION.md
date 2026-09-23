# Opening chart correction — operator review

Status: actual histories verified and two silent candidates compiled. Parent phone renders reject current text/layout; T17 engine correction is in progress. The old18-second diagnostic remains unchanged and rejected as the production treatment. Current script is being rewritten; all existing candidate clocks are geometry-only, not narrated alignment.

## Recall

- Recall: docs/content-video-engine/39-EVIDENCE-CHART-SYSTEM.md, sections 0, 3, 6-8: direct labels, two lines for two subjects, no dual axes, source/window chrome, actual data before rendering.
- Recall: docs/content-video-engine/50-THE-PHONE-IS-THE-SCREEN.md, sections 50.2 and 50.5: measure the final display at 390px width; 59px on a 1920px stage is the derived 12px phone reference, not proof of readability by itself.
- Recall: docs/portable/OPERATOR-RULINGS.md, E99 s82: full-stage chart; complete line then label/badge then next line; no unexplained partial crawl; no scale correction that moves values after drawing.
- Recall: docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md, section 9.33: chart-to recast is the same data in a new form, not an unexplained substitution of a different metric.
- Recall: effects_card.py chart_to:recast reports wired; effects_card.py melt reports callable but draft/look review required. Mechanical availability does not confer operator approval.

## Correction and acceptance

1. Replace the endpoint-only opening with two comparable historical lines. Preferred opening encoding: cumulative USD-trillion change since 01 Jun 2022 on one shared axis, through 11 Jun 2025; formula is observation minus its own first observation, with unit conversion recorded. This preserves the opening's net-change claim without dual axes or an indexed-percent implication. Requires matching official observation conventions and verified actual histories before implementation.
2. Explicit axis titles: `Date` and `Change since Jun 2022 ($ trillions)`; sparse readable year ticks, signed numeric y ticks and clear zero reference. Direct-label both entities and actual final changes. Dates, units, source and derivation remain visible. Source-footnote overflow is a failure, not a reason to remove units.
3. Full-stage plot, anchored bottom caption band. Essential text measured at the 390px phone display, using doc 50's 12px reference and an actual visual read. No shrinking to an arbitrary side column.
4. Draw assets completely, land its label/value, then reserves completely and its label/value. Timing comes from the measured opening words; if this cannot fit, simplify the choreography instead of accelerating it beyond readability or extending the take artificially.
5. Built naming: Candidate A keeps the historical lines; candidate B recasts the same derived changes into signed bars. Both still owe readable direct endpoint values. The T17 opt-in is first integrated into A; B cannot inherit unverified line-to-bar geometry. Render cheap short comparisons before choosing; a two-entity race has no useful rank-change story here.
6. ON RRP is a different account and a different date window: do NOT morph reserves into an ON RRP line as if they were identical observations. Prefer a short ink gather/melt and rebuild on the same board, with outgoing marks clearing and incoming metric, dates and scale explicitly rewriting. No slide cut, empty cream reset, inherited axis labels, or claim that ink continuity proves account-to-account causality. Prove the draft melt in motion before inclusion.
7. Freeze a new version for review; preserve old diagnostic and source files. Validate exact observations/derivation, no tick duplication, label collisions, source/date visibility, numeric stability and before/mid/after transition frames. Do not call this fixed until frames and measured geometry pass.

## Dependency

Source dependency resolved:159matched Wednesday observations per series,2022-06-01 through2025-06-11, WALCL/WRBWFRBL. `build_opening_history.py` verifies the retained sources and emits `evidence/objects/fed-assets-reserves-history.series.json`; exact deltas are−2237.895B/+72.280B. ON RRP remains a separately sourced daily history through2026-09-18. Render windows and metric names explicitly at their handoff; they are not one matched date range. Never substitute an interpolated curve.
