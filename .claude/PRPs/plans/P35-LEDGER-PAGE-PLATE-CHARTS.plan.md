---
id: P35-LEDGER-PAGE-PLATE-CHARTS
title: The ledger page - plate charts that roll out, write in ink, and build; plus the motion menu
status: running
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-09-02
updated: 2026-09-03
---

# The Ledger Page

## Summary

Every chart the channel ships is an evidence dock on a world plate. The
motion gate (E21) showed the still stretches are the windows with no dock.
The operator's answer is a new world-layer species and the channel's
signature (E22, doc 29 §9.26): a cream page rolls out, charcoal ink writes
the axes, labels and source by hand, and the graph builds from real data
on the page. This PRP builds it as a proposal first (two candidates from
one `series.json`, operator picks), then as a player species the shot
table can place, with the bar-race and decline variants, and adds the
motion menu (stop-motion plate life, beat-freeze chart exit, radial token
reveal, push hand-off, weight-shift anchor captions) as further
opt-in species. Nothing replaces a reviewed mechanism; every species is
an addition beside the locked wipe and dock choreography.

Research findings (2026-09-02, from the component sources and the
hyperframes skill references):
1. **Two chart builders, by data shape.** `chart-story` parses a
   comma-separated handful of values and fades one label per datum; it is
   a proof-stats unit (4-8 values: the 28-cents progress, the three
   questions as bars, 1845 vs 2026). The divergence chart is four series
   of 235 points; that shape uses OUR dash-offset builder (player template
   ~:470-760, driven by a `C` chart spec: panels, series, log, hlines,
   ymin/ymax), which is self-contained enough to port. The stitch's chart
   step therefore has two implementations and the page spec (T2) picks by
   series length.
2. **Ship path is a decision, not a given.** The hyperframes CLI renders
   `--format webm` (transparent) and `png-sequence` locally. A page can
   ship as a PNG/WebP frame sequence the player tiles as a plate (the
   player already tiles PNG plates; a per-frame swap is deterministic and
   needs no `<video>`), at the cost of asset weight (~150 frames per 5s
   page). The alternative is porting the picked stitch into the player as
   a species (T3 as written). Human Gate 4.
3. **Hyperframes' determinism allowlist** (opacity, x/y, scale, rotation,
   color, backgroundColor, borderRadius, transforms) does not list
   `clip-path`, `mask-image` or `filter`; registry items stay inside it by
   moving blobs with transforms and driving reveals through `onUpdate`.
   The roll-out must be authored the same way (a transform on a wrapper
   inside an overflow-hidden frame, not an animated clip-path) or
   `hyperframes check` flags it. Our own player has no such limit.
4. **Sequencing is native**: clips chain by id (`data-start="bleed + 0.4"`),
   sync points are published per component (`draw-complete`,
   `callout-landed`), and `hyperframes snapshot --at` gives the filmstrip.
5. The sound palette has no paper, ink or chalk cue; the page is silent
   until one is sourced (Human Gate 5).

## Intent And Acceptance

Intent: the payoff chart of every episode, and at least one more plate per
episode, is a ledger page; the still stretches the motion gate lists can be
filled with a page that builds rather than a bare plate.

Acceptance:
- `evidence/prototypes/ledger-page-motion.html` renders two candidates
  (A: unroll from the left with the rolled-edge light; B: unroll from the
  top like a scroll) of the divergence chart from its `series.json`,
  scrubbable, with a filmstrip beside it; the operator's pick is recorded
  in doc 29 §9.26.
- The player template gains a `plate-chart` species: a scene row whose
  `world` is `{kind: "ledger", series: "<id>", variant: "line|bars|race|decline|progress", emphasize: n, quiet_zone: "left|right"}`;
  all four beats derive from `t`; the screenshot render produces
  identical frames on re-shoot (sha-stable across two renders of the same
  second).
- Ink writing uses a pinned handwriting webfont bundled into the template
  (no generic cursive fallback), the per-glyph wipe + nib + seeded tilt;
  the graph build reuses the existing dash-offset draw with tip head and
  deposited dots; the callout lands on the raw value.
