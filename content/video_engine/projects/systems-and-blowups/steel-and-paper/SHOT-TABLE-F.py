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
( 7.1,  15.6, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,8.7,49.2)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 15.7,  27.9, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 27.9,  49.2, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 49.2,  56.0, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,49.2,69.3)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 56.0,  69.7, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 69.7,  84.4, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 84.6,  91.4, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,85.1,91.4)]),  # the cyclical trauma: returns -> capital -> oversupply
( 91.4,  96.9, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 97.1,  105.4, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 105.4, 112.2, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,105.4,112.2),("ev-railway-gdp-tile-v1",1,105.4,112.2)]),
(112.3, 117.7, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(117.7, 138.5, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,117.9,165.4)]),  # "I went and pulled a version myself"
(138.7, 155.4, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(155.4, 166.8, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,165.5,183.4)]),
(167.0, 197.0, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(197.0, 211.2, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(211.8, 219.1, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(219.3, 224.7, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,219.3,229.9)]),          # Karp on CNBC
(224.7, 229.9, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(229.9, 239.4, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,230.0,246.7)]),  # "can't draw a line to what you're shipping"
(239.7, 248.6, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(248.7, 260.0, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,248.9,260.2)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(260.0, 271.7, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(272.0, 275.6, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(275.7, 284.3, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(284.3, 289.4, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,284.5,294.7)]),  # the borrowing, as an object
(289.5, 294.7, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(294.7, 311.4, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,294.8,311.3)]),  # money that sat in utilities
(311.4, 321.4, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,311.9,323.4)]),
(321.4, 326.5, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(326.5, 333.0, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,326.5,341.3)]),        # a contract pinned to the site fence
(333.0, 341.3, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(341.3, 352.0, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,341.5,359.3)]),  # POOL: what investors believe future cash flows are worth
(352.0, 361.2, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(361.2, 374.5, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(374.5, 382.5, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(382.5, 390.1, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(390.7, 395.8, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,391.1,399.7)]),# it was railway CERTIFICATES
(395.8, 399.6, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(399.6, 416.7, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,399.7,417.1)], "cut"),  # the default your retirement sits in
(417.3, 425.8, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,417.3,426.3)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(426.0, 431.6, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(432.5, 442.2, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,432.7,442.4)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(442.6, 452.2, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,442.9,452.2)], "cut"),                       # railway steel sat 20 years; compute depreciates
(452.2, 459.4, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,452.2,459.4)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(459.4, 493.3, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,459.4,473.2),("ev-test-scorecard-v1",0,476.8,524.7)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(494.1, 505.7, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(505.7, 515.0, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(515.0, 525.1, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(525.2, 533.8, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,525.3,541.6)]),  # the chart RETURNS at the line that names it
(533.8, 540.5, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(541.6, 550.4, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(545.1, 557.8, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,545.4,558.8)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(559.0, 564.9, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,559.2,564.9)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(564.9, 571.4, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,564.9,571.4),("silicon-antidote-s09-capacity-penalty-v1",1,564.9,571.4)]),
(571.6, 577.8, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,571.7,577.8)]),  # every line marked through - sold out
(577.8, 598.8, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,577.8,586.5),("silicon-value-software-bubble-s13-teacher-stamped",1,587.8,598.8)]),  # the blank price card
(598.8, 604.6, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,598.8,604.6)]),  # the most vertical line is steel
(604.7, 613.6, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,609.4,624.7)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(613.9, 624.9, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(624.9, 631.7, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,625.0,631.7)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(631.7, 638.5, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-instrument-memory",0,631.7,638.5)]), # the instrument, method and threshold
(638.5, 657.1, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",0,638.5,648.9)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(657.1, 662.2, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(662.2, 665.4, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(665.4, 673.5, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(673.5, 682.5, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(682.5, 689.0, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(689.0, 700.5, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,692.4,700.4),("ev-memory-arithmetic-v1",1,696.0,700.4)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(700.5, 714.0, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,700.5,713.8)]),  # the verdict: the safe version IS the certificate
(714.0, 719.8, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(719.8, 738.7, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,719.8,724.7)]),  # CTA: you now have the test - the scorecard returns at its recap
(738.7, 747.7, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(747.7, 749.4, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
