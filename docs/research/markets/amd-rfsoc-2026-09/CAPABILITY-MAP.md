# AMD RFSoC "treason" episode - capability map (explorer, 2026-09-26)

Read-only recall. Source of truth: lane B worktree `p69-s90` at `1fffa97`
(`docs/content-video-engine/CAPABILITIES.md`, 478 lines). Line numbers below are
lane-B CAPABILITIES.md unless another path is named. docs_find layers were stale
once (09-23), so every hit below was re-read in CAPABILITIES.md itself.

Status legend: WIRED/LIVE = in the engine + golden; DRAFT = built, awaits an HG;
CANDIDATE = a recipe proved on a test bed, not yet used in an approved cut.

"first use" below is `effects_card.py "<id>"`'s field: `none` = no approved cut
carries it yet (most of the P70-P72 Bravos verbs are in that state).

---

## Beat 1 - The accusation (Patel's post on X; AMD's reply)

Serves it:
- **Press card dock + the press STACK** - CAPABILITIES.md:125 WIRED (P50 T3).
  Recall: CAPABILITIES.md:125 "`press_card.py <screenshot> --headline-box --source --phrase-box --out --meta`: the crop
  tool (PIL, no network) cuts a screenshot to its headline box ... the quoted phrase: a `callout` with
  `form: "underline"` ... draws the squiggle's hand-drawn underline under the phrase on the card's LIVE geometry".
  Use-when: "the sentence QUOTES a headline or a claim with a masthead (row 1) ... the stack when three claims
  land in a row". Golden `press-stack`; card `dock_kind:press` status wired, **first use: none**.
  Limits (row 125): "a press dock on a `ledger:` plate is a build error"; "the build-loop seam ... has unit tests,
  not an episode build - the first cut with a press row closes it". A press card holds with `idle: hold`
  (CAPABILITIES.md:120, P72 T19).
  Fit: Patel's X post = press card 1 (masthead "X / @dylan522p, <date>"), AMD's statement = press card 2, the
  Puzhi/crowdfunding listing = press card 3 -> the stack of three claims is exactly the row-125 use-when.
- **Record-document species** (typewriter + per-word highlighter on the narrator's words) - CAPABILITIES.md:19 LIVE,
  first use Steel and Paper build-f @ 226.6 s. Recall: CAPABILITIES.md:19 "Use when: the sentence QUOTES someone's
  claim and the words themselves are the proof". Best for AMD's reply read word-for-word ("diversion").
- **Quote on the word it opens** (caption) - CAPABILITIES.md:26 (P72 T14): "`build_caption_pages.place_quotes`
  moves an opening quote onto the word it opens".
- **Ring on a press card / prop** - CAPABILITIES.md:267 (P69 T65) - but it REQUIRES a number: "The compiler requires the
  NUMBER (a digit in `label`) and the POINTING". Usable on the listing card's "$1,000", not on the word "treason".
- **The "?" at the unknown** - CAPABILITIES.md:116 WIRED 2026-09-26 (P71 T18): `{"kind": "unknown", ..., under: "blur"}`
  "lays `#unkveil` ... over the live press cards' boxes" - the "who is right?" beat over the pile. Limit (row 116):
  "CHN's collage also SHRINKS to ~0.47 as it recedes - ... not built, so ours blurs in place".
- **Stamps / seal** - a stamped chip is a gold seal with optional `ring_text` / `ring_text_bottom` laid on two
  half-arcs (CAPABILITIES.md:115, P70 T1b "A STAMPED CHIP IS A GOLD SEAL"); the stamp is punctuation, landing just
  AFTER its word (CAPABILITIES.md:238, E99 s112). The "?" glyph is refused on the stamp form (row 116). A word
  stamp ("ACCUSED", "DIVERTED") over the pile = a stamped chip / `arrive: stamp` prop (CAPABILITIES.md:91).
- **Heads usable** (E68) - CAPABILITIES.md:39: "a public figure's cutout docks beside its datum
  (`assets/heads/manifest.json` -> `approved`, `render_eligible: true`)". A Patel head would need intake + approval.
- Bravos coverage: BRAVOS-USE-WHEN.md:97 "T43 Quote card with a grayscale portrait: TYPE · HAVE"; :121 "F5
  Highlighter band on the quoted phrase ... HAVE"; :127 "F9 Newest press card lit, older ones stepped back ... HAVE".

Gap: none central. A social-post card (avatar + handle + post body, not a newspaper masthead) has no dedicated
form - `docs_find "tweet"` 0 hits, `"post on X"` 0 relevant hits. The press card crops ANY screenshot, so a
cropped X post works with `source: "X / @handle"`; the masthead strip is newspaper-styled. Size S if wanted
(a `press.style: social` masthead variant) - no backlog row carries it.

## Beat 2 - The price wedge ($36,000 list vs ~$1,000 quoted; 36x)

Serves it:
- **Bars page + `chart_to compare` (E76)** - CAPABILITIES.md:31 WIRED (P57 T11/T12): "THE QUOTED METRIC BECOMES THE
  NUMBER THE VIEWER FEELS"; "a comparator the row cannot reproduce within 0.5 % is refused, never tweened; a morph
  with no comparator label is refused". CAPABILITIES.md:254 "A bar changes its own value on a compare ... the bar
  moves, not only its number" (golden `bar-value-morph`). Card `chart_to:compare` wired, **first use: none**.
- **Re-value then the ratio** - CAPABILITIES.md:255 WIRED (P71 T24) + recipe `recipe:revalue-then-the-ratio`
  (effects/recipes/revalue-then-the-ratio.json, CANDIDATE): "a bracket from the re-valued bar to its neighbour, the
  multiple written as its label (T50 on bars)". Here: the $36,000 bar "re-values" DOWN to the $1,000 quote? No -
  `from` must be a sourced OLD value of the SAME bar ("then -> now"); two different channels are two bars. Use the
  plain two-bar page + bracket instead.
- **Bracket with a ratio label** - CAPABILITIES.md:276 (level_join) truth rule: "a label whose number is not the
  page's arithmetic at its written precision (a difference; `x` a ratio ...)" - "36x" is checked, not trusted.
- **The equation row** - CAPABILITIES.md:123 WIRED (P70 T6): "the row is computed from each term's WRITTEN text ...
  `1 x 1 x 1 = 3` and `$100 x 5% = $500` are refused as untrue". `$36,000 / $1,000 = 36x` passes the unit algebra:
  build_scene_timeline_f.py:5791 `if acc == d: return EQUATION_RATIO` ("/ of a unit by itself is a ratio").
  Golden `equation-halving`; first use none.
- **Balance scale** - CAPABILITIES.md:124 WIRED (P70 T7) - but "no figure reaches the scale - a digit, a numeral, a
  money or percent sign" (refused, "pointing to two bars"). So the balance can weigh the NAMES ("the licence" vs
  "the grey market"), never the two prices.
