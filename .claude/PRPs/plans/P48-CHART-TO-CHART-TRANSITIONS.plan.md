---
id: P48-CHART-TO-CHART-TRANSITIONS
title: Chart-to-chart transitions as a first-rate feature - a chart changes STATE (redraw, rescale, extend, recast, morph) and never cuts
status: draft
operation: feature
risk: elevated
owner: parent
branch: main
created: 2026-09-07
updated: 2026-09-07
---

# Chart-to-chart transitions

## Summary

The operator, 2026-09-07: *"The chart-to-chart transitions need to become a first-rate feature: we should be able to
re-draw, change chart types/shapes, add additional points, or morph on page."*

Today a ledger page's chart is decided once. `ledger_page.py` picks ONE builder from the data shape and the variant
(`pick_builder`: dense-line | story | race | decline | combo | object), the player builds that builder's marks once in
`buildLedgerLine` / `buildLedgerBars` / `buildLedgerCombo` / … and `paintLedger*` maps `t` onto them. Everything we have
added since (P47 T2's `build_to`, T6's `undraw` and `figure`, T9's ordered redraw with a `paths` selector) moves the *pen*
over marks that never change. To show the same data another way we must leave the page: a second scene, a `snap`, a chart
card, or a cut. That is why the fourth watch produced two defects at once - a page that un-drew and never redrew the series
the sentence was about, and a second chart that had to arrive as an evidence dock over the first page's title.

This plan makes the chart's SHAPE a function of time like everything else. A page declares a base state and, on a word, a
transition to another state; the engine keeps both states' marks and blends them. The four verbs the operator names are one
mechanism with different inputs:

| verb | the state that changes | the transition |
|---|---|---|
| **re-draw** | the drawn extent (same data, same builder) | `build_to` / `undraw` - shipped (P47 T2/T6/T9) |
| **add additional points** | the data window and the scale | `extend` (new points draw on) + `rescale` (the axes retarget) |
| **change chart types/shapes** | the builder | `recast` - a keyed tween between two mark sets |
| **morph on page** | the geometry, with no key correspondence | `morph_to` - ARAP (`kinetics/arap.mjs`), today only a page ENTER |

The enabling idea, and the whole risk of the plan, is **T1**: every builder emits MARKS with stable keys instead of
drawing straight into `st`. A mark is `{key, role, geom, style}` where `key` is `(series, index)` for a datum and a role
name for furniture (axis, tick, name, label). With keys, a transition is a pure interpolation - matched keys tween, new
keys enter by the stroke or spring law, dropped keys exit - computed at `t` from two states that were both built at load.
Nothing is rebuilt per frame, so a seek is still the play and the renderer is unchanged.

## Intent And Acceptance

1. A ledger page declares `chart_to {at, dur, kind, …}` in its shot row's species list; the compiler resolves the target
   into a second full `ledger_page.v1` spec on the same scene (`world.page_states[]`), validates the transition's
   legality, and the player renders the blend as a pure function of `t`.
2. **rescale**: the y-domain and/or the x-window change; every mark that exists in both states moves to its new position on
   a min-jerk clock; the tick labels cross-fade and the new ticks write in the page's ink. A datum's identity never breaks.
3. **extend**: state B carries points state A did not; the shared marks rescale first, then the new points DRAW at the
   pen's speed (`kinetics/stroke.mjs`, the two-thirds law) from the last shared datum. Nothing pops.
4. **recast**: state B uses a different builder over the same window and cardinality; matched keys tween geometry (a line's
   point ↔ a bar's top-centre ↔ a combo's bar), unmatched marks enter/exit by the spring; the axes rescale in the same
   move. Legal pairs are declared and enforced, not discovered at render (see Not Building).
5. **morph_to**: two shapes with no key correspondence (a page element and a chart area, a chart area and a prop) morph by
   ARAP mid-page, with `measure_morph.py`'s three invariants reported per morph (M17), reusing T3's mesh work. This is the
   mechanism R26-16 needs (the morph's source planted in the outgoing scene - the red tie).
6. Every transition is an EVENT the gates can see: it is a landing for E51's push tie, it is motion for M01/M02, and it
   restarts E50's deployed clock (a chart that changes state is a new chart's life). New row **M23** names every declared
   transition with its clock and FAILs a page whose chart state changes with no declared transition.
7. **The goldens stay byte-identical.** A page with no `chart_to` renders exactly as it does today, before and after T1.
8. The shot table reads like the doctrine: one line per transition, on a word, with its own duration.

## Scope

- `content/video_engine/scripts/ledger_page.py` - resolve a named target state into a spec; the legality rules.
- `content/video_engine/scripts/build_scene_timeline_f.py` - the `chart_to` species and its grammar; `world.page_states`.
- `docs/content-video-engine/samples/scene-evidence-player.template.html` - the mark model, the state store, the
  interpolators, the four transitions; `__lpProbe` reports the active state and the blend.
- `content/video_engine/scripts/kinetics/` - a new `chartxf.mjs` for the keyed tween and the scale interpolation (the
  module discipline: pure, seek-exact, dialled, synced by `sync_kinetics.py`).
- `content/video_engine/scripts/gate_motion_density.py` - M23; the transition as a landing and as an E50 mark.
- Tests: `tests/kinetics/chartxf.test.mjs`, `tests/test_chart_transitions.py`, additions to `test_page_performs.py`,
  `test_golden_frames.py` (a flag golden per verb), `test_ledger_page.py`.
- Doctrine: a ruling (E53 candidate) + `docs/content-video-engine/CAPABILITIES.md` + `29-EVIDENCE-MOTION-STANDARDS.md`.
- The Tokyo application: the beats where each verb earns its place (see T7).

## Not Building

- **A recast between states that cannot be keyed 1:1.** A 316-point dense line has no honest correspondence to five bars;
  the compiler REFUSES it by name and points the author at `morph_to` or a cut. Legal recasts share a data window and
  cardinality (line ↔ combo's line, story bars ↔ combo's bars, line ↔ bars when the window is the story's window).
- **A new charting library, or a d3 dependency.** The scales, ticks and paths stay ours (`lpYTicks`, `lpNiceStep`,
  `strokeFrac`). We are porting a mechanism, not a runtime (the remotion-ui wipe port is the standing lesson).
- **Per-frame DOM construction.** Every state's marks are built at load; the frame only writes attributes.
- **More than `STATE_MAX` (3) states on one page.** A fourth is a new page or a card; the player's size and the reader's
  memory both say so.
- **A live editor for transitions.** That is R26-17 (the engine apart from the editor) and stays its own plan.
- **Race and decline builders as recast targets** in this plan (they carry their own clocks); they may be sources.

## Human Gates

- **HG1 (after T3):** the operator watches `rescale` and `extend` on a real page - do added points and a moving axis read
  as one continuous thing, or as a jump?
- **HG2 (after T4):** the operator watches `recast` - does a line becoming bars read as the same data, or as a new chart?
  This is the gate that decides whether recast ships or stays an experiment.
- **HG3 (after T5):** the morph on page, on the planted element (R26-16's tie) - the seam's length, the source's honesty.
- **HG4 (after T7):** the Tokyo cut with the verbs applied, before any render.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` - dispatch, hand-off, lane write sets.
- `docs/portable/OPERATOR-RULINGS.md` - **E25** (a chart proves one sentence and leaves), **E28** (it reads at a glance;
  sign is geometry), **E47/E48** (the transition vocabulary; the hero is the spiral; cut minimally), **E49** (nothing goes
  truly still), **E50** (the deployed life: 6-8 s from the last data mark, 12 s at most), **E51** (a push is tied to a
  landing), **E52** (a page cites, it does not footnote; a chart reads with no caption).
- `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.23b (series named inline, labels never overprint), §9.26
  (data only from a series.json), §9.27/§9.28 (the targeting law; surface × builder).
- `.claude/PRPs/plans/P47-STOP-ACTION-BUILD-ON-AND-THE-CHART-MORPH.plan.md` - T2 (the page species), T3 (ARAP and the
  strip mesh - **read the two failures recorded there**: a fan mesh flips on a jagged series; a vertex-covariance axis
  reads a strip as vertical), T6/T9 (the ordered redraw and the `paths` selector).
- `docs/ANIMATION-REGISTRY.md` - every dial and law with its status, so a new dial is tagged, not invented.
- Source: `scripts/ledger_page.py` (`pick_builder`, `build_spec`, `page_boxes`), `scripts/build_scene_timeline_f.py`
  (`SPECIES_KINDS`, `PAGE_SPECIES`, `_validate_page_fields`, `ledger_world`), the template's `buildLedgerLine` /
  `buildLedgerBars` / `buildLedgerCombo` / `paintLedger*` / `capFrac` / the `caps`+`undraw` sequence, `kinetics/arap.mjs`,
  `kinetics/stroke.mjs`, `kinetics/spring.mjs`, `scripts/measure_morph.py`.
- **Skills:** `backend-patterns` and `frontend-patterns` are NOT routed - this plan touches no API, database, server
  boundary, React/Next surface, form or route. The player is a single deterministic HTML template rendered headlessly; its
  contract is the golden frame, not a component library.

## Execution Path

T1 alone (the mark model, zero behaviour change, goldens the proof) → then T2 and T3 in order (they share the scale
interpolator) → HG1 → T4 (recast, the largest) → HG2 → T5 (morph_to; reuses T3 of P47) → HG3 → T6 (the gate and the
grammar's legality, which can land beside T4/T5) → T7 (doctrine + Tokyo) → HG4 → render only on the operator's word.

T1 is the only slice that touches every builder. It lands alone, on its own commit, with the golden suite as its acceptance -
if a single golden byte moves, the model is wrong and nothing else starts.

## Patterns To Mirror

- **The kinetics module discipline** (P43/P47): a pure `.mjs` with its dials at the top, tagged `[DERIVED: …]` or with a
  source on disk, node tests for the maths, inlined into the template by `sync_kinetics.py` between `KINETICS:BEGIN/END`
  markers, behind a `kinetics.*` flag that is OFF in the template's `KINETICS_DEFAULTS` and ON for compiled timelines.
- **The page species grammar** (P47 T2/T6): a kind in `SPECIES_KINDS` + `PAGE_SPECIES`, its fields validated by name in
  `_validate_page_fields`, its events credited in `SPECIES_EVENTS`, its browser behaviour probed through `window.__lpProbe`.
- **The seek test** (P43): frame N evaluated directly equals frames 0..N stepped, bit-identical.
- **The flag golden** (P39/P43 T6): a new capability gets a `FLAG_FRAMES` entry so its first frame is a byte-checked
  artifact, and the base goldens carry no flag.
- **E45's park choreography and E50's clock** for when a transition may fire: never over a build, never inside the last
  0.5 s of a page's life.

## Task Slices

### T1: The mark model - every builder emits keyed marks; nothing changes on screen
- Status: pending
- Owner: parent (the shared boundary; `implementation_luna` may take the bars/combo builders once the line's shape is set)
- Depends on: none
- Write set: `docs/content-video-engine/samples/scene-evidence-player.template.html` (`buildLedgerLine`, `buildLedgerBars`,
  `buildLedgerCombo`, `buildLedgerDecline`, `buildLedgerRace`, `paintLedger*`, `st` shape, `__lpProbe`),
  `content/video_engine/tests/test_page_performs.py`
- Acceptance: (1) each builder returns `marks: [{key, role, geom, el}]` where `key` is `s<si>:<index>` for a datum,
  `axis|tick|ylabel|name|src` for furniture, and `geom` is the numbers the paint step needs (a point, a rect, a path's
  points) - the ELEMENTS and the attributes written are exactly what they are today; (2) `paintLedger*` reads geometry from
  the marks rather than from closures; (3) `st.linePts` and every species target still resolve; (4) the whole golden suite
  is byte-identical and `test_page_performs.py` passes unchanged
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_page_performs.py content/video_engine/tests/test_morph.py -q`
- Evidence: pending

### T2: The state store and `rescale` - two states on one page, the axes retarget
- Status: pending
- Owner: parent
- Depends on: T1
- Write set: `scripts/ledger_page.py` (`resolve_state`), `scripts/build_scene_timeline_f.py` (`chart_to` in
  `SPECIES_KINDS`/`PAGE_SPECIES`, `_validate_page_fields`, `world.page_states`), `scripts/kinetics/chartxf.mjs` (new: the
  scale interpolator and the keyed tween), the template (the state store, `paintChartXf`), `tests/kinetics/chartxf.test.mjs`,
  `tests/test_chart_transitions.py`
- Acceptance: (1) `chart_to {at, dur, kind: "rescale", ymin?, ymax?, window?}` compiles to a second spec on the scene;
  (2) at `t` before `at` the page is state A exactly (byte-identical to no transition), after `at + dur` it is state B
  exactly; between, every shared mark is at the min-jerk blend of its two positions; (3) tick labels cross-fade, new ticks
  write in ink; (4) the seek test holds; (5) `STATE_MAX` 3 enforced by the compiler with a named error
- Validate: `node --test content/video_engine/tests/kinetics/chartxf.test.mjs`; `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T3: `extend` - additional points draw on at the pen's speed
- Status: pending
- Owner: `implementation_luna` (bounded; the interpolator exists after T2)
- Depends on: T2
- Write set: `scripts/kinetics/chartxf.mjs`, the template, `tests/test_chart_transitions.py`, `scripts/ledger_page.py`
- Acceptance: (1) `chart_to {kind: "extend", to_index | series}` where state B's window carries points A did not: the
  shared marks rescale over the first `EXTEND_RESCALE` share of the clock, then the new segment draws from the last shared
  datum by `strokeFrac` (the two-thirds law), the nib visible, landing exactly on the new last datum; (2) a new SERIES
  extends the same way (it draws from its first point); (3) the value labels of new points write as the nib passes, never
  before; (4) the seek test holds; (5) a flag golden `ledger-page@extend`
- Validate: `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T4: `recast` - the chart type changes by a keyed tween
- Status: pending
- Owner: parent (the correspondence rules are architecture; HG2 decides whether it ships)
- Depends on: T2 (and T3's dials)
- Write set: `scripts/kinetics/chartxf.mjs` (the mark correspondence), `scripts/ledger_page.py` (`RECAST_PAIRS` and the
  legality error), `scripts/build_scene_timeline_f.py`, the template, tests
- Acceptance: (1) `chart_to {kind: "recast", variant}` between a LEGAL pair only - the compiler names the illegal pair and
  the reason ("a 316-point line has no 5-bar correspondence: use morph_to or a cut"); (2) matched keys tween geometry (a
  line point ↔ a bar's top-centre), area marks grow from the zero line, unmatched furniture enters/exits by the spring;
  (3) sign survives the recast (a drop is down and blood red in both forms - E28); (4) the labels never overprint through
  the middle of the tween (§9.23b holds at every `t`, not only at the ends); (5) the seek test; a flag golden
- Validate: `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_golden_frames.py -q`; `node --test content/video_engine/tests/kinetics/chartxf.test.mjs`
- Evidence: pending

### T5: `morph_to` - ARAP between two shapes on the page
- Status: pending
- Owner: `implementation_luna` (bounded: the mesh and the invariants exist from P47 T3)
- Depends on: T1
- Write set: the template (`morphOn` generalised from the page ENTER to a species), `scripts/kinetics/arap.mjs` (only if a
  new source shape needs a mesh), `scripts/build_scene_timeline_f.py`, `scripts/measure_morph.py`, `gate_motion_density.py`
  (M17 per morph, not per page), tests
- Acceptance: (1) `chart_to {kind: "morph_to", from: <element|shape>, dur}` morphs mid-page with `det J > 0` at every
  sampled `t`; (2) M17's three invariants (centroid, axis, oriented area) are measured PER morph and reported; (3) the
  source may be a named page element (R26-16: the planted element, the tie) or a chart state; (4) with
  `kinetics.arap_morph` off the transition degrades to a `recast` or a cut of the same length, and the frame is
  byte-identical to that; (5) the seek test
- Validate: `python -m pytest content/video_engine/tests/test_morph.py content/video_engine/tests/test_chart_transitions.py -q`
- Evidence: pending

### T6: The gate - M23, the transition as a landing, E50's clock restarted
- Status: pending
- Owner: `junior_developer` (explicit, small; the rules are written here)
- Depends on: T2 (the timeline shape)
- Write set: `scripts/gate_motion_density.py` (`_transitions`, `_transition_gate` M23, `_landings` += the transition,
  `_deployed_lives` += the transition as a data mark, `SPECIES_EVENTS["chart_to"]`), `tests/test_gate_motion_density.py`,
  `docs/GATES-REGISTRY.md`
- Acceptance: (1) **M23** lists every declared transition with its scene, kind and clock; WARN when a transition fires
  inside a page's build beat or within 0.5 s of its exit; FAIL when a page carries two states and no `chart_to` to move
  between them; (2) a transition's landing time counts for E51's push tie (M22) and for M11's annotation window; (3) E50's
  deployed clock restarts at a transition's end (M21 reads the new state's last data mark); (4) the registry documents M23
- Validate: `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q`
- Evidence: pending

### T7: The doctrine and the Tokyo application
- Status: pending
- Owner: parent
- Depends on: T4, T5, T6
- Write set: `docs/portable/OPERATOR-RULINGS.md` (E53 candidate: *a chart changes state; it never cuts to another chart of
  the same data*), `docs/content-video-engine/CAPABILITIES.md`, `29-EVIDENCE-MOTION-STANDARDS.md` §9.28,
  `tokyo-tea-break/build_short.py`, `tokyo-tea-break/SHOT-TABLE-V3-PROPOSAL.md`
- Acceptance: (1) the ruling states when each verb is right and when a cut still wins; (2) Tokyo v3 uses at least two verbs
  on beats they earn - the candidates: **extend** on "and it's been selling since February" (the tail arrives as new data
  rather than a redraw of data already on the page), **recast** on "here's what nobody says: the money went home" (the
  holdings line becomes the monthly-change bars in place, which is what the fourth watch actually asked for and what the
  ring page now does with a second object), **morph_to** for R26-16's planted element; (3) the motion gate PASSes with M23
  clean; (4) stills for the watch
- Validate: `python build_short.py` in the Tokyo folder; `python content/video_engine/scripts/measure_frozen_frames.py <build>`; the gate report
- Evidence: pending

## Verification

- `node --test content/video_engine/tests/kinetics/*.test.mjs` - the interpolators, the seek test, the correspondence.
- `python -m pytest content/video_engine/tests -q --ignore=content/video_engine/tests/test_history_v4_pipeline.py --ignore=content/video_engine/tests/test_pipeline.py`
  (the two pipeline modules carry pre-existing collection errors; 57 further failures in the finance-whiteboard, production
  console and audio-synth modules pre-date this plan and are not its lane).
- `python content/video_engine/scripts/sync_kinetics.py --check` - the module and the template in sync.
- `python content/video_engine/scripts/build_docs_layers.py --check` - the eight generated layers.
- The golden suite is the contract: byte-identical for every page that declares no transition, at every slice.

## Evidence And Handoff

Each slice records: the exact commands and their counts, the golden verdict, the gate rows for any rebuilt Tokyo build, and
the stills sent for a human gate. A slice is not complete on a subagent's summary - the diff and the artifact paths are the
proof (AGENTS.md §9).

## Risks

1. **T1 moves a pixel.** The mark model touches every builder. Mitigation: T1 changes no element, no attribute and no order
   of writes - only where the numbers come from; the golden suite runs before anything else lands, and a single moved byte
   stops the plan.
2. **Recast reads as a new chart** (HG2's question). It may simply not work at 9:16 for a dense series. Mitigation: the
   legality rules keep it to keyed pairs; if HG2 says no, T4 stays behind its flag and `morph_to` plus a cut carry the
   feature - the plan still delivers three of the four verbs.
3. **Size and load time.** Three states per page = three mark sets in a 40 MB player. Mitigation: `STATE_MAX` 3, marks for
   an inactive state hidden (`display:none`, not removed), and a measured load-time budget recorded in T2's evidence.
4. **Purity.** A transition that reads the previous frame breaks the seek test and the renderer. Mitigation: the seek test
   is an acceptance row on T2, T3, T4 and T5, not a final check.
5. **Doctrine drift.** A page that can change shape will be asked to change shape too often. E50 already bounds the clock
   and E25 bounds the intent; T7's ruling must say plainly that a transition is how a chart LEAVES, not a way to keep it.
