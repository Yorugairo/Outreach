"""Steel and Paper — Script F SHOT TABLE. AUTHORED, not allocated.

One row per window. Each plate was chosen because its saved `semantic`
depicts the beat it sits under; each dock was chosen because that document
proves the claim being spoken. The density rules are the CHECK on this
table, never its source.

    (start, end, plate_id, ken_burns(scale, x, y), [docks][, exit[, species]])
    dock = (evidence_id, slot, enter, exit)
    exit = optional authored 6th element ("cut" | "wipe_right"); the default
           is mechanical - docks -> wipe, bare -> cut (doc 29 Part 6).
           Write None here when a row carries species but no authored exit.
    species = optional 7th element (doc 29 s9.27 MOTION MENU, P35 T7): a list of
           {"kind": ..., "at": <s>, "dur": <s>, "target": {...}} dicts. at/dur are
           episode seconds on the same clock as dock enter/exit. kind is one of
           punch | callout | focus_zoom | spotlight | squiggle | pull_back |
           plate_life | beat_freeze | radial | push. THE TARGETING LAW: a species
           that points, circles, zooms, spotlights or underlines takes its target
           as a DECLARED coordinate - nobody eyeballs a pixel; the player resolves
           it at render time (resolveTarget). Target kinds:
             {"kind":"datum","index":n[,"series":i]}  a ledger-page value or a chart
                                                     dock series point (series i for dense)
             {"kind":"point","x":0..1,"y":0..1[,"semantic":"..."]}  a plate coordinate
                                                     as a fraction of the frame, for the
                                                     semantic region the author names
             {"kind":"region","x0":..,"y0":..,"x1":..,"y1":..}  fractions of the frame
             {"kind":"span","from_word":n,"to_word":m}  caption word indices
           plate_life needs no target (its target is the plate); beat_freeze,
           radial, push take point | region; every other kind REQUIRES a target
           and a row without one is a HARD BUILD ERROR naming the row and the
           kind (s9.27: "a species with no declared target does not fire" - the
           build fails rather than dropping it). Exclusivity (s9.28 C3): a row
           carries at most ONE camera move (punch | focus_zoom | pull_back), and
           never one over an authored Ken Burns (scale > 0) - build error naming
           the row; the motion gate's M09 mirrors it on the compiled timeline.
           The pivot's reversal takes no species (s9.28 C4): validate_species
           checks a pivot_span, which the parent wires from the ledger later -
           the build passes None for now. The list is emitted verbatim as
           scene["species"]; the gate counts species events per the s9.27
           "Gate treatment" column (plate life steps at 10 fps).

A plate_id of the form "ledger:<series-id>:<variant>[:<emphasize>[:<quiet_zone>]]"
places a LEDGER PAGE world instead of an image plate (doc 29 s9.26 / s9.28,
P35 T4), e.g. "ledger:ev-trim-proof-v1:bars:7:right": the builder reads
evidence/objects/<series-id>.series.json, emits world.kind = "ledger" with
world.page = the ledger_page.v1 spec, and the player DRAWS the page (roll
0.6s, bleed 2.8s, outline 0.8s, build 3.0s from the scene start; the hold
after that is still, s9.28 C5). variant is line|bars|race|decline|progress;
emphasize is the datum index; quiet_zone is left|right (where docks land,
s9.28 B3). Docks on the row attach as on any plate. A missing series file
or a series that fails the page validator is a hard build error naming the
row. The motion gate counts the page's build beats as visual events and its
start as an evidence entry (s9.28 D1/D2).

Ken Burns is authored per shot: push in on arrivals and reveals, pull back
on reflection, drift laterally across a wide world. Scale is the doc 29
range (1.00 -> 1.04 over the shot), x/y in px; on a page it is capped to a
slow push by the player (s9.26 rules / C3).
"""

