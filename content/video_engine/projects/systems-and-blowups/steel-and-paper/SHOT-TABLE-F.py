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
(  0.0,  6.7, "world-spike-desk-v1",            (.05,  10,  -6), []),                       # the spike itself, macro. The ring token plants here.
( 6.8,  15.5, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,8.3,50.3)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 15.6,  28.3, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 28.3,  50.3, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 50.3,  57.4, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,50.3,71.5)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 57.4,  71.9, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 71.9,  87.3, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 87.6,  94.0, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,88.1,94.0)]),  # the cyclical trauma: returns -> capital -> oversupply
( 94.0,  99.1, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 99.3,  107.0, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 107.0, 116.1, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,107.0,116.1),("ev-railway-gdp-tile-v1",1,114.8,117.0)]),
(116.4, 123.6, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(123.6, 145.5, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,123.8,173.8)]),  # "I went and pulled a version myself"
(145.7, 163.3, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(163.3, 175.2, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,173.9,191.6)]),
(175.4, 205.1, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(205.1, 219.0, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(219.6, 226.8, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(227.0, 232.6, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,227.0,237.6)]),          # Karp on CNBC
(232.6, 237.6, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(237.6, 247.9, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,237.8,255.6)]),  # "can't draw a line to what you're shipping"
(248.2, 257.7, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(257.8, 269.7, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,258.0,269.9)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(269.7, 282.0, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(282.4, 286.1, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(286.2, 295.3, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(295.3, 300.6, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,295.5,306.1)]),  # the borrowing, as an object
(300.7, 306.1, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(306.1, 323.6, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,306.2,323.5)]),  # money that sat in utilities
(323.6, 331.5, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,324.1,332.9)]),
(331.5, 335.4, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(335.4, 344.0, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,335.4,355.0)]),        # a contract pinned to the site fence
(344.0, 355.0, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(355.0, 364.5, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,355.2,370.9)]),  # POOL: what investors believe future cash flows are worth
(364.5, 372.5, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(372.5, 384.2, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(384.2, 391.2, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(391.2, 397.8, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(398.3, 403.6, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,398.7,407.6)]),# it was railway CERTIFICATES
(403.6, 407.4, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(407.4, 424.1, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,407.6,424.5)], "cut"),  # the default your retirement sits in
(424.7, 434.0, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,424.7,434.6)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(434.2, 440.5, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(441.5, 452.3, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,441.7,452.5)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(452.7, 463.3, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,453.0,463.3)], "cut"),                       # railway steel sat 20 years; compute depreciates
(463.3, 467.8, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,463.3,467.8)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(467.8, 502.7, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,467.8,482.7),("ev-test-scorecard-v1",0,486.6,533.3)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(503.5, 514.8, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(514.8, 523.9, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(523.9, 533.7, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(533.8, 542.2, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,533.9,549.8)]),  # the chart RETURNS at the line that names it
(542.2, 548.7, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(549.8, 558.4, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(553.2, 565.6, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,553.5,566.6)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(566.8, 573.1, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,567.0,573.1)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(573.1, 583.9, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,573.1,583.9),("silicon-antidote-s09-capacity-penalty-v1",1,577.7,583.9)]),
(584.2, 587.0, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,584.4,587.0)]),  # every line marked through - sold out
(587.0, 606.5, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,587.0,595.6),("silicon-value-software-bubble-s13-teacher-stamped",1,596.7,606.5)]),  # the blank price card
(606.5, 612.4, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,606.5,612.4)]),  # the most vertical line is steel
(612.5, 621.7, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,617.1,633.9)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(622.0, 634.1, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(634.1, 648.5, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,634.2,648.5)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(648.5, 651.0, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,648.5,662.0)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(651.0, 672.9, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,651.0,662.0),("ev-june-print-v1",0,662.2,672.8)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(672.9, 679.6, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(679.6, 684.0, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(684.0, 694.7, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(694.7, 706.7, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(706.7, 715.3, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(715.3, 748.8, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,719.9,748.3),("ev-memory-arithmetic-v1",1,730.6,748.3)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(748.8, 761.8, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,748.8,761.6)]),  # the verdict: the safe version IS the certificate
(761.8, 767.5, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(767.5, 785.8, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,767.5,772.2)]),  # CTA: you now have the test - the scorecard returns at its recap
(785.8, 794.5, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(794.5, 796.1, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
