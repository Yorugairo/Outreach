---
id: P62-THE-WORKTREE-REGISTER
title: The worktree register - one row per worktree in the register we already have, a merge-before-main checklist that is only git (merge, test, fast-forward, never force), and one test that catches the two things that actually went wrong (a duplicate ruling number, a worktree nobody listed)
status: complete
operation: feature
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# The worktree register

## Summary

E99 s47: *"work has to be parallel ... worktrees with both agents aware of each worktree, and accept that there
will be sprawl at times until things get sent back to main."* The operator, 2026-09-16, on the first draft of this
plan (eight slices, a generated board, a third commit hook, hardlinks, a rehome): *"this is sounding way too
complex. isn't a better way to just check git before pushing to main and always preferring non-destructive
methods?"* Yes. What actually went wrong this week was two things: two lanes appended the same ruling number
(E99 s49) and a worktree existed that no board named. Both are caught by a check that runs before anything
reaches main, and git already carries every other fact (`git worktree list`, `git log main..branch`).

P62 is three small things, no new tools:

1. **The register is the file we have.** `docs/LANE-REGISTER.md` becomes `docs/WORKTREE-REGISTER.md`: one row per
   worktree (path, branch, owner, what it is for, live slice, engine lock yes/no, ruling numbers claimed, last
   merge to main), hand-edited, read at start, updated at every commit - s47's board. `docs/STATE-OF-WORK.md` and
   `survey_worktrees.py` (stale since 2026-09-03) are retired; `git worktree list` is the census.
2. **The merge-before-main checklist, only git and non-destructive.** In the lane's worktree: `git fetch`,
   `git merge main` (merge, never rebase a shared branch), run the two tests below plus the golden suite, resolve
   by keeping both sides on the record files, then `git merge --ff-only` onto main and update the row. Never
   `--force`, never amend after a push, never delete a branch or worktree without the operator's word, never
   `git add -A`, deletions in an index-only commit. Written once in `PRP_EXECUTION.md` and the steward agent.
3. **One test that fails before the merge if the rules were broken:** every `**E99 s<n> - ` heading in
   `OPERATOR-RULINGS.md` appears once, and every path in `git worktree list` has a row in the register. It runs
   with the suite the steward already runs.

## Intent And Acceptance

- Every worktree on this machine has a row; the test proves it (`git worktree list` vs the table) and fails when
  one is added without a row.
- Two lanes cannot both land one ruling number on main: the claim column is the rule, the uniqueness test is the
  check before the merge, and a duplicate found there is renumbered by the incoming lane (with its citations) before
  the fast-forward.
- The steward's checklist is written where the steward reads, and the first real merge after this plan follows it.
- The doctrine files say the three rules in one line each: read the register at start, claim a ruling number in it
  before writing, merge before main by the checklist.

## Scope

- `docs/LANE-REGISTER.md` -> `docs/WORKTREE-REGISTER.md` (renamed with `git mv`; the schema above; the four
  current rows carried over with their paths).
- `content/video_engine/tests/test_worktree_register.py` (new, under 60 lines).
- `docs/runbooks/PRP_EXECUTION.md` ("Lane write sets" -> "Worktrees and lanes" with the checklist),
  `.claude/agents/release_steward.md` (the same checklist), `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` (one line each),
  `docs/runbooks/RECALL-RECEIPT.md` (one line: the register is read before a ruling is numbered).
- `docs/STATE-OF-WORK.md` and `content/video_engine/scripts/survey_worktrees.py` deleted (index-only commit;
  nothing imports or tests the script - no receipt owed); `CAPABILITIES.md:330` and
  `docs/agent-memory/operator/recall-system.md:3,:23` repointed.
- `BACKLOG.md` R26-84 closed with the verdict in bold; the memories `worktree-sprawl`,
  `worktree-read-scope` amended.

## Not Building

- A generated register, a claims file in the git dir, a ruling-claim commit hook, `merge=union` attributes, a
  hardlink linker - the first draft (kept at `scratchpad/assembly/P62-REVIEW.md` with its review) - dropped by the
  operator's word: check git before main, prefer non-destructive methods.
- Saved states (route 2, E99 s47) and per-agent engine copies (route 3, refused).
- The f10b plate rehome (B2, `BACKLOG.md:730`; `build_plate_library.py:9` hard-codes the codex worktree path and two
  wave-06 manifests differ between the checkouts) and Steel and Paper's absolute worktree paths (`:731`): real debt,
  not parallel-work debt - they keep their rows, with those two facts added.
- Retiring any worktree (sprawl accepted until merged back, s47); inventories of the two stale Claude worktrees.
- Any change to the engine lock or its files.

## Human Gates

- None. Nothing here is destructive: a rename, a test, doctrine lines, and two tracked files deleted in git
  (recoverable). Pushes only on the operator's fresh word in chat.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md` (Lane write sets :73-:86; PRP Format :173-:240); `docs/runbooks/RECALL-RECEIPT.md`.
