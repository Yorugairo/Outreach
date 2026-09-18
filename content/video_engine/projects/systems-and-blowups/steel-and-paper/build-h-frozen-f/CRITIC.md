# CARRIED FROM COPY e - the director-critic's ONE read of the bed (E99 s82 (c)); copy f carries its first two rows fixed (the melt in the cut; the certificate's face); its third is R26-233. Read on copy e 2026-09-18.

# CRITIC - Steel and Paper H, the 30-SECOND BED (`build-h-frozen-e`, P68 T5, ONE read)

Read 2026-09-18 by the `reviewer` role in a fresh context, read-only, against
`docs/content-video-engine/CRITIC-REPORT.md` (the contract), the mechanism **list of 2026-09-16**, and
the bed's own plan (`REBUILD-TREATMENT-H.md` rows 1-6 and its **Amended** foot; `OPERATOR-RULINGS.md`
E99 s82 and its four amendments). INFO only: no verdict word, no FAIL row, no fix, nothing written
outside this file, nothing rebuilt, re-rendered or re-served. This is a DIFFERENT build from
`build-h-frozen-d` (53 s / 2 rows against 92.77 s / 3 rows); no row below is carried over from
`build-h-frozen-d/CRITIC.md`, and every number here is measured on this copy.

**What I read.** The compiled `SHOT-TABLE-H.py` (2 world rows) and `steel-and-paper-h.timeline.json`
(runtime **52.85 s**, 16:9, 2 scenes, sha256 `b92fead6753f150c…` - which **matches** `GATES-MOTION.md`'s
footer, so the shipped gate report describes this compile); `GATES-MOTION.md`
(`4 FAIL / 4 WARN / 15 PASS / 1 JUDGE / 9 INFO`); `BUILD-NOTES-H.md` §8 and §8b (**data, not
authority** - five rows below disagree with it and say so); `self-watch/bed.png` (8 tiles, read as an
image; it agrees with my own frames at 12.00 and 46.00, the two instants we share); `docks/`; the
treatment; E99 s82; and the engine shipped in the build, `scene-evidence-engine.mjs`.

**Frames I shot myself** (`probe.py <this frozen build> <t…> --sheet <scratchpad>/…`, nothing written
into the build): 0.00, 1.20, 2.40, 3.60, 4.80, 9.30, 9.40, 9.50, 9.60, 9.80, 10.20, 12.00, 16.50, 20.00,
22.00, 28.00, 28.70, 29.25, 31.00, 34.60, 36.60, 37.60, 42.10, 42.50, 42.90, 43.00, 43.05, 43.10, 43.15,
43.20, 43.30, 43.60, 44.00, 46.00. 12.00 was shot at `--tile 1920` and the card cropped out of the frame
and upscaled 3x - scoring a dock by its PLACEMENT box is the named predecessor error and I did not
repeat it.

