---
id: P48-CHART-TO-CHART-TRANSITIONS
title: Chart-to-chart transitions as a first-rate feature - a chart changes STATE (redraw, rescale, extend, recast, morph) and never cuts
status: running
operation: feature
risk: elevated
owner: parent
branch: main
created: 2026-09-07
updated: 2026-09-10
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

## What row 2 was supposed to do, and why it does not (2026-09-07)

The operator, on the row-2 frame: *"you still failed to actually make a new chart here. Why? Because we don't have
morph/redraw/etc in the capabilities yet? Is that the plan?"* And then, precisely: *"the problem is that we were supposed to
either morph or undraw that chart, which you did undraw it. Then we were supposed to re-draw or morph the chart to another
entirely different chart/view, not just redraw and relabel the tail."*

That is the correction, and it is a correction of MY reading, not only of the engine's reach. E50 says a chart un-draws **or
becomes the next thing**. The beat is: un-draw the 26-year holdings line, then become a DIFFERENT chart or view. What I built
instead was un-draw, then redraw a piece of the SAME line and label it - which is neither of the two things the ruling names.
The stub was the visible symptom; the wrong choice was the cause.

The measurement, for the record, because it also rules out the lazy fix: the February-June tail is **5 of 316 points, 1.27 %
of a 26-year x-axis**, so redrawing it paints a ~10 px mark that reads as debris. A `focus_zoom` was probed as the only
magnification the engine has and is a ~1.1x camera push; it does not rescue it. So even the thing I built cannot be dialled
into working - the beat needs a different chart, not a better-drawn tail.

**What "the next thing" could be here, and what each needs:**

| the next thing | what it shows | built today? |
|---|---|---|
| the same series, **windowed to Feb-Jun** | the sell-off at full width, the two figures still pinned to their data | **no** - `rescale` (T2) |
| **the monthly change as signed bars** (Feb +14.0, Mar -47.7, Apr +18.3, May -66.8, Jun -26.4 $bn) | the RATE of selling, sign as geometry | the object is derivable from the holdings data; putting it on the same page is `recast` (T4) |
| the holdings line **morphing** into either of the above | one continuous thing, no cut | **no** - `morph_to` (T5) |
| either of the above as a **chart card docked** over the page | the beat lands today | **yes** (`chart_card.py` + a dock) - but it is a card ARRIVING, not the page's chart BECOMING, and the operator has already ruled that a second chart of the same data should not arrive as an evidence dock |

**The operator chose, the same hour:** *"rotate it into a pie chart for example that shows the holdings of top 5 foreign
investors of USA including the japan holdings and animate it to show the 1/10 of the pie that got sold - it's literally all
there for us."* And on the seam: *"we could type-writer backspace the fonts and re-write, then redraw the pie chart. There
are hyperframes and remotion skills for animated pie charts if we need references."*

**The data is there.** `evidence/build_tokyo_evidence.py:121` already receives `rows`, the whole US Treasury TIC Major
Foreign Holders table (it reads `rows["Japan"]`, `rows["United Kingdom"]`, `rows["China, Mainland"]`, `rows["Grand Total"]`
out of it today). The top five and Japan's -$122.6B are a few lines from an object; no fetch.

**Half the seam is there too.** `retitle` already erases the old title glyph by glyph over `PS.ERASE_S` and writes the new
one - the typewriter backspace is built for a page's title, and the same `eraseFactor` serves any glyph run.

**What is NOT there, and one of it collides with our own doctrine:**

1. A **pie/share builder**. `ledger_page.py` refuses it BY NAME today - `"shares": "no chartable values: 'shares' is a
   donut; no page variant takes it"` - and **E53 §1** ranks angle and area at the bottom of the perception hierarchy, which
   is the reason that refusal exists. This beat is a legitimate exception and must be written as one, not slipped past:
   the hierarchy's objection is to COMPARING many slices, while this page makes a part-of-one-part claim ("a tenth of
   Japan's holding went"), which a circle states instantly. **E53 §1 needs an amendment naming the exception and its
   bounds** (a part-to-whole claim about ONE highlighted slice; never a general comparison; the sold wedge carries its own
   figure so no angle has to be estimated) before the builder ships.
