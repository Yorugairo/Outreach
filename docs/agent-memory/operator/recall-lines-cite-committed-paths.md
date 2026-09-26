---
name: recall-lines-cite-committed-paths
description: "the commit hook refuses a `Recall:` path not yet in the RECORD - new in this commit OR only on a lane branch (lane B's committed test_prop_shadow.py was refused 09-23); cite paths already on main, at MAIN's line numbers, grammar `<path>:<line> \"<verbatim span>\" (<note>)`"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-23T04:34:38.588Z
---

The repo's commit-msg hook checks every `Recall: <path>:<line> (note)` line against the record (HEAD), so a Recall line naming a file ADDED in the same commit is REFUSED ("names a path that does not exist in the record"). Hit on P69 T2 (2026-09-22) with a new test file.

**Why:** Recall lines prove the change was grounded in what already existed; a new file cannot be prior art.

**How to apply:** in a mechanism commit's message, cite only paths already committed (the module the constant derives from, the existing test it keeps green); the new test goes in the body prose. Related: [recall-before-propose](recall-before-propose.md).

**Also (2026-09-23, twice in lane B):** the test-deletion hook reads a RENAMED test as a deleted one. Any agent that renames a test must report it, and the commit message carries `Tests-removed: <old name> - renamed to <new name>; <why>`. Put this in every implementer brief that may touch tests.

**Working copies are CRLF (core.autocrlf=true) - 2026-09-23:** a Python edit that reads a working file must normalise `\r\n` before matching `\n` patterns and write LF. A conflict resolver with a `\n`-only regex silently matched nothing; the follow-on `git add` then staged the conflict markers (caught before commit). Always assert the markers are gone BEFORE `git add`, never chain `git add` after a script that can fail.

**Line numbers are MAIN's (2026-09-23, T26e):** the hook checks `<path>:<line> "<verbatim span>"` against main, not the lane's HEAD - a span at line 3020 on the lane but 2696 on main was refused. Every Recall line needs a line number and a verbatim span; check it with `git show main:<path> | sed -n '<line>p'`. A ruling written only on the lane (s106/s107) can't be cited until it reaches main - name it in the body instead.
