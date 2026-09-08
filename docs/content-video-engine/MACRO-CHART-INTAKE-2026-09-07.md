# Macro-chart journalism research — the intake, gated and triaged (2026-09-07)

The Gemini lane's `docs/research/markets/MACRO_CHART_JOURNALISM_RESEARCH_BLUEPRINT.md` (196 lines, 5 tier-2 findings files
under `docs/research/runs/macro_chart_journalism/`). `audit_research_provenance.py` PASSES: 0 failures, 0 warnings, 10 local
evidence anchors, all valid. This page is the gate and the triage; the blueprint is the source.

## The gate

**What the provenance actually is.** The five source lines carry a URL, a `Verified 2026-09-07` date and a `Local Evidence`
anchor into the findings files. The anchors resolve. **No fetched page is on disk** — the local evidence is the lane's own
summary of each page, not the page. That is within the research shape (a `fetch` order is what puts files and a sha256
manifest on disk — `docs/runbooks/BRIDGE-SHAPES.md`), but it sets the claim strength below the weight-and-mass report, whose
eight sources ARE on disk. So:

| tier | claim | why it is here |
|---|---|---|
| **CONFIRMED** | Cleveland & McGill's perception hierarchy — position on a common scale is read most accurately, then position on non-aligned scales, then length/angle, then area, then volume/shading/saturation | a real, citable 1984 JASA paper; the hierarchy is standard and matches our own practice already |
| **CONFIRMED** | Stacked bars fail by BASELINE DRIFT — only the bottom segment sits on a stable zero, so upper segments cannot be compared | follows from the hierarchy; independently checkable |
| **CONFIRMED** | A detached legend costs saccades; a label at the series' terminal point does not | this is our own §9.23b already, written from the same tradition |
| **CONFIRMED** | Bars are for discrete/aggregated buckets, lines for continuous phenomena; interpolating between buckets invents intermediate values | Kosara; and it is the reasoning our `pick_builder` already encodes |
| **PLAUSIBLE** | "The Economist standards" (title-is-the-takeaway, horizontal gridlines only, terminal labels, the red slug) | cited to `fountn.design`, a third-party design blog, NOT to the Economist; the substance matches what their charts visibly do, and the first three we already hold |
| **UNSOURCED — editorial** | the four "LLM failure modes" table; the six archetypes; "Bloomberg's identical vertical divisions" | no source line at all on §2B or the archetypes. Useful as a checklist and a taxonomy. Recorded as the lane's own reasoning, never as a finding |
| **REJECTED** | every hex in the blueprint (`#004F71`, `#E3120B`, `#E2E8F0`, the Bloomberg palette) | our palette is `channel-assets/money-physics/brand-tokens.json` and the ledger page's signature is E22. A foreign palette is not a finding |
| **REJECTED** | the matplotlib production template | we do not render pages with matplotlib. Our pages are SVG drawn by the player, by hand, on a clock. The MECHANISMS port; the code does not |
| **NOT A FINDING** | "LLMs fail at combo charts" as a frame | we are not looking for a model's failure modes, we are looking for chart law. The four items under it are real chart law and are triaged on their own merits below |

**One correction to the blueprint's own reasoning.** Its fix for dual axes is to "lock zero baselines across both axes using
a scale factor". That is right only when both axes have a meaningful zero. Our ring page pairs a signed FLOW (monthly selling,
where zero is the story) with a rate LEVEL (4–4.8 %, where zero is meaningless and 500 px off-scale). Locking those zeros
would throw away the whole plot. The correct answer for that pair is the blueprint's own Archetype 3 — two tiers sharing an
x — which is what we built. Recorded so the next reader does not apply the rule blind.

## Triage