2. The **recast into it** (T4): the line un-draws, the title backspaces and rewrites, the pie draws on, then the wedge equal
   to Japan's -$122.6B peels out and goes blood red (E28: the loss is geometry AND colour). This is the plan's `recast`
   with a new target builder, and it is now T4's acceptance case.
3. References to read before building the wedge: the HyperFrames harvest's chart components
   (`content/video_engine/hyperframes/compositions/components/`) and the remotion-ui intake - both are REFERENCES, and the
   standing rule is that mechanisms port and code does not.

So the first verb after T1 is **T4 (recast)**, not T2 (window), and its acceptance is this beat. Until it lands row 2 ships
as the two treasury figures standing where the line was - honest, and not pretending to be a chart - with the redraw
commented out in `build_short.py` giving this reason.

## Amended 2026-09-10 - what the Bravos reference adds (`sources/reference_analyses/bravos-china-just-triggered-a-new-world-order/REPORT.claude.md`)

Recall: doc 46 §46.7 (events are not cuts - Bravos changes the composition 2.5x a minute and the picture 6x; every
verb here is a BUILD on a held page, never a new plate); E53 §1 second amendment (the census exception, 2026-09-10);
`docs/research/tech/TREEMAP_READABILITY_RESEARCH_BLUEPRINT.md` §7.6 (Sondag et al. 2018: a re-partitioned layout
flickers; Bravos scales and translates the whole card instead - PLAUSIBLE tier: the paper is not on disk, the frames are).

1. **The legal pair for the keyed tween (T4b) now has a reference and a name.** Bravos shots 99-105: a five-series line
   chart names each line at its end (terminal tags), the tags GROW value bars at the line ends (104), then the page
   recasts into a horizontal bar chart of the current values (105). Cardinality n series -> n bars, keyed by series -
   the 1:1 correspondence the plan's Not Building demands. T4b's acceptance case is this pair: `multi-line (n) <-> bars
   (n)`, the bar growing from the line's end at the tag, the line un-drawing by length as the bar slides to the common
   baseline. The Fed-vs-yields page is our instance (two lines -> two bars).
