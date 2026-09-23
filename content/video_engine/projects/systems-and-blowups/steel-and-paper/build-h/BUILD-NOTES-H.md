# BUILD NOTES H - the 1:30 unit (P68 T5)

Every gap, every departure and every measurement of the first LONG-FORM build to run through the
authoring kit. The build is `build_episode_h.py` -> `build-h/`; the table a human reads is
`SHOT-TABLE-H.md`; the logs of every gated command are `build-h/logs/`.

**The cut:** 0:00-1:32.77 on the FINAL scratch take (838.77 s / 13:58), treatment rows 1-9,
**three world rows, zero cuts, three dips**, 243 visual events (157.2/min). Second pass: the parent's
seven collisions (s2). Third pass: the critic's attribution, stillness and tail rows (s2b). Fourth pass:
the critic's HOOK row (s2c). Fifth pass: the critic's spoiler, double-draw and one-tick rows (s2d).

---

## 1. The order of proof (R26-198, E99 s78/s79) - what ran, in this order

| # | command | log | verbatim result |
|---|---|---|---|
| 1 | `python build_episode_h.py` (compile) | `logs/build-fix3.log` | `scenes : 3 (one per world plate)` / `2 ledger pages` / `docks : 2 across 1 scene` |
| 2 | the cues, bound to what the compiled timeline FIRES (`authoring.audio.bind_cues`) | `logs/build-fix3.log` | `cues : 8 bound of 8 derived` |
| 3 | `gate_motion_density.write_report` - stamped AFTER the binding | `GATES-MOTION.md` | `RESULT: 1 FAIL / 3 WARN / 20 PASS / 1 JUDGE / 8 INFO` |
| 4 | `probe.py build-h --gate`, then the report re-stamped on the fresh probe | `logs/probe.log` | `restamped 1 FAIL` |
| 5 | `self_watch.py build-h --project <project> --script SCRIPT-H --long` | `logs/self-watch.log` | **REFUSED** - the missing door in s4 #1 (the sheets ARE written: `self-watch/opening.1-4.png`, 0:00-1:32 at 2 s steps) |
| 6 | `measure_frozen_frames.py build-h` | `logs/frozen.log` | `no run of identical frames over 0.50s (whole frame)` (E49 / M18 PASS) |
| 7 | `lint_species_choice.py <project> --build build-h --table build-h/SHOT-TABLE-H.py --long` | `logs/lint-species.log` | `INFO long form (93 s): E61 - every plate names its use (;use=landing|bridge|reset)` |
| 8 | `recall_verify.py build_episode_h.py` | `logs/recall-verify.log` | `PASS - 12 citation(s) verified across 9 stages.` |

No gated command was piped into `head` or `tail`; each was redirected to its own file and the file read.

### The one FAIL: the rescale's own tick hand-over

```
[FAIL ] M28 5 pair(s) of a page's own labels sitting on each other over 51 instants probed:
        tick:index · 100 =  on tick:index · 100 =  at 0:05 (s01), 9,531 px, 100 % of the smaller label;
        tick:Jan '26 on tick:Jan '26 ... tick:Apr '26 on tick:Apr '26 ... (0:05, s01)
```

Every pair is a label **on an identical copy of itself**: the hook's `chart_to rescale` changes the Y
domain only, so the outgoing state's X ticks and the incoming state's X ticks are the same words at the
same coordinates for the 0.9 s the axis hands over. "A number on a number is not a number" is about two
DIFFERENT numbers; this is one word drawn twice. **Read on the frame at 5.2 s** (`logs/`): the ticks
`Oct '25 · Jan '26 · Apr '26 · Jul '26` read cleanly, the y axis is mid-hand-over with `160` standing,
and the three lines are drawing. The engine row: a y-only rescale should un-write the ticks it is
replacing (or reuse them when the x domain has not moved) - `rescale_state`
(`build_scene_timeline_f.py:2316-2368`) hands over the whole axis either way.

### The three WARNs, each with the reason it stands

- `M04 3 distinct plates; target runtime/12s = 7` - **the point of the cut** (E58/E61: the page IS the
  world; `build-f` made 75 windows across 73 worlds and that is the fault this rebuild closes).
- `M21 1 page(s) deployed past 12s after the last data mark: s01 23.4s (0:31 -> 0:54)` - the page's
  last DATA mark is the recast; what follows is the page becoming the next thing (the ends, two
  retitles, the park, the agenda beside it), which is E50's own alternative.
- `M25 4 safe-zone intrusion(s): a card is 30 % inside the bottom safe-zone band at 0:10 ... 0:24` -
  the two cards' FLIGHTS pass through the bottom band; both landed boxes are clear of it.

---

## 2. The parent's seven, each fixed in the table and measured

