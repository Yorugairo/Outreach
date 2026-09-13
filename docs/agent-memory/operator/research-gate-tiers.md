---
name: research-gate-tiers
description: "A lane's research is gated into CONFIRMED / PLAUSIBLE / UNSOURCED-editorial / REJECTED before any of it is used, and a passing provenance audit is not the same as a source on disk"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-08T01:53:30.392Z
---

Gate every research drop into four tiers before acting on it, and say which tier each claim sits in: **CONFIRMED** (a real
citable source, independently checkable), **PLAUSIBLE** (the substance holds but the attribution is second-hand), **UNSOURCED
- editorial** (the lane's own reasoning, useful as a checklist, never quotable as a finding), **REJECTED** (out of our stack
or contrary to our own doctrine).

**Why:** `audit_research_provenance.py` PASSING is not the same as a source being on disk. The macro-chart drop (2026-09-07)
passed with zero failures and ten valid anchors, but every anchor pointed at the lane's own SUMMARY of a page, not the page -
a research order's shape, not a `fetch` order's. That is fine, and it sets the claim strength below the weight-and-mass
report, whose eight sources are on disk with hashes. In the same drop: the Cleveland & McGill hierarchy was real and
load-bearing; "the Economist's standards" were cited to a third-party design blog; the Bloomberg palette and the whole
"LLM failure modes" table carried no source line at all; the hex palette and the matplotlib template were rejected outright
(our palette is the brand sheet, and we do not render pages with matplotlib - the MECHANISMS port, the code does not).

**How to apply:** name the tier per claim in the intake page, then triage into priority / doctrine / backlog / explore /
index with our nearest existing capability named for each row. Where a rule is contested later, the fix is a `fetch` order
that puts the page on disk with a sha256. Also: read a finding against what we shipped THAT DAY - the drop's strongest rule
(a detached legend costs saccades) contradicted a fix I had made hours earlier, and the research's own dual-axis advice
("lock the zeros") was wrong for our case and had to be corrected in the intake so the next reader does not apply it blind.
Related: [our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md), [steal-now-harvest-not-replace](steal-now-harvest-not-replace.md), [thresholds-from-the-reference](thresholds-from-the-reference.md).