2. **A new verb, `park` (T2b).** Bravos shot 91: the finished treemap is not re-laid-out or dismissed; the WHOLE chart
   scales to ~0.75 and translates up as one affine transform, holding every cell and X in place while the next diagram
   enters below. E50's "becomes the next thing" has a third honest form: the chart makes room. `chart_to {at, dur, to:
   "park", scale, anchor}` = state B is state A's marks under one affine transform into the page's declared quiet zone
   (`page_boxes`), the title carried; never a re-layout of existing keys (the stability rule). Rides on T2's state
   store; no interpolator beyond the transform.
3. **`extend` by series has its reference.** Bravos shots 29-30: production draws first, consumption draws on after it,
   on its word - T3 (2), a new series drawing from its first point. Also 102: the fifth line (China) added after the four.
4. **The stability rule for every verb:** a transition never recomputes the layout of a key that exists in both states
   unless the verb IS a rescale; a `recast`/`park`/`extend` moves keys by transform or draws new ones. Written into T6's
   M23 as a WARN when a shared key's geometry changes under a non-rescale verb.

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
  as one continuous thing, or as a jump? **Ready 2026-09-10:** `steel-and-paper/build-f/chart-transitions-proof.html` on
  :8739 (`chart-transitions-proof`) - the Tokyo holdings page, rescale at 8 s, extend at 13 s; the frames were sent.
- **HG2 (after T4):** the operator watches `recast` - does a line becoming bars read as the same data, or as a new chart?
  This is the gate that decides whether recast ships or stays an experiment. **Stills sent 2026-09-07** (the holdings
  line leaving, the pie drawing on, the wedge peeled): the question for the watch is whether the hand-over reads as one
  page thinking, and whether the keyed tween (T4b) is worth building at all after seeing it.
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

**Reordered 2026-09-07 (operator-approved), because the beat that is waiting is a RECAST, not a window change:**
T1 alone (the mark model, zero behaviour change, goldens the proof) → **T4 recast** with the pie/share builder and the
top-five holders beat as its acceptance → **HG2** (does the line becoming a pie read as the same data?) → T2 and T3
(rescale, extend - they share the scale interpolator) → HG1 → T5 (morph_to; reuses P47 T3) → HG3 → T6 (the gate and the
grammar's legality, which can land beside T4/T5) → T7 (doctrine + Tokyo) → HG4 → render only on the operator's word.

T1 is still the only slice that touches every builder. It lands alone, on its own commit, with the golden suite as its
acceptance - if a single golden byte moves, the model is wrong and nothing else starts.



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
- Status: complete (2026-09-07)
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
- Evidence: `lpMark` / `lpMarkDatum` + `st.marks` / `st.markBy` / `st.plot` in the template; every builder registers as it
  draws (`b:<i>` a bar datum, `s<si>` a series' stroke with its `geom.pts`, `r:<j>` a race row, and role keys `axis`,
  `tick:<n>`, `ylab:<n>`, `axislabel`, `rule:<n>`, `rulelab:<n>`, `xtick:<n>`, `xlab:<i>`, `val:b:<i>`, `name:s<si>`,
  `callout`, `title`, `sub`, `src`); `__lpProbe` reports `marks` as `{key, role, geom}`.
  `python -m pytest ...test_golden_frames.py ...test_page_performs.py ...test_morph.py -q` -> **54 passed**, the goldens
  byte-identical (49 before, +5 new). Two new tests in `test_page_performs.py`: the mark model over the line golden (keys
  unique; the `title|sub|src|axis|tick|ylabel|line` roles all present; every stroke's mark carries EXACTLY the points its
  path resolves targets against), and a parametrized browser proof for **the four builders no golden covers** - story,
  combo, decline, race - asserting each builder's LAST registrations, so a throw inside one would fail it.
- Deviation from acceptance (2), recorded rather than faked: **no `paintLedger*` read a builder closure to begin with.**
  Every paint step already reads a builder-built record on `st` (`st.bars`, `st.paths`, `st.hlines`, `st.combo`, `st.dec`,
  `st.race`), so the row asked for a change that the code had already made. T1 therefore keys those records instead of
  rewriting the paint steps, and every mark carries `rec` - the record it indexes. That is also why the goldens could stay
  byte-identical: not one attribute write moved.

### T2: The state store and `rescale` - two states on one page, the axes retarget
- Status: complete (2026-09-10)
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
- Evidence: 2026-09-10 - `kinetics/chartxf.mjs` (xfLerp / xfPoint / xfPath / xfFade / xfInside / xfRect, dials XF.LEAVE and
  XF.ARRIVE) synced as the ninth region, **6 node tests**; the compiler: `chart_to {to: "rescale", ymin?, ymax?,
  window?}` - the state is DERIVED from the page's own series by `rescale_state` (the window sliced with `window_offsets`
  recorded, `axes.domain` / `axes.xdomain` set, the page's builder kept, month labels for a months-wide window, three
  at most) and appended by `derive_rescale_states` under STATE_MAX; the player: the line builder honours `axes.domain` /
  `axes.xdomain` (opt-in), every line and bars state keeps `st.scale`, `lpPaintRescale` re-projects the standing line
  from its DATA on the clock, lerps ticks / labels / rules / names / bars by value or key, fades leaving values by
  XF.LEAVE and arriving ones by XF.ARRIVE, and `lpRestoreState` puts every written attribute back when no rescale is
  on (the seek test); `lpMarkDatum` resolves against the ACTIVE state through the window offset, so a `figure` after
  a rescale lands on the right datum and a dropped one does not fire; the words stay (a rescale rewrites no sub or
  source). **22 transition tests** (grammar, the derived state, STATE_MAX / off-page refusal, the browser proof - before
  exact, mid moving with leaving ticks fading and no double line, after the derived state exactly with the standing
  path restored - and the seek test), **goldens byte-identical (68)**, kinetics sync 8/8. The frames: the Tokyo holdings
  page, the 26-year line becoming its Feb-Jun 2026 window in place (`scratchpad/frames/rescale-final.png`, sent to the
  operator). Deviations, named: the bars branch is written by the same mark-key law but proven only on the line (no bars
  page rescales yet); `decimal_year_label` truncated a four-decimal February to January - fixed with a hundredth of a
  month's tolerance, goldens unmoved; acceptance (2)'s "byte-identical to no transition" holds by the restore, checked
  through the probe (`built0`), not by a golden of the transition itself - the flag golden comes with T3.

### T2b: `park` - the chart makes room by one affine transform (Bravos shot 91)
- Status: complete (2026-09-10)
- Owner: `junior_developer` (bounded: a transform on the state store T2 builds; the quiet-zone box exists in `page_boxes`)
- Depends on: T2
- Write set: the template (`lpPaintStates` park branch), `scripts/build_scene_timeline_f.py` (`chart_to.to == "park"`,
  fields `scale`, `anchor: quiet|top|bottom`), `scripts/ledger_page.py` (the parked box from `page_boxes`), tests, a flag
  golden `ledger-page@park`
- Acceptance: (1) on the word the whole chart (plot, axes, labels, marks, any X or ring on it) scales to `scale` (default
  0.72) and translates into the anchor box on a min-jerk clock, the title staying; (2) no key's relative geometry changes
  (the affine is one matrix - measured: every mark's centre maps by the same transform within 0.5 px); (3) the freed
  region is reported on `__lpProbe` so a dock, a `flow` or a `figure` can take it; (4) the seek test; (5) goldens
  byte-identical without it
- Validate: `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: 2026-09-10 - `chart_to {to: "park", scale?, anchor?}` (scale in [0.3, 0.95], default 0.72; anchor top | bottom |
  left | right, default top - the corner the chart keeps); NO state is derived: the ACTIVE chart svg takes one CSS scale
  about that corner on the min-jerk clock and holds it until the next transition (`lpPaintPark` / `lpUnpark`; a
  single-state page parks too). The stability rule holds by construction - one transform on the whole svg, so every
  mark, tick, ring and X keeps its place inside the chart; datum targets map through it because `stageBox` reads the
  transformed rectangle (the test proves a datum lands at corner + 0.7 x its offset); the title stays; the words stay.
  Deviations, named: the parked chart shrinks toward a corner of its own box rather than travelling to a page band -
  the room it opens is the rest of its box (Bravos 91 is exactly this: the treemap up and smaller, the diagram below),
  and the freed region is not yet reported on `__lpProbe` (the box is the chart's minus the parked corner - T6/T7 add
  the probe line when a species needs it). **39 transition tests** (grammar; no state derived; the browser proof -
  between full and parked mid-clock, 0.7 of itself anchored at its top-left with the title unmoved, the datum through
  the transform, held six seconds later; the seek test with an unpark on a seek back). Goldens byte-identical (68).
  The proof page parks at 17.5 s (`scratchpad/frames/park-sheet.png`).

