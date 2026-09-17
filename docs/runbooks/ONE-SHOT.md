# Runbook - One-shot a short to the operator's standard

A one-shot is your best complete short in one pass, using every capability the story can carry - never a test of one page (E96,
`docs/portable/OPERATOR-RULINGS.md:2797`; E71 `:2291`). This page is the ordered loop for any agent - Claude, Codex, Gemini or Hermes.
Every command below was run with `--help` on 2026-09-14. Paths are repo-relative.

## Before step 1 - find what exists

- **Search first, never from memory:** `python content/video_engine/scripts/docs_find.py "<term>"` (one line per hit, capabilities
  first). Quote the hit before you propose anything (`docs/runbooks/RECALL-RECEIPT.md`).
- **What is built:** `python content/video_engine/scripts/docs_find.py --capabilities` prints one line per capability by
  section (add `--state LIVE` or `--section chart`); the same list is `docs/CAPABILITIES-INDEX.md`, and a hit's full row is
  `sed -n <line>p docs/content-video-engine/CAPABILITIES.md`.
- **An effect or a recipe by name:** `python content/video_engine/scripts/effects_card.py "<name>"` (for example `"badge ladder"`).
- **The rulings override everything:** `docs/portable/OPERATOR-RULINGS.md`.
- **THE DOCTRINE, PER STAGE, BEFORE ANYTHING IS AUTHORED** (the operator, 2026-09-16, after one-shot #3: "did you recall research and knowledge on
  video generation/animation/processes before building the one shot?" and "doesn't it need to recall more than doc 29? isn't the idea basically that all
  of the docs provide the knowledge of how to build our episode/worlds/voice?"): the docs ARE the knowledge, one layer per stage the loop runs, and
  every layer is read before its stage - `docs/content-video-engine/PIPELINE.md` (the stage map and the capability index it opens with) first, then:
  the PACKAGE - `docs/portable/PACKAGING-PLAYBOOK.md`, E24 / E27; the SCRIPT - `patterns/SCRIPT-PATTERN-KIT.md`, `patterns/FULL-VIDEO-MAP.md`,
  `patterns/CHECK-RESPONSIBILITIES.md`, doc 51 (the shorts shape), the blind viewer (P36); the VOICE - `docs/portable/VOICE-PACK.md`, docs 32 / 33 /
  36 / 37 (delivery and the take), E70; the WORLD - the style spine (`style-spine.woodblock-vox-newsprint.v2.md`), the plate doctrine (docs 17 / 21 / 45; E39 / E40:
  stills are the asset; the host's identity pack; `PLATE-LIBRARY.json` and its approved rows; E99 s65 plate life); the EVIDENCE - doc 39, E25 / E28 / E50-E53 (chart
  form is law), the research tiers, `CAPABILITIES.md` rows 19-31 (the pages and their species); the MOTION - doc 29 Parts 3 / 8 / 9 (§9.15),
  `docs/portable/MOTION-GRAMMAR.md`, `docs/research/runs/p56-recipe-seeds/measures.md`, the effects catalogue; the SOUND - `docs/portable/SOUND-SOURCING.md` and the beds' levels in
  the approved builds; the PUBLISH - R26-8; and the RULINGS over all of it. Then the approved shorts' OWN tables and sheets -
  `japan-tariff-trick/build_short.py` + `build-short/SELF-WATCH.md`, `tokyo-tea-break/build_short.py` - and the parity BY MECHANISM (the page on the
  hook, the mount's build, the spiral return, the dock that reads then parks, the callout on a chart): present / absent / replaced by what (E99 s67
  Apply 7). `docs_find.py "<term>"` reaches every layer. A number parity (M40) let a cut through that used none of the mechanisms; one-shot #3
  recalled the script, voice, motion and ruling layers and skipped the world, style, sound and packaging ones.

**The receipt the build refuses without (P67, E99 s68 Q3 = C).** What step 0 read is WRITTEN, per stage, in the project's
`PRODUCTION-LEDGER.md` under a `## Recall` heading (the verifier reads the LAST such heading), one line per citation:

    - Recall(<stage>): <path>:<line> "<verbatim span>" (<note>)
    - Recall(<stage>): docs_find 0 hits for "<term>"

The nine stages, each owed at least one line: `package script voice world evidence motion sound publish rulings`. The span
is at least 12 characters, quoted off the EXACT line (whitespace runs collapsed, case-sensitive); `recall_verify.py <project>`
re-reads every path and line, refuses a stage with no citation, a path not in the repo, a line past the end, a span not on
that line ("the span moved to `<path>:<N>` - cite that" when it finds it elsewhere), and re-runs a zero-hit claim through
`docs_find.py` (a hit refuses it). `table.compile_timeline` runs the verifier on a build dir's FIRST compile and refuses
without a pass; a test-bed or lab build passes `no_receipt="<reason>"` and the manifest prints the reason for the rest of
that cut's life (`player.json` `compile.recall_receipt`); a recompile of an existing build carries its block. A citation
is not grounding: the verifier matches the span, the critic (step 9) scores whether the rows actually obey the lines cited.

## The loop

| # | Step | Do | Check (a FAIL stops you) |
|---|---|---|---|
| 1 | **The package** - title, thumbnail, and sentence one answering the thumbnail (E27 `:810`, E24 `:743`) | Lock the title and the thumbnail before the script is final | G45 title-word proxy and J12 (a JUDGE row), through step 2's runner with `--title`, `--thumb`, `--thumb-file` |
| 2 | **The script and its gates** (doc 51, E41 `:1277`) | `run_script_gates.py <script> --short --title "<title>" --thumb "<words>" --thumb-file <png>` - writes `<script>-GATES.md` | S01 hook by 0:03, S02 mechanism by 0:10, S03, S05 the ring in the last 20 %, S06, S07 no brand line spoken: FAIL; S08 WARN; J50/J51 JUDGE |
| 2b | **The blind viewer** (E26 `:949`) | `viewer_windows.py <script>` -> `viewer_run.py <script> --title --thumb-file` -> `viewer_score.py <script>` | V01 an unperceived declared beat FAILs; V04 WARNs |
| 3 | **The take and the word timeline** (E70 `:2264`) | `scratch_take.py --engine both`; `record_short_take.py <script>` (preflight) then `--go`; `align_take_whisper.py <script.txt> <take.mp3> <out.words.json>` (local Whisper only); `retime_take.py <take> --gaps` for the tight take | The recorder refuses a stale or failing gates report. A cut lands in an acoustic gap of at least 0.30 s, at 0.8 of the gap: `authoring/words.py` `cut_before` refuses a smaller gap by name |
| 4 | **The beat plan** - species by sentence, the comparator, the capability inventory, a recipe per beat (E96 `:2801`, E76 `:2442`) | Read `docs/content-video-engine/SPECIES-BY-SENTENCE.md`; `lint_species_choice.py <project> --propose` drafts rows per sentence (INFO, it chooses nothing); pick recipes with `effects_card.py`; write `<build>/BEAT-PLAN.jsonl` (per beat: `t0`, `comparator.compared_to`, a recipe or `why_none`) | M41 FAILs a beat the plan does not cover; M38 FAILs proven-recipe coverage under 0.60 |
| 5 | **The shot table** - GENERATE, THEN MODIFY - and name every departure (E99 s68; `docs/content-video-engine/PIPELINE.md:33` still holds: authored, never allocated - the beat plan is the intelligence and the compiler realises it) | `python content/video_engine/scripts/generate_base_table.py <project> <build> --table <build>/SHOT-TABLE-SHORT.py` writes the approved skeleton from step 4's `BEAT-PLAN.jsonl` (its optional per-beat `moves`) as the BASE and `<build>/BASE-TABLE.md` (the skeleton, act and rule per row; the beats the plan leaves silent; the signature mix beside the approved cuts'). Then the two doors: edit the generated rows in your `build_short.py` / the table, or layer `<build>/overrides.json` (`table.apply_sidecar`); every departure is a numbered row in `PRODUCTION-LEDGER.md` "Decisions taken without the operator": `N. BASE DEPARTURE - row <n> <what changed>: <why>, <ruling or path:line>` | `generate_base_table.py <project> <build> --departures` exits 1 on a departure with no ledger row; M45 parity by mechanism (a mechanism the plan owes and the cut lacks FAILs) and M46 signature variety (WARN) at step 7. A silent beat is the author's to fill or to leave - never filled by count. Never hand-edit the approved `SHOT-TABLE-SHORT.py` |
| 6 | **The build** - in a PRIVATE directory | The project's build-dir variable (`TARIFF_BUILD_DIR`, `TOKYO_BUILD_DIR`) or a new build script beside `build_short.py`; `table.compile_timeline(..., aspect="9:16", caption_style="phrase")`. The build ends by running the self-watch bar | Never build into a directory the operator is watching (`review-link-frozen-copy`) |
| 7 | **The gates on the build** | `probe.py <build> --gate`; `gate_motion_density.py <build>`; `gate_one_shot_floor.py <build>`; `self_watch.py <build>` | Motion rows M01/M08/M10/M16 (stillness), M12 (chart held as homework), M25-M28 (layout), M31/M32 (empty stage, black seam) FAIL. The floor: M35 at least 3 chart forms, M36 at least 1 chart-to-chart transform, M37 docks on at least a third of the beats, M38 recipe coverage 0.60, M39 narrative-to-chart 1.0, M41 the plan. `NOT CLEAN` on the self-watch is a stop |
| 8 | **Serve a frozen copy** | `python content/video_engine/projects/systems-and-blowups/tokyo-tea-break/serve_player.py <build> --port <private port>` (no-store); `self_watch.py <build> --html --player-url <url>` | A port nobody else is serving; never `--watch` on a link the operator holds |
| 9 | **Read the frames, then the CRITIC reads them, then hand over** (RECALL-RECEIPT s4, E71; P67 E99 s68 Q6 = C) | Read the self-watch sheets and the recipe audit sheet as a viewer; measure the geometry behind anything you call fixed; fill O1-O11. Your read is not the critic's: dispatch `reviewer` with `docs/content-video-engine/CRITIC-REPORT.md` as the contract (the frozen build, the table, the receipt, the beat plan) - it writes `<build>/CRITIC.md`, two tables and two fractions (mechanisms present p/owed, rows attributed a/rows), never a verdict; a whole-cut watch card names it in `critic` (`build_review_queue.py` refuses one without it) and the scores ride the card as INFO | "CLEAN" is your word after reading. `approved` is the operator's word only |

