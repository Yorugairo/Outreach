# MOTION GATE — build-short

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\tokyo-tea-break\build-short ===
               runtime: 1:28
         visual_events: 330 (222.9/min)
                 docks: 0
           dock_source: evidence-dock.json
          ledger_pages: 3
  still_over_12s_share: 0%
            per_minute: 0:00:247/2 1:00:171/2

  [PASS ] M01 longest still stretch 1.3s at 0:26
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 28s from 0:17 (no docks at all)
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 11 distinct plates; target runtime/12s = 7
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
  [PASS ] M11 first chart ledger:s04 enters at 17.2s, its build lands at 24.6s, with spotlight at 25.6s (no evidence species in the timeline - every dock treated as a chart candidate)
          E24 / doc 29 s9.29: the first chart enters 0:08-0:20, annotated on its divergence, with a sound cue
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [PASS ] M16 longest gap between visual events 1.3s at 0:26; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [INFO ] M07 short: 1 full minute(s) in 89s - opening 247.0 events/min, 2.0 evidence entries/min; tail from 1:00 170.7/min; whole runtime 221.6/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 0 FAIL / 0 WARN / 14 PASS / 1 JUDGE / 1 INFO
```

TIMELINE: tokyo-short.timeline.json sha256:32ed0b05544b7b09867f88dfc1d1f68d1a3eccd2b0cb3aa16b1ddd72e78d8ade
VERDICT: PASS (0 FAIL)
