---
id: P68-STEEL-AND-PAPER-H
title: Steel and Paper H - the long-form shakedown on today's engine
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-18
updated: 2026-09-18 (approved with E99 s81)
---

# Steel and Paper H - the long-form shakedown on today's engine

## Summary

The channel is going back to long form. The decision is the operator's and is not re-opened
here: the first long form on today's engine is a **rebuild of Steel and Paper** (ep1, the
only shipped long form) as **Script H plus a shot table authored NEW**. The operator's
framing - *"the real question is will rebuilding it help you more than a fresh video"* - is
answered by the rebuild, because it is the only cut where the engine is the **only**
variable: `build-f/` lets every frame be read beside a reference at the same instant, the
evidence is verified (`REWRITE-ORDER-H.md` "The evidence holds"; every live figure
re-verified by the operator 2026-09-08), and the fault list is measured, not remembered. The
next long form is a fresh topic where the story is the only variable; that is out of this
plan.

**The operator's correction this plan discharges:** *"i had told you to build to be able to
run either long form or short form. sounds like that didn't happen."* The truth: the
authoring kit **is** one door for both formats and is WIRED
(`docs/content-video-engine/CAPABILITIES.md:90` - "one door for both formats ... the next
long's door is the kit itself"), and the per-format dials were ruled (E99 s55
`docs/portable/OPERATOR-RULINGS.md:3228`, s64 `:3246`, s65 `:3248` - 20 px drift is long
form, 30-40 is shorts). But **no long-form build has ever run through it**: every mechanism
since 2026-09-05 was proven at 9:16 in ~89 s cuts; ep1's own door
(`steel-and-paper/build_scene_evidence_cut.py:10`) still hardcodes a worktree path and
imports nothing from the kit; and `build-f/GATES-MOTION.md` reads **`ledger_pages: 0`** - the
E61 default (`OPERATOR-RULINGS.md:1991`; doc 29 s9.33 at
`docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md:2217`) that a long form is
authored on the ledger page has never run in a long form at all. This plan is that proof.
**Every engine gap it finds is a backlog row with an owner, never a workaround in the build
script.**

**Measured today (2026-09-18, in memory, nothing written):** the on-disk `SCRIPT-H-GATES.md`
(2026-09-08: "runtime 7:26", 2 FAIL / 2 WARN / 42 PASS) **does not reproduce on today's
code**. `gate_opening_structure.run` on `SCRIPT-H-VO.txt` gives **13:19 estimated, 7 FAIL**
(G40, G20, G21, G41, G27, G36, G44) and, handed `build-f/timeline.json`, **12:56 "measured",
7 FAIL** (G02, G09, G21, G41, G27, G36, G44). So: **G46 / E74's 8:00 floor is not at risk**
(`OPERATOR-RULINGS.md:2393`, `docs/GATES-REGISTRY.md:75`) - the 7:26 was an artifact;
**G15b now passes**; and the open fault set is the P2 geometry rows plus the late-body rows
the rewrite order already named. Two consequences: (1) the stale report is re-derived before
anything is judged from it; (2) **the phase geometry scales with runtime**
(`gate_opening_structure.py:650`), so H's true verdict settles only on H's **own** take -
T1 lands it clean on the estimate, T2's record re-runs it, and a second short prose pass may
be owed.

## Intent And Acceptance

1. **The script.** `SCRIPT-H-VO.txt` runs `run_script_gates.py` with **0 FAIL**, the WARNs
   judged in writing, the blind viewer (P36) run and folded, the runtime over 8:00 with
   substance (E74), and the package re-locked (E27 `OPERATOR-RULINGS.md:810`, plus the
   1:30-unit addendum `:868`). HG1.
2. **The record.** An H take exists with word timings on the build clock, the VO tone chain
   G verified (E99 s54 `:3226`), the whisper gate clean, the chain written down stage by
   stage as `RECORD-CHAIN-G.md` does. HG2 (paid audio).
3. **The either-format proof.** A table on disk naming every mechanism the shorts proved, its
   16:9 / long-form path (or the absence of one), and the gates that apply to a long form
   versus the ones that bind shorts only - with every gap filed as a backlog row.
4. **The treatment.** `REBUILD-TREATMENT-H.md`: row by row off `build-f`'s table, each row
   cited to the record, **every plate's use named** (E61: landing surface / bridge / reset),
   every held thing's idle (E49 `:1494`), the camera only where the sentence names the thing
   (E99 s76 `:3270`), the chart-to-chart moves (E58 `:1854`), and every cut or dip counted
   with **the transform it refused named** (E99 s74 `:3266`). A rebuild is judged on a NEW
   plan carrying today's doctrine, never the old table dressed up (E99 s72 `:3262`).
5. **The 1:30 unit of proof built first**, read on frames beside `build-f` at the same
   instants, served as a frozen copy, critic written. HG3.
6. **The whole cut**: body, outro, cues bound before the gate report (R26-198), gates,
   critic, frozen copy, the parent's read. HG4, with the render.