## The rules agents break (each cost a cut)

| Rule | Ruling | Caught by |
|---|---|---|
| Use every capability the story can carry; a gate-clean thin cut is a failure | E96 `:2797`, E71 `:2291` | M35-M41, then your read |
| A beat is a recipe; events per minute prove nothing | E96 `:2808` | M38 |
| The comparator comes before the series; inventory capabilities per beat before writing rows | E96 `:2801` | M41 |
| A fix adds or re-places motion; it never deletes it to pass | memory `first-pass-additive-capability-led` (no ruling yet) | nothing - your read |
| The chart proves one sentence and leaves | E25 `:761` | M12 |
| A chart reads right at a glance: sign is geometry, a date axis states its rule | E28 `:835`, E53 `:1705` | M26 in part; your read |
| The screen is never still; captions are the motion when nothing else moves | E21 `:557` | M01, M08, M10, M16 |
| Every held thing carries a named idle; parallax is not the cure for stillness | E49 `:1494` | M18 |
| A ring circles a number or a point on a chart; a picture's focus is a light | E56 `:1815` | the compiler |
| A dip is a world change, never a dock's transition or an entry into a mount | E47 `:1441` | M31, M32 |
| Fit a window by moving beats, never by clipping words | E41 `:1277` | `cut_before`, S01-S08 |
| Never rebuild a served review build; build privately | memory `review-link-frozen-copy` (no ruling yet) | nothing |
| Never pipe a gated step into `tail` or `head` | memory `never-pipe-gated-steps-to-tail` (no ruling yet) | nothing |
| Life marks belong to the plate they were measured on; never swap the plate under them | P58 T7 (2026-09-14) | nothing - your read |
| Depth needs a camera move that already has a reason; never add one to show parallax | E49 `:1494`, E59 `:1903` | nothing - your read |

## Known gaps (BACKLOG R26-135, R26-136)

- Step 4's beat plan and step 2's script are INTELLIGENCE work, not a tool's (E99 s66, 2026-09-16: "a tool can't realistically write the beat
  plan or the script, those always have to come from intelligence") - `BEAT-PLAN.jsonl` is written by the agent doing the one-shot; no writer is owed.
- The approved Japan and Tokyo shorts do NOT pass today's motion gate (Japan `3 FAIL`, Tokyo v2 `1 FAIL`) - they predate it. The
  one-shot floor measures against Japan as its reference; a new cut is held to today's gates, not to the approved cuts' scores.
- The silence-cut rule (M13) is enforced in `cut_before` and has no row in `docs/GATES-REGISTRY.md`.
