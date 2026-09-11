# Exploration review — what techniques and maths are still unexplored (2026-09-10)

The operator: *"review the backlog and exploration docs - what techniques / maths do we still have to explore? Did you
pull all of the math gemini referenced from the bravos doc?"* This is the answer, with the record cited at every row.
The three sources reviewed: the Bravos dossier (Gemini's `REPORT.md` / `SHOT_LEDGER.md` and our `REPORT.claude.md`),
[BACKLOG.md](BACKLOG.md) (every open row), and the exploration layer (docs 42–49, the intakes HF / MC / RU / TR / the ink
bloom, the research briefs under `docs/research/`). `scripts/check_research_extraction.py` PASSES: every heading of the
research bundle's ten primaries has a disposition (RESEARCH-INDEX), so the bundle's maths is accounted for; what is
NOT yet built from it is listed in §3.

## 1. The Bravos maths — what Gemini's dossier carries, and what we took

Gemini's `REPORT.md` is a **pacing report**, not a motion report. Everything numeric in it:

| Gemini's figure | value | our disposition |
|---|---|---|
| total cuts / rate | 120 cuts, 6.02 CPM | re-measured by us as EVENTS (cuts + builds) 6.0/min vs COMPOSITIONS 2.5/min - doc 46 §46.7; the difference detector is the finding Gemini's sampler could not make |
| mean shot | 9.97 s | ours: events median 5.9 s, compositions median 16.6 s (§46.7). Gemini's shots are a 5.7 s sampler (`REPORT.claude.md` Artifacts) - the mean is an artifact of the sampler |
| shot distribution | <3 s: 2 · 3-8 s: 63 · 8-15 s: 38 · >15 s: 17 | superseded by our Q1/Q3/longest per kind (§46.7) |
| speech | 3543 words, 177.7 WPM | carried (`REPORT.claude.md` §12: 178 WPM, no pauses) |
| per-phase WPM | P1 249 · P2 234 · P3 215 · P4 234 · P5 224 · P6 238 | **REJECTED, same fault as Wealth Logic's** (RESEARCH-INDEX conflict 4): every phase reads above the whole's 178 WPM, which is the caption over-count (rolling carryover). The phase *boundaries* are usable; the WPMs are not |
| the six phase windows | P1 0:00-1:30 · P2 1:30-3:23 · P3 3:23-8:58 · **P4 8:58-10:58 (45-55 %)** · P5 10:58-16:57 · P6 16:57-19:57 | **NOT carried until today** - now in doc 46 §46.7: Bravos's pivot sits at 45-55 % of the runtime, the FULL-VIDEO-MAP's chiastic turn, confirmed on a second reference |
| species per shot | `unclassified` × 120 | empty in Gemini's ledger; ours classifies every event (`SHOT_LEDGER.claude.md`) |

So: yes - the maths Gemini referenced in the Bravos doc is pacing arithmetic, and all of it is either carried,
re-measured better, or rejected with the reason written. The motion maths of the reference layer (springs, stroke
reparameterisation, Kubelka-Munk, ARAP, disocclusion, the figure rig) came from the research BUNDLE, not from the
Bravos doc, and the extraction check says every heading is dispositioned. What Bravos itself gave us that is *not*
built is a set of SPECIES (§2, from `REPORT.claude.md`'s grammar), not maths.

## 2. Bravos's species we have not built (from `REPORT.claude.md` §"The grammar")

| # | Bravos mechanic | what it needs | status |
|---|---|---|---|
| 3 | **the press card** - a real screenshot cropped to the headline, the key phrase underlined in the accent, cards stacking one at a time with the newest lit | a `press-card` dock: still + underline callout + the stack-with-newest-lit law (our `stack` species is the burst-clear pile; this is the quiet stack) | ABSENT as a species; the record dock is its typewriter sibling |
| 2 | **the TV-embed world** - other people's claims framed on a TV in a dark room; their own analysis bare | a world plate (a TV mock with a drift idle) the external lane's docks land in | ABSENT |
| 7 | **the live vector map** - countries light as named, dashed arcs with X's for blocked flows, year stamps as pink tags, a B/W figure cutout, a figure stamp on a country | a `vector-map` species (SVG world, per-country paths, the light-on-name law, arc + X, the stamp); the camera's one-move-per-composition push between countries is BUILT (P49 keys) | ABSENT (our crossings map is a painted plate with hop traces); RU-3's map-flight rejected for the runtime, so this is an SVG job |
| 8 | **the flow diagram** - dashed boxes of icon chips joined by arrows, the SAME diagram reused with one node swapped | a `flow-diagram` species: chips + arrows + the swap-one-node transition (the rhyme as a visual) | ABSENT; `bracket` covers the span brackets only |
| 6 | **the burst's furniture** - the "?" placeholder track, the value capsule counting up ON THE AXIS under the bar's end, the dotted leader from the bar's end to the axis | on top of E60's burst (BUILT today): a placeholder state before the reveal, the capsule as an axis-mounted callout, a dotted leader (we have the offset-annotation leader on lines) | PARTIAL - the burst and the rescale are built; the three ornaments are not |
| 10 | **the treemap with X marks** - exports by partner, partners crossed out | a part-to-whole form; E53 §1 holds ONE exception (the share/donut under four bounds) - a treemap needs its own ruling before code | ABSENT, needs a ruling |
| 4 | **line-end tags become the next chart's bars** (the terminal tags -> value bars -> the next chart) | a keyed recast pair (dense-line -> story) with the TAGS as the keyed marks; today's keyed pairs: `RECAST_PAIRS = (("dense-line","story"),)` keyed on the datum | PARTIAL - the keyed recast exists; keying on the terminal tag is a small extension |
| 5 | **the dashed ellipse on the datum** (the ring's form) with a flag chip beside | a `ring` form dial (dashed ellipse vs circle) + a chip | PARTIAL - the ring exists (E56's one use); the dashed-ellipse form and the chip do not |
| 9 | **the numbered agenda** ("China's Gameplan" 1 \| 2, revealed in turn) | a stage caption device: numbered figures revealed on their words | ABSENT; `figure` + `note` could compose it |
| (7:43) | **the isometric icon array** (the silos: a field of identical icons stacking up on a tilted plate) | a `count-array` species: N icons placed on an isometric grid, arriving in reading order, the count as the claim | ABSENT |
| 11 | **restraint, measured** - 37/45 held compositions camera-still; the map push once per composition; one slow push on a stacking collage | BUILT: E59 (LOCKED default, the four reasons a camera moves), M24; the Tokyo cut carries the pull + the arrival ("8742>8738") | BUILT |
| 12 | 178 WPM, no pauses; the sponsor block the only tonal break | doc 46; the take standard (E38/M13) | RECORDED |

## 3. The open backlog — the technique or maths each row needs

| row | needs | maths already on disk? |
|---|---|---|
| R26-13 M18 per layer | a per-layer frame hash (the page layer alone) so a frozen page under a boiling caption is seen | none needed - `measure_frozen_frames.py` gets a layer mask |
| R26-15 the HyperFrames harvest (12 components verbatim) | references to lift by hand, each against a beat | the harvest doc; no maths |
| R26-16 the morph's source is a planted element (the tie) | planting a real element of the outgoing world per scene, a seam's length, never on a mount; the ARAP path exists | `arap.mjs` BUILT (P47 T3); the planting is authoring + a compiler check |
| R26-20 badge-stamp's two-spring landing (RU-2) | a clamped scale spring plus a FREE trailing rotation spring on the stamp - the offset is the weight cue our single-spring landings lack | `spring.mjs` (`springPop`/`springEval`) has the closed-form spring; the second (rotation) spring and its trailing offset are the addition |
| R26-21 a cold seek into a snap / arrival window | one impure first frame after a cold seek (the card box is read from the dock loop's layout) | a closed-form box (the compiler's `place`, or `read_place` now) instead of the DOM read - the read->park's `read_place` is the same idea |
| R26-22 centred placement by E50's clock | a solo card centred by the chart's deployed clock instead of the reading rect over the title | `_page_land_offset` + E50's marks in the gate; a compiler rule |
| R26-24 N-tier pages (MC-7) | three bands, one x, one unit each - the general form of `tiers` (N = 2 built) | `tiers` BUILT for 2; the layout generalises |
| R26-25 the `span` species (MC-9) | a shaded region with a label behind a line (regime / epoch shading), with stage brackets | `bracket` BUILT; a shaded span is a rect + label on the page's scale (`lpRuleYNow`-style follow) |
| R26-27 page_boxes vs the player's layout | `centred_place` and the player disagree on a portrait page's band y (1250 vs 536) | the fix is one source of truth for the page's bands (the player's `page_boxes` measured once); no maths |
| R26-29 the breakthrough object's as-of date | read the printed quarter-end off the iShares fact sheets | none |
| R26-30 the breakthrough BLEND | the burst on `stopaction.mjs`'s frame-index cadence: the bar and the counter step together, the scale rewriting stepwise, the glow on the landing frame | `stopaction.mjs` cadence + `lpPaintBreakthrough` BUILT today; the blend is their composition |
| TR-7 the ARAP match cut as GATES | the three invariants (centroid <= 0.06 W, axis <= 15 deg, area ratio >= 0.60) checked before a morph is allowed | `arap.mjs` computes the oriented bounding area / inertia axis; M17 measures the morph; the invariants as a compiler refusal are the gap |
| TR-8 M13 into the registry; the log-normal shot-length check; the carried-light luminance check | three settled rules with no gate | doc 46 §46.1's distribution (keep the median, grow the tail); a luminance sampler |
| TR-9 the wipe-onto-stable-cream mount (E45 mount (a)) | a second mount code path: the world wipes onto a standing cream page | the wipe + the mount both exist; the branch is the work |
| TR-10 the older continuity contract (`transition.in: continuous`, motif, one hard cut per act) | retire or implement - a ruling | none |
| TR-11 isolate transition KINDS in retention | an experiment design on later shorts (n = 254 measured worlds, not kinds) | analytics only |
| TR-14 the ink bloom world change | the motion menu's radial reveal with an organic edge (the operator's own source in the intake): a clip-path from a named point + an edge field | `ink.mjs` (seeds, goo) has the organic edge; the reveal is `clip-path: circle()` grown from the point |
| TR-15 the Whisper gate normalises numerals | "a hundred and twenty-two billion dollars" == `$122 billion` before the diff | a numeral normaliser (text); no maths |
| MOTION MENU "not yet" | beat-freeze exit, radial reveal (= TR-14), push hand-off, weight-shift captions | the menu's own four; radial reveal is the ink bloom's parent |
| MC-8 spread / divergence | Archetype 4 | BUILT (the `spread` species, R26-26) - the intake's EXPLORE row is closed in practice; close it in the intake |
| MC-10 yield-curve term structure | Archetype 6 - INDEX only | no beat needs it yet |
| HF-15 arriving, not cutting | the next region visible at the frame edge before the move (a page-to-page arrival from the edge) | the camera's `look`/`at` (P49) can do it now: a key that leaves the next region in frame before the move - unauthored |
| HF-16 the three threads (the wire, the ruler, the protagonist chip) | one continuous element across worlds (the holdings baseline as the wire under the Meta bars) | authoring on the timeline; `extend` (P48 T3) is the wire's engine |
| HF-17 occlusion beats blur as the depth cue | one foreground occluder on a world plate, judged by eye | a compositing layer; the parallax engine (doc 45) has the depth |
| HF-11 text behind the subject with occlusion | spoken keywords as display text behind the cutout figure | a compositing layer in the player (the host cutout over the caption plane) |
| HF-8 / HF-9 the One Breather; `[focal]` / `[roles]` per row | one calm beat per film; the focal entity per shot row | shot-table fields + an INFO row in the gate; feeds D3's reading-order gate |
| HF-12 the encoder-size stillness signal | the last second's encoded size as a corroborating stillness metric | a line in `render_episode.py` + an INFO row; M18 covers the frame hashes |
| HF-18 a shader seam (`sdf-iris`) | only if a world change wants it | deferred by the intake |
| RU-2's `e` restitution | the hop after contact - `stopaction.mjs` carries `e` tagged from the weight brief; the operator has not heard it by ear at the four masses | the number is in the module; the listening is the gap |