**The receipt.** `recall_verify.py .../build_episode_h.py` -> `PASS - 12 citation(s) verified across 9
stages` (`## Recall` at line 39, sha256 `392fd17507bb`). Every span is real and on the line it names, so
table 2 is judged on those twelve spans only. Two observations that belong to score 2: (i) the receipt
carries **no line for any of the four doors this bed exists to prove** - `;domain=` (R26-223),
`;build=lines:` (R26-226), the full-stage / anchored caption (R26-205), `plate_idle_paints`
(R26-228) - and none for E99 s82 at all; (ii) `Recall(rulings) OPERATOR-RULINGS.md:3278` ("A second card
takes the outgoing card's slot… the certificate card hands its slot to the Bravos chart card") cites a
hand-over **E99 s82 struck and this table no longer has** - the Bravos card is gone, the slot stays
empty. `Recall(motion) CAPABILITIES.md:44`'s parenthesis ("in the room the park frees") is stale the same
way: there is no park.

---

## Table 1 - MECHANISM CORRECTNESS

### (a) the list of 2026-09-16

| mechanism | owed by | verdict | t | read from |
|---|---|---|---|---|
| 1 the open STARTS ON THE CHART - the page is the first frame, on its axes, its line drawing under the hook | treatment row 1 (*"The AI bubble is real. Just not in the steel."*) | present | 0.00 | probe 0.00: `page: title [62,40,763,64], plot [142,249,956,579]`, 7 labels (ticks `80`, `160`, the y label, four year ticks), `marks n 0`, no `data` box, no caption yet. Nothing precedes the page; first ink by 0.60 (`drawn 0.49`) |
| 2 every page BUILDS with the effects and HOLDS BUILT while its number is spoken; `enter=built` is not an answer | treatment rows 1 + 4 | present | 1.20, 2.40, 3.60, 31.00 | probe `marks`: `n 1 drawn 1` @1.20, `n 2 drawn 1` @2.40, `n 3 drawn 1` @3.60, the memory line `n 4 drawn 0.77` @28.70 -> `0.86` @29.25 -> `1` @31.00. No `enter=built`. Note: `build_s` is 4.8 but all three drawing lines are whole at 3.60 - 1.2 s of the declared build has nothing left to draw |
| 3 a page whose number lands 7 s or more MOUNTS over the world (`mount=`) | `not owed` | - | - | the bed holds ONE page and it is the first frame (E73, treatment row 1); no page enters over a standing world, so no row's number can land 7 s into a mount. The only number that lands late (`figure +613%` @36.39) lands on the page that has been on stage since 0.00 |
| 4 the axes entry elsewhere (`:axes`) - a page enters by its own signature, never zoomed up from a card | row 1's token `…:axes:cut` | present | 0.00 | `world.page.enter: "axes"` in the timeline; probe 0.00 shows the ticks and the y label up with `marks n 0` and nothing else on stage |
| 5 the dip only on a WORLD change; never a dock's transition, never into a mount | the 43.04 boundary (ledger -> plate) | present | 43.05 | the world does change and the compiled transition IS a dip (`s02.exit: "dip"`), mean luma **5.14, max 11** at 43.05 (near-black, M32's own threshold is < 8). **But it is the compiler's default, not an authored choice**: row 2's exit field is empty in `SHOT-TABLE-H.py` and the shape the operator named for this beat is the melt-toss - see (b) row B6. The card's arrival at 9.2 takes no dip (the page is continuous, probe 9.30-10.20) |
| 6 page to page by `suck` or `cut` with no empty cream between | `not owed` | - | - | one ledger object for the whole bed (`ev-divergence-v1`); the only page-to-page move a 2-row bed could hold does not exist. The `chart_to rescale` at 28.23 is a state change on the same page, scored in (b) |
| 7 the return by the SPIRAL, the page unwound, the ring on the chart | `not owed` | - | - | nothing returns inside rows 1-6 and no ring is authored; the +613 datum is pointed at by a camera key and a `figure`, not a ring (E56 is not called on by any sentence in the bed) |
| 8 a DOCK is an evidence still that READS then PARKS in the page's own room - never a chart page thrown as a card | treatment row 2 (the 1845 certificate) | present | 9.80, 12.00 | `docks: dock-h-certificate-1845 parked [1421,687,230,220]`, `place_room: corner`, `overlaps: none` from 9.80 on; and it is NOT a copy of the chart (E99 s82 (2) holds - `docks/dock-h-divergence-copy.png` and `dock-h-two-line-copy.png` are on disk but neither is compiled). **Two defects on the same row, both on the frame:** (i) the card's FACE is a BLANK ornate certificate - an empty cartouche, no "1845", no railway name, no number, plus a neighbour certificate's corner inside the crop (12.00 at `--tile 1920`, cropped and upscaled 3x) while the caption says *"This certificate is what the last bubble was"*; (ii) in FLIGHT it crosses the page's own end tags - `over chart.sname 4050 px (15 %)` @9.30, `7730 px (28 %)` @9.40, `11019 px (40 %)` + `3669 px (18 %)` @9.50, `10283 px (37 %)` + `7001 px (35 %)` @9.60. `GATES-MOTION` M27 reads PASS over its 17 instants, which straddle the throw; I disagree with that row at those four instants. Parked, it clears the caption strip by **11-12 px** and sits **19-20 % inside the bottom safe band** (M25's two WARNs) |
| 9 a plate carries its card for six seconds with directional life, never a bare still | row 2 (`world-three-notch-slate-v1`, 43.04-52.85 = 9.81 s) | present | 44.00, 46.00 | M44's floor is met (9.81 s) and the life is real and measured: registering 44.00 against 46.00 (full-res tiles, best-alignment search) the plate moves **dx +3 / dy +21 px in 2 s** - R26-228's "visible on two tiles 2 s apart" is satisfied by a number, not a feeling. Note: the plate carries NO card - `use=landing` with nothing landing on it, and the operator's *"add stamps for visuals"* (s82 (h)) is not drawn. §8b names the engine reason (the `stamp` species is admitted for the vector map's three species alone, `build_scene_timeline_f.py:671`); I confirm no stamp on any frame 43.20-46.00 |
| 10 a light is PUNCTUATION on a sentence that points, after the page's build | `not owed` | - | - | no `spotlight`/light species is authored in either row; the pointing in this bed is the camera key on the named datum (36.19-39.99, `look` datum 234) and the `figure +613%`. Nothing is lit for M16's sake |
| 11 old and new BLEND - a new mechanism sits inside the approved shape | rows 1-6 (the four doors) | present | 0.00-43.00 | the four engine doors ride INSIDE the approved ledger row (one `ledger:…:axes` token, the same species vocabulary); nothing replaced the shape. What the doors did to the gate is the honest caveat - see the note under the fractions |

