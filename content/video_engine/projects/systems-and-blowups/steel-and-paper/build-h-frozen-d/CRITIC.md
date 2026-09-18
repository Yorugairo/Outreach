# CRITIC - Steel and Paper H, the 1:30 unit (`build-h-frozen-d`, P68 T5, FOURTH read)

Read 2026-09-18 by the `reviewer` role in a fresh context, read-only, against
`docs/content-video-engine/CRITIC-REPORT.md` (the contract) and the mechanism **list of 2026-09-16**.
INFO only: no verdict word, no FAIL row, no fix, nothing written outside this file. I read copy d on its
own frames first and opened `build-h-frozen-c/CRITIC.md` only to answer "is each of c's three closed" -
no row below is inherited, and every number is re-measured on this copy.

**What I read.** The frozen copy's compiled `SHOT-TABLE-H.py` (3 world rows) and
`steel-and-paper-h.timeline.json` (runtime **92.77 s**, 16:9, 3 scenes, 51 caption pages, 2 `page_states`
on s01, sha256 `e052906b3c014867...` - which **matches** `GATES-MOTION.md`'s footer, so the shipped gate
report describes this compile); `GATES-MOTION.md` (`1 FAIL / 3 WARN / 19 PASS / 1 JUDGE / 9 INFO`);
`layout-probe.json` (53 instants); the lane's sheets `self-watch/opening.1-4.png` (they agree with my own
frames at every instant we share); `docks/*.png` and `docks/*.src`;
`objects/ev-divergence-hook-v1.series.json` against `evidence/objects/ev-divergence-v1.series.json`; the
treatment `REBUILD-TREATMENT-H.md` rows 1-9 (there is no `BEAT-PLAN.jsonl` for this unit); and
`BUILD-NOTES-H.md` (**data, not authority** - two rows below disagree with it and say so).

**Frames I shot myself** (`probe.py <frozen build> <t...> --sheet <scratchpad>/...`, nothing written into
the build): 0.00, 1.00, 2.00, 3.00, 4.00, 4.90, 6.00, 8.00, 10.06, 13.00, 17.25, 22.00, 26.00, 26.50,
28.20, 28.60, 29.00, 29.20, 29.40, 29.50, 29.60, 29.70, 29.80, 30.00, 30.10, 30.20, 30.30, 30.40, 30.60,
30.80, 30.90, 31.40, 35.80, 44.15, 46.00, 52.50, 54.85, 66.15, 68.00, 72.00, 78.58, 82.11, 88.00, 92.60.
13.00 and 26.50 were shot at `--tile 1920` and the two cards cropped out of the frame and upscaled ~3x -
scoring a dock by its PLACEMENT box was my predecessor's named error and I did not repeat it.

**The receipt.** `recall_verify.py .../build_episode_h.py` -> `PASS - 12 citation(s) verified across 9
stages` (`## Recall` at line 39, sha256 `4f5aa4ee7975` - a different block from copy c's `6fda23481364`;
the stage counts are unchanged, 1 per stage plus 4 rulings). Every span I checked is real and on the line
it names. Table 2 is judged on those twelve spans only. **The module's named-constant block above the
receipt is stale against this cut on five of its twelve constants now** - `OPEN_PAGE/OPEN_ENTER` still
says the open runs on `ev-bravos-original-v1`; `LAYER_RECAST` still describes the `;then=` recast;
`HOST_PLATE` still says the Bravos card is thrown onto the desk; `GDP_RECAST` still describes a recast to
`ev-equip-ipp-gdp-v1` that the table has not carried since copy b - and copy d's own new spine (the
DERIVED hook object and the two per-state Y domains) has no constant at all, so the departure this copy
exists for is the one the block does not record. `recall_verify` never reads that block; it is the
document-level hazard score 2 exists to catch (arXiv 2606.04990).

---

## The predecessor's three rows (`build-h-frozen-c/CRITIC.md`)

