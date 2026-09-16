---
id: P64-PROGRESS-WHILE-THE-SYSTEM-UPDATES
title: Progress while the system updates - the WRITE refreshes the layers in the background and a reader never rebuilds (docs_find reads what is there and says if it is stale), the gates registry stops costing fifteen seconds, and a per-file cache when the staleness window bites; the last waits P63 left
status: complete
operation: refactor
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# Progress while the system updates

> **APPROVED 2026-09-16** - the operator invoked `/prp-implement p64` after the amendment (the write refreshes, the read never rebuilds; T4 deferred). Running from T1.

## Summary

P63 took the layers out of git and off the commit path. One wait survived it, on the READ side: `docs_find.py` and every
runtime reader call `docs_layers.ensure()` before they read, and `ensure` is synchronous - when CAPABILITIES.md changes,
everything downstream re-digests and the next reader waits about three minutes (measured 2 m 55 s on 2026-09-16 evening);
a doc edit elsewhere costs 27 s. The operator, the same evening: *"i don't think we should force to hold on the
capabilities gates ... i think it's clear that our gates are working to keep everything up to date, can't we move to a
system where the agents are able to keep progressing while the system updates."*

Two facts decide the shape. First, most of the three minutes is one layer: `build_gates_registry.py` spends 14 of its
17 s in `tests_naming` - 326 gate ids x ~480 test files = 156,672 regex searches, the same per-id-over-every-file loop
P63 T3 removed from the animation registry - and `--check` builds the corpus twice (`scratchpad/gates_profile.txt`).
Second - the operator, later the same evening: *"i think docs_find doesnt need to rebuild the stale layer every answer"* -
a reader should not rebuild at all. The WRITE is the event: a hook on Edit / Write under `docs/` or the scripts (and a
post-commit hook for the other harnesses) starts ONE background refresh behind a pid lock; `docs_find.py` and every reader
only READ what is on disk and print one stderr line if a layer is stale. Staleness is bounded by one refresh and blocks
no one. Third, the operator asked whether the index should be tokenised the way SigMap tokenises the workspace. Measured:
SigMap answers a code query in 10.6 s from a per-file cache it refreshes at query time and indexes no prose; docs_find
answers the same term in 0.29 s from the layers, which already ARE the record's map (headings / leads / terms per section;
the registries from the checkers' own ASTs). The part of SigMap worth taking is its per-file cache: our builders re-walk
all ~480 files when one changes. That is T4, pulled forward only if the staleness window shows up in practice.

## Intent And Acceptance

- `docs_find.py "<term>"` NEVER rebuilds: on a stale checkout it answers in under 1 s from the layers as they sit and prints
  `[layers] stale: a, b (a refresh is running, pid N, started HH:MM:SS)` or `... (no refresh running - run
  build_docs_layers.py --refresh)` on stderr; the same query after the refresh answers with no line.
- The WRITE refreshes: a user-level PostToolUse hook on Edit|Write whose path is under `docs/`, `content/video_engine/scripts/`,
  `content/video_engine/tests/` or `content/video_engine/effects/` runs `build_docs_layers.py --refresh` (returns at once:
  starts ONE detached `--ensure` behind `docs/.layers/REBUILD.lock`, or does nothing if one is running - the running one
  re-checks the digests when it finishes and goes again if a write landed meanwhile); a `post-commit` hook does the same for
  the harnesses that do not run the Claude hook. Only one refresh runs at a time per checkout.
- A crashed rebuild leaves nothing wedged: the lock carries the pid and a start time; a lock whose pid is dead or older
  than 10 minutes is taken over, and the builder's last line is written beside it for the next reader to print.
- Callers that must have fresh layers (the record slices, a test, `--strict`) can still block: `ensure(..., wait=True)`
  and `build_docs_layers.py --ensure` keep today's synchronous behaviour.
