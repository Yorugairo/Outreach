---
name: thresholds-from-the-reference
description: "A production threshold is measured on the reference that works (Wealth Logic), then compared to ours - never derived from our own practice, which is the thing under suspicion"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 45114c3b-258a-4ca8-9aaf-b674a804cc7e
  modified: 2026-09-05T04:12:41.483Z
---

Operator, 2026-09-04, when P40 T1 proposed settling the cut-gap threshold from ep1's own
word timeline: *"Is basing the gap threshold off our own work really the right way? I think
we should check Wealth Logic's gap threshold and compare against ours."*

**Why:** our practice is what the retention data says is failing; a threshold fitted to it
just formalises the failure. The reference's practice is the only measured success we hold.
Done that way the answer came out different from BOTH research reports: 0.30 s (not 0.45),
cut at ~0.8 of the gap (not onset, not midpoint), and we had *more* usable gaps than the
reference - we just ignored them (46 §46.3).

**How to apply:** for any rhythm / density / placement number, measure the reference first
with the same tool (its audio via `yt-dlp` -> local `faster_whisper small.en` word
timestamps; its cuts from the frame-accurate ledger `04_shot_ledger_100_cuts.md`), then run
ours through the same aligner before comparing - mixing aligners produced a false "we have
fewer pauses" read. Script: `content/video_engine/scripts/measure_cut_gaps.py`. Reference
words are committed beside the (gitignored) audio. See [our-artifacts-beat-outside-advice](our-artifacts-beat-outside-advice.md),
[youtube-retention-clock](youtube-retention-clock.md).
