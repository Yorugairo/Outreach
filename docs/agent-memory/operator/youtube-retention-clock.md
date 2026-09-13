---
name: youtube-retention-clock
description: "Operator's retention doctrine for all YouTube scripts — 3s hook, 10s answer, 30s promise, then repeat the cycle"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-02T22:06:05.392Z
---

The operator's retention grammar for every YouTube script (stated 2026-08-24,
during the Alicia recreation):

- **0–3s: the hook itself** — the grab must be the first sentence. No
  atmosphere, no timestamps, no scene-setting first.
- **by 10s: answer it** — resolve the initial grab enough to prove the video
  keeps its promises.
- **by 30s: promise the payout** — an explicit reason to stay (the open loop,
  named).
- **then the cycle repeats per beat**: hook, show it's worth it, promise
  more, deliver — "over and over again."

**Why:** hooks judged on the page pass reviews and fail by ear; the operator
caught two consecutive hooks (memoir-register, then atmosphere-first) that
both my review and the extracted AOY rubric passed.

**How to apply:** write hooks as shot lists to this clock; time the beats
against synthesized audio, not word counts; every script section should carry
its own micro-cycle, not just the cold open.

**It is a GATE now (2026-09-02):** `content/video_engine/scripts/
gate_opening_structure.py` enforces this clock and the whole doc-38 / P1 / P2
opening shape (36 gates, exit 1) - run it before recording, and with
`--timeline` after. It exists because Steel and Paper's promise landed at 1:20
against a 0:30-0:60 window with only a "by hand" roster row to stop it, and
the first impression-viewer left at 0:56. Operator: "the structure of the
first 1-2 minutes is going to matter more than anything." Undeclared required
beats FAIL; JUDGE rows are printed for a reader, never auto-passed. Related: the hook rule in
`alicia-recreation-brief` (not yet written) (docs/content-video-engine/briefs/ALICIA-FORMAT-RECREATION-BRIEF.md).
