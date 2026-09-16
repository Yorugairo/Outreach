---
id: P64-PROGRESS-WHILE-THE-SYSTEM-UPDATES
title: Progress while the system updates - a stale layer never blocks a reader (the rebuild runs behind a lock, the reader reads what is there and says so), and the gates registry stops costing fifteen seconds; the last two waits P63 left
status: draft
operation: refactor
risk: standard
owner: parent
branch: main
created: 2026-09-16
updated: 2026-09-16
---

# Progress while the system updates

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
Second, a reader does not need the rebuild to FINISH; it needs to know the layer it read is stale, and the rebuild to be
under way exactly once. So: the reader reads what is on disk, prints one stderr line naming the stale layers, and starts
ONE background rebuild behind a lock file; the next reader gets the fresh layers. Staleness is bounded by one rebuild
and never blocks anyone.

## Intent And Acceptance

- `docs_find.py "<term>"` on a checkout with a stale layer returns in under 2 s, answers from the layers as they sit,
  prints `[layers] stale: a, b - rebuilding in the background (pid N)` on stderr, and the SAME query 30 s later (for a
  doc edit; ~1 min for a CAPABILITIES edit after T2) answers from fresh layers with no line.
- Only one rebuild runs at a time per checkout: a second reader while one is under way prints `[layers] stale: a, b -
  a rebuild is already running (pid N, started HH:MM:SS)` and starts nothing.
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

T1 and T2 are disjoint and run beside each other; T3 the record. Runs beside any engine lane (no engine file in any
write set).

## Patterns To Mirror

- P63 T3's `FileScan` / `word_tokens`: tokenise each file once, per-id lookups against a set.
- The review-queue server's mtime reload (`serve_review_queue.py`): a long-lived reader that never blocks on a rebuild.
- The bridge daemon's pid lock (`bridge_daemon.py`), if one exists - one process, a stale-pid takeover.

## Task Slices

### T1: THE NON-BLOCKING ENSURE - read what is there, say it is stale, rebuild once behind a lock
- Status: pending
- Owner: `implementation_luna`
- Depends on: none
- Write set: `content/video_engine/scripts/docs_layers.py`, `content/video_engine/scripts/build_docs_layers.py` (`--ensure --only` as the
  detached command; a `--status` that prints the lock / log), `content/video_engine/scripts/docs_find.py`,
  `content/video_engine/scripts/authoring/effects.py`, `content/video_engine/scripts/gate_one_shot_floor.py`,
  `content/video_engine/scripts/serve_player.py`, `content/video_engine/scripts/build_effects_gallery.py`,
  `content/video_engine/scripts/audit_research_provenance.py`, their tests (`test_docs_layers.py`, `test_build_docs_layers.py`,
  `test_docs_find.py`, `test_authoring_effects.py`, `test_gate_one_shot_floor.py`, `test_build_effects_gallery.py`)
- Acceptance: as Intent - `ensure(names, repo, wait=False)` returns immediately with `{"stale": [...], "started": pid | None,
  "running": {pid, started, names} | None}`; the lock file, the detached subprocess (`subprocess.Popen` with
  `creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` on Windows, `start_new_session=True` elsewhere; stdout/stderr to
  the log), the stale-pid / 10-minute takeover, the builder's last line surfaced by the next reader; `wait=True` = today's
  path; `docs_find --wait`; the readers' stderr lines as worded in Intent. Tests on a fake-builder tree: a stale layer ->
  one background rebuild -> fresh on the next call; two concurrent readers start one rebuild; a dead-pid lock is taken over;
  a failing builder's last line reaches the next reader; `wait=True` blocks and returns the rebuilt names.
- Validate: the tests above; then live: edit `docs/content-video-engine/BACKLOG.md` (a blank line, restored byte-identical
  afterwards), `time docs_find.py "verdict stack"` under 2 s with the stale line, `build_docs_layers.py --status`, then
  after the log ends the same query with no line and `--check` exit 0
- Evidence: pending

### T2: THE GATES REGISTRY'S FIFTEEN SECONDS
- Status: pending
- Owner: `junior_developer`
- Depends on: none
- Write set: `content/video_engine/scripts/build_gates_registry.py`, `content/video_engine/tests/test_build_gates_registry.py`
- Acceptance: `tests_naming` answers from a per-file token set built once per corpus (P63 T3's `word_tokens` shape; the
  predicate each candidate still faces is the original regex), `--check` builds the corpus once; output byte-identical
  (sha256 of both artifacts before and after, A/B/A in one process); `--check` under 3 s on this corpus (was 15-17 s); a
  test pins the byte identity on the fixture and a timing ceiling.
- Validate: `python content/video_engine/scripts/build_gates_registry.py --check` timed; `python -m pytest
  content/video_engine/tests/test_build_gates_registry.py -q`
- Evidence: pending

### T3: THE RECORD
- Status: pending
- Owner: parent
- Depends on: T1, T2
- Write set: `docs/content-video-engine/CAPABILITIES.md` (:201, one clause: reads never wait), `docs/content-video-engine/BACKLOG.md`
  (R26-159 closed, R26-161's GET clause closed if T1's non-blocking path covers the server route), `evals/LAYERS-TIMING-2026-09-16.md`
  (a third table), this plan -> complete
- Acceptance: the numbers in the rows; `build_docs_layers.py --check` clean; `prp_validate` PASS
- Validate: as above
- Evidence: pending

## Verification

- `python -m pytest content/video_engine/tests -q -k "docs_layers or docs_find or gates_registry or authoring_effects or one_shot_floor or effects_gallery"` green.
- The live read above under 2 s on a stale tree; the fresh read after the log ends; exactly one lock at a time.
- `build_gates_registry.py --check` under 3 s, byte-identical.

## Evidence And Handoff

Timings into `evals/LAYERS-TIMING-2026-09-16.md`. Handoff: P62 (per-lane worktrees) - each worktree carries its own
`docs/.layers/`, so a rebuild in one never touches another.