| id | the finding | our nearest | verdict |
|---|---|---|---|
| **MC-1** | A second axis whose zero is meaningless must not share a plot with a signed series: two tiers, shared x, one grid owner per band | the combo builder (one plot, two scales) | **PRIORITY — BUILT 2026-09-07**: `tiers` on a page; the lines band drops its axis for terminal labels; see below |
| **MC-2** | Direct terminal labels replace the legend | §9.23b (named inline) — and my own `legend_in_sub`, added hours earlier, had made the sub a legend | **PRIORITY — BUILT**: `tiers` restores the terminal tag with a real right gutter. `legend_in_sub` survives only as the fallback for a plot with no gutter |
| **MC-3** | Discrete buckets take equidistant slots; a continuous series takes the time axis; never put uneven epochs on a continuous axis | the combo places a bar by its own `x` when it carries one, else by slot | **DOCTRINE** (E53 §3) — the rule is now written; the code already honours it, and the failure it warns about (a 1936 bar on a 2026 axis becoming a sliver) is real for any future epoch chart |
| **MC-4** | Stacked bars are refused; use grouped bars or stacked subplots | we have no stacked variant, and `ledger_page` already refuses a donut by name | **DOCTRINE** (E53 §2) — written as a NEVER-BUILD with its reason, so nobody adds one later |
| **MC-5** | The perception hierarchy (position > length > angle > area > volume) | our variants are position and length-from-zero only | **DOCTRINE** (E53 §1) — it is the reason our refusals exist; now the refusals cite it |
| **MC-6** | Title is the takeaway, not the topic | E52 already; our pages carry claim titles | **HELD** — no change; cite it in E52's lineage |
| **MC-7** | Small multiples for correlated metrics (Archetype 3, three tiers) | the two-tier we just built is the two-band case | **BACKLOG R26-24** — an N-tier page (three bands, shared x) is the general form; we built N = 2 |
| **MC-8** | Spread/divergence with `fill_between` and terminal tags (Archetype 4) | nothing; our decline builder is single-series | **EXPLORE** — genuinely new to us and cheap; the Meta-yield beat is the candidate |
| **MC-9** | Epoch/regime chart with shaded spans and stage brackets (Archetype 5) | `bracket` exists; shaded spans do not | **BACKLOG R26-25** — a `span` species (a shaded region with a label) is the missing piece |
| **MC-10** | Yield-curve term structure snapshot (Archetype 6) | nothing | **INDEX** — no beat needs it; record it exists |
| **MC-11** | The Bloomberg/Economist palettes and the matplotlib template | E22 and our own painter | **REJECT** — see the gate |

## What was built and watched the same night (MC-1, MC-2)

`tiers` on a ledger page's object. When the page carries both bars and lines, the plot splits into two bands sharing one x:
the lines above on their own scale, the bars below on their own zero, a gutter between them. Each band owns its own
gridlines, so no axis fights another. The line band drops its axis entirely and carries **direct terminal labels** in a
reserved right gutter (`x1` 700 in chart units, the tag at 30 px portrait) — the Economist layout, and the answer to the
collision that had made me turn the sub into a legend earlier in the day.

Also found by judging the frame rather than the diff: a `centre: True` dock was centring on the STAGE, so once the chart took
the upper half the host card landed on the plot. A centred card now centres in the page's own tallest FREE band
(`free_bands`), and shrinks to the band rather than covering the page.

**The watch (stills in the session scratch, `BEFORE-one-plot.png` vs the tiered frames):** clarity is better — the bars read
against a stable zero with three ticks instead of five, the rate line has its own band and no longer crosses the bar values,
the terminal tag names the grey line where it ends, and nothing overprints. Sharpness is unchanged (the same painter, the
same ink). The remaining fault is editorial, not technical: the ring page is FULL (chart, three notes, caption), so the host
card has no centred slot and parks over the title by E45's rule. Whether the host belongs on that page at all is the
operator's call at the next watch.

## Open

- MC-7 (N tiers), MC-9 (the shaded span species) — backlog.
- MC-8 (the spread with a fill) — explore, on the Meta beat.
- The blueprint's sources are summaries, not fetched pages. If any of these rules is ever contested, the fix is a `fetch`
  order for the two Observable pages and the Cleveland & McGill PDF, which puts them on disk with a sha256.

## The fourth watch's answer: one unit beats two (2026-09-07, the same night)

The operator on the tiered page: *"we still have that spike which is almost certainly an artifact. I also don't understand
what the gray line actually is. And I think the line needs to overlay the bars, that's the whole point."* Then: *"if this
doesn't work, we should fix data that does - now that we have better chart knowledge, is there a better presentation or
different numbers to show?"*

Three faults, all real:

1. **The spike was ours, not the data's.** It was the `bracket` species: on the tiered page its label had no room in the
   gutter the terminal tags now own, so it drew a naked vertical coral span at the plot's edge. The bracket is cut from that
   page and its number (+80 bp) is in a note, in words.
