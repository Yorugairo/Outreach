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
( 7.8,  16.5, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,9.5,50.3)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 16.6,  29.0, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 29.0,  50.3, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 50.3,  57.2, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,50.3,70.8)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 57.2,  71.2, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 71.2,  86.1, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 86.3,  92.2, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,86.8,92.2)]),  # the cyclical trauma: returns -> capital -> oversupply
( 92.2,  96.9, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 97.1,  104.1, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 104.1, 112.2, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,104.1,112.2),("ev-railway-gdp-tile-v1",1,111.0,113.2)]),
(112.5, 119.5, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(119.5, 141.2, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,119.7,169.3)]),  # "I went and pulled a version myself"
(141.4, 158.8, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(158.8, 170.7, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,169.4,187.2)]),
(170.9, 200.9, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(200.9, 214.9, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(215.5, 222.8, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(223.0, 228.4, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,223.0,233.2)]),          # Karp on CNBC
(228.4, 233.2, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(233.2, 242.8, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,233.4,250.0)]),  # "can't draw a line to what you're shipping"
(243.1, 251.9, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(252.0, 263.4, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,252.2,263.6)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(263.4, 275.2, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(275.6, 279.1, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(279.2, 287.9, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(287.9, 293.0, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,288.1,298.2)]),  # the borrowing, as an object
(293.1, 298.2, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(298.2, 315.0, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,298.3,314.9)]),  # money that sat in utilities
(315.0, 323.0, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,315.4,324.4)]),
(323.0, 326.9, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(326.9, 334.7, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,326.9,344.8)]),        # a contract pinned to the site fence
(334.7, 344.8, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(344.8, 355.6, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,344.9,363.0)]),  # POOL: what investors believe future cash flows are worth
(355.6, 364.8, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(364.8, 378.3, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(378.3, 386.3, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(386.3, 393.9, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(394.5, 399.5, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,394.9,403.2)]),# it was railway CERTIFICATES
(399.5, 403.0, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(403.0, 420.5, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,403.2,420.9)], "cut"),  # the default your retirement sits in
(421.1, 430.4, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,421.1,431.0)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(430.6, 436.9, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(437.9, 448.7, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,438.1,448.9)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(449.1, 459.7, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,449.4,459.7)], "cut"),                       # railway steel sat 20 years; compute depreciates
(459.7, 464.6, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,459.7,464.6)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(464.6, 498.7, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,464.6,478.2),("ev-test-scorecard-v1",0,481.7,530.9)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(499.5, 511.4, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(511.4, 521.0, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(521.0, 531.3, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(531.4, 540.3, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,531.5,548.3)]),  # the chart RETURNS at the line that names it
(540.3, 547.1, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(548.3, 557.2, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(551.9, 564.6, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,552.2,565.7)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(565.9, 571.8, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,566.1,571.8)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(571.8, 581.7, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,571.8,581.7),("silicon-antidote-s09-capacity-penalty-v1",1,575.8,581.7)]),
(582.0, 584.7, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,582.2,584.7)]),  # every line marked through - sold out
(584.7, 605.6, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,584.7,593.5),("silicon-value-software-bubble-s13-teacher-stamped",1,594.6,605.6)]),  # the blank price card
(605.6, 611.5, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,605.6,611.5)]),  # the most vertical line is steel
(611.6, 620.5, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,616.3,631.9)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(620.8, 632.1, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(632.1, 646.3, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,632.2,646.3)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(646.3, 648.7, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,646.3,659.0)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(648.7, 669.6, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,648.7,659.0),("ev-june-print-v1",0,659.2,669.5)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(669.6, 676.1, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(676.1, 680.4, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(680.4, 690.8, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(690.8, 702.5, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(702.5, 710.8, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(710.8, 744.9, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,715.3,744.3),("ev-memory-arithmetic-v1",1,726.1,744.3)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(744.9, 757.4, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,744.9,757.2)]),  # the verdict: the safe version IS the certificate
(757.4, 762.9, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(762.9, 780.5, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,762.9,767.4)]),  # CTA: you now have the test - the scorecard returns at its recap
(780.5, 788.9, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(788.9, 790.4, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
