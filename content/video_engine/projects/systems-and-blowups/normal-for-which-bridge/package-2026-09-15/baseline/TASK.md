# T1 baseline audit ledger

Status: complete; no live tool/session handles
Date: 2026-09-15

## Acceptance criteria

- Preserve the watched source builds; write only under this `baseline/` directory.
- Copy exactly one prior build (`build-review`) as the gate target, without
  running the original `build_short.py`.
- Capture raw source/take/engine SHA-256 values, build inventory/counts, and
  exact stdout/stderr plus exit codes for layout, motion, floor, and self-watch
  commands.
- Record a comparison against the older `review-v1` report and list exact
  authoring, render, and scratch-voice commands for a future private package.
- Leave expected gate failures visible; do not suppress, repair, or relabel
  them.

## Anti-goals

- No new script, shot table, media, Flow order, voice, network request, render,
  original-build mutation, engine change, served review link, commit, or push.
- No claim that this historical build is ready for publication or operator
  approval.

## Write set

`baseline/` only. The source project and its existing `review-v1` and
`build-review` directories are read-only inputs.

## Checkpoint

- Copied 33 files from `build-review/` into `baseline/build-review/`.
- Probe gate: exit 0; 25 instants.
- Motion gate: exit 0; 0 FAIL / 2 WARN / 20 PASS / 1 JUDGE / 6 INFO.
- One-shot floor: exit 1; 5 FAIL / 1 WARN / 0 PASS / 1 JUDGE / 1 INFO.
- Self-watch: exit 1; NOT CLEAN, first failure M35; script/layout PASS,
  viewer absent, publish WARN.
- Evidence: `RUN-SUMMARY.tsv`, `HASHES.tsv`, `BASELINE-COMPARISON.md`,
  `COMMANDS.md`, `INCIDENT-2026-09-15.md`, and `logs/`.
- Next readiness: create a genuinely private package and obtain operator
  approval for its script/voice/render lane before authoring or rendering.
