---
name: rulings-need-carriers
description: "09-23: an approved build (the membership stack, s101) sat as a ruling with no slice or backlog row; five more were found. Every ruling that asks for a build names its slice/row in the SAME commit"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-23T22:51:33.978Z
---

The operator, finding the membership stack (E99 s101) approved but built nowhere: "why did we drop that build or backlog? that makes me concerned that we dropped the other stuff from that review which was important". The audit found five more unslotted approvals (s109 schematics, rings on every vertex, the 3D exploded pie; s99 freeze beat; s100 area forms) and drift where slices and the use-when guide still carried the OLD refusals.

**Why:** rulings don't feed the plan by themselves, and guides that slices copy from go stale the moment a ruling overturns them - so approvals silently die or get re-refused.

**How to apply:** when writing a ruling that asks for anything built/changed/decided, add its carrier (a plan slice or backlog row) and a row in the plan's "Ruling coverage" table in the SAME edit; update any guide it overturns (BRAVOS-USE-WHEN, the harvest conflicts) at once; re-run the ruling-coverage audit before each lane merge. Related: [check-rulings-before-asking](check-rulings-before-asking.md), [engine-advises-author-decides](engine-advises-author-decides.md).