- The motion gate treats a page's build phase (roll-out + ink + build,
  ~4s) as visual events and its start as an evidence entry; its hold does
  not count. Baselines: ep1 build stays 4 FAIL; a synthetic build with a
  ledger page inside a 30s dock-free window passes M01/M03.
- Bar-race and decline variants render from a `series.json` with periods;
  the memory-maker share race is the first real one, sourced.
- The motion menu lands in doc 29 as §9.27 with one entry per species
  (slot, mechanism, gate treatment); stop-motion plate life ships as the
  first menu species, in the player, from our own cutouts.
- Steel and Paper re-script consumes: the payoff (28 cents) as a ledger
  page, the 1845 vs 2026 comparison as a page, the memory race as a page.

## Scope

- `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/prototypes/ledger-page-motion.html` (+ filmstrip)
- `docs/content-video-engine/samples/scene-evidence-player.template.html`
  (`plate-chart` species: CSS, SVG builder, ink writer, page roll; font
  bundled as data URI)
- `content/video_engine/scripts/build_scene_timeline_f.py` (scene row
  `world.kind == "ledger"`), `gate_motion_density.py` (page events),
  `SHOT-TABLE-F.py` row form
- `content/video_engine/scripts/ledger_page.py` (series.json → page spec
  validation: exact values, labels, source; the variable contract)
- `content/video_engine/tests/test_ledger_page.py`, `test_gate_motion_density.py`
- Docs: doc 29 §9.26 (pick recorded), §9.27 motion menu; BRAND-SHEET §8b;
  PIPELINE stage 7 (page rows); CHECK-RESPONSIBILITIES §2 (gate row note)

## Not Building

- A Remotion or hyperframes runtime inside the episode player. The
  registry items are read for mechanism (handwriting-text ink wipe,
  chart-story value contract, bar-chart-race ranking, ink-bleed filter,
  stop-motion time law); the player stays HTML + its own seek.
- Replacing the wipe, the dock choreography, or any reviewed shot.
- ~~AI-generated paper or ink imagery. The page is drawn, not generated.~~ REVERSED 2026-09-03 by the operator: the page ground (and, by the two-plate build, the inked board) are generated world plates in the spine's register; the drawn field is the fallback. Claim `steel-and-paper-ledger-page-v1` opened.
- Hand-drawn stroke paths for glyphs (path-draw); the string wipe is the
  chosen mechanism for labels. Stroke order is reserved for a future
  signature/logogram case.
- The re-script itself.

## Human Gates

1. **The pick** (after T1): candidate A or B (or a blend), and the roll
   speed / ink pace, from the rendered prototype. The species is a
   proposal until picked.
2. **The font**: one handwriting webfont, licensed for embedding, chosen
   from three samples rendered in the prototype (charcoal on cream at
   1080). Written into the brand sheet's type table.
3. **Bar-race motion on a page**: overtaking bars are the busiest thing
   the channel will show; confirm from the render that it reads as a
   ledger and not a dashboard before it becomes a default variant.
4. **Ship path** - DECIDED 2026-09-02: port first. The chart must be
   crisp and ours (the dense-series builder already lives in the player),
   the page must coexist with docks on one renderer, and the grammar
   (T0) is authored against the player's timeline. Frame sequences are
   used only for the prototype and the pick.
5. **Sound** - DECIDED: source the cues (CC0 via the Freesound client;
   no paid audio). T9.
6. **The ring on a page**: "we'd have to see it to know" - the prototype
   carries one optional variant with the spike drawn on the ledger; the
   pick decides.

## Mandatory Reads

- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §8.3
  (do not bury the plate), §9.13, §9.15 (carried light), §9.22-9.23b
  (charts read like analysts; series named inline; a chart carries its own
  story), §9.25, §9.26
- `docs/portable/OPERATOR-RULINGS.md` E21, E22
- `docs/content-video-engine/REMOTION-UI-HARVEST.md` (the lesson; the
  line-chart tip head already harvested)
- `content/video_engine/channel-assets/money-physics/BRAND-SHEET.md`
  (tokens, the two registers, §8b)