### (b) the bed's own plan (E99 s82 and its amendments; the treatment's **Amended** foot)

| mechanism | owed by | verdict | t | read from |
|---|---|---|---|---|
| B1 the page is BORN on its domain; INK NEVER MOVES UNLESS THE SENTENCE MOVES IT; **no rescale inside a page's build** (R26-223 / s82 amended) | rows 1 + 4 | **absent** | 28.00 -> 29.25 | the birth half is clean (`;domain=80,277`; ticks `80`/`160` from 0.00, no 0:04 rescale - copy d's defect is closed). The rule's second half is not: `chart_to rescale` (28.23 +1.0 s) runs **simultaneously with** `build_to series 0` (28.23 **+2.2 s**), and the ink that is already landed slides down under it - `page.data` top edge **288 px @28.00 -> 432 @28.70 -> 503 @29.25** (a 215 px drop) with its height 463 -> 354 -> 322. The y scale loses its own baseline at the same instant: ticks `80, 160` @28.00 become `160, 320, 640` @29.25 - the `100 = Aug '25` the sub and the y label both name no longer prints. The caption does name a new line at 28.70 (*"Here's the layer it never drew."*), so the operator judges whether that sentence moves this much ink; what is not arguable is that the move happens INSIDE the new line's own build. Compare 24.00 and 30.00 on the lane's own `bed.png` |
| B2 LINE BY LINE - each series draws whole, its label and badge land, the next starts (R26-226) | rows 1 + 4 | present | 1.20, 2.40, 3.60 | `marks n 1 drawn 1` + `sname:+105% SEMICOND…` @1.20; `n 2` + `sname:+21% MEGA-CAP` @2.40; `n 3` + `sname:+21% S&P 500 (` @3.60. No stop inside a line anywhere in 0.00-4.80. Two notes: the drawn ORDER is semis -> mega-cap -> S&P where the Amended row names mega-cap -> S&P -> semis; and the mega-cap and S&P tags both print `+21%`, stacked 18 px apart (frame 12.00) - true to the data and the beat's point, but the two lines' identity is carried only by the tag text |
| B3 THE PAGE IS THE PLATE - full stage on 16:9, the caption in the anchored bottom strip, no column reserved (R26-205) | every page row | present | 1.20, 12.00 | `full_stage: true`, `caption: "anchor"` in the compiled page; the caption box is `[141,919,1638,41]` in the anchored strip at every instant and the page never parks for it. **The geometry the operator should judge**: `chart [48,192,1350,756]` = 70 % x 70 % of the stage, `plot [142,246,958,580]` = **49.9 % of the stage width**; the right ~500 px is the end-tag gutter (the tag text does run out to ~x 1880) and the card parks inside it. This is much more than copy d's 0.64 park, and it is not yet edge to edge |
| B4 A PAGE PARKS ONLY FOR SOMETHING THAT NEEDS ITS ROOM - never for the caption, never for a card that fits (s82 amended) | every page row | present | 0.00-43.00 | `marks.parked: False` at all 24 page instants I probed, including the whole card window (9.30, 9.50, 9.80, 12.00, 16.50). The card takes the corner at full page size and overlaps no ink when parked |
| B5 a docked card never carries the chart that IS the world (s82 (2)) | treatment row 3, amended | present | 9.80-16.64 | one dock in the bed, a certificate - a different object. The two chart-copy PNGs are on disk, uncompiled |
| B6 **the melt-toss for the agenda** - the chart melts to a ball and is tossed off, the list centres (s82 (g), the operator's own shape) | row 6 / the 43.04 beat | **absent** | 42.90 -> 43.20 | the token is written as **`exit: "melt:throw:1"` on the PAGE row (s01)**. The engine reads `exit` as the transition INTO the row it sits on - its own comment: *"`exit` names the transition INTO the scene it sits on (E47), so `s05.exit = \"melt\"` melts s04's"* (`scene-evidence-engine.mjs:2859`), and the code gates it on a predecessor: `const meltOn = prev && exitName(sc.exit) === "melt" && prev.world && prev.world.kind === "ledger" …` (`:15612`). **s01 has no `prev`, so nothing melts.** Row 2's exit field is empty, so the compiler's default `dip` is what plays. On the frames: the page is whole and unshrunk at 42.90 (`chart [50,194,1348,755]`, `marks n 4 drawn 1`), the stage is **near-black at 43.05** (mean luma 5.14, max 11; `page: no page`, `marks up 0.0`), the slate fades up 43.10 (luma 30.6) -> 43.15 (56.0) -> 43.20 (82.0). No ball, no throw, on any frame at any step of 0.05 s. **I disagree with `BUILD-NOTES` §8b** (*"the whole chart MELTS TO A BALL and is thrown off (`exit: "melt:throw:1.0"` on the page row - a melt takes the world, so it is the row's exit)"*): the premise is inverted against the engine in this build dir, and the 0:43 instant is not on the lane's own `bed.png` (its tiles are 2/6/12/18/24/30/38/46). Consequence for the beat: agenda row 1 fires at 43.04, inside the dark core - no row is on the frame at 43.05/43.10/43.15, the first `1` appears at 43.20 |
| B7 LIFE IS SEEN, NOT PASSED - the page lives INSIDE, the plate drifts (R26-228) | every row | present | 12.00; 20.00 vs 22.00; 44.00 vs 46.00 | the plate half is measured and clean (+21 px in 2 s, row 9 above). The page half is present but small: the three lead points are drawn on the three landed line ends (frame 12.00, cropped - a dot at each end tag), and registering 20.00 against 22.00 the whole page translates **dx +5 / dy -2 px in 2 s** with a residual difference after alignment (some of which is the caption changing words). The operator's own line is that the deckle's breath is NOT the life he asked for; the lead points are, and the glow/pulse amplitude is at the edge of what a 2 s pair can separate - a row for his eye, not for a number |
| B8 THE CHART'S TEXT IS SIZED FOR THE PHONE at 16:9 - *"a number, not a feeling"* (s82 (3) and (f)) | every page row | **absent** | 1.20-42.90 | measured on the page's own DOM, in STAGE px: **ticks 29-30, end tags 32, caption 33-34, source 26, sub 24-25, title 39-40**. The governing number is `docs/content-video-engine/50-THE-PHONE-IS-THE-SCREEN.md:47`: *"A font must be >= 59 px on our stage to reach 12 px on a phone in portrait"*, and its addendum is explicit that **59 px is the LANDSCAPE stage's floor** and must not be carried across from 9:16. Doc 50 §50.2's own table puts 30-34 px at "6.1-6.9 px - illegible" and 40 px at "8.1 px - marginal". So on this build every class on the page except the title is in doc 50's illegible band. This is a real 2.3x improvement on copy d (§8's 5.4-6.4 css) and it is still under the floor. **I disagree with `BUILD-NOTES` §8's cite** (*"Type in CSS px at 16:9 (doc 49 s49.1's floor is 12)"*): §49.1 is the vertical safe box and states no 12 px type floor; and the numbers tabulated there are the browser's CSS px, not the stage px doc 50 measures |