| its row | state | read from |
|---|---|---|
| 1. the 0:24 card was the finished four-line chart, spoiling the +613 payoff | **closed** | the row now compiles `dock-h-two-line-copy` (`SHOT-TABLE-H.py`, 24.16-28.05, `arrive: land`). Cropped off my own 26.50 frame and upscaled 3x, the card's face is a two-line page titled *"Two lines, one warning"*: the teal `+105% SEMICONDUCTOR STOCKS` and the two market lines `+21% S&P 500` / `+21% MEGA-CAP TECH`. **No memory line, no `MEMORY MAKERS (hynix+Micron)` legend, no `+613%`.** I verified the derivation number by number: `objects/ev-divergence-hook-v1.series.json` series 0/1/2 `pts` are **byte-identical** to `evidence/objects/ev-divergence-v1.series.json` series 1/2/3, the crimson +613 series and its badge are dropped, and no figure is typed. The card's three end tags are the same three the LIVE page has carried since 17.25, so it gives away nothing the frame has not already shown |
| 2. the reveal double-drew a second axis under the parked page | **half closed - the park is fixed, the double-draw moved** | The park half is closed: `chart_to park 1.0` at 28.35 releases first, and the chart box walks 698 (28.20) -> 792 (28.60) -> **1083 (29.00, `parked: False`)** and then only forward, 1084 / 1086 / 1090 / 1094 / 1096 through 31.40. There is no 693 -> 1086 -> 700 snap and no second rail sitting APART from the first. **The tick-on-tick is not closed - it moved off the gate's instants.** At **30.00** the page draws **16 labels** where 29.40 draws 10, and the probe's own `overlaps` reads four pairs at **100 % of the smaller**: `tick:index · 100 =` 9,558 px, `tick:Jan '26` 2,407 px, `tick:Apr '26` 2,407 px, `tick:Oct '25` 2,378 px - each word on an exact copy of itself. That is the same R26-222 mechanism as the shipped M28 FAIL at 0:05 (5 pairs, `layout-probe` 5.18). The gate probes 29.25 and 30.25 and reads `overlaps: none` at both, so its report never names the reveal's instance. **I disagree with `BUILD-NOTES` 2d heading *"The reveal no longer double-draws"***: its own table prints 16 labels at 29.8 and 30.0 and its body says *"the engine writes the arriving axis before the standing one leaves"* - the heading overstates the body |
| 3. the hook's y axis printed one tick for 24 s | **closed** | the domain is `ymin 80 / ymax 277` and **two ticks print** - `80` and `160` at every instant I probed from 5.18 to 29.25 (6.00, 8.00, 10.06, 13.00, 17.25, 22.00, 26.00, 28.20, 29.20, 29.40) - and nothing clips: the mega-cap line's own low is 93.94, above the floor, and the drawn ink sits inside the plot at every one of them. The scale also works harder than copy c's: `data` h / `plot` h reads **21 %** (4.90), **24 %** (6.00), **34 %** (13.00), **81 %** (17.25). `BUILD-NOTES` 2d's measurement table (24 % / 33 % / 50 % / 81 %) matches my frames at the rows I re-measured - unlike copy c's, which did not |

---

## Table 1 - MECHANISM CORRECTNESS (list of 2026-09-16)

