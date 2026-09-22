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

Counts of unmerged work go stale fast - `git worktree list` and
`git log main..<branch>` are the census, `docs/WORKTREE-REGISTER.md`
the board (P62); never trust a remembered census. (2026-08-29 harvest: sweet-villani + p31 + p16
merged to main; big player.html blobs must be STRIPPED before pushing -
filter-branch was needed once for 81-367MB blobs; keep build outputs
out of pushes.)

Related: [recall-system](recall-system.md), [worktree-read-scope](worktree-read-scope.md).

**AMENDED 2026-09-15 (E99 s47):** the operator: "work has to be parallel ... worktrees with both agents aware of each worktree, and accept that there will be sprawl at times until things get sent back to main." Worktrees are allowed for a second agent on its own episode or an adversarial pass; the cost is paid with AWARENESS - a tracked worktree register (path, branch, base, engine sha, owner, purpose, last merge) every agent reads at start and updates at every commit - and a merge-back cadence. P62 = that register, not saved states. Sprawl is accepted when the register names it.

**P62 SHIPPED 2026-09-16 - the simple form.** The operator on the eight-slice draft (a generated board, a claim hook, union merges, hardlinks): *"this is sounding way too complex. isn't a better way to just check git before pushing to main and always preferring non-destructive methods?"* So: the lane register became the hand table `docs/WORKTREE-REGISTER.md` (one row per checkout, a ruling number claimed there before it is written), the six-step merge-before-main checklist lives in `PRP_EXECUTION.md` "Worktrees and lanes" and the steward (merge main in, run the register + golden tests, keep both sides on record-file conflicts, fast-forward; never force / amend-after-push / delete without the word), and `test_worktree_register.py` fails a merge on a duplicate number or an unregistered worktree. A second agent (Astra) gets `git worktree add <path> -b <lane>/<slug> main` - a worktree, never a clone. The rejected draft and its 18-finding review: session scratchpad `assembly/P62-REVIEW.md`.

**2026-09-22, the sprawl's worst form and its fix.** Friday's hand-off named a stable sha and left it at that; no
worktree was created for either lane. Astra then worked for three nights INSIDE the main checkout - which it had
switched to `codex/Astra` - and committed nothing, so 65 tracked files from three lanes (the parent's hygiene wave,
a Codex tooling lane, Astra's own) sat mixed in one tree with the trunk unreachable and `main` 72 commits unpushed.
It also recompiled `build-f`, the reference cut. **A hand-off is not a sha; it is a worktree that exists and builds.**
The fix that works: `git worktree add .claude/worktrees/<lane> -b <branch> main`, then COPY the gitignored build
inputs in (the take's mp3, the evidence objects, the host plates, the props, the icons, the sound bed, the plate
claim dirs under `review/claims/` - about 900 MB), then RUN the project's own build there and read its gate before
calling the lane real. Plate ids resolve by ABSOLUTE path into the main checkout, so reading plates works from any
worktree; anything ffmpeg opens by repo-relative path does not.
