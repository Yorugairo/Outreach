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
(  0.0,  11.8, "world-spike-desk-v1",            (.05,  10,  -6), []),                       # the spike itself, macro. The ring token plants here.
( 11.9,  20.5, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-divergence-v1",0,14.6,20.4)]),  # 'The chart is right' SUMMONS the chart
( 20.6,  31.0, "world-share-office-queue-v1",  (.05,  16,  -8), [("ev-divergence-v1",0,22.0,31.0)]),      # foundry vs empty boardroom = the two lines
( 31.0,  41.4, "world-gpu-crate-dock-v1",          (.04, -12,   8), [("ev-divergence-v1",0,31.0,41.0)]),      # builders up 300%, hyperscalers flat
( 41.4,  45.6, "world-statement-kitchen",        (.06,   8, -10), []),  # "owns a piece of you" - a PUNCH plate, bare by rule: a 3.4s dock on a 4.2s beat is a drive-by (cadence: under ~8s, one piece or none); the balloon slide keeps its real hold at 6:15
( 45.6,  54.0, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 54.0,  63.0, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 63.1,  71.3, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,63.5,71.2)]),  # the cyclical trauma: returns -> capital -> oversupply
( 71.3,  78.3, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 78.5,  90.0, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 90.0, 102.8, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,85.4,96.0),("ev-railway-gdp-tile-v1",0,96.5,102.5)]),
(103.0, 115.0, "world-dotcom-server-room-v1",    (.04, -10,   6), [("ev-capital-formation-v1",0,103.0,115.0)]),  # the internet's 7% of GDP
(115.0, 128.8, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,115.0,128.5)]),  # "I went and pulled a version myself"
(128.9, 140.0, "world-pressure-gauge-v1",        (.05, -14,   8), [("ev-tnx-two-eras-v3",0,129.0,140.0)]),   # the rate trigger, as an instrument
(140.0, 147.6, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,140.0,147.5)]),
(147.7, 166.8, "world-broadcast-set-v2",         (.04, -12,  -8), [("ev-tnx-two-eras-v3",0,148.0,157.0)]),  # their line on the record, then the racetrack
(166.8, 175.9, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(176.2, 180.9, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(181.0, 192.0, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,181.0,195.8)]),          # Karp on CNBC
(192.0, 203.0, "world-budget-burndown-v1",       (.05, -12,   8), [("ev-uber-adoption-v1",1,192.5,203.0)]),  # Uber burned the annual budget by April
(203.0, 213.6, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,203.0,212.0)]),  # "can't draw a line to what you're shipping"
(213.9, 223.7, "world-exhibition-hall-morning-v1",(.05, -14,   6), [("ev-three-manias",0,214.0,223.5)], "cut"),      # the fair the morning after = the trough
(223.8, 234.0, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,224.0,234.0)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(234.0, 244.5, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(244.8, 248.0, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(248.1, 255.8, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(255.8, 265.7, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,256.0,265.5)]),  # the borrowing, as an object
(265.8, 276.0, "world-index-board-swelling",     (.04, -10,   8), [("ev-ig-credit-weighting-v1",0,266.0,276.0)]),  # one sector crowding the index
(276.0, 285.7, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,276.0,285.5)]),  # money that sat in utilities
(285.7, 303.0, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,286.0,297.0)]),
(303.0, 312.0, "world-lease-contracts-bound",    (.05, -14,   8), [("ev-doc-leases",0,303.0,312.0)]),        # bound contract volumes past the frame
(312.0, 319.0, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,312.0,319.0)]),        # a contract pinned to the site fence
(319.0, 328.0, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), [("ev-doc-macdonald",0,319.0,328.0)]),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(328.0, 335.9, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,328.0,335.5)]),  # POOL: what investors believe future cash flows are worth
(335.9, 342.7, "world-orderbook-stamped-v1",     (.05, -12,  -6), []),  # the historical blind spot: debt-financed overinvestment
(342.7, 352.6, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(352.6, 358.6, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(358.6, 364.2, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(364.7, 375.0, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,365.0,375.0)]),# it was railway CERTIFICATES
(375.0, 383.0, "world-exchange-floor-1845"   ,    (.05,  12,  -6), [("silicon-antidote-s02-valuation-bubble-v1",0,375.0,383.0)]),
(383.0, 392.2, "world-target-date-envelope-v1",  (.04, -10,   6), [("silicon-antidote-s02-valuation-bubble-v1",0,383.0,392.0)], "cut"),  # the default your retirement sits in
(392.5, 402.2, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,392.5,402.0)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(402.4, 408.7, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(409.7, 420.7, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,410.0,420.5)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(421.2, 432.0, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,421.5,431.5)], "cut"),                       # railway steel sat 20 years; compute depreciates
(432.0, 443.0, "hero-contract-ovens-v1",                   (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,434.9,443.0)], "cut"),  # orders in, slots gone  # ^REGISTER: the line issuing sealed contracts - orders in, slots gone
(443.0, 454.6, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,443.0,454.5)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(454.9, 466.0, "hero-barbell-v1",                       (.05,  12,   6), [("ev-test-scorecard-v1",0,455.5,486.5)]),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(466.0, 476.0, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(476.0, 486.8, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(486.9, 496.0, "world-two-rooms-divergence-v1",  (.05, -12,   6), []),
(496.0, 503.2, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(504.4, 513.9, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(508.2, 522.0, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,508.5,522.0)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(523.3, 533.0, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,523.5,533.0)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(533.0, 543.9, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,533.0,540.0),("silicon-antidote-s09-capacity-penalty-v1",0,540.0,543.8)]),
(544.3, 554.0, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,544.5,554.0)]),  # every line marked through - sold out
(554.0, 562.0, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,554.0,562.0),("silicon-value-software-bubble-s13-teacher-stamped",1,556.5,566.0)]),  # the blank price card
(562.0, 567.8, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,562.0,567.5)]),  # the most vertical line is steel
(567.9, 576.7, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), []),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(577.1, 588.0, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(588.0, 600.0, "world-korea-port-v1",            (.05,  12,   6), [("sovereign-memory-infrastructure-s05-teacher-stamped",0,588.2,595.2)]),  # the geographic monopoly - memory leaving Korea  # s05 carries NO figure at all; 7.0s and gone, and it takes the stage alone rather than the narrow rail
(600.0, 612.0, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-instrument-memory",0,600.0,612.0)]), # the instrument, method and threshold
(612.0, 628.0, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",0,612.0,622.0)]), # THE FLIP: a position deliberately reduced
# ── P6 CLOSE ───────────────────────────────────────────────────────────
(628.3, 633.3, "world-modern-certificate-v1",    (.05, -12,   6), [("silicon-reality-gap-s13-teacher-stamped",0,628.5,633.2)]),  # advanced memory is no longer swappable
(633.6, 641.0, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(641.0, 648.7, "world-club-interior-papered",    (.05, -10,  -6), []),                       # papered the walls of bankrupt clubs
(649.0, 656.0, "beat-03-008-009-physical-capacity-gate-v1",                       (.04,  10,   6), [("ev-test-scorecard-v1",0,649.2,656.0)]),  # POOL: the gate to physical capacity - scarcity is what they sell
(656.0, 663.6, "world-scales-coin-paper-v1",     (.05, -12,   8), []),  # vulnerability vs opportunity - EVIDENCE PULLED: the s15 slide reads "Opportunity."
(663.8, 675.0, "beat-05-002-strategic-chokepoints-v1",                    (.05,  14,  -6), []),  # EVIDENCE PULLED: antidote-s15 is a buy directive + third-party branding  # POOL: the world reorganizing around chokepoints - they're the steel
(675.0, 691.2, "world-listing-barge-v1",         (.05, -10,   6), []),  # accidental concentration, sold as safety
(691.3, 697.2, "beat-06-017-018-diworsification-v1",             (.06,  10,   8), []),                       # FINAL TRIAD: steel used / paper believed  # POOL: diworsification - the paper gets believed
(697.7, 712.0, "beat-04-001-buyer-behavior-v1",                       (.04, -12,   6), []),                       # CTA: you now have the test  # POOL: now look at buyer behaviour - the assignment
(712.0, 721.3, "beat-06-001-003-index-product-elevator-v1",            (.05,  12,  -8), []),                       # future pacing: which half of your portfolio is steel  # POOL: open the other elevator: your index fund
(721.4, 723.1, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
