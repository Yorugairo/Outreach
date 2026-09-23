# MOTION GATE — build-short-e47

```text
=== MOTION DENSITY GATE: C:\Users\Snipe\Downloads\Outreach Program\content\video_engine\projects\systems-and-blowups\normal-for-which-bridge\build-short-e47 ===
               runtime: 0:56
         visual_events: 177 (186.6/min)
                 docks: 0
           dock_source: evidence-dock.json
          ledger_pages: 5
  still_over_12s_share: 0%
            per_minute: 0:00:186/5

  [WARN ] M06 39 caption pages = 41/min, 4.0 words/page
          s9.15 r7 / build_caption_pages 4-6 words
  [PASS ] M01 longest still stretch 1.5s at 0:14
          doc 29 s8.19 / s9.25 stillness ceiling
  [PASS ] M02 0 stretches > 8s (working target)
          doc 29 s9.25
  [PASS ] M03 longest wait for evidence to enter: 14s from 0:10 (no docks at all)
          doc 29: evidence every 15-45s, every phase incl. P1 and P6 (E21)
  [PASS ] M04 6 distinct plates; target runtime/12s = 4
          doc 29 s9.13 plate density
  [PASS ] M05 no plate over the 20s hold
          doc 29 s9.13 as amended by E69 (2026-09-12): the hold is legal while the FRAME LIVES - the ceiling's two-dock condition was written when a world was a still and only a card could move on it
  [PASS ] M08 timeline declares cap_mode; every stretch over the ceiling carries stage captions (counted as events above)
          doc 29 s9.25 caption STAGE mode (E21: captions ARE the motion when nothing else moves)
  [PASS ] M09 no scene stacks two camera moves (punch | focus_zoom | pull_back) or a camera move over Ken Burns
          doc 29 s9.27 precedence / s9.28 C3: one camera move per window
  [PASS ] M10 no still stretch > 6s begins in the first 60s
          E24 / doc 29 s9.29: stillness inside the opening minute - 4-6s in the first 30-60s
  [PASS ] M11 first chart ledger:s01 enters at 0.0s, its build lands at 3.0s, with spotlight at 3.6s (no evidence species in the timeline - every dock treated as a chart candidate); window 0-10s (E44 short: the page rolls out on the hook - the chart is the mechanism by 0:10)
          E24 / doc 29 s9.29 (long form) + E44 (short): the first chart enters 0:08-0:20, or 0:00-0:10 on a short, annotated on its divergence, with a sound cue
  [PASS ] M12 no chart dock spans a scene boundary or holds past 10s (6s in the opening minute)
          E25 / doc 29 s9.30: the chart is the proof, not the homework
  [PASS ] M14 no camera move (punch | focus_zoom | pull_back) overlaps a card entrance or a badge reveal
          47 s2 G-a / doc 07 Pillar 4 (saccadic suppression): a camera move may not overlap an evidence build - the eye is blind during the move
  [PASS ] M15 no species window overlaps a page's retract
          E40 #5 (operator, 2026-09-05): no spotlight on a spiral out - no species window overlaps a page's retract
  [PASS ] M16 longest gap between visual events 1.5s at 0:14; 0 gap(s) over 2.5s
          doc 49 s49.6 / operator 2026-09-05: the short-form gate is the pulse - no gap between visual events over 2.5 s; no ceiling
  [PASS ] M29 1 transient cue(s) inside the drop window, each with a page or dock landing on it: page enter 2 (axes - the first line) at 10.94s gain 0.12 with s02 page arrives at 10.89s (window 0:05-0:12, E44 s2a: the press cue at a cut is not a hook device)
          E44 s2a / R26-5 (operator 2026-09-06: "the camera flash sound maybe shouldn't be as aggressive"): the press / flash cue at a cut is not a hook device - at 0:09 it is the last thing a viewer hears before leaving, so no TRANSIENT cue lands inside 0:05-0:12 unless a PAGE lands with it (the page's own arrival or its chart's landing, within 1.5 s). E83 (operator 2026-09-13: "for sound cue timing on docks: we probably should have sound cues"): a DOCK's own landing licenses the cue the same way - a card that lands is an instant the cue marks, not a cut's flash. The beds are exempt: a bed marks no instant
  [INFO ] M07 short: 0 full minute(s) in 57s - opening 185.6 events/min, 5.3 evidence entries/min; whole runtime 184.5/min - no minute distribution to rank in (E21 is judged on the whole)
          E21: the opening is the densest minute, never the thinnest
  [INFO ] M18 frozen frames not measured - run measure_frozen_frames.py <build> (writes frame-hashes.json)
          E49 / P47 T5: nothing ever goes truly still - a run of identical rendered frames over 0.5 s is a freeze (measure_frozen_frames.py); R26-13: read PER LAYER too - the page, the docks and the captions each on their own (frame-hashes.<layer>.json, the shell's ?layers= switch), because a caption boiling over a frozen page passes the whole-frame hash (Tokyo v2: 1036 distinct frames of 1066, M18 PASS, the pages still). The whole-frame verdict is still reported.
  [INFO ] M19 1 build_to hold(s) - the line rests at a datum until the next word: 0:13+2.5s
          P47 T2 (SHOT-TABLE-V3-PROPOSAL part B): a cap is a hold the sentence asked for, not stillness
  [INFO ] M21 1 page(s) deployed 8-12s after the last data mark (a dock's clip may hold it): s05 10.0s (0:37 -> 0:47)
          E50 (operator 2026-09-07): a chart's deployed life is 6-8 s from its last data mark on average, 12 s at most - then it un-draws or becomes the next thing
  [INFO ] M25 layout not measured - run probe.py <build> --gate (writes layout-probe.json)
          E45 s1 (the compiler's `place`: a card parks in the page's quiet space, never over the plot, the title, the source line or the caption's anchor) / E52 (the page CITES: the citation rides the park) / E60 - the three defects of 2026-09-10, refused from the page's own DOM (probe.py --gate)
  [INFO ] M26 values not measured - run probe.py <build> --gate (writes layout-probe.json)
          E28 (a chart reads right at a glance: a bar's height IS its value) / E53 (the scale and the value are printed at every instant) / R26-40 - the printed number and the DRAWN height, read against the scale the page itself prints, from the page's own DOM (probe.py --gate). R26-39 was exactly this mismatch: 303 px of bar at "0.00 %"
  [INFO ] M27 the read over a build not measured - run probe.py <build> --gate (writes layout-probe.json)
          E63 (operator 2026-09-11, on the Tokyo cut at 0:09.5-0:10.5: "docking over the plate while it's drawing is not a good standard practice ... as a rule we should probably use better handling now that we can manipulate scale/depth/placement easier"; widened the same evening, on the read that came back over the finished chart: "im confused, because you just left the dock over the chart now too. something went backwards"): a card that has not parked yet may not sit on a ledger page's INK, drawing or finished - the READ moves (the compiler's `read_moved` / `read_deferred`), never the word. The page's own INK is what the row scores (the data, the labels, the citation - M25's boxes): since E65 the placer may put a card in the plot's own empty ROOM on purpose, so the plot box is the WARN tier and the ink is the FAIL. A PARKED card is E45's contract and M25's row. Read from the page's own DOM (probe.py --gate)
  [INFO ] M28 text on text not measured - run probe.py <build> --gate (writes layout-probe.json)
          R26-53 (the operator, 2026-09-11: "why are we now crashing text?") - the Tokyo Meta page's four values "$665 $633 $604 $577" touched each other and the callout's pill on bar 4 covered bar 3's label, on the approved build and on every side build before f67c5ed, and no row saw it: M25 reads cards over ink, M26 the value's height, and the probe's `overlaps` carried card-vs-ink and pill-vs-rail only. E28 (a chart reads right at a glance): no two of a page's OWN labels may sit on each other, and the row that fits them (lpFitValues / lpPillBand) leaves half a figure of air between them. From the page's own DOM (probe.py --gate)
  [INFO ] M31 not measured - run measure_stage_gaps.py <build> to read the empty stage
          R26-66 / P53 T2, measured with measure_stage_gaps.py: a transition that TAKES the world (a suck, a melt) left the stage with no world on it for 3.1 s while the narration was already on the next sentence - 8.9% of a 69 s short. The DIP is the one transition licensed to empty the stage (a dip is a world change); everything else hands off, and the page that follows an inked arrival (enter=axes / built) measures 0.
  [INFO ] M32 not measured - run measure_seam_frames.py <build> to read the seams frame by frame
          P54 T9 (the operator, 2026-09-13: 'it's really the flash before or a second black frame that we're looking for'): measure_seam_frames.py seeks every boundary frame by frame; near-black = mean luma < 8 [MEASURED on the approved Japan short's six dips: darkest 0-6, cuts never under 52]. A declared dip's own dark core is the design; black anywhere else at a seam is the fault the operator found by hand twice (2026-09-05, 2026-09-12)
  [INFO ] M33 not measured - run measure_spoken_visuals.py <build>
          P54 T9 (the operator, 2026-09-13: 'gating for narration without the chart on screen is probably valid'; 2026-08-29: 'you open on the "spike" but you don't have the spike ons creen, you talk about charts without the charts on screen'): measure_spoken_visuals.py - a pointing phrase needs a page, a dock or a card on stage. WARN until the approved shorts show a real example (their one hit is a figure of speech)
  [JUDGE] J01 every savor beat holds its picture (card up, badge lit), never a bare plate with a drift
          doc 29 s9.25 #3

RESULT: 0 FAIL / 1 WARN / 14 PASS / 1 JUDGE / 11 INFO
```

TIMELINE: bridge-short.timeline.json sha256:500a5444f1938c336aeb3e5664488ca341aa40842935c88ddba874ec50e1dffc
VERDICT: PASS (0 FAIL)
