---
name: notebooklm-omni-opener
description: NotebookLM videos get a ~10s generated (Omni) opener so the hook line is rewritable and the first 10s has motion
metadata:
  type: project
---

Operator rule 2026-09-02, **applies from the NEXT short onward** — the Japan
chips short ships with its 6s hook and is the measured baseline, not a
rework target. On the NotebookLM → Facebook/YouTube short lane,
**cover the first ~10 seconds with generated footage (Gemini Omni), when
plausible.** Trim the NotebookLM picture from that window entirely.

**Why:** NotebookLM burns its word-plates into the picture, which locks the
narration to the frames. Retention data on the Japan chips short (n=238)
showed the tail improved 3x from pacing/audio work but the curve still lost
half the audience by 0:05 — the opener line was the wall, and it couldn't be
changed while NotebookLM's plates were under it. Generated footage over 0-10s
makes the opener freely rewritable (plates re-burned from the new words) and
gives the kill-zone motion instead of a static illustration. 10s = the
retention clock's hook (3s) + answer (10s) both under controllable footage.

**How to apply:** COMPRESS FIRST. Tighten inter-phrase gaps and apply speed
(pass 1) before quoting or deciding ANY timing — hook window, seams, plate
chunks, beats. Every number is on the recut timeline; never the source's
(operator correction 2026-09-02). Hook window ends on an existing scene change in the
recut (10.1s on the Japan short). Reverse-trick for the end frame (generate a
push-in FROM the handoff frame, reverse it). Two clips beat one 10s clip —
a pull-back reveal then a second beat that lands on the NotebookLM frame.
Opener line: ~25 words, most provocative claim inside 3s, fitted to the
window in the ship voice via ElevenLabs TTS. Pipeline: `scratchpad/recut`
+ `scratchpad/hook` (HOOK_LEN param). See [voice-lane-split](voice-lane-split.md),
[youtube-retention-clock](youtube-retention-clock.md).
