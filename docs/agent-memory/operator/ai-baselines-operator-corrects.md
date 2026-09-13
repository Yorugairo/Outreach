---
name: ai-baselines-operator-corrects
description: Operator standing order (2026-09-03) - never hand the operator work items; the AI produces the baseline for everything (including JUDGE rows and by-hand roster checks) and the operator corrects it
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-03T10:24:30.353Z
---

Operator, 2026-09-03, after I listed "adjudicate the seven JUDGE rows" as a
step for them: *"And no, we don't ask me to do the work. AI always baseline,
I correct if needed."*

**Why:** the operator's time is the scarce input and correction is cheaper
than authorship. A plan step addressed to them is a stall; a baseline they
can react to is progress. This is also why the still-image channel outruns
us - their loop never waits on a human to produce something.

**How to apply:** every deliverable ships as a completed draft, never as a
request. That explicitly includes the things the docs call "by hand" or
"the agent's own verdict" - the JUDGE rows in
`CHECK-RESPONSIBILITIES.md` §3, the duty-roster rows the checkers do not
cover, contact-sheet reads, and pick recommendations. Put a recommendation
on every DECISION rather than an open question; ask only when proceeding
either way would be unsafe or waste real spend (a paid render, a push).
See [cause-outcome-brevity](cause-outcome-brevity.md), [package-first-e27](package-first-e27.md).
