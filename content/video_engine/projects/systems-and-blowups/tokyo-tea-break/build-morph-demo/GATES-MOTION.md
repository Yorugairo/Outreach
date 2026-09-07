# MOTION GATE — build-morph-demo

```text
=== MOTION DENSITY GATE: content\video_engine\projects\systems-and-blowups\tokyo-tea-break\build-morph-demo ===
               runtime: 1:28
         visual_events: 297 (200.6/min)
                 docks: 4
           dock_source: timeline
          ledger_pages: 4
  still_over_12s_share: 0%
            per_minute: 0:00:211/6 1:00:177/4

  [FAIL ] M11 first chart enters full and unannotated - declare a spotlight/callout/punch on its divergence within 1.5s AFTER the page's build lands at 7.0s (never over the build); WARN no sound cue within 1.5s of the enter at 2.0s; window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [PASS ] M01 longest still stretch 1.3s at 0:26
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 21s from 0:15
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 8 distinct plates; target runtime/12s = 7
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
  [PASS ] M16 longest gap between visual events 1.3s at 0:26; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [PASS ] M17 s02: centroid 0.1 % W, axis 0.0 deg, area 0.69, min det 0.056
          P47 T3 / the brief B4 [DERIVED: :390-396]: a morph reads as one thing changing when its centroid moves <= 6 % of W, its dominant axis turns <= 15 deg and its bounding area keeps >= 60 % - measured in the player by measure_morph.py
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 211.0 events/min, 6.0 evidence entries/min; tail from 1:00 176.9/min; whole runtime 199.3/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py)
  [INFO ] M19 1 build_to hold(s) - the line rests at a datum until the next word: 0:10+8.3s
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M20 2 arrival(s): dock-c-blue-ties-panel throw ~1188 px/s -> on 1s; dock-g-two-fingers land (metal) - weight sold 0.32s before the impact
          P47 T1 (the brief :185-193, the cadence rule): a throw steps on 1s above 250 px/s, on 2s below - reported, not scored, until HG2 tunes it
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 1 FAIL / 0 WARN / 14 PASS / 1 JUDGE / 4 INFO
```

TIMELINE: tokyo-morph-demo.timeline.json sha256:34107474e3402b1ac58813055ce06dca7799349bb2a62de3a49c75d6c6d837bd
VERDICT: FAIL (1 FAIL)
