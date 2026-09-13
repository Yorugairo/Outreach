---
name: recall-before-propose
description: "Before proposing ANY mechanism (transition, arrival, camera, chart form), run docs_find on its nouns and quote the hits - the operator caught a full day of re-deriving what the record held (2026-09-08)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-08T22:27:36.263Z
---

Run `python content/video_engine/scripts/docs_find.py "<noun>"` for every noun in a proposal BEFORE proposing it, and
quote the hit (path:line) in the proposal. Never design from recollection or from the code in front of you alone.

**Why:** 2026-09-08 the operator asked "how come you just now found all of that research/doc information? the whole
point of making this information retrieval cheap and easy was to get you to use it." A day of transition work re-derived
things the record already held: the wipe was retired (E47), the throw-then-snap was the third watch (P47 T7), the camera
was in doc 16's contract, C3/doc 43, HyperFrames Rule 2, D1 and doc 24 - four times over - and I proposed each as if new.
The fast route in CLAUDE.md ("never say we don't have it before the manifest grep") only fires on "do we have X?"; it
did not fire on "let's build X". The failure is at the moment of PROPOSING, not of answering.

**How to apply:** the receipt is the gate. (1) Any message that proposes a mechanism carries a "Recall:" line with the
docs_find hits (or "docs_find: 0 hits for <term>") before the proposal. (2) Any commit touching the player template,
`kinetics/`, `build_scene_timeline_f.py` or a `build_short.py` shot table cites the record it integrates
(`Recall: <path>:<line>`) - the commit-msg hook `.git/hooks/commit-msg` -> `scripts/hooks/recall_receipt.py` is INSTALLED (2026-09-08),
shared by main and every worktree, and refuses the commit. (3) The grill-me Stage 2 spike is the DOCS first (`docs_find`, TRANSITIONS-REVIEW, the rulings),
the web only after. Related: [our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md), [recall-system](recall-system.md), [docs-layers-and-registries](docs-layers-and-registries.md).
