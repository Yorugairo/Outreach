---
id: P61-WHAT-THE-REVIEW-OWES
title: What the review owes - the BUILD group of the 2026-09-15 queue sort: the whole-chart morph first (it unblocks P47 T6/T7 and P48 T5b), then the two 2.5D fixes, the ball's shadows, the melt gathered to a dense point, the verdict stack's choreography and the agenda page, the gallery's speed and its motion examples, and a DESIGN slice for saved states - each slice returning as a queue card with a proof a person can judge
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-15
updated: 2026-09-15
---

# What the review owes

> **APPROVED 2026-09-15** - the operator invoked `/prp-implement P61` after answering the two open decisions (E99 s34); running from T1. Approval is the operator's word; this line records it.

## Summary

The review queue (`docs/content-video-engine/review-queue.v1.json` -> `REVIEW-QUEUE.md`) carries 20 items marked
**owed by the agent**: E99 s14 (`docs/portable/OPERATOR-RULINGS.md:2901`) ruled that *"a lot of what you ask for
doesn't appear to be served or have no proofs ... this is a bad review. i answered a lot of what i could, you need to
create a better pass."* An item reaches the operator only with a proof framed for a viewer - a clip that plays, a
player link that answers, or a crop on what changes - and until then the item is the agent's work, never the
operator's.

The operator sorted those 20 on 2026-09-15 into **assemble** (items whose proof already exists on disk and only has to
be gathered - a separate pass, not this plan) and **build** (items that owe a BUILD before a card can exist). This plan
is the build group, in the operator's order.

Nothing here is a new subsystem. Every slice is a named refusal against a named built mechanism:

| # | what the operator refused | the built thing it lands on |
| --- | --- | --- |
| 1 | the compare-morph is *"an extremely stupid morph"* - a morph must prove the WHOLE data set / chart (E99 s1) | the six `chart_to` verbs (`rescale` **:113**, `extend` **:114**, `recast keyed` **:115**, `morph_to` **:116**, `park` **:117**, `compare` **:28**, with the E64 recast rule at **:27**), `kinetics/morph_a.mjs`, `kinetics/arap.mjs`, `kinetics/contour.mjs`, `kinetics/chartxf.mjs`. **CAPABILITIES:118 is a different thing** - P47 T3's object-becomes-the-chart morph (the page-enter path) - and belongs to slice 2's hand-over, not to the chart-to verbs |
| 2 | the melt and its splash are *"ugly"*; the melt must gather like the vortex into one dense, heavy, vibrating point (E99 s2) | `species/melt.mjs` (`exit: melt[:throw|:splash:chart|:splash:plate]`, CAPABILITIES:37), `kinetics/drop.mjs`, the page vortex (CAPABILITIES:57), the ink bloom (`INTAKE-INK-BLOOM-2026-09-08.md`) |
| 3 | the living ball *"reads glossy"* - it owes shadow, a dark Fresnel rim, a metallic band, one point of deep shadow depth (E99 s3) | the ball's paint in `species/melt.mjs`, `kinetics/drop.mjs`, `docs/research/motion/LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md` (released by E99 s24) |
| 4 | the extruded bar's leave must break its shapes down more (E99 s4); a formed page mounts its charcoal and its leave does not clear its scribbles to cream (E99 s18) | the two 2.5D chart forms (CAPABILITIES:147, P58 T5), the cream mount page enter (CAPABILITIES:26, :64) |
| 5 | the short's evidence wall *"didn't just place them horizontally, we had real choreography"* (E99 s21); the beautified agenda page is *"still owed"* (E99 s16) | the VERDICT STACK's five phases (CAPABILITIES:184, `species/verdict.mjs`, `drawStack`), `species/agenda.mjs` (CAPABILITIES:43) |
| 6 | the gallery *"builds slow, and the examples are only pictures"* (E99 s20) | `build_effects_gallery.py` -> `content/video_engine/effects/gallery/index.html` + `frames/`; the catalogue (CAPABILITIES:318) |
| 7 | *"cant we just make a better engine/editor so that we can have saved states, or build copies of the engine/compiler per agent?"* (E99 s23) | the OVERRIDE SIDECAR (CAPABILITIES:108, P51 T5), HOT RELOAD + the determinism check (CAPABILITIES:109, P51 T4) |

**Slice 1 is first because three other things hang on it.** P47 T6 and T7 are both marked
`Status: blocked on P48` on the operator's 2026-09-10 sentence *"we still don't redraw/rebuild a new chart"*
(`.claude/PRPs/plans/P47-STOP-ACTION-BUILD-ON-AND-THE-CHART-MORPH.plan.md:174,183`); P48 T5b (the morph onto a planted
element) is unbuilt, so its card `p48-hg3-morph-onto-planted` has nothing to watch; and R26-117 (the ball into the next
chart) is the page-level form of the same hand-over. E99 s1 raised the bar under all three at once.

All repo paths below are the MAIN checkout (`C:/Users/Snipe/Downloads/Outreach Program`); `python` =
`C:/Users/Snipe/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe`. This draft was written from the
sweet-villani worktree and copied into MAIN by script (the harness refuses the Write tool against the main checkout's
`.claude/`). No git state was changed while drafting.

## Intent And Acceptance

**Intent.** Turn the seven refusals above into built mechanisms, each returning to the operator as ONE queue card with
a proof a person can judge, so the "owed by the agent" list shrinks by work, not by rewording.

**Acceptance (the whole plan).**

1. Every build slice ends with (a) a GOLDEN for the new behaviour, (b) every pre-existing golden byte-identical
   (`python -m pytest content/video_engine/tests/test_golden_frames.py -q`), and (c) a queue proof on disk - a clip
   through `review_queue_proofs.py --clips --only <item id>` (its source is a golden `surface` + `flags`, or a
   `build` + `page` directory) or a before/after crop through the same file's `diff_box` (which REFUSES a pair whose
   only difference is inside the caption box).
2. Every queue card states, in one plain sentence, the exact time range to watch, what changes in it, and the question
   (E99 s15). No card offers options the record never argued (E99 s14).
3. `python content/video_engine/scripts/gate_motion_density.py <build>` keeps M23 (chart transitions), M31 (the empty
   stage) and M25/M28 at or better than the reading recorded in the slice's Evidence; `gate_one_shot_floor.py` keeps
   M35-M42 where a slice touches a cut.
4. No approved cut is rebuilt (E45). Any change to how an approved cut renders ships behind a kinetics/compiler flag
   whose DEFAULT is today's look until the operator rules; the Japan tariff short and the Tokyo remake are read as
   regression fixtures, never re-authored.
5. `python content/video_engine/scripts/effects_catalog_check.py` 0 failures; `sync_kinetics.py --check` in sync; every
   slice names the `docs/content-video-engine/CAPABILITIES.md` row it changes and that row carries the change.
6. `python scripts/prp_validate.py .claude/PRPs/plans/P61-WHAT-THE-REVIEW-OWES.plan.md` PASS.

**Not acceptance.** An agent's opinion that a proof "reads better". Every slice's Evidence is a path, a frame, a gate
reading or a command tail.

## Scope

- `docs/content-video-engine/samples/scene-evidence-engine.mjs` and its synced regions (the engine).
- `content/video_engine/scripts/kinetics/**` and `content/video_engine/scripts/species/**` (`melt.mjs`, `drop.mjs`,
  `verdict.mjs`, `agenda.mjs`, `morph_a.mjs`, `arap.mjs`, `contour.mjs`, `chartxf.mjs`).
- `content/video_engine/scripts/build_scene_timeline_f.py` (the compiler: new verbs, options, refusals) and
  `ledger_page.py` where a form needs a spec field.