- **Scale-out / projected overtake** - CAPABILITIES.md:256 (P71 T25): an ESTIMATE rising past the leader; not this
  beat (no projection). Its Limit names the missing form: "D40's bracket runs to TODAY's bar with a ratio ("10X")
  where ours runs to #1 with the gap".
- **Breakthrough bars** - CAPABILITIES.md:104: a bar that overflows a stated scale while the axis rescales. Inverse
  of this beat (here the small bar is the surprise); probably not wanted.
- **Log scale** - exists on LINE pages only: ledger_page.py:142 `AXES_KEYS = ("overflow", "log", ...)`,
  :4914 `math.log10(v) if axes.get("log")`. Not needed: at 36x on a linear bars page the $1,000 bar is a 1/36
  sliver, which IS the claim (E53's honest zero).
- **Spread (E53 s6 "The gap is the argument")** - OPERATOR-RULINGS.md:1754: "When a page compares what is set
  against what is paid, the region BETWEEN them is the claim, and it is drawn: the `spread` species". Only if a
  TIME SERIES of grey-channel prices exists (none on disk; research in flight).

Gap (S): no "ratio bracket between two bars" is a named, golden'd single form - the recipe members exist
(`page_species:bracket` on bars, T50) but the "10X"-style bracket to a neighbour is the HG1-pending dial named in
CAPABILITIES.md:256's Limit. Proven path today: two-bar story page -> figure on each bar -> equation row or a
bracket with "36x". Nothing to build unless the operator wants D40's white "10X" bracket look.

## Beat 3 - The lead time (40-52 weeks via the channel vs "available now" grey)

Serves it:
- **Range bar** - ledger_page.py:14 "(P69 T8d: a value may be a RANGE [lo, hi] - the bar at its near end, a band to
  the far one, written "lo–hi")"; :91 "the page writes the range as the source states it, never a midpoint". So
  "40–52 weeks" is one honest bar.
- **Two clocks recipe** - effects/recipes/two-clocks.json (CANDIDATE, proved on H row 19): "two durations on ONE unit
  (years): the long bar deemphasized, the short bar crimson ... the short one's figure on its word". Use-when: "a
  contrast of two clocks where the SHORT one is the claim". Exact fit (52 weeks vs "in stock").
  Caveat: a zero-week bar - "available now" has no duration; the page needs a real figure (e.g. the listing's
  shipping days) or the short bar is a zero bar (BAR_FIELDS allow it; members refuse "a zero ... bar").