7. **The render** from the frozen copy at 24 fps (E99 s36 `:3172`) and a queue card. The
   post and the publication route are the operator's.

**Not acceptance:** the retention curve. That is the real verdict and it arrives after the
upload; this plan ends at a rendered file plus a card.

## Scope

- **In:** `content/video_engine/projects/systems-and-blowups/steel-and-paper/` (the H script
  and its reports, the H record chain, the treatment, the new door `build_episode_h.py`,
  `build-h*/`), the capability audit under `docs/research/`, backlog rows in
  `docs/content-video-engine/BACKLOG.md`, this plan.
- **Out, READ ONLY:** `build-f/`, `SHOT-TABLE-F.py`, `build_scene_evidence_cut.py`,
  `SCRIPT-G-*`, `vo-f/`, `RECORD-CHAIN-G.md` - the reference the frames are read against
  (the Tokyo v3 pattern: the approved build is never touched by its rebuild).
- **Engine code** (`content/video_engine/scripts/**`, `authoring/`, the player template, the
  species) is outside every slice's write set. A gap there is a backlog row and, if it
  blocks, its own PRP.
- **The parent's alone:** `docs/content-video-engine/REVIEW-QUEUE.md` /
  `review-queue.v1.json`, `docs/portable/OPERATOR-RULINGS.md`, the backlog rows, every
  integration and every completion claim.

## Not Building

- No new engine mechanism, no new species, no dial change. If the cut wants one: a row.
- No images, mp3, mp4 or `player.html` into git. Approved stills leave quarantine; build
  outputs stay in the worktree that made them (E99 s73 Apply 4(k), `:3264`).
- No rebuild under the operator: a served build is a **frozen copy** and is never rebuilt
  while its link is live (E99 s75 / R26-193).
- Nothing reaches the queue the parent has not read on frames **beside the reference at the
  same instants**; a whole-cut watch owes a critic path (`build_review_queue.py` refuses).
- A collision is **fixed** before a card, never named in a note (R26-191).
- No paid generators (E99 s37). No figure invented - every number keeps the sidecar it came
  from; a time anchor is dated, never "right now" (`REWRITE-ORDER-H.md` item 9; G48 already
  WARNs 14 publication-relative anchors in H).
- No piecemeal patching of a script that needs several edits - the next letter. H is the
  letter; the recorded G stays as recorded.
- No push, no upload, no unlisting. Push only on the operator's current word.
- Delegated roles run on Opus 5; judgement, integration and protected actions stay parent.

## Human Gates

The parent writes each row into `docs/content-video-engine/REVIEW-QUEUE.md` in the same
change that frames the gate; the ruling lands in `OPERATOR-RULINGS.md` and back here.

- **HG1 - the script and the re-locked package.** The operator reads `SCRIPT-H-VO.txt`
  gate-clean, plus the package as one object: title, thumbnail, sentence 1 (E27 `:810`; E24
  G45 / J12 `:743`). RULED 2026-09-18 (E99 s81): the post is Facebook first and probably a YouTube re-upload; the host is
  IN - Mike's studio and newsroom windows are Flow character stills (character + image prompt) on the
  table as named plate uses. HG1 is the script and the package only. Blocks T2 and T4.
- **HG2 - STRUCK (E99 s81).** No paid take. T2 is a local Kokoro scratch take at rate 1.06 (~175 wpm) for
  the build clock; the voice is auditioned on the 1:30 unit at HG3 ("a few different voice recordings on
  the 1:30"), and a Chirp take is a candidate for the Facebook file (E70: Facebook is the Chirp lane).
- **HG3 - the 1:30 unit of proof, and the voice.** The first 1:30 of the cut on its own port as a frozen
  copy, with the voice takes auditioned on it (E99 s81), with the contact sheets beside `build-f`'s same instants and the critic report (E27
  addendum `:868`: the 1:30 is the deliverable that earns the rest). Blocks T6.
- **HG4 - the whole-cut watch, with the render.** The full cut frozen and served, gates clean
  or each remaining FAIL named with the ruling that allows it, the critic's two fractions,
  and the 09-18 doctrine rows counted (idle tokens, the camera on named things, the plate
  uses, cuts and dips with their refused transform). Blocks the upload, which is the
  operator's.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` "Dispatch mapping" (line 46) and "PRP Format" (192);
  `AGENTS.md` section 9. `docs/runbooks/ONE-SHOT.md` for the build checklist (grown by E99
  s79 Apply 5). `docs/runbooks/RECALL-RECEIPT.md` - every proposal opens with `Recall:` lines.
- The project: `REWRITE-ORDER-H.md` in full (the script half of this order),
  `SCRIPT-H-GATES.md` (**stale - re-derive**), `SCRIPT-H-JUDGE.md`, `SCRIPT-H-SCREENS.md`,
  `SCRIPT-NOTES-retention-2-46.md` (the 2:46-3:23 sputter and how that unit should read),
  `SCRIPT-G-LEDGER.md` (the three ring tokens, the foreshadow table), `RECORD-CHAIN-G.md`
  (eight stages, the tool for each).
