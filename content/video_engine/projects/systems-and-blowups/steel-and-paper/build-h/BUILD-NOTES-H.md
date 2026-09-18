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
  `SCRIPT-H-*` files, `evidence/`, `sound/`, `host/` and `packaging/` before the build and asserts them
  unchanged after it.
- This build was never served and no frozen copy was made (the parent's, E99 s75 / R26-193).
