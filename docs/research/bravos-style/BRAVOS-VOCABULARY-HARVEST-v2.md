# Bravos Research chart vocabulary, merged harvest v2 (explorer, 2026-09-23)

This file merges the v1 harvest (106 items from three Bravos videos) with six new watches: four GPT/Luna reviews and two Gemini reviews. Nine Bravos videos are covered in total. Each item is deduplicated across the videos. The **n** column counts how many of the nine videos show the item; frequency is the signal. Each item is marked HAVE / PARTIAL / MISSING against the fable-p68 catalogue.

The static style numbers are in `BRAVOS-LONGFORM-CHART-SPEC.md` and are not repeated here. The companion guide, one entry per type, action, effect and recipe grouped by sentence act, is `BRAVOS-USE-WHEN.md` in this folder.

## 0. Sources

| code | video id | title | watcher (file) | coverage and trust |
|---|---|---|---|---|
| BUB | `RUH3BPQ5fTo` | The Bubble's Final Phase Has Begun | v1: Gemini 12 s sampler + contact sheets, read by Claude | **coarse**: every "#n" is a 12 s window (#n starts at (n-1)x12 s) |
| CHN | `1ZS5_txbOsc` | China Just Triggered A New World Order | v1: Claude difference-detector ledger | **event-timed**: times are builds |
| RST | `_rwFYNlKtEc` | A Once in a Lifetime Financial Reset | v1: Codex, 23 frames | thin. Its Gemini review was **not on disk** at either check (folder empty) |
| STK | `4AkB4c0tTfU` | Stocks Are About To Go Nuts (Emergency Update), 10:37 | GPT/Luna, `docs/research/bravos-chart-watch-2026-09-23/4AkB4c0tTfU.md` | 48 balanced frames + 63 focused at 2 s |
| HIS | `Jw8ykhoOVBQ` | History is About to Be Made (Emergency Update), 14:20 | GPT/Luna, `.../Jw8ykhoOVBQ.md` | 72 balanced + 116 focused at 0.5 s. LEDGER.md still says "running", but the report is complete |
| DOM | `PWMhM2_dj3s` | The First Domino of the Global Debt Crisis is Here, 18:39 | GPT/Luna, `.../PWMhM2_dj3s.md` | 44-frame sweep + 316 focused at 0.5 s |
| JPN | `nB1eXWQlW58` | Japan and the US Just Pulled the Trigger, 10:29 | GPT/Luna, `.../nB1eXWQlW58.md` | 33 grid frames + 170 focused at 0.5 s |
| BOOM | `jx3Ll-GJtMY` | (the review gives no title; its first chart is "AI Versus Past Boom-Bust Cycles") | Gemini, `docs/research/runs/bravos-watch/jx3Ll-GJtMY/GEMINI-REVIEW.md` | **Gemini's own timings; no frames or transcript on disk.** Tagged G-only where it is the only witness |
| D40 | `u70oUWgVoYU` | America Just Triggered a $40 Trillion Debt Reset | Gemini, `.../u70oUWgVoYU/GEMINI-REVIEW.md` | Gemini timings. 591 survey frames, 24 sheets and `clean_transcript.txt` are on disk. I spot-checked four quotes against the transcript (04:30 "7.5% per year", 12:04 "four times bigger", 12:56 "lowest level", 14:29 "third largest buyer") and all four matched |

**Gemini review status.** `jx3Ll-GJtMY` and `u70oUWgVoYU` are folded in. `_rwFYNlKtEc` and `cbknsJEshD8` were checked twice during this work, at the start and before writing, and both folders were empty. Neither is folded in.

**Catalogue delta since v1.** None. `effects/cards/*.json` (18 axes), `effects/recipes/*.json` (46) and `scripts/species/*.mjs` (24) are unchanged, and P69 T35/T35b are still `pending`. What has changed since v1 is the RULINGS: E99 s98 (blur under a dock), s99 (a light that travels or blinks is motion) and s100 (area forms are valid when drawn in proportion with their figures written). They move conflicts, not statuses (see §7).

**Status key.** It is the same as v1:
- **HAVE**: the named card, recipe or species exists.
- **PARTIAL**: the missing part is named.
- **MISSING**: absent from the roots listed in v1 §Sources.
- Where the catalogue could do something but a ruling refuses it, the row says so. "0 hits" means `docs_find.py` plus a grep of the cards. The docs layers still report STALE, so every MISSING claim was also grepped in the card JSONs.
- New ids continue v1's numbering (T29+, A41+, F14+, R18+, S9+), so v1 ids stay stable.

**Reviewer tags.** P = GPT/Luna, G = Gemini, C = Claude (v1), X = Codex (v1).

---

## 1. TYPE: chart and visual forms (48 items: 23 HAVE, 11 PARTIAL, 14 MISSING; 20 new)

