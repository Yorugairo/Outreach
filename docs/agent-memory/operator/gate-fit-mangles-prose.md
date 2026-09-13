---
name: gate-fit-mangles-prose
description: "Tokyo rewrite 2026-09-04: fitting clear sentences into the pinned P1 0:35 / P2 1:05 windows clipped them until the operator said 'your sentences don't even make sense'; write for sense, move beats not words; a clear cut that clears every long-form gate lands ~2:20, not 60 s - G2 short mode shipped 2026-09-05 (E41); Powell is no longer Fed chair"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-13T09:37:07.968Z
---

Operator, 2026-09-04, on the Tokyo rewrite (v3): *"your sentences don't even make sense"*,
then *"we need a complete re-write, not trying to hold on to the original."* Earlier the same
day: *"from our debt" is bad writing*, *"Japan's holdings" is unclear* (say American debt),
and *no commitment to Japan buying again* (their chip build-out may pay more than a 2 %
trade). Also: **Jerome Powell is no longer Fed chair** - write "the Fed chair" / "anyone at
the Fed", never the name.

**Why:** `gate_opening_structure.py` pins P1 at 0:35 and P2 at 0:35-1:05 below five
minutes; G18 + G12 leave a two-second slot for the promise, and P2 wants seven beats in
30 s. I hit the windows by clipping words ("Treasury's own table: Japan holds... selling
since February") and the prose stopped making sense. STRENGTH-LOOP precedence is
comprehension > structure > line-craft; I inverted it.

**How to apply:** write the sentence that makes sense first; fit a window by MOVING a beat
(merge tags onto the sentence that already carries it, reorder), never by deleting the
words that make the sentence a sentence. When a window cannot be met without clipping,
report it as a geometry finding (G2) and a DECISION, not as prose. A clean short that
clears G01-G45 lands ~2:15-2:25; a 45-60 s short cannot pass the long-form gate. **CLOSED 2026-09-05:**
G2 short mode shipped (`run_short`, S01-S08 + J50/J51; a measured clock under 3:00 routes by itself, `--short/--long`),
the ruling is E41 in OPERATOR-RULINGS, and the script skill (P44) cites it - run the runner with `--timeline`, never
fit a short to P1/P2. Arms are
kept as separate files (`SCRIPT-90S-VO.claude.txt` vs Gemini's `SCRIPT-90S-VO.txt`) -
Gemini writes into the canonical path concurrently, so never edit that file. See
[our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md), [viewer-perception-test](viewer-perception-test.md).

**Read the gate's source before fitting prose to its message (2026-09-07, P54 value pass K22):** editing a script
against a gate's printed message instead of the gate's own definition made two of six remaining FAILs self-inflicted,
and a "gate defect" claim had to be retracted when a token swap moved the result. Open the gate's code (the row's
regex, window, stems) first; only then decide whether the sentence or the gate is wrong.
