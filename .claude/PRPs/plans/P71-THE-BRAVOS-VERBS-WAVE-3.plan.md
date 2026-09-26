---
id: P71-THE-BRAVOS-VERBS-WAVE-3
title: The Bravos verbs, wave 3, and the engine fixes - the six engine fixes (R26-308/309/310/312/313/314), the squint gate (P69 T88), and every P69 Bravos slice not moved to P70 (T38-T43b, T40, T44, T53-T55, T57, T60, T62, T63, T67, T68, T70-T80)
status: running
operation: feature
risk: standard
owner: parent
branch: claude/fable-p68 (the plan); engine slices land on claude/p69-s90 (lane B); T8 (the label diet) on lane A
contract: tdd-v1
created: 2026-09-24
updated: 2026-09-24 (APPROVED by the operator - `/prp-implement P71` - and running; revision 2 + the s124 amendment)
---

# P71 - The Bravos verbs, wave 3, and the engine fixes

## Summary

The operator asked for `/prp-plan` on the P69 Bravos slices that did not go to P70. The aim is that once P71 lands,
every capability on the list can be built before the next one-shot test (measured against the 09-16 baseline). This
plan turns each P69 stub into a slice grounded in the code. Each slice keeps its P69 id as an alias, so the parent can
point P69 at P71; the parent edits P69, not this plan.

The plan also carries:
- the six engine fixes the backlog names;
- P69 T88, the squint gate and the H label diet;
- the P70 follow-ups P70's own plan defers: T44's formula recipe (R25, in T34), A55's traced point (in T20) and, since
  E99 s125, P69 T46 (3), a real series laid over a schematic (T39). The swap on an axis_tag pill waits on P70 T10 and
  is listed under Not Building.
- the five rulings of 2026-09-24 evening: s124 (a dock over a chart hovers by default and blurs by the author's
  option; T15), s125 (a real series over a schematic on its own axis, where it sits drawn as a claim; T39), s126 (M48
  blocks, and it reads the captions too; T7, T8), s127 (the seal gold `#E8B86D` and its gold shockwave; carried by P70
  T1c, which T5, T12 and T18 wait on) and s128 (a stamp is drawn over the world, a prop lives in it; T5).

Every verdict below comes from recall first (`$SP/p71-plan/recall-raw.txt`: 50 docs_find runs from the lane-B root),
then from the code read by symbol. Draft 1 read lane B at `557e1dc` (`$SP/p71-plan/src/`, a `git show 557e1dc:`
export). **Revision 2 re-cites every engine and compiler `:line` at lane B `50b2f85`** (P70 T1b, the seal, committed;
no tracked file dirty at capture), read with `git show 50b2f85:<path>`, so nothing uncommitted is cited. Between the two
heads the engine moved +31 lines from `:2322` to `:16882` and +176 past `:17190`; the compiler moved +9 to +217 past
`:207`; `ledger_page.py`, `gate_motion_density.py`, `measure_line_bloom.py` and every species module except `chip.mjs`
are unchanged.

### The slice table