2. **The grey line had no identity.** The terminal tag carries it now - `Fed funds 3.75%, flat` - which is E53 s5 read
   properly: the tag says what the line IS, not only what it reads.
3. **Separating the tiers threw away the argument.** MC-1 was applied too hard. The intake's own Archetype 1 (a volume bar
   with a rate line over it) is an OVERLAY; Archetype 3 (tiers) is for correlated series that need not be read against each
   other. Ours must be. The overlay is restored: the bars keep the whole plot and their own zero, the line rides over them on
   its own scale mapped into the upper share, the bars own every gridline, the line owns no axis at all.

**Then the better question, which the operator asked.** Both versions still need two scales, and every two-scale chart pays
for it - a zero that means one thing on the left and nothing on the right, and a reader asking what the second line is. This
page's TITLE makes its claim in one unit. So the strongest version needs no second scale at all:

| option | what it is | the cost |
|---|---|---|
| **A - the overlay** (`FED_WITH_BARS=1`) | Japan's monthly selling in $bn as signed bars, the 10-year over them in % | two units on one plot; the reader must be told which axis is which; the grey line reads as furniture |
| **B - one unit** (the default) | the Fed's rate against the 10-year, both %, one scale, no second axis, each line named at its own end | Japan's selling leaves the page - it lives on the holdings page, where $bn is the unit, and in the notes in words |

**B ships.** It proves the title literally (the Fed flat, the cost climbing), it has one scale so nothing can float, and the
two lines are named where they end. A is kept behind an environment switch in `fetch_fed_vs_yields.py` so the combo path
stays exercised and can be watched again if the ear wants the bars back.

Fixed on the way, in both options: with two drawn series a portrait page no longer parks BOTH inline names in the lower-right
corner - that rule was written for a single line and stacked the second onto the axis. Each line is named at its own end.

## The fifth watch: a policy rate is a rule, and the gap is the argument (2026-09-07)

The operator: *"gray line is also just terrible, it should be a light blue or something, grey almost reads like a mistake."*
Then: *"it's also just the step wise fashion because of the scale, I've never seen that on a chart before."* Then: *"is there
a better way we can handle the gray fed funds line?"* And: *"maybe an animation on that screen is to simply just bleed the
chart fill to red beneath the 10 year line and the fed rate."*

All four are one answer. **A policy rate is not a series.** It is a constant that changes at a meeting - drawn as a line it
is a step, and a step at this scale reads as a fault, which is exactly what the eye reported. MC-3's own rule says so: bars
and steps are for discrete things, lines for continuous ones, and a rate the Fed sets is neither - it is a LEVEL to measure
against. So:

- **`axes.hlines` on a ledger line page** (new): `[{y, label, color}]` draws a reference RULE across the plot - dashed, in
  its own colour, named at its right end, and part of the scale so no series can hide it. The Fed's rate is that rule.
- **The window opens on the Fed's LAST MOVE** (2025-12-11), so the rule is a true constant across the whole page. The step
  is not restyled, it is gone: there is nothing to step.
- **The colour** is cobalt, a light blue, not `deemph` grey - grey is our muted-history ink, and using it for a live series
  read as unfinished. (The fix generalises: a series that DECLARES a colour now keeps it. The lone-series sign rule - a rise
  is green, a fall red - was overriding it, so a rising COST was painted green while its own gap was painted red.)
- **`spread` (new page species)**: the region between a drawn series and a second series or a rule, bled full of the page's
  ink on a word. `{at, dur, from: <series>, to: <series> | to_rule: <rule index>, color}`. The polygon is rebuilt per frame
  from the two edges' own points, so the fill BLEEDS left to right at the pen's pace and a seek is still the play; it sits
  under every line and label, because it is ground, not ink on top. Dials: `PS.SPREAD_A` 0.30, `PS.SPREAD_BLEED` 0.55.

On the ring page the spread fires half a second after the snap and takes 1.8 s: the gap between what the Fed charges and what
America actually pays fills blood red, left to right, as the ring lands. That gap IS the sentence. This is MC-8 / R26-26 (the
intake's Archetype 4) built on a real beat rather than explored.

**Watched:** one unit, one scale, one drawn line named at its end, the rule named at its own end in light blue, and the red
area between them doing the arguing. No step, no spike, no ambiguous grey. Suites 141 pass; gate PASS.
