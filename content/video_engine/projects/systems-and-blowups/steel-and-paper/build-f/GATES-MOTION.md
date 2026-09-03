# MOTION GATE — build-f

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\.claude\worktrees\sweet-villani-1c3a16\content\video_engine\projects\systems-and-blowups\steel-and-paper\build-f ===
               runtime: 13:26
         visual_events: 375 (27.9/min)
                 docks: 43
           dock_source: timeline
          ledger_pages: 0
  still_over_12s_share: 12%
            per_minute: 0:00:19/2 1:00:39/3 2:00:13/2 3:00:36/2 4:00:40/2 5:00:23/4 6:00:32/3 7:00:30/5 8:00:15/1 9:00:34/7 10:00:28/4 11:00:28/4 12:00:19/4 13:00:41/0

  [FAIL ] M01 6 stretches > 12s with no visual event beyond Ken Burns/anchor captions (94s = 12% of runtime); worst 17.7s at 2:24
          doc 29 s8.19 / s9.25 stillness ceiling
  [FAIL ] M03 longest wait for evidence to enter: 54s from 2:52
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [FAIL ] M05 2 plates held > 20s without two docks over them; worst world-gpu-crate-dock-v1 21s at 0:29
          doc 29 s9.13 hard ceiling
  [FAIL ] M07 opening minute: 19.0 events/min, 2.0 docks/min - rank 3/14 from the bottom; episode median 29.0/min
          E21: the opening is the densest minute, never the thinnest
  [FAIL ] M08 6 still stretches > 12s carry no stage-mode caption: 0:33+16s, 0:57+14s, 2:24+18s, 6:53+15s, 8:14+16s, 12:24+15s
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)
  [WARN ] M02 17 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M04 73 distinct plates; target runtime/12s = 67
          doc 29 s9.13 plate density
  [PASS ] M06 464 caption pages = 35/min, 5.3 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 5 FAIL / 1 WARN / 3 PASS / 1 JUDGE / 0 INFO
```

VERDICT: FAIL (5 FAIL)
