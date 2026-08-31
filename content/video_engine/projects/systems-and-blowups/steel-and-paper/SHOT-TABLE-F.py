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
( 84.6,  90.6, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,85.1,90.6)]),  # the cyclical trauma: returns -> capital -> oversupply
( 90.6,  95.3, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 95.5,  102.6, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 102.6, 110.9, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,102.6,110.9),("ev-railway-gdp-tile-v1",1,109.5,111.7)]),
(111.1, 117.7, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
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
(311.4, 319.4, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,311.9,321.0)]),
(319.4, 323.5, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(323.5, 331.3, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,323.5,341.3)]),        # a contract pinned to the site fence
(331.3, 341.3, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(341.3, 351.8, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,341.5,358.9)]),  # POOL: what investors believe future cash flows are worth
(351.8, 360.7, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(360.7, 373.7, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(373.7, 381.5, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(381.5, 388.8, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(389.4, 394.7, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,389.8,398.8)]),# it was railway CERTIFICATES
(394.7, 398.6, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(398.6, 415.0, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,398.8,415.4)], "cut"),  # the default your retirement sits in
(415.6, 425.0, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,415.6,425.6)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(425.2, 431.5, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(432.5, 443.3, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,432.7,443.5)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(443.7, 454.4, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,444.0,454.4)], "cut"),                       # railway steel sat 20 years; compute depreciates
(454.4, 458.8, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,454.4,458.8)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(458.8, 493.8, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,458.8,473.8),("ev-test-scorecard-v1",0,477.7,524.5)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(494.6, 505.9, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(505.9, 515.0, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(515.0, 524.9, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(525.0, 533.4, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,525.1,541.0)]),  # the chart RETURNS at the line that names it
(533.4, 539.9, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(541.0, 549.6, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(544.4, 556.9, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,544.7,557.9)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(558.1, 564.3, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,558.3,564.3)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(564.3, 577.2, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,564.3,577.2),("silicon-antidote-s09-capacity-penalty-v1",1,568.6,577.2)]),
(577.6, 581.5, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,577.8,581.5)]),  # every line marked through - sold out
(581.5, 597.4, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,581.5,586.8),("silicon-value-software-bubble-s13-teacher-stamped",1,587.5,597.4)]),  # the blank price card
(597.4, 603.2, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,597.4,603.2)]),  # the most vertical line is steel
(603.3, 612.5, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,607.9,624.6)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(612.8, 624.8, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(624.8, 639.2, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,624.9,639.2)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(639.2, 641.7, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,639.2,652.7)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(641.7, 663.5, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,641.7,652.7),("ev-june-print-v1",0,652.9,663.4)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(663.5, 670.2, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(670.2, 674.5, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(674.5, 685.2, "world-club-interior-papered",    (.05, -10,  -6), []),                       # 1850: trains still running, certificates papering bankrupt clubs
(685.2, 697.1, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),            # everything holds - they sell scarcity, for cash; then the debt turn
(697.1, 705.7, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(705.7, 739.4, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,710.2,738.9),("ev-memory-arithmetic-v1",1,721.1,738.9)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(739.4, 752.2, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,739.4,752.0)]),  # the verdict: the safe version IS the certificate
(752.2, 757.8, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(757.8, 775.8, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,757.8,762.4)]),  # CTA: you now have the test - the scorecard returns at its recap
(775.8, 784.4, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(784.4, 786.0, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