---

## Table 2 - ATTRIBUTION QUALITY

| row | what it does | attribution | note |
|---|---|---|---|
| 1 (0.00-43.04) | `ledger:ev-divergence-v1:line:234:right:axes:cut;idle=live;domain=80,277;build=lines:1.2`; dock `dock-h-certificate-1845` 9.2-16.64 `centre/arrive: throw/mass: paper`; exit `melt:throw:1`; species `build_to`, `retitle` x3, `chart_to rescale`, `build_to`, `spread`, `figure`; camera keys 36.19/37.59/39.99 | **UNATTRIBUTED: the four engine doors (`;domain=80,277`, `;build=lines:1.2`, the full-stage/anchored caption, the kinetics dials) and the exit token** | Two tokens ARE attributed claim-level and I say so: `:axes` by `Recall(rulings) OPERATOR-RULINGS.md:2342` ("The hook opens on its axes") and `;idle=live` by `:1494` ("Nothing ever goes truly still"). Everything this bed was built to prove carries no cited span - R26-223, R26-226, R26-205, R26-228 and E99 s82 appear nowhere in the receipt, and neither do the throw/`mass: paper` (s71), the `chart_to rescale`, the `spread`, the `figure` or the camera (s76 / R26-201). One cited line is worse than silent: `:3278` (s80, the slot hand-over to "the Bravos chart card") states a rule for a card E99 s82 struck from this row |
| 2 (43.04-52.85) | `world-three-notch-slate-v1;use=landing;idle=drift;drift=20`, ken `(0.04, 10, -6)`, `agenda` 43.04 +9.41 with three rows at 43.04 / 44.09 / 45.62 | `Recall(world) OPERATOR-RULINGS.md:3248` "A plate's life is DIRECTIONAL" (the ken tuple + the 20 px drift); `Recall(motion) CAPABILITIES.md:44` "THE NUMBERED AGENDA (P52 T8)" (the three rows, one per word); `Recall(rulings) :1494` (`;idle=drift`) | Attributed on the three choices that carry the row. Two gaps are named for honesty, not scored: `use=landing` obeys E61's three-uses rule, which the receipt never cites (and nothing lands on the plate); and the plate's SELECTION at this beat is `BUILD-NOTES` §8b's reasoning, not a cited span |

