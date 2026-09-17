---
id: P67-THE-VERIFIED-RECEIPT-AND-THE-CRITIC
title: The verified receipt and the critic - the build refuses without a per-stage Recall block whose every line is re-read and matched verbatim, and the reviewer reads the BUILT cut as a different reader and returns two scores, never one verdict
status: running
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# The verified receipt and the critic

## Summary

E99 s68 Q3 = C, Q6 = C (`docs/portable/OPERATOR-RULINGS.md:3254`), from the operator's two questions behind R26-177:
*"did you recall research and knowledge on video generation/animation/processes before building the one shot? maybe we
need to include that lookup in the beginning of every video"* and *"doesn't it need to recall more than doc 29? isn't
the idea basically that all of the docs provide the knowledge of how to build our episode/worlds/voice?"*.

Today the record is read on trust. `docs/runbooks/ONE-SHOT.md` "Before step 1" names the doctrine per stage (package,
script, voice, world, evidence, motion, sound, publish, the rulings) and nothing checks that any of them was opened.
One-shot #3's `PRODUCTION-LEDGER.md` "## Recall" block is thirteen `- Recall: <path>:<line> (note)` lines - untyped by
stage, unverified past "the path exists", and the cut still skipped the world, style, sound and packaging layers. The
commit hook `scripts/hooks/recall_receipt.py` checks the same one thing on a four-entry `MECHANISM_PATHS` list that
does not include `build_caption_pages.py` or the authoring kit, so the 2026-09-16 caption fix - a mechanism change -
printed *"no mechanism touched"*.

The spike's gotcha is the design constraint: **citation is not grounding** (arXiv 2606.04990 - document-level citation
"may hide unsupported or partially supported claims"; "answer correctness should be separated from evidence support and
attribution quality"). A text-only receipt (Q6 A) was REJECTED as a fabrication surface. So P67 builds two things and
neither is a reminder:

1. **A receipt with teeth.** A stage tag, a `path:line`, and a VERBATIM QUOTED SPAN read back off that line - or an
   explicit `docs_find 0 hits` that the verifier re-runs. Nine stages, each owed at least one line. `compile_timeline`
   refuses a build whose project has no passing receipt; the lab's escape is a NAMED reason printed into the compile
   manifest, never a silent flag.
2. **A director-critic, two scores.** `reviewer` on Opus reads the BUILT cut against the mechanism list before the
   queue and writes `<build>/CRITIC.md`: mechanism correctness (present / absent / replaced by what) and attribution
   quality (each row traced to a receipt line, or named as an unattributed choice) - two fractions with their
   denominators stated, claim-level, never one verdict and never a gate row. It is a DIFFERENT reader from
   `self_watch.py`'s O1-O11: the builder reading its own cut is the thing that failed (memory
   `judge-the-frame-not-the-diff`).

The receipt's verdict is mechanical and final (R1). The critic's two scores are JUDGE and are never laundered into a
gate verdict (R1/R3, `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`): they ride the operator's card as
INFO. The operator judges the cut, not the scores.

## Intent And Acceptance

- A short cannot compile from a project whose `## Recall` block is missing a stage, cites a line that does not carry
  its quoted span, or claims a zero-hit term the record actually holds. Each refusal names the stage, the path and the
  reason; the refusal text tells the author how to repair it (including "the span moved to `:N`").
- A build that compiled carries its receipt's identity: `player.json`'s `compile.recall_receipt` block (ledger path,
  sha256 of the `## Recall` block, per-stage counts, verdict, timestamp) - or the `no_receipt` reason verbatim.
- The commit hook sees the authoring kit and the caption builder, and checks a quoted span when a `Recall:` line
  carries one (a line with no span still passes the COMMIT hook: older commits carry none; only the BUILD receipt
  requires spans). The hook has a test file for the first time.
- An open `watch` card whose proof is the WHOLE cut is refused by name unless it names a critic report that exists.
- HG1: one-shot #3's `build-oneshot-3` gets a receipt written after the fact and a critic pass, WITHOUT rebuilding it
  (E99 s11, `review-link-frozen-copy`) - the calibration case, and the operator's read of whether the two scores said
  anything the gates did not.

## Scope

- `content/video_engine/scripts/recall_verify.py` (new): the grammar, the verifier, the CLI, the refusal texts.
- `content/video_engine/scripts/authoring/table.py`: `compile_timeline` refuses without a pass; `write_compile_manifest`
  records the receipt block.
