# MOTION GATE — build-f

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\steel-and-paper\build-f ===
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
  [FAIL ] M10 3 still stretches > 6s begin in the first 60s: 0:16+10s, 0:33+16s, 0:57+14s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s
  [FAIL ] M11 first chart enters full and unannotated - declare a spotlight/callout/punch on its divergence; WARN no sound cue within 1.5s of the enter at 9.5s
          E24 / doc 29 s9.29: the first chart enters 0:08-0:20, annotated on its divergence, with a sound cue
  [FAIL ] M12 25 chart docks held as homework: ev-bravos-original-v1 0:09-0:50 crosses 2 scene boundaries (world-adviser-signature-v1 -> world-share-office-queue-v1 -> world-gpu-crate-dock-v1), hold 40.9s > 6s (opening minute); ev-divergence-v1 0:50-1:10 crosses 1 scene boundaries (world-statement-kitchen -> world-three-notch-slate-v1), hold 20.5s > 6s (opening minute); ev-capital-formation-v1 2:02-2:52 crosses 2 scene boundaries (world-ledger-page-v1 -> world-pressure-gauge-v1 -> world-viaduct-train-rain-v1), hold 50.1s > 10s; ev-tnx-two-eras-v3 2:52-3:10 crosses 1 scene boundaries (world-viaduct-train-rain-v1 -> world-broadcast-set-v2), hold 18.1s > 10s; ev-uber-adoption-v1 3:55-4:12 crosses 1 scene boundaries (world-empty-racks-v1 -> world-exhibition-hall-morning-v1), hold 16.5s > 10s; ev-debt-issuance-v2 4:50-5:00 crosses 1 scene boundaries (world-bond-prospectus -> world-index-board-swelling), hold 10.2s > 10s; ev-ig-credit-weighting-v1 5:01-5:17 hold 16.7s > 10s; ev-capex-consensus-v1 5:18-5:27 crosses 1 scene boundaries (world-datacenter-aisle-v1 -> world-lease-contracts-bound); ev-capex-funding-v1 6:08-6:25 crosses 2 scene boundaries (world-orderbook-stamped-v1 -> world-signature-close -> world-license-cabinet-v1), hold 16.8s > 10s; ev-railway-mileage-v1 6:40-6:50 crosses 2 scene boundaries (world-certificate-wall-v1 -> world-exchange-floor-1845 -> world-target-date-envelope-v1); ev-weight-check-v1 6:50-7:08 hold 18.1s > 10s; ev-smh-drawdown-v3 7:08-7:18 crosses 1 scene boundaries (hero-sp500-double-failure-v1 -> world-spike-certificate-ring-v2), hold 10.3s > 10s ... - re-enter the chart spotlit on the new datum rather than hold
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [WARN ] M02 17 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M04 73 distinct plates; target runtime/12s = 67
          doc 29 s9.13 plate density
  [PASS ] M06 464 caption pages = 35/min, 5.3 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 8 FAIL / 1 WARN / 4 PASS / 1 JUDGE / 0 INFO
```

TIMELINE: steel-and-paper.timeline.json sha256:0a9ba6d8bcc66365ec02d11c9d25d7abbe263465331f8c4d779f4d6d10b56492
VERDICT: FAIL (8 FAIL)
