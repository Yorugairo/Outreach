# Transitions — the review (2026-09-06)

The operator: *"I think we should review our research on transitions also, I don't think we've gotten them nailed properly."*
Prompted by the Tokyo short's retention (`../../content/video_engine/projects/systems-and-blowups/tokyo-tea-break/ANALYTICS-2026-09-06.md`,
n = 254): every bleed is a clip-to-clip cut, every plateau a ledger page. This page holds the parent's judgment (§1) and the
explorer's inventory of what the corpus actually says and what the player actually paints (§2–§5, verbatim from the recall, cited).

## 1. The judgment

**The research asked the right questions and mostly did not answer them.** The research brief's Track B (`briefs/RESEARCH-BRIEF-animation-craft.md:163`)
asked about the gap cut, the reset cost of a cut, J/L-cuts under continuous narration, graphic match cuts and rhythm as a
distribution. Its own status table (`:118-140`) records: B1 "no external measurement exists; ours is original"; B3 "the only
question no pass has touched"; B4 the perceptual half unanswered; B2 answered by a rhythm measurement that is not a reset-cost
measurement. "Cut on action", "invisible cut", Murch as a check: zero hits. The transitions we ship were designed by feel against
a research layer that said "unmeasured".

**The one reference measurement we hold is cadence and placement, not kind.** Wealth Logic cuts 5.9 times a minute and lands
72–81 % of cuts inside a ≥ 0.30 s gap at 0.8 of the gap (doc 46). But the 100-cut shot ledger classifies every row
`unclassified` and never names a transition type (§2 below). We do not know whether the reference dissolves, wipes, cuts, or
carries its evidence across boundaries. E38 says measure the reference first with the same tool; for transitions we never did.

**Several shipped transition numbers have no source** and no `[DERIVED]` tag (E42 D6 requires one): the suck's 0.3 s and 240°,
the dissolve's 0.8 s (the slowest thing we ship, against doc 29's "every transition well under a second" and the reference's
0.35 s), the mount's 5 steps and 28 px rise, the dock choreography's 0.45 / 1.2 / 0.7 / 0.35. Min-jerk, which the FINDING doc
endorses for transitions, is a kinetics flag that defaults to off, so the wipe and the dissolve run quart-in-out.

**Load-bearing pieces of our own grammar are unbuilt.** The beat-freeze chart exit is doc 29's default way to leave a page
mid-proof (`29:1841`) and is not built (`29:1770`), so pages leave by spiral, cut or wipe. The radial reveal, the push hand-off
and the book-flip are in the menu and unbuilt. J/L-cut offsets exist as a design proposal and nothing in the compiler offsets
picture from the sentence. The ARAP match cut - the metaphor becoming the chart, the one transition no stick-figure channel can
copy - is Tier 1 maths with no implementation.

**Two contradictions need a ruling.** Doc 51 §51.4 (2026-09-03) puts dissolves and Ken Burns IN and everything from docs 42–44
OUT for shorts; the Tokyo short and E44/E45 (2026-09-06) do the opposite and the curve rewards it. And the older lane's contract
(`06-SCRIPT-TRANSFORMATION-SPEC.md:99-110`: `continuous` by default, one hard cut per act) has no implementation and no
retirement note beside M16's 2.5 s pulse.

### What to do, in the operator's order (recent stumble → TOP; unbuilt → BACKLOG; unmeasured → EXPLORE)