- `scripts/hooks/recall_receipt.py`: the mechanism list grows; the span check; the first test.
- `content/video_engine/scripts/build_review_queue.py`: the whole-cut card owes a critic report.
- `docs/content-video-engine/CRITIC-REPORT.md` (new, the contract), `patterns/CHECK-RESPONSIBILITIES.md` (one section),
  `.claude/agents/reviewer.md` (the pass and its brief).
- `docs/runbooks/ONE-SHOT.md` (step 0 the grammar, step 9 the critic), `docs/runbooks/RECALL-RECEIPT.md` (the verifier,
  amending nothing in s1-s6), `docs/content-video-engine/CAPABILITIES.md` (one row), `BACKLOG.md` (R26-181, R26-177).
- `memory-trades-the-calendar/PRODUCTION-LEDGER.md` + `build-oneshot-3/CRITIC.md` + the queue card (HG1).

## Not Building

- **No gate ids.** `docs/GATES-REGISTRY.md` is GENERATED by `ast` from seven script-side checkers and `--check` refuses
  a hand edit; and an M- or R-id would make the verdict mechanical-final (R1) for a reader whose scores are JUDGE. The
  verifier refuses BY NAME at the compile door - the pattern `authoring/words.py:cut_before` already sets (M13 has no
  registry row either). The registry is untouched; CAPABILITIES carries the row.
- No change to `self_watch.py`, to the motion gates, to `gate_one_shot_floor.py` or to M40/M45 (P66 owns the parity
  row; until it lands the critic's mechanism list is E99 s67 Apply 1-8 plus the approved tables
  `japan-tariff-trick/build_short.py` and `tokyo-tea-break/build_short.py`).
- No rebuild of any approved or served cut (E99 s11). No re-recording, no re-render, no new generation.
- No scoring model, no learned weights, no critic-in-the-loop fix: the critic reports and stops.
- No receipt sidecar file (see Execution Path for why the ledger won), no new commit hook, no push.

## Approval

Approved by the operator 2026-09-16: *"yes, run them in parallel /prp-implement"* - P65, P66 and P67 run as concurrent delegated slices on main (disjoint write sets; the two shared files sequenced as written), no new worktree.

## Human Gates

- **HG1 - the first verified receipt and the first critic pass, on a real cut.** One-shot #3's `build-oneshot-3`
  re-verified without rebuilding it: the receipt typed for it after the fact (the calibration case - the nine stages
  against what that pass actually read, including the four it skipped), `recall_verify.py` run on it, and
  `<build>/CRITIC.md` written by a `reviewer` dispatch. The operator judges ONE question: do the two scores say
  something the gates did not? Queue row in `docs/content-video-engine/review-queue.v1.json` + `REVIEW-QUEUE.md`
  (written in T7, the change that frames it). It blocks nothing mechanical; it decides whether the critic pass becomes
  standing practice in the runbook's step 9 or stays a one-shot experiment.

## Mandatory Reads

- `docs/content-video-engine/GRILL-AGENTS-HARNESS-EFFECTS-2026-09-16.md` - decision 5, the rejected Q6 A, gotcha
  "citation is not grounding", build order item 3, appendix A section 3.
- `docs/portable/OPERATOR-RULINGS.md:3254` (E99 s68); `docs/content-video-engine/BACKLOG.md` R26-181 (:613), R26-177 (:609).
- `docs/runbooks/RECALL-RECEIPT.md` WHOLE (the triggers, the receipt, the order, s4 inspect AND measure, s5 silence,
  and the second receipt beside it - the same refusal-not-reminder shape and the same `commit-msg` hook).
- `docs/runbooks/ONE-SHOT.md` "Before step 1" (:7-:31) and the loop's steps 4-9.
- `scripts/hooks/recall_receipt.py` (its docstring is the 2026-09-08 ruling), `content/video_engine/tests/test_hook_test_deletions.py`
  (the hook-test pattern: `importlib.util.spec_from_file_location`, `check()` called directly, one case per real event).
