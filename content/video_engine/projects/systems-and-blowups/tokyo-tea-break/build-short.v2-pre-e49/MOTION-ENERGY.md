# Motion energy - tokyo-tea-break

`E = integral |v|^2 dt`, sampled from the built `player.html` at **15 fps** (0-88.823 s, 1333 frames, DOM depth <= 4), measured in 27.1 s.

Reference: **0.22** - ANSWERS-RESEARCH-BRIEF-animation-craft.md A6 - invented, reclassified in 47-FINDINGS-TO-CHECKS.md:146. It is a starting reference, not a threshold; a scene over it is a question, not a failure.

The template carries no `data-motion` attributes, so motion is discovered by change detection on each element's bounding-box centre and effective opacity. Opacity energy is reported separately: a fade is motion to the eye but not translation.

## 1. Whole screen

| | E_primary | E_secondary | ratio | reference | difference |
|---|---:|---:|---:|---:|---:|
| translation (px^2/s) | 1,307,384,547.1 | 32,999,269.8 | **0.025** | 0.22 | -0.195 |
| opacity (1/s) | 1,588.6 | 1,762.7 | **1.110** | 0.22 | 0.890 |

## 2. Per scene

| scene | span (s) | E_primary | E_secondary | ratio | vs 0.22 | movers mean/max | max step (px) |
|---|---|---:|---:|---:|---|---:|---:|
| s01 | 0.00-3.29 | 0.0 | 25,792.0 | **-** | - | 1.5 / 5 | 29 |
| s02 | 3.29-38.96 | 87,989,848.0 | 7,805,687.0 | **0.089** | under | 1.9 / 36 | 363 |
| s03 | 38.96-44.88 | 555,273,499.9 | 23,049,948.8 | **0.042** | under | 12.0 / 60 | 995 |
| s04 | 44.88-61.76 | 311,196,750.7 | 1,322,775.4 | **0.004** | under | 3.3 / 51 | 830 |
| s05 | 61.76-75.73 | 3,355,421.0 | 752,824.7 | **0.224** | OVER | 11.8 / 97 | 151 |
| s06 | 75.73-81.55 | 335,310,952.9 | 3,495.1 | **0.000** | under | 3.9 / 57 | 863 |
| s07 | 81.55-82.62 | 14,258,074.7 | 38,716.9 | **0.003** | under | 4.1 / 32 | 607 |
| s08 | 82.62-88.82 | 0.0 | 30.0 | **-** | - | 0.3 / 3 | 1 |

`max step` is the largest single-frame centre displacement in the scene - the tell for a re-layout counted as motion. A rebuilt subtree jumps once; a real move spreads over consecutive frames.

## 3. Per piece (top 25 by translation energy)

| element | class | label | E_trans | E_opacity | frames moving |
|---|---|---|---:|---:|---:|
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:5` | lab | PRIMARY | 108,417,585.8 | 30.00 | 35 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:4` | lab | PRIMARY | 88,872,442.7 | 15.00 | 22 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/path.ser:15` | ser | PRIMARY | 74,383,829.2 | 15.00 | 22 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:2` | lab | PRIMARY | 63,575,069.8 | 15.00 | 21 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:6` | lab | PRIMARY | 62,242,230.7 | 15.00 | 21 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:11` | lab | PRIMARY | 44,428,260.6 | 15.00 | 21 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/line.grid:3` | grid | PRIMARY | 41,579,166.1 | 15.00 | 19 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:6` | w | PRIMARY | 38,203,884.2 | 7.68 | 6 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:7` | lab | PRIMARY | 36,676,229.3 | 30.00 | 35 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:4` | w | PRIMARY | 36,196,162.1 | 12.00 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:0` | w | PRIMARY | 35,907,166.0 | 12.00 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:3` | w | PRIMARY | 32,704,663.7 | 12.00 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:1` | w | PRIMARY | 31,515,926.2 | 12.00 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:2` | w | PRIMARY | 30,667,469.0 | 12.00 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:0` | w | PRIMARY | 30,607,274.4 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:3` | lp-ink lp-title | PRIMARY | 29,635,987.8 | 12.00 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:1` | w | PRIMARY | 27,203,171.8 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:5` | w | PRIMARY | 26,127,082.1 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:2` | w | PRIMARY | 25,584,188.7 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:3` | w | PRIMARY | 24,939,675.0 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:7` | w | PRIMARY | 24,806,446.9 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:4` | w | PRIMARY | 24,731,590.3 | 7.68 | 6 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:10` | lab | PRIMARY | 23,627,271.7 | 15.00 | 22 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:8` | w | PRIMARY | 23,368,236.5 | 7.68 | 6 |
| `/#wA/div.lp:0/div.lp-page:0/div.lp-ink:4` | lp-ink lp-sub | PRIMARY | 23,195,129.4 | 7.68 | 6 |