- **Span** - CAPABILITIES.md:128 WIRED: "a shaded REGION between two x positions behind the page's chart ... A
  `bracket` MEASURES two data; a `span` NAMES a stretch of time" - needs a line page with a date x.
- **Lead-lag bracket** - CAPABILITIES.md:402 WIRED 2026-09-26 (P71 T27): computes the lag between TWO SERIES' data
  ("`lag_text`: days / weeks / months / years by length"). Only fits if there are two dated series; not this beat.
- **Decade ruler** - CAPABILITIES.md:122: "`settle: [2-4 consecutive decades]`", "years not four-digit ... refused" -
  wrong grain for weeks.

Gap (M, low-central): a CALENDAR / countdown form (weeks ticking, a queue that does not move vs a parcel that
ships) - `docs_find "calendar"` hits only prop PNGs (`prop-upcoming-catalysts-calendar-v1.png`) and the SCML row;
`"lead time"` 0 relevant hits; no species in scripts/species/ (listed: breakthrough, callout, countarray, newsreel,
press, record, ring, spotlight, thread, tippill, trace, treemap, spiral, freeze, axis_tag, level_join, ruler,
equation, balance, agenda, tiers, checklist, figure, vecmap, flow, lens, verdict, span, solo, compare,
lit_stretch, chip, melt). No backlog row or P70-P72 slice carries it. The two-clocks bars page covers the claim.

## Beat 4 - The route (US maker -> distributor -> reseller -> China)

The 09-10 Bravos gap list is CLOSED for all four species the brief names. Recall:
docs/content-video-engine/EXPLORATION-REVIEW-2026-09-10.md:50-55 listed "the press card ... ABSENT", "the live
vector map ... ABSENT", "the flow diagram ... ABSENT", "the treemap with X marks ... RECORDED"; all four were built
2026-09-11 (P50 T3/T4/T5/T6): CAPABILITIES.md:125, :127, :129, :131.