| P71 | was | title | class | owner | wave | depends on |
|---|---|---|---|---|---|---|
| T0 | - | base, approval, register, queue row, P69 pointers, the BOOM verification hand-off | - | parent (+ speedster for the pointer lines) | 0 | the operator's approval |
| T1 | R26-314 | a figure writes its last letter | EXTEND (a fix) | junior_developer | 1 | T0 |
| T2 | R26-308 | a title relight clears on its last frame, on the title standing at t | EXTEND (a fix) | junior_developer | 1 (frame read after P69 T37c) | T0; P69 T37c for the re-pin |
| T3 | R26-310 | a plain recast on the default clock never stands a half-written tick on an empty plot | EXTEND (a fix) | implementation_luna | 1 | T0 |
| T4 | R26-312 | the second melt throws the page on screen | EXTEND (a fix; diagnose first) | implementation_luna, reviewer | 1 | T0 |
| T5 | R26-313 | a stamped chip's seal is reserved: OTHER elements on its beat go round it, the stamp stays over the chart (s128) | EXTEND | junior_developer, reviewer | 3 | P70 T1c (P70 T1b landed at `50b2f85`) |
| T6 | R26-309 | a prop's exit near its page's end is honoured or refused with numbers | EXTEND (a fix; diagnose first) | implementation_luna, reviewer | 5 | P70 T8, P70 T9, T15 |
| T7 | P69 T88 (gate) | the squint gate, M48: a FAIL, pages and captions (s126) | REUSE (T37b's measure) + NEW (a gate row) | implementation_luna, reviewer | 2 (or the first wave after P69 T37c) | T0; P69 T37c |
| T8 | P69 T88 (lane A) | the H label diet on the divergence page's end tags | bounded discovery, then REUSE (lane A) or EXTEND (lane B) | implementation_luna | 8 | T7 merged into lane A; lane A's in-flight door commit; P70 T2 if the lane-B route is taken |
| T9 | P69 T38 | `axis_tag` and the drop guide | NEW | implementation_luna | 2 | T0 |
| T10 | P69 T39 | `level_join` | NEW | implementation_luna | 2 | T0 |
| T11 | P69 T43 | `loop`: a flow laid as a ring, tokens on its arrows | EXTEND | implementation_luna | 2 | T0 |
| T12 | P69 T42 | chip states `lit` / `tick` / `sell` (+ `buy`) | EXTEND | implementation_luna, reviewer | 3 | P70 T1c (`chip.mjs`; P70 T1b landed) |
| T13 | P69 T43b | a second axis and an inverted one (R26-307) | EXTEND | implementation_luna, reviewer | 3 | P70 T2 |
| T14 | P69 T55 | the decade ruler: a scrolling time-passage ground under a chip row (RESCOPED by BOOM's frames) | NEW | implementation_luna | 3 | T0 |
| T15 | P69 T40 | the dock over a chart: `under: hover` or `under: blur`, the author's choice by goal, over ledger pages; R3 (s124 amended) | EXTEND | implementation_luna, reviewer | 4 | P70 T8, P70 T13 |
| T16 | P69 T41 | `project`: a labelled dashed continuation | EXTEND | implementation_luna, reviewer | 4 | T13 |
| T17 | P69 T57 | hub and spoke, and a link that fails | EXTEND | implementation_luna | 4 | T11 |
| T18 | P69 T53 | the "?", the collage that resolves into it, the predictions board | EXTEND | implementation_luna | 5 | T12, T15, P70 T1c |
| T19 | P69 T60 | verdict tiles, two verdict panels, the BUY tab | EXTEND | implementation_luna | 5 | T12, T15, P70 T8, P70 T13 |
| T20 | P69 T62 | illustrations drawn as schematics: candles, the motif line, a ✓ / ✗ on a datum | EXTEND (of P70 T2) | implementation_luna, reviewer | 5 | P70 T2, T12 |
| T21 | P69 T73 | fills to a level: below zero, the glowing trough, the underwater fill below a prior peak (A45 confirmed) | EXTEND (REUSE `to_rule` first) | junior_developer | 4 | T10 |
| T22 | P69 T63 | the route map: tokens on routes, the routes lighting in turn; the chart beside the map and the ping frame-checked; the tilt DROPPED | EXTEND | implementation_luna | 6 | T11 |
| T23 | P69 T67 | a card joins its date: it reads in the plot's empty room (E65) or over the plot hovering / blurred (s124), then parks at its datum; the proof walk | EXTEND | implementation_luna | 6 | T9, T15, T20, P70 T8, P70 T13 |
| T24 | P69 T72 | bars re-valued then to now, the ratio after it, ranked dim-the-rest | EXTEND | implementation_luna, reviewer | 6 | T0 |
| T25 | P69 T74 | the scale-out reveal and the projected overtake | EXTEND | implementation_luna, reviewer | 6 | P70 T3, T16 |
| T26 | P69 T68 | the push to now then the unknown, evidence then the conditional future; A56 RESCOPED: a box round the last actual move, then the projection to a dated rule | EXTEND | implementation_luna | 7 | T16, T18, T9 |
| T27 | P69 T75 | the lead-lag bracket across two series (A52's travelling ring and A54's slide DROPPED) | EXTEND | implementation_luna, reviewer | 7 | P70 T5, T13 |
| T28 | P69 T76 | the line painter: trace first, the ink changes at a point (F18 already done by T37b) | EXTEND | implementation_luna | 7 | T13, T16 |
| T29 | P69 T77 | glow edges: a glow outline (F14 DROPPED; F19 retired by s121) | EXTEND | implementation_luna | 7 | T12 |
| T30 | P69 T78 | the longform chrome finish: the key chip and end badge on `solo`, the two-line source, the title capsule | EXTEND | junior_developer | 8 | P69 T37c |
| T31 | P69 T79 | labels: a category pill over axis-less story bars, logos as labels (bar and line end), the ladder to membership | EXTEND | implementation_luna | 8 | T25, P70 T2 |
| T32 | P69 T80 | the camera pedestal and the magnifier lens | EXTEND (pedestal) + NEW (lens) | implementation_luna, reviewer | 8 | T0 |
| T33 | P69 T54 | the inset echo: the plot parks, the twins stack BESIDE it, then the "?" (RESCOPED by BOOM's frames) | REUSE (a recipe; one option at most) | implementation_luna | 9 | T18 |
| T34 | P69 T44 | the Bravos recipes (six) + `the-bar-halves-its-number` | REUSE (recipes) | implementation_luna | 9 | T9, T10, T21, T24, T29, T32, P70 T6, P70 T10 |
| T35 | P69 T70 | chart-and-diagram recipes R19, R34, R35 | REUSE (recipes) | implementation_luna | 10 | T34, T12, T15 |
| T36 | P69 T71 | line recipes R21, R27, R32 (R32 unblocked: past cycles land lit, the dim is a later isolate) | REUSE (recipes) | implementation_luna | 9 | T9, T10 |
| T37 | - | integration and merge | - | parent, release_steward | per wave | each slice's review |
| T38 | - | P71-HG1: each verb as a beat played with the take, beside its Bravos frame | - | parent; the operator rules | end | T37 |
| T39 | P69 T46 (3) | the shape meets the data: a real series over a schematic on its own labelled axis, where it sits drawn as a claim (s125) | EXTEND (of P70 T2 / T20's family) | implementation_luna, reviewer | 9 | P70 T2, T13, T20 |

**What P69 does not carry into P71, and why:**
- T46 (1), (2), (4), T51, T52, T56, T58, T59, T61, T69 moved to P70. T46 (3), which P70 deferred, is T39 here (s125).
- T45, T47, T48, T50, T66 are done. T50 is `f63b569`; it hands R26-307 to T43b (this plan's T13).
- T64 is done at `c0836b8` and T65 at `bc5a82a`, although P69's stubs still read "pending". The parent corrects those two
  statuses in T0.
- T37 is done (`f8f6b06`) and T37b is done (`557e1dc`); their P69 stubs also still read "pending", and T0 corrects them.
  T37c is pending and in flight in lane B; P69 keeps it. T2, T7 and T30 wait on it (the ownership table).

No number in the brief is missing. Every stub the brief names exists in P69 under the id given, and none of them is done.

**Honest flags. Read them before approving.**
1. **The BOOM witness - VERIFIED on real frames; every BOOM gate is resolved (review finding 8).** Harvest v2 `:318`
   said "Verify the Gemini-only timings for BOOM (`jx3Ll-GJtMY` has no frames on disk) before any of R32 / R36 / A44 /
   A54 / A56 is built from them". The video was on disk all along (the main checkout's `scratch/jx3Ll_full.mp4`,
   1920x1080, 29.97 fps, 1263.1 s), and the parent's verifier read its frames: `C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/fable-p68/docs/research/runs/bravos-watch/jx3Ll-GJtMY/verify/VERIFY.md`
   (gitignored; each verdict is cited below by that path, the item folder and the TRUE times). No item waits on BOOM
   any more:
   - **Unblocked (confirmed):** T21's A45 (02:23.0, 02:48.5); T36's R32 (with a correction: the old cycles land in
     full ink, one at a time; the dim is a later isolate, 01:11-01:18); T34's epoch-walk A44 / A45 parts (A44 has one
     in-place witness, 02:27.0-02:27.5). P70 T10's badge swap (A44) is unblocked too; the parent updates P70.
   - **Rescoped to the witnessed form:** T14 (a scrolling decade ruler under a chip row; nothing pinned at a year);
     T33 (the twins BESIDE a parked plot, then a "?" - C16's own fallback; no in-plot twin); T26's A56 (a box round
     the last actual move, then the projection to a dated dashed rule and its axis pill).
   - **Dropped:** T27's A52 (no travelling ring) and A54 (no slide; A53 carries the lag); T22's tilted plane (the map
     is flat; the staggered routes are confirmed); T29's F14 (no glow perimeter; the witnessed crimson offset edge is
     a card style this plan does not build - the architect's call, reasons in T29).
   - **Kept out, reinforced:** F16 (flat ground, std 0) and F15 (ticks in series colour) were not found; C11 and C12
     are reinforced (no continuous push, no tracking pan, no vignette on chart frames).
   - **New BOOM witnesses** (recorded as evidence on the slices they strengthen, no new slice): A27 (08:19, 08:56,
     15:11) on T11 / T22; S9 (00:55-01:07, 15:32, 15:58.5) on T30; A13 (09:38-09:42) on T20; the counting pill
     ("-66%" to "-80%", 14:22.5-14:23) on T34's R18; the triple axis (14:18) on T13; the dashed path past the plot
     edge with a fill and a "?" (03:18) on T16 / T21 / T26.
   - The D40 items are Gemini-timed too, but D40's frames ARE on disk (591 + the 1080p video), so each D40-only item is
     frame-checked in its slice's step (0) (the harvest's own instruction, `:318`).
2. **A ruling conflict.** F19, the bevelled stamp slab for a "stamped verdict word" (P69 T77 (3)), conflicts with
   s121 (1): "a stamped CHIP, BADGE or VERDICT stamp lands as a seal". It also conflicts with s123 ("a seal is gold").
   It is retired from T29, not asked about: s121 (1) already rules the verdict stamp's form.
3. **Already done.** P69 T76 (3), F18 (the white-hot core), was done by T37b. s117 says T37b "takes T76's white-hot core
   forward", and CAPABILITIES has `LP_HOT`. T28 drops it.
4. **A mis-citation.** P69 T70 cites "the chart dims (T40 / `lpPlateRecede`)", but `lpPlateRecede` (engine `:9829`) is
   the two-plate FIELD's recede, not a dim. The dim under a tile is T15's `under: blur` (s124 (2)), or `panel_focus`'s
   `receded` role.
5. **A circular dependency.** P69 T44's `the-hidden-base` needs A33, the pedestal, which is T80. P69 T80 needs "T44 (the
   hidden base / iceberg the pedestal reveals)". This plan breaks the circle:
   - T32 builds the pedestal on a stage taller than the frame;
   - T34 composes it into the recipe.
   The iceberg form itself is a bounded discovery inside T34 (can T64's `segments`, a named `hline` and the pedestal
   compose it?). If they cannot, T34 files a form slice and does not invent one.
6. **Three stubs too thin to plan as written.** Each becomes a bounded discovery with an owner and a stop condition:
   - T13 (P69 T43b) names no H beat for the co-movement claim.
   - T6 (R26-309) has no root cause on disk.
   - T8 (P69 T88's label diet): draft 1's premise was false (review finding 2). The door does NOT derive the divergence
     PAGE's object; rows 1 and 4 draw the committed `ev-divergence-v1` directly, so T8 first reads what the page's end
     tags actually write, then picks its mechanism.
7. **No default change (s124 as amended - the operator, 2026-09-24: "it needs to be a choice depending on the goal").**
   T15 adds `under: hover | blur` as the author's per-dock choice; a dock over a chart naming neither compiles as today
   (byte-identical) and the compiler WARNs asking for the choice (s106). No committed dock moves.

(Draft 1's flag 7, a "double-encoded en dash" in `estimate-opens-as-a-wedge.json`, was a cp1252 misread: the file holds
one valid UTF-8 en dash, bytes `E2 80 93`, and no `C3 A2` at `50b2f85`. It is withdrawn; nothing fixes it.)

`$SP` below means
`C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad`.
The planning evidence is in `$SP/p71-plan/`:
- `provenance.txt`: both heads, both dirty sets, and the sha256 of each contended file at `557e1dc` (draft 1's capture;
  T0 re-captures at the approved base, `50b2f85` or later);
- `recall-raw.txt`;
- `take-times.txt`: every H word time cited, off lane A's `steel-and-paper/vo-h-scratch/scratch-kokoro.words.json`;
- `src/`: the committed engine, compiler, ledger_page, gate and species sources at `557e1dc` (draft 1);
- `REVIEW.md`: the fresh review of draft 1 (READY WITH FIXES, 15 findings), which this revision applies.
Revision 2's line cites were read directly with `git show 50b2f85:<path>` in lane B (no export written).

## Intent And Acceptance

Each verb is something an author can reach from a shot row, proved on a real H body beat (s60: a proof is a scene,
never a fixture) or, where no H row carries it, on a private test-bed beat that is labelled as one. Every verb is
opt-in (s124 as amended makes `under` a per-dock choice, not a default). Every
row that names none of it compiles and renders byte-identically, and so does the committed H door. Truth rules are
hard; placement findings are WARNs (s106). Each engine fix repairs a defect. It changes rendered frames on purpose, and
its goldens are re-pinned with a frame read. A gate row that s126 makes blocking (M48) FAILs at thresholds measured off
the reference, never fitted to ours (E38).

Plan-level acceptance:
1. T1-T32, T34-T36 and T39 are merged into their lane, one commit per slice,
   each with its own red, green and frame evidence in this plan. T14 and T33 are built in their rescoped, witnessed
   forms.
2. After each verb slice, the committed H door compiles identically (`engine_sha256` aside) and its rendered instants
   are identical. After a FIX slice (T1-T4, T6) and after T8, the H door's changed instants
   are listed, and each one is read by the parent as the intended change and nothing else moved.
3. The goldens are re-pinned once per wave, at the merge, with a sha table in the commit message.
   `page-boxes.v1.json` is regenerated by `measure_page_boxes.py --write`, by the parent only.
4. Every built capability has its CAPABILITIES row and its card or recipe in the same commit (the shared registry
   process). `effects_catalog_check.py` and the effects drift gate report 0 failures.
5. P71-HG1 is framed on the review queue (T0) and served at the end (T38).
6. **The successor is not a slice:** the next one-shot test, measured against the 09-16 baseline
   (`one-shot-lessons-2026-09-16`, the recipe floor, M35-M46). It opens once T37 has merged the last wave and T38 has
   been served. P71 claims only that every capability on the list can then be built. It does not claim the one-shot
   passes.

## Scope

- T1-T7 are the engine fixes and the squint gate (lane B). T8 is the H label diet (lane A, or lane B if its discovery
  says the end tag needs an engine key).
- T9-T32 and T39 are the verbs (lane B); T14 and T33 are rescoped to BOOM's witnessed forms (VERIFY.md).
- T34-T36 are the recipes: recipe JSON, catalogue regeneration, and proof beats in a new proof door directory.
- T0 is the parent's bookkeeping. T37 is integration. T38 is the human gate.

## Not Building

- **The in-place swap on an axis_tag pill** (P69 T61 (2) on any held pill; P70's Not Building). A44 is P70 T10, now
  unblocked by VERIFY.md (one in-place witness, 02:27.0-02:27.5). When P70 T10 lands, a swap on T9's pill is a
  follow-up that reuses T10's `swap`.
- **The BOOM items VERIFY.md dropped or did not find:** A52 (a travelling ring), A54 (a phase slide), the tilted map
  plane, F14 as a glow perimeter (and its witnessed offset-edge card style), P69 T55 (2)'s cards pinned at their
  years, an in-plot historical twin (P69 T54 (1)), F15 and F16. Each is recorded with its reason in its slice.
- **The equation's term docking into the page as its figure** (P69 T56 (3); P70's Not Building). P71 carries only
  `the-formula-by-its-words` (R25) in T34, which composes P70 T6's equation as it lands. No H sentence asks for the
  term to become the page's figure; it stays out until one does.
- **A brace on flow nodes, chips or figures** (v1 harvest `#13`, P70's Not Building). P70 T5 braces a stacked bar only;
  no H sentence decomposes a diagram, and P71 adds no brace form.
- **F19, the bevelled stamp slab** (retired, s121 (1) / s123); **F18, the white-hot core** (done, T37b).
- (No longer out: laying real data over a schematic is T39 under s125; a card reading on the plot at its date is T23
  (3) under E65 and s124; the inset echo is T33 in the beside form BOOM shows.)
- **The decor items** P69 already skips (T44 promo, T45 end collage, F6, F13, F16), and A64 / A65 (E59, M14).
- **H body adoption** of any verb. The body rows are lane A's (P69 T15-T33). The one exception is T8's label diet, which
  s120 names as a lane A carrier.
- **Flow orders, paid generators and new plates** (E36 consent; no paid spend).
- **Any P70 function**, until P70's slice that owns it has landed (the ownership table in the Execution Path).

## Human Gates

- **P71-HG1** (T38) comes at the end. The operator's standing word applies: "resolve all non-human blockers and i'll
  review human gates at the end". The operator watches each verb as a private test-bed beat played with the take
  (s60), frozen and served on its own port, beside the Bravos frame it was harvested from. Each engine fix is shown as
  its before and after at the H instant that showed the defect. The gate blocks nothing inside P71.
  - It carries ONE question: the adoption question, which verbs, if any, a body row adopts. It is asked once, for all of
    P71, and not again at P69-HG4. No ruled question is re-asked.
- T0 adds the queue row `p71-hg1-the-bravos-verbs-wave-3` to `docs/content-video-engine/REVIEW-QUEUE.md` (the runbook
  asks for it in the same change that frames the gate; that file is outside the architect's write set).

**Open operator questions: NONE, except the HG1 adoption question.** The rulings (E99 s87-s128) and
`review-answers.jsonl` were checked first. Draft 1's three open questions are all answered on disk:
1. **Draft 1's Q1 (C1 / C2 / C16), ANSWERED.**
   - The blur (C1): **E99 s124** (`OPERATOR-RULINGS.md:3379`). A dock over ANY chart, a chart plate or a ledger page's
     plot, HOVERS by default (it lifts, its shadow grows with the lift, it grows a step and holds on P70 T13's drift-hold
     idle, and the chart stays sharp). BLUR is the author's option per dock, by intent, and it clears on the dock's
     leave. It amends s98 and amends E63 so far as a dock may land over a ledger page's plot, hovering or blurred. Where
     the dock sits stays the author's (s106). -> T15.
   - The card or inset in the plot's EMPTY room (C16): **E65** (`OPERATOR-RULINGS.md:2111`-`:2129`, the reviewer's
     finding 3). The placer's order is "(2) the plot's EMPTY room - the largest rectangle the data's ink does not touch
     ... The READ (the landing) takes the same room enlarged toward the axis at the reading scale", and "a card in the
     plot's empty room passes both [M25, M27] because the ink is what they read". The operator's words there: *"inside
     of the empty data would be good"*. -> T23 (3) reads there (BOOM's A19 at 00:44.5 is the same form, VERIFY.md).
     T33 no longer needs it: BOOM's inset echo is the beside form (VERIFY.md, 08:45.5-08:55), C16's own fallback.
   - A card READING over the plot's ink at its date (C2): s124 (3) now lets a dock land over the plot, hovering or
     blurred. -> T23 (3) takes the empty room first (E65) and may sit over the ink when the author places it there,
     hovering or blurred, with M25 / M27 reporting it as a WARN with its numbers (T15).
2. **Draft 1's Q2 (a real series over a schematic), ANSWERED by E99 s125** (`OPERATOR-RULINGS.md:3381`): it may be laid
   over the schematic on its own real, labelled axis (dates and values), never rescaled or stretched to hug the curve;
   the schematic keeps its "shape" tag; where the series sits on the shape is the script's claim, drawn as a marker or
   ring with the claim's words, never implied by alignment. -> T39.
3. **Draft 1's approval item (M48's FAIL level), ANSWERED by E99 s126** (`OPERATOR-RULINGS.md:3383`): M48 FAILs, at
   thresholds measured off Bravos first, and ships as FAIL, not WARN-first; its scope includes the captions (the
   long-form strip and the shorts' strip) at the small size, at a floor measured off the reference. -> T7, T8.
4. **The BOOM-only items** were never an operator question, and they are now resolved by the parent's frame
   verification (VERIFY.md; honest flag 1).

## Mandatory Reads

No backend or frontend skill applies. This is a Python compiler plus a vanilla-JS, seek-safe engine. The reads are the
repo contracts:

- `docs/runbooks/PRP_EXECUTION.md` (Dispatch mapping, Hand-off policy, Lane write sets, "Before anything reaches
  main").
- `.claude/PRPs/plans/P70-THE-BRAVOS-VERBS-WAVE-2.plan.md`. Its lane-B workflow, its "Who owns what" and its registry
  list are this plan's too, and are restated only where P71 differs. Read its T1c (the gold shockwave and the open
  seal, `:407`; T5, T12 and T18 wait on it), T2 (the schematic, `:417`; T39 extends it), T8 (the dock-arrival branch,
  `:889`) and T13 (the drift-hold, `:1090`-`:1102`; its write set includes the compiler's dock / card option
  validation, and s124's hover holds on its `idle: hold`). These lines are in lane A's working tree at this revision.
- `.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`: T88 (`:1140`; its acceptance `:1145`
  is the source of "WARN first, FAIL on the operator's word", which s126 now overrides) and T37c (`:1149`; its write set
  `:1153` contends with T2, T7 and T30).
- `docs/AGENTS-VIDEO-ENGINE.md`, `docs/content-video-engine/PIPELINE.md`, `docs/content-video-engine/CAPABILITIES.md`
  (lane A: `:38` melt, `:45` ring, `:71` blurzoom, `:77` build-on, `:79` stamp, `:90` breakthrough, `:100` chip, `:101`
  press, `:103` flow, `:104` span, `:105` vecmap, `:110` tags-to-bars, `:118`-`:120` perform layer / rescale / extend,
  `:155`-`:156` depth and 2.5D forms, `:209`-`:238` P69's rows).
- `docs/portable/OPERATOR-RULINGS.md`: E99 s98 (`:3327`), s99 (`:3329`), s100 (`:3331`), s102 (`:3335`), s104-s123
  (`:3339`-`:3377`), **s124 (`:3379`, the dock over a chart), s125 (`:3381`, the series over a schematic), s126
  (`:3383`, M48 blocks and reads the captions), s127 (`:3385`, the seal gold and its gold shockwave) and s128 (`:3387`,
  a stamp is drawn over the world, a prop lives in it)**, E63 (`:2048`) and **E65 (`:2111`-`:2129`, the placer's empty
  room)**. s124-s128 are in lane A's working tree (uncommitted at this revision); the parent commits them before T0.
  Every slice names the rulings it respects.
- `docs/research/bravos-style/BRAVOS-VOCABULARY-HARVEST-v2.md` (§0 sources `:11`-`:19`, §1-§5 rows, §6 ranks
  `:247`-`:274`, conflicts `:286`-`:301`, §9 `:318`) and `docs/research/bravos-style/BRAVOS-USE-WHEN.md` (the entries
  each slice quotes).
- `content/video_engine/configs/effect_card.schema.json`, `effect_recipe.schema.json` (`use_when`),
  `scripts/effects_catalog_check.py`.
- P70's in-flight slice write sets (the ownership table below), and P69 T37c's (the title), which T2, T7 and T30 wait
  on.
- The HyperFrames drift-hold reference, `content/video_engine/hyperframes/compositions/components/drift-hold.html` (the
  "hyperframes reference" s124 names; P70 T13 ports it), for T15's hover.
- The Bravos media on disk:
  - STK `docs/research/runs/bravos-watch/4AkB4c0tTfU/watch/download/video.mp4`;
  - HIS `.../Jw8ykhoOVBQ/watch/download/video.mp4`;
  - DOM `.../PWMhM2_dj3s/watch/download/video.mp4`;
  - JPN `.../nB1eXWQlW58/watch/download/video.mp4`;
  - D40 `.../u70oUWgVoYU/video_1080p.mp4` (and 591 `frames_survey/`);
  - BUB `content/video_engine/sources/reference_analyses/bravos-the-bubbles-final-phase-has-begun/frames/frame_NNNN.jpg`
    (89 frames; `#n` is the 12 s window starting at (n-1) x 12 s, harvest `:11`);
  - CHN `.../bravos-china-just-triggered-a-new-world-order/frames/` (122);
  - BOOM `scratch/jx3Ll_full.mp4` (the video was on disk all along; `jx3Ll-GJtMY/GEMINI-REVIEW.md` is Gemini's timed
    read, superseded where they differ by the frame verification `C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/fable-p68/docs/research/runs/bravos-watch/jx3Ll-GJtMY/verify/VERIFY.md`,
    gitignored, in the fable-p68 worktree; its item folders hold the frames each slice cites).

  All of these are under the MAIN checkout `C:/Users/Snipe/Downloads/Outreach Program/` (gitignored media; the worktree
  read scope).

## Execution Path

### The lane-B workflow (every engine slice) - P70's, unchanged

P70's "The lane-B workflow" steps 1-6 apply verbatim:
1. a scratch export of lane B at the slice's base;
2. the base fail set first;
3. RED, then GREEN, then REFACTOR, logged under `$SP/p71-tN/logs/`;
4. the committed H door's byte identity, by `$SP/p69t84/scripts/door_identity.sh`;
5. an LF-only patch, `git apply --check` clean, with its sha256, per-file pytest counts (base vs patch), the
   door-identity log, a suggested CAPABILITIES row, the card or recipe JSON, and the frame PNGs;
6. the parent's review, the reviewer where named, and `release_steward` commits with explicit paths.

P71 differs in four places:
- **A FIX slice (T1-T4, T6), T15's second commit (the hover default) and T8** replace step 4's "identical" with: the
  changed H instants are LISTED, each one's before/after pair is written to `$SP/p71-tN/frames/`, and the parent reads
  each as the intended change and nothing else moved.
- **Every Expected RED is probed at the base in step 1**, as T13's was, and the probe's output is the RED's first line.
  Where the probe shows a key ACCEPTED AND IGNORED (R26-307's class: review finding 7 probed `tab`, `tick_at` and
  `glyph` on a chip, `layout` / `tokens` on a flow, `tokens` on an arc, `from` on a compare and `y2` / `ink_from` /
  `projection` on a line page, all silently accepted at `50b2f85`), the slice adds an explicit refusal BY NAME for the
  keys it introduces when they are malformed or misplaced (s106: "a silent drop is neither advice nor refusal").
- **A recipe slice (T33-T36; T26's recipes)** writes no engine code unless its slice names one bounded option. Its
  proof beats are built by a NEW proof door per slice, `content/video_engine/projects/_proofs/p71-recipes/proof_t<N>.py`
  (disjoint files). P69 T35's
  `_proofs/p69-recipes/proof_p69_recipes.py` is imported, never edited.
- **The base.** P71 starts on lane B's head AFTER P70 T1b is committed. It now is: `50b2f85` "feat(species): P70 T1b -
  a stamped chip is a gold seal" (21 files; the engine, the compiler, `stopaction.mjs`, `chip.mjs`), with no tracked
  file dirty at this revision's read. T0 re-captures the head per wave. Every `:line` below is at `50b2f85` and is
  re-read by its SYMBOL in the brief.

### What P71 must not touch until P70's owner lands (one writer per function)

From P70's "Who owns what". A P71 slice that finds it must edit one of these functions before P70's owner lands stops,
and the parent sequences it.

| P70 slice (owns) | P71 slices that wait on it |
|---|---|
| T1b: LANDED at `50b2f85` (`stopaction.mjs`, `chip.mjs`'s seal, the dock stamp paint, the compiler's `CHIP_SEAL_OPTS` / `DOCK_SEAL_REFUSED`, `chip_stamp_ring_fit`) | none now; T5, T12, T18 and T29 build on the committed seal |
| T1c (in progress on `50b2f85`; E99 s127 / s128): the stamp's impact-ring ink (`stampRing` / `RING_INK` in `kinetics/stopaction.mjs` and/or `species/chip.mjs`, synced), the engine's dock-stamp ring paint if separate, the matching compiler constant in `build_scene_timeline_f.py` if one exists, the stamp tests and the ring goldens | only where a ring matters: T5 (its frame read shows the stamped chip's shockwave, which must be T1c's gold; and it edits the compiler beside T1c's constant), T12 and T18 (both edit `species/chip.mjs`) |
| T2: `buildLedgerLine`'s tick-value and end-tag-value writes behind `pg.schematic`, `lpSchematicTag`, `ledger_page` `SCHEMATIC_SHAPES` / `schematic_series` (in progress on `50b2f85`) | T13, T16, T28 (`buildLedgerLine`), T20 and T39 (extend the schematic), T27 (3), T31 (the line-end logo), T8 (only on its lane-B route) |
| T3: `buildLedgerBars`'s gauge branch, `ledger_page` `CHART_FORMS` / `FORM_*` / `form_error`, compiler `page_form_geom` / `page_form_spec` | T25, T31 (`buildLedgerBars`) |
| T4: `ledger_page.scale_warnings`, the panel `measure` key | none (T13 adds a y2 WARN beside it, a different function) |
| T5: `buildPerform`'s bracket block, `paintBracket`, `BRACKET_FORMS`, the bracket validator | T27 (the bracket across two series) |
| T6: the new `equation` region | T34 (`the-formula-by-its-words` composes it) |
| T8: `render()`'s dock-arrival branch, `poofXf`, `ARRIVALS`, `dock_opts`, the gate's `_landings` / `_arrivals`, `authoring/audio` | T6 (the dock exit), T15 (`dock_opts`, `DOCK_OPTS`, the hover in the dock branch), T19 (the `verdict` dock key), T23 (the park target, `park_at`) |
| T9: `paintChapters` and its call in `render()`, `_validate_chapter`, the chapter lift in `main()`, `ring_obstacles`'s `extra` | T6 (both touch `render()` - sequenced) |
| T13 (drift-hold): `kinetics/idle.mjs`'s `hold` kind AND `build_scene_timeline_f.py`'s dock / card option validation (P70 plan `:1090`-`:1102`: the `idle: hold` option on a dock, i.e. the `DOCK_OPTS` / `dock_opts` pair) | T15 (`under`; hover holds on `idle: hold`), T19 (`verdict`), T23 (`park_at`): the dock-option tuple is the parent's union, and each waits on T13's landing |

**P69's in-flight lane-B slice that P71 must not touch until it lands (review finding 5):**

| P69 slice (owns, P69 plan `:1153`) | P71 slices that wait on it |
|---|---|
| T37c: `measure_line_bloom.py` (a full-resolution title cap-height read), `content/video_engine/assets/bravos-line-bloom.v1.json` (the Bravos title size), the engine's and the player template's title size token, the `--lp-title-ink` default, the overrun WARN, the title goldens | T7 (writes the same two files: `--build` and the band at n >= 5; it sequences after T37c's merge), T2 (rewrites the title glyphs' `style.color` every frame and re-pins the same title goldens; its frame read runs on T37c's merged title), T30 (draws round T37c's title), T15 (adds a `#dockveil` element to the same player template, a different region) |

### Who owns what inside P71 (parallel slices never edit the same function)

| slice | engine (functions / regions it owns) | compiler / Python (functions it owns) |
|---|---|---|
| T1 | the `figure` KINETICS region via `species/figure.mjs` (`figureSubGlyph` only; `figureGlyph` untouched) + `sync_kinetics.py --write`; `species/compare.mjs`'s dial comment `:166`-`:169` (comment only) | none |
| T2 | `paintPerform`'s RELIGHT loop (`:14525`-`:14532`) only; it READS the retitle chain (`:14534`) to resolve the standing title, and does not edit it | none |
| T3 | `lpAxisHandOver` (`:15457`) and its `AXIS_HAND` / `PLAIN_AXIS_HANDOFF` dials (`:15447`-`:15448`); `lpPaintStates`' plain-recast call line (`:16000`) and the `fedPlainRecast` derivation beside it (`:15979`-`:15980`) | none |
| T4 | `meltMount` (`:5292`), `paintMelt`'s mount-or-reuse lines (`:5345`-`:5347`), `clearMelt` (`:5504`); `render()`'s melt call site (`:20670`-`:20677`) only if the diagnosis puts the fault there | none |
| T5 | none | `row_stamp_fits` (`:8942`), `stamp_reserved_box` (`:8932`), `chip_stamp_ring_fit` (`:8335`, P70 T1 / T1b's) and its call in `main()` (`:10694`-`:10706`) |
| T6 | `render()`'s dock EXIT (`rk`, `:20849`, and the stamped exit `ex` beside it) - after P70 T8 / T9 and T15 | `scene_exit` (`:4090`; called `:10929`) or the dock's exit resolution, whichever the diagnosis names |
| T7 | none | `gate_motion_density.py`: NEW `load_squint`, `_squint_gate` (M48, pages and captions), `run`'s `squint=` argument; `measure_line_bloom.py`: a NEW `--build` mode (after P69 T37c); NEW `content/video_engine/assets/caption-squint-floor.v1.json` |
| T8 | none (lane-A route) or, on the lane-B route, `buildLedgerLine`'s end-tag name write (after P70 T2) | lane A `build_episode_h.py`: a NEW derived page object for rows 1 and 4 (the `_hook_object` pattern) and `OPEN_PAGE` / `LAYER_PAGE`; or, lane B, a `ledger_page` series key for the end tag's short name |
| T9 | NEW `species/axis_tag.mjs` region; a NEW `buildPerform` block (`axisTags`) + a NEW `paintPerform` dispatch line | NEW `_validate_axis_tag` |
| T10 | NEW `species/level_join.mjs` region; a NEW `buildPerform` block + dispatch line | NEW `_validate_level_join` |
| T11 | `species/flow.mjs`: `flowLayout` (a `ring` branch), a NEW `flowTokens` | `_validate_flow_extensions` (the `layout`, `tokens` keys) |
| T12 | `species/chip.mjs`: `chipCrossF`'s sibling `chipTickF`, a `lit` halo, the `sell` / `buy` tab | `_validate_chip`'s state keys, `CHIP_STATES` |
| T13 | `buildLedgerLine`: a NEW right-axis block (lifted from `buildLedgerCombo`'s `own` block `:11802`-`:11821` into a shared `lpRightAxis`); `buildLedgerCombo` calls it | `ledger_page.validate` (a top-level `y2` / `invert` / `claim` check), a NEW `_validate_y2` |
| T14 | NEW `species/ruler.mjs` region (the scroll; no pill, no pin) | NEW `_validate_ruler` |
| T15 | `render()`'s dock branch: the hover pose (lift, step, shadow) beside the arrival (`arriveOf`, `:20823`; the contact shadow `:20836`) - after P70 T8 and T13; a NEW `#dockveil` paint placed right after the wash/spot DIRECTION block (`:20708`-`:20719`, which knows `live`) and before `worldAnswer` (`:20722`), reusing the blurzoom veil's `backdropFilter` pattern (`:20587`-`:20588`); the player template: a NEW `<div id="dockveil">` between `#wash` (template `:676`) and `#dock-1` (`:684`) | `DOCK_OPTS` (`:118`) + `dock_opts` (`:6457`): an `under` key (after P70 T8 / T13); `read_over_build` (`:9222`; called `:10782`): a dock that names `under` keeps its authored read; the default resolution in `main()`; the gate's `_layout_faults` (`:2589`) and `_over_build_faults` (`:2745`): a dock with a resolved `under` over ink is a WARN with its numbers |
| T16 | `lpPaintExtend` (`:15395`) and `buildLedgerLine`'s path build (the dashed style for a `projection` series) | `ledger_page` series key `projection`, its validation |
| T17 | `species/flow.mjs`: `flowLayout` (a `hub` branch), an edge `fail` in the edge paint | `_validate_flow_extensions` (`layout: hub`, the edge `fail`) |
| T18 | `species/chip.mjs` (a `?` glyph as a text mark, drawn like the cross); `species/press.mjs` (the stack's recede under T15's `under: blur`) | `_validate_chip` (`glyph: "?"`), a NEW `_validate_unknown` |
| T19 | a NEW `paintDockVerdict(el, d, t)` helper (the tile-state layer on the chart-card dock's corner) and its ONE call line in `render()`'s dock loop, placed after T15's hover lines - after P70 T8 and T15 | `chart_card.py` (a `tile` size only if T10c's profile cannot carry it), the dock's `verdict` key (after P70 T13; the parent's union) |
| T20 | `buildLedgerLine`'s schematic branch (P70 T2's) for `candles` / `motif`; a NEW datum-badge block in `buildPerform` | `ledger_page` `SCHEMATIC_SHAPES` (two shapes) |
| T21 | `buildPerform` / `paintPerform`'s SPREAD block (`:14338`, `paintSpread` `:14410`: a `side` clip on the `to_rule` edge; a `level` target only if `to_rule` cannot carry it) | `_validate_page_fields`'s spread branch (`:2282`) |
| T22 | `species/vecmap.mjs`: the arc's tokens now; the ping after step (0); no tilted plane (dropped) | `_validate_vecmap_species` (`:2509`: `tokens`, `ping`) |
| T23 | the dock's park geometry (`dockGeom`'s park target, `:6411`) - after P70 T8 | `DOCK_OPTS` (`park_at`, after P70 T13), its validation; the read's place in the plot's empty room is E65's existing placer, READ, not edited |
| T24 | `lpBarMorphs` (`:14102`), `lpPaintBarMorphs` (`:14129`); `species/compare.mjs` (a `from` value) | the compare's `from` validation (`_validate_metric_comparator` `:1814`) |
| T25 | `buildLedgerBars`: a `projected` bar's paint and the rank pill - after P70 T3 | `ledger_page` `BAR_FIELDS` (`projected`), `_validate_bar_fields` |
| T26 | `species/span.mjs` (a `form: "box"` round a stretch's ink) or, if span cannot carry it, a NEW `stretch_box` `buildPerform` block + dispatch line | the span's `form` validation, or NEW `_validate_stretch_box` |
| T27 | `paintBracket` (`:14433`, a two-series span, level and elbow) - after P70 T5 | the bracket validator's two-series branch |
| T28 | `buildLedgerLine`'s stroke (an `ink_from` split); a NEW `trace` page enter | `ledger_page` series key `ink_from`; `LEDGER_ENTERS` (`:59`) |
| T29 | a NEW `glow` page species block | NEW `_validate_glow` |
| T30 | `species/solo.mjs` `paintSolo` (`:100`: the rail pill AND the end badge follow the solo); `buildLedger` (`:9015`): the source foot (`.lp-src`, `:9129`) and the title capsule round `.lp-title` (`:9125`) - after P69 T37c | `ledger_page` longform options (`source_lines`, `title=capsule`) |
| T31 | `buildLedgerBars` (`:10509`): story bars with `axes: none`, the category pill, a datum `logo`; `buildLedgerLine`'s end tag: a series `logo` at the line end (after P70 T2) | `ledger_page` story options, `BAR_FIELDS` (`pill`, `logo`), a series `logo` key |
| T32 | `kinetics/camera.mjs` (a `pedestal` key); NEW `species/lens.mjs` region | the camera key's `pedestal` validation; NEW `_validate_lens` |
| T39 | `buildLedgerLine`'s schematic branch (after P70 T2 and T20): an `overlay` series drawn on its own axes; the right axis via T13's shared `lpRightAxis`; the overlay's own date ticks in the x band the schematic leaves empty; a NEW claim-marker block in `buildPerform` | `ledger_page`: the schematic object's `overlay` key and its check (NEW `_validate_schematic_overlay`), called from P70 T2's schematic validation |

**The registries are the parent's integration points.** P70's list applies (`SPECIES_KINDS`, `PAGE_SPECIES`,
`SPECIES_WHEN`, `PANEL_SPECIES`, the `_validate_entry` dispatch chain `:3412`, `lint_species_choice.ACT_SPECIES`,
`recipe_walk.PAGE_SPECIES_KINDS`, `authoring/shapes.PLOT_MARKS`, `gate_motion_density.SPECIES_EVENTS`,
`tests/test_kinetics_sync.SPECIES`, the cards, `test_build_effects_catalog.py`'s exception list, the golden lists,
`measure_page_boxes.py`'s `GOLDEN_PAGES` / `representative()` / `BUILDERS`). P71 adds four:
- the engine's `LP_PANEL_KINDS` (`:12495`), for a page species a panel may carry;
- `buildPerform`'s return object (`:14392`) and `paintPerform`'s dispatch lines (each new page species appends one of
  each: the union is the parent's);
- `sync_kinetics.py`'s module order, for each new module;
- the `DOCK_OPTS` tuple and `dock_opts` (T15 `under`, T19 `verdict`, T23 `park_at`; P70 T8 and T13 write the same
  pair first, so the tuple is unioned by the parent after them).

**Generated files are never in a patch** (P70's rule): `docs/EFFECTS-CATALOG.*`, `page-boxes.v1.json`,
`SPECIES-BY-SENTENCE.md` and the docs layers.

**Waves.** At most four slices at once. Integration is in the listed order by `git apply --3way`, which is P70's stated
deviation: each implementer has its own scratch export, and the rule that keeps this safe is disjoint functions.

| wave | slices | why these together |
|---|---|---|
| 1 | T1, T2, T3, T4 | the engine fixes first: four disjoint functions, no P70 dependency. Their goldens re-pin once, after T4; T2's title goldens re-pin after P69 T37c's merge (both write them) |
| 2 | T7, T9, T10, T11 | the gate row (after P69 T37c; if T37c has not merged, T7 slides to the first wave after it), two new page species (registries unioned: T9 and T10 each append a `buildPerform` block, a `paintPerform` dispatch line and an `LP_PANEL_KINDS` entry - Deviation 7) and the flow's layout |
| 3 | T5, T12, T13, T14 | after P70 T1c (T5's ring frames; T12's `chip.mjs`) and P70 T2 (T13); T14 is a new species module (its `_validate_entry` dispatch line is the parent's union) |
| 4 | T15, T16, T17, T21 | after P70 T8 and T13 (T15); T16 after T13 (`buildLedgerLine`); T17 after T11 (`flowLayout`); T21 after T10. T15 is one commit (the option + the choose-by-goal WARN) |
| 5 | T6, T18, T19, T20 | T6 after T15 (both in `render()`'s dock branch) and P70 T8 / T9; T18 after T12 (`chip.mjs`) and P70 T1c; T19 after T15 (its one call line sits after T15's hover lines); T20 after P70 T2. T18's `unknown` and T20's datum badge both append a `buildPerform` block (Deviation 7) |
| 6 | T22, T23, T24, T25 | T23 after T15 (`under`) and P70 T13; T25 after P70 T3 and T16's projection grammar |
| 7 | T26, T27, T28, T29 | T27 after P70 T5; T28 after T16 (`buildLedgerLine`) |
| 8 | T30, T31, T32, T8 (lane A) | T30 after P69 T37c (`buildLedger`'s title / source, `paintSolo`); T31 after T25 (`buildLedgerBars`) and P70 T2 (the line-end logo); T30 and T31 name disjoint functions (`buildLedger` vs `buildLedgerBars` / `buildLedgerLine`); T8 is lane A (or lane B after P70 T2) |
| 9 | T34, T36, T39, T33 | recipes, after the verbs they compose (T34 after T21 and P70 T10 for the epoch walk; T33 after T18); T39 after T20 and T28 (the schematic branch and the stroke of `buildLedgerLine`) |
| 10 | T35 | R19 extends T34's R18 |

**Routing.**
- `implementation_luna` (Opus) builds the verbs, T3, T4, T6, T7 and T8.
- `junior_developer` (Opus) takes T1, T2, T5, T21 and T30: bounded, one function each.
- `speedster` (Sonnet) makes T0's P69 pointer edits, with the exact lines given.
- `reviewer` (Opus) reviews T4, T5, T6, T7, T12, T13, T15, T16, T20, T24, T25, T27, T32 and T39: the stamp (s128), a
  gate (M48, and T15's M25 / M27 change), a default change (T15, s124), a truth rule (E77, M26, s102, s109 (1), s125)
  or the camera.
- `release_steward` commits and never pushes without the operator's current word.
- The parent keeps the briefs, the frame reads, the registry unions, CAPABILITIES, the merge and the operator.

## Patterns To Mirror

- **A new page species with its checklist**: P69 T36 `104af07` (`lit_stretch`) - the module + region,
  `SPECIES_WHEN`, `lint_species_choice`, `authoring/shapes.py`, `gate_motion_density.py`, the card in
  `page_species.json`, the golden, `SPECIES-BY-SENTENCE.md`, "the H door compiles identical, renders N of N".
- **A page species that re-inks the page's own marks, pure in t**: P69 T37 `f8f6b06` (`species/solo.mjs`,
  `soloLevel`, `soloWrite`) - T12's `lit`, T30's rail pill.
- **An option on an existing species, refused by name elsewhere**: P70 T1 `5c25444` (`arrive: "stamp"`,
  `CHIP_ARRIVALS`) - T12, T17, T18.
- **A new field on a page object, refused by name when unknown**: P69 T64 `c0836b8` (`segments`, `BAR_FIELDS`,
  `_validate_bar_fields`: "a bar key the form does not know is refused by name") - T13 (`y2`), T16 (`projection`),
  T25 (`projected`), T28 (`ink_from`), T31 (`pill`, `logo`).
- **A glyph write that finishes at its window's end**: `species/compare.mjs` `compareGlyph` (`:221`-`:224`,
  `per = 1 / (n + OVERLAP - 1)`; its dial comment `:99`: "a run that stops exactly at n leaves its last letters
  half-inked") - T1.
- **A gate row read from a probe file beside the timeline, INFO until the file exists**: `load_layout` (`:2373`) +
  `_layout_gate` (`:2638`), M25 / M43; M32's `seam-frames.json` read (INFO unmeasured, FAIL on a measured fault); and
  P69 T87's M47 (`_empty_plot_gate` `:3534`) - T7 (M48 ships as FAIL, s126).
- **A candidate recipe proved as a beat, with its `use_when`**: P69 T35 (`estimate-opens-as-a-wedge.json`,
  `two-clocks.json`; the schema's `use_when`), P69 T47 `5bb0743` - T34-T36.
- **A right axis in its line's colour naming its unit**: `buildLedgerCombo` (`:11735`; `own`, `lunit`, `lcol`,
  `lp-y2`, `line_label`, `:11802`-`:11821`) - T13, and T39's overlay axis through T13's shared `lpRightAxis`.
- **A backdrop blur on a veil**: the blurzoom (`BLURZOOM_BLUR` 18 `:6059`; `bzveil.style.backdropFilter` `:20588`) and
  `panel_focus`'s recede blur (`PANEL_FOCUS.RECEDE {scale 0.86, dim 0.55, blur 5}` `:12484`, painted in
  `lpPaintPanels` `:12746`, the filter at `:12769`) - T15's `under: blur`.
- **A held idle on a dock**: `idleCssFor("dock", d.idle, ...)` in `render()`'s dock loop (`:20866`; the parked card
  `:20922`), which P70 T13's `hold` kind extends - T15's hover holds on it.
- **A decision the compiler records on the dock for the player and the gate to read**: `read_over_build` (`:9222`)
  writing `read_moved` / `read_deferred`, read back by M27's `_over_build_faults` (gate `:2745`) - T15's resolved
  `under`.
- **Golden sources read from committed objects, never re-typed**: T64's `stacked_funding_series()` in
  `build_golden_sources.py`; golden sources written LF (the T64 trap).

## Task Slices

**The TDD fields (`tdd-v1`, as P69 and P70 define them).**
- **Regression** is the command that must go RED first.
- **Expected RED** is what it prints before the change. It is probed read-only where marked "(probed)" (draft 1 at
  `557e1dc`; revision 2 at `50b2f85`), and otherwise predicted from the code. Every RED is re-probed at the slice's
  base in step 1 (the Execution Path).
- **Red / Failure attribution / Unrelated failures / Green / Refactor / Frame read / Review / Evidence** are reserved,
  `pending`. They hold the verbatim tails, the base fail set, the frame paths and the merge SHA.

**Common to every verb slice (T9-T32, T39), taken from P69's "Common to T51-T80" (a)-(f):**
- (a) Find and REUSE first. The `Recall:` lines are the finding, and a slice that finds a capability recall missed
  stops and reports.
- (b) The new card or recipe carries its USE-WHEN (act, story moment, data shape, use when / don't), copied from
  `BRAVOS-USE-WHEN.md` at the line cited.
- (c) Where the form carries data, s109's honesty test IS its check: true proportion, the figures the claim turns on
  written, and an unambiguous reading. A failure WARNs with its numbers (s106). A hard refusal is kept only for an
  untruth: a value drawn wrong, parts that do not sum, an unlabelled projection.
- (d) Every row that does not name the move compiles byte-identically: the H door and every golden.
- (e) One golden per new FORM, on a real H body beat where the slice names one, read by the parent before it is
  pinned. A recipe-only slice has no golden; its proof strip is read instead.
- (f) No body row adopts the move before HG1.
- (g) Drawn in the `longform` profile when the row takes it. Every label is at least at the s90 floor, 59.08 stage px
  (`ledger_page.CARD_TYPE_PX`). A label that names a series reads T37b's series-ink helper (s118) and sets no colour of
  its own. Motion that TRAVELS or BLINKS counts as motion; a light that sits is 0 events (s99, s91).
- (h) A key the slice introduces is refused BY NAME when malformed or misplaced; the probe decides whether today's
  behaviour is "refused as unknown" or "accepted and ignored" (review finding 7), and the RED says which.
- (i) s128: a STAMP (a seal, a stamped mark) is drawn over the world, open, the chart showing through; a PROP lives in
  the world (the resting shadow, the world's room). A slice that places either decides fill, shadow, occlusion and
  placement pressure by that line.

**COMMON-TAIL** means, each command in its own process and unpiped (never `| tail`):
`node --check docs/content-video-engine/samples/scene-evidence-engine.mjs`, then
`python content/video_engine/scripts/sync_kinetics.py --check`, then
`python -m pytest -q content/video_engine/tests/test_golden_frames.py`, then
`python -m pytest -q content/video_engine/tests/test_effects_catalog_drift.py`, then
`python -m pytest -q content/video_engine/tests/test_build_effects_catalog.py`, then
`python content/video_engine/scripts/effects_catalog_check.py`.

**BRAVOS-FRAME** means `ffmpeg -ss <s> -i "<video>" -frames:v 1 $SP/p71-tN/frames/bravos-<VID>-<mmss>.png`. `<video>` is
the path named in Mandatory Reads, under the main checkout. For BUB and CHN, where no video is on disk, it means the
frame file named. For BOOM it means `scratch/jx3Ll_full.mp4` at VERIFY.md's TRUE time (never Gemini's).

### T0: The base, the approval, the register, the review-queue row, the P69 pointers and the BOOM verification hand-off
- Status: done (the parent; evidence below)
- Owner: parent. speedster makes the P69 pointer lines, one exact line per stub.
- Depends on: the operator's approval of this plan.
- Write set:
  - this plan (status, base, T0 evidence);
  - `$SP/p71-plan/provenance.txt` (re-captured per wave);
  - `docs/WORKTREE-REGISTER.md` (lane B's row names P71 and its one writer per function);
  - `docs/content-video-engine/REVIEW-QUEUE.md` and `docs/content-video-engine/review-queue.v1.json` (the row
    `p71-hg1-the-bravos-verbs-wave-3`);
  - `.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`: each of T38-T43b, T40, T44, T53-T55,
    T57, T60, T62, T63, T67, T68 and T70-T80 reads "moved to P71 T<n>", T88 reads "moved to P71 T7 + T8", and T46 (3)
    reads "moved to P71 T39 (E99 s125)". T64 is corrected to `done (c0836b8)`, T65 to `done (bc5a82a)`, T37 to
    `done (f8f6b06)` and T37b to `done (557e1dc)`;
  - `docs/content-video-engine/BACKLOG.md` (R26-307/308/309/310/312/313/314: "carried by P71 T<n>").
- Acceptance:
  1. The base is lane B's head with P70 T1b committed (`50b2f85` at this revision, or later). `git rev-parse HEAD` and
     `git status --short | grep -v '^??'` show no tracked dirty file, and the sha256 of every file the wave edits is
     recorded.
  2. The approval is quoted here.
  3. The register row is updated before lane B's first P71 commit.
  4. The queue row exists, naming what to judge (each verb as a beat with the take, beside its Bravos frame; each fix
     before and after; T15's hover default before and after), where to look, and what it blocks (nothing in P71; the
     one-shot test).
  5. The P69 stubs and the backlog rows point here.
  6. **The BOOM verification is done and folded in** (VERIFY.md, honest flag 1): no research-lane commission is
     filed. P69's carrier map records A52, A54, F14 and the tilted plane as dropped, T14 / T33 / A56 as rescoped, and
     A44 / A45 / R32 as confirmed; P70 T10's unblocking is the parent's edit to P70.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P71-THE-BRAVOS-VERBS-WAVE-3.plan.md` then `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md` then `python -m pytest content/video_engine/tests/test_worktree_register.py -q` then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending
- T0 evidence (the parent, 2026-09-24): (2) APPROVAL, the operator: `/prp-implement P71`. (1) base: lane B `cd0b630` (P70 T1b `50b2f85`, T4 `d0dd19b`, T1c `cd0b630` committed; no tracked dirty file); P70 T2 / T3 / T13 and P69 T37c are in flight on lane B as scratch patches - P71 slices that share their functions wait (T2 waits for T37c; T15 for P70 T8 + T13). (3) register row names P71 (this commit). (4) queue row `p71-hg1-the-bravos-verbs-wave-3` (this commit). (5) P69 stubs + a BACKLOG row point here (this commit). (6) BOOM: VERIFY.md folded in revision 2.

### T1: A figure writes its last letter - the sub's hand finishes when its word does (R26-314)
- Status: done - lane B `ef96cee` (R26-314; the sub's last glyph whole at the word's end; page-figure re-pinned; H: only inside the five subs' glyph boxes)
- Owner: junior_developer (LANE B)
- Depends on: T0
- Bravos reference: none; this is a defect. For parity, HIS `Jw8ykhoOVBQ` 11:01, where the "$28 Billion" figure's
  words are whole (BRAVOS-FRAME `-ss 661`).
- Recall: docs_find "figure subtitle" -> 1 manifest hit, 0 capability rows. BACKLOG-HISTORY `:920` R26-314: "Row 10's
  "$28B a year" figure's second line reads "averag" plus a dim "e" from 249.0 s and still at 272.0 s ... the hand-write
  clock never reaches 1 on its last glyph".
- Verdict: EXTEND (a fix), one function.
  - `species/figure.mjs` `figureSubGlyph` (`:155`-`:158`) takes `per = SUB_WRITE / n` and fades each glyph over
    `per * OVERLAP` (1.6). `paintFigure` clamps `u` to 1 (`:167`).
  - So at `u = 1` the LAST sub glyph is `(0.4 - (n-1)*per) / (1.6*per) = 1/1.6 = 0.625`, which is the dim "e", for
    every figure with a sub.
  - The repo already fixed this twice: `spanGlyph` (`sp_span :205`, "The share is 1 / (n + 0.6), not 1 / n, so the
    LAST glyph is fully in exactly when the write ends") and `compareGlyph` (`sp_compare :221`-`:224`).
  - `figureGlyph` (the figure's own line) is NOT touched. Its last glyph is whole by `u = 0.6 * (n + 0.6) / n <= 0.96`,
    and `compare.mjs` imports it (`:83`; engine `:13435`, `:13601`, `:13920`).
  - **An existing test pins the defect** (review finding 9): `tests/kinetics/figure.test.mjs:202` asserts
    `near(figureSubGlyph(1, 1, 2), 0.625)`, with the comment at `:199`-`:201` ("it is recorded here, not corrected: a
    value change is a golden change"). That assertion is the one that flips. `compare.mjs`'s dial comment
    (`:166`-`:169`: "figureSubGlyph's OVERLAP slack overruns the figure's window and leaves its last glyph at 0.625")
    goes stale with the fix.
- Write set: `content/video_engine/scripts/species/figure.mjs` (`figureSubGlyph` only);
  `content/video_engine/scripts/species/compare.mjs` (the comment at `:166`-`:169` only, restated as history: the
  overrun was R26-314, fixed here); the engine's `figure` and `compare` regions via `sync_kinetics.py --write` (the
  compare region changes by that comment only); `content/video_engine/tests/kinetics/figure.test.mjs` (the `:202`
  assertion inverted to `=== 1`, its `:199`-`:201` comment rewritten, and the new law tests); the goldens a
  sub-bearing figure moves (re-pinned by the parent at the wave merge).
- Constraints:
  - `per = FIGURE.SUB_WRITE / (n + FIGURE.OVERLAP - 1)`, mirroring `spanGlyph`. No new dial.
  - A sub glyph's opacity at every `u` is at or above today's: a smaller share only brings each glyph in earlier, so
    no glyph is ever less written than it is now, and the tail finishes.
- Acceptance:
  1. For n in 1..40, `figureSubGlyph(1, n-1, n) === 1`, and `figureSubGlyph(u, j, n)` is monotone in u.
  2. The existing assertion at `figure.test.mjs:202` now reads `figureSubGlyph(1, 1, 2) === 1`, and its comment says why.
  3. `figureGlyph` is byte-identical over 1000 sampled `(u, j, n)`.
  4. `compare.mjs`'s `:166`-`:169` comment no longer claims the 0.625 tail; the compare region's code bytes are
     unchanged.
  5. H row 10's figure reads "average" whole at 249.0 and 272.0 s.
- Stop conditions: another caller reads `figureSubGlyph`'s `per` (report, do not widen); a golden moves that carries
  no figure sub (report).
- Regression: `node --test content/video_engine/tests/kinetics/figure.test.mjs`
- Expected RED: with the new law test written first, `figureSubGlyph(1, n-1, n)` returns 0.625 for every n >= 1
  (computed from the law at `figure.mjs:155`-`:158`, unchanged at `50b2f85`), so the new assertion fails. The existing
  `:202` assertion passes at the base and is the one inverted at GREEN.
- Validate: `node --test content/video_engine/tests/kinetics/figure.test.mjs` then `node --test content/video_engine/tests/kinetics/compare.test.mjs` then COMMON-TAIL
- Frame acceptance: the parent reads H row 10's figure at 249.0, 260.0 and 272.0 s, before and after
  (`$SP/p71-t1/frames/`), beside `$SP/p69-m47/j5late/zoom-272.png`, plus every re-pinned golden's before and after.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T2: A title relight clears on its last frame - the relight is a pure function of t (R26-308)
- Status: done - lane B `11b94d1` (R26-308; H row 12's title no longer held sunflower ~5 s after its relight; no golden moved; the glow's colour-change repaint residue filed R26-324, the cold-vs-played row-12 frame R26-325)
- Owner: junior_developer (LANE B)
- Depends on: T0 for the code; P69 T37c merged for the golden re-pin and the frame read (both write the title goldens,
  and T37c sets the title's own ink that the relight must hand back to)
- Bravos reference: none (a defect).
- Recall: docs_find "relight" -> effects `page_species:relight` ("A bracket or the title already on the page re-fires
  when the sentence retu…"); CAPABILITIES `:213` (T86: "A relight of the title lights every glyph and gives the span its
  token back"). BACKLOG-HISTORY `:914` R26-308.
- Verdict: EXTEND (a fix). The engine's `paintPerform` (`:14487`) RELIGHT loop (`:14525`-`:14532`) has four faults:
  - It does `if (u < 0 || u > 1) continue;`, so a title glyph's `style.color` is written only INSIDE the window.
  - It sets `PS.RELIGHT_COL` while `e > 0.02` (`e = sin(pi u)`, which is above 0.02 until u = 0.9936).
  - It never writes the colour back after the window. The last frame inside therefore keeps the sunflower, and a
    seek past the relight inherits whatever the last painted frame left. The colour is not a function of t.
  - **It paints the LAST retitle's glyphs whatever title stands at t** (review finding 14): `tg = PF.retitles.length ?
    PF.retitles[PF.retitles.length - 1].glyphs : st.titleGlyphs`. Once the colour is written every frame, a relight
    BEFORE a retitle would colour the not-yet-shown glyphs and leave the standing title plain.
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the relight loop only);
  `content/video_engine/tests/test_relight_clears.py` (new, a probe test: `node` renders a title relight at
  `at + dur + 1/24` with and without a preceding play-through, and a relight placed before a retitle). The goldens with
  a title relight are re-pinned by the parent, after P69 T37c's merge.
- Constraints:
  - Every frame, the glyphs of the title STANDING at t are resolved from the retitle chain's own clock (the chain
    `:14534`: `{glyphs: st.titleGlyphs, at: -Infinity}` then each retitle at its `sp.at`; the standing one is the last
    whose `at <= t`), read, not edited. Their colour is written from t: the sunflower where any title relight's
    `e > 0.02`, and otherwise `g.__col || ""`, which keeps T86's span token.
  - The glyphs of a title that is NOT standing at t are never coloured by a relight.
  - The bracket relight's opacity path is unchanged.
- Acceptance:
  1. After a relight ends, the title's glyphs read their own colour on the next frame, whether the frame is reached by
     a seek or by a play-through (same bits both ways).
  2. The same holds for a retitle carrying `color_span` (the span keeps `--lp-neg`).
  3. A relight before a retitle lights the standing title and leaves the later retitle's glyphs uncoloured.
  4. Every page with no title relight is byte-identical.
- Stop conditions: another painter writes the title glyphs' `style.color` after `paintPerform` in the same frame
  (report the order; do not reorder `render()`). P69 T37c changes how the title's ink is written (`style.color` vs a
  CSS token): re-brief on T37c's merged code.
- Regression: `python -m pytest content/video_engine/tests/test_relight_clears.py -q`
- Expected RED: a seek to `at + dur + 1/24` after painting `at + dur - 1/24` reports the glyph's `style.color` as
  `rgb(245, 183, 46)` (`PS.RELIGHT_COL` `#F5B72E`, `:13041`, as the DOM reads it back) instead of the title's own.
- Validate: `python -m pytest content/video_engine/tests/test_relight_clears.py -q` then `python -m pytest content/video_engine/tests/test_retitle_color.py -q` then COMMON-TAIL
- Frame acceptance: every H row with a title relight, at its `at + dur` and one frame after, before and after
  (`$SP/p71-t2/frames/`), read on P69 T37c's merged title.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T3: A plain recast on the default clock never stands a half-written tick on an empty plot (R26-310)
- Status: done - lane B `e6aaa30` (R26-310; option 1: arriving labels written by 0.75, whole over an empty plot; 45-66 fragments per recast -> 0 on H's six plain recasts; the covering panel is T3b)
- Owner: implementation_luna (LANE B)
- Depends on: T0
- Bravos reference: Bravos builds inside a held frame, and its axes never show a fragment (46 §46.7; CAPABILITIES
  `:119`). For parity: HIS `Jw8ykhoOVBQ` 11:01 (BRAVOS-FRAME `-ss 661`), a recast-free held axis.
- Recall: docs_find "recast ticks" -> CAPABILITIES `:77`, `:90`, `:229`. The mechanism is E64's axis hand-over (engine
  `:15442` comment: "the target's labels write themselves on over the back half of the same clock").
  BACKLOG-HISTORY `:916` R26-310: "for ~0.3 s a half-written tick ("16", "320") stands on an empty plot. An engine
  option: write the arriving ticks before the midpoint, or fade them in".
- Verdict: EXTEND (a fix), **on the DEFAULT clock, not the landscape-phone path** (review finding 1, re-verified at
  `50b2f85`):
  - `lpPaintStates` (`:15935`) derives `fedPlainRecast` (`:15979`-`:15980`), which is true ONLY when the from-state's
    readability is `LP_READABILITY.LANDSCAPE_PHONE`. Its plain-recast call (`:16000`) passes it as `lpAxisHandOver`'s
    5th parameter `plain`, so a non-phone unkeyed recast calls `lpAxisHandOver(from, to, plain.u, undefined, false)`.
  - With `plain` false, `lpAxisHandOver` (`:15457`) takes the default clock: the arriving labels write from
    `inn = clamp01((pu - AXIS_HAND.IN) / (1 - AXIS_HAND.IN))` (`:15474`; `IN` 0.35, `:15447`) through `sweep`'s
    per-label share `clamp01((w * (n + 1) - i) / 1.6)`, with no `lineGone` gate. Meanwhile the leaving state un-draws
    (`lpPaintChart` on `cCur = 1 - segEase(u)`) and the arriving state's data waits for its own build after the
    clock. So between pu 0.35 and the end, the arriving ticks are PART-written over a plot whose data ink is going or
    gone.
  - The H door's row 22 is this case: its page is `;readability=longform` (lane A `build_episode_h.py:1904`, `LONGFORM`
    `:549`) and the flip is `"to": "recast", "keyed": False` (`:2924`), so it runs the default clock.
  - The landscape-phone path (`PLAIN_AXIS_HANDOFF` 0.90, `lineGone`, `:15448`-`:15467`) is NOT the defect's path and is
    not changed; `test_fed_axis_handoff.py` guards it.
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`lpAxisHandOver`; `lpPaintStates`'
  plain-recast call line `:16000` and the flag derived beside it `:15979`-`:15980`, so the default-clock plain recast is
  distinguishable from the keyed / rescale / morph callers; `AXIS_HAND` or a new named dial with a `[DERIVED: ...]`
  tag); `content/video_engine/tests/test_recast_axis_whole.py` (new). The goldens that plain-recast are re-pinned by the
  parent.
- Constraints:
  - The fix is the backlog's first option, on the default clock: on an UNKEYED plain recast (non-phone), an arriving
    label is written WHOLE before the plot is empty - its write completes by the time the from-state's paths are fully
    un-drawn (the same `stroke-dashoffset >= 0.995 len` test the phone path's `lineGone` uses), so no part-written tick
    stands over an empty plot. The second option (the arriving labels fade in whole) is rendered beside it for the
    parent's pick on the frame.
  - The keyed, rescale and morph callers (`:15565`, `:15637`, `:15836`, `:15908`, all `plain` absent) keep their clock
    byte-for-byte, and so does the landscape-phone plain path.
  - **The H door's plain recasts move on purpose, and are listed as expected changed instants:** GDP_RECAST (`:2573`),
    DIV_RECAST (`:2578`), YARD_RECAST (`:2621`), IG_RECAST and CAPEX_RECAST (`:2698`-`:2700`), TRIM (`:2921`) and the
    flip (`:2924`) - every `chart_to recast` the door compiles without a key (lane A `build_episode_h.py`, committed at
    `910ddd6`; the file is dirty in lane A, so the slice re-reads the rows off the compiled timeline).
- Acceptance:
  1. At row 22's flip (the take's `the flip` 663.02-663.80), over every frame of the recast, no arriving tick label
     stands partly written while the plot's data ink is zero (measured by the probe: label `textContent` length vs
     `__full`, against the from-state's and the to-state's stroke dash states).
  2. The same holds at each listed H plain recast; their before / after pairs are in `$SP/p71-t3/frames/`.
  3. Both options are rendered as one strip for the parent.
  4. Every page with no plain recast, every keyed / rescale / morph recast and every landscape-phone recast is
     byte-identical (`test_fed_axis_handoff.py` unchanged and green).
- Stop conditions: the half-written tick comes from a caller other than `lpAxisHandOver` (report it by name).
- Regression: `python -m pytest content/video_engine/tests/test_recast_axis_whole.py -q`
- Expected RED (re-derived on the longform clock, predicted from `:15474` and the call at `:16000`; the probe logs the
  real window in step 1): on a `;readability=longform` page with an unkeyed `chart_to recast`, at some recast `pu` in
  about [0.35, 0.7], an arriving tick's `textContent` is a strict prefix of its `__full` while every from-state path's
  `stroke-dashoffset` is at or over 0.995 of its length and no to-state path has begun.
- Validate: `python -m pytest content/video_engine/tests/test_recast_axis_whole.py -q` then `python -m pytest content/video_engine/tests/test_chart_transitions.py -q` then `python -m pytest content/video_engine/tests/test_fed_axis_handoff.py -q` then COMMON-TAIL
- Frame acceptance: H 662.8, 663.0, 663.2, 663.4 and 663.8 s, before and after (both options), beside the parent's
  row-22 frame that found it.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T3b: A long-form plain recast carries the world it leaves - the target panel waits for the leaving data to un-draw; leaving labels leave whole over an empty plot (found by T3)
- Status: done - lane B a4bb9e1 (old data never under the new axis)
- Owner: implementation_luna (LANE B)
- Depends on: T3
- Harvest: T3's frame read (`$SP/p71-t3/frames/sheet-flip.png`): on every long-form page the target state's opaque `rect.lp-panel` covers the leaving chart from the recast's FIRST frame (checked with `elementsFromPoint`), so at H 663.20 the bars vanish in one frame and the plot stands empty ~0.6 s; the leaving un-draw is never seen; the leaving labels still un-write letter by letter over the empty plot. The parent's ruling from the record: E99 s74 (a transition carries the world it leaves), E21 (never still), M47 (the empty plot).
- Write set: `lpAxisHandOver` and the plain-recast call site T3 owns, plus the minimum that times the target panel's reveal; tests beside `tests/test_recast_axis_whole.py`.
- Acceptance: (1) no frame where the leaving data is covered before it has un-drawn (bars flat / lines undrawn per `lpPlotEmpty`), then the panel comes up; (2) leaving labels leave whole over an empty plot, mirroring `PLAIN_AXIS_WRITE_END`; (3) row 22's flip and the five other plain recasts probed at 96 fps: 0 half-written labels leaving or arriving, M47 measured before/after with numbers; whether row 22's door workaround becomes unnecessary is stated; (4) door identity outside the six recast windows; goldens unchanged unless named.
- Validate: `test_recast_axis_whole`, `test_chart_transitions`, `test_fed_axis_handoff`, `test_longform_profile`, `test_golden_frames`, each in its own process.
- Red evidence: pending
- Green evidence: pending
- Evidence: pending

### T4: The second melt throws the page on screen, not a stale snapshot (R26-312)
- Deviation (review MERGE, 2026-09-24): the write set includes `species/melt.mjs` (the synced source of `meltMount` / `paintMelt` / `clearMelt`; editing the engine alone fails `sync_kinetics --check`). "Pure in t" is met on the DOM for still pages, not byte-for-byte (the clone captures the live idle - pre-existing, R26-321); `melt:morph`'s one-frame stale ring filed R26-322.
- Status: done - lane B `7789afa` (R26-312; the mount keyed per boundary; H's melts at 104.31 / 242.38 / 303.54 throw the page on screen; reviewed MERGE; no golden moved)
- Owner: implementation_luna (LANE B), then reviewer (a transition carries the world it leaves, s74)
- Depends on: T0
- Bravos reference: none (a defect).
- Recall: docs_find "melt snapshot" -> 1 hit; CAPABILITIES `:38` (the melt, E88: "the INK is a clone of the outgoing
  world with its board hidden (`.meltink`)"). BACKLOG-HISTORY `:918` R26-312: "the page that melts and is thrown for
  ~0.45 s is row 14's "The railways took half" bars page, not the yields page on screen - a stale snapshot; the first
  melt at 195.82 is correct".
- Verdict: EXTEND (a fix), diagnosis first. The code offers a precise hypothesis:
  - `meltMount` (`:5292`) is "mounted ONCE and kept on wA.__melt ... read once, from the page as it stands at the
    boundary".
  - `paintMelt` (`:5345`-`:5347`) REUSES `wA.__melt` whenever its svg is still connected.
  - The only reset is `render()`'s `else if (wA.__melt) clearMelt(wA)` (`:20677`), on a frame with no melt; `meltOn`
    is computed at `render()`'s top level (`:20444`), so on a play-through every melt-free frame clears it (the
    reviewer confirmed the hypothesis; the stale clone needs a seek from one melt straight to another).
  - The first melt (195.82) throws the page on screen then, and that page is row 14's bars page (the take:
    `took roughly half` 185.75-186.69).
  - If no melt-free frame is painted on the same `wA` between the two melts (a seek, a probe capture, or a world pair
    that does not alternate), the second melt reuses the first one's clone.
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`meltMount`, the reuse lines in
  `paintMelt`, `clearMelt`; `render()`'s melt call site only if the diagnosis puts the fault there - otherwise stop);
  `content/video_engine/tests/test_melt_snapshot_is_current.py` (new).
- Constraints:
  - A mount is keyed to the scene it melts (a `sceneId` / `span[0]` stamp on `wA.__melt`). A key that differs from the
    frame's outgoing scene is cleared and re-mounted.
  - Pure in t: the same bits for a seek to 242.30 and for a play-through from 195.
  - The first melt is byte-identical.
- Acceptance:
  1. **Diagnosis, logged before any change:** reproduce with a play-through capture of 241.90-242.60 and with a cold
     seek to each instant, and write which DOM the clone reads (`$SP/p71-t4/logs/diagnosis.md`).
  2. After the fix, the ink thrown at 242.10, 242.30 and 242.45 is the yields page's, matched against the page's own
     frame at 241.90.
  3. Every other melt golden is byte-identical.
- Stop conditions: the stale page comes from the `wA` / `wB` assignment in `render()` rather than from the cache (stop:
  `render()` is contended with P70 T8 / T9, and the parent sequences it); the first melt changes.
- Regression: `python -m pytest content/video_engine/tests/test_melt_snapshot_is_current.py -q`
- Expected RED: two melts on one world element with no melt-free frame painted between them. The second melt's
  `.meltink` clone contains the FIRST page's title text.
- Validate: `python -m pytest content/video_engine/tests/test_melt_snapshot_is_current.py -q` then `node --test content/video_engine/tests/kinetics/melt.test.mjs` then COMMON-TAIL
- Frame acceptance: H 241.90, 242.10, 242.30, 242.45 and 242.60 s, before and after, beside `$SP/p69-m47/melt/M-tiles.png`
  (d-f) and the first melt at 195.82.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T5: A stamped chip's seal is reserved - OTHER elements on its beat go round it; the stamp stays where it lands, over the chart (R26-313; E99 s128)
- Status: done - lane B 3d6e8e5 (the seal reserved; legibility-first placement, words > ink > seals)
- Owner: junior_developer (LANE B), then reviewer (the stamp's room law, s128)
- Depends on: P70 T1c committed (it edits the stamp ring's ink beside the compiler's chip fit, and T5's frame read must
  show T1c's gold shockwave, s127 (2)); P70 T1b is committed at `50b2f85` (the seal, `seal_r`)
- Bravos reference: none (a placement defect). The law is P69 T5's (E99 s88, "the stamp takes the room first"), read
  through s128.
- Recall: docs_find "reserved box" -> CAPABILITIES `:77`, `:79`; lane A CAPABILITIES "The stamp takes the room first"
  (P69 T5: "`row_stamp_fits` fits a row's stamps first, in row order, each against the earlier stamps' fitted box").
  BACKLOG-HISTORY `:919` R26-313. E99 s128 (`OPERATOR-RULINGS.md:3387`) names this slice as its carrier: "a stamped
  chip's reserved box keeps OTHER elements from landing under it on the same beat; it does not keep the stamp off the
  chart".
- Verdict: EXTEND (re-verified at `50b2f85`).
  - `row_stamp_fits` (`:8942`) and `stamp_reserved_box` (`:8932`) reserve stamped DOCKS only.
  - The stamped chip is fitted by `chip_stamp_ring_fit` (`:8335`, P70 T1 / T1b; its seal radius is `seal_r`,
    `chip_stamp_seal_r` `:8132`) in `main()` (`:10694`-`:10706`) against the newsreel boxes plus the row's DOCK
    `stamp_boxes`, but its own box is never added to `stamp_boxes`: a later stamped chip does not see an earlier one,
    and `dock_place(..., clear_of=stamp_boxes)` (`:10707`) and `page_place` (`:7223`) do not see it either. A card over
    a dock stamp is already a WARN (`stamp_clash_error`, `:10773`, T26d).
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (the chip-stamp loop in `main()` adds each
  fitted chip's reserved box to `stamp_boxes` in row order; `stamp_reserved_box` if a chip needs its own box shape);
  `content/video_engine/tests/test_chip_stamp_reserved.py` (new).
- Constraints:
  - A stamped chip (`chip_is_stamped`, `:8251`: `form: "stamp"` and `arrive: "stamp"`) enters the row's stamp order at
    its `at`. Its reserved box is the seal (`seal_r`) plus the ring's peak.
  - **s128 (1): the reservation is for OTHER elements only.** A later stamp, a placed card or a dock on the same beat
    goes round the reserved box (or WARNs with its numbers where no room exists, s106). The stamped chip ITSELF is
    never moved, shrunk, filled or refused because it overlaps the chart's data or a line: T5 adds no chart ink, data
    mask or plot box to the chip's own obstacles, and the chip's fitted place, `ring_to`, `from_to` and `seal_r` are
    byte-identical to today's for the first chip of a row.
  - A glyph chip reserves nothing (its law is the badge spring).
  - s106: a card over a reserved box is REPORTED, not refused (T26d's rule).
- Acceptance:
  1. A row with a stamped chip and a later stamped dock: the dock's fitted box overlaps the chip's reserved box by 0 px.
  2. A row with a stamped chip and a card placed by `dock_place`: 0 px, or a WARN with its numbers where no room
     exists.
  3. A row with two stamped chips: the second fits clear of the first's reserved box, or WARNs with its numbers.
  4. A stamped chip whose seal lands over a drawn line keeps its authored place and size exactly (a test compares the
     fit with and without the line), and the chart shows through the open seal (P70 T1c's assertion, re-run).
  5. A row with no stamped chip compiles byte-identically, and so does the H door.
- Stop conditions: the chip's fitted box is not recorded on the species at compile time (report: that is P70 T1's
  contract); keeping a later element clear would need to move the stamp itself (stop: s128 forbids it; report the
  numbers).
- Regression: `python -m pytest content/video_engine/tests/test_chip_stamp_reserved.py -q`
- Expected RED: a second stamped chip in the same row gets a fit that overlaps the first chip's seal-plus-ring box
  (overlap area > 0), because `chip_stamp_ring_fit` is handed only the dock `stamp_boxes` (`:10701`).
- Validate: `python -m pytest content/video_engine/tests/test_chip_stamp_reserved.py -q` then `python -m pytest content/video_engine/tests/test_chip_stamp_arrival.py -q` then `python -m pytest content/video_engine/tests/test_stamp_is_a_seal.py -q` then `python -m pytest content/video_engine/tests/test_prop_free_placement.py -q` then `python -m pytest content/video_engine/tests/test_the_stamp_arrival.py -q` then COMMON-TAIL
- Frame acceptance: a private test-bed beat on H row 7 (`nvidia` 58.60-59.60): the stamped NVIDIA chip over the page's
  line, then a second stamped chip on the next word and a card on the same beat. The parent reads the frame at contact
  + 0.30 s for both chips, on P70 T1c's gold shockwave: the first seal open over the line and unmoved, the others clear
  of it.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T6: A prop's authored exit near its page's end is honoured, or refused with its numbers (R26-309)
- Status: done - lane B 43363ea: the engine's boundary snap skips `dockOwnsExit` docks (stamped marks, props); `swept` holds; cards unchanged; no refusal needed (s106); the reviewer's read runs post-commit
- Owner: implementation_luna (LANE B), then reviewer
- Depends on: P70 T8 and T9 committed (both own `render()` hunks); T15 (the same dock branch in wave 4: its hover lines
  sit beside the exit)
- Bravos reference: none (a defect).
- Recall: docs_find "reserved box" / "prop" -> CAPABILITIES `:79` (the stamp's exit: "`exitAtInFrames`, ease-IN cubic
  over STAMP.EXIT_S"). BACKLOG-HISTORY `:915` R26-309: "Row 22's RAM prop, given an exit 0.3 s or 1.0 s before its
  page's slide, stood on through the slide; only an exit 2.5 s early left".
- Verdict: EXTEND (a fix). **The stub is too thin to plan a fix**, because no root cause is on disk. This is a bounded
  discovery first. The candidates, read from the code:
  - `render()`'s dock loop takes the retract only for a non-stamped dock (`:20849`,
    `const rk = !stamped && t > d.exit ? ...`). A stamped prop exits on `stampExit`'s own curve (`ex`, the next line).
  - `scene_exit` (`:4090`; called `:10929`) or the slide's hand-over may hold docks across the boundary.
  - The compiler's prop `moves` (T26d) or the fit may re-time `exit`.
- Write set: diagnosis `$SP/p71-t6/logs/diagnosis.md` (first). Then either `docs/content-video-engine/samples/scene-evidence-engine.mjs`
  (`render()`'s dock exit only) or `content/video_engine/scripts/build_scene_timeline_f.py` (the exit's resolution),
  never both without the parent's word. `content/video_engine/tests/test_prop_exit_near_page_end.py` (new).
- Constraints:
  - An authored exit is honoured to the frame, or refused BY NAME with its numbers (the exit, the page's end, the
    owed exit curve's length). s106: a silent re-time is neither advice nor refusal.
  - Every dock whose exit already leaves is byte-identical.
- Acceptance:
  1. The diagnosis names the line that keeps the prop, with a failing instant.
  2. Row 22's RAM prop with an exit 0.3 s and 1.0 s before the slide: it is gone by its exit plus its owed curve at
     every sampled frame, or the compile prints the refusal.
  3. The H door is identical except that row.
- Stop conditions: the cause is in the slide transition's world swap (report; the parent sequences it against P70
  T9's `paintChapters` call and T4's melt call site).
- Regression: `python -m pytest content/video_engine/tests/test_prop_exit_near_page_end.py -q`
- Expected RED: a stamped prop dock with `exit = page_end - 0.3` still has visible opacity at `page_end - 0.05`.
- Validate: `python -m pytest content/video_engine/tests/test_prop_exit_near_page_end.py -q` then `python -m pytest content/video_engine/tests/test_the_stamp_arrival.py -q` then COMMON-TAIL
- Frame acceptance: row 22's RAM prop at its exit, exit + 0.27 s and the page's slide start, for exits of 0.3 s, 1.0 s
  and 2.5 s early (`$SP/p71-t6/frames/`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T7: The squint gate - a held page and its caption, shrunk to thumbnail width, still say what they are about; M48 FAILs (P69 T88, the gate; E99 s120, s126)
- Amended by E99 s129 (2026-09-25): words on the plot is INFO, never a FAIL; axis ticks and axis titles are not counted; M48 FAILs on lit share, title size, named-series size and caption size / contrast only.
- Status: done - lane B a469501 (M48 the squint gate, FAIL)
- Owner: implementation_luna (LANE B), then reviewer (a new BLOCKING gate row)
- Depends on: T0; P69 T37c merged (review finding 5: T37c writes `measure_line_bloom.py` and
  `bravos-line-bloom.v1.json` too; T7 sequences after it and extends its merged file). T37b is done (`557e1dc`:
  `measure_line_bloom.py` carries the squint read).
- Bravos reference: the band `content/video_engine/assets/bravos-line-bloom.v1.json` `band_1024` is already MEASURED off
  Bravos, which E38 requires:
  - its five frames are `jpn-0520`, `jpn-0523`, `ai-builders`, `kospi-index`, `kospi-retail`;
  - `lit_share` 0.572-0.743, `title_cap_px` 5.0, `label_cap_px` 2.5-3.44, `plot_words` 0-7 (n=3).
  - s120 asks for "the T37 sheet's JPN 05:20 / 05:23.5 + three more Bravos line pages". Two of the five are JPN, but n
    is 3 at 1024 px. The slice first extends the band to n >= 5 from the same five frames at 1024 px, or reports why a
    frame cannot be read.
- Recall: docs_find "squint" -> 0 hits (the layers are stale); docs_find "thumbnail" -> CAPABILITIES `:35` (E67, "THE
  CHART IS THE THUMBNAIL"); docs_find "caption strip" -> CAPABILITIES `:23` (the 16:9 caption strip, R26-205 / E99
  s82), `:25` (the caption moves under a card, E62). The code: `measure_line_bloom.py` `SQUINT_W = 320` (`:49`),
  `cap_height()` (`:195`), `ocr_words()` (`:212`), `squint()` (`:229`), `measure()` (`:243`), the `--band ... --check`
  mode (`check_band` `:319`); no caption read exists.
- Verdict: REUSE (the measurement) + NEW (a gate row that FAILs, and its caption scope).
  - **Which gate:** `gate_motion_density.py`, not `gate_one_shot_floor.py`. The squint read is PER HELD PAGE and PER
    CAPTION, off rendered frames, and belongs with M18 / M25 / M32 / M43, which read a probe file beside the timeline
    and are INFO until it exists (`load_layout` `:2373`, `_layout_gate` `:2638`). The floor gate holds whole-cut
    aggregates (M35-M46).
  - The next free id is **M48** (free repo-wide, the reviewer checked): the motion gate's highest is M47 (T87) and the
    floor gate's is M46.
  - **The level is FAIL (E99 s126 (1), `OPERATOR-RULINGS.md:3383`):** "M48 FAILs a cut whose page, rendered to thumbnail
    width, loses its focus or the words its story needs, at thresholds measured off Bravos first (E38; s120); it ships
    as FAIL, not WARN-first". Draft 1's "WARN first, FAIL on the operator's word" was P69 T88's acceptance wording
    (P69 plan `:1145`), misattributed to s120 (review finding 11); s120 (`:3371`) says only "it becomes a gate row", and
    s126 now sets the level.
  - **The scope includes the captions (s126 (2)):** "a caption page (the long-form strip and the shorts' strip) that
    does not read at the small size fails the same gate, at a floor measured off the reference, not fitted to ours".
- **Step (0b), a bounded discovery - the caption floor's reference.** Find reference frames on disk that carry a
  burned-in caption strip: for the long-form strip, the Bravos frames (the band's five and the D40 / HIS / STK / DOM /
  JPN videos under the main checkout); for the shorts' strip, the reference analyses under the main checkout's
  `content/video_engine/sources/reference_analyses/` that carry 9:16 frames with captions. Measure, at the gate's
  width, each caption's cap height in px and its text-to-ground luminance contrast, and write the floor (min, n, the
  frames) to a NEW `content/video_engine/assets/caption-squint-floor.v1.json` (separate from T37c's band file). The
  thumbnail width is read from the doctrine first (E67 Apply 4 names 320 px for a page; `docs_find "shorts thumbnail"`
  for the 9:16 strip); if none is ruled for 9:16, 320 px wide with a `[DERIVED: ...]` tag. Stop: no reference frame
  with a caption strip is on disk for a lane - that lane's caption row reports INFO "no reference floor measured"
  (never a floor fitted to ours, E38) and the slice files a research-lane frame order for it; the page row ships
  regardless.
- Write set: `content/video_engine/scripts/measure_line_bloom.py` (a new `--build <dir>` mode: each held ledger page's
  settled frame and each caption's settled frame, rendered by the frozen-frames capture path, measured at the gate's
  width and written to `<build>/squint.json` as `pages` and `captions`; a caption cap-height / contrast read);
  `content/video_engine/scripts/gate_motion_density.py` (new `load_squint`, `_squint_gate` M48, `run(..., squint=...)`,
  its SRC line and docstring row); `content/video_engine/assets/bravos-line-bloom.v1.json` (the band at n >= 5, if
  extended, on T37c's merged file); `content/video_engine/assets/caption-squint-floor.v1.json` (new);
  `content/video_engine/tests/test_squint_gate.py` (new); `docs/GATES-REGISTRY.md` (regenerated by the parent).
- Constraints:
  - Thresholds come from the reference only (E38): the page band off Bravos, the caption floor off the reference
    frames of step (0b); never fitted to ours.
  - **FAIL, not WARN** (s126 (1)): a measured page or caption outside its band FAILs with its numbers and the gate
    exits non-zero.
  - INFO when `squint.json` is absent, or a lane's caption floor is unmeasured (step 0b's stop); an INFO row names the
    command that measures it.
  - Per page, the gate reads the lit share, the title and named-label cap heights at the gate's width, and the plot
    word count. Per caption, the cap height and the contrast against the floor.
- Acceptance:
  1. M48 FAILs, with its numbers, a held page whose lit share, cap heights or word count falls outside the band, and a
     caption whose cap height or contrast falls under the floor. It PASSes a page and a caption inside.
  2. INFO with no file.
  3. The solo golden, the H divergence page (`ev-divergence-v1`, rows 1 and 4), H rows 9 and 15, and the H long-form
     caption strip at those instants are measured; one 9:16 caption strip (the approved Japan tariff short's build, if
     its build dir is on disk, else a golden 9:16 caption frame) is measured.
  4. A shrunk sheet is written: ours (pages and captions) beside the five Bravos frames and the step-(0b) caption
     reference frames, all at the gate's width.
  5. The committed H door's current M48 verdict is recorded (it is expected to FAIL on rows 1 and 4's word count; T8
     is the carrier that fixes it).
- Stop conditions: the frozen-frames capture cannot render a page's or a caption's settled instant (report; do not add
  a browser path to the gate itself).
- Regression: `python -m pytest content/video_engine/tests/test_squint_gate.py -q`
- Expected RED: `gate_motion_density` has no M48 row (the `Gate("M4..."` ids are M43, M44, M47), so a probe
  `squint.json` with an out-of-band page and an under-floor caption produces no M48 line.
- Validate: `python -m pytest content/video_engine/tests/test_squint_gate.py -q` then `python -m pytest content/video_engine/tests/test_line_bloom.py -q` then `python -m pytest content/video_engine/tests/test_gate_motion_density.py -q` then `python content/video_engine/scripts/measure_line_bloom.py --band content/video_engine/assets/bravos-line-bloom.v1.json --check`
- Frame acceptance: the parent reads the shrunk sheet (`$SP/p71-t7/frames/squint-sheet.png`): the solo golden, H rows 1,
  4, 9 and 15 with their captions, one 9:16 caption strip, the five Bravos frames and the caption reference frames, all
  at the gate's width.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T8: The H label diet - the divergence page's end tags are a name, not a name plus a sub-label (P69 T88, lane A; E99 s120 (3), s126)
- Status: DROPPED (E99 s129, the operator 2026-09-25: "agreed, drop T8" - the plot-word limit it served is no longer a gate)
- Owner: implementation_luna (LANE A; lane B only if step (0) picks the engine route)
- Depends on: T7 merged into LANE A before T8 starts (lane A at `910ddd6` has neither M48 nor `--build`; review finding
  10); lane A's in-flight door work committed (`build_episode_h.py` is dirty in lane A at this revision); P70 T2 if the
  lane-B route is taken (it owns `buildLedgerLine`'s end-tag writes)
- Bravos reference: JPN `nB1eXWQlW58` 05:20 (BRAVOS-FRAME `-ss 320`), whose end tags are short names.
- Recall and the premise, corrected (review finding 2, verified at lane A `910ddd6` and lane B `50b2f85`):
  - Rows 1 and 4 draw the COMMITTED object directly: `OPEN_PAGE = "ev-divergence-v1"` and
    `LAYER_PAGE = "ev-divergence-v1"` (`build_episode_h.py:217`-`:218`). The derived `HOOK_OBJECT_ID =
    "ev-divergence-hook-v1"` (`:393`) is the source of the two-line CHART CARD only; `_hook_object()` (`:3257`-`:3270`)
    DROPS the memory series and its badge. Shortening it changes neither end tag rows 1 and 4 write.
  - `ev-divergence-v1.series.json` carries the LONG names in `series[].name` ("MEMORY MAKERS (hynix+Micron)",
    "SEMICONDUCTOR STOCKS", "MEGA-CAP TECH STOCKS", "S&P 500 (the market)") and the SHORT names in `badges[].label`
    ("MEMORY MAKERS", "SEMICONDUCTORS", "MEGA-CAP TECH", "S&P 500"), each badge with a `tag` ("our layer", "their
    divergence", "matches the market", "the market"); its `names_note` records the operator's 2026-09-03 correction.
  - What an end tag writes (engine `buildLedgerLine`, `:11086`; the tag write near `:11254`-`:11259`): in the longform
    `full` form, the value, then `series.name`, then a chip carrying the inline badge's `tag` (or a card's
    `card_name`); in `badge` form the value and the chip; in `value` form the value alone. `ledger_page.apply_longform`
    (`:3217`) picks the fullest form that fits (`longform_tag_form`, `:3195`; `LONGFORM_TAG_FORMS` `:3007`).
  - The key rail (`ledger_page.longform_key`, `:3044`) writes `series[].name` - the long name - and appears only when
    the end tags gave up their names (`tag_form` badge or value). So "the parentheticals go to the key rail" holds only
    for a non-`full` tag form; `badges_for` (`:2252`) feeds the inline chips, not the rail.
- Verdict: a bounded discovery, then one of two mechanisms.
  - **Step (0):** read the compiled rows 1 and 4 off the H build's timeline and the rendered page at their settled
    instants: the `tag_form` each gets, each end tag's text (value, name, chip), and the plot word count M48 reads.
    Log it to `$SP/p71-t8/logs/end-tags.md`.
  - **Route A (lane A, REUSE; preferred when it suffices):** a derived PAGE object on `_hook_object`'s pattern (every
    number copied, none typed), written to `build-h/objects/` as `ev-divergence-page-v1`, with `OPEN_PAGE` /
    `LAYER_PAGE` pointed at it. It carries the four badges' own short labels as the end tags' names and drops the
    chip's `tag` words from the plot, while the key rail keeps the full names (a `tag_form` that gives the names to the
    rail, or the full names kept in `name` with the short ones where the tag reads them - whichever the engine already
    supports, per step (0)).
  - **Route B (lane B, EXTEND):** if no existing field lets the end tag write a short name while the rail keeps the
    long one, a series key for the end tag's short name (read by `buildLedgerLine`'s tag write; the rail keeps
    `name`), validated in `ledger_page`; then Route A points the door at it. This is an engine slice after P70 T2.
  - **All four tags** take the operator-corrected badge labels (MEMORY MAKERS, SEMICONDUCTORS, MEGA-CAP TECH,
    S&P 500): shortened, never renamed. The committed evidence object is not edited.
- Write set: Route A - `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py` (a new
  `_divergence_page_object()` and `OPEN_PAGE` / `LAYER_PAGE`); `.../SHOT-TABLE-H.md` (a note line). Route B adds, in lane
  B, `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`buildLedgerLine`'s end-tag name write only),
  `content/video_engine/scripts/ledger_page.py` (the key's validation) and `content/video_engine/tests/test_end_tag_short_name.py`
  (new).
- Constraints: the names stay the ones the operator corrected. A shortened name must not collide with another tag
  (s118's ink keeps them apart). The rail, when present, names each series in full.
- Acceptance:
  1. M48 on the H build PASSes rows 1 and 4 (inside the Bravos word band, s126: a FAIL blocks).
  2. The key rail, where the page shows one, still names each series in full; no information the page carried is lost
     (the tags' `tag` words are the ones that go, s120 (3): "a page's secondary labels are the first to go").
  3. Rows 1 and 4 compile differently ON PURPOSE (their page object); every OTHER row of the door compiles and renders
     identically, and rows 1 and 4's changed instants are listed and read.
- Stop conditions: step (0) shows the words over the band come from something other than the end tags (report); the
  key rail cannot carry the full names under the page's profile (report: the diet would lose information, and the
  parent decides).
- Regression: the measure-then-gate PAIR, each in its own process and unpiped: `python content/video_engine/scripts/measure_line_bloom.py --build content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h`
- Expected RED: the gate prints an M48 FAIL line naming rows 1 and 4 with a plot word count over the band's 7
  (predicted: 4 tags, each a name plus a chip, 2-4 words each) and exits non-zero (s126: a FAIL). Without the measure
  step M48 would only print INFO, which is why the regression is the pair.
- Validate: the door, then `python content/video_engine/scripts/measure_line_bloom.py --build content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h`, then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` (unpiped)
- Frame acceptance: rows 1 and 4 at their settled instants, full size and at the gate's width, before and after, beside
  JPN 05:20.
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T8b: The quiet caption reads at the squint - the long form's quiet strip raised to the reference's floor (E99 s126 (2); found by T7)
- Status: pending (after T7 lands)
- Owner: implementation_luna (LANE B)
- Depends on: T7 (M48 and `caption-squint-floor.v1.json`)
- Harvest: T7 ran M48 over the committed H door: 324 of 391 QUIET captions fail - 315 on cap height at 320 px (ours 4.00-4.21 px against Wealth Logic's measured 4.285 floor, n=82 frames) and 61 on contrast (as low as 1.79 against 3.97); the 53 STAGE captions all pass (7.56-8.43 px, contrast >= 6.98). The operator, s126: "we have this issue with our captions too".
- Write set: the caption strip's quiet style (the template CSS / the engine's caption painter - locate by recall), its tests; the caption goldens it moves (on purpose).
- Acceptance: (1) every H quiet caption passes M48's caption floor (size and contrast) at 320 px with numbers; (2) the strip's line breaks and pages are re-checked (the 25-28 character lines, two lines a page - E41; no new orphan lines), and the caption timing is unchanged; (3) the stage captions unchanged; (4) a before/after sheet at full size and at 320 px beside Wealth Logic's strip; (5) goldens that carry a quiet caption re-pinned on purpose, listed.
- Validate: `test_squint_gate`, the caption tests (locate by recall), `test_golden_frames`, each in its own process.
- Red evidence: pending
- Green evidence: pending
- Evidence: pending

### T9: `axis_tag` and the drop guide - the named year becomes an accent pill on the x axis (was P69 T38)
- Status: done - lane B `e96c6f6` (axis_tag + drop guide; two engine defects found and fixed on the test bed: the pop under a recast, the unmeasured label on play-through; golden axis-tag-two-thousand re-pinned on the title-glow engine)
- Owner: implementation_luna (LANE B)
- Depends on: T0. Done: P69 T36 `104af07` (the page-species pattern) and T37b `557e1dc` (the series ink).
- Harvest: v2 A10 "Axis tag: the named year / era / span replaces its tick as an accent pill", n=7 (BUB #14; CHN 39;
  RST 11:00; HIS 05:50 "1843 then 1846 tabs light in sequence"; JPN 01:16, 01:35; DOM 16:00; BOOM (G)). §6 rank 3.
  A42 / A43 are the same pill (P69's carrier map). §9 item 4: "check whether the pill replaces or covers the tick: HIS
  05:50-05:54, JPN 01:14-01:17".
- BOOM evidence (VERIFY.md, true times): A10 CONFIRMED - "2001" 02:23.5, "1929" 02:30, "November 1999"
  13:37.0-13:37.5, "2022" 17:35, "June 2027" 18:00, "3 Years" 00:36; the "November 1999" pill COVERS the 1998-2000
  ticks (the §9 "replaces or covers" check: BOOM covers). A42 drop guides CONFIRMED: the "3 Years" x-guide at
  00:36.0-00:36.5 and the "5x" y-guide at 00:41.0-00:41.5 (`R32_T36_A42_A1/frames/t00m36.5s.jpg`, `t00m41.5s.jpg`).
- Use when (USE-WHEN `:323`): "the sentence names a year or era ("in November of 1999", "the late 1990s")". Don't: "the
  date is not spoken; more than 2-3 tags in one hold".
- Recall: docs_find "axis_tag" -> 2 hits (USE-WHEN `:54`, harvest `:247`), 0 capability rows. docs_find "drop guide" ->
  0 relevant. The nearest built pieces:
  - `species/tippill.mjs` (the pill: `TIPPILL` `PAD_X` 14 / `PAD_Y` 9, `pillBox` `:122`, `leaderEnd` `:71`);
  - the key rail's capsule look (CAPABILITIES "Badges are the key");
  - the dotted leader of the breakthrough capsule (`CAP_LEAD_*`, engine `:5911`-`:5914`);
  - `lpMarkDatum` (`:11425`) and `lpDatumNow` (`:11394`) for the datum on the ACTIVE state.
- Verdict: NEW - a page species module `species/axis_tag.mjs`. It REUSES tippill's pill geometry and the dotted-leader
  law, and resolves on the active state as `span` does (`spanActiveState`).
- Write set:
  - `content/video_engine/scripts/species/axis_tag.mjs` (new; synced as its own region);
  - `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the synced region; a NEW `buildPerform` block + a
    `paintPerform` dispatch line);
  - `content/video_engine/scripts/build_scene_timeline_f.py` (NEW `_validate_axis_tag`);
  - `content/video_engine/effects/cards/page_species.json` (`page_species:axis_tag`; parent-merged);
  - `content/video_engine/tests/kinetics/axis_tag.test.mjs` (new), `content/video_engine/tests/test_axis_tag.py` (new);
  - the golden `axis-tag-two-thousand` (new, in `build_golden_sources.py` / `test_golden_frames.py` /
    `golden/{sources,frames}/`).
- Input evidence: H row 9, "In two thousand the internet crossed seven percent" (take: `two thousand` 79.80-80.49,
  `the internet crossed` 80.49-81.42, `seven percent` 81.42-82.14), on the `ev-equip-ipp-gdp-v1` page (P69 T66's
  cited series).
- Constraints:
  - `{"kind": "axis_tag", at, dur, x: <datum index | x value>, label?, series?, guide?: true}`.
  - The pill replaces the tick's label while it stands (the §9 check decides "replaces" vs "covers" off HIS 05:50 and
    JPN 01:16 before coding; the frame read confirms).
  - The guide drops dashed from the datum to the pill, never across a label (C14).
  - At most 3 tags standing in one hold (the don't): a fourth WARNs with its numbers.
  - A panel may carry it (`LP_PANEL_KINDS`).
- Acceptance:
  1. On its word, the tick springs into an accent pill (tippill's pop) and the guide draws by length to it.
  2. It follows a rescale on the live scale (R26-28's rule).
  3. It leaves with the page.
  4. Refused by name (truth rules): an `x` outside the page's domain, and a date or category that is not one of the
     page's x ticks or data. A tag on a bars page is NOT refused by type (review finding 15; s106, s109 (5)): it binds
     to a bar's category when the sentence names it, and the same truth rule refuses a label no bar carries.
  5. Byte-identical absent the token.
  6. One golden: 2000 tagged on row 9's page at 80.49 + 0.4 s.
- Stop conditions: the x tick labels are not addressable by value on the active state (report; do not re-lay the axis).
- Regression: `python -m pytest content/video_engine/tests/test_axis_tag.py -q`
- Expected RED: `axis_tag` is refused as an unknown species kind by `build_scene_timeline_f._validate_entry`.
- Validate: `python -m pytest content/video_engine/tests/test_axis_tag.py -q` then `node --test content/video_engine/tests/kinetics/axis_tag.test.mjs` then `python content/video_engine/scripts/measure_page_boxes.py --check` then `python -m pytest -q content/video_engine/tests/test_page_boxes.py` then COMMON-TAIL
- Frame acceptance: `axis-tag-two-thousand.png`, and a strip at 80.49 / 80.70 / 80.89 / 81.42 s, beside HIS 05:50 and
  05:52 (BRAVOS-FRAME `-ss 350`, `-ss 352`) and JPN 01:16 (`-ss 76`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T10: `level_join` - a dashed rule from one datum to another, a ring at each end, the gap written off the rule (was P69 T39)
- Status: done - lane B `04ee3cd` (level_join; golden on row 14's dot-com-to-today join, '+5 pts'; the long-form figure sized as an end-tag peer and nudged inside the plot frame; merged beside T9's named blocks)
- Owner: implementation_luna (LANE B)
- Depends on: T0
- Harvest: v2 A9 "Dashed LEVEL rule drawn from one datum to another", n=5 (BUB 2:48; RST 7:00; DOM 00:50 "from the
  endpoint to a "4%" pill"; BOOM 00:41 (G); D40 11:50 (G)). §6 rank 4. C14: the label never on the rule.
- BOOM evidence (VERIFY.md): the "5x" level pill sits ON the dashed rule by the axis at 00:41.0 (compare C14, "the
  label never on the rule"); ours keeps C14 - the label is written beside the rule - and the frame read notes the
  difference.
- Use when (USE-WHEN `:883`): ""higher than at the depth of 2008": the rule joins the two data". Don't: "put the label
  on the rule (C14)".
- Recall: docs_find "level_join" -> USE-WHEN `:54`, `:869`, harvest v1 `:198`; 0 capability rows. Built pieces:
  - `axes.hlines` (`ledger_page.AXES_KEYS` `:111`: static and full-width, harvest `:101`);
  - `bracket` (CAPABILITIES `:77`: "a measured vertical span between two data");
  - the dashed `ring` (`species/ring.mjs` `ringDashes` `:117`);
  - `lpDatumNow` for both anchors on the active state.
- Verdict: NEW - a page species `species/level_join.mjs`. It REUSES the ring's dash law for the rule and the end
  rings, and the bracket's label placement (off the rule).
- Write set: `content/video_engine/scripts/species/level_join.mjs` (new); the engine (the synced region, a NEW
  `buildPerform` block + dispatch line); `build_scene_timeline_f.py` (NEW `_validate_level_join`); `page_species.json`
  (card; parent-merged); `tests/kinetics/level_join.test.mjs` (new), `tests/test_level_join.py` (new); the golden
  `level-join-half-a-point` (new).
- Input evidence: H row 15, "five and a half" (take 225.21-226.49 is the earliest of three; the brief names the row-15
  beat), on the rate page the row draws. Where the page's datum is not the spoken level, the golden uses row 14's 28¢
  (`twenty-eight` 180.93-181.62) against rail's 50¢ (`took roughly half` 185.75-186.69).
- Constraints:
  - `{"kind": "level_join", at, dur, from: datum, to: datum | {y}, label, series?}`.
  - The rule is horizontal at `from`'s value and runs to `to`'s x; a ring lands at each end (dashed, the ring's law).
  - The figure is written beside the rule, never on it (C14): the engine places it off the rule by construction, and
    an authored placement that puts it on the rule is a placement WARN with its numbers (s106).
  - The gap figure is COMPUTED from the two data and refused when the written label disagrees (a truth rule: E28 / s109).
- Acceptance:
  1. The rule draws by length on its word, the end rings land, and the label writes.
  2. It follows a rescale.
  3. Refused by name: a `to` on another unit's series, or a label that contradicts the computed gap.
  4. Byte-identical absent the token.
  5. One golden: the frame at the label's write end.
- Stop conditions: the two anchors cannot both be read on a panel (report; ship the single-chart form).
- Regression: `python -m pytest content/video_engine/tests/test_level_join.py -q`
- Expected RED: `level_join` is refused as an unknown species kind.
- Validate: `python -m pytest content/video_engine/tests/test_level_join.py -q` then `node --test content/video_engine/tests/kinetics/level_join.test.mjs` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden, and a strip over the beat's word, beside DOM 00:50 (BRAVOS-FRAME `-ss 50`) and BUB 2:48
  (`frame_0015.jpg`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T11: `loop` - a flow laid as a ring, money moving on its arrows (was P69 T43)
- Status: done - lane B `95e3da8` (ring layout + tokens; token look from the parent's frame read; `TOKEN_MIN_CROSS_S` 0.49 s DERIVED from Bravos DOM 03:27 - the parent's 1.0 s request was withdrawn as not from the reference; golden flow-loop-tokens)
- Owner: implementation_luna (LANE B)
- Depends on: T0
- Harvest: v2 T21 "Circular loop / flywheel", n=3 (BUB 11:22; RST 9:30; BOOM (G)): "`flowLayout` is a row or a column
  only". A27 "Money tokens travel the edges", n=4 (BUB 11:22; DOM 03:30, 09:16; JPN 02:55). R8 "Capital loop with money
  moving" (T21 + A27). §6 rank 11.
- BOOM evidence (VERIFY.md): A27 has a NEW BOOM witness - a money note travelling a dashed edge at 08:14-08:21,
  08:55.5-08:57.5, 11:32 and 15:11 (`A58_dock_0810/frames/t08m19.0s.jpg`, `T40_R36_inset_echo/frames/t08m56.5s.jpg`).
  T21 / R8's BOOM witness is CORRECTED: at 04:22 two chips are joined by an infinity glyph, and at 15:10 the chain
  snakes down a grid and is "never closed into a loop"; BOOM is therefore NOT a witness for the ring, which stands on
  BUB 11:22 and RST 9:30.
- Use when: USE-WHEN `:583` T21 "the chain closes on itself ("a financing loop")", don't "an open chain"; `:613` A27
  "the direction of money is the mechanism", don't "decor on a static relation".
- Recall: docs_find "flow ring" -> CAPABILITIES `:103` (the FLOW DIAGRAM); docs_find "loop" -> no flow hit. The code:
  - `species/flow.mjs` `flowLayout` (`:75`: "A row inside the box; a COLUMN when the box is taller than it is wide");
  - the clothoid edges (`flowAnchors` `:178`, `flowEdgeF` `:171`);
  - `edge_states` / `operators` (`_validate_flow_extensions`, compiler `:2690`).
- Verdict: EXTEND flow. `flowLayout` gains a `ring` branch (the n nodes on an ellipse inscribed in the box, the first
  at 12 o'clock, clockwise). A NEW `flowTokens(sp, t)` places k tokens by ARC LENGTH along each drawn edge's polyline,
  a pure function of t. **A token is a plain dot in the edge's ink by default** (review finding 15: a drawn "coin"
  mark sits too close to A2a, never generate an icon); the sourced glyph `coins.svg` (Lucide) is used only when the row
  names it (`tokens: {glyph: "coins"}`).
- Write set: `content/video_engine/scripts/species/flow.mjs` (`flowLayout`, NEW `flowTokens`; synced);
  `build_scene_timeline_f.py` (`_validate_flow_extensions`: `layout: "ring"`, `tokens: {n, speed, from_at}`);
  `effects/cards/species.json` (`species:flow` options; parent-merged); `tests/kinetics/flow.test.mjs`,
  `tests/test_flow_loop.py` (new); the golden `flow-loop-tokens` (new).
- Input evidence: no H sentence names a loop outright (a 0-hit take search for "loop", "circle", "comes back"). The
  candidate beat is H row 16, "who is paying" (244.72-245.43): the capex money round the borrowers. **The parent
  confirms the beat on the frame, or the verb is proved on a private test-bed beat labelled as one** (P69's stub names
  rows 7, 16 and 17 as derived).
- Constraints:
  - A ring needs a closed edge chain (the last node back to the first). An open chain under `layout: ring` is refused
    by name ("a loop closes on itself - use the row").
  - Tokens never move on an edge before it is drawn, and their speed is constant per unit of arc.
  - Tokens are motion (s99, they travel), each counted once as an event at `from_at`.
  - Byte-identical for every existing flow (the goldens `flow-swap`, `ring-dashed-chip`, `chip-board` unchanged).
- Acceptance:
  1. A 4-6 node loop lays on a ring, and its edges draw in order.
  2. Tokens run the edges from `from_at`, seek-exact.
  3. The gate counts the tokens' start.
  4. One golden: a four-node loop, tokens mid-run.
- Stop conditions: the clothoid fitter cannot bow an edge along a ring without crossing a chip (report the angles; do
  not change the fitter).
- Regression: `python -m pytest content/video_engine/tests/test_flow_loop.py -q`
- Expected RED (probed at `50b2f85`): a flow with `layout: "ring"` and `tokens: {n: 3}` is ACCEPTED AND IGNORED -
  `_validate_flow_extensions` returns `[]` - and `flowLayout(box, 4, {layout: "ring"})` returns a row. The RED test
  asserts the ring geometry and the by-name refusal of `layout: "ring"` on an open chain; T11 adds both.
- Validate: `python -m pytest content/video_engine/tests/test_flow_loop.py -q` then `node --test content/video_engine/tests/kinetics/flow.test.mjs` then `node --test content/video_engine/tests/kinetics/flow-extensions.test.mjs` then `python -m pytest -q content/video_engine/tests/test_flow_extensions.py` then COMMON-TAIL
- Frame acceptance: the golden, and a strip (the loop drawing, tokens at 25 / 50 / 75 % of their lap), beside BUB 11:22
  (`frame_0057.jpg`) and DOM 03:30 (BRAVOS-FRAME `-ss 210`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T12: Chip states `lit` / `tick` / `sell` (and `buy`) (was P69 T42; A59's BUY folded in from P69 T60)
- Status: done - lane B 96fa32c (chip states)
- Owner: implementation_luna (LANE B), then reviewer (the chip, after P70 T1b's seal)
- Depends on: P70 T1c committed (it edits `species/chip.mjs`'s ring ink; P70 T1b, the seal, is committed at `50b2f85`)
- Harvest:
  - v2 A36 "The active actor tile glows", n=3 (BUB #20; CHN 97; D40 09:04 (G)): "`chip` has DIM, no LIT".
  - F3 "Halo behind the active tile" (BUB #20).
  - A14 "✓ / ✗ badges" (the tick; BUB #40, HIS 06:07).
  - A59 "BUY / SELL state tabs" (JPN 04:08, 05:34; DOM 17:30).
  - §6 rank 9.
- Use when: USE-WHEN `:637` A36 "the sentence is about ONE actor of a set", don't "a held halo counts as 0 events (s91);
  a pulse is motion (s99)"; `:667` A59 "who must sell, who buys (H row 10's SELL ticket)", don't "implying a trade
  record".
- Recall: docs_find "chip lit" -> effects `species:chip`, `species:ring`; docs_find "chip tick" -> no chip hit. The code:
  - `species/chip.mjs` `CHIP` (`:32`), `chipCrossF` (`:81`), `chipStrokes` (`:88`: the two-stroke X);
  - `CHIP_STATES = ("on", "crossed")` (compiler `:197`);
  - `_validate_chip` (`:2545`; since P70 T1b its stamp-form branch refuses `state` / `cross_at` by name, `:2595`:
    "chip stamp: state/cross_at are not supported").
- Verdict: EXTEND chip.
  - `state: "lit"` adds a held halo, an annotation (0 events, s91), or `pulse: true`, a blink counted as motion (s99).
  - `tick_at` is the cross's sibling: a two-stroke ✓ on the curvature stroke, the chip keeping its ink (no dim).
  - `tab: "sell" | "buy"` is a state tab on the chip's edge, landing on `tab_at` on the badge spring, SELL in the neg
    token and BUY in the pos token (E28's sign inks).
  - No icon is added: the ✓ is strokes, as the X is.
- Write set: `content/video_engine/scripts/species/chip.mjs` (synced); `build_scene_timeline_f.py` (`_validate_chip`,
  `CHIP_STATES`); `gate_motion_density.SPECIES_EVENTS["chip"]` (adds `tick_at`, `tab_at` and a pulse; parent-merged);
  `effects/cards/species.json` (`species:chip` options; parent-merged); `tests/kinetics/chip.test.mjs`,
  `tests/test_chip_states.py` (new); the golden `chip-states-sell` (new).
- Input evidence: H row 10, "sell" (take 91.72-92.00), on the NVIDIA / hynix chip board (P70 T1's `NVIDIA_CHIP` beat,
  58.60). The golden recasts one chip `tab: "sell"` at 91.72 + 0.1.
- Constraints:
  - Byte-identical absent the new keys (the goldens `chip-board`, `chip-stamp-*`, `flow-swap`, `count-array`
    unchanged).
  - `tick_at` and `cross_at` on one chip are refused ("a thing held or failed, not both").
  - The tab never implies a trade record: a tab label that is a number is refused.
  - The stamp form refuses the states by name today (`_validate_chip` `:2595`: "chip stamp: state/cross_at are not
    supported"). T12 extends that refusal to `tab`, `tab_at`, `tick_at` and `pulse` on a stamped chip; a seal carries
    its verdict in its ring text (s121), not in a state.
- Acceptance:
  1. Each state lands on its word.
  2. `lit` held = 0 events; `pulse` = 1 event per blink onset (s99).
  3. The ✓ draws in two strokes over `CHIP.CROSS_S`.
  4. SELL / BUY tabs land on the badge spring in the sign inks.
  5. One golden: the SELL tab on row 10's beat.
- Stop conditions: the seal's `chipPose` (`chip.mjs:224`, since T1b) moves the glyph chip's pose in a way the tab
  cannot follow (report).
- Regression: `python -m pytest content/video_engine/tests/test_chip_states.py -q`
- Expected RED (probed at `50b2f85`): `_validate_chip` refuses `state: "lit"` ("chip: state must be one of
  on|crossed"), but `tab: "sell"`, `tick_at` and `glyph` are ACCEPTED AND IGNORED (no error names them; the function
  checks `state` and `cross_at` only, `:2545`-`:2615`). The RED test asserts the new states' behaviour and T12's
  by-name refusals (a number as a tab label; `tick_at` with `cross_at`; a state on the stamp form).
- Validate: `python -m pytest content/video_engine/tests/test_chip_states.py -q` then `node --test content/video_engine/tests/kinetics/chip.test.mjs` then `python -m pytest -q content/video_engine/tests/test_chip_stamp_arrival.py` then `python -m pytest -q content/video_engine/tests/test_gate_motion_density.py` then COMMON-TAIL
- Frame acceptance: the golden; a strip of `lit`, the tick and SELL / BUY; beside JPN 04:08 (BRAVOS-FRAME `-ss 248`) and
  BUB #20 (`frame_0020.jpg`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T13: A second axis, and an inverted one, for a co-movement claim - and `y2` refused until it draws (was P69 T43b; R26-307)
- Status: done - lane B f956fd7: `y2` draws on a dense line page with its claim (inverted when asked); refused by name elsewhere and wherever a reading would cross the scales (the reviewer's round 2); golden `dual-axis-inverted` (TIC vs DGS10, r -0.83, a labelled reference beat)
- Owner: implementation_luna (LANE B), then reviewer (s102's truth conditions)
- Depends on: P70 T2 committed (it owns `buildLedgerLine`'s tick and tag writes)
- Harvest: v2 T14 "Dual-axis line over line (LHS/RHS, sometimes inverted)", n=7 (BUB #74; RST 7:00; HIS 00:00; DOM
  01:00, 08:56, 12:00, 16:04; JPN 01:10, 06:38; STK 6:54). F15 "Axis ticks coloured to match their series". C5 was
  cleared by s102.
- BOOM evidence (VERIFY.md): T14 dual-axis CONFIRMED in six forms (04:18, 05:47, 08:24, 13:33, 15:06, 16:18); a
  THIRD series with its own second right axis arrives at 14:17.5-14:18 (a triple axis - evidence only, not built
  here). F15 (ticks in the series' colour) is NOT FOUND in BOOM (the tick labels are grey on both axes; only the legend
  dashes carry colour): constraint (c) below rests on s102 (c), the operator's ruling, not on BOOM.
- Use when (USE-WHEN `:251`): "two series on their own axes (LHS / RHS), one inverted when they move inversely, and the
  sentence is "these move together" or "this one leads that one"". Don't: "the claim is a level or a change ...; an axis
  without its unit, an inverted axis not saying "inverted", ticks not "coloured with their own series"".
- Recall: docs_find "y2" -> 0 hits; docs_find "second axis" -> CAPABILITIES `:119` (and `:234`, THE FREEZE BEAT, a false
  hit; draft 1 mis-cited it as "the broken axis", review finding 12); docs_find
  "line_unit" -> CAPABILITIES `:77`. The code:
  - `buildLedgerCombo` (`:11735`) ALREADY draws a right axis in the line's own colour naming its unit (`own`, `lunit`,
    `lcol`, class `lp-y2`, `line_label`, `:11802`-`:11821`; P47 T9 + P69 T64);
  - `ledger_page.validate` (`:936`) checks no top-level `y2`, so it is silently dropped (BACKLOG-HISTORY `:913`
    R26-307).
- Verdict: EXTEND.
  - The combo's right-axis block is lifted into a shared `lpRightAxis`, called by both builders (the combo
    byte-identical).
  - A dense-line object gains `y2: {series: [i], unit, label, invert?}` plus a required `claim: "comove" | "lead_lag"`.
  - R26-307 is closed first. Until the draw lands, `y2` on any page is refused by name. Once it lands, it is refused
    without `claim`.
- **Thin stub, a bounded discovery.** P69 names no H beat for co-movement. The slice first searches `SCRIPT-H` and the
  take for a co-movement or lead-lag sentence and the committed series pair it would need (two sourced series in
  unlike units). If there is none, the golden is a private test-bed beat on a sourced pair from disk, labelled as
  reference. Owner: implementation_luna. Stop: no sourced pair with unlike units on disk (report; ship the refusal and
  the draw with a fixture-free unit test only, and the golden waits).
- Write set: `content/video_engine/scripts/ledger_page.py` (NEW `_validate_y2`, called from `validate`); the engine
  (`buildLedgerLine`'s right-axis block, `lpRightAxis` shared with `buildLedgerCombo`; the inverted y map);
  `build_scene_timeline_f.py` (only if the plate grammar must pass the key); `measure_page_boxes.py` (a
  representative; parent-merged); `tests/test_dual_axis.py` (new); the golden `dual-axis-inverted` (new).
- Constraints (s102):
  - (a) `claim` is required.
  - (b) Each axis names its unit, and an inverted axis writes "inverted" beside its unit.
  - (c) Each axis's ticks take their series' ink (T37b's helper).
  - E28 binds every single-axis page.
  - The longform key rail and badges carry both.
  - The right axis's words are in `page_boxes`.
- Acceptance:
  1. R26-307: `y2` on a page with no draw path is refused by name, tested FIRST.
  2. A comove pair draws on two labelled axes, one inverted, and the ticks are inked.
  3. A `y2` without `claim` is refused, citing s102.
  4. A single-axis page and every combo are byte-identical.
  5. One golden.
- Stop conditions: lifting the combo's block changes a combo golden (stop; keep a duplicate and report the debt).
- Regression: `python -m pytest content/video_engine/tests/test_dual_axis.py -q`
- Expected RED (probed by reading `validate` `:936`-`:985`): `ledger_page.validate({"title":..,"src":..,"series":[..2 pts series..],"y2":{...}}, "line")` returns `[]`, so `y2` is accepted and ignored.
- Validate: `python -m pytest content/video_engine/tests/test_dual_axis.py -q` then `python -m pytest -q content/video_engine/tests/test_stacked_combo.py` then `python -m pytest -q content/video_engine/tests/test_longform_profile.py` then `python -m pytest -q content/video_engine/tests/test_ledger_page.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside HIS 00:00 (BRAVOS-FRAME `-ss 0.5`) and JPN 01:10 (`-ss 70`), 16:9 and the phone
  390 px read.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T14: The decade ruler - a scrolling time-passage ground under a chip row (was P69 T55; RESCOPED by BOOM's frames)
- Status: done - lane B df678cc (the decade ruler)
- Owner: implementation_luna (LANE B)
- Depends on: T0. (Draft 1's dependency on T9's pill is gone: the witnessed ruler pins nothing to a tick.)
- Harvest: v2 T32 "Epoch ruler: a time axis with cards pinned to ticks", BOOM 05:50 (G) only. **VERIFY.md CORRECTED it
  (the ruler exists; the cards are not pinned):** "A full-width tick ruler (yearly minor ticks, large faded decade
  numerals) sweeps in over the blurred chart and **scrolls**: 1980/1990 at 05:51.0, settling on 2000/2010/2020 by
  05:52. The chips Smartphones, Streaming and Cloud Computing pop in a **row above the ruler** [05:53.5 / 05:54.5 /
  05:55.5]. There are no year labels, no dashed pins and no tick alignment. At 05:58 a "Telecom Companies" chip lands
  above them with a dashed tree to the three; "Not Wrong" (06:05.5) and "Too Early" (06:08) labels follow." Narration:
  "It took more than a decade for technologies like smartphones, streaming, cloud computing" (05:49.04-05:56.40).
  Frames: VERIFY.md `T32_epoch_ruler/frames/t05m51.0s.jpg`, `t05m52.0s.jpg`, `t05m55.5s.jpg`, `t06m08.0s.jpg`.
  **P69 T55's "cards pinned at their years" spec (its (2)) is retired as Gemini-invented**; the slice builds the
  witnessed form.
- Use when (USE-WHEN `:877`): "a lag of years between cause and payoff ("the fibre came first")". Don't: "a single date
  (use A10)". The card adds the witnessed don't: the ruler is a GROUND for time passing; it pins no card to a year.
- Recall: docs_find "ruler" -> 2 hits (USE-WHEN `:849`), 0 capability rows. `species/thread.mjs` names "the ruler"
  (HF-16) but builds only the wire. docs_find "epoch" -> CAPABILITIES `:104` (the span). The chip row is the existing
  chip species / chip board (CAPABILITIES `:100`); the dashed tree is the flow's dashed edges (CAPABILITIES `:103`);
  the chart behind recedes by an existing recede (`panel_focus`'s `receded` role, CAPABILITIES `:229`, or T15's
  `under: blur` when the chips are docked) - T14 adds no blur of its own.
- Verdict: NEW - `species/ruler.mjs`: `{"kind": "ruler", at, dur, from: <year>, to: <year>, settle: [<decade>, ...]}`.
  A full-width ruler with yearly minor ticks and large faded decade numerals wipes on (A67) and SCROLLS from `from` to
  its settle window on a pure-in-t ease, then holds. The chip row above it and the tree are composed by the author (the
  recipe `recipe:the-decade-ruler`, candidate), not drawn by the ruler.
- Write set: `content/video_engine/scripts/species/ruler.mjs` (new, synced); the engine (its region; the
  `_validate_entry` dispatch is the parent's union); `build_scene_timeline_f.py` (NEW `_validate_ruler`);
  `effects/cards/species.json` (`species:ruler`; parent-merged); `effects/recipes/the-decade-ruler.json` (new,
  candidate); `tests/kinetics/ruler.test.mjs`, `tests/test_decade_ruler.py` (new); the golden `decade-ruler-scroll`
  (new).
- Input evidence: H row 19, "twenty years" (432.35-432.96) - the lag to the payoff - or row 9's span from the
  railways to the internet (`two thousand` 79.80, `just crossed eight` 87.40); the parent confirms the beat, else a
  private test-bed beat labelled reference.
- Constraints:
  - The numerals are TRUE years at even spacing per year; the scroll lands on the named decades exactly (a settle that
    names a year outside `from`-`to` is refused by name).
  - The ruler implies no date for any chip: no pin, no leader to a tick, no year label on a chip that the ruler did
    not print (s109: an unambiguous reading).
  - The scroll TRAVELS, so it is motion (s99), counted once at its start; the held ruler is ground (0 events).
  - Byte-identical absent the species.
- Acceptance:
  1. The ruler wipes on, scrolls and settles on its word; seek-exact.
  2. The recipe composes it with a chip row and a dashed tree over a receded chart, proved as a beat.
  3. One golden: the settled ruler under a chip row.
- Stop conditions: the scroll needs a camera move rather than the ruler's own translation (report: M14 reads the
  camera).
- Regression: `python -m pytest content/video_engine/tests/test_decade_ruler.py -q`
- Expected RED: the `ruler` species is refused as an unknown kind by `_validate_entry` (probed at `50b2f85`: the kind
  list has no `ruler`).
- Validate: `python -m pytest content/video_engine/tests/test_decade_ruler.py -q` then `node --test content/video_engine/tests/kinetics/ruler.test.mjs` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- Frame acceptance: the golden and the recipe strip beside BOOM 05:51.0, 05:55.5 and 06:08.0 (BRAVOS-FRAME `-ss 351.0`,
  `-ss 355.5`, `-ss 368.0` on `scratch/jx3Ll_full.mp4`).
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T15: A dock over a chart chooses by intent - `under: hover` or `under: blur`, the author's choice by the beat's goal, over ledger pages; and R3, the term over the parked chart (was P69 T40; E99 s98, s124)
- Status: done - lane B 8765bf8: `under: hover | blur` per dock (never a default), the veil clipped round the page's words (E52), M25 / M27 WARN only on the chart's data (the page's words stay FAIL), the choose-WARN only when a dock meets the plot (H: 8); two review rounds; goldens dock-hover-over-ledger / dock-blur-over-plate; recipe term-over-the-parked-chart (candidate)
- Owner: implementation_luna (LANE B), then reviewer (a default change, and M25 / M27's rule for a dock over ink)
- Depends on: P70 T8 committed (it owns `dock_opts` and `render()`'s dock-arrival branch); P70 T13 committed (the
  drift-hold `idle: hold` the hover holds on, and the compiler's dock-option validation, P70 plan `:1090`-`:1102`)
- Harvest:
  - v2 A23 "The chart blurs / dims under an overlay", n=4 (BUB #11-12; DOM 02:00, 09:16; HIS 06:04; STK 1:54):
    "`exit:blurzoom` has an 18 px backdrop blur; no dock option. **s98 allows it** over a busy chart plate".
  - R3 "Term / mechanism over (or beside) the held chart", n=4 (BUB 1:59; DOM 08:56-09:29; HIS 06:04; JPN 04:08,
    05:28).
  - §6 rank 6.
  - The hover's reference: the operator's HyperFrames drift-hold (`content/video_engine/hyperframes/compositions/
    components/drift-hold.html`), which s124 names ("maybe use that hyperframes reference i provided before") and P70
    T13 ports as `idle: hold`.
- BOOM evidence (VERIFY.md): A22 / F4 CONFIRMED - the chart blurs and darkens behind chips at 03:39.5, 04:03.5 and
  12:40 (`T33_map_a/frames/t04m04.0s.jpg`): the `under: blur` case (the chart is not the point while the chips speak).
- Use when: USE-WHEN `:601` A23 "an explainer dock lands over a busy chart plate (s98 option)"; its don't: "the chart
  must keep being read ...". `:691` R3: "the chart blurs or parks, a term chip lands, a flow explains it, then the chart
  returns", don't "longer than one proof beat". s124 restates both: HOVER when the chart underneath must keep being
  read; BLUR when "the chart underneath is not the point right now and the dock (typically a small or
  medium evidence chart over a larger chart) is up briefly to make its point". The card copies s124's two cases.
- The ruling (E99 s124 AS AMENDED the same day - no default: "it needs to be a choice depending on the goal of what we want to have happen"; the original text, superseded on the default only, `OPERATOR-RULINGS.md:3379`): "(1) THE DEFAULT over any chart - a chart plate or a ledger page's
  plot - is HOVER: the dock lifts (its shadow grows with the lift), grows a step and holds on the drift-hold idle (P70
  T13, HyperFrames `drift-hold`), and the chart under it stays sharp and keeps being read. (2) BLUR is the author's
  OPTION per dock ... the blur clears on the dock's leave. (3) It AMENDS s98 ... and E63 so far as a dock may land over a
  ledger page's plot, hovering or blurred. Where the dock sits stays the author's (s106: fit findings are WARNs).
  Carrier: P71 T15".
- Recall:
  - docs_find "backdrop blur" -> effects `exit:blurzoom` ("... under an 18 px backdrop blur");
  - docs_find "blurzoom" -> CAPABILITIES `:71`; `BLURZOOM_BLUR` 18 (engine `:6059`), painted as
    `bzveil.style.backdropFilter` (`:20587`-`:20588`); `#bzveil` sits ABOVE the docks in the player template (`:697`),
    so a veil UNDER a dock needs its own element;
  - docs_find "panel_focus" -> CAPABILITIES `:229` ("`receded` - scale 0.86, dim 0.55, blur 5 px");
    `PANEL_FOCUS.RECEDE` (`:12484`), painted in `lpPaintPanels` (`:12746`; the filter `:12769`, "the filter is inside
    the scale");
  - the dock's idle: `idleCssFor("dock", d.idle, ...)` (`:20866`; the parked card `:20922`); the contact shadow
    `#dock-contact-<s>` (`:20836`); the arrival branch (`arriveOf`, `:20823`);
  - E63 in the compiler: `read_over_build` (`:9222`; called `:10782`) moves any read off a ledger plot
    (`read_moved` / `read_deferred`); in the gate, M27 (`_over_build_faults` `:2745`) FAILs a card reading on the
    page's data or ink, and M25 (`_layout_faults` `:2589`) FAILs a settled card on the data;
  - `lpPlateRecede` (`:9829`) is NOT a blur: it is the two-plate field's recede, and P69 T70's citation of it is wrong;
  - a chart plate IS a ledger page (E61): a ledger world is `world.kind == "ledger"` - no separate marker exists or is needed.
- Verdict: EXTEND, one commit.
  - **The option (byte-identical absent it).** The dock gains `under: "hover" | "blur"`.
    - `hover`: after the arrival settles, the dock lifts (a y offset and its shadow growing with the lift, on the
      contact shadow / the `.dock` shadow), grows one step (a scale dial), and holds on `idle: hold` (P70 T13's kind;
      `whisper` for a card carrying a chart, per P70 T13's acceptance); the chart under it is untouched and sharp. The
      lift and step reverse on the leave. The dials are read off drift-hold.html's own amplitudes where it has them,
      each with a `[DERIVED: ...]` tag; the frame read picks the rest.
    - `blur`: a NEW `#dockveil` element between `#wash` (template `:676`) and `#dock-1` (`:684`), its
      `backdropFilter` ramped on the dock's own enter / exit clock (the blurzoom's law, at `panel_focus`'s measured
      5 px or the blurzoom's 18 px: a dial the frame read picks, `[DERIVED: ...]`), painted in `render()` right after
      the wash/spot DIRECTION block (`:20708`-`:20719`, which knows `live`) and before `worldAnswer` (`:20722`). It
      clears on the dock's leave. `blur` implies no hover lift (the dock stands on the blurred chart).
    - Over a chart plate AND over a ledger page's plot (s124 (3) lifts E63's bar for a dock that names `under`).
    - A dock that NAMES `under` keeps its authored read place: `read_over_build` returns None for it (the author chose
      to sit over the chart, s124 (3), s106). A dock that names nothing keeps E63 / E65's placer exactly as today.
    - The gate: M27 and M25 report a dock whose resolved `under` is set and whose box overlaps the data or ink as a
      WARN with its numbers ("hovering over the chart by intent, s124"), not a FAIL. A card with no `under` keeps
      today's FAIL.
  - **The choice is named, never assumed (s124 as amended).** A dock that lands over a ledger page and names no
    `under` compiles exactly as today and the compiler WARNs once per dock: "dock over a chart - choose `under: hover`
    (keep the chart read) or `under: blur` (focus a temporary evidence dock)" (s106: a WARN, never a refusal). The
    authoring kit's dock guide and the dock card's `use_when` state the rule by goal. The committed H door is
    byte-identical; which of H's docks hover or blur is authored later in a lane-A row, by each beat's goal.
  - The recipe `term-over-the-parked-chart` (R3) composes `under` with `park`.
- **"Chart plate" IS the ledger page (E61 `OPERATOR-RULINGS.md:1991`: "The ledger/chart plate is the world that we build on").** No plate marker is needed. A dock over a picture plate (a generated still, the memo) is not over a chart: no WARN; `under` there is the author's word only.
- Write set:
  - `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`render()`'s dock branch: the hover pose beside the
    arrival and the contact shadow, after P70 T8 / T13's hunks; the NEW `#dockveil` paint after the wash/spot
    direction block);
  - `docs/content-video-engine/samples/scene-evidence-player.template.html` (the `#dockveil` element only; P69 T37c
    edits the title token in the same file, a different region, and lands first);
  - `content/video_engine/scripts/build_scene_timeline_f.py` (`DOCK_OPTS` `:118` + `dock_opts` `:6457`: `under`,
    refused by name when it is not `hover` / `blur`; `read_over_build` `:9222`: skip a dock that names `under`;
    the unchosen-dock WARN);
  - `content/video_engine/scripts/gate_motion_density.py` (`_layout_faults` `:2589` and `_over_build_faults` `:2745`:
    a dock with a resolved `under` over ink is a WARN with its numbers; the M25 / M27 SRC lines cite s124);
  - `effects/cards/dock_option.json` (`dock_option:under`; parent-merged);
  - `effects/recipes/term-over-the-parked-chart.json` (new, status `candidate`, with `use_when`);
  - `tests/test_dock_under.py` (new); the goldens `dock-hover-over-ledger` and `dock-blur-over-plate` (new).
- Input evidence: H row 11 (the memo plate, SHOT-TABLE-H #6, 104.31-147.82, `world-internal-memo-v1`) or row 16's
  chart plate for `blur` (a small evidence dock up briefly over a larger chart, s124 (2)); an H ledger page's held
  chart card for `hover` (row 16's capex page, the dock the door already lands there). The R3 proof beat is a private
  test-bed beat on row 12 (`inflated expectations` 134.07-136.10), labelled as one.
- Constraints:
  - s124 (amended): HOVER or BLUR is the author's per-dock choice by the beat's goal, over ledger pages; neither is a default. "Wash beats the focus rack" stays the default for a dock over a NON-chart plate.
  - Where the dock sits stays the author's (s106): overlap findings are WARNs with numbers, never a move.
  - A receded PANEL's blur stays `panel_focus`'s (s104; T8b owns it).
  - Pure in t: the hover and the veil ride the dock's own clock; a seek and a play-through give the same bits.
  - Byte-identical absent `under` (only the WARN is new).
- Acceptance:
  1. A dock with `under: "blur"` over a chart plate AND over a ledger plot blurs the chart under it while it reads and
     clears on its leave; the veil sits above the chart and below the dock.
  2. A dock with `under: "hover"` lifts, grows its step, holds on `idle: hold` (one whole drift-hold cycle across the
     hold, P70 T13's law), and the chart under it is pixel-identical to the chart without the dock outside the dock's
     own box and shadow.
  3. A dock that names `under` over a ledger plot is not moved by `read_over_build`, and M25 / M27 report it as a WARN
     with its numbers; a dock with no `under` keeps today's placement and today's FAIL (`test_dock_over_build.py`
     unchanged and green).
  4. A dock over a ledger page with no `under` compiles byte-identically and carries the choose-by-goal WARN; the H door is byte-identical (its new WARNs listed).
  5. The R3 recipe is proved as a beat whose strip the parent reads.
  6. Two goldens (hover over a ledger page, blur over a plate).
- Stop conditions: a `backdrop-filter` under a dock breaks the headless render's determinism (report the frame hash
  drift; fall back to a `filter` on the chart layer and say so); the hover needs to edit P70 T8's arrival lines rather
  than add beside them (stop; the parent sequences it); P70 T13's `hold` kind cannot be applied to a dock (report:
  that is T13's contract).
- Regression: `python -m pytest content/video_engine/tests/test_dock_under.py -q`
- Expected RED (probed at `50b2f85`): `dock_opts({"under": "hover"})` raises "dock option 'under' is not one of
  arrive|mass|centre|...|names" (unknown dock keys are refused by name, `:6457`-`:6475`); and M27 FAILs a probe
  instant where a placed dock reads on a ledger page's data.
- Validate: `python -m pytest content/video_engine/tests/test_dock_under.py -q` then `python -m pytest -q content/video_engine/tests/test_dock_over_build.py` then `python -m pytest -q content/video_engine/tests/test_gate_motion_density.py` then `python -m pytest -q content/video_engine/tests/test_transitions_e47.py` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- Frame acceptance: the goldens and a strip over each dock's enter / hold / leave (hover over a ledger page; blur over a
  plate and over a ledger plot), beside DOM 09:16 (BRAVOS-FRAME `-ss 556`) and HIS 06:04 (`-ss 364`); ours beside
  drift-hold.html rendered by `npx hyperframes@0.7.101 render` (P70 T13's sheet).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T16: `project` - a labelled dashed continuation past the last real point (was P69 T41)
- Status: done - lane B `7595f34`: `projection: {label, tier, src}` drawn dashed at Bravos's measured dash from the last real point, never blooming, refused by name as data (E77); golden `project-issuance-2026e`; found R26-385 / R26-386
- Owner: implementation_luna (LANE B), then reviewer (E77: an estimate is never data)
- Depends on: T13 (`buildLedgerLine`, wave 3)
- Harvest:
  - v2 A17 "Dashed hypothetical path past the last real point", n=6 (BUB 8:34 "???"; RST 17:20; STK 8:20, 9:01; HIS
    12:20; JPN 04:15).
  - T23 "Projection chart: actual -> forecast" (RST 17:20; D40 04:30): "The card's `dash` series only fades in".
  - S3 "Dashed = hypothetical".
  - §6 rank 7: `plate_option:project` on "`chart_to:extend`, the flow nib's dash, `tippill`".
- BOOM evidence (VERIFY.md): A17 / T23 CONFIRMED at 03:18, 17:59.5 and 18:52-19:00; S3 CONFIRMED (every dashed series
  is a projection); at 03:18-03:19 a dashed hypothetical path is drawn PAST the plot's right edge, with a fill under
  it and a "?" (`A17_forward_0320/frames/t03m19.0s.jpg`) - evidence that the projection may run off the plot (T26's
  R5 composes it).
- Use when (USE-WHEN `:415`): ""if ..., then", "could reach": a scenario, labelled as one". Don't: "unlabelled".
- Recall: docs_find "projection" -> effects `recipe:estimate-opens-as-a-wedge` (a RANGE, "a single-point forecast
  (continue the line dashed)" is its own don't); CAPABILITIES `:120` (`extend`: "`chart_to {to: "extend", series: k}`
  draws a `later: true` series ... from its first point"). The legacy chart dock's `sr.dash` (engine `:7418`-`:7424`)
  is the dashed-series precedent. `ledger_page` `later` series (`:1604`, `:2542`).
- Verdict: EXTEND `extend`.
  - A `later` series may carry `projection: {label, tier, src}`. It must start at the last actual datum (the path opens
    from the real line, never from nowhere).
  - `buildLedgerLine` draws it dashed (S3), unbloomed (s117: context, not a primary line), with its label as a tag.
  - `chart_to extend {series: k}` draws it on its word.
- Write set: `ledger_page.py` (the series key `projection`, its check); the engine (`buildLedgerLine`'s path style for a
  projection series; `lpPaintExtend` `:15395` only if the nib must dash); `build_scene_timeline_f.py` (only if the
  extend validation must read it); `effects/cards/plate_option.json` or `chart_to.json` (the option; parent-merged);
  `tests/test_projection_path.py` (new); the golden `project-consensus` (new).
- Input evidence: H row 16, "four hundred and eighty ... six hundred and ninety" (take 293.80-295.01, 297.49-299.05):
  the consensus capex. Its series file and tier are read off disk. If the consensus is a RANGE, the wedge recipe is the
  form and T16's golden uses the single point the script speaks.
- Constraints (E77, s93):
  - Refused by name (hard, an untruth): a projection with no `label`, no `tier`, or a first point that is not the last
    actual.
  - The label reads as a projection ("2026E", "consensus"), not a datum.
  - Byte-identical absent the key.
- Acceptance:
  1. The dashed continuation draws on its word from the last actual, labelled with its tier.
  2. It never blooms.
  3. The refusals hold.
  4. One golden.
- Stop conditions: a `later` series cannot start at the last actual's x without re-laying the x domain (report).
- Regression: `python -m pytest content/video_engine/tests/test_projection_path.py -q`
- Expected RED (probed at `50b2f85`): `ledger_page.validate` returns `[]` for a line page whose series carries
  `projection: {label: "x"}` (no `tier`, no first point at the last actual) - the key is ACCEPTED AND IGNORED. The RED
  test asserts the refusal of that unlabelled / untiered projection by name.
- Validate: `python -m pytest content/video_engine/tests/test_projection_path.py -q` then `python -m pytest -q content/video_engine/tests/test_line_bloom.py` then `python -m pytest -q content/video_engine/tests/test_chart_transitions.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden and a strip at 293.80 / 297.49 / 299.05 s, beside STK 9:01 (BRAVOS-FRAME `-ss 541`) and
  HIS 12:20 (`-ss 740`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T17: Hub and spoke - one institution to many, and a link that fails (was P69 T57)
- Status: done - lane B `f28a084`: `layout: hub` and `fail: {edge, at}` (BOOM's spring, the edge reddens); golden `hub-spoke-fail`; the badge's size and DOM's look are R26-384
- Owner: implementation_luna (LANE B)
- Depends on: T11 (`flowLayout`, tokens)
- Harvest: v2 T31 "Hub-and-spoke network", n=2 (DOM 04:30 "IMF seal, dashed spokes to six governments"; D40 09:04 (G)).
  A26 "A flow edge fails (an X on the link)", n=3 (BUB 8:46; BOOM (G); D40 09:04 (G)).
- BOOM evidence (VERIFY.md): A26 CONFIRMED at 04:41.0, "Investors ✕ Utility Companies"
  (`T21_loop_A26_fail/frames/t04m41.0s.jpg`).
- Use when: USE-WHEN `:521` "one institution connects to many ("the IMF stepped in for six")", don't "a chain (use
  `flow`)"; `:607` A26 "'lending dries up': the link breaks, not the node".
- Recall: docs_find "hub" -> only the remotion-ui registry (CAPABILITIES `:136`); docs_find "spoke" -> 0 relevant. The
  code: `flowLayout` (`:75`), the chip cross's two strokes (`chipStrokes`), the vecmap arc's struck X (CAPABILITIES
  `:105`).
- Verdict: EXTEND flow. `flowLayout` gains a `hub` branch (node 0 at the centre, 3-8 on a ring, T11's ellipse). An
  edge may carry `fail: {at}`: an X struck at the edge's midpoint by the chip's two-stroke law, the edge reddening in
  the neg token and severing (its two halves retracting 12 %). Its nodes stay.
- Write set: `species/flow.mjs` (the `hub` branch, the failed edge; synced); `build_scene_timeline_f.py`
  (`_validate_flow_extensions`: `layout: "hub"`, an edge's `fail`); `effects/cards/species.json` (parent-merged);
  `tests/kinetics/flow.test.mjs`, `tests/test_hub_and_spoke.py` (new); the golden `hub-spoke-fail` (new).
- Input evidence: H row 16, "bond market" (273.45-274.56) / "who is paying" (244.72-245.43). The hub is the bond
  market and the rim is the borrowers. The parent confirms the beat on the frame (derived, P69).
- Constraints:
  - A spoke carries no value by default. Weighted spokes draw widths in true proportion with figures written; unequal
    widths with no figures are refused (P69 T57 (4)).
  - Byte-identical for every existing flow.
- Acceptance:
  1. The hub lays out, its spokes draw on their words, and the rim nodes land on their names.
  2. One edge fails on its word.
  3. T11's tokens may run the spokes.
  4. One golden.
- Stop conditions: a failed edge needs `edge_states` to retract and the two conflict (report; `operators` and
  `edge_states` are already exclusive).
- Regression: `python -m pytest content/video_engine/tests/test_hub_and_spoke.py -q`
- Expected RED: `layout: "hub"` is refused (after T11: "not one of row|ring"); an edge `fail` is unknown.
- Validate: `python -m pytest content/video_engine/tests/test_hub_and_spoke.py -q` then `node --test content/video_engine/tests/kinetics/flow.test.mjs` then `python -m pytest -q content/video_engine/tests/test_flow_loop.py` then COMMON-TAIL
- Frame acceptance: the golden beside DOM 04:30 (BRAVOS-FRAME `-ss 270`) and BUB 8:46 (`frame_0044.jpg`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T18: The "?" at the unknown, the collage that resolves into it, the predictions board (was P69 T53)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T12 (`chip.mjs`); T15 (`under: blur`, the blur a collage recedes under); P70 T1c (`chip.mjs`)
- Harvest:
  - v2 A61 ""?" prompt at the unknown", n=5 (BUB 8:34 "???"; CHN 0:35; HIS 01:43 "a big ? over the ROI node"; DOM
    06:15, 13:30).
  - F12 "Collage dissolves into "?"" (CHN 0:35).
  - R13 "Predictions board" (CHN 1:28).
- BOOM evidence (VERIFY.md): A61 CONFIRMED at 08:52.5, with more at 03:19 and 13:52 ("???" over an investors chip).
- Use when: USE-WHEN `:789` (A61), `:1007` (F12), `:1013` (R13); P69 quotes `:791` "the open question is itself the
  sentence" and `:792`'s don't, "where we can state a figure".
- Recall: docs_find "placeholder" -> CAPABILITIES `:90` (the breakthrough's `overflow_placeholder` "?",
  `ledger_page.PLACEHOLDER_MAX` `:991`: "a placeholder is a MARK, not a caption: "?" is the one Bravos uses");
  docs_find "predictions board" -> CAPABILITIES `:100` (the chip board, "the predictions crossed out one by one");
  docs_find "collage" -> 0 capability rows. The press stack: `species/press.mjs` `pressStack` (`:100`).
- Verdict: EXTEND.
  - A chip may carry `glyph: "?"`, a TEXT mark in the page face, drawn and pulsed like the cross (no icon: the
    catalogue has five Lucide glyphs, and A2a forbids a generated one).
  - A NEW `unknown` species: a large "?" landing at a datum / node / region, pulsing (s99) or held (s91).
  - F12: the press stack recedes under T15's blur while the "?" rises.
  - R13 is the recipe `recipe:the-predictions-board` (the chip rail, struck one by one, each sourced).
- Write set: `species/chip.mjs` (the `?` glyph; synced); the engine (a NEW `unknown` block); `species/press.mjs` (the
  stack's recede under the blur, only if T15's option cannot carry it); `build_scene_timeline_f.py` (`_validate_chip`
  `glyph`, NEW `_validate_unknown`); `effects/cards/species.json`; `effects/recipes/the-predictions-board.json` (new,
  candidate); `tests/test_unknown_prompt.py` (new); the golden `unknown-decide` (new).
- Input evidence: H row 23, "decide for yourself" (take 743.04-744.10); row 12, "what survives it" (145.75-147.15). F12
  and R13 have no H row and are proved on a private test-bed beat for the next hook, labelled as one.
- Constraints:
  - A "?" on a thing the same row states a figure for is refused (the don't).
  - Each prediction on the board names its record or press card (sourced).
  - Byte-identical absent the keys.
- Acceptance:
  1. The "?" lands on its word; pulse = motion, held = annotation.
  2. The collage recedes and the "?" rises.
  3. The board's chips strike in turn.
  4. The refusal holds.
  5. One golden (row 23).
- Stop conditions: the press stack's recede cannot take the blur without editing `render()`'s dock branch (report;
  that is P70 T8's and T15's).
- Regression: `python -m pytest content/video_engine/tests/test_unknown_prompt.py -q`
- Expected RED (probed at `50b2f85`): `unknown` is refused as an unknown species kind by `_validate_entry`; a chip's
  `glyph: "?"` is ACCEPTED AND IGNORED (no error names it); the recipe id does not exist. T18 adds the refusal of a
  `glyph` other than "?" by name.
- Validate: `python -m pytest content/video_engine/tests/test_unknown_prompt.py -q` then `node --test content/video_engine/tests/kinetics/chip.test.mjs` then `node --test content/video_engine/tests/kinetics/press.test.mjs` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside HIS 01:43 (BRAVOS-FRAME `-ss 103`) and CHN 0:35 (the CHN frame nearest 35 s); the
  F12 / R13 strips beside CHN 1:28.
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T19: Verdict tiles with a check state, two verdict panels, and the BUY tab on a tile (was P69 T60)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T12 (the tick and the tabs); P70 T8 (the dock branch and `dock_opts`); P70 T13 (the dock-option
  validation); T15 (its hover lines in the same dock loop); done: P69 T10c (the card profile) and T8b (panels)
- Harvest: v2 T26 "Mini-chart verdict tiles / "your portfolio" pair", n=2 (BUB 18:45; STK 10:11): "No ✓ state". R14
  "Two verdict panels" (BUB 18:45; STK 10:11). A14, A59.
- Use when: USE-WHEN `:977` (T26), `:1019` (R14); P69 quotes `:979` "the close rejects two easy options, one panel
  each" and `:980`'s don't, "the panels carry no sourced data".
- Recall: docs_find "verdict tile" -> 2 hits (USE-WHEN `:955`), 0 capability rows. docs_find "verdict" names the
  VERDICT STACK (CAPABILITIES "THE VERDICT STACK", `species/verdict.mjs`), which is the evidence wall, a different move.
  The chart card: `chart_card.py`, T10c's `card` profile (lane A CAPABILITIES "A chart card drawn for its own size").
- Verdict: EXTEND. A chart-card dock gains `verdict: {state: "tick" | "cross" | "buy" | "sell", at}`, painted by
  T12's chip-state laws on the card's corner (one grammar). R14 is a recipe of two cards side by side.
- Write set: the engine (a NEW `paintDockVerdict(el, d, t)` helper and its ONE call line in `render()`'s dock loop,
  after T15's hover lines; review's wave check); `build_scene_timeline_f.py` (the dock's `verdict` key; it must not
  collide with P70 T1b's `DOCK_SEAL_REFUSED` = `ring_text`, `ring_text_bottom`, `seal`, `:211`: a verdict tile is a
  state on a card, never a seal);
  `chart_card.py` (a `tile` size only if T10c's profile cannot carry it; say so); `effects/cards/dock_option.json`;
  `effects/recipes/two-verdict-panels.json` (new, candidate); `tests/test_verdict_tiles.py` (new); the golden
  `verdict-tiles-three-questions` (new).
- Input evidence: H row 21, "So ask it the three questions" (take 467.44-468.94). The rows tick on their words.
- Constraints: a tile's chart is drawn from its own sourced series (refused otherwise); a BUY / SELL tab is a scenario
  label, never a trade record.
- Acceptance:
  1. Each tile's verdict lands on its word.
  2. The two-panel recipe is proved.
  3. Byte-identical absent the key.
  4. One golden.
- Stop conditions: the card's DOM has no stable corner the state can anchor to across a park (report).
- Regression: `python -m pytest content/video_engine/tests/test_verdict_tiles.py -q`
- Expected RED (probed at `50b2f85`): `dock_opts({"verdict": ...})` raises "dock option 'verdict' is not one of
  arrive|mass|...|names" (unknown keys are refused by name, `:6457`-`:6475`); the recipe id does not exist.
- Validate: `python -m pytest content/video_engine/tests/test_verdict_tiles.py -q` then `python -m pytest -q content/video_engine/tests/test_chart_card_readable.py` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside STK 10:11 (BRAVOS-FRAME `-ss 611`) and BUB 18:45 (`frame_0094.jpg` if present,
  else the nearest; BUB has 89 frames, so the implementer names the frame used).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T20: Illustrations drawn as schematics - candles over a ghost wave, the motif line with X marks, a ✓ / ✗ on a datum, and A55's traced point (was P69 T62; A55 folded in from P70's Not Building)
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (s109 (1): no axis values, no figures it cannot source)
- Depends on: P70 T2 committed (the schematic); T12 (the tick and the cross)
- Harvest: v2 T8 "Candlesticks over a ghost wave" (BUB 4:47); T46 "Axis-free "Market" motif line with repeated X marks"
  (JPN 08:20-09:20); A14 (a datum badge: DOM 13:00, JPN 06:40 "X pins the two endpoints"); A55 "Traced state: a point
  runs along a schematic curve and paints each phase's colour", n=3 (DOM 07:30-08:30; STK 1:48; BOOM (G)).
- BOOM evidence (VERIFY.md): A13, a NEW BOOM witness - a green glowing segment runs round the grey sine wave, over
  and over, at 09:38-09:42 (`A55_T7_traced_state/frames/t09m39.0s.jpg`): the comet on a schematic, which A55
  composes. A21 / A55 CONFIRMED with no orange: green to the crest 09:45-09:57, red after the crest 09:58-10:04, green
  again 10:08 (`t09m57.0s.jpg`, `t09m59.0s.jpg`).
- Use when: USE-WHEN `:571` (T8), `:989` (T46), `:995` (A14), `:655` (A55). P69 quotes `:573` "rarely; price action as
  illustration" and `:997` "a tick for what held, an X for what failed".
- Recall: docs_find "candlestick" -> 1 asset (`prop-icon-candlestick-price-action-v1.png`, a still); docs_find "motif"
  -> 0 capability rows. P70 T2 builds `SCHEMATIC_SHAPES` / `schematic_series` and the "a shape, not a series" tag; A55
  composes P69 T36's `lit_stretch` comet on that schematic.
- Verdict: EXTEND P70 T2's schematic.
  - Two more shapes, `candles` (bodies and wicks generated from the ghost wave) and `motif` (an axis-free line named by
    one word).
  - A datum badge ✓ / ✗ anchored as a ring is (T12's glyph strokes).
  - A55: `lit_stretch` on a schematic with `phase_ink: true`, where the comet paints each phase in its own series
    ink as it passes.
- Write set: `ledger_page.py` (`SCHEMATIC_SHAPES`: `candles`, `motif`); the engine (the schematic branch of
  `buildLedgerLine` for the two shapes; a NEW datum-badge block in `buildPerform`; `species/lit_stretch.mjs`'s
  `phase_ink` only if the comet cannot read the phases); `build_scene_timeline_f.py` (the badge's validation);
  `effects/cards/page_builder.json`, `page_species.json`; `tests/test_schematic_illustrations.py` (new); goldens
  `schematic-candles`, `schematic-motif` (new).
- Input evidence:
  - T8 serves no H row (the guide `:574`) and is built for the catalogue on s109 (1), on a private test-bed beat.
  - The motif's candidate is row 24.
  - A14 on data is row 22's tripwire endpoints (`tripwire` 606.56-607.09).
  - A55 is row 12's hype cycle (P70 T2's golden: `inflated expectations` 134.07-136.10, `trough` 136.39-136.84).
- Constraints (s109 (1), hard): no axis value, no tick label, and no figure it cannot source on a schematic page. The
  "schematic" tag stays. Byte-identical absent the shapes and keys.
- Acceptance:
  1. Candles along the ghost wave on the word.
  2. The motif line with an X at each named vertex.
  3. A ✓ / ✗ on a real chart's datum.
  4. A55's comet paints the phases.
  5. The truth refusal holds.
  6. One golden per new form.
- Stop conditions: P70 T2's schematic does not expose its phases to a page species (report: that is T2's contract).
- Regression: `python -m pytest content/video_engine/tests/test_schematic_illustrations.py -q`
- Expected RED: `candles` and `motif` are not schematic shapes (after P70 T2); a datum badge is an unknown species.
- Validate: `python -m pytest content/video_engine/tests/test_schematic_illustrations.py -q` then `python -m pytest -q content/video_engine/tests/test_schematic_page.py` then `python -m pytest -q content/video_engine/tests/test_lit_stretch.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the goldens beside BUB 4:47 (`frame_0024.jpg`), JPN 08:20 (BRAVOS-FRAME `-ss 500`), JPN 06:40
  (`-ss 400`) and DOM 07:30-08:30 (`-ss 450`, `-ss 480`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T21: Fills to a level - below zero at a signed dip, the negative spike's glowing trough, and the underwater fill below a prior peak (was P69 T73)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: T10 (a level from a datum, C14)
- Harvest:
  - v2 A46 "Fill below zero at a negative spike" (D40 12:54 (G)).
  - R29 "Negative spike and its glowing trough" (D40 12:46-13:08 (G)).
  - A45 "Underwater fill": **UNBLOCKED - VERIFY.md CONFIRMS it** at 02:23.0 (2000-2013) and CORRECTS the second
    instance to 02:48.5 (1929-1954): "A pink fill runs between the prior peak's level rule and the price below it, with
    the price edge glowing" (`A44_A45_T37_swap1/frames/t02m23.5s.jpg`, `A44_A45_swap2_R22/frames/t02m49.5s.jpg`). A
    third instance fills under a dashed hypothetical path at 03:19 (`A17_forward_0320/frames/t03m19.0s.jpg`, T26's
    R5).
  - D40's frames ARE on disk, so A46 and R29 are frame-checked first (step 0).
- Use when: USE-WHEN `:777` (A46), `:831` (R29), `:913` (A45). P69 quotes `:915` "a period spent below a prior peak is
  the claim ('lost decade')" and `:833` "H row 22's "one soft month in June"".
- Recall: effects `page_species:spread` ("The region between two drawn series bleeds full of ink on a word");
  CAPABILITIES `:118` (a spread's two edges read from the active state). The code: `buildPerform`'s spreads
  (`:14338`), `paintSpread` (`:14410`), `_validate_page_fields` (`:2282`).
  - **A spread already takes a REFERENCE RULE as its second edge** (found in revision 2, probed at `50b2f85`):
    `to_rule`, "a reference rule's index (a policy rate is a constant, so the gap is the area" (engine `:14340`;
    `paintSpread` reads it at `:14417`-`:14421`; the compiler requires exactly one of `to` / `to_rule`, `:2475`-`:2477`).
    A zero `hline` plus `to_rule` may already carry A46.
- Verdict: REUSE first, then EXTEND spread only for what `to_rule` cannot carry.
  - A46: a zero `hline` plus `to_rule` is tried first. The fill's colour already defaults to the neg token
    (`const col = PS_PAL[sp.color] || sp.color || "var(--lp-neg)"`, `:14349`), but a rule edge fills the WHOLE gap
    between the line and the rule, above it and below it alike (`hi = A; lo = B`, `:14421`). The one EXTEND is a
    `side: "below" | "above"` on a rule-edged spread: the fill is clipped to where the series is on the named side of
    the rule (the dip below zero), with the bounds still the true series and the true rule.
  - Only if a named zero rule cannot be authored on the page (the axes' `hlines` / `hline`, `AXES_KEYS` `:111`), a
    `spread` may name `to: {"level": "zero"}`.
  - A45 (confirmed): the same `to_rule` + `side: "below"` against a reference rule at the PRIOR PEAK's value (the
    value read from the datum, never typed), the fill beginning at the peak (`from_index`, which the spread already
    has) and running until the series regains the level; the duration below is COMPUTED and written. Only if a
    reference rule cannot be placed at a datum's value does the spread take `to: {"level": datum}` (T10's level).
- Write set: the engine (the spread block's `side` clip for a rule edge; a level target only if `to_rule` cannot
  carry it); `build_scene_timeline_f.py` (the spread's validation: `side`, refused by name without `to_rule`);
  `effects/cards/page_species.json`; `effects/recipes/the-glowing-trough.json` (new, candidate);
  `tests/test_fill_to_a_level.py` (new); the goldens `fill-below-zero` and `fill-underwater` (new).
- Input evidence: H row 22, "one soft month in June" (take 652.69-653.73, `June` 653.89-654.76), on the customs line
  (A46 / R29); for A45, a period below a prior peak (row 9's railway index after `crashed` 77.46-77.90, the parent
  confirms).
- Constraints: the fill's bounds are the true series and the true level; a duration is computed, never typed.
  Byte-identical absent the key.
- Acceptance:
  1. Step 0: D40 12:46-13:08's frames read and logged (withdraw A46 / R29 if not seen).
  2. The fill below zero on its word.
  3. The recipe proved.
  4. One golden.
  5. A45: the fill below the prior peak's level, from the peak until regained, with its computed duration written;
     one golden `fill-underwater` on the H row the parent confirms (row 9's railway index after its crash, or a
     private test-bed beat labelled reference).
- Stop conditions: the spread's painter cannot take a rule as an edge without re-laying the perform layer (report).
- Regression: `python -m pytest content/video_engine/tests/test_fill_to_a_level.py -q`
- Expected RED (read at `50b2f85`; the probe confirms in step 1): a `spread` with `to_rule` on a zero rule, over a
  series that is above zero and then dips below it, fills BOTH the area above the rule and the dip (predicted from
  `:14417`-`:14421`: no side clip exists), and a `side` key is ACCEPTED AND IGNORED or refused as unknown (the probe
  says which); a `spread` naming `to: {"level": ...}` is refused by `_validate_page_fields` ("spread: name exactly one
  of 'to' (a second series) or 'to_rule' ...", `:2475`-`:2477`).
- Validate: `python -m pytest content/video_engine/tests/test_fill_to_a_level.py -q` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- Frame acceptance: the goldens beside D40 12:54 (`ffmpeg -ss 774 -i ".../u70oUWgVoYU/video_1080p.mp4" ...`) and BOOM
  02:23.5 and 02:49.5 (BRAVOS-FRAME `-ss 143.5`, `-ss 169.5` on `scratch/jx3Ll_full.mp4`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T22: The route map - routes lighting in turn with tokens on them; the chart beside the map and the ping frame-checked; the tilted plane DROPPED (was P69 T63)
- Status: done - lane B `28eddf5`: tokens ride a route by length, one `ping` as a place lands (CHN / D40 measured; the sonar withdrawn); golden `vecmap-route-tokens`; candidate `the-chart-beside-the-map` (R17's layout is R26-382; the framing and the ping's glow R26-383)
- Owner: implementation_luna (LANE B)
- Depends on: T11 (tokens on an edge)
- Harvest: the witnesses are thin, and each is checked before it is built:
  - v2 T33 "2.5D tilted map with routes lighting in sequence": **VERIFY.md CORRECTED it - the map is flat and the tilt
    is DROPPED.** BOOM shows "a top-down, extruded (bevel plus drop shadow) dark US state map, with no perspective":
    map 04:06.0, tower nodes pop 04:07.0, glowing double-line arcs grow out of them staggered over about 1 s
    (04:08.0-04:08.5), the same map reused for telecom at 05:22.5-05:24.5 (VERIFY.md `T33_map_a/frames/
    full_t04m09.5s_1920.png`, `T33_map_b/frames/t05m23.5s.jpg`). The routes lighting IN TURN are confirmed and support
    this slice's untilted route map; nodes popping before their arcs is the witnessed order.
  - A27 "Money tokens travel the edges" has a NEW BOOM witness (VERIFY.md): a note moving along a dashed edge at
    08:14-08:21, 08:55.5-08:57.5 and 15:11 - evidence for the tokens (T11's law) on a route.
  - R17 "Dual-lane chart + map ping": CHN (Gemini 09-10).
  - A37 "Sonar ping": "G-only in both" (CHN; D40 13:54).
  - CHN's and D40's frames ARE on disk, so step (0) reads them. P69 T63 (0) already asks for this for A37.
- Use when: USE-WHEN `:527` (T33), `:539` (A37), `:557` (R17). P69 quotes `:529` "a physical network built out over
  time", `:559` "the chart and the place on one clock" and `:541` "(unverified) an origin that keeps emitting".
- Recall: docs_find "vecmap" -> CAPABILITIES `:105` (the VECTOR MAP world: a country lights, an arc crosses by length
  with the nib, `species/vecmap.mjs` `mapFit` `:109`); docs_find "tilted map" -> CAPABILITIES `:156` (`form=tilted_line`
  is a ledger page's); `;plane=tilt` is a ledger-page option (CAPABILITIES `:155`); docs_find "ping" -> 0 map hits.
- Verdict: EXTEND vecmap.
  - Now: T11's tokens travel an `arc` (the route) by arc length. N arcs lighting on their words is REUSE, since N `arc`
    species already compile.
  - After step (0): R17 as a recipe (a map and a line page on one clock, T8b's panels or a park), and the ping as a
    `ping` option on the vecmap `stamp` / `light` (a blink, s99; never a ring on a region, E56).
  - The tilted plane is DROPPED (VERIFY.md: no perspective in BOOM's map; its only witness was Gemini's). No `;plane=`
    option on the vecmap.
- Write set: `species/vecmap.mjs` (the arc's tokens; the ping, after step 0; synced); `build_scene_timeline_f.py`
  (`_validate_vecmap_species`: `tokens`, `ping`); `effects/cards/species.json`; `effects/recipes/the-chart-beside-the-map.json`
  (after step 0); `tests/kinetics/vecmap.test.mjs`, `tests/test_route_map.py` (new); the golden `vecmap-route-tokens`
  (new).
- Input evidence: H row 22, "leaving Korea ... by the kilo" (take 625.02-626.94), and the customs line (`customs`
  627.49-627.99). Derived; the parent confirms the beat.
- Constraints: nothing is area-encoded on the map unless it is true in the flat geometry with its figure written.
  Byte-identical for every existing vecmap world (the golden `vector-map-*` unchanged).
- Acceptance:
  1. Step (0) is logged: CHN frames at the R17 / A37 instants, and D40 13:54-14:18 (`ffmpeg -ss 834 ...` onward).
     Each item is confirmed or withdrawn.
  2. Route tokens run on their word.
  3. The confirmed items are built.
  4. One golden.
- Stop conditions: step (0) withdraws R17 and A37 (the slice ships the tokens only); a tilt is proposed (refuse: it is
  dropped on VERIFY.md's frames).
- Frame acceptance, BOOM: the route strip also sits beside BOOM 04:08.0 and 05:23.5 (BRAVOS-FRAME `-ss 248.0`,
  `-ss 323.5` on `scratch/jx3Ll_full.mp4`), the flat, staggered form.
- Regression: `python -m pytest content/video_engine/tests/test_route_map.py -q`
- Expected RED (probed at `50b2f85`): an `arc` with `tokens: {n: 3}` gets no error naming `tokens` from
  `_validate_vecmap_species` - the key is ACCEPTED AND IGNORED (the only errors are the arc's own `from` / `to`
  checks). The RED test asserts tokens travelling the arc and the by-name refusal of a malformed `tokens`.
- Validate: `python -m pytest content/video_engine/tests/test_route_map.py -q` then `node --test content/video_engine/tests/kinetics/vecmap.test.mjs` then COMMON-TAIL
- Frame acceptance: the golden beside CHN's R17 frame (named in step 0) and D40 13:54 (`-ss 834`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T23: A card joins its date on the line - it reads in the plot's empty room (E65) or over the plot hovering / blurred (s124), then parks at its datum - and the proof walk (was P69 T67)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: P70 T8 committed (the dock branch); P70 T13 committed (the dock-option validation `park_at` joins); T9
  (the era tagged); T15 (`under`: the hover default and the blur option); T20 (the ✓ / ✗ on a datum)
- Harvest:
  - v2 A19 "A card docks onto the plot at its date / peak", n=4 (BUB #39; STK 8:04 "card linked to the latest peak";
    HIS 00:17; BOOM (G)): "E63 conflict (C2)" - now answered (below).
  - R4 "Proof walk with press cards at their dates" (BUB 7:22).
- BOOM evidence (VERIFY.md): A19 CONFIRMED at 00:44.5 - "The card sits in the plot's empty upper-right, with a short
  leader from the ring. It is BOOM's clean in-plot case for C16" (`R32_T36_A42_A1/frames/t00m45.0s.jpg`): the E65
  empty-room read this slice builds.
- Use when: USE-WHEN `:103` (A19), `:931` (R4). P69 quotes `:105` "a headline belongs to one date on the line, and the
  join IS the claim" and `:933` "one long line proves a pattern by walking its episodes, each with its card".
- The rulings that unblock (3): **E65** (`OPERATOR-RULINGS.md:2111`-`:2129`): the placer's second place is "the plot's
  EMPTY room ... The READ (the landing) takes the same room enlarged toward the axis at the reading scale; the PARK is
  the corner", and "a card in the plot's empty room passes both [M25, M27] because the ink is what they read" (review
  finding 3). **E99 s124 (3)** (`:3379`): a dock may land over a ledger page's plot, hovering or blurred, by the author's choice
  (the author's option); where it sits is the author's (s106).
- Recall: docs_find "park_at" -> 0 hits; docs_find "proof walk" -> CAPABILITIES `:397` (recipe cards), `:72`, `:76`.
  The dock that reads then parks: CAPABILITIES `:91` (`read` / `read_s` / `park_s`, `DOCK_OPTS` `:118`); `dockGeom`
  (engine `:6411`); `axes.marks` (a dot, a chip and a dashed leader); E65's placer and E63's `read_over_build`
  (compiler `:9222`).
- Verdict: EXTEND the dock.
  - (1) `park_at: {datum, series?}` parks the read card to a small chip AT its datum, with a leader from the chip to the
    date. The join IS the claim.
  - (2) R4 is the recipe `recipe:the-proof-walk`: T36's stretch lit, T9's era tagged, the card read and parked, T20's
    ✓ / ✗ or T50's bracket, one episode per sentence.
  - (3) **The card READS on the plot at its date (A19's own form), now built:** the read takes E65's empty room at the
    date's side of the plot (the existing placer, read, not edited), and hovers there by T15's default. Where the
    empty room cannot hold the read at the legibility floor, or the author places the read over the ink on purpose,
    the dock names `under: "hover"` or `under: "blur"` (T15) and sits over the plot; M25 / M27 report it as a WARN
    with its numbers (T15), never a refusal. P69 T67 (1)'s "the plot behind the reading card may blur" is this
    `under: "blur"` (review finding 13).
- Write set: the engine (`dockGeom`'s park target; the leader); `build_scene_timeline_f.py` (`DOCK_OPTS` `park_at`, its
  validation, after P70 T13; the parent unions the tuple); `effects/cards/dock_option.json`;
  `effects/recipes/the-proof-walk.json` (new, candidate); `tests/test_card_at_its_date.py` (new); the goldens
  `card-parks-at-its-date` and `card-reads-in-the-empty-room` (new).
- Input evidence: H row 9's railway index and its episodes (`crashed` 77.46-77.90); row 16, "right there in the
  filing" (317.04-318.54).
- Constraints: the chip lands at the datum on the ACTIVE state and follows a rescale; the read goes to the plot's empty
  room first (E65), hovering; over the ink only by the author's `under` (s124), a WARN. Byte-identical absent the keys.
- Acceptance:
  1. A press card reads in the plot's empty room at its date, hovering, then parks to its date with a leader; M25 and
     M27 pass it there.
  2. The same card with `under: "blur"` placed over the ink blurs the plot under it while it reads; M27 WARNs with its
     numbers.
  3. The proof walk is proved as a beat.
  4. Two goldens.
- Stop conditions: `dockGeom`'s park cannot target a page point without the page's live box (report; the placer's
  boxes are in `page_boxes`); the empty-room read needs an edit to E65's placer (stop; report: T23 reads it, it does
  not change it).
- Regression: `python -m pytest content/video_engine/tests/test_card_at_its_date.py -q`
- Expected RED (probed at `50b2f85`): `dock_opts({"park_at": ...})` raises "dock option 'park_at' is not one of
  arrive|mass|...|names" (refused by name); the recipe id does not exist.
- Validate: `python -m pytest content/video_engine/tests/test_card_at_its_date.py -q` then `python -m pytest -q content/video_engine/tests/test_prop_free_placement.py` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside STK 8:04 (BRAVOS-FRAME `-ss 484`) and BUB 7:22 (`frame_0037.jpg`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T24: Bars re-valued - then to now, the ratio span after it, and the ranked dim-the-rest (was P69 T72)
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (M26: the printed value and the drawn bar at every instant)
- Depends on: T0. Done: P69 T26a (`lpBarMorphs`, `ghost=yes`), T37 (`solo` on bars), T50 (a bracket on bars).
- Harvest: v2 A48 "Bar re-value" (D40 11:46-11:52 (G): $47B in 2016 -> $94B); R28 "Bar re-value, then the ratio span"
  (D40 11:22-12:06 (G)); R30 "Ranked dim-the-rest spotlight" (D40 14:22-14:50 (G); CHN t530). D40's frames are on disk,
  so step (0) checks them.
- Use when: USE-WHEN `:1059` (A48), `:1089` (R28), `:213` (R30). P69 quotes `:1061` "H row 16's "28 → 121 → 150". Keep
  the figures at the bar tops (C14)".
- Recall: CAPABILITIES (lane A) "A bar changes its own value on a compare" (T26a: `lpBarMorphs` "morphs the compared
  bar's height to the comparator's value on the compare's own clock ... A ghost of the old height appears only when the
  row names it"); `species/compare.mjs`; effects `recipe:emphasized-bar-lit`, `recipe:badge-ladder`.
- Verdict: EXTEND the compare.
  - `chart_to compare` may carry `from: <sourced value>`. The bar SHRINKS to its sourced old value, holds, then grows
    to today, with a dashed ghost level at each top and its figure AT the bar top (C14).
  - R28 and R30 are recipes.
- Write set: the engine (`lpBarMorphs` `:14102`, `lpPaintBarMorphs` `:14129`); `species/compare.mjs` (the two-key path;
  synced); `build_scene_timeline_f.py` (the compare's `from` validation: sourced, with the `src` named);
  `effects/recipes/revalue-then-the-ratio.json`, `ranked-dim-the-rest.json` (new, candidate);
  `tests/test_bar_revalue.py` (new); the golden `bar-revalue-then-now` (new).
- Input evidence: H row 16, "twenty-eight" (260.74-261.31) -> "hundred and fifty" (267.39-268.81): the 28 -> 150 bar.
  The old value's source is read off the page's series file.
- Constraints: both states' values are sourced (a `from` with no source is refused, the don't at `:1062`). M26 holds
  at every instant of the morph. Byte-identical absent `from`.
- Acceptance:
  1. Step (0): D40's A48 / R28 / R30 frames read and logged.
  2. Then -> now runs on its word, with ghost levels at each top.
  3. Both recipes proved.
  4. M26 reads the probe's value and the drawn height equal at every sampled frame.
  5. One golden.
- Stop conditions: M26's probe cannot read a bar mid-morph (report; the reviewer decides whether T24 carries the probe
  change).
- Regression: `python -m pytest content/video_engine/tests/test_bar_revalue.py -q`
- Expected RED (probed at `50b2f85`): `_validate_metric_comparator` names no `from` key - a valid compare carrying
  `from: 28` is ACCEPTED AND IGNORED; neither recipe id exists. The RED test asserts the then-to-now morph and the
  refusal of a `from` with no source.
- Validate: `python -m pytest content/video_engine/tests/test_bar_revalue.py -q` then `python -m pytest -q content/video_engine/tests/test_bar_value_morph.py` then `node --test content/video_engine/tests/kinetics/compare.test.mjs` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden and a strip over the morph, beside D40 11:46-11:52 (`-ss 706`, `-ss 712`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T25: The scale-out reveal and the projected overtake (was P69 T74)
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (E77: a forecast labelled; the rank computed)
- Depends on: P70 T3 committed (`buildLedgerBars`); T16 (the projection grammar: `label`, `tier`)
- Harvest: v2 A50 "Scale-out reveal" (D40 15:02-15:06 (G): $120B, "18th Largest Holder"); A51 "Projected overtake"
  (D40 15:18-15:30 (G)); R31 (A50 + A51). The harvest (`:142`): "the composition is unproven". D40 step (0).
- Use when: USE-WHEN `:1065` (A50), `:851` (A51), `:863` (R31).
- Recall: effects `species:pull_back`; CAPABILITIES `:119` (`rescale`), `:120` (`extend`), `:90` (`overflow:burst`);
  effects `page_species:bracket`.
- Verdict: EXTEND.
  - A50 is REUSE: `rescale` / `extend` widening to the field, plus a rank pill. The rank is COMPUTED from the field,
    never typed.
  - A51 is NEW grammar: a bar datum `projected: {value, label, tier, src}`, drawn hatched or dashed as a projection
    (S3), with a bracket to #1.
  - R31 is a recipe.
- Write set: `ledger_page.py` (`BAR_FIELDS`: `projected`; `_validate_bar_fields`; the rank's computation); the engine
  (`buildLedgerBars`: the projected bar's paint, the rank pill); `build_scene_timeline_f.py` (validation only);
  `measure_page_boxes.py` (a representative; parent-merged); `effects/recipes/scale-out-then-the-overtake.json` (new,
  candidate); `tests/test_scale_out_overtake.py` (new); the golden `projected-overtake` (new).
- Input evidence: H row 18, "twenty percent" (385.21-385.89: the 20 bar alone, then the field); row 16's 690
  consensus (297.49-299.05). Derived.
- Constraints: an unlabelled projection is refused (hard); every bar in the field is sourced; the rank is computed.
  Byte-identical absent `projected`.
- Acceptance:
  1. Step (0) logged.
  2. One bar alone, then the field with its rank.
  3. The projected bar surges hatched and labelled, with a bracket to #1.
  4. The recipe proved.
  5. One golden.
- Stop conditions: the hatch / dash fights `bar_style=soft`'s hatch (report; pick the dash).
- Regression: `python -m pytest content/video_engine/tests/test_scale_out_overtake.py -q`
- Expected RED (probed by reading `_validate_bar_fields` / `BAR_FIELDS`): a bar's `projected` is refused as an unknown
  bar key (T64: "a bar key the form does not know is refused by name").
- Validate: `python -m pytest content/video_engine/tests/test_scale_out_overtake.py -q` then `python -m pytest -q content/video_engine/tests/test_stacked_combo.py` then `python -m pytest -q content/video_engine/tests/test_forms_by_honesty.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside D40 15:06 and 15:24 (`-ss 906`, `-ss 924`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T26: The push to now then the unknown, and the evidence then the conditional future; A56 rescoped - a box round the last actual move, then the projection to a dated rule (was P69 T68)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T16 (`project`); T18 (the "?" / "???"); T9 (the dated axis pill). Done: T26f (the camera free) and T36
  (the now lit).
- Harvest:
  - v2 R5 "Push to now, then the unknown", n=3 (BUB 8:22; STK 9:01 "lens + dashed "PREPARE!""; BOOM).
  - R26 "Evidence, then the conditional future", n=3 (STK 7:50-8:24; JPN 04:05-04:17; BOOM). VERIFY.md CONFIRMS
    R5 / R26 in BOOM at 16:14-18:01, **without** the push at 17:30 (no zoom there: the axis stays 1988-2028).
  - A56, **RESCOPED by VERIFY.md** (CORRECTED, Gemini 10.5 s early): the dashed box does NOT frame empty future space.
    It frames the **latest actual** PMI upswing (2025-26, lit pink) at 17:55.5-17:58.0 and leaves at 17:58.5; then a
    dashed vertical rule at June 2027, a crimson "June 2027" axis pill and a short dashed PMI extension up to the rule
    (17:59.0-18:00.5), on "could actually continue until June of 2027" (17:56.72-17:58.72). Frames: VERIFY.md
    `A56_future_box/frames/crop_t17m56.5s_box_fullres.png`, `crop_t18m00.5s_june2027_fullres.png`.
  - A NEW BOOM witness for R5 (VERIFY.md): a dashed hypothetical crash path drawn **past the plot's right edge**, with
    an underwater fill under it and a crimson "?" at 03:18-03:19 ("one could speculate regarding what could happen in
    the aftermath", 03:17.04; `A17_forward_0320/frames/t03m19.0s.jpg`).
- Use when: USE-WHEN `:421` (A56), `:427` (R5), `:433` (R26). A56's card copies the rescoped form: "the sentence
  projects the latest move forward to a date; the box names the move, the rule names the date".
- Recall: docs_find "future box" -> 0 hits; docs_find "scenario" -> 0 capability rows. Effects
  `recipe:estimate-opens-as-a-wedge`, `focus_zoom`, `chart_to:rescale` (CAPABILITIES `:119`); `span` (CAPABILITIES
  `:104`, a band between x-fraction edges) and `lit_stretch` for the stretch the box names.
- Verdict: EXTEND (recipes on T16, T18 and T9). Both recipes compose existing cards: s70, a recipe is a timing.
  - R5: a rescale or a push lands on today, then T16's labelled path or T18's "???" runs off the edge, never a
    continuous push (E59).
  - R26: the evidence held ~10-14 s, then the projection in a visibly new grammar.
  - A56 (rescoped) is a recipe plus ONE form: a dashed BOX round the last actual stretch's ink (REUSE `span` if a
    `form: "box"` bounded by the stretch's own data can carry it; else a NEW `stretch_box` page-species block), which
    leaves; then T16's projection to a DATED vertical dashed rule with T9's `axis_tag` pill naming the date. The date
    and the projection carry their tier (E77).
- Write set: `effects/recipes/push-to-now-then-the-unknown.json`, `evidence-then-the-conditional-future.json`,
  `box-the-move-then-project-to-the-date.json` (new, candidate); `content/video_engine/projects/_proofs/p71-recipes/proof_t26.py`
  (new); the engine (the `span` box form, or a NEW `stretch_box` block + dispatch line - Deviation 7's union);
  `build_scene_timeline_f.py` (its validation); `tests/test_stretch_box.py` (new); the golden `box-the-last-move`
  (new).
- Input evidence: H row 16, "four hundred and eighty ... six hundred and ninety" (293.80-299.05); row 23, "booked solid
  through twenty twenty-six" (724.21-726.45) - the box round the latest actual move, then the dated rule at 2026.
- Constraints (C15): every projected path names itself a projection and its tier; the push lands on a named datum
  (E59); the box bounds only drawn actual data (it never frames empty space); the dated rule's date is sourced.
- Acceptance:
  1. Both recipes are proved as beats, and the parent reads their strips.
  2. A56 rescoped: the box lands round the last actual stretch, leaves, then the dashed projection draws to the dated
     rule and its pill; one golden.
- Stop conditions: R5's push needs a camera path M14 refuses (report the refusal; the rescale form is used); `span`
  cannot bound a stretch's ink without a new form (build `stretch_box`, say so).
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the three recipe ids exists in `content/video_engine/effects/recipes/`; a `span` with
  `form: "box"` is refused or ignored (the probe says which, step 1).
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check` then `python -m pytest -q content/video_engine/tests/test_recipe_use_when.py` then `python -m pytest -q content/video_engine/tests/test_stretch_box.py` then `python content/video_engine/projects/_proofs/p71-recipes/proof_t26.py` then COMMON-TAIL
- Frame acceptance: the proof strips beside STK 9:01 (`-ss 541`), STK 8:10 (`-ss 490`) and JPN 04:10 (`-ss 250`); the
  A56 strip beside BOOM 17:56.5 and 18:00.5 (BRAVOS-FRAME `-ss 1076.5`, `-ss 1080.5`); R5 beside BOOM 03:19
  (`-ss 199.0`).
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T27: The lead-lag bracket across two series; the travelling ring and the phase slide DROPPED (was P69 T75)
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (a measured lag computed; s102 on unlike scales)
- Depends on: P70 T5 committed (it owns `paintBracket`); T13 (s102's conditions for two unlike scales)
- Harvest:
  - v2 A53 "Lead-lag bracket between two series' peaks", n=2 (BUB 4:35 "the lag bar between waves"; BOOM). **VERIFY.md
    CONFIRMS A53 in BOOM twice**: a crest-to-crest "1-2 Years" bracket on the schematic at 16:12.5 (on "leads the
    business cycle by roughly 1 to two years", 16:09.92-16:12.08), and a "1.5 Years" ELBOW bracket from a ring on the
    yield-curve end up to the PMI at 16:25.5-16:27 - the two-series form this slice builds (VERIFY.md
    `A54_phase_slide/frames/t16m13.0s.jpg`, `A53_A15_bracket_T11_band/frames/t16m27.0s.jpg`).
  - A52 "The ring travels": **DROPPED** (VERIFY.md NOT FOUND). Two independent rings 39 s apart (13:37.0 on the PMI
    peak, 14:16.0 on the lagging peak) with a chart reset between them; no travel at 0.5 s resolution.
  - A54 "Phase-shift slide": **DROPPED** (VERIFY.md NOT FOUND). The lead wave is path-drawn already offset
    (15:53.0-15:56.0); nothing slides along x; the lag is named by the crest-to-crest bracket (A53, above).
- Use when: USE-WHEN `:925` (A53).
- Recall: docs_find "lead-lag" -> only the BUB reference report (P69 T75). Effects `page_species:bracket` (CAPABILITIES
  `:77`, "a measured vertical span between two data").
- Verdict: EXTEND the bracket (A53): `bracket {from: {series, datum}, to: {series, datum}}` spans two series' peaks,
  horizontally or as BOOM's elbow (from a datum on one series up to the other), and its label is the lag COMPUTED from
  the two x and written. No ring travel and no slide are built.
- Write set: the engine (`paintBracket`'s two-series span); `build_scene_timeline_f.py` (the bracket validator's
  two-series branch); `effects/cards/page_species.json` (the option); `tests/test_lead_lag.py` (new); the golden
  `lead-lag-bracket` (new).
- Input evidence: H row 9, the ring from the 2000 7 % crossing (`seven percent` 81.42-82.14) to AI's 8 % (`just crossed
  eight` 87.40-88.67), as the lag between the two series. Derived.
- Constraints: the lag is computed (a typed lag that disagrees is refused); two series on unlike scales need s102's
  `claim` (T13). Byte-identical absent the two-series form.
- Acceptance:
  1. The two-series bracket draws with its computed lag (level and elbow forms).
  2. A52 and A54 are recorded as dropped (VERIFY.md), in this plan and P69's carrier map (T0).
  3. One golden.
- Stop conditions: P70 T5's brace branch reorders the bracket validator so the two-series form cannot branch first
  (report).
- Regression: `python -m pytest content/video_engine/tests/test_lead_lag.py -q`
- Expected RED: a bracket naming two series is refused (the bracket joins two data of one series, harvest `:108`;
  the probe confirms the message in step 1).
- Validate: `python -m pytest content/video_engine/tests/test_lead_lag.py -q` then `python -m pytest -q content/video_engine/tests/test_rings_on_vertices.py` then `python -m pytest -q content/video_engine/tests/test_forms_by_honesty.py` then COMMON-TAIL
- Frame acceptance: the golden beside BUB 4:35 (`frame_0023.jpg`) and BOOM 16:13.0 and 16:27.0 (BRAVOS-FRAME
  `-ss 973.0`, `-ss 987.0` on `scratch/jx3Ll_full.mp4`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T28: The line painter - the trace before the furniture, and the line changing ink at a point (was P69 T76; F18 is done)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T13 and T16 (`buildLedgerLine`, waves 3-4)
- Harvest: v2 A41 "Trace first, furniture after" (HIS 00:04-00:06, 05:50-05:51.5); A21 "The line changes ink at a
  point", n=3 (BUB 19:45; HIS 05:58 "red after the peak"; BOOM (G)). F18, the white-hot core, is DONE: s117 says T37b
  "takes T76's white-hot core (harvest F18) forward", and lane A CAPABILITIES has "THE LINES BLOOM" (`LP_HOT`: "core
  0.5 of the stroke, mix 0.55 toward white").
- BOOM evidence (VERIFY.md): A21 CONFIRMED - the line turns red after the crest at 09:58-10:04 and green again at
  10:08 (no orange apex).
- Use when: USE-WHEN `:347` (A41), `:341` (A21). P69 quotes `:349` "the SHAPE is the hook" and `:343` "a regime changes
  at a named moment".
- Recall: effects `page_enter:axes`, `recipe:hook-opens-on-the-axes`; `LEDGER_ENTERS` (compiler `:59`, "enter=axes ...
  the charcoal page lands with its ground, its ruled line, its title, its labels and its AXES already drawn");
  `highlight_from` (`AXES_KEYS` `:111`, a static relight).
- Verdict: EXTEND.
  - A41 is a NEW `trace` page enter in `LEDGER_ENTERS`: the series draws on the bare ground first, then the title,
    axes and key land. E73 still fixes row 1 on its axes, so this is opt-in for a row whose SHAPE is the hook.
  - A21 adds `ink_from: {x, color}` to a series: the stroke splits at x on its word. A declared colour wins over the
    sign default only where it does not lie (E53 s7, E28).
- Write set: `ledger_page.py` (the series `ink_from`, its check); the engine (`buildLedgerLine`'s stroke split; the
  `trace` enter in the page-enter law); `build_scene_timeline_f.py` (`LEDGER_ENTERS` `trace`, `:59`);
  `effects/cards/page_enter.json`, `page_species.json`; `tests/test_line_painter.py` (new); goldens `enter-trace`,
  `ink-from-crash` (new).
- Input evidence: H row 9, "crashed" (77.46-77.90): the railway line turning red after the peak.
- Constraints: the split recolours the drawn stroke and its bloom (T37b's layers) together; an `ink_from` that paints a
  fall in the pos ink is refused (E28). Byte-identical absent both.
- Acceptance:
  1. The trace-first enter draws the line, then the furniture.
  2. The ink changes at x on its word.
  3. One golden per form.
- Stop conditions: the split cannot share T37b's bloom filter pieces without duplicating them per segment (report the
  cost).
- Regression: `python -m pytest content/video_engine/tests/test_line_painter.py -q`
- Expected RED (probed at `50b2f85`): `enter=trace` is not one of `LEDGER_ENTERS` (`:59`) and is refused; a series'
  `ink_from` is ACCEPTED AND IGNORED by `ledger_page.validate` (returns `[]`). The RED test asserts the split and the
  refusal of an `ink_from` that paints a fall in the pos ink.
- Validate: `python -m pytest content/video_engine/tests/test_line_painter.py -q` then `python -m pytest -q content/video_engine/tests/test_line_bloom.py` then `python -m pytest -q content/video_engine/tests/test_longform_profile.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the goldens beside HIS 00:05 (BRAVOS-FRAME `-ss 5`) and HIS 05:58 (`-ss 358`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T29: Glow edges - a glow outline on a bar or region; F14 DROPPED; the stamp slab retired (was P69 T77)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T12 (one light grammar: `lit`). P70 T1b (the stamp's paint) is committed at `50b2f85`; T29 draws no
  stamp ring, so it does not wait on P70 T1c.
- Harvest:
  - v2 F2 "Glow outline on a region or bar", n=3 (BUB #3; CHN t530; D40 14:30 (G)): buildable.
  - F14 "Glowing red perimeter on a headline card": **DROPPED (the architect's call, as the parent asked).** VERIFY.md
    CORRECTED it: there is no glow perimeter. BOOM's white press cards carry "a hard crimson edge on the right and
    bottom (an offset slab, about 6 px at 1080)" and a crimson highlight box on the key phrase (00:44.5-00:51,
    18:01.5-18:10; `F14_card_perimeter/frames/crop_t00m47.0s_fullres.png`). Why drop rather than build the slab:
    (a) the phrase highlight is F5, which we already HAVE (the press card's highlighted phrase, T35's R34 uses it);
    (b) the offset slab is a card STYLE, not a verb that carries a sentence - it would restyle our reviewed press card
    (CAPABILITIES `:101`), which the harvest rule forbids (harvest, never replace a locked mechanism); (c) no H
    sentence asks for an alarm on a card. If the operator wants Bravos's card edge, it is a one-line press-card style
    option filed then, not a P71 slice.
  - F19 "Beveled stamp slab", BOOM 14:04 (G) only: **retired**. It conflicts with s121 ("a stamped CHIP, BADGE or
    VERDICT stamp lands as a seal") and s123 ("a seal is gold"). The retirement stands on s121 (1) alone (draft 1's
    clause giving the seal s92's resting shadow is dropped: s92 is about props, and s128 (2) keeps the shadow a prop's).
- Use when: USE-WHEN `:195` (F2), `:807` (F19, retired). F14's entry (`:139`) is retired with it.
- Recall: CAPABILITIES `:90` (the burst's glow); effects `recipe:emphasized-bar-lit`; CAPABILITIES `:101` (the press
  card). docs_find "bevel" / "stamp slab" -> 0.
- Verdict: EXTEND. A `glow` page species draws an outline in the named bar's or region's ink. Held, it is an annotation
  (0 events, s91); blinking, it is motion (s99). Never the move when a thing should arrive (s71).
- Write set: the engine (a NEW `glow` block); `build_scene_timeline_f.py` (NEW `_validate_glow`);
  `effects/cards/page_species.json`; `tests/test_glow_edges.py` (new); the golden `glow-outline-bar` (new). No press
  dock `perimeter` key (F14 dropped).
- Input evidence: H row 18, "twenty percent" (385.21-385.89): the 20 bar lit.
- Constraints: one glow per row by default (the don't at `:142`); a glow on a thing that should arrive WARNs (s71).
  Byte-identical absent the species.
- Acceptance:
  1. The glow outline lands on its word; held = 0 events, blink = motion.
  2. F19 and F14 are marked retired / dropped in this plan and in P69's carrier map (T0).
  3. One golden.
- Stop conditions: the outline duplicates T37b's bloom pieces on a bar (report; reuse them).
- Regression: `python -m pytest content/video_engine/tests/test_glow_edges.py -q`
- Expected RED: `glow` is refused as an unknown species.
- Validate: `python -m pytest content/video_engine/tests/test_glow_edges.py -q` then `python -m pytest -q content/video_engine/tests/test_gate_motion_density.py` then COMMON-TAIL
- Frame acceptance: the golden beside BUB #3 (`frame_0003.jpg`) and CHN t530 (the CHN frame at 530 s).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T30: The longform chrome finish - the key chip and the end badge turn accent on `solo`, the two-line source, the title capsule (was P69 T78)
- Status: pending
- Owner: junior_developer (LANE B)
- Depends on: P69 T37c committed (the title's size, glow and face: s122 amended), because S11 draws round the title
  T37c sets
- Harvest: v2 S9 "The legend chip turns accent when its series is isolated" (STK 4:14); S10 "Two-line source" (CHN
  spec, BOOM, D40); S11 "The chart title sits in an accent capsule" (BOOM, D40): D40 step (0) for S11.
- BOOM evidence (VERIFY.md): S9 has NEW BOOM witnesses - each series' legend entry turns into a crimson pill as it
  is named, 00:55, 01:04, 01:07, 15:32 ("PMI"), 15:58.5 ("Yield Curve") (`R32_A2_A12_dock/frames/t00m56.0s.jpg`).
  S10 CONFIRMED throughout ("Date: As of August 2026. / Source: Bloomberg Finance L.P., Bravos Research."). S11 is
  CORRECTED: BOOM's chart TITLES are plain pink text; some SUBTITLES sit in a crimson capsule (07:56, 12:28), and the
  schematic's "Business Cycle" title sits in a dark capsule. So step (0)'s D40 read decides between `;title=capsule`
  and `;sub=capsule`; if D40 also shows only the subtitle capsule, the option is `;sub=capsule`.
- Recall: CAPABILITIES (lane A) "Badges are the key" (the rail); "SOLO" (T37: "It re-inks only the page's own marks ...
  never the key"), which is the gap S9 names. `badges_for` (ledger_page); T8's longform column.
- Verdict: EXTEND.
  - S9: `paintSolo` (`species/solo.mjs` `:100`) also re-inks the named series' rail pill AND its end badge (the end
    tag's chip; P69 T78 (1): "its key chip and end badge take the accent", review finding 13) to its accent and mutes
    the others, on the solo's own clock.
  - S10: `;source=two_line` under longform.
  - S11: `;title=capsule`. It must render beside T37c's orange-glow title, since s122 settled the title's colour and
    glow. The capsule is an option, never a default, and the parent reads it beside T37c's pick.
- Write set: `species/solo.mjs` (`paintSolo`: the rail pill and the end badge; synced); `ledger_page.py` (the longform
  options); the engine: `buildLedger` (`:9015`) only - the source foot (`.lp-src`, `:9129`) for the two-line form and
  the capsule round `.lp-title` (`:9125`), named so T30 and T31 are provably disjoint (review's wave check);
  `measure_page_boxes.py`; `tests/test_longform_chrome.py` (new). No new form, so no golden: the parent reads the off
  / on pages.
- Constraints: M28 (text on text) clean; the two-line source wraps inside the safe column, never into the caption strip;
  byte-identical absent the options.
- Acceptance:
  1. The solo lights its rail pill and its end badge; the others mute.
  2. The two-line source and the capsule render off and on.
  3. M28 is clean.
- Stop conditions: T37c changes the title's box after this slice is briefed (re-brief).
- Regression: `python -m pytest content/video_engine/tests/test_longform_chrome.py -q`
- Expected RED: a solo'd series' rail pill and end badge keep their own colour; `source=two_line` and `title=capsule`
  are unknown page options (the probe says whether refused or ignored, step 1).
- Validate: `python -m pytest content/video_engine/tests/test_longform_chrome.py -q` then `python -m pytest -q content/video_engine/tests/test_solo.py` then `python -m pytest -q content/video_engine/tests/test_longform_profile.py` then `python -m pytest -q content/video_engine/tests/test_fed_chart_readability.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the off / on pages beside STK 4:14 (BRAVOS-FRAME `-ss 254`) and D40's S11 frame (named in step 0).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T31: Labels - a category pill over axis-less story bars, logos as data labels, the bar ladder that ends on a membership bar (was P69 T79)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T25 (`buildLedgerBars`, wave 6); P70 T2 (it owns `buildLedgerLine`'s end-tag writes, where the line-end
  logo goes). Done: T45 (the membership stack), T10 (the key rail).
- Harvest: v2 S5 "Story bars: no axis, a category pill" (3; s97 asks for it); S6 "Logos as data labels" (BUB, BOOM);
  R2 "Bar ladder with a membership bar" (BUB 0:48).
- BOOM evidence (VERIFY.md): S6 (logos as data labels) is NOT FOUND in BOOM - "Logos only ever appear as chips in
  rows and docks, never as labels on data". S6 now stands on BUB alone; the parent weighs that at HG1's adoption
  question.
- Use when: USE-WHEN `:207` (R2). S5 and S6 are STYLE items with no guide entry (P69).
- Recall: CAPABILITIES (lane A) "The membership stack" (T45: `members`, a cutout under 48 px gives way to its name, "a
  logo the catalogue lacks is dropped with a WARN - never invented"); `ledger_page` `MEMBER_FIELDS` (`:281`),
  `left_gutter` (the story y-axis reservation); effects `recipe:badge-ladder`.
- Verdict: EXTEND.
  - S5: a story page `axes: "none"` with a category `pill` per bar and its value badge. The written values state the
    scale.
  - S6: a bar or series `logo: "prop:<id>"`, only where the rights spec allows - under the bar, or AT THE LINE END
    as a series' end-tag label with its name kept in the key (P69 T79 (2), review finding 13). `docs/content-video-engine/11-ARCHIVAL-ASSET-AND-CITATION-SPEC.md`
    §4 ("Logos and organization marks require recorded permission; otherwise use text", quoted at `ledger_page.py:274`)
    governs it.
  - R2 is a recipe.
- Write set: `ledger_page.py` (story `axes: none`, `BAR_FIELDS` `pill`, `logo`, a series `logo` key); the engine
  (`buildLedgerBars`'s story branch; `buildLedgerLine`'s end-tag write for a series `logo`, after P70 T2); `build_scene_timeline_f.py` (validation only); `measure_page_boxes.py`; `effects/cards/page_builder.json`;
  `effects/recipes/bar-ladder-to-membership.json` (new, candidate); `tests/test_story_bar_labels.py` (new); the golden
  `story-bars-pills` (new).
- Input evidence: H rows 14 and 19 (the breakthrough bars as story bars; `twenty years` 432.35-432.96); row 16 (the 150
  of the five borrowers).
- Constraints: an axis-less page writes every value and its bars stand from zero in true proportion (hard); a logo
  without recorded permission falls back to its name with a WARN. Byte-identical absent the keys.
- Acceptance:
  1. The axis-less story page with its pills.
  2. A logo label where it is permitted, under a bar and at a line end (the name kept in the key).
  3. The ladder recipe proved.
  4. One golden.
- Stop conditions: `axes: none` collides with `left_gutter`'s story-axis reservation (report; refuse the pair by name).
- Regression: `python -m pytest content/video_engine/tests/test_story_bar_labels.py -q`
- Expected RED: `axes: none` is refused on a story page; a bar's `logo` / `pill` is refused as an unknown bar key
  (`BAR_FIELDS` `:476` refuses by name, T64); a series' `logo` is ACCEPTED AND IGNORED by `ledger_page.validate` (the
  probe confirms, step 1).
- Validate: `python -m pytest content/video_engine/tests/test_story_bar_labels.py -q` then `python -m pytest -q content/video_engine/tests/test_membership_stack.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside BUB 0:48 (`frame_0005.jpg`) and HIS 11:01 (BRAVOS-FRAME `-ss 661`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Evidence: pending

### T32: The camera - a pedestal down through the waterline, and the magnifier lens (was P69 T80)
- Status: done - lane B `d7cf74d`: the pedestal (camera.mjs) and the lens (zoom default 1 - Bravos's glass does not magnify); golden `lens-over-the-line`; the sky above y 0 is T34's; the lens over the tags is R26-387
- Owner: implementation_luna (LANE B), then reviewer (M14: the camera never moves over a build)
- Depends on: T0. Done: T26f (the camera free of the chrome). **The circle is broken here:** P69 T80 depended on T44's
  hidden base, and T44's hidden base depended on T80. T32 builds the pedestal on its own proof (a stage taller than the
  frame), and T34 composes it.
- Harvest: v2 A33 "Pedestal down through the waterline" (BUB 0:00); A57 "Magnifier lens over the chart", n=2 (STK 9:01
  "PREPARE!"; BOOM (G)): buildable on STK.
- BOOM evidence (VERIFY.md): A57 CONFIRMED at 06:28, 09:24 (with a camera crop), 11:07 and 12:32
  (`T4_T15_split_A57/frames/t06m28.0s.jpg`); A64 / A65 (a continuous push, a tracking pan) are NOT FOUND - only
  discrete eased punch-ins (09:24, 15:21, 16:22.5), which backs C11 and the pedestal's "after the settle" rule.
- Use when: USE-WHEN `:489` (A33), `:1103` (A57). P69 quotes `:1106`'s don't, "invent zoomed values".
- Recall: `kinetics/camera.mjs` (CAPABILITIES `:89`, "one persistent 2D similarity"); `focus_zoom`; the blur-zoom's
  magnify (CAPABILITIES `:71`). docs_find "pedestal" -> 0 hits.
- Verdict: EXTEND (the pedestal: a pure vertical move of `look` in `kinetics/camera.mjs` over a stage taller than the
  frame, after the build has settled) + NEW (a `lens` species: a circular magnifier that resamples the SAME series at
  k x inside the circle and invents no values).
- Write set: `kinetics/camera.mjs` (the `pedestal` key; synced); `species/lens.mjs` (new, synced); the engine (its
  region); `build_scene_timeline_f.py` (the camera key's validation, NEW `_validate_lens`); `gate_motion_density.py`
  (the camera mirror, only if the pedestal changes what M14 reads); `effects/cards/species.json`, `camera.json`;
  `tests/kinetics/camera.test.mjs`, `tests/test_pedestal_and_lens.py` (new); the golden `lens-over-the-line` (new).
- Input evidence: H row 22, "one soft month in June" (652.69-653.73) on the long customs line (the lens); row 16,
  "lease commitments" (307.48-308.85; T34's hidden base, which the pedestal serves).
- Constraints: the pedestal and the lens change the view, never the data; the gate's camera mirror agrees (M14);
  seek-safe. Byte-identical absent both.
- Acceptance:
  1. A pedestal key moves `look` vertically after the settle; a pedestal over a build is refused (M14).
  2. The lens magnifies a region with the same series' points.
  3. One golden (the lens).
- Stop conditions: the pedestal needs a stage taller than the frame that the page layout cannot provide (report; T34
  then carries the iceberg's layout).
- Regression: `python -m pytest content/video_engine/tests/test_pedestal_and_lens.py -q`
- Expected RED: a camera `pedestal` key is refused as unknown; `lens` is refused as an unknown species.
- Validate: `python -m pytest content/video_engine/tests/test_pedestal_and_lens.py -q` then `node --test content/video_engine/tests/kinetics/camera.test.mjs` then `python -m pytest -q content/video_engine/tests/test_camera_keeps_the_page.py` then `python -m pytest -q content/video_engine/tests/test_gate_motion_density.py` then COMMON-TAIL
- Frame acceptance: the golden beside STK 9:01 (BRAVOS-FRAME `-ss 541`); the pedestal strip beside BUB 0:00-0:48
  (`frame_0001.jpg`-`frame_0004.jpg`).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

### T33: The inset echo - the plot parks, the historical twins stack BESIDE it, then the "?" (was P69 T54; RESCOPED by BOOM's frames)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T18 (the "?"); done: P69 T8b (panels), T10c (the chart card for its displayed size), the park
  (`chart_to park`, CAPABILITIES `:124`)
- Harvest: v2 T40 "Inset echo: a historical twin mini-chart dropped into the plot's empty room" and R36 "Inset echo,
  then "?"", BOOM 08:44-08:50 (G). **VERIFY.md CORRECTED both (the twin is BESIDE the plot, not in it):** "The plot
  parks left (shrinks about 10%). Two twin mini-charts stack in the right column **beside** the plot: "Utility Companies
  1929" at 08:45.5, then "Telecom Companies 2000" at 08:48. Both leave at 08:51.5 and the plot restores. A crimson "?"
  lands to the right of the plot, by the RHS axis, at 08:52.5 and holds to about 08:55." Narration: "from utility
  companies in 1929 or away from telecom companies in 2000" (08:45.20-08:48.56); "?" on "the most important question"
  (08:51.44). Frames: VERIFY.md `T40_R36_inset_echo/frames/t08m45.5s.jpg`, `t08m48.0s.jpg`, `t08m51.0s.jpg`,
  `t08m52.5s.jpg`. The only in-plot inset BOOM shows (03:59-04:03) is a schematic idea sketch, not a historical twin;
  **no in-plot twin is witnessed, so none is built.** The park-and-restore is also A24 / A58's true instance (VERIFY.md:
  01:23, 08:45.5-08:51.5).
- Use when: USE-WHEN `:293` (T40), `:401` (R36). P69 quotes `:295` "the shape rhymes, and the rhyme is the argument"
  and `:296`'s don't, "over drawn ink (E63); without the twin's own source". The beside form is C16's own fallback ("or
  a panel beside it instead"), so it needs no placement ruling; E65 is not needed either.
- Recall: docs_find "inset" -> CAPABILITIES `:40` (the slide transition only), 0 chart-inset rows. The pieces:
  `chart_to park` (CAPABILITIES `:124`, "the chart makes room by one affine transform"); the chart card
  (`chart_card.py`, T10c's `card` profile); the dock `stack` option (`DOCK_OPTS` `:118`); T18's `unknown` "?".
- Verdict: REUSE, as a recipe plus at most one option: `recipe:inset-echo-then-the-question` - the page parks on its
  word; two chart-card docks (each the twin's OWN series file and source, titled with its era: "Utility Companies
  1929") stack in the freed column on their words; both leave and the page restores; T18's "?" lands beside the plot
  on "the question". A bounded check first: can two chart-card docks stack in the parked page's freed column with
  today's `stack` / `place` options? If not, the one option added is the dock's stack-in-the-freed-column placement,
  and nothing else.
- Write set: `effects/recipes/inset-echo-then-the-question.json` (new, candidate);
  `content/video_engine/projects/_proofs/p71-recipes/proof_t33.py` (new); only if the check fails, the compiler's dock
  placement for a stack beside a parked page (`dock_place`, `:7301`, after P70 T8) and `tests/test_inset_echo.py`
  (new).
- Input evidence: H row 9 (the railway mania, then the internet's crossing: the twins "Railways 1845" and "Internet
  2000" beside the parked AI page) or row 12 (the three manias); the parent confirms the beat. Each twin's series is a
  committed evidence object with its own source (never re-typed).
- Constraints: each twin states its own scale and unit and never borrows the host's axis (P69 T54 (2), E79); the twin
  is drawn from its own sourced series (refused otherwise); the host page is parked, never covered.
- Acceptance:
  1. The page parks, two twins stack beside it on their words, leave, the page restores, and the "?" lands beside the
     plot; proved as a beat and read by the parent.
  2. The bounded check's result is logged; if an option was added, it is byte-identical absent it.
- Stop conditions: a twin has no committed sourced series (stop: never invent one); the park leaves no column wide
  enough for a legible card at T10c's floor (report the numbers).
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: `recipe:inset-echo-then-the-question` does not exist in `content/video_engine/effects/recipes/`.
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check` then `python -m pytest -q content/video_engine/tests/test_recipe_use_when.py` then `python content/video_engine/projects/_proofs/p71-recipes/proof_t33.py` then COMMON-TAIL
- Frame acceptance: the proof strip beside BOOM 08:45.5, 08:48.0 and 08:52.5 (BRAVOS-FRAME `-ss 525.5`, `-ss 528.0`,
  `-ss 532.5` on `scratch/jx3Ll_full.mp4`).
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T34: The Bravos recipes - the ratio in the gap, the epoch walk, peak-fall-magnitude, isolate-then-quantify, the formula by its words, the hidden base; plus `the-bar-halves-its-number` (was P69 T44)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T9 (the axis tag), T10 (the level join), T24 (the re-value), T29 (the glow, for R1), T32 (the pedestal,
  for R1), P70 T6 (the equation, for R25), T21 (A45's underwater fill, for the epoch walk) and P70 T10 (A44's in-place
  swap, for the epoch walk; the parent updates P70 T10 as unblocked). Done: T36, T37, T47, T50 (the bracket on bars;
  R26-272 closed), T26a (the bar moves; R26-273 closed), T64 (`segments`).
- Harvest (§6 ranks 5, 8, 10, 13, 14, 15; the P69 T44 stub):
  - `the-ratio-read-in-the-gap` + the group bracket (R20, A15, A16, R28): STK 1:54-2:18, HIS 11:01, CHN 18:10 (A16).
  - `the-epoch-walk` (R22): DOM 06:11-06:38, JPN 01:35, BUB 7:22, and BOOM 02:22.5-03:14 (VERIFY.md CONFIRMS R22;
    its two dashed boxes land in sequence, 02:59 then 03:00). Its A44 / A45 parts are **UNBLOCKED** by VERIFY.md: A44
    has ONE clean in-place witness, 02:27.0-02:27.5 ("Dot-Com Bust" rolls into "Lost Decade" in the same pill, on
    "gave way to a lost decade"; the 02:47-02:49 instance is exit, gap, then a new pill, and is NOT cited as
    in-place); A45 is T21's underwater fill (02:23.0, 02:48.5).
  - `peak-fall-magnitude` (R18): STK 0:12-0:18, HIS 05:58-06:02, JPN 01:36; BOOM CONFIRMED by VERIFY.md with a NEW
    witness for the magnitude: the value pill COUNTS, "-66%" at 14:22.5 to "-80%" at 14:23 (a number re-valuing in
    place; `A52_ring_travel_R18/frames/t14m22.5s.jpg`, `t14m23.0s.jpg`). The recipe may let the magnitude count up
    by an existing card (`ticker`, or T24's re-value), evidence only; no new form.
  - `isolate-then-quantify-the-tail` (R24): JPN 05:25-05:45, STK 4:10-4:14; BOOM 16:36-16:42 (VERIFY.md A12 / R24:
    the inversion stretches lit, a "Yield Curve Inversion" pill at 16:40.5).
  - `the-formula-by-its-words` (R25): DOM 09:30-09:39.
  - `the-hidden-base` / the true iceberg (R1, T1, A33): BUB 0:00-0:48; s100 clears the iceberg under its two tests.
- Use when: USE-WHEN `:937` (R20), `:943` (R22), `:813` (R18), `:825` (R24), `:727` (R25), `:501` (R1), `:441` (T1).
- Recall:
  - docs_find "ratio read in the gap" -> CAPABILITIES (lane B `:241`, "P69's candidate recipes"): "Two were withdrawn:
    `the-bar-halves-its-number` (R26-273, now buildable after T26a) and `the-ratio-read-in-the-gap` (R26-272)". Both
    blockers are now closed, by T26a and T50.
  - docs_find "epoch walk" / "isolate then quantify" -> 0 hits; docs_find "peak fall magnitude" -> the STK chart-watch
    report; docs_find "formula by its words" -> 1 hit; docs_find "hidden base" / "iceberg" -> the harvest and USE-WHEN
    only.
- Verdict: REUSE. Each recipe is ordered card ids with offsets (s70: a recipe is a timing that composes), status
  `candidate`, `count: 0`, with its `use_when`. Two bounded discoveries sit inside the slice, each with a stop:
  - **The group bracket (A16):** does T50's bracket on a bars page span a GROUP (its first bar to its last)? If not,
    stop and file a bracket option. Do not write it here, because the bracket is P70 T5's function.
  - **The iceberg (T1 / R1):** can T64's `segments` (the visible part and the hidden part), a named `hline` waterline,
    T32's pedestal and T29's glow compose a true-proportion iceberg with its figures written (s100 (a), (b))? If not,
    stop and file a form slice. Never invent a form inside a recipe.
- Write set: `content/video_engine/effects/recipes/{the-ratio-read-in-the-gap,the-epoch-walk,peak-fall-magnitude,isolate-then-quantify-the-tail,the-formula-by-its-words,the-hidden-base,the-bar-halves-its-number}.json`
  (new, candidate); `content/video_engine/projects/_proofs/p71-recipes/proof_t34.py` (new; its builds are gitignored
  `build-lab-*`). The catalogue's generated files are regenerated by the parent.
- Input evidence (the H rows the harvest names; take times in `$SP/p71-plan/take-times.txt`):
  - ratio: row 16, 28 -> 150 (260.74, 267.39);
  - epoch walk: row 9 (79.80, 87.40);
  - peak-fall: row 9, "crashed" (77.46);
  - isolate: row 18's 20 (385.21);
  - formula: row 18, "if the AI names fall by half, that erases ten percent" (`fall by half` 402.38-403.48, `ten
    percent` 404.19-404.86; P70 T6's golden beat);
  - hidden base: row 16, "lease commitments" (307.48-308.85);
  - the halving: row 18, `fall by half` (402.38).
- Constraints: no new grammar; every member card exists (the catalogue check); no chart_to in an approved-cut pattern
  that E96 / E97 forbids (the one-shot floor's rules); each proof beat sits on its H row (s60).
- Acceptance:
  1. Seven recipe files, each validated by the recipe schema with its `use_when`.
  2. Each is proved as a beat, the strip written to `$SP/p71-t34/frames/` and read by the parent. A proof that reads
     wrong is withdrawn, not tuned.
  3. The two discoveries' results are logged.
  4. No golden.
- Stop conditions: either discovery fails (file the slice, ship the rest); P70 T6 is not merged (ship five, and
  `the-formula-by-its-words` waits).
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the seven recipe ids exists in `content/video_engine/effects/recipes/` (the directory listing
  at `50b2f85`, 50 files).
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check` then `python -m pytest -q content/video_engine/tests/test_recipe_use_when.py` then `python -m pytest -q content/video_engine/tests/test_effects_catalog_drift.py` then `python content/video_engine/projects/_proofs/p71-recipes/proof_t34.py` then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: each strip beside its Bravos frame: STK 2:16 (`-ss 136`), DOM 06:20 (`-ss 380`), STK 0:14-0:18
  (`-ss 14`, `-ss 18`), JPN 05:35 (`-ss 335`), DOM 09:35 (`-ss 575`), and BUB 0:00 / 0:48 (`frame_0001.jpg`,
  `frame_0005.jpg`).
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T35: Chart-and-diagram recipes - rise, turn, consequence; the doubt then the budget evidence; the total that points back (was P69 T70)
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T34 (R19 extends R18's peak-fall-magnitude); T12 (the ✓ on what survived); T15 (`under: blur`, s124)
- Harvest: v2 R19 "Rise, turn, consequence" (HIS 05:50-06:07); R34 "Doubt -> the budget evidence" (HIS 02:02-02:14);
  R35 "Flow -> the total -> a pointer back" (STK 0:02-0:10).
- Use when: USE-WHEN `:721` (R19), `:733` (R34), `:837` (R35).
- Recall: P69 T70's stub cites "the chart dims (T40 / `lpPlateRecede`)". `lpPlateRecede` (engine `:9829`) is the
  two-plate FIELD's recede, not a dim, so that citation is corrected here. The dim under a tile on a ledger page is
  now ruled (s124 (2)): T15's `under: blur`, the author's option when the chart is not the point for the tile's
  moment. R19 may also use the other built routes: `park` (CAPABILITIES `:124`, "the chart makes room by one affine
  transform") or a panels page's `receded` role (s104 amended).
- Verdict: REUSE.
  - R19: T34's R18, then park, recede or `under: blur` (T15), a flow branching out, and T12's ✓ on what survived.
  - R34: a flow above (a panels `stack` layout), the bars below, the press card last with its highlighted phrase (F5,
    HAVE).
  - R35: the headline total (a `figure`), a leader back to the bar it dwarfs, then the multiple (T50's bracket).
  - **Bounded discovery:** is there a CURVED leader to compose? The flow's clothoid arrow (CAPABILITIES `:102`, the
    clothoid fitter) is the candidate. If no card draws a free leader between a figure and a bar, stop and file it.
    Never draw one inside a recipe.
- Write set: `content/video_engine/effects/recipes/{rise-turn-consequence,doubt-then-the-budget-evidence,the-total-points-back}.json`
  (new, candidate); `content/video_engine/projects/_proofs/p71-recipes/proof_t35.py` (new).
- Input evidence: H rows 12-13 for R19 (row 13 is a plate reset, so R19 lands on row 12's page before the dip:
  `inflated expectations` 134.07, `kept working` 158.90-159.97); row 11 for R34 (the Uber record); row 16 for R35 (the
  150 total pointing back to the 28 bar: 267.39, 260.74). Derived; the parent confirms on the frame.
- Constraints: a recipe is a timing (s70); no new form; the total never competes with the data (a placement WARN,
  s106).
- Acceptance:
  1. Three recipe files with their `use_when`.
  2. Each proved as a beat and its strip read.
  3. The leader discovery's result logged.
- Stop conditions: R35's leader does not compose (ship R19 and R34; file the leader).
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the three recipe ids exists.
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check` then `python -m pytest -q content/video_engine/tests/test_recipe_use_when.py` then `python content/video_engine/projects/_proofs/p71-recipes/proof_t35.py` then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: strips beside HIS 06:04 (`-ss 364`), HIS 02:08 (`-ss 128`) and STK 0:06 (`-ss 6`).
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T36: Line recipes - the trace to its level, the divergence spread, and today's boom against past booms (was P69 T71)
- Status: running - lane B `861d8de`: `recipe:trace-to-the-level` (R21) and `recipe:the-divergence-spread` (R27), candidate, proved as beats; R32 waits on its evidence (R26-377); the spread's bloom is a dial (R26-378, P72 T49); the level's axis pill R26-379
- Owner: implementation_luna (LANE B)
- Depends on: T9 (the axis tag), T10 (the level join). Done: T37 (`solo`), T50 (the bracket on the gap).
- Harvest:
  - v2 R21 "Trace -> endpoint -> guide -> pill" (DOM 00:39-00:50.5; BOOM): buildable on DOM; VERIFY.md CONFIRMS it in
    BOOM at 00:36-00:41 (ring and "3 Years" x-guide 00:36.0-00:36.5; "5x" y-guide 00:41.0-00:41.5; the "5x" pill sits
    ON the dashed rule by the axis, which C14 does not copy: our label stays off the rule).
  - R27 "Divergence spread" (D40 04:30-04:50 (G); BOOM): D40 frame check first; VERIFY.md CONFIRMS BOOM's wedge fill
    at 08:35 (A47 / R27, a white-to-gold gradient in the gap; `A47_wedge/frames/t08m35.0s.jpg`).
  - R32 "Today's boom against past booms": **UNBLOCKED, with one correction** (VERIFY.md CORRECTED, 00:34.5-01:34,
    one held plot about 60 s): axes, then the AI line draws (00:34.5-00:36); "3 Years" x-pill (00:36.0); "5x" y-pill
    (00:41.0); a news card (00:44.5-00:51); then Dotcom (00:52.5), Roaring 20s (01:00), Railway + Canal (01:04.5)
    draw ONE AT A TIME. **The old cycles land in FULL ink with glow, not muted**; the muting is a LATER on-word
    isolate (01:11: the AI line dims and the old cycles stay lit; 01:17-01:18: AI relights and the rest dims); a ring
    on the AI tip at 01:20 (`R32_T36_A42_A1/frames/t00m36.5s.jpg`, `R32_A2_A12_dock/frames/t01m06.0s.jpg`,
    `t01m18.0s.jpg`). S9 (the legend chip turns accent as each series is named, 00:55 / 01:04 / 01:07) is T30's.
- Use when: USE-WHEN `:819` (R21), `:949` (R27), `:389` (R32; the card copies the correction: past cycles arrive
  lit, one per sentence; the dim is an isolate on its own word).
- Recall: effects `page_enter:axes`, `recipe:pill-rides-the-line`, `page_species:spread`, `bracket`;
  `recipe:estimate-opens-as-a-wedge` stays the projection's form (T35 of P69).
- Verdict: REUSE.
  - R21: the line draws, the tip blooms (T37b), a ring lands, T10's level join runs to the level, and the pill lands,
    with the label off the rule (C14).
  - R27: two lines, their end pills, `spread`, and a bracket on the gap with its figure.
  - R32: a rebased line page (x = years since each boom's start, y = the multiple of its pre-boom trough, the
    rebasing stated on the page, E77), today's line drawn first with its two pills (T9), then each past boom drawn on
    its own word in its full ink (`build_to` / `chart_to extend`, T37b's bloom), then `solo` isolates on its word (P69
    T37) and a ring lands on today's tip. No new form.
- Write set: `content/video_engine/effects/recipes/{trace-to-the-level,the-divergence-spread,todays-boom-against-past-booms}.json` (new, candidate);
  `content/video_engine/projects/_proofs/p71-recipes/proof_t36.py` (new).
- Input evidence: row 15's level for R21 (`five and a half` 225.21-226.49); R27 on H rows 1 / 10 / 20 / 24 (row 10's
  "chips doubling, customers flat": `doubling` 95.39-95.88, `customers` 96.26-96.84).
- Constraints: s70; no new form; E77, the rebasing stated on the page (R32); each past boom's series is a committed
  evidence object with its source, never re-typed.
- Acceptance:
  1. D40 04:30-04:50 read and logged (R27 is withdrawn if not seen).
  2. Three recipes proved as beats, their strips read.
  3. R32's past cycles land lit, one per word, and the isolate dims on its own word.
- Stop conditions: D40's frames do not show R27 (ship R21 and R32); no committed rebased-cycle evidence object is on
  disk for R32 (report: an evidence order for the parent; R32 ships only on committed series, never re-typed).
- Regression: `python content/video_engine/scripts/effects_catalog_check.py`
- Expected RED: none of the three recipe ids exists.
- Validate: `python content/video_engine/scripts/build_effects_catalog.py --check` then `python -m pytest -q content/video_engine/tests/test_recipe_use_when.py` then `python content/video_engine/projects/_proofs/p71-recipes/proof_t36.py` then `python content/video_engine/scripts/effects_catalog_check.py`
- Frame acceptance: strips beside DOM 00:45 (`-ss 45`), D40 04:40 (`-ss 280`), and BOOM 00:36.5, 01:06.0 and 01:18.0
  (BRAVOS-FRAME `-ss 36.5`, `-ss 66.0`, `-ss 78.0` on `scratch/jx3Ll_full.mp4`).
- Red evidence: pending
- Green evidence: pending
- Frame read: pending
- Evidence: pending

### T37: Integration and merge - per wave, the registries unioned, the generated files regenerated, CAPABILITIES, one commit per slice
- Status: pending
- Owner: parent (integration), release_steward (commits)
- Depends on: each slice's review and frame read
- Write set:
  - lane B: each slice's patched files;
  - the registries (the unions listed in the Execution Path);
  - the generated files, which only the parent writes (`page-boxes.v1.json`, `SPECIES-BY-SENTENCE.md`,
    `docs/EFFECTS-CATALOG.*`, `docs/GATES-REGISTRY.md`);
  - `docs/content-video-engine/CAPABILITIES.md` (one row per built capability, in its slice's commit; the shared
    registry process);
  - the goldens (re-pinned once per wave);
  - `docs/content-video-engine/BACKLOG.md` (the R26 rows closed);
  - lane A: T8's commit (and T7's merge into lane A before it).
  - (Draft 1's "side fix" for `estimate-opens-as-a-wedge.json` is withdrawn: the file holds a valid UTF-8 en dash,
    review finding 4.)
- Acceptance:
  1. Patches are applied with `git apply --3way` in wave order, each committed with explicit paths and a `Recall:` line
     citing a committed path.
  2. After each apply, run `sync_kinetics.py --write` then `--check`, `measure_page_boxes.py --write`,
     `lint_species_choice.py --when --write-doc`, and `build_effects_catalog.py --write` then `--check`.
  3. The goldens are re-pinned once per wave, with a sha table.
  4. The full suite is diffed against the base fail set (the grammar rule: `test_authoring_*` and a full-suite diff
     before any push).
  5. The committed H door is identical after each verb slice; after each fix slice and T8, every
     change is listed and read.
  6. Pushes that touch CAPABILITIES or cards need the registry check and a Claude bridge REGISTRY-ACK.
  7. No push without the operator's current word; the merge to main follows the register's checklist.
- Validate: `python content/video_engine/scripts/sync_kinetics.py --check` then `python content/video_engine/scripts/measure_page_boxes.py --check` then `python content/video_engine/scripts/lint_species_choice.py --when --check-doc` then `python content/video_engine/scripts/build_effects_catalog.py --check` then `python content/video_engine/scripts/effects_catalog_check.py` then `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py -q`
- Evidence: pending

### T38: P71-HG1 - each verb as a beat played with the take, frozen, beside its Bravos frame; each fix before and after
- Status: pending
- Owner: parent (frames the gate; the proof door built by implementation_luna in lane A); the operator rules
- Depends on: T37. Batched to the end on the operator's standing word.
- Write set:
  - `content/video_engine/projects/systems-and-blowups/steel-and-paper/proof_p71_verbs.py` (new, lane A, on the
    pattern of P70 T12's `proof_p70_verbs.py`): one private test-bed build per verb, played with the take
    (`vo-h-scratch/scratch-kokoro.words.json` and its audio);
  - `.../steel-and-paper/build-p71-<verb>/**` (gitignored, frozen, on its own port, never :8731, never rebuilt while
    linked);
  - the REVIEW-QUEUE row framed in T0 (updated with the links);
  - then `docs/portable/OPERATOR-RULINGS.md` and this plan with the ruling.
- Acceptance:
  1. **Scenes, not fixtures (s60).** Each verb (T9-T33, T39) is served as its test-bed beat PLAYED WITH THE TAKE,
     beside the Bravos frame cited in its slice (BOOM's at VERIFY.md's true times) and labelled with the H sentence it
     carries. A beat on no H row is labelled "reference".
  2. Each fix is served as a before / after pair at the H instant that showed the defect (T1 272.0 s, T2 the relight's
     end, T3 663.2 s, T4 242.30 s, T5 contact + 0.30 s, T6 the RAM prop's exit), and so are T15's hover default (a
     dock over an H chart, before / after) and T8's divergence page (rows 1 and 4).
  3. **ONE question, asked once:** the adoption question (which verbs, if any, a body row adopts). It is not re-asked
     at P69-HG4. There are no other open operator questions: draft 1's Q1 is answered by s124 and E65, Q2 by s125,
     and the M48 approval by s126.
  4. Ruled items are not re-asked: E79 / E53 s4 (scale), E65 (the empty room), s102 (dual axis), s109 (1)
     (schematics), s121 / s123 / s127 (seals and their gold), s122 (the title), s124 (hover / blur), s125 (a series
     over a schematic), s126 (M48 blocks), s128 (a stamp over the world).
- Validate: `python content/video_engine/projects/systems-and-blowups/steel-and-paper/proof_p71_verbs.py` then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

### T39: The shape meets the data - a real series laid over a schematic on its own labelled axis, where it sits drawn as the script's claim (was P69 T46 (3); E99 s125)
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (s125's four conditions are truth rules)
- Depends on: P70 T2 committed (the schematic: `SCHEMATIC_SHAPES`, `schematic_series`, `lpSchematicTag`, the
  `buildLedgerLine` value suppression behind `pg.schematic`); T13 (the shared right axis `lpRightAxis`, in its series'
  ink); T20 (the same schematic branch of `buildLedgerLine`, wave 5); T28 (`buildLedgerLine`'s stroke, wave 7)
- The ruling (E99 s125, `OPERATOR-RULINGS.md:3381`), verbatim in its four parts: "(1) A real series may be laid over a
  schematic on its word; (2) the series keeps ITS OWN real, labelled axis (dates and values) and is never rescaled or
  stretched to hug the curve - a series fitted to a shape claims a fit the data never showed; (3) the schematic keeps
  its "shape" tag (s109 (1)), so the page reads as two kinds of thing, a drawn shape and a measured line; (4) where the
  series sits on the shape is the script's CLAIM ("we are here") and the page draws it as one - a marker or ring with
  the claim's words - never implied by alignment alone. Clears P69 T46 (3) from Not Building. Carrier: P71 (the
  schematic + series slice, EXTEND of P70 T2)."
- Harvest: v2 T7 / R6 (the schematic cycle, P70 T2's harvest); P69 T46 (3) "a real series may later be laid over it on
  a word (the shape meets the data)". VERIFY.md confirms BOOM's schematic waves (09:38; 15:28) and the real chart that
  follows them "already shifted" (16:14), a shape and a measured series on one page in sequence.
- Use when: the sentence places TODAY on a known shape ("we are here on the cycle") and a measured series is the
  evidence for where. Don't: a series stretched onto the curve; a claim of position with no words on the page; a
  schematic that loses its "shape" tag.
- Recall: docs_find "schematic" -> P70 T2 (in progress on `50b2f85`; `test_schematic_page.py` is created by it);
  `buildLedgerCombo`'s right axis (`:11735`, `:11802`-`:11821`) is the pattern T13 lifts into `lpRightAxis`;
  `ring` (CAPABILITIES `:45`) marks a point on a chart (E56); docs_find "we are here" -> 0 capability rows.
- Verdict: EXTEND P70 T2's schematic.
  - A schematic object may carry `overlay: {series: <a sourced series, its own pts / src / tier>, axis: {unit, label},
    claim: {at: <episode s>, x: <schematic x-fraction>, text: "<the script's words>"}}`. P70 T2's refusal of `series`
    beside `schematic` stays; `overlay` is the one sanctioned way a measured line joins a shape.
  - The overlay draws on ITS OWN axes: its values on the right axis through T13's `lpRightAxis`, labelled with its
    unit and in its ink (s102 (b)/(c), s118); its dates in the x band the schematic leaves empty (the schematic writes
    no x values, P70 T2 acceptance 2). Its domain is computed from its own data by the page's ordinary tick law.
  - The claim draws as a marker or a ring AT the schematic's `claim.x` on the shape, with `claim.text` written beside
    it (C14: off the mark), on its word.
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`buildLedgerLine`'s schematic branch: the
  overlay's path and its axes; a NEW claim-marker block in `buildPerform` + dispatch line - Deviation 7's union);
  `content/video_engine/scripts/ledger_page.py` (NEW `_validate_schematic_overlay`, called from P70 T2's schematic
  validation); `content/video_engine/scripts/measure_page_boxes.py` (a representative; parent-merged);
  `effects/cards/page_builder.json` (the `line+schematic` card's overlay option; parent-merged);
  `content/video_engine/tests/test_schematic_overlay.py` (new); the golden `schematic-meets-the-data` (new).
- Input evidence: H row 12's hype cycle (P70 T2's golden: `peak of inflated expectations` 133.69-136.10, `trough
  already doing its job` 136.39-138.43) with a committed measured series the script ties to the trough (the slice
  finds it on disk: a sourced series whose sentence says where it sits); the claim's words are the script's own. If
  no committed series and sentence exist, a private test-bed beat on a sourced series from disk, labelled reference.
- Constraints (s125, all truth rules, so hard refusals BY NAME):
  - (2) an overlay with no `axis.unit` or no `axis.label` is refused ("a series over a schematic keeps its own
    labelled axis, s125 (2)"); an overlay carrying any domain, scale, offset or fit key (`domain`, `y_domain`,
    `scale`, `fit`, `align`, `stretch`) is refused ("never rescaled to hug the curve, s125 (2)");
  - (4) an overlay with no `claim` or an empty `claim.text` is refused ("where it sits is a claim, drawn with its
    words, s125 (4)");
  - (3) the schematic's "shape" tag stays on the page and in `page_boxes` with the overlay present;
  - the overlay is a measured, primary line (it blooms, s117); the shape keeps P70 T2's stroke;
  - byte-identical for every schematic with no `overlay` and every non-schematic page.
- Acceptance:
  1. A schematic with an overlay draws the shape (tagged "shape"), then on its word the measured series on its own
     labelled right axis and its own dates, then the claim's marker and words at the claimed point.
  2. The refusals of (2) and (4) hold, each naming s125.
  3. The page reads as two kinds of thing at 16:9 and at the squint width (M48 passes it).
  4. One golden.
- Stop conditions: P70 T2's schematic writes no x band the overlay's dates can use without re-laying the page (report);
  `lpRightAxis` is not yet shared (T13 not merged; wait).
- Regression: `python -m pytest content/video_engine/tests/test_schematic_overlay.py -q`
- Expected RED: after P70 T2, a schematic object carrying `overlay` is refused or ignored (the probe on P70 T2's merged
  code decides which, step 1); either way no overlay draws and no s125 refusal exists.
- Validate: `python -m pytest content/video_engine/tests/test_schematic_overlay.py -q` then `python -m pytest -q content/video_engine/tests/test_schematic_page.py` then `python -m pytest -q content/video_engine/tests/test_dual_axis.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden beside BOOM 15:28 and 16:14 (BRAVOS-FRAME `-ss 928.0`, `-ss 974.0` on
  `scratch/jx3Ll_full.mp4`: the schematic, then the real chart that follows it).
- Red evidence: pending
- Failure attribution: pending
- Unrelated failures: pending
- Green evidence: pending
- Refactor evidence: pending
- Frame read: pending
- Review: pending
- Evidence: pending

## Verification

- The parent runs each slice's Validate in lane B after integration: each pytest file in its own process, unpiped
  (never `| tail`; a tail's exit code masks a FAIL).
- Byte identity: after a verb slice, the committed H door compiles identically (`engine_sha256` aside) and renders N of
  N instants identically. After a fix slice and T8, the changed instants are listed and read. Log:
  `$SP/p71-tN/logs/door-identity.log`.
- After each wave: `python -m pytest content/video_engine/tests -q` and `node --test content/video_engine/tests/kinetics`,
  with the tails written to `$SP/p71-waveN/suite.txt`, and the fail set diffed against the wave's base.
- The plan: `python scripts/prp_validate.py .claude/PRPs/plans/P71-THE-BRAVOS-VERBS-WAVE-3.plan.md` and
  `python scripts/prp_status.py`.
- **The coverage table: the rulings each slice respects (and, for s124-s128, the slice that carries each).** Line
  numbers are in lane A's `docs/portable/OPERATOR-RULINGS.md` (s124-s128 in its working tree at this revision).

  | ruling | file line | what it requires | slices |
  |---|---|---|---|
  | E28 | `:835` | a chart reads at a glance; sign is geometry | T3 (an axis reads whole), T12 (the tab inks), T21 (the sign's fill), T28 (no fall in the pos ink), T1 (a figure reads whole) |
  | E38 | `:1204` | thresholds from the reference | T7 (M48's page band is Bravos's; the caption floor is the reference's) |
  | E53 s4 / E79 | `:1740` / `:2517` | one measure, one unit, one scale | T13 (y2 only with a comove claim), T27, T33 (each twin states its own scale) |
  | E56 / s110 (2) | `:1815` / `:3351` | a ring marks what the sentence points at | T22 (the ping is a blink, never a ring on a region), T39 (the claim's ring marks the claimed point) |
  | E63 (amended by s124 (3)) | `:2048` | no card reads over a ledger page's plot - except a dock that names `under` (hover / blur) | T15 (`read_over_build` keeps an authored `under`; M25 / M27 WARN it), T23 (3) |
  | E65 | `:2111`-`:2129` | the placer's order: a band, then the plot's EMPTY room (the read there passes M25 / M27), then the axis band | T23 (3) (the read in the empty room), T15 (the placer untouched for a dock with no `under`) |
  | E77 / s93 | `:2480` / `:3317` | a derived figure is our layer; a tier rides the object | T16, T25, T26 (every projection labelled with its tier), T36 (R32's rebasing stated) |
  | E99 s60 | `:3238` | a proof is a scene | every golden on an H beat or labelled reference; HG1 serves beats with the take |
  | s70 | `:3258` | a recipe is a timing that composes | T33-T36, T14's recipe, T15's R3, T18's R13, T19's R14, T26 |
  | s74 | `:3266` | a transition carries the world it leaves | T4 |
  | s91 / s99 | `:3313` / `:3329` | a light that sits is 0 events; travels / blinks is motion | T12 (`lit` / `pulse`), T11 (tokens), T14 (the scroll), T18 (the "?"), T29 (the glow) |
  | s98 (amended by s124) | `:3327` | blur under a dock over a busy chart plate - now an option over ANY chart, by intent | T15 |
  | s100 / s109 | `:3331` / `:3349` | forms judged by honesty | T20 (s109 (1) hard), T25, T31, T34's iceberg, T14 (no date implied for a chip), T39 |
  | s102 | `:3335` | a second / inverted axis on a comove claim | T13, T39 (the overlay's axis in its ink, naming its unit) |
  | s104 amended | `:3339` | receded panels blur | T15 (a receded panel's blur stays T8b's), T35 (R19's recede) |
  | s106 | `:3343` | the engine advises; truth rules stay hard | T5, T6, T9 (the fourth tag WARNs; no refusal by type), T10 (a placement WARN), T15 (a dock over ink WARNs), T31 (a logo falls back) |
  | s117 / s118 | `:3365` / `:3367` | primary lines bloom; names wear their series' ink | T13, T16 (a projection never blooms), T28 (the split keeps the bloom), T39 (the overlay blooms) |
  | s120 | `:3371` | the squint test: focus, the words the story needs, few words on the plot; "it becomes a gate row" | T7, T8 |
  | s121 / s123 | `:3373` / `:3377` | a seal-type stamp is a gold seal | T29 (F19 retired), T12 (the stamp form refuses the states) |
  | s122 | `:3375` | the title is Claude orange, glowing, Bravos-sized | T30 (the capsule waits on T37c), T2 (the relight hands back T37c's ink) |
  | **s124** | `:3379` | a dock over ANY chart HOVERS by default (lift, shadow, a step, the drift-hold idle, the chart sharp); BLUR is the author's per-dock option by intent; amends s98 and E63 | **T15** (the carrier: `under: hover` default / `blur` opt-in, plates and ledger plots; two commits), T23 (3), T18 (the collage under `blur`), T19 / T33 (docks over a chart hover by default); depends on P70 T13 |
  | **s125** | `:3381` | a real series over a schematic on its own labelled axis, never rescaled to hug; the "shape" tag stays; where it sits is a claim drawn with words | **T39** (the carrier; refusals of an unlabelled axis, a fit key and a missing claim) |
  | **s126** | `:3383` | M48 BLOCKS (FAIL, thresholds off Bravos first) and reads the captions (the long-form and shorts' strips at the small size, a floor off the reference) | **T7** (the carrier: M48 FAIL, pages and captions), T8 (its regression goes RED on the FAIL) |
  | **s127** | `:3385` | the seal gold is `#E8B86D`; a seal's shockwave is gold; a bare prop's ring picks chalk / charcoal by the measured ground | carried by **P70 T1c**; P71 depends on it where a ring matters: T5 (the frame read shows the gold shockwave), T12 and T18 (they edit `chip.mjs` after T1c) |
  | **s128** | `:3387` | a STAMP is drawn over the world (open, the chart shows through, overlap is not a defect, the fit never moves or fills it for that); a PROP lives in the world | **T5** (the carrier with P70 T1c: the reserved box keeps OTHER elements off a stamped chip on its beat, never pushes the stamp off the chart), T29 (F19's shadow clause dropped), common rule (i) |

## Evidence And Handoff

- **The planning evidence** is in `$SP/p71-plan/`:
  - `provenance.txt`: lane A `910ddd6` and lane B `557e1dc` with their tracked dirty sets (draft 1's capture; lane B then
    held P70 T1b uncommitted), plus the sha256 of the contended files at `557e1dc`. Revision 2 read lane B at
    `50b2f85` (T1b committed, no tracked file dirty) with `git show`; T0 re-captures;
  - `recall-raw.txt`: 50 docs_find runs from the lane-B root;
  - `take-times.txt`;
  - `src/`: the committed sources draft 1 cited;
  - `REVIEW.md`: the review this revision applies;
  - the BOOM frame verification: VERIFY.md (fable-p68 worktree, gitignored; path in Mandatory Reads).
- **The docs layers were STALE during recall.** docs_find reported "FAILED to build capabilities-index - 236 records, 4
  flagged". Every capability claim was therefore also read in `CAPABILITIES.md` (lane A and lane B) and in the code. A
  slice that finds a capability recall missed stops and reports.
- **Deviations:**
  1. As in P70, parallel wave slices edit the same files in separate scratch exports, with disjoint functions. The
     registries are parent-merged and integrated by `git apply --3way`. The runbook's rule is disjoint files.
  2. P69's stubs are renumbered. T88 splits into T7 (the gate, lane B) and T8 (the label diet, lane A).
  3. A59's BUY folds from P69 T60 into T12 (one state grammar), and A55 folds from P70's Not Building into T20.
  4. F18 is dropped as done by T37b, F19 is retired by s121 / s123, and F14 is dropped on VERIFY.md's frames.
  5. The P69 T80 <-> T44 circle is broken: the pedestal is built in T32, and the recipe composes it in T34.
  6. BOOM: draft 1 gated every BOOM-only item; revision 2 resolves every gate from the parent's frame verification
     (VERIFY.md) - confirmed, rescoped to the witnessed form, or dropped - so no BOOM gate remains (review finding 8).
  7. **Two writers in one registry function inside a wave** (review's wave check): wave 2's T9 and T10 each append a
     `buildPerform` block, a `paintPerform` dispatch line and an `LP_PANEL_KINDS` entry; wave 5's T18 (`unknown`) and
     T20 (the datum badge), and wave 7's T26 (`stretch_box`, if `span` cannot carry the box) and T29 (`glow`), each
     append a `buildPerform` block; wave 9's T39 appends its claim-marker block. Each is an append-only union the
     parent integrates, like P70's registries.
  8. T15 is one commit (the option + the choose-by-goal WARN): s124 as amended makes `under` a choice, not a default.
  9. P71 T39 is numbered after T38 (the gate) because it was added in revision 2; it runs in wave 9.
- **Handoff to the parent:**
  - T0: the re-captured base (`50b2f85` or later); the P69 pointers (including T46 (3) -> T39, F14 / A52 / A54 / the
    tilted plane dropped, T14 / T33 / A56 rescoped) and the T37 / T37b / T64 / T65 status corrections; the backlog
    pointers; the REVIEW-QUEUE row. No research commission is filed.
  - P70: T10 (the badge swap) is unblocked by VERIFY.md's A44 (02:27.0-02:27.5) - the parent's edit to P70.
  - The correction for P69 T70: its `lpPlateRecede` citation is wrong.
  - Commit the rulings s124-s128 in lane A before T0 (they are in its working tree).
  - HG1 carries ONE question, the adoption question; no other operator question is open.
- **The successor, not a slice:** the next one-shot test against the 09-16 baseline, opened once T37 has merged the
  last wave and T38 has been served.
