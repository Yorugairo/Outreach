---
id: P73-THE-AMD-RFSOC-EPISODE-GAPS
title: The AMD RFSoC episode's gaps - the mechanisms the next Money Physics long form needs that the engine did not have
status: running
operation: feature
risk: standard
owner: parent
branch: claude/fable-p68 (the plan, the research, the bookkeeping); every build slice lands on claude/p69-s90 (lane B)
contract: tdd-v1
created: 2026-09-26
updated: 2026-09-26 (the parent; built under the operator's order of 2026-09-26 - "determine what effects/recipes might be most beneficial for this story and then build those and stabilize main so we can roll out an episode work tree"; T1-T4 landed on lane B, T5 queued)
---

# P73 - The AMD RFSoC episode's gaps

## Summary

The operator (2026-09-26) chose the next Money Physics video: SemiAnalysis's Dylan Patel said "AMD needs to be
investigated for treason" (X, 2026-09-19) after an export-controlled Zynq UltraScale+ RFSoC (XCZU47DR) turned up on a
Chinese crowdfunded SDR board (Puzhi PZSDR P047, on Mouser-owned Crowd Supply). Title: "AMD's Cover-up Is Not Just
Money (Tried for Treason)"; the approved opening and the story's shape are in the operator's own words in memory
(`amd-episode-title-ruling`). The order: find a stable point with the day's fixes landed, determine the effects and
recipes this story needs, BUILD those, stabilize main, roll out an episode worktree.

The evidence: the research packs `docs/research/markets/amd-rfsoc-2026-09/RESEARCH.md` (0cd2524) and `RESEARCH-2.md`
(d529fb9), and the capability map `CAPABILITY-MAP.md` there (every beat mapped to CAPABILITIES rows; the gaps ranked).
Every beat already had a working mechanism; the gaps were the ones this story leans on hardest. The plate schedule (96
narrative scene options for ~12:00, the operator's floor "at least 1 narrative scene per 10 seconds") is the
episode's, not this plan's: `$SP/amd-rfsoc/PLATES.md` (AMD cobalt, Nvidia teal - the operator's "yes", 2026-09-26).

The common brief every slice ran under: `$SP/p73-brief-common.md` (the story's truth rules, the rulings, the lane-B
workflow, the RETURN). The slice orders: `$SP/p73-slices.md`.

## Slices

### T1: A claimed figure on a chart
- Status: done - lane B `2e92f04`: a bars datum's `claim: {by, said, evidence, src, standing?, quote?}` draws as the
  speaker's figure (an outline, his quote, "Dylan Patel, SemiAnalysis" over it); `claim_audit` off by default (the
  operator: his standing is the point); a claim never feeds a computed label unless the label is his. Goldens
  `claim-bar`, `claim-bar@proof-word`; `tests/test_claim_figure.py` (46). Human gate: P73-HG1 (1).

### T2: The dated event timeline page
- Status: done - lane B `4caa568`: `ledger:<id>:timeline` - dated events on one date axis with no series, empty years
  cut (`// 7 yrs`), each event landing on its word, a moved date struck and run to the new one, 16:9 and 9:16. Goldens
  `event-timeline`, `event-timeline-9x16` + two proofs; `tests/test_event_timeline.py` (47). Human gate: P73-HG1 (2).

### T3: The post card
- Status: done - lane B `9c2b39c` (goldens 243/243 with T1-T4): a press card's `style: "post"` header (name, @handle, UTC time, dated
  counts; no platform mark). Golden `press-post` + `@proof-reply`; `tests/test_press_post.py` (45). Human gate:
  P73-HG1 (3).

### T4: The supply-chain icons
- Status: done - lane B `b0eaa7a`: 16 sourced Lucide glyphs (ISC); golden `flow-supply-route`;
  `tests/test_icons_intake.py` (24). Human gate: P73-HG1 (4).

### T5: Hong Kong and Singapore on the map
- Status: done - lane B (the T5 commit): map POINTS (`{kind: place, id}`: HKG, SGP, MAC, HSINCHU from Natural Earth 1:10m, the map's own commit) light, ping and end arcs; goldens `vecmap-transship`, `vecmap-place-singapore` + proofs; `tests/test_map_places.py` (23). Human gate: P73-HG1 (5). The Atlantic route is R26-406 (T6).

### T6: A Pacific-centred map (R26-406)
- Status: done - lane B (the T6 commit): `;meridian=<deg>` re-centres the vector map (one formula for the paths, centroids, places and mappoints), splits the countries the new seam cuts, joins Natural Earth's 180 cut (Russia, Fiji, Antarctica); an arc the long way round WARNs with the meridian that fixes it; default byte-identical. Goldens `vecmap-pacific`, `vecmap-seam-split`; `tests/test_pacific_map.py` (31). P73-HG1 (6).

## Human gates

| Gate | What to judge, and where |
|---|---|
| **P73-HG1** | (1) the claimed figure: the outline (default) or the hatch; the name-over-figure's weight; the audit wording (`scratchpad/p73-t1/frames/SHEET-claim-bar.png`). (2) the timeline: at 16:9 the full-stage chart box uses ~0.69 of the width (the right third empty) - widen it when no dock stands?; the hollow pin + "reported"; teal as the lit ink; the axis-run for a moved date (`scratchpad/p73-t2/frames/sheet-16x9.png`, `sheet-9x16.png`). (3) the post card: AMD's reply as a second press card in the pile (built) or the hand-off (the post leaves, the record types); the header's size at 16:9; sans or serif (`scratchpad/p73-t3/frames/contact-sheet.png`). (4) the route: six nodes is the flow's cap (a phone-legibility rule) - merge two stops (built) or split a seven-stop route into two rows? (5) the map points: the dot 9 px, glow 10 px, label 30 px Inter 600, the side order right / below / left / above - all unmeasured dials; the ping ring crosses a label placed below for ~0.67 s (`scratchpad/p73-t5/frames/SHEET.png`). (6) the Pacific map: the cut edges stroke short lines on the frame's edges (Antarctica reads as a box - the Greenwich map already does at 180); Hong Kong's name below the dot on the Pacific beat (the auto side put it on the arriving route) (`scratchpad/p73-t6/frames/SHEET.png`). |

## Validation

Each slice: its own test file green, its neighbours' counts equal base, `test_golden_frames` green with only its own
new goldens, the H door identical apart from the engine hash. The episode worktree is rolled out from main after the
full suite (`run_full_suite.py`, P72 T51c) is green on the merged lanes.
