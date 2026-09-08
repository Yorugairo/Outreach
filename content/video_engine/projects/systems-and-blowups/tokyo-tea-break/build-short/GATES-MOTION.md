# MOTION GATE — build-short

```text
=== MOTION DENSITY GATE: projects\systems-and-blowups\tokyo-tea-break\build-short ===
               runtime: 1:28
         visual_events: 305 (206.0/min)
                 docks: 5
           dock_source: timeline
          ledger_pages: 4
  still_over_12s_share: 0%
            per_minute: 0:00:216/5 1:00:183/8

  [WARN ] M11 first chart ledger:s02 enters at 2.0s, its build lands at 10.7s, with build_to landing on datum 311 at 10.7s (the cap is the annotation: the line ends on the datum); WARN no sound cue within 1.5s of the enter at 2.0s; window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [PASS ] M01 longest still stretch 1.1s at 0:28
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 27s from 0:09
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 7 distinct plates; target runtime/12s = 7
          doc 29 s9.13 plate density
  [PASS ] M05 no plate over the 20s hold ceiling
          doc 29 s9.13 hard ceiling
  [PASS ] M06 53 caption pages = 36/min, 4.5 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M10 no still stretch > 6s begins in the first 60s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [PASS ] M16 longest gap between visual events 1.1s at 0:28; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [PASS ] M18 no run of bit-identical frames over 0.50s (1066 frames at 12 fps, 0:00-1:28); longest 0.00s at 0:00
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py)
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 216.0 events/min, 5.0 evidence entries/min; tail from 1:00 183.2/min; whole runtime 204.7/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M19 2 build_to hold(s) - the line rests at a datum until the next word: 0:10+8.3s, 0:20+5.4s
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M20 3 arrival(s): dock-c-blue-ties-panel throw ~1188 px/s -> on 1s; dock-g-two-fingers land (metal) - weight sold 0.32s before the impact; dock-h-fed-vs-yields throw ~1386 px/s -> on 1s
          P47 T1 (the brief :185-193, the cadence rule): a throw steps on 1s above 250 px/s, on 2s below - reported, not scored, until HG2 tunes it
  [INFO ] M21 1 page(s) deployed 8-12s after the last data mark (a dock's clip may hold it): s02 12.0s (0:26 -> 0:38)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 0 FAIL / 1 WARN / 14 PASS / 1 JUDGE / 4 INFO
```

TIMELINE: tokyo-short.timeline.json sha256:6794ef6f3b6498e5afa9166c3377e7f40a7a7e918b464029172add3f28cbae9d
VERDICT: PASS (0 FAIL)
