---
name: never-pipe-gated-steps-to-tail
description: "a test run or gated step piped through tail/head loses its exit code - twice it let a FAIL through (drifted audio shipped through a chain; a non-parsing test reached origin, 59 failures showed as 3); run gated steps unpiped or with pipefail (P54 value pass K6)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T17:02:01.556Z
---

Two incidents in agent command chains (P54 reasoning extract C05-R016, 2026-09-01; C09-R012, 2026-09-07): a join's drift
gate FAILED but `| tail` hid the exit code, so the chain ran once on drifted audio; a pytest run piped through `tail`
in a commit chain let a test file that did not parse reach origin and showed 3 of 59 failures.

**Why:** in a pipeline the shell's status is the LAST command's - `tail` always succeeds - so `&&` after it runs on a
failure; and a truncated list hides the size of the failure.

**How to apply:** in Bash, run a gated step (pytest, `gate_*.py`, `verify_*.py`, `--check`) on its own and read its
exit code, or `set -o pipefail` / check `${PIPESTATUS[0]}`; to shorten noisy output, redirect to a file and read the
file after the status is known. The repo scan `content/video_engine/scripts/check_gated_pipes.py` covers scripts and doc
code blocks; since 2026-09-13 (operator approved) the PreToolUse hook `~/.claude/hooks/gated_pipe_guard.py`
(registered in `~/.claude/settings.json`, Bash|PowerShell, cwd inside this repo only) BLOCKS a gated step piped to
tail/head followed by `&&` without pipefail - same detector; heredoc bodies and quoted strings are ignored (its first
live catch was a python heredoc string). A blocked command: redirect to a file, read the status, then read the file. Related: [gate-extraction-orders](gate-extraction-orders.md).
