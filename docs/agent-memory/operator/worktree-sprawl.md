---
name: worktree-sprawl
description: "Worktrees are isolation, not storage - doctrine/docs/skills merge to main IMMEDIATELY; stage-complete layers merge when the stage completes, not when the episode ships"
metadata: 
  node_type: memory
  type: project
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-08-31T09:05:58.355Z
---

**The durable rule:** doctrine/docs/skills commits merge to main
IMMEDIATELY, separate from episode content. When an episode stage
completes (script locked, evidence built, table authored), that layer
merges. Worktrees are isolation, not storage.

Counts of unmerged work go stale fast - `survey_worktrees.py`
regenerates docs/STATE-OF-WORK.md; run it instead of trusting any
remembered census. (2026-08-29 harvest: sweet-villani + p31 + p16
merged to main; big player.html blobs must be STRIPPED before pushing -
filter-branch was needed once for 81-367MB blobs; keep build outputs
out of pushes.)

Related: [recall-system](recall-system.md), [worktree-read-scope](worktree-read-scope.md).