- `content/video_engine/projects/systems-and-blowups/style-spine.woodblock-vox-newsprint.v2.md`
  (paper token; the text ban is for generated imagery)
- Player template: the chart dock builder (template ~:500-720: series,
  dash-offset draw, tip head, event bars, inline names), the record
  document species (`.paper`, `.hw`, `.pcur`), the scene/world layer and
  `paint()`
- `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/prototypes/record-document-motion.html`
  and `data-document-motion.html` (the prototype form: scrubbable, filmstrip)
- Registry references (read-only, mechanism only): remotion-ui
  `handwriting-text`; hyperframes `chart-story` README (envelope + value
  contract), `bar-chart-race`, `decline-chart`, `ink-bleed-reveal`,
  `stop-motion-cadence` README (the time law)
- Learned skill `chart-self-containment`; `dataviz` for the page's
  categorical/sequential colour rules within the six tokens

## Execution Path

Operator, 2026-09-02: "the first part of the plan is getting components
aligned and understanding how these things map over to our evidence
layer - what determines the full page surface, what belongs as pop-out
evidence on the plate, how do we determine the choreography that leads
to different outcomes / plate / evidence layers / transitions." The
episode rebuild ORDER waits for the verbal re-script; this plan builds
the vocabulary and the species, not the episode.

0. T0 the surface grammar (doc) first - it is what every later slice
   authors against.
1. T1 prototype next: settles the look (Human Gate 1) and the font
   (Human Gate 2) before any player code.
2. T2 (spec + validator) in parallel with T1: pure data contract.
3. T3 port into the player after the pick (Human Gate 4 decided: port
   first; frame sequences only for the prototype/pick). Parent-owned.
4. T4 (timeline + shot table + gate) after T3's species exists.
5. T5 (race + decline variants) after T3; Human Gate 3 on the race.
6. T6-T8 as before; T9 (sound cues) any time, disjoint write set.
7. The Steel and Paper re-script work order names its pages AFTER the
   verbal rewrite, using T0's grammar; not before.

## Builder Architecture (operator clarification, 2026-09-02)

Two independent axes; a shot-table row names both.

- **Surface** - where the chart lives: the LEDGER PAGE (world plate:
  cream, bleed, outline; new) or the DOCK (near-black evidence card;
  unchanged). The page set-up is shared by every chart that lands on it.
- **Builder** - one per treatment, each harvested from ITS OWN component
  with its own envelope and sync points; they are never merged:

| Builder | Source | Data shape | Today |
|---|---|---|---|
| `dense-line` | our player builder (template ~:470-760) | many points per series, several series, log scale, event bars, hlines | exists, dock-only |
| `story` | hyperframes `chart-story` | 4-8 values landing on exact numbers; bars / line / donut / progress; one emphasized datum with a rolling callout | to port |
| `race` | hyperframes `bar-chart-race` | series × periods; ranked bars overtaking; axis rescales; accent hands to the leader | to port |
| `decline` | hyperframes `decline-chart` | one metric start → end; line draws down, value counts down, ground darkens | to port |
| `combo` | hyperframes `data-chart` | bars + line, staggered reveal, NYT-style labels | to port |