- `content/video_engine/scripts/authoring/table.py:compile_timeline` / `:write_compile_manifest`,
  `authoring/__init__.py:Project` (`here` = the episode dir, `build` = the pass's own dir).
- `content/video_engine/scripts/build_review_queue.py` (`REQUIRED`, `PROOF_FIELDS`, `validate_proof`, `validate_record`)
  and `content/video_engine/tests/test_review_queue.py`.
- `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` s0-s1 (R1 a tool's verdict is final, R2 laundering,
  R3 JUDGE rows are never summarized, R5 tool outputs are cited).
- `content/video_engine/scripts/self_watch.py` (the header: section 1 mechanical, section 2 the agent's O1-O11, CLEAN
  is the agent's word) - the critic is a DIFFERENT reader, never the builder.
- `.claude/agents/reviewer.md`; `docs/runbooks/PRP_EXECUTION.md` "Dispatch mapping", "The brief", "PRP Format".
- `docs/WORKTREE-REGISTER.md` at start. Memories: `judge-the-frame-not-the-diff`, `recall-before-propose`,
  `never-pipe-gated-steps-to-tail`, `review-link-frozen-copy`, `script-changes-go-to-the-next-letter`.

## Execution Path

**The grammar** (one line per citation, inside the project's `## Recall` block):

    - Recall(<stage>): <path>:<line> "<verbatim span>" (<note>)
    - Recall(<stage>): docs_find 0 hits for "<term>"

Stages: `package script voice world evidence motion sound publish rulings` - the nine the runbook's step 0 names, each
owed at least one line. The span is at least 12 characters, compared after collapsing runs of whitespace, case-sensitive.

**Where it lives: the project's `PRODUCTION-LEDGER.md` "## Recall" block, not a `<build>/RECALL-RECEIPT.md` sidecar.**
`compile_timeline(ep, build, ...)` holds `ep` (`Project.here`, the episode dir) so the ledger is reachable without a new
argument; the recall is a PROJECT fact, read once and true across the eight build passes one-shot #3 took, while a
build dir is per-pass, thrown away, and explicitly movable (`write_compile_manifest` stores `episode_dir` RELATIVE to
the build for exactly that reason); one-shot #3 already carries the block, so the calibration case is an amendment and
not an invention; and a sidecar in a build dir is a file agents forget and gitignore by habit. The BUILD still records
which receipt it passed under - the manifest's `compile.recall_receipt` block carries the ledger path, the sha256 of
the block, the per-stage counts and the verdict - so a cut is traceable to its receipt after the ledger moves on.

**The tolerance: the EXACT line, never the line plus or minus one.** The stricter reading, for three reasons: a
one-line window doubles the false-accept surface for exactly the short spans that are easiest to fabricate; the docs
layers are build output rebuilt by digest, so "the file moved" is normal and a tolerance would quietly normalise stale
citations; and the strict check can repair itself - on a miss the verifier scans the whole file for the span and, when
it finds it, refuses with *"the span moved to `<path>:<N>` - cite that"*. A refusal that names the fix costs the author
one edit and keeps every number in the record true.

**The refusals, all by name:** a stage with no line at all; a path that is not in the repo; a line number past the end
of the file; a span that is not on that line (with the moved-to note when found elsewhere); a span under 12 characters;
a `0 hits` claim that `docs_find.py --json --limit 1` answers with a hit (the first hit is printed). Exit 1, one block
of text, no partial credit.

**The escape:** `compile_timeline(..., no_receipt="<reason>")` - a non-empty reason or nothing. It exists for the Tokyo
test bed and P65's recipe lab, and it writes itself verbatim into `compile.recall_receipt.skipped_reason`, so a cut
that skipped the receipt says so in its own manifest for the rest of its life.

**Order.** T1 (the verifier) first and alone - T2 and T3 both import it. T4 (the critic's contract) is doctrine and
runs in parallel with T1-T3; T5 (the queue's refusal) needs T4's report name. T6 (the runbook and the docs) after the
mechanisms work. T7 (HG1) last: the receipt typed for one-shot #3, verified, the critic dispatched, the card written -
nothing rebuilt.

**Overlap.** T5 and P65 T4 both edit `build_review_queue.py`'s `validate_record` and `test_review_queue.py`: P65 T4 (the `batch` kind) lands first and T5 is written on top of it; the steward never holds both open. **Dispatch.** T1 and T5 `implementation_luna` (bounded implementation with tests); T2 and T3 `junior_developer`
(explicit, small); T4, T6, T7 the parent (doctrine, the agent definition that gates the parent's own dispatches, the
operator's card). Every commit touching a mechanism file carries its own `Recall:` lines; the `release_steward`
commits allowlisted paths; nothing is pushed without the operator's fresh word.

## Patterns To Mirror

- `scripts/hooks/test_deletions.py` + `content/video_engine/tests/test_hook_test_deletions.py`: a pure `check()` the
  test calls directly, a refusal message that carries the repair, and a hook driven end-to-end with
  `--message "<msg>"` on synthetic paths. T3's test is its sibling.
- `content/video_engine/scripts/authoring/words.py:cut_before`: the compiler door that refuses a bad value BY NAME -
  the model for a compile refusal that is not a registry gate.
- `content/video_engine/tests/test_review_queue.py`: schema refusals asserted by their message
  (`pytest.raises(match=...)`), the LIVE queue data validated as its own test.
- `docs/content-video-engine/SELF-WATCH.md` + `self_watch.py`'s three sections: the shape for `CRITIC.md` - mechanical
  rows first, the reader's rows second, one verdict line last (here: two scores, never one).
- P62's restraint: no new tool where an existing file and one test will do.

## Task Slices

### T1: THE VERIFIER - the grammar, the re-read, the verbatim match, the zero-hit re-run
- Status: done
- Owner: `implementation_luna`
- Depends on: none
- Write set: `content/video_engine/scripts/recall_verify.py` (new), `content/video_engine/tests/test_recall_verify.py` (new)
- Acceptance: `STAGES` is the nine names in the runbook's order; `parse_block(text)` reads the `## Recall` block of a ledger and returns one record per `- Recall(<stage>): ...` line of the LAST `## Recall` heading in the ledger (a ledger carrying more than one - the calibration case appends a dated block below the original - is verified on the last block only, and the report says which heading it read); (a legacy `- Recall: ...` line with no stage parses as `stage=None` and is reported as UNSTAGED, never silently dropped); `verify(repo, ledger)` returns `(ok, lines)` refusing, each by name: a stage with no citation, a path outside the repo or absent, a line past EOF, a span under 12 characters, a span absent from the cited line (searching the file and printing "the span moved to `<path>:<N>`" when found), and a `0 hits for "<term>"` claim that `docs_find.py --json --limit 1` answers with a hit (the first hit printed); whitespace collapsed, case-sensitive; the exact-line tolerance pinned by a test (a span one line off is REFUSED and the message names the real line). CLI `python content/video_engine/scripts/recall_verify.py <episode dir or ledger path> [--json]` exits 0 or 1 and prints the refusals. No new dependency; the docs_find call is a subprocess so a stale layer rebuilds by digest. The module names no episode and no project (the authoring kit's rule) and never writes.
- Validate: `python -m pytest content/video_engine/tests/test_recall_verify.py -q`
- Evidence: `content/video_engine/scripts/recall_verify.py` (325 lines: `STAGES`, `MIN_SPAN = 12`, `parse_block` -> `RecallBlock` with `.sha256()` / `.stage_counts()` / `.unstaged()`, `verify(repo, ledger_or_episode_dir)`, `docs_find_hits` as a subprocess, the CLI) and `tests/test_recall_verify.py` - `22 passed in 0.21s` (the parent re-ran it); the exact-line pin mutation-checked (a +-1 window fails the test); the live zero-hit re-run refused `0 hits for "recall receipt"` with CAPABILITIES.md:272; the CLI on one-shot #3 exits 1 with 13 UNSTAGED legacy lines and all nine stages refused (the pre-T7 calibration state). A broken docs_find is reported `UNCHECKED` on its own line, never a silent pass (report `scratchpad/assembly/P67-T1.md`).

### T2: THE COMPILE DOOR - no passing receipt, no timeline; the manifest records which receipt it was
- Status: done
- Owner: `junior_developer`
- Depends on: T1
- Write set: `content/video_engine/scripts/authoring/table.py`, `content/video_engine/tests/test_authoring_kit.py`
- Acceptance: the door binds the FIRST compile of a build dir only. `compile_timeline` has eleven callers today (`rg "compile_timeline\(" content/video_engine`): seven project build scripts, the two P61 Tokyo builds, `change_report.py:260` and `serve_player.py:492` (the live editor's recompile) - the last two recompile EXISTING builds and must keep working. So: a build dir whose compile manifest already carries a `recall_receipt` block recompiles under that block unchanged; a manifest with no block (every build made before P67) recompiles with `{"skipped_reason": "legacy build (pre-P67)"}` stamped into it; a NEW build dir (no manifest) is where the check runs. On that first compile `compile_timeline` grows `no_receipt: str | None = None` and, before it touches the compiler, runs `recall_verify.verify` on `ep`; on a refusal it raises with the verifier's text verbatim and NO timeline is written; on a pass `write_compile_manifest` gains `recall_receipt={"ledger": <path relative to the build>, "sha256": <of the ## Recall block>, "stages": {<stage>: <count>}, "verdict": "pass", "checked_at": <iso>}`; with a non-empty `no_receipt` the compile proceeds and the block is `{"skipped_reason": <the string verbatim>}` instead; an empty string or `True` is refused as not a reason. Callers: P65's `lab_build.py` passes `no_receipt="recipe lab candidate <id>"` (the lab authors no episode); the approved projects' build scripts are NOT edited and NOT re-run (E99 s11) - a rebuild of an approved cut was already forbidden, and the door now says so by name. Tests: a fixture project with a good block compiles and the manifest carries the block; a recompile of a build dir with a legacy manifest passes and is stamped `legacy build (pre-P67)`; a missing stage refuses and leaves the build dir without a timeline; the escape records its reason. Before rewriting the test file, diff the `def test_*` NAMES before and after (`RECALL-RECEIPT.md` "the second receipt"), never the count.
- Validate: `python -m pytest content/video_engine/tests/test_authoring_kit.py -q`
- Evidence: `authoring/table.py` +63/-3: `recall_receipt_block(ep, build, no_receipt)` is `compile_timeline`'s first statement; the block lives in `player.json`'s `compile` dict under `recall_receipt` (pass: ledger/sha256/stages/verdict/checked_at; escape and legacy: `skipped_reason`). Test names 55 -> 61, no removals. Parent's review change: the door is keyed on the manifest's COMPILE block, not the file - a `player.json` the render baseline wrote before any compile is still a first compile (the legacy test adjusted to expect the refusal). `python -m pytest content/video_engine/tests/test_authoring_kit.py content/video_engine/tests/test_recall_verify.py -q` -> `85 passed in 0.61s` (report `scratchpad/assembly/P67-T2.md`).

### T3: THE COMMIT HOOK GROWS - the authoring kit and the caption builder, the span check, its first test
- Status: done
- Owner: `junior_developer`
- Depends on: T1
- Write set: `scripts/hooks/recall_receipt.py`, `content/video_engine/tests/test_hook_recall_receipt.py` (new)
- Acceptance: `MECHANISM_PATHS` gains `content/video_engine/scripts/build_caption_pages.py` and `content/video_engine/scripts/authoring/` (the 2026-09-16 caption fix printed "no mechanism touched" - the test names that case); a `Recall:` line that carries a quoted span is checked against the cited line through `recall_verify` (loaded by `importlib` from the main checkout, as `.git/hooks/commit-msg` already resolves); a line with NO span keeps today's path-exists check and passes (backward compatible - the BUILD receipt is where spans are mandatory); if the module is missing or fails to import the hook falls back to today's check and says so on one line, never blocking a commit on its own plumbing. `RECALL_RE` (`:33`, `^\s*Recall:\s*`) is widened to accept the staged form `Recall(<stage>):` as well, or a commit that cites in P67's own grammar is refused by the hook it ships - the test pins both forms. `check()` stays a pure function of `(message, paths)`. Test: the caption-fix case, an authoring-kit path, a good span, a wrong span refused naming the line, a spanless line still passing, and the hook driven end to end - `python scripts/hooks/recall_receipt.py --message "<msg>" content/video_engine/scripts/build_caption_pages.py` exits 1 without a receipt and 0 with one.
- Validate: `python -m pytest content/video_engine/tests/test_hook_recall_receipt.py -q`
- Evidence: `scripts/hooks/recall_receipt.py` +75/-7: `MECHANISM_PATHS` gains `build_caption_pages.py` and `authoring/`; `RECALL_RE` takes `Recall:` and `Recall(<stage>):`; a body with a quoted span is checked through `_load_verifier()` (importlib on `recall_verify.py`, registered in `sys.modules` before exec - three tests caught the silent fallback without it) via the verifier's own `_parse_line` + `_check_citation`; a spanless body keeps the path-exists check; a missing verifier prints one line and falls back. `tests/test_hook_recall_receipt.py` 12 passed; the sibling `test_hook_test_deletions.py` 6 passed (the parent re-ran both). Live: `REFUSED ... line 8 does not carry the span ...; the span moved to docs/runbooks/RECALL-RECEIPT.md:9 - cite that` (exit 1); the caption-fix case now reads `build_caption_pages.py` as a mechanism (report `scratchpad/assembly/P67-T3.md`).

### T4: THE CRITIC'S CONTRACT - two tables, two fractions, a different reader, and the brief
- Status: done
- Owner: parent
- Depends on: none
- Write set: `docs/content-video-engine/CRITIC-REPORT.md` (new), `docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md` (one new section), `.claude/agents/reviewer.md`
- Acceptance: `CRITIC-REPORT.md` fixes `<build>/CRITIC.md`: table 1 MECHANISM CORRECTNESS - one row per mechanism on the list (until P66's M45, the E99 s67 Apply 1-8 list plus the mechanisms of `japan-tariff-trick/build_short.py` and `tokyo-tea-break/build_short.py`), each `present / absent / replaced by <what>` with the instant (`t`, the frame read) it was judged at; table 2 ATTRIBUTION QUALITY - one row per shot-table row, traced to a receipt line (`Recall(<stage>) <path>:<line>`) or named as an unattributed choice, claim-level never document-level (arXiv 2606.04990); then TWO scores as fractions with their denominators stated on the same line (`mechanisms present 6/14 (the list of 2026-09-16)`, `rows attributed 19/32`), no third number and no verdict word. The page states: the critic is `reviewer` on Opus, never the parent and never the builder (`self_watch.py`'s O-rows are the builder's own read); the scores are JUDGE, ride the card as INFO, and are never laundered into a gate verdict (R1/R3); a mechanism the critic cannot see at an instant is `absent`, not "unclear". CHECK-RESPONSIBILITIES gains one section pointing at it and naming which verdict kind the two scores are. `reviewer.md` gains "The director-critic pass" - what to read (the built cut's frames, the shot table, the receipt), what to write, and the brief's fields per PRP_EXECUTION "The brief".
- Validate: `python content/video_engine/scripts/build_docs_layers.py --ensure` then `python content/video_engine/scripts/docs_find.py "director-critic"` (the new page is a hit) and `rg -n "CRITIC-REPORT" docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md .claude/agents/reviewer.md`
- Evidence: `docs/content-video-engine/CRITIC-REPORT.md` (new: what the critic reads, table 1 with the eleven-mechanism list of 2026-09-16 and the `not owed` rule, table 2 claim-level attribution, the two score lines, what it never does, the brief); `patterns/CHECK-RESPONSIBILITIES.md` section 4 (the scores are JUDGE, never a mechanical result); `.claude/agents/reviewer.md` "The director-critic pass". `build_docs_layers.py --ensure` exit 0 (layers rebuilt); `docs_find.py "director-critic"` hits the new page at :1 and :114; `rg CRITIC-REPORT` hits `CHECK-RESPONSIBILITIES.md:279` and `reviewer.md:34`.

### T5: THE QUEUE REFUSES A WHOLE-CUT WATCH WITH NO CRITIC
- Status: done
- Owner: `implementation_luna`
- Depends on: T4
- Write set: `content/video_engine/scripts/build_review_queue.py`, `content/video_engine/tests/test_review_queue.py`
- Acceptance: a module constant `WHOLE_CUT_S = 30.0` (the live data calibrates it: one-shot #3's whole-cut clip is 77.6 s, the beat clips are far under 30 s - measured in the slice, not quoted). The live card `one-shot-3-fable-memory-calendar` is an open whole-cut watch with no critic yet, so the rule lands in two steps: T5 ships it as a WARN printed by name (`--write` and `--check` still exit 0), and T7 flips the constant `CRITIC_REQUIRED = True` in the same commit that gives the live card its `critic` path - the live data never fails validation on main. At full strength `validate_record` refuses, by name, an OPEN `watch` record carrying a whole-cut proof (a `player` proof, or a `clip` with `t1 - t0 >= WHOLE_CUT_S`) that has no `critic` field naming a repo-relative report path - the message says why (E99 s68: a whole cut reaches the operator after a different reader has read it) and how to get past it (run the pass, or make the proof a clip of the beat it is about); `critic` is NOT added to `REQUIRED`, so the 79 records on disk are untouched; the DISK check (the named path exists and lives under the proof's `build`) runs in the writer, not in `validate`, so the fixture tests keep working. Tests: the WARN (and, with the constant flipped, the refusal) on a player proof and on a 77.6 s clip, a short clip unaffected, a `ruled` record unaffected, the live queue data still validating, and the writer refusing a `critic` path that is not on disk (`tmp_path`).
- Validate: `python -m pytest content/video_engine/tests/test_review_queue.py -q`
- Evidence: `build_review_queue.py` `WHOLE_CUT_S = 30.0`, `CRITIC_REQUIRED = False` (T7 flips it), `CRITIC_REPORT_NAME`, `critic_owed` in `validate_record` (WARN now, the same text as a refusal), `check_critic_files` in the writer (the disk check), the WARNs printed by `main`; 7 new tests, 59 pass (the parent re-ran); `--check` exit 0 printing exactly two WARNs: `one-shot-3-fable-memory-calendar` and `p66-hg1-the-first-generated-base` both owe a critic report. T7 must give BOTH cards a critic (or a beat clip) in the commit that flips the constant.

### T6: THE RUNBOOK AND THE DOCS - step 0's grammar, step 9's critic, the capability row, the backlog
- Status: pending
- Owner: parent
- Depends on: T1, T2, T3, T4, T5
- Write set: `docs/runbooks/ONE-SHOT.md`, `docs/runbooks/RECALL-RECEIPT.md`, `docs/content-video-engine/CAPABILITIES.md`, `docs/content-video-engine/BACKLOG.md`, `.claude/PRPs/plans/P67-THE-VERIFIED-RECEIPT-AND-THE-CRITIC.plan.md`
- Acceptance: ONE-SHOT.md "Before step 1" ends with the grammar (the two line forms, the nine stages, where the block lives, that the compile refuses without it, what the `no_receipt` reason costs) and step 9 gains the critic between the self-watch read and the hand-over ("your read is not the critic's; dispatch `reviewer`, attach `CRITIC.md`, the scores are INFO on the card"); RECALL-RECEIPT.md gains a section AFTER s6, beside "the second receipt", describing the BUILD receipt, its verifier, the exact-line tolerance and the self-repairing refusal - amending nothing in s1-s6 (the commit receipt and the order stand as written); CAPABILITIES.md gains ONE row (the verified receipt + the critic: where, state, proof = the three test files); BACKLOG R26-181 CLOSED in bold with the verdict, R26-177 amended in bold with the sentence that step 0 is now enforced at the compile door. The layers are build output - rebuilt, never hand-edited.
- Validate: `python content/video_engine/scripts/build_docs_layers.py --write` (unpiped), then `python content/video_engine/scripts/docs_find.py "recall receipt"`, `rg -n "R26-181.*CLOSED" docs/content-video-engine/BACKLOG.md`, and `python scripts/prp_validate.py .claude/PRPs/plans/P67-THE-VERIFIED-RECEIPT-AND-THE-CRITIC.plan.md`
- Evidence: pending

### T7: HG1 - the calibration case: one-shot #3's receipt, verified, and the first critic pass, nothing rebuilt
- Status: running (the receipt half done; the critic pass and the card's `critic` field wait on T5)
- Owner: parent
- Depends on: T1, T4, T5, T6
- Write set: `content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/PRODUCTION-LEDGER.md`, `content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar/build-oneshot-3/CRITIC.md` (untracked artifact), `docs/content-video-engine/review-queue.v1.json`, `docs/content-video-engine/REVIEW-QUEUE.md` (generated), `content/video_engine/scripts/build_review_queue.py` (the one constant)
- Acceptance: the ledger gains a DATED block `## Recall (verified, P67)` BELOW the original thirteen lines - the original stays as recorded (memory `script-changes-go-to-the-next-letter`) - carrying the nine stages with spans, and saying in one line which stages that pass did NOT read (a stage it never opened is cited now from the record it should have read, and the ledger says so, so the calibration case does not fabricate history); `recall_verify.py` exits 0 on it; a `reviewer` dispatch (brief per PRP_EXECUTION "The brief": this plan, T7, read-only, the mechanism list, `CRITIC-REPORT.md` as the contract, the frozen player, the exact validation) writes `build-oneshot-3/CRITIC.md` with the two tables and the two fractions; the queue card `one-shot-3-fable-memory-calendar` gains its `critic` path, `CRITIC_REQUIRED` flips to `True` in the same commit (T5), and ONE new line in `judge` naming the two scores as INFO and the operator's one question. THE CUT IS NOT REBUILT, NOT RE-SERVED AND NOT RE-RENDERED (E99 s11): the critic reads the frozen build read-only, through `probe.Probe` and the served copy.
- Validate: `python content/video_engine/scripts/recall_verify.py content/video_engine/projects/systems-and-blowups/memory-trades-the-calendar` (exit 0, unpiped); `python content/video_engine/scripts/build_review_queue.py --write --no-probe` then `python content/video_engine/scripts/build_review_queue.py --check`; `python -m pytest content/video_engine/tests/test_review_queue.py -q`
- Evidence: (receipt half, 2026-09-17) `memory-trades-the-calendar/PRODUCTION-LEDGER.md` gains `## Recall (verified, P67 T7 - 2026-09-17)` BELOW the original thirteen lines: eighteen `Recall(<stage>)` lines across the nine stages with verbatim spans, and one paragraph naming what the 2026-09-16 pass did NOT read (the package playbook, the strip rule, the plate-production doctrine, the sound-sourcing rules, the cross-posting row; the motion doctrine only through the floor). `recall_verify.py` on the project: `Read: "## Recall (verified, P67 T7 - 2026-09-17)" at line 66 (the last of 2 headings) - 18 Recall line(s)` ... `PASS - 18 citation(s) verified across 9 stages.` (exit 0). Nothing rebuilt.

## Verification

- Unpiped, in order: `python -m pytest content/video_engine/tests/test_recall_verify.py content/video_engine/tests/test_hook_recall_receipt.py content/video_engine/tests/test_authoring_kit.py content/video_engine/tests/test_review_queue.py -q` (never into `head` or `tail`: the pipe's exit code masks a FAIL).
- `python content/video_engine/scripts/build_docs_layers.py --check` in sync;
  `python scripts/prp_validate.py .claude/PRPs/plans/P67-THE-VERIFIED-RECEIPT-AND-THE-CRITIC.plan.md`; `python scripts/prp_status.py`.
- The end-to-end proof is T7: a real project verifies and a real cut gets a critic report without being rebuilt.
- Risks named: (1) **the receipt becomes typing** - the span match is the only defence against a plausible fabrication,
  so the 12-character floor and the exact line are load-bearing and the tests pin both; (2) **the compile door blocks
  the lab** - P65 builds hundreds of test-bed cuts and must pass `no_receipt="<reason>"`; if that reason is ever
  defaulted inside a build script the door is gone, so the manifest prints it and T7's report reads it back;
  (3) **the critic laundered into a gate** - the scores are fractions on a card and never a FAIL row (R1/R3), and
  nothing in `self_watch.py` or `gate_one_shot_floor.py` reads `CRITIC.md`; (4) **a hook that refuses a commit on its
  own plumbing** - T3's import fallback is mandatory and tested.

## Evidence And Handoff

- Reports under `docs/research/runs/p67-<slice>/` (gitignored disk-as-bus); each return names its path.
- Commits by the `release_steward`, allowlisted paths, each carrying its own `Recall:` lines (T2 and T3 touch mechanism
  files and will be refused without them - the hook they change gates them). Deletions, if any, index-only. No push
  without the operator's fresh word.
- The handoff is HG1's card: the receipt one-shot #3 should have had, the critic's two tables, and the operator's one
  question - do the two scores say something the gates did not?
- RESOLVED by the parent (2026-09-16), the readings kept for the record: **(a) nine stages on every project compile** (Reading A) - the lab and the test bed are not authoring an episode, so they pass the named `no_receipt` reason and the manifest prints it; a stage taxonomy per build kind is the filler surface, not the cure. **(b) the calibration receipt is APPENDED as a dated block** (Reading A) and the verifier reads the LAST `## Recall` heading (T1).
- The two readings as the architect framed them. **(a) Do all nine stages bind every compile, or only a short /
  one-shot compile?** Reading A (planned): nine always, and a lab build uses the named `no_receipt` reason - one rule,
  no taxonomy of build kinds to keep true. Reading B: a test-bed compile declares a subset (`world`, `motion` only),
  because demanding a `package` citation from a recipe-lab probe teaches agents to type filler - the fabrication
  surface Q6 A was rejected for. **(b) Does the calibration receipt amend one-shot #3's existing `## Recall` block or
  append a new dated one?** Reading A (planned): append - the original thirteen lines are what that pass actually read,
  and the record of a failure is evidence. Reading B: amend in place - a reader of the ledger should see one receipt,
  and the verifier then has one block to read instead of a rule about which block counts.