- `docs/portable/OPERATOR-RULINGS.md` E99 s23 (:3039), s47 (:3212); `docs/LANE-REGISTER.md` (all of it);
  `BACKLOG.md` R26-84 (:490).
- `.git/hooks/commit-msg` (the receipts resolve from the MAIN checkout via `git rev-parse --git-common-dir`, so a
  worktree runs main's hook scripts - a hook change merges first).
- `content/video_engine/tests/test_golden_frames.py` (:144-:166, the manifest's `engine_sha256` - re-pinned once at
  the merge if the engine moved on either side).
- Memories: `worktree-sprawl`, `worktree-read-scope`, `pathspec-commit-never-records-deletions`,
  `never-pipe-gated-steps-to-tail`.

## Execution Path

T1 (the test) and T2 (the register + the checklist + the doctrine) in parallel - disjoint write sets; T2's
register must make T1 pass on this machine (one live checkout - main - and four dormant worktrees today; Astra's
fresh worktree off main gets its row when it is cut - a worktree, not a clone: it shares the objects, the LFS store and
the hooks). One commit each, allowlisted paths, from the
main checkout; the deletions in T2's index-only commit.

## Patterns To Mirror

- `content/video_engine/tests/test_review_queue.py`: a test that reads a committed record file and asserts a
  structural rule on it, skipping cleanly when the environment lacks git.
- The current register's rules block (claim the next free number here BEFORE writing it; one shared file committed by
  one lane at a time; the engine lock has one holder) - kept verbatim, one column added for the worktree path.

## Task Slices

### T1: THE CHECK - one test: ruling numbers unique, every worktree has a row
- Status: complete (2026-09-16)
- Owner: `junior_developer`
- Depends on: none
- Write set: `content/video_engine/tests/test_worktree_register.py` (new)
- Acceptance: `test_every_ruling_number_appears_once` reads `docs/portable/OPERATOR-RULINGS.md` (UTF-8) and asserts each `^\*\*E99 s(\d+) - ` heading occurs once, naming the duplicates; `test_every_worktree_has_a_register_row` runs `git worktree list --porcelain` from the repo root, normalises each path, and asserts a row in `docs/WORKTREE-REGISTER.md` names it (a path column; case-insensitive on Windows), listing the unnamed ones; the test skips with a reason if git is absent. Under 60 lines; no new dependency.
- Validate: `python -m pytest content/video_engine/tests/test_worktree_register.py -q` (fails today on the row check until T2 lands - the report shows the failure text and then the pass after T2).
- Evidence: report `scratchpad/assembly/P62-T1.md`. `test_worktree_register.py`, 55 lines, no new dependency: `^\*\*E99 s(\d+) - ` counted
  with a `Counter` (65 headings, s1-s65, no duplicate); `git worktree list --porcelain` paths compared to the register's backticked
  cells by `Path.resolve()` casefolded (a cell that is not a directory is ignored - a stale row is not a failure; git absent ->
  skip). Before T2: `1 failed, 1 passed` on "docs/WORKTREE-REGISTER.md missing - P62 T2 writes it"; after T2: 2 passed.

