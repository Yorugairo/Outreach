"""Steel and Paper — Script F SHOT TABLE. AUTHORED, not allocated.

One row per window. Each plate was chosen because its saved `semantic`
depicts the beat it sits under; each dock was chosen because that document
proves the claim being spoken. The density rules are the CHECK on this
table, never its source.

    (start, end, plate_id, ken_burns(scale, x, y), [docks])
    dock = (evidence_id, slot, enter, exit)

Ken Burns is authored per shot: push in on arrivals and reveals, pull back
on reflection, drift laterally across a wide world. Scale is the doc 29
range (1.00 -> 1.04 over the shot), x/y in px.
"""

W = [
# ── P1 OPEN ────────────────────────────────────────────────────────────
(  0.0,  7.0, "world-spike-desk-v1",            (.05,  10,  -6), []),                       # the spike itself, macro. The ring token plants here.
( 7.1,  15.7, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,8.7,49.7)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 15.8,  28.2, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 28.2,  49.7, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 49.7,  56.6, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,49.7,70.1)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 56.6,  70.5, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 70.5,  85.3, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 85.6,  91.5, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,86.1,91.5)]),  # the cyclical trauma: returns -> capital -> oversupply
( 91.5,  96.2, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 96.4,  103.5, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 103.5, 111.8, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,103.5,111.8),("ev-railway-gdp-tile-v1",1,103.5,111.8)]),
(112.0, 118.6, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(118.6, 139.6, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,118.8,166.8)]),  # "I went and pulled a version myself"
(139.8, 156.7, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(156.7, 168.2, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,166.9,184.8)]),
(168.4, 198.4, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(198.4, 212.5, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(213.1, 220.4, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(220.6, 225.9, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,220.6,230.8)]),          # Karp on CNBC
(225.9, 230.8, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(230.8, 240.4, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,230.9,247.6)]),  # "can't draw a line to what you're shipping"
(240.7, 249.5, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(249.6, 261.0, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,249.8,261.2)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(261.0, 272.8, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(273.1, 276.7, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(276.8, 285.5, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(285.5, 290.5, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,285.7,295.8)]),  # the borrowing, as an object
(290.6, 295.8, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(295.8, 312.5, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,295.9,312.4)]),  # money that sat in utilities
(312.5, 320.5, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,313.0,322.0)]),
(320.5, 324.5, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(324.5, 332.3, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,324.5,342.3)]),        # a contract pinned to the site fence
(332.3, 342.3, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(342.3, 352.8, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,342.5,359.9)]),  # POOL: what investors believe future cash flows are worth
(352.8, 361.7, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(361.7, 374.7, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(374.7, 382.5, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(382.5, 389.8, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(390.4, 395.7, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,390.8,399.7)]),# it was railway CERTIFICATES
(395.7, 399.5, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(399.5, 416.2, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,399.7,416.6)], "cut"),  # the default your retirement sits in
(416.8, 426.1, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,416.8,426.7)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(426.3, 432.6, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(433.6, 444.4, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,433.8,444.6)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(444.8, 455.4, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,445.1,455.4)], "cut"),                       # railway steel sat 20 years; compute depreciates
(455.4, 459.9, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,455.4,459.9)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(459.9, 494.8, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,459.9,474.8),("ev-test-scorecard-v1",0,478.7,525.4)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(495.6, 506.9, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(506.9, 516.0, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(516.0, 525.8, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(525.9, 534.3, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,526.0,541.9)]),  # the chart RETURNS at the line that names it
(534.3, 540.8, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(541.9, 550.5, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(545.3, 557.7, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,545.6,558.7)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(558.9, 565.2, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,559.1,565.2)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(565.2, 578.5, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,565.2,578.5),("silicon-antidote-s09-capacity-penalty-v1",1,569.8,578.5)]),
(578.9, 582.8, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,579.1,582.8)]),  # every line marked through - sold out
(582.8, 598.7, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,582.8,588.1),("silicon-value-software-bubble-s13-teacher-stamped",1,588.8,598.7)]),  # the blank price card
(598.7, 604.5, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,598.7,604.5)]),  # the most vertical line is steel
(604.6, 613.8, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,609.2,626.0)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(614.1, 626.2, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(626.2, 640.6, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,626.3,640.6)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(640.6, 643.1, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,640.6,654.1)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(643.1, 665.0, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,643.1,654.1),("ev-june-print-v1",0,654.3,664.9)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(665.0, 671.7, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(671.7, 676.1, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(676.1, 686.8, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(686.8, 698.8, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(698.8, 707.4, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(707.4, 740.9, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,712.0,740.4),("ev-memory-arithmetic-v1",1,722.7,740.4)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(740.9, 753.9, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,740.9,753.7)]),  # the verdict: the safe version IS the certificate
(753.9, 759.6, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(759.6, 777.9, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,759.6,764.3)]),  # CTA: you now have the test - the scorecard returns at its recap
(777.9, 786.6, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(786.6, 788.2, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
