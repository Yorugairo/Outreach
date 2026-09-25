---
id: P72-THE-BACKLOG-BURNDOWN
title: The backlog burndown - every open backlog row and plan slice DONE with evidence, CLOSED with the reason, or a named human gate
status: draft
operation: maintenance
risk: standard
owner: parent
branch: claude/fable-p68 (the plan, the bookkeeping, lane-A docs); engine, gate and script slices land on claude/p69-s90 (lane B), one writer per function, after the P70 / P71 slice that owns the same function
contract: tdd-v1
created: 2026-09-25
updated: 2026-09-25 (draft 1, architect_sol)
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
- five new items the reads found (section E).

**The counts (primary verdict per item; 343 items):**

| verdict | items | where it goes in P72 |
|---|---|---|
| DONE-UNCLOSED | 140 | T0 - the closing pass (archive rows and status lines, in batches) |
| CLOSE-STALE / -SUPERSEDED / -DUPLICATE | 35 | T0 - each closed with its ruling or superseding row |
| ENGINE (lane B) | 71 | T6-T27 by function, in waves 2-6 |
| TOOLING | 52 | T1-T3, T8, T9, T28-T32 |
| LANE-A (docs, H, production) | 4 | T4, T35-T37 |
| RESEARCH (the claims-gated lane) | 3 (+ R26-254 part 2) | T33, T34 |
| ALREADY-PLANNED (a P48 / P68 / P69 / P70 / P71 slice) | 13 | referenced, never duplicated |
| HUMAN | 8 | the gate list (merged with the existing HGs) |
| OTHER-LANE (a running Codex / Astra plan) | 11 | listed; P72 writes none of it |
| BLOCKED-EXTERNAL | 1 | R26-111 (a plate generation no cut asks for) |
| parent decision / bookkeeping | 5 | T0 |

