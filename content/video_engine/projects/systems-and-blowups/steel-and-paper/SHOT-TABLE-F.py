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
(  0.0,  7.7, "world-spike-desk-v1",            (.05,  10,  -6), []),                       # the spike itself, macro. The ring token plants here.
( 7.8,  16.6, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,9.5,50.7)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 16.7,  29.2, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 29.2,  50.7, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 50.7,  57.8, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,50.7,71.8)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 57.8,  72.2, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 72.2,  87.5, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 87.7,  93.7, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,88.3,93.7)]),  # the cyclical trauma: returns -> capital -> oversupply
( 93.7,  98.4, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 98.6,  105.6, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 105.6, 114.0, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,105.6,114.0),("ev-railway-gdp-tile-v1",1,112.8,115.0)]),
(114.3, 121.3, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(121.3, 143.3, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,121.5,171.8)]),  # "I went and pulled a version myself"
(143.5, 161.2, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(161.2, 173.3, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,171.9,190.4)]),
(173.5, 204.6, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(204.6, 219.1, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(219.7, 227.3, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(227.5, 232.6, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,227.5,237.2)]),          # Karp on CNBC
(232.6, 237.2, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(237.2, 247.0, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,237.4,254.5)]),  # "can't draw a line to what you're shipping"
(247.3, 256.4, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(256.5, 268.2, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,256.7,268.4)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(268.2, 280.3, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(280.7, 284.3, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(284.4, 293.4, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(293.4, 298.6, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,293.6,303.9)]),  # the borrowing, as an object
(298.7, 303.9, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(303.9, 320.5, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,304.0,320.4)]),  # money that sat in utilities
(320.5, 328.5, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,320.9,329.8)]),
(328.5, 332.3, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(332.3, 340.5, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,332.3,351.1)]),        # a contract pinned to the site fence
(340.5, 351.1, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(351.1, 362.2, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,351.2,369.9)]),  # POOL: what investors believe future cash flows are worth
(362.2, 371.7, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(371.7, 385.7, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(385.7, 393.9, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(393.9, 401.8, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(402.4, 407.4, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,402.8,411.1)]),# it was railway CERTIFICATES
(407.4, 410.9, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(410.9, 428.5, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,411.1,428.9)], "cut"),  # the default your retirement sits in
(429.1, 439.0, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,429.1,439.6)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(439.2, 445.9, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(447.0, 458.5, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,447.2,458.8)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(459.0, 470.3, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,459.3,470.3)], "cut"),                       # railway steel sat 20 years; compute depreciates
(470.3, 475.2, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,470.3,475.2)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(475.2, 511.2, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,475.2,489.7),("ev-test-scorecard-v1",0,493.4,545.0)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(512.1, 524.5, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(524.5, 534.6, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(534.6, 545.4, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(545.5, 554.8, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,545.6,563.2)]),  # the chart RETURNS at the line that names it
(554.8, 562.0, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(563.2, 572.8, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(567.0, 580.8, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,567.3,582.0)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(582.2, 588.3, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,582.4,588.3)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(588.3, 598.5, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,588.3,598.5),("silicon-antidote-s09-capacity-penalty-v1",1,592.4,598.5)]),
(598.8, 601.6, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,599.0,601.6)]),  # every line marked through - sold out
(601.6, 623.7, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,601.6,610.7),("silicon-value-software-bubble-s13-teacher-stamped",1,611.9,623.7)]),  # the blank price card
(623.7, 629.7, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,623.7,629.7)]),  # the most vertical line is steel
(629.8, 638.7, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,634.5,650.1)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(639.0, 650.3, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(650.3, 664.8, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,650.4,664.8)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(664.8, 667.2, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,664.8,677.5)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(667.2, 688.3, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,667.2,677.5),("ev-june-print-v1",0,677.7,688.2)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(688.3, 695.0, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(695.0, 699.4, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(699.4, 710.1, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(710.1, 722.1, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(722.1, 730.6, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(730.6, 765.6, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,735.2,765.0),("ev-memory-arithmetic-v1",1,746.3,765.0)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(765.6, 778.6, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,765.6,778.4)]),  # the verdict: the safe version IS the certificate
(778.6, 784.3, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(784.3, 802.5, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,784.3,788.9)]),  # CTA: you now have the test - the scorecard returns at its recap
(802.5, 811.2, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(811.2, 812.7, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