| id | form | n | videos (example) | OURS |
|---|---|---|---|---|
| T1 | Partitioned pyramid "iceberg" at a waterline | 1 | BUB 0:00-0:48 | **MISSING**. s100 now ALLOWS it when drawn in proportion with figures written (C4 cleared) |
| T2 | Axis-less story bars: pill over the bar, glowing value badge | 3 | BUB 0:48; HIS 11:01 ("$28 Billion" / "$150 Billion" with period tabs); STK 1:54 (two bars, endpoint numerals) | **HAVE**. `page_builder:bars` + `recipe:emphasized-bar-lit`; the pill-over-bar is style S5 |
| T3 | Composition bar: logos as tiles inside a bar | 2 | BUB 1:24; BOOM 07:55 (G: 5 logos in a glass bar) | **MISSING**. Conflicts with E53 s2 (C3) |
| T4 | Divergence pair / side-by-side charts | 2 | BUB 1:48; BOOM 06:10 (G: two full charts, a "!" badge between) | **HAVE**. `chart_dock:panels`, `page_builder:tiers` |
| T5 | Framed single line with a ceiling / threshold rule | 3 | BUB 2:24; DOM 0:39-0:50 (dashed guide + "4%" pill); HIS 02:43 (dashed reference near the endpoint) | **HAVE**. `page_builder:line` + `axes.hlines` |
| T6 | Neon multi-line (3-6 series) | 6 | BUB #16; CHN 16:45; STK 0:20 (four tickers, right-edge pills); HIS 09:10; JPN 05:20; BOOM 00:34 | **HAVE**. The line page + E67 inks + R26-228 bloom + R26-226 line-by-line |
| T7 | Schematic cycle: phase waves, a mania arc, the hype cycle, the debt cycle | **5** | BUB 4:35; STK 1:42 ("three distinct phases"); HIS 03:26, 04:00-05:10; DOM 07:30, 11:00; BOOM 09:35, 15:45 (G) | **MISSING** as a builder. `evidence/ev-three-manias.html` is a one-off HTML record for H row 12, not a catalogue card. C9 needs a ruling |
| T8 | Candlesticks over a ghost wave | 1 | BUB 4:47 | **MISSING** |
| T9 | Zig-zag with a ring and "+40%" at each vertex | 1 | BUB 5:23 | **PARTIAL**. C7 |
| T10 | Decorative "portfolio" donut | 4 | BUB #19; CHN 43; STK 9:33; HIS 13:28 (collage) | **PARTIAL**. `page_builder:share`. A decor donut fails s100 test (b) |
| T11 | Line with shaded bands (recessions, a named phase, a lead zone) | 4 | BUB #37; DOM 12:30, 17:00; STK 1:48 (Mania band, dashed dividers); BOOM 16:30 (G) | **HAVE**. `page_species:span` |
| T12 | Annual columns with a dashed max rule and a ring | 1 | BUB 6:47 | **HAVE** |
| T13 | Dense monthly columns / flow bars around zero, the last one lit | 2 | BUB 13:10; STK 0:02 (ETF flows about a zero baseline) | **HAVE**. `emphasized-bar-lit`, `ring`, `chart_to:rescale` |
| T14 | **Dual-axis line over line** (LHS/RHS, sometimes inverted) | **7** | BUB #74; RST 7:00; HIS 00:00; DOM 01:00, 08:56, 12:00, 16:04; JPN 01:10, 06:38; STK 6:54; BOOM (six forms, G) | **MISSING** (no y2 key). The most frequent CONFLICT (C5) |
| T15 | Small multiples | 2 | CHN 3:29; BOOM 06:10 | **HAVE**. `tiers`, `recipe:two-tiers-one-x` |
| T16 | Ranked horizontal race with a scale break | 1 | CHN 7:42 | **HAVE**. `recipe:ranked-bars-race-then-burst` |
| T17 | Treemap census, departing cells crossed | 1 | CHN 14:52 | **HAVE**. `recipe:treemap-census-and-its-exception` |
| T18 | Horizontal value bars (current values, budget vs actual, durations) | 3 | CHN 18:01; HIS 02:00 (annual budget vs Jan-Apr actual on a month scale); D40 03:30 (G) | **HAVE**. `page_builder:bars` / `race` |
| T19 | Vector map (a country lit, arcs, stamps) | 5 | CHN 9:42; DOM 01:30 (UK filled pink); JPN 04:35 (Japan map with arrows); D40 13:54 (flight arcs, G); BOOM 04:05 (G) | **HAVE**. `vecmap`, `recipe:vector-map-named-lit-and-stamped` |
| T20 | Flow diagram: icon chips + arrows in a dashed box | **8** | CHN 13:12; BUB #44; HIS 01:43; DOM 03:00-04:30; JPN 02:30; BOOM 03:45 (G); D40 (G); RST 5:40 | **HAVE**. `species:flow` |
| T21 | Circular loop / flywheel | 3 | BUB 11:22; RST 9:30; BOOM 04:20, 15:10 (G: "Companies spend -> suppliers -> capacity -> profits -> reinvestment") | **MISSING**. `flowLayout` is a row or a column only |
| T22 | Filled area | 3 | RST 11:00; DOM 18:30 (promo); HIS 13:28 (collage) | **HAVE** |
| T23 | Projection chart: actual -> forecast | 3 | RST 17:20; D40 04:30 (G: "Today / +5 Years / +10 Years"); BOOM 17:48 (G) | **PARTIAL**. The card's `dash` series only fades in |
| T24 | Decomposition brace (one quantity braced into its parts) | 1 | RST 5:40 | **MISSING** |
| T25 | Isometric count array + cutaway card | 1 | CHN 7:43 | **HAVE**. `species:count_array` |
| T26 | Mini-chart verdict tiles / "your portfolio" pair | 2 | BUB 18:45; STK 10:11 | **PARTIAL**. No ✓ state |
| T27 | Balance scale (a tip, or a flag / scale / flag trio) | 2 | CHN 19:10; JPN 06:41 | **MISSING** |
| T28 | Board of options / predictions struck out | 2 | CHN 1:49; DOM 13:00 ("Austerity", "2nd Option", pink X) | **HAVE**. `species:chip` cross |
| **T29** | Partitioned (stacked) horizontal bar: income vs bills, revenue vs obligations | 1 | D40 03:30-04:26 (G) | **MISSING**. E53 s2 still refuses it (C3); s100 offers an area form instead |
| **T30** | 3D extruded donut with an exploded slice | 1 | D40 05:26 (G: 67.54 / 21.81 / 10.65 %) | **PARTIAL**. The flat `share` + `peel` exist. 3D perspective fails s100 test (a) (C10) |
| **T31** | Hub-and-spoke network (a central node, spokes to a ring of nodes) | 2 | D40 09:04 (G: dollar hub, flag ring, severed links red); DOM 04:30 (IMF seal, dashed spokes to six governments) | **MISSING**. docs_find 0 hits "hub and spoke" |
| **T32** | Epoch ruler: a time axis with cards pinned to ticks | 1 | BOOM 05:50 (G: 2000 overbuild -> Smartphones 2007, Streaming 2011, Cloud 2015) | **MISSING**. `thread.mjs` names "the ruler" from HF-16 but builds only the wire |
| **T33** | 2.5D tilted map with routes lighting in sequence | 1 | BOOM 04:05, 05:25 (G) | **PARTIAL**. `vecmap` + `arc`; `plate_option:plane` tilts a page, but a tilted vecmap is unproven |
| **T34** | Fill gauge / meter (a capsule filling to a share) | 2 | BOOM 10:55 (G); D40 17:24 (G: two-thirds filled) | **PARTIAL**. `chart_dock:shares` fills tracks to a fraction. No single vertical gauge; only a still prop `prop-treasury-yield-gauge-5pct-v1.png` |
| **T35** | Broken-axis cross-era line (`//` between the 1860s and 1985) | 1 | HIS 07:18-08:01 ("AI and Railway Spending As a % of GDP") | **MISSING**. E53 s3 tension (C13) |
| **T36** | Rebased cycle comparison (x = years since start, y = multiple of the trough) | 1 | BOOM 00:34 (G: AI vs Dotcom, Roaring 20s, Railway, Canal) | **HAVE**. A line page over a rebased series file; the rebasing is our derived layer (E77) |
| **T37** | Long log-scale history line | 1 | BOOM 02:19 (G: S&P 1900-2026, 4 / 40 / 400 / 4,000) | **HAVE**. `axes.log` (`ledger_page.py` AXES_KEYS) |
| **T38** | Equation row: inputs, relation, signed result | 1 | DOM 09:30-09:39 (3 %, 5 %, "Real Yield" -2 %) | **MISSING**. docs_find "equation" returns only 46 §46.4 (script structure) |
| **T39** | Companion bars beside a held line | 2 | DOM 06:00-06:04 (GDP vs debt bars beside the 130 % line); HIS 11:01 (the debt bars beside the rate chart, "5x") | **PARTIAL**. Park + a `chart_dock:bars` card exist (`recipe:chart-parks-for-their-claim`); an in-page companion inset does not |
| **T40** | Inset echo: a historical twin mini-chart dropped into the plot's empty room | 1 | BOOM 08:44 (G: "Utility Companies 1929") | **PARTIAL**. The chart card dock exists; the placement is E63 vs E65 (C16) |
| **T41** | A row of precedent cards (three historical rescues) | 1 | DOM 05:00 | **HAVE**. `species:chip` board / `agenda` |
| **T42** | A source document with its passage highlighted and a big figure over it | 1 | JPN 03:20 ("$14.2 trillion") | **HAVE**. `dock_payload:record` / `dock_kind:press` highlighter + `recipe:quoted-figure-becomes-the-felt-number` |
| **T43** | A quote card with a grayscale portrait | 1 | STK 7:44 (the Keynes line) | **HAVE**. `dock_payload:record` + `dock_kind:cutout` |
| **T44** | Promo dashboard / strategy equity curve / returns table | 4 | BOOM 11:25 (G); DOM 18:30; D40 06:46 (G); STK 10:11 | **PARTIAL**: the area line is HAVE, the table with micro-bars is not. **Not proposed**: this is conversion content |
| **T45** | End-card collage of chart species | 1 | HIS 13:28 | **MISSING**. Decor only, not proposed |
| **T46** | Axis-free "Market" motif line with repeated X marks | 1 | JPN 08:20-09:20 | **PARTIAL**. A line page always carries axes; the chip cross exists |
| **T47** | Dense ranked vertical bars (15-25) with rotated labels | 1 | D40 14:22, 15:02 (G) | **HAVE**. `page_builder:bars` |
| **T48** | Duration bars on different bases (Year 20 vs Year 3) | 1 | HIS 06:18 | **HAVE** on ONE scale (E79 s1, H row 19). Bravos's per-row scales would be refused |