- The reference: `build-f/timeline.json` and `build-f/steel-and-paper.timeline.json`
  (806.5 s - the real clock; `motion-plan.json` and `evidence-dock.json` are a 723 s base and
  are STALE per `REWRITE-ORDER-H.md`), `SHOT-TABLE-F.md` (75 windows),
  `build-f/CHOREOGRAPHY.md`, `build-f/FIRST-MINUTE-MEASUREMENT.md`, `build-f/GATES-MOTION.md`
  (8 FAIL today; `ledger_pages: 0`), `build-f/SURFACE-CENSUS.md` (the DEFECT rows),
  `build-f/TOPIC-EXIT-AUDIT.md`.
- The doctrine, by line: E21 `OPERATOR-RULINGS.md:557` (with doc 29 s9.25 at
  `29-EVIDENCE-MOTION-STANDARDS.md:1430` - ep1 shipped 23% of runtime still and its opening
  minute was the thinnest), E24 `:743`, E25 `:761`, E27 `:810` and the 1:30 addendum `:868`,
  E49 `:1494`, E58 `:1854`, E59 `:1903`, E60 `:1959`, E61 `:1991`, E73 `:2342`, E74 `:2393`,
  E99 s36 `:3172`, s54 `:3226`, s55 `:3228`, s64 `:3246`, s65 `:3248`, s72 `:3262`,
  s73 `:3264`, s74 `:3266`, s76 `:3270`, s78 `:3274`, s79 `:3276`, s80 `:3278`.
- The backlog rows that touch a long-form build: R26-17 (`BACKLOG.md:514` - the kit is the
  next long's door, step 0 done), R26-190, R26-191, R26-192, R26-194, R26-197, R26-198,
  R26-201, R26-202, R26-181 (the receipt and the critic).

### Recall (docs_find, run 2026-09-18 before any mechanism is named)

- `Recall: docs_find "outro" -> docs/content-video-engine/CAPABILITIES.md:63` - the Remotion
  kit outro (`outro-v2` dark, `outro-brand` cream, `outro-yt`), dissolved in as the last word
  ends, the recorded brand line stitched 0.7 s after it. **Path correction:** the asset is
  `content/video_engine/channel-assets/money-physics/outro/BRAND-LINE.txt` plus `vo/`, not
  `channel-assets/...`; `gate_opening_structure.py:121` matches the line's words.
- `Recall: docs_find "caption strip 16:9" -> 0 hits` across capabilities, assets, effects,
  manifest, index, topics, gates, animation, craft. **There is no 16:9 caption-strip
  capability row.** What exists: PHRASE captions are titled **(shorts)**
  (`CAPABILITIES.md:66`), and ep1's own captions are word-level pages
  (`build-f/caption-pages.json`; `GATES-MOTION.md` M06 = 464 pages, 35/min). This is T3's
  first gap, and R26-201's engine order (the caption yields under a camera key) lands on it.
- `Recall: docs_find "species-by-sentence" -> 29-EVIDENCE-MOTION-STANDARDS.md:2217` (s9.33,
  the chart is the WORLD) and `content/video_engine/scripts/lint_species_choice.py` (`--long`
  lists every plate row with its `;use=` and WARNs one without - E61).
- `Recall: docs_find "camera" -> CAPABILITIES.md:85` one persistent 2D similarity per timeline
  (`kinetics/camera.mjs`), `:84` the camera arrival, `:124` a pointing species carries a
  DECLARED target, `:149` the camera over layers.
- `Recall: docs_find "long form" -> CAPABILITIES.md:201` (G2 short mode: a measured clock
  under 3:00 routes the opening gate to the shorts shape, so the long-form shape is the
  default and `--long` forces it) and `:71` the idle, WIRED.
- `Recall: effects_card "recipe:outro-clip-life"` - the close: the outro clip is the world and
  its declared life carries the motion (with `...-still`, the refusal stated).
- `Recall: sigmap "long form rebuild shot table steel and paper" -> SHOT-TABLE-F.md` (rank 1)
  and `build-f/SURFACE-CENSUS.md` (rank 2, its own "DEFECT rows" heading) - the two documents
  the treatment is cut from.

## Execution Path

Serial by dependency, one variable at a time:

**T1 script (parent) -> HG1 -> T2 record (parent, HG2 first) -> T4 treatment (parent) ->
T5 the 1:30 unit -> HG3 -> T6 the body and the whole cut -> HG4 -> T7 render and card.**
**T3** (the capability audit) and **T3b** (its rows) run beside T1, because T3's write set is
disjoint from every other slice's.

T1 and T2 both touch `SCRIPT-H-GATES.md` and are therefore **never dispatched together**.
T5 and T6 share `build_episode_h.py` and run in order.

The way a cut is made now (E99 s78 Apply 3 `:3274`, s79 Apply 5 `:3276`) is the spine of
T4-T7 and is not re-invented: a treatment row by row with its cites -> a build script
**beside** the approved one, each change a named constant with its receipt in the module
docstring (R26-197) -> a build into a private dir -> cues bound, **then** the gate report
stamped (R26-198) -> probe and contact sheets read by the parent beside the reference at the
same instants -> a FROZEN copy served on its own port -> the critic -> the render -> the card.

## Patterns To Mirror

- **The whole method:**
  `content/video_engine/projects/systems-and-blowups/tokyo-tea-break/REBUILD-TREATMENT-V2.md`
  (the Recall block, then one table row per approved row -> its rebuild -> the record that
  binds it, then the flow count) and `tokyo-tea-break/build_short_v3.py` (the docstring
  receipt with one named constant per change, the `recall_verify.resolve_ledger` shim -
  R26-197, the approved module imported but never called, every write outside the build dir
  redirected or asserted), with `tokyo-tea-break/build-v3/` as the output shape.
- **The door:** `content/video_engine/scripts/authoring/` (`Project`, `words`, `docks`,
  `audio`, `table`) - R26-17 step 0, `CAPABILITIES.md:90`. Nothing in the package names an
  episode: every fact, crop, quote and level stays in `build_episode_h.py`. The F door is
  legacy and is not extended.
- **The record chain:** `RECORD-CHAIN-G.md`'s eight-stage table, tool by tool, status by
  status - H's own copy is written the same way.
- **The receipt and the critic:** `content/video_engine/scripts/recall_verify.py` (the nine
  `Recall(<stage>):` stages, verbatim spans, zero-hit re-runs) and
  `docs/content-video-engine/CRITIC-REPORT.md` (two tables, two fractions, never a verdict) -
  R26-181.
- **The self-watch bar:** `content/video_engine/scripts/self_watch.py` (on a long it grabs the
  opening **3:00** as contact sheets at 2 s steps; section 2's eleven O-rows are read by the
  agent, and CLEAN is a word written only after the read).

## Task Slices

### T1: Script H to gate-clean, and the package re-locked
- Status: complete
- Owner: parent
- Route: parent - the writing is the parent's (E99 s72 and the gate-fit lesson both make
  prose-under-a-gate a judgement slice); `docs_researcher` may be dispatched read-only for a
  craft precedent
