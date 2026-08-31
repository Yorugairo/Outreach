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
( 7.8,  16.6, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,9.5,50.5)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 16.7,  29.1, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 29.1,  50.5, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 50.5,  57.3, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,50.5,70.9)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 57.3,  71.3, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 71.3,  86.1, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 86.3,  92.3, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,86.9,92.3)]),  # the cyclical trauma: returns -> capital -> oversupply
( 92.3,  97.0, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 97.2,  104.2, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 104.2, 112.1, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,104.2,112.1),("ev-railway-gdp-tile-v1",1,104.2,112.1)]),
(112.4, 119.3, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(119.3, 141.2, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,119.5,169.6)]),  # "I went and pulled a version myself"
(141.4, 159.1, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(159.1, 171.1, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,169.7,187.7)]),
(171.3, 201.5, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(201.5, 215.6, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(216.2, 223.6, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(223.8, 228.9, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,223.8,233.5)]),          # Karp on CNBC
(228.9, 233.5, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(233.5, 242.9, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,233.7,250.1)]),  # "can't draw a line to what you're shipping"
(243.2, 251.9, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(252.0, 263.4, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,252.2,263.6)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(263.4, 275.2, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(275.6, 279.1, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(279.2, 288.0, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(288.0, 293.0, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,288.2,298.2)]),  # the borrowing, as an object
(293.1, 298.2, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(298.2, 314.7, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,298.3,314.6)]),  # money that sat in utilities
(314.7, 322.8, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,315.1,324.1)]),
(322.8, 326.6, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(326.6, 334.8, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,326.6,345.2)]),        # a contract pinned to the site fence
(334.8, 345.2, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(345.2, 356.2, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,345.3,363.7)]),  # POOL: what investors believe future cash flows are worth
(356.2, 365.5, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(365.5, 379.3, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(379.3, 387.4, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(387.4, 395.1, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(395.7, 400.7, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,396.1,404.4)]),# it was railway CERTIFICATES
(400.7, 404.2, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(404.2, 421.4, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,404.4,421.8)], "cut"),  # the default your retirement sits in
(422.0, 431.5, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,422.0,432.1)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(431.7, 438.2, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(439.2, 450.3, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,439.4,450.5)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(450.7, 461.6, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,451.0,461.6)], "cut"),                       # railway steel sat 20 years; compute depreciates
(461.6, 466.5, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,461.6,466.5)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(466.5, 501.9, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,466.5,481.0),("ev-test-scorecard-v1",0,484.6,534.7)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(502.8, 514.8, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(514.8, 524.6, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(524.6, 535.1, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(535.2, 544.2, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,535.3,552.3)]),  # the chart RETURNS at the line that names it
(544.2, 551.2, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(552.3, 561.5, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(556.0, 569.2, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,556.3,570.3)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(570.5, 576.5, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,570.7,576.5)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(576.5, 586.5, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,576.5,586.5),("silicon-antidote-s09-capacity-penalty-v1",1,580.6,586.5)]),
(586.8, 589.4, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,586.9,589.4)]),  # every line marked through - sold out
(589.4, 610.5, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,589.4,598.2),("silicon-value-software-bubble-s13-teacher-stamped",1,599.4,610.5)]),  # the blank price card
(610.5, 616.5, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,610.5,616.5)]),  # the most vertical line is steel
(616.6, 625.4, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,621.2,636.7)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(625.7, 636.9, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(636.9, 651.3, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,637.0,651.3)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(651.3, 653.8, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,651.3,664.0)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(653.8, 674.6, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,653.8,664.0),("ev-june-print-v1",0,664.2,674.5)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(674.6, 681.2, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(681.2, 685.5, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(685.5, 696.0, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(696.0, 707.8, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(707.8, 716.1, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(716.1, 750.6, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,720.6,750.0),("ev-memory-arithmetic-v1",1,731.4,750.0)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(750.6, 763.3, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,750.6,763.1)]),  # the verdict: the safe version IS the certificate
(763.3, 768.9, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(768.9, 786.7, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,768.9,773.4)]),  # CTA: you now have the test - the scorecard returns at its recap
(786.7, 795.2, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(795.2, 796.7, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
