---
name: scratch-trees-die-on-commit
description: "lane-B slice agents each export a full repo tree (+ base + H-door copy) into the scratchpad; 70 of them filled C: to 98% - delete a slice's tree/base/hdoor dirs the moment its commit lands"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-25T03:48:03.213Z
---

On 2026-09-24 C: hit 98% (21 GB free). Deleting the `tree/`, `base*/`, `hdoor*/` export dirs of ~35 already-committed P69/P70 slices in the session scratchpad freed **171 GB** (-> 192 GB free). Each lane-B slice agent (`git archive <sha> | tar -x` + forced gitignored inputs + a door copy) leaves 2-5 GB behind.

**Why:** the operator: "we need to do something about the local disk sprawl of assets, especially duplicate worktree generated assets". The exports are fully reproducible from git + the input lists, so keeping them buys nothing.

**How to apply:** after release_steward returns a slice's commit sha, `rm -rf` that slice's `$SP/<slice>/{tree*,base*,hdoor*,work*}` (keep NOTES.md, logs/, scripts/, frames/, the patch). Never touch a running agent's dir. A disk audit + a shared hash-named asset store for worktree-generated assets was commissioned the same night (see [worktree-sprawl](worktree-sprawl.md), [gitignored-artifacts-live-in-worktree](gitignored-artifacts-live-in-worktree.md)).

**Slip, 2026-09-25:** I deleted `p71-t3/tree` + `hdoor` right after T3 committed, while T3b (a follow-up slice) was still running IN those dirs - its round-2 edits were lost. Before any rm, check the slice has no live follow-up/agent (a slice that spawned "T<n>b" keeps its tree until the follow-up returns); `rm` reporting "Device or resource busy" means an agent is inside - stop, do not retry.
