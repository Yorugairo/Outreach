---
name: nearby-tests-miss-regressions
description: "per-merge \"nearby test files\" checks let test_prop_shadow fail unseen for ~50 lane-B commits; sweep the whole suite per wave"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-26T15:08:05.363Z
---

P70 T1b (`50b2f85`, the gold seal) broke `test_prop_shadow`'s contact-to-hatch handover: the weight dips to 0.870 against a 0.95 floor. It failed silently across ~50 lane-B commits, found 09-26 only because an agent reported it as "fails at base too" and I bisected. It was filed as R26-400.

**Why:** each merge ran the slice's own tests, the files near the change and the full goldens, never the whole Python and node suite. A "fails the same at base" note from an agent was accepted as environmental without dating it.

**How to apply:** after each wave lands, and before any push, run every test file at the lane head, each in its own process, sequentially, as a background sweep. When an agent says a failure "also fails at base", date it (bisect, or run it at an older head) before accepting that. Pairs with [never-pipe-gated-steps-to-tail](never-pipe-gated-steps-to-tail.md) and [grammar-change-runs-authoring-tests](grammar-change-runs-authoring-tests.md).
