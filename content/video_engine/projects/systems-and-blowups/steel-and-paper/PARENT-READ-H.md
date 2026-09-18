# The parent's read of the 1:30 unit (P68 T5) - H's frames beside build-f's, 2026-09-18

The sheets: `build-h/self-watch/opening.1-4.png` (0:00-1:30 at 2 s steps, the FINAL scratch take, 13:58) against
`build-f/frames-review.png` (the shipped cut's own review sheet) and `build-f/SHOT-TABLE-F.md` rows 1-11.

## First pass (the build lane's first rebuild) - what a viewer sees

| instant | H | build-f at the same sentence | read |
|---|---|---|---|
| 0:00 | the ledger page on its axes from frame one, Bravos' two lines drawing, the caption in STAGE mode on the charcoal | `world-spike-desk-v1` bare for 11.8 s, "An iron spike." | E73 answered; the opening minute is no longer the thinnest |
| 0:10-0:16 | the 1845 certificate thrown into the plot's low-right room; the caption "This certificate" lands ON the card at 0:10 | `world-broadcast-set-v2`, no dock | the arrival is right (s71); the landing spot is a collision - FIX 6 |
| 0:18-0:30 | "Hold an index fund" / "AI is 1845 again" written OVER the page's terminal tags (+105% SEMICONDUCTORS, +613% MEMORY MAKERS) | `world-two-rooms-divergence-v1` + the chart card small in a corner | the 16:9 STAGE caption and the page's tags share the right half - a collision at seven instants - FIX 1 (and R26-205's engine order underneath it) |
| 0:30 | the plain recast to the three lines - the old +21% MAMAA over the new +21% S&P 500 for one beat (M28/M34) | `world-dawn-factory-v1` + the same card held 21.3 s | the recast is the right move (E58); the label hand-over is the engine's, not the table's - stays named on the card |
| 0:36-0:40 | the +613 figure on the memory line; "Memory, six hundred and thirteen" beside it | — | the camera at 1.06 holds the title on stage; the 1.32 focus_zoom cut it (departure 8) |
| 0:42 | a ring on the S&P tip at "The address is wrong" | — | the WRONG line - the mark cannot reach series 2 (departure 2); a light on the wrong thing is worse than none - FIX 2 |
| 0:44-0:54 | the page parks top-left, the numbered agenda lands row by row under it, "your top five" as a note | `world-three-notch-slate-v1` bare 8.4 s, then the nib | the beat that reads best in the unit; the park IS the breath (E61) |
| 0:56-1:06 | Mike at the studio desk (the Flow plate as the world); the Bravos card thrown BIG over his face; the flow `capital -> value` drawn on the dark monitors | `world-hype-machine-v2` / `world-assay-sort-v1`, no host | the host window works; the card must take the desk's clear left third, never the face - FIX 4/5 |
| 1:08-1:22 | the railway index page on its axes, the 1843 level dashed, the line climbing on "quarter-billion", the -64% trough tagged "741 railway share prices" | `world-steelman-build-v1` bare 11.5 s, then the navvy plate + the card | the chart proves its sentence; the figures are the object's (-64 %, not the treatment's -66) |
| 1:24-1:30 | the recast to the GDP page - the railway notes and the 741 tag still on it; the caption says "seven percent", the page's peak reads 11.54 % | `world-dotcom-server-room-v1` + `ev-equip-ipp-gdp-v1` | stale ink after a chart_to (departure 4) - FIX 3; the measure on screen is not the measure in the sentence - FIX 7 / HG3's evidence question |

## The two readings that are the operator's, not mine

1. **The balance of chart-world to plates.** build-f is a picture book: eleven plates in its first 1:30 with a dark
   chart card docked small in a corner. H's unit is one plate in 1:30 with the chart as the world. E61 rules the
   chart is the world by default, and the same ruling says the plates are "visual grounding and our channel
   differentiation". The unit is the E61 default taken literally; the card asks whether the balance holds for a
   long form or whether the body wants a bridge plate every 40-60 s (E61's second use).
2. **The 16:9 page is half a stage.** Every page in the unit draws its plot in the LEFT half and keeps the right
   half quiet for the STAGE caption. The anchored bottom strip constant exists (`ledger_page.py:1159`) and nothing
   routes a page row's caption there; with it, the plot would take the whole stage as Bravos' do. That is
   R26-205's engine order made visible - the operator's call on whether the half-stage page ships once.

## The evidence question for HG3

- The 7 % / 8 % of GDP in P11 ("the internet crossed seven percent of GDP... AI spending just crossed eight") are
  Bravos' arithmetic; `ev-equip-ipp-gdp-v1` (BEA, equipment + IP share of GDP) peaks at 11.54 %. The dossier routes
  the sentence to the PIMCO series (`evidence/EVIDENCE-DOSSIER.md:120`). Either the page shows the measure the
  sentence names, or the sentence rides the railway page with no chart under it. Never a chart that contradicts
  the words on top of it.
- `ev-bravos-original-v1` is `SOURCES-TO-VERIFY`: its two end figures equal the verified divergence object's; what
  is unverified is the claim that the pairing is Bravos' own.

## Second pass (the rebuild with the seven fixes) - read on the re-shot sheets

- 0:00-0:16 clean: the page on its axes, the line drawing, the certificate card in the plot's low-right room with the
  caption clear of it (0 px at 10.06 and 12.21 s); the ring at 6 s gone.
- 0:16-0:44: the page PARKS to 0.64 the instant its last line is drawn and stays parked through the recast, so
  the terminal tags and the STAGE caption never meet (0 px at every measured instant; 7,020 px on the first
  pass). The cost: the chart reads small, top-left, for thirty seconds. At 0:30 the arriving chart draws full and
  tucks itself over the next two seconds - it should arrive tucked (a build-side note for T6, not a collision).
- 0:42 the wrong-line ring gone; 0:44-0:54 the park + the agenda unchanged (the beat that reads best).
- 0:56-1:06 the host window: no card over Mike - `dock_place` returns None on a picture plate, so a card on a
  plate cannot be placed at all (departure 10, R26 row owed); the caption back in STAGE mode at full size over
  the desk (white on luma 43-51); the crossed-out chip and the `capital -> value` flow on the dark monitors.
- 1:08-1:32 the railway page holds to the unit's end; the GDP page is NOT shown under "seven percent" (the
  object on disk measures a different thing - HG3's evidence question); the notes stay on the page that wrote
  them.
- Gates: M34 1 FAIL (the recast's own hand-over instant - the engine's, named), M11 FAIL by name (a ring on
  nothing is worse than an unannotated first chart), 3 WARN argued; no frozen frame over 0.5 s; every plate
  names its use. The frozen copy `build-h-frozen-a/` is served on :8775 and is the copy the card shows.

## Third pass (the critic's three closed) - read on the re-shot sheets; frozen copy b on :8776

- The open is the VERIFIED `ev-divergence-v1`, one page for 54 s, the memory line STAGED on it: at 26 s three
  lines (semis +105 %, S&P +21 %, mega-cap +21 %) and no memory tag; at 32 s the memory line at +613 % with the
  object's own "our layer" badge and the spread filling the gap beneath it - a stage change on the same page, no
  recast, no label hand-over (the last motion FAIL went with it). The 0:24 card is a still of the same verified
  page. `ev-bravos-original-v1` (SOURCES-TO-VERIFY) is cited nowhere in the cut.
- The railway line climbs from the dip at 68-72 s and takes the peak on "quarter-billion"; the axes are never
  bare past ~2 s. The cut ends on "eight." at 92.77 with no orphan caption.
- Gates: 0 FAIL / 3 WARN (M04 three plates against a target of seven - the point; M21 the page past its last
  data mark - E50's "becomes the next thing"; M25 two card FLIGHTS graze the bottom band, both landings clear);
  no frozen frame over 0.5 s; every plate names its use; the receipt PASS 12/9.
- What a viewer still sees and the operator judges: the chart at two-thirds size from 0:10 to 0:44 (the 16:9
  page keeps the right third for the caption - R26-205); the railway page holding under "seven percent of GDP"
  with no chart of that measure (the object on disk measures a different thing); one plate in ninety seconds
  against build-f's eleven.

## Fourth pass (the hook's scale) - frozen copy c on :8777, the copy the card shows

- The hook's two lines now fill the plot: a `chart_to rescale` with a per-state y domain fires on "Not the chips"
  (0:04) and the axis opens to the memory line's range on "Here's the layer" (0:30) - the operator's own rescale
  mechanic, found in the kit. Every hook line is staged, so each end tag lands with its own line at 0:17-0:18 and
  the memory tag at 0:31; nothing prints at 0:03. Ink height in the plot: 13 % -> 28 % at 0:02, 23 % -> 57 % at
  0:16, 98 % at 0:31.
- The first four seconds still stand on the object's own scale: a page cannot be born with a domain (departure
  11, an engine row) - the residue the operator weighs against a second object.
- The one motion FAIL is M28 on the rescale's tick hand-over: a y-only rescale re-draws the same x ticks at the
  same coordinates and the gate reads a label on an identical copy of itself as a collision. Read on the frame at
  5.2 s: the ticks are clean. An engine row, named on the card, not a table fault.

## Fifth pass (the critic's copy-c three) - frozen copy d on :8778, the copy the card shows

- The 0:24 card is now rendered from a DERIVED two-line object (the verified object with the staged series
  dropped, every number copied, none typed): at 26-28 s the card carries the two lines and nothing on screen knows
  about the memory line until 0:30. The payoff is kept.
- The reveal: the park is released 0.9 s before the rescale and the hand-over is 1.0 s; the chart box is stable
  through it (989 -> ~1090 as the page un-parks), and the label peak (16 for 0.7 s) is the engine's own axis
  hand-over writing the arriving axis before the standing one leaves (R26-222's door).
- The hook's y axis prints two ticks (80, 160) with no line clipped; 100 cannot be a tick without clipping the
  mega-cap line's low of 93.94, so the baseline stays in the y label's words.
- Read on sheet 2: 0:24 the two-line copy card, 0:28 the retitle, 0:30 the page un-parking and the axis opening
  as the memory line draws, 0:34 the spread, 0:38-0:40 the +613 % figure, 0:44 the agenda. Clean.

## Sixth pass - THE 30-SECOND BED on every door (E99 s82; read on `build-h/self-watch/bed.png`, eight tiles)

The doors under it: R26-218/219 (marks name their series; species leave with the page), R26-221/223 (the card's
box; the page born on `;domain=80,277`), R26-228 (the interior lives - the lead points, the bloom, the per-word
breath), R26-205 (the page IS the plate at 16:9; the caption in the anchored strip), R26-226 (`;build=lines:1.2`
- each line whole, then its tag and badge; a series held at 0 takes no turn).

- 0:02 the page full stage on its own scale (ticks 80 / 160), the semis line already drawing whole; 0:06 the
  three hook lines landed with their tags and badges (semis at 1.20 s, mega-cap 2.40, S&P 3.60) - no crawl;
  0:12 the certificate in the plot's low-right room, small, 0 px on the ink, the tags and the caption; 0:18 gone.
- 0:24 three lead points, one per landed line, each with its bloom; the caption in the anchored strip.
- 0:30 "AI is 1845 again" - the axis opens to 640 as the memory line draws whole on "Here's the layer"; 0:38
  +613 % and the crimson spread. The reveal is the one rescale left and the words name it.
- The type at 16:9 in CSS px: caption 14.6, title 17.4, end tags 14.2, ticks 13.0 (doc 49's floor 12) - the
  first time the page's type has cleared the phone rule; source 11.3 and sub 10.8 under it.
- 0:46 ONE COLLISION: the agenda's rows land over the parked page's end tags. Sent back as R26-229's shape (the
  chart melts to a ball and is tossed, the agenda centred on the board, no park).
- The gate: 4 FAIL - M11 (the first chart unannotated: the only mark the engine aims lands on series 0, the
  held memory line) and M05/M10/M16, the pulse rows reading 27 events where the old cut counted 243 - the
  anchored caption counts as nothing and the staging is gone while the page's life runs (R26-232, a gate row).
- What the operator judges: the card on a full-stage page is small (230 x 210); the page's own title names
  "the layer it needed" 28 s before the reveal (the object's title - a retitle at the open is the fix); the caption
  at 33 px in the strip (E62 - on the card); the plot at 49.9 % of the stage width (the end tags' reach - on the
  card).

## Seventh pass - the bed with the melt-toss agenda (frozen copy e on :8780, the copy the card shows)

- 0:46: the page melts to a ball and is thrown off on "One test"; the slate plate (build-f's own
  `world-three-notch-slate-v1`) is the world by "three questions"; the agenda lands centred on the slate's three
  notches, one row per word, 0 px on any ink or tag (there is none left), 32 px clear of the STAGE caption. No park
  anywhere in the bed. The rows' type reads small on the slate - the operator's eye.
- The gate: 48 visual events (from 27); M16's 0:44 gap gone with the park; the four FAILs unchanged and all in the
  page's first 20 s (M11 the first chart unannotated; M05/M10/M16 the pulse rows over the anchored caption -
  R26-232).
- Two rows, idle 2/2; the slate's drift paints now that the dial is on.

## Eighth pass - frozen copy f on :8781, the copy the card shows

- The melt is in the cut: the page melts to a ball over "One test" and splashes onto the slate (`melt:splash:plate`
  on the slate row's exit - the law: a row's exit is the move INTO it), no black core (luma 52 at the ball, 122 on
  the slate); the three questions on the slate's notches by "three questions". The certificate shows its face at
  0:12 (`CERT_CROP` 282 x 238 at 296,146 on the plate). The reveal's rescale runs on the memory line's own 2.2 s
  clock; the landed lines still slide (253 px over 2.2 s, from 215 px/s) - R26-233's door.
- Read on the tiles: clean at every instant; the slate's three-question type reads small - the operator's eye.
