---
id: P72-THE-BACKLOG-BURNDOWN
title: The backlog burndown - every open backlog row and plan slice DONE with evidence, CLOSED with the reason, or a named human gate
status: running
operation: maintenance
risk: standard
owner: parent
branch: claude/fable-p68 (the plan, the bookkeeping, lane-A docs); engine, gate and script slices land on claude/p69-s90 (lane B), one writer per function, after the P70 / P71 slice that owns the same function
contract: tdd-v1
created: 2026-09-25
updated: 2026-09-25 (APPROVED by the operator: "/prp-implement P72"; running on lane B df678cc / lane A be6299e; revision 1, architect_sol - the review's 18 findings applied as the parent ruled them; R26-331 .. R26-340 carried; lane B re-read at a469501; T0 the closing pass 2026-09-25 on lane A 0d2e705 - batches 1-3 and part 2, the five decisions recorded, `coverage.py` exit 0)
---

# P72 - The backlog burndown

## Summary

The operator (2026-09-25): "/prp-plan a backlog burndown to clear the backlog/open work to human gates only". When P72
closes, every open backlog row and every open plan slice is in one of three states: DONE (a sha, a test or an artifact
cites it), CLOSED (stale, superseded or a duplicate, with the ruling or the row that makes it so), or a HUMAN GATE
listed once in this plan's gate list with what to judge and where. Nothing else stays open.

The inventory is the planning evidence: `$SP/p72-plan/INVENTORY.md` (383 lines; one line per item, a verdict from the
evidence, never from the title). It read:
- the 136 `| open |` rows of `docs/content-video-engine/BACKLOG-HISTORY-2026-09.md` (R26-130 .. R26-330);
- the 164 other R26 rows that are not in the archive (the BACKLOG's `LEGACY-REVALIDATION-2026-09` row);
- the BACKLOG.md active queue (13 legacy follow-ups, the Codex modeling rows);
- every plan with status running / draft / blocked (19 plans, 139 slices not marked done);
- the 14 open review-queue items and the plans' human gates;
- five new items the reads found (section E);
- revision 1: the ten rows filed on 2026-09-25 after the inventory (R26-331 .. R26-340, section F; R26-340 was found by
  the live universe read itself, filed after the brief) and the two `panels+bars-9:16` dock cases no row carries
  (section F, by pytest node id).

**The counts (primary verdict per item; 353 items = draft 1's 343 + R26-331 .. R26-340):**

| verdict | items | where it goes in P72 |
|---|---|---|
| DONE-UNCLOSED | 139 | T0 - the closing pass (archive rows and status lines, in batches) |
| CLOSE-STALE / -SUPERSEDED / -DUPLICATE | 28 | T0 - each closed with its ruling or superseding row |
| TRIGGERED / DEFERRED (`⏸️`, BACKLOG-DISCIPLINE `:25`) | 5 | T0 keeps each as a `⏸️` row with its trigger: R26-44, 52, 137, 61, 15 - never archived |
| ENGINE (lane B) | 82 | T6-T27 and T40, T41, T43 by function, in waves 1-6 |
| TOOLING | 53 | T1-T3, T8, T9, T28-T32, T44 |
| LANE-A (docs, H, production) | 6 | T4, T35-T37, T42; the H-row re-aims in T36 |
| RESEARCH (the claims-gated lane) | 3 (+ R26-254 part 2) | T33, T34 |
| ALREADY-PLANNED (a P48 / P68 / P69 / P70 / P71 slice) | 12 | referenced, never duplicated |
| HUMAN | 8 | the gate list (merged with the existing HGs) |
| OTHER-LANE (a running Codex / Astra plan) | 11 | listed; P72 writes none of it |
| BLOCKED-EXTERNAL | 1 | R26-111 (a plate generation no cut asks for) |
| bookkeeping | 5 | T0 |

**Revision 1's deltas against draft 1** (each id's new line is in INVENTORY): R26-219 DONE -> ENGINE (the bracket half,
T43; the card half stays in T3); R26-9 CLOSE -> ENGINE (TR-3, T27); R26-143 CLOSE -> ENGINE (the second half, T17);
R26-261 ALREADY-PLANNED -> ENGINE (the title rewrites whole, T26); R26-44 ENGINE -> TRIGGERED; R26-52 / 137 / 61 / 15
CLOSE -> TRIGGERED; R26-168 CLOSE -> HUMAN (M38, the operator's open question); R26-127 TOOLING -> DONE (`bf539e3`);
R26-36 DONE -> ENGINE (T20, a listened pass owed); R26-283 ENGINE -> LANE-A (the engine half DONE at `af869b7`, the
row-15 re-aim left, T36); R26-229 HUMAN -> LANE-A ((a) built in T42, both forms on P68-HG3); R26-331 .. R26-340 +10
(ENGINE 8, TOOLING 2). Draft 1 did not record which bucket R26-219 and R26-229 were counted in; this revision counts
them by their first-named verdict (DONE-UNCLOSED and HUMAN). R26-308 / 310 / 312 / 314 stay DONE-UNCLOSED, but they are
archived as "code landed; the operator's read at P71-HG1" (BACKLOG-DISCIPLINE `:20`).

**Parent decisions: five** (D1-D5, recorded in T0; the same five everywhere in this plan): D1 R26-316, D2 R26-105, D3
P65 T6, D4 R26-214 (c), D5 the R26-9 / R26-102 closure. None of them is the operator's.

The engine work is grouped by FUNCTION, one writer each, and sequenced after the P70 / P71 slice that owns the same
function (the ownership tables in P70 and P71 are this plan's too). The slices the brief named are all here: s130 (1)
the fill glow (T10), s130 (2) the seal's gold by the measured ground (T11), R26-315 (T12), R26-318 as the highest
priority (T6: a truth gate that cannot read is a false PASS), and R26-316/317/319-330 (T6, T7, T12, T17, T19-T22).
P71 T15 keeps the dock's `under: hover|blur`; P72 does not touch it.

`$SP` below means
`C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad`.
Lane A = `C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/fable-p68` (read at 8f233a1); lane B =
`.../worktrees/p69-s90` (read at e43c3d8 with `git show e43c3d8:<path>`; every `:line` below is at e43c3d8 and is
re-read by its SYMBOL in the brief). Revision 1 re-read lane A at `bf539e3` and lane B at `a469501`: since e43c3d8,
P70 T2 (`3600ec5`, the schematic), P70 T13 (`35a2130`, the drift-hold) and P71 T7 (`a469501`, M48) have landed; P70
T5, P70 T7, P71 T3b, T12 and T15 have not.

### The slice table

T5 and T16 are unused numbers: R26-282 (T5's only item) was found DONE at `7d43e43`, and the page-states slice
moved to T26 behind P71's `buildLedgerLine` slices. The numbers match the inventory's pointers. Revision 1 adds T40-T43
(new numbers, so no inventory pointer moves).

| P72 | items | class | owner | wave | depends on |
|---|---|---|---|---|---|
| T0 | the closing pass: 167 DONE/CLOSE items archived with evidence; the five `⏸️` rows kept with their triggers; plan status corrections; queue rows for P69-HG1..HG4 and P72-HG1; the five parent decisions (D1-D5); the live coverage check | bookkeeping | parent + speedster | 0 (runs beside waves 1-2) | the operator's approval |
| T1 | NEW-1: the recall layer builds again (capabilities index over its byte cap, 4 malformed rows) | TOOLING (lane A) | junior_developer | 1 | T0 |
| T2 | R26-244, 238, 240, 145, 162, 141: the suite green and its pins honest | TOOLING | implementation_luna | 1 | T0 |
| T3 | R26-237 (+196), 116, 219 (the card half), 252: the recipes carry the rulings | TOOLING | implementation_luna | 1 | T0 |
| T4 | R26-195, 200, 202 (c), 188, 214 (a), 174, 193, 124, 136 (5): the builder's checklist and the record | LANE-A (doc) | parent (+ junior_developer) | 1 | T0, T1 (both edit `CAPABILITIES.md`) |
| T6 | R26-318, 303, 264, 319: the value gate reads every page | TOOLING (truth gate) + ENGINE | implementation_luna, reviewer | 1 | the operator's approval of this plan only (P70 T3 landed) |
| T7 | R26-326, 269, 189, 167, 132 (2), 202 (a): the motion gate credits what moves and judges a card at rest | TOOLING (gate) | implementation_luna, reviewer | 2 | P70 T8 (`_landings` / `_arrivals`); P71 T7 (landed `a469501`); acceptance (7) after P71 T15 |
| T8 | R26-207, 208, 203, 212, 206: the long form's gates | TOOLING (gates) | implementation_luna | 2 | T0 |
| T9 | R26-140, 243, 251, 151, 323: the renders and the golden sources are deterministic | TOOLING | implementation_luna | 2 | T0 |
| T10 | s130 (1): filled marks glow - the gauge's fill and the primary bars, measured off Bravos | ENGINE | implementation_luna, reviewer | 3 | P70 T3 (landed), T6 (the gauge branch), T9 |
| T11 | s130 (2): a seal's gold adjusts by the measured ground | ENGINE | junior_developer, reviewer | 3 | P71 T12 (`chip.mjs`) |
| T12 | R26-315, 316, 299, 339: the panels page builds in view; the long form holds at every preset | ENGINE | implementation_luna | 3 | T0 (D1, R26-316) |
| T13 | R26-274, 287, 250, 170, 217: a bars page writes its units and keeps its labels clear | ENGINE | implementation_luna | 3 | before P71 T25 / T31, or after both |
| T14 | R26-268 (HIGH), 278, 292: the captions read on every plate | ENGINE + TOOLING | implementation_luna | 3 | T0 |
| T15 | R26-253, 270 (+ R26-274's fixture): page_boxes carries every text box | ENGINE | implementation_luna, reviewer | 4 | T13, T40 |
| T17 | R26-249, 317, 154, 43, 149, 214 (b), 209, 258, 143 (2), 333: the compiler says what it drops | ENGINE (compiler) | implementation_luna | 4 | T0 |
| T18 | R26-284, 288, 255, 256: figures and rings on a bars page | ENGINE | implementation_luna, reviewer | 4 | T13 |
| T19 | R26-328, 285, 271, 320, 267, 202 (b): docks keep their box, leave with the dip, ride a park; the throw takes a side | ENGINE | implementation_luna, reviewer | 5 | P70 T8, T9, T13 (landed `35a2130`); P71 T6, T15, T19, T23; T0 (D2) |
| T20 | R26-286, 329, 35, 36: the sound follows the frame | ENGINE (sound) | implementation_luna | 5 | P70 T8 (`authoring/audio`) |
| T21 | R26-260, 21, 294, 321, 322, 324, 325: the named places the engine is not yet a pure function of t | ENGINE | implementation_luna, reviewer | 5 | P70 T8, T9; P71 T6, T15, T19 |
| T22 | R26-327, 304, 173, 169: the verdict stack | ENGINE | implementation_luna | 6 | T7 |
| T23 | R26-157, 146, 139: the melt's options | ENGINE | implementation_luna | 6 | T21, T30 (R26-115 / 138) |
| T24 | R26-153, 163, 150, 148, 152: the morph | ENGINE + TOOLING | implementation_luna | 6 | T7 (gate file, disjoint function), T9 (`build_golden_sources.py`'s idempotence) |
| T25 | R26-165, 164: the plate's moves take a window (R26-283 and R26-281's engine half are DONE at `af869b7`) | ENGINE | implementation_luna | 6 | P71 T32 only if step (0) finds the ken window in `kinetics/camera.mjs` |
| T26 | R26-266, 275, 265, 277, 331, 332, 261 (the title): a page's later states | ENGINE | implementation_luna, reviewer | 6 | P71 T3b, T13, T16, T28, T39; P70 T2 (landed `3600ec5`) |
| T27 | R26-57, 72, 73, 142, 123, 302, 257, 2, 171, 106, 9 (TR-3), 360: the small engine rows | ENGINE | junior_developer | 4-6 (one commit each) | each row's named neighbour |
| T28 | R26-227, 215, 197, 198 (b, c), 178, 130, 183, 136 (3), 188's mirror: scripts that cost runs or say the wrong thing | TOOLING | implementation_luna | 5 | T7 (`gate_motion_density.py main`), T20 (`authoring/audio.py`); the H-door half after P69 T32 |
| T29 | R26-242, 301: citations resolve by row title | TOOLING | implementation_luna | 2 | T1 |
| T30 | R26-160, 166, 182, 161, 115, 138: files under the line cap; one fold; the region order | TOOLING (refactor) | implementation_luna | 3 | T2, T3 |
| T31 | R26-254 (1), 128, 129, 144, 336: the research tooling and the bridge's astra lane | TOOLING | implementation_luna | 2 | T0; T44 (R26-340: "fix before P72 T31") |
| T32 | R26-85: the strobe's sharpness on real motion (a measurement) | TOOLING (measure) | implementation_luna | 4 | T9 |
| T33 | R26-311 (+ R26-29): the railway research and the as-of date, under the claims gate | RESEARCH | parent + the Gemini lane | 1 | T0 |
| T34 | R26-254 (2): the six dockets re-ingested under the gate | RESEARCH | parent + the research lane | 3 | T31 |
| T35 | R26-147: the full-page melt's design sheet | LANE-A (design) | implementation_luna | 6 | T23 |
| T36 | the P69 hand-off: the H-row follow-ups the fixes make possible (R26-281, 283 re-aims; R26-302 rows; `VERDICT_STACK_ON`; the R26-197 shim) | bookkeeping (P69) | parent | per wave | the engine slice named |
| T37 | R26-175, 135 (4), P54 T7: the one-shot comparison (one-shot #3 as authored, then Opus, then Astra) behind P54-HG3's two steps | LANE-A (production) | parent, implementation_luna, Astra | 7 | P71 T37 (last wave), T38, T31 (R26-336), T4 (R26-193's REWRITE ORDER), P54-HG3 step A |
| T38 | integration and merge, per wave | - | parent, release_steward | per wave | each slice's review |
| T39 | P72-HG1: the closing gate sheet | - | parent; the operator rules | end | T38, T41 |
| T40 | R26-337 + the two `panels+bars-9:16` cases: the dock's 9:16 fail set - the known three `test_video_dock` reds | ENGINE (placer) | implementation_luna, reviewer | 1 | the operator's approval of this plan; P70 T2 (landed `3600ec5`) |
| T41 | R26-334, 335: the balance's sign ink and the prop hatch - candidate sheets for the operator's pick and read | ENGINE (opt-in) + a sheet | implementation_luna | 3 | P70 T7 (the balance) merged; P69 T6b's `PROP_SHADOW` (landed) |
| T42 | R26-229 (a): the agenda beat's park-and-pan, authored on the 30 s bed in a private build, beside (b) on P68-HG3's card | LANE-A (production) | parent, implementation_luna | 3 | none on lane B; lane A at a slice boundary |
| T43 | R26-219 (the bracket half), 338: the bracket's label room - measured at 16:9, a room WARN and an "above" fallback | ENGINE | implementation_luna, reviewer | 4 | P70 T5 (the brace, `check_brace` / `paintBracket`) merged; T13 |
| T44 | R26-340 (1)-(5), (7): the bridge holds on a restart - one toast per tick, the printed conversation id, a reply newer than its follow-up, no futile repairs, the stranded original closed, replies written to the main checkout | TOOLING (lane A, the bridge scripts) | implementation_luna | 1 | the operator's approval of this plan; before T31 |
| T46 | R26-361, 362, 365: the wave-3 follow-ups (the seal's keyline and twin, the owned exit's twin and advice, the stroke width, the 9:16 badge rail, the weak prints' values) | ENGINE | implementation_luna, reviewer | 5 | P72 T11, T13, T17; P71 T6; the dock slices |
| T47 | R26-366: the panels page at phone, built (R26-316's build half) | ENGINE | implementation_luna, reviewer | 5 | P72 T12; P71 T13 |
| T48 | R26-367: a ring on a chart circles its datum (the chart-callout golden bound; a point-target mark off the line WARNed) | ENGINE (compiler) + golden | junior_developer | 4 | none (T17's print chain: union) |

**Honest flags. Read them before approving.**
1. **Counts are primary verdicts, and a half is never lost.** An item with two halves (e.g. R26-132: part 1 DONE, part 2
   ENGINE) is counted once by the verdict that keeps it open. The inventory line names both halves, and every open half
   has a named clause with its own acceptance line in a slice: R26-132 (2) in T7 acceptance (6); R26-202 (a) in T7 (7),
   (b) in T19 (7), (c) in T4; R26-9 TR-3 in T27's TR-3 row; R26-261's title in T26 (8); R26-143's second half in T17
   (8); R26-219's bracket half in T43 (1). A row with a half open is not archived until that clause lands (BACKLOG-DISCIPLINE `:22`).
2. **Ten rows the history still shows `open` are already done** at a sha (R26-263, 272, 276, 282, 305, 306, 308, 310,
   312, 314), and so are two P69 slices still marked pending (T85 `ffa2877`, T87 `965c4e2`); one archived row still reads
   `open` in the history (R26-239) - the
   history file's status words are stale by design (BACKLOG-DISCIPLINE: "old status tokens ... not current evidence").
3. **The P69 human gates are not on the review queue.** `review-queue.v1.json` has no `p69` id, though P69 names
   HG1-HG4 and the runbook requires a queue row in the change that frames a gate. T0 adds them.
4. **The docs layers are stale on lane A.** `build_capabilities_index.py --check` FAILS (the MD is 44,904 bytes over a
   44,000 cap; four malformed rows), so `docs_find.py` answers every recall from stale layers. T1 is first because
   every later slice starts with recall.
5. **`test_worktree_register.py` FAILS on lane A** (15 Codex worktrees without a row) and **`test_lab_log.py` FAILS**
   (R26-244). The first is the Codex lane's rows plus lane A taking main back, so it is a known environmental red and
   is not in any P72 validate chain (T38); the second is T2.
6. **Five parent decisions, none of them the operator's** (T0 records each with its reason): D1 R26-316 (does the long
   form ever render at `phone`? - weighed against R26-339, below), D2 R26-105 (build `rel: pin` only; the other six
   relation verbs wait for a sentence), D3 P65 T6 (close the lab's promotion step - recipes are proved as beats in
   proof doors now), D4 R26-214 (c) (no ambient-lane order until a cut asks; local only, E99 s37 - recorded as a `⏸️`
   row), D5 the R26-9 / R26-102 closure (after R26-9's TR-3 is split into T27, and R26-102 citing E99 s13). Not
   decisions: R26-44 is the operator's and triggered ("Ask on the first cut that threads a line", `hist:462`) - a `⏸️`
   row, not built; R26-168 / M38 is the operator's open question from `p65-hg2-the-reproved-set-and-m38` - the interim
   WARN is the status quo and the question is on the gate list; R26-127 is closed (`bf539e3`, the `bridge_inbox` hook
   self-starts the daemon).
7. **Two running plans look stale** (`MP-AI-USEFUL`, `MP-NORMAL-OUTREACH`: no update since 2026-09-15). They are the
   package lane's; the parent asks that lane for a status line (a bridge note) - P72 does not close another lane's
   plan.
8. **New operator questions: P72-HG1 is new, and it carries three that no gate asked before** - R26-334's pick (the
   balance's sign-ink pill), R26-335's read (the prop hatch's strength on charcoal) and M38's open question (from
   p65-hg2, never answered; the interim WARN stands until he does). The rest are existing gates (P68 HG1/HG3/HG4, P69
   HG1-HG4, P70 HG1, P71 HG1, P54 HG3's two steps) or frame reads added to P72-HG1. Computations and measured checks
   are attached as reports, never asked: the burndown's final-state table, the seal's contrast (T11), and R26-216's
   "which motion rows are NEW against ep1's 16-of-35" (printed on P68-HG4's card). The rulings through E99 s130 and
   `review-answers.jsonl` were checked first; nothing ruled is re-asked (R26-124's race default: s8 chose none - both
   stay selectable, no ask; P65 HG1: withdrawn by s84, not re-asked).
9. **The P54 bake-off is a scope change.** P54's HG3 is two steps: the brief before it is dispatched to Astra, and the
   verdict after the watch (`P54:107`). T37's three whole, labelled one-shots supersede P54 T7's one-beat, unlabelled
   watch (`P54:185-195`). That is a scope change, and the operator confirms it at step A (the brief). If he refuses,
   T37 runs P54 T7 as written.
10. **The dock's 9:16 fail set blocks acceptance 6.** At lane-B `a469501`, `pytest test_video_dock.py -k
    "never_covers_the_chart or read_the_same_bands"` gives `3 failed, 33 passed`: `[dense-line+schematic-9:16]` (R26-337)
    and two `[panels+bars-9:16]` cases that no row carries. T40 carries all three in wave 1.
11. **HG3 is pinned to one lane-B sha** (see "The HG3 pin" in the Execution Path): P72 slices that change what the
    committed door renders land before P69 T11 when their wave allows, and are then in both halves of the A/B.

## Intent And Acceptance

The backlog and the plans say only what is true: open work is either built, closed with its reason, or waiting on the
operator's eye with the frames served.

Plan-level acceptance:
1. Every open id in the LIVE universe ends in one of: archived with evidence (`backlog/archive/2026-09-completed.md`
   row: id, what closed it, the sha / file:line / ruling), carried by a named slice of P72 / P69 / P70 / P71 / P68 that
   is itself open only for its human gate, a `⏸️` triggered row in `BACKLOG.md` with its trigger, listed under
   OTHER-LANE with its owner, or listed once in this plan's Human Gates. The live universe is read at run time, never
   from INVENTORY's id list: every `| **R26-N**` row in `BACKLOG-HISTORY-2026-09.md` minus the archive's first column,
   `BACKLOG.md`'s active queue, every open task in P54, P68, P69, P70 and P71, and the open review-queue items (T0's
   `coverage.py`, which FAILs on any open id with no carrier).
2. `docs/content-video-engine/BACKLOG.md`'s active queue carries only: the running P69 / P70 / P71 / P72 umbrella rows
   (their children listed once), the OTHER-LANE rows with their owners, and one row per human gate - and no row
   whose next action is build work that is not in a slice.
3. Every engine / gate / script slice merges one commit per slice into its lane with its RED, GREEN and (where
   visual) frame evidence in this plan; the committed H door compiles identically after every non-fix slice
   (`engine_sha256` aside) and after every FIX slice its changed instants are listed and read.
4. Goldens are re-pinned once per wave, at the merge, with a sha table; `page-boxes.v1.json` is regenerated only by
   the parent (`measure_page_boxes.py --write`).
5. Every built capability updates its CAPABILITIES row and card / recipe in the same commit (the shared registry
   process); `effects_catalog_check.py` 0 failures; `build_docs_layers.py --check` in sync (after T1).
6. The whole-suite run on lane B at P72's last merge is green or each red is a named strict xfail with its row. T40
   (the dock's known three 9:16 reds) is this acceptance's precondition.
7. P72-HG1 is framed on the queue in T0 and served at the end (T39).

## Scope

- T0: the bookkeeping - archive rows, `⏸️` rows, plan statuses, queue rows, the backlog's active queue, the five parent
  decisions, the live coverage check.
- T1-T4, T28-T32, T44: tooling and docs that no P70 / P71 slice owns.
- T6-T27, T40, T41, T43: the engine and gate rows, by function, sequenced behind P70 / P71.
- T33-T34: the two research orders under the claims gate.
- T35-T37, T42: the design sheet, the P69 hand-off list, the one-shot comparison, the agenda beat's (a) form.
- T38-T39: integration and the closing gate.

## Not Building

- **Any P70 or P71 slice's work.** Those plans carry their own slices; P72 references them (ALREADY-PLANNED: R26-307
  P71 T13, R26-309 P71 T6, R26-313 P71 T5, R26-33's ping P71 T22; P70 T5-T12; P71 T3b, T5, T6, T8b, T12-T39; landed
  since draft 1: P70 T2 `3600ec5`, P70 T13 `35a2130`, P71 T7 `a469501`). R26-261 is no longer ALREADY-PLANNED: P71
  names it nowhere and T3b's acceptance has no title clause, so its title half is P72 T26 (8), after P71 T3b. P71 T8 is
  DROPPED (E99 s129); T0 marks it.
- **R26-44's wire** - the operator's doctrine call, triggered: "Ask on the first cut that threads a line"
  (`hist:462`). T0 keeps it as a `⏸️` row; no slice builds it.
- **M38's threshold** - the interim WARN is the status quo (P65 T7); the operator's question from p65-hg2 is on the gate
  list, and nothing changes until he answers.
- **The dock's `under: hover|blur`** - P71 T15, one commit (E99 s124 amended).
- **H body adoption** of any fix beyond the P69 hand-off list (T36): the body rows are P69's (T32-T34), held for
  P69-HG3 (the operator, 2026-09-25: "hold it all for a clean hg3 view").
- **The other lanes' plans**: MP-FED-LIQUIDITY, SHARED-MODEL-ENGINES, knockout-five-animated-variants,
  mp-series-visual-grammar, SCRIPT-REVIEW-CLEARANCE (Astra / the Codex MM lane); MP-AI-USEFUL and MP-NORMAL-OUTREACH
  (the package lane; they carry R26-66 and R26-88).
- **The six relation verbs beyond `pin`** (R26-105), unless the parent decides otherwise in T0 (D2).
- **`melt:all`'s engine slice** (R26-147): the design sheet only; the build waits for the operator's word on it.
- **The Japan re-render** (R26-137, R26-52): deferred by E99 s34 ("Japan will be re-rendered eventually, but it's not
  a concern right now"). Both stay `⏸️` rows with that trigger, and so do R26-61 (the first short that asks a figure to
  gesture, bend or hold weight) and R26-15 (each lesson its own slice "when a short asks"). None is archived; archiving
  would lose the operator's "eventually" (BACKLOG-DISCIPLINE `:25`, `:27`).
- **`mechanism-town-v1`** (R26-111): no cut asks for it; a Flow session needs the operator's consent (E36 / E40).
- **Flow orders, paid generators, new plates** (E36; no paid spend).
- **A pushed branch.** release_steward commits; a push needs the operator's current word.

## Human Gates

The operator's standing word applies: "resolve all non-human blockers and i'll review human gates at the end". Every
HUMAN item from the inventory is merged into the gates that already exist; nothing is asked twice. Each gate has (or
gets, in T0) its row in `docs/content-video-engine/review-queue.v1.json` / `REVIEW-QUEUE.md`.

| gate | what the operator judges | where | blocks | new in P72? |
|---|---|---|---|---|
| **P68-HG1** | (1) does Script H read as yours (any line sent back goes to the next letter, never a patch); (2) does the package (the locked title, the FINAL thumbnail, sentence 1) stand for the Facebook post and the YouTube re-upload | queue `p68-steel-and-paper-h-hg1`; `steel-and-paper/SCRIPT-H-VO.txt`, `SCRIPT-H-GATES.md`, `SCRIPT-H-JUDGE.md` | the upload | no |
| **P68-HG3** | the VOICE for the long form (the takes auditioned on the unit); the caption size question (A) and the plate balance only if P69-HG3's one-look pick does not settle them; the agenda beat on ONE card in BOTH forms the row owes (R26-229: (a) the ~20 % park with a camera pan, built by T42 in a private build; (b) melt to a ball, splash onto the slate, built on the 30 s bed) | queue `p68-steel-and-paper-h-hg3` (drift already answered: s84) | the voice of the render | no (R26-229 (a) and (b) folded in) |
| **P68-HG4** | the whole cut with the 1440p render; each remaining gate FAIL with its ruling; the Facebook file and the YouTube question. Printed on the card, not asked: R26-216's computation - which motion rows are NEW verdicts against ep1's 16-of-35 baseline (the H report's rows diffed against `build-f`'s) | queue `p68-steel-and-paper-h-hg4` | the upload | no (R26-216 printed) |
| **P69-HG1** | the chip's DEFAULT landing (`springPop` vs the stamp, one proof beat built twice) and whether the stamp's cue hits on the contact frame (`STAMP_CONTACT_S`); the ring-from-the-enter item is already closed by s121 (3) | P69 T13's proof door; queue row added in T0 | the chip default; one constant | queue row new |
| **P69-HG2** | the first prop on its own card: row 15's Fed stamp, frozen, with its enter / contact / rest frames and cue | P69 T23's card; queue row added in T0 | none now (rows built; "read at the end") | queue row new |
| **P69-HG3** | ONE look for the whole H episode: every page on the default profile vs every page in the long form, the whole episode rendered twice from one build at the same instants - BOTH sides from ONE lane-B sha, the lane-B head when P69 T11 runs (named on the card; "The HG3 pin" lists which P72 slices are in it). Folded in: the default page's sans face (R26-259, Inter vs the fallback), row 7's card line names at half the phone floor (R26-289 - if refused, a taller card) | P69 T11's build; queue row added in T0 | P69 T33 (held) | queue row new |
| **P69-HG4** | the body read on frames beside build-f's at the same instants (sha-verified 1440p), the critic run once, the gates; folded in: P67 HG1's question - did the critic's two scores say something the gates did not | P69 T34; queue row added in T0 | P68 T7 / HG4 | queue row new |
| **P70-HG1** | the nine verbs' beats played with the take beside their Bravos frames; the ONE adoption question (which verbs a body row adopts); bringing P70 T8's paper prop out of quarantine; the chapter pill's look (P70 T9 / T10): the key rail's white capsule or a crimson pill like BUB's - one card, `scratchpad/p70-t9/frames/hg1/chapter-candidate-sheet.png`; and whether H adopts an act (the proposed swap "The bubble" -> "The paper" on "It's in the paper wrapped around the steel") | queue `p70-hg1-the-nine-verbs` | nothing inside P70 | no |
| **P71-HG1** | each verb as a beat with the take beside its Bravos frame; each engine fix before and after at the H instant - including the four whose code landed and whose rows T0 archives as "code landed; the operator's read at P71-HG1": R26-308 (`11b94d1`), R26-310 (`e6aaa30`), R26-312 (`7789afa`), R26-314 (`ef96cee`); the ONE adoption question | queue `p71-hg1-the-bravos-verbs-wave-3` | nothing inside P71 | no (four reads named) |
| **P54-HG3 = the one-shot comparison, in two steps** | **step A (before dispatch to Astra):** the bake-off brief (`BAKEOFF-ASTRA-FABLE.md`, written by T37 - not on disk today), and the operator confirms the scope change: T37's three whole, labelled one-shots supersede P54 T7's one-beat, unlabelled watch. **Step B (after the watch):** the verdict - the three one-shots on one loop (one-shot #3 as authored by Fable, then Opus's, then Astra's - E99 s66's order) side by side on M35-M46 and the parent's read; R26-175, R26-135 (4) and P54 T7 answered by one card | queue `p54-hg3-astra-fable-bakeoff` (step A's brief attached by T37 before Astra's run; step B's cut refreshed after) | Astra's dispatch (step A); nothing (step B) | no (three items merged; the scope change is new) |
| **P65-HG2's M38 question (R26-168) (open)** | "does M38 return to a FAIL at 0.60, move, or stay the interim WARN?" - asked on the p65-hg2 card and never answered (`review-answers.jsonl` holds only the six `#recipe:` answers; s84 is silent on M38). The interim WARN (`M38_INTERIM_WARN = True`, P65 T7) is the status quo until he answers - not a parent ruling | the existing queue item `p65-hg2-the-reproved-set-and-m38` (its six recipe answers are ruled; this is its one unanswered question), shown as one line on P72-HG1's sheet so it is judged once | nothing (the WARN holds) | no (an old question, still open) |
| **P72-HG1** | the closing sheet, one line each, frames served: (1) s130 (1) the fill glow on the gauge and the primary bars at full size and at thumbnail width beside Bravos (built: lane B `ee7d5fc`, inside Bravos's band; at 256 px it barely reads - is that the strength you want, or a stronger dial? sheet `scratchpad/p72-t10/frames/SHEET3-256.png`) (a watch, the ruling is made); (2) R26-257 the extruded bar's shadow re-lit from the stage light before / after ("on the operator's read", the row); (3) R26-146 the ball's `body=blend` clip; (4) R26-147 the `melt:all` design sheet (a yes / no to build); (5) P50 T7's quarantined still `art-embed-washi-tv` (the frame read it waits on); (6) R26-334's pick - the balance's sign-ink pill, from T41's candidate sheet; (7) R26-335's read - the prop hatch's strength on charcoal at 1x, from T41's sheet; (8) M38's open question (the row above) - P72 T3 applied the operator's s84 recipe denials, which drops the Japan cut's M38 reading - and the reference - from 0.76 to 0.48; M38 is the interim WARN, so this matters only if the operator makes M38 a FAIL. (9) R26-368 (a), the strobe: E99 s36 puts everything but camera and speed on 2s; P72 T32 measured H beside Bravos and Wealth Logic with one pixel tool - sharpness does not separate them, the step rate does (the references step sharp marks in the 100-300 px/s band on nearly every frame; H steps its end-labels and a bars edge on 2s) - keep s36, or put this band's sharp marks on 1s; the finding's sheets (`docs/research/runs/p72-t32/`). Attached as reports, not asked: the burndown's final-state table (every id in the live universe and its state, `coverage.py`'s output) and s130 (2)'s measured check - the seal's contrast is at least 3.0:1 on a mid-tone photo (T11), with its frames (10) the listened pass on H's sound (P72 T20, lane B `4e077e4`): the 12 hand-off cues moved onto the card's first frame, a cue at each suck, and every accent (landing, page enter, dip, suck) STARTED at E81's 9 dB under the voice (the door's half held for the lane merge, `scratchpad/p72-t20/door-merge/h-door-t20-e81.patch`) - tune by ear (E81 apply 2) and R26-363 closes on it; the pass closes R26-36 (H's `:cut;then=` rows read as cuts - the pins hold) and R26-35 (Tokyo's recorded swell drops at 76.99 s against the camera's 76.83-77.28: the kit's default holds it, the approved cut stays frozen, E45) (11) the spread's hue (P72 T49, lane B `9a59dd4`): the fill now reads at D40's brightness and blooms (your "a dial not a recipe change"), but its ink is still `--lp-neg`, a brick red, where D40's is a deeper crimson with a stronger halo past the end - keep our red, or take D40's hue for spreads? sheet `scratchpad/p72-t49/frames/SHEET2-acceptance-full.png` (12) the melt's two re-pinned looks (P72 T23, lane B `151636d`, landed ON by your word): the gather's axis hairlines now curl into the spiral with the series (E99 s51's approved gather - only the hairlines change), and a two-ink morph hands the ball's ink over by a sweep (a crescent of the new ink) instead of a muddy mix - keep each, or turn its dial off (`MELT.G_LINE_CURL`, `MELT.HAND_INK_ON`: the old bytes, 0 px)? sheets `scratchpad/p72-t23/frames/sheet-139-gather.png`, `sheet-389-hand.png` (13) R26-371 the keyword box on a crimson plate: today sunflower on crimson reads 2.14 / 2.73 (under the 3.97 floor) - pick B darker box, C deep crimson box (the suggestion; 4.89 / 5.78), D chalk ink, or E charcoal on sunflower; the next short only (sheet `scratchpad/p72-t46e/frames/r26-371-sheet.png`). (14) R26-357 every 16:9 source line sits at y 959-965, inside YouTube's controls band (>= 959.8): a WARN first, then a sheet of the line lifted to y <= 938 beside today's on two H pages - moving it re-pins every 16:9 golden. (15) R26-372 M48's method: the keyword's own shadow (~22 px) hides the box under it; reading the ground as the brightest non-ink pixels fixes orange-on-crimson but moves the reference strip's 3.97 floor (E38) - keep today's method or re-measure the reference with the new one? (16) R26-369 the 9:16 agenda: narrow rows now shrink their icon and medallion so the words hold (24.6 -> ~46 px) - the icons at 130 px, keep or size them? (sheet `scratchpad/p72-t46c/frames/r26-369/sheet-agenda-9x16.png`). (17) the STACKED 9:16 dock pair: scaled badge rails collide (card 2 over card 1's rail, the caption over card 2's), so the pair stays as today - where should the pair's rails mount? and R26-365 (c): at 9:16 one of 8 bars writes its value - keep the thinning you chose (2b7b6a4; "7 of 8" is in the pill)? (sheet `r26-365c/`). (18) R26-381 four panels at phone: a 2x2 cannot hold (cells 210 / 248 px vs 327) - the 2-up (panels 3-4 on a second page, the baseline pick) or three panels? (sheet `r26-381/sheet-r26-381-candidates.png`). (19) R26-388 (b) the verdict stack's rail member at 9:16: cap the rail box at the landscape box's height (136x166, the whole card reads; one line) - the baseline pick (sheet `r26-388b/sheet-r26-388b.png`). (20) R26-325 / R26-397 `.lp-page`'s will-change layer: dropping it makes a played frame equal a cold seek (0 px on 48 of 48, H 333.42 / 197.5) but moves 138 goldens at raster level and antialiases the long form's top row (row 1 (17,23,30) -> ~(110,109,100); sheet `scratchpad/p72-t46a/frames/sheet-h-A.png`) - drop it (patch 2 is ready, `p72-t46a-r26-397.patch`) or keep today's layer? (21) R26-330 the spiral's return runs its field phase over a dark board (~0.64-0.9 s) after an authored dip - three candidates in `scratchpad/p72-t46a/NOTES.md`, frames `frames/step0-330/`; or the lane A option (cut, not dip). | `$SP/p72-t39/` served frozen on its own port; queue row `p72-hg1-the-backlog-burndown` added in T0 | nothing inside P72 | yes |

**Other lanes' gates (listed, not owned):** SHARED-MODEL-ENGINES HG1-HG4 and MP-FED-LIQUIDITY HG3 / HG4 (Astra, on the
queue); the Martial Matters lane's phone-frame reviews (MM-EXCH-01); R26-66's hand-off frames (the package lane's
Normal-for-Which short, `MP-NORMAL-OUTREACH` T3).

**Closed gates (no ask):** P65 HG1 (queue `lab-smoke-r2-plate-carries-a-card`, `lab-batch-r1-plate-carries-a-card`) -
the batch was pulled by the parent on 2026-09-17 and the operator said he cannot answer it until HG2 is resolved, which
s84 did; the cards are withdrawn (s82: no candidate-by-candidate cards). P47's :8738 watch - superseded by Tokyo v2 /
v3b (ruled, uploaded). P51 gates 2 and 3 - closed as not yet meaningful (REVIEWED 2026-09-14). P67 HG1 - folded into
P69-HG4.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (Dispatch mapping, Hand-off policy, Lane write sets, "Before anything reaches
  main").
- `$SP/p72-plan/INVENTORY.md` - the verdict and evidence for every item; a slice's brief quotes its lines.
- `.claude/PRPs/plans/P70-THE-BRAVOS-VERBS-WAVE-2.plan.md` ("The lane-B workflow", "Who owns what") and
  `.claude/PRPs/plans/P71-THE-BRAVOS-VERBS-WAVE-3.plan.md` ("What P71 must not touch", "Who owns what inside P71",
  the registries list, COMMON-TAIL, BRAVOS-FRAME). Their ownership tables bind P72: a P72 slice that finds it must edit
  a function a P70 / P71 slice owns stops, and the parent sequences it.
- `.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md` Human Gates (`:169`-`:203`) and T32-T35.
- `docs/content-video-engine/BACKLOG.md`, `BACKLOG-DISCIPLINE.md` (the archive rule: "Archive only when the evidence
  identifies the relevant artifact, measured result, test, commit, or operator ruling"),
  `backlog/archive/2026-09-completed.md` (the row format), `BACKLOG-HISTORY-2026-09.md` (each row by id).
- `docs/portable/OPERATOR-RULINGS.md`: E38 (thresholds off the reference), E45 (approved cuts frozen), E49, E99 s31
  (generated images out of git), s34, s67, s69, s74, s77, s84, s106 (the engine advises), s116 (the sound follows the
  frame), s117 (lines bloom), s123 / s127 (the seal gold), s126 (M48 blocks), s128 (a stamp over the world), **s129
  (no word-count gate; P71 T8 dropped), s130 (filled marks glow; a seal on a photo adjusts its gold)** (`:3389`,
  `:3391`).
- `docs/runbooks/RESEARCH-REPLY-CONTRACT.md` and `content/video_engine/scripts/verify_research_claims.py` (T33, T34).
- `docs/WORKTREE-REGISTER.md` (lane B's row names the P72 writer per function).
- `docs/content-video-engine/CAPABILITIES.md` rows the slices extend (by title; T1 fixes the index first).

## Execution Path

### The lane-B workflow - P70's, as P71 amended it

P70's steps 1-6 and P71's four differences apply verbatim: a scratch export of lane B at the slice's base; the base
fail set first; RED, then GREEN, then REFACTOR, logged under `$SP/p72-tN/logs/`; the committed H door's byte identity
by `$SP/p69t84/scripts/door_identity.sh` (a FIX slice lists its changed instants instead and writes each before /
after to `$SP/p72-tN/frames/`); an LF-only patch, `git apply --check` clean, with its sha256 and per-file pytest counts
(base vs patch); the parent's review, the reviewer where named, and `release_steward` commits with explicit paths.
Every Expected RED is probed at the base in step 1. A key the slice adds is refused BY NAME when malformed (s106: "a
silent drop is neither advice nor refusal").

P72 adds one step, **step (0) CONFIRM-OPEN**: before RED, the implementer re-probes the row at the slice's base. A row
already fixed at the base (a P70 / P71 slice may have fixed it in passing) is not rebuilt: the slice records the sha
that fixed it and the row goes to T0's next batch as DONE-UNCLOSED. Several rows (R26-21, 35, 73, 106, 153) are
marked "step (0) decides" in the inventory for this reason.

### One writer per function - what P72 waits on

| P72 slice | the function it edits | owned first by (must land before) |
|---|---|---|
| T7 | `gate_motion_density.py`: a NEW verdict-stack event read, the record-typing credit, a NEW refused-transform INFO row, a `--beat` window in `main` / `run`, a settled depth card's row in `_in_frame_faults` (R26-132 (2)), and a flight's frames as INFO in `_over_build_faults` (R26-202 (a)) | P70 T8 (`_landings`, `_arrivals`), P71 T7 (`load_squint`, `_squint_gate`, `run`'s `squint=` - landed `a469501`), P71 T15 (`_layout_faults`, `_over_build_faults`) - T7's `run` change is unioned on top of `a469501`; its R26-202 (a) edit to `_over_build_faults` is its own commit, after P71 T15 merges |
| T6 | `probe.py`'s value read (`:378`-`:398`: the zero line, the visible ticks, `line.grid, line.ax`), gate `_value_faults` (`:2679`), `ledger_page` `form_error`'s `gauge:h` refusal and the engine gauge branch (`:10782`-`:10972`, P70 T3's, landed) | P70 T3 (landed `e43c3d8`) |
| T10 | a NEW `lpFillGlow` beside `lpHotFilter` (`:11191`), one call line in the gauge's fill group (`:10805`) and one at a primary bar's rect; `measure_line_bloom.py` a NEW `--fill` mode; the band file's fills entry | P70 T3 (landed); P72 T6 (it edits the same gauge branch, `:10782`-`:10972`, so T10 rebases on it); P71 T24 (`lpBarMorphs`), T25 (projected bar paint), T29 (the `glow` outline species), T30 (`paintSolo`), T31 (story bars) - the call lines are placed where those slices' lines are not; the parent's `--3way` order is T10 before T25 / T29 / T31 or after all three |
| T11 | `species/chip.mjs` `sealGold` (`:140`) - it reads the measured ground as `stampRingInk` (`kinetics/stopaction.mjs:463`) does | P71 T12 (in flight on `chip.mjs`); before or after P71 T18 (also `chip.mjs`), the parent's order |
| T12 | `lpPanelStart`, the panel reveal clock, the panel layout per readability preset, the panel tick write, the one-bar stacked page's layout on `longform:phone` (R26-339: the T64 key's place, the category label's wrap) | P70 T4 (landed `d0dd19b`); P70 T5 (the brace) must not be mid-flight on the stacked page's layout - the parent orders them |
| T13 | the value / unit formatter (a prefix AND a suffix), the tick column's left bound, the `hlines` label placement (`:9013`-class), the bars' category-label side on a signed page; `ledger_page` unit validation; the treemap / tiers constants (`ledger_page.py:2070`, `:2072`) | P71 T25 and T31 also edit `buildLedgerBars` - T13 lands before both (they rebase) or after both |
| T14 | the caption layer on a picture plate (a plate's caption room, a contrast backing), `build_caption_pages.py`'s tokenizer, the caption's hand-over at a `morph:prop` exit | none (P71 T15 adds `#dockveil` to the template - a different region) |
| T15 | `ledger_page.page_boxes` (every page text box: basis, source, wrapped names), the compiler's E65 `empty`-room placer | T13 (the same pages' labels) |
| T17 | compiler: `validate_page_build_spans` (`:6776`), the page-warning print, the MELT twins beside `MELT_S` (`:124`), the tip-pill width WARN, `world.morph`'s `series` key, `IDLE_KINDS` on a plate world (`:87`), a camera-identity INFO, `dock_place`'s prop pad, `_freeze_row_errors`' ruler-scroll WARN (R26-333; P69 T49's function, landed), the `compare`-beside-`remake` check (R26-143) | P71 T5 (`row_stamp_fits`, `stamp_reserved_box`), T6 (`scene_exit`), T13 (`ledger_page.validate`), T15 (`DOCK_OPTS`, `dock_opts`, `read_over_build`) - none of these is T17's |
| T18 | `species/figure.mjs` `paintFigure`'s anchor on a bars page, a figure-restates-the-value WARN (compiler, s106), a ring `value` target on a bar, the emphasized pill's yield | T13 |
| T19 | `render()`'s dock painter (the per-scene box), the dip's dock exit, the hatch under a dock camera, `paintPress`'s hold, a NEW `rel: pin` on a dock, the throw's entry side (`flip++%2`, engine `:6179`) and a NEW `side=` row option (R26-202 (b)) | P70 T8 (the dock-arrival branch), T9 (`paintChapters` in `render()`), T13 (`idle: hold`); P71 T6 (the dock exit), T15 (the hover), T19 (`paintDockVerdict`), T23 (`park_at`) |
| T20 | `authoring/audio.py` (the cue binder, a suck cue, the slot hand-off's cue instant), the bed envelope | P70 T8 (`authoring/audio`) |
| T21 | `meltMount` / `paintMelt` (after P71 T4's key, landed), `render()`'s melt call and hand ring, the snap's card box, the dock slot state, the title glow's repaint | P70 T8, T9; P71 T6, T15, T19 |
| T22 | `species/verdict.mjs`, the compiler's verdict member model, the dock door's freeze check | T7 |
| T23 | `species/melt.mjs` options (`OFF_SCREEN`, `body=blend`), the gather's axis sampling | T21, T30 |
| T24 | the morph's ground floor, `polyStrip`, gate M17's measure (`:3875`) for a planted source | T7 is the gate's other writer - disjoint functions |
| T25 | the compiler's ken tuple window, `paintPlanes`' drift (the push reach is DONE: `camera_reach`, `af869b7`, P69 T26b - not rebuilt) | P71 T32 (the `pedestal` key) only if the ken window reads `kinetics/camera.mjs` |
| T26 | `lpPaintStates`' per-state domain and box, a NEW axes-recede token, the long-form palette's named-colour table; `lpPaintChart`'s bar leave law (R26-331) and its `build_to` cap on a state whose build has not started (R26-332); the recast's title rewrite (R26-261's title half) | P71 T3b (`lpAxisHandOver`, the plain recast, the arriving-layer rule), T13 (`lpRightAxis` in `buildLedgerLine`), T16, T28, T39; P70 T2 (landed) |
| T40 | `page_place` / `free_bands` / `dock_place`'s 9:16 band choice, `ledger_page.page_boxes` for the schematic and panels pages at 9:16, `measure_page_boxes.py`'s lists (the parent runs `--write`) | P70 T2 (landed `3600ec5`); P71 T15 owns `DOCK_OPTS`, `dock_opts`, `read_over_build` - T40 edits none of them; T15 (P72) rebases on T40 |
| T41 | the balance species' per-side `tone:` key and its pill (R26-334); no default change for the hatch (R26-335 is a sheet) | P70 T7 (the balance) |
| T43 | `paintBracket`'s label side and an "above" fallback; `check_brace`'s room estimate (a WARN) | P70 T5 (the brace) |

The registries (`SPECIES_KINDS`, `PAGE_SPECIES`, the `_validate_entry` chain, `LP_PANEL_KINDS`, `buildPerform`'s return
and `paintPerform`'s dispatch, `DOCK_OPTS`, `sync_kinetics` module order, the cards, the golden lists,
`measure_page_boxes.py`'s lists) stay the parent's union, as in P70 / P71. Generated files are never in a patch.

### Waves

At most four slices at once (the runbook's concurrency).

| wave | slices | why together |
|---|---|---|
| 0 | T0 | the closing pass, in batches; it runs BESIDE waves 1-2 and blocks only the slices that name it (T6 and T40 do not) |
| 1 | T6, T40, T44, then T1, T2, T3, T4 (after T1), T33 | **T6 is the highest priority** (R26-318, a truth gate's false PASS) and the first lane-B dispatch, on the plan's approval alone; T40 clears the suite's known three reds (acceptance 6's precondition). Then lane-A docs, tests, recipes, research; T1 before T4 (both edit `CAPABILITIES.md` with line anchors) |
| 2 | T7, T8, T9 (+ T29, T31 as tooling threads) | the gates, the determinism infrastructure; T7 after P70 T8 |
| 3 | T10 (after T6, T9), T11, T12, T13, T14 (+ T30, T34, T41, T42) | s130 and the page families; T11 after P71 T12; T13 before P71 T25 / T31; T41 after P70 T7 |
| 4 | T15, T17, T18, T32, T43 (+ T27's first commits) | the boxes, the compiler, figures, the bracket - each after T13; T43 after P70 T5 |
| 5 | T19, T20, T21, T28 | the dock branch and `render()` - after P70 T8 / T9 / T13 and P71 T6 / T15 / T19 / T23; T28 after T7 and T20 (its `--write` and bind-entry items) |
| 6 | T22, T23, T24, T25, T26, T35 | species and states, after their P71 owners |
| 7 | T37, then T39 | the one-shot comparison after P71's last merge, R26-336 (T31) and P54-HG3 step A; the closing gate |

At most four slices run at once, so wave 1's seven start in the order written. T36 (the P69 hand-off) runs at each
merge; T38 (integration) closes each wave.

### The HG3 pin - which P72 slices are in P69-HG3's A/B

P69-HG3 (P69 T11: the whole H episode, default profile vs long form) builds BOTH sides from ONE lane-B sha: the lane-B
head that exists when P69 T11 runs. T11's card names that sha, and the parent never builds the two sides from two
heads. The rule for a P72 slice that changes what the committed door renders:

- **Before HG3 (the default):** it lands on lane B before P69 T11 runs, when its wave allows. Both sides get it, so the
  A/B still shows only the profile. The parent does not hold T11 for a P72 slice. A before-HG3 slice that has not
  merged when T11 runs is named on T11's card as "not in this pick".
- **Held (the exception):** anything that changes the long form's H rows 1-13 by retrofit (an authored row edit) is
  P69 T33's, held for HG3. P72 never makes those edits; T36 lists them on P69's pass list.

| slice | what it changes on the committed door | HG3 |
|---|---|---|
| T9 | fonts settled before capture (R26-243 / 251): a fallback-face frame becomes the true face | before |
| T10 | the fill glow on the gauge and the primary bars (every bars page) | before |
| T12 | row 21's panels build in view (R26-315); the tick write | before |
| T13 | units and label clearance on the bars pages (rows 17 and the capex pages) | before |
| T14 | the caption's contrast backing on a plate (rows 12, 17); rows 7 / 13 are shown in a private build only, never the committed door | before (the engine backing); held (rows 7 / 12 / 13 / 17 declaring `caption_room` - T36) |
| T15 | the E65 `empty` room keeps text clear (unauthored placements only; authored places stand) | before |
| T17 | INFO / WARN lines; R26-258's prop pad (unauthored placements only) | before |
| T18 | row 17's 94 bars page prints its value once (the hand-over) | before |
| T19 | docks keep their box, leave with the dip (rows 17, 23) | before |
| T20 | the suck's cue; the hand-off cue (sound only; both sides) | before |
| T21 | melt purity (R26-321 moves every melt golden), the snap box, the title glow | before |
| T26 | a page's later states; R26-331's bar labels and R26-332's arriving state (H 663.4, 80.49); R26-261's title | before |
| T27 | R26-57 (text rendering), R26-123 (the caption-life default blend, unauthored rows), R26-257 (the extruded light), R26-2 (opt-in, none) | before (R26-57, 123, 257) |
| T43 | the bracket's label side at 16:9 (the railway page) | before |
| T11, T22, T23, T24, T25, T40, T41 (and the tooling slices, T1-T8, T28-T34, T44) | opt-in keys, 9:16-only placement, a seal on a photo plate, gates or scripts - no H frame changes unless a row authors the key | neither (no H change); T41's hatch strength, if the read picks one, lands after HG3 |
| T36's items | row 1's push and row 15's pull re-aimed (R26-281 / 283), row 20's text, row 23's flips | held (P69 T33 / T34) |

**Routing.** `implementation_luna` (Opus) builds most slices; `junior_developer` (Opus) T1, T11, T27; `speedster`
(Sonnet) makes T0's archive and status lines from exact text; `reviewer` (Opus) reviews T6, T7, T10, T11, T15, T18, T19,
T21, T26, T40, T43 (a truth gate, a motion gate, a visual default, placement, seek purity); `explorer` runs T0's
spot re-checks and T33's verifier reads; `release_steward` commits and never pushes without the operator's current
word. The parent keeps the briefs, the frame reads, the registry unions, CAPABILITIES, the merge, the decisions and the
operator.

## Patterns To Mirror

- **The archive row**: `backlog/archive/2026-09-completed.md`'s table (id, what closed it, the evidence command or sha) -
  T0.
- **An engine fix with a strict xfail that flips**: R26-315's pin in `tests/test_companion_bars.py` (it flips when
  fixed) - T12; R26-238 / R26-240's `xfail(strict=True)` - T2.
- **A truth gate read from a probe file, INFO until measured, FAIL on a measured fault**: M32's `seam-frames.json`
  read; P69 T87's M47 (`965c4e2`) - T6, T7.
- **An emissive halo, seek-exact**: `LP_HOT` / `lpHotFilter` (`:11173`-`:11281`), measured off Bravos by
  `measure_line_bloom.py`'s band (`assets/bravos-line-bloom.v1.json`, `--band --check`) - T10.
- **An ink chosen by the measured ground**: P70 T1c `stampRingInk` (`kinetics/stopaction.mjs:463`) - T11.
- **A fix that keys a mount to its boundary**: P71 T4 `7789afa` (`meltMount(..., key)`) - T21.
- **A glyph write that finishes at its window's end**: P71 T1 `ef96cee` (`figureSubGlyph`) - T12's tick write.
- **A new field refused by name when unknown**: P69 T64 `c0836b8` (`BAR_FIELDS`) - T13, T17, T19.
- **A verified research reply**: `b67df03` (R26-306: five objects, each tiered, the rejected ones named) - T33, T34.
- **A recipe proved as a beat**: P69 T35's proof door (`_proofs/p69-recipes/`, imported, never edited) - T3's melt
  recipe.

## Task Slices

**TDD fields (`tdd-v1`, as P69-P71 define them).** Regression is the command that must go RED first. Expected RED is
what it prints before the change (predicted from the code; re-probed at the base in step 1). The reserved fields (Red
evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read) are `pending` and hold
the verbatim tails, the base fail set, the frame paths and the merge sha.

**COMMON-TAIL** is P71's (each command in its own process, unpiped): `node --check
docs/content-video-engine/samples/scene-evidence-engine.mjs`, `python content/video_engine/scripts/sync_kinetics.py
--check`, `python -m pytest -q content/video_engine/tests/test_golden_frames.py`, `python -m pytest -q
content/video_engine/tests/test_effects_catalog_drift.py`, `python -m pytest -q
content/video_engine/tests/test_build_effects_catalog.py`, `python content/video_engine/scripts/effects_catalog_check.py`.

**BRAVOS-FRAME** is P71's (`ffmpeg -ss <s> -i "<video>" -frames:v 1 $SP/p72-tN/frames/bravos-<VID>-<mmss>.png`; the
videos under the main checkout; BOOM at VERIFY.md's TRUE times).

### T0: The closing pass - 167 items archived or closed with their evidence, five kept as triggered rows, the plans' statuses corrected, the gates on the queue, the five parent decisions recorded, the coverage read live
- Status: done (2026-09-25, lane A c02deb4 / d0b9410 / 4128aa5 + the part-2 commit; `coverage.py --root <lane A>` exits 0, UNMAPPED 0; the parent read D1-D5 and confirms D1 as recorded)
- Owner: parent; speedster writes the archive rows and status lines from the exact inventory text, one batch per commit; explorer re-checks a 10 % sample of the shas before each batch commits
- Depends on: the operator's approval of this plan. T0 runs beside waves 1-2; T6 and T40 do not wait on it.
- Write set:
  - `docs/content-video-engine/backlog/archive/2026-09-completed.md` (one row per DONE-UNCLOSED / CLOSE-* id: the id, what closed it, the sha / file:line / ruling - copied from `INVENTORY.md`). Revision-1 rules for the archive rows: R26-308, 310, 312, 314 read "code landed (`<sha>`); the operator's read at P71-HG1" (BACKLOG-DISCIPLINE `:20`: a code change does not close a visual task); R26-283 and R26-281's engine half cite `af869b7` (P69 T26b, `camera_reach`) - R26-281's row-1 re-aim and R26-283's row-15 re-aim stay open in T36; R26-127 cites `bf539e3` (the `bridge_inbox` hook self-starts the daemon); R26-108 cites H's own timeline (`build-h/steel-and-paper-h.timeline.json`: 23 of 25 scenes carry species, 14 carry pages - the long form now speaks the species vocabulary the open half asked for); R26-102 cites E99 s13 (`OPERATOR-RULINGS.md:2965`: "the 2026-09-13 readiness review is superseded; plans are written to be executed by either Claude or GPT"); R26-155 cites E99 s56 (`OPERATOR-RULINGS.md:3230`: "P61 HG6-2 closed" on approval). NOT archived while a half is open: R26-219 (T43), R26-9 (TR-3, T27), R26-143 (T17), R26-36 (T20, a listened pass owed), R26-132 (T7), R26-202 (T7 / T19 / T4), R26-229 ((a), T42);
  - `docs/content-video-engine/BACKLOG.md` (the active queue rewritten: the P69 / P70 / P71 / P72 umbrella rows with their children once, the OTHER-LANE rows with owners, one row per human gate, and the five `⏸️` triggered rows with their triggers - R26-44 "Ask on the first cut that threads a line" (`hist:462`), R26-52 and R26-137 "Japan will be re-rendered eventually, but it's not a concern right now" (E99 s34, `hist:581`), R26-61 "THE TRIGGER: the first short that asks a figure to gesture, bend or hold weight" (`hist:478`), R26-15 "The lessons named for a slice when a short asks" (`hist:447`) - plus D4's R26-214 (c) "no ambient-lane order until a cut asks"; `LEGACY-REVALIDATION-2026-09` closed by this pass; R26-31, 35, 36, 43, 45, 57, 65, 66, 85, 123, 124 each moved to its verdict);
  - `docs/content-video-engine/BACKLOG-DISCIPLINE.md` (the second-pass report: before/after counts, the archived ids, the `⏸️` ids, the five parent decisions);
  - plan status lines: P47 (retired; T4, T6, T7, T8 superseded - evidence per INVENTORY section D), P48 (complete), P50 (T7 waits on P72-HG1 item (5), the quarantined still; P50 -> complete after that read), P51 (complete), P53 (complete), P54 (T9 done; T7 -> P72 T37; HG3 kept as its two steps - the brief before Astra's dispatch, the verdict after the watch), P65 (T6 closed per D3; T9 done at T3's merge; then complete), P67 (T6 done; complete), P68 (T4 done `6e78106`; T5b done), P69 (T85 done `ffa2877`, T87 done `965c4e2`), P71 (T8 DROPPED, E99 s129 (4));
  - `docs/content-video-engine/review-queue.v1.json` + the regenerated `REVIEW-QUEUE.md`: rows `p69-hg1-*` .. `p69-hg4-*`, `p72-hg1-the-backlog-burndown`; `lab-smoke-r2-plate-carries-a-card` and `lab-batch-r1-plate-carries-a-card` closed as withdrawn (s82 / s84 cited); `p54-hg3-astra-fable-bakeoff`'s text pointed at T37's two steps; `p65-hg2-the-reproved-set-and-m38`'s unanswered M38 question named on P72-HG1's row, not asked twice;
  - `docs/WORKTREE-REGISTER.md` (lane B's row names P72 and its one writer per function);
  - `$SP/p72-t0/coverage.py` (gitignored scratch; the check below);
  - this plan (status, base, the decisions, T0 evidence).
  The history file is NOT edited: its banner pins the source slice's sha256; the archive row is the closure.
- Parent decisions recorded here - five, none of them the operator's, each with its reason: D1 R26-316 - whether the long form ever renders at `phone` (H runs `middle`); D1 must weigh R26-339, because `longform:phone` is the only preset that holds the brace's 59.08 px text floor, so refusing `phone` would strand the brace (T12 stops if D1 and R26-339 conflict); D2 R26-105 - build `rel: pin` only (R26-267 needs it), the other six verbs wait for a sentence; D3 P65 T6 - close the lab's promotion (recipes are proved as beats in proof doors; the defaults now come from rulings, s124 / s67, not from the lab); D4 R26-214 (c) - no ambient-lane order for a breathing host until a cut asks (local only, E99 s37), recorded as a `⏸️` row; D5 the R26-9 / R26-102 closure, after R26-9's TR-3 is split into T27 and R26-102 cites s13. Recorded, not decided: R26-168 / M38 - the interim WARN is the status quo and the question stays the operator's (the gate list).
- Decisions (recorded 2026-09-25, the parent's - none is the operator's):
  - **D1 (R26-316) - the long form keeps the `phone` preset; it is not refused by name.** P72 T12 makes the panels
    page (R26-316) and the one-bar stacked page (R26-339) hold at `longform:phone`, every text at or above the 59.08 px
    floor. Reason: `longform:phone` is the only preset that holds the brace's text floor (R26-339), so refusing `phone`
    would strand the brace; H itself runs `middle`, so the choice moves no approved frame. T12's stop condition (D1 vs
    R26-339) does not fire.
  - **D2 (R26-105) - build `rel: pin` only** (P72 T19: a dock rides another dock's park, R26-267); the other six
    relation verbs wait for a sentence that asks. Reason: R26-267 is the one open row that needs a relation; the E97
    grill ruled the grammar and its defaults, not a build order, and no other row authors a relation.
  - **D3 (P65 T6) - the lab's promotion step is closed**, and with it T9's "defaults" pointers. Reason: recipes are
    proved as beats in proof doors now (P69 T35, P71 T33-T36); the defaults come from rulings (E99 s124 / s67), not
    from the lab; `authoring/defaults.py` was never written, and HG2 ruled the set (s84). P65 T6 reads closed; P65 is
    complete at P72 T3's merge.
  - **D4 (R26-214 (c)) - no ambient-lane order for a breathing host until a cut asks**, recorded as a `⏸️` row on the
    board. Reason: the ambient lane is local only (E99 s37, no paid generators) and no cut asks for a breathing host
    today; R26-214 (a) and (b) go on in T4 and T17.
  - **D5 (R26-9 / R26-102) - R26-102 is closed on E99 s13; R26-9 closes when its TR-3 lands in T27.** Reason: s13
    (`OPERATOR-RULINGS.md:2965`) superseded the 2026-09-13 readiness review, so R26-102 is archived (batch 3); R26-9's
    TR-1 / TR-2 / TR-4 / TR-13 are done and the doctrine answered its questions, but TR-3 (tag and test `SUCK_S`,
    `DIP_S`, `SLIDE_S`) is not, so R26-9 stays open on P72 T27 and is archived after it.
  - **Recorded, not decided: R26-168 / M38.** The interim WARN (`M38_INTERIM_WARN = True`, P65 T7) is the status quo;
    the question - FAIL at 0.60, move, or stay the WARN - is the operator's, asked once on P72-HG1's sheet (item 8).
- Acceptance:
  1. `$SP/p72-t0/coverage.py` (written in this slice) builds its universe LIVE at run time - never from INVENTORY's id list: (a) every `| **R26-N**` row id in `docs/content-video-engine/BACKLOG-HISTORY-2026-09.md`, minus the ids in the first column of `backlog/archive/2026-09-completed.md`; (b) every row id in `BACKLOG.md`'s active queue; (c) every task in P54, P68, P69, P70 and P71 whose `Status:` is not done / complete / dropped / moved; (d) every item in `review-queue.v1.json` whose status is not ruled / closed / withdrawn. It maps each against the carriers: an archive row; a P72 / P68 / P69 / P70 / P71 slice that names it (for a split row, the slice naming its open half); a `⏸️` row in `BACKLOG.md` with its trigger; an OTHER-LANE owner; a gate in this plan. INVENTORY is one input (the verdict text), not the universe. It prints the unmapped set and exits 1 if any open id has no carrier; the set must be empty. A row filed after this plan (as R26-338 / 339 were, mid-revision) is in the universe by construction.
  2. Each archive batch's shas resolve (`git log -1 <sha>`), sampled by explorer before the commit.
  3. The P69 HG rows and P72-HG1 are on the queue with what to judge, where, and what they block.
  4. The five decisions are quoted in this plan with their reason; the M38 status quo is recorded as the operator's open question, not as a decision.
  5. The five `⏸️` rows are in `BACKLOG.md` with their triggers verbatim, and none of them is in the archive.
- Stop conditions: an inventory verdict the sample contradicts (report, re-verdict, do not archive); a row whose half is open (never archive it; its slice carries the half); a plan owned by another lane (P72 never edits MP-*, SHARED-MODEL-ENGINES, knockout, mp-series-visual-grammar, SCRIPT-REVIEW-CLEARANCE - it sends their owners a note).
- Regression: `python $SP/p72-t0/coverage.py`
- Expected RED: exits 1; the unmapped set holds every DONE / CLOSE id (no archive row yet), R26-331 .. R26-340 until this revision's plan is on disk, and every P69 HG (no queue row yet).
- Validate: `python $SP/p72-t0/coverage.py` then `python scripts/prp_validate.py .claude/PRPs/plans/P72-THE-BACKLOG-BURNDOWN.plan.md` then `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md .claude/PRPs/plans/P71-THE-BRAVOS-VERBS-WAVE-3.plan.md .claude/PRPs/plans/P47-STOP-ACTION-BUILD-ON-AND-THE-CHART-MORPH.plan.md .claude/PRPs/plans/P48-CHART-TO-CHART-TRANSITIONS.plan.md .claude/PRPs/plans/P51-THE-ANIMATORS-LOOP.plan.md .claude/PRPs/plans/P53-WHAT-THE-ONE-SHOT-TAUGHT.plan.md .claude/PRPs/plans/P65-THE-RECIPE-LAB.plan.md .claude/PRPs/plans/P67-THE-VERIFIED-RECEIPT-AND-THE-CRITIC.plan.md .claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md` then `python content/video_engine/scripts/build_review_queue.py` then `python scripts/prp_status.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): RED at 311aad7 - `coverage.py --root <lane A>` exit 1, universe 449, UNMAPPED 170 (153 closure verdicts with no archive row or closed status, the five triggered rows' missing `⏸️` rows, R26-111, R26-168 un-named by its gate row, R26-330 and R26-341..346 uncarried, P69-HG1..HG4 and P72-HG1 with no queue row) - each attributed to the missing closure or carrier, none to the tool; the uncarried rows were carried by `0d2e705` (92 unmapped there). GREEN after part 2: exit 0, universe 313, UNMAPPED 0. Refactor: the gate rule reads a board row's `P<n>-HG<k>` id through its queue row; the archive id regex takes a dated id (`LEGACY-REVALIDATION-2026-09`)
- Evidence: batch 1 `c02deb4` (70 DONE-UNCLOSED rows, R26-0 .. R26-158); batch 2 (53 DONE-UNCLOSED, R26-159 .. R26-314, the four P71 fixes as "code landed; the operator's read at P71-HG1"); batch 3 (20 CLOSE-* rows; R26-102 on s13, R26-155 on s56, R26-124 with the engine's default `eased` recorded); part 2 (R26-176 and R26-181 with their leftovers, LEGACY-REVALIDATION-2026-09, the census reconciled: 64 of its 71 archived, seven carried). Every cited sha resolved with `git log -1` against lane A, lane B and main (0 failed). The board rewritten (P72 / P71 / P70 / P69 / P68 rows with their children once, one row per human gate, the other lane's row, seven `⏸️` rows with their triggers verbatim); `BACKLOG-DISCIPLINE.md`'s second-pass report; queue rows `p69-hg1-*` .. `p69-hg4-*` and `p72-hg1-the-backlog-burndown`, the two lab cards withdrawn, the bake-off card on T37's two steps; the plan statuses (P47 retired; P48, P51, P53, P67 complete; P50, P54, P65, P68, P69 slices closed); lane B's register row names P72. Held open by rule: R26-281 / R26-283 (T36's re-aims), R26-219, R26-9, R26-143, R26-36, R26-132, R26-202, R26-229 (each has an open half and its slice).

### T1: The recall layer builds again - the capabilities index under its cap, its four malformed rows, and the ten search misses
- Status: done - lane A 14c1293 (the index builds, four rows fixed, WHAT_MAX 110) + eaa6d44 (docs_find's all-words fallback for `_` / `-`); lane B's own index is ported in T2 round 2
- Owner: junior_developer (LANE A)
- Depends on: T0
- Items: NEW-1; R26-136 (5)
- Write set: `docs/content-video-engine/CAPABILITIES.md` (the four flagged rows only: `:69` "Dock placement on a page" and `:123` "THE WHOLE-CHART MORPH" carry extra pipes; `:308`, `:309` carry 3 cells), `content/video_engine/scripts/build_capabilities_index.py` (only if the MD's per-record line is compacted - never the cap raised without a stated reason in the constant's comment), the aliases file the docs index reads for R26-136 (5) (step (0) names it), `content/video_engine/tests/test_build_capabilities_index.py`
- Acceptance: (1) `build_capabilities_index.py --check` exits 0 and the MD is under `MD_MAX_BYTES`; (2) `build_docs_layers.py --check` reports every layer in sync and `docs_find.py` prints no `[layers] stale` banner; (3) each of the ten R26-136 (5) terms ("beat plan", "recipes propose", "compile_timeline", "self_watch", "serve_player no-store", "judge the frame", "gate fit", "blind viewer", "retime take", "motion density gate") returns at least one hit that names the right file; (4) no capability row's meaning changes (the diff of the four rows is pipes and cells only).
- Stop conditions: the MD cannot fit without dropping records (report the numbers; the parent decides the cap); an alias would point at a retired capability.
- Regression: `python content/video_engine/scripts/build_capabilities_index.py --check`
- Expected RED (probed on lane A, 2026-09-25): `FLAGGED line 69 ... extra-pipes (5 cells)`, `FLAGGED line 123 ...`, `FLAGGED line 308 ... reference (3 cells)`, `FLAGGED line 309 ...`, `FAILURE docs/CAPABILITIES-INDEX.md is 44904 bytes, over MD_MAX_BYTES 44000`.
- Validate: `python content/video_engine/scripts/build_capabilities_index.py --check` then `python content/video_engine/scripts/build_docs_layers.py --check` then `python -m pytest -q content/video_engine/tests/test_build_capabilities_index.py content/video_engine/tests/test_docs_find.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T2: The suite is green and its pins are honest
- Status: done - lane B a4bfe6a: the lab pins on s84, every species / verb `when` under 260 (the strict xfail retired), the effects layer ranked by field, the guarded Playwright opener, the committed-tree test on a HEAD copy, check 13 (schema); T1 ported to lane B (WHAT_MAX 100 on both lanes); the gallery re-pinned
- Owner: implementation_luna (LANE B)
- Depends on: T0
- Items: R26-244 (the lab-log pins re-read against E99 s84: the live set now includes the 09-18 answer; which `plate-dock-wipe` answer supersedes which), R26-238 (`CHART_TO_WHEN["remake"]` trimmed to the 260 ceiling; the strict xfail at `test_lint_species_choice.py:35` removed in the same commit), R26-240 (the effects layer built `rank_by_field=True`; the strict xfail at `test_effects_catalog_drift.py:551` removed; `test_docs_find.py` re-run for pinned orders), R26-145 (the fixture that leaks the event loop named and closed), R26-162 (`test_the_committed_tree_passes_check` ensures into a scratch copy of the tree), R26-141 (`effects_catalog_check.py` loads `configs/effect_card.schema.json` and refuses a card the schema refuses, naming the field and the cap)
- Write set: `content/video_engine/tests/test_lab_log.py`, `content/video_engine/scripts/build_scene_timeline_f.py` (`CHART_TO_WHEN["remake"]`'s text only), `content/video_engine/tests/test_lint_species_choice.py`, `content/video_engine/scripts/docs_find.py` (the effects Layer's flag), `content/video_engine/tests/test_effects_catalog_drift.py`, `content/video_engine/tests/test_docs_find.py` (only a pin the flag moves, with the reason), the browser fixture that leaks (`tests/conftest.py` or `test_effects_gallery.py`, step (0) names it), `content/video_engine/tests/test_build_docs_layers.py`, `content/video_engine/scripts/effects_catalog_check.py`, a NEW `content/video_engine/tests/test_effects_catalog_schema.py`
- Acceptance: (1) `test_lab_log.py` passes with the s84 answer in the live set, and the supersession pin names the operator's latest `plate-dock-wipe` answer; (2) the two strict xfails are gone and their tests pass; (3) `test_chart_transitions.py` and `test_effects_gallery.py` pass in ONE pytest process; (4) the committed-tree test passes while another lane's working-tree edit sits in the checkout (a planted dirty card in a temp copy proves it); (5) a card with a `does` over 240 chars fails `effects_catalog_check.py` by name; (6) the regenerated `SPECIES-BY-SENTENCE.md` s4 is the parent's (generated).
- Stop conditions: the remake `when` cannot be cut to 260 without losing its rule (report; the parent moves the ceiling deliberately in the test and the row); a pinned docs_find order is a ruling's (report).
- Regression: `python -m pytest -q content/video_engine/tests/test_lab_log.py`
- Expected RED (probed on lane A, 2026-09-25): `FAILED ...::test_the_operators_six_answers_derive_to_six_live_judgements_that_validate`, `FAILED ...::test_a_later_answer_supersedes_the_earlier_and_the_earlier_is_kept`, `2 failed, 15 passed`.
- Validate: `python -m pytest -q content/video_engine/tests/test_lab_log.py content/video_engine/tests/test_lint_species_choice.py content/video_engine/tests/test_effects_catalog_drift.py content/video_engine/tests/test_docs_find.py content/video_engine/tests/test_build_docs_layers.py content/video_engine/tests/test_effects_catalog_schema.py` then `python -m pytest -q content/video_engine/tests/test_chart_transitions.py content/video_engine/tests/test_effects_gallery.py` then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T3: The recipes carry the rulings - the four denied leave the proven set, the two approved carry their notes, the melt stack and the note's `keep` are carded, the lab lands a stamp on a stamp's clock
- Status: done - lane B 80fa2f5: 11 proven / 4 denied (E99 s84, verbatim), the kit never offers a denied recipe, the catalogue prints the reason; M38 on the approved Japan cut 0.76 -> 0.48 (interim WARN), on P72-HG1 item 8
- Owner: implementation_luna (LANE B for the lab and the schema; the recipe JSON is the shared registry - the parent commits it with the catalogue)
- Depends on: T0
- Items: R26-237 (E99 s84), R26-196 (its two approved-recipe notes), R26-116, R26-219 (the card half only - the row's other open half, the bracket's label room at 16:9, is T43; the row is archived only when both land), R26-252
- Write set: `content/video_engine/configs/effect_recipe.schema.json` (a `denied` status with `denied_reason` and `ruled_by`), `content/video_engine/effects/recipes/{card-becomes-the-chart,dock-lands-page-renames,plate-dock-wipe,spotlight-held-past-the-cut}.json` (status denied, the operator's words verbatim from s84), `content/video_engine/effects/recipes/{badge-ladder,read-park-build-write}.json` (the use notes: "even pill counts preferred"; the retitle's edge), a NEW `content/video_engine/effects/recipes/melt-then-rewrite.json` (status `candidate` unless an approved cut carries it - step (0) searches), `content/video_engine/effects/cards/page_species.json` (`page_species:note` options gain `keep`), `content/video_engine/scripts/lab_build.py` (`ARRIVAL_LANDS_S` `:168` and `ARRIVAL_MASS` `:210` read from `authoring.audio` - `arrival_mass`, `landing_contact`), `content/video_engine/scripts/effects_catalog_check.py` (a denied recipe is never counted proven), NEW `content/video_engine/tests/test_recipes_carry_the_rulings.py`, `content/video_engine/tests/test_lab_build.py` (a stamp candidate lands at `STAMP_CONTACT_S` with `ink`)
- Acceptance: (1) the four recipes read `denied` with the reason and `ruled_by: "E99 s84"`; `effects_catalog_check.py` prints 11 proven, not 15, and 0 failures; the catalogue marks them DENIED (regenerated by the parent); (2) the M38 / M45 readers take the new set (a test); (3) a stamp candidate built by the lab lands on the stamp's contact with ink mass; (4) `page_species:note` lists `keep`; (5) `melt-then-rewrite` validates against the schema.
- Stop conditions: a denied recipe is a member of an approved cut's recipe (report - the cut is frozen, E45); the schema change breaks the catalogue generator (report).
- Regression: `python -m pytest -q content/video_engine/tests/test_recipes_carry_the_rulings.py`
- Expected RED: the new test's four assertions fail - each file reads `"status": "proven"` (checked on lane A, 2026-09-25) and the schema's enum is `proven|candidate` (`effect_recipe.schema.json:254-257`).
- Validate: `python -m pytest -q content/video_engine/tests/test_recipes_carry_the_rulings.py content/video_engine/tests/test_lab_build.py content/video_engine/tests/test_lab_log.py content/video_engine/tests/test_gate_one_shot_floor.py` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T4: The builder's checklist and the record - the editing rules s74-s79 where the builder reads them, the stopped compiler marked, the rows' remaining notes written
- Status: done - lane A 526096a: ONE-SHOT.md's builder's checklist (s70/s74-s80, R26-347, R26-174, R26-214 (a)), the shape compiler STOPPED (s77), CRITIC-REPORT mechanisms 12-19, the calendar's REWRITE-ORDER-B (gap: no ruling gives the new ending's words)
- Owner: parent (doctrine); junior_developer for the mechanical edits (LANE A)
- Depends on: T0; T1 (both edit `CAPABILITIES.md` with line anchors - T4 re-reads its rows by title after T1 lands)
- Items: R26-195 (s74 / s75 / s76 into `ONE-SHOT.md`'s checklist and the critic's table; CAPABILITIES' compiler row STOPPED), R26-200 (s79 Apply 5: idle tokens counted, the camera on named things, the axes open), R26-202 (c) (the slot rule yields to the room rule when the room is gone; (a) is T7, (b) is T19), R26-214 (a) (a host plate enters the library only when approved, with its layer sidecar; the quarantine rule unchanged; (c) is D4's `⏸️` row), R26-174 (one host rendering per cut), R26-193 (the calendar script's REWRITE ORDER, next letter - an order, never a patch), R26-124 (both race paths selectable; the current default written on the race row), P65's CAPABILITIES row `:96` (HG1 withdrawn, s84)
- Write set: `docs/runbooks/ONE-SHOT.md`, `content/video_engine/projects/systems-and-blowups/steel-and-paper/CRITIC-REPORT-H.md`'s table template (or the critic template the runbook names - step (0) finds it), `docs/content-video-engine/CAPABILITIES.md` (rows `:95`, `:96`, the race row), `content/video_engine/sources/PLATE-LIBRARY` doc or the plate-intake runbook the row names (R26-214 (a)), `content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/REWRITE-ORDER-<next letter>.md`
- Acceptance: (1) `docs_find.py "fewer cuts"`, `"fold a short plate"`, `"a light only"`, `"idle tokens"`, `"one host"` each hit `ONE-SHOT.md`'s checklist; (2) CAPABILITIES `:95` reads STOPPED (E99 s77) and `:96` no longer names an open HG1; (3) every edit cites its ruling; (4) no ruling text is changed.
- Stop conditions: a line would restate a ruling differently from its words (quote it instead); the calendar rewrite needs the operator's words beyond the ones recorded (write the order with what is recorded, list the gap).
- Regression: `python content/video_engine/scripts/docs_find.py "fewer cuts"`
- Expected RED: no hit in `docs/runbooks/ONE-SHOT.md` - lane A's file, the one T4 edits: `grep -c "fewer cuts" docs/runbooks/ONE-SHOT.md` prints `0` in fable-p68 at `bf539e3` (probed 2026-09-25, revision 1).
- Validate: `python content/video_engine/scripts/docs_find.py "fewer cuts"` then `python content/video_engine/scripts/docs_find.py "one host"` then `python content/video_engine/scripts/build_capabilities_index.py --check` then `python content/video_engine/scripts/build_docs_layers.py --check`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T6: The value gate reads every page - M26 finds the scale on a long-form bars page, reads a range as two ends, never counts a card's own badge as page ink, and reads a width
- Status: done - lane B 9dc5bb6 (three review rounds, MERGE): every page read (declared rules, panels), an unreadable page FAILs by name, the hand-over excused only by its arriving state at rest, the veil only when it covers, ranges at both ends, `gauge:h` by width; H INFO -> PASS 46 values; 0 flips
- Owner: implementation_luna (LANE B), then reviewer (a truth gate)
- Depends on: the operator's approval of this plan only - not T0 (P70 T3 landed at `e43c3d8`). Wave 1, the first lane-B dispatch.
- Step 1 (after CONFIRM-OPEN, before RED) - the flip list: at the slice's base, run M26 over every committed build dir that carries a probe file (step 1 lists them: `build-*` / `build*` dirs under `content/video_engine/projects/` with a probe JSON), with a read-only "cannot read" detector that records each page M26 skips today, without changing any verdict. Write `$SP/p72-t6/flips.txt`: one line per build, page and reason ("no scale", "a range", "a width"). These are the reports that turn FAIL when acceptance (2) lands. Stop condition for step 1: if the run passes 30 minutes of wall clock, or a flip lands on an approved (frozen) cut, stop and hand the partial list to the parent before GREEN. Approved cuts are never re-gated or re-rendered (E45); their flips are recorded as findings.
- Items: R26-318 (HIGHEST: "a truth gate that silently cannot read is a false PASS"; H row 12's bars page is one), R26-303, R26-264, R26-319 (the width reader, then `form=gauge:h` admitted)
- Write set: `content/video_engine/scripts/probe.py` (the value read `:378`-`:398`: a scale source that does not need a visible gridline - the page's own data-to-pixel map the engine already computes, exposed on the probe, or the axis ticks; a range parser; a dock's own child boxes excluded from the ink under it `:226`-`:233`, `:700`-`:709`), `content/video_engine/scripts/gate_motion_density.py` (`_value_faults` `:2679` only: widths; the "cannot read" case becomes a FAIL, not a silent pass), `content/video_engine/scripts/ledger_page.py` (`gauge:h`'s refusal lifted in `form_error`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the gauge branch's horizontal form, `:10782`-`:10972`, and a probe hook for the scale, only if the scale is not already exposed), tests: NEW `content/video_engine/tests/test_value_gate_longform.py`
- Acceptance: (1) on a long-form bars page (H row 12's) M26 reads every bar's value against the page's scale and PASSes a true page, FAILs a planted wrong height; (2) a page M26 cannot read FAILs by name ("no scale on <page>"), never PASSes; (3) "+55-60%" reads as a range and a range bar is judged at both ends; (4) a badged card over a page is not M25 / M27 ink; (5) `gauge:h` compiles, draws its fill as a width, and M26 judges it; (6) every committed page M26 read before still reads the same (the goldens' probes unchanged); the committed H door compiles identically; (7) every committed build whose M26 report flips to FAIL is listed by name - build dir, page, reason - from step 1's `flips.txt`, re-run at GREEN to confirm the list is exact (no flip missing, none extra); each flip on a frozen cut is filed as a finding row, never fixed in the cut.
- Stop conditions: step 1's (above); the scale can only come from pixels (report - the gate never fits a threshold to our own frames, E38); a committed cut goes RED on a real untruth (report it as a finding row, do not relax).
- Regression: `python -m pytest -q content/video_engine/tests/test_value_gate_longform.py`
- Expected RED: the long-form page reads "no scale" and the current `_value_faults` returns no fault for it (the silent pass); the range test reads 5560; `form=gauge:h` is refused by name (P70 T3).
- Validate: `python -m pytest -q content/video_engine/tests/test_value_gate_longform.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_fill_gauge.py` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` then COMMON-TAIL
- Frame acceptance: the parent reads the probe's contact sheet at H row 12's bars page and at the `gauge:h` golden, beside the gauge-94 golden.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T7: The motion gate credits what moves - the verdict stack's beats, a record's typing, and a window's own claim; the cuts counted with the transform each refused
- Status: done - lane B `9fe66e9` + `e16e393` (T7) and `8c699a6` (T7b: R26-342 M21 reads a park / un-park; R26-345 the life count names a `life` species); rings and cards restart nothing (E50 s1 / s2); no FAIL level moves on any build
- Owner: implementation_luna (LANE B), then reviewer (a motion gate)
- Depends on: P70 T8 (`_landings`, `_arrivals`); P71 T7 (`squint=`, landed `a469501` - the `run` change is unioned on top of it); acceptance (7) only after P71 T15 merges (it owns `_over_build_faults`) - that item is its own commit
- Items: R26-326 (the stack's flights, recede and burst as events; a live host anchors the captions), R26-269 (a record's character clock counts on any plate), R26-167 (a `--beat` window mode that scores the window's own claim), R26-189 (an INFO row: every cut and dip, the transform it refused - s74), R26-132 (2) (a dock at a depth overshoots the move that aimed at it: an in-frame row for a settled depth card at every landing, M24's sibling in `_in_frame_faults`), R26-202 (a) (M27 judges a card at rest: a flight's frames are its path, listed as INFO, never a FAIL); R26-342 (M21 counts only build marks: a page that returns drawn, parks, un-parks and is rung reads as deployed) and R26-345 (`T.life_tokens` misses a declared `life` species) - added 2026-09-25
- Write set: `content/video_engine/scripts/gate_motion_density.py` (a NEW verdict-stack event read, the record-typing credit in the events builder, a NEW INFO row, `main` / `run`'s window arguments, the depth card's row in `_in_frame_faults`, and - after P71 T15 - the flight clause in `_over_build_faults`), tests: NEW `content/video_engine/tests/test_motion_gate_credits.py`
- Acceptance: (1) H row 23 authored with `VERDICT_STACK_ON = True` (a private build) no longer FAILs M01 / M05 / M08 for want of events, and the one-slot version's verdict is unchanged; (2) `world-internal-memo-v1`'s typing earns M05 / M16 events without the steam; (3) a test-bed beat scored with `--beat t0,t1` is judged on its own window for M11; (4) the INFO row lists every cut / dip and prints `refused: <transform>` or `refused: (unnamed)`; (5) ep1's `build-f` report is byte-identical except the new INFO row; no FAIL level moves on the approved cuts; (6) R26-132 (2): the `dock-depth` golden's settled card at k 1.15, run off the right and bottom edges, is named by the gate's in-frame row with its overshoot in px; a settled flat card that is in frame reads as before. The row's second question (whether a `focus_zoom` aimed at a depth card should aim at its projected box) is written as a finding with the golden's numbers, not built; (7) R26-202 (a): Tokyo v3b's 0.46 s throw flight at 9.09 s (2,432 px over the line) is an INFO line naming the flight, not an M27 FAIL; a card that SETTLES over the line still FAILs M27 (a test for each).
- Stop conditions: crediting the stack needs `_arrivals`' body (P70 T8's) - stop and sequence; a credited event turns an approved cut's WARN into a PASS the reference does not support (report, E38); (7) needs `_over_build_faults` before P71 T15 has merged (stop; the parent sequences).
- Regression: `python -m pytest -q content/video_engine/tests/test_motion_gate_credits.py`
- Expected RED: the stack build FAILs M01 / M05 / M08 (as row 23 did, R26-326); the memo plate's typing earns 0 events; `--beat` is an unknown argument; the `dock-depth` card's overshoot produces no fault (M25 reads flat boxes, `hist:576`); v3b's flight FAILs M27.
- Validate: `python -m pytest -q content/video_engine/tests/test_motion_gate_credits.py content/video_engine/tests/test_gate_motion_density.py` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T8: The long form's gates - a landscape safe box, a long-form reference, M46 honest over 3:00, the opening gate on its own take, the brand line in the long shape
- Status: done - lane B 02e9b83: the landscape safe box off YouTube's measured controls band (120 px), --reference required over 3:00, M46 INFO, the take overlap 0.95 (measured), S07 in both shapes
- Owner: implementation_luna (LANE B)
- Depends on: T0; before P68-HG4 is served
- Items: R26-206, R26-207, R26-208, R26-203, R26-212
- Write set: `content/video_engine/scripts/gate_vertical_safe_box.py` (a 16:9 mode in the same tool: every dock and the anchored caption clear the bottom 120 px and the 145 px rails), `content/video_engine/scripts/gate_one_shot_floor.py` (`--reference` required over 3:00; M37 / M39 / M40 print "reference is a SHORT" until a long form is approved; M46 INFO over 3:00 with its reason), `content/video_engine/scripts/gate_opening_structure.py` (a take whose words do not match the script is refused with the take's path and the overlap; `timing` names the take; S07 runs in the long shape), tests: `test_gate_vertical_safe_box.py`, `test_gate_one_shot_floor.py`, `test_gate_opening_structure.py`
- Acceptance: (1) the 16:9 mode runs on `build-h` and names every dock over the bottom band; (2) the floor on `build-h` without `--reference` exits 2 naming the flag; with it, M37 / M39 / M40 carry the SHORT caveat and M46 reads INFO; (3) G's take under H's script is refused (a test), H's own take passes; (4) S07 FAILs a long script that speaks the brand line; (5) the shorts' verdicts are unchanged.
- Stop conditions: the landscape band numbers have no source (the CSS comment at template `:484` is the only record - cite it and measure the player's controls on a frame; never invent).
- Regression: `python -m pytest -q content/video_engine/tests/test_gate_opening_structure.py -k "take"`
- Expected RED: the new mismatch test passes a G take under H (the position mapping, `gate_opening_structure.py:288-307`).
- Validate: `python -m pytest -q content/video_engine/tests/test_gate_vertical_safe_box.py content/video_engine/tests/test_gate_one_shot_floor.py content/video_engine/tests/test_gate_opening_structure.py` then `python content/video_engine/scripts/gate_vertical_safe_box.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h --aspect 16:9`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T9: The renders and the golden sources are deterministic - fonts settled before a capture, a repeat probe, idempotent LF sources
- Status: done - lane B ae5f6b8: `__fontsSettled` + `FontsUnsettled`, `--repeat`, LF idempotent sources with `STALE_SOURCES`, `tests/served_player.py` (39 files); no golden moved; R26-360 (the local font) filed to T27
- Owner: implementation_luna (LANE B)
- Depends on: T0
- Items: R26-140 (`render_baseline.py --repeat` reports drift by surface), R26-243 + R26-251 (one fix: the template sets `__fontsSettled` after its post-font rebuild and `prepare_page` waits on it, not a fixed 250 ms; the un-awaited `document.fonts.ready` at `:484` removed), R26-151 (the builder's non-deterministic input named and pinned), R26-323 (`write_surface` writes `newline="\n"`); R26-351 (the R26-145 Playwright leak in 38 more test files - a shared guarded opener; added 2026-09-25)
- Write set: `content/video_engine/scripts/render_baseline.py` (`prepare_page`, a NEW `--repeat`), `docs/content-video-engine/samples/scene-evidence-player.template.html` (the flag set after the font rebuild - a region P71 T15's `#dockveil` does not touch), `content/video_engine/scripts/build_golden_sources.py`, tests: NEW `content/video_engine/tests/test_render_determinism.py`, `content/video_engine/tests/test_golden_frames.py` (a second build of the sources is byte-identical)
- Acceptance: (1) a CPU-throttled capture of the `tiers` / `treemap` / `race-path-eased` pages matches the golden; (2) `--repeat 3` on the data-to-bars golden reports 0 differing bytes or names the surface and the cause; (3) building the golden sources twice is byte-identical and LF; (4) no golden moves.
- Stop conditions: the drift is GPU raster timing that no page signal can cure (report the probe's numbers; the goldens keep their fresh-page rule).
- Regression: `python -m pytest -q content/video_engine/tests/test_render_determinism.py`
- Expected RED: the throttled capture renders the title in the fallback face (R26-243's diff class); the second source build differs on `tiers-two` / `treemap-cross`; the sources land CRLF.
- Validate: `python -m pytest -q content/video_engine/tests/test_render_determinism.py content/video_engine/tests/test_page_boxes.py` then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T10: s130 (1) - filled marks glow: the gauge's fill and the primary bars carry an emissive halo in their own ink, measured off Bravos's fills, seek-exact
- Status: done - lane B `ee7d5fc` (round 3 after two review rounds): the emphasized bar, the gauge's fill and the stack's parts glow in their own ink (`LP_FILL_GLOW` 6 px @ 0.5 / 22 px @ 0.55), inside the Bravos fills band measured by `measure_line_bloom.py --fill`; a solo hands it over, a muted gauge sheds it, a breaking or extruded bar never takes it; 5 goldens re-pinned; at 256 px the glow barely reads (P72-HG1 item 1)
- Owner: implementation_luna (LANE B), then reviewer (a visual default on every bars page)
- Depends on: P70 T3 (landed); T6 (it edits the same gauge branch, `:10782`-`:10972`, which holds `lp-gauge-fill` at `:10805`; T10 rebases on T6's merge); T9 (the captures the measure runs on are settled); the `--3way` order against P71 T25 / T29 / T31 (the ownership table)
- Items: E99 s130 (1): "a fill gauge's fill and bars (the lit / primary ones) carry an emissive halo in their own ink, measured off Bravos's fills first (the `measure_line_bloom` band, E38), seek-exact like `lpHotFilter`, a solo / focus still widening the lit-vs-muted gap"
- Bravos reference: BOOM `scratch/jx3Ll_full.mp4` 10:55 and D40 `u70oUWgVoYU` 17:24 (`-ss 1044`) - the two fill gauges P70 T3 cites; plus one Bravos bars page with a lit bar found in step (0) from the harvest (`BRAVOS-VOCABULARY-HARVEST-v2.md`), each by BRAVOS-FRAME.
- Write set: `content/video_engine/scripts/measure_line_bloom.py` (a NEW `--fill` mode: the halo profile of a filled region's edge against the ground, the lit-vs-muted contrast at full size and at thumbnail width), `content/video_engine/assets/bravos-line-bloom.v1.json` (a `fills` entry, measured), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (a NEW `lpFillGlow` beside `lpHotFilter` `:11191`, pure in t; one call line in the gauge's fill group `:10805`; one at a PRIMARY bar's rect - the emphasized bar, or the solo'd one; `soloLevel`'s muted bars get none), a named dial group `LP_FILL_GLOW` (INNER / OUTER px and alpha, each `[MEASURED: <frame>]`), tests: NEW `content/video_engine/tests/test_fill_glow.py`, the goldens the glow moves (re-pinned by the parent at the wave merge with a sha table)
- Acceptance: (1) the band's `fills` entry reproduces within `BAND_TOL` (`--band --check`); (2) our gauge-94 golden and one H bars page, measured by the same tool, land inside the Bravos band at full size and at thumbnail width; (3) a cold seek and a played frame are byte-identical at the glow's instants (the `lpHotFilter` rule); (4) a muted bar under a solo carries no glow and the lit-vs-muted gap widens (measured); (5) the committed H door compiles identically and its changed instants are the bars pages only (listed, each read); (6) CAPABILITIES' bloom row gains the fills line; the card updated.
- Stop conditions: the Bravos fills carry no measurable halo at 1080 (report the numbers - s130 is ruled, so the parent brings the measurement to P72-HG1 rather than inventing a radius); the glow pushes an H label under its contrast floor (report).
- Regression: `python -m pytest -q content/video_engine/tests/test_fill_glow.py`
- Expected RED: the gauge's fill and the emphasized bar carry no filter (`lp-gauge-fill` is a plain clipped group, `:10805`); `measure_line_bloom.py --fill` is an unknown argument.
- Validate: `python content/video_engine/scripts/measure_line_bloom.py --band content/video_engine/assets/bravos-line-bloom.v1.json --check` then `python -m pytest -q content/video_engine/tests/test_fill_glow.py content/video_engine/tests/test_fill_gauge.py content/video_engine/tests/test_line_bloom.py` then COMMON-TAIL
- Frame acceptance: the parent reads, side by side at full size and at 256 px wide: BOOM 10:55, D40 17:24, our gauge-94 before / after, one H bars page before / after (`$SP/p72-t10/frames/`); the same sheet goes to P72-HG1 item (1).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T11: s130 (2) - a seal's gold adjusts by the measured ground under it
- Status: done - lane B 6c7ff17: the seal's gold latched at its contact from 64 samples of the ground as the world stood then (`groundLumsThen` / `worldXfAt`); one gold per seal, the darkest ground wins (never white or black; the spread reported); mid photo #544227 3.02:1; three review rounds; golden `seal-on-photo`; follow-ups R26-361 (T46)
- Owner: junior_developer (LANE B), then reviewer (the seal's contrast, s123 / s127)
- Depends on: P71 T12 (in flight on `species/chip.mjs`); the parent orders it against P71 T18
- Items: E99 s130 (2): "a SEAL's gold (rings, ring text, name, shockwave) adjusts by the MEASURED ground under it, as the bare-prop ring already does (P70 T1c `stampRingInk` / `ringInkUnder`), holding the seal's contrast floor on a photo plate"
- Write set: `content/video_engine/scripts/species/chip.mjs` (`sealGold` `:140`: its ground is the measured luminance under the seal, not the row's authored `ink`; `CHIP_SEAL.CONTRAST_MIN` 3.0 kept), the engine's chip region via `sync_kinetics.py --write`, the dock-stamp ring paint that calls it (one line), tests: `content/video_engine/tests/kinetics/chip.test.mjs`, a NEW golden `seal-on-photo` (a mid-tone photo plate)
- Acceptance: (1) a MEASURED check, not a question (s130 is ruled): on a mid-tone photo the seal's gold against the measured ground under it is >= 3.0:1 (today 1.55:1, the parent's finding), printed by the test with the ratio, and the same measure on the rendered frame of the `seal-on-photo` golden; (2) on the dark ledger ground the gold is `#E8B86D` unchanged, on cream `#A07F4B` unchanged (byte-identical goldens); (3) the shockwave takes the same resolved gold (s127 (2)); (4) the seal stays open over the chart (s128); (5) a bare prop's ring is untouched.
- Stop conditions: the measured ground under a seal varies across the seal's box beyond one ink's reach (report the spread; one gold per seal, the darkest ground wins - the parent confirms).
- Regression: `node --test content/video_engine/tests/kinetics/chip.test.mjs`
- Expected RED: a new test with a measured mid-tone ground (luma ~0.45) gets `#E8B86D` back (1.55:1) because `sealGold` reads `sp.ink`.
- Validate: `node --test content/video_engine/tests/kinetics/chip.test.mjs` then `node --test content/video_engine/tests/kinetics/stopaction.test.mjs` then COMMON-TAIL
- Frame acceptance: the parent reads the seal on a photo, on the ledger ground and on cream, before / after (`$SP/p72-t11/frames/`). The frames and the measured ratio are ATTACHED to P72-HG1 as a report, not asked.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T12: The panels page builds in view and holds at every preset
- Status: done - lane B 1bbaded: `lpPanelBuildAt` (and a panel's figure on the same clock), `lpPanelOcclude`, the long form's bars at phone, a panels page at phone WARNed (s106); page-boxes regenerated; the build at phone is R26-366 (T47)
- Owner: implementation_luna (LANE B)
- Depends on: T0 (D1, R26-316); P70 T4 landed (`d0dd19b`); R26-339's item after P70 T5 if P70 T5 is mid-flight on the stacked page (the parent orders them)
- Items: R26-315 (a hidden panel's build waits for its reveal: the bars grow in view over ~1.5 s, Bravos DOM 06:02-06:04), R26-316 (the panels layout per readability preset - `phone` holds the s90 floor with the line alone, or the long form is refused at `phone` by name, per D1), R26-299 (a panel's tick text writes whole or not at all), R26-339 (a one-bar stacked page on `longform:phone`: the T64 key sits over the bar's total and the category label 'Q1 2026' wraps, `$SP/p70-t5/frames/probe-lf-phone.png` - the same long-form-on-phone layout class as the panels finding)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`lpPanelStart`, the panel reveal clock, the panels layout's preset branch, the panel tick write, the stacked page's key place and category width on `longform:phone`), `content/video_engine/scripts/ledger_page.py` (the phone-preset check if D1 refuses it), tests: `content/video_engine/tests/test_companion_bars.py` (the strict xfail flips and is removed), a NEW `content/video_engine/tests/test_panels_page.py`, a NEW `content/video_engine/tests/test_longform_phone_layout.py`
- Acceptance: (1) the golden's hidden panel shows its bars at 0 % on its first visible frame and grows in view; (2) the panels page at `phone` holds 59.08 stage px labels or is refused by name; (3) no "%" without digits on any frame of the resize golden; (4) the H door's changed instants are row 21's panels only, each read; (5) R26-339: on `longform:phone` a one-bar stacked page's T64 key clears the bar's total (box overlap 0) and 'Q1 2026' sits on one line, with every text at or above the 59.08 px floor; `longform` (non-phone) pages render byte-identically.
- Stop conditions: the reveal clock is shared with a P70 slice still in flight (report); D1 would refuse the long form at `phone` while R26-339 shows `longform:phone` is the only preset that holds the brace's floor (61.4 px) - stop and bring both to the parent before building either branch.
- Regression: `python -m pytest -q content/video_engine/tests/test_companion_bars.py`
- Expected RED: the strict xfail pinned by P70 T4 (R26-315) is the RED - it XPASSes when fixed, so the GREEN commit removes the marker.
- Validate: `python -m pytest -q content/video_engine/tests/test_companion_bars.py content/video_engine/tests/test_panels_page.py content/video_engine/tests/test_longform_phone_layout.py` then COMMON-TAIL
- Frame acceptance: the resize golden at the reveal and at ~12.9 s, before / after; DOM 06:02-06:04 by BRAVOS-FRAME; the one-bar stacked page on `longform:phone`, before (`probe-lf-phone.png`) / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T13: A bars page writes its units and keeps its labels clear
- Status: done - lane B `6c349b0`: R26-274 (a word unit spaced; the tick column keeps 12 px), R26-287 (`unit_suffix` writes "$480B"), R26-250 (a rule label slides / wraps / shrinks, never over a bar; `st.ruleFit`), R26-217 (treemap floors per stage); R26-170 already fixed at 2b7b6a4 (M28 PASS); golden balance-level re-pinned
- Owner: implementation_luna (LANE B)
- Depends on: T0; lands before P71 T25 / T31 (they rebase) or after both
- Items: R26-274 (a word unit takes a space, a symbol unit none; the tick column never leaves the stage), R26-287 (a unit with a prefix AND a suffix - `$` + `B` - on the value, the ticks and the figure, in the page and the card profile), R26-250 (a rule label shrinks, wraps or takes a leader into free ground, never over a bar), R26-170 (a signed page's category labels sit above zero when the bars point down, E28), R26-217 (the treemap / tiers legibility constants resolved from the stage they render on)
- Write set: `content/video_engine/scripts/ledger_page.py` (the unit spec and its validation; `TREEMAP_VALUE_FONT` / `TREEMAP_PAD` `:2070`-`:2072` per stage), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the value / tick unit formatter, the tick column's left bound, the `hlines` label placement, the category-label side), `content/video_engine/scripts/chart_card.py` (the card profile's unit, only if it formats separately), tests: NEW `content/video_engine/tests/test_bars_units_and_labels.py`
- Acceptance: (1) `ev-two-clocks-bars-v1` writes "20 years" and every y tick sits inside the stage; (2) the capex v2 bars print "$480B" / "$690B" and the ticks read "$...B"; (3) the index-concentration page's "historically 2-4%" never overlaps the bar (M28 PASS); (4) the weak-prints page's labels and value tags never share a foot (M28 PASS); (5) a unit with no suffix renders byte-identically (every golden that carries no word unit and no suffix unchanged).
- Stop conditions: a unit form the script's words do not support (the figure is the script's - E77; report).
- Regression: `python -m pytest -q content/video_engine/tests/test_bars_units_and_labels.py`
- Expected RED: "20years", "$480" with no suffix, the rule label's box intersecting the bar, the labels at one foot (M28 12 pairs) - predicted from the rows; probed in step 1.
- Validate: `python -m pytest -q content/video_engine/tests/test_bars_units_and_labels.py content/video_engine/tests/test_ledger_page.py` then COMMON-TAIL
- Frame acceptance: the four pages before / after; H row 17's capex bars at its figure's instant.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T14: The captions read on every plate - a plate's caption room and its contrast backing, a quote on the word it opens, a caption that waits for a collapsing page
- Status: done - lane B 7c2258d: `caption_room`, the measured stage-caption backing (text shadow, never a box), `place_quotes`, the collapse window; 12 goldens re-pinned inside the caption box only; M48 on H 455 -> 454 (the rest is P71 T8b's quiet strip)
- Owner: implementation_luna (LANE B)
- Depends on: T0; HIGH - "the contrast backing is owed before HG4" (R26-268, recurred on row 17)
- Items: R26-268, R26-278, R26-292
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (a plate's caption room, as `;room=` places cards - a NEW `PLATE_OPTS` key, refused by name when malformed), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the caption layer: the room, a contrast backing measured against the plate under it, the hand-over wait at a `morph:prop` exit), `content/video_engine/scripts/build_caption_pages.py` (an opening quote rides the word after it, a closing one the word before), tests: NEW `content/video_engine/tests/test_plate_caption_room.py`, `content/video_engine/tests/test_build_caption_pages.py`
- Acceptance: (1) on the desk plate (rows 12, 17) the caption's unspoken words hold the caption contrast floor; (2) a declared room places the caption off the host's collar (row 7) and the viaduct's edge (row 13) - shown in a PRIVATE build (`$SP/p72-t14/build-rooms/`), never the committed door: the rows declaring their room are P69's retrofit, held for HG3 (T36); (3) `And "don't try to call the top"` shows `And "don't try` on screen; (4) the next row's caption does not paint over a page collapsing into a prop; (5) a plate with no room declared captions as today (byte-identical).
- Stop conditions: the backing reads as a new box the doctrine refuses (a caption box on the long form is ruled? - step (0) greps the rulings for the strip's form; report before building).
- Regression: `python -m pytest -q content/video_engine/tests/test_plate_caption_room.py`
- Expected RED: `;caption_room=` refused as unknown; the quote test reads `And" don't`.
- Validate: `python -m pytest -q content/video_engine/tests/test_plate_caption_room.py content/video_engine/tests/test_build_caption_pages.py` then COMMON-TAIL
- Frame acceptance: rows 7, 12, 13, 17 at their caption instants, before / after; row 15 at 237 s.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T15: page_boxes carries every text box, and the E65 room keeps them clear
- Status: done - lane B `400cf89`: R26-253 (`page_boxes` carries the basis label and each bar's name; the E65 room is cut round the page's words; the card itself was fixed by P71 T5's `3d6e8e5`), R26-270 (a bar name into the source or the caption band WARNs), R26-274's fixture half already done (d11e919 / 54bd650); R26-349, R26-357 moved to T46 unbuilt; the loose ends are R26-380
- Owner: implementation_luna (LANE B), then reviewer (placement; findings are WARNs, s106)
- Depends on: T13 (the same pages' labels); T40 (it edits `page_boxes` and the 9:16 band choice first - T15 rebases on it)
- Items: R26-253 (the basis label, source, title, sub and end tags stay out of the `empty` room), R26-270 (a wrapped bar name's box, measured against the source foot and the caption band), R26-274's fixture half (the four unmeasured pages - `ev-debt-issuance-line-v1`, `ev-index-concentration-bars-v1`, `ev-hbm-wafer-ratio-bars-v1`, `ev-two-clocks-bars-v1` - measured into `page-boxes.v1.json` by the parent); R26-349 (M25's ink list misses a schematic's phase names and tag - added 2026-09-25); R26-357 (H's page source line inside the controls band - added 2026-09-25)
- Write set: `content/video_engine/scripts/ledger_page.py` (`page_boxes`: the text boxes), `content/video_engine/scripts/build_scene_timeline_f.py` (the E65 `empty`-room placer reads them), `content/video_engine/scripts/measure_page_boxes.py` (`GOLDEN_PAGES` / `representative()` gain the four pages - the parent runs `--write`), tests: NEW `content/video_engine/tests/test_empty_room_keeps_text.py`, `content/video_engine/tests/test_page_boxes.py`
- Acceptance: (1) on the golden full-stage page a card placed in the `empty` room clears the basis label (T5's red frame, card at (167, 224), no longer covers it); (2) a wrapped two-line bar name clears the source foot and the caption band or WARNs with its numbers; (3) the four pages read MEASURED, not ESTIMATED; (4) placements that cleared before are unchanged.
- Stop conditions: a committed H row's authored place now reads as a WARN (the author's place stands, s106 - list it, never move it).
- Regression: `python -m pytest -q content/video_engine/tests/test_empty_room_keeps_text.py`
- Expected RED: the placer's `empty` room overlaps the basis label's box (the room reads the data mask only).
- Validate: `python -m pytest -q content/video_engine/tests/test_empty_room_keeps_text.py content/video_engine/tests/test_page_boxes.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the golden full-stage page with the card, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T17: The compiler says what it drops - spans, warnings, twins, WARNs by name
- Status: done - lane B 79c075f: all ten item groups in ONE commit (deviation: the compiler's hand-merge with T12 / T13 / T14 is verified as a whole; the body lists every group); R26-143's pair REFUSED (the probe showed a dropped state); R26-249 a WARN (s106); replay over 43 timelines + H clean
- Owner: implementation_luna (LANE B); one commit per item group, one compiler writer at a time
- Depends on: T0 (R26-44 is no longer here: it is the operator's, a `⏸️` row triggered by the first cut that threads a line)
- Items: R26-249 (every page's entry + build + leave checked against its row, authored or not), R26-317 (a door prints the page's E79 WARN from `ledger_page.measure_unit_warnings`), R26-154 (`MELT_T_S`, `MELT_M_S` twins beside `MELT_S` `:124`, pinned by `test_transitions_e47`), R26-43 (a tag wider than its chart WARNs by name instead of dropping its tip pill), R26-149 (`world.morph` takes a `series` word, refused by name out of range), R26-214 (b) (`;idle=figure` refused on a `plate_option:world` plate, `IDLE_KINDS` `:87`), R26-209 (an INFO line: the open zoom at every scene boundary; a key set that never returns to identity names the next row's carry or WARNs), R26-258 (`dock_place` pads a `dock_kind:prop` box by `PROP_SHADOW`'s reach toward the light's fall), R26-143's second half (`compare` authored beside a `remake` on one page - "neither refused nor proven", `hist:587`), R26-333 (a decade ruler whose 1.5 s scroll overlaps a `freeze` beat is neither refused nor warned; the check belongs in `_freeze_row_errors`, P69 T49's function - `hist:940`)
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`validate_page_build_spans` `:6776`, the page-warning print, the MELT constants, the tip-pill width check, `world.morph` validation, the plate idle check, a camera-boundary INFO, `dock_place`'s prop pad, `_freeze_row_errors`' ruler check, the `compare` + `remake` pair); `docs/content-video-engine/samples/scene-evidence-engine.mjs` only for R26-149's series pick; tests: NEW `content/video_engine/tests/test_compiler_says_what_it_drops.py`, `content/video_engine/tests/test_transitions_e47.py`, one NEW golden only if R26-143's pair is proven (below)
- Acceptance: (1) an unauthored page on a short row is checked (the 44 compiled timelines replayed: none refused, as the row measured); (2) the H door's build log prints each E79 WARN its pages carry; (3) the twins exist and the pin fails when one is edited alone; (4)-(6) each new refusal / WARN names the key and the numbers; (7) the H door and every committed timeline compile identically (`engine_sha256` aside) except the new INFO / WARN lines; (8) R26-143's second half: a page authoring `compare` beside `remake` is either PROVEN (it compiles, and a golden read by the parent shows both on one page with no overlap or dropped state) or REFUSED by name (`compare` + `remake` on one page), with a test for whichever the step-(0) probe supports - never left silent. The 6 px corner half stays below the reading size, as the row records; (9) R26-333: a ruler whose scroll window overlaps a `freeze` beat compiles with a WARN by name (the ruler's id, the freeze's span, the overlap in seconds). It is a WARN, not a refusal (s106: timing advises), and a ruler clear of every freeze prints nothing.
- Stop conditions: a refusal would break a committed timeline (make it a WARN and report, s106); the prop pad moves a committed prop (report - the author's place stands).
- Regression: `python -m pytest -q content/video_engine/tests/test_compiler_says_what_it_drops.py`
- Expected RED: each case compiles silently today (the rows' own measurements; `MELT_T_S` absent at `:124`; `IDLE_KINDS` admits `figure` on any plate; `compare` + `remake` on one page compiles with no refusal and no golden; a ruler overlapping a freeze prints no WARN).
- Validate: `python -m pytest -q content/video_engine/tests/test_compiler_says_what_it_drops.py content/video_engine/tests/test_transitions_e47.py` then `python content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py` (the build log read for the WARN lines) then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T18: Figures and rings on a bars page - a figure that double-prints its bar's value is WARNed by name, a ring can circle the value, a centred figure keeps its anchor, the pill yields
- Status: done - lane B `4b07424`: R26-284 / R26-256 (a figure on a built bar hands over in place; M28's double print FAIL -> PASS on a private row 17), R26-255 (the figure rides its bar through a rescale), R26-288 (`part: value` rings the printed value); H rows 15 / 21 WARN a figure that restates its bar's value (frames unchanged)
- Owner: implementation_luna (LANE B), then reviewer (E77 / E56: truth and the ring's one use)
- Depends on: T13
- Items: R26-284 (a figure that restates the bar's own value WARNs by name - a double-print is legibility (M28), not a truth rule, so under s106 it advises and never refuses - or the hand-over is a true in-place morph), R26-288 (a `value` target on a bar: the value label's box; after P69 T26a it reads the morphed top), R26-255 (`paintFigure` keeps a centred bar figure's anchor on a page with chart states), R26-256 (an emphasized bar's pill yields to its figure on the figure's clock)
- Write set: `content/video_engine/scripts/species/figure.mjs` (`paintFigure`'s anchor), `content/video_engine/scripts/species/compare.mjs` (only the offset that reads the anchor, `:266`), the ring target resolution for a bar in the engine, `content/video_engine/scripts/build_scene_timeline_f.py` (the figure-restates-value WARN; the ring `value` target's validation), `sync_kinetics.py --write`, tests: `content/video_engine/tests/kinetics/figure.test.mjs`, NEW `content/video_engine/tests/test_bars_figures_and_rings.py`
- Acceptance: (1) H row 17's 94 bars page prints "94%" once at every frame (M28 PASS at 5:32) through the in-place hand-over; a row that still restates its bar's value compiles with a WARN naming the row, the figure and the value, and is never refused (s106); (2) a ring on a bar's value circles the label, not the bar; (3) a bars page with a `chart_to` keeps a centred figure centred; (4) no H frame changes except row 17's hand-over (listed, read).
- Stop conditions: the WARN lands on a committed H row (list the row for P69 T36's hand-off; the author's row stands).
- Regression: `python -m pytest -q content/video_engine/tests/test_bars_figures_and_rings.py`
- Expected RED: the M28 pair `val:94% on bracket:94% at 5:32` (R26-284's crop), the ring's ellipse crossing "Capex, next two years".
- Validate: `node --test content/video_engine/tests/kinetics/figure.test.mjs` then `python -m pytest -q content/video_engine/tests/test_bars_figures_and_rings.py` then COMMON-TAIL
- Frame acceptance: row 17 at its hand-over, before / after; the ring golden.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T19: Docks keep their box, leave with the dip, ride a park; the hatch rides the dock's camera; a press card holds
- Status: done - lane B `89de388`: R26-328 (a re-docking at a new box is a new docking), R26-285 (a dip takes the docks ending on its boundary, and their wash, at the black; the snap never crosses a landing), R26-271 (the hatch rides the dock camera), R26-320 (a press card holds with `idle: hold`), R26-267 (`rel: {pin, inherit?}`), R26-202 (b) (`side: left|right|bottom` on a throw), R26-343 (a park scales the key rail); NOT built: R26-344 (re-measured as R26-404) and R26-348 (a re-pin by nature - its own sequence); both carried to T46; no golden moved; H changes at row 24's parked key rail and the dip into the outro only
- Owner: implementation_luna (LANE B), then reviewer
- Depends on: P70 T8, T9, T13 (landed `35a2130`); P71 T6, T15, T19, T23 (the dock branch of `render()`); T0 D2 (R26-105 / R26-267)
- Items: R26-328 (the painter's box per scene, not per asset id), R26-285 (a dip clears the outgoing docks as a wipe does; the 1.4 s snap never moves an exit across a landing), R26-271 (the hatch rides the dock camera's transform), R26-320 (`paintPress` takes the drift-hold's span hand-over and light band), R26-267 (`rel: pin` - a dock parented to another dock's pose, read and park; the relation layer's first verb, E97's grammar), R26-202 (b) (the throw's entry side is the engine's `flip++%2`, `scene-evidence-engine.mjs:6179`, and unauthorable: a row option `side=left|right|bottom`); R26-343 (a park does not scale the page's legend chips), R26-344 (a callout keeps its stage size on a parked page) and R26-348 (the placer's default card aspect vs the drawn aspect; a re-pin) - added 2026-09-25
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`render()`'s dock painter box, the dip's dock exit, the hatch, `paintPress`, the pinned pose, the throw's side read), `content/video_engine/scripts/build_scene_timeline_f.py` (`rel: {pin: <dock>}` on a dock, refused by name when the target is absent or later; the throw's `side=` option, refused by name outside `left|right|bottom`), `content/video_engine/scripts/species/press.mjs` if `paintPress` lives there, the throw's card (`side` added to its options), tests: NEW `content/video_engine/tests/test_docks_keep_their_box.py`
- Acceptance: (1) row 23's workaround (`dock-h-railway-share-ring`) is no longer needed - the same id docks at the new scene's box; (2) a dip takes the outgoing docks with it; row 17's docks may end on the boundary; (3) the hatch stays on the prop under a dock zoom / pan; (4) a held press card drifts and catches its band; (5) SELL stamps on the ticket on its own word and rides the ticket's read-then-park; (6) the H door compiles identically; its changed instants listed and read; (7) R26-202 (b): a card thrown with `side=right` to a right slot enters from the right edge (its first visible frame's box touches the right edge), `side=bottom` from the bottom; `side=top` is refused by name; a throw with no `side` keeps `flip++%2` and renders byte-identically (every committed throw unchanged).
- Stop conditions: any of the five needs a function a P70 / P71 slice has not landed (stop, the parent sequences).
- Regression: `python -m pytest -q content/video_engine/tests/test_docks_keep_their_box.py`
- Expected RED: the second dock of one id draws at the previous scene's box (R26-328); the dip leaves the docks standing until the snap; `rel` is an unknown dock key; `side=` is an unknown throw option.
- Validate: `python -m pytest -q content/video_engine/tests/test_docks_keep_their_box.py content/video_engine/tests/test_golden_frames.py` then COMMON-TAIL
- Frame acceptance: rows 17 and 23 at the named instants, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T20: The sound follows the frame - the suck's cue, the slot hand-off's cue on the frame that shows it, the bed swell on the arrival that lands
- Status: done - lane B `4e077e4`: the suck booked at its scene's start (R26-286), a handed-on card cued on the frame it is first seen (R26-329, 12 H cues moved, frames 12 of 12), `swell_holds` / `accent_level`; no gain moves in any committed door, the approved shorts' plans identical. The door's half (the suck cues; every accent at E81's start, R26-363) is HELD for the lane merge: lane A's kit lacks `e81_gain` / `suck_cues` (patch `scratchpad/p72-t20/door-merge/h-door-t20-e81.patch`, applies to lane A 300f322). R26-35 / R26-36 / R26-363's tuning wait on P72-HG1 item (10), the listened pass
- Owner: implementation_luna (LANE B)
- Depends on: P70 T8 (`authoring/audio`)
- Items: R26-286 (a cue for the suck from the existing library - the melt's / the throw's family - bound by the door's cue check), R26-329 (the slot hand-off's cue at the frame the card is first seen, E99 s116), R26-35 (the bed swell keyed to the arrival that lands - step (0): P69 T84 `e416df5` may already have moved it), R26-36 (one assertion: H's `:cut;then=` rows read as the author meant, the legacy suffix reading kept for the shipped plans, `authoring/audio.py:196-210`); R26-363 (the shared landing gain 0.12 = 4.3 dB under the voice: each landing cue measured and started at E81's reference, `audio.e81_gain`, then tuned by ear - added 2026-09-25)
- Write set: `content/video_engine/scripts/authoring/audio.py`, `content/video_engine/sound/` cue map (the suck), the slot hand-off clock if the fix is in the engine (one function), tests: `content/video_engine/tests/test_authoring_kit.py` (the cue binder's), `content/video_engine/tests/test_landing_sound_follows_the_landing.py` (P69 T84's), NEW `content/video_engine/tests/test_sound_follows_the_frame.py`
- Acceptance: (1) `SOUND-PLAN.json` for H names a cue at every suck; (2) row 23's hand-off cues land within one frame of the card's first visible frame, and row 23's 0.8 s lead can be removed (a P69 T36 hand-off item); (3) the bed swell sits on the camera arrival in Tokyo's recorded plan (checked, not re-rendered - the cut is frozen, E45); (4) the approved shorts' cue plans are byte-identical; (5) R26-36 stays OPEN in this slice until a listened pass, which is the evidence the row names (BACKLOG-DISCIPLINE: R26-35 / 36 "sound fixes wait for a new listened pass"; the row's "it moves a cue the operator has heard"): the one assertion that H's `:cut;then=` rows are read as cuts (`authoring/audio.py:196-210`, `LEGACY_SUFFIX_OPTS` kept for the shipped plans), and the cue plan's before / after for those rows, played on the test bed beside the take. The row archives only on the listened pass that names it - P68-HG4's whole-cut watch, with the cue diff attached.
- Stop conditions: fixing the hand-off moves an approved cut's cue (report - frozen cuts keep theirs).
- Regression: `python -m pytest -q content/video_engine/tests/test_sound_follows_the_frame.py`
- Expected RED: no suck cue in H's plan; the hand-off cue at +0.32 s against a card first seen at ~+0.9 s.
- Validate: `python -m pytest -q content/video_engine/tests/test_sound_follows_the_frame.py` then `python content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py` (the cue check in its log)
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T21: The named places the engine is not yet a pure function of t
- Status: done - lane B `7263013`: R26-260 + R26-21 (the snap from the placed box, about the page's origin), R26-294 (the slot's pivot reset), R26-321 (the melt's clone at `span[0]`), R26-322 (the hand ring after the outgoing paint), R26-324 (the title repainted whole), R26-376 (`dockCam` from the placed height); R26-325 DIAGNOSED - a will-change raster, not the engine (R26-397, T46); no melt golden moved; `dock-depth` x2 re-pinned (R26-398); H cold frames change only inside melt windows
- Owner: implementation_luna (LANE B), then reviewer (seek purity; goldens move)
- Depends on: P70 T8, T9; P71 T6, T15, T19 (`render()`); T9 (the determinism probe)
- Items: R26-260 + R26-21 (the snap's card box a pure function of t: forward play and a cold seek agree at 57.38 s and inside the 0.45 s window), R26-294 (the dock slot state pure: the leases record at 306.34 s on a jump seek), R26-321 (the melt clone taken from the page as painted at `span[0]`, not the live frame - moves every melt golden), R26-322 (`melt:morph`'s hand ring computed after `paint(wA, prev)`), R26-324 (the title glow repainted whole after a colour change - a forced re-layout or an isolated glow layer), R26-325 (row 12's fresh-vs-played diff DIAGNOSED first; its fix is a follow-up in this slice only if the cause is one of the above); R26-376 (the dock-depth card seeks 69 px higher than it plays: `dockCam` reads the live layout) - added 2026-09-25 from P72 T7
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the snap's box read, the slot state, `meltMount` / `paintMelt` / the melt call site and the hand ring in `render()`, the title glow's paint after a colour change), `content/video_engine/scripts/species/melt.mjs` (the synced source), tests: NEW `content/video_engine/tests/test_pure_in_t.py` (forward play vs cold seek at every named instant), the melt goldens (re-pinned once, sha table)
- Acceptance: (1) at each named instant a played frame and a cold seek are byte-identical (or, for the glow, within 0/255 on the glyph band); (2) R26-325's cause is written with its frame diff; (3) the H door's changed instants are the melt instants only (listed, read).
- Stop conditions: byte-purity for the melt needs a paint the budget cannot afford (report the numbers; the melt stays pure on the DOM, P71 T4's standard).
- Regression: `python -m pytest -q content/video_engine/tests/test_pure_in_t.py`
- Expected RED: the snap's (+137, +100) px offset in forward play; 1,143 px / 28,544 px melt diffs; the title glow's 6/255 band; row 12's 54,480 px.
- Validate: `python -m pytest -q content/video_engine/tests/test_pure_in_t.py content/video_engine/tests/test_melt_snapshot_is_current.py` then COMMON-TAIL
- Frame acceptance: each instant's played / cold pair and its diff (`$SP/p72-t21/frames/`).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T22: The verdict stack - its members may be pages and live cards, it freezes under a freeze, it scrubs clean, a portrait card fits the wall
- Status: done - lane B `42d0fab`: R26-327 (members by name - a docked document or a page shown before the wall; anything else refused), R26-169 (a tall member takes its own box), R26-304 (the life clock; the dock door refuses a freeze), R26-173 (hidden, not removed - scrub-safe both ways); a live member and the 9:16 overlap are R26-388; `VERDICT_STACK_ON` stays T36's
- Owner: implementation_luna (LANE B)
- Depends on: T7 (the gate counts the stack's beats)
- Items: R26-327, R26-304 (`verdict.mjs` reads the life clock; the dock door refuses an entry inside a freeze by name), R26-173 (the burst's cards removed on any seek past `clear_at + REMOVE_AFTER`), R26-169 (a portrait card's box on the wall)
- Write set: `content/video_engine/scripts/species/verdict.mjs`, the engine's verdict region via `sync_kinetics.py --write`, `content/video_engine/scripts/build_scene_timeline_f.py` (the member model; the freeze check on docks), tests: NEW `content/video_engine/tests/test_verdict_stack.py`
- Acceptance: (1) row 23's stack, authored as it was meant (`VERDICT_STACK_ON = True`, in a private build), gates clean under T7's credit and shows its members; (2) a stack under a freeze holds still; (3) a seek from 63.5 to 65.5-70.5 shows no ghost; (4) a portrait chart card on a 9:16 wall shows more than its header; (5) the flip of row 23 itself is P69's (T36 hand-off).
- Stop conditions: a page member needs the page rendered as a texture (report the cost; members stay docked assets and the row says so).
- Regression: `python -m pytest -q content/video_engine/tests/test_verdict_stack.py`
- Expected RED: a page member refused; the stack breathing under a freeze; the ghost cards on the probe sheet.
- Validate: `python -m pytest -q content/video_engine/tests/test_verdict_stack.py` then COMMON-TAIL
- Frame acceptance: row 23's private stack build at its beats; the one-shot #3 wall at 9:16.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T23: The melt's options - the off-screen throw, the blended inks, the hairlines that curl
- Status: done - lane B `151636d`: R26-157 (`melt:splash:...:offscreen`, E99 s56's spelling; 2766 px/s in the sidecar), R26-146 (`body=blend`, Kubelka-Munk), R26-139 (the gather curls the hairlines), R26-389 (the two-ink hand sweeps, no muddy dip); the last two ON with off dials by the operator's word (2026-09-26: land on, read at HG1) - 4 goldens re-pinned incl. E99 s51's approved gather; P72-HG1 item (12)
- Owner: implementation_luna (LANE B)
- Depends on: T21 (`meltMount`), T30 (R26-115's region order and R26-138's single vortex map)
- Items: R26-157 (the ball picked off the screen and thrown back faster, E99 s56), R26-146 (`body=blend`: the inks merge, E99 s49 - built, then the operator's eye at P72-HG1), R26-139 (the axes' lines sampled so they curl under `melt:gather`); R26-389 (the handed ball's ink goes muddy between two inks - a ball-ink rule in `melt.mjs`) - added 2026-09-25 from P72 T24
- Write set: `content/video_engine/scripts/species/melt.mjs`, the engine's melt region via `sync_kinetics.py --write`, `content/video_engine/scripts/build_scene_timeline_f.py` (the two option tokens, refused by name elsewhere), the melt card(s), tests: `content/video_engine/tests/kinetics/melt.test.mjs`, one golden per new option
- Acceptance: (1) each option is opt-in; every committed melt renders byte-identically; (2) the off-screen throw leaves frame and returns faster (the numbers in the golden's sidecar); (3) the blend's mixed ink is measured on its golden; (4) the gather curls the axes.
- Stop conditions: the blend needs a colour space the page does not use (report).
- Regression: `node --test content/video_engine/tests/kinetics/melt.test.mjs`
- Expected RED: `melt:throw:offscreen` and `body=blend` refused as unknown tokens.
- Validate: `node --test content/video_engine/tests/kinetics/melt.test.mjs` then COMMON-TAIL
- Frame acceptance: each golden before it is pinned; the blend clip to P72-HG1 item (3).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T24: The morph - the soak's floor in seconds, M17 honest on a planted source, `polyStrip` beyond x-monotone, the two untested goldens
- Status: done - lane B `0927f90`: R26-153 (the soak's floor 0.6 s), R26-163 (M17 judges det on a planted source, names a fold), R26-150 (`stripFor`: the x strip kept whenever it keeps the shape - a fold reported, never turned away, the parent's ruling for the tie's approved upright beat; a turn only for a filled bay), R26-148 / R26-152 goldens (`melt-morph-two-inks`, `morph-planted-plates`); their findings R26-389 (T23) / R26-390 (T46)
- Owner: implementation_luna (LANE B)
- Depends on: T7 (the gate file's other writer; T24 edits only M17's measure); T9 (`build_golden_sources.py`'s idempotence - T24 adds two sources to the same file)
- Items: R26-153 (a floor in seconds for the soak, or a refusal by name under it), R26-163 (M17's centroid / axis / area invariants off for `world.morph.poly` sources; the tall-thin strip inversion fixed), R26-150 (`polyStrip` handles a C-shaped bay, or refuses it by name), R26-148 (a morph golden across two series colours), R26-152 (a `field=plates` morph golden)
- Write set: the engine's morph region (`MORPH` `:15251` / `LPMORPH` `:14647`) and its source module, `content/video_engine/scripts/gate_motion_density.py` (M17's measure `:3875` only), `content/video_engine/scripts/build_golden_sources.py` (two sources - after T9's idempotence), tests: the morph tests on disk, NEW `content/video_engine/tests/test_morph_floor_and_strip.py`
- Acceptance: (1) a 0.3 s morph soaks for the floor or is refused by name; (2) M17 on the tie (the planted source) reports only the real invariant and `min det` > 0; (3) a horseshoe keeps its bay; (4) the two goldens are read and pinned.
- Stop conditions: the strip fix changes a committed morph's pixels (report; re-pin with a frame read).
- Regression: `python -m pytest -q content/video_engine/tests/test_morph_floor_and_strip.py`
- Expected RED: the soak at 0.15 s for a 0.3 s morph; M17's three unreachable invariants on the tie; `min det -0.182`.
- Validate: `python -m pytest -q content/video_engine/tests/test_morph_floor_and_strip.py content/video_engine/tests/test_gate_motion_density.py` then COMMON-TAIL
- Frame acceptance: the two new goldens and the tie beat.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T25: The plate's moves take a window
- Status: done - lane B `2b37127`: R26-165 (the ken's window `(scale, x, y, t0, t1)`, one ken clock for `paint` and `worldXfAt`, a freeze pauses the lean; every three-value ken unchanged), R26-164 (a layered plate's walk projected onto the camera's move, off with a WARN when the camera gives none; a flat plate keeps its free drift); golden `plate-alive` re-pinned; the clash check's window is R26-392 (T46)
- Owner: implementation_luna (LANE B)
- Depends on: P71 T32 (`kinetics/camera.mjs`'s `pedestal`) only if step (0) finds the ken window in `kinetics/camera.mjs`
- Not in this slice (revision 1, the review's finding 8): R26-283 and R26-281's engine half are DONE at `af869b7` (P69 T26a + T26b: "a camera push on a full-stage page keeps the title and axes in frame" - `camera_reach`, refused by name when its framing would cut the title, the y-tick column, the source line or a measured end tag; row 1's zoom 1.06 REPORTED as a WARN, reachable 1.02). T0 archives both engine halves; the row re-aims (row 1's push, row 15's pull) stay in T36, held for P69-HG3. Nothing here rebuilds `camera_reach`.
- Items: R26-165 (`ken_burns(scale, deg, t0, t1)` - a window so a lean starts on a word), R26-164 (a layered plate's drift follows the camera's direction or is off - the shorts' plates; long form is Ken Burns alone, s84)
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (the ken tuple's window, `:5428` / `:7474`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`paintPlanes`' drift, and the ken's windowed clock), tests: NEW `content/video_engine/tests/test_ken_window.py`
- Acceptance: (1) a ken with a window starts on its word (its first moving frame within one frame of `t0`) and holds still after `t1`; a ken with none is byte-identical (every committed plate unchanged); (2) a layered short plate's planes move one way - the drift's sign follows the camera's, or the drift is off, by name; (3) the long form's plates are Ken Burns alone (s84), unchanged.
- Stop conditions: a committed ken tuple changes meaning under the new arity (report; the old tuple reads as before).
- Regression: `python -m pytest -q content/video_engine/tests/test_ken_window.py`
- Expected RED: `ken_burns` with `t0, t1` refused as malformed (the tuple is `{scale, x, y}`); a layered plate's planes drift against the camera.
- Validate: `python -m pytest -q content/video_engine/tests/test_ken_window.py` then COMMON-TAIL
- Frame acceptance: a windowed ken at `t0` - 1 frame, `t0`, `t1`; one layered short plate's planes over the drift, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T26: A page's later states - their own scale, their own box, the axes that can leave, the named colour kept; a leaving bar keeps its label, an arriving state waits for its build, the recast's title rewrites whole
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer
- Depends on: P71 T3b, T13, T16, T28, T39 (`buildLedgerLine`, `lpAxisHandOver`); P70 T2 (landed `3600ec5`). R26-261's title item is the T3b follow-up: it lands after P71 T3b merges and reads T3b's leave order as its base
- Items: R26-266 (a per-state `domain` on `;then=`), R26-275 (the long-form layout takes the max over every state's y label, sub and tag room), R26-265 (a page token that recedes its axes and chrome so a record owns a clean ground without a world change), R26-277 (the long-form palette maps a named colour by a written table, or keeps it), R26-331 (the bar leave law in `lpPaintChart` fades `bb.lab` ahead of its bar: at H 663.4 bars 5-8 stand with no month under them - `hist:938`), R26-332 (a page's `build_to` caps paint a state whose build has not started: H 80.49's arriving GDP line stood at 66 % from the recast's first frame, hidden now by T3b's arriving-layer rule, the cause standing - `hist:939`), R26-261's title half (the row owes "the title rewrites whole"; P71 T3b's acceptance carries no title clause and P71 names R26-261 nowhere - `hist:703`)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`lpPaintStates`' per-state scale and box, the axes-recede token, the long-form palette table, `lpPaintChart`'s bar leave law and its `build_to` cap on an unstarted state, the recast's title write), `content/video_engine/scripts/build_scene_timeline_f.py` / `ledger_page.py` (the state `domain` key and the recede token, refused by name when malformed), tests: NEW `content/video_engine/tests/test_page_later_states.py`
- Acceptance: (1) row 10's divergence lines fill their plot on their own state's range; (2) a bars -> line state draws the line in its own box, its y label clear of "+613%"; (3) row 11's records sit on a receded ground; (4) `ev-tnx-two-eras-v4`'s crimson draws crimson or the table names the remap; (5) pages without the keys are byte-identical; (6) R26-331: a leaving bar's category label holds full opacity until its bar's own leave begins and goes with it - at H 663.4 every standing bar (5-8) shows its month; (7) R26-332: a state whose build has not started paints nothing - the frame before its build's first instant carries none of its marks, tested with the arriving-layer rule OFF so the cause is fixed, not hidden; (8) R26-261's title: at every instant of a recast the title reads as one whole string, either the old title or the new one, never a half-written mix like ": heir peak" (a frame test at the recast's middle, 80.9 s), and the middle frame shows no two scales' labels at once.
- Stop conditions: a per-state scale reopens R26-261's unreadable middle (report to P71 T3b's owner); (8) needs `lpAxisHandOver`'s body before P71 T3b merges (stop; sequence).
- Regression: `python -m pytest -q content/video_engine/tests/test_page_later_states.py`
- Expected RED: `;then=` with a `domain` refused past `STATE_MAX`; the state's line in the bars box; the crimson series painted orange; bars 5-8 unlabelled at 663.4; the arriving state's marks present before its build (layer rule off); the title half-written at 80.9 s.
- Validate: `python -m pytest -q content/video_engine/tests/test_page_later_states.py` then COMMON-TAIL
- Frame acceptance: rows 10, 11, 15 at the states, before / after; H 663.4 (the leaving bars), 80.49 and 80.9 (the recast's arriving state and its title), before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T27: The small engine rows - one commit each
- Status: done - lane B: R26-57 244f129, R26-142 83c3a98 (16:9; 9:16 = R26-369), R26-72 3a3924c (default = R26-370), R26-360 4b54f77, R26-9 TR-3 b5fb270, R26-302 fe65732 (engine; the H-row half stays T36's), R26-257 73625e2 (P72-HG1 item 2), R26-2 033d418, R26-123 2a6d887 (the blend's keyword box on the shorts' phrase caption only), R26-73 19f5546; R26-106 a finding and R26-171 its own row (R26-365, T46)
- Owner: junior_developer (LANE B), one row per commit; reviewer on R26-257 and R26-123 (a visible default)
- Depends on: each row's named neighbour (below); none waits on a P70 / P71 function except where named
- Items (each with its step (0) CONFIRM-OPEN):
  - R26-57 - `text-rendering: geometricPrecision` on the stage-space classes (`#species .lab`, `.chiplab`, `.flowtag`, `.vmstamp`, the chartbox tier; the template `:211` covers only `.lp text, .lp-chart text`);
  - R26-72 - the engine's `tierDomain` reads `shared_tier_domains` (E79's shared scale enforced);
  - R26-73 - the newsreel strip's 9:16 default follows E84 (measure first);
  - R26-142 - the agenda page's palette moves to the template's classes; the page form proven at 9:16;
  - R26-123 - the caption-life default is `blend` (E99 s6) when nothing is authored; approved cuts that author none keep their bytes only if they pin the setting - step (0) lists them, and a frozen cut is never re-rendered (E45);
  - R26-302 - the checklist takes a per-column `at` (after P69 T28b's `checklist.profile`, landed `b449e9f`);
  - R26-257 - the extruded prism's light re-derived from `DROP.LIGHT_DEG` (the parent's call recorded in the row); its goldens re-pinned with a frame read and the before / after to P72-HG1 item (2);
  - R26-2 - the harmonisation pass (light wrap + substrate grain) on a composited sprite, opt-in, one golden;
  - R26-171 - the compiler scales a badge rail on a 9:16 dock to the stage, never drops it (E99 s71 amendment in the row; the lab already does, `lab_build.py:1162`);
  - R26-106 - a DISCOVERY only: does any painter draw `prof.w`'s outline (`kinetics/stroke.mjs:58`)? If none, the finding is written and the build is filed as its own slice for the parent;
  - R26-9 TR-3 - "tag and test the unsourced numbers" (`hist:529`; TR-4 is done, `e96059d`, E46): the transition constants that carry no source tag at `a469501` - `SUCK_S` / `SUCK_TURN` (engine `:6407`), `DIP_S` / `BLURZOOM_*` (`:6428`), `SLIDE_S` (`:6444`), the dissolve's duration (0.8 vs the reference's 0.35-0.5) and `MOUNT_STEPS` (step (0) finds each by name) - each gets `[DERIVED: <source>]`, `[MEASURED: <frame or run>]` or `[UNSOURCED - <why kept>]`, and one test pins that every constant in the transitions region carries a tag. No value changes here: a value the tag shows is wrong is filed as its own row, measured off the reference first (E38).
  - R26-360 - the hand (Kalam, OFL) served from a local file by the template instead of Google Fonts, so a capture never waits on the network (T9's `__fontsSettled` stays as the check); the goldens byte-identical, or the parent reads each moved frame;
- Write set: the engine regions each row names, `docs/content-video-engine/samples/scene-evidence-player.template.html` (R26-57, R26-142 only), `content/video_engine/scripts/build_scene_timeline_f.py` (R26-123's default only), `content/video_engine/scripts/species/checklist.mjs` (R26-302), tests: one NEW test file per row (`test_small_engine_rows.py` with one test per row is acceptable)
- Acceptance: one line per row, one commit each, the H door identical except the listed instants (R26-57, R26-123, R26-257) -
  - R26-57: every stage-space text class named in the row computes `text-rendering: geometricPrecision` (read off the rendered DOM), and the `.lp text` / `.lp-chart text` classes are unchanged; frames of one chip label, one flow tag and one stamp before / after at 1x;
  - R26-72: a tiers page with `shared_tier_domains` draws every tier on the one shared domain (the tiers' pixel heights are proportional to their values across tiers); a page without it renders byte-identically;
  - R26-73: step (0)'s measurement of the 9:16 whole-reel default is written with its numbers; if it contradicts E84, the default follows E84 and one golden is re-pinned with a frame read; if it agrees, the row closes on the measurement;
  - R26-142: the agenda page's colours come from template classes (no hex literal left in its painter), the page renders byte-identically at 16:9, and one 9:16 golden is added; frames at 16:9 and 9:16;
  - R26-123: an unauthored row gets `blend` caption life (E99 s6); step (0)'s list of approved cuts that author none is written, and each keeps its bytes by pinning the setting or is named as not re-rendered (E45); the H door's caption band before / after at the listed instants;
  - R26-302: a checklist with a per-column `at` writes each column on its own instant; one without `at` is byte-identical (after `b449e9f`'s `checklist.profile`);
  - R26-257: the extruded prism's lit face and shadow follow `DROP.LIGHT_DEG` (the shadow falls away from the light by the angle, measured on the golden), its goldens re-pinned with the parent's frame read, and the before / after goes to P72-HG1 item (2);
  - R26-2: with the opt-in on, a composited sprite shows the light wrap at its edge and the substrate grain (measured: edge luminance lift and grain variance on the golden); with it off, byte-identical; frames on / off;
  - R26-171: a badge rail on a 9:16 dock scales to the stage and is never dropped (the compiler's timeline carries every badge, with its scale); 16:9 unchanged;
  - R26-106: the discovery is written (which painter, if any, draws `prof.w`'s outline, with the grep and a frame); if none does, the build is filed as its own row for the parent - nothing built here;
  - R26-9 TR-3: the tag test passes, every transition constant named above carries a tag, and the engine's bytes differ only in comments.
  - R26-360: no capture requests fonts.googleapis.com / fonts.gstatic.com (read off the page's network log); `test_render_determinism` 19 green; every golden byte-identical or re-pinned with the parent's frame read;
- Stop conditions: a row's fix touches a function a P70 / P71 slice owns (stop; sequence).
- Regression: `python -m pytest -q content/video_engine/tests/test_small_engine_rows.py`
- Expected RED: one failing test per row (each predicted from the inventory's evidence line); TR-3's tag test fails on `SUCK_S` (no tag at `:6407`).
- Validate: `python -m pytest -q content/video_engine/tests/test_small_engine_rows.py` then COMMON-TAIL
- Frame acceptance: R26-257's extruded-bar goldens and R26-123's caption band, before / after; R26-57's three labels at 1x; R26-142's agenda page at 16:9 and 9:16; R26-2's sprite on / off.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T28: Scripts that cost runs or say the wrong thing
- Status: done - lane B `c7f133c` (+ the mirror `33c6d9c`): R26-227, 215, 197 (the receipt half), 198 (b, c), 178, 130, 183, 136 (3), 188's mirror. HELD for the lane merge: the H door's shim removal (`scratchpad/p72-t28/door/h-door-shim.diff`); the Tokyo shim stays (a frozen cut's door). R26-330, R26-341, R26-352, R26-356, R26-358, R26-359 moved to T46 unbuilt
- Owner: implementation_luna (LANE B for the scripts; the H-door shim removal is a one-line lane-A edit after P69 T32)
- Depends on: T0; T7 (it edits `gate_motion_density.py`'s `main` - R26-198 (b)'s `--write` rebases on T7's window arguments); T20 (it edits `authoring/audio.py` - R26-198 (c)'s bind entry rebases on T20's cue binder); R26-197's H half after P69 T32 (lane A is writing `build_episode_h.py`). Wave 5.
- Items: R26-227 (`scratch_take.py` prints words / spoken seconds and the ask, exit 2 outside the band; the runner's report carries the measured wpm), R26-215 (`lint_species_choice.py --table` takes a bare name resolved in the project; the default follows the build), R26-197 (`recall_verify.resolve_ledger` accepts a build script's own docstring as the receipt's home; the shims in `tokyo-tea-break/build_short_v2.py` and `build_episode_h.py:3849-3851` removed), R26-198 (b) the gate CLI grows `--write`, (c) `--bind-cues` refuses a `--timeline` that is not the build's own), R26-178 (a whole-cut watch card carries its frozen player link with the audio, or the clip route takes `--audio`), R26-130 (a plate-library rebuild that loses a shipped record refuses by name; the sweep for uncovered approved plates), R26-183 (`self_watch.verdict_line` reads what `self_watch.py` writes - a round-trip test), R26-136 (3) (M13 enforced in `authoring/words.py` `cut_before` gets its registry row), R26-188's mirror (`sync_operator_memory.py --check` as a docs-layer step); R26-330 (the spiral out of a plate shows ~1 s of dark board, rows 20 and 23 - added 2026-09-25 from T0's coverage read) and R26-341 (a `spread` paints nothing on `ev-divergence-v1` under `readability=longform`); R26-352 (the ingester's entity-name scrub: a gitignored terms file from the operator's folder - added 2026-09-25 from T31); R26-356 (the cards' 92 by-line cites), R26-358 (the screens borrow a take), R26-359 (load_timings on a kokoro words file) - added 2026-09-25
- Write set: `content/video_engine/scripts/scratch_take.py`, `run_script_gates.py`, `lint_species_choice.py`, `recall_verify.py`, `gate_motion_density.py` (`main`'s `--write` only - after T7), `authoring/audio.py`'s bind entry (after T20), `review_queue_proofs.py` or `build_review_queue.py`, `build_plate_library.py`, `self_watch.py`, `build_gates_registry.py`, `build_docs_layers.py` (the mirror step), their tests; lane A: `tokyo-tea-break/build_short_v2.py` and `build_episode_h.py` (the shim lines only)
- Acceptance: one line per item; the two doors compile identically with the shim gone -
  - R26-227: `scratch_take.py` prints the words, the spoken seconds, the measured wpm and the ask, and exits 2 when the wpm is outside the band (a test with a planted slow take); the runner's report carries the measured wpm;
  - R26-215: `lint_species_choice.py --table <bare name>` resolves the name inside the project and lints the same table as the full path; with no `--table` it reads the build's own (a test for each);
  - R26-197: `recall_verify.resolve_ledger` accepts a build script's own docstring as the receipt's home (the regression below goes GREEN), and both shims are gone - `tokyo-tea-break/build_short_v2.py`'s and `build_episode_h.py:3849-3851`'s - with both doors compiling identically;
  - R26-198 (b): the gate CLI's `--write` writes the report file it names and prints its path; without the flag, nothing is written (a test in a temp dir);
  - R26-198 (c): `--bind-cues` given a `--timeline` that is not the build's own is refused by name (both paths printed); the build's own passes;
  - R26-178: a whole-cut watch card carries its frozen player link WITH the audio (the served page plays the take), or the clip route takes `--audio` and the card's clip has an audio stream (ffprobe);
  - R26-130: a plate-library rebuild that would drop a shipped plate's record is refused by name (the plate id); the sweep lists every approved plate with no library record (0, or each named);
  - R26-183: a round-trip test - what `self_watch.py` writes, `self_watch.verdict_line` reads back to the same verdict;
  - R26-136 (3): M13's enforcement in `authoring/words.py` `cut_before` has its row in the gates registry (`build_gates_registry.py` lists it), and the registry check passes;
  - R26-188's mirror: `build_docs_layers.py --check` runs `sync_operator_memory.py --check` as one of its steps and FAILs when the mirror is stale (a planted stale copy in a temp tree).
- Stop conditions: removing the H shim while lane A has `build_episode_h.py` open (wait).
- Regression: `python -m pytest -q content/video_engine/tests/test_recall_verify.py -k docstring`
- Expected RED: a build dir with no ledger and a docstring receipt is refused (the shim is what passes it today).
- Validate: `python -m pytest -q content/video_engine/tests/test_recall_verify.py content/video_engine/tests/test_lint_species_choice.py content/video_engine/tests/test_self_watch.py content/video_engine/tests/test_plate_library_layers.py content/video_engine/tests/test_landing_sound_follows_the_landing.py content/video_engine/tests/test_scratch_take.py content/video_engine/tests/test_build_plate_library.py` (the last two NEW in this slice) then `python content/video_engine/scripts/build_docs_layers.py --check`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T29: Citations resolve by row title, not by line
- Status: done - lane B 47d87a0: title cites in the skeleton vocabulary / kit / deriver, the catalogue 587 of 645 cites (was 479)
- Owner: implementation_luna (LANE B)
- Depends on: T1 (the index the resolver reads)
- Items: R26-242, R26-301
- Write set: `content/video_engine/configs/shape_skeleton.schema.json`, `content/video_engine/scripts/authoring/shapes.py` (messages), `content/video_engine/scripts/derive_approved_mix.py`, `content/video_engine/effects/skeletons/approved-mix.json`, `content/video_engine/tests/test_shape_skeletons.py`, `content/video_engine/tests/test_authoring_shapes.py`; the resolver reuses `build_effects_catalog.py:73-84`'s DOCS-INDEX lookup
- Acceptance: (1) every cite names a row by its title span and resolves through the index; (2) inserting a row above every cited row leaves every test green (a test inserts one in a temp copy); (3) the four silent false passes of R26-242 are gone.
- Stop conditions: a cited row has no stable title (report; the row gets a title in T4).
- Regression: `python -m pytest -q content/video_engine/tests/test_shape_skeletons.py`
- Expected RED: the new insert-a-row test fails (19 `CAPABILITIES.md:<line>` cites in the schema at e43c3d8).
- Validate: `python -m pytest -q content/video_engine/tests/test_shape_skeletons.py content/video_engine/tests/test_authoring_shapes.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T30: Files under the line cap, one fold, the region order
- Status: pending
- Owner: implementation_luna (LANE B); a refactor - behaviour byte-identical, the tests as the net
- Depends on: T2, T3 (`lab_build.py`'s tables), T9
- Items: R26-160 (`build_animation_registry.py` 932 lines: `FileScan` + `word_tokens` to a sibling), R26-166 (`comfy_depth_split.py` 944: `--process` / `--fill-holes` to `depth_split_clean.py`), R26-182 (`lab_build.py` 2,613: `lab_splice.py`, `lab_gates.py`, `lab_build.py`), R26-161 (`docs_layers.ensure_or_warn()` folded into the five readers), R26-115 (`sync_kinetics` orders the regions by the import graph), then R26-138 (the vortex map written once)
- Write set: the named files and their NEW siblings, `content/video_engine/scripts/sync_kinetics.py`, `content/video_engine/scripts/species/melt.mjs` (R26-138's import only), their tests
- Acceptance: each file under 800 lines; every existing test passes unchanged; the generated engine is byte-identical after R26-115 (the order the graph gives equals today's, or the diff is the regions' order only and every golden holds); `meltGatherAt` imports `lpVortex`'s terms.
- Stop conditions: the split changes an import other lanes use (report).
- Regression: `python content/video_engine/scripts/sync_kinetics.py --check`
- Expected RED: a NEW test that a region importing a later one is ORDERED, not refused, fails (the hand-kept rule, `sync_kinetics.py:19`).
- Validate: `python -m pytest -q content/video_engine/tests/test_kinetics_sync.py content/video_engine/tests/test_lab_build.py content/video_engine/tests/test_build_animation_registry.py` then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T31: The research tooling
- Status: done - lane B 8f8106b (the ingester's scrub, the profiles' tier-0 rule, the ledger's transport) + lane A 6e9ba30 (R26-144 follow_moved_packet); R26-336 re-checked at 78c884f; findings R26-352..355
- Owner: implementation_luna (the Claude research-tooling lane; LANE B scripts)
- Depends on: T0; T44 (R26-340's row: "fix before P72 T31"). R26-127 is not here: it is closed (`bf539e3`, the `bridge_inbox` hook self-starts the daemon), and T0 archives it. The bridge items (R26-144, R26-336) land in LANE A after T44, because R26-340 names lane A the bridge scripts' owner - one writer for `bridge_*.py`. R26-336's fix also closes R26-340 (6) (the missing Astra branch, and `bridge_reply.resolve` sending Astra orders through the Gemini send).
- Items: R26-254 (1) (`ingest_stock_research.py` strips Drive ids / URLs, refuses offering documents - term sheet, PPM, subscription - by name, and FAILS a docket whose body is a search listing), R26-128 (the research profile never runs our layer regen; a tier-0 rule), R26-129 (the research ledger does not count the bridge transport as a run), R26-144 (the daemon's paths-written check follows a packet to `replied/`), R26-336 (the bridge daemon calls the watcher with `--lane astra`, which accepts only `gemini|claude`, so it errors every 60 s and the three `lane: astra` packets in `docs/research/runs/bridge/sent/` - 20ae64c6dfa9, 6a3c72d239a2, e6e94125cdb2 - never land; `hist:943`). T37's Astra run over the bridge depends on R26-336.
- Write set: `content/video_engine/scripts/ingest_stock_research.py`, the research profile file the lane reads, the research-ledger builder, the bridge daemon and `bridge_watch` (R26-336's lane list), their tests
- Acceptance: one line per item -
  - R26-254 (1): a re-run of the ingester on a copy writes no Drive id or Drive URL, refuses the term sheet, a PPM and a subscription document by name, and FAILS a planted docket whose body is a search listing;
  - R26-128: the research profile carries the tier-0 rule "never run the layer regen", and a test reads the profile and finds it;
  - R26-129: the research ledger built over a run folder holding a bridge-transport packet counts it 0 runs (a test with one real run and one transport packet: count 1);
  - R26-144: the daemon's paths-written check follows a packet from `sent/` to `replied/` and reports its paths written (a test that moves a planted packet);
  - R26-336 (+ R26-340 (6)): the watcher accepts `--lane astra` (the Codex lane), or the daemon routes `lane: astra` packets to the lane that takes them - one tick over a copy of `sent/` with the three packets exits 0 with no error line, and each packet reaches its lane's inbox; a packet with an unknown lane is refused by name, once, not every 60 s; `bridge_reply.resolve` never sends a `lane: astra` order through the Gemini send (a test).
- Stop conditions: the ingester would read files outside the operator's named folder (never; it reads that folder only); R26-336's fix would send a live packet (the tick runs on a copy; a live send is the parent's).
- Regression: `python -m pytest -q content/video_engine/tests/test_ingest_stock_research.py` (NEW, written first in this slice)
- Expected RED: a planted docket with a Drive search listing is written, not failed.
- Validate: `python -m pytest -q content/video_engine/tests/test_ingest_stock_research.py content/video_engine/tests/test_build_research_ledger.py` then the bridge daemon's tests (step (0) names them)
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T32: The strobe's sharpness on real motion - a measurement
- Status: done - lane B 514b465: `measure_strobe_sharpness.py` + its `--check`; the finding (step rate, not sharpness) in R26-368 and the record `docs/research/runs/p72-t32/` (main checkout); no threshold set
- Owner: implementation_luna (a measurement, no threshold change)
- Depends on: T9
- Items: R26-85 ("keep 154 px/s as the cited cinema-parity reference; measure the remaining sharpness/space question on real motion before promoting a 250/300 threshold") - H now carries real motion in the 100-300 px/s band
- Write set: `docs/research/runs/p72-t32/` (gitignored: the report and the frames), a measurement script only if none exists (step (0) names the strobe tooling the E99 s30 verification used)
- Acceptance: the speeds and the sharpness measured on H's moving marks, beside the reference's; the finding written; any threshold change is a new row measured off the reference first (E38), never set here.
- Stop conditions: the measurement needs a reference not on disk (report).
- Regression: the measurement's own `--check` (step (0) names it)
- Expected RED: no measurement on disk for H's motion.
- Validate: `python content/video_engine/scripts/docs_find.py "strobe"` (the finding reaches the record) then the measurement's `--check`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T33: The railway research and the as-of date, under the claims gate
- Status: pending
- Owner: parent (the order and the promotion) + the Gemini research lane; explorer runs the verifier reads
- Depends on: T0
- Items: R26-311 (the reply to packet `cbf13c74...` re-verified with OUR verifier, `verify_research_claims.py <run dir> --require-pass`; the lane-saved CSVs capped at PLAUSIBLE unless OUR fetch matches; each claim tiered CONFIRMED / PLAUSIBLE / UNSOURCED-editorial / REJECTED; only what earns its tier is promoted into `docs/research/markets/` or an evidence object), R26-29 (the iShares fact-sheet quarter-end read in a browser and written to `ev-bonds-vs-chips-10y-v1`'s `src` / `fetched`)
- Write set: `docs/research/runs/<the reply's run>/` (gitignored: `claims.jsonl`, `VERIFY.json`, `VERIFY.md`), `docs/research/markets/r26-311-*-VERIFY-2026-09-*.md` (the verified record), an evidence object only for a promoted claim, `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/evidence/objects/ev-bonds-vs-chips-10y-v1.series.json` (the date only)
- Acceptance: (1) `verify_research_claims.py <run> --require-pass` exits 0 for the claims file as promoted; (2) every REJECTED claim is listed with its reason; (3) no figure is written that the verifier did not pass (never fabricated); (4) the object's `src` names the printed quarter-end.
- Stop conditions: the reply is missing or the verifier differs from HEAD (its own tamper check refuses - report); the lane edits the verifier (restore, report, as on 09-24).
- Regression: `python content/video_engine/scripts/verify_research_claims.py <run dir> --require-pass`
- Expected RED: exits non-zero (no `VERIFY.json` for the current claims file yet, or the capped claims read above their earned tier).
- Validate: `python content/video_engine/scripts/verify_research_claims.py <run dir> --require-pass` then `python -m pytest -q content/video_engine/tests/test_verify_research_claims.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T34: The six dockets re-ingested under the gate
- Status: pending
- Owner: parent + the research lane
- Depends on: T31 (the ingester fixed)
- Items: R26-254 (2): dockets 11, 17, 26, 28, 29, 32 re-ingested from their `.docx` in the operator's folder, the scrub kept, each claim that a script will use verified by the claims gate before use
- Write set: `docs/research/markets/sovereign-compute/` (the six dockets), the run folders (gitignored)
- Acceptance: the six carry their research body, no Drive id, no search listing, no offering document; `audit_research_provenance.py` clean on them.
- Stop conditions: a `.docx` is itself a listing or an offering document (skip it by name; report).
- Regression: the ingester's `--check` on the six (the T31 test harness)
- Expected RED: the six bodies are Drive search listings today (the row).
- Validate: `python content/video_engine/scripts/audit_research_provenance.py docs/research/markets/sovereign-compute` then `python -m pytest -q content/video_engine/tests/test_research_gate.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T35: The full-page melt's design sheet
- Status: pending
- Owner: implementation_luna (a private test bed; LANE B read-only)
- Depends on: T23
- Items: R26-147 ("design first, then the operator's word"; E99 s49: "melt everything ... the slate or black metal reference")
- Write set: `$SP/p72-t35/` (the sheet and its frames), a private test-bed door under `content/video_engine/projects/_proofs/p72-melt-all/` (a proof is a scene, s60)
- Acceptance: two or three candidate full-page melts rendered from one source on a real H beat, frames at the instants that matter, the costs named; nothing wired in the engine.
- Stop conditions: a candidate needs engine code (the sheet shows today's mechanisms composed; a new mechanism is named, not built).
- Regression: the proof door builds (`python content/video_engine/projects/_proofs/p72-melt-all/proof.py`)
- Expected RED: the door does not exist.
- Validate: `python content/video_engine/projects/_proofs/p72-melt-all/proof.py`
- Frame acceptance: the sheet goes to P72-HG1 item (4).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T36: The P69 hand-off - the H-row follow-ups the fixes make possible
- Status: pending
- Owner: parent (an edit to P69's T33 / T34 pass lists; the rows themselves are P69's)
- Depends on: the engine slice named per item
- Items: now (the engine half landed at `af869b7`, P69 T26b's `camera_reach`) - row 1's push re-aimed to the reachable 1.02 (R26-281) and row 15's pull (R26-283), both rows-1-13-class retrofits held for P69-HG3 (P69 T33); after T27 - row 20's `TEST_SWEEP_WHY` / `BODY_DEPARTURES` text (R26-302); after T22 - row 23's `VERDICT_STACK_ON = True`; after T20 - row 23's 0.8 s hand-off lead removed (R26-329); after T19 - row 23's second asset id retired (R26-328); after T28 - the H door's R26-197 shim removed (if not done in T28); after T14 - rows 7 / 12 / 13 / 17 declare their caption room; R26-347 (added 2026-09-25: H's 12 dips -> 10, each dip that is not a world change becomes the continuity transform it refused - build work, never an operator card; the operator's words are in the row); R26-346 (row 24's derived yardstick card: a lone '20' with no unit, '28%' at the card's edge - E28); R26-350 (the H door's words call the denied `card-becomes-the-chart` proven - added 2026-09-25); R26-364 (the capex page's `unit_suffix: "B"` and the two-clocks object back to "years", after P72 T13 - added 2026-09-25); R26-374 (H's COO window, row 11, needs its own life: M01 / M05 / M08 FAIL at 2:00 without the steam) - added 2026-09-25 from P72 T7
- Write set: `.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md` (T33 / T34's lists), `docs/content-video-engine/BACKLOG.md` (the P69 umbrella's children)
- Acceptance: each item is on P69's pass list with the P72 slice and sha that enabled it; none is built here (the body is held for P69-HG3).
- Stop conditions: none.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`
- Evidence: pending

### T37: The one-shot comparison - one-shot #3 as Fable authored it, then Opus's, then Astra's, on one loop, behind P54-HG3's two steps
- Status: pending
- Owner: parent (the brief, the read, the card), implementation_luna (Opus's), Astra via the bridge (Astra's). The parent is now Opus 5.5 (the 09-22 trial), not Fable, so "Fable's one-shot" means the EXISTING one-shot #3 (built and ruled, E99 s66 / s71), kept exactly as authored - never rebuilt.
- Depends on: P71 T37 (its last wave merged) and T38 (P72's waves merged) - P71's stated successor, "the next one-shot test, measured against the 09-16 baseline"; T31 (R26-336: Astra's packets must land over the bridge); T4 (R26-193's calendar REWRITE ORDER, if the Opus and Astra cuts use the calendar script's next letter - one-shot #3 then stands on its own letter and the card says so); P54-HG3 step A before Astra's dispatch
- Items: R26-175 (E99 s66's order), R26-135 (4) (the calibration run: an agent other than Claude one-shots from the record), P54 T7 (the Astra-vs-Fable bake-off)
- Step A (P54-HG3's first half, before Astra is dispatched): the parent writes the bake-off brief (`BAKEOFF-ASTRA-FABLE.md` - not on disk today; P54's HG3 names it) and serves it on `p54-hg3-astra-fable-bakeoff`. It flags the SCOPE CHANGE for the operator to confirm: three whole, labelled one-shots (one-shot #3 as authored, Opus's, Astra's) supersede P54 T7's "one beat ... unlabelled watch" (P54 `:185-195`). If the operator refuses, T37 runs P54 T7 as written (one beat, unlabelled) and the three-cut comparison is dropped.
- Step B (the second half, after the watch): the verdict card - the three cuts side by side.
- Write set: `BAKEOFF-ASTRA-FABLE.md` (beside P54's other artifacts - step (0) names the folder P54 uses); two private build dirs under one-shot #3's project (Opus's, Astra's), each with its receipt, its frozen copy, its critic; one-shot #3's committed build read-only; `docs/content-video-engine/review-queue.v1.json` (`p54-hg3-astra-fable-bakeoff`: step A's brief, then step B's card)
- Acceptance: (1) step A: the brief is on the queue before any Astra packet is sent, and the operator's word on it (including the scope change) is quoted here; (2) step B: three cuts on `docs/runbooks/ONE-SHOT.md`'s loop - one-shot #3 unchanged (its build hash matches the committed one) and two new ones from the same script - compared on M35-M46, the motion gate and the parent's read beside the approved cuts, served frozen with the voice (R26-178's link); the card asks the one question the brief names.
- Stop conditions: a lane's cut needs an engine change (it files a row; the comparison runs on the engine as it is); step A is not answered (Astra is not dispatched); R26-336 is not landed (Astra's cut waits).
- Regression: `python content/video_engine/scripts/gate_one_shot_floor.py <each build> --project <project> --reference <the approved reference>`
- Expected RED: no one-shot built since 09-16 on today's engine.
- Validate: `python content/video_engine/scripts/gate_one_shot_floor.py <each build> --project <project> --reference <reference>` then `python content/video_engine/scripts/build_review_queue.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T38: Integration and merge - per wave, the registries unioned, the generated files regenerated, CAPABILITIES, one commit per slice
- Status: pending
- Owner: parent; release_steward commits (explicit paths, never `git add -A`, never a push without the operator's current word)
- Depends on: each slice's review
- Items: R26-353 (at the lane A merge: send the Gemini lane `$SP/p72-t45/r26-353/profiles-rule.patch` for its profile source, `C:/Users/Snipe/Downloads/WA JiuJitsu Registry-20260608T183757Z-3-001/.agents/agents/` - outside the repo, so never written from here)
- Write set: the slices' patches; `docs/content-video-engine/CAPABILITIES.md`; the cards / recipes; the generated files (`docs/EFFECTS-CATALOG.*`, `page-boxes.v1.json`, `SPECIES-BY-SENTENCE.md`, the docs layers) regenerated by the parent; the goldens re-pinned once per wave with a sha table; `docs/WORKTREE-REGISTER.md`; this plan's evidence; the archive rows for each merged item (T0's format)
- Acceptance: per wave - `git apply --check` clean in the listed order; the whole suite on lane B run unpiped before and after, the diff of failures empty or each new one a named row; the H door identical except the listed instants; the "Before anything reaches main" checklist for any merge to main.
- Known environmental red, not in this chain: `test_worktree_register.py` fails from any worktree with no register row, and the 15 missing rows are the Codex lane's (NEW-3). It stays red until the other lane's rows land, so it is read in the whole-suite failure diff as a named pre-existing red, never as a T38 gate.
- Validate: `python -m pytest content/video_engine/tests/test_golden_frames.py -q` then `python content/video_engine/scripts/effects_catalog_check.py` then `python content/video_engine/scripts/build_docs_layers.py --check` then `python scripts/prp_validate.py .claude/PRPs/plans/P72-THE-BACKLOG-BURNDOWN.plan.md`
- Evidence: pending

### T39: P72-HG1 - the closing gate sheet
- Status: pending
- Owner: parent; the operator rules
- Depends on: T38 (the last wave), T10, T11, T23, T27 (R26-257), T35, T41
- Write set: `$SP/p72-t39/` (the sheet, frozen, on its own port), `docs/content-video-engine/review-queue.v1.json` (the row T0 framed, now `where` filled), this plan
- Acceptance: the eight items of the Human Gates table's P72-HG1 row, each with its frames beside the reference, served frozen; attached as reports, not asked: the burndown table (every id in `coverage.py`'s live universe and its final state) and T11's measured seal contrast with its frames; the operator's answers written to `OPERATOR-RULINGS.md` and here.
- Validate: `python content/video_engine/scripts/build_review_queue.py` then `python $SP/p72-t0/coverage.py`
- Evidence: pending

### T40: The dock's 9:16 fail set - a parked card never covers the schematic's plot or the panels+bars page's, the suite's known three reds
- Status: done - lane B d509ed7: the schematic's 9:16 card goes to a band outside the plot (its phase names counted as ink); panels+bars at 9:16 is a refused page with no placement; test_video_dock 64 + 2 skip (the known 3 reds gone)
- Owner: implementation_luna (LANE B), then reviewer (placement: the placer is a default, s106; the test is E45 §1 against the player's own boxes)
- Depends on: the operator's approval of this plan only (wave 1); P70 T2 (landed `3600ec5`, the schematic)
- Items: R26-337 (`hist:944`: at 9:16 the placer puts the card in the schematic plot's 'empty' room and overlaps the plot by 83,814 px^2), plus the two pre-existing `panels+bars-9:16` cases of the same class. No row carries those two (grep of the history, `BACKLOG.md` and P69 / P70 / P71: only R26-337's own text names them), so this slice carries them by pytest node id. Together they are the whole known fail set of `test_video_dock.py`, and this slice is the precondition for plan acceptance 6.
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`page_place` / `free_bands` / `dock_place`'s band choice at 9:16 - never `DOCK_OPTS`, `dock_opts` or `read_over_build`, which are P71 T15's), `content/video_engine/scripts/ledger_page.py` (`page_boxes` for the schematic and the panels pages at 9:16, only if their plot box is mis-measured), `content/video_engine/scripts/measure_page_boxes.py` (the pages' entries; the parent runs `--write`), tests: `content/video_engine/tests/test_video_dock.py` (no expectation relaxed), `content/video_engine/tests/test_page_boxes.py`
- Acceptance: (1) the three node ids pass - `test_a_dock_on_a_measured_page_never_covers_the_chart_the_player_drew[dense-line+schematic-9:16]`, `...[panels+bars-9:16]`, `test_the_parked_card_and_the_centred_card_read_the_same_bands[panels+bars-9:16]` - either because the placer finds a band that clears the plot, source, rail and caption anchor, or because `page_place` returns `None` by its own measure (the test's documented "no band wide enough - the dock keeps its solo geometry" path). The test's assertions are never loosened; (2) every other `PLACE_CASES` case gives the same placement as at the base (a before / after table of `page_place` for every builder x aspect); (3) the committed H door (16:9) compiles identically.
- Stop conditions: the only fix is to relax the test's forbidden set (never - report); a case needs a panels layout P70 / P71 owns (stop; sequence); `page_boxes` is mid-edit by P72 T15 (T40 goes first; T15 rebases).
- Regression: `python -m pytest -q content/video_engine/tests/test_video_dock.py -k "never_covers_the_chart or read_the_same_bands"`
- Expected RED (probed at lane-B `a469501`, 2026-09-25, revision 1): `FAILED ...::test_a_dock_on_a_measured_page_never_covers_the_chart_the_player_drew[dense-line+schematic-9:16]`, `FAILED ...::test_a_dock_on_a_measured_page_never_covers_the_chart_the_player_drew[panels+bars-9:16]`, `FAILED ...::test_the_parked_card_and_the_centred_card_read_the_same_bands[panels+bars-9:16]`, `3 failed, 33 passed, 24 deselected in 1.61s`.
- Validate: `python -m pytest -q content/video_engine/tests/test_video_dock.py content/video_engine/tests/test_page_boxes.py` then `python content/video_engine/scripts/measure_page_boxes.py --check` then COMMON-TAIL
- Frame acceptance: the schematic and the panels+bars pages at 9:16 with the parked card (or its solo geometry), before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T41: The balance's sign ink and the prop hatch - candidate sheets for the operator's pick and read
- Status: done - lane B a29e67a: the opt-in `tone: neg|pos|neutral` pill; the two sheets at `content/video_engine/projects/_proofs/p72-sign-and-hatch/` (main checkout) for P72-HG1 items (6) the pill form and (7) the hatch strength
- Owner: implementation_luna (LANE B for R26-334's opt-in key; a private test bed for both sheets)
- Depends on: P70 T7 (the balance) merged - both rows came from its review; P69 T6b's `PROP_SHADOW` (landed)
- Items: R26-334 (`hist:941`: Bravos labels each pan with a coloured pill - threat red, opportunity green, CHN 113 / 114 - and ours writes cream Kalam on cream pans; s118 inks names by their series and a balance side has none: a per-side `tone: neg|pos|neutral` drawn as a pill in the palette's sign inks, "with a candidate sheet for the operator"), R26-335 (`hist:942`: T6b's resting hatch, `PROP_SHADOW` alpha 1, reads at 3x but barely at 1x on charcoal; strengthening it changes the shadow law for every prop and moves their goldens - "a separate look pass ... the operator's read")
- Write set: the balance species module and its compiler key (step (0) names both from P70 T7's merge; `tone` refused by name outside `neg|pos|neutral`), the balance's card (the option), a private test bed `content/video_engine/projects/_proofs/p72-sign-and-hatch/` (a proof is a scene, s60), `$SP/p72-t41/` (the two sheets), tests: NEW `content/video_engine/tests/test_balance_tone.py`
- Acceptance: (1) R26-334: `tone` is opt-in - a balance with no `tone` renders byte-identically; with it, each pan carries a pill in the palette's sign ink. The sheet shows two or three pill forms on one real balance beat, from one source, beside CHN 113 / 114 by BRAVOS-FRAME, at full size and at 1x - it goes to P72-HG1 item (6), and the default form is set only by the operator's pick; (2) R26-335: no default changes. The sheet shows today's hatch and two stronger candidates on the charcoal page and on cream, at 1x and 3x, from one source, each with its measured contrast against the ground - it goes to P72-HG1 item (7). The chosen strength, if any, is a follow-up (the goldens re-pinned once with a sha table), and it lands after HG3.
- Stop conditions: a pill needs a palette ink that does not exist (report; never invent an ink); the hatch candidates need an engine change to render (the sheet composes them in the test bed only).
- Regression: `python -m pytest -q content/video_engine/tests/test_balance_tone.py`
- Expected RED: `tone` is an unknown balance key.
- Validate: `python -m pytest -q content/video_engine/tests/test_balance_tone.py` then `python content/video_engine/projects/_proofs/p72-sign-and-hatch/proof.py` then COMMON-TAIL
- Frame acceptance: both sheets, read by the parent before they reach the gate.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T42: The agenda beat's park-and-pan - R26-229 (a), built so P68-HG3's card shows both forms
- Status: done - lane A c665190: form (a) built in a private bed beside (b); P68-HG3's card carries item (C), the side-by-side clip and the recommendation (b); R26-229 (a) closes when the operator rules at HG3
- Owner: parent (the beat's authoring and the frame read), implementation_luna (the build) - LANE A, a private build
- Depends on: none on lane B (the engine as it is); lane A at a slice boundary (P69 T32 is writing `build_episode_h.py` - T42 never edits the committed door)
- Items: R26-229 (a) (`hist:672`: "the beat authored both ways on the 30 s bed - (a) a ~20 % park with a camera pan; (b) `melt` to the ball ... - and the two on one card"). (b) is built (the 30 s bed, on P68-HG3's queue text); (a) was not, so the row stays open until the card carries both.
- Write set: a private build dir `content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h-agenda-a/` (gitignored, as P69 T11's `build-h-s90-*` dirs are - step (0) confirms with `git check-ignore`) - the 30 s bed with the agenda beat as (a); `docs/content-video-engine/review-queue.v1.json` (`p68-steel-and-paper-h-hg3`'s agenda item: both forms, one card)
- Acceptance: (1) (a) and (b) render from one source bed at the same instants, frozen, served on P68-HG3's card side by side with the take; (2) (a) shrinks the chart ~20 % and pans the frame (the operator's words, `hist:672`), with the camera on a named thing (s79 Apply 5); (3) the committed door is untouched (byte-identical); (4) the gates run on both (the motion gate's report per form, attached).
- Stop conditions: (a) needs an engine change (it files a row; the beat is built on today's engine); the bed would have to be rebuilt under a served review link (never - a private dir, "review link = frozen copy").
- Regression: `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h-agenda-a`
- Expected RED: the build dir does not exist.
- Validate: `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h-agenda-a` then `python content/video_engine/scripts/build_review_queue.py`
- Frame acceptance: (a) and (b) at the beat's enter, mid and rest, side by side.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T43: The bracket's label room - measured at 16:9, a room WARN and an "above" fallback
- Status: done - lane B `a0396db`: R26-338 (the brace lifts its label above the bar when no side is clean; `check_brace` WARNs the room by number); R26-219's bracket half WARNed - its span still stands in the end-tag gutter, moved to T46 with R26-375's loose ends
- Owner: implementation_luna (LANE B), then reviewer (placement; findings are WARNs, s106)
- Depends on: P70 T5 (the brace: `check_brace` / `paintBracket`) merged - not landed at `a469501`; T13 (the bars pages' labels)
- Items: R26-219's second half (`hist:662`: "the row's second half, the bracket's label room measured at 16:9, is NOT done and this row stays open on it" - the railway page's `bracket` drew as a naked span at the plot's edge with no room for its label), R26-338 (`hist:945`: on a three-bar stacked page, bracing the first or middle bar puts the cusp's label over the neighbouring bar; the engine takes the least-overlapping side and the compiler says nothing because it cannot measure the room - "a room estimate that WARNs (s106 ...) and a fallback that sets the label above the bar")
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`paintBracket`'s label side and the "above" fallback), `content/video_engine/scripts/build_scene_timeline_f.py` (`check_brace`'s room estimate from `page_boxes`, a WARN by name), tests: NEW `content/video_engine/tests/test_bracket_label_room.py`
- Acceptance: (1) R26-219: on the railway page at 16:9 the bracket's label is measured against the page's boxes - it sits in free ground beside its span, or the compiler WARNs by name with the numbers (the label's box, the room); the naked span at the plot's edge is gone; (2) R26-338: bracing bar 0 or bar 1 of a three-bar stacked page sets the label above the bar when neither side is clean (its box clears every neighbouring bar: overlap 0), and the compiler WARNs by name - never refuses (s106); (3) a bracket or brace with a clean side renders byte-identically (every committed golden that carries one).
- Stop conditions: the "above" fallback collides with the title or the value tag (report the numbers; the WARN stands, the author's place stands).
- Regression: `python -m pytest -q content/video_engine/tests/test_bracket_label_room.py`
- Expected RED: the railway page's bracket label has no measured room and no WARN; bars 0 / 1 braced put the label over their neighbour (`$SP/p70-t5/frames/probe-bars3-bar0.png`, `bar1`), silently.
- Validate: `python -m pytest -q content/video_engine/tests/test_bracket_label_room.py` then COMMON-TAIL
- Frame acceptance: the railway page's bracket at 16:9 and the three braced bars, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T44: The bridge holds on a restart - R26-340's defects (1)-(5) and (7)
- Status: done - lane A `78c884f` (ahead of approval: the operator raised it, "the bridge is freaking out"); defect (6) is in the same commit, so T31's R26-336 line is done too; the live daemon picks it up at the merge to main
- Owner: implementation_luna (LANE A - the row names lane A the bridge scripts' owner); the parent reviews (a live send is the parent's)
- Depends on: the operator's approval of this plan; wave 1, before T31 (the row: "fix before P72 T31")
- Placement note (revision 1): R26-340 was filed after the parent's brief and found by the live universe read; the architect placed it here by its row's own owner and order. The parent confirms the placement.
- Items: R26-340 (`hist:947`; triage `$SP/bridge-triage/TRIAGE.md`): (1) `escalate()` toasts per packet per reason with no per-tick grouping, and the budget toast repeats per packet though its docstring says once (`bridge_daemon.py:554-558`, `:615-631`); (2) `send_gemini` guesses the conversation id by file times and drops the one agentapi prints (`bridge_send.py:196-200`); (3) `gemini_reply` takes the last completed reply without checking it post-dates the follow-up (`bridge_watch.py:154-166`); (4) repairs queued for defects a repair cannot fix (transcript truncation; an order with no `fetch_dir`); (5) `close_repaired` runs only on a tier-1 `done`, stranding an original whose repair closed elsewhere; (7) Gemini wrote two Bravos reviews into the Astra worktree root instead of the main checkout. (6) is R26-336's, in T31.
- Write set: `content/video_engine/scripts/bridge_daemon.py`, `bridge_send.py`, `bridge_watch.py`, `bridge_reply.py` (the repair queue and `close_repaired`, only as (4) / (5) need), the reply-path resolution (7) in whichever of them writes it (step (0) names it); tests: `content/video_engine/tests/test_bridge_daemon.py`, `test_bridge_send.py`, `test_bridge_watch.py`, `test_bridge_reply.py`
- Acceptance: (1) one tick with N escalations toasts once, grouped by reason, and the budget toast fires once per day (a test with ten planted packets: at most one toast per reason per tick); (2) the conversation id agentapi prints is the one recorded; no packet is left `conversationId: null` when the id was printed (a test on captured stdout); (3) a reply older than its follow-up is never taken as the repair's reply (a test: a reply stamped before the follow-up is refused, 0-3 s "replies" included); (4) a defect a repair cannot fix (truncation; no `fetch_dir`) is escalated once and never queued as a repair; (5) an original whose repair closed on any path is closed on the next tick; (7) a lane's reply is written under the main checkout's research path, never a worktree root (a test with a planted worktree cwd). No live packet is sent by a test; the daemon's restart behaviour is exercised on a copy of `sent/`.
- Stop conditions: a fix needs a change to the Gemini or Astra session tooling outside these scripts (report); a live send or a machine-level change (a scheduler entry) would be needed (never - the parent's).
- Regression: `python -m pytest -q content/video_engine/tests/test_bridge_daemon.py content/video_engine/tests/test_bridge_send.py content/video_engine/tests/test_bridge_watch.py content/video_engine/tests/test_bridge_reply.py`
- Expected RED: the new tests fail - ten planted escalations raise ten toasts; the printed id is dropped; a stale reply is taken; a truncation defect is queued as a repair; the stranded original stays open; the reply lands in the worktree root.
- Validate: `python -m pytest -q content/video_engine/tests/test_bridge_daemon.py content/video_engine/tests/test_bridge_send.py content/video_engine/tests/test_bridge_watch.py content/video_engine/tests/test_bridge_reply.py content/video_engine/tests/test_bridge_check.py content/video_engine/tests/test_bridge_handlers.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

## Verification

- Per slice: its Regression RED first, then its Validate chain unpiped (`never pipe a gated step into tail`, E99 s11), then COMMON-TAIL for every engine / gate slice, then the door identity (or the listed instants for a FIX).
- Per wave (T38): the whole lane-B suite before and after, the failure diff; `sync_kinetics.py --check`; the goldens; `effects_catalog_check.py`; `build_docs_layers.py --check` (green from T1 on).
- At the end: `python $SP/p72-t0/coverage.py` exits 0 with an empty unmapped set over the LIVE universe (the history read at run time, `BACKLOG.md`, P54 / P68-P71's open tasks, the open queue items); `python scripts/prp_status.py` shows P72's slices done except T39's operator answers; `BACKLOG.md`'s active queue carries only umbrella, OTHER-LANE, `⏸️` triggered and gate rows.

## Evidence And Handoff

- Planning evidence: `$SP/p72-plan/INVENTORY.md` (the verdicts; revision 1's changed lines and its new section F), `$SP/p72-plan/REVIEW.md` (the review this revision applies), `row-evidence.txt` (per-row commit and plan hits), `gitlog-all.txt` (1,608 commits across every branch), `open-rows.txt`, `open-rows-full.txt`, `legacy-rows.txt`, `plan-slices.txt`.
- Heads read: draft 1 - lane A `8f233a1`, lane B `e43c3d8`, main `013128e`; revision 1 - lane A `bf539e3` (plus the uncommitted history rows R26-337 .. R26-340), lane B `a469501`.
- Probes run for draft 1 (read-only): `build_capabilities_index.py --check` (FAIL, NEW-1), `pytest test_worktree_register.py` (1 failed, NEW-3), `pytest test_lab_log.py` (2 failed, R26-244), `effects_catalog_check.py` (0 failures, 50 recipes, 15 proven).
- Probes run for revision 1 (read-only): `pytest -q test_video_dock.py -k "never_covers_the_chart or read_the_same_bands"` at lane-B `a469501` (`3 failed, 33 passed, 24 deselected` - T40's RED); H's timeline species count (`build-h/steel-and-paper-h.timeline.json`: 25 scenes, 23 with species, 14 with pages - R26-108's closure); `grep -c "fewer cuts" docs/runbooks/ONE-SHOT.md` on lane A (`0` - T4's RED); `git merge-base --is-ancestor af869b7 a469501` (true - R26-283 / 281's engine half); `git log -1 bf539e3` ("R26-127 closed"); the engine's transition constants at `a469501` (`SUCK_S :6407`, `DIP_S :6428`, `SLIDE_S :6444`, untagged - T27's TR-3); a prototype of T0's live universe read (`$SP/p72-plan/universe_probe.py`: every `| **R26-N**` history row minus the archive's first column, mapped against this plan and INVENTORY - 339 history ids, 31 archived, 308 live; it found R26-338 / 339, filed mid-revision, and then R26-340, filed after them, with no hand edit; after T44 it reports no live id unnamed).
- The parent owns: the approval, T0's decisions, every brief, every frame read, the registry unions, the merges, the gate, and the operator.
- Deviations: revision 1 (2026-09-25) applied the review's 18 findings as the parent ruled them - one per finding, listed in the architect's hand-off - and carried R26-331 .. R26-340 and the two `panels+bars-9:16` cases. Slices added: T40, T41, T42, T43, T44 (T44 carries R26-340, filed after the brief and placed by the architect from its row - the parent confirms). Slices narrowed: T25 (the push reach is DONE at `af869b7`), T31 (R26-127 closed). No slice removed.

### T45: The bridge follow-ups - a verdict up front, an astra inbox, the profiles' source
- Status: done - lane A d07fec2 (R26-354 verdict-up-front, R26-355 the astra lane read from the packet folder); R26-353 moved to T38 (its source is outside the repo); the three live astra packets closed by the parent (their work is in main)
- Owner: implementation_luna (LANE A - the bridge scripts and the profile source)
- Depends on: T31 (done), T44 (done)
- Items: R26-354 (tier 0 refuses a report-landed reply with no `## Verdict up front` - a form failure, one repair), R26-355 (a FILE-BASED astra watcher: the packet's own `reply.md` moves it through tier 0), R26-353 (the tier-0 "never run the layer regen" rule written into the Gemini profile source so a sync keeps it)
- Write set: `content/video_engine/scripts/bridge_handlers.py` (`check_report_landed`), `content/video_engine/scripts/bridge_daemon.py` + `bridge_watch.py` (an astra lane that reads the packet folder, never a transcript), the profile source named by `WORK-ORDER-GEMINI-PROFILES-2026-09-05.md`, their tests
- Acceptance: (1) a report-landed reply without the verdict section FAILs tier 0 by name and queues one form repair; (2) the three astra packets in `sent/` land in `replied/` from their own `reply.md` on one tick, tier 0 runs, no toast storm (R26-340's one-summary rule holds); (3) the profile source carries the rule and a sync reproduces the four profiles byte-identical to lane B 8f8106b's
- Stop conditions: an astra reply.md that is not the lane's own (stale, or written by another lane) - report, never land it; the profile source lives outside the repo (report its path)
- Regression: `python -m pytest -q content/video_engine/tests/test_bridge_handlers.py content/video_engine/tests/test_bridge_daemon.py`
- Expected RED: the new tests - a verdict-less report-landed reply passes tier 0; an astra packet stays in `sent/` with `watch-skip.json`
- Validate: every `test_bridge_*` file, each in its own process; `bridge_daemon.py --once --dry-run` on a copy of the live bridge folder
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T46: The wave-3 follow-ups - the seal's keyline and twin, the owned exit's twin and advice, the stroke width, the 9:16 badge rail, the weak prints' values
- Status: done with carries - T46a-e landed (81f39ae, 976fcc4, 16ecb98, 095c3ad, 7f5ead9); the carries are P72-HG1 (16)-(21) and **T46f** (wave 10, 2026-09-26, on main `019cdcc`): R26-385 clause 2 (an extend after a windowed rescale), R26-373 (c) (punch / focus_zoom on a dock datum - camera resolved after the docks), R26-106 (b) the chart's series under `stroke_width`; R26-348 (the card-aspect re-pin) stays last and alone
- Sub-slices (the parent, 2026-09-26; dispatched on lane B `151636d`, disjoint write sets): **T46a** engine correctness - PRIORITY R26-385, PRIORITY R26-400, R26-330, R26-341, R26-386, R26-390, R26-325 / R26-397, R26-399, R26-401, R26-402; **T46b** seal, prop and stroke - R26-361, R26-362, R26-391, R26-106 / R26-365 (a); **T46c** docks, the probe and 9:16 - R26-365 (b) (c), R26-171, R26-388, R26-393, R26-394, R26-398, R26-344 / R26-404, R26-369, R26-381, then R26-348 (a re-pin - last, alone); **T46d** page marks and looks - R26-219's span, R26-373, R26-375, R26-379, R26-382, R26-383, R26-384, R26-387, R26-395, R26-396, R26-370; **T46e** gates, tools and captions - R26-368 (b), R26-371, R26-372, R26-349, R26-392, R26-403, R26-136 (5), R26-352, R26-356, R26-357, R26-358, R26-359. R26-105's six verbs wait for a sentence (not dispatched). R26-380 goes to T51b (the same measurer). **T46b DONE** - lane B `976fcc4`: R26-361 (a)(b)(c), R26-362 (a)(b), (c) closed by decision (a spring cutout keeps the card's rule, E99 s45), R26-391 (a)(b), R26-106 (a) / R26-365 (a) (`kinetics.stroke_width`, off by default); `seal-on-photo` re-pinned (the name's keyline only). Still open: R26-106 (b) the chart's series, (c) draw-reveals, the other four brushes; R26-365 (b)(c) are T46c's. **T46e DONE** - lane B `7f5ead9`: R26-368 (b), 403, 392, 349 (the premise was false - only the names), 356, 136 (5), 352 (in code; the operator's `scrub-terms.txt` does not exist yet), 358, 359; carried to P72-HG1: R26-371 (13), R26-357 (14), R26-372 (15). **T46c DONE** - lane B `16ecb98`: R26-393, 394, 344 / 404, 398 (`dock-depth` re-pinned), 369 (the icon size to P72-HG1 (16)), 365 (b) / 171 for a SOLO 9:16 dock; still open: the stacked 9:16 pair's rail mount (P72-HG1 (17)), R26-365 (c) (a written decision: keep 2b7b6a4's thinning - P72-HG1 (17)), R26-381 (P72-HG1 (18)), R26-388 (a) (a capture pass - the refactor stop) and (b) (P72-HG1 (19)), R26-348 (not started). **T46d DONE** - lane B `095c3ad`: R26-219, 373 (a)(b), 375, 379 (an option), 382 (the map side), 383, 384, 387 (the tags), 395, 396, 370; 3 goldens re-pinned (`hub-spoke-fail`, `vecmap-route-tokens`, `lens-over-the-line`); still open: R26-373 (c) (punch / focus_zoom on a dock datum - now unblocked by T46c), R26-387's pedestal sky, the seal-look hub's failed spoke (a dash, not T17's sever). **T46a DONE** - lane B `81f39ae`: R26-385 (clause 1; clause 2 after a windowed rescale is open), R26-400 (test_prop_shadow green), R26-341, R26-386, R26-390, R26-399, R26-401, R26-402; 3 goldens re-pinned; R26-325 / R26-397 held for P72-HG1 (20), R26-330 for P72-HG1 (21).
- Owner: implementation_luna (LANE B), then reviewer (R26-362 (b) is advice; s106 - WARNs, never refusals)
- Depends on: P72 T11 (the seal), P71 T6 (43363ea), P72 T13, T17 (the compiler's print chain, for R26-362 (b)), P70 T8 / P71 T15 / T19 (the dock code, for R26-365 (b))
- Items: R26-361 (a)-(c), R26-362 (a)-(c), R26-365 (a)-(c) (filed 2026-09-25 from the landings' findings); R26-368 (b) (`cadence()` in picture widths per second, E99 s30's own definition - added 2026-09-25); R26-369 (the agenda page form at 9:16) and R26-370 (the tiers' shared scale as the compiler's default, `axes.domain` honoured) - added 2026-09-25; R26-371 (the shorts' keyword on its crimson box under 3.97 - a measured candidate sheet for the operator's pick) and R26-372 (M48's caption reader counts the word's shadow as its ground) - added 2026-09-25; R26-106 (the stroke's width profile - its discovery landed in T27b's finding, the build is R26-365 (a)) and R26-171 (the 9:16 dock's badge rail - R26-365 (b)), moved from T27 when T27 closed; R26-373 (M49 on bars pages, a dock datum before its line is drawn, punch / focus_zoom on a dock datum) - added 2026-09-25; R26-219's span (the railway bracket's span stands in the end-tag gutter, through "741 RAILWAY SHARE PRICES": the engine moves it out, or the compiler refuses the edge) and R26-375 (a)-(c) (the brace's point toward its lifted label, a pin that the compiler's copied bar constants match the engine, the non-ASCII `[WARN]` prints) - added 2026-09-25 from P72 T43; R26-349, R26-357, R26-330, R26-341, R26-352, R26-356, R26-358, R26-359 (moved from T15 / T28 unbuilt) and R26-379..387 (the level's axis pill, page_boxes' loose ends, four panels at phone, the chart beside the map, the map's framing and the ping's glow, the hub's fail badge and DOM's look, the line vanishing in an extend's rescale, the ignored `dash` key, the lens over the tags) - added 2026-09-25; R26-136 (5) (the search misses for natural terms - index aliases; its (3) landed in T28) - added 2026-09-25; R26-388 (a live dock as a wall member; the 9:16 tall-member overlap) and R26-390 (the two-plate ground's front-loaded first frame under a morph) - added 2026-09-25; R26-391 (the verdict tile's gate credit and the seal refusal's stale message) and R26-392 (the ken-versus-camera clash ignores the ken's window) - added 2026-09-25; R26-393 (a hovered card reads as moving to the probe; blur veils the join), R26-394 (the probe cannot read a re-counted figure), R26-395 (a solo lights one bar, R30 lights two), R26-396 (the long form's end badge has no box) - added 2026-09-25 from P71 T23 / T24 / T30; R26-325 (row 12's played-vs-cold diff - cause found by T21: the page's will-change raster) with R26-397 (the template decision), R26-398 (a dock at a depth runs its badge row off the stage), R26-399 (stale notes left by the purity fixes) - added 2026-09-25 from P72 T21; PRIORITY R26-400 (a regression from P70 T1b `50b2f85`: the stamp's ink dims the contact shadow mid-handover - `test_prop_shadow` fails, weight 0.870) - added 2026-09-26 from a bisect; R26-344 / R26-404 (a callout ring on a parked page stays stage size), R26-348 (needs its own re-pin slice), R26-401 (`lpVarHex` cannot read the sign inks), R26-402 (a reference rule's fade-in never shown), R26-403 (the gate does not credit a bars extend) - added 2026-09-26; R26-105 (the relation layer: `rel: pin` built by T19; its other six verbs - aim, group, path, derive, camera, weight - wait for a sentence that needs one, then a slice) - carried 2026-09-26
- Write set: `scripts/species/chip.mjs` (the name's keyline), `build_scene_timeline_f.py` (`seal_gold`'s note; the owned-exit WARN), the engine (`paint` through `worldXfAt`; `strokeAt`'s width), `emit_choreography.py` (mirror rule 2), `authoring/shapes.py` (`dock_leave`'s description; `_aspect_clean`'s rail), the template's pill CSS (the rail), tests NEW `test_wave3_followups.py`
- Acceptance: each row's clause closes with a test and, where visible, a before / after frame read by the parent; R26-362 (c) and R26-365 (c) may close on a written decision with its frame; the H door identical except the instants listed.
- Stop conditions: a clause touches a function an in-flight slice owns (sequence it); the keyline change moves a committed golden (list it for the parent's read).
- Regression: `python -m pytest -q content/video_engine/tests/test_wave3_followups.py`
- Expected RED: the keyline follows the authored ink on a photo; no WARN for an exit curve past its page; `strokeAt` has no caller; a 9:16 dock's badge rail is dropped.
- Validate: the regression, then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T47: The panels page at phone, built - R26-316's build half
- Status: done - lane B `9c4cac1`: R26-366 - the two-era panels page holds at `longform:phone` (0.9 px to spare); four-panel pages and the companion keep T12's WARN with the reason (R26-381)
- Owner: implementation_luna (LANE B), then reviewer (a long-form preset's layout; findings WARN, s106)
- Depends on: P72 T12 (the phone WARN, `lpPanelBuildAt`), P71 T13 (the second axis's phone read)
- Items: R26-366 (R26-316's build half, filed 2026-09-25; T12 prints its WARN until this lands)
- Write set: the engine's panels painter at `longform:phone`, `ledger_page.py` (`_longform_panel_scale`, the panel region), tests NEW `test_panels_at_phone.py`
- Acceptance: at `longform:phone` a panels page's subs, ticks, rule names and bars clear the 59.08 px floor or the page takes the room it needs (measured by the probe); `_longform_panel_scale` reads the floor cut; T12's WARN stops printing for a page that now holds; every other preset byte-identical; frames at phone before / after.
- Stop conditions: the page cannot hold by arithmetic even with the room (report the numbers; the WARN stays).
- Regression: `python -m pytest -q content/video_engine/tests/test_panels_at_phone.py`
- Expected RED: the companion page at phone gets 210 px against ~327; subs at 15.3 px.
- Validate: the regression, `test_longform_phone_layout.py`, then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T48: A ring on a chart circles its datum - the chart-callout golden bound, a point-target mark off the line WARNed
- Status: done - lane B dcf1b8d: the engine resolves a datum on a docked chart through the card's transform and paints it above the card (the 2026-09-08 layer rule's own reason); the compiler refuses a dock datum that resolves to nothing; M49 in the probe; the golden bound and re-pinned
- Owner: junior_developer (LANE B), then the parent's frame read
- Depends on: none (the callout's target resolution; P72 T17 owns the compiler's print chain - union at the merge)
- Items: R26-367 (the operator, 2026-09-25: "why is the ring completely missing the line?")
- Write set: `content/video_engine/tests/golden/build_golden_sources.py` (`chart_callout`'s target), its source and frame (re-pinned by the parent), `content/video_engine/scripts/build_scene_timeline_f.py` (a WARN for a point-target mark over a chart's plot, off every series), tests NEW `test_ring_on_its_datum.py`
- Acceptance: (1) the `chart-callout` golden's callout sits on the line (its centre within its own radius of the datum it names; frame before / after); (2) a callout / ring / spotlight / squiggle / punch with a `point` target over a ledger page's or a docked chart's plot, farther from every series than its reach, compiles with one WARN naming the mark, the distance in px and the nearest datum's index (s106 - never a refusal); one on the line, or over no chart, prints nothing; (3) every committed timeline compiles identically but the new WARN lines (none expected on H).
- Stop conditions: the dock chart's series geometry is not known at compile time (then the WARN moves to the probe / M25 and the parent is told).
- Regression: `python -m pytest -q content/video_engine/tests/test_ring_on_its_datum.py`
- Expected RED: the golden's callout centre is off the line; a point-target callout off the line compiles silently.
- Validate: the regression, `test_ring_on_the_named_thing.py`, then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending


### T49: The spread's glow, a dial measured off D40 (R26-378)
- Status: done - lane B `9a59dd4`: `PS.SPREAD_A` 0.51 (D40's measured fill brightness) and `LP_SPREAD_GLOW` (the halo inside D40's band), `measure_line_bloom.py --spread`; the recipe unchanged; the hue is P72-HG1 item (11)
- Owner: implementation_luna (LANE B)
- Items: R26-378 (the `spread` fill gains a halo in its own ink, measured off D40 04:48 with `measure_line_bloom.py`'s fills method; the recipe unchanged)
- Write set: the engine's spread painter (T10's filter helpers), `measure_line_bloom.py` (CRLF), `bravos-line-bloom.v1.json`, NEW `tests/test_spread_glow.py`

### T50: The capabilities index page fits its budget
- Status: done - lane B `6481bda`: bloat measured first (0 duplicate lines, no repeated phrase worth cutting; the only bloat the pointer's repeated `CAPABILITIES.md:`, cut); `MD_MAX_BYTES` 44,000 -> 50,000 with its reason (the operator's word); the page 49,575 -> 45,432; `docs_find` builds the page's line
- Owner: junior_developer (LANE B)
- Items: the page over its cap (`build_capabilities_index.py --check`, `test_build_docs_layers`)
- Write set: `content/video_engine/scripts/build_capabilities_index.py`, its tests; `docs_find.py`'s capability line if it copies the page's format

### T51: The suite goes green - every test file passes at the lane head, each in its own process
- Status: done - T51a-d landed (lane B 1fffa97, c5b508c, f217607, 0cca46b); the effects gallery re-pinned (3702834); the first `run_full_suite.py` runs read (R26-405 carries what is left - T52)
- Sub-slices (the parent, 2026-09-26; on lane B `151636d`): **T51a** the engine's pinned orders - (3) chapter_pill, (4) portrait_parity, (7) chart_forms_2_5d; **T51b** layout and pins - (5) gate_empty_plot, (6) full_stage_page_is_measured with R26-380, (8) shape_skeletons[remake], (9) bar_value_morph, (10) balance_scale; **T51c** the older five - (11) animation_registry, (12) docs_manifest, (13) effects_gallery, (14) fed_full_stage_fixture, (15) fed_runoff_comparison - AND a committed full-suite runner (every test file in its own process, sequentially, run in the lane's own worktree so no gitignored input is missing, a summary with each failure's assertion). (1) R26-400 is T46a's; (2) is fixed. **T51a DONE** - lane B `1fffa97`: (3) and (7) were stale test pins (P71 T23 8204488 put the dock joins between the species and the chapters; P72 T6 9dc5bb6 gave the gauge the bars page's `const bar` prefix), (4) was code (P72 T47 9c4cac1 re-typed the card's literal; now `LP_CARD.TYPE_PX`, 0 px); goldens 233/233. **T51c DONE** - lane B `f217607`: (11) animation_registry (CODE - the registry reads the history ledger), (12) docs_manifest, (14) fed_full_stage_fixture, (15) fed_runoff_comparison (TEST); (13) effects_gallery NOT re-pinned (re-pin once at the integration head); `run_full_suite.py` committed (first run: 489 files, 451 passed, 38 failed, 0 flaked). **T51d DONE** - lane B `0cca46b`: test_idle_e49 (P71 T28's two live pages admitted; the flag is load-bearing for their pixels). **T51b DONE** - lane B `c5b508c`: (5) gate_empty_plot (CODE), (6) full_stage_page_is_measured (TEST) + R26-380 (a) (CODE, `lpBarNameRoom`; page-boxes re-measured), (8) shape_skeletons[remake] (the cite, :282), (9) bar_value_morph (re-pinned: the caption strip since 2bf45d6), (10) balance_scale (TEST); R26-380 (b) needs a ruling (no placement cost order on record). The effects gallery re-pinned at lane B `3702834` (187 cards). T51's fifteen items are closed; the full suite runs next.
- Owner: implementation_luna (LANE B), per failure; the parent reads each fix
- Depends on: the wave in flight (P72 T23) landing first
- Items: the full-suite sweep at lane B 7263013 (2026-09-26, `$SP/suite-sweep/NOTES.md`; 481 files, 20 real failures in 15 files, 0 load flakes) - (1) R26-400 `test_prop_shadow` (the stamp's ink dims the contact shadow; broke at P70 T1b `50b2f85`); (2) `test_decomposition_brace` - FIXED 8a4c10a (T20's `lpLitPhaseSegs` moved out of the brace's window); (3) `test_chapter_pill::test_render_paints_the_chapters_right_after_the_species` - the engine no longer has `paintSpecies(sc, t);` then `paintChapters(t);` (a slice inserted a line between them after 42d0fab); (4) `test_portrait_parity::test_no_landscape_literal_in_player_code` - `PHONE_PX: 12 * 1920 / 390` (P72 T47); (5) `test_gate_empty_plot` - the mark mirror lacks `axis_tag` (and `lens`); (6) `test_full_stage_page_is_measured` - `story+gauge`'s full-stage plot is not wider than the column's (170 = 170); (7) `test_chart_forms_2_5d` - `extrudeFaces(...)` now sits after the bar rect it must precede; (8) `test_shape_skeletons[remake]` - `render_baseline.py:265` no longer says `remake`; (9) `test_bar_value_morph` - the golden frame's pixels changed (between 557e1dc and 42d0fab); (10) `test_balance_scale[tip]` - the caption box overlaps the balance's footprint; (11) `test_build_animation_registry` (2) - orphans `CADENCE.STROBE_PX_S` and two reclassified research headings; (12) `test_build_docs_manifest` - the "kubelka" hit is RESEARCH-INDEX.md, not 44-INK-AND-SURFACE.md; (13) `test_effects_gallery` (3 pinned gallery frames); (14) `test_fed_full_stage_fixture` (3) - `_fake_entry()` got `focus`; (15) `test_fed_runoff_comparison` - `'P ? 150 : 60'` not in `buildLedgerBars`. Items (11)-(15) failed before 557e1dc. And the sweep's own gaps: `ign-copy.txt` misses about a dozen gitignored inputs (31 files failed on environment), and a deep scratch path breaks Blender's 260-char limit (a shorter export path).
- Write set: per item - the test or the code it names, never both without saying which is wrong; a pinned test is re-pinned only when the change it catches was intended (name the commit)
- Acceptance: the full sweep (every `test_*.py` and node test, each alone, sequentially) reports 0 real failures at the lane head; each fix says whether the TEST or the CODE was wrong, with the commit that broke it.
- Evidence: pending

### T52: The suite's standing failures (R26-405)
- Status: running - the runner stages inputs / skips with the reason, LF for nine fixtures, Blender's path limit named (lane B, the T52 commit); the six pre-existing failures were missing inputs (dated); open: R26-411's seven (three LF pins, the review queue's stale P65 pin, the plate library's absolute paths, the hand baseline, the fresh worktree's missing generated catalogue)
- The first `run_full_suite.py` on lane B (c0b42c4): 30 failures, none from wave 9 or P73; classified in R26-405 (missing gitignored inputs, Blender's path, CRLF working copies, six pre-existing unowned, the register). Build: the runner stages or skips absent inputs with the reason; LF for byte-compared fixtures; a short-path Blender run; each pre-existing failure diagnosed at its cause.

### T46f: The wave-3 carries - what T46a-e could not close
- Status: running - (1)-(3) DONE on lane B (the T46f commit): R26-385 clause 2 (`lpGrownPen`), R26-373 (c) (punch / focus_zoom on a dock datum, `camTarget`), R26-106 (b) (the series under `stroke_width`); open: (4)-(7) as named, and R26-408 (the x ticks double-print mid-rescale), R26-409 (figure.mjs reads the active state, not `lpDatumNow`), R26-410 (the end name moves over no ink in an extend's rescale phase)
- (1) R26-385 clause 2: after a WINDOWED rescale an extend cuts the revealed series to the old window (not probed by T46a). (2) R26-373 (c): punch / focus_zoom on a DOCK datum - the camera resolved after the docks are laid out (T46d stopped: it reorders T46c's dock loop, which has landed). (3) R26-106 (b) the chart's series under `kinetics.stroke_width`, (c) draw-reveals, the other four brushes (T46b built (a)). (4) R26-171 / R26-365 (b)'s stacked 9:16 pair - its rail mount is P72-HG1 (17), built after the read. (5) R26-387's pedestal sky (no sky above y 0). (6) R26-348 the card-aspect re-pin - last and alone. (7) R26-407 (from P71 T26): `span` refuses an unknown `form` by name, and a `box` form round the last move's stretch (Bravos A56). Also carried here: R26-105's six `rel` verbs (they wait for a sentence that needs them - only `pin` is built) and R26-136's remaining parts (3).
