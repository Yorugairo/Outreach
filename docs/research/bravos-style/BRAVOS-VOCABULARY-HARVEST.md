# Bravos Research: chart vocabulary harvest, mapped against our catalogue (explorer, 2026-09-23)

This file covers what Bravos DOES with charts over time and which chart forms it uses. The static style numbers (colours, px, fonts) are in `measurements.json` beside this file. This file does not repeat them.

## Sources read

- **Bubbles**: *The Bubble's Final Phase Has Begun*, `content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/`. I read all 30 contact sheets (89 tiles), `SHOT_LEDGER.md`, `REPORT.md` and `transcript.json`.
  - **Warning: Bubbles times are coarse.** The ledger is Gemini's fixed 12 s sampler, so every "#n" time is a 12 s window, not an event. Per-build timings for Bubbles do not exist yet (see §8).
- **China**: *China Just Triggered A New World Order*, `.../bravos-china-just-triggered-a-new-world-order/`. I read all 10 `claude-watch/shots/sheet_*.png` (120 event frames), `SHOT_LEDGER.claude.md` (difference-detector events, so its times ARE builds), `REPORT.claude.md`, `GEMINI-CONVO-2026-09-10.md` and `claude-watch/transcript.json`.
- **Reset**: a third Bravos watch the brief did not name. It is *A Once in a Lifetime Financial Reset*, `.../pivot-_rwFYNlKtEc/` (a Codex watch, 2026-09-20, `docs/research/MP-TOPIC-PIVOT-REVIEW-2026-09-20.md`). Only 23 frames exist. I read the 5 overview sheets and the 3 targeted sheets. Items taken from it are tagged "Reset t=…".
- **Prior harvests**:
  - `docs/research/runs/macro_chart_journalism/findings_bravos.md`
  - `docs/research/runs/grill_pipeline-value/BRAVOS-RIG-VERIFIED.md` (Gemini's 09-13 paste, corrected at 2 fps)
  - `docs/research/runs/grill_pipeline-value/recipes_r1.md`
  - `docs/research/tech/TREEMAP_READABILITY_RESEARCH_BLUEPRINT.md`
  - `docs/research/markets/MACRO_CHART_JOURNALISM_RESEARCH_BLUEPRINT.md`
- **Our catalogue (fable-p68 worktree)**:
  - `content/video_engine/effects/cards/*.json`: 18 axes. Every token was read with its `does` line.
  - `effects/recipes/*.json`: 46 recipes.
  - `scripts/species/*.mjs`: 24 species.
  - `docs/content-video-engine/CAPABILITIES.md`, `docs/portable/OPERATOR-RULINGS.md`.
  - `scripts/ledger_page.py` `AXES_KEYS`, and `docs/content-video-engine/samples/scene-evidence-engine.mjs` (hlines / marks / eventbars / dashed series).
- **Recall caveat**: `docs_find.py` reported every generated layer STALE ("no refresh running"). So I checked every MISSING claim against the card JSONs and the engine or `ledger_page.py` source directly, not only against docs_find. Where I write "0 hits", that is docs_find plus a grep of the cards.

Status key:
- **HAVE**: the named card, recipe or species exists.
- **PARTIAL**: the thing that is missing is named.
- **MISSING**: absent from the roots above.
- **Gemini** marks an idea Gemini raised first:
  - "Gemini 09-10": `GEMINI-CONVO-2026-09-10.md`
  - "Gemini-B": Gemini's own Bubbles `REPORT.md` techniques
  - "Gemini 09-13": the rig paste, corrected in `BRAVOS-RIG-VERIFIED.md`

---

## 1. TYPE: chart forms (28 items: 16 HAVE, 4 PARTIAL, 8 MISSING)

| id | form | where | what it serves (transcript) | timing | OURS |
|---|---|---|---|---|---|
| T1 | **Partitioned pyramid ("iceberg")**. A triangle cut into Voronoi-like cells, each cell a company and $ figure. A WATERLINE splits the surface debt (grey) from the hidden base (pink). The base's biggest block takes a glow outline and a leader to "Purchase Commitments $1.52 trillion". A logo legend follows. | Bubbles #1-4, 0:00-0:48 | "This entire section represents AI related purchases and leases that these same big tech companies have already committed to." | 4 windows, ~12 s each: tip, then labels, then base, then legend | **MISSING**. docs_find 0 hits "waterline". "iceberg" hits only Gemini-B T1. `page_builder:tiers` is small multiples, not this. Gemini-B credited. |
| T2 | **Axis-less story bars**: a category pill over each bar and a glowing value badge on top. | Bubbles #5-8, 0:48-1:36 | "at the peak of the dotcom bubble … roughly $300 billion … 2008 … roughly $1.3 trillion" | one bar per claim, each on its window | **HAVE**. `page_builder:bars` (values land with the bars) plus the badge (`recipe:emphasized-bar-lit`). The pill-above-the-bar look is style only (S5). |
| T3 | **Composition bar**: the $3T bar filled with member logo tiles, a dashed bracket around it. | Bubbles #8, 1:24-1:36 | "Today, the total amount of AI related debt from just these few companies…" | tiles appear inside the standing bar | **MISSING**. It also conflicts with E53 §2 (C3). |
| T4 | **Divergence pair**: two framed mini-charts under category pills ("Stock Market", "Credit Market"). | Bubbles #10, 1:48 | "while the stock market might look calm … the credit market … is beginning to show cracks" | both in one window | **HAVE**. `chart_dock:panels`. |
| T5 | **Framed single line with a ceiling rule** (Oracle CDS, bp). | Bubbles #13-15, 2:24-3:00 | "surged to the highest level since 2009" | full hold ~36 s | **HAVE**. `page_builder:line` plus `axes.hlines`. |
| T6 | **Neon multi-line** (5-6 series, legend in a band at the top of the frame). | Bubbles #16-17, #75; China 99-104 | "This includes Alphabet, Amazon, Meta, Microsoft, and even Nvidia" / "Germany, the UK, Japan … yields moving higher" | China: draw from 16:45.5, tags from 16:59.8 (+14.3 s) | **HAVE**. Line page with E67 electric inks, the R26-228 bloom pulse and R26-226 line-by-line. The legend band is refused by E53 §3 (label at the line's end). |
| T7 | **Phase-shifted schematic waves**: "Credit Investors" leads "Stocks", then "Economy" is added. The future is drawn dashed, and a short bar measures the lag between the peaks. | Bubbles #24, #26, #29, 4:35-5:47 | "stock market investors are slower to react … long after the lenders have quietly started heading for the exits" | a wave per window; the third wave arrives ~1 min later | **MISSING**. 0 hits "sine" / "phase shift" outside Gemini-B T2. Gemini-B credited. |
| T8 | **Candlesticks** over a ghosted wave, with a dashed ring on the last candle. | Bubbles #25, 4:47 | "The stock can theoretically go up and up and up" | one window | **MISSING**. Only `prop-icon-candlestick-price-action-v1.png` exists. |
| T9 | **Schematic zig-zag with a ring and "+40%" at each vertex**, and a red dot at the low. | Bubbles #28, 5:23 | "A 40% return per year every year for the past 5 years" | 5 rings in one window | **PARTIAL**. Line page, `species:ring` and `page_species:figure` exist. A per-vertex ladder on a chart is not a recipe (`trace-callout-ladder` works on stills). See C7 and C9. |
| T10 | **Donut "Portfolio"** (no data, decorative). | Bubbles #19; China 43-44 (sponsor) | "unsure for what that means for your portfolio" | 1.5 s | **PARTIAL**. `page_builder:share` (one named slice) exists. `shares` (a donut) is refused. See C10. |
| T11 | **Line with shaded recession bands**. | Bubbles #37-43, #70-75 | "the exact same sequence played out during the dot-com bubble" | bands stand from the first frame | **HAVE**. `page_species:span`. |
| T12 | **Annual columns** with a dashed max rule and a dashed ring on the last bar top. | Bubbles #34, 6:47 | "Home building companies also started to accumulate more and more debt" | one window | **HAVE**. `page_builder:bars` + `axes.hlines` + `species:ring`. |
| T13 | **Dense monthly columns**: the last bar glows, with a value capsule in a dashed ring. Then a rescale to the new max. | Bubbles #65-67, 13:10-14:09 | "has gone from virtually zero in 2023 to 2.2% today" | 2.2% capsule, then the axis grows to 18% | **HAVE**. `recipe:emphasized-bar-lit`, `ring`, `chart_to:rescale`. |
| T14 | **Dual-axis line over line** (S&P LHS + Fed funds RHS; CDS + Fed hike probability). Reset: debt/GDP on an INVERTED right axis, and interest/revenue against the 10y. | Bubbles #74, #78-79; Reset t=7:00, t=13:40 | "the Federal Reserve tightened monetary policy by raising interest rates" | the second series arrives ghosted, with one stretch lit | **MISSING**. No rhs / y2 / invert key in `ledger_page.py` `AXES_KEYS`. Conflicts with E53 §4-5 and E75 (C5). |
| T15 | **Small multiples** (Japan SPR and US SPR), the drop shown as a pink vertical bar. | China 35-36, 3:29.8-3:42 | "here's Japan SPR … Here's the United States. SPR." | panel 2 lands +7.2 s after panel 1 | **HAVE**. `page_builder:tiers` (`recipe:two-tiers-one-x`). |
| T16 | **Ranked horizontal race with a scale break**: China's "?" track, a burst to 1,405, a capsule on the axis, a dotted drop rule. | China 50-55, 7:42.8-9:20 | "China has around 1.4 billion barrels … more than the combined total of every other country's" | bars 7:42.8, burst 8:00 (+17 s), capsule 8:26 | **HAVE**. `page_builder:race`, `overflow:burst`, `overflow_capsule:"axis"`, `recipe:ranked-bars-race-then-burst`. Gemini 09-10 technique 4 is BUILT (E60). |
| T17 | **Treemap census**, the departing partners crossed out. | China 89-91, 14:52.5-15:31 | "if we cross out all of the countries whose economy would be severely impacted … lost almost half of its export market" | Xs +13 s after the census, park +3.3 s after that | **HAVE**. `page_builder:treemap` + `page_species:cross`. The treemap blueprint's numerals, culling, X and affine shrink are all covered. |
| T18 | **Horizontal current-value bars** (10y yields). | China 105-106, 18:01-18:09 | "the world's money is already moving towards China" | 9.7 s after the line-end value bars | **HAVE**. `page_builder:bars` / `chart_to:recast`. |
| T19 | **Vector map**: countries light, arcs (with X) are drawn, stamps. | China 57-80, 9:42-13:00 | "In 1996 … Clinton signed a law that cut off the world from buying Iranian oil" | stamp, cutout, light, stamp every ~2 s (9:42.0 / 9:44.5 / 9:46.8 / 9:48.8) | **HAVE**. `vecmap` (`species:light`, `arc`, `stamp`), `recipe:vector-map-named-lit-and-stamped`. |
| T20 | **Flow diagram**: a dashed box of icon chips joined by arrows, a year tag. | China 82-86; Bubbles #44-47 | "in 1973, Arab oil states discovered that controlling the supply of oil gave them enormous geopolitical leverage" | box, then nodes, then the swap 54 s later | **HAVE**. `species:flow`. |
| T21 | **Circular loop diagram**: 3-5 nodes on a ring, green arrows, cash glyphs riding the ring, figures ("$100 Billion", "$2 Trillion"). Reset: "Debt Doom Loop" with up and down chevrons per node. | Bubbles #56-58, 11:22-11:58; Reset t=9:30 | "there is essentially a financing loop sitting underneath this entire AI boom" | the arrows draw, the bills travel | **MISSING**. `flowLayout` is a row or column only (`species/flow.mjs:75`), and there are no tokens on edges. Gemini-B T4 credited. |
| T22 | **Filled area chart** (debt/GDP). | Reset t=11:00 | (Reset; not quoted) | – | **HAVE**. The live-chart area fill (CAPABILITIES:20); on the page, the `spread` / `morph` area. |
| T23 | **Projection chart**: actual, then forecast, with value pills at 2026 and 2030 and a ring at the crossover. | Reset t=17:20 | (Reset; not quoted) | – | **PARTIAL**. The chart card's `dash` series only FADES in (`scene-evidence-engine.mjs:6856`). A drawn solid-to-dashed continuation on a page does not exist. |
| T24 | **Decomposition brace**: "Long-Term Interest Rates" braces two stacked components (short-term rate + term premium), each a pill chain from its source (Fed / bond vigilantes). | Reset t=5:40 | (Reset; not quoted) | – | **MISSING**. `bracket` braces two data on a chart. `flow` does not brace nodes. |
| T25 | **Isometric count array** (oil silos) with a cutaway card beside it. | China 51, 53; 7:43.8-8:25 | "oil silos, which are essentially large secure metal towers" | the array lands, the card comes on the next cut | **HAVE**. `species:count_array`. Gemini 09-10 technique 2: the array is HAVE; its satellites are MISSING (F14); its camera track-left was not in the frames (REJECTED). |
| T26 | **Mini-chart verdict tiles**: a globe ✓ against a chart ✗; SELL ✗ and BUY & HOLD ✗ panels, each with an actor avatar. | Bubbles #69, #84-85, 14:22; 18:45-19:09 | "Don't try and sell all your stocks … don't expect that a simple buy and hold strategy is going to work" | the second panel follows ~12 s later | **PARTIAL**. `chart_dock:panels` + `species:chip` cross exist. A ✓ state and an actor-per-panel do not. |
| T27 | **Balance scale** (Threat against Opportunity) that tips. | China 113-114, 19:10.8-19:15.5 | "not just threats. They can be some of the greatest wealth creation opportunities" | tips inside 4 s | **MISSING** as a species. Only doc 49 research mentions it. |
| T28 | **Prediction board**: icon tiles struck out "6 Months Later". | China 26-28, 1:49.5-1:57.8 | "pretty much none of these predictions have actually played out" | strikes 3-4 s apart | **HAVE**. `species:chip` (cross + DIM). |

## 2. ACTION: verbs on a chart (40 items: 21 HAVE, 9 PARTIAL, 10 MISSING)

| id | action | where | sentence | timing | OURS |
|---|---|---|---|---|---|
| A1 | The empty axes frame arrives, then the line draws. | China 37-38 | "a combined 32 countries agreed to release…" | frame first, then the draw | **HAVE**. `page_enter:axes`, `recipe:hook-opens-on-the-axes`. |
| A2 | Series added ONE at a time, the legend growing. | China 29-30; Bubbles #49-50 | "total world oil production … Meanwhile, total oil consumption" | production at 1:57.8, consumption at 2:31.2 (+33.4 s) | **HAVE**. R26-226 line-by-line; `chart_to:extend`. |
| A3 | Terminal tags (pills with a dot and a leader) at the line ends. | China 100-104; Bubbles #50 "$74 billion" | "Anthropic's revenue went from $1 billion to $74 billion" | +14.3 s after the draw starts | **HAVE**. E53 end label; `tippill` terminal. |
| A4 | A pill that rides the drawing tip. | China 99-100 (Gemini 09-10 technique 5) | – | locked to the tip | **HAVE**. `plate_option:pill`, `recipe:pill-rides-the-line` (R26-34 closed). |
| A5 | Line-end values grow into bars beside the plot, then become a bar chart. | China 104-105; Bubbles #53 | "China now has a lower 10-year government bond yield than the US, the UK, Japan, and Germany" | bars at 17:51.5 / 17:57, chart at 18:01.2 | **HAVE**. `chart_to:recast` keyed; CAPABILITIES:110 "Line-end TAGS become the next chart's BARS". |
| A6 | Scale break: the bar shoots, the domain rewrites. | China 52-54 | "1.4 billion barrels" | ~1.4 s shoot (8:01.8-8:03.2) | **HAVE**. `overflow:burst`. |
| A7 | A dashed ellipse on the datum plus a flag chip. | China 41, 5:58; Bubbles #78 | "stopped importing oil by the single largest amount that any country has ever done" | 42.4 s after the lit stretch | **HAVE**. `species:ring` `form:"dashed"`. |
| A8 | A small dashed ring on a point plus a value capsule with a leader. | Bubbles #15, #63 "6%", #65 "2.2%" | "went from 2% in 2018 to 6% today" | inside the window | **HAVE**. `ring` + `callout` / `figure`. |
| A9 | A dashed LEVEL rule drawn from one datum to another (the GFC peak to today, a ring at each end). | Bubbles #15, 2:48; Reset t=7:00 (1985 peak to now) | "more worried about Oracle defaulting than they were at the very depth of the global financial crisis" | the rule, then the two rings | **PARTIAL**. `axes.hlines` is a static full-width rule, and a ring exists. A rule drawn from datum A to datum B does not. |
| A10 | X-axis tick PILL: the named year or era replaces its tick in accent ("2009", "Late 1990s", "2000s", "April 1942", "2026", "2030"). | Bubbles #14-15, #70; China 39; Reset t=11:00, 17:20 | "Investors in internet companies in the late 1990s…" | on the word | **MISSING**. 0 hits "category pill" / "tick highlight" as a verb; no axes key for it. |
| A11 | A STRETCH of the line relights on the word while the rest mutes (several stretches in turn). | Bubbles #39-41, #70, #72; China 40, 5:15.8 | "China had been aggressively ramping up its oil imports" | China: lit stretch 43 s after the draw | **PARTIAL**. `axes.highlight_from` is a static tail from a date; `build_to` caps the draw; `relight` only re-fires a bracket or the title. |
| A12 | Context series ghost and one series stays lit. | China 101-102 (the four yields dim at 17:23.2, China lit at 17:36.5); Bubbles #75, #78 | "Now, look at China's 10-year government bond yield. It has actually gone down" | dim, then a focus +13 s later | **PARTIAL**. A series `muted` flag exists statically (`ledger_page.py:1290`). An on-word mute/focus verb does not. |
| A13 | Comet retrace: one stretch redraws bright over its own ghost. | Bubbles #75, 16:21 | "credit risk across several of the AI related companies" | – | **MISSING**. `undraw` / `build_to` act on the live stroke only. |
| A14 | ✓ / ✗ badges pop over ring markers or tiles. | Bubbles #40 ✓✓, #44 ✗✗, #69 | "Two completely different bubbles … essentially the exact same sequence" | ✓ at each ring in turn | **PARTIAL**. `chip` has a CROSS. No ✓ (tick) state, and no badge on a chart datum. |
| A15 | A brace between two points, with a label and a sub-figure. | Bubbles #41 "Quant Allocation Strategy / 120% Return" | "our quant allocation strategy that would have generated…" | – | **HAVE**. `page_species:bracket` (label, sub). |
| A16 | A span bracket over a DIAGRAM ("Decades"). | China 107-110, 18:10-18:29 | "Major shifts in global power take decades to play out" | the bracket draws 8.5 s after the diagram | **PARTIAL**. `bracket` is a ledger-page species only. |
| A17 | A dashed hypothetical path off the plot's right edge, with "???". | Bubbles #43, 8:34 | "needs to be taken seriously. even if stocks are at all-time highs" | – | **MISSING**. |
| A18 | The camera pushes to the latest stretch of the line. | Bubbles #42, 8:22 | same beat as A17 | – | **HAVE**. `species:focus_zoom` / `punch` / camera keys. |
| A19 | Press cards dock ONTO the plot at their dates, with a curved leader and a ring. | Bubbles #39, #43 | "The credit market began flashing warning signs in early 2000" | – | **PARTIAL**. The press dock and ring exist; an aimed-at-a-datum placement does not. Conflicts with E63 (C2). |
| A20 | Event pins with stacked tag pills along a line. | Bubbles #19; China 43 | "caught up in all of the narratives and the bad news" | pins land as the draw reaches them | **HAVE**. `axes.marks` (dot, chip, dashed leader), `scene-evidence-engine.mjs:6912`. |
| A21 | The line changes ink at a pin (red to green at "the call"). | Bubbles #89, 19:45 | "helped put them on a much more clear path" | – | **MISSING**. |
| A22 | The whole chart recedes nearly to black before the next beat. | Bubbles #27, 5:11 | "long after the lenders have quietly started heading for the exits" | – | **HAVE**. The field's recede (`lpPlateRecede`) / `exit:dip`. |
| A23 | The chart BLURS behind an explainer overlay (term pill, icon flow, press card). | Bubbles #11-12, 14, 22, 30, 38, 52, 71, 76-77 | "You can think of a credit default swap as a form of insurance…" | the blur holds 12-24 s | **PARTIAL**. Our equivalents are the wash and `chart_to:park`. The blur itself conflicts (C1). |
| A24 | The old chart shrinks aside while the next frame grows out of it. | Bubbles #34, #64 | "Home building companies also started to accumulate more and more debt" | – | **HAVE**. `chart_to:park` + `recipe:chart-to-chart-with-no-cream` (blur aside). |
| A25 | A value badge lands on each bar on its word. | Bubbles #5-8 | "$300 billion … $1.3 trillion" | one per window | **HAVE**. The bars page's values / `recipe:badge-ladder`. |
| A26 | A flow EDGE fails: an X on the link, the bill turns red. | Bubbles #44-46, 8:46-9:22 | "If not, then credit default swaps will start to rise exponentially. Lending will begin to dry up" | ✓ at #45, ✗ at #46 | **PARTIAL**. `arc` takes an X (map only). Flow `swap` changes a node; no edge X. |
| A27 | Money glyphs travel along the edges. | Bubbles #44-46, #57-58, #76-77 | "Open AI and Anthropic need investors money to pay the hyperscalers" | continuous | **MISSING**. |
| A28 | An icon rail builds beside a surface. | China 23-25 | "Oil would spike to 150 or even $200 a barrel … All flights were going to be cancelled" | rail items 1:28.8 / 1:37.5 / 1:44.2 | **HAVE**. `dock_option:badge`. |
| A29 | A numbered agenda, tile 2 revealed later. | China 81, 87 | "two key strategies that they are putting in place" | tile 1 at 13:01, tile 2 at 14:28 | **HAVE**. `species:agenda`, `recipe:numbered-agenda-on-its-words`. |
| A30 | A dashed group rectangle draws round its members. | China 74-77, 84-86; Reset t=5:40 | "invisible to the US financial system" | – | **HAVE**. Flow `box` (dash-by-dash nib). On the map it is only PARTIAL. |
| A31 | Node swap, the rhyme (Arab Oil States swapped to China). | China 82-84 | "China has now shown that it too can control the global oil supply" | 14:06.5 to 14:14 | **HAVE**. `flow` swap, `recipe:mechanism-drawn-then-counted`. |
| A32 | Year stamp, figure stamp in a country, a B/W figure cutout. | China 57-60, 78-79 | "a record 1.4 billion barrels" | ~2 s cadence | **HAVE**. `species:stamp` + `dock_kind:cutout`. |
| A33 | Pedestal DOWN through the waterline to reveal the hidden base. | Bubbles #1-3 | "the real debt load is larger" (Gemini-B T1 paraphrase) | – | **MISSING**. The camera exists (`kinetics/camera.mjs`); a waterline stage does not. Gemini-B T1. |
| A34 | Chapter pill: it types centre stage ("Strength of the Narrative", later "Liquidity"), then docks top-left above the title of every chart in the chapter. | Bubbles #61-62, 12:22; persists to #79 | "we can get a very good sense of that by looking at two crucial things" | carried for ~5 min across compositions | **MISSING**. 0 hits "chapter tag" / "kicker". |
| A35 | Poof arrival under a load; a wire draws on, then carries the load. | Bubbles 11:58.5-12:00 (Gemini 09-13, corrected) | "an elephant on a ball on a tightrope" | poof ~0.5 s, wire ~0.8 s (left, then right) | **MISSING**. 0 hits "poof". BRAVOS-RIG-VERIFIED: "Arrivals we lack". |
| A36 | The active actor tile glows (green or red halo) while the sentence is about it. | Bubbles #20, #25, #35; China 97-98 | "Credit investors … Stock Market Investors" | on the word | **PARTIAL**. `chip` has DIM only (`species/chip.mjs:44`). There is no LIT state. |
| A37 | Sonar ping at a point on a map. | Gemini 09-10 technique 3 (Hormuz) | – | `r = r_max((t-t0) mod T)/T` | **MISSING**. R26-33 is half-closed; `ping` is still open. |
| A38 | The treemap / chart shrinks to make room for the next diagram. | China 91 | "So when China stepped in to cushion the oil shock" | +3.3 s after the Xs | **HAVE**. `chart_to:park`. |
| A39 | The number counts up in an axis capsule at the break. | China 54 ("1,397 → 1,405") | "China has around 1.4 billion barrels" | – | **HAVE**. `overflow_capsule:"axis"`. |
| A40 | The balance tips on the word. | China 113-114 | "not just threats … opportunities" | within 4 s | **MISSING**. |

## 3. EFFECT: visual treatments (13 items: 8 HAVE, 1 PARTIAL, 4 MISSING)

| id | effect | where | OURS |
|---|---|---|---|
| F1 | Neon glow / bloom on the lines. | Bubbles #13, #16, #62; China 39, 100 | **HAVE**. R26-228 "the stroke's bloom pulse" + E67 inks. Gemini 09-10 technique 5 (the two-pass stroke) is covered. |
| F2 | A glow OUTLINE on a region (the pyramid's hidden block, a bar). | Bubbles #3-4 | **PARTIAL**. Only the burst's glow exists; there is no region-outline glow. |
| F3 | A radial halo behind the active tile. | Bubbles #20, #25, #35 | **MISSING**. Pairs with A36. |
| F4 | The whole chart recedes to dim. | Bubbles #27 | **HAVE**. See A22. |
| F5 | Key-phrase highlighter band on press headlines. | Bubbles #9, #36, #48, #55; China 5-10 | **HAVE**. `dock_kind:press` (accent key phrase) + the record highlighter. |
| F6 | A circuit-trace ground behind press cards and the AI chip. | Bubbles #2, #9 | **MISSING**. It is decor; a plate could carry it. |
| F7 | A spotlight vignette on the metaphor prop. | Bubbles #59-60, #80-83 | **HAVE**. `species:spotlight`. See C6. |
| F8 | Struck items dim under their X. | China 26-28, 90 | **HAVE**. `chip` DIM 0.55; the treemap's DIM. |
| F9 | The newest press card lit, older ones stepped back and dimmer. | China 5-10 | **HAVE**. `dock_option:stack`. |
| F10 | The TV/studio display stage for other people's claims. | China 2-25; Reset t=0:14 | **HAVE**. The ART-embed surface (R26-32 closed). Gemini 09-10 technique 1. |
| F11 | The answer bar glows. | Bubbles #65-67 | **HAVE**. `recipe:emphasized-bar-lit`. |
| F12 | The collage dissolves into "?" marks. | China 11, 0:35 | **MISSING**. |
| F13 | Satellites glide in with cone beams over the count array. | China 53, ~8:20 (Gemini 09-10 technique 2) | **MISSING**. |

## 4. RECIPE: timed compositions (17 items: 6 HAVE, 8 PARTIAL, 3 MISSING)

| id | recipe | where | composes | OURS |
|---|---|---|---|---|
| R1 | **The hidden base**: the surface tip, the waterline, the hidden base glows, leader labels, then a logo legend. | Bubbles 0:00-0:48 | T1 + A33 + F2 + A8 | **MISSING**. |
| R2 | **Bar ladder**: one bar and its badge; comparators arrive with pills; the big bar's membership is shown with logos in a dashed bracket. | Bubbles 0:48-1:36 | T2 + A25 + T3 | **PARTIAL**. The bars and badges are HAVE; the logos-in-bar step is MISSING (C3). |
| R3 | **Term explained over the chart**: the chart defocuses, a term pill lands, an icon flow explains it (investor / insurance / Oracle, a bill crossed), then the chart comes back sharp with the level rule to the GFC. | Bubbles 1:59-3:00 | A23 + chip + flow + A26 + A9 | **PARTIAL**. The compliant route is park (not blur) + chip + flow + un-park. The level rule (A9) is missing. |
| R4 | **Proof walk on a long line**: span bands; the pre-crisis runs lit; a ring at each peak; press cards dock at the rings; ✓ chips; a bracket carries the strategy's return. | Bubbles 7:22-8:22 | T11 + A11 + A8 + A19 + A14 + A15 | **PARTIAL**. The missing parts are A11, the ✓ and the press-to-datum step. |
| R5 | **Push to now, then the unknown**: the camera pushes into today's stretch, cards arrive, a dashed "???" runs off the edge. | Bubbles 8:22-8:46 | A18 + press + A17 | **PARTIAL**. A17 is missing. |
| R6 | **Cycle model**: two waves; actor tiles glow on the leading wave; candles overlay it; it dims; a third wave is added; a causal chain (company, liquidity, stock price, layoffs) sits over it. | Bubbles 4:35-5:59 | T7 + A36 + T8 + A22 + flow | **MISSING**. |
| R7 | **Race to the terminal values, then the values leave as bars**. | Bubbles 9:58-10:58; China 16:45-18:04 | A2 + A3 + A12 + A5 | **HAVE**. `recipe:chart-recast-into-the-other-form` (plus line-by-line). A12's on-word mute is the one PARTIAL inside it. |
| R8 | **Capital loop orbit** with bills. | Bubbles 11:22-11:58; Reset t=9:30 | T21 + A27 | **MISSING**. |
| R9 | **Scale-break race, stamp, cards beside**. | China 7:42-9:20 | T16 + A6 + A39 + T25 | **HAVE**. `recipe:ranked-bars-race-then-burst`. |
| R10 | **Treemap census X, then it parks for the flow**. | China 14:52-15:31 | T17 + A38 + flow | **HAVE**. `recipe:treemap-census-and-its-exception`. |
| R11 | **The map lit, stamped and struck**. | China 9:42-13:00 | T19 + A32 + arcs | **HAVE**. `recipe:vector-map-named-lit-and-stamped`. |
| R12 | **The rhyme**: A to B to C in 1973, the node swapped to China, a verdict card. | China 13:12-14:27 | T20 + A31 + press | **HAVE**. `recipe:mechanism-drawn-then-counted`. |
| R13 | **Predictions board**: a rail beside the TV, then a board, struck "6 Months Later". | China 1:28-1:58 | A28 + T28 | **PARTIAL**. The cards are HAVE; no recipe is written for the pair. |
| R14 | **Two verdict panels**: SELL ✗ and BUY & HOLD ✗, each with an actor. | Bubbles 18:45-19:09 | T26 + A14 | **PARTIAL**. The ✓/✗ states are missing. |
| R15 | **The claim stack on the TV**. | China 0:04-0:42 | F10 + F9 + press | **HAVE**. `recipe:chart-parks-for-their-claim` / `held-page-hosts-the-docks` + the embed. |
| R16 | **The rig**: elephant on a ball on a wire; label cards attach one at a time with leaders; the ball alone scales while the contact holds. | Bubbles 11:58-12:22, 18:09-18:45 (Gemini 09-13, corrected at 2 fps: no catenary, no wobble) | A35 + callout leaders + a contact-pinned scaling child | **PARTIAL**. Throw, land and leaders exist. The poof, the load-bearing wire and the pinned child do not. |
| R17 | **Dual-lane stage**: a chart left, a map with a ping right, one clock. | Gemini 09-10 technique 3 | park + dock + vecmap + A37 | **PARTIAL**. The ping is missing (R26-33). |

## 5. STYLE: finish rules (8 items: 4 HAVE, 3 PARTIAL, 1 MISSING)

| id | rule | OURS |
|---|---|---|
| S1 | One accent (pink) for the subject; white or grey for context; green only for up, ✓ and the CTA. | **HAVE** by ruling, but with a different palette: E67's electric teal plus orange (E22 charcoal field). |
| S2 | Framed plot: accent title top-left, subtitle, unit label above the y axis, legend in a top band inside the frame, source line bottom-left. | **PARTIAL**. Title and source ink per glyph (E52). The legend band is refused by E53 §3 (the label goes at the line's end). |
| S3 | Dashed means hypothetical or a grouping; solid means actual (waves, "???", group boxes). | **PARTIAL**. Dashed means a reference rule or a flow frame. We have no dashed actual-to-projection. |
| S4 | Value capsule: white on an accent capsule, with a dashed ring around it when it is the answer. | **HAVE**. Pills, `overflow_capsule`, ring. |
| S5 | Story bars carry no axis, only a category pill above each bar. | **PARTIAL**. Story bars carry names; the pill-over-bar form is not a named option. |
| S6 | Logos as data labels (tiles in a bar, a legend column, the axis under a bar). | **MISSING**. Chips carry glyphs, not brand marks. |
| S7 | Rounded dark icon tiles, the icon with its caption under it. | **HAVE**. `species:chip`. |
| S8 | Builds happen inside a held, locked composition (China: 6.0 events/min against 2.5 compositions/min; 37 of 45 holds camera-still). | **HAVE** as doctrine: P49 LOCKED default; `recipe:held-page-hosts-the-docks`. |

**Totals: 106 items. 55 HAVE, 25 PARTIAL, 26 MISSING.**

## 5b. Gemini's ideas, each marked (build on these, do not redo them)

| source | idea | status |
|---|---|---|
| Gemini 09-10 t1 | Diegetic studio display stage (homography, 4 depth layers, sine pan) | HAVE: the ART-embed surface (R26-32 closed; the sine pan was dropped with parallax) |
| Gemini 09-10 t2 | Isometric silos | HAVE: `count_array` |
| Gemini 09-10 t2 | Satellites with cone beams | MISSING (F13) |
| Gemini 09-10 t2 | Camera track-left to the cutaway | REJECTED: not in the frames (composition 53 is still) |
| Gemini 09-10 t3 | Dual-lane chart and map | PARTIAL: park + dock + vecmap |
| Gemini 09-10 t3 | Sonar ping | MISSING (A37, R26-33) |
| Gemini 09-10 t4 | Scale-break domain spring | HAVE: E60 burst (5% overshoot on the bar, not 8% on the domain) |
| Gemini 09-10 t5 | Neon bloom | HAVE: R26-228 |
| Gemini 09-10 t5 | Tip-riding pills | HAVE: `tippill` |
| Gemini 09-10 t5 | DoF rack push at 17:15 | REJECTED: not in the frames or the camera measurement; "wash beats the focus rack" |
| Gemini 09-10 | "9.97 s mean shot is the gold standard" | REJECTED: a sampler artifact (doc 46 §46.7) |
| Gemini-B T1 | Iceberg pedestal, clip-plane waterline | MISSING (T1/A33/R1). Candidate 4 below is the E53-safe form |
| Gemini-B T2 | Out-of-phase sine kinematics | MISSING (T7/R6). Candidate 12; needs a ruling (C9) |
| Gemini-B T3 | Elephant prop with a catenary sag and a wobble | PARTIAL. Gemini 09-13 corrected: no catenary, no wobble; the poof and the pinned child are missing (R16) |
| Gemini-B T4 | Circularity orbit with particles | MISSING (T21/R8). Candidate 5 |
| Gemini-B | Locked camera 66% | HAVE as doctrine (P49) |
| research lane 09-07 (`findings_bravos.md`, from Bravos's site reports, not the videos) | Multi-panel 3 tiers | HAVE: `tiers` |
| research lane 09-07 | Equal categorical spacing | HAVE: E53 §3 slots |
| research lane 09-07 | Era headers over brackets ("THE REFINANCING SHOCK") | HAVE: `span` with its name above |
| research lane 09-07 | Callout circles on inflections | HAVE: `ring` |
| research lane 09-07 | Bottom verdict boxes | PARTIAL: `verdict-recap` is a different object |
| treemap blueprint 09-10 | Numerals in cells, label culling, X on the word, affine shrink | all HAVE (T17/A38) |

---

## 6. CANDIDATES, ranked (MISSING and PARTIAL only)

Each candidate composes existing cards (s70: recipes are timings that compose). It gives the engine work and the H rows that could carry it. Row numbers follow `content/video_engine/projects/systems-and-blowups/steel-and-paper/REBUILD-TREATMENT-H.md`, rows 7-24.

| rank | proposed id | covers | composes | engine | H rows that could carry it |
|---|---|---|---|---|---|
| 1 | `page_species:lit_stretch` (plus a `comet:true` variant) | A11, A12, A13 | `build_to`'s capFrac (from/to on the path), `axes.highlight_from`, the R26-228 bloom, `relight` (re-fire on return), the series `muted` flag as an on-word verb | small | **9** ("crashed by nearly two-thirds": light the fall); **14** (the 23¢ dot-com stretch, then today's 28¢); **15** (the two eras of the rate line); **21** (the +500% run) |
| 2 | `page_species:level_join` | A9, R3's return | `axes.hlines` (dashed, own colour), the stroke draw from datum A to datum B, `ring` form dashed at each end, `figure` for the gap | small | **14** ("twenty-eight, the most it has ever been" joined back to the 23¢ peak); **15** (the 6% / 6.5% rings joined to today; the Bravos 5.5 tripwire); **21** |
| 3 | `page_species:axis_tag` | A10 | `retitle`'s per-glyph write + the spring pop of a pill on the x tick | small | **9** ("In two thousand the internet crossed seven percent"); **15** ("two eras"); **22** ("one soft month in June") |
| 4 | `recipe:the-hidden-base` (the iceberg as bars at a waterline) | T1, A33, R1, F2 | `page_builder:bars` (reported above zero, commitments hanging BELOW a waterline rule), `span` shading below the line (dark), camera keys (a pedestal: the stage is taller than the frame, per P49), `chip` legend, `figure` | small-new (the bar hangs below the rule) | **16**: "eight hundred and twenty-two billion in lease commitments … Data centers they've already agreed to pay for". This is the same claim as Bravos's iceberg (leases plus purchase commitments). |
| 5 | `species:loop` (a `flow` ring layout plus tokens) | T21, A27, R8 | `flow` (box, chips, clothoid arrows), `stagger`, arc-length tokens from `stroke.mjs` | small-medium (a ring in `flowLayout` + tokens) | **16** (who is paying: bond buyers, hyperscalers, capex, then back to the bond market); **17** (the arithmetic, 94% debt-funded); **18** ("It was never the AI stocks") |
| 6 | `plate_option:project` | T23, A17, S3, R5 | `chart_to:extend`, `flow.mjs`'s dash-by-dash nib applied to the continuation, `tippill` for the forecast figure or "?" | small | **16** ("four hundred and eighty… six hundred and ninety": a consensus forecast); **17**; **23** ("booked solid through twenty twenty-six") |
| 7 | `species:chip` states `lit` and `tick` | A14, A36, F3, R14 | `chip` (the cross exists), `dock_option:badge`, `idle:pulse` | small | **10** (the chips doubling, customers flat); **22** (tripwires: "Bravos 5.5 / mine"); **20** (the three questions, if they sit as chips rather than the checklist) |
| 8 | `recipe:proof-walk-on-the-long-line` | R4, A19 (E63-safe) | `span`, #1, `ring`, the press card read-then-park (`recipe:read-park-build-write`), which PARKS to a chip at the datum rather than docking over the plot, #7's tick, `bracket` | none after #1 and #7 | **12** (three manias: "the trough already doing its job"); **14**; **18** |
| 9 | `recipe:term-over-the-parked-chart` | R3, A23 (compliant form) | `chart_to:park`, `chip` (the term), `flow` (the mechanism), un-park, #2 | none after #2 | **16** ("bend the bond market": what IG credit weighting is); **18** ("railway certificates") |
| 10 | `species:chapter_tag` | A34 | caption STAGE (writes centre stage), `retitle`'s glyph write, an affine park to top-left, held across the chapter's pages | small | **13** (RESET 1), **18** (RESET 2), **23** (RESET 3): one tag per act |
| 11 | `recipe:two-verdict-panels` | T26, R14 | `chart_dock:panels`, `chip` + #7 (✓/✗), `ring` on each tip | none after #7 | **22** ("I trimmed some"); **24** (the close) |
| 12 | `page_builder:cycle` (schematic phase waves plus the lag bracket) | T7, R6 | the line page from a closed form, `bracket` placed horizontally for the lag, #6 for the dashed future | new builder | **12** (the hype cycle page `ev-three-manias`: the peak and trough markers ARE a cycle). Needs a ruling (C9). |
| 13 | `flow` option `brace` (decomposition) | T24 | `flow` + `bracket`'s draw, applied to a column of nodes | small | **15** (the rate as policy + term premium, if the script splits it); **16** |
| 14 | `species:regime_switch` | A21 | the line's ink changing at a `marks` pin | small | **22** ("The flip"); **24** |
| 15 | `species:ping` (R26-33's open half) | A37 | the `vecmap` stamp clock | small | none in H (H has no map row). Park it. |

Not proposed:
- F6 (circuit ground) and F12 (the "?" dissolve) are decor.
- A35 (the poof) and R16 (the rig) belong to the prop/rig lane, not the chart vocabulary. Rows 10 and 23 throw cards and could use a poof, but that is an arrival card.
- T8 (candles) and T27 (the balance scale) have no H row.

## 7. CONFLICTS with our rulings (the operator decides)

- **C1. The chart blurs behind an overlay** (A23; Bubbles #11-12, 14, 22, 30, 38, 52, 71, 76-77). Our rules say the opposite:
  - "wash beats the focus rack" (OPERATOR-RULINGS:729).
  - E63: *"a card never READS over a ledger page's plot, drawing or finished."*
  - Bravos puts the explainer ON the blurred chart. Candidate 9 uses park instead. Ruling needed only if the operator wants the blur itself.
- **C2. Press cards dock onto the plot at their dates** (A19; Bubbles #39, #43). This conflicts with E63 (same quote). Candidate 8 parks the card to a small chip at the datum after it reads in its slot.
- **C3. The composition bar** (T3; Bubbles #8). E53 §2: *"Never a stacked bar (baseline drift) … This is a never-build, not a backlog item."* Bravos's tiles are equal-height membership, not values, so a ruling could class it as a chip set on a bar rather than a stack. It would fit **row 18** ("AI builders are now twenty percent of the S&P five hundred").
- **C4. The iceberg pyramid encodes value as AREA** (T1). E53 §1: *"A chart that asks the reader to compare areas, angles or saturations is refused with this ruling cited."* Candidate 4 is the length-encoded form.
- **C5. Dual-axis line over line, including an INVERTED right axis** (T14; Bubbles #74, #78-79; Reset t=7:00, t=13:40).
  - E53 §4: *"Only when the two must be read AGAINST each other does a page carry two scales, and then it is an OVERLAY … the bars keep the plot … the line owns no axis, carrying a terminal tag instead."*
  - E75 §3: *"Never both scales on one reading."*
  - Bravos also draws the Fed funds rate as a series. E53 §5: *"A policy rate is a RULE, not a series."*
- **C6. Light as the emphasis.** Bravos uses a spotlight on the elephant, glowing stretches and a halo on the active tile (F7, A11, F3).
  - s71: *"a light is never the move."*
  - s76: a spotlight applies only where there is a specific callout.
  - s91: *"The view is a light as an annotation/highlight, not as motion"* (0 events).
  - Open question for the operator: does candidate 1 (a stretch that relights by a drawn stroke) earn motion credit, or is it an annotation like the spotlight?
- **C7. Rings on every vertex** (T9; Bubbles #28: 5 rings, "+40%" each). E56 allows a ring on a chart datum, but it also says *"We have to stop drawing rings or circles on everything."* A datum ladder of 5 rings needs the operator's word.
- **C8. Neon bloom.** REPORT.claude.md recorded the bloom as "by ruling not ours (E22: chalk on charcoal)". Since then R26-228 / E99 s83 wired the bloom pulse ("keep the electric/glow"). Resolved; recorded so nobody re-litigates it.
- **C9. Schematic curves with no data** (T7 waves; T9 "+40% every year"; T26 mini-charts). The binding rule is that figures are never fabricated, and E52 says the math is drawn. A schematic cycle carries no measured figure, so it is a diagram rather than a chart. It needs a ruling on whether a data-free curve may be drawn in chart ink. (T9's "+40%" is also Bravos's own performance claim.)
- **C10. The decorative donut** (T10). E53 §1 amendment: a pie only when (a) the claim is about one named slice, (b) that slice is highlighted, (c) its figure is written, and (d) there are five slices or fewer. Bravos's donut is decor and fails (a) and (c).

## 8. What the next watches should look for (3-5 Gemini, 3-5 Codex/Luna)

1. **Make every ledger a difference-detector ledger** (the `claude-watch` build: `cuts.json`, `camera.json`, one frame 0.5 s after each event). Do not use a fixed sampler. The Bubbles ledger is a 12 s sampler, so I could not time a single Bubbles build (T1-T13, A9-A27). Re-run Bubbles through `claude-watch/build_ledger.py` first. The Reset watch has only 23 frames and needs the same treatment.
2. **Lit stretch mechanics** (for candidate 1). Is the lit stretch a RETRACE drawn by a pen, or a cross-fade? How long is it, and when does it start relative to its word? Play Bubbles 7:40-8:20, 14:35-14:50 and 16:20-16:35, and China 5:10-5:20, at 10 fps.
3. **The level rule** (for candidate 2): its draw direction and speed, and the order of rule, rings and label (Bubbles 2:47-3:00).
4. **The axis tag** (for candidate 3): does the pill replace the tick or sit over it? When does it pop relative to the word? Does it persist?
5. **The loop** (for candidate 5): bill speed (constant or eased), spacing, the count on the ring, the arrow draw order, and how a node's ▲/▼ chevrons fire (Bubbles 11:22-11:58; Reset 9:10-9:50).
6. **The iceberg** (for candidate 4): is the reveal a camera pedestal, or a scale about a point (the rig read found a scale where the stills read a move)? Measure the waterline's own motion (Bubbles 0:00-0:48; `camera.json` #1 says SLOW_PUSH only).
7. **Chart to chart**: frame by frame, how does chart A become chart B (Bubbles 6:40-6:50, 12:58-13:10)? Compare with our `park`, `recast`, `remake` and `rescale`. Also count how often Bravos cuts between charts and how often it transforms one into the next. E64 says we never cut.
8. **Dual axes**: how often do they appear, is the right axis labelled, and is it inverted? This would give the operator evidence for C5.
9. **Frequency across 5+ episodes**: count each species per minute, to separate signature moves from one-offs. My candidates rank by H-row fit, not by how often Bravos uses them. Candidates 1-3 look like signature moves (every chart) but that is uncounted.
10. **Sound**: whether builds carry SFX (whooshes, ticks, the poof), and whether the bed ducks under builds. Neither ledger records audio events.
11. **Forms not seen in these episodes**: scatter or regression, a yield curve by maturity, heat maps, waterfalls, slope charts, and any 2.5D chart. We have `form=extruded_bar`, but Bravos showed none.
12. **The Gemini 09-10 ping**: verify it exists. My China frames show the Gulf map at 2:57.8 with labels but no rings. Gemini's "frame_0028 at 2:34" claim is still unverified.