- Depends on: none
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-H-VO.txt`, `.../SCRIPT-H-GATES.md`, `.../SCRIPT-H-SCREENS.md`, `.../SCRIPT-H-JUDGE.md`, `.../SCRIPT-H-VIEWER.md`, `.../SCRIPT-H-VIEWER-WINDOWS.json`, `.../SCRIPT-H-VIEWER-REPORTS.json`, `.../REWRITE-ORDER-H.md` (its status line only), `.../packaging/TITLE-CANDIDATES.md`
- Acceptance: the runner exits 0 with **0 FAIL**; the faults measured today are closed - G40
  (a `[catalyst]` inside the phase's first 60 s), G20 (the 53 s new-info gap), G21 (P2's loop
  count against the scaled geometry), G41 (`[debate]` after the head-fake), G27 (the ring
  token `certificate` touched **exactly once** in P2 - it reads 2x), G36 (the 141 s cycle gap
  from 8:48), G44 (no rehook in the last unit window); G02 is an **edit-clock** property and
  is closed by T2's build, never in prose; each WARN carries a written judgement in
  `SCRIPT-H-JUDGE.md` (G31 0 dabs for 2 loops, G43 1/8 beats on a gap connector, G48's 14
  publication-relative anchors); runtime clears 8:00 (G46) **with substance**, no padding
  (E74); the blind viewer runs (`viewer_windows.py` -> `viewer_run.py` -> `viewer_score.py`)
  and its unperceived beats are folded, its verdict quoted where the report says NOT RUN; the
  package is one object - title, thumbnail, sentence 1 - and J12 is verdicted by hand against
  the file the runner prints
- Validate: `python content/video_engine/scripts/run_script_gates.py content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-H-VO.txt --ring certificate --counterparty "Bravos Research" --title "<the locked title>" --thumb-file content/video_engine/projects/systems-and-blowups/steel-and-paper/packaging/<the locked thumb>.png --long`
- Evidence: 6e78106 (the pass), then the viewer rounds and the final take in wave 4: `SCRIPT-H-GATES.md` VERDICT PASS on `vo-h-scratch/timeline.json` (13:58; the promise at 0:44; 0 FAIL / 3 WARN / 47 PASS; the VIEWER line advisory), `SCRIPT-H-JUDGE.md` (the R2 table, the WARNs, the twelve JUDGE rows, the four viewer reads 79 -> 87 % with each miss judged), `SCRIPT-H-VIEWER.md`; HG1 open on the queue as `p68-steel-and-paper-h-hg1`

### T2: The H scratch record - the Kokoro take at ~175 wpm, the words, the clock (E99 s81)
- Status: complete (the scratch clock; the voice itself is HG3's)
- Owner: parent
- Route: parent for the spend and the join listen; `junior_developer` for the mechanical
  stages (whisper gate, word timeline, edit pauses) once the audio exists
- Depends on: none for the scratch clock (the take on the script AS IS runs first, the operator's word 2026-09-18); T1 + HG1 for the take the cut is built on
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/RECORD-CHAIN-H.md`, `.../vo-h/**`, `.../SCRIPT-H-EDIT-PAUSES.json`, `.../SCRIPT-H-GATES.md` (the re-run on the take's clock), `.../build-h/timeline.json`
- Acceptance: `RECORD-CHAIN-G.md`'s chain walked for H and written down stage by stage - the
  freeze (narration figures read against the frozen sidecars), `record_chained_take.py`
  chained at a phase boundary (H is over the 10,000-char mv2 cap),
  `verify_take_whisper.py` clean (no insertions, no deletions, WER <= 5%),
  `build_timeline_f.py` for the word timeline, `insert_edit_pauses.py` for the owed silences,
  the VO tone **chain G** applied with `master_vo_tone.py --verify` green (E99 s54); the
  opening gate re-run with H's **own** `--timeline` and every geometry row re-read on the real
  clock (a second short prose pass is allowed and stays in T1's write set); G02's 0.5-0.8 s
  breath exists in the edit clock
- Validate: `python content/video_engine/scripts/verify_take_whisper.py content/video_engine/projects/systems-and-blowups/steel-and-paper --take vo-h` then `python content/video_engine/scripts/master_vo_tone.py --verify` then `python content/video_engine/scripts/run_script_gates.py content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-H-VO.txt --ring certificate --counterparty "Bravos Research" --timeline content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h/timeline.json --long`
- Evidence: `vo-h-scratch/` (Kokoro am_michael at rate 1.075 - `scratch_take.py --rate` reaches Kokoro since 6e78106; 13:58; words.json + timeline.json + SCRATCH-INDEX.md; the mp3 gitignored); the tone chain and the whisper gate are owed on the CHOSEN voice after HG3, not on a scratch

### T3: The long-form capability audit - the either-format proof, BEFORE the table
- Status: complete
- Owner: junior_developer
- Route: `junior_developer` on Opus writes the audit and the table; `explorer` is read-only by
  the dispatch mapping (`PRP_EXECUTION.md:69`) and cannot land the file, so it is dispatched
  first only if the parent wants a deeper recall pass, with the same acceptance
- Depends on: none (runs beside T1)
- Write set: `docs/research/LONG-FORM-CAPABILITY-AUDIT-2026-09-18.md`
- Acceptance: one table, one row per mechanism the shorts proved (`CAPABILITIES.md` LIVE and
  WIRED rows, `docs/EFFECTS-CATALOG.jsonl` proven recipes,
  `effects/skeletons/approved-mix.json`), each row carrying the mechanism, where it is built
  (`path:line`), **whether it has a 16:9 / long-form path**, the dial per format with its
  ruling (E99 s55 / s64 / s65 - 20 px long form, 30-40 shorts), and the evidence for the
  answer (a cut that used it at 16:9, or none). Plus four sections, each a verdict rather than
  a survey - (a) **the caption layer**: PHRASE captions are titled "(shorts)"
  (`CAPABILITIES.md:66`), ep1 shipped word-level pages (`build-f/caption-pages.json`, M06
  35/min), `docs_find "caption strip 16:9"` returns 0 hits - say what a 16:9 strip **is**
  today and what R26-201's engine order (the caption yields under a camera key) costs a 16:9
  page punch; (b) **the gates**: which bind a long form and which bind shorts only, cited from
  `docs/GATES-REGISTRY.md` and from the tools' own words (`build-f/GATES-MOTION.md` M16 - "a
  long-form build; the pulse law binds shorts"; `gate_vertical_safe_box.py` is 9:16;
  `gate_one_shot_floor.py` M35-M46 reads a **reference build** whose only approved instances
  are shorts, and ep1's own build is PREDATES_E96 - say what M37 / M39 / M40 / M46 mean in
  that state); (c) **the camera and the outro at 16:9**: `CAPABILITIES.md:84`, `:85`, `:124`,
  `:149`, and the outro dissolve plus brand-line stitch (`:63`) as `build_short.py` does it,
  and what changes for a 13-minute cut; (d) **the door**: what `authoring/` covers for a long
  form and what ep1's legacy door (`build_scene_evidence_cut.py`) does that the kit has no
  function for. Every gap ends as a proposed backlog row **with an owner and a blocking
  verdict** (blocks T4 / blocks T6 / informational), listed at the foot of the file ready to
  paste. No engine file is touched
- Validate: `python content/video_engine/scripts/docs_find.py "caption strip 16:9"` and `python content/video_engine/scripts/lint_species_choice.py content/video_engine/projects/systems-and-blowups/steel-and-paper --build build-f --long` - both outputs quoted verbatim in the audit, and every `path:line` in the table re-opened by the parent before acceptance
- Evidence: 3a9d82e: `docs/research/LONG-FORM-CAPABILITY-AUDIT-2026-09-18.md` - 82 rows (12 CUT / 45 GOLDEN / 25 NONE at 16:9), five verdict sections, thirteen gaps

### T3b: The gaps filed as backlog rows
- Status: complete
- Owner: parent
- Route: parent - `BACKLOG.md` is a shared integration point, and two agents in it corrupt it
- Depends on: T3
- Write set: `docs/content-video-engine/BACKLOG.md`
- Acceptance: every gap T3 proposes becomes a row with its id, the measurement that found it,
  the owed work, an owner and a status; the rows this plan already knows are filed with them -
  the 16:9 caption strip has no capability row; the opening gate accepts a `--timeline` from a
  **different** script and prints its clock as "measured"
  (`gate_opening_structure.py:288-307` maps sentences onto the other take's words
  positionally - the defect that produced the stale 7:26 and a false G09 read); the one-shot
  floor has no long-form reference; R26-201's caption-under-a-camera-key order is re-scoped to
  16:9 pages
- Validate: `python scripts/prp_status.py` and `git diff --stat docs/content-video-engine/BACKLOG.md`
- Evidence: 3a9d82e: BACKLOG R26-205..R26-217 (audit G-01..G-13), R26-204 the pointer; R26-210 BUILT in wave 4 (the 16:9 outro)

### T4: REBUILD-TREATMENT-H.md - the new shot table, row by row, with its cites
- Status: pending
- Owner: parent
- Route: parent - this is the architecture of the cut, and E99 s72 makes a rebuild's treatment
  the thing the operator's judgement lands on
- Depends on: T1, T3, HG1
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/REBUILD-TREATMENT-H.md`
- Acceptance: a Recall block first (the nine stages `recall_verify.py` names, each a
  `path:line` with a verbatim span), then one table row per beat - `build-f`'s row (its window
  on the **806.5 s** clock, its plate, its dock, its narration) -> H's row -> the record that
  binds it. Every row satisfies, explicitly: **the world** - the ledger page by default (E61;
  `build-f` has `ledger_pages: 0`), the chart-to-chart family carrying the scenes (E58), the
  axes open where the hook allows it (E73); **the plate** - one of landing surface / bridge /
  reset, named on the row (E61; the lint WARNs an unnamed one), and no plate short enough to
  flash (R26-192); **the life** - an idle token on every held thing, `idle=live` on every page
  and `idle=drift` on every plate, Ken Burns plus the 20 px directional drift on a flat plate
  (E49, E99 s65, s79), with the idle-token **count** written in the treatment; **the camera** -
  only where the sentence names the thing (s76), one move per window (M09 / M14), a crop line
  between elements and never through a glyph (s80); **the evidence** - a chart proves one
  sentence and leaves, the 6 s opening hold ceiling (E25; `build-f` held 30 of 43 docks past
  it, 40.9 s at 0:09.5), a second card takes the outgoing card's slot rather than making the
  chart stand aside (s80), a light only with a callout (s76 / R26-194); **the flow** - every
  cut and dip counted, each naming **the transform it refused** (s74), the dip only at a real
  world change (E47). Plus a fault ledger: each of `build-f`'s measured defects (6 stretches
  over 12 s = 94 s; the 54 s evidence wait from 2:52; the opening minute at 35.0 events/min
  against a 46.5 median; the 2:46-3:23 sputter per `SCRIPT-NOTES-retention-2-46.md`; the
  promise at 1:16) with the H row that closes it. The host's windows are reserved or refused
  per HG1's ruling. Nothing is built until the treatment is complete
- Validate: `python content/video_engine/scripts/docs_find.py "<each mechanism the treatment names>"` with the hits quoted in the Recall block, then `python scripts/prp_validate.py .claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md`
- Evidence: pending

### T5: The first 1:30 built - the unit of proof
- Status: complete (the unit built and read; HG3 owed the critic and the card)
- Owner: implementation_luna
- Route: `implementation_luna` on Opus builds to the treatment; the parent reads the frames and
  owns the frozen copy, the link and the critic
- Depends on: T2, T4
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**` (gitignored build output), `.../CRITIC-REPORT-H.md`
- Acceptance: the door is **new and beside the old one** - `build_episode_h.py` through
  `authoring/` (R26-17 step 0), never an edit to `build_scene_evidence_cut.py`, with its
  `## Recall` receipt in the module docstring and every change a **named constant** whose cite
  sits in that docstring (R26-197); `build-f/`, `SHOT-TABLE-F.py` and `vo-f/` asserted
  read-only by the script itself; the first 1:30 compiles and the cues are bound **before**
  `gate_motion_density.write_report` stamps the report (R26-198); the opening 3:00 contact
  sheets exist (`self_watch.py`) and the parent has read H's tiles **beside `build-f`'s at the
  same instants** - the E21 rows in particular (the opening minute is the densest, not the
  thinnest; no still stretch over 6 s in the first 60 s, where `build-f` has three);
  `measure_frozen_frames.py` finds no freeze over 0.5 s (E49 / M18, unmeasured in `build-f`);
  `lint_species_choice.py --long` names a use on every plate row; a **frozen copy**
  (`build-h-frozen-a/`) is served on its own port - not :8731, which `render_episode.py` names
  by default - and is never rebuilt while the link is live; `CRITIC-REPORT-H.md` carries its
  two tables and two fractions, including the three 09-18 rows (idle tokens counted, the camera
  on named things, the open on the axes)
- Validate: `python content/video_engine/scripts/self_watch.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h --project content/video_engine/projects/systems-and-blowups/steel-and-paper --script SCRIPT-H` - section 3 reads CLEAN only after the parent's read of the sheets
- Evidence: `build_episode_h.py` (the door through `authoring/`, receipt PASS 12/9), `SHOT-TABLE-H.md`, `build-h/` (gitignored; `GATES-MOTION.md` 1 FAIL M34 the recast's own hand-over + M11 by name / 3 WARN; frozen frames none over 0.5 s; every plate names its use; `self-watch/opening.1-4.png`), `build-h/BUILD-NOTES-H.md` (ten departures), `PARENT-READ-H.md` (two passes beside build-f), the frozen copy `build-h-frozen-a/` on :8775; BACKLOG R26-218..221 (the engine doors the unit found missing)

### T5b: The engine doors the unit found missing, built before the body (parent's amendment 2026-09-18)
- Status: running
- Owner: parent
- Route: `implementation_luna` per pair of rows, each with a test, the source and the mirrored kinetics module edited together (`test_kinetics_sync`), reviewed before integration; the parent files the rows and orders them by what the body hits first
- Depends on: T5
- Write set: `docs/content-video-engine/samples/scene-evidence-engine.mjs`, `content/video_engine/scripts/kinetics/**`, `content/video_engine/scripts/species/**`, `content/video_engine/scripts/build_scene_timeline_f.py`, `content/video_engine/tests/**` (new tests only), `docs/content-video-engine/BACKLOG.md` (the rows' status)
- Acceptance: R26-218 (a mark names its series on a multi-line page) and R26-219 (page-bound species retract with the page at a `chart_to` unless `keep`) proven by tests with the existing suites green; then R26-221 (a card takes an authored box on a picture plate), R26-223 (a page born with a domain), R26-222 (M28 ignores a label paired with its identical copy), R26-205 (the 16:9 caption geometry - the largest, its own card) in the order the body's rows need them. The plan's "engine code is outside every slice" stands for T5-T7's build scripts: the doors are built as engine work with tests, never as workarounds in `build_episode_h.py`
- Validate: `python -m pytest content/video_engine/tests -q -x` and the node kinetics tests, tails to a file, never piped
- Evidence: R26-218 and R26-219 BUILT (wave 6): `scene-evidence-engine.mjs` (lpSeriesRange :8970, the figure's `sp.series ?? sp.tier ?? target.series` :10871, pageLeave :11056), `build_scene_timeline_f.py` (`_validate_target` bound :730, `check_target_series` :964, `stamp_page_leave` + `page_species_end` clamping `dur` :882-:944, wired :5335), `CAPABILITIES.md:74` (the leave and `keep`), tests `test_datum_names_its_series.py` (23) + `test_page_species_leave.py` (23), the note `tests/R26-218-219-NOTE.md` (33 spans verified); reviewed by `reviewer` (three findings, all applied); four-suite 287 passed, node 629/629, goldens byte-identical, the whole suite's 15 pre-existing failures unchanged (R26-224). Owed next: R26-221, R26-223, R26-222, R26-205

### T6: The body, the outro, the whole cut
- Status: pending
- Owner: implementation_luna
- Route: `implementation_luna` builds; `reviewer` reads the diff and the built cut against the
  treatment mechanism by mechanism (M45) before the parent integrates
- Depends on: T5, HG3
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build_episode_h.py`, `.../SHOT-TABLE-H.md`, `.../build-h/**`, `.../CRITIC-REPORT-H.md`, `.../BEAT-PLAN-H.jsonl`
- Acceptance: every treatment row built; the outro stitched as the last word ends (the dissolve
  plus the recorded brand line 0.7 s under the card - `CAPABILITIES.md:63`,
  `content/video_engine/channel-assets/money-physics/outro/`) with its declared life
  (`recipe:outro-clip-life`); cues bound, then the report stamped (R26-198);
  `gate_motion_density` **0 FAIL**, or each remaining FAIL named with the ruling that allows it
  (`build-f` stands at 8 FAIL - M01, M03, M05, M07, M08, M10, M11, M12 - and every one is a
  fault this cut exists to close); the one-shot floor run with `--reference` and its
  shorts-reference caveat from T3 quoted, never silently passed; the species lint clean of
  unnamed plate uses; the beat plan covers every beat (M41); a frozen copy served for HG4 with
  the render beside it; the critic's fractions written; no collision left named instead of fixed
  (R26-191)
- Validate: `python content/video_engine/scripts/gate_motion_density.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h` and `python content/video_engine/scripts/gate_one_shot_floor.py content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h --project content/video_engine/projects/systems-and-blowups/steel-and-paper --reference content/video_engine/projects/systems-and-blowups/steel-and-paper/build-f` - both run unpiped, because a tail masks a FAIL
- Evidence: pending

### T7: The render and the card
- Status: pending
- Owner: parent
- Route: parent - the render is a long-running action against a frozen copy and the card is a
  write into the queue data, both parent-only
- Depends on: T6, HG4
- Write set: `content/video_engine/projects/systems-and-blowups/steel-and-paper/build-h-frozen-a/render/**` (gitignored), `docs/content-video-engine/review-queue.v1.json`
- Acceptance: rendered **from the frozen copy**, 24 fps (E99 s36), 16:9 - the tool's own
  default stage is 1920x1080 captured at device scale 4/3, so the file is **2560x1440**
  (`render_episode.py:92-93`; `RENDER_ASPECT=9:16` is the shorts path and is not set) - driven
  by `RENDER_BUILD` / `RENDER_URL` / `RENDER_NAME` against the frozen copy's own port; the
  render is **not** forced - a stale or FAILing `GATES-MOTION.md` is refused with exit 2 and
  that refusal is correct (any `--force` records its reason in `render/FORCED-RENDER.md`, is
  the parent's call, and is named in the card); loudness reported against the -14 LUFS /
  -1 dBTP target; the queue card carries the render path, the critic path and the publication
  question. The upload, the unlisting of the 2026-08-30 original and any push are the
  operator's
- Validate: `python content/video_engine/scripts/render_episode.py --test` then the full run with `RENDER_BUILD` / `RENDER_URL` / `RENDER_NAME` set, then `python content/video_engine/scripts/build_review_queue.py`
- Evidence: pending

## Verification

Run from the repo root, unpiped (a `tail` masks a FAIL - the standing rule):

1. `python scripts/prp_validate.py .claude/PRPs/plans/P68-STEEL-AND-PAPER-H.plan.md`
2. `python content/video_engine/scripts/run_script_gates.py content/video_engine/projects/systems-and-blowups/steel-and-paper/SCRIPT-H-VO.txt --ring certificate --counterparty "Bravos Research" --title "<locked>" --thumb-file <locked png> --long` (T1; add `--timeline .../build-h/timeline.json` after T2)
3. `python content/video_engine/scripts/viewer_windows.py ...` then `viewer_run.py` then `viewer_score.py` (T1, P36 - the VIEWER block stops saying NOT RUN)
4. `python content/video_engine/scripts/verify_take_whisper.py ... --take vo-h` and `python content/video_engine/scripts/master_vo_tone.py --verify` (T2)
5. `python content/video_engine/scripts/lint_species_choice.py content/video_engine/projects/systems-and-blowups/steel-and-paper --build build-h --long` (T3, T5, T6)
6. `python content/video_engine/scripts/self_watch.py .../build-h --project .../steel-and-paper --script SCRIPT-H` (T5, T6)
7. `python content/video_engine/scripts/measure_frozen_frames.py .../build-h` (T5, T6 - E49 / M18)
8. `python content/video_engine/scripts/gate_motion_density.py .../build-h` and `python content/video_engine/scripts/gate_one_shot_floor.py .../build-h --project .../steel-and-paper --reference .../build-f` (T6)
9. `python content/video_engine/scripts/recall_verify.py .../build-h` (R26-181 - the nine stages, the verbatim spans)
10. `python content/video_engine/scripts/render_episode.py --test`, then the full render (T7)
11. `python scripts/prp_status.py`

## Evidence And Handoff

- **In the PRP, not in a transcript:** each slice's Evidence line carries the command run, its
  verbatim tail, and the artifact paths (report files, contact sheets, the frozen copy's port,
  the render path, the git SHA of the wave that landed it).
- **What counts as evidence:** `SCRIPT-H-GATES.md` with its script hash and verdict, the
  viewer's JSON, `RECORD-CHAIN-H.md`'s stage table,
  `docs/research/LONG-FORM-CAPABILITY-AUDIT-2026-09-18.md`, `REBUILD-TREATMENT-H.md`,
  `build-h/SELF-WATCH.md`, `build-h/GATES-MOTION.md` with its timeline sha256,
  `CRITIC-REPORT-H.md`, and the render's own path and loudness. A delegated role's summary is
  not evidence; the parent re-runs the slice's validation itself.
- **What never lands in git:** the take, the renders, `player.html`, the contact sheets and
  every generated still. They live in the worktree that made them; what commits is the record
  of them (intake JSON, tables, manifests, reports).
- **Handoff out:** a queue card per human gate, written by the parent; each ruling to
  `docs/portable/OPERATOR-RULINGS.md` and back into this plan; every engine gap to
  `docs/content-video-engine/BACKLOG.md` with an owner. The upload, the unlisting of the
  2026-08-30 original, and any push wait on the operator's current word.