W = [
# ── P1 OPEN ────────────────────────────────────────────────────────────
(  0.0,  7.7, "world-spike-desk-v1",            (.05,  10,  -6), []),                       # the spike itself, macro. The ring token plants here.
( 7.8,  16.6, "world-adviser-signature-v1",         (.04, -14,   6), [("ev-bravos-original-v1",0,9.5,50.4)]),  # THEIR chart, their two lines - held through the credit and both reads (topic-governed exit)
( 16.7,  29.1, "world-share-office-queue-v1",  (.05,  16,  -8), []),      # the original persists overhead
( 29.1,  50.4, "world-gpu-crate-dock-v1",          (.04, -12,   8), []),      # "so here's the original" - credit where due
( 50.4,  57.3, "world-statement-kitchen",        (.06,   8, -10), [("ev-divergence-v1",0,50.4,70.9)]),  # OUR chart takes over: semis erupt at "second line", memory at "one layer never drew"; exits when the topic does ("wrong address")
( 57.3,  71.3, "world-three-notch-slate-v1",     (.05, -10,   6), []),  # the test named, as an object
( 71.3,  86.0, "world-signature-nib-v2",         (.04,  12,   8), []),  # 'thirty seconds a stock'
( 86.2,  92.2, "world-hype-machine-v2",          (.05, -16,  -6), [("silicon-reality-gap-s04-teacher-stamped",0,86.8,92.2)]),  # the cyclical trauma: returns -> capital -> oversupply
( 92.2,  97.0, "world-assay-sort-v1",            (.04,  10,   6), []),  # the diagnostic matrix - the machine you can test
# ── P2 ENGINE — the steelman ───────────────────────────────────────────
( 97.2,  104.2, "world-steelman-build-v1",        (.05, -12,   8), []),  # the price-deflation capital cycle
( 104.2, 113.6, "world-navvy-cutting-v1",         (.05,  14,  -8), [("ev-railway-index-v1",0,104.2,113.6),("ev-railway-gdp-tile-v1",1,112.5,122.1)]),  # operator: Britain tile HOLDS through the dotcom plate; the yardstick's enter is its exit
(114.0, 121.9, "world-dotcom-server-room-v1",    (.04, -10,   6), []),  # the internet's 7% of GDP
(121.9, 143.8, "world-ledger-page-v1",           (.05,  10,  -6), [("ev-capital-formation-v1",0,122.1,172.2)]),  # "I went and pulled a version myself"
(144.0, 161.7, "world-pressure-gauge-v1",        (.05, -14,   8), []),   # the rate trigger, as an instrument
(161.7, 173.7, "world-viaduct-train-rain-v1",    (.04,  12,   6), [("ev-tnx-two-eras-v3",0,172.3,190.4)]),
(173.9, 204.3, "world-broadcast-set-v2",         (.04, -12,  -8), []),  # their line on the record, then the racetrack
(204.3, 218.3, "world-sell-ticket-v1"      ,     (.05,  10,   8), []),  # record earnings vs valuation - the profit-taking case
(218.9, 226.4, "world-trading-desk-dark",        (.05, -10,  -6), []),                       # "here's where their own chart gets strange"
# ── P3 GAP · unit 1: the evidence walk ─────────────────────────────────
(226.6, 231.1, "world-internal-memo-v1",         (.04,  12,   6), [("ev-doc-karp",0,226.6,235.3)]),          # Karp on CNBC
(231.1, 235.3, "world-budget-burndown-v1",       (.05, -12,   8), []),  # Uber burned the annual budget by April
(235.3, 244.6, "world-empty-racks-v1",           (.04,  10,  -8), [("ev-uber-adoption-v1",0,235.5,252.0)]),  # "can't draw a line to what you're shipping"
(244.9, 253.8, "world-exhibition-hall-morning-v1",(.05, -14,   6), [], "cut"),      # the fair the morning after = the trough
(253.9, 265.4, "hero-countercase-v1",                  (.05,  14,  -6), [("ev-three-manias",0,254.1,265.6)]),      # the trains ran through the crash  # ^REGISTER: the wave, the ruin, one green shoot - WHAT SURVIVES
(265.4, 277.4, "world-dawn-factory-v1"  ,           (.04, -10,   8), []),  # the inescapable physical reality  # s03 carries ONE figure (97%); clears at 7.0s so the plate breathes
(277.8, 281.4, "world-molten-pour-v2",       (.05,  10,   6), []),                       # u5 rehook: "who's paying for the steel this time"
# ── P3 GAP · unit 2: the debt unit ─────────────────────────────────────
(281.5, 290.5, "world-treasury-cash-count",      (.05, -12,  -8), []),  # cash generation vs paper gains
(290.5, 295.6, "world-bond-prospectus",          (.05,  12,   6), [("ev-debt-issuance-v2",0,290.7,300.9)]),  # the borrowing, as an object
(295.7, 300.9, "world-index-board-swelling",     (.04, -10,   8), []),  # one sector crowding the index
(300.9, 317.8, "world-substation-feed-v1",       (.05,  14,  -6), [("ev-ig-credit-weighting-v1",0,301.0,317.7)]),  # money that sat in utilities
(317.8, 326.3, "world-datacenter-aisle-v1",      (.04, -12,   6), [("ev-capex-consensus-v1",0,318.2,327.6)]),
(326.3, 330.1, "world-lease-contracts-bound",    (.05, -14,   8), []),        # bound contract volumes past the frame
(330.1, 338.3, "world-datacenter-shell",         (.05,  12,  -8), [("ev-doc-leases",0,330.1,348.8)]),        # a contract pinned to the site fence
(338.3, 348.8, "beat-05-017-018-market-prices-cashflows-v1",              (.05, -10,   6), []),     # POOL: conduits pumping into the built city - every dollar consumed by the buildout
(348.8, 360.1, "beat-05-006-listed-cash-flow-market-v1",                  (.04,  10,   8), [("ev-doc-macdonald",0,349.0,367.7)]),  # POOL: what investors believe future cash flows are worth
(360.1, 369.6, "world-orderbook-stamped-v1",     (.05, -12,  -6), [("ev-capex-funding-v1",0,368.5,385.3)]),  # the historical blind spot: debt-financed overinvestment; capex-vs-cash chart holds through "nobody is charting"
(369.6, 383.6, "world-signature-close",          (.05,  12,   6), []),                       # "they signed a promise, in a year that looked good"
# ── P4 PIVOT ───────────────────────────────────────────────────────────
(383.6, 391.9, "world-license-cabinet-v1",  (.06, -10,  -8), []),                       # "where most people get the whole thing wrong"
(391.9, 399.6, "hero-wrong-bubble-v1",              (.06,  10,   6), []),                       # THE REVERSAL: paper endless, hardware exact  # ^REGISTER: THE REVERSAL - the chip tower beside the basket of paper
(400.3, 406.0, "world-certificate-wall-v1",      (.05, -14,   8), [("ev-railway-mileage-v1",0,400.7,410.2)]),# it was railway CERTIFICATES
(406.0, 410.0, "world-exchange-floor-1845"   ,    (.05,  12,  -6), []),
(410.0, 427.9, "world-target-date-envelope-v1",  (.04, -10,   6), [("ev-weight-check-v1",0,410.2,428.3)], "cut"),  # the default your retirement sits in
(428.5, 438.2, "hero-sp500-double-failure-v1",          (.05,  14,   8), [("ev-smh-drawdown-v3",0,428.5,438.8)]),   # if the names fall by half  # ^REGISTER: the index as towers cascading paper onto a crowd
(438.4, 445.0, "world-spike-certificate-ring-v2",(.06, -8,   -6), []),                       # RING TOKEN RECONTEXTUALIZED: certificate curls onto the spike
(446.0, 457.3, "world-railway-acts-desk-v1",     (.05,  10,   8), [("ev-railway-index-v1",0,446.2,457.5)]),  # 1845 is the proof
# ── P5 REFLECTION ──────────────────────────────────────────────────────
(457.8, 468.9, "world-circuit-terrain-v1",       (.05, -12,   6), [("ev-railway-mileage-v1",0,458.1,468.9)], "cut"),                       # railway steel sat 20 years; compute depreciates
(468.9, 473.9, "world-hbm-die-stack",                      (.04,  12,  -8), [("silicon-antidote-s11-teacher-stamped",0,468.9,473.9)], "cut"),  # orders in, slots gone  # ^REGISTER: the die stack itself - allocation sealed (ovens plate RETIRED: read as bread out of context, operator)
(473.9, 509.9, "hero-korea-italy-v1",                        (.05, -10,   8), [("sovereign-memory-infrastructure-s10-teacher-stamped",0,473.9,488.7),("ev-test-scorecard-v1",0,492.3,543.0)], "cut"),  # sovereign stacks  # ^REGISTER: two continents, one hardware - sovereign stacks
(510.8, 522.9, "hero-barbell-v1",                       (.05,  12,   6), []),  # the three questions  # ^REGISTER: the balance: gold one side, paper the other - THE TEST
(522.9, 532.8, "beat-04-014-evidence-hierarchy-v1",                        (.05, -14,  -6), []),  # steel answers / paper answers - the sort  # POOL: contracts and shipments beat narrative - the test's own logic
(532.8, 543.4, "world-workbench-triad-v1",       (.04,  10,   8), []),                       # "thirty seconds a holding. run your top five tonight"
(543.5, 552.6, "world-two-rooms-divergence-v1",  (.05, -12,   6), [("ev-divergence-v1",0,543.6,560.8)]),  # the chart RETURNS at the line that names it
(552.6, 559.7, "beat-04-015-bottleneck-boom-v1",                        (.04,  12,  -8), []),  # the test, administered in public  # POOL: a bottleneck boom before a bubble
(560.8, 570.0, "world-seoul-fab-skyline-v1",     (.05, -10,   6), [], "cut"),  # the global DRAM battlefield  # extended to 9.0s so 500% / +716% can actually land
(564.5, 577.6, "hero-fab-constraint-v1",                 (.05,  14,   8), [("ev-krx-memory-v3",0,564.8,578.7)], "cut"),     # SK hynix, +517%  # ^REGISTER: the cleanroom line - SK hynix, the constraint itself
(578.9, 585.1, "hero-hbm-bandwidth-v1",                        (.06, -8,   -6), [("silicon-reality-gap-s07-hbm-stack-v1",0,579.2,585.1)]),   # dies stacked edge-on  # ^REGISTER: the die with bandwidth streaming - HBM physics
(585.1, 595.2, "world-dram-terrain-v1",          (.05,  10,   6), [("ev-hbm-wafer-ratio-v1",0,585.1,595.2),("silicon-antidote-s09-capacity-penalty-v1",1,589.1,595.2)]),
(595.5, 598.0, "world-allocation-board",         (.05, -12,   8), [("ev-dram-contract-v1",0,595.6,598.0)]),  # every line marked through - sold out
(598.0, 619.2, "world-laptop-shelf",             (.04,  12,  -6), [("ev-dram-contract-v1",0,598.0,606.9),("silicon-value-software-bubble-s13-teacher-stamped",1,608.1,619.2)]),  # the blank price card
(619.2, 625.3, "world-steel-mill-night",         (.05, -10,   6), [("silicon-antidote-s02-memory-triopoly-v1",0,619.2,625.3)]),  # the most vertical line is steel
(625.4, 634.3, "beat-04-013-guidance-not-gospel-v1",                       (.04,  10,   8), [("ev-tripwire-board-v1",0,630.0,645.8)]),                       # "it doesn't care what you were hoping to conclude"  # POOL: guidance is not gospel - the test doesn't care what you hoped
# ── P5 · the tell ──────────────────────────────────────────────────────
(634.6, 646.0, "beat-04-003-classic-cycle-counterargument-v1",         (.05, -14,  -6), []),  # paper-bubble mechanics - their tripwire, then ours  # POOL: the strongest argument against this video - their tripwire
(646.0, 660.4, "world-korea-port-v1",            (.05,  12,   6), [("ev-memory-monitor-v1",0,646.1,660.4)]),  # the monitor shows its OWN readings (s05 slide RETIRED here: no figure, partial match)
(660.4, 662.9, "world-memory-wafer-v1",          (.04, -10,   8), [("ev-trim-proof-v1",0,660.4,673.1)]),  # instrument card RETIRED (redundant with monitor analyst chart); objection card holds through the readings
(662.9, 683.5, "world-unwind-desk-v2",           (.05,  10,  -8), [("ev-hbm-export-series",1,662.9,673.1),("ev-june-print-v1",0,673.3,683.5)]), # THE FLIP: a position deliberately reduced - de-risked on camera
# ── P6 CLOSE ── re-authored to Script G's close (the beats reordered) ──
(683.5, 690.3, "world-modern-certificate-v1",    (.05, -12,   6), []),                       # certificates wear nicer names now - target-date, "the market"
(690.3, 694.6, "world-spike-certificate-ring-v2",(.05,  12,   8), []),                       # RING ECHO: the spike, one more time
(694.6, 705.2, "world-club-interior-papered",    (.05, -10,  -6), [("ev-holds-stack-v1",0,701.73,727.63)]),  # THE VERDICT STACK: nine proofs, "In 1850" through the monitor, burst on "go further than Bravos" (item beats in the dock entry). Window -0.77 to the post-CNBC clock to match the re-clocked stack members (enter-wash lead 1.14s preserved; exit rejoins clear_at 726.98)
(705.2, 717.1, "beat-03-008-009-physical-capacity-gate-v1", (.04,  10,   6), []),  # stack hosted on the club-papered row above
(717.1, 725.7, "world-listing-barge-v1",         (.05, -10,   6), []),  # a fifth of your index - the card holds for the VERDICT beat, not here (no reuse)
(725.7, 760.3, "beat-05-002-strategic-chokepoints-v1", (.05,  14,  -6), [("ev-hynix-steel-v1",0,730.3,759.7),("ev-memory-arithmetic-v1",1,741.2,759.7)]),  # purpose-built (operator): hynix price WITH the profit under it - not a house of cards
(760.3, 773.0, "world-listing-barge-v1",         (.05, -10,   6), [("ev-index-concentration-v1",0,760.3,772.8)]),  # the verdict: the safe version IS the certificate
(773.0, 778.6, "beat-06-017-018-diworsification-v1", (.06,  10,   8), []),                   # FINAL TRIAD: steel used / paper believed / discovered at once
(778.6, 796.5, "beat-04-001-buyer-behavior-v1",  (.04, -12,   6), [("ev-test-scorecard-v1",0,778.6,787.1)]),  # CTA: you now have the test - the scorecard returns at its recap
(796.5, 805.0, "beat-06-001-003-index-product-elevator-v1", (.05,  12,  -8), []),            # future pacing: which half of your portfolio is steel
(805.0, 806.5, "world-spike-rest-v2",            (.03,   6,   4), []),                       # RING ANCHOR: the spike stays on the desk. Lamp almost out.
]
