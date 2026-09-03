---
id: P35-LEDGER-PAGE-PLATE-CHARTS
title: The ledger page - plate charts that roll out, write in ink, and build; plus the motion menu
status: draft
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-09-02
updated: 2026-09-02
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
- AI-generated paper or ink imagery. The page is drawn, not generated.
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

1. T1 prototype first, alone: it settles the look (Human Gate 1) and the
   font (Human Gate 2) before any player code.
2. T2 (spec + validator) in parallel with T1: pure data contract, no
   visual dependency.
3. T3 (player species) after the pick; parent-owned because it edits the
   reviewed template.
4. T4 (timeline + shot table + gate) after T3's species exists.
5. T5 (race + decline variants) after T3; Human Gate 3 on the race.
6. T6 (motion menu doc + stop-motion plate life) can run in parallel with
   T3-T5; its write set is disjoint apart from the template, so its
   template edit lands after T3 by rebase, never concurrently.

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

### T1: Prototype - two candidates from one series.json
- Status: pending
- Owner: parent
- Depends on: none
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/prototypes/ledger-page-motion.html`,
  `.../prototypes/filmstrip-ledger-page.jpg`, `.../prototypes/ledger-*.png`
- Acceptance: page rolls out (A: from left with rolled-edge light; B:
  from top), ink writes axes/labels/title/source per glyph with nib and
  seeded tilt in three candidate fonts, the divergence line builds with
  tip head and deposited dots, callout rolls to the exact value; scrub
  bar; filmstrip at 0.3s steps; no wall-clock or random calls; the
  operator's pick and font choice recorded in doc 29 §9.26.
- Validate: open via `preview_start` (static server on the prototypes
  dir), screenshot at t = 0.3, 1.2, 2.4, 4.0 for both candidates; grep
  the file for `Math.random|Date.now|performance.now` returns nothing
- Evidence: pending

### T2: Page spec and validator
- Status: pending
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
- Evidence: pending

### T3: The plate-chart species in the player
- Status: pending
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
- Evidence: pending

### T4: Timeline, shot table, and the motion gate know the species
- Status: pending
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
- Evidence: pending

### T5: Bar-race and decline variants, with the first real race
- Status: pending
- Owner: implementation_luna (→ `general-purpose`)
- Depends on: T3, T4; Human Gate 3
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html` (variant builders only),
  `content/video_engine/projects/systems-and-blowups/steel-and-paper/evidence/objects/ev-memory-share-race-v1.series.json`,
  `content/video_engine/tests/test_ledger_page.py`
- Acceptance: race = ranked bars overtaking across periods with axis
  rescale and accent hand-off; decline = line drawing down with the value
  counting down and the page darkening slightly; the memory-maker share
  race renders from sourced data; the operator confirms it reads as a
  ledger.
- Validate: `python -m pytest content/video_engine/tests/test_ledger_page.py -q`; range render of the race
- Evidence: pending

### T6: The motion menu, and stop-motion plate life as its first species
- Status: pending
- Owner: parent (menu + template), junior_developer (→ `general-purpose`) for the doc rows
- Depends on: T3 (template ordering only)
- Write set: `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` (§9.27),
  `docs/content-video-engine/samples/scene-evidence-player.template.html` (plate-life species),
  `content/video_engine/scripts/gate_motion_density.py` (plate-life events),
  `content/video_engine/tests/test_gate_motion_density.py`
- Acceptance: §9.27 lists each species (ledger page, plate life,
  beat-freeze chart exit, radial token reveal, push hand-off, weight-shift
  anchor captions) with its slot, mechanism, and gate treatment; plate
  life renders our cutouts on a bare plate under the stepped-time law
  (quantize t to 8/10/12 fps first; squash on land; seeded two-frame boil)
  and counts as events; a side-by-side of one bare ep1 window with and
  without plate life for the operator.
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`; range render side-by-side
- Evidence: pending

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