Serves it:
- **Flow diagram** - CAPABILITIES.md:127 WIRED (P50 T4; P71 T11 ring + tokens; P71 T17 hub + fail).
  Recall: CAPABILITIES.md:127 "`{"kind": "flow", ..., "nodes": [{id, icon, label}], "edges": [[a, b]], "swap":
  {at, node, icon, label}?, "tag": "1973"?}` - ... the nodes land as CHIPS ... the arrows between named chips are
  CLOTHOIDS drawn by length"; "Use when: the sentence EXPLAINS a mechanism - A causes B via C". Golden `flow-swap`.
  Options that fit THIS story:
  - `tokens {n, speed, from_at, glyph?}` - "sends n tokens round every drawn arrow by ARC LENGTH" (golden
    `flow-loop-tokens`) = the part moving down the chain.
  - `fail: {edge, at}` - "a neg-ink disc ... springs in at the edge's midpoint ... with a white X ... the edge
    reddens and each half retracts 12 %" = the licence check that did not hold. Validated on ANY layout
    (build_scene_timeline_f.py:4159 `_validate_flow_fail`), not only the hub.
  - `edge_states: [{at, edges}]` - a changing graph: "each change retracts for .30s then draws each new edge for
    .34s" (build_scene_timeline_f.py:3909-3914) = the legal edge replaced by the bypass edge.
  - `swap` - "on a later word ONE node swaps and the rest stands" = "same chain, a different buyer".
  Limits: 2-6 nodes on the row layout; `tokens` x `edge_states`, `fail` x `edge_states`, `fail` x `operators` are
  mutually exclusive by name (build_scene_timeline_f.py:4059, :4170) - a diversion that REWIRES and a token that
  RIDES the new route need two rows (or a swap). Icons: a flow node / chip glyph must be an SVG -
  build_scene_timeline_f.py:351 `icon_file` returns `ICONS_DIR / f"{name}.svg"` and :3840 refuses anything else
  ("source it and record it in SOURCES.md (A2a), never generate one") - and only FIVE exist
  (`assets/icons/{coins,cpu,factory,landmark,ship}.svg`); E94's 44 woodblock cutouts are PNGs (props / agenda
  rows), not node glyphs. No warehouse / distributor / reseller (person) / customs / antenna / price-tag glyph.
  Node labels are free strings (only non-empty is checked, :3872), so "AMD · $36,000" as a label compiles; edges
  carry no label. R26-384 (lane-A BACKLOG-HISTORY-2026-09.md:991): "at our card size the fail
  disc ... is a small red dot where Bravos's is a badge" - in wave-9 T46d. `species:flow` first use: none.
- **Vector map world** - CAPABILITIES.md:129 WIRED (P50 T5; P71 T22 route tokens + ping).
  Recall: CAPABILITIES.md:129 "`light` (a country: the fill rises to the accent ...), `arc` (`from`, `to`,
  `crossed`?: drawn by length with the nib, an X at the midpoint on `crossed`), `stamp` (... the figure written at
  the centroid)"; "an `arc` takes `tokens: {from_at, n?, speed?}` - dots ride it by length ... and stop as the
  route is cut"; "A `light` or `stamp` takes `ping: true`: ONE ring leaves the place". Goldens `vecmap-arc`,
  `vecmap-route-tokens`. Fit: USA lights, "$36,000" stamps on USA, an arc USA -> CHN drawn and CROSSED on "export
  controlled", then a second arc via a transshipment point with tokens riding it, "$1,000" stamps on CHN.
  Limits:
  - Hong Kong and Singapore are NOT in the map data (checked: `"HKG"` 0 and `"SGP"` 0 matches in
    `assets/maps/world-110m.paths.json`; TWN, MYS, CHN, USA, KOR, JPN, ARE present) - Natural Earth 110m drops
    them. An arc may end at `{kind: mappoint, x, y}` (build_scene_timeline_f.py:3594-3599 validates `from`/`to`
    through `_validate_map_target`), but a mappoint cannot LIGHT (a light targets a country).
  - A fixed 1000x500 equirectangular box; the arc "lifts toward the POLE the two places share"
    (species/vecmap.mjs:208); no central-meridian option (grep `meridian|lon0|wrap|pacific` 0 hits), so a US -> China
    arc likely runs across the Atlantic/Europe, not the Pacific (INFERRED from the code, not rendered - read a frame).
  - R26-382 (lane-A BACKLOG-HISTORY:989): "a scene has one world, so neither a park nor T8b's panels can put a line
    page beside a map" - the price chart beside the map is NOT buildable; recipe `the-chart-beside-the-map`
    (CANDIDATE) pairs a chart CARD with a pinging light instead.
  - R26-383 (:990): "our route map fits the whole continent so the routes read small ... our ping is a thin ring
    where Bravos's blooms". R26-382 and R26-383 are both in wave-9 T46d.
  - `species:arc` / `light` / `stamp` first use: none; recipe `vector-map-named-lit-and-stamped` CANDIDATE.
- **Trace HOPS + stacked stamps** (the crossings-map beat) - CAPABILITIES.md:96 WIRED: "a trace species carries `hop
  {from,to,bow,draw_s,width}` (a bowed arc between two named points" - on a painted plate; the older route form.
- **Dock pin (`rel`)** - CAPABILITIES.md:120 (P72 T19): "`rel: {pin: <dock>, inherit?}` rides another dock's read
  and park" - a price-tag card riding the part card.

Gap: none for the diagram itself - the route is the BEST-served beat. Two small gaps: (a) icons for the chain's
roles (S - a Lucide intake with per-file URLs in `assets/icons/SOURCES.md`, A2a); (b) Hong Kong / Singapore on
the map (S - a point-light form or a finer-resolution inset). No backlog row carries either.

## Beat 5 - The rule (the export control as a page; ECCN; the licence line; 2022/2023/2024)

Serves it:
- **E53 s5, a threshold is a RULE** - docs/portable/OPERATOR-RULINGS.md:1748: "A number an institution SETS - a
  policy rate, a target, a threshold, a covenant - is a level to measure against ... It takes a reference rule
  (`axes.hlines`): dashed, in its own colour, named at its end". An export control is a SPEC THRESHOLD: a bars page
  of parts' spec with the control threshold as an `hlines` rule reads "above the line = licence required". Needs
  the rule's actual parameter from research (not on disk).
- **Record-document species** - CAPABILITIES.md:19 LIVE: the rule's text typed + the phrase highlighted as spoken.
- **Press card** of the Federal Register / BIS page - CAPABILITIES.md:125 (masthead = "Federal Register, <date>").
- **The test card (checklist)** - CAPABILITIES.md:325 "Checklist species = THE TEST CARD ... question cells TYPE on,
  answer cells take a marker-highlight sweep"; recipe `test-card-rows` PROVEN. Fit: "On the list? / Licensed
  buyer? / Where did it ship?". Limit R26-300 (lane-A BACKLOG-HISTORY:906): "the checklist species has no type
  option: 19 px cells" below the phone floor.
- **Numbered agenda** - CAPABILITIES.md:47 WIRED: "two to four numbered rows revealed one per word" = the rule waves
  (dates to be sourced).
- **Chapter pill held over an act** - CAPABILITIES.md:249 (P70 T9) + in-place swap :250.
- **Rules on a time axis**: `marks` / `eventbars` are AXES_KEYS on a line page (ledger_page.py:142) - rule dates
  pinned on a sourced series (e.g. AMD China revenue by year); `park_at` (CAPABILITIES.md:119, DRAFT, awaits
  P71-HG1): "it READS in the plot's empty room ... then PARKS to a chip ... beside the datum" - the rule's card
  parks at its date; `axis_tag` (CAPABILITIES.md:274): "the named year becomes an accent pill". The decade ruler
  (CAPABILITIES.md:122) refuses non-decade settles.

Gap (M, central to the mechanics angle): **no data-free EVENT TIMELINE page** - dated milestones on one x with no
series (rule 1 / rule 2 / rule 3 / the listing / the accusation). Page blocks on disk (ledger_page.py `_*_block`):
schematic, y2, bars_out, tiers, panels, treemap, object, share, pie, decline, story, dense, race (+ progress/gauge,
agenda). The schematic (CAPABILITIES.md:278) is "a shape drawn with no data" but only `shape: "hype"|"waves"|
"debt_cycle"`, and refuses "any axes value key (ticks, rules, log, a domain ...)". Nearest today: the agenda
(ordered, undated) or event `marks` on a sourced series. No R26 row or P70-P72 slice carries a timeline page.

## Beat 6 - The chip itself (product photo / prop; schematic; die / board cutaway)

Serves it:
- **Bare prop, stamped / poofed / thrown, resting on the hatch** - CAPABILITIES.md:91 (`arrive: stamp`,
  `prop: True`), :93 (`arrive: "poof"`), :246 ("a bare prop rests on an engraved hatch from the stage light"), :259
  ("A prop goes where the author puts it ... `place: {x, y, w}` ... `moves`"). Cutouts on lane B that fit:
  `assets/icons/cutouts/prop-icon-chiplet-bga-package-v1.png`, `prop-icon-microprocessor-silicon-die-v1.png`,
  `prop-icon-semiconductor-silicon-v1.png`; `assets/props/cutouts/prop-silicon-wafer-semiconductor-v1.png`,
  `prop-ai-pause-roadblock-barrier-v1.png`; Lucide `assets/icons/cpu.svg`. `dock_kind:prop` / `arrival:stamp` /
  `arrival:poof` first use: none. R26-400 (the stamp's ink dims the contact shadow, a bisected regression) is T46a.
- **A prop becomes a mark** - CAPABILITIES.md:261 (P69 T26e): "a prop becomes a MARK mid-page (`chart_to {to:
  "morph", from: "prop:<id>", mark: "b:<i>"`" - the chip prop morphs into the $36,000 bar (beat 2's entry).
- **Photo life** - ComfyUI 2.5D parallax (CAPABILITIES.md:173), the layered plate (:176). A real AMD product photo
  needs intake; E68 (CAPABILITIES.md:39) allows external material "as commentary on a surface ... never full-frame
  as our own".
- **Block diagram of the part** (antenna -> ADC -> FPGA fabric -> DAC) = a flow ROW (CAPABILITIES.md:127); icons
  missing (beat 4).

Gap: **"P71 T20 schematics" are NOT circuit schematics.** CAPABILITIES.md:278: "`schematic: {shape:
"hype"|"waves"|"debt_cycle", ...}` IN PLACE OF `series`" - an economic-cycle curve. No die shot, board cutaway,
exploded view or labelled-parts-on-a-picture form (`docs_find "cutaway"` 0 hits; "3D" hits only the review-only
Blender scene compiler CAPABILITIES.md:213 and the pie's 3D explode :270). Labels on a picture are E56-bound (a
ring on a picture with no number is refused; "a picture's focus is a LIGHT", CAPABILITIES.md:101). Size M-L; no
backlog row. Low-central: the story's mechanics do not need the silicon.

## Beat 7 - "Is it even real?" (counterfeit / recycled / relabelled)

Serves it:
- **The predictions board** - recipe `the-predictions-board` (CANDIDATE) on the chip (CAPABILITIES.md:115):
  "CROSSED on `cross_at` by a two-stroke X"; chip states (P71 T12): "`tick_at` springs a check BADGE", "`state:
  "lit"` rings a chip in a sunflower halo"; the "?" glyph (CAPABILITIES.md:116): "a TEXT "?" ... centred ABOVE
  the card". Fit: three hypothesis chips - DIVERTED / COUNTERFEIT / RECYCLED - a "?" over the board, then a tick
  or a cross as each piece of evidence lands. Refused: "a `tick_at` with a cross ("a thing held or failed, not
  both")", "`tick_at` and `tab` on one chip".
- **Balance scale with a tip** - CAPABILITIES.md:124: "two NAMED forces weighed ... a tip swings 12 deg toward
  `to`" - "diversion" vs "fake", tipping on the evidence word. Names only.
- **Verdict tile** - CAPABILITIES.md:118 (P71 T19; card DRAFT): "Refused by name off a sourced chart ... and on a
  prop, a stamp, a cutout, a press card" - it can NOT judge a chip photo. Its missing gate credit is R26-391 (T46b).
- **Seal with ring text** - CAPABILITIES.md:115 (P70 T1b) - a gold "VERIFIED" / "UNVERIFIED" seal, stamped just
  after the word (CAPABILITIES.md:238 "The stamp is punctuation"). Seal keyline / `seal_gold` notes = R26-361
  (T46b); on a mid-tone photo the seal "turns bronze" (CAPABILITIES.md:121 Limits).
- **Verdict stack / evidence wall** - CAPABILITIES.md:305 LIVE + recipe `verdict-recap` PROVEN - the recap of the
  three claims before the turn; first use Steel and Paper build-f @ 701.73 s.
- **The "?" under blur over the press pile** - CAPABILITIES.md:116 (`under: "blur"`).

Gap (M, central to the TURN): **a two-picture "genuine vs listing" compare with a read of the difference** (the
marking, the package). No split form; the lens is line-only (CAPABILITIES.md:275: "A `lens` page species ... on a
dense-line page"); a ring on a dock needs a number (CAPABILITIES.md:267). Today's path: two docks (a read then a
park, CAPABILITIES.md:105) + the spotlight on the difference (E56's light) + the camera arrival (CAPABILITIES.md:102).
The build: a picture-lens (the glass over a DOCK's box, magnifying its pixels) - S-M, reuses `species/lens.mjs`'s
glass; no backlog row.

## Beat 8 - The money (AMD's China revenue share; the RFSoC's segment)

Serves it (all WIRED; the DATA is not on disk - AMD 10-K geography is research in flight):
- **Fill gauge** - CAPABILITIES.md:277 (P70 T3): "one share of one whole as a capsule that IS the whole" = "China is
  X% of AMD's revenue". Golden `gauge-94-h`.
- **Pie / donut, 3D exploded, push onto a slice** - CAPABILITIES.md:270 (P69 T48): "Use when the sentence DIVIDES a
  whole and the story is one piece's weight" - the Embedded segment (where the RFSoC sits).
- **Stacked bar of values (+ line combo)** - CAPABILITIES.md:273: `segments` 2-4, "each true to its value";
  REFUSED "a stack that does not sum to its written total" - revenue by region per year.
- **Treemap** - CAPABILITIES.md:131; **N-tier pages** - CAPABILITIES.md:130.
- **Membership stack** - CAPABILITIES.md:272 - NOT this beat ("equal tiles are MEMBERSHIP, not value").

Gap: none in mechanism; the gap is DATA.

---

## GAPS - ranked by how central the beat is to THIS story

The story's spine is mechanics: the control opens a price wedge (beat 2) between two channels (beat 4), the rule
is the wall (beat 5), diversion is arbitrage across it, or the part is not the part (beat 7). Beats 2, 4, 7 are
the argument; 1 is the hook; 5 the cause; 3, 6, 8 support.

| # | Gap | Beat | Nearest today | What a slice adds | Size | Carried by |
|---|---|---|---|---|---|---|
| 1 | **Glyphs for the supply chain's roles** (distributor / warehouse, reseller, customs / border, antenna / radar, price tag, destination) | 4 (+6, 7) | 5 Lucide SVGs (`coins cpu factory landmark ship`); node labels are free text | a sourced Lucide intake (per-file URLs + LICENSE in `assets/icons/SOURCES.md`, A2a); no engine change - `icon_file` just finds more `.svg` | S | none (no R26 row) |
| 2 | **A data-free EVENT TIMELINE page** (rule waves 2022/23/24 -> the listing -> the post, dated on one x) | 5 (+1) | agenda (undated, CAPABILITIES.md:47); `marks`/`eventbars` on a SOURCED series (ledger_page.py:142); `park_at` DRAFT (:119); decade ruler refuses non-decades (:122) | a ledger page kind whose x is dates and whose marks are events (pins + labels landing on their words), reusing `axis_tag`'s pill and `span` for "since Oct 2022" | M | none |
| 3 | **Picture compare: genuine vs listing, the difference read** | 7 | two docks read -> park (:105) + spotlight (E56 light) + camera arrival (:102); lens is line-only (:275); dock ring needs a number (:267) | a picture-lens (T32's glass over a dock's box, magnifying its pixels; no ring, so E56-clean) and/or a two-dock split preset | S-M | none |
| 4 | **The map for a transshipment route** | 4 | vecmap light / arc crossed / tokens / stamp (:129); mappoint arcs | Hong Kong / Singapore as lightable points; a tight focus fit + the ping's bloom (R26-383); a map beside a chart (R26-382) | S (points) / M (R26-382) | **R26-382, R26-383 - P72 wave-9 T46d** |
| 5 | **A social-post (X) card** - avatar, handle, post body, not a newspaper masthead | 1 | press card crops any screenshot (:125); record dock types the words (:19) | a `press` style option for the masthead strip + the card drawn at its image's aspect | S | R26-348 (card aspect, the placer) - **T46c** (last); the style itself: none |
| 6 | **The ratio bracket between two bars ("36x", D40's "10X")** | 2 | two-bar story page + figure + equation row (:123, `$ / $` = ratio, build_scene_timeline_f.py:5791) or a bracket labelled "36x" (truth-checked, :276) | only the D40 look (white bracket to TODAY's bar) - an HG1 dial | S | CAPABILITIES.md:256 Limit ("HG1"); `recipe:revalue-then-the-ratio` CANDIDATE |
| 7 | **A calendar / lead-time countdown** | 3 | range bar "40–52" (ledger_page.py:14) + `recipe:two-clocks` (CANDIDATE) | a weeks-ticking form | M | none - low value, two-clocks covers the claim |
| 8 | **Chip anatomy: die / board cutaway, labelled parts, exploded view** | 6 | bare prop + hatch (:91/:246), prop -> mark morph (:261), flow row as a block diagram; P71 T20 "schematic" is an economic curve only (:278) | an anatomy form (labelled regions on a picture) - E56-constrained | M-L | none - low value |

Standing risk across beats 1, 2, 4, 7: `effects_card.py` reports **first use: none** for `dock_kind:press`,
`species:flow`, `species:arc` / `light` / `stamp`, `species:unknown`, `species:balance`, `species:equation`,
`species:chip`, `chart_to:compare`, `dock_kind:prop`, `arrival:stamp`, `arrival:poof`, `page_builder:share` (and
`dock_option:verdict` is DRAFT). Row 125 says of the press card: "the build-loop seam ... has unit tests, not an
episode build - the first cut with a press row closes it". This episode would be the first cut for several of
them; budget a seam-closing pass. Steel and Paper H (lane A `build-h/steel-and-paper-h.timeline.json`) used 0
vecmap, 0 press, 0 unknown, 0 verdict, 0 equation, 1 flow, 1 balance.

## P72 wave-9 work that touches these beats (scratchpad p72-wave9-inflight.md)

- **T46d (page marks and looks)** - R26-382 "the chart beside the map" and R26-383 "map framing + ping glow"
  (beat 4, the map); R26-384 "the hub's fail badge" (lane-A BACKLOG-HISTORY:991: the fail disc "reads as a dot" -
  beat 4's severed licence edge); R26-395 "solo two bars" (:1002 "A SOLO LIGHTS ONE BAR; BRAVOS R30 LIGHTS TWO" -
  beat 2's two-bar compare); R26-219 span end-tag gutter (beat 3/5 spans); R26-396 end badge box; R26-375 brace's
  point.
- **T46c (docks, probe, 9:16)** - R26-348 (:955 "the compiler places every card at the default card height, the
  player draws it at the image's own aspect" - an X-post screenshot is not the default aspect: beat 1); R26-404 / 344
  (a callout ring on a parked page); R26-398 dock-at-depth badge row; R26-394 the probe reading a figure; R26-369
  agenda at 9:16 (beat 5 if a short is cut).
- **T46b (seal, prop, stroke)** - R26-361 the seal's keyline / `seal_gold` notes (beat 7's VERIFIED seal); R26-391
  (:998) "`gate_motion_density` gives no credit for a verdict landing on its word" (beat 7 if a verdict tile is
  used on a chart card); R26-106 / 365 (a) the stroke's width profile (every clothoid arrow in beat 4).
- **T46a (engine correctness)** - R26-400 (:1007) "THE STAMP'S INK DIMS THE CONTACT SHADOW MID-HANDOVER" (every
  stamped prop: beat 6); R26-341 (:948) "A `spread` PAINTS NOTHING ... UNDER `readability=longform`" (E53 s6's wedge
  as a spread, beat 2, if a price series exists); R26-390 the two-plate ground under a morph (the prop -> bar
  morph, beats 6 -> 2); R26-386 a series `dash`; R26-385 the extend's rescale painter.
- **T46e (gates, tools, captions)** - R26-357 (:964) "H'S PAGE SOURCE LINE RENDERS INSIDE YOUTUBE'S CONTROLS BAND"
  (every sourced page); R26-136 (5) search aliases (recall for this episode's nouns); R26-403 the gate's bars-extend
  credit.
- Discrepancy seen: R26-320 ("THE DRIFT-HOLD DOES NOT REACH PRESS CARDS") is `open` in lane-A
  BACKLOG-HISTORY:926, but CAPABILITIES.md:120 (P72 T19, 2026-09-26) lists R26-320 and says "a PRESS card holds with
  `idle: hold`". The history row looks stale.

## Prior research on disk to reuse (thin)

Searched: `docs/research/` on both lanes, lane-B `content/video_engine/projects/` (md/json), for `export control |
entity list | Xilinx | AMD | RFSoC | ECCN | diversion | smuggl | counterfeit | grey/gray market | chip ban | H20`.
- lane A `docs/research/markets/r26-306-nvda-share-railway-gdp-VERIFY-2026-09-24.md:33` - "In 2024 … NVIDIA ...
  92% of the market share"; AMD 4%, Huawei 2%, market $125B; GPUs only | CONFIRMED"; :37 "65% of DC AI chips,
  2023 ($17.7B; Intel 22%, AMD 11%) | TechInsights Q1 2024 update | CONFIRMED (estimate)" - AMD's scale in DC
  accelerators, context only. (This file is on lane A, not lane B.)
- lane B `content/video_engine/projects/systems-and-blowups/registration/registration.sovereign-memory-infrastructure.json:310`
  - a registered slide: "Export controls create dual supply chains across US CHIPS reshoring and China stacks." (a
  diagram slide, `memory-countercase.context.diagram-v8`) - framing only, no figures.
- Reference watch for the China/trade visual register: `content/video_engine/sources/reference_analyses/bravos-china-just-triggered-a-new-world-order/`
  (the source of the vecmap, press pile and flow species).
- NOT found in those roots: anything on RFSoC, Zynq, Xilinx, ECCN, BIS rules, diversion or counterfeit parts, AMD
  geographic revenue. Not searched: the main checkout's `docs/research/runs`, gitignored run dirs, Drive.

## Template: the last long form's episode tree (P68 Steel and Paper H, lane A)

`content/video_engine/projects/systems-and-blowups/steel-and-paper/` (lane A): `REBUILD-TREATMENT-H.md`,
`REWRITE-ORDER-H.md`, `SCRIPT-H-VO.txt` + `SCRIPT-H-{GATES,JUDGE,SCREENS,VIEWER}.md`, `SHOT-TABLE-H.md`,
`build_episode_h.py`, `evidence/` (the chart builders, CAPABILITIES.md:300 "`steel-and-paper/evidence/build_evidence_documents.py`"),
`build-h/` (`SHOT-TABLE-H.py`, `BUILD-NOTES-H.md`, `objects/` the sourced `ev-*.series.json`, `docks/`,
`evidence-dock.json`, `SOUND-PLAN.json`, `steel-and-paper-h.timeline.json`, `player.html`, `self-watch/`,
`layout-probe.json`, `GATES-MOTION.md`), frozen review copies `build-h-frozen-{d..g}/`.
What H actually used (counted in `build-h/steel-and-paper-h.timeline.json`): 15 ledger pages, 40 `build_to`,
26 `retitle`, 21 prop docks, 12 `figure`, 12 `callout`, 12 `panel_focus`, 6 `chip`, 6 `steam`, 4 `agenda`, 3
`spread`, 3 `undraw`, 1 each `flow` / `balance` / `freeze` / `lit_stretch`; `chart_to`: 7 recast, 2 compare, 2 park,
1 rescale; arrivals 15 land / 13 throw / 11 stamp; record docks and a checklist test card. BUILD-NOTES-H.md §4 "The
doors that were MISSING" and §5 "what the treatment asks for that is not on disk (E77)" are the model for this
episode's own gap / evidence ledger.
