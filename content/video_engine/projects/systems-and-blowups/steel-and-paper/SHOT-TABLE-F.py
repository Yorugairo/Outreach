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
( 7.1,  15.6, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,8.7,15.6)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 15.7,  27.9, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 27.9,  49.2, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 49.2,  56.0, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,49.2,56.0)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 56.0,  69.7, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 69.7,  84.4, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 84.6,  91.4, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,85.1,91.3)]),  # the cyclical trauma: returns -> capital -> oversupply
( 91.4,  96.9, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 97.1,  105.5, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 105.5, 112.3, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,105.5,112.3),("ev-railway-gdp-tile-v1",1,105.5,112.3)]),
(112.4, 118.0, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(118.0, 138.8, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,118.2,138.8)]),  # "I went and pulled a version myself"
(139.0, 155.7, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(155.7, 167.0, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,164.8,167.0)]),
(167.2, 196.8, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(196.8, 210.9, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(211.5, 218.7, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(218.9, 223.9, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,218.9,223.9)]),          # Karp on CNBC
(223.9, 228.7, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(228.7, 238.1, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,228.8,238.1)]),  # "can't draw a line to what you're shipping"
(238.4, 247.1, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(247.2, 258.1, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,247.4,258.1)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(258.1, 269.4, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(269.7, 273.1, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(273.2, 281.5, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(281.5, 286.9, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,281.7,286.9)]),  # the borrowing, as an object
(286.9, 292.4, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(292.4, 309.2, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,292.5,309.2)]),  # money that sat in utilities
(309.2, 319.2, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,309.7,319.2)]),
(319.2, 324.3, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(324.3, 330.7, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,324.3,330.7)]),        # a contract pinned to the site fence
(330.7, 339.1, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(339.1, 349.5, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,339.3,349.5)]),  # POOL: what investors believe future cash flows are worth
(349.5, 358.6, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(358.6, 371.6, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(371.6, 379.6, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(379.6, 387.0, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(387.6, 392.7, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,388.0,392.7)]),# it was railway CERTIFICATES
(392.7, 396.5, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(396.5, 412.7, "world-target-date-envelope-v1",  (.04, -10,   6), [("silicon-antidote-s02-valuation-bubble-v1",0,396.6,412.7)], "cut"),  # the default your retirement sits in
(413.2, 421.7, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,413.2,421.7)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(421.9, 427.3, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(428.2, 437.8, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,428.5,437.8)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(438.3, 447.7, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,438.5,447.7)], "cut"),                       # railway steel sat 20 years; compute depreciates
(447.7, 454.9, "hero-contract-ovens-v1",                   (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,447.7,454.9)], "cut"),  # orders in, slots gone  # ^REGISTER: the line issuing sealed contracts - orders in, slots gone
(454.9, 487.9, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,454.9,469.4)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(488.8, 500.2, "hero-barbell-v1",                       (.05,  12,   6), [("ev-test-scorecard-v1",0,490.4,500.2)]),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(500.2, 509.4, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(509.4, 519.5, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(519.6, 528.1, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,519.6,528.1)]),  # the chart RETURNS at the line that names it
(528.1, 534.7, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(535.8, 544.4, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(539.3, 551.6, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,539.6,551.6)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(552.7, 558.6, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,552.9,558.6)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(558.6, 565.3, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,558.6,565.3),("silicon-antidote-s09-capacity-penalty-v1",1,558.6,565.3)]),
(565.5, 571.8, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,565.6,571.8)]),  # every line marked through - sold out
(571.8, 592.4, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,571.8,581.3),("silicon-value-software-bubble-s13-teacher-stamped",1,581.8,588.6)]),  # the blank price card
(592.4, 598.2, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,592.4,598.2)]),  # the most vertical line is steel
(598.3, 607.2, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), []),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(607.5, 618.5, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(618.5, 625.3, "world-korea-port-v1",            (.05,  12,   6), [("sovereign-memory-infrastructure-s05-teacher-stamped",0,618.6,625.3)]),  # the geographic monopoly - memory leaving Korea  # s05 carries NO figure at all; 7.0s and gone, and it takes the stage alone rather than the narrow rail
(625.3, 632.1, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-instrument-memory",0,625.3,632.1)]), # the instrument, method and threshold
(632.1, 650.8, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",0,632.1,643.3)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(650.8, 655.9, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(655.9, 659.1, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(659.1, 667.3, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(667.3, 676.3, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(676.3, 682.8, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(682.8, 694.3, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,686.3,694.3)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(694.3, 707.7, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,694.3,707.7)]),  # the verdict: the safe version IS the certificate
(707.7, 713.5, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(713.5, 732.2, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,713.5,718.7)]),  # CTA: you now have the test - the scorecard returns at its recap
(732.2, 741.1, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(741.1, 742.8, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