The engine work is grouped by FUNCTION, one writer each, and sequenced after the P70 / P71 slice that owns the same
function (the ownership tables in P70 and P71 are this plan's too). The slices the brief named are all here: s130 (1)
the fill glow (T10), s130 (2) the seal's gold by the measured ground (T11), R26-315 (T12), R26-318 as the highest
priority (T6: a truth gate that cannot read is a false PASS), and R26-316/317/319-330 (T6, T7, T12, T17, T19-T22).
P71 T15 keeps the dock's `under: hover|blur`; P72 does not touch it.

`$SP` below means
`C:/Users/Snipe/AppData/Local/Temp/claude/C--Users-Snipe-Downloads-Outreach-Program--claude-worktrees-sweet-villani-1c3a16/45114c3b-258a-4ca8-9aaf-b674a804cc7e/scratchpad`.
Lane A = `C:/Users/Snipe/Downloads/Outreach Program/.claude/worktrees/fable-p68` (read at 8f233a1); lane B =
`.../worktrees/p69-s90` (read at e43c3d8 with `git show e43c3d8:<path>`; every `:line` below is at e43c3d8 and is
re-read by its SYMBOL in the brief).

### The slice table

T5 and T16 are unused numbers: R26-282 (T5's only item) was found DONE at `7d43e43`, and the page-states slice
moved to T26 behind P71's `buildLedgerLine` slices. The numbers match the inventory's pointers.

| P72 | items | class | owner | wave | depends on |
|---|---|---|---|---|---|
| T0 | the closing pass: 175 DONE/CLOSE items archived with evidence; plan status corrections; queue rows for P69-HG1..HG4 and P72-HG1; the parent decisions | bookkeeping | parent + speedster | 0 | the operator's approval |
| T1 | NEW-1: the recall layer builds again (capabilities index over its byte cap, 4 malformed rows) | TOOLING (lane A) | junior_developer | 1 | T0 |
| T2 | R26-244, 238, 240, 145, 162, 141: the suite green and its pins honest | TOOLING | implementation_luna | 1 | T0 |
| T3 | R26-237 (+196), 116, 219, 252: the recipes carry the rulings | TOOLING | implementation_luna | 1 | T0 |
| T4 | R26-195, 200, 202 (c), 188, 214 (a, c), 174, 193, 124, 136 (5): the builder's checklist and the record | LANE-A (doc) | parent (+ junior_developer) | 1 | T0 |
| T6 | R26-318, 303, 264, 319: the value gate reads every page | TOOLING (truth gate) + ENGINE | implementation_luna, reviewer | 2 | T0 |
| T7 | R26-326, 269, 189, 167: the motion gate credits what moves | TOOLING (gate) | implementation_luna, reviewer | 2 | P70 T8 (`_landings` / `_arrivals`) |
| T8 | R26-207, 208, 203, 212, 206: the long form's gates | TOOLING (gates) | implementation_luna | 2 | T0 |
| T9 | R26-140, 243, 251, 151, 323: the renders and the golden sources are deterministic | TOOLING | implementation_luna | 2 | T0 |
| T10 | s130 (1): filled marks glow - the gauge's fill and the primary bars, measured off Bravos | ENGINE | implementation_luna, reviewer | 3 | P70 T3 (landed), T9 |
| T11 | s130 (2): a seal's gold adjusts by the measured ground | ENGINE | junior_developer, reviewer | 3 | P71 T12 (`chip.mjs`) |
| T12 | R26-315, 316, 299: the panels page builds in view and holds at every preset | ENGINE | implementation_luna | 3 | T0 (+ the R26-316 decision in T0) |
| T13 | R26-274, 287, 250, 170, 217: a bars page writes its units and keeps its labels clear | ENGINE | implementation_luna | 3 | before P71 T25 / T31, or after both |
| T14 | R26-268 (HIGH), 278, 292: the captions read on every plate | ENGINE + TOOLING | implementation_luna | 3 | T0 |
| T15 | R26-253, 270 (+ R26-274's fixture): page_boxes carries every text box | ENGINE | implementation_luna, reviewer | 4 | T13 |
| T17 | R26-249, 317, 154, 43, 149, 214 (b), 209, 258, 44: the compiler says what it drops | ENGINE (compiler) | implementation_luna | 4 | T0 |
| T18 | R26-284, 288, 255, 256: figures and rings on a bars page | ENGINE | implementation_luna, reviewer | 4 | T13 |
| T19 | R26-328, 285, 271, 320, 267: docks keep their box, leave with the dip, ride a park | ENGINE | implementation_luna, reviewer | 5 | P70 T8, T9, T13; P71 T6, T15, T19, T23 |
| T20 | R26-286, 329, 35, 36: the sound follows the frame | ENGINE (sound) | implementation_luna | 5 | P70 T8 (`authoring/audio`) |
| T21 | R26-260, 21, 294, 321, 322, 324, 325: the named places the engine is not yet a pure function of t | ENGINE | implementation_luna, reviewer | 5 | P70 T8, T9; P71 T6, T15, T19 |
| T22 | R26-327, 304, 173, 169: the verdict stack | ENGINE | implementation_luna | 6 | T7 |
| T23 | R26-157, 146, 139: the melt's options | ENGINE | implementation_luna | 6 | T21, T30 (R26-115 / 138) |
| T24 | R26-153, 163, 150, 148, 152: the morph | ENGINE + TOOLING | implementation_luna | 6 | T7 (gate file, disjoint function) |
| T25 | R26-283, 281 (engine), 165, 164: the camera keeps the page in frame; the plate's moves take a window | ENGINE | implementation_luna, reviewer | 6 | P71 T32 (`kinetics/camera.mjs`) |
| T26 | R26-266, 275, 265, 277: a page's later states | ENGINE | implementation_luna, reviewer | 6 | P71 T3b, T13, T16, T28, T39; P70 T2 |
| T27 | R26-57, 72, 73, 142, 123, 302, 257, 2, 171, 106: the small engine rows | ENGINE | junior_developer | 4-6 (one commit each) | each row's named neighbour |
| T28 | R26-227, 215, 197, 198 (b, c), 178, 130, 183, 136 (3): scripts that cost runs or say the wrong thing | TOOLING | implementation_luna | 2 | T0; the H-door half after P69 T32 |
| T29 | R26-242, 301: citations resolve by row title | TOOLING | implementation_luna | 2 | T1 |
| T30 | R26-160, 166, 182, 161, 115, 138: files under the line cap; one fold; the region order | TOOLING (refactor) | implementation_luna | 3 | T2, T3 |
| T31 | R26-254 (1), 128, 129, 144, 127: the research tooling | TOOLING | implementation_luna | 2 | T0 |
| T32 | R26-85: the strobe's sharpness on real motion (a measurement) | TOOLING (measure) | implementation_luna | 4 | T9 |
| T33 | R26-311 (+ R26-29): the railway research and the as-of date, under the claims gate | RESEARCH | parent + the Gemini lane | 1 | T0 |
| T34 | R26-254 (2): the six dockets re-ingested under the gate | RESEARCH | parent + the research lane | 3 | T31 |
| T35 | R26-147: the full-page melt's design sheet | LANE-A (design) | implementation_luna | 6 | T23 |
| T36 | the P69 hand-off: the H-row follow-ups the fixes make possible (R26-281, 283, 302 rows; `VERDICT_STACK_ON`; the R26-197 shim) | bookkeeping (P69) | parent | per wave | the engine slice named |
| T37 | R26-175, 135 (4), P54 T7: the one-shot comparison (Fable, then Opus, then Astra) | LANE-A (production) | parent, implementation_luna, Astra | 7 | P71 T37 (last wave), T38 |
| T38 | integration and merge, per wave | - | parent, release_steward | per wave | each slice's review |
| T39 | P72-HG1: the closing gate sheet | - | parent; the operator rules | end | T38 |

**Honest flags. Read them before approving.**
1. **Counts are primary verdicts.** An item with two halves (e.g. R26-132: part 1 DONE, part 2 ENGINE) is counted once by
   the verdict that keeps it open. The inventory line names both halves.
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
   (R26-244). The first is the Codex lane's rows plus lane A taking main back; the second is T2.
6. **Six parent decisions are needed, none of them the operator's** (T0 records each): R26-316 (does the long form
   ever render at `phone`?), R26-44 (does the wire belong to the page?), R26-105 (build `rel: pin` only, the other
   six relation verbs wait for a sentence), P65 T6 (close the lab's promotion step - recipes are proved as beats in
   proof doors now), R26-168 (M38 stays an interim WARN, M45 the floor), R26-127 (a scheduled task for the bridge
   daemon is a machine change - ask or drop).
7. **Two running plans look stale** (`MP-AI-USEFUL`, `MP-NORMAL-OUTREACH`: no update since 2026-09-15). They are the
   package lane's; the parent asks that lane for a status line (a bridge note) - P72 does not close another lane's
   plan.
8. **No new operator question.** Every HUMAN item is either an existing gate (P68 HG1/HG3/HG4, P69 HG1-HG4, P70
   HG1, P71 HG1, P54 HG3) or a frame read added to P72-HG1. The rulings through E99 s130 and `review-answers.jsonl`
   were checked first; nothing ruled is re-asked (R26-124's race default: s8 chose none - both stay selectable, no
   ask; P65 HG1: withdrawn by s84, not re-asked).

## Intent And Acceptance

The backlog and the plans say only what is true: open work is either built, closed with its reason, or waiting on the
operator's eye with the frames served.

Plan-level acceptance:
1. Every id in `$SP/p72-plan/INVENTORY.md` ends in one of: archived with evidence (`backlog/archive/2026-09-completed.md`
   row: id, what closed it, the sha / file:line / ruling), carried by a named slice of P69 / P70 / P71 / P68 that is
   itself open only for its human gate, listed under OTHER-LANE with its owner, or listed once in this plan's Human
   Gates.
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
6. The whole-suite run on lane B at P72's last merge is green or each red is a named strict xfail with its row.
7. P72-HG1 is framed on the queue in T0 and served at the end (T39).

## Scope

- T0: the bookkeeping - archive rows, plan statuses, queue rows, the backlog's active queue, the parent decisions.
- T1-T4, T28-T32: tooling and docs that no P70 / P71 slice owns.
- T6-T27: the engine and gate rows, by function, sequenced behind P70 / P71.
- T33-T34: the two research orders under the claims gate.
- T35-T37: the design sheet, the P69 hand-off list, the one-shot comparison.
- T38-T39: integration and the closing gate.

## Not Building

- **Any P70 or P71 slice's work.** Those plans carry their own slices; P72 references them (ALREADY-PLANNED: R26-261
  in P71 T3b, R26-307 P71 T13, R26-309 P71 T6, R26-313 P71 T5, R26-33's ping P71 T22; P70 T2, T5-T13; P71 T3b, T5-T7,
  T8b, T12-T39). P71 T8 is DROPPED (E99 s129); T0 marks it.
- **The dock's `under: hover|blur`** - P71 T15, one commit (E99 s124 amended).
- **H body adoption** of any fix beyond the P69 hand-off list (T36): the body rows are P69's (T32-T34), held for
  P69-HG3 (the operator, 2026-09-25: "hold it all for a clean hg3 view").
- **The other lanes' plans**: MP-FED-LIQUIDITY, SHARED-MODEL-ENGINES, knockout-five-animated-variants,
  mp-series-visual-grammar, SCRIPT-REVIEW-CLEARANCE (Astra / the Codex MM lane); MP-AI-USEFUL and MP-NORMAL-OUTREACH
  (the package lane; they carry R26-66 and R26-88).
- **The six relation verbs beyond `pin`** (R26-105), unless the parent decides otherwise in T0.
- **`melt:all`'s engine slice** (R26-147): the design sheet only; the build waits for the operator's word on it.
- **The Japan re-render** (R26-137, R26-52): deferred by E99 s34 ("eventually, not now").
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
| **P68-HG3** | the VOICE for the long form (the takes auditioned on the unit); the caption size question (A) and the plate balance only if P69-HG3's one-look pick does not settle them; the agenda beat's built form (R26-229 (b): melt to a ball, splash onto the slate) | queue `p68-steel-and-paper-h-hg3` (drift already answered: s84) | the voice of the render | no (R26-229 folded in) |
| **P68-HG4** | the whole cut with the 1440p render; each remaining gate FAIL with its ruling; which motion rows are NEW verdicts against ep1's 16-of-35 baseline (R26-216); the Facebook file and the YouTube question | queue `p68-steel-and-paper-h-hg4` | the upload | no (R26-216 folded in) |
| **P69-HG1** | the chip's DEFAULT landing (`springPop` vs the stamp, one proof beat built twice) and whether the stamp's cue hits on the contact frame (`STAMP_CONTACT_S`); the ring-from-the-enter item is already closed by s121 (3) | P69 T13's proof door; queue row added in T0 | the chip default; one constant | queue row new |
| **P69-HG2** | the first prop on its own card: row 15's Fed stamp, frozen, with its enter / contact / rest frames and cue | P69 T23's card; queue row added in T0 | none now (rows built; "read at the end") | queue row new |
| **P69-HG3** | ONE look for the whole H episode: every page on the default profile vs every page in the long form, the whole episode rendered twice from one build at the same instants. Folded in: the default page's sans face (R26-259, Inter vs the fallback), row 7's card line names at half the phone floor (R26-289 - if refused, a taller card) | P69 T11's build; queue row added in T0 | P69 T33 (held) | queue row new |
| **P69-HG4** | the body read on frames beside build-f's at the same instants (sha-verified 1440p), the critic run once, the gates; folded in: P67 HG1's question - did the critic's two scores say something the gates did not | P69 T34; queue row added in T0 | P68 T7 / HG4 | queue row new |
| **P70-HG1** | the nine verbs' beats played with the take beside their Bravos frames; the ONE adoption question (which verbs a body row adopts); bringing P70 T8's paper prop out of quarantine | queue `p70-hg1-the-nine-verbs` | nothing inside P70 | no |
| **P71-HG1** | each verb as a beat with the take beside its Bravos frame; each engine fix before and after at the H instant; the ONE adoption question | queue `p71-hg1-the-bravos-verbs-wave-3` | nothing inside P71 | no |
| **P54-HG3 = the one-shot comparison** | the three one-shots on one loop (Fable's, Opus's, Astra's - E99 s66's order) side by side on M35-M46 and the parent's read; R26-175, R26-135 (4) and P54 T7 answered by one card | queue `p54-hg3-astra-fable-bakeoff` (refreshed by T37) | nothing | no (three items merged) |
| **P72-HG1** | the closing sheet, one line each, frames served: (1) s130 (1) the fill glow on the gauge and the primary bars at full size and at thumbnail width beside Bravos (a watch, the ruling is made); (2) s130 (2) a seal on a mid-tone photo before / after; (3) R26-257 the extruded bar's shadow re-lit from the stage light before / after ("on the operator's read", the row); (4) R26-146 the ball's `body=blend` clip; (5) R26-147 the `melt:all` design sheet (a yes / no to build); (6) P50 T7's quarantined still `art-embed-washi-tv` (the frame read it waits on); (7) the burndown's own list - every item's final state, one table | `$SP/p72-t39/` served frozen on its own port; queue row `p72-hg1-the-backlog-burndown` added in T0 | nothing inside P72 | yes |

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
| T7 | `gate_motion_density.py`: a NEW verdict-stack event read, the record-typing credit, a NEW refused-transform INFO row, a `--beat` window in `main` / `run` | P70 T8 (`_landings`, `_arrivals`), P71 T7 (`load_squint`, `_squint_gate`, `run`'s `squint=`), P71 T15 (`_layout_faults`, `_over_build_faults`) - T7 edits none of them; its `run` signature change is unioned by the parent after P71 T7 |
| T6 | `probe.py`'s value read (`:378`-`:398`: the zero line, the visible ticks, `line.grid, line.ax`), gate `_value_faults` (`:2679`), `ledger_page` `form_error`'s `gauge:h` refusal and the engine gauge branch (`:10782`-`:10972`, P70 T3's, landed) | P70 T3 (landed `e43c3d8`) |
| T10 | a NEW `lpFillGlow` beside `lpHotFilter` (`:11191`), one call line in the gauge's fill group (`:10805`) and one at a primary bar's rect; `measure_line_bloom.py` a NEW `--fill` mode; the band file's fills entry | P70 T3 (landed); P71 T24 (`lpBarMorphs`), T25 (projected bar paint), T29 (the `glow` outline species), T30 (`paintSolo`), T31 (story bars) - the call lines are placed where those slices' lines are not; the parent's `--3way` order is T10 before T25 / T29 / T31 or after all three |
| T11 | `species/chip.mjs` `sealGold` (`:140`) - it reads the measured ground as `stampRingInk` (`kinetics/stopaction.mjs:463`) does | P71 T12 (in flight on `chip.mjs`); before or after P71 T18 (also `chip.mjs`), the parent's order |
| T12 | `lpPanelStart`, the panel reveal clock, the panel layout per readability preset, the panel tick write | P70 T4 (landed `d0dd19b`) |
| T13 | the value / unit formatter (a prefix AND a suffix), the tick column's left bound, the `hlines` label placement (`:9013`-class), the bars' category-label side on a signed page; `ledger_page` unit validation; the treemap / tiers constants (`ledger_page.py:2070`, `:2072`) | P71 T25 and T31 also edit `buildLedgerBars` - T13 lands before both (they rebase) or after both |
| T14 | the caption layer on a picture plate (a plate's caption room, a contrast backing), `build_caption_pages.py`'s tokenizer, the caption's hand-over at a `morph:prop` exit | none (P71 T15 adds `#dockveil` to the template - a different region) |
| T15 | `ledger_page.page_boxes` (every page text box: basis, source, wrapped names), the compiler's E65 `empty`-room placer | T13 (the same pages' labels) |
| T17 | compiler: `validate_page_build_spans` (`:6776`), the page-warning print, the MELT twins beside `MELT_S` (`:124`), the tip-pill width WARN, `world.morph`'s `series` key, `IDLE_KINDS` on a plate world (`:87`), a camera-identity INFO, `dock_place`'s prop pad | P71 T5 (`row_stamp_fits`, `stamp_reserved_box`), T6 (`scene_exit`), T13 (`ledger_page.validate`), T15 (`DOCK_OPTS`, `dock_opts`, `read_over_build`) - none of these is T17's |
| T18 | `species/figure.mjs` `paintFigure`'s anchor on a bars page, a figure-restates-the-value refusal (compiler), a ring `value` target on a bar, the emphasized pill's yield | T13 |
| T19 | `render()`'s dock painter (the per-scene box), the dip's dock exit, the hatch under a dock camera, `paintPress`'s hold, a NEW `rel: pin` on a dock | P70 T8 (the dock-arrival branch), T9 (`paintChapters` in `render()`), T13 (`idle: hold`); P71 T6 (the dock exit), T15 (the hover), T19 (`paintDockVerdict`), T23 (`park_at`) |
| T20 | `authoring/audio.py` (the cue binder, a suck cue, the slot hand-off's cue instant), the bed envelope | P70 T8 (`authoring/audio`) |
| T21 | `meltMount` / `paintMelt` (after P71 T4's key, landed), `render()`'s melt call and hand ring, the snap's card box, the dock slot state, the title glow's repaint | P70 T8, T9; P71 T6, T15, T19 |
| T22 | `species/verdict.mjs`, the compiler's verdict member model, the dock door's freeze check | T7 |
| T23 | `species/melt.mjs` options (`OFF_SCREEN`, `body=blend`), the gather's axis sampling | T21, T30 |
| T24 | the morph's ground floor, `polyStrip`, gate M17's measure (`:3875`) for a planted source | T7 is the gate's other writer - disjoint functions |
| T25 | `kinetics/camera.mjs`'s push reach (from the measured boxes), the compiler's ken tuple window, `paintPlanes`' drift | P71 T32 (the `pedestal` key) |
| T26 | `lpPaintStates`' per-state domain and box, a NEW axes-recede token, the long-form palette's named-colour table | P71 T3b (`lpAxisHandOver`, the plain recast), T13 (`lpRightAxis` in `buildLedgerLine`), T16, T28, T39; P70 T2 |

The registries (`SPECIES_KINDS`, `PAGE_SPECIES`, the `_validate_entry` chain, `LP_PANEL_KINDS`, `buildPerform`'s return
and `paintPerform`'s dispatch, `DOCK_OPTS`, `sync_kinetics` module order, the cards, the golden lists,
`measure_page_boxes.py`'s lists) stay the parent's union, as in P70 / P71. Generated files are never in a patch.

### Waves

At most four slices at once (the runbook's concurrency).

| wave | slices | why together |
|---|---|---|
| 0 | T0 | the closing pass; nothing else starts until its first batch lands |
| 1 | T1, T2, T3, T4, T33 | no engine function; lane A docs, tests, recipes, research. T1 first of all (recall) |
| 2 | T6, T7, T8, T9 (+ T28, T29, T31 as tooling threads) | the gates, the determinism infrastructure; T7 after P70 T8. **T6 is the highest priority** (R26-318, a truth gate's false PASS): it depends on T0 only and is the first lane-B dispatch, alongside wave 1 if a thread is free |
| 3 | T10, T11, T12, T13, T14 (+ T30, T34) | s130 and the page families; T11 after P71 T12; T13 before P71 T25 / T31 |
| 4 | T15, T17, T18, T32 (+ T27's first commits) | the boxes, the compiler, figures - each after T13 |
| 5 | T19, T20, T21 | the dock branch and `render()` - after P70 T8 / T9 / T13 and P71 T6 / T15 / T19 / T23 |
| 6 | T22, T23, T24, T25, T26, T35 | species and states, after their P71 owners |
| 7 | T37, then T39 | the one-shot comparison after P71's last merge; the closing gate |

T36 (the P69 hand-off) runs at each merge; T38 (integration) closes each wave.

**Routing.** `implementation_luna` (Opus) builds most slices; `junior_developer` (Opus) T1, T11, T27; `speedster`
(Sonnet) makes T0's archive and status lines from exact text; `reviewer` (Opus) reviews T6, T7, T10, T11, T15, T18, T19,
T21, T25, T26 (a truth gate, a motion gate, a visual default, placement, seek purity, the camera); `explorer` runs T0's
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

### T0: The closing pass - 175 items archived or closed with their evidence, the plans' statuses corrected, the gates on the queue, the parent's decisions recorded
- Status: pending
- Owner: parent; speedster writes the archive rows and status lines from the exact inventory text, one batch per commit; explorer re-checks a 10 % sample of the shas before each batch commits
- Depends on: the operator's approval of this plan
- Write set:
  - `docs/content-video-engine/backlog/archive/2026-09-completed.md` (one row per DONE-UNCLOSED / CLOSE-* id: the id, what closed it, the sha / file:line / ruling - copied from `INVENTORY.md`);
  - `docs/content-video-engine/BACKLOG.md` (the active queue rewritten: the P69 / P70 / P71 / P72 umbrella rows with their children once, the OTHER-LANE rows with owners, one row per human gate; `LEGACY-REVALIDATION-2026-09` closed by this pass; R26-31, 35, 36, 43, 44, 45, 52, 57, 65, 66, 85, 123, 124 each moved to its verdict);
  - `docs/content-video-engine/BACKLOG-DISCIPLINE.md` (the second-pass report: before/after counts, the archived ids, the parent decisions);
  - plan status lines: P47 (retired; T4, T6, T7, T8 superseded - evidence per INVENTORY section D), P48 (complete), P51 (complete), P53 (complete), P54 (T9 done; T7 -> P72 T37), P65 (T6 closed per decision 4; T9 done at T3's merge; then complete), P67 (T6 done; complete), P68 (T4 done `6e78106`; T5b done), P69 (T85 done `ffa2877`, T87 done `965c4e2`), P71 (T8 DROPPED, E99 s129 (4));
  - `docs/content-video-engine/review-queue.v1.json` + the regenerated `REVIEW-QUEUE.md`: rows `p69-hg1-*` .. `p69-hg4-*`, `p72-hg1-the-backlog-burndown`; `lab-smoke-r2-plate-carries-a-card` and `lab-batch-r1-plate-carries-a-card` closed as withdrawn (s82 / s84 cited); `p54-hg3-astra-fable-bakeoff`'s text pointed at T37;
  - `docs/WORKTREE-REGISTER.md` (lane B's row names P72 and its one writer per function);
  - this plan (status, base, the decisions, T0 evidence).
  The history file is NOT edited: its banner pins the source slice's sha256; the archive row is the closure.
- Parent decisions recorded here (none is the operator's; each with the reason): (1) R26-316 - whether the long form ever renders at `phone` (H runs `middle`); (2) R26-44 - the wire belongs to the page or between pages; (3) R26-105 - build `rel: pin` only (R26-267 needs it), the other six verbs wait for a sentence; (4) P65 T6 - close the lab's promotion (recipes are proved as beats in proof doors); (5) R26-168 - M38 stays the interim WARN, M45 the floor; (6) R26-127 - a scheduled task for the bridge daemon (a machine change): ask the operator or drop; (7) R26-214 (c) - whether a breathing host is worth an ambient-lane order (recorded, not built); (8) R26-9 / R26-102 closure confirmed.
- Acceptance:
  1. Every id in `INVENTORY.md` sections A-E maps to exactly one of: an archive row, a P72 / P69 / P70 / P71 / P68 slice, an OTHER-LANE owner, or a gate in this plan - checked by `$SP/p72-t0/coverage.py` (written in this slice: it reads INVENTORY's ids and the four targets and prints the unmapped set, which must be empty).
  2. Each archive batch's shas resolve (`git log -1 <sha>`), sampled by explorer before the commit.
  3. The P69 HG rows and P72-HG1 are on the queue with what to judge, where, and what they block.
  4. The decisions are quoted in this plan with their reason.
- Stop conditions: an inventory verdict the sample contradicts (report, re-verdict, do not archive); a plan owned by another lane (P72 never edits MP-*, SHARED-MODEL-ENGINES, knockout, mp-series-visual-grammar, SCRIPT-REVIEW-CLEARANCE - it sends their owners a note).
- Regression: `python $SP/p72-t0/coverage.py`
- Expected RED: every INVENTORY id prints as unmapped (the archive and the queue carry none of the 175 yet).
- Validate: `python $SP/p72-t0/coverage.py` then `python scripts/prp_validate.py .claude/PRPs/plans/P72-THE-BACKLOG-BURNDOWN.plan.md` then `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md .claude/PRPs/plans/P71-THE-BRAVOS-VERBS-WAVE-3.plan.md .claude/PRPs/plans/P47-STOP-ACTION-BUILD-ON-AND-THE-CHART-MORPH.plan.md .claude/PRPs/plans/P48-CHART-TO-CHART-TRANSITIONS.plan.md .claude/PRPs/plans/P51-THE-ANIMATORS-LOOP.plan.md .claude/PRPs/plans/P53-WHAT-THE-ONE-SHOT-TAUGHT.plan.md .claude/PRPs/plans/P65-THE-RECIPE-LAB.plan.md .claude/PRPs/plans/P67-THE-VERIFIED-RECEIPT-AND-THE-CRITIC.plan.md .claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md` then `python content/video_engine/scripts/build_review_queue.py` then `python scripts/prp_status.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T1: The recall layer builds again - the capabilities index under its cap, its four malformed rows, and the ten search misses
- Status: pending
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
- Status: pending
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
- Status: pending
- Owner: implementation_luna (LANE B for the lab and the schema; the recipe JSON is the shared registry - the parent commits it with the catalogue)
- Depends on: T0
- Items: R26-237 (E99 s84), R26-196 (its two approved-recipe notes), R26-116, R26-219 (the card half), R26-252
- Write set: `content/video_engine/configs/effect_recipe.schema.json` (a `denied` status with `denied_reason` and `ruled_by`), `content/video_engine/effects/recipes/{card-becomes-the-chart,dock-lands-page-renames,plate-dock-wipe,spotlight-held-past-the-cut}.json` (status denied, the operator's words verbatim from s84), `content/video_engine/effects/recipes/{badge-ladder,read-park-build-write}.json` (the use notes: "even pill counts preferred"; the retitle's edge), a NEW `content/video_engine/effects/recipes/melt-then-rewrite.json` (status `candidate` unless an approved cut carries it - step (0) searches), `content/video_engine/effects/cards/page_species.json` (`page_species:note` options gain `keep`), `content/video_engine/scripts/lab_build.py` (`ARRIVAL_LANDS_S` `:168` and `ARRIVAL_MASS` `:210` read from `authoring.audio` - `arrival_mass`, `landing_contact`), `content/video_engine/scripts/effects_catalog_check.py` (a denied recipe is never counted proven), NEW `content/video_engine/tests/test_recipes_carry_the_rulings.py`, `content/video_engine/tests/test_lab_build.py` (a stamp candidate lands at `STAMP_CONTACT_S` with `ink`)
- Acceptance: (1) the four recipes read `denied` with the reason and `ruled_by: "E99 s84"`; `effects_catalog_check.py` prints 11 proven, not 15, and 0 failures; the catalogue marks them DENIED (regenerated by the parent); (2) the M38 / M45 readers take the new set (a test); (3) a stamp candidate built by the lab lands on the stamp's contact with ink mass; (4) `page_species:note` lists `keep`; (5) `melt-then-rewrite` validates against the schema.
- Stop conditions: a denied recipe is a member of an approved cut's recipe (report - the cut is frozen, E45); the schema change breaks the catalogue generator (report).
- Regression: `python -m pytest -q content/video_engine/tests/test_recipes_carry_the_rulings.py`
- Expected RED: the new test's four assertions fail - each file reads `"status": "proven"` (checked on lane A, 2026-09-25) and the schema's enum is `proven|candidate` (`effect_recipe.schema.json:254-257`).
- Validate: `python -m pytest -q content/video_engine/tests/test_recipes_carry_the_rulings.py content/video_engine/tests/test_lab_build.py content/video_engine/tests/test_lab_log.py content/video_engine/tests/test_gate_one_shot_floor.py` then `python content/video_engine/scripts/build_effects_catalog.py --check` then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T4: The builder's checklist and the record - the editing rules s74-s79 where the builder reads them, the stopped compiler marked, the rows' remaining notes written
- Status: pending
- Owner: parent (doctrine); junior_developer for the mechanical edits (LANE A)
- Depends on: T0
- Items: R26-195 (s74 / s75 / s76 into `ONE-SHOT.md`'s checklist and the critic's table; CAPABILITIES' compiler row STOPPED), R26-200 (s79 Apply 5: idle tokens counted, the camera on named things, the axes open), R26-202 (c) (the slot rule yields to the room rule when the room is gone), R26-214 (a) (a host plate enters the library only when approved, with its layer sidecar; the quarantine rule unchanged), R26-174 (one host rendering per cut), R26-193 (the calendar script's REWRITE ORDER, next letter - an order, never a patch), R26-124 (both race paths selectable; the current default written on the race row), P65's CAPABILITIES row `:96` (HG1 withdrawn, s84)
- Write set: `docs/runbooks/ONE-SHOT.md`, `content/video_engine/projects/systems-and-blowups/steel-and-paper/CRITIC-REPORT-H.md`'s table template (or the critic template the runbook names - step (0) finds it), `docs/content-video-engine/CAPABILITIES.md` (rows `:95`, `:96`, the race row), `content/video_engine/sources/PLATE-LIBRARY` doc or the plate-intake runbook the row names (R26-214 (a)), `content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/REWRITE-ORDER-<next letter>.md`
- Acceptance: (1) `docs_find.py "fewer cuts"`, `"fold a short plate"`, `"a light only"`, `"idle tokens"`, `"one host"` each hit `ONE-SHOT.md`'s checklist; (2) CAPABILITIES `:95` reads STOPPED (E99 s77) and `:96` no longer names an open HG1; (3) every edit cites its ruling; (4) no ruling text is changed.
- Stop conditions: a line would restate a ruling differently from its words (quote it instead); the calendar rewrite needs the operator's words beyond the ones recorded (write the order with what is recorded, list the gap).
- Regression: `python content/video_engine/scripts/docs_find.py "fewer cuts"`
- Expected RED: no hit in `docs/runbooks/ONE-SHOT.md` (lane B's `ONE-SHOT.md` has no "fewer cuts" line; grep 0 at e43c3d8).
- Validate: `python content/video_engine/scripts/docs_find.py "fewer cuts"` then `python content/video_engine/scripts/docs_find.py "one host"` then `python content/video_engine/scripts/build_capabilities_index.py --check` then `python content/video_engine/scripts/build_docs_layers.py --check`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T6: The value gate reads every page - M26 finds the scale on a long-form bars page, reads a range as two ends, never counts a card's own badge as page ink, and reads a width
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (a truth gate)
- Depends on: T0 (P70 T3 landed at `e43c3d8`)
- Items: R26-318 (HIGHEST: "a truth gate that silently cannot read is a false PASS"; H row 12's bars page is one), R26-303, R26-264, R26-319 (the width reader, then `form=gauge:h` admitted)
- Write set: `content/video_engine/scripts/probe.py` (the value read `:378`-`:398`: a scale source that does not need a visible gridline - the page's own data-to-pixel map the engine already computes, exposed on the probe, or the axis ticks; a range parser; a dock's own child boxes excluded from the ink under it `:226`-`:233`, `:700`-`:709`), `content/video_engine/scripts/gate_motion_density.py` (`_value_faults` `:2679` only: widths; the "cannot read" case becomes a FAIL, not a silent pass), `content/video_engine/scripts/ledger_page.py` (`gauge:h`'s refusal lifted in `form_error`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the gauge branch's horizontal form, `:10782`-`:10972`, and a probe hook for the scale, only if the scale is not already exposed), tests: NEW `content/video_engine/tests/test_value_gate_longform.py`
- Acceptance: (1) on a long-form bars page (H row 12's) M26 reads every bar's value against the page's scale and PASSes a true page, FAILs a planted wrong height; (2) a page M26 cannot read FAILs by name ("no scale on <page>"), never PASSes; (3) "+55-60%" reads as a range and a range bar is judged at both ends; (4) a badged card over a page is not M25 / M27 ink; (5) `gauge:h` compiles, draws its fill as a width, and M26 judges it; (6) every committed page M26 read before still reads the same (the goldens' probes unchanged); the committed H door compiles identically.
- Stop conditions: the scale can only come from pixels (report - the gate never fits a threshold to our own frames, E38); a committed cut goes RED on a real untruth (report it as a finding row, do not relax).
- Regression: `python -m pytest -q content/video_engine/tests/test_value_gate_longform.py`
- Expected RED: the long-form page reads "no scale" and the current `_value_faults` returns no fault for it (the silent pass); the range test reads 5560; `form=gauge:h` is refused by name (P70 T3).
- Validate: `python -m pytest -q content/video_engine/tests/test_value_gate_longform.py content/video_engine/tests/test_gate_motion_density.py content/video_engine/tests/test_fill_gauge.py` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` then COMMON-TAIL
- Frame acceptance: the parent reads the probe's contact sheet at H row 12's bars page and at the `gauge:h` golden, beside the gauge-94 golden.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T7: The motion gate credits what moves - the verdict stack's beats, a record's typing, and a window's own claim; the cuts counted with the transform each refused
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (a motion gate)
- Depends on: P70 T8 (`_landings`, `_arrivals`); the `run` signature is unioned by the parent after P71 T7 (`squint=`)
- Items: R26-326 (the stack's flights, recede and burst as events; a live host anchors the captions), R26-269 (a record's character clock counts on any plate), R26-167 (a `--beat` window mode that scores the window's own claim), R26-189 (an INFO row: every cut and dip, the transform it refused - s74)
- Write set: `content/video_engine/scripts/gate_motion_density.py` (a NEW verdict-stack event read, the record-typing credit in the events builder, a NEW INFO row, `main` / `run`'s window arguments), tests: NEW `content/video_engine/tests/test_motion_gate_credits.py`
- Acceptance: (1) H row 23 authored with `VERDICT_STACK_ON = True` (a private build) no longer FAILs M01 / M05 / M08 for want of events, and the one-slot version's verdict is unchanged; (2) `world-internal-memo-v1`'s typing earns M05 / M16 events without the steam; (3) a test-bed beat scored with `--beat t0,t1` is judged on its own window for M11; (4) the INFO row lists every cut / dip and prints `refused: <transform>` or `refused: (unnamed)`; (5) ep1's `build-f` report is byte-identical except the new INFO row; no FAIL level moves on the approved cuts.
- Stop conditions: crediting the stack needs `_arrivals`' body (P70 T8's) - stop and sequence; a credited event turns an approved cut's WARN into a PASS the reference does not support (report, E38).
- Regression: `python -m pytest -q content/video_engine/tests/test_motion_gate_credits.py`
- Expected RED: the stack build FAILs M01 / M05 / M08 (as row 23 did, R26-326); the memo plate's typing earns 0 events; `--beat` is an unknown argument.
- Validate: `python -m pytest -q content/video_engine/tests/test_motion_gate_credits.py content/video_engine/tests/test_gate_motion_density.py` then `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T8: The long form's gates - a landscape safe box, a long-form reference, M46 honest over 3:00, the opening gate on its own take, the brand line in the long shape
- Status: pending
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
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T0
- Items: R26-140 (`render_baseline.py --repeat` reports drift by surface), R26-243 + R26-251 (one fix: the template sets `__fontsSettled` after its post-font rebuild and `prepare_page` waits on it, not a fixed 250 ms; the un-awaited `document.fonts.ready` at `:484` removed), R26-151 (the builder's non-deterministic input named and pinned), R26-323 (`write_surface` writes `newline="\n"`)
- Write set: `content/video_engine/scripts/render_baseline.py` (`prepare_page`, a NEW `--repeat`), `docs/content-video-engine/samples/scene-evidence-player.template.html` (the flag set after the font rebuild - a region P71 T15's `#dockveil` does not touch), `content/video_engine/scripts/build_golden_sources.py`, tests: NEW `content/video_engine/tests/test_render_determinism.py`, `content/video_engine/tests/test_golden_frames.py` (a second build of the sources is byte-identical)
- Acceptance: (1) a CPU-throttled capture of the `tiers` / `treemap` / `race-path-eased` pages matches the golden; (2) `--repeat 3` on the data-to-bars golden reports 0 differing bytes or names the surface and the cause; (3) building the golden sources twice is byte-identical and LF; (4) no golden moves.
- Stop conditions: the drift is GPU raster timing that no page signal can cure (report the probe's numbers; the goldens keep their fresh-page rule).
- Regression: `python -m pytest -q content/video_engine/tests/test_render_determinism.py`
- Expected RED: the throttled capture renders the title in the fallback face (R26-243's diff class); the second source build differs on `tiers-two` / `treemap-cross`; the sources land CRLF.
- Validate: `python -m pytest -q content/video_engine/tests/test_render_determinism.py content/video_engine/tests/test_page_boxes.py` then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T10: s130 (1) - filled marks glow: the gauge's fill and the primary bars carry an emissive halo in their own ink, measured off Bravos's fills, seek-exact
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (a visual default on every bars page)
- Depends on: P70 T3 (landed); T9 (the captures the measure runs on are settled); the `--3way` order against P71 T25 / T29 / T31 (the ownership table)
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
- Status: pending
- Owner: junior_developer (LANE B), then reviewer (the seal's contrast, s123 / s127)
- Depends on: P71 T12 (in flight on `species/chip.mjs`); the parent orders it against P71 T18
- Items: E99 s130 (2): "a SEAL's gold (rings, ring text, name, shockwave) adjusts by the MEASURED ground under it, as the bare-prop ring already does (P70 T1c `stampRingInk` / `ringInkUnder`), holding the seal's contrast floor on a photo plate"
- Write set: `content/video_engine/scripts/species/chip.mjs` (`sealGold` `:140`: its ground is the measured luminance under the seal, not the row's authored `ink`; `CHIP_SEAL.CONTRAST_MIN` 3.0 kept), the engine's chip region via `sync_kinetics.py --write`, the dock-stamp ring paint that calls it (one line), tests: `content/video_engine/tests/kinetics/chip.test.mjs`, a NEW golden `seal-on-photo` (a mid-tone photo plate)
- Acceptance: (1) on a mid-tone photo the seal holds >= 3.0:1 (today 1.55:1, the parent's finding); (2) on the dark ledger ground the gold is `#E8B86D` unchanged, on cream `#A07F4B` unchanged (byte-identical goldens); (3) the shockwave takes the same resolved gold (s127 (2)); (4) the seal stays open over the chart (s128); (5) a bare prop's ring is untouched.
- Stop conditions: the measured ground under a seal varies across the seal's box beyond one ink's reach (report the spread; one gold per seal, the darkest ground wins - the parent confirms).
- Regression: `node --test content/video_engine/tests/kinetics/chip.test.mjs`
- Expected RED: a new test with a measured mid-tone ground (luma ~0.45) gets `#E8B86D` back (1.55:1) because `sealGold` reads `sp.ink`.
- Validate: `node --test content/video_engine/tests/kinetics/chip.test.mjs` then `node --test content/video_engine/tests/kinetics/stopaction.test.mjs` then COMMON-TAIL
- Frame acceptance: the seal on a photo, on the ledger ground and on cream, before / after (`$SP/p72-t11/frames/`) - to P72-HG1 item (2).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T12: The panels page builds in view and holds at every preset
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T0 (decision 1, R26-316); P70 T4 landed (`d0dd19b`)
- Items: R26-315 (a hidden panel's build waits for its reveal: the bars grow in view over ~1.5 s, Bravos DOM 06:02-06:04), R26-316 (the panels layout per readability preset - `phone` holds the s90 floor with the line alone, or the long form is refused at `phone` by name, per decision 1), R26-299 (a panel's tick text writes whole or not at all)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`lpPanelStart`, the panel reveal clock, the panels layout's preset branch, the panel tick write), `content/video_engine/scripts/ledger_page.py` (the phone-preset check if decision 1 refuses it), tests: `content/video_engine/tests/test_companion_bars.py` (the strict xfail flips and is removed), a NEW `content/video_engine/tests/test_panels_page.py`
- Acceptance: (1) the golden's hidden panel shows its bars at 0 % on its first visible frame and grows in view; (2) the panels page at `phone` holds 59.08 stage px labels or is refused by name; (3) no "%" without digits on any frame of the resize golden; (4) the H door's changed instants are row 21's panels only, each read.
- Stop conditions: the reveal clock is shared with a P70 slice still in flight (report).
- Regression: `python -m pytest -q content/video_engine/tests/test_companion_bars.py`
- Expected RED: the strict xfail pinned by P70 T4 (R26-315) is the RED - it XPASSes when fixed, so the GREEN commit removes the marker.
- Validate: `python -m pytest -q content/video_engine/tests/test_companion_bars.py content/video_engine/tests/test_panels_page.py` then COMMON-TAIL
- Frame acceptance: the resize golden at the reveal and at ~12.9 s, before / after; DOM 06:02-06:04 by BRAVOS-FRAME.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T13: A bars page writes its units and keeps its labels clear
- Status: pending
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
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T0; HIGH - "the contrast backing is owed before HG4" (R26-268, recurred on row 17)
- Items: R26-268, R26-278, R26-292
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (a plate's caption room, as `;room=` places cards - a NEW `PLATE_OPTS` key, refused by name when malformed), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (the caption layer: the room, a contrast backing measured against the plate under it, the hand-over wait at a `morph:prop` exit), `content/video_engine/scripts/build_caption_pages.py` (an opening quote rides the word after it, a closing one the word before), tests: NEW `content/video_engine/tests/test_plate_caption_room.py`, `content/video_engine/tests/test_build_caption_pages.py`
- Acceptance: (1) on the desk plate (rows 12, 17) the caption's unspoken words hold the caption contrast floor; (2) a declared room places the caption off the host's collar (row 7) and the viaduct's edge (row 13); (3) `And "don't try to call the top"` shows `And "don't try` on screen; (4) the next row's caption does not paint over a page collapsing into a prop; (5) a plate with no room declared captions as today (byte-identical).
- Stop conditions: the backing reads as a new box the doctrine refuses (a caption box on the long form is ruled? - step (0) greps the rulings for the strip's form; report before building).
- Regression: `python -m pytest -q content/video_engine/tests/test_plate_caption_room.py`
- Expected RED: `;caption_room=` refused as unknown; the quote test reads `And" don't`.
- Validate: `python -m pytest -q content/video_engine/tests/test_plate_caption_room.py content/video_engine/tests/test_build_caption_pages.py` then COMMON-TAIL
- Frame acceptance: rows 7, 12, 13, 17 at their caption instants, before / after; row 15 at 237 s.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T15: page_boxes carries every text box, and the E65 room keeps them clear
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (placement; findings are WARNs, s106)
- Depends on: T13 (the same pages' labels)
- Items: R26-253 (the basis label, source, title, sub and end tags stay out of the `empty` room), R26-270 (a wrapped bar name's box, measured against the source foot and the caption band), R26-274's fixture half (the four unmeasured pages - `ev-debt-issuance-line-v1`, `ev-index-concentration-bars-v1`, `ev-hbm-wafer-ratio-bars-v1`, `ev-two-clocks-bars-v1` - measured into `page-boxes.v1.json` by the parent)
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
- Status: pending
- Owner: implementation_luna (LANE B); one commit per item group, one compiler writer at a time
- Depends on: T0 (decision 2 for R26-44)
- Items: R26-249 (every page's entry + build + leave checked against its row, authored or not), R26-317 (a door prints the page's E79 WARN from `ledger_page.measure_unit_warnings`), R26-154 (`MELT_T_S`, `MELT_M_S` twins beside `MELT_S` `:124`, pinned by `test_transitions_e47`), R26-43 (a tag wider than its chart WARNs by name instead of dropping its tip pill), R26-149 (`world.morph` takes a `series` word, refused by name out of range), R26-214 (b) (`;idle=figure` refused on a `plate_option:world` plate, `IDLE_KINDS` `:87`), R26-209 (an INFO line: the open zoom at every scene boundary; a key set that never returns to identity names the next row's carry or WARNs), R26-258 (`dock_place` pads a `dock_kind:prop` box by `PROP_SHADOW`'s reach toward the light's fall), R26-44 (the wire's visibility by decision 2 - on the page's first cream frame, or between pages)
- Write set: `content/video_engine/scripts/build_scene_timeline_f.py` (`validate_page_build_spans` `:6776`, the page-warning print, the MELT constants, the tip-pill width check, `world.morph` validation, the plate idle check, a camera-boundary INFO, `dock_place`'s prop pad); `docs/content-video-engine/samples/scene-evidence-engine.mjs` only for R26-44's wire and R26-149's series pick; tests: NEW `content/video_engine/tests/test_compiler_says_what_it_drops.py`, `content/video_engine/tests/test_transitions_e47.py`
- Acceptance: (1) an unauthored page on a short row is checked (the 44 compiled timelines replayed: none refused, as the row measured); (2) the H door's build log prints each E79 WARN its pages carry; (3) the twins exist and the pin fails when one is edited alone; (4)-(6) each new refusal / WARN names the key and the numbers; (7) the H door and every committed timeline compile identically (`engine_sha256` aside) except the new INFO / WARN lines.
- Stop conditions: a refusal would break a committed timeline (make it a WARN and report, s106); the prop pad moves a committed prop (report - the author's place stands).
- Regression: `python -m pytest -q content/video_engine/tests/test_compiler_says_what_it_drops.py`
- Expected RED: each case compiles silently today (the rows' own measurements; `MELT_T_S` absent at `:124`; `IDLE_KINDS` admits `figure` on any plate).
- Validate: `python -m pytest -q content/video_engine/tests/test_compiler_says_what_it_drops.py content/video_engine/tests/test_transitions_e47.py` then `python content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py` (the build log read for the WARN lines) then COMMON-TAIL
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T18: Figures and rings on a bars page - a figure never double-prints its bar's value, a ring can circle the value, a centred figure keeps its anchor, the pill yields
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (E77 / E56: truth and the ring's one use)
- Depends on: T13
- Items: R26-284 (a figure that restates the bar's own value is refused by name - the value is the figure - or the hand-over is a true in-place morph), R26-288 (a `value` target on a bar: the value label's box; after P69 T26a it reads the morphed top), R26-255 (`paintFigure` keeps a centred bar figure's anchor on a page with chart states), R26-256 (an emphasized bar's pill yields to its figure on the figure's clock)
- Write set: `content/video_engine/scripts/species/figure.mjs` (`paintFigure`'s anchor), `content/video_engine/scripts/species/compare.mjs` (only the offset that reads the anchor, `:266`), the ring target resolution for a bar in the engine, `content/video_engine/scripts/build_scene_timeline_f.py` (the figure-restates-value refusal; the ring `value` target's validation), `sync_kinetics.py --write`, tests: `content/video_engine/tests/kinetics/figure.test.mjs`, NEW `content/video_engine/tests/test_bars_figures_and_rings.py`
- Acceptance: (1) H row 17's 94 bars page prints "94%" once at every frame (M28 PASS at 5:32); (2) a ring on a bar's value circles the label, not the bar; (3) a bars page with a `chart_to` keeps a centred figure centred; (4) no H frame changes except row 17's hand-over (listed, read).
- Stop conditions: the refusal would reject a committed H row (make it a WARN; report the row for P69 T36's hand-off).
- Regression: `python -m pytest -q content/video_engine/tests/test_bars_figures_and_rings.py`
- Expected RED: the M28 pair `val:94% on bracket:94% at 5:32` (R26-284's crop), the ring's ellipse crossing "Capex, next two years".
- Validate: `node --test content/video_engine/tests/kinetics/figure.test.mjs` then `python -m pytest -q content/video_engine/tests/test_bars_figures_and_rings.py` then COMMON-TAIL
- Frame acceptance: row 17 at its hand-over, before / after; the ring golden.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T19: Docks keep their box, leave with the dip, ride a park; the hatch rides the dock's camera; a press card holds
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer
- Depends on: P70 T8, T9, T13; P71 T6, T15, T19, T23 (the dock branch of `render()`); T0 decision 3 (R26-105 / R26-267)
- Items: R26-328 (the painter's box per scene, not per asset id), R26-285 (a dip clears the outgoing docks as a wipe does; the 1.4 s snap never moves an exit across a landing), R26-271 (the hatch rides the dock camera's transform), R26-320 (`paintPress` takes the drift-hold's span hand-over and light band), R26-267 (`rel: pin` - a dock parented to another dock's pose, read and park; the relation layer's first verb, E97's grammar)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`render()`'s dock painter box, the dip's dock exit, the hatch, `paintPress`, the pinned pose), `content/video_engine/scripts/build_scene_timeline_f.py` (`rel: {pin: <dock>}` on a dock, refused by name when the target is absent or later), `content/video_engine/scripts/species/press.mjs` if `paintPress` lives there, tests: NEW `content/video_engine/tests/test_docks_keep_their_box.py`
- Acceptance: (1) row 23's workaround (`dock-h-railway-share-ring`) is no longer needed - the same id docks at the new scene's box; (2) a dip takes the outgoing docks with it; row 17's docks may end on the boundary; (3) the hatch stays on the prop under a dock zoom / pan; (4) a held press card drifts and catches its band; (5) SELL stamps on the ticket on its own word and rides the ticket's read-then-park; (6) the H door compiles identically; its changed instants listed and read.
- Stop conditions: any of the five needs a function a P70 / P71 slice has not landed (stop, the parent sequences).
- Regression: `python -m pytest -q content/video_engine/tests/test_docks_keep_their_box.py`
- Expected RED: the second dock of one id draws at the previous scene's box (R26-328); the dip leaves the docks standing until the snap; `rel` is an unknown dock key.
- Validate: `python -m pytest -q content/video_engine/tests/test_docks_keep_their_box.py content/video_engine/tests/test_golden_frames.py` then COMMON-TAIL
- Frame acceptance: rows 17 and 23 at the named instants, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T20: The sound follows the frame - the suck's cue, the slot hand-off's cue on the frame that shows it, the bed swell on the arrival that lands
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: P70 T8 (`authoring/audio`)
- Items: R26-286 (a cue for the suck from the existing library - the melt's / the throw's family - bound by the door's cue check), R26-329 (the slot hand-off's cue at the frame the card is first seen, E99 s116), R26-35 (the bed swell keyed to the arrival that lands - step (0): P69 T84 `e416df5` may already have moved it), R26-36 (one assertion: H's `:cut;then=` rows read as the author meant, the legacy suffix reading kept for the shipped plans, `authoring/audio.py:196-210`)
- Write set: `content/video_engine/scripts/authoring/audio.py`, `content/video_engine/sound/` cue map (the suck), the slot hand-off clock if the fix is in the engine (one function), tests: `content/video_engine/tests/test_authoring_kit.py` (the cue binder's), `content/video_engine/tests/test_landing_sound_follows_the_landing.py` (P69 T84's), NEW `content/video_engine/tests/test_sound_follows_the_frame.py`
- Acceptance: (1) `SOUND-PLAN.json` for H names a cue at every suck; (2) row 23's hand-off cues land within one frame of the card's first visible frame, and row 23's 0.8 s lead can be removed (a P69 T36 hand-off item); (3) the bed swell sits on the camera arrival in Tokyo's recorded plan (checked, not re-rendered - the cut is frozen, E45); (4) the approved shorts' cue plans are byte-identical.
- Stop conditions: fixing the hand-off moves an approved cut's cue (report - frozen cuts keep theirs).
- Regression: `python -m pytest -q content/video_engine/tests/test_sound_follows_the_frame.py`
- Expected RED: no suck cue in H's plan; the hand-off cue at +0.32 s against a card first seen at ~+0.9 s.
- Validate: `python -m pytest -q content/video_engine/tests/test_sound_follows_the_frame.py` then `python content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py` (the cue check in its log)
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T21: The named places the engine is not yet a pure function of t
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (seek purity; goldens move)
- Depends on: P70 T8, T9; P71 T6, T15, T19 (`render()`); T9 (the determinism probe)
- Items: R26-260 + R26-21 (the snap's card box a pure function of t: forward play and a cold seek agree at 57.38 s and inside the 0.45 s window), R26-294 (the dock slot state pure: the leases record at 306.34 s on a jump seek), R26-321 (the melt clone taken from the page as painted at `span[0]`, not the live frame - moves every melt golden), R26-322 (`melt:morph`'s hand ring computed after `paint(wA, prev)`), R26-324 (the title glow repainted whole after a colour change - a forced re-layout or an isolated glow layer), R26-325 (row 12's fresh-vs-played diff DIAGNOSED first; its fix is a follow-up in this slice only if the cause is one of the above)
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
- Status: pending
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
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T21 (`meltMount`), T30 (R26-115's region order and R26-138's single vortex map)
- Items: R26-157 (the ball picked off the screen and thrown back faster, E99 s56), R26-146 (`body=blend`: the inks merge, E99 s49 - built, then the operator's eye at P72-HG1), R26-139 (the axes' lines sampled so they curl under `melt:gather`)
- Write set: `content/video_engine/scripts/species/melt.mjs`, the engine's melt region via `sync_kinetics.py --write`, `content/video_engine/scripts/build_scene_timeline_f.py` (the two option tokens, refused by name elsewhere), the melt card(s), tests: `content/video_engine/tests/kinetics/melt.test.mjs`, one golden per new option
- Acceptance: (1) each option is opt-in; every committed melt renders byte-identically; (2) the off-screen throw leaves frame and returns faster (the numbers in the golden's sidecar); (3) the blend's mixed ink is measured on its golden; (4) the gather curls the axes.
- Stop conditions: the blend needs a colour space the page does not use (report).
- Regression: `node --test content/video_engine/tests/kinetics/melt.test.mjs`
- Expected RED: `melt:throw:offscreen` and `body=blend` refused as unknown tokens.
- Validate: `node --test content/video_engine/tests/kinetics/melt.test.mjs` then COMMON-TAIL
- Frame acceptance: each golden before it is pinned; the blend clip to P72-HG1 item (4).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T24: The morph - the soak's floor in seconds, M17 honest on a planted source, `polyStrip` beyond x-monotone, the two untested goldens
- Status: pending
- Owner: implementation_luna (LANE B)
- Depends on: T7 (the gate file's other writer; T24 edits only M17's measure)
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

### T25: The camera keeps the page in frame; the plate's moves take a window
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer (the camera)
- Depends on: P71 T32 (`kinetics/camera.mjs`'s `pedestal`)
- Items: R26-283 (a push on a full-stage page keeps the title and the axes in frame - its reach from the page's measured boxes, as the tags already are), R26-281's engine half (the camera reads the DRAWN tags; row 1's re-aim is a P69 T36 item), R26-165 (`ken_burns(scale, deg, t0, t1)` - a window so a lean starts on a word), R26-164 (a layered plate's drift follows the camera's direction or is off - the shorts' plates; long form is Ken Burns alone, s84)
- Write set: `content/video_engine/scripts/kinetics/camera.mjs` (the push's reach), `content/video_engine/scripts/build_scene_timeline_f.py` (the ken tuple's window, `:5428` / `:7474`), `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`paintPlanes`' drift), tests: `content/video_engine/tests/kinetics/camera.test.mjs`, NEW `content/video_engine/tests/test_ken_window.py`
- Acceptance: (1) row 15's pull at 218.66 keeps the title's left edge, the y ticks and the source line in frame; (2) row 1's push is bounded by the drawn "+613%" tag; (3) a ken with a window starts on its word; a ken with none is byte-identical; (4) a layered short plate's planes move one way.
- Stop conditions: a committed camera key becomes unreachable (report the row for P69 T36; the author's key stands with a WARN).
- Regression: `python -m pytest -q content/video_engine/tests/test_ken_window.py`
- Expected RED: `ken_burns` with `t0, t1` refused as malformed (the tuple is `{scale, x, y}`); the push crops the title at 218.66.
- Validate: `python -m pytest -q content/video_engine/tests/test_ken_window.py` then COMMON-TAIL
- Frame acceptance: rows 1 and 15 at the push, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T26: A page's later states - their own scale, their own box, the axes that can leave, the named colour kept
- Status: pending
- Owner: implementation_luna (LANE B), then reviewer
- Depends on: P71 T3b, T13, T16, T28, T39 (`buildLedgerLine`, `lpAxisHandOver`); P70 T2
- Items: R26-266 (a per-state `domain` on `;then=`), R26-275 (the long-form layout takes the max over every state's y label, sub and tag room), R26-265 (a page token that recedes its axes and chrome so a record owns a clean ground without a world change), R26-277 (the long-form palette maps a named colour by a written table, or keeps it)
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs` (`lpPaintStates`' per-state scale and box, the axes-recede token, the long-form palette table), `content/video_engine/scripts/build_scene_timeline_f.py` / `ledger_page.py` (the state `domain` key and the recede token, refused by name when malformed), tests: NEW `content/video_engine/tests/test_page_later_states.py`
- Acceptance: (1) row 10's divergence lines fill their plot on their own state's range; (2) a bars -> line state draws the line in its own box, its y label clear of "+613%"; (3) row 11's records sit on a receded ground; (4) `ev-tnx-two-eras-v4`'s crimson draws crimson or the table names the remap; (5) pages without the keys are byte-identical.
- Stop conditions: a per-state scale reopens R26-261's unreadable middle (report to P71 T3b's owner).
- Regression: `python -m pytest -q content/video_engine/tests/test_page_later_states.py`
- Expected RED: `;then=` with a `domain` refused past `STATE_MAX`; the state's line in the bars box; the crimson series painted orange.
- Validate: `python -m pytest -q content/video_engine/tests/test_page_later_states.py` then COMMON-TAIL
- Frame acceptance: rows 10, 11, 15 at the states, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T27: The small engine rows - one commit each
- Status: pending
- Owner: junior_developer (LANE B), one row per commit; reviewer on R26-257 and R26-123 (a visible default)
- Depends on: each row's named neighbour (below); none waits on a P70 / P71 function except where named
- Items (each with its step (0) CONFIRM-OPEN):
  - R26-57 - `text-rendering: geometricPrecision` on the stage-space classes (`#species .lab`, `.chiplab`, `.flowtag`, `.vmstamp`, the chartbox tier; the template `:211` covers only `.lp text, .lp-chart text`);
  - R26-72 - the engine's `tierDomain` reads `shared_tier_domains` (E79's shared scale enforced);
  - R26-73 - the newsreel strip's 9:16 default follows E84 (measure first);
  - R26-142 - the agenda page's palette moves to the template's classes; the page form proven at 9:16;
  - R26-123 - the caption-life default is `blend` (E99 s6) when nothing is authored; approved cuts that author none keep their bytes only if they pin the setting - step (0) lists them, and a frozen cut is never re-rendered (E45);
  - R26-302 - the checklist takes a per-column `at` (after P69 T28b's `checklist.profile`, landed `b449e9f`);
  - R26-257 - the extruded prism's light re-derived from `DROP.LIGHT_DEG` (the parent's call recorded in the row); its goldens re-pinned with a frame read and the before / after to P72-HG1 item (3);
  - R26-2 - the harmonisation pass (light wrap + substrate grain) on a composited sprite, opt-in, one golden;
  - R26-171 - the compiler scales a badge rail on a 9:16 dock to the stage, never drops it (E99 s71 amendment in the row; the lab already does, `lab_build.py:1162`);
  - R26-106 - a DISCOVERY only: does any painter draw `prof.w`'s outline (`kinetics/stroke.mjs:58`)? If none, the finding is written and the build is filed as its own slice for the parent.
- Write set: the engine regions each row names, `docs/content-video-engine/samples/scene-evidence-player.template.html` (R26-57, R26-142 only), `content/video_engine/scripts/build_scene_timeline_f.py` (R26-123's default only), `content/video_engine/scripts/species/checklist.mjs` (R26-302), tests: one NEW test file per row (`test_small_engine_rows.py` with one test per row is acceptable)
- Acceptance: each row's own acceptance line in the inventory, one commit each, the H door identical except the listed instants (R26-257, R26-123).
- Stop conditions: a row's fix touches a function a P70 / P71 slice owns (stop; sequence).
- Regression: `python -m pytest -q content/video_engine/tests/test_small_engine_rows.py`
- Expected RED: one failing test per row (each predicted from the inventory's evidence line).
- Validate: `python -m pytest -q content/video_engine/tests/test_small_engine_rows.py` then COMMON-TAIL
- Frame acceptance: R26-257's extruded-bar goldens and R26-123's caption band, before / after.
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T28: Scripts that cost runs or say the wrong thing
- Status: pending
- Owner: implementation_luna (LANE B for the scripts; the H-door shim removal is a one-line lane-A edit after P69 T32)
- Depends on: T0; R26-197's H half after P69 T32 (lane A is writing `build_episode_h.py`)
- Items: R26-227 (`scratch_take.py` prints words / spoken seconds and the ask, exit 2 outside the band; the runner's report carries the measured wpm), R26-215 (`lint_species_choice.py --table` takes a bare name resolved in the project; the default follows the build), R26-197 (`recall_verify.resolve_ledger` accepts a build script's own docstring as the receipt's home; the shims in `tokyo-tea-break/build_short_v2.py` and `build_episode_h.py:3849-3851` removed), R26-198 (b) the gate CLI grows `--write`, (c) `--bind-cues` refuses a `--timeline` that is not the build's own), R26-178 (a whole-cut watch card carries its frozen player link with the audio, or the clip route takes `--audio`), R26-130 (a plate-library rebuild that loses a shipped record refuses by name; the sweep for uncovered approved plates), R26-183 (`self_watch.verdict_line` reads what `self_watch.py` writes - a round-trip test), R26-136 (3) (M13 enforced in `authoring/words.py` `cut_before` gets its registry row), R26-188's mirror (`sync_operator_memory.py --check` as a docs-layer step)
- Write set: `content/video_engine/scripts/scratch_take.py`, `run_script_gates.py`, `lint_species_choice.py`, `recall_verify.py`, `gate_motion_density.py` (`main`'s `--write` only - after T7), `authoring/audio.py`'s bind entry (after T20), `review_queue_proofs.py` or `build_review_queue.py`, `build_plate_library.py`, `self_watch.py`, `build_gates_registry.py`, `build_docs_layers.py` (the mirror step), their tests; lane A: `tokyo-tea-break/build_short_v2.py` and `build_episode_h.py` (the shim lines only)
- Acceptance: each item's owed line in the inventory; the two doors compile identically with the shim gone.
- Stop conditions: removing the H shim while lane A has `build_episode_h.py` open (wait).
- Regression: `python -m pytest -q content/video_engine/tests/test_recall_verify.py -k docstring`
- Expected RED: a build dir with no ledger and a docstring receipt is refused (the shim is what passes it today).
- Validate: `python -m pytest -q content/video_engine/tests/test_recall_verify.py content/video_engine/tests/test_lint_species_choice.py content/video_engine/tests/test_self_watch.py content/video_engine/tests/test_plate_library_layers.py content/video_engine/tests/test_landing_sound_follows_the_landing.py content/video_engine/tests/test_scratch_take.py content/video_engine/tests/test_build_plate_library.py` (the last two NEW in this slice) then `python content/video_engine/scripts/build_docs_layers.py --check`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T29: Citations resolve by row title, not by line
- Status: pending
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
- Status: pending
- Owner: implementation_luna (the Claude research-tooling lane; LANE B scripts)
- Depends on: T0 (decision 6 for R26-127)
- Items: R26-254 (1) (`ingest_stock_research.py` strips Drive ids / URLs, refuses offering documents - term sheet, PPM, subscription - by name, and FAILS a docket whose body is a search listing), R26-128 (the research profile never runs our layer regen; a tier-0 rule), R26-129 (the research ledger does not count the bridge transport as a run), R26-144 (the daemon's paths-written check follows a packet to `replied/`), R26-127 (a scheduler entry only on decision 6)
- Write set: `content/video_engine/scripts/ingest_stock_research.py`, the research profile file the lane reads, the research-ledger builder, the bridge daemon, their tests
- Acceptance: each item's owed line; a re-run of the ingester on a copy writes no Drive id and refuses the term sheet.
- Stop conditions: the ingester would read files outside the operator's named folder (never; it reads that folder only).
- Regression: `python -m pytest -q content/video_engine/tests/test_ingest_stock_research.py` (NEW, written first in this slice)
- Expected RED: a planted docket with a Drive search listing is written, not failed.
- Validate: `python -m pytest -q content/video_engine/tests/test_ingest_stock_research.py content/video_engine/tests/test_build_research_ledger.py` then the bridge daemon's tests (step (0) names them)
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence): pending
- Evidence: pending

### T32: The strobe's sharpness on real motion - a measurement
- Status: pending
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
- Frame acceptance: the sheet goes to P72-HG1 item (5).
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T36: The P69 hand-off - the H-row follow-ups the fixes make possible
- Status: pending
- Owner: parent (an edit to P69's T33 / T34 pass lists; the rows themselves are P69's)
- Depends on: the engine slice named per item
- Items: after T25 - row 1's push re-aimed (R26-281) and row 15's pull (R26-283); after T27 - row 20's `TEST_SWEEP_WHY` / `BODY_DEPARTURES` text (R26-302); after T22 - row 23's `VERDICT_STACK_ON = True`; after T20 - row 23's 0.8 s hand-off lead removed (R26-329); after T19 - row 23's second asset id retired (R26-328); after T28 - the H door's R26-197 shim removed (if not done in T28); after T14 - rows 7 / 12 / 13 / 17 declare their caption room
- Write set: `.claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md` (T33 / T34's lists), `docs/content-video-engine/BACKLOG.md` (the P69 umbrella's children)
- Acceptance: each item is on P69's pass list with the P72 slice and sha that enabled it; none is built here (the body is held for P69-HG3).
- Stop conditions: none.
- Validate: `python scripts/prp_validate.py .claude/PRPs/plans/P69-THE-STAMP-LANDS-THE-PAGE-BANDS-AND-THE-BODY.plan.md`
- Evidence: pending

### T37: The one-shot comparison - Fable's, then Opus's, then Astra's, on one loop
- Status: pending
- Owner: parent (Fable's one-shot and the read), implementation_luna (Opus's), Astra via the bridge (Astra's)
- Depends on: P71 T37 (its last wave merged) and T38 (P72's waves merged) - P71's stated successor, "the next one-shot test, measured against the 09-16 baseline"
- Items: R26-175 (E99 s66's order), R26-135 (4) (the calibration run: an agent other than Claude one-shots from the record), P54 T7 (the Astra-vs-Fable bake-off, one beat)
- Write set: three private build dirs under one short's project (the parent names the script), each with its receipt, its frozen copy, its critic; `docs/content-video-engine/review-queue.v1.json` (`p54-hg3-astra-fable-bakeoff` refreshed as the one card)
- Acceptance: three cuts from one script on `docs/runbooks/ONE-SHOT.md`'s loop, compared on M35-M46, the motion gate and the parent's read beside the approved cuts, served frozen with the voice (R26-178's link); the card asks the one question the plan names.
- Stop conditions: a lane's cut needs an engine change (it files a row; the comparison runs on the engine as it is).
- Regression: `python content/video_engine/scripts/gate_one_shot_floor.py <each build> --project <project> --reference <the approved reference>`
- Expected RED: no one-shot built since 09-16 on today's engine.
- Validate: `python content/video_engine/scripts/gate_one_shot_floor.py <each build> --project <project> --reference <reference>` then `python content/video_engine/scripts/build_review_queue.py`
- TDD reserved (Red evidence, Failure attribution, Unrelated failures, Green evidence, Refactor evidence, Frame read): pending
- Evidence: pending

### T38: Integration and merge - per wave, the registries unioned, the generated files regenerated, CAPABILITIES, one commit per slice
- Status: pending
- Owner: parent; release_steward commits (explicit paths, never `git add -A`, never a push without the operator's current word)
- Depends on: each slice's review
- Write set: the slices' patches; `docs/content-video-engine/CAPABILITIES.md`; the cards / recipes; the generated files (`docs/EFFECTS-CATALOG.*`, `page-boxes.v1.json`, `SPECIES-BY-SENTENCE.md`, the docs layers) regenerated by the parent; the goldens re-pinned once per wave with a sha table; `docs/WORKTREE-REGISTER.md`; this plan's evidence; the archive rows for each merged item (T0's format)
- Acceptance: per wave - `git apply --check` clean in the listed order; the whole suite on lane B run unpiped before and after, the diff of failures empty or each new one a named row; the H door identical except the listed instants; the "Before anything reaches main" checklist for any merge to main.
- Validate: `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py -q` then `python content/video_engine/scripts/effects_catalog_check.py` then `python content/video_engine/scripts/build_docs_layers.py --check` then `python scripts/prp_validate.py .claude/PRPs/plans/P72-THE-BACKLOG-BURNDOWN.plan.md`
- Evidence: pending

### T39: P72-HG1 - the closing gate sheet
- Status: pending
- Owner: parent; the operator rules
- Depends on: T38 (the last wave), T10, T11, T23, T27 (R26-257), T35
- Write set: `$SP/p72-t39/` (the sheet, frozen, on its own port), `docs/content-video-engine/review-queue.v1.json` (the row T0 framed, now `where` filled), this plan
- Acceptance: the seven items of the Human Gates table's P72-HG1 row, each with its frames beside the reference, served frozen; the burndown table (every INVENTORY id and its final state) attached; the operator's answers written to `OPERATOR-RULINGS.md` and here.
- Validate: `python content/video_engine/scripts/build_review_queue.py` then `python $SP/p72-t0/coverage.py`
- Evidence: pending

## Verification

- Per slice: its Regression RED first, then its Validate chain unpiped (`never pipe a gated step into tail`, E99 s11), then COMMON-TAIL for every engine / gate slice, then the door identity (or the listed instants for a FIX).
- Per wave (T38): the whole lane-B suite before and after, the failure diff; `sync_kinetics.py --check`; the goldens; `effects_catalog_check.py`; `build_docs_layers.py --check` (green from T1 on).
- At the end: `python $SP/p72-t0/coverage.py` prints an empty unmapped set; `python scripts/prp_status.py` shows P72's slices done except T39's operator answers; `BACKLOG.md`'s active queue carries only umbrella, OTHER-LANE and gate rows.

## Evidence And Handoff

- Planning evidence: `$SP/p72-plan/INVENTORY.md` (the verdicts), `row-evidence.txt` (per-row commit and plan hits), `gitlog-all.txt` (1,608 commits across every branch), `open-rows.txt`, `open-rows-full.txt`, `legacy-rows.txt`, `plan-slices.txt`.
- Heads read: lane A `8f233a1`, lane B `e43c3d8`, main `013128e`.
- Probes run for this draft (read-only): `build_capabilities_index.py --check` (FAIL, NEW-1), `pytest test_worktree_register.py` (1 failed, NEW-3), `pytest test_lab_log.py` (2 failed, R26-244), `effects_catalog_check.py` (0 failures, 50 recipes, 15 proven).
- The parent owns: the approval, T0's decisions, every brief, every frame read, the registry unions, the merges, the gate, and the operator.
- Deviations: none yet.