| # | what the parent read | what the table does now | the measurement |
|---|---|---|---|
| 1 | the STAGE caption ON the page's terminal tags at 18-30 s and touching them at 32-40 s | there is no door to shorten a tag and none to move a page row's caption (s4 #8), so **the page PARKS to 0.64 the moment its last line is drawn** (`PARK_TAGS_SCALE`, on "is still carrying trains") and stays parked through the recast - a park scales the tags with the chart | caption box `[1111, 432, 692, 144]`; tag boxes and their overlap with it: **17.25 s** `+105% SEMICOND [697,351,216,19]` **0 px**, `+21% MAMAA [697,484,112,19]` **0 px**; **24.16 s** both **0 px**; **29.25 s** all six tags **0 px**; **35.67 s** all four **0 px**. Before the park (first pass) the same tag overlapped by **7,020 px** |
| 2 | three rings with no correct target (6 s, 26 s, 42 s) | all three removed (E99 s76). The `+613%` figure on series 0 stays - it is the one mark this page can aim | the two frames that proved it: at 37.4 s a ring targeting `series: 2` and at 39.6 s one targeting `series: 1` both drew on the MEMORY line's tip |
| 3 | stale railway ink on the GDP page at 84-90 s | there is no GDP page any more (row 7), so the notes and the `741 RAILWAY SHARE PRICES` tag stay on the page that wrote them | sheet 4: the two notes stand in the railway page's quiet zone from 0:76 to the unit's end, on their own chart |
| 4 | the Bravos card over Mike's face at 58-62 s | **the card is off the host plate.** A dock on a picture plate cannot be placed at all (s4 #10), so obeying "never over the host" means not docking it there; the window keeps the plate, the ken push, the 20 px drift, the chip and the flow | the compiled dock carried `arrive` + `mass` and **no `place`**; the engine's solo card landed at `[758, 167, 1068, 515]` - across the host |
| 5 | the caption at 58-62 s barely legible in the dark under the card | with no dock live the caption is back in **STAGE mode** at full size, where it read at 0:56 | caption box `[199, 432, 1522, 72]`, `mode=stage` at 60.58 and 62.16 (it was the 41 px anchored strip `[145, 919, 1630, 41]`). Ground luma under the band, median / p95 of the glyphs: **56.0 s 51/235, 58.5 s 49/204, 60.6 s 44/234, 62.5 s 43/244** - white type on a ground at luma 43-51 is about 11:1, well over the 4.5:1 floor |
| 6 | "This certificate" (10 s) over the thrown card | the card is thrown **on the cut BEFORE its sentence**, not on its first word: a caption page is stamped stage/anchor by whether a dock is live at the PAGE'S START (`_dock_live_at`), so a card one word late has the whole first page written across it | overlap of the caption box with the card: **10.06 s 0 px** (card `[1354, 648, 326, 308]`), **12.21 s 0 px** |
| 7 | the caption says "seven percent"/"eight" over an 11.54 % chart | **the share-of-GDP page is not shown under those words.** The dossier's routed object IS `ev-equip-ipp-gdp-v1` and what it measures is equipment + IP investment as a share of GDP - 11.539 % at the Q2-2000 peak, 11.505 % today - so it cannot stand under seven and eight. The railway page holds to the unit's end | the object the sentence needs (AI / tech spending as a share of GDP on Bravos' math) **is missing from disk**: HG3's row |

Six more collisions were found and fixed on the first pass, before the parent's read: the agenda
written through by the caption (the block moved below the measured caption band), three end figures
stacked on one datum, the camera cutting the page title (the `focus_zoom` species is the engine's
fixed 1.32 - the move is authored as camera KEYS at 1.06), a card reading over the page's data, an
11.3 s dead frame at 0:10-0:21 (the line now builds under the card, one step per phrase), the first
chart entering unannotated, a 3.9 s hole on the host plate, a recast carrying the wrong title, a ring
landing outside the plot, a stale `-64%` figure on the next chart, and two span names on the page's
own rule. Each is a named constant in `build_episode_h.py` with its measurement.

## 2b. The director-critic's three, each fixed in the table

| # | the critic's row | what the table does now | the measurement |
|---|---|---|---|
| 1 | ATTRIBUTION - the opening page was `ev-bravos-original-v1`, `status: SOURCES-TO-VERIFY` | **the page is the VERIFIED `ev-divergence-v1` from 0.00 to 0:54, one object, one state, no recast** - and the memory line is STAGED ON IT: `MEMORY_STAGED`, a `build_to` that names `series: DIV_MEMORY` holds it at its first datum from 0.00 and a second one draws it to its end on "Here's the layer it never drew". **The kit allowed the better route**: a PAGE species may name the series it performs on (the engine's perform layer filters by `sp.series ?? sp.tier ?? sp.target.series`, `scene-evidence-engine.mjs:11362`) - which the generic marks (callout / spotlight / focus_zoom) cannot do (s4 #2). The card at 0:24 is `dock_png` of `evidence/objects/ev-divergence-v1.png` - a still of the same verified page | read on the frames: **26.0 s** three lines only (semis +105 %, S&P +21 %, mega-cap +21 %), no memory line and no memory tag; **34.0 s** the memory line at +613 % with the object's own "our layer" badge and the spread bleeding the gap between the giants and it. The unverified file is cited nowhere in the cut |
| 2 | STILLNESS - the railway page held bare axes 10.2 s | the index **draws from the dip**: `RAIL_STEPS` climbs the 1843-45 bull one step per phrase (the dip, "Every transformative technology overshoots", "Railways in the 1840s"), then takes the peak on "a quarter-billion pounds" and the crash on "two-thirds" | read at **70.0 s**: the line is already climbing off the 1843 level with its tip dot, 3.9 s after the dip; the page's marks are never `n 0` past ~2 s |
| 3 | THE TAIL - an orphan caption "So" on the last frame | the unit ends on the **last HARD STOP before the P12 boundary** and the audio runs `UNIT_TAIL_S` 0.6 s past it, so the line lands instead of snapping | the take's boundary is 92.88 and the word "So" starts at 92.875; the unit now ends at **92.77** with the last word `eight.` (ends 92.175) and the last caption page `AI spending just crossed eight.` 89.89-92.17 |

## 2c. The critic's HOOK row: the chart the video opens on

**The defect:** the object is log-scaled for a line that ends at 712, so with the memory line staged the
two lines the hook is ABOUT sat flat under the bottom tick, and the end tags printed 30 s before the
words named them.

**The door exists, and it is the operator's own mechanic.** `chart_to rescale` takes a per-state Y
DOMAIN - `ymin` / `ymax` on the species, carried into the derived state as `axes.domain`
(`build_scene_timeline_f.py:2356-2357`, `rescale_state`). So the page now carries two rescales, both
with their bounds read off the data, never typed:

- **the hook's scale** - `HOOK_YMIN 95 / HOOK_YMAX` (1.06 x the two lines' own maximum) on "Not the
  chips, not the models, not the machines";
- **the axis opening as the layer arrives** - `FULL_YMIN / FULL_YMAX` (1.06 x the memory line's
  maximum) on "Here's the layer it never drew", on the same clock the memory line draws on.

**And every line the hook draws is STAGED** (`STAGED_SERIES`), one step per phrase of the sentence that
owns the beat, so a series' end tag lands when its own line lands - at 0:17, with the sentence that
ends the certificate beat - and never at 0:03. The memory tag lands with the memory line at 0:31.

**Measured, the plot's ink height (the drawn data's box against the plot's own box):**

| t | before | after |
|---|---|---|
| 0:02-0:03 | 62 px of 471 px - **13 %** | 130 px of 471 px - **28 %** |
| 0:08-0:09.6 | 62 px of 466 px - **13 %** | 129 px of 466 px - **28 %** |
| 0:16 | 70 px of 301 px - **23 %** | 173 px of 301 px - **57 %** |
| 0:31 (the layer, after the second rescale) | - | 295 px of 301 px - **98 %** |

(The 28 % at 0:02-0:09 is the STAGING, not the scale: a quarter of the year is drawn by then. The
scale is the hook's from 0:04 and the lines fill the plot as they climb.)

**What the kit refused: departure 11.** A page cannot be BORN with a domain. Its opening state is built
from the evidence object alone (`ledger_world` -> `LPG.build_spec`), `AXES_KEYS` (`ledger_page.py:79`,
which includes `domain`) live on the OBJECT, and `PLATE_OPTS` (`build_scene_timeline_f.py:111`) has no
scale option - only a DERIVED state (a `chart_to rescale`) may name one. A rescale at 0.00 was tried
and refused twice over: `M23` ("s01 rescale at 0:00 fires inside the page's build beat - E45: never
over a build") and `M28` at the video's own first frame. So the hook's rescale fires on the first word
after the page's build lands (0:03.9, "Not the chips"), and **the first four seconds still stand on the
object's own scale** - the residue of the missing door, and the one thing the parent may want to weigh
against the alternative (open on a second object, which would cost the attribution or a label
hand-over).

## 2d. The critic's copy-c three

**1. The card no longer spoils the payoff.** `ev-divergence-v1.png` is the FINISHED four-line chart -
the memory line, its legend and +613 % - and it was on screen at 0:24, five seconds before the sentence
that reveals them. The kit's door for the critic's first choice is `docks.chart_card` ->
`chart_card.render_card`, which renders a PAGE from a series object: so the build DERIVES one -
`_hook_object()` writes `build-h/objects/ev-divergence-hook-v1.series.json`, the verified object with the
staged series dropped and its memory badge with it, every number copied and none typed - and renders the
card from that. Read on the frame at 26.5 s: the card carries the two-line chart under the title "Two
lines, one warning", the page behind it carries the same two lines on the hook's scale, and nothing on
screen knows about memory until 0:30. (The page's own SUB still reads "plus the S&P 500 and the memory
builders" through that window - it is the object's text and the object is read-only.)

**2. The reveal no longer double-draws.** The rescale was firing on a PARKED page. The park is now
released `UNPARK_LEAD_S` 0.9 s before it - the memory line needs the room anyway - and the axis
hand-over is shortened to `RESCALE_S` 1.0 s. **Measured at the critic's own instants** (`probe.Probe.at`,
the page's chart box and every label the page draws):

| t | chart box | labels (ticks) | y ticks | before |
|---|---|---|---|---|
| 29.5 | `[148, 172, 1083, 779]` | 10 (7) | 80, 160 | box 693 |
| 29.8 | `[147, 171, 1084, 780]` | 16 (13) | 160, 320, 640 | - |
| 30.0 | `[145, 171, 1086, 781]` | 16 (13) | 160, 320, 640 | box 1086 |
| 30.5 | `[142, 169, 1091, 784]` | 11 (8) | 160, 320, 640 | box 700, 16 labels |
| 31.0 | `[139, 168, 1095, 787]` | 12 (8) | 160, 320, 640 | - |

The chart box is now stable across the whole reveal (989 -> ~1090 as the page un-parks, never 693 ->
1086 -> 700) and one axis' worth is 8 ticks (3 y + 4 x + the y label). The 16-label peak is the axis
HAND-OVER itself and it lasts the rescale's own 0.7 s (29.55-30.25): **the engine writes the arriving
axis before the standing one leaves** (`rescale_state` + the engine's `AXIS_HAND`,
`build_scene_timeline_f.py:2316-2368`), which is the same door as the M28 tick-on-tick above. Shortening
`RESCALE_S` from 1.6 to 1.0 is all a row can do; three of the four instants are inside one axis' worth
and the fourth (30.0) sits in the hand-over.

**3. Two ticks on the hook's scale.** The engine's log axis ticks at DOUBLINGS of a power of ten from
`10^floor(log10(ymin))` (`scene-evidence-engine.mjs:8717-8722`), so from ymin 95 the sequence was
10-20-40-80-160-320 and only **160** fell inside the hook's domain. The sequence reaches 100 only when
ymin >= 100 - and the mega-cap line's own low is **93.94**, so a domain that prints the baseline would
CLIP the data. The honest pick is the widest domain that clips nothing and prints two: **`HOOK_YMIN 80`,
`HOOK_YMAX` = 1.06 x the hook's own max (277)**. Measured:

| t | y ticks | ink height |
|---|---|---|
| 5.18 | **80, 160** | 112 of 466 px (24 %) |
| 12.21 | **80, 160** | 98 of 300 px (33 %) |
| 15.57 | 80, 160 | **151 of 301 px (50 %)** - the 16 s fill |
| 17.25 | 80, 160 | 240 of 298 px (81 %) |

(The baseline 100 cannot be a tick without clipping; the page states it in words - "100 = Aug 2025, log
scale" - on its own y label.)

**Carried, not fixed:** the first ~5 s stand on the object's own scale (R26-223, a page cannot be born
with a domain - departure 11), and the railway page holds still under "seven percent" because the object
the sentence needs is missing from disk (HG3's question, s5 #1).

---

## 3. What is on screen, read on this build's own frames

The contact sheets are `build-h/self-watch/opening.1-4.png` (0:00-1:32 at 2 s steps).

| at | what is on screen | collision? |
|---|---|---|
| **0:02** | the ledger page **on its axes** (E73), its title writing in the page's hand, the three lines starting on the object's own scale; the caption in the page's right room | the four seconds before the rescale are the flat residue of departure 11 |
| **0:06** | the axis has RESCALED to the hook's own bounds - the two lines the hook is about fill the plot and climb | none |
| **0:12** | the certificate card landed low-right, the page's line building under it, the caption at STAGE size above it | none (0 px, measured) |
| **0:18** | the page PARKED to 0.64 with its tags beside it, the caption clear to its right, the card gone on its own sentence | none (0 px, measured) |
| **0:18** | the three lines complete and their end tags land together (+105 % / +21 % / +21 %) - no tag printed at 0:03 | none |
| **0:24** | the parked chart left with THREE lines, and a card of the TWO-LINE chart dropping into the slot the certificate left (E99 s80) - "his fourth copy of the same chart", rendered from the derived object so nothing on screen knows about memory yet | none |
| **0:30** | the page un-parks, the axis opens from 80/160 to 160/320/640 and the MEMORY line draws to +613 % on the words that name it - one page, one object, one clock | the axis hand-over's own 0.7 s carries both tick sets |
| **0:34** | the spread bleeding the gap between the giants and memory - the layer it never drew, as a region | none |
| **0:36** | the hand re-titling "The layer it never drew", the caption on its right | none |
| **0:40** | the `+613%` figure at the memory line's end, the camera at 1.06 on that datum | none |
| **0:46** | the chart parked to 0.52 and the numbered agenda landing row by row in the room it freed | none |
| **0:58** | HOST WINDOW 1: Mike at the studio desk, **no card on him**, the caption in STAGE mode over the dark left | none |
| **1:02** | the NVIDIA chip landed and crossed out on "and it isn't Nvidia" | none |
| **1:04** | the flow `CAPITAL -> VALUE` drawn in the studio's dark upper-left, the caption under it | none |
| **1:10** | the railway index already climbing off the 1843 level (it starts on the dip), the £250m note writing in the quiet zone | none |
| **1:22** | the line at its 1845 peak and falling, the second note ("then -64% by 1850") under the first | none |
| **1:26** | the railway page holding while the caption carries "crossed seven percent of GDP" | **no chart under those words by design** - s2 #7 |
| **1:32** | the last full sentence closes on "AI spending just crossed eight." and the cut ends 0.6 s later | none - no orphan word |

One thing the parent should judge on the watch, not a gate row: the page is PARKED to 0.64 from the
certificate's arrival (0:10) to the agenda's park (0:44), because that is the only door that keeps the
page's terminal tags out of the caption's room and out from under the card (s2 #1, s4 #8-#9). The
chart therefore reads at about two thirds of its drawn size for most of row 1 - the cost of the 16:9
geometry, and the reason departure 9 is written down.

---

## 4. The doors: what the kit gave, and what it refused

### What worked, first time

`authoring.Project` + `words.take_words` on the scratch take as it stands (`vo-h-scratch/` is only
read); `table.at` / `words.cut_before` for every anchor; `ledger:<series>:line:<emph>:right:axes:cut;idle=live`
for the open on the axes; `;then=` + `chart_to recast` for the chart-to-chart; `;use=landing;idle=drift;drift=20`
+ the ken tuple for the plate (the lint reads the use back); `docks.register` for a project-local Flow
plate as a world (no engine change); the numbered agenda; the flow diagram with the sourced glyphs
`coins` and `factory`; the chip with its cross; `chart_to park`; camera KEYS as the row's 8th element;
`authoring.audio` for cues bound to what fires; `recall_verify` with the R26-197 shim.

### The doors that were MISSING, each with the path:line

1. **`self_watch.py` cannot run on a long-form build whose table is not `SHOT-TABLE-SHORT.py` in the
   project root.** `lint_species_choice.py:51` `TABLE_NAME = "SHOT-TABLE-SHORT.py"`,
   `lint_species_choice.py:561` `table = table or project / TABLE_NAME`, and `self_watch.py:746`
   calls `L.report(project, build=...)` with no `table=` and no CLI flag to pass one. The bar dies
   after it has written the probe, the sheets and the gate, and before `SELF-WATCH.md`. **`build-h/SELF-WATCH.md`
   does not exist for this cut**; section 2's eleven O-rows are answered in s3 above. One argument fixes it.
2. **A mark cannot name its SERIES on a multi-line ledger page.** The compiler passes
   `{"kind":"datum","index":234,"series":2}` through unchanged; the engine clamps it -
   `scene-evidence-engine.mjs:12365` `pts = lpst && lpst.linePts ? lpst.linePts[tg.series | 0] : null`
   and this page's `linePts` carries one series. Measured on two rendered frames. Consequence: the
   three end figures are the page's own terminal tags, and only series 0 carries an authored mark.
3. **`docks.still_card` / `docks.dock_png` crop a full-width BAND only** (`authoring/docks.py:85`).
   One certificate out of `world-certificate-wall-v1` needs an x; `docks.dock_still(..., still=True,
   frame_crop=(w, h, x, y))` (`authoring/docks.py:70`) is the kit's only x-aware crop and reads a PNG
   as happily as a clip. A `still_card(..., crop=(x, y, w, h))` is the honest door.
4. **A `figure` or a `note` the page writes is never cleared by a `chart_to`** (measured: a `-64%`
   figure and a note stood on the next chart eight seconds after the recast). A `bracket` DOES leave
   with the line, but at 16:9 it drew as a naked red span at the plot's edge with no room for its
   label (measured at 83.0 s on the first pass) - the fault Tokyo's own row records.
5. **No `pill` species** (`pill=` on a plate id is a dense-line page's TIP pill,
   `build_scene_timeline_f.py:111`). Built as a `note`.
6. **A unit build has no door:** the compiler stretches the LAST row to `timeline.runtime_s`
   (`build_scene_timeline_f.py:5162`), so a 1:30 unit of a 13:58 take must be a real 1:30 cut - the
   module trims the take with ffmpeg into `build-h/audio/` and truncates the words.
7. **`recall_verify.py` does not take a build dir** (`recall_verify.py:154-157`); run against the
   module, which IS this cut's ledger under the R26-197 shim.
8. **A page row's caption cannot be moved, and a page's terminal tags cannot be shortened.** The
   names live in the evidence object (read-only) and `PLATE_OPTS` (`build_scene_timeline_f.py:111`)
   has no label option; `ledger_page.CAPTION_ANCHOR` 16:9 = `(145, 878, 1630, 82)` exists and ONLY a
   live dock demotes a caption to it (`_dock_live_at`). The one door a row has is to make the page
   smaller - which is what this cut does, and which costs the chart a third of its size.
9. **The 16:9 page draws its plot in the LEFT half and keeps the right half quiet for the caption,
   so every chart reads half-size.** Measured on this build: the page's own boxes at 52.02 s are
   `plot [180, 236, 403, 244]`, `chart [140, 168, 568, 409]`, `title [58, 39, 277, 64]`,
   `source [140, 969, 510, 41]` while the stage is 1920x1080 - and unparked the chart box is
   `[140, 168, 870, ...]` with its tags running to x 1527. The caption's strip is the right third by
   construction (`caption_strip_x`, `build_scene_timeline_f.py:4333-4341`: with `quiet_zone: right`
   the caption takes x 1114-1800). Nothing puts a page row's caption in the anchored bottom strip,
   so the page and the words share one frame side by side instead of one over the other. **This is
   the 16:9 geometry row the treatment says has no capability entry** - T3's audit owns it.
10. **A dock on a picture plate cannot be placed by the author.** `dock_place`
    (`build_scene_timeline_f.py:4005-4011`) returns None unless the world is a ledger page (E45: "a
    dock on a plain plate keeps the solo card"), so `centre`, `centre_w/x/y`, `read`, `read_s` and
    `park_s` are all dropped for a card on a plate. Measured: the compiled dock carried `arrive` and
    `mass` and no `place`, and the solo card landed at `[758, 167, 1068, 515]` - across the host's
    face, in the frames the Flow order kept his left third clear for. **The host window therefore
    carries no card at all.** The door: a plate's own declared room for a dock, as a page has.

---

## 5. The evidence: what the treatment asks for that is not on disk (E77 - no figure is invented)

1. **The 7 % and the 8 % of treatment row 9 have no series.** `ev-equip-ipp-gdp-v1` measures
   equipment + IP investment as a share of GDP: **11.539 %** at the Q2-2000 peak, **11.505 %** today.
   The dossier routes the sentence there (`evidence/EVIDENCE-DOSSIER.md:120`) and records the
   correction (`:250`). A chart reading 11.5 under words that say seven and eight is a different
   measure on screen than in the sentence, so **it is not shown**: the railway page holds through
   the sentence and the object the script needs is missing. HG3's row: either the line moves to the
   PIMCO framing the dossier recommends, or the object is built.
2. **The treatment's "-66%" is the object's -64 %** (`ev-railway-index-v1` marks 2,062 -> 741, and the
   page's own title reads "fell 64% from their peak"). The build writes -64 %.
3. **`ev-bravos-original-v1` is not used at all.** It carries `status: "SOURCES-TO-VERIFY"` and the
   operator's own note; the director-critic's attribution row struck it from the world and from the
   card, and the verified `ev-divergence-v1` does both jobs (s2b #1).
4. **The certificates on `world-certificate-wall-v1` are blank** - the card reads as ornate deckled
   paper, not as a document with words on it.

---

## 6. The counts, against the treatment's own

- **Idle tokens: 3 of 3 rows** (`;idle=live`, `;use=landing;idle=drift;drift=20`, `;idle=live`). The
  treatment counts nine page rows live + one plate drifting for rows 1-9 because it counts one table
  row per treatment row; this build carries the same nine treatment rows in THREE world rows, which is
  E58's spine and E99 s74's "a cut or a dip is the last resort". Every world row carries its idle, and
  `measure_frozen_frames` finds no run of identical frames over 0.5 s anywhere in the unit.
- **Flow count: 0 cuts, 3 dips** (page -> studio at 0:54.90, studio -> page at 1:06.15, and the unit's
  own end, which T6 takes on). Each dip is a world change and refuses the same transform.
- **Cards: 2 arrivals in ONE slot** on the page (the certificate thrown, a still of the page's own
  verified render dropped into the room it left - E99 s80). None on the plate (s4 #10).
- **Objects on screen: two, both verified.** `ev-divergence-v1` (names corrected 2026-09-03) is the
  world and the card for rows 1-6; `ev-railway-index-v1` is the world for rows 8-9. The
  SOURCES-TO-VERIFY file is cited nowhere.
- **Camera: 1 move**, authored as keys at zoom 1.06 on the +613 datum, on the words that name it.
- **Sound: 8 cues, 8 bound.** Two page enters (`axes`), two landings at their contact frames, three
  dips, one bed at -28 LU under the voice (the long form's calibration; the take measures -28.0 LUFS
  untoned, so the bed gain is 0.0073). No cue claims an effect the compiled timeline does not fire.

## 7. For T6 (the body) and for the parent

- The unit's last row exits `dip` into nothing; T6 picks it up at "So the obvious move" (P12).
- `build_episode_h.py --whole` refuses by name until T6 authors rows 10-24.
- The script moved three times under this build, so the fragile anchors resolve through `any_at(...)`,
  which takes the first wording the take carries and refuses by name if none is there.
- Nothing outside `build-h/` was written: `_assert_read_only` fingerprints `build-f/`, `SHOT-TABLE-F.py`,
  `build_scene_evidence_cut.py`, `vo-f/`, `vo/`, `vo-h-scratch/`, `REBUILD-TREATMENT-H.md`, the
  `SCRIPT-H-*` files, `evidence/`, `sound/`, `host/`, `packaging/` and (P69 T14) `REFERENCE-F.md` before
  the build and asserts them unchanged after it.
- This build was never served and no frozen copy was made (the parent's, E99 s75 / R26-193).

---

## 8. THE 30-SECOND BED on the three doors (E99 s82 (b), 2026-09-18)

The build is now the FIRST WORLD ROW ONLY - 0:00 to the dip into the studio, 52.85 s on the new take
(rate 1.14). The rows after it are T6's. What the doors replaced, and what they measure:

| the door | the token this row writes | what it retired |
|---|---|---|
| R26-223 | `;domain=80,277` - the page is BORN on the hook's scale | the 0:04 `chart_to rescale` (ink that moved while no word named a move) |
| R26-226 | `;build=lines:1.2` - `build_s` 4.8, the windows `[[0,1.2],[1.2,2.4],[2.4,3.6]]` | fifteen per-phrase `build_to` species (the crawl that stops) |
| R26-205 | nothing - a 16:9 page row is stamped `full_stage: true`, `caption: "anchor"` | the 0.64 park that kept the tags out of the caption's room |
| R26-228 | `plate_idle_paints: true`, `plate_idle_drift_px: 20` in the build's kinetics | an authored `;drift=` that painted 0 px |

**The slot fix (the held series takes no turn) is in**: `build_lines` is THREE windows, not four - the
drawing lines start at 0.00 and the build ends a turn early, the memory series joining on its own
reveal cap at 0:29.

**Each line lands whole, with its own tag and badge** (probe, this build):

| t | what is whole | its tag |
|---|---|---|
| 0.60 | semis drawing (`drawn 0.49`) | - |
| **1.20** | semis WHOLE (`marks n 1, drawn 1`) | `+105% SEMICONDUCTOR STOCKS` + "their divergence" |
| **2.40** | mega-cap whole (`n 2`) | `+21% MEGA-CAP TECH STOCKS` + "matches the market" |
| **3.60** | S&P whole (`n 3`) | `+21% S&P 500 (the market)` + "the market" |
| 29.25-31.5 | the memory line whole on "Here's the layer it never drew" | `+613% MEMORY MAKERS (hynix+Micron)` + "our layer" |

**The lead points**: three on the three landed lines at 0:24 - teal at the semis' end, blue at the
mega-cap's, grey at the S&P's, each with its own bloom; the held memory line has none (R26-228's rule).

**The geometry, measured**: plot `[140, 247, 958, 580]` (958 px = 49.9 % of the stage width, the lane's
own ceiling), chart `[45, 193, 1350, 756]`, parked for the agenda at 0.80 -> `[52, 194, 1072, 600]`.
**Type in CSS px at 16:9** (doc 49 s49.1's floor is 12): caption **14.6**, title **17.4**, end tags
**14.2**, ticks **13.0**, source 11.3, sub 10.8 - against 5.4 / 5.9 / 6.4 under the old 0.64 park. At the
agenda's 0.80 park the ticks fall to 10.4 and the tags to 11.3.

**The card**: the placer found NO room on a full-stage page and took the emptiest corner at the
legibility floor (101 x 102 px), so the row names the rectangle the page leaves - x 1400-1900, y 700-910,
between the lowest end tag (y 685) and the anchored strip (y 919). The card is `[1421, 687, 230, 210]`
and its overlaps are **0 px on the ink, 0 px on the tags, 0 px on the caption**. A card on a full-stage
page is SMALL, and that is R26-205's geometry, not a choice.

**The gate**: `RESULT: 4 FAIL / 4 WARN / 14 PASS / 1 JUDGE / 9 INFO`, `visual_events: 27 (30.7/min)`.
M28 and the card's M25 are gone with the rescale and the park. The four are M11 (unchanged: the only
mark the engine can aim lands on series 0, the undrawn memory line) and **M05 / M10 / M16** - and that
trio is a GATE ROW, not a cut fault: the previous cut counted 243 visual events, this one 27, because
R26-205 moved every page caption to the anchored strip (M08 counts STAGE caption pages as events and
counts nothing in the strip) and E99 s82 struck the fifteen staging species. The gate reads a page whose
life is exactly what R26-228 built - the tip spark, the bloom, the per-word breath - as a dead frame.
No species was invented to fill it (that is the crawl the operator refused).

**The sheet**: `build-h/self-watch/bed.png` - eight tiles at 0:02, 0:06, 0:12, 0:18, 0:24, 0:30, 0:38, 0:46.

### 8b. The 0:46 collision, fixed with the operator's own shape (R26-229 b)

The agenda's rows were landing on the PARKED page's end tags. A page parks for nothing, so the park is
gone and the beat is the operator's: on "One test," the whole chart **MELTS TO A BALL and is thrown off**
(`exit: "melt:throw:1.0"` on the page row - a melt takes the world, so it is the row's exit, E88 /
CAPABILITIES:37), and the board it clears for is **`world-three-notch-slate-v1`** - build-f's own plate at
this beat, dark enough for white type, and literally the three questions as an object. The agenda lands
CENTRED on its face, one row per word: "three questions" / "thirty seconds" / "and it sorts".

- **The melt's length is 1.0 s** so the board is there ON "three questions": the page row ends at 43.04.
- **The rows sit on 0 px of ink and 0 px of tag** - measured at 44.0, 46.0 and 50.0 s, the probe reports
  `page {}`, `labels []`, `overlaps []`: there is no page ink or tag left on the stage at all.
- **The block sits above the caption**: on a PLATE row the caption is back in STAGE mode (the anchored
  strip is the page rule) at `[192, 432, 1535, 72]`, 64-65 px / **28.4 CSS px**, so the block was lifted to
  y 0.10-0.37 (108-400 px) - 32 px clear of the caption's top edge. Read on the frame at 0:46: the three
  numbered rows across the slate's own three notches, the caption under them.
- **No value stamp beside the rows**: the `stamp` species is admitted for the VECTOR MAP's three species
  alone (`build_scene_timeline_f.py:671`), so there is no stamp at hand for a list on a plate. None drawn.
- The bed is now TWO rows - the page 0.00-43.04, the slate 43.04-52.85 - `visual_events: 48 (54.5/min)`,
  up from 27, and M16's 0:44 gap is gone with the park.

### 8c. Copy e's two, and R26-233 measured

**1. THE MELT IS IN THE CUT NOW.** A row's `exit` is the transition **INTO** that row
(`door_boundary_error`'s own docstring, `build_scene_timeline_f.py:2186`: "may the door INTO `sc` open
here?", with the predecessor passed beside it), and s01 has no predecessor - so the melt authored on the
PAGE row did nothing and the slate's empty exit fell to the mechanical dip. The melt now sits on the
SLATE row. Two things the engine then taught, both by refusal and both kept:

- `melt:throw` into a plate is refused **by name**: *"a throw hands the same board to the next chart
  (E88) - the incoming world is not a ledger page; say melt:splash:plate to paint a plate"*. So the
  ending is `melt:splash:plate:1.0` - the ball splashes onto the slate, the operator's own second ending
  (E76 s5, "splatter it back on to the canvas").
- the boundary moved one melt-length earlier (`t_melt = t_three_q - MELT_S_H`) so the melt RUNS over
  "One test," and ENDS as the slate lands on "three questions" - the agenda's first row fires on the
  slate, never inside the transition.

MEASURED on the frames (mean luma of the whole frame; the dip this replaced cored at luma 5):

| t | mean luma | what is on stage |
|---|---|---|
| 42.00 | 60.2 | the page, whole |
| 42.50 | 51.6 | **the ball** - the chart melted into one orange sphere with its shadow, on the page's own charcoal, under "One test," |
| 43.00 | 121.8 | the slate, landed |
| 43.10 | 121.8 | the slate |
| 43.30 | 122.2 | the slate, the first row firing on it |

**No black core anywhere** and the agenda's rows still measure `page {}`, `labels []`, `overlaps []` at
43.2 / 44.5 / 46.0 - 0 px on any remaining ink or tag.

**2. THE CERTIFICATE HAS ITS FACE.** The old rectangle took an empty cartouche and a neighbour's corner.
The new one is `CERT_CROP = (282, 238, 296, 146)` - **w 282, h 238, x 296, y 146** on the plate's own
1536x1024 frame - picked by eye off the plate and checked for the blue light shaft pixel by pixel. It is
the only certificate on that wall whose four borders, crest medallion, ruled signature line and engraved
vignette are all visible at once; the plate's blue light shaft clips its lower-left corner, which is the
plate's own light and not the crop's edge. The room and the 0 px are unchanged (`[1421, 695, 230, 194]`).

**3. R26-233 - the drop, measured.** The rescale's only dial on a row is its `dur`, so it is now the
memory line's own window: `RESCALE_S = MEMORY_DRAW_S = 2.2`, both opening on "Here's the layer it never
drew". The ink still moves, but it moves WITH the line's climb instead of in a 1.0 s hand-over beside it:

| t | the semis tag's y | the drop since 28.0 |
|---|---|---|
| 28.00 | 369 | - |
| 28.70 | 390 | 21 px |
| 29.25 | 483 | 114 px |
| 30.20 | 622 | 253 px over 2.2 s (~115 px/s; it was ~215 px/s in the 1.0 s hand-over) |

An axis whose EASING is the line's own climb - the breakthrough shape the critic names - is not a row's
to write: `chart_to rescale` takes a domain and a length and nothing else. That part stays R26-233's.

### 8d. The three doors of copy f, recompiled

**R26-232 - the gate now sees the page.** `RESULT: 1 FAIL / 2 WARN / 19 PASS / 1 JUDGE / 10 INFO`,
`visual_events: 151 (171.4/min)` against 49 on the same rows an hour ago: with the anchored caption pages
and the live page's own life credited, **M05, M10 and M16 all PASS** and M11 is the one FAIL - the row it
has been since the rings came off (the only mark the engine can aim lands on series 0, the undrawn memory
line). The two WARNs are M04 (2 plates) and M25's safe-zone (the card's FLIGHT clips the bottom band at
0:09-0:10; the landed box is clear).

**R26-234 - the words hold still.** Measured through the player's own DOM at 0:30 (the reveal, the busiest
instant on the page): **410 word elements inside the ledger world, 0 carrying a translate**. The life is
the lead point, the halo and the bloom, as the ruling says.

**R26-233 - the followed axis.** `"follow": True` on the reveal rescale, beside the `build_to` that stages
the memory line. The compiler refused the first attempt by name and the refusal was the measurement: the
memory series tops at 1074.29 and the page keeps x1.06 of air, so the highest a follow can push is
**1138.75** - `FULL_YMAX` is now that number exactly (it was 1139, "reached after the line had stopped,
which is the drag this row exists to end"). What the landed ink does:

| t | semis tag y | drop | y ticks |
|---|---|---|---|
| 28.00 | 369 | **0 px** | 80, 160 |
| 28.70 | 371 | **2 px** | 80, 160 |
| 29.25 | 481 | 112 px | 80, 160 |
| 30.20 | 623 | 254 px | 160, 320, 640 |
| 30.50 | 623 | 254 px (landed) | 160, 320, 640 |

**The 2 px at 28.70 is not the rescale**: the same tag reads 371 / 372 / 371 / 368 / 369 at 24 / 25 / 26 /
27 / 28 s with the domain unchanged at 80,160 - that is `;idle=live`'s own breath, a +/-2 px band. The
ticks are still the hook's at 29.25, so the axis has not yielded while the line is inside the born top;
it yields as the line passes it, and lands on the same frame as the plain rescale did (it was 21 px down
at 28.70 before the follow).

---

## 9. The body's preflight: rows 7-24, the data departures (P69 T14, 2026-09-22)

Folded in from `build-h/P69-DATA-DEPARTURES.md` (implementation_luna, P69 T14a; the text below is that file's,
its headings renumbered). The door carries the same record as constants: `BODY_ASSETS` (every page object with
its builder, card, plate, prop, host still, cue file and outro part, rows 7-24), `BODY_DEPARTURES`
(row, item, fallback) and `TREATMENT_SUPERSEDED` (E99 s84, s83, s91, E47, E50, each quoted). Since the file
was written: rows 16 and 19 are RESOLVED as pages (`ev-debt-issuance-line-v1` with `DEBT_SPREAD` and the
figure `$130–150B` / `2026E`; `ev-two-clocks-bars-v1`), with no PNG fallback; the outro clip and the
brand-line mp3 are now on disk in this worktree (gitignored media, copied 2026-09-22 21:01), so row 24 no
longer waits on a copy; and the stale `HOST_CARD_REFUSED` note is replaced by `HOST_CARD_DOOR` (R26-221
`plate_dock_place` places a card on a picture plate). The bed is unchanged by T14: the private-dir timeline
and table are byte-identical before and after (the parent's evidence).


Scope: every row 7-24 item that the treatment (`REBUILD-TREATMENT-H.md` rows 7-24) or the plan (T15-T32) wanted drawn
as a page or a datum on a page, and that is not. The source for each item is `P69-T14-INVENTORY.md` (explorer),
re-checked on disk. Tiers: CONFIRMED (a primary source on disk), PLAUSIBLE (a secondary dossier only), UNSOURCED (only
the script says it), REJECTED (the sources conflict). A series takes the tier of its weakest figure.

`P` = `content/video_engine/projects/systems-and-blowups/steel-and-paper`. `OBJ` = `P/evidence/objects`.
Correction to the dispatch brief: `P/build-h/` is NOT gitignored. `git check-ignore -v` exits 1 for this file, and
five files under `build-h/` are tracked (`BUILD-NOTES-H.md`, `GATES-MOTION.md`, `SHOT-TABLE-H.py`, `SOUND-PLAN.json`,
`objects/ev-divergence-hook-v1.series.json`).

### 9.1 What the bars builder can and cannot draw (the range finding)

`ledger_page._story_block` (`content/video_engine/scripts/ledger_page.py:1153-1160`) carries one numeric value per bar
(`labels / values / value_strings / colors` + `AXES_KEYS`). `_validate_values` refuses a non-numeric value
(`validate(..., 'bars')` on `"value": "130-150"` -> `bars[2] value '130-150' is not numeric`). Extra `lo`/`hi` keys pass
`validate` and are then DROPPED by `build_spec` (the 2026E bar compiles as `140.0`, a midpoint). The painter
(`docs/content-video-engine/samples/scene-evidence-engine.mjs:8862-8990`, `buildLedgerBars`; the rules at `:8982`) draws each bar from zero to
its one value. It has no range bar, whisker or band. Its only horizontal device is `axes.hlines`: a full-width labelled
rule, the comparator rule (E53 s6). (The `span` band at `:729-945` is an x-period shade on line pages, not a y-range.)

So:
- **A range that is a REFERENCE** (a norm every bar is read against) can be drawn honestly as two rules bounding it,
  never as a midpoint. `ev-index-concentration-bars-v1` does this for the historical 2-4%.
- **A range that is a DATUM** (one bar's own value, such as 2026E $130-150B) cannot be drawn by this builder. Rules
  across the whole plot would read as a reference for 2020-24 and 2025 too.

### 9.2 Authored objects (new ids, nothing existing edited)

| row | id | tier | validator (door path, 16:9, bars) | note |
|---|---|---|---|---|
| 14 | `ev-rail-vs-yardstick-bars-v1` | PLAUSIBLE | OK story, full_stage | 50 is dossier-only; 28 is CONFIRMED (FRED reading). Breakthrough: `domain [0,30]`, `overflow: burst` |
| 17 | `ev-capex-ocf-94-bars-v1` | PLAUSIBLE | OK story, full_stage | PIMCO's forward two-year claim only (see row 17 below) |
| 18 | `ev-index-concentration-bars-v1` | PLAUSIBLE | OK story, full_stage | the 20 bar; 2-4% drawn as two `hlines` (2 and 4), no midpoint |
| 21 | `ev-hbm-wafer-ratio-bars-v1` | PLAUSIBLE | OK story, full_stage | 1x vs about 3x |
| 23 | `ev-weight-check-bars-v1` | PLAUSIBLE | OK story, full_stage | 24.3 is CONFIRMED (iShares IWV file on disk, hashed); the 20 is Bravos-attributed |

The quotes and paths behind each figure are in each object's `proof` / `src_full` / `provenance_note`.

### 9.3 Departures

| row | item | reason | tier | falls back to |
|---|---|---|---|---|
| 9 | 7% tick / 8% datum on `ev-equip-ipp-gdp-v1` | not on the object; the series is equipment + IP as a share of GDP (11.54% Q2 2000 peak). The 7/8 are Bravos' figures for a different measure (`docs/content-video-engine/briefs/ANSWER-BRAVOS-HYPE-CYCLE.md:527`, "Internet 4%→7% GDP; ... AI ≈ 8% GDP \| Bravos video") | PLAUSIBLE (and a different series) | **cut** (the page rings its own 11.54% datum, T17). Already a named departure |
| 11 | `ev-uber-adoption-v1` burndown | PNG only, no series | PLAUSIBLE (`evidence/EVIDENCE-DOSSIER.md:169-170`, "rising from **32% to 84%**", The Information, not on disk) | **PNG card** (`OBJ/ev-uber-adoption-v1.png`) |
| 11 | the COO line as a record | `ev-doc-macdonald` has no record payload (CAPABILITIES:19) | PLAUSIBLE (`EVIDENCE-DOSSIER.md:172-175`, The Verge, not on disk) | **PNG card** (`OBJ/ev-doc-macdonald.png`); the caption strip carries the words |
| 12 | `ev-three-manias` peak and trough markers | PNG only: a 4x3 comparison table, not a hype-cycle chart. "peak to trough" is cell text only | PLAUSIBLE (its -64% is `EVIDENCE-DOSSIER.md:86-91`, Campbell & Turner via the dossier) | **PNG card**; the peak-to-trough move is a callout on the card's own cell (T20) |
| 15 | BoE 6% ring, Fed 6.5% ring, Bravos 5.5% tripwire on `ev-tnx-two-eras-v3` | no BoE or Fed-funds series on the page (it is the 10-year yield). A funds-rate datum on a 10-year page mixes two units (E53) | PLAUSIBLE (Bravos-attributed, `ANSWER-BRAVOS-HYPE-CYCLE.md:526-528`) | **badge** (the attributed figures as text, no ring) |
| 16 | `ev-debt-issuance:bars` 28 -> 121 -> 2026E $130-150B | **RESOLVED 2026-09-22, no longer a departure.** Drawn as the dense-line page `ev-debt-issuance-line-v1` (`OBJ/ev-debt-issuance-line-v1.series.json`; `ledger_page.py --check --variant line` -> `OK ... dense-line line 3 values`). Three series: `issuance` (2020-24 flat at the $28B AVERAGE, then 2025 $121B), `$150B` and `$130B` (both leave 2025 $121B for 2026E). The 2025 -> 2026E stretch is a `spread` wedge between the two estimate series, `{kind:"spread", from:1, to:2}` (engine `docs/content-video-engine/samples/scene-evidence-engine.mjs:11485-11501`), with a `figure` reading "$130–150B", sub "2026E". Nothing is drawn at a midpoint; the old PNG (`vals = [28, 121, 140]`, `P/evidence/build_railway_documents.py:153`) stays NOT a fallback | PLAUSIBLE (`EVIDENCE-DOSSIER.md:129-131`, `:137`; quotes in the object's `proof`). Still not Bravos' "$150B '24–25, $244B '26 YTD" (`ANSWER-BRAVOS-HYPE-CYCLE.md:528`); never on the same page or badge | **page**: `ev-debt-issuance-line-v1` + spread + figure (draws once the operator says yes to a PLAUSIBLE page, as H1-H5) |
| 17 | the other 94: `ev-capex-funding-v1` mark "94 cents of every dollar, operating cash consumed, Q1 '26" | a DIFFERENT claim from the script's: a realised single quarter (Epoch AI from company filings, 148.4 / 157.9 = 94.0%) vs PIMCO's two-year projection (`EVIDENCE-DOSSIER.md:117-118`). The script (`SCRIPT-H-VO.txt:37`) makes the PIMCO claim, so only that is authored (`ev-capex-ocf-94-bars-v1`) | the Epoch object is its own series (not re-tiered here) | stays on its own dense-line page as it is. It is **not** the row's 94 bar. **cut** from row 17's bar beat |
| 17 | the PIMCO record ("`ev-doc-macdonald`" in the treatment) | mis-named: `ev-doc-macdonald` is the Uber COO quote. No PIMCO record object exists, and the PIMCO paper is not on disk | PLAUSIBLE | **badge** ("PIMCO, Figure 3"); the new page's source line already names PIMCO |
| 18, 22, 23 | the certificate card's "-66%" figure, ringed | the crop carries no figure. The -66 is the treatment's; the railway object's arithmetic is -64 | PLAUSIBLE (Campbell & Turner via `EVIDENCE-DOSSIER.md:86-91`; the object `OBJ/ev-railway-index-v1.series.json` marks 2,062 and 741) | **badge** at `RAIL_DROP` (see the note below) |
| 19 | breakthrough bars `20 years` vs `5 years` | **RESOLVED 2026-09-22, no longer a departure.** The 20 is SUPPORTED by the Gemini research lane (`content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/RAILWAY-LAG-20Y-FINDINGS.md`: Campbell 2012 EEH p. 238, "During the subsequent two decades the rises in dividends were modest and rates barely returned to their pre-Mania levels"; Odlyzko 2010 p. 181, 26 years to 1872); the 5 is the operator's word. Drawn as `ev-two-clocks-bars-v1` (`ledger_page.py --check --variant bars` -> `OK ... story bars 2 values`). SCRIPT NOTE for the next letter (never patched): the 1840s track was wrought iron, not steel (FINDINGS row 7) | PLAUSIBLE (academic quotes with DOI, papers not on disk); 5 years: operator | **page**: `ev-two-clocks-bars-v1`; the `sold out` pill stays |
| 20 | the phone card | no phone icon among `assets/icons/*.svg` (5) or the 44 `icons/cutouts/prop-*`, and no phone prop | n/a (an asset, not a figure) | **cut** until an asset is generated (human decision H6) |
| 22 | `chart_to ev-tripwire-board-v1` | a `checklist` object: `validate` refuses it as a page ("keep it a dock") | its own | **PNG card** / the checklist dock it already compiles to (`OBJ/ev-tripwire-board-v1.png`) |
| 22 | "+17%" / "+14%" end figures on `ev-memory-monitor-v1` | not on the object; the script's basis is not stated (`SCRIPT-H-VO.txt:47`, "DRAM up seventeen percent, and the stacked memory ... up fourteen. That's the July release"). The object's own last month (the July release) reproduces neither cleanly: DRAM 74,686 -> 86,970 = +16.4%, HBM-CLASS 94,138 -> 95,408 = +1.3% | **UNSOURCED** on disk (the +14 may be a script/source conflict on a basis we do not hold; the parent should check before any figure is drawn) | **cut**; the page's end labels ($87.0k / $95.4k) carry the level |
| 22 | the June datum ringed on `ev-june-print-v1` | that page's `marks` is empty; the June customs datum lives on `ev-memory-monitor-v1` ("Jun '26 print: -3.7%") | as its object | re-target, not a figure departure: ring the monitor's own June mark |
| 23 | `ev-memory-arithmetic-v1:bars` ("a fab: 5 years; a chip generation: 2×") | the fab's duration is now **5 years on the operator's word** (2026-09-22, "5 years is the fab build out"; the script, `SCRIPT-H-VO.txt:49`: "A memory fab takes five years to build"), so reason (2) is closed; the record's "4-5 years" (`OBJ/ev-memory-arithmetic-v1.series.json:1`) is not the figure drawn. Two blockers remain. (1) Two units on one bars page, years and a multiple (E53: one unit before two). (2) The script's "doubles" vs the record's 80GB -> 192GB (2.4×) | 5 years: operator's word; the 80 -> 192GB is PLAUSIBLE (our src line only) | **PNG card** (`OBJ/ev-memory-arithmetic-v1.png`) or the checklist dock it already is, until the two-unit page and "doubles" vs 80 -> 192 GB are settled. A one-unit option for the parent: a bars page of H100 80 GB vs B200 192 GB (PLAUSIBLE, not authored) |

### 9.4 Note: the certificate figure, a badge at `RAIL_DROP` (rows 18, 22, 23)

Not an object. The certificate crop (`CERT_PLATE` + `CERT_CROP`, `P/build_episode_h.py:241-254`) carries no printed
figure, so the ring (E56: a number on a card) needs one. That figure is a **badge** whose text is `RAIL_DROP`,
`P/build_episode_h.py:222`:
`RAIL_DROP = "−%d%%" % abs(round(100 * (RAIL["marks"][1]["y"] / RAIL["marks"][0]["y"] - 1)))`, which gives **"−64%"**
(741 / 2,062 - 1 = -0.6406). The marks are `OBJ/ev-railway-index-v1.series.json` (`{"y": 2062, "sub": "6 Oct 1845"}`,
`{"y": 741, "sub": "Apr 1850"}`), and the source is `EVIDENCE-DOSSIER.md:89-91`: "peak **2,062 on 6 October 1845** ...
trough **741 in April 1850**. That is a **64.1% peak-to-trough decline**". Never the treatment's "−66%". The script's
"the paper still lost two-thirds" (`SCRIPT-H-VO.txt:39`) is the dossier's allowed wording ("nearly two-thirds",
`:93-94`). The badge must read the constant, not a typed string, so the certificate and the railway page cannot
disagree.

### 9.5 Human decisions (only the two kinds asked for)

**May a PLAUSIBLE series draw as a page?** Each of these compiles. None draws until the operator says yes:
- H1, row 14: `ev-rail-vs-yardstick-bars-v1`. The railway ~50% is dossier-only (Campbell & Turner via Focus-Economics).
  If no, the row cuts the bars; `ev-capital-formation-v1` already carries the 50% as an amber rule.
- H2, row 17: `ev-capex-ocf-94-bars-v1`. PIMCO Figure 3 is dossier-only.
- H3, row 18: `ev-index-concentration-bars-v1`. Bravos-attributed; no transcript on disk. The operator's 2026-08-24
  ruling (`ANSWER-BRAVOS-HYPE-CYCLE.md:534-536`) accepts Bravos as a primary source for this format, which may settle
  this one. The same answer settles the 20 in H5.
- H4, row 21: `ev-hbm-wafer-ratio-bars-v1`. Two dossiers agree on ~3:1; no disclosure on disk.
- H5, row 23: `ev-weight-check-bars-v1`. The 24.3 is CONFIRMED; the 20 is Bravos (H3).

**A missing asset that needs generation:**
- H6, row 20: the phone card. There is no phone icon, cutout or prop.
- H7, row 23: host still H-3 (`P/host/H-3-newsroom.png`). It prints legible certificate text. HOST-NOTES-H.md (the
  H-3 row) says "RE-ROLL before HG4", a new order id.

### 9.6 Not departures, listed so they are not re-asked

- Rows 7, 20, 23 host stills H-1/H-2/H-3 resolve; they are quarantined until the operator approves (E10).
- Row 11 `ev-doc-karp`, row 16 `ev-doc-leases`, row 20/21 `ev-test-scorecard-v1`: records and a checklist dock by design.
- Row 16 `ev-ig-credit-weighting-v1`, row 21 `ev-dram-contract-v1`: the treatment says `:line`; both are bars (story) pages.
- Row 24 outro clip and brand-line audio: present in the main checkout only
  (`content/video_engine/channel-assets/money-physics/outro/`). They are a copy for the parent, not a generation.

---

## 10. P69 T15 - body row 7 (0:54-1:09): host window 1, the studio (2026-09-22)

The build now runs 0.00-63.77 s (168 of 2335 words). `UNIT_CUT_PHRASE` moved past row 7 to "But capital that fast"
(row 8's first words; T16 owns that dip). Treatment row 7 compiles as TABLE row 3 (`s03`, 52.92-63.77).

| what | anchor (take words) | how |
|---|---|---|
| the world: `world-h1-studio-v1;use=landing` + ken `(0.05, -12, 6)` | the cut before "The three questions read" (52.92) | E99 s84: the ken push ALONE, no `;idle=drift` (R26-236) |
| the dip INTO the studio | 52.92 | plate -> plate: the thread, the edge arrival, the occluder and the melt refused by name (`HOST_DIP_WHY`, printed in `SHOT-TABLE-H.md`) |
| their chart (`dock-h-two-line-copy`) THROWN | "Bravos Research" 55.62 | `arrive: throw, mass: paper`; reads over the dark LEFT monitor (`BRAVOS_READ`), put down on the desk's left third on "and it isn't Nvidia" (58.26, `park_s` 0.6), leaves at 61.57 (`CARD_LIFE_S` 5.95: E50's 6 s floor and M12's 6 s opening-minute ceiling meet) |
| the NVIDIA chip (the SVG chip, NO `form: stamp` - HG1's) | "Nvidia" 58.60, crossed at 59.80 | on the RIGHT monitor (0.86, 0.17); `idle: breath` (E49). The first build's point (0.47, 0.59) was Mike's forearm, read on the plate |
| the flow `CAPITAL -> VALUE` | "capital arriving faster" 59.86 | `FLOW_BOX`, the dark left monitor, to the row's end |

**Measured and fixed in the row:** M25 on the first build found the parked card 40 px into the anchored caption strip
(y 918 vs the strip's 878). At 0.28 wide centred at y 0.655 it is `plate-box [144, 556, 538, 303]`: y 556-858, 20 px clear.

**Fixed in the door:** the `dip N` cue sat at `r[1] - 0.35`, the row's END. A row's exit is the door INTO it
(`transitions.mjs` `dipIn`, `build_scene_timeline_f.py:2660`), so it now sits at `r[0] - 0.35`: `dip 3` at 52.57.

**Life:** 3 of 3 rows (row 1 `idle=live`; row 2 `ken 0.04/10/-6`; row 3 `ken 0.05/-12/6`). Between the tiles at 53.40 and
55.40 s, on the caption-free region x 1300-1920, y 560-1080, the mean absolute luma difference is 6.96, with a -2 px
shift by phase correlation: the push, visible. M18: no run of identical frames over 0.5 s (766 frames at 12 fps).

**The order of proof (logs in `logs/`):** `t15-door.log` (door rc 0, cues 5 of 5 bound), `t15-frozen-final.log`,
`t15-probe-final.log` (22 instants), `t15-seams.log` (the dip clean: 0 faults), `t15-stagegaps.log` (0.5 s empty, licensed),
`t15-spoken.log`, `t15-gate-final2.log`: **RESULT: 2 FAIL / 2 WARN / 21 PASS / 1 JUDGE / 7 INFO.**

**The FAILs, named:**
- **M03** "longest wait for evidence to enter: 46s from 0:09". The gate counts a dock or a page START as evidence entering
  (`gate_motion_density.py:1325`). The bed had 43.6 s from the certificate (9.20) to its end. Row 7's first evidence
  is their chart, and it arrives on its own name at 55.62. To clear 45 s, a card would have to land by 54.20, on "The three
  questions read for one thing", before anything is named (E99 s71). Row 7 cannot fix this. Two fixes are open: the gate
  credits a page's staged reveal (row 4's memory line at 28.23 is new evidence on the same page), or rows 1-6 enter evidence
  between 0:09 and 0:54. Both are outside T15's write set.
- **M11** pre-exists (row 1's hook annotation; the baseline carried it before T15).

**WARNs:** M04 (3 plates vs a target of 5, a long-form density target). M25 is the certificate card at 0:09-0:10 in the
bottom safe-zone band. That is row 1's, first surfaced by the fresh probe, not by row 7.

**Found, not fixable in this write set (for the parent's read):**
1. On a picture plate, a live dock ALWAYS sends the caption to the anchored strip. `stamp_caption_bands` stamps a plain
   plate's dock `null`, so from 55.62 to 61.57 the words sit small at y 878-960, over the desk's printed chart and Mike's hand
   (tile 57.60). The engine has no caption band on a picture plate.
2. The STAGE caption on this plate is stage-centred. On the row's last page ("the value it's chasing.", tile 63.40) it
   runs x 630-1290 at y 450-500, across Mike's collar and lapel. A picture plate has no caption room (`PLATE_OPTS` `room=` places cards only).
3. The door's `## Recall` still quotes s65 ("the 20 px drift") at `:55` and `:61`. s84 supersedes both, and
   `TREATMENT_SUPERSEDED` says so. The quotes are left as cited text for `recall_verify`.

**Tiles for the parent** (the scratchpad `p69t15/`): `tile-<t>.png` at 53.40 / 55.40 (the life pair, the host plate), 56.20
(the throw landed), 57.60 (the read), 58.90 (the put-down), 59.30 (the chip landed), 60.40 (the chip crossed, the flow drawing),
61.60 (the flow, the card leaving), 63.40 (the flow whole). `ref-<t>.png` is build-f's mp4 (sha256 `9a27de1c...` verified
against REFERENCE-F.md) at the SAME SENTENCE on Script G's clock (`ref-map.txt`: 83.40-91.93 s). There, the bare nib plate
runs through "isn't Bravos ... isn't Nvidia", then the hype machine and the hype-cycle card.

---

## 11. P69 T15b (row 7 corrected), T16 (row 8) and T17 (row 9) - 2026-09-23

The build now runs 0.00-89.27 s (228 of 2335 words); `UNIT_CUT_PHRASE` = "So the obvious move" (row 10, T18's).

### 11.1 Row 7 corrected (T15b): the card BECOMES the chart

The operator on T15's tiles: "Those charts still seem tough to read to me." T15 read their chart at a third of the
frame and parked it on the desk - E99 s71's fault ("a thrown full-screen card ... throw-then-zoom or throw-then-push to
make it full screen"). Now:

| table row | window | what |
|---|---|---|
| 3 `world-h1-studio-v1` | 49.45-56.62 | the host window opens on the promise ("By the end you'll run it on your own top five", `HOST_FROM_PHRASE`) so the studio holds its six seconds (M44: a plate under 6 s with a dock FAILs; from "The three questions read" to the push is 3.7 s). Their chart card thrown on "Bravos Research" (55.62) onto the dark left monitor, `arrive: throw, mass: paper` |
| 4 `ev-divergence-v1 ... camera=dock-h-two-line-copy;card=no;domain=80,277` | 56.62-63.80 | THROW-THEN-PUSH: one second after the throw the camera pushes the card to the stage and the page shows at the match; memory held at nothing (the card's three lines), the hand writes the card's title; the NVIDIA chip lands on "Nvidia" in the page's empty upper right and is crossed at 59.80; the flow `capital -> value` draws beside it on "capital arriving faster". The chart is read FULL SIZE throughout - no park |

- **The slate shortens** to 42.04-49.45 (7.4 s; the agenda's three rows land by 45.62). This moves the BED's row 6 end - the parent's call.
- **Why not the snap** (`snap=`, throw-then-zoom, the proven recipe): measured (`scratchpad/p69t15b/seq-play`), a 16:9 full-stage page grown by the snap lands OFFSET (+137, +100 px, cream showing top-left) and stays there for the row in forward frame-by-frame play (every frame from 57.38 s), while a cold seek paints it at identity. An engine seek-purity defect in the snap (`paintLedger` `snapBoard`, `scene-evidence-engine.mjs:13286`) - owner: the engine lane. `camera=` settles at identity both ways (`seq-cam`).
- Chip and flow boxes measured on drafts: at (0.80, 0.60) the chip sat on "+21% S&P 500"; at (0.84, 0.25) its label fell on "+105% SEMICONDUCTOR STOCKS"; a 0.64 park made room for the flow but printed the chart's labels at 8.3-9.1 phone px (probe M25 INFO), so there is no park.
- Life: 50.50 vs 52.50 (studio, x 1300-1920 y 560-1080) mean |dL| 9.36, 24.2 % of px changed; 59.20 vs 61.20 (the page's chart only, x 0-1100 y 150-850) 5.15 / 5.7 %.
- Open: the page's SUB still reads the object's own "Their pairing, plus the S&P 500 and the memory builders" while memory is held (the card's sub reads "Mega-cap tech against the chip industry"); no row option rewrites a sub.

### 11.2 Row 8 (T16): the rehook - no dip, a melt

Row 7 now ENDS ON A PAGE, so the treatment's "dip 1" (studio -> page) no longer exists: E47 refuses a dip between two
pages. The boundary at 63.80 ("But capital that fast") is `melt:throw:1` (E88): their pairing's ink balls up and is
thrown, and the railway index draws on the same board on its axes (`RAIL_MELT_WHY`: the dip, recast, rescale/extend,
morph, melt:splash:chart and melt:morph refused by name). The index climbs from the page's entry (first cap 1843.7), and
one pen carries it from "paper trail" to the half-way cap (1844.35) as row 9 begins - no stop-and-go crawl.
Life: 66.40 vs 68.40 (x 0-1100 y 150-850) mean |dL| 2.99, 4.0 %. The first T16 cut (the dip from the studio, before T15b)
is kept in `scratchpad/p69t16/door-at-t16.py` history comments only.

### 11.3 Row 9 (T17): the peak, the crash, the recast, the ring

Same table row (5), same page, `;then=ev-equip-ipp-gdp-v1:line`:
the stroke carries on to the 6 Oct 1845 peak landing on "pounds" (75.20); the crash draws on "crashed" (77.46, 1.2 s);
`-64%` (`RAIL_DROP`, the object's arithmetic) written red over the trough and UNDER the 1,000 rule on "nearly two-thirds"
(E28; at dy +1.1 it had landed on the x axis' "1850"); on "the internet" (80.49) the plain recast (no key - E64's
hand-over) to the share-of-GDP line; the hand writes the object's own title 0.1 s after it (a retitle ON the recast's
word is dropped by R26-219 (c), and without one the railway title stood over the GDP line); the GDP line lands at the
railway's cap index (Q4 2004 - the peak and the fall); the ring on its own Q2-2000 peak on "then the tower came down"
(83.35, no label - the rule already writes "Q2 2000 peak - 11.54%"); its last twenty years draw on "AI spending just
crossed" (86.49), back to the peak, ending at its own "11.51%" on "eight.".
Life: 69.50 vs 71.50 mean |dL| 3.59, 4.5 %; 84.20 vs 86.60 3.54, 5.4 %.

**Departures and flags (row 9):**
- `RAIL_NOTE` ("£250m raised - over $1T in today's money") is NOT drawn: no source on disk (only the treatment and the door carry it; `EVIDENCE-DOSSIER.md` has no railway capital figure). Added to `BODY_DEPARTURES`.
- The 7 % tick and 8 % datum are cut (the standing departure). FLAG: the GDP line's own end tag "11.51%" lands on "eight." - the page's measure beside the voice's figure; the parent / HG rules.
- The GDP object carries no `xticks` and no `ylabel`: the recast page shows no years on its x axis and bare 8-11 on y (E28's "a selected axis states its rule"). The object is read-only here - owner: the evidence object.
- The railway page's title ("fell 64% from their peak") states the drop from 63.8 s, before the voice says it at 77.5 s.
- build-f at the same sentence carries `ev-railway-gdp-tile-v1` ("Where Britain's money went, 1844-47": railways ~7 % of British GDP) - an object on disk that fits "seven percent" for the RAILWAYS, not the internet; noted for the parent.

### 11.4 The order of proof (logs in `logs/`)

T15b + T16 (unit 0-68.60): `t16-door.log` (rc 0, cues 7 of 7 bound), `t16-frozen.log`, `t16-probe.log` (28 instants),
`t16-seams.log` (4 boundaries, 0 faults), `t16-stagegaps.log`, `t16-spoken.log`, `t16-gate.log`: **3 FAIL / 1 WARN / 21 PASS**.
T17 (unit 0-89.27): `t17-door.log` (rc 0, cues 7 of 7), `t17-frozen.log` (no run over 0.5 s, 1072 frames), `t17-probe.log`
(40 instants), `t17-seams.log` (0 faults), `t17-stagegaps.log` (0.5 s, the licensed dip only), `t17-spoken.log`,
`t17-gate.log`: **2 FAIL / 2 WARN / 22 PASS / 1 JUDGE / 6 INFO**.

FAILs named: **M03** (46 s from 0:09 - the bed's gap before row 7's card, pre-existing, P69-HG4) and **M11** (row 1, pre-existing).
**M31** FAILed on the T16 build (0.2 s "empty" at the melt, 63.80) and PASSes on the T17 build with the identical melt
(0.0 s) - the melt's throw holds the next chart until the board is clear (`meltDrawDelay`), so this sits on the
measure's own edge; owner if it returns: the gate (a ball in flight is not an empty stage) or the engine.
WARNs: M04 (5 plates vs 7), M25 (row 1's certificate at 0:09-0:10, pre-existing).

---

## 12. P69 T18 (row 10) and T19 (row 11) - 2026-09-23

### 12.1 Row 10 (T18): the sell ticket thrown over the recast

The build ran 0.00-102.70 s at T18 (263 of 2335 words). `UNIT_CUT_PHRASE` was "But walk Bravos'" (row 11, T19's). Row 10
has no world change: the board is the same page (table row 5), which now has THREE states: the railway index, the share of GDP
and the divergence (`;then=ev-divergence-v1:line`, `DIV_RECAST`, STATE_MAX 3).

| what | anchor (take words) | how |
|---|---|---|
| the ticket `dock-h-sell-ticket`, THROWN | "obvious move" 89.61 | `arrive: throw, mass: paper`. The card is the order form's FACE cut from `world-sell-ticket-v1` (`SELL_CROP` 250x226 at plate (712, 562), inside the form's four edges). The plate's rubber stamp stands at plate x 985+, so a whole-form crop would carry a prop onto a card (E99 s92) |
| its badge `ORDER / SELL / the steel` | springs at 91.66 (the compiler's badge clock, enter + 2.05), on "sell" 91.72 | the crop carries no word. SELL is the sentence's verb. No numeral, so no document owes one |
| the READ, then the PARK | read in the GDP page's right room (`TICKET_READ` 0.30 wide at (0.815, 0.47), box [1277, 247, 576, 521]) to 92.64, then parked over 0.7 s into `TICKET_ROOM` [1382, 107, 384, 347] | a read centred on the stage was DEFERRED by E63 ("a card never reads over the plot", draft 3). SELL reads at ~26 px at the reading size and ~20 px parked (0.15 wide: 9 px, draft 4) |
| the GDP line unwinds | 92.44-93.24 ("before the paper catches up") | `undraw` series 0 to nothing, so the divergence's MEMORY line arrives held (see below) |
| the RECAST to the divergence | "catches up with it" 93.34, 1.2 s | the plain hand-over (E64), UNDER the parked ticket. Retitled 0.1 s after to the sentence's own "Chipmakers doubling. Customers flat." |
| the lines, one at a time (`build=lines`) | the chips on "Chipmakers doubling" (94.5-95.7); mega-cap and the S&P on "their customers sit flat at the index" (95.7-98.1) | each whole, with its end tag (+105% / +21% / +21%). The chart is read at the full page (tile 98.40: labels 32 px) |

**Measured and fixed across five drafts (`scratchpad/p69t18/draft1..5`, `onset/`, `spread/`):**
- A `build_to` to datum 0 cannot hold a line whose cap is already further on. Series 0's cap is the GDP line's last datum, so draft 1 drew memory whole, with "+613% MEMORY" under the ticket. An `undraw` that starts WITH the recast still let memory draw to the GDP cap for half a second (`onset` 93.40; probe M25 `chart.sname` at 93.34-93.44). The undraw now lands 0.1 s before the recast (`MEMORY_HOLD_GAP_S`).
- A recast on "Chipmakers" itself (2.0 s) drew nothing until "sit flat" was over (draft 4). The recast moved to "catches up with it" (1.2 s), and the GDP page's deployed life is now 4.9 s. E50's 6-8 s is an average, and a floor only for a page that arrives built.
- The ticket at 0.15 carried a 9 px pill. It now reads at 0.30, then parks at 0.20. With memory held, the divergence's lines and tags sit at y 0.50-0.75, so the whole upper band is empty.

**Departures (in `BODY_DEPARTURES`, row 10):**
- The ticket "reads SELL over the chip line's tip": SELL is the card's badge.
- "any adviser would sign it", a signature stroke ON the ticket: CUT. No species draws on a still card (the callout's `phrase` target is a press card's alone, and a squiggle is a caption word's). The caption carries the words.
- The page on the hook's scale: NOT DRAWN. A recast carries no domain, and a `chart_to rescale` after it is refused by name ("4 chart states is past STATE_MAX (3)", `logs/t18-door2.log`). The page lands on the object's own log domain (sized for memory's 1,074), and the three lines fill the plot's lower ~40%. The other door (row 10 as its own page on `;domain=80,277`) would trade E64's recast under the card for a page-to-page transform across a live dock. That is the parent's call.
- The chips-vs-customers gap as a `spread`: CUT. It painted nothing (`spread/` 98.20-100.10). On a page with states, "a bracket or spread is built on the page's own geometry and waits while a derived state stands" (`scene-evidence-engine.mjs:11498-11501`), and state 0 (the railway) has one series. Owner: the engine.

**The transform inside the row** (`DIV_RECAST_WHY`, now printed in `SHOT-TABLE-H.md` under "Transforms inside a row"):
- TAKEN: the recast under a live card (E64).
- REFUSED:
  - the melt (it takes the ticket's board);
  - the dip and the cut (no world change, E47);
  - rescale / extend (another series);
  - morph (a strip of this frame);
  - remake (no shared data).

**Found, outside this write set:**
1. **Probe (M25 + M27 FAIL on the ticket): a card over ITS OWN badge pill.** `probe.py:226-233` pushes every `.dock .pill` as a solid and as ink. The pairing at `:700-709` then sets the card against its own pill (10,440 px = 100% of the pill, which sits inside the card). The code's own comment says "a card's pill belongs to the card". Owner: the probe. The only fix in this write set is to drop the badge, which takes away the word SELL.
2. **Engine transient at the second recast (93.5-93.9, `tile-93.60`).** The erasing sub and source are the RAILWAY page's ("... January 1843 = 1,000", "... index, 1843-1850"), not the GDP state's. The plain recast's outgoing text reads state 0's strings.
3. The divergence's SUB still reads the object's own "Their pairing, plus the S&P 500 and the memory builders" while memory is held (the open item of 11.1: no row option rewrites a sub).

**Life:** 98.40 vs 100.40 on the chart (x 0-1100, y 150-850), after every line has landed: mean |dL| 3.18, 5.5% of px changed (`idle=live`). Table rows 5 of 5 carry life.

**The order of proof (logs in `logs/`):**
- RED: `t18-red.log` (the table's row 5 ended at 89.27).
- `t18-door.log` (rc 0, cues 8 of 8 bound).
- `t18-probe.log` (48 instants).
- `t18-frozen.log` (no run over 0.5 s).
- `t18-seams.log` (4 boundaries, 0 faults).
- `t18-stagegaps.log` (0.5 s, the licensed dip only).
- `t18-spoken.log` (0 uncovered).
- `t18-gate.log`: **4 FAIL / 1 WARN / 21 PASS / 1 JUDGE / 6 INFO**.
  - FAILs: M03 (the bed's 46 s gap, pre-existing, HG4); M11 (row 1, pre-existing); M25 and M27 (the probe's self-pill defect above).
  - WARN: M04 (5 plates vs 8).
  - INFO: M21 s05 8.2 s (the divergence held to the unit's end; row 11's undraw closes it).
- Drafts: `t18-door1..5.log`. Table snapshot: `t18-SHOT-TABLE-H.md`.

**Tiles** (`scratchpad/p69t18/`):
- `tile-<t>.png` + `tiles-sheet.png` at 89.80, 90.40, 91.90, 92.90, 93.60, 95.40, 96.60, 98.40, 100.40, 102.40.
- `ref-<t>.png` + `ref-sheet.png` from build-f's mp4 (sha256 `9a27de1c...` verified, `ref-sha.txt`), mapped by sentence (`ref-map.txt`, 211.30-219.90 on Script G's clock). There the sell-ticket PLATE stands bare for 9 s with nothing arriving, then cuts to the trading desk.

### 12.2 Row 11 (T19): one slot, three records

The build now runs 0.00-127.80 s (334 of 2335 words). `UNIT_CUT_PHRASE` = "Remember that" (row 12, T20's). The take spells the
word "line—", so "Remember that line" is not a phrase in it. Row 11 is still table row 5 (the same board): no world change.

| what | anchor (take words) | how |
|---|---|---|
| the board re-titled | "own evidence" 103.65 | "Bravos' own evidence", the sentence's words |
| the divergence UNDRAWS | "claims adjuster" 104.56, 1.2 s | `undraw`, every series, to nothing. E50: the sentence has left the chart's argument, and the next thing is not a chart. The true clock from the last line's landing (~98.1) is 6.4 s. The gate's M21 reads 10.0 s from the recast's landing (INFO) |
| the ticket leaves; KARP is THROWN | "Alex Karp" 107.09 | a RECORD dock (`dock-h-karp-record`, live type, CAPABILITIES:19). It types from 107.49, and the highlighter lands word by word on the narrator's "paying for tokens that create no value" (109.35-111.75, `D.record_words`). Its words, header, kicker, attribution and source are the record's own (build-f's payload, `ev-doc-karp.png`) |
| UBER takes the slot | "Uber's CTO" 114.21 | `land` (`SLOT_HANDOFF_ARRIVE`). The PNG card `ev-uber-adoption-v1.png` is a CHART (32% -> 84% adoption), so it is read at 0.83 of the stage (1594 x 574; labels 26-40 px, `draft1/zoom.png`). Its badge springs on "April" (116.26): ANNUAL AI BUDGET / spent by April / 2026, words on the card (B3). build-f's "4 months" is the script's arithmetic and is not carried |
| the COO's line takes the slot | "And their COO" 120.65, to the row's end | `land`. The PNG card `ev-doc-macdonald.png` at 0.60, with its own highlighter on "that trade becomes harder to justify". The anchored caption strip carries the narrator's words under it |

**Measured and fixed (`scratchpad/p69t19/draft1`, probe):**
- The undraw takes the LINES, not the axes. On draft 1 (slot 0.92 wide, centred at y 0.472) each card sat on the board's axis labels: the unit label "index - 100 = ..." at y 205-238, the ticks at x 79-133 and the dates at y 837-873 (M25, 72-100% of each). The slot is now centred in the free box (x 140-1780, y 245-830).
- The COO card's frame adds ~31 px under its picture: at 0.655 it drew 603 px tall, and its foot sat on the dates (M25, 36-44%). It is 0.60 now; Karp's paper is its type's own height (~415 px) and keeps 0.655.
- After both fixes, no card touches any page label (`t19-probe.log`, 62 instants). The ticket's self-pill (12.1) is the only overlap left.

**Departures:**
- **The records' slot is NOT the ticket's corner** (the treatment says "lands in its slot"). The ticket's box is 384 px wide, and a record there types at ~8 px. The operator's T15 lesson outranks it: nothing of words or of a chart is read at card size. The three records share ONE box and centre (s80, the footprint narrowing where the aspects differ).
- **Uber is a PNG card** (no series on disk; `BODY_DEPARTURES` row 11), read near full width, not small.
- **The COO line is a PNG card** (no record payload), with the caption strip carrying the words.

**Transforms inside the row** (printed in `SHOT-TABLE-H.md`):
- `WALK_UNDRAW_WHY`:
  - TAKEN: the undraw (E50).
  - REFUSED: recast / remake (the next thing is a quote, and STATE_MAX is spent); melt / dip (no world change, E47); park (the undrawn plot IS the room, s80).
- `SLOT_WHY`:
  - TAKEN: the slot hand-off (E99 s80). Karp is thrown on his name (s71); Uber and the COO land.
  - REFUSED: a park of the page; a dip per quote (E47); three worlds (build-f's memo / burndown / racks, the G31 listing risk).

**Found, for the parent:**
1. The board keeps the divergence's axes (ticks, the unit label, the dates) under the records for 20 s. They peek around each card (`tile-115.30`). No species un-draws a page's AXES. The object's `sub` also still reads "Their pairing, plus the S&P 500 and the memory builders" under "Bravos' own evidence" (no row option rewrites a sub, 11.1). Owner: the engine; flagged for HG4.
2. E99 s98's blur under a dock over a busy chart plate is NOT built (no option in the compiler or the engine: `grep -i blur` finds the blurzoom exit and the caption stagger only). Here the chart is undrawn before the records land, so there is nothing busy under them.
3. M21 reads a `build=lines` page's last data mark at the recast's landing (94.54), not at the last line's (98.1).
4. A transient Playwright `NetworkError` failed one door run (`t19-door2.log`). The re-run was clean.

**Life:**
- COO hold: 122.40 vs 124.40 (x 0-1920, y 150-870), mean |dL| 9.17, 9.6% of px changed.
- Board strip: 121.60 vs 124.20 (y 0-240), 3.29, 4.6%.
- Table rows: 5 of 5 carry life (row 5 `idle=live`).

**The order of proof (logs in `logs/`):**
- `t19-door.log` (rc 0, cues 11 of 11 bound).
- `t19-probe.log` (62 instants).
- `t19-frozen.log` (no run over 0.5 s).
- `t19-seams.log` (4 boundaries, 0 faults).
- `t19-stagegaps.log` (0.5 s, the licensed dip only).
- `t19-spoken.log` (0 uncovered).
- `t19-gate.log`: **4 FAIL / 1 WARN / 21 PASS / 1 JUDGE / 6 INFO**.
  - FAILs: M03 and M11 (the bed's, pre-existing, HG4); M25 and M27 (the ticket's self-pill, the probe's defect, 12.1).
  - WARN: M04 (5 plates vs 10).
  - INFO: M21 s05 10.0 s (item 3 above).
  - M05, M10, M12 and M16 PASS (the longest gap between visual events is 1.5 s).
- Drafts: `t19-door1..3.log`. Table snapshot: `t19-SHOT-TABLE-H.md`.

**Tiles** (`scratchpad/p69t19/`):
- `tile-<t>.png` + `tiles-sheet.png` at 103.90, 105.30, 106.60, 107.90, 110.00, 112.40, 115.30, 117.80, 121.60, 124.20, 126.90.
- `ref-<t>.png` + `ref-sheet.png` from build-f's mp4 (sha256 verified, `ref-sha.txt`; `ref-map.txt` 222.30-248.20). There, Karp's record stands on two plates (the memo desk, the whiteboard office), and the Uber card is held across the racks and the exhibition hall. The COO's line is never shown as a document.

### 12.3 The parent's fixes to rows 10-11 (T18b, T19b) - 2026-09-23

**SUPERSEDES** in 12.1: the ORDER / SELL badge, and the M25 / M27 self-pill FAILs (the badge is gone). **SUPERSEDES** in 12.2:
the undraw, the "Bravos' own evidence" retitle, "no world change", and the slot fitted between the undrawn axes.

**FIX 1: SELL reads big (row 10).** The parent: "The whole point of the beat is the word SELL ... SELL at least ~72 px ... The SELL
must be the largest thing on the card while it's read."
- The card is now the form's face with SELL STAMPED across its centre: a rubber-stamp impression with a ruled border, a -7 degree tilt and the ink's grain.
- The ink is the brand's negative, `brand-tokens.json` coral #ED6A4A ("negative / alarm"). The accent sunflower vanishes on cream paper.
- The door composes it at build (`_sell_ticket_card`, 4x the crop, the repo's Inter at Black, a fixed grain seed).
- The word spans 0.66 of the card. Its cap height is ~140 px at the 0.30 read and ~95 px parked at 0.20 (`p69t18b/tile-91.90`, `tile-98.40`).
- The badge is gone, and with it the probe's self-pill M25 / M27 FAILs.
- Not built: SELL landing ON the ticket as its own stamp on the word "sell". A second dock cannot ride the first dock's read-then-park (no door), so the word is on the card from its throw on "the obvious move". The move IS the sell.

**FIX 2: a clean ground for the records (row 11). Taken: (b), a world change, made by a TRANSFORM (the melt), not a dip.**
- **Why (a) was not taken:** it has NO DOOR.
  - `undraw` takes a page's LINES and never its axes (T19 draft 3).
  - No species dims or retracts a page's furniture (SPECIES_KINDS).
  - The dock `#wash` is a fixed 0.18-0.34 gradient scrim (`scene-evidence-player.template.html:250-262`) that no row can deepen.
  - Engine gap for the parent to file: "a page recedes to its ground under a card" (an undraw of the axes, or a row-level wash depth).
- **What was done:** the divergence MELTS on "like a claims adjuster" (104.31, `melt:splash:plate:1`, E88; row 2's own ending) and splashes onto `world-internal-memo-v1` (a lamp, a desk, one memo: a plain document plate). There Karp, Uber and the COO take one slot in turn (table row 6).
- **Refused, by name** (`MEMO_MELT_WHY`, printed in `SHOT-TABLE-H.md`):
  - the page receding (no door);
  - the dip (the melt IS this pair's transform, s74);
  - the thread;
  - recast / remake (STATE_MAX spent, and the next thing is a quote);
  - a park (the "broken chart").
- The ticket leaves with its page at the melt.
- **New FAILs from the move to a plate** (draft 1: M05 and M16, gaps of 6.7 s, 4.4 s and 6.8 s). On a picture plate a record's typing and a PNG card's hold earn no event, and the anchored caption is not credited. Fixed with LIFE, not by removing motion:
  - the desk's own MUG breathes steam (E49; s38 "plate life = the ambient lane"), its rim measured at x 0.72-0.83, y 0.35-0.40 (`p69t19b/mug-grid.png`);
  - so the two documents stand in the slot's left 0.64, leaving the mug visible;
  - the Uber CHART keeps the full 0.90 width (a chart is never small), and its window's life is three badges, each a phrase printed on the card: spent by April / 2026, 32% -> 84% / Uber engineering, $500-$2,000 / per month;
  - the steam runs ONLY in windows where it is seen.
- Result: M05 and M16 PASS (longest gap 2.4 s).

**FIX 3: row 10's scale. LEFT, NAMED.** `;domain=` sets the scale of the state a page is BORN on (row 7's `domain=80,277`). The
divergence is the rail page's THIRD state, and a rescale after its recast is refused by name (4 states > STATE_MAX 3). Two other paths
exist, and neither is cheap:
- a page of its own for row 10 would trade the recast under the card (E64) for a page-to-page transform across a live dock;
- a per-state domain on `;then=` needs an engine door.

The recast's half-title flash at 93.6 s is R26-261 (known, left).

Checkpoint gate after the fixes (`t19b-gate.log`): **2 FAIL / 2 WARN / 22 PASS**. The FAILs are the bed's M03 and M11. Seams: 5 boundaries, 0 faults. The rest of the chain is in `t19b-*.log`.

Life: the mug region at 107.90 vs 110.00 reads mean |dL| 6.63 (10.1%).

Tiles:
- `scratchpad/p69t18b/` (`tiles-sheet.png` + the build-f `ref-sheet.png`);
- `scratchpad/p69t19b/` (`tiles-sheet.1.png`, `tiles-sheet.2.png` + `ref-sheet.png`).

### 12.4 Row 12 (T20) and row 13 (T21) - 2026-09-23

The build now runs 0.00-162.50 s (429 of 2335 words). `UNIT_CUT_PHRASE` = "So I built" (row 14, T22's). RED: `t20-red.log`
(the table ended at 127.80). Rows 12 and 13 were authored together and validated in one build (`t21-*` logs).

| table row | window | what |
|---|---|---|
| 6 `world-internal-memo-v1` (rows 11-12) | 104.31-147.82 | row 12: the COO's card (the "that line") holds through "Remember that line - he's reaching for the third question ... without having it" to 133.00; on "And that isn't the peak" the THREE-MANIAS table takes the slot (`land`, s80) at ~0.76 of the stage; its four badges spring 135.05 / 136.35 / 137.65 / 138.95: THE MARKET PRICED / returns inside three years; THE PAPER / fell 64% / peak to trough (on "trough", 136.29); THE RETURNS / took twenty years; 2024-26 AI BUILD / still open. The table leaves on "Which flips the question" (141.38, an 8.4 s read) and the desk, its steam and the caption in STAGE mode carry "not when the disappointment arrives ... but what survives it" |
| 7 `world-viaduct-train-rain-v1;use=reset` | 147.82-162.50 | RESET 1: **dip 2** on the cut before "And in 1849" (E47, a world change); Ken Burns alone (0.05 push, E99 s84) and the locomotive's STACK breathing steam (the mouth measured at x 0.397-0.424, y 0.150-0.165 across the push, `p69t21/stack-*.png`); the anaphora "The steel kept working. The paper stopped pretending." in caption STAGE mode (no dock on the row) |

**The three-manias card (T20):** the object is a PNG TABLE only (a card, as T14 named it).
- Whole, it would be capped at 626 px tall, with its cells at ~16 px (7 phone css). That is a table read small (E99 s71).
- It is COMPOSED from its own pixel bands (`_manias_card`, nothing redrawn): the title, the column heads and their rule, the three rows the sentence reads, and the source line.
- CUT: the subtitle and the "Capital committed" row. That row's ~7% / ~8% of GDP are the measures row 9 keeps off screen, and a row the sentence does not read is height the cells cannot spare.
- It reads at 1456 x 626, cells ~22 px and heads ~26 px (`p69t20/manias-zoom.png`).
- The peak-to-trough move is the card's own red "64%" plus its badge landing on "trough". No callout can mark a still card (the callout's inner target is a PRESS card's phrase alone, and E56's ring is a chart's).

**Transitions:**
- Row 12 is inside table row 6 (no boundary): the COO -> the table is the slot hand-off (`SLOT_WHY`).
- Dip 2 into row 13 (`VIADUCT_DIP_WHY`):
  - TAKEN: the dip (plate to plate, the pair the dip is for).
  - REFUSED: the thread; the edge arrival (two pictures, not one stage); the occluder (none declared); the melt (the desk carries no chart ink); the recast (neither world is a page).
- Seams: 147.82 `s06->s07 exit=dip darkest 5.3 clean`.

**Departures (`BODY_DEPARTURES` rows 11-13):**
- the records' world change (11);
- the composed card and the cut capital row (12);
- the peak-to-trough move by the badges and the card's own red (12);
- the agenda's third question NOT drawn (12). The dock form writes white on a dark ground and the desk wall is cream, and the page form takes the frame. The COO's card holds instead. Option for HG4;
- the anaphora stage-centred, not "on the plate's quiet zone" (13). A picture plate places cards, never its caption (no door).

**Life:**
- Desk steam, 144.00 vs 146.30 at the mug: mean |dL| 8.60, 11.9% of px changed.
- The table's hold with its badges, 136.60 vs 138.00, whole frame: 20.13, 27.2%.
- The viaduct, 150.00 vs 152.40 (x 0-1000, y 0-420: push + steam): 17.97, 51.4%.
- Table rows: 7 of 7 carry life (row 6 ken 0.04/8/-6, row 7 ken 0.05/-12/4).

**The order of proof (`logs/`):**
- `t21-door.log` (rc 0, cues 13 of 13 bound).
- `t21-probe.log` (67 instants).
- `t21-frozen.log` (no run over 0.5 s).
- `t21-seams.log` (6 boundaries, 0 faults).
- `t21-stagegaps.log` (1.0 s: the two licensed dips only).
- `t21-spoken.log` (0 uncovered).
- `t21-gate.log`: **2 FAIL / 2 WARN / 22 PASS / 1 JUDGE / 6 INFO**.
  - FAILs: M03 and M11 (the bed's, pre-existing, HG4).
  - WARNs: M04 (7 plates vs 13) and M25 (row 1's certificate in the safe band at 0:09-0:10, pre-existing).
  - M05, M10 and M16 PASS (longest gap 2.4 s at 2:18).
  - INFO: M21 s05 9.8 s.
- `t21-door-final.log`: the record-table edits only; the timeline and the table are byte-identical before and after.
- Table snapshot: `t21-SHOT-TABLE-H.md`.

**Tiles:**
- `scratchpad/p69t20/` (10 instants 128.40-146.30) and `scratchpad/p69t21/` (8 instants 147.60-161.00).
- Each has `ref-sheet.png` from build-f's mp4 (sha256 `9a27de1c...` verified, `ref-sha.txt`, `ref-map.txt` 249.50-279.90). There, the Uber card holds on the exhibition hall through "Remember that line". The whole table (four rows, ~55% of the frame) stands 11 s on a busy collage. The 1849 sentence runs on the dawn factory, then the molten pour.

---

## 13. P69 T22 (row 14) and T23 (row 15, BLOCKED) - 2026-09-23

The build now runs 0.00-196.25 s (520 of 2335 words). `UNIT_CUT_PHRASE` = "Bravos' sharpest" (row 15, T23's). RED:
`t22-red.log` (the table ended at 162.50). Row 14 is the first body row in the LONG FORM's profile.

### 13.1 Row 14 (T22): the yardstick - dip 3, camera 2, the breakthrough bars

| table row | window | what |
|---|---|---|
| 7 `world-viaduct-train-rain-v1` | 147.82-162.60 | ends on the cut before "So I built" (was the unit's end) |
| 8 `ev-capital-formation-v1 ...;readability=longform;then=ev-rail-vs-yardstick-bars-v1:bars` | 162.60-196.25 | **dip 3** INTO the page at the world change (the 1849 viaduct -> the 2026 investment page, E47); the page on its axes (E73), `idle=live`; the scale line "ALL EQUIPMENT + IP (for scale)" and the tech line held at nothing; the tech line climbs in ONE pen from "It counts every" (168.12) to the dot-com peak landing on "peak" (177.74); the object's own "23%" written at its 2001 Q1 datum on "twenty-three cents" (178.51); the last twenty-five years draw on "Today it's" (180.44) and land on "twenty-eight" (180.94) with the end tag "28% COMPUTERS + SOFTWARE"; **camera 2** pushes to 1.06 on that landing (180.94 -> 182.04), holds through "the most it has ever been", releases by 185.06; the line undraws over "1840s" (184.26-185.06); the **recast** to the breakthrough bars on "railways took roughly" (185.16), retitled 0.1 s after to the object's own "The railways took half. Tech takes 28 cents."; the two bars land at the comparator's 28 on the stated [0, 30], the railways' bar BURSTS to 50 as the scale rewrites to 0-60, landing on "roughly half" (~186.4) |

**Measured and fixed across drafts (`scratchpad/p69t22/draft1`, `draft2`, `logs/t22-door1..4.log`):**
- "In the 1840s" first matched row 9's "Railways in the 1840s drew" (72.14 s): the camera keys went out of order (`t22-door1.log`). Anchored on "railways took roughly".
- A recast on "In the 1840s" (183.78) burst before "roughly" was said (draft 1, 185.2). On "railways" (185.16) the 50 lands on "roughly half".
- **Camera 2's reach.** The compiler refused 1.06 by name (`t22-door2.log`): "the title's right edge leaves the stage at 1.033". The long form's title and sub start at x 42 and the engine resolves the 28 at (1168, 609) (probe at 181.6 s), so a zoom IN PLACE crops the title at 1.037. The push therefore LANDS the datum at `at` (0.6344, 0.5833) = (1218, 630): the only window that keeps the page's glyphs on the stage (title left >= 1194 px, top >= 612 px) and its own edges past the stage's (page left <= 1238, top <= 645 - else the ground beyond the page shows: at (1260, 660) a 22 px cream strip left and 14 px top, 182.6 s). Final probe at 182.3 / 183.5 / 184.2 s: zoom 1.06, look (1168, 609), title [43..38, 26..29], tag `28% COMPUTERS` at x 1236-1733 - steady.
- **ENGINE DEFECT, named for the parent:** a `datum` look with `at` != look RUNS AWAY. The engine resolves the datum on the camera-moved frame each instant, so the look walks with the pan it causes (drafts 2-3: look 1183 -> 1116 px over 1.9 s at a constant 1.06; the title's left edge -7 then -62 px). A datum is stable only zoomed in place. The row's look is a `point` at the 28's own REST position (`YARD_CAM_LOOK`). Owner: the engine (resolve a camera's datum look in world coordinates).
- The recast drew the arriving "50¢" value label ON the tech line at 3:05 (the gate's M34 FAIL on draft 4). The line now undraws first (`YARD_UNDRAW_S`, row 10's MEMORY_HOLD pattern); M34 PASS.
- The object's own mark (`23%`, "dot-com high") is not drawn by the page, so the figure is the one "23%" on screen (no M28 pair).

**Departures and findings (for the parent):**
- **The scale line is held at nothing.** "ALL EQUIPMENT + IP (for scale)" (65%) is on the object, and no sentence names it. Its tag would be a number the voice never says, and it is not "everything the country invests" (that is 100). build-f drew it.
- **Units: % on the line page, ¢ on the bars page** (each page one unit, E53). The treatment's "23¢ / 28¢" figures are written as the line object's own "23%" and "28%". The bars object states its own ¢.
- **The breakthrough pill drops the unit:** the railways' bar reads "50", the 28 bar "28¢" (tiles 186.8-195.0). The burst's count writes the number, not the object's `note` "~50¢". Owner: the engine (`lpPaintBreakthrough`'s pill string).
- **The plot uses ~55% of the page width** (plot x 128-1168 of 1920) on both states. The right ~40% is the long form's end-tag room, sized for the widest tag of every series, including the held 65% line's. The key rail with the full names is T10's and NOT BUILT, so the tags keep their full names here ("28% COMPUTERS + SOFTWARE" fits at full form). Owner: T10 / T33.
- **The recast's middle** (185.3-186.1, `tile-185.80`): a half-written title, the bars' "28¢" / "50¢" labels floating, the "23%" figure ghosting under the arriving bars. This is R26-261 (known); the figure outlives its line's undraw (a page-bound figure retracts with its PAGE, R26-219).
- **E50:** the bars' burst lands ~186.4 and the row ends at 196.25, 9.9 s (INFO band). The gate's M21 did not list s08.
- **The empty open (162.6-168.1):** the page's axes, title, sub and its 50% railway rule stand for 5.5 s while "So I built a yardstick for America" is said, before the line starts. The rule IS the yardstick. Life on this stretch: 164.0 vs 167.0 (x 0-1500, y 150-850), mean |dL| 1.84, 2.9% changed.

**Transitions** (printed in `SHOT-TABLE-H.md`):
- Dip 3 INTO row 14 (`YARD_DIP_WHY`). TAKEN the dip, the last resort: this page names no arrival that could carry it. REFUSED: the snap / throw-then-zoom / throw-then-push (nothing thrown on the viaduct names the yardstick); object-becomes-chart (the train is not the page's data); the spiral return (a first page); the mount (the yardstick does not belong to 1849's plate, E47); the melt (the plate carries no chart ink); recast / rescale / morph (a plate is not a chart). Seam 162.60 `s07->s08 exit=dip darkest 3.8 clean`.
- The recast inside row 14 (`YARD_RECAST_WHY`). TAKEN the plain recast (E64: one measure, one technology's share of a country's investment, in the other form - the line's last datum IS the 28 bar). REFUSED: the dip and the cut (no world change); rescale / extend (the 50 is not on this series); morph; remake (the 50 is Britain's, not the same data); the melt (it would clear the board the 28 stands on).

**Life:** 188.00 vs 190.00 (the bars held, x 0-1500, y 150-850): mean |dL| 1.95, 3.0% changed. Table rows 8 of 8 carry life (row 8 `idle=live`).

**The order of proof (`logs/`):** `t22-door-final.log` (rc 0, cues 15 of 15 bound), `t22-probe.log` (80 instants), `t22-gate.log`
**2 FAIL / 2 WARN / 23 PASS / 1 JUDGE / 5 INFO** - FAILs M03 and M11 (the bed's, pre-existing, HG4); WARNs M04 (8 plates vs 16) and
M25 (row 1's certificate at 0:09-0:10, pre-existing); M24 PASS (the pointing species on the moving-camera scenes in frame); M34 PASS.
`t22-frozen.log`, `t22-seams.log`, `t22-stagegaps.log`, `t22-spoken.log`: see 13.3. Drafts: `t22-door1..4.log`. Table snapshot: `t22-SHOT-TABLE-H.md`.

**Tiles:** `scratchpad/p69t22/` - `tiles-sheet.1.png` / `.2.png` at 162.4, 164.0, 167.0, 170.0, 174.0, 177.9, 179.6, 181.3, 182.6, 184.6,
185.8, 186.8, 188.0, 190.0, 195.0; `ref-sheet.1.png` / `.2.png` from build-f's mp4 (sha256 `9a27de1c...` verified, `ref-sha.txt`;
`ref-map.txt`, Script G's clock 122.6-165.2 - Script G carries this paragraph BEFORE 1849). There, the SAME capital-formation chart
stands as a card ~55% of the frame wide over the ledger desk and then the boiler gauge, in every ref tile from 122.6 to 165.2 s
(the treatment's #13 held dock), the 65% line drawn, no build, no camera and no bars.

### 13.2 Row 15 (T23): BLOCKED - the two-eras page draws no lines

`ev-tnx-two-eras-v3` is a PANELS object: `axes.panels` (dot-com 1998-2001, AI era 2021-today) and no top-level `series`. A
LEDGER PAGE draws no panel. Compiled, the page is `dense-line` with **0 series** (`scratchpad/p69t23/draft1/page-spec.txt`:
`dense-line 0 True 0 7.2`). The engine paints `panels` only in the dock's live chart (`fillDock`,
`scene-evidence-engine.mjs:6724`), and `buildLedgerLine` never reads them. On the frame (`scratchpad/p69t23/draft1/tiles-sheet.png`,
196.6-240.0) the page shows its title, its two rules ("Fed funds peak, 2000 - 6.5%", "their tripwire - 5.5%"), a y axis
5.5-6.5 and a garbled "2000" tick, and no line for 46 s. The two `note`s (BoE, the concession) did not show either.

**The stamp refuses:** with the Fed authored (`prop: True, arrive: stamp` on "Fed at six and", 217.46), the door FAILs by name
(`t23-door1.log`): "the largest mark this place holds at (112, 180) paints 46 px on its long side, under the 120 px mark floor". So no
HG2 frame exists: no frozen copy was made and no strip was rendered.

**The door is left at T22** (every row-15 constant, the page, the dock and the prop registration withdrawn; a comment at
`YARD_RECAST_WHY` names the block). The full T23 draft, as it compiled, is staged at `scratchpad/p69t23/door-t23-draft.py`:
- the melt's throw into the page (`TNX_MELT_WHY`: the dip, a third recast state, rescale / extend, morph and melt:splash:chart /
  melt:morph refused by name);
- the Fed prop, its DOCK_META entry and its `D.register`;
- a `note` for the BoE's 6% (the page's own rules already write the Fed's 6.5% and their 5.5%, so those are not written twice);
- a concession note;
- `{"attention": "landings"}` for the camera's pull on the contact.

**The object's rules are themselves a unit mix:** the Fed-funds 6.5% and Bravos' 5.5% Fed tripwire are drawn as `hlines` on a
10-YEAR-yield axis. The departure (BODY_DEPARTURES row 15) refuses rings for exactly this reason, and the object draws the rules
anyway. Operator item. **SUPERSEDED (the parent, 2026-09-23):** E53 s5, "a policy rate is a RULE" - the rules are the right form,
not a unit mix; the parent authored `ev-tnx-two-eras-v4` (door (a) below). Section 14 builds on it.

**Doors for the parent (none is in this write set):**
- (a) an evidence object the ledger page can draw: the two eras as ordinary `series` on one x axis (a gap between 2001 and 2021),
  or one era per page. Write set: `evidence/objects/`;
- (b) the engine: `buildLedgerLine` draws `axes.panels` (the dock chart already does, `:6724`). Lane B;
- (c) the live chart card of the object, read at ~0.90 of the stage on a plate, with the Fed stamped in the plate's room
  (`;room=`). This departs from "the page's biggest room" and from the treatment's "no bare plate 2:45-6:04".

### 13.3 The chain tails (T22's final build)

- `t22-frozen.log`: `no run of identical frames over 0.50s (whole frame)`.
- `t22-seams.log`: `seam frames: 7 boundaries, 0 faults`; `162.60 s07->s08 exit=dip darkest 3.8 clean`.
- `t22-stagegaps.log`: `162.60 s07 exit=dip -> enter=axes empty 0.2s picture 0.4s licensed (a dip is a world change)`.
- `t22-spoken.log`: `spoken visuals: 1 pointing phrases, 0 uncovered`.
- `t22-probe.log`: 80 instants. The gate as in 13.1.

## 14. P69 T23 (row 15) - the trigger and the concession on `ev-tnx-two-eras-v4`; PROP 1 WITHHELD - 2026-09-23

The build runs 0.00-242.85 s. `UNIT_CUT_PHRASE` = "But here's the question" (row 16, T24's). RED: `t23-red.log`.

| table row | window | what |
|---|---|---|
| 8 (row 14) | 162.60-195.82 | ends 0.5 s before "Bravos' sharpest" (TNX_MELT_LEAD_S) |
| 9 `ev-tnx-two-eras-v4 ...;idle=live;readability=longform` | 195.82-242.85 | the bars MELT and are thrown (E88) in the breath after "eighty years."; the yields page on its axes, the dot-com line on a 1998 stub (TNX_OPEN_CAP, M31), the AI era held at nothing; the dot-com yield draws on "what actually ends" (198.38) through the 1998 dip to x 1.2 by "They fail by pointing" (206.07), then crosses back above its first print on "It dies when rates cross back above" (209.95), landing on its Jan 2000 high on "began"; on "Fed" (217.46) the title becomes "The Fed at 6.5% in 2000: the internet trade rolled over" (the page's own 6.5% rule); the rollover draws on "internet trade rolled" (219.69); the AI era draws on "for this cycle" (223.30), ending at 4.7% under their 5.5% rule; on "Put my agreement" (228.90) the title becomes "Agreed: the cycle is real, and so is the threshold". No bare plate 2:45-6:04 |

**PROP 1 IS WITHHELD (`FED_STAMPED = False`) - three blockers, none in this write set:**
1. **The fit has no room (the fixture).** v4 is not in `content/video_engine/assets/page-boxes.v1.json`; on the estimated boxes the plot
   is solid and the fit refuses the Fed at 61 px (`t23-door3.log`). Measured into a SCRATCH copy of the fixture
   (`scratchpad/p69t23/fitsim/fitsim.log`), the same fit takes the plot's empty lower-right room: mark 186 x 171 painted px at (1136, 672).
   Unblock: `measure_page_boxes.py --write --project <build-h>` (reads this build's compiled timeline).
2. **The right margin is refused (the end-tag column).** `ledger_page._landscape_full_boxes` reserves the end tags as a COLUMN from
   the plot's top to its bottom (x 1329-1880, y 250-808), and `page_boxes` keeps that estimate even on a measured page
   (`ledger_page.py:2277-2280`, "the fixture does not measure" tags). Authored centres in the margin level with the rules are refused
   at every point tried (`fitsim/margin.log`). Owner: the engine (tags boxed at their drawn extents).
3. **The prop renders as a black square (the compiler flattens alpha).** `build_scene_timeline_f.dock_uri` (`:5373-5377`) embeds every
   non-video dock through `data_uri(p, CARD_W)` (`:5335-5346`), which does `convert("RGB")` and writes JPEG; the Fed's asset map entry
   is `data:image/jpeg` (`scratchpad/p69t23/hg2-preview/build-sim/assets.json`), so the transparent sky paints black and the hatch
   shadow is cast by the square (`hg2-preview/fed-settled-crop2x.png`). The cutout itself has true alpha
   (`hg2-preview/fed-cutout-on-magenta.png`). The goldens bypass this route (`build_golden_sources.py` `_prop_stamp` embeds PNG).
   Call site: `:7789 uris[aid] = dock_uri(ap)`.
No frozen copy (`build-h-frozen-hg2/`) was made: there is no stamp to freeze. The preview (scratch fixture, scratch build) is in
`scratchpad/p69t23/hg2-preview/`.

**Measured and fixed:**
- Notes land OFF the stage: both `note`s at y 1142 / 1222 on a 1080 stage (`scratchpad/p69t23/notes/notes.log`) - the engine's
  "no free column" fallback on a full-stage page. Replaced by retitles; the BoE's 6% is said, not drawn. Owner: the engine.
- The first BoE retitle contradicted the page (no 6% rule on a US page; the parent's read) - replaced by the Fed title off the page's rule.
- A melt opened ON "Bravos'" left 0.2 s empty under the word (`t23-stagegaps.log`, draft 5): moved 0.5 s earlier into the breath.

**Named, not fixed:**
- **M31 FAIL (0.2 s at 195.82, silent)** is the probe's blind spot, not an empty frame: a melting BARS page records no page ink for its
  first 0.2 s (`scratchpad/p69t23/notes/gap-fresh.log`) while the frame shows the bars melting (`scratchpad/p69t23/gapframes/cold/`).
  Row 8's melt of a line page keeps its `chart` box. Owner: the probe / stage-gap measure.
- **Melt seek purity:** seeking 63.95 then 195.85 painted row 7's divergence page melting at 195.85 (`gapframes/tiles-sheet.png`); a
  fresh seek paints the bars. The melt's snapshot survives a jump between two melts. Owner: the engine.
- **M03 FAIL** now reads 47 s from 3:15 - row 15 has no arrival while the Fed is withheld (the stamp at 217.46 splits it). The bed's
  own 45 s gap (0:09-0:54) stands under it.
- **M21 WARN** s09 17.6 s past the last data mark (3:45 -> 4:02): the concession carries no figure; the narrator's own tripwire has
  none in the script. CUT, unsourced: a figure for "my own tripwire", and "don't try to call the top" as a written quote.
- The AI era renders ORANGE though the object names `crimson` (the palette's mapping).
- Preview only: the camera's landing pull brings the rewritten title's left edge to the stage edge (218.66, `hg2-preview`).

**Life:** 235.0 vs 237.0 (x 0-1500, y 150-850) mean |dL| 7.20, 8.3% changed; 208.0 vs 210.0 mean |dL| 3.02, 4.3%. Rows 9 of 9 carry life.

**Transitions:** INTO row 15, the melt's throw (`TNX_MELT_WHY`); refused by name: the dip (no world change, E47), a third recast state,
rescale / extend, morph, melt:splash:chart and melt:morph. Seam `195.82 s08->s09 exit=melt:throw:1 darkest 23.2 clean`. No dip.

**The order of proof (`logs/`):** `t23-door-final.log` (rc 0, cues 16 of 16), `t23-probe.log` (93 instants), `t23-stagegaps.log`,
`t23-gate.log` **3 FAIL / 3 WARN / 22 PASS / 1 JUDGE / 4 INFO** (M03, M11 - row 1's, M31), `t23-seams.log` (8 boundaries, 0 faults),
`t23-spoken.log` (2 pointing phrases, 0 uncovered), `t23-frozen.log` (no run over 0.50 s). Drafts: `t23-door3..5.log`.

**Tiles:** `scratchpad/p69t23/final2/tiles-sheet.1.png` / `.2.png` beside `ref-sheet.png` (build-f's mp4, sha256 `9a27de1c...0dd3`
verified, `ref-sha.txt`; `ref-map.txt`, Script G 173.2-199.5). build-f holds the old two-panel card small over the broadcast desk,
then a bare desk for the concession; H holds the page full-stage through both.

## 15. P69 T24 (row 16) - who is paying: the issuance, two recasts, the filings on the desk; PROP 2 STAMPED - 2026-09-23

The build runs 0.00-321.12 s (897 of 2335 words). `UNIT_CUT_PHRASE` = "So put it together" (row 17, T25's). RED: `t24-red.log`
(the table ended at row 9, 195.82-242.85). Row 15 now ends at 242.38 (the melt's lead into row 16).

| table row | window | what |
|---|---|---|
| 10 `ev-debt-issuance-line-v1 ...;idle=live;readability=longform;then=ev-ig-credit-weighting-v1:bars:2;then=ev-capex-consensus-v1:bars:1` | 242.38-303.54 | the yields MELT and are thrown (E88) in the breath before "But here's the question"; the issuance page on its axes, the 2020 average a stub, the 2026E estimates at nothing; the title becomes the rehook's question on "who is paying" (244.72); the 2020-24 average draws across its years on "For years the giants ... out of pocket" (246.80-251.96); the object's own title "The builders started borrowing" is written back on "Then the bills got" (255.01); "$28B a year / 2020-24 average" lands on "twenty-eight" (260.74); the 2025 actual climbs on "Last year" to 121, "$121B" under its end tag (264.55); the two 2026E estimates draw on "tracking toward" (266.61), the wedge a SPREAD and "$130-150B / 2026E" above the $150B tag as "fifty" is said (T14: a range, never a midpoint); **recast 1** (plain, `keyed: false`) to the IG index on "Technology used to be" (274.56), its unit in its title, the >12% bar EMPHASIZED; **recast 2** (plain) to the capex consensus on "a bet on data centers" (287.59), its unit in its title, the 690 EMPHASIZED |
| 11 `world-internal-memo-v1;use=landing;room=0.62,0.03,0.35,0.33` | 303.54-321.12 | the page MELTS and splashes onto the records' desk (row 11's world) on "Go into the filings"; the `ev-doc-leases` record is thrown as the splash lands (304.59, contact 305.05) at the reading size (0.64 of the stage, box [48, 405, 1229, 442]); **PROP 2** `prop-hyperscale-datacenter-v1` STAMPED on "Data centers" (308.85, contact 309.00, cue `landing 11 (stamp, ink)`) into the desk's declared room - fitted FIRST (P69 T5): `plate: mark 244x150 painted px (12.7% of the stage width); ring capped at 1.08x by the room`, box [1399, 148, 245, 152], 0 px against the record; the ken push and the mug's steam are the desk's life; both leave with the desk |

**PROP 2 IS STAMPED (`DATACENTER_STAMPED = True`)** - on the desk, not on a page. It renders as the T6d BLACK SQUARE (the compiler's
JPEG flatten; the hatch is cast by the square): `scratchpad/p69t24/final/stamp-contact-crop.png`, `stamp-parked-crop.png`. The
placement, the timing and the cue are the row's; the square is lane B's.

**Why the record and the stamp moved to the desk (measured, drafts 2-4, `logs/t24-door2..4.log`, `scratchpad/p69t24/draft3/`):**
1. On the three-state page the stamp was REFUSED: "the largest mark this place holds at (1756, 192) paints 70 px on its long side,
   under the 120 px mark floor" (`t24-door2.log`, estimated boxes). And a row's stamp and docks are fitted to the row's FIRST page
   (`row_stamp_fits` / `dock_place` read `world["page"]`, state 0): a stamp landing in the capex state is fitted to the ISSUANCE
   page's room. Owner: the engine (fit a dock to the state it lands in). Measuring the page into the fixture would not fix this.
2. With the capex as its own page (draft 3), E65 placed the record `outside [608, 64, 703, 253]` - over the title and the 870
   label, at 703 px (card-size type).
3. E50: the capex bars would stand 27 s past their landing under the record (M21 4:53 -> 5:21).
The desk is the build's own records' world (row 11, the parent's FIX 2: records need a clean ground).

**Measured and fixed:**
- `t_28` collided with row 14's camera-landing variable (the camera keys went out of order, `t24-door1.log`) - renamed `t_avg28`.
- A prop and a card both on slot 0 painted only the card (draft 4: no data centre on any tile) - the prop is on slot 1 (T5's golden pair).
- The range figure pinned to the $150B tip read "$130-150B $150B" (draft 3); under the $130B tip it sat on "issuance" (draft 4) - lifted above the wedge.
- The IG recast stretched to land the bars on their words (8 s) garbled the axis hand-over for 8 s (draft 4) - back to 1.2 s.
- A `bracket` on the capex bars state drew no span and wrote its label behind the 690 bar (draft 5, tile 302.5) - cut.
- The probe's M28 ("issuance" tag on "$121B", 21 %) and M34 ($121B on both 2026E lines; the callouts on bars crossing "Projected" and "2026 consensus") - `$121B` moved under its tag (`DEBT_2025_DY`), the rings replaced by the state's emphasized bar.
- The compiler would DERIVE `keyed: true` for the issuance -> IG recast (three lines, three bars) and carry the issuance datum into the 9% bar - authored `keyed: false`.

**Named, not fixed:**
- **M03 FAIL 62 s from 4:02** (242.38 -> 303.54): the gate counts dock entries and page starts, never a recast (`gate_motion_density.py:1323`), and this row's two E58 recasts are the treatment's. Splitting the IG off as its own page would pass M03 and lose a recast. Owner: the gate (a recast's arriving chart is evidence entering), or the parent's call.
- **M21 WARN s10 14.8 s** (4:48 -> 5:03): the capex bars carry three sentences ("four hundred and eighty", "six hundred and ninety", "The estimate went up faster than the year went by") to 5:01. The IG bars pass (11.8 s).
- **The bars objects carry no unit** (`yunit`/`yfmt` absent): the bars print "9.0 / 10.0 / 12.0" and "480 / 690 / 870" and the y axes have no unit. Each state's retitle carries the unit (`IG_TITLE`, `CAPEX_TITLE`). Door for the parent: a v2 of each object with `yunit`/`yfmt` (evidence/objects is not this slice's).
- **The capex object states two figures the row never says**: the 2027 $870B bar and the sub "94% of operating cash flow" (row 17's figure). Both are sourced (PIMCO Figs 2-3); neither is spoken here. Door: the v2 above, or the parent's ruling.
- **The capex bars land on "a bet on data centers"**, ~5 s before "four hundred and eighty" is said (E50 on the IG bars puts the recast there).
- **The recast's middle** (275.2, 288.0): the issuance page's figures ghost over the arriving bars; the 12.0 pill floats above the plot at 288.0 - R26-261 (known).
- The ring at the stamp's contact grazes the mug's rim (the ken push lifts the mug into the room; ~5 px for the ring's 0.47 s).
- The stamp's mark is 244x150 in a 672x356 room: the ring's circle (the mark's diagonal x 1.08) binds on the room's height. Engine behaviour, reported.
- "right there in the filing" - the treatment's callout on the filing's line is cut: E56 refuses a ring on a still card; the record's own highlight on "$822 billion" carries it.

**Transitions** (printed in `SHOT-TABLE-H.md`): INTO row 16 the melt's throw (`DEBT_MELT_WHY`: the dip, a recast, rescale / extend, morph, melt:splash:chart / melt:morph refused); the two recasts (`IG_RECAST_WHY`, `CAPEX_RECAST_WHY`: dip, cut, rescale / extend, morph, remake, the melt refused); INTO the desk the melt's splash onto the plate (`DESK_MELT_WHY`: the record and the stamp on the page, an undraw under the record, a park, the dip, the thread, recast / remake refused). No dip, no cut.

**Life:** 270.5 vs 272.5 (the debt page, x 0-1500, y 150-850) mean |dL| 2.46, 3.1% changed; 298.3 vs 301.0 (the capex state) 2.66, 3.6%; 313.0 vs 315.0 (the desk) 11.26, 19.8%. Rows 11 of 11 carry life (row 10 `idle=live`, row 11 `ken 0.04/8/-6` + the mug's steam).

**Tiles:** `scratchpad/p69t24/final/tiles-sheet.1-3.png` (29 instants, 242.6-320.8) beside `ref-sheet.1-3.png` (build-f's mp4, sha256 `9a27de1c...0dd3` verified, `ref-sha.txt`; `ref-map.txt`, Script G 280.6-348.8). build-f carries the same beats as PNG cards over plates (the bank vault, the ledger desk, the exchange board, the pylons); H draws them on one page and lands the record on the desk.

## 16. P69 T25 - R26-282 (the IG and capex objects' v2) and row 17: the arithmetic, the 94 bar - 2026-09-23

The build runs 0.00-358.03 s (1006 of 2335 words). `UNIT_CUT_PHRASE` = "And that's the part everyone" (row 18, T26's). RED: before
the slice the table ended at row 11 (303.54-321.12, `logs/t24-door-final.log`).

**R26-282 - the two v2 objects (evidence/objects/, values and colours unchanged, each with `proof` and `provenance_note`):**
- `ev-ig-credit-weighting-v2`: `unit: "%"` (the source's own - % of the Bloomberg Corporate Bond Index, dossier C3 `:143-146`);
  values written as the integers they are (9.0 -> 9: a bars page prints the token as written, so v1 printed "9.0"); the sub states
  what the bars show ("Tech's weight in the Bloomberg Corporate Bond Index, as a % of the index: 2024, now, and the projection
  (above 12%)"). The third bar is a FLOOR: the source says "above 12%" (the script "past twelve"); it stands at 12 and the sub says
  "above 12%" - no number above 12 is on disk. v1's sub (data centres) dropped: the bars do not show data centres.
- `ev-capex-consensus-v2`: `unit: "$"` - the page's currency PREFIX (`lpWithUnit`, scene-evidence-engine.mjs:8179: "$" is a prefix,
  every other unit a suffix; there is no "$...B" form), so the bars print $480 / $690 and the axis $0-$600, and the sub carries
  "US$ billions". The sub no longer carries row 17's "94% of operating cash flow" (PIMCO Figure 3, a different measure). **The 2027
  $870B bar is DROPPED**: the source shows it (dossier B1 `:115-117`, `:226`), but the script never says it - row 16 reads the
  REVISION of the 2026 estimate ("When the year opened ... four hundred and eighty ... Consensus now says six hundred and ninety. The
  estimate went up faster than the year went by."), not the forward consensus. '2026 consensus' relabelled 'Consensus now' (both
  bars are 2026 estimates taken at two dates; the sub names the year).
- Row 16 points its recasts at the v2 objects; the title stopgap is gone: each recast retitles to the state's OWN title (a recast
  rewrites sub and source itself, the title only by a verb - `titleText`, :8494). Door re-run `logs/t25-door-step1.log` (rc 0).
  Tiles `scratchpad/p69t25/step1/` and `final/` (275.2-301.0): "9% / 10% / 12%", "$480 / $690", bars 196 px (probe plot box).
  Named: at the recast middle (288.0) the IG pill tweens a transient "11.6%" behind the panel edge (`step1/crop-288-pill.png`) -
  R26-261's garbled middle.

| table row | window | what |
|---|---|---|
| 11 `world-internal-memo-v1;use=landing;room=...` | 303.54-324.62 | row 16b now also holds row 17's rehook ("So put it together, because this is where the arithmetic gets tight."); the record and PROP 2 END at 323.12 (1.5 s before the dip - see below), the desk bare with the stage caption for "gets tight." |
| 12 `ledger:ev-capex-ocf-94-bars-v1:bars::right:axes:cut;idle=live;readability=longform` | 324.62-338.44 | **dip 4** centred on "Over the next two years, PIMCO" (the take has no measured gap after "tight.", so `at()` - cut_before's own dip rule is the onset); the page on its axes, the 100 rule "every dollar from operations"; the one bar grows as the page lands and stands at 94 with its value by ~325.4; the **figure "94%"** (the object's own note) written on the repeat "Ninety-four." (332.21), INSIDE the bar under the 100 rule (T6's `lpBarLabelPlace`), the value yielding to it; not emphasized (R26-256: the pill would print 94% twice) |
| 13 `world-internal-memo-v1;use=landing;room=...` | 338.44-358.03 | the page SPINS INTO A POINT (the suck, `suck:0.345,0.58` - the record's slot centre) in the breath before "So when you hear the buildout" and the records' desk is standing there; "funded out of profits - that was true. It stopped being true ... Nobody here committed fraud." in caption STAGE mode over the bare desk; the filings' record (`dock-h-leases-record`) thrown back on "signed" (348.01) at its reading size, for "They signed a promise ... The steel kept building. The paper just got heavier. And promises are the part of this that nobody is charting." (anchor caption); ken push + mug steam |

**Measured and fixed:**
- The page first left on "It stopped being true" (draft 1): M21 read s12 14.4 s - the gate's clock starts at the BAR's landing, and a
  figure "neither restarts nor ends the clock" (`_deployed_lives`). Moved to the breath before "So when you hear": s12 now under 12 s
  (M21 lists only s09 / s10).
- The desk's docks stood over the 94 page after the dip (draft 2, `scratchpad/p69t25/propexit/`): the record faded by ~324.8 and PROP 2
  stood at the page's top right to ~325.1 - a prop over a chart. Ending them 0.6 s early changed nothing (draft 3): the engine SNAPS a
  dock exit within 1.4 s of a boundary onto the boundary (scene-evidence-engine.mjs:6592) and only a WIPE sweeps a card off (`swept`,
  :17425). They now end 1.5 s early, on "arithmetic" (`draft4/`, clean).
- A sub on the figure ("of operating cash flow", the object's words) was wider than the 196 px bar and written in the bar's ink - its
  ends vanished on the dark plot (`draft5/tile-334.50.png`). Cut.

**Named, not fixed:**
- **M28 FAIL (new) `val:94% on bracket:94%` at 5:32** - T6's hand-over: the bar's value fades on the figure's write clock (the T6 test
  asserts 0 < opacity < 1 mid-write) and the figure's number sits a few px off the value, so for ~0.6 s "94%" double-prints
  (`scratchpad/p69t25/m28/crops.png`, tile 332.70); after it the page reads exactly as before, so the figure's landing is nearly
  invisible. Owner: the engine (write the figure ON the value it replaces, or cut the value at the figure's first glyph) and the probe
  (M28 pairs a value with the figure it yields to).
- **The bar lands ~2.6 s before "ninety-four"** (~325.4 vs 328.00): the page's visible bar build is ~0.8 s (the gate books 3.0 s,
  327.62); a bars page has no hold for a bar (`build_to` caps a series), and a mid-sentence dip was refused. The title states 94 from
  the landing, inside the sentence that says it. The treatment's "shooting on Ninety-four" is a departure (BODY_DEPARTURES row 17).
- **A dip does not take the outgoing docks** (above) - engine: a dip should clear the docks in its black as a wipe does.
- **The suck is silent**: "[silent] no cue mapped for suck" (the kit's cue map has no suck slot). Owner: sound / `authoring.audio`.
- **The stage caption on the bare desk is low-contrast** (white on the cream wall and the lamp's cone, 340.5 / 344.0) - R26-268.
- CADENCE WARN "5:42 16.0 s on a single piece" (the desk row 13 and its one record, 348-358).
- M03 (62 s from 4:02, R26-280), M11 (row 1), M31 (row 15's 0.2 s probe blind spot) - pre-existing.

**Transitions** (in `SHOT-TABLE-H.md`): INTO row 12 **dip 4** (`ARITH_DIP_WHY`) - refused: snap / throw-then-zoom / throw-then-push (the
only card on the desk is another figure), object-becomes-chart (PROP 2 is not the page's data), the spiral return, the mount, the axes
open as the boundary's carrier (it would CUT photograph -> board mid-rehook; the page still enters on its axes; row 14's dip 3 is the
build's plate -> page precedent), the melt, recast / rescale / morph. INTO row 13 **the suck** (`DESK_SUCK_WHY`) - refused: the melt
(the transform row 16b spent on this desk 40 s earlier - the variety rule), the door, the dip, holding the page (E50). The shot table's
boundary lookup now reads `(plate, exit)` first so a RETURNING world names its own transition. Flow count: 0 cuts, 4 dips, 1 arrival,
7 transforms. The treatment's dips 4 and 5 (row 18) become dips 5 and 6.

**Departures and cuts (BODY_DEPARTURES row 17):** the Epoch "94 cents" mark (a different claim) cut; the PIMCO "record" (the treatment's
`ev-doc-macdonald` is the Uber COO) - no badge, the page's own source line names PIMCO Figure 3; `chart_to ev-capex-funding-v1` from
row 16's page -> dip 4 from the desk; the page holding through the post-key -> E50's leave by the suck, the anaphora on the ANCHOR
caption under the record (a dock stamps the caption anchor); the bar "shooting on Ninety-four" -> landing with the page.

**Life:** 334.5 vs 336.5 (the 94 page, x 0-1500, y 150-850) mean |dL| 2.19, 3.0% changed; 328.2 vs 330.0 2.67, 3.6%; 350.5 vs 352.5
(the desk) 12.39, 19.0%. Rows 13 of 13 carry life (row 12 `idle=live`, row 13 `ken 0.04/8/-6` + the mug's steam).

**The order of proof (`logs/`):** `t25-door-final.log` (rc 0, cues 22 of 22), `t25-probe.log` (132 instants), `t25-gate.log` then
`t25-gate-final.log` re-stamped on the fresh frame hashes **4 FAIL / 3 WARN / 21 PASS / 1 JUDGE / 4 INFO** (M03, M11, M28, M31),
`t25-frozen.log` (no run over 0.50 s, 0-358.03), `t25-seams.log` (12 boundaries, 0 faults; 324.62 dip darkest 1.1 clean; 338.44
suck darkest 35.3 clean), `t25-spoken.log` (3 pointing phrases, 0 uncovered), `t25-stagegaps.log` (324.62 empty 0.2 s licensed;
338.44 empty 0.0 s). Drafts: `t25-door1..5.log`.

**Tiles:** `scratchpad/p69t25/final/tiles-sheet.1-4.png` (37 instants: row 16's recasts 275.2-301.0, row 17 321.5-357.8) beside
`final/ref/ref-sheet.1-2.png` (build-f's mp4, sha256 `9a27de1c...0dd3` verified, `ref/ref-sha.txt`; `ref/ref-map.txt`, a word
alignment of the two takes). build-f carries the 94 as a badge on the Uber COO card over the pipeline plate, then Epoch's quarterly
capex-vs-cash card with its "94 cents" mark (the realised-quarter claim T14 cut) over the signature; H draws PIMCO's forward 94 at
page size and returns to the filings for the promise.

### 16a. Revision on the coordinator's read of row 17 (2026-09-23) - supersedes the section above where they differ

1. **The bare desk (338.44-348.01) was a defect** - REBUILD-TREATMENT-H.md:173 "no bare plate between 2:45 and 6:04", and the centred
   stage caption's unspoken words were pale grey on the pale cream wall (tile 344.00; R26-268). The record's 348.01 entry was this
   door's own choice (`t_signed`, "signed"), NOT the engine's dock-exit snap (`scene-evidence-engine.mjs:6592` moves exits only).
   Now `dock-h-leases-record` is THROWN AS THE SUCK STARTS (`t_record = t_stop`, 338.44), lands as the page vanishes into its point,
   and stands to 358.03; it is live before "So when you hear" (338.74), so every caption page of row 13 is stamped ANCHOR (a caption
   page takes the dock live at its START, `_dock_live_at`) - the whole row, anaphora included, is the bottom caption under the record.
   Table row 13: `dock-h-leases-record` 338.44-358.03. CADENCE WARN now "5:38 19.6 s on a single piece".
2. **The 94 double print (M28)** - the figure is DROPPED (the bar's own value is the 94). The coordinator's `ring` was tried first
   (Recall: `CAPABILITIES.md:87` "E56: a ring has one use - a number or a point on a CHART"; `CAPABILITIES.md:45` the `ring` kind,
   `form: "dashed"`): on the bar's datum it resolves the WHOLE `.bar` (resolveTarget's bar branch, `:13722`) and the dashed ellipse
   crossed "Capex, next two years" (`scratchpad/p69t25/draft6/`, tiles 332.70 / 333.40); a `point` / `region` ring must carry a label
   with a digit (`_validate_ring`) and `paintRing` WRITES it beside the ellipse (`species/ring.mjs:261`) - a second "94%". No target
   reaches the value label alone. Taken instead: **`relight {ref: title}` on "Ninety-four." (332.21, 1.2 s)** - Recall:
   `build_scene_timeline_f.py:576` SPECIES_WHEN "relight: the sentence RETURNS to a number already on the page (the ring's echo) - the
   bracket or the title re-fires"; `CAPABILITIES.md:77` "RETURNS to a number (relight)". The title "Ninety-four cents of every dollar"
   lights gold on the word; one "94%" on the page (`draft7/`, `final2/`). Table row 12: `relight @332.21`. M28 CLEARS.

**The order of proof (second run, `logs/`):** `t25-door-final2.log` (rc 0, cues 22 of 22; "[silent] no cue mapped for suck"),
`t25-probe2.log` (130 instants), `t25-frozen2.log` (no run of identical frames over 0.50 s), `t25-gate-final2.log` (stamped AFTER the
frame hashes) **3 FAIL / 3 WARN / 22 PASS / 1 JUDGE / 4 INFO** - M03 (62 s from 4:02, R26-280), M11 (row 1), M31 (row 15's 0.2 s probe
blind spot), all pre-existing; M21 lists only s09 / s10; M18 PASS 0:00-5:58. `t25-seams2.log` 12 boundaries, 0 faults (324.62 dip
darkest 1.1 clean; 338.44 suck darkest 35.3 clean); `t25-spoken2.log` 3 pointing phrases, 0 uncovered; `t25-stagegaps2.log` 324.62
empty 0.2 s licensed, 338.44 empty 0.0 s picture 0.0 s. Drafts: `t25-door6.log` (ring), `t25-door7.log` (relight).

**Life (final2):** the desk under the record 340.5 vs 342.5 mean |dL| 9.75, 15.1% changed; 350.5 vs 352.5 11.79, 19.3%. The 94 page's
life as above (334.5 vs 336.5, 2.19, 3.0%). 13 of 13 rows carry a life token.

**Tiles:** `scratchpad/p69t25/final2/tiles-sheet.png` (324.9, 332.3, 332.7, 333.4, 338.55, 338.8, 340.5, 342.5, 344.0, 347.5, 350.5,
352.5).