No `overrides.json` in this build, so the denominator is the two compiled rows.

---

## Two more things the frames say (INFO, no row of their own)

- **0:04-0:25 is one held chart.** Between the build landing (3.60) and the first retitle (24.96) the only
  visual events are the card's throw/park (9.2-16.64) and the captions - `bed.png`'s 6.00 / 12.00 / 18.00 /
  24.00 tiles are the same frame with a different caption. The shipped gate reads this as M05 / M10 / M16
  (8.3 s at 0:16). §8's answer is that R26-205 moved the captions out of STAGE mode so the gate stopped
  counting them; that is true of the COUNT, and it does not change what the 20 s look like. This is the
  operator's E21 question, and it is his to answer, not the gate's.
- **The retitle lags its own sentence by ~6 s.** The caption reads *"Here's the layer it never drew."* at
  28.70 while the title still reads *"AI is 1845 again"*; the retitle carrying those words fires at 34.50
  (title box `[101,36,240,64]` @34.60). And `BUILD-NOTES` §8's card row prints two different sizes for the
  same card (*"101 x 102 px"* and *"[1421, 687, 230, 210]"*); the DOM reads `[1421,687,230,220]` parked.

---

The two doors that closed since copy d closed cleanly and are worth saying plainly: the 0:04 rescale is
gone (B1's first half) and the 0.64 park is gone (B4) - both were the operator's own refusals. The
mechanism fraction below does not rise to meet them, because this read adds the bed's own eight owed
doors to the eleven-item list; **it is not comparable to `build-h-frozen-d/CRITIC.md`'s fraction**, which
was scored against the list alone on a different, three-row cut.

mechanisms present 12/15 (list of 2026-09-16 + the bed's own doors, E99 s82)
rows attributed 1/2
