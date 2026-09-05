# MOTION GATE — build-short

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\tokyo-tea-break\build-short ===
               runtime: 1:28
         visual_events: 135 (91.2/min)
                 docks: 0
           dock_source: evidence-dock.json
          ledger_pages: 3
  still_over_12s_share: 0%
            per_minute: 0:00:105/2 1:00:60/2

  [FAIL ] M16 longest gap between visual events 3.0s at 0:12; 4 gap(s) over 2.5s: 0:02+2.9s, 0:12+3.0s, 0:35+2.7s, 1:16+2.5s - add motion there (a species, a caption pop, plate life); never cut motion to pass
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [WARN ] M06 35 caption pages = 24/min, 6.7 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M01 longest still stretch 3.0s at 0:12
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 28s from 0:17 (no docks at all)
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 11 distinct plates; target runtime/12s = 7
          doc 29 s9.13 plate density
  [PASS ] M05 no plate over the 20s hold ceiling
          doc 29 s9.13 hard ceiling
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M10 no still stretch > 6s begins in the first 60s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s
  [PASS ] M11 first chart ledger:s04 enters at 17.2s, its build lands at 24.6s, with spotlight at 25.6s (no evidence species in the timeline - every dock treated as a chart candidate)
          E24 / doc 29 s9.29: the first chart enters 0:08-0:20, annotated on its divergence, with a sound cue
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 105.0 events/min, 2.0 evidence entries/min; tail from 1:00 60.4/min; whole runtime 89.8/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 1 FAIL / 1 WARN / 12 PASS / 1 JUDGE / 1 INFO
```

TIMELINE: tokyo-short.timeline.json sha256:22a6cba36db9c818f10108dd7ef8c6209aaae22b2376ed036d33a9b1bcfebc74
VERDICT: FAIL (1 FAIL)
