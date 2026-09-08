# MOTION GATE — build-short

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\japan-tariff-trick\build-short ===
               runtime: 1:29
         visual_events: 311 (208.8/min)
                 docks: 6
           dock_source: timeline
          ledger_pages: 5
  still_over_12s_share: 0%
            per_minute: 0:00:223/7 1:00:178/8

  [WARN ] M06 62 caption pages = 42/min, 4.0 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M01 longest still stretch 2.3s at 0:28
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 16s from 0:01
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 12 distinct plates; target runtime/12s = 7
          doc 29 s9.13 plate density
  [PASS ] M05 no plate over the 20s hold ceiling
          doc 29 s9.13 hard ceiling
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M10 no still stretch > 6s begins in the first 60s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s
  [PASS ] M11 first chart ledger:s02 enters at 1.8s, its build lands at 1.8s, with spotlight at 2.7s; window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [PASS ] M16 longest gap between visual events 2.3s at 0:28; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 223.0 events/min, 7.0 evidence entries/min; tail from 1:00 177.8/min; whole runtime 207.5/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py)
  [INFO ] M19 build_to caps declared; none holds between caps
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M20 2 arrival(s): dock-b-holdings throw ~2479 px/s -> on 1s; dock-g-receipt throw ~2479 px/s -> on 1s
          P47 T1 (the brief :185-193, the cadence rule): a throw steps on 1s above 250 px/s, on 2s below - reported, not scored, until HG2 tunes it
  [INFO ] M21 2 page(s) deployed 8-12s after the last data mark (a dock's clip may hold it): s02 10.0s (0:01 -> 0:11); s06 10.8s (0:36 -> 0:47)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 0 FAIL / 1 WARN / 13 PASS / 1 JUDGE / 5 INFO
```

TIMELINE: japan-short.timeline.json sha256:02bcfc0f1e2a3c90b84ff1274d4db42fbdd699a7bd9a1d0534ea0248a7d0a7a9
VERDICT: PASS (0 FAIL)
