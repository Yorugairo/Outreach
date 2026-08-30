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
(  0.0,  11.4, "world-spike-desk-v1",            (.05,  10,  -6), []),                       # the spike itself, macro. The ring token plants here.
( 11.5,  19.8, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,14.1,47.6)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 19.9,  30.0, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 30.0,  47.6, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 47.6,  54.7, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,47.6,68.5)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 54.7,  68.9, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 68.9,  84.2, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 84.4,  91.2, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,85.0,91.2)]),  # the cyclical trauma: returns -> capital -> oversupply
( 91.2,  96.7, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 96.9,  106.0, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 106.0, 114.1, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,106.0,114.1),("ev-railway-gdp-tile-v1",0,111.0,114.1)]),
(114.2, 120.1, "world-dotcom-server-room-v1",    (.04, -10,   6), [("ev-capital-formation-v1",0,114.2,120.1)]),  # the internet's 7% of GDP
(120.1, 141.2, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,120.1,133.6)]),  # "I went and pulled a version myself"
(141.4, 158.3, "world-pressure-gauge-v1",        (.05, -14,   8), [("ev-tnx-two-eras-v3",0,141.5,158.3)]),   # the rate trigger, as an instrument
(158.3, 169.9, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,158.3,170.5)]),
(170.1, 202.0, "world-broadcast-set-v2",         (.04, -12,  -8), [("ev-tnx-two-eras-v3",0,170.5,179.5)]),  # their line on the record, then the racetrack
(202.0, 217.2, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(217.8, 225.6, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(225.8, 231.1, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,225.8,231.1)]),          # Karp on CNBC
(231.1, 236.3, "world-budget-burndown-v1",       (.05, -12,   8), [("ev-uber-adoption-v1",1,231.3,236.3)]),  # Uber burned the annual budget by April
(236.3, 246.7, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,236.3,245.3)]),  # "can't draw a line to what you're shipping"
(247.0, 256.7, "world-exhibition-hall-morning-v1",(.05, -14,   6), [("ev-three-manias",0,247.1,257.0)], "cut"),      # the fair the morning after = the trough
(256.8, 268.6, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,257.0,267.0)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(268.6, 280.9, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(281.2, 285.0, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(285.1, 294.1, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(294.1, 300.0, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,294.3,300.0)]),  # the borrowing, as an object
(300.1, 306.1, "world-index-board-swelling",     (.04, -10,   8), [("ev-ig-credit-weighting-v1",0,300.2,306.1)]),  # one sector crowding the index
(306.1, 325.3, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,306.1,315.6)]),  # money that sat in utilities
(325.3, 335.8, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,325.9,335.8)]),
(335.8, 341.1, "world-lease-contracts-bound",    (.05, -14,   8), [("ev-doc-leases",0,335.8,341.1)]),        # bound contract volumes past the frame
(341.1, 347.8, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,341.1,347.8)]),        # a contract pinned to the site fence
(347.8, 356.5, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), [("ev-doc-macdonald",0,347.8,356.5)]),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(356.5, 366.9, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,356.5,364.0)]),  # POOL: what investors believe future cash flows are worth
(366.9, 375.9, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(375.9, 388.9, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(388.9, 396.8, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(396.8, 404.2, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(404.8, 410.4, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,405.2,410.4)]),# it was railway CERTIFICATES
(410.4, 414.6, "world-exchange-floor-1845"   ,    (.05,  12,  -6), [("silicon-antidote-s02-valuation-bubble-v1",0,410.4,414.6)]),
(414.6, 432.2, "world-target-date-envelope-v1",  (.04, -10,   6), [("silicon-antidote-s02-valuation-bubble-v1",0,414.6,423.6)], "cut"),  # the default your retirement sits in
(432.8, 442.4, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,432.8,442.3)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(442.6, 448.8, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(449.8, 460.7, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,450.1,460.6)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(461.2, 471.9, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,461.5,471.5)], "cut"),                       # railway steel sat 20 years; compute depreciates
(471.9, 480.1, "hero-contract-ovens-v1",                   (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,474.8,480.1)], "cut"),  # orders in, slots gone  # ^REGISTER: the line issuing sealed contracts - orders in, slots gone
(480.1, 515.7, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,480.1,491.6)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(516.6, 528.8, "hero-barbell-v1",                       (.05,  12,   6), [("ev-test-scorecard-v1",0,518.4,528.8)]),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(528.8, 538.7, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(538.7, 549.4, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(549.5, 558.6, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,549.6,558.6)]),  # the chart RETURNS at the line that names it
(558.6, 565.7, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(566.9, 576.1, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(570.6, 583.9, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,570.9,583.9)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(585.1, 591.4, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,585.3,591.4)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(591.4, 598.7, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,591.4,598.4),("silicon-antidote-s09-capacity-penalty-v1",1,591.4,598.4)]),
(598.9, 605.9, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,599.1,605.9)]),  # every line marked through - sold out
(605.9, 623.6, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,605.9,613.9),("silicon-value-software-bubble-s13-teacher-stamped",1,616.8,623.6)]),  # the blank price card
(623.6, 630.8, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,623.6,630.8)]),  # the most vertical line is steel
(630.9, 641.8, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), []),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(642.2, 655.7, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(655.7, 662.9, "world-korea-port-v1",            (.05,  12,   6), [("sovereign-memory-infrastructure-s05-teacher-stamped",0,655.9,662.9)]),  # the geographic monopoly - memory leaving Korea  # s05 carries NO figure at all; 7.0s and gone, and it takes the stage alone rather than the narrow rail
(662.9, 670.0, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-instrument-memory",0,662.9,670.0)]), # the instrument, method and threshold
(670.0, 690.0, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",0,670.0,680.0)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(690.0, 695.5, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(695.5, 698.9, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(698.9, 707.7, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(707.7, 717.3, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(717.3, 724.3, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(724.3, 736.9, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,728.0,736.8)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(736.9, 751.2, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,736.9,751.0)]),  # the verdict: the safe version IS the certificate
(751.2, 757.3, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(757.3, 777.3, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,757.3,762.5)]),  # CTA: you now have the test - the scorecard returns at its recap
(777.3, 786.8, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(786.8, 788.6, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