| id | item | why | cost |
|---|---|---|---|
| **TR-1 TOP** | **Classify the reference's 100 cuts by transition kind** — cut / dissolve / wipe / push / continuous (evidence enters, world persists) / zoom-through, from the keyframe pairs in `bundle/04_shot_ledger_100_cuts.md`; add the share and the per-kind gap placement to doc 46 | E38: the reference first. We hold cadence and gap placement and nothing on kind. The first live order for the Gemini lane through the bridge (a `report-landed` packet) | one vision pass over 100 keyframe pairs |
| **TR-2 TOP** | **Measure the voice-to-picture offset on the reference** (the J/L-cut question, B3): for each of the 100 cuts, the signed offset between the cut and the nearest sentence boundary from the Whisper word times `measure_cut_gaps.py` already reads; the distribution, not the mean | the only research question no pass touched; the mount is already an L-cut by construction and we do not know if the reference does it | a Python pass over data on file |
| **TR-3 TOP** | **Tag and test the unsourced transition numbers** — `SUCK_S`, `SUCK_TURN`, `DISSOLVE_S`, `MOUNT_STEPS`, `LP_MOUNT_RISE`, `DOCK_POP_S/READ_S/PARK_S`: `[DERIVED]` tags at the constants; dissolve tested at 0.35–0.5 against 0.8 (doc 29's own rule); `min_jerk` flipped on for one Tokyo v2 build and judged by eye | E42 D6; the dissolve is the slowest transition we ship with no source | a constants pass + two builds |
| **TR-4 TOP** | **Reconcile doc 51 §51.4 with E44/E45** — recommendation: §51.4 stays the standard for the brand-essence / NotebookLM shorts lane; the Money Physics chart shorts run under E44/E45; write that split into doc 51 | a live contradiction the Tokyo build already violates | one ruling, one paragraph |
| **TR-5 TOP** | **The E44 §2(b) gate** — a cut-on for an already-introduced character FAILs; the mount rule is the check | the Tokyo 0:11 defect has no gate | one gate row |
| TR-6 BACKLOG | **The beat-freeze chart exit** (freeze as a hit, directional-stretch cut into the next plate) | doc 29's default page exit, unbuilt | a species + an exit name |
| TR-7 BACKLOG | **The ARAP match cut** — the object → chart transition with the three invariants (centroid ≤ 0.06 W, axis ≤ 15°, area ratio ≥ 0.60) as gates | the transition that is ours alone; T4 already backlogged, this is its transition use | the morph (T4) + one exit name |
| TR-8 BACKLOG | **M13 into the registry**; the shot-length distribution check (log-normal, keep the median, grow the tail); the carried-light luminance check automated | settled rules with no gate | three gate rows |
| TR-9 BACKLOG | **The wipe-onto-stable-cream mount** (E45's mount (a)) as a code path; today a wipe into a ledger row runs the roll-out | E45 names two mounts, the player has one | a compiler branch |
| TR-10 EXPLORE | **Retire or implement the older continuity contract** (`transition.in: continuous`, motif, one hard cut per act) | a contract with no implementation and no retirement note | a ruling |
| TR-11 EXPLORE | **Isolate transition kinds in retention** — only after TR-1: v2 against v1 tests "page vs clip chain", not kinds | n = 254 measures worlds, not transitions | later shorts |

## 2–5. The inventory (explorer recall, 2026-09-06, cited)

Where a row says "implemented", the file:line is the player's paint site or the compiler's branch; "not implemented" means
nothing in `build_scene_timeline_f.py` or the template paints it. Line numbers are as of commit 821e82b.

### 2.1 Operator rulings (`docs/portable/OPERATOR-RULINGS.md`)

| path:line | what it says | source | status in the player |
|---|---|---|---|
| `OPERATOR-RULINGS.md:188` | the legacy history-lane pattern, still frames held full-screen with hard cuts, is deprecated | operator | doctrine, enforced by lane |
| `:190` | wipes on evidence-free boundaries | operator | implemented as `wipe` (default exit) |
| `:255` | the two-part join is one re-encode: trim to last word + 1.2 s settle, short crossfade | operator (C2) | an ffmpeg join step, not the player |
| `:586` | no stretch > 12 s without a visual event; a scene change counts as the event; 8 s target | E21 | gated, M01 |
| `:1255-1256` | a returning page unwinds from its point (`enter=spiral`), never rolls out again; the page leaves by spiral | E40 §4 | implemented, `lpSpiral` template:2499 |
| `:1341` | a returning character mounts the way he first mounted; a cut-on for an introduced character is a defect, gate it | E44 §2(b) | **not gated**; Tokyo s03 is the defect |
| `:1336-1340` | the press cue at a cut is not a hook device; 0.16 → 0.08 `[DERIVED]`; no transient cue inside 0:05–0:12 unless a page lands | E44 §2(a) | partly; no 0:05–0:12 rule anywhere |
| `:1347-1351` | the mount is the transition into a full-page ledger | E45 | implemented, `mountIn` template:2870 |
| `:1358-1366` | the dock springs in, holds, shrinks and slides by min-jerk; by the springs, never a cut | E45 §1 | implemented, template:843-880 |
| `:1367-1373` | mount for a first arrival, spirals for returns, the roll-out for the cold open; the mount IS the roll-out, the savor stays; chart at mount end + 6.7 s | E45 §2 | implemented, template:2416/2429 |
| `:1374-1379` | the two mounts: (a) wipe onto stable cream, (b) fade-and-mount ending at the cut point | E45 | (b) implemented; **(a) is not a code path**, a wipe into a ledger row runs the roll-out |

### 2.2 Doc 29 (`29-EVIDENCE-MOTION-STANDARDS.md`)

| path:line | what it says | source | status |
|---|---|---|---|
| `:26` | wipes on evidence-free boundaries; persisting evidence holds while the front passes; held stills with hard cuts are a defect | operator + showcase | implemented (dock coalescer, template:2970) |
| `:185,195` | the linked-evidence chain replaces most cutting: new evidence entering IS the transition | derived | partly, the chain is authored not generated |
| `:211` | document reveal: clip-path wipe left→right ~0.7 s `power3.out` | reference deck | implemented as the dock reveal |
| `:240-246` | Part 6 palette: clean cut = contrast; directional wipe = process continuation; 3D book-flip = structural reframe, sparing | derived doctrine | cut + wipe implemented; **book-flip never built** |
| `:450-459` | hand-led reveal ~1.05 s ease-in-out; exits fire 0.6 s before the scene exit | measured vs showcase | partly (drawing lane) |
| `:659,666-667,677` | the measured table: reference scene wipe **0.35 s quart-in-out**; ours 1.25 → **0.62 s**; "settles slow, moves fast, every transition well under a second" | measured from the reference artifact's CSS | implemented, `WIPE = 0.62` template:830 |
| `:907-935` | s9.15 ruling 1: the wipe is the cross-reveal with carried light, one hard `inset()` front; the feathered port was reverted | operator 2026-08-29 | implemented, template:2929-2941 |
| `:932` | a wipe is a monotonic luminance ramp across the boundary | derived check | **not automated** |
| `:938-943` | near-boundary exits snap to the boundary | operator | implemented (compiler snap) |
| `:981-983` | exit style hybrid-authored: docks → wipe, bare → cut, authored override | operator 9.16 §3 | implemented, `build_scene_timeline_f.py:628` |
| `:1493-1505` | the roll-out: 0–0.6 s, clip-path from one edge with the carried-light band | E22 | implemented, `LP.ROLL = 0.7` |
| `:1736` | radial reveal (`clip-path: circle()` from the named point) | motion menu | **not built** (:1770) |
| `:1737` | push hand-off (dock A pushes dock B) | motion menu | **not built** |
| `:1748` | beat-freeze chart exit: freeze as a hit, directional-stretch cut into the next plate | motion menu | **not built** |
| `:1841-1843` | leaving a page: same proof → beat-freeze; topic change → the wipe; "a page never simply fades" | operator 9.28 | partly: beat-freeze unbuilt, so pages leave by spiral, cut or wipe |
| `:1855-1858` | entering a page from a bare plate: the roll-out IS the transition; a page never rolls out under a live dock | operator 9.28 | implemented; E45 overrides the full-frame case with the mount |
| `:1984-2006` | s9.31 the vortex: retract over 2 s, `r(1 − u^1.7)`, three turns, core ~4× rim, area-preserved stretch; return 1.6 s; "the transition should BE the spiral" | operator 2026-09-05 | implemented, `LP_RETRACT` template:2380 |
| `:2008-2011` | nothing rides a spiral out (M15); `exit=cut` for a beat on the last line | operator | implemented + gated |
| `:2013-2021` | the mount: five steps, the cream in the other half of each step; a mount is a dissolve on a word so M13 does not apply; no sound cue | operator 2026-09-05 | implemented, `MOUNT_STEPS = 5`, `LP_MOUNT_RISE = 28` |

### 2.3 Rhythm, gates, shorts, research

| path:line | what it says | source | status |
|---|---|---|---|
| `46-REFERENCE-RHYTHM.md:18-25` | reference 5.9 cuts/min, mean 10.1 s, median 9.6, IQR 6.9; ours 5.6, 9.5, 9.7, IQR 3.4 | measured from `bundle/04` | measurement only |
| `46:27-32` | "we hold the right average with the wrong distribution; we metronome, they vary" | derived | **no gate on spread** |
| `46:35-42` | shot durations log-normal (Cutting, Brunick & DeLong 2011); "the fit has not been tested against our own or the reference's data" | paper | not implemented, not tested |
| `46:69-90` | reference 15–25 % mid-word, 72–81 % in a gap ≥ 0.30 s, the cut at 0.80–0.83 of the gap; ours 39–42 %, 52–54 %, 0.46 | measured (Whisper) | `measure_cut_gaps.py` shipped; **M13 not in `GATES-REGISTRY.md`** |
| `GATES-REGISTRY.md:126` | M14: a camera move may not overlap an evidence build (saccadic suppression) | bundle 07 Pillar 4 | shipped |
| `GATES-REGISTRY.md:128` | M16: the short-form pulse, no gap between visual events over 2.5 s | doc 49 §49.6 + operator | shipped |
| `51-THE-SHORTS-FORMAT.md:61-64` | shorts standard: IN dissolves, Ken Burns, compression; OUT generated plates, chart overlays, the deckle, ARAP, anything from 42–44 | operator (yen short, 2026-09-03) | **contradicted by the Tokyo build and E44/E45** |
| `briefs/ANSWERS…animation-craft.md:112` | pauses ≥ 0.30 s trigger blinks/saccades; masking τ ≈ 50–100 ms (Bridgeman 1975) | paper | the M13/M14 basis |
| `:321-325` | Murch's rule of six is practitioner doctrine; Smith & Henderson 2008: edit blindness is attentional, not blink/saccade | papers | not a check anywhere |
| `:328-331` | the 82 % / 32 % figures are our own measurement; no published study of cut alignment to silence | our measurement | the provenance of M13 |
| `:334` | M13 as proposed: < −32 dBFS for ≥ 200 ms within ±8 frames | proposal | superseded by 46 §46.3's rule; **two decision rules for one gate live in two docs** |
| `:370-386` | J-cut audio leads 4–8 frames; L-cut picture leads 6–10 frames ("ledger rollout before verbal metric analysis") | Pincus & Ascher 2013, `[DERIVED]`, never measured | **not implemented**, no split-edit offset exists |
| `:390-396` | graphic match cut (ARAP): centroid ≤ 0.06 W, axis ≤ 15°, area ratio ≥ 0.60 | Alexa 2000 / Igarashi 2005 | **not implemented**; OUT for shorts per 51:64 |
| `:400-403` | shot lengths log-normal μ 0.85, σ 0.42, 1/f (Cutting 2011) | paper | not implemented |
| `FINDING…:141-145` | "we zoom while the chart builds": serialise punch then build | monograph | gated (M14) |
| `FINDING…:154-157` | the 6-beat timeline is our LP clock (0.7/0.8/2.4/0.5/3.0, focus at 7.4), minimum-jerk transitions | monograph | implemented as `LP` |
| `ANIMATION-REGISTRY.md:364,384` | minimum-jerk, the quintic for rest-to-rest; use sites `kinetics/ease.mjs` | bundle 07 §1.1 | implemented in kinetics, **`min_jerk` flag off by default** (template:456) |
| `06-SCRIPT-TRANSFORMATION-SPEC.md:99-110` | `transition.in` + `motif` on every boundary; `continuous` default; > 1 hard cut per act = reject; audio never cuts | older lane directive | **no implementation, no retirement note** |
| `00-BRAINSTORM…:92-99` | 1–3 s hard-cut cap for verticals, ≤ 6 s landscape | operator's pasted findings | superseded in effect by M16 |
| `storyboard.schema.json:123` | `pattern_interrupt_max_s: 30` | schema default | orphan vs M16's 2.5 s (named in the Gemini profiles work order) |

### 3. What the reference channel does (thin, and that is the finding)

Cadence and placement are measured (`bundle/01_wealth_logic_production_report.md:20,40,50,53`; doc 46). **Transition kind is not:**
`bundle/04_shot_ledger_100_cuts.md` has columns Shot / Start / End / Dur / Keyframe / Species / Spoken line and every one of the
100 rows reads `unclassified`; a grep for `transition|dissolve|wipe|hard cut|whip|cross-fade` across the ledger returns zero hits.
The only reference-derived transition shape we hold is second-hand from the Gemini showcase, not from Wealth Logic: the 0.35 s
quart-in-out wipe (`29:659`).

### 4. What the player paints (`samples/scene-evidence-player.template.html`)

| exit / enter | painted at | duration | curve | cue from the build |
|---|---|---|---|---|
| `cut` | default branch `:2879` | 0 | — | none |
| `wipe` / `wipe_right` | `:2939-2941`, seam `:2949` | `WIPE = 0.62` (`:830`) | `quartIO`, `minJerk` only if `kin("min_jerk")` | none |
| `dissolve` | `:2870-2878`, opacity `:2938` | `DISSOLVE_S = 0.8` (`:830`) | `quartIO` / `minJerk` | none (incl. the outro) |
| `suck:<a>,<b>` | `:2866-2867`, `:2944-2951` | `SUCK_S = 0.3`, `SUCK_TURN = 240°` (`:831`) | `pow(1 − su, 1.6)` (no name, no source) | yes, `suck` at the row start, 0.12 |
| ledger `spiral` | `lpSpiral` `:2378-2384`, `:2499` | retract 1.0 + 1.0; return 1.6; 3 turns | closed-form vortex map | yes, enter 0.12; retract at end − 2.2 s |
| ledger `mount=<s>` | `:2870`, `:2955`, `lpDance` `:2422`, clock `:2415-2429` | `mount_s` (default `LP.FIELD`) | stepped, 5 steps; rise 28 px | none, by rule |
| ledger roll-out | `:2418`, edge `:2424` | `LP.ROLL 0.7` then 0.8 / 2.4 / 0.5 / 3.0 | `expoOut` | yes, `page enter` 0.12 |
| dock on a page (E45) | `:843-880` | pop 0.45 from 0.85, fade 0.12, read 1.2, park 0.7, retract 0.35 | analytic spring (POP, Mp 4 %) + min-jerk slide | none |
| dock on a plate | `:841` | in 0.75 / out 0.72 | expo-out | none |

Two facts to hold: `min_jerk` defaults to `false` (template:456), so the shipped wipe, dissolve and suck do not run the quintic the
FINDING endorses; and the cue map (`build_short.py:381-400`) emits cues only for ledger enters, ledger retracts, the suck and the
press pack. `cut`, `wipe`, `dissolve` and the outro get silence.

### 5. Not found where I looked

Roots: `docs/` (all), `content/video_engine/sources/` (incl. `reference_analyses/` and the bundle), `content/video_engine/scripts/`.
Zero hits: "cut on action", "invisible cut", "Bordwell", "whip pan"; "match cut" only as the ARAP graphic match; "one world" only
as the CSS wrapper; transition kinds in the Wealth Logic shot ledger. Coverage limits: doc 29 read in windows (Parts 3/4/6/8,
§§9.15, 9.16, 9.25, 9.27, 9.28, 9.31), not end to end; doc 47 grepped for M13–M16 only; bundle 02/05/06/07 not opened in full.

## 6. TR-1 landed — the reference's transition mix, measured (2026-09-06, same day)

`content/video_engine/scripts/measure_cut_kinds.py` over the 720p upload (30 fps), all 99 boundaries in 2.4 s, calibrated on
seven boundaries by eye (`docs/research/motion/WEALTH_LOGIC_TRANSITIONS_MEASURED.md`, `wealth_logic_transitions_measured.csv`):

| kind | count | share | median shot before it | what it is |
|---|---|---|---|---|
| hard cut | 36 | 36.4 % | 9.35 s | one-frame switch, both plates steady |
| **dip through black** | 35 | 35.4 % | 6.9 s | a full fade to L = 0 and back, **14 frames (0.47 s) wide at every one** |
| **blur-zoom** | 28 | 28.3 % | 9.8 s | the outgoing plate magnifies until detail is gone, switches, the incoming plate scales up out of softness |
| dissolve / wipe / push / world-persists | 0 | 0 | — | never |

Every boundary changes the world; 71 of 99 sit in a caption gap ≥ 0.30 s (Gemini's transcript pass, agreed); 69 of 99 still
carry measurable motion 0.5 s after the boundary. The Gemini vision pass said "all 99 hard cuts, nothing moves"; with the
`/watch` skill named it verified two boundaries, both agreeing with the tool, and marked the other 97 unverified by its own
fetch limit. Frame-level classification is a Python job.

**What it changes in the judgment above.** The reference has exactly three transitions, and two of them are things our
doctrine forbids or does not have: doc 29 §9.28 says "a page never simply fades", and the reference's single most common
non-cut transition is a 0.47 s fade through black; and the blur-zoom is a zoom-through we have as the `suck` only in the
inverted form. None of the reference's three is a mount, a spiral, a wipe or a dissolve. This does not make E45 wrong: our
world persists (the page is the stage) and the reference's never does, so the reference has no "arrival into a page" to solve.
It does say that for a WORLD CHANGE (clip to clip, plate to plate, page to a different page) the reference's kit is cut in the
gap, dip through black in 0.47 s, or blur-zoom, and nothing else - and that the dip and the blur-zoom are what our kit lacks.
The next measurement (TR-2) is the voice-to-picture offset on the same boundaries, now a Python job on data on disk.

Rows: TR-1 done; TR-2 next; a new TR-12 (decision) - whether the dip through black and the blur-zoom enter our kit for world
changes, with the 14-frame dip as the starting reference `[DERIVED: from the reference, measured]`.
