---
name: chart-reads-at-a-glance-e28
description: "Ruling E28 (2026-09-03) - a chart must read right at first glance: the sign is geometry (drops go down), a selected date axis states its rule on the page, the first-glance read is the viewer's (P36) job"
metadata:
  type: feedback
---

Operator, 2026-09-03, on the trim-proof page rendered with magnitude bars
and the sign only in a note/colour: "every bar appears to be positive at a
glance, and the negative move is the tallest bar ... the dates are total
nonsense ... this chart tells no story." It was the real series file; the
representation was backwards and the selection (8 weak prints in 25
months) was unstated.

**Why:** the chart is the proof of one sentence (E25); a proof the eye
reads backwards disproves the sentence. Data correctness is not chart
correctness.

**How to apply:** values are SIGNED in series files (never magnitude +
signed note); `ledger_page.validate` FAILs sign-in-note; uneven date
axes raise a `[JUDGE]` row naming the gaps and the file's `selection`
rule, and the sub must say it on the page; when reviewing any chart,
read it as a stranger for two seconds first and say what it says before
checking the numbers. See [chart-proof-not-homework](chart-proof-not-homework.md),
[ledger-page-signature](ledger-page-signature.md).