| mechanism | owed by | verdict | t | read from |
|---|---|---|---|---|
| 1 the open STARTS ON THE CHART - the ledger page is the first frame, on its axes, its line drawing under the hook | treatment row 1, P01 *"The AI bubble is real."* | present | 0.00, 1.00 | probe 0.00: `page: title [58,39,763,64], plot [217,299,776,470]`, 8 labels (three y ticks, four x ticks, the y label), `marks n 0`, no caption, the title mid-stroke; first ink at 1.00 (`data [221,701,73,33]`, `drawn 0.04`). Nothing precedes the page |
| 2 every page BUILDS with the effects and HOLDS BUILT while its number is spoken; `enter=built` is not an answer | rows 1, 2, 4, 9 | present | 3.00, 17.25, 31.40, 82.11 | probe 1.00 (`drawn 0.04`) -> 3.00 (`0.25`) -> 13.00 (`0.5`) -> 17.25 (`drawn 1`); the memory line 29.70 (`n 4, drawn 0.77`) -> 31.40 (`1.0`); the railway page 68.00 (`0.07`) -> 82.11 (`1`). No `enter=built` anywhere. The ORDER is still the note, not the build: all three hook end tags land together at **17.25** and their words are at 33.24 and 35.77, 16-18 s later |
| 3 a page whose number lands 7 s or more MOUNTS over the world (`mount=`) and builds under the setup sentence | row 9 - the railway page enters 66.15, its numbers land 78.58 and 82.11, 12.4 s and 16.0 s later | replaced by `:axes` on the dip, building under the setup | 66.15-78.58 | no `mount=` token anywhere in the table. probe 66.15 `marks n 0` on bare axes; 68.00 `data 76 x 43 px` inside `plot 776 x 470` (**0.9 % of the plot's area** - a stub in the corner), 72.00 `98 x 61`, 78.58 `300 x 342`. The build-under-the-setup half is carried; the mount over the studio plate is the route the cut did not take, and the page's first ~6 s are all but empty |
| 4 the axes entry elsewhere (`:axes`) - a page enters by its own signature, never zoomed up from a card | rows 1, 9 | present | 0.00, 66.15 | `page.enter: axes` on both ledger scenes; probe 66.15 - the title, the `1843 level` rule, seven year ticks and three y ticks up, `plot` empty, no card on stage before it (54.90-66.15 is the plate) |
| 5 the dip only on a WORLD change; never a dock's transition, never into a mount | rows 7, 8 (page -> studio plate; studio plate -> page) | present | 54.90, 66.15 | the two scene exits are `dip` and nothing else is; probe 54.85 is still the page (`scene s01`) and 66.15 is `scene s03` with the page not yet inked. Neither card arrival takes a dip - the page is continuous across both (probe 10.06, 26.00) |
| 6 page to page by `suck` or `cut` with no empty cream between (a chart-to-chart transform) | row 4 (*"`chart_to` the page to `ev-divergence-v1`"*) and row 9 (*"`chart_to` `ev-equip-ipp-gdp-v1`"*) | replaced by `chart_to rescale` - a Y-domain state change on ONE object; the unit holds no second page | 4.28-5.18, 29.25-30.25 | the transform is real and the stage never empties: probe 28.20 -> 31.40 reads a page at every instant, `marks` 3 -> 4, the domain opening `[80,277]` -> `[95,1139]`, and `GATES-MOTION` M23 counts 5 transitions "each on a built chart". What is absent is the page-to-page hand-over both owed rows name: 2 ledger objects, each alone in its own scene behind a dip, no `;then=`, no second page in the tail |
| 7 the return by the SPIRAL, the page unwound, the ring on the chart (its one use) | row 9, *"AI spending just crossed eight"* (the treatment: *"a **ring** lands on the 8 % datum"*); no page returns inside rows 1-9, so the spiral is not owed | absent | 88.00-92.77 | probe 88.00 and 92.60: the page's only labels are `sname:1843 level`, `sname:741 RAILWAY SH`, three y ticks and seven year ticks - no ring, no marker, no figure in scene 3. The object's own declared marks (`2,062 - 6 Oct 1845`, `741 - Apr 1850`) never print either, so the peak the −64 % is measured from is a bend in the line and nowhere a number. The 8 % object is not on disk (`BUILD-NOTES` s5 #1) |
| 8 a DOCK is an evidence still or document that READS then parks in the page's own room - never a chart page thrown as a card | rows 2, 3 | replaced by an ornament that does not read (row 2) and by a rendered page-card (row 3) | 13.00, 26.50 | **The placement is textbook and stays on the record**: probe 10.06 `dock-h-certificate-1845 parked [1354,648,326,308]`, `caption_px 73`, `overlaps: none`; 26.00 `dock-h-two-line-copy parked [1354,704,327,205]`, `caption_px 200`, `overlaps: none`, and the page keeps building under both. **Row 2's face is unchanged from copy c**: cropped off my 13.00 frame and upscaled, it is a **blank ornate certificate** - deckle, rose border, an EMPTY cartouche, no name, no date, no "1845", no share count - with a neighbouring certificate's corner and a sliver of the blue shaft intruding at two edges, under *"This certificate is what the last bubble was: paper sold as safety"*. I read the blankness against the mechanism's own "READS" clause. **Row 3's face is much better and still the rule's named refusal**: the spoiler is gone, but the card is a chart PAGE rendered as a card, and it is rendered in our page's own clothes - the same cream mat, the same handwritten title face, the same `Yahoo Finance - pairing after Bravos Research` source line, the same single `160` y tick - so it reads as our page shrunk, not as the guy's copy of somebody else's chart. `docks/dock-h-bravos-original.png` + `.src` (the actual Bravos still, the object treatment row 3 names) is in the build dir with no row compiling it |
| 9 a plate carries its card for six seconds with directional life | row 7, the host window 54.90-66.15 (11.25 s) | replaced by a plate with no dock (an NVIDIA chip and a `CAPITAL -> VALUE` flow carry the window) | 55.40-65.90 | `docks: []` on scene 2 in the table and `docks: no docks` at every instant in it. The life is real - `ken_burns (0.05,-12,6)` + `idle_drift_px 20`, and the frame tracks between 56.00 and 66.00 on sheet `opening.3`. The plate ART carries a printed line chart lying on the desk, so *"And it isn't Bravos Research, whose chart this is"* does not play over an empty desk - it plays over a chart the cut cannot point at, cite or move, because it is paint. The card row 7 owes is still absent |
| 10 a light is PUNCTUATION on a sentence that points, placed after the page's build | `not owed` | not owed | - | treatment rows 1-9 hold no shape that calls for a light: the pointing they name is a callout (rows 3, 5), a `figure` (row 4), a ring (row 9) and the numbered agenda (row 6). No spotlight is in the timeline; E99 s76 refuses a light with nothing specific to point at |
| 11 old and new BLEND - a new mechanism sits inside the approved shape | rows 3, 6, 7 (and the `spread`) | present | 26.50, 46.00, 63.50 | three of them, all inside the approved shape. **The newest is copy d's own**: a card rendered at build time from a DERIVED series object (`chart_card.render_card` on `objects/ev-divergence-hook-v1.series.json`) sits inside the dock/slot shape E99 s80 already defines and changes nothing about the slot (26.50, and the two-file comparison above). probe/frame 46.00: the page parked to `chart [145,171,565,406]` with the agenda `1 Scarce? / 2 Cash or paper? / 3 Used tomorrow?` typing into the room the park freed; 63.50: the `CAPITAL -> VALUE` flow in the plate's dark upper-left. One caveat for the parent, unchanged from copy c: the `spread`'s coral fill is declared `dur 2.0` (33.02-35.02) and is still on the page at 54.85 - **19.8 s** - through the park to 0.52 and under the agenda, where at 5.4 css it reads as a red mass rather than a measured gap (sheet `opening.3`, tiles 48.00-54.00) |

Owed in this cut: **10** (mechanism 10 is `not owed`). Present: 1, 2, 4, 5, 11. Replaced: 3, 6, 8, 9. Absent: 7.

**The fraction did not move from copy c's 5/10, and the reason is worth a line so the parent does not read
it as "nothing happened".** Both of this copy's changes landed INSIDE mechanisms that were already scored:
the card fix improved mechanism 8's face without changing its verdict, because the rule's named refusal is
a chart page as a card and the card is still a rendered chart page; the rescale fix sits inside mechanism 6,
which was already `replaced`, and inside mechanism 2, which was already `present`. Nothing regressed. The
contract refuses a third number precisely so this does not read as a flat pass.

---

## Table 2 - ATTRIBUTION QUALITY

The rule I applied, stated so it can be discounted: a row is attributed when **every principal authored
token** has a receipt span whose quoted words state the rule that token obeys; otherwise `UNATTRIBUTED`,
and the uncovered choice is named. Three compiled rows carry nine treatment beats, so the denominator is
coarse - each note says which tokens ARE covered. No `overrides.json` is in the build, so there is no
override row.

| row | what it does | attribution | note |
|---|---|---|---|
| 1 - 0.00-54.90 | `ledger:ev-divergence-v1:line:234:right:axes:cut;idle=live`; docks `dock-h-certificate-1845` (throw/paper 9.60-17.31) and **`dock-h-two-line-copy` (land/paper 24.16-28.05, rendered from the derived object)** in slot 0; 17 `build_to` (series 0 pinned to datum 0 at 0.00, released to 234 at 29.25; series 1-3 staged 0.0 / 9.6 / 12.21 / 13.97 / 15.45); **`chart_to rescale` `[80,277]` at 4.28 and `[95,1139]` at 29.25**; `chart_to park` 0.64 at 9.60, **1.0 at 28.35**, 0.52 at 43.25; `spread` 2->0 at 33.02; 3 x `retitle`; `figure +613%` at 37.64; `agenda` 3 rows; `note`; camera keys 1.0 / 1.06 / 1.0; exit `dip` | `UNATTRIBUTED:` **the derived hook object and the card rendered from it** - the mechanism this whole copy turns on. No receipt span states a rule about deriving an object, rendering a card from a series, or withholding a payoff; the nearest line, `OPERATOR-RULINGS.md:3278` *"A second card takes the outgoing card's slot"*, states the SLOT rule and the slot is unchanged. Also uncovered: **the two per-state Y domains** and the `rescale` itself (no span about a chart's scale, a domain, E58/E61/E64); the 0.9 s park release (`UNPARK_LEAD_S`); the three `chart_to park` (E61); the `land` arrive that replaced the throw (E99 s71 - in the module's prose, not in the receipt); the staged `build_to` ladder; the `spread`; the `figure`; the camera at 1.06 (E99 s76 - cited only inside `CAMERA_613`, which `recall_verify` does not read). Covered: `:2342` *"The hook opens on its axes"* for `:axes`; `:1494` *"Nothing ever goes truly still"* for `;idle=live`; `:3278` for the two docks in slot 0; `CAPABILITIES.md:43` *"THE NUMBERED AGENDA"* for the agenda | One integrity note on the derivation, since table 2 is where it belongs: every **number** in `ev-divergence-hook-v1.series.json` is byte-identical to the verified object (I compared the three shared series' `pts` lists) and no figure is typed, which is the claim `BUILD-NOTES` 2d makes and it holds. Two text fields are NOT copies: `title` and `sub` are new authored strings (`HOOK_CARD_TITLE` / `HOOK_CARD_SUB`), and `ylabel` is normalised to `index · 100 = ...` where the verified object holds the double-encoded `index Â· 100 = ...`. Both render the same on the frame; I name it because "the verified object with the staged series dropped" is not quite what the file is. Separately: the card has **no `.src` sidecar** where both orphan cards (`dock-h-bravos-original`, `dock-h-divergence-copy`) do, so from the build dir alone the one card a viewer reads at 0:24 cannot be traced to anything - its provenance lives only in the module and the derived JSON |
| 2 - 54.90-66.15 | `world-h1-studio-v1;use=landing;idle=drift;drift=20` + ken `(0.05,-12,6)`; `chip` NVIDIA 60.58 (crossed 61.78); `flow` CAPITAL -> VALUE 62.16; no dock; exit `dip` | `UNATTRIBUTED:` `;use=landing` (E61's three plate uses - in the treatment, not in this module's receipt) and the row's only two authored events, the `chip` and the `flow` (`CAPABILITIES:99`, cited in the module's prose and in no Recall line). Covered: `OPERATOR-RULINGS.md:3248` *"A plate's life is DIRECTIONAL"* for the ken push and the 20 px drift, which I read moving across sheet `opening.3` | Unchanged from copy c. The caption is in STAGE mode across the dark left and reads cleanly on the plate; the chip badge is small, dark and low on the desk line; the flow diagram is the one thing in this window with a shape and it is well placed in the plate's dark upper-left |
| 3 - 66.15-92.77 | `ledger:ev-railway-index-v1:line:139:right:axes:cut;idle=live`; `build_to` 66.15 / 71.28 / 74.30 / 76.38 / 80.51; `note` 74.30 and 81.31; exit `dip` | Attributed. `Recall(evidence) evidence/EVIDENCE-DOSSIER.md:120` *"seven percent of GDP in two thousand"* is a claim-level span for the choice that shapes the whole row - the refusal to put `ev-equip-ipp-gdp-v1` (11.54 % of GDP) under the words "seven" and "eight"; `OPERATOR-RULINGS.md:2342` for `:axes`; `:1494` for `;idle=live`. Two fine points I am not deducting for but will name again: the `:2342` span states the rule for the HOOK's axes and this row is a mid-cut entry, and the word-anchored `build_to` ladder rests on the module's own parenthetical rather than on the quoted span of `Recall(script)` (which quotes `SCRIPT-H-VO.txt:1` only) | Every figure the page prints is the object's own and the treatment's −66 is correctly refused for −64. The uncovered figure is the first `note`'s conversion, *"Railways, 1845: £250m raised - over $1T in today's money"*: the page cites nothing for it and the receipt has no span stating the rule it obeys. Both notes are still drawn at 92.60 (`note [1298,195,611,138]`, declared `dur` 3.0 and 2.4), and the second scene's 51.27 note (`dur 2.4`) is still drawn at 54.85 - notes do not retract in this engine |

---

## The three rows the operator should look at first

1. **0:01.5-0:25.9 - the card no longer gives the reveal away; the page's own WORDS still do.**
   This copy moved the payoff out of the picture at 0:24 and it worked (predecessor row 1, closed above).
   What is still on screen for the 24 s before it is the page's own title and sub-title, which name the
   thing in plain English: the title reads **"The sharpest chart on YouTube - plus the layer it needed"**
   in full from 1.00 (`title [66,43,1006,63]`) to the retitle at 25.91 (probe 1.00-25.36; sheet
   `opening.1` tiles 2.00 through 22.00), and the sub under it reads **"Their pairing, plus the S&P 500
   and the memory builders. 100 = Aug '25, log scale"** at every instant from 1.00 (`sub [147,113,860,31]`,
   10.7 css; legible at full res on my 30.00 crop). The caption that pays it off - *"Here's the layer it
   never drew"* - is at 29.25, and the memory line is deliberately pinned at datum 0 until then. So the
   frame announces "the layer" in words 28 s before it draws it, and then announces it again as news.
   `BUILD-NOTES` 2d names this in one parenthesis - *"the page's own SUB still reads ... it is the
   object's text and the object is read-only"* - which is true of the object and not of the cut: the
   row already carries three `retitle` strokes (25.91, 35.67, 40.20), and `_hook_object()` is now the
   proven door for a page's text that is not the verified object's own. This is the last leak of the
   thing the whole copy was built to withhold, and it is the one an operator can hear in one watch.

2. **0:29.5-0:30.3 - the reveal's tick-on-tick survived the fix and moved off the gate's instants, and
   one orange dot is loose in the plot.** The park half of the predecessor's row 2 is genuinely closed:
   the page unparks first (28.35 + 0.7 s), the chart box only grows (698 -> 792 -> 1083 -> 1096 across
   28.20-31.40) and the displaced second rail is gone. The double-draw is not. At **30.00** the page
   draws **16 labels** against 10 at 29.40, and the probe's `overlaps` reads four pairs at **100 % of
   the smaller** - `index · 100 =` (9,558 px), `Oct '25`, `Jan '26`, `Apr '26`, each word sitting on an
   exact copy of itself. It is the same engine door as the M28 FAIL the report DOES carry at 0:05
   (5 pairs, `layout-probe` 5.18, R26-222) and the gate cannot see this one: its probe list holds 29.25
   and 30.25 and reads `overlaps: none` at both, so 30.00 falls in the gap. Superimposed duplicates are
   invisible, so this is a record row, not a picture row - **but there is a picture row inside the same
   window.** From 29.50 to about 30.20 a single orange dot floats **detached** in the plot, roughly 120 px
   above the memory line's own head and at a value the data does not have at that x (frames 29.70, 30.00,
   30.10, 30.20; gone by 30.30; clearest on my full-res 30.00 crop, where the line's head sits just under
   the 320 rule and the stray dot sits between 320 and 640). It reads as the line's end marker drawn
   against the outgoing domain while the polyline is already on the incoming one. It lands on the unit's
   single most important instant - the words *"Here's the layer it never drew"*.