### T3: `extend` - additional points draw on at the pen's speed
- Status: complete (2026-09-10)
- Owner: `implementation_luna` (bounded; the interpolator exists after T2)
- Depends on: T2
- Write set: `scripts/kinetics/chartxf.mjs`, the template, `tests/test_chart_transitions.py`, `scripts/ledger_page.py`
- Acceptance: (1) `chart_to {kind: "extend", to_index | series}` where state B's window carries points A did not: the
  shared marks rescale over the first `EXTEND_RESCALE` share of the clock, then the new segment draws from the last shared
  datum by `strokeFrac` (the two-thirds law), the nib visible, landing exactly on the new last datum; (2) a new SERIES
  extends the same way (it draws from its first point); (3) the value labels of new points write as the nib passes, never
  before; (4) the seek test holds; (5) a flag golden `ledger-page@extend`
- Validate: `python -m pytest content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: 2026-09-10 - `chart_to {to: "extend", to_index | series}`: the compiler grows the CURRENT window (the page's
  whole series or the last rescale's) to `to_index` and records `from_index` (the last shared datum, in the page's
  indexing), or reveals a `later: true` series (`ledger_page._dense_block` keeps such a series off the page's own
  chart; `rescale_state(..., reveal=k)` puts it on the derived one); `lpPaintExtend`: the first XF_EXTEND.RESCALE (0.45)
  of the clock is T2's rescale (the target's line hidden), then the target stands and EVERY path of the extended series
  - the muted history and the highlighted tail alike - is drawn to the pen: `capFrac` at the shared datum plus the
  remainder by `strokeFrac` (the two-thirds law), the nib visible, through `cs.extendCap` in lpPaintChart; the
  boundary is invisible because the re-projected geometry IS the target's. **32 transition tests** (grammar; the grown
  window and the shared datum; a later series off the page until revealed; the browser proofs for to_index and for a
  later series - phase 1 moving with the target's line undrawn, phase 2 the target standing with its line short of
  the end and the nib on it, after fully drawn with the cap released; the seek test), goldens byte-identical, and the
  plan's flag golden as a SURFACE golden: `ledger-extend` (the golden series windowed at 8 s and extended at 12 s,
  judged at 13.05 s mid-tail - and it caught a cap applied to the first series alone: a window that grows grows for EVERY series (6de864f); its derived states come from the compiler off a temp episode, so the golden proves the
  compiler and the player together). Frames: `scratchpad/frames/extend-sheet2.png` (sent). One defect the frames
  caught and the tests then pinned: the muted history path ran ahead of the pen (the cap was applied to the
  highlighted path only) - now every path of the series caps itself at its own shared datum.

### T4: `recast` - the chart type changes by a keyed tween
- Status: **the hand-over ships (2026-09-07); the keyed tween for the legal pair ships (T4b, 2026-09-10)** - HG2 answered
  by the operator on the proof page ("great mechanics on the extensions/transformations/rescales")
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
- Evidence: **196 passed**, the goldens byte-identical. Three commits: the mark model (T1), the share page and the
  `peel` species, and the recast. Shipped: `;then=<series>:<variant>` on a plate id -> `world.page_states` (a second
  FULL page spec, validated like the page's own, `STATE_MAX` 3 enforced by name); `chart_to {at, dur, to: "recast",
  state}`; `lpPaintChart` (paintLedger's build beat, lifted out unchanged) + `lpPaintStates`; a new `share` builder and
  the `peel` species; `fetch_top_holders.py` and `ev-top-holders-v1.series.json`.
- **Deviation, named rather than pretended: the recast that shipped is a HAND-OVER, not a keyed tween.** The plan's own
  Not Building refuses a tween between mark sets with no honest 1:1 correspondence - "a 316-point dense line has no
  5-bar correspondence" - and the beat the operator chose is exactly that pair, 316 points becoming 5 wedges. So the
  verb is built the way E50 already says a chart leaves: the standing state runs its own build law BACKWARDS (which is
  what an un-draw is, for every builder, for free) and the named state then draws on by its own law, on the same page,
  with the title, sub and source rewritten by the hand that rewrites a title. That is the operator's own description of
  the beat - *"we could type-writer backspace the fonts and re-write, then redraw the pie chart"* - and it needs no
  correspondence to be honest. **The keyed tween for LEGAL pairs (line <-> combo's line, story bars <-> combo's bars)
  is not built** and is now T4b, after HG2: `RECAST_PAIRS`, the mark correspondence in `chartxf.mjs`, and the flag
  golden. Acceptance rows (2) and (4) belong to T4b; (1), (3) and (5) are met by what shipped.
- **T4b's acceptance case (2026-09-10): the Bravos pair.** `multi-line (n series) <-> bars (n)`, keyed by series: the
  terminal tag grows a value bar at the line's end, the line un-draws by length while the bar slides to a common
  baseline and the axis retargets; `RECAST_PAIRS` names it; the Fed-vs-yields page (two lines -> two bars of the
  current yields) is the Tokyo instance for T7.
- **T4b evidence (2026-09-10): `chart_to {to: "recast", state, keyed: true}`.** The compiler admits it on a legal pair
  only - `RECAST_PAIRS = (("dense-line", "story"),)` - and refuses by name otherwise ("dense-line -> share has no honest
  key correspondence ... use the plain recast, morph_to or a cut"; "4 line(s) and 2 bar(s) - a keyed recast needs one
  bar per series"). The player (`lpPaintRecastKeyed`, `KEYED.TAG` 0.3) runs two phases on ONE clock, raw `u`: phase 1,
  each line's terminal NAME gives way to its terminal VALUE (the number its bar will be, born at the name's settled,
  pushed-apart y - so four values never overprint each other or the tag chips); phase 2 on the min-jerk clock, the
  line leaves by its HISTORY (the dash window slides toward the tail: what stays is the last value), its end and its
  value travel to the bar's top-centre, the bar grows from the common baseline beneath them (`scaleY(v)` about its
  base), A's furniture leaves over the first half and B's arrives over the second, the bar's name comes up under it;
  at the clock's end the target stands exactly as built and `lpRestoreState` takes the transform and the furniture
  opacities off (a seek to any t paints one frame). The words rewrite as every recast's do (the sub and source erase
  and rewrite). Deviation from the acceptance's wording, stated: the value bar does not grow AT the line's end and
  then slide - with a non-zero-based domain a bar from the line's end to the floor would not be the value (E28), so
  the honest phase 1 is the value, not a bar; the bar grows where it will stand. Frames read at 34.5 / 35.4 / 35.9 /
  36.4 / 36.9 / 37.6 s of the proof: four values stand separated at the ends, the lines retreat from their starts,
  the tails fly to the bar tops as the bars rise, the built page reads (labels Memory / Chips / Mega-cap / S&P 500);
  the first cut's two overprints (120.8 over 121.5, 712.5 over "our layer") are what moved the value to the name's
  place. Life check: 90,784 px change between 38.0 and 38.6 s on the built bar page (the page's idle). Golden
  `ledger-keyed` (the divergence page becoming its four bars, mid-flight) added; the 12 others byte-identical.
  `test_chart_transitions.py` 42 (three new: the legal-pair refusals, the lines become their bars on one clock, the
  seek), `test_golden_frames.py` 13. Proof page :8739 rebuilt with a second scene (the keyed recast at 35 s).
  Acceptance rows (2) and (4) are now met for the legal pair.
- Two faults the FRAMES caught, both fixed at the cause: the sub and source went on describing the chart that had left
  (a caption lying about the page - they are rewritten with the chart now), and the line's un-draw ran on the pen's
  two-thirds law backwards, which on a dense series stands still for most of the clock and then vanishes (a line leaves
  by LENGTH, and in the reverse order it was drawn, so a highlighted tail does not float off the end as a stray mark).

### T5: `morph_to` - ARAP between two shapes on the page
- Status: **complete for the chart-state source (2026-09-10)**; the planted-element source (R26-16, the tie) stays open as T5b - see the deviation
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
- Evidence (2026-09-10): `chart_to {at, dur, to: "morph", state}` - the AREA UNDER THE STANDING LINE becomes the area
  under the target state's line by ARAP (`kinetics/arap.mjs`'s strip mesh, the same mesh as P47 T3's page-enter morph),
  mid-page, on one clock. The compiler admits it between two line pages only (`MORPH_BUILDERS = ("dense-line",)`) and
  refuses by name otherwise ("dense-line -> story: a morph moves the AREA UNDER A LINE into another ... n lines -> n bars
  is the keyed recast; anything else the recast or a cut"). The player (`lpStrip`, `lpMorphFor`, `lpPaintMorphTo`,
  `lpPaintMorphHold`, `XF_MORPH.LEAVE` 0.3): the first 0.3 of the clock the standing line un-draws by length in reverse
  while its area fills in the series' own colour (MORPH.FILL_A); the rest of the clock the filled strip morphs (min-jerk)
  into the target's area, det J > 0 at every sampled frame, the standing axes leaving over the morph's first half and the
  target's arriving over the second; then the target BUILDS on its own law and the fill leaves with the build, as the
  page-enter morph's does. The strip is built once per (from, to) pair at first need from geometry fixed at load - pure;
  hidden whenever no morph is on or holding (a seek to any t paints one frame). **M17 per morph:** `_morph_events` /
  `_morphs` in the gate list a page's enter morph (keyed by its scene id, as before) and every morph_to (keyed
  `scene@at`); `measure_morph.py` seeks each morph_to to 0.65 of its clock and reads `__morphInvariants("from>to")`;
  M23 counts a morph as a data transition (its end a landing and a data mark). **Flag off:** with `kinetics.arap_morph`
  off a morph_to falls through to the recast hand-over of the same length - the test hashes three frames of a `morph`
  build against a `recast` build and they are identical. Frames read at 49.5 / 50.4 / 50.9 / 51.4 / 52.3 / 54.5 s of
  the proof (the Tokyo holdings line -> the Fed-vs-yields line, two different series on disk): the holdings area fills
  as its line leaves, the filled shape becomes the yield line's shape as the $bn axis goes and the % axis comes, the
  yield line draws over the strip's top edge and the fill leaves - one thing changing shape. Invariants on the test pair
  (the four-line page -> its first series alone): centroid, axis and area inside M17's bounds, min det > 0, end error
  < 1e-3. `test_chart_transitions.py` 47 (five new: the legal pair, the morph and its invariants, the seek, the flag-off
  byte-for-byte, measure_morph per morph), `test_gate_motion_density.py` 62 (+1: M23 counts a morph, M17 keys per
  morph), `test_morph.py` green, 13 goldens byte-identical. Proof page :8739 gains a third scene (the morph at 50 s).
- **Deviation, stated: acceptance (3)'s planted-element source (R26-16, the tie) is not built here.** A morph_to's
  source is a CHART STATE (the standing line's area); the tie is an element of the outgoing WORLD (a Flow still), which
  needs the page-ENTER morph to take a traced outline in stage px on the outgoing scene's last frame, the morph spanning
  the boundary, the fill sampled from the source's colour (R26-16's own list). That is a separate half-day on the
  page-enter path (`world.morph = {poly: [...]}` + a silhouette tracer for a still) - **T5b**, after HG3's watch of
  what shipped; nothing here forecloses it (the strip mesh takes any x-monotone pair).

### T6: The gate - M23, the transition as a landing, E50's clock restarted
- Status: complete (2026-09-10)
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
- Evidence: 2026-09-10 - `_transitions` / `_states_without_a_transition` / `_transition_gate` in `gate_motion_density.py`:
  **M23** lists every chart_to with its scene, verb and clock; WARN when one fires before the page's build lands
  (`_page_land_offset`) or ends inside the last `TRANSITION_EDGE_S` (0.5 s) of its page; FAIL when a page carries two or
  three chart states and no recast/rescale/extend to move between them (a state built for nothing); no row on a page
  with one chart and no chart_to. A transition's END is a landing in `_landings` (M22's push tie sees it) and a data
  mark in `_deployed_lives` (E50's clock restarts at it) - for `TRANSITION_DATA_KINDS` only: a park moves the chart
  and changes no data, so it is neither. `SRC_M23` + the header row; the registry regenerated (`docs/GATES-REGISTRY.md`
  carries M23). **61 gate tests** (4 new: the listing/PASS, the build-beat and edge WARNs, the orphan-states FAIL and
  the no-row case, the landing + the restarted clock with the park excluded). Deviation, named: acceptance (2)'s M11
  annotation window is untouched - M11 is the FIRST chart's entry and a transition is never that; the stability WARN
  the Bravos amendment asked for (a shared key moving under a non-rescale verb) is a player-side measurement, not a
  timeline read - it belongs with the life check, not this gate.

### T7: The doctrine and the Tokyo application
- Status: **the doctrine complete; the Tokyo application built on :8740 with ONE verb, awaiting HG4** (2026-09-10) - the
  second verb's beat is the operator's choice (see the deviation)
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
- Evidence (2026-09-10): **E58** written (`docs/portable/OPERATOR-RULINGS.md`: a chart changes STATE, never cuts to another
  chart of the same data; the table of five verbs - the sentence that earns each, what moves, what it is NOT for; when a
  cut still wins; the laws every verb obeys) and **doc 29 §9.28 (e)** (the transition grammar under the surface grammar).
  **Tokyo:** `build_short.py` row 2 - on "The Treasury's table" the holdings page RESCALES to the February-June window
  (`HOLDINGS_WINDOW`, a month's margin either side of the peak and the last print) instead of un-drawing, so the sell-off
  the sentence is about stands at full width (the 09-07 note: five of 316 points were a ~10 px stub); the two treasury
  figures then write on the windowed line (the peak on "over a trillion", June on "selling since February"; no month subs -
  the months are the axis now, E52; June writes above its point, it being the plot's floor); the line un-draws on "The
  opponent" (E50: the rescale restarts the clock at 0:22, the title turns at 0:30 - on "Two numbers" M21 read 14.1 s).
  Built BESIDE the watched remake (`TOKYO_BUILD_DIR=build-short-p48`, served by `tokyo-short-player-p48` on :8740; the
  09-09 build on :8738 untouched). Gate: 0 FAIL / 2 WARN (M11 no sound cue on the first chart and M21 s06 0.2 s short -
  both pre-existing in the watched build) / M23 PASS (`s02 rescale 0:21+1.4s`); frozen frames: no run over 0.5 s.
  Stills at 20.8 / 21.8 / 22.7 / 24.5 / 27.0 / 34.6 s sent for HG4. **Found by the stills, fixed at the cause:** page
  species (figure, bracket, spread) were drawn inside state 0's svg and vanished the moment a rescale made the derived
  state active - the two treasury figures were invisible. On a page with chart states the perform layer now draws on its
  OWN svg above every state (`st.performSvg`; a page with one chart draws exactly as it did - goldens byte-identical), a
  figure follows the ACTIVE state's datum through `lpMarkDatum` (a datum the window dropped shows nothing), the layer
  rides the active chart's park, and a cold seek past the rescale no longer inherits the hidden chart's opacity (the
  second still caught that). Test: `test_a_figure_follows_the_active_state_after_a_rescale_and_a_dropped_datum_shows_nothing`.
- **Deviation, stated: one verb on Tokyo, not two.** The candidates named here were written before the verbs existed.
  `extend` on "selling since February" would redraw a tail the page already drew on "watching" (a build_to) - the
  sentence does not earn it. `recast` on "here's what nobody says: the money went home" has 2.2 s before the Meta page
  mounts on "went home" - a recast that stands two seconds is a cut wearing a verb (E58). `morph_to` for R26-16's tie
  is T5b (the page-enter path). The beat that WOULD earn a second verb is the operator's cut to make: the monthly-change
  bars as a keyed/hand-over recast on "The Treasury prints" (row 4) in place of the June-print figure changes what the
  first number IS; or a `park` on "Two numbers" so the fingers land beside the windowed chart instead of on the bare page
  (needs `centred_place` to read the park - the freed-region line). Both are stated for HG4, not forced.
- **Open (a follow-up, not this plan's lane):** brackets and spreads on a page with states are built on the page's own
  geometry and WAIT while a derived state stands (hidden); making them follow the active state the way figures do is a
  bounded slice (`buildPerform` per state, or geometry per frame) - BACKLOG R26-28.

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