## 4. The reference layer's maths not yet built (docs 42–49, all "reference — not yet folded to portable")

| doc | maths | built? |
|---|---|---|
| 42 Drawing kinetics | stroke reparameterisation (arc-length), closed-form springs + the overshoot inverse, squash | BUILT (`stroke.mjs`, `spring.mjs`, `squash.mjs`); **Euler spirals** (the pen's path curvature law) are in the doc and nowhere in the kinetics - unbuilt |
| 43 Scene graph and transform | the anchor sandwich, Z-stack, dirty flags, both morph methods (§43.5: Method A vertex-based - Flubber / d3-interpolate-path with the rotational alignment `argmin_k Σ‖v_A,i − v_B,(i+k)‖²`; Method B ARAP), the cutout rig (§43.6) | Method B BUILT (`arap.mjs`, with the same alignment step in `correspond`); Method A (closed outline shapes, cheap) is unbuilt; the cutout rig is unbuilt by design (the host is a bound Flow character) |
| 44 Ink and surface | Kubelka-Munk, the coffee-ring edge, anisotropic wicking | K-M BUILT (the ink layer), then BOUNDED by E22: the soak is a plate - six filter rounds lost to the alpha film; the wicking/coffee-ring maths stay reference |
| 45 Parallax and plate motion | the disocclusion limit, the viability matrix, multi-plane inpainting, masked ambient motion | the ComfyUI 2.5D engine BUILT; the dial audit (our dials matched no target) was the finding - the viability matrix as a per-plate check is unbuilt |
| 46 Reference rhythm | the distribution (log-normal), the gap threshold (0.30 s at onset), the equation spine, the phase map, Bravos's events-vs-compositions | M13/M16 BUILT; the log-normal shot-length check is TR-8; a compositions-per-minute INFO row (Bravos 2.5/min against our events) is unbuilt |
| 48 The figure and the ground | FK/IK boundary, balance, the rig, idling, reach and grasp, grounding | the host is a bound Flow character (MP host identity) - the in-engine rig is unbuilt by design; grounding lives in `stopaction.mjs` (contact shadow, ground dip) |
| 49 Generative video and the vertical stage | Wan/LTX/depth dials, mask pinning, the mobile safe box | the safe box BUILT (the 9:16 CSS defect it caught); the Wan/LTX dials are the Comfy layout (models hardlinked), not a per-beat capability yet |

## 5. Audio

The sub-threshold bed research (`docs/research/audio/`) triangulated a −22 to −30 LU window (MEDIUM: craft consensus, not
experiments); the operator set −20 LU by ear (E55) and the bed BREATHES +4 dB over thrown cards (`env` keys). Unexplored:
the research's "bed rise toward −18 LU under scene transitions and savor pauses" as an authored envelope law, and any
measurement of the bed against the take's word onsets (a ducking curve). No maths beyond LU arithmetic.

## 6. What I would explore next, in order

1. **The press-card dock** (§2 #3) - Bravos's proof species and the cheapest gap: a still, an underline callout, the quiet stack with the newest lit. Every short we make has an article behind it.
2. **The burst's furniture** (§2 #6): the "?" placeholder state and the axis-mounted value capsule with the dotted leader - E60's burst is built; these finish Bravos's version.
3. **R26-30 the stop-motion burst** - the operator's blend; the two mechanisms exist, the composition is a day.
4. **R26-25 the span species and R26-24 N-tier pages** - the two macro-chart archetypes we still refuse a beat for.
5. **The vector map** (§2 #7) - the largest gap and the one Bravos leans on most; an SVG world with the light-on-name law, arcs and stamps; the camera's map push is already built for it.
6. **TR-7's ARAP invariants as compiler refusals** - the morph is built; the gate that stops a bad match is not.
7. **The treemap ruling** (§2 #10) before any code.