- `content/video_engine/tests/**` (node kinetics tests, pytest, goldens + their sources).
- `content/video_engine/scripts/build_effects_gallery.py` and `content/video_engine/effects/gallery/**`.
- `content/video_engine/effects/cards/*.json` (the catalogue cards for anything new).
- Private, NEW build directories for proofs (never an approved cut's directory).
- `docs/content-video-engine/review-queue.v1.json` + the generated `REVIEW-QUEUE.md`, `CAPABILITIES.md`, `BACKLOG.md`
  rows, and the generated docs layers - parent (docs lane) only.
- `docs/research/runs/p61-*/` - the trace, the design options sheet, run transcripts (gitignored disk-as-bus).

## Not Building

- **The assemble pass.** The queue items whose proof already exists and only has to be gathered
  (`r26-133-drift-idle-paints-nothing`, `r26-125-p57-hg1-measured-defects`, `p56-hg2-one-shot-floor`,
  `p53-hg4-cutout-dock-first-frame`, `p58-hg1-follow-ups`, `p54-hg2-triage-digest`, `p54-hg3-astra-fable-bakeoff`,
  `p46-hg1-hg3-bridge-contract`, `gemini-rerun-vs-split`, `r26-68-span-darker`) run as a separate pass. This plan
  touches none of their write sets.
- **Re-rendering or re-authoring an approved cut** (E45; the Japan tariff short is APPROVED + rendered 2026-09-09, and
  the operator's standing instruction on Tokyo is *"DO NOT ASK FOR A RENDER"*, `docs/agent-memory/operator/tokyo-short-render.md:79-93`).
- **A second engine writer in its own worktree** (E99 s23 refused it outright: *"we already experienced a big
  drift/sprawl mess from using worktrees"*).
- **An SDF / implicit-field rewrite of the morph.** R26-120's research landed UNSOURCED-editorial and its cost figure
  was REJECTED (`docs/content-video-engine/BACKLOG.md:552`); E99 s24 released it as hypotheses only. `morph_a` stays
  the law in this plan; any field blend is a later row with its own goldens.
- **Any editor gate.** E99 s17 closed P51 gates 2 and 3: *"the editor's pretty useless to a human, all i can do is edit
  integers"*, and the timeline comes before any further editor gate. T10 designs saved state, it does not build editor UI.
- **A morph proof built on the compare verb.** E99 s1 refused exactly that shape; the compare verb stays as built.

## Human Gates

One gate per slice - the operator's answer on that slice's queue card. T3 lands TWO cards (the ball into the next
chart, and the morph onto a planted element), so it carries two gates. Each gate gets its row in
`docs/content-video-engine/REVIEW-QUEUE.md` in the same change that frames it (PRP_EXECUTION "PRP Format"), and leaves
that page only with the operator's ruling written to `docs/portable/OPERATOR-RULINGS.md` and back into this plan.

| gate | slice | queue card | the ONE question the card asks |
| --- | --- | --- | --- |
| **HG1** | T2 | `r26-70-compare-morph` (rewritten) | "Watch the two clips end to end. Does it **read as a transformation, not a cut, and read as intentional** (E99 s34)? The entire chart should transform - every series, datum and axis. Approve, or name what cuts or reads as accidental." **RULED 2026-09-15 (E99 s39): line -> bars taken; bars -> line rebuilt in T2b** **HG1b RULED 2026-09-16 (E99 s50): bars -> line approved; closed** |
| **HG2** | T3 | `r26-117-ball-into-the-next-chart` (**created by the parent at T3's dispatch** - it does not exist today; it supersedes the `"missing": true` line on `r26-70-compare-morph`) | "The page melts, balls up, and the ball becomes the NEXT FULL CHART with no cut between. Watch 0:00-0:08. Does the hand-over hold, or does it read as a jump?" **T3 LANDED 2026-09-16: card open (watch, clip 14.6-21.2 s)** **RULED 2026-09-16 (E99 s53): good; the chart-to-ball snap re-timed - T3c** |
| **HG2b** | T3 (the planted-element half) | `p48-hg3-morph-onto-planted` (**exists**; today reads "Missing proof: P48 T5b ... is unbuilt") | "The chart morphs onto a PLANTED element - the prop outline traced from the thing already standing in the world (R26-16's tie). Watch the seam. Does the morph land on the planted thing honestly, or does the seam show?" **T3 LANDED 2026-09-16: card open (watch, clip 14.4-20.3 s)** **RULED 2026-09-16 (E99 s52): the morph fine; the fill may not snap in - T3b** |
| **HG3** | T4a | `p58-hg3-extruded-bar-leave` | "`form-extruded-bar@proof-leave` beside `form-tilted-line@proof-leave`, as clips. Do the prism's shapes break down enough now? Approve, or say 'more'." **RULED 2026-09-15 (E99 s40): approved** |
| **HG4** | T4b | `p58-hg3-forms-mount-not-scribble` | "The formed page arriving by the two-plate cross-fade and by the soak, each leaving by the soak's recede (E99 s35). Watch both enters and the leave. Approve, or name what still reads wrong." **RULED 2026-09-15 (E99 s41): approved** |
| **HG5** | T5 | `r26-118-metallic-ball` | "The ball, before and after: more shadow, a dark Fresnel rim, a metallic band, one point of deep shadow depth. Does it read metallic and heavy now, or still glossy?" **RULED 2026-09-15 (E99 s42): refused - the prior ball + the darkness; T5b** **HG5b RULED 2026-09-16 (E99 s49): the reference body; T5c** |
| **HG6** | T6 | `r26-76-melt-endings-in-motion` | "The melt as the vortex's motion gathered into one dense, heavy, vibrating point, splashing into a full chart / world plate. Watch the gather and the splash. Approve the new default, or keep today's look behind the flag." **PROOF B LANDED 2026-09-16 via T3: card open (watch, both clips)** **RULED 2026-09-16 (E99 s51): the gather approved; the splash becomes a throw - T6b** |
| **HG7** | T7 | `r26-82-verdict-stack-choreography` | "The verdict stack on a short with Steel and Paper's choreography - cards that move, then the burst. Watch it beside the Steel and Paper reference clip. Approve, or name the phase that is still flat." **RULED 2026-09-15 (E99 s43): rails in reading order; T7b** |
| **HG8** | T8 | `r26-80-agenda-page-owed` | "The beautified agenda page - the plate version of the list effect, each row with its catalogued icon stamped after its sentence (E93). Beside today's three plain rows. Approve, or name the change." **RULED 2026-09-15 (E99 s44): approved as a build** |
| **HG9** | T9 | `p55-gallery-speed-and-motion` | "The gallery: its build time before and after, and three effects a still cannot show now carrying a clip. Is it fast enough and clear enough? Approve, or name what is still unreadable." |
| **HG10** | T10 | `r26-84-engine-saved-states` | "Three routes to parallel agents without worktrees, each with its cost and what it breaks, and the agent's recommendation. Which route do we take - or does it need its own plan?" **RULED 2026-09-15 (E99 s47): worktrees with both agents aware; P62 = the register** |

**HG10 is the only gate with options**, and the record argues each (E99 s14's bar). No other card offers a menu.

## Mandatory Reads

**Rulings (read the Apply line verbatim before touching the slice).** `docs/portable/OPERATOR-RULINGS.md` - **E99**
opens at `:2901`. s1 (the whole-chart morph), s2 (the melt gathers), s3 (the ball's shadows), s4 (judged in video; the
extruded bar's leave), s14 (a proof a person can judge), s15 (a card names the moment and the question), s16 (the
agenda page still owed), s18 (mount, not scribble; no clearing to cream), s20 (the gallery), s21 (the verdict stack's
choreography), s23 (saved states or per-agent copies), s24 (the three research runs released), and **s34 at `:3143`**
(P61's own two decisions: the morph's bar is that it reads as a transformation and as intentional; the text may be
rewritten OR morphed; Japan is re-rendered later, not now). Also **E45** (no approved cut is rebuilt), **E47** (a scene's `exit` is the transition INTO it - the reading that made two "hand-off"
clips read as jumps, E99 s19), **E50/E53** (a chart un-draws OR becomes the next thing; a chart changes state, never
cuts to another chart of the same data), **E64** (the recast re-writes or morphs, never cuts), **E88** (the chart
melts, the board stays), **E93** (an agenda row carries a catalogued icon), **E96/E97** (the one-shot floor; a beat is
a recipe), **E99 s25** (`throw=depth` -> `throw=growth`).

**Doctrine.** `docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md` §9.24 (the verdict stack, `:1364`), §9.28,
§9.31 (the page vortex, `:2100`), §9.33 (the chart is the WORLD, `:2217`); `43-SCENE-GRAPH-AND-TRANSFORM.md` §43.5
(the morph - two methods and when each applies; the heading is at **`:62`**, Method B's cotangent weights at `:91`);
`41-LEDGER-PAGE-SPECIES.md`;
`INTAKE-INK-BLOOM-2026-09-08.md:19` (the bloom preset E99 s2 names as an accepted route).

**The record of what is built.** `docs/content-video-engine/CAPABILITIES.md` rows 27, 28, 37, 43, 57, 64, 103, 104,
108, 109, 113, 114, 115, 116, 117, 118, 147, 148, 184, 318. `docs/content-video-engine/BACKLOG.md` rows R26-16, R26-49
(`:455`), R26-70 (`:476`), R26-76 (`:482`), R26-80 (`:486`), R26-82 (`:488`), R26-84 (`:490`), R26-86 (`:492`),
R26-116 (`:548`), R26-117 (`:549`), R26-118 (`:550`), R26-120 (`:552`).

**Plans.** `.claude/PRPs/plans/P48-CHART-TO-CHART-TRANSITIONS.plan.md` (T4/T5 evidence; HG3 at `:185`; the T5b
deviation at `:412` and `:451`; the second-verb note at `:517`), `P47-STOP-ACTION-BUILD-ON-AND-THE-CHART-MORPH.plan.md`
(T6 `:173`, T7 `:182` - both blocked), `P58-THE-2-5D-STAGE.plan.md` (T5 the two forms; HG3),
`P51-THE-ANIMATORS-LOOP.plan.md` (T4 hot reload + determinism, T5 the override sidecar),
`P55-THE-EFFECTS-CATALOGUE.plan.md` (the gallery, HG2), `P52` (T8 the agenda, T9 the melt).

**Gates.** `docs/GATES-REGISTRY.md` - M23 (`:141`), M31 (`:149`), M35-M42 (`:156-163`).

**Process.** `docs/runbooks/PRP_EXECUTION.md` (dispatch mapping, lane write sets, the return contract),
`docs/runbooks/RECALL-RECEIPT.md` (the receipt every proposed mechanism opens with),
`docs/runbooks/RENDER-REGRESSION.md`.

## Execution Path

```
T1 (trace, read-only, NO lock)
  -> T2 the whole-chart morph            [LOCK]  -> HG1   removes P47 T6/T7's BLOCKER (not the watch)
       -> T3 ball -> next full chart      [LOCK]  -> HG2  + HG2b (planted) -> closes P48 T5b
  -> T4a extruded-bar leave              [LOCK]  -> HG3
  -> T4b mount, not scribble             [LOCK]  -> HG4
  -> T5 the ball's shadows               [LOCK]  -> HG5
  -> T6 the melt gathers to a point      [LOCK]  -> HG6   (depends on T5 ONLY - proof A lands in a WORLD PLATE;
                                                   proof B, the full-chart splash, is appended when T3 lands)
  -> T7 the verdict stack choreography   [LOCK]  -> HG7
  -> T8 the agenda page                  [LOCK]  -> HG8
  -> T11 the record (parent, docs lane)

beside them, no lock:
  T9  the gallery (speed + motion examples)      -> HG9
  T10 saved states - a DESIGN sheet, not code    -> HG10
```

**The engine lock.** `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `kinetics/**`, `species/**`,
`build_scene_timeline_f.py` and the player template take ONE writer at a time (PRP_EXECUTION "Lane write sets";
BACKLOG R26-84 `:490` states the same rule). Slices T2-T8 hold it and run strictly one at a time, in the order above.
T1, T9, T10 and T11 do not touch those files and may run beside the lock holder. The parent hands the lock out
explicitly in each dispatch brief and takes it back with the reviewed diff.

**Dispatch (PRP_EXECUTION "Dispatch mapping"; every delegated role runs Opus 5, effort high).**

| slice | route | why |
| --- | --- | --- |
| T1 | `explorer` (read-only) | an open-ended "what does this actually transform" trace across engine + compiler |
| T2, T3, T5, T6, T7, T8 | `implementation_luna` (one at a time) | coherent moderate engine slices with tests and goldens |
| T4a, T4b | `junior_developer` | two small bounded fixes with the lines named, still needing implementation reasoning |
| T9 | `junior_developer` | tooling only, off the engine |
| T10 | `architect_sol` -> parent | architecture; options and costs, the operator decides |
| T11 | parent (Claude/Fable docs lane) | shared files (`CAPABILITIES.md`, `BACKLOG.md`, the queue) are the parent's |
| before every `complete` | `reviewer` | every delegated diff is reviewed before integration |

Human gates, briefs, the diff reads and the completion claim stay with the parent regardless of slice size.

## Patterns To Mirror

- **The chart-to verbs' shape** (`build_scene_timeline_f.py`, `CHART_TO_KINDS`): a verb is a compiler-checked row with
  named refusals (`MORPH_BUILDERS` / `RECAST_PAIRS` refuse any pair they cannot do and POINT at the verb that can). A
  new whole-chart verb refuses by name and names its alternative; it never tweens a pair it cannot key.
- **A painter is a pure function of t** (P51 "the agent's loop"; the compare painter's 18 node tests: u=0 exact source,
  u=1 exact target, identical on two calls). Every new painter gets the same three tests.
- **The region-synced engine** (`sync_kinetics.py --check`): a module is authored once under `kinetics/` or `species/`
  and mirrored into `scene-evidence-engine.mjs` by region. Never hand-edit both. R26-115 is the module-order rule.
- **The outlines are ours** (`kinetics/contour.mjs`, P57 T12c): geometry is measured off the page's own ink by
  canvas raster + marching squares - no font file parsed, no vendored library. T2/T3 reuse it for labels and marks.
- **A golden proves the compiler and the player together** (`ledger-extend` at the mid-tail, `compare-morph@proof-*`):
  a golden names the INSTANT that matters, not just the end state.
- **The melt's own composition** (T12b reused `meltRun` / `meltTextFilterMarkup` from `species/melt.mjs` and changed no
  pixel it paints): a new behaviour composes the existing exports before it adds any.
- **The queue proof pipeline** (`review_queue_proofs.py`): `--clips` renders from a golden surface + flags or a build +
  page in ONE headless browser across the window and pipes to ffmpeg; crops come from `diff_box`, which refuses a pair
  that differs only inside the caption box. Slices produce proofs THROUGH this file, never by hand.
- **The recall receipt** (`docs/runbooks/RECALL-RECEIPT.md`): every proposed mechanism opens with `Recall:` lines
  quoting the hits. `Recall: docs_find 0 hits for "<term>"` is valid; silence is not.

## Task Slices

### T1: THE TRACE - what `recast`, `morph_to`, `compare` and the page-enter morph actually transform today
- Status: complete (2026-09-15) - the trace verified; T2 briefed from it
- Owner: `explorer` (read-only; no engine lock)
- Depends on: none
- Write set: `docs/research/runs/p61-whole-chart-morph/TRACE.md` (gitignored disk-as-bus) ONLY
- Acceptance: a table with one row per transform (`rescale`, `extend`, `recast` plain, `recast keyed:true`,
  `recast keyed:"tags"`, `morph_to`, `park`, `compare`, `page_enter:morph`) and one column per chart part - series
  paths, individual datum marks, the x axis + its ticks, the y axis + its ticks, the tick LABELS, series names/tags,
  the title, the rail, the page's scribble field - each cell `morphed` / `re-written` / `crossfaded` / `cut` /
  `untouched`, every cell carrying a `path:line` in `samples/scene-evidence-engine.mjs`,
  `build_scene_timeline_f.py`, `kinetics/chartxf.mjs`, `kinetics/morph_a.mjs` or `kinetics/arap.mjs`. Plus: the exact
  gap list to "full chart becomes full chart". **Plus the text decision, which E99 s34 handed to measurement:** the
  operator does not mind *"if the text is re-written or directly morphed - both is a transformation"*, so T1 measures
  **BOTH routes** on the same label set and reports numbers, not a preference - (a) the CONTOUR route: `contour.mjs`'s
  cost per glyph at 12 fps (raster at RASTER_S 4 device px per page px, marching squares, Douglas-Peucker, cached per
  (text, face)), measured for a chart's full tick-label count, not one glyph, and whether the frame budget holds;
  (b) the RE-WRITE route: `figure.mjs`'s `figureGlyph` re-writing at the datum (E76 s4, the operator's own *"just
  collapse or melt then re-draw"*), its cost and what it needs from the compiler. Each route's failure mode is named.
  T2 takes the one that READS, on the two readings the bar states; T1 supplies the cost so that choice is not a guess.
  Report "not found in <the places I searched>", never "does not exist".
- Validate: `python content/video_engine/scripts/docs_find.py "chart_to"` and
  `python scripts/sigmap_context.py query "chart_to transform" --top 5` run and quoted in the trace's header; then the
  parent verifies every `path:line` in the table resolves with one `rg` each before T2 is briefed
- Evidence: `docs/research/runs/p61-whole-chart-morph/TRACE.md` (gitignored; written in the worktree, copied into main by
  the parent). Header quotes both recall commands (`docs_find "chart_to"` 20+ hits; SigMap ranks nothing in the engine -
  its index carries no `.mjs` symbols). The 9x9 table (s1) with the compiler's admissions (`C:280` CHART_TO_KINDS, `C:281`
  MORPH_BUILDERS, the line->bars refusal `C:2127-2137`); the gap list (s2, nine items: no verb morphs a bars page; `morph_to`
  moves ONE series (`E:9761` lpStrip) and CROSSFADES the whole axis layer (`E:9799`/`:9801`) though `lpAxisHandOver`
  (`E:9584`) already is the no-cut hand-over; no datum correspondence outside `keyed: "data"`; no rect<->polyline pairing;
  the title never changes on any verb; tick labels re-write only on a recast; `st.xfNow` (`E:9880`) has no whole-chart
  phase; rail and field outside every verb). The text decision measured (s3), same 16-string / 92-glyph label set, HeadlessChrome
  149 on the i9-13900KF: route (a) contour - one morph frame 5.53 ms (6.56 with the DOM write), 12.6x inside the 12 fps frame,
  but a ONE-TIME 121.5 ms prepare (64.2 raster + 57.3 pair) that must land at page build, never on the morph's first frame;
  route (b) re-write - 0.012 ms per frame, no prepare, and the tick-label re-write is ALREADY shipped as `lpWriteText`
  (`E:9567`) through `sweep` (`E:9600-9606`). Failure modes named for both (contour: the prepare hitch, no node coverage, the
  webfont race, 16 simultaneous rank-collapses unmeasured; re-write: the '20 20 20' stub (closed by sweep), no direction of
  its own, churn on unchanged strings, tspan-bearing labels skipped). Remaining (s5): `keyed: "data"` (`E:9712-9751`) is the
  nearest existing shape to a whole-chart morph and T2 starts from it. Parent spot-checked `E:9761`, `E:9584`, `E:9795`,
  `E:9880`, `E:9851`, `C:280`, `C:281`, `C:2137` with grep against the post-C2 engine: all resolve (one cite off by one line).

### T2: THE WHOLE-CHART MORPH - line -> bars and bars -> line, every series, datum, axis and label
- Status: complete (2026-09-15) - HG1 open on the queue as `r26-70-compare-morph` (watch, two clips)
- Owner: `implementation_luna` (**ENGINE LOCK #1**)
- Depends on: T1
- Write set: `content/video_engine/scripts/kinetics/morph_a.mjs`, `content/video_engine/scripts/kinetics/chartxf.mjs`,
  `content/video_engine/scripts/kinetics/contour.mjs` (additive exports only), `content/video_engine/scripts/build_scene_timeline_f.py`
  (the verb + its refusals), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the chart-to region ONLY,
  via `sync_kinetics.py --write`), `content/video_engine/tests/kinetics/*.test.mjs`,
  `content/video_engine/tests/test_whole_chart_morph.py` (NEW), `content/video_engine/tests/golden/` (the new goldens +
  their sources), `content/video_engine/effects/cards/chart_to.json`
- **THE BAR, from the operator (E99 s34, `OPERATOR-RULINGS.md:3143`), verbatim:** *"I don't think I'm picky. to me, i
  care that the morph reads as a transformation, not a cut, and that it reads as intentional. The entire chart should
  transform, but I don't much mind if the text is re-written or directly morphed - both is a transformation."* Apply
  (the ruling's own words): the bar is **two readings, not a mechanism** - a viewer sees ONE thing becoming the next
  (no cut, nothing left behind, nothing appearing from nowhere) and sees it as MEANT (the motion has a direction and a
  rhythm, not a dissolve); every series, datum and axis transforms; the labels and titles **may morph glyph by glyph
  or be rewritten, and the choice is made by what reads, measured in T1**.
- Acceptance: a `chart_to` row makes a FULL chart become a FULL chart on one clock and clears the bar above - no cut
  anywhere in the window, nothing left behind, nothing arriving from nowhere, and the motion carrying a direction and
  a rhythm rather than a dissolve. The series' geometry morphs (`morph_a` under the existing pairing rule), the datum
  marks travel to their counterparts, the axes' rules morph or hand over on the same clock. **The tick LABELS, series
  names and title take whichever of the two routes T1 measured as the one that READS** - morph by `contour.mjs` glyph
  by glyph, or re-written at the datum by `figure.mjs`'s `figureGlyph` (E76 s4's route); E99 s34 permits either and
  both, and the slice records which it took and why in Evidence. A crossfade is still refused, and no frame draws both
  charts flat. Two pairs
  ship: `line -> bars` and `bars -> line`. The compiler REFUSES by name any pair it cannot key and points at the verb
  that can. A probe asserts the invariant a jump cannot satisfy: at u = 0.5 neither the source nor the target chart is
  drawable as itself (the `@proof-050` pattern of P57 T12c). Pure function of t (u=0 exact source, u=1 exact target,
  identical on two calls). Every pre-existing golden byte-identical. **The slice is not done until the queue proof is
  on disk**: the parent rewrites the card `r26-70-compare-morph` to HG1's question (the two clips, the one plain
  sentence, no options) and the clip renders through `review_queue_proofs.py --clips --only r26-70-compare-morph`.
- Recall (`docs/runbooks/RECALL-RECEIPT.md`): `docs_find "morph_to"` -> *"[capabilities] CAPABILITIES.md:116 -
  morph_to: the area under the line becomes another line's area by ARAP, mid-page... - LIVE - chart_to {at, dur,
  to: 'morph', state} between two LINE pages (MOR..."*; `docs_find "recast"` -> *"[capabilities] CAPABILITIES.md:27 -
  A CHART BECOMES ANOTHER CHART BY RE-WRITING (E64): the data-keyed recast and th... - WIRED"* and *"[effects]
  recipe:chart-recast-into-the-other-form - The argument keeps the data and changes its form"*; `docs_find "chart_to"`
  -> nine capability rows (`:27 :28 :104 :113 :114 :115 :116 :117 :270`), so a SEVENTH verb must justify itself
  against six that exist. Nothing in any layer claims a WHOLE-chart morph - that is the gap.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then
  `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_whole_chart_morph.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_sync.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`
  (unchanged reading) then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-70-compare-morph`
  - each run UNPIPED (a gated step never goes into `tail`)
- Evidence: report `scratchpad/assembly/P61-T2.md` (287 lines; the parent read it, the module + compiler + card diffs, and all
  six pinned frames as a viewer). THE VERB: `chart_to {to: "remake", state: k}` - the seventh, admitted on a line <-> bars pair
  only (`REMAKE_PAIRS`, `REMAKE_KEYS` level | change; `remake_mark_map` `build_scene_timeline_f.py:2113`; refusals by name
  `:2199-2234`, incl. dense-line -> dense-line -> use rescale/extend/morph, a retitle on the same row, a bar merely close to a
  datum - E77). ONE pairing law: every keyed datum's share of the source's ink (its column of the area, or its bar) described
  as one ring column by column (`chartxf.mjs` `xfSpanTop`/`xfStripRing`/`xfBarRing`, `REMAKE` COLS 8 LEAVE 0.28 DRAW 0.62
  TRAVEL 0.9, `xfRemakeClock`, `REMAKE_BEAT`), so `morphAPrepare(resample:false, normalise:false)` returns offset 0 - the
  node test asserts it; the ring drawn as a polyline (`xfRingPath`) so a landed bar hands over to the page's own <rect>. Datum
  marks travel on `lpDataDots` (the one travelling-data path, generalised); the axes hand over on the WHOLE clock through
  `lpAxisHandOver` - never the whole-svg crossfade; a browser test asserts both layers at opacity 1 at u 0.25/0.5/0.75.
  TEXT: the RE-WRITE route (T1 route b) - 0.012 ms/frame vs 6.56 + a 121.5 ms prepare; already the engine's hand
  (`lpWriteText` through `sweep`); its open failure mode closed: a label whose string AND place do not change is held whole
  (`lpRemakeHold`, `sweep`'s `held`). The TITLE transforms (gap 6: erased and the target's written from a title ink built at
  first need, `lpStateTitle`). `st.xfNow.remake` + `st.active` resolve to the target once the marks land (gap 8). Engine:
  `lpPaintRemake` :9999, `lpRemakeFor` :9964, `xfNow.remake` :10120. FRAMES (parent's read): u 0.25 the history gone, the tail
  standing, y labels mid-un-write, the title being re-written; u 0.50 five shapes that are NEITHER chart (the line's wedges
  on top, the bars' baseline below, the data riding) - the frame no cut can produce; u 0.75 almost bars with the new labels
  arriving; the mirror reads the same the other way. The lane's own first read changed the choreography (the whole line had
  un-drawn at u 0.25 - a disappearance then an appearance) to lpPaintRecastData's law: history leaves by the dash window,
  the tail stands until its ink drops into the columns; it also caught and fixed a lingering dot cap (E50). Goldens:
  `remake-line-to-bars`, `remake-bars-to-line` + @proof-025/@proof-075 each (six new, every pre-existing golden byte-identical).
  Validate: node 561/561 EXIT 0 (the plan's `node --test <dir>` form fails on node 24 - CJS directory resolution, identical on
  a pristine HEAD; the `*.test.mjs` glob form is the one that runs - T11 corrects the runbook line); sync in sync; pytest 145
  passed (test_whole_chart_morph 17 + the register); effects_catalog_check 0 failures; gate_motion_density on the approved Japan
  cut UNCHANGED (3 FAIL / 16 PASS, identical from a pristine HEAD copy - it reads the build's frozen player.html); registry in
  sync 930 records 0 orphaned; page-boxes re-pinned sha-only (44 passed). DEVIATIONS ratified: `render_baseline.py` PROOF_FRAMES
  gained the four proof instants (outside the literal write set; it is where every other lane's @proof-* instants live).
  RECORDED, not fixed: a 6 px corner detail at the two hand-over instants (rx 6 rect vs polyline ring; below the reading's
  threshold); a WARM player's pixels are not byte-stable on any surface (13 bytes across three captures of the shipped
  data-to-bars; pre-existing - T11 writes the backlog row); the un-keyed history WIPES by the dash window with 15 data -> 5
  bars (named in HG1's recommendation for the operator to read); compare beside a remake untested and unrefused. HG1's card
  rewritten by the parent with the two clip records; `r26-117-ball-into-the-next-chart` created (owed) as T3's prerequisite.
- CAPABILITIES rows changed: **:116** (`morph_to`) gains the whole-chart form; **:27** (the recast/E64 row) gains the
  pointer; a NEW row for the verb. **What this closes, precisely:** `P47:173` (T6) and `P47:183` (T7) are both marked
  `Status: blocked on P48` on the operator's sentence *"we still don't redraw/rebuild a new chart"*, and both say the
  slice closes "when a Tokyo page becomes the next chart on the page". T2 removes that BLOCKER - the mechanism exists
  and is proven in a PRIVATE Tokyo test-bed build directory, the approved cut untouched (E45; Tokyo is the test bed,
  no render). **T2 does not close T6 or T7.** P47 T7 is the THIRD WATCH (`P47:182-183`) - an operator watch that is
  not scheduled by this plan and cannot be, because Tokyo is under the operator's standing *"DO NOT ASK FOR A RENDER"*
  (`docs/agent-memory/operator/tokyo-short-render.md:79-93`). The watch stays P47's to schedule; T11 records only that
  the blocker is gone.

### T2b: BARS -> LINE COLLAPSES TO THE APEX AND DRAWS BACK TO THE ROOT (E99 s39)
- Status: complete (2026-09-15); HG1b RULED 2026-09-16 (E99 s50): approved
- Owner: `implementation_luna` (**ENGINE LOCK**)
- Depends on: T2, HG1 (ruled E99 s39)
- Write set: `content/video_engine/scripts/kinetics/chartxf.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the
  chart-to region via `sync_kinetics.py --write`), `content/video_engine/scripts/build_scene_timeline_f.py` (only if the pair's grammar
  needs a word), `content/video_engine/tests/kinetics/*.test.mjs`, `content/video_engine/tests/test_whole_chart_morph.py`,
  `content/video_engine/tests/golden/` (`remake-bars-to-line*` re-baselined + sources), `content/video_engine/effects/cards/chart_to.json`
- Acceptance: E99 s39 verbatim - *"for bars-> line I'd like to see it all collapse to the single apex point and then draw the line back
  to the root instead of sliding and snapping together and the whole line is formed -- if the whole thing is magically formed that is
  basically a snap/cut"*. Every bar's ink collapses into ONE point at the apex datum (the highest bar's top); the line is then DRAWN from
  the apex back to the root (the first datum) by the page's own stroke; the axes hand over on the same clock; at u 0.5 the frame shows
  the point and a partial stroke, never a whole line arriving (a browser probe asserts the drawn length is strictly between 0 and 1 at
  u 0.5). line -> bars is untouched and its goldens byte-identical. The card `r26-70-compare-morph` reopens with the new clip only.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_whole_chart_morph.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-70-compare-morph`
- Evidence: report `scratchpad/assembly/P61-T2b.md`. THE COLLAPSE cannot ride morph_a (a correspondence needs two rings; the
  destination is one POINT), so `kinetics/chartxf.mjs` gains a dedicated clock: `REMAKE_LINE` (GATHER 0.24 / SETTLE 0.32 / SPREAD
  0.25 / HOLD 0.86), `xfRemakeLineClock`, `xfGatherK` (rank 0 = the ring FARTHEST from the apex starts first and every ring lands
  together - the collapse ends as one point, never a queue), `xfRingTo` (every vertex of a ring to one point), `xfDrawWindow` (the
  stroke's visible interval growing out of the apex toward the root). `xfBarRing` still says WHAT collapses. Dead code removed
  with it (`REMAKE.DRAW`, the `toLine` branch); `xfRemakeClock` numerically identical on line -> bars. THE ENGINE: `lpPaintRemake`
  is the line -> bars painter only (its three goldens byte-identical); `lpRemakeApex` (the smallest tip y, sign carried),
  `lpRemakeDrawBack` - THE PAGE'S OWN STROKE: the same dasharray/dashoffset pair `lpPaintChart` draws every ledger line with, a
  NEGATIVE offset starting the window at the apex, the pen `strokeFrac ?? minJerk` (never constant velocity), the nib on the
  root-side end, `lpRestoreState` putting the page's dasharray back; `lpPaintRemakeToLine` - gather / settle / draw back, the axes
  on `lpAxisHandOver` over the whole clock, the bars page's numbers and categories un-written over SETTLE (gone as their ink
  reaches the point). GOLDENS: `remake-bars-to-line` base MOVED from u 0.50 to u 0.15 (12.36 s, mid-gather: five rings in flight)
  so the new `@proof-050` (13.2 s) is not the same instant twice - ratified by the parent; `@proof-025` (the point alone with its
  figure), `@proof-050` (the point + a partial stroke, the nib on the root side), `@proof-075` (most of the line, the labels
  un-writing). Parent's read: the collapse converges, the point stands, the stroke grows out of it - a point and a partial stroke
  at u 0.5, the frame a snap cannot produce. Card `chart_to:remake` phases 4 -> 7; page-boxes re-pinned sha-only. Tests: chartxf
  +5 node tests (the clock's ends, farthest-first / land-together, the k=1 point, root-first growth, the ruling's instant) and
  the browser probe in test_whole_chart_morph (drawn length at u 0.5 strictly inside (0.05, 0.95); no frame draws both charts
  flat). Validate: node 577/577 EXIT 0; sync_kinetics in sync; pytest test_whole_chart_morph + test_golden_frames 141 passed; effects_catalog_check 0 failures; page-boxes re-pinned sha-only (44 passed); registry 966 records, 0 orphaned. Deviation: the lane patched main-checkout files by an exact-string patcher (Edit refuses
  main paths from a worktree session) - verified by node --check, the node tests and the goldens; ratified.

### T3: THE BALL BECOMES THE NEXT FULL CHART - R26-117's third ending, and P48 T5b's planted source
- Status: complete (2026-09-16) - HG2 open as `r26-117-ball-into-the-next-chart` and HG2b as `p48-hg3-morph-onto-planted` (watch); proof B on `r26-76-melt-endings-in-motion` (HG6)
- Owner: `implementation_luna` (**ENGINE LOCK #2**)
- Depends on: T2, HG1 (ruled E99 s39 on line -> bars: T3 is UNBLOCKED)
- Write set: `content/video_engine/scripts/species/melt.mjs`, `content/video_engine/scripts/build_scene_timeline_f.py`
  (the `melt:morph` ending + `world.morph` planted source), `docs/content-video-engine/samples/scene-evidence-engine.mjs`
  (the melt + page-enter regions), `content/video_engine/tests/test_melt_morph.py` (NEW),
  `content/video_engine/tests/golden/` (the hand-over goldens + sources),
  `content/video_engine/effects/cards/exit.json` + `page_enter.json`
- Acceptance: `exit: melt:morph` hands the ball's ONE ring to the next page's `page_enter:morph` as its prop outline on
  ONE clock with no cut between (R26-117 names exactly this: *"the ball is the prop it starts from"*), and the page it
  opens into is a FULL chart built to T2's standard (E99 s1). A golden sits AT the hand-over frame. Separately, the
  planted-element source lands: `world.morph = {poly: [...]}` traced from a planted element's silhouette
  (`P48:451`, R26-16's tie) with its own golden - that is P48 T5b, and its card `p48-hg3-morph-onto-planted` (which
  already exists on the queue, today carrying "Missing proof: P48 T5b ... is unbuilt, so there is nothing to watch")
  gets a clip for the first time. The three-ending grammar stays `then: morph | splash | throw`; a bare ending is
  refused.
- **Card prerequisite (parent, at dispatch):** `r26-117-ball-into-the-next-chart` DOES NOT EXIST on the queue today -
  R26-117 lives only as the "not built" line inside `r26-70-compare-morph`'s `where` array
  (`docs/content-video-engine/review-queue.v1.json`, item `r26-70-compare-morph`, the entry
  `{"label": "R26-117 the page-level ball-to-chart morph (not built)", "missing": true}`). Queue writes are the
  parent's (T11's write set), so the PARENT creates the card in `review-queue.v1.json` and regenerates
  `REVIEW-QUEUE.md` **at T3's dispatch, before the slice runs**, so that T3's `--only r26-117-ball-into-the-next-chart`
  resolves. The delegated agent never edits the queue.
- Recall (`docs/runbooks/RECALL-RECEIPT.md`): `docs_find "morph"` -> *"[effects] The morph page enter -
  page_enter:morph - The page's prop outline (tab, plate or card) deforms by ARAP into the chart's sh..."* - the
  hand-over target already exists as a page enter; BACKLOG `:549` (R26-117) says it in the same words: *"page_enter:morph
  already deforms a prop outline into the chart's shape, so the ball is the prop it starts from"*. `docs_find "melt"`
  -> *"[effects] content/video_engine/scripts/species/melt.mjs - The melt scene exit - exit:melt - Only the outgoing
  chart's ink sags, fuses and compiles on 2s into a dense heavy ball wh..."* - the ball exists; only the third ending
  does not.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_melt_morph.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-117-ball-into-the-next-chart` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only p48-hg3-morph-onto-planted`
- Evidence: report `scratchpad/assembly/P61-T3.md`. ONE DOOR, TWO SOURCES: `world.morph` takes either the HANDED ball's ring or a
  PLANTED `poly`. `arap.mjs` `polyStrip` re-expresses any closed outline as the strip `stripMesh` carries (STRIP.EPS_X 0.004 /
  MIN_H 0.02; minDet 1.000 -> 0.261 across t, det J > 0 throughout). `melt.mjs` the fourth ending: `meltHandAt` / `meltHandDelay` /
  `meltHandSecs` / `meltHandRing` - delay + secs == the melt's window, so the melt's last frame IS the morph's first; the ball does
  not vanish - `meltState`'s morph branch gives its body the outline the page carries this frame (`lpMorphInWorld` -> `ctx.hand`)
  and its paint gives way to the page's ink over `M_FADE` 0.85. FOUND ON THE FRAME, NOT THE DIFF: the first hand-over frame cut
  the GROUND (the outgoing page is punched, a morph page's board was not) - `handed -> pk = 1`. `contour.mjs` gains
  `contourSilhouette` / `contourLuma` (the planted form traced off its own raster; a test re-traces and refuses a drift).
  REFUSALS by name: a poly with < 3 points / self-crossing / off-stage; melt:morph on a non-page, a second enter, a page with
  no area under a line, a page naming its own prop ('the BALL is the prop'). GOLDENS: `melt-morph` (the hand-over 16.60) +
  @proof-ball 16.50 / @proof-050 17.25 / @proof-built 18.30; `morph-planted` (15.02) + @proof-050 (16.00); T6 PROOF B composes by
  construction (a phase token and an ending in different branches of the same parsers; the window makes room, S + G_S + M_S =
  3.8 s) - `melt-gather-morph` + @proof-point / @proof-chart, pinned by a test. Parent's read of the frames: the ball alone; the
  hand-over frame indistinguishable from the one before it; the mid-frame one lens with the page's outline rising round it - the
  frame no cut can produce; the chart made on the shape (the morph's fill still standing at the built instant, leaving as the
  lines draw - named on the card); the planted form standing where the plate's form stood and stretching toward the area.
  Tests: test_melt_morph.py (46), morphsrc.test.mjs (20), melt.test.mjs (MELT_ENDINGS is four). Validate: node 597/597; sync in
  sync; pytest 214 passed; page-boxes sha-only (44); registry 974, 0 orphaned; effects_catalog_check EXIT 1 ONLY on
  `plate_option:use` (the voice lane's deleted test - pre-existing, not this slice's); gate on the Japan cut unchanged (4 FAIL /
  16 PASS since M44). DEVIATIONS ratified: `test_transitions_e47.py` (MELT_ENDINGS tuple of four), `test_golden_frames.py`
  SURFACES (+2 base goldens), the EFFECTS-CATALOG regenerated. NAMED for the backlog (T11): the field/punch beats under an
  ordinary morph page; two pages with different series colours untested; `buildMorph` targets series 0 only with no refusal;
  `polyStrip` is x-monotone (a C-shaped silhouette loses its bay, nothing refuses one). Closes P48 T5b; HG2 / HG2b / HG6 on the queue.
- CAPABILITIES rows changed: **:37** (the melt exit) gains the third ending; **:118** / **:116** gain the planted
  source. Closes **P48 T5b** and its card; `P48:185` (HG3) can then be answered

### T3b: THE MORPH PAGE'S GROUND ARRIVES, NEVER SNAPS IN AROUND THE PROP (E99 s52)
- Status: pending
- Owner: `implementation_luna` (**ENGINE LOCK**)
- Depends on: T3, HG2b (ruled E99 s52); T4b's field entries
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the morph page's field / punch beats under a morph enter), `content/video_engine/scripts/species/melt.mjs`
  (the handed page), `content/video_engine/scripts/build_scene_timeline_f.py` (the morph page's `;field=` word), `content/video_engine/tests/test_melt_morph.py`,
  `content/video_engine/tests/golden/` (`morph-planted*` + `melt-morph*` re-baselined, a new `@proof-ground` each), `content/video_engine/scripts/render_baseline.py`
- Acceptance: E99 s52 verbatim - *"going from the ink splotch to the full fill on the board instantly around it is the problem"*. A morph page's charcoal
  field arrives by the field entry its row names (s35; the soak spreading out from the splotch is the default for a planted page), on its own clock under
  the morph; a browser probe asserts that no two consecutive frames after the cut differ in the board's filled area by more than a named share; the handed
  ball's page reads against the same rule; the morph itself untouched (the mid-frames byte-identical where the field is not painted).
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_melt_morph.py content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only p48-hg3-morph-onto-planted`
- Evidence: pending

### T3c: THE CHART-TO-BALL IS A VISIBLE FUSION, NOT A SNAP (E99 s53)
- Status: pending
- Owner: `implementation_luna` (**ENGINE LOCK**)
- Depends on: T3, HG2 (ruled E99 s53)
- Write set: `content/video_engine/scripts/species/melt.mjs` (the compile phase's clock and shares), `content/video_engine/scripts/kinetics/morph_a.mjs` (additive),
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the melt region), `content/video_engine/tests/kinetics/melt.test.mjs`, `content/video_engine/tests/test_melt_morph.py`,
  `content/video_engine/tests/golden/` (every melt golden that carries the compile, re-baselined and named), `content/video_engine/scripts/render_baseline.py`
- Acceptance: E99 s53 verbatim - *"a rushed snap at the end transforming the chart to a ball"*. The compile (the sagged ink fusing into the ball) takes a
  longer, eased share of the melt's window on 2s: the last drips arrive INTO the ball, the circle is the end of a visible closing; a test measures the
  outline's area and perimeter frame to frame across the compile and refuses a jump above a named threshold; a golden at the fusion's midpoint. The default
  melt's total length unchanged unless the slice argues otherwise in Evidence (E45: the approved cuts render through their frozen players either way).
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_melt_morph.py content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-117-ball-into-the-next-chart`
- Evidence: pending

### T4a: THE EXTRUDED BAR'S LEAVE BREAKS ITS SHAPES DOWN MORE
- Status: complete (2026-09-15) - HG3 open on the queue as `p58-hg3-extruded-bar-leave` (watch, two clips)
- Owner: `junior_developer` (**ENGINE LOCK #3**; small)
- Depends on: none (may take the lock between T2 and T3 if the schedule wants it)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`buildLedgerBars` / the `EXTRUDE` leave
  path ONLY), `content/video_engine/tests/test_chart_forms_2_5d.py`, `content/video_engine/tests/golden/`
  (`form-extruded-bar@proof-leave` re-baselined + its source)
- Acceptance: the prism's leave decomposes the way the tilted line's does (E99 s4: *"would like to see the shapes break
  down more in form-extruded-bar@proof-leave to look more similar to form-tilted-line@proof-leave"*) - each prism's
  faces separate and go their own way rather than the block fading as one. Only `form-extruded-bar*` goldens change;
  every other golden byte-identical. The flat page's rows are untouched (M25/M28 read identical flat vs formed, the
  invariant CAPABILITIES:147 already carries).
- Validate: `python -m pytest content/video_engine/tests/test_chart_forms_2_5d.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only p58-hg3-extruded-bar-leave`
- Evidence: report `scratchpad/assembly/P61-T4.md` (T4a sections). Parent read the committed golden against the re-baselined one:
  before, four prisms carried off as rigid bodies with their dark sides welded on; after, the sides and caps tumble away from
  their bars while the coloured face rides alone - the tilted line's kind of break-down. The change: `extrudeFaces` records each
  face's own centre (engine :6646, :6656-6658); `shed(u, P)` re-drives every face through the vortex's own map at its own clock
  (`SHED` LEAD [0.12, 0.30, 0.52], SPIN [-150, 220, 340], DRIFT [2.4, 3.2, 4.4], :6661-6696); `lpShedPrisms` :6705-6712, called
  after `lpSpiral` (:10450) so the drain's lazy home measurement sees the faces at home on any seek order - two seeks to 28.5 s
  with a seek away between return byte-identical transforms. Only `form-extruded-bar@proof-leave` changed; `form-extruded-bar`,
  `@proof-build`, `form-tilted-line@proof-leave`, `thread-baseline` measured SAME before re-baselining; the flat path untouched.
  Tests: a served-player harness + 2 (`test_chart_forms_2_5d.py:246-285`) - the acceptance measured (no two faces of one prism
  share a transform at the leave instant; nothing written at 6.0 s). Validate: 127 passed; sync in sync; page-boxes 44; registry in
  sync. The card's two clip records written by the parent.
- CAPABILITIES row changed: **:147** (Two chart forms in 2.5D - the "owed" note on the leave is retired)

### T4b: A FORMED PAGE TAKES THE SOAK OR THE CROSS-FADE BY ITS JOB, AND LEAVES BY THE SOAK (E99 s35)
- Status: complete (2026-09-15) - HG4 open on the queue as `p58-hg3-forms-mount-not-scribble` (watch, three clips)
- Owner: `junior_developer` (**ENGINE LOCK #4**; small)
- Depends on: T4a (same files)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the ledger page's field enter + leave regions ONLY),
  `content/video_engine/scripts/build_scene_timeline_f.py` (the page's field option + its refusal), `content/video_engine/scripts/ledger_page.py`
  (only if a spec field is needed), `content/video_engine/tests/test_chart_forms_2_5d.py`, `content/video_engine/tests/golden/`
  (the two form goldens re-authored + a leave golden, with sources), `content/video_engine/effects/cards/page_enter.json` / `page_exit.json`
  (the two entries as first-class cards)
- Acceptance: E99 s35 verbatim - *"I think they should both be first class effects. When we are trying to maintain continuity, connecting
  ideas, speaking across plates i think the cross-fade is the answer, when we are building an idea or introducing a new idea or looking
  to fill space to separate ideas, the soak is the transition."* and *"the leave-soak is much better than the two plate leave"*. Three
  things: (1) BOTH field entries are first-class and authored by the sentence's job - the two-plate cross-fade (`page.plate` +
  `page.field_plate` + `page.board`, the generated plates) for continuity, the soak (`page.field = "soak"`) for a new idea or a
  separator; a formed page takes whichever its row names, never the scribble by default. (2) THE LEAVE IS THE SOAK'S RECEDE FOR BOTH:
  a page that arrived by the cross-fade leaves by the soak recede (today its inked plate fades out to the cream plate - retired as a
  leave). (3) The scribble (`page.field = "scribble"`) stays an opt-in back-up, untouched, never a default; NO work on its leave.
  Goldens: `form-tilted-line` re-authored on the two-plate cross-fade (its plates as URIs in the source, the way other goldens carry
  `DOCK_PLATE`), `form-extruded-bar` re-authored on the soak, and one leave golden of the cross-fade page leaving by the soak recede; the
  non-formed ledger page's goldens byte-identical (`ledger-soak-page`, `ledger-page-mid-build` - the latter is authored on the scribble
  and stays so as the back-up's own pin). The parent's three rendered clips of 2026-09-15 (scribble / soak / two-plate enter and leave
  on the formed page, scratchpad `assembly/t4b/`) are the reference the operator judged; the slice's clips match them.
- Validate: `python -m pytest content/video_engine/tests/test_chart_forms_2_5d.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only p58-hg3-forms-mount-not-scribble`
- Evidence: report `scratchpad/assembly/P61-T4.md` (T4b sections; the lane read the parent's three reference clips first). (1) THE
  LEAVE: `lpPlateRecede` (engine :6705-6728, called :10472 BEFORE `lpSpiral` because the drain measures the field's box on its
  first on-frame) - a two-plate page's seeps and crisp rect are already built and merely hidden while the plate carries the ground,
  so the leave lets them stand on the drain's own clock, fades the plate + rect on RECT_FADE and the seeps ride the vortex as a
  soak page's; a page with no field_plate takes none of it (`ledger-soak-page`, `ledger-page-mid-build` byte-identical). (2) THE
  GRAMMAR: `;field=soak|plates|scribble` (`PLATE_OPTS` :93, `_check_opt` :2468-2470, `PAGE_FIELDS` / `PAGE_FIELD_PLATES` /
  `page_field_spec` :2929-2963, applied only when named :3235-3243); `plates` refused by name when the page has no plate /
  field_plate, printing the two ids; `ledger_page.py` untouched. (3) THE CARDS: `plate_option:field` (the ruling verbatim as
  `when`), `page_enter:field_soak` + `page_enter:field_plates` (first-class, implicit - the row asks with `;field=`),
  `page_exit:retract` (the ground recedes with the marks whichever field it arrived on); effects_catalog_check was red first and
  named every drift, all fixed at the source. (4) THE GOLDENS: `form-extruded-bar` re-authored on the soak, `form-tilted-line` on
  the cross-fade (the two plates read from the quarantine objects at fixture-build time, paths + sha256 recorded, nothing copied
  into a tracked path), new `form-tilted-line@proof-recede` (29.6 s) in PROOF_FRAMES; six frames moved, every other golden
  byte-identical. Parent's read: the tilted line's base frame is the chart on the inked plate; @proof-recede is one lumpy ink
  island with the plate's own cream paper eaten in - the soak clip's event; the extruded bar builds on the seeped charcoal.
  (5) TESTS: 9 new (26 total; `test_chart_forms_2_5d.py:307-382`), incl. the measured acceptance in a browser (held: field hidden,
  plate opaque, no seep transformed; at the recede: field standing, plate < 0.01, every seep on the vortex; seek back = held).
  Validate: 135 passed; sync in sync; effects_catalog_check 0 failures; page-boxes re-pinned sha-only (44 passed); registry in
  sync 930 / 0 orphaned. DECISIONS by the parent: the tilted line's `uris.json` grows to ~390 KB of base64 plate - within the
  golden sources' precedent (camera-layers / dock-depth / page-depth carry 310 KB of the dock plate each, 57 uris files tracked);
  accepted. `render_baseline.py` PROOF_FRAMES entry ratified (where every @proof-* instant lives). Left to T11: CAPABILITIES
  :147 / :56 and doc 41 s2 beat 3. The first T4b brief ("keep the scribbles") was withdrawn before any code on the operator's
  challenge; E99 s35 ruled on the three clips the parent rendered from one source (`scratchpad/assembly/t4b/render_variants.py`). (T4b's first brief - "mount the charcoal and leave the scribbles intact" - was withdrawn before any code on the
  operator's challenge of 2026-09-15; the parent rendered the three field entries as clips from the form-tilted-line source and the
  operator ruled E99 s35 on them)
- CAPABILITIES row changed: **:147** (the "owed" clause becomes: a formed page takes the soak or the cross-fade by its job and leaves by
  the soak, E99 s35); **:56** (the field's two first-class entries and the scribble as back-up); doc 41 s2 beat 3 (T11)

### T5: THE BALL'S SHADOWS - a dark Fresnel rim, a metallic band, one point of deep shadow depth
- Status: complete (2026-09-15) - HG5 open on the queue as `r26-118-metallic-ball` (look: the crop + two clips)
- Owner: `implementation_luna` (**ENGINE LOCK #5**)
- Depends on: none (independent of T2/T3's geometry; ordered after T4 per the operator)
- Write set: `content/video_engine/scripts/kinetics/drop.mjs`, `content/video_engine/scripts/species/melt.mjs` (the
  ball's paint / the MASS material), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the melt region),
  `content/video_engine/tests/kinetics/drop.test.mjs`, `content/video_engine/tests/test_ball_material.py` (NEW),
  `content/video_engine/tests/golden/` (the ball goldens + sources)
- Acceptance: E99 s3 verbatim - *"We definitely need more shadows. The shadows are where the weight/mass largely come
  from i think, dark fresnel rim + metallic band and I imagine incorporating at least one point of deep shadow depth."*
  The ball gains (a) more cast/contact shadow, (b) a DARK Fresnel rim (grazing-angle darkening, not a bright
  highlight ring), (c) a metallic band, (d) at least one point of deep shadow depth - each a named dial with a
  measured default, sourced to `docs/research/motion/LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md` §2.1 where the
  blueprint's finding is one the research gate marked usable (E99 s24: the excluded findings stay excluded). The new
  look ships behind the existing `melt:weight` opt-in until HG5, so no approved cut's frames move; every pre-existing
  golden byte-identical. A before/after crop at the same instant through `diff_box`.
- Recall (`docs/runbooks/RECALL-RECEIPT.md`): **`docs_find "Fresnel"` returns 3 hits and NOT ONE is a shading term** -
  *"[animation] content/video_engine/scripts/kinetics/clothoid.mjs:115 - fresnel - export const fresnel = (x) => {"*,
  `clothoid.mjs:147 fresnelMoments`, and `CAPABILITIES.md:96` (the CLOTHOID fitter, Euler spirals). That is the Fresnel
  INTEGRAL for curve fitting, a different thing from the Fresnel rim the operator asked for; **the slice must not reuse
  the name or the module**. The material the record does have: `docs_find "splat"` ->
  *"[manifest] docs/research/motion/LIVING_METALLIC_DROP_RESEARCH_BLUEPRINT.md - Research Blueprint - The Living
  Metallic Drop: Surface Modes, Damping, the High..."* and its `:148` *"2.1 Impact Phenomenology & Mode
  Decomposition"* - released by E99 s24, usable findings only.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_ball_material.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-118-metallic-ball`
- Evidence: report `scratchpad/assembly/P61-T5.md`. The ball today (lane's read, parent's agreed): a rubber bouncy ball - one
  white spot on an evenly lit saturated dome, the silhouette its BRIGHTEST region, no band, no deep shadow, a floating grey slit
  for a shadow. THE GATE READ FIRST: R26-119 (the living drop) is PLAUSIBLE overall, nothing CONFIRMED, the galinstan sigma
  and the ink row EXCLUDED (E99 s24 honoured). Twenty named dials: the material's profiles in `kinetics/drop.mjs:60-108`
  (RIM_AT 0.42 / RIM_GAMMA 1.15 / RIM_A 0.97; BAND_P 0.60 / BAND_H 0.055 / BAND_A 0.85; PIT_AT 0.44 / PIT_R 0.52 /
  PIT_GAMMA 1.4 / PIT_A 0.80 - every one DERIVED and says so; the licence for a rim and a band at all is s3.3's zero-diffuse
  metal, gate tier PLAUSIBLE) and the ball's paint in `species/melt.mjs:182-215` (the W_OCCL_* / W_RIM_* / W_BAND_* / W_PIT_*
  paint dials). The SIGN is the operator's and contradicts the finding, written down as such: the blueprint's grazing rim is
  bright, E99 s3 asks for a dark one, the ruling wins (RECALL-RECEIPT s3) and is right on our board (no bright environment
  to mirror); the profile is the physical 1 - cos(theta) geometry, only the sign inverted. `melt:weight` has NO kinetics
  key - the opt-in is a token in the authored exit string (compiler :1511), so the flag-off proof is the surface `melt-page`
  and its four goldens, byte-identical; the five opt-in goldens that MAY move (`melt-ball-roll` x3, `melt-depth` x2) did.
  Frames (parent's read of settle-before / settle-after / the land crop): a dark rim all round, a bright band across the lower
  half, a well opposite the highlight, a tight dark contact core - heavier, plainly; metallic-ish, not metal. Measured: the
  silhouette ring's luminance 120.7 -> 64.6 (from brighter than the body to 43% of it), the contact shadow 26.9 -> 10.5
  (57% -> 22% of the board), the body 141 -> 149. Tests: `test_ball_material.py` (15: dials + sources declared, flag-off
  strings byte-identical, rim monotone toward the silhouette, band + pit present, two seeks identical, the four flag-off
  goldens by sha256) + `drop.test.mjs`. Validate: node 566/566; sync in sync; 124 passed; effects_catalog_check 0
  failures; `build_effects_catalog.py --check` STALE by two derived dials_values fields (a generated layer outside the write
  set - the parent ran `--write`); page-boxes re-pinned sha-only (44); registry 955 records, 0 orphaned. A render flake on
  `page-depth@proof-leave` in one batch run, identical to its golden on three isolated re-renders. HONEST LIMIT for HG5,
  named in the card's recommendation: the body stays the chart's orange (the blueprint's near-black metal is a RULING - the
  ball stops carrying the chart's colour - not a dial; the shape of that dial, `W_BODY_SHADE`, is described), and the band is
  a straight stripe (a mesh could curve it). The card rewritten by the parent: the crop (diff_box [734, 714, 962, 963]) +
  the weight clip + the default melt clip.
- CAPABILITIES rows changed: **:37** (the melt exit's ball) and the `melt:weight` note on R26-118's row

### T5b: THE PRIOR BALL WITH THE DARKNESS KEPT, AND TWO BODY COLOURS FOR THE OPERATOR'S EYE (E99 s42)
- Status: complete (2026-09-15) - HG5b open on the queue as `r26-118-metallic-ball` (look: three crops + three clips)
- Owner: `implementation_luna` (**ENGINE LOCK**)
- Depends on: T5, HG5 (ruled E99 s42)
- Write set: `content/video_engine/scripts/kinetics/drop.mjs`, `content/video_engine/scripts/species/melt.mjs`,
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the melt region), `content/video_engine/tests/kinetics/drop.test.mjs`,
  `content/video_engine/tests/test_ball_material.py`, `content/video_engine/tests/golden/` (the ball goldens + sources)
- Acceptance: E99 s42 verbatim - *"the ball is too blurred so the prior work is actually better. this slice is pixelated on the edges
  now, the darkness feels right, but the blur is wrong, and i think the rim is wrong ... I would be interested in seeing it just melt to
  the slate gray or the reference color"*. FIRST the slice names, from the T5 diff, what blurred the ball and what pixelated its edge
  (evidence before any dial). THEN: the surface returns to the pre-`d719e21` look (the highlight, the clean silhouette; no blur, no
  pixelated edge - the pre-T5 goldens are the reference, read side by side), the darkness stays (the deeper contact core and shadow
  depth), the dark rim and the band are OFF by default; two further variants render the same instants with the body melting to the
  board's SLATE GREY and to the REFERENCE colour (`W_BODY_SHADE`), as an authored option. The card `r26-118-metallic-ball` reopens as a
  three-way crop + clips (prior / slate / reference). Every non-ball golden byte-identical; the default melt byte-identical.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_ball_material.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-118-metallic-ball`
- Evidence: report `scratchpad/assembly/P61-T5b.md`. THE FINDING FIRST (no filter blurred anything): the blur was `dropRimAlpha`'s
  ramp (`kinetics/drop.mjs:99-112`) - the board-to-body transition went from 1 px to 100+ px across the silhouette; the pixelation
  was four antialiased copies of one path (`species/melt.mjs:1357-1372`): an edge pixel at 0.567 coverage ended at 0.988
  (1 - (1 - 0.567)^4 = 0.965). THE FIX: `W_RIM_ON: false` / `W_BAND_ON: false` gates (every profile dial kept and tested); the
  darker contact core and the pit kept. Measured at the settle: silhouette luminance 120.6 (prior 120.7, T5 64.2); contact floor
  9.8 (T5's darkness kept); the prior-vs-restored diff bbox is only the pit and the core. THE VARIANTS: `melt:weight:...:body=
  slate|reference` (`build_scene_timeline_f.py:1640-1641`; `meltOpts` :313/329; `meltBodyInk` :997; `W_BODY_SHADE` :244, 1 for
  both) - slate `#25313C` (the template's page ink, `scene-evidence-player.template.html:50`), reference `#000000` (the living
  drop blueprint s3.3.1); an unknown body word refused by name. Goldens: `melt-ball-roll` x3 + `melt-depth@proof-ball` re-baselined
  (six moved incl. `melt-depth`, `melt-gather@proof-point`), NEW `melt-ball-slate` + `@proof-settle`, `melt-ball-reference` +
  `@proof-settle`. Parent's read of the four settle frames: the restored ball IS the prior ball (the highlight, the clean
  silhouette) with a deeper contact shadow and a dark pit on its lower right that reads as a smudge - named on the card; the slate
  ball sinks toward its own board; the reference ball is a black disc with a highlight and no form. Tests: test_ball_material
  (the flag-off goldens by sha256; rim/band off by default - the silhouette not darker than the body; no filter in the ball's
  markup; the two bodies measured at the settle; an unknown word refused; two seeks identical); drop.test.mjs. Validate: node
  577/577; sync in sync (41); pytest 176 passed; effects_catalog_check 0; page-boxes sha-only (44); registry 966, 0 orphaned.
  Known: `build_golden_sources.py` drifts on two unrelated surfaces (`tiers-two`, `treemap-cross`) when run - restored by the lane,
  a row for T11. Card: three crops (prior vs restored / slate / reference) + three clips 15.0-17.75 s; options argued by E99 s42.

### T5c: THE REFERENCE BLACK IS THE WEIGHT BALL'S DEFAULT BODY (E99 s49)
- Status: complete (2026-09-16) - the ruling's default in the engine; no card (HG5b ruled E99 s49)
- Owner: `junior_developer` (**ENGINE LOCK** - one default + the goldens)
- Depends on: T5b, HG5b (ruled E99 s49); after T3 (the same file)
- Write set: `content/video_engine/scripts/species/melt.mjs`, `content/video_engine/scripts/build_scene_timeline_f.py` (the default
  body word), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the melt region), `content/video_engine/tests/test_ball_material.py`,
  `content/video_engine/tests/golden/` (the weight-ball goldens re-baselined, listed by name), `content/video_engine/effects/cards/exit.json`
- Acceptance: E99 s49 - *"I like the reference"*: a `melt:weight` ball with no `body=` word renders the reference black (the
  blueprint's near-black metal, `W_BODY_SHADE` 1); `body=chart` keeps the restored orange; `body=slate` unchanged; the default melt
  (no weight token) byte-identical; the goldens that move are exactly the weight-ball ones, named; T3's hand-over ball inherits it.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_ball_material.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: report `scratchpad/assembly/P61-T5c.md`. The default in ONE place per side: `species/melt.mjs:428` `out.wbody = out.wbody
  || (out.weight ? "reference" : "chart")` and `build_scene_timeline_f.py:1762` `body or ("reference" if weight else "chart")`; a new
  test_ball_material test pins the two agree over twelve exit strings (`melt` -> chart, `melt:weight` -> reference, `melt:weight:metal`
  -> reference, `melt:weight:body=chart` -> chart, `melt:gather:weight:splash:plate` -> reference, `melt:morph` -> chart, `dip` -> chart).
  GOLDENS: 6 of 136 moved - `melt-ball-roll` x3, `melt-depth` x2, `melt-gather@proof-point` (shas in the report); `melt-morph` and
  `melt-gather-morph` carry NO weight token and do not move - the reference body reaches T3's hand-over ball only when a row authors
  `weight` (or `body=`); `melt-page`, the slate and the reference goldens unchanged. Parent's read: `melt-ball-roll@proof-settle` is the
  black ball with its specular spot and the contact shadow kept, and it is BYTE-IDENTICAL to `melt-ball-reference@proof-settle` (the
  lane measured it: one sha). Card `exit:melt` body option names the default. Page-boxes re-pinned sha-only. DEVIATIONS ratified by the
  parent: `test_transitions_e47.py:353-354` and `test_melt_morph.py:179` pinned the old default and were updated to the ruling's
  (each a one-line expectation). Validate: node 0; sync in sync; pytest ball_material + transitions_e47 + melt_morph + golden_frames 236 passed (exit 0); page-boxes 44 (sha-only); registry 0 orphaned; effects_catalog_check red only on the voice lane's `plate_option:use`.

### T6: THE MELT GATHERS TO ONE DENSE, HEAVY, VIBRATING POINT - and splashes into a full chart or a world plate
- Status: complete (proof A 2026-09-15, proof B 2026-09-16 via T3) - HG6 open on `r26-76-melt-endings-in-motion` (watch, both clips)
- Owner: `implementation_luna` (**ENGINE LOCK #6**)
- Depends on: **T5 only** (the point IS the ball; its material must land first). **T6 is NOT held behind T2/HG1.** The
  operator ranked the melt second, and putting it behind the whole-chart morph would park the second-ranked item
  behind the first gate. So the slice ships in two proofs on ONE card (`r26-76-melt-endings-in-motion`):
  **proof A (this slice, T5 only)** - the gather and the splash landing in a high-resolution WORLD PLATE, which E99 s2
  names first (*"a scenic, high-resolution world plate or fully assembled chart"*) and which needs no chart work at
  all; **proof B (added when T3 lands)** - the same gather splashing into a FULLY ASSEMBLED chart built to T2/T3's
  standard, appended to the same card before HG6 is asked. HG6 is asked once, with both proofs, unless the operator
  wants proof A alone sooner
- Write set: `content/video_engine/scripts/species/melt.mjs`, `content/video_engine/scripts/kinetics/drop.mjs`,
  `content/video_engine/scripts/build_scene_timeline_f.py` (the new gather form + the flag),
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the melt region), the ink-bloom module it composes,
  `content/video_engine/tests/test_melt_gather.py` (NEW), `content/video_engine/tests/kinetics/*.test.mjs`,
  `content/video_engine/tests/golden/` (the gather + splash goldens), `content/video_engine/effects/cards/exit.json`
- Acceptance: E99 s2 verbatim - *"i expect almost like our swirl effect, i don't want the melt to be blur or a wipe, it
  should be closer to the swirl except for instead of a whirlpool, vortexing around a single point, it collects and
  amasses into a single point, that single point should be dense, heavy, and vibrating with energy, and when it
  splashes, it should splash into a scenic, high-resolution world plate or fully assembled chart."* So: (a) the
  gather is the page VORTEX's motion (CAPABILITIES:57, doc 29 §9.31) aimed at ONE point rather than a whirlpool - a
  measurable convergence, no blur filter and no wipe anywhere in the window; (b) the point vibrates on a named idle
  (E49: nothing ever goes truly still) with an amplitude dial; (c) the splash lands in a **high-resolution world plate
  (proof A)** and, once T3 has landed, in a **fully assembled chart (proof B)**; the ink-splat -> ink-bloom route
  (`INTAKE-INK-BLOOM-2026-09-08.md:19`) is explicitly permitted by the ruling and is the first candidate because it
  composes a preset already on disk. A probe asserts no frame in the window is a blur or a wipe (the gather's pixels
  travel; they do not lose contrast in place).
- **THE FLAG, named.** The melt has no `kinetics.*` config flag - **its opt-ins are tokens in the authored exit
  string**, parsed once on the compiler side and mirrored once on the player side. The pattern to copy is `melt:weight`
  (R26-118 / E88 s6): `build_scene_timeline_f.py:105` lists `melt` in `TIMED_EXITS`, `:1511` holds `MELT_ENDINGS`
  (`"throw", "splash:chart", "splash:plate"`) and `MELT_MATERIALS`, and `:1536` documents the grammar -
  *"R26-118 / E88 s6 adds ``weight``, optionally followed by a MATERIAL ... It is opt-in ... A material this engine
  does not have is refused BY NAME, never painted as the default."* So this slice adds the token **`melt:gather`**
  (a phase token beside `weight`, composable with the endings), **read in exactly ONE place per side**:
  `parse_exit` in `build_scene_timeline_f.py` (the `MELT_ENDINGS` / grammar region at `:1511`-`:1540`) and `meltOpts`
  in `species/melt.mjs` - *"the two have to agree, and test_transitions_e47 pins the pair"* (`:1540`). An unknown token
  is refused BY NAME. **The default - an exit string with no `gather` token - renders today's melt byte-identical**,
  and that is a TEST, not a promise: `test_transitions_e47` gains a case asserting `parse_exit("melt")` and
  `parse_exit("melt:splash:chart")` are unchanged tuples, and every existing `melt*` golden
  (`melt-plate`, `melt-depth*`, the throw/chart/plate proofs) re-renders byte-identical under
  `test_golden_frames.py`. E45 and the approved Japan short are protected by that byte-identity, not by intent.
  **E99 s34 settles the rest** (`OPERATOR-RULINGS.md:3143`; the operator: *"Japan will be re-rendered eventually, but
  it's not a concern right now."* Apply: *"`melt:gather` (and every P61 flag) stays off on the approved Japan short;
  its re-render is a later item on the record, not a P61 acceptance."*). So: **`melt:gather` is never authored into
  the Japan short's rows inside this plan**, and no P61 slice re-renders it. The re-render is a NAMED FOLLOW-UP ROW the
  parent writes to `docs/content-video-engine/BACKLOG.md` at T11 - *"the approved Japan tariff short is re-rendered
  with the P61 mechanisms the operator approved (E99 s34: eventually, not now)"*, blocked on nothing, scheduled by the
  operator - and it is explicitly NOT an acceptance criterion of this plan.
- Recall (`docs/runbooks/RECALL-RECEIPT.md`): `docs_find "melt"` -> *"[capabilities] CAPABILITIES.md:37 - THE MELT
  EXIT, REWORKED TO E88: THE CHART MELTS, THE BOARD STAYS (P52 T9 -> BAC... - WIRED - exit:
  melt[:throw|:splash:chart|:splash:plate][:<s>][:<x>,<y>]"* and *"[effects] species/melt.mjs - The melt scene exit -
  exit:melt - Only the outgoing chart's ink sags, fuses and compiles on 2s into a dense heavy ball wh..."*;
  `docs_find "mount"` -> *"[capabilities] CAPABILITIES.md:57 - The page VORTEX - LIVE - how a ledger page leaves and
  how it returns"* (the swirl the operator compares the gather to, doc 29 §9.31 at `:2100`); `docs_find "splat"` ->
  *"[index] docs/content-video-engine/INTAKE-INK-BLOOM-2026-09-08.md:19 - What the preset is (the source, kept
  verbatim below) - A Canvas 2D bloom from the frame centre: a 40-segment blob whose radius carries two-harmonic
  n..."* - the accepted route is a preset already on disk, not a new one.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_melt_gather.py content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short`
  (M31's empty-stage reading must not worsen) then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-76-melt-endings-in-motion`
- Evidence: report `scratchpad/assembly/P61-T6.md` (14 sections). THE TOKEN `melt:gather` - read in exactly one place per side
  (`_melt_parts` / `melt_gather` / `MELT_G_S` in the compiler; `meltOpts` in `species/melt.mjs`), composable with weight / material /
  depth / length / every ending, an unknown token refused by name; `parse_exit("melt")` and `parse_exit("melt:splash:chart")`
  unchanged tuples (test_transitions_e47, 30 tests) and every pre-existing melt golden byte-identical (166 passed). THE GATHER: the
  page vortex's own map (doc 29 s9.31) aimed at the ball's centre - every mark and word travels there and amasses (`G_KEEP`); the
  point wears T5's material and vibrates on `drop.mjs`'s own FLOOR at `G_VIB` (no new motion law); the splash is the existing
  ink-splat -> bloom painting the committed Tokyo dock plate up through its stains. No blur, no mask, no wipe - measured: ink spread
  265.5 -> 59.9 px, pixel count 3725 -> 2305, peak contrast 575 -> 575. The FRAME caught what the diff could not: series paths
  turned rigidly as sticks; s9.31's own words ('redrawn point by point') were the fix - paths are sampled and curl. Parent's read of
  the four goldens: the series curl into one spiral converging on the point; the point is the ball with the last words streaming in;
  the splash paints the plate up from the left through a lumpy ink boundary; the plate lands whole - the ruling's words. Tests:
  test_melt_gather.py (23: the grammar both sides, the refusal, the default byte-identity, the convergence probe, the no-blur/no-wipe
  probe, the idle amplitude, two seeks identical, every gather dial pinned to LP_RETRACT's numbers and the pose to lpVortex's
  output), melt.test.mjs (+6). Validate: node 572/572; sync in sync; 166 passed; effects_catalog_check 0 + build_effects_catalog
  --check in sync (the card's generated layer written); registry 0 orphaned; page-boxes 44; M31 on the Japan cut unchanged (INFO).
  Goldens: `melt-gather` + @proof-point / @proof-splash / @proof-plate (PROOF_FRAMES). FOLLOW-UPS to the backlog at T11 (named,
  not done): (1) the vortex map is written twice (`meltGatherAt` carries lpVortex's five terms because sync_kinetics refuses an
  import from a later region) - pinned by tests, the real fix a shared `kinetics/vortex.mjs` with spiral's region moved, a slice
  of its own; (2) the axis hairlines (`<line>` children) still turn rigidly - converting them to sampled polylines finishes the
  swirl. Proof A on the card `r26-76-melt-endings-in-motion` (surface melt-gather 14.7-18.9 s); the card stays owed until proof B.
- CAPABILITIES row changed: **:37** (THE MELT EXIT) - the gather replaces the sag/ball description behind its flag

### T6b: THE SPLASH IS A THROW - the ball picked up, thrown forward, splatting where it lands (E99 s51)
- Status: pending
- Owner: `implementation_luna` (**ENGINE LOCK**)
- Depends on: T6, T5b, HG6 (ruled E99 s51)
- Write set: `content/video_engine/scripts/species/melt.mjs` (the splash endings), `content/video_engine/scripts/kinetics/stopaction.mjs` (additive: the pick-up),
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the melt region), `content/video_engine/tests/kinetics/*.test.mjs`, `content/video_engine/tests/test_melt_gather.py`,
  `content/video_engine/tests/golden/` (`melt-gather*`, `melt-splash`, `melt-plate` re-baselined + `@proof-pickup` / `@proof-flight` / `@proof-splat`), `content/video_engine/scripts/render_baseline.py`,
  `content/video_engine/effects/cards/exit.json`
- Acceptance: E99 s51 verbatim - *"the ball actually picked up and then thrown forward to splat on the canvas ... I want it to be thrown"*. For `splash:chart`
  and `splash:plate`: the ball is LIFTED (weight sold first, `landXf` run backwards - an anticipation, the shadow tightening under it), travels FORWARD in a
  ballistic arc (`throwXf` toward the canvas, the shadow lagging `LAG_FRAMES` behind), and SPLATS at the landing - the splat and the stains grow from the
  impact point; a test asserts the ball's centre rises before it advances, advances monotonically, and the first stain's centre is the landing point; the
  bounce-roll-burst reading is gone from the splash (the weight phase's roll stays for `throw`). Every non-splash golden byte-identical.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_melt_morph.py content/video_engine/tests/test_transitions_e47.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-76-melt-endings-in-motion`
- Evidence: pending

### T7: THE VERDICT STACK ON A SHORT - Steel and Paper's choreography, so the burst lands
- Status: complete (2026-09-15) - HG7 open on the queue as `r26-82-verdict-stack-choreography` (watch, two clips)
- Owner: `implementation_luna` (**ENGINE LOCK #7**)
- Depends on: none
- Write set: `content/video_engine/scripts/species/verdict.mjs`,
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the stack's mount + `drawStack` region),
  `content/video_engine/scripts/build_scene_timeline_f.py` (the short's stack options),
  `content/video_engine/tests/test_verdict_stack.py` (NEW/extended), `content/video_engine/tests/golden/` (one golden
  per phase), `content/video_engine/effects/cards/dock_payload.json`
- Acceptance: E99 s21 verbatim - *"We're missing some of the choreography, our cards in steel and paper felt much more
  alive, and also it didn't just place them horizontally, we had real choreography and movement, which then made the
  burst better as well, but this is the right direction."* The short's stack keeps ALL FIVE phases (memory
  `composite-effects-keep-every-phase`: enter one at a time from depth -> FOCUS large near centre while its phrase is
  spoken -> RECEDE to an asymmetric rail spot so the page re-composes as a MOSAIC -> railed cards IDLE -> radial BURST
  on the pivot line, 60 ms apart) - CAPABILITIES:184 and `drawStack` already carry them for 16:9; the short's version
  must not flatten any phase into a horizontal row. A golden at EACH of the five phases. The Steel and Paper reference
  (`build-f/evidence-dock.json` `ev-holds-stack-v1`, nine proofs 702.87-723.69 s, BACKLOG R26-82 `:488`) is rendered
  as a side-by-side reference clip for the card - read, never modified.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_verdict_stack.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-82-verdict-stack-choreography`
- Evidence: report `scratchpad/assembly/P61-T7.md`. The lane read the REFERENCE first - Steel and Paper's own beat rendered from its
  frozen build (read-only): every phase measured (enter translateZ -288.8 / rotateY -12.4 / opacity 0.59; focus 840x388 at
  scale 1.816; the mosaic four across the top at four widths; the burst's opacities 0.50-0.98 along their own bearings). Today's
  16:9 stack forced to 9:16: four cards in a horizontal row inside the platform's top chrome, both flank cards off the edges, the
  focus card 223 px past the right edge - the flattening E99 s21 names. BUILT: `VERDICT_9X16` (verdict.mjs) - the same dials with
  the geometry re-laid: nine rail spots inside G-l's safe box, the focus card 63.9% of the stage near the box's centre (the
  reference's ratio is 43.8% of a landscape stage), enter swing/rise sized for a 1080-wide stage, the burst radial from the
  MOSAIC's centre (a short's right 200 px are platform chrome); `verdictDials(portrait)` the one entry; `verdictPose` gains one
  branch - the railed share of the pose comes from `idleXf` on a NAMED kind (`live`, E49) phased per card; `VERDICT` untouched
  number for number and the 16:9 goldens byte-identical. The layout was rebuilt THREE times against measurements (coverage
  73% -> 51%; the fill order alternating band and side; the centre kept open after the focus card buried a whole card). The
  compiler's `stack_entry` derives the payload AND the host dock's window from ONE set of times (s9.24's 0.77 s dimming drift
  made mechanical) with six refusals by name. Goldens: `verdict-stack-9x16` (the mosaic, 13.6 s) + @proof-enter 2.25 / @proof-focus
  3.1 / @proof-idle 15.4 / @proof-burst 16.75 (PROOF_FRAMES). Parent's read of the five: one card from depth; the focus card
  alone and large; the mosaic asymmetric with the eighth card across the middle and none buried; the rails drifted on the idle;
  the burst throwing cards off along five bearings - every phase the operator named. Honest shortfall: the reference's wall is
  nine real documents of six shapes on a painted plate, ours nine synthetic cards on a flat plate. Tests: test_verdict_stack.py
  (12: stack_entry's refusals, the full-frame dials pinned by text, eight browser reads - one at a time from depth, focus >= 55%
  and >= 1.4x every rail, rails >= 25% of the height with no 60 px band holding half, every card inside the safe box at every
  0.25 s, every railed card moved 0.3-25 px, every card thrown AWAY from the centre, card i at t + i x 0.06 at the same share of
  its throw, two seeks one frame). Validate: node 572/572; sync in sync; 129 passed (117 goldens + 12); both catalogue checks
  green; page-boxes sha-only; registry regenerated. DEVIATIONS: `render_baseline.py` PROOF_FRAMES (four entries) and the
  generated EFFECTS-CATALOG ratified. The lane ran a tagged `git stash push` / `apply` / `drop` to prove a failure pre-existing -
  against the brief; the tree was verified intact and the other session's stash untouched; the finding was real:
  `test_every_wired_card_is_in_a_recipe` fails on T2's and T4b's four cards (no lane's validate line ran that test) - a
  recipes lane fixes it. Card: the short's clip 1.9-17.5 s and the reference via the build route 702.87-727.6 s (extended past
  the brief's 723.69 so the reference's own burst at 726.98 is on the card).
- CAPABILITIES row changed: **:184** (THE VERDICT STACK) gains the short's form with its five phases named

### T7b: THE VERDICT STACK'S RAILS IN READING ORDER (E99 s43)
- Status: complete (2026-09-16) - HG7b open on the queue as `r26-82-verdict-stack-choreography` (watch)
- Owner: `implementation_luna` (**ENGINE LOCK**)
- Depends on: T7, HG7 (ruled E99 s43)
- Write set: `content/video_engine/scripts/species/verdict.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the
  stack region), `content/video_engine/tests/test_verdict_stack.py`, `content/video_engine/tests/golden/` (`verdict-stack-9x16*`
  re-baselined + sources), `content/video_engine/effects/cards/dock_payload.json`
- Acceptance: E99 s43 verbatim - *"1-2 on top, left to right since thats how people read. then 3-4, on bottom, 5-6 on top, 7-8 on
  bottom etc."* `VERDICT_9X16`'s rail spots are re-laid in reading bands (cards 1-2 across the top left to right, 3-4 across the
  bottom left to right, 5-6 top, 7-8 bottom, the ninth by the same rule), the focus card large near the centre between the bands, the
  five phases and the burst unchanged; a test asserts the rail order (card k's spot is left of card k+1's within a band, and the band
  alternates top / bottom by pairs); the 16:9 `VERDICT` is read against the rule and reported, not changed. The card
  `r26-82-verdict-stack-choreography` reopens with the new clip.
- Validate: `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python -m pytest content/video_engine/tests/test_verdict_stack.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-82-verdict-stack-choreography`
- Evidence: report `scratchpad/assembly/P61-T7b.md`. `VERDICT_9X16` (`species/verdict.mjs:99-140`) re-laid in reading BANDS: TOP line 0
  cards 1, 2 / BOTTOM line 0 cards 3, 4 / TOP line 1 cards 5, 6, 9 / BOTTOM line 1 cards 7, 8 - each left to right; 5-6 take a second
  row because the portrait width is spent (348 + 340 of 776 px; four across would be 194 px cards, 18 %); 9 sits right of 6 because
  the band height is spent (y 286-614, lines at 286-476 and 452-605); the focus card unchanged, owning y 614-1010; every spot inside
  x 80-880, y 280-1340; the union 45 % of the stage; five column starts. Asymmetric in size and tilt, never in order (s43 amending
  s21). THE 16:9 `VERDICT` READ, not changed (`:39-42`): a strict raster - top line 1-4 left to right, middle 5-6, bottom 7-9 - so
  it already obeys the reading rule but fills the top line four-wide before going down (a 1920 px line has the width; a 1080 px one
  does not) - the pair alternation there is a card if the operator wants it. Parent's read of the mosaic and the idle: 1 red / 2
  blue top, 5 purple / 6 pink under them, the focus card centre, 3 green / 4 gold bottom, 7 blue / 8 orange under - the order the
  operator named. Tests: test_verdict_stack.py gains the rail-order assertions (left of the next within a band; the bands alternate
  top / bottom by pairs) beside the eight browser reads. Goldens: the five verdict-stack-9x16 frames re-baselined through
  `render_baseline.py --surface`, sources untouched; every other golden byte-identical. Validate: node 597/597; sync in sync; pytest
  147 passed; effects_catalog_check 0 failures (the voice lane restored its test); page-boxes 44; registry in sync. Card
  `dock_payload:stack` names the reading order.

### T8: THE BEAUTIFIED AGENDA PAGE - the plate version of the list effect
- Status: complete (2026-09-15) - HG8 open on the queue as `r26-80-agenda-page-owed` (watch)
- Owner: `implementation_luna` (**ENGINE LOCK #8**)
- Depends on: none
- Write set: `content/video_engine/scripts/species/agenda.mjs`,
  `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the agenda region),
  `content/video_engine/scripts/build_scene_timeline_f.py` (the page form of the agenda),
  `content/video_engine/tests/test_agenda_page.py` (NEW), `content/video_engine/tests/golden/`,
  `content/video_engine/effects/cards/species.json` + `page_species.json`
- Acceptance: E99 s16 verbatim - *"still need the beautified agenda page, which i think we discussed as basically just
  being the plate version of our list effect."* Today (`species-proof@proof-agenda.png`, 28.5 s, BACKLOG R26-80 `:486`)
  it is three plain rows - a gold numeral, white bold sans, a grey hairline - parked bottom-right with the upper
  two-thirds of the page EMPTY. The page form fills its own plate: rows placed and scaled to the page's quiet zone,
  each row carrying its CATALOGUED icon stamped on after its sentence is read (E93, heading at
  `OPERATOR-RULINGS.md:2760`;
  `render_eligible: true` per E94), the model being Steel and Paper's three-question TEST card. The dock form of the
  agenda is untouched and byte-identical.
- Validate: `python -m pytest content/video_engine/tests/test_agenda_page.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python content/video_engine/scripts/effects_catalog_check.py` then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only r26-80-agenda-page-owed`
- Evidence: report `scratchpad/assembly/P61-T8.md`. Today's agenda read cold: a flat plate, the upper two-thirds empty, three
  rows in the bottom-right corner (30% x 35%), no ground, no heading, no mark per row, the figure in footnote grey. The MODEL
  (Steel and Paper's TEST card) read beside it: mounted, titled, column heads, a mark per row, fills its box, closes itself,
  and the rows happen. BUILT: `form: "page"` on the agenda declaration - `paintAgenda` branches on `agendaIsPage` as its first
  statement and the dock form's body is untouched (every committed golden byte-identical). `agendaPageLayout` (the board inset,
  the title's room, rows dividing the rest exactly, ONE scale for the block - the dock's cap of 1 was what kept rows body-sized
  on a plate), `agendaRowRead` (E93's instant), `agendaStampF` (nothing until the sentence is read, then a fall from 1.45 with a
  stop-motion squash at impact), `paintAgendaPage` (title + rule, per row: mount, the medallion the nib draws, numeral, the
  rule along the row's bottom edge, text, the sub as a gold FIGURE, the icon as an <image> from the catalogue). The COMPILER:
  the first render path to the operator's catalogue - `catalogue_icon` refuses by name an id not in the catalogue, not kind
  icon, not operator_approved, not render_eligible (E94), not on disk, or whose bytes no longer hash to the recorded sha; the
  page form's region must cover >= 0.55 on both axes (E99 s16: the page fills its own plate); a row without an icon, an icon on
  a dock, a title on a dock - all refused with the fix named. Goldens: `agenda-page` (12.0 s, the page at rest) + @proof-first-row
  5.54 (the sentence written, its icon NOT yet there - E93's order in a frame) / @proof-stamp 7.39 (mid-fall) / @proof-full 9.30.
  Parent's read: a titled board, each row on its own mount with a drawn medallion numeral, the figure in gold, the operator's own
  icons (Liberty/flag, the falling percent, the household basket) stamped on - beside today's corner list it is the beautified
  plate. Deviation named: the five new classes are styled as presentation attributes because the player template is outside
  the write set; moving the four palette dials into the template's CSS is a one-line follow-up (T11 backlog). Validation: see the
  report's final lines (recorded by the parent after the lane's resumed run).
- CAPABILITIES row changed: **:43** (THE NUMBERED AGENDA) gains the page/plate form

### T9: THE GALLERY - a faster build, and a clip where a still cannot show the effect
- Status: complete (2026-09-15) - HG9 open on the queue as `p55-gallery-speed-and-motion` (watch)
- Owner: `junior_developer` (**NO engine lock** - the code runs beside T2-T8; **but the TIMING runs of (a) are
  scheduled when no engine lane is executing**, both the before and the after, or the numbers mean nothing)
- Depends on: none
- Write set: `content/video_engine/scripts/build_effects_gallery.py`, `content/video_engine/effects/gallery/**`
  (generated), `content/video_engine/tests/test_effects_gallery.py` (NEW/extended)
- Acceptance: E99 s20 verbatim - *"yes, but the page builds slow, and the examples are only pictures when sometimes
  someone would need to see a sequence, a gif, or a video to understand."* Three measurable bars:

  **(a) SPEED - a number, not "materially faster".** Record the BASELINE first: three consecutive runs of
  `python content/video_engine/scripts/build_effects_gallery.py` on an otherwise **idle machine - no engine lane
  running, no clip render, no golden suite in flight** (the engine lanes T2-T8 saturate the same CPU and would make
  any before/after meaningless), median wall-clock in seconds, written to Evidence with the machine and the timestamp.
  **The bar: the after-median is <= 0.50x the before-median** on the same three-run protocol. If the slice cannot
  reach 0.50x it reports the number it did reach and WHY (which stage dominates), and the parent decides - it never
  silently lowers the bar.

  **(b) THE PAGE IS PINNED.** The gallery page gets a pinned frame set so "faster" can never mean "renders less":
  a golden capture of the built `content/video_engine/effects/gallery/index.html` at a fixed viewport - the top of the
  page, one mid-page axis section, and the foot - registered in `test_golden_frames.py` the way every other golden is,
  plus an assertion that the built page still lists **every** card in `docs/EFFECTS-CATALOG.jsonl` (count equal, no
  card dropped). The three frames must be byte-identical before and after the speed work, except where a motion
  example replaced a still (those cases named in Evidence).

  **(c) MOTION - three effects, named, with the command.** An effect a still cannot show carries a sequence, gif or
  video, rendered through `review_queue_proofs.py`'s existing headless-Chromium-to-ffmpeg path, REUSED, never
  re-implemented. The effects that get motion are chosen by a STATED rule - a composite with more than one phase, or a
  card whose `does` names a change over time - not by taste. HG9 asks about **three** of them, and the card's clips
  are rendered by: `python content/video_engine/scripts/review_queue_proofs.py --clips --only p55-gallery-speed-and-motion`
  (the card's `where` carrying the three clip paths, one per effect; the three are named in Evidence before the card
  is asked). `dock_payload:stack` (five phases) and `exit:melt` (sag, ball, ending) are the obvious two by the rule;
  the third is the slice's to pick and justify.

  The catalogue's cards and `docs/EFFECTS-CATALOG.{jsonl,md}` are not edited by this slice. E99 s14 stands: the gallery
  is KEPT - *"why are you suggesting to potentially trim or retire the effects gallery?"* - no keep/trim/retire
  question returns.
- Recall (`docs/runbooks/RECALL-RECEIPT.md`): `docs_find "gallery"` returns **exactly 1 hit** -
  *"[capabilities] CAPABILITIES.md:318 - The effects catalogue - LIVE - one card per effect the engine performs
  (129 cards on 18 axes...)"* - the gallery itself is documented only as a line inside the catalogue's row, which is
  why its build has no timing on record to beat. The baseline in (a) IS the record.
- Validate: `python -m pytest content/video_engine/tests/test_effects_gallery.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/build_effects_gallery.py` (the timing printed; the three-run median protocol of
  (a), machine idle) then
  `python content/video_engine/scripts/effects_catalog_check.py` (0 failures - the catalogue must not drift) then
  `python content/video_engine/scripts/review_queue_proofs.py --clips --only p55-gallery-speed-and-motion`
- Evidence: report `scratchpad/assembly/P61-T9.md` (parent read it, the two pinned frames and one mid-window frame of
  each clip). (a) SPEED: baseline 0.206 / 0.201 / 0.194 s (median 0.201; idle check busy_python 0, CPU 10.2 / 4.7 / 5.6 %)
  -> after 0.106 / 0.096 / 0.098 s (median 0.098 = 0.488x, CPU 3.3 / 8.1 / 6.1 %): the dominant stage was the directory scan
  (`resolve_proof` globbed the frames dir ~300 times); now ONE `scandir` (`FrameIndex`), `copy_if_stale` (19.3 MB no longer
  re-copied), one tally, no argparse/shutil/urllib on the no-flag path. (b) PINNED: `gallery-top`, `gallery-axis-kinetics`,
  `gallery-foot` at 1280x900, byte-identical before and after (955b0da0.., f58c925f.., e8f8a1fc..); 180 records = 180 tiles
  asserted; a 1 px CSS perturbation test proves the pin bites. **Deviation ratified by the parent:** the three are a sibling
  `PAGE_SURFACES` register (`build_golden_sources.py`, `test_golden_frames.py`), not `SURFACES` members - a static page has
  no `#scrub` to seek, so membership would break `render_baseline.py --check/--update`; the comparison lives in
  `test_effects_gallery.py` (20 tests). Write set extended by acceptance (b), which names `test_golden_frames.py`:
  that file and `tests/golden/build_golden_sources.py` gained the `PAGE_SURFACES` register and the three `*.page.json`
  sources + `gallery-*.png` goldens - ratified. The pin is of the clip-free page (goldens derive from committed inputs; the mp4s
  are gitignored). (c) MOTION by a stated rule (more than one phase AND a golden that already needed extra `@proof-*`
  instants; ranked by phases then instants; re-derived by a test): `chart_to:compare` (10/3, compare-morph 12.0-15.4 s),
  `exit:melt` (5/4, melt-page 14.8-17.6 s), `dock_payload:stack` (5/1, verdict-stack 2.4-20.8 s; window tightened from
  21.2 s after the parent-style read of its contact strip); rendered by CALLING `review_queue_proofs.render_clip`; the tiles
  carry them as `<video class="motion">`. Validate: `122 passed in 214.43s`; the build's counts line, exit 0;
  `effects_catalog_check: 0 failure(s), 2 example(s) skipped, 42 recipe(s) (15 proven, 7 decoration(s))`. Not done here:
  CAPABILITIES:318 (T11's).
- CAPABILITIES row changed: **:318** (The effects catalogue) - the gallery's line gains the motion examples

### T10: SAVED STATES OR PER-AGENT ENGINE COPIES - a DESIGN sheet, three routes with their costs
- Status: complete (2026-09-15) - HG10 open on the queue as `r26-84-engine-saved-states` (kind rule)
- Owner: `architect_sol` -> parent (**NO engine lock**; no product code)
- Depends on: none
- Write set: `docs/research/runs/p61-saved-states/OPTIONS.md` (gitignored disk-as-bus) ONLY
- Acceptance: E99 s23 verbatim - *"we already experienced a big drift/sprawl mess from using worktrees. I'd rather not
  diverge to different worktrees, cant we just make a better engine/editor so that we can have saved states, or build
  copies of the engine/compiler per agent?"* The sheet states the problem as the record has it (the engine and
  compiler take ONE writer at a time - PRP_EXECUTION "Lane write sets", BACKLOG R26-84 `:490`; worktree sprawl is
  refused - memory `worktree-sprawl`), then gives AT LEAST THREE routes, each with: what it is in this repo's terms,
  what it costs to build, what it breaks, what it does NOT solve, and how a saved state is proven identical (the
  DETERMINISM CHECK of CAPABILITIES:109 is the existing proof mechanism). The routes the record already argues and
  which the sheet must at minimum evaluate: (1) **the sidecar route** - per-agent `overrides.json` layered over one
  engine (CAPABILITIES:108, P51 T5: keyed by row id and field), the smallest change and the one already built;
  (2) **the saved-state route** - a named, addressable snapshot of a build's inputs + the engine revision, restorable
  and diffable, proven by the hot-reload determinism check (CAPABILITIES:109, P51 T4); (3) **the per-agent engine copy
  route** - the engine + compiler vendored per agent under one checkout with a merge discipline, which is what the
  operator literally asked about and which must be costed against the sprawl it is meant to avoid. The sheet ends with
  ONE recommendation and says plainly whether the chosen route is a slice of this plan or its own plan.
  **The agent's current reading (to be argued, not assumed): this becomes its own plan (P62) if the operator picks
  route 2 or 3 - both are a persistence/identity model for builds, which is PRP-sized work of exactly the kind
  PRP_EXECUTION reserves for a plan - and stays a slice here only if route 1 is picked.** No code is written in T10.
- Validate: `python content/video_engine/scripts/docs_find.py "saved states"` and
  `python content/video_engine/scripts/docs_find.py "override sidecar"` and
  `python content/video_engine/scripts/docs_find.py "hot reload"` quoted in the sheet's Recall header (the first
  returns 0 hits - that is the finding, and `Recall: docs_find 0 hits for "saved states"` is the receipt); then the
  parent verifies every `path:line` in the sheet resolves
- Evidence: `docs/research/runs/p61-saved-states/OPTIONS.md` (gitignored, `.gitignore:53`). Recall receipt in its
  header: `docs_find` 0 hits for "saved states" (the finding), 3 hits each for "override sidecar" (CAPABILITIES:108)
  and "hot reload" (CAPABILITIES:109). Parent verified the load-bearing `path:line`s with rg: `authoring/table.py:59`
  (`table = Path(ep) / shot_table_file`) and `:69` (`write_shot_table(table, rows, header)`) - the write-back defect;
  `render_baseline.py:270` (a served build never reaches back into docs/) and `:283` (`engine_sha256`);
  `BACKLOG.md:490` (R26-84 REVIEWED 2026-09-14: not yet); `OPERATOR-RULINGS.md:3037` (E99 s23). Three routes,
  each with what it is, its cost, what it breaks, what it does not solve, and the proof of identity (byte-identical
  re-compile + `determinism_check.py --against`). Recommendation: route 2 as its own plan P62; route 3 refused as
  E99 s23's sprawl with fewer tools; route 1 already built and solves five row fields, not the engine. One P61 slice
  proposed: `apply_sidecar` stops rewriting the shared episode shot table (`table.py:59`, `:69`) - which moves the
  human-readable literal into the build dir, a doctrine change for HG10's ruling. No code written, no git state changed.
- CAPABILITIES rows cited (not changed by T10): **:108**, **:109**

### T12: THE FRAME CLOCK - the render at 24 fps, plate life on the 2s grid (E99 s36)
- Status: complete (2026-09-15) - proven by measurement, no gate asked
- Owner: `junior_developer` (**ENGINE LOCK** - one dial in the engine; takes the lock after T6)
- Depends on: T6 (the lock only)
- Write set: `content/video_engine/scripts/render_episode.py` (FPS 30 -> 24), `docs/content-video-engine/samples/scene-evidence-engine.mjs`
  (the plate-life block's `LIFE_FPS` 10 -> 12 ONLY - it is inline engine code, not a module), `content/video_engine/scripts/species/breakthrough.mjs`
  (its comment that names the 30 fps delivery, :130) + `sync_kinetics.py --write`, `content/video_engine/scripts/measure_cut_offsets.py`
  (`FPS = 30.0` :44, the 3-frame `CUT_LEAD_S` note :181), `content/video_engine/scripts/measure_seam_frames.py` (`DIP_CORE_FRAMES` :40 and the
  30 fps grid notes :39-43), `content/video_engine/tests/test_render_clock.py` (NEW), `content/video_engine/tests/golden/` (any golden plate
  life re-quantises), `content/video_engine/assets/page-boxes.v1.json` (sha only), `docs/ANIMATION-REGISTRY.{jsonl,md}`
- Acceptance: E99 s36 verbatim - *"yes, render should be 24 fps. align plate life to 12 fps."* The renderer captures at 24; a 2s hold
  lands as exactly two rendered frames and a 3s hold as three (a probe renders a stepped element over one second and asserts every hold
  is the same length - no 2/3 alternation); plate life quantises to 12; the stop-action split (`CADENCE.FPS` 24, `ON1_PX_S` 154, camera
  on 1s, boil on 3s) and the soak's 8 fps step are UNCHANGED and a test pins them; the measurement scripts' frame guards say 24 (or
  seconds) and their tests still pass; the gates' seconds-valued dials do not move (`DIP_S`, `BLURZOOM_S` byte-identical); every golden
  byte-identical except those plate life re-quantises, which are listed by name in Evidence with their instants. No approved cut is
  re-rendered (E45; the Japan short's re-render is the T11 backlog row).
- Recall (`docs/runbooks/RECALL-RECEIPT.md`): `docs_find "stop-action"` -> CAPABILITIES:75 (stop-action mechanics, LIVE) and
  `kinetics/stopaction.mjs` CADENCE.FPS 24 / ON1_PX_S 154 - the split already exists; `docs_find "on 2s"` -> the animation-craft brief's
  cadence rule (:187) and the drop blueprint's s4 at 12 fps on 2s; the one contradiction is `render_episode.py:33` FPS = 30.
- Validate: `python -m pytest content/video_engine/tests/test_render_clock.py content/video_engine/tests/test_golden_frames.py content/video_engine/tests/test_kinetics_flags.py -q` then
  `node --test content/video_engine/tests/kinetics/*.test.mjs` then `python content/video_engine/scripts/sync_kinetics.py --check` then
  `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/japan-tariff-trick/build-short` (unchanged reading)
- Evidence: report `scratchpad/assembly/P61-T12.md`. Moved: `render_episode.py` FPS 30 -> 24 (every frame count derived from it;
  the audio mux and the captions stay seconds); the engine's plate-life dial `LIFE_FPS` 10 -> 12 (+ its stale '10 fps' comment);
  `species/breakthrough.mjs`'s 30 fps comment + `sync_kinetics --write` (41 regions); `measure_cut_offsets.py` FPS 24.0 with
  `CUT_LEAD_S` 0.10 unchanged (re-expressed in seconds); `measure_seam_frames.py` gains `FPS = 24.0`, `DIP_CORE_FRAMES` stays 2
  (grid-independent: 2 frames at 30 = 0.067 s = 1.6 at 24, rounds to 2). NEW `test_render_clock.py`: the render clock 24, the
  plate-life dial 12 read out of the engine text, CADENCE.FPS 24 / ON1_PX_S 154 / SOAK_STEP.FPS 8 unchanged, and THE EVEN-HOLD
  PROBE - a stepped element rendered over one second at the render clock: on 1s [1 x 24], on 2s [2 x 12], on 3s [3 x 8], plate
  life [2 x 12]; the controls show the defect the ruling removed - 30 fps on 2s alternates [2, 3, 2, 3, ...] and plate life at
  10 on a 24 grid runs [3, 2, 3, 2, 2, 3, ...]. GOLDENS RE-PINNED: NONE - 113/113 byte-identical, proven correct rather than
  lucky: `LIFE_FPS`'s only consumers are the `plate_life` species (0 golden sources use it) and the PHRASE boil (`caption_style`
  None in all 58 sources). Validate: pytest 131 passed; node 572/572; sync in sync; the measure + page-boxes tests 73 passed;
  registry 0 orphaned; gate_motion_density on the approved Japan cut byte-identical under both dials (A/B with the engine
  restored; its reading is 4 FAIL / 16 PASS since M44 - E45, the cut untouched). Page-boxes re-pinned sha-only. One line in
  `test_measure_cut_offsets.py` (a duplicated dial de-duplicated) ratified. The catalogue card that still said plate life is
  10 fps corrected by the parent with the catalogue rebuilt.
- CAPABILITIES rows changed: **:75** (stop-action mechanics gains the render clock) and the plate-life line of **:121**

### T13: THE DARK SPAN BECOMES THE DEFAULT (E99 s46)
- Status: complete (2026-09-16) - the ruling's default in the engine; no card (r26-68 ruled E99 s46)
- Owner: `junior_developer` (**ENGINE LOCK** - one dial default)
- Depends on: HG-span ruled (E99 s46)
- Write set: `content/video_engine/scripts/species/span.mjs`, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the span
  region), `content/video_engine/scripts/build_scene_timeline_f.py` (`KINETICS_DIALS` span_tone / span_alpha defaults),
  `content/video_engine/tests/test_kinetics_flags.py`, `content/video_engine/tests/golden/` (every golden with a span re-baselined,
  listed by name), `content/video_engine/effects/cards/*.json` (the span card's default)
- Acceptance: E99 s46 - `span_tone` dark at `span_alpha` 0.30 is the default for a new build; the approved cuts render byte-identical
  through their frozen players (E45); the goldens that move are exactly the ones carrying a span, named in Evidence.
- Validate: `python -m pytest content/video_engine/tests/test_kinetics_flags.py content/video_engine/tests/test_golden_frames.py -q` then
  `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/effects_catalog_check.py`
- Evidence: report `scratchpad/assembly/P61-T13.md`. `species/span.mjs:61-62` `TONE: "dark"`, `ALPHA_DARK: 0.30`; `spanToneIsDark` /
  `spanGround` (:170-178); `spanAlphaOf` falls back by tone (0.30 dark / 0.16 light, :187-191); the engine's span region re-inlined
  (`spanGround(KIN.span_tone, col)` :10129); the compiler's `SPAN_DIAL_DEFAULTS = {span_tone: dark, span_alpha: 0.30}` (:4715) into
  `build_kinetics()`; the two sides' agreement pinned in `test_kinetics_flags.py:57-91`; `span.test.mjs` 0.160 -> 0.300 + 3 tests.
  GOLDENS: exactly one moved - `span-decade` (b6bfdecf -> e089cb23); every other byte-identical. Parent's read: the run-up band
  sits darker than the page under the untouched name, the gridlines and the four figures read through it. The Japan build-short's
  frozen player untouched (E45); `gate_motion_density` on it unchanged: 4 FAIL / 0 WARN / 16 PASS / 1 JUDGE / 8 INFO. Card
  `page_species` span dials name the default. Page-boxes re-pinned sha-only. Validate: node 600/600; sync in sync; pytest 148;
  effects_catalog_check 0 failures; page-boxes 44. The registry regenerates with T11 (another lane holds it staged).

### T11: THE RECORD - the CAPABILITIES rows, the backlog rows, the queue, the layers
- Status: in progress (2026-09-15) - the built half written; the operator ruled HG1 / HG3 / HG4 / HG5 / HG7 / HG8 / HG10 and the span and the cutout-dock cards the same night (E99 s39-s47, all nine recorded verbatim, the cards ruled, the rows carried); open: HG6 (asked once proof B lands with T3), the drift plate's visible proof (E99 s38), and the four follow-up slices T2b / T5b / T7b / T13 the rulings opened
- Owner: parent (Claude/Fable docs lane)
- Depends on: every gate ruled
- Write set: `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md` (rows R26-70, R26-76,
  R26-80, R26-82, R26-84, R26-86, R26-117, R26-118, **a NEW row for the Japan re-render (E99 s34: "eventually, not
  now")** and P47/P48's status lines only),
  `docs/content-video-engine/review-queue.v1.json` + the generated `REVIEW-QUEUE.md`,
  `docs/portable/OPERATOR-RULINGS.md` (the new rulings the gates produce), the generated docs layers
- Acceptance: each ruled gate's answer written verbatim to `OPERATOR-RULINGS.md` with its Apply line; each backlog row
  carrying the verdict VERBATIM in bold (memory `orphan-tracking-registry`: a triage verdict is not real until a row
  carries it verbatim in bold); each CAPABILITIES row named in T1-T9 carrying its change; each queue card moved from
  "Owed" to "Ruled since the last pass" with its ruling and sources; P47 T6/T7 and P48 T5b status lines updated with
  what actually closed them; the ten generated layers rebuilt and `--check` clean.
- Validate: `python content/video_engine/scripts/build_review_queue.py --write` then
  `python content/video_engine/scripts/build_docs_layers.py --write` then
  `python content/video_engine/scripts/build_docs_layers.py --check` then
  `python -m pytest content/video_engine/tests/test_build_docs_index.py -q` then
  `python scripts/prp_validate.py .claude/PRPs/plans/P61-WHAT-THE-REVIEW-OWES.plan.md`
- Evidence: the built half (2026-09-15) - CAPABILITIES - rows amended by script (`scratchpad/assembly/record_t11.py`, every anchor
  unique): THE NUMBERED AGENDA (the page form, T8), LEDGER PAGE species (the field by its job, E99 s35, T4b), stop-action mechanics
  (the render clock, E99 s36, T12), the E64 recast row (the pointer to the seventh verb), `morph_to` (the pointer + P48 T5b's owner),
  THE MELT EXIT (the ball's shadows T5 + the gather T6, status cell), MOTION MENU species (plate life 12 fps), Two chart forms in 2.5D
  (the prism's leave T4a + the field T4b, the 'owed' clause retired), THE VERDICT STACK (the short's form T7, status + goldens), The
  effects catalogue (the gallery's speed, pin and motion examples T9, HG9 closed); ONE NEW ROW 'THE WHOLE-CHART MORPH' (`remake`, T2)
  after `morph_to`. BACKLOG - the verdict written VERBATIM IN BOLD on R26-70 (BUILT, T2), R26-76 (BUILT proof A, T6), R26-80 (BUILT,
  T8; its stale E94 line corrected), R26-82 (BUILT, T7), R26-84 (DESIGNED, T10), R26-86 (HG9 CLOSED, T9), R26-117 (CARD CREATED),
  R26-118 (BUILT, T5); SEVEN NEW ROWS R26-137 the Japan re-render carrying M44's FAIL reading (E99 s34), R26-138 the shared
  `kinetics/vortex.mjs`, R26-139 the axis hairlines, R26-140 the warm-pixel drift, R26-141 the catalogue-check schema gap, R26-142
  the agenda palette dials + the 9:16 golden, R26-143 the remake's 6 px corner detail. Doc 41 s2 beat 3 rewritten to E99 s35. This
  plan's six `node --test <dir>` lines corrected to the `*.test.mjs` glob (node 24). P47 T6 / T7 status lines: the BLOCKER removed by
  T2, the third watch still P47's to schedule; P48 T5b: P61 T3 named as its owner. The queue's cards are the slices' own records
  (HG1 / HG3 / HG4 / HG5 / HG7 / HG8 / HG10 open; HG9 and p55-gallery ruled). STILL OWED by T11 when the gates are ruled: each
  ruling verbatim into OPERATOR-RULINGS with its Apply line, each card moved to 'Ruled since the last pass', the plan to `complete`.

## Verification

**Per slice, in this order, each command run UNPIPED** (memory `never-pipe-gated-steps-to-tail`: `tail`'s exit code
masks a FAIL, and a failure shipped twice that way):

1. `node --test content/video_engine/tests/kinetics/*.test.mjs` - the pure-function tests for any kinetics module touched (the bare
   directory form fails on node 24 - CJS directory resolution - identical on a pristine HEAD; T2 found it, T11 corrected the line).
2. `python content/video_engine/scripts/sync_kinetics.py --check` - the engine's mirrored regions are in sync.
3. `python -m pytest <the slice's new test file> content/video_engine/tests/test_golden_frames.py -q` - the new
   behaviour proven AND every pre-existing golden byte-identical.
4. `python content/video_engine/scripts/effects_catalog_check.py` - 0 failures (no phantom card, no missing anchor, no
   proof that is not on disk, no example the compiler rejects).
5. `python content/video_engine/scripts/gate_motion_density.py <the slice's build>` - M23, M25, M28, M31 at or better
   than the reading recorded in Evidence; `python content/video_engine/scripts/gate_one_shot_floor.py <build>` where a
   cut is touched (M35-M42).
6. `python content/video_engine/scripts/review_queue_proofs.py --clips --only <the slice's item id>` - the card's clip
   exists on disk; or the before/after crop through the same file's `diff_box` (which REFUSES a pair differing only
   inside the caption box).
7. **The frame read.** After a visual change, the parent reads the RENDERED frames at the instants that matter as a
   viewer, not the diff (memory `judge-the-frame-not-the-diff`), and measures the geometry behind them. Verifying your
   own change is a different check and misses everything you did not touch.

**Plan-level:** `python scripts/prp_validate.py .claude/PRPs/plans/P61-WHAT-THE-REVIEW-OWES.plan.md` must PASS, and
`python scripts/prp_status.py` must show this plan.

**Standing constraints checked at every integration:**

- No approved cut is rebuilt (E45). The Japan tariff short (APPROVED + rendered 2026-09-09) and the Tokyo remake are
  regression fixtures. A change to how they render ships behind a flag defaulting to today's look.
- A fix never lowers motion (E99 s11). If a gate's motion reading drops, the slice is not done.
- Figures are never fabricated; the record outranks recollection and the code in front of you.
- Every proposed mechanism opens with its `Recall:` receipt (`docs/runbooks/RECALL-RECEIPT.md`) - and the rule binds
  this plan first: **T2, T3, T5, T6 and T9 each carry a `Recall:` line that QUOTES its `docs_find` hit** (T5's is the
  finding that `Fresnel` in this repo is the Euler-spiral integral in `kinetics/clothoid.mjs`, not a shading term;
  T9's is that `gallery` returns exactly one hit). `Recall: docs_find 0 hits for "<term>"` is a valid receipt - T10's
  is exactly that for `saved states`; a bare assertion that recall was run is not.

## Evidence And Handoff

**Where evidence goes.** Per-slice run transcripts, trace tables and option sheets go to
`docs/research/runs/p61-<slug>/` (gitignored disk-as-bus), command logs through `sqz compress --mode safe` - never the
test verdicts, hashes or security evidence. Goldens and their sources go to `content/video_engine/tests/golden/`.
Queue clips land in `content/video_engine/review/queue/clips/` (gitignored) via `review_queue_proofs.py --clips`.
Proof builds go to NEW private build directories, never an approved cut's.

**The delegation contract** (PRP_EXECUTION "Hand-off policy"). Each brief names: this plan path, the task id, the
allowed files, the acceptance, the exact validation command, the answer cap (<= 200 words as `path:line` + values), and
where the full evidence goes. A delegated agent returns "not found in <the places I searched>", never "does not exist".
The parent verifies every negative with one grep, reads every diff, and runs the slice's validation itself before
integrating. A subagent summary is not proof.

**How a gate is asked.** The parent updates `review-queue.v1.json` (the card's `judge` = the one plain sentence with
the time range and what changes; `where` = the clip or crop paths; `options` = empty for HG1-HG9), regenerates
`REVIEW-QUEUE.md` with `build_review_queue.py --write`, and serves
`python content/video_engine/scripts/serve_review_queue.py` (http://127.0.0.1:8766/). The operator's answer appends to
`review-answers.jsonl`; the parent applies it (`build_review_queue.py --answers`) and writes it to
`OPERATOR-RULINGS.md` and back into this plan. A served review build is never rebuilt under the operator - an agent
practice from the 2026-09-11 incident, not an operator ruling (E99 s11).

**Open decisions for the operator (the record does not settle these; the parent asks them, the plan does not assume
an answer).**

1. **Which pair and which data is the canonical proof** - `line -> bars`, `bars -> line`, or both, and on the Tokyo
   test bed or a new private build?
2. **T10's home.** Whether saved states becomes its own plan (the agent's reading: yes for routes 2 and 3) is HG10's
   second half.

**Answered since the draft - E99 s34 (`OPERATOR-RULINGS.md:3143`), both items closed and folded into the slices:**

- *How far does "the entire chart" reach into TEXT?* **Answered.** The bar is two readings, not a mechanism: it reads
  as a transformation, not a cut, and reads as intentional; the entire chart transforms; *"the text is re-written or
  directly morphed - both is a transformation"*. T1 measures both routes, T2 takes the one that reads (T2's bar block;
  T1's acceptance). No longer open.
- *Is the approved Japan short re-rendered with the new melt?* **Answered:** *"Japan will be re-rendered eventually,
  but it's not a concern right now."* `melt:gather` and every P61 flag stay OFF on that short; the re-render is a named
  backlog row written at T11, not a P61 acceptance. No longer open.

**The three biggest risks.**

1. **The whole-chart bar is a READING, so it cannot be unit-tested.** E99 s34 set the bar as "reads as a
   transformation, not a cut, and reads as intentional" - the probes in T2 (no frame draws both charts flat; at
   u = 0.5 neither chart is drawable as itself) can refute a cut but cannot prove *intentional*. Only HG1 can, so a
   slice that passes every gate can still fail the gate that matters. The cost risk is now bounded rather than open:
   E99 s34 permits either text route, T1 measures both, and if `contour.mjs` does not fit the frame budget the answer
   is the re-write route - never a crossfade, which E99 s1 would refuse the way it refused the compare.
2. **Engine-lock serialization is the schedule.** Seven of eleven slices hold the lock. Only T1, T9, T10 and T11 run
   beside it. A slice that overruns delays everything behind it, and two agents editing
   `scene-evidence-engine.mjs` is how a parallel run corrupts itself (PRP_EXECUTION).
3. **T6 changes a mechanism that ships in an approved cut.** The melt is authored in the Japan tariff short. The
   `melt:gather` token keeps today's look as the default - proven byte-identical by `test_transitions_e47` and the
   existing `melt*` goldens, not promised - but it grows the melt's token surface beside `weight`, `depth=` and the
   three endings, and a token whose default is never flipped is how a refused look survives. E99 s34 removed the
   scheduling half of this risk (the flag stays off on Japan; the re-render is a later row) but not the drift half:
   **HG6 must still produce a DEFAULT for NEW cuts, not just an approval** - whether a bare `melt` becomes the gather
   going forward, or the gather stays opt-in and every new cut has to remember to ask for it.