Making a builder render on either surface is work inside T3 (the
existing builder knows only the dock's geometry and palette), not a
given. T0's grammar decides which surface × builder combinations the lane
allows; the draft rule is that THEIR evidence stays a dark card and OUR
proof earns the page.

## Patterns To Mirror

- Prototype form: `evidence/prototypes/record-document-motion.html` -
  standalone, scrubbable, filmstrip PNGs beside it, reviewed by contact
  sheet before anything enters the template.
- Species in the template: the record document (`.dock.record`,
  `ev.record` branch at template ~:395) - a species is a class on the
  container plus a branch in the paint routine, driven by `t`.
- Chart draw: the existing dock builder's dash-offset + `getPointAtLength`
  tip head + deposited dots; inline series names (s9.23b).
- Determinism: everything derived from `t`; seeded jitter via a pure hash
  of (seed, index, salt), never `Math.random` (handwriting-text rule 2;
  stop-motion-cadence "no wall clock, no incremental state").
- Data contract: `series.json` beside the asset, source line mandatory
  (`ev-*.series.json`; chart-self-containment).
- Gate shape and tests: `gate_motion_density.py` + red/green tests.

## Task Slices

### T0: The surface grammar - page vs dock vs transition, decided by rule
- Status: done
- Owner: parent (doctrine), explorer (→ `Explore`) for the ep1 window census
- Depends on: none
- Write set: `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (§9.28),
  `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` (§3 row: the agent verdicts surface choice per window),
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f/SURFACE-CENSUS.md`
- Acceptance: §9.28 states, as testable rules, (a) what earns the FULL
  PAGE: a proof that is OURS (we ran it, we drew it), carried by a series
  we own, at a beat that turns the argument (payoff, tell, catalyst,
  ring close) or a window the motion gate would otherwise mark still;
  (b) what stays POP-OUT evidence: their document, their chart, a
  citation, a stamped slide, anything read rather than built - the dock
  register (near-black, unchanged); (c) what decides the CHOREOGRAPHY at
  a boundary: leaving a page → beat-freeze exit or the wipe by whether
  the next beat continues the proof; a dock landing on a page → the
  declared quiet zone, never over the emphasized datum; camera moves
  mutually exclusive per window; the pivot's reversal takes no species;
  (d) the density rule linking to E21: no window > 12s without a dock,
  a page build, or plate life. The census applies (a)-(d) to every ep1
  window and lists, per window, page / dock / plate-life / none with the
  rule that decided it - the input the re-script's shot table starts
  from.
- Validate: the census covers every row of `SHOT-TABLE-F.py`; each row
  cites a rule letter; `gate_motion_density.py` still runs unchanged
- Evidence: doc 29 §9.28 (surfaces table; rules A1-A3, B1-B4, C1-C6, D1-D4; the census form); CHECK-RESPONSIBILITIES §3g surface choice per window; `build-f/SURFACE-CENSUS.md` covers all 75 rows of `SHOT-TABLE-F.py` (len(W)=75, not 76), each with rule letters and a builder; counts page 8 rows / 6 pages, dock 49, plate-life 4, none 14; PAGE candidates agree with the PRP's three (28c yardstick #13-14, 1845 vs 2026 #41 conditional on the VO claiming the check, memory race #70 pending its series) and add three (#6 divergence layer, #47 the test, #62 the monitor). FINDING: the motion gate reads `evidence-dock.json` / `motion-plan.json` on an older clock than the timeline (divergence dock 26.4 vs 50.4); on the timeline's own scene docks there are 20 stretches > 12s, not 11 - T4 must read the timeline's `scenes[].docks`. Shot rows #53/#54 overlap 5.5s.

### T1: Prototype - the stitch, in the hyperframes lane
- Status: review (Human Gate 1 pick open; C is the working reference)
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/hyperframes/compositions/ledger-page-v1.html`,
  `content/video_engine/hyperframes/compositions/components/{ink-bleed-reveal,outline-draw,chart-story,whiteboard-ink}.html` (registry adds, verbatim),
  `content/video_engine/hyperframes/renders/ledger-page-v1*.mp4`,
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/prototypes/filmstrip-ledger-page.jpg`
- Acceptance: operator's own definition - "roll out the cream, bleed in
  the charcoal, use the outline component, then build the chart; it's
  literally just stitching the components together." One composition
  mounts, in sequence on one paused timeline: the page roll-out
  (clip-path inset with the rolled-edge light, authored in the
  composition), `ink-bleed-reveal` with the charcoal field as its mark
  slot, `outline-draw` around the field, then `chart-story` (line
  variant, divergence data and labels from `ev-divergence-v1.series.json`,
  exact values, source line) with our six tokens mapped onto the
  components' `--brand/--accent/--fg/--bg` variables. Sync points chain
  (bleed settles → outline `draw-complete` → chart `callout-landed`).
  Variant B swaps the bleed for `whiteboard-ink` strokes (the scribble
  field) with its default sketch replaced by field strokes; variant A is
  the plain page without the field, for comparison only. Rendered with
  the pinned CLI (`npm run render`), filmstrip at 0.3s steps; `hyperframes
  check` clean; no wall-clock or random calls (the components are
  deterministic by contract). The operator's pick recorded in doc 29
  §9.26.
- Validate: `cd content/video_engine/hyperframes && npm run check && npm run render -- -c compositions/ledger-page-v1.html`;
  filmstrip present; `grep -E "Math.random|Date.now|performance.now" compositions/ledger-page-v1.html` returns nothing
- Evidence: registry adds ink-bleed-reveal / outline-draw / chart-story / whiteboard-ink (pinned 0.7.101); `compositions/ledger-page-v1-{A,B,C}.html` + `ledger-page-v1.html` (=C) generated from one data set; three renders `renders/ledger-page-v1-{A,B,C}.mp4` (artifact validated, 7-13s each, untracked like the lane's other renders); filmstrips `evidence/prototypes/filmstrip-ledger-page-{A,B,C}.jpg` reviewed: roll-out, field, sunflower outline, bars landing on the exact values, source in the cream margin; determinism grep clean. Deviation: `hyperframes check` targets the project index.html only, so validation is the renders themselves. Doc 29 s9.26 carries the candidate note; the pick is the operator's

### T2: Page spec and validator
- Status: done
- Owner: junior_developer (→ `general-purpose`)
- Depends on: none
- Write set: `content/video_engine/scripts/ledger_page.py`,
  `content/video_engine/tests/test_ledger_page.py`
- Acceptance: `ledger_page.py <series.json> --variant line|bars|race|decline|progress --emphasize n`
  validates the series (numeric, labels aligned, source present, periods
  for race), emits the page spec JSON the template consumes (values
  verbatim as strings so no re-rounding), and fails on a missing source
  line; tests cover each variant and the failure.
- Validate: `python -m pytest content/video_engine/tests/test_ledger_page.py -q`
- Evidence: `ledger_page.py` (299 lines; pick_builder / validate / build_spec pure; values verbatim via parse_float=str; race/decline/progress contracts in the docstring; checklist series rejected with 'keep it a dock'); `pytest test_ledger_page.py -q` 17 passed; trim-proof -> story bars 8 values, value_strings verbatim; divergence -> dense-line 4x235 pts with the axes block carried

### T3: The plate-chart species in the player
- Status: done (working reference C; the pick and the font stay open)
- Owner: parent
- Depends on: T1 (Human Gates 1, 2), T2
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html`
- Acceptance: a scene whose `world.kind == "ledger"` renders the picked
  candidate from the page spec; all four beats from `t`; the bundled
  font; a declared quiet zone where docks land; two renders of the same
  second are byte-identical; the reviewed wipe and dock code are
  untouched (diff confined to the new species block + one branch in
  `paint()`).
- Validate: `python content/video_engine/scripts/render_episode.py --range <s> <e>`
  on a synthetic timeline twice and compare frame hashes; visual check via
  `preview_start` episode-player
- Evidence: template gains the LEDGER PAGE species: CSS block after `.world`, `LP` constants + lpHash + buildLedger/buildLedgerBars/buildLedgerLine/paintLedger before `render`, one branch in `paint()` (world.kind == "ledger": no image, Ken Burns capped to a 0.03 push); reviewed wipe and dock code untouched. Synthetic proof `build-f/ledger-species-proof.html` (story bars from ev-trim-proof, dense line from ev-divergence, then a plain plate): all four beats render from t; stage innerHTML sha at t=8.0 identical from two seek orders (0ca203ff04e45b16); callout lands on the exact value string 13.8; inline names de-collide; wipe out of a page clean; utf-8 declared at the top of the template (the served player had no charset - caption dashes decoded as cp1252 before). Font: Inter until Human Gate 2 | Corrected 2026-09-03 on operator review (E22 addenda 2-3): five beats - textured unravel, half savor, FIELD (soak = ink absorbed, or scribble = the original idea, `page.field`), outline on the field's own edge (no gap), ink + build; coffee-stained parchment margin from the first frame. Proof re-verified: hash 47ba741f3b75b2b7 identical from two seek orders; bars seated on the baseline; scribble strokes hidden until their turn | 2026-09-03 later: settled to plain cream -> field -> line (coffee stains and the uneven halo refused); species takes `page.plate` (generated blank washi page) and `page.field_plate` (generated inked board, cross-faded in beat 3); claim steel-and-paper-ledger-page-v1 opened and handed to Codex headless; contact sheet pending the operator | PLATES DELIVERED: claim steel-and-paper-ledger-page-v1 (world-ledger-blank-page-v1, world-ledger-inked-board-v1; claim-resume 2 flagged / 0 failed); species takes `page.board` (measured box) + `page.plate_zoom`; proof scene 1 runs the two-plate path - washi cream, felt-charcoal board, the outline tight on the plate's own edge; contact sheet pending the operator

### T4: Timeline, shot table, and the motion gate know the species
- Status: done
- Owner: implementation_luna (→ `general-purpose`)
- Depends on: T3
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py`,
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/SHOT-TABLE-F.py` (row form only, documented in the header),
  `content/video_engine/scripts/gate_motion_density.py`,
  `content/video_engine/tests/test_gate_motion_density.py`,
  `docs/content-video-engine/PIPELINE.md`, `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`
- Acceptance: the shot table can place `("ledger:<series>:<variant>", start, end, kb, [docks])`;
  the compiled timeline carries the page spec; the gate counts the build
  phase as events and the start as an evidence entry; ep1 baseline stays
  4 FAIL; a synthetic 30s dock-free window with a page passes M01/M03.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: `pytest test_gate_motion_density.py test_motion_gate_wiring.py -q` 22 passed; shot row `ledger:<series>:<variant>[:<emphasize>[:<quiet_zone>]]` -> `world_for_plate` emits `{kind: ledger, page: <spec>}` (no asset), timeline gains `species`; gate clock FIXED: dock events from the timeline's own scenes[].docks incl. badge reveals (`dock_source: timeline`), evidence-dock.json only as fallback; page beats (0/0.6/3.4/4.2/7.2s) count as events, page start as evidence entry, hold still; ep1 after the fix: M01 8 stretches 123s=15% worst 17.7s at 2:24 (was 11/23%/34.6s), M03 54s from 2:52 (was 197s), still 4 FAIL; synthetic 90s window with a page at 12-31s passes M01/M03/M05, without it FAILs; GATES-MOTION.md regenerated. Plate-life events still uncounted (T6)

### T5: The other builders - story, race, decline, combo - each ported from its own component
- Status: review (Human Gate 3: the race on a page; the memory-share race waits on sourced TrendForce quarters)
- Owner: implementation_luna (→ `general-purpose`), one builder per dispatch
- Depends on: T3, T4; Human Gate 3 (race)
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html` (one builder function per treatment, keyed by the row's `builder`; no changes to `dense-line`),
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-memory-share-race-v1.series.json`,
  `content/video_engine/tests/test_ledger_page.py`
- Acceptance: four separate builders, each reproducing its component's
  envelope and sync point - `story` (bars/line/donut/progress landing on
  exact values, callout rolls, `callout-landed`), `race` (ranked bars
  overtaking across periods, axis rescale, accent hand-off), `decline`
  (line draws down, value counts down, ground darkens), `combo` (bars +
  line, staggered) - each renders on the page surface and, where T0
  allows, in a dock; the memory-maker share race renders from sourced
  data; the operator confirms it reads as a ledger. Race and story are
  distinct builders; nothing is folded into `dense-line`.
- Validate: `python -m pytest content/video_engine/tests/test_ledger_page.py -q`; range render of the race
- Evidence: template species block gains buildLedgerRace / buildLedgerDecline / buildLedgerCombo, each from its own component's envelope (race: rank keyframes, overtakes as swaps, axis glides, accent on the leader, `st.sync` rank-settled times; decline: draw-down + count-down + darkening ground, endpoint locks on the exact string; combo: bars then the line, NYT direct labels with field-coloured halos); dense-line/story untouched; `pytest test_ledger_page.py -q` 23 passed; determinism hashes equal at three t's; proof `build-f/ledger-builders-proof.html`. Race data: `ev-memory-share-race-v1.series.json` is SOURCES-TO-VERIFY with `placeholder: true` (no multi-quarter DRAM vendor share exists in the repo) and the validator refuses placeholders, so it can never render; the proof race uses synthetic data marked not for air

### T6: The motion menu, and stop-motion plate life as its first species
- Status: review (plate life shipped in the player; side-by-side on a bare ep1 window still to render)
- Owner: parent (menu + template), junior_developer (→ `general-purpose`) for the doc rows
- Depends on: T3 (template ordering only)
- Write set: `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (§9.27),
  `docs/content-video-engine/samples/scene-evidence-player.template.html` (plate-life species),
  `content/video_engine/scripts/gate_motion_density.py` (plate-life events),
  `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: §9.27 (written 2026-09-02) is the menu of record; plate
  life renders our cutouts on a bare plate under the stepped-time law
  (quantize t to 8/10/12 fps first; squash on land; seeded two-frame boil)
  and counts as events; a side-by-side of one bare ep1 window with and
  without plate life for the operator.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`; range render side-by-side
- Evidence: pending
- Evidence: §9.27 is the menu of record (written 2026-09-02); plate life species in the template (`plate_life` rows: cutouts from assets/generated/cutouts, t quantized to 10 fps first, throw-and-land with squash, seeded two-frame boil, carried by the camera); gate counts stepping events (T7); proof scene 3 carries two cutouts on a bare plate

### T7: Targeted species - punch, scribble callout, focus zoom, feathered spotlight, squiggle marks, pull-back
- Status: review (player half shipped for punch / focus zoom / pull-back / callout / spotlight / squiggle; beat-freeze, radial, push not built)
- Owner: parent (template + targeting resolver), implementation_luna (→ `general-purpose`) for the shot-table row forms and tests
- Depends on: T4
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html` (species blocks + one `resolveTarget()`),
  `content/video_engine/scripts/build_scene_timeline_f.py` (species rows with declared targets),
  `content/video_engine/scripts/gate_motion_density.py` (events per §9.27; camera-move exclusivity per window),
  `content/video_engine/tests/test_targeted_species.py`, `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: the targeting law is code - every species row carries a
  target of kind `datum|point|region|span` and the player resolves it to
  pixels at render time (`resolveTarget`); a row without a target is
  rejected by the builder; camera punch, focus zoom, pull-back and Ken
  Burns are mutually exclusive per window (builder error, gate FAIL);
  the punch lands on "this iron spike" (ring token, plate semantic
  region) in a range render; a scribble callout circles the emphasized
  datum of a ledger page; a focus zoom holds dead still at the anchor
  (micro-drift ends at exactly zero); the feathered spotlight glides
  between two declared targets; squiggle marks draw under a declared word
  span in stage captions; pull-back opens on one declared number and
  reveals the page around it. Each species: one range render for the
  operator.
- Validate: `python -m pytest content/video_engine/tests/test_targeted_species.py content/video_engine/tests/test_gate_motion_density.py -q`; range renders
- Evidence: (data half) `validate_species` in build_scene_timeline_f.py (target kinds datum|point|region|span; pointing species without a target FAIL the build naming the row; punch|focus_zoom|pull_back mutually exclusive and never over Ken Burns > 0; optional pivot span); scenes carry `species` verbatim, timeline `species` lists kinds; gate SPECIES_EVENTS table (plate life steps at 10 fps), M09 camera-move clash gate; `pytest test_targeted_species.py test_gate_motion_density.py test_motion_gate_wiring.py -q` 42 passed; ep1 RESULT 5 FAIL / 1 WARN / 3 PASS
  (player half) `resolveTarget` (datum -> the page's bar or dense-line point; point/region -> frame fractions; span -> caption words), `camXf` one world transform about the target (docks fixed), `paintSpecies` overlay; proof: callout circles the trim bar with its label, squiggle draws under 'ledger', spotlight glides between two points, punch on a point moves the world and the cutouts; no console errors; range renders per species for the operator are still to cut

### T8: Focus rack vs the current evidence lighting - side by side (proposal)
- Status: review (the operator picks; the current mechanism stays)
- Owner: parent
- Depends on: T3 (template ordering only)
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/prototypes/focus-rack-vs-wash.html`
  (+ filmstrip), `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (§9.15 / §9.27 pick recorded)
- Acceptance: the same two-evidence window from ep1 (a pair of docks over
  one plate) rendered twice from the same timeline - current mechanism
  (wash/spot clipped to the front, §9.15) and focus rack (synchronized
  blur, dimming, scale and parallax shifting focus once between the two
  cards) - with a filmstrip at the boundary frames where images currently
  cut; the operator picks; the current mechanism stays until then and is
  not edited in this slice.
- Validate: `preview_start` on the prototypes dir; filmstrip present; the
  reviewed template untouched (`git diff --stat` shows no template change from this slice)
- Evidence: `evidence/prototypes/focus-rack-vs-wash.html` (standalone, real ep1 assets from row 585.1-595.2 on an 8s clock; TOP = the template's wash/spot/settle copied verbatim, BOTTOM = flat dim + one 0.6s rack: blur 0-2.5px, brightness 1-0.78, scale 1-0.985, x -+6px); filmstrip 8 cols x 2 rows at 3.9/4.1/4.3/4.6/5.0 and the front 7.35/7.5/7.7 (gitignored); template diff empty; no Math.random/Date.now; doc 29 s9.27 paragraph. Agent's read: the rack removes the scrim/spot SHAPE and makes the boundary a one-value step; it does not by itself stop the card severing at the front (that is a card-exit decision under s9.15)

### T9: Sound cues for the page - paper roll, ink bleed, chalk stroke
- Status: done
- Owner: junior_developer (→ `general-purpose`)
- Depends on: none
- Write set: `content/video_engine/configs/sound_palette.json` (three cues),
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/sound/` (CC0 files + SOURCES.md with Freesound ids and licences),
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/sound/SOUND-PLAN.json` (page cue slots, gains at the −28 LU bed rule)
- Acceptance: three CC0 cues sourced through the Freesound client used
  for the whoosh (operator: "source the sounds"; no paid audio), each
  ≤1.5s, trimmed, loudness-matched to the existing accent gain (0.9)
  and aligned to the page's sync points (roll-out start, bleed settle,
  outline `draw-complete`); SOURCES.md records id, author, licence.
- Validate: `python -c "import json;json.load(open('content/video_engine/configs/sound_palette.json'))"`; ffprobe on each file; SOURCES.md present
- Evidence: commit 1c97b84; Freesound CC0 464302 (paper slide, roll-out), 166322 (water drop, bleed settle - no CC0 ink sound under 4s exists; flag at the contact sheet), 447925 (chalk stroke, outline draw-complete); trimmed <=1.5s, matched to fs-whoosh-1 at -14.06 LUFS within +-1 LU (roll -13.99, bleed -14.09, stroke -14.45 limited); sound_palette.json + SOUND-PLAN.json `page_cues` (page-relative, because `cues` is flattened onto the episode clock by render_episode.mix_audio); mp3s gitignored like the whoosh; SOURCES.md carries the table

## Verification

```powershell
python -m pytest content/video_engine/tests/test_ledger_page.py content/video_engine/tests/test_gate_motion_density.py -q
python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f --timeline steel-and-paper.timeline.json
python scripts/prp_validate.py .claude/PRPs/plans/P35-LEDGER-PAGE-PLATE-CHARTS.plan.md
```

Determinism check for every visual slice: render the same one-second range
twice and compare frame hashes; grep the template for
`Math.random|Date.now|performance.now` inside the new species.

## Evidence And Handoff

- T1: the prototype path, filmstrip, and the recorded pick + font.
- T3-T6: range renders, frame-hash equality output, test runs, commit shas.
- Close: `main` fast-forwarded; brand sheet §8b and doc 29 §9.26 carry
  the picked candidate; the Steel and Paper re-script work order names the
  three ledger pages it will carry; memory `money-physics-brand-sheet`
  updated with the signature.