3. **0:09.6-0:17.3 - the one piece of real evidence in the unit is a blank certificate, and three critic
   passes have now said so.** `dock-h-certificate-1845` is placed as well as anything in this cut
   (`parked [1354,648,326,308]`, `caption_px 73`, `overlaps: none`, the page's line building under it,
   the throw cued at 10.02 s with M29 licensing the cue) - and the face, cropped out of my own 13.00 frame
   and upscaled 3x, is an **empty ornate cartouche**: deckle and rose border, no name, no date, no "1845",
   no company, no share count, plus the corner of a neighbouring certificate and a sliver of the blue
   shaft intruding at two edges of the crop. It holds the frame for 7.7 s of the opening minute under
   *"This certificate is what the last bubble was: paper sold as safety"* and *"is still carrying trains"*.
   Nothing in the table changed here between copies b, c and d. The mechanism's own words are "an evidence
   still or document that **READS**"; this one has nothing to read, so the sentence's proof is an
   ornament. `CERT_CROP = (248, 226, 566, 442)` is a pixel window on
   `world-certificate-wall-v1.png` - it is a crop choice, and the plate has other certificates in it.

**Also on the watch, not scored here:** the tail is unchanged - the 1840s page is complete and its `data`
box is **identical at 82.11, 88.00 and 92.60** (`[219,327,776,418]`, `drawn 1`) under *"seven percent of
GDP"*, *"then the tower came down"* and *"AI spending just crossed eight"*, and the last authored visual
event ends at **83.71**, leaving **9.06 s** of captions over a still page; the railway page's first 6 s
are 99 % empty (`data 76 x 43` in `plot 776 x 470` at 68.00); the page never un-parks on purpose (M25's
own INFO line prints `chart.lab parked 5.4`, `chart.sname parked 5.9`) while the agenda, the four end tags
and the coral spread are all read at that size; the spread and all three `note`s never retract (19.8 s,
18.5 s and 11.3 s past their declared `dur`); the railway page's two declared marks (`2,062`, `741`) never
print; the M28 FAIL block quoted in `BUILD-NOTES` s1 says *"51 instants probed"* where the shipped
`GATES-MOTION.md` says 53, so that quoted block is from an earlier compile; and
`docks/dock-h-bravos-original.*` and `docks/dock-h-divergence-copy.*` are both still in the build dir with
no row compiling them.

mechanisms present 5/10 (list of 2026-09-16)
rows attributed 1/3
