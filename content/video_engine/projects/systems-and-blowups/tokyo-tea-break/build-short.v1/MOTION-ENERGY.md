# Motion energy - tokyo-tea-break

`E = integral |v|^2 dt`, sampled from the built `player.html` at **15 fps** (0-88.823 s, 1333 frames, DOM depth <= 4), measured in 30.1 s.

Reference: **0.22** - ANSWERS-RESEARCH-BRIEF-animation-craft.md A6 - invented, reclassified in 47-FINDINGS-TO-CHECKS.md:146. It is a starting reference, not a threshold; a scene over it is a question, not a failure.

The template carries no `data-motion` attributes, so motion is discovered by change detection on each element's bounding-box centre and effective opacity. Opacity energy is reported separately: a fade is motion to the eye but not translation.

## 1. Whole screen

| | E_primary | E_secondary | ratio | reference | difference |
|---|---:|---:|---:|---:|---:|
| translation (px^2/s) | 1,050,345,224.4 | 27,050,074.5 | **0.026** | 0.22 | -0.194 |
| opacity (1/s) | 752.5 | 1,806.8 | **2.401** | 0.22 | 2.181 |

## 2. Per scene

| scene | span (s) | E_primary | E_secondary | ratio | vs 0.22 | movers mean/max | max step (px) |
|---|---|---:|---:|---:|---|---:|---:|
| s01 | 0.00-5.09 | 0.0 | 64,707.3 | **-** | - | 1.3 / 5 | 36 |
| s02 | 5.09-8.99 | 2,666,017.2 | 96,274.5 | **0.036** | under | 1.3 / 6 | 221 |
| s03 | 8.99-17.17 | 2,672,457.9 | 12,507.1 | **0.005** | under | 1.3 / 5 | 207 |
| s04 | 17.17-33.05 | 413,468,760.8 | 6,618,514.2 | **0.016** | under | 4.0 / 37 | 833 |
| s05 | 33.05-38.96 | 2,666,007.9 | 57,198.2 | **0.021** | under | 1.5 / 4 | 227 |
| s06 | 38.96-44.88 | 733,115.8 | 19,589,943.2 | **26.721** | OVER | 9.7 / 18 | 203 |
| s07 | 44.88-54.52 | 619,455,226.2 | 369,126.3 | **0.001** | under | 6.6 / 51 | 830 |
| s08 | 54.52-61.76 | 2,667,538.2 | 5,447.4 | **0.002** | under | 1.6 / 5 | 227 |
| s09 | 61.76-75.73 | 3,350,092.4 | 194,114.3 | **0.058** | under | 10.3 / 66 | 52 |
| s10 | 75.73-82.62 | 2,666,007.9 | 42,212.0 | **0.016** | under | 1.5 / 5 | 227 |
| s11 | 82.62-88.82 | 0.0 | 30.0 | **-** | - | 0.3 / 3 | 1 |

`max step` is the largest single-frame centre displacement in the scene - the tell for a re-layout counted as motion. A rebuilt subtree jumps once; a real move spreads over consecutive frames.

## 3. Per piece (top 25 by translation energy)

| element | class | label | E_trans | E_opacity | frames moving |
|---|---|---|---:|---:|---:|
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:5` | lab | PRIMARY | 158,038,161.4 | 30.00 | 48 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:4` | lab | PRIMARY | 132,522,055.7 | 15.00 | 33 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/path.ser:15` | ser | PRIMARY | 110,777,242.4 | 15.00 | 33 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:2` | lab | PRIMARY | 95,793,902.0 | 15.00 | 33 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:6` | lab | PRIMARY | 93,683,741.3 | 15.00 | 35 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/line.grid:3` | grid | PRIMARY | 67,965,976.5 | 15.00 | 31 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:11` | lab | PRIMARY | 65,982,199.9 | 15.00 | 34 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:7` | lab | PRIMARY | 54,889,624.4 | 30.00 | 46 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:10` | lab | PRIMARY | 36,036,725.9 | 15.00 | 33 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:8` | lab | PRIMARY | 29,650,475.9 | 15.00 | 33 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.sname:17` | sname | PRIMARY | 28,144,316.6 | 3.53 | 33 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/text.lab:9` | lab | PRIMARY | 22,578,236.5 | 16.62 | 46 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/path.ser:12` | ser muted | PRIMARY | 18,706,230.8 | 15.00 | 36 |
| `/#seam` | div | PRIMARY | 16,009,070.2 | 180.00 | 50 |
| `/#wB/div.lp:0/div.lp-page:0/svg.lp-chart:6/line.ax:0` | ax | PRIMARY | 11,180,070.9 | 30.00 | 29 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:4` | w | PRIMARY | 3,401,988.9 | 0.75 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:3` | w | PRIMARY | 3,376,172.3 | 0.75 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:0` | w | PRIMARY | 3,376,035.3 | 0.75 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:1` | w | PRIMARY | 3,358,905.4 | 0.75 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:3/span.w:2` | w | PRIMARY | 3,358,475.8 | 0.75 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:3` | lp-ink lp-title | PRIMARY | 3,350,040.8 | 0.75 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:0` | w | PRIMARY | 3,324,709.1 | 0.48 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:6` | w | PRIMARY | 3,320,010.9 | 0.48 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:5` | w | PRIMARY | 3,319,377.9 | 0.48 | 42 |
| `/#wB/div.lp:0/div.lp-page:0/div.lp-ink:4/span.w:1` | w | PRIMARY | 3,309,565.5 | 0.48 | 42 |

## 4. The read

Whole-screen secondary/primary translation ratio is **0.026** against the 0.22 reference (under it). 1 of 11 scenes exceed it: s06 (26.721). The pieces that dominate are `text.lab:5` (PRIMARY, 158,038,161), `text.lab:4` (PRIMARY, 132,522,056), `path.ser:15` (PRIMARY, 110,777,242), `text.lab:2` (PRIMARY, 95,793,902), `text.lab:6` (PRIMARY, 93,683,741). Read the ratio as a description of this build, not a verdict on it - the number it is compared against was invented, and the point of measuring is to replace it with one derived from our own footage and the references (BACKLOG X2).

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

Scenes measuring `E_primary = 0` here: **s01, s11**. Read that as "no primary DOM element translated", never as "nothing moved" - check the scene's world layer before drawing any conclusion from it.
