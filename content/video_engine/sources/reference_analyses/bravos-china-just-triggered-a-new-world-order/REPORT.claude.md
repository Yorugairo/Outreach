# PRODUCTION REFERENCE REPORT (Claude, 2026-09-10): China Just Triggered A New World Order

- **Source:** `https://youtu.be/1ZS5_txbOsc` - Bravos Research, 19:56.5 (1196.5 s), 1280x720 av1, 29.97 fps
- **Transcript:** native captions, deduped (YouTube's rolling windows repeat lines): **3542 words, 177.6 WPM** over the runtime
- **Visual events:** 120 (6.0/min) - of which **50 new compositions (2.5/min)** and 70 builds inside a held composition
- **Sponsor:** 06:33.0-07:08.0 (35 s) inside P3, on its own maroon ground; the CTA is the last 41 s

## The distribution (doc 46's table, recomputed here)

| | events (cuts + builds) | compositions (cuts only) | WL reference (doc 46) |
|---|---|---|---|
| per minute | 6.0 | 2.5 | 5.9 |
| mean | 10.0 s | 23.9 s | 10.1 s |
| median | 5.9 s | 16.6 s | 9.6 s |
| Q1 / Q3 | 3.3 / 12.4 s | 8.8 / 34.1 s | 6.3 / 13.2 s |
| IQR | 9.1 s | 25.3 s | 6.9 s |
| longest | 54.2 s | 112.0 s | 26.0 s |
| shortest | 0.2 s | 1.0 s | 1.6 s |
| >= 6 s | 50 % | 84 % | 80 % |

**The finding:** the picture changes six times a minute, the composition only two and a half. The 'clean' feel is
builds inside a held frame - a card lands, a line draws, a country lights, one node swaps - not cutting. Their cut
rate is well under the WL reference's; their event rate matches it. This is E21 (never still) answered by BUILDS, and
E50's deployed clock answered by a composition that keeps earning its hold.

## Screen time by lane

| lane | seconds | share |
|---|---|---|
| own | 959 | 80 % |
| external | 157 | 13 % |
| cta | 41 | 3 % |
| sponsor | 40 | 3 % |

external = other people's claims (press cards, news clips) - always framed on the TV or as a stacked card; own = Bravos' analysis on the bare black stage.

## The six phases (the house grid; words from the deduped captions)

| phase | window | events | compositions | words | WPM |
|---|---|---|---|---|---|
| P1 The Open | 00:00.0-01:30.0 | 23 | 11 | 273 | 182 |
| P2 The Engine | 01:30.0-03:23.4 | 10 | 4 | 348 | 184 |
| P3 The Gap | 03:23.4-08:58.4 | 22 | 12 | 976 | 175 |
| P4 The Pivot | 08:58.4-10:58.1 | 12 | 5 | 349 | 175 |
| P5 The Payoff | 10:58.1-16:57.1 | 32 | 11 | 1049 | 175 |
| P6 The Close | 16:57.1-19:56.5 | 21 | 7 | 547 | 183 |

Gemini's report gave 214-249 WPM per phase against a 177.7 total - the rolling caption windows counted twice (4,530 words for a 3,543-word take). The honest phases run near the mean.

## The grammar (what the frames say; what it maps to in our engine)

1. **One stage, one accent.** Near-black charcoal, one pink, white type; green only for 'up' and the CTA. Titles top-centre in the accent; a small source line bottom-left (`Data: ... Source: ..., Bravos Research`). -> our brand tokens already say this (charcoal 60 / chalk 30 / coral+sunflower 10); we use two accents, they use one.
2. **Other people's claims are framed; their own analysis is bare.** The first 1:40 plays entirely on a TV in a dark room (articles, news clips); the moment the argument is theirs the TV is gone and the stage is black. -> a WORLD plate for the external lane (`tv-embed`) we do not have; our docks could carry it.
3. **The press card is their proof species.** A real screenshot cropped to the headline, the key phrase underlined in the accent, cards stacking one at a time with the newest lit (shots 5-10, 16-19, 94-98, 111). -> our `record document` species is the typewriter; a `press-card` dock (still + underline callout) is the missing sibling.
4. **Charts draw and name themselves at the end.** Lines draw left-to-right, the subject series in pink, context grey; TERMINAL TAGS (pill labels at the line ends, 99-104) - exactly E53's 'named at its end'; the value bars at the line ends (104) then become the next chart (105). -> we have the terminal tag; the line-end-to-bar handoff is a morph we have (P47 T3).
5. **The ring is a dashed ellipse on the datum** (38-41: the final drop of China's imports, with a flag chip beside) - E56's one allowed use, done as a dashed oval, not a circle. -> our callout ring; consider the dashed ellipse form.
6. **Ranked bars race and stamp** (50-55: SPR by country; China's bar runs out, `1,405` in a pink capsule, a dotted rule). -> our story bars + the E53 reference rule.
7. **The map is a live vector stage** (31, 57-80): countries light in pink/white as named, dashed arcs with X's for blocked flows, year stamps as pink tags, a B/W figure cutout (Clinton), a figure stamp on a country ('1.4 Billion Barrels'). -> our crossings map is a painted plate with hop traces; a `vector map` species (SVG world, lit countries, arcs) is the gap.
8. **Diagrams are dashed boxes of icon chips joined by arrows**, and the SAME diagram is reused with one node swapped (82-86: Arab Oil States -> China) - the rhyme as a visual. Span brackets ('Decades', 107-110). -> our `bracket` exists; a `flow-diagram` species (chips + arrows + a swap) is the gap.
9. **A numbered agenda** ('China's Gameplan' 1 | 2, revealed in turn, 81/87) sets the second half. -> a stage caption device we could do with figures.
10. **The treemap with X marks** (89-91: exports by partner, partners crossed out) is a part-to-whole we have not built (E53 s7 has the donut exception; the treemap is a second one worth a ruling).
11. **Motion is restrained:** slow pushes on the map between countries, a drift on the TV mock, chart draws; no host, no camera shake, no particles. Nothing is ever still and nothing ever spins. **Measured 2026-09-10 (`claude-watch/camera.json`, ORB+RANSAC similarity between frames 2 s apart per held composition):** 37 of 45 held compositions (>= 3.2 s) are camera-still (< 0.15 %/s zoom, < 4 px/s pan); every chart (11 of 12) and every diagram (4 of 4) is; the camera moves on the MAP (one push, three pans - between countries, once per composition, then still) and as a slow push on the press collage (+1.25 %/s). The "camera stuff" a viewer feels is the builds under a locked camera and the cuts, not the camera. -> P49 amended: LOCKED is the default; the move is for a stage wider than the frame or a landing.
12. **Sound:** a continuous narration at 178 WPM with no pauses for effect; the sponsor block is the only tonal break.

## Gemini's un-filed summary, mapped (the operator's paste, 2026-09-10)

The operator: *"Did all of this make it into gemini's docs? sometimes i think it's best work is the summary that it doesn't
write into the doc."* It did not - Gemini's `REPORT.md` is the pacing table. The paste is filed verbatim as
[GEMINI-CONVO-2026-09-10.md](GEMINI-CONVO-2026-09-10.md). Its five techniques and six formulas, each checked against the
frames (`claude-watch/`), the camera measurement (`camera.json`) and our record:

| Gemini's claim | checked | ours |
|---|---|---|
| **1. The diegetic studio display stage** - articles on a monitor in a lit concrete studio, perspective warp, card shadows, a micro camera pan-and-drift; the maths: a 3x3 planar homography (or `perspective(1200px) rotateY(-4deg) rotateX(2deg)`), four depth layers (wall -100 / bezel -20 / content 0 / callouts +40), `Camera_X(u) = A sin(wu)` for parallax | TRUE (shots 2-10, 16-19: the TV lane) | ABSENT - the `tv-embed` world (§2 above); the maths is small (a CSS perspective transform per layer + one sine pan) and lives nowhere in the record. **BACKLOG R26-32.** Note E49 retired parallax as the blunt cure for stillness; here it is a WORLD, not a cure |
| **2. Isometric 3D metaphor staging** - a 5x5 array of oil silos on a dark-glass dock; satellites glide in from the top corners with cone beams; "at 08:22 the camera tracks left to reveal an underground cross-section card" | the array and the satellites: TRUE (8:20-8:24: the silos, two satellites entering, the cutaway card). The track-left: **NOT in the frames** - composition 53 (8:19.0-8:25.8) is still (pan 0 px/s, zoom 0), the card is already standing at 8:20; it was a CUT from the bar chart (52) | ABSENT - the count array (§2, "the isometric icon array"); the satellites are a species of their own (an object arriving on an icon array with a beam). The cutaway card is a second dock beside it - we have that (two cards up at once, today's read->park) |
| **3. The dual-lane synchronized stage** - left a coordinate line graph (production vs consumption), right a 3D dark map of Hormuz with radial sonar rings and flag pills; the maths: `Viewport_A [0, 0.52 W]`, `Viewport_B [0.52 W, W]`, one clock; the ping `r(t) = r_max ((t - t0) mod T) / T`, `alpha = 1 - r / r_max` | TRUE (shot 28) | PARTIAL - the split stage exists as of today: a PARKED chart beside a docked card on one clock (Tokyo row 4: the ten-year bars at 0.52 with the record beside). The map lane is the vector-map gap (§2 #7); the sonar ping is a species we do not have (a `ping` at a point: radius + alpha on a period). **BACKLOG R26-33** |
| **4. The scale-break asymmetry payoff** - China's blank teasing bar; on the number the chart boundaries expand and the bar shoots past the 500M and 1,000M lines to 1,397M with a glowing callout and a vertical drop-down guide; the maths: `X_max(u) = X_base + (X_expanded - X_base) springPop(u, Mp = 0.08)`, `x(v, u) = x0 + width v / X_max(u)` - the other bars compress as the domain expands | TRUE (8:01.8-8:03.2, measured frame by frame; the capsule counts 1,397 -> 1,405) | **BUILT** today as E60's burst - the same law (the scale rewrites under the shoot; the honest bars shrink). Two differences worth keeping in the record: Gemini puts the overshoot on the DOMAIN (Mp 8 %), we put 5 % on the BAR; and Bravos's "?" placeholder track, the axis-mounted value capsule and the dotted leader are the unbuilt furniture (§2 #6) |
| **5. Volumetric neon bloom on the yield lines; pinheads and country pills stuck to the drawing tip; "at 17:15 the camera pushes into the Western yields while the background blurs out (DoF), then zooms back out"** | the bloom and the tip pills: TRUE (17:08-17:22: four glowing lines, the pills at the ends, a flow diagram beside). The DoF push-in: **NOT in the frames and not in the measurement** - composition 99 (16:45.0-18:00.8, 75.8 s) is still (zoom 0, pan 0); at 17:26 the chart DISSOLVES into a new single-line chart, which is what a sampler reads as "blur then zoom back". E59's count stands: zero of the chart holds carry a push | the bloom: a two-pass stroke (halo + hot core) or `feGaussianBlur + feMerge` - **by ruling not ours** (E22: chalk on charcoal; the burst's glow is the one bloom we use, a dial). The tip pill: PARTIAL - our dense line draws with a tip head and names each series at its end (E53); a pill that RIDES the tip during the draw with a leader is the addition. **BACKLOG R26-34**. The rack focus was ruled against on ep1 ("wash beats the focus rack", doc 29 §9.27) |
| the maths in common | `P_tip(u) = P_k + (uN - k)(P_k+1 - P_k)` (the fractional tip); `springPop(., Mp = 0.05)` for a badge's pop; the domain spring | all BUILT: `stroke.mjs` (arc-length reparameterisation, the tip interpolated), `spring.mjs` (`springPop`, the POP preset Mp 4 %), E60's `lpPaintBreakthrough` |
| "9.97 s mean shot (6 CPM) is the gold standard" | the mean is the 5.7 s sampler's artifact | REJECTED (doc 46 §46.7: events 6.0/min, compositions 2.5/min; medians 5.9 s / 16.6 s) |
| "your custom stateless player ... O(1) seek-safety, zero integrator drift" | a description of our engine, correct | the doc 42 law (§42.2: closed-form, never integrated) |

What the paste adds that the record lacked: the studio display stage as a technique (homography + layers + a sine pan), the
sonar ping, and the tip-riding pill. What it gets wrong: two camera moves that the frames do not contain. The
difference detector and the per-composition camera measurement are why we can say so.

## Artifacts

- `SHOT_LEDGER.claude.md` - every event with its species and line; `claude-watch/shots/` - one frame per event (0.5 s after) and ten contact sheets
- `claude-watch/cuts.json` (event times), `claude-watch/d1.npy` (the per-sample difference), `claude-watch/transcript.json` (deduped captions)
- Gemini's `REPORT.md` / `SHOT_LEDGER.md` / `frames/` are kept as its own artifact; its shot times are a 5.7 s sampler, its species empty, its phase word counts doubled.