## 2. ACTION: verbs on a chart (68 items: 30 HAVE, 22 PARTIAL, 16 MISSING; 28 new)

| id | action | n | videos (example) | OURS |
|---|---|---|---|---|
| A1 | Axes / frame first, then the line draws | 4 | CHN 37; DOM 0:39 (heading and empty plot, then the trace in ~3.5 s); BOOM 00:34 (G); D40 04:30 (G) | **HAVE**. `page_enter:axes`, `recipe:hook-opens-on-the-axes`. See A41 for the reverse |
| A2 | Series added one at a time to a held plot | **7** | CHN 1:57; BUB #49; JPN 01:14; DOM 00:59, 16:04; HIS 09:10; BOOM 00:52 (G); D40 04:30 (G) | **HAVE**. R26-226, `chart_to:extend` |
| A3 | Terminal tags at the line ends | 6 | CHN 16:59; BUB #50; STK 0:18-0:20; HIS 05:54; D40 04:30, 16:10 (G); JPN 05:45 | **HAVE**. E53 s8, `tippill` |
| A4 | A pill or head node rides the drawing tip | 2 | CHN 17:00; D40 12:48 (G) | **HAVE**. `recipe:pill-rides-the-line` |
| A5 | Line-end values grow into bars | 2 | CHN 17:51; BUB #53 | **HAVE**. `chart_to:recast` keyed |
| A6 | A bar shoots past the scale | 2 | CHN 8:01; D40 15:18 (G, a projected value) | **HAVE**. `overflow:burst` |
| A7 | Dashed ellipse on a datum or region | 4 | CHN 5:58; BUB #78; DOM 18:00 (the volatile tail); D40 12:54 (G: trough) | **HAVE**. `ring` `form:"dashed"` |
| A8 | Ring on a point + value capsule with a leader | 6 | BUB #15; STK 0:14; HIS 05:54 ("+100% in 3 Years"); DOM 00:48; JPN 01:19; BOOM 00:36 (G) | **HAVE**. `ring` + `callout` / `figure` |
| A9 | Dashed LEVEL rule drawn from one datum to another | **5** | BUB 2:48; RST 7:00; DOM 00:50 (from the endpoint to a "4%" pill); BOOM 00:41 (G: to the y-axis "5x"); D40 11:50 (G: from bar tops) | **PARTIAL**. `axes.hlines` is static and full-width. See C14 |
| A10 | **Axis tag**: the named year / era / span replaces its tick as an accent pill | **7** | BUB #14; CHN 39; RST 11:00; HIS 05:50 (1843 then 1846 tabs light in sequence); JPN 01:16, 01:35 (2007, 1987, 2001 capsules); DOM 16:00 (1914 / 1946 / 1971; a green 1975 tick); BOOM 02:23, 13:35 (G: "2001", "November 1999") | **MISSING**. No axes key |
| A11 | **A stretch relights**: the glow travels down one segment, the rest mutes | **8** | BUB #39; CHN 5:15; STK 0:16 (falling segment); HIS 05:58-06:03 (red glow down the decline); DOM 06:11 (1914, then WWII); JPN 05:44; BOOM 13:39 (G); D40 16:56 (G "neon sweep") | **PARTIAL**. `highlight_from` is static, `build_to` caps the draw. **Cleared as MOTION by s99** |
| A12 | **On-word isolate (lines)**: peers ghost, one series stays lit | **8** | CHN 17:23; BUB #75; STK 4:14 (retail lit, legend turns pink); HIS 00:07; DOM 08:56 (debt -> inflation); JPN 05:25 (China / UK mute, Japan alone); BOOM 02:37, 16:38 (G: 10-15 %); D40 14:30 (G, bars; see A49) | **PARTIAL**. A static `muted` flag exists; no on-word verb |
| A13 | Comet retrace over its own ghost | 2 | BUB 16:21; D40 16:56 (G) | **MISSING** (lit_stretch's `comet` variant) |
| A14 | ✓ / ✗ badges on tiles or data | 4 | BUB #40; HIS 06:07 (green checks after the branches); DOM 13:00 (pink X); JPN 06:40 (X pins the two endpoints) | **PARTIAL**. The chip cross exists; no ✓, no badge on a datum |
| A15 | Bracket between two data, its label the number | 5 | BUB #41; STK 2:16 ("6x"), 8:00; HIS 11:01 ("5x"); D40 04:30, 12:04 (G "4x"); BOOM 16:25 (G "1.5 Years") | **HAVE**. `page_species:bracket` |
| A16 | Span bracket over a group (a diagram, several bars) | 2 | CHN 18:10 ("Decades"); D40 11:34 (G: "For More Than 2 Years" over three bars) | **PARTIAL**. `bracket` joins two data on a page |
| A17 | Dashed hypothetical path past the last real point | **6** | BUB 8:34 ("???"); RST 17:20; STK 8:20, 9:01; HIS 12:20; JPN 04:15; BOOM 17:48 (G). DOM 16:15's dashed tail is ambiguous (P: "does not establish whether it is a forecast") | **MISSING** |
| A18 | Camera to the latest stretch | 3 | BUB 8:22; JPN 05:44 (crop to the Japan tail, then the "$100 Billion" badge); BOOM 03:10, 17:30 (G) | **HAVE**. `focus_zoom`, `punch`, `chart_to:rescale` |
| A19 | A card docks onto the plot at its date / peak | 4 | BUB #39; STK 8:04 (card linked to the latest peak); HIS 00:17; BOOM 00:44 (G: news card inside the chart) | **PARTIAL**. E63 conflict (C2) |
| A20 | Event pins with tag pills along the line | 4 | BUB #19; CHN 43; DOM 06:11 (WWI, WWII); JPN 01:35 (Black Monday, Dot-com) | **HAVE**. `axes.marks` |
| A21 | The line changes ink at a point | 3 | BUB 19:45; HIS 05:58 (red after the peak); BOOM 09:45 (G: grey -> green -> orange -> red) | **MISSING** |
| A22 | The whole chart recedes to near-black | 2 | BUB 5:11; BOOM (G "dim-to-base") | **HAVE**. `lpPlateRecede` / `exit:dip` |
| A23 | The chart **blurs / dims under an overlay** | 4 | BUB #11-12; DOM 02:00, 09:16 (the plot softens under the card); HIS 06:04 (dims under the Railways tile); STK 1:54 | **PARTIAL**. `exit:blurzoom` has an 18 px backdrop blur; no dock option. **s98 allows it** over a busy chart plate |
| A24 | Old chart shrinks aside, the next frame grows | 3 | BUB #34; D40 04:50, 13:00 (G: scales to ~65 %, docks left); BOOM 08:10 (G) | **HAVE**. `chart_to:park` |
| A25 | A value badge lands on each bar on its word | 4 | BUB 0:48; STK 1:54-2:02; HIS 11:01; D40 11:38 (G) | **HAVE**. `recipe:badge-ladder` |
| A26 | A flow edge fails (an X on the link) | 3 | BUB 8:46; BOOM 04:40 (G: Investors -> X -> Utility); D40 09:04 (G: severed spokes) | **PARTIAL**. `arc` takes an X on the map only |
| A27 | **Money tokens travel the edges** | 4 | BUB 11:22; DOM 03:30, 09:16 (green cash tokens); JPN 02:55 (yen notes on a dotted path); D40 13:54 (G) | **MISSING** |
| A28 | Icon rail builds beside a surface | 2 | CHN 1:28; STK 7:25 | **HAVE**. `dock_option:badge` |
| A29 | Numbered agenda / numbered branches | 2 | CHN 13:01; DOM 11:30 ("1" and "2" paths off the cycle) | **HAVE**. `species:agenda` |
| A30 | Dashed group rectangle draws round members | 4 | CHN 74; RST 5:40; HIS 01:43 (red dashed box round the ROI process); D40 03:30 (G) | **HAVE**. `flow` box |
| A31 | Node swap (the rhyme) | 1 | CHN 14:06 | **HAVE** |
| A32 | Year / figure stamp in a country | 1 | CHN 9:42 | **HAVE**. `species:stamp` |
| A33 | Pedestal down through the waterline | 1 | BUB 0:00 | **MISSING** |
| A34 | Chapter pill held over an act's charts | 1 | BUB 12:22 | **MISSING** |
| A35 | Poof arrival under a load | 1 | BUB 11:58 | **MISSING** |
| A36 | The active actor tile glows | 3 | BUB #20; CHN 97; D40 09:04 (G: red pulse on nodes) | **PARTIAL**. `chip` has DIM, no LIT |
| A37 | Sonar ping at a map point | 2 | CHN (Gemini 09-10, unverified by v1 frames); D40 13:54 (G: origin pin pulse ring). **G-only in both** | **MISSING**. R26-33 open |
| A38 | Chart shrinks to make room for a diagram | 1 | CHN 15:28 | **HAVE**. `park` |
| A39 | The number steps / counts up | 2 | CHN 8:26; STK 1:54-1:58 (59 % -> 116 % -> 200 %) | **HAVE**. `overflow_capsule`, the burst pill's count |
| A40 | The balance tips | 1 | CHN 19:10 | **MISSING** |
| **A41** | **Trace first, furniture after**: the line is up before the title, axes and legend | 1 | HIS 00:04-00:06, 05:50-05:51.5 | **PARTIAL**. Every `page_enter` lands the furniture first. P and C disagree on which order Bravos uses: it uses both |
| **A42** | Orthogonal drop guides: dashed lines from a point to BOTH axes, a pill at each foot | 3 | BOOM 00:36-00:41 (G: "3 Years" on x, "5x" on y); DOM 06:24 (1975 tick + a full-height guide); JPN 01:16 (the 2007 guide) | **MISSING**. It composes A9 + A10 |
| **A43** | Vertical event guide: a full-height dashed line at a date under its capsule | 3 | JPN 01:16-01:37; DOM 06:24; STK 1:48 (dashed dividers of the Mania band) | **PARTIAL**. `axes.marks` (dot, chip, dashed leader); `eventbars` |
| **A44** | In-place badge swap: the pill's text flips, the pill stays | 1 | BOOM 02:23->02:27 ("Dot-Com Bust" -> "Lost Decade"), 02:40->02:48 (G) | **MISSING**. `retitle` rewrites only the title |
| **A45** | Underwater fill: the gap between a prior peak's level and the price below it | 1 | BOOM 02:23, 02:37 (G) | **PARTIAL**. `spread` fills to a rule; a rule from the peak's datum forward is A9 (C14) |
| **A46** | Fill below zero at a negative spike | 1 | D40 12:54 (G) | **PARTIAL**. `spread` to the zero rule |
| **A47** | Divergence wedge: the gap between two diverging lines fills | 2 | BOOM 08:34 (G); D40 04:42 (G) | **HAVE**. `page_species:spread` (E53 s6 "the gap is the argument") |
| **A48** | Bar re-value: the bar shrinks to its old value, then grows to today, a dashed level at each top | 1 | D40 11:46-11:52 (G: $47B in 2016 -> $94B) | **PARTIAL**. `chart_to:compare` melts a bar to a comparator; no two-state re-value with ghost levels (C14) |
| **A49** | On-word isolate (bars): one bar ignites, the rest dim to ~25 % | 2 | D40 14:30 (G: "3rd Largest Buyer"); CHN t530 (spec: lit bar halo, unlit at 0.38x) | **PARTIAL**. `emphasized-bar-lit` lights the answer bar; no on-word dim of the rest |
| **A50** | Scale-out reveal: one bar close, then the axis widens to the whole field and its rank | 1 | D40 15:02-15:06 (G: $120B, "18th Largest Holder") | **PARTIAL**. `species:pull_back` + `chart_to:extend` / `rescale`; the composition is unproven |
| **A51** | Projected overtake: a bar surges past the field to a forecast, a bracket to #1 | 1 | D40 15:18-15:30 (G: "$1.2 Trillion vs $1.1 Trillion") | **PARTIAL**. The burst + `bracket`; a forecast must be labelled (E77, C15) |
| **A52** | The ring travels from one peak to the lagging one | 1 | BOOM 14:15 (G) | **PARTIAL**. A ring on each datum; a TRAVELLING ring is new (and s99 would credit it) |
| **A53** | Lead-lag bracket between two series' peaks | 2 | BOOM 16:25 (G "1.5 Years"); BUB 4:35 (the lag bar between waves) | **PARTIAL**. `bracket` spans two data of one series |
| **A54** | Phase-shift slide: a wave slides along x to show the lag | 1 | BOOM 15:55 (G) | **MISSING** |
| **A55** | Traced state: a point runs along a schematic curve and paints each phase's colour | 3 | BOOM 09:45-10:10 (G); DOM 07:30-08:30 (the active segment green, pink at the next crest); STK 1:48 | **MISSING**. Would compose A11 on T7 |
| **A56** | A dashed box frames the future space before the forward draw | 1 | BOOM 17:45 (G) | **MISSING** |
| **A57** | Magnifier lens over the chart | 2 | STK 9:01 ("PREPARE!"); BOOM 06:25, 09:20, 11:05, 12:30 (G) | **PARTIAL**. `focus_zoom` is the camera form; docs_find 0 hits "magnifier" |
| **A58** | Side dock slides in, then out, and the plot reclaims its width | 4 | BOOM 08:10 / 08:24 (G); JPN 04:08, 05:28 (diagram parked right while the chart holds); DOM 16:15 (What / Why rail); D40 13:00 (G) | **HAVE**. Park / un-park `scale: 1.0` (SPECIES-BY-SENTENCE 12b) |
| **A59** | BUY / SELL state tabs on flow nodes or on the chart | 2 | JPN 04:08, 05:34 (a pink SELL, a green BUY); DOM 17:30 (a "SELL" label on the S&P tail) | **PARTIAL**. The chip label exists; there is no state tab |
| **A60** | Equation built in spoken order | 1 | DOM 09:30-09:39 | **MISSING** (T38) |
| **A61** | "?" prompt at the unknown | **5** | BUB 8:34 ("???"); CHN 0:35; HIS 01:43 (a big ? over the ROI node); DOM 06:15, 13:30; BOOM 08:50 (G: a pulsing red ?) | **PARTIAL**. `overflow_placeholder:"?"` on the burst only; a chip can carry a ? glyph |
| **A62** | A stamp slab on the plot ("EXCESSIVE") | 1 | BOOM 14:04 (G) | **HAVE**. `arrival:stamp`, `species:stamp` |
| **A63** | The opening chart returns with a new label ("Conditions") | 1 | HIS 11:53 | **HAVE**. E40 s4 return from its point + `retitle`; H row 20 |
| **A64** | Continuous slow push on a held chart | 2 | BOOM, D40 (G-only: "1.05-1.10x"). **Disputed**: P found no camera move in HIS, DOM or STK; C measured CHN at 37 of 45 holds still | **HAVE** as `camera:keys`, **REFUSED** by E59 ("never a continuous push on a held chart") (C11) |
| **A65** | Tracking pan following the drawing tip | 2 | BOOM 17:45; D40 (G-only) | **HAVE** as `camera:keys`, **REFUSED** (M14: no camera move over an evidence build) |
| **A66** | Slice ejection (the dominant slice pushes out) | 1 | D40 05:48 (G) | **HAVE**. `page_species:peel` |
| **A67** | Frames and rulers wipe on | 1 | BOOM 03:40, 05:50 (G) | **HAVE**. A wipe exists as `exit:wipe`; the page enters are listed in A1 |
| **A68** | Hard cut from the chart to a speaker clip | 1 | BOOM 00:10, 02:18 (G) | **HAVE**. `exit:cut` into a clip world (a world change, E47 / E64) |

## 3. EFFECT: visual treatments (19 items: 8 HAVE, 4 PARTIAL, 7 MISSING; 6 new)

| id | effect | n | videos | OURS |
|---|---|---|---|---|
| F1 | Neon bloom on the active line | **8** | BUB, CHN, STK, HIS, DOM, JPN, BOOM, D40 | **HAVE**. R26-228 + E67. The spec measures Bravos's hero bloom reaching ~4x further than ours |
| F2 | Glow outline on a region or bar | 3 | BUB #3; CHN t530; D40 14:30 (G) | **PARTIAL**. Only the burst's glow |
| F3 | Halo behind the active tile | 2 | BUB #20; D40 09:04 (G) | **MISSING** |
| F4 | Whole chart dims | 2 | BUB 5:11; BOOM (G) | **HAVE** |
| F5 | Highlighter band on the quoted phrase | 5 | BUB #9; CHN 0:04; HIS 02:11; JPN 03:20; BOOM 00:45 (G) | **HAVE**. `dock_kind:press` / record |
| F6 | Circuit-trace ground | 1 | BUB #2 | **MISSING** (decor) |
| F7 | Spotlight vignette on a prop | 1 | BUB #59 | **HAVE**. `species:spotlight` |
| F8 | Struck items dim under their X | 2 | CHN 26; DOM 13:00 | **HAVE** |
| F9 | Newest press card lit, older ones back | 1 | CHN 0:04 | **HAVE**. `dock_option:stack` |
| F10 | TV / studio display stage | 2 | CHN 0:02; RST 0:14 | **HAVE**. The art-embed surface |
| F11 | The answer bar glows | 3 | BUB 13:10; CHN t530; D40 14:30 (G) | **HAVE**. `emphasized-bar-lit` |
| F12 | Collage dissolves into "?" | 1 | CHN 0:35 | **MISSING** |
| F13 | Satellites with cone beams | 1 | CHN 8:20 (Gemini 09-10) | **MISSING** |
| **F14** | Glowing red perimeter on a headline card | 1 | BOOM 00:45, 18:00 (G) | **PARTIAL**. The press card exists; no glow border |
| **F15** | Axis ticks coloured to match their series (dual axis) | 1 | BOOM (G: steal item 9) | **MISSING**. Goes with T14 (C5) |
| **F16** | Vignette + fine noise on the ground | 2 | BOOM, D40 (G-only). **Disputed**: the spec measured a flat ground (corner = centre) on six CHN frames | **MISSING** (C12) |
| **F17** | Framed plot panel: smoked-glass fill, 1-1.5 px border, soft shadow | **6** | CHN, BUB (spec, measured); HIS ("thin gray borders"); JPN ("dark slate panels"); BOOM, D40 (G) | **MISSING**. Spec (d) new work 1; E22 addendum 7 retired the outline |
| **F18** | Two-layer stroke: a white-hot core over the hue body | 3 | CHN t170 (spec); BOOM, D40 (G "dual-radius") | **PARTIAL**. Spec (d) 6 |
| **F19** | Beveled stamp slab with a drop shadow | 1 | BOOM 14:04 (G) | **PARTIAL**. The stamp exists; s92 adds a resting shadow to props only |

## 4. RECIPE: timed compositions (36 items: 8 HAVE, 24 PARTIAL, 4 MISSING; 19 new)

| id | recipe | n | videos | composes | OURS |
|---|---|---|---|---|---|
| R1 | The hidden base | 1 | BUB 0:00 | T1 + A33 + F2 | **MISSING**. s100 clears the true iceberg |
| R2 | Bar ladder with a membership bar | 1 | BUB 0:48 | T2 + A25 + T3 | **PARTIAL** |
| R3 | **Term / mechanism over (or beside) the held chart** | 4 | BUB 1:59; DOM 08:56-09:29 (the side card moves inward, the plot softens, nodes and tokens); HIS 06:04; JPN 04:08, 05:28 (the beside variant) | A23 + chip + flow (+ A27) | **PARTIAL**. The park form is HAVE; **s98 clears the blur form** over a busy chart plate |
| R4 | Proof walk with press cards at their dates | 1 | BUB 7:22 | T11 + A11 + A19 + A14 + A15 | **PARTIAL** |
| R5 | Push to now, then the unknown | 3 | BUB 8:22; STK 9:01 (lens + dashed "PREPARE!"); BOOM 17:30-17:48 (G) | A18 + A17 (+ A56) | **PARTIAL** |
| R6 | **Cycle model** | **5** | BUB 4:35; STK 1:42-1:50; HIS 04:24-04:40; DOM 07:30, 11:00; BOOM 09:35 (G) | T7 + A55 + A53 + A36 | **MISSING**. C9 |
| R7 | Race to the terminal values, then values leave as bars | 2 | BUB 9:58; CHN 16:45 | A2 + A3 + A12 + A5 | **HAVE**. `chart-recast-into-the-other-form` |
| R8 | Capital loop with money moving | 3 | BUB 11:22; RST 9:30; BOOM 15:10 (G) | T21 + A27 | **MISSING** |
| R9 | Scale-break race | 1 | CHN 7:42 | T16 + A6 + A39 | **HAVE** |
| R10 | Treemap census, then park | 1 | CHN 14:52 | T17 + A38 | **HAVE** |
| R11 | Map lit, stamped, struck | 2 | CHN 9:42; D40 13:54 (G: arcs, origin pulse, zoom to Turkey) | T19 + A32 (+ A27, A37) | **HAVE** (tokens and ping missing) |
| R12 | The rhyme (a node swapped) | 1 | CHN 13:12 | T20 + A31 | **HAVE** |
| R13 | Predictions board | 1 | CHN 1:28 | A28 + T28 | **PARTIAL** |
| R14 | Two verdict panels | 2 | BUB 18:45; STK 10:11 | T26 + A14 | **PARTIAL** |
| R15 | Claim stack on the TV | 2 | CHN 0:04; RST 0:14 | F10 + F9 | **HAVE** |
| R16 | The rig | 1 | BUB 11:58 | A35 + leaders | **PARTIAL** |
| R17 | Dual-lane chart + map ping | 1 | CHN (Gemini 09-10) | park + vecmap + A37 | **PARTIAL** |
| **R18** | **Peak -> fall -> magnitude**: ring the peak, light the falling stretch, land the % at the trough | 4 | STK 0:12-0:18 (ring 0:14, glow 0:16, "-25%" 0:18); HIS 05:58-06:02 ("-70%"); BOOM 13:35-14:20 (G "-81%"); JPN 01:36 (a decline badge per episode) | A8 + A11 + A3 / figure | **PARTIAL**. A11 is missing; `the-decline-drawn-then-undrawn` is a candidate |
| **R19** | Rise, turn, consequence: R18, then the chart dims under a tile, branches draw, checks land | 1 | HIS 05:50-06:07 | R18 + A23 + flow + A14 | **PARTIAL** |
| **R20** | **Raw values -> hold -> bracket -> derived multiple** | 3 | STK 1:54-2:18 (raw values, then 14-16 s, then "6x"); HIS 11:01 ("5x"); D40 11:22-12:06 (G "2x", "4x") | A25 + hold + A15 + figure | **PARTIAL**. T35's `the-ratio-read-in-the-gap` is proposed, not built |
| **R21** | Trace -> endpoint -> guide -> pill | 2 | DOM 00:39-00:50.5; BOOM 00:34-00:41 (G) | A1 + A8 + A9 / A42 | **PARTIAL**. A9 and A42 are missing |
| **R22** | **Epoch walk**: one long line, named eras lit in turn, a clear between each | 4 | DOM 06:11-06:38; BOOM 02:19-03:00 (G: underwater fills, badge swap, both eras boxed); JPN 01:35 (1987 / 2001 / 2007); BUB 7:22 | T11 + A11 + A10 + A20 (+ A44, A45) | **PARTIAL** |
| **R23** | Add the comparison without restarting | 3 | JPN 01:10-01:20; DOM 00:59-01:04; HIS 08:01 | A2 + A43 + A8 | **HAVE** on one scale (`chart_to:extend {series}` + figure); the dual-axis form is C5 |
| **R24** | **Isolate, then quantify the tail** | 3 | JPN 05:25-05:45; STK 4:10-4:14; BOOM 16:38 (G) | A12 + A18 + figure | **PARTIAL**. A12 is missing; `punch-then-callout` is proven |
| **R25** | Formula by spoken order | 1 | DOM 09:30-09:39 | T38 + A60 | **MISSING** |
| **R26** | **Evidence, then the conditional future** (history + named averages, the now lit, then a dashed path in a new grammar) | 3 | STK 7:50-8:24; BOOM 16:15-17:55 (G); JPN 04:05-04:17 (dotted downside before BUY / SELL) | A2 + A11 + A15 + A17 | **PARTIAL** |
| **R27** | Divergence spread: two lines, their pills, the gap fills, a gap bracket | 2 | D40 04:30-04:50 (G); BOOM 08:20-08:50 (G, + echo inset + ?) | A2 + A3 + A47 + A15 | **PARTIAL**. Every part is HAVE; no recipe is written (T35's `estimate-opens-as-a-wedge` is close) |
| **R28** | Bar re-value, then the ratio span | 1 | D40 11:22-12:06 (G) | A48 + A15 | **PARTIAL** |
| **R29** | Negative spike and its glowing trough | 1 | D40 12:46-13:08 (G) | A1 + A46 + A7 | **PARTIAL** |
| **R30** | Ranked dim-the-rest spotlight | 2 | D40 14:22-14:50 (G); CHN t530 | T47 + A49 + A8 | **PARTIAL** |
| **R31** | Scale-out, then the projected overtake | 1 | D40 15:02-15:30 (G) | A50 + A51 | **PARTIAL** |
| **R32** | Today's boom against past booms (rebased cycles, axis pills, the old cycles drawn muted) | 1 | BOOM 00:34-01:25 (G) | T36 + A42 + A2 + A12 | **PARTIAL** |
| **R33** | Lead with the divergence | 1 | HIS 00:00-00:34 | A41 + A3 + A12 | **HAVE**. H row 1 already opens on this chart (`hook-opens-on-the-axes`) |
| **R34** | Doubt -> the budget evidence (a diagram above the bars, the actual row, the source card, the highlighted quote) | 1 | HIS 02:02-02:14 | flow + T18 + F5 | **PARTIAL**. Parts HAVE; the stacked layout is unwritten |
| **R35** | Flow -> the total -> a pointer back (a curved leader, a multiple badge) | 1 | STK 0:02-0:10 | T13 + figure + A15 | **PARTIAL** |
| **R36** | Inset echo, then "?" | 1 | BOOM 08:44-08:50 (G) | T40 + A61 | **PARTIAL**. C16 |

## 5. STYLE: finish rules (11 items: 4 HAVE, 6 PARTIAL, 1 MISSING; 3 new)

| id | rule | n | OURS |
|---|---|---|---|
| S1 | One accent for the subject, white / grey for context | 8 | **HAVE** by ruling (E67 palette) |
| S2 | Framed plot: title, subtitle, unit, top band, source | 8 | **PARTIAL**. The legend band is refused by E53 s8 |
| S3 | Dashed = hypothetical or a grouping; solid = actual | 5 (BUB, STK, HIS, JPN, BOOM) | **PARTIAL**. No dashed projection |
| S4 | White value capsule (pink dot, leader); a dashed ring when it is the answer | 5 | **HAVE** |
| S5 | Story bars: no axis, a category pill | 3 | **PARTIAL**. s97 asks for it |
| S6 | Logos as data labels | 2 (BUB, BOOM) | **MISSING** |
| S7 | Rounded dark icon tiles | 6 | **HAVE**. `chip` |
| S8 | Builds inside a held composition (BOOM 00:34: 8 events in 51 s, G; D40 11:22: 7 events in 44 s, G; CHN 6.0 events/min) | 6 | **HAVE** as doctrine (P49) |
| **S9** | The legend chip turns accent when its series is isolated | 1 (STK 4:14) | **PARTIAL**. s90 badges are the key |
| **S10** | Two-line source "Date: ... / Source: ..., Bravos Research." | 3 (CHN spec, BOOM, D40) | **PARTIAL**. We have a one-line source |
| **S11** | The chart title sits in an accent capsule | 2 (BOOM, D40) | **PARTIAL**. We have a title, not a capsule |

**Totals: 182 items. 73 HAVE, 67 PARTIAL, 42 MISSING. 76 are new: 18 HAVE, 42 PARTIAL, 16 MISSING.** v1 had 106 items: 55 HAVE, 25 PARTIAL, 26 MISSING.

---

## 6. CANDIDATES, re-ranked by frequency x usefulness

- **Score** = n (videos of 9, taking the union of the items a candidate covers) x usefulness (3 = serves several Steel and Paper H body rows or a core act; 2 = one or two rows; 1 = decor or the rare act).
- **Rows** are the H body rows (`REBUILD-TREATMENT-H.md`, rows 7-24) whose own sentence the move would serve.
- Every candidate composes existing cards (s70). "Cleared" means no ruling is needed.

| rank | candidate | covers | n | use | score | composes | H rows (the sentence it serves) | ruling |
|---|---|---|---|---|---|---|---|---|
| 1 | `page_species:lit_stretch` (+ `comet`) | A11, A13, A55 | 8 | 3 | 24 | `build_to` capFrac over [from, to], R26-228 bloom, `relight` | **9** "crashed by nearly two-thirds" (light the fall to −66 %); **14** 23¢ then 28¢; **15** the two eras of the rate line; **21** the +500 % run | cleared by **s99** (a light that travels = motion) |
| 2 | `page_species:solo`: the on-word isolate for lines and bars | A12, A49, S9 | 8 | 3 | 24 | the series `muted` flag as a verb, E67 0.45 history, `emphasized-bar-lit` | **10** chips doubling / customers flat; **16** "bend the bond market" (the tech share); **18** the 20 bar against the 2-4 band; **22** DRAM +17 % vs HBM +14 % | cleared (a mute, not a light) |
| 3 | `page_species:axis_tag` (+ drop guides A42/A43) | A10, A42, A43 | 7 | 3 | 21 | `retitle`'s glyph write + the spring pill on the x tick; `axes.marks` for the guide | **9** "In two thousand the internet crossed seven percent"; **15** "Bank of England above six percent" / the Fed's year; **22** "one soft month in June"; **14** the dot-com peak year | cleared |
| 4 | `page_species:level_join` | A9, R21 | 6 | 3 | 18 | `hlines` stroke drawn A -> B, `ring` dashed at each end, `figure` for the gap | **15** "five and a half" (the Bravos 5.5 tripwire against 6 / 6.5); **14** "twenty-eight, the most it has ever been" against the 23¢ peak; **21** | cleared, but mind C14 (keep the label off the rule) |
| 5 | `recipe:the-ratio-read-in-the-gap` (T35's) + the bracket over a group | R20, A15, A16, R28 | 6 | 3 | 18 | bars + badge-ladder + hold + `bracket` + `figure` | **16** 28 -> 150 (HIS 11:01 is the SAME claim, "5x"); **14** rail 50¢ vs 28¢; **21** "three times the wafer capacity"; **19** 20 years vs 5 | cleared |
| 6 | `dock_option:blur` + `recipe:term-over-the-parked-chart` | A23, R3, A19 | 6 | 3 | 18 | `exit:blurzoom`'s 18 px backdrop blur held under a dock, `park`, `chip`, `flow` | **10** the SELL ticket over the page; **16** "bend the bond market" / the leases record; **11** the Karp record in the slot; **18** "railway certificates" | cleared by **s98** as an option over a busy chart plate. Open: does it reach a ledger-page plot (E63)? See C1 |
| 7 | `plate_option:project` (dashed continuation, a scenario label, optional future box) | A17, T23, A56, R5, R26, S3 | 7 | 2.5 | 17.5 | `chart_to:extend`, the flow nib's dash, `tippill` | **16** "four hundred and eighty… six hundred and ninety" (a consensus forecast); **17** the funding arithmetic; **23** "booked solid through twenty twenty-six"; **22** "The flip" | cleared. It must label itself a projection and carry its tier (E77, s93) |
| 8 | `recipe:the-epoch-walk` | R22, A44, A45 | 5 | 3 | 15 | `span` + #1 + #3 + `marks` (+ a pill text swap) | **9** railway 1840s -> 2000 -> today; **12** three manias; **15** the two eras; **14** 23¢ / 28¢ | after #1 and #3 |
| 9 | `species:chip` states `lit` / `tick` / `sell` | A14, A36, A59, F3, T26, R14 | 7 | 2 | 14 | `chip` (cross exists), `idle:pulse`, `dock_option:badge` | **10** "SELL"; **20-21** the three questions ticking; **22** "Bravos 5.5 / mine" | a held halo is an annotation (s91); a blink is motion (s99) |
| 10 | `recipe:peak-fall-magnitude` | R18, R19 | 4 | 3 | 12 | `ring` + #1 + `figure` at the trough | **9** "crashed by nearly two-thirds" −66 %; **21** "The most vertical line on the board is steel"; **14** | after #1 |
| 11 | `species:loop` + edge tokens | T21, A27, R8, A26 | 6 | 2 | 12 | `flow` ring layout, `stroke.mjs` arc-length tokens | **7** "Capital arriving faster than the value"; **16** who is paying; **17** 94 % debt-funded | cleared |
| 12 | `page_builder:cycle` (a schematic with traced phases and a lag bracket) | T7, R6, A53, A54, A55 | 5 | 2 | 10 | a line from a closed form + #1 + `bracket` | **12** the hype cycle (`ev-three-manias`: peak -> trough) | **C9 needs a ruling** |
| 13 | `recipe:isolate-then-quantify-the-tail` | R24 | 3 | 3 | 9 | #2 + `focus_zoom` + `figure` (`punch-then-callout`) | **14** camera 2 on the 28; **18** camera 3 on the 20; **21** camera 4 on the tip | after #2 |
| 14 | `recipe:the-formula-by-its-words` | T38, A60, R25 | 1 | 3 | 3 | `figure` x3 + `flow` operators | **17** "Ninety-four" (the arithmetic); **23** a fab 5 years / a chip 2x | cleared |
| 15 | `recipe:the-hidden-base` / the true iceberg | T1, A33, R1 | 1 | 3 | 3 | bars below a waterline, or a proportional iceberg (s100) | **16** "another eight hundred and twenty-two billion in lease commitments" | cleared by **s100** for the iceberg |

**Outside the ranking:**
- **The `longform` profile** covers F17 plot panel (6 videos), F18, S2, S5, S10 and S11. It is already P69 T8-T10 (`BRAVOS-LONGFORM-CHART-SPEC.md`), so it is not a harvest verb.
- **Dual axis** (T14, 7 videos) has the highest frequency of any conflict. It needs the operator (C5).
- **The chapter pill** (A34, 1 video) drops from v1 rank 10 to 1 video's worth of signal. Keep it for rows 13 / 18 / 23 only if the operator wants act markers.

**v1 -> v2 movement:**
- `solo` split out of v1 #1 and rose to #2.
- The ratio recipe and the blur option entered the top 10.
- The cycle builder fell (5 videos, but one H row and a ruling owed).
- The hidden base and the chapter tag fell (1 video each).

## 7. CONFLICTS restated under the new rulings

| id | item | under E99 s97-s100 | status |
|---|---|---|---|
| C1 | The chart blurs under an overlay (A23, R3) | **s98**: *"The blur under overlays is a good option to handle our busy chart plates when docking."* An option per row, amending "wash beats the focus rack" only for a dock over a busy chart plate. **Open**: s98 says "chart plate"; E63 (*"a card never READS over a ledger page's plot"*) is not named as amended. Whether a ledger-page plot counts as a chart plate is the operator's call | **CLEARED** for chart plates; ledger page open |
| C2 | Press cards dock onto the plot at their dates (A19, 4 videos) | E63 stands. s98 helps only if the plot blurs under the card | **OPEN** |
| C3 | Composition bar (T3) and the NEW partitioned stacked bar (T29) | s100: *"E53 s2 (never a stacked bar) and E28 (sign is geometry) are NOT changed."* The honest routes are now an AREA form (s100: a proportional block with figures written) or grouped bars / tiers | **STANDS** |
| C4 | Iceberg / pyramid encodes value as area (T1) | s100: area *"is chosen when it tells the story better"*, truthful when (a) *"drawn in true proportion"* and (b) the figures are *"WRITTEN on the page"* | **CLEARED** (under the two tests) |
| C5 | Dual axis, inverted axes, the Fed rate drawn as a series (T14, F15; **7 of 9 videos**) | E53 s4 (*"the line owns no axis, carrying a terminal tag"*), s5 (*"A policy rate is a RULE"*), E75 s3 (*"Never both scales on one reading"*). E79 lets side-by-side panels of unrelated measures carry their own scales (`axes.independent`), which is the honest route. Bravos's opening divergence (HIS 00:00) is dual-axis, and H row 1 draws the same argument | **STANDS**. The frequency is now evidence for the operator |
| C6 | Light as emphasis (A11, F3, F7, the pulsing reticle) | **s99**: *"A highlight that TRAVELS along a length ... or BLINKS counts as motion; a light that comes on as everything else STOPS is a punctuation beat."* s91 still holds for a light that sits (0 events). s71 still holds: a named thing ARRIVES rather than being lit. The freeze-beat has a named-but-unbuilt species, `species:beat_freeze` | **CLEARED** for travelling and blinking light; a sitting light is an annotation |
| C7 | Rings on every vertex (T9) | E56 unchanged. A ring that blinks or travels (A52) now earns motion under s99, but the "rings on everything" objection is about count, not motion | **STANDS** |
| C8 | Neon bloom | Resolved in v1 (R26-228, s83) | **RESOLVED** |
| C9 | Schematic curves with no data (T7, R6; now **5 videos**) | No new ruling. s93 (plausible pages) concerns sourced values; a schematic has none | **OPEN**. The frequency now argues for a ruling |
| C10 | Donuts (T10 decor, T30 3D) | s100 supersedes the donut's four-point exception with two tests. A decor donut fails (b), no figures. A 3D extruded donut fails (a): perspective scales the near slices up. The flat `share` + `peel` passes | **REFINED** |
| **C11** | Continuous push and tracking pan on held charts (A64, A65) | **Disputed evidence**: Gemini claims both in BOOM and D40; GPT saw fixed framing in HIS, DOM and STK and one crop in JPN; C measured 37 of 45 CHN holds still. E59 refuses a continuous push on a held chart; M14 refuses a move over a build | **REFUSED**. Do not adopt on Gemini's word |
| **C12** | Vignette + noise ground (F16) | Gemini-only; the spec measured a flat ground. E22 register (the spec's (c)1) | **OPEN, weak evidence** |
| **C13** | Broken x-axis across eras (T35) | E53 s3: uneven epochs *"never go on a continuous axis"*. A visible `//` break is not a continuous axis, so it needs a ruling; E79 panels with their own x are the existing route | **OPEN** |
| **C14** | A level drawn from a datum (A9 level_join, A45 underwater, A48 ghost levels) | The E53 addendum: *"a value already on the chart is never a reference line"*. The fault ruled there was a LABELLED rule that read as a mislabel. A level_join is a measured span like `bracket`, so it is safe if its figure sits at the datum, not on the rule | **CONSTRAINT** on the build |
| **C15** | Projections (A17, A51, T23) | E77: a derived figure is our layer, set beside outside projections. s93: the tier rides the object. A projected path must say it is one | **CONSTRAINT** |
| **C16** | A card or inset inside the plot's empty room (T40, BOOM 00:44 headline card) | E63 vs E65's placer (*"inside of the empty data would be good"*). s98 covers only the blurred-plate case | **OPEN** |

## 8. Where the reviews disagree (both sources named)

- **Entry order.** GPT HIS: *"data first"*, the trace before the title and axes (00:04-00:06, 05:50). GPT DOM, Gemini BOOM and D40, and Claude CHN: the frame and axes first. Bravos does both. We build only the second (A1 vs A41).
- **Camera.** Gemini BOOM and D40: a constant 1.05-1.10x creep and tracking pans. GPT HIS: *"No pan, tilt, or chart-camera move is evident"*. GPT DOM: *"the camera framing remains fixed"*. GPT JPN: one crop at 05:44. GPT STK: *"Camera motion appears limited"*. Claude CHN: 37 of 45 holds still. Weight the frame-backed watchers (C11).
- **Gridlines.** Gemini BOOM and D40 report faint horizontal gridlines; GPT HIS reports a *"faint horizontal grid"*. The spec measured **0** interior gridlines on CHN t530 / t1078 and BUB 0035. Bravos probably varies by chart. The spec's "0" rests on the CHN / BUB frames only.
- **Ground.** Gemini: a 15-20 % vignette plus noise. Spec: flat, corner = centre (C12).
- **Bar corners.** Gemini D40: *"slightly rounded top corners"*. Spec: radius 0 (CHN t1088).
- **Plot width.** Gemini BOOM: 75-80 % of the screen solo. GPT HIS: *"central 60-75% width"*. Spec: the panel at 43-57 %, and chart plus annotations at 79-94 %. They measure different boxes.
- **Stroke.** Gemini: 3-3.5 px active. Spec: a 4.5 px core at 1080 (CHN t170, t1078).
- **The ping (A37).** Only Gemini has reported it, in CHN (09-10, unverified by v1 frames) and in D40. No GPT or Claude frame shows it.
- **The DOM dashed tail (16:15).** GPT DOM declines to call it a forecast. The other watchers call every dashed tail hypothetical (S3).

## 9. Next watches

1. When `_rwFYNlKtEc` and `cbknsJEshD8` land, fold them in. `_rwFYNlKtEc` would firm up RST's thin v1 read (T14 inverted axis, T21, T23, T24).
2. Verify the Gemini-only timings for BOOM (`jx3Ll-GJtMY` has no frames on disk) before any of R32 / R36 / A44 / A54 / A56 is built from them. D40's frames are on disk (`frames_survey/`, 591), so its items can be checked frame by frame.
3. For lit_stretch (#1), time the travelling glow at 10 fps: STK 0:14-0:18, HIS 05:58-06:03, DOM 06:11-06:24. Is it a pen retrace or a cross-fade, and what is its speed per unit of arc?
4. For axis_tag (#3), check whether the pill replaces or covers the tick: HIS 05:50-05:54, JPN 01:14-01:17.
