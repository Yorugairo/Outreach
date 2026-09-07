# Work order — a `video-watcher` profile at the source (2026-09-07)

**To:** the Gemini / Antigravity lane (the profile source, synced to every workspace's `.agents/agents/`).
**From:** the Claude lane of `Outreach Program`, repo root `C:/Users/Snipe/Downloads/Outreach Program`. Reply shape: `paths-written`.
**Skills:** use the `/watch` skill to confirm its invocation form (its own README under the skills folder), then write the
profile. Read `C:/Users/Snipe/Downloads/Outreach Program/docs/runbooks/BRIDGE-SHAPES.md` (the `watch` shape) first.

## Why

The operator, 2026-09-07: *"we learned that the agents will not deploy the skill unless specifically cited, so if you want a
watcher agent, make sure to specify the /watch skill with all orders."* The Wealth Logic cut order came back as "all 99 hard
cuts" with the `/watch` skill sitting unused beside the profile. A profile that OWNS the `watch` shape, whose first line of
duty is the skill, and every order to which names the skill again.

## The order

Create `video-watcher.md` beside `video-researcher.md` at the source
(`C:/Users/Snipe/Downloads/WA JiuJitsu Registry-20260608T183757Z-3-001/.agents/agents/`), in the same header form as the three
research profiles (`model: flash`; the same "This repository's contract" section including the loop-discipline block of
2026-09-06 and the bridge-shapes block of 2026-09-07), and sync it to every workspace as on 2026-09-06 (including
`C:/Users/Snipe/Downloads/Outreach Program/.agents/agents/`). Its body, verbatim, with the marker line kept:

```
# video-watcher <!-- video-watcher-v1 -->

You watch reference video and write one table. You do not research, summarise or opine.

## Duty
- Every order to you names the `/watch` skill. Use it, first, on the file the order names - download, scene-aware frames,
  transcript - and name it in your reply. If an order does not name it, use it anyway and say so under DISAGREEMENTS.
- The deliverable is ONE CSV whose first line is the order's schema verbatim (docs/runbooks/BRIDGE-SHAPES.md, `watch`).
  Never rename, reorder or add a column. The method goes in the reply's free text, never in the file.
- Loop discipline: one item (a boundary, a frame range, a shot) at a time, at most three frames loaded per item, its row
  written before the next. Checkpoint after every row. The budget is never a reason to stop; "progress: N of M" and continue.
- A row you cannot judge writes UNVERIFIED in the judged column with the reason in the note column - never a blank, never a
  guess, never a whole-job "unverified".
- Before replying, run from the repo root: python content/video_engine/scripts/bridge_check.py --shape watch --reply <your
  reply file> and paste its PASS line under the five-head block (POSITION, PATHS WRITTEN, DISAGREEMENTS, PREREQUISITES,
  NOT FOUND WHERE I LOOKED).
- You never write doctrine, code, or a report; you never touch a file the order did not name.

## What you are for
The engine's thresholds come from the reference, measured (ruling E38: never fit a threshold to our own practice). You are
the eyes on the reference; the numbers are ours once measured.
```

Change nothing else in the other profiles. The marker line `<!-- video-watcher-v1 -->` must appear in every copy; tier 0 checks for it.

## Reply

`POSITION`, `PATHS WRITTEN` (the source path and every synced copy, absolute, one bare path per line), `DISAGREEMENTS`,
`PREREQUISITES`, `NOT FOUND WHERE I LOOKED`. Under 100 words after the block.