## 4. The read

Whole-screen secondary/primary translation ratio is **0.025** against the 0.22 reference (under it). 1 of 8 scenes exceed it: s05 (0.224). The pieces that dominate are `text.lab:5` (PRIMARY, 108,417,586), `text.lab:4` (PRIMARY, 88,872,443), `path.ser:15` (PRIMARY, 74,383,829), `text.lab:2` (PRIMARY, 63,575,070), `text.lab:6` (PRIMARY, 62,242,231). Read the ratio as a description of this build, not a verdict on it - the number it is compared against was invented, and the point of measuring is to replace it with one derived from our own footage and the references (BACKLOG X2).

## 5. Classification table (declared, not guessed)

| name | kind | label | why |
|---|---|---|---|
| `world` | class | PRIMARY | the world/plate layer - #wA/#wB, the beat's ground |
| `clipv` | class | PRIMARY | the generative clip filling a world layer |
| `seam` | id | PRIMARY | the cross-reveal wipe front (29 s9.15) - the transition IS the beat |
| `lp` | class | PRIMARY | the ledger page mount |
| `lp-page` | class | PRIMARY | the ledger page build/retract/spiral (E22) |
| `lp-field` | class | PRIMARY | the page field the ink lands in |
| `lp-edge` | class | PRIMARY | the deckle edge - it arrives with the page (E22) |
| `lp-ink` | class | PRIMARY | page ink write-on (title/sub/src) - part of the page build |
| `w` | class | PRIMARY | an ink word inside .lp-ink (its `.g` glyphs are depth 5) |
| `lp-chart` | class | PRIMARY | the chart - proof of one sentence (E25) |
| `ser` | class | PRIMARY | a chart series path, drawn on |
| `bar` | class | PRIMARY | a chart bar, grown |
| `ax` | class | PRIMARY | chart axis |
| `grid` | class | PRIMARY | chart gridline |
| `lab` | class | PRIMARY | chart axis label - it reads at a glance with the chart (E28) |
| `val` | class | PRIMARY | a bar's value, drawn with the bar |
| `sname` | class | PRIMARY | a series name, drawn with the series |
| `dock` | class | PRIMARY | the evidence dock - the carrier of the scene's evidence (29 Part 8) |
| `slide-frame` | class | PRIMARY | the dock's frame |
| `i1` | id | PRIMARY | dock 1 evidence image |
| `i2` | id | PRIMARY | dock 2 evidence image |
| `caption` | id | SECONDARY | the caption block - captions ARE the motion, but they ride the beat |
| `cg` | class | SECONDARY | a caption phrase group |
| `cw` | class | SECONDARY | a caption word - pop / lift / boil |
| `pill` | class | SECONDARY | a badge pill |
| `pill-label` | class | SECONDARY | badge label |
| `pill-row` | class | SECONDARY | badge row |
| `pill-num` | class | SECONDARY | badge number |
| `pill-tag` | class | SECONDARY | badge tag |
| `cpill` | class | SECONDARY | a chart callout badge |
| `callout` | class | SECONDARY | a chart callout label |
| `species` | id | SECONDARY | species life (41-LEDGER-PAGE-SPECIES) |
| `plife` | id | SECONDARY | plate life - boil / jitter |
| `lp-grain` | class | SECONDARY | paper grain boil on the page |
| `lp-rail` | class | SECONDARY | the page rail accent |
| `rail` | class | SECONDARY | a dock rail accent |
| `wash` | id | SECONDARY | the atmospheric wash - a full-stage opacity layer |
| `spot` | id | SECONDARY | the spotlight (M11) - a full-stage opacity layer |

## 6. Unclassified

None - every element under `#stage` resolved to PRIMARY or SECONDARY.

## 7. What this measurement cannot see

This is DOM geometry, not pixels. Four kinds of on-screen motion are invisible to it:

1. **Motion inside a `<video>`** - a generative clip filling a world layer has a fixed bounding box, so a scene carried entirely by clip motion measures `E_primary = 0`.
2. **Motion inside a raster plate or canvas** - the same reason.
3. **Shape change that leaves the bounding-box centre where it was** - a symmetric grow, a boil, a colour or stroke-width change.
4. **Motion across a content swap** - when an element's text or `src` changes, identity is reset and the step is dropped, because a caption page turning over is a cut, not a pan.

Scenes measuring `E_primary = 0` here: **s01, s08**. Read that as "no primary DOM element translated", never as "nothing moved" - check the scene's world layer before drawing any conclusion from it.
