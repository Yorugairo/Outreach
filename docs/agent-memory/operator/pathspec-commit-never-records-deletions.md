---
name: pathspec-commit-never-records-deletions
description: "git commit -- <paths> commits WORKING-TREE content of those paths and ignores what is staged for them; staged `git rm --cached` deletions are silently dropped (P63 T4, 2026-09-16 - d7448ca re-committed 13 layer files as edits instead of removing 24 from the index)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-16T19:44:27.569Z
---

On 2026-09-16 the P63 T4 commit was briefed as "pathspec form, name the 24 deleted paths too" so the staged `git rm --cached`
deletions would ride along. They did not: `git commit -F msg -- <paths>` records the working-tree content of the named paths
(the files were still on disk), re-committed 13 of them as modifications and left all 24 tracked. A third, index-only commit
(`git rm --cached` then `git commit -F msg` with NO pathspec) recorded the deletions.

**Why:** a pathspec-limited commit is a snapshot of the working tree for those paths; the index is bypassed for them. The
shared-checkout steward pattern (pathspec commits so other lanes' staged files never ride along) therefore cannot carry
deletions of files that still exist on disk - which is exactly the "untrack but keep on disk" case.

**How to apply:** to untrack files that stay on disk, stage with `git rm --cached` and commit INDEX-ONLY (no pathspec), after
confirming `git diff --cached --name-status` holds nothing but those `D` entries; if another lane has staged files, wait or
have them commit first. Never amend to repair it (history rule) - a follow-up commit says what happened.
Related: [worktree-sprawl](worktree-sprawl.md), [never-pipe-gated-steps-to-tail](never-pipe-gated-steps-to-tail.md).
