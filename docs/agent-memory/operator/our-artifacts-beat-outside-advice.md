---
name: our-artifacts-beat-outside-advice
description: "Check our own artifacts before trusting a tutorial, a research pass, or my own recollection — four errors in one day all had this shape"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-04T23:13:30.758Z
---

**Before recording an external claim as a finding, grep our own artifacts for the answer.**
On 2026-09-04 I made four errors with the same shape, each caught by the operator asking one
question:

| I claimed | the artifact said | the check I skipped |
|---|---|---|
| Omni animation prompts use a field schema (from a tutorial) | our working prompt is **768 chars, zero newlines, no fields** — prose, and it shipped | read one `_meta.json` |
| our doctrine target is 145–165 WPM | **no such target exists** — every citation traced back to a line I wrote that morning; the real number is 140, an *estimation constant* | `grep` for its origin |
| M10 measures shot length and is broken | it measures **gaps between visual events**, and shot length has its own separate ceiling | read `gate_motion_density.py:277` |
| the tutorial's CHARACTER LOCK answers our identity problem | `@Mike` is **already bound** and exercised on motion in Tokyo | `grep @Mike` in the project metadata |

**Why:** outside sources arrive as prose *about* a subject, which reads as more
authoritative than a JSON file — but the JSON file is evidence and the prose is advice. And
a number I wrote earlier the same day looks, by afternoon, exactly like a number I read
somewhere. **A citation loop with nothing at the centre is invisible from the inside.**

**How to apply:** when an external doc says how something should be done, first check
whether we already do it and what happened. When quoting *any* internal number as doctrine,
`grep` for its origin before citing it — if every hit is a doc I wrote, it is not doctrine.
The operator's question *"where does that come from?"* is the check; run it unprompted.

Related: [recall-system](recall-system.md) (enumerate before you grep), [ai-baselines-operator-corrects](ai-baselines-operator-corrects.md).
