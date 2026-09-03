# SURFACE CENSUS — Steel and Paper, build-f

P35 T0 census. Doc 29 §9.28 (the SURFACE GRAMMAR) applied to every row of
`SHOT-TABLE-F.py` (`W`, imported with Python — numbers are the table's, not retyped).
Date: 2026-09-03. Classifies surfaces only; no data values are invented here.

Gate run (`gate_motion_density.py build-f --timeline steel-and-paper.timeline.json`), verbatim:

    RESULT: 4 FAIL / 1 WARN / 2 PASS / 2 JUDGE / 1 INFO

ep1 baseline: **4 FAIL** (M01 11 stretches > 12s = 23% of runtime, worst 34.6s at 12:05;
M03 197s evidence gap from 10:09; M05 4 plates held > 20s; M07 opening minute rank 5/14 from the bottom).

**Clock caveat (finding).** The gate reads `build-f/evidence-dock.json` and `motion-plan.json`
for dock/cue events, and both sit on an older clock than `steel-and-paper.timeline.json`:
`ev-divergence-v1` docks at 26.40 in evidence-dock.json, anchored on *"The giants are the market now"*,
which the timeline speaks at 49.5–51.3 and docks at 50.4 (scene s05). The dock file also carries assets
the shot table no longer uses (`ev-mechanism-ladder`, `ev-instrument-memory`, `silicon-antidote-s02-valuation-bubble-v1`).
So the M01/M08 stretch list is partly wrong for this build. The table therefore carries BOTH:
`gate` = the gate's printed stretch (what the task asked for), `tl` = the same computation
(scene bounds + scene-dock enter/exit) on the timeline's own scene docks. On the timeline clock there are
**20** stretches > 12s (gate says 11) and 48 > 8s (gate says 30). Still = `Y` overlaps a gate M01/M08 stretch;
`Y*` only the timeline clock shows > 12s; `y*` timeline shows 8–12s only; `N` neither.

## Legend (§9.28, short)

- **A1** the proof is ours — we ran/pulled/drew it, the VO says so in first person, a `series.json` with our source sits beside the asset (a re-plot of their chart is theirs).
- **A2** carried by a series we own — exact values, labels aligned, source present. No series, no page.
- **A3** lands at a turning beat (mini-payoff, catalyst close, P3's best evidence, the pivot's THEREFORE, payoff, tell, ring close) or fills an M01/M08 still with no dock inside 12s.
- **B1** their evidence always docks (chart, document, quote, stamped slide, record).
- **B2** our proof docks when the beat does not turn (supporting number, second view, tile beside a page).
- **B3** a dock may land on a page, in its quiet zone, never over the emphasized datum.
- **B4** theirs-but-we-extend (the divergence): pages only where the VO claims our layer; 'here's the original' docks.
- **C1** leaving a page: same proof continues → beat-freeze exit; topic changes → s9.15 wipe. Never a fade.
- **C2** dock on a page enters in the quiet zone with carried light; datum stays uncovered.
- **C3** one camera move per window; on a page, Ken Burns is a slow push only.
- **C4** the pivot's reversal takes no species; a page fires only on the THEREFORE after it.
- **C5** a page holds like a plate: 20s ceiling; build counts as events; past 12s of hold it needs a dock, plate life, or stage captions.
- **C6** entering a page: bare plate → roll-out is the transition; dock-bearing plate → the dock exits first.
- **D1** no window > 12s without a dock, a page build, or plate life.
- **D2** evidence enters at least every 45s per phase; a page start counts.
- **D3** the opening minute is never the thinnest; a P1 page only under (a) — the mini-payoff chart is the default candidate.
- **D4** stage captions cover what (a)–(c) leave bare — the floor, not the plan.
- **<12s** the NONE surface's own condition (bare plate + Ken Burns under 12s, or a savor / pivot beat).

## The table — 75 rows, one per `W` window (`len(W) == 75`)

Surface verdicts are for the re-script's shot table; `(cand.)` marks a PAGE the census supports but that needs a re-script condition named in the rules cell (A1* VO claim, A2* series). `(held)` = a dock that entered in an earlier row and is still up; held docks with no event past 12s cite D4. Builder is by data shape (§9.28: builder and surface are independent axes).

| # | start–end | plate | beat | docks today (asset: ours/theirs) | still today? | SURFACE | builder | rules |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.0–7.7 (7.7s) | `world-spike-desk-v1` | P1 hook - the spike, ring token plants | — | N · gate — · tl — | none | — | <12s (hook; ring token) |
| 2 | 7.8–16.6 (8.8s) | `world-adviser-signature-v1` | P1 their chart - 'fourth version of the same chart' | `ev-bravos-original-v1` theirs (9.5–50.4) | Y · gate 8.9s@7.8 · tl — | dock | dense-line | B1 (their re-plot, A1 names it) |
| 3 | 16.7–29.1 (12.4s) | `world-share-office-queue-v1` | P1 the copies - 'nobody checked the original's math' | _bravos held over from #2 (9.5–50.4)_ | Y · gate 9.7s@16.7 · tl 12.4s@16.7 | dock (held) | — | B1 D4 (held dock, no event 12.4s) |
| 4 | 29.1–50.4 (21.3s) | `world-gpu-crate-dock-v1` | P1 'here's the original' - credit; 'we drew the index underneath' | _bravos held over (to 50.4)_ | Y · gate 8.1s@33.9, 8.4s@42.0 · tl 21.3s@29.1 | dock (held) | — | B1 B4('here's the original'→dock) D4 C5(21.3s>20s hold, M05) |
| 5 | 50.4–57.3 (6.9s) | `world-statement-kitchen` | P1 mini-payoff opens - S&P line, semis +105 | `ev-divergence-v1` B4 pair: their 2 lines + OUR layer (50.4–70.9) | N · gate — · tl — | dock | dense-line | B4 (their pairing side) B2; C6 dock exits before #6's roll-out |
| 6 | 57.3–71.3 (14.0s) | `world-three-notch-slate-v1` | P1 MINI-PAYOFF - 'one layer Bravos never drew': memory +613; 'wrong address' | _divergence held over from #5 (to 70.9)_ | Y · gate 14.0s@57.3 · tl 13.6s@57.3 | **PAGE** | dense-line | A1(B4 our layer, 'never drew') A2(series x4/235) A3(mini-payoff + M01 14.0s) D3(P1 default candidate) C1(wipe: #7 changes topic) |
| 7 | 71.3–86.0 (14.7s) | `world-signature-nib-v2` | P1 promise - one test, three questions, 30s a stock | — | Y · gate 13.7s@71.3 · tl 14.9s@71.3 | plate-life (cand.) · today DEFECT | — | D1 D4 - cutouts: nib lowers, three ink marks stepped in |
| 8 | 86.2–92.2 (6.0s) | `world-hype-machine-v2` | P1 the opponent - the hype machine | `silicon-reality-gap-s04-teacher-stamped` theirs (86.8–92.2) | N · gate — · tl — | dock | — | B1 (stamped slide) |
| 9 | 92.2–97.0 (4.8s) | `world-assay-sort-v1` | P1→P2 'a machine you can test' | — | N · gate — · tl — | none | — | <12s |
| 10 | 97.2–104.2 (7.0s) | `world-steelman-build-v1` | P2 catalyst opens - Bravos' case at full strength | — | N · gate — · tl — | none | — | <12s |
| 11 | 104.2–113.6 (9.4s) | `world-navvy-cutting-v1` | P2 railways 1840s: £¼bn, -⅔ ; tile ~7% GDP | `ev-railway-index-v1` theirs-data, we drew (104.2–113.6); `ev-railway-gdp-tile-v1` theirs-data (112.5–122.1) | y* · gate — · tl 8.3s@104.2 | dock | decline + story | B1 (C&T index + tile; their data) |
| 12 | 114.0–121.9 (7.9s) | `world-dotcom-server-room-v1` | P2 dotcom 7% of GDP; 'AI just crossed eight' | _railway tile held over from #11 (to 122.1)_ | N · gate — · tl — | dock (held) | — | B1 |
| 13 | 121.9–143.8 (21.9s) | `world-ledger-page-v1` | P2 'I pulled their yardstick myself' - the build | `ev-capital-formation-v1` OURS (122.1–172.2) | Y · gate 8.2s@121.9 · tl 21.9s@122.1 | **PAGE** (build) | dense-line | A1('I pulled… I ran it') A2(series x2/226, BEA/FRED) A3(catalyst's close; M05 22s hold w/ 1 dock) C6(tile exits first) C5(page hold >20s across #13–#15: split) |
| 14 | 144.0–161.7 (17.7s) | `world-pressure-gauge-v1` | P2 CATALYST CLOSE - 23¢ → 28¢, 'the most it has ever been' | _capital-formation held over from #13 (to 172.2)_ | Y · gate 13.5s@148.2 · tl 17.7s@144.0 | **PAGE** (hold · 28¢ lands) | dense-line (story callout: ½ / 23¢ / 28¢ / 65¢) | A1 A2 A3(28-cent payoff, PRP-named) D4(17.7s still under a held chart) C5 |
| 15 | 161.7–173.7 (12.0s) | `world-viaduct-train-rain-v1` | P2 'closest run in 180 years' - new instrument; trigger enters at 172.3 | `ev-tnx-two-eras-v3` theirs-argument, we drew (172.3–190.4) · _capital-formation held (to 172.2)_ | Y · gate 12.2s@161.7 · tl 10.5s@161.7 | page → C1 wipe | dense-line | B2(tnx: their argument) C1(topic turns to rates at 172.3 → s9.15 wipe) C6 |
| 16 | 173.9–204.3 (30.4s) | `world-broadcast-set-v2` | P2 the trigger - BoE 6%, Fed 6.5%, tripwire 5.5; 'don't call the top' | _tnx held over from #15 (172.3–190.4), then bare 190.4–204.3_ | Y · gate 9.4s@173.9, 9.4s@183.4 · tl 16.5s@173.9, 13.9s@190.4 | dock (held) → plate-life (cand.) · bare 13.9s DEFECT | dense-line | B1 D1 D4 C5(30.4s window, M05: split) |
| 17 | 204.3–218.3 (14.0s) | `world-sell-ticket-v1` | P2→P3 the obvious move - take profits | — | Y · gate 9.9s@204.3 · tl 14.6s@204.3 | plate-life (cand.) · today DEFECT | — | D1 D4 - cutouts: the sell ticket stamped, torn, pinned |
| 18 | 218.9–226.4 (7.5s) | `world-trading-desk-dark` | P3 open - 'their own chart gets strange' | — | N · gate — · tl — | none | — | <12s |
| 19 | 226.6–231.1 (4.5s) | `world-internal-memo-v1` | P3 u1 Karp on CNBC | `ev-doc-karp` theirs (226.6–235.3) | N · gate — · tl — | dock | — | B1 (record) |
| 20 | 231.1–235.3 (4.2s) | `world-budget-burndown-v1` | P3 u1 'something has gone completely wrong' | _karp held over (to 235.3)_ | N · gate — · tl — | dock (held) | — | B1 |
| 21 | 235.3–244.6 (9.3s) | `world-empty-racks-v1` | P3 u1 Uber burned the budget by April | `ev-uber-adoption-v1` theirs (235.5–252.0) | y* · gate — · tl 9.4s@235.5 | dock | — | B1 (quote card) |
| 22 | 244.9–253.8 (8.9s) cut | `world-exhibition-hall-morning-v1` | P3 u1 COO: 'can't draw a line to what you're shipping' - the trough | _uber held over (to 252.0)_ | Y · gate 9.0s@244.9 · tl — | dock (held) | — | B1 |
| 23 | 253.9–265.4 (11.5s) | `hero-countercase-v1` | P3 u1 the trough doing its job - three manias | `ev-three-manias` ours-authored table (254.1–265.6) | y* · gate — · tl 11.3s@254.1 | dock | — | B2 (ours-authored table, no series → A2 fails) |
| 24 | 265.4–277.4 (12.0s) | `world-dawn-factory-v1` | P3 u1 what survives - 1849 the steel; trains ran through the crash | _three-manias exits 265.6_ | Y* · gate — · tl 12.2s@265.6 | plate-life (cand.) · today DEFECT (12.0s) | — | D1 D4 - cutouts: a train crossing the works, stepped; smoke plumes |
| 25 | 277.8–281.4 (3.6s) | `world-molten-pour-v2` | P3 u1 rehook - 'who's paying for the steel this time' | — | N · gate — · tl — | none | — | <12s (rehook breath) |
| 26 | 281.5–290.5 (9.0s) | `world-treasury-cash-count` | P3 u2 out of pocket - 'the whole flex' | — | y* · gate — · tl 9.0s@281.5 | none | — | <12s |
| 27 | 290.5–295.6 (5.1s) | `world-bond-prospectus` | P3 u2 borrowing $28bn/yr | `ev-debt-issuance-v2` theirs (290.7–300.9) | N · gate — · tl — | dock | — | B1 |
| 28 | 295.7–300.9 (5.2s) | `world-index-board-swelling` | P3 u2 $121bn → $150bn | _debt-issuance held over (to 300.9)_ | N · gate — · tl — | dock (held) | — | B1 |
| 29 | 300.9–317.8 (16.9s) | `world-substation-feed-v1` | P3 u2 IG index 9% → 10% → 12+ | `ev-ig-credit-weighting-v1` theirs-data (301.0–317.7) | Y* · gate — · tl 16.7s@301.0 | dock | story | B1 D4 (held 16.7s, no event) |
| 30 | 317.8–326.3 (8.5s) | `world-datacenter-aisle-v1` | P3 u2 capex consensus 480 → 690 | `ev-capex-consensus-v1` theirs-data (318.2–327.6) | y* · gate — · tl 8.1s@318.2 | dock | story | B1 |
| 31 | 326.3–330.1 (3.8s) | `world-lease-contracts-bound` | P3 u2 'faster than the year went by' | _capex-consensus held (to 327.6)_ | N · gate — · tl — | dock (held) | — | B1 |
| 32 | 330.1–338.3 (8.2s) | `world-datacenter-shell` | P3 u2 $822bn leases | `ev-doc-leases` theirs (330.1–348.8) | y* · gate — · tl 8.2s@330.1 | dock | — | B1 (record) |
| 33 | 338.3–348.8 (10.5s) | `beat-05-017-018-market-prices-cashflows-v1` | P3 u2 'not hidden - right there in the filing' | _leases held over (to 348.8)_ | Y · gate 10.5s@338.3 · tl 10.5s@338.3 | dock (held) | — | B1 |
| 34 | 348.8–360.1 (11.3s) | `beat-05-006-listed-cash-flow-market-v1` | P3 u2 PIMCO: 94% of operating cash | `ev-doc-macdonald` theirs (349.0–367.7) | Y · gate 11.3s@348.8 · tl 11.1s@349.0 | dock | — | B1 (record) |
| 35 | 360.1–369.6 (9.5s) | `world-orderbook-stamped-v1` | P3 u2 BEST EVIDENCE - 'spending all of it, borrowing the difference' | `ev-capex-funding-v1` ours-drawn, unclaimed (368.5–385.3) · _macdonald held (to 367.7); capex-funding enters 368.5_ | N · gate — · tl — | dock | combo | B2 (A1 fails: Epoch aggregation, VO never says 'I pulled the filings'; A3 would hold - P3's last unit) → page only if the re-script claims the pull |
| 36 | 369.6–383.6 (14.0s) | `world-signature-close` | P3 close - 'they signed a promise in a year that looked good' | _capex-funding held over (368.5–385.3) - covers the whole window_ | Y* · gate — · tl 14.0s@369.6 | dock (held) | combo | B2 D4 (14.0s held, no event) |
| 37 | 383.6–391.9 (8.3s) | `world-license-cabinet-v1` | P4 setup - 'the part nobody is charting' | — | N · gate — · tl — | none | — | <12s |
| 38 | 391.9–399.6 (7.7s) | `hero-wrong-bubble-v1` | P4 REVERSAL - 'the bubble isn't in the steel, it's in the paper' | — | y* · gate — · tl 8.4s@391.9 | none | — | C4 (reversal takes no species; register shift is the motion) <12s |
| 39 | 400.3–406.0 (5.7s) | `world-certificate-wall-v1` | P4 therefore - railway certificates | `ev-railway-mileage-v1` theirs-data (400.7–410.2) | N · gate — · tl — | dock | story | B1 (Jackman bars) |
| 40 | 406.0–410.0 (4.0s) | `world-exchange-floor-1845` | P4 therefore - 'priced off the best year' | _mileage held over (to 410.2)_ | N · gate — · tl — | dock (held) | — | B1 |
| 41 | 410.0–427.9 (17.9s) cut | `world-target-date-envelope-v1` | P4 THEREFORE - 1845 vs 2026: AI builders 20% of S&P, historically 2–4 | `ev-weight-check-v1` OURS (410.2–428.3) | Y · gate 18.5s@410.0 · tl 18.1s@410.2 | **PAGE** (cand.) | story | A1*(card: 'We checked'; VO says 'Bravos' own number' - re-script must claim the check) A2(shares x2, SCML ledger) A3(pivot's THEREFORE + M01 18s) C6(mileage exits first) C1(freeze exit: #42 continues the proof) |
| 42 | 428.5–438.2 (9.7s) | `hero-sp500-double-failure-v1` | P4 therefore - fall by half → -10% of 'the market' | `ev-smh-drawdown-v3` ours-drawn, unclaimed (428.5–438.8) | y* · gate — · tl 9.9s@428.5 | dock | decline | B2 (second view of #41's proof) B3 (may land on the page, quiet zone) |
| 43 | 438.4–445.0 (6.6s) | `world-spike-certificate-ring-v2` | P4 savor - ring token: 'the spike was never the risk' | — | N · gate — · tl — | none | — | <12s (savor holds its picture, s9.25 #3) |
| 44 | 446.0–457.3 (11.3s) | `world-railway-acts-desk-v1` | P4→P5 '1845 is the proof' - the rails worked, paper lost ⅔ | `ev-railway-index-v1` theirs-data, we drew (446.2–457.5) | y* · gate — · tl 11.3s@446.2 | dock | decline | B1 (C&T index returns) |
| 45 | 457.8–468.9 (11.1s) cut | `world-circuit-terrain-v1` | P5 'skips a gear' - steel sat 20 years; compute depreciates in 5 | `ev-railway-mileage-v1` theirs-data (458.1–468.9) | y* · gate — · tl 10.8s@458.1 | dock | story | B1 (mileage returns) |
| 46 | 468.9–473.9 (5.0s) cut | `world-hbm-die-stack` | P5 sold out into next year | `silicon-antidote-s11-teacher-stamped` theirs (468.9–473.9) | N · gate — · tl — | dock | — | B1 (stamped slide) |
| 47 | 473.9–509.9 (36.0s) cut | `hero-korea-italy-v1` | P5 PAYOFF - sovereign stacks, then THE TEST read aloud (59–63%) | `sovereign-memory-infrastructure-s10-teacher-stamped` theirs (473.9–488.7); `ev-test-scorecard-v1` OURS (492.3–543.0) | Y · gate 8.1s@478.4, 16.3s@487.4 · tl 14.8s@473.9, 18.5s@492.3 | dock → **PAGE** (cand.) at 'Now the test' ~488 | story (three questions as bars) | B1(sovereign slide) then A1(ours) A2(checklist series; T2 must accept non-numeric rows) A3(payoff delivery + M01 16–18s) C6(slide exits first) C5(36.0s window, M05: split) |
| 48 | 510.8–522.9 (12.1s) | `hero-barbell-v1` | P5 'check all three from your phone' | _scorecard held over from #47 (492.3–543.0)_ | Y* · gate — · tl 12.1s@510.8 | dock (held) | story | B2 D4 (12.1s held, no event) - plate-life alt.: gold block / paper slip dropped on each pan |
| 49 | 522.9–532.8 (9.9s) | `beat-04-014-evidence-hierarchy-v1` | P5 cash flow + share count | _scorecard held_ | y* · gate — · tl 9.9s@522.9 | dock (held) | story | B2 |
| 50 | 532.8–543.4 (10.6s) | `world-workbench-triad-v1` | P5 'steel answers scarce, cash, used' - run your top five | _scorecard held (to 543.0)_ | y* · gate — · tl 10.2s@532.8 | dock (held) | story | B2 |
| 51 | 543.5–552.6 (9.1s) | `world-two-rooms-divergence-v1` | P5 the divergence re-read - our chart RETURNS | `ev-divergence-v1` B4 pair: their 2 lines + OUR layer (543.6–560.8) | y* · gate — · tl 9.0s@543.6 | dock | dense-line | B2 (second view of the #6 page) |
| 52 | 552.6–559.7 (7.1s) | `beat-04-015-bottleneck-boom-v1` | P5 'the test, administered in public' | _divergence held (to 560.8)_ | y* · gate — · tl 8.2s@552.6 | dock (held) | — | B2 |
| 53 | 560.8–570.0 (9.2s) cut | `world-seoul-fab-skyline-v1` | P5 SK hynix - 'the most extreme number' (overlaps #54 564.5–570.0) | — | Y* · gate — · tl 13.9s@564.8 | none → dock | — | <12s; row overlap with #54 is a shot-table defect to fix in the re-script |
| 54 | 564.5–577.6 (13.1s) cut | `hero-fab-constraint-v1` | P5 hynix +500% - 'if anything is a bubble, it should be that' | `ev-krx-memory-v3` ours-drawn, unclaimed (564.8–578.7) | Y* · gate — · tl 13.9s@564.8 | dock | dense-line | B2 (ours-drawn, VO not first-person) D4 (13.9s held) |
| 55 | 578.9–585.1 (6.2s) | `hero-hbm-bandwidth-v1` | P5 HBM physics - dies stacked | `silicon-reality-gap-s07-hbm-stack-v1` theirs (579.2–585.1) | N · gate — · tl — | dock | — | B1 (stamped slide) |
| 56 | 585.1–595.2 (10.1s) | `world-dram-terrain-v1` | P5 3× wafer per GB | `ev-hbm-wafer-ratio-v1` theirs-data (585.1–595.2); `silicon-antidote-s09-capacity-penalty-v1` theirs (589.1–595.2) | Y · gate 9.1s@585.1 · tl — | dock | story | B1 (tile + slide) |
| 57 | 595.5–598.0 (2.5s) | `world-allocation-board` | P5 laptop memory costs | `ev-dram-contract-v1` theirs-data (595.6–598.0) | N · gate — · tl — | dock | story | B1 |
| 58 | 598.0–619.2 (21.2s) | `world-laptop-shelf` | P5 hynix answers the three questions - 'It passes' | `ev-dram-contract-v1` theirs-data (598.0–606.9); `silicon-value-software-bubble-s13-teacher-stamped` theirs (608.1–619.2) · _dram-contract held to 606.9; s13 slide 608.1_ | y* · gate — · tl 8.9s@598.0, 11.1s@608.1 | dock | story | B1 C5(21.2s window with 2 docks - ok under s9.13) |
| 59 | 619.2–625.3 (6.1s) | `world-steel-mill-night` | P5 'the most vertical line is steel' | `silicon-antidote-s02-memory-triopoly-v1` theirs (619.2–625.3) | N · gate — · tl — | dock | — | B1 (stamped slide) |
| 60 | 625.4–634.3 (8.9s) | `beat-04-013-guidance-not-gospel-v1` | P5 tell opens - Bravos' tripwire 5.5; 'mine is stricter' | `ev-tripwire-board-v1` OURS (630.0–645.8) | Y · gate 9.2s@625.4 · tl — | dock | story | B2 (ours, board; the tell's chart is #62) |
| 61 | 634.6–646.0 (11.4s) | `beat-04-003-classic-cycle-counterargument-v1` | P5 tell - the variable is memory; 'I don't take that on trust' | _tripwire held over (to 645.8)_ | Y · gate 11.4s@634.6 · tl 11.2s@634.6 | dock (held) | story | B2 <12s |
| 62 | 646.0–660.4 (14.4s) | `world-korea-port-v1` | P5 THE TELL - 'I built a monitor for it' - customs, by the kilo | `ev-memory-monitor-v1` OURS (646.1–660.4) | Y · gate 14.4s@646.0 · tl 14.3s@646.1 | **PAGE** (cand.) | dense-line | A1('I built a monitor') A2(series x3/43, SCML source line) A3(the tell + M01 14.4s) C6(board exits first) C1(freeze exit: #63–#64 continue the proof) |
| 63 | 660.4–662.9 (2.5s) | `world-memory-wafer-v1` | P5 tell - 'that print, I start trimming' | `ev-trim-proof-v1` OURS (660.4–673.1) | N · gate — · tl — | dock | story | B2 (8 prints, ours) <12s |
| 64 | 662.9–683.5 (20.6s) | `world-unwind-desk-v2` | P5 the readings + the June trim - 'a big run digesting' | `ev-hbm-export-series` ours, png only (662.9–673.1); `ev-june-print-v1` OURS (673.3–683.5) · _trim-proof held to 673.1_ | Y · gate 13.7s@662.9 · tl 10.2s@662.9, 10.2s@673.3 | dock | combo (june-print) · — (png) | B2 (second view of the #62 page) B3 D4 C5(20.6s window, M05) |
| 65 | 683.5–690.3 (6.8s) | `world-modern-certificate-v1` | P5→P6 the flip - 'I de-risk the builders on camera' | — | N · gate — · tl — | none | — | <12s |
| 66 | 690.3–694.6 (4.3s) | `world-spike-certificate-ring-v2` | P6 ring echo - the spike | — | N · gate — · tl — | none | — | <12s (savor) |
| 67 | 694.6–705.2 (10.6s) | `world-club-interior-papered` | P6 'paper is paper' - the spike, one more time; 1850 | `ev-holds-stack-v1` mixed stack (701.7–727.6) · _holds-stack enters 701.7_ | Y · gate 10.6s@694.6 · tl — | dock | — | B1 (stack of their docs) |
| 68 | 705.2–717.1 (11.9s) | `beat-03-008-009-physical-capacity-gate-v1` | P6 verdict stack - 'everything we checked holds' | _holds-stack held over (to 727.6)_ | Y · gate 11.9s@705.2 · tl 11.9s@705.2 | dock (held) | — | B1 <12s (11.9s) |
| 69 | 717.1–725.7 (8.6s) | `world-listing-barge-v1` | P6 'a fifth of your index rides on one bet' | _holds-stack held_ | Y · gate 8.6s@717.1 · tl 8.6s@717.1 | dock (held) | — | B1 <12s |
| 70 | 725.7–760.3 (34.6s) | `beat-05-002-strategic-chokepoints-v1` | P6 RING CLOSE - 'further than Bravos': sold out and paid for; the fab arithmetic | `ev-hynix-steel-v1` OURS (730.3–759.7); `ev-memory-arithmetic-v1` OURS (741.2–759.7) | Y · gate 34.6s@725.7 · tl 10.9s@730.3, 18.5s@741.2 | **PAGE** (cand.) | race (series pending) · today combo + story | A1(ours: 'I own them on purpose', DART cross-check) A2*(ev-memory-share-race-v1.series.json does NOT exist - T5; hynix-steel series does) A3(ring close + M01 34.6s worst) C5(34.6s window, M05: split) D4 |
| 71 | 760.3–773.0 (12.7s) | `world-listing-barge-v1` | P6 verdict - 'the safe version IS the certificate' | `ev-index-concentration-v1` theirs-data (760.3–772.8) | Y · gate 12.7s@760.3 · tl 12.5s@760.3 | dock | story | B1 (Bravos figures) D4 (12.7s held, no event) |
| 72 | 773.0–778.6 (5.6s) | `beat-06-017-018-diworsification-v1` | P6 final triad - used / believed / discovered | — | N · gate — · tl — | none | — | <12s |
| 73 | 778.6–796.5 (17.9s) | `beat-04-001-buyer-behavior-v1` | P6 CTA - 'you now have the test'; the watch; the yardstick quarterly | `ev-test-scorecard-v1` OURS (778.6–787.1) · _scorecard 778.6–787.1 then bare 9.4s_ | Y · gate 17.9s@778.6 · tl 8.5s@778.6, 9.4s@787.1 | dock | story | B2 (recap view of #47) D4 (17.9s window) |
| 74 | 796.5–805.0 (8.5s) | `beat-06-001-003-index-product-elevator-v1` | P6 future pacing - 'which half of your portfolio is steel' | — | Y · gate 8.5s@796.5 · tl 8.5s@796.5 | none | — | <12s (8.5s) D4 |
| 75 | 805.0–806.5 (1.5s) | `world-spike-rest-v2` | P6 ring anchor - the spike stays on the desk | — | N · gate — · tl — | none | — | <12s (savor) |

## SUMMARY

### Counts per surface (primary surface of the row)

- **page**: 8
- **dock**: 49
- **plate-life**: 4
- **none**: 14
- total: 75 = len(W)

The 8 page rows are **6 distinct pages**: #13–#14–#15 is one page (build, datum lands, wipe out) and #47 is dock→page inside one window. #16 counts as plate-life for its bare second half (its first half is a held dock).

Secondary surfaces inside those rows: #16 dock→plate-life (its bare second half), #47 dock→page, #15 page→wipe, #53 none→dock (overlaps #54).

### PAGE candidates, in time order (the re-script chooses from these)

1. **#6 · 57.3–71.3 · the memory layer** (`ev-divergence-v1`, dense-line). The P1 mini-payoff: 'one layer Bravos' chart never drew' is the B4 claim of OUR layer, the series is ours (x4/235, Yahoo), and it sits in a 14.0s M01 still on a bare plate. D3 names the mini-payoff chart the default P1 page. #5 stays the dock (their pairing + our S&P line); C6: that dock exits, the page rolls out at 'one layer'. Exit by wipe — #7 changes topic to the promise. *Census adds this one; the PRP did not name it.*
2. **#13→#14 · 121.9–161.7 · the yardstick, 28 cents** (`ev-capital-formation-v1`, dense-line; story callout for ½ / 23¢ / 28¢ / 65¢). 'I pulled their yardstick myself, and I ran it all the way back' is the cleanest A1 in P2; BEA-via-FRED series x2/226 with our source line; A3 = the catalyst's close, and today it is a 22s single-dock plate (M05) followed by a 17.7s held-chart still. **The PRP's '28-cent payoff' — census agrees.** One page across two windows: build in #13, the 28¢ datum lands in #14, wipe out at 172.3 when rates take over (#15). C5: the current 50s dock span (122.1–172.2) must be split so the page never holds past 20s bare.
3. **#41 · 410.0–427.9 · 1845 vs 2026** (`ev-weight-check-v1`, story: their 20% / our check / historically 2–4, against 1845's paper that lost ⅔). The pivot's THEREFORE (never the reversal, #38 — C4), in the gate's 18.5s still. A2 holds (shares x2, iShares filing via SCML ledger). **A1 is conditional**: the card says 'We checked. It's bigger.' but the VO says 'Bravos' own number' — the re-script has to claim the check out loud. **The PRP's '1845 vs 2026' — census agrees, with that condition.** #42 (SMH fall-by-half, decline) is the second view: B2/B3, lands on the page's quiet zone or follows a beat-freeze exit.
4. **#47 · ~488–509.9 · THE TEST** (`ev-test-scorecard-v1`, story — the three questions as bars, PRP line 35). P5 payoff delivery at 59–63% of runtime; ours; a checklist series (T2's validator must accept word rows, no numerics). The sovereign slide docks first (B1) and must exit before the roll-out (C6). The 36.0s window is an M05 over-hold and must split. *Census adds this one.*
5. **#62 · 646.0–660.4 · the memory monitor — the tell** (`ev-memory-monitor-v1`, dense-line, series x3/43 monthly, log). 'I built a monitor for it' is the strongest first-person claim in the script; SCML source line on the series; the tell is a turning beat and the window is a 14.4s M01 still on both clocks. Tripwire board exits first (C6); #63–#64 continue the proof (trim-proof, June print) → beat-freeze exit, docks B2/B3. *Census adds this one; it is the tell's page by A3's own list.*
6. **#70 · 725.7–760.3 · the memory race — ring close** (builder `race`; today `ev-hynix-steel-v1` combo + `ev-memory-arithmetic-v1` story). 'Further than Bravos … I own them on purpose … do the arithmetic yourself' — ours; the worst still in the episode (34.6s, M01) and an M05 over-hold. **The PRP's 'memory race' — census agrees on the slot, but A2 fails today: `evidence/objects/ev-memory-share-race-v1.series.json` does not exist (T5 builds it).** Until then the hynix-steel series (ours, DART cross-check) is the page-able chart here, builder combo. The window must split (C5).

Doctrine floor: the payoff page by default plus at least one more. Six candidates clear (a); the three the PRP named (#13–14, #41, #70) all survive the census, two with a stated condition (#41 A1 wording, #70 A2 series). The census adds #6, #47 and #62.

Near-misses that would page if the VO claimed the pull (A1 only): **#35** `ev-capex-funding-v1` (P3's best evidence, combo — 'I pulled the filings' is missing), **#54** `ev-krx-memory-v3` (dense-line, our Yahoo pull, VO third-person). Both dock today (B2).

### DEFECT rows — still > 12s with no page, dock, or plate life today

Bare plate under narration, over the ceiling on the timeline clock; each is a plate-life candidate (D1) and cites D4 as the floor:

- **#7** 71.3–86.0 (14.7s) `world-signature-nib-v2` — the promise. Cutouts: nib lowers, three ink marks stepped in.
- **#16** 190.4–204.3 bare half (13.9s) of a 30.4s window, `world-broadcast-set-v2` — after the tnx dock exits. Split the window (M05).
- **#17** 204.3–218.3 (14.0s) `world-sell-ticket-v1` — the obvious move. Cutouts: ticket stamped / torn / pinned.
- **#24** 265.4–277.4 (12.0s; 12.2s on the timeline) `world-dawn-factory-v1` — what survives. Cutouts: a train crossing the works, smoke plumes stepped.

Held-dock stills > 12s (a dock is up but nothing moves — not a §9.28 defect, but D4 applies until the page/plate-life lands): #3 (12.4s), #4 (21.3s), #13 (21.9s), #14 (17.7s), #16 first half (16.5s), #29 (16.7s), #36 (14.0s), #41 (18.1s), #47 (14.8s + 18.5s), #48 (12.1s), #54 (13.9s), #62 (14.3s), #70 (18.5s), #71 (12.5s). Four of these are PAGE candidates, which is the E21 point: the still windows are the windows with no built chart.

### Shot-table defects noticed while classifying (not surface verdicts)

- `evidence-dock.json` / `motion-plan.json` are on a stale clock vs the timeline (see the caveat above); the gate's M01/M03/M08 figures for build-f are computed against them. Regenerating both from the timeline's scene docks is a T4 precondition, or the gate should read `scenes[].docks` when present.
- Rows #53 (560.8–570.0) and #54 (564.5–577.6) overlap by 5.5s in `W`.
- The task brief said 76 rows; `len(W)` is 75. The table has 75 rows.

Sources read: doc 29 §9.25–§9.28; `SHOT-TABLE-F.py`; `build-f/steel-and-paper.timeline.json` (scenes, captions, evidence map); `build-f/evidence-dock.json`; `evidence/objects/*.series.json` (`src` lines); `content/video_engine/sources/PLATE-LIBRARY.json` + review-claim manifests (plate semantics); `scripts/gate_motion_density.py` (`_load`, `analyse`).