- `build_gates_registry.py --check` under 3 s (was 15-17 s), byte-identical output.
- Every runtime reader T2 wired (authoring.effects, the one-shot floor gate, the gallery, the player server's catalogue
  route, the provenance audit) takes the non-blocking path by default; the gate and the audit, whose verdicts depend
  on a current layer, print the staleness in their report header and exit as today.

## Scope

- `content/video_engine/scripts/docs_layers.py`: `ensure(..., wait=False)` -> the lock file `docs/.layers/REBUILD.lock`
  (pid, started, names), a detached subprocess running `build_docs_layers.py --ensure --only <names>` with its output to
  `docs/.layers/REBUILD.log`, `rebuild_status()` for the readers' line; `wait=True` the old path.
- `docs_find.py` and the five readers: the default flips to non-blocking; `--wait` / `wait=True` where a caller needs it.
- `build_gates_registry.py`: `tests_naming` reads a per-file token set built once; `--check` builds once.
- CAPABILITIES:201 (one clause), the P63 backlog rows R26-159 / R26-161 closed by this.

## Not Building

- A daemon or a file watcher. A rebuild is started by the read that found the staleness; nothing runs when nothing reads.
- Any change to what the layers contain or to the commit path (P63 settled both).
- The engine lock (P62).

## Human Gates

- HG1 - the approval of this plan. No card: nothing here is visual.

## Mandatory Reads