### T2: THE REGISTER AND THE CHECKLIST - rename, one column, the merge flow, the doctrine lines, the retirements
- Status: complete (2026-09-16)
- Owner: parent
- Depends on: none (T1's test is the acceptance)
- Write set: `docs/LANE-REGISTER.md` -> `docs/WORKTREE-REGISTER.md` (`git mv`; columns: path, branch, owner, purpose, live slice, engine lock, rulings claimed, last merge to main; a row for each path `git worktree list` shows today - the main checkout's lanes as they are, the two codex and two Claude worktrees marked "dormant, unmerged: <n> commits" from `git log main..<branch> --oneline | wc -l`; the rules block kept, plus the checklist below), `docs/runbooks/PRP_EXECUTION.md` ("Worktrees and lanes": read the register at start; claim a ruling number in it before writing; one engine writer per worktree; THE CHECKLIST - in the lane's worktree `git fetch` and `git merge main` (never rebase a shared branch), `python -m pytest content/video_engine/tests/test_worktree_register.py content/video_engine/tests/test_golden_frames.py -q` unpiped, a conflict on `OPERATOR-RULINGS.md` / `review-answers.jsonl` resolved by keeping both sides, a duplicate number renumbered by the incoming lane together with its citations (`rg "E99 s<n>"`), goldens re-pinned once with a sha table if the engine moved on either side, then from main `git merge --ff-only <branch>`, the row updated; NON-DESTRUCTIVE - never `--force`, never amend after a push, never delete a branch or worktree without the operator's word, never `git add -A`, deletions index-only; push only on the operator's word), `.claude/agents/release_steward.md` (the checklist verbatim), `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` (one line each pointing at the register and the checklist), `docs/runbooks/RECALL-RECEIPT.md` (one line), `docs/STATE-OF-WORK.md` + `content/video_engine/scripts/survey_worktrees.py` (deleted, index-only commit), `docs/content-video-engine/CAPABILITIES.md:330`, `docs/agent-memory/operator/recall-system.md:3,:23` (repointed), `BACKLOG.md` (R26-84 CLOSED in bold; B2 / `:730` / `:731` gain the two facts from Not Building), the memories `worktree-sprawl`, `worktree-read-scope` (+ `MEMORY.md`), this plan's status
- Acceptance: T1 passes on this machine; `git ls-files docs/LANE-REGISTER.md docs/STATE-OF-WORK.md content/video_engine/scripts/survey_worktrees.py` empty; `rg -n "STATE-OF-WORK|LANE-REGISTER" --glob '!.claude/worktrees/**' --glob '!node_modules/**'` hits only history (rulings, plans); the steward file and the runbook carry the same checklist in the same order; `docs_find "worktree register"` hits the runbook after the layers refresh; R26-84's verdict grepped in bold.
- Validate: `python -m pytest content/video_engine/tests/test_worktree_register.py -q`; `git ls-files` as above; `rg` as above; `python content/video_engine/scripts/docs_find.py "worktree register"`; `rg -n "R26-84.*\*\*.*CLOSED" docs/content-video-engine/BACKLOG.md`; `python scripts/prp_validate.py .claude/PRPs/plans/P62-THE-WORKTREE-REGISTER.plan.md`.
- Evidence: script `scratchpad/assembly/p62_t2.py` (run from the main checkout). `git mv docs/LANE-REGISTER.md docs/WORKTREE-REGISTER.md`;
  the page: the s47 sentence, the operator's 2026-09-16 sentence, five rules, the six-step checklist, eight rows (three lanes on main,
  four dormant worktrees with `git log main..<branch>` counts: f10b 1 ahead / 1169 behind, p29 0 / 1165, spark-animations 0 / 1173,
  sweet-villani 2 / 703). The same six steps, one Python constant, in `PRP_EXECUTION.md` "Worktrees and lanes" (:73) and
  `release_steward.md`. One line each in `AGENTS.md` (section 9), `CLAUDE.md` (a fast route), `GEMINI.md` (a task-route row),
  `RECALL-RECEIPT.md` (:38). `git rm docs/STATE-OF-WORK.md content/video_engine/scripts/survey_worktrees.py` (nothing imported or
  tested the script); `build_docs_manifest.py` :54 / :144 and its test :215 repointed from STATE-OF-WORK.md to WORKTREE-REGISTER.md
  (a name-kind rule, not a file read); `CAPABILITIES.md:330`, `docs/agent-memory/operator/recall-system.md` (:3, :22-:26),
  `worktree-sprawl.md:16-18`, `BACKLOG.md:3` repointed; R26-84 CLOSED in bold; the two carried-debt lines (:730-:731) carry the
  review's facts (the builder's hard-coded path, the two divergent wave-06 manifests, the 188 references). Validate: the manifest
  test failed twice on the STALE docs-index layer (the deleted files still indexed) until `build_docs_layers.py --ensure` rebuilt
  11 layers; then `test_worktree_register.py` + `test_build_docs_manifest.py` 29 passed; `build_docs_layers.py --check` every layer
  in sync (12); `docs_find "worktree register"` hits the register, the runbook :73, BACKLOG :1, recall-system; `git ls-files` of
  the three retired paths empty; `rg STATE-OF-WORK|LANE-REGISTER` outside rulings / plans hits only recall-system's history line.
  DEVIATION: T1 and T2 land in ONE index commit (the test is red without the register and the deletions need an index commit).

## Verification

- `python -m pytest content/video_engine/tests/test_worktree_register.py -q` (unpiped; the exit code is the verdict).
- `python scripts/prp_validate.py .claude/PRPs/plans/P62-THE-WORKTREE-REGISTER.plan.md`; `python scripts/prp_status.py`.
- The first real merge from a worktree after this plan runs the checklist and its report quotes each step.
- Risks named: (1) a hand-edited register can go stale - the row check catches a missing row, not a stale purpose;
  that is the awareness cost s47 accepted; (2) a duplicate number caught at the merge means renumbering after
  citation - the claim column is what prevents it, the test is the backstop; (3) the hooks resolve from the main
  checkout, so a hook change merges to main first.

## Evidence And Handoff

- Reports: `scratchpad/assembly/P62-T1.md`, `P62-T2.md`.
- Two commits, allowlisted paths, from the main checkout; push only on the operator's word.
- The register page is the handoff: one live checkout, four dormant worktrees, the checklist under them; Astra's row
  when its worktree is cut.