- `content/video_engine/scripts/docs_layers.py` (`ensure` :468, `stale` :457, `stamp` :496, the lock-free design it has today),
  `docs_find.py` (the ensure call and the stderr line T2 added), `build_gates_registry.py` (`tests_naming` :425-427,
  `build` :501, `check` :670, `rendered` :657, `main` :688), `build_animation_registry.py` (`word_tokens`, `FileScan` -
  P63 T3's pattern to copy), `tests/test_docs_layers.py` (the fake-builder fixture), `tests/test_build_gates_registry.py`.
- `.claude/PRPs/plans/P63-THE-LAYERS-ARE-BUILD-OUTPUT.plan.md` (T1 / T2 evidence), `evals/LAYERS-TIMING-2026-09-16.md`.

## Execution Path

T1 and T2 are disjoint and run beside each other; T3 the record; T4 deferred behind the condition on its status line. Runs beside any engine lane (no engine file in any
write set).

## Patterns To Mirror

- P63 T3's `FileScan` / `word_tokens`: tokenise each file once, per-id lookups against a set.
- The review-queue server's mtime reload (`serve_review_queue.py`): a long-lived reader that never blocks on a rebuild.
- The bridge daemon's pid lock (`bridge_daemon.py`), if one exists - one process, a stale-pid takeover.

## Task Slices

### T1: THE WRITE REFRESHES, THE READ NEVER REBUILDS - a background refresh behind a lock, started by the hook
- Status: complete (2026-09-16)
- Owner: `implementation_luna`
- Depends on: none
- Write set: `content/video_engine/scripts/docs_layers.py`, `content/video_engine/scripts/build_docs_layers.py` (`--refresh`, `--status`;
  `--ensure --only` as the detached command), `~/.claude/hooks/layers_refresh.py` (NEW, user-level - the operator's config, shown as a
  diff) + its entry in `~/.claude/settings.json`, `.git/hooks/post-commit` (main checkout; the voice lane's `commit-msg` untouched), `content/video_engine/scripts/docs_find.py`,
  `content/video_engine/scripts/authoring/effects.py`, `content/video_engine/scripts/gate_one_shot_floor.py`,
  `content/video_engine/scripts/serve_player.py`, `content/video_engine/scripts/build_effects_gallery.py`,
  `content/video_engine/scripts/audit_research_provenance.py`, their tests (`test_docs_layers.py`, `test_build_docs_layers.py`,
  `test_docs_find.py`, `test_authoring_effects.py`, `test_gate_one_shot_floor.py`, `test_build_effects_gallery.py`)
- Acceptance: as Intent - `refresh(repo)` returns immediately with `{"stale": [...], "started": pid | None, "running":
  {pid, started, names} | None}` and `status(repo)` reads the lock / log; the readers call `status` only (never `ensure`); the
  hook (`~/.claude/hooks/layers_refresh.py`, pipe-tested like the guard) and `.git/hooks/post-commit` call `--refresh`; the lock
  file, the detached subprocess (`subprocess.Popen` with
  `creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` on Windows, `start_new_session=True` elsewhere; stdout/stderr to
  the log), the stale-pid / 10-minute takeover, the builder's last line surfaced by the next reader; `wait=True` = today's
  path; `docs_find --wait`; the readers' stderr lines as worded in Intent. Tests on a fake-builder tree: a stale layer ->
  one background rebuild -> fresh on the next call; two concurrent readers start one rebuild; a dead-pid lock is taken over;
  a failing builder's last line reaches the next reader; `wait=True` blocks and returns the rebuilt names.
- Validate: the tests above; then live: edit `docs/content-video-engine/BACKLOG.md` (a blank line, restored byte-identical
  afterwards), `time docs_find.py "verdict stack"` under 2 s with the stale line, `build_docs_layers.py --status`, then
  after the log ends the same query with no line and `--check` exit 0
- Evidence: report `scratchpad/assembly/P64-T1.md`. `docs_layers.refresh()` / `status()` / `start_refresh()` (detached: DETACHED_PROCESS |
  CREATE_NEW_PROCESS_GROUP on Windows, a new session elsewhere), the pid lock `docs/.layers/REBUILD.lock` {pid, started, names} + `REBUILD.log`,
  `pid_alive` / `live_lock` (a dead pid or > 600 s taken over), `--then-recheck` bounded to three rounds; the venv's python.exe is a
  REDIRECTOR (Popen's pid 30568 vs the child's own 11460) so the child re-stamps the lock with its own pid at startup and clears it only
  if still its own. `build_docs_layers.py --refresh / --status / --then-recheck / --only a,b`. The readers status-only by default with
  `--wait`: docs_find (the two stderr wordings), authoring.effects, the one-shot floor gate (the header line + `Measures.layers_note`),
  the gallery, the provenance audit, the player server. The hook `~/.claude/hooks/layers_refresh.py` (resolves the checkout from the edited
  file's path) registered by the parent in `~/.claude/settings.json` (PostToolUse, Edit|Write|MultiEdit|NotebookEdit, timeout 10; the
  before-copy in the scratchpad) and pipe-tested: an Edit under docs/ started a refresh (pid 21196) in 0.95 s, silent; `.git/hooks/post-commit`
  appended to the existing git-lfs hook. MEASURED: docs_find on a stale tree 0.837 s with the stale line (was 27 s - 2 m 55 s), 0.494 s
  once fresh; the parent's own read 0.769 s; the catalogue GET 422-437 ms -> 21 ms then 1.6-5.0 ms. Tests: 24 added, 3 renamed with
  receipts, none deleted; the parent's run 193 passed in 28 s (the committed-tree test green once the other lane's card validated).

### T2: THE GATES REGISTRY'S FIFTEEN SECONDS
- Status: complete (2026-09-16)
- Owner: `junior_developer`
- Depends on: none
- Write set: `content/video_engine/scripts/build_gates_registry.py`, `content/video_engine/tests/test_build_gates_registry.py`
- Acceptance: `tests_naming` answers from a per-file token set built once per corpus (P63 T3's `word_tokens` shape; the
  predicate each candidate still faces is the original regex), `--check` builds the corpus once; output byte-identical
  (sha256 of both artifacts before and after, A/B/A in one process); `--check` under 3 s on this corpus (was 15-17 s); a
  test pins the byte identity on the fixture and a timing ceiling.
- Validate: `python content/video_engine/scripts/build_gates_registry.py --check` timed; `python -m pytest
  content/video_engine/tests/test_build_gates_registry.py -q`
- Evidence: report `scratchpad/assembly/P64-T2.md`. `token_runs(text)` = every maximal `[\w-]+` run, built once per test file in
  `build()`; `tests_naming` answers a one-run id by set membership (the `(?<![\w-])id(?![\w-])` regex can only match a maximal run - an
  exact equivalence), a multi-run rule text by the runs as a candidate filter with every candidate still facing the original regex;
  `rendered` / `write` / `check` take pre-built records so `main` builds once (was 2 on --check, 4 on --write). PROOF A/B/A in one
  process against HEAD's script: 163 records equal, both renders the same sha256 (jsonl bb1cd301..., md cf11a45f...); the fixture
  render pinned before the edit. `--check` 14.73 / 14.79 s -> 0.85 / 0.82 / 0.81 s (the parent's own run 0.66 s); HEAD build 7.25 s vs
  patched 0.46 s. Five tests added, none deleted or renamed (the token table vs a direct sweep on a tricky corpus and on the real
  480-file corpus, the pin, one corpus read per check, a ceiling); 45 passed (the parent's run 45 in 2.03 s).

### T4: THE PER-FILE CACHE - the two heaviest builders re-extract only the files whose hash changed (SigMap's lesson)
- Status: pending - DEFERRED: pulled forward only if T1's staleness window (~27 s after a doc edit; ~1 min after a CAPABILITIES edit once T2 lands) shows up in practice
- Owner: `implementation_luna`
- Depends on: T1, T2
- Write set: `content/video_engine/scripts/build_docs_index.py`, `content/video_engine/scripts/build_gates_registry.py`, `content/video_engine/scripts/docs_layers.py`
  (a per-builder cache dir under `docs/.layers/cache/<layer>/`), their tests
- Acceptance: each builder keeps per-input-file records keyed by (path, sha256) under the cache dir and re-extracts only the files whose key
  changed, then renders the artifact from all records; output byte-identical to a cold build (sha256 A/B); a one-file doc edit rebuilds
  the docs index in under 0.5 s (was 1.7 s) and the gates registry in under 1 s; a cold build (no cache) equals today's.
- Validate: the sha tables; the timings; the builders' tests
- Evidence: pending

### T3: THE RECORD
- Status: complete (2026-09-16)
- Owner: parent
- Depends on: T1, T2
- Write set: `docs/content-video-engine/CAPABILITIES.md` (:201, one clause: the write refreshes, a read never rebuilds), the
  `retrieval-layers` skill + `CLAUDE.md`'s fast route (one clause each), `docs/content-video-engine/BACKLOG.md`
  (R26-159 closed, R26-161's GET clause closed if T1's non-blocking path covers the server route), `evals/LAYERS-TIMING-2026-09-16.md`
  (a third table), this plan -> complete
- Acceptance: the numbers in the rows; `build_docs_layers.py --check` clean; `prp_validate` PASS
- Validate: as above
- Evidence: CAPABILITIES:201 (the P64 clause), the retrieval-layers skill and CLAUDE.md's fast route (a read never rebuilds; --wait), BACKLOG
  R26-159 closed (31ebf09) and R26-161's GET clause closed, `evals/LAYERS-TIMING-2026-09-16.md` third table. T4 stays deferred on its
  condition (the staleness window is now background time no reader pays; pull it forward only if a lane reads stale in practice).

## Verification

- `python -m pytest content/video_engine/tests -q -k "docs_layers or docs_find or gates_registry or authoring_effects or one_shot_floor or effects_gallery"` green.
- The live read above under 2 s on a stale tree; the fresh read after the log ends; exactly one lock at a time.
- `build_gates_registry.py --check` under 3 s, byte-identical.

## Evidence And Handoff

Timings into `evals/LAYERS-TIMING-2026-09-16.md`. Handoff: P62 (per-lane worktrees) - each worktree carries its own
`docs/.layers/`, so a rebuild in one never touches another.
